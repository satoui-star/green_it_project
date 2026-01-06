import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

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
    page_title="Green IT | Sustainability Executive Dashboard",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; color: #1e293b; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 600 !important; color: #64748b; text-transform: uppercase; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
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

# ===============================
# SIDEBAR (Simplified & Collapsed)
# ===============================
st.sidebar.title("Cloud Footprint")

selected_providers = st.sidebar.multiselect(
    "Providers",
    options=df_cloud['Provider'].unique().tolist(),
    default=["AWS"],
    help="Select the providers used for your infrastructure."
)

if not selected_providers:
    selected_providers = ["AWS"]

storage_tb = st.sidebar.number_input(
    "Total Storage (TB)", 
    min_value=0.1, 
    value=100.0, 
    step=10.0
)
storage_gb = storage_tb * 1024

reduction_target_pct = st.sidebar.slider(
    "Reduction Goal (%)", 
    5, 80, 30
)

with st.sidebar.expander("⚙️ Advanced Assumptions"):
    annual_growth_pct = st.slider("Data Growth Rate (%)", 0, 100, 15)
    projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)

# --- INTERNAL CALCULATIONS ---
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

current_emissions = calculate_annual_emissions(storage_gb, CARBON_INTENSITY)
target_emissions_kg = current_emissions * (1 - reduction_target_pct / 100)
current_cost = calculate_annual_cost(storage_gb, 0, STANDARD_STORAGE_COST_PER_GB_MONTH, ARCHIVAL_STORAGE_COST_PER_GB_MONTH)
current_water = calculate_annual_water(storage_gb)

# ===============================
# SECTION 1: YOUR CURRENT IMPACT
# ===============================
st.title("Sustainability Executive Overview")

# Top Level Scorecard
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Annual Carbon", f"{current_emissions:,.0f} kg CO₂")
with kpi2:
    st.metric("Annual Cost", f"€{current_cost:,.0f}")
with kpi3:
    st.metric("Current Goal", f"-{reduction_target_pct}%")
with kpi4:
    is_on_track = current_emissions <= target_emissions_kg
    status_label = "✅ ON TRACK" if is_on_track else "⚠️ ACTION REQUIRED"
    st.markdown(f"**GOAL STATUS**")
    if is_on_track:
        st.markdown(f'<div class="status-pill status-ok">{status_label}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-pill status-risk">{status_label}</div>', unsafe_allow_html=True)

st.markdown("---")

# Gauge & Context
col_gauge, col_context = st.columns([1, 1.5])

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = reduction_target_pct,
        title = {'text': "Target Ambition (%)", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "#10b981"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 30], 'color': '#d1fae5'},
                {'range': [30, 60], 'color': '#6ee7b7'},
                {'range': [60, 100], 'color': '#059669'}],
        }
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_context:
    st.subheader("What does this mean?")
    pools = (current_water / OLYMPIC_POOL_LITERS)
    trees = (current_emissions / CO2_PER_TREE_PER_YEAR)
    
    st.markdown(f"""
    Your current cloud footprint is equivalent to:
    - 🌳 **{trees:,.0f} trees** planted every year to offset emissions.
    - 💧 **{pools:.1f} Olympic pools** of water used for infrastructure cooling.
    - 📉 **Cost Inefficiency:** You are likely paying **€{(current_cost * 0.4):,.0f}** more than necessary due to inactive data storage.
    """)

# ===============================
# SECTION 2: RECOMMENDED ACTION
# ===============================
st.markdown("## Recommended Strategy")

archival_df = calculate_archival_needed(
    storage_gb, target_emissions_kg, CARBON_INTENSITY, projection_years, 
    annual_growth_pct/100, ARCHIVAL_CARBON_REDUCTION, 
    STANDARD_STORAGE_COST_PER_GB_MONTH, ARCHIVAL_STORAGE_COST_PER_GB_MONTH
)
year_1 = archival_df.iloc[0]

st.markdown(f"""
<div class="recommendation-card" style="border-left-color: {'#10b981' if year_1['Data to Archive (GB)'] > 0 else '#64748b'};">
    <h3 style="margin-top:0;">🎯 Year 1 Priority</h3>
    <p style="font-size: 18px; color: #334155;">
        To meet your sustainability goals, you should move <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        of inactive data to cold/archive storage this year.
    </p>
    <p style="color: #64748b; font-weight: 500;">
        This action alone reduces emissions by <b>{reduction_target_pct}%</b> and lowers your storage bill by <b>€{year_1['Cost Savings (€)']:,.0f}</b>.
    </p>
</div>
""", unsafe_allow_html=True)

# Before vs After Impact
act_col1, act_col2 = st.columns(2)

with act_col1:
    # ROI Visual Comparison Tabs
    c_tab_co2, c_tab_water = st.tabs(["💨 Carbon Savings", "💧 Water Savings"])
    
    with c_tab_co2:
        fig_impact = go.Figure()
        fig_impact.add_trace(go.Bar(
            x=["Current Status", "After Strategy"],
            y=[current_emissions, year_1["Emissions After Archival (kg)"]],
            name="CO2 Emissions",
            marker_color=['#94a3b8', '#10b981']
        ))
        fig_impact.update_layout(title="Annual Carbon Impact (kg)", height=300, margin=dict(t=40, b=0))
        st.plotly_chart(fig_impact, use_container_width=True)

    with c_tab_water:
        fig_water = go.Figure()
        fig_water.add_trace(go.Bar(
            x=["Current Status", "After Strategy"],
            y=[current_water, year_1["Water After Archival (L)"]],
            name="Water Usage",
            marker_color=['#94a3b8', '#3b82f6']
        ))
        fig_water.update_layout(title="Annual Water Footprint (Liters)", height=300, margin=dict(t=40, b=0))
        st.plotly_chart(fig_water, use_container_width=True)

with act_col2:
    st.subheader("Your ROI Summary")
    total_savings = archival_df["Cost Savings (€)"].sum()
    total_co2 = (current_emissions - year_1["Emissions After Archival (kg)"]) * projection_years
    total_water = archival_df["Water Savings (L)"].sum()
    
    res_a, res_b = st.columns(2)
    res_a.metric("Total 5-Year Savings", f"€{total_savings:,.0f}")
    res_b.metric("Total CO₂ Avoided", f"{total_co2:,.0f} kg")
    
    res_c, res_d = st.columns(2)
    res_c.metric("Total Water Saved", f"{total_water:,.0f} L")
    res_d.metric("Pools Equivalent", f"{total_water / OLYMPIC_POOL_LITERS:.1f} Pools")
    
    st.info("💡 **Why this works:** Archival storage uses significantly less electricity and cooling, directly mitigating both carbon emissions and water scarcity risks in data center regions.")

# ===============================
# SECTION 3: WHAT HAPPENS OVER TIME
# ===============================
st.markdown("## 5-Year Outlook")

forecast_data = archival_df[["Year", "Emissions w/o Archival (kg)", "Emissions After Archival (kg)"]].copy()
forecast_data = forecast_data.rename(columns={
    "Emissions w/o Archival (kg)": "Standard Growth (Doing Nothing)",
    "Emissions After Archival (kg)": "Optimized Strategy"
})

fig_forecast = px.line(forecast_data, x="Year", y=["Standard Growth (Doing Nothing)", "Optimized Strategy"], 
                      title="Emissions Forecast over Time",
                      color_discrete_map={"Standard Growth (Doing Nothing)": "#ef553b", "Optimized Strategy": "#10b981"})
fig_forecast.update_layout(yaxis_title="kg CO₂", xaxis_title="Projection Year", height=400)
st.plotly_chart(fig_forecast, use_container_width=True)

with st.expander("🧬 View Technical Breakdown & Calculation Transparency"):
    st.markdown("Detailed annualized metrics including total projected water usage and cost avoidance.")
    
    # Detailed Table formatting
    cols_to_show = [
        "Year", "Storage (TB)", "Emissions w/o Archival (kg)", 
        "Emissions After Archival (kg)", "Water w/o Archival (L)", 
        "Water After Archival (L)", "Water Savings (L)", "Cost Savings (€)"
    ]
    
    st.dataframe(archival_df[cols_to_show].style.format({
        "Storage (TB)": "{:.1f}",
        "Emissions w/o Archival (kg)": "{:,.0f}",
        "Emissions After Archival (kg)": "{:,.0f}",
        "Water w/o Archival (L)": "{:,.0f}",
        "Water After Archival (L)": "{:,.0f}",
        "Water Savings (L)": "{:,.0f}",
        "Cost Savings (€)": "€{:,.0f}"
    }), use_container_width=True)

    st.markdown("---")
    st.markdown("#### Methodology & Sources")
    st.write("""
        - **Carbon Intensity:** Based on average grid factors ($gCO_2/kWh$) provided by cloud regions.
        - **Water Scarcity & WUE:** Calculated using industry-standard 1.9 L/kWh average (The Green Grid). Water usage effectiveness (WUE) is a critical operational risk factor in water-stressed regions.
        - **Tree Equivalency:** 22kg $CO_2$/year per mature tree (Source: One Tree Planted / Winrock International).
        - **Olympic Pool Equivalent:** 2.5 million liters standard volume.
        - **Archival Savings:** Assuming a conservative 90% power and water cooling reduction for cold storage tiers (Glacier/Archive classes).
    """)

st.divider()
st.caption("💡 **Recommendation**: Implement a continuous archival policy for data older than 5 years to maintain sustainable storage emissions as your data grows.")
st.caption(f"📊 **Benefits of Archival**: {ARCHIVAL_CARBON_REDUCTION*100:.0f}% $CO_2$ reduction | {ARCHIVAL_WATER_REDUCTION*100:.0f}% water reduction | Cost savings vary by provider.")
st.caption(f"💧 **Water Impact**: Based on industry-standard WUE of 1.9 L/kWh (The Green Grid / EESI data).")
st.caption(f"🌍 **Real-World Comparisons**: 1 Olympic pool = 2.5M liters | 1 mature tree absorbs ~{CO2_PER_TREE_PER_YEAR} kg $CO_2$/year (Winrock International).")
st.caption("Advisor v2.2 | Outcome-Oriented Sustainability Engine | Powered by Green IT Framework.")
