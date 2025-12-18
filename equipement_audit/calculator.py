import pandas as pd
import numpy as np

# --- 1. SCIENTIFIC REFERENCE DATABASES ---

# DATABASE COMPLETE (LVMH Specs)
DEVICE_DB = {
    "Laptop": {
        "price_new": 1000,          
        "lifespan_months": 60,      # 5 ans
        "co2_manufacturing": 250,   
        "power_kw": 0.03,           # 30W
    },
    "Smartphone": {
        "price_new": 500,
        "lifespan_months": 48,      # 4 ans
        "co2_manufacturing": 60,
        "power_kw": 0.005,          
    },
    "Screen": {
        "price_new": 2000,          
        "lifespan_months": 72,      # 6 ans
        "co2_manufacturing": 350,
        "power_kw": 0.16,           
    },
    "Tablet": {
        "price_new": 500,
        "lifespan_months": 60,
        "co2_manufacturing": 150,
        "power_kw": 0.01,           
    },
    "Switch/Router": {
        "price_new": 250,
        "lifespan_months": 72,
        "co2_manufacturing": 100,
        "power_kw": 0.05,           
    },
    "Landline phone": {
        "price_new": 350,
        "lifespan_months": 96,      
        "co2_manufacturing": 40,
        "power_kw": 0.003,          
    },
    "Meeting room screen": {
        "price_new": 3000,
        "lifespan_months": 84,      
        "co2_manufacturing": 800,   
        "power_kw": 0.30,           
    },
    # --- REFURBISHED OPTIONS ---
    "Refurbished smartphone": {
        "price_new": 1,             
        "lifespan_months": 36,      
        "co2_manufacturing": 10,    
        "power_kw": 0.005,
    },
    "Refurbished screen": {
        "price_new": 800,
        "lifespan_months": 72,
        "co2_manufacturing": 20,    
        "power_kw": 0.16,
    }
}

# Grid Carbon Intensity (gCO2e / kWh)
GRID_INTENSITY_DB = {
    "France": 58,    # Low (Nuclear)
    "USA": 360,      # Medium (Mixed)
    "China": 550,    # High (Coal heavy)
    "Germany": 350,  # Medium-High
    "Global Average": 475
}

# Electricity Cost (EUR / kWh)
COST_DB = {
    "France": 0.22,
    "USA": 0.18,
    "China": 0.09,
    "Global Average": 0.15
}

class CarbonCalculator:
    @staticmethod
    def calculate_line_item(row):
        """Calculates CO2 and Cost for a single inventory line item using LCA methodology."""
        # 1. Extract Inputs
        device_type = row.get('Device Type', 'Laptop')
        country = row.get('Location', 'Global Average')
        hours_per_day = float(row.get('Daily Hours', 8))
        age_years = float(row.get('Age (Years)', 1))

        # 2. Get Scientific Factors (Fallback to Laptop if unknown)
        device_specs = DEVICE_DB.get(device_type, DEVICE_DB["Laptop"])
        grid_factor = GRID_INTENSITY_DB.get(country, GRID_INTENSITY_DB["Global Average"]) 
        elec_price = COST_DB.get(country, COST_DB["Global Average"]) 

        # 3. Manufacturing Impact (Scope 3)
        mfg_co2 = device_specs['co2_manufacturing']

        # 4. Usage Impact (Scope 2)
        power_kw = device_specs['power_kw'] 
        annual_hours = hours_per_day * 240 # Approx 240 working days
        total_kwh = power_kw * annual_hours * age_years
        
        usage_co2 = (total_kwh * grid_factor) / 1000.0 # Convert grams to kg
        energy_cost = total_kwh * elec_price

        # 5. Financial Value (Depreciation)
        lifespan_years = device_specs['lifespan_months'] / 12.0
        purchase_price = row.get('Purchase Price', device_specs['price_new'])
        
        depreciation_per_year = purchase_price / lifespan_years
        current_value = max(0, purchase_price - (depreciation_per_year * age_years))

        return {
            "Mfg CO2 (kg)": round(mfg_co2, 2),
            "Usage CO2 (kg)": round(usage_co2, 2),
            "Total CO2 (kg)": round(mfg_co2 + usage_co2, 2),
            "Energy Cost (€)": round(energy_cost, 2),
            "Current Value (€)": round(current_value, 2),
            "Status": "End of Life" if age_years > lifespan_years else "Active"
        }

    @staticmethod
    def process_inventory(df):
        """Applies calculation to the whole dataframe"""
        results = df.apply(CarbonCalculator.calculate_line_item, axis=1, result_type='expand')
        return pd.concat([df, results], axis=1)

def get_demo_data():
    """Generates scientifically plausible random inventory for testing."""
    np.random.seed(42)
    devices_list = list(DEVICE_DB.keys())
    
    data = {
        'Device ID': [f"LVMH-{i:04d}" for i in range(1, 51)],
        'Device Type': np.random.choice(devices_list, 50),
        'Location': np.random.choice(list(GRID_INTENSITY_DB.keys()), 50),
        'Age (Years)': np.random.randint(1, 7, 50),
        'Daily Hours': np.random.randint(2, 12, 50),
        'Purchase Price': [] 
    }
    
    # Fill Purchase Price logic
    for dtype in data['Device Type']:
        base_price = DEVICE_DB[dtype]['price_new']
        data['Purchase Price'].append(base_price * np.random.uniform(0.9, 1.1))

    return pd.DataFrame(data)