import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# --- 1. ROBUST IMPORT BLOCK ---
# This tries to import from 'cloud.cloud_cal' first, then falls back to local import
try:
    from cloud.cloud_cal import (
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
    try:
        # Try importing as if we are inside the cloud folder
        from cloud_cal import (
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
        st.error("Could not import 'cloud_cal'. Please check your file structure.")
        st.stop()

# --- 2. THE UI CODE ---

def render_cloud_section():
    """Main function to render the Cloud Optimizer page."""
    st.markdown("### ☁️ Cloud Storage Optimizer")
    st.write("Optimize your data center footprint through intelligent archival strategies.")

    # --- INPUTS ---
    st.subheader("Settings")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        # Changed from "Country Code" to "Provider" because that is what your backend data supports
        selected_provider = st.selectbox("Cloud Provider", options=df_cloud['Provider'].unique().tolist(), index=0)
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.slider("Projection (Years)", 1, 10, 5)

    # --- DATA PREPARATION ---
    # 1. Get the data for the selected provider from your df_cloud
    provider_data = df_cloud[df_cloud['Provider'] == selected_provider].iloc[0]
    
    # 2. Extract key metrics from the backend data
    # Your backend has 'CO2_kg_TB_Month', but the formula expects 'carbon_intensity' (gCO2/kWh)
    # We perform the conversion here so we don't have to touch the backend file.
    # Conversion: (kg/TB/Month * 12 months * 1000g) / (1024 GB * 1.2 kWh/GB)
    co2_kg_month = provider_data['CO2_kg_TB_Month']
    estimated_intensity = (co2_kg_month * 12 * 1000) / (1024 * 1.2)
    
    # Costs from your data (Average of Standard vs Archive for this provider)
    # We use a simple filter to find "Archive" or "Cold" rows for this provider
    provider_rows = df_cloud[df_cloud['Provider'] == selected_provider]
    
    try:
        # Try to find specific prices in your dataframe
        std_price = provider_rows[provider_rows['Storage Class'].str.contains('Standard|Hot', case=False)]['Price_EUR_TB_Month'].mean()
        arch_price = provider_rows[provider_rows['Storage Class'].str.contains('Archive|Glacier|Cold', case=False)]['Price_EUR_TB_Month'].mean()
    except:
        # Fallbacks if exact matches fail
        std_price = 20.0
        arch_price = 4.0
        
    # Handle NaN cases (fill with defaults)
    if pd.isna(std_price): std_price = 20.0
    if pd.isna(arch_price): arch_price = 3.0

    # Convert to GB cost for the backend function
    std_cost_gb = std_price / 1024
    arch_cost_gb = arch_price / 1024

    # --- CALCULATIONS ---
    storage_gb = storage_tb * 1024
    
    # Calculate Base Metrics
    current_emissions = calculate_annual_emissions(storage_gb, estimated_intensity)
    current_water = calculate_annual_water(storage_gb)
    target_emissions_kg = current_emissions * (1 - reduction_target / 100)

    # --- DIAGNOSTIC ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Annual Carbon", f"{current_emissions:,.0f} kg CO₂")
    m2.metric("Annual Water", f"{current_water:,.0f} Liters")
    m3.metric("Goal Target", f"{target_emissions_kg:,.0f} kg CO₂")

    # --- STRATEGY ENGINE ---
    # Calling the function from your 'cloud_cal' file
    archival_df = calculate_archival_needed(
        current_storage_gb=storage_gb,
        target_emissions_kg=target_emissions_kg,
        carbon_intensity=estimated_intensity,
        years_ahead=projection_years,
        annual_growth_rate=0.15,      # Default 15% growth
        archival_reduction=0.90,      # Default 90% savings
        standard_cost=std_cost_gb,
        archive_cost=arch_cost_gb
    )
    
    if not archival_df.empty:
        year_1 = archival_df.iloc[0]
        
        st.subheader("Optimization Strategy")
        st.success(f"**Recommendation:** Archive **{year_1['Data to Archive (TB)']:.2f} TB** to Cold Storage.")
        
        # Visuals
        tab1, tab2 = st.tabs(["📉 Emissions Forecast", "📊 Detailed Data"])
        
        with tab1:
            chart_data = archival_df.rename(columns={
                "Emissions w/o Archival (kg)": "BAU (No Action)",
                "Emissions After Archival (kg)": "Optimized"
            })
            fig = px.line(chart_data, x="Year", y=["BAU (No Action)", "Optimized"], 
                          title="Carbon Emissions Trajectory",
                          color_discrete_map={"BAU (No Action)": "#ef4444", "Optimized": "#10b981"})
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.dataframe(archival_df, use_container_width=True)

# Function alias to satisfy different entry points
def run():
    render_cloud_section()

if __name__ == "__main__":
    render_cloud_section()