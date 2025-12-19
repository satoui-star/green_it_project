import streamlit as st
import pandas as pd
import altair as alt
import os
# 👇 STRICTLY IMPORTING FROM YOUR API FILE
from reference_data_API import PERSONAS, LOCAL_DB
from calculator import SmartCalculator

CSV_FILE = "my_fleet_inventory.csv"

# Define theme colors for Altair charts
THEME_GOLD = '#8a6c4a'
THEME_RED_MUTED = '#A65D57' # Muted brick red for negative/costs
THEME_GREEN_MUTED = '#7A9A7E' # Muted sage for environmental wins
THEME_GREY = '#999999'

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Device ID", "Persona", "Device Type", "Age (Years)"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def run_audit_ui():
    st.markdown("### 🧭 Decision Support System: Green IT Audit")
    
    # --- 1. DATA INPUT ---
    df_inventory = load_data()
    with st.expander("📥 Input / Inventory Management", expanded=(len(df_inventory) == 0)):
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        with c1: persona = st.selectbox("Persona Profile", list(PERSONAS.keys()))
        with c2: dtype = st.selectbox("Hardware Type", list(LOCAL_DB.keys()))
        with c3: age = st.number_input("Age (Yrs)", 0.0, 15.0, 4.0, 0.5)
        with c4: 
            st.write("") # Spacer
            if st.button("➕ Add Asset"):
                new_id = f"DEV-{len(df_inventory)+1:03d}"
                new_row = {"Device ID": new_id, "Persona": persona, "Device Type": dtype, "Age (Years)": age}
                df_inventory = pd.concat([df_inventory, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_inventory)
                st.rerun()

    # --- 2. INTELLIGENT ANALYSIS ---
    if not df_inventory.empty:
        # Run calculation
        df_analyzed = SmartCalculator.process_inventory(df_inventory)
        st.markdown("---")

        # --- A. EXECUTIVE SUMMARY (Top Level) ---
        tot_fin_roi = df_analyzed["Financial ROI (€)"].sum()
        tot_env_roi = df_analyzed["Env. ROI (kg)"].sum()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # KPI 1: Financial (Fix: Red if negative)
        fin_color = "normal" # Green/Gold by default
        if tot_fin_roi < 0:
             fin_color = "inverse" # Red if losing money

        kpi1.metric(
            "💰 Net Financial ROI", 
            f"€{tot_fin_roi:,.0f}", 
            delta="vs Keeping Old Devices",
            delta_color=fin_color,
            help="Total Money Saved by replacing recommended devices (Salary Efficiency - Hardware Cost)"
        )

        # KPI 2: Environmental (Smart Labeling)
        if tot_env_roi < 0:
            env_label = "🌍 Net Carbon Debt"
            env_val = f"{abs(tot_env_roi):.1f} kg" # Show positive number for debt
            env_color = "inverse" # Red
            env_help = "You are adding Carbon to the atmosphere by manufacturing new devices."
        else:
            env_label = "🌍 Net Carbon Saved"
            env_val = f"{tot_env_roi:.1f} kg"
            env_color = "normal" # Green
            env_help = "You are saving Carbon because the new devices are much more efficient."

        kpi2.metric(
            env_label, 
            env_val,
            delta="vs Keeping Old Devices",
            delta_color=env_color,
            help=env_help
        )
        
        # KPI 3: Strategy
        if tot_fin_roi > 0 and tot_env_roi < 0:
            strategy_text = "⚠️ Trade-off: Profitable, but increases Carbon."
        elif tot_fin_roi > 0 and tot_env_roi > 0:
            strategy_text = "✅ Win-Win: Saves Money AND Carbon."
        elif tot_fin_roi < 0:
             strategy_text = "📉 No Action Needed: Keeping current devices is cheaper."
        else:
            strategy_text = "ℹ️ Optimization Required."
            
        kpi3.info(f"**Strategy:** {strategy_text}")

        # --- B. DUAL-LENS ANALYSIS (Tabs) ---
        tab_money, tab_planet, tab_matrix = st.tabs(["💰 CFO View (Financial)", "🌿 CSO View (Environmental)", "📋 Decision Matrix"])
        
        # TAB 1: FINANCIAL
        with tab_money:
            st.caption("Comparing Cost of **Inaction (Keeping)** vs. **Action (Replacing)**")
            
            # Prepare Data for Chart
            chart_fin = df_analyzed[["Device ID", "Fin. Cost Keep (€)", "Fin. Cost Replace (€)"]].melt("Device ID", var_name="Type", value_name="Cost")
            
            # Altair Chart with Theme Colors
            c = alt.Chart(chart_fin).mark_bar(size=40).encode(
                x=alt.X('Type:N', axis=None, title=""),
                y=alt.Y('Cost:Q', title="Annual Cost (€)"),
                # CHANGED COLORS HERE:
                color=alt.Color('Type:N', scale=alt.Scale(range=[THEME_RED_MUTED, THEME_GOLD]), legend=alt.Legend(title="Scenario")),
                column=alt.Column('Device ID:N', header=alt.Header(labelOrient="bottom"))
            ).properties(height=220)
            st.altair_chart(c, use_container_width=True)
            st.markdown(f"**Observation:** :red[Red bars] (Cost to Keep) include wasted salary. If Red > :orange[Gold] (Cost to Replace), you are losing money.")

        # TAB 2: ENVIRONMENTAL
        with tab_planet:
            st.caption("Comparing **Operational Carbon (Keep)** vs. **Manufacturing Carbon Debt (Replace)**")
            
            chart_env = df_analyzed[["Device ID", "Carbon Keep (kg)", "Carbon Replace (kg)"]].melt("Device ID", var_name="Type", value_name="Carbon")
            
            # Altair Chart with Theme Colors
            c = alt.Chart(chart_env).mark_bar(size=40).encode(
                x=alt.X('Type:N', axis=None),
                y=alt.Y('Carbon:Q', title="Annual Impact (kgCO₂e)"),
                 # CHANGED COLORS HERE:
                color=alt.Color('Type:N', scale=alt.Scale(range=[THEME_GREEN_MUTED, THEME_GREY]), legend=alt.Legend(title="Scenario")), 
                column=alt.Column('Device ID:N', header=alt.Header(labelOrient="bottom"))
            ).properties(height=220)
            st.altair_chart(c, use_container_width=True)
            st.markdown("**Observation:** :grey[Grey bars] are usually higher because making a new laptop releases ~250kg of CO₂.")

        # TAB 3: THE MATRIX (Detailed Table - No Colors to avoid Import Errors)
        with tab_matrix:
            st.dataframe(
                df_analyzed[[
                    "Device ID", "Persona", "Device Source", "Age (Years)", 
                    "Financial ROI (€)", "Env. ROI (kg)", 
                    "Action", "Logic"
                ]].style.format({
                    "Financial ROI (€)": "€{:.0f}", 
                    "Env. ROI (kg)": "{:.1f} kg",
                    "Age (Years)": "{:.1f}"
                }),
                use_container_width=True
            )
            
        # Reset Button
        if st.button("🗑️ Clear Audit Data"):
            if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
            st.rerun()