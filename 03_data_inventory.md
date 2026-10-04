# 03 — Data Inventory

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.3 — **Date :** 2026-10-04 — **Statut :** **figé** le 2026-10-04
**Sources :** `workspace/_PROJECT.txt` (ressources mises à jour), `02_decision_matrix.xlsx` (v1.1, figé), registre `data/raw/_SOURCES.csv`, recherches complémentaires des 3 et 4 octobre 2026 (§8) et leur validation (`workspace/validation.md`)

> L’inventaire **recense** : pour chaque besoin D1–D13 du 02, ce qui existe, où, sous quelle licence, à quelle maille et sur quelles années. Il télécharge ce qui est accessible, sans l’analyser. Profiler les fichiers, contrôler leur qualité et dire ce qui est calculable relève du 04.
>
> Le 02 est figé (R-20) : la disponibilité est consignée ici, pas dans le classeur. Les écarts avec le 02 sont listés au §5 ; ils seront déclarés, avec leur règle de repli, une fois confirmés par le 04.
>
> ✅ marque une décision validée ou un point tranché. Le journal des décisions est au §11.

---

## 1. Ce qu’il faut retenir

1. **Les accidents ne sont publiés qu’au niveau national, et aucune source territoriale homogène n’existe.** Le Togo n’a pas encore de base nationale d’accidents : l’Observatoire de la sécurité routière n’est pas en service. Les annuaires régionaux de l’INSEED couvrent 3 régions sur 5, de façon hétérogène, et ne sont pas retenus. C’est la limite majeure prévue par le 01 (§2.3) : l’objectif 5 ne peut pas croiser risque et territoire, et les recommandations s’organisent par levier.
2. **Face à l’énoncé, les données couvrent 93 % de ce qui est demandé ; face au 02, 77 % des indicateurs sont calculables, et 47 % à la maille visée** (§4). L’écart tient aux accidents nationaux.
3. **Les séries de mobilité sont longues mais nationales** : parc immatriculé par type de 1990 à 2022, motos comprises ; premières mises en circulation des 4 roues de 2000 à 2022 ; permis par catégorie de 2007 à 2022. Seul contexte par zone : l’usage de la moto et du moto-taxi par les ménages en 2021-2022 (EHCVM, D12).
4. **Le réseau et les auto-écoles sont fins, mais incomplets.** Ils viennent de la collecte nationale PRISE de 2021–2022. 799 tronçons classés sont géolocalisés, sans leur état. L’état n’existe que pour 2020, par tronçon nommé, sans géométrie ; la couche géolocalisée des dégradations existe au géoportail, mais n’est pas ouverte. 272 auto-écoles sont géolocalisées, sans activité ni capacité. ✅ Le référentiel des 39 préfectures, commun à toutes les sources, est arrêté (D8).
5. **La population est complète pour 2022 et annuelle au niveau national.** Le recensement 2022 descend jusqu’au canton, et jusqu’à la préfecture par âge, sexe et milieu. Les projections de l’INSEED donnent la population nationale de chaque année de 2011 à 2031. Il manque seulement la population par préfecture et par année : les taux territoriaux portent sur 2022.
6. **Trois jeux de l’énoncé n’ont pas de licence ouverte** : deux sont publiés en licence non ouverte, un sans licence précisée. Les documents PDF de l’INSEED n’ont pas de licence déclarée.
7. **Vingt-trois jeux de données ne figurent pas dans l’énoncé** (§3) : avec les 7 jeux de l’énoncé, ils forment les 30 jeux du registre (§9). Parmi eux, le profil OMS 2023 répartit les tués de 2021 par type d’usager : 60 % sont des usagers de deux et trois roues.

---

## 2. Bilan par besoin du 02

Statuts : **Disponible** (le besoin est couvert) · **Partiel** (le jeu existe mais manque de maille, d’années ou de variables) · **Manquant** (rien trouvé).

| Code | Besoin (02) | Objectifs | Statut | Fichiers | Maille réelle | Années | Licence | Bloquant |
| ---- | ----------- | --------- | ------ | -------- | ------------- | ------ | ------- | -------- |
| D1 | Immatriculations par catégorie | O1, O2 | Partiel | `parc_immatricule_par_type_1.csv`, `parc_immatricule_par_type_2.csv`, `transports_statistiques_cles.csv` | National | 1990–2022 | Non précisée ; non ouverte | Oui |
| D2 | Permis délivrés par catégorie | O1 | Partiel | `permis_par_categorie.csv` | National | 2007–2022 | Non ouverte | Oui |
| D3 | Accidents, blessés, tués | O2, O5 | Partiel | `transports_statistiques_cles.csv`, `accidents_police_gendarmerie.csv`, `accidents_bilan_police_gendarmerie.csv`, `annuaire_statistique_national_2024.pdf`, `oms_profil_securite_routiere_2023.pdf` | **National** | 2010–2024 | Non ouverte ; ouverte ; non déclarée ; CC BY-NC-SA 3.0 IGO | Oui |
| D4 | État du réseau | O3, O5 | Partiel | `etat_reseau_routier.csv` | Tronçon nommé, sans géométrie | 2020 | Ouverte | Oui |
| D5 | Tracé du réseau classé | O2, O3, O4, O5 | Disponible | `routes_classees.csv` (+ métadonnées), `densite_reseau_routier.csv`, `geoportail_catalogue.json` | Tronçon géolocalisé, rattaché à la préfecture | Collecte PRISE 2021–2022 | Ouverte | Oui |
| D6 | Auto-écoles | O4, O5 | Partiel | `auto_ecoles.csv` (+ métadonnées), `auto_ecoles_vehicules_metadonnees.csv`, `geoportail_catalogue.json` | Point, rattaché à la préfecture | Collecte PRISE 2021–2022 | Ouverte | Oui |
| D7 | Population | O1, O2, O4, O5 | Partiel | `rgph_2022_population.csv`, `rgph5_livret02_age_milieu_prefecture.pdf`, `projections_demographiques_2011_2031.csv`, `population_region_sexe_2010.csv`, `wpp2024_population_age_simple_togo.csv` | Préfecture en 2022 (âge × sexe × milieu) ; national chaque année | 2022 ; 1990–2031 (national) | Ouverte ; non déclarée ; CC BY 3.0 IGO | Oui |
| D8 | Référentiel administratif | O4 ; référentiel de toutes les cartes (R-01) | Disponible | `limites_administratives_hdx.geojson.zip`, `limites_administratives_hdx.xlsx`, `data/reference/referentiel_prefectures.csv` | 39 préfectures (référentiel) ; 5 régions, 40 unités HDX de niveau 2 ramenées à 39, 373 de niveau 3 | Découpage de 2022 ; limites HDX valides depuis 2021 | CC BY-IGO | Oui |
| D9 | Benchmark externe | O2 ; repère (SE-03) | Disponible | `oms_tues_pour_100000.json`, `oms_profil_securite_routiere_2023.pdf` | National : Togo, Bénin, Ghana, Burkina Faso | 2021 | CC BY-NC-SA 3.0 IGO | Non |
| D10 | Comptages de trafic | O2, O3 ; contexte | Partiel | `transports_statistiques_cles.csv` | National, pas par tronçon | 2014–2022 | Non ouverte | Non |
| D11 | Chronologie des réformes | O1, O2 ; contexte | Partiel (table compilée) | `data/reference/chronologie_reformes.csv`, `oms_profil_securite_routiere_2023.pdf` | National | 2013–2026 | Sources citées ligne à ligne | Non |
| D12 | Enquête sur les déplacements | O1, O2 ; contexte | Partiel | `ehcvm_2021_2022_csv.zip`, `dhs_possession_moto_velo_region.json` | 6 zones (EHCVM) ; région, Lomé à part (DHS) | 2021-2022 ; 1998, 2013, 2017 | Conditions de la Banque mondiale, sans redistribution ; conditions du programme DHS | Non |
| D13 | Lieux candidats et grille de population | O4, O5 | Disponible | `limites_administratives_hdx.xlsx` (31 chefs-lieux, 419 localités) ; grille WorldPop recensée, non téléchargée | Point ; grille de 100 m | 2020 | CC BY-IGO ; CC BY 4.0 | Non |

Les fichiers sont dans `data/raw/`, sauf ceux de `data/reference/`. Licences : « ouverte » et « non ouverte » traduisent les codes `other-open` et `other-closed` du portail ; le détail par fichier est dans le registre.

### Ce que contient chaque jeu, et ce qui lui manque par rapport au 02

**D1 — Immatriculations.**
- Présent : parc immatriculé par type (voitures, camionnettes, autocars, camions, semi-remorques, tracteurs, 2 roues et assimilées, total) de 1990 à 2022 ; même indicateur de 2013 à 2019, avec les 2 roues par cylindrée ; dans les statistiques clés, premières mises en circulation des 4 roues (2000–2022) et 2 roues immatriculées (2014–2022).
- Manque : le mois ; le territoire ; les premières immatriculations des 2 roues avant 2014.
- Contrôle externe : le profil OMS 2023 compte 93 944 véhicules immatriculés en 2021, dont 65 363 deux et trois roues. Il servira à trancher stock ou flux (§7).

**D2 — Permis.**
- Présent : permis délivrés « aux examens », par catégorie A à F et au total. Tous les candidats passent par une auto-école agréée (service-public.gouv.tg). Âges minimaux par catégorie dans `data/reference/ages_minimaux_permis.csv` : A et B 18 ans, C, D et E 21 ans, F 18 ans par défaut ; sources secondaires, étiquetées C.
- Manque : le mois, le sexe, l’âge des titulaires, le territoire ; le texte officiel des âges (décret n° 2022-085/PR).

**D3 — Accidents.**
- Présent : nombre d’accidents, de morts et de blessés, plus un indicateur « accidents mortels / 100 000 hab. ». Trois sources nationales qui se recoupent : statistiques clés (2010–2022), police et gendarmerie (2014–2022), bilan police et gendarmerie (2014–2019). L’annuaire national 2024 prolonge la série jusqu’en 2024. Le profil OMS 2023 répartit les 680 tués déclarés en 2021 par type d’usager : 4 roues 11 %, 2 et 3 roues 60 %, piétons 23 %, cyclistes 0 %, autres 6 %. Il estime aussi les tués à 1 961 la même année.
- Manque : le territoire, le mois, l’heure, la gravité des blessures, la catégorie de véhicule, le statut d’immatriculation, le sexe et l’âge des victimes et des conducteurs, la cause déclarée. Les annuaires régionaux de l’INSEED ne comblent pas ce manque (§3.3).

**D4 — État du réseau.**
- Présent : longueurs en km par état (bon, moyen, mauvais, travaux, total), pour quatre types (routes revêtues, voiries revêtues, routes en terre, voiries en terre), sur 88 libellés de tronçon, lignes de total comprises.
- Manque : la géométrie, la préfecture, l’identifiant commun avec D5, la méthode de notation (introuvable), tout relevé autre que 2020. La couche « Routes – Dégradations » de la collecte 2021–2022 existe au géoportail, mais n’est pas ouverte.

**D5 — Tracé du réseau classé.**
- Présent : 799 tronçons géolocalisés (199 noms de route), collectés en 2021–2022, avec région, préfecture (38 distinctes), commune, canton, type (nationale revêtue, nationale non revêtue, voirie urbaine, piste rurale), revêtement et nombre de voies. Densité du réseau par type en 2020, au niveau national.
- Manque : l’état, et un identifiant commun avec D4.

**D6 — Auto-écoles.**
- Présent : 272 établissements géolocalisés, collectés en 2021–2022, présents dans 24 préfectures, dont 224 dans la région Maritime. Statut d’agrément : 85 agréées, 47 antennes agréées, 138 non agréées, 2 « néant ». Le géoportail compte officiellement les « auto-écoles et antennes agréées », soit 132.
- Manque : la date d’agrément, l’activité et la capacité. Le jeu « Auto-écoles – Véhicules » ne publie que la description de ses champs.

**D7 — Population.**
- Présent : population résidente 2022, de la nation au canton (745 unités dans une seule colonne) ; dans ce fichier, « Maritime » signifie la Maritime hors Grand Lomé. Livret 02 du RGPH-5 : population 2022 par groupe d’âges quinquennal, sexe et milieu (urbain, rural), pour le pays, les régions, le Grand Lomé et les 39 préfectures. Projections de l’INSEED : population nationale par groupe d’âges et sexe, chaque année de 2011 à 2031. Recensement de 2010 par région et sexe. WPP 2024 de l’ONU : population nationale par âge simple et sexe, de 1990 à 2024 ; c’est la seule source annuelle avant 2010. Son niveau dépasse celui de l’INSEED de 8,7 % en 2010 et de 12,7 % en 2022 : on n’en retient que la structure par âge et l’évolution (§5).
- Manque : la population par préfecture et par année.

✅ **D8 — Référentiel des préfectures.** Décision du 2026-10-04 : la préfecture, brique commune de tous les croisements (R-01), suit un référentiel unique de **39 préfectures**. Il est construit par `scripts/referentiel_prefectures.py` dans `data/reference/referentiel_prefectures.csv`.
- **Pivot** : les 39 préfectures du Livret 02 du RGPH-5, soit le découpage de 2022, celui qu’attend le 01. Le nom de référence est l’orthographe de la collecte nationale de 2021–2022 ; le code est celui de HDX (pcode), qui porte les géométries.
- **Correspondance** : chaque ligne donne le nom exact dans chaque source, la région et la zone (Grand Lomé 2, Maritime hors Grand Lomé 6, Plateaux 12, Centrale 5, Kara 7, Savanes 7). 37 préfectures sont présentes partout ; les noms ne diffèrent que par les accents.
- **Trois règles pour HDX**, dont le découpage date de 2021 : « Lome Commune » (TG0305) est fusionnée avec le Golfe (TG0303) ; « Plaine du Mo » (TG0102) est l’ancien nom de Mô ; « Naki-Ouest » (TG0518) est rattachée à Kpendjal-Ouest par élimination, mais son libellé est douteux et sera vérifié sur la carte en 04.
- **Écarts normaux** : les routes classées n’ont aucun tronçon à Mô (à vérifier en 04) ; 15 préfectures n’ont aucune auto-école recensée. Dans le recensement CSV, la ligne d’Avé est libellée « TOTOAL AVE » (coquille) et 5 préfectures ont un homonyme parmi les communes ou les cantons.
- **Contrôle** : le script s’arrête si un nom d’une source ne trouve pas sa préfecture, ou si une préfecture manque dans le Livret 02, le recensement ou HDX.

**D11 — Chronologie.** Dix dates sourcées, de la loi de 2013 portant code de la route à l’entrée en vigueur de la Charte africaine de la sécurité routière en 2026, dont le permis moto obligatoire et la campagne d’immatriculation des motos de 2019. Aucune réforme datée n’a été trouvée avant 2013, alors que le 02 attend toute la période de D1 et D2, soit depuis 1990 : d’où le statut « Partiel » (§5).

**D12 — Déplacements.** Aucune enquête sur les déplacements n’existe : l’OMS note l’absence de système national de données sur les déplacements. Deux enquêtes auprès des ménages en tiennent lieu, en contexte et étiquetées C.
- **EHCVM 2021-2022** (INSEED, 6 462 ménages) : représentative des 6 zones, pas des préfectures. Trois mesures, par zone seulement : la part des ménages qui possèdent une moto (et une voiture, un vélo) ; la part de ceux qui ont payé un moto-taxi dans les 7 derniers jours ; la part de ceux qui ont acheté du carburant pour moto dans les 7 derniers jours.
- **DHS** (1998, 2013 ; enquête paludisme 2017) : la part des ménages qui possèdent une moto ou un vélo, par région. En 2017, la part de la moto va de 28 % (Maritime hors Lomé) à 42 % (Lomé, Savanes). Elle sert à la tendance ; les deux enquêtes ne sont pas mises bout à bout.
- Manque : les parts modales et le nombre de déplacements, qu’attend le 02. Une dépense déclarée dit qu’un mode est utilisé, pas combien (§5).

---

## 3. Sources trouvées hors de l’énoncé

Le registre compte 23 jeux absents de l’énoncé : 18 servent les besoins du 02 (§3.1), 5 sont hors 02 (§3.2).

### 3.1 Sources retenues pour les besoins du 02

| Source | Producteur | Apport | Statut |
| ------ | ---------- | ------- | ------ |
| Accidents constatés par la police et la gendarmerie (2014–2022) | INSEED | D3 : deuxième série nationale | Téléchargé |
| Bilan des accidents constatés par la police et la gendarmerie (2014–2019) | INSEED | D3 : troisième série nationale | Téléchargé |
| Annuaire statistique national 2024 (PDF) | INSEED | D3 : accidents, morts et blessés 2023–2024 | Téléchargé |
| Rapport mondial sur la sécurité routière 2023, profil du Togo (PDF) | OMS | D1 : contrôle stock ou flux du parc (véhicules immatriculés en 2021) ; D3 : tués par type d’usager en 2021 (O2-09) ; D9 : même taux estimé que le fichier RS_198, qui reste la source du repère SE-03 ; D11 : état des lois | Téléchargé |
| Catalogue du géoportail national (JSON) | Ministère de l’Économie numérique | D5, D6 : collecte PRISE 2021–2022 et règle de comptage des auto-écoles ; D4 : couche des dégradations non ouverte | Téléchargé |
| Auto-écoles – Véhicules | Ministère des Transports | D6 : description des champs seulement, sans données | Téléchargé |
| Densité du réseau routier par type de route (2020) | Ministère des Travaux publics | O4-02 au niveau national | Téléchargé |
| Réseau routier complet (138 Mo) | Ministère des Transports | Réseau non classé, hors périmètre de O4 | Recensé |
| Routes, pistes rurales et statut de route classée (110 Mo) | Ministère des Transports | Pistes non classées, « à confirmer » au périmètre (01 §6) | Recensé |
| RGPH-5, Livret 02 (PDF) | INSEED | D7 : population 2022 par âge, sexe et milieu jusqu’à la préfecture ; PA-03 | Téléchargé |
| Projections démographiques 2011–2031 | INSEED | D7 : population nationale annuelle par âge et sexe | Téléchargé |
| Population résidente par région et sexe, 2010 | INSEED | D7 : année 2010 | Téléchargé |
| World Population Prospects 2024, âges simples, Togo 1990–2024 (API) | Nations unies | D7 : population nationale avant 2010 (O1-04 sur le parc 1990–2022) ; découpage des groupes d’âges pour PA-05 | Téléchargé |
| Limites administratives (COD-AB) | OCHA / HDX, d’après GAUL | D8, et D13 (chefs-lieux, localités) | Téléchargé |
| Taux de tués estimé (indicateur RS_198) | OMS | D9 | Téléchargé |
| Possession de motos et de vélos par région (DHS 1998, 2013 ; MIS 2017) | The DHS Program | D12 : tendance de la possession, 1998–2017 | Téléchargé |
| Enquête harmonisée sur les conditions de vie des ménages 2021-2022 (EHCVM-2), catalogue de microdonnées de la Banque mondiale | INSEED, avec la Banque mondiale et l’UEMOA | D12 : possession de motos, recours au moto-taxi et achat de carburant pour moto, par zone | Téléchargé, non versionné |
| Grille de population 2020 | WorldPop | D13, pour O4-08 | Recensé |

Dans l’énoncé, les « URL Data 2 » des routes classées et des auto-écoles pointent vers des **fichiers de métadonnées** (la liste des champs), pas vers des données. Celle de l’état du réseau est le lien stable du même fichier que la « URL Data ». Au total, les 16 URL de données de l’énoncé, liens stables compris, donnent 10 fichiers, tous au registre.

### 3.2 Sources hors 02, en contexte seulement

✅ Elles n’alimentent aucun indicateur, aucun profil ni aucun classement. Leur usage est un écart déclaré (R-20).

| Source | Producteur | Usage | Statut |
| ------ | ---------- | ----- | ------ |
| Longueur de route entretenue et taux de couverture des besoins d’entretien (2016–2019) | INSEED | Annexe nationale, contexte de O3 | Téléchargé |
| Panneaux de signalisation, ralentisseurs, passages piétons, feux tricolores (4 jeux, collecte 2021–2022) | Ministère des Transports | Couche facultative sur la carte de O5, désactivée par défaut, libellée « non utilisée dans les indicateurs » | Téléchargé |

✅ **Traitement en 04.** Ces sources ne sont pas profilées. Avant tout affichage, le 04 fait seulement un contrôle : nombre de points, coordonnées dans le Togo et rattachement aux 39 préfectures pour les équipements ; années et unité pour la longueur entretenue. Si le contrôle échoue, ou si le tableau de bord manque de place, elles sont seulement citées en page Méthodologie, comme « données disponibles non utilisées ». Le fichier des panneaux sert déjà au référentiel des préfectures (D8), pour l’orthographe des noms ; ses 39 préfectures y sont toutes retrouvées.

Deux tables compilées à la main complètent l’inventaire, dans `data/reference/` : `chronologie_reformes.csv` (D11) et `ages_minimaux_permis.csv` (PA-05). Chaque ligne cite sa source.

### 3.3 Sources recensées, non retenues

✅ Ces choix sont validés (§11).

| Source | Raison |
| ------ | ------ |
| Annuaires statistiques régionaux de l’INSEED (accidents) | Hétérogènes : 3 régions sur 5, constatés par la gendarmerie seule ou avec la police, variables différentes, Grand Lomé absent, qualité douteuse par endroits. Comparer ces chiffres produirait un classement faux |
| Couches « Dégradations », « Ponts », « Gendarmeries » du géoportail | Non ouvertes : objet d’une recommandation « données » (§8) |
| Parc des deux-roues immatriculés par ville (2014–2019) | Cinq villes, sans Lomé ; lieu d’immatriculation ≠ lieu d’usage |
| Charges de sinistres automobiles (2014–2022) | Coût assuré, pas coût social : trompeur ; à citer au plus en méthodologie |
| WorldPop 2015–2030 (population annuelle modélisée) | L’année 2022 suffit pour le territorial ; option de repli si le 04 en montre le besoin |
| HeiGIT (revêtement des axes principaux, 2020–2024) | Mesure le revêtement, pas l’état |
| Page « Données relatives au transport » du portail (gares, parkings, sociétés de transport…) | Aucun besoin D1–D13 |
| Projections 2011–2021, population 2014–2019 par sexe, estimations HDX 2021 | Redondantes ou dépassées |
| Documents de la BAD et du SSATP | Inaccessibles automatiquement |
| EHCVM 2018-2019, MICS 2017, recensement 2010 (échantillon IPUMS) | Plus anciens que l’EHCVM 2021-2022, ou redondants avec la DHS ; IPUMS : accès sur dossier |
| Afrobaromètre 2022 | 1 200 personnes ; état de la route observé et avis sur l’entretien, non comparables au relevé de 2020. Cité en méthodologie parmi les données disponibles non utilisées |
| ANID, ARCEP, autres jeux HDX et Banque mondiale, autres études du catalogue de microdonnées | Hors sujet |

---

## 4. Couverture des objectifs

Avec les données recensées, chaque objectif de l’énoncé peut-il être traité ? Deux lectures : face à ce que demande l’énoncé (§4.1), puis face aux 43 indicateurs du 02 (§4.2). Les taux reposent sur la structure des fichiers ; le 04 les confirmera.

- **Face à l’énoncé, les données couvrent 93 % de ce qui est demandé** (83 % avec les seuls jeux de l’énoncé). Aucune demande n’est entièrement découverte.
- **Face au 02, 77 % des indicateurs sont calculables, et 47 % à la maille visée.** Les 30 indicateurs « Socle » sont tous calculables : 18 à la maille cible, 12 en repli. Les 10 indicateurs non calculables sont tous des « Si données ».
- **L’écart entre les deux lectures vient des accidents nationaux.** L’énoncé ne demande pas d’accidents par territoire ; la décision du 01, qui croise risque et desserte, en a besoin. Ce qui reste territorial, c’est l’offre : l’objectif 5 pourra dire où entretenir et où former, mais pas, en l’état, où le risque est le plus élevé.

### 4.1 Face à l’énoncé

Chaque objectif de `workspace/_PROJECT.txt` est découpé en ses demandes explicites. **Énoncé seul** : les 7 jeux fournis. **+ complémentaires** : avec les sources du §3.1.

| Obj. | Demande de l’énoncé | Énoncé seul | + complémentaires | Données et limites |
| ---- | ------------------- | ----------- | ----------------- | ------------------ |
| O1 | Évolution des véhicules immatriculés : voitures, motos, poids lourds | Couvert | Couvert | Parc par type, 1990–2022 ; stock ou flux à trancher en 04 |
| O1 | Évolution des permis délivrés, par catégorie | Couvert | Couvert | Catégories A à F, 2007–2022 |
| O2 | Accidents, blessés et morts | Couvert | Couvert | National, 2010–2024 ; les deux séries police et gendarmerie servent au recoupement |
| O2 | Rapportés à la population | Partiel | Couvert | Seul : population de 2022 seulement. Avec les projections : population de chaque année |
| O2 | Rapportés au nombre de véhicules | Couvert | Couvert | Parc immatriculé publié |
| O3 | Bon état, état moyen, mauvais état, travaux en cours | Couvert | Couvert | Relevé de 2020 seulement |
| O3 | Par tronçon | Couvert | Couvert | 84 tronçons nommés, sans tracé : tableau ; carte si les tronçons se rattachent aux routes classées (04) |
| O3 | Par région | Partiel | Partiel | Code de région dans le libellé de 64 tronçons ; 20 à rattacher en 04 |
| O4 | Réseau classé, cartographié par région et préfecture | Partiel | Couvert | Tracé et préfecture dans les routes classées ; les limites HDX apportent le fond de carte et les surfaces |
| O4 | Auto-écoles, cartographiées par région et préfecture | Partiel | Couvert | 272 points rattachés à leur préfecture ; fond de carte HDX |
| O4 | Rapportés à la population | Couvert | Couvert | Recensement 2022 par préfecture ; référentiel des 39 préfectures arrêté (D8) |
| O5 | Repérer les régions les moins bien desservies | Couvert | Couvert | Desserte : routes et auto-écoles par habitant, par préfecture |
| O5 | Recommandations ciblées : formation des conducteurs | Couvert | Couvert | Par préfecture |
| O5 | Recommandations ciblées : entretien du réseau | Couvert | Couvert | Par tronçon et par région, état de 2020 |
| O5 | Recommandations ciblées : sécurité routière | Partiel | Partiel | Ciblage par la desserte possible, pas par le risque observé : accidents nationaux |

Pour atteindre 100 %, il reste le rattachement des 20 tronçons sans code de région (04) pour O3, et les accidents par territoire pour O5. Ces derniers n’existent pas aujourd’hui (§8).

### 4.2 Synthèse par objectif

**Taux face à l’énoncé** = (demandes couvertes + ½ × demandes partielles) / demandes. **Indicateurs du 02**, sources complémentaires comprises : *cible* = calculable comme le 02 le prévoit ; *repli* = calculable avec une règle de repli (maille plus large, dénominateur approché, année unique) ; *non* = non calculable.

| Objectif | Énoncé seul | Énoncé + complémentaires | Indicateurs du 02 : cible / repli / non | Calculables | À la maille cible | Ce qui limite |
| -------- | ----------- | ------------------------ | --------------------------------------- | ----------- | ----------------- | ------------- |
| O1 Immatriculations et permis | 100 % | 100 % | 8 / 0 / 1 | 89 % | 89 % | Non : O1-08 (permis sans sexe ni âge) |
| O2 Sécurité routière | 83 % | 100 % | 1 / 6 / 7 | 50 % | 7 % | Repli : O2-01 à O2-03, O2-05, O2-06 (national au lieu de la préfecture) ; O2-09 (type d’usager, 2021, OMS). Non : O2-07, O2-08, O2-10 à O2-14 (accidents sans territoire, catégorie, mois ni cause) |
| O3 État du réseau | 83 % | 83 % | 2 / 4 / 1 | 86 % | 29 % | Repli : O3-01 à O3-03, O3-06 (région au lieu de la préfecture, sauf rattachement au tracé en 04). Non : O3-07 (un seul relevé) |
| O4 Réseau et auto-écoles | 67 % | 100 % | 8 / 0 / 1 | 89 % | 89 % | Non : O4-09 (capacité des auto-écoles). Sans les sources complémentaires, O4-02 (surfaces HDX) et O4-08 (grille WorldPop) ne sont pas calculables : 67 % |
| O5 Recommandations | 88 % | 88 % | 1 / 3 / 0 | 100 % | 25 % | Repli : O5-01, O5-02, O5-04, sans la dimension risque, « non déterminable » (R-10) ; réseau lu par région |
| **Ensemble** | **83 %** | **93 %** | **20 / 13 / 10** | **77 %** | **47 %** | Sans les sources complémentaires : 70 % calculables, 37 % à la maille cible |

---

## 5. Écarts prévisibles avec le 02

Ces écarts viennent de la structure des fichiers : une maille ou une variable absente. Le 04 les confirmera ; ils seront alors déclarés avec leur règle de repli.

✅ Un changement de statut dans le 03 n’est pas un écart : le 02 fixe le besoin et son rôle, pas sa disponibilité. Ainsi, D11 et D12, « Manquant » dans la v1.0 du 03, sont désormais « Partiel » sans que le 02 change (R-20), et leur rôle reste « Contexte ». Un écart naît quand une source s’éloigne de ce que le 02 attend : contenu, maille ou période.

| Écart | Indicateurs et hypothèses touchés | Repli |
| ----- | --------------------------------- | ----- |
| **Accidents nationaux seulement** ; aucune source territoriale homogène | O2-01, O2-02, O2-03, O2-05, O2-06, O2-12 par territoire ; H3, H4, H7, H9, H11 ; dimension risque de O5-01 et O5-02 | Pas de classement territorial du risque ; recommandations par levier (05_Priorisation, « Unité de classement »). Sans O2-02 territorial, les profils P1 à P4 ne s’appliquent pas : seul P5 s’applique (05_Priorisation, « Combinaison des profils ») |
| Accidents sans mois, heure, âge, catégorie de véhicule, immatriculation, cause | O2-07, O2-08, O2-10, O2-11, O2-13, O2-14 ; H5, H10, H12 ; H2 côté véhicules | Indicateurs « Si données » non calculés ; hypothèses non testables, écart déclaré |
| Victimes connues seulement par type d’usager, pour 2021 (OMS) | O2-09 ; H2 côté victimes | ✅ Écart favorable : O2-09 calculé en repli (national, 2021, sans sexe ni âge), étiqueté ; H2 testé côté victimes pour 2021 |
| Tués estimés par l’OMS (1 961 en 2021, contre 680 déclarés) | O2-01, O2-02 | ✅ Repère seulement (SE-03), jamais une correction des tués déclarés ; l’écart illustre la sous-déclaration |
| Permis sans sexe, âge, territoire, mois | O1-08 | Non calculé, écart déclaré |
| Âges minimaux tirés de sources secondaires | O1-07 (PA-05) | ✅ Étiquetés C. Les groupes d’âges quinquennaux sont découpés avec les âges simples de WPP ; à défaut, répartition uniforme (2/5 des 15–19 ans pour 18 ans et plus) |
| Population annuelle avant 2010 : aucune série de l’INSEED ; WPP plus élevé que l’INSEED de 9 à 13 % | O1-04 (1990–2009) ; O1-07 (2007–2009) | ✅ Population reconstituée à partir du recensement 2010, en lui appliquant les taux de croissance annuels de WPP (pas de rupture de niveau en 2010). Années 1990–2009 étiquetées C ; sur la courbe, bande grisée « population modélisée (WPP) » |
| Population par préfecture pour 2022 seulement | Taux territoriaux hors 2022 | Année de référence 2022 (R-05) ; aucun taux territorial annuel |
| Mobilité nationale seulement | Dimension mobilité du classement | Déjà prévu : mobilité affichée à part (05_Priorisation, « Dimensions ») ; usage de la moto par zone (EHCVM, D12) en contexte |
| Chronologie (D11) sans réforme datée avant 2013 ; le 02 attend toute la période de D1 et D2, depuis 1990 | Aucun indicateur ; lecture des ruptures de O1 avant 2013 | Annotations à partir de 2013 seulement ; une rupture antérieure est montrée sans annotation |
| Aucune enquête sur les déplacements (D12) : des enquêtes auprès des ménages remplacent les parts modales | Aucun indicateur ; H2, pour l’usage réel de la moto | ✅ Par zone, 2021-2022 (EHCVM) : possession, recours au moto-taxi, achat de carburant pour moto, étiquetés C ; jamais par préfecture. Une dépense dit qu’un mode est utilisé, pas combien de déplacements. DHS pour la tendance de la possession, 1998–2017 |
| État du réseau : un seul relevé, sans géométrie ; couche des dégradations non ouverte | O3-07 ; O3-02 par préfecture | O3-07 non calculé. O3-02 : rattacher chaque tronçon nommé à sa route géolocalisée (04) ; sinon lecture par type de route et par région |
| Auto-écoles sans activité ni capacité | O4-04, O4-05 ; O4-09 | ✅ On compte les agréées et les antennes agréées (règle officielle du géoportail) ; R-12 : étiquetées C, car l’activité est inconnue. O4-09 non calculé |

**Un écart favorable possible** : si le 04 confirme que `parc_immatricule_par_type_1.csv` est bien un stock, le taux par véhicule utilisera le parc immatriculé publié (preuve B) plutôt que le cumul des immatriculations (preuve C, PA-01) (R-11).

**Deux sources sont utilisées hors du 02**, en contexte seulement (§3.2) : la longueur de route entretenue, et les équipements de sécurité routière. Elles sont déclarées comme écart (R-20).

---

## 6. Réponses aux questions ouvertes du 01 (§9)

| N° | Question | Réponse | État |
| -- | -------- | ------- | ---- |
| 1 | Quels jeux, sur quelles années ? | Voir §2 | ✅ Répondu |
| 2 | Immatriculations et permis par mois ? Permis par sexe, âge, région ? Première délivrance ou renouvellement ? | Non, séries annuelles et nationales ; confirmé par les recherches. « Délivrés aux examens » laisse penser à des premières délivrances | Partiel : à confirmer en 04 |
| 3 | Le parc est-il publié ? | Un « parc automobile immatriculé par type » est publié de 1990 à 2022. Stock ou flux : à trancher en 04, notamment avec les 93 944 véhicules immatriculés en 2021 selon l’OMS, dont 65 363 deux et trois roues | Partiel : à confirmer en 04 |
| 4 | Nomenclature des permis ? | A moto, B voiture légère, C poids lourd, D transport en commun, E semi-remorque, F voiture spéciale. Âges minimaux : A et B 18 ans (A1 jusqu’à 50 cm³ : 14 ans depuis 2022), C, D et E 21 ans, F 18 ans par défaut | ✅ Répondu (sources secondaires, C) |
| 5 | Accidents ventilés par territoire, mois, profil ? | Non : national et annuel. Il n’existe pas de base nationale d’accidents. Seule la répartition des tués de 2021 par type d’usager est connue (OMS) | ✅ Répondu |
| 6 | Les 7 500 accidents de 2022 sont-ils corporels ? Définition du décès ? | Les chiffres existent ; la comparaison relève de S3 | Ouvert : 04 |
| 7 | Réseau : routes en terre incluses ? Types distingués ? Date et méthode des relevés ? | Oui, le réseau classé inclut terre, gravier et pavé. Types : nationale revêtue ou non, voirie urbaine, piste rurale. Tracé collecté en 2021–2022 ; état relevé en 2020, méthode non documentée et introuvable | ✅ Répondu |
| 8 | Auto-écoles : liste officielle, agrément, géolocalisation, activité, capacité ? | Liste collectée en 2021–2022, avec statut d’agrément, sans date d’agrément. Toutes géolocalisées. Le décompte officiel retient les agréées et les antennes agréées. Activité et capacité non publiées | ✅ Répondu |
| 9 | La Maritime inclut-elle le Grand Lomé ? | Recensement : non (Maritime hors Grand Lomé ; Golfe et Agoè-Nyivé à part). Routes et auto-écoles : oui au niveau région, mais la préfecture permet de séparer. Accidents : sans objet (national) | ✅ Répondu |
| 10 | Grille de notation du jury ? | Inconnue | Ouvert |

---

## 7. Observations à vérifier en 04

Relevées en lisant les en-têtes et les libellés, sans analyse du contenu.

- **Parc immatriculé** : stock ou flux ? À comparer avec les 93 944 véhicules immatriculés en 2021 selon l’OMS. Le portail annonce une couverture 2013–2019 alors que le premier fichier couvre 1990–2022. Libellé « Voitues ». Les deux fichiers se recoupent sur 2013–2019 avec des catégories différentes.
- **Permis A** : les sous-catégories A1 à A3 introduites en 2022 se reflètent-elles dans la série ? Les ruptures de 2019 (permis moto obligatoire, campagne d’immatriculation des motos) sont attendues ; elles seront annotées, sans lecture causale.
- **Statistiques clés** : l’indicateur « Accidents mortels /100.000 hab » parle-t-il d’accidents ou de morts ? Sur quelle population ?
- **Accidents** : trois séries nationales se recoupent sur 2014–2019, et l’annuaire 2024 sur 2020–2022 ; leur cohérence est à vérifier.
- **État du réseau** : des lignes de total sont mêlées aux tronçons (risque de double compte). Le code de région semble inclus dans le nom du tronçon (TGRPRR, TGRCRR, TGRKRR, TGRSRR, TGRMRT), à décoder.
- **Recensement** : cinq niveaux dans une seule colonne, sans code de niveau ; 13 libellés en double (par exemple CINKASSE, préfecture et canton) ; la préfecture d’Avé est libellée « TOTOAL AVE ». Le référentiel (D8) donne le libellé exact de chaque préfecture.
- **Livret 02 du RGPH-5** : extraire par script ses 47 tableaux (PDF), puis vérifier que les préfectures somment aux régions et au pays, et que les totaux correspondent au fichier du recensement.
- **Projections** : écart de 0,3 % avec le recensement en 2022 (8 068 000 contre 8 095 498), à documenter. Le fichier de 2010 porte le libellé erroné « population résidente en 2022 ».
- ✅ **WPP** : tranché. La série de référence des taux nationaux est celle de l’INSEED (recensements 2010 et 2022, projections 2011–2031). WPP sert seulement aux parts par âge et aux taux de croissance avant 2010. Constat à documenter : WPP dépasse l’INSEED de 8,7 % en 2010 et de 12,7 % en 2022 ; ses chiffres sont des estimations interpolées jusqu’en 2010, puis des projections, car WPP 2024 n’intègre pas encore le recensement de 2022. Retenir la variante « Median » (17 variantes publiées pour 2024).
- **Âges minimaux** : tenter une dernière fois de trouver le décret n° 2022-085/PR ; s’il est trouvé, PA-05 passe de C à A.
- ✅ **Référentiel des préfectures** : tranché, 39 préfectures (D8). Restent trois tâches pour le 04 : fusionner les polygones TG0303 et TG0305 pour le Golfe ; vérifier sur la carte que les routes et les équipements de Kpendjal-Ouest tombent dans TG0518 (« Naki-Ouest ») ; dire si l’absence de Mô dans les routes classées est un vrai vide ou un défaut de rattachement.
- **EHCVM** : ne lire que les fichiers utiles (couverture du questionnaire, dépenses des 7 derniers jours, biens durables, pondérations) ; calculer des parts pondérées par zone. Les codes de préfecture suivent l’ancien découpage (5 préfectures dans les Savanes, Lomé en arrondissements) et ne sont pas utilisés.
- **Géométries** : coordonnées en degrés, à reprojeter en UTM 31N (R-16).
- **Auto-écoles** : 163 adresses « Nsp », mais toutes géolocalisées. La moitié des établissements sont « non agréés », donc hors du décompte officiel.

---

## 8. Recherches complémentaires

**Méthode.** Les recherches des 3 et 4 octobre 2026 ont porté sur :
- le portail entier : ses 42 organisations, et 9 mots-clés. La recherche par mots-clés ne suffit pas seule : elle ne trouve que les mots des titres ;
- le site de l’INSEED (annuaires, livrets du RGPH-5) et le géoportail national ;
- l’OMS, la Banque mondiale, l’Union africaine, les enquêtes DHS, HDX et la presse ;
- le catalogue de microdonnées de la Banque mondiale : ses 84 études sur le Togo, avec la liste des variables des enquêtes candidates.

Leurs résultats ont été validés le 2026-10-04 (`workspace/validation.md`).

| N° | Besoin | Résultat |
| -- | ------ | -------- |
| 1 | Accidents par région ou par préfecture | **Introuvables sous une forme utilisable.** Les annuaires régionaux sont hétérogènes (§3.3). Le Togo n’a pas de base nationale d’accidents : l’Office national de la sécurité routière (ONSR), créé en 2022, doit encore mettre en service l’Observatoire de la sécurité routière (Banque mondiale, 2026), et l’observatoire africain n’a reçu aucune donnée du Togo en 2021 |
| 2 | Population par année et par âge | **Trouvée** : projections de l’INSEED (2011–2031), recensement de 2010, Livret 02 du RGPH-5, WPP |
| 3 | Population urbaine par préfecture | **Trouvée** : Livret 02 du RGPH-5. PA-03 devient calculable, donc H8 testable |
| 4 | Âges minimaux par catégorie de permis | **Trouvés** dans des sources secondaires concordantes ; texte officiel introuvable |
| 5 | Méthode de notation de l’état du réseau | **Introuvable.** Le suivi de l’état est décrit comme « fragmenté » (Banque mondiale, 2026). Repères nationaux sans méthode : 49 % du réseau en mauvais état en 2012, 40 % en 2016 |
| 6 | Chronologie des réformes | **Compilée** : dix dates sourcées (D11) |
| 7 | Usage de la moto et des motos-taxis (D12) | **Trouvé en partie** : EHCVM 2021-2022, par zone. Les parts modales restent introuvables. Piste non vérifiée : si le RGPH-5 a repris la question du recensement de 2010 sur la moto, un livret sur les ménages donnerait la possession par préfecture en 2022 ; seuls les livrets 01 à 03 ont été trouvés |

✅ **Recommandations « données ».** Elles naissent de ces recherches et forment une rubrique du tableau de bord : « Pour aller plus loin : ce que les données ne permettent pas encore de dire ». Elle est placée après les recommandations territoriales, pas en tête. Elle comporte trois demandes :
- **une base d’accidents par préfecture**, tenue par l’ONSR, selon un format commun à la police et à la gendarmerie ;
- **l’ouverture des couches « Dégradations » et « Ponts »** du géoportail ;
- **la publication de l’activité des auto-écoles.**

Elle ajoute une hypothèse à tester quand les accidents seront localisés : les tronçons sans aménagements de sécurité concentrent-ils les accidents ?

---

## 9. Traçabilité

- **`data/raw/`** contient les fichiers tels que publiés. Ils ne sont jamais modifiés ; le nettoyage produira d’autres fichiers.
- **WPP (ONU)** : l’API exige un jeton personnel, lu dans la variable d’environnement `ONU_DATAPORTAL_TOKEN` ou dans le fichier `.env`. Le jeton n’est jamais versionné. Sans jeton, le script se replie sur le fichier mondial publié (62 Mo, tous pays), n’en garde que le Togo et note au registre l’empreinte du fichier publié.
- **EHCVM (Banque mondiale)** : le téléchargement exige un compte gratuit, lu dans les variables d’environnement `BM_MICRODATA_EMAIL` et `BM_MICRODATA_PASSWORD`, ou dans les lignes `email` et `password` du fichier `.env`.
- ✅ **`data/raw/_SOURCES.csv`** est le registre des fichiers : **une ligne par fichier publié**, soit 34 fichiers issus de 30 jeux de données (31 téléchargés, 3 recensés seulement). Vérification du 2026-10-04 : les 31 fichiers téléchargés sont dans `data/raw/`, avec la taille et l’empreinte du registre et un format valide ; aucun fichier n’est en trop ; les 3 recensés sont absents, comme prévu. Un fichier aux usages multiples n’a qu’une ligne ; ses usages sont dans la colonne « Codes D ». Par exemple, le profil OMS 2023 porte D1, D3, D9 et D11. Si un téléchargement échoue alors que le fichier local est intact, la ligne précédente est conservée et l’échec est noté en remarque. Pour chaque fichier : codes D, jeu de données, producteur, page source, URL, licence déclarée, dernière modification sur le portail, couverture déclarée, statut, date de téléchargement, taille, empreinte SHA-256 et remarque.
- **`data/reference/`** contient les tables compilées à la main (chronologie, âges minimaux), avec une source par ligne, et le référentiel des préfectures. Celui-ci est produit à partir de `data/raw/` par `python3 scripts/referentiel_prefectures.py`.
- **Versionnement** : les PDF de `data/raw/` (22 Mo) et l’archive de l’EHCVM (15 Mo), dont les conditions d’usage interdisent la redistribution, ne sont pas versionnés (`.gitignore`) ; ils restent téléchargeables à leur source. Sur une copie neuve du dépôt, ces 4 fichiers manquent : relancer le script d’inventaire avec le jeton de l’ONU et le compte de la Banque mondiale ; sans jeton, le fichier WPP serait remplacé par l’extrait du fichier mondial. Le reste est versionné avec le registre.
- **Pour rejouer l’inventaire** : `python3 scripts/inventaire_03.py`. Les URL du portail sont datées : si une source est republiée, l’ancienne URL peut ne plus fonctionner. Le registre garde l’URL et l’empreinte du fichier réellement utilisé.
- **Licences à citer dans le rendu** :
  - HDX : CC BY-IGO ;
  - OMS : CC BY-NC-SA 3.0 IGO, usage non commercial ;
  - WorldPop : CC BY 4.0 ;
  - WPP : CC BY 3.0 IGO ;
  - DHS : conditions du programme DHS ;
  - EHCVM : conditions de la Banque mondiale, sans redistribution ; citation obligatoire, dont le texte est dans le registre ;
  - PDF de l’INSEED et catalogue du géoportail : licence non déclarée.

  Pour les jeux de l’INSEED publiés en licence non ouverte ou sans licence, l’usage dans le cadre du challenge est couvert par l’énoncé, qui les fournit ; le statut est à mentionner en page Méthodologie.

---

## 10. Suite

1. **04 — Data understanding.** Ouvrir et profiler chaque fichier des besoins D1–D13 (les sources hors 02 ont seulement un contrôle avant affichage, §3.2), trancher les observations du §7, confirmer les écarts du §5 et les déclarer avec leur repli. Toutes les sources se joignent par le référentiel des préfectures (D8, R-01). WorldPop ne sera utilisé qu’en repli, si un taux territorial annuel s’avère indispensable.
2. ✅ **Consignes pour le tableau de bord**, issues de la validation :
   - **page des accidents** : séparer la courbe nationale 2010–2024 des chiffres 2022 utilisés dans les taux et les croisements ; afficher l’estimation OMS comme repère, jamais à la place des tués déclarés ;
   - **courbes de O1** : annoter les dates de la chronologie, sans lecture causale ; sur O1-04, griser les années 1990–2009, libellées « population modélisée (WPP) » ;
   - **carte de O5** : couche facultative des équipements de sécurité routière, désactivée par défaut, libellée « non utilisée dans les indicateurs » (conditions au §3.2) ;
   - **page O1** : en contexte, l’usage de la moto et du moto-taxi par zone (EHCVM 2021-2022), jamais par préfecture ;
   - **pages O2 ou O5** : un encadré « ce que les données ne permettent pas de dire » ;
   - **rubrique « Pour aller plus loin »** : les recommandations « données », après les recommandations territoriales ;
   - **annexe nationale** : la longueur de route entretenue, en contexte de O3 (conditions au §3.2) ;
   - **page Méthodologie** : la raison institutionnelle de l’absence d’accidents par territoire, les données disponibles non utilisées, et les licences.

---

## 11. Journal des décisions

| Décision | Où | Validée par |
| -------- | -- | ----------- |
| ✅ **Accidents par territoire** : option A. Les annuaires régionaux ne servent à aucun calcul ; ils sont cités en méthodologie et donnent lieu à une recommandation « données » | §3.3, §8 | `workspace/validation.md`, 2026-10-04 |
| ✅ **Population** : projections 2011–2031, recensement 2010, Livret 02 du RGPH-5 et WPP intégrés | §2 (D7) | `workspace/validation.md` |
| ✅ **Âges minimaux des permis** : A, B et F 18 ans ; C, D et E 21 ans ; étiquetés C | §2 (D2), §5 | `workspace/validation.md` |
| ✅ **Année de référence** : 2022 pour le territorial ; 2023–2024 seulement sur la courbe nationale des accidents | §10 | `workspace/validation.md` |
| ✅ **Chronologie (D11)** : contexte, en annotations sur les courbes de O1 | §2, §10 | `workspace/validation.md` |
| ✅ **Équipements de sécurité routière** : couche facultative sur la carte de O5, jamais dans un indicateur ou un profil | §3.2 | `workspace/validation.md` |
| ✅ **Entretien et coût** : longueur de route entretenue en annexe nationale ; charges de sinistres non retenues | §3.2, §3.3 | `workspace/validation.md` |
| ✅ **Recommandations « données »** : rubrique « Pour aller plus loin », après les recommandations territoriales | §8 | `workspace/validation.md` |
| ✅ **Profil OMS 2023** : O2-09 en repli ; les 1 961 tués estimés restent un repère | §5 | `workspace/validation.md` |
| ✅ **Géoportail** : D5 et D6 datés de 2021–2022 ; auto-écoles comptées « agréées + antennes agréées » | §2 | `workspace/validation.md` |
| ✅ **Options modélisées** : DHS et WPP retenus ; WorldPop et HeiGIT non | §3 | `workspace/validation.md` |
| ✅ **Téléchargement** : WPP par l’API (extrait du fichier mondial en repli) ; catalogue du géoportail dans `data/raw/` ; PDF non versionnés | §9 | Points A, B, C, 2026-10-04 |
| ✅ **Référentiel des 39 préfectures** (option C) : pivot du Livret 02, géométries HDX, table de correspondance | §2 (D8) | 2026-10-04 |
| ✅ **Registre des sources** : une ligne par fichier publié ; les usages multiples vont dans la colonne « Codes D » (profil OMS : D1, D3, D9, D11 ; limites HDX : D8, D13) | §9 | Vérification du 2026-10-04 |
| ✅ **Population avant 2010** : option A amendée. Population reconstituée à partir du recensement 2010 avec les taux de croissance de WPP ; années 1990–2009 étiquetées C et grisées sur la courbe | §5, §7 | Point 1.2, 2026-10-04 |
| ✅ **D11 et D12** : leur passage de « Manquant » à « Partiel » est un statut du 03, pas un écart ; le 02 reste inchangé (R-20) et leur rôle reste « Contexte ». Deux écarts de contenu sont déclarés : aucune réforme datée avant 2013 (D11), enquêtes auprès des ménages au lieu des parts modales (D12) | §2, §5 | Point sur D11 et D12, 2026-10-04 |
| ✅ **Sources hors 02** : dans le livrable en contexte (couche facultative de O5, annexe nationale de O3), sans profilage en 04 ; un contrôle avant affichage, sinon citation en méthodologie seulement | §3.2, §10 | Point 1.5, 2026-10-04 |
| ✅ **EHCVM 2021-2022 (D12)** : retenue en contexte de O1 et de H2, étiquetée C ; trois parts de ménages, par zone seulement ; DHS gardée pour la tendance 1998–2017, sans raccord ; archive téléchargée avec le compte de `.env`, non versionnée. Les autres études du catalogue de microdonnées ne sont pas retenues | §2 (D12), §3, §5, §9 | §7.3 de `tmp/recherche-complementaires.md`, 2026-10-04 |
