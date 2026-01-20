"""
LVMH Green in Tech - UI Utilities & Homepage
Light Luxury Theme - Interactive Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

def render_logo():
    """Render the LVMH logo image with a fallback to text if the file is missing."""
    
    # 1. SETUP: Define the path to your logo
    # Make sure your file is actually here. 
    # If it is just at the root (not in a folder), change this to "lvmh_logo.png"
    logo_path = "logo/lvmh_logo.png" 

    # 2. RENDER
    if os.path.exists(logo_path):
        # Read the image and convert to Base64 string
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        # Inject the image via HTML for perfect control over size and centering
        st.markdown(f"""
        <div class="logo-section" style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{encoded}" alt="LVMH Logo" style="width: 250px; max-width: 100%; margin-bottom: 10px;">
            <div class="logo-tagline" style="font-family: 'Lato', sans-serif; font-size: 10px; letter-spacing: 4px; color: #666; text-transform: uppercase; margin-top: 5px;">
                Green in Tech Program
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # FALLBACK: If the file is not found, display the Elegant Text (Safety Net)
        st.markdown("""
        <div class="logo-section" style="text-align: center; margin-bottom: 20px;">
            <div style="font-family: 'Playfair Display', serif; font-size: 60px; color: #C5A059; letter-spacing: 8px; margin-bottom: 0px;">LVMH</div>
            <div class="logo-tagline" style="font-family: 'Lato', sans-serif; font-size: 10px; letter-spacing: 4px; color: #666; text-transform: uppercase;">
                Green in Tech Program
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Uncomment the line below if you want to see where Python is looking for the file
        # st.error(f"Debug: Logo file not found at {os.path.abspath(logo_path)}")
# =============================================================================
# GLOBAL STYLES - LIGHT LUXURY THEME
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - cream/white background"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === LIGHT LUXURY BASE === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === COMPLETELY HIDE EXPANDER ARROWS === */
    /* This targets the material icon font that shows "keyboard_arrow" */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* Hide any SVG in expanders */
    [data-testid="stExpander"] svg,
    [data-testid="stExpander"] path,
    .streamlit-expanderHeader svg {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    /* Force hide the icon container */
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
    
    /* Style expander container */
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
    
    /* === LOGO SECTION === */
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
    
    /* === WELCOME HERO === */
    .welcome-hero {
        background: linear-gradient(135deg, #fff 0%, #f8f6f2 50%, #fff 100%);
        border: 1px solid #e8e4dc;
        border-radius: 8px;
        padding: 60px 50px;
        margin: 25px 0 45px 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(138, 108, 74, 0.06);
    }
    
    .welcome-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 3rem !important;
        color: #2c2c2c !important;
        margin-bottom: 20px !important;
        line-height: 1.3 !important;
        font-weight: 500 !important;
        letter-spacing: 2px !important;
    }
    
    .welcome-subtitle {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.3rem;
        color: #6a6a6a;
        line-height: 1.8;
        max-width: 650px;
        margin: 0 auto;
        font-weight: 400;
    }
    
    .welcome-date {
        font-family: 'Montserrat', sans-serif;
        color: #999;
        font-size: 0.7rem;
        margin-top: 30px;
        letter-spacing: 2px;
        text-transform: uppercase;
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
    
    .kpi-delta {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
        font-weight: 500;
        margin-top: 8px;
    }
    
    .kpi-delta-positive {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .kpi-delta-neutral {
        background: #fff3e0;
        color: #e65100;
    }
    
    /* === HELP BUTTON === */
    .help-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        background: #f5f3ef;
        border: 1px solid #d4cfc5;
        border-radius: 50%;
        font-size: 10px;
        color: #8a6c4a;
        cursor: pointer;
        font-weight: 600;
        margin-left: 6px;
        transition: all 0.2s ease;
    }
    
    .help-btn:hover {
        background: #8a6c4a;
        color: #fff;
        border-color: #8a6c4a;
    }
    
    /* === PILLAR CARDS === */
    .pillar-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 8px;
        padding: 28px 22px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .pillar-card:hover {
        border-color: #8a6c4a;
        box-shadow: 0 6px 20px rgba(138, 108, 74, 0.1);
    }
    
    .pillar-icon {
        font-size: 1.8rem;
        margin-bottom: 15px;
        color: #8a6c4a;
    }
    
    .pillar-title {
        font-family: 'Montserrat', sans-serif;
        color: #2c2c2c;
        font-weight: 600;
        font-size: 0.75rem;
        margin-bottom: 10px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    
    .pillar-desc {
        font-family: 'Cormorant Garamond', serif;
        color: #777;
        font-size: 1rem;
        line-height: 1.5;
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
    
    /* === ACTION CARDS === */
    .action-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 40px 30px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .action-card:hover {
        border-color: #8a6c4a;
        box-shadow: 0 12px 40px rgba(138, 108, 74, 0.12);
        transform: translateY(-5px);
    }
    
    .action-icon {
        font-size: 2.5rem;
        margin-bottom: 20px;
        color: #8a6c4a;
    }
    
    .action-title {
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        font-size: 1.5rem;
        margin-bottom: 12px;
        font-weight: 500;
    }
    
    .action-desc {
        font-family: 'Cormorant Garamond', serif;
        color: #777;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    
    /* === SECTION HEADERS === */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 50px 0 28px 0;
        padding-bottom: 15px;
        border-bottom: 2px solid #e8e4dc;
    }
    
    .section-icon {
        font-size: 1.1rem;
        color: #8a6c4a;
    }
    
    .section-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.6rem !important;
        color: #8a6c4a !important;
        margin: 0 !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
    }
    
    /* === DIVIDERS === */
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 50px 0;
    }
    
    /* === STATS === */
    .stat-item {
        text-align: center;
        padding: 20px 0;
    }
    
    .stat-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        color: #2c2c2c;
        font-weight: 500;
    }
    
    .stat-label {
        font-family: 'Montserrat', sans-serif;
        color: #999;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 8px;
    }
    
    /* === DATA INPUT SECTION === */
    .data-input-section {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .data-input-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        color: #8a6c4a;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
    }
    
    /* === CHART CONTAINER === */
    .chart-container {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .chart-label {
        font-family: 'Montserrat', sans-serif;
        color: #888;
        font-size: 0.7rem;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
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
    
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #8a6c4a !important;
        border: 1px solid #8a6c4a !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #8a6c4a !important;
        color: #fff !important;
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: #fff !important;
        border: 1px solid #d4cfc5 !important;
        border-radius: 6px !important;
    }
    
    /* Number input */
    [data-testid="stNumberInput"] > div > div > input {
        background: #fff !important;
        border: 1px solid #d4cfc5 !important;
        border-radius: 6px !important;
    }
    
    /* Slider */
    [data-testid="stSlider"] > div > div > div {
        background: #8a6c4a !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #2c2c2c !important;
        font-family: 'Playfair Display', serif !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #888 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 2px solid #e8e4dc;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #888;
        padding: 12px 25px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 1px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #8a6c4a !important;
        border-bottom: 2px solid #8a6c4a !important;
        margin-bottom: -2px;
    }
    
    /* Info box */
    [data-testid="stAlert"] {
        background: #faf8f5 !important;
        border: 1px solid #e8e4dc !important;
        color: #555 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# DATA & KPI CALCULATIONS - NOW INTERACTIVE
# =============================================================================

def get_default_maison_data():
    """Default Maison energy data - replace with your actual data source"""
    return pd.DataFrame({
        'Maison': ['Louis Vuitton', 'Dior', 'Sephora', 'Tiffany', 'Bulgari', 'Fendi', 'Givenchy'],
        'Current_MWh': [2800, 2200, 1900, 1400, 1100, 900, 700],
        'Target_MWh': [2240, 1760, 1520, 1120, 880, 720, 560],  # -20% targets
        'Devices': [12000, 9500, 8200, 6100, 4800, 3900, 3000],
        'Avg_Device_Age': [4.1, 4.5, 3.8, 4.2, 4.6, 3.9, 4.0]
    })


def calculate_kpis_from_data(maison_df, baseline_carbon=125000):
    """
    Calculate KPIs dynamically from Maison data
    This makes the dashboard INTERACTIVE - when you change data, KPIs update
    """
    total_energy = maison_df['Current_MWh'].sum()
    total_devices = maison_df['Devices'].sum()
    avg_lifespan = (maison_df['Avg_Device_Age'] * maison_df['Devices']).sum() / total_devices
    
    # Carbon calculation (MWh to tonnes CO2)
    carbon_factor = 0.0575  # tonnes CO2 per MWh (France average)
    current_carbon = total_energy * carbon_factor
    carbon_reduction = ((baseline_carbon - current_carbon) / baseline_carbon) * 100
    
    # Energy savings (vs baseline)
    baseline_energy = total_energy * 1.25  # Assume 25% more in 2021
    energy_savings = (baseline_energy - total_energy) * 180  # €180/MWh
    
    # Green score
    target_energy = maison_df['Target_MWh'].sum()
    energy_progress = min(100, ((baseline_energy - total_energy) / (baseline_energy - target_energy)) * 100)
    lifespan_score = min(100, (avg_lifespan / 5) * 100)
    green_score = (carbon_reduction * 0.3 + lifespan_score * 0.25 + 
                   energy_progress * 0.25 + 72 * 0.2)  # 72% circularity assumed
    
    return {
        'carbon_reduction': round(carbon_reduction, 1),
        'current_carbon': round(current_carbon, 0),
        'baseline_carbon': baseline_carbon,
        'device_lifespan': round(avg_lifespan, 1),
        'total_devices': total_devices,
        'energy_savings': round(energy_savings, 0),
        'total_energy': round(total_energy, 0),
        'green_score': round(green_score, 1),
        'target_energy': target_energy
    }


# =============================================================================
# CHART COMPONENTS
# =============================================================================

def create_progress_chart(kpis):
    """Creates progress chart with actual data"""
    years = ['2021', '2022', '2023', '2024', '2025', '2026']
    target = [0, -4, -8, -12, -16, -20]
    
    # Calculate actual based on current reduction
    current_reduction = kpis['carbon_reduction']
    actual = [0, 
              current_reduction * 0.22,
              current_reduction * 0.48,
              current_reduction * 0.75,
              current_reduction,
              None]
    
    fig = go.Figure()
    
    # Target line
    fig.add_trace(go.Scatter(
        x=years, y=target,
        mode='lines+markers',
        name='Target Path',
        line=dict(color='#8a6c4a', width=2, dash='dash'),
        marker=dict(size=8, color='#8a6c4a')
    ))
    
    # Actual progress
    fig.add_trace(go.Scatter(
        x=years[:5], y=actual[:5],
        mode='lines+markers',
        name='Actual Progress',
        line=dict(color='#2e7d32', width=3),
        marker=dict(size=10, color='#2e7d32'),
        fill='tozeroy',
        fillcolor='rgba(46, 125, 50, 0.1)'
    ))
    
    # Current marker
    fig.add_trace(go.Scatter(
        x=['2025'], y=[actual[4]],
        mode='markers+text',
        name='Current',
        marker=dict(size=16, color='#2e7d32', line=dict(color='#fff', width=3)),
        text=[f'{actual[4]:.1f}%'],
        textposition='top center',
        textfont=dict(size=12, color='#2e7d32', family='Montserrat')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#666', family='Montserrat'),
        height=320,
        margin=dict(l=50, r=30, t=40, b=50),
        xaxis=dict(
            showgrid=False,
            linecolor='#e8e4dc',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f0ece4',
            title=dict(text='Carbon Reduction %', font=dict(size=11, color='#888')),
            range=[-25, 5],
            ticksuffix='%',
            tickfont=dict(size=10)
        ),
        legend=dict(
            orientation='h', y=1.1, x=0.5, xanchor='center',
            font=dict(size=10)
        )
    )
    
    return fig


def create_maison_chart(maison_df):
    """Creates Maison energy chart with YOUR ACTUAL DATA"""
    df = maison_df.sort_values('Current_MWh', ascending=True)
    
    fig = go.Figure()
    
    # Current bars
    fig.add_trace(go.Bar(
        y=df['Maison'],
        x=df['Current_MWh'],
        orientation='h',
        name='Current',
        marker=dict(color='#8a6c4a'),
        text=[f"{v:,.0f}" for v in df['Current_MWh']],
        textposition='outside',
        textfont=dict(size=10, family='Montserrat', color='#666')
    ))
    
    # Target markers
    fig.add_trace(go.Scatter(
        y=df['Maison'],
        x=df['Target_MWh'],
        mode='markers',
        name='2026 Target',
        marker=dict(symbol='line-ns', size=25, color='#2e7d32', 
                   line=dict(width=3, color='#2e7d32'))
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#666', family='Montserrat'),
        height=320,
        margin=dict(l=20, r=80, t=40, b=50),
        barmode='overlay',
        xaxis=dict(
            showgrid=True,
            gridcolor='#f0ece4',
            title=dict(text='Energy (MWh/year)', font=dict(size=11, color='#888')),
            tickfont=dict(size=10)
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        legend=dict(
            orientation='h', y=1.1, x=0.5, xanchor='center',
            font=dict(size=10)
        )
    )
    
    return fig


# =============================================================================
# HOMEPAGE COMPONENTS
# =============================================================================

def render_logo():
    """Render the LVMH logo section"""
    st.markdown("""
    <div class="logo-section">
        <div class="logo-text">LVMH</div>
        <div class="logo-tagline">Green in Tech Program</div>
    </div>
    """, unsafe_allow_html=True)


def render_welcome_section():
    """Render the welcome hero section"""
    st.markdown(f"""
    <div class="welcome-hero">
        <h1 class="welcome-title">Welcome to Green in Tech</h1>
        <p class="welcome-subtitle">
            Your strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
        <p class="welcome-date">Last updated · {datetime.now().strftime("%B %d, %Y")}</p>
    </div>
    """, unsafe_allow_html=True)


def render_data_input_section():
    """
    INTERACTIVE DATA INPUT - This is where users can modify data
    and see KPIs update in real-time
    """
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">⚙</span>
        <h2 class="section-title">Dashboard Parameters</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #888; font-size: 0.85rem; margin-bottom: 20px;">
        Adjust parameters below to see how KPIs change. Connect to your actual data sources for real-time updates.
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        baseline = st.number_input(
            "2021 Baseline (tonnes CO₂)", 
            value=125000, 
            step=5000,
            help="Total CO₂ emissions from IT operations in 2021"
        )
    
    with col2:
        energy_adjustment = st.slider(
            "Energy Reduction %",
            min_value=0, max_value=30, value=15,
            help="Overall energy reduction achieved vs 2021"
        )
    
    with col3:
        lifespan_target = st.slider(
            "Avg Device Lifespan (yrs)",
            min_value=3.0, max_value=7.0, value=4.3, step=0.1,
            help="Target average lifespan for IT devices"
        )
    
    with col4:
        selected_maisons = st.multiselect(
            "Maisons to Include",
            options=['All', 'Louis Vuitton', 'Dior', 'Sephora', 'Tiffany', 'Bulgari', 'Fendi', 'Givenchy'],
            default=['All'],
            help="Filter dashboard by specific Maisons"
        )
    
    return baseline, energy_adjustment, lifespan_target, selected_maisons


def render_kpi_section(kpis):
    """Render KPI cards - now using CALCULATED values"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">📊</span>
        <h2 class="section-title">Key Performance Indicators</h2>
    </div>
    """, unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        delta_class = "kpi-delta-positive" if kpis['carbon_reduction'] > 10 else "kpi-delta-neutral"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🌱</div>
            <div class="kpi-label">Carbon Reduction</div>
            <div class="kpi-value">{kpis['carbon_reduction']}<span class="kpi-unit">%</span></div>
            <div class="kpi-delta {delta_class}">↓ vs 2021 baseline</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("How is this calculated?"):
            st.markdown(f"""
            **Formula:** `((Baseline - Current) / Baseline) × 100`
            
            **Current Values:**
            - Baseline (2021): **{kpis['baseline_carbon']:,}** tonnes CO₂
            - Current: **{kpis['current_carbon']:,}** tonnes CO₂
            - Reduction: **{kpis['carbon_reduction']}%**
            
            **Target:** -20% by 2026
            """)
    
    with k2:
        delta_class = "kpi-delta-positive" if kpis['device_lifespan'] > 4 else "kpi-delta-neutral"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💻</div>
            <div class="kpi-label">Avg Device Lifespan</div>
            <div class="kpi-value">{kpis['device_lifespan']}<span class="kpi-unit"> yrs</span></div>
            <div class="kpi-delta {delta_class}">↑ lifecycle extended</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("How is this calculated?"):
            st.markdown(f"""
            **Formula:** `Σ(Device Age × Count) / Total Devices`
            
            **Current Values:**
            - Total Devices: **{kpis['total_devices']:,}**
            - Average Age: **{kpis['device_lifespan']} years**
            
            **Impact:** Each year extended = ~300 kg CO₂ saved
            
            **Target:** 5+ years average
            """)
    
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-label">Energy Savings</div>
            <div class="kpi-value">€{kpis['energy_savings']/1000:.0f}<span class="kpi-unit">K</span></div>
            <div class="kpi-delta kpi-delta-positive">Annual savings</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("How is this calculated?"):
            st.markdown(f"""
            **Formula:** `(Baseline - Current Energy) × €180/MWh`
            
            **Current Values:**
            - Current Usage: **{kpis['total_energy']:,}** MWh/year
            - Savings: **€{kpis['energy_savings']:,}**/year
            
            **Target:** €500K+ annual savings
            """)
    
    with k4:
        delta_class = "kpi-delta-positive" if kpis['green_score'] > 65 else "kpi-delta-neutral"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Green IT Score</div>
            <div class="kpi-value">{kpis['green_score']}<span class="kpi-unit">/100</span></div>
            <div class="kpi-delta {delta_class}">Composite score</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("How is this calculated?"):
            st.markdown(f"""
            **Formula:** Weighted average of 4 pillars
            
            | Pillar | Weight | Score |
            |--------|--------|-------|
            | Carbon | 30% | {kpis['carbon_reduction']:.0f} |
            | Lifespan | 25% | {min(100, kpis['device_lifespan']/5*100):.0f} |
            | Energy | 25% | — |
            | Circularity | 20% | 72 |
            
            **Target:** 80+ by 2026
            """)


def render_charts_section(maison_df, kpis):
    """Render charts with actual data"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">📈</span>
        <h2 class="section-title">Progress & Distribution</h2>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<p class="chart-label">Carbon Reduction Timeline</p>', unsafe_allow_html=True)
        st.plotly_chart(create_progress_chart(kpis), use_container_width=True, config={'displayModeBar': False})
    
    with c2:
        st.markdown('<p class="chart-label">Energy by Maison (Your Data)</p>', unsafe_allow_html=True)
        st.plotly_chart(create_maison_chart(maison_df), use_container_width=True, config={'displayModeBar': False})
    
    # Data source note
    st.caption("💡 **Data Source:** The Maison chart uses sample data. Upload your fleet inventory CSV or connect to your data source for real values.")


def render_context_section():
    """Render program context"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🎯</span>
        <h2 class="section-title">Program Context</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="context-card">
            <div class="context-title">LIFE 360 Program</div>
            <p class="context-text">
                An alliance of Nature and Creativity. LVMH's LIFE 360 program sets ambitious 
                environmental targets across all Maisons, with <strong>Green in Tech</strong> 
                focusing on reducing our technological environmental footprint.
            </p>
        </div>
        
        <div class="context-card">
            <div class="context-title">Our Commitment: -20% by 2026</div>
            <p class="context-text">
                Reduce LVMH's IT environmental footprint by <strong style="color: #2e7d32;">20%</strong> 
                compared to our 2021 baseline, encompassing carbon emissions, energy consumption, 
                and e-waste across all IT operations globally.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 15px 0;">
            <div class="stat-item">
                <div class="stat-value">2026</div>
                <div class="stat-label">Target Year</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">−20%</div>
                <div class="stat-label">Reduction Goal</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">75+</div>
                <div class="stat-label">Maisons Engaged</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_pillars_section():
    """Render program pillars"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🏛</span>
        <h2 class="section-title">Strategic Pillars</h2>
    </div>
    """, unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    
    pillars = [
        ("🔄", "Harmonize", "Unify initiatives across Maisons"),
        ("📊", "Define & Monitor", "Track KPIs at Group level"),
        ("🎛", "Master", "Control environmental impact"),
        ("🚀", "Develop", "Build sustainable IT strategy")
    ]
    
    for col, (icon, title, desc) in zip([p1, p2, p3, p4], pillars):
        with col:
            st.markdown(f"""
            <div class="pillar-card">
                <div class="pillar-icon">{icon}</div>
                <div class="pillar-title">{title}</div>
                <p class="pillar-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def render_insights_section():
    """Render insights"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">💡</span>
        <h2 class="section-title">Strategic Insights</h2>
    </div>
    """, unsafe_allow_html=True)
    
    i1, i2, i3 = st.columns(3)
    
    with i1:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">🔋 High Impact</div>
            <p class="insight-text">
                Server consolidation could reduce energy by <strong>15%</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Details", key="i1"):
            st.session_state['page'] = 'cloud'
            st.rerun()
    
    with i2:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">⏰ Lifecycle</div>
            <p class="insight-text">
                <strong>234 devices</strong> can be extended, saving €450K
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Review", key="i2"):
            st.session_state['page'] = 'equipment'
            st.rerun()
    
    with i3:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">☁️ Cloud</div>
            <p class="insight-text">
                Green regions could cut cloud carbon by <strong>30%</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore", key="i3"):
            st.session_state['page'] = 'cloud'
            st.rerun()


def render_navigation_section():
    """Render navigation cards"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🧭</span>
        <h2 class="section-title">Tools</h2>
    </div>
    """, unsafe_allow_html=True)
    
    nav1, nav2 = st.columns(2)
    
    with nav1:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🖥</div>
            <div class="action-title">Equipment Audit</div>
            <p class="action-desc">Analyze device lifecycle and get ROI recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Equipment Audit", key="nav_eq", use_container_width=True):
            st.session_state['page'] = 'equipment'
            st.rerun()
    
    with nav2:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">☁</div>
            <div class="action-title">Cloud Optimizer</div>
            <p class="action-desc">Optimize storage and plan archival strategies</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Cloud Optimizer", key="nav_cl", use_container_width=True):
            st.session_state['page'] = 'cloud'
            st.rerun()


def render_footer():
    """Render footer"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; 
           letter-spacing: 3px; text-transform: uppercase;">
            LVMH Green in Tech · Alberthon 2025
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN HOMEPAGE FUNCTION
# =============================================================================

def show_home_page():
    """Main function - INTERACTIVE DASHBOARD"""
    inject_global_styles()
    
    render_logo()
    render_welcome_section()
    
    # INTERACTIVE: Data input section
    baseline, energy_adj, lifespan, maisons = render_data_input_section()
    
    # Get data and calculate KPIs dynamically
    maison_df = get_default_maison_data()
    
    # Apply energy adjustment to simulate real-time updates
    maison_df['Current_MWh'] = maison_df['Current_MWh'] * (1 - energy_adj/100)
    maison_df['Avg_Device_Age'] = lifespan
    
    # Filter by selected maisons
    if 'All' not in maisons and len(maisons) > 0:
        maison_df = maison_df[maison_df['Maison'].isin(maisons)]
    
    # Calculate KPIs from the (adjusted) data
    kpis = calculate_kpis_from_data(maison_df, baseline)
    
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    # Display sections with calculated data
    render_kpi_section(kpis)
    render_charts_section(maison_df, kpis)
    render_context_section()
    render_pillars_section()
    render_insights_section()
    render_navigation_section()
    render_footer()
