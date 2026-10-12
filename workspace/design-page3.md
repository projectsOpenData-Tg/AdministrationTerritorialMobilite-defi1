## Page 3 — Évolutions et constats

**Objectif :** suivre l’évolution de la mobilité, de la sécurité routière et du réseau, et dire ce que les données confirment, avec les 17 vérifications et hypothèses du 02.

**Nom dans le menu et surtitre :** « Évolutions et constats » (groupe Analyses). La procédure l’appelle « analyse détaillée » (étape 12) ; le nom dit les deux moitiés de la page : ce qui change (Mobilité, Sécurité routière, Réseau) et ce que les données confirment (Synthèse).

**Question de la page :** « Qu’est-ce qui change, et que confirment les données ? »

**Réponse sous le titre** (11 §4.3) : « Les immatriculations ont été multipliées par 4,56 en 20 ans, portées par les motos ; les accidents déclarés augmentent, mais les 6 taux baissent ; 49 tronçons concentrent le mauvais état du réseau. » Les trois chiffres sont lus dans `indicateurs_07.csv` (multiplicateur sur 20 ans de 2022 ; tronçons critiques, ligne du pays) et `taux_09.csv`.

La page a **4 onglets** (maquette §7 : 3 à 5 vues, la première est une vue synthèse) : **Synthèse | Mobilité | Sécurité routière | Réseau**. Les cartes Mobilité et Sécurité routière de la page 1 ouvrent leur onglet.

**Ouverture sur un onglet.** Les onglets sont ceux de la maquette (`onglets(cle, libelles)`, §8.10), avec la clé `evolutions` : l’onglet actif est retenu par son rang dans `st.session_state["evolutions_rang"]` (0 Synthèse, 1 Mobilité, 2 Sécurité routière, 3 Réseau). Le bouton « Voir le détail → » d’une carte de la page 1 écrit ce rang, puis appelle `st.switch_page` vers la page 3 : la page s’ouvre sur l’onglet de la carte, marqué comme actif. Sans passage par la page 1, elle s’ouvre sur la Synthèse. La formation est détaillée en pages 2 et 4, les questions ouvertes en page Méthodologie : la page 3 ne les répète pas.

```text
┌──────────────────────────────────────────────────────────────────┐
│  QU’EST-CE QUI CHANGE, ET QUE CONFIRMENT LES DONNÉES ?            │
├──────────────────────────────────────────────────────────────────┤
│  [ONGLETS : Synthèse | Mobilité | Sécurité routière | Réseau]     │
├──────────────────────────────────────────────────────────────────┤
│  [3 CHIFFRES CLÉS DE L’ONGLET]                                    │
├──────────────────────────────────────────────────────────────────┤
│  [VISUEL PRINCIPAL DE L’ONGLET]                          │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [VISUELS SECONDAIRES — un export CSV sous chaque bloc]           │
├──────────────────────────────────────────────────────────────────┤
│  [LIMITE DE L’ONGLET]                                             │
├──────────────────────────────────────────────────────────────────┤
│  [SYNTHÈSE CHIFFRÉE DE LA PAGE — une puce par onglet]             │
└──────────────────────────────────────────────────────────────────┘
```

**Bandeaux :** chaque onglet a son Constat et sa Limite, à la fin de l’onglet (maquette §8.9). Le Constat est en tête d’onglet pour Synthèse et Réseau, dont le visuel principal est une carte ou un tableau large ; à droite du graphique principal pour Mobilité et Sécurité routière. La maquette permet les deux places (§8.7). La Synthèse chiffrée est commune à la page : une puce par onglet (section 5).

---

### Section 1 — Onglet « Synthèse » : les 17 vérifications et hypothèses

**Ordre de l’onglet :** Constat ; carte des constats et encart national ; tableau des 17 vérifications et hypothèses ; ce que chaque verdict change ; Limite.

**Carte des constats** (visuel principal) : ce que les données confirment, vu sur le Togo, pour le lecteur qui ne lit pas les tableaux. Elle ne montre que ce qui est mesuré par territoire ; chaque couche porte dans la légende le verdict qu’elle illustre.

| Couche | Ce qu’elle montre | Verdict dans la légende | Source |
| ------ | ----------------- | ----------------------- | ------ |
| Fond, par défaut | Les 39 préfectures, chacune de la couleur de sa zone selon la part de km en mauvais état (palette `BLEUS`, 5 classes fixées : moins de 10 %, 10 à 15 %, 15 à 20 %, 20 à 30 %, 30 % ou plus) : de 7,7 % (Grand Lomé) à 40,3 % (Centrale) | « Le réseau est inégalement entretenu : confirmée, 32,6 points d’écart » | `zones_10.csv`, `geo/prefectures.geojson` |
| Tronçons en mauvais état | Les 49 tronçons qui ont des km en mauvais état, tracés en rouge sur la route, épaisseur selon les km en mauvais état | « 49 tronçons sur 84 en mauvais état » | `D4_etat_troncons.csv` (colonne « Noms du tracé »), `geo/routes_classees.geojson` |
| Auto-écoles agréées | Les 132 auto-écoles agréées, en points | « Les auto-écoles sont concentrées dans les grandes villes : confirmée, 84,8 % dans les 4 préfectures urbaines » | `geo/auto_ecoles.geojson`, `hypotheses_09.csv` |

- **Tracé des tronçons.** Chaque tronçon relevé est rattaché au tracé par son nom (04 §5, 05, `correspondance_etat_trace.csv`) : les 84 le sont, les 49 en mauvais état aussi. Le tableau de bord choisit les lignes du tracé dont le nom figure dans « Noms du tracé » : c’est une sélection, pas un calcul. Pour 7 tronçons rattachés par l’axe, l’état est réparti le long de l’axe (niveau C).
- **Réglages** (maquette §8.14, carte des régions) : projection Mercator, sans fond de carte, cadrage explicite sur le Togo ; contours blancs de 0,8 px ; hauteur 620 px ; survol seulement.
- **Valeur écrite sur chaque zone** (« 40,3 % »), en blanc sur les deux classes les plus foncées ; l’étiquette du Grand Lomé est placée sous la côte, reliée par un trait.
- **Légende**, à droite de la carte : les 5 classes avec le nombre de zones de chacune, même vides ; le trait rouge des tronçons (« 49 tronçons sur 84 ; épaisseur selon les km en mauvais état ») ; le point des auto-écoles agréées. Sous la couche qu’elle illustre, l’étiquette du verdict et sa mesure (« confirmée : 32,6 points d’écart entre zones » ; « confirmée : 84,8 % dans les 4 préfectures urbaines »).
- **Info-bulle :** la préfecture et sa zone, la part en mauvais état de la zone ; pour un tronçon, son nom réécrit et ses km en mauvais état sur ses km relevés ; pour une auto-école, sa préfecture.
- **Contours des préfectures** : anneaux extérieurs dans le sens des aiguilles d’une montre, que la cartographie de Plotly attend ; dans l’autre sens, le polygone couvre tout le cadre (constaté sur la maquette).
- **Lien :** « Voir la carte détaillée → » (page 4).

**Encart national**, à droite de la carte (sous la carte sur un écran étroit), pour voir d’un coup d’œil ce qui est par territoire et ce qui est national : ce que les données ne donnent que pour tout le pays. Chaque thème a son étiquette de verdict, son chiffre, une courbe de 92 px avec la première et la dernière valeur écrites, et l’énoncé vérifié.

| Thème | Chiffre | Courbe | Verdict |
| ----- | ------- | ------ | ------- |
| Mobilité | ×4,56 immatriculations de 2002 à 2022 | Immatriculations de l’année, 1990–2024 | confirmée |
| Sécurité routière | Tués pour 100 000 habitants : −29,4 % ; accidents déclarés : +9,4 % (2010–2012 face à 2022–2024) | Tués pour 100 000 habitants, 2010–2024 | nuancée (« les accidents augmentent ») |
| Accidents par territoire | Non publiés : 7 questions restent non testables | — | non testable |

**Phrase sous l’encart :** « Les immatriculations, les permis et les accidents ne sont publiés que pour tout le pays : ils ne se cartographient pas. »

**Ce que la carte ne montre pas, et pourquoi.**
- **Pas d’accidents sur la carte.** Ils ne sont publiés qu’au niveau national (écart 1) : une couleur unique sur tout le pays laisserait croire à une lecture par territoire qui n’existe pas, et les hypothèses sur le risque par territoire sont non testables.
- **Pas de curseur des années sur la carte.** Les données par territoire n’ont qu’une date : l’état du réseau en 2020, les auto-écoles en 2021-2022, la population en 2022. Le temps se lit dans les courbes de l’encart : 1990–2024 pour les immatriculations, 2010–2024 pour la sécurité, les mêmes séries que dans les onglets.

**Maquette validée :** https://claude.ai/artifact/DdUWgdWFBoMSkWF8XSm6ng (version 2, Équipe, 2026-10-07).

**Sources de la carte et de l’encart :** `zones_10.csv`, `D4_etat_troncons.csv`, `hypotheses_09.csv`, `indicateurs_07.csv`, `taux_09.csv`, `geo/prefectures.geojson`, `geo/routes_classees.geojson`, `geo/auto_ecoles.geojson`.


**Filtres :** thème (Mobilité, Sécurité, Réseau, Formation, Réseau et formation) ; verdict (confirmée, infirmée, nuancée, non testable).

**Tableau** lu dans `hypotheses_09.csv`. Aucun code n’est affiché : la colonne « Code » sert au tri et à la correspondance avec le thème, elle est masquée.

| Colonne affichée            | Contenu                                                                                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Thème                       | Fixé par ce plan, d’après le code (table ci-dessous)                                                                                                    |
| Énoncé                     | Colonne « Énoncé »                                                                                                                                     |
| Verdict                      | Colonne « Verdict »                                                                                                                                      |
| Ce que montrent les données | Colonne « Mesure » pour les vérifications et hypothèses testées ; colonne « Raison » pour les non testables. Réécrites à l’affichage (11 §4.2) |
| Niveau                       | Colonne « Niveau » ; « — » pour une non testable                                                                                                      |

| Thème               | Énoncé                                                                                                                          | Verdict                             | Ce que montrent les données                                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Mobilité            | Les immatriculations annuelles ont plus que quadruplé en 20 ans                                                                  | confirmée                          | multiplicateur de 4,56 en 2022, face à 2002                                                                                   |
| Mobilité            | Cette hausse est portée par les motos                                                                                            | confirmée                          | 80,6 % de la hausse de 2002 à 2022 : 59 007 motos sur 73 217 immatriculations de plus                                         |
| Mobilité            | L’écart immatriculations / permis est plus marqué pour les motos que pour les voitures et les poids lourds                     | confirmée                          | 40,20 immatriculations de motos par permis A en cumul 2007–2024 ; de 0,37 à 2,33 pour les autres catégories                 |
| Sécurité           | Plus de 7 500 accidents et 683 morts en 2022                                                                                      | confirmée                          | 7 507 accidents constatés et 683 tués en 2022                                                                                |
| Sécurité           | Les accidents augmentent                                                                                                          | nuancée                            | les accidents constatés montent, de 6 381,7 à 6 980,7 par an ; les tués baissent par habitant et par véhicule              |
| Sécurité           | Les motos sont surreprésentées parmi les véhicules impliqués et les victimes                                                  | confirmée, sur les tués seulement | 60 % des tués de 2021 sont des usagers de deux et trois-roues motorisés, pour 54,7 % à 59,7 % de motos dans le parc estimé |
| Sécurité           | Le taux par habitant et le taux par véhicule évoluent en sens inverse                                                           | infirmée                           | les deux baissent : −29,4 % par habitant, −40,4 % par véhicule                                                              |
| Sécurité           | Le risque routier par habitant varie fortement d’un territoire à l’autre                                                       | non testable                        | pas d’accidents par territoire                                                                                                |
| Sécurité           | Les accidents augmentent en saison des pluies et aux périodes de fêtes                                                          | non testable                        | pas de mois                                                                                                                    |
| Sécurité           | Le Grand Lomé concentre les accidents en volume, mais le risque par habitant est plus élevé ailleurs, en milieu rural          | non testable                        | ni la part du Grand Lomé dans les accidents ni son taux ne sont connus                                                        |
| Sécurité           | Les jeunes conducteurs (18–25 ans) sont surreprésentés parmi les conducteurs impliqués                                        | non testable                        | pas d’âge des conducteurs                                                                                                    |
| Réseau              | Le réseau est inégalement entretenu selon les régions                                                                          | confirmée                          | 32,6 points d’écart entre la Centrale (40,3 % de km en mauvais état) et le Grand Lomé (7,7 %)                              |
| Réseau              | Les territoires au réseau dégradé ont un taux d’accidents plus élevé                                                        | non testable                        | pas d’accidents par territoire                                                                                                |
| Réseau              | Les poids lourds en transit (corridor du port de Lomé vers le nord) pèsent sur l’accidentalité et l’usure de l’axe nord-sud | infirmée                           | le corridor de la RN1 (6 tronçons, 667,7 km) a 18,0 % de km en mauvais état, moins que le pays (21,2 %)                      |
| Formation            | Les territoires peu dotés en auto-écoles ont un taux d’accidents plus élevé                                                  | non testable                        | pas d’accidents par territoire                                                                                                |
| Formation            | Les auto-écoles sont concentrées dans les grandes villes                                                                        | confirmée                          | les 4 préfectures urbaines ont 84,8 % des auto-écoles agréées pour 32,3 % de la population, soit 2,62 fois                 |
| Réseau et formation | Certains territoires cumulent forte pression de mobilité, risque élevé, réseau dégradé et faible offre de formation         | non testable                        | le cumul complet exige le risque, non mesuré par territoire                                                                   |

La dernière colonne reprend ici le sens de la colonne source ; à l’écran, c’est la colonne réécrite qui s’affiche, pas ce résumé.

**Bilan :** 7 confirmées, 2 infirmées, 1 nuancée, 7 non testables.

**Réécriture à l’affichage** (11 §4.2) : chaque code d’indicateur est remplacé par son intitulé, lu dans `catalogue_07.csv` (« O1-09 » devient « Rapport immatriculations / permis, par catégorie ») ; les renvois entre parenthèses ou entre crochets (« (écart 1) », « (PA-03) », « (08 §3.1) ») sont retirés.

**Ce que chaque verdict change pour l’action**, lu dans `consequences_11.csv` (colonne « Conséquence affichée ») : la conséquence que le 09 a retenue pour chaque verdict (09 §10), extraite mot pour mot par `scripts/consequences_11.py`, sans les codes ni les renvois.

| Vérification ou hypothèse                                             | Verdict                   | Ce qui change pour l’action                                                                                                                                                                                 |
| ----------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Les immatriculations ont plus que quadruplé en 20 ans                  | confirmée                | La page d’accueil affiche le multiplicateur mesuré (4,56 en 2022)                                                                                                                                          |
| Cette hausse est portée par les motos                                  | confirmée                | La moto est la catégorie de référence                                                                                                                                                                     |
| Plus de 7 500 accidents et 683 morts en 2022                            | confirmée                | Le tableau de bord affiche le chiffre de la source, avec sa définition                                                                                                                                      |
| Les accidents augmentent                                                | nuancée                  | Le message est « plus de véhicules », pas « une route plus dangereuse »                                                                                                                                 |
| Le réseau est inégalement entretenu selon les régions                | confirmée                | L’entretien se cible par territoire, pas seulement par tronçon                                                                                                                                             |
| L’écart immatriculations / permis est plus marqué pour les motos     | confirmée                | Le levier formation cible d’abord le permis moto                                                                                                                                                            |
| Les motos sont surreprésentées parmi les victimes                     | confirmée, sur les tués | Des mesures ciblées sur les motos (casque, permis moto) deviennent recommandables, après vérification. La surreprésentation est faible (indice de 1,01 à 1,10), mais elle tient sur toute la fourchette |
| Les poids lourds en transit pèsent sur l’axe nord-sud                 | infirmée                 | Le corridor de la RN1 ne devient pas une cible commune d’entretien et de contrôle                                                                                                                          |
| Le taux par habitant et le taux par véhicule évoluent en sens inverse | infirmée                 | La conséquence prévue (« la hausse du risque vient de l’exposition ») ne s’applique pas                                                                                                                |
| Les auto-écoles sont concentrées dans les grandes villes              | confirmée                | Le déficit de formation est rural : ouverture d’auto-écoles hors des villes                                                                                                                               |
| Les 7 non testables                                                     | non testable              | Aucune recommandation ne s’y appuie. La donnée qui les rendrait testables est en page Méthodologie                                                                                                                    |

Les 7 non testables ont le même texte : le tableau les regroupe en une ligne. L’énoncé de chaque ligne est celui de `hypotheses_09.csv` ; il est abrégé ici.

**Constat :** « L’énoncé est vérifié, sauf « les accidents augmentent », qui est nuancé : les accidents déclarés montent, mais les 6 taux baissent. »

**Limite :** « 7 questions restent non testables faute d’accidents par préfecture, par mois et par âge des conducteurs. Les tués sont ceux que déclarent la police et la gendarmerie. »

**Sources de l’onglet :** `hypotheses_09.csv`, `consequences_11.csv`, `catalogue_07.csv`.

---

### Section 2 — Onglet « Mobilité »

**Chiffres clés :**

| Chiffre clé                            | Valeur       | Contexte                                                                           | Niveau | Source                                                   |
| --------------------------------------- | ------------ | ---------------------------------------------------------------------------------- | ------ | -------------------------------------------------------- |
| Immatriculations, sur 20 ans            | ×4,56       | de 2002 à 2022 ; ×1,83 en 2024, mais depuis 2004, année de rupture de la série | B      | `indicateurs_07.csv` (multiplicateur sur 20 ans)       |
| Croissance annuelle moyenne, 1990–2024 | 7,8 % par an | motos : 11,7 % par an ; voitures : 4,2 %                                           | B      | `indicateurs_07.csv` (taux de croissance annuel moyen) |
| Part des motos, 2024                    | 74,4 %       | 22,2 % en 1990                                                                     | B      | `indicateurs_07.csv` (part de chaque catégorie)       |

**Bloc 1 — Immatriculations par groupe, 1990–2024** (visuel principal, à côté du Constat)

- **Choix d’affichage :** volume | part | pour 1 000 habitants.
  - **Volume :** une courbe par groupe (motos, voitures, poids lourds, bus et cars, autres).
  - **Part :** aires empilées à 100 % : les motos passent de 22,2 % en 1990 à 74,4 % en 2024.
  - **Pour 1 000 habitants :** 1,86 en 1990, 11,58 en 2022, 10,45 en 2024 pour l’ensemble.
- **Couleurs :** celles des familles de véhicules de la page 1 (design-page1.md, section 5).
- **Annotations :** ruptures de série de 1995 et de 2004, en pointillé gris ; les 3 dates de contexte de la page 1 (`chronologie_reformes.csv`).
- **Niveau :** A pour le volume ; B pour la part ; pour 1 000 habitants, B en 2010 et en 2022 (années de recensement), C les autres années. Le niveau de chaque année s’affiche dans l’info-bulle.
- **Export :** les trois séries, et la croissance annuelle de chaque groupe, année par année.

**Bloc 2 — Permis par catégorie, 2007–2024**

- **Choix d’affichage :** volume | pour 1 000 habitants en âge de conduire.
  - **Volume :** une courbe par catégorie, de A à F.
  - **Pour 1 000 habitants en âge de conduire :** permis A, 0,07 en 2007 et 2,15 en 2024 ; permis B, 2,08 en 2007 et 4,97 en 2024.
- 2013 non renseignée : la courbe s’interrompt.
- Jamais deux axes verticaux : le choix d’affichage remplace le second axe.
- **Niveau :** A pour le volume ; C pour le taux (âges minimaux et population par âge estimés).

**Bloc 3 — Immatriculations pour un permis, cumul 2007–2024**

Barres horizontales, une par catégorie de permis : A 40,20 · C 2,33 · B 1,29 · E 0,81 · D 0,37. Le permis F n’a pas de barre : aucun véhicule immatriculé ne lui correspond.

**Phrase :** « Sur 2007–2024, 40 motos ont été immatriculées pour un permis moto délivré ; moins de 2,5 véhicules pour un permis dans les autres catégories. »

- **Niveau :** B. **Réserve :** une immatriculation n’est pas un conducteur ; la correspondance entre véhicules et permis suit le décret de 2022 (`correspondance_vehicules_permis.csv`).
- **Export :** le rapport, année par année et en cumul.

**Bloc 4 — Parc estimé, 2009–2024**

Courbe de la valeur centrale, avec la bande de la fourchette. En 2024 : **751 398 véhicules** (de 579 845 à 965 702), dont 449 226 motos.

- **Phrase :** « Le parc en circulation n’est pas publié : il est estimé à partir des immatriculations et d’une durée de vie par groupe (7 ans pour une moto, entre 5 et 10). » La durée de vie est lue dans la colonne « Note ».
- **Niveau :** C. Ce parc sert de dénominateur aux taux par véhicule (onglet Sécurité routière).

**Constat :** « Les immatriculations ont été multipliées par 4,56 de 2002 à 2022, et les motos font 80,6 % de la hausse. Les permis moto suivent de loin : 40 motos immatriculées pour un permis moto sur 2007–2024. »

**Limite :** « Immatriculations de l’année, pas parc en circulation. Ruptures de série en 1995 et 2004. Permis de 2013 non renseignés. Le parc est estimé (C), et les taux par habitant hors 2010 et 2022 reposent sur une population projetée. »

**Sources de l’onglet :** `indicateurs_07.csv` (immatriculations, parts, croissance, immatriculations pour 1 000 habitants, parc estimé, permis, permis pour 1 000 habitants en âge de conduire, rapport immatriculations / permis), `hypotheses_09.csv`, `chronologie_reformes.csv`, `correspondance_vehicules_permis.csv`.

---

### Section 3 — Onglet « Sécurité routière »

**Chiffres clés :**

| Chiffre clé                 | Valeur    | Contexte                                                            | Niveau | Source                             |
| ---------------------------- | --------- | ------------------------------------------------------------------- | ------ | ---------------------------------- |
| Tués pour 100 000 habitants | −29,4 %  | 10,45 en 2010–2012, 7,38 en 2022–2024                             | C      | `taux_09.csv`                    |
| Accidents constatés par an  | +9,4 %    | 6 381,7 en 2010–2012, 6 980,7 en 2022–2024                        | A      | `taux_09.csv`                    |
| Tués estimés par l’OMS    | 2,63 fois | le taux déclaré en 2021 : 22,7 contre 8,62 pour 100 000 habitants | C      | `regions_08.csv` (ligne du pays) |

**Bloc 1 — Les 6 taux : 2010–2012 face à 2022–2024** (visuel principal, à côté du Constat)

Moyennes des 3 premières et des 3 dernières années, lues dans `taux_09.csv` :

| Mesure               | Volume par an                | Pour 100 000 habitants      | Pour 10 000 véhicules      |
| -------------------- | ---------------------------- | --------------------------- | --------------------------- |
| Accidents constatés | 6 381,7 → 6 980,7 (+9,4 %)  | 101,90 → 84,60 (−17,0 %)  | 142,95 → 100,29 (−29,8 %) |
| Blessés             | 8 402,0 → 9 500,3 (+13,1 %) | 134,30 → 115,10 (−14,3 %) | 189,13 → 136,29 (−27,9 %) |
| Tués                | 654,0 → 608,7 (−6,9 %)     | 10,45 → 7,38 (−29,4 %)    | 14,71 → 8,76 (−40,4 %)    |

- **D’abord les trois taux du cadre d’analyse :** tués pour 100 000 habitants, tués pour 10 000 véhicules, accidents pour 100 000 habitants.
- **Puis un bloc séparé, « Compléments à l’énoncé »** (07 §9) : accidents pour 10 000 véhicules, blessés pour 100 000 habitants, blessés pour 10 000 véhicules. Le bloc dit qu’ils ne font pas partie du cadre d’analyse et n’entrent dans aucun verdict.
- **Graphique :** pour chaque mesure, deux barres (2010–2012, 2022–2024).
- **Taux par véhicule :** le parc est estimé dans une fourchette. Le graphique montre la fourchette ; la baisse tient sur toute la fourchette, pour les trois.
- **Volumes :** à côté de chaque taux (règle des volumes).
- **Niveaux** (`taux_09.csv`) : volumes A ; les 6 taux C (les moyennes mêlent des années de population projetée et un parc estimé).

**Bloc 2 — Accidents, blessés et tués, année par année, 2010–2024**

- **Trois petits graphiques**, un par mesure, chacun avec son axe : accidents constatés (3 101 en 2010, 7 507 en 2022, 6 529 en 2024), blessés (9 918 en 2022), tués (470 en 2010, 683 en 2022, 597 en 2024).
- **Variations atypiques marquées** d’un point et de la mention « variation atypique », lue dans la colonne « Note » sans son code : accidents en 2011, 2013, 2015 et 2016 ; tués en 2011 et 2015 ; blessés en 2016. Aucune après 2016.
- **Note sous le graphique :** « D’une année à l’autre, les séries varient fortement avant 2017 : c’est pourquoi l’évolution se lit sur des moyennes de trois ans (bloc 1). »
- **Niveau :** A. Accidents et victimes déclarés par la police et la gendarmerie ; aucune définition publiée du tué.

**Bloc 3 — Les taux, année par année, 2010–2024**

- **Sélecteur :** un taux à la fois, les 3 du cadre d’abord, puis les 3 compléments, signalés comme tels.
- Pour un taux par véhicule, la bande de la fourchette du parc : tués pour 10 000 véhicules, 16,80 en 2011 (de 14,11 à 22,73), 7,95 en 2024 (de 6,18 à 10,30).
- Tués pour 100 000 habitants : de 6,62 (2023) à 12,03 (2014) ; 8,44 en 2022.
- **Niveau :** lu ligne par ligne. Taux par habitant : B en 2010 et en 2022 (années de recensement), C les autres années. Taux par véhicule : C (parc estimé).

**Bloc 4 — Gravité : tués et blessés pour 100 accidents, 2010–2024**

- Deux petits graphiques, chacun avec son axe : tués pour 100 accidents, de 7,9 (2023) à 16,6 (2015) ; blessés pour 100 accidents, de 103,2 (2014) à 201,3 (2010).
- **Niveau :** B.

**Bloc 5 — Tués déclarés et estimation de l’OMS, 2021**

| Repère                                                 | Tués pour 100 000 habitants |
| ------------------------------------------------------- | ---------------------------- |
| Tués déclarés (police et gendarmerie)                | 8,62                         |
| Estimation de l’OMS pour le Togo                       | 22,7                         |
| Moyenne estimée du Bénin, du Ghana et du Burkina Faso | 26,17                        |

**Phrase :** « L’OMS estime le taux de tués à 2,63 fois le taux déclaré. Cette estimation ne corrige pas les chiffres déclarés : les baisses du bloc 1 portent sur les tués déclarés. » Source : `regions_08.csv`, ligne du pays.

**Bloc 6 — Les tués par type d’usager, 2021**

- Barres horizontales : deux et trois-roues motorisés 60 % ; piétons 23 % ; véhicules à 4 roues 11 % ; autres et inconnus 6 % ; cyclistes 0 %.
- **Phrase :** « 60 % des tués sont des usagers de deux et trois-roues motorisés, pour 54,7 % à 59,7 % de motos dans le parc estimé : un peu plus que leur part du parc. » (`hypotheses_09.csv`, mesure de la vérification sur les motos.)
- **Niveau :** C. Une seule année ; ni sexe ni âge ; la catégorie inclut les trois-roues.

**Constat :** « Plus de véhicules, pas une route plus dangereuse : les accidents déclarés augmentent (+9,4 %), mais les 6 taux baissent. »

**Limite :** « Accidents et victimes déclarés par la police et la gendarmerie, au niveau national seulement : ni préfecture, ni mois, ni âge. Aucune définition publiée du tué ; l’OMS en estime 2,63 fois plus. Les taux par véhicule reposent sur un parc estimé (C). »

**Sources de l’onglet :** `taux_09.csv`, `indicateurs_07.csv` (accidents, blessés et tués ; taux annuels ; gravité ; tués par type d’usager), `regions_08.csv`, `hypotheses_09.csv`.

---

### Section 4 — Onglet « Réseau »

L’objectif 3 demande l’état du réseau « par tronçon et par région : bon état, état moyen, mauvais état, travaux en cours ». L’onglet montre les 84 tronçons relevés, avec leurs km dans chaque état, en zones ou en régions. Les préfectures sont en page 2.

**Maille :** zones (par défaut) | régions. Elle règle le filtre du tableau des tronçons (bloc 1) et le contenu du bloc 2. Le bloc 3 n’existe que par zone.

**Chiffres clés :**

| Chiffre clé               | Valeur    | Contexte                           | Niveau | Source                                       |
| -------------------------- | --------- | ---------------------------------- | ------ | -------------------------------------------- |
| Réseau évalué           | 3 163 km  | routes nationales, relevé de 2020 | C      | `regions_08.csv` (ligne du pays)           |
| En mauvais état           | 21,2 %    | 669,34 km                          | C      | `regions_08.csv` (ligne du pays)           |
| Tronçons en mauvais état | 49 sur 84 | 34 revêtus, 15 non revêtus       | C      | `indicateurs_07.csv` (tronçons critiques) |

**Bloc 1 — Les 84 tronçons relevés et leur état** (visuel principal, à côté du Constat)

Tableau lu dans `D4_etat_troncons.csv`, la table du relevé préparée au 05, d’où le 07 tire les tronçons critiques :

| Colonne affichée                                             | Contenu                                                             |
| ------------------------------------------------------------- | ------------------------------------------------------------------- |
| Tronçon                                                      | Colonne « Tronçon », sans le code du relevé (règle ci-dessous) |
| Type                                                          | Route nationale revêtue ou non revêtue                            |
| Km en bon état, en état moyen, en mauvais état, en travaux | Colonnes`km_bon`, `km_moyen`, `km_mauvais`, `km_travaux`    |
| Km relevés                                                   | Colonne`km_total`                                                 |
| Zones traversées, ou régions traversées                    | Selon la maille                                                     |
| Préfectures traversées                                      | Colonne « Préfectures traversées »                              |

- **Vue par défaut :** les 49 tronçons qui ont des km en mauvais état, triés par km en mauvais état, puis par km relevés. Le bouton « Afficher les 84 tronçons » ajoute les 35 tronçons sans km en mauvais état.
- **Filtres :** zone ou région traversée, selon la maille ; type de route.
- **Dans chaque ligne**, une barre empilée des 4 états, aux couleurs du bloc 3, pour lire l’état d’un coup d’œil.

**Les 6 premiers :**

| Tronçon                                 | Type     | Bon   | Moyen | Mauvais | Travaux | Km relevés | Zones traversées                             |
| ---------------------------------------- | -------- | ----- | ----- | ------- | ------- | ----------- | --------------------------------------------- |
| RN19 KARA-KABOU-FRE GHANA                | revêtue | 0,21  | 7,54  | 76,25   | 0       | 84,01       | Kara                                          |
| RN1 BABAME-SOKODE-ALEHERIDE              | revêtue | 39,90 | 55,59 | 59,10   | 0       | 154,59      | Centrale                                      |
| RN14 SOKODE-TCHAMBA-KABOLI-FRE BENIN     | revêtue | 0,10  | 27,22 | 59,10   | 0       | 86,43       | Centrale                                      |
| RN27 LANGABOU-YEGUE-FRE GHANA            | revêtue | 0,83  | 9,80  | 56,05   | 0       | 66,67       | Centrale                                      |
| RN1 AMAKPAPE-ATAKPAME- BABAME            | revêtue | 50,31 | 51,31 | 38,12   | 0       | 139,74      | Plateaux, Centrale, Maritime hors Grand Lomé |
| RN30 ADETA(RN5)-NDIGBE-APEYEME-FRE GHANA | revêtue | 0     | 0     | 33,50   | 0       | 33,50       | Plateaux                                      |

En km, relevé de 2020. Pays : 997,02 km en bon état, 735,54 en état moyen, 669,34 en mauvais état, 761,57 en travaux, sur 3 163,49 km relevés.

- **Concordance avec le 07 :** les 49 tronçons de la vue par défaut sont les tronçons critiques de `indicateurs_07.csv`, avec les mêmes km en mauvais état (669,34 km en tout). Le contrôle est au 11 §7.
- **Lien :** « Les 10 premiers sont la cible de la recommandation « Remettre en état les 10 tronçons les plus dégradés » → » (page 6).
- **Note sous le tableau :** « Le corridor de la RN1, du port de Lomé au nord (6 tronçons, 667,7 km), a 18,0 % de km en mauvais état : moins que le pays (21,2 %). » (`hypotheses_09.csv`.)

**Réécriture des noms de tronçon** (11 §4.2) : quand le nom commence par le code du relevé (« TGR… »), ce code est retiré. S’il est collé au numéro de route, le numéro est gardé : « TGRKRRRN19 KARA-KABOU-FRE GHANA » devient « RN19 KARA-KABOU-FRE GHANA ». Sinon, le code part seul : « TGRKRT KOUMEA-SIOU » devient « KOUMEA-SIOU ». Le reste du nom est gardé tel que publié ; la légende du tableau dit « FRE : frontière ». Les noms sans code (« RN1 AMAKPAPE-ATAKPAME- BABAME », « DAVIE-AMAKPAPE ») ne changent pas.

**Bloc 2 — Selon la maille**

*Maille zones :* les tronçons en mauvais état par zone traversée (`indicateurs_07.csv`, tronçons critiques, maille « Zone »).

| Zone                      | Tronçons | Km en mauvais état |
| ------------------------- | --------- | ------------------- |
| Plateaux                  | 23        | 292,15              |
| Centrale                  | 6         | 236,25              |
| Kara                      | 8         | 108,68              |
| Maritime hors Grand Lomé | 11        | 88,24               |
| Savanes                   | 8         | 66,79               |
| Grand Lomé               | 4         | 21,55               |

**Note :** « Un tronçon qui traverse plusieurs zones compte dans chacune, pour tous ses km : les lignes ne s’additionnent pas. Pays : 49 tronçons, 669,34 km. »

*Maille régions :* l’état par région (`regions_08.csv`, lignes « Région »).

| Région  | Km évalués | Km en mauvais état | Part en mauvais état |
| -------- | ------------ | ------------------- | --------------------- |
| Centrale | 437,2        | 176,3               | 40,3 %                |
| Plateaux | 965,6        | 270,7               | 28,0 %                |
| Kara     | 694,5        | 105,4               | 15,2 %                |
| Savanes  | 521,2        | 66,8                | 12,8 %                |
| Maritime | 545,1        | 50,1                | 9,2 %                 |

**Note :** « Ici, les km en mauvais état sont répartis le long du tracé, préfecture par préfecture : les lignes s’additionnent (669,34 km). Les tronçons d’une région se lisent dans le bloc 1, avec le filtre par région. »

**Bloc 3 — L’état par type de route et par zone, 2020**

Barres empilées, une par zone et par type (route nationale revêtue, non revêtue), en km par état : bon, moyen, mauvais, travaux, non évalué (`indicateurs_07.csv`, km par type de route et par état). Le Grand Lomé n’a aucune route nationale non revêtue. En maille régions, le bloc reste en 6 zones, avec la mention « par zone seulement » : le tableau de bord n’additionne pas les zones.

**Bloc 4 — Une autre publication de 2020 : l’annuaire national, 2020–2022**

- **Barres groupées** par année, part des routes nationales par état, revêtues et non revêtues ensemble : mauvais état **29,75 %** en 2020, 30,47 % en 2021, 19,63 % en 2022 (`D4_etat_national_pct.csv`).
- **Phrase :** « Pour 2020, l’annuaire national donne 29,75 % de routes nationales en mauvais état, le relevé des tronçons 21,2 % : les deux publications ne concordent sur aucune part. Le tableau de bord s’appuie sur le relevé, le seul à donner l’état par tronçon et par préfecture. Dans l’annuaire, la part en mauvais état baisse en 2022. »
- **Jamais sur le même graphique** que les blocs 1 à 3 (07, réserve de l’évolution de l’état).
- **Niveau :** C. 2020 « en travaux » des routes non revêtues : non renseigné.

**Constat :** « Le mauvais état se concentre sur 49 des 84 tronçons : ceux qui traversent les Plateaux en portent le plus (292,15 km, 23 tronçons), puis ceux de la Centrale (236,25 km, 6 tronçons). »

**Limite :** « État relevé en 2020, sur les routes nationales seulement, avec une méthode de notation non publiée. L’annuaire national de la même année donne d’autres parts (29,75 % en mauvais état, contre 21,2 %). Les tronçons sont rattachés au tracé par leur nom ; pour 7 d’entre eux, l’état est réparti le long de l’axe. »

**Sources de l’onglet :** `regions_08.csv`, `indicateurs_07.csv` (tronçons critiques, km par type de route et par état), `D4_etat_troncons.csv`, `hypotheses_09.csv`, `D4_etat_national_pct.csv`.

---

### Section 5 — Synthèse chiffrée de la page

**Chiffre-titre :** ×4,56, « les immatriculations de 2022 face à celles de 2002 ».

**Puces :**

- **7 vérifications confirmées sur 17**, 2 infirmées, 1 nuancée, 7 non testables. *(détail : onglet « Synthèse »)*
- **74,4 % des immatriculations de 2024 sont des motos**, et 40 motos sont immatriculées pour un permis moto sur 2007–2024. *(détail : onglet « Mobilité »)*
- **Tués pour 100 000 habitants : 10,45 puis 7,38**, de 2010–2012 à 2022–2024, alors que les accidents déclarés augmentent de 9,4 %. *(détail : onglet « Sécurité routière »)*
- **49 tronçons sur 84 en mauvais état, 669,34 km**, dont 292,15 km sur les tronçons qui traversent les Plateaux. *(détail : onglet « Réseau »)*

---

### Section 6 — Sources de la page

`hypotheses_09.csv`, `consequences_11.csv`, `taux_09.csv`, `regions_08.csv`, `catalogue_07.csv`, `indicateurs_07.csv`, `chronologie_reformes.csv`, `correspondance_vehicules_permis.csv`, `D4_etat_troncons.csv`, `D4_etat_national_pct.csv`, `zones_10.csv`, `geo/prefectures.geojson`, `geo/routes_classees.geojson`, `geo/auto_ecoles.geojson`.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
