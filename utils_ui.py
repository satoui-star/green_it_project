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
# GLOBAL STYLES - RESTORED WITH RED BOX & CARD MANAGEMENT
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - Full CSS restoration with High-Priority Alert Fix"""
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
    
    /* === URGENT ALERT RECTANGLE FIX (Red Box) === */
    /* !important is used here to prevent other page-level CSS from overriding this */
    div.urgent-alert {
        background: #fef2f2 !important;
        padding: 30px !important;
        border-radius: 10px !important;
        border: 2px solid #ef4444 !important; 
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1) !important;
        margin: 25px 0 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    div.urgent-alert-header {
        color: #991b1b !important;
        margin-bottom: 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.9rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }

    div.urgent-alert p {
        color: #7f1d1d !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        font-family: 'Cormorant Garamond', serif !important;
        margin-bottom: 0 !important;
    }

    div.urgent-alert h3 {
        color: #991b1b !important;
        margin-top: 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.8rem !important;
    }

    /* === RECTANGLES & CARD MANAGEMENT === */
    .kpi-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 35px 25px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06);
        transition: all 0.3s ease;
        position: relative;
        height: 100%;
    }

    .data-input-section, .chart-container {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

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
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# REORGANIZED NARRATIVE COMPONENTS
# =============================================================================

def render_urgent_alert(header_text, title_text, paragraph_text):
    """Specific function to render the Urgent Red Box across pages."""
    st.markdown(f"""
    <div class="urgent-alert">
        <div class="urgent-alert-header">{header_text}</div>
        <h3>{title_text}</h3>
        <p>{paragraph_text}</p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, equivalent_text, equivalent_emoji):
    """Render shared metric card style."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon" style="font-size:1.5rem; color:#8a6c4a; margin-bottom:12px;">{equivalent_emoji}</div>
        <div class="kpi-label" style="font-size:0.65rem; color:#888; text-transform:uppercase; letter-spacing:2px; margin-bottom:15px;">{label}</div>
        <div class="kpi-value" style="font-family:'Playfair Display'; font-size:2.8rem; color:#2c2c2c; line-height:1;">{value}</div>
        <div class="kpi-unit" style="font-family:'Montserrat'; color:#8a6c4a; font-size:1rem;">~{equivalent_text}</div>
    </div>
    """, unsafe_allow_html=True)

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
