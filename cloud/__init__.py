import pandas as pd
import io

# ===============================
# CONFIG & CONSTANTS
# ===============================

csv_data = """Provider,Service,Storage Class,Region,Price_EUR_TB_Month,CO2_kg_TB_Month,Intensity
AWS,S3,Standard,EU-West-1,23.0,6.0,Medium
AWS,S3,Infrequent Access,EU-West-1,12.5,4.2,Medium
AWS,S3,Glacier,EU-West-1,4.0,2.0,Low
Azure,Blob Storage,Hot,West Europe,21.5,5.8,Medium
Azure,Blob Storage,Cool,West Europe,10.0,3.9,Medium
Azure,Blob Storage,Archive,West Europe,3.6,1.9,Low
GCP,Cloud Storage,Standard,Europe-West1,20.0,4.5,Low
GCP,Cloud Storage,Nearline,Europe-West1,10.0,3.0,Low
GCP,Cloud Storage,Coldline,Europe-West1,4.0,1.8,Low
GCP,Cloud Storage,Archive,Europe-West1,2.8,1.2,Very Low
Alibaba Cloud,OSS,Standard,Germany (FRA),16.0,4.8,Low
Alibaba Cloud,OSS,Infrequent Access,Germany (FRA),11.0,3.2,Low
Alibaba Cloud,OSS,Archive,Germany (FRA),4.5,1.5,Very Low"""

df_cloud = pd.read_csv(io.StringIO(csv_data))

KWH_PER_GB_PER_YEAR = 1.2  # kWh/GB/year (conservative estimate)

# Water consumption (based on average WUE of 1.9 L/kWh from The Green Grid)
LITERS_PER_GB_PER_YEAR = KWH_PER_GB_PER_YEAR * 1.9  # 2.28 liters/GB/year

# Archival savings (water is fixed at 90%)
ARCHIVAL_WATER_REDUCTION = 0.90  # 90% water reduction for archived data

# Real-world comparisons
OLYMPIC_POOL_LITERS = 2_500_000  # Standard Olympic swimming pool volume
CO2_PER_TREE_PER_YEAR = 22  # kg CO2 absorbed by one mature tree per year

# ===============================
# FUNCTIONS
# ===============================
def calculate_annual_emissions(storage_gb, carbon_intensity):
    """Calculate annual CO2 emissions in kg."""
    return storage_gb * KWH_PER_GB_PER_YEAR * carbon_intensity / 1000  # kg CO2

def calculate_annual_water(storage_gb):
    """Calculate annual water consumption in liters."""
    return storage_gb * LITERS_PER_GB_PER_YEAR

def calculate_annual_cost(storage_gb, archival_gb, standard_cost_per_gb_month, archive_cost_per_gb_month):
    """Calculate annual storage cost in EUR."""
    standard_gb = storage_gb - archival_gb
    standard_cost = standard_gb * standard_cost_per_gb_month * 12
    archival_cost = archival_gb * archive_cost_per_gb_month * 12
    return standard_cost + archival_cost

def calculate_archival_needed(current_storage_gb, target_emissions_kg, carbon_intensity, years_ahead, 
                              annual_growth_rate, archival_reduction, standard_cost, archive_cost):
    results = []
    for year in range(1, int(years_ahead) + 1):
        projected_storage_gb = current_storage_gb * ((1 + annual_growth_rate) ** year)
        projected_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        projected_water = calculate_annual_water(projected_storage_gb)
        cost_without_archival = calculate_annual_cost(projected_storage_gb, 0, standard_cost, archive_cost)
        
        archived_gb_needed = 0
        if projected_emissions > target_emissions_kg and archival_reduction > 0:
            co2_per_gb = calculate_annual_emissions(1, carbon_intensity)
            archived_gb_needed = (projected_emissions - target_emissions_kg) / (co2_per_gb * archival_reduction)
            archived_gb_needed = min(max(archived_gb_needed, 0), projected_storage_gb)
            
        final_emissions = projected_emissions - (archived_gb_needed * calculate_annual_emissions(1, carbon_intensity) * archival_reduction)
        
        water_per_gb = calculate_annual_water(1)
        water_savings = archived_gb_needed * water_per_gb * ARCHIVAL_WATER_REDUCTION 
        final_water = projected_water - water_savings
        
        cost_with_archival = calculate_annual_cost(projected_storage_gb, archived_gb_needed, standard_cost, archive_cost)
        cost_savings = cost_without_archival - cost_with_archival
        
        results.append({
            "Year": year,
            "Storage (TB)": projected_storage_gb / 1024,
            "Storage (GB)": projected_storage_gb,
            "Emissions w/o Archival (kg)": projected_emissions,
            "Water w/o Archival (L)": projected_water,
            "Cost w/o Archival (€)": cost_without_archival,
            "Data to Archive (GB)": archived_gb_needed,
            "Data to Archive (TB)": archived_gb_needed / 1024,
            "Emissions After Archival (kg)": final_emissions,
            "Water After Archival (L)": final_water,
            "Water Savings (L)": water_savings,
            "Cost After Archival (€)": cost_with_archival,
            "Cost Savings (€)": cost_savings,
            "Meets Target": "✅" if final_emissions <= target_emissions_kg + 5 else "❌"
        })
    return pd.DataFrame(results)
