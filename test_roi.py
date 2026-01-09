import pandas as pd

def clean_and_read_csv(file_path):
    """Fonction magique pour lire tes fichiers mal formés."""
    raw = pd.read_csv(file_path, encoding='utf-8-sig', header=None)
    header = raw.iloc[0, 0].split(',')
    data = [line[0].split(',') for line in raw.values[1:]]
    return pd.DataFrame(data, columns=header)

print("="*50)
print(" CALCUL DU ROI ENVIRONNEMENTAL LVMH ")
print("="*50)

try:
    # 1. Chargement des deux fichiers avec notre méthode
    inv = clean_and_read_csv("assets/Original_data_ROI_calculation.csv")
    carb = clean_and_read_csv("assets/Carbon emissions per equipement.csv")

    # 2. Nettoyage des données (enlever les espaces)
    inv['equipment_type'] = inv['equipment_type'].str.strip()
    carb['equipment_type'] = carb['equipment_type'].str.strip()
    inv['Category'] = inv['Category'].str.strip()

    # 3. On ne garde que l'inventaire
    inv_stock = inv[inv['Category'] == 'Inventory'].copy()

    # 4. Jointure (Merge) pour récupérer les infos carbone et salaires
    # Note : On convertit les colonnes en nombres car le split les a mis en texte
    df = inv_stock.merge(carb, on="equipment_type", how="left")
    
    for col in ['mfg_kgco2e', 'annual_salary']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 5. Calculs Roadmap v01
    df['Gain_Carbone_kg'] = df['mfg_kgco2e'] * 0.8
    df['Valeur_Carbone_Euro'] = (df['Gain_Carbone_kg'] / 1000) * 80
    df['Lag_Cost_Euro'] = df['annual_salary'] * 0.03
    df['ROI_Net'] = df['Valeur_Carbone_Euro'] - df['Lag_Cost_Euro']

    # 6. Affichage
    print("\n--- RÉSULTATS PAR ÉQUIPEMENT ---")
    print(df[['equipment_type', 'Valeur_Carbone_Euro', 'Lag_Cost_Euro', 'ROI_Net']])
    
    print("\n" + "="*50)
    print(f" TOTAL ROI ENVIRONNEMENTAL : {df['ROI_Net'].sum():,.2f} €")
    print("="*50)

except Exception as e:
    print(f"❌ Erreur lors du calcul : {e}")
