import streamlit as st
import requests
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Green Cloud Storage Optimizer", layout="wide")

ELECTRICITY_MAPS_API_KEY = "YOUR_API_KEY_HERE"  # required
KWH_PER_GB_PER_YEAR = 0.005  # modeled assumption

# -----------------------------
# UTILITIES
# -----------------------------
def get_electricity_carbon_intensity(country_code):
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?countryCode={country_code}"
    headers = {"auth-token": ELECTRICITY_MAPS_API_KEY}
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.json()["carbonIntensity"]
    return None


def calculate_storage_emissions(storage_gb, carbon_intensity):
    """
    Emissions = GB * kWh/GB/year * gCO2/kWh
    """
    return storage_gb * KWH_PER_GB_PER_YEAR * carbon_intensity / 1000  # kg CO2


# -----------------------------
# CLOUD PRICING (SIMPLIFIED API ACCESS)
# -----------------------------
def get_azure_blob_price(region="westeurope"):
    url = "https://prices.azure.com/api/retail/prices"
    params = {
        "serviceName": "Storage",
        "productName": "Blob Storage",
        "armRegionName": region
    }
    r = requests.get(url, params=params)
    items = r.json().get("Items", [])
    return min([item["unitPrice"] for item in items if "Hot" in item["meterName"]], default=None)


def get_aws_s3_price():
    # AWS pricing API is huge – simplified static assumption for MVP
    return 0.023  # USD per GB-month (standard S3)


def get_gcp_storage_price():
    return 0.020  # USD per GB-month (standard tier)


# -----------------------------
# DATA RETENTION LOGIC
# -----------------------------
def retention_recommendation(
    current_storage,
    annual_growth_rate,
    target_emissions,
    carbon_intensity
):
    current_emissions = calculate_storage_emissions(current_storage, carbon_intensity)

    if current_emissions <= target_emissions:
        return {
            "delete_gb": 0,
            "keep_gb": current_storage,
            "message": "You are already within your CO₂ target."
        }

    excess_emissions = current_emissions - target_emissions
    gb_to_delete = excess_emissions * 1000 / (KWH_PER_GB_PER_YEAR * carbon_intensity)

    return {
        "delete_gb": round(gb_to_delete, 2),
        "keep_gb": round(current_storage - gb_to_delete, 2),
        "message": "Data deletion or archiving recommended."
    }


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("🌱 Green Cloud Storage Optimizer")

st.markdown("""
Decision-support tool to **reduce cloud storage cost and CO₂ emissions**  
Based on **pricing APIs, energy carbon intensity, and Green IT standards**
""")

# -----------------------------
# INPUTS
# -----------------------------
st.sidebar.header("Company Inputs")

country = st.sidebar.selectbox("HQ Country", ["FR", "DE", "US", "GB"])
industry = st.sidebar.selectbox("Industry", ["Tech", "Finance", "Retail", "Healthcare"])
storage_gb = st.sidebar.number_input("Current Storage (GB)", 100, 10_000_000, 10_000)
growth_rate = st.sidebar.slider("Annual Data Growth Rate (%)", 0, 50, 15)
target_co2 = st.sidebar.number_input("Target CO₂ Emissions (kg/year)", 1, 100_000, 500)

# -----------------------------
# SECTION 1 – PROVIDER COMPARISON
# -----------------------------
st.header("1️⃣ Best Cloud Storage Provider (Cost + CO₂)")

carbon_intensity = get_electricity_carbon_intensity(country)

pricing = {
    "AW
