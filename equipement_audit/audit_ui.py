"""
LVMH Green in Tech - Equipment Audit UI
========================================

IMPROVED VERSION:
- Killer stat updates dynamically with inputs
- Better "business-friendly" graph
- Clear ranking logic

Author: Green in Tech Team
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from io import BytesIO

# =============================================================================
# IMPORTS - Data and Logic from other modules
# =============================================================================

try:
    from equipement_audit.reference_data_API import (
        LOCAL_DB, PERSONAS, get_data_sources_summary,
        REFURB_CONFIG, DEPRECIATION_CURVE, STRATEGY_CONFIG
    )
    from equipement_audit.calculator import (
        TCOCalculator, UrgencyCalculator, StrategySimulator,
        FleetAnalyzer
    )
except ImportError:
    from reference_data_API import (
        LOCAL_DB, PERSONAS, get_data_sources_summary,
        REFURB_CONFIG, DEPRECIATION_CURVE, STRATEGY_CONFIG
    )
    from calculator import (
        TCOCalculator, UrgencyCalculator, StrategySimulator,
        FleetAnalyzer
    )

# Get dropdown options from data
DEVICE_OPTIONS = list(LOCAL_DB.keys())
PERSONA_OPTIONS = list(PERSONAS.keys())


def run():
    """Entry point from main.py"""
    render_audit_page()


# =============================================================================
# DYNAMIC KILLER STAT CALCULATOR
# =============================================================================

def calculate_killer_stats(fleet_size, current_co2, target_pct):
    """
    Calculate the killer stats DYNAMICALLY based on user inputs.
    
    This updates the banner at the top when user changes values.
    
    LOGIC EXPLAINED:
    ================
    
    1. STRANDED VALUE (€):
       - Each device has resale value based on age
       - Average device is ~4 years old → 20% of original value remains
       - Formula: fleet_size × avg_price × depreciation_rate
       - Example: 29,000 × €1,200 × 0.20 = €6.96M
    
    2. AVOIDABLE CO2 (tonnes):
       - If 40% of replacements were refurbished instead of new
       - Each refurbished device saves 85% of manufacturing CO2
       - Formula: fleet_size × 40% × avg_co2_kg × 85% ÷ 1000
       - Example: 29,000 × 0.40 × 85 × 0.85 ÷ 1000 = 837 tonnes
    
    3. DEVICES TO ACT ON:
       - About 30% of any fleet needs attention (old, slow, or EOL)
       - Formula: fleet_size × 30%
       - Example: 29,000 × 0.30 = 8,700 devices
    
    4. MONTHS TO TARGET:
       - Comes from Strategy Simulator (best strategy time)
       - Uses the "Optimal Combined" strategy calculation
    """
    
    # Get config values
    avg_price = STRATEGY_CONFIG.get("avg_device_cost_eur", 1200)
    avg_co2_kg = STRATEGY_CONFIG.get("avg_device_co2_kg", 85)
    avg_depreciation = DEPRECIATION_CURVE.get(4, 0.20)  # 4-year average age
    
    # 1. STRANDED VALUE
    # Logic: Old devices still have resale value that's not being captured
    stranded_value = fleet_size * avg_price * avg_depreciation
    
    # 2. AVOIDABLE CO2
    # Logic: If 40% of purchases were refurbished, how much CO2 saved?
    refurb_potential_rate = 0.40  # Assume 40% could go refurbished
    co2_savings_rate = REFURB_CONFIG.get("co2_reduction", 0.85)  # 85% savings
    avoidable_co2 = (fleet_size * refurb_potential_rate * avg_co2_kg * co2_savings_rate) / 1000
    
    # 3. DEVICES NEEDING ACTION
    # Logic: ~30% of fleet is typically due for action
    action_rate = 0.30
    devices_to_act = int(fleet_size * action_rate)
    
    # 4. MONTHS TO TARGET
    # Run the strategy simulator to get best time
    results = StrategySimulator.simulate_all(current_co2, target_pct, fleet_size)
    best_strategy = results[0] if results else {"months_to_target": 24, "name": "Combined"}
    months_to_target = best_strategy["months_to_target"]
    
    return {
        "stranded_value": stranded_value,
        "avoidable_co2": avoidable_co2,
        "devices_to_act": devices_to_act,
        "months_to_target": months_to_target,
        "best_strategy": best_strategy.get("name", "Combined"),
    }


# =============================================================================
# STYLING
# =============================================================================

def inject_styles():
    """Inject luxury LVMH styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Cormorant+Garamond:wght@400;500&family=Montserrat:wght@300;400;500;600&display=swap');
    
    .stApp { background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 100%); }
    #MainMenu, footer, header { visibility: hidden; }
    
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
    p, span, div, label { font-family: 'Montserrat', sans-serif !important; }
    
    /* Header */
    .page-header {
        background: #fff; border-bottom: 2px solid #e8e4dc;
        padding: 25px 0; margin-bottom: 25px; text-align: center;
    }
    .page-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: #2c2c2c; margin: 0; }
    .page-title span { color: #2e7d32; }
    .page-subtitle { font-size: 0.75rem; color: #888; letter-spacing: 2px; text-transform: uppercase; margin-top: 8px; }
    
    /* Killer Banner */
    .killer-banner {
        background: #f8f6f2; border: 1px solid #d4cfc5; border-left: 4px solid #8a6c4a;
        border-radius: 8px; padding: 20px 25px; margin: 15px 0 25px 0;
    }
    .killer-text { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; line-height: 1.7; color: #4a4a4a; }
    .killer-hl { color: #8a6c4a; font-weight: 600; }
    
    /* Section */
    .section-header {
        display: flex; align-items: center; gap: 10px;
        margin: 25px 0 18px 0; padding-bottom: 10px; border-bottom: 2px solid #e8e4dc;
    }
    .section-title { font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: #8a6c4a; margin: 0; }
    
    /* Recommendation Banners */
    .rec-banner { border-radius: 10px; padding: 28px 20px; text-align: center; margin: 20px 0; }
    .bg-keep { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border: 1px solid #a5d6a7; }
    .bg-keep .rec-title { color: #2e7d32; }
    .bg-refurb { background: linear-gradient(135deg, #e3f2fd, #bbdefb); border: 1px solid #90caf9; }
    .bg-refurb .rec-title { color: #1565c0; }
    .bg-new { background: linear-gradient(135deg, #fff3e0, #ffe0b2); border: 1px solid #ffcc80; }
    .bg-new .rec-title { color: #e65100; }
    .bg-resell { background: linear-gradient(135deg, #f3e5f5, #e1bee7); border: 1px solid #ce93d8; }
    .bg-resell .rec-title { color: #7b1fa2; }
    
    .rec-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 2px; color: #666; margin-bottom: 8px; }
    .rec-title { font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 500; margin: 0; }
    .rec-sub { font-size: 0.8rem; color: #666; margin-top: 10px; }
    
    /* Metrics */
    .metric-card {
        background: #fff; border: 1px solid #e8e4dc; border-radius: 10px;
        padding: 18px 12px; text-align: center;
    }
    .metric-icon { font-size: 1.2rem; margin-bottom: 6px; }
    .metric-label { font-size: 0.55rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .metric-value { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: #2c2c2c; }
    .metric-sub { font-size: 0.65rem; margin-top: 4px; }
    .text-green { color: #2e7d32; }
    .text-orange { color: #e65100; }
    .text-red { color: #c62828; }
    
    /* Strategy Cards */
    .strat-card { background: #fff; border: 1px solid #e8e4dc; border-radius: 10px; padding: 18px; margin: 10px 0; }
    .strat-card.winner { border: 2px solid #2e7d32; background: linear-gradient(135deg, #f1f8e9, #fff); }
    .strat-rank { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: #8a6c4a; }
    .strat-name { font-weight: 600; font-size: 0.95rem; color: #2c2c2c; margin: 4px 0; }
    .strat-desc { font-size: 0.85rem; color: #666; }
    .strat-stats { display: flex; gap: 20px; margin-top: 12px; }
    .strat-stat-val { font-family: 'Playfair Display', serif; font-size: 1.2rem; color: #2e7d32; }
    .strat-stat-lbl { font-size: 0.5rem; color: #888; text-transform: uppercase; }
    
    /* Winner Banner */
    .winner-banner {
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        color: white; border-radius: 12px; padding: 25px;
        text-align: center; margin: 20px 0;
    }
    .winner-title { font-family: 'Playfair Display', serif; font-size: 1.8rem; margin-bottom: 10px; }
    .winner-subtitle { font-size: 0.9rem; opacity: 0.9; }
    
    /* Do Nothing Warning */
    .warning-banner {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border: 2px solid #ef5350; border-radius: 12px; padding: 20px;
        text-align: center; margin: 20px 0;
    }
    .warning-title { font-family: 'Playfair Display', serif; font-size: 1.3rem; color: #c62828; }
    .warning-text { color: #b71c1c; margin-top: 8px; }
    
    /* Sources */
    .sources-box {
        background: #fdfcfa; border: 1px solid #e8e4dc; border-radius: 8px;
        padding: 15px; margin-top: 15px; font-size: 0.75rem; color: #666;
    }
    .sources-title { font-weight: 600; color: #8a6c4a; margin-bottom: 8px; }
    
    /* Divider */
    .divider { height: 1px; background: linear-gradient(90deg, transparent, #d4cfc5, transparent); margin: 20px 0; }
    
    /* Buttons */
    .stButton > button {
        background: #8a6c4a !important; color: #fff !important; border: none !important;
        padding: 12px 25px !important; border-radius: 6px !important;
        text-transform: uppercase !important; letter-spacing: 1px !important;
        font-size: 0.75rem !important; font-weight: 500 !important;
    }
    .stButton > button:hover { background: #6d553a !important; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #fff; border-bottom: 2px solid #e8e4dc; }
    .stTabs [data-baseweb="tab"] { color: #888; font-size: 0.8rem; padding: 12px 20px; }
    .stTabs [aria-selected="true"] { color: #8a6c4a !important; border-bottom: 3px solid #8a6c4a !important; }
    
    /* Expander */
    [data-testid="stExpander"] { background: #fff !important; border: 1px solid #e8e4dc !important; border-radius: 8px !important; }
    
    /* Logic Box */
    .logic-box {
        background: #f5f5f5; border: 1px solid #ddd; border-radius: 8px;
        padding: 15px; margin: 10px 0; font-family: monospace; font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# DEMO DATA GENERATOR
# =============================================================================

def get_demo_csv():
    """Generate demo fleet data using actual personas and devices"""
    personas = PERSONA_OPTIONS[:4] if len(PERSONA_OPTIONS) >= 4 else PERSONA_OPTIONS * 2
    devices = DEVICE_OPTIONS[:4] if len(DEVICE_OPTIONS) >= 4 else DEVICE_OPTIONS * 2
    
    data = {
        "Device_Model": [devices[i % len(devices)] for i in range(10)],
        "Age_Years": [4, 3, 5, 2, 6, 4, 3, 5, 4, 2],
        "Persona": [personas[i % len(personas)] for i in range(10)],
        "Maison": ["Louis Vuitton", "Louis Vuitton", "Dior", "Dior", "Sephora",
                   "Sephora", "Tiffany", "Bulgari", "Fendi", "Givenchy"]
    }
    return pd.DataFrame(data).to_csv(index=False).encode('utf-8')


# =============================================================================
# CHARTS
# =============================================================================

def create_tco_chart(scenarios, winner):
    """Bar chart comparing TCO across scenarios"""
    options = list(scenarios.keys())
    values = [scenarios[k]["fin"] for k in options]
    colors = ["#2e7d32" if k == winner else "#8a6c4a" if k != "NEW" else "#94a3b8" for k in options]
    
    fig = go.Figure(go.Bar(
        x=options, y=values, marker_color=colors,
        text=[f"€{v:,.0f}" for v in values], textposition='outside',
        textfont=dict(size=11, family='Montserrat')
    ))
    fig.update_layout(
        title=dict(text="Annual TCO Comparison", font=dict(family='Cormorant Garamond', size=15, color='#8a6c4a'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=260, margin=dict(l=40, r=40, t=45, b=40),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f0ece4')
    )
    return fig


def create_impact_chart(results, target_co2):
    """
    NEW BUSINESS-FRIENDLY CHART
    
    Shows: "If you do THIS, you reach your goal. If you do NOTHING, you fail."
    
    Visual: Big green checkmark area vs red danger zone
    """
    
    # Find best strategy and "Do Nothing"
    best = results[0]
    do_nothing = next((r for r in results if r["key"] == "baseline"), results[-1])
    
    fig = go.Figure()
    
    # Add target zone (green area at bottom)
    fig.add_hrect(
        y0=0, y1=target_co2,
        fillcolor="rgba(46, 125, 50, 0.15)",
        line_width=0,
        annotation_text="🎯 TARGET ZONE",
        annotation_position="inside top left",
        annotation=dict(font=dict(size=14, color="#2e7d32"))
    )
    
    # Add danger zone (red area at top)
    fig.add_hrect(
        y0=target_co2, y1=best["projection"][0]["co2"] * 1.05,
        fillcolor="rgba(198, 40, 40, 0.08)",
        line_width=0,
    )
    
    # Target line
    fig.add_hline(
        y=target_co2, 
        line_dash="solid", 
        line_color="#2e7d32", 
        line_width=3,
        annotation_text=f"TARGET: {target_co2:,.0f} tonnes (-{results[0]['projection'][0]['co2'] - target_co2:.0f}t)",
        annotation_position="right",
        annotation=dict(font=dict(size=12, color="#2e7d32", weight="bold"))
    )
    
    # BEST STRATEGY LINE (thick green)
    best_months = [p["month"] for p in best["projection"]]
    best_co2 = [p["co2"] for p in best["projection"]]
    
    fig.add_trace(go.Scatter(
        x=best_months, y=best_co2,
        mode='lines',
        name=f"✅ {best['name']} (RECOMMENDED)",
        line=dict(color="#2e7d32", width=4),
        fill='tozeroy',
        fillcolor='rgba(46, 125, 50, 0.1)',
    ))
    
    # Add marker where best strategy hits target
    target_month = None
    for i, p in enumerate(best["projection"]):
        if p["co2"] <= target_co2:
            target_month = p["month"]
            break
    
    if target_month:
        fig.add_trace(go.Scatter(
            x=[target_month], y=[target_co2],
            mode='markers+text',
            marker=dict(size=20, color="#2e7d32", symbol="star"),
            text=[f"🎉 GOAL REACHED\nMonth {target_month}"],
            textposition="top center",
            textfont=dict(size=11, color="#2e7d32"),
            showlegend=False
        ))
    
    # DO NOTHING LINE (dashed red)
    nothing_months = [p["month"] for p in do_nothing["projection"]]
    nothing_co2 = [p["co2"] for p in do_nothing["projection"]]
    
    fig.add_trace(go.Scatter(
        x=nothing_months, y=nothing_co2,
        mode='lines',
        name="❌ Do Nothing (FAIL)",
        line=dict(color="#c62828", width=3, dash="dash"),
    ))
    
    # Add "NEVER REACHES TARGET" annotation for Do Nothing
    fig.add_annotation(
        x=20, y=nothing_co2[-1],
        text="❌ NEVER reaches target",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#c62828",
        font=dict(size=11, color="#c62828"),
        ax=-50, ay=-30
    )
    
    fig.update_layout(
        title=dict(
            text="📊 Will You Reach Your Target?",
            font=dict(family='Playfair Display', size=20, color='#2c2c2c'),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=420,
        margin=dict(l=60, r=120, t=60, b=50),
        xaxis=dict(
            title="Months",
            showgrid=True,
            gridcolor='#f0ece4',
            range=[0, 24]
        ),
        yaxis=dict(
            title="CO₂ Emissions (tonnes/year)",
            showgrid=True,
            gridcolor='#f0ece4',
        ),
        legend=dict(
            orientation='h',
            y=1.12,
            x=0.5,
            xanchor='center',
            font=dict(size=11)
        ),
        showlegend=True
    )
    
    return fig


def create_comparison_bars(results):
    """
    Horizontal bar chart showing months to target for each strategy.
    Visual: Green = fast, Red = slow/never
    """
    
    # Filter out "never" strategies and sort
    valid = [r for r in results if r["months_to_target"] < 100]
    valid = sorted(valid, key=lambda x: x["months_to_target"])[:5]
    
    names = [r["name"] for r in valid]
    months = [r["months_to_target"] for r in valid]
    
    # Color: green for fast, orange for medium, red for slow
    colors = []
    for m in months:
        if m <= 18:
            colors.append("#2e7d32")  # Green - fast
        elif m <= 30:
            colors.append("#f9a825")  # Yellow - medium
        else:
            colors.append("#c62828")  # Red - slow
    
    fig = go.Figure(go.Bar(
        y=names,
        x=months,
        orientation='h',
        marker_color=colors,
        text=[f"{m:.0f} months" for m in months],
        textposition='outside',
        textfont=dict(size=12, family='Montserrat')
    ))
    
    fig.update_layout(
        title=dict(
            text="⏱️ Time to Reach Target (Faster = Better)",
            font=dict(family='Cormorant Garamond', size=16, color='#8a6c4a'),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280,
        margin=dict(l=150, r=80, t=50, b=40),
        xaxis=dict(title="Months", showgrid=True, gridcolor='#f0ece4'),
        yaxis=dict(showgrid=False),
    )
    
    return fig


# =============================================================================
# TAB 1: SINGLE DEVICE AUDIT
# =============================================================================

def render_single_audit():
    """Single device analysis tab"""
    st.markdown('<div class="section-header"><span>🔍</span><h3 class="section-title">Single Device Analysis</h3></div>', unsafe_allow_html=True)
    
    # Input form
    c1, c2, c3 = st.columns([2, 1, 1.5])
    with c1:
        device = st.selectbox("Device Model", DEVICE_OPTIONS, help="Select device from inventory")
    with c2:
        age = st.slider("Age (Years)", 1, 8, 4, help="Time device has been in service")
    with c3:
        persona = st.selectbox("User Profile", PERSONA_OPTIONS, help="User role affects productivity calculation")
    
    c4, c5 = st.columns([1, 2])
    with c4:
        country = st.selectbox("Country", ["FR", "DE", "UK", "US", "CN"], help="Affects carbon grid intensity")
    with c5:
        priority = st.radio("Priority", ["Balanced", "Cost-First", "Eco-First"], horizontal=True, help="Weighting preference")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Run analysis
    if st.button("🚀 Run Analysis", use_container_width=True):
        with st.spinner("Analyzing..."):
            time.sleep(0.5)
            st.session_state['audit_done'] = True
    
    # Display results
    if st.session_state.get('audit_done'):
        fin_weight = {"Balanced": 0.5, "Cost-First": 1.0, "Eco-First": 0.0}[priority]
        
        # Get calculations from calculator.py
        scenarios = TCOCalculator.calculate_all_scenarios(device, age, persona, country)
        winner, scores, sav_fin, sav_env = TCOCalculator.get_recommendation(scenarios, fin_weight, persona)
        urgency = UrgencyCalculator.calculate(age)
        
        # Recommendation banner
        styles = {"KEEP": "bg-keep", "NEW": "bg-new", "REFURB": "bg-refurb", "RESELL": "bg-resell"}
        subs = {"KEEP": "✓ Extend Lifecycle", "NEW": "→ Upgrade", "REFURB": "↻ Circular", "RESELL": "$ Recover"}
        
        st.markdown(f'''
        <div class="rec-banner {styles[winner]}">
            <div class="rec-label">Recommendation</div>
            <div class="rec-title">{winner}</div>
            <div class="rec-sub">{subs[winner]}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            cl = "text-green" if sav_fin > 0 else "text-orange"
            st.markdown(f'<div class="metric-card"><div class="metric-icon">💰</div><div class="metric-label">Savings</div><div class="metric-value">€{sav_fin:,.0f}</div><div class="metric-sub {cl}">vs NEW</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">🌱</div><div class="metric-label">CO₂ Avoided</div><div class="metric-value">{sav_env:.1f}kg</div><div class="metric-sub text-green">/year</div></div>', unsafe_allow_html=True)
        with m3:
            resale = scenarios["RESELL"]["resale_value"]
            st.markdown(f'<div class="metric-card"><div class="metric-icon">💎</div><div class="metric-label">Resale Value</div><div class="metric-value">€{resale:,.0f}</div><div class="metric-sub">hidden asset</div></div>', unsafe_allow_html=True)
        with m4:
            ucl = "text-green" if urgency["priority"] == "LOW" else "text-orange"
            st.markdown(f'<div class="metric-card"><div class="metric-icon">⏱️</div><div class="metric-label">Urgency</div><div class="metric-value">{urgency["priority"]}</div><div class="metric-sub {ucl}">{urgency["score"]}x</div></div>', unsafe_allow_html=True)
        
        # Chart
        st.plotly_chart(create_tco_chart(scenarios, winner), use_container_width=True, config={'displayModeBar': False})
        
        # Details expander
        with st.expander("📐 Calculation Details & Data Sources"):
            st.markdown(f"""
            **TCO Breakdown:**
            - **KEEP:** €{scenarios['KEEP']['fin']:,.0f}/yr (includes €{scenarios['KEEP']['productivity_loss']:,.0f} productivity loss at {scenarios['KEEP']['lag_pct']}% slowdown)
            - **NEW:** €{scenarios['NEW']['fin']:,.0f}/yr (€{scenarios['NEW']['hardware_cost']:,.0f} hardware amortization)
            - **REFURB:** €{scenarios['REFURB']['fin']:,.0f}/yr (saves {scenarios['REFURB']['co2_saved']:.1f}kg CO₂ vs NEW)
            - **RESELL:** €{scenarios['RESELL']['fin']:,.0f}/yr (recovers €{scenarios['RESELL']['resale_value']:,.0f}, net cost €{scenarios['RESELL']['net_cost']:,.0f})
            """)
            
            sources = get_data_sources_summary()
            st.markdown(f"""
            <div class="sources-box">
                <div class="sources-title">📚 Data Sources</div>
                • Depreciation: {sources['Depreciation']}<br>
                • Productivity: {sources['Productivity Model']}<br>
                • Refurbished: {sources['Refurbished Data']}<br>
                • Carbon Grid: {sources['Grid Carbon']}<br>
                • Urgency: {sources['Urgency Framework']}
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: FLEET ANALYSIS
# =============================================================================

def render_fleet_analysis():
    """Fleet analysis tab"""
    st.markdown('<div class="section-header"><span>📊</span><h3 class="section-title">Fleet Analysis</h3></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        uploaded = st.file_uploader("Upload Fleet CSV", type=["csv"], help="Columns: Device_Model, Age_Years, Persona, Maison")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Load Demo Data", use_container_width=True):
            st.session_state['demo_fleet'] = True
    
    df = None
    if uploaded:
        df = pd.read_csv(uploaded)
    elif st.session_state.get('demo_fleet'):
        df = pd.read_csv(BytesIO(get_demo_csv()))
    
    if df is not None:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Analyze fleet using calculator.py
        with st.spinner("Analyzing fleet..."):
            results = FleetAnalyzer.analyze_fleet(df)
        
        # Summary metrics
        total_sav = sum(r["savings_eur"] for r in results)
        total_co2 = sum(r["co2_saved_kg"] for r in results)
        total_resale = sum(r["resale_value"] for r in results)
        high_urg = sum(1 for r in results if r["urgency"] == "HIGH")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">💰</div><div class="metric-label">Total Savings</div><div class="metric-value">€{total_sav:,.0f}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">🌱</div><div class="metric-label">CO₂ Avoidable</div><div class="metric-value">{total_co2:,.0f}kg</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">💎</div><div class="metric-label">Stranded Value</div><div class="metric-value">€{total_resale:,.0f}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-icon">🚨</div><div class="metric-label">High Urgency</div><div class="metric-value">{high_urg}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Results table
        res_df = pd.DataFrame([{
            "Device": r["device"], "Age": r["age"], "Maison": r["maison"],
            "Action": r["recommendation"], "Savings": f"€{r['savings_eur']:,.0f}",
            "CO2": f"{r['co2_saved_kg']:.1f}kg", "Urgency": r["urgency"]
        } for r in results])
        
        st.dataframe(res_df, use_container_width=True, hide_index=True)


# =============================================================================
# TAB 3: STRATEGY SIMULATOR (IMPROVED!)
# =============================================================================

def render_strategy_simulator():
    """Strategy simulator tab - IMPROVED VERSION"""
    st.markdown('<div class="section-header"><span>🎯</span><h3 class="section-title">Strategy Simulator</h3></div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#666;font-size:0.9rem;">Which strategy gets us to our target <strong>fastest</strong>?</p>', unsafe_allow_html=True)
    
    # Input parameters
    c1, c2, c3 = st.columns(3)
    with c1:
        fleet = st.number_input("Fleet Size", 1000, 100000, 29000, 1000, help="Total number of devices")
    with c2:
        co2 = st.number_input("Current CO₂ (tonnes/yr)", 100, 50000, 4025, 100, help="Total annual carbon footprint")
    with c3:
        target = st.slider("Reduction Target %", 5, 50, 20, help="Target CO₂ reduction")
    
    # Calculate and show DYNAMIC killer stats
    killer = calculate_killer_stats(fleet, co2, target)
    
    st.markdown(f'''
    <div class="killer-banner">
        <p class="killer-text">
            Based on your inputs: <span class="killer-hl">€{killer["stranded_value"]/1e6:.1f}M</span> stranded value, 
            <span class="killer-hl">{killer["avoidable_co2"]:,.0f} tonnes</span> avoidable CO₂, 
            <span class="killer-hl">{killer["devices_to_act"]:,} devices</span> to act on, 
            achievable in <span class="killer-hl">{killer["months_to_target"]:.0f} months</span> with {killer["best_strategy"]}.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Run simulation
    if st.button("🚀 Simulate Strategies", use_container_width=True):
        with st.spinner("Running simulations..."):
            time.sleep(0.8)
            st.session_state['sim_results'] = StrategySimulator.simulate_all(co2, target, fleet)
            st.session_state['sim_target'] = co2 * (1 - target/100)
    
    # Display results
    if st.session_state.get('sim_results'):
        results = st.session_state['sim_results']
        target_co2 = st.session_state.get('sim_target', co2 * 0.8)
        best = results[0]
        
        # WINNER BANNER
        st.markdown(f'''
        <div class="winner-banner">
            <div class="winner-title">🏆 RECOMMENDED: {best["name"]}</div>
            <div class="winner-subtitle">Reaches -{target}% target in <strong>{best["months_to_target"]:.0f} months</strong> | 
            Saves <strong>{best["annual_co2_saved"]:.0f} tonnes CO₂/year</strong> | 
            Saves <strong>€{best["annual_eur_saved"]/1000:.0f}K/year</strong></div>
        </div>
        ''', unsafe_allow_html=True)
        
        # DO NOTHING WARNING
        do_nothing = next((r for r in results if r["key"] == "baseline"), None)
        if do_nothing and do_nothing["months_to_target"] > 100:
            st.markdown('''
            <div class="warning-banner">
                <div class="warning-title">⚠️ WARNING: "Do Nothing" NEVER reaches the target!</div>
                <div class="warning-text">Without action, you will miss your sustainability goals.</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # NEW IMPACT CHART
        st.plotly_chart(create_impact_chart(results, target_co2), use_container_width=True, config={'displayModeBar': False})
        
        # COMPARISON BARS
        st.plotly_chart(create_comparison_bars(results), use_container_width=True, config={'displayModeBar': False})
        
        # DETAILED RANKINGS with explanation
        st.markdown('<div class="section-header"><span>🏆</span><h3 class="section-title">Strategy Rankings</h3></div>', unsafe_allow_html=True)
        
        for r in results[:5]:
            win_class = "winner" if r["rank"] == 1 else ""
            status = "✅ BEST" if r["rank"] == 1 else ("⚠️ SLOW" if r["months_to_target"] > 36 else "")
            
            st.markdown(f'''
            <div class="strat-card {win_class}">
                <div style="display:flex;align-items:flex-start;gap:15px;">
                    <div class="strat-rank">#{r["rank"]}</div>
                    <div style="flex:1;">
                        <div class="strat-name">{r["name"]} {status}</div>
                        <div class="strat-desc">{r["description"]}</div>
                        <div class="strat-stats">
                            <div><div class="strat-stat-val">{r["months_to_target"]:.0f}</div><div class="strat-stat-lbl">Months to Target</div></div>
                            <div><div class="strat-stat-val">{r["annual_co2_saved"]:.0f}t</div><div class="strat-stat-lbl">CO₂ Saved/Year</div></div>
                            <div><div class="strat-stat-val">€{r["annual_eur_saved"]/1000:.0f}K</div><div class="strat-stat-lbl">Money Saved/Year</div></div>
                        </div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # LOGIC EXPLANATION
        with st.expander("🧮 How is the ranking calculated?"):
            st.markdown("""
            ### Ranking Logic (Simple Version)
            
            **We rank strategies by ONE thing: How fast do they reach the target?**
            
            ---
            
            **Step 1: Calculate CO₂ savings per strategy**
            
            Each strategy saves CO₂ in different ways:
            
            | Strategy | How It Saves CO₂ |
            |----------|------------------|
            | **Refurbished** | Each refurb device = 85% less manufacturing CO₂ |
            | **Extend Lifespan** | Fewer replacements = less manufacturing |
            | **Combined** | Both benefits together! |
            
            ---
            
            **Step 2: Calculate time to reach target**
            
            ```
            gap = current_co2 - target_co2
            monthly_savings = annual_savings ÷ 12
            months_to_target = gap ÷ monthly_savings
            ```
            
            ---
            
            **Step 3: Rank by speed (fastest = #1)**
            
            That's it! The strategy that closes the gap fastest wins.
            
            ---
            
            **Why "Do Nothing" fails:**
            - 0% refurbished = 0 savings
            - 0 years extension = 0 savings
            - Total savings = 0
            - Time to target = ∞ (never!)
            """)
            
            # Show actual numbers for this simulation
            st.markdown("### Your Simulation Numbers:")
            st.markdown(f"""
            - **Target:** {target_co2:,.0f} tonnes (that's -{target}% from {co2:,.0f})
            - **Gap to close:** {co2 - target_co2:,.0f} tonnes
            - **Best strategy ({best['name']}):** saves {best['annual_co2_saved']:.0f} tonnes/year = {best['annual_co2_saved']/12:.1f} tonnes/month
            - **Time:** {co2 - target_co2:.0f} ÷ {best['annual_co2_saved']/12:.1f} = **{best['months_to_target']:.0f} months**
            """)
        
        # Sources
        sources = get_data_sources_summary()
        st.markdown(f'''
        <div class="sources-box">
            <div class="sources-title">📚 Methodology & Data Sources</div>
            • Refurbished CO₂ savings (85%): {sources['Refurbished Data']}<br>
            • Strategy parameters: {sources['Strategy Params']}<br>
            • Replacement rate: 25%/year (industry standard 4-year refresh)
        </div>
        ''', unsafe_allow_html=True)


# =============================================================================
# MAIN PAGE
# =============================================================================

def render_audit_page():
    """Main page renderer"""
    inject_styles()
    
    # Header
    st.markdown('''
    <div class="page-header">
        <h1 class="page-title">EcoCycle <span>Intelligence</span></h1>
        <p class="page-subtitle">LVMH · Equipment Lifecycle Management</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Default killer stat (will update dynamically in Strategy Simulator)
    default_killer = calculate_killer_stats(45000, 3825, 20)
    st.markdown(f'''
    <div class="killer-banner">
        <p class="killer-text">
            LVMH is sitting on <span class="killer-hl">€{default_killer["stranded_value"]/1e6:.1f}M</span> of stranded value and 
            <span class="killer-hl">{default_killer["avoidable_co2"]:,.0f} tonnes</span> of avoidable CO₂. Our tool identifies exactly which 
            <span class="killer-hl">{default_killer["devices_to_act"]:,} devices</span> to act on, in which order, to capture this within 
            <span class="killer-hl">{default_killer["months_to_target"]:.0f} months</span>.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Tabs
    t1, t2, t3 = st.tabs(["🔍 Single Audit", "📊 Fleet Analysis", "🎯 Strategy Simulator"])
    with t1:
        render_single_audit()
    with t2:
        render_fleet_analysis()
    with t3:
        render_strategy_simulator()
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#999;font-size:0.7rem;letter-spacing:2px;">LVMH GREEN IN TECH · HACKATHON 2025</p>', unsafe_allow_html=True)


# Entry point
if __name__ == "__main__":
    render_audit_page()