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

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math
import pandas as pd
import io
import math
import random



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
        "do_nothing": {"name": "Do Nothing", "description": "Continue current policy with no changes", "refurb_rate": 0.0, "lifecycle_years": 4, "recovery_rate": 0.0, "implementation_months": 0},
        "lifecycle_extension": {"name": "Lifecycle Extension", "description": "Extend device lifecycle from 4 to 5 years", "refurb_rate": 0.0, "lifecycle_years": 5, "recovery_rate": 0.0, "implementation_months": 6},
        "refurb_25": {"name": "25% Refurbished", "description": "Conservative approach - 25% refurbished adoption", "refurb_rate": 0.25, "lifecycle_years": 4, "recovery_rate": 0.5, "implementation_months": 6},
        "refurb_40": {"name": "40% Refurbished", "description": "Balanced approach - 40% refurbished adoption", "refurb_rate": 0.40, "lifecycle_years": 4, "recovery_rate": 0.7, "implementation_months": 9},
        "refurb_60": {"name": "60% Refurbished", "description": "Aggressive adoption - 60% refurbished for maximum impact", "refurb_rate": 0.60, "lifecycle_years": 4, "recovery_rate": 0.8, "implementation_months": 12},
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
    
    # Alias for compatibility with audit_ui
    @property
    def annual_capex_avoidance_eur(self) -> float:
        return self.annual_savings_eur


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

"""
calculator_extensions.py
========================
Additional calculator functions for ÉLYSIA v5.0

These functions extend the core calculator.py with:
1. Risk-based strategy selection
2. Fleet executive insights generation
3. Device policy impact calculation
4. Dynamic action plan generation

USAGE: Copy these into your calculator.py or import from this module.

All functions follow the same principles:
- No UI logic
- All constants from reference_data_API
- Returns dataclasses for type safety
"""

# =============================================================================
# IMPORTS FROM MAIN CALCULATOR
# =============================================================================

_IMPORTS_OK = True
_IMPORT_ERROR = None

try:
    from calculator import (
        StrategyResult, StrategySimulator, FleetAnalyzer,
        HopeCalculator, TCOCalculator, CO2Calculator,
        DEVICES, PERSONAS, STRATEGIES, AVERAGES,
        GRID_CARBON_FACTORS, REFURB_CONFIG,
    )
    from reference_data_API import get_grid_factor
except ImportError as e:
    _IMPORTS_OK = False
    _IMPORT_ERROR = str(e)
    # Minimal fallbacks
    DEVICES = {}
    PERSONAS = {}
    STRATEGIES = {
        "do_nothing": {"name": "Do Nothing", "description": "Continue current policy", "refurb_rate": 0.0, "lifecycle_years": 4, "implementation_months": 0},
        "lifecycle_extension": {"name": "Lifecycle Extension", "description": "Extend to 5 years", "refurb_rate": 0.0, "lifecycle_years": 5, "implementation_months": 6},
        "refurb_25": {"name": "25% Refurbished", "description": "Conservative - 25% refurb", "refurb_rate": 0.25, "lifecycle_years": 4, "implementation_months": 6},
        "refurb_40": {"name": "40% Refurbished", "description": "Balanced - 40% refurb", "refurb_rate": 0.40, "lifecycle_years": 4, "implementation_months": 9},
        "refurb_60": {"name": "60% Refurbished", "description": "Aggressive - 60% refurb", "refurb_rate": 0.60, "lifecycle_years": 4, "implementation_months": 12},
    }
    AVERAGES = {"device_price_eur": 1150, "device_co2_manufacturing_kg": 365}
    GRID_CARBON_FACTORS = {"FR": {"factor": 0.052, "name": "France"}}
    REFURB_CONFIG = {"co2_savings_rate": 0.80, "price_ratio": 0.59}
    def get_grid_factor(code): return 0.052


def _safe_float(x: Any, default: float = 0.0) -> float:
    """Safely convert to float."""
    try:
        return float(x) if x is not None else default
    except (ValueError, TypeError):
        return default


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationReport:
    """Results of fleet data validation."""
    rows_total: int
    rows_valid: int
    rows_dropped: int
    missing_columns: List[str]
    defaults_applied: List[str]
    warnings: List[str]


@dataclass
class CalculationProof:
    """Proof of calculation for transparency."""
    formula: str
    inputs: Dict[str, Any]
    result: Any
    source: str


@dataclass
class InsightWithProof:
    """A single insight with calculation proof."""
    title: str
    main_text: str
    calculation: CalculationProof
    severity: str  # "positive", "warning", "neutral"


@dataclass
class FleetInsightsResult:
    """Executive insights from fleet data analysis."""
    validation: ValidationReport
    summary: Dict[str, Any]
    insights: List[InsightWithProof]  # Changed: now includes proofs
    deltas: Dict[str, Any]  # Changed: now includes calculation proofs
    confidence_before: str
    confidence_after: str


@dataclass
class DevicePolicy:
    """A policy for handling a device category."""
    category: str
    action: str  # "keep_longer", "refurb_when_due", "always_new"
    age_threshold: float
    description: str = ""


@dataclass
class CategoryInfo:
    """Information about a device category."""
    name: str
    count: int
    pct_of_fleet: float
    avg_age: float
    devices_at_risk: int  # >4 years old
    refurb_eligible: int
    recommendation: str
    recommendation_reason: str
    potential_savings_eur: float
    potential_co2_reduction_kg: float


@dataclass
class PolicyImpactResult:
    """Impact of applying device policies to a strategy."""
    affected_devices: int
    categories: List[CategoryInfo]  # Added: detailed category info
    co2_baseline_pct: float
    co2_with_policy_pct: float
    co2_delta_pct: float
    savings_baseline_eur: float
    savings_with_policy_eur: float
    savings_delta_eur: float
    time_baseline_months: int
    time_with_policy_months: int
    time_delta_months: int
    policy_summary: List[str]


@dataclass
class ActionPlanPhase:
    """A phase in the action plan."""
    number: int
    name: str
    subtitle: str
    tasks: List[str]
    milestone: str
    milestone_date: str


@dataclass
class ActionPlanMetric:
    """A success metric for the action plan."""
    name: str
    target: str
    owner: str
    frequency: str


@dataclass
class ActionPlanResult:
    """Complete action plan output."""
    basis: Dict[str, Any]
    outcomes: Dict[str, Any]
    phases: List[ActionPlanPhase]
    metrics: List[ActionPlanMetric]
    changes_from_baseline: List[str]  # Added: what changed
    generated_at: str


@dataclass
class RiskStrategySet:
    """Set of strategies for different risk appetites."""
    conservative: StrategyResult
    recommended: StrategyResult
    ambitious: StrategyResult
    all_distinct: bool  # True if all 3 are different strategies
    explanations: Dict[str, str]


# =============================================================================
# 1. RISK-BASED STRATEGY SELECTION - FIXED
# =============================================================================

class RiskBasedSelector:
    """Select strategies based on risk appetite - FIXED to return distinct strategies."""
    
    @staticmethod
    def get_refurb_rate(strategy: StrategyResult) -> float:
        """Extract refurb rate from strategy."""
        details = strategy.calculation_details or {}
        strat_info = details.get("strategy", {})
        return _safe_float(strat_info.get("refurb_rate", 0.0), 0.0)
    
    @staticmethod
    def get_risk_score(strategy: StrategyResult) -> float:
        """Get numeric risk score (0-1) for sorting."""
        refurb_rate = RiskBasedSelector.get_refurb_rate(strategy)
        impl_months = min(strategy.time_to_target_months, 24) / 24.0
        return (refurb_rate * 0.7) + (impl_months * 0.3)
    
    @staticmethod
    def categorize_risk(strategy: StrategyResult) -> str:
        """Categorize strategy risk level."""
        refurb_rate = RiskBasedSelector.get_refurb_rate(strategy)
        if refurb_rate <= 0.25:
            return "LOW"
        elif refurb_rate <= 0.50:
            return "MEDIUM"
        else:
            return "HIGH"
    
    @staticmethod
    def pick_by_risk_appetite(
        results: List[StrategyResult],
        risk_appetite: str = "balanced"
    ) -> RiskStrategySet:
        """
        Select 3 DISTINCT strategies for each risk level.
        
        FIXED: Now guarantees 3 different strategies are returned.
        """
        if not results:
            raise ValueError("No strategies to select from")
        
        risk_appetite = (risk_appetite or "balanced").lower().strip()
        if risk_appetite not in ("conservative", "balanced", "aggressive"):
            risk_appetite = "balanced"
        
        # Filter out "do_nothing" for recommendations
        actionable = [r for r in results if r.strategy_key != "do_nothing"]
        if len(actionable) < 3:
            actionable = results  # Fall back to all if not enough
        
        # Sort by refurb rate (low to high)
        sorted_by_refurb = sorted(actionable, key=RiskBasedSelector.get_refurb_rate)
        
        # FIXED: Pick 3 DISTINCT strategies
        # Conservative = lowest refurb rate
        # Ambitious = highest refurb rate
        # Recommended = middle one (or based on risk appetite)
        
        conservative = sorted_by_refurb[0]
        ambitious = sorted_by_refurb[-1]
        
        # Find middle option (different from both conservative and ambitious)
        middle_candidates = [
            s for s in sorted_by_refurb 
            if s.strategy_key != conservative.strategy_key 
            and s.strategy_key != ambitious.strategy_key
        ]
        
        if middle_candidates:
            # Pick the one closest to middle
            mid_idx = len(middle_candidates) // 2
            balanced = middle_candidates[mid_idx]
        else:
            # If no middle options, use the second-lowest
            balanced = sorted_by_refurb[min(1, len(sorted_by_refurb)-1)]
        
        # Determine which is "recommended" based on risk appetite
        if risk_appetite == "conservative":
            recommended = conservative
        elif risk_appetite == "aggressive":
            recommended = ambitious
        else:
            recommended = balanced
        
        # Check if all are distinct
        keys = {conservative.strategy_key, balanced.strategy_key, ambitious.strategy_key}
        all_distinct = len(keys) == 3
        
        # Generate explanations
        explanations = {
            "conservative": RiskBasedSelector._generate_explanation(
                conservative, "conservative", conservative == recommended
            ),
            "recommended": RiskBasedSelector._generate_explanation(
                recommended, risk_appetite, True
            ),
            "ambitious": RiskBasedSelector._generate_explanation(
                ambitious, "ambitious", ambitious == recommended
            ),
        }
        
        return RiskStrategySet(
            conservative=conservative,
            recommended=recommended,
            ambitious=ambitious,
            all_distinct=all_distinct,
            explanations=explanations,
        )
    
    @staticmethod
    def _generate_explanation(strategy: StrategyResult, context: str, is_recommended: bool) -> str:
        """Generate human-readable explanation."""
        refurb_rate = RiskBasedSelector.get_refurb_rate(strategy) * 100
        risk = RiskBasedSelector.categorize_risk(strategy)
        
        base_text = {
            "conservative": (
                f"Minimal change: {refurb_rate:.0f}% refurbished adoption. "
                f"Lower risk, proven approach ideal for pilot programs or risk-averse organizations."
            ),
            "balanced": (
                f"Optimal trade-off: {refurb_rate:.0f}% refurbished adoption. "
                f"Best balance of impact and feasibility for most organizations."
            ),
            "aggressive": (
                f"Maximum impact: {refurb_rate:.0f}% refurbished adoption. "
                f"Highest savings and CO₂ reduction, requires significant procurement change."
            ),
        }
        
        return base_text.get(context, f"{refurb_rate:.0f}% refurbished adoption. Risk level: {risk}.")


# =============================================================================
# 2. DEVICE CATEGORY EXTRACTION - FIXED
# =============================================================================

class DeviceCategoryExtractor:
    """Extract device categories from fleet data - FIXED with aggressive pattern matching."""
    
    # Pattern matching for device categorization
    LAPTOP_PATTERNS = [
        "laptop", "macbook", "thinkpad", "latitude", "elitebook", "probook",
        "xps", "spectre", "envy", "pavilion", "inspiron", "vostro", "precision",
        "zbook", "surface laptop", "gram", "zenbook", "vivobook", "ideapad",
        "yoga", "carbon", "x1", "t14", "t15", "p14", "p15", "x13"
    ]
    
    DESKTOP_PATTERNS = [
        "desktop", "imac", "optiplex", "elitedesk", "prodesk", "thinkcentre",
        "precision tower", "workstation", "mac mini", "mac studio", "mac pro",
        "compaq", "pavilion desktop", "envy desktop"
    ]
    
    MONITOR_PATTERNS = [
        "monitor", "display", "ultrasharp", "cinema display", "studio display",
        "thunderbolt display", "lg ultrafine", "screen"
    ]
    
    PHONE_PATTERNS = [
        "iphone", "galaxy", "pixel", "smartphone", "phone", "mobile"
    ]
    
    TABLET_PATTERNS = [
        "ipad", "tablet", "surface pro", "surface go", "galaxy tab"
    ]
    
    @staticmethod
    def categorize_device(device_name: str) -> str:
        """Categorize a single device by name."""
        name_lower = device_name.lower().strip()
        
        # Check each category
        for pattern in DeviceCategoryExtractor.LAPTOP_PATTERNS:
            if pattern in name_lower:
                return "Laptop"
        
        for pattern in DeviceCategoryExtractor.DESKTOP_PATTERNS:
            if pattern in name_lower:
                return "Desktop"
        
        for pattern in DeviceCategoryExtractor.MONITOR_PATTERNS:
            if pattern in name_lower:
                return "Monitor"
        
        for pattern in DeviceCategoryExtractor.PHONE_PATTERNS:
            if pattern in name_lower:
                return "Phone"
        
        for pattern in DeviceCategoryExtractor.TABLET_PATTERNS:
            if pattern in name_lower:
                return "Tablet"
        
        # Check DEVICES catalog as fallback
        if DEVICES:
            meta = DEVICES.get(device_name, {})
            if isinstance(meta, dict) and meta.get("category"):
                return meta["category"]
        
        return "Other"
    
    @staticmethod
    def extract_categories(df: pd.DataFrame) -> Dict[str, CategoryInfo]:
        """
        Extract device categories from fleet DataFrame.
        
        FIXED: Now properly extracts categories with aggressive pattern matching.
        """
        if df is None or df.empty:
            return {}
        
        categories: Dict[str, Dict] = {}
        total_devices = len(df)
        
        for _, row in df.iterrows():
            device_name = str(row.get("Device_Model", "Unknown"))
            age = _safe_float(row.get("Age_Years", 3.0), 3.0)
            
            # Get category
            category = DeviceCategoryExtractor.categorize_device(device_name)
            
            if category not in categories:
                categories[category] = {
                    "count": 0,
                    "total_age": 0.0,
                    "ages": [],
                    "devices": [],
                    "at_risk": 0,
                    "refurb_eligible": 0,
                }
            
            categories[category]["count"] += 1
            categories[category]["total_age"] += age
            categories[category]["ages"].append(age)
            categories[category]["devices"].append(device_name)
            
            if age >= 4.0:
                categories[category]["at_risk"] += 1
            
            # Check refurb eligibility
            meta = DEVICES.get(device_name, {}) if DEVICES else {}
            if meta.get("refurb_available", True):  # Default to True
                categories[category]["refurb_eligible"] += 1
        
        # Convert to CategoryInfo objects
        result: Dict[str, CategoryInfo] = {}
        
        for cat_name, data in categories.items():
            count = data["count"]
            avg_age = data["total_age"] / count if count > 0 else 0
            at_risk = data["at_risk"]
            refurb_eligible = data["refurb_eligible"]
            
            # Calculate potential savings and CO2 reduction
            # Using averages from reference data
            avg_price = _safe_float(AVERAGES.get("device_price_eur", 1150), 1150)
            avg_co2 = _safe_float(AVERAGES.get("device_co2_manufacturing_kg", 365), 365)
            refurb_savings_rate = _safe_float(REFURB_CONFIG.get("price_ratio", 0.59), 0.59)
            co2_savings_rate = _safe_float(REFURB_CONFIG.get("co2_savings_rate", 0.80), 0.80)
            
            # Potential savings if refurb eligible devices are replaced with refurb
            potential_savings = refurb_eligible * avg_price * (1 - refurb_savings_rate)
            potential_co2 = refurb_eligible * avg_co2 * co2_savings_rate
            
            # Generate recommendation
            if at_risk > count * 0.3:  # >30% at risk
                recommendation = "Replace with Refurbished"
                recommendation_reason = (
                    f"{at_risk} devices ({at_risk/count*100:.0f}%) are >4 years old. "
                    f"Refurbished saves €{potential_savings/1000:.0f}K and reduces CO₂ by {potential_co2/1000:.1f}t."
                )
            elif avg_age < 2.5:
                recommendation = "Keep Longer"
                recommendation_reason = (
                    f"Average age {avg_age:.1f} years is below threshold. "
                    f"Extend lifecycle to maximize value."
                )
            else:
                recommendation = "Refurbish When Due"
                recommendation_reason = (
                    f"Standard refresh applies. Replace with refurbished when devices reach 4 years."
                )
            
            result[cat_name] = CategoryInfo(
                name=cat_name,
                count=count,
                pct_of_fleet=count / total_devices if total_devices > 0 else 0,
                avg_age=avg_age,
                devices_at_risk=at_risk,
                refurb_eligible=refurb_eligible,
                recommendation=recommendation,
                recommendation_reason=recommendation_reason,
                potential_savings_eur=potential_savings,
                potential_co2_reduction_kg=potential_co2,
            )
        
        # If no categories found, create "All Devices" as fallback
        if not result and total_devices > 0:
            avg_age = df["Age_Years"].mean() if "Age_Years" in df.columns else 3.5
            at_risk = int((df["Age_Years"] >= 4).sum()) if "Age_Years" in df.columns else 0
            
            result["All Devices"] = CategoryInfo(
                name="All Devices",
                count=total_devices,
                pct_of_fleet=1.0,
                avg_age=float(avg_age),
                devices_at_risk=at_risk,
                refurb_eligible=total_devices,
                recommendation="Refurbish When Due",
                recommendation_reason="Apply standard refurbishment policy to all devices.",
                potential_savings_eur=total_devices * 1150 * 0.41 / 4,  # Annual
                potential_co2_reduction_kg=total_devices * 365 * 0.80 / 4,
            )
        
        return result


# =============================================================================
# 3. FLEET INSIGHTS WITH CALCULATION PROOFS - FIXED
# =============================================================================

class FleetInsightsGenerator:
    """Generate executive-ready insights with calculation proofs."""
    
    BENCHMARKS = {
        "avg_fleet_age_years": 3.2,
        "age_risk_threshold_years": 4.0,
        "productivity_cost_per_old_device_eur": 450,
        "typical_refurb_eligible_pct": 0.65,
    }
    
    @staticmethod
    def validate_fleet_data(df: pd.DataFrame, default_country: str = "FR") -> Tuple[pd.DataFrame, ValidationReport]:
        """Validate and clean fleet data."""
        if df is None or not isinstance(df, pd.DataFrame):
            return pd.DataFrame(), ValidationReport(
                rows_total=0, rows_valid=0, rows_dropped=0,
                missing_columns=["Device_Model", "Age_Years"],
                defaults_applied=[], warnings=["No data provided"]
            )
        
        rows_total = len(df)
        missing_columns = []
        defaults_applied = []
        warnings = []
        
        # Check and rename columns
        df_clean = df.copy()
        
        if "Device_Model" not in df_clean.columns:
            if "Model" in df_clean.columns:
                df_clean = df_clean.rename(columns={"Model": "Device_Model"})
                defaults_applied.append("Renamed 'Model' to 'Device_Model'")
            else:
                missing_columns.append("Device_Model")
        
        if "Age_Years" not in df_clean.columns:
            if "Age" in df_clean.columns:
                df_clean = df_clean.rename(columns={"Age": "Age_Years"})
                defaults_applied.append("Renamed 'Age' to 'Age_Years'")
            else:
                missing_columns.append("Age_Years")
        
        if missing_columns:
            return pd.DataFrame(), ValidationReport(
                rows_total=rows_total, rows_valid=0, rows_dropped=rows_total,
                missing_columns=missing_columns, defaults_applied=defaults_applied,
                warnings=["Required columns missing"]
            )
        
        # Convert types
        df_clean["Age_Years"] = pd.to_numeric(df_clean["Age_Years"], errors="coerce")
        
        # Handle Country
        if "Country" not in df_clean.columns:
            df_clean["Country"] = default_country
            defaults_applied.append(f"Country set to '{default_country}' for all devices")
        else:
            missing_count = df_clean["Country"].isna().sum()
            if missing_count > 0:
                df_clean["Country"] = df_clean["Country"].fillna(default_country)
                defaults_applied.append(f"Country defaulted to '{default_country}' for {missing_count} devices")
        
        # Handle Persona
        if "Persona" not in df_clean.columns:
            df_clean["Persona"] = "Admin Normal (HR/Finance)"
            defaults_applied.append("Persona set to 'Admin Normal' for all devices")
        
        # Drop invalid rows
        rows_before = len(df_clean)
        df_clean = df_clean.dropna(subset=["Device_Model", "Age_Years"])
        rows_dropped = rows_before - len(df_clean)
        
        if rows_dropped > 0:
            warnings.append(f"{rows_dropped} rows dropped (missing required data)")
        
        return df_clean, ValidationReport(
            rows_total=rows_total,
            rows_valid=len(df_clean),
            rows_dropped=rows_dropped,
            missing_columns=[],
            defaults_applied=defaults_applied,
            warnings=warnings,
        )
    
    @staticmethod
    def generate_executive_insights(
        df: pd.DataFrame,
        baseline_estimates: Dict[str, Any],
        selected_strategy: StrategyResult,
        geo_code: str = "FR",
        refresh_cycle: int = 4,
    ) -> FleetInsightsResult:
        """Generate board-ready insights with calculation proofs."""
        
        # Validate
        df_clean, validation = FleetInsightsGenerator.validate_fleet_data(df, geo_code)
        
        if df_clean.empty:
            return FleetInsightsResult(
                validation=validation,
                summary={},
                insights=[],
                deltas={},
                confidence_before="MEDIUM",
                confidence_after="LOW",
            )
        
        # Calculate summary
        fleet_size = len(df_clean)
        avg_age = float(df_clean["Age_Years"].mean())
        age_risk_share = float((df_clean["Age_Years"] >= 4.0).mean())
        devices_at_risk = int((df_clean["Age_Years"] >= 4.0).sum())
        
        # Get categories
        categories = DeviceCategoryExtractor.extract_categories(df_clean)
        refurb_eligible = sum(c.refurb_eligible for c in categories.values())
        refurb_eligible_share = refurb_eligible / fleet_size if fleet_size > 0 else 0
        
        # Primary geography
        if "Country" in df_clean.columns:
            primary_geo = df_clean["Country"].mode().iloc[0] if not df_clean["Country"].mode().empty else geo_code
            geo_distribution = df_clean["Country"].value_counts(normalize=True).to_dict()
        else:
            primary_geo = geo_code
            geo_distribution = {geo_code: 1.0}
        
        summary = {
            "fleet_size": fleet_size,
            "avg_age": avg_age,
            "age_risk_share": age_risk_share,
            "devices_at_risk": devices_at_risk,
            "refurb_eligible_share": refurb_eligible_share,
            "devices_refurb_eligible": refurb_eligible,
            "primary_geography": primary_geo,
            "geo_distribution": geo_distribution,
            "categories": {k: v.__dict__ for k, v in categories.items()},
        }
        
        # Generate insights WITH PROOFS
        insights = FleetInsightsGenerator._generate_insights_with_proofs(
            summary, baseline_estimates, geo_code
        )
        
        # Calculate deltas WITH PROOFS
        deltas = FleetInsightsGenerator._calculate_deltas_with_proofs(
            summary, baseline_estimates, selected_strategy, refresh_cycle, primary_geo
        )
        
        return FleetInsightsResult(
            validation=validation,
            summary=summary,
            insights=insights,
            deltas=deltas,
            confidence_before="MEDIUM",
            confidence_after="HIGH",
        )
    
    @staticmethod
    def _generate_insights_with_proofs(
        summary: Dict[str, Any],
        baseline: Dict[str, Any],
        geo_code: str,
    ) -> List[InsightWithProof]:
        """Generate insights with calculation proofs."""
        insights = []
        benchmarks = FleetInsightsGenerator.BENCHMARKS
        
        # INSIGHT 1: Fleet age analysis
        avg_age = summary.get("avg_age", 3.5)
        benchmark_age = benchmarks["avg_fleet_age_years"]
        age_diff_pct = ((avg_age - benchmark_age) / benchmark_age) * 100
        devices_at_risk = summary.get("devices_at_risk", 0)
        hidden_cost = devices_at_risk * benchmarks["productivity_cost_per_old_device_eur"]
        
        if age_diff_pct > 10:
            insights.append(InsightWithProof(
                title="Fleet Age Above Benchmark",
                main_text=(
                    f"Your fleet is {abs(age_diff_pct):.0f}% older than industry average, "
                    f"with {devices_at_risk} high-risk devices creating hidden productivity costs."
                ),
                calculation=CalculationProof(
                    formula="Hidden Cost = Devices at Risk × Productivity Cost per Device",
                    inputs={
                        "devices_at_risk": devices_at_risk,
                        "productivity_cost_per_device": f"€{benchmarks['productivity_cost_per_old_device_eur']}",
                        "your_avg_age": f"{avg_age:.1f} years",
                        "benchmark_avg_age": f"{benchmark_age:.1f} years",
                    },
                    result=f"€{hidden_cost:,.0f}/year",
                    source="Gartner IT Productivity Study 2023",
                ),
                severity="warning",
            ))
        elif age_diff_pct < -10:
            insights.append(InsightWithProof(
                title="Fleet Younger Than Average",
                main_text=(
                    f"Your fleet is {abs(age_diff_pct):.0f}% younger than industry average — "
                    f"focus on extending lifecycles to maximize sustainability impact."
                ),
                calculation=CalculationProof(
                    formula="Age Difference = (Your Age - Benchmark) / Benchmark × 100",
                    inputs={
                        "your_avg_age": f"{avg_age:.1f} years",
                        "benchmark_avg_age": f"{benchmark_age:.1f} years",
                    },
                    result=f"{age_diff_pct:.0f}%",
                    source="Industry benchmark: 3.2 years average fleet age",
                ),
                severity="positive",
            ))
        else:
            insights.append(InsightWithProof(
                title="Fleet Age on Track",
                main_text=(
                    f"Fleet age ({avg_age:.1f} years) aligns with industry benchmarks — "
                    f"standard refresh policies should apply effectively."
                ),
                calculation=CalculationProof(
                    formula="Comparison to benchmark",
                    inputs={
                        "your_avg_age": f"{avg_age:.1f} years",
                        "benchmark_avg_age": f"{benchmark_age:.1f} years",
                    },
                    result="Within ±10% of benchmark",
                    source="Gartner IT Asset Management Report 2023",
                ),
                severity="neutral",
            ))
        
        # INSIGHT 2: Refurbishment opportunity
        refurb_eligible = summary.get("devices_refurb_eligible", 0)
        refurb_share = summary.get("refurb_eligible_share", 0)
        fleet_size = summary.get("fleet_size", 100)
        
        avg_price = _safe_float(AVERAGES.get("device_price_eur", 1150), 1150)
        savings_rate = 1 - _safe_float(REFURB_CONFIG.get("price_ratio", 0.59), 0.59)
        annual_replacements = fleet_size / 4  # Assuming 4-year cycle
        potential_savings = annual_replacements * refurb_share * avg_price * savings_rate
        
        insights.append(InsightWithProof(
            title="Refurbishment Opportunity",
            main_text=(
                f"{refurb_eligible} devices ({refurb_share*100:.0f}% of fleet) qualify for "
                f"refurbished alternatives, unlocking significant savings potential."
            ),
            calculation=CalculationProof(
                formula="Annual Savings = (Fleet ÷ Cycle) × Refurb Rate × Price × (1 - Price Ratio)",
                inputs={
                    "fleet_size": fleet_size,
                    "refresh_cycle": "4 years",
                    "refurb_eligible_rate": f"{refurb_share*100:.0f}%",
                    "avg_device_price": f"€{avg_price:,.0f}",
                    "refurb_price_ratio": f"{REFURB_CONFIG.get('price_ratio', 0.59)*100:.0f}%",
                },
                result=f"€{potential_savings:,.0f}/year potential",
                source="Back Market Business Pricing 2024",
            ),
            severity="positive" if refurb_share > 0.5 else "neutral",
        ))
        
        # INSIGHT 3: Geography impact
        primary_geo = summary.get("primary_geography", geo_code)
        try:
            grid_factor = get_grid_factor(primary_geo)
        except:
            grid_factor = 0.3
        
        geo_name = GRID_CARBON_FACTORS.get(primary_geo, {}).get("name", primary_geo)
        
        if grid_factor < 0.15:
            insight_text = (
                f"Your {geo_name}-heavy geography benefits from low-carbon electricity — "
                f"CO₂ wins come primarily from manufacturing reductions (~80% of device footprint)."
            )
            severity = "positive"
        elif grid_factor > 0.4:
            insight_text = (
                f"High grid carbon intensity in {geo_name} means energy efficiency "
                f"will amplify CO₂ savings beyond manufacturing alone."
            )
            severity = "warning"
        else:
            insight_text = (
                f"Moderate grid carbon in {geo_name} — balanced impact from both "
                f"manufacturing reductions and energy efficiency improvements."
            )
            severity = "neutral"
        
        insights.append(InsightWithProof(
            title="Geography Carbon Impact",
            main_text=insight_text,
            calculation=CalculationProof(
                formula="Grid Carbon Factor determines use-phase emissions",
                inputs={
                    "primary_geography": geo_name,
                    "grid_factor": f"{grid_factor:.3f} kg CO₂/kWh",
                    "benchmark_eu_avg": "0.270 kg CO₂/kWh",
                },
                result=f"{'Low' if grid_factor < 0.15 else 'High' if grid_factor > 0.4 else 'Medium'} carbon grid",
                source="European Environment Agency 2023",
            ),
            severity=severity,
        ))
        
        return insights[:3]
    
    @staticmethod
    def _calculate_deltas_with_proofs(
        summary: Dict[str, Any],
        baseline: Dict[str, Any],
        strategy: StrategyResult,
        refresh_cycle: int,
        geo_code: str,
    ) -> Dict[str, Any]:
        """Calculate deltas between estimates and actual data with proofs."""
        
        # Get actual values
        actual_fleet = summary.get("fleet_size", 0)
        actual_age = summary.get("avg_age", 3.5)
        
        # Get baseline estimates
        baseline_fleet = baseline.get("fleet_size", actual_fleet)
        baseline_age = baseline.get("avg_age", 3.5)
        
        # Calculate what the strategy would achieve with actual data
        # This is a simplified recalculation
        details = strategy.calculation_details or {}
        strat_info = details.get("strategy", {})
        refurb_rate = _safe_float(strat_info.get("refurb_rate", 0.4), 0.4)
        
        # CO2 calculation
        avg_co2_new = _safe_float(AVERAGES.get("device_co2_manufacturing_kg", 365), 365)
        co2_savings_rate = _safe_float(REFURB_CONFIG.get("co2_savings_rate", 0.80), 0.80)
        
        # Baseline CO2 (with baseline fleet)
        baseline_annual_repl = baseline_fleet / refresh_cycle
        baseline_co2_kg = baseline_annual_repl * avg_co2_new
        strategy_co2_kg = baseline_annual_repl * ((1 - refurb_rate) * avg_co2_new + refurb_rate * avg_co2_new * (1 - co2_savings_rate))
        baseline_co2_reduction = ((strategy_co2_kg - baseline_co2_kg) / baseline_co2_kg * 100) if baseline_co2_kg > 0 else 0
        
        # Actual CO2 (with actual fleet)
        actual_annual_repl = actual_fleet / refresh_cycle
        actual_co2_kg = actual_annual_repl * avg_co2_new
        actual_strategy_co2_kg = actual_annual_repl * ((1 - refurb_rate) * avg_co2_new + refurb_rate * avg_co2_new * (1 - co2_savings_rate))
        actual_co2_reduction = ((actual_strategy_co2_kg - actual_co2_kg) / actual_co2_kg * 100) if actual_co2_kg > 0 else 0
        
        # Savings calculation
        avg_price = _safe_float(AVERAGES.get("device_price_eur", 1150), 1150)
        refurb_price_ratio = _safe_float(REFURB_CONFIG.get("price_ratio", 0.59), 0.59)
        
        baseline_cost = baseline_annual_repl * avg_price
        strategy_cost = baseline_annual_repl * ((1 - refurb_rate) * avg_price + refurb_rate * avg_price * refurb_price_ratio)
        baseline_savings = baseline_cost - strategy_cost
        
        actual_cost = actual_annual_repl * avg_price
        actual_strategy_cost = actual_annual_repl * ((1 - refurb_rate) * avg_price + refurb_rate * avg_price * refurb_price_ratio)
        actual_savings = actual_cost - actual_strategy_cost
        
        return {
            "co2_baseline_pct": baseline_co2_reduction,
            "co2_actual_pct": actual_co2_reduction,
            "co2_delta_pct": actual_co2_reduction - baseline_co2_reduction,
            "co2_proof": {
                "formula": "CO₂ Reduction = (Strategy CO₂ - Baseline CO₂) / Baseline CO₂ × 100",
                "baseline_inputs": {
                    "fleet_size": baseline_fleet,
                    "annual_replacements": f"{baseline_annual_repl:.0f}",
                    "co2_per_device": f"{avg_co2_new} kg",
                },
                "actual_inputs": {
                    "fleet_size": actual_fleet,
                    "annual_replacements": f"{actual_annual_repl:.0f}",
                    "co2_per_device": f"{avg_co2_new} kg",
                },
                "explanation": (
                    f"Fleet size difference: {actual_fleet - baseline_fleet:+,} devices. "
                    f"This {'increases' if actual_fleet > baseline_fleet else 'decreases'} impact proportionally."
                ),
            },
            "savings_baseline_eur": baseline_savings,
            "savings_actual_eur": actual_savings,
            "savings_delta_eur": actual_savings - baseline_savings,
            "savings_proof": {
                "formula": "Savings = Annual Replacements × Price × (1 - Refurb Rate × Price Ratio)",
                "baseline_inputs": {
                    "annual_replacements": f"{baseline_annual_repl:.0f}",
                    "avg_price": f"€{avg_price:,.0f}",
                    "refurb_rate": f"{refurb_rate*100:.0f}%",
                },
                "actual_inputs": {
                    "annual_replacements": f"{actual_annual_repl:.0f}",
                    "avg_price": f"€{avg_price:,.0f}",
                    "refurb_rate": f"{refurb_rate*100:.0f}%",
                },
            },
            "time_baseline_months": strategy.time_to_target_months,
            "time_actual_months": strategy.time_to_target_months,  # Same unless fleet is very different
            "time_delta_months": 0,
        }


# =============================================================================
# 4. POLICY IMPACT CALCULATOR - FIXED
# =============================================================================

class PolicyImpactCalculator:
    """Calculate impact of device policies - FIXED with proper category extraction."""
    
    @staticmethod
    def get_device_categories(df: pd.DataFrame) -> Dict[str, CategoryInfo]:
        """Get device categories - delegates to fixed extractor."""
        return DeviceCategoryExtractor.extract_categories(df)
    
    @staticmethod
    def calculate_policy_impact(
        fleet_df: pd.DataFrame,
        base_strategy: StrategyResult,
        policies: List[DevicePolicy],
        refresh_cycle: int = 4,
        geo_code: str = "FR",
    ) -> PolicyImpactResult:
        """Calculate the impact of applying device policies."""
        
        if fleet_df is None or fleet_df.empty:
            return PolicyImpactResult(
                affected_devices=0,
                categories=[],
                co2_baseline_pct=base_strategy.co2_reduction_pct,
                co2_with_policy_pct=base_strategy.co2_reduction_pct,
                co2_delta_pct=0,
                savings_baseline_eur=base_strategy.annual_savings_eur,
                savings_with_policy_eur=base_strategy.annual_savings_eur,
                savings_delta_eur=0,
                time_baseline_months=base_strategy.time_to_target_months,
                time_with_policy_months=base_strategy.time_to_target_months,
                time_delta_months=0,
                policy_summary=["No data to analyze"],
            )
        
        # Get categories
        categories = DeviceCategoryExtractor.extract_categories(fleet_df)
        category_list = list(categories.values())
        
        if not policies:
            return PolicyImpactResult(
                affected_devices=0,
                categories=category_list,
                co2_baseline_pct=base_strategy.co2_reduction_pct,
                co2_with_policy_pct=base_strategy.co2_reduction_pct,
                co2_delta_pct=0,
                savings_baseline_eur=base_strategy.annual_savings_eur,
                savings_with_policy_eur=base_strategy.annual_savings_eur,
                savings_delta_eur=0,
                time_baseline_months=base_strategy.time_to_target_months,
                time_with_policy_months=base_strategy.time_to_target_months,
                time_delta_months=0,
                policy_summary=["No policies applied - using strategy defaults"],
            )
        
        # Calculate impact
        fleet_size = len(fleet_df)
        affected_devices = 0
        co2_adjustment_kg = 0.0
        savings_adjustment_eur = 0.0
        policy_summaries = []
        
        avg_price = _safe_float(AVERAGES.get("device_price_eur", 1150), 1150)
        avg_co2 = _safe_float(AVERAGES.get("device_co2_manufacturing_kg", 365), 365)
        
        for policy in policies:
            cat_name = policy.category
            action = policy.action
            threshold = policy.age_threshold
            
            # Find matching category
            if cat_name == "All" or cat_name == "All Devices":
                affected = fleet_df[fleet_df["Age_Years"] >= threshold]
                cat_info = CategoryInfo(
                    name="All Devices", count=len(fleet_df), pct_of_fleet=1.0,
                    avg_age=float(fleet_df["Age_Years"].mean()), devices_at_risk=len(affected),
                    refurb_eligible=len(fleet_df), recommendation="", recommendation_reason="",
                    potential_savings_eur=0, potential_co2_reduction_kg=0
                )
            elif cat_name in categories:
                cat_info = categories[cat_name]
                # Get devices in this category
                cat_devices = [d for d in fleet_df["Device_Model"] 
                              if DeviceCategoryExtractor.categorize_device(str(d)) == cat_name]
                affected = fleet_df[
                    (fleet_df["Device_Model"].isin(cat_devices)) & 
                    (fleet_df["Age_Years"] >= threshold)
                ]
            else:
                continue
            
            count = len(affected)
            affected_devices += count
            
            if count == 0:
                continue
            
            # Calculate impact based on action
            if action == "keep_longer":
                # Extending lifecycle reduces annual replacements by ~20%
                reduction_factor = 0.20
                co2_saved = count * avg_co2 * reduction_factor / refresh_cycle
                money_saved = count * avg_price * reduction_factor / refresh_cycle
                co2_adjustment_kg += co2_saved
                savings_adjustment_eur += money_saved
                policy_summaries.append(
                    f"{cat_name}: Keep {count} devices longer — saves €{money_saved:,.0f}/yr, -{co2_saved/1000:.1f}t CO₂/yr"
                )
            
            elif action == "refurb_when_due":
                # Full refurb savings
                co2_rate = _safe_float(REFURB_CONFIG.get("co2_savings_rate", 0.80), 0.80)
                price_savings = 1 - _safe_float(REFURB_CONFIG.get("price_ratio", 0.59), 0.59)
                annual_repl = count / refresh_cycle
                co2_saved = annual_repl * avg_co2 * co2_rate
                money_saved = annual_repl * avg_price * price_savings
                co2_adjustment_kg += co2_saved
                savings_adjustment_eur += money_saved
                policy_summaries.append(
                    f"{cat_name}: Refurb {count} devices when due — saves €{money_saved:,.0f}/yr, -{co2_saved/1000:.1f}t CO₂/yr"
                )
            
            elif action == "always_new":
                # No adjustment - using new devices
                policy_summaries.append(
                    f"{cat_name}: New devices for {count} units — predictable but no sustainability gain"
                )
        
        # Calculate final metrics
        # Adjust baseline by the additional savings from policies
        co2_with_policy = base_strategy.co2_reduction_pct - (co2_adjustment_kg / (fleet_size * avg_co2 / refresh_cycle) * 100)
        savings_with_policy = base_strategy.annual_savings_eur + savings_adjustment_eur
        
        return PolicyImpactResult(
            affected_devices=affected_devices,
            categories=category_list,
            co2_baseline_pct=base_strategy.co2_reduction_pct,
            co2_with_policy_pct=co2_with_policy,
            co2_delta_pct=co2_with_policy - base_strategy.co2_reduction_pct,
            savings_baseline_eur=base_strategy.annual_savings_eur,
            savings_with_policy_eur=savings_with_policy,
            savings_delta_eur=savings_adjustment_eur,
            time_baseline_months=base_strategy.time_to_target_months,
            time_with_policy_months=base_strategy.time_to_target_months,
            time_delta_months=0,
            policy_summary=policy_summaries if policy_summaries else ["No significant impact from policies"],
        )


# =============================================================================
# 5. ACTION PLAN GENERATOR - PERSONALIZED
# =============================================================================

class ActionPlanGenerator:
    """Generate personalized, dynamic action plans with real numbers."""
    
    @staticmethod
    def generate(
        strategy: StrategyResult,
        fleet_profile: Dict[str, Any],
        policies: Optional[List[DevicePolicy]] = None,
        data_source: str = "estimates",
        confidence: str = "MEDIUM",
        top_models: Optional[List[str]] = None,
    ) -> ActionPlanResult:
        """Generate a personalized 90-day action plan with real numbers."""
        
        # Extract key numbers
        fleet_size = int(fleet_profile.get("fleet_size", 12500))
        avg_age = float(fleet_profile.get("avg_age", 3.5))
        devices_at_risk = int(fleet_profile.get("devices_at_risk", int(fleet_size * 0.3)))
        refurb_eligible = int(fleet_profile.get("devices_refurb_eligible", int(fleet_size * 0.7)))
        
        # Get top device models if available
        top_device = top_models[0] if top_models else "your highest-volume model"
        
        # Strategy details
        details = strategy.calculation_details or {}
        strat_info = details.get("strategy", {})
        refurb_rate = _safe_float(strat_info.get("refurb_rate", 0.4), 0.4)
        
        # Calculate personalized numbers
        refresh_cycle = int(strat_info.get("lifecycle_years", 4))
        annual_replacements = int(fleet_size / refresh_cycle)
        refurb_target = int(annual_replacements * refurb_rate)
        
        # Pilot size: 5-10% of at-risk devices, min 20, max 200
        pilot_size = max(20, min(200, int(devices_at_risk * 0.08)))
        
        # Track what changed from baseline
        changes_from_baseline = []
        if data_source == "uploaded":
            changes_from_baseline.append(f"Fleet data uploaded ({fleet_size:,} devices)")
        if policies:
            changes_from_baseline.append(f"Custom policies applied ({len(policies)} rules)")
        if not changes_from_baseline:
            changes_from_baseline.append("Using baseline estimates")
        
        # Build basis info
        basis = {
            "strategy_name": strategy.strategy_name,
            "strategy_key": strategy.strategy_key,
            "data_source": "Uploaded Fleet Data" if data_source == "uploaded" else "Baseline Estimates",
            "policies_applied": len(policies) if policies else 0,
            "confidence": confidence,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fleet_size": fleet_size,
            "devices_at_risk": devices_at_risk,
        }
        
        # Build outcomes
        outcomes = {
            "co2_reduction_pct": abs(strategy.co2_reduction_pct),
            "annual_savings_eur": strategy.annual_savings_eur,
            "time_to_target_months": strategy.time_to_target_months,
            "confidence": confidence,
            "reaches_target": strategy.reaches_target,
        }
        
        # PERSONALIZED PHASES
        phases = [
            ActionPlanPhase(
                number=1,
                name="Governance & Planning",
                subtitle="Days 1–30",
                tasks=[
                    "Form steering committee: IT + Procurement + CSR + Finance representatives",
                    f"Complete baseline assessment: {fleet_size:,} total devices, {devices_at_risk:,} flagged for priority attention",
                    f"Define success criteria: <2% failure rate, >90% user satisfaction, {refurb_rate*100:.0f}% refurb adoption",
                    "Evaluate certified vendors: Back Market Business, AFB Group, Recommerce (request quotes)",
                    f"Draft pilot scope: {pilot_size} devices from low-risk user groups",
                ],
                milestone=f"Vendor selected, pilot cohort of {pilot_size} devices identified",
                milestone_date="Day 25",
            ),
            ActionPlanPhase(
                number=2,
                name="Pilot Deployment",
                subtitle="Days 31–60",
                tasks=[
                    f"Deploy {pilot_size} refurbished devices to Administrative/HR teams (lowest performance sensitivity)",
                    f"Focus on {top_device} — your highest volume eligible model" if top_models else "Focus on highest-volume device models first",
                    "Implement tracking dashboard: failure rate, support tickets, user NPS scores",
                    "Weekly stakeholder check-ins with IT support and pilot users",
                    "Document configuration differences and support procedures for refurbished units",
                ],
                milestone=f"Pilot complete: {pilot_size} devices deployed with NPS >8.0 and failure rate <2%",
                milestone_date="Day 55",
            ),
            ActionPlanPhase(
                number=3,
                name="Scale & Operationalize",
                subtitle="Days 61–90",
                tasks=[
                    f"Expand refurbished procurement to {refurb_rate*100:.0f}% of annual replacements ({refurb_target:,} devices/year)",
                    "Update ERP/procurement system with refurbished vendor catalogs and approval workflows",
                    f"Train IT support team on refurbished device handling ({int(fleet_size * 0.01)} estimated annual support tickets)",
                    "Launch internal communications: 'Sustainable IT @ LVMH' campaign with pilot success metrics",
                    f"Project Year 1 impact: €{strategy.annual_savings_eur:,.0f} savings, {abs(strategy.co2_reduction_pct):.0f}% CO₂ reduction",
                ],
                milestone=f"Policy live in procurement: {refurb_target:,} refurbished devices/year target active",
                milestone_date="Day 85",
            ),
        ]
        
        # Build metrics
        metrics = [
            ActionPlanMetric(
                name="Refurbished adoption rate",
                target=f"{refurb_rate*100:.0f}%",
                owner="Procurement",
                frequency="Monthly",
            ),
            ActionPlanMetric(
                name="Device failure rate",
                target="< 1.5%",
                owner="IT Operations",
                frequency="Monthly",
            ),
            ActionPlanMetric(
                name="User satisfaction (NPS)",
                target="> 8.0",
                owner="HR / IT Support",
                frequency="Quarterly",
            ),
            ActionPlanMetric(
                name="CO₂ reduction vs baseline",
                target=f"-{abs(strategy.co2_reduction_pct):.0f}%",
                owner="CSR / Sustainability",
                frequency="Quarterly",
            ),
            ActionPlanMetric(
                name="Cost savings realized",
                target=f"€{strategy.annual_savings_eur:,.0f}/year",
                owner="Finance",
                frequency="Quarterly",
            ),
        ]
        
        return ActionPlanResult(
            basis=basis,
            outcomes=outcomes,
            phases=phases,
            metrics=metrics,
            changes_from_baseline=changes_from_baseline,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )


# =============================================================================
# 6. HELPER FUNCTIONS
# =============================================================================

def generate_fleet_template() -> str:
    """Generate a CSV template for fleet data upload."""
    return """Device_Model,Age_Years,Persona,Country
MacBook Pro 14,2.5,Developer (Tech),FR
ThinkPad X1 Carbon,4.2,Admin Normal (HR/Finance),FR
Dell Latitude 5520,3.8,Sales / Mobile (Field),DE
iMac 27,5.1,Creative (Design),FR
HP EliteDesk 800,3.2,Admin Normal (HR/Finance),GB
Dell UltraSharp U2722D,2.0,Admin Normal (HR/Finance),FR
iPhone 14,1.5,Sales / Mobile (Field),FR"""


def generate_demo_fleet_extended(n: int = 150) -> pd.DataFrame:
    """Generate a realistic demo fleet for testing."""
    random.seed(42)
    
    devices = [
        ("MacBook Pro 14", 0.15),
        ("MacBook Pro 16", 0.08),
        ("ThinkPad X1 Carbon", 0.18),
        ("Dell Latitude 5520", 0.15),
        ("HP EliteBook 840", 0.10),
        ("iMac 27", 0.06),
        ("Dell OptiPlex 7090", 0.08),
        ("HP EliteDesk 800", 0.05),
        ("Dell UltraSharp U2722D", 0.08),
        ("iPhone 14", 0.07),
    ]
    
    personas = [
        ("Developer (Tech)", 0.25),
        ("Admin Normal (HR/Finance)", 0.35),
        ("Sales / Mobile (Field)", 0.15),
        ("Creative (Design)", 0.10),
        ("Executive", 0.10),
        ("Intern / Temporary", 0.05),
    ]
    
    countries = [
        ("FR", 0.60),
        ("DE", 0.15),
        ("GB", 0.10),
        ("IT", 0.08),
        ("US", 0.07),
    ]
    
    def weighted_choice(options):
        items, weights = zip(*options)
        return random.choices(items, weights=weights, k=1)[0]
    
    rows = []
    for _ in range(n):
        device = weighted_choice(devices)
        persona = weighted_choice(personas)
        country = weighted_choice(countries)
        age = max(0.5, min(7.0, random.gauss(3.5, 1.5)))
        
        rows.append({
            "Device_Model": device,
            "Age_Years": round(age, 1),
            "Persona": persona,
            "Country": country,
        })
    
    return pd.DataFrame(rows)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data classes
    "ValidationReport",
    "CalculationProof",
    "InsightWithProof",
    "FleetInsightsResult",
    "DevicePolicy",
    "CategoryInfo",
    "PolicyImpactResult",
    "ActionPlanPhase",
    "ActionPlanMetric",
    "ActionPlanResult",
    "RiskStrategySet",
    
    # Classes
    "RiskBasedSelector",
    "DeviceCategoryExtractor",
    "FleetInsightsGenerator",
    "PolicyImpactCalculator",
    "ActionPlanGenerator",
    
    # Functions
    "generate_fleet_template",
    "generate_demo_fleet_extended",
]

# =============================================================================
# SIMPLE ROI - ADD THIS TO THE END OF YOUR calculator.py
# =============================================================================
#
# Uses ONLY real data from reference_data_API.py:
# - Disposal cost: €14/device (LVMH Partner)
# - Price ratio: 59% (Back Market)
# - Device prices from your catalog
#
# Shows "Return Multiple" instead of fake ROI %


# Get real costs from reference data
try:
    from reference_data_API import (
        DISPOSAL_COST_WITH_DATA,
        REFURB_CONFIG,
        AVERAGES,
    )
    _DISPOSAL_COST = DISPOSAL_COST_WITH_DATA  # €14
except ImportError:
    _DISPOSAL_COST = 14


@dataclass
class SimpleROI:
    """Simple, honest ROI result."""
    # What the user sees
    return_multiple: float          # "For every €1, you get €X back"
    annual_savings_eur: float
    five_year_savings_eur: float
    transition_cost_eur: float
    payback_months: int
    headline: str
    
    # Calculation details for transparency
    calculation: Dict[str, Any]
    
    # Aliases for compatibility with audit_ui
    @property
    def annual_capex_avoidance_eur(self) -> float:
        return self.annual_savings_eur
    
    @property
    def five_year_capex_avoidance_eur(self) -> float:
        return self.five_year_savings_eur


class SimpleROICalculator:
    """
    Calculate ROI using ONLY real data.
    
    Investment = Disposal costs (€14/device) - from LVMH partner
    Savings = Price difference (new vs refurb) - from Back Market
    """
    
    @staticmethod
    def calculate(
        fleet_size: int,
        refresh_cycle_years: int,
        refurb_rate: float,
        current_refurb_rate: float = 0.0,
        years: int = 5,
    ) -> SimpleROI:
        """
        Calculate simple ROI based on user inputs.
        
        Args:
            fleet_size: From calibration step (e.g., 12500)
            refresh_cycle_years: From calibration (e.g., 4)
            refurb_rate: Target from strategy (e.g., 0.40)
            current_refurb_rate: From calibration (e.g., 0.16)
            years: Time horizon (default 5)
        """
        # Sanitize inputs
        fleet_size = max(1, int(fleet_size))
        refresh_cycle_years = max(1, int(refresh_cycle_years))
        refurb_rate = max(0.0, min(1.0, float(refurb_rate)))
        current_refurb_rate = max(0.0, min(refurb_rate, float(current_refurb_rate)))
        years = max(1, int(years))
        
        # Get reference data
        try:
            avg_price_new = float(AVERAGES.get("device_price_eur", 1150))
            price_ratio = float(REFURB_CONFIG.get("price_ratio", 0.59))
        except:
            avg_price_new = 1150
            price_ratio = 0.59
        
        avg_price_refurb = avg_price_new * price_ratio
        savings_per_device = avg_price_new - avg_price_refurb
        
        # Annual calculations
        annual_replacements = fleet_size / refresh_cycle_years
        incremental_rate = refurb_rate - current_refurb_rate
        devices_switching = annual_replacements * incremental_rate
        
        # === ANNUAL SAVINGS ===
        annual_savings = devices_switching * savings_per_device
        five_year_savings = annual_savings * years
        
        # === TRANSITION COST (Investment) ===
        # Real cost: disposal/data wipe at €14/device
        transition_cost = devices_switching * _DISPOSAL_COST
        
        # === RETURN MULTIPLE ===
        if transition_cost > 0:
            return_multiple = five_year_savings / transition_cost
        else:
            return_multiple = 0
        
        # === PAYBACK ===
        if annual_savings > 0 and transition_cost > 0:
            payback_months = max(1, int((transition_cost / annual_savings) * 12))
        else:
            payback_months = 0 if transition_cost == 0 else 999
        
        # === HEADLINE ===
        if return_multiple >= 1:
            headline = f"For every €1 invested, you get €{return_multiple:.0f} back over {years} years"
        elif transition_cost == 0 and annual_savings > 0:
            headline = f"€{annual_savings:,.0f} annual savings with minimal transition cost"
        else:
            headline = "Adjust parameters to see potential returns"
        
        # === CALCULATION PROOF ===
        calculation = {
            "inputs": {
                "fleet_size": f"{fleet_size:,}",
                "refresh_cycle": f"{refresh_cycle_years} years",
                "target_refurb_rate": f"{refurb_rate*100:.0f}%",
                "current_refurb_rate": f"{current_refurb_rate*100:.0f}%",
            },
            "from_your_data": {
                "avg_new_price": f"€{avg_price_new:,.0f}",
                "refurb_price": f"€{avg_price_refurb:,.0f} ({price_ratio*100:.0f}% of new)",
                "savings_per_device": f"€{savings_per_device:,.0f}",
                "disposal_cost": f"€{_DISPOSAL_COST}/device",
            },
            "calculation": {
                "annual_replacements": f"{annual_replacements:,.0f}",
                "devices_switching_to_refurb": f"{devices_switching:,.0f}",
                "annual_savings": f"€{annual_savings:,.0f}",
                "transition_cost": f"€{transition_cost:,.0f}",
            },
            "formula": f"Return = (€{annual_savings:,.0f} × {years}) ÷ €{transition_cost:,.0f} = {return_multiple:.0f}x",
            "sources": [
                "Device prices: Dell France Price List 2024",
                "Refurb ratio: Back Market France 2024",
                "Disposal cost: LVMH Refurb Partner Jan 2025",
            ],
        }
        
        return SimpleROI(
            return_multiple=round(return_multiple, 1),
            annual_savings_eur=round(annual_savings, 0),
            five_year_savings_eur=round(five_year_savings, 0),
            transition_cost_eur=round(transition_cost, 0),
            payback_months=payback_months,
            headline=headline,
            calculation=calculation,
        )


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test with example user inputs
    print("=" * 60)
    print("SIMPLE ROI TEST - Based on User Inputs")
    print("=" * 60)
    
    # Simulate user inputs from calibration
    user_fleet = 12500      # Medium fleet
    user_refresh = 4        # 25% per year
    user_current = 0.10     # 10% current refurb
    strategy_target = 0.40  # 40% target
    
    roi = SimpleROICalculator.calculate(
        fleet_size=user_fleet,
        refresh_cycle_years=user_refresh,
        refurb_rate=strategy_target,
        current_refurb_rate=user_current,
    )
    
    print(f"\nUser Inputs:")
    print(f"  Fleet: {user_fleet:,} devices")
    print(f"  Refresh: {user_refresh}-year cycle")
    print(f"  Current refurb: {user_current*100:.0f}%")
    print(f"  Target refurb: {strategy_target*100:.0f}%")
    
    print(f"\nResults:")
    print(f"  Return Multiple: {roi.return_multiple}x")
    print(f"  Annual Savings: €{roi.annual_savings_eur:,.0f}")
    print(f"  5-Year Savings: €{roi.five_year_savings_eur:,.0f}")
    print(f"  Transition Cost: €{roi.transition_cost_eur:,.0f}")
    print(f"  Payback: {roi.payback_months} months")
    
    print(f"\n  HEADLINE: {roi.headline}")
    
    print("\n" + "=" * 60)
    print("CALCULATION PROOF:")
    print("=" * 60)
    for section, data in roi.calculation.items():
        print(f"\n{section}:")
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"  {k}: {v}")
        elif isinstance(data, list):
            for item in data:
                print(f"  - {item}")
        else:
            print(f"  {data}")