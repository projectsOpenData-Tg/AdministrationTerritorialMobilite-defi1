# Journal du design — tableau de bord

Suivi des changements de design du tableau de bord (`dashboard/`), validés un à un sur maquette avant d'être codés.
Branches : `design/sidebar-branding` (étapes 1 à 4), puis `design/palette-a` (étape 5 et suivantes, qui part de la
première). Le développement fonctionnel reste suivi dans `workspace/dev-progress.md`.

---

## 1. Barre latérale : logo et slogan (toutes les pages)

- **Logo en haut**, en face du bouton qui replie la barre (`st.logo`) : le Togo en miniature aux couleurs du drapeau,
  traversé par une route, avec « TOGO / MOBILITÉ & SÉCURITÉ ROUTIÈRE / Tableau de bord territorial d'aide à la
  décision ». Silhouette seule quand la barre est repliée.
  - Contour du pays tiré des 39 préfectures du projet (`data/processed/geo/prefectures.geojson`).
  - Produit par `scripts/logo_barre_laterale.py` → `static/logo_barre_laterale.svg` et `static/logo_togo_icone.svg`.
- **Slogan en bas** : « Des routes plus sûres pour une mobilité durable au Togo », un court filet turquoise, puis une
  illustration de montagnes et de route sinueuse (`static/routes_slogan.svg`). Poussé en bas de la barre par CSS
  quand la hauteur le permet (`composants.pied_barre_laterale`, `.slogan-barre`).

## 2. Barre du haut (toutes les pages)

- Sous-titre : « Comprendre les risques, identifier les priorités d'action » (au lieu de « Évolution de la
  mobilité, de la sécurité routière et du réseau »).
- **Superposition à l'en-tête de Streamlit Cloud (option A)** : l'en-tête de Streamlit devient transparent et notre
  barre blanche remonte tout en haut ; les boutons de Streamlit Cloud (Share, étoile, édition, GitHub) prennent place
  dans le coin droit de la barre, dont la colonne de droite leur réserve 230 px. Option B (masquer ces boutons)
  écartée. À vérifier sur l'application déployée.
- Logo Togo AI Lab aligné à droite de sa colonne.

## 3. Vue nationale : en-tête et chiffres clés

- Texte d'introduction sous le titre dans une **carte à fond blanc** (filet bleu nuit à gauche) :
  `entete(..., carte=True)`.
- **Six chiffres clés sur une seule ligne** (`rangee_kpi(..., une_ligne=True)`), 3 puis 2 colonnes sur écran étroit.
- **Pastille d'icône** du thème à gauche du titre de chaque carte (`carte_kpi(..., icone=...)`, `ICONES` dans
  `composants.py`) : personnes, voiture, triangle d'alerte, cœur-pouls, route, toque.
- Titres en MAJUSCULES, couleur d'encre ; **année entre parenthèses sous le titre** (`periode=`).
- Libellés :

  | Avant | Après |
  |---|---|
  | Population 2022 · « habitants, recensement de 2022 » | POPULATION (2022) · « habitants » |
  | Immatriculations 2024 | IMMATRICULATIONS (2024) |
  | Tués 2022 | MORTS SUR LA ROUTE (2022) |
  | Blessés 2022 | BLESSÉS SUR LA ROUTE (2022) |
  | Réseau évalué · « milliers de km, relevé de 2020 » · « 84 tronçons ; 21,2 % … » | RÉSEAU ROUTIER ÉVALUÉ (2020) · « dont 84 tronçons » · « 21,2 % en mauvais état (669 km). » |

- Étiquettes de qualité A / B / C retirées des six cartes de cette page (gardées sur les autres pages).
- Un peu d'espace avant le texte de fin de chaque carte ; chiffres alignés d'une carte à l'autre.

## 4. Palette A — institutionnelle moderne (validée)

Fond « café » `#F4F2EC` **conservé** à la demande. Le reste :

| Élément | Couleur |
|---|---|
| Cartes KPI et graphiques | blanc `#FFFFFF`, bordure `#E2E8F0`, ombre discrète |
| Barre latérale | bleu nuit `#0B263D` ; texte `#F8FAFC` ; intitulés `#CBD5E1` |
| Navigation active | fond bleu soutenu `#1769AA`, texte blanc (le jaune n'est plus sur les boutons) |
| Filtres | fond blanc, bordure `#E2E8F0`, sélection bleu `#1769AA` |
| Texte principal / secondaire | `#172B3A` / `#64748B` |
| Titres, chiffres clés | bleu nuit `#0B263D` |
| Accents nationaux | vert `#006B3F`, jaune `#FCD116`, rouge `#CE1126` |
| Barre du haut | fond blanc, titre bleu nuit, sous-titre gris ardoise, petit filet tricolore vert / jaune / rouge |

Couleurs fixes par donnée, dans `theme.py`, pour qu'un indicateur garde sa couleur sur toutes les pages :

- `SERIE` : motos `#16834A`, voitures `#2474C6`, poids lourds `#E6B422`, accidents `#CE1126`, blessés `#E87518`,
  décès `#8E1B2B`, auto-écoles `#2474C6`.
- `ETAT` (routes) : bon `#16834A`, moyen `#E6B422`, mauvais `#CE1126`, travaux `#8293A7`.
- `THEME` : Mobilité `#2474C6`, Sécurité routière `#E87518`, Réseau `#E6B422`, Couverture `#16834A`.
- Carte : rampe séquentielle bleue (`BLEUS`) pour les valeurs croissantes, inchangée.
- Vert et rouge côte à côte sont confondus par une part des daltoniens : toujours écrire le libellé ou la valeur
  à côté de la couleur.

## 5. Recommandations validées (R1, R2, R3)

- **R1 — Tendance en badge arrondi coloré** sous le chiffre (`carte_kpi(..., tendance=...)`), variation sur un an
  lue dans `indicateurs_07.csv` (`variation()` dans `vue_nationale.py`) :
  immatriculations −32,6 % vs 2023 (gris : ni bon ni mauvais), morts +0,4 % vs 2021 et blessés +5,8 % vs 2021
  (rouge : aggravation). Le vert est réservé à une amélioration démontrée.
- **R2 — Liseré fin en bas de chaque carte**, de la couleur de son thème (celle de la pastille d'icône).
- **R3 — Encadré « Constat »** sur fond blanc avec un filet jaune drapeau à gauche (toutes les pages).
- **Bloc central** : chiffre, badge de tendance et phrase qui suit (ex. « blessés déclarés ») centrés dans la carte,
  haut aligné pour que les chiffres restent sur une même ligne.
- R5 (passer les accidents en 2024) écarté : on garde 2022, année de la population de référence.

## 6. Ajustements des cartes et des sections (Vue nationale)

- Couleur (pastille d'icône et liseré bas) : **Immatriculations en vert** `#16834A`, **Morts sur la route en rouge**
  `#CE1126`, **Blessés en jaune-or** `#E6B422` (le jaune drapeau `#FCD116` est trop clair sur fond blanc pour une
  icône et un liseré lisibles).
- **Balayage lumineux au survol des chiffres clés rétabli** (il avait été retiré par la règle « pas de dégradés
  décoratifs » de la palette A).
- Section « Le Togo, préfecture par préfecture » : encadré **Constat placé sous le titre**, sur toute la largeur ;
  carte resserrée (colonnes 1,25 / 1 au lieu de 1,6 / 1) ; à droite, les légendes (régions, classes de population),
  la note sur les permis, les précisions et le lien « Voir la carte détaillée ».
- Section des thèmes renommée **« Les quatre thèmes confirmés »** ; chaque thème dans une **carte blanche arrondie**,
  liseré bas de la couleur de son titre (bleu, ambre, brique, vert), légère élévation au survol, sans balayage.
- **R4 refusé** : les émojis des cartes de thème restent tels quels.

## 7. Section carte, cartes de thème, contrôles (Vue nationale)

- Légende des régions : nombre de préfectures par région, lu dans `prefectures_10` — Maritime (8), Plateaux (12),
  Centrale (5), Kara (7), Savanes (7).
- Les deux précisions sous les légendes passent dans des **bandes-cartes** (même style que les légendes) ;
  « niveau C » retiré de la précision sur le réseau.
- **Boutons radio** de la couche : contour visible (2 px gris ardoise) même quand ils ne sont pas sélectionnés.
- **« Voir le détail »** : survol bleu `#1769AA`, texte blanc, comme la navigation de la barre latérale.
- Cartes de thème de même hauteur ; **« Voir le détail » toujours en bas** de chaque carte (Couverture comprise).
- Carte Réseau : précision « Relevé de 2020, niveau C. » retirée.

## 8. Bas de page (Vue nationale)

- « Voir le détail » : survol **bleu clair** `#E8F0FB` (texte bleu nuit), au lieu du bleu soutenu jugé trop foncé.
- **Permis de conduire délivrés** (titre sans 2024 ; sous-titre « Total et décomposition par catégorie ») : graphique
  et axes conservés ; chaque barre prend la couleur de sa catégorie, celle de la page Évolutions (A bleu, B orange,
  C vert, E vert clair, D ambre, F gris) ; chiffres alignés à droite des barres.
- **Immatriculations et permis, 1990–2024** : note de fin dans une carte (fond bleu clair, filet bleu), sur deux
  lignes — « Une date situe une variation… » puis « Repères : ① … ② … ③ … » (`.note-carte`).
- **À retenir** : carte blanche, cinq messages numérotés dans des pastilles rondes (`.retenir`).

