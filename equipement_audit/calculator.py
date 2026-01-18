"""
EcoCycle Intelligence - Calculator Module
==========================================
LVMH · Digital Sustainability Division

All calculation logic with documented mathematical formulas.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from reference_data_API import (
    DEVICES, PERSONAS, PRICE_KWH_EUR, PRODUCTIVITY_CONFIG, REFURB_CONFIG,
    URGENCY_CONFIG, URGENCY_THRESHOLDS, STRATEGIES, MAISONS,
    get_grid_factor, get_depreciation_rate, is_premium_device,
    PREMIUM_RETENTION_BONUS, get_disposal_cost
)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DeviceAnalysis:
    """Complete analysis result for a single device."""
    device_name: str
    age_years: float
    persona: str
    country: str
    recommendation: str
    urgency: str
    urgency_score: float
    tco_keep: float
    tco_new: float
    tco_refurb: Optional[float]
    residual_value: float
    annual_savings: float
    co2_keep: float
    co2_new: float
    co2_refurb: Optional[float]
    co2_savings: float
    productivity_loss_pct: float
    energy_cost_annual: float
    rationale: str
    maison: str = ""


@dataclass
class StrategyProjection:
    """Projection result for a strategy."""
    strategy_key: str
    strategy_name: str
    description: str
    months_to_target: float
    reaches_target: bool
    final_co2_reduction_pct: float
    implementation_cost: float
    annual_savings: float
    annual_recovery_value: float
    roi_year1: float
    payback_months: float
    monthly_co2: List[float] = field(default_factory=list)


# =============================================================================
# TCO CALCULATOR
# =============================================================================

class TCOCalculator:
    """
    Total Cost of Ownership Calculator
    
    Formula:
    TCO_annual = (Purchase_Cost / Lifespan_Years) 
               + Energy_Cost 
               + Productivity_Loss
               + Disposal_Cost / Lifespan
               - Residual_Value / Remaining_Years
    """
    
    @staticmethod
    def calculate_energy_cost(device_name: str, persona: str, country: str) -> float:
        """
        Energy_Cost = Power_kW × Hours_Annual × Price_kWh
        """
        device = DEVICES.get(device_name)
        persona_data = PERSONAS.get(persona)
        if not device or not persona_data:
            return 0.0
        
        daily_hours = persona_data["daily_hours"]
        annual_hours = daily_hours * 220  # ~220 working days
        power_kw = device["power_kw"]
        
        return round(power_kw * annual_hours * PRICE_KWH_EUR, 2)
    
    @staticmethod
    def calculate_productivity_loss(device_name: str, age_years: float, persona: str) -> Tuple[float, float]:
        """
        If age > optimal_years:
            Loss_Pct = min((age - optimal) × degradation_rate, max_degradation)
            Loss_Cost = Salary × Loss_Pct × Lag_Sensitivity
        """
        persona_data = PERSONAS.get(persona)
        if not persona_data:
            return 0.0, 0.0
        
        optimal = PRODUCTIVITY_CONFIG["optimal_years"]
        degradation = PRODUCTIVITY_CONFIG["degradation_per_year"]
        max_deg = PRODUCTIVITY_CONFIG["max_degradation"]
        
        if age_years <= optimal:
            loss_pct = 0.0
        else:
            loss_pct = min((age_years - optimal) * degradation, max_deg)
        
        salary = persona_data["salary_eur"]
        sensitivity = persona_data["lag_sensitivity"]
        loss_cost = salary * loss_pct * sensitivity
        
        return round(loss_pct, 4), round(loss_cost, 2)
    
    @staticmethod
    def calculate_residual_value(device_name: str, age_years: float) -> float:
        """
        Residual = Price_New × Depreciation_Rate × (1 + Premium_Bonus if applicable)
        """
        device = DEVICES.get(device_name)
        if not device:
            return 0.0
        
        price_new = device["price_new_eur"]
        dep_rate = get_depreciation_rate(age_years)
        
        if is_premium_device(device_name):
            dep_rate = min(dep_rate + PREMIUM_RETENTION_BONUS, 1.0)
        
        return round(price_new * dep_rate, 2)
    
    @staticmethod
    def calculate_tco_keep(device_name: str, age_years: float, persona: str, country: str) -> Dict:
        """TCO for keeping current device one more year."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}, "productivity_loss_pct": 0}
        
        energy_cost = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(device_name, age_years, persona)
        
        # Residual value decreases over time
        current_residual = TCOCalculator.calculate_residual_value(device_name, age_years)
        future_residual = TCOCalculator.calculate_residual_value(device_name, age_years + 1)
        residual_loss = current_residual - future_residual
        
        total = energy_cost + productivity_cost + residual_loss
        
        return {
            "total": round(total, 2),
            "breakdown": {
                "energy": energy_cost,
                "productivity_loss": productivity_cost,
                "residual_loss": residual_loss,
            },
            "productivity_loss_pct": loss_pct,
        }
    
    @staticmethod
    def calculate_tco_new(device_name: str, persona: str, country: str) -> Dict:
        """TCO for buying a new device (annualized)."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        lifespan_years = device["lifespan_months"] / 12
        annual_purchase = device["price_new_eur"] / lifespan_years
        energy_cost = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        disposal_cost = get_disposal_cost(device_name) / lifespan_years
        
        # Residual benefit (value at end of year 1)
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
        """TCO for buying a refurbished device."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}, "available": False}
        
        if not device.get("refurb_available", False):
            return {"total": float('inf'), "breakdown": {}, "available": False}
        
        # Refurb pricing
        price_refurb = device["price_new_eur"] * (1 - REFURB_CONFIG["price_discount_factor"])
        lifespan_years = REFURB_CONFIG["warranty_years"]
        annual_purchase = price_refurb / lifespan_years
        
        # Energy (10% penalty for older tech)
        base_energy = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        energy_cost = base_energy * (1 + REFURB_CONFIG["energy_penalty_factor"])
        
        # Minor productivity loss (refurb is ~1.5 year old equivalent)
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(device_name, 1.5, persona)
        
        disposal_cost = get_disposal_cost(device_name) / lifespan_years
        residual_benefit = price_refurb * 0.2 / lifespan_years
        
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
    """
    Carbon Footprint Calculator
    
    Formula:
    CO2_annual = (Manufacturing_CO2 / Lifespan_Years) + Usage_CO2
    Usage_CO2 = Power_kW × Hours_Annual × Grid_Factor
    """
    
    @staticmethod
    def calculate_usage_co2(device_name: str, persona: str, country: str) -> float:
        """Annual CO2 from device usage (operational emissions)."""
        device = DEVICES.get(device_name)
        persona_data = PERSONAS.get(persona)
        if not device or not persona_data:
            return 0.0
        
        daily_hours = persona_data["daily_hours"]
        annual_hours = daily_hours * 220
        power_kw = device["power_kw"]
        grid_factor = get_grid_factor(country)
        
        return round(power_kw * annual_hours * grid_factor, 2)
    
    @staticmethod
    def calculate_co2_keep(device_name: str, persona: str, country: str) -> Dict:
        """CO2 for keeping current device (manufacturing already emitted)."""
        usage_co2 = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        return {
            "total": round(usage_co2, 2),
            "breakdown": {
                "manufacturing": 0,  # Already emitted
                "usage": round(usage_co2, 2),
            }
        }
    
    @staticmethod
    def calculate_co2_new(device_name: str, persona: str, country: str) -> Dict:
        """Annual CO2 for a new device (amortized manufacturing + usage)."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        lifespan_years = device["lifespan_months"] / 12
        manufacturing_annual = device["co2_manufacturing_kg"] / lifespan_years
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
        """Annual CO2 for refurbished device (85% less manufacturing CO2)."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        if not device.get("refurb_available", False):
            return {"total": float('inf'), "breakdown": {}, "available": False}
        
        lifespan_years = REFURB_CONFIG["warranty_years"]
        
        # 85% reduction in manufacturing CO2
        manufacturing_refurb = device["co2_manufacturing_kg"] * (1 - REFURB_CONFIG["co2_reduction_factor"])
        manufacturing_annual = manufacturing_refurb / lifespan_years
        
        # Usage (10% penalty for older tech)
        usage_base = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        usage_annual = usage_base * (1 + REFURB_CONFIG["energy_penalty_factor"])
        
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
    """
    Urgency Scoring based on ITIL v4 Framework
    
    Score = Base + Age_Factor + Performance_Factor + Sensitivity_Factor
    """
    
    @staticmethod
    def calculate_score(device_name: str, age_years: float, persona: str) -> Tuple[float, str, str]:
        """Returns: (score, level, rationale)"""
        score = 1.0
        factors = []
        
        # Age factor
        if age_years >= URGENCY_CONFIG["age_critical_years"]:
            score += 1.5
            factors.append(f"Device age ({age_years:.1f}y) exceeds critical threshold ({URGENCY_CONFIG['age_critical_years']}y)")
        elif age_years >= URGENCY_CONFIG["age_high_years"]:
            score += 0.8
            factors.append(f"Device age ({age_years:.1f}y) above recommended ({URGENCY_CONFIG['age_high_years']}y)")
        
        # Performance factor
        loss_pct, _ = TCOCalculator.calculate_productivity_loss(device_name, age_years, persona)
        performance = 1 - loss_pct
        if performance < URGENCY_CONFIG["performance_threshold"]:
            score += 0.7
            factors.append(f"Performance degraded to {performance*100:.0f}%")
        
        # Persona sensitivity factor
        persona_data = PERSONAS.get(persona, {})
        sensitivity = persona_data.get("lag_sensitivity", 1.0)
        if sensitivity >= 2.0:
            score += 0.3
            factors.append(f"High-impact role ({persona})")
        
        # Determine level
        if score >= URGENCY_THRESHOLDS["HIGH"]:
            level = "HIGH"
        elif score >= URGENCY_THRESHOLDS["MEDIUM"]:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        rationale = " | ".join(factors) if factors else "Device within normal parameters"
        
        return round(score, 2), level, rationale


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

class RecommendationEngine:
    """Generates recommendations based on TCO and CO2 analysis."""
    
    @staticmethod
    def analyze_device(device_name: str, age_years: float, persona: str,
                       country: str, optimization_goal: str = "balanced") -> DeviceAnalysis:
        """
        Complete analysis for a single device.
        
        optimization_goal: "balanced", "cost_first", "eco_first"
        """
        # Calculate all TCOs
        tco_keep = TCOCalculator.calculate_tco_keep(device_name, age_years, persona, country)
        tco_new = TCOCalculator.calculate_tco_new(device_name, persona, country)
        tco_refurb = TCOCalculator.calculate_tco_refurb(device_name, persona, country)
        
        # Calculate all CO2s
        co2_keep = CO2Calculator.calculate_co2_keep(device_name, persona, country)
        co2_new = CO2Calculator.calculate_co2_new(device_name, persona, country)
        co2_refurb = CO2Calculator.calculate_co2_refurb(device_name, persona, country)
        
        # Calculate urgency
        urgency_score, urgency_level, _ = UrgencyCalculator.calculate_score(device_name, age_years, persona)
        
        # Calculate residual value
        residual = TCOCalculator.calculate_residual_value(device_name, age_years)
        
        # Determine recommendation
        refurb_available = tco_refurb.get("available", False)
        
        options = {
            "KEEP": {"tco": tco_keep["total"], "co2": co2_keep["total"]},
            "NEW": {"tco": tco_new["total"], "co2": co2_new["total"]},
        }
        if refurb_available:
            options["REFURBISHED"] = {"tco": tco_refurb["total"], "co2": co2_refurb["total"]}
        
        # Score options based on goal
        max_tco = max(o["tco"] for o in options.values()) or 1
        max_co2 = max(o["co2"] for o in options.values()) or 1
        
        scores = {}
        for opt, data in options.items():
            if optimization_goal == "cost_first":
                scores[opt] = data["tco"]
            elif optimization_goal == "eco_first":
                scores[opt] = data["co2"]
            else:  # balanced
                tco_norm = data["tco"] / max_tco if max_tco > 0 else 0
                co2_norm = data["co2"] / max_co2 if max_co2 > 0 else 0
                scores[opt] = (tco_norm + co2_norm) / 2
        
        best = min(scores, key=scores.get)
        
        # Override for HIGH urgency
        if urgency_level == "HIGH" and best == "KEEP":
            best = "REFURBISHED" if refurb_available else "NEW"
            rationale = "High urgency: device requires replacement due to age/performance"
        elif best == "KEEP":
            rationale = f"Cost-effective to maintain. Annual TCO: €{tco_keep['total']:.0f}"
        elif best == "REFURBISHED":
            savings = tco_keep["total"] - tco_refurb["total"]
            co2_saved = co2_new["total"] - co2_refurb["total"]
            rationale = f"Best value: saves €{savings:.0f}/year and {co2_saved:.1f}kg CO2 vs new"
        else:
            rationale = "New device recommended for optimal performance and reliability"
        
        if residual > 50 and best != "KEEP":
            rationale += f". Current device recoverable value: €{residual:.0f}"
        
        # Calculate savings
        tco_refurb_val = tco_refurb["total"] if refurb_available else float('inf')
        co2_refurb_val = co2_refurb["total"] if refurb_available else float('inf')
        
        best_tco = min(tco_keep["total"], tco_new["total"], tco_refurb_val)
        best_co2 = min(co2_keep["total"], co2_new["total"], co2_refurb_val)
        
        annual_savings = max(0, tco_keep["total"] - best_tco)
        co2_savings = max(0, co2_keep["total"] - best_co2)
        
        return DeviceAnalysis(
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
            residual_value=residual,
            annual_savings=annual_savings,
            co2_keep=co2_keep["total"],
            co2_new=co2_new["total"],
            co2_refurb=co2_refurb["total"] if refurb_available else None,
            co2_savings=co2_savings,
            productivity_loss_pct=tco_keep.get("productivity_loss_pct", 0),
            energy_cost_annual=tco_keep["breakdown"].get("energy", 0),
            rationale=rationale,
        )


# =============================================================================
# STRATEGY SIMULATOR
# =============================================================================

class StrategySimulator:
    """Simulates lifecycle strategies and projects outcomes."""
    
    @staticmethod
    def simulate_strategy(strategy_key: str, fleet_size: int,
                          current_refresh_years: int, current_refurb_rate: float,
                          average_device_value: float, average_co2_per_device: float,
                          target_reduction: float = 0.20,
                          time_horizon_months: int = 36) -> StrategyProjection:
        """Simulate a strategy and project monthly outcomes."""
        
        strategy = STRATEGIES.get(strategy_key)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_key}")
        
        # Current state
        current_annual_co2 = fleet_size * average_co2_per_device
        target_co2 = current_annual_co2 * (1 - target_reduction)
        
        # Strategy parameters
        new_refresh_years = strategy["refresh_years"]
        new_refurb_rate = strategy["refurb_rate"]
        recovery_rate = strategy["recovery_rate"]
        
        # Calculate annual replacements
        current_replacements = fleet_size / current_refresh_years
        new_replacements = fleet_size / new_refresh_years
        
        # Manufacturing CO2 calculations
        avg_manufacturing_co2 = 200  # kg average from DEVICES
        
        current_manufacturing_co2 = current_replacements * avg_manufacturing_co2 * (1 - current_refurb_rate * REFURB_CONFIG["co2_reduction_factor"])
        new_manufacturing_co2 = new_replacements * avg_manufacturing_co2 * (1 - new_refurb_rate * REFURB_CONFIG["co2_reduction_factor"])
        
        # Monthly CO2 reduction rate
        annual_reduction = current_manufacturing_co2 - new_manufacturing_co2
        monthly_reduction_rate = annual_reduction / 12 / current_annual_co2 if current_annual_co2 > 0 else 0
        
        # Project monthly CO2
        monthly_co2 = []
        current_co2 = current_annual_co2
        months_to_target = None
        
        for month in range(time_horizon_months + 1):
            monthly_co2.append(current_co2)
            
            if current_co2 <= target_co2 and months_to_target is None:
                months_to_target = month
            
            # Apply reduction with ramp-up (first 6 months)
            ramp_factor = min(month / 6, 1.0) if month < 6 else 1.0
            current_co2 = current_co2 * (1 - monthly_reduction_rate * ramp_factor)
        
        reaches_target = months_to_target is not None
        if not reaches_target:
            months_to_target = 999
        
        # Financial calculations
        implementation_cost = fleet_size * average_device_value * strategy["implementation_cost_factor"]
        replacement_savings = (current_replacements - new_replacements) * average_device_value
        refurb_savings = new_replacements * new_refurb_rate * average_device_value * REFURB_CONFIG["price_discount_factor"]
        annual_recovery = fleet_size / new_refresh_years * recovery_rate * average_device_value * 0.2  # 20% residual
        
        annual_savings = replacement_savings + refurb_savings
        total_year1_benefit = annual_savings + annual_recovery - implementation_cost
        roi_year1 = total_year1_benefit / implementation_cost if implementation_cost > 0 else 0
        payback_months = implementation_cost / ((annual_savings + annual_recovery) / 12) if (annual_savings + annual_recovery) > 0 else 999
        
        final_co2_reduction = (current_annual_co2 - monthly_co2[-1]) / current_annual_co2 if current_annual_co2 > 0 else 0
        
        return StrategyProjection(
            strategy_key=strategy_key,
            strategy_name=strategy["name"],
            description=strategy["description"],
            months_to_target=months_to_target,
            reaches_target=reaches_target,
            final_co2_reduction_pct=final_co2_reduction,
            implementation_cost=round(implementation_cost, 2),
            annual_savings=round(annual_savings, 2),
            annual_recovery_value=round(annual_recovery, 2),
            roi_year1=round(roi_year1, 2),
            payback_months=round(payback_months, 1) if payback_months < 900 else 999,
            monthly_co2=monthly_co2,
        )
    
    @staticmethod
    def compare_strategies(fleet_size: int, current_refresh_years: int = 4,
                           current_refurb_rate: float = 0.0,
                           target_reduction: float = 0.20,
                           time_horizon_months: int = 36) -> List[StrategyProjection]:
        """Compare all strategies and return ranked list."""
        
        # Estimate averages from DEVICES
        avg_value = sum(d["price_new_eur"] for d in DEVICES.values()) / len(DEVICES)
        avg_co2 = sum(d["co2_manufacturing_kg"] / (d["lifespan_months"]/12) for d in DEVICES.values()) / len(DEVICES)
        
        results = []
        for strategy_key in STRATEGIES:
            projection = StrategySimulator.simulate_strategy(
                strategy_key=strategy_key,
                fleet_size=fleet_size,
                current_refresh_years=current_refresh_years,
                current_refurb_rate=current_refurb_rate,
                average_device_value=avg_value,
                average_co2_per_device=avg_co2,
                target_reduction=target_reduction,
                time_horizon_months=time_horizon_months,
            )
            results.append(projection)
        
        # Sort by months_to_target (ascending), then by ROI (descending)
        results.sort(key=lambda x: (x.months_to_target, -x.roi_year1))
        
        return results


# =============================================================================
# FLEET ANALYZER
# =============================================================================

class FleetAnalyzer:
    """Analyzes entire device fleets from CSV data."""
    
    @staticmethod
    def analyze_fleet(fleet_data: List[Dict], optimization_goal: str = "balanced") -> List[DeviceAnalysis]:
        """Analyze all devices in a fleet."""
        results = []
        
        for device in fleet_data:
            device_name = device.get("Device_Model", "Laptop (Standard)")
            age = float(device.get("Age_Years", 3))
            persona = device.get("Persona", "Admin Normal (HR/Finance)")
            country = device.get("Country", "FR")
            
            # Validate device exists
            if device_name not in DEVICES:
                device_name = "Laptop (Standard)"
            
            # Validate persona exists
            if persona not in PERSONAS:
                persona = "Admin Normal (HR/Finance)"
            
            analysis = RecommendationEngine.analyze_device(
                device_name=device_name,
                age_years=age,
                persona=persona,
                country=country,
                optimization_goal=optimization_goal,
            )
            
            analysis.maison = device.get("Maison", "")
            results.append(analysis)
        
        return results
    
    @staticmethod
    def summarize_fleet(analyses: List[DeviceAnalysis]) -> Dict:
        """Generate summary statistics for a fleet analysis."""
        total = len(analyses)
        if total == 0:
            return {"total_devices": 0}
        
        by_recommendation = {"KEEP": 0, "NEW": 0, "REFURBISHED": 0}
        by_urgency = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for a in analyses:
            if a.recommendation in by_recommendation:
                by_recommendation[a.recommendation] += 1
            by_urgency[a.urgency] += 1
        
        total_savings = sum(a.annual_savings for a in analyses)
        total_co2_savings = sum(a.co2_savings for a in analyses)
        total_residual = sum(a.residual_value for a in analyses)
        
        # By Maison
        by_maison = {}
        for a in analyses:
            maison = a.maison or 'Unknown'
            if maison not in by_maison:
                by_maison[maison] = {"count": 0, "savings": 0, "co2": 0, "high_urgency": 0}
            by_maison[maison]["count"] += 1
            by_maison[maison]["savings"] += a.annual_savings
            by_maison[maison]["co2"] += a.co2_savings
            if a.urgency == "HIGH":
                by_maison[maison]["high_urgency"] += 1
        
        return {
            "total_devices": total,
            "by_recommendation": by_recommendation,
            "by_urgency": by_urgency,
            "total_annual_savings_eur": round(total_savings, 2),
            "total_co2_savings_kg": round(total_co2_savings, 2),
            "total_recoverable_value_eur": round(total_residual, 2),
            "by_maison": by_maison,
        }


# =============================================================================
# DEMO DATA GENERATOR
# =============================================================================

def generate_demo_fleet(n_devices: int = 50, seed: int = 42) -> List[Dict]:
    """Generate realistic demo fleet data."""
    import random
    random.seed(seed)
    
    # Device distribution (weighted)
    device_choices = [
        ("Laptop (Standard)", 0.35),
        ("Smartphone (Generic)", 0.25),
        ("iPhone 14 (Alternative)", 0.10),
        ("Tablet", 0.10),
        ("Scanner (Logistics)", 0.08),
        ("Workstation", 0.05),
        ("Screen (Monitor)", 0.05),
        ("Switch/Router", 0.02),
    ]
    devices = [d[0] for d in device_choices]
    weights = [d[1] for d in device_choices]
    
    # Age distribution (normal, centered at 3.5 years)
    def random_age():
        age = random.gauss(3.5, 1.2)
        return max(0.5, min(7, age))
    
    # Persona distribution
    persona_choices = list(PERSONAS.keys())
    persona_weights = [0.40, 0.35, 0.10, 0.15]
    
    # Country distribution
    country_choices = ["FR", "FR", "FR", "US", "US", "CN", "CN", "JP", "DE", "IT", "UK", "HK"]
    
    # Maison distribution
    maison_choices = list(MAISONS.keys())
    maison_weights = [MAISONS[m]["estimated_fleet_size"] for m in maison_choices]
    total_weight = sum(maison_weights)
    maison_weights = [w/total_weight for w in maison_weights]
    
    fleet = []
    for _ in range(n_devices):
        fleet.append({
            "Device_Model": random.choices(devices, weights=weights)[0],
            "Age_Years": round(random_age(), 1),
            "Persona": random.choices(persona_choices, weights=persona_weights)[0],
            "Country": random.choice(country_choices),
            "Maison": random.choices(maison_choices, weights=maison_weights)[0],
        })
    
    return fleet