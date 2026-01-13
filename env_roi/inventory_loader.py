import pandas as pd

def load_inventory(path="assets/Original_data_ROI_calculation.csv"):
    """
    Charge l'inventaire des actifs (le stock).
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip() # Nettoyage des noms de colonnes
    return df
