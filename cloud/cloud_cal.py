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
# -----------------------------
# SECTION 1 – CLOUD PROVIDER COMPARISON
# -----------------------------
pricing = {
    "AWS S3": get_aws_s3_price(),
    "Azure Blob": get_azure_blob_price(),
    "Google Cloud Storage": get_gcp_storage_price()
}

provider_data = []

for provider, price in pricing.items():
    emissions = calculate_storage_emissions(storage_gb, carbon_intensity)
    provider_data.append({
        "Provider": provider,
        "Price ($/GB/month)": price,
        "Estimated CO₂ (kg/year)": round(emissions, 2)
    })

df_providers = pd.DataFrame(provider_data)
st.dataframe(df_providers)

best_provider = df_providers.sort_values(
    ["Estimated CO₂ (kg/year)", "Price ($/GB/month)"]
).iloc[0]["Provider"]

st.success(f"✅ Recommended Provider: **{best_provider}**")

# -----------------------------
# SECTION 2 – CO₂ OBJECTIVE & DATA RETENTION
# -----------------------------
st.header("2️⃣ CO₂ Objective & Data Retention Recommendation")

retention = retention_recommendation(
    storage_gb,
    growth_rate,
    target_co2,
    carbon_intensity
)

st.metric("Data to Delete (GB)", retention["delete_gb"])
st.metric("Data to Keep (GB)", retention["keep_gb"])
st.info(retention["message"])

# -----------------------------
# SECTION 3 – DATA AGING ANALYSIS
# -----------------------------
st.header("3️⃣ Data Aging & Unused Data Impact")

data_aging = pd.DataFrame({
    "Data Age": ["< 1 year", "1–3 years", "3–5 years", "> 5 years"],
    "Estimated %": [30, 30, 20, 20],
    "Usage": ["Active", "Moderate", "Low", "Unused"]
})

data_aging["GB"] = storage_gb * data_aging["Estimated %"] / 100
data_aging["CO₂ (kg/year)"] = data_aging["GB"].apply(
    lambda x: calculate_storage_emissions(x, carbon_intensity)
)

st.dataframe(data_aging)

unused = data_aging[data_aging["Usage"] == "Unused"]["CO₂ (kg/year)"].sum()

st.warning(
    f"⚠️ Unused data (>5 years) represents approximately "
    f"**{round(unused, 2)} kg CO₂/year**"
)

# -----------------------------
# FOOTER – TRANSPARENCY
# -----------------------------
st.markdown("---")
st.caption("""
**Methodology Notes**
- Emissions are estimated using electricity carbon intensity and storage energy models
- No automatic deletion is performed
- Results are recommendations only
- Sources: Google Cloud Carbon Footprint, Electricity Maps, ADEME, GSF
""")
