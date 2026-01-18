import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

LITERS_PER_SHOWER = 50

try:
    from cloud import (
        df_cloud, 
        calculate_annual_emissions, 
        calculate_annual_water, 
        calculate_annual_cost, 
        calculate_archival_needed,
        ARCHIVAL_WATER_REDUCTION,
        OLYMPIC_POOL_LITERS,
        CO2_PER_TREE_PER_YEAR
    )
    except ImportError:
        raise ImportError("Missing components. Please ensure the 'cloud' folder contains '__init__.py'.")

def get_cloud_providers():
    return df_cloud['Provider'].unique().tolist()

def calculate_carbon_intensity(selected_providers):
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    std_co2 = filtered['CO2_kg_TB_Month'].iloc[0] if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000
    return carbon_intensity

def calculate_baseline_metrics(storage_gb, carbon_intensity):
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water_liters = calculate_annual_water(storage_gb)
    current_showers = current_water_liters / LITERS_PER_SHOWER
    current_trees = current_emissions / CO2_PER_TREE_PER_YEAR
    
    return {
        'emissions': current_emissions,
        'water_liters': current_water_liters,
        'showers': current_showers,
        'trees': current_trees
    }

def calculate_archival_strategy(storage_gb, reduction_target, data_growth_rate, carbon_intensity, projection_years):
    target_reduction_factor = (1 - reduction_target / 100)
    
    results = []
    for yr in range(1, int(projection_years) + 1):
        projected_storage_gb = storage_gb * ((1 + data_growth_rate / 100) ** yr)
        bau_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        bau_water = calculate_annual_water(projected_storage_gb)
        bau_cost = calculate_annual_cost(projected_storage_gb, 0, 0.022, 0.004)
        
        target_emissions_kg = bau_emissions * target_reduction_factor
        
        co2_per_gb_std = calculate_annual_emissions(1, carbon_intensity)
        archived_gb_needed = (bau_emissions - target_emissions_kg) / (co2_per_gb_std * 0.90)
        archived_gb_needed = min(max(archived_gb_needed, 0), projected_storage_gb)
        
        final_emissions = bau_emissions - (archived_gb_needed * co2_per_gb_std * 0.90)
        final_water = bau_water - (archived_gb_needed * (bau_water / projected_storage_gb) * 0.90)
        final_cost = calculate_annual_cost(projected_storage_gb, archived_gb_needed, 0.022, 0.004)
        
        results.append({
            "Year": yr,
            "Storage (TB)": projected_storage_gb / 1024,
            "Data to Archive (TB)": archived_gb_needed / 1024,
            "Emissions w/o Archival (kg)": bau_emissions,
            "Emissions After Archival (kg)": final_emissions,
            "Water Savings (L)": bau_water - final_water,
            "Cost Savings (€)": bau_cost - final_cost,
            "Meets Target": "✅"
        })
    
    return pd.DataFrame(results)

def calculate_cumulative_savings(archival_df):
    total_co2_no_action = archival_df["Emissions w/o Archival (kg)"].sum()
    total_co2_optimized = archival_df["Emissions After Archival (kg)"].sum()
    total_savings_co2 = total_co2_no_action - total_co2_optimized
    total_savings_euro = archival_df["Cost Savings (€)"].sum()
    total_water_saved_liters = archival_df["Water Savings (L)"].sum()
    
    total_showers_saved = total_water_saved_liters / LITERS_PER_SHOWER
    total_trees_equivalent = total_savings_co2 / CO2_PER_TREE_PER_YEAR
    
    return {
        'co2_saved': total_savings_co2,
        'water_saved': total_water_saved_liters,
        'euro_saved': total_savings_euro,
        'showers_saved': total_showers_saved,
        'trees_equivalent': total_trees_equivalent
    }

