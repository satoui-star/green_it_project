import streamlit as st
import requests
import pandas as pd

# ===============================
# CONFIG & CONSTANTS
# ===============================
st.set_page_config(
    page_title="Green IT – Cloud Storage Optimizer",
    layout="wide"
)

KWH_PER_GB_PER_YEAR = 1.2  # kWh/GB/year (conservative estimate)
DEFAULT_CARBON_INTENSITY = 400  # gCO2/kWh
ELECTRICITY_MAPS_API_KEY = "PUT_YOUR_API_KEY_HERE"

# Archival savings
ARCHIVAL_CARBON_REDUCTION = 0.70  # 70% carbon reduction for archived data

# Annual data growth
ANNUAL_DATA_GROWTH = 0.10  # 10% per year

# ===============================
# FUNCTIONS
# ===============================
def get_carbon_intensity(country_code):
    """Return carbon intensity in gCO2/kWh; fallback to default."""
    try:
        url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?countryCode={country_code}"
        headers = {"auth-token": ELECTRICITY_MAPS_API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return float(r.json().get("carbonIntensity", DEFAULT_CARBON_INTENSITY))
    except Exception:
        pass
    return DEFAULT_CARBON_INTENSITY

def calculate_annual_emissions(storage_gb, carbon_intensity):
    """Calculate annual CO2 emissions in kg."""
    return storage_gb * KWH_PER_GB_PER_YEAR * carbon_intensity / 1000  # kg CO2

def calculate_archival_needed(current_storage_gb, target_emissions_kg, carbon_intensity, years_ahead):
    """
    Calculate how much data needs to be archived to meet target emissions
    considering data growth over specified years.
    """
    results = []
    
    for year in range(years_ahead + 1):
        # Calculate projected storage with growth
        projected_storage_gb = current_storage_gb * ((1 + ANNUAL_DATA_GROWTH) ** year)
        
        # Calculate emissions without archival
        projected_emissions = calculate_annual_emissions(projected_storage_gb, carbon_intensity)
        
        # Calculate how much needs to be archived to meet target
        if projected_emissions > target_emissions_kg:
            # excess_emissions = projected_emissions - target_emissions_kg
            # For archived data: emission_reduction = archived_gb * co2_per_gb * ARCHIVAL_CARBON_REDUCTION
            co2_per_gb = calculate_annual_emissions(1, carbon_intensity)
            
            # We need: projected_emissions - (archived_gb * co2_per_gb * ARCHIVAL_CARBON_REDUCTION) = target_emissions_kg
            # Solving for archived_gb:
            archived_gb_needed = (projected_emissions - target_emissions_kg) / (co2_per_gb * ARCHIVAL_CARBON_REDUCTION)
            
            # Can't archive more than we have
            archived_gb_needed = min(archived_gb_needed, projected_storage_gb)
            
            # Calculate actual emissions after archival
            archival_savings = archived_gb_needed * co2_per_gb * ARCHIVAL_CARBON_REDUCTION
            final_emissions = projected_emissions - archival_savings
        else:
            archived_gb_needed = 0
            final_emissions = projected_emissions
        
        results.append({
            "Year": year,
            "Storage (TB)": projected_storage_gb / 1024,
            "Storage (GB)": projected_storage_gb,
            "Emissions w/o Archival (kg)": projected_emissions,
            "Data to Archive (GB)": archived_gb_needed,
            "Data to Archive (TB)": archived_gb_needed / 1024,
            "Emissions After Archival (kg)": final_emissions,
            "Meets Target": "✅" if final_emissions <= target_emissions_kg else "❌"
        })
    
    return pd.DataFrame(results)

# ===============================
# SIDEBAR INPUTS
# ===============================
st.sidebar.header("Company Inputs")

storage_tb = st.sidebar.number_input(
    "Current Total Storage (TB)", min_value=0.1, value=100.0, step=10.0
)
storage_gb = storage_tb * 1024

country_code = st.sidebar.text_input("HQ Country Code (ISO-2)", value="FR")

reduction_target_pct = st.sidebar.slider(
    "CO₂ Reduction Target (%)", 
    min_value=5, 
    max_value=80, 
    value=30,
    help="Target percentage reduction in CO₂ emissions from current levels"
)

projection_years = st.sidebar.slider(
    "Projection Period (years)", 
    min_value=1, 
    max_value=10, 
    value=5
)

# ===============================
# CARBON INTENSITY
# ===============================
carbon_intensity = get_carbon_intensity(country_code)
if carbon_intensity == DEFAULT_CARBON_INTENSITY:
    st.warning(
        "⚠️ Using default carbon intensity (IEA global average) due to missing API or invalid key."
    )

st.info(f"📍 Carbon Intensity for {country_code}: {carbon_intensity:.0f} gCO₂/kWh")

# ===============================
# CURRENT STATUS
# ===============================
st.header("📊 Current Storage Status")

current_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
target_emissions_kg = current_emissions * (1 - reduction_target_pct / 100)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Storage", f"{storage_tb:.1f} TB")

with col2:
    st.metric("Current Annual Emissions", f"{current_emissions:,.0f} kg CO₂/year")

with col3:
    st.metric(
        f"Target Emissions (-{reduction_target_pct}%)", 
        f"{target_emissions_kg:,.0f} kg CO₂/year"
    )

# ===============================
# ARCHIVAL RECOMMENDATION
# ===============================
st.header("📦 Archival Strategy with Data Growth")

st.info(f"📈 Assuming {ANNUAL_DATA_GROWTH*100:.0f}% annual data growth | 🌱 Archival reduces CO₂ by {ARCHIVAL_CARBON_REDUCTION*100:.0f}% for archived data")

# Calculate archival needs
archival_df = calculate_archival_needed(storage_gb, target_emissions_kg, carbon_intensity, projection_years)

# Display year 0 (current) recommendation
current_year = archival_df[archival_df["Year"] == 0].iloc[0]

st.subheader("🎯 Immediate Action Required")

if current_year["Data to Archive (GB)"] > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Archive Now", 
            f"{current_year['Data to Archive (TB)']:.2f} TB",
            help="Amount of data to archive immediately to meet target"
        )
        st.metric(
            "Percentage of Current Storage",
            f"{(current_year['Data to Archive (GB)'] / storage_gb * 100):.1f}%"
        )
    
    with col2:
        st.metric(
            "CO₂ After Archival",
            f"{current_year['Emissions After Archival (kg)']:,.0f} kg/year"
        )
        reduction = current_emissions - current_year['Emissions After Archival (kg)']
        st.metric(
            "Annual CO₂ Savings",
            f"{reduction:,.0f} kg/year",
            delta=f"-{(reduction/current_emissions)*100:.1f}%"
        )
    
    if current_year['Meets Target'] == "✅":
        st.success("✅ This archival strategy will meet your CO₂ target!")
    else:
        st.error("❌ Even with maximum archival, target cannot be met. Consider a higher emission target.")
else:
    st.success("✅ Current emissions are already below target! No immediate archival needed.")

# ===============================
# MULTI-YEAR PROJECTION
# ===============================
st.subheader(f"📅 {projection_years}-Year Projection & Archival Plan")

# Format display dataframe
display_df = archival_df.copy()
display_df["Year"] = display_df["Year"].apply(lambda x: f"Year {x}")
display_df = display_df[[
    "Year", 
    "Storage (TB)", 
    "Emissions w/o Archival (kg)", 
    "Data to Archive (TB)",
    "Emissions After Archival (kg)",
    "Meets Target"
]]

# Format numbers
display_df["Storage (TB)"] = display_df["Storage (TB)"].apply(lambda x: f"{x:.2f}")
display_df["Emissions w/o Archival (kg)"] = display_df["Emissions w/o Archival (kg)"].apply(lambda x: f"{x:,.0f}")
display_df["Data to Archive (TB)"] = display_df["Data to Archive (TB)"].apply(lambda x: f"{x:.2f}")
display_df["Emissions After Archival (kg)"] = display_df["Emissions After Archival (kg)"].apply(lambda x: f"{x:,.0f}")

st.dataframe(display_df, use_container_width=True)

# ===============================
# KEY INSIGHTS
# ===============================
st.header("💡 Key Insights")

total_archival_needed = archival_df["Data to Archive (TB)"].sum()
years_meeting_target = (archival_df["Meets Target"] == "✅").sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        f"Total Archival Over {projection_years} Years",
        f"{total_archival_needed:.2f} TB"
    )

with col2:
    st.metric(
        "Years Meeting Target",
        f"{years_meeting_target}/{projection_years + 1}"
    )

with col3:
    avg_annual_archival = total_archival_needed / projection_years if projection_years > 0 else 0
    st.metric(
        "Avg Annual Archival Needed",
        f"{avg_annual_archival:.2f} TB/year"
    )

st.caption("💡 **Recommendation**: Implement a continuous archival policy for data older than 5 years to maintain sustainable storage emissions as your data grows.")
st.caption(f"📊 **Benefits of Archival**: 70% CO₂ reduction on archived data | 90% cost savings on archived data")