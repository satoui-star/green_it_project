"""calculator.py (rebuilt engine)

Élysia - Calculation Engine
===========================

Design rules (as requested)
- All constants, reference values, and source-backed assumptions come from
  `reference_data_API.py`.
- `audit_ui.py` should only render UI: no hard-coded formulas or fixed numbers.
- This module provides a clean API for the UI:
    - ShockCalculator / HopeCalculator
    - StrategySimulator (compare + recommend)
    - FleetAnalyzer (profile + ranking)
    - TCOCalculator / CO2Calculator
    - RecommendationEngine (device-level recommendation)

The module is defensive: if `reference_data_API.py` is missing, it falls back
without crashing (but will mark confidence as LOW).

Units convention
- CO2 factors: kg CO2
- Grid factors: kg CO2 / kWh
- Monetary values: EUR
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import io
import math
import random

import pandas as pd


# -----------------------------------------------------------------------------
# Reference data (single source of truth)
# -----------------------------------------------------------------------------

_BACKEND_READY = True
_IMPORT_ERROR: Optional[str] = None

try:
    from reference_data_API import (  # type: ignore
        DEVICES,
        PERSONAS,
        STRATEGIES,
        AVERAGES,
        GRID_CARBON_FACTORS,
        HOURS_ANNUAL,
        PRICE_KWH_EUR,
        DEFAULT_REFRESH_YEARS,
        DEFAULT_TARGET_REDUCTION,
        PRODUCTIVITY_CONFIG,
        REFURB_CONFIG,
        URGENCY_CONFIG,
        calculate_stranded_value,
        calculate_avoidable_co2,
        get_grid_factor,
        get_disposal_cost,
    )
except Exception as e:
    _BACKEND_READY = False
    _IMPORT_ERROR = str(e)

# -----------------------------------------------------------------------------
# Reference-data compatibility shim (DO NOT put any UI logic here)
# Fixes:
# - GRID_CARBON_FACTORS being dicts {"factor": ...} instead of floats
# - AVERAGES key mismatch (device_price_eur vs avg_price_new_eur, etc.)
# -----------------------------------------------------------------------------

try:
    from reference_data_API import (
        AVERAGES as _REF_AVG,
        REFURB_CONFIG as _REF_REFURB,
        GRID_CARBON_FACTORS as _REF_GRID,
        DEFAULT_GRID_FACTOR as _REF_DEFAULT_GRID,
        get_grid_factor as _REF_GET_GRID_FACTOR,
    )

    # 1) Normalize AVERAGES keys expected by this calculator module
    if isinstance(AVERAGES, dict) and isinstance(_REF_AVG, dict):
        if "avg_price_new_eur" not in AVERAGES and "device_price_eur" in _REF_AVG:
            AVERAGES["avg_price_new_eur"] = float(_REF_AVG["device_price_eur"])

        if "avg_mfg_co2_new_kg" not in AVERAGES and "device_co2_manufacturing_kg" in _REF_AVG:
            AVERAGES["avg_mfg_co2_new_kg"] = float(_REF_AVG["device_co2_manufacturing_kg"])

        # refurb price derived from reference ratio (if missing)
        if "avg_price_refurb_eur" not in AVERAGES and "avg_price_new_eur" in AVERAGES:
            AVERAGES["avg_price_refurb_eur"] = float(AVERAGES["avg_price_new_eur"]) * float(_REF_REFURB.get("price_ratio", 0.59))

        # refurb manufacturing factor derived from savings rate (if missing)
        # savings_rate=0.80 => refurb_mfg_factor=0.20
        if "refurb_mfg_factor" not in AVERAGES and "co2_savings_rate" in _REF_REFURB:
            AVERAGES["refurb_mfg_factor"] = max(0.05, min(0.50, 1.0 - float(_REF_REFURB["co2_savings_rate"])))

    # 2) Always use a safe grid-factor getter
    def get_grid_factor(country_code: str) -> float:
        try:
            return float(_REF_GET_GRID_FACTOR(country_code))
        except Exception:
            v = _REF_GRID.get(country_code, _REF_DEFAULT_GRID)
            if isinstance(v, dict):
                return float(v.get("factor", _REF_DEFAULT_GRID))
            return float(v)

except Exception:
    # fallback if reference_data_API isn't available
    def get_grid_factor(country_code: str) -> float:
        v = GRID_CARBON_FACTORS.get(country_code, 0.30) if isinstance(GRID_CARBON_FACTORS, dict) else 0.30
        if isinstance(v, dict):
            return float(v.get("factor", 0.30))
        return float(v)


    # Conservative minimal fallbacks (only to avoid crashes).
    DEVICES = {
        "Laptop (Standard)": {
            "price_new_eur": 1000.0,
            "co2_manufacturing_kg": 250.0,
            "power_kw": 0.03,
            "lifespan_months": 48,
            "category": "Laptop",
            "refurb_available": True,
            "has_data": True,
        }
    }
    PERSONAS = {
        "Admin Normal (HR/Finance)": {"salary_eur": 55000, "daily_hours": 8, "lag_sensitivity": 1.0}
    }
    STRATEGIES = {
        "do_nothing": {"name": "Do Nothing", "description": "", "refurb_rate": 0.0, "lifecycle_years": 4, "recovery_rate": 0.0, "implementation_months": 0},
        "refurb_40": {"name": "40% Refurbished", "description": "", "refurb_rate": 0.40, "lifecycle_years": 4, "recovery_rate": 0.7, "implementation_months": 9},
    }
    AVERAGES = {
        "device_price_eur": 1150.0,
        "device_co2_manufacturing_kg": 365.0,
        "device_co2_annual_kg": 50.0,
        "salary_eur": 65000.0,
        "working_days_per_year": 220,
        "hours_per_day": 8,
    }
    GRID_CARBON_FACTORS = {"FR": {"factor": 0.27, "name": "France"}}
    HOURS_ANNUAL = 1607
    PRICE_KWH_EUR = 0.22
    DEFAULT_REFRESH_YEARS = 4
    DEFAULT_TARGET_REDUCTION = 0.20
    PRODUCTIVITY_CONFIG = {"optimal_years": 3, "degradation_per_year": 0.03, "max_degradation": 0.15}
    REFURB_CONFIG = {"co2_savings_rate": 0.80, "price_ratio": 0.59, "energy_penalty": 0.10, "equivalent_age_years": 1.5}
    URGENCY_CONFIG = {"performance_threshold": 0.70}

    def get_grid_factor(country_code: str) -> float:
        return float(GRID_CARBON_FACTORS.get(country_code, {}).get("factor", 0.27))

    def get_disposal_cost(device_name: str) -> float:
        _ = device_name
        return 20.0

    def calculate_stranded_value(fleet_size: int, avg_age: float, avg_price: Optional[float] = None) -> dict:
        if avg_price is None:
            avg_price = float(AVERAGES.get("device_price_eur", 1150.0))
        remaining_value_pct = 0.70 ** max(0.0, float(avg_age))
        value = float(fleet_size) * float(avg_price) * remaining_value_pct
        return {"value": value, "calculation": {"fleet_size": fleet_size, "avg_price": avg_price, "avg_age": avg_age, "remaining_value_pct": remaining_value_pct}}

    def calculate_avoidable_co2(fleet_size: int, refresh_cycle: int, refurb_rate: float = 0.40) -> dict:
        annual_replacements = float(fleet_size) / max(1, int(refresh_cycle))
        co2_per_device = float(AVERAGES.get("device_co2_manufacturing_kg", 365.0))
        savings_rate = float(REFURB_CONFIG.get("co2_savings_rate", 0.80))
        avoidable_kg = annual_replacements * float(refurb_rate) * co2_per_device * savings_rate
        return {"value_kg": avoidable_kg, "value_tonnes": avoidable_kg / 1000, "calculation": {"annual_replacements": annual_replacements, "refurb_rate": refurb_rate, "co2_per_device_kg": co2_per_device, "savings_rate": savings_rate}}


# -----------------------------------------------------------------------------
# Public data objects (imported by the UI)
# -----------------------------------------------------------------------------

@dataclass
class StrategyResult:
    strategy_key: str
    strategy_name: str
    description: str
    co2_reduction_pct: float  # negative = reduction
    annual_savings_eur: float
    roi_3year: float
    time_to_target_months: int
    reaches_target: bool
    calculation_details: Dict[str, Any]


@dataclass
class DeviceRecommendation:
    device: str
    persona: str
    country: str
    recommendation: str  # KEEP / NEW / REFURBISHED
    rationale: str
    tco_total_eur: float
    co2_total_kg: float
    breakdown: Dict[str, Any]


@dataclass
class ShockResult:
    stranded_value_eur: float
    avoidable_co2_tonnes: float
    stranded_calculation: Dict[str, Any]
    co2_calculation: Dict[str, Any]


@dataclass
class HopeResult:
    current_co2_tonnes: float
    target_co2_tonnes: float
    co2_reduction_pct: float
    current_cost_eur: float
    target_cost_eur: float
    cost_savings_eur: float
    months_to_target: int
    calculation_details: Dict[str, Any]


# -----------------------------------------------------------------------------
# Internal helpers (no UI)
# -----------------------------------------------------------------------------

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _avg_new_price() -> float:
    return _safe_float(AVERAGES.get("device_price_eur"), 1150.0)


def _avg_mfg_co2_new() -> float:
    return _safe_float(AVERAGES.get("device_co2_manufacturing_kg"), 365.0)


def _refurb_price(new_price: float) -> float:
    return float(new_price) * _safe_float(REFURB_CONFIG.get("price_ratio"), 0.59)


def _refurb_mfg_co2(new_mfg_co2_kg: float) -> float:
    # co2_savings_rate = reduction relative to new
    savings = _clamp(_safe_float(REFURB_CONFIG.get("co2_savings_rate"), 0.80), 0.0, 0.95)
    return float(new_mfg_co2_kg) * (1.0 - savings)


def _annual_replacements(fleet_size: int, refresh_years: float) -> float:
    return float(fleet_size) / max(1.0, float(refresh_years))


def _target_co2_threshold(baseline_co2_tonnes: float, target_pct: int) -> float:
    # target_pct expected negative (e.g. -20)
    return float(baseline_co2_tonnes) * (1.0 + (float(target_pct) / 100.0))


def _effective_refurb_rate(strategy_refurb: float, current_refurb: float) -> float:
    # Never recommend going backwards.
    return float(max(strategy_refurb, current_refurb))


def _effective_refresh_years(strategy_lifecycle: float, current_refresh: float) -> float:
    # Never recommend a shorter lifecycle than current (unless UI explicitly asks for it).
    return float(max(strategy_lifecycle, current_refresh))


def _energy_kwh_per_year(device_name: str) -> float:
    meta = DEVICES.get(device_name, {}) if isinstance(DEVICES, dict) else {}
    power_kw = _safe_float(meta.get("power_kw"), 0.03)
    return power_kw * float(HOURS_ANNUAL)


def _usage_cost_eur_per_year(device_name: str) -> float:
    return _energy_kwh_per_year(device_name) * float(PRICE_KWH_EUR)


def _usage_co2_kg_per_year(device_name: str, country_code: str) -> float:
    factor = float(get_grid_factor(country_code))
    return _energy_kwh_per_year(device_name) * factor


def _lifespan_years(device_name: str) -> float:
    meta = DEVICES.get(device_name, {}) if isinstance(DEVICES, dict) else {}
    months = _safe_float(meta.get("lifespan_months"), 48)
    return max(1.0, months / 12.0)


def _remaining_life_years_for_refurb(device_name: str) -> float:
    # If the device entry itself is a refurbished SKU, keep its lifespan.
    meta = DEVICES.get(device_name, {}) if isinstance(DEVICES, dict) else {}
    if bool(meta.get("is_refurbished", False)):
        return _lifespan_years(device_name)

    base = _lifespan_years(device_name)
    equiv_age = _safe_float(REFURB_CONFIG.get("equivalent_age_years"), 1.5)
    return max(1.0, base - equiv_age)


def _productivity_loss_pct(age_years: float, persona_name: str) -> float:
    """Model-based productivity loss (theoretical, but source-backed in reference_data_API).

    Uses PRODUCTIVITY_CONFIG and persona lag_sensitivity.
    """
    p = PERSONAS.get(persona_name, {}) if isinstance(PERSONAS, dict) else {}
    lag = _safe_float(p.get("lag_sensitivity"), 1.0)

    optimal = _safe_float(PRODUCTIVITY_CONFIG.get("optimal_years"), 3)
    degr = _safe_float(PRODUCTIVITY_CONFIG.get("degradation_per_year"), 0.03)
    cap = _safe_float(PRODUCTIVITY_CONFIG.get("max_degradation"), 0.15)

    over = max(0.0, float(age_years) - optimal)
    base_loss = min(cap, over * degr)
    weighted = min(cap, base_loss * lag)
    return _clamp(weighted, 0.0, cap)


def _productivity_cost_eur(age_years: float, persona_name: str) -> float:
    p = PERSONAS.get(persona_name, {}) if isinstance(PERSONAS, dict) else {}
    salary = _safe_float(p.get("salary_eur"), _safe_float(AVERAGES.get("salary_eur"), 65000.0))
    loss_pct = _productivity_loss_pct(age_years, persona_name)
    return salary * loss_pct


def _performance_index(age_years: float) -> float:
    # Simple proxy: 1.0 at <= optimal, declines linearly by degradation_per_year.
    optimal = _safe_float(PRODUCTIVITY_CONFIG.get("optimal_years"), 3)
    degr = _safe_float(PRODUCTIVITY_CONFIG.get("degradation_per_year"), 0.03)
    over = max(0.0, float(age_years) - optimal)
    return _clamp(1.0 - (over * degr), 0.0, 1.0)


def _confidence_from_data_mode(data_mode: str) -> str:
    if data_mode == "measured":
        return "HIGH"
    if data_mode == "partial":
        return "MEDIUM"
    return "MEDIUM" if _BACKEND_READY else "LOW"


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

class ShockCalculator:
    """Act 1 - Shock: stranded value + avoidable CO2."""

    @staticmethod
    def calculate(
        fleet_size: int,
        avg_age: float = 3.5,
        refresh_cycle: int = DEFAULT_REFRESH_YEARS,
        target_pct: int = int(-DEFAULT_TARGET_REDUCTION * 100),
        geo_code: str = "FR",
        current_refurb_pct: float = 0.0,
        base_strategy_key: str = "refurb_40",
    ) -> ShockResult:
        fleet_size = int(max(0, fleet_size))
        refresh_cycle = int(max(1, refresh_cycle))

        stranded = calculate_stranded_value(
            fleet_size=fleet_size,
            avg_age=float(avg_age),
            avg_price=_avg_new_price(),
        )

        base_refurb_rate = _safe_float(STRATEGIES.get(base_strategy_key, {}).get("refurb_rate"), 0.40)
        avoidable = calculate_avoidable_co2(
            fleet_size=fleet_size,
            refresh_cycle=refresh_cycle,
            refurb_rate=float(base_refurb_rate),
        )

        # Adjust for current refurb adoption so we don't over-claim.
        current_refurb_pct = _clamp(float(current_refurb_pct), 0.0, 1.0)
        effective_refurb_rate = max(0.0, float(base_refurb_rate) - current_refurb_pct)
        scale = (effective_refurb_rate / float(base_refurb_rate)) if float(base_refurb_rate) > 0 else 0.0
        adjusted_avoidable_tonnes = float(avoidable.get("value_tonnes", 0.0)) * scale

        stranded_calc = dict(stranded.get("calculation", {}) or {})
        co2_calc = dict(avoidable.get("calculation", {}) or {})
        co2_calc.update(
            {
                "geo_code": geo_code,
                "target_pct": int(target_pct),
                "current_refurb_pct": current_refurb_pct,
                "base_refurb_rate": float(base_refurb_rate),
                "effective_refurb_rate": float(effective_refurb_rate),
                "adjustment_scale": float(scale),
            }
        )

        return ShockResult(
            stranded_value_eur=float(stranded.get("value", 0.0)),
            avoidable_co2_tonnes=float(adjusted_avoidable_tonnes),
            stranded_calculation=stranded_calc,
            co2_calculation=co2_calc,
        )


class HopeCalculator:
    """Act 2 - Hope: baseline vs one strategy."""

    @staticmethod
    def calculate(
        fleet_size: int,
        avg_age: float = 3.5,
        refresh_cycle: int = DEFAULT_REFRESH_YEARS,
        target_pct: int = int(-DEFAULT_TARGET_REDUCTION * 100),
        strategy_key: str = "refurb_40",
        current_refurb_pct: float = 0.0,
    ) -> HopeResult:
        fleet_size = int(max(0, fleet_size))
        refresh_cycle = float(max(1, int(refresh_cycle)))

        new_price = _avg_new_price()
        new_mfg = _avg_mfg_co2_new()
        refurb_price = _refurb_price(new_price)
        refurb_mfg = _refurb_mfg_co2(new_mfg)

        base_refurb = _clamp(float(current_refurb_pct), 0.0, 1.0)

        # Baseline (current approach)
        base_repl = _annual_replacements(fleet_size, refresh_cycle)
        base_co2_kg = base_repl * ((1.0 - base_refurb) * new_mfg + base_refurb * refurb_mfg)
        base_cost = base_repl * ((1.0 - base_refurb) * new_price + base_refurb * refurb_price)

        # Strategy
        s = STRATEGIES.get(strategy_key, {}) if isinstance(STRATEGIES, dict) else {}
        s_refurb = _effective_refurb_rate(_safe_float(s.get("refurb_rate"), 0.0), base_refurb)
        s_lifecycle = _effective_refresh_years(_safe_float(s.get("lifecycle_years"), refresh_cycle), refresh_cycle)
        s_repl = _annual_replacements(fleet_size, s_lifecycle)

        s_co2_kg = s_repl * ((1.0 - s_refurb) * new_mfg + s_refurb * refurb_mfg)
        s_cost = s_repl * ((1.0 - s_refurb) * new_price + s_refurb * refurb_price)

        base_t = base_co2_kg / 1000.0
        strat_t = s_co2_kg / 1000.0

        reduction_pct = ((strat_t - base_t) / base_t * 100.0) if base_t > 0 else 0.0  # negative is good
        savings = base_cost - s_cost

        target_threshold = _target_co2_threshold(base_t, int(target_pct))
        reaches = strat_t <= target_threshold if base_t > 0 else False

        impl_months = int(_safe_float(s.get("implementation_months"), 0))
        months = impl_months if reaches else 999

        details = {
            "backend_ready": _BACKEND_READY,
            "import_error": _IMPORT_ERROR,
            "inputs": {
                "fleet_size": fleet_size,
                "avg_age": float(avg_age),
                "refresh_cycle_years": float(refresh_cycle),
                "target_pct": int(target_pct),
                "strategy_key": strategy_key,
                "current_refurb_pct": float(base_refurb),
            },
            "assumptions": {
                "new_price_eur": float(new_price),
                "refurb_price_eur": float(refurb_price),
                "new_mfg_co2_kg": float(new_mfg),
                "refurb_mfg_co2_kg": float(refurb_mfg),
            },
            "baseline": {
                "annual_replacements": float(base_repl),
                "refurb_rate": float(base_refurb),
                "co2_tonnes": float(base_t),
                "cost_eur": float(base_cost),
            },
            "strategy": {
                "annual_replacements": float(s_repl),
                "refurb_rate": float(s_refurb),
                "lifecycle_years": float(s_lifecycle),
                "co2_tonnes": float(strat_t),
                "cost_eur": float(s_cost),
                "implementation_months": int(impl_months),
            },
            "target": {"threshold_tonnes": float(target_threshold), "reaches": bool(reaches)},
        }

        return HopeResult(
            current_co2_tonnes=float(base_t),
            target_co2_tonnes=float(strat_t),
            co2_reduction_pct=float(reduction_pct),
            current_cost_eur=float(base_cost),
            target_cost_eur=float(s_cost),
            cost_savings_eur=float(savings),
            months_to_target=int(months),
            calculation_details=details,
        )


class StrategySimulator:
    """Act 4 - Strategy: compare strategies and optionally pick one."""

    @staticmethod
    def compare_all_strategies(
        fleet_size: int,
        current_refresh: int = DEFAULT_REFRESH_YEARS,
        avg_age: float = 3.5,
        target_pct: int = int(-DEFAULT_TARGET_REDUCTION * 100),
        time_horizon_months: int = 36,
        geo_code: str = "FR",
        current_refurb_pct: float = 0.0,
        data_mode: str = "estimated",
    ) -> List[StrategyResult]:
        fleet_size = int(max(0, fleet_size))
        current_refresh = float(max(1, int(current_refresh)))
        time_horizon_months = int(max(1, time_horizon_months))

        # Baseline
        baseline = HopeCalculator.calculate(
            fleet_size=fleet_size,
            avg_age=avg_age,
            refresh_cycle=int(current_refresh),
            target_pct=int(target_pct),
            strategy_key="do_nothing",
            current_refurb_pct=float(current_refurb_pct),
        )
        baseline_co2_t = float(baseline.current_co2_tonnes)
        baseline_cost = float(baseline.current_cost_eur)
        threshold_t = _target_co2_threshold(baseline_co2_t, int(target_pct))

        results: List[StrategyResult] = []

        for key, s in (STRATEGIES.items() if isinstance(STRATEGIES, dict) else []):
            if not isinstance(s, dict):
                continue

            name = str(s.get("name", key))
            desc = str(s.get("description", ""))

            # Compute strategy outcome vs baseline using same engine.
            h = HopeCalculator.calculate(
                fleet_size=fleet_size,
                avg_age=avg_age,
                refresh_cycle=int(current_refresh),
                target_pct=int(target_pct),
                strategy_key=key,
                current_refurb_pct=float(current_refurb_pct),
            )

            strat_co2_t = float(h.target_co2_tonnes)
            strat_cost = float(h.target_cost_eur)

            co2_reduction_pct = ((strat_co2_t - baseline_co2_t) / baseline_co2_t * 100.0) if baseline_co2_t > 0 else 0.0
            annual_savings = baseline_cost - strat_cost

            reaches = strat_co2_t <= threshold_t if baseline_co2_t > 0 else False

            impl_months = int(_safe_float(s.get("implementation_months"), 0))
            time_to_target = impl_months if reaches else 999
            if impl_months > time_horizon_months:
                time_to_target = 999

            recovery = _clamp(_safe_float(s.get("recovery_rate"), 0.0), 0.0, 1.0)
            risk_score = 1.0 - recovery
            risk_level = "LOW" if risk_score <= 0.30 else ("MEDIUM" if risk_score <= 0.55 else "HIGH")

            confidence = _confidence_from_data_mode(data_mode)

            details = {
                "geo_code": geo_code,
                "data_mode": data_mode,
                "confidence": confidence,
                "baseline": {
                    "co2_tonnes": baseline_co2_t,
                    "cost_eur": baseline_cost,
                    "threshold_tonnes": threshold_t,
                },
                "strategy": {
                    "co2_tonnes": strat_co2_t,
                    "cost_eur": strat_cost,
                    "refurb_rate": _safe_float(STRATEGIES.get(key, {}).get("refurb_rate"), 0.0),
                    "lifecycle_years": _safe_float(STRATEGIES.get(key, {}).get("lifecycle_years"), current_refresh),
                    "implementation_months": impl_months,
                    "recovery_rate": recovery,
                },
                "risk": {"score": risk_score, "level": risk_level},
                "calc": h.calculation_details,
            }

            results.append(
                StrategyResult(
                    strategy_key=key,
                    strategy_name=name,
                    description=desc,
                    co2_reduction_pct=float(co2_reduction_pct),
                    annual_savings_eur=float(annual_savings),
                    roi_3year=0.0,
                    time_to_target_months=int(time_to_target),
                    reaches_target=bool(reaches),
                    calculation_details=details,
                )
            )

        # Stable sort: first strategies reaching target, then by CO2 impact, then savings.
        results.sort(key=lambda r: (not r.reaches_target, abs(r.co2_reduction_pct), r.annual_savings_eur), reverse=True)
        return results

    @staticmethod
    def pick_strategy(results: List[StrategyResult], priority: str = "cost") -> StrategyResult:
        """UI-safe selection.

        This is intentionally *rule-based* to avoid introducing arbitrary
        weighting constants that don't come from `reference_data_API`.
        """
        if not results:
            raise ValueError("No strategies to select from")

        priority = (priority or "cost").lower().strip()
        priority = priority if priority in {"cost", "co2", "speed"} else "cost"

        # Prefer actionable strategies (exclude baseline) when possible.
        candidates = [r for r in results if r.strategy_key != "do_nothing"] or list(results)

        def risk_score(r: StrategyResult) -> float:
            # lower is better
            d = (r.calculation_details or {}).get("risk", {})
            return _clamp(_safe_float(d.get("score"), 0.5), 0.0, 1.0)

        def co2_impact(r: StrategyResult) -> float:
            return abs(_safe_float(r.co2_reduction_pct, 0.0))

        def speed_value(r: StrategyResult) -> float:
            t = int(_safe_float(r.time_to_target_months, 999))
            return 999999 if t >= 999 else t

        def savings_value(r: StrategyResult) -> float:
            return _safe_float(r.annual_savings_eur, 0.0)

        # Step 1 — if anything reaches target, restrict to those.
        reachable = [r for r in candidates if bool(r.reaches_target)]
        pool = reachable or candidates

        # Step 2 — primary selection by priority.
        if priority == "co2":
            pool.sort(key=lambda r: (co2_impact(r), savings_value(r), -risk_score(r)), reverse=True)
        elif priority == "speed":
            pool.sort(key=lambda r: (speed_value(r), -co2_impact(r), risk_score(r)))
        else:  # cost
            pool.sort(key=lambda r: (savings_value(r), co2_impact(r), -risk_score(r)), reverse=True)

        # Step 3 — tie-break: prefer lower risk.
        best = pool[0]
        # If another option is virtually the same (same key metrics), pick lower risk.
        for r in pool[1:5]:
            if (
                abs(savings_value(r) - savings_value(best)) < 1e-9
                and abs(co2_impact(r) - co2_impact(best)) < 1e-9
                and speed_value(r) == speed_value(best)
                and risk_score(r) < risk_score(best)
            ):
                best = r
        return best


class FleetAnalyzer:
    """Fleet evidence: profile + hotspots based on uploaded data."""

    REQUIRED_COLUMNS = ["Device_Model", "Age_Years"]

    @staticmethod
    def normalize_fleet_df(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return pd.DataFrame(columns=FleetAnalyzer.REQUIRED_COLUMNS)

        norm = df.copy()
        rename_map: Dict[str, str] = {}
        if "Model" in norm.columns and "Device_Model" not in norm.columns:
            rename_map["Model"] = "Device_Model"
        if "Age" in norm.columns and "Age_Years" not in norm.columns:
            rename_map["Age"] = "Age_Years"
        if rename_map:
            norm = norm.rename(columns=rename_map)

        # Ensure required cols exist
        for c in FleetAnalyzer.REQUIRED_COLUMNS:
            if c not in norm.columns:
                norm[c] = None

        # Types
        norm["Device_Model"] = norm["Device_Model"].astype(str)
        norm["Age_Years"] = pd.to_numeric(norm["Age_Years"], errors="coerce")

        if "Country" in norm.columns:
            norm["Country"] = norm["Country"].astype(str)
        if "Persona" in norm.columns:
            norm["Persona"] = norm["Persona"].astype(str)

        norm = norm.dropna(subset=["Device_Model", "Age_Years"]).reset_index(drop=True)
        return norm

    @staticmethod
    def profile(df: pd.DataFrame, refresh_cycle_years: int, default_country: str = "FR") -> Dict[str, Any]:
        norm = FleetAnalyzer.normalize_fleet_df(df)
        fleet_size = int(len(norm))

        if fleet_size == 0:
            return {
                "data_mode": "estimated",
                "fleet_size": 0,
                "avg_age": 0.0,
                "annual_replacements": 0,
                "age_risk_share": 0.0,
                "eligible_refurb_share": 0.0,
                "annual_new_spend_eur": 0.0,
            }

        avg_age = float(norm["Age_Years"].mean())
        annual_repl = int(round(_annual_replacements(fleet_size, max(1, int(refresh_cycle_years)))))

        # Use the urgency framework threshold from reference data (no UI hardcoding)
        age_high = _safe_float(URGENCY_CONFIG.get("age_high_years"), 4.0)
        age_risk_share = float((norm["Age_Years"] >= age_high).mean())

        # Eligibility: based on known device catalog
        eligible = 0
        total_new_spend = 0.0
        for _, row in norm.iterrows():
            dev = str(row.get("Device_Model"))
            meta = DEVICES.get(dev, {}) if isinstance(DEVICES, dict) else {}
            if bool(meta.get("refurb_available", False)):
                eligible += 1
            total_new_spend += _safe_float(meta.get("price_new_eur"), _avg_new_price())

        eligible_share = float(eligible / fleet_size) if fleet_size else 0.0

        # Spend (annual new purchases baseline)
        avg_new_price = total_new_spend / fleet_size if fleet_size else _avg_new_price()
        annual_new_spend = float(annual_repl) * float(avg_new_price)

        # Determine data_mode
        data_mode = "measured" if fleet_size > 0 else "estimated"

        return {
            "data_mode": data_mode,
            "fleet_size": fleet_size,
            "avg_age": avg_age,
            "annual_replacements": annual_repl,
            "age_risk_share": age_risk_share,
            "eligible_refurb_share": eligible_share,
            "annual_new_spend_eur": annual_new_spend,
            "default_country": default_country,
        }

    @staticmethod
    def top_models(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        norm = FleetAnalyzer.normalize_fleet_df(df)
        if norm.empty:
            return pd.DataFrame(columns=["Device_Model", "count", "avg_age"])
        agg = (
            norm.groupby("Device_Model")
            .agg(count=("Device_Model", "size"), avg_age=("Age_Years", "mean"))
            .sort_values(["count", "avg_age"], ascending=[False, False])
            .head(int(n))
            .reset_index()
        )
        return agg


class TCOCalculator:
    """Device-level annual TCO (EUR/year)."""

    @staticmethod
    def calculate_tco_keep(device: str, age_years: float, persona: str, country: str) -> Dict[str, Any]:
        _ = country  # currently not used for cost
        energy = _usage_cost_eur_per_year(device)
        productivity = _productivity_cost_eur(float(age_years), persona)
        total = energy + productivity
        return {
            "option": "KEEP",
            "total": float(total),
            "breakdown": {
                "energy_eur": float(energy),
                "productivity_eur": float(productivity),
                "capex_annualized_eur": 0.0,
                "disposal_annualized_eur": 0.0,
            },
        }

    @staticmethod
    def calculate_tco_new(device: str, persona: str, country: str) -> Dict[str, Any]:
        _ = (persona, country)
        meta = DEVICES.get(device, {}) if isinstance(DEVICES, dict) else {}
        price_new = _safe_float(meta.get("price_new_eur"), _avg_new_price())
        life = _lifespan_years(device)
        capex = price_new / life
        energy = _usage_cost_eur_per_year(device)
        productivity = _productivity_cost_eur(0.0, persona)
        disposal = get_disposal_cost(device) / life
        total = capex + energy + productivity + disposal
        return {
            "option": "NEW",
            "total": float(total),
            "breakdown": {
                "energy_eur": float(energy),
                "productivity_eur": float(productivity),
                "capex_annualized_eur": float(capex),
                "disposal_annualized_eur": float(disposal),
                "lifespan_years": float(life),
            },
        }

    @staticmethod
    def calculate_tco_refurb(device: str, persona: str, country: str) -> Dict[str, Any]:
        _ = country
        meta = DEVICES.get(device, {}) if isinstance(DEVICES, dict) else {}
        if not bool(meta.get("refurb_available", False)):
            return {"option": "REFURBISHED", "available": False, "total": float("inf"), "breakdown": {"reason": "not_available"}}

        price_new = _safe_float(meta.get("price_new_eur"), _avg_new_price())
        price_ref = _safe_float(meta.get("price_refurb_eur"), _refurb_price(price_new))
        life = _remaining_life_years_for_refurb(device)

        capex = price_ref / life
        # Older hardware energy penalty
        energy = _usage_cost_eur_per_year(device) * (1.0 + _safe_float(REFURB_CONFIG.get("energy_penalty"), 0.10))
        productivity = _productivity_cost_eur(_safe_float(REFURB_CONFIG.get("equivalent_age_years"), 1.5), persona)
        disposal = get_disposal_cost(device) / life
        total = capex + energy + productivity + disposal

        return {
            "option": "REFURBISHED",
            "available": True,
            "total": float(total),
            "breakdown": {
                "energy_eur": float(energy),
                "productivity_eur": float(productivity),
                "capex_annualized_eur": float(capex),
                "disposal_annualized_eur": float(disposal),
                "lifespan_years": float(life),
                "price_refurb_eur": float(price_ref),
            },
        }


class CO2Calculator:
    """Device-level annual CO2 (kg/year)."""

    @staticmethod
    def calculate_co2_keep(device: str, persona: str, country: str) -> Dict[str, Any]:
        _ = persona
        use = _usage_co2_kg_per_year(device, country)
        # manufacturing is sunk for KEEP
        total = use
        return {
            "option": "KEEP",
            "total": float(total),
            "breakdown": {"manufacturing_kg": 0.0, "use_phase_kg": float(use), "grid_factor": float(get_grid_factor(country))},
        }

    @staticmethod
    def calculate_co2_new(device: str, persona: str, country: str) -> Dict[str, Any]:
        _ = persona
        meta = DEVICES.get(device, {}) if isinstance(DEVICES, dict) else {}
        mfg = _safe_float(meta.get("co2_manufacturing_kg"), _avg_mfg_co2_new())
        life = _lifespan_years(device)
        mfg_annual = mfg / life
        use = _usage_co2_kg_per_year(device, country)
        total = mfg_annual + use
        return {
            "option": "NEW",
            "total": float(total),
            "breakdown": {
                "manufacturing_kg": float(mfg_annual),
                "manufacturing_total_kg": float(mfg),
                "use_phase_kg": float(use),
                "grid_factor": float(get_grid_factor(country)),
                "lifespan_years": float(life),
            },
        }

    @staticmethod
    def calculate_co2_refurb(device: str, persona: str, country: str) -> Dict[str, Any]:
        _ = persona
        meta = DEVICES.get(device, {}) if isinstance(DEVICES, dict) else {}
        if not bool(meta.get("refurb_available", False)):
            return {"option": "REFURBISHED", "available": False, "total": float("inf"), "breakdown": {"reason": "not_available"}}

        new_mfg = _safe_float(meta.get("co2_manufacturing_kg"), _avg_mfg_co2_new())
        mfg_ref = _refurb_mfg_co2(new_mfg)
        life = _remaining_life_years_for_refurb(device)
        mfg_annual = mfg_ref / life

        use = _usage_co2_kg_per_year(device, country) * (1.0 + _safe_float(REFURB_CONFIG.get("energy_penalty"), 0.10))
        total = mfg_annual + use

        return {
            "option": "REFURBISHED",
            "available": True,
            "total": float(total),
            "breakdown": {
                "manufacturing_kg": float(mfg_annual),
                "manufacturing_total_kg": float(mfg_ref),
                "use_phase_kg": float(use),
                "grid_factor": float(get_grid_factor(country)),
                "lifespan_years": float(life),
                "energy_penalty": float(_safe_float(REFURB_CONFIG.get("energy_penalty"), 0.10)),
            },
        }
CO2Calculator._grid_factor = staticmethod(get_grid_factor)


class RecommendationEngine:
    """Decision logic for device recommendation (moves logic out of UI)."""

    @staticmethod
    def recommend_device(
        device: str,
        persona: str,
        country: str,
        age_years: float,
        objective: str = "Balanced",
        criticality: str = "Medium",
    ) -> DeviceRecommendation:
        objective = (objective or "Balanced").strip()
        criticality = (criticality or "Medium").strip()

        tco_keep = TCOCalculator.calculate_tco_keep(device, age_years, persona, country)
        tco_new = TCOCalculator.calculate_tco_new(device, persona, country)
        tco_ref = TCOCalculator.calculate_tco_refurb(device, persona, country)

        co2_keep = CO2Calculator.calculate_co2_keep(device, persona, country)
        co2_new = CO2Calculator.calculate_co2_new(device, persona, country)
        co2_ref = CO2Calculator.calculate_co2_refurb(device, persona, country)

        options: List[Tuple[str, float, float, Dict[str, Any]]] = [
            ("KEEP", float(tco_keep["total"]), float(co2_keep["total"]), {"tco": tco_keep, "co2": co2_keep}),
            ("NEW", float(tco_new["total"]), float(co2_new["total"]), {"tco": tco_new, "co2": co2_new}),
        ]
        if bool(tco_ref.get("available", True)) and math.isfinite(float(tco_ref.get("total", float("inf")))):
            options.append(("REFURBISHED", float(tco_ref["total"]), float(co2_ref["total"]), {"tco": tco_ref, "co2": co2_ref}))

        # Urgency guardrail: if performance is below threshold AND criticality is high, avoid KEEP.
        perf = _performance_index(float(age_years))
        perf_threshold = _safe_float(URGENCY_CONFIG.get("performance_threshold"), 0.70)
        age_high = _safe_float(URGENCY_CONFIG.get("age_high_years"), 4.0)
        forbid_keep = (criticality.lower() == "high") and (perf < perf_threshold or float(age_years) >= age_high)

        filtered = [o for o in options if (o[0] != "KEEP" or not forbid_keep)] or options

        if objective == "Min cost":
            best = min(filtered, key=lambda x: x[1])
            rationale = "Optimized for minimum annual TCO."
        elif objective == "Min CO₂":
            best = min(filtered, key=lambda x: x[2])
            rationale = "Optimized for minimum annual CO₂ footprint."
        elif objective == "Min risk":
            # Rule-based: when devices are old (>= age_high) or performance is low, do not KEEP.
            risk_filtered = [o for o in filtered if (o[0] != "KEEP" or (perf >= perf_threshold and float(age_years) < age_high))]
            if not risk_filtered:
                risk_filtered = filtered
            best = min(risk_filtered, key=lambda x: (x[1] + x[2]))
            rationale = "Optimized for lower operational risk (age/performance-aware)."
        else:
            # Balanced: normalize cost & CO2 then average.
            max_cost = max([o[1] for o in filtered] + [1.0])
            max_co2 = max([o[2] for o in filtered] + [1.0])
            best = min(filtered, key=lambda x: (x[1] / max_cost + x[2] / max_co2))
            rationale = "Balanced trade-off between annual TCO and annual CO₂."

        reco, best_cost, best_co2, extra = best

        breakdown = {
            "objective": objective,
            "criticality": criticality,
            "performance_index": perf,
            "performance_threshold": perf_threshold,
            "forbid_keep": forbid_keep,
            "options": [
                {"name": o[0], "tco_total_eur": o[1], "co2_total_kg": o[2]} for o in options
            ],
            "selected": {"name": reco, "tco": extra["tco"], "co2": extra["co2"]},
        }

        return DeviceRecommendation(
            device=device,
            persona=persona,
            country=country,
            recommendation=reco,
            rationale=rationale,
            tco_total_eur=float(best_cost),
            co2_total_kg=float(best_co2),
            breakdown=breakdown,
        )


# -----------------------------------------------------------------------------
# Compatibility helpers (UI imports these)
# -----------------------------------------------------------------------------

def validate_fleet_data(df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame]:
    """Validate and normalize fleet CSV."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return False, ["Empty file"], pd.DataFrame()

    norm = FleetAnalyzer.normalize_fleet_df(df)

    errors: List[str] = []
    for c in FleetAnalyzer.REQUIRED_COLUMNS:
        if c not in norm.columns:
            errors.append(f"Missing column: {c}")

    if norm.empty:
        errors.append("No valid rows after cleaning (check Age_Years values)")

    ok = len(errors) == 0
    return ok, errors, norm


def validate_device_inputs(device: str, persona: str, country: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if device not in DEVICES:
        errors.append("Unknown device")
    if persona not in PERSONAS:
        errors.append("Unknown persona")
    if country not in GRID_CARBON_FACTORS:
        errors.append("Unknown country")
    return len(errors) == 0, errors


def generate_demo_fleet(n: int = 150) -> List[Dict[str, Any]]:
    """Deterministic-ish demo dataset for the UI."""
    random.seed(42)
    device_names = list(DEVICES.keys())
    persona_names = list(PERSONAS.keys())
    countries = list(GRID_CARBON_FACTORS.keys())

    rows: List[Dict[str, Any]] = []
    for _ in range(int(n)):
        dev = random.choice(device_names)
        per = random.choice(persona_names)
        c = random.choice(countries)
        age = round(random.uniform(0.5, 6.5), 1)
        rows.append({"Device_Model": dev, "Age_Years": age, "Persona": per, "Country": c})
    return rows


def generate_synthetic_fleet(
    fleet_size: int,
    avg_age: float = 3.5,
    country: str = "FR",
    persona: str = "Admin Normal (HR/Finance)",
) -> pd.DataFrame:
    """Generate a synthetic fleet based on high-level parameters."""
    random.seed(7)
    device_names = list(DEVICES.keys())

    n = int(max(0, fleet_size))
    ages = [max(0.5, random.gauss(mu=float(avg_age), sigma=1.0)) for _ in range(n)]
    ages = [round(min(7.0, a), 1) for a in ages]

    return pd.DataFrame(
        {
            "Device_Model": [random.choice(device_names) for _ in range(n)],
            "Age_Years": ages,
            "Persona": [persona] * n,
            "Country": [country] * n,
        }
    )


def export_recommendations_to_csv(recos: List[DeviceRecommendation]) -> bytes:
    df = pd.DataFrame(
        [
            {
                "device": r.device,
                "persona": r.persona,
                "country": r.country,
                "recommendation": r.recommendation,
                "tco_total_eur": r.tco_total_eur,
                "co2_total_kg": r.co2_total_kg,
            }
            for r in (recos or [])
        ]
    )
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def generate_markdown_report(strategy: StrategyResult, fleet_profile: Dict[str, Any]) -> str:
    """Lightweight markdown report (UI can download it)."""
    fp = fleet_profile or {}
    lines = []
    lines.append("# Élysia Strategy Report")
    lines.append("")
    lines.append(f"## Recommended Strategy: {strategy.strategy_name}")
    if strategy.description:
        lines.append("")
        lines.append(strategy.description)

    lines.append("")
    lines.append("## Key Metrics")
    lines.append(f"- CO₂ reduction: {strategy.co2_reduction_pct:.1f}%")
    lines.append(f"- Annual savings: €{strategy.annual_savings_eur:,.0f}")
    ttt = strategy.time_to_target_months
    lines.append(f"- Time to target: {ttt} months" if ttt < 999 else "- Time to target: Not reached")
    lines.append(f"- Reaches target: {'Yes' if strategy.reaches_target else 'No'}")

    lines.append("")
    lines.append("## Fleet Profile")
    lines.append(f"- Fleet size: {int(fp.get('fleet_size', 0)):,}")
    lines.append(f"- Average age: {float(fp.get('avg_age', 0.0)):.1f} years")
    lines.append(f"- Annual replacements: {int(fp.get('annual_replacements', 0)):,}")

    return "\n".join(lines)


# Backwards-compat name (some UIs import this symbol)
StrategyEngine = StrategySimulator

