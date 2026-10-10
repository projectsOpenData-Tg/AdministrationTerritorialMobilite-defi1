# Tableau de bord — Mobilité et sécurité routière au Togo (Défi 1)

Restitue les résultats du projet (documents 06 à 10 et annexe Horizon 2031) : 8 pages en 4 groupes de menu.
Le tableau de bord **affiche, il ne calcule pas** (11 §2) : chaque chiffre vient d'une table déjà produite
(`data/analysis/`, `data/processed/`). Français seul.

## Lancer en local

Depuis la racine du projet :

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

L'application lit les données du dépôt (`../data`). Python 3.11.

## Déployer sur Streamlit Community Cloud

1. Dépôt : ce dépôt Git (les CSV et GeoJSON de `data/` sont versionnés ; seuls les bruts lourds — PDF, raster
   WorldPop, archive EHCVM — sont exclus et ne sont pas nécessaires au tableau de bord).
2. **Main file path** : `dashboard/app.py`.
3. **Dépendances** : `dashboard/requirements.txt` (volontairement léger — ni ydata-profiling, ni rasterio, ni
   JupyterLab, qui ne servent qu'aux scripts d'analyse). Veiller à ce que Streamlit Cloud installe **ce** fichier
   (adjacent au main file), pas le `requirements.txt` de la racine, qui est l'environnement de développement complet.
4. La configuration (`.streamlit/config.toml`), le thème et le service des fichiers statiques
   (`enableStaticServing = true`, pour `static/`) sont dans `dashboard/.streamlit/` et sont pris en compte quand le
   main file est `dashboard/app.py`.

Rien d'autre à préparer : les contours, les tables et l'armoirie sont dans le dépôt.

## Arborescence

```
dashboard/
├── app.py              navigation (8 pages, 4 groupes), filtres globaux, barre du haut
├── theme.py            palette (11 §4.1) et CSS ; correctif anti-barre Streamlit Cloud
├── composants.py       barre du haut, chiffres clés, constat, synthèse, onglets, choroplèthe, pied
├── donnees.py          lecture des CSV et GeoJSON (aucun recalcul)
├── views/              une page par fichier (vue_nationale, comparaison, evolutions, carte,
│                       priorites, recommandations, horizon, methodologie)
├── static/             armoiries-togo-ecu.svg (CC BY-SA 4.0, Edem Fiadjoe — attribution en page Méthodologie),
│                       logo_togo_ai_lab.png (repli texte si absent), logo_barre_laterale.svg et
│                       logo_togo_icone.svg (logo de la barre latérale, produits par scripts/logo_barre_laterale.py),
│                       routes_slogan.svg (illustration du slogan en bas de la barre latérale)
├── .streamlit/config.toml
└── requirements.txt
```

## Les 8 pages

| Groupe | Page | Objet |
| ------ | ---- | ----- |
| Principal | Vue nationale | synthèse : 6 chiffres clés, carte, 4 thèmes, immatriculations et permis |
| Analyses | Comparaison territoriale | zones / régions / préfectures : réseau, formation, desserte |
| Analyses | Évolutions et constats | 4 onglets : Synthèse (17 vérifications), Mobilité, Sécurité routière, Réseau |
| Analyses | Carte du réseau et des auto-écoles | 39 préfectures, une couche à la fois, routes et auto-écoles |
| Pilotage | Priorités | par où commencer : zones, 5 qui cumulent, 10 premières, robustesse |
| Pilotage | Recommandations | 7 onglets : 15 cartes du 10 et 39 fiches préfectures |
| Pilotage | Horizon 2031 | curseur d'horizon : besoins à +1, +3, +5 ans (annexe A1) |
| Méthodologie | Méthodologie | sources, méthode (9 étapes), formules, contrôles, limites, licences |
