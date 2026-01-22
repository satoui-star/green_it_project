# green_it_project - Élysia 

Élysia est un système d'intelligence IT durable conçu pour optimiser le renouvellement du parc informatique en équilibrant les coûts financiers (TCO - *Total Cost of Ownership*) et l'impact carbone (CO2). Ce projet modulaire vise à fournir une recommandation pondérée entre trois scénarios de gestion de flotte : Conserver (KEEP EXISTING), Acheter Neuf (BUY NEW), et Acheter Reconditionné (BUY REFURBISHED).

Ce document sert de guide technique exhaustif pour l'installation, l'exécution et la compréhension de l'architecture de l'application.

---

## 1. Architecture Technique

L'application Élysia est construite sur une architecture Python modulaire, séparant clairement la couche de présentation, la couche de données et le moteur de calcul.

| Module | Rôle | Description Technique |
| :--- | :--- | :--- |
| **Frontend (Interface Utilisateur)** | `main.py`, `utils_ui.py`, `equipement_audit/`, `cloud/` | Application web interactive développée avec **Streamlit**. `main.py` agit comme un routeur central, gérant l'état de session (`st.session_state`) et dirigeant l'utilisateur vers les modules `equipment` ou `cloud`. |
| **Couche de Données** | `reference_data_API.py` | Centralise toutes les constantes, les données de référence (Personas, Facteurs Carbone, Constantes Économiques) et assure une source unique de vérité pour les calculs [3]. |
| **Couche Méthodologique** | `methodology.py` | Formalise les définitions et les formules de calcul du TCO et du CO2, incluant la logique de la perte de productivité (*Lag Cost*) et l'amortissement carbone [2]. |
| **Moteur de Calcul** | `calculator.py` | Orchestre les calculs. Contient les classes `ShockCalculator`, `StrategySimulator`, et `RecommendationEngine` qui implémentent la logique d'arbitrage et le calcul du Score Composite Pondéré [4]. |

### Dépendances Clés

L'application est une application Python pure.

| Dépendance | Version Minimale | Rôle |
| :--- | :--- | :--- |
| **Python** | 3.8+ | Langage d'exécution principal. |
| **Streamlit** | (Dernière stable) | Framework pour la création de l'interface utilisateur web interactive. |
| **Pandas** | (Dernière stable) | Utilisé dans `calculator.py` pour la manipulation et l'analyse de données complexes. |

---

## 2. Installation et Configuration

### 2.1. Prérequis

Assurez-vous que **Python 3.8** ou une version ultérieure est installé sur votre système.

### 2.2. Instructions d'Installation

1.  **Clonage du Dépôt (Hypothétique)**
    ```bash
    git clone [URL_DU_DEPOT]/elysia.git
    cd elysia
    ```

2.  **Création d'un Environnement Virtuel (Recommandé)**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Sous Linux/macOS
    # venv\Scripts\activate  # Sous Windows
    ```

3.  **Installation des Dépendances**
    Les dépendances sont listées dans le fichier `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *(Le fichier `requirements.txt` contient au minimum `streamlit` et `pandas`)*

### 2.3. Configuration des Données

Le moteur de calcul repose sur des données de référence critiques (facteurs carbone, personas, prix de l'électricité) qui sont intégrées dans le module `reference_data_API.py`.

**Aucune configuration externe n'est requise** pour le lancement initial, car les données sont chargées en dur dans le code. Pour modifier les constantes (ex: Facteur Carbone Grille, Taux d'Économie CO2 Reconditionné), il est nécessaire d'éditer directement le fichier `reference_data_API.py`.

---

## 3. Instructions d'Exécution (*Run Instructions*)

L'application est lancée via le framework Streamlit.

### Lancement de l'Application Web

Depuis le répertoire racine du projet (`elysia/`), exécutez la commande suivante :

```bash
streamlit run main.py
```

L'application démarrera et sera accessible via votre navigateur web (généralement à l'adresse `http://localhost:8501`).

### Flux de Navigation

Le fichier `main.py` gère la navigation entre les trois sections principales :

1.  **Home Page** (`st.session_state['page'] = 'home'`) : Point d'entrée.
2.  **Equipment Audit** (`st.session_state['page'] = 'equipment'`) : Logique de recommandation KEEP/NEW/REFURBISHED.
3.  **Cloud Optimizer** (`st.session_state['page'] = 'cloud'`) : Optimisation des ressources Cloud.

---

## 4. Logique de Simulation et Workflow

Le cœur de l'application repose sur un workflow en quatre étapes, reflétant la chaîne de valeur de l'analyse [5] :

| Étape | Module de Calcul Impliqué | Objectif | Description Détaillée |
| :--- | :--- | :--- | :--- |
| **1. CALIBRATE** | `reference_data_API.py` | Définir la ligne de base. | L'utilisateur fournit les paramètres de la flotte (Taille, Taux de Renouvellement, Géographie, Cible). Le backend mappe ces entrées aux constantes (ex: Géographie → Facteur Carbone Grille). |
| **2. SHOCK** | `calculator.py` (`ShockCalculator`) | Quantifier le coût de l'inaction. | Calcule la **Valeur Bloquée** (*Stranded Value*) et le **CO2 Évitable** si aucune stratégie d'optimisation n'est adoptée. |
| **3. COMPARE** | `calculator.py` (`StrategySimulator`) | Évaluer les options macro. | Compare différentes stratégies (ex: "Refurb 40%" vs "Extension de Cycle de Vie") et calcule le ROI sur 3 ans. |
| **4. DECIDE** | `calculator.py` (`RecommendationEngine`) | Recommandation individuelle. | Pour un appareil/persona donné, calcule le **Score Composite Pondéré** (TCO vs CO2) pour déterminer l'option optimale (KEEP, NEW, REFURBISHED). |

### Logique de Décision Détaillée

La recommandation finale est basée sur le **Score Composite Pondéré** [4] :

$$
\text{Score Composite} = (\text{Score Financier Normalisé} \times \text{Poids Financier}) + (\text{Score Environnemental Normalisé} \times \text{Poids Environnemental})
$$

Le moteur applique une **Vérification d'Éligibilité** avant le calcul :
*   Si la sensibilité au lag de la persona est trop élevée (ex: > 2.0), l'option REFURBISHED est automatiquement exclue.
*   Si l'appareil n'est pas disponible en reconditionné, l'option est exclue.

---
