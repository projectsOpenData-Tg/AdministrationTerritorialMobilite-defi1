# 11 — Tableau de bord

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 0.10 — **Date :** 2026-10-08 — **Statut :** plan et plans détaillés des 8 pages validés ; **non figé**, en attente de la validation d’ensemble avant le codage
**Sources :** `01` à `10` (figés), `A1_horizon.md` (annexe, validée), `data/analysis/06_exploration/` à `data/analysis/10_recommandations/`, `data/analysis/A1_horizon/`, `methodology/MAQUETTE_dashboard.md`, `methodology/_GARDRAILS_DASHBOARD.txt`

> **Question du 11 :** que doit afficher le tableau de bord, page par page, et avec quelles données ?
>
> Le 11 couvre l’étape 12 de la procédure. C’est un **document de spécification** : il décrit ce que chaque page affiche, pas ce qu’elle calcule. Le tableau de bord lit les CSV produits par les documents 06 à 10 ; il ne recalcule aucun indicateur, sauf les deux exceptions de la maquette (§4.4).
>
> Chaque chiffre cité ici vient d’un de ces CSV. Le tableau de bord le relit dans le CSV, il ne le recopie pas (R-19).
>
> Le 11 est suivi du livrable `dashboard.zip` (code Streamlit) et du ppt. Les documents 12 (validation) et 13 (rapport final) ne seront pas écrits : ce qu’ils devaient porter est repris en page Méthodologie (§5) et dans le ppt.
>
> Ce document donne le plan d’ensemble et les règles communes. Le plan détaillé de chaque page est dans `workspace/design-page1.md` à `design-page8.md` (§5).
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §10.

---

## Point de départ

**Ce que le 10 transmet** (10 §10) :

- **Pour la page « Recommandations »** : les 15 cartes au format du 10 §6, les 7 onglets, les filtres priorité et zone, la rubrique « Pour aller plus loin ».
- **Les horizons** : l’annexe Horizon 2031 est validée ✅. Les cartes de recommandation de la page 6 gardent la quantité de 2022, mesurée, et affichent sous elle la quantité de leur propre horizon, lue dans `horizon_A1.csv` ; la page 8 porte la vue d’ensemble par horizon.
- **Pour la page Méthodologie** : les deux analyses des zones les moins desservies (10 §4.6), la limite de l’accès rural mot pour mot, la légende des niveaux de preuve.
- **Pour toutes les pages** : la règle des codes.
- **Les fichiers** : `recommandations_10.csv`, `prefectures_10.csv`, `zones_10.csv`, `cartes_10.csv`.

**Ce que le 09 transmet** (09 §10) : le multiplicateur de 4,56 en page d’accueil ; la moto comme catégorie de référence ; le chiffre de la source avec sa définition ; le message « plus de véhicules, pas une route plus dangereuse ».

**Ce que le 08 transmet** (08 §11) : le classement s’affiche avec son niveau, « classement en C : vérification avant investissement ».

**Ce que l’annexe Horizon 2031 transmet** (A1 §11, §13) : les quantités de chaque recommandation aux 5 horizons ; les deux mesures de l’accès rural ; la correction A1-E1 et la réserve A1-R1 ; les formules des estimations. La correction ne change pas la priorité de la recommandation de zone de la Centrale : les pages Priorités et Recommandations gardent la lecture du 10 et portent une note.

**Ce que le 07 transmet** (07 §9 ✅) : les 3 compléments (blessés par habitant, accidents et blessés par véhicule) vont dans une section « Compléments à l’énoncé », séparée des indicateurs du 02.

**Ce que demande la procédure** (étape 12) :

- 7 pages au moins, dans l’ordre : vue nationale, comparaison territoriale, analyse détaillée (nommée « Évolutions et constats »), carte (nommée « Carte du réseau et des auto-écoles »), priorités, recommandations, méthodologie ; le tableau de bord en ajoute une 8e, « Horizon 2031 », qui restitue l’annexe ;
- **trois bandeaux sur chaque vue** : le constat à côté du graphique, la synthèse chiffrée en bas, la limite de cette vue sur place ;
- **au moins un seuil d’analyse déplaçable** par le lecteur ;
- **un export CSV par bloc** ;
- rien de technique dans l’interface ;
- la règle des dix secondes par page : un message, trois chiffres, une action.

**Ce que fixent la maquette et les garde-fous** : Streamlit 1.61, navigation par `st.navigation()` et un menu en 4 groupes, pages dans un dossier `views/` (jamais `pages/`), graphiques et cartes en Plotly, palette validée, décideur non technique, sources détaillées seulement en page Méthodologie.

---

## 1. Objectif du 11

Décrire ce que chaque page du tableau de bord affiche, avec quelles données, quelles règles visuelles et quels garde-fous. Le livrable Streamlit s’écrit ensuite à partir de cette spécification.

**Ce que le 11 fait :**

- il décrit **chaque page** : titre, contenu, données, filtres, interactions ;
- il fixe les **règles visuelles** : couleurs, formats, étiquettes, tri ;
- il fixe les **règles de contenu** : aucun code interne, niveaux A, B, C avec leur légende, aucune causalité ;
- il liste les **fichiers de données** de chaque page.

**Ce que le 11 ne fait pas :**

- il ne calcule rien (documents 06 à 10) ;
- il ne recommande rien (10) ;
- il ne valide rien (12) ;
- il n’est pas le tableau de bord lui-même : c’en est le plan.

**Rapport avec les autres documents :** le 10 produit les 15 recommandations et les 39 fiches préfectures ; le 11 dit où, comment et avec quoi elles s’affichent ; le 12 vérifie que le livrable est conforme au 11 ; le 13 en fait le rapport final.

---

## 2. Méthode et outils

**Le tableau de bord ne calcule rien.** Il lit :

- `data/analysis/06_exploration/signaux_06.csv` (points d’attention, page 2), `prefectures_06.csv` et `rapports_06.csv` (page 4 : parts en bon et en moyen état, tronçons relevés, surface, part de la population du Grand Lomé) ;
- `data/analysis/07_indicateurs/indicateurs_07.csv`, `catalogue_07.csv` ;
- `data/analysis/08_priorisation/classement_08.csv`, `regions_08.csv`, `sensibilite_08.csv`, `controles_08.csv` (seuil du classement et nombre de préfectures évaluées, page 4) ;
- `data/analysis/09_diagnostic/hypotheses_09.csv`, `taux_09.csv`, `diagnostic_09.csv` ;
- `data/analysis/10_recommandations/recommandations_10.csv`, `prefectures_10.csv`, `zones_10.csv`, `cartes_10.csv` ;
- `data/processed/geo/*.geojson` (couches cartographiques, dont les équipements de sécurité routière, couche facultative de la page 4) et `data/processed/D13_points_depart_o4_08.csv` (points de départ de la distance, page 4) ;
- `data/reference/chronologie_reformes.csv` (annotations de contexte), `correspondance_vehicules_permis.csv` (couleurs par famille de véhicules) et `data/raw/_SOURCES.csv` (registre des sources, page 7) ;
- `data/processed/D4_etat_national_pct.csv` (page 3, onglet Réseau) : les parts par état de l’annuaire national, 2020–2022. Le 07 n’en garde que les différences d’une année à l’autre (évolution de l’état) ; c’est la seule table qui donne ces parts.
- `data/processed/D4_etat_troncons.csv` (page 3, onglet Réseau) : les 84 tronçons du relevé, avec leurs km dans chaque état et les zones et régions traversées. Le 07 n’en garde que les 49 tronçons critiques ; les 49 lignes à km en mauvais état sont les siennes, à l’identique (§7) ;
- `data/analysis/11_tableau_de_bord/consequences_11.csv` (pages 3 et 7) : la conséquence retenue pour chaque verdict et la donnée qui rendrait chaque hypothèse testable, extraites du 09 §10 (ci-dessous) ;
- `data/analysis/11_tableau_de_bord/phrases_11.csv` (page 5) : les 18 phrases de diagnostic du 09 §6 (10 préfectures, Mô, 6 zones, la région Maritime), extraites de même ;
- `data/analysis/A1_horizon/horizon_A1.csv`, `population_A1.csv`, `national_A1.csv`, `acces_A1.csv`, `emplacements_A1.csv`, `sites_A1.csv` (page 8), `erratum_A1.csv` et `formules_A1.csv` (page 7, et notes des pages 5 et 6) ;
- les tables de contrôle de chaque étape (page Méthodologie, section 8) : `controles_coherence.csv`, `controles_05.csv`, `controles_07.csv`, `controles_08.csv`, `controles_09.csv`, `controles_10.csv`, `controles_11.csv`, `controles_A1.csv`. Le nombre de lignes et de conformes est compté à l’affichage ; aucun n’est écrit en dur.

Les séries d’immatriculations et de permis viennent de `indicateurs_07.csv`, et non de `data/processed/` : une seule source par grandeur (procédure, étape 14).

**Outils du livrable :** Streamlit 1.61, Plotly, pandas, geopandas. Ils sont dans le `requirements.txt` du livrable (§8). L’environnement d’analyse `.venv` n’est pas modifié.

**Un seul script au 11, d’extraction : `scripts/consequences_11.py`.** Le 09 écrit en texte, et non dans un CSV, la conséquence retenue pour chaque verdict et la donnée qui manque pour chaque hypothèse (§10), ainsi que les phrases de diagnostic par territoire (§6) ; aucune page ne lit un `.md`. Le script reprend ces textes mot pour mot, les relie aux 17 codes de `hypotheses_09.csv` et aux 18 lignes de `diagnostic_09.csv`, et écrit `consequences_11.csv` et `phrases_11.csv`, avec des colonnes « affichées » sans codes, renvois ni mentions techniques (« 6 tests sur 6 » devient « en tête du classement dans les 6 tests de robustesse »). Il ne calcule rien et ne modifie ni le 09 ni ses sorties. Contrôles : `controles_11.csv`, 9 conformes sur 9 ; sorties identiques d’une exécution à l’autre. Le reste du 11 est un document de spécification.

---

## 3. Structure générale — 8 pages

| # | Page                               | Groupe du menu | Question (titre de la page)                                       | Rôle                                                   | Plan détaillé |
| - | ---------------------------------- | -------------- | ----------------------------------------------------------------- | ------------------------------------------------------- | ------------- |
| 1 | **Vue nationale**            | Principal      | La mobilité et la sécurité routière au Togo : où en est-on ? | Point d’entrée : synthèse du pays, 4 thèmes, permis | [design-page1.md](workspace/design-page1.md) |
| 2 | **Comparaison territoriale** | Analyses       | Quels territoires sont les moins bien équipés ?                 | Les 6 zones, les 5 régions et les 39 préfectures côte à côte | [design-page2.md](workspace/design-page2.md) |
| 3 | **Évolutions et constats** | Analyses       | Qu’est-ce qui change, et que confirment les données ?           | L’évolution de la mobilité, de la sécurité et du réseau ; les 17 vérifications et hypothèses | [design-page3.md](workspace/design-page3.md) |
| 4 | **Carte du réseau et des auto-écoles** | Analyses       | Que voit-on, préfecture par préfecture ?                        | Les 39 préfectures sur fond cartographique : 8 couches, routes classées, état des tronçons, auto-écoles, équipements | [design-page4.md](workspace/design-page4.md) |
| 5 | **Priorités**               | Pilotage       | Par où commencer ?                                                | Les zones en difficulté, les préfectures, les leviers, la robustesse du classement | [design-page5.md](workspace/design-page5.md) |
| 6 | **Recommandations**          | Pilotage       | Quelle action engager ?                                           | Les 15 recommandations et les 39 fiches                 | [design-page6.md](workspace/design-page6.md) |
| 7 | **Horizon 2031**             | Pilotage       | Combien en faudra-t-il d’ici 2031 ?                               | Les quantités de chaque levier dans 1, 3 et 5 ans, et l’écart à la cible de sécurité | [design-page8.md](workspace/design-page8.md) |
| 8 | **Méthodologie**            | Méthodologie  | Sources, méthode et limites                                      | Ce que les données disent et ne disent pas, les corrections, les formules et les contrôles | [design-page7.md](workspace/design-page7.md) |

La page Horizon 2031 vient après Recommandations : la page 6 dit quoi faire, la page 8 combien il en faudra. Son plan garde le nom de fichier `design-page8.md` ; la Méthodologie garde `design-page7.md`, écrit avant elle.

**Menu :** les 4 groupes de la maquette (Principal, Analyses, Pilotage, Méthodologie), par `st.navigation()`.

**Navigation :** chaque carte de thème de la page 1 mène à sa page de détail par `st.page_link`. La page 1 est la synthèse ; les autres sont des zooms.

La page 3 a **4 onglets** (Synthèse, Mobilité, Sécurité routière, Réseau ; [design-page3.md](workspace/design-page3.md)). La page 6 a **7 onglets internes** ([design-page6.md](workspace/design-page6.md), section 1). La page Horizon 2031 a un **curseur d’horizon** à 5 positions, qui change tous ses chiffres ([design-page8.md](workspace/design-page8.md)).

---

## 4. Règles transverses

### 4.1 Design

Les jetons de la maquette (`MAQUETTE_dashboard.md` §2) : fond, cartes, bandeaux, polices Fraunces et IBM Plex Sans.

| Usage                           | Couleur                                                                                                                                          | Source                    |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------- |
| Priorité haute                 | `#0d366b`                                                                                                                                      | palette`PRIORITE`       |
| Priorité moyenne               | `#3987e5`                                                                                                                                      | palette`PRIORITE`       |
| Priorité faible                | `#cde2fb`                                                                                                                                      | palette`PRIORITE`       |
| Non classée, aucune action     | `#b9b6ad`                                                                                                                                      | palette`PRIORITE`       |
| Thème Mobilité                | `#2a78d6`                                                                                                                                      | palette`CATEGORIELLE`   |
| Thème Sécurité routière     | `#eda100`                                                                                                                                      | palette`CATEGORIELLE`   |
| Thème Réseau                  | `#eb6834`                                                                                                                                      | palette`CATEGORIELLE`   |
| Thème Couverture               | `#1baf7a`                                                                                                                                      | palette`CATEGORIELLE`   |
| Zones                           | Grand Lomé`#256abf`, Maritime hors Grand Lomé `#008300`, Plateaux `#ab6300`, Centrale `#4a3aa7`, Kara `#cb4b0c`, Savanes `#bb537d` | palette`COULEUR_REGION` |
| Valeurs continues sur une carte | `#cde2fb` → `#0d366b`, 5 classes                                                                                                            | palette`BLEUS`          |
| États du réseau | bon `#1baf7a`, moyen `#eda100`, mauvais `#e34948`, travaux `#2a78d6`, non évalué `#b9b6ad` | palettes `CATEGORIELLE`, `CATEGORIELLE_8` et `PRIORITE` ; la maquette n’en prévoit pas pour les états. Vérifiées pour les daltonismes ; un orange pour « mauvais » échouait, trop proche du jaune |

Les couleurs de thème sont prises dans la palette `CATEGORIELLE`, déjà validée pour l’accessibilité : la maquette interdit d’en changer.

**Grille :** 3 colonnes pour les cartes (`st.columns(3)`) ; Streamlit les empile sur un écran étroit.

**Composants** (maquette §8) : carte de chiffre clé, rangée de 3 ou 4 chiffres clés, bandeaux Constat, Synthèse chiffrée et Limite, carte de recommandation (§8.11), tableau triable, filtres, onglets, carte Plotly avec couches, bouton d’export.

### 4.2 Contenu

**Règle des codes** (10 §10) : aucun code interne dans l’interface. Interdits : indicateurs (« O3-02 »), vérifications et hypothèses (« S4 », « H1 »), seuils (« SE-04 »), écarts (« écart 22 »), signaux (« SIG-29 »), profils (« P1 »), identifiants de recommandation (« REC-R1 »), noms de fichiers, numéros d’étape. Cette règle est plus stricte que la procédure, qui tolère un code accompagné de son intitulé. Les phrases du 09 contiennent des codes (« [SIG-25] ») et des mentions techniques (« 6 tests sur 6 ») : le tableau de bord les réécrit à l’affichage, et le 09 reste inchangé.

**Réécriture à l’affichage :** elle s’applique à **toutes les pages**, Méthodologie comprise, à tout texte lu dans un CSV et affiché tel quel. Dans l’ordre :

1. **Codes d’indicateurs** : chaque code est remplacé par son intitulé, lu dans `catalogue_07.csv` (colonne « Indicateur »), après le point 5.
2. **Codes d’objectifs** : « O1 » à « O5 » deviennent « l’objectif 1 » à « l’objectif 5 ».
3. **Parenthèses et crochets de renvoi** : retirés quand ils ne contiennent qu’un renvoi ou un code : « (écart 1) », « (08 §3.1) », « (01 §6) », « (SE-10) », « (PA-03) », « [SIG-25] ». Sont retirés aussi les formules (« (I(2022) / I(2002)) ») et le numéro de document en fin de parenthèse (« (depuis 2004, année de rupture de la série, 04) » devient « (depuis 2004, année de rupture de la série) »).
4. **Noms de sources entre parenthèses** (« (OMS) ») : retirés sur les pages 1 à 6 ; un nom qui fait partie de la phrase (« l’estimation de l’OMS ») reste.
5. **Vocabulaire de l’interface** : « auto-école(s) comptée(s) » devient « auto-école(s) agréée(s) » (R-12) ; les autres « compté » ne changent pas (« km déjà comptés ») ; « accidents corporels » devient « accidents constatés », y compris dans les intitulés du catalogue (« Accidents corporels, blessés, tués »), car aucune source ne les dit corporels.
6. **Cas particuliers** : le nom d’un tronçon perd le code du relevé qui le précède (« TGRKRRRN19 KARA-KABOU-FRE GHANA » devient « RN19 KARA-KABOU-FRE GHANA », « TGRKRT KOUMEA-SIOU » devient « KOUMEA-SIOU ») ; un point d’attention de la page 2 affiche son titre en clair, fixé par le plan de la page, puis le résumé du signal à partir du deuxième deux-points.

Les colonnes d’identifiants (« ID », « Code », « Recommandations » de `prefectures_10.csv`, « Recommandation » de `zones_10.csv`) servent au tri et aux liens ; elles ne s’affichent jamais. Chaque plan de page renvoie à cette règle ; le contrôle « Règle des codes » (§7) la vérifie sur toutes les pages.

**Autorisés :** noms en français, années, noms de territoires et de routes (« RN1 »), niveaux A, B, C avec leur légende.

**Règle des niveaux :** la légende est visible sous chaque graphique concerné et rappelée en page 7 : **A** = mesuré (comptage direct) ; **B** = calculé (formule maîtrisée) ; **C** = estimé (approximation ou méthode non documentée).

**Règle des volumes :** un taux est toujours accompagné de son volume (population, km, nombre).

**Règle de non-causalité :** aucun texte n’affirme qu’une chose en cause une autre. Une date de la chronologie est un contexte, pas une cause.

**Règle des totaux :** les habitants ne s’additionnent jamais d’une carte de recommandation à l’autre. La barre de résumé de la page 6 le dit.

**Format des nombres :** espace des milliers, virgule décimale (« 8 095 498 », « 21,2 % ») ; en Plotly, `separators=", "`.

**Sources :** sur les pages 1 à 6, une mention générale seulement : « Données : portail national de données ouvertes du Togo et sources institutionnelles complémentaires. » Le détail est en page 7 (garde-fous).

### 4.3 Gabarit d’une page

- **En-tête :** la question de la page, et une réponse d’une phrase en dessous.
- **Trois bandeaux** (procédure, étape 12) : **Constat** à côté du graphique principal ; **Synthèse chiffrée** en bas ; **Limite** de cette page, sur place. Une limite renvoyée en page 7 n’a pas été énoncée.
- **Règle des dix secondes :** un message, trois chiffres, une action.
- **Export :** un bouton « Télécharger (CSV) » sous chaque bloc de données.

### 4.4 Ce que le tableau de bord calcule

Rien, sauf les deux exceptions de la maquette (§1, « Règle d’architecture ») :

1. **Les poids du score** (page 5) : le lecteur déplace le poids du réseau ; le score se recalcule avec la formule du 08 (somme pondérée des deux rangs percentiles de `classement_08.csv`). C’est le seuil d’analyse déplaçable que demande la procédure.
2. **Un seuil choisi par le lecteur**, appliqué à une valeur déjà calculée (page 2) : la part de routes en mauvais état au-delà de laquelle une préfecture est signalée.

Le **curseur d’horizon** de la page 8 n’est pas un calcul : il choisit la ligne à lire dans `horizon_A1.csv`, où chaque horizon a déjà sa quantité.

### 4.5 Garde-fous

- **Pas de zéro inventé** : une valeur absente s’écrit « non défini » ou « non renseigné ». Mô n’a aucune route classée : sa part en mauvais état est « non définie », pas 0. L’année 2013 des permis est « non renseignée ».
- **Pas d’« amélioration » ni de « dégradation » réelles** : ce sont des accidents **déclarés**.
- **Pas de comparaison sans réserve** quand le niveau est C.
- **Un bandeau Limite par page.** Réserves communes : pas d’accidents par préfecture ; le coût des actions n’est pas dans les données ; recommandations en C, à vérifier avant d’investir.

---

## 5. Plans détaillés des pages

Chaque page a son plan détaillé dans `workspace/` : objectif, schéma de la page, sections, chiffres et sources. Le 11 garde le plan d’ensemble (§3), les règles communes (§4) et les fichiers lus par chaque page (§6). Une page ne déroge pas aux règles communes : en cas d’écart, c’est le plan de la page qui se corrige.

| Page | Plan détaillé | Ce que la page montre |
| ---- | ------------- | --------------------- |
| 1 — Vue nationale | [design-page1.md](workspace/design-page1.md) | 6 chiffres clés, carte du Togo à 4 couches, 4 cartes de thème, permis 2024, immatriculations et permis, 5 messages |
| 2 — Comparaison territoriale | [design-page2.md](workspace/design-page2.md) | Maille zones, régions ou préfectures ; 3 chiffres clés ; réseau et formation avec seuil déplaçable ; zones ou régions avec seuils franchis ; état du réseau par zone ; concentration et distance des auto-écoles ; les 39 préfectures ; points d’attention |
| 3 — Évolutions et constats | [design-page3.md](workspace/design-page3.md) | 4 onglets, ouverts sur l’onglet choisi depuis la page 1. Synthèse : la carte des constats et l’encart national, les 17 vérifications et hypothèses, et ce que chaque verdict change pour l’action. Mobilité : immatriculations, permis, rapport immatriculations / permis, parc estimé. Sécurité routière : les 6 taux (compléments à part), séries annuelles, gravité, OMS, tués par usager. Réseau : les 84 tronçons et leurs km dans chaque état, en zones ou en régions ; l’état par type de route ; l’annuaire national |
| 4 — Carte du réseau et des auto-écoles | [design-page4.md](workspace/design-page4.md) | 4 chiffres clés ; carte à 8 couches (l’état du réseau en 5 états) avec encart du Grand Lomé ; tracé par type ou état des tronçons relevés ; auto-écoles ; équipements facultatifs ; filtre par zone ou région ; Constat par couche ; fiche de la préfecture, avec un lien vers la page 6 ; les 8 couches en tableau ; les 272 auto-écoles en tableau |
| 5 — Priorités | [design-page5.md](workspace/design-page5.md) | Les zones en difficulté (rang du 08 et conclusion du 10 §4.6, phrases du 09) ; les 5 qui cumulent ; les 10 premières, avec les km évalués et leur phrase de diagnostic ; les deux leviers et leur écart à la cible ; poids du réseau déplaçable et 5 tests de robustesse ; le classement complet, avec déficits, desserte et distance ; Mô à part |
| 6 — Recommandations | [design-page6.md](workspace/design-page6.md) | Suit le 10 §6 : 7 onglets, les 15 cartes et leur détail (R-18), filtres priorité et zone, la rubrique « Pour aller plus loin », les 39 fiches et leurs cas particuliers ; une ligne « Zones en difficulté » en tête, l’onglet des zones renvoyant à la page 5 |
| 7 — Horizon 2031 | [design-page8.md](workspace/design-page8.md) | Curseur d’horizon (2022, 2026, 2027, 2029, 2031) ; 4 chiffres clés ; ce qu’il faut ajouter, par préfecture, par zone et par recommandation ; le taux sans action ; l’écart à la cible de sécurité et le plafond du casque ; où ouvrir les auto-écoles |
| 8 — Méthodologie | [design-page7.md](workspace/design-page7.md) | Comment nous avons travaillé, en 9 étapes ; sources ; limites ; niveaux de preuve ; questions ouvertes et la donnée qui les rendrait testables ; les deux mesures de l’accès rural ; les 18 formules, par thème, avec un exemple chiffré ; corrections et contrôles ; licences |

**Conséquences et données manquantes (pages 3 et 8).** ✅ Lues dans `consequences_11.csv`, extrait mot pour mot du 09 §10 par `scripts/consequences_11.py` (§2). Le 09 et le 10 restent figés ; le fichier est une extraction, pas une décision nouvelle.

**Revue de rigueur et revue de décision** ✅. Les garde-fous les exigent avant le rendu, et les documents 12 et 13 ne seront pas écrits. Elles tiennent dans la page Méthodologie (sections 7 et 8) :

- **rigueur** : les formules de chaque indicateur, avec un exemple chiffré, et un tableau des contrôles de chaque étape, compté à l’affichage dans les tables de contrôle ;
- **décision** : l’erratum de l’annexe, qui dit ce qu’une analyse plus fine a corrigé, ce qu’elle a mis en réserve, et ce que chaque point change à l’action. Une seule décision en découle, prise ici : la recommandation de zone de la Centrale garde sa priorité haute.

La section 1 de la même page, « Comment nous avons travaillé », donne la chaîne en 9 étapes, de l’énoncé au livrable : c’est ce que la procédure attend d’un rapport de méthode.

---

## 6. Fichiers de données par page

| Page                          | Fichiers lus                                                                                                                                                                                         |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 — Vue nationale            | `indicateurs_07.csv`, `taux_09.csv`, `hypotheses_09.csv`, `regions_08.csv`, `classement_08.csv`, `prefectures_10.csv`, `zones_10.csv`, `chronologie_reformes.csv`, `correspondance_vehicules_permis.csv`, `geo/*.geojson` |
| 2 — Comparaison territoriale | `classement_08.csv`, `regions_08.csv`, `prefectures_10.csv`, `zones_10.csv`, `indicateurs_07.csv`, `hypotheses_09.csv`, `signaux_06.csv` |
| 3 — Évolutions et constats | `hypotheses_09.csv`, `consequences_11.csv`, `taux_09.csv`, `regions_08.csv`, `catalogue_07.csv`, `indicateurs_07.csv`, `chronologie_reformes.csv`, `correspondance_vehicules_permis.csv`, `D4_etat_troncons.csv`, `D4_etat_national_pct.csv`, `zones_10.csv`, `geo/*.geojson` |
| 4 — Carte du réseau et des auto-écoles | `geo/*.geojson`, `prefectures_10.csv`, `recommandations_10.csv`, `zones_10.csv`, `classement_08.csv`, `regions_08.csv`, `controles_08.csv`, `indicateurs_07.csv`, `prefectures_06.csv`, `rapports_06.csv`, `D4_etat_troncons.csv`, `D13_points_depart_o4_08.csv` |
| 5 — Priorités               | `classement_08.csv`, `sensibilite_08.csv`, `regions_08.csv`, `prefectures_10.csv`, `zones_10.csv`, `cartes_10.csv`, `recommandations_10.csv`, `signaux_06.csv`, `phrases_11.csv`, `erratum_A1.csv` |
| 6 — Recommandations          | `cartes_10.csv`, `prefectures_10.csv`, `zones_10.csv`, `recommandations_10.csv`, `horizon_A1.csv`, `erratum_A1.csv`                                                                          |
| 7 — Horizon 2031             | `horizon_A1.csv`, `population_A1.csv`, `national_A1.csv`, `acces_A1.csv`, `emplacements_A1.csv`, `sites_A1.csv`, `cartes_10.csv`, `geo/*.geojson` |
| 8 — Méthodologie            | `_SOURCES.csv`, les 4 tables du cadre de décision (`01_Matrice.csv`, `02_Hypotheses.csv`, `03_Seuils.csv`, `07_Regles.csv`), `catalogue_07.csv`, `indicateurs_07.csv`, `classement_08.csv`, `regions_08.csv`, `hypotheses_09.csv`, `consequences_11.csv`, `zones_10.csv`, `recommandations_10.csv`, `acces_A1.csv`, `horizon_A1.csv`, `national_A1.csv`, `erratum_A1.csv`, `formules_A1.csv`, les 8 tables de contrôle |

Aucune page ne lit un document `.md` : tout chiffre affiché vient d’un CSV (R-19). Hors des deux exceptions du §4.4, aucune page ne recalcule un indicateur.

---

## 7. Validation

| Contrôle          | Attendu                                                                                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pages              | 8 pages en 4 groupes de menu ; 4 onglets dans la page Évolutions et constats, 7 dans la page Recommandations ; curseur à 5 positions dans la page Horizon 2031 ; dossier`views/` |
| Chiffres           | Chaque chiffre affiché égal à sa valeur dans le CSV source ; les chiffres de ce document revérifiés à l’écran sur trois territoires (procédure, étape 13) |
| Règle des codes   | Aucun code interne, renvoi, formule ou nom de source entre parenthèses visible sur les 8 pages, après la réécriture du §4.2 ; « auto-école comptée » jamais affiché ; « accidents constatés » partout. Les identifiants de l’erratum (« A1-E1 ») ne s’affichent pas |
| R-18               | Chaque carte de recommandation affiche territoire, cible, population, horizon, acteur, indicateur de suivi, niveau et réserve                                      |
| Règle des volumes | Chaque taux accompagné de son volume                                                                                                                               |
| Règle des niveaux | Légende A, B, C sous chaque graphique concerné                                                                                                                    |
| Trois bandeaux     | Constat, Synthèse chiffrée et Limite sur chaque page                                                                                                              |
| Seuil déplaçable | Le poids du score (page 5) et le seuil de mauvais état (page 2, maille préfectures) ; aux valeurs par défaut, les résultats du 08 |
| Export             | Un export CSV par bloc de données                                                                                                                                  |
| Valeurs absentes   | « Non défini » ou « non renseigné », jamais 0 (Mô, permis de 2013)                                                                                           |
| Tronçons | Les 49 tronçons de `D4_etat_troncons.csv` à km en mauvais état sont les tronçons critiques de `indicateurs_07.csv`, avec les mêmes km (669,34 km en tout) |
| Conséquences et phrases | `controles_11.csv` : 9 contrôles conformes ; chaque texte affiché vient du 09 (§10, §6), sans nombre changé ; 18 phrases, une par ligne de `diagnostic_09.csv`, au rang du 09 |
| Non-causalité     | Aucune affirmation causale ; la chronologie annotée comme contexte                                                                                                 |
| Navigation         | Chaque carte de thème de la page 1 mène à sa page ; Mobilité et Sécurité routière à leur onglet de la page 3 ; le bouton de la fiche (page 4) ouvre la page 6 sur l’onglet « Actions par zone », filtrée sur la préfecture ; les recommandations de zone de la page 5 ouvrent la page 6 sur l’onglet « Zones les moins desservies » |
| Comptages de la page 4 | 272 auto-écoles, dont 132 agréées (= `regions_08.csv`, ligne du pays) ; 16 797 équipements (= 05, contrôle 7-12) ; 84 tronçons tracés, dont 49 en mauvais état ; 99,0 km de routes nationales sans état (= 04, part du réseau non évaluée) ; 13 auto-écoles « à vérifier » |
| Horizon | À l’horizon 2022, les quantités de la page 8 égalent celles du 10 affichées en page 6 ; aux autres horizons, chaque valeur vient de `horizon_A1.csv`, sans recalcul ; la quantité de remise en état ne change pas d’un horizon à l’autre ; aucune carte des accidents ni des permis |
| Accès rural | Les deux mesures affichées côte à côte en page Méthodologie ; la même note courte sur les pages Priorités, Recommandations et Horizon 2031, lue dans `erratum_A1.csv` ; la lecture du 10 gardée sur les pages Priorités et Recommandations |
| Rigueur et décision | Page Méthodologie : les 8 tables de contrôle comptées à l’affichage ; l’erratum avec sa source et sa conséquence ; les formules écrites en entier |
| Étapes de travail | Page Méthodologie, section 1 : 9 étapes ; chaque chiffre de la colonne « Ce que l’étape produit » compté à l’affichage dans son fichier, aucun écrit en dur |
| Formules | Page Méthodologie, section 7 : 18 formules en 5 blocs ; chacune avec son niveau de preuve, ses termes et un exemple chiffré égal à la valeur affichée ailleurs dans le tableau de bord |
| Cohérence | Le contenu de chaque page suit son plan détaillé (`workspace/design-pageN.md`), sans ajout ; les règles communes (§4) priment |
---

## 8. Livrable `dashboard.zip`

**Arborescence** (maquette §1) :

```text
dashboard.zip
├── app.py                 point d’entrée : configuration, thème, menu en 4 groupes, navigation
├── theme.py               jetons de couleur et bloc CSS
├── composants.py          chiffres clés, bandeaux, cartes de recommandation, export, cartes géographiques
├── donnees.py             lecture des CSV (cache), filtres, format des nombres ; aucun recalcul
├── views/                 une page par fichier ; jamais un dossier nommé pages/
│   ├── vue_nationale.py
│   ├── comparaison.py
│   ├── evolutions.py
│   ├── carte.py
│   ├── priorites.py
│   ├── recommandations.py
│   ├── horizon.py
│   └── methodologie.py
├── static/                logo, icônes
├── .streamlit/config.toml thème de base
├── data/                  copie des CSV et GeoJSON lus (§6)
├── README.md              installation, lancement, structure
└── requirements.txt       streamlit 1.61, plotly 5.15 ou plus (deux légendes), pandas 2.3.3, geopandas 1.2.0
```

**Les données sont copiées dans `data/`**, et non liées par un lien symbolique : une archive zip ne conserve pas toujours les liens, et le jury doit pouvoir lancer le tableau de bord sans le dépôt. La copie est faite par un script du livrable, qui vérifie l’empreinte de chaque fichier copié.

**Lancement :**

```bash
unzip dashboard.zip
cd dashboard
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Contraintes techniques :** Python 3.11 ; Streamlit 1.61 ; Plotly pour les graphiques et les cartes (choroplèthes sur GeoJSON), comme la maquette.

---

## 9. Suite

- **Livrable :** `dashboard.zip`, écrit à partir de ce plan.
- **Ppt :** rédigé à partir des mêmes sources, dont l’erratum et les formules de la page Méthodologie.

**Les documents 12 (validation) et 13 (rapport final) ne seront pas écrits** ✅ (décision du 2026-10-08, faute de temps). Ce qu’ils devaient porter :

| Ce que le 12 ou le 13 devait porter | Où cela va |
| --- | --- |
| Revue de rigueur | Page Méthodologie, section 6 : les 8 tables de contrôle |
| Revue de décision | Page Méthodologie, section 6 : l’erratum de l’annexe et sa conséquence |
| Comparer le livrable à ce plan, revérifier deux ou trois territoires à la main | À faire à la relecture du livrable, avant le rendu : le contrôle « Chiffres » du §7 |
| Présenter les résultats, les limites et les questions ouvertes | Le ppt, et les pages Méthodologie et Horizon 2031 |

---

## 10. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 11** : 7 pages, document de spécification, pas de calcul | Tout | Équipe, 2026-10-07 |
| ✅ **Structure** : barre latérale, 7 pages | §3 | Équipe, 2026-10-07 |
| ✅ **Page 6** : 7 onglets, dont « Actions par zone » en 7e position | design-page6.md, section 1 | Équipe, 2026-10-07 |
| ✅ **Règle des codes** : aucun code interne dans l’interface | §4.2 | Équipe, 2026-10-07 |
| ✅ **Règle des niveaux** : légende A, B, C visible | §4.2 | Équipe, 2026-10-07 |
| ✅ **Bandeaux de limite** : un par page | §4.3 | Équipe, 2026-10-07 |
| ✅ **Couleurs de priorité** : palette `PRIORITE` du 10 | §4.1 | Équipe, 2026-10-07 |
| ✅ **Fichiers par page** : aucun recalcul | §6 | Équipe, 2026-10-07 |
| ✅ **Vue nationale** : carte du Togo, 4 cartes de thème, carte des permis, immatriculations et permis ; point d’entrée vers les pages de détail | design-page1.md | Équipe, 2026-10-07 |
| ✅ **Carte du Togo** : 4 couches, permis signalés comme nationaux | design-page1.md, section 2 | Équipe, 2026-10-07 |
| ✅ **Permis** : total et décomposition de A à F | design-page1.md, section 4 | Équipe, 2026-10-07 |
| ✅ **Immatriculations et permis** : une figure en deux étages sur la même échelle des années, un axe vertical par étage, une couleur par famille de véhicules ; graphique à deux axes écarté (maquette : « jamais deux axes verticaux ») ; maquette visuelle validée | design-page1.md, section 5 | Équipe, 2026-10-07 |
| ✅ **Date du décret de 2022 corrigée** dans `chronologie_reformes.csv` : 3 août 2022, date du décret n° 2022-085/PR au Journal officiel n° 41 bis du 7 octobre 2022, au lieu du 25 juillet 2022 tiré de la presse. C’est la date déjà retenue au 04 (écart 6). L’année ne change pas : contrôles du 04, signaux du 06 et annotations du 07 identiques après relance ; seul `profil_variables.csv` du 04 change, sur les 3 lignes de la chronologie | design-page1.md, section 5 | Équipe, 2026-10-07 |
| ✅ **Livrable** : `dashboard.zip` Streamlit | §8 | Équipe, 2026-10-07 |
| ✅ **Chiffres corrigés** : permis 2024, 38 531 au total (10 165 est le seul permis A) ; blessés 2022, 9 918 (9 500 était la moyenne 2022–2024) ; 17 vérifications et hypothèses, dont 7 non testables (et non 15 et 5) | design-page1.md, design-page3.md | Équipe, 2026-10-07 |
| ✅ **Couverture, chiffre 3** : l’accès rural (17,2 %) remplace les km de route par habitant de la Maritime hors Grand Lomé, que le 10 §4.6 a montrés biaisés par la densité | design-page1.md, section 3 | Équipe, 2026-10-07 |
| ✅ **Couleurs de thème** prises dans la palette `CATEGORIELLE` de la maquette, au lieu de `#eab308` et `#059669`, hors palette validée | §4.1 | Équipe, 2026-10-07 |
| ✅ **Exigences de la procédure ajoutées** : trois bandeaux par page, seuil déplaçable (poids du score, seuil de mauvais état), export CSV par bloc, règle des dix secondes | §4.3, §4.4, design-page2.md, design-page5.md | Équipe, 2026-10-07 |
| ✅ **Maquette suivie** : menu en 4 groupes, dossier `views/` (un dossier `pages/` désactive `st.navigation`), Plotly pour les cartes (au lieu de Folium ou PyDeck), polices de la maquette | §3, §4.1, §8 | Équipe, 2026-10-07 |
| ✅ **Onglet des zones court** : 3 cartes et tableau de conclusion ; les deux analyses en page 7 (décision du 10) | design-page6.md, design-page7.md | Équipe, 2026-10-07 |
| ✅ **Champs de R-18 affichés** sur chaque carte (bouton « Détail »), lus dans les nouvelles colonnes de `cartes_10.csv` | design-page6.md, section 2 | Équipe, 2026-10-07 |
| ✅ **Compléments à l’énoncé** séparés des taux du 02 ; tués déclarés face à l’estimation de l’OMS | design-page3.md | Équipe, 2026-10-07 |
| ✅ **Aucune page ne lit un `.md`** : page 7 lue dans `_SOURCES.csv`, `catalogue_07.csv`, `hypotheses_09.csv`, `zones_10.csv` | design-page7.md, §6 | Équipe, 2026-10-07 |
| ✅ **Données copiées dans le zip**, pas de lien symbolique ; lancement par `streamlit run app.py` | §8 | Équipe, 2026-10-07 |
| ✅ **Page 3 en 4 onglets** : Synthèse, Mobilité, Sécurité routière, Réseau ; titre « Qu’est-ce qui change, et que confirment les données ? ». Formation et Données ne sont pas repris : ils sont en pages 2, 4, 6 et 7 | §3, design-page3.md | Équipe, 2026-10-07 |
| ✅ **Onglet Mobilité** : immatriculations (volume, part, pour 1 000 habitants), permis (volume, pour 1 000 habitants en âge de conduire), rapport immatriculations / permis en cumul, parc estimé ; la croissance annuelle dans l’export | design-page3.md, section 2 | Équipe, 2026-10-07 |
| ✅ **Onglet Sécurité routière** : les 6 taux et l’OMS, plus les séries année par année, absentes jusqu’ici | design-page3.md, section 3 | Équipe, 2026-10-07 |
| ✅ **Onglet Réseau** : les tronçons en mauvais état, que l’objectif 3 demande (« par tronçon ») et qu’aucune page ne montrait ; l’état par type de route et par zone ; l’annuaire national 2020–2022 | design-page3.md, section 4 | Équipe, 2026-10-07 |
| ✅ **Page 2 en 5 régions** : maille zones (par défaut, R-02), régions ou préfectures ; régions lues dans `regions_08.csv` ; blocs « par zone seulement » sans addition | design-page2.md, sections 1 et 4 | Équipe, 2026-10-07 |
| ✅ **Liens de la page 1** : les cartes Mobilité et Sécurité routière ouvrent leur onglet de la page 3 | design-page1.md, section 3 | Équipe, 2026-10-07 |
| ✅ **Page 2, relecture du 06 au 09** : 3 chiffres clés (dont 26 préfectures à plus de 10 km d’une auto-école agréée, 3 482 856 habitants) ; seuils franchis et rang par zone et par région ; note de la région Maritime (3,06 contre 0,37) ; concentration urbaine des auto-écoles (84,8 % pour 32,3 % de la population) ; distance qui distingue les 23 préfectures à zéro ; colonnes « non évaluée » et « desserte faible » ; 5 points d’attention du 06 | design-page2.md | Équipe, 2026-10-07 |
| ✅ **Corrections à la validation de la page 2** : préfectures sans auto-école agréée au niveau B, celui de l’indicateur au 07 (et non C en page 2, ni A en page 1) ; texte d’un point d’attention lu à partir du deuxième deux-points du résumé (le premier suit l’intitulé du signal) ; réserve sur le point « ménages équipés d’une moto », tiré d’une seule enquête | design-page1.md, design-page2.md, §4.2 | Équipe, 2026-10-07 |
| ✅ **`signaux_06.csv` lu par la page 2** (points d’attention), seule source de ces repères ; lu sans recalcul | §2, §6 | Équipe, 2026-10-07 |
| ✅ **Plans détaillés par page** dans `workspace/design-page1.md` à `design-page7.md` ; le 11 garde le plan d’ensemble et les règles communes | §5 | Équipe, 2026-10-07 |
| ✅ **Réécriture à l’affichage** : codes d’indicateurs remplacés par leur intitulé (`catalogue_07.csv`), renvois retirés | §4.2 | Équipe, 2026-10-07 |
| ✅ **Page 3, ajouts de la relecture** : gravité (tués et blessés pour 100 accidents) et tués par type d’usager (onglet Sécurité routière) ; colonne « Ce que montrent les données » dans la Synthèse ; l’annuaire national présenté comme une autre publication de 2020 (29,75 % en mauvais état, contre 21,2 % au relevé), jamais sur le même graphique | design-page3.md | Équipe, 2026-10-07 |
| ✅ **Un fichier lu en plus pour la page 3** : `D4_etat_national_pct.csv`, table préparée au 05, seule source des parts de l’annuaire ; lue sans recalcul | §2, §6 | Équipe, 2026-10-07 |
| ✅ **Limite du réseau en page 7** : le relevé de 2020 et l’annuaire de la même année ne concordent pas | design-page7.md, section 2 | Équipe, 2026-10-07 |
| ✅ **Conséquences retenues et données manquantes** (pages 3 et 7) : extraites mot pour mot du 09 §10 dans `consequences_11.csv` par `scripts/consequences_11.py` (5 contrôles conformes). Option proposée en validation : un fichier dérivé, sans rouvrir le 09 ni le 10. Fait autrement : le fichier va dans `data/analysis/11_tableau_de_bord/`, pas dans `data/reference/`, qui garde les tables de référence sourcées ; il est écrit par un script et non recopié (R-19) ; deux colonnes « affichées » retirent codes et renvois | §2, §5, design-page3.md, design-page7.md | Équipe, 2026-10-07 |
| ✅ **Niveaux de preuve vérifiés** : préfectures sans auto-école agréée en B dans `catalogue_07.csv`, en pages 1 et 2 ; le décompte de la page 7 (5 A, 10 B, 17 C) ne change pas, car il suit le catalogue ; les 3 compléments et l’accès rural y sont déjà ajoutés à part. Les repères du 06 ne sont pas des indicateurs : ils n’entrent pas dans le décompte | design-page1.md, design-page2.md, design-page7.md | Équipe, 2026-10-07 |
| ✅ **Les 84 tronçons et tous leurs états** en page 3 : bon, moyen, mauvais, travaux, km relevés, lus dans `D4_etat_troncons.csv` ; vue par défaut sur les 49 en mauvais état, identiques au 07 | design-page3.md, section 4 | Équipe, 2026-10-07 |
| ✅ **Maille zones ou régions** dans l’onglet Réseau de la page 3 : filtre des tronçons par zone ou région traversée ; état par région lu dans `regions_08.csv` ; l’état par type de route reste par zone | design-page3.md, section 4 | Équipe, 2026-10-07 |
| ✅ **Ouverture sur un onglet** : le bouton de la page 1 écrit le rang de l’onglet (`evolutions_rang`) puis appelle `st.switch_page` ; la page 3 s’ouvre sur cet onglet (composant `onglets` de la maquette, §8.10) | design-page1.md, section 3 ; design-page3.md | Équipe, 2026-10-07 |
| ✅ **Page 3 renommée « Évolutions et constats »** : le nom dit ce qui change (Mobilité, Sécurité routière, Réseau) et ce que les données confirment (Synthèse) ; écarté : « Évolutions et vérifications », « Tendances et preuves », « État des lieux ». Clé des onglets `evolutions`, fichier `views/evolutions.py` | §3, §5, §6, §8, design-page3.md, design-page1.md | Équipe, 2026-10-07 |
| ✅ **Réponse sous le titre de la page 3**, qui manquait au plan (11 §4.3) : multiplicateur de 4,56, accidents en hausse et 6 taux en baisse, 49 tronçons | design-page3.md | Équipe, 2026-10-07 |
| ✅ **Réécriture à l’affichage complétée** après la maquette de la page 3 : formules, renvois à un document, noms de sources entre parenthèses, « comptée » devenu « agréée », « accidents corporels » devenu « accidents constatés » | §4.2 | Équipe, 2026-10-07 |
| ✅ **Couleurs des états du réseau** : bon, moyen, mauvais, travaux, non évalué, prises dans les palettes de la maquette et vérifiées pour les daltonismes | §4.1 | Équipe, 2026-10-07 |
| ✅ **Place du Constat en page 3** : en tête d’onglet pour Synthèse et Réseau, à droite du graphique pour Mobilité et Sécurité routière (maquette §8.7) | design-page3.md | Équipe, 2026-10-07 |
| ✅ **Carte des constats** dans l’onglet Synthèse de la page 3 : réseau par zone (vérification « entretien inégal »), 49 tronçons en mauvais état tracés sur la route, auto-écoles agréées (vérification « concentration urbaine ») ; à côté, un encart national avec les courbes 1990–2024 (immatriculations) et 2010–2024 (tués par habitant). Écartés : les accidents sur la carte (publiés pour tout le pays seulement) et un curseur des années (les données par territoire n’ont qu’une date) | design-page3.md, section 1 | Équipe, 2026-10-07 |
| ✅ **Correction : l’état des tronçons se dessine sur le tracé.** Les 84 tronçons relevés sont rattachés au tracé par leur nom (04 §5) ; les pages 3 et 4 disaient l’inverse, d’après le 03 écrit avant ce rattachement | design-page3.md, design-page4.md | Équipe, 2026-10-07 |
| ✅ **Carte des constats, réglages de la maquette** : 5 classes fixées (moins de 10 %, 10 à 15 %, 15 à 20 %, 20 à 30 %, 30 % ou plus) ; valeur écrite sur chaque zone ; étiquette du Grand Lomé sous la côte ; légende à droite de la carte, avec le verdict de chaque couche ; encart national à droite de la carte, dessous sur un écran étroit | design-page3.md, section 1 | Équipe, 2026-10-07 |
| ✅ **Réécriture uniforme sur les 7 pages** : la règle du §4.2, complétée sur la page 3, vaut pour tout texte lu dans un CSV, Méthodologie comprise. Ajouts de la vérification sur toutes les colonnes affichées : codes d’objectifs (« O4 ») ; parenthèses de code « (SE-10) » ; « comptée » remplacé seulement dans « auto-école(s) comptée(s) », car la réserve d’une carte dit « km déjà comptés » ; intitulé « Accidents corporels, blessés, tués » du catalogue. Les colonnes d’identifiants ne s’affichent jamais | §4.2, §7, design-page1.md à design-page7.md | Équipe, 2026-10-07 |
| ✅ **Page 4 renommée « Carte du réseau et des auto-écoles »** : le nom reprend l’objectif 4 | §3, §5, design-page4.md | Équipe, 2026-10-07 |
| ✅ **Page 4, carte** : couche « État du réseau » en 5 états (remplace la part en mauvais état seule), densité routière, distance avec ses points de départ ; tracé « État des tronçons relevés » (dessin de la page 3, plus les 35 autres tronçons et les 99,0 km sans état) ; équipements de sécurité routière en couche facultative, masquée par défaut, un type à la fois, « non utilisée dans les indicateurs » (03 §3.2) ; limites des 5 régions et filtre par zone ou région ; fiche de la préfecture au clic, avec un lien vers la page 6 ; info-bulle complétée ; encadré « Ce que la carte ne montre pas » | design-page4.md, sections 2 à 7 et 11 ; design-page6.md, section 5 | Équipe, 2026-10-07 |
| ✅ **Page 4, réglages de la maquette** : réponse sous le titre ; tracé par type en noir et gris, les couleurs restant aux états ; limites des régions en bande grise ; 5 classes fixes par couche ; limite complétée (distance, équipements) ; export de la couche | design-page4.md | Équipe, 2026-10-07 |
| ✅ **Page 4, un Constat par couche**, et par état pour l’état du réseau : 12 textes | design-page4.md, section 8 | Équipe, 2026-10-07 |
| ✅ **Auto-écoles : 138 non agréées et 2 au statut non renseigné**, au lieu de « 140 sans agrément » | design-page1.md, design-page4.md | Équipe, 2026-10-07 |
| ✅ **Page 4, 4 chiffres clés** : réseau dégradé (13 sur 38 évaluées, au-delà du seuil du classement, et non « au moins un km en mauvais état », 36 sur 38) ; auto-écoles recensées par statut (activité non publiée) ; préfectures sans auto-école agréée ; équipements par type, sans ratio par km de route classée (la couche couvre aussi les rues non classées) | design-page4.md, section 1 ; maquette validée (version 2) | Équipe, 2026-10-07 |
| ✅ **Page 4, deux tableaux exportables** : les 8 couches par préfecture, aux couleurs de la carte, avec zone et région ; les 272 auto-écoles, avec statut, localisation, population de la préfecture et habitants par auto-école agréée, et les 13 « à vérifier ». Écartés : la distance de chaque auto-école au chef-lieu (aucune analyse ne la calcule) et la population autour de chaque auto-école (pas de grille de population) | design-page4.md, sections 9 et 10 ; maquette validée (version 2) | Équipe, 2026-10-07 |
| ✅ **Zones en difficulté définies en page 5** : la page 5 dit par où commencer (zones, puis préfectures), la page 6 quoi faire. Le tableau de conclusion du 10 §4.6 passe de l’onglet « Zones les moins desservies » de la page 6 à la page 5, avec le rang des zones du 08 : **écart au 10 §6**, le 10 figé n’étant pas modifié. L’onglet garde ses 3 cartes et son bandeau, et renvoie à la page 5 ; une ligne « Zones en difficulté » ouvre l’onglet « Toutes » | design-page5.md, section 1 ; design-page6.md, section 4 | Équipe, 2026-10-07 |
| ✅ **Page 5, vérifiée contre les analyses du 03 au 10** : ajouts du 08 (déficits ; desserte et distance affichées à côté du classement ; km évalués à côté de la part ; les deux leviers, leur ordre et leur écart à la cible ; les 5 tests de robustesse ; Grand Lomé hors des 10 premières ; lecture par région) ; du 09 (phrase de diagnostic des 10 premières, de Mô et des zones) ; du 06 (les 5 qui cumulent, déjà repérées à l’exploration) ; réponse sous le titre ; question « Par où commencer ? » | design-page5.md | Équipe, 2026-10-07 |
| ✅ **Phrases du 09 §6 extraites** dans `phrases_11.csv` par le script d’extraction du 11 ; 4 contrôles ajoutés, 9 conformes sur 9 ; `consequences_11.csv` inchangé à l’octet près | §2, §7 | Équipe, 2026-10-07 |
| ✅ **Page Méthodologie, deux sections ajoutées** : « Comment nous avons travaillé » en section 1, la chaîne en 9 étapes avec ce que chacune produit ; « Les formules » en section 7, 18 calculs en 5 blocs thématiques, chacun avec son niveau de preuve, ses termes et un exemple chiffré pris dans les données. Les formules sortent de la section « Corrections », qui garde l’erratum et les contrôles. Sections renumérotées de 1 à 10 | design-page7.md, §5, §6, §7 | Utilisateur, 2026-10-08 |
| ✅ **Chiffres de ces deux sections vérifiés avant écriture.** Repris de la proposition : 43 indicateurs, 14 pour la sécurité routière, 9 non calculables, 7 questions ouvertes, 10 seuils, 15 recommandations, les exemples des tués, de la gravité, de l’accès rural, du permis moto, de la cible et du casque. Corrigés : les immatriculations de 2022 (93 770, et non 93 944) et de 1990 (6 829, et non 5 200) ; la densité routière (Golfe : 96,8 ÷ 240,8, et non 95,6 ÷ 240,8) ; les écarts déclarés (32, et non 5) ; le nombre de formules (18, et non 15) ; les recommandations avec une quantité (10 sur 15) ; « accidents constatés » au lieu de « accidents corporels » (règle des codes) | design-page7.md | Vérification, 2026-10-08 |
| ✅ **Deux exemples refaits** : les auto-écoles à ouvrir se calculent par préfecture puis s’additionnent — appliquée au pays, la formule donnerait une valeur négative ; l’exemple prend Haho en 2029. Les km à remettre en état prennent Blitta, au lieu d’une préfecture fictive | design-page7.md, section 7 | Vérification, 2026-10-08 |
| ✅ **Trois scénarios écartés une seconde fois** : l’étape « Et d’ici 2031 ? » dit 2 références sans action nouvelle, conformément à l’annexe ; les scénarios sobre, médian et ambitieux avaient été écartés faute de source pour leurs élasticités | design-page7.md, section 1 | Utilisateur, 2026-10-08 |
| ✅ **Registre des sources non réécrit** : la page compte 31 téléchargés et 3 recensés, comme le registre de l’inventaire, et une note dit que la grille WorldPop a été téléchargée depuis, avec son empreinte dans `sources_A1.csv`. Écarté : annoncer 32 téléchargés, que le registre lu par la page ne dit pas | design-page7.md, section 2 | Vérification, 2026-10-08 |
| ✅ **Couleurs des deux sections prises dans la maquette** : rampe `BLEUS` pour les 9 étapes (l’intensité dit l’avancement, elle ne code rien), couleurs de thème pour les 5 blocs de formules. Écarté : neuf couleurs d’étape et des emojis, hors palette validée | design-page7.md, §4.1 | Utilisateur, 2026-10-08 |
| ✅ **8e page « Horizon 2031 »**, groupe Pilotage, après Recommandations : la page 6 dit quoi faire, la page 8 combien il en faudra dans 1, 3 et 5 ans. Curseur d’horizon à 5 positions, 2029 par défaut ; aucune carte des accidents ni des permis ; aucun effet des actions sur les accidents | §3, §5, §6, §8, design-page8.md | Utilisateur, 2026-10-08 |
| ✅ **Annexe Horizon 2031 validée** : la page 6 garde la quantité de 2022 sur chaque carte et affiche sous elle celle de l’horizon de la recommandation, lue dans `horizon_A1.csv` ; le message « l’annexe n’est pas validée » est retiré | Point de départ, §6, design-page6.md | Utilisateur, 2026-10-08 |
| ✅ **Accès rural : deux mesures, une seule page qui les compare.** La page Méthodologie (section 5) affiche la population uniforme et la grille WorldPop côte à côte, avec les médianes et la conclusion par dimension. Les pages Priorités, Recommandations et Horizon 2031 portent la même note courte, lue dans `erratum_A1.csv`, et gardent la lecture du 10. Écarté : afficher des conclusions différentes sur plusieurs pages sans les rapprocher | design-page5.md, design-page6.md, design-page7.md, design-page8.md, §7 | Utilisateur, 2026-10-08 |
| ✅ **Décision de la revue : la recommandation de zone de la Centrale garde sa priorité haute.** La Centrale reste la zone au réseau le plus dégradé (40,3 % contre 12,8 % dans les Savanes), la lecture « formation » ne change pas, et l’écart des Savanes à la médiane est de 0,28 point | design-page7.md, A1 §13 | Utilisateur, 2026-10-08 |
| ✅ **Page Méthodologie, section « Corrections, formules et contrôles »** : l’erratum (1 correction, 1 réserve), les 8 formules écrites en entier et les 8 tables de contrôle comptées à l’affichage. Elle tient lieu de revue de rigueur et de revue de décision, exigées par les garde-fous | design-page7.md, §5, §7 | Utilisateur, 2026-10-08 |
| ✅ **Page Méthodologie, trois mises à jour** : WorldPop passe de « recensée seulement » à téléchargée et utilisée (licence CC BY 4.0) ; deux limites majeures ajoutées (le raccord de la population en âge de conduire, et les quantités d’ici 2031 qui sont des estimations) ; la limite de l’accès rural réécrite, l’ancienne annonçant une grille non téléchargée | design-page7.md | Utilisateur, 2026-10-08 |
| ✅ **Les documents 12 et 13 ne seront pas écrits** ; ce qu’ils devaient porter est repris en page Méthodologie et dans le ppt | §9 | Utilisateur, 2026-10-08 |
| ✅ **Erratum limité à ce qui en est un** : la date du décret de 2022 n’y figure pas (le 04 portait déjà la bonne date, seul le fichier de chronologie était à corriger) ; la médiane de l’accès rural non plus (conséquence de la correction, pas une correction de plus) ; le plafond du casque non plus (résultat de l’annexe) | design-page7.md, A1 §13 | Utilisateur, 2026-10-08 |
| **Gel reporté** : rien n’est figé ni commité tant que l’ensemble n’est pas validé, avant le codage | Tout le document | Utilisateur, 2026-10-08 |
| ✅ **Page 6, alignée sur le 10** : couleurs `PRIORITE` et horizon de l’action ; filtre par zone sur la colonne `Zones` de `cartes_10.csv`, cartes nationales toujours affichées, aucun total additionné ; titre complet et phrase d’introduction de la rubrique « Pour aller plus loin », priorité de la base d’accidents gardée ; format des fiches et cas particuliers (Mô, Agoè-Nyivé, Golfe, Zio et Kpélé) ; Constat du 10 (« 5 préfectures cumulent les deux déficits ») | design-page6.md | Équipe, 2026-10-07 |
