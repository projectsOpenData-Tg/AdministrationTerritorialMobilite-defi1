# A1 — Horizon 2031 (annexe)

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 0.4 — **Date :** 2026-10-08 — **Statut :** résultats validés ; **non figé**, en attente de la validation d’ensemble avant le codage
**Sources :** `01_problem_definition.md` à `10_recommendation.md` (figés), `11_tableau_de_bord.md` (v0.9), `data/processed/`, `data/analysis/07_indicateurs/` à `data/analysis/10_recommandations/`

> **Question de l’annexe :** si rien ne change, où en sera chaque territoire dans 1, 3 et 5 ans ; combien faut-il ajouter sur chaque levier pour atteindre la cible ; et quel effort la cible de sécurité demande-t-elle ?
>
> L’annexe sort de la série 01 à 13 : l’énoncé ne demande pas de projection. Elle ne modifie aucun document figé. Le « A » la range après les documents numérotés ; le « 1 » laisse la place à d’autres annexes.
>
> Elle estime, elle ne prévoit pas. Chaque valeur projetée est C (R-17) : un ordre de grandeur pour fixer un horizon, pas un devis. Elle ne prête aux actions aucun effet sur les accidents que les données ne mesurent pas.
>
> Chaque chiffre cité vient de `data/analysis/A1_horizon/`, écrit par `horizon_A1.py` (R-19) ; le contrôle 10-13 relit ceux des blocs de résultats. Les choix du §9 sont fixés avant les résultats (R-20), sauf le constat de A1-5, déclaré après un premier calcul.
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §12.

---

## Point de départ

- **Le 01 (§3.5)** : chaque recommandation porte un horizon de 1, 3 ou 5 ans. Depuis 2026, ce sont 2027, 2029 et 2031.
- **Le 10 confie deux tâches à A1** :
  - **le scénario prospectif** (10 §2, point b) : « si A1 est validée, chaque recommandation lit la quantité de son horizon dans `horizon_A1.csv` » ;
  - **la vérification de l’accès rural** (10 §10) : télécharger la grille WorldPop, recalculer l’accès rural (O4-E1) et l’emplacement des auto-écoles, puis confirmer ou corriger la conclusion du 10 §4.6. C’est la vérification qui manque à l’écart 32.
- **Les quantités de 2022**, à reproduire :
  - au 08, dans le périmètre des leviers : 41 auto-écoles et 304,6 km ; sur toutes les préfectures sous la cible (07) : 54 auto-écoles et 327,9 km ;
  - au 10, par recommandation : 175,6 km (REC-R1), 129,0 km (REC-R2), 25 auto-écoles (REC-F1), 16 (REC-F2), environ 28,3 km pour Mô (REC-R4), au moins 5 513 permis A par an (REC-F3) ; 3 828 051 ruraux à plus de 2 km d’une route revêtue.
- **Le 09** : les accidents et les permis ne sont publiés qu’au niveau national (écart 1) ; H3, H4 et H7 restent non testables.
- **Le 11 (v0.9)** affiche les cibles de 2022 tant que A1 n’est pas validée.

---

## 1. Objectif de l’annexe

Trois parties :

1. **Modèle des besoins** (§4) : pour chaque recommandation du 10 et chaque palier, l’existant, la cible, la quantité à ajouter, et l’état de l’indicateur si elle est réalisée ;
2. **Modèle de sécurité** (§5) : au national, les accidents, blessés et tués attendus sans action nouvelle, la cible de la Décennie d’action, et l’écart entre les deux ;
3. **Vérification avec la grille WorldPop** (§6) : la tâche renvoyée par le 10, si le téléchargement est validé.

**Sorties**, dans `data/analysis/A1_horizon/` :

1. `population_A1.csv` : population totale et rurale, et densité, par préfecture, en 2022 et de 2026 à 2031, variantes (a) et (b) ;
2. `horizon_A1.csv` : une ligne par recommandation, territoire, palier et levier : existant, cible, quantité à ajouter, état sans action, état avec action, bornes, niveau, source, note. Le nom est celui que fixe le 10 ;
3. `national_A1.csv` : population de 18 ans et plus, permis, accidents, blessés et tués, de la série observée aux paliers : deux références sans action, cible, écart, plafond du casque ;
4. `acces_A1.csv`, `emplacements_A1.csv` et `sites_A1.csv` : accès rural, couverture des auto-écoles et sites retenus avec la grille (§6) ;
5. `erratum_A1.csv` et `formules_A1.csv` : la correction et la réserve du §13, et les formules des estimations, lues par la page Méthodologie ;
6. `sources_A1.csv` : les fichiers bruts lus, avec leur empreinte, dont la grille WorldPop ;
7. `controles_A1.csv` : les contrôles du §10.

Et `notebooks/A1_horizon.ipynb` : les cartes et les graphes du §7, lus dans ces CSV.

**Règles :**

- Les sorties du 07 au 10 ne sont jamais modifiées.
- Aucun chiffre national n’est réparti entre les territoires : ni carte, ni tableau par zone des accidents ou des permis ✅.
- Aucun effet sur les accidents n’est prêté à la remise en état des routes ou à l’ouverture d’auto-écoles : les données ne le mesurent pas (H3, H4 non testables), et la littérature ne l’établit pas (choix A1-8).
- Aucun résultat n’est écrit avant le calcul : les phrases de la page sont lues dans les CSV.

**L’annexe est terminée quand :**

- chaque recommandation chiffrée du 10 a sa quantité aux 5 paliers, avec sa fourchette ;
- le modèle de sécurité a ses deux références, sa cible et son écart ;
- la partie 3 est faite, ou son report est écrit ;
- les contrôles du §10 sont conformes ; les cartes et les graphes du §7 sont tracés.

---

## 2. Les paliers ✅

| Palier | Année | Population | Leviers |
| --- | --- | --- | --- |
| Passé | 2022 | Recensement (A) | Observés : auto-écoles (collecte 2021-2022), état du réseau (relevé de 2020), séries nationales de 2022 |
| Actuel | 2026 | Projection de l’INSEED (C) | Dernière observation reportée : auto-écoles 2021-2022, état 2020, séries nationales 2024 (choix A1-2) |
| +1 an | 2027 | Projection (C) | Quantité à ajouter |
| +3 ans | 2029 | Projection (C) | Quantité à ajouter |
| +5 ans | 2031 | Projection (C) | Quantité à ajouter ; dernière année des projections |

Chaque palier répond à : « pour être à la cible cette année-là, combien faut-il ajouter à l’existant ? ». Chaque recommandation lit le palier de son horizon d’action (10, colonne « Horizon ») : 3 ans pour REC-R1, REC-R3, REC-F1 à REC-F3, REC-S1 et REC-Z1 à REC-Z3 ; 5 ans pour REC-R2 et REC-R4.

Le curseur de la page couvre les 5 paliers, 2022 compris. Pour les séries nationales, le « passé » est toute la série observée (2007 ou 2010 à 2024).

---

## 3. Population par préfecture ✅

**Source : l’INSEED, pas la Banque mondiale.** Le 01 fixe une seule source de population : le recensement de 2022 et les projections officielles. Les chiffres de la Banque mondiale reprennent ceux de l’ONU (WPP), qui dépassent le recensement de 12,7 % en 2022 (03 §5). Les projections de l’INSEED vont jusqu’en 2031.

**Total national :** le recensement en 2022, puis les projections de l’INSEED de 2026 à 2031, reprises telles quelles, comme au 05 pour 2023 et 2024 (saut de 0,34 % en 2022 [4.4-07]).

**Répartition entre les préfectures**, deux variantes présentées en fourchette :

- **(a) parts constantes** : chaque préfecture garde sa part de 2022 ;
- **(b) tendance régionale** : chaque région prolonge sa croissance annuelle moyenne entre les recensements de 2010 et de 2022 ; les 5 régions sont ensuite ramenées au total de l’INSEED ; dans une région, chaque préfecture garde sa part de 2022.

Le Grand Lomé et la Maritime hors Grand Lomé gardent leur part de la Maritime en 2022 : le recensement de 2010 isole Lomé Commune, qui n’est pas le Grand Lomé (Golfe et Agoè-Nyivé).

**Population rurale et de 18 ans et plus :** chaque préfecture garde sa part rurale de 2022 (accès rural) ; la population de 18 ans et plus suit les groupes d’âges nationaux de l’INSEED (permis A).

<!-- résultats -->
**Résultat :**

- La population passe de 8 095 498 habitants en 2022 à 8 812 000 en 2026, 9 384 000 en 2029 et 9 767 000 en 2031 (projections de l’INSEED).
- Les régions n’ont pas grandi au même rythme entre 2010 et 2022 : 2,72 % par an dans les Savanes, 2,59 % dans la Maritime, 2,13 % dans la Centrale, 2,08 % dans la Kara, 1,46 % dans les Plateaux. La variante (b) prolonge ces écarts. En 2031 : 2 713 339 habitants dans le Grand Lomé, 1 835 037 dans les Plateaux, 1 669 651 dans la Maritime hors Grand Lomé, 1 434 270 dans les Savanes, 1 167 834 dans la Kara, 946 869 dans la Centrale.
- **Constat au calcul (A1-5) :** les projections de l’INSEED par âge ne raccordent pas au recensement. Les 18 ans et plus font 51,8 % de la population au recensement de 2022, et 55,6 % dans les projections de 2023. L’annexe garde le niveau du recensement et la seule croissance des projections : 4 193 458 habitants de 18 ans et plus en 2022, 4 736 037 en 2026, 5 398 017 en 2031.
<!-- fin -->

---

## 4. Partie 1 — Modèle des besoins

Chaque quantité se calcule par préfecture, puis s’additionne par recommandation, zone, région et pays. Un rapport de zone ne remplace jamais cette somme : le surplus du Grand Lomé ne comble pas le manque des Savanes. Les recommandations de zone (REC-Z1 à REC-Z3) reprennent les quantités des leviers, sans les additionner une seconde fois.

| Levier | Recommandations | Existant, gardé constant | Cible | Quantité à ajouter au palier t | État avec action |
| --- | --- | --- | --- | --- | --- |
| Auto-écoles | REC-F1, REC-F2 ; préfectures hors levier sous la cible, en colonne | Auto-écoles comptées (collecte 2021-2022) | 1,065 pour 100 000 habitants (écart 21), valeur de 2022 | Arrondi supérieur de 1,065 × population(t) / 100 000, moins les comptées, si positif | Chaque préfecture à la cible ; plus aucun habitant dans une préfecture sans auto-école agréée |
| Remise en état | REC-R1, REC-R2 ; tronçons de REC-R3 | Km en mauvais état (relevé de 2020) | 14,35 % des km évalués (médiane de O3-02) | Km en mauvais état moins 14,35 % des km évalués, si positif. Même valeur à chaque palier : aucune donnée ne mesure l’usure | Chaque préfecture du levier à 14,35 % ; part nationale recalculée |
| Desserte de Mô | REC-R4 | Aucune route classée | 5,39 km pour 10 000 habitants (écart 28) | 5,39 × population de Mô(t) / 10 000 | Desserte à la médiane |
| Accès rural | Contexte de REC-Z1 et REC-Z3 (10 : « suivi, sans cible ») | Part des ruraux à moins de 2 km d’une route revêtue (O4-E1, écart 32) | Aucune (10 §4.6) | Aucune : l’annexe compte les ruraux à plus de 2 km à chaque palier, en habitants | — |
| Permis moto | REC-F3 | Permis A délivrés | Taux de 2022–2024 pour 1 000 habitants de 18 ans et plus, soit 5 513 permis A par an en moyenne (écart 29) | Ce taux appliqué à la population de 18 ans et plus de t (choix A1-5) | — |
| Deux-roues parmi les tués | REC-S1 | Indice de 1,01 à 1,10 | Indice sous 1 (écart 30) | Aucune quantité : la cible ne dépend pas de la population | — |

**Les trois cas de départ, et ce que l’annexe en fait :**

| Cas | Ce que les données permettent | Ce que l’annexe calcule |
| --- | --- | --- |
| Territoire dense, peu de routes, beaucoup d’accidents | Routes : oui. Accidents : national seulement | Le manque de routes se lit en accès, pas en km par habitant (10, écart 31) : en ville dense, il relève de la voirie urbaine, absente des données. Accidents au modèle de sécurité, au national |
| Territoire sans auto-école | Oui | Auto-écoles à créer à chaque palier, selon la population |
| Territoire peu dense : accidents ? routes ? | Routes : oui (accès rural). Accidents : national seulement | Ruraux à plus de 2 km d’une route revêtue, à chaque palier ; auto-écoles selon la population |

<!-- résultats -->
**Résultat, au palier de l’horizon de chaque recommandation** (`horizon_A1.csv`, colonne « Palier de l’horizon ») :

| Recommandation | 2022 (10) | Palier | Quantité | Fourchette (a)–(b) | Population concernée |
| --- | --- | --- | --- | --- | --- |
| REC-R1 | 175,6 km | 2029 | 175,6 km | — | 729 319 |
| REC-R2 | 129,0 km | 2031 | 129,0 km | — | 2 645 816 |
| REC-R3 | 416,8 km en mauvais état | 2029 | 318,9 km à remettre en état | — | — |
| REC-R4 | 28,3 km | 2031 | 33,6 km | 33,6 à 34,1 | 62 426 |
| REC-F1 | 25 auto-écoles | 2029 | 30 auto-écoles | 30 à 31 | 2 081 464 |
| REC-F2 | 16 auto-écoles | 2029 | 18 auto-écoles | 18 à 19 | 1 278 886 |
| REC-F3 | 5 513 permis A par an | 2029 | 6 540 permis A par an | — | 5 131 425 de 18 ans et plus |
| REC-Z1 | 150,5 km | 2029 | 150,5 km | — | 883 973 |
| REC-Z2 | 15 auto-écoles | 2029 | 17 auto-écoles | — | 1 198 843 |
| REC-Z3 | 113,6 km ; 6 auto-écoles | 2029 | 113,6 km ; 6 auto-écoles | 6 à 7 auto-écoles | 852 444 ; 477 575 |

REC-S1 et REC-D1 à REC-D4 n’ont pas de quantité : la cible de REC-S1 ne dépend pas de la population ; les quatre autres sont des demandes de données, à un an.

- **Auto-écoles : le manque grandit avec la population.** Sans ouverture, le taux national passe de 1,63 auto-école agréée pour 100 000 habitants en 2022 à 1,35 en 2031 ; dans les Savanes, de 0,35 à 0,28. Dans le périmètre des leviers, les auto-écoles à ouvrir passent de 41 en 2022 à 45 en 2026, 48 en 2029 et 50 en 2031. Sur toutes les préfectures sous la cible : de 54 à 59, 64 et 69.
- **Remise en état : 304,6 km à chaque palier**, faute de donnée sur l’usure. Faite, elle ramène les 13 préfectures du levier de 37,30 % de km en mauvais état à 14,35 %. REC-R3 reçoit sa quantité : 318,9 km à remettre en état sur ses 416,8 km en mauvais état, des km qui recoupent ceux de REC-R1 et REC-R2.
- **Accès rural :** sans route nouvelle, les ruraux à plus de 2 km d’une route revêtue passent de 3 828 051 en 2022 à 4 147 410 en 2026, puis 4 570 433 en 2031 (méthode du 10).
- **Permis moto :** garder le taux de 2022–2024, 1,275 permis A pour 1 000 habitants de 18 ans et plus, demande 6 037 permis A en 2026, 6 540 en 2029 et 6 880 en 2031.
<!-- fin -->

---

## 5. Partie 2 — Modèle de sécurité : l’écart à la cible

Au national seulement. Le modèle ne dit pas ce que les actions éviteraient ; il dit ce que la cible demande d’éviter.

**Deux références sans action nouvelle**, en fourchette (choix A1-6) :

- **taux inchangé** : le taux moyen de 2022 à 2024 pour 100 000 habitants, appliqué à la population de t ;
- **tendance** : la variation annuelle moyenne du taux entre 2010–2012 et 2022–2024, prolongée à partir de 2023. Les fenêtres de 3 ans sont celles du 02 pour H6 et S4 ; le 09 a montré que les 6 taux baissent (H6).

**Cible** ✅ : la Décennie d’action pour la sécurité routière 2021–2030 vise au moins 50 % de tués et de blessés en moins d’ici 2030 (résolution A/RES/74/299 de l’Assemblée générale des Nations unies, 2020). Trajectoire linéaire depuis 2021 ; 2031 garde la cible de 2030.

**Écart** : à chaque palier, les tués et les blessés attendus moins la cible : ce qu’il faudrait éviter cette année-là pour être sur la trajectoire.

**Repère : le plafond du casque** (choix A1-8). En 2021, 60 % des tués déclarés étaient des usagers de deux et trois-roues motorisés (OMS). Le casque réduit le risque de décès d’un motocycliste d’environ 42 % (revue Cochrane, Liu et al., 2008, chiffre à vérifier à la source avant affichage). Le produit des deux donne la part des tués que le port du casque généralisé pourrait éviter **si aucun usager ne le portait aujourd’hui**. Le taux de port n’est pas publié (profil OMS 2023 : « - ») : c’est un plafond, pas une estimation. Il se compare à l’écart à la cible, et il se rattache à REC-S1.

**Ce que le modèle ne fait pas, et pourquoi :**

| Effet | Pourquoi il n’est pas modélisé |
| --- | --- |
| Accidents évités par la remise en état | Les accidents ne sont pas localisés : la part qui a lieu sur les routes remises en état est inconnue. Les revues de mesures ne trouvent pas d’effet net établi du revêtement sur les accidents ; la vitesse peut augmenter. H3 non testable |
| Accidents évités par les auto-écoles | Les revues ne montrent pas de baisse des accidents par la formation à la conduite (revue Cochrane, Roberts et Kwan, 2001). H4 non testable. Le levier se justifie par l’accès à la formation (objectif 5), pas par un effet sur les accidents |
| Montée en charge et effet rebond | Aucune source pour les fixer ; aucun comptage de trafic par route |
| Résultats par zone ou par préfecture | Les accidents ne sont pas publiés par territoire (écart 1) ; les répartir inventerait une géographie (H7 non testable) |

**Sources vérifiées avant affichage** ✅ : la revue Cochrane CD004333 (Liu et al., 2008) donne un risque de décès réduit de 42 % (OR 0,58 ; intervalle de confiance à 95 % de 0,50 à 0,68), d’où les bornes de 32 % à 50 % du plafond ; la résolution A/RES/74/299 (2020) fixe la cible de la Décennie.

<!-- résultats -->
**Résultat :**

- **Les deux références sans action.** De 2022 à 2024, le taux moyen est de 84,60 accidents, 115,10 blessés et 7,38 tués pour 100 000 habitants. Entre 2010–2012 et 2022–2024, il baisse de 1,54 %, 1,28 % et 2,86 % par an. En 2031, les tués attendus vont de 571 (tendance) à 720 (taux inchangé), les blessés de 10 143 à 11 242, les accidents de 7 300 à 8 263.
- **La cible de la Décennie :** 340 tués et 4 688 blessés en 2030, la moitié des 680 tués et des 9 376 blessés de 2021. Sur la trajectoire : 491 tués en 2026, 378 en 2029.
- **L’écart à la cible grandit à chaque palier**, même avec la tendance à la baisse : 105 à 159 tués à éviter en 2026, 204 à 314 en 2029, 231 à 380 en 2031. Pour les blessés : 2 987 à 3 371 en 2026, 5 455 à 6 554 en 2031.
- **Le plafond du casque** vaut 25,2 % des tués (60 % × 42 %). En 2026, il dépasse l’écart : au plus 150 à 164 tués évités, pour un écart de 105 à 159. Dès 2029, il reste en dessous : 147 à 174, pour un écart de 204 à 314 ; en 2031, 144 à 182, pour 231 à 380. Même à son plafond, le casque seul ne suffit plus à suivre la trajectoire après 2026 : la cible demande d’autres mesures, que les données ne permettent pas de chiffrer.
<!-- fin -->

---

## 6. Partie 3 — Vérification avec la grille WorldPop

La tâche que le 10 renvoie à A1 (10 §10). Elle dépend d’un téléchargement, présenté pour validation avant d’être fait.

**Téléchargement proposé :** la grille de population 2020 à 100 m du Togo (WorldPop, CC BY 4.0), recensée au 03 (D13). Lecture avec un nouveau paquet, `rasterio`. Comme pour WPP au 03, on ne garde que la répartition dans l’espace : la grille est ramenée, dans chaque préfecture, à la population de l’INSEED (choix A1-9).

**Deux calculs :**

1. **Accès rural recalculé** : O4-E1 avec la grille, à la place d’une population répartie uniformément. **Critère fixé avant le calcul :** la conclusion du 10 §4.6 est confirmée si les mêmes zones restent sous la médiane des zones (Centrale et Plateaux) ; sinon, elle est corrigée dans l’annexe et signalée au 13. Les Savanes, cas limite au 10, sont lues à part.
2. **Emplacement des auto-écoles** : choisir, parmi les lieux candidats de D13 (les 31 chefs-lieux et les points d’étiquette des 40 préfectures et des 373 cantons, HDX), les sites qui couvrent le plus d’habitants à moins de 10 km (SE-08). Le nombre de sites de chaque préfecture est sa quantité de REC-F1 ou de REC-F2 au palier de leur horizon, 2029 (choix A1-10). On compare la population couverte avec ces sites et avec le site indicatif du 10 (le point de départ de O4-08).

**Téléchargement validé et fait** ✅ (2026-10-08) : `data/raw/worldpop_tgo_2020.tif`, 31 776 501 octets, empreinte dans `sources_A1.csv`. Le script le retélécharge s’il manque, et vérifie son empreinte.

<!-- résultats -->
**Résultat :**

- **La grille** compte 6 718 506 carreaux peuplés. Ramenée à chaque préfecture, elle retrouve exactement sa population et sa population rurale (contrôle 10-12).
- **L’accès rural est plus élevé avec la grille** : 27,12 % des ruraux à moins de 2 km d’une route revêtue, contre 17,17 % avec une population uniforme. La grille place une part des ruraux près des routes, là où la répartition uniforme les étale. Par zone : Maritime hors Grand Lomé 39,55 % (23,14 % au 10), Centrale 25,12 % (13,19 %), Kara 23,65 % (17,49 %), Savanes 23,37 % (16,93 %), Plateaux 21,26 % (13,55 %).
- **La conclusion du 10 §4.6 est corrigée pour la route**, selon le critère fixé avant le calcul. La médiane des zones passe à 23,65 %, la valeur de la Kara. Sous la médiane : les Plateaux, comme au 10, et les Savanes, au lieu de la Centrale. La Centrale passe au-dessus (25,12 %). Les Savanes sont un cas limite : 23,37 % pour une médiane de 23,65 %.
- **Ce que cela change à la lecture par dimension du 10 :** la formation ne change pas (Centrale, Savanes, Maritime hors Grand Lomé). Pour l’accès, la zone qui cumule les deux retards devient les Savanes, de justesse ; la Centrale ne cumule plus. Elle reste la zone au réseau le plus dégradé (40,3 % de km en mauvais état) : REC-Z3 garde ses quantités d’entretien et de formation. Le 10, figé, n’est pas modifié ; la correction est transmise aux documents 12 (validation) et 13 (rapport final), qui restent à écrire (§11).
- **Les emplacements.** Les 48 auto-écoles à ouvrir en 2029 dans les 23 préfectures du levier formation couvriraient à moins de 10 km 56,7 % de leur population en sites optimisés. Au site indicatif du 10, elles en couvriraient 32,2 % ; avant ouverture, 2,4 %. L’écart vaut 719 730 habitants (population de 2022). Il est le plus fort à Bas-Mono (28,8 % au site indicatif, 96,9 % en sites optimisés), presque nul à Mô (23,4 % et 24,1 %), où une seule auto-école est à ouvrir.
- Les sites retenus sont dans `sites_A1.csv`. Ils orientent la vérification sur place ; ce ne sont pas des adresses.
<!-- fin -->

---

## 7. Cartes, graphes et page du tableau de bord

**Notebook.** Il reprend le style du 06 (`style_06.py`) : palette validée, étiquettes directes, un tableau à côté de chaque graphe. Les classes des cartes sont fixées sur 2022 et gardées à tous les paliers, pour que les couleurs se comparent.

1. **Cartes « sans action / avec action », un panneau par palier**, sur les 6 zones et les 39 préfectures :
   - auto-écoles comptées pour 100 000 habitants : le taux baisse sans action, il atteint la cible avec action ;
   - part des km en mauvais état : un seul panneau, la valeur ne change pas d’un palier à l’autre ;
   - ruraux à plus de 2 km d’une route revêtue, en habitants ;
   - densité de population, en contexte.
2. **Graphe par zone** : auto-écoles à ouvrir et km à remettre en état aux 5 paliers, avec la fourchette (a)–(b).
3. **Graphe national** : permis A, accidents, blessés et tués observés ; les deux références sans action en bande, de 2025 à 2031 ; la cible de la Décennie ; l’écart en barres aux paliers ; le plafond du casque en regard. La période projetée est grisée.

Aucune carte des accidents. Chaque vue porte sa limite : valeurs C ; état du réseau de 2020 ; auto-écoles de 2021-2022, activité non vérifiée ; tués déclarés sous l’estimation de l’OMS (SE-03).

**Page du tableau de bord.** Une page 8 « Horizon 2031 », dans le groupe Pilotage, après « Recommandations » : elle projette les actions de la page 6. Son plan détaillé ira dans `workspace/design-page8.md`, comme pour les 7 autres pages, une fois les résultats connus. Il reprendra la structure proposée : curseur de palier en haut, chiffres clés du palier, population, besoins, sécurité, national, limite.

---

## 8. Méthode et outils

**Outils.** Ceux des étapes précédentes, dans `.venv` : pandas, numpy, geopandas, matplotlib. Un nouveau paquet pour la partie 3 seulement : `rasterio`.

**Script** : `scripts/horizon_A1.py`. Il lit :

- `data/processed/` : la table maîtresse (population 2022, rurale, surface, km, auto-écoles), `D2_permis.csv`, `D3_accidents.csv`, `D3_victimes_usager_2021.csv`, `D7_population_age_conduire.csv`, `D7_population_nationale.csv`, les couches `geo/` ;
- `data/analysis/` : `indicateurs_07.csv`, `classement_08.csv`, `recommandations_10.csv`, `prefectures_10.csv`, `zones_10.csv` ;
- `data/raw/` : `projections_demographiques_2011_2031.csv` (années 2025 à 2031), `population_region_sexe_2010.csv`, `wpp2024_population_age_simple_togo.csv` (choix A1-7), `limites_administratives_hdx.xlsx` (lieux candidats) ; la grille WorldPop `worldpop_tgo_2020.tif` pour la partie 3.

**Ordre de travail :**

1. la population par préfecture et par palier (§3) ;
2. le modèle des besoins (§4) ;
3. le modèle de sécurité (§5) ;
4. les contrôles (§10) ;
5. le notebook (§7) ;
6. la partie 3, après validation du téléchargement (§6).

**Pour tout reproduire :** la chaîne du 10, puis `horizon_A1.py`, puis le notebook.

---

## 9. Choix de l’annexe

L’annexe va au-delà du 02 : ses choix sont déclarés ici, avant les résultats (R-20).

| # | Choix | Raison |
| --- | --- | --- |
| A1-1 ✅ | Population : la valeur citée est celle de la variante (b) ; les bornes sont le minimum et le maximum des variantes (a) et (b) | (b) suit la croissance observée de chaque région ; (a) montre ce que donne une croissance uniforme |
| A1-2 ✅ | En 2026 et après, chaque levier garde sa dernière observation : auto-écoles 2021-2022, état du réseau 2020, séries nationales 2024 | Aucune donnée plus récente ; « actuel » veut dire « population de 2026, leviers tels qu’observés » |
| A1-3 ✅ | Périmètre : les recommandations du 10, plus les préfectures hors levier sous la cible, en colonne ; les cibles gardent leur valeur de 2022 | Le lien avec le 10 est la règle ; la colonne montre le besoin du reste de la population. Une cible recalculée chaque année bougerait avec la population qu’elle mesure |
| A1-4 | Routes : pas de km à ajouter en général. L’accès rural se compte en habitants, sans cible ; seule Mô reçoit des km (REC-R4, écart 28) | Le 10 a établi que les km par habitant mesurent la densité, pas l’accès (écart 31), et n’a fixé ni cible d’accès ni création de route, sauf la vérification de Mô |
| A1-5 | Permis moto : le rapport entre la moyenne des permis A et la moyenne de la population de 18 ans et plus de 2022 à 2024, appliqué à la population de 18 ans et plus de t ; groupes d’âges de l’INSEED coupés avec les parts par âge de WPP. **Constat au calcul :** les projections par âge ne raccordent pas au recensement (§3, résultat) ; la population de 18 ans et plus garde le niveau du recensement de 2022 et suit la croissance des projections | Garde la cible de REC-F3 (5 513 par an, écart 29) et la fait suivre la population. Méthode de coupe du 05. Le raccord suit la règle du 03 pour WPP : le niveau vient du recensement, la croissance de la projection. Déclaré après un premier calcul, comme l’écart 32 au 10 |
| A1-6 | Sécurité : deux références sans action nouvelle (taux inchangé ; tendance entre 2010–2012 et 2022–2024) ; taux par habitant seulement ; cible de la Décennie sur une trajectoire linéaire depuis 2021 | Les fenêtres de 3 ans sont la méthode du 02 (H6, S4). Le parc est estimé (C) dans une fourchette large : le prolonger empilerait deux estimations |
| A1-7 | Trois fichiers bruts lus directement : les projections de 2025 à 2031, le recensement de 2010 par région, les parts par âge de WPP | Le 05 n’a préparé que les années utiles à la chaîne ; ces fichiers ont été profilés au 04 |
| A1-8 | Aucune élasticité d’accidents pour la route et les auto-écoles. Un seul repère d’effet, le casque, affiché en plafond, avec sa source vérifiée avant affichage | Un effet sans source datée ne remonte à aucun fichier (R-19). Pour la route et la formation, la littérature ne l’établit pas ; pour le casque, elle l’établit, mais le taux de port manque |
| A1-9 | WorldPop : une grille (2020, 100 m), ramenée dans chaque préfecture à la population du recensement de 2022. Dans chaque préfecture, les carreaux les plus denses portent la population urbaine du recensement, les autres la population rurale. Un carreau est à moins de 2 km si son centre est dans la bande | La règle du 03 pour WPP : une source modélisée ne donne que la répartition. Le partage par densité garde les totaux urbain et rural du recensement |
| A1-10 | Emplacements : couverture maximale à 10 km (SE-08), parmi les lieux de D13, avec le nombre de sites de REC-F1 ou REC-F2 de chaque préfecture en 2029. Choix glouton : à chaque étape, le site qui couvre le plus d’habitants encore non couverts. Les auto-écoles comptées existantes, y compris celles des préfectures voisines, couvrent déjà leurs environs | La méthode que la procédure demande (étape 11), avec le seuil de distance déjà utilisé au 07 et au 08. Le choix glouton est la méthode courante de la couverture maximale |

---

## 10. Validation

| # | Contrôle | Attendu |
| --- | --- | --- |
| 10-01 | Population | La somme des préfectures égale le total national à chaque année, dans chaque variante (R-04) |
| 10-02 | Population en 2022 | Les variantes (a) et (b) égalent le recensement, préfecture par préfecture |
| 10-03 | Reproduction du 07 et du 08 | En 2022 : 41 auto-écoles et 304,6 km dans le périmètre des leviers ; 54 auto-écoles et 327,9 km sur toutes les préfectures |
| 10-04 | Reproduction du 10 | En 2022 : 175,6 km (REC-R1), 129,0 km (REC-R2), 25 et 16 auto-écoles (REC-F1, REC-F2), environ 28,3 km (REC-R4), 5 513 permis A par an (REC-F3), 3 828 051 ruraux à plus de 2 km |
| 10-05 | Bornes | Borne basse ≤ valeur ≤ borne haute, sur chaque ligne |
| 10-06 | Sens | Quantités à ajouter positives ou nulles ; non décroissantes de 2026 à 2031 pour les auto-écoles, Mô et les permis |
| 10-07 | Agrégats | 6 zones et 5 régions ; chaque agrégat égale la somme de ses préfectures (R-02, R-03) ; REC-Z1 à REC-Z3 sans double compte |
| 10-08 | Niveaux | Toute valeur projetée en C, avec sa source |
| 10-09 | Cible de la Décennie | En 2030, la cible vaut la moitié de la valeur de 2021, pour les blessés et pour les tués |
| 10-10 | Maille nationale | Aucune ligne territoriale pour les permis et les accidents |
| 10-11 | Plafond du casque | Égal au produit de ses deux termes, chacun avec sa source |
| 10-12 | Grille WorldPop | Si la partie 3 est faite : la grille ramenée égale la population de chaque préfecture |
| 10-13 | Chiffres du document | Chaque chiffre des blocs de résultats se retrouve dans les CSV, vérifié par script (comme le contrôle 8-07 du 09) |
| 10-14 | Sources | Les quatre fichiers bruts lus ont l’empreinte du registre du 03 ; la grille WorldPop a la sienne dans `sources_A1.csv` |
| 10-15 | Erratum et formules | Chaque ligne de l’erratum nomme le document, la source et la conséquence ; chaque formule dit d’où viennent ses valeurs |

<!-- résultats -->
**Résultat :** 15 contrôles conformes sur 15 (`controles_A1.csv`). Deux exécutions donnent des fichiers identiques. Le contrôle des chiffres du document relève bien une erreur : sur une copie où trois nombres étaient faussés, il a signalé les trois.
<!-- fin -->

---

## 11. Suite

- **Le 10** (figé, non modifié) : chaque recommandation lit la quantité de son horizon dans `horizon_A1.csv`, comme le prévoit son point b.
- **Le 11** (v0.9) : si A1 est validée, trois mises à jour avant son gel :
  - la page 6 affiche les quantités du palier de chaque recommandation au lieu des cibles de 2022 ;
  - la page 8 « Horizon 2031 » s’ajoute, avec son plan `workspace/design-page8.md` ;
  - la page 7 remplace la limite « grille WorldPop recensée mais non téléchargée » par le résultat de la partie 3.
Le 12 et le 13 sont les deux documents qui suivent le 11 dans la procédure, pas des pages du tableau de bord. L’annexe ne les écrit pas : elle note ici ce qu’ils devront traiter.

**Les documents 12 et 13 ne seront pas écrits** ✅ (décision du 2026-10-08, faute de temps). Ce qu’ils devaient porter est redirigé :

| Ce que le 12 ou le 13 devait porter | Où cela va |
| --- | --- |
| Revue de décision : REC-Z3 garde-t-elle sa priorité haute ? | **Tranché ici** : oui (§13, A1-E1). Le tableau de bord l’affiche avec sa note |
| Revue de rigueur | Un tableau des contrôles de chaque étape, en page Méthodologie (11 §7) |
| La correction de l’accès rural, et le cas limite des Savanes | §13 ; page Méthodologie ; diapositive des limites du ppt |
| Le raccord des projections par âge | §13 ; limites de la page Méthodologie ; ppt |
| Le plafond du casque après 2026 | §5 ; page Horizon 2031 ; ppt |
- **Limite à dire au jury** : aucun coût unitaire n’est publié ; l’annexe chiffre des quantités et un effort, pas un budget ni un effet des actions sur les accidents.

---

## 13. Erratum — ce que l’annexe corrige, et ce qu’elle met en réserve

Les documents 01 à 10 restent figés. Cette section dit ce que le calcul de l’annexe change à leur lecture, et ce qu’il ne change pas. Elle est lue dans `erratum_A1.csv` et `formules_A1.csv` par la page Méthodologie du tableau de bord, et reprise dans le ppt.

**Une correction change une conclusion. Une réserve dit de quoi un chiffre dépend, sans le dire faux.** Deux lignes seulement, car l’annexe n’a trouvé qu’une conclusion à corriger.

<!-- résultats -->
| # | Type | Document | Objet | Ce que montre l’annexe | Conséquence |
| --- | --- | --- | --- | --- | --- |
| A1-E1 | **Correction** | 10, les régions les moins bien desservies | La zone qui cumule les deux retards, accès à la route et formation | Les Savanes, à 23,37 % pour une médiane de 23,65 %, et non la Centrale, qui passe au-dessus à 25,12 %. Les Plateaux restent sous la médiane dans les deux lectures | La recommandation de zone de la Centrale garde sa priorité haute : elle reste la zone au réseau le plus dégradé (40,3 % de km en mauvais état, contre 12,8 % dans les Savanes), et la lecture « formation » ne change pas. Un écart de 0,28 point ne sépare pas deux zones en C |
| A1-R1 | **Réserve** | 07, permis pour 1 000 habitants en âge de conduire, 2023 et 2024 | La population de 18 ans et plus après le recensement | Les projections par âge ne raccordent pas au recensement : 51,8 % de 18 ans et plus en 2022, 55,6 % dans la projection de 2023 | Les taux de 2023 et 2024 dépendent de ce saut ; leur niveau reste C. Le 07 n’est pas corrigé : aucun de ses calculs n’est faux |
<!-- fin -->

**Ce qui n’entre pas dans l’erratum, et pourquoi :**

- **La date du décret n° 2022-085/PR.** Le 04 porte déjà la bonne date, le 3 août 2022, prise au Journal officiel. Ce qui portait le 25 juillet, c’est `data/reference/chronologie_reformes.csv`, corrigé depuis (11 §10). Le 04 n’a jamais été faux.
- **La médiane de l’accès rural.** 16,93 % et 23,65 % sont les médianes du même indicateur calculé par deux méthodes. Aucune des deux n’est fausse : c’est la conséquence de A1-E1, pas une correction de plus.
- **Le plafond du casque.** C’est un résultat de l’annexe (§5), pas une correction d’un document figé.

**Les formules des estimations** sont dans `formules_A1.csv`, affichées en page Méthodologie et dans le ppt : auto-écoles à ouvrir, km à remettre en état, km pour Mô, permis moto, accidents et tués attendus, cible de la Décennie, accès rural, plafond du casque. Chacune dit d’où viennent ses valeurs. Elles sont écrites en entier : la formule des auto-écoles comprend l’arrondi supérieur et la soustraction des auto-écoles existantes, sans quoi elle donne la cible et non la quantité à ouvrir.

---

## 12. Journal des décisions

| Décision | Où | Validée par |
| --- | --- | --- |
| ✅ **Annexe hors de la série 01 à 13**, nommée `A1_horizon.md` | En-tête | Utilisateur, 2026-10-06 |
| ✅ **Paliers** : 2022 (passé), 2026 (actuel), 2027, 2029, 2031 (1, 3 et 5 ans) ; le curseur couvre les 5 | §2 | Utilisateur, 2026-10-06 et 2026-10-08 |
| ✅ **Population de l’INSEED**, pas de la Banque mondiale ; fourchette (a)–(b) | §3 | Plan validé, 2026-10-06 ; note du 2026-10-08 |
| ✅ **Accidents et permis au niveau national**, sans répartition entre territoires | §1, §5 | Plan validé, 2026-10-06 |
| ✅ **Modèle des besoins** : auto-écoles à 1,065 pour 100 000 habitants, remise en état à 14,35 %, leviers à leur dernière observation (A1-1 à A1-3) | §4, §9 | Note du 2026-10-08 |
| ✅ **Cible de la Décennie d’action** pour les blessés et les tués | §5 | Plan validé, 2026-10-06 |
| ✅ **Un second modèle** sur la page, à côté des besoins | §5 | Note du 2026-10-08 |
| ✅ **Le second modèle en écart à la cible**, avec deux références sans action et le plafond du casque, au lieu d’un modèle d’impact à élasticités (A1-6, A1-8) | §5, §9 | Utilisateur, 2026-10-08 |
| ✅ **Pas de km à ajouter en général** ; accès rural en habitants ; Mô seule en km (A1-4) | §4, §9 | Utilisateur, 2026-10-08 |
| ✅ **Sorties par recommandation du 10**, dans `horizon_A1.csv` | §1, §4 | Utilisateur, 2026-10-08 |
| ✅ **Partie 3 (WorldPop)** : téléchargement de la grille et paquet `rasterio` (A1-9, A1-10) | §6, §9 | Utilisateur, 2026-10-08 |
| ✅ **Page 8 dans le groupe Pilotage**, après « Recommandations » ; plan dans `workspace/design-page8.md` après les résultats | §7, §11 | Utilisateur, 2026-10-08 |
| ✅ **Précisions de méthode déclarées avant le calcul** : partage urbain et rural par densité, lieux candidats, sites comptés au palier 2029, fichiers `sites_A1.csv` et `sources_A1.csv`, contrôle 10-14 | §6, §9, §10 | Exécution, 2026-10-08 |
| ✅ **Sources vérifiées avant affichage** : revue Cochrane CD004333 (42 %, OR 0,58 [0,50–0,68]) ; résolution A/RES/74/299 | §5 | Vérification, 2026-10-08 |
| ✅ **Résultats** : `horizon_A1.py` exécuté, 14 contrôles conformes sur 14, fichiers reproductibles ; notebook `A1_horizon.ipynb` exécuté (12 figures) | §3 à §6, §10 | Exécution, 2026-10-08 |
| ✅ **Constat de A1-5**, déclaré après un premier calcul : niveau du recensement et croissance des projections pour les 18 ans et plus ; porté en réserve A1-R1, et non en correction du 07 | §3, §9, §13 | Utilisateur, 2026-10-08 |
| ✅ **Correction de la conclusion du 10 §4.6** pour la route (Savanes au lieu de la Centrale, cas limite), portée en A1-E1 ; **la recommandation de zone de la Centrale garde sa priorité haute** | §6, §11, §13 | Utilisateur, 2026-10-08 |
| ✅ **Les documents 12 et 13 ne seront pas écrits** ; ce qu’ils devaient porter est redirigé vers le tableau de bord et le ppt | §11 | Utilisateur, 2026-10-08 |
| ✅ **Erratum réduit à une correction et une réserve** : la date du décret, la médiane de l’accès rural et le plafond du casque n’en sont pas ; formules écrites en entier | §13 | Utilisateur, 2026-10-08 |
| ✅ **`erratum_A1.csv` et `formules_A1.csv`** écrits par le script et lus par la page Méthodologie ; contrôle 10-15 | §1, §10, §13 | Utilisateur, 2026-10-08 |
| **Gel reporté** : rien n’est figé ni commité tant que l’ensemble n’est pas validé, avant le codage | Tout le document | Utilisateur, 2026-10-08 |
