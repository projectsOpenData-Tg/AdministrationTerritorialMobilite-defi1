# 08 — Priorisation

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-06 — **Statut :** **figé** le 2026-10-06
**Sources :** `01_problem_definition.md` (figé), `02_decision_matrix.xlsx` (v1.1, figé), `03_data_inventory.md` (v1.3, figé), `04_data_understanding.md` (v1.0, figé), `05_data_preparation.md` (v1.0, figé), `06_exploration.md` (v1.0, figé), `07_indicateurs.md` (v1.0, figé), `data/analysis/07_indicateurs/`

> **Question du 08 :** quelles préfectures et quelles régions sont prioritaires, sur quel levier, et le classement tient-il ?
>
> Le 08 couvre l’étape 9 de la procédure. Il applique les seuils de classement du 02, calcule le nombre de déficits (O5-01) et le rang de priorité (O5-02), ordonne les préfectures par levier, et teste la robustesse du classement.
>
> Le 08 classe ; il n’explique pas (09) et ne recommande pas (10).
>
> Chaque chiffre cité vient de `data/analysis/08_priorisation/`, écrit par `priorisation_08.py` (R-19). Toute décision de méthode est prise ici, avant de voir le classement (R-20).
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §12.

---

## Point de départ : le 07 et le 02

**Ce que le 07 transmet** (07 §9) :
- les dimensions par préfecture : O3-02 (38 préfectures ; Mô non défini), O4-05 (23 ex aequo à 0 [SIG-26]), O4-03, O3-06 ;
- O5-04, pour la cible : la formation suit la variante de l’écart 21, le réseau la formule du 02 ;
- O4-08 : 26 préfectures ont leur point de départ au-delà de SE-08 ;
- les 3 compléments (O2-E1 à O2-E3) restent hors du classement (écart 22).

**Ce que le 02 prévoit quand le risque n’existe qu’au national** (écart 1) :
- **Pas de classement territorial du risque** ; les recommandations s’organisent par levier (`05_Priorisation`, « Unité de classement » ; 03 §1).
- **O5-01 et O5-02 se calculent sans la dimension risque**, sur les dimensions mesurées par préfecture : réseau et formation (03 §4, 04 §8).
- ✅ **Ni P1 ni P2 sans O2-02.** Le risque reste « non déterminable » (P5) dans chaque préfecture. Le 08 attribue les leviers réseau et formation sans les nommer P1 ou P2 (07 §9).
- **P3, P4 et P6 exigent aussi O2-02** (`04_Profils`) : ils ne s’appliquent pas.

---

## 1. Objectif du 08

Ordonner les préfectures et les régions sur ce que les données mesurent par territoire, l’état du réseau et l’offre de formation, et dire si cet ordre tient.

**Ce que le 08 apporte à chaque objectif du projet :**

| Objectif | Ce que le 08 en fait |
| -------- | -------------------- |
| O1 Mobilité | Pas de dimension mobilité : les immatriculations sont nationales et comptées au lieu d’enregistrement (`05_Priorisation`, « Dimensions »). Elles restent affichées à part |
| O2 Sécurité | Le risque ne se classe pas par territoire (écart 1). SE-03 situe le taux national de tués face au repère de l’OMS. Le manque de données d’accidents par territoire relève de P5, au national |
| O3 Réseau | Dimension réseau : O3-02, seuil SE-04. Les tronçons critiques (O3-05) et les km à remettre en état (O5-04) des préfectures retenues |
| O4 Couverture | Dimension formation : O4-05, seuil SE-07. La desserte (O4-03, SE-06) et la distance (O4-08, SE-08) affichées à côté |
| O5 Recommandations | Rang de priorité, déficits, leviers par préfecture et par région, population concernée, robustesse. Les recommandations elles-mêmes sont au 10 |

**Sorties**, dans `data/analysis/08_priorisation/` :
1. `classement_08.csv` : une ligne par préfecture ;
2. `regions_08.csv` : une ligne par zone (6), par région (5) et pour le pays ; la ligne du pays porte SE-03 ;
3. `sensibilite_08.csv` : le rang de chaque préfecture dans chaque test ;
4. `controles_08.csv` : les contrôles du §9.

**Règles :**
- `data/processed/` et `data/analysis/07_indicateurs/` ne sont jamais modifiés.
- Les valeurs viennent de `indicateurs_07.csv` ; les seuils, de `03_Seuils.csv`.
- Un zéro est une valeur. O4-05 = 0 est défini : 0 auto-école comptée. Seul un rapport sans dénominateur est non défini (R-10) : O3-02 pour Mô.
- Une préfecture sans valeur sur une dimension retenue n’est pas classée ; elle est affichée à part, jamais comme favorable (`05_Priorisation`, « Valeurs manquantes »).
- Le classement porte sur les taux ; la population concernée est affichée à côté (« Intensité et volume »).
- Ni recommandation (10), ni lecture causale (09).

**Le 08 est terminé quand :**
- les seuils applicables sont appliqués, et les autres dits non applicables, avec la raison ;
- O5-01 et O5-02 sont calculés, et les préfectures ordonnées par levier ;
- la lecture par région est faite ;
- les tests de sensibilité sont faits et la stabilité est jugée ;
- les contrôles du §9 sont conformes.

---

## 2. Méthode et outils

**Outils.** Ceux des étapes précédentes, dans `.venv` : pandas, numpy. Aucun nouveau paquet.

**Script** : `scripts/priorisation_08.py`. Il lit `indicateurs_07.csv`, `03_Seuils.csv` et `D9_repere_oms.csv`, et écrit les quatre fichiers du §1.

**Ordre de travail :** seuils (§3) ; déficits et rang (§4) ; leviers (§5) ; régions (§6) ; sensibilité (§7) ; contrôles (§9).

✅ **Ni figure ni notebook au 08.** Le tableau de bord (11) restituera le classement à partir de `classement_08.csv`. Les contrôles du §9 vérifient les calculs.

**Pour tout reproduire :** la chaîne du 07, puis `priorisation_08.py`.

---

## 3. Seuils

### 3.1 Application

Un percentile se calcule comme au 06 (interpolation linéaire). Une préfecture franchit le seuil si sa valeur est ≥ (ou ≤) la valeur du percentile, **ex aequo compris**.

| Seuil | Indicateur | Règle du 02 | Au 08 |
| ----- | ---------- | ----------- | ----- |
| SE-01 | Transversal | 20 événements | Appliqué au 07 : au moins 470 tués par an au national |
| SE-02 | O2-02 | Tercile supérieur | **Non applicable** : O2-02 est national (écart 1) |
| SE-03 | O2-02 | Repère de l’OMS (D9) | Appliqué au national : O2-02 de 2021 face à l’estimation de l’OMS pour le Togo, et à la moyenne du Bénin, du Ghana et du Burkina Faso. Écrit sur la ligne du pays de `regions_08.csv`. Ne déclenche aucun profil |
| SE-04 | O3-02 | Préfecture : tercile supérieur ; zone : au-dessus de la médiane des 6 | Appliqué, sur les 38 préfectures où O3-02 est défini |
| SE-05 | O3-06 | Plus de 25 % non évalué : réseau non déterminable | Appliqué. D’après le 07, aucune préfecture ne dépasse 25 % ; Mô est non défini |
| SE-06 | O4-03 | Préfecture : tercile inférieur ; zone : sous la médiane | Appliqué, affiché à côté du classement ; ne déclenche aucun levier |
| SE-07 | O4-05 | Préfecture : tercile inférieur ; zone : sous la médiane | Appliqué, sur les 39 préfectures (§3.2 a) |
| SE-08 | O4-08 | 10 km | Appliqué au 07 |
| SE-09 | O2-08 | Indice > 1 | **Non applicable** : O2-08 n’est pas calculable (04 §8) |
| SE-10 | O5-01 | Toutes les dimensions retenues : 3 sur 3, ou 4 sur 4 | **Non applicable** : le cumul complet exige le risque. H9 n’est pas testable (03 §5) |

**Résultat :**
- **SE-04 :** O3-02 ≥ 22,13 % ; 13 préfectures sur 38.
- **SE-05 :** aucune préfecture au-delà de 25 %.
- **SE-06 :** O4-03 ≤ 3,68 km pour 10 000 habitants ; 14 préfectures, dont Mô.
- **SE-07 :** O4-05 ≤ 0 ; les 23 préfectures à 0 auto-école comptée.
- **SE-03 :** en 2021, 8,62 tués déclarés pour 100 000 habitants. C’est sous l’estimation de l’OMS pour le Togo (22,7) et sous la moyenne du Bénin, du Ghana et du Burkina Faso (26,17). Le 09 lit cet écart.

### 3.2 Points tranchés

✅ **a) SE-07 et les 23 ex aequo à 0** [SIG-26]. Le 02 écrit « O4-05 ≤ SE-07 », avec SE-07 au 33,3e percentile. 23 préfectures sur 39 sont à 0, donc ce percentile vaut 0, et la condition retient les 23 préfectures, ex aequo compris. Le « tercile » compte 23 préfectures, et non 13 : le 08 l’écrit tel quel. Aucun écart n’est nécessaire.

✅ **b) Mô.** Mô n’a aucune route classée : le 05 l’a établi (vrai vide). O3-02 y est non défini, faute de route, pas faute de donnée.
- **Rang :** Mô n’entre pas dans O5-02, qui exige les deux dimensions (`05_Priorisation`, « Valeurs manquantes »). Elle est affichée à part, avec la cause « aucune route classée ».
- **Leviers :** les leviers se lisent dimension par dimension. Mô reçoit le levier formation si O4-05 ≤ SE-07, et prend sa place dans l’ordre de ce levier.
- **Réseau :** « non défini », et non « non renseigné » (R-10). P5 ne s’applique pas à cette dimension : aucune donnée ne manque, c’est la route qui manque. Sa desserte (O4-03 = 0, SE-06) est affichée avec elle.
- **Régions :** Mô est comptée dans les sommes de la zone Centrale et de la région Centrale : population, auto-écoles, km (R-04).

✅ **c) Le Grand Lomé.** Le classement principal inclut Golfe et Agoè-Nyivé ; un test les retire (§7), comme le prévoit `05_Priorisation`.

✅ **d) L’indicateur de formation reste O4-05.** Le 02 le remplace par la distance (O4-08) si H4 montre que la distance va davantage avec le risque. H4 n’est pas testable sans risque par préfecture (03 §5). La distance est affichée à côté, et elle sert dans un test de sensibilité (§7, écart 25).

---

## 4. Déficits et rang (O5-01, O5-02)

**O5-01 : nombre de déficits.** Formule du 02, sans le terme du risque : 1[O3-02 ≥ SE-04] + 1[O4-05 ≤ SE-07]. Il vaut 0, 1 ou 2, et se lit « x déficits sur les 2 dimensions mesurées ; risque non déterminable ».

**O5-02 : rang de priorité.** Méthode du 02 (`05_Priorisation`), sur les 38 préfectures classées :
1. Chaque dimension est convertie en rang percentile : le rang divisé par le nombre de préfectures, entre 1/38 et 1. Il est orienté pour que plus haut soit plus prioritaire : O3-02 dans l’ordre croissant, O4-05 dans l’ordre décroissant. Les ex aequo reçoivent le rang moyen : les 22 préfectures classées à 0 auto-école comptée ont le même percentile de formation (Mô, la 23e, n’est pas classée).
2. La somme des deux rangs percentiles, à poids égaux, donne le score, entre 0 et 2.
3. Le rang 1 revient au score le plus élevé. À score égal, la préfecture qui compte le plus d’habitants passe devant (« Intensité et volume »).

✅ **Le score est la somme prévue par le 02** (`05_Priorisation`, « Agrégation »), pas le « score composite » que le 02 écarte par défaut. Celui-ci serait un indice opaque ; la somme reste décomposable. Elle est toujours affichée décomposée : rang percentile du réseau, rang percentile de la formation.

**Préfectures en tête :** les 10 premières sur 38 classées (26 %, « environ un quart » pour le 02), avec la population qu’elles représentent (`05_Priorisation`, « Territoires en tête »).

**Résultat :**
- **O5-01 :** 5 préfectures cumulent les deux déficits, 26 en ont un, 8 n’en ont aucun.
- **Les 10 premières** comptent 1 416 859 habitants. Les 5 premières cumulent les deux déficits : ce sont les 5 préfectures que le 06 trouvait déjà dans le pire quart des deux dimensions [SIG-29].

| Rang | Préfecture | Zone | Population | O3-02 (%) | O4-05 | Leviers | Tests parmi les 10 premières |
| ---- | ---------- | ---- | ---------- | --------- | ----- | ------- | ---------------------------- |
| 1 | Danyi | Plateaux | 40 240 | 100,0 | 0 | réseau ; formation | 6 sur 6 |
| 2 | Blitta | Centrale | 163 272 | 68,2 | 0 | réseau ; formation | 6 sur 6 |
| 3 | Agou | Plateaux | 85 793 | 40,0 | 0 | réseau ; formation | 6 sur 6 |
| 4 | Tchamba | Centrale | 200 585 | 34,0 | 0 | réseau ; formation | 6 sur 6 |
| 5 | Bassar | Kara | 152 065 | 28,0 | 0 | réseau ; formation | 6 sur 6 |
| 6 | Oti | Savanes | 124 848 | 21,1 | 0 | formation | 6 sur 6 |
| 7 | Bas-Mono | Maritime hors Grand Lomé | 94 860 | 21,1 | 0 | formation | 6 sur 6 |
| 8 | Est-Mono | Plateaux | 164 460 | 17,2 | 0 | formation | 4 sur 6 |
| 9 | Oti-Sud | Savanes | 150 376 | 14,4 | 0 | formation | 4 sur 6 |
| 10 | Tchaoudjo | Centrale | 240 360 | 36,9 | 0,83 | réseau | 3 sur 6 |

Le taux ne dit pas le volume. Danyi est en tête avec 100 % de km en mauvais état, mais sur 49,8 km évalués, et elle compte 40 240 habitants.

---

## 5. Leviers par préfecture

Chaque préfecture reçoit :
- **P5 pour le risque**, partout : non déterminable par territoire. Le levier de P5, « collecte et ouverture des données manquantes », est national : des accidents par territoire ;
- **le levier réseau** si O3-02 ≥ SE-04 : entretien des tronçons prioritaires (O3-05) ; cible et écart : km à remettre en état (O5-04, formule du 02) ;
- **le levier formation** si O4-05 ≤ SE-07 : ouverture d’auto-écoles ; cible et écart : auto-écoles manquantes (O5-04, variante de l’écart 21), avec la nature du zéro ;
- les deux leviers si les deux seuils sont franchis. Le déficit au rang percentile le plus élevé est alors affiché en premier (`05_Priorisation`, « Combinaison des profils »).

**Ordre dans chaque levier.** Les préfectures retenues sont rangées par leur rang percentile sur la dimension. À valeur égale, la plus peuplée passe devant (« Intensité et volume »). C’est le cas des 23 préfectures à 0 auto-école comptée : la population les départage.

**Population concernée** (O5-03) : la population de la préfecture. Pour la formation, la population au-delà de SE-08 (O4-08) est affichée à côté.

**Niveau de preuve :** O3-02 et O4-05 sont en C, donc chaque levier aussi. La recommandation qui en sortira commencera par une vérification, pas par un investissement (R-17).

**Résultat :** les écarts à la cible ne portent que sur les préfectures qui reçoivent le levier.

| Levier | Préfectures | Population | Écart à la cible (O5-04) | En tête du levier |
| ------ | ----------- | ---------- | ------------------------ | ----------------- |
| Réseau (SE-04) | 13 | 2 868 523 | 304,6 km à remettre en état | Danyi (100,0 %) |
| Formation (SE-07) | 23, dont Mô | 2 932 492 | 41 auto-écoles (variante de l’écart 21) | Haho, la plus peuplée des 23 (305 096 habitants) |

5 préfectures reçoivent les deux leviers ; 8 n’en reçoivent aucun.

---

## 6. Lecture par région

L’énoncé demande les « régions les moins bien desservies ». Le 02 lit le territoire en 6 zones, et la vue en 5 régions reste disponible par agrégation (R-02, R-03).

- **Valeurs.** O3-02 et O4-05 par zone et par région : somme des numérateurs sur somme des dénominateurs des préfectures (R-02). Ce ne sont jamais des moyennes de taux.
- **Seuils aux 6 zones.** SE-04 : au-dessus de la médiane des 6 zones ; SE-07 et SE-06 : en dessous.
- **Rang.** La même méthode qu’aux préfectures (§4), sur les 6 zones. Les 6 sont présentées, sans coupure (`05_Priorisation`).
- **Population** de chaque zone, et part des préfectures de la zone qui reçoivent chaque levier.
- **Toutes les préfectures comptent dans les sommes**, Mô comprise (Centrale) : la somme des zones égale le total national (R-04). Mô ne compte que dans le classement des préfectures, dont elle est exclue.

Les 5 régions sont calculées de la même façon, et affichées pour la lecture « par région » de l’énoncé. La ligne du pays donne les totaux et porte SE-03.

**Résultat par zone :**

| Rang | Zone | Population | O3-02 (%) | O4-05 | Seuils franchis | Levier réseau | Levier formation |
| ---- | ---- | ---------- | --------- | ----- | --------------- | ------------- | ---------------- |
| 1 | Centrale | 795 529 | 40,3 | 0,50 | réseau, formation | 4 préfectures, 113,6 km | 3 préfectures, 6 auto-écoles |
| 2 | Savanes | 1 143 520 | 12,8 | 0,35 | formation, desserte | — | 5 préfectures, 9 auto-écoles |
| 3 | Plateaux | 1 635 946 | 28,0 | 0,55 | réseau | 6 préfectures, 150,5 km | 7 préfectures, 12 auto-écoles |
| 4 | Maritime hors Grand Lomé | 1 346 615 | 9,5 | 0,37 | formation, desserte | — | 3 préfectures, 6 auto-écoles |
| 5 | Kara | 985 512 | 15,2 | 0,71 | réseau | 2 préfectures, 37,3 km | 5 préfectures, 8 auto-écoles |
| 6 | Grand Lomé | 2 188 376 | 7,7 | 4,71 | desserte | 1 préfecture, 3,2 km | — |

**Par région :** Centrale, puis Plateaux, Savanes, Kara et Maritime. La Centrale est en tête dans les deux lectures : c’est la seule zone, et la seule région, qui franchit les seuils du réseau et de la formation.

---

## 7. Sensibilité et confiance

Le 02 prévoit trois familles de tests (`05_Priorisation`). Deux ne fonctionnent plus telles quelles avec 2 dimensions et une médiane nulle : elles sont adaptées par écart (§8), avant le calcul.

| Test | Ce qui change | Source |
| ---- | ------------- | ------ |
| T0 — Principal | Poids égaux, rang percentile, 38 préfectures | §4 |
| T1, T2 — Pondérations | Réseau 2/3 et formation 1/3, puis l’inverse | Écart 23 |
| T3 — Normalisation | Écart à la médiane, en part de la médiane, au lieu du rang percentile | Écart 24 |
| T4 — Point extrême | Sans Golfe ni Agoè-Nyivé : 36 préfectures | `05_Priorisation` |
| T5 — Mesure de la formation | Distance O4-08 au lieu de O4-05 | Écart 25 |

**Stabilité** (règle du 02) : le classement est stable si, dans chaque test, au plus 2 des 10 préfectures en tête changent. ✅ Pour T4, la comparaison se fait avec le classement T0 dont on retire Golfe et Agoè-Nyivé : le test mesure l’effet de leur retrait sur les autres préfectures. Leur propre présence parmi les 10 premières de T0 est écrite à part, sans compter comme un changement. Si le classement est instable, il est présenté par levier (§5) plutôt que par rang.

**Confiance, par préfecture :** le nombre de tests sur 6 où elle figure parmi les 10 premières, et le niveau de preuve des dimensions (C).

**Résultat : le classement est stable.** Aucun test ne change plus de 2 des 10 premières.

| Test | Changements parmi les 10 premières | Entrées | Sorties |
| ---- | ---------------------------------- | ------- | ------- |
| T1 — réseau 2/3 | 2 | Kloto, Ogou | Est-Mono, Oti-Sud |
| T2 — formation 2/3 | 1 | Haho | Tchaoudjo |
| T3 — normalisation | 1 | Kloto | Oti-Sud |
| T4 — sans le Grand Lomé | 1 | Haho | Tchaoudjo |
| T5 — distance | 2 | Anié, Haho | Est-Mono, Tchaoudjo |

- **Toujours parmi les 10 premières (6 tests sur 6) :** Danyi, Blitta, Agou, Tchamba, Bassar, Oti, Bas-Mono.
- **Les moins sûres :** Est-Mono et Oti-Sud (4 sur 6), Tchaoudjo (3 sur 6).
- **Grand Lomé :** ni Golfe ni Agoè-Nyivé ne figurent parmi les 10 premières de T0.

---

## 8. Écarts au 02

Déclarés avant le calcul (R-20). Les écarts 1 à 19 sont ceux du 04, 20 à 22 ceux du 07. Le 02 n’est pas modifié.

| N° | Écart | Traitement | Raison |
| -- | ----- | ---------- | ------ |
| 23 | Le 02 teste les pondérations en donnant tour à tour la moitié du total à chaque dimension. Avec 2 dimensions, la moitié chacune, ce sont les poids égaux : le test ne teste rien | Chaque dimension pèse tour à tour 2/3, l’autre 1/3 | Avec 3 dimensions, une moitié face à deux quarts donne à la dimension testée le double de chacune des autres. Le rapport 2 pour 1 est gardé |
| 24 | Le 02 teste la normalisation en rapportant les valeurs à la médiane nationale. La médiane de O4-05 vaut 0 [SIG-26] : le rapport est non défini | Réseau : (O3-02 − médiane) / médiane. Formation : (médiane − O4-05) / médiane, avec la médiane de l’écart 21 (préfectures avec au moins une auto-école comptée, 07 §3) | Même raison que l’écart 21 : avec 23 zéros, la médiane ne mesure plus rien. Chaque terme vaut 0 à la médiane, et plus il est haut, plus la préfecture est prioritaire |
| 25 | Le 02 ne teste pas la mesure de la formation | Un test remplace O4-05 par la distance O4-08 (rang percentile, la plus grande distance la plus prioritaire) | H4, qui devait choisir entre les deux mesures, n’est pas testable (§3.2 d). La distance distingue les 23 préfectures à zéro (06 §3, O4) : le test dit si les 10 premières dépendent de ces ex aequo |

---

## 9. Validation

| Contrôle | Attendu |
| -------- | ------- |
| Préfectures | 39 lignes ; 38 classées ; Mô à part, avec sa cause |
| Seuils | Valeur de chaque percentile ; nombre de préfectures retenues par seuil ; SE-07 : les 23 à 0 ; SE-03 sur la ligne du pays ; SE-02, SE-09, SE-10 non applicables, avec la raison |
| Concordance avec le 07 | Les valeurs de O3-02, O4-05, O4-03, O4-08 et O5-03 sont celles de `indicateurs_07.csv` |
| O5-01 | Entre 0 et 2 ; égal à la somme des seuils franchis |
| O5-02 | Rangs de 1 à 38, sans trou ; scores décroissants ; ex aequo départagés par la population |
| Leviers | Un levier pour chaque seuil franchi, et aucun autre ; P5 pour le risque partout ; ni P1, ni P2, ni P3, ni P4, ni P6 |
| Régions | Somme des zones = somme des régions = ligne du pays (R-04), Mô comprise ; valeurs des 6 zones égales à celles du 06 (`rapports_06.csv`) |
| Compléments | O2-E1 à O2-E3 absents du classement (écart 22) |
| Sensibilité | 6 classements ; nombre de changements dans les 10 premières, par test |
| Reproductibilité | Deux exécutions donnent les mêmes fichiers |

**Résultat : 9 contrôles conformes sur 9** (`controles_08.csv`).
- **Concordance :** les 195 valeurs reprises du 07 sont identiques ; les 24 valeurs des 6 zones sont égales à celles du 06.
- **Régions :** les zones, les régions et le pays ont les mêmes totaux, Mô comprise dans la Centrale.
- **Reproductibilité :** deux exécutions donnent des fichiers identiques à l’octet près. Ni `data/processed/` ni `data/analysis/07_indicateurs/` ne sont modifiés.

---

## 10. Fichiers produits

**Dans `data/analysis/08_priorisation/`**, écrits par `priorisation_08.py` :

| Fichier | Contenu |
| ------- | ------- |
| `classement_08.csv` | Par préfecture : zone, région, population ; O3-02, O4-05, O4-03, O4-08 ; seuils franchis ; rangs percentiles ; O5-01 ; score ; O5-02 ; présence parmi les 10 premières ; leviers, dans l’ordre ; rang dans chaque levier ; O5-04 ; population concernée ; niveau de preuve (C) ; note (Mô, nature du zéro) |
| `regions_08.csv` | Par zone, par région et pour le pays : mêmes colonnes, valeurs par sommes (R-02) ; écarts de O5-04 des préfectures au levier ; sur la ligne du pays, SE-03 : O2-02 de 2021, les deux repères de l’OMS et la position du taux face à chacun |
| `sensibilite_08.csv` | Par préfecture et par test : score, rang, présence parmi les 10 premières ; une ligne de synthèse par test |
| `controles_08.csv` | Les contrôles du §9 |

---

## 11. Suite

- **Transmis au 09 :** les 10 premières, et d’abord les 5 qui cumulent les deux déficits ; le volume derrière chaque taux (Danyi : 49,8 km évalués) ; l’écart entre les tués déclarés et l’estimation de l’OMS (SE-03) ; la Centrale, en tête des zones et des régions.
- **Transmis au 10 :** par levier, les préfectures dans l’ordre, la population et l’écart à la cible : 13 préfectures et 304,6 km pour le réseau ; 23 préfectures et 41 auto-écoles pour la formation.
- **09 — Diagnostic** (étape 10) : une phrase par préfecture en tête, qui dit ce qu’elle cumule ; les hypothèses du 02, dont H8 ; la lecture des 6 taux de l’énoncé (07 §9).
- **10 — Recommandations** (étape 11) : par levier, avec la cible et l’écart de O5-04, en habitants ; P5 au national ; vérification avant investissement (R-17).
- **11 — Tableau de bord** : le classement s’affiche avec son niveau, « classement en C : vérification avant investissement » (R-17).
- **Puis** : 12 Validation, 13 Rapport final.

---

## 12. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Ni P1 ni P2 sans O2-02** : leviers réseau et formation, risque non déterminable (P5) | Point de départ, §5 | Équipe, 2026-10-06 (07 §9) |
| ✅ **Plan du 08** : un script, quatre fichiers ; ni figure ni notebook | §1, §2 | Équipe, 2026-10-06 |
| ✅ **Seuils** : SE-02, SE-09, SE-10 non applicables ; SE-03 au national ; percentiles ex aequo compris | §3.1 | Équipe, 2026-10-06 |
| ✅ **SE-07 appliqué tel quel** : les 23 préfectures à 0, sans écart | §3.2 a | Équipe, 2026-10-06 |
| ✅ **Mô à part**, cause « aucune route classée » | §3.2 b | Équipe, 2026-10-06 |
| ✅ **Grand Lomé** dans le classement principal, retiré dans T4 | §3.2 c | Équipe, 2026-10-06 |
| ✅ **Formation mesurée par O4-05**, la distance à côté | §3.2 d | Équipe, 2026-10-06 |
| ✅ **O5-01 et O5-02 sur 2 dimensions** ; rang moyen pour les ex aequo ; population pour départager | §4 | Équipe, 2026-10-06 |
| ✅ **Ordre dans chaque levier** : rang percentile, puis population | §5 | Équipe, 2026-10-06 |
| ✅ **Lecture par région** : 6 zones et 5 régions, par sommes | §6 | Équipe, 2026-10-06 |
| ✅ **Écarts 23, 24, 25** : pondérations 2/3–1/3, normalisation avec la médiane de l’écart 21, test par la distance | §7, §8 | Équipe, 2026-10-06 |
| ✅ **Précisions** : SE-03 sur la ligne du pays de `regions_08.csv` ; Mô comptée dans la Centrale, levier formation possible, réseau non défini sans P5 ; score décomposé (`05_Priorisation`, « Agrégation ») ; T4 comparé à T0 sans le Grand Lomé ; avertissement « classement en C » au 11 | §3, §4, §6, §7, §11 | Équipe, 2026-10-06 |
| ✅ **Choix de calcul** : rangs percentiles et scores arrondis à 6 décimales ; écarts de O5-04 sommés par région sur les seules préfectures au levier ; seuils de la vue en 5 régions à la médiane des 5 ; « -0,0 » du 07 écrit 0,0 | §6, §10 | Équipe, 2026-10-06 |
| ✅ **Résultats** : 10 premières, leviers, zones et régions, stabilité ; 9 contrôles conformes sur 9 | §3 à §7, §9 | Équipe, 2026-10-06 |
