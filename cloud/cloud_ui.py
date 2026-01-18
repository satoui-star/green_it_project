import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# Custom Metric Helper to allow small sub-text within the "Square"
def render_metric_card(label, value, equivalent_text, equivalent_emoji, help_text=""):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{equivalent_emoji}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-unit">~{equivalent_text}</div>
        </div>
    """, unsafe_allow_html=True)

# Shared CSS for consistent display
st.markdown("""
    <style>
    /* === LIGHT LUXURY BASE === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === COMPLETELY HIDE EXPANDER ARROWS === */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    [data-testid="stExpander"] svg,
    [data-testid="stExpander"] path,
    .streamlit-expanderHeader svg {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    [data-testid="stExpander"] summary > span:first-child,
    [data-testid="stExpander"] details > summary > div:first-child {
        display: none !important;
    }
    
    details summary {
        list-style: none !important;
        list-style-type: none !important;
    }
    
    details summary::-webkit-details-marker,
    details summary::marker {
        display: none !important;
        content: "" !important;
        font-size: 0 !important;
    }
    
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    
    [data-testid="stExpander"] > details > summary {
        padding: 14px 18px !important;
        color: #8a6c4a !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    
    [data-testid="stExpander"] > details > summary:hover {
        color: #6d553a !important;
        background: #faf8f5 !important;
    }
    
    [data-testid="stExpander"] > details[open] > summary {
        border-bottom: 1px solid #e8e4dc !important;
    }
    
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #fdfcfa !important;
        padding: 18px !important;
    }
    
    /* === TYPOGRAPHY === */
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        font-weight: 500 !important;
        letter-spacing: 2px !important;
    }
    
    h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #8a6c4a !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
    }
    
    p, span, div, label, li {
        font-family: 'Montserrat', sans-serif !important;
        color: #4a4a4a !important;
    }
    
    /* === KPI CARDS - PROMINENT === */
    .kpi-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06);
        transition: all 0.3s ease;
        position: relative;
        height: 100%;
    }
    
    .kpi-card:hover {
        box-shadow: 0 8px 30px rgba(138, 108, 74, 0.12);
        transform: translateY(-3px);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 3px 3px;
    }
    
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 12px;
        color: #8a6c4a;
    }
    
    .kpi-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.65rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-weight: 500;
    }
    
    .kpi-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.8rem;
        font-weight: 500;
        color: #2c2c2c;
        line-height: 1;
        margin-bottom: 12px;
    }
    
    .kpi-unit {
        font-family: 'Montserrat', sans-serif;
        font-size: 1rem;
        color: #8a6c4a;
        font-weight: 400;
    }
    
    /* === CONTEXT SECTION === */
    .context-card {
        background: #fff;
        border-left: 3px solid #8a6c4a;
        border-radius: 0 8px 8px 0;
        padding: 25px 30px;
        margin: 18px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    
    .context-title {
        font-family: 'Montserrat', sans-serif;
        color: #8a6c4a;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .context-text {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        line-height: 1.8;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* === INSIGHT CARDS === */
    .insight-card {
        background: linear-gradient(135deg, #f0f7f1 0%, #fff 100%);
        border: 1px solid #c8e6c9;
        border-radius: 8px;
        padding: 24px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.1);
    }
    
    .insight-title {
        font-family: 'Montserrat', sans-serif;
        color: #2e7d32;
        font-weight: 600;
        font-size: 0.7rem;
        margin-bottom: 12px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .insight-text {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* === URGENT ALERT BOX === */
    .urgent-alert {
        background: linear-gradient(135deg, #fef2f2 0%, #fff5f5 100%);
        padding: 28px;
        border-radius: 10px;
        border: 1px solid #fecaca;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.08);
        margin-bottom: 30px;
    }
    
    .urgent-alert h3 {
        color: #991b1b;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.75rem;
    }
    
    .urgent-alert p {
        color: #7f1d1d;
        font-size: 1rem;
        line-height: 1.6;
        font-family: 'Cormorant Garamond', serif !important;
    }
    
    /* === DIVIDERS === */
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 50px 0;
    }
    
    /* === CHART CONTAINER === */
    .chart-container {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    /* === STREAMLIT OVERRIDES === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 6px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-size: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: #6d553a !important;
        box-shadow: 0 6px 20px rgba(138, 108, 74, 0.25) !important;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background: #fff !important;
        border: 1px solid #d4cfc5 !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stNumberInput"] > div > div > input {
        background: #fff !important;
        border: 1px solid #d4cfc5 !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSlider"] > div > div > div {
        background: #8a6c4a !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #2c2c2c !important;
        font-family: 'Playfair Display', serif !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #888 !important;
    }
    
    [data-testid="stAlert"] {
        background: #faf8f5 !important;
        border: 1px solid #e8e4dc !important;
        color: #555 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- VISUALIZATION FUNCTIONS ---

def create_diverging_path_chart(archival_df, reduction_target):
    """PRIMARY VISUALIZATION: Shows the widening gap between action and inaction."""
    fig = go.Figure()
    
    # Line for Business As Usual (destructive path)
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions w/o Archival (kg)'],
        name='Without Action',
        line=dict(color='#ef4444', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='x'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    # Line for Optimized path
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions After Archival (kg)'],
        name='With Strategic Archival',
        line=dict(color='#10b981', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    # Fill the GAP between them
    fig.add_trace(go.Scatter(
        x=archival_df['Year'].tolist() + archival_df['Year'].tolist()[::-1],
        y=archival_df['Emissions w/o Archival (kg)'].tolist() + 
          archival_df['Emissions After Archival (kg)'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(239, 68, 68, 0.2)',
        line=dict(width=0),
        showlegend=True,
        name='Carbon Waste Gap',
        hoverinfo='skip'
    ))
    
    # Add annotation for total gap
    total_gap = (archival_df['Emissions w/o Archival (kg)'] - 
                 archival_df['Emissions After Archival (kg)']).sum()
    
    mid_year = len(archival_df) // 2
    mid_y = (archival_df['Emissions w/o Archival (kg)'].iloc[mid_year] + 
             archival_df['Emissions After Archival (kg)'].iloc[mid_year]) / 2
    
    fig.add_annotation(
        x=archival_df['Year'].iloc[mid_year],
        y=mid_y,
        text=f"<b>Total Avoidable<br>Emissions:<br>{total_gap:,.0f} kg CO₂</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#991b1b",
        ax=-80,
        ay=-40,
        font=dict(size=14, color="#991b1b", family="Arial Black"),
        bgcolor="rgba(254, 242, 242, 0.95)",
        bordercolor="#ef4444",
        borderwidth=2,
        borderpad=8
    )
    
    fig.update_layout(
        title={
            'text': '<b>The Diverging Paths: Action vs Inaction</b><br><sub>Every year of delay widens the sustainability gap</sub>',
            'font': {'size': 20, 'color': '#1e293b'}
        },
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Annual CO₂ Emissions (kg)</b>",
        height=550,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        plot_bgcolor='#f8fafc',
        paper_bgcolor='white'
    )
    
    return fig

def run_cloud_optimizer():
    """Function to render the Cloud Optimizer page."""
    st.title("Cloud Storage Sustainability Advisor")
    st.write("Optimize your data center footprint through intelligent archival strategies.")

    # --- INPUTS ---
    st.subheader("Settings")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        selected_providers = st.multiselect("Cloud Providers", options=df_cloud['Provider'].unique().tolist(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("CO₂ Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)
    with c5:
        data_growth_rate = st.slider("Data Growth Rate (%/year)", 0, 50, 15)

    # Calculation Prep
    storage_gb = storage_tb * 1024
    
    # Calculate Blended Intensity for selected providers
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    std_co2 = filtered['CO2_kg_TB_Month'].iloc[0] if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000
    
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water_liters = calculate_annual_water(storage_gb)
    
    # Yearly Logic: Target is relative to growth to allow Hot Data growth sustainably
    target_reduction_factor = (1 - reduction_target / 100)

    # Convert Water to Showers and CO2 to Trees
    current_showers = current_water_liters / LITERS_PER_SHOWER
    current_trees = current_emissions / CO2_PER_TREE_PER_YEAR

    # --- ANNUAL SNAPSHOT (DIAGNOSTIC) ---
    st.divider()
    st.subheader("Current Annual Baseline")
    st.caption("These metrics show your current yearly impact before optimization.")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Annual Carbon Footprint", f"{current_emissions:,.0f} kg CO₂", f"{current_trees:,.0f} Trees", "🌳")
    with m2:
        render_metric_card("Annual Water Usage", f"{current_water_liters:,.0f} Liters", f"{current_showers:,.0f} Showers", "🚿")
    with m3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Efficiency Goal</div>
            <div class="kpi-value" style="color: #059669;">-{reduction_target}%</div>
            <div class="kpi-unit">Relative reduction vs growth</div>
        </div>""", unsafe_allow_html=True)

    # --- STRATEGY ---
    st.subheader("🚨 ACTION REQUIRED IMMEDIATELY")
    
    # Run the math engine manually to ensure dynamic relative reduction in the table
    results = []
    for yr in range(1, int(projection_years) + 1):
        # BAU Data Growth
        projected_storage_gb = storage_gb * ((1 + data_growth_rate / 100) ** yr)
        bau_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        bau_water = calculate_annual_water(projected_storage_gb)
        bau_cost = calculate_annual_cost(projected_storage_gb, 0, 0.022, 0.004)
        
        # TARGET: Reduce current year's BAU emissions by the target %
        # This prevents a "flat line" and allows optimized emissions to grow sustainably
        target_emissions_kg = bau_emissions * target_reduction_factor
        
        # Archival calculation to reach target
        # Logic: (BAU_E - Target_E) / (CO2_saved_per_GB_archived)
        co2_per_gb_std = calculate_annual_emissions(1, carbon_intensity)
        archived_gb_needed = (bau_emissions - target_emissions_kg) / (co2_per_gb_std * 0.90)
        archived_gb_needed = min(max(archived_gb_needed, 0), projected_storage_gb)
        
        # Final optimized metrics
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
    
    archival_df = pd.DataFrame(results)
    year_1 = archival_df.iloc[0]
    
    # Urgent Disclaimer Card
    st.markdown(f"""
    <div class="urgent-alert">
        <h3>Immediate Intervention Required</h3>
        <p><b>CRITICAL:</b> Your emissions are directly tied to data growth. To maintain a sustainable <b>{reduction_target}%</b> efficiency gain, you must archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        this year. In the table below, notice how <b>Emissions After Archival</b> now scale with your business growth, ensuring that your 'Hot' tier remains optimized rather than artificially capped.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- CUMULATIVE IMPACT ---
    st.subheader(f" Total {projection_years}-Year Environmental Gap")
    
    total_co2_no_action = archival_df["Emissions w/o Archival (kg)"].sum()
    total_co2_optimized = archival_df["Emissions After Archival (kg)"].sum()
    total_savings_co2 = total_co2_no_action - total_co2_optimized
    total_savings_euro = archival_df["Cost Savings (€)"].sum()
    total_water_saved_liters = archival_df["Water Savings (L)"].sum()
    
    total_showers_saved = total_water_saved_liters / LITERS_PER_SHOWER
    total_trees_equivalent = total_savings_co2 / CO2_PER_TREE_PER_YEAR

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Total CO₂ Saved", f"{total_savings_co2:,.0f} kg CO₂", f"{total_trees_equivalent:,.0f} Trees", "🌳")
    with k2:
        render_metric_card("Total Water Reclaimed", f"{total_water_saved_liters:,.0f} Liters", f"{total_showers_saved:,.0f} Showers", "🚿")
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Total Financial ROI</div>
            <div class="kpi-value">€{total_savings_euro:,.0f}</div>
            <div class="kpi-unit">Avoided Costs over {projection_years}y</div>
        </div>""", unsafe_allow_html=True)

    # --- NEW VISUALIZATIONS SECTION ---
    st.write("###  Visual Impact Analysis")
    st.caption("Diverging path visualization showing the magnitude and urgency of action")

    # PRIMARY: Diverging Path Chart
    st.plotly_chart(
        create_diverging_path_chart(archival_df, reduction_target),
        use_container_width=True,
        key="diverging_path"
    )

    # --- TECHNICAL BREAKDOWN ---
    with st.expander("🧬 View Technical Breakdown & Data Evolution"):
        st.write("Detailed annualized metrics. Note how 'Emissions After Archival' increases relative to data growth, acknowledging business scaling.")
        
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
    
    # --- METHODOLOGY SECTION ---
    st.divider()
    st.write("**Methodology & Calculation Logic**")
    st.write(f"""
        -  **Carbon Intensity:** Calculated at {carbon_intensity:.0f} gCO₂/kWh based on cloud region energy mix.
        -  **Water Equivalency:** 1 Shower is standardized at **{LITERS_PER_SHOWER} Liters** (Average duration and flow rate).
        -  **Tree Equivalency:** 1 Mature tree offsets **{CO2_PER_TREE_PER_YEAR} kg CO₂** per year (Winrock/One Tree Planted).
        -  **Dynamic Scaling:** Unlike a static carbon cap, this model applies the reduction target to each year's projected growth. This means 'Emissions After Archival' grows at a sustainable rate rather than staying constant.
    """)

# Main entry
if __name__ == "__main__":
    st.title("Élysia Cloud Solution")
    st.markdown("### Strategic decision-making model for a sustainable cloud storage.")
    
    st.divider()
    run_cloud_optimizer()
