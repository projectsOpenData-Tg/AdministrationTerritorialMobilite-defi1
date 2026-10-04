# 04 — Data Understanding

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-04 — **Statut :** **figé** le 2026-10-04
**Sources :** `workspace/_PROJECT.txt` (énoncé), `01_problem_definition.md` (figé), `02_decision_matrix.xlsx` (v1.1, figé), `03_data_inventory.md` (v1.3, figé), registre `data/raw/_SOURCES.csv`

> **Question du 04 :** les données disponibles sont-elles réellement fiables et exploitables pour calculer les indicateurs définis dans le 02 ? Autrement dit : que permettent-elles de dire, et que ne permettent-elles pas de dire ?
>
> Les colonnes « Résultat » sont remplies à partir des sorties des scripts (R-19).
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §11.

---

## Le projet

**Constat de l’énoncé.** Le nombre de véhicules immatriculés chaque année au Togo a plus que quadruplé en vingt ans, porté par les motos. Les accidents augmentent : plus de 7 500 accidents et 683 morts en 2022. Le réseau routier reste inégalement entretenu selon les régions.

**Livrable.** Un tableau de bord interactif, en Python, qui mesure l’évolution de la mobilité et de la sécurité routière, et des recommandations pour une mobilité plus sûre.

| Objectif | Énoncé |
| -------- | ------ |
| O1 | Retracer l’évolution des véhicules immatriculés (voitures, motos, poids lourds) et des permis de conduire délivrés par catégorie |
| O2 | Analyser la sécurité routière : accidents, blessés et morts, rapportés à la population et au nombre de véhicules |
| O3 | Évaluer l’état du réseau routier par tronçon et par région : bon état, état moyen, mauvais état, travaux en cours |
| O4 | Cartographier le réseau routier classé et les auto-écoles par région et par préfecture, et les rapporter à la population |
| O5 | Proposer des recommandations ciblées pour améliorer la sécurité routière, la formation des conducteurs et l’entretien du réseau dans les régions les moins bien desservies |

## Point de départ : le 03

- **Les fichiers sont là.** Le registre compte 30 jeux et 34 fichiers : 31 sont téléchargés dans `data/raw/` et vérifiés (taille, empreinte, format) ; 3 sont seulement recensés (03 §9).
- **Le référentiel des 39 préfectures est arrêté** (03 §2, D8). Toute jointure territoriale passe par lui (R-01).
- **La limite majeure est connue** : les accidents ne sont publiés qu’au niveau national. Il n’y aura pas de classement territorial du risque (03 §1).
- **La couverture a été estimée sur la structure des fichiers** : 93 % de ce que demande l’énoncé ; 77 % des 43 indicateurs du 02 calculables, 47 % à la maille cible (03 §4). Le 04 confirme ou corrige ces taux en ouvrant les fichiers.
- **Ce que le 03 confie au 04** : les 13 écarts prévisibles à confirmer (03 §5), les observations à trancher (03 §7), dont « stock ou flux » pour le parc, et les questions 2, 3 et 6 du 01 (03 §6).

---

## 1. Objectif du Data Understanding

Le 04 répond, fichier par fichier puis indicateur par indicateur, à une question : **que la donnée permet-elle de dire, et que ne permet-elle pas de dire ?**

**Sorties :**
1. une fiche de profil par fichier (§3) ;
2. **un niveau de preuve pour chaque variable utilisée** (R-17) : **A** mesuré (comptage direct, recalculable), **B** calculé (dérivé d’une formule maîtrisée), **C** estimé (indicateur pré-calculé, proxy, méthode non documentée). Ce niveau suit la variable jusqu’à la recommandation ;
3. pour chacun des 43 indicateurs du 02 : calculable ou non, à quelle maille, avec quel niveau de preuve (§8) ;
4. les écarts au 02, confirmés et déclarés avec leur règle de repli (§7).

**Règles :**
- `data/raw/` n’est jamais modifié : le 04 lit, il ne nettoie pas.
- Une valeur manquante n’est jamais un zéro (R-10) : elle est comptée, et affichée « non renseignée ».
- Le 04 ne calcule ni indicateur à interpréter, ni seuil, ni classement : il vérifie qu’un indicateur est calculable. Les valeurs relèvent du 08.
- Un écart nouveau est déclaré avec son repli avant d’en lire l’effet sur les résultats (R-20).
- Aucune lecture causale.

**Frontière avec le 05 (qualité et validation).** Le 04 ne garde que les contrôles qui changent la calculabilité ou le niveau de preuve d’un indicateur. Le registre des anomalies, les exclusions et les contrôles bloquants appartiennent au 05 : les anomalies vues en 04 lui sont transmises (§4).

**Le 04 est terminé quand :**
- chaque fichier a sa fiche ;
- chaque variable utilisée a son niveau de preuve ;
- chaque indicateur, chaque écart et chaque piège a un résultat ;
- la question « stock ou flux » est tranchée ;
- les tests du référentiel sont passés (§5).

---

## 2. Méthode et outils

**Outils.**
- pandas pour les tableaux ;
- geopandas, shapely et pyproj pour les géométries, reprojetées en UTM 31N (R-16) ;
- pypdf pour les PDF ;
- ydata-profiling pour les rapports de profil ;
- Jupyter pour les notebooks.

Les versions sont figées dans `requirements.txt` (Python 3.11), installé dans un environnement `.venv` à la racine du dépôt, non versionné. ydata-profiling impose pandas 2.3 ; sur aarch64, il demande g++ pour compiler `phik`.

**Scripts**, dans `scripts/`, nommés comme ceux du 03 :

| Script | Rôle | Sorties |
| ------ | ---- | ------- |
| `profil_04.py` | Profil de chaque fichier et de chaque variable (§3) | `profil_fichiers.csv`, `profil_variables.csv`, rapports HTML |
| `extraction_pdf_04.py` | Tableaux du Livret 02 (population 2022 par préfecture, âge, sexe et milieu) ; de l’annuaire 2024, années 2020 à 2024 : accidents (7.2), état du réseau (39.2), parc, premières mises en circulation, deux-roues par centre d’immatriculation et permis (40.1 à 40.4) ; du profil OMS (tués, victimes par type d’usager, véhicules) | `data/interim/livret02_population_2022.csv`, `data/interim/annuaire2024_tableaux.csv`, `data/interim/oms_profil_2023.csv` |
| `jointures_04.py` | Tests du référentiel et des jointures (§5), et contrôles spatiaux du §4.3 ; lit la table de correspondance état ↔ tracé de `data/reference/` | `jointures.csv`, et les fichiers de `data/interim/` listés au §5 |
| `coherence_04.py` | Contrôles de cohérence non spatiaux (§4) | `controles_coherence.csv` |
| `faisabilite_04.py` | Faisabilité des 43 indicateurs : maille, période, couverture, niveau de preuve (§8, §10) | `faisabilite_indicateurs.csv`, `synthese_faisabilite.csv` |

**Notebooks**, un par objectif : `notebooks/04_O1.ipynb` à `04_O5.ipynb`, exécutés, avec un style commun (`notebooks/style_04.py`). Ils lisent les sorties des scripts et montrent les données de leur objectif : séries, cartes, et un tableau à côté de chaque graphique. Ils ne calculent aucun indicateur. Un chiffre cité dans le 04 est toujours lu dans un CSV écrit par un script, jamais tiré d’un notebook seul (R-19).

**Pour tout reproduire**, dans cet ordre : `profil_04.py`, `extraction_pdf_04.py`, `coherence_04.py`, `jointures_04.py`, `faisabilite_04.py`, puis les notebooks.

**Sorties**, dans `data/analysis/04_understanding/` : les CSV ci-dessus, `faisabilite_indicateurs.csv` (une ligne par indicateur) et `figures/`. Les rapports HTML, dans `rapports/`, ne sont pas versionnés : ils sont lourds et se régénèrent.

**EHCVM.** Ses conditions d’usage interdisent toute redistribution. Elle n’a donc pas de rapport ydata-profiling, qui recopie des lignes du fichier : seules des statistiques agrégées par zone sortent du script.

**Ordre de travail :**
1. profil des fichiers (§3) ;
2. référentiel et jointures (§5) ;
3. contrôles de cohérence (§4) ;
4. indicateurs, objectif par objectif (§8) ;
5. pièges et écarts (§6, §7) ;
6. synthèse (§10).

---

## 3. Profilage des données

**Périmètre.** Les 26 fichiers téléchargés des besoins D1 à D13, et les 3 tables de `data/reference/`. Les 5 sources hors 02 n’ont qu’un contrôle avant affichage (03 §3.2) ; les 3 fichiers recensés ne sont pas ouverts.

**Pour chaque fichier** (`profil_fichiers.csv`) :
- structure : format, encodage, séparateur, format long ou large ;
- volumétrie : lignes, colonnes, années, unités territoriales ;
- valeurs manquantes et doublons ;
- modalités et valeurs atypiques.

**Pour chaque variable utilisée** (`profil_variables.csv`) : type, unité, part de manquants, modalités, valeurs extrêmes, **niveau de preuve** et sa justification.

| Besoin | Fichiers | Lecture particulière |
| ------ | -------- | -------------------- |
| D1 | `parc_immatricule_par_type_1.csv`, `parc_immatricule_par_type_2.csv`, `transports_statistiques_cles.csv` | Format long du portail (indicateur, modalité, unité, date, valeur). Un même fichier peut mêler stock et flux |
| D2 | `permis_par_categorie.csv` | Format long ; total et catégories A à F dans la même colonne |
| D3 | `accidents_police_gendarmerie.csv`, `accidents_bilan_police_gendarmerie.csv`, `annuaire_statistique_national_2024.pdf`, `oms_profil_securite_routiere_2023.pdf` | Format long ; tableaux PDF extraits par script |
| D4 | `etat_reseau_routier.csv` | Format long, par tronçon et par état ; lignes de total mêlées aux tronçons |
| D5 | `routes_classees.csv` (+ métadonnées), `densite_reseau_routier.csv`, `geoportail_catalogue.json` | Géométrie en texte WKT (`MULTILINESTRING`), en degrés ; dictionnaire des champs dans les métadonnées |
| D6 | `auto_ecoles.csv` (+ métadonnées), `auto_ecoles_vehicules_metadonnees.csv` | Points WKT en degrés ; statut d’agrément ; colonnes `journee_ouverture` et `activite_categorie` à lire ; le jeu « Véhicules » ne publie que ses champs |
| D7 | `rgph_2022_population.csv`, `rgph5_livret02_age_milieu_prefecture.pdf`, `projections_demographiques_2011_2031.csv`, `population_region_sexe_2010.csv`, `wpp2024_population_age_simple_togo.csv` | Recensement : cinq niveaux dans une colonne ; Livret 02 : 47 tableaux PDF ; WPP : séparateur « \| », précédé d’une ligne `sep` |
| D8, D13 | `limites_administratives_hdx.geojson.zip`, `limites_administratives_hdx.xlsx`, `data/reference/referentiel_prefectures.csv` | 40 polygones de niveau 2 ; chefs-lieux et localités dans le fichier Excel |
| D9 | `oms_tues_pour_100000.json` | Réponse d’API (OData) |
| D11 | `data/reference/chronologie_reformes.csv` | Table compilée, une source par ligne |
| D12 | `ehcvm_2021_2022_csv.zip`, `dhs_possession_moto_velo_region.json` | EHCVM : quatre fichiers utiles, lus dans l’archive sans l’extraire ; pondérations obligatoires |
| PA-05 | `data/reference/ages_minimaux_permis.csv` | Table compilée |

**Résultat** (`profil_fichiers.csv`, `profil_variables.csv`, 2026-10-04) :

- **Lecture.** Les 29 fichiers donnent 59 tables (feuilles Excel, couches GeoJSON, listes JSON, fichiers de l’EHCVM) et 850 variables. Les textes sont en UTF-8. Les 11 fichiers longs du portail n’ont ni cellule vide ni valeur non numérique.
- ✅ **Niveaux de preuve.** Les 130 variables utilisées en ont un :
  - A (54) : comptages publiés, attributs des routes, position et statut des auto-écoles ;
  - B (4) : géométries dont les longueurs et surfaces sont recalculées en UTM 31N ;
  - C (39) : état du réseau, indicateurs pré-calculés, projections de l’INSEED, estimations de l’ONU et de l’OMS, enquêtes auprès des ménages, chefs-lieux, jours d’ouverture ;
  - sans objet (33) : dictionnaires, référentiel, clés, pondérations.

  Les projections de l’INSEED sont en C : les taux nationaux de 2011 à 2021 portent ce niveau ; ceux de 2010 et de 2022 reposent sur un recensement.

| Besoin | Constat | Suite |
| ------ | ------- | ----- |
| D1 | Parc : 8 types de 1990 à 2022 (fichier 1), 10 de 2013 à 2019 (fichier 2), lignes de total mêlées aux types ; statistiques clés : 4 roues, 2 roues, premières mises en circulation | Stock ou flux (§4.4) |
| D2 | Catégories A à F, 2007–2022 ; 2013 sans catégorie, avec un total à 0 | Piège nouveau (§6) |
| D3 | Trois séries nationales, sans territoire, mois, âge ni catégorie de véhicule | Écarts 1 et 2 (§7) |
| D4 | 88 libellés de tronçon, « TOTAL » compris ; lignes de total sur le tronçon (10) et sur l’état (88) ; état « TRAVAUX » sur 19 lignes | Rattachement (§5) ; R-14 |
| D5 | 799 tronçons, 38 préfectures, 4 types de route ; 8 tronçons à 0 voie ; 2 sans nom | Mô (§5) ; zéros transmis au 05 |
| D6 | 272 auto-écoles, 24 préfectures : 85 agréées, 47 antennes agréées, 138 non agréées, 2 « Néant » ; 163 adresses « Nsp » ; aucun doublon exact | R-12 : 132 auto-écoles comptées |
| D7 | Recensement : 745 unités dans une colonne, 14 doublons de libellé ; WPP : 17 variantes | Variante « Median » seule |
| D8, D13 | 40 unités de niveau 2 (version v02 du 7 janvier 2021) ; 31 chefs-lieux : 1 national, 4 régionaux, 26 préfectoraux | O4-08 (§5) |
| D9 | 4 pays, 2021 | Repère |
| D12 | EHCVM : 6 462 ménages, 6 zones ; fichiers des biens et des achats : seulement des « oui » ; DHS : 3 enquêtes, 7 régions | Piège nouveau (§6) |
| PDF | Annuaire : 776 pages, dont 765 avec du texte ; Livret 02 : 87 pages, dont 78 ; profil OMS : 1 page | Extraits sans OCR (`extraction_pdf_04.py`) : 6 tableaux de l’annuaire, les 47 du Livret 02 (aucun ne tombe sur une page sans texte), 17 valeurs du profil OMS |

---

## 4. Contrôles de cohérence

Chaque contrôle dit ce qu’il décide. Résultat possible : conforme ; écart expliqué ; anomalie transmise au 05.

**Résultat** (`controles_coherence.csv`, 2026-10-04) : 36 contrôles ; 16 conformes, 15 écarts expliqués, 5 anomalies transmises au 05. Le numéro entre crochets renvoie à la ligne du fichier. Les contrôles spatiaux du §4.3 sont faits par `jointures_04.py` (`jointures.csv`).

### 4.1 Cohérence interne

| Contrôle | Fichier | Ce qu’il décide | Résultat |
| -------- | ------- | --------------- | -------- |
| Le total égale la somme des types, chaque année | Parc 1 et 2 ; annuaire 40.1 à 40.4 | Fiabilité de O1-01 à O1-03 | Conforme : 33 années sur 33 (fichier 1), 7 sur 7 (fichier 2), 5 sur 5 pour chaque tableau de l’annuaire [4.1-01 à 4.1-03] |
| Le total égale la somme des catégories A à F | Permis | O1-06 | Écart expliqué : 15 années sur 15 ; 2013 n’a aucune catégorie et un total à 0 : « non renseignée » (écart 14) [4.1-04] |
| Bon + moyen + mauvais + travaux = total ; repérer les lignes de total | État du réseau | Pas de double compte dans O3-01 à O3-03 | Conforme : 84 tronçons sur 84 (52 revêtus, 32 en terre), à l’arrondi de 0,01 km près. Les lignes de total (« TOTAL », « TOTAL RT ») et les 2 lignes des voiries, sans tronçon, sont exclues des calculs. Un tronçon sans ligne « TRAVAUX » (67 tronçons) a 0 km en travaux, puisque ses états publiés font son total [4.1-05] |
| Bon + moyen + mauvais + travaux = 100 % | Annuaire 39.2 | O3-07 en pourcentage | Anomalie transmise au 05 : 7 lignes sur 9 ; 99,90 % pour les routes revêtues en 2022, 99,54 % pour l’ensemble en 2022 [4.1-06] |
| Accidents mortels ≤ accidents ; tués et blessés cohérents avec les accidents | Accidents | O2-05, O2-06 | Conforme : aucune série d’accidents mortels n’est publiée ; tués < accidents chaque année ; de 1,03 (2014) à 1,66 (2017) blessés par accident [4.1-07] |
| Modalités du statut d’agrément exhaustives | Auto-écoles | Décompte officiel (R-12) | Écart expliqué : 85 agréées, 47 antennes agréées, 138 non agréées, 2 « Néant » ; 132 auto-écoles comptées ; « Néant » transmis au 05 [4.1-08] |
| Hommes + femmes = ensemble ; urbain + rural = total ; somme des âges = total | Livret 02 | O1-07, O4-03, PA-03 | Anomalie transmise au 05 : un écart d’une personne (hommes ruraux de Doufelgou, 25-29 ans et 85 ans et plus), repris dans la Kara et au Togo ; le reste est exact. Une ligne, reconstituée à l’extraction, est hors contrôle [4.1-09] |
| Répartition des tués par usager = 100 % | Profil OMS | O2-09 | Écart expliqué : 100 % ; les catégories de véhicules ne font pas le total (« Other » non publié) [4.1-10] |

### 4.2 Cohérence temporelle

| Contrôle | Fichier | Ce qu’il décide | Résultat |
| -------- | ------- | --------------- | -------- |
| Années couvertes contre couverture déclarée : le portail annonce 2013–2019, le fichier couvre 1990–2022 | Parc | Période de O1 | Écart expliqué : O1 couvre 1990–2022, et jusqu’en 2024 avec l’annuaire [4.2-01] |
| Ruptures de série, repérées et annotées sans lecture causale | Parc, permis | Lecture de O1 ; H1 | Anomalies transmises au 05, annotées sur les graphiques de O1. Plus fortes variations : parc total en 1995 (+257 %) et 2004 (+67 %) ; deux-roues en 1995 (+636 %) ; permis en 2016 (+252 %) ; permis moto en 2019 (+497 %) et 2022 (+2 192 %), deux années de la chronologie [4.2-02] |
| Sous-catégories A1 à A3 après 2022 | Permis | O1-06, O1-09 | Conforme : aucune sous-catégorie, ni au portail (2007–2022) ni dans l’annuaire (2020–2024) [4.2-03] |
| Libellé « population résidente en 2022 » du fichier de 2010 | Population 2010 | Année réelle du fichier | Écart expliqué : libellé erroné ; le fichier ne contient que 2010 (6 191 155 habitants) [4.2-04] |
| Millésimes : état 2020, tracé et auto-écoles 2021–2022, population 2022 | D4 à D7 | Légitimité des croisements de l’année de référence (R-05) | Écart expliqué : routes et auto-écoles viennent de la campagne PRISE 2021/2022, croisables avec 2022 ; l’état par tronçon reste le relevé de 2020, daté comme tel [4.2-05] |

### 4.3 Cohérence géographique

| Contrôle | Fichier | Ce qu’il décide | Résultat |
| -------- | ------- | --------------- | -------- |
| Points et tronçons dans les limites du Togo, après reprojection en UTM 31N (R-16) | Routes, auto-écoles | O4-01, O4-04 | Écart expliqué : 272 auto-écoles sur 272 dans une préfecture ; 5,1 km des 3 366 km du tracé hors du Togo, exclus des longueurs par préfecture [4.3-05, 4.3-08] |
| La préfecture déclarée est celle du polygone qui contient le point | Routes, auto-écoles | Rattachement (R-01) | Écart expliqué : 97,0 % des tronçons et 98,5 % des auto-écoles. Les autres (24 tronçons, 35 km ; 4 auto-écoles entre Golfe, Agoè-Nyivé et Zio) suivent le polygone [4.3-06, 4.3-09] |
| Tronçons à cheval sur deux préfectures | Routes | Découpage (R-15) | Écart expliqué : 89 tronçons ; 77 km (2,3 % du tracé) hors de leur préfecture principale, comptés là où ils passent [4.3-07] |
| « Maritime » avec ou sans le Grand Lomé, source par source ; la somme des zones égale le total national | Toutes (R-04) | Lecture en 6 zones (R-02, R-03) | Conforme : les 6 zones font le total national dans le recensement, le Livret 02 et la population 2010. « Maritime » exclut le Grand Lomé dans le recensement (où il s’appelle « DAGL ») et dans l’EHCVM ; il l’inclut dans les routes et les auto-écoles, et dans la DHS (« Ensemble Maritime »). La zone est donc toujours lue par la préfecture [4.3-01 à 4.3-04] |

### 4.4 Cohérence entre sources

| Contrôle | Sources | Ce qu’il décide | Résultat |
| -------- | ------- | --------------- | -------- |
| ✅ Parc publié face aux 93 944 véhicules immatriculés en 2021 selon l’OMS : **stock ou flux ?** | Parc, annuaire, profil OMS | Dénominateur de O2-04 ; utilité de O1-05 | **Flux.** Chaque année de 2020 à 2024, les 4 roues et plus du « parc » égalent les premières mises en circulation, neufs et occasions (23 890, 28 581, 26 131, 23 014, 22 605). Une seule série : le fichier 1 égale les statistiques clés (33 années sur 33) et le fichier 2. Les 93 944 véhicules de l’OMS sont les immatriculations de 2021, catégorie par catégorie, et ses « 4 roues » ne comptent que les voitures. O2-04 suit R-11 jusqu’au cumul (C) ; écart 16 [4.4-01 à 4.4-04] |
| Trois séries d’accidents ; annuaire 2024 ; tués de 2022 face aux 683 de l’énoncé | D3 | Série de référence de O2-01 ; définition du tué | Conforme : les séries sont identiques sur leurs années communes ; série de référence 2010–2024 (statistiques clés, puis annuaire) ; 7 507 accidents et 683 tués en 2022, comme l’énoncé. Aucune source ne définit le tué ni ne dit les accidents « corporels » (écart 15) [4.4-05] |
| ✅ Indicateur « accidents mortels / 100 000 hab. » : accidents ou tués ? Sur quelle population ? | Statistiques clés | Réutilisable ou non | Anomalie transmise au 05 : accidents constatés ÷ population de l’INSEED × 100 000, exactement (projection de 2011 à 2021, recensement en 2022) ; en 2010, la population utilisée est la projection de 2011. Non repris : O2-03 est recalculé (B) [4.4-06] |
| Projections et recensement en 2022 | D7 | Dénominateur de chaque année (R-06) | Écart expliqué : +0,34 % (8 068 000 projetés, 8 095 498 recensés) ; saut annoté en 2022 [4.4-07] |
| WPP face à l’INSEED | D7 | Population 1990–2009, étiquetée C | Écart expliqué : +8,7 % en 2010 ; +12,3 % en 2022 face au recensement (+12,7 % face à la projection : c’est le chiffre du 03) ; seuls les parts par âge et les taux de croissance servent [4.4-08] |
| Permis : portail face à l’annuaire | D2 | Période de O1-06 | Conforme : 3 années sur 3 identiques (2020–2022) ; l’annuaire ajoute 2023 et 2024 [4.4-09] |
| Ménages possédant une moto (EHCVM, pondérée) face au parc des deux-roues | D1, D12 | Ordre de grandeur du piège « motos non immatriculées », étiqueté C | Écart expliqué : 32,6 % des ménages ont au moins une moto, soit 683 541 motos (pondéré). Les deux-roues immatriculés en cumul jusqu’en 2021 font 360 276 sur 7 ans (PA-01), entre 249 336 et 496 997 : 1,9 moto possédée par deux-roues immatriculé (1,4 à 2,7), en C [4.4-10] |
| Longueur des routes classées, calculée, face à la densité nationale publiée | D5 | O4-01, O4-02 | Écart expliqué : routes revêtues, 2 236 km sur le tracé, contre 2 348 km par la densité (−4,8 %) et 2 198 km dans l’état du réseau (+1,7 %) ; routes non revêtues, de −10,6 % à −16,3 % ; voiries, périmètres sans rapport. O4-01 et O4-02 sont calculés sur le tracé (B) [4.4-11] |
| Kilomètres revêtus selon l’OMS | Profil OMS | Usage du chiffre | Anomalie transmise au 05 : 11 777 km en 2021, 5,3 fois le réseau revêtu ; jamais utilisé [4.4-12] |

### 4.5 Contrôle des totaux

| Contrôle | Fichier | Ce qu’il décide | Résultat |
| -------- | ------- | --------------- | -------- |
| Préfectures → régions → pays | Livret 02 | O1-07 ; PA-03 | Conforme : 39 préfectures ; chaque zone et le pays égalent la somme de leurs préfectures (8 095 498) [4.5-01] |
| Livret 02 face au recensement CSV, préfecture par préfecture | D7 | Choix du dénominateur 2022 | Conforme : 39 sur 39 identiques ; les 5 libellés de préfecture en double dans le CSV sont résolus par la valeur la plus élevée [4.5-02] |
| Niveaux du recensement sans code ; libellés en double ; total par niveau | Recensement CSV | Lecture des préfectures | Conforme : 745 libellés pour 759 lignes ; les 6 zones, les 39 préfectures et le pays font 8 095 498 [4.5-03] |
| Somme des pondérations cohérente avec le nombre de ménages ; 6 zones présentes | EHCVM | Parts par zone | Écart expliqué : 6 462 ménages, 1 877 870 ménages pondérés ; population pondérée 8 081 764 (−0,2 % du recensement) ; parts des zones égales à celles du recensement [4.5-04] |
| Ligne absente : « non » ou « non renseigné » ? | EHCVM | Calcul des parts (R-10) | Écart expliqué : les 2 029 ménages ayant une ligne « moto » sont ceux que le producteur compte ; 142 ménages (1,5 % pondéré) n’ont rempli aucune ligne des biens, et 116 aucune des achats : ils sont « non renseignés » [4.5-05] |

**Transmis au 05** :
- les 5 anomalies ci-dessus [4.1-06, 4.1-09, 4.2-02, 4.4-06, 4.4-12] ;
- une anomalie des jointures : le taux de couverture de l’entretien routier [4.3-11] ;
- celles du profil (§3) : 8 tronçons à 0 voie ; 2 auto-écoles au statut « Néant » ;
- les deux-roues et trois-roues de 2024 dans l’annuaire (6 487 et 59 106, contre 62 736 et 4 903 en 2022), hors année de référence [4.4-01].

---

## 5. Référentiel des préfectures : tests

✅ Le référentiel est arrêté (03, D8). Le 04 le met à l’épreuve sur les données.

**Résultat** (`jointures.csv`, 2026-10-04) : 22 tests, dont 12 conformes, 9 écarts expliqués et 1 anomalie transmise au 05 (contrôles spatiaux et sources hors 02 compris). Le script écrit aussi, dans `data/interim/` :
- les 39 préfectures (`prefectures_2022.geojson`) ;
- le tracé découpé par préfecture (`routes_par_prefecture.csv`) ;
- les auto-écoles rattachées à leur polygone (`auto_ecoles_prefecture.csv`) ;
- les 84 tronçons de l’état du réseau rattachés au tracé (`etat_troncons_rattaches.csv`) ;
- un point de départ par préfecture pour O4-08, le chef-lieu ou le point d’étiquette (`points_depart_o4_08.csv`).

| Test | Attendu | Résultat |
| ---- | ------- | -------- |
| Fusion des polygones TG0303 (Golfe) et TG0305 (Lomé Commune) | Un seul polygone pour le Golfe ; sa surface égale la somme des deux | Conforme : un seul polygone, 240,8 km² ; 40 unités HDX donnent les 39 préfectures [5-01, 5-02] |
| Kpendjal-Ouest et « Naki-Ouest » (TG0518) | Les routes et les auto-écoles déclarées à Kpendjal-Ouest tombent dans TG0518 | Conforme : 36,3 km sur les 38,7 km déclarés tombent dans TG0518 ; aucune auto-école n’y est déclarée [5-04, 5-07] |
| Absence de Mô dans les routes classées | Vrai vide ou défaut de rattachement | Vrai vide : aucun tronçon ne passe dans le polygone de Mô. Mô a 0 km de route classée dans la couche [5-05] |
| Codes de région dans le nom des tronçons (« TGRM… », « TGRP… ») | Code = région du polygone | 792 sur 797 concordent ; le code ne sert pas au rattachement [5-03] |
| Chefs-lieux HDX (D13) | Un point par préfecture | Écart expliqué : 31 points dans 30 préfectures ; 9 préfectures n’en ont aucun (Agoè-Nyivé, Akébou, Anié, Cinkassé, Danyi, Kpendjal-Ouest, Kpélé, Mô, Oti-Sud) [5-09]. Chacune a un point d’étiquette HDX dans son polygone : repli de O4-08 (écart 19) [5-15] |

**Jointures testées.** Le taux de rattachement attendu est de 100 % ; tout reste est listé.

| Besoin | Jointure | Clé | Attendu | Résultat |
| ------ | -------- | --- | ------- | -------- |
| D4 → D5 | État du réseau → routes classées | Nom du tronçon (aucun identifiant commun) | Part des 84 tronçons rattachés ; à défaut, lecture par type de route et par région (03 §5) | 84 tronçons sur 84 (100 % des km évalués) : 59 par le nom exact, 16 par le nom normalisé, 2 par un nom proche validé, 7 par l’axe. Les 7 sont sur 4 axes de la région Maritime et du Grand Lomé, que l’état et le tracé découpent ou numérotent autrement : RN1 Lomé–Amakpapé, RN2/3 Aflao–frontière du Bénin, RN34 Lomé–Vogan–Anfoin, RN4 Tsévié–Tabligbo–Aného. Noms proches et axes sont dans une table de correspondance validée, une raison et une source par ligne (`data/reference/correspondance_etat_trace.csv`). La longueur du tracé confirme le rattachement : rapport médian de 1,00 (quartiles 0,99 et 1,00), de 0,98 à 1,03 pour les axes ; aucun nom du tracé rattaché deux fois [5-10] |
| D5 | Routes classées → référentiel | Nom de préfecture, puis contrôle spatial | 38 préfectures ; absence de Mô expliquée | Conforme : 38 noms, tous dans le référentiel ; 38 préfectures traversées, Mô sans tracé [5-06] |
| D6 | Auto-écoles → référentiel | Nom de préfecture, puis contrôle spatial | 24 préfectures | Conforme : 24 préfectures ; 16 ont au moins une auto-école agréée ou antenne agréée ; 15 n’ont aucune auto-école [5-08] |
| D7 | Recensement CSV et Livret 02 → référentiel | Libellé de préfecture | 39 sur 39 | Conforme : 39 sur 39 dans chaque source [5-12] |
| D8 | Polygones HDX → référentiel | Code HDX (pcode) | 40 unités → 39 préfectures | Conforme [5-02] |
| D12 | EHCVM → 6 zones | Code de région | 6 zones | Conforme : codes 1 à 6, le 6 étant le Grand Lomé [5-13] |
| D3 | — | — | Aucune jointure : accidents nationaux (03 §5) | Confirmé [5-14] |

**Part du réseau national non évaluée** (R-14, O3-06) : 99 km sur 3 100 km de routes nationales (3,2 %) n’ont aucun tronçon d’état rattaché [5-11].

---

## 6. Pièges du 02 : confirmés, infirmés, nouveaux

Les pièges viennent de la colonne « Piège connu » du 02 (`06_Donnees_requises`).

| Besoin | Piège (02) | Vérification en 04 | Statut |
| ------ | ---------- | ------------------ | ------ |
| D1 | Lieu d’enregistrement ≠ lieu d’usage | Sans objet tant que D1 reste national | Actif si l’on utilise les deux-roues par centre d’immatriculation de l’annuaire (tableau 40.3) |
| D1 | Pics administratifs | Ruptures de série (§4.2) | Confirmé : ruptures en 1995 et 2004 (parc), en 2016, 2019 et 2022 (permis) ; annotées sans lecture causale [4.2-02] |
| D1 | Motos non immatriculées | Ordre de grandeur avec l’EHCVM (§4.4) | Ordre de grandeur : 1,9 moto possédée par deux-roues immatriculé en 7 ans (1,4 à 2,7), en C [4.4-10] |
| D2 | Renouvellements mêlés aux premières délivrances | Libellé « délivrés aux examens » ; métadonnées du portail | Non tranché : le portail parle de permis « attribués lors des examens », sans définition |
| D2 | Nomenclature togolaise | Catégories présentes ; A1 à A3 (§4.2) | Confirmé : catégories A à F seulement, aucune sous-catégorie jusqu’en 2024 [4.2-03] |
| D3 | Sous-déclaration | 680 tués déclarés contre 1 961 estimés par l’OMS en 2021 : repère SE-03 | Confirmé : 1 961 tués estimés (1 644 à 2 277) pour 680 déclarés en 2021 (`oms_profil_2023.csv`) ; repère seulement |
| D3 | Définition du tué | Annuaire, métadonnées, profil OMS | Confirmé : aucune définition, ni au portail, ni dans l’annuaire (« nombre de morts »), ni au profil OMS [4.4-05] |
| D3 | « Maritime » avec ou sans le Grand Lomé | Sans objet : accidents nationaux | Sans objet |
| D4 | Relevé ancien ; tronçons non évalués ; méthode non documentée | Date du relevé ; part non évaluée (R-14) ; preuve C pour l’état | Méthode : confirmé, aucune documentation (C). Relevé par tronçon de 2020 ; l’annuaire donne des pourcentages jusqu’en 2022 [4.2-05]. Part non évaluée : 3,2 % des routes nationales [5-11] |
| D5 | Jointure D4–D5 sur l’identifiant du tronçon | Pas d’identifiant commun : rattachement par le nom (§5) | Confirmé : aucun identifiant commun. Les 84 tronçons sont rattachés, 77 par le nom et 7 par l’axe (table de correspondance), et les longueurs le confirment [5-10] |
| D6 | Géocodage ; doublons ; agréée ≠ active | Contrôle spatial (§4.3) ; doublons sur le nom et les coordonnées ; R-12 | Doublons : aucun doublon exact. Activité : confirmé, aucune variable ne la mesure (écart 13). Géocodage : les 272 points sont dans le Togo, 98,5 % dans leur préfecture déclarée [4.3-08, 4.3-09] |
| D7 | Grand Lomé publié à part de la Maritime | Somme des zones égale au total (R-04) | Confirmé et traité : les 6 zones font le total national dans chaque source ; la zone est lue par la préfecture [4.3-01 à 4.3-04] |
| D8 | Noms différents selon les sources ; découpage à confirmer | ✅ Traité par le référentiel ; tests du §5 | Confirmé et traité : tests du §5 conformes [5-01, 5-02, 5-12] |
| D9 | Estimation modélisée | Repère seulement (SE-03) | Confirmé : C |
| D10 | Rarement publiés | National seulement : contexte | Confirmé : trafic national de 2014 à 2022 seulement (statistiques clés), en C |
| D11 | Sources dispersées | Table compilée, une source par ligne | Confirmé : 10 mesures, une source chacune |
| D12 | Enquête déclarative ; année différente | EHCVM 2021-2022, proche de 2022 ; DHS jusqu’en 2017 pour la tendance | Confirmé, en C. L’EHCVM est calée sur le recensement de 2022 : population pondérée à −0,2 %, parts des zones identiques [4.5-04] |
| D13 | Sans grille, O4-08 est calculé depuis les chefs-lieux (C) | Chefs-lieux HDX (C), ou WorldPop en repli (03 §3.3) | Aggravé : 9 préfectures sans chef-lieu ; repli par le point d’étiquette HDX (écart 19) [5-09, 5-15] |

**Pièges repérés au 03** : tous confirmés par le profil (§3).
- Parc : libellé « Voitues » ; les deux fichiers se recoupent sur 2013–2019 avec des catégories différentes (le fichier 2 sépare les deux-roues par cylindrée).
- État du réseau : lignes de total, sur le tronçon et sur l’état. Les codes de région dans le nom des tronçons sont traités au §5.
- Recensement : « TOTOAL AVE » ; 14 doublons de libellé.
- Population 2010 : libellé « population résidente en 2022 ».
- EHCVM : codes de préfecture de l’ancien découpage, non utilisés.
- Auto-écoles : 163 adresses « Nsp », et 8 « Néant ».

**Pièges découverts en 04 :**
1. **Permis, 2013** : aucune catégorie n’est publiée, et le total vaut 0. L’année manque aussi dans les statistiques clés. Ce zéro marque une absence : 2013 est « non renseignée » (R-10), sans interpolation.
2. **Libellés trompeurs du portail**, prouvés au §4.4 :
   - le « parc automobile immatriculé » désigne les immatriculations de l’année ;
   - les « premières mises en circulation » des statistiques clés ne comptent que les véhicules neufs ;
   - « Accidents mortels /100 000 hab » rapporte tous les accidents constatés à la population ;
   - les « véhicules à 4 roues » du profil OMS ne comptent que les voitures ;
   - l’état du réseau numérote « RN4 » la route Lomé–Vogan–Anfoin, qui est la RN34 (§5).

   Un libellé du portail n’est jamais repris sans vérification.
3. **EHCVM, biens et achats** : seules les réponses « oui » sont publiées.
   - Une ligne absente vaut « non » si le ménage a rempli la section, et « non renseigné » sinon (R-10).
   - Une part se calcule par zone : somme des poids des ménages qui ont la ligne, divisée par la somme des poids des ménages qui ont rempli la section.
   - Les agrégats du producteur (`moto` et `car` du fichier des ménages) ne traitent pas de la même façon les ménages sans section : ils ne sont pas utilisés.

   Les effectifs sont au §4.5.
4. **Auto-écoles** : `activite_categorie` ne prend qu’une valeur, « {Auto-école} » ; `journee_ouverture` donne des jours déclarés, dont 16 « Nsp ». Aucune des deux ne mesure l’activité.
5. **Routes classées** : 8 tronçons ont 0 voie. Zéro ou absence : la question est transmise au 05.

---

## 7. Écarts avec le 02

✅ Ces écarts ont été listés au 03 (§5) avant l’ouverture des fichiers, comme l’exige R-20. Le 04 en apporte la preuve, puis les déclare avec leur repli.

| N° | Écart prévu (03 §5) | Preuve à apporter | Résultat |
| -- | ------------------- | ----------------- | -------- |
| 1 | Accidents nationaux seulement | Aucune variable territoriale dans les trois séries ni dans l’annuaire | Confirmé (§3 ; annuaire, tableau 7.2) |
| 2 | Accidents sans mois, heure, âge, catégorie de véhicule, immatriculation ni cause | Variables des fichiers D3 | Confirmé : accidents, tués et blessés par année, rien d’autre (§3) |
| 3 | Victimes par type d’usager, pour 2021 seulement (OMS) | Tableau du profil OMS | Confirmé : part des tués déclarés pour 5 types d’usager, 2021, sans sexe ni âge [4.1-10] |
| 4 | Tués estimés par l’OMS | Repère SE-03, jamais une correction des tués déclarés | Confirmé : 1 961 estimés (1 644 à 2 277) pour 680 déclarés en 2021 |
| 5 | Permis sans sexe, âge, territoire ni mois | Variables du fichier D2 | Confirmé : catégorie et année seulement, au portail comme dans l’annuaire (§3) |
| 6 | Âges minimaux tirés de sources secondaires | Dernière recherche du décret n° 2022-085/PR | **Trouvé** : décret n° 2022-085/PR du 3 août 2022, article 9 ([Journal officiel n° 41 bis du 7 octobre 2022](https://jo.gouv.tg/sites/default/files/JO/JOS_07_10_2022%20-%2067%20E%20ANNEE%20N%C2%B041%20BIS.pdf), p. 123-124). Âges : A1 14 ans, A2 16 ans, A3 18 ans, B 18 ans, C 21 ans, D 21 ans, F 18 ans ; E sans âge propre (épreuve pratique de B, C ou D réussie). ✅ `ages_minimaux_permis.csv` est mise au décret : E à 18 ans et non 21, car le B est exigé avant toute autre catégorie (art. 12) ; A2 à 16 ans dans le libellé ; A reste à 18 ans, les permis étant publiés sans sous-catégorie. Ces âges valent depuis août 2022 ; avant, ils restent non documentés : O1-07 reste en C |
| 7 | Population avant 2010 reconstituée avec les taux de croissance de WPP | Série sans rupture en 2010 | À établir avec O1-04 (§8) ; écart de niveau de WPP : +8,7 % en 2010 [4.4-08] |
| 8 | Population par préfecture pour 2022 seulement | Aucune série préfectorale annuelle | Confirmé : Livret 02 et recensement CSV, identiques, pour 2022 seulement [4.5-01, 4.5-02] |
| 9 | Mobilité nationale seulement | Aucune variable territoriale dans D1 et D2 | Confirmé pour les préfectures. L’annuaire ventile les deux-roues entre 6 centres d’immatriculation (2020–2024) : c’est le lieu d’enregistrement, pas celui de l’usage (piège D1) |
| 10 | Chronologie sans réforme datée avant 2013 | Table compilée (rien à profiler) | Confirmé : première mesure le 7 juin 2013 |
| 11 | Enquêtes auprès des ménages au lieu des parts modales (D12) | Variables de l’EHCVM ; parts pondérées calculables par zone | Confirmé : parts pondérées calculables dans les 6 zones, avec la règle des lignes absentes [4.5-04, 4.5-05] |
| 12 | État du réseau : un seul relevé, sans géométrie | Rattachement D4 → D5 (§5) | Confirmé : un seul relevé par tronçon (2020). Les 84 tronçons sont rattachés au tracé, dont 7 par l’axe : O3-01 à O3-03 et O3-06 par préfecture, partout [5-10] |
| 13 | Auto-écoles sans activité ni capacité | Contenu de `journee_ouverture` et `activite_categorie` ; champs du jeu « Véhicules » | Confirmé : aucune des deux colonnes ne mesure l’activité (§6). Le dictionnaire décrit 83 champs collectés, dont `personnel_nombre`, `activite` et `horaire_ouverture`, mais le fichier n’en publie que 12. Le jeu « Véhicules » ne publie que ses champs |
| — | Écart favorable possible : le parc publié est un stock | Contrôle « stock ou flux » (§4.4) | Infirmé : c’est un flux [4.4-01 à 4.4-04] |
| — | Deux sources hors 02, en contexte | Contrôle avant affichage (03 §3.2) | Équipements : conforme, plus de 99 % des points dans une préfecture, affichables en couche facultative [4.3-10]. Longueur entretenue : citable en annexe de O3 (km, 2016–2019) ; le taux de couverture (0 ou 1 %) est inutilisable et transmis au 05 [4.3-11] |

**Écarts nouveaux**, non prévus par le 03. Ils sont déclarés ici avec leur repli, avant tout calcul d’indicateur (R-20).

| N° | Écart | Indicateurs | Repli | Preuve |
| -- | ----- | ----------- | ----- | ------ |
| 14 | Permis : 2013 non publiée | O1-06, O1-07, O1-09 | 2013 « non renseignée », sans interpolation ; taux de croissance calculés sur les seules années publiées | [4.1-04] |
| 15 | Accidents « constatés » par la police et la gendarmerie : aucune source ne les dit corporels | O2-01, O2-03, O2-05, O2-06 | Indicateurs nommés « accidents constatés » ; le comptage reste en A | [4.4-05] |
| 16 | Le parc publié est un flux : aucun stock de véhicules n’est publié | O1-05, O2-04 | R-11 : cumul des immatriculations sur une durée de vie (PA-01), en C et en fourchette ; O1-01 lit directement la série | [4.4-01 à 4.4-04] |
| 19 | Chefs-lieux HDX pour 30 préfectures sur 39 | O4-08 | ✅ Distance depuis le chef-lieu ; à défaut, depuis le point d’étiquette HDX de la préfecture ; en C : distance d’un point, pas de la population. Les 9 préfectures mesurées depuis le point d’étiquette sont signalées comme telles | [5-09, 5-15] |

**Écarts favorables**, établis par l’extraction des PDF et déclarés avant calcul (R-20) :

| N° | Écart | Indicateurs | Repli | Preuve |
| -- | ----- | ----------- | ----- | ------ |
| 17 | Séries nationales prolongées jusqu’en 2024 par l’annuaire : parc, permis, accidents | O1-01 à O1-03, O1-06, O2-01 | Années 2023 et 2024 affichées ; l’année de référence reste 2022 (R-05) | [4.1-03, 4.4-05, 4.4-09] |
| 18 | État du réseau national, en pourcentage par catégorie de route, de 2020 à 2022 (annuaire 39.2) | O3-07 | « Non » devient un repli : évolution nationale en %, en C, avec les réserves de 4.1-06 | [4.1-06] |

---

## 8. Validation des données par objectif (43 indicateurs)

Colonnes :
- **Preuve (02)** : le niveau attendu par le 02 ;
- **Prévu (03)** : la calculabilité estimée au 03 (§4.2) ;
- **À vérifier** : ce que le 04 doit établir ;
- **Résultat** : cible, repli ou non, avec la maille obtenue ;
- **Preuve (04)** : le niveau retenu.

### O1 — Immatriculations et permis (9 indicateurs)

| ID | Indicateur | Données | Preuve (02) | Prévu (03) | À vérifier | Résultat | Preuve (04) |
| -- | ---------- | ------- | ----------- | ---------- | ---------- | -------- | ----------- |
| O1-01 | Immatriculations par catégorie | D1 | A | Cible | Flux ou stock ; catégories voiture, moto, poids lourd | Cible : national, 1990–2024 | A |
| O1-02 | Part de chaque catégorie | D1 | B | Cible | Total égal à la somme des catégories | Cible : national, 1990–2024 | B |
| O1-03 | Croissance annuelle, taux de croissance annuel moyen, multiplicateur | D1 | B | Cible | Série continue ; ruptures annotées | Cible : national, 1990–2024 ; réserve : ruptures de 1995 et 2004 à annoter | B |
| O1-04 | Immatriculations pour 1 000 habitants | D1, D7 | B | Cible | Population de chaque année ; 1990–2009 reconstituée (C) | Cible : national, 1990–2024 | B en 2010 et 2022, C les autres années |
| O1-05 | Parc estimé | D1 | C | Cible | Utile seulement si le parc publié n’est pas un stock (R-11) | Cible : national, 2009–2024 | C |
| O1-06 | Permis délivrés par catégorie | D2 | A | Cible | Premières délivrances ou renouvellements ; A1 à A3 | Cible : national, 2007–2024 (sans 2013) ; réserve : premières délivrances non prouvées (piège D2) | A |
| O1-07 | Permis pour 1 000 habitants en âge de conduire | D2, D7 | B | Cible | Âges minimaux (C) ; groupes d’âges découpés avec WPP | Cible : national, 2007–2024 (sans 2013) | C |
| O1-08 | Permis par sexe et tranche d’âge | D2 | A | Non | Confirmer l’absence du sexe et de l’âge | Non : Aucune variable de sexe ni d'âge (§3) | — |
| O1-09 | Rapport immatriculations / permis, par catégorie | D1, D2 | B | Cible | Correspondance entre catégories de véhicules et de permis | Cible : national, 2007–2024 (sans 2013) ; réserve : correspondance des catégories de véhicules et de permis à fixer au 06 | B |

### O2 — Sécurité routière (14 indicateurs)

| ID | Indicateur | Données | Preuve (02) | Prévu (03) | À vérifier | Résultat | Preuve (04) |
| -- | ---------- | ------- | ----------- | ---------- | ---------- | -------- | ----------- |
| O2-01 | Accidents corporels, blessés, tués | D3 | A | Repli : national | Série de référence parmi les trois ; accidents « corporels » ; définition du tué | Repli : national, 2010–2024 ; réserve : libellé « accidents constatés » | A |
| O2-02 | Tués pour 100 000 habitants | D3, D7 | B | Repli : national | Population de chaque année (R-06) | Repli : national, 2010–2024 | B en 2010 et 2022, C les autres années |
| O2-03 | Accidents corporels pour 100 000 habitants | D3, D7 | B | Repli : national | Population de chaque année (R-06) | Repli : national, 2010–2024 ; réserve : libellé « accidents constatés » | B en 2010 et 2022, C les autres années |
| O2-04 | Tués pour 10 000 véhicules | D1, D3 | B ou C | Cible (national) | Stock ou flux : parc publié (B) ou cumul (C) (R-11) | Cible : national, 2010–2024 | C |
| O2-05 | Tués pour 100 accidents corporels | D3 | B | Repli : national | Mêmes accidents au numérateur et au dénominateur | Repli : national, 2010–2024 ; réserve : accidents constatés (écart 15) | B |
| O2-06 | Blessés pour 100 accidents corporels | D3 | B | Repli : national | Mêmes accidents au numérateur et au dénominateur | Repli : national, 2010–2024 ; réserve : accidents constatés (écart 15) | B |
| O2-07 | Accidents par catégorie de véhicule impliqué | D1, D3 | B ou C | Non | Confirmer l’absence de la catégorie | Non : Aucune catégorie de véhicule impliqué (§3) | — |
| O2-08 | Surreprésentation d’une catégorie | D1, D3 | B ou C | Non | Confirmer l’absence de la catégorie | Non : Aucune catégorie de véhicule impliqué (§3) | — |
| O2-09 | Victimes par type d’usager, sexe et âge | D3 | A | Repli : type d’usager, 2021 (OMS) | Tableau du profil OMS, sans sexe ni âge | Repli : national, type d'usager, 2021 | C |
| O2-10 | Part des véhicules non immatriculés parmi les impliqués | D3 | A | Non | Confirmer l’absence de la variable | Non : Aucune variable d'immatriculation des véhicules impliqués (§3) | — |
| O2-11 | Indice de saisonnalité | D3 | B | Non | Confirmer l’absence du mois | Non : Aucun mois (§3) | — |
| O2-12 | Accidents pour 100 km de route classée | D3, D5 | B | Non | Accidents sans territoire | Non : Accidents sans territoire ; repli prévu à la zone seulement (§3) | — |
| O2-13 | Surreprésentation des jeunes conducteurs | D3, D7 | B | Non | Confirmer l’absence de l’âge | Non : Aucun âge des conducteurs (§3) | — |
| O2-14 | Accidents par cause déclarée | D3 | A | Non | Confirmer l’absence de la cause | Non : Aucune cause (§3) | — |

### O3 — État du réseau (7 indicateurs)

| ID | Indicateur | Données | Preuve (02) | Prévu (03) | À vérifier | Résultat | Preuve (04) |
| -- | ---------- | ------- | ----------- | ---------- | ---------- | -------- | ----------- |
| O3-01 | Km par état | D4, D5 | B | Repli : région | Lignes de total ; rattachement au tracé (§5) | Cible : préfecture, 2020 ; réserve : RN1 Lomé–Amakpapé, RN34 Lomé–Vogan–Anfoin, RN2/3 Aflao–frontière du Bénin, RN4 Tsévié–Tabligbo–Aného rattachées par l'axe (table de correspondance) : leur état est réparti le long de l'axe, au prorata des km | C |
| O3-02 | Part des km en mauvais état | D4, D5 | B ou C | Repli : région | Rattachement au tracé ; méthode de notation inconnue (C) | Cible : préfecture, 2020 ; réserve : RN1 Lomé–Amakpapé, RN34 Lomé–Vogan–Anfoin, RN2/3 Aflao–frontière du Bénin, RN4 Tsévié–Tabligbo–Aného rattachées par l'axe (table de correspondance) : leur état est réparti le long de l'axe, au prorata des km | C |
| O3-03 | Part des km en travaux | D4 | B | Repli : région | Rattachement au tracé | Cible : préfecture, 2020 ; réserve : RN1 Lomé–Amakpapé, RN34 Lomé–Vogan–Anfoin, RN2/3 Aflao–frontière du Bénin, RN4 Tsévié–Tabligbo–Aného rattachées par l'axe (table de correspondance) : leur état est réparti le long de l'axe, au prorata des km | C |
| O3-04 | Km par type de route et par état | D4, D5 | B | Cible | Quatre types du relevé | Cible : zone, 2020 ; réserve : RN1 Lomé–Amakpapé, RN34 Lomé–Vogan–Anfoin, RN2/3 Aflao–frontière du Bénin, RN4 Tsévié–Tabligbo–Aného rattachées par l'axe (table de correspondance) : leur état est réparti le long de l'axe, au prorata des km | C |
| O3-05 | Tronçons critiques | D4, D5 | A | Cible | Tronçons nationaux identifiables dans les libellés | Cible : tronçon, 2020 | C |
| O3-06 | Part du réseau non évaluée | D4, D5 | B | Repli : région | Longueur non évaluée (R-14) | Cible : préfecture, 2020 (état), 2021-2022 (tracé) ; réserve : 99 km de routes nationales sans état (3,2 %), affichés comme non évalués | B |
| O3-07 | Évolution de l’état | D4 | B | Non | Confirmer qu’il n’existe qu’un relevé | Repli : national, par catégorie de route, 2020–2022 ; réserve : pourcentages seulement, sans km | C |

### O4 — Réseau et auto-écoles (9 indicateurs)

| ID | Indicateur | Données | Preuve (02) | Prévu (03) | À vérifier | Résultat | Preuve (04) |
| -- | ---------- | ------- | ----------- | ---------- | ---------- | -------- | ----------- |
| O4-01 | Km de routes classées, par classe | D5 | B | Cible | Longueurs en UTM 31N (R-16) ; tronçons à cheval (R-15) | Cible : préfecture, Collecte 2021-2022 | B |
| O4-02 | Densité routière | D5, D8 | B | Cible | Surfaces HDX, Golfe fusionné (§5) | Cible : préfecture, Collecte 2021-2022 | B |
| O4-03 | Km de routes pour 10 000 habitants | D5, D7 | B | Cible | Population 2022 par préfecture | Cible : préfecture, 2022 | B |
| O4-04 | Nombre d’auto-écoles | D6 | A | Cible | Doublons ; agréées et antennes agréées (R-12) ; colonnes d’activité | Cible : préfecture, Collecte 2021-2022 ; réserve : activité non vérifiée (écart 13) | A |
| O4-05 | Auto-écoles pour 100 000 habitants | D6, D7 | B ou C | Cible | Activité inconnue : C (R-12) | Cible : préfecture, 2022 ; réserve : activité non vérifiée (écart 13) | C |
| O4-06 | Habitants par auto-école | D6, D7 | B | Cible | Non défini sans auto-école | Cible : préfecture, 2022 ; réserve : activité non vérifiée (écart 13) | C |
| O4-07 | Préfectures sans auto-école | D6, D7 | B | Cible | 15 préfectures sans auto-école recensée ; recompter avec les seules agréées et antennes agréées | Cible : préfecture, 2022 ; réserve : activité non vérifiée (écart 13) | B |
| O4-08 | Distance à l’auto-école la plus proche | D6, D13 | B ou C | Cible | Chefs-lieux HDX (C) ou grille WorldPop | Repli : préfecture, Collecte 2021-2022 ; réserve : distance d'un point par préfecture, pas de la population ; les préfectures mesurées depuis le point d'étiquette sont signalées comme telles | C |
| O4-09 | Capacité de formation | D6, D7 | A | Non | Confirmer l’absence de moniteurs, de véhicules et de candidats | Non : Champs de capacité collectés mais non publiés (écart 13) | — |

### O5 — Recommandations (4 indicateurs)

| ID | Indicateur | Données | Preuve (02) | Prévu (03) | À vérifier | Résultat | Preuve (04) |
| -- | ---------- | ------- | ----------- | ---------- | ---------- | -------- | ----------- |
| O5-01 | Nombre de déficits par territoire | D3 à D7 | B | Repli : sans la dimension risque | Dimensions calculables par préfecture ; risque « non déterminable » (R-10) | Repli : préfecture, 2022 ; réserve : recommandation C : vérification, pas investissement (R-17) | C |
| O5-02 | Rang de priorité | D3 à D7 | B | Repli : sans la dimension risque | Dimensions calculables par préfecture | Repli : préfecture, 2022 ; réserve : recommandation C (R-17) | C |
| O5-03 | Population concernée | D7, D13 | B | Cible | Population 2022 par préfecture | Cible : préfecture, 2022 | A |
| O5-04 | Écart à la cible | D3 à D7 | B | Repli : sans la dimension risque | Dimensions calculables par préfecture | Repli : préfecture, 2022 ; réserve : recommandation C (R-17) | C |

---

## 9. Décisions de périmètre

**Données retenues et exclues.** ✅ Ce sont celles du 03 (§3). Le 04 ne les change que sur preuve, et l’inscrit ici et au journal (§11).

| Changement | Raison | Décidé le |
| ---------- | ------ | --------- |
| Annuaire 2024 : utilisé aussi pour le parc, les permis et l’état du réseau (tableaux 39.2, 40.1 à 40.4), pas seulement pour les accidents | Il prolonge les séries jusqu’en 2024 et prouve que le parc est un flux (écarts 16 à 18) | 2026-10-04 |
| EHCVM : fichiers « welfare » (taille du ménage) et « ménages » (agrégat `moto`) lus pour deux contrôles, sans autre usage | Contrôles 4.5-04 et 4.5-05 ; seuls des agrégats sortent | 2026-10-04 |
| ✅ HDX : points d’étiquette des préfectures (`tgo_adminpoints`, dans le zip HDX déjà téléchargé) pour O4-08 | 9 préfectures sans chef-lieu (écart 19) [5-15] | 2026-10-04 |
| ✅ Nouvelle table compilée, `data/reference/correspondance_etat_trace.csv` : 2 noms proches et 4 axes, une raison et une source par ligne | Aucun identifiant commun entre l’état et le tracé ; 7 tronçons découpés ou numérotés autrement [5-10] | 2026-10-04 |
| ✅ PA-05 : âges minimaux pris au décret n° 2022-085/PR, au lieu des sources secondaires | Décret trouvé (écart 6) | 2026-10-04 |

**Règles de repli du 02 à confirmer :**

| Règle | Objet | Indicateurs | Résultat |
| ----- | ----- | ----------- | -------- |
| R-05 | Année de référence 2022 | Croisements territoriaux | Confirmée : routes et auto-écoles collectées en 2021-2022, population de 2022 ; état par tronçon de 2020, daté comme tel [4.2-05] |
| R-06 | Population de la même année que le numérateur | O1-04, O1-07, O2-02, O2-03, O4-03, O4-05 | Confirmée : recensements en 2010 et 2022 (A), projections de 2011 à 2021 (C) ; saut de +0,34 % en 2022 [4.4-07] |
| R-10 | Une valeur manquante n’est jamais un zéro | Tous | Appliquée : permis de 2013, cellules « - » du Livret 02, ménages sans section dans l’EHCVM [4.1-04, 4.5-05] |
| R-11 | Dénominateur du taux par véhicule | O1-05, O2-04 | Dernier recours : aucun stock publié, cumul des immatriculations sur la durée de vie PA-01, en C et en fourchette [4.4-01] |
| R-12 | Auto-écoles dont l’activité est inconnue | O4-04 à O4-08 | Appliquée : 132 auto-écoles agréées ou antennes agréées, activité non vérifiée (écart 13) [4.1-08] |
| R-14 | Un tronçon non évalué n’est pas en bon état | O3-01 à O3-03, O3-06 | Appliquée : les états de chaque tronçon évalué font son total [4.1-05] ; 3,2 % des routes nationales non évaluées, affichées comme telles [5-11] |
| R-15 | Tronçon à cheval sur deux territoires | O3-01 à O3-06, O4-01 à O4-03 | Appliquée : 89 tronçons à cheval, découpés par préfecture [4.3-07] |
| R-16 | Longueurs, surfaces et distances en UTM 31N | O4-01, O4-02, O4-08 | Appliquée aux longueurs du tracé, aux surfaces des 39 préfectures et aux distances de O4-08 [4.4-11, 5-01] |

---

## 10. Synthèse de faisabilité (mise à jour du 03 §4.2)

**Résultat** (`synthese_faisabilite.csv`, écrit par `faisabilite_04.py` à partir de `faisabilite_indicateurs.csv`, 2026-10-04). Le niveau de preuve d’un indicateur est le plus faible de ceux qu’il porte : un taux qui n’est en B qu’en 2010 et en 2022 compte en C.

| Objectif | Prévu au 03 : cible / repli / non | Confirmé au 04 | Preuve A / B / C | Écart avec le 03 |
| -------- | --------------------------------- | -------------- | ---------------- | ---------------- |
| O1 | 8 / 0 / 1 | 8 / 0 / 1 | 2 / 3 / 3 | Aucun en calculabilité. O1-04 et O1-07 passent en C (population projetée ; âges minimaux) ; O1-05 devient nécessaire (flux, écart 16) |
| O2 | 1 / 6 / 7 | 1 / 6 / 7 | 1 / 2 / 4 | Aucun en calculabilité. O2-04 passe en C (aucun stock publié) ; O2-09 en C ; accidents « constatés » (écart 15) |
| O3 | 2 / 4 / 1 | 6 / 1 / 0 | 0 / 1 / 6 | O3-01 à O3-03 et O3-06 passent à la préfecture grâce au rattachement au tracé, dont 4 axes par la table de correspondance ; O3-07 devient un repli national (écart 18) |
| O4 | 8 / 0 / 1 | 7 / 1 / 1 | 1 / 4 / 3 | O4-08 passe en repli : 9 préfectures sans chef-lieu (écart 19) |
| O5 | 1 / 3 / 0 | 1 / 3 / 0 | 1 / 0 / 3 | Aucun en calculabilité ; dimensions en C, donc recommandations de vérification (R-17) |
| **Ensemble** | **20 / 13 / 10** : 77 % calculables, 47 % à la maille cible | **23 / 11 / 9** : 79 % calculables, 53 % à la maille cible | **5 / 10 / 19** | Plus d’indicateurs à la maille cible, mais 19 des 34 indicateurs calculables sont en C |

**Indicateurs** (`faisabilite_indicateurs.csv`) :
- **à la maille cible (23)** : O1-01 à O1-07, O1-09 ; O2-04 ; O3-01 à O3-06 ; O4-01 à O4-07 ; O5-03 ;
- **avec repli (11)** : O2-01, O2-02, O2-03, O2-05, O2-06, O2-09 (national) ; O3-07 (national, en %) ; O4-08 (chef-lieu ou point d’étiquette) ; O5-01, O5-02, O5-04 (sans la dimension risque) ;
- **non calculables (9)** : O1-08 ; O2-07, O2-08, O2-10, O2-11, O2-12, O2-13, O2-14 ; O4-09.

**Limites restantes.**
- Les accidents sont nationaux. Aucun classement territorial du risque n’est possible.
- L’état du réseau date de 2020, avec une notation non documentée (C). Sur 4 axes autour de Lomé, il est réparti le long de l’axe, au prorata des km.
- L’activité des auto-écoles est inconnue (R-12).
- Aucun stock de véhicules n’est publié. Le parc est estimé en fourchette (C), et les motos possédées sont environ deux fois plus nombreuses que les deux-roues immatriculés (C).
- La population annuelle est projetée (C), sauf en 2010 et en 2022.

**Recommandations « données ».** Les trois demandes du 03 (§8) ✅ sont complétées par ce que le 04 a trouvé :
1. **Une base d’accidents par préfecture**, tenue par l’ONSR. Elle devrait aussi dire :
   - si l’accident est corporel ou seulement matériel ;
   - la définition du tué ;
   - le mois, l’âge, la catégorie de véhicule et la cause.
2. **L’ouverture des couches « Dégradations » et « Ponts »** du géoportail. S’y ajoutent :
   - la méthode de notation de l’état ;
   - un identifiant de tronçon commun à l’état du réseau et au tracé ;
   - un relevé par tronçon après 2020.
3. **La publication de l’activité des auto-écoles.** La campagne PRISE a collecté le personnel, l’activité, les horaires et les véhicules des auto-écoles, mais ne les publie pas.
4. **Nouveau : des libellés exacts sur le portail.** Il faudrait renommer :
   - le « parc automobile immatriculé » en « immatriculations de l’année » ;
   - les « accidents mortels /100 000 hab » en « accidents constatés pour 100 000 habitants » ;
   - les « premières mises en circulation » en « véhicules neufs » ;
   - dans l’état du réseau, la « RN4 » Lomé–Vogan–Anfoin en « RN34 ».

   Il faudrait aussi publier un stock de véhicules en circulation.

---

## 11. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Plan du 04** : adaptations comprises (frontière avec le 05, jointure D4 → D5, pas de rapport ydata pour l’EHCVM) | Tout le document | Équipe, 2026-10-04 |
| ✅ **Environnement** : `.venv` à la racine, versions figées dans `requirements.txt` | §2 | Équipe, 2026-10-04 |
| ✅ **Niveaux de preuve** des 130 variables utilisées, dont les projections de l’INSEED en C | §3 ; `scripts/profil_04.py` | Équipe, 2026-10-04 |
| ✅ **Stock ou flux** : le parc publié est un flux, les immatriculations de l’année ; O2-04 passe au cumul (R-11, C) | §4.4 [4.4-01 à 4.4-04] ; écart 16 | Équipe, 2026-10-04 |
| ✅ **« Accidents mortels /100 000 hab »** : accidents constatés rapportés à la population ; non repris, O2-03 recalculé (B) | §4.4 [4.4-06] | Équipe, 2026-10-04 |
| ✅ **EHCVM** : ligne absente = « non » si la section est remplie, « non renseigné » sinon ; parts pondérées par zone | §4.5 [4.5-05] ; §6 | Équipe, 2026-10-04 |
| ✅ **Écarts nouveaux** 14 à 16 et **favorables** 17 et 18, déclarés avant calcul (R-20) | §7 | Équipe, 2026-10-04 |
| ✅ **État du réseau rattaché au tracé** : 84 tronçons sur 84, 75 par le nom, 2 par un nom proche validé (NABLOUGOU et NABOULGOU, ALINMONDJI et ALIMONDJI), 7 par l’axe (RN1, RN2/3, RN34, RN4 autour de Lomé), confirmés par les longueurs ; table `data/reference/correspondance_etat_trace.csv` ; O3 par préfecture partout ; part non évaluée : 3,2 % | §5 [5-10, 5-11] ; écart 12 | Équipe, 2026-10-04 |
| ✅ **O4-08 depuis le point d’étiquette HDX** pour les 9 préfectures sans chef-lieu (écart 19), en C, ces préfectures signalées comme telles ; points dans `points_depart_o4_08.csv` | §5 [5-15] ; §7 ; §8 | Équipe, 2026-10-04 |
| ✅ **Synthèse** : 23 indicateurs à la maille cible, 11 avec repli, 9 non calculables ; 19 des 34 calculables en C | §10 | Équipe, 2026-10-04 |
| ✅ **Âges minimaux (PA-05)** : `ages_minimaux_permis.csv` mise au décret n° 2022-085/PR (art. 9 et 12) : E à 18 ans et non 21 ; A2 à 16 ans dans le libellé ; A gardé à 18 ans, les permis étant publiés sans sous-catégorie ; valables depuis août 2022, O1-07 reste en C | §7, écart 6 ; §9 | Équipe, 2026-10-04 |
