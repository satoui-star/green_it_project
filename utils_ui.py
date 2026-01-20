"""
LVMH Green in Tech - Strategic Program Homepage
Refined Luxury Theme - Narrative & Governance Focus
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# =============================================================================
# GLOBAL STYLES - LIGHT LUXURY THEME (KEPT AS REQUESTED)
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - cream/white background"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Cormorant+Garamond:wght@300;400;500;600&family=Montserrat:wght@300;400;500;600&display=swap');
    
    .stApp {
        background: linear-gradient(160deg, #faf9f7 0%, #f5f3ef 50%, #faf9f7 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TYPOGRAPHY */
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        font-weight: 500 !important;
        letter-spacing: 2px !important;
    }
    
    h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #8a6c4a !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
    }
    
    /* LOGO SECTION */
    .logo-section {
        text-align: center;
        padding: 40px 0 30px 0;
        border-bottom: 1px solid #e8e4dc;
        margin-bottom: 35px;
        background: linear-gradient(180deg, #fff 0%, #faf9f7 100%);
    }
    
    .logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        color: #2c2c2c;
        letter-spacing: 12px;
        font-weight: 400;
        margin-bottom: 12px;
    }

    /* NARRATIVE HERO */
    .welcome-hero {
        background: transparent;
        padding: 40px 0;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 3.5rem !important;
        margin-bottom: 25px !important;
    }
    
    .welcome-subtitle {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem;
        color: #6a6a6a;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
        font-style: italic;
    }

    /* STRATEGIC CONTEXT CARDS */
    .context-block {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 4px;
        padding: 35px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }

    .context-tag {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 3px;
        color: #8a6c4a;
        text-transform: uppercase;
        margin-bottom: 15px;
        display: block;
    }

    .context-description {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.25rem;
        line-height: 1.8;
        color: #4a4a4a;
    }

    /* PILLAR CARDS */
    .pillar-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        padding: 30px 20px;
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .pillar-icon { font-size: 2rem; margin-bottom: 15px; }
    
    .pillar-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* ACTION/TOOL CARDS */
    .action-card {
        background: #fff;
        border: 1px solid #d4cfc5;
        border-radius: 8px;
        padding: 40px 30px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .action-card:hover {
        transform: translateY(-5px);
        border-color: #8a6c4a;
    }

    /* INSIGHT CARDS - STATIC */
    .insight-static {
        background: #fdfcfa;
        border-left: 3px solid #8a6c4a;
        padding: 20px 25px;
        margin-bottom: 15px;
    }
    
    .insight-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8a6c4a;
    }

    /* BUTTON OVERRIDES */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        width: 100%;
        border-radius: 0px !important;
        letter-spacing: 2px !important;
    }

    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 60px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# REFINED PAGE COMPONENTS
# =============================================================================

def render_logo():
    st.markdown("""
    <div class="logo-section">
        <div class="logo-text">LVMH</div>
        <div class="logo-tagline" style="font-family: 'Montserrat', sans-serif; font-size: 10px; letter-spacing: 4px; color: #666; text-transform: uppercase;">
            Green in Tech Program
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero():
    st.markdown("""
    <div class="welcome-hero">
        <h1 class="welcome-title">Technology for a Sustainable Future</h1>
        <p class="welcome-subtitle">
            "Weaving environmental excellence into the fabric of our digital transformation."
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_program_context():
    """Static, high-impact narrative blocks"""
    st.markdown('### Program Vision', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="context-block">
            <span class="context-tag">Our Mission</span>
            <p class="context-description">
                Green in Tech is LVMH’s dedicated strategic framework to align IT operations with the 
                <strong>LIFE 360</strong> environmental ambitions. We aim to decouple our digital 
                growth from our environmental footprint.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="context-block">
            <span class="context-tag">The Commitment</span>
            <p class="context-description">
                By 2026, the Group is committed to a significant reduction in the environmental 
                impact of our IT infrastructure, focusing on circularity, carbon sobriety, and 
                responsible resource management across all Maisons.
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_pillars():
    st.markdown('<div style="margin-top:40px"></div>', unsafe_allow_html=True)
    st.markdown('### Strategic Pillars', unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    pillars = [
        ("🔄", "Harmonize", "Unifying digital sustainability standards across the Group."),
        ("📊", "Monitor", "Establishing transparent governance through precise tracking."),
        ("🎛", "Master", "Actively reducing the impact of hardware and cloud services."),
        ("🚀", "Develop", "Fostering a culture of sustainable IT innovation and design.")
    ]
    
    for col, (icon, title, desc) in zip([p1, p2, p3, p4], pillars):
        with col:
            st.markdown(f"""
            <div class="pillar-card">
                <div class="pillar-icon">{icon}</div>
                <div class="pillar-title">{title}</div>
                <p style="font-family: 'Cormorant Garamond', serif; font-size: 1rem; color: #777;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def render_tools_navigation():
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown('### Strategic Tools', unsafe_allow_html=True)
    st.info("Select a tool below to begin your analysis.")
    
    t1, t2 = st.columns(2)
    
    with t1:
        st.markdown("""
        <div class="action-card">
            <div style="font-size: 2.5rem; margin-bottom:15px;">🖥</div>
            <h4 style="margin-bottom:10px;">Equipment Audit</h4>
            <p style="font-family: 'Cormorant Garamond', serif; color: #666; margin-bottom:20px;">
                Analyze device lifecycles and evaluate the environmental impact of your hardware fleet.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access Audit Tool", key="goto_eq"):
            st.session_state['page'] = 'equipment'
            st.rerun()

    with t2:
        st.markdown("""
        <div class="action-card">
            <div style="font-size: 2.5rem; margin-bottom:15px;">☁</div>
            <h4 style="margin-bottom:10px;">Cloud Optimizer</h4>
            <p style="font-family: 'Cormorant Garamond', serif; color: #666; margin-bottom:20px;">
                Evaluate cloud storage strategies and optimize regional carbon footprints.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access Optimizer Tool", key="goto_cl"):
            st.session_state['page'] = 'cloud'
            st.rerun()

def render_strategic_insights():
    """Read-only insights section at the end"""
    st.markdown('<div style="margin-top:60px"></div>', unsafe_allow_html=True)
    st.markdown('### Strategic Insights', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-static">
        <span class="insight-label">Priority: High Impact</span>
        <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; margin: 5px 0;">
            Extending the average lifespan of workstations from 4 to 5 years represents the 
            most significant lever for immediate carbon reduction in IT.
        </p>
    </div>
    <div class="insight-static">
        <span class="insight-label">Governance Tip</span>
        <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; margin: 5px 0;">
            Standardizing data archival policies across Maisons can reduce redundant cloud 
            energy consumption by up to 20% annually.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div style="text-align: center; padding: 60px 0 30px 0; border-top: 1px solid #e8e4dc; margin-top: 50px;">
        <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; 
           letter-spacing: 3px; text-transform: uppercase;">
            LVMH Green in Tech · Strategy & Governance · 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN ENTRY POINT (KEPT AS REQUESTED)
# =============================================================================

def show_home_page():
    """Main function rendering the narrative-first strategy page"""
    inject_global_styles()
    
    render_logo()
    render_hero()
    
    # 1. Context (Storytelling)
    render_program_context()
    
    # 2. Structure (Pillars)
    render_pillars()
    
    # 3. Action (Tools)
    render_tools_navigation()
    
    # 4. Direction (Insights)
    render_strategic_insights()
    
    render_footer()
