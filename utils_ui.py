"""
LVMH Green in Tech - Strategic Program Homepage
Narrative-First Redesign - Executive Focus
"""

import streamlit as st
import os
import base64
from datetime import datetime

def render_logo():
    """Render the LVMH logo image with a fallback to text if the file is missing."""
    
    logo_path = "logo/lvmh_logo.png" 

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        st.markdown(f"""
        <div class="logo-section" style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{encoded}" alt="LVMH Logo" style="width: 250px; max-width: 100%; margin-bottom: 10px;">
            <div class="logo-tagline" style="font-family: 'Lato', sans-serif; font-size: 10px; letter-spacing: 4px; color: #666; text-transform: uppercase; margin-top: 5px;">
                Green in Tech Program
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="logo-section" style="text-align: center; margin-bottom: 20px;">
            <div style="font-family: 'Playfair Display', serif; font-size: 60px; color: #C5A059; letter-spacing: 8px; margin-bottom: 0px;">LVMH</div>
            <div class="logo-tagline" style="font-family: 'Lato', sans-serif; font-size: 10px; letter-spacing: 4px; color: #666; text-transform: uppercase;">
                Green in Tech Program
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# GLOBAL STYLES - LIGHT LUXURY THEME
# =============================================================================

def inject_global_styles():
    """Light luxury LVMH styling - cream/white background"""
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
    
    /* === HERO SECTION - ENHANCED === */
    .hero-section {
        background: linear-gradient(135deg, #fff 0%, #f8f6f2 50%, #fff 100%);
        border: 1px solid #e8e4dc;
        border-radius: 12px;
        padding: 80px 60px;
        margin: 35px 0 60px 0;
        text-align: center;
        box-shadow: 0 6px 30px rgba(138, 108, 74, 0.08);
        position: relative;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 120px;
        height: 4px;
        background: linear-gradient(90deg, #8a6c4a, #b8956e);
        border-radius: 0 0 4px 4px;
    }
    
    .hero-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 3.5rem !important;
        color: #2c2c2c !important;
        margin-bottom: 25px !important;
        line-height: 1.2 !important;
        font-weight: 500 !important;
        letter-spacing: 3px !important;
    }
    
    .hero-mission {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem;
        color: #555;
        line-height: 2;
        max-width: 750px;
        margin: 0 auto 20px auto;
        font-weight: 400;
    }
    
    .hero-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.95rem;
        color: #888;
        line-height: 1.8;
        max-width: 650px;
        margin: 20px auto 0 auto;
        font-weight: 400;
    }
    
    /* === CONTEXT BLOCKS - RICH & IMPACTFUL === */
    .context-container {
        margin: 60px 0;
    }
    
    .context-block {
        background: #fff;
        border-left: 4px solid #8a6c4a;
        border-radius: 0 10px 10px 0;
        padding: 35px 40px;
        margin: 25px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .context-block:hover {
        box-shadow: 0 8px 35px rgba(138, 108, 74, 0.12);
        transform: translateX(5px);
    }
    
    .context-label {
        font-family: 'Montserrat', sans-serif;
        color: #8a6c4a;
        font-size: 0.65rem;
        font-weight: 700;
        margin-bottom: 18px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .context-title {
        font-family: 'Playfair Display', serif;
        color: #2c2c2c;
        font-size: 1.6rem;
        margin-bottom: 18px;
        font-weight: 500;
        letter-spacing: 1px;
    }
    
    .context-text {
        font-family: 'Cormorant Garamond', serif;
        color: #555;
        line-height: 2;
        font-size: 1.15rem;
        font-weight: 400;
    }
    
    /* === PILLAR CARDS - ENHANCED === */
    .pillar-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 10px;
        padding: 40px 25px;
        text-align: center;
        transition: all 0.4s ease;
        height: 100%;
        cursor: pointer;
        position: relative;
    }
    
    .pillar-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #8a6c4a, transparent);
        border-radius: 10px 10px 0 0;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .pillar-card:hover::before {
        opacity: 1;
    }
    
    .pillar-card:hover {
        border-color: #8a6c4a;
        box-shadow: 0 8px 30px rgba(138, 108, 74, 0.15);
        transform: translateY(-8px);
    }
    
    .pillar-icon {
        font-size: 2.5rem;
        margin-bottom: 20px;
        color: #8a6c4a;
        transition: transform 0.3s ease;
    }
    
    .pillar-card:hover .pillar-icon {
        transform: scale(1.1);
    }
    
    .pillar-title {
        font-family: 'Playfair Display', serif;
        color: #2c2c2c;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 15px;
        letter-spacing: 1px;
    }
    
    .pillar-desc {
        font-family: 'Cormorant Garamond', serif;
        color: #777;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 12px;
    }
    
    .pillar-why {
        font-family: 'Montserrat', sans-serif;
        color: #8a6c4a;
        font-size: 0.75rem;
        font-style: italic;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #f0ece4;
    }
    
    /* === TOOL CARDS - PRIMARY ACTIONS === */
    .tool-card {
        background: linear-gradient(135deg, #fff 0%, #fafaf8 100%);
        border: 2px solid #e8e4dc;
        border-radius: 12px;
        padding: 45px 35px;
        text-align: center;
        transition: all 0.4s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .tool-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(138, 108, 74, 0.05) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .tool-card:hover::before {
        opacity: 1;
    }
    
    .tool-card:hover {
        border-color: #8a6c4a;
        box-shadow: 0 12px 50px rgba(138, 108, 74, 0.2);
        transform: translateY(-10px);
    }
    
    .tool-icon {
        font-size: 3.5rem;
        margin-bottom: 25px;
        color: #8a6c4a;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .tool-card:hover .tool-icon {
        transform: scale(1.15);
    }
    
    .tool-title {
        font-family: 'Playfair Display', serif !important;
        color: #2c2c2c !important;
        font-size: 1.8rem;
        margin-bottom: 15px;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    .tool-benefit {
        font-family: 'Cormorant Garamond', serif;
        color: #666;
        font-size: 1.1rem;
        line-height: 1.7;
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
    }
    
    /* === INSIGHT CARDS - READ ONLY === */
    .insight-card-static {
        background: linear-gradient(135deg, #f8fbf9 0%, #fff 100%);
        border: 1px solid #d4e7d7;
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .insight-card-static:hover {
        box-shadow: 0 6px 25px rgba(46, 125, 50, 0.1);
    }
    
    .insight-impact {
        display: inline-block;
        font-family: 'Montserrat', sans-serif;
        color: #2e7d32;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 6px 14px;
        background: #e8f5e9;
        border-radius: 20px;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .insight-impact.medium {
        color: #f57c00;
        background: #fff3e0;
    }
    
    .insight-statement {
        font-family: 'Cormorant Garamond', serif;
        color: #2c2c2c;
        font-size: 1.25rem;
        line-height: 1.8;
        font-weight: 500;
    }
    
    /* === SECTION HEADERS === */
    .section-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 70px 0 40px 0;
        padding-bottom: 20px;
        border-bottom: 2px solid #e8e4dc;
    }
    
    .section-icon {
        font-size: 1.5rem;
        color: #8a6c4a;
    }
    
    .section-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 2rem !important;
        color: #8a6c4a !important;
        margin: 0 !important;
        font-weight: 500 !important;
        letter-spacing: 1.5px !important;
    }
    
    /* === DIVIDERS === */
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4cfc5, transparent);
        margin: 70px 0;
    }
    
    /* === STREAMLIT BUTTON OVERRIDES === */
    .stButton > button {
        background: #8a6c4a !important;
        color: #fff !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 16px 40px !important;
        border-radius: 8px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 0.8rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(138, 108, 74, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: #6d553a !important;
        box-shadow: 0 8px 30px rgba(138, 108, 74, 0.35) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE SECTIONS
# =============================================================================

def render_hero_section():
    """Enhanced hero section - Strategic positioning"""
    st.markdown(f"""
    <div class="hero-section">
        <h1 class="hero-title">Green in Tech</h1>
        <p class="hero-mission">
            Embedding sustainability into technology decisions across all LVMH Maisons
        </p>
        <p class="hero-subtitle">
            A strategic program to measure, reduce, and master the environmental 
            footprint of our IT infrastructure while maintaining operational excellence
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_program_context():
    """Rich, narrative-driven context - No numbers, pure strategy"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🎯</span>
        <h2 class="section-title">Program Context</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="context-container">
        <div class="context-block">
            <div class="context-label">Purpose</div>
            <div class="context-title">Why Green in Tech Exists</div>
            <p class="context-text">
                Technology is integral to LVMH's operations, creativity, and customer experience. 
                Yet it carries an environmental cost. Green in Tech was created to ensure that 
                our technological advancement aligns with our environmental commitments, transforming 
                IT from a passive consumer of resources into an active driver of sustainability.
            </p>
        </div>
        
        <div class="context-block">
            <div class="context-label">Vision</div>
            <div class="context-title">Our Long-Term Ambition</div>
            <p class="context-text">
                To establish LVMH as a leader in sustainable luxury technology—where every device, 
                server, and cloud service is optimized not just for performance and security, but 
                for environmental responsibility. We envision an IT landscape that respects both 
                craftsmanship and the planet.
            </p>
        </div>
        
        <div class="context-block">
            <div class="context-label">Scope</div>
            <div class="context-title">What We Address</div>
            <p class="context-text">
                Green in Tech encompasses the entire IT lifecycle across all Maisons: from device 
                procurement and usage patterns to data center operations, cloud infrastructure, 
                and end-of-life equipment management. It spans hardware, software, and the human 
                behaviors that shape our technological footprint.
            </p>
        </div>
        
        <div class="context-block">
            <div class="context-label">Commitment</div>
            <div class="context-title">Our Pledge to LIFE 360</div>
            <p class="context-text">
                As part of LVMH's LIFE 360 program—an alliance of Nature and Creativity—Green in Tech 
                commits to reducing our IT environmental footprint by twenty percent by 2026 compared 
                to our 2021 baseline. This is not merely a target; it is a transformation of how we 
                think about, deploy, and manage technology.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_strategic_pillars():
    """Enhanced strategic pillars - Clickable, rich descriptions"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🏛</span>
        <h2 class="section-title">Strategic Pillars</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #777; font-size: 0.95rem; margin-bottom: 35px; font-family: 'Cormorant Garamond', serif; line-height: 1.8;">
        Our approach is built on four interconnected pillars that guide decision-making, 
        measurement, and continuous improvement across the program.
    </p>
    """, unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    
    pillars = [
        {
            "icon": "🔄",
            "title": "Harmonize",
            "desc": "Align sustainability initiatives across all Maisons and geographies",
            "why": "Reduces fragmentation and amplifies collective impact"
        },
        {
            "icon": "📊",
            "title": "Define & Monitor",
            "desc": "Establish clear KPIs and track environmental performance at Group level",
            "why": "Enables data-driven decisions and accountability"
        },
        {
            "icon": "🎛",
            "title": "Master",
            "desc": "Take control of IT environmental impact through governance and best practices",
            "why": "Transforms reactive compliance into proactive leadership"
        },
        {
            "icon": "🚀",
            "title": "Develop",
            "desc": "Build and evolve a long-term sustainable IT strategy",
            "why": "Ensures continuous improvement and innovation"
        }
    ]
    
    for col, pillar in zip([p1, p2, p3, p4], pillars):
        with col:
            st.markdown(f"""
            <div class="pillar-card">
                <div class="pillar-icon">{pillar['icon']}</div>
                <div class="pillar-title">{pillar['title']}</div>
                <p class="pillar-desc">{pillar['desc']}</p>
                <p class="pillar-why">Why it matters: {pillar['why']}</p>
            </div>
            """, unsafe_allow_html=True)


def render_tools_section():
    """Primary action section - Navigate to analytical tools"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🛠</span>
        <h2 class="section-title">Analytical Tools</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #777; font-size: 0.95rem; margin-bottom: 40px; font-family: 'Cormorant Garamond', serif; line-height: 1.8;">
        Access specialized tools to analyze specific aspects of your IT environmental footprint 
        and receive actionable recommendations.
    </p>
    """, unsafe_allow_html=True)
    
    tool1, tool2 = st.columns(2)
    
    with tool1:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">🖥</div>
            <div class="tool-title">Equipment Audit</div>
            <p class="tool-benefit">
                Analyze device lifecycle, identify replacement opportunities, 
                and calculate ROI for equipment optimization strategies
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Equipment Audit", key="nav_equipment", use_container_width=True):
            st.session_state['page'] = 'equipment'
            st.rerun()
    
    with tool2:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">☁</div>
            <div class="tool-title">Cloud Optimizer</div>
            <p class="tool-benefit">
                Optimize cloud storage footprint, plan archival strategies, 
                and reduce data center energy consumption
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Cloud Optimizer", key="nav_cloud", use_container_width=True):
            st.session_state['page'] = 'cloud'
            st.rerun()


def render_strategic_insights():
    """Insight-only section - No buttons, reflective content"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">💡</span>
        <h2 class="section-title">Strategic Insights</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #777; font-size: 0.95rem; margin-bottom: 35px; font-family: 'Cormorant Garamond', serif; line-height: 1.8;">
        Key observations and opportunities identified through our ongoing analysis. 
        These insights guide strategic planning and investment decisions.
    </p>
    """, unsafe_allow_html=True)
    
    insights = [
        {
            "impact": "HIGH IMPACT",
            "level": "high",
            "statement": "Server consolidation and virtualization represent the single largest opportunity to reduce energy consumption across our IT infrastructure. Early analysis suggests potential reductions of 15-20% in data center energy usage."
        },
        {
            "impact": "HIGH IMPACT",
            "level": "high",
            "statement": "Device lifecycle extension beyond the current 4-year average could deliver substantial financial and environmental returns. Each additional year of use avoids approximately 300 kg of CO₂ equivalent per device."
        },
        {
            "impact": "MEDIUM IMPACT",
            "level": "medium",
            "statement": "Migration to carbon-optimized cloud regions, particularly for non-latency-sensitive workloads, could reduce our cloud carbon footprint by 25-30% without compromising performance."
        },
        {
            "impact": "MEDIUM IMPACT",
            "level": "medium",
            "statement": "Standardization of device procurement across Maisons would improve our negotiating position for sustainable hardware and streamline circular economy initiatives at end-of-life."
        }
    ]
    
    for insight in insights:
        st.markdown(f"""
        <div class="insight-card-static">
            <span class="insight-impact {insight['level']}">{insight['impact']}</span>
            <p class="insight-statement">{insight['statement']}</p>
        </div>
        """, unsafe_allow_html=True)


def render_footer():
    """Footer section"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 0 30px 0;">
        <p style="font-family: 'Montserrat', sans-serif; color: #aaa; font-size: 0.7rem; 
           letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px;">
            LVMH Green in Tech Program
        </p>
        <p style="font-family: 'Cormorant Garamond', serif; color: #bbb; font-size: 0.85rem;">
            Strategic Sustainability · Alberthon 2025
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN HOMEPAGE FUNCTION
# =============================================================================

def show_home_page():
    """Main function - Narrative-first strategic page"""
    inject_global_styles()
    
    render_logo()
    render_hero_section()
    render_program_context()
    render_strategic_pillars()
    render_tools_section()
    render_strategic_insights()
    render_footer()
