# 05 — Data Preparation

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-04 — **Statut :** **figé** le 2026-10-04
**Sources :** `01_problem_definition.md` (figé), `02_decision_matrix.xlsx` (v1.1, figé), `03_data_inventory.md` (v1.3, figé), `04_data_understanding.md` (v1.0, figé), registre `data/raw/_SOURCES.csv`

> **Question du 05 :** peut-on croiser ces données sans mentir, et quelles tables portent la décision ?
>
> Le 05 couvre les étapes 5 (qualité et validation) et 6 (tables de décision) de la procédure. Il prépare les données ; il ne calcule aucun indicateur.
>
> Les colonnes « Résultat » sont remplies à partir des sorties des scripts (R-19). Le numéro entre crochets renvoie à la ligne de `controles_05.csv`.
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §10.

---

## Point de départ : le 04

- **34 indicateurs sur 43 sont calculables** : 23 à la maille cible, 11 avec repli ; 9 ne le sont pas (04 §10).
- **Le niveau de preuve de chaque variable est fixé** (04 §3). Il suit la variable dans chaque table du 05.
- **Le parc publié est un flux** : ce sont les immatriculations de l’année, jamais un stock (04 §4.4).
- **Les jointures sont testées** : référentiel des 39 préfectures, état du réseau rattaché au tracé (84 tronçons sur 84, par la table `data/reference/correspondance_etat_trace.csv`), points de départ de O4-08 (04 §5).
- **Le 04 transmet au 05** 6 anomalies et 3 points du profil et de l’annuaire (04 §4.5) : ils sont traités au §3.

---

## 1. Objectif du Data Preparation

Passer des fichiers bruts à des tables propres, **sans perdre, doubler ni inventer une valeur**, et les réunir dans les tables qui porteront la décision.

**Sorties :**
1. un registre des anomalies et des exclusions, avec la décision prise pour chacune (§3) ;
2. une table nettoyée par besoin, de D1 à D13 (§4) ;
3. les jointures finales et une table maîtresse par préfecture (§5) ;
4. les variables dérivées : des numérateurs et des dénominateurs (§6) ;
5. les contrôles de validation, dont les contrôles bloquants (§7).

**Règles :**
- `data/raw/` n’est jamais modifié.
- Une valeur manquante n’est jamais un zéro (R-10). Un zéro n’est gardé que s’il est prouvé, et la preuve est citée.
- **Aucun ratio, aucun indicateur, aucun seuil, aucun classement.** Les tables portent les numérateurs et les dénominateurs ; les indicateurs viennent après l’exploration. Seule exception : le parc estimé, qui est aussi le dénominateur de O2-04 (§6).
- Chaque valeur garde sa source, son année et son niveau de preuve (R-17).
- Une décision est prise avant d’en voir l’effet sur les résultats (R-20).
- Aucune lecture causale.

**Le 05 est terminé quand :**
- chaque anomalie transmise a sa décision, appliquée et inscrite au registre ;
- chaque table de `data/processed/` a passé ses contrôles ;
- la table maîtresse compte les 39 préfectures du référentiel ;
- les contrôles bloquants sont conformes.

---

## 2. Méthode et outils

**Outils.** Ceux du 04, dans le même environnement `.venv` (`requirements.txt`) : pandas ; geopandas, shapely et pyproj.

**Scripts**, dans `scripts/`. ✅ Chaque fichier de `data/processed/` n’a qu’un script qui l’écrit : pour le changer, on change ce script, jamais le fichier.

| Script | Rôle | Sorties |
| ------ | ---- | ------- |
| `nettoyage_05.py` | Applique les décisions du §3 ; nettoie chaque fichier (§4) | Tables sans territoire à rattacher (D1, D2, D3, D4 national, D7 national, D9, D10, D12, contexte) ; tables nettoyées avant jointure, dans `data/interim/05_nettoyage/` ; `registre_anomalies.csv`, `lignes_05.csv` |
| `jointures_05.py` | Jointures finales et table maîtresse (§5) ; variables dérivées (§6). Reprend la règle de normalisation des noms du 04 (`cle_troncon`) | Tables par territoire (D4, D5, D6, D7 par préfecture, D13) ; `D1_parc_estime.csv`, `D7_population_age_conduire.csv` ; table maîtresse et dictionnaire ; couches de `geo/` ; `jointures_05.csv` |
| ✅ `validation_05.py` | Contrôles du §7, recalculés depuis `data/raw/` sans reprendre le code des deux autres scripts. Un contrôle bloquant en échec arrête la chaîne | `controles_05.csv` |

Les scripts lisent `data/raw/`, `data/reference/` et les extractions du 04 dans `data/interim/` (Livret 02, annuaire 2024, profil OMS, points de départ de O4-08). Ils ne refont pas l’extraction des PDF.

**Sorties :**
- `data/processed/` : les tables (§8) ;
- `data/analysis/05_preparation/` : le registre des anomalies, le décompte des lignes, les jointures et les contrôles.

**Pour tout reproduire :** la chaîne du 04, puis `nettoyage_05.py`, `jointures_05.py` et `validation_05.py`. **Résultat :** chaîne relancée deux fois après chaque modification, 35 fichiers de sortie identiques octet pour octet.

**Règles appliquées :**

| Règle | Objet | Où, dans le 05 |
| ----- | ----- | -------------- |
| R-10 | Une valeur manquante n’est jamais un zéro | Permis de 2013 ; cellules « - » du Livret 02 et de l’annuaire ; tronçons à 0 voie ; adresses « Nsp » ; ménages sans section dans l’EHCVM |
| R-14 | Un tronçon non évalué n’est pas en bon état | Km du tracé national sans état, comptés « non évalués » (§6) |
| R-15 | Tronçon à cheval sur deux territoires | Découpage du tracé par préfecture ; état réparti au prorata des km (§5) |
| R-16 | Longueurs, surfaces et distances en UTM 31N | Km du tracé, surfaces des préfectures. Les couches d’affichage sont en WGS 84 |
| R-01 | La préfecture, brique commune | Routes et auto-écoles rattachées par le polygone, jamais par le nom déclaré |
| R-04 | La somme des zones égale le total national | Population, km, auto-écoles (§7) |
| R-12 | Auto-écoles dont l’activité est inconnue | Colonne « comptée » : agréées et antennes agréées |
| R-17 | Niveau de preuve | Une colonne « niveau » dans chaque table ; le dictionnaire, pour la table maîtresse |

---

## 3. Qualité : traitement des anomalies du 04

### 3.1 Les anomalies transmises

Le 04 transmet 6 anomalies et 3 points (04 §4.5). Le plan en annonçait 5 : ce sont les 5 contrôles de cohérence, auxquels s’ajoutent l’anomalie des jointures [4.3-11] et 3 points du profil et de l’annuaire.

Le 05 en a trouvé une dixième : 24 polygones de passages piétons dont le contour se recoupe (n° 10).

### 3.2 Décision pour chacune

Trois décisions possibles :
- **corriger** : la valeur change, la règle est citée ;
- **documenter** : la valeur publiée est gardée, avec sa réserve ;
- **exclure** : la valeur ne sort pas dans `data/processed/`.

Aucune décision n’impute de valeur. ✅ Décisions 1 à 9 validées avec le plan, décision 10 validée ensuite.

| N° | Anomalie | Décision | Traitement | Résultat |
| -- | -------- | -------- | ---------- | -------- |
| 1 | Annuaire 39.2 : deux lignes de 2022 ne font pas 100 % (99,90 % et 99,54 %) [4.1-06] | Documenter | Pourcentages publiés, sans remise à 100 % ; la somme de chaque ligne est gardée dans la table | Appliqué : 2 lignes |
| 2 | Livret 02 : un écart d’une personne (hommes ruraux de Doufelgou, 25-29 ans et 85 ans et plus), repris dans la Kara et au Togo [4.1-09] | Documenter | Valeurs publiées ; la colonne « Ensemble » fait référence ; aucune correction | Appliqué : 6 cellules |
| 3 | Ruptures de série : parc en 1995 et 2004, permis en 2016, 2019 et 2022 [4.2-02] | Documenter | Valeurs gardées ; colonne « Rupture » dans D1 et D2, pour les annoter ; ni lissage ni exclusion | Appliqué : 32 lignes annotées |
| 4 | « Accidents mortels /100 000 hab » : accidents constatés rapportés à la population ; 2010 calculé sur la projection de 2011 [4.4-06] | Exclure | Indicateur non repris ; O2-03 sera recalculé avec les accidents et la population (B) | Appliqué : 13 valeurs exclues |
| 5 | Profil OMS : 11 777 km revêtus en 2021, 5,3 fois le réseau revêtu [4.4-12] | Exclure | Chiffre sans définition ni périmètre, jamais repris | Appliqué : 1 valeur exclue |
| 6 | Taux de couverture de l’entretien routier : 0 ou 1 % [4.3-11] | Exclure le taux | La longueur entretenue (km, 2016–2019) est gardée, en contexte de O3 | Appliqué : 4 valeurs du taux exclues, 4 longueurs gardées |
| 7 | Routes classées : 8 tronçons à 0 voie (04 §3) | Corriger | 0 devient « non renseigné » (R-10) : une route tracée a au moins une voie | Appliqué : 8 tronçons |
| 8 | Auto-écoles : 2 au statut « Néant » [4.1-08] | Documenter | Statut « non renseigné » ; gardées dans la table, jamais comptées (R-12) | Appliqué : 2 auto-écoles |
| 9 | Annuaire 2024 : deux-roues 6 487 et trois-roues 59 106, contre 62 736 et 4 903 en 2022 [4.4-01] | Documenter | La catégorie retenue, « deux-roues et assimilées », somme les deux lignes, comme le portail (contrôlé sur 2020–2022). La somme ne dépend pas de l’ordre des lignes ; le détail de l’annuaire n’est pas repris | Appliqué : 2 lignes de 2024 sommées |
| 10 | **Nouveau.** Passages piétons : 24 polygones dont le contour se recoupe, donc des géométries invalides (contrôle 7-16) | Corriger | Géométrie réparée (`shapely.make_valid`), puis calée sur une grille de 0,1 mm, qui retire les débris de surface nulle laissés par la réparation ; nombre d’équipements gardé | Appliqué : 24 polygones ; 16 797 géométries valides sur 16 797. Surface enclose gardée : 65,594 m² avant, 65,593 m² après (écart 0,0008 %, sous le seuil de 0,1 %). Un polygone perd une pointe de surface nulle, de 2,4 m [7-16, 7-21] |

Le registre (`registre_anomalies.csv`) reprend ces 10 lignes, avec le fichier, le nombre de valeurs touchées et la date de la décision.

### 3.3 Impact sur les indicateurs

| N° | Indicateurs touchés | Impact attendu |
| -- | ------------------- | -------------- |
| 1 | O3-07 | Aucun : la réserve figure déjà au 04 (§8) |
| 2 | O1-07, O4-03, PA-03 | Une personne sur 8 095 498 : aucun |
| 3 | O1-01 à O1-03, O1-06 | Aucun en valeur ; les ruptures sont annotées sans lecture causale (H1) |
| 4 | O2-03 | Aucun : déjà recalculé (04 §4.4) |
| 5 | — | Aucun |
| 6 | Contexte de O3 | Aucun |
| 7 | — | Aucun : aucun indicateur n’utilise le nombre de voies |
| 8 | O4-04 à O4-08 | Aucun : les 2 auto-écoles sont déjà hors des 132 comptées |
| 9 | O1-01 à O1-03 | Aucun sur la catégorie « deux-roues et assimilées » |
| 10 | — | Aucun : couche facultative, hors 02 |

**Impact attendu :** aucun indicateur ne change de calculabilité ni de niveau de preuve ; la synthèse du 04 (23 / 11 / 9) reste valable.

**Résultat :** aucune décision n’a retiré une donnée dont un indicateur a besoin, et chaque jointure des besoins réussit à 100 % [7-12]. La synthèse du 04 reste valable.

---

## 4. Nettoyage par fichier

Chaque table de `data/processed/` porte au moins la valeur, l’année, la source et le niveau de preuve. Une ligne retirée l’est pour un motif écrit dans le script.

**Résultat** (`lignes_05.csv`) : 18 fichiers lus, 27 820 lignes brutes, 26 016 gardées, 1 804 retirées, chacune avec son motif [7-01].

### D1 — Immatriculations

- **Sources :**
  - portail, fichier 1 (1990–2022) ;
  - annuaire 2024, tableau 40.1 (2023 et 2024).

  Le fichier 2 et les statistiques clés ne servent qu’au contrôle : ils donnent la même série (4.4-01).
- **Nettoyage :**
  - la ligne « Total » est retirée, après le contrôle « total = somme des types » ;
  - « Voitues » devient « Voitures » ;
  - la grandeur s’appelle « immatriculations de l’année », jamais « parc » (écart 16) ;
  - annuaire : « deux-roues et assimilées » = 2 roues + 3 roues (anomalie 9) ; les « 4 roues moto », absents du portail, ne sont pas repris.
- ✅ **Groupe O1**, selon les catégories du 02 (O1-01) :

  | Groupe | Types |
  | ------ | ----- |
  | Moto | deux-roues et assimilées |
  | Voiture | voitures |
  | Poids lourd | camions, semi-remorques, tracteurs |
  | Bus et car | autocars et autobus |
  | Autres | camionnettes |

- **Sortie :** `D1_immatriculations.csv` : année, type, groupe, valeur, source, niveau (A), rupture.
- **Résultat :** 245 lignes, 7 types de 1990 à 2024 ; l’annuaire égale le portail sur 2020–2022, deux-roues = 2 roues + 3 roues.

### D2 — Permis

- **Sources :** portail (2007–2022) ; annuaire 2024, tableau 40.4 (2023 et 2024). Les deux sont identiques sur 2020–2022 (4.4-09).
- **Nettoyage :**
  - la ligne « Total » est retirée, après le contrôle « total = somme des catégories » ;
  - les catégories sont codées de A à F ;
  - **2013** : aucune catégorie et un total à 0. Toutes ses valeurs sont « non renseignées », jamais 0 (R-10, écart 14).
- **Sortie :** `D2_permis.csv` : année, catégorie, valeur, statut (publié ou non renseigné), source, niveau (A), rupture.
- **Résultat :** 108 lignes, 6 catégories de 2007 à 2024 ; 2013 vide. Les 7 zéros de la table sont publiés : catégorie F, de 2007 à 2014, hors 2013 [7-13].

### D3 — Accidents

- **Série de référence, 2010–2024** (4.4-05) : statistiques clés de 2010 à 2022, puis annuaire 2024, tableau 7.2, pour 2023 et 2024. Les deux fichiers « accidents » ne servent qu’au contrôle.
- **Nettoyage :**
  - libellés : « accidents constatés » (écart 15), « tués », « blessés » ;
  - l’indicateur « accidents mortels /100 000 hab » est exclu (anomalie 4).
- **Victimes par type d’usager** (O2-09) : part des tués déclarés en 2021, tirée du profil OMS, en C.
- **Sorties :** `D3_accidents.csv` (année, mesure, valeur, source, niveau A) ; `D3_victimes_usager_2021.csv`.
- **Résultat :** 45 valeurs ; les deux fichiers « accidents » et l’annuaire de 2020 à 2022 sont identiques à la série de référence.

### D4 — État du réseau

- **Nettoyage :**
  - lignes retirées : les totaux, sur le tronçon (« TOTAL », « TOTAL RT ») et sur l’état ; les lignes de voiries sans tronçon ;
  - une ligne par tronçon : km en bon état, moyen, mauvais, en travaux, et total ;
  - un tronçon sans ligne « TRAVAUX » a 0 km en travaux. Ce zéro est prouvé : les états publiés font le total du tronçon (4.1-05). Ce n’est pas une imputation.
- **État national en pourcentage** (O3-07) : annuaire 39.2, de 2020 à 2022, avec la somme de chaque ligne (anomalie 1).
- **Sorties :** `D4_etat_troncons.csv` (84 tronçons, relevé de 2020, niveau C ; écrit par `jointures_05.py` avec le rattachement au tracé et les zones traversées) ; `D4_etat_national_pct.csv`.
- **Résultat :**
  - 84 tronçons ; 18 lignes retirées (10 de total, 8 de voiries) ;
  - 67 tronçons à 0 km en travaux, chacun sans ligne « TRAVAUX » dans le brut [7-14] ;
  - annuaire : un « - » (routes non revêtues en travaux, 2020), laissé vide (R-10) ; la ligne fait 100 % sans lui.

### D5 — Tracé

- **Nettoyage :**
  - géométries WKT en degrés, reprojetées en UTM 31N pour les longueurs (R-16) ;
  - découpage par préfecture (R-15) ; les km hors du Togo sont exclus (4.3-05) ;
  - 8 tronçons à 0 voie : « non renseigné » (anomalie 7) ;
  - 2 tronçons sans nom : gardés. Ce sont des voiries urbaines : leurs km comptent pour O4-01, et ils ne portent pas d’état.
- **Sorties :** `D5_trace_prefecture.csv` (§5) ; `geo/routes_classees.geojson`, en WGS 84, pour les cartes.
- **Résultat :** 799 tronçons gardés ; 3 361,4 km dans les 39 préfectures, 5,1 km hors du Togo [7-08].

### D6 — Auto-écoles

- **Nettoyage :**
  - préfecture prise dans le polygone qui contient le point (R-01) ; la préfecture déclarée est gardée pour mémoire ;
  - statut : agréée, antenne agréée, non agréée, ou non renseigné (« Néant », anomalie 8) ;
  - colonne « comptée » (R-12) : agréée ou antenne agréée ;
  - adresses « Nsp » et « Néant », jours d’ouverture « Nsp » : non renseignés (R-10) ;
  - colonne `activite_categorie` retirée : une seule valeur, « {Auto-école} » (04 §6) ;
  - l’offre est en C : « activité non vérifiée » (écart 13).
- **Sorties :** `D6_auto_ecoles.csv` ; `geo/auto_ecoles.geojson`.
- **Résultat :** 272 auto-écoles, dont 132 comptées ; 171 adresses et 16 jours d’ouverture non renseignés [7-09, 7-15].

### D7 — Population

- **2022, par préfecture** : Livret 02, identique au recensement CSV (4.5-02). Total, sexe, milieu et groupes d’âges. Les cellules « - » sont non renseignées (R-10) ; l’écart d’une personne est documenté (anomalie 2).
- **Série nationale annuelle**, avec la source de chaque année (R-06) :

  | Années | Source | Niveau |
  | ------ | ------ | ------ |
  | 1990–2009 | Reconstituée à partir de 2010 avec les taux de croissance de WPP (écart 7) | C |
  | 2010 | Recensement | A |
  | 2011–2021 | Projections de l’INSEED | C |
  | 2022 | Recensement | A |
  | 2023–2024 | Projections de l’INSEED | C |

- **Population nationale par âge**, pour les années des permis (O1-07) :
  - groupes quinquennaux du Livret 02 en 2022 (A), des projections de l’INSEED de 2011 à 2021 et en 2023-2024 (C) ;
  - avant 2011, parts par âge de WPP appliquées à la série nationale (C) ;
  - les âges simples de WPP découpent les groupes 15-19 et 20-24 aux âges minimaux de PA-05 (03 §5).
- **Sorties :** `D7_population_prefecture_2022.csv` (écrit par `jointures_05.py`, avec le nom du référentiel) ; `D7_population_nationale.csv` ; `D7_population_age_nationale.csv`.
- **Résultat :**
  - 143 cellules « - » vides dans les préfectures [7-13], dont la population rurale de Golfe et d’Agoè-Nyivé ;
  - série nationale de 1990 à 2024, sans trou ; recensements et projections repris à l’identique [7-11] ;
  - en 2022, l’âge non déclaré du recensement forme un groupe à part, hors des âges minimaux.

### D8 — Référentiel

- 39 préfectures (03, D8). Golfe = TG0303 + TG0305 ; surfaces en UTM 31N ; région ; zone (6 zones, Grand Lomé séparé, R-02 et R-03).
- **Sortie :** `geo/prefectures.geojson`, en WGS 84 avec la surface en km². Ses attributs entrent dans la table maîtresse.
- **Résultat :** 39 préfectures, 6 zones, 5 régions [B-01].

### D9–D13 — Autres (contexte)

| Besoin | Contenu préparé | Sortie | Niveau |
| ------ | --------------- | ------ | ------ |
| D9 | Repères de l’OMS : tués estimés en 2021, avec leur fourchette (SE-03) ; tués pour 100 000 habitants dans 4 pays. Jamais une correction des tués déclarés | `D9_repere_oms.csv` | C |
| D10 | Trafic de marchandises et de passagers, 2014–2022, national | `D10_trafic.csv` | C |
| D11 | Chronologie des réformes, lue telle quelle dans `data/reference/` | — | sans objet |
| D12 | EHCVM, par zone, les mesures du 03 : possession d’une moto, d’une voiture, d’un vélo ; recours au moto-taxi et achat de carburant pour moto dans les 7 derniers jours. Ménages concernés et ménages ayant rempli la section, pondérés : la part se calculera au 07. Règle des lignes absentes (04 §6) ; seuls des agrégats par zone sortent (licence). DHS : possession par région, 1998–2017, telle que publiée | `D12_menages_zone.csv`, `D12_dhs_region.csv` | C |
| D13 | Points de départ de O4-08 : 30 chefs-lieux et 9 points d’étiquette (écart 19) | `D13_points_depart_o4_08.csv` | C |
| Hors 02 | Longueur de route entretenue, 2016–2019, km seulement (anomalie 6) ; équipements de sécurité, en couche facultative (anomalie 10) | `contexte_entretien.csv`, `geo/equipements.geojson` | C |

---

## 5. Jointures finales

Le taux attendu est de 100 % pour chaque jointure. Tout reste est listé (`jointures_05.csv`).

| Jointure | Clé | Méthode | Attendu | Résultat |
| -------- | --- | ------- | ------- | -------- |
| D4 × D5 | Nom du tronçon | Nom exact, nom normalisé, puis ✅ `correspondance_etat_trace.csv` (04 §5). L’état de chaque tronçon est réparti entre préfectures au prorata des km de son tracé ; pour un axe, le long de l’axe (R-15). Les préfectures et zones traversées sont écrites dans `D4_etat_troncons.csv` (O3-05) | 84 tronçons sur 84 ; km de l’état conservés | 84 sur 84 : 59 par le nom exact, 16 par le nom normalisé, 7 par l’axe, 2 par un nom proche validé. Km répartis = km de l’état : bon 997,02, moyen 735,54, mauvais 669,34, travaux 761,57 [7-07, 7-12] |
| D5 × D8 | Polygone | Intersection du tracé avec les 39 polygones | Tout le tracé du Togo rattaché ; Mô à 0 km, un zéro prouvé (5-05) | 799 tronçons sur 799 ; Mô : aucun tracé dans son polygone, 0 km [7-08, 7-14] |
| D6 × D8 | Polygone | Point dans le polygone | 272 auto-écoles sur 272 | 272 sur 272 [7-12] |
| D7 × D8 | Libellé du Livret 02 | Nom du référentiel | 39 préfectures sur 39 | 39 sur 39 ; les préfectures font les 6 zones et le pays, 8 095 498 habitants [7-10] |
| D13 × D8 | Préfecture | Un point par préfecture | 39 sur 39 | 39 sur 39 [7-12] |
| Hors 02 | Polygone | Équipements, point dans le polygone | Plus de 99 % (4.3-10) | 16 768 sur 16 797 (99,8 %) [7-12] |

**Table maîtresse par préfecture** (`table_maitresse_prefecture.csv`) : une ligne par préfecture, 39 lignes. Elle porte :
- l’identité : préfecture, code HDX, région, zone, surface ;
- la population de 2022 : totale, par sexe, par milieu ;
- les km de routes classées, par type ;
- les km de l’état du réseau, par état, et les km de routes nationales non évalués ;
- les auto-écoles recensées et comptées (R-12) ;
- l’origine du point de départ de O4-08.

Aucune colonne d’accidents : ils ne sont publiés qu’au niveau national (écart 1).

Un dictionnaire (`dictionnaire_table_maitresse.csv`) donne, pour chaque colonne, sa définition, son unité, sa source, son année et son niveau de preuve.

**Résultat :**
- 39 lignes et 22 colonnes, toutes décrites par le dictionnaire [7-17, B-01] ;
- 2 cellules vides : la population rurale de Golfe et d’Agoè-Nyivé, « - » dans le Livret 02 [7-15] ;
- les zéros de km et d’auto-écoles sont des absences mesurées dans le polygone, et le dictionnaire le dit.

---

## 6. Variables dérivées

Ce sont des numérateurs et des dénominateurs. Aucun ratio n’est calculé ici.

| Variable | Définition | Données | Maille | Niveau | Pour |
| -------- | ---------- | ------- | ------ | ------ | ---- |
| Km par préfecture et par état | Km de chaque état du tronçon × part de la préfecture dans son tracé ; km du tracé national sans tronçon rattaché comptés « non évalués » (R-14) | D4, D5 | Préfecture | C (état), B (non évalué) | O3-01 à O3-03, O3-06 |
| Km par préfecture et par type de route | Longueur des morceaux du tracé, en UTM 31N | D5 | Préfecture | B | O4-01 à O4-03 |
| Population 2022 par préfecture | Livret 02 : totale, par sexe, par milieu | D7 | Préfecture | A | O4-03, O4-05, O4-06, O5-03 |
| Auto-écoles par préfecture | Recensées ; comptées (agréées et antennes agréées, R-12) | D6 | Préfecture | A (comptage), C (offre) | O4-04 à O4-08 |
| Année de référence | 2022 (R-05) dans chaque table. L’état reste daté de 2020, le tracé et les auto-écoles de la collecte 2021-2022 | Toutes | — | — | Tous |

✅ **Trois ajouts :**

| Variable | Définition | Données | Maille | Niveau | Pour |
| -------- | ---------- | ------- | ------ | ------ | ---- |
| Parc estimé | Cumul des immatriculations de l’année et des L − 1 années précédentes, par groupe, pour la valeur centrale et les deux bornes de PA-01 : motos 7 ans [5–10] ; voitures, poids lourds, bus et cars, camionnettes 15 ans [10–20]. Une année sans L années de série est non renseignée, jamais 0 | D1, PA-01 | National | C | O1-05, O2-04 |
| Population en âge de conduire, par catégorie de permis et par année | Population nationale ayant l’âge minimal de la catégorie (`ages_minimaux_permis.csv` : 18 ans, ou 21 ans pour C et D) | D7, PA-05 | National | C | O1-07 |
| Correspondance entre véhicules et permis | A : deux-roues et assimilées ; B : voitures, camionnettes ; C : camions, tracteurs ; D : autocars et autobus ; E : semi-remorques ; F : aucun type immatriculé à part. Tirée des définitions de l’article 9 du décret n° 2022-085/PR ; écrite dans `data/reference/correspondance_vehicules_permis.csv` | D1, D2 | National | B | O1-09 |

**Parc estimé.**
- C’est à la fois l’indicateur O1-05 et le dénominateur de O2-04 (R-11, écart 16). Le 05 le calcule une seule fois, comme dénominateur ; le 07 le lit sans le recalculer.
- ✅ PA-01 ne donne pas de durée de vie aux camionnettes (groupe « Autres ») : 15 ans [10–20], la valeur que PA-01 donne à tous les autres véhicules à 4 roues. Le 02, figé, n’est pas modifié (R-20) : la raison est écrite ici, au journal, et dans la colonne « Note » de `D1_parc_estime.csv`.
- Les ruptures de 1995 et 2004 (anomalie 3) entrent dans le cumul ; elles restent annotées.

**Tronçons critiques (O3-05).**
- O3-05 lit directement `D4_etat_troncons.csv` ; aucune autre table n’est nécessaire.
- Chaque tronçon y porte ses km par état, son rattachement au tracé et les zones qu’il traverse : c’est la désagrégation que demande le 02.
- O3-05 est en C (04 §8), parce que la notation de l’état n’est pas documentée.

**Correspondance entre véhicules et permis.** Le 04 la renvoyait « au 06 », l’étape des tables de décision, que couvre ce 05.

**Résultat :**
- **Parc estimé :** complet de 2009 à 2024 pour tous les groupes ; chaque valeur égale la somme de sa fenêtre, et les bornes sont ordonnées [7-18].
- **Population en âge de conduire :** 108 valeurs, de 2007 à 2024, toutes inférieures à la population de l’année [7-19].
- **Correspondance véhicules ↔ permis :** les 7 types immatriculés sont placés, chacun dans une seule catégorie ; F n’a pas de type à part [7-20].
- **Km par état :** le réseau national est évalué à 96,8 % ; restent 99 km non évalués, dans 13 préfectures [B-03].

---

## 7. Validation du nettoyage

**Résultat** (`controles_05.csv`, 2026-10-04) : 25 contrôles, dont 3 bloquants ; 25 conformes.

| Contrôle | Attendu | Résultat |
| -------- | ------- | -------- |
| Lignes avant et après, par fichier | Lignes brutes = lignes gardées + lignes retirées, chacune avec son motif | Conforme : 27 820 = 26 016 + 1 804, sur 18 fichiers ; les 13 fichiers bruts recomptés donnent le même nombre. Lignes des tables produites conformes à l’attendu (types × années, 84 tronçons, 272 établissements, 39 préfectures) [7-01, 7-02] |
| Totaux conservés | D1 et D2 : somme des catégories = total publié, chaque année (sauf 2013) ; D3 : séries publiées ; D4 : km par état = total de chaque tronçon ; D4 × D5 : km répartis = km de l’état ; D5 : morceaux + hors Togo = tracé ; D6 : 272 ; D7 : préfectures = zones = pays | Conforme. D1 : 35 années sur 35 ; D2 : 17 sur 17 ; D3 : 45 valeurs sur 45 ; D4 : 3 163,49 km, écart max. par tronçon 0,01 km ; D4 × D5 : km répartis égaux, état par état ; D5 : 3 361,4 km recalculés dans les polygones ; D6 : 272, dont 132 comptées ; D7 : 8 095 498 partout, série nationale identique aux sources [7-03 à 7-11] |
| Taux de succès des jointures | 100 % pour chaque jointure du §5 | Conforme : 100 % pour chaque besoin ; équipements, 99,8 % [7-12] |
| Valeurs manquantes « non renseignées » | Aucun zéro là où la source n’a rien (permis de 2013, cellules « - », 0 voie) ; chaque zéro gardé a sa preuve (travaux, Mô) ; nombre de valeurs non renseignées par table | Conforme. Aucun zéro inventé : les 7 zéros de permis sont publiés ; les 67 travaux à 0 sont prouvés ; Mô n’a aucun tracé. Cases vides, colonnes d’annotation exclues : parc estimé, 49, 76 et 104 selon la borne, faute de L années de série ; permis de 2013, 6 ; annuaire 39.2, 1 ; auto-écoles, 171 adresses et 16 jours d’ouverture ; population par préfecture, 143 ; bornes OMS, 8 ; table maîtresse, 2 [7-13, 7-14, 7-15] |
| Variables dérivées | Parc estimé : chaque valeur = somme des immatriculations de sa fenêtre ; borne basse ≤ valeur centrale ≤ borne haute ; années sans fenêtre complète non renseignées. Population en âge de conduire ≤ population totale de l’année | Conforme : 0 écart au recalcul ; bornes ordonnées ; population en âge de conduire toujours inférieure au total [7-18, 7-19] |
| Correspondance véhicules ↔ permis | Chaque type immatriculé dans une seule catégorie | Conforme : 7 types sur 7 [7-20] |
| Population totale de chaque préfecture | 39 totaux renseignés ; les cellules vides ne touchent que les ventilations | Conforme : 39 totaux sur 39. Les 143 cellules vides sont des ventilations par milieu, sexe ou âge, dont 126 en milieu rural à Golfe et Agoè-Nyivé. Les indicateurs par préfecture, qui prennent la population totale (O4-03, O4-05, O4-06, O5-03), n’en sont pas touchés ; PA-03 non plus, puisqu’il classe le Grand Lomé urbain par règle [7-22] |
| Anomalie 10 : surface des polygones réparés | Écart < 0,1 % face à la surface enclose par le contour brut (l’aire d’un contour qui se recoupe est mal définie : ses lobes s’annulent) | Conforme : 65,594 m², puis 65,593 m² (écart 0,0008 %) ; un polygone perd une pointe de surface nulle, de 2,4 m [7-21] |
| Types | Années en entiers ; valeurs numériques ; codes en texte ; géométries valides | Conforme : 4 couches, toutes leurs géométries valides, en WGS 84 (après l’anomalie 10) [7-16] |
| Niveau de preuve | Chaque valeur de `data/processed/` a une source et un niveau | Conforme : chaque ligne de chaque table ; la table maîtresse, par son dictionnaire [7-17] |

**Contrôles bloquants** (procédure, étape 5). Un échec arrête la chaîne.

| Contrôle | Attendu | Résultat |
| -------- | ------- | -------- |
| Entités par maille = découpage officiel | 39 préfectures, 6 zones, 5 régions dans la table maîtresse | Conforme : 39 préfectures, 6 zones, 5 régions [B-01] |
| Aucune somme au-dessus du total réel | Préfectures ≤ pays pour la population, les km et les auto-écoles | Conforme : population 8 095 498 = pays ; 272 auto-écoles = fichier ; 3 163,5 km de l’état = total [B-02] |
| Aucune couverture nationale à 0 % ni à 100 % | Part du réseau national évaluée, part des préfectures avec une auto-école comptée : strictement entre 0 et 100 % | Conforme : réseau national évalué à 96,8 % ; 16 préfectures sur 39 (41,0 %) ont une auto-école comptée ; 23 n’en ont aucune, dont 15 sans aucune auto-école recensée [B-03] |

---

## 8. Fichiers produits

**Dans `data/processed/` :**

| Fichier | Contenu | Maille |
| ------- | ------- | ------ |
| `D1_immatriculations.csv` | Immatriculations de l’année, par type et par groupe, 1990–2024 | National |
| `D1_parc_estime.csv` | Parc estimé par groupe et ensemble : borne basse, valeur centrale, borne haute (PA-01), 1990–2024, complet de 2009 à 2024 | National |
| `D2_permis.csv` | Permis délivrés, par catégorie, 2007–2024 (2013 non renseignée) | National |
| `D3_accidents.csv` | Accidents constatés, tués, blessés, 2010–2024 | National |
| `D3_victimes_usager_2021.csv` | Part des tués par type d’usager, 2021 | National |
| `D4_etat_troncons.csv` | Km par état, rattachement au tracé, zones traversées ; 84 tronçons, 2020 (O3-05) | Tronçon |
| `D4_etat_national_pct.csv` | État en %, par catégorie de route, 2020–2022 | National |
| `D4_D5_etat_trace.csv` | Km par type de route et par état, dont les km nationaux non évalués | Préfecture |
| `D5_trace_prefecture.csv` | Km de routes classées, par type | Préfecture |
| `D6_auto_ecoles.csv` | Auto-écoles, statut, préfecture, « comptée », coordonnées | Établissement |
| `D7_population_prefecture_2022.csv` | Population 2022, par sexe, milieu et âge | Préfecture |
| `D7_population_nationale.csv` | Population, 1990–2024, avec la source de chaque année | National |
| `D7_population_age_nationale.csv` | Population par âge, 2007–2024 | National |
| `D7_population_age_conduire.csv` | Population ayant l’âge minimal de chaque catégorie de permis, 2007–2024 | National |
| `D9_repere_oms.csv`, `D10_trafic.csv`, `D12_menages_zone.csv`, `D12_dhs_region.csv`, `D13_points_depart_o4_08.csv`, `contexte_entretien.csv` | Contexte et repères (§4) | Variable |
| `table_maitresse_prefecture.csv` et `dictionnaire_table_maitresse.csv` | Une ligne par préfecture (§5) | Préfecture |
| `geo/prefectures.geojson`, `geo/routes_classees.geojson`, `geo/auto_ecoles.geojson`, `geo/equipements.geojson` | Couches des cartes, en WGS 84 (10 Mo, dont 5,6 pour les routes) | — |

**Dans `data/reference/` :** ✅ `correspondance_vehicules_permis.csv` (§6), une source par ligne.

**Dans `data/interim/05_nettoyage/` :** les tables nettoyées avant jointure ; elles se régénèrent.

**Dans `data/analysis/05_preparation/` :** `registre_anomalies.csv`, `lignes_05.csv`, `jointures_05.csv` et `controles_05.csv`.

---

## 9. Suite

Le 05 couvre les étapes 5 et 6 de la procédure. L’étape suivante est la 7, l’exploration, avant tout indicateur. La procédure est explicite : « l’EDA précède tout indicateur », et chaque indicateur porte sa justification, issue de l’exploration.

✅ **Validé :**
- **06 — Exploration** (étape 7) : distributions, comparaisons entre préfectures et entre zones, cartes. Elle cherche les écarts, avec les cinq contradictions de la procédure, dont les préfectures voisines très différentes.
- **07 — Indicateurs** (étape 8) : calcul des 34 indicateurs calculables, à partir des tables du 05, avec leur niveau de preuve.

**Transmis au 06 :**
- **Offre de formation.** 23 préfectures sur 39 n’ont aucune auto-école comptée, dont 15 n’ont aucune auto-école recensée [B-03]. À explorer en priorité pour O4 et O5, avec la réserve R-12 : activité non vérifiée. La valeur de O4-07 sera établie au 07.
- **Réseau non évalué.** Il reste 99 km de routes nationales sans état, dans 13 préfectures (§6).

---

## 10. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 05** : étapes 5 et 6 de la procédure dans un seul document ; aucun ratio ni indicateur | Tout le document | Équipe, 2026-10-04 |
| ✅ **Décisions sur les 9 anomalies et points transmis par le 04** | §3 | Équipe, 2026-10-04 |
| ✅ **Groupes de O1** (moto, voiture, poids lourd, bus et car, autres) et types qui les composent | §4, D1 | Équipe, 2026-10-04 |
| ✅ **Parc estimé** (O1-05, O2-04) préparé au 05, une seule fois, en C ; camionnettes à 15 ans [10–20], faute de valeur dans PA-01 | §6 | Équipe, 2026-10-04 |
| ✅ **Correspondance entre véhicules et permis**, tirée de l’article 9 du décret | §6 ; `data/reference/correspondance_vehicules_permis.csv` | Équipe, 2026-10-04 |
| ✅ **Troisième script, `validation_05.py`** | §2, §7 | Équipe, 2026-10-04 |
| ✅ **Suite** : 06 Exploration, puis 07 Indicateurs | §9 | Équipe, 2026-10-04 |
| ✅ **Anomalie 10** : 24 polygones de passages piétons réparés (`shapely.make_valid`, grille de 0,1 mm), avec un contrôle de surface : écart < 0,1 % | §3 ; §7 [7-21] | Équipe, 2026-10-04 |
| ✅ **Tables d’étape** : un seul script écrit chaque fichier de `data/processed/` ; on change le script, jamais le fichier ; les tables nettoyées avant jointure passent par `data/interim/05_nettoyage/` | §2 | Équipe, 2026-10-04 |
| ✅ **Camionnettes hors PA-01** : raison écrite dans le 05 et dans `D1_parc_estime.csv`, sans toucher au 02 figé (R-20) | §6 | Équipe, 2026-10-04 |
