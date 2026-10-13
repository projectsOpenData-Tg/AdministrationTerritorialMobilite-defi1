# Rapport de couverture — ce qui était prévu, ce que le tableau de bord affiche

**Projet :** Mobilité et sécurité routière au Togo
**Date :** 13 octobre 2026
**Références :** `workspace/_PROJECT.txt` (énoncé), `01_problem_definition.md` (§3, objectifs), `02_decision_matrix/01_Matrice.csv` (43 indicateurs), `02_Hypotheses.csv` (17 vérifications et hypothèses), `data/analysis/07_indicateurs/catalogue_07.csv` (indicateurs calculés), tableau de bord `dashboard/` (8 pages)

---

## 1. En bref

| Mesure                                                        | Résultat                    |
| ------------------------------------------------------------- | --------------------------- |
| Pages du tableau de bord exécutées sans erreur                | **8 sur 8**                 |
| Indicateurs du socle (prévus sans condition) affichés         | **91,7 %** (27,5 sur 30)    |
| Ensemble des indicateurs du 02 (socle + « si données »)       | **70,9 %** (30,5 sur 43)    |
| Vérifications et hypothèses du 02 affichées avec leur verdict | **17 sur 17** (10 tranchées, 7 non testables) |
| Recommandations au format du 01 (§3.5) et de la règle R-18    | **15 sur 15**               |

Le socle est presque entièrement couvert. L'écart vient surtout de l'objectif 2 : les accidents ne sont publiés qu'au niveau national, sans mois, âge, sexe ni véhicule. Huit indicateurs « si données » n'ont donc pas pu être calculés. Ce manque était anticipé dans le 01 (§2.3, unité de décision) et il est écrit sur le tableau de bord (pages Évolutions, Carte et Méthodologie).

---

## 2. Méthode

1. **Ce qui était prévu.** Ce sont les 43 indicateurs de `01_Matrice.csv`. Le 02 en marque 30 « Socle » (à produire quoi qu'il arrive) et 13 « Si données » (à produire si la source le permet). S'y ajoutent les éléments de cadre du 01 : mailles, carte à couches, hypothèses, priorisation et format des recommandations.
2. **Ce qui a été calculé.** Ce sont les 35 lignes de `catalogue_07.csv`, plus O5-01 et O5-02, calculés au 08 (`classement_08.csv`).
3. **Ce qui est affiché.** Chaque page a été exécutée hors navigateur avec `streamlit.testing` (AppTest). Le texte, les tableaux, les graphiques et les contrôles rendus ont été relevés, puis rapprochés des indicateurs. Aucune page ne lève d'exception.
4. **Notation de chaque indicateur :**

| Statut                       | Points | Sens                                                                          |
| ---------------------------- | :----: | ------------------------------------------------------------------------------ |
| ✅ Affiché                   | 1      | Montré sur une page, sous la forme prévue ou une forme équivalente            |
| 🟡 Partiel                   | 0,5    | Montré sous une forme réduite (une seule année, un seul exemple, sans les désagrégations prévues) |
| 🔸 Calculé, non affiché      | 0      | Présent dans les CSV du 07, absent des pages (hors table des formules)        |
| ⛔ Non calculé (données)     | 0      | Aucune source ne le permet ; manque déclaré au 03 et au 04                    |

Le pourcentage d'un objectif est la somme des points divisée par le nombre d'indicateurs prévus. Il est donné deux fois : sur le socle, et sur l'ensemble.

---

## 3. Couverture par objectif

| Objectif (énoncé)                                                                        | Prévus (socle + si données) | ✅ | 🟡 | 🔸 | ⛔ | **Couverture du socle** | **Couverture totale** | Pages qui l'affichent                                               |
| ----------------------------------------------------------------------------------------- | :--------------------: | :-: | :-: | :-: | :-: | :---------------------: | :-------------------: | -------------------------------------------------------------------- |
| **O1** — Évolution des immatriculations et des permis par catégorie                      | 9 (8 + 1)              | 7  | 0  | 1  | 1  | **87,5 %** (7/8)        | **77,8 %** (7/9)      | Vue nationale ; Évolutions et constats (onglet Mobilité)             |
| **O2** — Sécurité routière : accidents, blessés, tués, par habitant et par véhicule      | 14 (6 + 8)             | 4  | 3  | 1  | 6  | **75,0 %** (4,5/6)      | **39,3 %** (5,5/14)   | Vue nationale ; Évolutions et constats (onglet Sécurité routière) ; Horizon 2031 |
| **O3** — État du réseau par tronçon et par région                                        | 7 (5 + 2)              | 5  | 2  | 0  | 0  | **100 %** (5/5)         | **85,7 %** (6/7)      | Vue nationale ; Comparaison ; Évolutions (onglet Réseau) ; Carte     |
| **O4** — Carte du réseau classé et des auto-écoles, rapportés à la population            | 9 (7 + 2)              | 8  | 0  | 0  | 1  | **100 %** (7/7)         | **88,9 %** (8/9)      | Vue nationale ; Comparaison ; Carte ; Horizon 2031                   |
| **O5** — Recommandations ciblées (sécurité, formation, entretien)                        | 4 (4 + 0)              | 4  | 0  | 0  | 0  | **100 %** (4/4)         | **100 %** (4/4)       | Priorités ; Recommandations ; Horizon 2031                           |
| **Total**                                                                                 | **43 (30 + 13)**       | **28** | **5** | **2** | **8** | **91,7 %** (27,5/30) | **70,9 %** (30,5/43) |                                                                       |

**Lecture :**

- **O1** : il ne manque au socle que les permis pour 1 000 habitants en âge de conduire (O1-07). L'indicateur est calculé mais pas affiché, parce que le dénominateur ne se raccorde pas d'une source à l'autre (limite n° 7 de la page Méthodologie). La pyramide des âges des nouveaux titulaires (O1-08) est impossible : les permis n'ont ni âge ni sexe.
- **O2** : les 4 taux principaux (volumes, tués et accidents pour 100 000 habitants, tués pour 10 000 véhicules) sont affichés, avec 3 compléments et le repère OMS. La gravité (O2-05, O2-06) n'apparaît pas comme indicateur. Les 8 indicateurs « si données » sont limités par l'absence d'accidents détaillés.
- **O3** : le socle est complet. Le détail par type de route (O3-04) et l'évolution de l'état (O3-07) sont partiels, faute de relevé de tronçons sur plusieurs années.
- **O4** : couverture complète, sauf la capacité de formation (O4-09), que la campagne PRISE n'a pas publiée.
- **O5** : couverture complète. La seule réserve est de fond : le risque n'étant pas mesuré par territoire, la priorisation porte sur deux leviers (réseau, formation) au lieu des quatre dimensions prévues par le 01 (§2.1). C'est le repli prévu au 01 (§2.3).

---

## 4. Détail indicateur par indicateur

### O1 — Mobilité

| ID    | Indicateur prévu (02)                                  | Statut   | Ce qui est affiché, et où                                                                                         |
| ----- | ------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------ |
| O1-01 | Immatriculations par catégorie                         | ✅       | Courbes par groupe 1990–2024, ruptures 1995 et 2004 (Évolutions › Mobilité, mode « Volume ») ; double graphique immatriculations / permis (Vue nationale) |
| O1-02 | Part de chaque catégorie                               | ✅       | Mode « Part (%) » du même graphique ; 74,4 % de motos en 2024 (KPI)                                               |
| O1-03 | Croissance, TCAM, multiplicateur                       | ✅       | ×4,56 de 2002 à 2022 ; 7,8 % par an sur 1990–2024 (motos 11,7 %, voitures 4,2 %)                                  |
| O1-04 | Immatriculations pour 1 000 habitants                  | ✅       | Mode « Pour 1 000 habitants » (B en 2010 et 2022, C les autres années)                                           |
| O1-05 | Parc estimé                                            | ✅       | « Parc estimé des véhicules, 2009–2024 », valeur centrale et fourchette (751 398 en 2024)                        |
| O1-06 | Permis délivrés par catégorie                          | ✅       | Courbes permis A à F, 2007–2024, 2013 non renseignée ; barres 2024 (Vue nationale)                                |
| O1-07 | Permis pour 1 000 habitants en âge de conduire         | 🔸       | Calculé au 07, non affiché ; cité seulement en limite (Méthodologie, limite n° 7)                                 |
| O1-08 | Permis par sexe et tranche d'âge *(si données)*        | ⛔       | Les permis n'ont ni âge ni sexe dans la source                                                                     |
| O1-09 | Rapport immatriculations / permis                      | ✅       | « Immatriculations pour un permis, cumul 2007–2024 » : 40 motos par permis moto                                  |

### O2 — Sécurité routière

| ID    | Indicateur prévu (02)                                         | Statut   | Ce qui est affiché, et où                                                                                  |
| ----- | ------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| O2-01 | Accidents corporels, blessés, tués                            | ✅       | Trois courbes 2010–2024 (Évolutions › Sécurité routière) ; 683 tués et 7 507 accidents en 2022 (Vue nationale) |
| O2-02 | Tués pour 100 000 habitants                                   | ✅       | Graphique « Les 6 taux » 2010–2012 face à 2022–2024 ; KPI −29,4 %. National seulement (pas de carte)        |
| O2-03 | Accidents corporels pour 100 000 habitants                    | ✅       | Même graphique                                                                                              |
| O2-04 | Tués pour 10 000 véhicules                                    | ✅       | Même graphique, sur le parc estimé (C)                                                                     |
| O2-05 | Tués pour 100 accidents corporels                             | 🟡       | Seulement comme exemple de formule (Méthodologie : 9,1 tués pour 100 accidents en 2022)                    |
| O2-06 | Blessés pour 100 accidents corporels                          | 🔸       | Calculé au 07, non affiché                                                                                  |
| O2-07 | Accidents par catégorie de véhicule *(si données)*            | ⛔       | Véhicule impliqué non publié                                                                                |
| O2-08 | Surreprésentation d'une catégorie *(si données)*              | 🟡       | Non calculé au 07, mais approché : 60 % des tués à deux ou trois-roues pour 54,7 à 59,7 % de motos dans le parc (Évolutions, Recommandations) |
| O2-09 | Victimes par type d'usager, sexe et âge *(si données)*        | 🟡       | Tués par type d'usager, 2021 seulement, sans sexe ni âge                                                    |
| O2-10 | Part des véhicules non immatriculés *(si données)*            | ⛔       | Non publié                                                                                                  |
| O2-11 | Indice de saisonnalité *(si données)*                         | ⛔       | Pas de série mensuelle                                                                                      |
| O2-12 | Accidents pour 100 km de route classée *(si données)*         | ⛔       | Accidents non localisés                                                                                     |
| O2-13 | Surreprésentation des jeunes conducteurs *(si données)*       | ⛔       | Âge des conducteurs non publié                                                                              |
| O2-14 | Accidents par cause déclarée *(si données)*                   | ⛔       | Causes non publiées                                                                                         |

**Hors notation, affichés en plus :** blessés pour 100 000 habitants (O2-E1), accidents et blessés pour 10 000 véhicules (O2-E2, O2-E3), et le repère OMS (×2,63 le taux déclaré en 2021).

### O3 — État du réseau

| ID    | Indicateur prévu (02)                                  | Statut   | Ce qui est affiché, et où                                                                                         |
| ----- | ------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------ |
| O3-01 | Km par état                                            | ✅       | Barres empilées bon / moyen / mauvais / travaux / non évalué par zone (Comparaison) ; couches d'état (Carte, carte 3) |
| O3-02 | Part des km en mauvais état                            | ✅       | Carte choroplèthe (Vue nationale) ; 21,2 % national ; seuil de 22,13 % ; colonne de chaque tableau               |
| O3-03 | Part des km en travaux                                 | ✅       | Segment « Travaux » des barres ; couche « travaux » de la carte ; colonne du tableau des tronçons                 |
| O3-04 | Km par type de route et par état *(si données)*        | 🟡       | Seulement revêtue / non revêtue (routes nationales) : tableau des 84 tronçons, « 34 revêtus, 15 non revêtus »    |
| O3-05 | Tronçons critiques                                     | ✅       | 49 tronçons sur 84 (table triée, carte, barres par zone traversée) ; recommandation « 10 tronçons les plus dégradés » |
| O3-06 | Part du réseau non évaluée                             | ✅       | Segment et couche « non évalué » ; colonne « Réseau non évalué » (Comparaison)                                   |
| O3-07 | Évolution de l'état *(si données)*                     | 🟡       | Part en mauvais état 2020–2022 d'après l'annuaire national (national, une catégorie) ; pas d'évolution par tronçon |

### O4 — Réseau classé et auto-écoles rapportés à la population

| ID    | Indicateur prévu (02)                                  | Statut   | Ce qui est affiché, et où                                                                                         |
| ----- | ------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------ |
| O4-01 | Km de routes classées, par classe                      | ✅       | Réseau coloré par type (nationale revêtue, non revêtue…) sur les cartes ; réglage « Routes classées par type »   |
| O4-02 | Densité routière                                       | ✅       | Couche « Densité routière » (Carte) ; colonne « Km /1 000 km² » (Comparaison)                                   |
| O4-03 | Km de routes pour 10 000 habitants                     | ✅       | Couche dédiée (Carte) ; colonne et seuil de desserte (Comparaison, Priorités)                                    |
| O4-04 | Nombre d'auto-écoles                                   | ✅       | 272 recensées, dont 132 agréées : points sur les cartes, liste filtrable (Carte)                                |
| O4-05 | Auto-écoles pour 100 000 habitants                     | ✅       | Couche choroplèthe ; axe vertical du nuage réseau × formation (Comparaison) ; seuil de formation (Priorités)     |
| O4-06 | Habitants par auto-école                               | ✅       | Colonne « Habitants / agréée » de la liste des auto-écoles (Carte)                                               |
| O4-07 | Préfectures sans auto-école                            | ✅       | 23 sur 39 sans auto-école agréée ; « nature du zéro » (15 sans aucune recensée, 8 avec des non agréées)          |
| O4-08 | Distance à l'auto-école la plus proche *(si données)*  | ✅       | Barres par préfecture avec seuil de 10 km (Comparaison) ; couche (Carte) ; 26 préfectures à plus de 10 km        |
| O4-09 | Capacité de formation *(si données)*                   | ⛔       | Activité, moniteurs et véhicules non publiés (recommandation « Publier l'activité des auto-écoles »)             |

**Prévus au 01 (§3.4) pour la carte et affichés :** limites des régions et des préfectures, réseau coloré par classe, auto-écoles en points (agréées ou non), fond coloré par indicateur, info-bulle, agrandissement de la Maritime et du Grand Lomé.

### O5 — Priorités et recommandations

| ID    | Indicateur prévu (02)                    | Statut   | Ce qui est affiché, et où                                                                                         |
| ----- | ---------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| O5-01 | Nombre de déficits par territoire        | ✅       | 5 préfectures à 2 déficits, 26 à 1, 8 à 0 ; colonne « Déficits » (Priorités)                                    |
| O5-02 | Rang de priorité                         | ✅       | Classement des 38 préfectures, score décomposé réseau / formation, 10 premières (Priorités)                     |
| O5-03 | Population concernée                     | ✅       | À côté de chaque rang et sur chaque carte de recommandation                                                       |
| O5-04 | Écart à la cible                         | ✅       | 304,6 km à remettre en état ; 41 auto-écoles à ouvrir en 2022 (48 à l'horizon 2029)                              |

---

## 5. Autres éléments du cadre (01 et 02)

| Élément prévu                                                          | Source             | Statut | Ce qui est affiché                                                                                    |
| ---------------------------------------------------------------------- | ------------------ | ------ | ------------------------------------------------------------------------------------------------------ |
| Lecture national → région → préfecture ; 6 zones, Grand Lomé à part   | 01 §2.3 ; R-02, R-03 | ✅   | Choix de maille « Zones (6) / Régions » ; filtres Zone, Priorité et Levier dans la barre latérale    |
| Carte interactive à couches                                            | 01 §3.4            | ✅     | Page Carte : 8 couches thématiques et 5 couches d'état, zoom, fiche préfecture au clic               |
| Immatriculations et permis côte à côte, catégorie par catégorie       | 01 §3.1            | ✅     | Graphique à deux étages (Vue nationale) ; rapport par catégorie (Évolutions)                           |
| Deux lectures du risque : par habitant et par véhicule                | 01 §3.2            | ✅     | Les 6 taux, national seulement                                                                         |
| 17 vérifications et hypothèses tranchées                               | 02 `02_Hypotheses` | ✅     | Verdicts : 7 confirmées, 2 infirmées, 1 nuancée, 7 non testables (Évolutions › Synthèse) ; les 7 non testables et la donnée qui manque (Méthodologie) |
| Seuils et méthode de classement ; test de sensibilité                  | 02 `03_Seuils`, `05_Priorisation` | ✅ | Curseur du poids du réseau et 5 tests de robustesse (Priorités)                          |
| Profils de territoire (6) qui orientent le levier                      | 02 `04_Profils`    | 🟡     | Seuls les profils réseau et formation sont utilisables ; les profils fondés sur le risque ne le sont pas (risque non territorialisé) |
| Format de recommandation (territoire, cible, population, horizon, acteur, suivi, preuve, réserve) | 01 §3.5 ; R-18 | ✅ | 15 cartes avec un panneau « Détail » ; horizons 1, 3 et 5 ans                             |
| Niveaux de preuve A / B / C visibles                                    | R-17               | ✅     | Étiquette sur chaque KPI ; tableau des niveaux (Méthodologie)                                         |
| Repère externe (OMS)                                                    | 02 SE-03 ; D9      | ✅     | Tués déclarés face à l'estimation OMS, 2021                                                           |
| Chronologie des réformes                                                | D11                | ✅     | Repères 2019, 2022 et 2023 sur le graphique immatriculations / permis                                 |
| Lecture mensuelle et saisonnalité                                       | 01 §2.3 ; R-07, R-08 | ⛔   | Aucune source mensuelle                                                                               |
| Désagrégations par sexe et par âge                                      | 01 §2.3            | ⛔     | Absentes des sources (permis, victimes)                                                               |

---

## 6. Ce qui a été construit au-delà du plan

- **Annexe A1 — Horizon 2031** (page Horizon 2031). Elle projette les besoins à 1, 3 et 5 ans, mesure l'effort que demande la cible de la Décennie sur les tués et propose 48 sites candidats pour ouvrir des auto-écoles.
- **Accès rural à une route revêtue**, mesuré de deux façons : population uniforme et grille WorldPop (Priorités, Méthodologie).
- **Équipements de sécurité routière** (16 797 panneaux, ralentisseurs, feux et passages piétons) en couche sur la carte.
- **Page Méthodologie**, qui reprend ce que devaient porter les documents 12 (validation) et 13 (rapport final), non écrits. Elle contient les sources, les contrôles étape par étape, les formules, les limites et les licences.
- **Sélecteur de langue** dans la barre latérale (voir `README_traduction.md`).

---

## 7. Points d'attention relevés pendant l'analyse

1. **Chiffres écrits dans le code (règle R-19).** La règle veut qu'aucun chiffre ne soit retapé. Pourtant, plusieurs valeurs sont saisies directement dans `dashboard/views/evolutions.py` au lieu d'être lues dans un CSV :
   - les données du graphique « Tronçons en mauvais état par zone traversée » (l. 645-646) ;
   - les KPI de l'onglet Mobilité (×4,56 ; 7,8 % ; 74,4 %, l. 387-391) ;
   - les KPI de l'onglet Sécurité routière (−29,4 % ; +9,4 % ; ×2,63, l. 515-521) ;
   - les KPI de l'onglet Réseau (3 163 km ; 21,2 % ; 49 sur 84, l. 611-615).

   Les valeurs concordent aujourd'hui avec les CSV, mais elles ne suivraient pas une mise à jour des données. Les autres pages n'ont pas été passées en revue ligne à ligne sur ce point.
2. **Deux indicateurs calculés mais invisibles** (O1-07, O2-06). Ils pourraient être ajoutés à l'onglet concerné, avec leur réserve, sans nouveau calcul.
3. **Avertissements Streamlit** : `use_container_width` était déprécié (retrait annoncé après le 31/12/2025). *Corrigé le 13/10/2026 : les 12 appels utilisent désormais `width="stretch"`.*
