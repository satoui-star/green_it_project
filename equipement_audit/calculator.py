"""
Élysia - Calculator Module
===========================
LVMH · Sustainable IT Intelligence

All calculation logic with documented mathematical formulas.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging
import pandas as pd
from datetime import datetime
from difflib import get_close_matches

logger = logging.getLogger(__name__)

try:
    from reference_data_API import (
        DEVICES, PERSONAS, PRICE_KWH_EUR, PRODUCTIVITY_CONFIG, REFURB_CONFIG,
        URGENCY_CONFIG, URGENCY_THRESHOLDS, STRATEGIES, AVERAGES,
        get_grid_factor, get_depreciation_rate, is_premium_device,
        PREMIUM_RETENTION_BONUS, get_disposal_cost, calculate_stranded_value,
        calculate_avoidable_co2, GRID_CARBON_FACTORS
    )
except ImportError as e:
    logger.error(f"Failed to import reference data: {e}")
    raise


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ShockMetrics:
    """Metrics for Act 1: The Shock."""
    stranded_value_eur: float
    avoidable_co2_tonnes: float
    deadline_status: str
    stranded_calculation: Dict = field(default_factory=dict)
    co2_calculation: Dict = field(default_factory=dict)


@dataclass
class HopeMetrics:
    """Metrics for Act 2: The Hope."""
    current_co2_tonnes: float
    target_co2_tonnes: float
    current_cost_eur: float
    target_cost_eur: float
    co2_reduction_pct: float
    cost_reduction_pct: float
    cost_savings_eur: float
    deadline_achievable: bool
    months_to_target: int


@dataclass
class StrategyResult:
    """Result of a strategy simulation."""
    strategy_key: str
    strategy_name: str
    description: str
    co2_savings_tonnes: float
    co2_reduction_pct: float
    cost_savings_eur: float
    time_to_target_months: float
    reaches_target: bool
    implementation_cost_eur: float
    annual_savings_eur: float
    payback_months: float
    roi_3year: float
    monthly_co2: List[float] = field(default_factory=list)
    calculation_details: Dict = field(default_factory=dict)


@dataclass
class DeviceRecommendation:
    """Recommendation for a single device."""
    device_name: str
    age_years: float
    persona: str
    country: str
    device_id: Optional[str] = None
    fleet_position: int = 0
    recommendation: str = "KEEP"
    urgency: str = "LOW"
    urgency_score: float = 1.0
    tco_keep: float = 0.0
    tco_new: float = 0.0
    tco_refurb: Optional[float] = None
    annual_savings: float = 0.0
    co2_keep: float = 0.0
    co2_new: float = 0.0
    co2_refurb: Optional[float] = None
    co2_savings: float = 0.0
    residual_value: float = 0.0
    productivity_loss_pct: float = 0.0
    rationale: str = ""
    peer_analysis: Dict = field(default_factory=dict)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def _find_closest_device(name: str, valid_devices: set) -> str:
    """Find closest matching device."""
    matches = get_close_matches(name, list(valid_devices), n=1, cutoff=0.6)
    return matches[0] if matches else list(valid_devices)[0]


def validate_fleet_data(df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame]:
    """
    Validate fleet CSV data.
    
    Returns:
        (is_valid, error_messages, cleaned_dataframe)
    """
    errors = []
    cleaned_df = df.copy()
    
    required = ["Device_Model", "Age_Years"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return False, errors, cleaned_df
    
    if "Persona" not in cleaned_df.columns:
        cleaned_df["Persona"] = "Admin Normal (HR/Finance)"
    if "Country" not in cleaned_df.columns:
        cleaned_df["Country"] = "FR"
    if "Device_ID" not in cleaned_df.columns:
        cleaned_df["Device_ID"] = [f"DEV-{i:05d}" for i in range(len(cleaned_df))]
    
    valid_devices = set(DEVICES.keys())
    valid_personas = set(PERSONAS.keys())
    valid_countries = set(GRID_CARBON_FACTORS.keys())
    
    rows_to_drop = []
    
    for idx, row in cleaned_df.iterrows():
        row_errors = []
        
        if pd.isna(row["Device_Model"]) or str(row["Device_Model"]).strip() == "":
            row_errors.append("Device_Model is empty")
        elif row["Device_Model"] not in valid_devices:
            closest = _find_closest_device(row["Device_Model"], valid_devices)
            row_errors.append(f"Unknown device '{row['Device_Model']}'. Did you mean '{closest}'?")
        
        try:
            age = float(row["Age_Years"])
            if age < 0.5:
                row_errors.append(f"Age {age} is too low (minimum: 0.5 years)")
            elif age > 10:
                row_errors.append(f"Age {age} is too high (maximum: 10 years)")
            cleaned_df.at[idx, "Age_Years"] = age
        except (ValueError, TypeError):
            row_errors.append(f"Age_Years '{row['Age_Years']}' is not numeric")
        
        if pd.isna(row["Persona"]) or str(row["Persona"]).strip() == "":
            cleaned_df.at[idx, "Persona"] = "Admin Normal (HR/Finance)"
        elif row["Persona"] not in valid_personas:
            cleaned_df.at[idx, "Persona"] = "Admin Normal (HR/Finance)"
            row_errors.append(f"Unknown persona '{row['Persona']}'. Using default.")
        
        if pd.isna(row["Country"]) or str(row["Country"]).strip() == "":
            cleaned_df.at[idx, "Country"] = "FR"
        elif row["Country"] not in valid_countries:
            cleaned_df.at[idx, "Country"] = "FR"
            row_errors.append(f"Unknown country '{row['Country']}'. Using FR default.")
        
        if row_errors:
            for err in row_errors:
                errors.append(f"Row {idx + 2}: {err}")
            rows_to_drop.append(idx)
    
    if rows_to_drop:
        cleaned_df = cleaned_df.drop(rows_to_drop).reset_index(drop=True)
        if len(cleaned_df) == 0:
            errors.insert(0, "No valid rows after validation")
            return False, errors, cleaned_df
    
    logger.info(f"Fleet validation: {len(df)} rows → {len(cleaned_df)} valid, {len(errors)} errors")
    return len(errors) == 0, errors, cleaned_df


def validate_device_inputs(device_name: str, age_years: float, 
                          persona: str, country: str) -> Tuple[bool, List[str]]:
    """
    Validate device simulator inputs.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    if device_name not in DEVICES:
        errors.append(f"Device '{device_name}' not found")
    
    if not isinstance(age_years, (int, float)):
        errors.append("Age must be numeric")
    else:
        if age_years < 0.5:
            errors.append("Device must be at least 0.5 years old")
        elif age_years > 10:
            errors.append("Device age cannot exceed 10 years")
    
    if persona not in PERSONAS:
        errors.append(f"Persona '{persona}' not found")
    
    if country not in GRID_CARBON_FACTORS:
        errors.append(f"Country '{country}' not supported")
    
    return len(errors) == 0, errors


def generate_synthetic_fleet(n_devices: int = 100, avg_age: float = 3.5,
                            seed: int = 42) -> List[Dict]:
    """Generate synthetic fleet for demo."""
    import random
    random.seed(seed)
    
    device_choices = list(DEVICES.keys())
    persona_choices = list(PERSONAS.keys())
    country_choices = list(GRID_CARBON_FACTORS.keys())
    
    if not device_choices or not persona_choices or not country_choices:
        raise ValueError("Missing required reference data")
    
    fleet = []
    for i in range(n_devices):
        device = random.choice(device_choices)
        age = max(0.5, min(7.0, random.gauss(avg_age, 1.5)))
        persona = random.choice(persona_choices)
        country = random.choice(country_choices)
        
        fleet.append({
            "Device_ID": f"SYN-{i:05d}",
            "Device_Model": device,
            "Age_Years": round(age, 1),
            "Persona": persona,
            "Country": country,
        })
    
    logger.info(f"Generated synthetic fleet: {n_devices} devices")
    return fleet


def generate_demo_fleet(n_devices: int = 100, seed: int = 42) -> List[Dict]:
    """Generate demo fleet."""
    return generate_synthetic_fleet(n_devices, avg_age=3.5, seed=seed)


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_recommendations_to_csv(recommendations: List[DeviceRecommendation]) -> str:
    """Convert recommendations to CSV."""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Device_ID", "Device_Model", "Age_Years", "Persona", "Country",
        "Recommendation", "Urgency", "Urgency_Score",
        "TCO_Keep_EUR", "TCO_New_EUR", "TCO_Refurb_EUR",
        "Annual_Savings_EUR", "CO2_Savings_kg", "Residual_Value_EUR",
        "Rationale"
    ])
    
    for rec in recommendations:
        writer.writerow([
            rec.device_id or "—",
            rec.device_name,
            round(rec.age_years, 1),
            rec.persona,
            rec.country,
            rec.recommendation,
            rec.urgency,
            round(rec.urgency_score, 2),
            round(rec.tco_keep, 2),
            round(rec.tco_new, 2),
            round(rec.tco_refurb, 2) if rec.tco_refurb else "—",
            round(rec.annual_savings, 2),
            round(rec.co2_savings, 2),
            round(rec.residual_value, 2),
            rec.rationale
        ])
    
    return output.getvalue()


def generate_markdown_report(best_strategy: StrategyResult, fleet_size: int, 
                            summary: Dict, recommendations: List[DeviceRecommendation]) -> str:
    """Generate markdown report."""
    md = f"""# Élysia Strategy Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
**Recommended Strategy:** {best_strategy.strategy_name}

{best_strategy.description}

### Key Metrics
- **CO₂ Reduction:** {best_strategy.co2_reduction_pct}%
- **Annual Savings:** €{best_strategy.annual_savings_eur:,.0f}
- **Implementation Cost:** €{best_strategy.implementation_cost_eur:,.0f}
- **3-Year ROI:** {best_strategy.roi_3year:.2f}x
- **Payback Period:** {best_strategy.payback_months:.0f} months
- **Time to Target:** {best_strategy.time_to_target_months} months

## Fleet Overview
- **Total Devices:** {fleet_size:,}
- **HIGH Urgency:** {summary.get('by_urgency', {}).get('HIGH', 0)}
- **MEDIUM Urgency:** {summary.get('by_urgency', {}).get('MEDIUM', 0)}
- **LOW Urgency:** {summary.get('by_urgency', {}).get('LOW', 0)}

## Breakdown by Recommendation
- **KEEP:** {summary.get('by_recommendation', {}).get('KEEP', 0)} devices
- **NEW:** {summary.get('by_recommendation', {}).get('NEW', 0)} devices
- **REFURBISHED:** {summary.get('by_recommendation', {}).get('REFURBISHED', 0)} devices

## Financial Impact
- **Total Annual Savings:** €{summary.get('total_annual_savings_eur', 0):,.0f}
- **CO₂ Savings:** {summary.get('total_co2_savings_kg', 0)/1000:.1f}t
- **Recoverable Value:** €{summary.get('total_recoverable_value_eur', 0):,.0f}

## Top 10 Priority Devices
"""
    
    for i, rec in enumerate(recommendations[:10], 1):
        md += f"""
### {i}. {rec.device_name}
- **Device ID:** {rec.device_id or "—"}
- **Age:** {rec.age_years} years
- **Persona:** {rec.persona}
- **Recommendation:** {rec.recommendation}
- **Urgency:** {rec.urgency}
- **Annual Savings:** €{rec.annual_savings:,.0f}
- **CO₂ Savings:** {rec.co2_savings:.0f}kg
- **Rationale:** {rec.rationale}
"""
    
    return md


# =============================================================================
# SHOCK CALCULATOR
# =============================================================================

class ShockCalculator:
    """Calculates cost of inaction."""
    
    @staticmethod
    def calculate(fleet_size: int, avg_age: float = 3.5, 
                  refresh_cycle: int = 4, target_pct: float = -20) -> ShockMetrics:
        """Calculate shock metrics."""
        try:
            stranded = calculate_stranded_value(fleet_size, avg_age)
            stranded_value = stranded.get("value", 0)
            
            avoidable = calculate_avoidable_co2(fleet_size, refresh_cycle, refurb_rate=0.40)
            avoidable_co2 = avoidable.get("value_tonnes", 0)
            
            deadline_status = "WILL MISS" if target_pct < 0 else "ON TRACK"
            
            logger.info(f"Shock: ${stranded_value}, CO2={avoidable_co2}t")
            
            return ShockMetrics(
                stranded_value_eur=round(stranded_value, 2),
                avoidable_co2_tonnes=round(avoidable_co2, 1),
                deadline_status=deadline_status,
                stranded_calculation=stranded.get("calculation", {}),
                co2_calculation=avoidable.get("calculation", {})
            )
        except Exception as e:
            logger.error(f"ShockCalculator error: {e}")
            return ShockMetrics(0, 0, "ERROR", {}, {})


# =============================================================================
# HOPE CALCULATOR
# =============================================================================

class HopeCalculator:
    """Calculates what's possible."""
    
    @staticmethod
    def calculate(fleet_size: int, avg_age: float = 3.5,
                  refresh_cycle: int = 4, target_pct: float = -20,
                  strategy_key: str = "refurb_40") -> HopeMetrics:
        """Calculate before/after comparison."""
        try:
            strategy = STRATEGIES.get(strategy_key, STRATEGIES.get("refurb_40"))
            
            annual_replacements = fleet_size / refresh_cycle
            manufacturing_co2 = annual_replacements * AVERAGES.get("device_co2_manufacturing_kg", 100)
            usage_co2 = fleet_size * AVERAGES.get("device_co2_annual_kg", 50)
            current_co2_kg = manufacturing_co2 + usage_co2
            current_co2_tonnes = current_co2_kg / 1000
            
            current_equipment_cost = annual_replacements * AVERAGES.get("device_price_eur", 800)
            backlog_pct = max(0, (avg_age - 3) * 0.10)
            backlog_devices = fleet_size * backlog_pct
            productivity_loss = backlog_devices * 0.03 * AVERAGES.get("salary_eur", 50000)
            current_cost = current_equipment_cost + productivity_loss
            
            new_lifecycle = strategy.get("lifecycle_years", 5)
            refurb_rate = strategy.get("refurb_rate", 0.4)
            new_annual_replacements = fleet_size / new_lifecycle
            new_devices = new_annual_replacements * (1 - refurb_rate)
            refurb_devices = new_annual_replacements * refurb_rate
            
            new_manufacturing_co2 = new_devices * AVERAGES.get("device_co2_manufacturing_kg", 100)
            refurb_manufacturing_co2 = refurb_devices * AVERAGES.get("device_co2_manufacturing_kg", 100) * (1 - REFURB_CONFIG.get("co2_savings_rate", 0.80))
            optimized_co2_kg = new_manufacturing_co2 + refurb_manufacturing_co2 + usage_co2
            optimized_co2_tonnes = optimized_co2_kg / 1000
            
            new_cost = new_devices * AVERAGES.get("device_price_eur", 800)
            refurb_cost = refurb_devices * AVERAGES.get("device_price_eur", 800) * REFURB_CONFIG.get("price_ratio", 0.65)
            reduced_productivity_loss = productivity_loss * 0.5
            optimized_cost = new_cost + refurb_cost + reduced_productivity_loss
            
            co2_reduction_pct = ((current_co2_tonnes - optimized_co2_tonnes) / current_co2_tonnes * 100) if current_co2_tonnes > 0 else 0
            cost_savings = current_cost - optimized_cost
            cost_reduction_pct = (cost_savings / current_cost * 100) if current_cost > 0 else 0
            
            target_co2 = current_co2_tonnes * (1 + target_pct / 100)
            co2_gap = current_co2_tonnes - target_co2
            annual_co2_savings = current_co2_tonnes - optimized_co2_tonnes
            
            if annual_co2_savings > 0:
                months_to_target = int(co2_gap / (annual_co2_savings / 12))
                reaches_target = months_to_target <= 36
            else:
                months_to_target = 999
                reaches_target = False
            
            logger.info(f"Hope: CO2 {co2_reduction_pct:.1f}%, savings €{cost_savings:,.0f}")
            
            return HopeMetrics(
                current_co2_tonnes=round(current_co2_tonnes, 1),
                target_co2_tonnes=round(target_co2, 1),
                current_cost_eur=round(current_cost, 0),
                target_cost_eur=round(optimized_cost, 0),
                co2_reduction_pct=round(co2_reduction_pct, 1),
                cost_reduction_pct=round(cost_reduction_pct, 1),
                cost_savings_eur=round(cost_savings, 0),
                deadline_achievable=reaches_target,
                months_to_target=months_to_target
            )
        except Exception as e:
            logger.error(f"HopeCalculator error: {e}")
            return HopeMetrics(0, 0, 0, 0, 0, 0, 0, False, 999)


# =============================================================================
# STRATEGY SIMULATOR
# =============================================================================

class StrategySimulator:
    """Simulates different strategies."""
    
    @staticmethod
    def simulate_strategy(strategy_key: str, fleet_size: int,
                          current_refresh: int = 4, avg_age: float = 3.5,
                          target_pct: float = -20,
                          time_horizon_months: int = 36) -> StrategyResult:
        """Simulate a single strategy."""
        try:
            strategy = STRATEGIES.get(strategy_key)
            if not strategy:
                raise ValueError(f"Unknown strategy: {strategy_key}")
            
            annual_replacements_current = fleet_size / current_refresh
            current_manufacturing_co2 = annual_replacements_current * AVERAGES.get("device_co2_manufacturing_kg", 100)
            current_usage_co2 = fleet_size * AVERAGES.get("device_co2_annual_kg", 50)
            current_annual_co2_kg = current_manufacturing_co2 + current_usage_co2
            current_annual_co2_tonnes = current_annual_co2_kg / 1000
            
            current_annual_cost = annual_replacements_current * AVERAGES.get("device_price_eur", 800)
            
            new_lifecycle = strategy.get("lifecycle_years", 5)
            refurb_rate = strategy.get("refurb_rate", 0.4)
            
            annual_replacements_new = fleet_size / new_lifecycle
            new_devices = annual_replacements_new * (1 - refurb_rate)
            refurb_devices = annual_replacements_new * refurb_rate
            
            new_manufacturing_co2 = new_devices * AVERAGES.get("device_co2_manufacturing_kg", 100)
            refurb_manufacturing_co2 = refurb_devices * AVERAGES.get("device_co2_manufacturing_kg", 100) * 0.20
            new_annual_co2_kg = new_manufacturing_co2 + refurb_manufacturing_co2 + current_usage_co2
            new_annual_co2_tonnes = new_annual_co2_kg / 1000
            
            new_cost = new_devices * AVERAGES.get("device_price_eur", 800)
            refurb_cost = refurb_devices * AVERAGES.get("device_price_eur", 800) * REFURB_CONFIG.get("price_ratio", 0.65)
            new_annual_cost = new_cost + refurb_cost
            
            co2_savings_tonnes = current_annual_co2_tonnes - new_annual_co2_tonnes
            co2_reduction_pct = (co2_savings_tonnes / current_annual_co2_tonnes * 100) if current_annual_co2_tonnes > 0 else 0
            cost_savings = current_annual_cost - new_annual_cost
            
            target_co2 = current_annual_co2_tonnes * (1 + target_pct / 100)
            co2_gap = current_annual_co2_tonnes - target_co2
            
            monthly_co2 = []
            current_co2 = current_annual_co2_tonnes
            months_to_target = None
            implementation_months = strategy.get("implementation_months", 6)
            
            for month in range(time_horizon_months + 1):
                monthly_co2.append(round(current_co2, 2))
                
                if current_co2 <= target_co2 and months_to_target is None:
                    months_to_target = month
                
                if month < implementation_months:
                    ramp_factor = month / implementation_months
                else:
                    ramp_factor = 1.0
                
                monthly_reduction = (co2_savings_tonnes / 12) * ramp_factor
                current_co2 = max(new_annual_co2_tonnes, current_co2 - monthly_reduction)
            
            reaches_target = months_to_target is not None
            if not reaches_target:
                months_to_target = 999
            
            implementation_cost = fleet_size * 10 * (refurb_rate + 0.02)
            annual_savings = cost_savings
            
            if annual_savings > 0 and implementation_cost > 0:
                payback_months = (implementation_cost / annual_savings) * 12
                roi_3year = ((annual_savings * 3) - implementation_cost) / implementation_cost if implementation_cost > 0 else 0
            else:
                payback_months = 999
                roi_3year = 0
            
            logger.info(f"Strategy {strategy_key}: CO2 {co2_reduction_pct:.1f}%, ROI {roi_3year:.2f}x")
            
            return StrategyResult(
                strategy_key=strategy_key,
                strategy_name=strategy.get("name", "Unknown"),
                description=strategy.get("description", ""),
                co2_savings_tonnes=round(co2_savings_tonnes, 1),
                co2_reduction_pct=round(co2_reduction_pct, 1),
                cost_savings_eur=round(cost_savings, 0),
                time_to_target_months=months_to_target if months_to_target < 999 else 999,
                reaches_target=reaches_target,
                implementation_cost_eur=round(implementation_cost, 0),
                annual_savings_eur=round(annual_savings, 0),
                payback_months=round(payback_months, 1) if payback_months < 999 else 999,
                roi_3year=round(roi_3year, 2),
                monthly_co2=monthly_co2,
                calculation_details={
                    "fleet_size": fleet_size,
                    "current_refresh": current_refresh,
                    "new_lifecycle": new_lifecycle,
                    "refurb_rate": refurb_rate,
                    "current_annual_co2": round(current_annual_co2_tonnes, 1),
                    "new_annual_co2": round(new_annual_co2_tonnes, 1),
                }
            )
        except Exception as e:
            logger.error(f"StrategySimulator error: {e}")
            raise
    
    @staticmethod
    def compare_all_strategies(fleet_size: int, current_refresh: int = 4,
                               avg_age: float = 3.5, target_pct: float = -20,
                               time_horizon_months: int = 36) -> List[StrategyResult]:
        """Compare all strategies."""
        results = []
        
        for strategy_key in STRATEGIES:
            try:
                result = StrategySimulator.simulate_strategy(
                    strategy_key=strategy_key,
                    fleet_size=fleet_size,
                    current_refresh=current_refresh,
                    avg_age=avg_age,
                    target_pct=target_pct,
                    time_horizon_months=time_horizon_months
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to simulate {strategy_key}: {e}")
                continue
        
        results.sort(key=lambda x: (not x.reaches_target, x.time_to_target_months, -x.roi_3year))
        return results
    
    @staticmethod
    def get_recommended_strategy(fleet_size: int, current_refresh: int = 4,
                                 avg_age: float = 3.5, target_pct: float = -20,
                                 priority: str = "balanced") -> StrategyResult:
        """Get best strategy."""
        results = StrategySimulator.compare_all_strategies(
            fleet_size, current_refresh, avg_age, target_pct
        )
        
        viable = [r for r in results if r.strategy_key != "do_nothing"]
        
        if not viable:
            return results[0] if results else None
        
        if priority == "cost":
            return max(viable, key=lambda x: x.cost_savings_eur)
        elif priority == "co2":
            return max(viable, key=lambda x: x.co2_reduction_pct)
        elif priority == "speed":
            viable_reaching = [r for r in viable if r.reaches_target]
            if viable_reaching:
                return min(viable_reaching, key=lambda x: x.time_to_target_months)
            return viable[0]
        else:
            reaching = [r for r in viable if r.reaches_target]
            if reaching:
                return max(reaching, key=lambda x: x.roi_3year)
            return max(viable, key=lambda x: x.roi_3year)


# =============================================================================
# TCO CALCULATOR
# =============================================================================

class TCOCalculator:
    """Total Cost of Ownership."""
    
    @staticmethod
    def calculate_energy_cost(device_name: str, persona: str, country: str) -> float:
        """Calculate annual energy cost."""
        device = DEVICES.get(device_name)
        persona_data = PERSONAS.get(persona)
        if not device or not persona_data:
            return 0.0
        
        daily_hours = persona_data.get("daily_hours", 8)
        annual_hours = daily_hours * AVERAGES.get("working_days_per_year", 250)
        power_kw = device.get("power_kw", 0.1)
        
        return round(power_kw * annual_hours * PRICE_KWH_EUR, 2)
    
    @staticmethod
    def calculate_productivity_loss(device_name: str, age_years: float, 
                                    persona: str) -> Tuple[float, float]:
        """Calculate productivity loss."""
        persona_data = PERSONAS.get(persona)
        if not persona_data:
            return 0.0, 0.0
        
        optimal = PRODUCTIVITY_CONFIG.get("optimal_years", 3)
        degradation = PRODUCTIVITY_CONFIG.get("degradation_per_year", 0.05)
        max_deg = PRODUCTIVITY_CONFIG.get("max_degradation", 0.25)
        
        if age_years <= optimal:
            loss_pct = 0.0
        else:
            loss_pct = min((age_years - optimal) * degradation, max_deg)
        
        salary = persona_data.get("salary_eur", 50000)
        sensitivity = persona_data.get("lag_sensitivity", 1.0)
        loss_cost = salary * loss_pct * sensitivity
        
        return round(loss_pct, 4), round(loss_cost, 2)
    
    @staticmethod
    def calculate_residual_value(device_name: str, age_years: float) -> float:
        """Calculate residual value."""
        device = DEVICES.get(device_name)
        if not device:
            return 0.0
        
        price_new = device.get("price_new_eur", 800)
        remaining_pct = get_depreciation_rate(age_years)
        
        if is_premium_device(device_name):
            remaining_pct = min(remaining_pct * (1 + PREMIUM_RETENTION_BONUS), 1.0)
        
        return round(price_new * remaining_pct, 2)
    
    @staticmethod
    def calculate_tco_keep(device_name: str, age_years: float, 
                          persona: str, country: str) -> Dict:
        """Calculate TCO for keeping."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}, "productivity_loss_pct": 0}
        
        energy_cost = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(
            device_name, age_years, persona
        )
        
        current_residual = TCOCalculator.calculate_residual_value(device_name, age_years)
        future_residual = TCOCalculator.calculate_residual_value(device_name, age_years + 1)
        residual_loss = current_residual - future_residual
        
        total = energy_cost + productivity_cost + residual_loss
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "energy": energy_cost,
                "productivity_loss": productivity_cost,
                "residual_loss": round(residual_loss, 2),
            },
            "productivity_loss_pct": loss_pct,
        }
    
    @staticmethod
    def calculate_tco_new(device_name: str, persona: str, country: str) -> Dict:
        """Calculate TCO for new."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        lifespan_years = device.get("lifespan_months", 48) / 12
        annual_purchase = device.get("price_new_eur", 800) / lifespan_years
        energy_cost = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        disposal_cost = get_disposal_cost(device_name) / lifespan_years
        
        residual_y1 = TCOCalculator.calculate_residual_value(device_name, 1)
        residual_benefit = residual_y1 / lifespan_years
        
        total = annual_purchase + energy_cost + disposal_cost - residual_benefit
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "purchase": round(annual_purchase, 2),
                "energy": energy_cost,
                "disposal": round(disposal_cost, 2),
                "residual_benefit": round(residual_benefit, 2),
            },
        }
    
    @staticmethod
    def calculate_tco_refurb(device_name: str, persona: str, country: str) -> Dict:
        """Calculate TCO for refurb."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}, "available": False}
        
        if not device.get("refurb_available", False):
            return {"total": float('inf'), "breakdown": {}, "available": False}
        
        price_refurb = device.get("price_new_eur", 800) * REFURB_CONFIG.get("price_ratio", 0.65)
        lifespan_years = REFURB_CONFIG.get("warranty_years", 3)
        annual_purchase = price_refurb / lifespan_years
        
        base_energy = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        energy_cost = base_energy * (1 + REFURB_CONFIG.get("energy_penalty", 0.05))
        
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(
            device_name, REFURB_CONFIG.get("equivalent_age_years", 2), persona
        )
        
        disposal_cost = get_disposal_cost(device_name) / lifespan_years
        residual_benefit = price_refurb * 0.15 / lifespan_years
        
        total = annual_purchase + energy_cost + productivity_cost + disposal_cost - residual_benefit
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "purchase": round(annual_purchase, 2),
                "energy": round(energy_cost, 2),
                "productivity_loss": productivity_cost,
                "disposal": round(disposal_cost, 2),
                "residual_benefit": round(residual_benefit, 2),
            },
            "productivity_loss_pct": loss_pct,
            "available": True,
        }


# =============================================================================
# CO2 CALCULATOR
# =============================================================================

class CO2Calculator:
    """Carbon Footprint."""
    
    @staticmethod
    def calculate_usage_co2(device_name: str, persona: str, country: str) -> float:
        """Calculate usage CO2."""
        device = DEVICES.get(device_name)
        persona_data = PERSONAS.get(persona)
        if not device or not persona_data:
            return 0.0
        
        daily_hours = persona_data.get("daily_hours", 8)
        annual_hours = daily_hours * AVERAGES.get("working_days_per_year", 250)
        power_kw = device.get("power_kw", 0.1)
        grid_factor = get_grid_factor(country)
        
        return round(power_kw * annual_hours * grid_factor, 2)
    
    @staticmethod
    def calculate_co2_keep(device_name: str, persona: str, country: str) -> Dict:
        """CO2 for keeping."""
        usage_co2 = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        return {
            "total": round(usage_co2, 2),
            "breakdown": {
                "manufacturing": 0,
                "usage": round(usage_co2, 2),
            }
        }
    
    @staticmethod
    def calculate_co2_new(device_name: str, persona: str, country: str) -> Dict:
        """CO2 for new."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        lifespan_years = device.get("lifespan_months", 48) / 12
        manufacturing_annual = device.get("co2_manufacturing_kg", 100) / lifespan_years
        usage_annual = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        
        return {
            "total": round(manufacturing_annual + usage_annual, 2),
            "breakdown": {
                "manufacturing": round(manufacturing_annual, 2),
                "usage": round(usage_annual, 2),
            }
        }
    
    @staticmethod
    def calculate_co2_refurb(device_name: str, persona: str, country: str) -> Dict:
        """CO2 for refurb."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        if not device.get("refurb_available", False):
            return {"total": float('inf'), "breakdown": {}, "available": False}
        
        lifespan_years = REFURB_CONFIG.get("warranty_years", 3)
        
        manufacturing_refurb = device.get("co2_manufacturing_kg", 100) * (1 - REFURB_CONFIG.get("co2_savings_rate", 0.80))
        manufacturing_annual = manufacturing_refurb / lifespan_years
        
        usage_base = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        usage_annual = usage_base * (1 + REFURB_CONFIG.get("energy_penalty", 0.05))
        
        return {
            "total": round(manufacturing_annual + usage_annual, 2),
            "breakdown": {
                "manufacturing": round(manufacturing_annual, 2),
                "usage": round(usage_annual, 2),
            },
            "available": True,
        }


# =============================================================================
# URGENCY CALCULATOR
# =============================================================================

class UrgencyCalculator:
    """Urgency Scoring."""
    
    @staticmethod
    def calculate(device_name: str, age_years: float, 
                  persona: str) -> Tuple[float, str, str]:
        """Calculate urgency score."""
        score = 1.0
        factors = []
        
        age_critical = URGENCY_CONFIG.get("age_critical_years", 6)
        age_high = URGENCY_CONFIG.get("age_high_years", 5)
        
        if age_years >= age_critical:
            score += 1.5
            factors.append(f"Age ({age_years:.1f}y) exceeds critical threshold")
        elif age_years >= age_high:
            score += 0.8
            factors.append(f"Age ({age_years:.1f}y) above recommended")
        
        loss_pct, _ = TCOCalculator.calculate_productivity_loss(device_name, age_years, persona)
        perf_threshold = PRODUCTIVITY_CONFIG.get("max_degradation", 0.25)
        if loss_pct >= perf_threshold:
            score += 0.7
            factors.append(f"Performance degraded to {(1-loss_pct)*100:.0f}%")
        
        persona_data = PERSONAS.get(persona, {})
        sensitivity = persona_data.get("lag_sensitivity", 1.0)
        if sensitivity >= 2.0:
            score += 0.3
            factors.append(f"High-impact role ({persona})")
        
        high_threshold = URGENCY_THRESHOLDS.get("HIGH", 2.5)
        medium_threshold = URGENCY_THRESHOLDS.get("MEDIUM", 1.5)
        
        if score >= high_threshold:
            level = "HIGH"
        elif score >= medium_threshold:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        rationale = " | ".join(factors) if factors else "Device within normal parameters"
        
        return round(score, 2), level, rationale


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

class RecommendationEngine:
    """Generates device recommendations."""
    
    @staticmethod
    def analyze_device(device_name: str, age_years: float, persona: str,
                       country: str, priority: str = "balanced") -> DeviceRecommendation:
        """Analyze single device."""
        
        tco_keep = TCOCalculator.calculate_tco_keep(device_name, age_years, persona, country)
        tco_new = TCOCalculator.calculate_tco_new(device_name, persona, country)
        tco_refurb = TCOCalculator.calculate_tco_refurb(device_name, persona, country)
        
        co2_keep = CO2Calculator.calculate_co2_keep(device_name, persona, country)
        co2_new = CO2Calculator.calculate_co2_new(device_name, persona, country)
        co2_refurb = CO2Calculator.calculate_co2_refurb(device_name, persona, country)
        
        urgency_score, urgency_level, urgency_rationale = UrgencyCalculator.calculate(
            device_name, age_years, persona
        )
        
        residual = TCOCalculator.calculate_residual_value(device_name, age_years)
        
        refurb_available = tco_refurb.get("available", False)
        
        options = {
            "KEEP": {"tco": tco_keep["total"], "co2": co2_keep["total"]},
            "NEW": {"tco": tco_new["total"], "co2": co2_new["total"]},
        }
        if refurb_available:
            options["REFURBISHED"] = {"tco": tco_refurb["total"], "co2": co2_refurb["total"]}
        
        max_tco = max(o["tco"] for o in options.values()) or 1
        max_co2 = max(o["co2"] for o in options.values()) or 1
        
        scores = {}
        for opt, data in options.items():
            if priority == "cost":
                scores[opt] = data["tco"]
            elif priority == "co2":
                scores[opt] = data["co2"]
            else:
                tco_norm = data["tco"] / max_tco if max_tco > 0 else 0
                co2_norm = data["co2"] / max_co2 if max_co2 > 0 else 0
                scores[opt] = (tco_norm + co2_norm) / 2
        
        best = min(scores, key=scores.get)
        
        if urgency_level == "HIGH" and best == "KEEP":
            best = "REFURBISHED" if refurb_available else "NEW"
            rationale = "High urgency: device requires replacement"
        elif best == "KEEP":
            rationale = f"Cost-effective to maintain. Annual TCO: €{tco_keep['total']:.0f}"
        elif best == "REFURBISHED":
            savings = tco_new["total"] - tco_refurb["total"]
            co2_saved = co2_new["total"] - co2_refurb["total"]
            rationale = f"Best value: saves €{savings:.0f}/year and {co2_saved:.1f}kg CO₂"
        else:
            rationale = "New device recommended"
        
        if residual > 50 and best != "KEEP":
            rationale += f". Recoverable: €{residual:.0f}"
        
        tco_refurb_val = tco_refurb["total"] if refurb_available else float('inf')
        best_tco = min(tco_keep["total"], tco_new["total"], tco_refurb_val)
        annual_savings = max(0, tco_keep["total"] - best_tco)
        
        best_co2 = min(co2_keep["total"], co2_new["total"])
        if refurb_available:
            best_co2 = min(best_co2, co2_refurb["total"])
        co2_savings = max(0, co2_keep["total"] - best_co2)
        
        logger.info(f"Device {device_name} age {age_years}y → {best}")
        
        return DeviceRecommendation(
            device_name=device_name,
            age_years=age_years,
            persona=persona,
            country=country,
            recommendation=best,
            urgency=urgency_level,
            urgency_score=urgency_score,
            tco_keep=tco_keep["total"],
            tco_new=tco_new["total"],
            tco_refurb=tco_refurb["total"] if refurb_available else None,
            annual_savings=annual_savings,
            co2_keep=co2_keep["total"],
            co2_new=co2_new["total"],
            co2_refurb=co2_refurb["total"] if refurb_available else None,
            co2_savings=co2_savings,
            residual_value=residual,
            productivity_loss_pct=tco_keep.get("productivity_loss_pct", 0),
            rationale=rationale
        )


# =============================================================================
# FLEET ANALYZER
# =============================================================================

class FleetAnalyzer:
    """Analyzes entire fleets."""
    
    @staticmethod
    def analyze_fleet(fleet_data: List[Dict], 
                      priority: str = "balanced") -> List[DeviceRecommendation]:
        """Analyze all devices."""
        results = []
        
        for idx, device in enumerate(fleet_data):
            try:
                device_name = device.get("Device_Model", "Laptop (Standard)")
                age = float(device.get("Age_Years", 3))
                persona = device.get("Persona", "Admin Normal (HR/Finance)")
                country = device.get("Country", "FR")
                device_id = device.get("Device_ID", f"DEV-{idx:05d}")
                
                if device_name not in DEVICES:
                    device_name = "Laptop (Standard)"
                if persona not in PERSONAS:
                    persona = "Admin Normal (HR/Finance)"
                if country not in GRID_CARBON_FACTORS:
                    country = "FR"
                
                recommendation = RecommendationEngine.analyze_device(
                    device_name=device_name,
                    age_years=age,
                    persona=persona,
                    country=country,
                    priority=priority
                )
                
                recommendation.device_id = device_id
                recommendation.fleet_position = idx
                results.append(recommendation)
            except Exception as e:
                logger.warning(f"Failed to analyze device {idx}: {e}")
                continue
        
        results.sort(key=lambda x: x.urgency_score, reverse=True)
        for idx, rec in enumerate(results):
            rec.fleet_position = idx
        
        logger.info(f"Fleet analysis complete: {len(results)} devices")
        return results
    
    @staticmethod
    def summarize_fleet(recommendations: List[DeviceRecommendation]) -> Dict:
        """Generate summary."""
        total = len(recommendations)
        if total == 0:
            return {"total_devices": 0}
        
        by_recommendation = {"KEEP": 0, "NEW": 0, "REFURBISHED": 0}
        by_urgency = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for r in recommendations:
            by_recommendation[r.recommendation] = by_recommendation.get(r.recommendation, 0) + 1
            by_urgency[r.urgency] = by_urgency.get(r.urgency, 0) + 1
        
        total_savings = sum(r.annual_savings for r in recommendations)
        total_co2_savings = sum(r.co2_savings for r in recommendations)
        total_residual = sum(r.residual_value for r in recommendations)
        
        return {
            "total_devices": total,
            "by_recommendation": by_recommendation,
            "by_urgency": by_urgency,
            "total_annual_savings_eur": round(total_savings, 2),
            "total_co2_savings_kg": round(total_co2_savings, 2),
            "total_recoverable_value_eur": round(total_residual, 2),
        }