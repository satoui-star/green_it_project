import streamlit as st
import pandas as pd

# --- ON INTÈGRE LES DONNÉES ICI POUR ÉVITER LES ERREURS D'IMPORT ---
EQUIPMENT_DB = {
    "Laptop Standard": {"co2_mfg": 280, "price": 1100},
    "Laptop High-Perf": {"co2_mfg": 450, "price": 2200},
    "Monitor 24": {"co2_mfg": 120, "price": 250},
    "Smartphone": {"co2_mfg": 80, "price": 900}
}
# -------------------------------------------------------------------

def run_simulation_ui():
    st.markdown("## 🔮 Future Impact Simulator")
    st.markdown("Predict the carbon and financial impact of your IT growth strategy.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚙️ Growth Scenarios")
        growth_rate = st.slider("Annual Headcount Growth (%)", 0, 50, 10)
        years = st.slider("Projection Period (Years)", 1, 10, 3)
        strategy = st.radio("Procurement Strategy", ["Buy New (Standard)", "Buy Refurbished (-40% CO2)"])

    with col2:
        st.subheader("🏢 Current Fleet To Expand")
        laptop_count = st.number_input("Number of Laptops", value=150)
        phone_count = st.number_input("Number of Smartphones", value=150)

    # --- CALCULS RAPIDES ---
    st.divider()
    
    # Facteur d'impact selon la stratégie
    impact_factor = 0.6 if "Refurbished" in strategy else 1.0
    cost_factor = 0.7 if "Refurbished" in strategy else 1.0

    # Projection
    future_laptops = laptop_count * ((1 + growth_rate/100) ** years)
    new_devices_needed = future_laptops - laptop_count
    
    # Impact (Laptop Standard par défaut)
    co2_impact = new_devices_needed * EQUIPMENT_DB["Laptop Standard"]["co2_mfg"] * impact_factor
    budget_impact = new_devices_needed * EQUIPMENT_DB["Laptop Standard"]["price"] * cost_factor

    # --- RÉSULTATS ---
    st.subheader(f"📊 Projection at Year {years}")
    k1, k2, k3 = st.columns(3)
    
    k1.metric("New Devices to Buy", f"{int(new_devices_needed)}")
    k2.metric("Est. Carbon Footprint", f"{co2_impact/1000:.1f} tons", 
              delta="-40%" if "Refurbished" in strategy else "Standard Impact")
    k3.metric("Est. Budget Required", f"{budget_impact/1000:.0f} k€")

    if "Refurbished" in strategy:
        st.success("✅ Excellent Strategy: Using refurbished devices for growth absorbs the carbon impact of new hires.")