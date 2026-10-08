

## Page 6 — Recommandations

**Objectif :** restituer les 15 recommandations du 10 et les 39 fiches préfectures : quoi faire, où, pour combien d’habitants, dans quel ordre. La page dit quoi faire ; la page 5 dit par où commencer.

**Référence :** le 10 §6, §6.1, §6.2 et §7, qui fixent le format des cartes, les 7 onglets, l’ordre, les filtres, les textes des cartes, le format des fiches et la rubrique « Pour aller plus loin ». Ce plan les suit. Un seul écart, noté au journal du 11 : le tableau de conclusion des zones (10 §4.6) est en page 5, où les zones en difficulté sont définies ; l’onglet des zones garde ses 3 cartes et renvoie à la page 5.

```text
┌──────────────────────────────────────────────────────────────────┐
│  QUELLE ACTION ENGAGER ?                                          │
├──────────────────────────────────────────────────────────────────┤
│  [BARRE DE RÉSUMÉ]   [Filtres : priorité, zone, recherche]        │
│  [ZONES EN DIFFICULTÉ — une ligne, lien vers la page 5]           │
├──────────────────────────────────────────────────────────────────┤
│  [ONGLETS : Toutes | Réseau | Formation | Sécurité routière |     │
│             Zones les moins desservies | Données | Actions par zone]│
├──────────────────────────────────────────────────────────────────┤
│  [CARTES DE RECOMMANDATION — grille de 3 colonnes]       │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [POUR ALLER PLUS LOIN — 4 cartes « données »]                    │
├──────────────────────────────────────────────────────────────────┤
│  [SYNTHÈSE CHIFFRÉE]  [LIMITE]                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Section 1 — Les 7 onglets

Dans l’ordre du 10 §6 :

| # | Onglet | Contenu |
| - | ------ | ------- |
| 1 | **Toutes** | Une ligne « Zones en difficulté » en tête (section 4), les 11 cartes de recommandation, puis la rubrique « Pour aller plus loin » (4 cartes) |
| 2 | **Réseau** | Les 4 recommandations sur le réseau |
| 3 | **Formation** | Les 3 recommandations sur la formation |
| 4 | **Sécurité routière** | La recommandation sur les deux-roues |
| 5 | **Zones les moins desservies** | Les 3 cartes de zone sous un bandeau « Par où commencer », et un lien « Pourquoi ces zones → page 5 » (section 4) |
| 6 | **Données** | La rubrique « Pour aller plus loin » : les 4 recommandations sur les données |
| 7 | **Actions par zone** | Les 39 fiches préfectures, avec le filtre par zone (section 5) |

### Section 2 — Format d’une carte

Lu dans `cartes_10.csv` (10 §6, maquette §8.11) :

- **Thème** (pastille et libellé en majuscules) ; **titre** ; **phrase de cible** ; **contexte** (« N préfectures · Z habitants concernés ») ;
- **étiquettes :** priorité, nature (immédiate ou conditionnelle), horizon. Couleurs de la palette `PRIORITE` : haute `#0d366b`, moyenne `#3987e5`, faible `#cde2fb`, non classée `#b9b6ad`. L’horizon affiché est celui de l’action ; la vérification d’une carte conditionnelle se fait dans l’année, et le texte le dit (10 §6) ;
- **bouton « Détail »** : les champs de R-18 en clair, à savoir acteur, indicateur de suivi, niveau de preuve et réserve. R-18 est une règle d’affichage : aucune carte sans ces champs ;
- le **texte** de la carte (10 §6.1) sous le contexte.

**Exemple, la première carte :**

> **ZONES LES MOINS DESSERVIES**
> **Agir d’abord dans la Centrale, seule zone en retard sur la route et la formation**
> Remettre en état 113,6 km et ouvrir 6 auto-écoles en premier
> 5 préfectures · 795 529 habitants concernés
> [Haute] [Conditionnelle] [3 ans]
>
> *Détail :* Ministère des travaux publics, fonds d’entretien routier ; ministère chargé des transports, auto-écoles · Suivi : Part des km de routes en mauvais état ; auto-écoles agréées pour 100 000 habitants ; accès rural à une route revêtue · Niveau : C — estimé · Réserve : Km et auto-écoles déjà comptés dans les autres recommandations. L’accès rural est estimé en supposant la population répartie uniformément.

Les champs du détail sont lus tels quels dans `cartes_10.csv` (colonnes `Acteur`, `Indicateur de suivi`, `Niveau de preuve`, `Réserve`), écrites en clair par le 10 §8 ; l’identifiant et la source de la recommandation ne s’affichent pas (10 §3).

**Ordre par défaut :** la colonne « Ordre » de `cartes_10.csv`, soit la priorité, puis les habitants.

**Filtres** (10 §4.5 et §6) :

- **priorité :** haute, moyenne, faible ;
- **zone :** tout le Togo (par défaut), puis les 6 zones. Une carte s’affiche si sa colonne `Zones` de `cartes_10.csv`, prévue « pour le filtre » (10 §8), contient la zone choisie ; les zones de cette colonne viennent de `prefectures_10.csv`, comme le demande le 10 §6. Les cartes nationales (deux-roues, permis moto, données) restent affichées, avec la mention « national ». La recommandation sur les 10 tronçons les plus dégradés n’est pas répartie : ses tronçons traversent 5 zones, elle s’affiche pour chacune ;
- **recherche :** dans le titre et le texte ;
- **le levier** est donné par les onglets.

Aucun total de la page (barre de résumé, filtre par zone) n’additionne les habitants, les km ou les auto-écoles d’une carte à l’autre (10 §6, « pas de double compte »).

**Horizons.** La cible affichée sur chaque carte reste celle de 2022, mesurée. Sous elle, une ligne donne la quantité à l’horizon que la recommandation porte elle-même, lue dans `horizon_A1.csv` (lignes de maille « Recommandation », colonne « Palier de l’horizon ») :

> « D’ici 2029, horizon de cette action : 30 auto-écoles, la population ayant grandi. »

Elle ne s’affiche que pour les recommandations chiffrées dont la quantité change avec la population : les auto-écoles, la desserte de Mô et le permis moto. Pour la remise en état, une ligne dit à la place : « Cette quantité ne change pas avec l’horizon : aucune donnée ne mesure l’usure du réseau. » Les recommandations sur les données et sur les deux-roues n’ont pas de quantité : elles n’ont pas cette ligne.

Le détail par horizon, zone et préfecture est en page Horizon 2031, où chaque carte renvoie.

### Section 3 — Les 15 cartes, dans l’ordre

| # | Titre | Thème | Habitants | Priorité | Nature | Horizon |
| - | ----- | ----- | --------- | -------- | ------ | ------- |
| 1 | Agir d’abord dans la Centrale, seule zone en retard sur la route et la formation | Zones les moins desservies | 795 529 | Haute | Conditionnelle | 3 ans |
| 2 | Remettre en état le réseau des 5 préfectures qui cumulent | Réseau | 641 955 | Haute | Conditionnelle | 3 ans |
| 3 | Cibler les usagers de deux-roues motorisés | Sécurité routière | 8 095 498 | Moyenne | Conditionnelle | 3 ans |
| 4 | Faire du permis moto la priorité de la formation | Formation | 4 193 458 | Moyenne | Immédiate | 3 ans |
| 5 | Remettre en état les 10 tronçons les plus dégradés | Réseau | 3 311 579 | Moyenne | Conditionnelle | 3 ans |
| 6 | Ouvrir d’abord des auto-écoles dans les Savanes et la Maritime hors Grand Lomé | Zones les moins desservies | 2 490 135 | Moyenne | Conditionnelle | 3 ans |
| 7 | Remettre en état le réseau de 8 autres préfectures | Réseau | 2 226 568 | Moyenne | Conditionnelle | 5 ans |
| 8 | Ouvrir des auto-écoles dans les 15 préfectures qui n’en ont aucune | Formation | 1 822 046 | Moyenne | Conditionnelle | 3 ans |
| 9 | Remettre en état d’abord le réseau des Plateaux | Zones les moins desservies | 1 635 946 | Moyenne | Conditionnelle | 3 ans |
| 10 | Vérifier les auto-écoles non agréées de 8 préfectures | Formation | 1 110 446 | Moyenne | Conditionnelle | 3 ans |
| 11 | Vérifier la desserte de Mô | Réseau | 52 448 | Faible | Conditionnelle | 5 ans |
| 12 | Créer une base d’accidents par préfecture | Données | 8 095 498 | Haute | Immédiate | 1 an |
| 13 | Ouvrir les couches « Dégradations » et « Ponts » | Données | 8 095 498 | Moyenne | Immédiate | 1 an |
| 14 | Publier l’activité des auto-écoles | Données | 8 095 498 | Moyenne | Immédiate | 1 an |
| 15 | Publier un parc en circulation et des libellés exacts | Données | 8 095 498 | Faible | Immédiate | 1 an |

Les cartes 12 à 15 forment la rubrique **« Pour aller plus loin : ce que les données ne permettent pas encore de dire »**, placée après les recommandations territoriales (03 §8, 10 §7). Sa phrase d’introduction, celle du 10 §7 :

> « Ces 4 actions relèvent des producteurs de données, pas des régions. La base d’accidents par préfecture permettrait de trancher 7 questions que le diagnostic laisse ouvertes, dont le lien entre réseau dégradé et accidents. Les trois autres rendraient vérifiables les chiffres estimés de cette page. »

La priorité « Haute » de la base d’accidents reste affichée sur sa carte : la place dans la page ne change pas la priorité (10 §7).

### Section 4 — Les zones en difficulté sur cette page

**En tête de l’onglet « Toutes »**, une ligne, au-dessus des cartes : « Zones en difficulté : Centrale (route et formation), Plateaux (route), Savanes et Maritime hors Grand Lomé (formation). Pourquoi ces zones → page 5. » Zones et dimensions lues dans `zones_10.csv` (colonne « Moins bien desservie pour »). Elle répond à l’objectif 5 (« dans les régions les moins bien desservies ») dès l’ouverture de la page, sans changer l’ordre des cartes du 10.

**Onglet « Zones les moins desservies » :**

- **Bandeau « Par où commencer » :** « Ces trois cartes ne créent ni km ni auto-école en plus : elles disent par quelle zone commencer. » (10 §4.6.)
- **Les 3 cartes :** 1 (Centrale), 9 (Plateaux), 6 (Savanes et Maritime hors Grand Lomé).
- **Lien :** « Pourquoi ces zones → page 5 » : le tableau de conclusion du 10 §4.6 (accès rural, auto-écoles pour 100 000 habitants, médianes des zones, « moins bien desservie pour… ») y est affiché, avec le rang des zones du 08. Les deux mesures de l’accès rural et leurs calculs sont en page Méthodologie (section 6).
- **Note sur l’accès rural, lue dans `erratum_A1.csv` (ligne A1-E1) :** « Mesuré avec la grille de population WorldPop, l’accès rural change de lecture : les Savanes passent sous la médiane et la Centrale au-dessus. La Centrale garde la première place : elle reste la zone au réseau le plus dégradé, et sa formation ne change pas. Les deux mesures sont en page Méthodologie. »

**Arrivée depuis la page 5 :** les liens de la section 1 de la page 5 écrivent le rang 5 dans `st.session_state["recommandations_rang"]` : la page s’ouvre sur cet onglet.

### Section 5 — Onglet « Actions par zone »

Les 39 fiches de `prefectures_10.csv`, au format du 10 §6.2 :

- **format :** celui des cartes, même grille de 3 colonnes, mêmes étiquettes de priorité ;
- **titre :** la préfecture ; **thème :** la zone ; **grand chiffre :** la population ;
- **blocs** « Réseau » et « Formation » (colonnes `Texte réseau`, `Texte formation`) ; pour Mô, le premier bloc s’intitule « Desserte » ;
- **bandeau** « Actions recommandées » (colonne `Actions`), fond gris clair, bordure gauche sombre ;
- **pied :** l’étiquette de priorité et le tag « Zone — Préfecture » ;
- **icônes :** 🛣️ réseau seul, 📚 formation seule, 🛣️📚 les deux, ✓ suivi courant ;
- **aucun code interne** dans les textes.

**Cas particuliers** (10 §6.2), textes lus dans `prefectures_10.csv` :

- **Mô :** 📚, moyenne. « Desserte : aucune route classée : ni état ni km évalué. » ; formation : aucune auto-école, la plus proche à 52,2 km ; actions : vérifier la desserte sur place, puis ouvrir une auto-école après vérification.
- **Agoè-Nyivé :** 🛣️, moyenne. Réseau : 26,0 % en mauvais état, 3,2 km à remettre en état. Formation : 3,29 auto-écoles pour 100 000 habitants, au-dessus de la cible.
- **Golfe :** ✓, aucune action. Formation : la plus forte offre du pays (5,67 pour 100 000 habitants).
- **Les 7 autres préfectures sans levier** (Zio, Assoli, Cinkassé, Tône, Kpélé, Lacs, Vo) : ✓, « Suivi courant. Aucune action prioritaire. » Pour Zio et Kpélé, la fiche ajoute qu’un des 10 tronçons les plus dégradés les traverse (colonne « Réseau — dont parmi les 10 plus dégradés »).

**Filtre :** tout le Togo (par défaut), puis les 6 zones.

**Répartition :** 5 fiches en priorité haute, 26 en moyenne, 8 sans action (couleur `#b9b6ad`).

**Exemple, Danyi :**

> **Danyi** — Plateaux · **40 240** habitants
> **Réseau :** 100 % des routes en mauvais état (49,8 km évalués, 3 tronçons critiques).
> **Formation :** Aucune auto-école, ni agréée ni recensée. La plus proche est à 12,9 km.
> **Actions recommandées :** Vérifier l’état sur place, puis remettre en état 42,7 km. Vérifier qu’aucune auto-école n’existe, puis en ouvrir une.
> [Haute] 📍 Plateaux — Danyi

**Tri :** rang national par défaut (Mô, non classée, après les 38), puis population, zone, nombre de déficits.

**Arrivée depuis la page 4 :** le bouton « Voir la fiche de <préfecture> → » de la carte écrit la préfecture dans `st.session_state["fiche_prefecture"]` et le rang 7 dans `st.session_state["recommandations_rang"]`. La page s’ouvre alors sur cet onglet, filtrée sur la préfecture, avec un bouton « Voir les 39 fiches » qui retire le filtre (design-page4.md, section 7).

### Section 6 — Résumé, constat, synthèse chiffrée et limite

**Barre de résumé :** « 15 recommandations · les habitants ne s’additionnent pas d’une carte à l’autre ».

**Constat** (10 §6) : « 5 préfectures cumulent les deux déficits : Danyi, Blitta, Agou, Tchamba et Bassar, 641 955 habitants. » (`recommandations_10.csv`, territoire et population de la recommandation sur ces 5 préfectures.)

**Synthèse chiffrée :** 15 recommandations : 3 en priorité haute, 10 en moyenne, 2 en faible ; 10 conditionnelles, 5 immédiates. Réseau : 304,6 km à remettre en état dans 13 préfectures. Formation : 41 auto-écoles dans 23 préfectures.

**Limite :** « Recommandations en C : vérifier avant d’investir ; pas d’accidents par territoire ; le coût n’est pas dans les données. »

**Export :** les cartes et les fiches, en CSV.

**Sources de la page :** `cartes_10.csv`, `prefectures_10.csv`, `zones_10.csv`, `recommandations_10.csv`.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
