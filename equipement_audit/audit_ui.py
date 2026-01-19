"""
Élysia - Sustainable IT Intelligence
======================================
LVMH · Digital Sustainability Division

Version: 3.0.0 (Production)
Complete UI with:
- Luxury visual design
- CSV upload for fleet analysis
- Device simulator with full results
- Strategy trajectory chart
- First 3 Actions section
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import io
import uuid
import time

# =============================================================================
# BACKEND IMPORTS
# =============================================================================

# Add AFTER your existing imports
from calculator import (
    ShockCalculator, HopeCalculator, StrategySimulator,
    validate_fleet_data, validate_device_inputs,
    generate_demo_fleet, generate_synthetic_fleet,
    export_recommendations_to_csv, generate_markdown_report,
    FleetAnalyzer, RecommendationEngine,
    DeviceRecommendation, StrategyResult
)
# ADD THESE NEW IMPORTS
from credibility_ui import (
    inject_credibility_css,
    show_general_disclaimer,
    show_stranded_value_disclaimer,
    enhanced_metric_card,
    sources_expander,
    render_methodology_tab,
)
from audit_logger import audit_log
try:
    from reference_data_API import (
        PERSONAS, DEVICES, STRATEGIES, AVERAGES,
        FLEET_SIZE_OPTIONS, FLEET_AGE_OPTIONS, GRID_CARBON_FACTORS,
        get_device_names, get_persona_names, get_country_codes, get_all_sources
    )
    from calculator import (
        ShockCalculator, HopeCalculator, StrategySimulator,
        TCOCalculator, CO2Calculator, RecommendationEngine,
        FleetAnalyzer, generate_demo_fleet
    )
    BACKEND_READY = True
except ImportError as e:
    BACKEND_READY = False
    IMPORT_ERROR = str(e)

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Élysia | LVMH Sustainable IT",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# LUXURY CSS THEME
# =============================================================================
LUXURY_CSS = """
<style>
/* ============================================
   FONTS
   ============================================ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

/* ============================================
   CSS VARIABLES
   ============================================ */
:root {
    --cream: #FAFAF8;
    --warm-white: #F5F3EF;
    --white: #FFFFFF;
    --border: #E8E4DD;
    --border-dark: #D4CFC5;
    --gold: #8a6c4a;
    --gold-light: #a8896a;
    --gold-dark: #6d5539;
    --text-dark: #2D2A26;
    --text-mid: #6B6560;
    --text-light: #9A958E;
    --success: #4A7C59;
    --success-bg: #E8F5E9;
    --danger: #9E4A4A;
    --danger-bg: #FFEBEE;
    --warning: #C4943A;
}

/* ============================================
   BASE
   ============================================ */
.stApp {
    background: var(--cream) !important;
}

#MainMenu, footer, header, .stDeployButton {
    visibility: hidden !important;
    display: none !important;
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: var(--text-dark) !important;
    font-weight: 500 !important;
}

p, span, div, label, li, td, th {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* ============================================
   LUXURY HEADER
   ============================================ */
.lux-header {
    background: linear-gradient(180deg, var(--white) 0%, var(--cream) 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.5rem 0 1.25rem 0;
    margin-bottom: 2rem;
    text-align: center;
}

.lux-header-brand {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.lux-header-icon {
    font-size: 1.75rem;
}

.lux-header-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 500;
    color: var(--gold);
    letter-spacing: 0.08em;
}

.lux-header-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-light);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ============================================
   ACT BADGE
   ============================================ */
.act-badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    background: var(--warm-white);
    border: 1px solid var(--border);
    padding: 0.6rem 2rem;
    border-radius: 30px;
    margin-bottom: 1.5rem;
}

/* ============================================
   OPENING SCREEN
   ============================================ */
.opening-wrap {
    min-height: 60vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
}

.opening-brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.opening-icon {
    font-size: 3.5rem;
}

.opening-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 4.5rem;
    font-weight: 500;
    color: var(--gold);
    letter-spacing: 0.08em;
}

.opening-tagline {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.5rem;
    font-style: italic;
    color: var(--text-mid);
    line-height: 1.8;
    max-width: 500px;
}

/* ============================================
   METRIC CARDS (Luxury)
   ============================================ */
.metric-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem 1.5rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
    height: 100%;
}

.metric-card:hover {
    border-color: var(--gold);
    box-shadow: 0 8px 24px rgba(138, 108, 74, 0.12);
    transform: translateY(-4px);
}

.metric-card-value {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 3rem;
    font-weight: 500;
    color: var(--text-dark);
    line-height: 1.1;
    margin-bottom: 0.5rem;
}

.metric-card-value.gold { color: var(--gold); }
.metric-card-value.danger { color: var(--danger); }
.metric-card-value.success { color: var(--success); }

.metric-card-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-mid);
}

.metric-card-logic {
    margin-top: 1.25rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border);
    text-align: left;
}

.metric-card-logic-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--gold);
    margin-bottom: 0.75rem;
}

.metric-card-logic-formula {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.8rem;
    color: var(--success);
    background: var(--warm-white);
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    margin-bottom: 0.75rem;
}

.metric-card-logic-list {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: var(--text-mid);
    line-height: 1.8;
    margin: 0;
    padding-left: 1rem;
}

.metric-card-logic-source {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-style: italic;
    color: var(--text-light);
    margin-top: 0.75rem;
}

/* ============================================
   COMPARISON CARDS
   ============================================ */
.compare-card {
    border: 2px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.compare-card.current {
    background: var(--danger-bg);
    border-color: var(--danger);
}

.compare-card.target {
    background: var(--success-bg);
    border-color: var(--success);
}

.compare-badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.5rem 1.25rem;
    border-radius: 20px;
    margin-bottom: 1.25rem;
}

.compare-card.current .compare-badge {
    background: var(--danger);
    color: white;
}

.compare-card.target .compare-badge {
    background: var(--success);
    color: white;
}

.compare-value {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 2.75rem;
    font-weight: 500;
    color: var(--text-dark);
    margin: 0.5rem 0;
}

.compare-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-mid);
}

.compare-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    color: var(--gold);
    font-weight: 300;
}

/* ============================================
   SUMMARY STATS ROW
   ============================================ */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 4rem;
    margin: 2.5rem 0;
    flex-wrap: wrap;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 2.25rem;
    font-weight: 500;
    color: var(--success);
}

.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-mid);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.25rem;
}

/* ============================================
   GOLD TICKET (Winner)
   ============================================ */
.gold-ticket {
    background: linear-gradient(135deg, #FAF6F1 0%, #FFF9F0 50%, #FAF6F1 100%);
    border: 2px solid var(--gold);
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 20px rgba(138, 108, 74, 0.15);
}

.gold-ticket::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--gold-dark), var(--gold), var(--gold-light), var(--gold), var(--gold-dark));
    border-radius: 16px 16px 0 0;
}

.gold-ticket-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.75rem;
}

.gold-ticket-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.25rem;
    font-weight: 500;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
}

.gold-ticket-desc {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: var(--text-mid);
    max-width: 600px;
    margin: 0 auto;
}

/* ============================================
   IMPACT METRICS ROW
   ============================================ */
.impact-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin: 2rem 0;
}

.impact-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.75rem;
    text-align: center;
    transition: all 0.3s ease;
}

.impact-card:hover {
    border-color: var(--gold);
}

.impact-value {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 2.5rem;
    font-weight: 500;
    color: var(--gold);
}

.impact-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-mid);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.5rem;
}

/* ============================================
   ACTIONS BOX
   ============================================ */
.actions-box {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 2rem;
}

.actions-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.25rem;
    color: var(--text-dark);
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.action-row {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border);
}

.action-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.action-num {
    width: 32px;
    height: 32px;
    min-width: 32px;
    background: var(--gold);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
}

.action-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: var(--text-dark);
    line-height: 1.6;
}

/* ============================================
   ALERT BOXES
   ============================================ */
.alert-box {
    padding: 1.25rem 1.5rem;
    border-radius: 0 10px 10px 0;
    margin: 1.5rem 0;
}

.alert-box.warning {
    background: var(--danger-bg);
    border-left: 4px solid var(--danger);
}

.alert-box.success {
    background: var(--success-bg);
    border-left: 4px solid var(--success);
}

.alert-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.alert-box.warning .alert-title { color: var(--danger); }
.alert-box.success .alert-title { color: var(--success); }

.alert-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-mid);
    line-height: 1.6;
}

/* ============================================
   RECOMMENDATION BOX
   ============================================ */
.reco-box {
    background: linear-gradient(135deg, #FAF6F1 0%, #F5EFE6 100%);
    border: 2px solid var(--gold);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin: 1.5rem 0;
}

.reco-box.keep {
    border-color: var(--success);
    background: var(--success-bg);
}

.reco-box.new {
    border-color: #6A8CAA;
    background: #EBF2F7;
}

.reco-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.5rem;
}

.reco-box.keep .reco-label { color: var(--success); }
.reco-box.new .reco-label { color: #6A8CAA; }

.reco-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.75rem;
    font-weight: 500;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
}

.reco-rationale {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-mid);
}

/* ============================================
   FORM STYLING
   ============================================ */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-dark) !important;
}

.stSelectbox > div > div:hover,
.stNumberInput > div > div > input:hover {
    border-color: var(--gold) !important;
}

.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(138, 108, 74, 0.1) !important;
}

.stSlider > div > div > div[data-baseweb="slider"] > div {
    background: var(--border) !important;
}

.stSlider > div > div > div[data-baseweb="slider"] > div > div {
    background: var(--gold) !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--gold) !important;
    border: 3px solid white !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
}

/* Dropdown */
[data-baseweb="menu"],
[data-baseweb="popover"] > div {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
}

[data-baseweb="menu"] li {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-dark) !important;
}

[data-baseweb="menu"] li:hover {
    background: var(--warm-white) !important;
}

/* ============================================
   BUTTONS
   ============================================ */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    background: var(--gold) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(138, 108, 74, 0.25) !important;
}

.stButton > button:hover {
    background: var(--gold-dark) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(138, 108, 74, 0.35) !important;
}

/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    box-shadow: none !important;
}

.stDownloadButton > button:hover {
    background: var(--gold) !important;
    color: white !important;
}

/* ============================================
   TABS
   ============================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-mid) !important;
    background: transparent !important;
    border: none !important;
    padding: 1rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--gold) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}

/* ============================================
   FILE UPLOADER
   ============================================ */
.stFileUploader > div {
    background: var(--white) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

.stFileUploader > div:hover {
    border-color: var(--gold) !important;
    background: var(--warm-white) !important;
}

/* ============================================
   TABLES
   ============================================ */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ============================================
   FOOTER
   ============================================ */
.lux-footer {
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
    border-top: 1px solid var(--border);
}

.lux-footer-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-light);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
</style>
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def fmt_currency(val):
    """Format as Euro with K/M suffix."""
    if val is None:
        return "—"
    if abs(val) >= 1_000_000:
        return f"€{val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"€{val/1_000:,.0f}K"
    return f"€{val:,.0f}"


def fmt_co2(val_kg):
    """Format CO2 in kg or tonnes."""
    if val_kg is None:
        return "—"
    if abs(val_kg) >= 1000:
        return f"{val_kg/1000:,.0f}t"
    return f"{val_kg:.0f}kg"


def render_header():
    """Render the luxury header."""
    st.markdown("""
    <div class="lux-header">
        <div class="lux-header-brand">
            <span class="lux-header-icon">🌿</span>
            <span class="lux-header-title">ÉLYSIA</span>
        </div>
        <div class="lux-header-sub">Sustainable IT Intelligence</div>
    </div>
    """, unsafe_allow_html=True)


def render_act_badge(num, title):
    """Render act indicator badge."""
    st.markdown(f"""
    <div style="text-align: center;">
        <span class="act-badge">ACT {num} · {title}</span>
    </div>
    """, unsafe_allow_html=True)


def create_trajectory_chart(results, target_pct, current_co2):
    """Create CO2 trajectory projection chart."""
    fig = go.Figure()
    
    colors = {
        "Do Nothing": "#9E4A4A",
        "20% Refurbished": "#C4943A",
        "40% Refurbished": "#8a6c4a",
        "60% Refurbished": "#4A7C59",
        "Lifecycle Extension": "#6A8CAA",
        "Combined Strategy": "#2E7D32",
    }
    
    for result in results:
        name = result.strategy_name
        monthly = result.monthly_co2
        
        if monthly:
            months = list(range(len(monthly)))
            is_baseline = name == "Do Nothing"
            
            fig.add_trace(go.Scatter(
                x=months,
                y=monthly,
                mode='lines',
                name=name,
                line=dict(
                    color=colors.get(name, "#8a6c4a"),
                    width=3 if not is_baseline else 2,
                    dash='dash' if is_baseline else 'solid'
                ),
                hovertemplate=f"<b>{name}</b><br>Month %{{x}}<br>CO₂: %{{y:,.0f}}t<extra></extra>"
            ))
    
    target_co2 = current_co2 * (1 + target_pct / 100)
    
    fig.add_hline(
        y=target_co2,
        line_dash="dot",
        line_color="#8a6c4a",
        line_width=2,
        annotation_text=f"TARGET: {target_co2:,.0f}t ({target_pct}%)",
        annotation_position="right",
        annotation_font=dict(color="#8a6c4a", size=11, family="Inter")
    )
    
    fig.add_hrect(
        y0=0, y1=target_co2,
        fillcolor="rgba(74, 124, 89, 0.06)",
        line_width=0
    )
    
    fig.update_layout(
        title=dict(
            text="CO₂ Trajectory by Strategy",
            font=dict(family="Playfair Display", size=18, color="#2D2A26"),
            x=0.5
        ),
        xaxis_title="Months",
        yaxis_title="Annual CO₂ (tonnes)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#6B6560"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)"
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        xaxis=dict(gridcolor='#E8E4DD', zeroline=False),
        yaxis=dict(gridcolor='#E8E4DD', zeroline=False, tickformat=",d"),
        hovermode="x unified"
    )
    
    return fig


def create_fleet_age_chart():
    """Fleet age distribution bar chart."""
    data = []
    for key, info in FLEET_AGE_OPTIONS.items():
        label = info["label"].split("(")[0].strip()
        data.append({
            "Category": label,
            "Years": info["estimate"],
        })
    
    df = pd.DataFrame(data)
    
    fig = go.Figure(go.Bar(
        x=df["Category"],
        y=df["Years"],
        marker_color="#8a6c4a",
        text=df["Years"].apply(lambda x: f"{x}y"),
        textposition='outside',
        textfont=dict(family="Inter", size=12, color="#6B6560")
    ))
    
    fig.update_layout(
        title=dict(text="Fleet Age Categories", font=dict(family="Playfair Display", size=16), x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#6B6560"),
        xaxis=dict(title="", gridcolor='#E8E4DD'),
        yaxis=dict(title="Average Age (years)", gridcolor='#E8E4DD'),
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False
    )
    
    return fig


def create_device_co2_chart():
    """CO2 by device category donut chart."""
    categories = {}
    for name, device in DEVICES.items():
        cat = device.get("category", "Other")
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += device["co2_manufacturing_kg"]
    
    labels = list(categories.keys())
    values = list(categories.values())
    
    colors = ["#8a6c4a", "#4A7C59", "#C4943A", "#6A8CAA", "#9E4A4A", "#a8896a", "#6d5539", "#7B9E89"]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker_colors=colors[:len(labels)],
        textinfo='label+percent',
        textfont=dict(family="Inter", size=11),
        hovertemplate="<b>%{label}</b><br>%{value:.0f} kg CO₂<br>%{percent}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text="CO₂ by Device Category", font=dict(family="Playfair Display", size=16), x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#6B6560"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=60, b=80),
        annotations=[dict(
            text="Manufacturing<br>CO₂",
            x=0.5, y=0.5,
            font_size=12, font_family="Inter", font_color="#6B6560",
            showarrow=False
        )]
    )
    
    return fig


# =============================================================================
# ACT SCREENS
# =============================================================================

def render_opening():
    """Opening screen."""
    st.markdown("""
    <div class="opening-wrap">
        <div class="opening-brand">
            <span class="opening-icon">🌿</span>
            <span class="opening-title">ÉLYSIA</span>
        </div>
        <div class="opening-tagline">
            "Every device tells a story.<br>
            What story is your fleet telling?"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Discover →", key="btn_start", use_container_width=True):
            st.session_state["stage"] = "shock_q"
            st.rerun()


def render_shock_question():
    """Act 0: Baseline calibration (pre-shock)."""
    render_header()
    render_act_badge(0, "CALIBRATION")

    st.markdown(
        "<h2 style='text-align: center; margin-bottom: 0.75rem;'>Calibrate your baseline</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#6B6560; margin-bottom: 2rem;'>"
        "These inputs personalize the shock numbers and your roadmap."
        "</p>",
        unsafe_allow_html=True
    )

    PH = "— Select —"

    refresh_options = [PH, "20% (≈ 5-year cycle)", "25% (≈ 4-year cycle)", "30% (≈ 3-year cycle)"]
    refresh_map = {20: 5, 25: 4, 30: 3}

    geo_options = [PH, "France", "Germany", "United Kingdom", "Outside EU", "Mixed / global"]
    geo_map = {
        "France": "FR",
        "Germany": "DE",
        "United Kingdom": "GB",
        "Outside EU": "US",
        "Mixed / global": "MIXED",
    }

    target_options = ["— Optional —", "-20% by 2026 (LIFE 360)", "-30%", "-40%"]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("act0_form"):
            st.markdown("**1) Fleet size**")
            fleet_choice = st.selectbox(
                "Fleet size",
                options=[PH] + list(FLEET_SIZE_OPTIONS.keys()),
                format_func=lambda x: x if x == PH else f"{FLEET_SIZE_OPTIONS[x]['label']} — {FLEET_SIZE_OPTIONS[x]['description']}",
                key="act0_fleet_choice",
                label_visibility="collapsed",
            )

            if fleet_choice != PH:
                est = FLEET_SIZE_OPTIONS[fleet_choice]["estimate"]
                st.markdown(
                    f"""
                    <div style="text-align: center; margin: 1.25rem 0;">
                        <span style="background: #F5F3EF; padding: 0.6rem 1.25rem; border-radius: 25px;
                                     font-size: 0.9rem; color: #6B6560; border: 1px solid #E8E4DD;">
                            📊 Estimated: <strong style="color: #2D2A26;">{est:,}</strong> devices
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**2) Refresh rate (% replaced per year)**")
            refresh_choice = st.selectbox(
                "Refresh rate",
                options=refresh_options,
                key="act0_refresh_choice",
                label_visibility="collapsed",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**3) Geography (where most devices are located)**")
            geo_choice = st.selectbox(
                "Geography",
                options=geo_options,
                key="act0_geo_choice",
                label_visibility="collapsed",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**4) Do you already buy refurbished devices? (optional)**")
            refurb_mode = st.selectbox(
                "Refurb experience",
                options=[PH, "No / unsure", "Yes"],
                key="act0_refurb_mode",
                label_visibility="collapsed",
            )
            current_refurb_pct = 0.0
            if refurb_mode == "Yes":
                current_refurb_pct = st.slider(
                    "Current refurbished share",
                    min_value=0,
                    max_value=40,
                    value=20,
                    step=5,
                    key="act0_refurb_pct",
                ) / 100.0
                st.caption(f"Current baseline: **{int(current_refurb_pct * 100)}%** refurbished")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**5) Sustainability target (optional)**")
            target_choice = st.selectbox(
                "Target",
                options=target_options,
                key="act0_target_choice",
                label_visibility="collapsed",
            )

            submitted = st.form_submit_button("SHOW ME THE IMPACT →", use_container_width=True)

        if submitted:
            errors = []
            if fleet_choice == PH:
                errors.append("Select your fleet size.")
            if refresh_choice == PH:
                errors.append("Select your refresh rate.")
            if geo_choice == PH:
                errors.append("Select your geography.")

            if errors:
                st.error(" ".join(errors))
                return

            fleet_size = FLEET_SIZE_OPTIONS[fleet_choice]["estimate"]

            refresh_pct = int(refresh_choice.split("%")[0])
            refresh_cycle = refresh_map[refresh_pct]

            geo_code = geo_map[geo_choice]

            target_known = False
            target_pct = -20
            if target_choice.startswith("-"):
                target_pct = int(target_choice.split("%")[0])
                target_known = True

            st.session_state["fleet_size"] = fleet_size
            st.session_state["refresh_cycle"] = refresh_cycle
            st.session_state["geo_code"] = geo_code
            st.session_state["current_refurb_pct"] = float(current_refurb_pct)
            st.session_state["target_pct"] = target_pct
            st.session_state["target_known"] = target_known

            try:
                audit_log.log_user_action("act0_submitted", {
                    "session_id": st.session_state.get("session_id"),
                    "fleet_size": fleet_size,
                    "refresh_pct": refresh_pct,
                    "refresh_cycle": refresh_cycle,
                    "geo": geo_choice,
                    "geo_code": geo_code,
                    "current_refurb_pct": current_refurb_pct,
                    "target_pct": target_pct,
                    "target_known": target_known,
                })
            except Exception:
                pass

            st.session_state["stage"] = "shock_reveal"
            st.rerun()


def render_shock_reveal():
    """Act 1: Shock reveal with metrics."""
    render_header()
    render_act_badge(1, "THE COST OF INACTION")

    fleet_size = st.session_state.get("fleet_size", 12500)
    refresh_cycle = st.session_state.get("refresh_cycle", 4)
    target_pct = st.session_state.get("target_pct", -20)
    target_known = st.session_state.get("target_known", False)
    current_refurb_pct = st.session_state.get("current_refurb_pct", 0.0)

    shock = ShockCalculator.calculate(
        fleet_size,
        avg_age=3.5,
        refresh_cycle=refresh_cycle,
        target_pct=target_pct
    )

    # Adjust avoidable CO₂ if the organization already buys refurbished devices
    base_refurb_rate = float(shock.co2_calculation.get("refurb_rate", 0.4))
    effective_refurb_rate = max(0.0, base_refurb_rate - float(current_refurb_pct))
    scale = (effective_refurb_rate / base_refurb_rate) if base_refurb_rate > 0 else 0.0
    avoidable_co2_tonnes = float(shock.avoidable_co2_tonnes) * scale

    try:
        audit_log.log_calculation(
            "shock",
            inputs={
                "fleet_size": fleet_size,
                "avg_age": 3.5,
                "refresh_cycle": refresh_cycle,
                "target_pct": target_pct,
                "current_refurb_pct": current_refurb_pct,
            },
            outputs={
                "stranded_value_eur": getattr(shock, "stranded_value_eur", None),
                "avoidable_co2_tonnes": avoidable_co2_tonnes,
                "base_refurb_rate": base_refurb_rate,
                "effective_refurb_rate": effective_refurb_rate,
            },
        )
    except Exception:
        pass

    st.markdown(
        """
        <h2 style="text-align: center; font-family: 'Playfair Display', serif;
                   font-size: 2rem; color: #2D2A26; margin-bottom: 2.5rem;">
            If you do nothing...
        </h2>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-value gold">{fmt_currency(shock.stranded_value_eur)}</div>
            <div class="metric-card-label">stranded in old devices</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">📐 Calculation Logic</div>
                <div class="metric-card-logic-formula">Fleet × Avg Price × Remaining Value %</div>
                <ul class="metric-card-logic-list">
                    <li>Fleet size: <strong>{shock.stranded_calculation['fleet_size']:,}</strong> devices</li>
                    <li>Avg purchase price: <strong>€{shock.stranded_calculation['avg_price']:,}</strong></li>
                    <li>Average age: <strong>{shock.stranded_calculation['avg_age']}</strong> years</li>
                    <li>Remaining value: <strong>{shock.stranded_calculation['remaining_value_pct']*100:.0f}%</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: Gartner IT Asset Depreciation Guide 2023</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-value gold">{avoidable_co2_tonnes:,.0f}t</div>
            <div class="metric-card-label">avoidable CO₂ emissions</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">📐 Calculation Logic</div>
                <div class="metric-card-logic-formula">Replacements × Refurb Rate × CO₂/device × 80%</div>
                <ul class="metric-card-logic-list">
                    <li>Annual replacements: <strong>{shock.co2_calculation['annual_replacements']:,.0f}</strong> devices</li>
                    <li>Refurb potential: <strong>{effective_refurb_rate*100:.0f}%</strong></li>
                    <li>CO₂ per device: <strong>{shock.co2_calculation['co2_per_device_kg']}</strong> kg</li>
                    <li>Savings rate: <strong>{shock.co2_calculation['savings_rate']*100:.0f}%</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: Dell Circular Economy Report 2023</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-value danger">2026</div>
            <div class="metric-card-label">LIFE 360 deadline at risk</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">📐 LIFE 360 Commitment</div>
                <ul class="metric-card-logic-list">
                    <li>Target: <strong>{target_pct}%</strong> CO₂ by 2026</li>
                    <li>Current trajectory: <strong>No reduction</strong> (100% new devices)</li>
                    <li>Status: <strong style="color: #9E4A4A;">WILL MISS TARGET</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: LVMH LIFE 360 Program</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        show_stranded_value_disclaimer()

        if not target_known:
            st.caption("Using -20% as default target because no target was provided in calibration.")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("WHAT CAN I DO? →", key="btn_hope", use_container_width=True):
            try:
                audit_log.log_user_action("go_to_hope", {"session_id": st.session_state.get("session_id")})
            except Exception:
                pass
            st.session_state["stage"] = "hope"
            st.rerun()


def render_hope():
    """Act 2: The Hope comparison."""
    render_header()
    render_act_badge(2, "WHAT'S POSSIBLE")

    fleet_size = st.session_state.get("fleet_size", 12500)
    refresh_cycle = st.session_state.get("refresh_cycle", 4)
    target_pct = st.session_state.get("target_pct", -20)

    hope = HopeCalculator.calculate(
        fleet_size,
        avg_age=3.5,
        refresh_cycle=refresh_cycle,
        target_pct=target_pct,
        strategy_key="refurb_40",
    )

    try:
        audit_log.log_calculation(
            "hope",
            inputs={
                "fleet_size": fleet_size,
                "avg_age": 3.5,
                "refresh_cycle": refresh_cycle,
                "target_pct": target_pct,
                "strategy_key": "refurb_40",
            },
            outputs={
                "current_co2_tonnes": getattr(hope, "current_co2_tonnes", None),
                "target_co2_tonnes": getattr(hope, "target_co2_tonnes", None),
                "co2_reduction_pct": getattr(hope, "co2_reduction_pct", None),
                "cost_savings_eur": getattr(hope, "cost_savings_eur", None),
                "months_to_target": getattr(hope, "months_to_target", None),
            },
        )
    except Exception:
        pass

    st.markdown(
        """
        <h2 style="text-align: center; font-family: 'Playfair Display', serif;
                   font-size: 2rem; color: #4A7C59; margin-bottom: 2.5rem;">
            But there's another path...
        </h2>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([5, 1, 5])

    with col1:
        st.markdown(f"""
        <div class="compare-card current">
            <span class="compare-badge">CURRENT TRAJECTORY</span>
            <div class="compare-value">{hope.current_co2_tonnes:,.0f}t</div>
            <div class="compare-label">CO₂ per year</div>
            <div style="height: 1.5rem;"></div>
            <div class="compare-value">{fmt_currency(hope.current_cost_eur)}</div>
            <div class="compare-label">Annual cost</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="compare-arrow">→</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="compare-card target">
            <span class="compare-badge">WITH ÉLYSIA</span>
            <div class="compare-value">{hope.target_co2_tonnes:,.0f}t</div>
            <div class="compare-label">CO₂ per year</div>
            <div style="height: 1.5rem;"></div>
            <div class="compare-value">{fmt_currency(hope.target_cost_eur)}</div>
            <div class="compare-label">Annual cost</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-value">-{abs(hope.co2_reduction_pct):.0f}%</div>
            <div class="stat-label">CO₂ Reduction</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{fmt_currency(hope.cost_savings_eur)}</div>
            <div class="stat-label">Annual Savings</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{hope.months_to_target}mo</div>
            <div class="stat-label">Time to Target</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    show_general_disclaimer()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("HOW DO WE GET THERE? →", key="btn_clarity", use_container_width=True):
            try:
                audit_log.log_user_action("go_to_clarity", {"session_id": st.session_state.get("session_id")})
            except Exception:
                pass
            st.session_state["stage"] = "clarity"
            st.rerun()


def render_clarity():
    """Act 3: The 5 questions (strategy calibration)."""
    render_header()
    render_act_badge(3, "BUILD YOUR STRATEGY")

    st.markdown(
        """
        <p style="text-align: center; color: #6B6560; font-size: 1rem; margin-bottom: 2rem;">
            Answer 5 questions to build your personalized roadmap.
        </p>
        """,
        unsafe_allow_html=True,
    )

    PH = "— Select —"

    # Defaults can come from Act 0 answers (not biased; it's the user's prior input)
    existing_refresh = st.session_state.get("refresh_cycle", None)
    existing_target = st.session_state.get("target_pct", None)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("strategy_form"):
            # Q1
            st.markdown("**1. How old is your fleet, on average?**")
            age_options = [PH] + list(FLEET_AGE_OPTIONS.keys())
            fleet_age = st.selectbox(
                "Age",
                options=age_options,
                format_func=lambda x: x if x == PH else f"{FLEET_AGE_OPTIONS[x]['label']} — {FLEET_AGE_OPTIONS[x]['description']}",
                key="q1",
                label_visibility="collapsed",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Q2
            st.markdown("**2. How often do you replace devices?**")
            cycle_options = [PH, 3, 4, 5, 6]
            default_cycle_idx = 0
            if existing_refresh in cycle_options:
                default_cycle_idx = cycle_options.index(existing_refresh)
            refresh_cycle = st.selectbox(
                "Cycle",
                options=cycle_options,
                index=default_cycle_idx,
                format_func=lambda x: x if x == PH else f"{x} years — " + ("Aggressive" if x==3 else "Standard" if x==4 else "Extended" if x==5 else "Conservative"),
                key="q2",
                label_visibility="collapsed",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Q3
            st.markdown("**3. What is your annual IT equipment budget?**")
            budget_brackets = [PH, "€0.5M", "€1M", "€2M", "€5M", "€10M", "€20M", "€50M", "Custom"]
            bracket = st.selectbox(
                "Budget",
                options=budget_brackets,
                key="q3_bracket",
                label_visibility="collapsed",
            )

            budget = None
            if bracket != PH:
                if bracket == "Custom":
                    budget = st.number_input(
                        "Custom annual budget",
                        min_value=100000,
                        max_value=100000000,
                        value=int(st.session_state.get("budget", 5000000)),
                        step=500000,
                        format="%d",
                        key="q3_custom",
                    )
                else:
                    # Parse bracket like "€5M" -> 5_000_000
                    m = bracket.replace("€", "").replace("M", "")
                    budget = int(float(m) * 1_000_000)

            if budget is not None:
                st.caption(f"💡 That's approximately **{fmt_currency(budget)}**/year")

            st.markdown("<br>", unsafe_allow_html=True)

            # Q4
            st.markdown("**4. What is your #1 priority?**")
            prio_options = [PH, "cost", "co2", "speed"]
            priority = st.selectbox(
                "Priority",
                options=prio_options,
                format_func=lambda x: x if x == PH else ("💰 Cost reduction" if x=="cost" else "🌱 CO₂ reduction" if x=="co2" else "⚡ Speed to target"),
                key="q4",
                label_visibility="collapsed",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Q5
            st.markdown("**5. How ambitious is your target?**")
            target_options = [PH, -20, -30, -40]
            default_target_idx = 0
            if existing_target in target_options:
                default_target_idx = target_options.index(existing_target)
            target = st.selectbox(
                "Target",
                options=target_options,
                index=default_target_idx,
                format_func=lambda x: x if x == PH else f"{x}% — " + ("LIFE 360 Standard" if x==-20 else "Ambitious" if x==-30 else "Industry Leader"),
                key="q5",
                label_visibility="collapsed",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Generate My Strategy →", use_container_width=True)

            if submitted:
                errors = []
                if fleet_age == PH:
                    errors.append("Select fleet age.")
                if refresh_cycle == PH:
                    errors.append("Select refresh cycle.")
                if budget is None:
                    errors.append("Select a budget bracket (or choose Custom).")
                if priority == PH:
                    errors.append("Select priority.")
                if target == PH:
                    errors.append("Select target ambition.")

                if errors:
                    st.error(" ".join(errors))
                else:
                    st.session_state["avg_age"] = FLEET_AGE_OPTIONS[fleet_age]["estimate"]
                    st.session_state["refresh_cycle"] = refresh_cycle
                    st.session_state["budget"] = budget
                    st.session_state["priority"] = priority
                    st.session_state["target_pct"] = target

                    try:
                        audit_log.log_user_action("clarity_submitted", {
                            "session_id": st.session_state.get("session_id"),
                            "avg_age": st.session_state["avg_age"],
                            "refresh_cycle": refresh_cycle,
                            "budget": budget,
                            "priority": priority,
                            "target_pct": target,
                        })
                    except Exception:
                        pass

                    st.session_state["stage"] = "action"
                    st.rerun()




def _get_fleet_df() -> Optional[pd.DataFrame]:
    df = st.session_state.get("fleet_data")
    if df is None:
        return None
    if isinstance(df, pd.DataFrame) and len(df) > 0:
        return df
    return None


def _policy_default() -> Dict[str, bool]:
    """Category-level policy: allow refurbished procurement by category."""
    return st.session_state.get("category_policy", {})


def _compute_fleet_profile(df: Optional[pd.DataFrame], refresh_cycle: int) -> Dict:
    """Compute business-facing metrics from either uploaded fleet or estimates."""
    refresh_cycle = int(refresh_cycle or 4)
    refresh_cycle = max(1, refresh_cycle)

    profile = {
        "data_mode": "estimated",
        "fleet_size": int(st.session_state.get("fleet_size", 12500)),
        "avg_age": float(st.session_state.get("avg_age", 3.5)),
        "annual_replacements": int(round(int(st.session_state.get("fleet_size", 12500)) / refresh_cycle)),
        "eligible_refurb_share": None,
        "annual_new_spend_eur": None,
        "annual_mfg_co2_kg": None,
        "age_risk_share": None,
        "top_categories": [],
        "top_models": [],
    }

    if df is None:
        return profile

    profile["data_mode"] = "measured"

    # Fleet size & age
    profile["fleet_size"] = int(len(df))
    if "Age_Years" in df.columns:
        try:
            profile["avg_age"] = float(pd.to_numeric(df["Age_Years"], errors="coerce").dropna().mean())
        except Exception:
            pass

    profile["annual_replacements"] = int(round(profile["fleet_size"] / refresh_cycle))

    # Risk proxy: share older than 4 years
    if "Age_Years" in df.columns:
        ages = pd.to_numeric(df["Age_Years"], errors="coerce")
        valid = ages.dropna()
        if len(valid) > 0:
            profile["age_risk_share"] = float((valid >= 4.0).mean())

    # Device model / category metrics
    policy = _policy_default()

    model_col = "Device_Model" if "Device_Model" in df.columns else None
    if model_col:
        models = df[model_col].astype(str)
        counts = models.value_counts()
        top_models = []
        for model, cnt in counts.head(5).items():
            meta = DEVICES.get(model, {})
            top_models.append({
                "model": model,
                "count": int(cnt),
                "category": meta.get("category", "Unknown"),
                "refurb_available": bool(meta.get("refurb_available", False)),
            })
        profile["top_models"] = top_models

        # Category mix
        cats = []
        refurb_eligible = 0
        annual_new_spend = 0.0
        annual_mfg_co2 = 0.0

        for model, cnt in counts.items():
            meta = DEVICES.get(model)
            category = meta.get("category", "Unknown") if isinstance(meta, dict) else "Unknown"
            cats.append(category)

            # Annual replacement volume for that model (simple approximation)
            annual_qty = float(cnt) / refresh_cycle

            if isinstance(meta, dict):
                price_new = float(meta.get("price_new_eur", 0.0))
                co2_mfg = float(meta.get("co2_manufacturing_kg", 0.0))
                annual_new_spend += annual_qty * price_new
                annual_mfg_co2 += annual_qty * co2_mfg

                refurb_ok = bool(meta.get("refurb_available", False))
                policy_ok = bool(policy.get(category, True))
                if refurb_ok and policy_ok:
                    refurb_eligible += int(cnt)

        # Eligible refurb share (supply + policy)
        profile["eligible_refurb_share"] = float(refurb_eligible / profile["fleet_size"]) if profile["fleet_size"] else 0.0

        profile["annual_new_spend_eur"] = annual_new_spend
        profile["annual_mfg_co2_kg"] = annual_mfg_co2

        # Top categories by count
        cat_series = pd.Series(cats)
        top_cats = cat_series.value_counts().head(4)
        profile["top_categories"] = [{"category": c, "share": float(v / len(cats))} for c, v in top_cats.items()]

    return profile


def _effective_max_refurb(profile: Dict, risk_appetite: str) -> float:
    # Appetite caps
    caps = {"Conservative": 0.35, "Standard": 0.50, "Aggressive": 0.65}
    cap = float(caps.get(risk_appetite, 0.50))

    eligible = profile.get("eligible_refurb_share")
    if eligible is None:
        return cap
    # Add a small buffer over what is eligible (procurement smoothing), then clamp
    return max(0.0, min(cap, float(eligible) + 0.10))


def _filter_strategies(results: List[StrategyResult], max_refurb_rate: float) -> List[StrategyResult]:
    out = []
    for r in results:
        rr = float(getattr(r, "calculation_details", {}).get("refurb_rate", 0.0))
        if rr <= max_refurb_rate + 1e-9 or r.strategy_key == "do_nothing":
            out.append(r)
    return out


def _pick_strategy(results: List[StrategyResult], priority: str) -> StrategyResult:
    """Pick best strategy from a list (deterministic scoring, consulting-style)."""
    if not results:
        raise ValueError("No strategies to select from")

    # Normalizers
    max_savings = max([float(getattr(r, "annual_savings_eur", 0.0)) for r in results] + [1.0])

    def score(r: StrategyResult) -> float:
        co2 = abs(float(getattr(r, "co2_reduction_pct", 0.0))) / 100.0
        savings = float(getattr(r, "annual_savings_eur", 0.0)) / max_savings
        ttt = float(getattr(r, "time_to_target_months", 999.0))
        speed = (1.0 / (ttt + 1.0)) if ttt < 999 else 0.0
        rr = float(getattr(r, "calculation_details", {}).get("refurb_rate", 0.0))
        risk = 1.0 - rr
        reaches = 1.0 if getattr(r, "reaches_target", False) else 0.0

        if priority == "co2":
            base = 0.60 * co2 + 0.20 * savings + 0.20 * risk
        elif priority == "speed":
            base = 0.60 * speed + 0.20 * co2 + 0.20 * risk
        else:  # cost
            base = 0.60 * savings + 0.20 * co2 + 0.20 * risk

        return base + 0.75 * reaches

    # Exclude do-nothing unless it's the only option
    candidates = [r for r in results if r.strategy_key != "do_nothing"] or results
    return max(candidates, key=score)


def _render_action_nav(current: int, labels: List[str]) -> int:
    st.markdown("<div style='margin-top:0.25rem; margin-bottom:0.75rem;'></div>", unsafe_allow_html=True)
    selected = st.radio(
        "",
        options=labels,
        index=current,
        horizontal=True,
        label_visibility="collapsed",
        key="action_nav_radio",
    )
    return labels.index(selected)


def _device_policy_block(selected_device: str):
    """Allow user to constrain refurb at category level, used by strategy selection."""
    meta = DEVICES.get(selected_device, {})
    category = meta.get("category", "Unknown")
    refurb_available = bool(meta.get("refurb_available", False))

    st.markdown("##### Policy signal")
    st.caption("Use this to reflect what IT / Security / Support will actually allow. It will constrain the strategy recommendation.")

    policy = st.session_state.get("category_policy", {})
    current = bool(policy.get(category, True))

    if refurb_available:
        allow = st.toggle(f"Allow refurbished for {category}", value=current, key=f"policy_allow_{category}")
    else:
        allow = False
        st.info(f"Refurbished is not available in reference data for **{category}**. This category will not count toward refurb eligibility.")

    if st.button("Apply to strategy", key=f"btn_apply_policy_{category}"):
        policy = dict(policy)
        policy[category] = bool(allow)
        st.session_state["category_policy"] = policy
        try:
            audit_log.log_user_action("policy_updated", {"category": category, "allow_refurb": bool(allow)})
        except Exception:
            pass
        st.success("✓ Policy applied. Your strategy recommendation will update.")
        st.rerun()


def _choose_device_action(tco_keep, tco_new, tco_refurb, co2_keep, co2_new, co2_refurb, device_age_years: float, lifespan_years: float, objective: str, criticality: str, refurb_available: bool):
    """UX-side decision model to avoid 'always KEEP' and make rationale explicit."""

    # Build options
    opts = []
    opts.append({"key": "KEEP", "tco": float(tco_keep.get("total", 0.0)), "co2": float(co2_keep.get("total", 0.0)), "base_risk": min(1.0, device_age_years / max(lifespan_years, 1.0))})
    opts.append({"key": "NEW", "tco": float(tco_new.get("total", 0.0)), "co2": float(co2_new.get("total", 0.0)), "base_risk": 0.25})
    if refurb_available and tco_refurb.get("available", True):
        opts.append({"key": "REFURBISHED", "tco": float(tco_refurb.get("total", 0.0)), "co2": float(co2_refurb.get("total", 0.0)), "base_risk": 0.35})

    # Normalizers
    max_tco = max(o["tco"] for o in opts) or 1.0
    max_co2 = max(o["co2"] for o in opts) or 1.0

    crit_w = {"Low": 0.75, "Medium": 1.0, "High": 1.6}.get(criticality, 1.0)

    if objective == "Min CO₂":
        wt_tco, wt_co2, wt_risk = 0.20, 0.65, 0.15
    elif objective == "Min cost":
        wt_tco, wt_co2, wt_risk = 0.65, 0.20, 0.15
    elif objective == "Min risk":
        wt_tco, wt_co2, wt_risk = 0.25, 0.20, 0.55
    else:  # Balanced
        wt_tco, wt_co2, wt_risk = 0.45, 0.40, 0.15

    def score(o):
        ntco = o["tco"] / max_tco
        nco2 = o["co2"] / max_co2
        risk = o["base_risk"]
        # lower is better
        return wt_tco * ntco + wt_co2 * nco2 + wt_risk * risk * crit_w

    best = min(opts, key=score)

    # Rationale
    s = sorted(opts, key=score)
    runner = s[1] if len(s) > 1 else best

    rationale = f"Selected **{best['key']}** because it performs best for your objective ({objective}) given {criticality.lower()} criticality."

    return best["key"], rationale



def render_action():
    """Act 4: Strategy experience (guided flow, integrated evidence + policy)."""
    render_header()
    render_act_badge(4, "YOUR STRATEGY")

    # Base inputs
    refresh_cycle = int(st.session_state.get("refresh_cycle", 4) or 4)
    target_pct = int(st.session_state.get("target_pct", -20) or -20)
    priority = st.session_state.get("priority", "cost")

    # Data-derived profile (fleet upload + policy)
    df = _get_fleet_df()
    profile = _compute_fleet_profile(df, refresh_cycle)

    # Navigation state
    labels = [
        "Executive Summary",
        "Decision",
        "Fleet Evidence",
        "Policy Lab",
        "Plan",
    ]
    if "action_step" not in st.session_state:
        st.session_state["action_step"] = 0

    st.session_state["action_step"] = _render_action_nav(int(st.session_state["action_step"]), labels)
    step = int(st.session_state["action_step"])

    # Decision controls stored in session
    if "risk_appetite" not in st.session_state:
        st.session_state["risk_appetite"] = "Standard"

    # Strategy calculation uses best available fleet_size/age
    fleet_size = int(profile["fleet_size"])
    avg_age = float(profile["avg_age"])

    # Run strategy sims
    results_all = StrategySimulator.compare_all_strategies(
        fleet_size=fleet_size,
        current_refresh=refresh_cycle,
        avg_age=avg_age,
        target_pct=target_pct,
        time_horizon_months=36,
    )

    max_refurb = _effective_max_refurb(profile, st.session_state.get("risk_appetite", "Standard"))
    results = _filter_strategies(results_all, max_refurb)

    baseline = next((r for r in results_all if r.strategy_key == "do_nothing"), None)
    selected = _pick_strategy(results, priority)

    # Expose to other steps
    st.session_state["selected_strategy_key"] = getattr(selected, "strategy_key", None)

    # Confidence badge
    confidence = "HIGH" if profile.get("data_mode") == "measured" else "MEDIUM"

    # ---------------------------------------------------------------------
    # STEP 0 — Executive Summary (30 seconds)
    # ---------------------------------------------------------------------
    if step == 0:
        st.markdown(f"""
        <div class="gold-ticket">
            <div class="gold-ticket-label">◆ RECOMMENDED STRATEGY</div>
            <div class="gold-ticket-title">{selected.strategy_name}</div>
            <div class="gold-ticket-desc">{selected.description}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        c1.metric("CO₂ reduction", f"-{abs(selected.co2_reduction_pct):.0f}%")
        c2.metric("Annual savings", fmt_currency(selected.annual_savings_eur))
        c3.metric("Time to target", f"{selected.time_to_target_months} mo" if selected.time_to_target_months < 999 else "—")
        c4.metric("Confidence", confidence)

        if profile.get("data_mode") != "measured":
            st.markdown(
                "<div class='alert-box warning'><div class='alert-title'>Refine with your real fleet</div>"
                "<div class='alert-text'>Upload your CSV to replace estimates with measured data and increase confidence.</div></div>",
                unsafe_allow_html=True,
            )

        # Quick narrative + CTAs
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Continue →", use_container_width=True, key="btn_step0_next"):
                st.session_state["action_step"] = 1
                st.rerun()
        with col_b:
            if st.button("Upload fleet data (recommended)", use_container_width=True, key="btn_step0_to_evidence"):
                st.session_state["action_step"] = 2
                st.rerun()

    # ---------------------------------------------------------------------
    # STEP 1 — Decision (scenarios + execution constraints)
    # ---------------------------------------------------------------------
    elif step == 1:
        st.markdown("### Decision framing")
        st.caption("Choose a strategy that you can execute. We constrain recommendations using supply/policy ceilings.")

        left, right = st.columns([2, 1])
        with right:
            st.markdown("#### Execution controls")
            st.session_state["risk_appetite"] = st.selectbox(
                "Risk appetite",
                ["Conservative", "Standard", "Aggressive"],
                index=["Conservative", "Standard", "Aggressive"].index(st.session_state.get("risk_appetite", "Standard")),
                key="risk_appetite_select",
            )

            # Show supply ceiling when we have data
            eligible = profile.get("eligible_refurb_share")
            if eligible is not None:
                st.caption(f"Supply/policy ceiling from your fleet: **{int(eligible*100)}%** eligible for refurb")
            st.caption(f"Max refurb used in strategy selection: **{int(max_refurb*100)}%**")

            if st.button("Recompute with these constraints", use_container_width=True, key="btn_recompute_constraints"):
                st.rerun()

        with left:
            # Scenario blocks
            non_baseline = [r for r in results if r.strategy_key != "do_nothing"]
            best_case = max(non_baseline, key=lambda r: abs(r.co2_reduction_pct)) if non_baseline else selected

            def _risk_label(r):
                rr = float(getattr(r, "calculation_details", {}).get("refurb_rate", 0.0))
                if rr >= 0.55:
                    return "HIGH"
                if rr >= 0.35:
                    return "MEDIUM"
                return "LOW"

            worst_case = baseline if baseline is not None else min(results_all, key=lambda r: abs(r.co2_reduction_pct))

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-value success">BEST</div>
                    <div class="metric-card-label">{best_case.strategy_name}</div>
                    <div style="color:#6B6560; font-size:0.85rem; margin-top:0.5rem;">
                        Risk: {_risk_label(best_case)} · CO₂: -{abs(best_case.co2_reduction_pct):.0f}%<br>
                        ROI: {best_case.roi_3year:.1f}x · Refurb: {int(float(getattr(best_case,'calculation_details',{}).get('refurb_rate',0))*100)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-value gold">REALISTIC</div>
                    <div class="metric-card-label">{selected.strategy_name}</div>
                    <div style="color:#6B6560; font-size:0.85rem; margin-top:0.5rem;">
                        Risk: {_risk_label(selected)} · CO₂: -{abs(selected.co2_reduction_pct):.0f}%<br>
                        ROI: {selected.roi_3year:.1f}x · Refurb: {int(float(getattr(selected,'calculation_details',{}).get('refurb_rate',0))*100)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-value danger">WORST</div>
                    <div class="metric-card-label">{worst_case.strategy_name}</div>
                    <div style="color:#6B6560; font-size:0.85rem; margin-top:0.5rem;">
                        Likely misses target<br>
                        CO₂: -{abs(worst_case.co2_reduction_pct):.0f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Show underlying comparison"):
                comparison_data = []
                for r in sorted(results, key=lambda x: (not x.reaches_target, -abs(x.co2_reduction_pct)))[:6]:
                    comparison_data.append({
                        "Strategy": r.strategy_name,
                        "CO₂": f"-{abs(r.co2_reduction_pct):.0f}%",
                        "Savings": fmt_currency(r.annual_savings_eur),
                        "Time to target": f"{r.time_to_target_months}mo" if r.time_to_target_months < 999 else "Never",
                        "Refurb %": f"{int(float(getattr(r,'calculation_details',{}).get('refurb_rate',0))*100)}%",
                    })
                st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            if st.button("← Back", use_container_width=True, key="btn_step1_back"):
                st.session_state["action_step"] = 0
                st.rerun()
        with b2:
            if st.button("Continue →", use_container_width=True, key="btn_step1_next"):
                st.session_state["action_step"] = 4
                st.rerun()
        with b3:
            if st.button("Review fleet evidence", use_container_width=True, key="btn_step1_to_evidence"):
                st.session_state["action_step"] = 2
                st.rerun()

    # ---------------------------------------------------------------------
    # STEP 2 — Fleet Evidence (business-driven)
    # ---------------------------------------------------------------------
    elif step == 2:
        st.markdown("### Fleet evidence")
        st.caption("Turn fleet data into CFO/COO-ready insights and raise confidence.")

        # Upload + demo
        col_upload, col_demo = st.columns([2, 1])
        with col_upload:
            uploaded_file = st.file_uploader(
                "Upload Fleet CSV",
                type=["csv"],
                key="fleet_upload_step",
                help="Required columns: Device_Model, Age_Years. Optional: Persona, Country",
            )

        with col_demo:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Load demo fleet", use_container_width=True, key="btn_demo_step"):
                demo = generate_demo_fleet(150)
                st.session_state["fleet_data"] = pd.DataFrame(demo)
                st.success("✓ Demo data loaded (150 devices)")
                st.rerun()

        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                if "Device_Model" not in df_up.columns or "Age_Years" not in df_up.columns:
                    st.error("CSV must include at least: Device_Model, Age_Years")
                else:
                    st.session_state["fleet_data"] = df_up
                    try:
                        audit_log.log_user_action("fleet_uploaded", {"rows": int(len(df_up))})
                    except Exception:
                        pass
                    st.success(f"✓ Loaded {len(df_up)} devices")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

        # Recompute profile with current df
        df2 = _get_fleet_df()
        profile2 = _compute_fleet_profile(df2, refresh_cycle)

        # Executive metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fleet size", f"{profile2['fleet_size']:,}")
        m2.metric("Avg age", f"{profile2['avg_age']:.1f}y")
        m3.metric("Annual replacements", f"{profile2['annual_replacements']:,}")
        if profile2.get("annual_new_spend_eur") is not None:
            m4.metric("Annual new spend (est.)", fmt_currency(profile2["annual_new_spend_eur"]))
        else:
            m4.metric("Confidence", "MEDIUM")

        # Top 3 business insights
        st.markdown("#### Top 3 business insights")
        insights = []
        if profile2.get("age_risk_share") is not None:
            insights.append(f"**{int(profile2['age_risk_share']*100)}%** of devices are **≥ 4 years** (support & SLA risk proxy).")
        if profile2.get("eligible_refurb_share") is not None:
            insights.append(f"Based on model mix + policy, **{int(profile2['eligible_refurb_share']*100)}%** of devices are **eligible for refurbished sourcing**.")
        if profile2.get("annual_mfg_co2_kg") is not None:
            insights.append(f"Estimated manufacturing CO₂ for annual replacements: **{profile2['annual_mfg_co2_kg']/1000:.0f} tCO₂/year**.")
        if not insights:
            insights = ["Upload your fleet CSV to unlock measured insights."]

        for i, t in enumerate(insights[:3], 1):
            st.markdown(f"{i}. {t}")

        # Segment drill-down (expander)
        with st.expander("See supporting evidence"):
            if profile2.get("top_categories"):
                st.markdown("**Category concentration**")
                st.write(pd.DataFrame(profile2["top_categories"]))
            if profile2.get("top_models"):
                st.markdown("**Top models (by count)**")
                st.write(pd.DataFrame(profile2["top_models"]))

            # Simple distribution charts if we have data
            if df2 is not None and "Age_Years" in df2.columns:
                ages = pd.to_numeric(df2["Age_Years"], errors="coerce").dropna()
                if len(ages) > 0:
                    fig = px.histogram(ages, nbins=12, title="Device age distribution (years)")
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            if st.button("← Back", use_container_width=True, key="btn_step2_back"):
                st.session_state["action_step"] = 0
                st.rerun()
        with b2:
            if st.button("Continue →", use_container_width=True, key="btn_step2_next"):
                st.session_state["action_step"] = 1
                st.rerun()
        with b3:
            if st.button("Go to policy lab", use_container_width=True, key="btn_step2_to_policy"):
                st.session_state["action_step"] = 3
                st.rerun()

    # ---------------------------------------------------------------------
    # STEP 3 — Policy Lab (device simulator integrated)
    # ---------------------------------------------------------------------
    elif step == 3:
        st.markdown("### Policy Lab")
        st.caption("Test device-level decisions and apply policy signals to constrain the strategy recommendation.")

        col1, col2, col3 = st.columns(3)
        with col1:
            selected_device = st.selectbox("Device", options=get_device_names(), index=5, key="sim_device_step")
        with col2:
            selected_persona = st.selectbox("User profile", options=get_persona_names(), index=1, key="sim_persona_step")
        with col3:
            countries = get_country_codes()
            country = st.selectbox(
                "Location",
                options=list(countries.keys()),
                format_func=lambda x: countries[x],
                index=0,
                key="sim_country_step",
            )

        col4, col5, col6 = st.columns(3)
        with col4:
            device_age = st.slider("Current device age (years)", 0.5, 7.0, 3.5, 0.5, key="sim_age_step")
        with col5:
            objective = st.selectbox("Objective", ["Balanced", "Min CO₂", "Min cost", "Min risk"], key="sim_obj_step")
        with col6:
            criticality = st.selectbox("Criticality", ["Low", "Medium", "High"], index=1, key="sim_crit_step")

        if st.button("Calculate", use_container_width=True, key="btn_calc_step"):
            meta = DEVICES.get(selected_device, {})
            lifespan_years = float(meta.get("lifespan_months", 48)) / 12.0
            refurb_available = bool(meta.get("refurb_available", False))

            # Compute scenarios
            tco_keep = TCOCalculator.calculate_tco_keep(selected_device, device_age, selected_persona, country)
            tco_new = TCOCalculator.calculate_tco_new(selected_device, selected_persona, country)
            tco_refurb = TCOCalculator.calculate_tco_refurb(selected_device, selected_persona, country)

            co2_keep = CO2Calculator.calculate_co2_keep(selected_device, selected_persona, country)
            co2_new = CO2Calculator.calculate_co2_new(selected_device, selected_persona, country)
            co2_refurb = CO2Calculator.calculate_co2_refurb(selected_device, selected_persona, country)

            reco_key, rationale = _choose_device_action(
                tco_keep, tco_new, tco_refurb,
                co2_keep, co2_new, co2_refurb,
                device_age_years=float(device_age),
                lifespan_years=float(lifespan_years),
                objective=str(objective),
                criticality=str(criticality),
                refurb_available=refurb_available,
            )

            st.session_state["device_reco"] = {"key": reco_key, "rationale": rationale}

            try:
                audit_log.log_user_action("device_simulated", {
                    "device": selected_device,
                    "persona": selected_persona,
                    "country": country,
                    "age_years": float(device_age),
                    "objective": objective,
                    "criticality": criticality,
                    "recommendation": reco_key,
                })
            except Exception:
                pass

        # Render results
        reco = st.session_state.get("device_reco")
        if reco:
            st.markdown("<br>", unsafe_allow_html=True)
            reco_class = "keep" if reco["key"] == "KEEP" else ("new" if reco["key"] == "NEW" else "")
            st.markdown(f"""
            <div class="reco-box {reco_class}">
                <div class="reco-label">RECOMMENDATION</div>
                <div class="reco-title">{reco['key']}</div>
                <div class="reco-rationale">{reco['rationale']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Apply policy signal
            _device_policy_block(st.session_state.get("sim_device_step"))

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            if st.button("← Back", use_container_width=True, key="btn_step3_back"):
                st.session_state["action_step"] = 2
                st.rerun()
        with b2:
            if st.button("Continue →", use_container_width=True, key="btn_step3_next"):
                st.session_state["action_step"] = 1
                st.rerun()
        with b3:
            if st.button("Go to plan", use_container_width=True, key="btn_step3_to_plan"):
                st.session_state["action_step"] = 4
                st.rerun()

    # ---------------------------------------------------------------------
    # STEP 4 — Plan (deliverable-style)
    # ---------------------------------------------------------------------
    else:
        st.markdown("### 90-Day execution plan")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
**Days 1–30 (Governance + Baseline)**
- Steering committee (IT + Procurement + Sustainability + Finance)
- Lock KPIs (CO₂, spend, failure rate, refresh policy)
- Pilot scope + success criteria
""")
        with m2:
            st.markdown("""
**Days 31–60 (Pilot)**
- Deploy **100–300 devices**
- Measure: failure rate, ticket volume, user satisfaction
- Validate supplier capacity + lead times
""")
        with m3:
            st.markdown("""
**Days 61–90 (Scale)**
- Scale to next wave (**10–20%** of annual replacements)
- Embed rules into procurement workflows
- Train IT support + publish comms
""")

        st.markdown("#### Months 4–36 roadmap")
        st.markdown("""
**Months 4–12:** scale & stabilize (supplier governance, grading, acceptance testing)  
**Months 12–24:** optimize mix by category + integrate reporting into dashboards  
**Months 24–36:** institutionalize circular procurement + audit readiness
""")

        st.markdown("#### Success metrics")
        st.markdown("""
- Refurb adoption (by category/region)
- Finance-validated annual savings
- Failure rate threshold (e.g., **<1.5%**)
- CO₂ trajectory vs target
""")

        st.markdown("#### When this won’t work")
        st.markdown("""
- Mostly desktops (low refurb availability) → refurb targets must be lower
- No supplier grading / SLA enforcement → failure risk increases
- Security forbids secondary market → focus lifecycle extension only
""")

        with st.expander("Methodology & Sources"):
            render_methodology_tab()
            try:
                sources_expander(get_all_sources())
            except Exception:
                pass

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back", use_container_width=True, key="btn_step4_back"):
                st.session_state["action_step"] = 1
                st.rerun()
        with col2:
            if st.button("Start new analysis", use_container_width=True, key="btn_restart_v2"):
                try:
                    duration = int(time.time() - st.session_state.get("session_started_at", time.time()))
                    audit_log.log_session_end(st.session_state.get("session_id"), duration_seconds=duration)
                    audit_log.log_user_action("restart", {"session_id": st.session_state.get("session_id"), "duration_seconds": duration})
                except Exception:
                    pass
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state["stage"] = "opening"
                st.rerun()
        with col3:
            if st.button("Export report", use_container_width=True, key="btn_export_report"):
                try:
                    md = generate_markdown_report(
                        fleet_size=fleet_size,
                        avg_age=avg_age,
                        refresh_cycle=refresh_cycle,
                        target_pct=target_pct,
                        strategy_name=selected.strategy_name,
                        annual_savings=selected.annual_savings_eur,
                        co2_reduction=selected.co2_reduction_pct,
                        time_to_target=selected.time_to_target_months,
                    )
                    st.download_button("Download report (MD)", md, file_name="elysia_report.md")
                except Exception:
                    st.info("Report export is not available in this environment.")
# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def run():
    """Main application entry point."""
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)
    inject_credibility_css()  
    # --- Session init (once) ---
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["session_started_at"] = time.time()
        try:
            audit_log.log_session_start(st.session_state["session_id"])
        except Exception:
            pass

    
    if not BACKEND_READY:
        st.error(f"⚠️ Backend module error: {IMPORT_ERROR}")
        st.info("Ensure `reference_data_API.py` and `calculator.py` are in the same directory.")
        st.stop()
    
    if "stage" not in st.session_state:
        st.session_state["stage"] = "opening"
    
    stage = st.session_state["stage"]
    
    # Route to appropriate screen
    if stage == "opening":
        render_opening()
    elif stage == "shock_q":
        render_shock_question()
    elif stage == "shock_reveal":
        render_shock_reveal()
    elif stage == "hope":
        render_hope()
    elif stage == "clarity":
        render_clarity()
    elif stage == "action":
        render_action()
    else:
        st.session_state["stage"] = "opening"
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="lux-footer">
        <div class="lux-footer-text">ÉLYSIA · LVMH GREEN IT · LIFE 360</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    run()