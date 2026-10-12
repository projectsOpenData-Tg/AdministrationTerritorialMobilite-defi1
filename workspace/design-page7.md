

## Page 7 — Méthodologie

**Objectif :** dire comment la décision a été produite, et ce que les données ne disent pas. Le tableau de bord montre la décision et son fondement ; cette page explique comment elle a été produite (garde-fous).

```text
┌──────────────────────────────────────────────────────────────────┐
│  SOURCES, MÉTHODE ET LIMITES                                      │
├──────────────────────────────────────────────────────────────────┤
│  [COMMENT NOUS AVONS TRAVAILLÉ — 9 étapes]               │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [SOURCES — 30 jeux de données, tableau]                          │
├──────────────────────────────────────────────────────────────────┤
│  [LIMITES MAJEURES]                                               │
├──────────────────────────────────────────────────────────────────┤
│  [NIVEAUX DE PREUVE — légende et décompte]                        │
├──────────────────────────────────────────────────────────────────┤
│  [QUESTIONS OUVERTES — 7 hypothèses et la donnée qui manque]      │
├──────────────────────────────────────────────────────────────────┤
│  [ZONES LES MOINS DESSERVIES — les deux mesures]                  │
├──────────────────────────────────────────────────────────────────┤
│  [FORMULES — 18 calculs, par thème, avec un exemple chiffré]      │
├──────────────────────────────────────────────────────────────────┤
│  [CORRECTIONS ET CONTRÔLES]                                       │
├──────────────────────────────────────────────────────────────────┤
│  [LICENCES]                                                       │
├──────────────────────────────────────────────────────────────────┤
│  [SYNTHÈSE CHIFFRÉE]  [LIMITE]                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Section 1 — Comment nous avons travaillé

Premier bloc de la page : il répond à « comment êtes-vous passés du problème à la solution ? » avant d’entrer dans le détail des sources.

**Forme :** une liste verticale de 9 étapes. Chaque ligne porte un numéro, un titre, une phrase, et un encadré « Ce que l’étape produit », aligné à droite. Sur un écran étroit, l’encadré passe sous le texte. Un trait vertical relie les numéros.

**Couleurs :** les numéros prennent la rampe `BLEUS` de la maquette, du clair au foncé, de l’étape 1 à l’étape 9 : l’intensité dit l’avancement, elle ne code aucune catégorie. Aucune autre couleur n’est introduite (11 §4.1).

| # | Étape | Phrase | Ce que l’étape produit |
| - | ----- | ------ | ---------------------- |
| 1 | **Ce que l’énoncé demande** | Cinq objectifs : retracer les immatriculations et les permis, analyser la sécurité routière, évaluer l’état du réseau, cartographier le réseau et les auto-écoles, recommander. | 5 objectifs, et une question de décision : où agir en priorité ? |
| 2 | **Le cadre de décision** | Chaque objectif devient des indicateurs mesurables, des hypothèses à trancher et des seuils, fixés **avant** de regarder les données. La sécurité routière en compte 14 à elle seule. | 43 indicateurs · 17 vérifications et hypothèses · 10 seuils · 20 règles |
| 3 | **Les données** | Recensement des données ouvertes : immatriculations, permis, accidents, réseau, auto-écoles, population, enquêtes. Licences, mailles et années vérifiées une à une. | 34 fichiers · 30 jeux de données · 7 recherches complémentaires, dont 2 sans réponse |
| 4 | **Préparation et calcul** | Nettoyage, jointures, puis calcul de chaque indicateur avec la formule du cadre. Chacun reçoit son niveau de preuve. | 32 indicateurs calculés : 5 mesurés, 10 calculés, 17 estimés |
| 5 | **Ce que les données disent** | Le constat, sans jugement : le parc a quadruplé, porté par les motos ; les accidents augmentent en volume mais les taux baissent ; le réseau est inégalement entretenu. | 5 messages · 5 préfectures qui cumulent les deux déficits · 4 zones en difficulté |
| 6 | **Ce qu’elles ne disent pas** | Les accidents ne sont publiés que pour tout le pays. L’activité des auto-écoles n’est pas publiée. Le coût des actions est absent. Chaque manque est écrit, jamais comblé par une hypothèse. | 9 indicateurs non calculables · 7 questions ouvertes · 32 écarts déclarés |
| 7 | **Priorité et recommandations** | Les territoires sont classés sur ce qui est mesuré, puis chaque recommandation reçoit un territoire, une cible chiffrée, une population, un horizon, un responsable et une réserve. | 38 préfectures classées · 15 recommandations, dont 10 avec une quantité |
| 8 | **Et d’ici 2031 ?** | La population projetée est appliquée à chaque levier : combien faudra-t-il ajouter dans 1, 3 et 5 ans, et que demande la cible internationale de sécurité routière. | 5 horizons · 2 références sans action nouvelle · une fourchette sur chaque quantité |
| 9 | **Le livrable** | Ce tableau de bord, qui lit des fichiers de résultats sans rien recalculer, et une présentation. | 8 pages · une présentation · cette page de méthode |

**Phrase sous la liste :** « Chaque étape a été gelée avant de passer à la suivante : les seuils ont été fixés avant de voir les résultats, et aucun chiffre affiché ici n’a été recopié à la main. »

**Lecture des chiffres de la colonne « Ce que l’étape produit » :** comptés à l’affichage dans les fichiers (`01_Matrice.csv`, `02_Hypotheses.csv`, `03_Seuils.csv`, `07_Regles.csv` du cadre de décision ; `_SOURCES.csv` ; `catalogue_07.csv` ; `classement_08.csv` ; `recommandations_10.csv` ; `horizon_A1.csv`). Aucun n’est écrit en dur.

### Section 2 — Sources

Tableau lu dans `data/raw/_SOURCES.csv` : jeu de données, producteur, licence déclarée, statut, date de téléchargement.

- **34 fichiers**, issus de **30 jeux de données** ;
- **31 téléchargés** à l’inventaire, **3 recensés seulement**.

**Note sous le tableau :** « La grille de population WorldPop, recensée seulement à l’inventaire, a été téléchargée ensuite pour mesurer l’accès rural et placer les auto-écoles (page Horizon 2031). Son empreinte est dans `sources_A1.csv`. » Le registre reste celui de l’inventaire : il n’est pas réécrit après coup.

Seule page où les sources sont détaillées : les autres n’ont qu’une mention générale (11 §4.2).

### Section 3 — Limites majeures

1. Les accidents ne sont publiés qu’au niveau national : ni préfecture, ni mois, ni âge, ni véhicule.
2. L’activité des auto-écoles n’est pas publiée : une auto-école agréée n’est pas forcément active.
3. L’état du réseau vient du relevé des tronçons de 2020, avec une méthode de notation non publiée. L’annuaire national de la même année donne d’autres parts par état ; aucune ne concorde (page 3, onglet Réseau).
4. Le parc de véhicules en circulation n’est pas publié : il est estimé dans une fourchette.
5. Le coût des actions n’est pas dans les données : les quantités sont des ordres de grandeur, pas des devis.
6. Les recommandations en C demandent une vérification avant tout investissement.
7. La population en âge de conduire ne se raccorde pas d’une source à l’autre : les 18 ans et plus font 51,8 % de la population au recensement de 2022 et 55,6 % dans la projection de 2023. Les permis par habitant en âge de conduire de 2023 et 2024 dépendent de ce saut. Lu dans `erratum_A1.csv` (ligne A1-R1).
8. Les quantités d’ici 2031 sont des estimations, pas des prévisions : elles supposent la population projetée par l’INSEED et les leviers à leur dernière observation.

### Section 4 — Niveaux de preuve

**Légende :** **A** = mesuré (comptage direct) ; **B** = calculé (formule maîtrisée) ; **C** = estimé (approximation ou méthode non documentée).

| Niveau | Indicateurs du cadre d’analyse |
| ------ | ------------------------------ |
| A | 5 |
| B | 10 |
| C | 17 |
| **Total** | **32** |

S’y ajoutent les 3 compléments à l’énoncé (C) et l’accès rural à une route revêtue (C). Décompte lu dans `catalogue_07.csv` (07 §4).

### Section 5 — Questions ouvertes

Les 7 hypothèses non testables : l’énoncé et la colonne « Raison », lus dans `hypotheses_09.csv` et réécrits sans codes (11 §4.2) ; la donnée qui rendrait chaque hypothèse testable, lue dans `consequences_11.csv` (colonne « Donnée manquante affichée »), extraite du 09 §10.

| Hypothèse | Pourquoi elle n’est pas testable | Donnée qui la rendrait testable |
| --------- | -------------------------------- | ------------------------------- |
| Les territoires au réseau dégradé ont un taux d’accidents plus élevé | pas d’accidents par territoire | Accidents et tués par préfecture |
| Les territoires peu dotés en auto-écoles ont un taux d’accidents plus élevé | pas d’accidents par territoire | Accidents et tués par préfecture |
| Le risque routier par habitant varie fortement d’un territoire à l’autre | pas d’accidents par territoire | Accidents et tués par préfecture |
| Le Grand Lomé concentre les accidents en volume, mais le risque par habitant est plus élevé ailleurs, en milieu rural | ni la part du Grand Lomé dans les accidents ni son taux ne sont connus | Accidents et tués par préfecture |
| Certains territoires cumulent forte pression de mobilité, risque élevé, réseau dégradé et faible offre de formation | le cumul complet exige le risque, non mesuré par territoire | Accidents par préfecture ; immatriculations au lieu d’usage |
| Les accidents augmentent en saison des pluies et aux périodes de fêtes | pas de mois | Mois des accidents |
| Les jeunes conducteurs (18–25 ans) sont surreprésentés parmi les conducteurs impliqués | pas d’âge des conducteurs | Âge des conducteurs impliqués |

**Phrase sous le tableau :** « Une base d’accidents par préfecture, avec le mois, l’âge et la catégorie de véhicule, rendrait ces 7 questions testables (recommandation « Créer une base d’accidents par préfecture », page 6). »

### Section 6 — Les zones les moins desservies

Les deux analyses du 10 §4.6, lues dans `zones_10.csv` :

**Analyse 1, par habitant.** Une zone est moins bien desservie si elle est sous la médiane des 6 zones à la fois pour les km de route par habitant (médiane 5,18 pour 10 000 habitants) et pour les auto-écoles par habitant (médiane 0,53 pour 100 000). Résultat : les Savanes et la Maritime hors Grand Lomé.

**Analyse 2, accès rural (Banque mondiale).** Part des ruraux à moins de 2 km d’une route revêtue, sous la médiane des 5 zones rurales. Deux mesures du même indicateur, affichées côte à côte, lues dans `zones_10.csv` et `acces_A1.csv` :

| Zone | Population rurale supposée uniforme | Position | Population placée par la grille WorldPop | Position |
| ---- | ----------------------------------- | -------- | ---------------------------------------- | -------- |
| Maritime hors Grand Lomé | 23,14 % | au-dessus | 39,55 % | au-dessus |
| Centrale | 13,19 % | **sous la médiane** | 25,12 % | au-dessus |
| Kara | 17,49 % | au-dessus | 23,65 % | au-dessus (médiane) |
| Savanes | 16,93 % | au-dessus (médiane) | 23,37 % | **sous la médiane** |
| Plateaux | 13,55 % | **sous la médiane** | 21,26 % | **sous la médiane** |
| **Médiane des 5 zones rurales** | **16,93 %** | | **23,65 %** | |
| **Pays** | **17,17 %** | | **27,12 %** | |

La grille place la population là où elle vit, au lieu de l’étaler sur toute la préfecture : l’accès monte partout. Les Plateaux restent sous la médiane dans les deux mesures. La Centrale en sort, les Savanes y entrent, à 0,28 point.

**Pourquoi elles divergent.** Pour la route, les km par habitant baissent quand la densité monte : la Maritime hors Grand Lomé paraît mal desservie (3,51 km pour 10 000 habitants), alors que ses ruraux ont le meilleur accès (23,1 %) et que, rapportée à la surface, c’est la 2e zone la mieux desservie (79,0 km pour 1 000 km²). Pour la formation, le ratio par habitant reste la bonne mesure : une auto-école a une capacité.

**Conclusion, par dimension.** Formation, inchangée dans les deux mesures : la Centrale, les Savanes et la Maritime hors Grand Lomé. Route : la Centrale et les Plateaux avec la population uniforme ; les Savanes et les Plateaux avec la grille. **La zone qui cumule les deux retards est donc la Centrale dans la première mesure et les Savanes dans la seconde.** Le tableau de conclusion, avec le rang des zones, est en page Priorités (section 1).

**Ce que cela change à l’action, en une phrase, sous le tableau :** « La recommandation de zone de la Centrale garde sa priorité haute : la Centrale reste la zone au réseau le plus dégradé, 40,3 % de km en mauvais état contre 12,8 % dans les Savanes, et la lecture « formation » ne change pas. Un écart de 0,28 point ne sépare pas deux zones à ce niveau de preuve. » Texte lu dans `erratum_A1.csv` (colonne « Conséquence », ligne A1-E1) ; les pages Priorités, Recommandations et Horizon 2031 portent la même note courte, avec un lien vers cette section.

**Limite de l’accès rural**, mot pour mot :

> « L’accès rural est estimé : avec la population rurale supposée répartie uniformément dans chaque préfecture, ou placée par la grille de population WorldPop 2020 (carreaux de 100 m). Les deux mesures sont affichées ; la seconde est la plus fine, mais la grille est elle-même un modèle. »

### Section 7 — Les formules

**Forme :** 5 blocs par thème, en 2 colonnes, repliés sur une seule colonne en écran étroit. Un bloc porte en tête une pastille de la couleur de son thème (11 §4.1) : Mobilité `#2a78d6`, Sécurité routière `#eda100`, Réseau `#eb6834`, Formation `#1baf7a`, Horizon `#0d366b`. Aucune icône ni emoji : la pastille et le titre suffisent.

Chaque formule porte **son nom et son niveau de preuve**, **la formule en toutes lettres**, **ce que chaque terme désigne**, et **un exemple chiffré pris dans les données du projet**. L’exemple est lu dans le fichier de l’indicateur ; il n’est pas recopié.

**Phrase au-dessus des blocs :** « Chaque indicateur affiché dans ce tableau de bord vient d’une de ces formules. L’exemple de chaque bloc reprend une valeur réellement affichée ailleurs dans le tableau de bord. »

#### Bloc 1 — Mobilité

| Formule | Calcul | Termes | Exemple |
| ------- | ------ | ------ | ------- |
| **Immatriculations pour 1 000 habitants** (A) | immatriculations de l’année ÷ population de l’année × 1 000 | immatriculations : véhicules immatriculés dans l’année, un flux et non un parc | 2022 : 93 770 ÷ 8 095 498 × 1 000 = **11,6 pour 1 000 habitants** |
| **Rapport immatriculations / permis** (B) | immatriculations d’une catégorie ÷ permis délivrés de la catégorie correspondante | un rapport élevé signale une tension entre le parc et la formation ; ce n’est pas un nombre de conducteurs sans permis | Cumul 2007–2024 : **40,2 motos immatriculées par permis moto**, contre 0,37 à 2,33 pour les autres catégories |
| **Croissance annuelle moyenne** (B) | (valeur finale ÷ valeur initiale) élevée à la puissance 1 ÷ nombre d’années, moins 1 | sert aux séries longues et à la population par région | Immatriculations 1990–2024 : (88 198 ÷ 6 829) puissance 1/34, moins 1 = **7,8 % par an** |

#### Bloc 2 — Sécurité routière

| Formule | Calcul | Termes | Exemple |
| ------- | ------ | ------ | ------- |
| **Tués pour 100 000 habitants** (B) | tués de l’année ÷ population de l’année × 100 000 | seule la maille nationale est disponible : les accidents ne sont pas publiés par territoire | 2022 : 683 ÷ 8 095 498 × 100 000 = **8,44 pour 100 000 habitants** |
| **Tués pour 10 000 véhicules** (C) | tués de l’année ÷ parc estimé × 10 000 | parc estimé : cumul des immatriculations sur la durée de vie des véhicules, 7 ans pour les motos et 15 ans pour les autres, chacune dans une fourchette | 2024 : 597 ÷ 751 398 × 10 000 = **7,95 pour 10 000 véhicules** (de 6,18 à 10,30) |
| **Gravité** (B) | tués de l’année ÷ accidents constatés de l’année × 100 | une gravité élevée peut venir de la nature des accidents ou de l’accès aux secours ; les données ne permettent pas de trancher | 2022 : 683 ÷ 7 507 × 100 = **9,1 tués pour 100 accidents** |

#### Bloc 3 — Réseau routier

| Formule | Calcul | Termes | Exemple |
| ------- | ------ | ------ | ------- |
| **Part en mauvais état** (C) | km en mauvais état ÷ km évalués × 100 | km évalués = bon + moyen + mauvais + travaux. Les km non évalués sortent du dénominateur ; ils ne comptent jamais pour 0 | Blitta : 69,0 ÷ 101,1 × 100 = **68,2 % en mauvais état** |
| **Km de routes pour 10 000 habitants** (B) | km de routes classées ÷ population × 10 000 | ce rapport baisse quand la densité monte : il mesure la densité du réseau, pas l’accès | Savanes : 528,0 ÷ 1 143 520 × 10 000 = **4,62 km pour 10 000 habitants** |
| **Densité routière** (B) | km de routes classées ÷ surface × 1 000 | surface en km², mesurée en projection métrique | Golfe : 96,8 ÷ 240,8 × 1 000 = **401,9 km pour 1 000 km²** |
| **Accès rural à une route revêtue** (C) | population rurale à moins de 2 km d’une route nationale revêtue ÷ population rurale × 100 | approche de l’indice d’accès rural de la Banque mondiale. Deux mesures : population supposée uniforme, ou placée par la grille WorldPop (section 6) | Pays : **17,2 %** avec la population uniforme, **27,1 %** avec la grille |

#### Bloc 4 — Formation

| Formule | Calcul | Termes | Exemple |
| ------- | ------ | ------ | ------- |
| **Auto-écoles pour 100 000 habitants** (C) | auto-écoles agréées ÷ population × 100 000 | agréées = agréées et antennes agréées. L’activité n’étant pas publiée, l’indicateur reste estimé | Savanes : 4 ÷ 1 143 520 × 100 000 = **0,35 pour 100 000 habitants** |
| **Habitants par auto-école agréée** (B) | population ÷ auto-écoles agréées | lecture inverse de la précédente ; non définie quand il n’y a aucune auto-école agréée, jamais affichée comme 0 | Haho : 305 096 ÷ 0 = **non défini**, aucune auto-école agréée |
| **Distance à l’auto-école agréée la plus proche** (C) | la plus courte distance entre le point de départ de la préfecture et une auto-école agréée | point de départ : le chef-lieu, ou le point d’étiquette de la préfecture quand le chef-lieu manque. Distance à vol d’oiseau | Oti-Sud : **84,0 km**, la plus grande des 39 préfectures |

#### Bloc 5 — Horizon 2031

| Formule | Calcul | Termes | Exemple |
| ------- | ------ | ------ | ------- |
| **Auto-écoles à ouvrir** (C) | arrondi à l’entier supérieur de (1,065 × population ÷ 100 000), moins les auto-écoles agréées déjà présentes ; jamais négatif | 1,065 : la médiane des préfectures qui ont au moins une auto-école agréée. Le calcul se fait **par préfecture**, puis s’additionne : un excédent ailleurs ne comble pas un manque | Haho en 2029 : arrondi supérieur de (1,065 × 334 220 ÷ 100 000) = 4, moins 0 = **4 auto-écoles à ouvrir** |
| **Km à remettre en état** (C) | km en mauvais état, moins 14,35 % des km évalués ; jamais négatif | 14,35 % : la médiane des préfectures évaluées. La quantité ne change pas d’un horizon à l’autre : aucune donnée ne mesure l’usure | Blitta : 69,0 − (14,35 % × 101,1) = **54,5 km à remettre en état** |
| **Permis moto à délivrer dans l’année** (C) | 1,275 × population de 18 ans et plus ÷ 1 000 | 1,275 : le taux des années 2022 à 2024, affiché arrondi ; le calcul utilise le taux exact | 2029 : **6 540 permis moto**, pour 5 131 425 habitants de 18 ans et plus |
| **Cible de la Décennie d’action** (C) | valeur de 2021, diminuée de moitié à l’horizon 2030, sur une trajectoire régulière ; 2031 garde la cible de 2030 | résolution de l’Assemblée générale des Nations unies de 2020 : au moins 50 % de tués et de blessés en moins d’ici 2030 | Tués : la moitié de 680 = **340 tués en 2030** |
| **Plafond de ce que le casque pourrait éviter** (C) | tués attendus × 60 % × 42 % | 60 % : part des usagers de deux ou trois-roues parmi les tués de 2021 (OMS). 42 % : réduction du risque de décès par le casque (revue Cochrane). C’est un plafond : il suppose qu’aucun usager tué ne portait de casque, et le taux de port n’est pas publié | 2031 : **de 144 à 182 tués**, pour un écart à la cible de 231 à 380 |

**Les 5 blocs sont dépliés par défaut.** Un 6e bloc, replié, donne toutes les autres formules du cadre d’analyse, lues dans `catalogue_07.csv` (colonne « Formule »), réécrites sans codes (11 §4.2).

**Sources des exemples :** `indicateurs_07.csv`, `regions_08.csv`, `classement_08.csv`, `horizon_A1.csv`, `national_A1.csv`, `formules_A1.csv`.

### Section 8 — Corrections et contrôles

Deux blocs, dépliables. Avec la section 7, ils tiennent lieu de revue de rigueur et de revue de décision : les documents de validation et de rapport final n’ont pas été écrits.

**Bloc 1 — Ce qu’une analyse plus fine a corrigé.** Lu dans `erratum_A1.csv` : type, document, objet, ce que montre l’annexe, source, conséquence.

| # | Type | Objet | Conséquence |
| - | ---- | ----- | ----------- |
| 1 | Correction | La zone qui cumule les deux retards : les Savanes, et non la Centrale | La recommandation de zone de la Centrale garde sa priorité haute |
| 2 | Réserve | La population de 18 ans et plus après le recensement | Les permis par habitant en âge de conduire de 2023 et 2024 dépendent d’un saut de source |

**Phrase au-dessus :** « Les analyses qui fondent ce tableau de bord ont été gelées étape par étape. Une analyse plus fine, faite ensuite, a corrigé une conclusion et mis un chiffre en réserve. Les deux sont ici, avec leur source. »

**Bloc 2 — Les contrôles.** Un tableau par étape, lu dans les tables de contrôle : nombre de contrôles et nombre de conformes.

| Étape | Table lue |
| ----- | --------- |
| Compréhension des données | `controles_coherence.csv` |
| Préparation des données | `controles_05.csv` |
| Indicateurs | `controles_07.csv` |
| Classement | `controles_08.csv` |
| Diagnostic | `controles_09.csv` |
| Recommandations | `controles_10.csv` |
| Textes du tableau de bord | `controles_11.csv` |
| Horizon 2031 | `controles_A1.csv` |

Le nombre de contrôles et le nombre de conformes sont comptés dans chaque table, à l’affichage : aucun n’est écrit en dur. L’exploration n’a pas de table de contrôle ; ses repères sont les points d’attention de la page 2.

**Phrase sous le tableau :** « Chaque étape vérifie ses propres chiffres avant de passer à la suivante : les sommes, les totaux, les bornes, et chaque chiffre écrit dans le document correspondant. »

### Section 9 — Licences

D’après 03 §9 :

| Source | Licence |
| ------ | ------- |
| HDX (limites administratives, chefs-lieux) | CC BY-IGO |
| OMS (profil du Togo) | CC BY-NC-SA 3.0 IGO, usage non commercial |
| WPP (Nations unies) | CC BY 3.0 IGO |
| DHS | Conditions du programme DHS |
| EHCVM (Banque mondiale) | Conditions de la Banque mondiale, sans redistribution ; citation obligatoire |
| Jeux de l’INSEED et catalogue du géoportail | Licence non déclarée ; usage couvert par l’énoncé |
| WorldPop | CC BY 4.0 ; grille de population 2020, utilisée pour l’accès rural et l’emplacement des auto-écoles (page Horizon 2031) |

### Section 10 — Constat, synthèse chiffrée et limite

**Constat :** « Le tableau de bord montre la décision et son fondement ; cette page dit comment elle a été produite et où elle s’arrête. »

**Synthèse chiffrée :** 9 étapes de travail ; 30 jeux de données ; 32 indicateurs, dont 17 en C ; 18 formules ; 7 questions ouvertes ; 1 correction et 1 réserve.

**Limite :** « Un indicateur en C demande une vérification avant tout investissement. »

**Sources de la page :** `data/raw/_SOURCES.csv`, les 4 tables du cadre de décision, `catalogue_07.csv`, `indicateurs_07.csv`, `classement_08.csv`, `regions_08.csv`, `hypotheses_09.csv`, `consequences_11.csv`, `zones_10.csv`, `recommandations_10.csv`, `acces_A1.csv`, `horizon_A1.csv`, `national_A1.csv`, `erratum_A1.csv`, `formules_A1.csv`, les tables de contrôle de chaque étape.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
