# 07 — Indicateurs

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-06 — **Statut :** **figé** le 2026-10-06
**Sources :** `01_problem_definition.md` (figé), `02_decision_matrix.xlsx` (v1.1, figé), `03_data_inventory.md` (v1.3, figé), `04_data_understanding.md` (v1.0, figé), `05_data_preparation.md` (v1.0, figé), `06_exploration.md` (v1.0, figé), tables de `data/processed/`, `data/analysis/06_exploration/signaux_06.csv`

> **Question du 07 :** combien valent les indicateurs du 02, et sur quoi chacun repose-t-il ?
>
> Le 07 couvre l’étape 8 de la procédure. Il calcule 32 indicateurs du 02, avec la formule du 02, à la maille obtenue au 04 et avec son niveau de preuve. Il y ajoute 3 compléments de l’énoncé (écart 22). Chaque indicateur porte sa justification, issue du 06. Le 07 ne classe pas et ne calcule aucun score : c’est le 08.
>
> Chaque chiffre cité vient de `data/analysis/07_indicateurs/`, écrit par `indicateurs_07.py` (R-19).
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §10.

---

## Point de départ : le 06

- **34 indicateurs sont calculables** : 23 à la maille cible, 11 avec repli (04 §10).
- **2 passent au 08** (06 §9) : le rang de priorité (O5-02), qui est un score, et le nombre de déficits (O5-01), qui compte des seuils franchis. **Le 07 en calcule donc 32** : 23 à la maille cible, 9 avec repli.
- **9 indicateurs ne sont pas calculables** (04 §8) : O1-08 ; O2-07, O2-08, O2-10 à O2-14 ; O4-09.
- **Les seuils de classement** (SE-02 à SE-07, SE-10) s’appliquent au 08. SE-01 et SE-08 restent au 07 : ils entrent dans les formules de O2-02 (R-09) et de O4-08 (06 §9).
- **Le 06 transmet au 07** (06 §9) :
  - déclarer l’écart du 02 sur O5-01 et O5-02 (§6) ;
  - ne jamais mélanger le relevé de 2020 (O3-01 à O3-06) et l’annuaire 39.2 (O3-07), qui diffèrent sur chaque part [SIG-27] ;
  - annoter les années atypiques des séries nationales, sans lecture causale [SIG-01 à SIG-14] ;
  - afficher le volume à côté du taux [SIG-31, SIG-41, SIG-43].

---

## 1. Objectif du 07

Donner à chaque indicateur sa valeur, sa source, son année et son niveau de preuve, et dire sur quoi il repose. C’est le catalogue d’indicateurs de la procédure (étape 8) : définition, maille, source, sens de lecture, niveau de preuve, justification.

**Sorties :**
1. `indicateurs_07.csv` : les valeurs, une ligne par indicateur × territoire × année × catégorie ;
2. `catalogue_07.csv` : une ligne par indicateur, avec sa justification (§5) ;
3. `controles_07.csv` : les contrôles du §7.

**Règles :**
- `data/processed/` n’est jamais modifié.
- La formule est celle du 02 ; un repli est celui du 04. Toute autre différence est un écart, déclaré au §6 avant le calcul (R-20).
- Un taux porte son numérateur et son dénominateur, dans la même ligne : le volume est toujours à côté du taux (06 §9).
- Une valeur manquante reste « non renseignée », et un rapport sans dénominateur « non défini » (R-10).
- Le niveau de preuve est celui du 04 (§8), porté valeur par valeur : un comptage garde le sien ; un rapport est en B, ou en C si l’un de ses termes l’est (R-17).
- Aucun seuil de classement, aucun rang, aucun score, aucune hypothèse tranchée (§9).

**Le 07 est terminé quand :**
- les 32 indicateurs et les 3 compléments ont leurs valeurs, chacune avec sa source, son année et son niveau ;
- chaque indicateur a sa justification issue du 06 ;
- les écarts 20 à 22 sont déclarés ;
- les contrôles du §7 sont conformes.

---

## 2. Méthode et outils

**Outils.** Ceux des étapes précédentes, dans le même environnement `.venv` : pandas, geopandas, numpy. Aucun nouveau paquet.

**Script** : `scripts/indicateurs_07.py`.
- Il lit les tables du 05 (`data/processed/`) et `data/reference/`.
- Il lit, sans les recopier à la main, le nom, la définition, la formule et le sens de lecture de chaque indicateur dans le 02 (`02_decision_matrix/01_Matrice.csv`), ainsi que SE-01 et SE-08 (`03_Seuils.csv`). Il lit aussi la maille obtenue, la période et le niveau dans le 04 (`faisabilite_indicateurs.csv`), et les signaux du 06.
- Il écrit les trois fichiers du §8.

**Contrôles.** Ils comparent les valeurs du 07 à celles que le 06 a calculées de son côté, avec la même formule (`rapports_06.csv`, `prefectures_06.csv`). Deux calculs indépendants doivent donner la même valeur.

✅ **Ni figure ni notebook au 07.** Le 06 montre déjà ces grandeurs (29 figures), et le tableau de bord (11) les restituera à partir de `indicateurs_07.csv`. La vérification qu’un notebook ferait à l’œil, le contrôle de concordance avec le 06 la fait en chiffres : une erreur de calcul y apparaît comme un écart (§7).

**Pour tout reproduire :** la chaîne du 05, puis `exploration_06.py`, puis `indicateurs_07.py`.

---

## 3. Calcul par objectif

Le niveau est celui du 04 (§8). La justification cite le signal du 06 qui la porte, ou le paragraphe de résultat du 06 quand aucun signal ne s’y rapporte (§5).

### O1 — Mobilité (8 indicateurs, national)

| ID | Indicateur | Calcul au 07 | Période | Niveau | Justification (06) |
| -- | ---------- | ------------ | ------- | ------ | ------------------ |
| O1-01 | Immatriculations par catégorie | Lues dans D1, par groupe | 1990–2024 | A | Années atypiques à annoter [SIG-01 à SIG-04] |
| O1-02 | Part de chaque catégorie | Groupe / total × 100 | 1990–2024 | B | Part des motos de 22,2 % à 74,4 % (06 §3, O1) |
| O1-03 | Croissance annuelle, TCAM, multiplicateur | Par groupe et pour l’ensemble ; TCAM sur 1990–2024 ; multiplicateur sur 20 ans, de 2010 à 2024 | 1990–2024 | B | Ruptures de 1995 et 2004, à annoter [SIG-01] |
| O1-04 | Immatriculations pour 1 000 habitants | Population de la même année (R-06) | 1990–2024 | B en 2010 et 2022, C sinon | Raccord de population de 2011 [SIG-11] |
| O1-05 | Parc estimé | Lu dans `D1_parc_estime.csv`, calculé une seule fois au 05 (05 §6) | 2009–2024 | C | Fourchette à 51,4 % de la valeur centrale en 2024 : jamais sans ses bornes (06 §3, O1) |
| O1-06 | Permis délivrés par catégorie | Lus dans D2 ; 2013 non renseignée | 2007–2024 | A | Années atypiques à annoter [SIG-05 à SIG-10] |
| O1-07 | Permis pour 1 000 habitants en âge de conduire | Dénominateur : `D7_population_age_conduire.csv` | 2007–2024 | C | Hausse de A en 2022 et 2024 [SIG-05] |
| O1-09 | Rapport immatriculations / permis | Par catégorie de permis (correspondance du 05), par année et en cumul | 2007–2024 | B | Écarts entre catégories en cumul : de 0,37 (D) à 40,2 (A) (06 §3, O1) |

**Résultat :**
- En 2024 : 88 198 immatriculations, dont 74,4 % de motos.
- Croissance annuelle moyenne de 1990 à 2024 : 7,8 % pour l’ensemble, 11,7 % pour les motos.
- Multiplicateur sur 20 ans : 4,56 en 2022 (2022 face à 2002). En 2024, il vaut 1,83, mais il part de 2004, année de rupture : la note le dit.
- Parc estimé en 2024 : 751 398 véhicules, entre 579 845 et 965 702.

### O2 — Sécurité (7 indicateurs et 3 compléments, national)

Les accidents ne sont publiés qu’au niveau national (écart 1) : O2-01 à O2-03, O2-05 et O2-06 sont en repli national. R-09 ne joue pas au national : il y a au moins 470 tués par an, bien au-dessus de SE-01 (20).

| ID | Indicateur | Calcul au 07 | Période | Niveau | Justification (06) |
| -- | ---------- | ------------ | ------- | ------ | ------------------ |
| O2-01 | Accidents constatés, blessés, tués | Lus dans D3 | 2010–2024 | A | Années atypiques à annoter [SIG-12 à SIG-14] |
| O2-02 | Tués pour 100 000 habitants | Population de la même année (R-06) | 2010–2024 | B en 2010 et 2022, C sinon | Raccord de population de 2011 [SIG-11] ; repère de l’OMS (SE-03) appliqué au 08 |
| O2-03 | Accidents constatés pour 100 000 habitants | Idem | 2010–2024 | B en 2010 et 2022, C sinon | [SIG-11, SIG-12] |
| O2-04 | Tués pour 10 000 véhicules | Dénominateur : le parc estimé, avec ses bornes (R-11) | 2010–2024 | C | Fourchette large (06 §3, O2) |
| O2-05 | Tués pour 100 accidents constatés | Tués / accidents × 100 | 2010–2024 | B | De 7,9 à 16,6 (06 §3, O2) |
| O2-06 | Blessés pour 100 accidents constatés | Blessés / accidents × 100 | 2010–2024 | B | De 103,2 à 201,3 (06 §3, O2) |
| O2-09 | Victimes par type d’usager | Lues dans `D3_victimes_usager_2021.csv` | 2021 | C | 60 % de deux et trois-roues motorisés (06 §3, O2) |
| O2-E1 | Blessés pour 100 000 habitants | ✅ **Complément de l’énoncé, hors 02 (écart 22)** : blessés / population × 100 000 ; règles de O2-02 | 2010–2024 | B en 2010 et 2022, C sinon | Taux non exploré au 06 (hors 02) ; blessés atypiques en 2016 [SIG-14] ; raccord de population [SIG-11] |
| O2-E2 | Accidents constatés pour 10 000 véhicules | ✅ **Complément, hors 02 (écart 22)** : accidents / parc estimé × 10 000 ; règles de O2-04 | 2010–2024 | C | Taux non exploré au 06 (hors 02) ; accidents atypiques [SIG-12] ; fourchette du parc (06 §3, O2) |
| O2-E3 | Blessés pour 10 000 véhicules | ✅ **Complément, hors 02 (écart 22)** : blessés / parc estimé × 10 000 ; règles de O2-04 | 2010–2024 | C | Taux non exploré au 06 (hors 02) ; [SIG-14] ; fourchette du parc (06 §3, O2) |

**Résultat :** les 6 taux de l’énoncé sont calculés de 2010 à 2024. En 2024 :

| Mesure | Pour 100 000 habitants (C) | Pour 10 000 véhicules du parc estimé (C), avec la fourchette |
| ------ | -------------------------- | ------------------------------------------------------------ |
| Accidents constatés | 77,4 (O2-03) | 86,89 [67,61 ; 112,60] (O2-E2) |
| Blessés | 107,6 (O2-E1) | 120,83 [94,01 ; 156,58] (O2-E3) |
| Tués | 7,08 (O2-02) | 7,95 [6,18 ; 10,30] (O2-04) |

La comparaison des deux lectures, et de leur évolution, se fait au 09.

### O3 — Réseau (7 indicateurs)

O3-01 à O3-06 viennent du relevé de 2020 (D4 × D5) ; O3-07 vient de l’annuaire 39.2. Les deux ne sont jamais mélangés : ils diffèrent sur chaque part [SIG-27].

| ID | Indicateur | Calcul au 07 | Maille | Niveau | Justification (06) |
| -- | ---------- | ------------ | ------ | ------ | ------------------ |
| O3-01 | Km par état | Km par état, répartis sur le tracé (R-15) | Préfecture | C | [SIG-20, SIG-27] |
| O3-02 | Part des km en mauvais état | Mauvais / km évalués × 100 ; non défini pour Mô | Préfecture | C | Danyi, Blitta, Kloto hors des bornes [SIG-20] |
| O3-03 | Part des km en travaux | Travaux / km évalués × 100 | Préfecture | C | Médiane 21,85 % ; 10 préfectures à 0 (06 §3, O3) |
| O3-04 | Km par type et par état | Somme par zone, type de route nationale et état, non évalué compris | Zone | C | De 7,7 % à 40,3 % en mauvais état selon la zone (06 §3, O3) |
| O3-05 | Tronçons critiques | ✅ Le 02 dit « classe nationale, état mauvais ». Le relevé donne des km par état pour chaque tronçon : sont retenus les tronçons qui ont des km en mauvais état, triés par ces km (repli du 02 : « tronçons en mauvais état de plus grande longueur »). Nombre et somme des km, par zone traversée | Tronçon | C | Carte des tronçons (06 §3, O3) |
| O3-06 | Part du réseau non évaluée | Km sans état / km de routes nationales du tracé × 100 | Préfecture | B | 7 préfectures hors des bornes [SIG-21] |
| O3-07 | Évolution de l’état | ✅ Part de chaque état, l’année moins l’année précédente, en points, par catégorie de route : 2021 − 2020, 2022 − 2021 | National | C | Deux sources de 2020 en désaccord [SIG-27] |

**Résultat :**
- 49 tronçons ont des km en mauvais état, 669,34 km en tout. Les Plateaux en portent le plus : 23 tronçons, 292,15 km. Un tronçon compte dans chaque zone qu’il traverse.
- O3-02 est défini pour 38 préfectures ; Mô n’a aucun km évalué.
- O3-07 : 23 différences sur 24. Celle des routes non revêtues en travaux, de 2020 à 2021, est non définie : « - » dans l’annuaire de 2020.

### O4 — Couverture (8 indicateurs, préfecture)

| ID | Indicateur | Calcul au 07 | Période | Niveau | Justification (06) |
| -- | ---------- | ------------ | ------- | ------ | ------------------ |
| O4-01 | Km de routes classées, par classe | Lus dans D5, par type | Collecte 2021-2022 | B | [SIG-16 à SIG-18] ; Mô sans route classée [SIG-44] |
| O4-02 | Densité routière | Km / surface × 1 000 | Collecte 2021-2022 | B | Golfe, Agoè-Nyivé, Lacs hors des bornes [SIG-19] |
| O4-03 | Km de routes pour 10 000 habitants | Km / population 2022 × 10 000 | 2022 | B | [SIG-30, SIG-32] |
| O4-04 | Nombre d’auto-écoles | Comptées (R-12) ; recensées en désagrégation | Collecte 2021-2022 | A | [SIG-22, SIG-23, SIG-43] |
| O4-05 | Auto-écoles pour 100 000 habitants | Comptées / population 2022 × 100 000 | 2022 | C | 23 préfectures ex aequo à 0 [SIG-24, SIG-26] |
| O4-06 | Habitants par auto-école | Population / comptées ; non défini sans auto-école comptée | 2022 | C | Non défini pour 23 préfectures [SIG-26] |
| O4-07 | Préfectures sans auto-école | ✅ Les 23 sans auto-école comptée (R-12, 04 §8), avec leur population ; la note donne les 15 sans aucune auto-école recensée, définition littérale du 02 | 2022 | B | [SIG-26] |
| O4-08 | Distance à l’auto-école la plus proche | Repli du 02 : distance du point de départ à l’auto-école comptée la plus proche, en UTM 31N. ✅ Avec SE-08 : la population des préfectures dont le point de départ est à plus de 10 km. Ce n’est pas la population à plus de 10 km, faute de grille de population (04 §8) | Collecte 2021-2022 | C | Oti-Sud hors des bornes [SIG-25] ; la distance distingue les 23 préfectures à zéro (06 §3, O4) |

**Résultat :**
- 132 auto-écoles comptées, sur 272 recensées.
- 23 préfectures n’ont aucune auto-école comptée : 2 932 492 habitants. 15 d’entre elles n’en ont aucune recensée : 1 822 046 habitants.
- 26 préfectures ont leur point de départ à plus de 10 km (SE-08) de l’auto-école comptée la plus proche : 3 482 856 habitants.

### O5 — Recommandations (2 indicateurs, préfecture)

O5-01 et O5-02 passent au 08 (écart 20).

| ID | Indicateur | Calcul au 07 | Période | Niveau | Justification (06) |
| -- | ---------- | ------------ | ------- | ------ | ------------------ |
| O5-03 | Population concernée | Population 2022 de chaque préfecture (A) ; pour la distance, celle de O4-08 (C) | 2022 | A | Le volume à côté du taux [SIG-29 à SIG-32] |
| O5-04 | Écart à la cible | Km à remettre en état : cible PA-04 (médiane de O3-02). Auto-écoles manquantes : deux valeurs côte à côte, la formule du 02 et la variante de l’écart 21 ; plus la nature du zéro (§6). L’écart de tués n’est pas calculable (O2-02 national) | 2022 | C | Médiane de O4-05 = 0 [SIG-26] ; médiane de O3-02 = 14,35 % (06 §3, O3) |

**Résultat :** les écarts positifs sont sommés sans compenser les écarts négatifs d’une préfecture à l’autre.

| Dimension | Cible | Préfectures à écart positif | Total |
| --------- | ----- | --------------------------- | ----- |
| Réseau | Médiane de O3-02 : 14,35 % | 19 | 327,9 km à remettre en état |
| Formation, formule du 02 | Médiane de O4-05 sur 39 préfectures : 0 | 0 | 0 auto-école |
| Formation, variante (écart 21) | Médiane de O4-05 sur les 16 préfectures avec au moins une auto-école comptée : 1,065 | 31 | 54 auto-écoles |

La formule du 02 ne donne aucun écart positif pour la formation : par la règle de l’écart 21, les recommandations (10) utiliseront la variante. Le réseau garde la formule du 02.

### Couverture des objectifs

Quelles données le 07 croise pour chaque objectif, et ce qui manque.

| Objectif | Données croisées | Indicateurs du 02 au 07 | Ce qui manque, et pourquoi |
| -------- | ---------------- | ----------------------- | -------------------------- |
| O1 | D1, D2, D7 ; correspondance véhicules ↔ permis ; PA-01 | 8 sur 9 | O1-08 : permis sans sexe ni âge (écart 5) |
| O2 | D3, D7, D1 (parc estimé), D9 | 7 sur 14, au national ; et 3 compléments (écart 22) : les 6 taux de l’énoncé, au national | Aucun accident par territoire (écart 1) ; ni mois, ni catégorie de véhicule, ni cause, ni âge (écart 2) : O2-07, O2-08, O2-10 à O2-14 |
| O3 | D4 × D5 ; référentiel des préfectures | 7 sur 7 | O3-07 au national, par catégorie de route, pas par zone (écart 18) |
| O4 | D5, D6, D7, D8, D13 | 8 sur 9 | O4-09 : aucune capacité de formation (écart 13) ; O4-08 mesuré depuis un point par préfecture (écart 19) |
| O5 | Tables du 05 ; O3-02, O4-05 | 2 sur 4 ; O5-01 et O5-02 au 08 (écart 20) | Pas de dimension risque par territoire : O2-02 est national (04 §8) |

**Résultat :** 35 indicateurs calculés, les 32 du 02 et les 3 compléments, en 2 624 lignes et 2 584 valeurs. Les 40 lignes sans valeur sont non renseignées (permis de 2013 ; « - » de l’annuaire) ou non définies (Mô ; O4-06 sans auto-école comptée ; R-10).

---

## 4. Niveaux de preuve

Ce sont ceux du 04 (§8), moins O5-01 et O5-02 (C), passés au 08.

| Niveau | Indicateurs | Nombre |
| ------ | ----------- | ------ |
| A | O1-01, O1-06, O2-01, O4-04, O5-03 | 5 |
| B | O1-02, O1-03, O1-09, O2-05, O2-06, O3-06, O4-01, O4-02, O4-03, O4-07 | 10 |
| C | O1-04, O1-05, O1-07, O2-02, O2-03, O2-04, O2-09, O3-01 à O3-05, O3-07, O4-05, O4-06, O4-08, O5-04 | 17 |
| **Total** | | **32** |

O1-04, O2-02 et O2-03 sont en B en 2010 et 2022, années de recensement, et en C les autres années. Ils sont comptés en C, comme au 04, et chaque valeur porte son propre niveau.

Les 3 compléments suivent la même règle : O2-E1 comme O2-02, O2-E2 et O2-E3 en C, comme O2-04. Ils ne sont pas comptés dans les 32.

---

## 5. Justification par le 06

La procédure le demande : « chaque indicateur porte sa justification, issue du 07 », c’est-à-dire de l’exploration, notre 06.

✅ **Règle :** la justification cite le signal du 06 qui la porte. Quand aucun signal ne s’y rapporte, elle cite le paragraphe de résultat du 06 (par exemple O2-05 : 06 §3, O2). Elle est écrite dans `catalogue_07.csv`, colonne « Justification (06) ».

✅ **Les 3 compléments** (écart 22) n’ont pas été explorés au 06, puisqu’ils sont hors 02. Leur justification le dit, puis cite les signaux de leur numérateur et de leur dénominateur.

Une justification décrit ce que l’exploration a montré ; elle ne fixe aucun seuil.

---

## 6. Écarts au 02

Déclarés avant le calcul (R-20). Les écarts 1 à 19 sont ceux du 04 (§7). Le 02 n’est pas modifié.

| N° | Écart | Indicateurs | Traitement | Raison |
| -- | ----- | ----------- | ---------- | ------ |
| 20 | ✅ Le 02 range O5-01 et O5-02 parmi les indicateurs (`01_Matrice`), mais ce sont un comptage de seuils franchis et un score | O5-01, O5-02 | Calculés au 08, avec les seuils de classement | La procédure interdit tout score avant l’étape 9 (06 §9). Le 08 reprendra cet écart |
| 21 | ✅ Cible de la formation : la médiane de O4-05 sur les 39 préfectures vaut 0 [SIG-26]. Avec elle, aucune préfecture ne manque d’auto-école | O5-04 | Deux valeurs côte à côte : la formule du 02, en référence, et une variante, même formule avec la médiane des seules préfectures qui ont au moins une auto-école comptée | PA-04 justifie la médiane par « la moitié des préfectures y sont déjà » : avec 23 zéros, la cible ne mesure plus rien |
| 22 | ✅ L’énoncé demande les accidents, les blessés et les morts rapportés à la population et au nombre de véhicules ; le 02 ne retient que 3 de ces 6 taux | O2-E1 à O2-E3 | Les 3 taux manquants, calculés au national avec les mêmes données et les mêmes règles (R-06, R-11) ; étiquetés « complément de l’énoncé, hors 02 » ; volume à côté du taux et niveau porté valeur par valeur, comme pour les 32 ; hors des 32 et hors du classement : ni O5-01, ni O5-02, ni profils P1 à P6 | Le 01 §3.2 l’écrit : « deux lectures du même risque, toutes deux exigées ». Mêmes données, aucune interprétation nouvelle. Taux non explorés au 06 (hors 02) |

**Écart 21 : règle fixée avant le calcul.** Pour une dimension où la formule du 02 ne donne aucun écart positif, les recommandations (10) utilisent la variante ; sinon, elles utilisent la formule du 02. La règle porte sur la capacité de la formule à distinguer les préfectures, jamais sur les préfectures qu’elle fait ressortir. Le réseau garde la formule du 02 : sa médiane, 14,35 %, distingue les préfectures.

**Écart 21 : nature du zéro.** Pour chaque préfecture sans auto-école comptée, O5-04 dit pourquoi :

| Nature du zéro | Préfectures | Ce que dit la donnée | Recommandation attendue (10) |
| -------------- | ----------- | -------------------- | ---------------------------- |
| Aucune auto-école recensée | 15 | Rien dans l’inventaire | Vérifier sur place qu’il n’en existe pas, puis ouvrir |
| Recensées, aucune agréée | 8 (13 établissements non agréés) | Une offre existe peut-être, sans agrément | Vérifier leur activité et leur agrément : le manque est peut-être administratif |

O4-05 est en C : la recommandation commence par une vérification, pas par un investissement (R-17). Le manque de données sur ces préfectures relève du profil P5 du 02 (« collecte et ouverture des données manquantes »).

---

## 7. Validation

| Contrôle | Attendu |
| -------- | ------- |
| Indicateurs calculés | 32 indicateurs du 02, et les 3 compléments ; ni O5-01 ni O5-02 ; aucun des 9 non calculables |
| Valeurs | Chaque indicateur a au moins une valeur ; chaque valeur a sa source, son année, son niveau |
| Niveaux | Le niveau de chaque indicateur est celui du 04 |
| Maille et période | Celles du 04 (`faisabilite_indicateurs.csv`) |
| Concordance avec le 06 | Même valeur que le 06 pour chaque rapport calculé des deux côtés (`rapports_06.csv`, `prefectures_06.csv`) |
| Compléments (écart 22) | Le 06 ne les a pas calculés : leurs termes se contrôlent à la place. Numérateur égal à celui de O2-01, dénominateur égal à celui de O2-02 ou de O2-04, la même année ; « hors 02 » sur chaque ligne |
| Totaux | Somme des préfectures = total national : km par état, km de routes classées, auto-écoles, population (R-04) |
| Valeurs manquantes | Aucun zéro là où le rapport est non défini (Mô ; O4-06 sans auto-école comptée) ; 2013 non renseignée pour les permis (R-10) |
| Écart 21 | Deux valeurs pour les auto-écoles manquantes, dans chaque préfecture ; une nature du zéro pour chacune des 23 préfectures sans auto-école comptée (15 + 8) |
| SE-01 (R-09) au national | Au moins 20 tués par an : le taux national se calcule sans cumul d’années |
| Justification | Chaque indicateur cite un signal ou un paragraphe du 06 ; chaque signal cité existe |

**Résultat : 11 contrôles conformes sur 11** (`controles_07.csv`).
- **Concordance avec le 06 :** 1 647 valeurs identiques. Le 07 lit les tables détaillées du 05 (tracé, états, auto-écoles, population), le 06 la table maîtresse : les deux chemins donnent les mêmes valeurs.
- **Totaux :** les km par état des préfectures égalent ceux des tronçons du relevé. Les km de routes classées font 3 361,35, contre 3 361,36 pour le tracé découpé par les limites des préfectures : l’écart vient des arrondis. Les auto-écoles (132 comptées, 272 recensées) et la population (8 095 498 habitants) égalent les totaux nationaux.
- **SE-01 :** de 470 à 802 tués par an.
- **Reproductibilité :** deux exécutions donnent des fichiers identiques à l’octet près ; `data/processed/` n’est pas modifié.

---

## 8. Fichiers produits

**Dans `data/analysis/07_indicateurs/`**, écrits par `indicateurs_07.py` :

| Fichier | Contenu |
| ------- | ------- |
| `indicateurs_07.csv` | Une ligne par indicateur × territoire × année × catégorie |
| `catalogue_07.csv` | Une ligne par indicateur : nom, définition, formule et sens de lecture lus dans le 02 (l’énoncé pour les compléments) ; calcul appliqué ; maille, période et niveau du 04 ; justification du 06 ; réserve ; périmètre (« 02 », ou « complément de l’énoncé, hors 02, hors classement ») ; nombre de lignes et de valeurs |
| `controles_07.csv` | Les contrôles du §7 : attendu, mesure, résultat |

**Colonnes de `indicateurs_07.csv` :**

| Colonne | Contenu |
| ------- | ------- |
| ID | O1-01, O2-02… ; O2-E1 à O2-E3 pour les compléments |
| Maille | National, zone, préfecture, tronçon |
| Territoire | Nom du référentiel |
| Année | 2022, ou une période (« 2007–2024 ») pour un cumul |
| Catégorie | La désagrégation : groupe, catégorie de permis, état, type de route, type d’usager, cible (02 ou écart 21) |
| Mesure | Ce qui est mesuré, quand un indicateur en a plusieurs : O1-03 (croissance annuelle, TCAM, multiplicateur), O3-05, O4-07, O4-08, O5-04 |
| Numérateur, Dénominateur | Les termes d’un rapport ; vides pour un comptage |
| Valeur | La valeur ; vide si non renseignée ou non définie |
| Borne basse, Borne haute | Pour une valeur en fourchette (O1-05, O2-04, O2-E2, O2-E3) |
| Unité | — |
| Niveau | A, B ou C, valeur par valeur |
| Source | Table du 05 |
| Note | Année atypique (signal du 06) ou rupture, non défini, non renseigné, nature du zéro, « hors 02 » |

---

## 9. Suite

- **08 — Priorisation** (étape 9) : seuils de classement (SE-02 à SE-07, SE-10), O5-01, O5-02, sensibilité du classement. Il tranche les terciles de SE-07, face aux 23 ex aequo, avant de voir le classement [SIG-26]. Il teste aussi le classement sans Golfe ni Agoè-Nyivé (`05_Priorisation`). Les 3 compléments n’entrent ni dans O5-01, ni dans O5-02, ni dans les profils P1 à P6 (écart 22).
- **Puis** : 09 Diagnostic (étape 10), 10 Recommandations (11), 11 Tableau de bord (12), 12 Validation (13), 13 Rapport final (14), comme au 06 §9.
- ✅ **Compléments au 11 et au 13.** Le tableau de bord et le rapport final les montrent dans une section « Compléments à l’énoncé », séparée des indicateurs du 02. Elle dit pourquoi ils ne sont pas dans le 02, et qu’ils restent disponibles si le comité de pilotage veut les y intégrer.

✅ **Les hypothèses du 02 se tranchent au 09.** Chacune est un croisement (`02_Hypotheses`), et le croisement est l’étape 10 de la procédure. Le 07 calcule les indicateurs qu’elles utilisent, sans les trancher.

**À prévoir au 08 et au 10 : les leviers sans la dimension risque.**
- **Ce que disent le 02 et le 03.** P1 (réseau) et P2 (formation) exigent un risque élevé : O2-02 ≥ SE-02 (`04_Profils`). Or O2-02 n’existe qu’au national (écart 1). Le 02 prévoit ce cas : « sans O2-02, seul P5 s’applique », et les recommandations s’organisent par levier (`05_Priorisation`, « Combinaison des profils » et « Unité de classement »). Le 03 l’a confirmé (§1).
- **« P5 en complément de P1 ou P2 » ne permet pas de déclencher P1 ou P2 sans le risque.** Ce complément vise un territoire où P1 ou P2 est établi, mais où la dimension réseau ou formation manque (par exemple O3-06 > SE-05). Il ne vise pas le risque.
- **Ce que le 08 tranche, avant de voir le classement :** quelles préfectures reçoivent le levier réseau (O3-02 ≥ SE-04) et le levier formation (O4-05 ≤ SE-07). Il ne les nomme ni P1 ni P2, car ces profils s’intitulent « risque élevé », que les données ne mesurent pas par préfecture. Le risque y reste « non déterminable » (P5).

**Transmis au 08 :**
- Les dimensions par préfecture : O3-02 (38 préfectures ; Mô non défini), O4-05 (23 ex aequo à 0 [SIG-26]), O4-03 et O3-06 (pour SE-05).
- Pour O5-04, la formation suit la variante de l’écart 21 ; le réseau suit la formule du 02.
- O4-08 : 26 préfectures au-delà de SE-08, une dimension possible pour P2 si H4 la désigne (`04_Profils`).
- Les 3 compléments restent hors du classement.

**Transmis au 09 :** les 6 taux de l’énoncé, pour comparer la lecture par habitant et la lecture par véhicule (01 §3.2).

---

## 10. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 07** : 32 indicateurs, un script, trois fichiers (valeurs, catalogue, contrôles) | Tout le document | Équipe, 2026-10-06 |
| ✅ **Ni figure ni notebook au 07** : le 06 montre, le tableau de bord restitue ; le contrôle de concordance avec le 06 vérifie les calculs | §2, §7 | Équipe, 2026-10-06 |
| ✅ **Niveaux** : ceux du 04, valeur par valeur | §4 | Équipe, 2026-10-06 |
| ✅ **Justification** : un signal du 06, ou le paragraphe de résultat du 06 | §5 | Équipe, 2026-10-06 |
| ✅ **Écart 20** : O5-01 et O5-02 au 08 | §6 | Équipe, 2026-10-06 |
| ✅ **Définitions appliquées** : O3-05 (tronçons ayant des km en mauvais état, triés par ces km) ; O3-07 (année moins année précédente) ; O4-07 (23 sans auto-école comptée, 15 sans aucune recensée en note) ; O4-08 et SE-08 (population des préfectures dont le point de départ est à plus de 10 km) | §3 | Équipe, 2026-10-06 |
| ✅ **Écart 21** : cible de la formation, formule du 02 et variante côte à côte, règle d’usage fixée avant le calcul, nature du zéro | §6 | Équipe, 2026-10-06 |
| ✅ **Couverture des objectifs** : données croisées et manques, objectif par objectif | §3 | Équipe, 2026-10-06 |
| ✅ **Hypothèses tranchées au 09** | §9 | Équipe, 2026-10-06 |
| ✅ **Écart 22** : les 3 taux de l’énoncé absents du 02, calculés comme compléments hors 02 ; hors classement (O5-01, O5-02, P1 à P6) ; justification « non exploré au 06 », puis signaux des termes ; termes contrôlés à la place de la concordance | §3, §5, §6, §7 | Équipe, 2026-10-06 |
| ✅ **Compléments au 11 et au 13** : section « Compléments à l’énoncé », séparée du 02 | §9 | Équipe, 2026-10-06 |
| ✅ **Choix de calcul** : colonne « Mesure » ; parc estimé sur la période commune du 04, 2009–2024 ; km sommés à 3 décimales, celles du 05 ; un tronçon critique compte dans chaque zone traversée ; écarts positifs de O5-04 sommés au national, sans compensation | §3, §8 | Équipe, 2026-10-06 |
| ✅ **Résultats** : 35 indicateurs, 11 contrôles conformes sur 11 | §3, §7, §9 | Équipe, 2026-10-06 |
| ✅ **Leviers sans la dimension risque** : ni P1 ni P2 sans O2-02 (02, 03 §1) ; le 08 attribue les leviers réseau et formation, risque « non déterminable » (P5) | §9 | Équipe, 2026-10-06 |
