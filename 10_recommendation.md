# 10 — Recommandations

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-07 — **Statut :** **figé** le 2026-10-07
**Sources :** `01` à `09` (figés), `data/analysis/07_indicateurs/`, `data/analysis/08_priorisation/`, `data/analysis/09_diagnostic/`, `methodology/MAQUETTE_dashboard.md`

> **Question du 10 :** que faire, où, pour combien d’habitants, et dans quel ordre ?
>
> Le 10 couvre l’étape 11 de la procédure : la chaîne fait → écart → impact → action → priorité, reliée au diagnostic du 09. Chaque recommandation suit le format du 01 (§3.5) : constat → ampleur → territoire → déficit associé → action, avec acteur, cible chiffrée, population concernée, horizon, indicateur de suivi, niveau de preuve et réserve (R-18).
>
> Le 10 est le dernier document analytique. Le 11 (tableau de bord) le restitue, le 12 le valide, le 13 en fait le rapport final.
>
> Chaque chiffre cité vient de `data/analysis/10_recommandations/`, écrit par `recommandations_10.py` (R-19), qui lit `classement_08.csv`, `regions_08.csv`, `hypotheses_09.csv`, `indicateurs_07.csv`, `D4_etat_troncons.csv` et les couches géographiques.
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §12.

---

## Point de départ : le 09, le 08 et le 07

**Ce que le 09 transmet** (09 §10) :

- **Les verdicts** : S1, S2, S3, S5, H1, H2, H8 confirmées ; S4 nuancée ; H5, H6 infirmées ; H3, H4, H7, H9, H10, H11, H12 non testables.
- **La conséquence que le 02 attache à chaque verdict.** Celles qui fondent une recommandation : H1 (le levier formation cible d’abord le permis moto), H2 (mesures ciblées sur les motos, en C, surreprésentation faible écrite comme telle), H8 (ouverture d’auto-écoles hors des villes), S5 (entretien ciblé par territoire, pas seulement par tronçon). Celles qui en interdisent : H5 (le corridor de la RN1 n’est pas une cible commune), H6 (pas de lecture « le risque vient de l’exposition »), les 7 non testables.
- **Le message des 6 taux** : tous en baisse. « Plus de véhicules, pas une route plus dangereuse » (S4).
- **Les phrases de diagnostic** : 10 préfectures, Mô, 6 zones, la région Maritime.

**Ce que le 08 transmet** (08 §11) :

- **13 préfectures au levier réseau** : 2 868 523 habitants, 304,6 km à remettre en état.
- **23 préfectures au levier formation**, dont Mô : 2 932 492 habitants, 41 auto-écoles manquantes.
- **5 préfectures qui cumulent** les deux : Danyi, Blitta, Agou, Tchamba, Bassar (641 955 habitants).
- **La Centrale**, seule zone qui franchit les seuils du réseau et de la formation.
- **Les zones peu desservies** au sens du 02 (SE-06 : sous la médiane des 6 zones) : Grand Lomé, Maritime hors Grand Lomé, Savanes.
- **Le niveau** : classement en C, vérification avant investissement (R-17).

**Ce que le 07 transmet** (07 §9) : les leviers sans la dimension risque. P1 et P2 exigent O2-02, qui n’est que national (écart 1). Le 02 prévoit ce cas : les recommandations s’organisent par levier (`05_Priorisation`, « Unité de classement »). Ce n’est donc pas un écart : le 08 l’a déjà appliqué, le 10 en hérite. Pour O5-04 : la formation suit la variante de l’écart 21, le réseau la formule du 02.

**Ce que le 03 et le 04 transmettent** : les recommandations « données » (03 §8 ✅, complétées au 04 §10), et leur place dans le tableau de bord : une rubrique « Pour aller plus loin », après les recommandations territoriales.

---

## 1. Objectif du 10

Produire des recommandations chiffrées, localisées et priorisées, prêtes pour la page « Recommandations » du tableau de bord.

**Ce que le 10 apporte à chaque objectif du projet :**

| Objectif | Ce que le 10 en fait |
| -------- | -------------------- |
| O1 Mobilité | Permis moto (H1 confirmée) : REC-F3. Pas de recommandation territoriale sur les immatriculations : elles sont nationales et comptées au lieu d’enregistrement (08 §1). Publication d’un parc en circulation : REC-D4 |
| O2 Sécurité | Pas de recommandation territoriale sur le risque (écart 1). Usagers de deux-roues motorisés (H2 confirmée sur les tués, faible, C) : REC-S1. Base d’accidents par préfecture (P5) : REC-D1 |
| O3 Réseau | Entretien par préfecture (13 préfectures, 304,6 km) : REC-R1, REC-R2. Par tronçon (10 premiers des 49 tronçons critiques) : REC-R3. Aucune cible commune sur le corridor de la RN1 (H5 infirmée) |
| O4 Couverture | Ouverture d’auto-écoles hors des villes (H8 confirmée) : 23 préfectures, 41 auto-écoles, REC-F1 et REC-F2. La desserte (SE-06) ne déclenche aucun profil, sauf le cas unique de Mô : REC-R4 |
| O5 Recommandations | 15 recommandations, par levier et par priorité. Les « régions les moins bien desservies » de l’énoncé deviennent une cible, par dimension : la Centrale, qui cumule (REC-Z3), la route (REC-Z1), la formation (REC-Z2) (§4.6). Une fiche par préfecture : onglet « Actions par zone » (§4.7) |

**Sorties**, dans `data/analysis/10_recommandations/` :

1. `recommandations_10.csv` : une ligne par recommandation, avec les colonnes du §3 ;
2. `prefectures_10.csv` : une ligne par préfecture (39) : valeurs, leviers, recommandations qui la visent, priorité, texte d’action. Il sert au filtre par zone, au §4.5 et à l’onglet « Actions par zone » ;
3. `zones_10.csv` : une ligne par zone, avec la médiane des zones et le pays : les deux analyses et la conclusion du §4.6, pour que le tableau de bord les affiche sans rien agréger ;
4. `cartes_10.csv` : une ligne par carte de recommandation (§6) ;
5. `controles_10.csv` : les contrôles du §9.

**Règles :**

- Les sorties du 06, 07, 08 et 09 ne sont jamais modifiées.
- Chaque recommandation porte les champs de R-18.
- Une recommandation portée par un indicateur C commence par une vérification, pas par un investissement (R-17). Elle est dite « conditionnelle ».
- Les hypothèses non testables, et les 3 compléments O2-E1 à O2-E3 (écart 22), ne fondent aucune recommandation.
- Aucune lecture causale.
- Les habitants ne s’additionnent jamais d’une recommandation à l’autre : les territoires se recoupent (MAQUETTE §8.11).
- Le coût n’est pas dans les données : les quantités sont des ordres de grandeur, pas des devis.

**Le 10 est terminé quand :**

- les 4 leviers d’action ont leurs recommandations : réseau, formation, sécurité routière (les trois de l’énoncé), données (P5) ;
- les régions les moins bien desservies ont leurs recommandations : cumul (REC-Z3), route (REC-Z1), formation (REC-Z2) ;
- chaque recommandation a sa priorité, sa nature et sa localisation ;
- les 39 fiches préfectures de l’onglet « Actions par zone » ont leur problème et leur action ;
- les cartes du §6 sont écrites et vérifiées ;
- les contrôles du §9 sont conformes.

---

## 2. Méthode et outils

**Outils.** Ceux des étapes précédentes, dans `.venv` : pandas, numpy, et geopandas pour O4-E1 (déjà utilisé du 04 au 07). Aucun nouveau paquet.

**Script** : `scripts/recommandations_10.py`. Il lit :

- le 08 : `classement_08.csv` (leviers, rangs, O5-04, nature du zéro), `regions_08.csv` (zones) ;
- le 09 : `hypotheses_09.csv` (verdicts, conséquences, niveaux), `diagnostic_09.csv` (faits des phrases) ;
- le 07 : `indicateurs_07.csv` (O1-06, O1-09, O2-09, O3-05, O4-02, O4-03, O4-04, O5-04) ;
- `D4_etat_troncons.csv` (tronçons critiques, recomptés par préfecture comme au 09) et `D7_population_age_conduire.csv` (REC-F3) ;
- pour O4-E1 (§4.6) : `geo/routes_classees.geojson`, `geo/prefectures.geojson` et la population rurale de `table_maitresse_prefecture.csv` ;
- ce document, pour vérifier les nombres des cartes du §6.1 (comme le contrôle 8-07 du 09).

**Rédaction.** Les textes des cartes (§6.1) sont écrits dans ce document, à partir de `recommandations_10.csv`. Les textes des 39 fiches préfectures (§6.2) sont produits par le script, selon une règle fixe, car ils sont trop nombreux pour être écrits à la main. Chaque chiffre se relit contre les CSV.

**Ni figure ni notebook au 10.** Le tableau de bord (11) restitue les cartes.

**Ordre de travail :** leviers (§4.1 à §4.4) ; zones (§4.5 à §4.7) ; priorités (§5) ; cartes (§6) ; rubrique « données » (§7) ; contrôles (§9).

**Pour tout reproduire :** la chaîne du 09, puis `recommandations_10.py`.

**Points validés :**

**a) ✅ La localisation des auto-écoles.** La procédure (étape 11) demande une optimisation max-couverture si la couche de lieux candidats existe. Elle n’existe qu’en partie : 31 chefs-lieux et 419 localités (HDX), sans population ; la grille WorldPop est recensée, pas téléchargée (03 §2, D13). Le 10 ne fait donc pas d’optimisation. Le site indicatif est le point de départ de O4-08 de chaque préfecture (chef-lieu ou point d’étiquette, écart 19), l’ordre est le rang dans le levier formation (08 §5). **Réserve :** si la grille WorldPop est téléchargée plus tard, l’optimisation devient possible. C’est une piste, notée ici ; A1 n’est pas modifiée.

**b) ✅ Le scénario prospectif.** La procédure demande un scénario chiffré. Il relève de l’annexe A1 (horizon 2031). Si A1 est validée, chaque recommandation lit la quantité de son horizon dans `horizon_A1.csv`. Sinon, le 10 affiche les cibles de 2022 (O5-04), et le §10 le dit au 11.

---

## 3. Structure d’une recommandation

Chaque recommandation est une ligne de `recommandations_10.csv`, avec 19 colonnes. L’exemple est REC-R1.

| Colonne | Contenu | Exemple |
| ------- | ------- | ------- |
| ID | `REC-<levier><n°>` | REC-R1 |
| Levier | Réseau, Formation, Sécurité routière, Données, Zones les moins desservies | Réseau |
| Sous-levier | Entretien, Desserte, Ouverture, Vérification, Permis moto, Deux-roues, Collecte, Ouverture des données, Ciblage par zone : route, formation ou cumul | Entretien |
| Priorité | Haute, Moyenne, Faible (§5) | Haute |
| Nature | Immédiate ou conditionnelle (R-17) | Conditionnelle |
| Constat | Une phrase, issue du 09 | « 5 préfectures cumulent un réseau dégradé et aucune auto-école comptée » |
| Ampleur | Le chiffre, avec son volume | 256,3 km en mauvais état sur 562,8 km évalués ; 14 tronçons critiques |
| Territoire | Zone, région, préfecture | Plateaux (Danyi, Agou), Centrale (Blitta, Tchamba), Kara (Bassar) |
| Déficit | Ce qui manque, chiffré (O5-04) | 175,6 km à remettre en état |
| Action | Vérification, puis action | Vérifier sur place l’état relevé en 2020, puis remettre en état les tronçons critiques |
| Acteur | Celui du profil du 02 (`04_Profils`) | Ministère des travaux publics, fonds d’entretien routier |
| Cible | La cible chiffrée | Ramener chaque préfecture à la médiane nationale : 14,35 % de km en mauvais état |
| Population concernée | Habitants (O5-03) | 641 955 |
| Horizon | 1, 3 ou 5 ans (`04_Profils`) | 1 an (vérification), 3 ans (entretien) |
| Indicateur de suivi | L’ID du 02 | O3-02 |
| Niveau de preuve | A, B, C | C |
| Réserve | Ce qui reste incertain | Relevé de 2020 ; méthode de notation non documentée |
| Source | Signal du 06, verdict ou phrase du 09 | SIG-29 ; 09 §6 |
| Carte | Le texte de la carte | §6.1 |

L’ID et la source sont des colonnes techniques : elles ne s’affichent pas dans le tableau de bord.

---

## 4. Les leviers

### 4.1 Réseau

**Source :** 13 préfectures au levier réseau (08 §5) ; 49 tronçons critiques, 669,34 km en mauvais état (O3-05). Cible : la médiane nationale de O3-02, 14,35 % (PA-04). Acteur : ministère des travaux publics, fonds d’entretien routier (P1). Niveau C : chaque action commence par une vérification sur place.

| ID | Action | Territoire | Déficit (O5-04) | Population | Horizon | Priorité |
| -- | ------ | ---------- | --------------- | ---------- | ------- | -------- |
| REC-R1 | Vérifier, puis remettre en état le réseau des 5 préfectures qui cumulent | Danyi, Blitta, Agou, Tchamba, Bassar | 175,6 km (42,7 + 54,5 + 31,8 + 23,7 + 22,9) ; 14 tronçons critiques | 641 955 | 1 an, puis 3 ans | Haute |
| REC-R2 | Vérifier, puis remettre en état le réseau des 8 autres préfectures au levier réseau | Tchaoudjo, Ogou, Anié, Kloto, Wawa, Sotouboua, Agoè-Nyivé, Kozah | 129,0 km ; 20 tronçons critiques | 2 226 568 | 1 an, puis 5 ans | Moyenne |
| REC-R3 | Vérifier, puis remettre en état les 10 premiers tronçons critiques (triés par km en mauvais état, O3-05) | 18 préfectures traversées | 416,8 km en mauvais état sur 682,5 km | 3 311 579 | 1 an, puis 3 ans | Moyenne |
| REC-R4 | Vérifier la desserte de Mô, seule préfecture sans route classée | Centrale, Mô | Aucune route classée ; environ 28,3 km pour la médiane de desserte (écart 28) | 52 448 | 1 an, puis 5 ans | Faible |

**Ce que le 10 ajoute au 08 :**

- Les 13 préfectures en 2 vagues, qui se partagent les 304,6 km : 175,6 km pour les 5 qui cumulent, 129,0 km pour les 8 autres. Est-Mono n’y figure pas : elle n’est qu’au levier formation.
- La population de REC-R2 tient surtout à Agoè-Nyivé : 882 695 habitants, pour 3,2 km à remettre en état. La carte le dit.
- REC-R3 croise REC-R1 et REC-R2 : 2 des 10 tronçons sont sur la RN1, mais chacun pour ses propres km. Ce n’est pas le corridor (H5 infirmée).
- REC-R4 : la desserte ne déclenche aucun profil du 02 (SE-06). Mô est le seul cas où elle est nulle, d’où une vérification, et pas une création de route.

---

### 4.2 Formation

**Source :** 23 préfectures au levier formation (08 §5), 41 auto-écoles manquantes (O5-04, variante de l’écart 21). Cible : la médiane des 16 préfectures qui ont au moins une auto-école comptée, soit 1,065 pour 100 000 habitants. Acteur : ministère chargé des transports, auto-écoles (P2).

| ID | Action | Territoire | Déficit | Population | Horizon | Priorité |
| -- | ------ | ---------- | ------- | ---------- | ------- | -------- |
| REC-F1 | Vérifier sur place qu’il n’existe aucune auto-école, puis en ouvrir | Les 15 préfectures sans auto-école recensée, dont Danyi et Mô | 25 auto-écoles | 1 822 046 | 1 an, puis 3 ans | Moyenne |
| REC-F2 | Vérifier l’activité et l’agrément des 13 auto-écoles recensées non agréées, puis combler le manque restant | Blitta, Agou, Tchamba, Bassar, Oti, Bas-Mono, Yoto, Amou | 16 auto-écoles, si aucune n’est agréée | 1 110 446 | 1 an, puis 3 ans | Moyenne |
| REC-F3 | Faire du permis moto la priorité de la formation (H1 confirmée) | National | 40,2 immatriculations de deux-roues par permis A en cumul 2007–2024 ; 0,37 à 2,33 pour les autres catégories | 4 193 458 (18 ans et plus, 2022) | 3 ans | Moyenne |

**Ce que le 10 ajoute au 08 :**

- Les 23 préfectures en 2 groupes selon la nature du zéro (08, colonne « Note ») : 15 sans auto-école recensée (25 manquantes), 8 avec des auto-écoles recensées mais non agréées (16 manquantes). 25 + 16 = 41.
- Les 15 de REC-F1 ont toutes leur point de départ au-delà de 10 km de l’auto-école comptée la plus proche (12,9 à 84,0 km).
- Le permis moto au national (REC-F3), seule maille des permis.

**c) ✅ La cible de REC-F3 : au moins 5 513 permis A par an**, la moyenne de 2022–2024 (méthode des 3 dernières années du 02, H6 et S4). Le 02 ne la chiffre pas : P2 suit O1-06 (permis délivrés). Elle est déclarée par écart (29). Les années varient beaucoup : 4 837 permis A en 2022 (1,15 pour 1 000 habitants de 18 ans et plus), 1 538 en 2023, 10 165 en 2024. Le rapport annuel des motos suit : 13,98 en 2022, 70,12 en 2023, 6,45 en 2024. **Réserve :** 2022 et 2024 sont atypiques [SIG-05], et la moyenne en dépend. La réserve de la recommandation le dit.

---

### 4.3 Sécurité routière

**Source :** H2 confirmée sur les tués seulement (écart 26), niveau C. La conséquence du 02 : des mesures ciblées sur les motos deviennent recommandables, en C. Le 01 (§3.5) ne recommande le casque que si les données montrent une forte part de victimes à moto : 60 % des tués de 2021.

| ID | Action | Territoire | Constat | Population | Horizon | Priorité |
| -- | ------ | ---------- | ------- | ---------- | ------- | -------- |
| REC-S1 | Vérifier la part des deux-roues parmi les tués sur une seconde année, puis cibler leurs usagers : contrôle du casque et du permis A, sensibilisation | National | 60 % des tués de 2021, pour 54,7 % à 59,7 % de motos dans le parc estimé (indice de 1,01 à 1,10) | 8 095 498 | 1 an, puis 3 ans | Moyenne |

Acteur : organisme chargé de la sécurité routière (ONSR), police, gendarmerie. Suivi : O2-09.

**d) ✅ La cible de REC-S1 : ramener l’indice sous 1**, c’est-à-dire la part des deux-roues parmi les tués sous leur part dans le parc. C’est le critère de H2 lui-même (SE-09). Elle est déclarée par écart (30). **Réserve :** la surreprésentation est faible (1,01 à 1,10), et mesurée sur une seule année (2021, OMS). La carte le dit.

---

### 4.4 Données

**Source :** P5 pour le risque dans les 39 préfectures (08 §5) ; les demandes du 03 §8 ✅ et du 04 §10. Acteurs : les producteurs des données. Suivi : part des territoires renseignés (P5). Horizon : 1 an (P5).

| ID | Action | Ce qu’elle débloque | Population | Priorité |
| -- | ------ | ------------------- | ---------- | -------- |
| REC-D1 | Créer une base d’accidents par préfecture, tenue par l’ONSR, au format commun police–gendarmerie : préfecture, mois, âge, catégorie de véhicule, cause, accident corporel ou matériel, définition du tué | Les 7 hypothèses non testables (H3, H4, H7, H9, H10, H11, H12) et H2 pour les véhicules (09 §10) | 8 095 498 | Haute |
| REC-D2 | Ouvrir les couches « Dégradations » et « Ponts » du géoportail ; publier la méthode de notation, un identifiant de tronçon commun et un relevé postérieur à 2020 | La vérification de REC-R1 à REC-R3 | 8 095 498 | Moyenne |
| REC-D3 | Publier l’activité des auto-écoles collectée par PRISE (personnel, activité, horaires, véhicules) | La vérification de REC-F1 et REC-F2 ; 272 auto-écoles, dont 132 comptées | 8 095 498 | Moyenne |
| REC-D4 | Publier un parc en circulation, et corriger les libellés du portail (« parc automobile immatriculé », « accidents mortels », « premières mises en circulation », « RN4 ») | Des taux par véhicule calculés, et non plus estimés | 8 095 498 | Faible |

**Ce que le 10 ajoute au 03 et au 04 :** l’acteur, la priorité et ce que chaque demande débloque. REC-D4 réunit la 4e demande du 04 (libellés) et le parc en circulation, que le 04 donne comme limite : les deux portent sur la même série.

---

### 4.5 Répartition par zone

Le 10 répartit les recommandations des préfectures par zone, sans double compte dans un même levier. Les sommes égalent celles du 08 (§6).

| Zone | Population | Réseau (REC-R1, R2) | Formation (REC-F1, F2) | Desserte sous la médiane | Recommandations |
| ---- | ---------- | ------------------- | ---------------------- | ------------------------ | --------------- |
| Centrale | 795 529 | 4 préfectures, 113,6 km | 3 préfectures, 6 auto-écoles | Non | R1, R2, R4, F1, F2, Z3 |
| Savanes | 1 143 520 | — | 5 préfectures, 9 auto-écoles | Oui | F1, F2, Z2 |
| Plateaux | 1 635 946 | 6 préfectures, 150,5 km | 7 préfectures, 12 auto-écoles | Non | R1, R2, F1, F2, Z1 |
| Maritime hors Grand Lomé | 1 346 615 | — | 3 préfectures, 6 auto-écoles | Oui | F1, F2, Z2 |
| Kara | 985 512 | 2 préfectures, 37,3 km | 5 préfectures, 8 auto-écoles | Non | R1, R2, F1, F2 |
| Grand Lomé | 2 188 376 | 1 préfecture, 3,2 km | — | Oui | R2 |

La Centrale est la seule zone sur les deux leviers. REC-R3 n’est pas réparti : ses tronçons traversent plusieurs zones. Le tableau de bord fait de ce tableau le filtre par zone (§6).

---

### 4.6 Les régions les moins bien desservies (REC-Z1 à REC-Z3)

L’énoncé demande des recommandations « dans les régions les moins bien desservies ». Le 10 mène deux analyses, montre pourquoi elles divergent, puis conclut par dimension : la route d’un côté, la formation de l’autre.

#### Analyse 1 — Par habitant, à la maille des zones

**Règle.** Une zone est moins bien desservie si elle est sous la médiane des 6 zones à la fois pour la desserte routière (O4-03, km de routes classées pour 10 000 habitants, SE-06) et pour la formation (O4-05, auto-écoles comptées pour 100 000 habitants, SE-07).

| Zone | Desserte (km pour 10 000 hab.) | Sous la médiane (5,18) | Formation (pour 100 000 hab.) | Sous la médiane (0,53) | Moins bien desservie |
| ---- | ------------------------------ | ---------------------- | ----------------------------- | ---------------------- | -------------------- |
| Grand Lomé | 0,74 | Oui | 4,71 | Non | Non |
| Maritime hors Grand Lomé | 3,51 | Oui | 0,37 | Oui | **Oui** |
| Savanes | 4,62 | Oui | 0,35 | Oui | **Oui** |
| Centrale | 5,73 | Non | 0,50 | Oui | Non |
| Plateaux | 6,20 | Non | 0,55 | Non | Non |
| Kara | 7,40 | Non | 0,71 | Non | Non |

**Résultat :** les Savanes et la Maritime hors Grand Lomé, 2 490 135 habitants.

**Variante écartée.** Ajouter « population au-dessus de la médiane des 6 zones » ne laisse que la Maritime hors Grand Lomé : les Savanes (1 143 520 habitants) sont sous la médiane (1 245 068). Ce critère mêle le volume à l’intensité (`05_Priorisation`), et un seuil à la moyenne (1 349 250) ne retiendrait aucune zone.

#### Analyse 2 — Accès rural à une route revêtue (standard de la Banque mondiale)

**Règle.** L’indice d’accès rural (Banque mondiale, indicateur ODD 9.1.1) est la part de la population rurale qui vit à moins de 2 km d’une route praticable toute l’année. Le 10 l’approche par O4-E1 (écart 32) :

- **route praticable toute l’année** : les routes nationales revêtues du tracé (collecte PRISE 2021–2022) ;
- **calcul** : une bande de 2 km autour de ces routes, croisée avec chaque préfecture (UTM 31N, R-16) ; la part de la surface de la préfecture dans la bande ;
- **population** : la population rurale de 2022 (RGPH-5), supposée répartie uniformément dans la préfecture, multipliée par cette part ; puis sommée par zone ;
- **seuil** : sous la médiane des 5 zones qui ont une population rurale. Le Grand Lomé n’en a pas : il sort de lui-même.

| Zone | Population rurale | Ruraux à moins de 2 km d’une route revêtue | Ruraux plus loin | Sous la médiane (16,9 %) |
| ---- | ----------------- | ------------------------------------------ | ---------------- | ------------------------ |
| Centrale | 592 422 | 13,2 % | 514 276 | **Oui** |
| Plateaux | 1 266 569 | 13,6 % | 1 094 908 | **Oui** |
| Savanes | 900 681 | 16,9 % | 748 163 | Non (c’est la médiane) |
| Kara | 700 697 | 17,5 % | 578 139 | Non |
| Maritime hors Grand Lomé | 1 161 337 | 23,1 % | 892 565 | Non |
| **Togo** | 4 621 706 | **17,2 %** | | |

**Résultat :** la Centrale et les Plateaux, 2 431 475 habitants, dont 1 609 184 ruraux à plus de 2 km d’une route revêtue. Ce sont aussi les deux zones au réseau le plus dégradé (40,3 % et 28,0 % de km en mauvais état).

#### Pourquoi les deux analyses divergent

Elles s’opposent sur la Maritime hors Grand Lomé : mal desservie pour l’analyse 1 (3,51 km pour 10 000 habitants), la mieux desservie des zones rurales pour l’analyse 2 (23,1 %).

- **Pour la route, le ratio par habitant mesure la densité.** Une route sert tous ceux qui vivent à côté, quel que soit leur nombre. Les km par habitant baissent donc mécaniquement quand la densité monte. La Maritime hors Grand Lomé compte 225 habitants au km² ; rapportée à la surface, c’est la 2e zone la mieux desservie (79,0 km pour 1 000 km², O4-02).
- **Pour la formation, le ratio par habitant est la bonne mesure.** Une auto-école a une capacité : elle forme un nombre limité d’élèves. Le critère formation de l’analyse 1 est donc gardé.

**Les deux analyses ne peuvent pas converger.** Ce n’est pas la même chose mesurée par deux méthodes, ce sont deux choses différentes : pour la route, l’analyse 1 mesure la densité, l’analyse 2 l’accès. Aucun réglage de seuil ne les rapprocherait.

**Pourquoi ne pas additionner les zones des deux analyses.** Le total (Savanes, Maritime hors Grand Lomé, Centrale, Plateaux) compte 4 921 610 habitants, soit 83 % de la population hors Lomé : « les moins bien desservies » ne ciblerait plus. Il retiendrait aussi, pour la route, une zone que l’analyse 2 classe première.

#### Conclusion : les zones les moins bien desservies, par dimension

Même règle pour les deux dimensions : sous la médiane des zones.

| Zone | Route : ruraux à moins de 2 km (médiane 16,9 %) | Formation : auto-écoles pour 100 000 hab. (médiane 0,53) | Moins bien desservie pour… | Recommandation |
| ---- | ------------------------------------------------ | -------------------------------------------------------- | -------------------------- | -------------- |
| **Centrale** | **13,2 %** | **0,50** | **la route et la formation** | REC-Z3 (Haute) |
| **Plateaux** | **13,6 %** | 0,55 | la route | REC-Z1 |
| **Savanes** | 16,9 % (limite) | **0,35** | la formation | REC-Z2 |
| **Maritime hors Grand Lomé** | 23,1 % | **0,37** | la formation | REC-Z2 |
| Kara | 17,5 % | 0,71 | — | — |
| Grand Lomé | — (aucune population rurale) | 4,71 | — | — |

Chaque zone reçoit le levier de son déficit. La Centrale est la seule qui cumule les deux, comme au 08, où elle était déjà la seule zone sur les leviers réseau et formation. Comme les 5 préfectures qui cumulent (REC-R1), elle a sa propre recommandation, en priorité haute (§5.1).

✅ **Le seuil de la route : la médiane des zones, et non la valeur nationale.** Avec la valeur nationale (17,2 %), les Savanes (16,9 %) entreraient sur la route, puis passeraient en cumul et en priorité haute. Le 10 ne le retient pas :

- **même règle pour les deux dimensions** : pour la formation, la valeur nationale (1,63 auto-école pour 100 000 habitants, tirée par Lomé) retiendrait 5 zones sur 6 ;
- **l’écart est sous la précision de la mesure** : 0,24 point, sur une estimation en C qui suppose la population répartie uniformément, alors que les Savanes ont de grandes aires protégées ;
- **l’action route n’aurait rien à faire dans les Savanes** : aucune de leurs préfectures n’est au levier réseau (12,8 % de km en mauvais état, sous la médiane).

Les Savanes sont donc écrites comme cas limite pour la route, et retenues pour la formation. Le 13 le dit : avec le seuil national, elles entreraient aussi en cumul.

**Pourquoi trois recommandations, et pas deux en priorité haute.** Mettre en « Haute » les deux recommandations qui contiennent la Centrale y ferait entrer les zones qui ne cumulent pas : 86,7 % des km à remettre en état et 51,2 % des auto-écoles manquantes du pays. Les mêmes km seraient « Haute » dans une carte et « Moyenne » dans REC-R2. Les zones sont donc réparties comme les préfectures : celle qui cumule (REC-Z3), celle qui n’a que la route (REC-Z1), celles qui n’ont que la formation (REC-Z2).

#### REC-Z3 — La Centrale, seule zone qui cumule la route et la formation

| Colonne | Contenu |
| ------- | ------- |
| ID | REC-Z3 |
| Levier | Zones les moins desservies |
| Sous-levier | Ciblage par zone : cumul |
| Priorité | Haute (la zone cumule les deux déficits, §5.1) |
| Nature | Conditionnelle |
| Constat | La Centrale est la seule zone sous la médiane pour l’accès à la route et pour la formation |
| Ampleur | 13,2 % des ruraux à moins de 2 km d’une route revêtue (17,2 % dans le pays) : 514 276 ruraux plus loin ; 40,3 % de km en mauvais état ; 0,50 auto-école pour 100 000 habitants |
| Territoire | Centrale (5 préfectures) |
| Déficit | Réseau : 113,6 km dans 4 préfectures (Blitta, Tchamba, Tchaoudjo, Sotouboua). Formation : 6 auto-écoles dans 3 préfectures (Blitta, Tchamba, Mô). Déjà comptés dans REC-R1, REC-R2, REC-F1 et REC-F2 |
| Action | Vérifier, puis remettre en état les 113,6 km et ouvrir les 6 auto-écoles en premier |
| Acteur | Ministère des travaux publics, fonds d’entretien routier ; ministère chargé des transports, auto-écoles |
| Cible | 14,35 % de km en mauvais état ; 1,065 auto-école pour 100 000 habitants (écart 21), dans chaque préfecture au levier |
| Population concernée | 795 529 |
| Horizon | 1 an (vérification), 3 ans (action) |
| Indicateur de suivi | O3-02, O4-05 ; O4-E1 en contexte |
| Niveau de preuve | C |
| Réserve | Les quantités sont déjà dans les leviers : REC-Z3 les cible, elle ne les ajoute pas. L’accès rural est estimé en supposant la population répartie uniformément dans chaque préfecture : il peut être sous-estimé là où il y a de grandes zones vides (parc de Fazao). La grille WorldPop, recensée mais non téléchargée, permettrait un calcul plus précis |
| Source | §4.6, analyses 1 et 2 ; 08 §6 ; écarts 31 et 32 |
| Carte | §6.1, carte 1 |

#### REC-Z1 — La route : les Plateaux

| Colonne | Contenu |
| ------- | ------- |
| ID | REC-Z1 |
| Levier | Zones les moins desservies |
| Sous-levier | Ciblage par zone : route |
| Priorité | Moyenne (un seul déficit : le réseau) |
| Nature | Conditionnelle |
| Constat | Dans les Plateaux, 13,6 % des ruraux vivent à moins de 2 km d’une route revêtue, contre 17,2 % dans le pays ; c’est la 2e zone au réseau le plus dégradé |
| Ampleur | 1 094 908 ruraux à plus de 2 km d’une route revêtue ; 28,0 % de km en mauvais état |
| Territoire | Plateaux (12 préfectures) |
| Déficit | 6 préfectures au levier réseau (Danyi, Agou, Ogou, Anié, Kloto, Wawa) : 150,5 km, déjà comptés dans REC-R1 et REC-R2 |
| Action | Vérifier, puis remettre en état les 150,5 km en premier |
| Acteur | Ministère des travaux publics, fonds d’entretien routier |
| Cible | 14,35 % de km en mauvais état dans chaque préfecture au levier ; l’accès rural est suivi, sans cible (point 2) |
| Population concernée | 1 635 946 |
| Horizon | 1 an (vérification), 3 ans (entretien) |
| Indicateur de suivi | O3-02 ; O4-E1 en contexte |
| Niveau de preuve | C |
| Réserve | Les 150,5 km sont déjà dans REC-R1 et REC-R2. Accès rural estimé avec une population répartie uniformément ; « revêtue » approche « praticable toute l’année » ; seules les routes classées comptent |
| Source | §4.6, analyse 2 ; 08 §6 ; écarts 31 et 32 |
| Carte | §6.1, carte 9 |

#### REC-Z2 — La formation : les Savanes et la Maritime hors Grand Lomé

| Colonne | Contenu |
| ------- | ------- |
| ID | REC-Z2 |
| Levier | Zones les moins desservies |
| Sous-levier | Ciblage par zone : formation |
| Priorité | Moyenne (un seul déficit : la formation) |
| Nature | Conditionnelle |
| Constat | Les Savanes et la Maritime hors Grand Lomé ont le moins d’auto-écoles par habitant des 6 zones |
| Ampleur | 0,35 et 0,37 auto-école pour 100 000 habitants (médiane : 0,53) |
| Territoire | Savanes (7 préfectures), Maritime hors Grand Lomé (6) |
| Déficit | 8 préfectures sans auto-école agréée : 15 auto-écoles (9 dans les Savanes, 6 dans la Maritime hors Grand Lomé), déjà comptées dans REC-F1 et REC-F2 |
| Action | Vérifier, puis ouvrir les 15 auto-écoles en premier |
| Acteur | Ministère chargé des transports, auto-écoles |
| Cible | 1,065 auto-école pour 100 000 habitants dans chaque préfecture au levier (écart 21) |
| Population concernée | 2 490 135 |
| Horizon | 1 an (vérification), 3 ans (ouverture) |
| Indicateur de suivi | O4-05 |
| Niveau de preuve | C |
| Réserve | Les 15 auto-écoles sont déjà dans REC-F1 et REC-F2. L’activité des auto-écoles n’est pas connue (écart 13). Les Savanes sont à la limite pour la route (16,9 %, pour 17,2 % dans le pays) |
| Source | §4.6, analyse 1 ; 08 §6 ; écart 31 |
| Carte | §6.1, carte 6 |

**Ce que REC-Z1 à REC-Z3 ne sont pas.** Ce sont des leviers de ciblage, pas des actions nouvelles : ils ne créent ni km ni auto-école en plus de ceux des quatre leviers. Ils disent au décideur par où commencer. L’accès rural (O4-E1) y sert de contexte et d’indicateur de suivi, jamais de cible : une cible en ruraux rapprochés de la route doublerait celle de l’entretien, que la même action produit.

**REC-Z3 est une recommandation de priorisation, pas une action nouvelle.** Ses km et ses auto-écoles sont déjà dans REC-R1, REC-R2, REC-F1 et REC-F2. Le tableau de bord présente les trois recommandations de zone comme un ordre de passage (« par où commencer »), pas comme un investissement supplémentaire. Leurs quantités ne s’additionnent jamais à celles des leviers.

**Limites de l’analyse 2 (niveau C).** « L’accès rural est estimé en supposant la population répartie uniformément dans chaque préfecture. Cette approximation peut sous-estimer l’accès dans les préfectures qui ont de grandes zones vides. La grille de population WorldPop, recensée mais non téléchargée, permettrait un calcul plus précis. » Ce texte va dans la réserve des cartes et dans la page Méthodologie (11). Le calcul avec la grille est une piste pour l’annexe A1.

---

### 4.7 Actions par zone : une fiche par préfecture

**Objectif.** Offrir au décideur une lecture par préfecture, complémentaire des vues par levier. Les vues par levier disent « voici toutes les actions de formation » ; celle-ci dit « voici tout ce qu’il faut faire dans telle préfecture ».

**Source :** `prefectures_10.csv`, construit depuis `classement_08.csv` et `recommandations_10.csv`. Les tronçons critiques qui traversent chaque préfecture sont recomptés depuis `D4_etat_troncons.csv`, comme au 09.

**Ce que la vue contient :**

- une fiche par préfecture, soit 39 fiches (format au §6.2) ;
- un filtre par zone : tout le Togo (par défaut), puis les 6 zones du 02 ;
- un tri : rang national (par défaut ; Mô, non classée, après les 38), population, zone, nombre de déficits.

**Règle de contenu.** La priorité d’une préfecture suit le §5.1 : elle vient de ses leviers.

| Cas | Préfectures | Priorité | Ce que la fiche affiche |
| --- | ----------- | -------- | ----------------------- |
| Réseau et formation (O5-01 = 2) | 5 | Haute | Les deux problèmes, les deux actions |
| Un seul levier (O5-01 = 1) | 26, dont Mô | Moyenne | Le problème et l’action du levier. Pour Mô, aussi la desserte à vérifier (REC-R4) |
| Aucun levier (O5-01 = 0) | 8 : Zio, Assoli, Cinkassé, Tône, Kpélé, Lacs, Vo, Golfe | Aucune action | « Suivi courant. Aucune action prioritaire. » Et les tronçons des 10 plus dégradés qui la traversent, s’il y en a |

Les préfectures sans levier ne sont pas « Faible » : cette étiquette laisserait croire à une action. Elles prennent la couleur « non classée » de la maquette.

**Ce que cette vue n’est pas :** elle ne crée pas de recommandation. Elle répartit les 15 recommandations au niveau des préfectures. Les totaux (habitants, km, auto-écoles) restent ceux du 08 et du 10, sans double compte.

---

## 5. Priorités

### 5.1 Règle

La priorité dit l’intensité du déficit. Le volume (les habitants) ordonne les recommandations de même priorité (`05_Priorisation`, « Intensité et volume »). La règle est fixée ici, avant le calcul (R-20).

| Priorité | Condition |
| -------- | --------- |
| **Haute** | La recommandation ne vise que des territoires qui cumulent les deux déficits mesurés : des préfectures (O5-01 = 2) ou une zone (route et formation sous la médiane des zones, §4.6). Ou elle conditionne tout ciblage par le risque (base d’accidents : sans elle, le risque reste national, 01 §2.3) |
| **Moyenne** | Elle vise un seul déficit mesuré (levier réseau ou formation du 08), elle découle d’une hypothèse confirmée (H1, H2), ou elle vérifie une recommandation en C |
| **Faible** | Elle ne vise ni un levier du 02 ni une hypothèse confirmée : cas de Mô, lisibilité des séries |

**Pourquoi ni la population, ni l’horizon, ni le niveau de preuve ne sont des critères :**

- **Population.** Les groupes sont grands et se recoupent. Un seuil de 500 000 habitants mettrait presque tout en « Haute ». REC-R2 dépasserait le seuil grâce à Agoè-Nyivé, pour 3,2 km. La population sert à ordonner, pas à classer.
- **Horizon.** Il vient du profil du 02 (`04_Profils`) : il ne peut pas en même temps décider de la priorité.
- **Niveau de preuve.** Toutes les recommandations territoriales sont en C : le critère ne départage rien. Il décide de la nature (§5.2).

**Application :**

| Priorité | Recommandations |
| -------- | --------------- |
| Haute | REC-R1, REC-Z3, REC-D1 |
| Moyenne | REC-R2, REC-R3, REC-F1, REC-F2, REC-F3, REC-S1, REC-Z1, REC-Z2, REC-D2, REC-D3 |
| Faible | REC-R4, REC-D4 |

Le script recalcule chaque priorité depuis la règle. Le contrôle compare avec ce tableau.

### 5.2 Nature : immédiate ou conditionnelle

La matrice impact × faisabilité de la version 0.1 est retirée : le coût n’est pas dans les données (01 §3.5), et ni l’impact ni la faisabilité n’avaient de définition mesurable. La nature, prévue par la maquette (étiquette `reco-nature`), dit ce que le décideur peut lancer tout de suite :

| Nature | Condition | Recommandations |
| ------ | --------- | --------------- |
| **Conditionnelle** | Portée par un indicateur C : la vérification vient d’abord (R-17) | REC-R1 à REC-R4, REC-F1, REC-F2, REC-S1, REC-Z1 à REC-Z3 |
| **Immédiate** | Portée par un indicateur A ou B, ou demande de données | REC-F3 (B), REC-D1 à REC-D4 |

---

## 6. Cartes de la page « Recommandations »

Cette section explique comment afficher les recommandations : d’abord les éléments que l’objectif demande, puis les compléments que le décideur doit voir. Les autres pages du tableau de bord sont définies au 11.

**Format** : la carte de recommandation de la maquette (`MAQUETTE_dashboard.md` §8.11). Grille de 3 colonnes.

- **Thème** : pastille et libellé en majuscules. Réseau, Formation, Sécurité routière, Zones les moins desservies, Données.
- **Titre** : 1 ligne, verbe + objet + territoire.
- **Phrase de cible** : « Porter X de A à B ».
- **Contexte** : « N préfectures · Z habitants concernés », avec l’espace des milliers.
- **Étiquettes** : priorité, nature, horizon. Couleurs de la palette `PRIORITE` : haute `#0d366b`, moyenne `#3987e5`, faible `#cde2fb`, non classée `#b9b6ad`. L’horizon affiché est celui de l’action ; la vérification d’une carte conditionnelle se fait dans l’année, et le texte le dit.
- **Ordre par défaut** : priorité, puis habitants.
- **Filtres** : priorité et zone (via `prefectures_10.csv`) ; le levier est donné par les onglets.
- **Barre de résumé** : « 15 recommandations · … », avec la légende « les habitants ne s’additionnent pas d’une carte à l’autre ».
- **Trois bandeaux** (procédure, étape 12) : le constat (« 5 préfectures cumulent les deux déficits »), la synthèse chiffrée, et la limite de la page : « recommandations en C : vérifier avant d’investir ; pas d’accidents par territoire ; le coût n’est pas dans les données ».
- **Aucun code interne** dans les textes : ni indicateur (« O3-02 »), ni hypothèse (« H1 »), ni seuil, signal, écart, profil, ni identifiant de recommandation (« REC-R1 »).
- **Pas de double compte** : les km et les auto-écoles des cartes de zone sont déjà dans les cartes des leviers. Aucun total de la page (barre de résumé, filtre par zone) ne les additionne.

**Les onglets de la page.** 7 onglets, dans cet ordre :

1. Toutes : les 15 cartes, la rubrique « Pour aller plus loin » à la fin ;
2. Réseau ;
3. Formation ;
4. Sécurité routière ;
5. Zones les moins desservies : les 3 cartes de zone sous un bandeau « Par où commencer », et le tableau de conclusion du §4.6, sans les calculs. Les deux analyses et leurs calculs vont dans la page Méthodologie ;
6. Données : la rubrique « Pour aller plus loin » (§7) ;
7. Actions par zone : les 39 fiches préfectures (§4.7, §6.2).

**Les 15 cartes** : 11 sur la page, 4 dans la rubrique « Pour aller plus loin » (§7).

| # | Titre | Thème | Habitants | Priorité | Nature | Horizon | Territoire |
| - | ----- | ----- | --------- | -------- | ------ | ------- | ---------- |
| 1 | Agir d’abord dans la Centrale, seule zone en retard sur la route et la formation | Zones les moins desservies | 795 529 | Haute | Conditionnelle | 3 ans | Centrale |
| 2 | Remettre en état le réseau des 5 préfectures qui cumulent | Réseau | 641 955 | Haute | Conditionnelle | 3 ans | Plateaux, Centrale, Kara |
| 3 | Cibler les usagers de deux-roues motorisés | Sécurité routière | 8 095 498 | Moyenne | Conditionnelle | 3 ans | National |
| 4 | Faire du permis moto la priorité de la formation | Formation | 4 193 458 | Moyenne | Immédiate | 3 ans | National |
| 5 | Remettre en état les 10 tronçons les plus dégradés | Réseau | 3 311 579 | Moyenne | Conditionnelle | 3 ans | 18 préfectures |
| 6 | Ouvrir d’abord des auto-écoles dans les Savanes et la Maritime hors Grand Lomé | Zones les moins desservies | 2 490 135 | Moyenne | Conditionnelle | 3 ans | Savanes, Maritime hors Grand Lomé |
| 7 | Remettre en état le réseau de 8 autres préfectures | Réseau | 2 226 568 | Moyenne | Conditionnelle | 5 ans | 4 zones |
| 8 | Ouvrir des auto-écoles dans les 15 préfectures qui n’en ont aucune | Formation | 1 822 046 | Moyenne | Conditionnelle | 3 ans | 5 zones |
| 9 | Remettre en état d’abord le réseau des Plateaux | Zones les moins desservies | 1 635 946 | Moyenne | Conditionnelle | 3 ans | Plateaux |
| 10 | Vérifier les auto-écoles non agréées de 8 préfectures | Formation | 1 110 446 | Moyenne | Conditionnelle | 3 ans | 5 zones |
| 11 | Vérifier la desserte de Mô | Réseau | 52 448 | Faible | Conditionnelle | 5 ans | Centrale, Mô |
| 12 | Créer une base d’accidents par préfecture | Données | 8 095 498 | Haute | Immédiate | 1 an | National |
| 13 | Ouvrir les couches « Dégradations » et « Ponts » | Données | 8 095 498 | Moyenne | Immédiate | 1 an | National |
| 14 | Publier l’activité des auto-écoles | Données | 8 095 498 | Moyenne | Immédiate | 1 an | National |
| 15 | Publier un parc en circulation et des libellés exacts | Données | 8 095 498 | Faible | Immédiate | 1 an | National |

---

### 6.1 Textes des cartes

**Carte 1 — Agir d’abord dans la Centrale, seule zone en retard sur la route et la formation**

> Dans la Centrale, seuls 13,2 % des ruraux vivent à moins de 2 km d’une route revêtue (17,2 % dans le pays), 40,3 % des routes sont en mauvais état, et l’offre est de 0,50 auto-école pour 100 000 habitants. C’est la seule zone en retard sur la route et sur la formation. 113,6 km à remettre en état et 6 auto-écoles à ouvrir en premier, après vérification. 795 529 habitants concernés.

**Carte 2 — Remettre en état le réseau des 5 préfectures qui cumulent**

> Danyi, Blitta, Agou, Tchamba et Bassar ont de 28 % à 100 % de leurs routes en mauvais état, et aucune auto-école agréée. 14 tronçons critiques les traversent. Les ramener à la médiane nationale (14,35 %) suppose de remettre en état 175,6 km, après vérification sur place. 641 955 habitants concernés.

**Carte 3 — Cibler les usagers de deux-roues motorisés**

> En 2021, 60 % des tués sont des usagers de deux et trois-roues motorisés, pour 54,7 % à 59,7 % de motos dans le parc. La surreprésentation est faible, mais elle tient dans toute la fourchette. À vérifier sur une seconde année, avant les contrôles du casque et du permis.

**Carte 4 — Faire du permis moto la priorité de la formation**

> De 2007 à 2024, 40,2 deux-roues ont été immatriculés pour un permis moto délivré, contre 0,37 à 2,33 véhicules par permis dans les autres catégories. Le rapport est plus bas en 2022 et en 2024 (13,98 et 6,45), années de forte hausse des permis moto. 4 193 458 habitants en âge de conduire.

**Carte 5 — Remettre en état les 10 tronçons les plus dégradés**

> 49 tronçons ont des km en mauvais état, 669,34 km en tout. Les 10 premiers en portent 416,8 km, dont 2 sur la RN1. Ils traversent 18 préfectures. L’état date du relevé de 2020 : à vérifier avant les travaux.

**Carte 6 — Ouvrir d’abord des auto-écoles dans les Savanes et la Maritime hors Grand Lomé**

> Les Savanes et la Maritime hors Grand Lomé ont le moins d’auto-écoles par habitant : 0,35 et 0,37 pour 100 000 habitants. 8 de leurs préfectures n’en ont aucune agréée : 15 auto-écoles à ouvrir en premier, après vérification. 2 490 135 habitants concernés.

**Carte 7 — Remettre en état le réseau de 8 autres préfectures**

> Tchaoudjo, Ogou, Anié, Kloto, Wawa, Sotouboua, Agoè-Nyivé et Kozah ont de 22,3 % à 65,0 % de leurs routes en mauvais état, sans manque d’auto-écoles. 129,0 km à remettre en état. 2 226 568 habitants, dont 882 695 à Agoè-Nyivé pour 3,2 km.

**Carte 8 — Ouvrir des auto-écoles dans les 15 préfectures qui n’en ont aucune**

> 15 préfectures n’ont aucune auto-école, ni agréée ni recensée : l’auto-école agréée la plus proche est à 12,9 à 84,0 km, selon la préfecture. Atteindre la médiane des préfectures équipées (1,065 pour 100 000 habitants) suppose 25 auto-écoles, après vérification sur place. 1 822 046 habitants concernés.

**Carte 9 — Remettre en état d’abord le réseau des Plateaux**

> Dans les Plateaux, seuls 13,6 % des ruraux vivent à moins de 2 km d’une route revêtue (17,2 % dans le pays) : 1 094 908 ruraux en sont plus loin. 28,0 % des routes sont en mauvais état. Leurs 6 préfectures au réseau dégradé ont 150,5 km à remettre en état en premier, après vérification. 1 635 946 habitants concernés.

**Carte 10 — Vérifier les auto-écoles non agréées de 8 préfectures**

> Blitta, Agou, Tchamba, Bassar, Oti, Bas-Mono, Yoto et Amou n’ont aucune auto-école agréée, mais 13 y sont recensées. Vérifier leur activité et leur agrément : le manque est peut-être administratif. S’il est réel, 16 auto-écoles sont à ouvrir. 1 110 446 habitants concernés.

**Carte 11 — Vérifier la desserte de Mô**

> Mô n’a aucune route classée, et son auto-école agréée la plus proche est à 52,2 km. C’est la seule préfecture dans ce cas. La médiane nationale de desserte représenterait environ 28,3 km de routes : un ordre de grandeur, pas un tracé. 52 448 habitants concernés.

**Carte 12 — Créer une base d’accidents par préfecture**

> Les accidents ne sont publiés qu’au niveau national : 7 507 accidents et 683 tués en 2022, sans préfecture, mois, âge ni véhicule. Cette base permettrait de croiser risque et territoire, et de trancher 7 questions que les données laissent ouvertes.

**Carte 13 — Ouvrir les couches « Dégradations » et « Ponts »**

> L’état du réseau vient d’un relevé de 2020, sans tracé ni méthode de notation publiée. Les couches de la collecte 2021–2022 existent au géoportail, mais ne sont pas ouvertes. Elles permettraient de vérifier l’état des 13 préfectures ciblées.

**Carte 14 — Publier l’activité des auto-écoles**

> La campagne PRISE a relevé le personnel, l’activité, les horaires et les véhicules de 272 auto-écoles, sans les publier. Ces données diraient lesquelles fonctionnent, et vérifieraient le manque dans les 23 préfectures sans auto-école agréée.

**Carte 15 — Publier un parc en circulation et des libellés exacts**

> Le « parc automobile immatriculé » du portail compte les immatriculations de l’année, pas les véhicules en circulation. Un parc publié rendrait les taux par véhicule calculés, et non plus estimés. D’autres libellés sont à corriger, dont les « accidents mortels », qui sont des accidents constatés.

---

### 6.2 Fiches de l’onglet « Actions par zone »

**Format :** celui des cartes du §6.1 (même grille de 3 colonnes, mêmes étiquettes de priorité). Différences :

- **Titre :** le nom de la préfecture.
- **Thème :** la zone.
- **Grand chiffre :** la population de la préfecture.
- **Corps :** deux blocs courts, « Réseau » et « Formation », avec le problème chiffré ; pour Mô, un bloc « Desserte ».
- **Bandeau d’action :** un bloc « Actions recommandées », fond gris clair, bordure gauche sombre.
- **Pied :** étiquette de priorité et tag « Zone — Préfecture ».
- **Aucun code interne** dans les textes.

**Icônes par cas :** 🛣️ réseau seul ; 📚 formation seule ; 🛣️📚 les deux ; ✓ suivi courant, sans action.

**Exemple :**

> **Danyi** — Plateaux
>
> **40 240** habitants
>
> **Réseau :** 100 % des routes en mauvais état (49,8 km évalués, 3 tronçons critiques).
> **Formation :** aucune auto-école, ni agréée ni recensée. La plus proche est à 12,9 km.
>
> **Actions recommandées**
> Vérifier l’état sur place, puis remettre en état 42,7 km. Vérifier qu’aucune auto-école n’existe, puis en ouvrir une.
>
> [Haute] 📍 Plateaux — Danyi

**Cas particuliers :**

- **Mô :** 📚, Moyenne. « Desserte : aucune route classée, à vérifier sur place. Formation : aucune auto-école, la plus proche à 52,2 km ; vérifier, puis en ouvrir une. »
- **Agoè-Nyivé :** 🛣️, Moyenne. Réseau : 26,0 % en mauvais état, 3,2 km à remettre en état. Formation : 3,29 auto-écoles pour 100 000 habitants, au-dessus de la cible.
- **Golfe :** ✓, aucune action. Réseau : 0,5 % en mauvais état. Formation : la plus forte offre du pays (5,67 pour 100 000 habitants).
- **Les 7 autres préfectures sans levier** (Zio, Assoli, Cinkassé, Tône, Kpélé, Lacs, Vo) : ✓, « Suivi courant. Aucune action prioritaire. » Si un des 10 tronçons les plus dégradés les traverse (Zio, Kpélé), la fiche le dit.

Le texte de chaque fiche est produit par le script, selon cette règle, et ses nombres sont vérifiés contre `prefectures_10.csv`.

---

## 7. Rubrique « Pour aller plus loin »

Les 4 recommandations « données » (REC-D1 à REC-D4) forment la rubrique **« Pour aller plus loin : ce que les données ne permettent pas encore de dire »**, placée après les recommandations territoriales (03 §8 ✅).

**Phrase d’introduction**, sans code :

> « Ces 4 actions relèvent des producteurs de données, pas des régions. La base d’accidents par préfecture permettrait de trancher 7 questions que le diagnostic laisse ouvertes, dont le lien entre réseau dégradé et accidents. Les trois autres rendraient vérifiables les chiffres estimés de cette page. »

La priorité « Haute » de REC-D1 reste affichée sur sa carte : la place dans la page ne change pas la priorité.

Le 03 (§8) ajoute une question à poser quand les accidents seront localisés : les tronçons sans aménagement de sécurité concentrent-ils les accidents ? Elle va au 13, avec les hypothèses restées ouvertes.

---

## 8. Fichiers produits

**Dans `data/analysis/10_recommandations/`**, écrits par `recommandations_10.py` :

| Fichier | Contenu |
| ------- | ------- |
| `recommandations_10.csv` | 15 lignes (REC-R1 à REC-R4, REC-F1 à REC-F3, REC-S1, REC-Z1 à REC-Z3, REC-D1 à REC-D4), 19 colonnes (§3) |
| `prefectures_10.csv` | 39 lignes, une par préfecture : filtre par zone, §4.5, onglet « Actions par zone » (§4.7, §6.2) |
| `zones_10.csv` | 6 zones, la médiane des zones et le pays : accès rural, desserte, km pour 1 000 km², auto-écoles, part en mauvais état, km par état, verdicts des deux analyses, recommandation (§4.6) |
| `cartes_10.csv` | 15 lignes, format carte |
| `controles_10.csv` | Les contrôles du §9 |

`prefectures_10.csv` remplace `territoires_10.csv` de la version 0.2 : les deux étaient à la maille de la préfecture. Un seul fichier évite que deux endroits portent la même grandeur (procédure, étape 14).

**Colonnes de `cartes_10.csv` :**

| Colonne | Contenu |
| ------- | ------- |
| ID | REC-R1, etc. (non affiché) |
| Ordre | Rang d’affichage par défaut : priorité, puis habitants ; rubrique « données » à la fin |
| Onglet | Réseau, Formation, Sécurité routière, Zones les moins desservies, Données |
| Rubrique | Recommandations, ou « Pour aller plus loin » |
| Titre | 1 ligne |
| Cible | La phrase de cible |
| Contexte | Territoires · habitants |
| Habitants | Nombre entier |
| Priorité | Haute, Moyenne, Faible |
| Nature | Immédiate, Conditionnelle |
| Horizon | 1 an, 3 ans, 5 ans |
| Zones | Les zones concernées, pour le filtre |
| Acteur | L’acteur (R-18) |
| Indicateur de suivi | L’indicateur, en clair (R-18, règle des codes) |
| Niveau de preuve | A — mesuré, B — calculé, C — estimé, ou sans objet (R-18) |
| Réserve | La réserve, en clair (R-18) ; la colonne de `recommandations_10.csv` garde ses références techniques |
| Texte | Le texte du §6.1 |

**Colonnes de `prefectures_10.csv` :**

| Colonne | Contenu |
| ------- | ------- |
| Préfecture | Nom |
| Zone | Une des 6 zones du 02 |
| Région | Une des 5 régions |
| Population | Habitants en 2022 |
| Réseau — part en mauvais état | O3-02 (vide pour Mô) |
| Réseau — km évalués | Dénominateur de O3-02 |
| Réseau — tronçons critiques | Nombre de tronçons critiques qui la traversent (O3-05) |
| Réseau — dont parmi les 10 plus dégradés | Nombre de tronçons de REC-R3 qui la traversent |
| Réseau — km à remettre en état | O5-04, pour les préfectures au levier réseau |
| Formation — auto-écoles comptées | Agréées et antennes agréées (O4-04, R-12) |
| Formation — auto-écoles recensées | Toutes les auto-écoles du fichier (O4-04) |
| Formation — distance à la plus proche | O4-08, km |
| Formation — auto-écoles à ouvrir | O5-04 (écart 21), pour les préfectures au levier formation |
| Desserte | O4-03, km pour 10 000 habitants |
| Population rurale | Habitants ruraux en 2022 (RGPH-5) |
| Accès rural à une route revêtue | O4-E1 : part des ruraux à moins de 2 km d’une route nationale revêtue (§4.6, analyse 2) |
| Déficits | O5-01 : 0, 1 ou 2 |
| Rang national | O5-02 ; vide pour Mô (non classée) |
| Leviers | Réseau, formation, les deux ou aucun |
| Recommandations | Les ID qui la visent (REC-R1, REC-F1…) |
| Priorité | Haute, Moyenne, Aucune action (§4.7) |
| Texte réseau | Le bloc « Réseau » de la fiche |
| Texte formation | Le bloc « Formation » de la fiche |
| Actions | Le texte du bandeau d’action |
| Note | Mô, nature du zéro |

---

## 9. Validation

| Contrôle | Attendu |
| -------- | ------- |
| Recommandations | 15 lignes ; 4 leviers d’action et le ciblage par zone (cumul, route, formation) ; les champs de R-18 renseignés pour chacune |
| Concordance réseau | REC-R1 + REC-R2 = les 13 préfectures du 08, 304,6 km, 2 868 523 habitants ; chaque préfecture dans une seule des deux |
| Concordance formation | REC-F1 + REC-F2 = les 23 préfectures du 08, 41 auto-écoles, 2 932 492 habitants ; chaque préfecture dans une seule des deux |
| Zones | Les sommes par zone de `prefectures_10.csv` égalent celles de `regions_08.csv` (§4.5) |
| Zones les moins desservies | Analyse 1 recalculée depuis `regions_08.csv` : Savanes et Maritime hors Grand Lomé. O4-E1 recalculé depuis les couches : la somme des ruraux des préfectures égale 4 621 706 ; part de chaque préfecture entre 0 et 1 ; Centrale et Plateaux sous la médiane des 5 zones rurales. REC-Z3 = Centrale (113,6 km, 6 auto-écoles) ; REC-Z1 = Plateaux (150,5 km) ; REC-Z2 = Savanes et Maritime hors Grand Lomé (15 auto-écoles) ; chaque fois égal aux leviers du 08 dans ces zones, et chaque zone dans une seule des trois |
| Préfectures | 39 lignes ; 6 zones et 5 régions représentées ; chaque valeur identique à sa source (`classement_08.csv`, `indicateurs_07.csv`) ou recalculée par le script (tronçons critiques, O4-E1), jamais saisie ; 5 Haute, 26 Moyenne, 8 sans action |
| Tronçons | 49 tronçons critiques et 669,34 km, recomptés depuis le relevé ; les 10 premiers et leurs préfectures |
| Priorités | Chaque priorité suit la règle du §5.1, recalculée par le script ; « Haute » seulement pour des recommandations qui ne visent que des territoires en cumul, ou pour la base d’accidents ; aucun quota |
| R-17 | Chaque recommandation en C est « conditionnelle », et son action commence par une vérification |
| Hypothèses et compléments | Aucune recommandation ne s’appuie sur une hypothèse non testable, sur H5 ou H6, ni sur O2-E1 à O2-E3 |
| Cartes et fiches | 15 cartes et 39 fiches ; chaque nombre vaut, à son arrondi, une valeur des CSV ; aucun code interne dans les textes |
| Pas de double compte | Dans chaque levier, une préfecture n’apparaît qu’une fois ; les quantités de REC-Z1 à REC-Z3 et de REC-R3 ne sont ajoutées à aucun total |
| Table des zones | `zones_10.csv` : population, part en mauvais état, auto-écoles et desserte égales à `regions_08.csv` ; km par état cohérents avec les km évalués ; ligne du pays égale à la somme des zones |
| Style des fiches et des cartes | Phrases complètes ; aucun code interne ; aucun « None », « nan » ni « 0 » écrit à la place d’une valeur manquante : une valeur absente s’écrit en mots (« aucune route classée ») |
| Reproductibilité | Deux exécutions donnent les mêmes fichiers |

Le contrôle « somme des populations ≤ 8 095 498 » de la version 0.1 est retiré : les habitants ne s’additionnent pas entre recommandations (MAQUETTE §8.11), et REC-D1 couvre à elle seule tout le pays. La non-duplication se contrôle dans chaque levier.

**Résultat : 14 contrôles conformes sur 14** (`controles_10.csv`).

- **Concordance avec le 08 :** réseau, 5 + 8 préfectures, 175,6 + 129,0 = 304,6 km, 2 868 523 habitants ; formation, 15 + 8 préfectures, 25 + 16 = 41 auto-écoles, 2 932 492 habitants. Aucune préfecture dans deux recommandations d’un même levier.
- **Zones :** les 6 zones × 5 grandeurs de `prefectures_10.csv` égalent `regions_08.csv`.
- **Zones les moins desservies :** l’accès rural est calculé sur les 4 621 706 ruraux du pays. La médiane des 5 zones rurales est 16,93 %, et la valeur nationale 17,17 %. Route : Centrale et Plateaux ; formation : Centrale, Savanes et Maritime hors Grand Lomé. REC-Z3, REC-Z1 et REC-Z2 couvrent chacune des zones distinctes : 264,1 km sur 304,6 et 21 auto-écoles sur 41, déjà dans les leviers.
- **Préfectures :** 39 fiches ; 273 valeurs comparées à `classement_08.csv`, aucune différence ; 5 Haute, 26 Moyenne, 8 sans action.
- **Priorités :** recalculées par la règle du §5.1, identiques au tableau d’application.
- **Cartes :** les 81 nombres des 15 cartes du §6.1 sont vérifiés par le script ; l’ordre et le tableau du §6 sont identiques au calcul ; aucun code interne.
- **Table des zones :** les 6 zones de `zones_10.csv` redonnent les valeurs de `regions_08.csv` ; la ligne du pays (8 095 498 habitants, 4 621 706 ruraux, dont 3 828 051 à plus de 2 km d’une route revêtue) égale la somme des zones.
- **Style :** 207 textes relus (fiches, cartes, et champs de R-18 en clair), sans défaut.
- **Reproductibilité :** deux exécutions donnent des fichiers identiques à l’octet près. Les sorties du 06 au 09 ne sont pas modifiées.

---

## 10. Suite

Les 11, 12 et 13 sont les trois documents qui suivent le 10. Ce ne sont pas des pages. Depuis le 08, un document couvre l’étape suivante de la procédure : le 11 couvre l’étape 12, le 12 l’étape 13, le 13 l’étape 14.

- **11 — Tableau de bord** (étape 12) : construit l’application et ses 7 pages (vue nationale, comparaison territoriale, analyse détaillée, carte, priorités, recommandations, méthodologie). Le 11 définit ce que chaque page affiche. Le 10 lui transmet :
  - **pour la page « Recommandations »** : les 15 cartes au format du §6, les 7 onglets (dont « Zones les moins desservies » et « Actions par zone »), les filtres priorité et zone, la rubrique « Pour aller plus loin » (§7) ;
  - **les horizons** : si l’annexe A1 est validée, les quantités de chaque palier ; sinon, les cibles de 2022, affichées comme telles ;
  - **pour la page Méthodologie** : les deux analyses du §4.6 avec leurs calculs, la limite de l’accès rural mot pour mot, et la légende des niveaux de preuve (A = mesuré, B = calculé, C = estimé) ;
  - **pour la vue nationale**, les consignes du 09 (09 §10) : le multiplicateur de 4,56 (S1), la moto comme catégorie de référence (S2), le chiffre de la source avec sa définition (S3), le message « plus de véhicules, pas une route plus dangereuse » (S4) ;
  - **pour toutes les pages, la règle des codes** : aucun code interne dans l’interface (indicateurs, hypothèses, seuils, écarts, signaux, profils, recommandations), seulement les intitulés en clair ; les niveaux de preuve A, B, C avec leur légende (mesuré, calculé, estimé). Elle est plus stricte que la procédure, qui tolère un code accompagné de son intitulé. Les phrases du 09 contiennent des codes (« [SIG-25] ») et des mentions techniques (« 6 tests sur 6 ») : le 11 les réécrit à l’affichage ; le 09, figé, n’est pas modifié. Le 11 reporte aussi la règle dans la maquette.
- **Annexe A1** : télécharger la grille WorldPop, recalculer l’accès rural (O4-E1) et l’optimisation de l’emplacement des auto-écoles (point a), puis confirmer ou corriger la conclusion du §4.6. C’est la vérification qui manque à l’écart 32. Le 10 n’en dépend pas.
- **12 — Validation** (étape 13) : « cette recommandation est-elle réellement justifiée par les données ? », une revue de rigueur et une revue de décision.
- **13 — Rapport final** (étape 14) : les recommandations chiffrées, les hypothèses restées ouvertes et la donnée qui les rendrait testables (09 §10). La divergence des deux mesures de la desserte (§4.6) y devient un résultat : les km de route par habitant mesurent la densité, pas l’accès.
  Il transmet aussi trois points sur les zones :
  - **l’énoncé** : rappeler que REC-Z1 à REC-Z3 répondent à l’objectif 5 (« dans les régions les moins bien desservies »), et que la lecture par dimension est nécessaire parce que les indicateurs du 02 ne permettent pas une lecture unique ;
  - **l’écart 32** : « L’accès rural (O4-E1) a été introduit après un calcul exploratoire. La dimension route en dépend entièrement ; la dimension formation repose sur un indicateur du 02 et n’en dépend pas. » ;
  - **les Savanes** : cas limite pour la route (16,9 %, pour 17,2 % dans le pays) ; avec le seuil national, elles entreraient en cumul.

---

## 11. Écarts au 02

Déclarés avant le calcul (R-20), sauf l’écart 32, déclaré après un calcul exploratoire (voir sa raison). Les écarts 1 à 26 sont ceux du 04, 07, 08 et 09. Le 02 n’est pas modifié.

| N° | Écart | Traitement | Raison |
| -- | ----- | ---------- | ------ |
| 27 | Le 02 ne fixe pas de règle de priorité entre recommandations ; la procédure (étape 11) en demande une | Règle du §5.1 : intensité du déficit, puis habitants pour ordonner. Le cumul vaut pour les préfectures et pour les zones | Une règle écrite avant le calcul évite le classement arbitraire. Elle reprend la distinction « intensité et volume » de `05_Priorisation`. Une même notion de cumul, à toutes les mailles |
| 28 | Le 02 ne prévoit pas de cible pour la desserte (O4-03 n’entre dans aucun profil) | Pour Mô seulement : la médiane nationale de O4-03 (5,39 km pour 10 000 habitants), soit environ 28,3 km, en C | R-18 exige une cible chiffrée. Mô est la seule préfecture sans route classée. La cible reste un ordre de grandeur derrière une vérification |
| 29 | Le 02 ne chiffre pas la cible du permis moto (P2 suit O1-06) | Au moins 5 513 permis A par an, la moyenne de 2022–2024 | R-18 exige une cible chiffrée. Les 3 dernières années sont la méthode du 02 pour H6 et S4. Réserve : 2022 et 2024 sont atypiques [SIG-05] |
| 30 | Le 02 ne chiffre pas la cible des mesures sur les deux-roues | Indice sous 1 : part des deux-roues parmi les tués sous leur part dans le parc | C’est le critère de H2 (SE-09). Réserve : une seule année mesurée, surreprésentation faible |
| 31 | Le 02 appelle « peu desservie » une zone sous la médiane de O4-03 (SE-06), soit 3 zones dont le Grand Lomé | « Moins bien desservie » se lit par dimension, sous la médiane des zones. Route : O4-E1 (accès rural), au lieu de O4-03 ; Centrale et Plateaux. Formation : O4-05 (SE-07) ; Centrale, Savanes et Maritime hors Grand Lomé. La Centrale cumule. Les Savanes sont un cas limite pour la route (0,24 point sous la valeur nationale) | Pour la route, O4-03 mesure la densité : la Maritime hors Grand Lomé y paraît mal desservie alors que ses ruraux ont le meilleur accès (§4.6). Pour la formation, le ratio par habitant mesure bien une capacité. L’énoncé cible ces régions pour la formation, l’entretien et la sécurité : chaque zone reçoit le levier de son déficit |
| 32 | Le 02 ne prévoit pas d’indicateur d’accès à la route | O4-E1, complément au 02 (comme O2-E1 à O2-E3, écart 22) : part des ruraux à moins de 2 km d’une route nationale revêtue, approche de l’indice d’accès rural de la Banque mondiale (ODD 9.1.1). Niveau C | C’est la mesure de référence de la desserte rurale. **Déclaré après un calcul exploratoire**, et non avant comme le demande R-20 : le calcul a été fait pour comparer deux définitions, puis retenu. Le document le dit ici |

L’écart 27 de la version 0.1 (« P1 à P6 ») est retiré. Ce n’en est pas un : le 02 prévoit les recommandations par levier quand le risque est national, et le 08 l’a appliqué (voir Point de départ).

---

## 12. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 10** : un script, quatre fichiers ; ni figure ni notebook | Tout le document | Équipe, 2026-10-07 |
| ✅ **Groupes** : réseau en 2 vagues (5 qui cumulent, 8 autres) ; formation selon la nature du zéro (15 sans auto-école recensée, 8 avec des non agréées) | §4.1, §4.2 | Équipe, 2026-10-07 |
| ✅ **REC-R4** : vérifier la desserte de Mô, sans création de route | §4.1 | Équipe, 2026-10-07 |
| ✅ **REC-S1** ajoutée : conséquence de H2 transmise par le 09 | §4.3 | Équipe, 2026-10-07 |
| ✅ **REC-F4 retirée** : elle s’appuyait sur H8, qui porte sur la concentration urbaine des auto-écoles, pas sur l’usage de la moto ; ses 15 auto-écoles étaient déjà dans REC-F1 et REC-F2 | §4.2 | Équipe, 2026-10-07 |
| ✅ **Priorité** : règle du §5.1, sans population ni horizon comme critères | §5.1 | Équipe, 2026-10-07 |
| ✅ **Nature** immédiate ou conditionnelle, à la place de la matrice impact × faisabilité | §5.2 | Équipe, 2026-10-07 |
| ✅ **Format des cartes** : celui de la maquette (§8.11) | §6 | Équipe, 2026-10-07 |
| ✅ **Rubrique « Pour aller plus loin »** pour les 4 recommandations « données » | §7 | 03 §8 |
| ✅ **Points a à d** : localisation sans optimisation (WorldPop en piste) ; scénario renvoyé à A1, cibles de 2022 sinon ; 5 513 permis A par an ; indice des deux-roues sous 1 | §2, §4.2, §4.3 | Équipe, 2026-10-07 |
| ✅ **Écarts 27 et 28** | §11 | Équipe, 2026-10-07 |
| ✅ **Régions les moins bien desservies** : deux analyses (par habitant ; accès rural, Banque mondiale), divergence expliquée, conclusion par dimension, pas d’addition des zones | §4.6 | Équipe, 2026-10-07 |
| ✅ **Écarts 29 et 30** : cibles de REC-F3 et REC-S1, déclarées comme les points c et d le prévoient | §11 | Équipe, 2026-10-07 |
| ✅ **Écarts 31 et 32** : définition par dimension ; O4-E1, déclaré après un calcul exploratoire | §4.6, §11 | Équipe, 2026-10-07 |
| ✅ **Règle « Haute » étendue au cumul par zone** : la Centrale, seule zone en retard sur la route et la formation | §4.6, §5.1, §11 (écart 27) | Équipe, 2026-10-07 |
| ✅ **Mise en œuvre par trois recommandations** : REC-Z3 (Centrale, cumul, Haute), REC-Z1 (Plateaux, route), REC-Z2 (Savanes et Maritime hors Grand Lomé, formation), au lieu de passer REC-Z1 et REC-Z2 en « Haute » | §4.6, §6 | Équipe, 2026-10-07 |
| ✅ **Pas de cible d’accès** pour les recommandations de zone : l’accès rural sert de contexte et de suivi ; la cible reste l’entretien (14,35 %) | §4.6 | Équipe, 2026-10-07 |
| ✅ **WorldPop** : approche uniforme gardée, en C ; limite écrite dans les réserves et la page Méthodologie ; calcul avec la grille renvoyé à l’annexe A1 | §4.6, §10 | Équipe, 2026-10-07 |
| ✅ **Onglet « Actions par zone »** : 39 fiches préfectures, 7e onglet ; préfectures sans levier en « Aucune action » | §4.7, §6, §6.2 | Équipe, 2026-10-07 |
| ✅ **`prefectures_10.csv`** remplace `territoires_10.csv` | §1, §8 | Équipe, 2026-10-07 |
| ✅ **Règle des codes** pour toutes les pages, transmise au 11 ; niveaux de preuve A, B, C permis, avec leur légende | §10 | Équipe, 2026-10-07 |
| ✅ **Seuil de l’accès rural** : médiane des zones ; Savanes en cas limite, signalé au 13 | §4.6, §10 | Équipe, 2026-10-07 |
| ✅ **Points de vigilance** : REC-Z3 présentée comme un ordre de passage ; contrôles « pas de double compte » et « style des fiches » ; onglet de zone court, analyses dans la page Méthodologie ; énoncé, écart 32 et Savanes transmis au 13 | §4.6, §6, §9, §10 | Équipe, 2026-10-07 |
| ✅ **Plan validé** : 15 recommandations, 39 fiches, 4 fichiers | Tout le document | Équipe, 2026-10-07 |
| ✅ **`zones_10.csv`** ajouté (5e fichier) : le tableau de bord (11) affiche l’accès rural et les km par état, par zone, sans agréger lui-même ; contrôlé par 10-14 | §1, §8, §9 | Équipe, 2026-10-07 |
| ✅ **Champs de R-18 en clair dans `cartes_10.csv`** : acteur, indicateur de suivi, niveau de preuve, réserve, pour que chaque carte les affiche sans code (R-18 est une règle d’affichage) ; relus par le contrôle de style | §8 | Équipe, 2026-10-07 |
| ✅ **Résultats** : `recommandations_10.py` exécuté ; 13 contrôles conformes sur 13, puis 14 avec la table des zones ; fichiers reproductibles. `prefectures_10.csv` a 25 colonnes : le nombre de tronçons parmi les 10 plus dégradés, et les blocs « Réseau » et « Formation » des fiches, produits par le script | §8, §9 | Exécution, 2026-10-07 |
| ✅ **Gel du 10 en v1.0** : 14 contrôles conformes sur 14 ; fichiers reproductibles ; plus aucun point à valider | Tout le document | Équipe, 2026-10-07 |
