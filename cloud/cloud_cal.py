import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

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

# --- THEME & CONFIG ---
st.set_page_config(
    page_title="Green IT | Cloud Sustainability Advisor",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f9fbf9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# ===============================
# SIDEBAR INPUTS (Simplified Labels)
# ===============================
st.sidebar.title("Configuration")
st.sidebar.markdown("Define your current cloud footprint to generate an optimization plan.")

selected_providers = st.sidebar.multiselect(
    "Cloud Providers",
    options=df_cloud['Provider'].unique().tolist(),
    default=["AWS"],
    help="We use provider-specific data to calculate your unique impact."
)

if not selected_providers:
    selected_providers = ["AWS"]

storage_tb = st.sidebar.number_input(
    "Total Data Volume (TB)", 
    min_value=0.1, 
    value=100.0, 
    step=10.0,
    help="Your total storage across all buckets/containers."
)
storage_gb = storage_tb * 1024

annual_growth_pct = st.sidebar.slider(
    "Estimated Yearly Growth (%)", 
    min_value=0, 
    max_value=100, 
    value=15,
    help="How much your data volume increases annually."
)

# --- INTERNAL CALCULATIONS (Preserved Logic) ---
standard_costs = []
archive_costs = []
co2_standards = []
co2_archives = []

for provider in selected_providers:
    provider_data = df_cloud[df_cloud['Provider'] == provider]
    std_data = provider_data.iloc[0]
    arc_data = provider_data.iloc[-1]
    standard_costs.append(float(std_data['Price_EUR_TB_Month']) / 1024)
    archive_costs.append(float(arc_data['Price_EUR_TB_Month']) / 1024)
    co2_standards.append(float(std_data['CO2_kg_TB_Month']))
    co2_archives.append(float(arc_data['CO2_kg_TB_Month']))

STANDARD_STORAGE_COST_PER_GB_MONTH = sum(standard_costs) / len(standard_costs)
ARCHIVAL_STORAGE_COST_PER_GB_MONTH = sum(archive_costs) / len(archive_costs)
avg_co2_standard = sum(co2_standards) / len(co2_standards)
avg_co2_archive = sum(co2_archives) / len(co2_archives)
CARBON_INTENSITY = (avg_co2_standard * 12 / (1024 * 1.2)) * 1000
ARCHIVAL_CARBON_REDUCTION = 1 - (avg_co2_archive / avg_co2_standard) if avg_co2_standard > 0 else 0.90

# ===============================
# HEADER & NAVIGATION
# ===============================
st.title("🌱 Cloud Sustainability Advisor")
st.markdown(f"**Targeting Net Zero storage for:** `{', '.join(selected_providers)}` | **Current Data Intensity:** `{CARBON_INTENSITY:.0f} gCO₂/kWh`")

tab_diag, tab_opt, tab_deep = st.tabs(["📊 Impact Diagnostic", "🚀 Optimization Strategy", "🧬 Data Deep Dive"])

# ===============================
# TAB 1: DIAGNOSTIC (Measurement)
# ===============================
with tab_diag:
    current_emissions = calculate_annual_emissions(storage_gb, CARBON_INTENSITY)
    current_water = calculate_annual_water(storage_gb)
    current_cost = calculate_annual_cost(storage_gb, 0, STANDARD_STORAGE_COST_PER_GB_MONTH, ARCHIVAL_STORAGE_COST_PER_GB_MONTH)

    st.subheader("Current Environmental & Financial Footprint")
    st.info("This section represents your 'Business as Usual' scenario if no optimization is performed.")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Annual Carbon Footprint", f"{current_emissions:,.0f} kg CO₂", help="Equivalent to manufacturing emissions and energy usage.")
    with m_col2:
        st.metric("Annual Water Footprint", f"{current_water:,.0f} Liters", help="Estimated water used for data center cooling.")
    with m_col3:
        st.metric("Estimated Operational Cost", f"€{current_cost:,.0f}", help="Standard retail storage pricing before archival.")

    # Contextual Visualization
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        trees_needed = round(current_emissions / CO2_PER_TREE_PER_YEAR)
        st.write("### The Scale of Impact")
        st.write(f"To offset your current storage emissions, you would need to plant **{trees_needed:,} mature trees** every year.")
        # Visual indicator
        st.progress(min(trees_needed/1000, 1.0))
        st.caption("Low Impact < 100 trees | Medium Impact 100-500 | High Impact > 500")

# ===============================
# TAB 2: OPTIMIZATION (Actionable Recommendation)
# ===============================
with tab_opt:
    st.subheader("Step-by-Step Optimization Plan")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("#### 1. Set Your Ambition")
        reduction_target_pct = st.slider(
            "CO₂ Reduction Target (%)", 
            5, 80, 30,
            help="Higher targets require moving more data to Archive classes."
        )
        projection_years = st.number_input("Strategy Horizon (Years)", 1, 10, 5)
        
        target_emissions_kg = current_emissions * (1 - reduction_target_pct / 100)
        
        st.markdown("---")
        st.markdown("#### 2. Summary Action")
        archival_df = calculate_archival_needed(
            storage_gb, target_emissions_kg, CARBON_INTENSITY, projection_years, 
            annual_growth_pct/100, ARCHIVAL_CARBON_REDUCTION, 
            STANDARD_STORAGE_COST_PER_GB_MONTH, ARCHIVAL_STORAGE_COST_PER_GB_MONTH
        )
        year_1 = archival_df.iloc[0]
        
        st.success(f"**Recommended Action:** Move **{year_1['Data to Archive (TB)']:.1f} TB** to Cold Storage / Archive immediately.")

    with col_right:
        st.markdown("#### 3. Projected Optimization Benefits")
        
        total_co2_savings = 0
        for _, row in archival_df.iterrows():
            total_co2_savings += row["Emissions w/o Archival (kg)"] - row["Emissions After Archival (kg)"]
        
        res1, res2 = st.columns(2)
        with res1:
            st.metric("Total CO₂ Prevented", f"{total_co2_savings:,.0f} kg", delta=f"{reduction_target_pct}% reduction")
            st.write(f"🌳 **Equivalent to:** {round(total_co2_savings / CO2_PER_TREE_PER_YEAR):,} trees")
        with res2:
            total_savings_euro = archival_df["Cost Savings (€)"].sum()
            st.metric("Total Financial Savings", f"€{total_savings_euro:,.0f}", delta="Cost Avoidance", delta_color="normal")
            st.write(f"💰 **Avg ROI:** { (total_savings_euro / (current_cost * projection_years) * 100):.1f}%")

        # Visual Comparison Chart
        chart_data = archival_df[["Year", "Emissions w/o Archival (kg)", "Emissions After Archival (kg)"]].copy()
        chart_data = chart_data.rename(columns={
            "Emissions w/o Archival (kg)": "Standard (Doing Nothing)",
            "Emissions After Archival (kg)": "Optimized (Archival Strategy)"
        })
        fig = px.line(chart_data, x="Year", y=["Standard (Doing Nothing)", "Optimized (Archival Strategy)"], 
                      title="Emissions Forecast: Optimization vs. Growth",
                      color_discrete_map={"Standard (Doing Nothing)": "#ef553b", "Optimized (Archival Strategy)": "#00cc96"})
        fig.update_layout(yaxis_title="kg CO₂", xaxis_title="Projection Year")
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# TAB 3: DEEP DIVE (Technical/Spreadsheet)
# ===============================
with tab_deep:
    st.subheader("Technical Audit Trail")
    st.markdown("Detailed breakdown of projected volumes, water scarcity impact, and unit cost distribution.")
    
    # Format display dataframe for readability
    display_df = archival_df.copy()
    display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
    
    cols_to_show = [
        "Year", "Storage (TB)", "Emissions w/o Archival (kg)", 
        "Data to Archive (TB)", "Emissions After Archival (kg)", 
        "Water Savings (L)", "Cost Savings (€)", "Meets Target"
    ]
    
    formatted_df = display_df[cols_to_show].style.format({
        "Storage (TB)": "{:.2f}",
        "Emissions w/o Archival (kg)": "{:,.0f}",
        "Data to Archive (TB)": "{:.2f}",
        "Emissions After Archival (kg)": "{:,.0f}",
        "Water Savings (L)": "{:,.0f}",
        "Cost Savings (€)": "€{:,.0f}"
    })
    
    st.dataframe(formatted_df, use_container_width=True)
    
    with st.expander("Methodology & Sources"):
        st.write("""
            - **Carbon Intensity:** Based on average grid factors provided by cloud regions.
            - **Water Scarcity:** Calculated using 1.9 L/kWh average (The Green Grid).
            - **Tree Equivalency:** 22kg CO2/year per mature tree (Winrock International).
            - **Archival Savings:** Assuming 90% power reduction for cold storage tiers.
        """)

st.divider()
st.caption("Advisor v2.0 | Green IT Framework | Actionable sustainability insights for business users.")
