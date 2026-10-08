## Page 5 — Priorités

**Objectif :** dire par où commencer : les zones en difficulté, puis les préfectures, sur quel levier, et si ce classement tient. La page dit où agir ; la page 6 dit quoi faire.

**Question :** « Par où commencer ? »

**Réponse sous le titre** (11 §4.3) : « Commencer par la Centrale, seule zone en retard sur la route et la formation, et par 5 préfectures qui cumulent les deux déficits (641 955 habitants) ; aucun test de robustesse ne change plus de 2 des 10 premières. » Chiffres lus dans `zones_10.csv` (colonne « Moins bien desservie pour »), `recommandations_10.csv` (population de la recommandation sur les 5 préfectures qui cumulent) et `sensibilite_08.csv` (lignes de synthèse des tests).

**Ce que la page reprend** : le classement, les leviers, la lecture par zone et par région et la robustesse du 08 ; les phrases de diagnostic du 09 (§6) ; la conclusion du 10 sur les zones les moins bien desservies (§4.6), qui passe de la page 6 à cette page (11, journal).

```text
┌──────────────────────────────────────────────────────────────────┐
│  PAR OÙ COMMENCER ?   + réponse                                   │
├──────────────────────────────────────────────────────────────────┤
│  [Filtres : zone, levier, priorité]                               │
├──────────────────────────────────────────────────────────────────┤
│  [LES ZONES EN DIFFICULTÉ — 6 zones, pour quoi]           │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [LES 5 QUI CUMULENT]                                             │
├──────────────────────────────────────────────────────────────────┤
│  [LES 10 PREMIÈRES — barres, ce qu’elles cumulent]                │
├──────────────────────────────────────────────────────────────────┤
│  [LES DEUX LEVIERS — réseau (13), formation (23)]                 │
├──────────────────────────────────────────────────────────────────┤
│  [LE CLASSEMENT TIENT-IL ? — poids du réseau, 5 tests]            │
├──────────────────────────────────────────────────────────────────┤
│  [CLASSEMENT DES 38 — tableau triable ; Mô à part]                │
├──────────────────────────────────────────────────────────────────┤
│  [SYNTHÈSE CHIFFRÉE]  [LIMITE]                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Filtres :** zone (les 6 zones, R-02), levier (réseau, formation, les deux, aucun), priorité. Ils s’appliquent aux sections 2 à 6 ; la section 1 montre toujours les 6 zones.

### Section 1 — Les zones en difficulté

Visuel principal, à côté du Constat. Deux analyses désignent les mêmes 4 zones : le classement des zones (08 §6) et la conclusion du 10 sur les zones les moins bien desservies (10 §4.6).

| Zone | Rang | Moins bien desservie pour… | Ruraux à moins de 2 km d’une route revêtue | Auto-écoles agréées pour 100 000 hab. | Levier réseau | Levier formation | Recommandation |
| ---- | ---- | -------------------------- | ------------------------------------------ | ------------------------------------- | ------------- | ---------------- | -------------- |
| Centrale | 1 | la route et la formation | 13,2 % | 0,50 | 4 préfectures, 113,6 km | 3 préfectures, 6 auto-écoles | Agir d’abord dans la Centrale, seule zone en retard sur la route et la formation |
| Savanes | 2 | la formation | 16,9 % (cas limite pour la route) | 0,35 | — | 5 préfectures, 9 auto-écoles | Ouvrir d’abord des auto-écoles dans les Savanes et la Maritime hors Grand Lomé |
| Plateaux | 3 | la route | 13,6 % | 0,55 | 6 préfectures, 150,5 km | 7 préfectures, 12 auto-écoles | Remettre en état d’abord le réseau des Plateaux |
| Maritime hors Grand Lomé | 4 | la formation | 23,1 % | 0,37 | — | 3 préfectures, 6 auto-écoles | Ouvrir d’abord des auto-écoles dans les Savanes et la Maritime hors Grand Lomé |
| Kara | 5 | — | 17,5 % | 0,71 | 2 préfectures, 37,3 km | 5 préfectures, 8 auto-écoles | — |
| Grand Lomé | 6 | — | sans population rurale | 4,71 | 1 préfecture, 3,2 km | — | — |

- **Sources :** rang et leviers, `regions_08.csv` (lignes de zone) ; « moins bien desservie pour », accès rural et auto-écoles, `zones_10.csv` ; titre de la recommandation, `cartes_10.csv` (ligne de la colonne `Recommandation` de `zones_10.csv`).
- **Règle, sous le tableau :** « Une zone est moins bien desservie si elle est sous la médiane des zones : 16,9 % des ruraux à moins de 2 km d’une route revêtue pour la route, 0,53 auto-école pour 100 000 habitants pour la formation. » Médianes lues sur la ligne « Médiane des zones » de `zones_10.csv`.
- **Note des Savanes :** « Les Savanes sont un cas limite pour la route : 16,9 %, pour 17,2 % dans le pays. » (`zones_10.csv`, ligne du pays.)
- **Note sur l’accès rural, lue dans `erratum_A1.csv` (ligne A1-E1) :** « Mesuré avec la grille de population WorldPop, l’accès rural change de lecture : les Savanes passent sous la médiane et la Centrale au-dessus. La Centrale garde la première place : elle reste la zone au réseau le plus dégradé, et sa formation ne change pas. Les deux mesures sont en page Méthodologie. »
- **Couleur :** la colonne « Moins bien desservie pour… » en pastille : route et formation en `#0d366b`, un seul déficit en `#3987e5`, aucun en `#b9b6ad` (palette `PRIORITE`, comme la priorité des recommandations de zone).
- **Ce que dit chaque zone :** sous chaque ligne, sa phrase de diagnostic (`phrases_11.csv`, maille « Zone », colonne « Phrase affichée »). Exemple, la Centrale : « Centrale est la seule zone au-dessus de la médiane pour le réseau et en dessous pour la formation : 40,3 % de km en mauvais état sur 437,2 km évalués, et 4 auto-écoles agréées pour 795 529 habitants (0,50 pour 100 000). 4 de ses 5 préfectures reçoivent le levier réseau (113,6 km à remettre en état), 3 le levier formation (6 auto-écoles). »
- **Par région :** une ligne sous le tableau : « Par région : Centrale, puis Plateaux, Savanes, Kara et Maritime. La Centrale est en tête dans les deux lectures. » Ordre lu dans `regions_08.csv` (lignes de région). Avec la phrase de la région Maritime (`phrases_11.csv`) : son offre de 3,06 auto-écoles pour 100 000 habitants cache celle de la Maritime hors Grand Lomé (0,37).
- **Liens :** chaque recommandation mène à la page 6, onglet « Zones les moins desservies » (`st.session_state["recommandations_rang"]` = 5).
- **Ce que ce tableau n’est pas :** la comparaison complète des zones, avec tous les indicateurs et les seuils, est en page 2 (section 4). Les deux mesures de l’accès rural et leurs calculs sont en page Méthodologie (section 6).

### Section 2 — Les 5 préfectures qui cumulent

| Préfecture | Zone     | Population | Part en mauvais état | Km à remettre en état | Auto-écoles à ouvrir |
| ----------- | -------- | ---------- | --------------------- | ----------------------- | ---------------------- |
| Danyi       | Plateaux | 40 240     | 100 %                 | 42,7                    | 1                      |
| Blitta      | Centrale | 163 272    | 68,2 %                | 54,5                    | 2                      |
| Agou        | Plateaux | 85 793     | 40,0 %                | 31,8                    | 1                      |
| Tchamba     | Centrale | 200 585    | 34,0 %                | 23,7                    | 3                      |
| Bassar      | Kara     | 152 065    | 28,0 %                | 22,9                    | 2                      |

**Total :** 641 955 habitants ; 175,6 km à remettre en état ; 9 auto-écoles à ouvrir. Lien vers la recommandation « Remettre en état le réseau des 5 préfectures qui cumulent » (page 6).

**Note :** « Déjà repérées à l’exploration : ces 5 préfectures étaient dans le pire quart des deux dimensions. » (`signaux_06.csv`, croisement réseau dégradé et formation basse ; 08 §4.)

**Sources :** `prefectures_10.csv` ; `recommandations_10.csv` (population et km de la recommandation).

### Section 3 — Les 10 premières

Barres horizontales du score, une par préfecture, colorées par levier. Le score se lit décomposé : la part du réseau et la part de la formation sont deux segments de la barre (08 §4). À droite, la robustesse : « en tête du classement dans 6 tests sur 6 ».

| Rang | Préfecture | Zone                      | Population | Part en mauvais état (km évalués) | Auto-écoles pour 100 000 hab. | Leviers              | Tests sur 6 |
| ---- | ----------- | ------------------------- | ---------- | --------------------------------- | ------------------------------ | -------------------- | ----------- |
| 1    | Danyi       | Plateaux                  | 40 240     | 100 % (49,8 km)                   | 0                              | réseau et formation | 6           |
| 2    | Blitta      | Centrale                  | 163 272    | 68,2 % (101,1 km)                 | 0                              | réseau et formation | 6           |
| 3    | Agou        | Plateaux                  | 85 793     | 40,0 % (124,1 km)                 | 0                              | réseau et formation | 6           |
| 4    | Tchamba     | Centrale                  | 200 585    | 34,0 % (120,3 km)                 | 0                              | réseau et formation | 6           |
| 5    | Bassar      | Kara                      | 152 065    | 28,0 % (167,5 km)                 | 0                              | réseau et formation | 6           |
| 6    | Oti         | Savanes                   | 124 848    | 21,1 % (140,6 km)                 | 0                              | formation            | 6           |
| 7    | Bas-Mono    | Maritime hors Grand Lomé | 94 860     | 21,1 % (35,8 km)                  | 0                              | formation            | 6           |
| 8    | Est-Mono    | Plateaux                  | 164 460    | 17,2 % (110,7 km)                 | 0                              | formation            | 4           |
| 9    | Oti-Sud     | Savanes                   | 150 376    | 14,4 % (131,7 km)                 | 0                              | formation            | 4           |
| 10   | Tchaoudjo   | Centrale                  | 240 360    | 36,9 % (125,7 km)                 | 0,83                           | réseau              | 3           |

- **Les km évalués** sont écrits à côté de la part : le taux ne dit pas le volume. Danyi est en tête avec 100 % de km en mauvais état, sur 49,8 km évalués, pour 40 240 habitants (08 §4).
- **Ce qu’elle cumule :** chaque ligne s’ouvre sur sa phrase de diagnostic (`phrases_11.csv`, maille « Préfecture », colonne « Phrase affichée »). Exemple : « Blitta cumule 68,2 % de km en mauvais état sur 101,1 km évalués (4 tronçons critiques) et aucune auto-école agréée pour 163 272 habitants (2 recensées, non agréées), à 25,9 km de la plus proche. En tête du classement dans les 6 tests de robustesse. »
- **Note :** « Les 10 premières comptent 1 416 859 habitants. Ni le Golfe ni Agoè-Nyivé n’en font partie. » (`classement_08.csv` ; `sensibilite_08.csv`, note du test sans le Grand Lomé.)

**Sources :** `classement_08.csv`, `sensibilite_08.csv`, `phrases_11.csv`.

### Section 4 — Les deux leviers

Le classement se lit aussi par levier : chaque préfecture reçoit le levier de chaque seuil qu’elle franchit (08 §5).

| Levier | Préfectures | Population | Écart à la cible | Cible | En tête du levier |
| ------ | ----------- | ---------- | ---------------- | ----- | ----------------- |
| Réseau | 13 | 2 868 523 | 304,6 km à remettre en état | 14,35 % de km en mauvais état, la médiane nationale | Danyi (100,0 %) |
| Formation | 23, dont Mô | 2 932 492 | 41 auto-écoles à ouvrir | 1,065 auto-école pour 100 000 habitants, la médiane des 16 préfectures équipées | Haho, la plus peuplée des 23 (305 096 habitants) |

Deux listes, côte à côte, dans l’ordre de chaque levier (`classement_08.csv`, colonnes « Rang dans le levier réseau » et « Rang dans le levier formation ») :

- **Réseau (13) :** rang, préfecture, part en mauvais état et km évalués, km à remettre en état. De Danyi (42,7 km) à Sotouboua (7,1 km). Agoè-Nyivé, 10e, a 3,2 km à remettre en état pour 882 695 habitants.
- **Formation (23) :** rang, préfecture, population, auto-écoles à ouvrir, distance à l’auto-école agréée la plus proche, population dont le chef-lieu est à plus de 10 km. Les préfectures à égalité (aucune auto-école agréée) sont départagées par la population. La nature du zéro est écrite en clair : « aucune auto-école recensée » (15 préfectures, 25 auto-écoles) ou « auto-écoles recensées, non agréées » (8 préfectures, 16 auto-écoles), comme dans les recommandations de la page 6.

**Déficits, sous les deux listes :** « 5 préfectures cumulent les deux déficits, 26 en ont un, 8 n’en ont aucun. » (`classement_08.csv`, colonne des déficits.)

**Liens :** réseau → recommandations « Remettre en état le réseau des 5 préfectures qui cumulent » et « … de 8 autres préfectures » ; formation → « Ouvrir des auto-écoles dans les 15 préfectures qui n’en ont aucune » et « Vérifier les auto-écoles non agréées de 8 préfectures » (page 6).

**Sources :** `classement_08.csv`, `regions_08.csv` (ligne du pays : préfectures, population et écart de chaque levier), `recommandations_10.csv` (cibles).

### Section 5 — Le classement tient-il ?

**Poids du réseau** (seuil déplaçable, exception de calcul admise par la maquette, 11 §4.4) :

- **Curseur :** le poids du réseau, de 0 à 100 %, par défaut à 50 %. Le poids de la formation est le complément.
- **Formule du 08 :** score = poids du réseau × rang percentile du réseau + poids de la formation × rang percentile de la formation, lus dans `classement_08.csv`. À score égal, la préfecture la plus peuplée passe devant.
- **Affichage :** le nouveau classement des 10 premières, et les préfectures qui entrent ou sortent, par rapport au classement à 50 %.
- **Valeurs de contrôle :** à 50 %, le classement du 08. À 2/3, comme le test du 08 : entrent Kloto et Ogou, sortent Est-Mono et Oti-Sud. À 1/3 : entre Haho, sort Tchaoudjo.

**Les 5 tests de robustesse** (`sensibilite_08.csv`, lignes de synthèse ; libellés fixés par ce plan, entrées et sorties lues dans le CSV) :

| Test | Changements parmi les 10 premières | Entrent | Sortent |
| ---- | ---------------------------------- | ------- | ------- |
| Réseau compté pour 2/3 | 2 | Kloto, Ogou | Est-Mono, Oti-Sud |
| Formation comptée pour 2/3 | 1 | Haho | Tchaoudjo |
| Écart à la médiane, au lieu du rang | 1 | Kloto | Oti-Sud |
| Sans le Grand Lomé | 1 | Haho | Tchaoudjo |
| Distance à l’auto-école, au lieu du nombre d’auto-écoles | 2 | Anié, Haho | Est-Mono, Tchaoudjo |

- **Règle, sous le tableau :** « Le classement est stable si aucun test ne change plus de 2 des 10 premières. »
- **Les plus sûres et les moins sûres :** « Toujours en tête : Danyi, Blitta, Agou, Tchamba, Bassar, Oti, Bas-Mono. Les moins sûres : Est-Mono et Oti-Sud (4 tests sur 6), Tchaoudjo (3 sur 6). » (`classement_08.csv`, colonne des tests.)

### Section 6 — Classement complet

- **Tableau triable** des 38 préfectures classées : rang, zone, population, part en mauvais état et km évalués, auto-écoles pour 100 000 habitants, déficits (sur 2), leviers, km de routes pour 10 000 habitants avec la mention « desserte faible » (13 des 38, et Mô), distance à l’auto-école agréée la plus proche, tests sur 6. La desserte et la distance sont affichées à côté du classement, sans y entrer (08 §3).
- **Mô, à part**, sous le tableau, avec sa phrase de diagnostic (`phrases_11.csv`) : « Mô, hors classement, n’a aucune route classée : ni état, ni km évalué, et une desserte nulle. Elle n’a aucune auto-école, ni agréée ni recensée, pour 52 448 habitants, à 52,2 km de la plus proche. »
- **Lien :** « Voir le classement sur la carte → » (page 4, couche Priorité).

**Export :** le classement, en CSV.

**Sources :** `classement_08.csv`, `phrases_11.csv`.

### Section 7 — Constat, synthèse chiffrée et limite

**Constat :** « La Centrale est la seule zone en retard sur la route et la formation. Le classement est stable : aucun test ne change plus de 2 des 10 premières ; 7 préfectures y restent dans les 6 tests : Danyi, Blitta, Agou, Tchamba, Bassar, Oti, Bas-Mono. »

**Synthèse chiffrée :** 4 zones en difficulté (Centrale : route et formation ; Plateaux : route ; Savanes et Maritime hors Grand Lomé : formation) ; 5 préfectures qui cumulent, 641 955 habitants ; 10 premières, 1 416 859 habitants ; 13 préfectures au levier réseau (304,6 km), 23 au levier formation (41 auto-écoles).

**Limite :** « Classement en C : vérification avant investissement. Le risque n’est pas classé par territoire, faute d’accidents par préfecture. L’accès rural, qui désigne les zones en retard sur la route, est estimé avec une population répartie uniformément dans chaque préfecture. »

**Sources de la page :** `classement_08.csv`, `sensibilite_08.csv`, `regions_08.csv`, `prefectures_10.csv`, `zones_10.csv`, `cartes_10.csv`, `recommandations_10.csv`, `signaux_06.csv`, `phrases_11.csv`.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
