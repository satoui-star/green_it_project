import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURATION & CONSTANTS (Project Plan v2.0 + Country Grid Logic) ---

# Asset Data: avg_watts is used for the 40-hour week calculation
ASSET_DATA = {
    "High-End Laptop": {"price": 1500, "price_rec": 1800, "prod_co2": 350, "avg_watts": 55, "life": 4.0},
    "Corporate Smartphone": {"price": 800, "price_rec": 960, "prod_co2": 70, "avg_watts": 8, "life": 3.0},
    "Monitor / Screen": {"price": 400, "price_rec": 480, "prod_co2": 250, "avg_watts": 35, "life": 7.0}
}

PERSONA_DATA = {
    "Developer": {"salary": 60, "sens": 2.2, "desc": "High Sensitivity (Performance Critical)"},
    "Sales": {"salary": 40, "sens": 1.0, "desc": "Medium Sensitivity"},
    "Admin": {"salary": 25, "sens": 0.5, "desc": "Low Sensitivity"}
}

# Grid Emission Factors (kgCO2e per kWh) - Reference data for Member 1
COUNTRY_DATA = {
    "France": 0.055,   # Low Carbon (Nuclear/Renewables)
    "Germany": 0.380,  # Medium (Mixed)
    "USA": 0.370,      # Medium
    "Poland": 0.700,   # High (Coal-reliant)
    "UK": 0.190        # Medium-Low
}

# Global Business Rules
RULES = {
    "carbon_price": 85,      # €/ton
    "work_hours_week": 40,   # Standard work week
    "weeks_per_year": 52,    # Annual multiplication
    "life_factor": 0.7,      # 70% life for refurbished
    "lag_factor": 0.7,       # 70% lag onset (starts at 2.1y vs 3.0y)
    "energy_penalty": 1.12,  # +12% energy usage for refurbished tech
    "lag_new_trigger": 3.0,  # Standard years before new tech slows down
    "refurb_prod_debt": 0.10,# 10% refurb process debt
    "weight_multiplier": 50  # Score balancing factor
}

# --- 2. LOGIC FUNCTIONS ---

def calculate_lag_cost(age, sens, salary, is_rec=False):
    """Calculates annual productivity loss in Euros."""
    trigger = RULES["lag_new_trigger"]
    if is_rec:
        trigger = trigger * RULES["lag_factor"] 
    if age <= trigger:
        return 0
    # Average lost time scaled by years past trigger
    lost_hours = 30 * (age - trigger) * sens
    return lost_hours * salary

def run_simulation(device_name, persona_name, country_name, current_age, fin_weight_pct):
    asset = ASSET_DATA[device_name]
    persona = PERSONA_DATA[persona_name]
    grid_factor = COUNTRY_DATA[country_name]
    
    w_fin = fin_weight_pct / 100
    w_env = 1 - w_fin

    # Annual Usage Calculation (Member 1 T1.2)
    annual_usage_hours = RULES["work_hours_week"] * RULES["weeks_per_year"]
    annual_kwh_base = (asset["avg_watts"] / 1000) * annual_usage_hours

    # --- SCENARIO A: KEEP EXISTING ---
    lag_keep = calculate_lag_cost(current_age, persona["sens"], persona["salary"], is_rec=False)
    energy_keep_kwh = annual_kwh_base * 1.25 # Efficiency loss for old tech
    env_keep = energy_keep_kwh * grid_factor

    # --- SCENARIO B: BUY NEW ---
    fin_new = asset["price"] / asset["life"]
    env_new_prod = asset["prod_co2"] / asset["life"]
    env_new_usage = annual_kwh_base * grid_factor
    env_new = env_new_prod + env_new_usage

    # --- SCENARIO C: BUY REFURBISHED ---
    refurb_life = asset["life"] * RULES["life_factor"]
    amort_price_rec = asset["price_rec"] / refurb_life
    # Mid-cycle lag estimation
    lag_rec = calculate_lag_cost(refurb_life / 2, persona["sens"], persona["salary"], is_rec=True)
    fin_rec = amort_price_rec + lag_rec

    env_rec_prod = (asset["prod_co2"] * RULES["refurb_prod_debt"]) / refurb_life
    env_rec_usage = (annual_kwh_base * RULES["energy_penalty"]) * grid_factor
    env_rec = env_rec_prod + env_rec_usage

    # --- COMPOSITE SCORING ---
    m_env_keep = (env_keep / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]
    m_env_new = (env_new / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]
    m_env_rec = (env_rec / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]

    score_keep = (lag_keep * w_fin) + (m_env_keep * w_env)
    score_new = (fin_new * w_fin) + (m_env_new * w_env)
    score_rec = (fin_rec * w_fin) + (m_env_rec * w_env)

    return {
        "keep": {"fin": lag_keep, "env": env_keep, "score": score_keep, "kwh": energy_keep_kwh},
        "new": {"fin": fin_new, "env": env_new, "score": score_new, "kwh": annual_kwh_base},
        "refurb": {"fin": fin_rec, "env": env_rec, "score": score_rec, "kwh": annual_kwh_base * RULES["energy_penalty"]},
        "meta": {"grid_factor": grid_factor, "hours_yr": annual_usage_hours}
    }

# --- 3. STREAMLIT UI ---

st.set_page_config(page_title="Green IT Optimizer v2.1", layout="wide")

st.title("🌱 Green IT Lifecycle Optimizer v2.1")
st.markdown("### Energy-Aware Lifecycle Modeling")

# Sidebar
st.sidebar.header("1. Scenario Settings")
country_choice = st.sidebar.selectbox("Operating Country", list(COUNTRY_DATA.keys()))
device_choice = st.sidebar.selectbox("Device Category", list(ASSET_DATA.keys()))
persona_choice = st.sidebar.selectbox("Employee Persona", list(PERSONA_DATA.keys()))
age_choice = st.sidebar.slider("Current Asset Age (Years)", 1.0, 8.0, 4.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.header("2. Strategy Weighting")
fin_weight = st.sidebar.slider("Financial Focus (%)", 0, 100, 60)

# Run Logic
results = run_simulation(device_choice, persona_choice, country_choice, age_choice, fin_weight)
best_scenario = min(results, key=lambda x: results[x]["score"] if x != "meta" else 999999)

# Dashboard Display
st.markdown(f"**Context:** Standard {RULES['work_hours_week']}h work week in **{country_choice}** (Grid Factor: {results['meta']['grid_factor']} kg/kWh)")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if best_scenario == "keep":
        st.success("### 🏆 Recommendation: KEEP EXISTING")
    elif best_scenario == "refurb":
        st.info("### 🏆 Recommendation: BUY REFURBISHED")
    else:
        st.warning("### 🏆 Recommendation: BUY NEW TECH")
    st.write(f"Best path identified based on {fin_weight}% financial / {100-fin_weight}% environmental weighting.")

with col2:
    st.metric("Composite Score", round(results[best_scenario]["score"], 1))
with col3:
    st.metric("Annual CO2 (Best)", f"{round(results[best_scenario]['env'], 1)} kg")

# Visuals
c1, c2 = st.columns(2)
with c1:
    fig_fin = go.Figure(data=[go.Bar(x=['Keep', 'New', 'Refurb'], y=[results['keep']['fin'], results['new']['fin'], results['refurb']['fin']], marker_color=['#94a3b8', '#6366f1', '#10b981'])])
    fig_fin.update_layout(title_text='Annual Financial TCO (€)', template="simple_white")
    st.plotly_chart(fig_fin, use_container_width=True)

with c2:
    fig_env = go.Figure(data=[go.Bar(x=['Keep', 'New', 'Refurb'], y=[results['keep']['env'], results['new']['env'], results['refurb']['env']], marker_color=['#94a3b8', '#f43f5e', '#10b981'])])
    fig_env.update_layout(title_text='Annual Carbon Debt (kgCO2)', template="simple_white")
    st.plotly_chart(fig_env, use_container_width=True)

# Comparison Table
st.markdown("### Detailed Metric Breakdown")
st.table(pd.DataFrame({
    "Metric": ["Annual Usage Hours", "Energy Consumption", "Grid Factor Used", "Annual Fin. Cost", "Annual Carbon Debt"],
    "Keep": [results['meta']['hours_yr'], f"{round(results['keep']['kwh'], 1)} kWh", results['meta']['grid_factor'], f"{int(results['keep']['fin'])} €", f"{round(results['keep']['env'], 1)} kg"],
    "New": [results['meta']['hours_yr'], f"{round(results['new']['kwh'], 1)} kWh", results['meta']['grid_factor'], f"{int(results['new']['fin'])} €", f"{round(results['new']['env'], 1)} kg"],
    "Refurb": [results['meta']['hours_yr'], f"{round(results['refurb']['kwh'], 1)} kWh", results['meta']['grid_factor'], f"{int(results['refurb']['fin'])} €", f"{round(results['refurb']['env'], 1)} kg"]
}))
