"""
Élysia - Sustainable IT Intelligence
=====================================
LVMH · Digital Sustainability Division

V4: Light theme, business-level questions, Élysia branding
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64

# =============================================================================
# IMPORTS FROM LOCAL MODULES
# =============================================================================
try:
    from reference_data_API import (
        PERSONAS, DEVICES, GRID_CARBON_FACTORS, DEFAULT_GRID_FACTOR,
        DEPRECIATION_CURVE, MAISONS, REFURB_CONFIG, STRATEGIES,
        HOURS_ANNUAL, PRICE_KWH_EUR, DISPOSAL_COST_WITH_DATA, DISPOSAL_COST_NO_DATA,
        get_device_names, get_persona_names, get_country_codes, get_maison_names,
        get_grid_factor, get_depreciation_rate
    )
    from calculator import (
        TCOCalculator, CO2Calculator, UrgencyCalculator, 
        RecommendationEngine, StrategySimulator, FleetAnalyzer,
        generate_demo_fleet
    )
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    IMPORT_ERROR = str(e)

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Élysia | LVMH Sustainable IT",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# ÉLYSIA LIGHT THEME - LUXURY & CLEAN
# =============================================================================
ELYSIA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-primary: #FAFAF8;
    --bg-secondary: #F5F3EF;
    --bg-card: #FFFFFF;
    --bg-input: #FFFFFF;
    --border-light: #E8E4DD;
    --border-medium: #D4CFC5;
    --border-focus: #8a6c4a;
    --text-primary: #2D2A26;
    --text-secondary: #6B6560;
    --text-muted: #9A958E;
    --accent-bronze: #8a6c4a;
    --accent-bronze-light: #a8896a;
    --accent-bronze-dark: #6d5539;
    --success: #4A7C59;
    --success-light: #E8F0EA;
    --warning: #C4943A;
    --warning-light: #FBF5E9;
    --danger: #9E4A4A;
    --danger-light: #F9EDED;
}

/* Base App - LIGHT BACKGROUND */
.stApp {
    background: var(--bg-primary) !important;
}

/* Hide Streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

p, span, div, label, li {
    font-family: 'Inter', sans-serif !important;
}

/* ============================================
   HEADER WITH LOGO
   ============================================ */

.elysia-header {
    text-align: center;
    padding: 2.5rem 0 2rem 0;
    border-bottom: 1px solid var(--border-light);
    margin-bottom: 2rem;
    background: linear-gradient(180deg, #FFFFFF 0%, var(--bg-primary) 100%);
}

.elysia-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.elysia-logo-icon {
    width: 50px;
    height: auto;
}

.elysia-logo-text {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 500;
    color: var(--accent-bronze);
    letter-spacing: 0.02em;
}

.elysia-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--text-secondary);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ============================================
   TABS
   ============================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border-light);
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
    border: none !important;
    padding: 1rem 2rem !important;
    font-weight: 500 !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--accent-bronze) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent-bronze) !important;
    border-bottom: 2px solid var(--accent-bronze) !important;
}

/* ============================================
   FORM INPUTS - LIGHT THEME
   ============================================ */

/* Labels */
.stSelectbox label, 
.stNumberInput label, 
.stSlider label,
.stTextInput label,
.stCheckbox label,
.stRadio label,
.stMultiSelect label {
    color: var(--text-primary) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 0.5rem !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    min-height: 48px !important;
}

.stSelectbox > div > div:hover {
    border-color: var(--accent-bronze) !important;
}

.stSelectbox > div > div:focus-within {
    border-color: var(--accent-bronze) !important;
    box-shadow: 0 0 0 3px rgba(138, 108, 74, 0.15) !important;
}

/* Dropdown text */
.stSelectbox [data-baseweb="select"] span {
    color: var(--text-primary) !important;
}

/* Dropdown menu */
[data-baseweb="menu"], 
[data-baseweb="popover"] > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
}

[data-baseweb="menu"] li,
[role="option"] {
    color: var(--text-primary) !important;
    background-color: var(--bg-card) !important;
}

[data-baseweb="menu"] li:hover,
[role="option"]:hover {
    background-color: var(--bg-secondary) !important;
}

/* Number Input */
.stNumberInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    min-height: 48px !important;
    font-size: 1rem !important;
}

.stNumberInput > div > div > input:hover {
    border-color: var(--accent-bronze) !important;
}

.stNumberInput > div > div > input:focus {
    border-color: var(--accent-bronze) !important;
    box-shadow: 0 0 0 3px rgba(138, 108, 74, 0.15) !important;
}

/* Number input buttons */
.stNumberInput button {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border-medium) !important;
    color: var(--text-primary) !important;
}

.stNumberInput button:hover {
    background-color: var(--accent-bronze) !important;
    color: white !important;
    border-color: var(--accent-bronze) !important;
}

/* Slider */
.stSlider > div > div > div[data-baseweb="slider"] > div {
    background: var(--border-medium) !important;
}

.stSlider > div > div > div[data-baseweb="slider"] > div > div {
    background: var(--accent-bronze) !important;
}

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent-bronze) !important;
    border: 3px solid white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}

/* Checkbox & Radio */
.stCheckbox > label > div[data-testid="stMarkdownContainer"] > p,
.stRadio > label > div > p {
    color: var(--text-primary) !important;
}

.stCheckbox input:checked + div {
    background-color: var(--accent-bronze) !important;
    border-color: var(--accent-bronze) !important;
}

/* Multiselect */
.stMultiSelect > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
}

.stMultiSelect > div > div:focus-within {
    border-color: var(--accent-bronze) !important;
    box-shadow: 0 0 0 3px rgba(138, 108, 74, 0.15) !important;
}

/* Tags in multiselect */
.stMultiSelect [data-baseweb="tag"] {
    background-color: var(--accent-bronze) !important;
    color: white !important;
}

/* ============================================
   CARDS
   ============================================ */

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 1.75rem;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.metric-card:hover {
    border-color: var(--accent-bronze);
    box-shadow: 0 8px 25px rgba(138, 108, 74, 0.1);
    transform: translateY(-3px);
}

.metric-card .value {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    color: var(--accent-bronze);
    font-weight: 500;
    line-height: 1.2;
}

.metric-card .label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.75rem;
}

.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: var(--text-primary);
    letter-spacing: 0.02em;
    border-bottom: 1px solid var(--border-light);
    padding-bottom: 0.75rem;
    margin: 2.5rem 0 1.5rem 0;
}

/* ============================================
   HERO STATS
   ============================================ */

.hero-stat {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 2rem 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.hero-stat:hover {
    border-color: var(--accent-bronze);
    box-shadow: 0 8px 25px rgba(138, 108, 74, 0.1);
    transform: translateY(-3px);
}

.hero-stat .number {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    color: var(--accent-bronze);
    font-weight: 500;
}

.hero-stat .description {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.75rem;
    line-height: 1.6;
}

/* ============================================
   ALERT BOXES
   ============================================ */

.info-box {
    background: var(--bg-card);
    border-left: 4px solid var(--accent-bronze);
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.info-box p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
}

.warning-box {
    background: var(--danger-light);
    border-left: 4px solid var(--danger);
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
}

.warning-box .title {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--danger);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.warning-box .text {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.success-box {
    background: var(--success-light);
    border-left: 4px solid var(--success);
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
}

.success-box .title {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--success);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.success-box .text {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* ============================================
   COMPARISON BOXES
   ============================================ */

.comparison-box {
    background: var(--bg-card);
    border: 2px solid var(--border-light);
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s ease;
}

.comparison-box.current {
    border-color: var(--danger);
    background: var(--danger-light);
}

.comparison-box.optimized {
    border-color: var(--success);
    background: var(--success-light);
}

.comparison-box .status {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.75rem;
    font-weight: 600;
}

.comparison-box.current .status { color: var(--danger); }
.comparison-box.optimized .status { color: var(--success); }

.comparison-box .value {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    color: var(--text-primary);
    margin: 0.5rem 0;
    font-weight: 500;
}

.comparison-box .label {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* ============================================
   WINNER BOX
   ============================================ */

.winner-box {
    background: linear-gradient(135deg, #FAF6F1 0%, #F5EFE6 100%);
    border: 2px solid var(--accent-bronze);
    padding: 2rem;
    border-radius: 12px;
    margin: 1.5rem 0;
}

.winner-box .rank {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--accent-bronze);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 600;
}

.winner-box .name {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: var(--text-primary);
    margin: 0.5rem 0;
    font-weight: 500;
}

.winner-box .metrics {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.8;
}

/* ============================================
   BUTTONS
   ============================================ */

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    background: var(--accent-bronze) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.85rem 2.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(138, 108, 74, 0.2) !important;
}

.stButton > button:hover {
    background: var(--accent-bronze-dark) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(138, 108, 74, 0.3) !important;
}

/* Secondary button style */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--accent-bronze) !important;
    border: 1px solid var(--accent-bronze) !important;
    box-shadow: none !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--accent-bronze) !important;
    color: white !important;
}

/* ============================================
   DATA TABLES
   ============================================ */

.stDataFrame {
    border: 1px solid var(--border-light) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

.stDataFrame th {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

.stDataFrame td {
    color: var(--text-primary) !important;
}

/* ============================================
   EXPANDER
   ============================================ */

.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

.streamlit-expanderHeader:hover {
    color: var(--accent-bronze) !important;
    border-color: var(--accent-bronze) !important;
}

.streamlit-expanderContent {
    border: 1px solid var(--border-light) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    background: var(--bg-card) !important;
}

/* ============================================
   FILE UPLOADER
   ============================================ */

.stFileUploader > div {
    background-color: var(--bg-card) !important;
    border: 2px dashed var(--border-medium) !important;
    border-radius: 12px !important;
    padding: 2rem !important;
}

.stFileUploader > div:hover {
    border-color: var(--accent-bronze) !important;
    background-color: var(--bg-secondary) !important;
}

/* ============================================
   QUESTION CARDS
   ============================================ */

.question-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.question-card .question-number {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: var(--accent-bronze);
    margin-bottom: 1rem;
}

.question-hint {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: var(--bg-secondary);
    border-radius: 6px;
    display: inline-block;
}

/* ============================================
   RECOMMENDATION BOXES
   ============================================ */

.reco-box {
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    margin: 1rem 0;
    transition: all 0.3s ease;
}

.reco-keep {
    background: var(--success-light);
    border: 2px solid var(--success);
}

.reco-refurb, .reco-refurbished {
    background: linear-gradient(135deg, #FAF6F1 0%, #F5EFE6 100%);
    border: 2px solid var(--accent-bronze);
}

.reco-new {
    background: #F0F4F8;
    border: 2px solid #6A8CAA;
}

.reco-box .title {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: var(--text-primary);
    font-weight: 500;
}

.reco-box .subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 0.75rem;
    line-height: 1.6;
}

/* ============================================
   URGENCY BADGES
   ============================================ */

.urgency-high {
    background: var(--danger);
    color: white;
    padding: 0.35rem 1rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    display: inline-block;
}

.urgency-medium {
    background: var(--warning);
    color: white;
    padding: 0.35rem 1rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    display: inline-block;
}

.urgency-low {
    background: var(--success);
    color: white;
    padding: 0.35rem 1rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    display: inline-block;
}

/* ============================================
   INTEGRATION MOCKUP
   ============================================ */

.integration-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.integration-card:hover {
    border-color: var(--accent-bronze);
    box-shadow: 0 4px 15px rgba(138, 108, 74, 0.1);
}

.integration-card.disabled {
    opacity: 0.6;
}

.integration-card .icon {
    font-size: 2rem;
    margin-bottom: 0.75rem;
}

.integration-card .name {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-primary);
    font-weight: 500;
}

.integration-card .status {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
}

/* ============================================
   ANIMATIONS
   ============================================ */

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease-out forwards;
}

/* ============================================
   SOURCE NOTE
   ============================================ */

.source-note {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-muted);
    font-style: italic;
    margin-top: 1rem;
}
</style>
"""

# =============================================================================
# ÉLYSIA LOGO - Using image file
# =============================================================================
import base64
from pathlib import Path

def get_logo_base64():
    """Load logo image and convert to base64 for embedding in HTML."""
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent / "logo.png" / "elysia_logo.png",  # ../logo.png/elysia_logo.png
        Path(__file__).parent / "elysia_logo.png",  # Same folder
        Path(__file__).parent.parent / "assets" / "elysia_logo.png",  # ../assets/
    ]
    
    for logo_path in possible_paths:
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

ELYSIA_LOGO_BASE64 = get_logo_base64()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_currency(value):
    if value is None:
        return "—"
    if abs(value) >= 1_000_000:
        return f"€{value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"€{value/1_000:.0f}K"
    else:
        return f"€{value:.0f}"

def format_co2(value):
    if value is None:
        return "—"
    if abs(value) >= 1000:
        return f"{value/1000:.1f}t"
    else:
        return f"{value:.0f}kg"

def estimate_fleet_from_budget(annual_budget, avg_device_cost=1000, refresh_years=4):
    """Estimate fleet size from annual IT budget."""
    return int(annual_budget / avg_device_cost * refresh_years)

def estimate_co2_from_fleet(fleet_size, avg_co2_per_device=50):
    """Estimate annual CO2 from fleet size."""
    return fleet_size * avg_co2_per_device / 1000  # tonnes

def get_urgency_html(level):
    if level == "HIGH":
        return '<span class="urgency-high">HIGH PRIORITY</span>'
    elif level == "MEDIUM":
        return '<span class="urgency-medium">MEDIUM</span>'
    else:
        return '<span class="urgency-low">LOW</span>'

def get_recommendation_class(reco):
    reco_lower = reco.lower()
    if "keep" in reco_lower:
        return "reco-keep"
    elif "refurb" in reco_lower:
        return "reco-refurb"
    return "reco-new"


def create_strategy_chart(results, target_pct, current_co2):
    """Create strategy projection chart with Élysia styling."""
    fig = go.Figure()
    
    # Bronze-based color palette
    colors = {
        "Baseline": "#9E4A4A",  # Danger red
        "Lifecycle Extension": "#4A7C59",  # Success green
        "Circular Procurement": "#8a6c4a",  # Bronze
        "Asset Recovery": "#C4943A",  # Warning amber
        "Combined Optimization": "#6A8CAA",  # Soft blue
        "Aggressive Transition": "#4A7C59"  # Success green
    }
    
    for result in results:
        name = result.strategy_name
        monthly_co2 = result.monthly_co2
        
        if monthly_co2:
            months = list(range(len(monthly_co2)))
            is_baseline = name == "Baseline"
            
            fig.add_trace(go.Scatter(
                x=months,
                y=monthly_co2,
                mode='lines',
                name=name,
                line=dict(
                    color=colors.get(name, "#8a6c4a"),
                    width=3 if not is_baseline else 2,
                    dash='dash' if is_baseline else 'solid'
                ),
                hovertemplate=f"<b>{name}</b><br>Month %{{x}}<br>CO₂: %{{y:,.0f}}t<extra></extra>"
            ))
    
    target_co2 = current_co2 * (1 + target_pct/100)
    
    # Target line
    fig.add_hline(
        y=target_co2,
        line_dash="dot",
        line_color="#8a6c4a",
        line_width=2,
        annotation_text=f"TARGET: {target_co2:,.0f}t",
        annotation_position="right",
        annotation_font=dict(color="#8a6c4a", size=12, family="Inter")
    )
    
    # Target zone
    fig.add_hrect(
        y0=0,
        y1=target_co2,
        fillcolor="rgba(74, 124, 89, 0.08)",
        line_width=0,
        annotation_text="Target Zone",
        annotation_position="bottom left",
        annotation_font=dict(color="#4A7C59", size=10)
    )
    
    fig.update_layout(
        title=dict(
            text="CO₂ Trajectory by Strategy",
            font=dict(family="Playfair Display", size=20, color="#2D2A26"),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Months",
        yaxis_title="CO₂ (tonnes/year)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#6B6560"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        xaxis=dict(
            gridcolor='#E8E4DD',
            zerolinecolor='#E8E4DD',
            tickfont=dict(color="#6B6560")
        ),
        yaxis=dict(
            gridcolor='#E8E4DD',
            zerolinecolor='#E8E4DD',
            tickfont=dict(color="#6B6560"),
            tickformat=",d"
        ),
        hovermode="x unified"
    )
    
    return fig


def create_breakdown_chart(data, title):
    """Create a donut chart with Élysia styling."""
    labels = list(data.keys())
    values = list(data.values())
    
    color_map = {
        "KEEP": "#4A7C59",
        "REFURBISHED": "#8a6c4a",
        "NEW": "#6A8CAA",
        "HIGH": "#9E4A4A",
        "MEDIUM": "#C4943A",
        "LOW": "#4A7C59"
    }
    
    colors = [color_map.get(l, "#8a6c4a") for l in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo='label+value',
        textfont=dict(size=11, family="Inter", color="#2D2A26"),
        hovertemplate="%{label}: %{value} devices<extra></extra>"
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#6B6560"),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[dict(
            text=title,
            x=0.5, y=0.5,
            font_size=14,
            font_family="Playfair Display",
            font_color="#8a6c4a",
            showarrow=False
        )]
    )
    
    return fig


def create_maisons_chart(maisons_data):
    """Create a horizontal bar chart for Maisons comparison."""
    df = pd.DataFrame(maisons_data)
    df = df.sort_values('potential_savings', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['maison'],
        x=df['potential_savings'],
        orientation='h',
        marker_color='#8a6c4a',
        text=[f"€{x/1000:.0f}K" for x in df['potential_savings']],
        textposition='outside',
        textfont=dict(family="Inter", size=11, color="#6B6560"),
        hovertemplate="<b>%{y}</b><br>Potential: €%{x:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="Savings Potential by Maison",
            font=dict(family="Playfair Display", size=18, color="#2D2A26"),
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#6B6560"),
        xaxis=dict(
            title="Annual Savings Potential (€)",
            gridcolor='#E8E4DD',
            tickformat=",d"
        ),
        yaxis=dict(title=""),
        margin=dict(l=120, r=80, t=60, b=40),
        height=400
    )
    
    return fig


# =============================================================================
# TAB 1: STRATEGY PLANNER - BUSINESS-LEVEL QUESTIONS
# =============================================================================

def render_strategy_planner():
    """Render the Strategy Planner with business-level questions."""
    
    # HERO SECTION
    st.markdown('<p class="section-header">The Opportunity</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="hero-stat">
            <div class="number">-20%</div>
            <div class="description">LIFE 360 CO₂ reduction target for IT assets by 2026</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="hero-stat">
            <div class="number">85%</div>
            <div class="description">CO₂ saved when choosing refurbished over new devices</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="hero-stat">
            <div class="number">€10M+</div>
            <div class="description">Potential stranded value in aging devices group-wide</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # BUSINESS QUESTIONS
    st.markdown('<p class="section-header">Define Your Scope</p>', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="info-box">
        <p>Answer these business-level questions. Élysia will derive the technical parameters automatically.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Question 1: Scope
    st.markdown("**1. What is your scope?**")
    
    scope_type = st.radio(
        "Select scope type",
        options=["All LVMH Group", "Selected Maisons", "Custom"],
        horizontal=True,
        key="scope_type",
        help="Choose whether to analyze the entire group or specific entities"
    )
    
    if scope_type == "Selected Maisons":
        selected_maisons = st.multiselect(
            "Select Maisons to include",
            options=list(MAISONS.keys()),
            default=["Louis Vuitton", "Sephora", "Christian Dior"],
            key="selected_maisons",
            help="Choose one or more Maisons for analysis"
        )
        # Calculate fleet from selected Maisons
        total_fleet = sum(MAISONS[m]["estimated_fleet_size"] for m in selected_maisons)
        st.markdown(f'<div class="question-hint">📊 Estimated scope: {total_fleet:,} devices across {len(selected_maisons)} Maisons</div>', unsafe_allow_html=True)
    
    elif scope_type == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            custom_employees = st.number_input(
                "Number of employees in scope",
                min_value=100,
                max_value=200000,
                value=15000,
                step=1000,
                key="custom_employees",
                help="Total employees covered by this analysis"
            )
        with col2:
            devices_per_employee = st.slider(
                "Average devices per employee",
                min_value=1.0,
                max_value=4.0,
                value=2.5,
                step=0.5,
                key="devices_per_employee",
                help="Include laptops, phones, tablets, etc."
            )
        total_fleet = int(custom_employees * devices_per_employee)
        st.markdown(f'<div class="question-hint">📊 Estimated fleet: {total_fleet:,} devices</div>', unsafe_allow_html=True)
    
    else:  # All LVMH Group
        total_fleet = sum(m["estimated_fleet_size"] for m in MAISONS.values())
        st.markdown(f'<div class="question-hint">📊 Full group scope: {total_fleet:,} estimated devices across {len(MAISONS)} Maisons</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question 2: Budget (alternative to refresh cycle)
    st.markdown("**2. What is your annual IT equipment budget?**")
    
    col1, col2 = st.columns(2)
    with col1:
        annual_budget = st.number_input(
            "Annual budget (€)",
            min_value=100000,
            max_value=100000000,
            value=5000000,
            step=500000,
            format="%d",
            key="annual_budget",
            help="Total annual spend on IT equipment procurement"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        derived_refresh = round(total_fleet * 1000 / annual_budget, 1) if annual_budget > 0 else 4
        derived_refresh = max(2, min(7, derived_refresh))  # Clamp to reasonable range
        st.markdown(f'<div class="question-hint">📊 This implies a ~{derived_refresh:.1f} year refresh cycle</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question 3: Target
    st.markdown("**3. What is your sustainability target?**")
    
    target_option = st.radio(
        "Select target",
        options=["LIFE 360 Standard (-20% by 2026)", "Ambitious (-30% by 2026)", "Custom"],
        horizontal=True,
        key="target_option",
        help="Choose your CO₂ reduction target"
    )
    
    if target_option == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            custom_reduction = st.slider(
                "Reduction target (%)",
                min_value=-50,
                max_value=-10,
                value=-25,
                key="custom_reduction"
            )
        with col2:
            custom_year = st.selectbox(
                "Target year",
                options=[2025, 2026, 2027, 2028, 2030],
                index=1,
                key="custom_year"
            )
        target_pct = custom_reduction
        target_year = custom_year
    elif target_option == "Ambitious (-30% by 2026)":
        target_pct = -30
        target_year = 2026
    else:
        target_pct = -20
        target_year = 2026
    
    # Calculate months to target
    from datetime import datetime
    current_year = datetime.now().year
    current_month = datetime.now().month
    months_remaining = (target_year - current_year) * 12 + (12 - current_month)
    
    st.markdown(f'<div class="question-hint">⏱️ {months_remaining} months remaining to reach {target_pct}% target</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question 4: Risk tolerance
    st.markdown("**4. What is your organization's approach to change?**")
    
    risk_tolerance = st.select_slider(
        "Change tolerance",
        options=["Conservative", "Balanced", "Progressive", "Aggressive"],
        value="Balanced",
        key="risk_tolerance",
        help="This affects how quickly we recommend transitioning to new practices"
    )
    
    risk_implications = {
        "Conservative": "Minimal disruption. Gradual 5-year transition. Lower savings, lower risk.",
        "Balanced": "Recommended. 3-year transition with measured steps.",
        "Progressive": "Faster adoption. 2-year transition. Higher savings potential.",
        "Aggressive": "Maximum impact. 18-month transition. Requires strong change management."
    }
    
    st.markdown(f'<div class="question-hint">💡 {risk_implications.get(risk_tolerance, "")}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question 5: Constraints
    st.markdown("**5. Do you have specific constraints?**")
    
    col1, col2 = st.columns(2)
    with col1:
        constraint_vendors = st.checkbox("Must use approved vendors only", value=True, key="constraint_vendors")
        constraint_developers = st.checkbox("Developers require new devices", value=True, key="constraint_developers")
    with col2:
        constraint_max_age = st.checkbox("Cannot extend lifecycle beyond 5 years", value=False, key="constraint_max_age")
        constraint_data_security = st.checkbox("Enhanced data security requirements", value=True, key="constraint_data_security")
    
    # SUMMARY BOX
    st.markdown(f'''
    <div class="info-box">
        <p><strong>Analysis Configuration:</strong><br>
        • Scope: {total_fleet:,} devices<br>
        • Budget: {format_currency(annual_budget)}/year<br>
        • Target: {target_pct}% CO₂ reduction by {target_year}<br>
        • Approach: {risk_tolerance}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # RUN BUTTON
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_analysis = st.button("Generate Strategy Recommendations", key="run_strategy", use_container_width=True)
    
    if run_analysis:
        with st.spinner("Analyzing optimal strategies..."):
            # Map risk tolerance to refurb rate
            risk_to_refurb = {
                "Conservative": 0.0,
                "Balanced": 0.10,
                "Progressive": 0.25,
                "Aggressive": 0.40
            }
            current_refurb = risk_to_refurb.get(risk_tolerance, 0.10)
            
            # Calculate time horizon based on target year
            time_horizon = months_remaining
            
            results = StrategySimulator.compare_strategies(
                fleet_size=total_fleet,
                current_refresh_years=int(derived_refresh),
                current_refurb_rate=current_refurb,
                target_reduction=abs(target_pct) / 100,
                time_horizon_months=min(time_horizon, 48)
            )
            
            # Estimate current CO2
            current_co2 = estimate_co2_from_fleet(total_fleet)
            
            st.session_state["strategy_results"] = results
            st.session_state["current_co2"] = current_co2
            st.session_state["total_fleet"] = total_fleet
            st.session_state["target_pct"] = target_pct
            st.session_state["annual_budget"] = annual_budget
    
    # RESULTS
    if "strategy_results" in st.session_state:
        results = st.session_state["strategy_results"]
        current_co2 = st.session_state["current_co2"]
        total_fleet = st.session_state["total_fleet"]
        target_pct = st.session_state["target_pct"]
        
        # Find best strategy
        best = None
        for r in results:
            if r.strategy_name != "Baseline" and r.months_to_target < 999:
                if best is None or r.months_to_target < best.months_to_target:
                    best = r
        
        baseline = next((r for r in results if r.strategy_name == "Baseline"), None)
        
        # IMPACT ASSESSMENT
        st.markdown('<p class="section-header">Impact Assessment</p>', unsafe_allow_html=True)
        
        # Warning if baseline fails
        if baseline and baseline.months_to_target >= 999:
            target_co2 = current_co2 * (1 + target_pct/100)
            gap = current_co2 - target_co2
            
            st.markdown(f'''
            <div class="warning-box">
                <div class="title">⚠️ Current Trajectory Misses Target</div>
                <div class="text">
                    Without intervention, your organization will not achieve the {target_pct}% CO₂ target. 
                    The projected gap of <strong>{gap:,.0f} tonnes</strong> annually represents significant 
                    exposure to sustainability commitments and stakeholder expectations.
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Before/After comparison
        if best:
            target_co2 = current_co2 * (1 + target_pct/100)
            
            col1, col2, col3 = st.columns([5, 1, 5])
            
            with col1:
                st.markdown(f'''
                <div class="comparison-box current">
                    <div class="status">Current Trajectory</div>
                    <div class="value">{current_co2:,.0f}t</div>
                    <div class="label">CO₂ emissions per year</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:2rem;color:#8a6c4a;">→</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'''
                <div class="comparison-box optimized">
                    <div class="status">With Élysia Strategy</div>
                    <div class="value">{target_co2:,.0f}t</div>
                    <div class="label">CO₂ per year ({target_pct}%)</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Winner box
            st.markdown(f'''
            <div class="winner-box">
                <div class="rank">◆ RECOMMENDED STRATEGY</div>
                <div class="name">{best.strategy_name}</div>
                <div class="metrics">
                    ✓ Reaches target in <strong>{best.months_to_target:.0f} months</strong><br>
                    ✓ Annual savings: <strong>{format_currency(best.annual_savings)}</strong><br>
                    ✓ ROI Year 1: <strong>{best.roi_year1:.1f}x</strong> · Payback: <strong>{best.payback_months:.0f} months</strong>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Success box
            st.markdown(f'''
            <div class="success-box">
                <div class="title">✓ Business Case Summary</div>
                <div class="text">
                    Implementing <strong>{best.strategy_name}</strong> across {total_fleet:,} devices requires 
                    an investment of <strong>{format_currency(best.implementation_cost)}</strong>, generating 
                    <strong>{format_currency(best.annual_savings)}</strong> in annual savings with a 
                    <strong>{best.payback_months:.0f}-month</strong> payback period.
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Strategy ranking
        st.markdown('<p class="section-header">All Strategies Compared</p>', unsafe_allow_html=True)
        
        ranking_data = []
        for i, r in enumerate(results):
            status = "✓ On Track" if r.months_to_target < 999 else "✗ Misses Target"
            months_display = f"{r.months_to_target:.0f} months" if r.months_to_target < 999 else "—"
            
            ranking_data.append({
                "Rank": i + 1,
                "Strategy": r.strategy_name,
                "Time to Target": months_display,
                "Annual Savings": format_currency(r.annual_savings),
                "ROI (Year 1)": f"{r.roi_year1:.1f}x" if r.roi_year1 > 0 else "—",
                "Status": status
            })
        
        st.dataframe(pd.DataFrame(ranking_data), use_container_width=True, hide_index=True)
        
        # Chart
        st.markdown('<p class="section-header">CO₂ Trajectory Projection</p>', unsafe_allow_html=True)
        fig = create_strategy_chart(results, target_pct, current_co2)
        st.plotly_chart(fig, use_container_width=True)
        
        # Financial summary
        if best:
            st.markdown('<p class="section-header">Financial Summary</p>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="value">{format_currency(best.implementation_cost)}</div>
                    <div class="label">Implementation Cost</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="value">{format_currency(best.annual_savings)}</div>
                    <div class="label">Annual Savings</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="value">{best.payback_months:.0f}mo</div>
                    <div class="label">Payback Period</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                three_year = best.annual_savings * 3 - best.implementation_cost
                st.markdown(f'''
                <div class="metric-card">
                    <div class="value">{format_currency(three_year)}</div>
                    <div class="label">3-Year Net Benefit</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # Methodology
        with st.expander("📋 Methodology & Data Sources"):
            st.markdown('''
            **Calculation Methodology:**
            
            | Component | Formula | Source |
            |-----------|---------|--------|
            | Fleet Size | Budget × Refresh Cycle ÷ Avg Cost | Derived from inputs |
            | Current CO₂ | Fleet × 50 kg/device/year | Industry average |
            | Manufacturing CO₂ | Device-specific LCA data | Apple, Dell, HP Reports |
            | Refurbished savings | 85% of manufacturing | Apple Environmental Report 2023 |
            | TCO | Purchase + Energy + Productivity + Disposal | Gartner Guidelines |
            
            **Key Assumptions:**
            - Average device cost: €1,000
            - Average device CO₂: 50 kg/year (amortized manufacturing + usage)
            - Refurbished price discount: 45%
            - Refurbished CO₂ reduction: 85%
            - France grid factor: 0.052 kg CO₂/kWh
            ''')


# =============================================================================
# TAB 2: MAISONS COMPARISON
# =============================================================================

def render_maisons_comparison():
    """Render the Maisons comparison leaderboard."""
    
    st.markdown('<p class="section-header">Maisons Sustainability Leaderboard</p>', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="info-box">
        <p>Compare progress toward LIFE 360 targets across LVMH Maisons. Rankings are based on estimated potential and current trajectory.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Generate Maisons data
    maisons_data = []
    for name, data in MAISONS.items():
        fleet = data["estimated_fleet_size"]
        avg_age = data["estimated_avg_age_years"]
        
        # Estimate potential savings (older fleets = more potential)
        potential_savings = fleet * 200 * (avg_age / 4)  # €200/device × age factor
        potential_co2 = fleet * 50 * 0.2  # 20% reduction potential
        
        # Score (lower age = closer to target)
        score = 100 - (avg_age - 3) * 15  # Normalize around 3 years
        score = max(0, min(100, score))
        
        maisons_data.append({
            "maison": name,
            "category": data["category"],
            "fleet_size": fleet,
            "avg_age": avg_age,
            "potential_savings": potential_savings,
            "potential_co2": potential_co2,
            "score": score
        })
    
    # Sort by score
    maisons_data = sorted(maisons_data, key=lambda x: -x["score"])
    
    # Metrics row
    total_fleet = sum(m["fleet_size"] for m in maisons_data)
    total_savings = sum(m["potential_savings"] for m in maisons_data)
    total_co2 = sum(m["potential_co2"] for m in maisons_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="value">{len(maisons_data)}</div>
            <div class="label">Maisons Analyzed</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="value">{total_fleet:,}</div>
            <div class="label">Total Devices</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="value">{format_currency(total_savings)}</div>
            <div class="label">Total Savings Potential</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="value">{total_co2/1000:.1f}t</div>
            <div class="label">CO₂ Reduction Potential</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Leaderboard table
    st.markdown('<p class="section-header">Rankings</p>', unsafe_allow_html=True)
    
    leaderboard_data = []
    for i, m in enumerate(maisons_data):
        status = "🟢" if m["score"] >= 70 else "🟡" if m["score"] >= 50 else "🔴"
        
        leaderboard_data.append({
            "Rank": i + 1,
            "Maison": m["maison"],
            "Category": m["category"],
            "Fleet Size": f"{m['fleet_size']:,}",
            "Avg Age": f"{m['avg_age']:.1f}y",
            "Savings Potential": format_currency(m["potential_savings"]),
            "Status": status
        })
    
    st.dataframe(pd.DataFrame(leaderboard_data), use_container_width=True, hide_index=True)
    
    # Chart
    st.markdown('<p class="section-header">Savings Potential by Maison</p>', unsafe_allow_html=True)
    fig = create_maisons_chart(maisons_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # Source note
    st.markdown('<p class="source-note">Data shown are illustrative estimates for demonstration purposes. Actual figures should be obtained from IT asset management systems.</p>', unsafe_allow_html=True)


# =============================================================================
# TAB 3: DATA CONNECTIONS (MOCKUP)
# =============================================================================

def render_data_connections():
    """Render the data connections/integrations page."""
    
    st.markdown('<p class="section-header">Data Sources</p>', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="info-box">
        <p>Connect your existing systems to automate data ingestion and enable real-time analysis.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Integration cards
    st.markdown("**Available Integrations**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('''
        <div class="integration-card">
            <div class="icon">🔧</div>
            <div class="name">ServiceNow</div>
            <div class="status">Available</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Connect", key="connect_servicenow"):
            st.info("ServiceNow integration coming soon")
    
    with col2:
        st.markdown('''
        <div class="integration-card">
            <div class="icon">☁️</div>
            <div class="name">Microsoft Intune</div>
            <div class="status">Available</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Connect", key="connect_intune"):
            st.info("Intune integration coming soon")
    
    with col3:
        st.markdown('''
        <div class="integration-card">
            <div class="icon">📊</div>
            <div class="name">SAP</div>
            <div class="status">Available</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Connect", key="connect_sap"):
            st.info("SAP integration coming soon")
    
    with col4:
        st.markdown('''
        <div class="integration-card disabled">
            <div class="icon">📁</div>
            <div class="name">CSV Upload</div>
            <div class="status">Active</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Manual upload section
    st.markdown('<p class="section-header">Manual Data Upload</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload fleet inventory (CSV)",
            type=["csv"],
            key="fleet_upload",
            help="Required columns: Device_Model, Age_Years, Persona, Country"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Demo data button
        if st.button("📊 Use Demo Data", key="load_demo", use_container_width=True):
            demo_fleet = generate_demo_fleet(100)
            st.session_state["fleet_df"] = pd.DataFrame(demo_fleet)
            st.success("✓ Demo data loaded (100 devices)")
        
        # Template download
        template_df = pd.DataFrame({
            "Device_Model": ["Laptop (Standard)", "iPhone SE (Legacy)", "Tablet"],
            "Age_Years": [3, 4, 2],
            "Persona": ["Admin Normal (HR/Finance)", "Vendor (Phone/Tablet)", "Admin Normal (HR/Finance)"],
            "Country": ["FR", "US", "FR"],
            "Maison": ["Louis Vuitton", "Sephora", "Christian Dior"]
        })
        
        csv_template = template_df.to_csv(index=False)
        st.download_button(
            "📥 Download Template",
            csv_template,
            "elysia_template.csv",
            "text/csv",
            key="download_template",
            use_container_width=True
        )
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate columns
            required_cols = ["Device_Model", "Age_Years"]
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                st.info("Please ensure your CSV has: Device_Model, Age_Years, Persona (optional), Country (optional)")
            else:
                st.session_state["fleet_df"] = df
                st.success(f"✓ Loaded {len(df)} devices")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Show fleet analysis if data loaded
    if "fleet_df" in st.session_state:
        df = st.session_state["fleet_df"]
        
        st.markdown('<p class="section-header">Fleet Analysis</p>', unsafe_allow_html=True)
        
        with st.spinner("Analyzing fleet..."):
            fleet_data = df.to_dict('records')
            analyses = FleetAnalyzer.analyze_fleet(fleet_data, optimization_goal="balanced")
            summary = FleetAnalyzer.summarize_fleet(analyses)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="value">{summary["total_devices"]:,}</div>
                <div class="label">Devices Analyzed</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <div class="value">{format_currency(summary["total_annual_savings_eur"])}</div>
                <div class="label">Annual Savings</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
            <div class="metric-card">
                <div class="value">{format_co2(summary["total_co2_savings_kg"])}</div>
                <div class="label">CO₂ Savings</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'''
            <div class="metric-card">
                <div class="value">{format_currency(summary["total_recoverable_value_eur"])}</div>
                <div class="label">Recoverable Value</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_reco = create_breakdown_chart(summary["by_recommendation"], "By Action")
            st.plotly_chart(fig_reco, use_container_width=True)
        
        with col2:
            fig_urgency = create_breakdown_chart(summary["by_urgency"], "By Priority")
            st.plotly_chart(fig_urgency, use_container_width=True)
        
        # Priority actions table
        st.markdown('<p class="section-header">Priority Actions</p>', unsafe_allow_html=True)
        
        urgency_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_analyses = sorted(analyses, key=lambda x: (urgency_order.get(x.urgency, 2), -x.annual_savings))
        
        display_data = []
        for a in sorted_analyses[:15]:
            display_data.append({
                "Device": a.device_name,
                "Age": f"{a.age_years}y",
                "Profile": a.persona,
                "Action": a.recommendation,
                "Priority": a.urgency,
                "Savings": f"€{a.annual_savings:.0f}/yr"
            })
        
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
        
        # Export
        export_data = [{"Device": a.device_name, "Age": a.age_years, "Recommendation": a.recommendation, 
                        "Urgency": a.urgency, "Annual_Savings": a.annual_savings} for a in analyses]
        csv_export = pd.DataFrame(export_data).to_csv(index=False)
        
        st.download_button(
            "📥 Export Action Plan",
            csv_export,
            "elysia_action_plan.csv",
            "text/csv",
            key="export_plan"
        )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def run():
    # Inject CSS
    st.markdown(ELYSIA_CSS, unsafe_allow_html=True)
    
    # Check modules
    if not MODULES_LOADED:
        st.error(f"Module import error: {IMPORT_ERROR}")
        st.info("Ensure reference_data_API.py and calculator.py are in the same directory.")
        st.stop()
    
    # Header with logo
    logo_html = ""
    if ELYSIA_LOGO_BASE64:
        logo_html = f'<img src="data:image/png;base64,{ELYSIA_LOGO_BASE64}" class="elysia-logo-icon" alt="Élysia">'
    else:
        # Fallback text if logo not found
        logo_html = '<span style="font-family: Playfair Display; font-size: 3rem; color: #8a6c4a;">É</span>'
    
    st.markdown(f'''
    <div class="elysia-header">
        <div class="elysia-logo">
            {logo_html}
            <span class="elysia-logo-text">lysia</span>
        </div>
        <div class="elysia-subtitle">LVMH · Sustainable IT Intelligence</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["◆ STRATEGY PLANNER", "◆ MAISONS COMPARISON", "◆ DATA & INTEGRATIONS"])
    
    with tab1:
        render_strategy_planner()
    
    with tab2:
        render_maisons_comparison()
    
    with tab3:
        render_data_connections()
    
    # Footer
    st.markdown('''
    <div style="text-align:center;margin-top:4rem;padding:1.5rem;border-top:1px solid #E8E4DD;">
        <span style="font-family:Inter;font-size:0.7rem;color:#9A958E;letter-spacing:0.1em;">
            ÉLYSIA · LVMH GREEN IT · LIFE 360
        </span>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    run()