import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to sys.path so 'cloud' can be imported as a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    # Fallback for different execution environments
    from __init__ import (
        df_cloud, 
        calculate_annual_emissions, 
        calculate_annual_water, 
        calculate_annual_cost, 
        calculate_archival_needed,
        ARCHIVAL_WATER_REDUCTION,
        OLYMPIC_POOL_LITERS,
        CO2_PER_TREE_PER_YEAR
    )

st.set_page_config(
    page_title="Green IT – Cloud Storage Optimizer",
    layout="wide"
)

# ===============================
# SIDEBAR INPUTS
# ===============================
st.sidebar.header("Company Inputs")

# Multi-select for cloud providers
selected_providers = st.sidebar.multiselect(
    "Select Cloud Provider(s)",
    options=df_cloud['Provider'].unique().tolist(),
    default=["AWS"],
    help="Select one or multiple cloud providers. Costs and CO₂ will be averaged if multiple are selected."
)

# If no provider selected, default to AWS
if not selected_providers:
    selected_providers = ["AWS"]
    st.sidebar.warning("⚠️ No provider selected. Defaulting to AWS.")

# Calculate weighted average costs and CO2 across selected providers (equal distribution)
standard_costs = []
archive_costs = []
co2_standards = []
co2_archives = []

for provider in selected_providers:
    provider_data = df_cloud[df_cloud['Provider'] == provider]
    std_data = provider_data.iloc[0]  # First row = Standard storage
    arc_data = provider_data.iloc[-1]  # Last row = Archive storage
    
    # Costs (convert from EUR/TB/month to EUR/GB/month)
    standard_costs.append(float(std_data['Price_EUR_TB_Month']) / 1024)
    archive_costs.append(float(arc_data['Price_EUR_TB_Month']) / 1024)
    
    # CO2 data
    co2_standards.append(float(std_data['CO2_kg_TB_Month']))
    co2_archives.append(float(arc_data['CO2_kg_TB_Month']))

# Average across selected providers
STANDARD_STORAGE_COST_PER_GB_MONTH = sum(standard_costs) / len(standard_costs)
ARCHIVAL_STORAGE_COST_PER_GB_MONTH = sum(archive_costs) / len(archive_costs)

avg_co2_standard = sum(co2_standards) / len(co2_standards)
avg_co2_archive = sum(co2_archives) / len(co2_archives)

# Calculate carbon intensity from average CO2 data
CARBON_INTENSITY = (avg_co2_standard * 12 / (1024 * 1.2)) * 1000

# Calculate archival CO2 reduction percentage
if avg_co2_standard > 0:
    ARCHIVAL_CARBON_REDUCTION = 1 - (avg_co2_archive / avg_co2_standard)
else:
    ARCHIVAL_CARBON_REDUCTION = 0.90  # Fallback value

# Display selected provider(s)
provider_display = " + ".join(selected_providers) if len(selected_providers) > 1 else selected_providers[0]

storage_tb = st.sidebar.number_input(
    "Current Total Storage (TB)", 
    min_value=0.1, 
    value=100.0, 
    step=10.0
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
    step=1,
    help="Number of years to project storage growth and archival needs"
)

# ===============================
# PROVIDER & CARBON INTENSITY INFO
# ===============================
st.info(f"☁️ **Provider(s):** {provider_display} | 📍 Carbon Intensity: {CARBON_INTENSITY:.0f} gCO₂/kWh")

# ===============================
# CURRENT STATUS
# ===============================
st.header("📊 Current Storage Status")

current_emissions = calculate_annual_emissions(storage_gb, CARBON_INTENSITY)
current_water = calculate_annual_water(storage_gb)
current_cost = calculate_annual_cost(storage_gb, 0, STANDARD_STORAGE_COST_PER_GB_MONTH, ARCHIVAL_STORAGE_COST_PER_GB_MONTH)
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
    st.metric("Current Annual Cost", f"€{current_cost:,.0f}/year")

# ===============================
# ARCHIVAL RECOMMENDATION
# ===============================
st.header("📦 Archival Strategy with Data Growth")

st.info(f"📈 Assuming {annual_growth_pct:.0f}% annual data growth | 🌱 Archival reduces CO₂ by {ARCHIVAL_CARBON_REDUCTION*100:.0f}% and water by {ARCHIVAL_WATER_REDUCTION*100:.0f}% for archived data")

# Calculate archival needs
archival_df = calculate_archival_needed(
    storage_gb, 
    target_emissions_kg, 
    CARBON_INTENSITY, 
    projection_years, 
    annual_growth_rate,
    ARCHIVAL_CARBON_REDUCTION,
    STANDARD_STORAGE_COST_PER_GB_MONTH,
    ARCHIVAL_STORAGE_COST_PER_GB_MONTH
)

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
    
    # Water and Cost savings
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Water Savings",
            f"{first_year['Water Savings (L)']:,.0f} L/year",
            delta=f"-{(first_year['Water Savings (L)']/first_year['Water w/o Archival (L)'])*100:.1f}%"
        )
    with col2:
        st.metric(
            "Cost Savings",
            f"€{first_year['Cost Savings (€)']:,.0f}/year",
            delta=f"-{(first_year['Cost Savings (€)']/first_year['Cost w/o Archival (€)'])*100:.1f}%"
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
    "Cost w/o Archival (€)",
    "Data to Archive (TB)",
    "Emissions After Archival (kg)",
    "Water After Archival (L)",
    "Cost After Archival (€)",
    "Cost Savings (€)",
    "Meets Target"
]]

# Format numbers
display_df["Storage (TB)"] = display_df["Storage (TB)"].apply(lambda x: f"{x:.2f}")
display_df["Emissions w/o Archival (kg)"] = display_df["Emissions w/o Archival (kg)"].apply(lambda x: f"{x:,.0f}")
display_df["Water w/o Archival (L)"] = display_df["Water w/o Archival (L)"].apply(lambda x: f"{x:,.0f}")
display_df["Cost w/o Archival (€)"] = display_df["Cost w/o Archival (€)"].apply(lambda x: f"€{x:,.0f}")
display_df["Data to Archive (TB)"] = display_df["Data to Archive (TB)"].apply(lambda x: f"{x:.2f}")
display_df["Emissions After Archival (kg)"] = display_df["Emissions After Archival (kg)"].apply(lambda x: f"{x:,.0f}")
display_df["Water After Archival (L)"] = display_df["Water After Archival (L)"].apply(lambda x: f"{x:,.0f}")
display_df["Cost After Archival (€)"] = display_df["Cost After Archival (€)"].apply(lambda x: f"€{x:,.0f}")
display_df["Cost Savings (€)"] = display_df["Cost Savings (€)"].apply(lambda x: f"€{x:,.0f}")

st.dataframe(display_df, use_container_width=True)

# ===============================
# KEY INSIGHTS
# ===============================
st.header("💡 Key Insights")

total_archival_needed = archival_df["Data to Archive (TB)"].sum()
years_meeting_target = (archival_df["Meets Target"] == "✅").sum()
total_water_savings = archival_df["Water Savings (L)"].sum()
total_cost_savings = archival_df["Cost Savings (€)"].sum()

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
        f"Total Cost Savings ({projection_years} yrs)",
        f"€{total_cost_savings:,.0f}",
        help="Total financial savings from archival strategy"
    )

# Real-world comparisons section
st.subheader("🌍 Real-World Environmental Impact")

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

# Financial ROI section
st.subheader("💰 Financial Impact & ROI")

# Calculate cost per TB archived
cost_per_tb_archived = total_cost_savings / total_archival_needed if total_archival_needed > 0 else 0

# Calculate ROI percentage
total_standard_cost = sum(archival_df["Cost w/o Archival (€)"])
roi_percentage = (total_cost_savings / total_standard_cost * 100) if total_standard_cost > 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Annual Savings",
        f"€{total_cost_savings/projection_years:,.0f}/year",
        help="Average cost savings per year from archival strategy"
    )

with col2:
    st.metric(
        "Cost Efficiency",
        f"€{cost_per_tb_archived:,.0f}/TB",
        help="Average savings per TB archived"
    )

with col3:
    st.metric(
        "ROI from Archival",
        f"{roi_percentage:.1f}%",
        help="Percentage of storage costs saved through archival"
    )

st.caption("💡 **Recommendation**: Implement a continuous archival policy for data older than 5 years to maintain sustainable storage emissions as your data grows.")
st.caption(f"📊 **Benefits of Archival**: {ARCHIVAL_CARBON_REDUCTION*100:.0f}% CO₂ reduction | {ARCHIVAL_WATER_REDUCTION*100:.0f}% water reduction")
st.caption(f"🌍 **Real-World Comparisons**: 1 Olympic pool = 2.5M liters | 1 mature tree absorbs ~{CO2_PER_TREE_PER_YEAR} kg CO₂/year")
