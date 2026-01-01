import streamlit as st
import requests
import pandas as pd

# ===============================
# CONFIG & CONSTANTS
# ===============================

# ⚠️ CRITICAL FIX: We comment this out because main.py already sets the config!
# st.set_page_config(
#     page_title="Green IT – Cloud Storage Optimizer",
#     layout="wide"
# )

KWH_PER_GB_PER_YEAR = 1.2  # kWh/GB/year (conservative estimate)
DEFAULT_CARBON_INTENSITY = 400  # gCO2/kWh
ELECTRICITY_MAPS_API_KEY = "PUT_YOUR_API_KEY_HERE"

# Archival savings
ARCHIVAL_CARBON_REDUCTION = 0.70  # 70% carbon reduction for archived data

# Annual data growth
ANNUAL_DATA_GROWTH = 0.10  # 10% per year

# ===============================
# FUNCTIONS
# ===============================
def get_carbon_intensity(country_code):
    """Return carbon intensity in gCO2/kWh; fallback to default."""
    try:
        url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?countryCode={country_code}"
        headers = {"auth-token": ELECTRICITY_MAPS_API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return float(r.json().get("carbonIntensity", DEFAULT_CARBON_INTENSITY))
    except Exception:
        pass
    return DEFAULT_CARBON_INTENSITY

def calculate_annual_emissions(storage_gb, carbon_intensity):
    """Calculate annual CO2 emissions in kg."""
    return storage_gb * KWH_PER_GB_PER_YEAR * carbon_intensity / 1000  # kg CO2

def calculate_archival_needed(current_storage_gb, target_emissions_kg, carbon_intensity, years_ahead):
    """
    Calculate how much data needs to be archived to meet target emissions
    considering data growth over specified years.
    """
    results = []
    
    for year in range(years_ahead + 1):
        # Calculate projected storage with growth
        projected_storage_gb = current_storage_gb * ((1 + ANNUAL_DATA_GROWTH) ** year)
        
        # Calculate emissions without archival
        projected_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        
        # Calculate how much needs to be archived to meet target
        if projected_emissions > target_emissions_kg:
            # excess_emissions = projected_emissions - target_emissions_kg
            # For archived data: emission_reduction = archived_gb * co2_per_gb * ARCHIVAL_CARBON_REDUCTION
            co2_per_gb = calculate_annual_emissions(1, carbon_intensity)
            
            # We need: projected_emissions - (archived_gb * co2_per_gb * ARCHIVAL_CARBON_REDUCTION) = target_emissions_kg
            # Solving for archived_gb:
            archived_gb_needed = (projected_emissions - target_emissions_kg) / (co2_per_gb * ARCHIVAL_CARBON_REDUCTION)
            
            # Can't archive more than we have
            archived_gb_needed = min(archived_gb_needed, projected_storage_gb)
            
            # Calculate actual emissions after archival
            archival_savings = archived_gb_needed * co2_per_gb * ARCHIVAL_CARBON_REDUCTION
            final_emissions = projected_emissions - archival_savings
        else:
            archived_gb_needed = 0
            final_emissions = projected_emissions
        
        results.append({
            "Year": year,
            "Storage (TB)": projected_storage_gb / 1024,
            "Storage (GB)": projected_storage_gb,
            "Emissions w/o Archival (kg)": projected_emissions,
            "Data to Archive (GB)": archived_gb_needed,
            "Data to Archive (TB)": archived_gb_needed / 1024,
            "Emissions After Archival (kg)": final_emissions,
            "Meets Target": "✅" if final_emissions <= target_emissions_kg else "❌"
        })
    
    return pd.DataFrame(results)


