import pandas as pd
import sys
import os

# Ajoute le dossier courant au path pour pouvoir importer tes modules
sys.path.append(os.path.dirname(__file__))

from env_roi.inventory_loader import load_inventory
from env_roi.carbon_factor_loader import load_carbon_factors
from env_roi.calculator import compute_environmental_roi

def test_calculateur():
    print("="*50)
    print("VÉRIFICATION TECHNIQUE DU ROI ENVIRONNEMENTAL")
    print("="*50)

    try:
        # 1. Chargement des données
        print(f"Chargement de l'inventaire...")
        inventory = load_inventory("assets/Original_data_ROI_calculation.csv")
        
        print(f"Chargement des facteurs carbone...")
        # On charge le CSV des émissions en DataFrame pour la jointure
        factors_df = pd.read_csv("assets/Carbon emissions per equipement.csv")

        # 2. Simulation du calcul
        # On fusionne l'inventaire avec les données carbone sur la colonne 'equipment_type'
        df_merged = inventory.merge(factors_df, on="equipment_type", how="left")
        
        # Vérification des valeurs manquantes après jointure
        if df_merged['mfg_kgco2e'].isnull().any():
            missing = df_merged[df_merged['mfg_kgco2e'].isnull()]['equipment_type'].unique()
            print(f"⚠️ Attention : Certains types d'équipements n'ont pas de correspondance carbone : {missing}")

        # 3. Calcul du ROI (Formules de la Roadmap)
        # Gain Carbone (80% évitée) converti en € (80€/t)
        df_merged['carbon_gain_euro'] = (df_merged['mfg_kgco2e'] * 0.8 / 1000) * 80
        
        # Perte de productivité (3% du salaire annuel)
        df_merged['lag_cost_euro'] = df_merged['annual_salary'] * 0.03
        
        # ROI Net
        df_merged['net_roi'] = df_merged['carbon_gain_euro'] - df_merged['lag_cost_euro']

        # 4. Affichage d'un échantillon de résultats
        print("\n--- RÉSULTATS DES 5 PREMIÈRES LIGNES ---")
        cols_to_show = ['equipment_type', 'annual_salary', 'carbon_gain_euro', 'lag_cost_euro', 'net_roi']
        print(df_merged[cols_to_show].head())

        # 5. Validation du "Point de Bascule" (Member 4 Insight)
        print("\n--- ANALYSE DE DÉCISION ---")
        total_positif = len(df_merged[df_merged['net_roi'] > 0])
        total_negatif = len(df_merged[df_merged['net_roi'] < 0])
        
        print(f"✅ Nombre de profils où le reconditionné est rentable : {total_positif}")
        print(f"❌ Nombre de profils où le reconditionné coûte trop cher (Productivité) : {total_negatif}")
        
        print("\n" + "="*50)
        print("TEST TERMINÉ AVEC SUCCÈS")
        print("="*50)

    except Exception as e:
        print(f"❌ ERREUR DURANT LE TEST : {e}")

if __name__ == "__main__":
    test_calculateur()
