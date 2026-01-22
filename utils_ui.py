"""
LVMH Green in Tech - UI Utilities & Homepage
Light Luxury Theme - Fully Centered with Framed Rectangles
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import base64

# =============================================================================
# GLOBAL STYLES - FULL CENTERING & LUXURY FRAMING
# =============================================================================

import streamlit as st
import os
import base64

# =============================================================================
# GLOBAL STYLES - REFINED VISUAL HIERARCHY & RHYTHM
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - Refined visual hierarchy and breathing room"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === BASE APP === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* === REFINED SECTION TITLES === */
    h2, h3, h4, .section-title, .context-title {
        text-align: left !important;
        width: 100% !important;
        margin-left: 0 !important;
        font-family: 'Cormorant Garamond', serif !important;
        color: #8a6c4a !important;
        letter-spacing: 1.5px !important;
        font-weight: 700 !important; 
        font-size: 1.95rem !important;
        margin-bottom: 24px !important;
        line-height: 1.3 !important;
    }

    /* Small titles inside cards (Pillars, Insights, KPI labels) */
    .kpi-label, .pillar-title, .insight-title {
        text-align: left !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important; 
        margin-bottom: 12px !important;
        display: block !important;
        color: #8a6c4a !important;
        line-height: 1.4 !important;
    }

    /* Refined centered H1 */
    h1 {
        text-align: center !important;
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        font-size: 3.2rem !important;
        font-weight: 500 !important;
        line-height: 1.2 !important;
        margin-bottom: 18px !important;
    }

    /* === FRAMING BOXES - REFINED BREATHING ROOM === */
    .pillar-card, .action-card, .context-card, .insight-card, .data-input-section, .chart-container {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 12px !important;
        padding: 32px !important; 
        margin-bottom: 28px !important;
        box-shadow: 0 4px 12px rgba(138, 108, 74, 0.04) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
    }

    /* Context Card specific styling */
    .context-card {
        border-left: 6px solid #8a6c4a !important;
        border-radius: 4px 12px 12px 4px !important;
        padding: 28px 32px !important;
        margin-bottom: 20px !important;
    }

    /* === KPI CARDS - REFINED SPACING === */
    .kpi-card {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 12px !important;
        padding: 36px 28px !important;
        text-align: center !important;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06) !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        margin-bottom: 28px !important;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 80px; height: 5px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 4px 4px;
    }

    /* === URGENT ALERT (RED BOX) - REFINED SPACING === */
    div.urgent-alert {
        background: #fef2f2 !important;
        padding: 38px 32px !important;
        border-radius: 15px !important;
        border: 2px solid #ef4444 !important; 
        box-shadow: 0 6px 25px rgba(239, 68, 68, 0.1) !important;
        margin: 48px 0 !important;
        text-align: center !important;
    }

    /* === BODY TEXT - REFINED LINE HEIGHT === */
    p, span, div, label, li {
        font-family: 'Montserrat', sans-serif !important;
        color: #4a4a4a !important;
        font-size: 1rem !important;
        line-height: 1.65 !important;
    }

    /* Context text specific */
    .context-text {
        line-height: 1.7 !important;
        margin-bottom: 0 !important;
    }

    /* Section headers spacing - REFINED RHYTHM */
    .section-header { 
        border-bottom: 2px solid #e8e4dc; 
        margin: 58px 0 36px 0; 
        padding-bottom: 20px; 
    }

    /* === BUTTONS - REFINED PADDING === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        border-radius: 8px !important;
        padding: 14px 40px !important;
        font-weight: 600 !important;
        margin-top: 8px !important;
    }

    /* === COLUMN SPACING - ADD BREATHING ROOM === */
    .row-widget.stHorizontal {
        gap: 24px !important;
    }

    /* === LOGO SECTION - REFINED SPACING === */
    .logo-section {
        padding: 28px 0 18px 0 !important;
        margin-bottom: 42px !important;
    }

    /* === WELCOME HERO - REFINED SPACING === */
    .welcome-hero {
        margin-bottom: 52px !important;
        padding: 0 20px !important;
    }

    .welcome-hero p {
        line-height: 1.68 !important;
        margin-top: 12px !important;
    }

    /* === PILLAR CARDS - REFINED INTERNAL SPACING === */
    .pillar-card {
        min-height: 200px !important;
        padding: 28px 22px !important;
    }

    .pillar-card > div:first-child {
        margin-bottom: 16px !important;
    }

    .pillar-card > div:nth-child(2) {
        margin-bottom: 10px !important;
    }

    /* === ACTION CARDS - REFINED INTERNAL SPACING === */
    .action-card {
        min-height: 220px !important;
        padding: 36px 28px !important;
    }

    .action-card > div:first-child {
        margin-bottom: 18px !important;
    }

    .action-card > div:nth-child(2) {
        margin-bottom: 14px !important;
    }

    /* === INSIGHT CARDS - REFINED DENSITY === */
    .insight-card {
        padding: 24px 20px !important;
        min-height: 140px !important;
    }

    .insight-card > div:first-child {
        margin-bottom: 10px !important;
    }

    /* === GOLD DIVIDER - REFINED SPACING === */
    .gold-divider {
        margin: 48px 0 !important;
    }

    /* === FOOTER - REFINED SPACING === */
    div:has(> p[style*="Élysia"]) {
        padding: 32px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
def render_logo():
    """Render a significantly larger Elysia logo, centered and positioned high."""
    logo_path = "logo.png/elysia_logo.png" 

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        st.markdown(f"""
        <div class="logo-section" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 28px 0 18px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 42px; background: white;">
            <img src="data:image/png;base64,{encoded}" alt="Elysia Logo" style="width: 500px; max-width: 95%; margin-bottom: 8px; display: block; margin: 0 auto;">
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 5px; color: #8a6c4a; text-transform: uppercase; margin-top: 2px; text-align: center;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-section" style="text-align: center; padding: 28px 0 18px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 42px; background: white;">
            <div style="font-family: 'Playfair Display', serif; font-size: 90px; color: #8a6c4a; letter-spacing: 15px; line-height: 1; text-align: center;">ELYSIA</div>
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 5px; color: #8a6c4a; text-transform: uppercase; margin-top: 12px; text-align: center;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
        
def render_welcome_section():
    """Centered Hero section."""
    st.markdown(f"""
    <div class="welcome-hero" style="text-align: center; margin-bottom: 52px; padding: 0 20px;">
        <h1 style="font-size: 3.2rem !important; margin-bottom: 18px !important; line-height: 1.2 !important; text-align: center;">Welcome to Élysia</h1>
        <p style="text-align: center; margin: 12px auto 0; max-width: 850px; font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; color: #6a6a6a; line-height: 1.68;">
            Your strategic command center for measuring, tracking, and optimizing 
            the environmental impact of LVMH's IT infrastructure across all Maisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_context_section():
    """Render program context narrative."""
    st.markdown("""
    <div class="section-header">
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
            by embedding sustainability into our technological framework.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_pillars_section():
    """Render strategic pillars."""
    st.markdown("""
    <div class="section-header">
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
                <div style="font-size:1.8rem; margin-bottom:16px; color:#8a6c4a;">{icon}</div>
                <div style="font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:10px;">{title}</div>
                <p style="color:#777; font-size:0.95rem; line-height:1.6;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def render_navigation_section():
    """Render navigation cards."""
    st.markdown('<div class="gold-divider" style="height:1px; background:linear-gradient(90deg,transparent,#d4cfc5,transparent); margin:48px 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">Tools</h2>
    </div>
    """, unsafe_allow_html=True)
    
    nav1, nav2 = st.columns(2)
    with nav1:
        st.markdown("""
        <div class="action-card">
            <div style="font-size:2.5rem; margin-bottom:18px; color:#8a6c4a;">🖥</div>
            <div style="font-family:'Playfair Display'; font-size:1.5rem; margin-bottom:14px;">Equipment Audit</div>
            <p style="color:#777; font-size:1.05rem; line-height:1.6;">Analyze device lifecycle and get ROI recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Equipment Audit", key="nav_eq", use_container_width=True):
            st.session_state['page'] = 'equipment'
            st.rerun()
    
    with nav2:
        st.markdown("""
        <div class="action-card">
            <div style="font-size:2.5rem; margin-bottom:18px; color:#8a6c4a;">☁</div>
            <div style="font-family:'Playfair Display'; font-size:1.5rem; margin-bottom:14px;">Cloud Optimizer</div>
            <p style="color:#777; font-size:1.05rem; line-height:1.6;">Optimize storage and plan archival strategies</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Cloud Optimizer", key="nav_cl", use_container_width=True):
            st.session_state['page'] = 'cloud'
            st.rerun()

def render_insights_section():
    """Render strategic insights."""
    st.markdown("""
    <div class="section-header">
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
                <div style="color:#2e7d32; font-weight:600; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;">{title}</div>
                <p style="font-size:1rem; line-height:1.6;">{text}</p>
            </div>
            """, unsafe_allow_html=True)

def render_footer():
    """Render footer."""
    st.markdown('<div class="gold-divider" style="height:1px; background:linear-gradient(90deg,transparent,#d4cfc5,transparent); margin:48px 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 32px 0;">
        <p style="color: #aaa; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase;">
            Élysia · Alberthon 2026 
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_urgent_alert(header_text, title_text, paragraph_text):
    """Specific function to render the Urgent Red Box with full centering."""
    st.markdown(f"""
    <div class="urgent-alert">
        <div class="urgent-alert-header">🚨 {header_text}</div>
        <h3 style="text-align: center;">{title_text}</h3>
        <p style="text-align: center;">{paragraph_text}</p>
    </div>
    """, unsafe_allow_html=True)

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
