import streamlit as st
import pandas as pd

# 👇 IMPORT LOGIC
try:
    from cloud import cloud_cal as backend
except ImportError:
    import cloud_cal as backend

def run_cloud_ui():
    st.markdown("## ☁️ Cloud Storage Optimizer")
    
    # --- INPUTS (Moved from sidebar to main page for better layout) ---
    st.markdown("### ⚙️ Settings")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        storage_tb = st.number_input("Current Storage (TB)", 0.1, 10000.0, 100.0, 10.0)
    with c2:
        country_code = st.text_input("Country Code", "FR")
    with c3:
        reduction_target_pct = st.slider("Reduction Target (%)", 5, 80, 30)
    with c4:
        projection_years = st.slider("Projection (Years)", 1, 10, 5)

    # --- CALCULATIONS (Using Backend) ---
    storage_gb = storage_tb * 1024
    carbon_intensity = backend.get_carbon_intensity(country_code)
    current_emissions = backend.calculate_annual_emissions(storage_gb, carbon_intensity)
    target_emissions_kg = current_emissions * (1 - reduction_target_pct / 100)
    
    # Run Simulation
    archival_df = backend.calculate_archival_needed(
        storage_gb, target_emissions_kg, carbon_intensity, projection_years
    )
    current_year = archival_df[archival_df["Year"] == 0].iloc[0]

    st.markdown("---")

    # --- VISUALS (Exact same metrics as before) ---
    st.header("📊 Current Storage Status")
    st.info(f"📍 Carbon Intensity: {carbon_intensity:.0f} gCO₂/kWh")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Storage", f"{storage_tb:.1f} TB")
    col2.metric("Annual Emissions", f"{current_emissions:,.0f} kg CO₂")
    col3.metric(f"Target (-{reduction_target_pct}%)", f"{target_emissions_kg:,.0f} kg CO₂")

    st.header("📦 Archival Strategy")
    st.info(f"📈 Assumptions: {backend.ANNUAL_DATA_GROWTH*100:.0f}% growth | 🌱 {backend.ARCHIVAL_CARBON_REDUCTION*100:.0f}% savings on archival")

    st.subheader("🎯 Immediate Action Required")
    if current_year["Data to Archive (GB)"] > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Archive Now", f"{current_year['Data to Archive (TB)']:.2f} TB")
            st.metric("Of Current Storage", f"{(current_year['Data to Archive (GB)'] / storage_gb * 100):.1f}%")
        with c2:
            st.metric("CO₂ After Archival", f"{current_year['Emissions After Archival (kg)']:,.0f} kg")
            saved = current_emissions - current_year['Emissions After Archival (kg)']
            st.metric("Annual Savings", f"{saved:,.0f} kg", delta="Saved")
        
        if current_year['Meets Target'] == "✅":
            st.success("✅ Target Met!")
        else:
            st.error("❌ Target not met even with archival.")
    else:
        st.success("✅ No immediate archival needed.")

    st.subheader(f"📅 {projection_years}-Year Projection")
    
    # Display Table
    display_df = archival_df.copy()
    display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
    st.dataframe(
        display_df.style.format({
            "Storage (TB)": "{:.2f}",
            "Emissions w/o Archival (kg)": "{:,.0f}",
            "Data to Archive (TB)": "{:.2f}",
            "Emissions After Archival (kg)": "{:,.0f}"
        }),
        width = "stretch"
    )
    
    # Key Insights
    st.header("💡 Key Insights")
    total_archival = archival_df["Data to Archive (TB)"].sum()
    k1, k2 = st.columns(2)
    k1.metric(f"Total Archival ({projection_years}y)", f"{total_archival:.2f} TB")
    k2.metric("Avg Annual Archival", f"{(total_archival/projection_years):.2f} TB/year")