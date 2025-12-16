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

YEARS_STORED = {
    "< 1 year": 0.5,
    "1–3 years": 2,
    "3–5 years": 4,
    "> 5 years": 5
}

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
    return storage_gb * KWH_PER_GB_PER_YEAR * carbon_intensity / 1000  # kg CO2

# ===============================
# SIDEBAR INPUTS
# ===============================
st.sidebar.header("Company Inputs")

storage_tb = st.sidebar.number_input(
    "Total storage (TB)", min_value=0.1, value=100.0, step=10.0
)
storage_gb = storage_tb * 1024

country_code = st.sidebar.text_input("HQ Country code (ISO-2)", value="FR")

saving_target_pct = st.sidebar.slider(
    "Target CO₂ reduction (%)", min_value=5, max_value=80, value=30
)

st.sidebar.subheader("Data Aging (%)")
age_lt_1 = st.sidebar.number_input("< 1 year", 0.0, 100.0, 30.0)
age_1_3 = st.sidebar.number_input("1–3 years", 0.0, 100.0, 30.0)
age_3_5 = st.sidebar.number_input("3–5 years", 0.0, 100.0, 20.0)
age_gt_5 = st.sidebar.number_input("> 5 years", 0.0, 100.0, 20.0)

total_pct = age_lt_1 + age_1_3 + age_3_5 + age_gt_5
if total_pct != 100:
    st.error("⚠️ Percentages must sum to 100%")
    st.stop()

# ===============================
# CARBON INTENSITY
# ===============================
carbon_intensity = get_carbon_intensity(country_code)
if carbon_intensity == DEFAULT_CARBON_INTENSITY:
    st.warning(
        "⚠️ Using default carbon intensity (IEA global average) due to missing API or invalid key."
    )

# ===============================
# ANNUAL EMISSIONS
# ===============================
annual_emissions = calculate_annual_emissions(storage_gb, carbon_intensity)
st.metric("Estimated Annual Storage Emissions", f"{annual_emissions:,.0f} kg CO₂ / year")

# ===============================
# DATA AGING & CUMULATIVE EMISSIONS
# ===============================
st.header("Data Aging & Cumulative CO₂")

data_aging = pd.DataFrame({
    "Data Age": ["< 1 year", "1–3 years", "3–5 years", "> 5 years"],
    "Share (%)": [age_lt_1, age_1_3, age_3_5, age_gt_5]
})
data_aging["Years Stored"] = data_aging["Data Age"].map(YEARS_STORED)
data_aging["Storage (GB)"] = storage_gb * data_aging["Share (%)"] / 100
data_aging["Annual CO₂ (kg)"] = data_aging["Storage (GB)"].apply(
    lambda x: calculate_annual_emissions(x, carbon_intensity)
)
data_aging["Cumulative CO₂ (kg)"] = data_aging["Annual CO₂ (kg)"] * data_aging["Years Stored"]

st.dataframe(data_aging, use_container_width=True)

# Insight: old vs new
old = data_aging.loc[data_aging["Data Age"] == "> 5 years"].iloc[0]
new = data_aging.loc[data_aging["Data Age"] == "< 1 year"].iloc[0]
ratio = (old["Cumulative CO₂ (kg)"]/old["Storage (GB)"]) / (new["Cumulative CO₂ (kg)"]/new["Storage (GB)"])
st.info(f"1 GB of data >5 years accumulates approx. {ratio:.1f}× more CO₂ than <1 year data")

# ===============================
# TARGET REDUCTION
# ===============================
st.header("CO₂ Reduction Recommendation")

target_reduction_kg = annual_emissions * saving_target_pct / 100
co2_per_gb = calculate_annual_emissions(1, carbon_intensity)
gb_to_delete = target_reduction_kg / co2_per_gb

st.success(f"To achieve {saving_target_pct}% reduction: delete ~{gb_to_delete:,.0f} GB (~{gb_to_delete/1024:.1f} TB)")

# Deletion priority table
st.subheader("Deletion Priority (Highest Impact)")
priority = data_aging.sort_values("Cumulative CO₂ (kg)", ascending=False)[
    ["Data Age", "Storage (GB)", "Cumulative CO₂ (kg)"]
]
st.table(priority)

st.caption("Recommendation: prioritize deletion or archival of old/unused data to reduce cumulative emissions.")
