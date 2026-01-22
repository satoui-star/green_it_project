"""
LVMH Green in Tech - UI Utilities & Homepage
Light Luxury Theme - Narrative Homepage & Shared Styles
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
import os
import base64

# =============================================================================
# GLOBAL STYLES - ORIGINAL CSS PRESERVED AND UNCHANGED
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - Full CSS restoration for Cloud/Equipment pages"""
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
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
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
# REORGANIZED NARRATIVE COMPONENTS
# =============================================================================

def render_logo():
    """Render the Elysia logo image with a fallback to text."""
    logo_path = "logo.png/elysia_logo.png" 

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        st.markdown(f"""
        <div class="logo-section">
            <img src="data:image/png;base64,{encoded}" alt="Elysia Logo" style="width: 280px; max-width: 100%; margin-bottom: 10px;">
            <div class="logo-tagline">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback to elegant text if logo is missing
        st.markdown("""
        <div class="logo-section">
            <div style="font-family: 'Playfair Display', serif; font-size: 60px; color: #C5A059; letter-spacing: 8px; margin-bottom: 0px;">ELYSIA</div>
            <div class="logo-tagline">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_welcome_section():
    """Render the welcome hero section with centered alignment."""
    st.markdown(f"""
    <div class="welcome-hero">
        <h1 class="welcome-title">Welcome to Élysia</h1>
        <p class="welcome-subtitle" style="text-align: center; margin: 0 auto;">
            Your strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_context_section():
    """Render program context narrative."""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon"></span>
        <h2 class="section-title">Program Context</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Render single column context (removed 2026/target metrics as requested)
    st.markdown("""
    <div class="context-card">
        <div class="context-title">LIFE 360 Program</div>
        <p class="context-text">
            An alliance of Nature and Creativity. LVMH's LIFE 360 program sets ambitious 
            environmental targets across all Maisons, with <strong>Élysia</strong> 
            focusing on reducing the technological environmental footprint.
        </p>
    </div>
    
    <div class="context-card">
        <div class="context-title">Our Commitment</div>
        <p class="context-text">
            We are dedicated to reducing LVMH's IT environmental footprint 
            by embedding sustainability into our technological framework. Our approach encompasses 
            carbon emissions management, cloud storage optimization, and global e-waste 
            reduction across all IT operations.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_pillars_section():
    """Render strategic pillars."""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon"></span>
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

def render_navigation_section():
    """Render navigation cards."""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <span class="section-icon"></span>
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

def render_insights_section():
    """Render strategic insights."""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon"></span>
        <h2 class="section-title">Strategic Insights</h2>
    </div>
    """, unsafe_allow_html=True)
    
    i1, i2, i3 = st.columns(3)
    insights = [
        ("🔋 High Impact", "The impact is not only environmental but also Financial"),
        ("⏰ Lifecycle", "Devices' lifecycle could be extended, saving money and carbon"),
        ("☁️ Cloud", "Archiving could cut cloud carbon by 90%")
    ]
    
    for col, (title, text) in zip([i1, i2, i3], insights):
        with col:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{title}</div>
                <p class="insight-text">{text}</p>
            </div>
            """, unsafe_allow_html=True)

def render_footer():
    """Render footer."""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; 
           letter-spacing: 3px; text-transform: uppercase;">
            Élysia · Alberthon 2026 
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN HOMEPAGE FUNCTION
# =============================================================================

def show_home_page():
    """Main function rendering the narrative strategy homepage."""
    inject_global_styles()
    
    render_logo()
    render_welcome_section()
    render_context_section()
    render_pillars_section()
    render_navigation_section()
    render_insights_section()
    render_footer()
