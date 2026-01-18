"""
Élysia - Calculator Module
===========================
LVMH · Sustainable IT Intelligence

All calculation logic with documented mathematical formulas.
Every formula includes source documentation for transparency.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from reference_data_API import (
    DEVICES, PERSONAS, PRICE_KWH_EUR, PRODUCTIVITY_CONFIG, REFURB_CONFIG,
    URGENCY_CONFIG, URGENCY_THRESHOLDS, STRATEGIES, AVERAGES, LIFE_360,
    FLEET_SIZE_OPTIONS, FLEET_AGE_OPTIONS, DEPRECIATION_BASE,
    get_grid_factor, get_depreciation_rate, is_premium_device,
    PREMIUM_RETENTION_BONUS, get_disposal_cost, calculate_stranded_value,
    calculate_avoidable_co2
)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ShockMetrics:
    """Metrics for Act 1: The Shock - showing cost of inaction."""
    stranded_value_eur: float
    avoidable_co2_tonnes: float
    deadline_status: str  # "WILL MISS" or "AT RISK"
    
    # Calculation details for transparency
    stranded_calculation: Dict = field(default_factory=dict)
    co2_calculation: Dict = field(default_factory=dict)


@dataclass
class HopeMetrics:
    """Metrics for Act 2: The Hope - showing what's possible."""
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
    
    # Key metrics
    co2_savings_tonnes: float
    co2_reduction_pct: float
    cost_savings_eur: float
    time_to_target_months: float
    reaches_target: bool
    
    # Financial
    implementation_cost_eur: float
    annual_savings_eur: float
    payback_months: float
    roi_3year: float
    
    # Trajectory for charting
    monthly_co2: List[float] = field(default_factory=list)
    
    # Calculation details
    calculation_details: Dict = field(default_factory=dict)


@dataclass
class DeviceRecommendation:
    """Recommendation for a single device."""
    device_name: str
    age_years: float
    persona: str
    country: str
    
    recommendation: str  # "KEEP", "REFURBISHED", "NEW"
    urgency: str  # "HIGH", "MEDIUM", "LOW"
    urgency_score: float
    
    # Costs
    tco_keep: float
    tco_new: float
    tco_refurb: Optional[float]
    annual_savings: float
    
    # CO2
    co2_keep: float
    co2_new: float
    co2_refurb: Optional[float]
    co2_savings: float
    
    # Other
    residual_value: float
    productivity_loss_pct: float
    rationale: str


# =============================================================================
# SHOCK CALCULATOR (Act 1)
# =============================================================================

class ShockCalculator:
    """
    Calculates the "cost of inaction" metrics for Act 1.
    
    Shows users what they're losing by doing nothing:
    - Stranded value (€)
    - Avoidable CO2 (tonnes)
    - Whether they'll miss 2026 deadline
    """
    
    @staticmethod
    def calculate(fleet_size: int, avg_age: float = 3.5, 
                  refresh_cycle: int = 4, target_pct: float = -20) -> ShockMetrics:
        """
        Calculate shock metrics based on fleet size and age.
        
        Args:
            fleet_size: Number of devices
            avg_age: Average age in years
            refresh_cycle: Current refresh cycle in years
            target_pct: Target CO2 reduction (e.g., -20 for -20%)
        
        Returns:
            ShockMetrics with all values and calculations
        """
        # 1. Stranded Value
        stranded = calculate_stranded_value(fleet_size, avg_age)
        stranded_value = stranded["value"]
        
        # 2. Avoidable CO2 (assuming 40% refurb adoption is possible)
        avoidable = calculate_avoidable_co2(fleet_size, refresh_cycle, refurb_rate=0.40)
        avoidable_co2 = avoidable["value_tonnes"]
        
        # 3. Deadline Status
        # Calculate if doing nothing will reach target
        current_annual_co2 = fleet_size * AVERAGES["device_co2_annual_kg"] / 1000  # tonnes
        target_co2 = current_annual_co2 * (1 + target_pct / 100)
        
        # With "do nothing", no CO2 reduction happens
        deadline_status = "WILL MISS" if target_pct < 0 else "ON TRACK"
        
        return ShockMetrics(
            stranded_value_eur=stranded_value,
            avoidable_co2_tonnes=avoidable_co2,
            deadline_status=deadline_status,
            stranded_calculation=stranded["calculation"],
            co2_calculation=avoidable["calculation"]
        )


# =============================================================================
# HOPE CALCULATOR (Act 2)
# =============================================================================

class HopeCalculator:
    """
    Calculates the "what's possible" metrics for Act 2.
    
    Shows the Before/After comparison:
    - Current state (CO2, cost)
    - Optimized state with Élysia strategy
    """
    
    @staticmethod
    def calculate(fleet_size: int, avg_age: float = 3.5,
                  refresh_cycle: int = 4, target_pct: float = -20,
                  strategy_key: str = "refurb_40") -> HopeMetrics:
        """
        Calculate hope metrics comparing current vs optimized state.
        
        Args:
            fleet_size: Number of devices
            avg_age: Average age in years
            refresh_cycle: Current refresh cycle in years
            target_pct: Target CO2 reduction percentage
            strategy_key: Which strategy to show as "optimized"
        
        Returns:
            HopeMetrics with before/after comparison
        """
        strategy = STRATEGIES.get(strategy_key, STRATEGIES["refurb_40"])
        
        # Current state calculations
        annual_replacements = fleet_size / refresh_cycle
        
        # Current CO2 (all new devices)
        # Formula: (Replacements × Manufacturing CO2) + (Fleet × Usage CO2)
        manufacturing_co2 = annual_replacements * AVERAGES["device_co2_manufacturing_kg"]
        usage_co2 = fleet_size * AVERAGES["device_co2_annual_kg"]
        current_co2_kg = manufacturing_co2 + usage_co2
        current_co2_tonnes = current_co2_kg / 1000
        
        # Current cost
        # Formula: Replacements × New Price + Productivity Loss
        current_equipment_cost = annual_replacements * AVERAGES["device_price_eur"]
        
        # Productivity loss from aging devices
        backlog_pct = max(0, (avg_age - 3) * 0.10)  # 10% more backlog per year over 3
        backlog_devices = fleet_size * backlog_pct
        productivity_loss = backlog_devices * 0.03 * AVERAGES["salary_eur"]  # 3% productivity loss
        
        current_cost = current_equipment_cost + productivity_loss
        
        # Optimized state calculations
        new_lifecycle = strategy["lifecycle_years"]
        refurb_rate = strategy["refurb_rate"]
        
        # New replacements volume
        new_annual_replacements = fleet_size / new_lifecycle
        
        # New CO2
        # Formula: (New devices × full CO2) + (Refurb devices × 20% CO2) + Usage
        new_devices = new_annual_replacements * (1 - refurb_rate)
        refurb_devices = new_annual_replacements * refurb_rate
        
        new_manufacturing_co2 = new_devices * AVERAGES["device_co2_manufacturing_kg"]
        refurb_manufacturing_co2 = refurb_devices * AVERAGES["device_co2_manufacturing_kg"] * (1 - REFURB_CONFIG["co2_savings_rate"])
        optimized_co2_kg = new_manufacturing_co2 + refurb_manufacturing_co2 + usage_co2
        optimized_co2_tonnes = optimized_co2_kg / 1000
        
        # Optimized cost
        # Formula: (New × New Price) + (Refurb × Refurb Price) + Reduced Productivity Loss
        new_cost = new_devices * AVERAGES["device_price_eur"]
        refurb_cost = refurb_devices * AVERAGES["device_price_eur"] * REFURB_CONFIG["price_ratio"]
        reduced_productivity_loss = productivity_loss * 0.5  # Assume 50% reduction with better fleet
        
        optimized_cost = new_cost + refurb_cost + reduced_productivity_loss
        
        # Calculate reductions
        co2_reduction_pct = ((current_co2_tonnes - optimized_co2_tonnes) / current_co2_tonnes) * 100
        cost_savings = current_cost - optimized_cost
        cost_reduction_pct = (cost_savings / current_cost) * 100 if current_cost > 0 else 0
        
        # Time to target
        target_co2 = current_co2_tonnes * (1 + target_pct / 100)
        co2_gap = current_co2_tonnes - target_co2
        annual_co2_savings = current_co2_tonnes - optimized_co2_tonnes
        monthly_savings = annual_co2_savings / 12
        
        if monthly_savings > 0:
            months_to_target = int(co2_gap / monthly_savings)
            reaches_target = months_to_target <= 36  # Within 3 years
        else:
            months_to_target = 999
            reaches_target = False
        
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


# =============================================================================
# STRATEGY SIMULATOR (Act 4)
# =============================================================================

class StrategySimulator:
    """
    Simulates different strategies and projects outcomes over time.
    
    Used to compare all strategies and recommend the best one.
    """
    
    @staticmethod
    def simulate_strategy(strategy_key: str, fleet_size: int,
                          current_refresh: int = 4, avg_age: float = 3.5,
                          target_pct: float = -20,
                          time_horizon_months: int = 36) -> StrategyResult:
        """
        Simulate a single strategy and project monthly outcomes.
        
        Args:
            strategy_key: Key from STRATEGIES dict
            fleet_size: Number of devices
            current_refresh: Current refresh cycle in years
            avg_age: Current average device age
            target_pct: Target CO2 reduction (negative number)
            time_horizon_months: How far to project
        
        Returns:
            StrategyResult with all metrics and monthly trajectory
        """
        strategy = STRATEGIES.get(strategy_key)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_key}")
        
        # Current state
        annual_replacements_current = fleet_size / current_refresh
        current_manufacturing_co2 = annual_replacements_current * AVERAGES["device_co2_manufacturing_kg"]
        current_usage_co2 = fleet_size * AVERAGES["device_co2_annual_kg"]
        current_annual_co2_kg = current_manufacturing_co2 + current_usage_co2
        current_annual_co2_tonnes = current_annual_co2_kg / 1000
        
        current_annual_cost = annual_replacements_current * AVERAGES["device_price_eur"]
        
        # New state with strategy
        new_lifecycle = strategy["lifecycle_years"]
        refurb_rate = strategy["refurb_rate"]
        
        annual_replacements_new = fleet_size / new_lifecycle
        new_devices = annual_replacements_new * (1 - refurb_rate)
        refurb_devices = annual_replacements_new * refurb_rate
        
        # New CO2
        new_manufacturing_co2 = new_devices * AVERAGES["device_co2_manufacturing_kg"]
        refurb_manufacturing_co2 = refurb_devices * AVERAGES["device_co2_manufacturing_kg"] * 0.20  # 80% savings
        new_annual_co2_kg = new_manufacturing_co2 + refurb_manufacturing_co2 + current_usage_co2
        new_annual_co2_tonnes = new_annual_co2_kg / 1000
        
        # New cost
        new_cost = new_devices * AVERAGES["device_price_eur"]
        refurb_cost = refurb_devices * AVERAGES["device_price_eur"] * REFURB_CONFIG["price_ratio"]
        new_annual_cost = new_cost + refurb_cost
        
        # Calculate savings
        co2_savings_tonnes = current_annual_co2_tonnes - new_annual_co2_tonnes
        co2_reduction_pct = (co2_savings_tonnes / current_annual_co2_tonnes) * 100 if current_annual_co2_tonnes > 0 else 0
        cost_savings = current_annual_cost - new_annual_cost
        
        # Target calculation
        target_co2 = current_annual_co2_tonnes * (1 + target_pct / 100)
        co2_gap = current_annual_co2_tonnes - target_co2
        
        # Monthly trajectory
        monthly_co2 = []
        current_co2 = current_annual_co2_tonnes
        months_to_target = None
        implementation_months = strategy.get("implementation_months", 6)
        
        for month in range(time_horizon_months + 1):
            monthly_co2.append(current_co2)
            
            # Check if target reached
            if current_co2 <= target_co2 and months_to_target is None:
                months_to_target = month
            
            # Apply reduction with ramp-up during implementation
            if month < implementation_months:
                ramp_factor = month / implementation_months
            else:
                ramp_factor = 1.0
            
            monthly_reduction = (co2_savings_tonnes / 12) * ramp_factor
            current_co2 = max(new_annual_co2_tonnes, current_co2 - monthly_reduction)
        
        reaches_target = months_to_target is not None
        if not reaches_target:
            months_to_target = 999
        
        # Financial calculations
        implementation_cost = fleet_size * 10 * (refurb_rate + 0.02)  # €10/device base + refurb setup
        annual_savings = cost_savings
        
        if annual_savings > 0 and implementation_cost > 0:
            payback_months = (implementation_cost / annual_savings) * 12
            roi_3year = ((annual_savings * 3) - implementation_cost) / implementation_cost
        else:
            payback_months = 999
            roi_3year = 0
        
        return StrategyResult(
            strategy_key=strategy_key,
            strategy_name=strategy["name"],
            description=strategy["description"],
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
    
    @staticmethod
    def compare_all_strategies(fleet_size: int, current_refresh: int = 4,
                               avg_age: float = 3.5, target_pct: float = -20,
                               time_horizon_months: int = 36) -> List[StrategyResult]:
        """
        Compare all available strategies and return ranked list.
        
        Ranking criteria:
        1. Reaches target (True before False)
        2. Time to target (ascending)
        3. ROI (descending)
        """
        results = []
        
        for strategy_key in STRATEGIES:
            result = StrategySimulator.simulate_strategy(
                strategy_key=strategy_key,
                fleet_size=fleet_size,
                current_refresh=current_refresh,
                avg_age=avg_age,
                target_pct=target_pct,
                time_horizon_months=time_horizon_months
            )
            results.append(result)
        
        # Sort: reaches_target (True first), then time_to_target (asc), then ROI (desc)
        results.sort(key=lambda x: (
            not x.reaches_target,  # True sorts before False
            x.time_to_target_months,
            -x.roi_3year
        ))
        
        return results
    
    @staticmethod
    def get_recommended_strategy(fleet_size: int, current_refresh: int = 4,
                                 avg_age: float = 3.5, target_pct: float = -20,
                                 priority: str = "balanced") -> StrategyResult:
        """
        Get the best recommended strategy based on priority.
        
        Args:
            priority: "cost" | "co2" | "speed" | "balanced"
        
        Returns:
            Best StrategyResult for the given priority
        """
        results = StrategySimulator.compare_all_strategies(
            fleet_size, current_refresh, avg_age, target_pct
        )
        
        # Filter out "do_nothing"
        viable = [r for r in results if r.strategy_key != "do_nothing"]
        
        if not viable:
            return results[0]
        
        if priority == "cost":
            # Maximize cost savings
            return max(viable, key=lambda x: x.cost_savings_eur)
        elif priority == "co2":
            # Maximize CO2 reduction
            return max(viable, key=lambda x: x.co2_reduction_pct)
        elif priority == "speed":
            # Minimize time to target
            viable_reaching = [r for r in viable if r.reaches_target]
            if viable_reaching:
                return min(viable_reaching, key=lambda x: x.time_to_target_months)
            return viable[0]
        else:
            # Balanced: best that reaches target, or highest ROI if none reach
            reaching = [r for r in viable if r.reaches_target]
            if reaching:
                return max(reaching, key=lambda x: x.roi_3year)
            return max(viable, key=lambda x: x.roi_3year)


# =============================================================================
# TCO CALCULATOR (Device-Level)
# =============================================================================

class TCOCalculator:
    """
    Total Cost of Ownership Calculator for individual devices.
    
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
        Calculate annual energy cost.
        
        Formula: Energy_Cost = Power_kW × Hours_Annual × Price_kWh
        """
        device = DEVICES.get(device_name)
        persona_data = PERSONAS.get(persona)
        if not device or not persona_data:
            return 0.0
        
        daily_hours = persona_data["daily_hours"]
        annual_hours = daily_hours * AVERAGES["working_days_per_year"]
        power_kw = device["power_kw"]
        
        return round(power_kw * annual_hours * PRICE_KWH_EUR, 2)
    
    @staticmethod
    def calculate_productivity_loss(device_name: str, age_years: float, 
                                    persona: str) -> Tuple[float, float]:
        """
        Calculate productivity loss from aging device.
        
        Formula:
        If age > optimal_years:
            Loss_Pct = min((age - optimal) × degradation_rate, max_degradation)
            Loss_Cost = Salary × Loss_Pct × Lag_Sensitivity
        
        Returns: (loss_percentage, loss_cost_eur)
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
        Calculate current residual value of device.
        
        Formula: Residual = Price_New × (0.70)^age × (1 + Premium_Bonus)
        """
        device = DEVICES.get(device_name)
        if not device:
            return 0.0
        
        price_new = device["price_new_eur"]
        remaining_pct = get_depreciation_rate(age_years)
        
        if is_premium_device(device_name):
            remaining_pct = min(remaining_pct * (1 + PREMIUM_RETENTION_BONUS), 1.0)
        
        return round(price_new * remaining_pct, 2)
    
    @staticmethod
    def calculate_tco_keep(device_name: str, age_years: float, 
                          persona: str, country: str) -> Dict:
        """Calculate TCO for keeping the current device one more year."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}, "productivity_loss_pct": 0}
        
        energy_cost = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(
            device_name, age_years, persona
        )
        
        # Residual value loss over one year
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
        """Calculate annualized TCO for buying a new device."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        lifespan_years = device["lifespan_months"] / 12
        annual_purchase = device["price_new_eur"] / lifespan_years
        energy_cost = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        disposal_cost = get_disposal_cost(device_name) / lifespan_years
        
        # Residual benefit at end of year 1
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
        """Calculate annualized TCO for buying a refurbished device."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}, "available": False}
        
        if not device.get("refurb_available", False):
            return {"total": float('inf'), "breakdown": {}, "available": False}
        
        # Refurb pricing and lifespan
        price_refurb = device["price_new_eur"] * REFURB_CONFIG["price_ratio"]
        lifespan_years = REFURB_CONFIG["warranty_years"]
        annual_purchase = price_refurb / lifespan_years
        
        # Energy (10% penalty for older tech)
        base_energy = TCOCalculator.calculate_energy_cost(device_name, persona, country)
        energy_cost = base_energy * (1 + REFURB_CONFIG["energy_penalty"])
        
        # Minor productivity loss (refurb equivalent to 1.5 year old)
        loss_pct, productivity_cost = TCOCalculator.calculate_productivity_loss(
            device_name, REFURB_CONFIG["equivalent_age_years"], persona
        )
        
        disposal_cost = get_disposal_cost(device_name) / lifespan_years
        residual_benefit = price_refurb * 0.15 / lifespan_years  # Lower residual for refurb
        
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
# CO2 CALCULATOR (Device-Level)
# =============================================================================

class CO2Calculator:
    """
    Carbon Footprint Calculator for individual devices.
    
    Formula:
    CO2_annual = (Manufacturing_CO2 / Lifespan_Years) + Usage_CO2
    Usage_CO2 = Power_kW × Hours_Annual × Grid_Factor
    """
    
    @staticmethod
    def calculate_usage_co2(device_name: str, persona: str, country: str) -> float:
        """
        Calculate annual CO2 from device usage (operational emissions).
        
        Formula: Usage_CO2 = Power_kW × Hours_Annual × Grid_Factor
        """
        device = DEVICES.get(device_name)
        persona_data = PERSONAS.get(persona)
        if not device or not persona_data:
            return 0.0
        
        daily_hours = persona_data["daily_hours"]
        annual_hours = daily_hours * AVERAGES["working_days_per_year"]
        power_kw = device["power_kw"]
        grid_factor = get_grid_factor(country)
        
        # Grid factor is in kg CO2/kWh
        return round(power_kw * annual_hours * grid_factor, 2)
    
    @staticmethod
    def calculate_co2_keep(device_name: str, persona: str, country: str) -> Dict:
        """CO2 for keeping current device (manufacturing already emitted)."""
        usage_co2 = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        return {
            "total": round(usage_co2, 2),
            "breakdown": {
                "manufacturing": 0,  # Already emitted in past
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
        """Annual CO2 for refurbished device (80% less manufacturing CO2)."""
        device = DEVICES.get(device_name)
        if not device:
            return {"total": 0, "breakdown": {}}
        
        if not device.get("refurb_available", False):
            return {"total": float('inf'), "breakdown": {}, "available": False}
        
        lifespan_years = REFURB_CONFIG["warranty_years"]
        
        # 80% reduction in manufacturing CO2
        manufacturing_refurb = device["co2_manufacturing_kg"] * (1 - REFURB_CONFIG["co2_savings_rate"])
        manufacturing_annual = manufacturing_refurb / lifespan_years
        
        # Usage with 10% energy penalty
        usage_base = CO2Calculator.calculate_usage_co2(device_name, persona, country)
        usage_annual = usage_base * (1 + REFURB_CONFIG["energy_penalty"])
        
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
    Urgency Scoring based on ITIL v4 Framework.
    
    Score = Base + Age_Factor + Performance_Factor + Sensitivity_Factor
    """
    
    @staticmethod
    def calculate(device_name: str, age_years: float, 
                  persona: str) -> Tuple[float, str, str]:
        """
        Calculate urgency score for a device.
        
        Returns: (score, level, rationale)
        """
        score = 1.0
        factors = []
        
        # Age factor
        if age_years >= URGENCY_CONFIG["age_critical_years"]:
            score += 1.5
            factors.append(f"Age ({age_years:.1f}y) exceeds critical threshold ({URGENCY_CONFIG['age_critical_years']}y)")
        elif age_years >= URGENCY_CONFIG["age_high_years"]:
            score += 0.8
            factors.append(f"Age ({age_years:.1f}y) above recommended ({URGENCY_CONFIG['age_high_years']}y)")
        
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
    """
    Generates device-level recommendations based on TCO and CO2 analysis.
    """
    
    @staticmethod
    def analyze_device(device_name: str, age_years: float, persona: str,
                       country: str, priority: str = "balanced") -> DeviceRecommendation:
        """
        Complete analysis for a single device.
        
        Args:
            device_name: Name of device from DEVICES
            age_years: Current age of device
            persona: Persona from PERSONAS
            country: Country code for grid factor
            priority: "balanced" | "cost" | "co2"
        
        Returns:
            DeviceRecommendation with all analysis
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
        urgency_score, urgency_level, urgency_rationale = UrgencyCalculator.calculate(
            device_name, age_years, persona
        )
        
        # Calculate residual value
        residual = TCOCalculator.calculate_residual_value(device_name, age_years)
        
        # Build options
        refurb_available = tco_refurb.get("available", False)
        
        options = {
            "KEEP": {"tco": tco_keep["total"], "co2": co2_keep["total"]},
            "NEW": {"tco": tco_new["total"], "co2": co2_new["total"]},
        }
        if refurb_available:
            options["REFURBISHED"] = {"tco": tco_refurb["total"], "co2": co2_refurb["total"]}
        
        # Score options
        max_tco = max(o["tco"] for o in options.values()) or 1
        max_co2 = max(o["co2"] for o in options.values()) or 1
        
        scores = {}
        for opt, data in options.items():
            if priority == "cost":
                scores[opt] = data["tco"]
            elif priority == "co2":
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
            savings = tco_new["total"] - tco_refurb["total"]
            co2_saved = co2_new["total"] - co2_refurb["total"]
            rationale = f"Best value: saves €{savings:.0f}/year and {co2_saved:.1f}kg CO2 vs new"
        else:
            rationale = "New device recommended for optimal performance and reliability"
        
        if residual > 50 and best != "KEEP":
            rationale += f". Recoverable value: €{residual:.0f}"
        
        # Calculate savings
        tco_refurb_val = tco_refurb["total"] if refurb_available else float('inf')
        co2_refurb_val = co2_refurb["total"] if refurb_available else float('inf')
        
        best_tco = min(tco_keep["total"], tco_new["total"], tco_refurb_val)
        baseline_tco = tco_keep["total"]
        annual_savings = max(0, baseline_tco - best_tco)
        
        best_co2 = min(co2_keep["total"], co2_new["total"], co2_refurb_val)
        co2_savings = max(0, co2_new["total"] - best_co2) if best != "NEW" else 0
        
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
    """Analyzes entire device fleets from CSV data."""
    
    @staticmethod
    def analyze_fleet(fleet_data: List[Dict], 
                      priority: str = "balanced") -> List[DeviceRecommendation]:
        """
        Analyze all devices in a fleet.
        
        Args:
            fleet_data: List of dicts with device info
            priority: "balanced" | "cost" | "co2"
        
        Returns:
            List of DeviceRecommendation
        """
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
            
            recommendation = RecommendationEngine.analyze_device(
                device_name=device_name,
                age_years=age,
                persona=persona,
                country=country,
                priority=priority
            )
            
            results.append(recommendation)
        
        return results
    
    @staticmethod
    def summarize_fleet(recommendations: List[DeviceRecommendation]) -> Dict:
        """Generate summary statistics for a fleet analysis."""
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
# DEMO DATA GENERATOR
# =============================================================================

def generate_demo_fleet(n_devices: int = 100, seed: int = 42) -> List[Dict]:
    """Generate realistic demo fleet data."""
    import random
    random.seed(seed)
    
    # Device distribution
    device_choices = [
        ("Laptop (Standard)", 0.40),
        ("Smartphone (Generic)", 0.20),
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
        age = random.gauss(3.5, 1.5)
        return max(0.5, min(7, round(age, 1)))
    
    # Persona distribution
    persona_choices = list(PERSONAS.keys())
    persona_weights = [0.35, 0.40, 0.10, 0.15]
    
    # Country distribution (LVMH presence)
    country_choices = ["FR", "FR", "FR", "US", "US", "CN", "CN", "JP", "DE", "IT", "UK"]
    
    fleet = []
    for i in range(n_devices):
        fleet.append({
            "Device_ID": f"DEV-{i+1:04d}",
            "Device_Model": random.choices(devices, weights=weights)[0],
            "Age_Years": random_age(),
            "Persona": random.choices(persona_choices, weights=persona_weights)[0],
            "Country": random.choice(country_choices),
        })
    
    return fleet