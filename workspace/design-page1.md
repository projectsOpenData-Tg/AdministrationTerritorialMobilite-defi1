

## Page 1 — Vue nationale

**Objectif :** donner en une page la synthèse du projet. Chaque thème de l’énoncé a sa carte, qui mène à sa page de détail.

```text
┌──────────────────────────────────────────────────────────────────┐
│  LA MOBILITÉ ET LA SÉCURITÉ ROUTIÈRE AU TOGO : OÙ EN EST-ON ?     │
├──────────────────────────────────────────────────────────────────┤
│  [6 chiffres clés, en 2 rangées de 3]                             │
├──────────────────────────────────────────────────────────────────┤
│  [CARTE DU TOGO — 4 couches activables + encart permis]  │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [4 CARTES DE THÈME : Mobilité | Sécurité | Réseau | Couverture]  │
├──────────────────────────────────────────────────────────────────┤
│  [PERMIS 2024 — total et 6 catégories]                            │
├──────────────────────────────────────────────────────────────────┤
│  [IMMATRICULATIONS ET PERMIS — 1 figure, 2 étages alignés]        │
├──────────────────────────────────────────────────────────────────┤
│  [5 MESSAGES « À RETENIR »]  [SYNTHÈSE CHIFFRÉE]  [LIMITE]        │
└──────────────────────────────────────────────────────────────────┘
```

### Section 1 — 6 chiffres clés

La maquette met 3 ou 4 cartes par rangée : les 6 chiffres vont sur 2 rangées de 3.

| Chiffre clé                           | Valeur    | Sous-titre                                                                    | Niveau | Source                                               |
| -------------------------------------- | --------- | ----------------------------------------------------------------------------- | ------ | ---------------------------------------------------- |
| Population 2022                        | 8 095 498 | habitants, recensement de 2022                                                | A      | `regions_08.csv` (pays)                            |
| Immatriculations 2024                  | 88 198    | dont 74,4 % de motos (65 593)                                                 | A      | `indicateurs_07.csv` (immatriculations par groupe) |
| Tués 2022                             | 683       | tués déclarés par la police et la gendarmerie ; 7 507 accidents constatés | A      | `indicateurs_07.csv` (accidents, blessés, tués)  |
| Blessés 2022                          | 9 918     | blessés déclarés                                                           | A      | `indicateurs_07.csv`                               |
| Réseau évalué                       | 3 163 km  | 84 tronçons, relevé de 2020 ; 21,2 % en mauvais état                       | C      | `regions_08.csv` (pays)                            |
| Préfectures sans auto-école agréée | 23 sur 39 | 2 932 492 habitants                                                           | B      | `indicateurs_07.csv` (préfectures sans auto-école) |

« Immatriculations » désigne les immatriculations de l’année, pas le parc en circulation : le libellé « parc automobile immatriculé » du portail est inexact (10, REC-D4).

### Section 2 — Carte du Togo

**Fond :** les 39 préfectures, les limites des 5 régions, un encart pour le Grand Lomé.

**Couches activables :**

1. **Population par préfecture** (par défaut), en 5 classes de la palette `BLEUS` ;
2. **Auto-écoles** : 272 points en deux couleurs, les 132 agréées d’un côté, les 138 non agréées et les 2 au statut non renseigné de l’autre ;
3. **Routes classées** : le tracé, coloré par type (route nationale revêtue, route nationale non revêtue, voirie urbaine, piste rurale) ;
4. **Routes nationales seules**, mises en évidence.

**Info-bulle :** nom, zone, région, population, auto-écoles agréées, km évalués, part en mauvais état (ou « non définie » pour Mô).

**Encart :** « Permis : données nationales seulement. 38 531 permis délivrés en 2024, dont 10 165 permis moto. » (Les permis n’ont ni territoire, ni âge, ni mois : 04 §7, écart 5.)

**Lien :** « Voir la carte détaillée → » (page 4).

**Sources :** `geo/prefectures.geojson`, `geo/auto_ecoles.geojson`, `geo/routes_classees.geojson`, `prefectures_10.csv`, `indicateurs_07.csv`.

### Section 3 — 4 cartes de thème

**Format commun :** icône et titre du thème ; 3 chiffres ; une mini-visualisation ; un lien « Voir le détail → ».

**Lien « Voir le détail → » :** un bouton, pas un simple lien. Pour Mobilité et Sécurité routière, il écrit le rang de l’onglet dans `st.session_state["evolutions_rang"]` (1 Mobilité, 2 Sécurité routière), puis appelle `st.switch_page` vers la page 3, qui s’ouvre sur cet onglet (design-page3.md). Pour Réseau et Couverture, il appelle `st.switch_page` vers les pages 4 et 2.

| Thème                           | Chiffre 1                                      | Chiffre 2                                        | Chiffre 3                                                                | Mini-visualisation                                                         | Lien   |
| -------------------------------- | ---------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------ | -------------------------------------------------------------------------- | ------ |
| 🚗**Mobilité**            | 88 198 immatriculations (2024)                 | ×4,56 en 20 ans (2002 → 2022)                  | 74,4 % de motos (2024)                                                   | Courbe des immatriculations 1990–2024, ruptures de 1995 et 2004 marquées | Page 3, onglet Mobilité |
| 🚦**Sécurité routière** | 683 tués (2022)                               | 7 507 accidents constatés (2022)                | 60 % des tués sont des usagers de deux et trois-roues motorisés (2021) | Les 6 taux, 2010–2012 face à 2022–2024 : tous en baisse                 | Page 3, onglet Sécurité routière |
| 🛣️**Réseau**            | 3 163 km évalués (relevé de 2020)           | 21,2 % en mauvais état (669,34 km)              | 49 tronçons critiques                                                   | Mini-carte de la part en mauvais état par préfecture                     | Page 4 |
| 🏫**Couverture**           | 132 auto-écoles agréées, sur 272 recensées | 23 préfectures sur 39 sans auto-école agréée | 17,2 % des ruraux à moins de 2 km d’une route revêtue                 | Jauge : 16 préfectures sur 39 ont au moins une auto-école agréée       | Page 2 |

**Réserves sur les cartes :** Sécurité, « accidents déclarés, données nationales seulement » ; Réseau, « relevé de 2020, niveau C » ; Couverture, « accès rural estimé, niveau C ».

**Sources :** `indicateurs_07.csv`, `taux_09.csv`, `regions_08.csv`, `classement_08.csv`, `zones_10.csv`.

### Section 4 — Permis 2024

L’objectif 1 demande les permis délivrés par catégorie.

- **Grand chiffre :** 38 531 permis délivrés en 2024.
- **6 barres horizontales :** B 23 538 · A 10 165 · C 1 973 · E 1 554 · D 679 · F 622.
- **Phrase :** « Les permis moto ont bondi en 2022 et en 2024 : 4 837 en 2022 et 10 165 en 2024, contre 211 en 2021. »
- **Niveau :** A.

**Source :** `indicateurs_07.csv` (permis délivrés par catégorie).

### Section 5 — Immatriculations et permis

**Une figure en deux étages**, sur la même échelle des années (1990–2024). Les années sont alignées : une date se lit sur les deux séries à la fois.

- **Étage du haut :** immatriculations de l’année par groupe (motos, voitures, poids lourds, bus et cars, autres), 1990–2024. Les ruptures de série de 1995 et de 2004 sont marquées en pointillé gris, avec la mention « rupture de série ».
- **Étage du bas :** permis délivrés par catégorie, de A à F, 2007–2024. Avant 2007, l’étage reste vide, avec la mention « Permis non publiés avant 2007 ». L’année 2013 est non renseignée : la courbe s’interrompt, elle ne passe pas par zéro, et la mention « 2013 non renseignée » le dit.
- **Axes :** chaque étage a son axe vertical, à gauche ; l’axe des années est commun aux deux. Aucun étage n’a de second axe vertical : la maquette l’exclut (« jamais deux axes verticaux »).
- **Légendes :** une par étage, au-dessus de l’étage, titrées « Immatriculations de l’année » et « Permis délivrés ».
- **Couleurs : une par famille de véhicules**, dans la palette `CATEGORIELLE`. La courbe d’un groupe de véhicules et celle du permis qui le conduit ont la même couleur :

| Famille | Immatriculations | Permis | Couleur | Trait |
| ------- | ---------------- | ------ | ------- | ----- |
| Moto | motos | A | `#2a78d6` | plein |
| Voiture | voitures | B | `#eb6834` | plein |
| Poids lourd | poids lourds | C | `#1baf7a` | plein |
| Poids lourd (semi-remorques) | comptées avec les poids lourds | E | `#1baf7a` | tireté |
| Bus et car | bus et cars | D | `#eda100` | plein |
| Autres véhicules | autres | aucun permis propre | `#e87ba4` | plein |
| Aucun véhicule | aucun type immatriculé | F | `#8a8780` (gris de repère, maquette §8.13) | pointillé |

La correspondance entre véhicules et permis est lue dans `correspondance_vehicules_permis.csv` (article 9 du décret n° 2022-085/PR, établie au 05).
- **Annotations de contexte** (`chronologie_reformes.csv`) : 3 lignes tiretées qui traversent les deux étages, numérotées de 1 à 3 en haut de l’étage des immatriculations. Leur légende est sous la figure :
  1. 20 septembre 2019 : permis obligatoire pour les conducteurs de moto ;
  2. 3 août 2022 : décret d’application du code de la route, catégories A1, A2, A3 (date du décret au Journal officiel) ;
  3. novembre 2023 : tournée nationale d’immatriculation des motos.
- **Dernières valeurs** annotées en gras au bout des courbes, dans la couleur de la série : motos 65 593 ; permis B 23 538 ; permis A 10 165.
- **Notes sous la figure** (bleu foncé) :
  - en gras : « En 2021, 310 motos ont été immatriculées pour un permis moto délivré ; en 2024, 6. » Valeurs lues dans le rapport immatriculations / permis de la catégorie A (`indicateurs_07.csv` : 309,78 en 2021, 6,45 en 2024), arrondies à l’unité ;
  - « Une date situe une variation ; elle ne l’explique pas. »
- **Hauteur :** 440 px, la borne haute d’un graphique principal (maquette §8.13). Sur un écran étroit, la figure s’allonge pour laisser la place aux légendes.
- **Niveau :** A pour les séries ; B pour la phrase sur les motos.
- **Export :** les séries des deux étages, en CSV.

**Mise en œuvre :** `make_subplots(rows=2, cols=1, shared_xaxes=True)` ; deux légendes (`legend` et `legend2`, Plotly 5.15 ou plus) ; lignes de contexte en `add_vline` sur chaque étage.

**Pourquoi pas un graphique à deux axes :** 11 courbes sur deux graduations superposées font comparer des hauteurs qui ne se comparent pas, et la maquette l’exclut. Les deux étages alignés montrent la même coïncidence dans le temps.

**Maquette visuelle validée :** https://claude.ai/artifact/VeDDYy492eSvZL9HK21WJh (Équipe, 2026-10-07).

**Sources :** `indicateurs_07.csv` (immatriculations par groupe, permis par catégorie, rapport immatriculations / permis), `chronologie_reformes.csv`, `correspondance_vehicules_permis.csv`.

### Section 6 — 5 messages « À retenir » (bandeau Constat)

1. **Les immatriculations ont plus que quadruplé en 20 ans** : ×4,56 de 2002 à 2022.
2. **Les motos portent la hausse** : 80,6 % des immatriculations supplémentaires entre 2002 et 2022.
3. **Plus de véhicules, pas une route plus dangereuse** : les accidents déclarés augmentent (+9,4 % entre 2010–2012 et 2022–2024), mais les 6 taux baissent.
4. **60 % des tués de 2021 sont des usagers de deux et trois-roues motorisés**, un peu plus que leur part du parc (1,01 à 1,10 fois).
5. **7 questions restent sans réponse**, faute d’accidents par préfecture, par mois et par âge.

**Sources :** `hypotheses_09.csv`, `taux_09.csv`.

### Section 7 — Synthèse chiffrée et Limite

**Synthèse chiffrée :** 8 095 498 habitants ; 5 préfectures cumulent un réseau dégradé et aucune auto-école agréée (641 955 habitants) ; 15 recommandations, dont 3 en priorité haute. Lien vers la page 6.

**Limite :**

> « Les accidents ne sont publiés qu’au niveau national. Les volumes et les taux portent sur les accidents **déclarés** par la police et la gendarmerie, pas sur l’ensemble des accidents. Les taux par véhicule dépendent d’un parc estimé (niveau C). Le coût des actions n’est pas dans les données. »

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
