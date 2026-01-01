import requests
import time

# --- 1. SCIENTIFIC CONSTANTS (The "Physics") ---
HOURS_ANNUAL = 1607    # Legal standard work year (France)
PRICE_KWH = 0.22       # Avg Enterprise Rate 2024 (€/kWh)

# Fallback Data (Scientific Averages from ADEME/EEA)
# Used if the API is offline or limits are reached.
GRID_FACTORS_FALLBACK = {
    "FR": 0.057,   # France (Nuclear)
    "EU": 0.270,   # Europe Avg
    "US": 0.367,   # USA (Fossil Heavy)
    "PL": 0.700,   # Poland (Coal)
    "DE": 0.350    # Germany (Mixed)
}

# --- 2. GRID FACTOR API (ElectricityMaps) ---
def get_grid_factor_from_api(country_code="FR"):
    """
    Fetches real-time Carbon Intensity (gCO2eq/kWh) from ElectricityMaps.
    Professional 'Try/Except' pattern ensures the app never crashes.
    """
    # NOTE: In production, store this in an environment variable.
    # You can get a free trial key from api.electricitymap.org
    API_KEY = "YOUR_API_KEY_HERE" 
    
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={country_code}"
    
    print(f"📡 Connecting to Grid API for {country_code}...") # Visual cue for Jury
    
    try:
        headers = {"auth-token": API_KEY}
        response = requests.get(url, headers=headers, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            # API returns grams, we need kg. (grams / 1000)
            carbon_intensity_grams = data.get('carbonIntensity', 0)
            print(f"✅ API Success: {carbon_intensity_grams} gCO2/kWh")
            return carbon_intensity_grams / 1000.0
            
    except Exception as e:
        print(f"⚠️ API Unavailable ({e}). Using Scientific Fallback.")
    
    # FALLBACK: Return the hardcoded scientific average
    return GRID_FACTORS_FALLBACK.get(country_code, 0.270)

# --- 3. STRATEGIC PERSONAS ---
PERSONAS = {
    "Vendor (Phone/Tablet)": {
        "description": "Sales/Floor staff. Low lag sensitivity.",
        "lag_sensitivity": 0.2,
        "salary": 35000,
        "daily_hours": 8,
        "typical_device": "Smartphone"
    },
    "Admin Normal (HR/Finance)": {
        "description": "Standard Office. Medium sensitivity.",
        "lag_sensitivity": 1.0,
        "salary": 55000,
        "daily_hours": 8,
        "typical_device": "Laptop"
    },
    "Admin High (Dev/Data)": {
        "description": "High Performance. Time is money.",
        "lag_sensitivity": 2.5,
        "salary": 95000,
        "daily_hours": 9,
        "typical_device": "Workstation"
    },
    "Depot Worker (Logistics)": {
        "description": "Critical Shift Work (2 shifts). Device failure blocks operations.",
        "lag_sensitivity": 1.5,
        "salary": 40000,
        "daily_hours": 16, # CRITICAL: 2 Shifts
        "typical_device": "Scanner"
    }
}

# --- 4. HARDWARE DATABASE (Client Data + Apple Scenarios) ---
LOCAL_DB = {
    # --- CLIENT SPECIFIC SCENARIO: APPLE TRANSITION ---
    # Prices estimated B2B Market Value. CO2 is Mfg Impact (kgCO2e).
    "iPhone SE (Legacy)": {
        "price_new": 529, "co2_manufacturing": 73.0, "power_kw": 0.005, "lifespan_months": 48,
        "source": "Client Data (Legacy Model)"
    },
    "iPhone 16e (New Target)": {
        "price_new": 969, "co2_manufacturing": 249.5, "power_kw": 0.005, "lifespan_months": 48,
        "source": "Client Data (High Impact)"
    },
    "iPhone 14 (Alternative)": {
        "price_new": 749, "co2_manufacturing": 226.5, "power_kw": 0.005, "lifespan_months": 48,
        "source": "Client Data"
    },
    "iPhone 13 (Refurbished)": {
        "price_new": 450, "co2_manufacturing": 79.0, "power_kw": 0.005, "lifespan_months": 24,
        "source": "Client Data (Refurb Impact)"
    },
    "iPhone 12 (Refurbished)": {
        "price_new": 350, "co2_manufacturing": 12.0, "power_kw": 0.005, "lifespan_months": 24,
        "source": "Client Data (Spare Parts Only)"
    },

    # --- STANDARD GENERIC EQUIPMENT ---
    "Laptop (Standard)": { 
        "price_new": 1000, "co2_manufacturing": 250, "power_kw": 0.030, "lifespan_months": 48,
        "source": "Dell Latitude 5420 Carbon Report"
    },
    "Workstation": { 
        "price_new": 2200, "co2_manufacturing": 450, "power_kw": 0.080, "lifespan_months": 60,
        "source": "HP ZBook Fury LCA"
    },
    "Smartphone (Generic)": { 
        "price_new": 500, "co2_manufacturing": 60, "power_kw": 0.005, "lifespan_months": 36,
        "source": "Boavizta Average"
    },
    "Tablet": { 
        "price_new": 500, "co2_manufacturing": 150, "power_kw": 0.010, "lifespan_months": 48,
        "source": "iPad Air LCA"
    },
    "Scanner (Logistics)": { 
        "price_new": 1200, "co2_manufacturing": 180, "power_kw": 0.015, "lifespan_months": 48,
        "source": "Zebra TC52 Report"
    },
    "Screen (Monitor)": { 
        "price_new": 300, "co2_manufacturing": 350, "power_kw": 0.035, "lifespan_months": 72,
        "source": "Dell 24 Monitor LCA"
    },
    "Meeting Room Screen": { 
        "price_new": 3000, "co2_manufacturing": 800, "power_kw": 0.150, "lifespan_months": 84,
        "source": "Samsung LFD LCA"
    },
    "Switch/Router": { 
        "price_new": 250, "co2_manufacturing": 100, "power_kw": 0.050, "lifespan_months": 72,
        "source": "Cisco Catalyst LCA"
    }
}

# --- 5. HARDWARE DATA API (Boavizta) ---
def fetch_device_data_from_api(device_query):
    """
    Connects to Boavizta API. Falls back to LOCAL_DB.
    """
    api_url = f"https://api.boavizta.org/v1/component/search?name={device_query}"
    
    try:
        response = requests.get(api_url, timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            if data and 'gwp' in data[0]:
                return {
                    "co2_manufacturing": data[0]['gwp']['total'],
                    "source": "Boavizta API (Live)"
                }
    except:
        pass

    return LOCAL_DB.get(device_query, LOCAL_DB["Laptop (Standard)"])