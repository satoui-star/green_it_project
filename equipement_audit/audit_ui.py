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
    """Act 1: Fleet size question."""
    render_header()
    render_act_badge(1, "THE SITUATION")
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>How large is your IT fleet?</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        choice = st.radio(
            "Select fleet size",
            options=list(FLEET_SIZE_OPTIONS.keys()),
            format_func=lambda x: f"{FLEET_SIZE_OPTIONS[x]['label']} — {FLEET_SIZE_OPTIONS[x]['description']}",
            key="fleet_choice",
            label_visibility="collapsed"
        )
        
        selected = FLEET_SIZE_OPTIONS[choice]
        st.markdown(f"""
        <div style="text-align: center; margin: 1.5rem 0;">
            <span style="background: #F5F3EF; padding: 0.6rem 1.25rem; border-radius: 25px; 
                         font-size: 0.9rem; color: #6B6560; border: 1px solid #E8E4DD;">
                📊 Estimated: <strong style="color: #2D2A26;">{selected['estimate']:,}</strong> devices
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("SHOW ME THE IMPACT →", key="btn_shock", use_container_width=True):
            st.session_state["fleet_size"] = selected["estimate"]
            st.session_state["stage"] = "shock_reveal"
            st.rerun()


def render_shock_reveal():
    """Act 1: Shock reveal with metrics."""
    render_header()
    render_act_badge(1, "THE COST OF INACTION")
    
    fleet_size = st.session_state.get("fleet_size", 12500)
    shock = ShockCalculator.calculate(fleet_size, avg_age=3.5, refresh_cycle=4, target_pct=-20)
    
    st.markdown("""
    <h2 style="text-align: center; font-family: 'Playfair Display', serif; 
               font-size: 2rem; color: #2D2A26; margin-bottom: 2.5rem;">
        If you do nothing...
    </h2>
    """, unsafe_allow_html=True)
    
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
            <div class="metric-card-value gold">{shock.avoidable_co2_tonnes:,.0f}t</div>
            <div class="metric-card-label">avoidable CO₂ emissions</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">📐 Calculation Logic</div>
                <div class="metric-card-logic-formula">Replacements × Refurb Rate × CO₂/device × 80%</div>
                <ul class="metric-card-logic-list">
                    <li>Annual replacements: <strong>{shock.co2_calculation['annual_replacements']:,.0f}</strong> devices</li>
                    <li>Refurb potential: <strong>{shock.co2_calculation['refurb_rate']*100:.0f}%</strong></li>
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
                    <li>Target: <strong>-20%</strong> CO₂ by 2026</li>
                    <li>Current trajectory: <strong>No reduction</strong> (100% new devices)</li>
                    <li>Status: <strong style="color: #9E4A4A;">WILL MISS TARGET</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: LVMH LIFE 360 Program</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        show_stranded_value_disclaimer()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("WHAT CAN I DO? →", key="btn_hope", use_container_width=True):
            st.session_state["stage"] = "hope"
            st.rerun()


def render_hope():
    """Act 2: The Hope comparison."""
    render_header()
    render_act_badge(2, "WHAT'S POSSIBLE")
    
    fleet_size = st.session_state.get("fleet_size", 12500)
    hope = HopeCalculator.calculate(fleet_size, avg_age=3.5, refresh_cycle=4, 
                                    target_pct=-20, strategy_key="refurb_40")
    
    st.markdown("""
    <h2 style="text-align: center; font-family: 'Playfair Display', serif; 
               font-size: 2rem; color: #4A7C59; margin-bottom: 2.5rem;">
        But there's another path...
    </h2>
    """, unsafe_allow_html=True)
    
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
            st.session_state["stage"] = "clarity"
            st.rerun()


def render_clarity():
    """Act 3: The 5 questions."""
    render_header()
    render_act_badge(3, "BUILD YOUR STRATEGY")
    
    st.markdown("""
    <p style="text-align: center; color: #6B6560; font-size: 1rem; margin-bottom: 2rem;">
        Answer 5 questions to build your personalized roadmap.
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("strategy_form"):
            # Q1
            st.markdown("**1. How old is your fleet, on average?**")
            fleet_age = st.radio(
                "Age", 
                options=list(FLEET_AGE_OPTIONS.keys()),
                format_func=lambda x: f"{FLEET_AGE_OPTIONS[x]['label']} — {FLEET_AGE_OPTIONS[x]['description']}",
                key="q1", 
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Q2
            st.markdown("**2. How often do you replace devices?**")
            refresh_cycle = st.radio(
                "Cycle",
                options=[3, 4, 5, 6],
                format_func=lambda x: f"{x} years — " + ("Aggressive" if x==3 else "Standard" if x==4 else "Extended" if x==5 else "Conservative"),
                index=1,
                key="q2",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Q3
            st.markdown("**3. What is your annual IT equipment budget?**")
            budget = st.number_input(
                "Budget",
                min_value=100000,
                max_value=100000000,
                value=5000000,
                step=500000,
                format="%d",
                key="q3",
                label_visibility="collapsed"
            )
            st.caption(f"💡 That's approximately **{fmt_currency(budget)}**/year")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Q4
            st.markdown("**4. What is your #1 priority?**")
            priority = st.radio(
                "Priority",
                options=["cost", "co2", "speed"],
                format_func=lambda x: "💰 Cost reduction" if x=="cost" else "🌱 CO₂ reduction" if x=="co2" else "⚡ Speed to target",
                key="q4",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Q5
            st.markdown("**5. How ambitious is your target?**")
            target = st.radio(
                "Target",
                options=[-20, -30, -40],
                format_func=lambda x: f"{x}% — " + ("LIFE 360 Standard" if x==-20 else "Ambitious" if x==-30 else "Industry Leader"),
                key="q5",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Generate My Strategy →", use_container_width=True)
            
            if submitted:
                st.session_state["avg_age"] = FLEET_AGE_OPTIONS[fleet_age]["estimate"]
                st.session_state["refresh_cycle"] = refresh_cycle
                st.session_state["budget"] = budget
                st.session_state["priority"] = priority
                st.session_state["target_pct"] = target
                st.session_state["stage"] = "action"
                st.rerun()


def render_action():
    """Act 4: Strategy results with 3 tabs."""
    render_header()
    render_act_badge(4, "YOUR STRATEGY")
    
    # Get parameters
    fleet_size = st.session_state.get("fleet_size", 12500)
    avg_age = st.session_state.get("avg_age", 3.5)
    refresh_cycle = st.session_state.get("refresh_cycle", 4)
    priority = st.session_state.get("priority", "balanced")
    target_pct = st.session_state.get("target_pct", -20)
    
    # Calculate strategies
    results = StrategySimulator.compare_all_strategies(
        fleet_size=fleet_size,
        current_refresh=refresh_cycle,
        avg_age=avg_age,
        target_pct=target_pct,
        time_horizon_months=36
    )
    
    best = StrategySimulator.get_recommended_strategy(
        fleet_size=fleet_size,
        current_refresh=refresh_cycle,
        avg_age=avg_age,
        target_pct=target_pct,
        priority=priority
    )
    
    baseline = next((r for r in results if r.strategy_key == "do_nothing"), None)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["◆ STRATEGIC ROADMAP", "◆ FLEET INTELLIGENCE", "◆ DEVICE SIMULATOR"])
    
    # =========================================================================
    # TAB 1: Strategic Roadmap
    # =========================================================================
    with tab1:
        # Warning if baseline fails
        if baseline and not baseline.reaches_target:
            st.markdown(f"""
            <div class="alert-box warning">
                <div class="alert-title">⚠️ Current trajectory misses the {target_pct}% target</div>
                <div class="alert-text">
                    Without intervention, your organization will not achieve its LIFE 360 commitment. 
                    The strategies below show how to get back on track.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gold Ticket Winner
        st.markdown(f"""
        <div class="gold-ticket">
            <div class="gold-ticket-label">◆ RECOMMENDED STRATEGY</div>
            <div class="gold-ticket-title">{best.strategy_name}</div>
            <div class="gold-ticket-desc">{best.description}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Impact Metrics
        st.markdown(f"""
        <div class="impact-row">
            <div class="impact-card">
                <div class="impact-value">-{abs(best.co2_reduction_pct):.0f}%</div>
                <div class="impact-label">CO₂ Reduction</div>
            </div>
            <div class="impact-card">
                <div class="impact-value">{fmt_currency(best.annual_savings_eur)}</div>
                <div class="impact-label">Annual Savings</div>
            </div>
            <div class="impact-card">
                <div class="impact-value">{best.time_to_target_months if best.time_to_target_months < 999 else '—'}mo</div>
                <div class="impact-label">Time to Target</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Success alert
        if best.reaches_target:
            st.markdown(f"""
            <div class="alert-box success">
                <div class="alert-title">✓ Target Achievable</div>
                <div class="alert-text">
                    With <strong>{best.strategy_name}</strong>, you will reach the {target_pct}% target in 
                    <strong>{best.time_to_target_months} months</strong>. 
                    Payback period: <strong>{best.payback_months:.0f} months</strong>.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Strategy Comparison Table
        st.markdown("#### Strategy Comparison")
        
        comparison_data = []
        for r in results[:5]:
            comparison_data.append({
                "Strategy": r.strategy_name,
                "CO₂ Reduction": f"-{abs(r.co2_reduction_pct):.0f}%",
                "Annual Savings": fmt_currency(r.annual_savings_eur),
                "Time to Target": f"{r.time_to_target_months}mo" if r.time_to_target_months < 999 else "Never",
                "Reaches Target": "✓" if r.reaches_target else "✗",
                "ROI (3yr)": f"{r.roi_3year:.1f}x" if r.roi_3year > 0 else "—"
            })
        
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
        
        # Trajectory Chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### CO₂ Trajectory Projection")
        
        current_co2 = best.monthly_co2[0] if best.monthly_co2 else fleet_size * 50 / 1000
        fig = create_trajectory_chart(results, target_pct, current_co2)
        st.plotly_chart(fig, use_container_width=True)
        
        # First 3 Actions
        refurb_rate = best.calculation_details.get('refurb_rate', 0.4)
        new_lifecycle = best.calculation_details.get('new_lifecycle', 5)
        
        st.markdown(f"""
        <div class="actions-box">
            <div class="actions-title">🎯 Your First 3 Actions</div>
            <div class="action-row">
                <div class="action-num">1</div>
                <div class="action-text">
                    <strong>Identify priority devices:</strong> Find the <strong>{int(fleet_size / refresh_cycle * 0.3):,}</strong> 
                    devices due for replacement in the next 6 months. Focus on aging laptops and workstations first.
                </div>
            </div>
            <div class="action-row">
                <div class="action-num">2</div>
                <div class="action-text">
                    <strong>Source refurbished alternatives:</strong> Partner with LVMH-certified refurbishers to procure 
                    <strong>{int(refurb_rate * 100)}%</strong> of upcoming purchases as refurbished devices.
                </div>
            </div>
            <div class="action-row">
                <div class="action-num">3</div>
                <div class="action-text">
                    <strong>Update lifecycle policy:</strong> Extend the standard refresh cycle from {refresh_cycle} to 
                    <strong>{new_lifecycle} years</strong> for eligible device categories.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 2: Fleet Intelligence
    # =========================================================================
    with tab2:
        st.markdown("### Fleet Intelligence Dashboard")
        st.markdown("""
        <p style="color: #6B6560; margin-bottom: 1.5rem;">
            Upload your fleet data for detailed analysis, or explore with demo data.
        </p>
        """, unsafe_allow_html=True)
        
        # CSV Upload Section
        col_upload, col_demo = st.columns([2, 1])
        
        with col_upload:
            uploaded_file = st.file_uploader(
                "📁 Upload Fleet CSV",
                type=["csv"],
                key="fleet_upload",
                help="Required columns: Device_Model, Age_Years, Persona, Country"
            )
        
        with col_demo:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📊 Load Demo Data", key="btn_demo", use_container_width=True):
                demo = generate_demo_fleet(100)
                st.session_state["fleet_data"] = pd.DataFrame(demo)
                st.success("✓ Demo data loaded (100 devices)")
            
            # Template download
            template_df = pd.DataFrame({
                "Device_Model": ["Laptop (Standard)", "iPhone 14 (Alternative)", "Tablet"],
                "Age_Years": [3.5, 2.0, 4.0],
                "Persona": ["Admin Normal (HR/Finance)", "Vendor (Phone/Tablet)", "Admin Normal (HR/Finance)"],
                "Country": ["FR", "US", "FR"]
            })
            csv_template = template_df.to_csv(index=False)
            st.download_button(
                "📥 Download Template",
                csv_template,
                "elysia_template.csv",
                "text/csv",
                use_container_width=True
            )
        
        # Process uploaded file
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                required = ["Device_Model", "Age_Years"]
                missing = [c for c in required if c not in df.columns]
                
                if missing:
                    st.error(f"Missing required columns: {', '.join(missing)}")
                else:
                    st.session_state["fleet_data"] = df
                    st.success(f"✓ Loaded {len(df)} devices from CSV")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_age = create_fleet_age_chart()
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            fig_co2 = create_device_co2_chart()
            st.plotly_chart(fig_co2, use_container_width=True)
        
        # Device Reference Table
        st.markdown("#### Device Reference Data")
        
        device_data = []
        for name, device in DEVICES.items():
            device_data.append({
                "Device": name,
                "Category": device.get("category", "Other"),
                "Price (New)": f"€{device['price_new_eur']:,}",
                "CO₂ (kg)": device["co2_manufacturing_kg"],
                "Lifespan": f"{device['lifespan_months']}mo",
                "Refurb?": "✓" if device.get("refurb_available") else "✗"
            })
        
        st.dataframe(pd.DataFrame(device_data), use_container_width=True, hide_index=True)
        
        # Fleet Summary Metrics
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Fleet Size", f"{fleet_size:,}")
        col2.metric("Avg Age", f"{avg_age:.1f} years")
        col3.metric("Annual Replacements", f"{fleet_size // refresh_cycle:,}")
        
        avg_co2 = sum(d["co2_manufacturing_kg"] for d in DEVICES.values()) / len(DEVICES)
        total_co2 = avg_co2 * (fleet_size // refresh_cycle) / 1000
        col4.metric("Est. Annual CO₂", f"{total_co2:.0f}t")
    
    # =========================================================================
    # TAB 3: Device Simulator
    # =========================================================================
    with tab3:
        st.markdown("### Device-Level Simulator")
        st.markdown("""
        <p style="color: #6B6560; margin-bottom: 1.5rem;">
            Calculate the TCO and CO₂ impact for specific device scenarios.
        </p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_device = st.selectbox(
                "Select Device",
                options=get_device_names(),
                index=5,  # Laptop (Standard)
                key="sim_device"
            )
        
        with col2:
            selected_persona = st.selectbox(
                "Select User Profile",
                options=get_persona_names(),
                index=1,  # Admin Normal
                key="sim_persona"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            device_age = st.slider(
                "Current Device Age (years)",
                min_value=0.5,
                max_value=7.0,
                value=3.5,
                step=0.5,
                key="sim_age"
            )
        
        with col2:
            countries = get_country_codes()
            country = st.selectbox(
                "Location (for grid carbon)",
                options=list(countries.keys()),
                format_func=lambda x: countries[x],
                index=0,  # FR
                key="sim_country"
            )
        
        if st.button("CALCULATE IMPACT", key="btn_calc", use_container_width=True):
            # Calculate all scenarios
            tco_keep = TCOCalculator.calculate_tco_keep(selected_device, device_age, selected_persona, country)
            tco_new = TCOCalculator.calculate_tco_new(selected_device, selected_persona, country)
            tco_refurb = TCOCalculator.calculate_tco_refurb(selected_device, selected_persona, country)
            
            co2_keep = CO2Calculator.calculate_co2_keep(selected_device, selected_persona, country)
            co2_new = CO2Calculator.calculate_co2_new(selected_device, selected_persona, country)
            co2_refurb = CO2Calculator.calculate_co2_refurb(selected_device, selected_persona, country)
            
            # Get recommendation
            reco = RecommendationEngine.analyze_device(
                selected_device, device_age, selected_persona, country, priority
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Recommendation Box
            reco_class = "keep" if reco.recommendation == "KEEP" else ("" if reco.recommendation == "REFURBISHED" else "new")
            st.markdown(f"""
            <div class="reco-box {reco_class}">
                <div class="reco-label">RECOMMENDATION</div>
                <div class="reco-title">{reco.recommendation}</div>
                <div class="reco-rationale">{reco.rationale}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Comparison Table
            st.markdown("#### Scenario Comparison")
            
            refurb_available = tco_refurb.get("available", False)
            
            results_data = [
                {
                    "Scenario": "🔄 Keep Current",
                    "Annual TCO": f"€{tco_keep['total']:.0f}",
                    "Annual CO₂": f"{co2_keep['total']:.1f} kg",
                    "Notes": f"Productivity loss: {tco_keep.get('productivity_loss_pct', 0)*100:.0f}%"
                },
                {
                    "Scenario": "🆕 Buy New",
                    "Annual TCO": f"€{tco_new['total']:.0f}",
                    "Annual CO₂": f"{co2_new['total']:.1f} kg",
                    "Notes": "Full manufacturing CO₂"
                }
            ]
            
            if refurb_available:
                results_data.append({
                    "Scenario": "♻️ Buy Refurbished",
                    "Annual TCO": f"€{tco_refurb['total']:.0f}",
                    "Annual CO₂": f"{co2_refurb['total']:.1f} kg",
                    "Notes": "80% less manufacturing CO₂"
                })
            
            st.dataframe(pd.DataFrame(results_data), use_container_width=True, hide_index=True)
            
            # Savings Summary
            if reco.recommendation != "KEEP":
                st.markdown(f"""
                <div class="alert-box success">
                    <div class="alert-title">💰 Potential Savings</div>
                    <div class="alert-text">
                        By choosing <strong>{reco.recommendation}</strong>, you save approximately 
                        <strong>€{reco.annual_savings:.0f}/year</strong> in TCO and 
                        <strong>{reco.co2_savings:.1f} kg CO₂/year</strong> compared to buying new.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed Breakdown
            with st.expander("📊 View Detailed Breakdown"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Keep Current**")
                    st.write(f"Energy: €{tco_keep['breakdown'].get('energy', 0):.0f}")
                    st.write(f"Productivity Loss: €{tco_keep['breakdown'].get('productivity_loss', 0):.0f}")
                    st.write(f"Residual Loss: €{tco_keep['breakdown'].get('residual_loss', 0):.0f}")
                
                with col2:
                    st.markdown("**Buy New**")
                    st.write(f"Purchase (annual): €{tco_new['breakdown'].get('purchase', 0):.0f}")
                    st.write(f"Energy: €{tco_new['breakdown'].get('energy', 0):.0f}")
                    st.write(f"Disposal: €{tco_new['breakdown'].get('disposal', 0):.0f}")
                
                if refurb_available:
                    with col3:
                        st.markdown("**Buy Refurbished**")
                        st.write(f"Purchase (annual): €{tco_refurb['breakdown'].get('purchase', 0):.0f}")
                        st.write(f"Energy: €{tco_refurb['breakdown'].get('energy', 0):.0f}")
                        st.write(f"Disposal: €{tco_refurb['breakdown'].get('disposal', 0):.0f}")
    
    # Restart button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← START NEW ANALYSIS", key="btn_restart"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state["stage"] = "opening"
            st.rerun()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def run():
    """Main application entry point."""
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)
    inject_credibility_css()  
    
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