# Tableau de bord — Mobilité et sécurité routière au Togo (Défi 1)

Dashboard Streamlit qui restitue les résultats du projet : 8 pages réparties en 4 groupes de menu (Principal, Analyses, Pilotage, Méthodologie). Le tableau de bord **affiche, il ne calcule pas** : chaque chiffre vient d'une table CSV déjà produite par les scripts d'analyse.

## Prérequis

- **Python 3.11** (testé avec 3.11.7)
- `pip` ou un gestionnaire de paquets compatible
- Un terminal (Linux, macOS ou Windows PowerShell)

## Installation

```bash
# 1. Se placer à la racine du projet
cd AdministrationTerritorialMobilite-defi1

# 2. Créer un environnement virtuel
python3.11 -m venv .venv

# 3. Activer l'environnement
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 4. Installer les dépendances du tableau de bord
pip install -r dashboard/requirements.txt
```

## Lancer le tableau de bord

```bash
streamlit run dashboard/app.py
```

Le tableau de bord s'ouvre automatiquement dans le navigateur à l'adresse `http://localhost:8501`.

Les données sont lues depuis le dossier `data/` (CSV et GeoJSON versionnés dans le dépôt).

## Pages du tableau de bord

| Groupe | Page | Contenu |
| ------ | ---- | ------- |
| Principal | Vue nationale | 6 chiffres clés, carte nationale, 4 thèmes, immatriculations et permis |
| Analyses | Comparaison territoriale | Zones, régions, préfectures : réseau, formation, desserte |
| Analyses | Évolutions et constats | 4 onglets : Synthèse (17 vérifications), Mobilité, Sécurité routière, Réseau |
| Analyses | Carte du réseau et des auto-écoles | 39 préfectures, routes et auto-écoles |
| Pilotage | Priorités | Zones prioritaires, les 5 qui cumulent, 10 premières, robustesse |
| Pilotage | Recommandations | 15 cartes de recommandation et 39 fiches préfectures |
| Pilotage | Horizon 2031 | Besoins projetés à +1, +3, +5 ans |
| Méthodologie | Méthodologie | Sources, méthode (9 étapes), formules, contrôles, limites, licences |

## Fichiers essentiels

```
dashboard/
├── app.py              Point d'entrée : navigation, filtres globaux, barre latérale
├── theme.py            Palette de couleurs et CSS du thème
├── composants.py       Composants réutilisables (entête, chiffres clés, constat, carte…)
├── donnees.py          Chargement des CSV et GeoJSON (aucun recalcul)
├── requirements.txt    Dépendances Python du tableau de bord
├── views/              Une page par fichier
│   ├── vue_nationale.py
│   ├── comparaison.py
│   ├── evolutions.py
│   ├── carte.py
│   ├── priorites.py
│   ├── recommandations.py
│   ├── horizon.py
│   └── methodologie.py
├── static/             Images et logos (armoiries, logo barre latérale…)
└── .streamlit/
    └── config.toml     Configuration Streamlit (thème, serveur)
```

## Données

Le tableau de bord lit les tables déjà produites dans :

- `data/analysis/` — résultats des analyses (indicateurs, priorisation, diagnostic)
- `data/processed/` — données nettoyées et transformées
- `data/reference/` — contours GeoJSON, référentiels

Aucun fichier brut lourd (PDF, raster WorldPop, archive EHCVM) n'est nécessaire pour faire tourner le tableau de bord.
