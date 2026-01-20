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
    page_title="LVMH Green in Tech",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# PATH SETUP
# =============================================================================
# Ensure Python can find our modules
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'cloud'))
sys.path.insert(0, os.path.join(current_dir, 'equipement_audit'))

# =============================================================================
# IMPORTS
# =============================================================================
from utils_ui import show_home_page, inject_global_styles

# Import your existing modules
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
# SESSION STATE INITIALIZATION
# =============================================================================
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

# =============================================================================
# BACK BUTTON COMPONENT
# =============================================================================
def render_back_button():
    """Render a styled back button to return to homepage"""
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← Back to Dashboard", key="back_btn", type="secondary"):
            st.session_state['page'] = 'home'
            st.rerun()

# =============================================================================
# PAGE ROUTING
# =============================================================================

# HOME PAGE
if st.session_state['page'] == 'home':
    show_home_page()

# EQUIPMENT AUDIT PAGE
elif st.session_state['page'] == 'equipment':
    inject_global_styles()
    render_back_button()
    st.markdown("---")
    
    if AUDIT_AVAILABLE:
        # Try different function names based on your audit_ui.py structure
        if hasattr(audit_ui, 'render_audit_section'):
            audit_ui.render_audit_section()
        elif hasattr(audit_ui, 'run'):
            audit_ui.run()
        else:
            st.error("""
            ⚠️ **Module Configuration Issue**
            
            The `audit_ui.py` file was found but doesn't have the expected function.
            
            Please ensure your `audit_ui.py` has one of these functions:
            - `render_audit_section()`
            - `run()`
            """)
            st.code("""
# Add this at the end of audit_ui.py:
def run():
    render_audit_section()
            """)
    else:
        st.error(f"""
        ⚠️ **Equipment Audit Module Not Found**
        
        Error: `{audit_error}`
        
        Please ensure:
        1. The `equipement_audit` folder exists
        2. It contains `audit_ui.py`
        3. It contains `__init__.py`
        """)

# CLOUD OPTIMIZER PAGE  
elif st.session_state['page'] == 'cloud':
    inject_global_styles()
    render_back_button()
    st.markdown("---")
    
    if CLOUD_AVAILABLE:
        # Try different function names based on your cloud_ui.py structure
        if hasattr(cloud_ui, 'render_cloud_section'):
            cloud_ui.render_cloud_section()
        elif hasattr(cloud_ui, 'run'):
            cloud_ui.run()
        else:
            st.error("""
            ⚠️ **Module Configuration Issue**
            
            The `cloud_ui.py` file was found but doesn't have the expected function.
            
            Please ensure your `cloud_ui.py` has one of these functions:
            - `render_cloud_section()`
            - `run()`
            """)
            st.code("""
# Add this at the end of cloud_ui.py:
def run():
    render_cloud_section()
            """)
    else:
        st.error(f"""
        ⚠️ **Cloud Optimizer Module Not Found**
        
        Error: `{cloud_error}`
        
        Please ensure:
        1. The `cloud` folder exists
        2. It contains `cloud_ui.py`
        3. It contains `__init__.py`
        """)

# =============================================================================
# FALLBACK FOR UNKNOWN PAGES
# =============================================================================
else:
    st.session_state['page'] = 'home'
    st.rerun()
