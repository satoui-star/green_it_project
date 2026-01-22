"""
LVMH Green in Tech - Main Application
Navigation hub connecting Homepage, Equipment Audit, and Cloud Optimizer
"""

import streamlit as st
import sys
import os

# =============================================================================
# PAGE CONFIGURATION (Must be first Streamlit command)
# =============================================================================
st.set_page_config(
    page_title="Elysia home page",
    page_icon="logo.png/elysia_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# PATH SETUP
# =============================================================================
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'cloud'))
sys.path.insert(0, os.path.join(current_dir, 'equipement_audit'))

# =============================================================================
# IMPORTS
# =============================================================================
from utils_ui import show_home_page, inject_global_styles

try:
    from cloud import cloud_ui
    CLOUD_AVAILABLE = True
except ImportError as e:
    CLOUD_AVAILABLE = False
    cloud_error = str(e)

try:
    from equipement_audit import audit_ui
    AUDIT_AVAILABLE = True
except ImportError as e:
    AUDIT_AVAILABLE = False
    audit_error = str(e)

# =============================================================================
# SESSION STATE
# =============================================================================
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

# =============================================================================
# PAGE ROUTING
# =============================================================================

# HOME PAGE
if st.session_state['page'] == 'home':
    show_home_page()

# EQUIPMENT AUDIT PAGE
elif st.session_state['page'] == 'equipment':
    # NE PAS appeler inject_global_styles() ici!
    # audit_ui a son propre CSS
    
    # Back button avec style qui match audit_ui
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Force light theme everywhere */
    .stApp, [data-testid="stAppViewContainer"], .main, .block-container,
    [data-testid="stHeader"], section[data-testid="stSidebar"] {
        background: #FAFAF8 !important;
        background-color: #FAFAF8 !important;
    }
    
    /* Override dark mode */
    [data-theme="dark"] .stApp,
    [data-theme="dark"] [data-testid="stAppViewContainer"] {
        background: #FAFAF8 !important;
    }
    
    /* Back button style */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #F5F4F0 0%, #E8E6E0 100%) !important;
    color: #1a1a1a !important;
    border: 1.5px solid #8a6c4a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #8a6c4a 0%, #6d5539 100%) !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(138, 108, 74, 0.3) !important;
}
    
    
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(138, 108, 74, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← Dashboard", key="back_btn"):
            st.session_state['page'] = 'home'
            st.rerun()
    
    if AUDIT_AVAILABLE:
        if hasattr(audit_ui, 'render_audit_section'):
            audit_ui.render_audit_section()
        elif hasattr(audit_ui, 'run'):
            audit_ui.run()
        else:
            st.error("Module audit_ui non configuré correctement")
    else:
        st.error(f"Module Equipment Audit non trouvé: {audit_error}")

# CLOUD OPTIMIZER PAGE  
elif st.session_state['page'] == 'cloud':
    inject_global_styles()
    
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← Back to Dashboard", key="back_btn", type="secondary"):
            st.session_state['page'] = 'home'
            st.rerun()
    
    st.markdown("---")
    
    if CLOUD_AVAILABLE:
        if hasattr(cloud_ui, 'render_cloud_section'):
            cloud_ui.render_cloud_section()
        elif hasattr(cloud_ui, 'run'):
            cloud_ui.run()
        else:
            st.error("Module cloud_ui non configuré correctement")
    else:
        st.error(f"Module Cloud Optimizer non trouvé: {cloud_error}")

# FALLBACK
else:
    st.session_state['page'] = 'home'
    st.rerun()