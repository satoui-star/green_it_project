# calculator.py
from reference_data_API import HOURS_ANNUAL, PRICE_KWH, get_grid_factor_from_api, fetch_device_data_from_api, PERSONAS, LOCAL_DB

class SmartCalculator:
    
    @staticmethod
    def get_refurb_alternative(device_name, new_specs):
        mappings = {
            "iPhone 16e (New Target)": "iPhone 12 (Refurbished)",
            "iPhone 14 (Alternative)": "iPhone 13 (Refurbished)",
            "Laptop (Standard)": "Laptop (Refurbished Generic)" 
        }
        
        target_refurb_key = mappings.get(device_name)
        if target_refurb_key and target_refurb_key in LOCAL_DB:
             return LOCAL_DB[target_refurb_key]
             
        return {
            "price_new": new_specs["price_new"] * 0.85, 
            "co2_manufacturing": new_specs["co2_manufacturing"] * 0.15,
            "power_kw": new_specs["power_kw"] * 1.1, 
            "lifespan_months": 24, 
            "source": "Market Projection (Generic)"
        }

    @staticmethod
    def calculate_scenarios(device_name, age_years, persona_name, country_code, secure_wipe_needed):
        """
        Calculates TCO and now adds ROI/Savings metrics.
        """
        # 1. Load Data
        specs_new = fetch_device_data_from_api(device_name)
        specs_refurb = SmartCalculator.get_refurb_alternative(device_name, specs_new)
        persona = PERSONAS[persona_name]
        grid_co2 = get_grid_factor_from_api(country_code)
        
        # 2. Operations
        hours_active = persona["daily_hours"] * 220 
        
        # 3. Disposal / GDPR Cost
        # Renaming the logic internally to be clear
        if "Screen" in device_name: disposal_fee = 8.0
        elif secure_wipe_needed:    disposal_fee = 18.0 # Cost of certified erasure
        else:                       disposal_fee = 14.0 # Standard formatting

        # --- A: KEEP (The Baseline for Savings) ---
        lag_start_year = 3
        lag_factor = max(0, (age_years - lag_start_year) * 0.03) 
        productivity_loss = persona["salary"] * lag_factor * persona["lag_sensitivity"]
        
        energy_cost_keep = specs_new["power_kw"] * hours_active * PRICE_KWH
        carbon_keep = specs_new["power_kw"] * hours_active * grid_co2
        
        fin_keep = energy_cost_keep + productivity_loss
        env_keep = carbon_keep 

        # --- B: BUY NEW (The "Default" Action) ---
        amort_years_new = specs_new["lifespan_months"] / 12
        annual_hw_cost = specs_new["price_new"] / amort_years_new
        
        fin_new = annual_hw_cost + disposal_fee + (specs_new["power_kw"] * hours_active * PRICE_KWH)
        
        annual_mfg_co2 = specs_new["co2_manufacturing"] / amort_years_new
        env_new = annual_mfg_co2 + (specs_new["power_kw"] * hours_active * grid_co2)

        # --- C: BUY REFURB ---
        amort_years_ref = specs_refurb["lifespan_months"] / 12
        annual_hw_ref = specs_refurb["price_new"] / amort_years_ref
        
        fin_refurb = annual_hw_ref + disposal_fee + (specs_refurb["power_kw"] * hours_active * PRICE_KWH)
        
        annual_mfg_ref = specs_refurb["co2_manufacturing"] / amort_years_ref
        env_refurb = annual_mfg_ref + (specs_refurb["power_kw"] * hours_active * grid_co2)

        return {
            "KEEP":   {"fin": fin_keep,   "env": env_keep},
            "NEW":    {"fin": fin_new,    "env": env_new, "details": specs_new},
            "REFURB": {"fin": fin_refurb, "env": env_refurb, "details": specs_refurb}
        }

    @staticmethod
    def get_recommendation(scenarios, fin_weight, persona_name):
        env_weight = 1.0 - fin_weight
        
        # Extract values
        fin_vals = [scenarios["KEEP"]["fin"], scenarios["NEW"]["fin"], scenarios["REFURB"]["fin"]]
        env_vals = [scenarios["KEEP"]["env"], scenarios["NEW"]["env"], scenarios["REFURB"]["env"]]
        keys = ["KEEP", "NEW", "REFURB"]
        scores = {}

        # Normalization
        def normalize(val, all_vals):
            min_v, max_v = min(all_vals), max(all_vals)
            if (max_v - min_v) < 1.0: return 0.0 
            return (val - min_v) / (max_v - min_v)

        for i, key in enumerate(keys):
            n_fin = normalize(fin_vals[i], fin_vals)
            n_env = normalize(env_vals[i], env_vals)
            
            score = (n_fin * fin_weight) + (n_env * env_weight)
            
            # --- BUSINESS RISK FILTERS ---
            if key == "REFURB" and "High" in persona_name: score += 0.25 # Risk Aversion
            if key == "REFURB" and "Depot" in persona_name: score += 0.40 # Reliability Critical

            scores[key] = score

        winner = min(scores, key=scores.get)
        
        # Inertia Rule (Avoid churn for <5% gain)
        if winner != "KEEP" and (scores["KEEP"] - scores[winner]) < 0.05:
            winner = "KEEP"
            
        # --- ROI CALCULATION ---
        # "ROI" here is defined as Savings vs. Buying New (The standard alternative)
        baseline_cost = scenarios["NEW"]["fin"]
        baseline_carbon = scenarios["NEW"]["env"]
        
        winner_cost = scenarios[winner]["fin"]
        winner_carbon = scenarios[winner]["env"]
        
        savings_fin = baseline_cost - winner_cost
        savings_env = baseline_carbon - winner_carbon

        return winner, scores, savings_fin, savings_env