import streamlit as st
import sys
import os

# Ensure the 'cloud' package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the cloud UI components and logic
try:
    from cloud.cloud_cal import run_cloud_optimizer
    from cloud import RULES as lifecycle_rules
except ImportError:
    st.error("Missing components. Ensure 'cloud/__init__.py' and 'cloud/cloud_cal.py' are present.")

# --- SHARED UI CONFIG ---
st.set_page_config(
    page_title="Green IT Decision Model",
    page_icon="🌱",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .recommendation-card { 
        background-color: #ffffff; 
        padding: 24px; 
        border-radius: 16px; 
        border-left: 8px solid #10b981; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
st.sidebar.title("🌱 Green IT Portal")
page = st.sidebar.radio("Navigate", ["🏠 Home & Lifecycle", "☁️ Cloud Storage Advisor"])

# =================================================================
# PAGE: HOME & LIFECYCLE (Member 1-4 Logic)
# =================================================================
if page == "🏠 Home & Lifecycle":
    st.title("Green IT Lifecycle & ROI Optimization")
    st.markdown("### Strategic decision-making for a sustainable circular economy.")
    
    st.info("""
    This platform balances **Financial ROI** (Productivity vs. Amortized Cost) and 
    **Environmental ROI** (Carbon Debt vs. Credits) to help companies choose between 
    Buying New, Keeping Existing, or Buying Refurbished IT assets.
    """)

    # Methodology Section
    with st.expander("📖 View Project Methodology (Members 1-4)"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            **🌍 Member 1: Environmental Specialist**
            - **T1.2:** Implemented the **70% Lifespan Factor** for refurbished tech.
            - **T1.3:** Applied the **12% Energy Penalty** for older hardware generations.
            """)
        with c2:
            st.markdown("""
            **💶 Member 2: Financial Analyst**
            - **T2.1:** Monetized Carbon at **€85/ton**.
            - **T2.3:** Modeled performance lag starting at **Year 1.5** for refurbished units.
            """)

    st.divider()
    
    # Simple Lifecycle Dashboard (Placeholder for Member 4 Integrator)
    st.subheader("Asset Lifecycle Quick-View")
    st.write("This model calculates the composite score for hardware transitions.")
    
    lc1, lc2, lc3 = st.columns(3)
    lc1.metric("Refurb. Life", f"{int(lifecycle_rules['life_factor']*100)}%", help="Refurbished units have 70% the life of new tech.")
    lc2.metric("Lag Threshold", "2.1 Years", help="Productivity lag starts earlier on refurbished units.")
    lc3.metric("Carbon Value", f"€{lifecycle_rules['carbon_price']}/t", help="Internal carbon price for decision making.")

    st.warning("👈 Use the 'Cloud Storage Advisor' in the sidebar to run the full Data Center optimization model.")

# =================================================================
# PAGE: CLOUD STORAGE ADVISOR
# =================================================================
elif page == "☁️ Cloud Storage Advisor":
    # Call the dedicated Cloud UI function from cloud_cal.py
    run_cloud_optimizer()

# Footer
st.divider()
st.caption("Green IT Framework v2.2 | Integrated Lifecycle & Cloud Storage Decisions")
