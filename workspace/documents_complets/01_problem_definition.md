# 01 — Problem Definition

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.3 — **Date :** 2026-10-03 — **Statut :** **figé** le 2026-10-03
**Validé par :** [noms à compléter]
**Sources :** `workspace/_PROJECT.txt` (énoncé), `methodology/_PROCEDURE_METHODOLOGIE.txt` (procédure)

> Écrit avant tout profilage des données. Une fois validé, ce document n’est plus modifié : il sert de référence pour mesurer l’écart entre ce que l’on croyait du sujet et ce que les données permettent. Les seuils, pondérations et règles de calcul détaillées relèvent du `02_decision_matrix`.

---

## 1. Contexte

L’énoncé pose trois constats :

- les immatriculations annuelles ont plus que quadruplé en vingt ans, portées par les motos ;
- les accidents augmentent : plus de 7 500 accidents et 683 morts en 2022 ;
- le réseau routier est inégalement entretenu selon les régions.

Il demande un tableau de bord qui mesure l’évolution de la mobilité et de la sécurité routière, et des recommandations pour une mobilité plus sûre. Données ouvertes annoncées : immatriculations, permis, accidents, état et tracé du réseau, auto-écoles, population.

> **Lecture :** le parc motorisé croît vite, surtout en motos. La formation des conducteurs et le réseau routier ont-ils suivi, et où ce décalage va-t-il de pair avec un risque routier plus élevé ?

---

## 2. Décision à éclairer

### 2.1 Décision

> **Identifier les régions et préfectures où la croissance du parc motorisé, le déficit de formation des conducteurs et la dégradation du réseau se cumulent avec un risque routier élevé, pour y cibler en priorité des actions de sécurité routière, de formation et d’entretien.**

Le tableau de bord montrera qu’un territoire **cumule** ces caractéristiques. Il ne prétendra pas qu’elles **causent** les accidents : les données ne permettent pas de le démontrer.

**Ce que « cibler en priorité » produit :** un classement des territoires, décomposé par dimension (mobilité, risque, réseau, formation), avec la population concernée affichée à côté. Le décideur voit les territoires en tête de classement et le seuil qui les y a fait entrer. La méthode de classement est fixée dans le 02 ; un score composite n’est retenu que si l’exploration le justifie (procédure, étape 09).

### 2.2 Utilisateurs

| Utilisateur                                              | Décision qu’il prend                                      |
| -------------------------------------------------------- | --------------------------------------------------------- |
| Ministère chargé des transports                          | Où renforcer la formation et le contrôle des permis       |
| Organisme chargé de la sécurité routière                 | Où concentrer contrôles et sensibilisation                |
| Ministère des travaux publics, fonds d’entretien routier | Quels tronçons entretenir en premier                      |
| Collectivités, dont le District autonome du Grand Lomé   | Situer leur territoire par rapport à la médiane nationale |

Noms exacts des institutions à confirmer avec les producteurs des données.

### 2.3 Cadre

| Élément                            | Choix                                                                                                           |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Mailles                            | National (tendances) → région (comparaison) → préfecture (ciblage). Tronçon pour le réseau uniquement           |
| Découpage                          | 5 régions administratives et 39 préfectures, à confirmer. Le Grand Lomé (préfectures du Golfe et d’Agoè-Nyivé) fait partie de la région Maritime |
| Zones d’analyse                    | 6 zones, comme l’INSEED : Grand Lomé, Maritime hors Grand Lomé, Plateaux, Centrale, Kara, Savanes. Le Grand Lomé regroupe 62 % des habitants de la Maritime : fondu dans la région, il masquerait le reste de la Maritime |
| Brique commune                     | La préfecture : toute donnée est rattachée à une préfecture, puis agrégée en 5 régions ou en 6 zones selon le besoin |
| Période                            | De la première à la dernière année disponible (environ 20 ans)                                                  |
| Temporalité                        | Annuelle pour les séries longues ; mensuelle si la source le permet (saisonnalité, ruptures)                    |
| Désagrégations                     | Sexe, âge, type d’usager, catégorie de véhicule, immatriculé ou non : toutes optionnelles, selon les données. Détail par objectif au §3 |
| Année de référence des croisements | 2022 par défaut : recensement (RGPH-5) et chiffres de l’énoncé. Si les données couvrent une année plus récente et que la population de cette année est disponible (projections INSEED), on prend la plus récente. Si une couche manque pour l’année retenue, on croise sur l’année la plus proche et l’écart est affiché |
| Unité de décision                  | Préfecture si les accidents y sont ventilés ; sinon les 6 zones ; sinon national. Dans ce dernier cas, O5 ne peut plus croiser risque et territoire : les recommandations s’organisent par levier (O1, O3, O4). Limite majeure, à signaler dès l’étape 03 |
| Population                         | Une seule source pour tous les taux : recensement 2022, projections officielles pour les séries                 |
| Livrable                           | Tableau de bord interactif (.zip) en Python (Streamlit)                                                         |

### 2.4 Résultat attendu

Le tableau de bord permet à un décideur de passer d’une vision nationale à un diagnostic territorial, dans l’ordre des objectifs : comment évolue la mobilité → où se situe le risque → où sont les déficits de réseau et de formation → quels territoires cumulent les enjeux, et quel levier actionner.

---

## 3. Objectifs

Les cinq objectifs de l’énoncé sont conservés tels quels : le jury évalue sur eux. Les objectifs 1 à 4 décrivent la situation, l’objectif 5 en tire la décision.

| Obj. | Dimension                 | Rôle dans l’analyse                 | Données        |
| ---- | ------------------------- | ----------------------------------- | -------------- |
| O1   | Mobilité                  | Exposition : véhicules et conducteurs formés | D1, D2, D7 |
| O2   | Sécurité                  | Conséquences : accidents et victimes | D1, D3, D7    |
| O3   | Infrastructure            | Qualité du réseau                   | D4, D5         |
| O4   | Infrastructure, formation | Couverture du territoire            | D5, D6, D7     |
| O5   | Croisement                | Priorités et actions                | Tous           |

Niveau de preuve de chaque indicateur : **A** mesuré, **B** calculé, **C** estimé (voir §4).

### 3.1 Objectif 1 — Retracer l’évolution des véhicules immatriculés et des permis de conduire

**Énoncé :** Retracer l’évolution des véhicules immatriculés (voitures, motos, poids lourds) et des permis de conduire délivrés par catégorie.

**Question décisionnelle :** La formation des conducteurs suit-elle la croissance du parc, catégorie par catégorie ?

**Ce que l’objectif demande :**

- Retracer, depuis la première année disponible, les immatriculations par catégorie : motos, voitures, poids lourds, et aussi bus, cars et autres catégories présentes dans les données.
- Retracer les permis délivrés par catégorie sur la même période.
- Mettre les deux séries côte à côte, catégorie par catégorie. C’est ce rapprochement qui donne son sens à l’objectif : la formation suit-elle le parc ?
- Rapporter les deux à la population.

**Temporalité et désagrégations :**

- **Année** pour les séries longues ; **mois** si la source le permet, pour repérer saisonnalité et ruptures.
- **Sexe et âge** : pour les permis, car le titulaire est une personne. Pas pour les immatriculations : seul le propriétaire du véhicule a un sexe et un âge, et c’est rarement publié.
- **Région** : avec prudence (voir vigilance).

**Indicateurs :**

| Indicateur                                        | Calcul                                                                 | Preuve |
| ------------------------------------------------- | ---------------------------------------------------------------------- | ------ |
| Immatriculations par catégorie (an, mois)         | Comptage                                                               | A      |
| Part de chaque catégorie, dont les motos          | Immatriculations de la catégorie / total                               | B      |
| Croissance annuelle et taux de croissance moyen   | Variation d’une année sur l’autre ; (dernière / première)^(1/n) − 1    | B      |
| Immatriculations pour 1 000 habitants             | Immatriculations / population × 1 000                                  | B      |
| Parc estimé                                       | Cumul des immatriculations sur une durée de vie supposée               | C      |
| Permis délivrés par catégorie (an, mois)          | Comptage                                                               | A      |
| Permis pour 1 000 habitants, par catégorie        | Permis / population en âge de conduire × 1 000                         | B      |
| Permis par sexe et tranche d’âge                  | Comptage, part des femmes                                              | A      |
| Rapport immatriculations / permis, par catégorie  | Immatriculations d’une catégorie / permis de la catégorie correspondante | B    |

**Points de vigilance :**

- **Flux et stock.** Les immatriculations annuelles sont un flux : quatre fois plus d’immatriculations ne veut pas dire un parc quatre fois plus grand.
- **Lieu d’enregistrement et lieu d’usage.** Beaucoup de véhicules et de permis sont enregistrés à Lomé et utilisés ailleurs. Les chiffres régionaux mesurent l’activité administrative, pas le parc ni les conducteurs de la région.
- **Motos non immatriculées.** Elles sont absentes par construction : le parc réel est sous-estimé.
- **Pics administratifs.** Une campagne de régularisation ou une réforme peut créer une hausse ponctuelle sans hausse réelle du parc.
- **Le rapport immatriculations / permis signale une tension.** Il ne compte pas les conducteurs sans permis. Il est moins net pour les voitures (plusieurs conducteurs par véhicule, flottes d’entreprise) : les catégories se comparent entre elles, pas à un seuil absolu.
- **Correspondance véhicule / permis.** Elle n’est pas toujours un pour un (un permis poids lourds suppose souvent un permis voiture). Elle suit la nomenclature togolaise, à confirmer.

---

### 3.2 Objectif 2 — Analyser la sécurité routière

**Énoncé :** Analyser la sécurité routière : accidents, blessés et morts, rapportés à la population et au nombre de véhicules.

**Question décisionnelle :** Où, quand et pour quels usagers le risque routier est-il le plus élevé ?

**Ce que l’objectif demande :**

Deux lectures du même risque, toutes deux exigées :

1. **Par habitant** : le risque pour la population. Permet de comparer les territoires entre eux, et le Togo à d’autres pays.
2. **Par véhicule** : le risque à exposition égale. Dit si la route devient plus dangereuse, ou s’il y a simplement plus de véhicules.

Les deux taux peuvent évoluer en sens inverse : c’est un résultat en soi. Les territoires se comparent par des taux ; le volume reste affiché à côté.

**Réponses aux questions de départ :**

- **Faut-il utiliser le parc en circulation ?** Le parc roulant est le bon dénominateur, mais il n’est presque jamais mesuré. À défaut, on prend le parc immatriculé s’il est publié ; sinon le cumul des immatriculations, étiqueté C. Ce cumul surestime le parc (les véhicules retirés ne sont pas déduits) ; les véhicules non immatriculés et étrangers en transit jouent en sens inverse. Le taux par véhicule sera probablement national seulement, car le parc par territoire n’est pas fiable (voir O1).
- **Faut-il montrer les causes ?** Seulement si la source les déclare (vitesse, alcool, défaut de maîtrise, état du véhicule, état de la route…). Elles sont alors affichées comme « cause déclarée », avec leur part de non-renseignés.
- **Véhicules immatriculés ou non ?** Seulement si les données d’accidents le précisent.
- **Sexe et âge ?** Oui pour les victimes, si la source les fournit.

**Temporalité et désagrégations :**

- **Année**, et **mois** si disponible, pour la saisonnalité ; jour et heure si disponibles.
- **Victimes** : sexe, âge, type d’usager (piéton, cycliste, motocycliste, automobiliste, occupant de poids lourd ou de bus).
- **Véhicules impliqués** : catégorie (moto, voiture, poids lourd, bus), immatriculé ou non.
- **Gravité** : tué, blessé grave, blessé léger.
- **Territoire** : région, préfecture, tronçon si disponible.

**Indicateurs :**

| Indicateur                                              | Calcul                                                              | Preuve                       |
| ------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------- |
| Accidents, blessés, tués (an, mois)                     | Comptage                                                            | A                            |
| Tués pour 100 000 habitants                             | Tués / population × 100 000                                         | B                            |
| Accidents corporels pour 100 000 habitants              | Accidents corporels / population × 100 000                          | B                            |
| Tués pour 10 000 véhicules                              | Tués / parc × 10 000                                                | B si parc publié, C si proxy |
| Tués pour 100 accidents corporels                       | Tués / accidents corporels × 100                                    | B                            |
| Blessés pour 100 accidents corporels                    | Blessés / accidents corporels × 100                                 | B                            |
| Accidents par catégorie de véhicule impliqué            | Part de chaque catégorie ; taux pour 10 000 véhicules de la catégorie | B ou C                     |
| Surreprésentation d’une catégorie                       | Part dans les accidents / part dans le parc                         | B ou C                       |
| Victimes par type d’usager, sexe et âge                 | Comptage, parts                                                     | A                            |
| Part des véhicules non immatriculés parmi les impliqués | Non immatriculés / véhicules impliqués                              | A, si la donnée existe       |
| Saisonnalité                                            | Accidents du mois / moyenne mensuelle                               | B                            |
| Accidents pour 100 km de route classée (optionnel)      | Accidents / km de route × 100                                       | B                            |

**Points de vigilance :**

- **Sous-déclaration.** Les accidents sans intervention des forces de l’ordre et les décès survenus à l’hôpital peuvent manquer. Les estimations de l’OMS, souvent plus élevées, servent de repère, pas de correction.
- **Véhicules en transit.** Des poids lourds immatriculés à l’étranger sont impliqués dans des accidents au Togo, mais absents des immatriculations togolaises.
- **Véhicule impliqué, véhicule responsable et véhicule de la victime** sont trois choses différentes.
- **Accès aux secours.** La gravité dépend aussi de la distance aux soins, absente des données : un fort taux de tués en zone isolée ne désigne pas forcément la route.
- **Petits volumes.** Un taux calculé sur peu d’accidents varie fortement d’une année à l’autre : lisser sur plusieurs années si besoin.
- **Variables probablement absentes :** causes, vitesse, éclairage, signalisation.

---

### 3.3 Objectif 3 — Évaluer l’état du réseau routier par tronçon et par région

**Énoncé :** Évaluer l’état du réseau routier par tronçon et par région : bon état, état moyen, mauvais état, travaux en cours.

**Question décisionnelle :** Où le réseau est-il dégradé, et sur quels types de routes ?

**Ce que l’objectif demande :**

Trois lectures du même jeu de données :

1. **Par tronçon.** La source découpe chaque route en segments. Chaque segment porte l’un des quatre états de l’énoncé : bon, moyen, mauvais, travaux en cours. On les affiche tels quels : liste et carte colorée par état.
2. **Par région et par préfecture.** On n’attribue pas *un* état unique à un territoire. On calcule la **répartition de ses kilomètres** entre les quatre états.
3. **Par type de route** : nationale, régionale, préfectorale, urbaine, rurale, selon la classification de la source. Une nationale dégradée n’a pas le même poids qu’une piste rurale dégradée.

Si plusieurs relevés existent, on montre l’évolution : amélioration ou dégradation.

Exemple de lecture (valeurs fictives) :

| Tronçon | Route   | Type      | Région   | Longueur (km) | État             |
| ------- | ------- | --------- | -------- | ------------: | ---------------- |
| T-012   | Route A | Nationale | Région X |            42 | Mauvais          |
| T-013   | Route A | Nationale | Région X |            35 | Travaux en cours |
| T-087   | Route B | Régionale | Région Y |            28 | Bon              |

| Région   | Bon    | Moyen | Mauvais | Travaux | % km en mauvais état |
| -------- | -----: | ----: | ------: | ------: | -------------------: |
| Région X | 120 km | 80 km |  150 km |   35 km |                 39 % |

O3 mesure la **qualité** du réseau. Sa **quantité** rapportée au territoire et à la population (densité routière) relève de O4.

**Indicateurs :**

| Indicateur                                  | Calcul                                                  | Preuve |
| ------------------------------------------- | ------------------------------------------------------- | ------ |
| Km par état                                 | Somme des longueurs par état                            | B      |
| Part des km en mauvais état                 | Km en mauvais état / km évalués                         | B      |
| Part des km en travaux                      | Km en travaux / km évalués                              | B      |
| Km par type de route et par état            | Somme des longueurs par type et par état                | B      |
| Tronçons critiques                          | Tronçons en mauvais état sur le réseau national         | A      |
| Part du réseau non évaluée                  | Km sans état / km total                                 | B      |
| Évolution de l’état (si plusieurs relevés)  | Variation de la part de km par état entre deux relevés  | B      |

**Points de vigilance :**

- **Pondérer par la longueur**, jamais par le nombre de tronçons : un tronçon de 2 km ne pèse pas comme un tronçon de 60 km.
- **Tronçon à cheval sur deux territoires** : le découper par intersection géographique, ou le rattacher là où il est le plus long. La règle est fixée dans le 02.
- **Date des relevés** : des « travaux en cours » relevés il y a plusieurs années peuvent être terminés.
- **Méthode de notation** (inspection visuelle, mesure) : à documenter. Sans documentation, niveau de preuve C.
- **Revêtue ou non** : une piste en bon état et une route bitumée en bon état ne sont pas comparables. Les distinguer si la donnée existe.

---

### 3.4 Objectif 4 — Cartographier le réseau routier classé et les auto-écoles

**Énoncé :** Cartographier le réseau routier classé et les auto-écoles par région et par préfecture, et les rapporter à la population.

**Question décisionnelle :** Quels territoires manquent de routes classées et d’auto-écoles au regard de leur population ?

**Ce que l’objectif demande :**

Une carte interactive à couches, lisible par région et par préfecture :

- limites des régions et des préfectures ;
- réseau routier classé, coloré par classe de route ;
- auto-écoles en points ;
- fond coloré par population ou par indicateur ;
- info-bulle avec la population, les km de routes et le nombre d’auto-écoles.

La carte ne suffit pas : le cœur de l’objectif est de **rapporter l’offre à la population**, en ratio et en habitants concernés. L’offre de formation se lit de trois façons, selon les données disponibles :

- **combien** : nombre d’auto-écoles par habitant ;
- **à quelle distance** : éloignement de la population à l’auto-école la plus proche ;
- **avec quelle capacité** : moniteurs, véhicules, candidats formés.

**Indicateurs :**

| Indicateur                                       | Calcul                                                                  | Preuve                             |
| ------------------------------------------------ | ----------------------------------------------------------------------- | ---------------------------------- |
| Km de routes classées, par classe                | Somme des longueurs                                                     | B                                  |
| Densité routière                                 | Km / 1 000 km² de surface                                               | B                                  |
| Km de routes pour 10 000 habitants               | Km / population × 10 000                                                | B                                  |
| Nombre d’auto-écoles (agréées, actives si connu) | Comptage                                                                | A                                  |
| Auto-écoles pour 100 000 habitants               | Auto-écoles / population × 100 000                                      | B                                  |
| Habitants par auto-école                         | Population / auto-écoles                                                | B                                  |
| Préfectures sans auto-école                      | Comptage                                                                | B                                  |
| Distance à l’auto-école la plus proche           | Distance moyenne, et population à plus de X km (X fixé dans le 02)      | B, ou C sans grille de population  |
| Capacité de formation (si disponible)            | Moniteurs, véhicules, candidats formés par auto-école                   | A                                  |

**Points de vigilance :**

- **Géocodage des auto-écoles** : vérifier que chaque point tombe dans la bonne préfecture, dédoublonner, distinguer agréée et active.
- **Population** : à la même maille et au même millésime que l’offre.
- **Intensité et volume** : une préfecture peut avoir un ratio faible mais peu d’habitants concernés. Afficher les deux, et compter le manque en habitants.
- **Voisinage** : une préfecture sans auto-école peut être servie par sa voisine. C’est le rôle de l’indicateur de distance.
- **Seuils de desserte** (à partir de quand un territoire est sous-doté) : fixés dans le 02.

---

### 3.5 Objectif 5 — Proposer des recommandations ciblées

**Énoncé :** Proposer des recommandations ciblées pour améliorer la sécurité routière, la formation des conducteurs et l’entretien du réseau dans les régions les moins bien desservies.

**Question décisionnelle :** Où agir en premier, sur quel levier, et pour combien d’habitants ?

**Ce que l’objectif demande :**

Passer du diagnostic à l’action, en croisant les objectifs 1 à 4 par territoire. L’énoncé nomme trois leviers (sécurité routière, formation des conducteurs, entretien du réseau) et une cible (les régions les moins bien desservies).

**Ce que chaque objectif apporte au croisement :**

| Objectif | Apport au profil du territoire                                                                        |
| -------- | ----------------------------------------------------------------------------------------------------- |
| O1       | Pression de mobilité : croissance des immatriculations, écart immatriculations / permis (fragile par territoire, voir O1) |
| O2       | Niveau de risque : tués et accidents pour 100 000 habitants, gravité                                  |
| O3       | État du réseau : part de km en mauvais état, tronçons critiques                                       |
| O4       | Couverture : routes et auto-écoles par habitant, distance à l’auto-école                              |

**Profil du territoire**, qui oriente le levier :

| Profil                               | Levier                                    | Acteur probable                          | Indicateur de suivi                              |
| ------------------------------------ | ----------------------------------------- | ---------------------------------------- | ------------------------------------------------ |
| Risque élevé et réseau dégradé       | Entretien des tronçons prioritaires       | Travaux publics, fonds d’entretien       | Part de km en mauvais état sur les tronçons ciblés |
| Risque élevé et déficit de formation | Formation et permis                       | Ministère des transports, auto-écoles    | Auto-écoles pour 100 000 habitants, permis délivrés |
| Risque élevé sans déficit mesuré     | Contrôles, sensibilisation                | Sécurité routière, police, gendarmerie   | Tués pour 100 000 habitants                      |
| Déficits sans risque mesuré          | Prévention ; vérifier la sous-déclaration | Sécurité routière, collectivités         | Accidents déclarés, couverture des relevés       |
| Non déterminable                     | Collecte de données                       | Producteurs des données                  | Part des territoires renseignés                  |

Les seuils (« élevé », « faible ») et la méthode de priorisation (score, pondérations, test de sensibilité) sont fixés dans le 02.

**Format de chaque recommandation :**

Elle suit la chaîne **constat → ampleur → territoire → déficit associé → action**, et porte : un territoire nommé, une cible chiffrée, la population concernée, un horizon (1, 3 ou 5 ans), un acteur responsable, un indicateur de suivi, un niveau de preuve et une réserve. Exemple fictif :

> **Préfecture X** — 1 auto-école pour 150 000 habitants, contre 1 pour 40 000 en médiane nationale. Atteindre la médiane suppose environ 6 auto-écoles de plus ; 300 000 habitants concernés. Horizon : 3 ans. Acteur : ministère chargé des transports. Suivi : auto-écoles pour 100 000 habitants. Preuve : B. Réserve : activité réelle des auto-écoles non vérifiée.

**Points de vigilance :**

- **Les données décident de la recommandation, pas l’inverse.** Par exemple, ne recommander le port du casque que si les données montrent une forte part de victimes à moto.
- **Pas de coût dans les données** : ordres de grandeur, pas devis.
- **Une recommandation portée par un indicateur C** déclenche une vérification, pas un investissement.
- **Pas de recommandation générique** (« sensibiliser la population ») sans territoire, cible et horizon.

---

## 4. Définitions

| Terme                      | Définition retenue                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| Immatriculations annuelles | Premières immatriculations de l’année (flux)                                               |
| Parc immatriculé           | Véhicules immatriculés et non radiés à une date donnée (stock administratif). Rarement publié |
| Parc roulant               | Véhicules réellement en circulation, immatriculés ou non. Le vrai dénominateur du risque par véhicule, presque jamais mesuré |
| Permis délivrés            | Premières délivrances de l’année par catégorie (flux), hors renouvellements et duplicatas. Différent du nombre de titulaires |
| Accident corporel          | Accident avec au moins un blessé ou un tué                                                 |
| Accident mortel            | Accident corporel avec au moins un tué                                                     |
| Victime                    | Personne blessée ou tuée dans un accident corporel                                         |
| Usager vulnérable          | Piéton, cycliste, conducteur ou passager de deux-roues motorisé. À adapter aux catégories des données |
| Tué                        | Décès sur le coup ou dans un délai fixé (30 jours selon l’OMS) : à vérifier dans la source |
| Tronçon                    | Segment de route homogène : identifiant, début, fin, longueur, type, état                  |
| Réseau classé              | Routes de la classification officielle (nationales, régionales, etc.)                      |
| Auto-école agréée          | Établissement autorisé à former à la conduite                                              |
| Auto-école active          | Auto-école agréée ayant formé au moins un candidat dans l’année. Si la donnée n’existe pas, le signaler |
| Niveau de preuve           | A mesuré (comptage direct), B calculé (formule maîtrisée), C estimé (proxy ou méthode non documentée) |

---

## 5. Hypothèses à vérifier

Ce sont des pistes, pas des conclusions. Une hypothèse infirmée est un résultat.

**Affirmations de l’énoncé**

| Code | Affirmation                                                     | Vérification                                                        |
| ---- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| S1   | Les immatriculations annuelles ont plus que quadruplé en 20 ans | Rapport dernière année / année n−20, sur le flux et non sur le parc |
| S2   | Cette hausse est portée par les motos                           | Part des motos dans la hausse                                       |
| S3   | 7 500 accidents et 683 morts en 2022                            | Retrouver les chiffres. Accidents corporels ? Définition du décès ? |
| S4   | Les accidents augmentent                                        | En volume et en taux : le volume peut monter quand le taux baisse   |
| S5   | Le réseau est inégalement entretenu selon les régions           | Écart entre régions de la part de km en mauvais état                |

**Hypothèses de travail**

| Code | Type  | Hypothèse                                                                                                                   | Test                                                      |
| ---- | ----- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| H1   | Lien  | L’écart immatriculations / permis est plus marqué pour les motos que pour les voitures et les poids lourds                  | Comparer les catégories entre elles                       |
| H2   | Lien  | Les motos sont surreprésentées parmi les véhicules impliqués et les victimes                                                | Part dans les accidents / part dans le parc               |
| H3   | Lien  | Les territoires au réseau dégradé ont un taux d’accidents plus élevé                                                        | Comparaison entre territoires, à lire avec le trafic (§8) |
| H4   | Lien  | Les territoires peu dotés en auto-écoles ont un taux d’accidents plus élevé                                                 | Comparaison entre territoires, avec deux mesures de l’offre : auto-écoles par habitant et distance. Laquelle va le plus avec le risque ? |
| H5   | Lien  | Les poids lourds en transit (corridor du port de Lomé vers le nord) pèsent sur l’accidentalité et l’usure de l’axe nord-sud | Accidents de poids lourds, état des tronçons de l’axe. Preuve C sans comptages de trafic |
| H6   | Lien  | Le taux par habitant et le taux par véhicule évoluent en sens inverse                                                       | Comparer les deux séries                                  |
| H7   | Écart | Le risque routier par habitant varie fortement d’un territoire à l’autre                                                    | Écart entre territoires des taux pour 100 000 habitants   |
| H8   | Écart | Les auto-écoles sont concentrées dans les grandes villes                                                                    | Part des auto-écoles comparée à la part de la population  |
| H9   | Cumul | Certains territoires cumulent forte pression de mobilité, risque élevé, réseau dégradé et faible offre de formation         | Nombre de déficits par territoire, seuils du 02           |
| H10  | Écart | Les accidents augmentent en saison des pluies et aux périodes de fêtes                                                      | Saisonnalité mensuelle, si les données sont mensuelles    |
| H11  | Écart | Le Grand Lomé concentre les accidents en volume, mais le risque par habitant est plus élevé ailleurs, en milieu rural       | Part du Grand Lomé dans les accidents ; tués pour 100 000 habitants par zone, puis par préfecture urbaine ou rurale |
| H12  | Écart | Les jeunes conducteurs (18–25 ans) sont surreprésentés parmi les conducteurs impliqués                                      | Part des 18–25 ans parmi les conducteurs impliqués, comparée à leur part dans la population en âge de conduire |

**Ordre de test :** les écarts (S5, H7, H8, H10 à H12), puis les liens (H1 à H6), puis le cumul (H9). Un lien ne se teste que si les deux facteurs varient d’un territoire à l’autre.

**H9 teste la décision elle-même.** Si aucun territoire ne cumule les déficits, les recommandations s’organisent par levier plutôt que par territoire.

---

## 6. Périmètre

- **Inclus :** transport routier motorisé (motos, voitures, poids lourds, bus, autres catégories présentes), permis, accidents et victimes, réseau classé, auto-écoles, population.
- **Exclus :** transports ferroviaire, aérien et maritime ; suivi individuel de conducteurs ou de véhicules ; chiffrage du coût des actions (aucune donnée de coût : ordres de grandeur seulement) ; modèle causal.
- **À confirmer :** piétons et cyclistes (comme victimes, si les données les distinguent) ; pistes non classées.

---

## 7. Données attendues (à vérifier)

La section « Ressources » de l’énoncé est vide : ce tableau décrit le besoin, pas l’existant.

| Code | Données                                        | Maille attendue                            | Objectifs |
| ---- | ---------------------------------------------- | ------------------------------------------ | --------- |
| D1   | Immatriculations par catégorie                 | National, peut-être région ; an, peut-être mois | O1, O2 |
| D2   | Permis délivrés par catégorie                  | National, peut-être région ; an, peut-être mois | O1     |
| D3   | Accidents, blessés, tués                       | National ; région, préfecture ou tronçon ? | O2, O5    |
| D4   | État du réseau                                 | Tronçon                                    | O3, O5    |
| D5   | Tracé du réseau classé                         | Tronçon                                    | O3, O4    |
| D6   | Auto-écoles                                    | Point ou adresse                           | O4, O5    |
| D7   | Population (INSEED : RGPH-5 2022, projections) | Région, préfecture ; Grand Lomé publié à part | Tous   |

À chercher aussi dès l’étape 03, car ces couches ne se rattrapent pas plus tard :

- **Référentiel administratif** (limites et codes des régions et préfectures). **Bloquant** : sans lui, aucun croisement.
- **Benchmark externe** : taux de tués estimés par l’OMS pour le Togo et ses voisins.
- **Comptages de trafic** sur les grands axes : seule mesure de l’exposition réelle.
- **Chronologie des réformes** (permis moto, casque, procédures d’immatriculation) : pour expliquer les ruptures de séries.
- **Enquête sur les déplacements** des ménages : usage réel de la moto, motos-taxis.
- **Lieux candidats** (chefs-lieux, communes) et **grille de population** : pour localiser de nouvelles auto-écoles et calculer des distances.

---

## 8. Limites transversales

Les précautions propres à un objectif sont dans sa section (§3). Celles-ci concernent plusieurs objectifs à la fois.

- **Trafic non mesuré.** Un axe très fréquenté paraît dangereux par simple volume. Et les routes en bon état attirent plus de trafic et de vitesse : la comparaison réseau / accidents peut s’inverser.
- **Accidents non localisés.** Sans rattachement aux tronçons, le lien avec l’état des routes ne se lit qu’entre territoires.
- **Années différentes.** Les jeux de données ne couvrent pas forcément les mêmes années : croiser sur l’année de référence commune.
- **« Maritime » a deux sens.** Selon la source, la Maritime inclut ou non le Grand Lomé. Chaque source est étiquetée, et la somme des zones doit égaler le total national : sinon, le Grand Lomé est compté deux fois.
- **Valeur manquante ≠ zéro.** Un tronçon non évalué n’est pas en bon état ; une préfecture sans donnée d’accidents n’a pas zéro accident.
- **Projection.** Longueurs, surfaces et distances se calculent en projection métrique (UTM zone 31N), pas en degrés.

---

## 9. Questions ouvertes (étape 03)

1. Quels jeux de données sont fournis, et sur quelles années ?
2. Immatriculations et permis : sont-ils disponibles par mois ? Les permis, par sexe, âge et région ? Distinguent-ils première délivrance et renouvellement ?
3. Le parc immatriculé ou le parc roulant est-il publié ?
4. Quelle est la nomenclature des permis au Togo ?
5. Accidents : sont-ils ventilés par région, préfecture ou tronçon ? Par mois, tranche horaire (jour / nuit), sexe, âge, type d’usager, catégorie de véhicule, véhicule immatriculé ou non ? L’âge des conducteurs impliqués est-il connu, ou seulement celui des victimes ?
6. Les 7 500 accidents de 2022 sont-ils des accidents corporels ? Quelle définition du décès ?
7. Réseau : le réseau classé inclut-il les routes en terre, ou seulement le bitumé ? Les types de routes sont-ils distingués ? De quand datent les relevés d’état, et selon quelle méthode ?
8. Auto-écoles : existe-t-il une liste officielle des auto-écoles agréées, avec date d’agrément ? Sont-elles géolocalisées ? Actives ? Leur capacité est-elle connue ?
9. Dans chaque source, la Maritime inclut-elle le Grand Lomé ? Les données descendent-elles jusqu’aux préfectures du Golfe et d’Agoè-Nyivé ?
10. Quelle est la grille de notation du jury ?

---

## 10. Suite

**Ordre analytique :** référentiel territorial et population → O1 (le parc sert de dénominateur à O2) → O2 → O3 → O4 → croisement → O5.

**Validation :** décision (§2.1), cadre (§2.3), définitions (§4) et hypothèses (§5) validés le 2026-10-03. Tout écart constaté ensuite est déclaré dans les étapes suivantes, sans modifier ce document.

**Prochaine étape :** `02_decision_matrix`, une ligne par indicateur (question → données → calcul → seuil → décision possible), fixée avant tout calcul.
