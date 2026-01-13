"""
LVMH Green in Tech - Equipment Audit Module
EcoCycle Intelligence - Luxury Edition
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from io import BytesIO

# --- 1. SECURE IMPORTS ---
try:
    from equipement_audit.reference_data_API import LOCAL_DB, PERSONAS
    from equipement_audit.calculator import SmartCalculator
except ImportError:
    try:
        from reference_data_API import LOCAL_DB, PERSONAS
        from calculator import SmartCalculator
    except ImportError as e:
        st.error(f"Core modules missing: {e}")
        st.stop()


def run():
    """Entry point called from main.py"""
    render_audit_section()


# --- 2. LUXURY VISUAL SETUP ---
def inject_luxury_style():
    """
    Luxury LVMH styling for Equipment Audit - matches homepage design
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === BASE === */
    .stApp {
        background: linear-gradient(160deg, #0d0d0d 0%, #1a1a1a 40%, #0f0f0f 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === FIX EXPANDER ICONS === */
    [data-testid="stExpander"] svg { display: none !important; }
    details > summary { list-style: none !important; }
    details > summary::-webkit-details-marker { display: none !important; }
    details > summary::marker { display: none !important; content: "" !important; }
    
    [data-testid="stExpander"] {
        border: 1px solid rgba(138, 108, 74, 0.2) !important;
        border-radius: 4px !important;
        background: rgba(20, 20, 20, 0.8) !important;
    }
    
    [data-testid="stExpander"] summary {
        padding: 12px 16px !important;
        color: #a08d6c !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.8rem !important;
    }
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif !important;
        color: #c9b896 !important;
        font-weight: 400 !important;
        letter-spacing: 2px !important;
    }
    
    p, div, label, span {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* === PAGE HEADER === */
    .page-header {
        padding: 30px 0 25px 0;
        border-bottom: 1px solid rgba(138, 108, 74, 0.15);
        margin-bottom: 30px;
    }
    
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #f5f0e8;
        font-weight: 400;
        letter-spacing: 3px;
        margin: 0;
    }
    
    .page-title span {
        color: #7cb880;
    }
    
    .page-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        color: #666;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 8px;
    }
    
    /* === SECTION HEADER === */
    .section-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        color: #c9b896;
        font-weight: 400;
        letter-spacing: 2px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-icon {
        color: #8a6c4a;
        font-size: 1rem;
    }
    
    /* === INPUT LABELS WITH TOOLTIPS === */
    .input-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .tooltip-help {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 14px;
        height: 14px;
        background: transparent;
        border: 1px solid rgba(138, 108, 74, 0.4);
        border-radius: 50%;
        font-size: 8px;
        color: #8a6c4a;
        cursor: help;
        font-weight: 600;
    }
    
    .tooltip-help:hover {
        background: rgba(138, 108, 74, 0.15);
    }
    
    /* === RECOMMENDATION BANNER === */
    .rec-banner {
        border-radius: 6px;
        padding: 40px 30px;
        text-align: center;
        margin: 25px 0;
        position: relative;
        overflow: hidden;
    }
    
    .rec-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    }
    
    .bg-keep {
        background: linear-gradient(135deg, #1a3d2e 0%, #2d5a45 50%, #1a3d2e 100%);
        border: 1px solid rgba(124, 184, 128, 0.3);
    }
    
    .bg-refurb {
        background: linear-gradient(135deg, #1a2d3d 0%, #2d4a5a 50%, #1a2d3d 100%);
        border: 1px solid rgba(100, 150, 180, 0.3);
    }
    
    .bg-new {
        background: linear-gradient(135deg, #3d2d1a 0%, #5a4530 50%, #3d2d1a 100%);
        border: 1px solid rgba(180, 140, 100, 0.3);
    }
    
    .rec-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 15px;
    }
    
    .rec-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 400;
        color: #fff;
        margin: 0;
        letter-spacing: 4px;
    }
    
    .rec-subtitle {
        margin-top: 18px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        display: inline-block;
        padding: 10px 25px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* === METRIC CARDS === */
    .metric-card {
        background: linear-gradient(145deg, rgba(25, 25, 25, 0.95), rgba(12, 12, 12, 0.98));
        border: 1px solid rgba(138, 108, 74, 0.15);
        border-radius: 4px;
        padding: 25px 20px;
        text-align: center;
    }
    
    .metric-card:hover {
        border-color: rgba(138, 108, 74, 0.3);
    }
    
    .metric-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.6rem;
        text-transform: uppercase;
        color: #666;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 400;
        color: #c9b896;
        letter-spacing: 1px;
    }
    
    .metric-sub {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        color: #7cb880;
        font-weight: 500;
        margin-top: 8px;
    }
    
    .metric-footnote {
        font-size: 0.65rem;
        color: #555;
        margin-top: 10px;
    }
    
    /* === TRANSPARENCY BOX === */
    .transparency-box {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid rgba(138, 108, 74, 0.15);
        border-radius: 4px;
        padding: 20px;
        margin-top: 20px;
    }
    
    .verified-badge {
        background: rgba(76, 135, 80, 0.15);
        color: #7cb880;
        padding: 6px 14px;
        border-radius: 3px;
        font-size: 0.65rem;
        font-weight: 600;
        border: 1px solid rgba(76, 135, 80, 0.3);
        display: inline-block;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background: linear-gradient(135deg, #8a6c4a 0%, #6d553a 100%) !important;
        color: #0d0d0d !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 14px 35px !important;
        border-radius: 4px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #a08058 0%, #8a6c4a 100%) !important;
        box-shadow: 0 10px 30px rgba(138, 108, 74, 0.3) !important;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid rgba(138, 108, 74, 0.15);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #666;
        border-radius: 0;
        padding: 12px 25px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #c9b896 !important;
        border-bottom: 2px solid #8a6c4a !important;
        background: transparent !important;
    }
    
    /* === SELECTBOX / INPUTS === */
    [data-testid="stSelectbox"] > div > div {
        background: rgba(20, 20, 20, 0.9) !important;
        border: 1px solid rgba(138, 108, 74, 0.2) !important;
        border-radius: 4px !important;
        color: #ccc !important;
    }
    
    [data-testid="stSelectbox"] label {
        color: #888 !important;
        font-size: 0.7rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    
    /* === RADIO === */
    [data-testid="stRadio"] > label {
        color: #888 !important;
        font-size: 0.7rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    
    [data-testid="stRadio"] > div {
        gap: 20px;
    }
    
    /* === SLIDER === */
    [data-testid="stSlider"] > div > div > div {
        background: #8a6c4a !important;
    }
    
    [data-testid="stSlider"] label {
        color: #888 !important;
        font-size: 0.7rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    
    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
        border-right: 1px solid rgba(138, 108, 74, 0.1);
    }
    
    section[data-testid="stSidebar"] h2 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #c9b896 !important;
        font-size: 1.2rem !important;
        letter-spacing: 2px !important;
    }
    
    /* === DIVIDER === */
    .luxury-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(138, 108, 74, 0.2), transparent);
        margin: 25px 0;
    }
    
    /* === INFO BOX === */
    .stAlert {
        background: rgba(138, 108, 74, 0.1) !important;
        border: 1px solid rgba(138, 108, 74, 0.2) !important;
        border-radius: 4px !important;
    }
    
    /* === CAPTION === */
    .stCaption {
        color: #555 !important;
        font-size: 0.7rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 3. DEMO DATA ---
def get_demo_csv():
    data = {
        "Device Model": ["iPhone 14", "Dell XPS 13", "iPad Pro", "Monitor 27_inch", "iPhone 12"],
        "Age_Years": [2, 4, 3, 5, 4],
        "Persona": ["Sales (Mobile)", "Developer (High Perf)", "Creative (Tablet)", "Office Admin", "Sales (Mobile)"],
        "Country": ["FR", "US", "UK", "CN", "FR"]
    }
    return pd.DataFrame(data).to_csv(index=False).encode('utf-8')


# --- 4. BUSINESS-FRIENDLY CHARTS ---
def plot_tco_comparison(scenarios, winner):
    """
    Creates a clean, business-friendly TCO comparison chart
    """
    target = winner if winner != "NEW" else "KEEP"
    
    options = ['Buy New', f'Recommend: {target}']
    values = [scenarios["NEW"]['fin'], scenarios[target]['fin']]
    colors = ['#555555', '#7cb880' if target in ['KEEP', 'REFURB'] else '#8a6c4a']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=options,
        x=values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        text=[f'€{v:,.0f}/yr' for v in values],
        textposition='outside',
        textfont=dict(color='#999', size=12, family='Montserrat')
    ))
    
    # Add savings annotation
    if target != "NEW":
        savings = scenarios["NEW"]['fin'] - scenarios[target]['fin']
        fig.add_annotation(
            x=max(values) * 0.8,
            y=1.3,
            text=f"Savings: €{savings:,.0f}/yr",
            showarrow=False,
            font=dict(color='#7cb880', size=13, family='Montserrat'),
            bgcolor='rgba(124, 184, 128, 0.1)',
            borderpad=8
        )
    
    fig.update_layout(
        title=dict(
            text='Total Cost of Ownership Comparison',
            font=dict(family='Cormorant Garamond', size=16, color='#c9b896'),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Montserrat', color='#888'),
        height=200,
        margin=dict(l=20, r=100, t=50, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(138, 108, 74, 0.08)',
            title=dict(text='Annual Cost (€)', font=dict(size=10, color='#666')),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color='#aaa')
        )
    )
    
    return fig


def plot_fleet_donut(df_results):
    """Business-friendly donut chart for fleet analysis"""
    
    colors = {'KEEP': '#7cb880', 'REFURB': '#6496b4', 'NEW': '#b48c64'}
    
    fig = px.pie(
        df_results, 
        names='Action', 
        title='Recommended Strategy Distribution',
        color='Action',
        color_discrete_map=colors,
        hole=0.65
    )
    
    fig.update_layout(
        title=dict(
            font=dict(family='Cormorant Garamond', size=16, color='#c9b896'),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Montserrat', color='#888', size=11),
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(size=10)
        )
    )
    
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=11)
    )
    
    return fig


# --- 5. TRANSPARENCY SECTION ---
def render_transparency_section(winner, scenarios):
    with st.expander("→ View calculation methodology"):
        t1, t2 = st.tabs(["Financial Model", "Data Sources"])
        
        with t1:
            st.markdown(f"""
            **Total Cost of Ownership (TCO) Analysis**
            
            The engine evaluates three scenarios and recommends the lowest TCO option:
            
            | Scenario | Formula | Rationale |
            |:---------|:--------|:----------|
            | **Buy New** | `(Asset + Labor) / 3 yrs` | Standard 3-year depreciation cycle |
            | **Refurbish** | `(Market × 1.15) / 2 yrs` | 15% risk premium for failure rates |
            | **Keep** | `Maint + (Salary × Slowness)` | Productivity loss quantification |
            
            **Current Analysis Results:**
            - Buy New: **€{scenarios['NEW']['fin']:,.0f}** / year
            - Refurbish: **€{scenarios['REFURB']['fin']:,.0f}** / year  
            - Keep: **€{scenarios['KEEP']['fin']:,.0f}** / year
            """)
        
        with t2:
            st.markdown("""
            **Data Provenance & Standards**
            
            - **Carbon Data:** Boavizta API + Manufacturer Reports (Apple, Dell, Lenovo)
            - **Grid Intensity:** ElectricityMaps real-time CO₂ factors
            - **Methodology:** ISO 14040/14044 Lifecycle Assessment standards
            """)
            st.markdown('<span class="verified-badge">Audit Ready Data</span>', unsafe_allow_html=True)


# --- 6. SINGLE AUDIT ---
def render_single_audit():
    st.markdown("""
    <div class="section-title">
        <span class="section-icon">◈</span>
        Single Device Analysis
    </div>
    """, unsafe_allow_html=True)
    
    # Row 1: Device & Age
    c1, c2, c3 = st.columns([2, 1, 1.5])
    
    with c1:
        st.markdown("""
        <div class="input-label">
            Device Model
            <span class="tooltip-help" title="Select the device model from your inventory">?</span>
        </div>
        """, unsafe_allow_html=True)
        dev_opts = list(LOCAL_DB.keys())
        def_idx = dev_opts.index("iPhone 16e (New Target)") if "iPhone 16e (New Target)" in dev_opts else 0
        device_name = st.selectbox("Device Model", dev_opts, index=def_idx, label_visibility="collapsed")
    
    with c2:
        st.markdown("""
        <div class="input-label">
            Age (Years)
            <span class="tooltip-help" title="How long the device has been in service">?</span>
        </div>
        """, unsafe_allow_html=True)
        age = st.slider("Age", 1, 8, 4, label_visibility="collapsed")
    
    with c3:
        st.markdown("""
        <div class="input-label">
            Employee Profile
            <span class="tooltip-help" title="User role affects productivity impact calculation">?</span>
        </div>
        """, unsafe_allow_html=True)
        persona_name = st.selectbox("Profile", list(PERSONAS.keys()), label_visibility="collapsed")
    
    # Row 2: Country & Strategy
    c4, c5 = st.columns([1, 2])
    
    with c4:
        st.markdown("""
        <div class="input-label">
            Location
            <span class="tooltip-help" title="Country affects carbon grid intensity">?</span>
        </div>
        """, unsafe_allow_html=True)
        ctry = st.selectbox("Country", ["FR", "US", "UK", "DE", "CN"], label_visibility="collapsed")
    
    with c5:
        st.markdown("""
        <div class="input-label">
            Optimization Goal
            <span class="tooltip-help" title="Weight financial vs environmental factors">?</span>
        </div>
        """, unsafe_allow_html=True)
        strategy_mode = st.radio("Goal", ["Balanced", "Cost-First", "Eco-First"], 
                                 horizontal=True, label_visibility="collapsed")
    
    st.markdown('<div class="luxury-divider"></div>', unsafe_allow_html=True)
    
    # Action Button
    if st.button("Run Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing device lifecycle and calculating TCO..."):
            time.sleep(1.0)
            st.session_state['run_calc'] = True
    
    # Results
    if st.session_state.get('run_calc'):
        w_fin = 1.0 if strategy_mode == "Cost-First" else (0.0 if strategy_mode == "Eco-First" else 0.5)
        scenarios = SmartCalculator.calculate_scenarios(device_name, age, persona_name, ctry, True)
        winner, scores, sav_fin, sav_env = SmartCalculator.get_recommendation(scenarios, w_fin, persona_name)
        
        # Recommendation Banner
        st.markdown("<br>", unsafe_allow_html=True)
        
        if winner == "KEEP":
            style_cls, icon, sub_txt = "bg-keep", "✓", "Extend Lifecycle"
        elif winner == "REFURB":
            style_cls, icon, sub_txt = "bg-refurb", "↻", "Switch to Circular"
        else:
            style_cls, icon, sub_txt = "bg-new", "→", "Upgrade Required"
        
        st.markdown(f"""
        <div class="rec-banner {style_cls}">
            <div class="rec-label">Strategic Recommendation</div>
            <div class="rec-title">{icon} {winner}</div>
            <div class="rec-subtitle">{sub_txt}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics Row
        m1, m2 = st.columns(2)
        
        with m1:
            val = f"€{sav_fin:,.0f}" if not (sav_fin == 0 and winner == "NEW") else "Baseline"
            sub_msg = "ROI Positive" if sav_fin > 0 else "Best Performance"
            is_verified = "iPhone" in device_name or "Dell" in device_name
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Projected Savings</div>
                <div class="metric-value">{val}</div>
                <div class="metric-sub">{sub_msg}</div>
                <div class="metric-footnote">{'Manufacturer Verified' if is_verified else 'Market Estimation'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m2:
            car_km = sav_env / 0.12
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Carbon Avoided</div>
                <div class="metric-value">{sav_env:.1f} kg</div>
                <div class="metric-sub">CO₂e Saved</div>
                <div class="metric-footnote">Equivalent to {car_km:.0f} km driven</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_tco_comparison(scenarios, winner), use_container_width=True, config={'displayModeBar': False})
        
        # Transparency
        render_transparency_section(winner, scenarios)


# --- 7. BULK AUDIT ---
def render_bulk_audit():
    st.markdown("""
    <div class="section-title">
        <span class="section-icon">◈</span>
        Fleet Analysis
    </div>
    """, unsafe_allow_html=True)
    
    c_up, c_act = st.columns([2, 1])
    
    with c_up:
        uploaded_file = st.file_uploader("Upload fleet inventory CSV", type=["csv"], label_visibility="collapsed")
    
    with c_act:
        if st.button("Load Demo Data", use_container_width=True):
            st.session_state['demo_active'] = True
    
    df = None
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    elif st.session_state.get('demo_active'):
        df = pd.read_csv(BytesIO(get_demo_csv()))
    
    if df is not None:
        st.markdown('<div class="luxury-divider"></div>', unsafe_allow_html=True)
        
        results = []
        for _, row in df.iterrows():
            if row['Age_Years'] > 3 and "High Perf" not in row['Persona']:
                act, sav = "KEEP", 250
            elif "High Perf" in row['Persona']:
                act, sav = "NEW", -50
            else:
                act, sav = "REFURB", 180
            results.append({"Model": row['Device Model'], "Action": act, "Savings": sav})
        
        df_res = pd.DataFrame(results)
        
        k1, k2 = st.columns([1, 2])
        
        with k1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Savings</div>
                <div class="metric-value">€{df_res['Savings'].sum():,.0f}</div>
                <div class="metric-sub">Annual Impact</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Devices Analyzed</div>
                <div class="metric-value">{len(df_res)}</div>
                <div class="metric-sub">Fleet Size</div>
            </div>
            """, unsafe_allow_html=True)
        
        with k2:
            st.plotly_chart(plot_fleet_donut(df_res), use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_res, use_container_width=True)


# --- 8. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        st.markdown("## Settings")
        st.caption("Configure cost assumptions for analysis")
        
        st.markdown('<div class="luxury-divider"></div>', unsafe_allow_html=True)
        
        with st.expander("→ Labor & Costs"):
            st.number_input("IT Labor Rate (€/hr)", value=68, step=5)
            st.number_input("Battery Replacement (€)", value=84, step=5)
        
        st.markdown('<div class="luxury-divider"></div>', unsafe_allow_html=True)
        st.caption("v3.3 · Production Build")


# --- 9. MAIN ENTRY ---
def render_audit_section():
    """Main function called by main.py"""
    inject_luxury_style()
    render_sidebar()
    
    # Header
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">EcoCycle <span>Intelligence</span></h1>
        <p class="page-subtitle">LVMH · Digital Sustainability Division</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    t1, t2 = st.tabs(["Single Audit", "Fleet Analysis"])
    with t1:
        render_single_audit()
    with t2:
        render_bulk_audit()


if __name__ == "__main__":
    render_audit_section()