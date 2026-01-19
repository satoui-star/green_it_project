"""
Élysia - Calculator Module (Enhanced)
======================================
LVMH · Sustainable IT Intelligence

All calculation logic with documented mathematical formulas.
ENHANCED: Added 3-scenario analysis (BEST/REALISTIC/WORST) and roadmap generation.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging
import pandas as pd
from datetime import datetime, timedelta
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
class ScenarioResult:
    """Result for BEST/REALISTIC/WORST scenario analysis."""
    scenario_type: str  # "BEST", "REALISTIC", "WORST"
    label: str
    description: str
    co2_reduction_pct: float
    annual_savings_eur: float
    refurb_rate: float
    supply_risk: str
    support_cost_factor: float
    probability: str
    key_assumptions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


@dataclass
class RoadmapTask:
    """A task in the 90-day roadmap."""
    day: int
    week: int
    month: int
    title: str
    description: str
    owner: str
    deliverable: str
    success_criteria: str
    contingency: Optional[str] = None
    risk_level: str = "LOW"


@dataclass
class RoadmapPhase:
    """A phase in the production roadmap."""
    phase_number: int
    name: str
    duration_months: str
    objectives: List[str]
    key_actions: List[str]
    success_metrics: List[str]
    risks: List[str]


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
                  refresh_cycle: int = 4, target_pct: float = -20,
                  country: str = "FR", current_refurb_pct: float = 0.0) -> ShockMetrics:
        """
        Calculate shock metrics.
        
        Args:
            fleet_size: Total number of devices
            avg_age: Average device age in years
            refresh_cycle: Current refresh cycle in years
            target_pct: Target CO2 reduction percentage (negative)
            country: Primary country for grid factor
            current_refurb_pct: Current percentage of refurbished purchases
        """
        try:
            stranded = calculate_stranded_value(fleet_size, avg_age)
            stranded_value = stranded.get("value", 0)
            
            # Adjust for current refurb rate
            potential_refurb_rate = 0.40 - current_refurb_pct
            avoidable = calculate_avoidable_co2(fleet_size, refresh_cycle, refurb_rate=potential_refurb_rate)
            avoidable_co2 = avoidable.get("value_tonnes", 0)
            
            # Adjust CO2 by country grid factor
            grid_factor = get_grid_factor(country)
            france_factor = get_grid_factor("FR")
            if france_factor > 0:
                co2_multiplier = grid_factor / france_factor
            else:
                co2_multiplier = 1.0
            
            # Apply grid factor adjustment (usage CO2 varies by country)
            # Manufacturing CO2 stays same, but usage portion varies
            usage_portion = 0.15  # ~15% of CO2 is from usage
            adjusted_co2 = avoidable_co2 * (1 - usage_portion + usage_portion * co2_multiplier)
            
            deadline_status = "WILL MISS" if target_pct < 0 else "ON TRACK"
            
            logger.info(f"Shock: €{stranded_value}, CO2={adjusted_co2}t (country={country})")
            
            return ShockMetrics(
                stranded_value_eur=round(stranded_value, 2),
                avoidable_co2_tonnes=round(adjusted_co2, 1),
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
                  strategy_key: str = "refurb_40",
                  country: str = "FR") -> HopeMetrics:
        """Calculate before/after comparison."""
        try:
            strategy = STRATEGIES.get(strategy_key, STRATEGIES.get("refurb_40"))
            
            # Get grid factor for country
            grid_factor = get_grid_factor(country)
            
            annual_replacements = fleet_size / refresh_cycle
            manufacturing_co2 = annual_replacements * AVERAGES.get("device_co2_manufacturing_kg", 100)
            usage_co2 = fleet_size * AVERAGES.get("device_co2_annual_kg", 50) * (grid_factor / 0.052)  # Normalize to France
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
                months_to_target=min(months_to_target, 999)
            )
        except Exception as e:
            logger.error(f"HopeCalculator error: {e}")
            return HopeMetrics(0, 0, 0, 0, 0, 0, 0, False, 999)


# =============================================================================
# SCENARIO ANALYZER (NEW - BEST/REALISTIC/WORST)
# =============================================================================

class ScenarioAnalyzer:
    """
    Generates BEST, REALISTIC, and WORST case scenarios.
    This addresses the critical gap in Act 2.
    """
    
    @staticmethod
    def analyze(fleet_size: int, refresh_cycle: int = 4, 
                avg_age: float = 3.5, country: str = "FR") -> List[ScenarioResult]:
        """
        Generate three scenarios for strategy presentation.
        
        Returns:
            List of [BEST, REALISTIC, WORST] ScenarioResult objects
        """
        base_savings_per_device = AVERAGES["device_price_eur"] * (1 - REFURB_CONFIG["price_ratio"])
        annual_replacements = fleet_size / refresh_cycle
        co2_per_device = AVERAGES["device_co2_manufacturing_kg"]
        
        scenarios = []
        
        # BEST CASE: Everything goes perfectly
        best_refurb_rate = 0.45
        best_savings = annual_replacements * best_refurb_rate * base_savings_per_device
        best_co2_reduction = best_refurb_rate * REFURB_CONFIG["_co2_savings_range"]["high"]  # 91%
        
        scenarios.append(ScenarioResult(
            scenario_type="BEST",
            label="Best Case",
            description="All conditions align: strong supplier partnerships, high-quality inventory available, smooth user adoption.",
            co2_reduction_pct=round(best_co2_reduction * 100, 0),
            annual_savings_eur=round(best_savings * 1.1, 0),  # 10% bonus from volume discounts
            refurb_rate=best_refurb_rate,
            supply_risk="LOW",
            support_cost_factor=1.0,
            probability="20%",
            key_assumptions=[
                "45% of devices available as refurbished at enterprise scale",
                "91% CO₂ savings per refurbished device (Back Market claim)",
                "Volume discounts of 10% achieved",
                "No increase in support tickets",
                "User acceptance rate >90%"
            ],
            risks=[
                "Supply may not meet demand for specific models",
                "Requires strong vendor relationships"
            ]
        ))
        
        # REALISTIC CASE: Most likely outcome
        realistic_refurb_rate = 0.35
        support_cost_increase = 0.15  # 15% more support costs
        realistic_savings = annual_replacements * realistic_refurb_rate * base_savings_per_device
        realistic_savings *= (1 - support_cost_increase * 0.3)  # Offset by support costs
        realistic_co2_reduction = realistic_refurb_rate * REFURB_CONFIG["_co2_savings_range"]["mid"]  # 80%
        
        scenarios.append(ScenarioResult(
            scenario_type="REALISTIC",
            label="Realistic Case",
            description="Balanced expectations: good supplier availability, some model constraints, normal learning curve.",
            co2_reduction_pct=round(realistic_co2_reduction * 100, 0),
            annual_savings_eur=round(realistic_savings, 0),
            refurb_rate=realistic_refurb_rate,
            supply_risk="MEDIUM",
            support_cost_factor=1.15,
            probability="60%",
            key_assumptions=[
                "35% of devices available as refurbished",
                "80% CO₂ savings per refurbished device (Dell claim)",
                "15% increase in IT support tickets during transition",
                "2-month learning curve for procurement team",
                "Some users request exceptions"
            ],
            risks=[
                "Popular models may have longer lead times",
                "Initial quality issues during supplier vetting",
                "Executive devices likely excluded"
            ]
        ))
        
        # WORST CASE: Significant challenges
        worst_refurb_rate = 0.20
        support_cost_increase = 0.30  # 30% more support costs
        worst_savings = annual_replacements * worst_refurb_rate * base_savings_per_device
        worst_savings *= (1 - support_cost_increase * 0.5)  # Significant offset
        worst_co2_reduction = worst_refurb_rate * REFURB_CONFIG["_co2_savings_range"]["low"]  # 70%
        
        scenarios.append(ScenarioResult(
            scenario_type="WORST",
            label="Worst Case",
            description="Significant constraints: limited supply, quality concerns, resistance from users.",
            co2_reduction_pct=round(worst_co2_reduction * 100, 0),
            annual_savings_eur=round(worst_savings, 0),
            refurb_rate=worst_refurb_rate,
            supply_risk="HIGH",
            support_cost_factor=1.30,
            probability="20%",
            key_assumptions=[
                "Only 20% of devices available as refurbished",
                "70% CO₂ savings (conservative estimate)",
                "30% increase in IT support tickets",
                "Multiple suppliers needed, inconsistent quality",
                "Significant user pushback"
            ],
            risks=[
                "May need to abandon program if quality too low",
                "Reputational risk if failures visible to executives",
                "Procurement team overwhelmed with exceptions"
            ]
        ))
        
        return scenarios
    
    @staticmethod
    def get_scenario_comparison_table(scenarios: List[ScenarioResult]) -> List[Dict]:
        """Convert scenarios to table format for display."""
        return [
            {
                "Scenario": s.label,
                "CO₂ Reduction": f"-{s.co2_reduction_pct:.0f}%",
                "Annual Savings": f"€{s.annual_savings_eur:,.0f}",
                "Refurb Rate": f"{s.refurb_rate*100:.0f}%",
                "Supply Risk": s.supply_risk,
                "Probability": s.probability
            }
            for s in scenarios
        ]


# =============================================================================
# ROADMAP GENERATOR (NEW - Act 3)
# =============================================================================

class RoadmapGenerator:
    """
    Generates 90-day action plan with contingencies.
    This addresses the critical gap for Act 3.
    """
    
    @staticmethod
    def generate_90_day_roadmap(fleet_size: int, strategy: str = "refurb_40",
                                 refresh_cycle: int = 4) -> List[RoadmapTask]:
        """
        Generate detailed 90-day implementation roadmap.
        
        Args:
            fleet_size: Total devices in fleet
            strategy: Selected strategy key
            refresh_cycle: Current refresh cycle in years
        """
        annual_replacements = fleet_size // refresh_cycle
        pilot_size = min(100, annual_replacements // 10)
        
        tasks = [
            # WEEK 1: Preparation
            RoadmapTask(
                day=1, week=1, month=1,
                title="Kick-off Meeting",
                description="Convene steering committee with IT, Procurement, Sustainability, and Finance.",
                owner="Project Sponsor",
                deliverable="Project charter signed",
                success_criteria="All stakeholders aligned on goals and timeline",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=3, week=1, month=1,
                title="Current State Assessment",
                description="Document current fleet composition, procurement processes, and baseline metrics.",
                owner="IT Asset Manager",
                deliverable="Fleet inventory report",
                success_criteria="100% of devices catalogued with age and model",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=5, week=1, month=1,
                title="Budget Reallocation Request",
                description="Submit request to reallocate equipment budget for refurbished procurement.",
                owner="Finance Lead",
                deliverable="Budget modification request",
                success_criteria="Request submitted to CFO",
                contingency="If CFO requires Board approval → extend timeline by 3 weeks",
                risk_level="MEDIUM"
            ),
            
            # WEEK 2: Vendor Selection
            RoadmapTask(
                day=8, week=2, month=1,
                title="Vendor RFI",
                description="Send Request for Information to 5+ certified refurbishment partners.",
                owner="Procurement Lead",
                deliverable="RFI responses received",
                success_criteria="At least 3 qualified vendors respond",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=12, week=2, month=1,
                title="Vendor Evaluation",
                description="Evaluate vendors on quality, warranty, pricing, and sustainability certifications.",
                owner="Procurement Lead",
                deliverable="Vendor scorecard",
                success_criteria="Top 2 vendors identified",
                risk_level="LOW"
            ),
            
            # WEEK 3: Contracting
            RoadmapTask(
                day=15, week=3, month=1,
                title="Contract Negotiation",
                description="Negotiate pilot contract with selected vendor including SLAs and return policy.",
                owner="Procurement Lead",
                deliverable="Draft contract",
                success_criteria="<5% premium over target pricing",
                contingency="If pricing >10% above target → negotiate volume commitments",
                risk_level="MEDIUM"
            ),
            RoadmapTask(
                day=19, week=3, month=1,
                title="Legal Review",
                description="Legal team reviews warranty, liability, and data security clauses.",
                owner="Legal",
                deliverable="Approved contract",
                success_criteria="No red flags in contract terms",
                risk_level="LOW"
            ),
            
            # WEEK 4: Pilot Preparation
            RoadmapTask(
                day=22, week=4, month=1,
                title="Pilot Group Selection",
                description=f"Identify {pilot_size} devices for pilot replacement in low-risk department.",
                owner="IT Asset Manager",
                deliverable="Pilot device list",
                success_criteria="Pilot group represents typical use cases",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=26, week=4, month=1,
                title="Communication Plan",
                description="Prepare internal communications explaining the pilot and sustainability goals.",
                owner="Internal Comms",
                deliverable="Email templates and FAQ",
                success_criteria="Approved by Sustainability and IT leadership",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=28, week=4, month=1,
                title="Pilot Order Placed",
                description=f"Order {pilot_size} refurbished devices from selected vendor.",
                owner="Procurement Lead",
                deliverable="Purchase order",
                success_criteria="Order confirmed with 2-week delivery",
                contingency="If delivery >3 weeks → consider alternative models",
                risk_level="MEDIUM"
            ),
            
            # MONTH 2: Pilot Execution
            RoadmapTask(
                day=35, week=5, month=2,
                title="Pilot Devices Received",
                description="Receive and inspect pilot devices for quality and completeness.",
                owner="IT Operations",
                deliverable="Receiving report",
                success_criteria="<2% DOA (Dead on Arrival) rate",
                contingency="If DOA >2% → pause rollout, escalate to vendor",
                risk_level="HIGH"
            ),
            RoadmapTask(
                day=38, week=6, month=2,
                title="Pilot Deployment",
                description=f"Deploy {pilot_size} devices to pilot group with standard imaging.",
                owner="IT Operations",
                deliverable="Deployment completion report",
                success_criteria="All devices deployed within 1 week",
                risk_level="MEDIUM"
            ),
            RoadmapTask(
                day=45, week=7, month=2,
                title="Week 1 Check-in",
                description="Survey pilot users on device quality, performance, and satisfaction.",
                owner="IT Support Lead",
                deliverable="User feedback report",
                success_criteria="Satisfaction score >7/10",
                contingency="If satisfaction <6/10 → conduct focus group to identify issues",
                risk_level="MEDIUM"
            ),
            RoadmapTask(
                day=52, week=8, month=2,
                title="Week 2 Support Metrics",
                description="Analyze support tickets from pilot group vs. control group.",
                owner="IT Support Lead",
                deliverable="Support metrics comparison",
                success_criteria="Ticket volume <150% of control group",
                contingency="If tickets >200% → identify root cause, adjust deployment",
                risk_level="HIGH"
            ),
            RoadmapTask(
                day=56, week=8, month=2,
                title="Pilot Review Meeting",
                description="Present pilot results to steering committee with go/no-go recommendation.",
                owner="Project Sponsor",
                deliverable="Pilot results presentation",
                success_criteria="Go decision for scaled rollout",
                contingency="If no-go → develop remediation plan or reduce refurb target",
                risk_level="HIGH"
            ),
            
            # MONTH 3: Scale Preparation
            RoadmapTask(
                day=60, week=9, month=3,
                title="Scaled Procurement Plan",
                description=f"Develop procurement schedule for {annual_replacements} annual devices.",
                owner="Procurement Lead",
                deliverable="12-month procurement calendar",
                success_criteria="Schedule accounts for seasonality and lead times",
                risk_level="MEDIUM"
            ),
            RoadmapTask(
                day=65, week=10, month=3,
                title="Policy Updates",
                description="Update IT Asset Management policy to include refurbished devices.",
                owner="IT Governance",
                deliverable="Updated policy document",
                success_criteria="Approved by IT leadership",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=70, week=10, month=3,
                title="Vendor Capacity Confirmation",
                description="Confirm vendor can supply required volume for scaled rollout.",
                owner="Procurement Lead",
                deliverable="Vendor capacity confirmation",
                success_criteria="Vendor commits to volume with <4 week lead time",
                contingency="If vendor cannot meet volume → engage secondary vendor",
                risk_level="MEDIUM"
            ),
            RoadmapTask(
                day=75, week=11, month=3,
                title="Training Program",
                description="Develop training for IT support on refurbished device handling.",
                owner="IT Training",
                deliverable="Training materials and schedule",
                success_criteria="All support staff trained within 2 weeks",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=80, week=12, month=3,
                title="Success Metrics Framework",
                description="Establish KPIs and dashboard for ongoing program monitoring.",
                owner="Program Manager",
                deliverable="KPI dashboard",
                success_criteria="Automated tracking of failure rate, savings, CO₂",
                risk_level="LOW"
            ),
            RoadmapTask(
                day=85, week=12, month=3,
                title="Executive Report",
                description="Present 90-day results and full rollout plan to executive committee.",
                owner="Project Sponsor",
                deliverable="Executive summary presentation",
                success_criteria="Executive approval for full program",
                risk_level="MEDIUM"
            ),
            RoadmapTask(
                day=90, week=13, month=3,
                title="Program Launch",
                description="Officially launch refurbished device program across organization.",
                owner="Project Sponsor",
                deliverable="Launch announcement",
                success_criteria="Program operational, first batch ordered",
                risk_level="LOW"
            ),
        ]
        
        return tasks
    
    @staticmethod
    def get_tasks_by_month(tasks: List[RoadmapTask]) -> Dict[int, List[RoadmapTask]]:
        """Group tasks by month."""
        by_month = {1: [], 2: [], 3: []}
        for task in tasks:
            by_month[task.month].append(task)
        return by_month
    
    @staticmethod
    def get_high_risk_tasks(tasks: List[RoadmapTask]) -> List[RoadmapTask]:
        """Get tasks with contingencies (decision points)."""
        return [t for t in tasks if t.contingency]


# =============================================================================
# PRODUCTION ROADMAP GENERATOR (NEW - Act 4)
# =============================================================================

class ProductionRoadmapGenerator:
    """
    Generates long-term production roadmap (Months 4-36).
    This addresses the critical gap for Act 4.
    """
    
    @staticmethod
    def generate_production_roadmap(fleet_size: int, 
                                    target_refurb_rate: float = 0.40,
                                    target_co2_reduction: float = -20) -> List[RoadmapPhase]:
        """Generate 3-year production roadmap phases."""
        
        annual_replacements = fleet_size // 4
        year1_savings = annual_replacements * target_refurb_rate * 470  # €470 savings per device
        
        phases = [
            RoadmapPhase(
                phase_number=1,
                name="Scale Phase",
                duration_months="Months 4-12",
                objectives=[
                    f"Reach {int(target_refurb_rate * 100)}% refurbished adoption",
                    "Establish second vendor partnership",
                    "Achieve <2% device failure rate"
                ],
                key_actions=[
                    "Monthly procurement of refurbished devices",
                    "Quarterly vendor performance reviews",
                    "User satisfaction surveys (quarterly)",
                    "Support ticket analysis and process improvement"
                ],
                success_metrics=[
                    f"Refurbished adoption: {int(target_refurb_rate * 100)}%",
                    "Device failure rate: <2%",
                    "User satisfaction: >7.5/10",
                    f"Cost savings: €{int(year1_savings * 0.75):,} (Q1-Q4)"
                ],
                risks=[
                    "Vendor may not scale with demand",
                    "New device models may not have refurb availability",
                    "User resistance in high-profile departments"
                ]
            ),
            RoadmapPhase(
                phase_number=2,
                name="Optimization Phase",
                duration_months="Months 13-24",
                objectives=[
                    "Optimize vendor mix for best pricing",
                    "Expand to additional device categories",
                    "Reduce support overhead to baseline"
                ],
                key_actions=[
                    "Competitive rebidding for volume discounts",
                    "Pilot refurbished monitors and peripherals",
                    "Develop internal refurbishment capability assessment",
                    "Implement predictive replacement based on device health"
                ],
                success_metrics=[
                    f"Refurbished adoption maintained: {int(target_refurb_rate * 100)}%",
                    "Device failure rate: <1.5%",
                    "Support tickets: at baseline",
                    f"Annual savings locked in: €{int(year1_savings):,}"
                ],
                risks=[
                    "Market conditions may affect refurb pricing",
                    "Technology changes may limit refurb options"
                ]
            ),
            RoadmapPhase(
                phase_number=3,
                name="Sustainability Phase",
                duration_months="Months 25-36",
                objectives=[
                    f"Achieve LIFE 360 target: {target_co2_reduction}% CO₂ reduction",
                    "Establish circular economy metrics",
                    "Document and share best practices"
                ],
                key_actions=[
                    "Full lifecycle carbon tracking",
                    "Device recovery and resale program",
                    "Publish sustainability impact report",
                    "Present at industry conferences"
                ],
                success_metrics=[
                    f"CO₂ reduction: {abs(target_co2_reduction)}% vs. baseline",
                    f"Cumulative savings: €{int(year1_savings * 2.5):,}",
                    "Devices recovered/resold: >50%",
                    "Program recognized as best practice"
                ],
                risks=[
                    "Regulatory changes may affect targets",
                    "New sustainability standards may require adjustment"
                ]
            ),
            RoadmapPhase(
                phase_number=4,
                name="Maturity Phase",
                duration_months="Year 4+",
                objectives=[
                    "Maintain program as standard operating procedure",
                    "Continuous improvement based on data",
                    "Extend to group-wide adoption"
                ],
                key_actions=[
                    "Annual program review and target adjustment",
                    "Share playbook with other Maisons",
                    "Explore emerging technologies (AI-powered device health)",
                    "Advocacy for industry-wide standards"
                ],
                success_metrics=[
                    "Program self-sustaining (no dedicated project team)",
                    "Year-over-year improvement in all KPIs",
                    "Adopted by 3+ additional Maisons",
                    "Referenced in LVMH sustainability report"
                ],
                risks=[
                    "Leadership changes may affect priority",
                    "Budget pressures may reduce investment"
                ]
            )
        ]
        
        return phases


# =============================================================================
# TCO CALCULATOR
# =============================================================================

class TCOCalculator:
    """Calculates Total Cost of Ownership for devices."""
    
    @staticmethod
    def calculate_productivity_loss(device_name: str, age_years: float, 
                                    persona: str) -> Tuple[float, float]:
        """
        Calculate productivity loss from aging device.
        
        Returns:
            (loss_percentage, annual_cost)
        """
        optimal_years = PRODUCTIVITY_CONFIG.get("optimal_years", 3)
        degradation_per_year = PRODUCTIVITY_CONFIG.get("degradation_per_year", 0.03)
        max_degradation = PRODUCTIVITY_CONFIG.get("max_degradation", 0.15)
        
        if age_years <= optimal_years:
            loss_pct = 0.0
        else:
            years_over = age_years - optimal_years
            loss_pct = min(years_over * degradation_per_year, max_degradation)
        
        persona_data = PERSONAS.get(persona, {})
        salary = persona_data.get("salary_eur", 50000)
        lag_sensitivity = persona_data.get("lag_sensitivity", 1.0)
        
        annual_cost = salary * loss_pct * lag_sensitivity
        
        return round(loss_pct, 4), round(annual_cost, 2)
    
    @staticmethod
    def calculate_tco_keep(device_name: str, age_years: float, 
                          persona: str, country: str) -> Dict:
        """Calculate TCO for keeping current device."""
        device = DEVICES.get(device_name, {})
        
        power_kw = device.get("power_kw", 0.03)
        annual_hours = 1607
        energy_kwh = power_kw * annual_hours
        grid_factor = get_grid_factor(country)
        energy_cost = energy_kwh * PRICE_KWH_EUR
        
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(
            device_name, age_years, persona
        )
        
        residual_now = TCOCalculator.calculate_residual_value(device_name, age_years)
        residual_next = TCOCalculator.calculate_residual_value(device_name, age_years + 1)
        residual_loss = residual_now - residual_next
        
        total = energy_cost + productivity_cost + residual_loss
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "energy": round(energy_cost, 2),
                "productivity_loss": round(productivity_cost, 2),
                "residual_loss": round(residual_loss, 2),
            },
            "productivity_loss_pct": loss_pct,
            "note": "Annual cost to keep current device"
        }
    
    @staticmethod
    def calculate_tco_new(device_name: str, persona: str, country: str) -> Dict:
        """Calculate TCO for buying new device."""
        device = DEVICES.get(device_name, {})
        
        price = device.get("price_new_eur", 1000)
        lifespan_months = device.get("lifespan_months", 48)
        lifespan_years = lifespan_months / 12
        annual_purchase = price / lifespan_years
        
        power_kw = device.get("power_kw", 0.03)
        annual_hours = 1607
        energy_cost = power_kw * annual_hours * PRICE_KWH_EUR
        
        disposal = get_disposal_cost(device_name)
        annual_disposal = disposal / lifespan_years
        
        total = annual_purchase + energy_cost + annual_disposal
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "purchase": round(annual_purchase, 2),
                "energy": round(energy_cost, 2),
                "disposal": round(annual_disposal, 2),
            },
            "note": "Annual cost for new device"
        }
    
    @staticmethod
    def calculate_tco_refurb(device_name: str, persona: str, country: str) -> Dict:
        """Calculate TCO for buying refurbished device."""
        device = DEVICES.get(device_name, {})
        
        if not device.get("refurb_available", False):
            return {
                "total": float('inf'),
                "available": False,
                "note": "Refurbished not available for this device"
            }
        
        price_new = device.get("price_new_eur", 1000)
        price_refurb = price_new * REFURB_CONFIG.get("price_ratio", 0.59)
        
        warranty_years = REFURB_CONFIG.get("warranty_years", 2)
        annual_purchase = price_refurb / warranty_years
        
        power_kw = device.get("power_kw", 0.03)
        energy_penalty = REFURB_CONFIG.get("energy_penalty", 0.10)
        effective_power = power_kw * (1 + energy_penalty)
        energy_cost = effective_power * 1607 * PRICE_KWH_EUR
        
        disposal = get_disposal_cost(device_name)
        annual_disposal = disposal / warranty_years
        
        total = annual_purchase + energy_cost + annual_disposal
        
        return {
            "total": round(total, 2),
            "available": True,
            "breakdown": {
                "purchase": round(annual_purchase, 2),
                "energy": round(energy_cost, 2),
                "disposal": round(annual_disposal, 2),
            },
            "note": "Annual cost for refurbished device"
        }
    
    @staticmethod
    def calculate_residual_value(device_name: str, age_years: float) -> float:
        """Calculate residual value of device."""
        device = DEVICES.get(device_name, {})
        price = device.get("price_new_eur", 1000)
        
        depreciation_rate = get_depreciation_rate(age_years)
        base_residual = price * depreciation_rate
        
        if is_premium_device(device_name):
            base_residual *= (1 + PREMIUM_RETENTION_BONUS)
        
        return round(max(0, base_residual), 2)


# =============================================================================
# CO2 CALCULATOR
# =============================================================================

class CO2Calculator:
    """Calculates CO2 emissions for devices."""
    
    @staticmethod
    def calculate_co2_keep(device_name: str, persona: str, country: str) -> Dict:
        """Calculate annual CO2 for keeping current device."""
        device = DEVICES.get(device_name, {})
        
        power_kw = device.get("power_kw", 0.03)
        annual_hours = 1607
        energy_kwh = power_kw * annual_hours
        grid_factor = get_grid_factor(country)
        usage_co2 = energy_kwh * grid_factor
        
        return {
            "total": round(usage_co2, 2),
            "breakdown": {
                "usage": round(usage_co2, 2),
                "manufacturing": 0,
            },
            "note": "Only usage CO2 (device already manufactured)"
        }
    
    @staticmethod
    def calculate_co2_new(device_name: str, persona: str, country: str) -> Dict:
        """Calculate annual CO2 for buying new device."""
        device = DEVICES.get(device_name, {})
        
        manufacturing_co2 = device.get("co2_manufacturing_kg", 250)
        lifespan_months = device.get("lifespan_months", 48)
        lifespan_years = lifespan_months / 12
        annual_manufacturing = manufacturing_co2 / lifespan_years
        
        power_kw = device.get("power_kw", 0.03)
        annual_hours = 1607
        energy_kwh = power_kw * annual_hours
        grid_factor = get_grid_factor(country)
        usage_co2 = energy_kwh * grid_factor
        
        total = annual_manufacturing + usage_co2
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "manufacturing": round(annual_manufacturing, 2),
                "usage": round(usage_co2, 2),
            },
            "note": "Full lifecycle CO2"
        }
    
    @staticmethod
    def calculate_co2_refurb(device_name: str, persona: str, country: str) -> Dict:
        """Calculate annual CO2 for buying refurbished device."""
        device = DEVICES.get(device_name, {})
        
        if not device.get("refurb_available", False):
            return {
                "total": float('inf'),
                "available": False,
                "note": "Refurbished not available"
            }
        
        manufacturing_co2 = device.get("co2_manufacturing_kg", 250)
        co2_savings_rate = REFURB_CONFIG.get("co2_savings_rate", 0.80)
        refurb_manufacturing = manufacturing_co2 * (1 - co2_savings_rate)
        
        warranty_years = REFURB_CONFIG.get("warranty_years", 2)
        annual_manufacturing = refurb_manufacturing / warranty_years
        
        power_kw = device.get("power_kw", 0.03)
        energy_penalty = REFURB_CONFIG.get("energy_penalty", 0.10)
        effective_power = power_kw * (1 + energy_penalty)
        annual_hours = 1607
        energy_kwh = effective_power * annual_hours
        grid_factor = get_grid_factor(country)
        usage_co2 = energy_kwh * grid_factor
        
        total = annual_manufacturing + usage_co2
        
        return {
            "total": round(total, 2),
            "available": True,
            "breakdown": {
                "manufacturing": round(annual_manufacturing, 2),
                "usage": round(usage_co2, 2),
            },
            "note": f"{int(co2_savings_rate*100)}% savings on manufacturing CO2"
        }


# =============================================================================
# URGENCY CALCULATOR
# =============================================================================

class UrgencyCalculator:
    """Calculates replacement urgency for devices."""
    
    @staticmethod
    def calculate(device_name: str, age_years: float, 
                  persona: str) -> Tuple[float, str, str]:
        """
        Calculate urgency score and level.
        
        Returns:
            (score, level, rationale)
        """
        score = 0.0
        factors = []
        
        age_critical = URGENCY_CONFIG.get("age_critical_years", 5)
        age_high = URGENCY_CONFIG.get("age_high_years", 4)
        
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
        strategy = STRATEGIES.get(strategy_key, STRATEGIES.get("do_nothing"))
        
        annual_replacements = fleet_size / current_refresh
        current_co2 = annual_replacements * AVERAGES["device_co2_manufacturing_kg"]
        current_co2_tonnes = current_co2 / 1000
        
        refurb_rate = strategy.get("refurb_rate", 0)
        new_lifecycle = strategy.get("lifecycle_years", 4)
        
        new_annual_replacements = fleet_size / new_lifecycle
        new_devices_co2 = new_annual_replacements * (1 - refurb_rate) * AVERAGES["device_co2_manufacturing_kg"]
        refurb_devices_co2 = new_annual_replacements * refurb_rate * AVERAGES["device_co2_manufacturing_kg"] * 0.20
        new_co2 = new_devices_co2 + refurb_devices_co2
        new_co2_tonnes = new_co2 / 1000
        
        co2_savings = current_co2_tonnes - new_co2_tonnes
        co2_reduction_pct = (co2_savings / current_co2_tonnes * 100) if current_co2_tonnes > 0 else 0
        
        current_cost = annual_replacements * AVERAGES["device_price_eur"]
        new_devices_cost = new_annual_replacements * (1 - refurb_rate) * AVERAGES["device_price_eur"]
        refurb_devices_cost = new_annual_replacements * refurb_rate * AVERAGES["device_price_eur"] * REFURB_CONFIG["price_ratio"]
        new_cost = new_devices_cost + refurb_devices_cost
        
        cost_savings = current_cost - new_cost
        
        implementation_cost = fleet_size * 5
        
        target_co2 = current_co2_tonnes * (1 + target_pct / 100)
        monthly_reduction = co2_savings / 12 if co2_savings > 0 else 0
        
        if monthly_reduction > 0:
            gap = current_co2_tonnes - target_co2
            months_to_target = int(gap / monthly_reduction)
            reaches_target = months_to_target <= time_horizon_months
        else:
            months_to_target = 999
            reaches_target = False
        
        monthly_co2 = []
        current = current_co2_tonnes
        for month in range(time_horizon_months + 1):
            monthly_co2.append(round(current, 1))
            if month < strategy.get("implementation_months", 0):
                continue
            current = max(new_co2_tonnes, current - monthly_reduction)
        
        if cost_savings > 0:
            payback_months = implementation_cost / (cost_savings / 12)
        else:
            payback_months = 999
        
        roi_3year = ((cost_savings * 3) - implementation_cost) / implementation_cost if implementation_cost > 0 else 0
        
        return StrategyResult(
            strategy_key=strategy_key,
            strategy_name=strategy["name"],
            description=strategy["description"],
            co2_savings_tonnes=round(co2_savings, 1),
            co2_reduction_pct=round(co2_reduction_pct, 1),
            cost_savings_eur=round(cost_savings, 0),
            time_to_target_months=min(months_to_target, 999),
            reaches_target=reaches_target,
            implementation_cost_eur=round(implementation_cost, 0),
            annual_savings_eur=round(cost_savings, 0),
            payback_months=round(payback_months, 1),
            roi_3year=round(roi_3year, 2),
            monthly_co2=monthly_co2,
            calculation_details={
                "refurb_rate": refurb_rate,
                "new_lifecycle": new_lifecycle,
                "annual_replacements": annual_replacements,
            }
        )
    
    @staticmethod
    def compare_all_strategies(fleet_size: int, current_refresh: int = 4,
                               avg_age: float = 3.5, target_pct: float = -20,
                               time_horizon_months: int = 36) -> List[StrategyResult]:
        """Compare all available strategies."""
        results = []
        for key in STRATEGIES.keys():
            result = StrategySimulator.simulate_strategy(
                key, fleet_size, current_refresh, avg_age, target_pct, time_horizon_months
            )
            results.append(result)
        
        results.sort(key=lambda x: (-x.reaches_target, -x.co2_reduction_pct))
        return results
    
    @staticmethod
    def get_recommended_strategy(fleet_size: int, current_refresh: int = 4,
                                 avg_age: float = 3.5, target_pct: float = -20,
                                 priority: str = "balanced") -> StrategyResult:
        """Get recommended strategy based on priority."""
        results = StrategySimulator.compare_all_strategies(
            fleet_size, current_refresh, avg_age, target_pct
        )
        
        valid = [r for r in results if r.reaches_target and r.strategy_key != "do_nothing"]
        
        if not valid:
            valid = [r for r in results if r.strategy_key != "do_nothing"]
        
        if not valid:
            return results[0]
        
        if priority == "cost":
            valid.sort(key=lambda x: -x.annual_savings_eur)
        elif priority == "co2":
            valid.sort(key=lambda x: -x.co2_reduction_pct)
        elif priority == "speed":
            valid.sort(key=lambda x: x.time_to_target_months)
        else:
            valid.sort(key=lambda x: (-x.co2_reduction_pct * 0.4 - x.annual_savings_eur / 1000000 * 0.4 - (1 if x.reaches_target else 0) * 0.2))
        
        return valid[0]


# =============================================================================
# LIMITATIONS GENERATOR (NEW)
# =============================================================================

class LimitationsGenerator:
    """
    Generates "When This Won't Work" section.
    Addresses the credibility gap.
    """
    
    @staticmethod
    def get_limitations(country: str = "FR", fleet_composition: str = "mixed") -> Dict:
        """Get limitations and contraindications."""
        
        limitations = {
            "not_recommended_if": [
                "Your fleet is primarily desktop computers (refurbished availability <20%)",
                "You require specific hardware configurations not available refurbished",
                "Your security policy prohibits non-new devices",
                "Your fleet is less than 2 years old on average",
                "You operate in a high-carbon grid country with no sustainability mandate"
            ],
            "reduced_effectiveness_if": [
                "Executive devices represent >30% of fleet (typically excluded from refurb)",
                "You have strict cosmetic requirements (Grade A only)",
                "Your procurement process cannot accommodate longer lead times",
                "You require same-day replacement SLAs"
            ],
            "country_specific": [],
            "assumptions_to_validate": [
                "Refurbished devices available at enterprise scale for your models",
                "Your IT support team can handle potential increase in tickets",
                "Your vendor contracts allow mid-cycle changes",
                "Budget can be reallocated (not just reduced)"
            ]
        }
        
        # Add country-specific limitations
        grid_factor = get_grid_factor(country)
        if grid_factor > 0.3:
            limitations["country_specific"].append(
                f"High-carbon grid ({country}): Manufacturing CO₂ dominates, so refurbished impact is higher"
            )
        elif grid_factor < 0.1:
            limitations["country_specific"].append(
                f"Low-carbon grid ({country}): Usage CO₂ is minimal, so manufacturing is main focus"
            )
        
        return limitations