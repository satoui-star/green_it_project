import streamlit as st
import pandas as pd
import altair as alt

# --- IMPORTING FROM NEIGHBOR FOLDER ---
# This only works when running 'main.py'
try:
    from equipement_audit.reference_data import EQUIPMENT_DB
except ImportError:
    # Fallback to prevent crash, but warn user
    EQUIPMENT_DB = {}
    st.error("⚠️ Please run this app using 'streamlit run main.py' to load the database correctly.")

def run_simulation_ui():
    st.markdown("## 🔮 Future Impact Simulation")
    st.markdown("Predict the carbon and financial impact of your IT growth strategy over the next 5 years.")
    st.markdown("---")

    if not EQUIPMENT_DB:
        st.warning("Database not loaded. Please run from main.py")
        return

    # --- 1. SIMULATION CONTROLS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Growth Parameters")
        growth_rate = st.slider("Annual IT Growth (%)", 0, 50, 10)
        years = st.slider("Projection Period (Years)", 1, 10, 5)
    
    with col2:
        st.subheader("🏢 Current Fleet")
        laptop_count = st.number_input("Number of Laptops", value=100)
        screen_count = st.number_input("Number of Screens", value=100)
        
    st.markdown("---")

    # --- 2. CALCULATION ENGINE ---
    if st.button("🚀 Run Simulation"):
        # Get Carbon constants
        co2_laptop = EQUIPMENT_DB['Laptop']['co2_manufacturing']
        co2_screen = EQUIPMENT_DB['Screen']['co2_manufacturing']
        
        # Calculate Year-over-Year
        projection_data = []
        current_laptops = laptop_count
        current_screens = screen_count
        
        for year in range(1, years + 1):
            # Apply growth
            current_laptops *= (1 + growth_rate / 100)
            current_screens *= (1 + growth_rate / 100)
            
            # Simple footprint calc
            total_co2 = (current_laptops * co2_laptop) + (current_screens * co2_screen)
            
            projection_data.append({
                "Year": f"Year {year}",
                "Total Devices": int(current_laptops + current_screens),
                "Carbon Footprint (kgCO2)": round(total_co2, 2)
            })
            
        df_proj = pd.DataFrame(projection_data)
        
        # --- 3. VISUALIZATION ---
        st.subheader("📈 Carbon Emission Trajectory")
        
        # LVMH Style Chart
        chart = alt.Chart(df_proj).mark_area(
            color='#D4AF37', # Gold
            opacity=0.6,
            line={'color':'#D4AF37'}
        ).encode(
            x='Year',
            y='Carbon Footprint (kgCO2)',
            tooltip=['Year', 'Carbon Footprint (kgCO2)', 'Total Devices']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)