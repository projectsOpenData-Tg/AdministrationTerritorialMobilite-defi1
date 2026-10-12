# 06 — Exploration

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-05 — **Statut :** **figé** le 2026-10-05
**Sources :** `01_problem_definition.md` (figé), `02_decision_matrix.xlsx` (v1.1, figé), `03_data_inventory.md` (v1.3, figé), `04_data_understanding.md` (v1.0, figé), `05_data_preparation.md` (v1.0, figé), tables de `data/processed/`

> **Question du 06 :** que disent les données préparées, avant de fixer les indicateurs ? Où sont les écarts ?
>
> Le 06 couvre l’étape 7 de la procédure, l’analyse exploratoire. Il cherche les écarts, pas les moyennes. Il ne fixe aucun indicateur : c’est l’objet du 07, qui citera, pour chaque indicateur, ce que le 06 a montré.
>
> Les colonnes « Résultat » sont remplies à partir des sorties du script (R-19). Le numéro entre crochets renvoie à la ligne de `signaux_06.csv`.
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §10.

---

## Point de départ : le 05

- **34 indicateurs sur 43 sont calculables** : 23 à la maille cible, 11 avec repli ; 9 ne le sont pas (04 §10). Le 05 n’en a changé aucun (05 §3.3).
- **Les tables sont validées** : 25 contrôles conformes, dont 3 bloquants (05 §7).
- **La table maîtresse** porte 22 colonnes pour les 39 préfectures (05 §5).
- **Le parc estimé** est calculé une seule fois, en C, avec ses bornes (05 §6).
- **Les accidents ne sont publiés qu’au niveau national** (écart 1). Les préfectures se comparent donc sur le réseau, la formation et la population, jamais sur le risque routier.
- **Le 05 transmet au 06** (05 §9) :
  - 23 préfectures sur 39 sans auto-école comptée, dont 15 sans aucune auto-école recensée ;
  - 99 km de routes nationales sans état, dans 13 préfectures.

---

## 1. Objectif de l’Exploration

Décrire ce que disent les tables du 05, avant de fixer les indicateurs. L’exploration sert à :
1. **voir les distributions** : ce qui est concentré, étalé, atypique ;
2. **repérer les écarts entre territoires**, par préfecture et par zone (R-02) ;
3. **confronter les sources** qui mesurent la même chose, quand le 04 ne l’a pas fait ;
4. **tester les cinq contradictions** de la procédure (§7) ;
5. **justifier les indicateurs** : chaque indicateur du 07 portera sa justification, issue du 06 (procédure, étape 8).

**Sorties :**
1. les chiffres de l’exploration, écrits par un script (§8) ;
2. un notebook exécuté par objectif, pour les figures ;
3. la liste des signaux transmis au 07 (`signaux_06.csv`).

**Règles :**
- `data/processed/` n’est jamais modifié : le 06 le lit.
- ✅ Le 06 calcule des rapports pour voir les écarts (par habitant, par km, parts), avec la formule du 02. Il n’applique aucun seuil du 02, ne classe pas et ne calcule aucun score (étape 9). Ces rapports sont écrits dans `rapports_06.csv` et `prefectures_06.csv`, mais ne sont ni publiés ni repris : le 07 recalcule chaque indicateur avec toutes les règles du 02, et le tableau de bord et le rapport ne lisent que le 07.
- Une valeur manquante reste « non renseignée » (R-10). Un rapport sans dénominateur est « non défini », jamais 0 : Mô n’a aucune route classée (05 §5).
- Un écart est décrit, pas expliqué. Une date de la chronologie posée à côté d’une série est une coïncidence, pas une cause (H1).
- Les règles qui font un signal (§4) sont fixées avant de lancer l’exploration (R-20).
- Chaque figure porte son titre, sa source, son année et son niveau de preuve.

**Le 06 est terminé quand :**
- chaque notebook est exécuté, et chaque chiffre du 06 est lu dans un CSV écrit par le script ;
- les règles du §4 ont été appliquées à chaque variable listée ;
- les cinq contradictions ont été testées : trouvée ou non, chacune a son résultat ;
- les signaux sont validés avant le 07.

---

## 2. Méthode et outils

**Outils.** Ceux du 04 et du 05, dans le même environnement `.venv` (`requirements.txt`) : pandas, geopandas, shapely, pyproj, matplotlib, Jupyter. Aucun nouveau paquet.

✅ **Script et notebooks.** Même partage qu’au 04 : le script calcule, les notebooks montrent.

| Fichier | Rôle | Sorties |
| ------- | ---- | ------- |
| `scripts/exploration_06.py` | Calcule chaque chiffre cité dans le 06 : distributions, rapports, voisinages, comparaisons de sources, contradictions ; applique les règles du §4 | Les 6 CSV de `data/analysis/06_exploration/` (§8) |
| `notebooks/06_O1.ipynb` à `06_O5.ipynb` | Les figures de chaque objectif, chacune avec un tableau à côté. Ils lisent les tables du 05 et les CSV du script ; aucun chiffre n’est tiré d’un notebook seul (R-19) | — |
| `notebooks/style_06.py` | Reprend les fonctions de `style_04.py` et prolonge sa palette à six couleurs, validées ; chemins du 06 | — |

**Mailles.** Préfecture (39) et zone (6, R-02 et R-03) ; région (5) par agrégation. O1 et O2 au national. Année de référence : 2022 (R-05).

**Pour tout reproduire :** la chaîne du 05, puis `exploration_06.py`, puis les notebooks.

**Résultat :** script relancé deux fois, 6 fichiers de sortie identiques octet pour octet ; 5 notebooks exécutés, 29 figures, aucune erreur. `data/processed/` n’a pas changé.

**Ordre de travail :**
1. O1 et O2 : séries nationales ;
2. O3 et O4 : préfectures et zones ;
3. O5 : croisements ;
4. les cinq contradictions (§7) ;
5. les signaux (§4).

---

## 3. Exploration par objectif

Chaque figure dit quel indicateur ou quelle hypothèse du 02 elle prépare (colonne « Prépare »). Chaque indicateur calculable de O1 à O4 a sa figure ; O5-02 et O5-04 se calculent à partir des autres et n’en ont pas au 06.

### O1 — Mobilité (national)

**Questions :**
- Immatriculations 1990–2024 par groupe (05 §4) : niveau, croissance, variations atypiques (§4) ; poids des motos dans le total.
- Permis 2007–2024 par catégorie (2013 non renseignée) : variations atypiques.
- Ruptures annotées au 05 (parc en 1995 et 2004, permis en 2016, 2019 et 2022) et dates de la chronologie (`chronologie_reformes.csv`), posées côte à côte, sans lecture causale.
- Immatriculations et permis de la même catégorie (correspondance du 05) : les deux séries vont-elles ensemble ?
- Parc estimé : largeur de la fourchette de PA-01, groupe par groupe.
- Population nationale : les raccords entre sources (série reconstituée jusqu’en 2009, recensements de 2010 et 2022, projections) se voient-ils ? Ils touchent chaque taux par habitant.

| Figure | Forme | Tables | Prépare |
| ------ | ----- | ------ | ------- |
| Immatriculations par groupe | Courbes, 5 groupes ; ruptures et chronologie annotées | `D1_immatriculations.csv` | O1-01, O1-03 ; S1 |
| Part de chaque groupe | Aires empilées à 100 % | `rapports_06.csv` (D1) | O1-02 ; S2 |
| Permis par catégorie | Courbes, 6 catégories ; 2013 laissée vide | `D2_permis.csv` | O1-06 |
| Immatriculations et permis, par catégorie | Un panneau par catégorie | `D1`, `D2`, `correspondance_vehicules_permis.csv` | O1-09 ; H1 |
| Parc estimé | Courbe avec la bande des bornes, par groupe | `D1_parc_estime.csv` | O1-05 |
| Immatriculations pour 1 000 habitants ; permis pour 1 000 habitants en âge de conduire | Deux panneaux, un axe chacun | `rapports_06.csv` (D1, D2, D7) | O1-04, O1-07 |
| Population nationale | Courbe ; la source de chaque année marquée | `D7_population_nationale.csv` | Dénominateur des taux par habitant (R-06) |

**Résultat :**
- **Immatriculations.** La part des motos passe de 22,2 % en 1990 à 74,4 % en 2024 (82,4 % en 2023). Leurs variations atypiques sont les deux ruptures du 05 : 1995 (+635,7 %) et 2004 (+180,1 %) [SIG-01]. Celle de 2023 (+59,4 %), année de la tournée d’immatriculation des motos, reste sous la borne de Tukey (+93,4 %). Les autres groupes ont leurs propres années atypiques, sans date de la chronologie [SIG-02 à SIG-04].
- **Permis.** Variations atypiques : A en 2022 (+2 192,4 %) et 2024 (+560,9 %) ; B, C et D en 2016 ; E en 2009, 2015 et 2016 ; F en 2016 et 2024 [SIG-05 à SIG-10]. 2016 et 2022 sont des années de la chronologie : coïncidence, pas une cause. La hausse de A en 2019 (+497,3 %) reste sous la borne (+520,4 %).
- **Immatriculations et permis.** En cumul sur 2007–2024, sans 2013 : 40,2 immatriculations de deux-roues pour un permis A ; 2,33 pour C ; 1,29 pour B ; 0,81 pour E ; 0,37 pour D (B). H1 n’est pas tranchée ici.
- **Taux par habitant.** 1,86 immatriculation pour 1 000 habitants en 1990, 11,58 en 2022, 15,86 en 2023. Permis A : 0,05 pour 1 000 habitants en âge de conduire en 2021, 1,15 en 2022, 2,15 en 2024.
- **Parc estimé.** La fourchette de PA-01 vaut 51,4 % de la valeur centrale pour l’ensemble en 2024 (36,5 % en 2009) ; 55,7 % pour les motos.
- **Population.** Variations atypiques en 1993–1996, dans la série reconstituée avec WPP, et en 2011 (+0,2 %), au raccord entre le recensement de 2010 et la projection de 2011 [SIG-11]. Le raccord de 2022 (+2,7 %) n’est pas atypique.

### O2 — Sécurité (national)

**Questions :**
- Accidents constatés, tués et blessés, 2010–2024 : variations atypiques, décrites sans cause.
- Tués et blessés pour 100 accidents : stables ou non ?
- Accidents constatés et tués pour 100 000 habitants, année par année : vont-ils dans le même sens ? Les années où la population est en C sont marquées (R-06).
- Tués pour 10 000 véhicules, dans la fourchette du parc estimé : va-t-il dans le même sens que le taux par habitant ?
- Tués déclarés face aux tués estimés par l’OMS en 2021 : repère SE-03, jamais une correction (04 §6).
- Part des tués par type d’usager en 2021 (OMS, C). La comparer à la part des motos dans le parc serait O2-08, non calculable (04 §8) : le 06 ne le fait pas.

| Figure | Forme | Tables | Prépare |
| ------ | ----- | ------ | ------- |
| Accidents, tués, blessés | Trois panneaux, un axe chacun | `D3_accidents.csv` | O2-01 ; S3, S4 |
| Tués et blessés pour 100 accidents | Deux panneaux | `rapports_06.csv` (D3) | O2-05, O2-06 |
| Accidents pour 100 000 habitants ; tués pour 100 000 habitants ; tués pour 10 000 véhicules | Trois panneaux, un axe chacun, jamais deux axes ; bande des bornes du parc | `rapports_06.csv` (D3, D7, D1_parc_estime) | O2-02, O2-03, O2-04 ; H6 |
| Repères de l’OMS, 2021 | Barres : tués déclarés et estimés, avec la fourchette ; taux estimés du Togo et de trois voisins | `D3`, `D9_repere_oms.csv` | SE-03 |
| Tués par type d’usager, 2021 | Barres | `D3_victimes_usager_2021.csv` | O2-09 ; H2 |

**Résultat :**
- **Séries.** Variations atypiques : accidents en 2011 (+154,4 %), 2013 (−33,8 %), 2015 (−47,1 %) et 2016 (+89,2 %) ; tués en 2011 (+57,2 %) et 2015 (−41,0 %) ; blessés en 2016 (+76,9 %) [SIG-12 à SIG-14]. Aucune après 2016 : 2020 n’est pas atypique.
- **Gravité.** De 7,9 tués pour 100 accidents (2023) à 16,6 (2015) ; de 103,2 blessés pour 100 accidents (2014) à 201,3 (2010).
- **Taux.** Tués pour 100 000 habitants : de 6,62 (2023) à 12,03 (2014) ; 8,44 en 2022. Tués pour 10 000 véhicules : 16,80 en 2011 [14,11 – 22,73], 7,95 en 2024 [6,18 – 10,30]. Les deux taux sont au plus haut de 2011 à 2014. H6 n’est pas tranchée ici.
- **Repères de l’OMS.** 680 tués déclarés en 2021, 1 961 estimés (de 1 644 à 2 277). Taux estimé : 22,7 pour 100 000 habitants au Togo, de 24,8 à 27,8 chez les trois voisins ; taux déclaré : 8,62. Un repère, jamais une correction.
- **Usagers.** En 2021, 60 % des tués déclarés sont des usagers de deux et trois-roues motorisés, 23 % des piétons, 11 % des usagers de véhicules à 4 roues (OMS, C).

### O3 — Réseau (préfecture)

L’état ne couvre que les routes nationales, revêtues et non revêtues, relevées en 2020 (C). Les pistes rurales et les voiries urbaines n’ont pas d’état.

**Questions :**
- Part des km évalués en mauvais état, et en travaux, par préfecture et par zone : distribution, valeurs atypiques.
- Les 99 km non évalués : quelle part du réseau national de chaque préfecture ?
- Km par type de route nationale et par état, par zone.
- Tronçons en mauvais état : longueur, préfectures traversées.
- L’état national de 2020, vu par les 84 tronçons et par l’annuaire 39.2 (§5).

| Figure | Forme | Tables | Prépare |
| ------ | ----- | ------ | ------- |
| Part en mauvais état | Choroplèthe, 39 préfectures | `prefectures_06.csv`, `geo/prefectures.geojson` | O3-02 ; S5 |
| Parts par état | Boîtes à moustaches avec les 39 points, un état par boîte | `prefectures_06.csv` | O3-01, O3-03 |
| Part non évaluée | Choroplèthe | `prefectures_06.csv` | O3-06 |
| Km par type et par état | Barres empilées, 6 zones | `D4_D5_etat_trace.csv` | O3-04 |
| Tronçons | Carte des tronçons, colorés par leur part en mauvais état | `rapports_06.csv` (D4), `geo/routes_classees.geojson` | O3-05 ; H5 |
| État national, 2020–2022 | Barres groupées par année et par catégorie de route | `D4_etat_national_pct.csv` | O3-07 |

**Résultat :**
- **Mauvais état.** Médiane : 14,35 % des km évalués (Q1 4,75 ; Q3 25,325), sur 38 préfectures ; Mô, sans route classée, est non défini. Hors des bornes de Tukey : Danyi (100,0 %), Blitta (68,2 %) et Kloto (65,0 %) [SIG-20]. Par zone, de 7,7 % (Grand Lomé) à 40,3 % (Centrale).
- **Travaux.** Médiane : 21,85 % ; 10 préfectures sans km en travaux.
- **Non évalué.** 25 préfectures sur 38 n’ont aucun km non évalué. Sept sont hors des bornes, d’Agoè-Nyivé (20,0 %) à Kloto (5,4 %) [SIG-21] ; le Grand Lomé est à 14,6 %.
- **Deux publications de 2020.** Le relevé des 84 tronçons et l’annuaire 39.2 ne donnent aucune part identique : 11 sur 11 diffèrent. L’écart maximal est de −25,14 points (routes non revêtues en état moyen : 31,47 % au relevé, 56,61 % dans l’annuaire). Sur l’ensemble du réseau national, le mauvais état fait 21,16 % au relevé et 29,75 % dans l’annuaire [SIG-27].

### O4 — Couverture : routes et auto-écoles (préfecture)

**Questions :**
- Km de routes classées par type, rapportés à la surface et à la population : distribution, valeurs atypiques.
- Auto-écoles recensées et comptées (R-12) : concentration. Part des auto-écoles et part de la population, zone par zone.
- Auto-écoles comptées pour 100 000 habitants : 23 préfectures sont à zéro. Que devient une coupure en terciles (SE-07, appliquée au 08) quand plus d’un tiers des valeurs sont égales ?
- Distance de chaque point de départ (D13) à l’auto-école comptée la plus proche, en UTM 31N (repli de O4-08, C) : que montre-t-elle que le nombre ne montre pas ?
- Les préfectures qui ont peu de routes ont-elles aussi peu d’auto-écoles ?

| Figure | Forme | Tables | Prépare |
| ------ | ----- | ------ | ------- |
| Km de routes classées, par type | Barres empilées, 39 préfectures groupées par zone | `prefectures_06.csv` (D5) | O4-01 |
| Auto-écoles pour 100 000 habitants | Choroplèthe, avec les points (comptées ou non) ; les préfectures à zéro marquées. Le tableau à côté donne aussi les habitants par auto-école, sa lecture inverse, non définie sans auto-école | `prefectures_06.csv`, `geo/auto_ecoles.geojson` | O4-04 à O4-07 ; H8 |
| Part des auto-écoles et part de la population | Barres côte à côte, 6 zones | `rapports_06.csv` (D6, D7) | H8 |
| Km de routes pour 10 000 habitants | Choroplèthe | `prefectures_06.csv` | O4-03 |
| Densité routière | Choroplèthe | `prefectures_06.csv` | O4-02 |
| Distance à l’auto-école comptée la plus proche | Carte des points de départ ; histogramme des 39 distances | `prefectures_06.csv` (D13, D6) | O4-08 |
| Routes et auto-écoles | Nuage, 39 points, taille selon la population, couleur selon la classe de PA-03 | `prefectures_06.csv` | O4-03, O4-05 |

**Résultat :**
- **Routes.** Médiane : 84,0 km de routes classées par préfecture, aucune valeur atypique ; Mô n’en a aucune. Seules 4 préfectures ont des pistes rurales [SIG-17]. Densité : Golfe (401,9 km pour 1 000 km²), Agoè-Nyivé (390,5) et Lacs (213,3) sont hors des bornes [SIG-19]. Km pour 10 000 habitants : médiane 5,39, aucune valeur atypique.
- **Auto-écoles.** Médiane : 0 auto-école comptée pour 100 000 habitants ; Q3 : 0,83. Hors des bornes : Golfe (5,67), Agoè-Nyivé (3,29) et Kozah (2,11), trois des quatre préfectures urbaines (PA-03) [SIG-24]. 23 préfectures sur 39 sont ex aequo à 0 : le tercile inférieur de SE-07 ne peut pas les séparer [SIG-26].
- **Concentration (H8).** Le Grand Lomé a 27,0 % de la population et 78,0 % des auto-écoles comptées. Chacune des cinq autres zones a de 3,0 % à 6,8 % des auto-écoles comptées, pour 9,8 % à 20,2 % de la population.
- **Distance.** Médiane : 24,7 km du point de départ à l’auto-école comptée la plus proche (Q1 2,2 ; Q3 31,25). Oti-Sud, à 84,0 km, est hors des bornes [SIG-25]. Pour les 23 préfectures sans auto-école comptée, la plus proche est à 11,0 km (Agou) jusqu’à 84,0 km (Oti-Sud) : la distance distingue ces préfectures, que le nombre laisse toutes à zéro.
- **Peu de routes, peu d’auto-écoles.** Akébou, Dankpen, Mô et Tandjoaré sont dans le quart bas des deux (450 807 habitants) [SIG-30].

### O5 — Croisements (préfecture)

**Questions, sans classer :**
- Réseau (part en mauvais état, km pour 10 000 habitants) face à la formation (auto-écoles pour 100 000 habitants) : quelles préfectures sont en bas des deux ?
- Ces préfectures sont-elles peuplées ? L’intensité n’est pas le volume (procédure, étape 9).
- Où sont le Grand Lomé et les préfectures rurales (PA-03) dans ce croisement ?

| Figure | Forme | Tables | Prépare |
| ------ | ----- | ------ | ------- |
| Réseau et formation | Nuages, un panneau par zone, taille selon la population ; repères des quartiles (§4) | `prefectures_06.csv` | O5-01, O5-03 ; H9 |
| Urbaines et rurales | Même nuage, couleur selon la classe de PA-03 | `prefectures_06.csv` | PA-03 |
| Voisines très différentes | Quatre cartes, un trait par paire (§7, contradiction 3) | `voisines_06.csv` | O3-02, O3-06, O4-03, O4-05 |

**Ne se fait pas au 06 :** aucun rang, aucun score, aucun seuil du 02. La matrice territoires × dimensions est la figure de O5-01 : elle vient au 08, avec les seuils du 02 (§9).

**Résultat :**
- **En bas des deux.** Agou, Bassar, Blitta, Danyi et Tchamba ont un réseau dégradé (part en mauvais état dans le quart haut) et une formation basse (quart bas) : 641 955 habitants [SIG-29]. Aucune n’a une population haute (Q3 : 212 498 habitants).
- **Grand Lomé et PA-03.** Les quatre préfectures urbaines (Golfe, Agoè-Nyivé, Kloto, Kozah) ont toutes au moins une auto-école comptée ; les 23 préfectures à zéro sont rurales. Golfe et Agoè-Nyivé sont hors des bornes sur la formation [SIG-24] et sur la part non évaluée [SIG-21] ; Agoè-Nyivé a aussi une part en mauvais état haute, sur peu de km évalués [SIG-42].

---

## 4. Distributions et valeurs atypiques

✅ **Règles, fixées avant l’exploration (R-20).** Elles décrivent ; elles ne classent pas. Ce ne sont pas des seuils du 02.

Par construction, environ un quart des préfectures est « haut » et un quart « bas » : c’est large, et voulu pour repérer. Un signal « haut » n’est pas une priorité : la priorisation vient au 08 (étape 9).

| Règle | Définition |
| ----- | ---------- |
| Valeur atypique entre préfectures | Hors de [Q1 − 1,5 × EI ; Q3 + 1,5 × EI] sur les 39 préfectures (règle de Tukey ; EI : écart interquartile) |
| Variation atypique dans une série | La même règle, sur les variations annuelles de la série |
| Haut, bas | Dans le quart supérieur (≥ Q3) ou inférieur (≤ Q1) des 39 préfectures ; les ex aequo sont tous retenus. Aux 6 zones : au-dessus ou au-dessous de la médiane, comme au 02 |
| Voisines | Préfectures dont les polygones ont une frontière commune ; un simple point de contact ne compte pas |

**Variables passées aux règles :**
- séries nationales : immatriculations par groupe, permis par catégorie, accidents, tués, blessés, population ;
- préfectures : population 2022 ; km de routes par type, pour 10 000 habitants et pour 1 000 km² ; parts en mauvais état, en travaux et non évaluée ; auto-écoles recensées, comptées et pour 100 000 habitants ; distance à l’auto-école comptée la plus proche.

**Sortie : `signaux_06.csv`**, une ligne par signal :

| Colonne | Contenu |
| ------- | ------- |
| ID | `SIG-<n°>` |
| Résumé | Une phrase, lisible sans ouvrir les figures |
| Objectif | O1 à O5 |
| Table et colonne | Le fichier du 06 et la colonne lus |
| Territoire ou période | — |
| Ampleur | Les valeurs en cause, ou le nombre de préfectures, de paires ou de zones |
| Règle | Règle du §4, ou contradiction du §7 (1 à 5) |
| Niveau | Un comptage garde son niveau ; un rapport est en B, ou en C si l’un de ses termes l’est (R-17) |
| Question transmise | Au 07 ou au 08 |
| Indicateurs et hypothèses | IDs du 02 |

**Résultat :** 44 signaux : 14 variations atypiques, 11 variables à valeurs atypiques, 1 cas d’ex aequo, 2 comparaisons de sources, 2 croisements et 14 lignes de contradiction.

---

## 5. Comparaisons entre sources

**Déjà faites au 04, non refaites :**
- population 2022, Livret 02 et recensement CSV [4.5-02] ;
- permis 2020–2022, portail et annuaire [4.4-09] ;
- parc publié : un flux, face aux 93 944 véhicules de l’OMS [4.4-01 à 4.4-04] ;
- longueur des routes classées, face à la densité et à l’état publiés [4.4-11] ;
- motos des ménages (EHCVM) face aux deux-roues immatriculés [4.4-10] ;
- trois séries d’accidents du portail et l’annuaire : identiques sur leurs années communes [4.4-05], et la série de référence identique à ses sources [05, 7-05] ;
- tués déclarés face à l’estimation de l’OMS (04 §6).

Le 06 les cite ; il ne les recalcule pas. Une figure de séries identiques ne montrerait que des courbes superposées.

**Nouvelles au 06 :**

| Comparaison | Tables | Ce qu’on vérifie | Résultat |
| ----------- | ------ | ---------------- | -------- |
| État national de 2020 : les 84 tronçons agrégés, face à l’annuaire 39.2 | `D4_etat_troncons.csv`, `D4_etat_national_pct.csv` | Les deux publications de 2020 donnent-elles les mêmes parts par état ? L’une porte O3-01 à O3-06, l’autre O3-07 | Non : 11 parts sur 11 diffèrent ; écart maximal de −25,14 points (routes non revêtues, état moyen) [SIG-27] |
| Ménages possédant une moto : DHS 2017, puis EHCVM 2021-2022, par zone | `D12_dhs_region.csv`, `D12_menages_zone.csv` | L’ordre des zones tient-il d’une enquête à l’autre ? « Lomé » dans la DHS et Grand Lomé dans l’EHCVM : périmètres à comparer (4.3-03) | Non : le Grand Lomé passe de la 1re part (42,3 %) à la 4e (33,3 %), la Kara de la 5e à la 1re (38,4 %, à égalité avec les Savanes). Toutes les parts baissent, sauf la Kara (+3,8 points). Deux dates et deux périmètres : pas une tendance [SIG-28] |

Un écart entre deux sources devient un signal (§4).

---

## 6. Cartes exploratoires

Les cartes sont listées au §3, objectif par objectif. Elles suivent toutes ces règles :
- les calculs se font en UTM 31N (R-16) ; l’affichage, en WGS 84, à partir de `data/processed/geo/` ;
- chaque carte porte son titre, sa source, son année et son niveau de preuve, et une légende ;
- une valeur manquante ou non définie est en gris, jamais confondue avec un zéro (R-10). Un zéro mesuré a sa propre marque : préfecture sans auto-école comptée, Mô sans route classée ;
- les classes de couleur sont les quartiles des 39 préfectures (§4), jamais les terciles du 02 : ce sont des seuils, appliqués au 08 (§9). Les tronçons ont une couleur continue, sans classe ;
- une carte ou un nuage porte au plus trois couleurs ; au-delà, un panneau par catégorie ;
- le Grand Lomé est séparé de la Maritime (R-03), et un encart l’agrandit ;
- les équipements de sécurité, hors 02, ne sont pas cartographiés.

---

## 7. Les cinq contradictions de la procédure

✅ La procédure (étape 7) demande de tester cinq contradictions. Le 06 les teste par préfecture, avec les règles du §4, sauf mention contraire. La deuxième est éclatée en trois : réseau, formation, usage.

| N° | Contradiction | Test au 06 | Tables | Résultat |
| -- | ------------- | ---------- | ------ | -------- |
| 1 | Population forte, offre faible | Population 2022 haute ; auto-écoles comptées pour 100 000 habitants basses, ou km de routes pour 10 000 habitants bas | `prefectures_06.csv` | Formation : Haho (305 096 habitants) [SIG-31]. Réseau : Agoè-Nyivé, Golfe, Tône, Vo et Zio (3 301 594 habitants) [SIG-32] |
| 2a | Réseau correct, état mauvais | Km de routes pour 10 000 habitants hors du bas ; part en mauvais état haute | `prefectures_06.csv` | 9 préfectures : Agou, Bassar, Blitta, Danyi, Kloto, Ogou, Tchamba, Tchaoudjo, Wawa (1 383 068 habitants) [SIG-33] |
| 2b | Formation présente, couverture faible | Au moins une auto-école comptée ; distance du point de départ à l’auto-école comptée la plus proche haute | `prefectures_06.csv` (D6, D13) | Non trouvée [SIG-34] |
| 2c | Usage fort, formation faible | Aux 6 zones : part des ménages qui possèdent une moto au-dessus de la médiane ; auto-écoles comptées pour 100 000 habitants au-dessous | `rapports_06.csv` (D12, D6, D7) | Centrale et Savanes [SIG-35] |
| 3 | Voisines très différentes | Paires de voisines, l’une haute, l’autre basse, sur : km pour 10 000 habitants, auto-écoles pour 100 000 habitants, part en mauvais état, part non évaluée | `voisines_06.csv` | Sur 78 paires : 13 (km), 25 (auto-écoles), 9 (mauvais état), 27 (non évalué) [SIG-36 à SIG-39]. Pour les auto-écoles et le non évalué, le quart bas réunit tous les zéros (23 et 25 préfectures), d’où beaucoup de paires |
| 4 | Taux élevé, volume faible, et l’inverse | Auto-écoles : taux haut sur un nombre bas, et taux bas sur une population haute. Réseau : part en mauvais état haute sur peu de km évalués | `prefectures_06.csv` | Taux haut sur nombre bas : non trouvée, le quart bas du nombre est 0 [SIG-40]. Taux bas sur population haute : Haho [SIG-41]. Réseau : Agoè-Nyivé [SIG-42] |
| 5 | Service unique : s’il tombe ? | Par préfecture : une seule auto-école comptée, et la population qui en dépend. Préfectures traversées par un seul tronçon du relevé ; Mô, sans route classée, est notée à part | `prefectures_06.csv` (D6, D4) | Anié, Assoli, Cinkassé, Kpélé et Zio n’ont qu’une auto-école comptée (956 482 habitants) [SIG-43]. Tandjoaré n’est traversée que par un tronçon [SIG-44] |

**Non testable :** toute contradiction qui met en jeu le risque routier par territoire. Les accidents ne sont publiés qu’au niveau national (écart 1), et O2-02 est en repli national (04 §8) : H3, H4, H7 et H11 n’ont pas de test par territoire.

Chaque contradiction a sa ligne dans `signaux_06.csv`, trouvée ou non.

---

## 8. Fichiers produits

**Dans `data/analysis/06_exploration/`**, écrits par `exploration_06.py` :

| Fichier | Contenu |
| ------- | ------- |
| `prefectures_06.csv` | Une ligne par préfecture : les variables du §4, la classe de PA-03, la distance et le nombre de tronçons du relevé |
| `distributions_06.csv` | Pour chaque variable du §4 : effectif, valeurs manquantes, minimum, Q1, médiane, Q3, maximum, valeurs atypiques |
| `rapports_06.csv` | Les rapports d’exploration, au national, par zone et par tronçon, avec la formule du 02 ; jamais publiés (§1) |
| `voisines_06.csv` | Les paires de préfectures voisines et leur écart, pour chaque variable de la contradiction 3 |
| `comparaisons_06.csv` | Les deux comparaisons nouvelles du §5 |
| `signaux_06.csv` | Les 44 signaux, dont une ligne par contradiction (§4, §7) |

**Dans `notebooks/` :** `06_O1.ipynb` à `06_O5.ipynb`, exécutés, et `style_06.py`.

Rien n’est écrit dans `data/processed/`.

---

## 9. Suite

Le 06 couvre l’étape 7. La suite garde un document par étape de la procédure.

✅ **Validé :**
- **07 — Indicateurs** (étape 8) : 32 des 34 indicateurs calculables, depuis les tables du 05, avec leur niveau de preuve. Chacun cite le signal du 06 qui le justifie.
- **Puis**, une étape par document : 08 Priorisation (étape 9), 09 Diagnostic (10), 10 Recommandations (11), 11 Tableau de bord (12), 12 Validation (13), 13 Rapport final (14).
- **Le 11 décrit un livrable**, pas une analyse : le tableau de bord restitue, il ne découvre rien (procédure, étape 12).

✅ **Rang de priorité et seuils au 08.** Le rang de priorité (O5-02) est un score, et la procédure interdit tout score avant l’étape 9. Le 08 le calcule, et applique les seuils de classement du 02 : SE-02 à SE-07 et SE-10.

✅ **Conséquences :**
- le nombre de déficits (O5-01) compte les seuils franchis : il vient aussi au 08. Le 07 calcule donc 32 indicateurs ;
- SE-01 et SE-08 restent au 07 : ils entrent dans les formules de O2-02 (R-09) et de O4-08 ;
- SE-09 ne s’applique pas : O2-08 n’est pas calculable (04 §8).

**Transmis au 07 :**
- **Écart à déclarer au 07 et au 08.** Le 02, figé (R-20), range O5-01 et O5-02 parmi les indicateurs (`01_Matrice`) et décrit le classement dans `05_Priorisation`. Le 02 n’est pas modifié : le 07 et le 08 écrivent chacun ce décalage et sa raison (ci-dessus).
- **Signaux.** 44 lignes dans `signaux_06.csv`. Les plus utiles à la suite :
  - **SE-07 en terciles.** 23 préfectures sur 39 sont ex aequo à 0 ; le tercile inférieur ne les sépare pas. À trancher au 08, avant de voir le classement (R-20) [SIG-26].
  - **Deux sources pour l’état de 2020.** Le relevé (O3-01 à O3-06) et l’annuaire 39.2 (O3-07) diffèrent sur chaque part. Le 07 dit laquelle porte quoi, sans les mélanger [SIG-27].
  - **Années atypiques** des séries nationales, à annoter au 07 sans lecture causale [SIG-01 à SIG-14] ; raccord de population de 2011, qui touche les taux par habitant [SIG-11].
  - **Points extrêmes.** Golfe et Agoè-Nyivé sont hors des bornes sur la population, la densité et les auto-écoles [SIG-15, SIG-19, SIG-22 à SIG-24]. Le 08 teste le classement sans eux (`05_Priorisation`).
  - **Le volume à côté du taux.** Haho, peuplée, sans auto-école comptée [SIG-31, SIG-41] ; 5 préfectures à une seule auto-école comptée [SIG-43].

---

## 10. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 06** : un script calcule, un notebook par objectif montre ; ni note de synthèse ni dossier de figures à part | §1, §2, §8 | Équipe, 2026-10-05 |
| ✅ **Rapports d’exploration** : formule du 02, sans seuil ni rang ; écrits dans `rapports_06.csv` et `prefectures_06.csv`, jamais publiés ; le 07 recalcule les indicateurs | §1 | Équipe, 2026-10-05 |
| ✅ **Règles des signaux** : règle de Tukey, quartiles, voisines par frontière commune ; fixées avant l’exploration ; « haut » n’est pas une priorité | §4 | Équipe, 2026-10-05 |
| ✅ **Cinq contradictions** : celles de la procédure, adaptées aux données ; la deuxième éclatée en 2a, 2b, 2c ; le risque par territoire n’est pas testable | §7 | Équipe, 2026-10-05 |
| ✅ **Comparaisons de sources** : celles du 04 citées, séries d’accidents comprises ; deux nouvelles | §5 | Équipe, 2026-10-05 |
| ✅ **Figures ajoutées** : O1-04 et O1-07, O2-03, O4-01 ; O4-06 lu dans le tableau de O4-05 ; colonne « Résumé » dans `signaux_06.csv` | §3, §4 | Équipe, 2026-10-05 |
| ✅ **Suite** : 07 Indicateurs, puis un document par étape ; le 11 est un livrable | §9 | Équipe, 2026-10-05 |
| ✅ **Rang de priorité (O5-02) au 08**, avec les seuils de classement (SE-02 à SE-07, SE-10) : c’est un score (procédure, étape 9). Le 02 n’est pas modifié ; l’écart sera déclaré au 07 et au 08 | §9 | Équipe, 2026-10-05 |
| ✅ **Conséquences** : O5-01 au 08 avec les seuils, le 07 calcule 32 indicateurs ; SE-01 et SE-08 restent au 07, dans les formules de O2-02 et O4-08 | §9 | Équipe, 2026-10-05 |
| ✅ **Implémentation**, écarts au plan : `prefectures_06.csv` ajouté ; contradiction 5 (réseau) lue sur les tronçons du relevé, plus robuste que les numéros de route ; chaque contradiction a sa ligne, trouvée ou non ; croisement de O5 et population ajoutés aux règles du §4 | §2, §4, §7, §8 | Équipe, 2026-10-05 |
| ✅ **Signaux du 06** : 44, dont ceux transmis au 07 et au 08 | §4, §9 | Équipe, 2026-10-05 |
