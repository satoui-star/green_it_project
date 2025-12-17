import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURATION & CONSTANTS (Project Plan v2.0) ---
ASSET_DATA = {
    "High-End Laptop": {"price": 1500, "price_rec": 1800, "prod_co2": 350, "energy": 80, "life": 4.0},
    "Corporate Smartphone": {"price": 800, "price_rec": 960, "prod_co2": 70, "energy": 15, "life": 3.0},
    "Monitor / Screen": {"price": 400, "price_rec": 480, "prod_co2": 250, "energy": 50, "life": 7.0}
}

PERSONA_DATA = {
    "Developer": {"salary": 60, "sens": 2.2, "desc": "High Sensitivity (Performance Critical)"},
    "Sales": {"salary": 40, "sens": 1.0, "desc": "Medium Sensitivity"},
    "Admin": {"salary": 25, "sens": 0.5, "desc": "Low Sensitivity"}
}

# Advanced Logic Constants (70% Rules)
RULES = {
    "carbon_price": 85,      # €/ton
    "life_factor": 0.7,      # 70% life for refurbished
    "lag_factor": 0.7,       # 70% performance threshold (Lag begins at 2.1y vs 3.0y)
    "energy_penalty": 1.12,  # +12% energy usage for refurbished tech
    "lag_new_trigger": 3.0,  # Standard years before new tech slows down
    "grid_factor": 0.12,     # kgCO2/kWh
    "refurb_prod_debt": 0.10,# Only 10% production debt attributed to refurb
    "weight_multiplier": 50  # Factor to balance CO2 costs vs salary costs in score
}

# --- 2. LOGIC FUNCTIONS ---
def calculate_lag_cost(age, sens, salary, is_rec=False):
    """Calculates annual productivity loss in Euros."""
    # Refurbished lag trigger is now 70% of the new trigger (3.0 * 0.7 = 2.1)
    trigger = RULES["lag_new_trigger"]
    if is_rec:
        trigger = trigger * RULES["lag_factor"] 
        
    if age <= trigger:
        return 0
    
    # 30 hours base lost per year past trigger, scaled by persona sensitivity
    lost_hours = 30 * (age - trigger) * sens
    return lost_hours * salary

def run_simulation(device_name, persona_name, current_age, fin_weight_pct):
    asset = ASSET_DATA[device_name]
    persona = PERSONA_DATA[persona_name]
    w_fin = fin_weight_pct / 100
    w_env = 1 - w_fin

    # --- SCENARIO A: KEEP EXISTING (Status Quo) ---
    lag_keep = calculate_lag_cost(current_age, persona["sens"], persona["salary"], is_rec=False)
    fin_keep = lag_keep
    # Older hardware efficiency penalty (25% worse than baseline)
    energy_usage_keep = (asset["energy"] * 1.25) * RULES["grid_factor"]
    env_keep = energy_usage_keep

    # --- SCENARIO B: BUY NEW ---
    effective_life_new = asset["life"]
    fin_new = asset["price"] / effective_life_new
    # Manufacturing debt + usage
    env_new = (asset["prod_co2"] / effective_life_new) + (asset["energy"] * RULES["grid_factor"])

    # --- SCENARIO C: BUY REFURBISHED ---
    # Apply 70% rule to lifespan (Higher annualized CAPEX)
    refurb_life = asset["life"] * RULES["life_factor"]
    amort_price_rec = asset["price_rec"] / refurb_life
    
    # Calculate mid-cycle lag for the refurbished period
    avg_age_refurb = refurb_life / 2
    lag_rec = calculate_lag_cost(avg_age_refurb, persona["sens"], persona["salary"], is_rec=True)
    fin_rec = amort_price_rec + lag_rec

    # Env: 10% production debt compressed over shorter life + 12% energy penalty
    env_prod_rec = (asset["prod_co2"] * RULES["refurb_prod_debt"]) / refurb_life
    env_usage_rec = (asset["energy"] * RULES["energy_penalty"]) * RULES["grid_factor"]
    env_rec = env_prod_rec + env_usage_rec

    # --- COMPOSITE SCORING ---
    # Monetary conversion of Carbon
    m_env_keep = (env_keep / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]
    m_env_new = (env_new / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]
    m_env_rec = (env_rec / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]

    score_keep = (fin_keep * w_fin) + (m_env_keep * w_env)
    score_new = (fin_new * w_fin) + (m_env_new * w_env)
    score_rec = (fin_rec * w_fin) + (m_env_rec * w_env)

    return {
        "keep": {"fin": fin_keep, "env": env_keep, "score": score_keep, "lag": lag_keep, "life": "Extending"},
        "new": {"fin": fin_new, "env": env_new, "score": score_new, "lag": 0, "life": effective_life_new},
        "refurb": {"fin": fin_rec, "env": env_rec, "score": score_rec, "lag": lag_rec, "life": round(refurb_life, 1)},
    }

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="Green IT Optimizer v2.0", layout="wide")

st.title("🌱 Green IT Lifecycle Optimizer v2.0")
st.markdown(f"""
This engine uses **Advanced Lifecycle Modeling** to compare IT hardware strategies. 
- **The 70% Rule**: Refurbished units have a **{int(RULES['life_factor']*100)}% lifespan** and performance decay starts at **{round(RULES['lag_new_trigger'] * RULES['lag_factor'], 1)} years**.
- **The TCO Factor**: Accounts for salary productivity loss vs. manufacturing carbon debt.
""")

# Sidebar
st.sidebar.header("1. Input Parameters")
device_choice = st.sidebar.selectbox("Device Category", list(ASSET_DATA.keys()))
persona_choice = st.sidebar.selectbox("Employee Persona", list(PERSONA_DATA.keys()))
age_choice = st.sidebar.slider("Current Asset Age (Years)", 1.0, 8.0, 4.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.header("2. Decision Weighting")
fin_weight = st.sidebar.slider("Financial Focus (%)", 0, 100, 60)
env_weight = 100 - fin_weight

# Calculation
results = run_simulation(device_choice, persona_choice, age_choice, fin_weight)
best_scenario = min(results, key=lambda x: results[x]["score"])

# --- 4. DASHBOARD DISPLAY ---
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if best_scenario == "keep":
        st.success("### 🏆 Recommendation: KEEP EXISTING")
        st.write(f"The productivity lag on your {age_choice}-year-old device is currently manageable. Delaying purchase is the most efficient choice.")
    elif best_scenario == "refurb":
        st.info("### 🏆 Recommendation: BUY REFURBISHED")
        st.write(f"Despite the shorter lifecycle, the 90% manufacturing carbon saving outweighs the financial premium for an **{persona_choice}**.")
    else:
        st.warning("### 🏆 Recommendation: BUY NEW TECH")
        st.write(f"Productivity is critical for a **{persona_choice}**. The earlier performance decay of refurbished units makes New hardware the better long-term TCO.")

with col2:
    st.metric("Composite Score", round(results[best_scenario]["score"], 1))

with col3:
    st.metric("Annual Carbon (Best)", f"{round(results[best_scenario]['env'], 1)} kg")

# Visualizations
st.markdown("### Visual Comparison")
c_fin, c_env = st.columns(2)

with c_fin:
    fig_fin = go.Figure(data=[go.Bar(
        x=['Keep Existing', 'Buy New', 'Buy Refurb'],
        y=[results['keep']['fin'], results['new']['fin'], results['refurb']['fin']],
        marker_color=['#94a3b8', '#6366f1', '#10b981']
    )])
    fig_fin.update_layout(title_text='Annual Financial TCO (€)', template="simple_white", showlegend=False)
    st.plotly_chart(fig_fin, use_container_width=True)

with c_env:
    fig_env = go.Figure(data=[go.Bar(
        x=['Keep Existing', 'Buy New', 'Buy Refurb'],
        y=[results['keep']['env'], results['new']['env'], results['refurb']['env']],
        marker_color=['#94a3b8', '#f43f5e', '#10b981']
    )])
    fig_env.update_layout(title_text='Annual Carbon Debt (kgCO2)', template="simple_white", showlegend=False)
    st.plotly_chart(fig_env, use_container_width=True)

# Detailed Table
st.markdown("### Detailed Lifecycle Metrics")
st.table(pd.DataFrame({
    "Metric": ["Effective Lifespan", "Performance Lag Trigger", "Annual Financial Cost", "↳ Incl. Salary Lag Cost", "Annual Carbon Debt"],
    "Keep (Status Quo)": [results['keep']['life'], f"{RULES['lag_new_trigger']} Yrs", f"{int(results['keep']['fin'])} €", f"{int(results['keep']['lag'])} €", f"{round(results['keep']['env'], 1)} kg"],
    "Buy New": [f"{results['new']['life']} Yrs", f"{RULES['lag_new_trigger']} Yrs", f"{int(results['new']['fin'])} €", "0 €", f"{round(results['new']['env'], 1)} kg"],
    "Buy Refurbished": [f"{results['refurb']['life']} Yrs", f"{round(RULES['lag_new_trigger'] * RULES['lag_factor'], 1)} Yrs", f"{int(results['refurb']['fin'])} €", f"~{int(results['refurb']['lag'])} €", f"{round(results['refurb']['env'], 1)} kg"]
}))
