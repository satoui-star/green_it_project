import pandas as pd

def compute_environmental_roi(inventory_df, carbon_factors_df):
    """
    Calcule le ROI environnemental en croisant l'inventaire 
    et les facteurs d'émissions (Roadmap v01).
    """
    # 1. Jointure des données sur le type d'équipement
    # On s'assure que les colonnes correspondent
    df = inventory_df.merge(carbon_factors_df, on="equipment_type", how="left")
    
    # 2. Calcul du Gain Carbone (T1.4)
    # Le document indique qu'on évite la fabrication du neuf (crédit de ~80%)
    df['co2_saved_kg'] = df['mfg_kgco2e'] * 0.8
    
    # 3. Monétisation du Carbone (T2.1)
    # Prix cible : 80€ / tonne
    df['carbon_value_euro'] = (df['co2_saved_kg'] / 1000) * 80
    
    # 4. Coût de Productivité / Yearly Lag Cost (T2.2)
    # Formule : Salaire * 3% (exemple back-office du PDF page 68)
    # Note: Vous pourriez rendre ce 0.03 dynamique plus tard
    df['yearly_lag_cost'] = df['annual_salary'] * 0.03
    
    # 5. ROI Environnemental Net
    # C'est la valeur du carbone moins la perte de productivité
    df['net_environmental_roi'] = df['carbon_value_euro'] - df['yearly_lag_cost']
    
    return df
