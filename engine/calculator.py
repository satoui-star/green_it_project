def compute_roi(row, mfg_co2, carbon_price=80):
    # 1. Gain Carbone (80% de la fabrication économisée)
    co2_saved = mfg_co2 * 0.8
    carbon_value = (co2_saved / 1000) * carbon_price
    
    # 2. Yearly Lag Cost (Perte de productivité basée sur le salaire)
    # On applique le taux de 3% défini dans le PDF (Membre 2)
    lag_cost = row['annual_salary'] * 0.03
    
    # 3. ROI Environnemental Net
    net_roi = carbon_value - lag_cost
    
    return {
        "Equipement": row['equipment_type'],
        "Gain Carbone (kg)": round(co2_saved, 2),
        "Valeur Carbone (€)": round(carbon_value, 2),
        "Perte Productivité (€)": round(lag_cost, 2),
        "ROI Net (€)": round(net_roi, 2)
    }
