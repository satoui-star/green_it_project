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
        selected_providers = st.multiselect("Cloud Providers", options=df_cloud['Provider'].unique().tolist(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.slider("Projection (Years)", 1, 10, 5)

    # --- DATA PREPARATION ---
    storage_gb = storage_tb * 1024
    
    # Calculate Blended Intensity for selected providers
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    std_co2 = filtered['CO2_kg_TB_Month'].iloc[0] if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000

    # --- CALCULATIONS ---
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water = calculate_annual_water(storage_gb)
    target_emissions_kg = current_emissions * (1 - reduction_target / 100)

    # --- DIAGNOSTIC ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Annual Carbon", f"{current_emissions:,.0f} kg CO₂")
    m2.metric("Annual Water", f"{current_water:,.0f} Liters")
    m3.metric("Goal Target", f"{target_emissions_kg:,.0f} kg CO₂")

    # --- STRATEGY ENGINE ---
    archival_df = calculate_archival_needed(
        storage_gb, target_emissions_kg, carbon_intensity, projection_years, 
        0.15, 0.90, 0.022, 0.004 
    )
    
    if not archival_df.empty:
        year_1 = archival_df.iloc[0]
        
        st.subheader("Optimization Strategy")
        st.success(f"**Recommendation:** Archive **{year_1['Data to Archive (TB)']:.1f} TB** to Cold Storage.")
        st.info(f"This reduces your footprint to **{year_1['Emissions After Archival (kg)']:,.0f} kg CO₂/year** and saves **{year_1['Water Savings (L)']:,.0f} Liters** of water.")
        
        # Visual Comparison - Histograms (Bar Charts)
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            fig_impact = go.Figure()
            fig_impact.add_trace(go.Bar(
                x=["Current Status", "After Strategy"],
                y=[current_emissions, year_1["Emissions After Archival (kg)"]],
                name="CO2 Emissions",
                marker_color=['#94a3b8', '#10b981']
            ))
            fig_impact.update_layout(title="Annual Carbon Impact (kg)", height=300, margin=dict(t=40, b=0))
            st.plotly_chart(fig_impact, use_container_width=True)

        with act_col2:
            fig_water = go.Figure()
            fig_water.add_trace(go.Bar(
                x=["Current Status", "After Strategy"],
                y=[current_water, year_1["Water After Archival (L)"]],
                name="Water Usage",
                marker_color=['#94a3b8', '#3b82f6']
            ))
            fig_water.update_layout(title="Annual Water Footprint (Liters)", height=300, margin=dict(t=40, b=0))
            st.plotly_chart(fig_water, use_container_width=True)

        # Visual Forecast
        chart_data = archival_df.rename(columns={
            "Emissions w/o Archival (kg)": "Doing Nothing",
            "Emissions After Archival (kg)": "Optimized Strategy"
        })
        fig_line = px.line(chart_data, x="Year", y=["Doing Nothing", "Optimized Strategy"], 
                      title=f"{projection_years}-Year Emissions Forecast", color_discrete_map={"Doing Nothing": "#ef4444", "Optimized Strategy": "#10b981"})
        st.plotly_chart(fig_line, use_container_width=True)

        with st.expander("Technical Breakdown & Calculation Transparency"):
            st.write("Detailed annualized metrics highlighting required archival actions and savings.")
            
            # Table columns: Including Storage (TB) back as data evolution
            cols_to_show = [
                "Year", "Storage (TB)", "Data to Archive (TB)",
                "Emissions w/o Archival (kg)", "Emissions After Archival (kg)", 
                "Water Savings (L)", "Cost Savings (€)", "Meets Target"
            ]
            
            # Format display dataframe for readability
            display_df = archival_df.copy()
            display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
            
            formatted_df = display_df[cols_to_show].style.format({
                "Storage (TB)": "{:.2f}",
                "Data to Archive (TB)": "{:.2f}",
                "Emissions w/o Archival (kg)": "{:,.0f}",
                "Emissions After Archival (kg)": "{:,.0f}",
                "Water Savings (L)": "{:,.0f}",
                "Cost Savings (€)": "€{:,.0f}"
            })
            
            st.dataframe(formatted_df, use_container_width=True, hide_index=True)
            
            st.divider()
            st.write("**Methodology & Sources**")
            st.write(f"""
                - 💨 **Carbon Intensity:** Calculated based on selected provider profiles ({carbon_intensity:.0f} gCO₂/kWh).
                - 💧 **Water Impact:** Reported as total savings achieved through archival, based on 1.9 L/kWh (The Green Grid).
                - 🌳 **Tree Equivalency:** {CO2_PER_TREE_PER_YEAR} kg CO₂/year per mature tree.
                - 📦 **Archival Logic:** Determines the specific TB volume required to be shifted into cold storage classes to satisfy emissions targets.
            """)

# Function alias to satisfy different entry points
def run():
    render_cloud_section()

if __name__ == "__main__":
    render_cloud_section()
