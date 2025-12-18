import streamlit as st
import pandas as pd
import plotly.express as px

# --- FIX UNIVERSEL ---
# Essaie d'importer avec le point (mode Cockpit / main.py)
# Si ça échoue, importe sans le point (mode Test direct)
try:
    from .calculator import CarbonCalculator, get_demo_data
except ImportError:
    from calculator import CarbonCalculator, get_demo_data
# ---------------------

def run_audit_ui():
    # Note: On n'utilise pas st.set_page_config ici car c'est main.py qui le fait
    
    st.markdown("### 📊 Intelligent Fleet Audit")
    
    # --- 1. DATA INGESTION ---
    col_up, col_dl = st.columns([3, 1])
    with col_up:
        uploaded_file = st.file_uploader("Upload Inventory (CSV/Excel)", type=["csv", "xlsx"])
    with col_dl:
        st.markdown("<br>", unsafe_allow_html=True)
        # Utilisation de st.session_state pour persister les données
        if st.button("Load Demo Data"):
            st.session_state['audit_data'] = get_demo_data()
            st.rerun()
    
    # Gestion des données (Fichier ou Démo)
    df = None
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
        except:
            df = pd.read_excel(uploaded_file)
    elif 'audit_data' in st.session_state:
        df = st.session_state['audit_data']
    
    # --- 2. DASHBOARD ---
    if df is not None:
        # Calcul
        with st.spinner("Calculating Lifecycle Assessment (LCA)..."):
            enriched_df = CarbonCalculator.process_inventory(df)
        
        # KPIs
        total_co2 = enriched_df["Total CO2 (kg)"].sum() / 1000 # tonnes
        total_cost = enriched_df["Energy Cost (€)"].sum()
        avg_age = enriched_df["Age (Years)"].mean()
        
        mfg_share = enriched_df["Mfg CO2 (kg)"].sum()
        usage_share = enriched_df["Usage CO2 (kg)"].sum()
        ratio_pct = int(mfg_share / (mfg_share + usage_share) * 100) if (mfg_share + usage_share) > 0 else 0
        
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Fleet Footprint", f"{total_co2:.2f} tCO2e", delta="Scope 2+3")
        m2.metric("Est. Energy Cost", f"€{total_cost:,.0f}", delta="Lifetime")
        m3.metric("Avg Device Age", f"{avg_age:.1f} Years")
        m4.metric("Mfg vs Usage Ratio", f"{ratio_pct}% Mfg", help="Impact Fabrication vs Usage")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- 3. GRAPHIQUES ---
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("##### 🌍 Emissions Hotspots")
            melted = enriched_df.melt(
                id_vars=["Location"], 
                value_vars=["Mfg CO2 (kg)", "Usage CO2 (kg)"],
                var_name="Emission Source", 
                value_name="CO2"
            )
            color_map = {"Mfg CO2 (kg)": "#D4AF37", "Usage CO2 (kg)": "#444444"}
            
            fig_bar = px.bar(
                melted, x="Location", y="CO2", color="Emission Source",
                title="Carbon Impact by Region", color_discrete_map=color_map, barmode='stack'
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#CCC")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c2:
            st.markdown("##### ⚠️ Top Emitters")
            top_emitters = enriched_df.nlargest(5, "Total CO2 (kg)")[["Device ID", "Device Type", "Total CO2 (kg)"]]
            st.dataframe(
                top_emitters, hide_index=True, use_container_width=True,
                column_config={"Total CO2 (kg)": st.column_config.ProgressColumn("Impact", format="%.0f kg", max_value=float(enriched_df["Total CO2 (kg)"].max()))}
            )

        # --- 4. RECOMMANDATIONS ---
        st.markdown("### 💡 Strategic Recommendations")
        rec_col1, rec_col2 = st.columns(2)
        
        # Logic 1: Extension de vie
        old_devices = enriched_df[enriched_df["Age (Years)"] >= 4]
        potential_savings = old_devices["Mfg CO2 (kg)"].sum()
        with rec_col1:
            st.info(f"**Life Extension:** {len(old_devices)} devices > 4 years.\n\nKeeping them avoids **{potential_savings:,.0f} kg CO2e** (Scope 3).")

        # Logic 2: Grid Decarbonization
        dirty_devs = enriched_df[(enriched_df["Location"].isin(["China", "Global Average", "Germany", "USA"])) & (enriched_df["Device Type"].str.contains("Server|Screen"))]
        with rec_col2:
            st.warning(f"**Grid Optimization:** {len(dirty_devs)} High-Power devices on Carbon Grids.\n\nSwitch to Green Energy or relocate.")

        with st.expander("Detailed Inventory View"):
            st.dataframe(enriched_df, use_container_width=True)

        # Sources
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📚 Data Sources & Methodology"):
            st.markdown("""
            **Methodology:** Lifecycle Assessment (LCA) / GHG Protocol.
            **Data Sources:** ADEME Base Empreinte®, Boavizta API, LVMH Internal Specs.
            """)

    else:
        st.info("👋 Upload a file or click 'Load Demo Data' to begin analysis.")