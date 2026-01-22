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
    """Light luxury LVMH styling - Full Restoration with Card Management & Alerts"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === LIGHT LUXURY BASE === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === CARD & RECTANGLE MANAGEMENT (Restored) === */
    /* KPI Cards */
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

    /* Data Input & Chart Rectangles */
    .data-input-section, .chart-container {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    /* Pillar & Action Cards */
    .pillar-card, .action-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 8px;
        padding: 28px 22px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    .action-card:hover {
        border-color: #8a6c4a;
        box-shadow: 0 12px 40px rgba(138, 108, 74, 0.12);
        transform: translateY(-5px);
    }

    /* === ALERT & WARNING MANAGEMENT (The "Red Box" fix) === */
    /* Default LVMH styled info box */
    [data-testid="stAlert"] {
        background: #faf8f5 !important;
        border: 1px solid #e8e4dc !important;
        color: #555 !important;
    }

    /* High Visibility Warning/Error override (Restores the Red Box) */
    [data-testid="stAlert"] > div[role="alert"] {
        border-radius: 6px;
    }
    /* Targets st.error specifically to bring back the red/pink tone */
    .stException, [data-baseweb="notification"] {
        background-color: #fff5f5 !important;
        border: 1px solid #feb2b2 !important;
        color: #c53030 !important;
    }

    /* === EXPANDER MANAGEMENT === */
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 6px !important;
    }
    [data-testid="stExpander"] svg { display: none !important; } /* Hides arrows */

    /* === TYPOGRAPHY === */
    h1 { font-family: 'Playfair Display', serif !important; color: #2c2c2c !important; letter-spacing: 2px !important; }
    h2, h3 { font-family: 'Cormorant+Garamond', serif !important; color: #8a6c4a !important; }
    p, span, div, label { font-family: 'Montserrat', sans-serif !important; color: #4a4a4a !important; }

    /* === BUTTONS === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: #6d553a !important;
        box-shadow: 0 6px 20px rgba(138, 108, 74, 0.25) !important;
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
