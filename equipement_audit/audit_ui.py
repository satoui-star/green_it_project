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
from pathlib import Path

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

from pathlib import Path

def _load_brand_assets():
    """
    Returns dict with optional 'logo' and 'icon' absolute paths if files exist.
    Never crashes if assets are missing.
    """
    project_root = Path(__file__).resolve().parents[1]  # /workspaces/green_it_project showing equipement_audit/
    logo_dir = project_root / "logo.png"

    logo_path = logo_dir / "elysia_logo.png"
    icon_path = logo_dir / "elysia_icon.png"

    return {
        "logo": str(logo_path) if logo_path.exists() else None,
        "icon": str(icon_path) if icon_path.exists() else None,
    }

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


/* Welcome hero */
.welcome-hero{
  max-width: 860px;
  margin: 6vh auto 0 auto;
  padding: 2.75rem 1.5rem 2.25rem 1.5rem;
  text-align: center;
}
.welcome-logo img{
  height: 44px;
  width: auto;
  display: inline-block;
}
.welcome-logo-text{
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  letter-spacing: .02em;
  color: var(--forest);
  margin-bottom: .25rem;
}
.welcome-tagline{
  font-size: .95rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: .6rem;
}
.welcome-value{
  margin-top: 1.35rem;
  font-size: 1.05rem;
  color: #4b4744;
  line-height: 1.55;
}


/* Action navigation */
.action-nav-wrap{margin-top:.25rem;margin-bottom:1.25rem;}
.action-nav-sub{margin-top:.35rem;text-align:center;color:var(--muted);font-size:.95rem;}

/* KPI cards */
.kpi-card{background:#fff;border:1px solid rgba(74,124,89,.12);border-radius:18px;padding:1rem 1.1rem;text-align:center;box-shadow:0 10px 26px rgba(0,0,0,.06);}
.kpi-value{font-family:'Playfair Display',serif;font-size:1.75rem;color:var(--forest);}
.kpi-label{margin-top:.25rem;color:var(--muted);font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;}

.strategy-title{font-family:'Playfair Display',serif;font-size:1.65rem;color:var(--forest);text-align:center;margin-top:.75rem;}
.strategy-desc{text-align:center;color:#5f5a56;margin:.25rem auto 1rem auto;max-width:860px;}

.what-means{margin-top:1rem;background:rgba(138,108,74,.07);border:1px solid rgba(138,108,74,.18);border-radius:16px;padding:1rem 1.1rem;}
.what-means-title{font-weight:700;color:#3f3b38;margin-bottom:.25rem;}
.what-means-text{color:#4b4744;}

.assumptions{margin-top:.85rem;color:var(--muted);font-size:.92rem;text-align:center;}
.assumptions-title{color:#3f3b38;font-weight:700;}

.step-why{color:var(--muted);margin-top:-.5rem;margin-bottom:1rem;text-align:center;}
.mini-box{background:#fff;border:1px dashed rgba(74,124,89,.25);border-radius:14px;padding:.85rem 1rem;color:#555;}

/* Scenario cards */
.scenario-card{background:#fff;border:1px solid rgba(138,108,74,.18);border-radius:18px;padding:1rem 1.05rem;box-shadow:0 10px 26px rgba(0,0,0,.06);}
.scenario-card.selected{border:2px solid rgba(138,108,74,.75);}
.scenario-card.empty{height:160px;display:flex;align-items:center;justify-content:center;color:var(--muted);}
.scenario-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:.55rem;}
.scenario-pill{display:inline-block;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;padding:.28rem .55rem;border-radius:999px;background:rgba(74,124,89,.10);color:var(--forest);}
.scenario-risk{font-size:.78rem;color:var(--muted);}
.scenario-name{font-weight:800;color:#3f3b38;line-height:1.25;margin-bottom:.35rem;}
.scenario-metrics{color:#5f5a56;font-size:.9rem;}
.scenario-why{margin-top:.55rem;color:var(--muted);font-size:.85rem;}
.compare-explain{margin-top:.75rem;margin-bottom:1rem;text-align:center;color:#5f5a56;}

/* Simulator */
.sim-rec{margin-top:1rem;background:rgba(74,124,89,.08);border:1px solid rgba(74,124,89,.18);border-radius:16px;padding:1rem 1.05rem;text-align:center;color:#3f3b38;}
.sim-rationale{text-align:center;color:var(--muted);margin-top:.45rem;margin-bottom:.6rem;}

/* Plan */
.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:.5rem;margin-bottom:1.25rem;}
.plan-card{background:#fff;border:1px solid rgba(138,108,74,.18);border-radius:18px;padding:1rem 1.1rem;box-shadow:0 10px 26px rgba(0,0,0,.06);}
.plan-title{font-weight:900;color:#3f3b38;margin-bottom:.55rem;}
@media (max-width: 900px){.plan-grid{grid-template-columns:1fr;}}

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
    """Step 0: Welcome (hero centered)."""

    assets = _load_brand_assets()

    # Centered hero layout
    st.markdown("<div class='welcome-hero'>", unsafe_allow_html=True)

    if assets.get("logo"):
        st.markdown(f"<div class='welcome-logo'><img src='{assets['logo']}' alt='ÉLYSIA' /></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='welcome-logo-text'>ÉLYSIA</div>", unsafe_allow_html=True)

    st.markdown("<div class='welcome-tagline'>Sustainable IT strategy · Evidence-backed</div>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-value'>Measure the impact of your refresh policy and turn it into an execution-ready plan.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start →", key="btn_start", use_container_width=True):
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

    geo_options = ["— Select —"] + [v["name"] for v in GRID_CARBON_FACTORS.values()]
    geo_map = {v["name"]: code for code, v in GRID_CARBON_FACTORS.items()}
    geo_choice = st.selectbox(
    "Geography",
    options=geo_options,
    key="act0_geo_choice",
    label_visibility="collapsed",
)

    geo_code = geo_map.get(geo_choice, None)  # "FR", "DE", ...
    st.session_state["geo_code"] = geo_code

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
# ACT 4: ACTION (GUIDED EXPERIENCE — NO BUSINESS MATH IN UI)
# =============================================================================

ACTION_STEPS = [
    ("strategy", "Your Strategy", "Outcome"),
    ("compare", "Compare Options", "Choose scenario"),
    ("upload", "Upload Data", "Validate with your fleet"),
    ("simulator", "Device Simulator", "Stress-test decisions"),
    ("plan", "Action Plan", "Execution blueprint"),
]


def _action_step_index(key: str) -> int:
    for i, (k, _, _) in enumerate(ACTION_STEPS):
        if k == key:
            return i
    return 0


def _set_action_step(key: str) -> None:
    st.session_state["action_view"] = key
    st.rerun()


def _get_strategy_inputs() -> Dict[str, any]:
    """Collect inputs for the calculator engine (no computation here)."""
    return {
        "fleet_size": int(st.session_state.get("fleet_size", 12500)),
        "refresh_cycle": float(st.session_state.get("refresh_cycle", 4)),
        "avg_age": float(st.session_state.get("avg_age", 3.5)),
        "target_pct": int(st.session_state.get("target_pct", -20)),
        "priority": str(st.session_state.get("priority", "cost")),
        "geo": str(st.session_state.get("geo", "FR")),
        "current_refurb_pct": int(st.session_state.get("current_refurb_pct", 0)),
    }


def _compute_strategies() -> Dict[str, any]:
    """Compute strategies through calculator engine; cache in session."""
    inp = _get_strategy_inputs()

    cache_key = (
        inp["fleet_size"], inp["refresh_cycle"], inp["avg_age"], inp["target_pct"],
        inp["priority"], inp["geo"], inp["current_refurb_pct"],
        bool(st.session_state.get("fleet_data") is not None),
    )

    if st.session_state.get("_strategy_cache_key") == cache_key and st.session_state.get("_strategy_cache"):
        return st.session_state["_strategy_cache"]

    results_all = StrategySimulator.compare_all_strategies(
        fleet_size=inp["fleet_size"],
        current_refresh=inp["refresh_cycle"],
        avg_age=inp["avg_age"],
        target_pct=inp["target_pct"],
    )

    recommended = RecommendationEngine.pick(results_all, priority=inp["priority"]) if results_all else None

    # BEST = maximize CO2 impact (engine optional)
    best = None
    try:
        best = RecommendationEngine.best_case(results_all)  # type: ignore
    except Exception:
        pass
    if best is None and results_all:
        candidates = [r for r in results_all if getattr(r, "strategy_key", "") != "do_nothing"] or results_all
        best = min(candidates, key=lambda r: float(getattr(r, "co2_reduction_pct", 0.0)))

    do_nothing = None
    try:
        do_nothing = RecommendationEngine.do_nothing(results_all)  # type: ignore
    except Exception:
        pass
    if do_nothing is None and results_all:
        do_nothing = next((r for r in results_all if getattr(r, "strategy_key", "") == "do_nothing"), None)

    pack = {
        "inputs": inp,
        "results_all": results_all,
        "recommended": recommended,
        "best": best,
        "do_nothing": do_nothing,
    }

    st.session_state["_strategy_cache_key"] = cache_key
    st.session_state["_strategy_cache"] = pack
    return pack


def _risk_label(r: Optional[StrategyResult]) -> str:
    if not r:
        return "—"
    # Prefer engine-provided risk if available
    details = getattr(r, "calculation_details", {}) or {}
    if isinstance(details, dict) and details.get("risk_level"):
        return str(details["risk_level"])

    # Lightweight fallback based on refurb rate (kept simple)
    rr = None
    try:
        rr = float(details.get("refurb_rate"))
    except Exception:
        rr = None

    if rr is None:
        return "Medium"
    if rr >= 0.55:
        return "High"
    if rr >= 0.30:
        return "Medium"
    return "Low"


def _confidence_level() -> str:
    return "High" if st.session_state.get("fleet_data") is not None else "Medium"


def _render_action_nav(current_key: str) -> None:
    st.markdown("<div class='action-nav-wrap'>", unsafe_allow_html=True)
    labels = [f"{title}" for _, title, _ in ACTION_STEPS]
    keys = [k for k, _, _ in ACTION_STEPS]
    idx = _action_step_index(current_key)

    choice = st.radio(
        "",
        options=keys,
        index=idx,
        format_func=lambda k: dict((a, b) for a, b, _ in ACTION_STEPS).get(k, k),
        horizontal=True,
        key="action_view_radio",
        label_visibility="collapsed",
    )

    st.session_state["action_view"] = choice

    # Subtitle
    subtitle = dict((k, sub) for k, _, sub in ACTION_STEPS).get(choice, "")
    st.markdown(f"<div class='action-nav-sub'>{subtitle}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_outcome_kpis(r: StrategyResult) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{abs(float(r.co2_reduction_pct)):.0f}%</div><div class='kpi-label'>CO₂ reduction</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{fmt_currency(getattr(r, 'annual_savings_eur', 0.0))}</div><div class='kpi-label'>annual savings</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{int(getattr(r, 'time_to_target_months', 0))} mo</div><div class='kpi-label'>time to target</div></div>", unsafe_allow_html=True)


def _render_strategy_screen() -> None:
    pack = _compute_strategies()
    rec = pack.get("recommended")
    inp = pack.get("inputs", {})

    st.markdown("### Recommended strategy")

    if not rec:
        st.warning("No strategy result available. Please check your inputs.")
        return

    # Confidence
    render_confidence_badge(_confidence_level(), "Confidence", "Based on available evidence.")

    st.markdown(f"<div class='strategy-title'>{rec.strategy_name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='strategy-desc'>{rec.description}</div>", unsafe_allow_html=True)

    _render_outcome_kpis(rec)

    # What this means
    msg = "This recommendation balances impact and feasibility under your current inputs."
    if getattr(rec, "reaches_target", False):
        msg = "This recommendation reaches your target under your current inputs with the best trade-off for your priority."
    st.markdown(f"<div class='what-means'><div class='what-means-title'>What this means</div><div class='what-means-text'>{msg}</div></div>", unsafe_allow_html=True)

    # Assumptions used (short, factual)
    geo = inp.get("geo", "—")
    st.markdown(
        f"<div class='assumptions'><span class='assumptions-title'>Assumptions used:</span> refresh cycle {inp.get('refresh_cycle')}y · average age {inp.get('avg_age')}y · geography {geo}</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Continue → Compare options", use_container_width=True, key="cta_to_compare"):
            _set_action_step("compare")
    with col2:
        if st.button("Upload fleet data (increase confidence)", use_container_width=True, key="cta_to_upload"):
            _set_action_step("upload")


def _render_compare_screen() -> None:
    pack = _compute_strategies()
    inp = pack.get("inputs", {})
    results_all: List[StrategyResult] = pack.get("results_all") or []

    st.markdown("### Compare options")
    st.markdown("<div class='step-why'>Why this step exists: make the recommendation understandable and selectable.</div>", unsafe_allow_html=True)

    # Controls
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        risk_appetite = st.selectbox(
            "Risk appetite",
            options=["Conservative", "Balanced", "Aggressive"],
            index=1,
            key="risk_appetite",
        )
    with col_b:
        st.caption("Constraints summary")
        st.markdown(f"<div class='mini-box'>Refresh {inp.get('refresh_cycle')}y · Avg age {inp.get('avg_age')}y · Geo {inp.get('geo')}</div>", unsafe_allow_html=True)
    with col_c:
        if st.button("Recompute", use_container_width=True, key="btn_recompute"):
            st.session_state.pop("_strategy_cache_key", None)
            st.session_state.pop("_strategy_cache", None)
            st.rerun()

    # Select strategies
    recommended = pack.get("recommended")
    best = pack.get("best")
    do_nothing = pack.get("do_nothing")

    st.markdown("<div class='compare-explain'><b>Best case</b> maximizes impact. <b>Recommended</b> maximizes feasibility under your inputs.</div>", unsafe_allow_html=True)

    cards = [
        ("BEST", best),
        ("RECOMMENDED", recommended),
        ("DO NOTHING", do_nothing),
    ]

    cols = st.columns(3)
    for (label, r), col in zip(cards, cols):
        with col:
            if not r:
                st.markdown("<div class='scenario-card empty'>—</div>", unsafe_allow_html=True)
                continue

            is_selected = st.session_state.get("selected_strategy_key") == r.strategy_key
            card_cls = "scenario-card selected" if is_selected else "scenario-card"

            st.markdown(f"<div class='{card_cls}'>", unsafe_allow_html=True)
            st.markdown(f"<div class='scenario-top'><span class='scenario-pill'>{label}</span><span class='scenario-risk'>{_risk_label(r)} risk</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='scenario-name'>{r.strategy_name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='scenario-metrics'>CO₂: <b>{abs(float(r.co2_reduction_pct)):.0f}%</b> · Savings: <b>{fmt_currency(getattr(r,'annual_savings_eur',0.0))}</b> · Time: <b>{int(getattr(r,'time_to_target_months',0))} mo</b></div>", unsafe_allow_html=True)

            # Micro 'why'
            if label == "BEST" and recommended and best and recommended.strategy_key != best.strategy_key:
                st.markdown("<div class='scenario-why'>Why: higher impact, but higher execution dependency.</div>", unsafe_allow_html=True)
            elif label == "RECOMMENDED":
                st.markdown("<div class='scenario-why'>Why: best trade-off for your priority and constraints.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='scenario-why'>Why: stable baseline, no change management.</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Select", key=f"select_{r.strategy_key}", use_container_width=True):
                st.session_state["selected_strategy_key"] = r.strategy_key
                st.success("Selected")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", use_container_width=True, key="compare_back"):
            _set_action_step("strategy")
    with col2:
        if st.button("Continue → Upload data", use_container_width=True, key="compare_next"):
            _set_action_step("upload")


def _render_upload_screen() -> None:
    st.markdown("### Upload fleet data")
    st.markdown("<div class='step-why'>Why this step exists: turn estimates into CFO-ready evidence and raise confidence.</div>", unsafe_allow_html=True)

    template_csv = "Device_Model,Age_Years,Persona,Country\nMacBook Pro 14,3.2,Office,FR\n"

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "Download CSV template",
            data=template_csv.encode("utf-8"),
            file_name="elysia_fleet_template.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        if st.button("Load demo data", use_container_width=True, key="load_demo"):
            st.session_state["fleet_data"] = generate_demo_fleet(n=250)
            st.success("Demo fleet loaded")
            st.session_state.pop("_strategy_cache_key", None)
            st.session_state.pop("_strategy_cache", None)
            st.rerun()

    uploaded = st.file_uploader(
        "Upload fleet CSV",
        type=["csv"],
        key="fleet_uploader",
        help="Required: Device_Model, Age_Years. Optional: Persona, Country",
    )

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            ok, msgs, norm = validate_fleet_data(df)
            if not ok:
                st.error("CSV validation failed")
                for m in msgs:
                    st.caption(f"• {m}")
            else:
                st.session_state["fleet_data"] = norm
                st.success("Fleet data loaded")
                st.session_state.pop("_strategy_cache_key", None)
                st.session_state.pop("_strategy_cache", None)
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

    df = st.session_state.get("fleet_data")
    if isinstance(df, pd.DataFrame) and len(df) > 0:
        profile = FleetAnalyzer.analyze(df, refresh_cycle=float(st.session_state.get("refresh_cycle", 4)))
        if profile.get("ok"):
            st.markdown("#### Executive summary")
            render_confidence_badge("High", "Confidence", "Measured fleet data provided.")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Fleet size", f"{profile.get('fleet_size', 0):,}")
            with c2:
                st.metric("Average age", f"{profile.get('avg_age', 0):.1f} y")
            with c3:
                st.metric("Annual replacements", f"{profile.get('annual_replacements', 0):,}")

            st.markdown("<div class='mini-box'>Your strategy will now use measured fleet age for the next steps.</div>", unsafe_allow_html=True)
            st.session_state["avg_age"] = float(profile.get("avg_age", st.session_state.get("avg_age", 3.5)))
        else:
            st.warning("Fleet data loaded but could not be analyzed.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", use_container_width=True, key="upload_back"):
            _set_action_step("compare")
    with col2:
        if st.button("Continue → Device simulator", use_container_width=True, key="upload_next"):
            _set_action_step("simulator")


def _render_simulator_screen() -> None:
    st.markdown("### Device simulator")
    st.markdown("<div class='step-why'>Why this step exists: stress-test device decisions against your strategy.</div>", unsafe_allow_html=True)

    # Inputs
    device_models = list(DEVICES.keys()) if isinstance(DEVICES, dict) and DEVICES else []
    if not device_models:
        st.warning("No device catalog available.")
        return

    countries = get_country_codes()
    available_codes = [c for c in countries.keys() if c in GRID_CARBON_FACTORS]
    available_codes = sorted(available_codes, key=lambda c: countries.get(c, c))

    col1, col2 = st.columns([1, 1])
    with col1:
        model = st.selectbox("Device model", options=device_models, key="sim_model")
        age = st.slider("Current age (years)", min_value=0.0, max_value=8.0, value=3.0, step=0.1, key="sim_age")
        persona = st.selectbox("Persona", options=list(PERSONAS.keys()), key="sim_persona")
    with col2:
        country = st.selectbox("Location", options=available_codes, format_func=lambda c: f"{countries.get(c,c)} ({c})", key="sim_country")
        objective = st.selectbox("Objective", options=["Cost", "CO2", "Balanced"], key="sim_objective")
        criticality = st.selectbox("Criticality", options=["Low", "Medium", "High"], index=1, key="sim_criticality")

    if st.button("Run simulation", use_container_width=True, key="sim_run"):
        try:
            from calculator import recommend_device  # Optional helper (preferred)
            rec: DeviceRecommendation = recommend_device(
                device_model=model,
                age_years=float(age),
                persona=str(persona),
                country=str(country),
                objective=str(objective).lower(),
                criticality=str(criticality).lower(),
            )

            st.markdown(f"<div class='sim-rec'>Recommendation: <b>{rec.recommendation}</b></div>", unsafe_allow_html=True)
            if rec.rationale:
                st.markdown(f"<div class='sim-rationale'>{rec.rationale}</div>", unsafe_allow_html=True)

            # Comparison table (provided by engine if available)
            if rec.options:
                df = pd.DataFrame(rec.options)
                st.dataframe(df, use_container_width=True, hide_index=True)

        except Exception:
            st.warning("Device recommendation helper not found in calculator. Add a `recommend_device(...)` function in calculator to keep business logic out of the UI.")

    st.markdown("<div class='mini-box'>These device-level choices can shift lifecycle policy and update strategy assumptions.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", use_container_width=True, key="sim_back"):
            _set_action_step("upload")
    with col2:
        if st.button("Continue → Action plan", use_container_width=True, key="sim_next"):
            _set_action_step("plan")


def _render_plan_screen() -> None:
    st.markdown("### Action plan")
    st.markdown("<div class='step-why'>Why this step exists: convert the strategy into concrete deliverables and governance.</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='plan-grid'>
      <div class='plan-card'>
        <div class='plan-title'>0–30 days</div>
        <ul>
          <li>Confirm scope, owners, and procurement constraints</li>
          <li>Lock refresh policy and approved categories</li>
          <li>Define reporting cadence and KPI owner</li>
        </ul>
      </div>
      <div class='plan-card'>
        <div class='plan-title'>31–60 days</div>
        <ul>
          <li>Run pilot on 1–2 categories</li>
          <li>Validate supplier capacity + QA process</li>
          <li>Track first savings and CO₂ impact</li>
        </ul>
      </div>
      <div class='plan-card'>
        <div class='plan-title'>61–90 days</div>
        <ul>
          <li>Scale to priority categories</li>
          <li>Finalize governance and audit trail</li>
          <li>Prepare executive update (CFO/CSO)</li>
        </ul>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Exports")
    pack = _compute_strategies()
    results_all = pack.get("results_all") or []

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        try:
            md = generate_markdown_report(results_all)
            st.download_button(
                "Download Strategy Pack (MD)",
                data=md,
                file_name="elysia_strategy_pack.md",
                mime="text/markdown",
                use_container_width=True,
            )
        except Exception:
            st.download_button(
                "Download Strategy Pack (MD)",
                data="Strategy pack not available.",
                file_name="elysia_strategy_pack.md",
                mime="text/markdown",
                use_container_width=True,
            )
    with col2:
        try:
            csvb = export_recommendations_to_csv(results_all)
            st.download_button(
                "Download Strategies (CSV)",
                data=csvb,
                file_name="elysia_strategies.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception:
            pass
    with col3:
        if st.button("Start new analysis", use_container_width=True, key="reset_all"):
            for k in list(st.session_state.keys()):
                if k not in ("session_id", "session_started_at"):
                    st.session_state.pop(k, None)
            st.session_state["stage"] = "opening"
            st.rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", use_container_width=True, key="plan_back"):
            _set_action_step("simulator")
    with col2:
        st.empty()


def render_action():
    """Act 4: Guided Strategy experience."""
    render_header()
    render_progress_bar(4)
    render_act_badge(4, "YOUR STRATEGY")

    if "action_view" not in st.session_state:
        st.session_state["action_view"] = "strategy"

    current = st.session_state.get("action_view", "strategy")

    # Navigation
    _render_action_nav(current)

    # Content
    if current == "strategy":
        _render_strategy_screen()
    elif current == "compare":
        _render_compare_screen()
    elif current == "upload":
        _render_upload_screen()
    elif current == "simulator":
        _render_simulator_screen()
    elif current == "plan":
        _render_plan_screen()
    else:
        st.session_state["action_view"] = "strategy"
        st.rerun()

def render_audit_section():
    # Default stage
    if "stage" not in st.session_state:
        st.session_state["stage"] = "opening"

    stage = st.session_state["stage"]

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
        # fallback safety
        st.session_state["stage"] = "opening"
        render_opening()


def run():
    render_audit_section()
