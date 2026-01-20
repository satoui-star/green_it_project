"""
Élysia - Sustainable IT Intelligence
======================================
LVMH · Digital Sustainability Division

Version: 3.1.0 (Production)
FIXED VERSION with:
- Navigation bug fix (session_state conflict resolved)
- Logo display fix
- Improved UX with clearer section names
- Better action plan design
- Export functionality
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import io
import uuid
import time
import base64
import os

# =============================================================================
# BACKEND IMPORTS
# =============================================================================

from calculator import (
    ShockCalculator, HopeCalculator, StrategySimulator,
    validate_fleet_data, validate_device_inputs,
    generate_demo_fleet, generate_synthetic_fleet,
    export_recommendations_to_csv, generate_markdown_report,
    FleetAnalyzer, RecommendationEngine,
    DeviceRecommendation, StrategyResult
)
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
# LOGO PATH CONFIGURATION (FIXED)
# =============================================================================

def _get_project_root() -> str:
    """Get the project root directory."""
    # Try to find the project root by looking for the logo folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check current directory
    if os.path.exists(os.path.join(current_dir, "logo.png")):
        return current_dir
    
    # Check parent directory
    parent_dir = os.path.dirname(current_dir)
    if os.path.exists(os.path.join(parent_dir, "logo.png")):
        return parent_dir
    
    # Fallback to workspace path
    workspace_path = "/workspaces/green_it_project"
    if os.path.exists(workspace_path):
        return workspace_path
    
    return current_dir


PROJECT_ROOT = _get_project_root()

LOGO_PATHS = {
    "icon": os.path.join(PROJECT_ROOT, "logo.png", "elysia_icon.png"),
    "logo": os.path.join(PROJECT_ROOT, "logo.png", "elysia_logo.png"),
}


def get_logo_path(name: str) -> Optional[str]:
    """Get logo path if it exists."""
    path = LOGO_PATHS.get(name)
    if path and os.path.exists(path):
        return path
    return None


def _img_to_base64(path: str) -> str:
    """Convert image to base64 data URI."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


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
    gap: 0.75rem;
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
   PROGRESS INDICATOR (NEW)
   ============================================ */
.progress-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.progress-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.progress-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--border);
    transition: all 0.3s ease;
}

.progress-dot.active {
    background: var(--gold);
    box-shadow: 0 0 0 4px rgba(138, 108, 74, 0.2);
}

.progress-dot.completed {
    background: var(--success);
}

.progress-line {
    width: 40px;
    height: 2px;
    background: var(--border);
}

.progress-line.completed {
    background: var(--success);
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
    gap: 1rem;
    margin-bottom: 2rem;
}

.opening-icon {
    width: 80px;
    height: auto;
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

.alert-box.info {
    background: #E3F2FD;
    border-left: 4px solid #1976D2;
}

.alert-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.alert-box.warning .alert-title { color: var(--danger); }
.alert-box.success .alert-title { color: var(--success); }
.alert-box.info .alert-title { color: #1976D2; }

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
    border: 2px solid var(--gold) !important;
    box-shadow: none !important;
}

.stDownloadButton > button:hover {
    background: var(--gold) !important;
    color: white !important;
}

/* ============================================
   TABS - CLEANER STYLE
   ============================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.25rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-mid) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 8px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--gold) !important;
    background: var(--warm-white) !important;
}

.stTabs [aria-selected="true"] {
    color: white !important;
    background: var(--gold) !important;
}

/* ============================================
   PLAN CARDS (IMPROVED)
   ============================================ */
.plan-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    height: 100%;
    transition: all 0.3s ease;
}

.plan-card:hover {
    border-color: var(--gold);
    box-shadow: 0 4px 16px rgba(138, 108, 74, 0.1);
}

.plan-card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.plan-card-number {
    width: 36px;
    height: 36px;
    background: var(--gold);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 600;
}

.plan-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-dark);
}

.plan-card-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.plan-list {
    margin: 0;
    padding-left: 1.25rem;
    color: var(--text-mid);
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    line-height: 1.7;
}

.plan-list li {
    margin-bottom: 0.5rem;
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

/* ============================================
   SCENARIO CARDS (NEW)
   ============================================ */
.scenario-card {
    background: var(--white);
    border: 2px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.scenario-card.best {
    border-color: var(--success);
}

.scenario-card.realistic {
    border-color: var(--gold);
}

.scenario-card.worst {
    border-color: var(--danger);
}

.scenario-label {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.scenario-card.best .scenario-label { color: var(--success); }
.scenario-card.realistic .scenario-label { color: var(--gold); }
.scenario-card.worst .scenario-label { color: var(--danger); }

.scenario-strategy {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-mid);
    margin-bottom: 1rem;
}

.scenario-details {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-light);
    line-height: 1.6;
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


# =============================================================================
# HEADER COMPONENT (FIXED)
# =============================================================================

def render_header():
    """Render the luxury header with proper logo handling."""
    icon_path = get_logo_path("icon")
    logo_path = get_logo_path("logo")
    
    st.markdown("<div class='lux-header'>", unsafe_allow_html=True)
    
    # Build header HTML
    if icon_path or logo_path:
        header_html = "<div class='lux-header-brand'>"
        
        if icon_path:
            icon_b64 = _img_to_base64(icon_path)
            header_html += f'<img src="{icon_b64}" style="height:40px; width:auto;">'
        else:
            header_html += '<span class="lux-header-icon">🌿</span>'
        
        if logo_path:
            logo_b64 = _img_to_base64(logo_path)
            header_html += f'<img src="{logo_b64}" style="height:36px; width:auto; margin-left:8px;">'
        else:
            header_html += '<span class="lux-header-title">ÉLYSIA</span>'
        
        header_html += "</div>"
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="lux-header-brand">
            <span class="lux-header-icon">🌿</span>
            <span class="lux-header-title">ÉLYSIA</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="lux-header-sub">Sustainable IT Intelligence</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_act_badge(num, title):
    """Render act indicator badge."""
    st.markdown(f"""
    <div style="text-align: center;">
        <span class="act-badge">ACT {num} · {title}</span>
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(current_step: int, total_steps: int = 5):
    """Render a visual progress bar."""
    steps = ["Calibrate", "Impact", "Opportunity", "Strategy", "Execute"]
    
    html = '<div class="progress-bar">'
    for i, step in enumerate(steps):
        dot_class = "completed" if i < current_step else ("active" if i == current_step else "")
        html += f'<div class="progress-step">'
        html += f'<div class="progress-dot {dot_class}"></div>'
        if i < len(steps) - 1:
            line_class = "completed" if i < current_step else ""
            html += f'<div class="progress-line {line_class}"></div>'
        html += '</div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


# =============================================================================
# NAVIGATION FIX - This is the critical fix
# =============================================================================

def safe_goto(stage: str):
    """Safely navigate to a stage without session_state conflicts."""
    st.session_state["stage"] = stage
    st.rerun()


def safe_goto_step(step: int, labels: List[str]):
    """Safely navigate to a step within action stage."""
    step = int(max(0, min(step, len(labels) - 1)))
    st.session_state["action_step"] = step
    # Don't set action_nav_choice here - let the widget control it
    st.rerun()


# =============================================================================
# ACT SCREENS
# =============================================================================

def render_opening():
    """Opening screen with proper logo display."""
    icon_path = get_logo_path("icon")
    logo_path = get_logo_path("logo")
    
    st.markdown('<div class="opening-wrap">', unsafe_allow_html=True)
    
    # Brand section
    brand_html = '<div class="opening-brand">'
    if icon_path:
        icon_b64 = _img_to_base64(icon_path)
        brand_html += f'<img src="{icon_b64}" class="opening-icon" style="width:80px; height:auto;">'
    else:
        brand_html += '<span style="font-size:4rem;">🌿</span>'
    
    if logo_path:
        logo_b64 = _img_to_base64(logo_path)
        brand_html += f'<img src="{logo_b64}" style="height:80px; width:auto;">'
    else:
        brand_html += '<span class="opening-title">ÉLYSIA</span>'
    
    brand_html += '</div>'
    st.markdown(brand_html, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="opening-tagline">
        "Every device tells a story.<br>
        What story is your fleet telling?"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Discover →", key="btn_start", use_container_width=True):
            safe_goto("shock_q")


def render_shock_question():
    """Act 0: Baseline calibration."""
    render_header()
    render_progress_bar(0)
    render_act_badge(0, "CALIBRATION")

    st.markdown(
        "<h2 style='text-align: center; margin-bottom: 0.75rem;'>Calibrate your baseline</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#6B6560; margin-bottom: 2rem;'>"
        "Answer 5 quick questions to personalize your analysis."
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

            safe_goto("shock_reveal")


def render_shock_reveal():
    """Act 1: Shock reveal with metrics."""
    render_header()
    render_progress_bar(1)
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
            safe_goto("hope")


def render_hope():
    """Act 2: The Hope comparison."""
    render_header()
    render_progress_bar(2)
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
            safe_goto("clarity")


def render_clarity():
    """Act 3: The 5 questions (strategy calibration)."""
    render_header()
    render_progress_bar(3)
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

    existing_refresh = st.session_state.get("refresh_cycle", None)
    existing_target = st.session_state.get("target_pct", None)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("strategy_form"):
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
                    m = bracket.replace("€", "").replace("M", "")
                    budget = int(float(m) * 1_000_000)

            if budget is not None:
                st.caption(f"💡 That's approximately **{fmt_currency(budget)}**/year")

            st.markdown("<br>", unsafe_allow_html=True)

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
                    st.session_state["action_step"] = 0  # Reset action step

                    safe_goto("action")


# =============================================================================
# ACT 4: ACTION (COMPLETELY REWRITTEN WITH TABS)
# =============================================================================

def _get_fleet_df() -> Optional[pd.DataFrame]:
    df = st.session_state.get("fleet_data")
    if df is None:
        return None
    if isinstance(df, pd.DataFrame) and len(df) > 0:
        return df
    return None


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
    profile["fleet_size"] = int(len(df))
    
    if "Age_Years" in df.columns:
        try:
            profile["avg_age"] = float(pd.to_numeric(df["Age_Years"], errors="coerce").dropna().mean())
        except Exception:
            pass

    profile["annual_replacements"] = int(round(profile["fleet_size"] / refresh_cycle))

    if "Age_Years" in df.columns:
        ages = pd.to_numeric(df["Age_Years"], errors="coerce")
        valid = ages.dropna()
        if len(valid) > 0:
            profile["age_risk_share"] = float((valid >= 4.0).mean())

    model_col = "Device_Model" if "Device_Model" in df.columns else None
    if model_col:
        models = df[model_col].astype(str)
        counts = models.value_counts()
        
        refurb_eligible = 0
        annual_new_spend = 0.0

        for model, cnt in counts.items():
            meta = DEVICES.get(model)
            annual_qty = float(cnt) / refresh_cycle

            if isinstance(meta, dict):
                price_new = float(meta.get("price_new_eur", 0.0))
                annual_new_spend += annual_qty * price_new

                refurb_ok = bool(meta.get("refurb_available", False))
                if refurb_ok:
                    refurb_eligible += int(cnt)

        profile["eligible_refurb_share"] = float(refurb_eligible / profile["fleet_size"]) if profile["fleet_size"] else 0.0
        profile["annual_new_spend_eur"] = annual_new_spend

    return profile


def _pick_strategy(results: List[StrategyResult], priority: str) -> StrategyResult:
    """Pick best strategy from a list."""
    if not results:
        raise ValueError("No strategies to select from")

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
        else:
            base = 0.60 * savings + 0.20 * co2 + 0.20 * risk

        return base + 0.75 * reaches

    candidates = [r for r in results if r.strategy_key != "do_nothing"] or results
    return max(candidates, key=score)


def render_action():
    """Act 4: Strategy experience - REWRITTEN WITH TABS."""
    render_header()
    render_progress_bar(4)
    render_act_badge(4, "YOUR STRATEGY")

    # Base inputs
    refresh_cycle = int(st.session_state.get("refresh_cycle", 4) or 4)
    target_pct = int(st.session_state.get("target_pct", -20) or -20)
    priority = st.session_state.get("priority", "cost")

    # Compute profile
    df = _get_fleet_df()
    profile = _compute_fleet_profile(df, refresh_cycle)

    fleet_size = int(profile["fleet_size"])
    avg_age = float(profile["avg_age"])

    # Get strategies
    results_all = StrategySimulator.compare_all_strategies(
        fleet_size=fleet_size,
        current_refresh=refresh_cycle,
        avg_age=avg_age,
        target_pct=target_pct,
        time_horizon_months=36,
    )

    selected = _pick_strategy(results_all, priority)
    confidence = "HIGH" if profile.get("data_mode") == "measured" else "MEDIUM"

    # Reset button
    col_reset = st.columns([6, 1])
    with col_reset[1]:
        if st.button("🔄 Reset", key="btn_reset_action"):
            for k in list(st.session_state.keys()):
                if not k.startswith("_"):
                    del st.session_state[k]
            st.session_state["stage"] = "opening"
            st.rerun()

    # TABS - This replaces the broken radio navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Your Strategy",
        "🔄 Compare Options",
        "📁 Upload Data",
        "🎛️ Device Simulator",
        "📋 Action Plan"
    ])

    # TAB 1: Strategy Overview
    with tab1:
        st.markdown(f"""
        <div class="gold-ticket">
            <div class="gold-ticket-label">◆ RECOMMENDED STRATEGY</div>
            <div class="gold-ticket-title">{selected.strategy_name}</div>
            <div class="gold-ticket-desc">{selected.description}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CO₂ reduction", f"-{abs(selected.co2_reduction_pct):.0f}%")
        c2.metric("Annual savings", fmt_currency(selected.annual_savings_eur))
        c3.metric("Time to target", f"{selected.time_to_target_months} mo" if selected.time_to_target_months < 999 else "—")
        c4.metric("Confidence", confidence)

        if profile.get("data_mode") != "measured":
            st.markdown(
                """<div class='alert-box info'>
                <div class='alert-title'>💡 Increase confidence</div>
                <div class='alert-text'>Upload your fleet data in the "Upload Data" tab to replace estimates with real numbers.</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # TAB 2: Compare Strategies
    with tab2:
        st.markdown("### Compare Strategies")
        st.caption("See how different approaches stack up against each other.")

        # Scenario cards
        non_baseline = [r for r in results_all if r.strategy_key != "do_nothing"]
        best_case = max(non_baseline, key=lambda r: abs(r.co2_reduction_pct)) if non_baseline else selected
        baseline = next((r for r in results_all if r.strategy_key == "do_nothing"), None)

        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
            <div class="scenario-card best">
                <div class="scenario-label">BEST CASE</div>
                <div class="scenario-strategy">{best_case.strategy_name}</div>
                <div class="scenario-details">
                    CO₂: <strong>-{abs(best_case.co2_reduction_pct):.0f}%</strong><br>
                    Savings: <strong>{fmt_currency(best_case.annual_savings_eur)}</strong><br>
                    Time: <strong>{best_case.time_to_target_months}mo</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="scenario-card realistic">
                <div class="scenario-label">RECOMMENDED</div>
                <div class="scenario-strategy">{selected.strategy_name}</div>
                <div class="scenario-details">
                    CO₂: <strong>-{abs(selected.co2_reduction_pct):.0f}%</strong><br>
                    Savings: <strong>{fmt_currency(selected.annual_savings_eur)}</strong><br>
                    Time: <strong>{selected.time_to_target_months}mo</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            if baseline:
                st.markdown(f"""
                <div class="scenario-card worst">
                    <div class="scenario-label">DO NOTHING</div>
                    <div class="scenario-strategy">{baseline.strategy_name}</div>
                    <div class="scenario-details">
                        CO₂: <strong>-{abs(baseline.co2_reduction_pct):.0f}%</strong><br>
                        Savings: <strong>{fmt_currency(baseline.annual_savings_eur)}</strong><br>
                        Status: <strong style="color:#9E4A4A;">MISS TARGET</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### Full Comparison")
        comparison_data = []
        ranked = sorted(results_all, key=lambda x: (not x.reaches_target, -abs(x.co2_reduction_pct)))
        for r in ranked:
            comparison_data.append({
                "Strategy": r.strategy_name,
                "CO₂": f"-{abs(r.co2_reduction_pct):.0f}%",
                "Savings": fmt_currency(r.annual_savings_eur),
                "Time to target": f"{r.time_to_target_months}mo" if r.time_to_target_months < 999 else "Never",
                "Reaches Target": "✅" if r.reaches_target else "❌",
            })
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

    # TAB 3: Upload Data
    with tab3:
        st.markdown("### Upload Your Fleet Data")
        st.caption("Replace estimates with real data to increase confidence.")

        col_upload, col_demo = st.columns([2, 1])
        with col_upload:
            uploaded_file = st.file_uploader(
                "Upload Fleet CSV",
                type=["csv"],
                key="fleet_upload_tab",
                help="Required columns: Device_Model, Age_Years. Optional: Persona, Country",
            )

        with col_demo:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Load Demo Fleet", use_container_width=True, key="btn_demo"):
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
                    st.success(f"✓ Loaded {len(df_up)} devices")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

        # Show current data
        df2 = _get_fleet_df()
        profile2 = _compute_fleet_profile(df2, refresh_cycle)

        st.markdown("### Current Fleet Profile")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fleet size", f"{profile2['fleet_size']:,}")
        m2.metric("Avg age", f"{profile2['avg_age']:.1f}y")
        m3.metric("Annual replacements", f"{profile2['annual_replacements']:,}")
        m4.metric("Data source", "Uploaded ✅" if profile2.get("data_mode") == "measured" else "Estimated")

        if profile2.get("age_risk_share") is not None:
            st.info(f"**{int(profile2['age_risk_share']*100)}%** of devices are ≥4 years old (potential risk)")

    # TAB 4: Device Simulator
    with tab4:
        st.markdown("### Device Simulator")
        st.caption("Test what decision makes sense for a specific device.")

        col1, col2, col3 = st.columns(3)
        with col1:
            selected_device = st.selectbox("Device", options=get_device_names(), index=5, key="sim_device")
        with col2:
            selected_persona = st.selectbox("User profile", options=get_persona_names(), index=1, key="sim_persona")
        with col3:
            countries = get_country_codes()
            country = st.selectbox(
                "Location",
                options=list(countries.keys()),
                format_func=lambda x: countries[x],
                index=0,
                key="sim_country",
            )

        col4, col5, col6 = st.columns(3)
        with col4:
            device_age = st.slider("Device age (years)", 0.5, 7.0, 3.5, 0.5, key="sim_age")
        with col5:
            objective = st.selectbox("Objective", ["Balanced", "Min CO₂", "Min cost", "Min risk"], key="sim_obj")
        with col6:
            criticality = st.selectbox("Criticality", ["Low", "Medium", "High"], index=1, key="sim_crit")

        if st.button("Calculate Recommendation", use_container_width=True, key="btn_calc"):
            meta = DEVICES.get(selected_device, {})
            refurb_available = bool(meta.get("refurb_available", False))

            tco_keep = TCOCalculator.calculate_tco_keep(selected_device, device_age, selected_persona, country)
            tco_new = TCOCalculator.calculate_tco_new(selected_device, selected_persona, country)
            tco_refurb = TCOCalculator.calculate_tco_refurb(selected_device, selected_persona, country)

            co2_keep = CO2Calculator.calculate_co2_keep(selected_device, selected_persona, country)
            co2_new = CO2Calculator.calculate_co2_new(selected_device, selected_persona, country)
            co2_refurb = CO2Calculator.calculate_co2_refurb(selected_device, selected_persona, country)

            # Simple decision logic
            options = [
                ("KEEP", tco_keep["total"], co2_keep["total"]),
                ("NEW", tco_new["total"], co2_new["total"]),
            ]
            if refurb_available and tco_refurb.get("available", True):
                options.append(("REFURBISHED", tco_refurb["total"], co2_refurb["total"]))

            if objective == "Min cost":
                best = min(options, key=lambda x: x[1])
            elif objective == "Min CO₂":
                best = min(options, key=lambda x: x[2])
            else:
                best = min(options, key=lambda x: (x[1] + x[2]) / 2)

            reco_key = best[0]
            reco_class = "keep" if reco_key == "KEEP" else ("new" if reco_key == "NEW" else "")
            
            st.markdown(f"""
            <div class="reco-box {reco_class}">
                <div class="reco-label">RECOMMENDATION</div>
                <div class="reco-title">{reco_key}</div>
                <div class="reco-rationale">Based on {objective.lower()} optimization for {criticality.lower()} criticality device.</div>
            </div>
            """, unsafe_allow_html=True)

            # Show comparison
            st.markdown("### Cost & CO₂ Comparison")
            comp_df = pd.DataFrame([
                {"Option": "Keep", "Annual TCO": f"€{tco_keep['total']:,.0f}", "Annual CO₂": f"{co2_keep['total']:.0f}kg"},
                {"Option": "Buy New", "Annual TCO": f"€{tco_new['total']:,.0f}", "Annual CO₂": f"{co2_new['total']:.0f}kg"},
            ])
            if refurb_available:
                comp_df = pd.concat([comp_df, pd.DataFrame([
                    {"Option": "Refurbished", "Annual TCO": f"€{tco_refurb['total']:,.0f}", "Annual CO₂": f"{co2_refurb['total']:.0f}kg"}
                ])], ignore_index=True)
            st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # TAB 5: Action Plan
    with tab5:
        st.markdown("### Your 90-Day Action Plan")
        st.caption("A board-ready execution blueprint.")

        # Phase cards
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
            <div class="plan-card">
                <div class="plan-card-header">
                    <div class="plan-card-number">1</div>
                    <div>
                        <div class="plan-card-title">Governance</div>
                        <div class="plan-card-subtitle">Days 1–30</div>
                    </div>
                </div>
                <ul class="plan-list">
                    <li>Form steering committee</li>
                    <li>Lock KPIs and success criteria</li>
                    <li>Define pilot scope</li>
                    <li>Select initial vendor</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="plan-card">
                <div class="plan-card-header">
                    <div class="plan-card-number">2</div>
                    <div>
                        <div class="plan-card-title">Pilot</div>
                        <div class="plan-card-subtitle">Days 31–60</div>
                    </div>
                </div>
                <ul class="plan-list">
                    <li>Deploy 100–300 devices</li>
                    <li>Measure failure rate</li>
                    <li>Track support tickets</li>
                    <li>Survey user satisfaction</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div class="plan-card">
                <div class="plan-card-header">
                    <div class="plan-card-number">3</div>
                    <div>
                        <div class="plan-card-title">Scale</div>
                        <div class="plan-card-subtitle">Days 61–90</div>
                    </div>
                </div>
                <ul class="plan-list">
                    <li>Expand to 10–20% of fleet</li>
                    <li>Update procurement workflows</li>
                    <li>Train IT support team</li>
                    <li>Launch internal comms</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Success Metrics")
        metrics_df = pd.DataFrame([
            {"Metric": "Refurbished adoption rate", "Owner": "Procurement", "Frequency": "Monthly", "Target": "↑"},
            {"Metric": "Device failure rate", "Owner": "IT Ops", "Frequency": "Monthly", "Target": "< 1.5%"},
            {"Metric": "Annual savings (validated)", "Owner": "Finance", "Frequency": "Quarterly", "Target": "€"},
            {"Metric": "CO₂ trajectory", "Owner": "Sustainability", "Frequency": "Quarterly", "Target": "On track"},
        ])
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        st.markdown("### Export Your Strategy")
        
        # Generate report
        try:
            report_md = f"""# Élysia Strategy Report
Generated: {time.strftime('%Y-%m-%d %H:%M')}

## Recommended Strategy: {selected.strategy_name}

{selected.description}

### Key Metrics
- **CO₂ Reduction:** {selected.co2_reduction_pct}%
- **Annual Savings:** €{selected.annual_savings_eur:,.0f}
- **Time to Target:** {selected.time_to_target_months} months
- **Confidence Level:** {confidence}

### Fleet Profile
- **Fleet Size:** {fleet_size:,} devices
- **Average Age:** {avg_age:.1f} years
- **Refresh Cycle:** {refresh_cycle} years
- **Target:** {target_pct}% CO₂ reduction

### Next Steps
1. Form steering committee (Week 1)
2. Select vendor partners (Week 2-3)
3. Launch pilot with 100-300 devices (Month 2)
4. Scale based on results (Month 3)
"""
        except Exception:
            report_md = "Error generating report"

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "📄 Download Report (MD)",
                data=report_md,
                file_name="elysia_strategy_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_dl2:
            # Create CSV of strategies
            strat_csv = pd.DataFrame([{
                "Strategy": r.strategy_name,
                "CO2_Reduction_Pct": r.co2_reduction_pct,
                "Annual_Savings_EUR": r.annual_savings_eur,
                "Time_to_Target_Months": r.time_to_target_months,
                "Reaches_Target": r.reaches_target,
            } for r in results_all]).to_csv(index=False)
            
            st.download_button(
                "📊 Download Strategies (CSV)",
                data=strat_csv,
                file_name="elysia_strategies.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Methodology
        with st.expander("📚 Methodology & Sources"):
            render_methodology_tab()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def run():
    """Main application entry point."""
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)
    inject_credibility_css()
    
    # Session init
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["session_started_at"] = time.time()
    
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
