import pandas as pd
import sys
import os

# Ensure the 'cloud' package logic is discoverable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from cloud import (
        df_cloud, 
        calculate_annual_emissions, 
        calculate_annual_water, 
        calculate_annual_cost
    )
except ImportError:
    from __init__ import (
        df_cloud, 
        calculate_annual_emissions, 
        calculate_annual_water, 
        calculate_annual_cost
    )

def perform_cloud_simulation(selected_providers, storage_tb, reduction_target, projection_years, data_growth_rate):
    """
    Core logic engine for the cloud sustainability simulator.
    Separated from UI code to allow for backend testing and clean architecture.
    """
    storage_gb = storage_tb * 1024
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    
    # Calculate Blended Averages for intensities and costs based on provider data
    std_co2 = filtered[filtered['Storage Class'].isin(['Standard', 'Hot'])]['CO2_kg_TB_Month'].mean() if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000
    
    std_cost_tb = filtered[filtered['Storage Class'].isin(['Standard', 'Hot'])]['Price_EUR_TB_Month'].mean() if not filtered.empty else 23.0
    arc_cost_tb = filtered[filtered['Storage Class'].isin(['Glacier', 'Archive'])]['Price_EUR_TB_Month'].mean() if not filtered.empty else 4.0
    
    std_cost_gb = std_cost_tb / 1024
    arc_cost_gb = arc_cost_tb / 1024
    
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water_liters = calculate_annual_water(storage_gb)
    target_reduction_factor = (1 - reduction_target / 100)
    
    results = []
    for yr in range(1, int(projection_years) + 1):
        # Projected BAU Data Growth
        projected_storage_gb = storage_gb * ((1 + data_growth_rate / 100) ** yr)
        bau_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        bau_water = calculate_annual_water(projected_storage_gb)
        bau_cost = calculate_annual_cost(projected_storage_gb, 0, std_cost_gb, arc_cost_gb)
        
        # Calculate Target for each year dynamically vs BAU growth
        target_emissions_kg = bau_emissions * target_reduction_factor
        
        # Archival calculation to reach target
        co2_per_gb_std = calculate_annual_emissions(1, carbon_intensity)
        # Reduction gain assumed at 90% (Archive tier footprint vs Standard)
        archived_gb_needed = (bau_emissions - target_emissions_kg) / (co2_per_gb_std * 0.90)
        archived_gb_needed = min(max(archived_gb_needed, 0), projected_storage_gb)
        
        # Final optimized metrics
        final_emissions = bau_emissions - (archived_gb_needed * co2_per_gb_std * 0.90)
        final_water = bau_water - (archived_gb_needed * (bau_water / projected_storage_gb) * 0.90)
        final_cost = calculate_annual_cost(projected_storage_gb, archived_gb_needed, std_cost_gb, arc_cost_gb)
        
        results.append({
            "Year": yr,
            "Storage (TB)": projected_storage_gb / 1024,
            "Data to Archive (TB)": archived_gb_needed / 1024,
            "Emissions w/o Archival (kg)": bau_emissions,
            "Emissions After Archival (kg)": final_emissions,
            "Water w/o Archival (L)": bau_water,
            "Water After Archival (L)": final_water,
            "Water Savings (L)": bau_water - final_water,
            "Cost Savings (€)": bau_cost - final_cost,
            "Meets Target": "✅"
        })
    
    return {
        "archival_df": pd.DataFrame(results),
        "current_emissions": current_emissions,
        "current_water_liters": current_water_liters,
        "carbon_intensity": carbon_intensity
    }
