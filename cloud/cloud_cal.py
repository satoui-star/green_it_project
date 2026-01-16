import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Ensure the 'cloud' package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Constants for human-readable metrics
LITERS_PER_SHOWER = 50 

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
    
    /* URGENT RED ALERT BOX */
    .urgent-alert {
        background-color: #fef2f2;
        padding: 28px;
        border-radius: 16px;
        border: 2px solid #ef4444;
        border-left: 12px solid #ef4444;
        box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.1);
        margin-bottom: 30px;
    }
    .urgent-alert h3 {
        color: #991b1b;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 800;
    }
    .urgent-alert p {
        color: #7f1d1d;
        font-size: 1.1rem;
        line-height: 1.5;
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
    current_water_liters = calculate_annual_water(storage_gb)
    target_emissions_kg = current_emissions * (1 - reduction_target / 100)

    # Convert Water to Showers
    current_showers = current_water_liters / LITERS_PER_SHOWER

    # --- ANNUAL SNAPSHOT (DIAGNOSTIC) ---
    st.divider()
    st.subheader("Current Annual Baseline")
    st.caption("These metrics show your current yearly impact before optimization.")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Annual Carbon", f"{current_emissions:,.0f} kg CO₂/yr")
    m2.metric("Annual Water Footprint", f"{current_showers:,.0f} Showers/yr", 
              help=f"Equivalent to {current_water_liters:,.0f} Liters. Logic: 1 shower = {LITERS_PER_SHOWER}L of water used for data center cooling.")
    m3.metric("Yearly Goal Target", f"{target_emissions_kg:,.0f} kg CO₂/yr")

    # --- STRATEGY ---
    st.subheader("🚨 ACTION REQUIRED IMMEDIATELY")
    
    # Run the math engine
    archival_df = calculate_archival_needed(
        storage_gb, target_emissions_kg, carbon_intensity, projection_years, 
        0.15, 0.90, 0.022, 0.004 
    )
    
    year_1 = archival_df.iloc[0]
    
    # Urgent Disclaimer Card
    st.markdown(f"""
    <div class="urgent-alert">
        <h3>Immediate Intervention Required</h3>
        <p><b>CRITICAL:</b> To halt your current environmental debt, you must archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        of data immediately. Doing nothing will cause your emissions to surge exponentially as your data grows. 
        Moving to Cold Storage is no longer a choice—it is a requirement to hit your <b>{reduction_target}%</b> reduction mandate.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- CUMULATIVE IMPACT ---
    st.subheader(f"📈 Total {projection_years}-Year Environmental Gap")
    
    total_co2_no_action = archival_df["Emissions w/o Archival (kg)"].sum()
    total_co2_optimized = archival_df["Emissions After Archival (kg)"].sum()
    total_savings_co2 = total_co2_no_action - total_co2_optimized
    total_savings_euro = archival_df["Cost Savings (€)"].sum()
    total_water_saved_liters = archival_df["Water Savings (L)"].sum()
    total_showers_saved = total_water_saved_liters / LITERS_PER_SHOWER

    k1, k2, k3 = st.columns(3)
    k1.metric(f"Total CO₂ Saved", f"{total_savings_co2:,.0f} kg CO₂", delta="Massive Reduction", delta_color="normal")
    k2.metric(f"Total Water Reclaimed", f"{total_showers_saved:,.0f} Showers", 
              help=f"Total water savings: {total_water_saved_liters:,.0f} Liters. Calculation: Showers = Total Liters / {LITERS_PER_SHOWER}L per shower.")
    k3.metric(f"Total Financial ROI", f"€{total_savings_euro:,.0f}", delta="Cost Avoided", delta_color="normal")

    # --- DRAMATIC VISUAL COMPARISON ---
    st.write("### The Impact Contrast")
    act_col1, act_col2 = st.columns(2)
    
    with act_col1:
        # Dramatic Bar Chart
        fig_impact = go.Figure()
        fig_impact.add_trace(go.Bar(
            x=["Business As Usual", "After Intervention"],
            y=[current_emissions, year_1["Emissions After Archival (kg)"]],
            name="CO2 Emissions",
            marker_color=['#450a0a', '#10b981'], # Dark red vs bright green
            text=[f"{current_emissions:,.0f} kg", f"{year_1['Emissions After Archival (kg)']:,.0f} kg"],
            textposition='auto',
        ))
        fig_impact.update_layout(title="Carbon Impact Reduction (Annual)", height=350, template="plotly_white")
        st.plotly_chart(fig_impact, use_container_width=True)

    with act_col2:
        # Water to Showers Bar Chart
        after_showers = year_1["Water After Archival (L)"] / LITERS_PER_SHOWER
        fig_water = go.Figure()
        fig_water.add_trace(go.Bar(
            x=["Wasteful Pattern", "Optimized Pattern"],
            y=[current_showers, after_showers],
            name="Water in Showers",
            marker_color=['#1e3a8a', '#60a5fa'],
            text=[f"{current_showers:,.0f} Showers", f"{after_showers:,.0f} Showers"],
            textposition='auto',
        ))
        fig_water.update_layout(title="Water Footprint (Showers Saved)", height=350, template="plotly_white")
        st.plotly_chart(fig_water, use_container_width=True)

    # --- DRAMATIC FORECAST (AREA CHART) ---
    st.write("### Survival Forecast: The Growing Sustainability Gap")
    
    chart_data = archival_df.rename(columns={
        "Emissions w/o Archival (kg)": "Business As Usual (Destructive)",
        "Emissions After Archival (kg)": "Strategic Archival (Sustainable)"
    })
    
    # Using area chart for dramatic visual volume
    fig_area = px.area(chart_data, x="Year", 
                       y=["Business As Usual (Destructive)", "Strategic Archival (Sustainable)"],
                       title="Projected Cumulative Carbon Debt",
                       color_discrete_map={
                           "Business As Usual (Destructive)": "#ef4444", 
                           "Strategic Archival (Sustainable)": "#10b981"
                       })
    
    fig_area.update_layout(
        yaxis_title="kg CO₂ Emitted", 
        xaxis_title="Projection Year", 
        height=500,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_area, use_container_width=True)

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
        st.write("**Methodology & Calculation Logic**")
        st.write(f"""
            - 💨 **Carbon Intensity:** Calculated at {carbon_intensity:.0f} gCO₂/kWh based on cloud region energy mix.
            - 🚿 **Water to Showers:** 1 Shower is standardized at **{LITERS_PER_SHOWER} Liters** (Average duration and flow rate). Total liters used for cooling divided by {LITERS_PER_SHOWER}.
            - 🌳 **Tree Equivalency:** {CO2_PER_TREE_PER_YEAR} kg CO₂/year per mature tree.
            - 📦 **Urgency Logic:** Delaying archival for even one year increases the 'Recovery TB' needed by 15% due to data growth compounding.
        """)

# Main entry
if __name__ == "__main__":
    st.title("Green IT Lifecycle & ROI Optimization")
    st.markdown("### Strategic decision-making models for a sustainable circular economy.")
    
    st.divider()
    run_cloud_optimizer()
