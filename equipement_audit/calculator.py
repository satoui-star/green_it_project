import pandas as pd
# 👇 STRICTLY IMPORTING FROM YOUR API FILE
from reference_data_API import GreenTechAPI, PERSONAS

# --- SCIENTIFIC CONSTANTS ---
ELEC_PRICE_EUR = 0.22         # Avg EU Enterprise rate
GRID_INTENSITY_KG = 0.060     # France/Low-Carbon Mix (kgCO2e/kWh)
WORK_DAYS = 220
MFG_AMORTIZATION_YEARS = 4.0  # Standard accounting & carbon depreciation

class SmartCalculator:

    @staticmethod
    def _calculate_productivity_drag(age_years, sensitivity, device_type):
        """
        Calculates % of productivity lost based on device age.
        CRITICAL FIX: Only 'Compute' devices (Laptops, Phones) cause lag.
        Monitors, Routers, and Landlines do not slow down human thinking.
        """
        # 1. Identify if this is a "Compute" device
        compute_keywords = ["laptop", "smartphone", "tablet", "workstation", "desktop", "mac", "pc"]
        is_compute = any(k in device_type.lower() for k in compute_keywords)

        # 2. If it's a "dumb" device (Screen, Phone), Drag is ALWAYS 0.
        if not is_compute:
            return 0.0

        # 3. Standard Drag Logic for Computers
        if age_years <= 3: base_drag = 0.00      
        elif age_years <= 4: base_drag = 0.03    # 3% lag
        elif age_years <= 5: base_drag = 0.08    # 8% lag
        else: base_drag = 0.15                   # 15% lag
        
        return base_drag * sensitivity

    @staticmethod
    def calculate_line_item(row):
        d_type = row.get('Device Type', 'Laptop')
        age = float(row.get('Age (Years)', 0))
        p_name = row.get('Persona', 'Admin Normal (Std Laptop)')

        # 1. Fetch Real Data via your API Class
        specs = GreenTechAPI.get_device_data(d_type)
        persona = PERSONAS.get(p_name, PERSONAS["Admin Normal (Std Laptop)"])
        
        # --- A. FINANCIAL ANALYSIS (Money) ---
        # "Keep" Scenario (Status Quo)
        # 👇 PASSING DEVICE TYPE HERE TO FIX THE LANDLINE BUG
        drag_impact = SmartCalculator._calculate_productivity_drag(age, persona["lag_sensitivity"], d_type)
        
        productivity_loss_eur = persona["avg_salary"] * drag_impact
        
        daily_hours = persona.get("daily_hours", 8)
        annual_energy_kwh = specs['power_kw'] * daily_hours * WORK_DAYS
        energy_cost_eur = annual_energy_kwh * ELEC_PRICE_EUR
        
        cost_to_keep_fin = productivity_loss_eur + energy_cost_eur
        
        # "Replace" Scenario (Buy New)
        # We amortize the new hardware price over 3 years
        amortized_hardware_cost = specs['price_new'] / 3 
        cost_to_replace_fin = amortized_hardware_cost + energy_cost_eur 
        
        financial_roi = cost_to_keep_fin - cost_to_replace_fin

        # --- B. ENVIRONMENTAL ANALYSIS (Carbon) ---
        # "Keep" Scenario (Scope 2 Only)
        # Keeping an old device incurs 0 manufacturing carbon. It only uses electricity.
        carbon_keep_kg = annual_energy_kwh * GRID_INTENSITY_KG
        
        # "Replace" Scenario (Scope 2 + Amortized Scope 3)
        # Buying new incurs a "Carbon Spike" from manufacturing. We amortize this debt over 4 years.
        amortized_mfg_carbon = specs['co2_manufacturing'] / MFG_AMORTIZATION_YEARS
        carbon_replace_kg = amortized_mfg_carbon + carbon_keep_kg
        
        # Environmental ROI (Positive = Earth wins / Negative = Earth loses)
        environmental_roi = carbon_keep_kg - carbon_replace_kg

        # --- C. DECISION LOGIC ---
        health_penalty = max(0, (age - 3) * 20)
        if drag_impact > 0: health_penalty += 10
        health_score = max(0, 100 - health_penalty)

        if financial_roi > 500:
            action = "🚨 REPLACE"
            logic = "High Productivity Gain"
        elif environmental_roi > 0:
            action = "🚨 REPLACE" 
            logic = "Energy Efficiency Gain"
        elif age > 5:
            action = "⚠️ REVIEW"
            logic = "End of Life Risk"
        else:
            action = "✅ KEEP"
            logic = "Optimal State"

        return {
            "Device Source": specs.get("source", "DB"), 
            "Health": health_score,
            # Financials
            "Prod. Loss (€)": productivity_loss_eur,
            "Fin. Cost Keep (€)": cost_to_keep_fin,
            "Fin. Cost Replace (€)": cost_to_replace_fin,
            "Financial ROI (€)": financial_roi,
            # Environmental
            "Carbon Keep (kg)": carbon_keep_kg,
            "Carbon Replace (kg)": carbon_replace_kg,
            "Env. ROI (kg)": environmental_roi,
            # Meta
            "Action": action,
            "Logic": logic
        }

    @staticmethod
    def process_inventory(df):
        if df.empty: return df
        results = df.apply(SmartCalculator.calculate_line_item, axis=1, result_type='expand')
        return pd.concat([df, results], axis=1)