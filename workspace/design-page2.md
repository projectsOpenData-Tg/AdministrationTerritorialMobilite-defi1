## Page 2 — Comparaison territoriale

**Objectif :** comparer les territoires sur ce qui est mesuré par territoire : l’état du réseau, l’offre de formation, la desserte. L’énoncé demande ces mesures « par région et par préfecture » (objectifs 3 et 4) : la page lit les 6 zones, les 5 régions et les 39 préfectures.

```text
┌──────────────────────────────────────────────────────────────────┐
│  QUELS TERRITOIRES SONT LES MOINS BIEN ÉQUIPÉS ?                  │
├──────────────────────────────────────────────────────────────────┤
│  [Maille : zones | régions | préfectures]  [Filtres]              │
├──────────────────────────────────────────────────────────────────┤
│  [3 CHIFFRES CLÉS]                                                │
├──────────────────────────────────────────────────────────────────┤
│  [RÉSEAU ET FORMATION — nuage de points + curseur]       │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [LES TERRITOIRES — tableau des zones ou des régions]             │
├──────────────────────────────────────────────────────────────────┤
│  [ÉTAT DU RÉSEAU PAR ZONE — barres empilées]                      │
├──────────────────────────────────────────────────────────────────┤
│  [OÙ SONT LES AUTO-ÉCOLES — concentration et distance]            │
├──────────────────────────────────────────────────────────────────┤
│  [LES 39 PRÉFECTURES — tableau triable]                           │
├──────────────────────────────────────────────────────────────────┤
│  [POINTS D’ATTENTION]                                             │
├──────────────────────────────────────────────────────────────────┤
│  [SYNTHÈSE CHIFFRÉE]  [LIMITE]                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Section 1 — Maille et filtres

- **Maille :** zones (6, par défaut) | régions (5) | préfectures (39). Le nuage de points et le tableau des territoires suivent la maille choisie.
  - **Zones** (par défaut, R-02) : Grand Lomé, Maritime hors Grand Lomé, Plateaux, Centrale, Kara, Savanes.
  - **Régions :** Maritime (Grand Lomé compris), Plateaux, Centrale, Kara, Savanes, lues dans `regions_08.csv` (lignes « Région »). Le tableau de bord ne les recalcule pas : le 08 les a calculées par sommes (08 §6).
  - **Préfectures :** les 39.
- **Filtres :** zone, priorité (haute, moyenne, aucune action).
- **Tri :** par population, part de routes en mauvais état, auto-écoles pour 100 000 habitants, accès rural, priorité.

**Ce que la maille « régions » change.** Plateaux, Centrale, Kara et Savanes sont à la fois zone et région : leurs valeurs ne changent pas. Seule la Maritime diffère. Une note s’affiche sous le tableau quand la maille « régions » est choisie :

> « Avec le Grand Lomé, la région Maritime a 3,06 auto-écoles agréées pour 100 000 habitants : ce chiffre cache celui de la Maritime hors Grand Lomé : 0,37. »

Les deux valeurs sont lues dans `regions_08.csv` (région Maritime, zone Maritime hors Grand Lomé) ; la phrase vient du 09 §6.

### Section 2 — 3 chiffres clés

| Chiffre clé                                  | Valeur    | Contexte                                                                                     | Niveau | Source                                                             |
| --------------------------------------------- | --------- | -------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------ |
| Préfectures au réseau dégradé             | 13        | 2 868 523 habitants ; plus de 22,13 % de routes en mauvais état                             | C      | `regions_08.csv` (ligne du pays)                                 |
| Préfectures sans auto-école agréée        | 23 sur 39 | 2 932 492 habitants ; 15 n’ont aucune auto-école, même non agréée (1 822 046 habitants) | B      | `indicateurs_07.csv` (préfectures sans auto-école)             |
| Préfectures loin d’une auto-école agréée | 26 sur 39 | 3 482 856 habitants ; chef-lieu à plus de 10 km de l’auto-école agréée la plus proche   | C      | `indicateurs_07.csv` (distance à l’auto-école la plus proche) |

**Réserve du 3e chiffre :** la distance part du chef-lieu ; pour 9 préfectures, d’un point central de la préfecture. Ce n’est pas la population à plus de 10 km, faute de grille de population.

Ces chiffres sont nationaux : ils ne bougent pas avec la maille.

### Section 3 — Réseau et formation

**Nuage de points :**

- en abscisse, la part de routes en mauvais état (%) ;
- en ordonnée, les auto-écoles agréées pour 100 000 habitants ;
- taille du point : la population ; couleur : la priorité (palette `PRIORITE`) en maille préfectures, la couleur de la zone (`COULEUR_REGION`) en maille zones ou régions.

En maille préfectures, les 38 préfectures classées : Mô n’a aucune route classée, sa part en mauvais état est non définie. Elle n’est pas placée sur le graphique ; une note le dit en dessous.

**Seuil déplaçable** (11 §4.4), en maille préfectures : un curseur sur la part de routes en mauvais état, de 0 à 100 %, par défaut à **22,13 %**, le seuil du classement. Le graphique trace la ligne. La synthèse donne le nombre de préfectures au-delà et leur population : au seuil par défaut, **13 préfectures et 2 868 523 habitants**, les valeurs du 08. En maille zones ou régions, le curseur est masqué : les seuils y sont les médianes du 08, lues dans la colonne « Seuils franchis » du tableau (section 4).

**Niveau :** C (état relevé en 2020 ; activité des auto-écoles non publiée).

**Sources :** `classement_08.csv`, `regions_08.csv`, `prefectures_10.csv`.

### Section 4 — Les territoires

**Maille zones** (par défaut) :

| Zone                      | Rang | Population | Part en mauvais état | Auto-écoles pour 100 000 hab. | Km de routes pour 10 000 hab. | Km de routes pour 1 000 km² | Ruraux à moins de 2 km d’une route revêtue | Seuils franchis     | Levier réseau           | Levier formation                |
| ------------------------- | ---- | ---------- | --------------------- | ------------------------------ | ----------------------------- | ---------------------------- | --------------------------------------------- | ------------------- | ------------------------ | ------------------------------- |
| Centrale                  | 1    | 795 529    | 40,3 %                | 0,50                           | 5,73                          | 34,7                         | 13,2 %                                        | réseau, formation  | 4 préfectures, 113,6 km | 3 préfectures, 6 auto-écoles  |
| Savanes                   | 2    | 1 143 520  | 12,8 %                | 0,35                           | 4,62                          | 61,6                         | 16,9 %                                        | formation, desserte | —                       | 5 préfectures, 9 auto-écoles  |
| Plateaux                  | 3    | 1 635 946  | 28,0 %                | 0,55                           | 6,20                          | 58,2                         | 13,6 %                                        | réseau             | 6 préfectures, 150,5 km | 7 préfectures, 12 auto-écoles |
| Maritime hors Grand Lomé | 4    | 1 346 615  | 9,5 %                 | 0,37                           | 3,51                          | 79,0                         | 23,1 %                                        | formation, desserte | —                       | 3 préfectures, 6 auto-écoles  |
| Kara                      | 5    | 985 512    | 15,2 %                | 0,71                           | 7,40                          | 61,9                         | 17,5 %                                        | réseau             | 2 préfectures, 37,3 km  | 5 préfectures, 8 auto-écoles  |
| Grand Lomé               | 6    | 2 188 376  | 7,7 %                 | 4,71                           | 0,74                          | 397,2                        | sans population rurale                        | desserte            | 1 préfecture, 3,2 km    | —                              |

- **Seuils franchis :** au-dessus de la médiane des 6 zones pour le réseau, en dessous pour la formation et la desserte (colonnes « Réseau dégradé », « Formation faible », « Desserte faible » de `regions_08.csv`).
- **Rang :** colonne « Rang » de `regions_08.csv`, par la méthode du classement des préfectures.
- **Note sous le tableau :** « Les km de route par habitant baissent quand la densité monte : l’accès rural dit mieux qui est loin de la route. »

**Maille régions :**

| Région  | Rang | Population | Part en mauvais état | Auto-écoles pour 100 000 hab. | Km de routes pour 10 000 hab. | Seuils franchis     | Levier réseau           | Levier formation                |
| -------- | ---- | ---------- | --------------------- | ------------------------------ | ----------------------------- | ------------------- | ------------------------ | ------------------------------- |
| Centrale | 1    | 795 529    | 40,3 %                | 0,50                           | 5,73                          | réseau, formation  | 4 préfectures, 113,6 km | 3 préfectures, 6 auto-écoles  |
| Plateaux | 2    | 1 635 946  | 28,0 %                | 0,55                           | 6,20                          | réseau             | 6 préfectures, 150,5 km | 7 préfectures, 12 auto-écoles |
| Savanes  | 3    | 1 143 520  | 12,8 %                | 0,35                           | 4,62                          | formation, desserte | —                       | 5 préfectures, 9 auto-écoles  |
| Kara     | 4    | 985 512    | 15,2 %                | 0,71                           | 7,40                          | —                  | 2 préfectures, 37,3 km  | 5 préfectures, 8 auto-écoles  |
| Maritime | 5    | 3 534 991  | 9,2 %                 | 3,06                           | 1,79                          | desserte            | 1 préfecture, 3,2 km    | 3 préfectures, 6 auto-écoles  |

- **Seuils :** médianes des 5 régions (colonne « Note » de `regions_08.csv`). La Kara, au-dessus de la médiane des 6 zones pour le réseau, ne l’est plus parmi les 5 régions : le tableau l’affiche tel quel.
- **Colonnes par zone seulement :** les km pour 1 000 km² et l’accès rural ne sont calculés que par zone (`zones_10.csv`). En maille régions, ces colonnes sont absentes, avec la mention « par zone seulement » ; le tableau de bord ne les additionne pas.
- **Note de la Maritime :** section 1.

**Ce que dit le tableau, dans les deux mailles :** la Centrale est la seule zone, et la seule région, qui franchit les seuils du réseau et de la formation (08 §6).

**Export :** le tableau de la maille choisie, en CSV.

**Sources :** `regions_08.csv`, `zones_10.csv`.

### Section 5 — État du réseau par zone

Barres empilées des km par état, une barre par zone (`zones_10.csv`) :

| Zone                      | Bon état | État moyen | Mauvais état | Travaux | Non évalués | Part en mauvais état |
| ------------------------- | --------- | ----------- | ------------- | ------- | ------------- | --------------------- |
| Grand Lomé               | 37,1      | 18,2        | 7,6           | 34,9    | 16,7          | 7,7 %                 |
| Maritime hors Grand Lomé | 171,8     | 110,3       | 42,5          | 122,6   | 0,8           | 9,5 %                 |
| Plateaux                  | 356,2     | 204,0       | 270,7         | 134,6   | 18,9          | 28,0 %                |
| Centrale                  | 41,4      | 93,5        | 176,3         | 125,9   | 24,6          | 40,3 %                |
| Kara                      | 223,5     | 206,3       | 105,4         | 159,3   | 33,0          | 15,2 %                |
| Savanes                   | 167,0     | 103,2       | 66,8          | 184,2   | 4,8           | 12,8 %                |

En km. La part en mauvais état se calcule sur les km évalués (bon, moyen, mauvais, travaux). En maille régions, le bloc reste en 6 zones, avec la mention « par zone seulement ». Le détail par tronçon est en page 3, onglet Réseau.

**Niveau :** C. **Source :** `zones_10.csv`.

### Section 6 — Où sont les auto-écoles

**Concentration :** « Les 4 préfectures urbaines (Agoè-Nyivé, Golfe, Kloto, Kozah) ont 84,8 % des auto-écoles agréées pour 32,3 % de la population : 2,62 fois leur part. » Lu dans `hypotheses_09.csv` (mesure de la vérification sur la concentration urbaine). Niveau B.

**Distance à l’auto-école agréée la plus proche :**

- **Barres horizontales**, une par préfecture, triées par distance (`prefectures_10.csv`, colonne « Formation — distance à la plus proche (km) ») ; les 23 préfectures sans auto-école agréée en couleur pleine, les autres en couleur claire ; une ligne à 10 km.
- **Phrase :** « Le nombre laisse les 23 préfectures sans auto-école agréée toutes à zéro ; la distance les distingue : de 11,0 km (Agou) à 84,0 km (Oti-Sud). »
- **Niveau :** C. La distance part du chef-lieu (un point central pour 9 préfectures), à vol d’oiseau.

**Export :** les distances, en CSV.

### Section 7 — Les 39 préfectures

Tableau triable, une ligne par préfecture :

| Colonne                                                           | Source                                                                                                               |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Zone, région, population                                         | `prefectures_10.csv`                                                                                               |
| Part en mauvais état, km évalués                               | `prefectures_10.csv`                                                                                               |
| Part du réseau national non évaluée                            | `classement_08.csv` (de 0 à 20,0 %, à Agoè-Nyivé ; aucune au-delà de 25 %)                                    |
| Auto-écoles agréées ; auto-écoles recensées                  | `prefectures_10.csv`                                                                                               |
| Auto-écoles pour 100 000 habitants                               | `classement_08.csv`                                                                                                |
| Distance à l’auto-école agréée la plus proche                | `prefectures_10.csv`                                                                                               |
| Km de routes pour 10 000 habitants ; desserte faible (oui ou non) | `prefectures_10.csv` ; `classement_08.csv` (14 préfectures à 3,68 km pour 10 000 habitants ou moins, dont Mô) |
| Accès rural                                                      | `prefectures_10.csv`                                                                                               |
| Priorité                                                         | `prefectures_10.csv`                                                                                               |

- Mô : part en mauvais état « non définie (aucune route classée) ».
- Golfe et Agoè-Nyivé : accès rural « sans population rurale ».
- Une valeur nulle mesurée s’écrit 0 (par exemple, 0 auto-école agréée dans 23 préfectures).

**Export :** le tableau, en CSV.

### Section 8 — Points d’attention

Cinq repères de l’exploration (06 §7), qu’aucun autre bloc ne montre. Chaque point a un titre, fixé par ce plan, puis le texte lu dans `signaux_06.csv` : la colonne « Résumé », à partir du deuxième deux-points. Le code du signal ne s’affiche pas.

| Titre affiché                                                                      | Texte lu dans le résumé du signal                                           | Signal lu |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------- |
| Une seule auto-école agréée : si elle ferme, la préfecture n’en a plus         | Anié, Assoli, Cinkassé, Kpélé, Zio (956 482 habitants)                    | SIG-43    |
| La plus peuplée des préfectures sans auto-école agréée                         | Haho (305 096 habitants)                                                      | SIG-31    |
| Peu de routes et peu d’auto-écoles par habitant                                   | Akébou, Dankpen, Mô, Tandjoaré (450 807 habitants)                         | SIG-30    |
| Un seul tronçon relevé, ou aucune route classée                                  | Tandjoaré (138 867 habitants) ; sans route classée : Mô (52 448 habitants) | SIG-44    |
| Zones où plus de ménages ont une moto que la médiane, avec moins d’auto-écoles | Centrale, Savanes                                                             | SIG-35    |

- **Phrase d’introduction :** « Ces repères viennent de l’exploration des données. Ils ne sont pas des seuils de décision et ne changent pas le classement. »
- **Niveau :** C, pour les cinq.
- **Réserve du dernier point**, affichée sous lui : « D’après une seule enquête auprès des ménages (2021-2022) ; l’ordre des zones change d’une enquête à l’autre. » (06 §5.)
- **Signaux écartés de ce bloc :** « population forte, peu de km par habitant » (Agoè-Nyivé, Golfe, Tône, Vo, Zio), que le 10 §4.6 a montré biaisé par la densité ; « réseau correct, état mauvais » (9 préfectures), déjà porté par le levier réseau.

### Section 9 — Constat, synthèse chiffrée et limite

**Constat :** « La Centrale est la seule zone, et la seule région, qui cumule un réseau dégradé et un déficit de formation. »

**Synthèse chiffrée :** 13 préfectures au réseau dégradé (2 868 523 habitants) ; 23 préfectures sans auto-école agréée (2 932 492 habitants) ; 26 dont le chef-lieu est à plus de 10 km d’une auto-école agréée (3 482 856 habitants) ; 5 qui cumulent réseau dégradé et aucune auto-école agréée (641 955 habitants).

**Limite :** « État du réseau relevé en 2020 (niveau C) ; activité des auto-écoles non publiée ; accès rural estimé avec une population répartie uniformément dans chaque préfecture. La vue par région fond la Maritime hors Grand Lomé dans le Grand Lomé : la vue par zone est la lecture par défaut. »

**Sources de la page :** `classement_08.csv`, `regions_08.csv`, `prefectures_10.csv`, `zones_10.csv`, `indicateurs_07.csv`, `hypotheses_09.csv`, `signaux_06.csv`.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
