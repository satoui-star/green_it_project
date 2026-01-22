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

def inject_global_styles():
    """Light luxury LVMH styling - Large bold headers, left alignment, and increased spacing"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    /* === BASE APP === */
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* === BOLD & BIGGER SECTION TITLES (Yellow Highlights Fix) === */
    /* text-align is forced left, weight is bold, and font-size is increased */
    h2, h3, h4, .section-title, .context-title {
        text-align: left !important;
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        font-family: 'Cormorant Garamond', serif !important;
        color: #8a6c4a !important;
        letter-spacing: 1px !important;
        font-weight: bold !important; 
        font-size: 2.2rem !important; /* Made significantly bigger than body text */
        margin-bottom: 25px !important;
    }

    /* Small labels inside cards that were highlighted yellow */
    .kpi-label, .pillar-title, .insight-title {
        text-align: left !important;
        font-weight: bold !important;
        font-size: 1.1rem !important; /* Bigger than standard text */
        margin-bottom: 12px !important;
        display: block !important;
    }

    /* Keep the main Welcome H1 centered and very large */
    h1 {
        text-align: center !important;
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        letter-spacing: 2px !important;
        font-size: 3.5rem !important;
        font-weight: 500 !important;
    }

    /* === BEAUTIFUL FRAMING BOXES WITH INCREASED SPACE === */
    .pillar-card, .action-card, .context-card, .insight-card, .data-input-section, .chart-container {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 12px !important;
        padding: 40px !important; /* Increased padding for a more luxury feel */
        margin-bottom: 60px !important; /* Even more space between blocks */
        box-shadow: 0 4px 12px rgba(138, 108, 74, 0.04) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important; /* Consistent left alignment */
    }

    .pillar-card:hover, .action-card:hover {
        border-color: #8a6c4a !important;
        box-shadow: 0 8px 24px rgba(138, 108, 74, 0.12) !important;
        transform: translateY(-2px);
    }

    /* Context Card styling */
    .context-card {
        border-left: 6px solid #8a6c4a !important;
        border-radius: 4px 12px 12px 4px !important;
    }

    /* === KPI CARDS (Centered for balance) === */
    .kpi-card {
        background: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 12px !important;
        padding: 45px 30px !important;
        text-align: center !important;
        box-shadow: 0 4px 16px rgba(138, 108, 74, 0.06) !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        margin-bottom: 50px !important;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 70px; height: 5px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 4px 4px;
    }

    /* === URGENT ALERT (RED BOX) === */
    div.urgent-alert {
        background: #fef2f2 !important;
        padding: 45px !important;
        border-radius: 15px !important;
        border: 2px solid #ef4444 !important; 
        box-shadow: 0 6px 25px rgba(239, 68, 68, 0.1) !important;
        margin: 60px 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
    }

    /* === BODY TYPOGRAPHY === */
    p, span, div, label, li {
        font-family: 'Montserrat', sans-serif !important;
        color: #4a4a4a !important;
        font-size: 1rem !important; /* Base size for comparison */
        line-height: 1.6 !important;
    }

    /* Section headers spacing */
    .section-header { 
        border-bottom: 2px solid #e8e4dc; 
        margin: 80px 0 45px 0; /* Clear distinction between sections */
        padding-bottom: 20px; 
    }

    /* === BUTTONS === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        border-radius: 8px !important;
        padding: 15px 40px !important;
        font-weight: 600 !important;
    }
    
    /* === EXPANDERS === */
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 8px !important;
        margin-bottom: 50px !important;
    }
    [data-testid="stExpander"] svg { display: none !important; }

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
        <div class="logo-section" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px 0 10px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 35px; background: white;">
            <img src="data:image/png;base64,{encoded}" alt="Elysia Logo" style="width: 500px; max-width: 95%; margin-bottom: 5px; display: block; margin: 0 auto;">
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 5px; color: #8a6c4a; text-transform: uppercase; margin-top: -5px; text-align: center;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="logo-section" style="text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid #e8e4dc; margin-bottom: 35px; background: white;">
            <div style="font-family: 'Playfair Display', serif; font-size: 90px; color: #8a6c4a; letter-spacing: 15px; line-height: 1; text-align: center;">ELYSIA</div>
            <div style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; letter-spacing: 5px; color: #8a6c4a; text-transform: uppercase; margin-top: 10px; text-align: center;">
                Where insight drives impact
            </div>
        </div>
        """, unsafe_allow_html=True)
        
def render_welcome_section():
    """Centered Hero section."""
    st.markdown(f"""
    <div class="welcome-hero" style="text-align: center; margin-bottom: 50px;">
        <h1 style="font-size: 3.5rem !important; margin-bottom: 15px !important; text-align: center;">Welcome to Élysia</h1>
        <p style="text-align: center; margin: 0 auto; max-width: 850px; font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; color: #6a6a6a; line-height: 1.6;">
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
                <div style="font-size:1.8rem; margin-bottom:15px; color:#8a6c4a;">{icon}</div>
                <div style="font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:1.5px;">{title}</div>
                <p style="color:#777; font-size:1rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def render_navigation_section():
    """Render navigation cards."""
    st.markdown('<div class="gold-divider" style="height:1px; background:linear-gradient(90deg,transparent,#d4cfc5,transparent); margin:50px 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">Tools</h2>
    </div>
    """, unsafe_allow_html=True)
    
    nav1, nav2 = st.columns(2)
    with nav1:
        st.markdown("""
        <div class="action-card">
            <div style="font-size:2.5rem; margin-bottom:20px; color:#8a6c4a;">🖥</div>
            <div style="font-family:'Playfair Display'; font-size:1.5rem;">Equipment Audit</div>
            <p style="color:#777; font-size:1.05rem;">Analyze device lifecycle and get ROI recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Equipment Audit", key="nav_eq", use_container_width=True):
            st.session_state['page'] = 'equipment'
            st.rerun()
    
    with nav2:
        st.markdown("""
        <div class="action-card">
            <div style="font-size:2.5rem; margin-bottom:20px; color:#8a6c4a;">☁</div>
            <div style="font-family:'Playfair Display'; font-size:1.5rem;">Cloud Optimizer</div>
            <p style="color:#777; font-size:1.05rem;">Optimize storage and plan archival strategies</p>
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
                <div style="color:#2e7d32; font-weight:600; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">{title}</div>
                <p style="font-size:1.05rem;">{text}</p>
            </div>
            """, unsafe_allow_html=True)

def render_footer():
    """Render footer."""
    st.markdown('<div class="gold-divider" style="height:1px; background:linear-gradient(90deg,transparent,#d4cfc5,transparent); margin:50px 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
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
