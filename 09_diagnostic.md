# 09 — Diagnostic

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-06 — **Statut :** **figé** le 2026-10-06
**Sources :** `01_problem_definition.md` (figé), `02_decision_matrix.xlsx` (v1.1, figé), `03_data_inventory.md` à `08_priorisation.md` (figés), `data/analysis/06_exploration/`, `data/analysis/07_indicateurs/`, `data/analysis/08_priorisation/`

> **Question du 09 :** pourquoi ces territoires sont-ils en tête, et que disent les hypothèses du 02 ?
>
> Le 09 couvre l’étape 10 de la procédure : passer de « A est au rang 1 » à « A cumule… ». Il vérifie les chiffres de l’énoncé, tranche les hypothèses du 02 avec leurs critères, lit les 6 taux de l’énoncé, et écrit une phrase de diagnostic par territoire en tête.
>
> Le 09 décrit ; il ne recommande pas (10). Une coïncidence n’est pas une cause.
>
> Chaque chiffre cité vient de `data/analysis/09_diagnostic/`, écrit par `diagnostic_09.py` (R-19). Les critères des hypothèses sont ceux du 02, fixés avant les données (R-20).
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §11.

---

## Point de départ : le 08 et le 07

**Ce que le 08 transmet** (08 §11) :
- les 10 premières préfectures, dont les 5 qui cumulent les deux déficits : Danyi, Blitta, Agou, Tchamba, Bassar ;
- le volume derrière chaque taux (Danyi : 49,8 km évalués) ;
- l’écart entre les tués déclarés et l’estimation de l’OMS (SE-03) ;
- la Centrale, en tête des zones et des régions.

**Ce que le 07 transmet** (07 §9) : les 6 taux de l’énoncé, pour comparer la lecture par habitant et la lecture par véhicule (01 §3.2).

**Ce que le 02 demande au 09** (`02_Hypotheses`) : 17 hypothèses, chacune avec son critère.
- **S1 à S5** vérifient les chiffres de l’énoncé.
- **H1 à H12** testent des écarts, des liens et un cumul.

---

## 1. Objectif du 09

Dire ce que chaque territoire en tête cumule, et ce que les données confirment ou non de l’énoncé et des hypothèses.

**Ce que le 09 apporte à chaque objectif du projet :**

| Objectif | Ce que le 09 en fait |
| -------- | -------------------- |
| O1 Mobilité | S1 (quadruplement en 20 ans), S2 (porté par les motos), H1 (écart immatriculations / permis des motos) |
| O2 Sécurité | S3 (7 500 accidents et 683 morts en 2022), S4 (les accidents augmentent), H6 et les 6 taux, H2 sur les tués ; écart aux tués estimés par l’OMS |
| O3 Réseau | S5 (entretien inégal selon les régions), H5 sur sa partie réseau : le corridor de la RN1 |
| O4 Couverture | H8 (auto-écoles concentrées dans les villes) |
| O5 Recommandations | Une phrase par préfecture en tête et par zone ; H9 ; ce que chaque verdict permet ou interdit au 10 |

**Sorties**, dans `data/analysis/09_diagnostic/` :
1. `hypotheses_09.csv` : une ligne par hypothèse (S1 à S5, H1 à H12) : critère du 02, mesure, verdict, raison, conséquence du 02, niveau ;
2. `taux_09.csv` : les 6 taux de l’énoncé, moyenne des 3 premières et des 3 dernières années, sens, avec la fourchette du parc ;
3. `diagnostic_09.csv` : une ligne par territoire diagnostiqué : les faits qui fondent sa phrase (§6) ;
4. `controles_09.csv` : les contrôles du §8.

**Règles :**
- Les sorties du 06, du 07 et du 08 ne sont jamais modifiées.
- Une hypothèse se tranche avec le critère du 02, lu dans `02_Hypotheses.csv`. Le verdict est l’un de : confirmée, infirmée, nuancée ou indéterminée (seulement quand le 02 prévoit ces cas), non testable (avec la raison).
- Un diagnostic décrit ce qu’un territoire cumule ; il ne dit pas pourquoi (aucune lecture causale).
- Le volume est toujours écrit à côté du taux.
- Aucune recommandation (10).

**Le 09 est terminé quand :**
- les 17 hypothèses ont un verdict ;
- les 6 taux sont comparés ;
- chaque préfecture en tête et chaque zone a sa phrase ;
- les contrôles du §8 sont conformes.

---

## 2. Méthode et outils

**Outils.** Ceux des étapes précédentes, dans `.venv` : pandas, numpy. Aucun nouveau paquet.

**Script** : `scripts/diagnostic_09.py`. Il lit :
- le 06 : `signaux_06.csv` ; `prefectures_06.csv`, pour la classe PA-03 (H8) et les quarts ;
- le 07 : `indicateurs_07.csv` ;
- le 08 : `classement_08.csv`, pour les rangs, les leviers, les écarts à la cible et la présence dans les tests (colonne qui résume `sensibilite_08.csv`) ; `regions_08.csv`, pour les zones, les régions et le pays ;
- le 02 : `02_Hypotheses.csv` ;
- `D4_etat_troncons.csv`, pour les tronçons critiques (§6) et le corridor de H5 ;
- ce document, pour vérifier les nombres des phrases du §6 (contrôle 8-07).

**Rédaction.** Les phrases de diagnostic (§6) sont écrites dans ce document, à partir de `diagnostic_09.csv` : un diagnostic est un texte. Chaque chiffre d’une phrase se relit contre ce fichier.

✅ **Ni figure ni notebook au 09.** Le tableau de bord (11) restituera les verdicts et les phrases.

**Ordre de travail :** énoncé (§3) ; 6 taux (§4) ; hypothèses (§5) ; phrases (§6) ; contrôles (§8).

**Pour tout reproduire :** la chaîne du 08, puis `diagnostic_09.py`.

---

## 3. Vérifier l’énoncé (S1 à S5)

| Code | Énoncé | Critère du 02 | Mesure au 09 |
| ---- | ------ | ------------- | ------------ |
| S1 | Les immatriculations ont plus que quadruplé en 20 ans | Multiplicateur I(n) / I(n−20) ≥ 4 | O1-03, ensemble (§3, point a) |
| S2 | Cette hausse est portée par les motos | Contribution des motos à la hausse > 50 % | (motos(n) − motos(n−20)) / (total(n) − total(n−20)), même n que S1 |
| S3 | Plus de 7 500 accidents et 683 morts en 2022 | Écart ≤ 5 % sur les deux chiffres | O2-01 de 2022 face à 7 500 et 683 |
| S4 | Les accidents augmentent | Volume et taux par habitant en hausse ; nuancée si le volume monte mais qu’un des taux baisse | Moyennes 2010–2012 et 2022–2024 : volume, O2-02, O2-04 (§4) |
| S5 | Le réseau est inégalement entretenu selon les régions | Écart ≥ 15 points entre la zone la plus dégradée et la moins dégradée | O3-02 des 6 zones (`regions_08.csv`) |

**Point à valider :**

**a) L’année n de S1 et S2.** Le 02 ne la fixe pas. Le 09 retient **2022, l’année des chiffres de l’énoncé** : ses accidents et ses morts sont de 2022. 2023 et 2024 sont écrits à côté. Le multiplicateur de 2024 part de 2004, une année de rupture de la série (04) : il ne se compare pas aux autres. Ces valeurs sont déjà connues du 07 : le choix suit l’énoncé, pas le résultat, et les trois années restent visibles.

**Résultat : l’énoncé est vérifié, sauf « les accidents augmentent », qui est nuancé.**

| Code | Verdict | Mesure |
| ---- | ------- | ------ |
| S1 | Confirmée | Multiplicateur de 4,56 en 2022 (face à 2002) ; 4,53 en 2023 ; 1,83 en 2024, depuis 2004, année de rupture |
| S2 | Confirmée | Les motos font 80,6 % de la hausse de 2002 à 2022 : 59 007 des 73 217 immatriculations de plus |
| S3 | Confirmée | 2022 : 7 507 accidents constatés (+0,1 %) et 683 tués (+0,0 %) |
| S4 | Nuancée | Les accidents constatés montent (6 381,7 puis 6 980,7 par an), mais les tués baissent par habitant et par véhicule (§4) |
| S5 | Confirmée | 32,6 points entre la Centrale (40,3 % de km en mauvais état) et le Grand Lomé (7,7 %) |

---

## 4. Les 6 taux de l’énoncé (H6, S4)

Le 01 §3.2 demande « deux lectures du même risque, toutes deux exigées ». Le 07 a calculé les 6 taux ; le 09 compare leurs évolutions.

| Mesure | Pour 100 000 habitants | Pour 10 000 véhicules |
| ------ | ---------------------- | --------------------- |
| Accidents constatés | O2-03 | O2-E2 (complément, écart 22) |
| Blessés | O2-E1 (complément) | O2-E3 (complément) |
| Tués | O2-02 | O2-04 |

**Méthode du 02** (H6, S4) : la moyenne des 3 premières années (2010–2012) face à celle des 3 dernières (2022–2024).
- **Fourchette du parc.** Un taux par véhicule se calcule trois fois : valeur centrale, parc haut, parc bas. Son sens n’est établi que si les trois vont dans le même sens. Sinon, il est « indéterminé ».
- **H6** (tués seulement) : confirmée si O2-02 et O2-04 évoluent en sens opposés sur toute la fourchette ; infirmée s’ils vont dans le même sens ; indéterminée si la fourchette ne tranche pas.
- **Les messages sont ceux du 02.** Si le volume monte et que le taux par véhicule baisse, le message est « plus de véhicules », pas « une route plus dangereuse » (S4). Le 09 n’écrit ni « amélioration réelle » ni « dégradation réelle » : ce sont des accidents déclarés.
- ✅ **Les 3 compléments** (O2-E1 à O2-E3, écart 22) se lisent à côté des 3 taux du 02, de la même façon, à titre descriptif. Ils n’entrent dans aucun verdict : le 02 ne les teste pas.
- **Les années atypiques** restent celles du 06 [SIG-12 à SIG-14], avec leurs coïncidences de la chronologie, sans lecture causale.

**Tués déclarés et estimation de l’OMS.** En 2021, le taux déclaré (8,62 pour 100 000 habitants) est sous l’estimation de l’OMS pour le Togo (22,7 ; 08 §3.1). Le 09 écrit le rapport entre les deux. Il rappelle que l’estimation n’est jamais une correction des tués déclarés (D9), et que la limite de S3 et la réserve de P4 visent la sous-déclaration. Il ne corrige aucun chiffre.

**Résultat :**

| Mesure | Volume par an | Pour 100 000 habitants | Pour 10 000 véhicules (fourchette du parc) |
| ------ | ------------- | ---------------------- | ------------------------------------------ |
| Accidents constatés | 6 381,7 → 6 980,7 (+9,4 %) | 101,90 → 84,60 (−17,0 %) | 142,95 → 100,29 (−29,8 %), baisse sur toute la fourchette |
| Blessés | 8 402,0 → 9 500,3 (+13,1 %) | 134,30 → 115,10 (−14,3 %) | 189,13 → 136,29 (−27,9 %), baisse sur toute la fourchette |
| Tués | 654,0 → 608,7 (−6,9 %) | 10,45 → 7,38 (−29,4 %) | 14,71 → 8,76 (−40,4 %), baisse sur toute la fourchette |

Moyennes de 2010–2012, puis de 2022–2024. Les lignes des accidents et des blessés par véhicule, et des blessés par habitant, sont les compléments (écart 22) : descriptifs, sans verdict.

- **H6 : infirmée.** Les tués baissent par habitant et par véhicule, sur toute la fourchette du parc : les deux lectures vont dans le même sens.
- **S4 : nuancée.** Les accidents constatés et les blessés montent en volume. Les 6 taux baissent : les volumes montent moins vite que la population et que le parc. C’est le cas que le 02 décrit : le message est « plus de véhicules », pas « une route plus dangereuse ».
- **Tués déclarés et OMS :** en 2021, l’estimation de l’OMS (22,7 pour 100 000 habitants) vaut 2,63 fois le taux déclaré (8,62). Les baisses ci-dessus portent sur les tués déclarés.

---

## 5. Hypothèses H1 à H12

| Code | Énoncé (02) | Testable au 09 ? | Mesure ou raison |
| ---- | ----------- | ---------------- | ---------------- |
| H1 | L’écart immatriculations / permis est plus marqué pour les motos | Oui | O1-09 en cumul 2007–2024, par catégorie : celui des motos (A) est-il le plus élevé ? |
| H2 | Les motos sont surreprésentées parmi les véhicules impliqués et les victimes | **En partie, par écart (26)** | Les véhicules impliqués n’existent pas (O2-08, écart 2). Les tués par type d’usager existent pour 2021 (O2-09) : point b |
| H3 | Réseau dégradé, taux d’accidents plus élevé | Non | Pas d’accidents par territoire (écart 1) |
| H4 | Peu d’auto-écoles, taux d’accidents plus élevé | Non | Idem |
| H5 | Les poids lourds en transit pèsent sur l’accidentalité et l’usure de l’axe nord-sud | Non : la condition sur les accidents manque | La part des poids lourds dans les accidents n’existe pas (écart 2). La condition réseau est mesurée et écrite à part : point c |
| H6 | Taux par habitant et par véhicule en sens inverse | Oui | §4 |
| H7 | Le risque varie fortement d’un territoire à l’autre | Non | Pas d’accidents par territoire (écart 1) |
| H8 | Les auto-écoles sont concentrées dans les grandes villes | Oui | Part des auto-écoles comptées (R-12) dans les préfectures urbaines (PA-03), face à leur part de la population ; confirmée si ≥ 1,5 fois. Les recensées sont écrites à côté |
| H9 | Certains territoires cumulent mobilité, risque, réseau dégradé et formation faible | **Non** | Le cumul complet (SE-10) exige le risque (08 §3.1). Le cumul des deux dimensions mesurées (5 préfectures) est écrit à côté, sans valoir verdict |
| H10 | Plus d’accidents en saison des pluies et aux fêtes | Non | Pas de mois (écart 2) |
| H11 | Le Grand Lomé concentre les accidents en volume, le risque est plus élevé ailleurs | **Non** | Ni la part du Grand Lomé dans les accidents ni son taux ne sont connus : les accidents sont nationaux (écart 1) |
| H12 | Les jeunes conducteurs sont surreprésentés | Non | Pas d’âge des conducteurs (écart 2) |

**Points à valider :**

**b) H2 sur les tués (écart 26).** La part des deux et trois-roues motorisés parmi les tués de 2021 (O2-09, OMS) est rapportée à la part des motos dans le parc estimé de 2021 (O1-05).
- **Fourchette :** cette part se calcule aux deux bornes et à la valeur centrale du parc.
- **Verdict, règle de SE-09 :** au-dessus de 1 sur toute la fourchette, H2 est confirmée pour les tués ; en dessous de 1 partout, infirmée ; entre les deux, indéterminée.
- **Niveau :** C.
- **Limites :** la catégorie de l’OMS inclut les trois-roues ; les véhicules impliqués restent non testés.

**c) H5, partie réseau.** Le corridor (PA-07) est la RN1, du port de Lomé à la frontière du Burkina Faso. Ce sont 6 tronçons du relevé : les 2 de l’axe Lomé–Amakpapé (04), puis ceux dont le nom porte la RN1 comme route propre, sans les bretelles. La part de km en mauvais état du corridor est comparée à celle du pays (21,2 %, `regions_08.csv`). H5 reste non testable : cette partie se lit seule.

**d) H9 non testable.** Les 5 préfectures qui cumulent réseau dégradé et formation faible sont un cumul partiel. Le 02 ne le compte pas comme H9.

**Résultat :**

| Code | Verdict | Mesure ou raison |
| ---- | ------- | ---------------- |
| H1 | Confirmée | En cumul 2007–2024, 40,20 immatriculations de motos par permis A ; les autres catégories vont de 0,37 (D) à 2,33 (C) |
| H2 | Confirmée, sur les tués seulement (écart 26) | 60 % des tués de 2021 sont des usagers de deux et trois-roues motorisés, pour 54,7 % à 59,7 % de motos dans le parc estimé. Indice de 1,01 à 1,10 : au-dessus de 1 sur toute la fourchette, de peu. Niveau C |
| H3, H4, H7 | Non testables | Pas d’accidents par territoire (écart 1) |
| H5 | ✅ **Infirmée** | La condition réseau est mesurée : le corridor de la RN1 (6 tronçons, 667,7 km) a 18,0 % de km en mauvais état, sous le pays (21,2 %). Le critère du 02 est « infirmée si une des deux conditions n’est pas remplie » : cette condition non remplie suffit, quelle que soit la condition sur les accidents (non mesurée, écart 2) |
| H6 | Infirmée | §4 |
| H8 | Confirmée | Les 4 préfectures urbaines (Agoè-Nyivé, Golfe, Kloto, Kozah) ont 84,8 % des auto-écoles comptées pour 32,3 % de la population : 2,62 fois. Recensées : 2,57 fois |
| H9 | Non testable | Le cumul complet exige le risque. Cumul partiel, sans valeur de verdict : Danyi, Blitta, Agou, Tchamba et Bassar, 641 955 habitants |
| H10 | Non testable | Pas de mois (écart 2) |
| H11 | Non testable | Ni la part du Grand Lomé dans les accidents ni son taux ne sont connus (écart 1) |
| H12 | Non testable | Pas d’âge des conducteurs (écart 2) |

**H5 diffère du plan.** Le plan la disait non testable, faute de la condition sur les accidents. Mais le critère du 02 est « infirmée si une des deux conditions n’est pas remplie » : une condition réseau non remplie suffit, quelle que soit l’autre. Le script applique ce critère ; il aurait écrit « non testable » si le corridor avait dépassé la moyenne du pays.

**Ce que cela change pour le 10.** Le 10 ne fonde aucune recommandation sur une hypothèse non testable. Il reprend la conséquence que le 02 attache à chaque verdict (`02_Hypotheses`, « Conséquence pour la décision »). Le rapport final (13) dit quelles hypothèses restent ouvertes, et quelle donnée les rendrait testables.

---

## 6. Diagnostic par territoire

**Territoires diagnostiqués :**
- les 10 premières préfectures du 08 ;
- ✅ **Mô**, hors classement mais seule préfecture sans route classée. Sa phrase porte sur l’absence de route (desserte nulle) et sur la formation, pas sur l’état du réseau ;
- les 6 zones ;
- ✅ **les 5 régions**, par agrégation des zones (R-02). Plateaux, Centrale, Kara et Savanes sont à la fois zone et région : leur phrase vaut pour les deux. Seule la Maritime diffère : la vue en 5 régions inclut le Grand Lomé, que la vue en 6 zones sépare. Elle a sa propre phrase, qui tient compte des deux lectures.

**Ce qui fonde une phrase** (`diagnostic_09.csv`), pour chaque territoire :
- O3-02 avec ses km évalués ; O4-05 avec ses auto-écoles comptées et recensées ; O4-03 ; O4-08 ; la population ;
- ✅ **les tronçons critiques (O3-05) qui traversent la préfecture** : leur nombre (`D4_etat_troncons.csv`, « Préfectures traversées ») et les km en mauvais état de la préfecture (O3-01). Un tronçon qui traverse plusieurs préfectures compte dans chacune ;
- la position de chaque valeur parmi les 39 préfectures, dans les quarts du 06 (haut, milieu, bas) ;
- les leviers, l’écart à la cible (O5-04) et la présence parmi les 10 premières dans les tests du 08 ;
- les signaux du 06 qui le nomment.

**Forme de la phrase**, sur le modèle de la procédure : « Blitta cumule 68,2 % de km en mauvais état sur 101,1 km évalués, aucune auto-école comptée pour 163 272 habitants, et… ».
- La phrase dit ce que le territoire cumule et sa population.
- ✅ **Desserte et distance**, selon une règle fixe : la desserte (O4-03) est citée si la préfecture franchit SE-06 ; la distance (O4-08), si son point de départ est au-delà de SE-08 (10 km). Elles restent toutes deux dans `diagnostic_09.csv`.
- Elle se termine par sa fiabilité : présence dans les tests, niveau C.

**Ce que les données ne disent pas, pour tous les territoires.** Il n’y a pas d’accidents par territoire (écart 1), et l’activité des auto-écoles n’est pas connue (écart 13). L’état du réseau date du relevé de 2020 (C). Cette limite est écrite une fois, ici, et pas dans chaque phrase.

**Résultat : préfectures en tête**, dans l’ordre du 08. Distance : du point de départ à l’auto-école comptée la plus proche.

1. **Danyi** cumule 100 % de km en mauvais état sur 49,8 km évalués, traversés par 3 tronçons critiques, et aucune auto-école, ni comptée ni recensée, pour 40 240 habitants, à 12,9 km de la plus proche. 6 tests sur 6.
2. **Blitta** cumule 68,2 % de km en mauvais état sur 101,1 km évalués (4 tronçons critiques) et aucune auto-école comptée pour 163 272 habitants (2 recensées, non agréées), à 25,9 km de la plus proche. 6 tests sur 6.
3. **Agou** cumule 40,0 % de km en mauvais état sur 124,1 km évalués (5 tronçons critiques) et aucune auto-école comptée pour 85 793 habitants (1 recensée, non agréée), à 11,0 km de la plus proche. 6 tests sur 6.
4. **Tchamba** cumule 34,0 % de km en mauvais état sur 120,3 km évalués (1 tronçon critique) et aucune auto-école comptée pour 200 585 habitants (2 recensées, non agréées), à 31,1 km de la plus proche. 6 tests sur 6.
5. **Bassar** cumule 28,0 % de km en mauvais état sur 167,5 km évalués (1 tronçon critique) et aucune auto-école comptée pour 152 065 habitants (2 recensées, non agréées), à 47,5 km de la plus proche. 6 tests sur 6.
6. **Oti** n’a aucune auto-école comptée pour 124 848 habitants (3 recensées, non agréées), à 62,0 km de la plus proche ; son réseau (21,1 % en mauvais état sur 140,6 km) reste sous le seuil. 6 tests sur 6.
7. **Bas-Mono** n’a aucune auto-école comptée pour 94 860 habitants (1 recensée, non agréée), à 31,2 km de la plus proche, et sa desserte est faible : 3,68 km de routes pour 10 000 habitants. Réseau : 21,1 % sur 35,8 km. 6 tests sur 6.
8. **Est-Mono** n’a aucune auto-école, ni comptée ni recensée, pour 164 460 habitants, à 27,4 km de la plus proche. Réseau : 17,2 % sur 110,7 km. 4 tests sur 6.
9. **Oti-Sud** n’a aucune auto-école, ni comptée ni recensée, pour 150 376 habitants, à 84,0 km de la plus proche, valeur hors des bornes au 06 [SIG-25]. Réseau : 14,4 % sur 131,7 km. 4 tests sur 6.
10. **Tchaoudjo** cumule 36,9 % de km en mauvais état sur 125,7 km évalués (3 tronçons critiques) pour 240 360 habitants ; sa formation n’est pas en déficit (2 auto-écoles comptées, 0,83 pour 100 000 habitants). 3 tests sur 6 : la moins sûre des 10.

**Mô**, hors classement, n’a aucune route classée : ni état, ni km évalué, et une desserte nulle. Elle n’a aucune auto-école, ni comptée ni recensée, pour 52 448 habitants, à 52,2 km de la plus proche.

**Résultat : zones**, dans l’ordre du 08.

1. **Centrale** est la seule zone au-dessus de la médiane pour le réseau et en dessous pour la formation : 40,3 % de km en mauvais état sur 437,2 km évalués, et 4 auto-écoles comptées pour 795 529 habitants (0,50 pour 100 000). 4 de ses 5 préfectures reçoivent le levier réseau (113,6 km à remettre en état), 3 le levier formation (6 auto-écoles).
2. **Savanes** a la formation et la desserte sous la médiane : 4 auto-écoles comptées pour 1 143 520 habitants (0,35 pour 100 000), 4,62 km de routes pour 10 000 habitants. 5 de ses 7 préfectures reçoivent le levier formation (9 auto-écoles), aucune le levier réseau.
3. **Plateaux** a le réseau au-dessus de la médiane : 28,0 % de km en mauvais état sur 965,6 km évalués, traversés par 23 tronçons critiques. Pour 1 635 946 habitants, 6 de ses 12 préfectures reçoivent le levier réseau (150,5 km), 7 le levier formation (12 auto-écoles).
4. **Maritime hors Grand Lomé** a la formation et la desserte sous la médiane : 5 auto-écoles comptées pour 1 346 615 habitants (0,37 pour 100 000), 3,51 km de routes pour 10 000 habitants. 3 de ses 6 préfectures reçoivent le levier formation (6 auto-écoles).
5. **Kara** a le réseau au-dessus de la médiane : 15,2 % sur 694,5 km évalués. Pour 985 512 habitants, 2 de ses 7 préfectures reçoivent le levier réseau (37,3 km), 5 le levier formation (8 auto-écoles).
6. **Grand Lomé** a le réseau le moins dégradé (7,7 %) et la meilleure offre (103 auto-écoles comptées, 4,71 pour 100 000 habitants) ; seule sa desserte est sous la médiane (0,74 km pour 10 000 habitants), pour 2 188 376 habitants.

**Région Maritime** (5e des 5 régions) : avec le Grand Lomé, elle ne franchit que le seuil de la desserte (1,79 km pour 10 000 habitants). Son offre (3,06 auto-écoles pour 100 000 habitants) cache celle de la Maritime hors Grand Lomé (0,37). Les 4 autres régions sont les zones du même nom.

---

## 7. Écarts au 02

Déclarés avant le calcul (R-20). Les écarts 1 à 19 sont ceux du 04, 20 à 22 ceux du 07, 23 à 25 ceux du 08. Le 02 n’est pas modifié.

| N° | Écart | Traitement | Raison |
| -- | ----- | ---------- | ------ |
| 26 | Le 02 teste H2 par O2-08 (part des motos parmi les véhicules impliqués), qui n’est pas calculable (écart 2) | H2 testée sur les tués seulement : la part des deux et trois-roues motorisés parmi les tués de 2021 (O2-09), rapportée à la part des motos dans le parc estimé, sur toute la fourchette (règle de SE-09) | L’énoncé insiste sur les motos, et H2 dit « parmi les véhicules impliqués et les victimes ». Les victimes sont mesurées pour une année. Le verdict ne porte que sur elles, en C |

---

## 8. Validation

| Contrôle | Attendu |
| -------- | ------- |
| Hypothèses | 17 lignes (S1 à S5, H1 à H12) ; critères identiques à `02_Hypotheses.csv` ; un verdict permis par le 02 pour chacune ; une raison pour chaque « non testable » |
| Concordance | Les valeurs reprises sont celles du 07 et du 08 (`indicateurs_07.csv`, `classement_08.csv`, `regions_08.csv`) |
| 6 taux | 6 lignes ; moyennes sur 3 années complètes ; taux par véhicule aux trois valeurs du parc |
| H2 (écart 26) | Part des motos dans le parc aux deux bornes et à la valeur centrale ; verdict selon la règle de SE-09 |
| H5, partie réseau | 6 tronçons, de Lomé à la frontière du Burkina Faso ; sommes de km égales au relevé |
| Diagnostic | Une ligne par territoire diagnostiqué (10 préfectures, Mô, 6 zones, la région Maritime) ; tronçons critiques recomptés depuis le relevé |
| Phrases du §6 | Vérifiées par le script : chaque nombre vaut, à son arrondi, une valeur de `diagnostic_09.csv` pour le territoire de la phrase ou un territoire qu’elle nomme ; rangs et tests vérifiés |
| Reproductibilité | Deux exécutions donnent les mêmes fichiers |

**Résultat : 7 contrôles conformes sur 7** (`controles_09.csv`).
- **Hypothèses :** 17 verdicts, tous permis par le 02, avec des critères identiques : 7 confirmées, 2 infirmées, 1 nuancée, 7 non testables, chacune avec sa raison.
- **Concordance :** les 77 valeurs de préfecture reprises du 08 sont identiques, et les moyennes de taux sont recalculées depuis le 07.
- **Diagnostic et corridor :** les 49 tronçons critiques sont recomptés depuis le relevé, comme au 07. Le corridor fait 667,73 km, par état comme au total.
- **Phrases :** les 105 nombres des 18 phrases du §6 sont vérifiés par le script (8-07). Testé sur une copie faussée du document, le contrôle signale chaque nombre changé.
- **Reproductibilité :** deux exécutions donnent des fichiers identiques à l’octet près. Les sorties du 06, du 07 et du 08 ne sont pas modifiées.

---

## 9. Fichiers produits

**Dans `data/analysis/09_diagnostic/`**, écrits par `diagnostic_09.py` :

| Fichier | Contenu |
| ------- | ------- |
| `hypotheses_09.csv` | Par hypothèse : code, énoncé, critère du 02, indicateurs, mesure, valeurs, verdict, raison, conséquence du 02, niveau |
| `taux_09.csv` | Par taux : mesure, dénominateur, moyenne 2010–2012, moyenne 2022–2024, variation, sens ; aux trois valeurs du parc pour les taux par véhicule ; niveau |
| `diagnostic_09.csv` | Par territoire : valeurs, positions dans les quarts du 06, volumes, tronçons critiques, leviers, écart à la cible, présence dans les tests, signaux du 06 |
| `controles_09.csv` | Les contrôles du §8 |

---

## 10. Suite

- **Transmis au 10** : la conséquence que le 02 attache à chaque verdict (`02_Hypotheses`).

  | Verdict | Conséquence du 02 pour le 10 |
  | ------- | ---------------------------- |
  | S1 confirmée | La page d’accueil affiche le multiplicateur mesuré (4,56 en 2022) |
  | S2 confirmée | La moto est la catégorie de référence de O1 et de H1 |
  | S3 confirmée | Le tableau de bord affiche le chiffre de la source, avec sa définition |
  | S4 nuancée | Le message est « plus de véhicules », pas « une route plus dangereuse » |
  | S5 confirmée | L’entretien se cible par territoire, pas seulement par tronçon |
  | H1 confirmée | Le levier formation cible d’abord le permis moto |
  | H2 confirmée, sur les tués (C) | Des mesures ciblées sur les motos (casque, permis moto) deviennent recommandables, en C. ✅ La surreprésentation est faible (indice de 1,01 à 1,10), mais elle tient sur toute la fourchette : le 10 l’écrit ainsi |
  | H5 infirmée | Le corridor de la RN1 ne devient pas une cible commune d’entretien et de contrôle |
  | H6 infirmée | La conséquence prévue (« la hausse du risque vient de l’exposition ») ne s’applique pas |
  | H8 confirmée | Le déficit de formation est rural : ouverture d’auto-écoles hors des villes |
  | H3, H4, H7, H9 à H12 non testables | Aucune recommandation ne s’y appuie ; le 13 dit quelle donnée les rendrait testables |

  Le 10 part aussi des phrases du §6.

- ✅ **Transmis au 13 : la donnée qui rendrait chaque hypothèse testable.**

  | Hypothèse | Donnée manquante |
  | --------- | ---------------- |
  | H3, H4, H7, H11 | Accidents et tués par préfecture |
  | H9 | Accidents par préfecture (risque) ; immatriculations au lieu d’usage, si la mobilité est retenue (`05_Priorisation`) |
  | H10 | Mois des accidents |
  | H12 | Âge des conducteurs impliqués |
  | H2, pour les véhicules | Catégorie des véhicules impliqués (O2-08) |
- **10 — Recommandations** (étape 11) : par levier, la chaîne fait, écart, impact, action, priorité, reliée aux phrases du §6 ; cibles en habitants (O5-04) ; vérification avant investissement (R-17) ; P5 au national.
- **Puis** : 11 Tableau de bord, 12 Validation, 13 Rapport final, avec les hypothèses restées ouvertes.

---

## 11. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 09** : un script, quatre fichiers ; phrases écrites dans le document ; ni figure ni notebook | §1, §2, §6 | Équipe, 2026-10-06 |
| ✅ **S1 à S5 testées** avec les critères du 02 | §3 | Équipe, 2026-10-06 |
| ✅ **Année de S1 et S2 : 2022**, celle de l’énoncé ; 2023 et 2024 à côté | §3 a | Équipe, 2026-10-06 |
| ✅ **6 taux** : moyennes 2010–2012 et 2022–2024 ; sens établi sur toute la fourchette du parc ; messages du 02 seulement | §4 | Équipe, 2026-10-06 |
| ✅ **Écart 26** : H2 testée sur les tués de 2021 | §5 b, §7 | Équipe, 2026-10-06 |
| ✅ **H5** non testable ; partie réseau mesurée sur le corridor de la RN1 (6 tronçons) | §5 c | Équipe, 2026-10-06 |
| ✅ **H8** sur les auto-écoles comptées ; recensées à côté | §5 | Équipe, 2026-10-06 |
| ✅ **H9 et H11 non testables** ; cumul partiel de H9 écrit à côté | §5 d | Équipe, 2026-10-06 |
| ✅ **Diagnostic** : 10 préfectures et 6 zones, une phrase chacune ; limites communes écrites une fois | §6 | Équipe, 2026-10-06 |
| ✅ **Compléments du plan** : Mô diagnostiquée ; les 5 régions couvertes ; tronçons critiques par préfecture ; desserte et distance citées selon SE-06 et SE-08 ; fichiers du 08 lus nommés | §2, §4, §6 | Équipe, 2026-10-06 |
| ✅ **H5 infirmée** par le critère du 02 (une condition non remplie suffit), au lieu de « non testable » prévu au plan | §5 | Équipe, 2026-10-06 |
| ✅ **Résultats** : 17 verdicts, 6 taux, phrases de 10 préfectures, de Mô, des 6 zones et de la région Maritime ; 6 contrôles conformes sur 6 | §3 à §6, §8, §10 | Équipe, 2026-10-06 |
| ✅ **Précisions** : H5 reformulée (la condition réseau non remplie infirme) ; H2 faible écrite au 10 ; données manquantes transmises au 13 ; phrases vérifiées par script (8-07) | §5, §8, §10 | Équipe, 2026-10-06 |
