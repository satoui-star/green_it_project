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
# GLOBAL STYLES - RESTORED BOXES + RED BOX FIX
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - Full CSS restoration including Homepage Boxes & Red Box"""
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

    /* === HOMEPAGE BOXES RESTORATION === */
    /* Pillar & Action Cards */
    .pillar-card, .action-card {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 8px !important;
        padding: 28px 22px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
        display: block !important;
    }

    .pillar-card:hover, .action-card:hover {
        border-color: #8a6c4a !important;
        box-shadow: 0 6px 20px rgba(138, 108, 74, 0.1) !important;
    }

    /* Context Cards */
    .context-card {
        background: #ffffff !important;
        border-left: 3px solid #8a6c4a !important;
        border-radius: 0 8px 8px 0 !important;
        padding: 25px 30px !important;
        margin: 18px 0 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
        display: block !important;
    }

    /* Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, #f0f7f1 0%, #fff 100%) !important;
        border: 1px solid #c8e6c9 !important;
        border-radius: 8px !important;
        padding: 24px !important;
        margin: 10px 0 !important;
        transition: all 0.3s ease !important;
        display: block !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 10px !important;
        padding: 30px 20px !important;
        text-align: center !important;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06) !important;
        position: relative !important;
    }

    /* === URGENT ALERT RECTANGLE FIX (Red Box) === */
    div.urgent-alert {
        background: #fef2f2 !important;
        padding: 30px !important;
        border-radius: 10px !important;
        border: 2px solid #ef4444 !important; 
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1) !important;
        margin: 25px 0 !important;
        display: block !important;
    }

    div.urgent-alert-header {
        color: #991b1b !important;
        margin-bottom: 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.9rem !important;
    }

    /* === TYPOGRAPHY & HEADERS === */
    h1 { font-family: 'Playfair Display', serif !important; color: #2c2c2c !important; letter-spacing: 2px !important; }
    h2, h3, h4 { font-family: 'Cormorant Garamond', serif !important; color: #8a6c4a !important; letter-spacing: 1px !important; }
    p, span, div, label, li { font-family: 'Montserrat', sans-serif !important; color: #4a4a4a !important; }

    .section-header { border-bottom: 2px solid #e8e4dc; margin: 50px 0 28px 0; padding-bottom: 15px; }

    /* === EXPANDERS === */
    [data-testid="stExpander"] { background: #fff !important; border: 1px solid #e8e4dc !important; border-radius: 6px !important; }
    [data-testid="stExpander"] svg { display: none !important; }
    
    /* === BUTTONS === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        border-radius: 6px !important;
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
            <div class="logo-tagline">Where insight drives impact</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-section">
            <div style="font-family: 'Playfair Display', serif; font-size: 60px; color: #C5A059; letter-spacing: 8px; margin-bottom: 0px;">ELYSIA</div>
            <div class="logo-tagline">Where insight drives impact</div>
        </div>
        """, unsafe_allow_html=True)

def render_welcome_section():
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
    st.markdown('<div class="section-header"><h2 class="section-title">Program Context</h2></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="context-card">
        <div class="context-title">LIFE 360 Program</div>
        <p class="context-text">An alliance of Nature and Creativity. LVMH's LIFE 360 program sets ambitious environmental targets across all Maisons.</p>
    </div>
    <div class="context-card">
        <div class="context-title">Our Commitment</div>
        <p class="context-text">We are dedicated to reducing LVMH's IT environmental footprint by embedding sustainability into our technological framework.</p>
    </div>
    """, unsafe_allow_html=True)

def render_pillars_section():
    st.markdown('<div class="section-header"><h2 class="section-title">Strategic Pillars</h2></div>', unsafe_allow_html=True)
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
                <div style="font-size:1.8rem; margin-bottom:15px; color:#8a6c4a;">{icon}</div>
                <div class="pillar-title">{title}</div>
                <p class="pillar-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def render_navigation_section():
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h2 class="section-title">Tools</h2></div>', unsafe_allow_html=True)
    nav1, nav2 = st.columns(2)
    with nav1:
        st.markdown("""
        <div class="action-card">
            <div style="font-size:2.5rem; margin-bottom:20px; color:#8a6c4a;">🖥</div>
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
            <div style="font-size:2.5rem; margin-bottom:20px; color:#8a6c4a;">☁</div>
            <div class="action-title">Cloud Optimizer</div>
            <p class="action-desc">Optimize storage and plan archival strategies</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Cloud Optimizer", key="nav_cl", use_container_width=True):
            st.session_state['page'] = 'cloud'
            st.rerun()

def render_insights_section():
    st.markdown('<div class="section-header"><h2 class="section-title">Strategic Insights</h2></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; padding: 30px 0;"><p style="font-family: Montserrat; color: #aaa; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase;">Élysia · Alberthon 2026</p></div>', unsafe_allow_html=True)

def show_home_page():
    inject_global_styles()
    render_logo()
    render_welcome_section()
    render_context_section()
    render_pillars_section()
    render_navigation_section()
    render_insights_section()
    render_footer()
