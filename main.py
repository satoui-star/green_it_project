import streamlit as st
import os
import sys

# 1. SETUP
st.set_page_config(page_title="LVMH Sustainable IT", page_icon="⚜️", layout="wide")

# 2. PATHS & IMPORTS
sys.path.append(os.path.join(os.path.dirname(__file__), "equipement_audit"))
sys.path.append(os.path.join(os.path.dirname(__file__), "cloud"))

# Import your custom Utils
import utils_ui

# Import Sub-Modules
try:
    from audit_ui import run_audit_ui
except ImportError:
    run_audit_ui = None

try:
    from cloud_ui import run_cloud_ui
except ImportError:
    run_cloud_ui = None

# 3. APPLY STYLE & HEADER (From utils_ui)
utils_ui.load_lvmh_style()

# 4. NAVIGATION CALLBACK
def set_page(page_name):
    st.session_state["app_mode"] = page_name

if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "Home"

# 5. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.radio("Nav", ["Home", "Equipment Audit", "Cloud Analytics"], key="app_mode", label_visibility="collapsed")
    st.markdown("---")
    st.caption("LVMH • Green in Tech | v1.0")

# 6. LAYOUT
# We call render_header() from utils_ui
utils_ui.render_header()

content_col, assumptions_col = st.columns([3.2, 1.2], gap="large")

with content_col:
    # --- HOMEPAGE ---
    if st.session_state.app_mode == "Home":
        st.markdown(
        """
        <div class='hero'>
            <div class='hero-title'>Sustainable IT Cockpit</div>
            <div class='hero-sub'>LVMH Digital • Green in Tech Decision Support</div>
            <div class='hero-row'>
                <div class='chip'>Decision support — not execution</div>
                <div class='chip'>Financial + CO₂ + Organizational ROI</div>
            </div>
        </div>
        <br>
        """, unsafe_allow_html=True)
        
        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("IT Carbon Footprint", "4,102 tCO₂e", "-5% YoY", delta_color="inverse")
        with c2: st.metric("Active Assets", "14,205", "+12%")
        with c3: st.metric("Energy Efficiency", "85%", "+2 pts")
        with c4: st.metric("Reconditioning Rate", "32%", "+5%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation Cards with Fixed Callbacks
        m1, m2 = st.columns(2, gap="large")
        
        with m1:
            st.markdown("""
            <div class="card">
                <div class="card-title">💻 Equipment Audit</div>
                <div class="divider"></div>
                <p>Inventory analysis (CSV) + policy simulations to estimate cost, CO₂ and feasibility.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Open Equipment Audit →", on_click=set_page, args=("Equipment Audit",), width = "stretch")

        with m2:
            st.markdown("""
            <div class="card">
                <div class="card-title">☁️ Cloud Analytics</div>
                <div class="divider"></div>
                <p>Storage decision support: retention scenarios and provider comparison.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Open Cloud Analytics →", on_click=set_page, args=("Cloud Analytics",), width = "stretch")

    # --- MODULES ---
    elif st.session_state.app_mode == "Equipment Audit":
        st.markdown("## 💻 Equipment Lifecycle & ROI")
        st.markdown("---")
        if run_audit_ui:
            run_audit_ui()
        else:
            st.error("❌ Audit module not found.")

    elif st.session_state.app_mode == "Cloud Analytics":
        st.markdown("## ☁️ Cloud Storage Decision Support")
        st.markdown("---")
        if run_cloud_ui:
            run_cloud_ui()
        else:
            st.error("❌ Cloud module not found.")

    # Footer
    st.markdown("<div class='footerline'>In collaboration with Albert School • Mines Paris – PSL</div>", unsafe_allow_html=True)

# 7. RIGHT DRAWER (From utils_ui)
with assumptions_col:
    utils_ui.render_assumptions_drawer()