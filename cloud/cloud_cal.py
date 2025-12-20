import streamlit as st
import pandas as pd

# ===============================
# CONFIG & CONSTANTS
# ===============================
st.set_page_config(
    page_title="Green IT – Cloud Storage Optimizer",
    layout="wide"
)

KWH_PER_GB_PER_YEAR = 1.2  # kWh/GB/year (conservative estimate)
CARBON_INTENSITY = 400  # gCO2/kWh (IEA global average)

# Water consumption (based on average WUE of 1.9 L/kWh from The Green Grid)
# Source: Environmental and Energy Study Institute (EESI)
LITERS_PER_GB_PER_YEAR = KWH_PER_GB_PER_YEAR * 1.9  # 2.28 liters/GB/year

# Archival savings
ARCHIVAL_CARBON_REDUCTION = 0.90  # 90% carbon reduction for archived data
ARCHIVAL_WATER_REDUCTION = 0.90  # 90% water reduction for archived data

# Real-world comparisons
OLYMPIC_POOL_LITERS = 2_500_000  # Standard Olympic swimming pool volume
CO2_PER_TREE_PER_YEAR = 22  # kg CO2 absorbed by one mature tree per year (One Tree Planted / Winrock International)

# ===============================
# FUNCTIONS
# ===============================
def calculate_annual_emissions(storage_gb, carbon_intensity):
    """Calculate annual CO2 emissions in kg."""
    return storage_gb * KWH_PER_GB_PER_YEAR * carbon_intensity / 1000  # kg CO2

def calculate_annual_water(storage_gb):
    """Calculate annual water consumption in liters."""
    return storage_gb * LITERS_PER_GB_PER_YEAR

def calculate_archival_needed(current_storage_gb, target_emissions_kg, carbon_intensity, years_ahead, annual_growth_rate):
    """
    Calculate how much data needs to be archived to meet target emissions
    considering data growth over specified years.
    """
    results = []
    
    for year in range(1, years_ahead + 1):
        # Calculate projected storage with growth
        projected_storage_gb = current_storage_gb * ((1 + annual_growth_rate) ** year)
        
        # Calculate emissions and water without archival
        projected_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        projected_water = calculate_annual_water(projected_storage_gb)
        
        # Calculate how much needs to be archived to meet target
        if projected_emissions > target_emissions_kg:
            co2_per_gb = calculate_annual_emissions(1, carbon_intensity)
            
            # Solving for archived_gb:
            archived_gb_needed = (projected_emissions - target_emissions_kg) / (co2_per_gb * ARCHIVAL_CARBON_REDUCTION)
            
            # Can't archive more than we have
            archived_gb_needed = min(archived_gb_needed, projected_storage_gb)
            
            # Calculate actual emissions and water after archival
            archival_savings = archived_gb_needed * co2_per_gb * ARCHIVAL_CARBON_REDUCTION
            final_emissions = projected_emissions - archival_savings
            
            water_per_gb = calculate_annual_water(1)
            water_savings = archived_gb_needed * water_per_gb * ARCHIVAL_WATER_REDUCTION
            final_water = projected_water - water_savings
        else:
            archived_gb_needed = 0
            final_emissions = projected_emissions
            final_water = projected_water
            water_savings = 0
        
        results.append({
            "Year": year,
            "Storage (TB)": projected_storage_gb / 1024,
            "Storage (GB)": projected_storage_gb,
            "Emissions w/o Archival (kg)": projected_emissions,
            "Water w/o Archival (L)": projected_water,
            "Data to Archive (GB)": archived_gb_needed,
            "Data to Archive (TB)": archived_gb_needed / 1024,
            "Emissions After Archival (kg)": final_emissions,
            "Water After Archival (L)": final_water,
            "Water Savings (L)": water_savings,
            "Meets Target": "✅" if final_emissions <= target_emissions_kg else "❌"
        })
    
    return pd.DataFrame(results)

# ===============================
# SIDEBAR INPUTS
# ===============================
st.sidebar.header("Company Inputs")

storage_tb = st.sidebar.number_input(
    "Current Total Storage (TB)", min_value=0.1, value=100.0, step=10.0
)
storage_gb = storage_tb * 1024

annual_growth_pct = st.sidebar.slider(
    "Annual Data Growth Rate (%)", 
    min_value=0, 
    max_value=100, 
    value=10,
    help="Expected annual percentage growth in data storage"
)
annual_growth_rate = annual_growth_pct / 100

reduction_target_pct = st.sidebar.slider(
    "CO₂ Reduction Target (%)", 
    min_value=5, 
    max_value=80, 
    value=30,
    help="Target percentage reduction in CO₂ emissions from current levels"
)

projection_years = st.sidebar.number_input(
    "Projection Period (years)", 
    min_value=1, 
    max_value=10, 
    value=5,
    step=1
)

# ===============================
# FIXED CARBON INTENSITY INFO
# ===============================
st.info(f"📍 Carbon Intensity: {CARBON_INTENSITY:.0f} gCO₂/kWh (IEA global average)")

# ===============================
# CURRENT STATUS
# ===============================
st.header("📊 Current Storage Status")

current_emissions = calculate_annual_emissions(storage_gb, CARBON_INTENSITY)
current_water = calculate_annual_water(storage_gb)
target_emissions_kg = current_emissions * (1 - reduction_target_pct / 100)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Storage", f"{storage_tb:.1f} TB")

with col2:
    st.metric("Current Annual Emissions", f"{current_emissions:,.0f} kg CO₂/year")

with col3:
    st.metric(
        f"Target Emissions (-{reduction_target_pct}%)", 
        f"{target_emissions_kg:,.0f} kg CO₂/year"
    )

with col4:
    st.metric("Current Water Usage", f"{current_water:,.0f} L/year")

# ===============================
# ARCHIVAL RECOMMENDATION
# ===============================
st.header("📦 Archival Strategy with Data Growth")

st.info(f"📈 Assuming {annual_growth_pct:.0f}% annual data growth | 🌱 Archival reduces CO₂ and water by {ARCHIVAL_CARBON_REDUCTION*100:.0f}% for archived data")

# Calculate archival needs
archival_df = calculate_archival_needed(storage_gb, target_emissions_kg, CARBON_INTENSITY, projection_years, annual_growth_rate)

# Display year 1 recommendation
first_year = archival_df[archival_df["Year"] == 1].iloc[0]

st.subheader("🎯 Year 1 Action Required")

if first_year["Data to Archive (GB)"] > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Archive in Year 1", 
            f"{first_year['Data to Archive (TB)']:.2f} TB",
            help="Amount of data to archive in the first year to meet target"
        )
        st.metric(
            "Percentage of Year 1 Storage",
            f"{(first_year['Data to Archive (GB)'] / first_year['Storage (GB)'] * 100):.1f}%"
        )
    
    with col2:
        st.metric(
            "CO₂ After Archival",
            f"{first_year['Emissions After Archival (kg)']:,.0f} kg/year"
        )
        reduction = first_year['Emissions w/o Archival (kg)'] - first_year['Emissions After Archival (kg)']
        st.metric(
            "Annual CO₂ Savings",
            f"{reduction:,.0f} kg/year",
            delta=f"-{(reduction/first_year['Emissions w/o Archival (kg)'])*100:.1f}%"
        )
    
    # Water savings
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Water After Archival",
            f"{first_year['Water After Archival (L)']:,.0f} L/year"
        )
    with col2:
        st.metric(
            "Annual Water Savings",
            f"{first_year['Water Savings (L)']:,.0f} L/year",
            delta=f"-{(first_year['Water Savings (L)']/first_year['Water w/o Archival (L)'])*100:.1f}%"
        )
    
    if first_year['Meets Target'] == "✅":
        st.success("✅ This archival strategy will meet your CO₂ target!")
    else:
        st.error("❌ Even with maximum archival, target cannot be met. Consider a higher emission target.")
else:
    st.success("✅ Year 1 emissions are already below target! No archival needed in the first year.")

# ===============================
# MULTI-YEAR PROJECTION
# ===============================
st.subheader(f"📅 {projection_years}-Year Projection & Archival Plan")

# Format display dataframe
display_df = archival_df.copy()
display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
display_df = display_df[[
    "Year", 
    "Storage (TB)", 
    "Emissions w/o Archival (kg)", 
    "Water w/o Archival (L)",
    "Data to Archive (TB)",
    "Emissions After Archival (kg)",
    "Water After Archival (L)",
    "Meets Target"
]]

# Format numbers
display_df["Storage (TB)"] = display_df["Storage (TB)"].apply(lambda x: f"{x:.2f}")
display_df["Emissions w/o Archival (kg)"] = display_df["Emissions w/o Archival (kg)"].apply(lambda x: f"{x:,.0f}")
display_df["Water w/o Archival (L)"] = display_df["Water w/o Archival (L)"].apply(lambda x: f"{x:,.0f}")
display_df["Data to Archive (TB)"] = display_df["Data to Archive (TB)"].apply(lambda x: f"{x:.2f}")
display_df["Emissions After Archival (kg)"] = display_df["Emissions After Archival (kg)"].apply(lambda x: f"{x:,.0f}")
display_df["Water After Archival (L)"] = display_df["Water After Archival (L)"].apply(lambda x: f"{x:,.0f}")

st.dataframe(display_df, use_container_width=True)

# ===============================
# KEY INSIGHTS
# ===============================
st.header("💡 Key Insights")

total_archival_needed = archival_df["Data to Archive (TB)"].sum()
years_meeting_target = (archival_df["Meets Target"] == "✅").sum()
total_water_savings = archival_df["Water Savings (L)"].sum()

# Calculate total CO2 savings
total_co2_savings = 0
for _, row in archival_df.iterrows():
    total_co2_savings += row["Emissions w/o Archival (kg)"] - row["Emissions After Archival (kg)"]

# Calculate real-world comparisons
olympic_pools_equivalent = total_water_savings / OLYMPIC_POOL_LITERS
trees_equivalent = round(total_co2_savings / CO2_PER_TREE_PER_YEAR)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        f"Total Archival Over {projection_years} Years",
        f"{total_archival_needed:.2f} TB"
    )

with col2:
    st.metric(
        "Years Meeting Target",
        f"{years_meeting_target}/{projection_years}"
    )

with col3:
    st.metric(
        f"Total Water Savings ({projection_years} yrs)",
        f"{total_water_savings:,.0f} L"
    )

# Real-world comparisons section
st.subheader("🌍 Real-World Impact")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "💧 Water Saved = Olympic Pools",
        f"{olympic_pools_equivalent:.2f} pools",
        help=f"Total water savings equivalent to Olympic swimming pools over {projection_years} years"
    )

with col2:
    st.metric(
        "🌳 CO₂ Saved = Trees Planted",
        f"{trees_equivalent:,} trees",
        help=f"Equivalent to the annual CO₂ absorption of this many mature trees over {projection_years} years"
    )

st.caption("💡 **Recommendation**: Implement a continuous archival policy for data older than 5 years to maintain sustainable storage emissions as your data grows.")
st.caption(f"📊 **Benefits of Archival**: 90% CO₂ reduction on archived data | 90% water consumption reduction | 90% cost savings on archived data")
st.caption(f"💧 **Water Impact**: Based on industry-standard WUE of 1.9 L/kWh (The Green Grid / EESI data)")
st.caption(f"🌍 **Real-World Comparisons**: 1 Olympic pool = 2.5M liters | 1 mature tree absorbs ~{CO2_PER_TREE_PER_YEAR} kg CO₂/year (One Tree Planted / Winrock International)")
