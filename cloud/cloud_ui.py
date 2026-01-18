import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

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
    page_title="Élysia Cloud Solution",
    page_icon="🌱",
    layout="wide"
)

# =============================================================================
# GLOBAL STYLES - LIGHT LUXURY THEME
# =============================================================================

def inject_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Expander Styling */
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

    /* Typography */
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

    /* Logo Section */
    .logo-section {
        text-align: center;
        padding: 40px 0 30px 0;
        border-bottom: 1px solid #e8e4dc;
        margin-bottom: 35px;
        background: linear-gradient(180deg, #fff 0%, #faf9f7 100%);
    }
    
    .logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #2c2c2c;
        letter-spacing: 12px;
        font-weight: 400;
        margin-bottom: 12px;
    }
    
    .logo-tagline {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 4px;
        color: #8a6c4a;
        text-transform: uppercase;
    }

    /* KPI Cards */
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
        font-size: 2.2rem;
        font-weight: 500;
        color: #2c2c2c;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    
    .kpi-equivalent {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem;
        color: #8a6c4a;
        font-weight: 400;
    }

    /* Urgent Alert */
    .urgent-alert {
        background: #fff;
        border-left: 5px solid #8a6c4a;
        border-radius: 0 8px 8px 0;
        padding: 25px 30px;
        margin: 18px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    
    .urgent-alert h3 {
        font-family: 'Montserrat', sans-serif;
        color: #8a6c4a;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .urgent-alert p {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        line-height: 1.6;
        font-size: 1.2rem;
        font-weight: 400;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 50px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid #e8e4dc;
    }
    
    .section-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.6rem !important;
        color: #8a6c4a !important;
        margin: 0 !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
    }

    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 40px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def render_logo():
    st.markdown("""
    <div class="logo-section">
        <div class="logo-text">ÉLYSIA</div>
        <div class="logo-tagline">Green in Tech Program</div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, equivalent_text, equivalent_emoji):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-equivalent">{equivalent_emoji} ~{equivalent_text}</div>
        </div>
    """, unsafe_allow_html=True)

# --- VISUALIZATION FUNCTIONS ---

def create_diverging_path_chart(archival_df, reduction_target):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions w/o Archival (kg)'],
        name='Without Action',
        line=dict(color='#ef4444', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='x'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=archival_df['Year'],
        y=archival_df['Emissions After Archival (kg)'],
        name='With Strategic Archival',
        line=dict(color='#10b981', width=4),
        mode='lines+markers',
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Year %{x}</b><br>Emissions: %{y:,.0f} kg CO₂<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=archival_df['Year'].tolist() + archival_df['Year'].tolist()[::-1],
        y=archival_df['Emissions w/o Archival (kg)'].tolist() + 
          archival_df['Emissions After Archival (kg)'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(239, 68, 68, 0.1)',
        line=dict(width=0),
        showlegend=True,
        name='Carbon Waste Gap',
        hoverinfo='skip'
    ))
    
    total_gap = (archival_df['Emissions w/o Archival (kg)'] - 
                 archival_df['Emissions After Archival (kg)']).sum()
    
    mid_year = len(archival_df) // 2
    mid_y = (archival_df['Emissions w/o Archival (kg)'].iloc[mid_year] + 
             archival_df['Emissions After Archival (kg)'].iloc[mid_year]) / 2
    
    fig.add_annotation(
        x=archival_df['Year'].iloc[mid_year],
        y=mid_y,
        text=f"<b>Avoidable Gap:<br>{total_gap:,.0f} kg CO₂</b>",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#8a6c4a",
        font=dict(size=12, color="#2c2c2c", family="Montserrat"),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#e8e4dc",
        borderwidth=1,
        borderpad=6
    )
    
    fig.update_layout(
        title={
            'text': 'The Diverging Paths: Action vs Inaction',
            'font': {'size': 20, 'family': 'Playfair Display', 'color': '#2c2c2c'}
        },
        xaxis_title="Year",
        yaxis_title="Annual CO₂ Emissions (kg)",
        height=550,
        hovermode='x unified',
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Montserrat')
    )
    
    return fig

def run_cloud_optimizer():
    inject_global_styles()
    render_logo()

    st.markdown('<h1 style="text-align: center;">Sustainability Advisor</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6a6a6a; font-family: \'Cormorant Garamond\', serif; font-size: 1.2rem;">Strategic modeling for carbon-optimized cloud infrastructure.</p>', unsafe_allow_html=True)

    # --- INPUTS ---
    st.markdown('<div class="section-header"><h2 class="section-title">Scenario Parameters</h2></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        selected_providers = st.multiselect("Cloud Providers", options=df_cloud['Provider'].unique().tolist(), default=["AWS"])
    with c2:
        storage_tb = st.number_input("Total Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c3:
        reduction_target = st.slider("Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.number_input("Projection Period (Years)", 1, 10, 5)
    with c5:
        data_growth_rate = st.slider("Growth Rate (%/year)", 0, 50, 15)

    # Calculation Prep
    storage_gb = storage_tb * 1024
    filtered = df_cloud[df_cloud['Provider'].isin(selected_providers if selected_providers else ["AWS"])]
    std_co2 = filtered['CO2_kg_TB_Month'].iloc[0] if not filtered.empty else 6.0
    carbon_intensity = (std_co2 * 12 / (1024 * 1.2)) * 1000
    
    current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
    current_water_liters = calculate_annual_water(storage_gb)
    target_reduction_factor = (1 - reduction_target / 100)

    # Convert Water to Showers and CO2 to Trees
    current_showers = current_water_liters / LITERS_PER_SHOWER
    current_trees = current_emissions / CO2_PER_TREE_PER_YEAR

    # --- ANNUAL SNAPSHOT ---
    st.markdown('<div class="section-header"><h2 class="section-title">Current Annual Baseline</h2></div>', unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Annual Carbon Footprint", f"{current_emissions:,.0f} kg CO₂", f"{current_trees:,.0f} Trees", "🌳")
    with m2:
        render_metric_card("Annual Water Usage", f"{current_water_liters:,.0f} Liters", f"{current_showers:,.0f} Showers", "🚿")
    with m3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Efficiency Goal</div>
                <div class="kpi-value" style="color: #8a6c4a;">-{reduction_target}%</div>
                <div class="kpi-equivalent">🎯 Relative reduction vs growth</div>
            </div>
        """, unsafe_allow_html=True)

    # --- STRATEGY ---
    results = []
    for yr in range(1, int(projection_years) + 1):
        projected_storage_gb = storage_gb * ((1 + data_growth_rate / 100) ** yr)
        bau_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        bau_water = calculate_annual_water(projected_storage_gb)
        bau_cost = calculate_annual_cost(projected_storage_gb, 0, 0.022, 0.004)
        
        target_emissions_kg = bau_emissions * target_reduction_factor
        co2_per_gb_std = calculate_annual_emissions(1, carbon_intensity)
        archived_gb_needed = (bau_emissions - target_emissions_kg) / (co2_per_gb_std * 0.90)
        archived_gb_needed = min(max(archived_gb_needed, 0), projected_storage_gb)
        
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
    
    st.markdown('<div class="section-header"><h2 class="section-title">Action Strategy</h2></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="urgent-alert">
        <h3>Strategic Recommendation</h3>
        <p>To maintain a sustainable <b>{reduction_target}%</b> efficiency gain, you must archive <b>{year_1['Data to Archive (TB)']:.1f} TB</b> 
        this year. Emissions after archival will scale with your business growth, ensuring infrastructure remains optimized.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- CUMULATIVE IMPACT ---
    st.markdown('<div class="section-header"><h2 class="section-title">Cumulative Forecast</h2></div>', unsafe_allow_html=True)
    
    total_co2_no_action = archival_df["Emissions w/o Archival (kg)"].sum()
    total_co2_optimized = archival_df["Emissions After Archival (kg)"].sum()
    total_savings_co2 = total_co2_no_action - total_co2_optimized
    total_savings_euro = archival_df["Cost Savings (€)"].sum()
    total_water_saved_liters = archival_df["Water Savings (L)"].sum()
    
    total_showers_saved = total_water_saved_liters / LITERS_PER_SHOWER
    total_trees_equivalent = total_savings_co2 / CO2_PER_TREE_PER_YEAR

    k1, k2, k3 = st.columns(3)
    with k1:
        render_metric_card("Total CO₂ Saved", f"{total_savings_co2:,.0f} kg", f"{total_trees_equivalent:,.0f} Trees", "🌳")
    with k2:
        render_metric_card("Total Water Saved", f"{total_water_saved_liters:,.0f} L", f"{total_showers_saved:,.0f} Showers", "🚿")
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Financial ROI</div>
            <div class="kpi-value">€{total_savings_euro:,.0f}</div>
            <div class="kpi-equivalent">💰 Over {projection_years}y period</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # PRIMARY: Diverging Path Chart
    st.plotly_chart(
        create_diverging_path_chart(archival_df, reduction_target),
        use_container_width=True,
        key="diverging_path"
    )

    # --- TECHNICAL BREAKDOWN ---
    with st.expander("Technical Breakdown & Data Evolution"):
        st.write("Detailed annualized metrics highlighting sustainable infrastructure scaling.")
        
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
    
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 30px 0;">
            <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase;">
                ÉLYSIA SUSTAINABILITY FRAMEWORK · ALBERTHON 2025
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run_cloud_optimizer()
