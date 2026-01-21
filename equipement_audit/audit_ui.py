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
    sizes = {"small": "40px", "medium": "64px", "large": "80px", "hero": "100px"}
    icon_size = sizes.get(size, sizes["medium"])
    logo_b64 = _get_logo_base64("logo.png/elysia_logo.png")
    if logo_b64:
        return f'<div style="display:flex; align-items:center; justify-content:center;"><img src="data:image/png;base64,{logo_b64}" style="height:{icon_size}; width:auto;" alt="Élysia"/></div>'
    return f'<div style="text-align:center;"><span style="font-family:\'Playfair Display\',Georgia,serif; font-size:2rem; font-weight:500; color:#8a6c4a; letter-spacing:0.08em;">ÉLYSIA</span></div>'


# =============================================================================
# CSS
# =============================================================================

LUXURY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
:root { --cream: #FAFAF8; --warm-white: #F5F3EF; --white: #FFFFFF; --border: #E8E4DD; --gold: #8a6c4a; --gold-light: #a8896a; --gold-dark: #6d5539; --text-dark: #2D2A26; --text-mid: #6B6560; --text-light: #9A958E; --success: #4A7C59; --success-bg: #E8F5E9; --danger: #9E4A4A; --danger-bg: #FFEBEE; --warning: #C4943A; --warning-bg: #FFF8E1; --info: #5B7B9A; --info-bg: #E3F2FD; --shadow-md: 0 4px 16px rgba(0,0,0,0.06); --shadow-gold: 0 4px 20px rgba(138, 108, 74, 0.12); }
.stApp { background: var(--cream) !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; display: none !important; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--text-dark) !important; font-weight: 500 !important; }
h1 { font-size: 2.75rem !important; } h2 { font-size: 2rem !important; } h3 { font-size: 1.5rem !important; }
p, span, div, label, li { font-family: 'Inter', sans-serif !important; line-height: 1.7 !important; }
.lux-header { background: linear-gradient(180deg, var(--white) 0%, var(--cream) 100%); border-bottom: 1px solid var(--border); padding: 1.25rem 0 1rem 0; margin-bottom: 2rem; text-align: center; }
.lux-header-sub { font-size: 0.75rem; color: var(--text-light); letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.5rem; }
.hero-container { min-height: 65vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 3rem 2rem; background: linear-gradient(180deg, var(--white) 0%, var(--cream) 40%, var(--warm-white) 100%); }
.hero-tagline { font-size: 1.5rem; font-weight: 400; color: var(--text-dark); line-height: 1.6; max-width: 650px; margin-bottom: 1rem; margin-top: 2rem; }
.hero-tagline strong { color: var(--gold); font-weight: 600; }
.hero-subtitle { font-size: 1rem; color: var(--text-mid); max-width: 550px; line-height: 1.6; margin-bottom: 2.5rem; }
.hero-trust { font-size: 0.7rem; color: var(--text-light); letter-spacing: 0.15em; text-transform: uppercase; margin-top: 2.5rem; padding-top: 2rem; border-top: 1px solid var(--border); }
.step-badge { display: inline-block; font-size: 0.6rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); background: var(--warm-white); border: 1px solid var(--border); padding: 0.5rem 1.75rem; border-radius: 30px; margin-bottom: 1.25rem; }
.progress-container { display: flex; justify-content: center; align-items: center; margin-bottom: 2rem; gap: 4px; }
.progress-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--border); transition: all 0.3s ease; }
.progress-dot.active { background: var(--gold); box-shadow: 0 0 0 4px rgba(138, 108, 74, 0.15); width: 12px; height: 12px; }
.progress-dot.completed { background: var(--success); }
.progress-line { width: 32px; height: 2px; background: var(--border); }
.progress-line.completed { background: var(--success); }
.metric-card { background: var(--white); border: 1px solid var(--border); border-radius: 20px; padding: 2rem 1.5rem; text-align: center; box-shadow: var(--shadow-md); height: 100%; }
.metric-card-value { font-family: 'Playfair Display', serif !important; font-size: 2.5rem; font-weight: 500; color: var(--text-dark); margin-bottom: 0.5rem; }
.metric-card-value.gold { color: var(--gold); }
.metric-card-value.success { color: var(--success); }
.metric-card-value.danger { color: var(--danger); }
.metric-card-label { font-size: 0.9rem; color: var(--text-mid); }
.metric-card-logic { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); text-align: left; }
.metric-card-logic-title { font-size: 0.7rem; font-weight: 600; color: var(--gold); text-transform: uppercase; margin-bottom: 0.5rem; }
.metric-card-logic-list { font-size: 0.8rem; color: var(--text-mid); line-height: 1.7; margin: 0; padding-left: 1rem; }
.metric-card-logic-source { font-size: 0.7rem; font-style: italic; color: var(--text-light); margin-top: 0.5rem; }
.compare-card { border: 2px solid var(--border); border-radius: 24px; padding: 2rem 1.5rem; text-align: center; background: var(--white); box-shadow: var(--shadow-md); }
.compare-card.current { background: linear-gradient(135deg, #FFF5F5 0%, #FFEBEE 100%); border-color: var(--danger); }
.compare-card.target { background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 100%); border-color: var(--success); }
.compare-badge { display: inline-block; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.4rem 1rem; border-radius: 20px; margin-bottom: 1rem; }
.compare-card.current .compare-badge { background: var(--danger); color: white; }
.compare-card.target .compare-badge { background: var(--success); color: white; }
.compare-value { font-family: 'Playfair Display', serif !important; font-size: 2.25rem; font-weight: 500; color: var(--text-dark); margin: 0.5rem 0; }
.compare-label { font-size: 0.85rem; color: var(--text-mid); }
.compare-arrow { display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: var(--gold); }
.stats-row { display: flex; justify-content: center; gap: 4rem; margin: 2rem 0; flex-wrap: wrap; }
.stat-item { text-align: center; }
.stat-value { font-family: 'Playfair Display', serif !important; font-size: 2rem; font-weight: 500; color: var(--success); }
.stat-label { font-size: 0.7rem; color: var(--text-mid); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }
.strategy-card { background: var(--white); border: 2px solid var(--border); border-radius: 24px; padding: 2rem 1.5rem; text-align: center; height: 100%; position: relative; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.strategy-card.conservative { border-left: 5px solid var(--success); }
.strategy-card.recommended { border: 3px solid var(--gold); background: linear-gradient(180deg, #FFFCF8 0%, #FFF9F0 100%); box-shadow: var(--shadow-gold); }
.strategy-card.recommended::before { content: 'RECOMMENDED'; position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%); color: white; font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em; padding: 0.4rem 1.25rem; border-radius: 20px; }
.strategy-card.ambitious { border-left: 5px solid var(--warning); }
.strategy-card-title { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; margin-top: 0.75rem; }
.strategy-card-desc { font-size: 0.85rem; color: var(--text-mid); margin-bottom: 1.25rem; min-height: 2.5rem; }
.strategy-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1.25rem; }
.strategy-metric { background: var(--warm-white); border-radius: 10px; padding: 0.6rem 0.4rem; }
.strategy-metric-value { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; color: var(--text-dark); }
.strategy-metric-label { font-size: 0.6rem; color: var(--text-light); text-transform: uppercase; }
.strategy-risk { display: inline-block; font-size: 0.6rem; font-weight: 600; padding: 0.3rem 0.9rem; border-radius: 20px; margin-bottom: 0.75rem; }
.strategy-risk.low { background: var(--success-bg); color: var(--success); }
.strategy-risk.medium { background: var(--warning-bg); color: var(--warning); }
.strategy-risk.high { background: var(--danger-bg); color: var(--danger); }
.strategy-why { font-size: 0.8rem; color: var(--text-mid); padding-top: 0.75rem; border-top: 1px solid var(--border); margin-top: 0.75rem; text-align: left; }
.legend-box { background: var(--warm-white); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.5rem; margin: 1.5rem auto; max-width: 800px; }
.legend-title { font-size: 0.7rem; font-weight: 600; color: var(--gold); text-transform: uppercase; margin-bottom: 0.75rem; }
.legend-items { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.legend-item { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.85rem; color: var(--text-mid); }
.legend-item strong { color: var(--text-dark); white-space: nowrap; }
.roi-section { background: var(--white); border: 1px solid var(--border); border-radius: 20px; padding: 2rem; margin: 2rem 0; }
.roi-title { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; color: var(--text-dark); text-align: center; margin-bottom: 1.5rem; }
.stButton > button { font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important; font-weight: 500 !important; background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 0.85rem 2rem !important; box-shadow: 0 4px 12px rgba(138, 108, 74, 0.25) !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(138, 108, 74, 0.35) !important; }
.stDownloadButton > button { background: transparent !important; color: var(--gold) !important; border: 2px solid var(--gold) !important; box-shadow: none !important; }
.lux-footer { text-align: center; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid var(--border); }
.lux-footer-text { font-size: 0.6rem; color: var(--text-light); letter-spacing: 0.2em; text-transform: uppercase; }
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
    st.markdown(f'<div class="hero-container">{_get_logo_html("hero")}<div class="hero-tagline">Reduce your IT fleet\'s carbon footprint by <strong>30-50%</strong><br>while cutting procurement costs.</div><div class="hero-subtitle">Data-driven sustainable IT strategy, powered by LVMH LIFE 360 methodology.</div></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Begin Your Analysis", key=ui_key("welcome", "begin"), use_container_width=True):
            safe_goto("calibration")
        st.markdown("<p style='text-align:center; font-size:0.8rem; color:#9A958E; margin:1rem 0;'>— or —</p>", unsafe_allow_html=True)
        if st.button("I have fleet data - Skip to Upload", key=ui_key("welcome", "skip"), use_container_width=True):
            _update({"fleet_size": 10000})
            safe_goto("upload")
    st.markdown('<div class="hero-trust">Trusted by LVMH Maisons · Backed by Industry Research</div>', unsafe_allow_html=True)


# =============================================================================
# STEP 1: CALIBRATION
# =============================================================================

def render_calibration():
    render_header()
    render_progress(0)
    render_step_badge(1, "CALIBRATION")
    st.markdown("<h2 style='text-align:center;'>Calibrate Your Baseline</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6B6560;'>Answer a few questions to personalize your analysis.</p>", unsafe_allow_html=True)
    geo_options = _get_geo_options()
    refresh_map = {"20": 5, "25": 4, "30": 3}
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(ui_key("calibration", "form")):
            st.markdown("**1. Fleet size**")
            fleet_choice = st.selectbox("Fleet", options=["— Select —"] + list(FLEET_SIZE_OPTIONS.keys()), format_func=lambda x: x if x == "— Select —" else f"{FLEET_SIZE_OPTIONS[x]['label']} — {FLEET_SIZE_OPTIONS[x]['description']}", key=ui_key("calibration", "fleet"), label_visibility="collapsed")
            st.markdown("**2. Refresh rate** *(% replaced per year)*")
            refresh_choice = st.selectbox("Refresh", options=["— Select —", "20% (5-year cycle)", "25% (4-year cycle)", "30% (3-year cycle)"], key=ui_key("calibration", "refresh"), label_visibility="collapsed")
            st.markdown("**3. Primary geography**")
            geo_choice = st.selectbox("Geography", options=["— Select —"] + list(geo_options.keys()), format_func=lambda x: x if x == "— Select —" else geo_options.get(x, x), key=ui_key("calibration", "geo"), label_visibility="collapsed")
            st.markdown("**4. Current refurbished adoption** *(optional)*")
            refurb_pct = st.slider("Current %", 0, 40, 0, 5, key=ui_key("calibration", "refurb")) / 100.0
            st.markdown("**5. Sustainability target** *(optional)*")
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
    
    st.markdown("<h2 style='text-align:center;'>If you do nothing...</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    sc, cc = shock.stranded_calculation, shock.co2_calculation
    
    with col1:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-card-value gold">{fmt_currency(shock.stranded_value_eur)}</div>
            <div class="metric-card-label">stranded in aging devices</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">How we calculated this</div>
                <ul class="metric-card-logic-list">
                    <li>Fleet: <strong>{sc.get("fleet_size", fleet_size):,}</strong> devices</li>
                    <li>Avg price: <strong>€{sc.get("avg_price", 1150):,.0f}</strong></li>
                    <li>Remaining value: <strong>{sc.get("remaining_value_pct", 0.35)*100:.0f}%</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: Gartner IT Asset Depreciation 2023</div>
            </div>
        </div>''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-card-value gold">{shock.avoidable_co2_tonnes:,.0f}t</div>
            <div class="metric-card-label">avoidable CO2 / year</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">How we calculated this</div>
                <ul class="metric-card-logic-list">
                    <li>Replacements: <strong>{cc.get("annual_replacements", 3125):,.0f}</strong>/year</li>
                    <li>Refurb potential: <strong>{cc.get("effective_refurb_rate", 0.4)*100:.0f}%</strong></li>
                    <li>CO2 savings rate: <strong>{cc.get("savings_rate", 0.8)*100:.0f}%</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: Dell Circular Economy Report 2023</div>
            </div>
        </div>''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-card-value danger">2026</div>
            <div class="metric-card-label">LIFE 360 deadline at risk</div>
            <div class="metric-card-logic">
                <div class="metric-card-logic-title">LIFE 360 Commitment</div>
                <ul class="metric-card-logic-list">
                    <li>Target: <strong>{target_pct}%</strong> CO2 by 2026</li>
                    <li>Trajectory: <strong style="color:#9E4A4A;">WILL MISS</strong></li>
                </ul>
                <div class="metric-card-logic-source">Source: LVMH LIFE 360 Program</div>
            </div>
        </div>''', unsafe_allow_html=True)
    
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
    
    st.markdown("<h2 style='text-align:center; color:#4A7C59;'>But there's another path...</h2>", unsafe_allow_html=True)
    
    # Comparison cards
    col1, col2, col3 = st.columns([5, 1, 5])
    with col1:
        st.markdown(f'''<div class="compare-card current">
            <span class="compare-badge">CURRENT TRAJECTORY</span>
            <div class="compare-value">{hope.current_co2_tonnes:,.0f}t</div>
            <div class="compare-label">CO2 per year</div>
            <div style="height:0.75rem;"></div>
            <div class="compare-value">{fmt_currency(hope.current_cost_eur)}</div>
            <div class="compare-label">Annual cost</div>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="compare-arrow">→</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="compare-card target">
            <span class="compare-badge">WITH ÉLYSIA</span>
            <div class="compare-value">{hope.target_co2_tonnes:,.0f}t</div>
            <div class="compare-label">CO2 per year</div>
            <div style="height:0.75rem;"></div>
            <div class="compare-value">{fmt_currency(hope.target_cost_eur)}</div>
            <div class="compare-label">Annual cost</div>
        </div>''', unsafe_allow_html=True)
    
    # Stats row
    time_text = fmt_time(hope.months_to_target)
    st.markdown(f'''<div class="stats-row">
        <div class="stat-item"><div class="stat-value">-{abs(hope.co2_reduction_pct):.0f}%</div><div class="stat-label">CO2 Reduction</div></div>
        <div class="stat-item"><div class="stat-value">{fmt_currency(hope.cost_savings_eur)}</div><div class="stat-label">Annual Savings</div></div>
        <div class="stat-item"><div class="stat-value">{time_text}</div><div class="stat-label">Time to Target</div></div>
    </div>''', unsafe_allow_html=True)
    
    
    # --- ÉTAPE 1 : Définir la disponibilité (à mettre au début ou juste ici) ---
    try:
    # On vérifie si ta classe existe bien
        ROI_AVAILABLE = 'SimpleROICalculator' in globals() or 'SimpleROICalculator' in locals()
    except NameError:
        ROI_AVAILABLE = False

    if ROI_AVAILABLE:
        st.markdown("---")
        st.markdown('<div class="roi-section"><div class="roi-title">Financial Potential</div>', unsafe_allow_html=True)
        
        # Le calcul doit être indenté (4 espaces)
        roi_data = SimpleROICalculator.calculate(
            fleet_size=fleet_size,
            refresh_cycle_years=float(refresh_cycle),
            refurb_rate=0.40, 
            current_refurb_rate=current_refurb,
        )
        
        # Les colonnes doivent être indentées
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Potential 5-Year Savings", f"€{roi_data.five_year_savings_eur:,.0f}")
        with m2:
            annual_impact = roi_data.five_year_savings_eur / 5
            st.metric("Estimated Annual Impact", f"€{annual_impact:,.0f}")
        
        # L'expander doit être indenté
        with st.expander("How we estimate these savings"):
            st.markdown("Hardware savings (CAPEX) based on Price Delta and Lifespan.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- BOUTON DE NAVIGATION (Sorti du "if" pour être toujours visible) ---

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
                        <div class="strategy-metric-value">{fmt_currency(strat.annual_savings_eur)}</div>
                        <div class="strategy-metric-label">Savings</div>
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
            "Savings": fmt_currency(r.annual_savings_eur),
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
.insight-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
.insight-card { background: var(--white); border: 1px solid var(--border); border-radius: 16px; padding: 1.25rem; border-left: 4px solid var(--success); }
.insight-title { font-family: 'Playfair Display', serif; font-size: 0.95rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; }
.insight-text { font-size: 0.8rem; color: var(--text-mid); margin-bottom: 0.75rem; }
.insight-value { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 600; color: var(--success); }

.simulator-card { background: var(--white); border: 1px solid var(--border); border-radius: 20px; padding: 2rem; margin: 1.5rem 0; }
.simulator-title { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; }
.simulator-subtitle { font-size: 0.85rem; color: var(--text-mid); margin-bottom: 1.5rem; }
.simulator-result { background: var(--success-bg); border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem; text-align: center; }
.simulator-result-title { font-size: 0.7rem; font-weight: 600; color: var(--success); text-transform: uppercase; margin-bottom: 0.5rem; }
.simulator-result-value { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 600; color: var(--success); }

.strategy-summary { background: linear-gradient(135deg, var(--warm-white) 0%, var(--cream) 100%); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; }
.strategy-summary-title { font-size: 0.7rem; font-weight: 600; color: var(--gold); text-transform: uppercase; margin-bottom: 0.75rem; }
.strategy-summary-name { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; }
.strategy-summary-metrics { display: flex; gap: 2rem; margin-top: 1rem; }
.strategy-summary-metric { text-align: center; }
.strategy-summary-metric-value { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 600; color: var(--success); }
.strategy-summary-metric-label { font-size: 0.7rem; color: var(--text-mid); text-transform: uppercase; }

.plan-phase { background: var(--white); border: 1px solid var(--border); border-radius: 20px; padding: 1.5rem; margin-bottom: 1rem; }
.plan-phase-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }
.plan-phase-number { width: 44px; height: 44px; background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; }
.plan-phase-title { font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 600; color: var(--text-dark); }
.plan-phase-subtitle { font-size: 0.7rem; color: var(--text-light); text-transform: uppercase; }
.plan-phase-tasks { margin: 0; padding-left: 1.25rem; color: var(--text-mid); font-size: 0.85rem; line-height: 1.8; }

.business-value-card { background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E9 100%); border: 2px solid var(--success); border-radius: 20px; padding: 2rem; margin: 1.5rem 0; text-align: center; }
.business-value-title { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; color: var(--text-dark); margin-bottom: 1.5rem; }
.business-value-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.business-value-item { }
.business-value-item-value { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 600; color: var(--success); }
.business-value-item-label { font-size: 0.8rem; color: var(--text-mid); margin-top: 0.25rem; }

.roi-card { background: var(--white); border: 1px solid var(--border); border-radius: 20px; padding: 2rem 1.5rem; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
.roi-card-value { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 500; color: var(--success); margin-bottom: 0.5rem; }
.roi-card-label { font-size: 0.9rem; color: var(--text-mid); }
</style>
"""


# =============================================================================
# STEP 5: UPLOAD DATA
# =============================================================================

def render_upload():
    render_header()
    render_progress(4)
    render_step_badge(5, "UPLOAD DATA")
    st.markdown("<h2 style='text-align:center;'>Increase Your Confidence</h2>", unsafe_allow_html=True)
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
        
        # Executive Summary
        st.markdown("### Executive Summary")
        fleet_size = len(df)
        avg_age = df["Age_Years"].mean() if "Age_Years" in df.columns else 3.5
        at_risk = (df["Age_Years"] >= 4).sum() if "Age_Years" in df.columns else int(fleet_size * 0.3)
        at_risk_pct = at_risk / fleet_size * 100 if fleet_size > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fleet Size", f"{fleet_size:,}")
        c2.metric("Avg Age", f"{avg_age:.1f} years")
        c3.metric("At Risk (>4yr)", f"{at_risk_pct:.0f}%")
        c4.metric("Refurb Eligible", "100%")
        
        # Insights - HORIZONTAL layout
        st.markdown("### Key Insights")
        st.markdown(PART2_CSS, unsafe_allow_html=True)
        
        # Calculate insight values
        hidden_cost = at_risk * 450  # €450 productivity cost per at-risk device
        savings_potential = (fleet_size / _s("refresh_cycle", 4)) * 0.4 * 1150 * 0.41  # 41% savings on refurb
        
        st.markdown(f'''
        <div class="insight-grid">
            <div class="insight-card">
                <div class="insight-title">FLEET AGE ABOVE BENCHMARK</div>
                <div class="insight-text">Your fleet is older than industry average, with {at_risk} high-risk devices creating hidden productivity costs.</div>
                <div class="insight-value">€{hidden_cost:,.0f}/year</div>
            </div>
            <div class="insight-card">
                <div class="insight-title">REFURBISHMENT OPPORTUNITY</div>
                <div class="insight-text">{fleet_size} devices (100% of fleet) qualify for refurbished alternatives, unlocking significant savings.</div>
                <div class="insight-value">€{savings_potential:,.0f}/year potential</div>
            </div>
            <div class="insight-card">
                <div class="insight-title">CO2 REDUCTION POTENTIAL</div>
                <div class="insight-text">By adopting refurbished devices, you can significantly reduce your carbon footprint.</div>
                <div class="insight-value">{(fleet_size / _s("refresh_cycle", 4)) * 0.4 * 0.2:.0f}t CO2/year</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Calculation details in dropdown
        with st.expander("View calculation details"):
            st.markdown(f"""
            **Hidden Productivity Cost:**
            - Devices at risk: {at_risk}
            - Cost per device: €450/year
            - Total: €{hidden_cost:,.0f}/year
            - Source: Gartner IT Productivity Study 2023
            
            **Refurbishment Savings:**
            - Annual replacements: {fleet_size / _s("refresh_cycle", 4):.0f}
            - Refurb rate: 40%
            - Price difference: 41% savings
            - Total potential: €{savings_potential:,.0f}/year
            - Source: Back Market Business Pricing 2024
            """)
        
        # ROI card
        try:
    # On vérifie si ta classe existe bien
            ROI_AVAILABLE = 'SimpleROICalculator' in globals() or 'SimpleROICalculator' in locals()
        except NameError:
            ROI_AVAILABLE = False

        if ROI_AVAILABLE:
            st.markdown("### Return on Investment")
            roi_analysis = ROICalculator.generate_complete_analysis(
                fleet_size=fleet_size,
                refresh_cycle_years=float(_s("refresh_cycle", 4)),
                refurb_rate=0.40,
                current_refurb_rate=_s("current_refurb_pct", 0.0),
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                payback = roi_analysis.financial.payback_months
                payback_text = f"{payback} months" if payback < 999 else "N/A"
                st.markdown(f'<div class="roi-card"><div class="roi-card-value">{roi_analysis.financial.roi_percent:+.0f}%</div><div class="roi-card-label">5-Year ROI</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="roi-card"><div class="roi-card-value">{payback_text}</div><div class="roi-card-label">Payback Period</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="roi-card"><div class="roi-card-value">€{roi_analysis.financial.cumulative_5year:,.0f}</div><div class="roi-card-label">5-Year Net Benefit</div></div>', unsafe_allow_html=True)
        
        st.success(f"Confidence upgraded: **MEDIUM** → **HIGH** (based on uploaded data)")
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key=ui_key("upload", "back")):
            safe_goto("strategy")
    with col2:
        btn_text = "Continue with Fleet Data" if df is not None else "Skip - Use Estimates"
        if st.button(btn_text, key=ui_key("upload", "next"), use_container_width=True):
            safe_goto("simulator")


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
                <div class="strategy-summary-metric-value">{fmt_currency(strategy.annual_savings_eur)}</div>
                <div class="strategy-summary-metric-label">Annual Savings</div>
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
    render_step_badge(7, "ACTION PLAN")
    
    strategy = _s("selected_strategy")
    if not strategy:
        st.error("No strategy selected. Please start over.")
        if st.button("Start Over", key=ui_key("action", "restart_err")):
            _reset_state()
            st.rerun()
        return
    
    df = _s("fleet_data")
    data_source = "uploaded" if df is not None else "estimates"
    confidence = "HIGH" if data_source == "uploaded" else "MEDIUM"
    fleet_size = len(df) if df is not None else _s("fleet_size", 12500)
    
    # Get strategy metrics
    details = strategy.calculation_details or {}
    refurb_rate = details.get("strategy", {}).get("refurb_rate", 0.4)
    co2_pct = abs(strategy.co2_reduction_pct)
    savings = strategy.annual_savings_eur
    time_text = fmt_time(strategy.time_to_target_months)
    
    st.markdown(PART2_CSS, unsafe_allow_html=True)
    
    # Basis box
    st.markdown(f'''
    <div class="strategy-summary">
        <div class="strategy-summary-title">This Plan is Based On</div>
        <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 0.5rem;">
            <div>Strategy: <strong>{strategy.strategy_name}</strong></div>
            <div>Data: <strong>{"Uploaded Fleet" if data_source == "uploaded" else "Estimates"}</strong></div>
            <div>Fleet: <strong>{fleet_size:,} devices</strong></div>
            <div>Confidence: <strong>{confidence}</strong></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Business Value Summary
    st.markdown("### Total Business Value (5-Year)")
    
    try:
    # On vérifie si ta classe existe bien
        ROI_AVAILABLE = 'SimpleROICalculator' in globals() or 'SimpleROICalculator' in locals()
    except NameError:
        ROI_AVAILABLE = False

    if ROI_AVAILABLE:
        inject_roi_css()
        roi_analysis = ROICalculator.generate_complete_analysis(
            fleet_size=fleet_size,
            refresh_cycle_years=float(_s("refresh_cycle", 4)),
            refurb_rate=float(refurb_rate),
            current_refurb_rate=_s("current_refurb_pct", 0.0),
        )
        
        # Calculate CO2
        annual_replacements = fleet_size / _s("refresh_cycle", 4)
        co2_avoided = annual_replacements * refurb_rate * 0.2 * 5  # 5 years, 0.2t per device
        
        payback = roi_analysis.financial.payback_months
        payback_text = f"{payback} mo" if payback < 999 else "N/A"
        
        st.markdown(f'''
        <div class="business-value-card">
            <div class="business-value-grid">
                <div class="business-value-item">
                    <div class="business-value-item-value">€{roi_analysis.financial.cumulative_5year:,.0f}</div>
                    <div class="business-value-item-label">Net Savings</div>
                </div>
                <div class="business-value-item">
                    <div class="business-value-item-value">{co2_avoided:.0f}t</div>
                    <div class="business-value-item-label">CO2 Avoided</div>
                </div>
                <div class="business-value-item">
                    <div class="business-value-item-value">{payback_text}</div>
                    <div class="business-value-item-label">Payback</div>
                </div>
            </div>
            <div style="margin-top: 1.5rem; font-size: 1rem; color: var(--text-dark);">
                <strong>{roi_analysis.headline}</strong>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # ROI Details in expander
        with st.expander("View detailed ROI breakdown"):
            render_roi_detailed_breakdown(roi_analysis)
            render_5year_projection(roi_analysis)
    else:
        # Fallback without ROI
        st.markdown(f'''
        <div class="business-value-card">
            <div class="business-value-grid">
                <div class="business-value-item">
                    <div class="business-value-item-value">{fmt_currency(savings * 5)}</div>
                    <div class="business-value-item-label">5-Year Savings</div>
                </div>
                <div class="business-value-item">
                    <div class="business-value-item-value">-{co2_pct:.0f}%</div>
                    <div class="business-value-item-label">CO2 Reduction</div>
                </div>
                <div class="business-value-item">
                    <div class="business-value-item-value">{time_text}</div>
                    <div class="business-value-item-label">Time to Target</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Projected Outcomes
    st.markdown("### Projected Outcomes")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CO2 Reduction", f"-{co2_pct:.0f}%")
    c2.metric("Annual Savings", fmt_currency(savings))
    c3.metric("Time to Target", time_text)
    c4.metric("Confidence", confidence)
    
    # 90-Day Roadmap
    st.markdown("### 90-Day Execution Roadmap")
    
    phases = [
        ("1", "Governance & Planning", "Days 1-30", [
            f"Form steering committee: IT + Procurement + CSR + Finance representatives",
            f"Complete baseline assessment: {fleet_size:,} total devices, identify priority categories",
            "Evaluate and select certified refurbished vendors (Back Market, Recommerce, etc.)",
            "Define success metrics and tracking dashboard"
        ], "Vendor contract signed"),
        ("2", "Pilot Deployment", "Days 31-60", [
            f"Deploy pilot batch of 50-100 refurbished devices to volunteer groups",
            "Implement tracking dashboard for device performance and user satisfaction",
            "Document support procedures and create internal FAQ",
            "Collect user feedback and address concerns"
        ], "Pilot success metrics validated"),
        ("3", "Scale & Operationalize", "Days 61-90", [
            f"Expand procurement policy to cover {int(refurb_rate*100)}% refurbished target",
            "Train IT support team on refurbished device handling",
            "Launch internal communication campaign highlighting sustainability benefits",
            "Set up quarterly review process for continuous improvement"
        ], "Policy fully operational"),
    ]
    
    for num, name, subtitle, tasks, milestone in phases:
        st.markdown(f'''
        <div class="plan-phase">
            <div class="plan-phase-header">
                <div class="plan-phase-number">{num}</div>
                <div>
                    <div class="plan-phase-title">{name}</div>
                    <div class="plan-phase-subtitle">{subtitle}</div>
                </div>
            </div>
            <ul class="plan-phase-tasks">
                {"".join(f"<li>{t}</li>" for t in tasks)}
            </ul>
            <div style="background: var(--success-bg); border-radius: 10px; padding: 0.75rem 1rem; margin-top: 1rem; font-size: 0.8rem;">
                <strong style="color: var(--success);">Key Milestone:</strong> {milestone}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Success Metrics
    st.markdown("### Success Metrics Dashboard")
    metrics_df = pd.DataFrame([
        {"Metric": "Refurbished adoption rate", "Target": f"{int(refurb_rate*100)}%", "Owner": "Procurement", "Frequency": "Monthly"},
        {"Metric": "Device failure rate", "Target": "< 1.5%", "Owner": "IT Operations", "Frequency": "Monthly"},
        {"Metric": "User satisfaction (NPS)", "Target": "> 8.0", "Owner": "HR", "Frequency": "Quarterly"},
        {"Metric": "Cost savings vs budget", "Target": fmt_currency(savings), "Owner": "Finance", "Frequency": "Quarterly"},
        {"Metric": "CO2 reduction", "Target": f"-{co2_pct:.0f}%", "Owner": "CSR", "Frequency": "Quarterly"},
    ])
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Export
    st.markdown("### Export Your Strategy")
    c1, c2 = st.columns(2)
    
    # Build report content
    try:
    # On vérifie si ta classe existe bien
        ROI_AVAILABLE = 'SimpleROICalculator' in globals() or 'SimpleROICalculator' in locals()
    except NameError:
        ROI_AVAILABLE = False
    if ROI_AVAILABLE:
        report_content = f"""# Élysia Strategy Report
Generated: {datetime.now().strftime('%Y-%m-%d')}

## Strategy: {strategy.strategy_name}

### Key Metrics
- CO2 Reduction: {co2_pct:.0f}%
- Annual Savings: €{savings:,.0f}
- Time to Target: {time_text}
- Confidence: {confidence}

### Financial ROI (5-Year)
- ROI: {roi_analysis.financial.roi_percent:+.0f}%
- Payback Period: {payback_text}
- Total Investment: €{roi_analysis.financial.total_investment:,.0f}
- Annual Benefits: €{roi_analysis.financial.annual_benefits:,.0f}
- 5-Year Net Benefit: €{roi_analysis.financial.cumulative_5year:,.0f}

### Business Value
{roi_analysis.headline}

### Recommendation
{roi_analysis.recommendation}

---
*Generated by Élysia · LVMH Green IT · LIFE 360*
"""
    else:
        report_content = f"""# Élysia Strategy Report
Generated: {datetime.now().strftime('%Y-%m-%d')}

## Strategy: {strategy.strategy_name}

### Key Metrics
- CO2 Reduction: {co2_pct:.0f}%
- Annual Savings: €{savings:,.0f}
- Time to Target: {time_text}
- Confidence: {confidence}

---
*Generated by Élysia · LVMH Green IT · LIFE 360*
"""
    
    with c1:
        st.download_button("Download Report (Markdown)", data=report_content, file_name="elysia_strategy_report.md", mime="text/markdown", use_container_width=True, key=ui_key("action", "download_md"))
    with c2:
        csv_data = pd.DataFrame([{
            "Strategy": strategy.strategy_name,
            "CO2_Reduction": f"{co2_pct:.1f}%",
            "Annual_Savings_EUR": savings,
            "Time_Months": strategy.time_to_target_months,
            "Confidence": confidence,
            "Fleet_Size": fleet_size,
        }]).to_csv(index=False)
        st.download_button("Download Data (CSV)", data=csv_data, file_name="elysia_strategy.csv", mime="text/csv", use_container_width=True, key=ui_key("action", "download_csv"))
    
    # Methodology
    with st.expander("Methodology & Sources"):
        render_methodology_tab()
    
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
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
    
    st.markdown('<div class="lux-footer"><div class="lux-footer-text">ÉLYSIA · LVMH GREEN IT · LIFE 360</div></div>', unsafe_allow_html=True)


def run():
    """Alias for main.py compatibility."""
    render_audit_section()


if __name__ == "__main__":
    try:
        st.set_page_config(page_title="Élysia", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")
    except:
        pass
    run()



if __name__ == "__main__":
    import streamlit as st
    try:
        st.set_page_config(page_title="Élysia", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")
    except:
        pass
    run()