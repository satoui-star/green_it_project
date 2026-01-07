import pandas as pd

def load_carbon_factors(path="assets/Base_Carbone.csv"):
    """
    Load ADEME Base Carbone and extract CO2 factors (kgCO2e / unit)
    """
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.lower()

    factors = {}

    for _, row in df.iterrows():
        label = str(row.get("poste", "")).lower()
        value = row.get("valeur", None)

        if value is None:
            continue

        if "ordinateur portable" in label:
            factors["Laptop"] = value
        elif "smartphone" in label:
            factors["Smartphone"] = value
        elif "écran" in label or "ecran" in label:
            factors["Screen"] = value
        elif "tablette" in label:
            factors["Tablet"] = value
        elif "routeur" in label or "switch" in label:
            factors["Switch/Router"] = value

    return factors
