"""
LVMH Green in Tech - Calculator Engine
=======================================

This file contains ALL mathematical and business logic.
No UI code here - just pure calculations.

Author: Green in Tech Team
"""

# Import all data from reference_data_API
try:
    from equipement_audit.reference_data_API import (
        HOURS_ANNUAL, PRICE_KWH,
        DEPRECIATION_CURVE, PREMIUM_BRANDS, PREMIUM_RETENTION_BONUS,
        URGENCY_CONFIG,
        PRODUCTIVITY_CONFIG,
        REFURB_CONFIG,
        GRID_FACTORS_FALLBACK,
        PERSONAS, LOCAL_DB, MAISON_WEIGHTS,
        STRATEGY_CONFIG,
        get_grid_factor_from_api, fetch_device_data_from_api,
    )
except ImportError:
    from reference_data_API import (
        HOURS_ANNUAL, PRICE_KWH,
        DEPRECIATION_CURVE, PREMIUM_BRANDS, PREMIUM_RETENTION_BONUS,
        URGENCY_CONFIG,
        PRODUCTIVITY_CONFIG,
        REFURB_CONFIG,
        GRID_FACTORS_FALLBACK,
        PERSONAS, LOCAL_DB, MAISON_WEIGHTS,
        STRATEGY_CONFIG,
        get_grid_factor_from_api, fetch_device_data_from_api,
    )


# =============================================================================
# 1. TCO CALCULATOR - Core Device Analysis
# =============================================================================

class TCOCalculator:
    """
    Total Cost of Ownership Calculator
    
    Calculates the true annual cost of a device considering:
    - Hardware costs (purchase, disposal)
    - Energy costs
    - Productivity impact
    - Environmental impact
    
    Provides 4 scenarios: KEEP, NEW, REFURB, RESELL
    """
    
    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    
    @staticmethod
    def get_persona(persona_name):
        """
        Safely retrieve persona data with fallback.
        
        Args:
            persona_name: Name of the persona (e.g., "Admin Normal (HR/Finance)")
            
        Returns:
            dict: Persona configuration
        """
        if persona_name in PERSONAS:
            return PERSONAS[persona_name]
        # Fallback to first available
        return list(PERSONAS.values())[0]
    
    @staticmethod
    def get_device(device_name):
        """
        Safely retrieve device data with fallback.
        
        Args:
            device_name: Name of device (e.g., "iPhone 14 (Alternative)")
            
        Returns:
            dict: Device specifications
        """
        if device_name in LOCAL_DB:
            return LOCAL_DB[device_name]
        # Fallback to generic laptop
        return LOCAL_DB.get("Laptop (Standard)", list(LOCAL_DB.values())[0])
    
    @staticmethod
    def get_grid_factor(country_code):
        """
        Get carbon grid factor for a country.
        Tries API first, falls back to stored values.
        
        Args:
            country_code: ISO country code (e.g., "FR", "US")
            
        Returns:
            float: kg CO2 per kWh
        """
        try:
            factor = get_grid_factor_from_api(country_code)
            if factor and factor > 0:
                return factor
        except:
            pass
        return GRID_FACTORS_FALLBACK.get(country_code, 0.270)
    
    # -------------------------------------------------------------------------
    # Core Calculation Methods
    # -------------------------------------------------------------------------
    
    @staticmethod
    def calculate_productivity_loss(age_years, persona):
        """
        Calculate annual productivity loss from device aging.
        
        FORMULA:
        productivity_loss = salary × lag_factor × lag_sensitivity
        
        Where:
        - lag_factor = max(0, (age - 3) × 0.03)  [3% per year after year 3]
        - lag_sensitivity = how much this role is affected (0.2 to 2.5)
        
        EXAMPLE:
        - 5-year-old device for a developer (€95K salary, 2.5 sensitivity)
        - lag_factor = (5 - 3) × 0.03 = 0.06 (6%)
        - productivity_loss = €95,000 × 0.06 × 2.5 = €14,250/year
        
        Args:
            age_years: Device age in years
            persona: Persona dict with salary and lag_sensitivity
            
        Returns:
            tuple: (productivity_loss_eur, lag_factor_decimal)
        """
        # Calculate years past optimal threshold
        years_degraded = max(0, age_years - PRODUCTIVITY_CONFIG["optimal_years"])
        
        # Calculate lag factor (capped at max_degradation)
        lag_factor = min(
            years_degraded * PRODUCTIVITY_CONFIG["degradation_per_year"],
            PRODUCTIVITY_CONFIG["max_degradation"]
        )
        
        # Calculate monetary loss
        salary = persona.get("salary", 45000)
        sensitivity = persona.get("lag_sensitivity", 1.0)
        
        productivity_loss = salary * lag_factor * sensitivity
        
        return productivity_loss, lag_factor
    
    @staticmethod
    def calculate_energy_cost(device, persona, country_code):
        """
        Calculate annual energy cost and carbon footprint.
        
        FORMULA:
        energy_cost = power_kw × hours_per_year × price_per_kwh
        carbon_footprint = power_kw × hours_per_year × grid_factor
        
        EXAMPLE:
        - Laptop: 0.030 kW
        - Usage: 8 hours/day × 220 days = 1,760 hours/year
        - Price: €0.22/kWh
        - energy_cost = 0.030 × 1,760 × 0.22 = €11.62/year
        
        Args:
            device: Device dict with power_kw
            persona: Persona dict with daily_hours
            country_code: ISO country code for grid factor
            
        Returns:
            tuple: (energy_cost_eur, carbon_kg)
        """
        power_kw = device.get("power_kw", 0.030)
        daily_hours = persona.get("daily_hours", 8)
        hours_per_year = daily_hours * 220  # ~220 working days
        
        # Energy cost
        energy_cost = power_kw * hours_per_year * PRICE_KWH
        
        # Carbon footprint
        grid_factor = TCOCalculator.get_grid_factor(country_code)
        carbon_kg = power_kw * hours_per_year * grid_factor
        
        return energy_cost, carbon_kg
    
    @staticmethod
    def calculate_resale_value(device_name, device, age_years):
        """
        Calculate current resale value of a device.
        
        FORMULA:
        resale_value = original_price × depreciation_factor × premium_bonus
        
        DEPRECIATION CURVE (from Gartner):
        - Year 0: 100%
        - Year 1: 70%
        - Year 2: 50%
        - Year 3: 35%
        - Year 4: 20%
        - Year 5+: 10%
        
        EXAMPLE:
        - iPhone 14 (€749), 2 years old
        - depreciation_factor = 0.50
        - premium_bonus = 1.15 (Apple brand)
        - resale_value = €749 × 0.50 × 1.15 = €431
        
        Args:
            device_name: Name of device (to check premium brand)
            device: Device dict with price_new
            age_years: Age in years
            
        Returns:
            float: Resale value in EUR
        """
        price_new = device.get("price_new", 1000)
        
        # Get depreciation factor (cap age at 5)
        age_key = min(int(age_years), 5)
        depreciation = DEPRECIATION_CURVE.get(age_key, 0.10)
        
        # Check for premium brand bonus
        premium_bonus = 1.0
        for brand in PREMIUM_BRANDS:
            if brand in device_name:
                premium_bonus = 1.0 + PREMIUM_RETENTION_BONUS
                break
        
        resale_value = price_new * depreciation * premium_bonus
        
        return resale_value
    
    # -------------------------------------------------------------------------
    # Main Scenario Calculator
    # -------------------------------------------------------------------------
    
    @staticmethod
    def calculate_all_scenarios(device_name, age_years, persona_name, country_code):
        """
        Calculate TCO for all 4 scenarios.
        
        SCENARIOS:
        1. KEEP - Continue using current device
        2. NEW - Buy brand new device
        3. REFURB - Buy refurbished device
        4. RESELL - Sell current device + buy new
        
        Args:
            device_name: Name of device
            age_years: Current age in years
            persona_name: User profile name
            country_code: Country for grid factor
            
        Returns:
            dict: All scenarios with financial and environmental metrics
        """
        # Get data
        device = TCOCalculator.get_device(device_name)
        persona = TCOCalculator.get_persona(persona_name)
        
        # Common calculations
        energy_cost, carbon_operational = TCOCalculator.calculate_energy_cost(
            device, persona, country_code
        )
        
        price_new = device.get("price_new", 1000)
        co2_manufacturing = device.get("co2_manufacturing", 250)
        lifespan_months = device.get("lifespan_months", 48)
        lifespan_years = lifespan_months / 12
        
        disposal_cost = 18.0  # GDPR-compliant data wipe
        
        # =================================================================
        # SCENARIO A: KEEP
        # =================================================================
        # TCO = Energy + Productivity Loss
        # (No hardware cost - already owned)
        
        productivity_loss, lag_factor = TCOCalculator.calculate_productivity_loss(
            age_years, persona
        )
        
        fin_keep = energy_cost + productivity_loss
        env_keep = carbon_operational
        
        # =================================================================
        # SCENARIO B: BUY NEW
        # =================================================================
        # TCO = (Purchase / Lifespan) + Disposal + Energy
        # Carbon = (Manufacturing / Lifespan) + Operational
        
        annual_hardware_cost = price_new / lifespan_years
        
        fin_new = annual_hardware_cost + disposal_cost + energy_cost
        env_new = (co2_manufacturing / lifespan_years) + carbon_operational
        
        # =================================================================
        # SCENARIO C: BUY REFURBISHED
        # =================================================================
        # Price: 45% discount
        # Carbon: 85% reduction in manufacturing
        # Energy: 10% higher (older hardware)
        # Lifespan: Shorter warranty (2 years)
        
        refurb_price = price_new * (1 - REFURB_CONFIG["price_discount"])
        refurb_lifespan = REFURB_CONFIG["warranty_years"]
        refurb_energy = energy_cost * (1 + REFURB_CONFIG["energy_penalty"])
        refurb_co2 = co2_manufacturing * (1 - REFURB_CONFIG["co2_reduction"])
        
        annual_hw_refurb = refurb_price / refurb_lifespan
        
        fin_refurb = annual_hw_refurb + disposal_cost + refurb_energy
        env_refurb = (refurb_co2 / refurb_lifespan) + (carbon_operational * 1.1)
        
        co2_saved_vs_new = env_new - env_refurb
        
        # =================================================================
        # SCENARIO D: RESELL + BUY NEW
        # =================================================================
        # Net Cost = New Price - Resale Value
        # Then amortize over lifespan
        
        resale_value = TCOCalculator.calculate_resale_value(
            device_name, device, age_years
        )
        
        net_hardware_cost = max(0, price_new - resale_value)
        annual_net_cost = net_hardware_cost / lifespan_years
        
        fin_resell = annual_net_cost + disposal_cost + energy_cost
        env_resell = env_new  # Same as NEW (still manufacturing new device)
        
        # =================================================================
        # Return all scenarios
        # =================================================================
        return {
            "KEEP": {
                "fin": round(fin_keep, 2),
                "env": round(env_keep, 2),
                "productivity_loss": round(productivity_loss, 2),
                "lag_pct": round(lag_factor * 100, 1),
                "description": "Continue using current device",
            },
            "NEW": {
                "fin": round(fin_new, 2),
                "env": round(env_new, 2),
                "hardware_cost": round(annual_hardware_cost, 2),
                "description": "Purchase brand new device",
            },
            "REFURB": {
                "fin": round(fin_refurb, 2),
                "env": round(env_refurb, 2),
                "co2_saved": round(co2_saved_vs_new, 2),
                "price": round(refurb_price, 2),
                "description": "Purchase refurbished device",
            },
            "RESELL": {
                "fin": round(fin_resell, 2),
                "env": round(env_resell, 2),
                "resale_value": round(resale_value, 2),
                "net_cost": round(net_hardware_cost, 2),
                "description": "Sell current device, buy new",
            },
        }
    
    # -------------------------------------------------------------------------
    # Recommendation Engine
    # -------------------------------------------------------------------------
    
    @staticmethod
    def get_recommendation(scenarios, financial_weight=0.5, persona_name=""):
        """
        Determine the best scenario based on weighted scoring.
        
        SCORING METHOD:
        1. Normalize financial and environmental scores to 0-1 scale
        2. Apply user's weight preference
        3. Add business risk adjustments
        4. Select lowest score (best option)
        
        Args:
            scenarios: Output from calculate_all_scenarios
            financial_weight: 0.0 (eco-first) to 1.0 (cost-first)
            persona_name: For risk adjustments
            
        Returns:
            tuple: (winner, scores, savings_eur, savings_co2)
        """
        env_weight = 1.0 - financial_weight
        
        keys = ["KEEP", "NEW", "REFURB", "RESELL"]
        fin_values = [scenarios[k]["fin"] for k in keys]
        env_values = [scenarios[k]["env"] for k in keys]
        
        # Normalize to 0-1 (lower is better)
        def normalize(value, all_values):
            min_v, max_v = min(all_values), max(all_values)
            if max_v - min_v < 1:
                return 0.0
            return (value - min_v) / (max_v - min_v)
        
        scores = {}
        for i, key in enumerate(keys):
            norm_fin = normalize(fin_values[i], fin_values)
            norm_env = normalize(env_values[i], env_values)
            
            # Weighted score
            score = (norm_fin * financial_weight) + (norm_env * env_weight)
            
            # Business risk adjustments for REFURB
            if key == "REFURB":
                # High-performance users shouldn't get refurbished
                if "High" in persona_name or "Dev" in persona_name:
                    score += 0.25  # Penalty
                # Depot workers need reliable devices
                if "Depot" in persona_name:
                    score += 0.40  # Higher penalty
            
            scores[key] = round(score, 3)
        
        # Select winner (lowest score)
        winner = min(scores, key=scores.get)
        
        # Inertia rule: Don't change for <5% improvement
        if winner != "KEEP" and scores.get("KEEP", 1) > 0:
            improvement = (scores["KEEP"] - scores[winner]) / scores["KEEP"]
            if improvement < 0.05:
                winner = "KEEP"  # Not worth the hassle
        
        # Calculate savings vs NEW baseline
        savings_eur = scenarios["NEW"]["fin"] - scenarios[winner]["fin"]
        savings_co2 = scenarios["NEW"]["env"] - scenarios[winner]["env"]
        
        return winner, scores, round(savings_eur, 2), round(savings_co2, 2)


# =============================================================================
# 2. URGENCY CALCULATOR
# =============================================================================

class UrgencyCalculator:
    """
    Calculates action urgency based on ITIL v4 framework.
    
    Factors considered:
    - Device age (>5 years = high risk)
    - Performance degradation
    - End-of-support timeline
    """
    
    @staticmethod
    def calculate(age_years, performance_pct=None, eol_months=None):
        """
        Calculate urgency score and priority level.
        
        SCORING:
        - Base score: 1.0
        - Age > 5 years: ×1.5
        - Performance < 70%: ×1.3
        - EOL < 6 months: ×2.0
        
        PRIORITY LEVELS:
        - LOW: score < 1.3
        - MEDIUM: 1.3 ≤ score < 2.0
        - HIGH: score ≥ 2.0
        
        Args:
            age_years: Device age
            performance_pct: Optional performance score (0-1)
            eol_months: Optional months until end-of-support
            
        Returns:
            dict: {score, priority, reasons}
        """
        score = 1.0
        reasons = []
        
        # Age factor
        if age_years >= URGENCY_CONFIG["age_critical_years"]:
            score *= URGENCY_CONFIG["age_multiplier"]
            reasons.append(f"Age ≥{URGENCY_CONFIG['age_critical_years']} years")
        
        # Performance factor
        if performance_pct is not None:
            if performance_pct < URGENCY_CONFIG["performance_threshold"]:
                score *= URGENCY_CONFIG["performance_multiplier"]
                reasons.append(f"Performance <{int(URGENCY_CONFIG['performance_threshold']*100)}%")
        
        # End-of-life factor
        if eol_months is not None:
            if eol_months <= URGENCY_CONFIG["eol_threshold_months"]:
                score *= URGENCY_CONFIG["eol_multiplier"]
                reasons.append(f"EOL in <{URGENCY_CONFIG['eol_threshold_months']} months")
        
        # Determine priority level
        if score >= 2.0:
            priority = "HIGH"
        elif score >= 1.3:
            priority = "MEDIUM"
        else:
            priority = "LOW"
        
        return {
            "score": round(score, 2),
            "priority": priority,
            "reasons": reasons,
        }


# =============================================================================
# 3. STRATEGY SIMULATOR
# =============================================================================

class StrategySimulator:
    """
    Simulates different fleet management strategies and calculates
    time-to-target for CO2 reduction goals.
    
    This answers: "Which strategy gets us to -20% fastest?"
    """
    
    # Available strategies to simulate
    STRATEGIES = [
        {
            "key": "baseline",
            "name": "Do Nothing",
            "description": "Continue current practices with no changes",
            "refurb_rate": 0.0,
            "lifespan_extension": 0,
            "color": "#94a3b8",  # Gray
        },
        {
            "key": "refurb_50",
            "name": "50% Refurbished",
            "description": "Replace 50% of purchases with refurbished devices",
            "refurb_rate": 0.50,
            "lifespan_extension": 0,
            "color": "#22c55e",  # Green
        },
        {
            "key": "refurb_80",
            "name": "80% Refurbished",
            "description": "Aggressive refurbished purchasing for most roles",
            "refurb_rate": 0.80,
            "lifespan_extension": 0,
            "color": "#16a34a",  # Dark green
        },
        {
            "key": "extend_1yr",
            "name": "Extend +1 Year",
            "description": "Extend device lifespan by 1 year before replacement",
            "refurb_rate": 0.0,
            "lifespan_extension": 1,
            "color": "#3b82f6",  # Blue
        },
        {
            "key": "extend_2yr",
            "name": "Extend +2 Years",
            "description": "Extend device lifespan by 2 years before replacement",
            "refurb_rate": 0.0,
            "lifespan_extension": 2,
            "color": "#1d4ed8",  # Dark blue
        },
        {
            "key": "combined",
            "name": "Optimal Combined",
            "description": "50% refurbished + 1 year extension + active resale",
            "refurb_rate": 0.50,
            "lifespan_extension": 1,
            "color": "#8b5cf6",  # Purple
        },
    ]
    
    @staticmethod
    def simulate_strategy(strategy, current_co2, target_pct, fleet_size):
        """
        Simulate a single strategy and calculate time-to-target.
        
        CALCULATION:
        1. Calculate annual CO2 savings from strategy
        2. Divide CO2 gap by monthly savings
        3. Generate 24-month projection
        
        Args:
            strategy: Strategy dict from STRATEGIES
            current_co2: Current annual CO2 in tonnes
            target_pct: Target reduction percentage (e.g., 20 for -20%)
            fleet_size: Number of devices in fleet
            
        Returns:
            dict: Simulation results
        """
        # Calculate target
        target_co2 = current_co2 * (1 - target_pct / 100)
        gap = current_co2 - target_co2
        
        # Get config
        replacement_rate = STRATEGY_CONFIG["replacement_rate"]
        avg_co2 = STRATEGY_CONFIG["avg_device_co2_kg"]
        avg_cost = STRATEGY_CONFIG["avg_device_cost_eur"]
        
        devices_replaced_per_year = fleet_size * replacement_rate
        
        # =================================================================
        # Calculate CO2 savings from refurbished purchasing
        # =================================================================
        # Each refurbished device saves 85% of manufacturing CO2
        refurb_savings_kg = (
            devices_replaced_per_year *
            strategy["refurb_rate"] *
            avg_co2 *
            REFURB_CONFIG["co2_reduction"]
        )
        refurb_savings_tonnes = refurb_savings_kg / 1000
        
        # =================================================================
        # Calculate CO2 savings from lifespan extension
        # =================================================================
        # Extending lifespan reduces replacement rate
        if strategy["lifespan_extension"] > 0:
            extension_factor = 1 + (strategy["lifespan_extension"] * 0.25)
            reduced_rate = replacement_rate / extension_factor
            avoided_replacements = (replacement_rate - reduced_rate) * fleet_size
            extend_savings_tonnes = (avoided_replacements * avg_co2) / 1000
        else:
            avoided_replacements = 0
            extend_savings_tonnes = 0
        
        # =================================================================
        # Total annual savings
        # =================================================================
        total_annual_co2 = refurb_savings_tonnes + extend_savings_tonnes
        monthly_co2 = total_annual_co2 / 12
        
        # Time to target (in months)
        if monthly_co2 > 0:
            months_to_target = gap / monthly_co2
            months_to_target = min(months_to_target, 120)  # Cap at 10 years
        else:
            months_to_target = 999  # Never reaches target
        
        # =================================================================
        # Financial impact
        # =================================================================
        # Refurb saves 45% on hardware
        refurb_financial = (
            devices_replaced_per_year *
            strategy["refurb_rate"] *
            avg_cost *
            REFURB_CONFIG["price_discount"]
        )
        
        # Extension saves replacement costs
        extend_financial = avoided_replacements * avg_cost
        
        total_financial = refurb_financial + extend_financial
        
        # =================================================================
        # Generate monthly projection (24 months)
        # =================================================================
        projection = []
        current = current_co2
        for month in range(25):
            projection.append({
                "month": month,
                "co2": round(current, 2),
                "target": round(target_co2, 2),
                "reached": current <= target_co2,
            })
            current = max(target_co2, current - monthly_co2)
        
        return {
            "key": strategy["key"],
            "name": strategy["name"],
            "description": strategy["description"],
            "months_to_target": round(months_to_target, 1),
            "annual_co2_saved": round(total_annual_co2, 2),
            "annual_eur_saved": round(total_financial, 0),
            "color": strategy["color"],
            "projection": projection,
            "feasible": months_to_target < 60,  # Achievable in 5 years
        }
    
    @staticmethod
    def simulate_all(current_co2, target_pct, fleet_size):
        """
        Simulate all strategies and rank by time-to-target.
        
        Args:
            current_co2: Current annual CO2 in tonnes
            target_pct: Target reduction percentage
            fleet_size: Number of devices
            
        Returns:
            list: Strategies sorted by months_to_target (fastest first)
        """
        results = []
        
        for strategy in StrategySimulator.STRATEGIES:
            result = StrategySimulator.simulate_strategy(
                strategy, current_co2, target_pct, fleet_size
            )
            results.append(result)
        
        # Sort by months to target (fastest first)
        results.sort(key=lambda x: x["months_to_target"])
        
        # Add ranking
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        return results


# =============================================================================
# 4. FLEET ANALYZER
# =============================================================================

class FleetAnalyzer:
    """
    Analyzes entire device fleets and provides aggregated insights.
    """
    
    @staticmethod
    def analyze_device(device_name, age_years, persona_name, country_code="FR"):
        """
        Analyze a single device and return recommendation.
        
        Returns:
            dict: Device analysis with recommendation
        """
        scenarios = TCOCalculator.calculate_all_scenarios(
            device_name, age_years, persona_name, country_code
        )
        
        winner, scores, sav_fin, sav_env = TCOCalculator.get_recommendation(
            scenarios, 0.5, persona_name
        )
        
        urgency = UrgencyCalculator.calculate(age_years)
        
        device = TCOCalculator.get_device(device_name)
        resale = TCOCalculator.calculate_resale_value(device_name, device, age_years)
        
        return {
            "device": device_name,
            "age": age_years,
            "persona": persona_name,
            "recommendation": winner,
            "savings_eur": sav_fin,
            "co2_saved_kg": sav_env,
            "resale_value": round(resale, 2),
            "urgency": urgency["priority"],
            "urgency_score": urgency["score"],
        }
    
    @staticmethod
    def analyze_fleet(fleet_data, country_code="FR"):
        """
        Analyze entire fleet from DataFrame.
        
        Args:
            fleet_data: DataFrame with columns:
                - Device_Model
                - Age_Years
                - Persona
                - Maison (optional)
                
        Returns:
            list: Analysis for each device
        """
        results = []
        
        for _, row in fleet_data.iterrows():
            device = row.get("Device_Model", "Laptop (Standard)")
            age = row.get("Age_Years", 3)
            persona = row.get("Persona", list(PERSONAS.keys())[0])
            maison = row.get("Maison", "Unknown")
            
            analysis = FleetAnalyzer.analyze_device(
                device, age, persona, country_code
            )
            analysis["maison"] = maison
            results.append(analysis)
        
        return results
    
    @staticmethod
    def aggregate_by_maison(fleet_results):
        """
        Aggregate fleet results by Maison.
        
        Returns:
            list: Summary per Maison
        """
        from collections import defaultdict
        
        maison_data = defaultdict(lambda: {
            "devices": 0,
            "total_savings": 0,
            "total_co2": 0,
            "total_resale": 0,
            "ages": [],
        })
        
        for item in fleet_results:
            maison = item["maison"]
            maison_data[maison]["devices"] += 1
            maison_data[maison]["total_savings"] += item["savings_eur"]
            maison_data[maison]["total_co2"] += item["co2_saved_kg"]
            maison_data[maison]["total_resale"] += item["resale_value"]
            maison_data[maison]["ages"].append(item["age"])
        
        results = []
        for maison, data in maison_data.items():
            avg_age = sum(data["ages"]) / len(data["ages"]) if data["ages"] else 0
            weight = MAISON_WEIGHTS.get(maison, {}).get("weight", 1.0)
            
            results.append({
                "maison": maison,
                "devices": data["devices"],
                "avg_age": round(avg_age, 1),
                "total_savings": round(data["total_savings"], 0),
                "total_co2": round(data["total_co2"], 1),
                "total_resale": round(data["total_resale"], 0),
                "priority_score": round(data["total_savings"] * weight / 1000, 2),
            })
        
        # Sort by priority score
        results.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return results


# =============================================================================
# 5. KILLER STAT GENERATOR
# =============================================================================

def generate_killer_stat(fleet_size=45000):
    """
    Generate the memorable pitch statistic.
    
    Returns a dict with:
    - stranded_value: Resale value sitting idle
    - avoidable_co2: CO2 that could be saved
    - devices_to_act: Number needing action
    - months_to_target: Time to reach -20%
    - pitch: Formatted pitch sentence
    """
    avg_cost = STRATEGY_CONFIG["avg_device_cost_eur"]
    avg_co2 = STRATEGY_CONFIG["avg_device_co2_kg"]
    avg_age = 4  # Assume 4-year average age
    
    # Stranded value
    depreciation = DEPRECIATION_CURVE.get(avg_age, 0.20)
    stranded_value = fleet_size * avg_cost * depreciation
    
    # Avoidable CO2 (if 40% went refurb)
    refurb_potential = fleet_size * 0.40
    avoidable_co2 = (refurb_potential * avg_co2 * REFURB_CONFIG["co2_reduction"]) / 1000
    
    # Devices needing action (~30% of fleet)
    devices_to_act = int(fleet_size * 0.30)
    
    # Time to target
    current_co2 = (fleet_size * avg_co2) / 1000
    strategies = StrategySimulator.simulate_all(current_co2, 20, fleet_size)
    best = strategies[0]
    
    pitch = (
        f"LVMH is sitting on €{stranded_value/1e6:.1f}M of stranded value and "
        f"{avoidable_co2:,.0f} tonnes of avoidable CO₂. Our tool identifies exactly which "
        f"{devices_to_act:,} devices to act on, in which order, to capture this within "
        f"{best['months_to_target']:.0f} months."
    )
    
    return {
        "stranded_value": round(stranded_value, 0),
        "avoidable_co2": round(avoidable_co2, 0),
        "devices_to_act": devices_to_act,
        "months_to_target": best["months_to_target"],
        "best_strategy": best["name"],
        "pitch": pitch,
    }