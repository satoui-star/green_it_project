import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURATION & CONSTANTS (Logic from Members 1, 2, & 3) ---
ASSET_DATA = {
    "High-End Laptop": {"price": 1500, "price_rec": 1800, "prod_co2": 350, "energy": 85, "life": 3.5},
    "Corporate Smartphone": {"price": 800, "price_rec": 960, "prod_co2": 70, "energy": 12, "life": 2.5},
    "Desktop Workstation": {"price": 2000, "price_rec": 2400, "prod_co2": 500, "energy": 200, "life": 5.0}
}

PERSONA_DATA = {
    "Developer": {"salary": 65, "sens": 2.2, "desc": "High Sensitivity"},
    "Admin": {"salary": 28, "sens": 0.5, "desc": "Low Sensitivity"},
    "Sales": {"salary": 42, "sens": 1.2, "desc": "Med Sensitivity"}
}

RULES = {
    "carbon_price": 85,      # €/ton
    "life_factor": 0.7,      # 70% life for refurbished
    "energy_penalty": 1.12,  # +12% energy for refurbished
    "lag_new_trigger": 3.0,  # Years before new tech slows down
    "lag_rec_trigger": 1.5,  # Years before refurb tech slows down
    "grid_factor": 0.12,     # kgCO2/kWh
    "refurb_prod_debt": 0.10,# Only 10% production debt attributed to refurb
    "weight_multiplier": 50  # Factor to balance CO2 costs vs huge salary costs
}

# --- 2. LOGIC FUNCTIONS (Logic from Member 4) ---
def calculate_lag_cost(age, sens, salary, is_rec=False):
    """Calculates annual productivity loss in Euros."""
    trigger = RULES["lag_rec_trigger"] if is_rec else RULES["lag_new_trigger"]
    if age <= trigger:
        return 0
    # Logic: 30 hours base lost per year past trigger, scaled by sensitivity
    lost_hours = 30 * (age - trigger) * sens
    return lost_hours * salary

def run_simulation(device_name, persona_name, current_age, fin_weight_pct):
    asset = ASSET_DATA[device_name]
    persona = PERSONA_DATA[persona_name]
    w_fin = fin_weight_pct / 100
    w_env = 1 - w_fin

    # --- SCENARIO A: KEEP EXISTING ---
    lag_keep = calculate_lag_cost(current_age, persona["sens"], persona["salary"], is_rec=False)
    fin_keep = lag_keep
    # Energy penalty for older tech (25% less efficient)
    env_keep = (asset["energy"] * 1.25) * RULES["grid_factor"]

    # --- SCENARIO B: BUY NEW ---
    fin_new = asset["price"] / asset["life"] # Annualized amortization
    # Annualized CO2 = (Manufacturing / life) + usage
    env_new = (asset["prod_co2"] / asset["life"]) + (asset["energy"] * RULES["grid_factor"])

    # --- SCENARIO C: BUY REFURBISHED (v2.0 Logic) ---
    refurb_life = asset["life"] * RULES["life_factor"]
    amort_price_rec = asset["price_rec"] / refurb_life
    # Mid-life lag estimation for the new cycle
    lag_rec = calculate_lag_cost(refurb_life / 2, persona["sens"], persona["salary"], is_rec=True)
    fin_rec = amort_price_rec + lag_rec

    # Only 10% prod debt, but compressed over shorter life
    env_prod_rec = (asset["prod_co2"] * RULES["refurb_prod_debt"]) / refurb_life
    env_usage_rec = (asset["energy"] * RULES["energy_penalty"]) * RULES["grid_factor"]
    env_rec = env_prod_rec + env_usage_rec

    # --- COMPOSITE SCORING ---
    # Convert kg to Euros and scale up so Carbon impact is visible vs Salary
    m_env_keep = (env_keep / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]
    m_env_new = (env_new / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]
    m_env_rec = (env_rec / 1000) * RULES["carbon_price"] * RULES["weight_multiplier"]

    score_keep = (fin_keep * w_fin) + (m_env_keep * w_env)
    score_new = (fin_new * w_fin) + (m_env_new * w_env)
    score_rec = (fin_rec * w_fin) + (m_env_rec * w_env)

    return {
        "keep": {"fin": fin_keep, "env": env_keep, "score": score_keep, "lag": lag_keep, "life": "Extending"},
        "new": {"fin": fin_new, "env": env_new, "score": score_new, "lag": 0, "life": asset["life"]},
        "refurb": {"fin": fin_rec, "env": env_rec, "score": score_rec, "lag": lag_rec, "life": round(refurb_life, 1)},
    }

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="Green IT Optimizer v2.0", layout="wide")

st.title("🌱 Green IT Lifecycle Optimizer v2.0")
st.markdown("""
This tool simulates the **Total Cost of Ownership (TCO)** and **Carbon Debt** of IT equipment. 
It accounts for **v2.0 logic**: refurbished tech has a **70% lifespan** and starts **lagging after 1.5 years**.
""")

# Sidebar Controls
st.sidebar.header("Scenario Configuration")
device_choice = st.sidebar.selectbox("Device Category", list(ASSET_DATA.keys()))
persona_choice = st.sidebar.selectbox("Employee Persona", list(PERSONA_DATA.keys()))
age_choice = st.sidebar.slider("Current Asset Age (Years)", 1.0, 8.0, 4.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.header("Decision Weighting")
fin_weight = st.sidebar.slider("Financial ROI Weight (%)", 0, 100, 50)
env_weight = 100 - fin_weight
st.sidebar.info(f"Strategy: {fin_weight}% Finance / {env_weight}% Environment")

# Run Logic
results = run_simulation(device_choice, persona_choice, age_choice, fin_weight)

# --- 4. DISPLAY RECOMMENDATION ---
best_scenario = min(results, key=lambda x: results[x]["score"])

if best_scenario == "keep":
    st.success(f"### 🏆 Recommendation: KEEP EXISTING")
    st.write(f"Your {age_choice}-year-old hardware is still the most efficient choice for an **{persona_choice}**. The lag cost is manageable.")
elif best_scenario == "refurb":
    st.info(f"### 🏆 Recommendation: BUY REFURBISHED")
    st.write("Environmental circularity wins. Despite the **70% life** and early lag, the 90% reduction in production carbon debt is too large to ignore.")
else:
    st.warning(f"### 🏆 Recommendation: BUY NEW TECH")
    st.write(f"Productivity is critical. A **{persona_choice}** cannot afford the early performance decay of refurbished units. New tech provides the best ROI.")

# Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Composite Score", round(results[best_scenario]["score"], 1))
col2.metric("Annual Cost (Best)", f"{int(results[best_scenario]['fin'])} €")
col3.metric("Annual Carbon (Best)", f"{round(results[best_scenario]['env'], 1)} kg")

# --- 5. VISUALIZATIONS ---
c_fin1, c_env1 = st.columns(2)

with c_fin1:
    fig_fin = go.Figure(data=[
        go.Bar(name='Financial TCO (€)', x=['Keep', 'New', 'Refurb'], 
               y=[results['keep']['fin'], results['new']['fin'], results['refurb']['fin']],
               marker_color=['#94a3b8', '#6366f1', '#10b981'])
    ])
    fig_fin.update_layout(title_text='Annual Financial TCO (€)', template="simple_white", showlegend=False)
    st.plotly_chart(fig_fin, use_container_width=True)

with c_env1:
    fig_env = go.Figure(data=[
        go.Bar(name='Carbon Debt (kg)', x=['Keep', 'New', 'Refurb'], 
               y=[results['keep']['env'], results['new']['env'], results['refurb']['env']],
               marker_color=['#94a3b8', '#f43f5e', '#10b981'])
    ])
    fig_env.update_layout(title_text='Annual Carbon Debt (kgCO2)', template="simple_white", showlegend=False)
    st.plotly_chart(fig_env, use_container_width=True)

# --- 6. BREAKDOWN TABLE ---
st.markdown("### Detailed Lifecycle Comparison")
df_data = {
    "Metric": ["Effective Lifespan", "Annual Financial Cost", "↳ Incl. Lag Cost (Salary)", "Annual Carbon Debt"],
    "Keep (Current)": [
        results['keep']['life'], 
        f"{int(results['keep']['fin'])} €", 
        f"{int(results['keep']['lag'])} €", 
        f"{round(results['keep']['env'], 1)} kg"
    ],
    "Buy New": [
        f"{results['new']['life']} Yrs", 
        f"{int(results['new']['fin'])} €", 
        "0 €", 
        f"{round(results['new']['env'], 1)} kg"
    ],
    "Buy Refurbished": [
        f"{results['refurb']['life']} Yrs", 
        f"{int(results['refurb']['fin'])} €", 
        f"~{int(results['refurb']['lag'])} €", 
        f"{round(results['refurb']['env'], 1)} kg"
    ]
}
st.table(pd.DataFrame(df_data))

st.markdown("---")
st.caption("Logic derived from Member 1-4 Tasks (v2.0) • Shorter Lifecycle (70%) and Early Decay (1.5yr) enabled.")
