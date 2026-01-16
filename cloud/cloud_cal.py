import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Ensure the 'cloud' package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 1. ROBUST IMPORT BLOCK ---
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
        st.error("Missing components. Please ensure the 'cloud' folder contains '__init__.py'.")
        st.stop()

# --- GLOBAL PAGE CONFIG ---
st.set_page_config(
    page_title="Green IT Decision Portal",
    page_icon="🌱",
    layout="wide"
)

# Shared CSS for consistent display
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .recommendation-card { 
        background-color: #ffffff; 
        padding: 24px; 
        border-radius: 16px; 
        border-left: 8px solid #10b981; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 24px;
    }
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .status-ok { background-color: #dcfce7; color: #15803d; }
    .status-risk { background-color: #fee2e2; color: #b91c1c; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# HARDWARE LIFECYCLE (Keep as is in the unified view)
# =================================================================
# Note: Since the user specifically asked to fix the increment issue in the 
# cloud calculator part of ui.py, I am focusing on the run_cloud_optimizer section.

def run_cloud_optimizer():
    """Function to render the Cloud Optimizer page."""
    st.title("Cloud Storage Sustainability Advisor")
    st.write("Optimize your data center footprint through intelligent archival strategies.")

    # --- INPUTS ---
    st.subheader("Settings")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        selected_providers = st.multiselect("Cloud Providers", options=df_cloud['Provider'].unique().tolist(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("CO₂ Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)

    # Calculation Prep
    storage_gb = storage_tb * 1024
    
    # Calculate Blended Intensity for selected providers
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    std_co2 = filtered['CO2_kg_TB_Month'].iloc[0] if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000
    
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water = calculate_annual_water(storage_gb)
    target_emissions_kg = current_emissions * (1 - reduction_target / 100)

    # --- ANNUAL SNAPSHOT (DIAGNOSTIC) ---
    st.divider()
    st.subheader("Current Annual Baseline")
    st.caption("These metrics show your current yearly impact before optimization.")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Annual Carbon", f"{current_emissions:,.0f} kg CO₂/yr")
    m2.metric("Current Annual Water", f"{current_water:,.0f} L/yr")
    m3.metric("Yearly Goal Target", f"{target_emissions_kg:,.0f} kg CO₂/yr")

    # --- STRATEGY ---
    st.subheader("Optimization Strategy")
    
    # Run the math engine
    # Using 15% growth and 90% archival reduction as per logic
    archival_df = calculate_archival_needed(
        storage_gb, target_emissions_kg, carbon_intensity, projection_years, 
        0.15, 0.90, 0.022, 0.004 
    )
    
    year_1 = archival_df.iloc[0]
    
    # Recommendation
    st.success(f"**Action Recommended:** Move **{year_1['Data to Archive (TB)']:.1f} TB** to Cold Storage immediately to meet your **{reduction_target}%** goal.")
    st.info(f"This reduces your footprint to **{year_1['Emissions After Archival (kg)']:,.0f} kg CO₂/year** and saves **{year_1['Water Savings (L)']:,.0f} Liters** of water in Year 1.")

    # --- CUMULATIVE IMPACT (THE FIX) ---
    st.subheader(f"📈 Total {projection_years}-Year Impact")
    st.write(f"Total accumulated values over the {projection_years} year period, accounting for data growth and optimization.")
    
    total_co2_no_action = archival_df["Emissions w/o Archival (kg)"].sum()
    total_co2_optimized = archival_df["Emissions After Archival (kg)"].sum()
    total_savings_co2 = total_co2_no_action - total_co2_optimized
    total_savings_euro = archival_df["Cost Savings (€)"].sum()
    total_water_saved = archival_df["Water Savings (L)"].sum()

    k1, k2, k3 = st.columns(3)
    k1.metric(f"Total CO₂ Avoided ({projection_years}y)", f"{total_savings_co2:,.0f} kg CO₂", delta="Impact", delta_color="normal")
    k2.metric(f"Total Financial Savings", f"€{total_savings_euro:,.0f}", delta="ROI", delta_color="normal")
    k3.metric(f"Total Water Saved", f"{total_water_saved:,.0f} L", delta="Sustainability", delta_color="normal")

    # --- VISUAL COMPARISON (HISTOGRAMS) ---
    st.write("### Yearly Comparison")
    act_col1, act_col2 = st.columns(2)
    with act_col1:
        fig_impact = go.Figure()
        fig_impact.add_trace(go.Bar(
            x=["Current Baseline", "Year 1 Optimized"],
            y=[current_emissions, year_1["Emissions After Archival (kg)"]],
            name="CO2 Emissions",
            marker_color=['#94a3b8', '#10b981']
        ))
        fig_impact.update_layout(title="Carbon Impact (kg CO₂ / Year)", height=300, margin=dict(t=40, b=0))
        st.plotly_chart(fig_impact, use_container_width=True)

    with act_col2:
        fig_water = go.Figure()
        fig_water.add_trace(go.Bar(
            x=["Current Baseline", "Year 1 Optimized"],
            y=[current_water, year_1["Water After Archival (L)"]],
            name="Water Usage",
            marker_color=['#94a3b8', '#3b82f6']
        ))
        fig_water.update_layout(title="Water Footprint (L / Year)", height=300, margin=dict(t=40, b=0))
        st.plotly_chart(fig_water, use_container_width=True)

    # --- VISUAL FORECAST ---
    chart_data = archival_df.rename(columns={
        "Emissions w/o Archival (kg)": "Doing Nothing",
        "Emissions After Archival (kg)": "Optimized Strategy"
    })
    fig_line = px.line(chart_data, x="Year", y=["Doing Nothing", "Optimized Strategy"], 
                  title=f"{projection_years}-Year Emissions Trajectory", color_discrete_map={"Doing Nothing": "#ef4444", "Optimized Strategy": "#10b981"})
    st.plotly_chart(fig_line, use_container_width=True)

    # --- TECHNICAL BREAKDOWN ---
    with st.expander("🧬 View Technical Breakdown & Data Evolution"):
        st.write("Detailed annualized metrics showing storage growth and archival targets.")
        
        cols_to_show = [
            "Year", "Storage (TB)", "Data to Archive (TB)",
            "Emissions w/o Archival (kg)", "Emissions After Archival (kg)", 
            "Water Savings (L)", "Cost Savings (€)", "Meets Target"
        ]
        
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
            - 📦 **Archival Logic:** Determines the required shift to cold storage classes to satisfy targets across the {projection_years}-year period.
        """)

# Main entry
if __name__ == "__main__":
    # If using unified page, hardware part would go here
    st.title("Green IT Lifecycle & ROI Optimization")
    st.markdown("### Strategic decision-making models for a sustainable circular economy.")
    
    # Rest of the hardware logic...
    # (Existing section 1 code from ui.py would be here)
    
    st.divider()
    run_cloud_optimizer()
