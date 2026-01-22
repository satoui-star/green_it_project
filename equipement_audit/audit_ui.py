"""
Élysia - audit_ui_part1.py
Steps 0-4: Welcome, Calibration, Shock, Hope, Strategy
+ Shared CSS, helpers, state management
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import uuid
import base64
import os
from datetime import datetime

# =============================================================================
# BACKEND IMPORTS
# =============================================================================

_BACKEND_READY = True
_IMPORT_ERROR = None
_EXTENSIONS_READY = True

try:
    from credibility_ui import inject_credibility_css, show_general_disclaimer, show_stranded_value_disclaimer, render_methodology_tab
    _CREDIBILITY_AVAILABLE = True
except ImportError:
    _CREDIBILITY_AVAILABLE = False
    def inject_credibility_css(): pass
    def show_general_disclaimer(): st.caption("*Estimates based on industry benchmarks*")
    def show_stranded_value_disclaimer(): st.caption("*Stranded value is theoretical - see methodology*")
    def render_methodology_tab(): st.info("Methodology documentation not available")

from calculator import SimpleROICalculator, SimpleROI

try:
    from reference_data_API import (
        PERSONAS, DEVICES, STRATEGIES, AVERAGES,
        FLEET_SIZE_OPTIONS, FLEET_AGE_OPTIONS, GRID_CARBON_FACTORS,
        get_device_names, get_persona_names, get_country_codes, get_all_sources
    )
except ImportError as e:
    _BACKEND_READY = False
    _IMPORT_ERROR = str(e)
    FLEET_SIZE_OPTIONS = {
        "small": {"label": "Small", "description": "< 5,000 devices", "estimate": 3000},
        "medium": {"label": "Medium", "description": "5,000 - 20,000 devices", "estimate": 12500},
        "large": {"label": "Large", "description": "20,000 - 50,000 devices", "estimate": 35000},
        "enterprise": {"label": "Enterprise", "description": "> 50,000 devices", "estimate": 75000},
    }
    FLEET_AGE_OPTIONS = {"young": {"label": "Young", "estimate": 1.5}, "mature": {"label": "Mature", "estimate": 3.0}, "aging": {"label": "Aging", "estimate": 4.5}, "legacy": {"label": "Legacy", "estimate": 6.0}}
    GRID_CARBON_FACTORS = {"FR": {"factor": 0.052, "name": "France"}, "DE": {"factor": 0.385, "name": "Germany"}, "GB": {"factor": 0.268, "name": "United Kingdom"}, "US": {"factor": 0.410, "name": "United States"}, "IT": {"factor": 0.371, "name": "Italy"}, "ES": {"factor": 0.185, "name": "Spain"}, "CH": {"factor": 0.035, "name": "Switzerland"}}
    STRATEGIES, DEVICES, PERSONAS = {}, {}, {}
    AVERAGES = {"device_price_eur": 1150, "device_co2_manufacturing_kg": 365}
    def get_country_codes(): return {k: v.get("name", k) for k, v in GRID_CARBON_FACTORS.items()}
    def get_all_sources(): return {}

try:
    from calculator import (ShockCalculator, HopeCalculator, StrategySimulator, validate_fleet_data, generate_demo_fleet, FleetAnalyzer, StrategyResult)
except ImportError as e:
    _BACKEND_READY = False
    _IMPORT_ERROR = f"{_IMPORT_ERROR}; calculator: {e}" if _IMPORT_ERROR else f"calculator: {e}"

try:
    from calculator import (RiskBasedSelector, FleetInsightsGenerator, PolicyImpactCalculator, ActionPlanGenerator, DeviceCategoryExtractor, generate_fleet_template, generate_demo_fleet_extended, DevicePolicy, FleetInsightsResult, PolicyImpactResult, ActionPlanResult, RiskStrategySet, CategoryInfo, InsightWithProof)
    _EXTENSIONS_READY = True
except ImportError:
    _EXTENSIONS_READY = False
    def generate_fleet_template(): return "Device_Model,Age_Years,Persona,Country\nMacBook Pro 14,2.5,Developer (Tech),FR"
    def generate_demo_fleet_extended(n): return pd.DataFrame(generate_demo_fleet(n)) if _BACKEND_READY else pd.DataFrame()

try:
    from audit_logger import audit_log
except ImportError:
    def audit_log(*args, **kwargs): pass


# Additional imports
try:
    from credibility_ui import inject_credibility_css, render_methodology_tab
except ImportError:
    def inject_credibility_css(): pass
    def render_methodology_tab(): st.info("Methodology documentation not available")


try:
    from calculator import (
        StrategySimulator, StrategyResult,
        RiskBasedSelector, FleetInsightsGenerator, ActionPlanGenerator,
        DeviceCategoryExtractor, generate_fleet_template, generate_demo_fleet_extended,
        DevicePolicy,
    )
except ImportError:
    def generate_fleet_template(): return "Device_Model,Age_Years,Persona,Country\nMacBook Pro 14,2.5,Developer (Tech),FR"
    def generate_demo_fleet_extended(n): return pd.DataFrame()


# =============================================================================
# WIDGET KEY MANAGEMENT
# =============================================================================

def ui_key(step: str, name: str) -> str:
    audit = st.session_state.get("audit", {})
    session_id = audit.get("session_id", "default")[:8]
    return f"{step}_{name}_{session_id}"


# =============================================================================
# SESSION STATE
# =============================================================================

def _get_audit_state() -> Dict[str, Any]:
    if "audit" not in st.session_state:
        st.session_state["audit"] = _create_default_state()
    return st.session_state["audit"]

def _create_default_state() -> Dict[str, Any]:
    return {
        "session_id": str(uuid.uuid4()),
        "stage": "welcome",
        "fleet_size": 12500,
        "refresh_cycle": 4,
        "geo_code": "FR",
        "current_refurb_pct": 0.0,
        "target_pct": -20,
        "avg_age": 3.5,
        "shock_result": None,
        "hope_result": None,
        "risk_appetite": "balanced",
        "all_strategies": None,
        "strategy_set": None,
        "selected_strategy_key": None,
        "selected_strategy": None,
        "fleet_data": None,
        "fleet_insights": None,
        "data_source": "estimates",
        "confidence": "MEDIUM",
        "device_categories": None,
        "device_policies": None,
        "policy_impact": None,
        "action_plan": None,
    }

def _s(key: str, default: Any = None) -> Any:
    return _get_audit_state().get(key, default)

def _update(updates: Dict[str, Any]) -> None:
    state = _get_audit_state()
    for key, value in updates.items():
        state[key] = value

def _reset_state() -> None:
    st.session_state["audit"] = _create_default_state()

def safe_goto(stage: str) -> None:
    _update({"stage": stage})
    st.rerun()

def _sanity_check_backend() -> Tuple[bool, List[str]]:
    errors = []
    if not _BACKEND_READY:
        errors.append(f"Backend import failed: {_IMPORT_ERROR}")
    return len(errors) == 0, errors


# =============================================================================
# LOGO - ONLY ICON
# =============================================================================

def _get_logo_base64(logo_path: str) -> Optional[str]:
    for path in [logo_path, "logo.png/elysia_logo.png", "logo.png/elysia_icon.png", "elysia_logo.png", "logo.png", "/workspaces/green_it_project/logo.png/elysia_logo.png"]:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                continue
    return None

def _get_logo_html(size: str = "medium") -> str:
    sizes = {"small": "48px", "medium": "80px", "large": "100px", "hero": "140px"}
    icon_size = sizes.get(size, sizes["medium"])
    logo_b64 = _get_logo_base64("logo.png/elysia_logo.png")
    if logo_b64:
        return f'<div style="display:flex; align-items:center; justify-content:center;"><img src="data:image/png;base64,{logo_b64}" style="height:{icon_size}; width:auto;" alt="Élysia"/></div>'
    # Text fallback with elegant styling
    font_size = {"small": "1.5rem", "medium": "2.5rem", "large": "3rem", "hero": "4rem"}.get(size, "2.5rem")
    return f'<div style="text-align:center;"><span style="font-family:\'Playfair Display\',Georgia,serif; font-size:{font_size}; font-weight:500; color:#8a6c4a; letter-spacing:0.08em;">Élysia</span></div>'


# =============================================================================
# CSS
# =============================================================================

LUXURY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0');

/* ============================================
   UNIFIED EXECUTIVE DESIGN SYSTEM
   Typography: Inter (clean, modern, professional)
   ============================================ */

:root {
    --cream: #FAFAF8;
    --warm-white: #F5F4F0;
    --white: #FFFFFF;
    --border: #E8E6E0;
    --gold: #8a6c4a;
    --gold-light: #a8896a;
    --gold-dark: #6d5539;
    --text-dark: #1a1a1a;
    --text-mid: #6B6560;
    --text-light: #9A958E;
    --success: #4A7C59;
    --success-bg: #E8F5E9;
    --danger: #9E4A4A;
    --danger-bg: #FFEBEE;
    --warning: #C4943A;
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
}

/* Global Reset */
.stApp { background: var(--cream) !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }

/* ============================================
   TYPOGRAPHY - UNIFIED ACROSS ALL PAGES
   ============================================ */

/* Base font, sans casser les polices d'icônes */
html, body, .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif !important;
}

/* Texte normal */
.stApp :is(p, div, label, li, a, input, textarea, button, h1, h2, h3, h4, h5, h6) {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif !important;
}

/* Icônes Streamlit (fix _arrow_right) */
.stApp .material-icons { font-family: 'Material Icons' !important; }
.stApp .material-symbols-outlined { font-family: 'Material Symbols Outlined' !important; }
.stApp .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }


/* Headers - Light weight, clean */
h1, h2, h3 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-dark) !important;
    font-weight: 300 !important;
    letter-spacing: -0.02em !important;
}

h1 { font-size: 3.6rem !important; }
h2 { font-size: 2.6rem !important; }
h3 { font-size: 2rem !important; }

/* Body text */
p, div, label, li {
    font-family: 'Inter', sans-serif !important;
    line-height: 1.6 !important;
    color: var(--text-mid);
}

/* spans, mais pas les icônes */
span:not(.material-icons):not(.material-symbols-outlined):not(.material-symbols-rounded) {
    font-family: 'Inter', sans-serif !important;
    line-height: 1.6 !important;
    color: var(--text-mid);
}

/* ============================================
   LARGE NUMBERS - Executive Style
   ============================================ */

.exec-number {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.8rem;
    font-weight: 300;
    color: var(--text-dark);
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.exec-number.gold { color: var(--gold); }
.exec-number.success { color: var(--success); }
.exec-number.danger { color: var(--danger); }

.exec-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-top: 0.5rem;
}

.exec-sublabel {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.65rem;
    color: var(--text-light);
    font-weight: 400;
}

/* ============================================
   HEADER & NAVIGATION
   ============================================ */

.lux-header {
    background: var(--white);
    border-bottom: 0.5px solid var(--border);
    padding: 1.5rem 0 1.25rem 0;
    margin-bottom: 2rem;
    text-align: center;
}

.lux-header-sub {
    font-size: 0.7rem;
    color: var(--text-light);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    font-weight: 500;
}

.step-badge {
    display: inline-block;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-mid);
    background: var(--warm-white);
    border: 0.5px solid var(--border);
    padding: 0.7rem 2.2rem;
    border-radius: 30px;
    margin-bottom: 1.5rem;
}
.page-headline {
    text-align: center;
    font-size: 3.2rem;     /* ← ajuste ici pour toutes les pages */
    font-weight: 300;
    color: #1a1a1a;
    letter-spacing: -0.01em;
    margin: 0.25rem 0 0.5rem 0;
}

.page-subtitle {
    text-align: center;
    font-size: 1.05rem;    /* ← ajuste ici */
    color: #6B6560;
    margin: 0 0 1.5rem 0;
}

.section-headline {
    text-align: center;
    font-size: 1.55rem;    /* ← pour les h3 style “Your Risk Appetite” */
    font-weight: 500;
    color: #1a1a1a;
    margin: 2rem 0 1rem 0;
}

/* Progress dots */
.progress-container { display: flex; justify-content: center; align-items: center; margin-bottom: 2rem; gap: 4px; }
.progress-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--border); transition: all 0.3s ease; }
.progress-dot.active { background: var(--gold); width: 10px; height: 10px; }
.progress-dot.completed { background: var(--success); }
.progress-line { width: 24px; height: 1px; background: var(--border); }
.progress-line.completed { background: var(--success); }

/* ============================================
   HERO / WELCOME PAGE
   ============================================ */

.hero-container {
    min-height: 60vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3rem 2rem;
    background: var(--white);
}

.hero-slogan {
    font-size: 1rem;
    font-style: italic;
    color: var(--gold);
    letter-spacing: 0.05em;
    margin-top: 1rem;
    font-weight: 400;
}

.hero-tagline {
    font-size: 1.4rem;
    font-weight: 300;
    color: var(--text-dark);
    line-height: 1.6;
    max-width: 600px;
    margin: 1.5rem 0 1rem 0;
}

.hero-tagline strong { color: var(--gold); font-weight: 500; }

.hero-subtitle {
    font-size: 0.95rem;
    color: var(--text-mid);
    max-width: 500px;
    line-height: 1.6;
    margin-bottom: 2.5rem;
    font-weight: 400;
}

.hero-trust {
    font-size: 0.65rem;
    color: var(--text-light);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 2.5rem;
    padding-top: 2rem;
    border-top: 0.5px solid var(--border);
    font-weight: 500;
}

/* ============================================
   COMPARISON CARDS (Hope Page)
   ============================================ */

.compare-card {
    border: 0.5px solid var(--border);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    text-align: center;
    background: var(--white);
}

.compare-card.current {
    background: linear-gradient(135deg, #FFF8F8 0%, #FFF5F5 100%);
    border-color: var(--danger);
    border-width: 1px;
}

.compare-card.target {
    background: linear-gradient(135deg, #F8FBF8 0%, #F5FAF5 100%);
    border-color: var(--success);
    border-width: 1px;
}

.compare-badge {
    display: inline-block;
    font-size: 0.55rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}

.compare-card.current .compare-badge { background: var(--danger); color: white; }
.compare-card.target .compare-badge { background: var(--success); color: white; }

.compare-value {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.2rem;
    font-weight: 300;
    color: var(--text-dark);
    margin: 0.5rem 0;
    letter-spacing: -0.02em;
}

.compare-label {
    font-size: 0.75rem;
    color: var(--text-mid);
    font-weight: 400;
}

.compare-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: var(--text-light);
    font-weight: 300;
}

/* Stats Row */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 4rem;
    margin: 2.5rem 0;
    padding: 1.5rem 0;
    flex-wrap: wrap;
}

.stat-item { text-align: center; }

.stat-value {
    font-family: 'Inter', sans-serif !important;
    font-size: 2rem;
    font-weight: 300;
    color: var(--text-dark);
    letter-spacing: -0.02em;
}

.stat-label {
    font-size: 0.65rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.35rem;
    font-weight: 500;
}

/* ============================================
   METRIC CARDS
   ============================================ */

.metric-card {
    background: var(--white);
    border: 0.5px solid var(--border);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    text-align: center;
    height: 100%;
}

.metric-card-value {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.2rem;
    font-weight: 300;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.metric-card-value.gold { color: var(--gold); }
.metric-card-value.success { color: var(--success); }
.metric-card-value.danger { color: var(--danger); }

.metric-card-label {
    font-size: 0.75rem;
    color: var(--text-mid);
    font-weight: 400;
}

.metric-card-logic {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 0.5px solid var(--border);
    text-align: left;
}

.metric-card-logic-title {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

.metric-card-logic-list {
    font-size: 0.8rem;
    color: var(--text-mid);
    line-height: 1.7;
    margin: 0;
    padding-left: 1rem;
}

.metric-card-logic-source {
    font-size: 0.7rem;
    font-style: italic;
    color: var(--text-light);
    margin-top: 0.5rem;
}

/* ============================================
   STRATEGY CARDS
   ============================================ */

.strategy-card {
    background: var(--white);
    border: 0.5px solid var(--border);
    border-radius: 16px;
    padding: 2rem 1.5rem;
    text-align: center;
    height: 100%;
    position: relative;
}

.strategy-card.conservative { border-left: 3px solid var(--success); }
.strategy-card.ambitious { border-left: 3px solid var(--warning); }

.strategy-card.recommended {
    border: 1.5px solid var(--gold);
    background: linear-gradient(180deg, #FFFCF9 0%, #FFF9F5 100%);
}

.strategy-card.recommended::before {
    content: 'RECOMMENDED';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
    color: white;
    font-size: 0.5rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    padding: 0.3rem 1rem;
    border-radius: 20px;
}

.strategy-card-title {
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
    margin-top: 0.5rem;
}

.strategy-card-desc {
    font-size: 0.8rem;
    color: var(--text-mid);
    margin-bottom: 1.25rem;
    min-height: 2.5rem;
    font-weight: 400;
    line-height: 1.5;
}

.strategy-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.strategy-metric {
    background: var(--warm-white);
    border-radius: 8px;
    padding: 0.6rem 0.4rem;
}

.strategy-metric-value {
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--text-dark);
}

.strategy-metric-label {
    font-size: 0.55rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.strategy-risk {
    display: inline-block;
    font-size: 0.55rem;
    font-weight: 600;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 0.75rem;
    letter-spacing: 0.08em;
}

.strategy-risk.low { background: var(--success-bg); color: var(--success); }
.strategy-risk.medium { background: #FFF8E1; color: var(--warning); }
.strategy-risk.high { background: var(--danger-bg); color: var(--danger); }

.strategy-why {
    font-size: 0.75rem;
    color: var(--text-mid);
    padding-top: 0.75rem;
    border-top: 0.5px solid var(--border);
    margin-top: 0.75rem;
    text-align: left;
    line-height: 1.5;
}

/* ============================================
   ROI SECTION
   ============================================ */

.roi-section {
    background: var(--white);
    border: 0.5px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
}

.roi-title {
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--text-dark);
    text-align: center;
    margin-bottom: 1.5rem;
}

/* ============================================
   BUTTONS - FIXED: Readable text
   ============================================ */

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #F5F4F0 0%, #E8E6E0 100%) !important;
    color: #1a1a1a !important;
    border: 1.5px solid var(--gold) !important;
    border-radius: 8px !important;
    padding: 0.8rem 2rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(138, 108, 74, 0.3) !important;
}

/* Form submit buttons (CTA) - gold with white text */
div[data-testid="stForm"] .stButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stForm"] .stButton > button:hover {
    background: linear-gradient(135deg, var(--gold-dark) 0%, #5a4530 100%) !important;
}

.stDownloadButton > button {
    background: transparent !important;
    color: var(--gold) !important;
    border: 1.5px solid var(--gold) !important;
    box-shadow: none !important;
}

.stDownloadButton > button:hover {
    background: var(--gold) !important;
    color: white !important;
}

/* ============================================
   FOOTER
   ============================================ */

.lux-footer {
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
    border-top: 0.5px solid var(--border);
}

.lux-footer-text {
    font-size: 0.6rem;
    color: var(--text-light);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ============================================
   DROPDOWNS / SELECT BOXES - FIXED
   ============================================ */

div[data-testid="stSelectbox"] {
    margin-bottom: 1rem;
}

div[data-testid="stSelectbox"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-dark) !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    transition: border-color 0.2s ease !important;
}

div[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--gold) !important;
}

div[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(138, 108, 74, 0.1) !important;
}

/* Slider styling */
div[data-testid="stSlider"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-dark) !important;
}

div[data-testid="stSlider"] > div > div > div {
    background: var(--gold) !important;
}

/* Radio buttons */
div[data-testid="stRadio"] label {
    font-family: 'Inter', sans-serif !important;
}

/* ============================================
   EXPANDERS - Clean styling
   ============================================ */

div[data-testid="stExpander"] {
    background: var(--white) !important;
    border: 0.5px solid var(--border) !important;
    border-radius: 12px !important;
    margin: 1rem 0 !important;
}

div[data-testid="stExpander"] summary {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: var(--text-dark) !important;
    padding: 1rem 1.25rem !important;
}

div[data-testid="stExpander"] summary:hover {
    color: var(--gold) !important;
}

/* ============================================
   METHODOLOGY SECTION - Clean styling
   ============================================ */

.methodology-box {
    background: var(--warm-white);
    border: 0.5px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.methodology-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 1rem;
}

.methodology-item {
    margin-bottom: 1rem;
}

.methodology-term {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--gold);
    margin-bottom: 0.25rem;
}

.methodology-def {
    font-size: 0.8rem;
    color: var(--text-mid);
    line-height: 1.6;
}

/* ============================================
   ROADMAP / ACTION PLAN
   ============================================ */

.roadmap-phase {
    background: var(--white);
    border: 0.5px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}

.roadmap-phase-header {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.roadmap-phase-num {
    width: 32px;
    height: 32px;
    background: var(--gold);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 600;
}

.roadmap-phase-name {
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-dark);
    flex-grow: 1;
}

.roadmap-phase-time {
    font-size: 0.7rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.roadmap-milestone {
    font-size: 0.8rem;
    color: var(--success);
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 0.5px solid var(--border);
}

/* ============================================
   SECTION TITLES
   ============================================ */

.section-title {
    font-size: 1.8rem;
    font-weight:600;
    color: var(--text-dark);
    text-align: center;
    margin: 2.5rem 0 2rem 0;
    text-transform: uppercase;
}
/* Page main titles - big and luxurious */
.page-title {
    font-size: 2.8rem;
    font-weight: 300;
    color: var(--text-dark);
    text-align: center;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.page-subtitle {
    font-size: 1.1rem;
    color: var(--text-mid);
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* ============================================
   STREAMLIT METRIC OVERRIDE
   ============================================ */

[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 300 !important;
    color: var(--text-dark) !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    color: var(--text-mid) !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'Inter', sans-serif !important;
}

/* ============================================
   LEGEND
   ============================================ */

.legend-box {
    background: var(--warm-white);
    border: 0.5px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin: 1.5rem auto;
    max-width: 800px;
}

.legend-title {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
}

.legend-items {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.legend-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: var(--text-mid);
}

.legend-item strong {
    color: var(--text-dark);
    white-space: nowrap;
    font-weight: 500;
}

/* ===== EXPANDER FIX: Hide broken arrow_right text ===== */

/* Remove list marker */
div[data-testid="stExpander"] details > summary {
  list-style: none !important;
}
div[data-testid="stExpander"] details > summary::-webkit-details-marker {
  display: none !important;
}

/* CRITICAL: Hide the SVG icon that shows "arrow_right" text */
div[data-testid="stExpander"] details > summary svg,
div[data-testid="stExpander"] details > summary [data-testid="stIconMaterial"] {
  display: none !important;
}

/* Style expander box */
div[data-testid="stExpander"] {
  border: 0.5px solid #E8E6E0 !important;
  border-radius: 8px !important;
  background: #FFFFFF !important;
  margin: 1rem 0 !important;
}

div[data-testid="stExpander"] details > summary {
  padding: 1rem 1.25rem !important;
  font-weight: 500 !important;
  color: #1a1a1a !important;
  cursor: pointer !important;
}

div[data-testid="stExpander"] details > summary:hover {
  color: #8a6c4a !important;
}

</style>
"""



# =============================================================================
# HELPERS
# =============================================================================

def fmt_currency(val: Any) -> str:
    if val is None: return "—"
    val = float(val)
    if abs(val) >= 1_000_000: return f"€{val/1_000_000:.1f}M"
    elif abs(val) >= 1_000: return f"€{val/1_000:,.0f}K"
    return f"€{val:,.0f}"

def fmt_time(months: int) -> str:
    if months >= 999:
        return "Not achievable"
    return f"{months}mo"

def _get_geo_options() -> Dict[str, str]:
    return {k: v.get("name", k) if isinstance(v, dict) else k for k, v in GRID_CARBON_FACTORS.items()}


# =============================================================================
# COMPONENTS
# =============================================================================

def render_header():
    st.markdown(f'<div class="lux-header">{_get_logo_html("medium")}<div class="lux-header-sub">Sustainable IT Intelligence · LVMH</div></div>', unsafe_allow_html=True)

def render_step_badge(step: int, title: str):
    st.markdown(f'<div style="text-align:center;"><span class="step-badge">STEP {step} · {title}</span></div>', unsafe_allow_html=True)

def render_progress(current: int, total: int = 7):
    dots = []
    for i in range(total):
        dot_class = "completed" if i < current else ("active" if i == current else "")
        dots.append(f'<div class="progress-dot {dot_class}"></div>')
        if i < total - 1:
            dots.append(f'<div class="progress-line {"completed" if i < current else ""}"></div>')
    st.markdown(f'<div class="progress-container">{"".join(dots)}</div>', unsafe_allow_html=True)

def render_strategy_legend():
    st.markdown('<div class="legend-box"><div class="legend-title">Understanding Strategy Types</div><div class="legend-items"><div class="legend-item"><strong>Recommended</strong> = Best balance of feasibility and impact</div><div class="legend-item"><strong>Conservative</strong> = Lower risk, proven approach</div><div class="legend-item"><strong>Ambitious</strong> = Maximum impact, higher effort</div></div></div>', unsafe_allow_html=True)


# =============================================================================
# STEP 0: WELCOME
# =============================================================================

def render_welcome():
    st.markdown(f'''<div class="hero-container">
        {_get_logo_html("hero")}
        <div class="hero-slogan">Where Insight Drives Impact</div>
        <div class="hero-tagline">Reduce your IT fleet's carbon footprint by <strong>30-50%</strong><br>while cutting procurement costs.</div>
        <div class="hero-subtitle">Data-driven sustainable IT strategy, powered by LVMH LIFE 360 methodology.</div>
    </div>''', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Begin Your Analysis", key=ui_key("welcome", "begin"), use_container_width=True):
            safe_goto("calibration")
        st.markdown("<p style='text-align:center; font-size:0.8rem; color:#9A958E; margin:1rem 0;'>— or —</p>", unsafe_allow_html=True)
        if st.button("I have fleet data - Skip to Upload", key=ui_key("welcome", "skip"), use_container_width=True):
            _update({"fleet_size": 12500})  # Default medium fleet
            safe_goto("upload")
    st.markdown('<div class="hero-trust">Trusted by LVMH Maisons · Backed by Industry Research</div>', unsafe_allow_html=True)


# =============================================================================
# STEP 1: CALIBRATION
# =============================================================================

def render_calibration():
    render_header()
    render_progress(0)
    render_step_badge(1, "CALIBRATION")
    st.markdown("<h2 style='text-align:center; font-size: 2.4rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.01em;'>Calibrate Your Baseline</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6B6560;'>Answer a few questions to personalize your analysis.</p>", unsafe_allow_html=True)
    geo_options = _get_geo_options()
    refresh_map = {"20": 5, "25": 4, "30": 3}
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(ui_key("calibration", "form")):
            st.markdown("**1. Fleet size** ▼")
            fleet_choice = st.selectbox("Fleet", options=["— Select —"] + list(FLEET_SIZE_OPTIONS.keys()), format_func=lambda x: x if x == "— Select —" else f"{FLEET_SIZE_OPTIONS[x]['label']} — {FLEET_SIZE_OPTIONS[x]['description']}", key=ui_key("calibration", "fleet"), label_visibility="collapsed")
            st.markdown("**2. Refresh rate** *(% replaced per year)* ▼")
            refresh_choice = st.selectbox("Refresh", options=["— Select —", "20% (5-year cycle)", "25% (4-year cycle)", "30% (3-year cycle)"], key=ui_key("calibration", "refresh"), label_visibility="collapsed")
            st.markdown("**3. Primary geography** ▼")
            geo_choice = st.selectbox("Geography", options=["— Select —"] + list(geo_options.keys()), format_func=lambda x: x if x == "— Select —" else geo_options.get(x, x), key=ui_key("calibration", "geo"), label_visibility="collapsed")
            st.markdown("**4. Current refurbished adoption** *(optional)*")
            refurb_pct = st.slider("Current %", 0, 40, 0, 5, key=ui_key("calibration", "refurb")) / 100.0
            st.markdown("**5. Sustainability target** *(optional)* ▼")
            target_choice = st.selectbox("Target", options=["— Optional —", "-20% by 2026 (LIFE 360)", "-30%", "-40%"], key=ui_key("calibration", "target"), label_visibility="collapsed")
            submitted = st.form_submit_button("Show Me the Impact", use_container_width=True)
        if submitted:
            errors = []
            if fleet_choice == "— Select —": errors.append("Select fleet size.")
            if refresh_choice == "— Select —": errors.append("Select refresh rate.")
            if geo_choice == "— Select —": errors.append("Select geography.")
            if errors:
                st.error(" ".join(errors))
            else:
                _update({"fleet_size": FLEET_SIZE_OPTIONS[fleet_choice]["estimate"], "refresh_cycle": refresh_map.get(refresh_choice.split("%")[0], 4), "geo_code": geo_choice, "current_refurb_pct": refurb_pct, "target_pct": int(target_choice.split("%")[0]) if target_choice.startswith("-") else -20})
                safe_goto("shock")


# =============================================================================
# STEP 2: SHOCK (NO ROI - moved to Hope page)
# =============================================================================

def render_shock():
    render_header()
    render_progress(1)
    render_step_badge(2, "COST OF INACTION")
    fleet_size = _s("fleet_size", 12500)
    refresh_cycle = _s("refresh_cycle", 4)
    target_pct = _s("target_pct", -20)
    geo_code = _s("geo_code", "FR")
    current_refurb = _s("current_refurb_pct", 0.0)
    
    shock = ShockCalculator.calculate(fleet_size=fleet_size, avg_age=3.5, refresh_cycle=refresh_cycle, target_pct=target_pct, geo_code=geo_code, current_refurb_pct=current_refurb)
    _update({"shock_result": shock})
    
    st.markdown("<h2 style='text-align:center; font-size: 2.4rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.01em;font-family: Inter, sans-serif; font-weight: 300; color: #1a1a1a; font-size: 2rem;'>If you do nothing...</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    sc, cc = shock.stranded_calculation, shock.co2_calculation
    
    with col1:
        st.markdown(f'''
        <div style="background: #FFFFFF; border: 0.5px solid #E8E6E0; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; height: 100%;">
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #8a6c4a; margin-bottom: 0.5rem; letter-spacing: -0.02em;">{fmt_currency(shock.stranded_value_eur)}</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.8rem; color: #6B6560; font-weight: 400;">stranded in aging devices</div>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 0.5px solid #E8E6E0; text-align: left;">
                <div style="font-family: Inter, sans-serif; font-size: 0.6rem; font-weight: 600; color: #8a6c4a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">How we calculated this</div>
                <ul style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; line-height: 1.8; margin: 0; padding-left: 1rem;">
                    <li>Fleet: <strong style="color: #1a1a1a;">{sc.get("fleet_size", fleet_size):,}</strong> devices</li>
                    <li>Avg price: <strong style="color: #1a1a1a;">€{sc.get("avg_price", 1150):,.0f}</strong></li>
                    <li>Remaining value: <strong style="color: #1a1a1a;">{sc.get("remaining_value_pct", 0.35)*100:.0f}%</strong></li>
                </ul>
                <div style="font-family: Inter, sans-serif; font-size: 0.65rem; font-style: italic; color: #9A958E; margin-top: 0.5rem;">Source: Gartner IT Asset Depreciation 2023</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div style="background: #FFFFFF; border: 0.5px solid #E8E6E0; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; height: 100%;">
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #8a6c4a; margin-bottom: 0.5rem; letter-spacing: -0.02em;">{shock.avoidable_co2_tonnes:,.0f}t</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.8rem; color: #6B6560; font-weight: 400;">avoidable CO2 / year</div>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 0.5px solid #E8E6E0; text-align: left;">
                <div style="font-family: Inter, sans-serif; font-size: 0.6rem; font-weight: 600; color: #8a6c4a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">How we calculated this</div>
                <ul style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; line-height: 1.8; margin: 0; padding-left: 1rem;">
                    <li>Replacements: <strong style="color: #1a1a1a;">{cc.get("annual_replacements", 3125):,.0f}</strong>/year</li>
                    <li>Refurb potential: <strong style="color: #1a1a1a;">{cc.get("effective_refurb_rate", 0.4)*100:.0f}%</strong></li>
                    <li>CO2 savings rate: <strong style="color: #1a1a1a;">{cc.get("savings_rate", 0.8)*100:.0f}%</strong></li>
                </ul>
                <div style="font-family: Inter, sans-serif; font-size: 0.65rem; font-style: italic; color: #9A958E; margin-top: 0.5rem;">Source: Dell Circular Economy Report 2023</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div style="background: #FFFFFF; border: 0.5px solid #E8E6E0; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; height: 100%;">
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #9E4A4A; margin-bottom: 0.5rem; letter-spacing: -0.02em;">2026</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.8rem; color: #6B6560; font-weight: 400;">LIFE 360 deadline at risk</div>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 0.5px solid #E8E6E0; text-align: left;">
                <div style="font-family: Inter, sans-serif; font-size: 0.6rem; font-weight: 600; color: #8a6c4a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">LIFE 360 Commitment</div>
                <ul style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; line-height: 1.8; margin: 0; padding-left: 1rem;">
                    <li>Target: <strong style="color: #1a1a1a;">{target_pct}%</strong> CO2 by 2026</li>
                    <li>Trajectory: <strong style="color: #9E4A4A;">WILL MISS</strong></li>
                </ul>
                <div style="font-family: Inter, sans-serif; font-size: 0.65rem; font-style: italic; color: #9A958E; margin-top: 0.5rem;">Source: LVMH LIFE 360 Program</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    show_stranded_value_disclaimer()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("What Can I Do?", key=ui_key("shock", "next"), use_container_width=True):
            safe_goto("hope")


# =============================================================================
# STEP 3: HOPE (WITH ROI)
# =============================================================================

def render_hope():
    render_header()
    render_progress(2)
    render_step_badge(3, "WHAT'S POSSIBLE")
    
    fleet_size = _s("fleet_size", 12500)
    refresh_cycle = _s("refresh_cycle", 4)
    target_pct = _s("target_pct", -20)
    current_refurb = _s("current_refurb_pct", 0.0)
    
    hope = HopeCalculator.calculate(fleet_size=fleet_size, avg_age=3.5, refresh_cycle=refresh_cycle, target_pct=target_pct, strategy_key="refurb_40", current_refurb_pct=current_refurb)
    _update({"hope_result": hope})
    
    # Title
    st.markdown("<h2 style='text-align:center; font-size: 2.4rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.01em; font-family: Inter, sans-serif; font-weight: 300; color: #1a1a1a; font-size: 2rem;'>But there's another path...</h2>", unsafe_allow_html=True)
    
    # Comparison cards with INLINE STYLES
    col1, col2, col3 = st.columns([5, 1, 5])
    with col1:
        st.markdown(f'''
        <div style="border: 1px solid #9E4A4A; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; background: linear-gradient(135deg, #FFF8F8 0%, #FFF5F5 100%);">
            <span style="display: inline-block; font-family: Inter, sans-serif; font-size: 0.55rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.35rem 0.9rem; border-radius: 20px; background: #9E4A4A; color: white; margin-bottom: 1rem;">CURRENT TRAJECTORY</span>
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; margin: 0.5rem 0; letter-spacing: -0.02em;">{hope.current_co2_tonnes:,.0f}t</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; font-weight: 400;">CO2 per year</div>
            <div style="height: 1.5rem;"></div>
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; margin: 0.5rem 0; letter-spacing: -0.02em;">{fmt_currency(hope.current_cost_eur)}</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; font-weight: 400;">Annual cost</div>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="display: flex; align-items: center; justify-content: center; height: 100%; font-size: 2rem; color: #9A958E; font-weight: 300;">→</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
        <div style="border: 1px solid #4A7C59; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; background: linear-gradient(135deg, #F8FBF8 0%, #F5FAF5 100%);">
            <span style="display: inline-block; font-family: Inter, sans-serif; font-size: 0.55rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.35rem 0.9rem; border-radius: 20px; background: #4A7C59; color: white; margin-bottom: 1rem;">WITH ÉLYSIA</span>
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; margin: 0.5rem 0; letter-spacing: -0.02em;">{hope.target_co2_tonnes:,.0f}t</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; font-weight: 400;">CO2 per year</div>
            <div style="height: 1.5rem;"></div>
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; margin: 0.5rem 0; letter-spacing: -0.02em;">{fmt_currency(hope.target_cost_eur)}</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #6B6560; font-weight: 400;">Annual cost</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Stats row with INLINE STYLES
    time_text = fmt_time(hope.months_to_target)
    annual_savings = hope.current_cost_eur - hope.target_cost_eur
    st.markdown(f'''
    <div style="display: flex; justify-content: center; gap: 5rem; margin: 3rem 0; padding: 2rem 0; flex-wrap: wrap;">
        <div style="text-align: center;">
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.02em;">-{abs(hope.co2_reduction_pct):.0f}%</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.65rem; color: #9A958E; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 0.5rem; font-weight: 500;">CO2 REDUCTION</div>
        </div>
        <div style="text-align: center;">
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.02em;">{fmt_currency(annual_savings)}</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.65rem; color: #9A958E; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 0.5rem; font-weight: 500;">ANNUAL CAPEX AVOIDANCE</div>
        </div>
        <div style="text-align: center;">
            <div style="font-family: Inter, sans-serif; font-size: 2.5rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.02em;">{time_text}</div>
            <div style="font-family: Inter, sans-serif; font-size: 0.65rem; color: #9A958E; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 0.5rem; font-weight: 500;">TIME TO TARGET</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Financial Potential section
    try:
        ROI_AVAILABLE = 'SimpleROICalculator' in globals() or 'SimpleROICalculator' in locals()
    except NameError:
        ROI_AVAILABLE = False

    if ROI_AVAILABLE:
        st.markdown("<hr style='border: none; border-top: 0.5px solid #E8E6E0; margin: 2rem 0;'>", unsafe_allow_html=True)
        
        hope_refurb_rate = hope.calculation_details.get("strategy", {}).get("refurb_rate", 0.40)
        
        roi_data = SimpleROICalculator.calculate(
            fleet_size=fleet_size,
            refresh_cycle_years=float(refresh_cycle),
            refurb_rate=float(hope_refurb_rate), 
            current_refurb_rate=current_refurb,
        )
        
        st.markdown(f'''
        <div style="background: #FFFFFF; border: 0.5px solid #E8E6E0; border-radius: 16px; padding: 2rem; margin: 1.5rem 0;">
            <div style="font-family: Inter, sans-serif; font-size: 1rem; font-weight: 500; color: #1a1a1a; text-align: center; margin-bottom: 2rem;">Financial Potential</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div style="text-align: center;">
                    <div style="font-family: Inter, sans-serif; font-size: 0.7rem; color: #9A958E; margin-bottom: 0.5rem; font-weight: 400;">Potential 5-Year CAPEX Avoidance</div>
                    <div style="font-family: Inter, sans-serif; font-size: 2.2rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.02em;">€{roi_data.five_year_capex_avoidance_eur:,.0f}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: Inter, sans-serif; font-size: 0.7rem; color: #9A958E; margin-bottom: 0.5rem; font-weight: 400;">Estimated Annual Impact</div>
                    <div style="font-family: Inter, sans-serif; font-size: 2.2rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.02em;">€{roi_data.five_year_capex_avoidance_eur / 5:,.0f}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander(" ▼ How we estimate these savings"):
            st.markdown(f"""
            **Calculation basis:**
            - Fleet size: {fleet_size:,} devices
            - Refresh cycle: {refresh_cycle} years
            - Target refurb rate: {hope_refurb_rate*100:.0f}%
            - Price delta: €{1150 - 679:.0f} per device (New vs Refurbished)
            """)

    # Navigation button
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Build My Strategy", key=ui_key("hope", "next"), use_container_width=True):
            safe_goto("strategy")


# =============================================================================
# STEP 4: STRATEGY SELECTION
# =============================================================================

def render_strategy():
    render_header()
    render_progress(3)
    render_step_badge(4, "CHOOSE YOUR STRATEGY")
    
    fleet_size = _s("fleet_size", 12500)
    refresh_cycle = _s("refresh_cycle", 4)
    target_pct = _s("target_pct", -20)
    geo_code = _s("geo_code", "FR")
    
    results_all = StrategySimulator.compare_all_strategies(fleet_size=fleet_size, current_refresh=refresh_cycle, avg_age=3.5, target_pct=target_pct, geo_code=geo_code, data_mode="estimated")
    _update({"all_strategies": results_all})
    
    st.markdown("<h3 style='text-align:center;'>Your Risk Appetite</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        risk_appetite = st.radio(
            "Risk Appetite",
            options=["conservative", "balanced", "aggressive"],
            index=["conservative", "balanced", "aggressive"].index(_s("risk_appetite", "balanced")),
            format_func=lambda x: {"conservative": "Conservative", "balanced": "Balanced", "aggressive": "Aggressive"}.get(x, x),
            key=ui_key("strategy", "risk"),
            horizontal=True,
            label_visibility="collapsed"
        )
        _update({"risk_appetite": risk_appetite})
    
    # Get strategies
    if _EXTENSIONS_READY:
        try:
            strategy_set = RiskBasedSelector.pick_by_risk_appetite(results_all, risk_appetite)
            conservative, recommended, ambitious = strategy_set.conservative, strategy_set.recommended, strategy_set.ambitious
            explanations = strategy_set.explanations
        except:
            sorted_s = sorted([r for r in results_all if r.strategy_key != "do_nothing"], key=lambda x: abs(x.co2_reduction_pct))
            conservative = sorted_s[0] if sorted_s else results_all[0]
            ambitious = sorted_s[-1] if len(sorted_s) > 1 else sorted_s[0]
            recommended = sorted_s[len(sorted_s)//2] if len(sorted_s) > 2 else conservative
            explanations = {"conservative": "Lower risk, proven approach.", "recommended": "Balanced trade-off.", "ambitious": "Maximum impact."}
    else:
        sorted_s = sorted([r for r in results_all if r.strategy_key != "do_nothing"], key=lambda x: abs(x.co2_reduction_pct))
        conservative = sorted_s[0] if sorted_s else results_all[0]
        ambitious = sorted_s[-1] if len(sorted_s) > 1 else sorted_s[0]
        recommended = sorted_s[len(sorted_s)//2] if len(sorted_s) > 2 else conservative
        explanations = {"conservative": "Lower risk, proven approach.", "recommended": "Balanced trade-off.", "ambitious": "Maximum impact."}
    
    render_strategy_legend()
    
    def get_risk_level(s):
        details = s.calculation_details or {}
        refurb = details.get("strategy", {}).get("refurb_rate", 0.3)
        if refurb <= 0.25: return "low", "LOW RISK"
        elif refurb <= 0.50: return "medium", "MEDIUM RISK"
        return "high", "HIGH RISK"
    
    col1, col2, col3 = st.columns(3)
    for col, strat, card_type, is_rec in [(col1, conservative, "conservative", False), (col2, recommended, "recommended", True), (col3, ambitious, "ambitious", False)]:
        with col:
            risk_class, risk_text = get_risk_level(strat)
            card_class = f"strategy-card {card_type}" + (" recommended" if is_rec else "")
            desc = strat.description[:80] + "..." if strat.description and len(strat.description) > 80 else (strat.description or "")
            time_text = fmt_time(strat.time_to_target_months)
            
            st.markdown(f'''<div class="{card_class}">
                <div class="strategy-card-title">{strat.strategy_name}</div>
                <div class="strategy-card-desc">{desc}</div>
                <div class="strategy-metrics">
                    <div class="strategy-metric">
                        <div class="strategy-metric-value">-{abs(strat.co2_reduction_pct):.0f}%</div>
                        <div class="strategy-metric-label">CO2</div>
                    </div>
                    <div class="strategy-metric">
                        <div class="strategy-metric-value">{fmt_currency(strat.annual_capex_avoidance_eur)}</div>
                        <div class="strategy-metric-label">CAPEX Avoidance</div>
                    </div>
                    <div class="strategy-metric">
                        <div class="strategy-metric-value">{time_text}</div>
                        <div class="strategy-metric-label">Time</div>
                    </div>
                    <div class="strategy-metric">
                        <div class="strategy-metric-value">{"Yes" if strat.reaches_target else "No"}</div>
                        <div class="strategy-metric-label">Target</div>
                    </div>
                </div>
                <span class="strategy-risk {risk_class}">{risk_text}</span>
                <div class="strategy-why">{explanations.get(card_type, "")}</div>
            </div>''', unsafe_allow_html=True)
            
            if st.button("Select", key=ui_key("strategy", f"sel_{card_type}"), use_container_width=True):
                _update({"selected_strategy_key": strat.strategy_key, "selected_strategy": strat})
                safe_goto("upload")
    
    # Full comparison table
    st.markdown("<h3 style='text-align:center; margin-top:2rem;'>Full Strategy Comparison</h3>", unsafe_allow_html=True)
    comp_data = []
    for r in sorted(results_all, key=lambda x: (not x.reaches_target, -abs(x.co2_reduction_pct))):
        comp_data.append({
            "Strategy": ("→ " if r.strategy_key == recommended.strategy_key else "") + r.strategy_name,
            "CO2": f"-{abs(r.co2_reduction_pct):.0f}%",
            "CAPEX Avoidance": fmt_currency(r.annual_capex_avoidance_eur),
            "Time": fmt_time(r.time_to_target_months),
            "Target": "Yes" if r.reaches_target else "No"
        })
    st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)


# =============================================================================
# EXPORTS for part2
# =============================================================================

__all__ = [
    # State management
    "ui_key", "_get_audit_state", "_create_default_state", "_s", "_update", "_reset_state", "safe_goto", "_sanity_check_backend",
    # Components
    "render_header", "render_step_badge", "render_progress", "render_strategy_legend",
    "_get_logo_html", "fmt_currency", "fmt_time", "_get_geo_options",
    # CSS
    "LUXURY_CSS",
    # Steps
    "render_welcome", "render_calibration", "render_shock", "render_hope", "render_strategy",
    # Flags
    "_BACKEND_READY", "_IMPORT_ERROR", "_EXTENSIONS_READY", "_CREDIBILITY_AVAILABLE", "ROI_AVAILABLE",
    # Imports
    "FLEET_SIZE_OPTIONS", "GRID_CARBON_FACTORS",
]# =============================================================================
# ADDITIONAL CSS FOR PART 2
# =============================================================================

PART2_CSS = """
<style>
/* ============================================
   PART 2 CSS - UNIFIED WITH INTER TYPOGRAPHY
   ============================================ */

.insight-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
.insight-card { background: var(--white); border: 0.5px solid var(--border); border-radius: 12px; padding: 1.25rem; border-left: 3px solid var(--success); }
.insight-title { font-size: 0.75rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; }
.insight-text { font-size: 0.8rem; color: var(--text-mid); margin-bottom: 0.75rem; line-height: 1.5; }
.insight-value { font-size: 1.4rem; font-weight: 300; color: var(--success); letter-spacing: -0.02em; }

.simulator-card { background: var(--white); border: 0.5px solid var(--border); border-radius: 16px; padding: 2rem; margin: 1.5rem 0; }
.simulator-title { font-size: 1.1rem; font-weight: 500; color: var(--text-dark); margin-bottom: 0.5rem; }
.simulator-subtitle { font-size: 0.8rem; color: var(--text-mid); margin-bottom: 1.5rem; }
.simulator-result { background: var(--success-bg); border-radius: 10px; padding: 1.25rem; margin-top: 1.5rem; text-align: center; }
.simulator-result-title { font-size: 0.65rem; font-weight: 600; color: var(--success); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
.simulator-result-value { font-size: 1.4rem; font-weight: 300; color: var(--success); }

.strategy-summary { background: var(--warm-white); border: 0.5px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
.strategy-summary-title { font-size: 0.65rem; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem; }
.strategy-summary-name { font-size: 1.1rem; font-weight: 500; color: var(--text-dark); margin-bottom: 0.5rem; }
.strategy-summary-metrics { display: flex; gap: 2rem; margin-top: 1rem; }
.strategy-summary-metric { text-align: center; }
.strategy-summary-metric-value { font-size: 1.3rem; font-weight: 300; color: var(--success); }
.strategy-summary-metric-label { font-size: 0.65rem; color: var(--text-mid); text-transform: uppercase; letter-spacing: 0.08em; }

.plan-phase { background: var(--white); border: 0.5px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
.plan-phase-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 0.5px solid var(--border); }
.plan-phase-number { width: 36px; height: 36px; background: var(--gold); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 600; }
.plan-phase-title { font-size: 1rem; font-weight: 500; color: var(--text-dark); }
.plan-phase-subtitle { font-size: 0.7rem; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.08em; }
.plan-phase-tasks { margin: 0; padding-left: 1.25rem; color: var(--text-mid); font-size: 0.85rem; line-height: 1.8; }

.business-value-card { background: linear-gradient(135deg, #F8FAF8 0%, #F5F9F5 100%); border: 1px solid var(--success); border-radius: 16px; padding: 2rem; margin: 1.5rem 0; text-align: center; }
.business-value-title { font-size: 1.1rem; font-weight: 500; color: var(--text-dark); margin-bottom: 1.5rem; }
.business-value-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.business-value-item { }
.business-value-item-value { font-size: 1.8rem; font-weight: 300; color: var(--success); letter-spacing: -0.02em; }
.business-value-item-label { font-size: 0.7rem; color: var(--text-mid); margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.08em; }

.roi-card { background: var(--white); border: 0.5px solid var(--border); border-radius: 16px; padding: 2rem 1.5rem; text-align: center; }
.roi-card-value { font-size: 2rem; font-weight: 300; color: var(--success); margin-bottom: 0.5rem; letter-spacing: -0.02em; }
.roi-card-label { font-size: 0.75rem; color: var(--text-mid); }
</style>
"""


# =============================================================================
# STEP 5: UPLOAD DATA
# =============================================================================

def render_upload():
    render_header()
    render_progress(4)
    render_step_badge(5, "UPLOAD DATA")
    st.markdown("<h2 style='text-align:center; font-size: 2.4rem; font-weight: 300; color: #1a1a1a; letter-spacing: -0.01em;'>Increase Your Confidence</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6B6560;'>Upload fleet data for precise, board-ready recommendations.</p>", unsafe_allow_html=True)
    
    # Ensure strategy is set
    if not _s("selected_strategy"):
        results = _s("all_strategies") or StrategySimulator.compare_all_strategies(
            fleet_size=_s("fleet_size", 12500),
            current_refresh=_s("refresh_cycle", 4),
            avg_age=3.5,
            target_pct=_s("target_pct", -20)
        )
        if _EXTENSIONS_READY:
            try:
                _update({"selected_strategy": RiskBasedSelector.pick_by_risk_appetite(results, _s("risk_appetite", "balanced")).recommended})
            except:
                if results:
                    _update({"selected_strategy": results[0]})
        elif results:
            _update({"selected_strategy": results[0]})
    
    # Upload section
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("**Upload Your Data**")
        uploaded = st.file_uploader("Fleet CSV", type=["csv"], key=ui_key("upload", "file"))
    with col2:
        st.markdown("**Get Template**")
        template_data = generate_fleet_template() if _EXTENSIONS_READY else "Device_Model,Age_Years,Persona,Country\nMacBook Pro 14,2.5,Developer (Tech),FR"
        st.download_button("Download Template", data=template_data, file_name="fleet_template.csv", mime="text/csv", use_container_width=True, key=ui_key("upload", "template"))
    with col3:
        st.markdown("**Try Demo Data**")
        if st.button("Load Demo Fleet", key=ui_key("upload", "demo"), use_container_width=True):
            demo_df = generate_demo_fleet_extended(150) if _EXTENSIONS_READY else pd.DataFrame()
            _update({"fleet_data": demo_df, "data_source": "uploaded"})
            st.rerun()
    
    if uploaded:
        try:
            _update({"fleet_data": pd.read_csv(uploaded), "data_source": "uploaded"})
            st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    df = _s("fleet_data")
    if df is not None and len(df) > 0:
        st.markdown("---")
        
        # Get strategy for insights
        strategy = _s("selected_strategy")
        if not strategy:
            results = StrategySimulator.compare_all_strategies(len(df), _s("refresh_cycle", 4), 3.5, _s("target_pct", -20))
            strategy = results[0] if results else None
        
        # Generate DYNAMIC insights using FleetInsightsGenerator
        if _EXTENSIONS_READY and strategy:
            try:
                insights_result = FleetInsightsGenerator.generate_executive_insights(
                    df=df,
                    baseline_estimates={'fleet_size': len(df), 'avg_age': df["Age_Years"].mean() if "Age_Years" in df.columns else 3.5},
                    selected_strategy=strategy,
                    refresh_cycle=_s("refresh_cycle", 4)
                )
                
                # Executive Summary from real data
                st.markdown("### Executive Summary")
                summary = insights_result.summary
                fleet_size = summary.get("fleet_size", len(df))
                avg_age = summary.get("avg_age", 3.5)
                at_risk = summary.get("devices_at_risk", 0)
                at_risk_pct = summary.get("age_risk_share", 0) * 100
                refurb_eligible = summary.get("devices_refurb_eligible", fleet_size)
                refurb_pct = summary.get("refurb_eligible_share", 1.0) * 100
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Fleet Size", f"{fleet_size:,}")
                c2.metric("Avg Age", f"{avg_age:.1f} years")
                c3.metric("At Risk (>4yr)", f"{at_risk_pct:.0f}%")
                c4.metric("Refurb Eligible", f"{refurb_pct:.0f}%")
                
                # Dynamic Key Insights
                st.markdown("### Key Insights")
                st.markdown(PART2_CSS, unsafe_allow_html=True)
                
                # Build insight cards from dynamic data
                insight_cards_html = '<div class="insight-grid">'
                for insight in insights_result.insights:
                    severity_color = "var(--success)" if insight.severity == "positive" else ("var(--warning)" if insight.severity == "warning" else "var(--text-mid)")
                    insight_cards_html += f'''
                    <div class="insight-card" style="border-left-color: {severity_color};">
                        <div class="insight-title">{insight.title.upper()}</div>
                        <div class="insight-text">{insight.main_text}</div>
                        <div class="insight-value" style="color: {severity_color};">{insight.calculation.result}</div>
                    </div>'''
                insight_cards_html += '</div>'
                st.markdown(insight_cards_html, unsafe_allow_html=True)
                
                # Calculation proofs in dropdown
                with st.expander(" ▼ View calculation details"):
                    for insight in insights_result.insights:
                        st.markdown(f"**{insight.title}**")
                        st.markdown(f"- Formula: {insight.calculation.formula}")
                        st.markdown(f"- Inputs: {insight.calculation.inputs}")
                        st.markdown(f"- Result: {insight.calculation.result}")
                        if insight.calculation.source:
                            st.caption(f"Source: {insight.calculation.source}")
                        st.markdown("---")
                
                # Store insights for action plan
                _update({"fleet_insights": insights_result})
                
                st.success(f"Confidence upgraded: **{insights_result.confidence_before}** → **{insights_result.confidence_after}** (based on uploaded data)")
                
            except Exception as e:
                # Fallback to basic display
                st.warning(f"Using basic analysis (advanced insights unavailable)")
                _render_basic_upload_summary(df)
        else:
            _render_basic_upload_summary(df)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key=ui_key("upload", "back")):
            safe_goto("strategy")
    with col2:
        btn_text = "Continue with Fleet Data" if df is not None else "Skip - Use Estimates"
        if st.button(btn_text, key=ui_key("upload", "next"), use_container_width=True):
            safe_goto("simulator")


def _render_basic_upload_summary(df):
    """Fallback basic summary when advanced insights unavailable."""
    fleet_size = len(df)
    avg_age = df["Age_Years"].mean() if "Age_Years" in df.columns else 3.5
    at_risk = (df["Age_Years"] >= 4).sum() if "Age_Years" in df.columns else int(fleet_size * 0.3)
    at_risk_pct = at_risk / fleet_size * 100 if fleet_size > 0 else 0
    
    # Get constants from calculator or use defaults
    try:
        from calculator import AVERAGES, REFURB_CONFIG
        device_price = AVERAGES.get("device_price_eur", 1150)
        price_ratio = REFURB_CONFIG.get("price_ratio", 0.59)
    except:
        device_price = 1150
        price_ratio = 0.59
    
    refurb_price = device_price * price_ratio
    price_delta = device_price - refurb_price
    
    refresh_cycle = _s("refresh_cycle", 4)
    target_refurb_rate = 0.40  # Default strategy assumption
    
    st.markdown("### Executive Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fleet Size", f"{fleet_size:,}")
    c2.metric("Avg Age", f"{avg_age:.1f} years")
    c3.metric("At Risk (>4yr)", f"{at_risk_pct:.0f}%")
    # Most enterprise devices are refurb eligible - calculate based on age
    refurb_eligible_count = len(df[df["Age_Years"] >= 1]) if "Age_Years" in df.columns else fleet_size
    refurb_eligible_pct = (refurb_eligible_count / fleet_size * 100) if fleet_size > 0 else 100
    c4.metric("Refurb Eligible", f"{refurb_eligible_pct:.0f}%")
    
    st.markdown("### Key Insights")
    # Calculate using proper formula: at_risk * productivity_cost_per_device
    productivity_cost_per_device = 450  # Industry benchmark
    hidden_cost = at_risk * productivity_cost_per_device
    
    # Calculate savings: (fleet/cycle) * refurb_rate * price_delta
    annual_replacements = fleet_size / refresh_cycle
    savings_potential = annual_replacements * target_refurb_rate * price_delta
    
    st.markdown(f'''
    <div class="insight-grid">
        <div class="insight-card">
            <div class="insight-title">FLEET AGE ABOVE BENCHMARK</div>
            <div class="insight-text">Your fleet has {at_risk} high-risk devices creating hidden productivity costs.</div>
            <div class="insight-value">€{hidden_cost:,.0f}/year</div>
        </div>
        <div class="insight-card">
            <div class="insight-title">REFURBISHMENT OPPORTUNITY</div>
            <div class="insight-text">{fleet_size} devices qualify for refurbished alternatives.</div>
            <div class="insight-value">€{savings_potential:,.0f}/year potential</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.success("Confidence upgraded: **MEDIUM** → **HIGH** (based on uploaded data)")


# =============================================================================
# STEP 6: DEVICE SIMULATOR (SIMPLIFIED)
# =============================================================================

def render_simulator():
    render_header()
    render_progress(5)
    render_step_badge(6, "DEVICE SIMULATOR")
    
    strategy = _s("selected_strategy")
    if not strategy:
        st.warning("No strategy selected. Please go back and select a strategy.")
        if st.button("Back to Strategy", key=ui_key("simulator", "back_strat")):
            safe_goto("strategy")
        return
    
    # Strategy Summary
    details = strategy.calculation_details or {}
    refurb_rate = details.get("strategy", {}).get("refurb_rate", 0.4)
    time_text = fmt_time(strategy.time_to_target_months)
    
    st.markdown(f'''
    <div class="strategy-summary">
        <div class="strategy-summary-title">Your Selected Strategy</div>
        <div class="strategy-summary-name">{strategy.strategy_name}</div>
        <div class="strategy-summary-metrics">
            <div class="strategy-summary-metric">
                <div class="strategy-summary-metric-value">-{abs(strategy.co2_reduction_pct):.0f}%</div>
                <div class="strategy-summary-metric-label">CO2 Reduction</div>
            </div>
            <div class="strategy-summary-metric">
                <div class="strategy-summary-metric-value">{fmt_currency(strategy.annual_capex_avoidance_eur)}</div>
                <div class="strategy-summary-metric-label">Annual CAPEX Avoidance</div>
            </div>
            <div class="strategy-summary-metric">
                <div class="strategy-summary-metric-value">{int(refurb_rate*100)}%</div>
                <div class="strategy-summary-metric-label">Refurb Rate</div>
            </div>
            <div class="strategy-summary-metric">
                <div class="strategy-summary-metric-value">{time_text}</div>
                <div class="strategy-summary-metric-label">Time to Target</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(PART2_CSS, unsafe_allow_html=True)
    
    # Device Simulator
    st.markdown('''
    <div class="simulator-card">
        <div class="simulator-title">Device Simulator</div>
        <div class="simulator-subtitle">Test what decision makes sense for a specific device.</div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        device_type = st.selectbox("Device", options=["Laptop (Standard)", "Laptop (Performance)", "Smartphone", "Tablet", "Screen"], key=ui_key("simulator", "device"))
    with col2:
        user_profile = st.selectbox("User Profile", options=["Admin Normal (HR/Finance)", "Developer (Tech)", "Executive", "Field Worker"], key=ui_key("simulator", "profile"))
    with col3:
        location = st.selectbox("Location", options=["France", "Germany", "UK", "USA", "Italy"], key=ui_key("simulator", "location"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        device_age = st.slider("Device Age (years)", 0.0, 7.0, 3.5, 0.5, key=ui_key("simulator", "age"))
    with col2:
        objective = st.selectbox("Objective", options=["Balanced", "Cost Priority", "Sustainability Priority"], key=ui_key("simulator", "objective"))
    with col3:
        criticality = st.selectbox("Criticality", options=["Low", "Medium", "High"], key=ui_key("simulator", "criticality"))
    
    if st.button("Calculate Recommendation", key=ui_key("simulator", "calc"), use_container_width=True):
        # Simple recommendation logic
        if device_age >= 4:
            if criticality == "High":
                recommendation = "REPLACE WITH NEW"
                reason = "High criticality role requires maximum reliability"
                savings = 0
            else:
                recommendation = "REPLACE WITH REFURBISHED"
                reason = f"Device is {device_age:.1f} years old - ideal for refurbished replacement"
                savings = 470  # Avg savings
        elif device_age >= 3:
            recommendation = "EXTEND LIFECYCLE (+1 YEAR)"
            reason = "Device still has useful life remaining"
            savings = 287  # Deferred purchase
        else:
            recommendation = "KEEP CURRENT DEVICE"
            reason = "Device is relatively new, no action needed"
            savings = 0
        
        st.markdown(f'''
        <div class="simulator-result">
            <div class="simulator-result-title">Recommendation</div>
            <div class="simulator-result-value">{recommendation}</div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-mid);">{reason}</div>
            {f'<div style="margin-top: 0.75rem; font-size: 1rem; color: var(--success);"><strong>Potential savings: €{savings}</strong></div>' if savings > 0 else ''}
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key=ui_key("simulator", "back")):
            safe_goto("upload")
    with col2:
        if st.button("Generate Action Plan", key=ui_key("simulator", "next"), use_container_width=True):
            safe_goto("action")


# =============================================================================
# STEP 7: ACTION PLAN (FIXED)
# =============================================================================

def render_action():
    render_header()
    render_progress(6)
    render_step_badge(7, "EXECUTIVE DASHBOARD")
    
    strategy = _s("selected_strategy")
    if not strategy:
        st.error("No strategy selected. Please start over.")
        if st.button("Start Over", key=ui_key("action", "restart_err")):
            _reset_state()
            st.rerun()
        return
    
    df = _s("fleet_data")
    data_source = "uploaded" if df is not None and len(df) > 0 else "estimates"
    confidence = "HIGH" if data_source == "uploaded" else "MEDIUM"
    
    # CRITICAL: Ensure fleet_size is never 0
    if df is not None and len(df) > 0:
        fleet_size = len(df)
    else:
        fleet_size = _s("fleet_size", 12500)
    if fleet_size == 0:
        fleet_size = 12500  # Fallback
    
    refresh_cycle = _s("refresh_cycle", 4)
    if refresh_cycle == 0:
        refresh_cycle = 4
    
    # Get strategy metrics
    details = strategy.calculation_details or {}
    refurb_rate = details.get("strategy", {}).get("refurb_rate", 0.4)
    if refurb_rate == 0:
        refurb_rate = 0.4  # Default to 40%
    
    co2_pct = abs(strategy.co2_reduction_pct)
    
    # Business Value Summary - Calculate fresh
    roi = SimpleROICalculator.calculate(
        fleet_size=fleet_size,
        refresh_cycle_years=int(refresh_cycle),
        refurb_rate=float(refurb_rate),
        current_refurb_rate=float(_s("current_refurb_pct", 0.0)),
    )
    
    # Calculate CO2 avoided over 5 years using calculator constants
    try:
        from calculator import AVERAGES, REFURB_CONFIG
        co2_per_device_kg = AVERAGES.get("device_co2_manufacturing_kg", 365)
        co2_savings_rate = REFURB_CONFIG.get("co2_savings_rate", 0.80)
    except:
        co2_per_device_kg = 365
        co2_savings_rate = 0.80
    
    annual_replacements = fleet_size / refresh_cycle
    # CO2 avoided = devices switching to refurb * CO2 per device * savings rate
    co2_avoided_per_year_kg = annual_replacements * refurb_rate * co2_per_device_kg * co2_savings_rate
    co2_avoided_5yr = co2_avoided_per_year_kg / 1000 * 5  # Convert to tonnes, multiply by 5 years
    
    # =========================================================================
    # LUXURY EXECUTIVE DASHBOARD CSS
    # =========================================================================
    st.markdown("""
    <style>
    /* Executive Dashboard Typography */
    .exec-dashboard {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        letter-spacing: 0.02em;
    }
    
    /* Executive Summary KPIs */
    .exec-kpi-container {
        display: flex;
        justify-content: center;
        gap: 3rem;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #fafaf8 0%, #f5f4f0 100%);
        border-radius: 16px;
        margin: 1.5rem 0 3rem 0;
        border: 0.5px solid #e8e6e0;
    }
    
    .exec-kpi {
        text-align: center;
        padding: 0 2rem;
    }
    
    .exec-kpi:not(:last-child) {
        border-right: 0.5px solid #d4d2cc;
    }
    
    .exec-kpi-value {
        font-size: 2.8rem;
        font-weight: 300;
        color: #1a1a1a;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    .exec-kpi-value.gold {
        color: #8a6c4a;
    }
    
    .exec-kpi-label {
        font-size: 0.7rem;
        font-weight: 500;
        color: #6b6560;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 0.5rem;
    }
    
    .exec-kpi-sublabel {
        font-size: 0.65rem;
        color: #9a958e;
        margin-top: 0.25rem;
        font-weight: 400;
    }
    
    /* Section Titles */
    .section-title {
        font-size: 0.75rem;
        font-weight: 500;
        color: #9a958e;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        text-align: center;
        margin: 3rem 0 1.5rem 0;
    }
    
    /* Strategy Triptych */
    .triptych-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .triptych-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
    }
    
    /* Heritage - Conservative */
    .triptych-card.heritage {
        border: 0.5px solid #4a4a4a;
    }
    
    .triptych-card.heritage:hover {
        border-color: #2a2a2a;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Élysia Optimum - Recommended */
    .triptych-card.optimum {
        border: 1.5px solid #8a6c4a;
        box-shadow: 0 8px 32px rgba(212,175,55,0.15);
    }
    
    .triptych-card.optimum::before {
        content: 'RECOMMENDED';
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #8a6c4a 0%, #6d5639 100%);
        color: white;
        font-size: 0.55rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        padding: 0.35rem 1rem;
        border-radius: 20px;
    }
    
    /* Frontier - Ambitious */
    .triptych-card.frontier {
        border: 0.5px solid #d4d2cc;
    }
    
    .triptych-card.frontier:hover {
        border-color: #b8b5ae;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .triptych-name {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: 0.02em;
    }
    
    .triptych-subtitle {
        font-size: 0.7rem;
        color: #9a958e;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }
    
    .triptych-desc {
        font-size: 0.85rem;
        color: #6b6560;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        min-height: 3rem;
    }
    
    .triptych-metrics {
        display: flex;
        justify-content: space-around;
        padding-top: 1rem;
        border-top: 0.5px solid #e8e6e0;
    }
    
    .triptych-metric {
        text-align: center;
    }
    
    .triptych-metric-value {
        font-size: 1.3rem;
        font-weight: 400;
        color: #1a1a1a;
    }
    
    .triptych-metric-label {
        font-size: 0.6rem;
        color: #9a958e;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.25rem;
    }
    
    /* Methodology Expander */
    .methodology-section {
        margin-top: 3rem;
        padding: 1.5rem;
        background: #fafaf8;
        border-radius: 12px;
        border: 0.5px solid #e8e6e0;
    }
    
    .methodology-title {
        font-size: 0.8rem;
        font-weight: 500;
        color: #6b6560;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }
    
    .methodology-item {
        margin-bottom: 1rem;
    }
    
    .methodology-term {
        font-weight: 500;
        color: #1a1a1a;
        font-size: 0.9rem;
    }
    
    .methodology-def {
        color: #6b6560;
        font-size: 0.85rem;
        margin-top: 0.25rem;
        line-height: 1.5;
    }
    
    /* 90-Day Roadmap Minimal */
    .roadmap-phase {
        background: #ffffff;
        border: 0.5px solid #e8e6e0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    
    .roadmap-phase-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .roadmap-phase-num {
        width: 24px;
        height: 24px;
        background: #f5f4f0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 600;
        color: #6b6560;
    }
    
    .roadmap-phase-name {
        font-size: 0.9rem;
        font-weight: 500;
        color: #1a1a1a;
    }
    
    .roadmap-phase-time {
        font-size: 0.7rem;
        color: #9a958e;
        margin-left: auto;
    }
    
    .roadmap-milestone {
        background: linear-gradient(135deg, #f0f7f0 0%, #e8f4e8 100%);
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        color: #2d5a2d;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # EXECUTIVE SUMMARY - TOP KPIs
    # =========================================================================
    st.markdown(f"""
    <div class="exec-dashboard">
        <div class="exec-kpi-container">
            <div class="exec-kpi">
                <div class="exec-kpi-value gold">€{roi.annual_capex_avoidance_eur:,.0f}</div>
                <div class="exec-kpi-label">CAPEX Optimization</div>
                <div class="exec-kpi-sublabel">Annual Avoidance</div>
            </div>
            <div class="exec-kpi">
                <div class="exec-kpi-value">-{co2_pct:.0f}%</div>
                <div class="exec-kpi-label">Carbon Reduction</div>
                <div class="exec-kpi-sublabel">Year-over-Year</div>
            </div>
            <div class="exec-kpi">
                <div class="exec-kpi-value">{roi.return_multiple:.0f}x</div>
                <div class="exec-kpi-label">Return Multiple</div>
                <div class="exec-kpi-sublabel">5-Year Horizon</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # THE TRIPTYCH - Strategy Cards
    # =========================================================================
    st.markdown('<div class="section-title">Strategic Pathways</div>', unsafe_allow_html=True)
    
    # Get all strategies for triptych
    results_all = _s("all_strategies") or StrategySimulator.compare_all_strategies(
        fleet_size=fleet_size, current_refresh=refresh_cycle, avg_age=3.5, 
        target_pct=_s("target_pct", -20), geo_code=_s("geo_code", "FR")
    )
    
    # Find conservative, optimum, ambitious - filter out strategies with 0 impact
    actionable = [r for r in results_all if r.strategy_key != "do_nothing" and abs(r.co2_reduction_pct) > 0]
    if len(actionable) < 3:
        actionable = [r for r in results_all if r.strategy_key != "do_nothing"]
    
    sorted_strats = sorted(actionable, key=lambda x: abs(x.co2_reduction_pct))
    
    if len(sorted_strats) >= 3:
        conservative = sorted_strats[0]
        optimum = sorted_strats[len(sorted_strats)//2]
        ambitious = sorted_strats[-1]
    elif len(sorted_strats) == 2:
        conservative = sorted_strats[0]
        optimum = sorted_strats[1]
        ambitious = sorted_strats[1]
    elif len(sorted_strats) == 1:
        conservative = optimum = ambitious = sorted_strats[0]
    else:
        # Fallback - use first available
        conservative = optimum = ambitious = results_all[0] if results_all else None
    
    # Elegant descriptions
    descriptions = {
        "heritage": "Time-tested methodology. Minimal operational disruption with steady, measurable progress toward sustainability targets.",
        "optimum": "The equilibrium of ambition and pragmatism. Optimal balance of environmental impact and financial return.",
        "frontier": "Bold transformation. Maximum sustainability impact for organizations ready to lead the industry transition."
    }
    
    # Use st.columns for proper layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="triptych-card heritage">
            <div class="triptych-name">{conservative.strategy_name if conservative else "Conservative"}</div>
            <div class="triptych-subtitle">Heritage Approach</div>
            <div class="triptych-desc">{descriptions['heritage']}</div>
            <div class="triptych-metrics">
                <div class="triptych-metric">
                    <div class="triptych-metric-value">-{abs(conservative.co2_reduction_pct) if conservative else 0:.0f}%</div>
                    <div class="triptych-metric-label">CO2</div>
                </div>
                <div class="triptych-metric">
                    <div class="triptych-metric-value">{fmt_currency(conservative.annual_capex_avoidance_eur) if conservative else "€0"}</div>
                    <div class="triptych-metric-label">CAPEX</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="triptych-card optimum">
            <div class="triptych-name">{optimum.strategy_name if optimum else "Balanced"}</div>
            <div class="triptych-subtitle">The Elysia Optimum</div>
            <div class="triptych-desc">{descriptions['optimum']}</div>
            <div class="triptych-metrics">
                <div class="triptych-metric">
                    <div class="triptych-metric-value">-{abs(optimum.co2_reduction_pct) if optimum else 0:.0f}%</div>
                    <div class="triptych-metric-label">CO2</div>
                </div>
                <div class="triptych-metric">
                    <div class="triptych-metric-value">{fmt_currency(optimum.annual_capex_avoidance_eur) if optimum else "€0"}</div>
                    <div class="triptych-metric-label">CAPEX</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="triptych-card frontier">
            <div class="triptych-name">{ambitious.strategy_name if ambitious else "Ambitious"}</div>
            <div class="triptych-subtitle">Frontier Strategy</div>
            <div class="triptych-desc">{descriptions['frontier']}</div>
            <div class="triptych-metrics">
                <div class="triptych-metric">
                    <div class="triptych-metric-value">-{abs(ambitious.co2_reduction_pct) if ambitious else 0:.0f}%</div>
                    <div class="triptych-metric-label">CO2</div>
                </div>
                <div class="triptych-metric">
                    <div class="triptych-metric-value">{fmt_currency(ambitious.annual_capex_avoidance_eur) if ambitious else "€0"}</div>
                    <div class="triptych-metric-label">CAPEX</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # =========================================================================
    # 90-DAY ROADMAP (Minimal)
    # =========================================================================
    st.markdown('<div class="section-title">Implementation Roadmap</div>', unsafe_allow_html=True)
    
    # Build fleet profile for action plan
    fleet_profile = {
        "fleet_size": fleet_size,
        "avg_age": _s("avg_age", 3.5),
        "devices_at_risk": int(fleet_size * 0.3),
        "devices_refurb_eligible": fleet_size,
    }
    
    fleet_insights = _s("fleet_insights")
    if fleet_insights and hasattr(fleet_insights, 'summary'):
        fleet_profile.update({
            "avg_age": fleet_insights.summary.get("avg_age", 3.5),
            "devices_at_risk": fleet_insights.summary.get("devices_at_risk", int(fleet_size * 0.3)),
        })
    
    try:
        action_plan = ActionPlanGenerator.generate(
            strategy=strategy,
            fleet_profile=fleet_profile,
            data_source=data_source,
            confidence=confidence,
        )
        
        for phase in action_plan.phases:
            st.markdown(f"""
            <div class="roadmap-phase">
                <div class="roadmap-phase-header">
                    <div class="roadmap-phase-num">{phase.number}</div>
                    <div class="roadmap-phase-name">{phase.name}</div>
                    <div class="roadmap-phase-time">{phase.subtitle}</div>
                </div>
                <div class="roadmap-milestone">✓ {phase.milestone}</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception:
        # Minimal fallback
        phases = [
            ("1", "Governance & Planning", "Days 1–30", "Vendor selected, pilot scope defined"),
            ("2", "Pilot Deployment", "Days 31–60", "Pilot validated with NPS >8.0"),
            ("3", "Scale & Operationalize", "Days 61–90", "Policy fully operational"),
        ]
        for num, name, time, milestone in phases:
            st.markdown(f"""
            <div class="roadmap-phase">
                <div class="roadmap-phase-header">
                    <div class="roadmap-phase-num">{num}</div>
                    <div class="roadmap-phase-name">{name}</div>
                    <div class="roadmap-phase-time">{time}</div>
                </div>
                <div class="roadmap-milestone">✓ {milestone}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # METHODOLOGY DROPDOWN - Clean text, no raw HTML classes
    # =========================================================================
    with st.expander(" ▼ Understanding the Strategic Logic"):
        st.markdown("#### Financial Methodology")
        
        st.markdown(f"""
**Price Delta Arbitrage**  
The €{roi.annual_capex_avoidance_eur:,.0f} annual optimization derives from the price delta between new and certified refurbished devices. 
Market analysis indicates refurbished enterprise hardware trades at 59% of new acquisition cost while delivering equivalent operational performance.

**Lifecycle Extension Asset Arbitrage**  
By extending the productive lifecycle of IT assets and incorporating certified refurbished units into the procurement mix, 
organizations capture value from the depreciation curve differential—effectively arbitraging the gap between accounting depreciation and actual operational utility.

**Carbon Accounting Basis**  
CO₂ reduction calculations follow GHG Protocol Scope 3 methodology. Manufacturing emissions (365 kg CO₂e per device) represent ~80% of total device lifecycle impact. 
Refurbished procurement avoids 80% of these embodied emissions.

**Return Multiple Calculation**  
The {roi.return_multiple:.0f}x return multiple represents 5-year cumulative CAPEX avoidance (€{roi.five_year_capex_avoidance_eur:,.0f}) 
divided by transition investment (€{roi.transition_cost_eur:,.0f} disposal and change management costs).
        """)
        
        st.markdown("---")
        st.markdown("#### Data Sources")
        st.markdown("""
- **Hardware Pricing**: Gartner IT Asset Management Report 2023
- **Environmental Data**: GHG Protocol Scope 3, Dell Circular Economy Report 2023
- **Grid Carbon Factors**: IEA 2023
        """)
    
    # =========================================================================
    # METHODOLOGY & TRANSPARENCY TAB + DOWNLOADABLE PDF
    # =========================================================================
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Tabs for methodology
    tab1, tab2 = st.tabs(["📊 Executive Summary", "📖 Full Methodology"])
    
    with tab1:
        # Already shown above - just a placeholder
        st.info("Executive summary metrics displayed above.")
    
    with tab2:
        st.markdown("### Complete Methodology & Transparency Report")
        st.markdown("""
This section provides full transparency on how Élysia calculates its recommendations.

#### Calculation Formulas

**Annual CAPEX Avoidance**
```
= (Fleet Size / Refresh Cycle) × Refurb Rate × Price Delta
Where Price Delta = €1,150 (new) - €679 (refurb) = €471
```

**CO₂ Reduction**
```
= Annual Replacements × Refurb Rate × Manufacturing CO₂ × Savings Rate
Where Manufacturing CO₂ = 365 kg, Savings Rate = 80%
```

**Return Multiple (ROI)**
```
= 5-Year CAPEX Avoidance / Transition Cost
Where Transition Cost = €50/device (disposal + change management)
```

#### Confidence Levels
| Level | Data Quality | Description |
|-------|-------------|-------------|
| HIGH | Uploaded fleet data | Actual device inventory |
| MEDIUM | Estimated inputs | Industry benchmarks |
| LOW | Defaults only | Broad averages |

#### Limitations
1. Device pricing based on enterprise averages
2. Not all models available refurbished
3. Productivity estimates from surveys
4. Grid carbon factors are annual averages
        """)
        
        # Full methodology PDF download
        methodology_content = f"""# Élysia Methodology & Transparency Report
Generated: {datetime.now().strftime('%Y-%m-%d')}

## Overview
Élysia is a sustainable IT decision support tool developed for LVMH LIFE 360 compliance.

---

## Financial Calculations

### Price Delta Arbitrage
- Formula: Annual Savings = (Fleet Size / Refresh Cycle) × Refurb Rate × Price Delta
- Price Delta: €1,150 (new) - €679 (refurbished) = €471 per device
- Source: Gartner Enterprise Hardware Pricing 2023

### Return Multiple
- Formula: ROI = 5-Year CAPEX Avoidance / Transition Cost
- Transition Cost: €50/device (disposal + change management)

---

## Carbon Calculations

### Scope 3 Emissions (GHG Protocol)
- Manufacturing Emissions: 365 kg CO₂e per device
- Refurbished Savings Rate: 80%
- Source: Dell Circular Economy Report 2023

### Grid Carbon Factors (kg CO₂/kWh)
- France: 0.052
- Germany: 0.385
- UK: 0.268
- USA: 0.410
(Source: IEA 2023)

---

## Data Sources
- Gartner IT Asset Management Report 2023
- Dell Product Carbon Footprint Studies
- GHG Protocol Scope 3 Guidance
- IEA Grid Carbon Intensity Data 2023

---

## Limitations
1. Device pricing based on enterprise averages
2. Refurbishment availability varies by model
3. Productivity impact estimates from industry surveys
4. Carbon factors are annual averages

---
*Generated by Élysia v2.0 · LVMH Green IT · LIFE 360*
"""
        st.download_button(
            "📥 Download Full Methodology (PDF)",
            data=methodology_content,
            file_name="elysia_methodology.md",
            mime="text/markdown",
            use_container_width=True,
            key=ui_key("action", "methodology_download")
        )
    
    # =========================================================================
    # EXPORT & NAVIGATION
    # =========================================================================
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        report_content = f"""# Élysia Executive Summary
Generated: {datetime.now().strftime('%Y-%m-%d')}

## Selected Strategy: {strategy.strategy_name}

### Key Performance Indicators
- Annual CAPEX Optimization: €{roi.annual_capex_avoidance_eur:,.0f}
- Carbon Reduction: -{co2_pct:.0f}%
- Return Multiple: {roi.return_multiple:.0f}x (5-Year)
- Payback Period: {roi.payback_months} months

### 5-Year Projection
- Cumulative CAPEX Avoidance: €{roi.five_year_capex_avoidance_eur:,.0f}
- CO₂ Avoided: {co2_avoided_5yr:.0f} tonnes

---
*Generated by Élysia · LVMH Sustainable IT Intelligence*
*Where Insight Drives Impact*
"""
        st.download_button("Download Report", data=report_content, file_name="elysia_executive_summary.md", 
                          mime="text/markdown", use_container_width=True, key=ui_key("action", "download"))
    
    with col3:
        if st.button("Start New Analysis", key=ui_key("action", "restart"), use_container_width=True):
            _reset_state()
            st.rerun()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def render_audit_section():
    """Main UI function - entry point for the audit."""
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)
    st.markdown(PART2_CSS, unsafe_allow_html=True)
    inject_credibility_css()
    
    _get_audit_state()
    ok, errors = _sanity_check_backend()
    if not ok:
        st.error("Backend initialization failed:")
        for err in errors:
            st.error(f"• {err}")
        st.stop()
    
    stage = _s("stage", "welcome")
    
    stages = {
        "welcome": render_welcome,
        "calibration": render_calibration,
        "shock": render_shock,
        "hope": render_hope,
        "strategy": render_strategy,
        "upload": render_upload,
        "simulator": render_simulator,
        "policy": render_simulator,  # Alias for old stage name
        "action": render_action,
    }
    
    render_func = stages.get(stage, render_welcome)
    render_func()
    
    st.markdown('<div class="lux-footer"><div class="lux-footer-text">ÉLYSIA · LVMH GREEN IT · LIFE 360<br><span style="font-style:italic; font-size:0.7rem;">Where Insight Drives Impact</span></div></div>', unsafe_allow_html=True)


def run():
    """Alias for main.py compatibility."""
    render_audit_section()


if __name__ == "__main__":
    try:
        st.set_page_config(page_title="Élysia", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")
    except:
        pass
    run()

# --- CSS INJECTION START ---
st.markdown("""
<style>
    /* 1. MAKE THE STRATEGY BOX BIGGER */
    .strategy-summary {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 30px 40px; /* This makes it big */
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .strategy-summary-title {
        color: #666;
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .strategy-summary-name {
        color: #1E1E1E;
        font-size: 36px; /* This makes the text big */
        font-weight: 800;
        margin-bottom: 25px;
        line-height: 1.2;
    }
    .strategy-summary-metrics {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        border-top: 1px solid #ddd;
        padding-top: 20px;
    }
    .strategy-summary-metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 5px;
    }
    .strategy-summary-metric-label {
        font-size: 14px;
        color: #555;
        font-weight: 500;
    }

    /* 2. FIX THE DROPDOWN ARROW */
    div[data-baseweb="select"] > div:nth-child(2) > svg {
        width: 1.5rem !important;
        height: 1.5rem !important;
        fill: #444 !important;
    }
</style>
""", unsafe_allow_html=True)
# --- CSS INJECTION END ---