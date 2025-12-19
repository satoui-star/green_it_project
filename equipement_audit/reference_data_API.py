import requests

# --- 1. PERSONA MATRIX ---
PERSONAS = {
    "Vendor (Phone/Tablet)": {
        "description": "Sales/Floor staff. Low lag sensitivity.",
        "lag_sensitivity": 0.2,
        "target_lifespan_years": 4,
        "avg_salary": 35000,
        "daily_hours": 8,
        "typical_device": "Tablet"
    },
    "Admin Normal (Std Laptop)": {
        "description": "HR, Finance. Medium sensitivity.",
        "lag_sensitivity": 1.0,
        "target_lifespan_years": 5,
        "avg_salary": 55000,
        "daily_hours": 8,
        "typical_device": "Laptop"
    },
    "Admin High (High Spec)": {
        "description": "Dev, Data, Creative. Time is expensive.",
        "lag_sensitivity": 2.5,
        "target_lifespan_years": 3,
        "avg_salary": 95000,
        "daily_hours": 9,
        "typical_device": "Laptop"
    },
    "Depot Worker (Scanner)": {
        "description": "Logistics. Critical Shift Work (2 shifts).",
        "lag_sensitivity": 1.5,
        "target_lifespan_years": 3,
        "avg_salary": 40000,
        "daily_hours": 16, # CRITICAL: Used 16 hours/day
        "typical_device": "Scanner"
    }
}

# --- 2. EQUIPMENT_DB ---
LOCAL_DB = {
    "Laptop": { "price_new": 1000, "lifespan_months": 60, "co2_manufacturing": 250, "power_kw": 0.03 },
    "Smartphone": { "price_new": 500, "lifespan_months": 48, "co2_manufacturing": 60, "power_kw": 0.005 },
    "Screen": { "price_new": 2000, "lifespan_months": 72, "co2_manufacturing": 350, "power_kw": 0.16 },
    "Tablet": { "price_new": 500, "lifespan_months": 60, "co2_manufacturing": 150, "power_kw": 0.01 },
    "Switch/Router": { "price_new": 250, "lifespan_months": 72, "co2_manufacturing": 100, "power_kw": 0.05 },
    "Landline phone": { "price_new": 350, "lifespan_months": 96, "co2_manufacturing": 40, "power_kw": 0.003 },
    "Meeting room screen": { "price_new": 3000, "lifespan_months": 84, "co2_manufacturing": 800, "power_kw": 0.30 },
    "Refurbished smartphone": { "price_new": 1, "lifespan_months": 36, "co2_manufacturing": 10, "power_kw": 0.005 },
    "Refurbished screen": { "price_new": 800, "lifespan_months": 72, "co2_manufacturing": 20, "power_kw": 0.16 },
    "Scanner": { "price_new": 1200, "lifespan_months": 48, "co2_manufacturing": 180, "power_kw": 0.015 },
    "Workstation": { "price_new": 2200, "lifespan_months": 60, "co2_manufacturing": 450, "power_kw": 0.08 }
}

class GreenTechAPI:
    BASE_URL = "https://api.boavizta.org/v1"

    @staticmethod
    def get_device_data(device_type):
        # 1. Fallback for custom items
        if "Refurbished" in device_type or device_type not in ["Laptop", "Smartphone", "Tablet", "Screen"]:
            return GreenTechAPI._get_local(device_type)

        # 2. Try Cloud API
        try:
            api_map = {"Laptop": "laptop", "Smartphone": "smartphone", "Tablet": "tablet", "Screen": "monitor"}
            archetype = api_map.get(device_type)
            
            response = requests.get(
                f"{GreenTechAPI.BASE_URL}/component/{archetype}?verbose=false&duration=1",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                local_data = LOCAL_DB.get(device_type, LOCAL_DB["Laptop"])
                return {
                    "co2_manufacturing": round(data['gwp']['manufacturing'], 1),
                    "power_kw": local_data['power_kw'],
                    "price_new": local_data['price_new'],
                    "lifespan_months": local_data['lifespan_months'],
                    "source": "✅ API (Boavizta)"
                }
        except Exception:
            pass 

        # 3. Final Fallback
        return GreenTechAPI._get_local(device_type)

    @staticmethod
    def _get_local(device_type):
        data = LOCAL_DB.get(device_type, LOCAL_DB["Laptop"])
        data_copy = data.copy()
        data_copy["source"] = "📂 Internal DB"
        return data_copy
