import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Ensure the 'cloud' package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the cloud UI components and logic
try:
    from cloud.cloud_cal import run_cloud_optimizer
    from cloud import RULES as lifecycle_rules
except ImportError:
    # Fallback/Default Rules if not in cloud/__init__.py
    lifecycle_rules = {
        "carbon_price": 85,
        "life_factor": 0.7,
        "lag_factor": 0.7,
        "energy_penalty": 1.12,
        "lag_new_trigger": 3.0,
        "grid_factor": 0.12,
        "refurb_prod_debt": 0.10,
        "weight_multiplier": 50,
        "work_hours_week": 40,
        "weeks_per_year": 52
    }

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
            - **T1.5:** 40h/week Grid Factor multiplication.
            """)
            st.markdown("""
            **💶 Member 2: Financial Analyst**
            - **T2.1:** Monetized Carbon at **€85/ton**.
            - **T2.3:** Modeled performance lag starting at **Year 1.5** for refurbished units.
            """)
        with c2:
            st.markdown("""
            **🛒 Member 3: Procurement Lead**
            - **T3.2:** Managed the **1.2x price premium** for certified refurbished contracts.
            - **T3.4:** Integrated fixed refurbishment (€14) and recycling (€8) fees.
            """)
            st.markdown("""
            **⚙️ Member 4: Model Integration**
            - **T4.2:** Composite Scoring (Financial TCO + Weighted Carbon impact).
            - **T4.4:** Final logic gates for automated strategy recommendations.
            """)

    st.divider()
    
    # --- SIMULATOR INTEGRATION ---
    st.subheader("Interactive Lifecycle Simulator")
    
    # 1. Hardware Data Structures
    ASSET_DATA = {
        "High-End Laptop": {"price": 1500, "price_rec": 1800, "prod_co2": 350, "avg_watts": 55, "life": 4.0},
        "Corporate Smartphone": {"price": 800, "price_rec": 960, "prod_co2": 70, "avg_watts": 8, "life": 3.0},
        "Desktop Workstation": {"price": 2000, "price_rec": 2400, "prod_co2": 500, "avg_watts": 180, "life": 5.0}
    }

    PERSONA_DATA = {
        "Developer": {"salary": 65, "sens": 2.2},
        "Sales": {"salary": 45, "sens": 1.1},
        "Admin": {"salary": 30, "sens": 0.5}
    }

    COUNTRY_DATA = {
        "France": 0.055, "Germany": 0.380, "USA": 0.370, "Poland": 0.700, "UK": 0.190
    }

    # 2. Simulator Controls
    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        country_choice = st.selectbox("Operating Country", list(COUNTRY_DATA.keys()))
        device_choice = st.selectbox("Device Category", list(ASSET_DATA.keys()))
    with ctrl2:
        persona_choice = st.selectbox("Employee Persona", list(PERSONA_DATA.keys()))
        age_choice = st.slider("Current Device Age (Yrs)", 1.0, 8.0, 4.0, 0.5)
    with ctrl3:
        fin_weight = st.slider("Financial Focus (%)", 0, 100, 60)
        env_weight = 100 - fin_weight

    # 3. Calculation Logic
    def run_lifecycle_logic():
        asset = ASSET_DATA[device_choice]
        persona = PERSONA_DATA[persona_choice]
        grid = COUNTRY_DATA[country_choice]
        w_fin = fin_weight / 100
        w_env = 1 - w_fin

        # Annual Usage: 40h/week * 52 weeks
        ann_hours = 2080 
        base_kwh = (asset["avg_watts"] / 1000) * ann_hours

        # LAG CALCULATION
        def get_lag(age, is_rec):
            trigger = lifecycle_rules["lag_new_trigger"] * (lifecycle_rules["lag_factor"] if is_rec else 1.0)
            if age <= trigger: return 0
            return 30 * (age - trigger) * persona["sens"] * persona["salary"]

        # SCENARIOS
        # A: Keep
        lag_keep = get_lag(age_choice, False)
        env_keep = (base_kwh * 1.25) * grid
        m_env_keep = (env_keep / 1000) * lifecycle_rules["carbon_price"] * lifecycle_rules["weight_multiplier"]
        score_keep = (lag_keep * w_fin) + (m_env_keep * w_env)

        # B: New
        fin_new = asset["price"] / asset["life"]
        env_new = (asset["prod_co2"] / asset["life"]) + (base_kwh * grid)
        m_env_new = (env_new / 1000) * lifecycle_rules["carbon_price"] * lifecycle_rules["weight_multiplier"]
        score_new = (fin_new * w_fin) + (m_env_new * w_env)

        # C: Refurb
        ref_life = asset["life"] * lifecycle_rules["life_factor"]
        fin_ref = (asset["price_rec"] / ref_life) + get_lag(ref_life/2, True)
        env_ref = ((asset["prod_co2"] * 0.1) / ref_life) + (base_kwh * 1.12 * grid)
        m_env_ref = (env_ref / 1000) * lifecycle_rules["carbon_price"] * lifecycle_rules["weight_multiplier"]
        score_ref = (fin_ref * w_fin) + (m_env_ref * w_env)

        return {
            "keep": {"score": score_keep, "fin": lag_keep, "env": env_keep},
            "new": {"score": score_new, "fin": fin_new, "env": env_new},
            "refurb": {"score": score_ref, "fin": fin_ref, "env": env_ref}
        }

    res = run_lifecycle_logic()
    best = min(["keep", "new", "refurb"], key=lambda x: res[x]["score"])

    # 4. Result Display
    st.markdown(f"""
    <div class="recommendation-card">
        <h3 style="margin-top:0;">🏆 Recommendation: BUY {best.upper() if best != 'keep' else 'KEEP EXISTING'}</h3>
        <p>Strategy for a <b>{persona_choice}</b> in <b>{country_choice}</b> using a <b>{device_choice}</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        f_fig = go.Figure(data=[go.Bar(x=['Keep', 'New', 'Refurb'], y=[res['keep']['fin'], res['new']['fin'], res['refurb']['fin']], marker_color=['#94a3b8', '#6366f1', '#10b981'])])
        f_fig.update_layout(title="Annualized Cost (€)", height=300, template="simple_white")
        st.plotly_chart(f_fig, use_container_width=True)
    with r_col2:
        e_fig = go.Figure(data=[go.Bar(x=['Keep', 'New', 'Refurb'], y=[res['keep']['env'], res['new']['env'], res['refurb']['env']], marker_color=['#94a3b8', '#f43f5e', '#10b981'])])
        e_fig.update_layout(title="Annual Carbon (kg)", height=300, template="simple_white")
        st.plotly_chart(e_fig, use_container_width=True)

# =================================================================
# PAGE: CLOUD STORAGE ADVISOR
# =================================================================
elif page == "☁️ Cloud Storage Advisor":
    # Call the dedicated Cloud UI function from cloud_cal.py
    run_cloud_optimizer()

# Footer
st.divider()
st.caption("Green IT Framework v2.2 | Integrated Lifecycle & Cloud Storage Decisions")
