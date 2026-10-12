

## Page 4 — Carte du réseau et des auto-écoles

**Nom dans le menu :** « Carte du réseau et des auto-écoles ». Il reprend l’objectif 4 ; il tient sur deux lignes dans le menu.

**Objectif :** voir les 39 préfectures sur fond cartographique, une couche à la fois, avec les routes classées, l’état des tronçons relevés, les auto-écoles et, en option, les équipements de sécurité routière.

**Objectifs du projet :**

- **objectif 4, principal :** c’est la seule page qui dessine, préfecture par préfecture, le réseau classé et les auto-écoles, rapportés à la population ;
- **objectif 3, en partie :** l’état du réseau par préfecture et sur le tracé ; le détail chiffré par tronçon est en page 3, onglet Réseau ;
- **objectif 5, en appui :** la couche Priorité montre où agir ; ce qu’il faut faire est en pages 5 et 6 ;
- **objectifs 1 et 2 :** pas de données par territoire ; l’encadré « Ce que la carte ne montre pas » le dit (section 11).

**Question :** « Que voit-on, préfecture par préfecture ? »

**Réponse sous le titre** (11 §4.3) : « Le mauvais état du réseau se concentre au centre du pays (40,3 % des km évalués dans la Centrale) ; 103 des 132 auto-écoles agréées sont dans le Grand Lomé, et 26 préfectures ont leur chef-lieu à plus de 10 km de la plus proche. » Chiffres lus dans `regions_08.csv` (Centrale, ligne de zone, part en mauvais état ; Grand Lomé et pays, auto-écoles agréées) et `indicateurs_07.csv` (distance à l’auto-école la plus proche, ligne nationale).

**Maquette validée :** https://claude.ai/artifact/86jNwbm69MZ9LdXZA3od63 (version 2).

```text
┌──────────────────────────────────────────────────────────────────┐
│  QUE VOIT-ON, PRÉFECTURE PAR PRÉFECTURE ?   + réponse             │
├──────────────────────────────────────────────────────────────────┤
│  [RÉSEAU DÉGRADÉ] [AUTO-ÉCOLES] [SANS AUTO-ÉCOLE] [ÉQUIPEMENTS]   │
├──────────────────────────────────────────────────────────────────┤
│  [Couche : 8]  [État : 5]  [Territoire : zone ou région]          │
│  [Tracé : 3]  [Auto-écoles]  [Équipements : 4 types]              │
├──────────────────────────────────────────────────────────────────┤
│                                                     │ CONSTAT     │
│  [CARTE DU PAYS]          [ENCART GRAND LOMÉ]       │ LÉGENDE     │
│  [NIVEAU] [EXPORT]   [FICHE DE LA PRÉFECTURE]       │ NIVEAU      │
├──────────────────────────────────────────────────────────────────┤
│  [LES 8 COUCHES, PRÉFECTURE PAR PRÉFECTURE]               (CSV)   │
│  [LES 272 AUTO-ÉCOLES RECENSÉES]                          (CSV)   │
│  [CE QUE LA CARTE NE MONTRE PAS]                                  │
│  [SYNTHÈSE CHIFFRÉE]  [LIMITE]                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Section 1 — 4 chiffres clés

Une rangée de 4 cartes de chiffre clé (maquette §8.4), au-dessus des réglages de la carte.

| Carte | Valeur | Phrase et contexte | Réserve | Niveau | Source |
| ----- | ------ | ------------------ | ------- | ------ | ------ |
| **Préfectures au réseau dégradé** | 13 sur 38 évaluées | Plus de 22,13 % de leurs routes évaluées en mauvais état ; 2 868 523 habitants y vivent | Mô n’a aucune route classée : 38 préfectures évaluées sur 39. Relevé de 2020 | C | `regions_08.csv` (ligne du pays : préfectures et population au levier réseau) ; `controles_08.csv` (seuil et « sur 38 », contrôle 9-02) |
| **Auto-écoles recensées** | 272 | 132 agréées, 138 non agréées, 2 au statut non renseigné ; barre de répartition : 85 agréées, 47 antennes agréées, 138 non agréées, 2 non renseignées | Activité non publiée : aucune auto-école n’est vérifiée en activité | A | `geo/auto_ecoles.geojson` (nombre de points par statut ; contrôle au 11 §7) |
| **Préfectures sans auto-école agréée** | 23 sur 39 | 2 932 492 habitants y vivent ; dont 15 sans aucune auto-école recensée (1 822 046 habitants). Chaque zone et chaque région en a au moins 4 | Activité des auto-écoles non publiée | B | `indicateurs_07.csv` (préfectures sans auto-école, ligne nationale) ; `regions_08.csv` (auto-écoles agréées par zone et par région) |
| **Équipements de sécurité routière** | 16 797 | 9 089 panneaux, 6 121 ralentisseurs, 1 041 passages piétons, 546 feux tricolores. Réseau classé : 3 361 km ; les équipements n’y sont pas rapportés, car la couche couvre aussi les rues non classées | Collecte 2021-2022, non vérifiée ; hors indicateurs | C | `geo/equipements.geojson` (nombre de points par type) ; `regions_08.csv` (km de routes classées, ligne du pays) |

- **Réseau :** la carte compte les préfectures au-delà du seuil du classement. Compter celles qui ont au moins un km en mauvais état ne distinguerait rien : 36 sur 38.
- **Activité des auto-écoles :** elle n’est pas publiée (écart 13). Le fichier ne donne que des jours d’ouverture déclarés, pour 256 auto-écoles sur 272 : ce n’est pas une preuve d’activité.
- **Équipements :** aucun ratio par km de route classée. Seuls 39,8 % des équipements sont à moins de 50 m d’une route classée, et 13,6 % des ralentisseurs (vérification faite pour ce plan, non affichée). Les équipements restent hors indicateurs (03 §3.2).

### Section 2 — Réglages de la carte

| Réglage | Choix | Par défaut |
| ------- | ----- | ---------- |
| **Couche** | Liste groupée : Réseau (état du réseau, km de routes pour 10 000 habitants, densité routière, accès rural) ; Formation (auto-écoles agréées pour 100 000 habitants, distance à l’auto-école agréée la plus proche) ; Population ; Pilotage (priorité) | État du réseau |
| **État** (avec la couche État du réseau) | Mauvais, Bon, Moyen, Travaux, Non évalué | Mauvais |
| **Territoire** | Tout le pays ; 6 zones ; 5 régions (R-02, R-03) | Tout le pays |
| **Tracé** | Aucun ; Routes classées par type ; État des tronçons relevés | Routes classées par type |
| **Auto-écoles** | Affichées ou masquées | Affichées |
| **Équipements de sécurité routière** | Masqués, ou un type à la fois (panneaux, ralentisseurs, passages piétons, feux tricolores), avec la mention « non utilisée dans les indicateurs » | Masqués |

### Section 3 — Les 8 couches

Une couche à la fois, en 5 classes fixes de la palette `BLEUS` (la priorité, en palette `PRIORITE`). La légende montre toujours les 5 classes, avec leur effectif, même vides (maquette §8.14).

| Couche | Unité | 5 classes | Valeurs | Valeur absente | Niveau | Source |
| ------ | ----- | --------- | ------- | -------------- | ------ | ------ |
| **État du réseau : mauvais** (par défaut) | % des km évalués | moins de 10 ; 10 à 25 ; 25 à 40 ; 40 à 60 ; 60 ou plus | de 0,0 (Dankpen, Moyen-Mono) à 100 (Danyi) | Mô : non définie, aucune route classée | C | `prefectures_10.csv` |
| État du réseau : bon | % des km évalués | mêmes classes | de 0,0 (Danyi) à 78,9 (Vo) | Mô | C | `prefectures_06.csv` |
| État du réseau : moyen | % des km évalués | mêmes classes | de 0,0 (Danyi) à 68,7 (Est-Mono) | Mô | C | `prefectures_06.csv` |
| État du réseau : travaux | % des km évalués | mêmes classes | de 0,0 (10 préfectures) à 78,5 (Moyen-Mono) | Mô | C | `indicateurs_07.csv` (part des km en travaux) |
| État du réseau : non évalué | % des km de routes nationales | 0 % ; moins de 5 ; 5 à 10 ; 10 à 15 ; 15 ou plus | de 0 (25 préfectures) à 20,0 (Agoè-Nyivé) | Mô | B | `indicateurs_07.csv` (part du réseau non évaluée) |
| Population | habitants, 2022 | moins de 100 000 ; 100 000 à 150 000 ; 150 000 à 200 000 ; 200 000 à 300 000 ; 300 000 ou plus | de 40 240 (Danyi) à 1 305 681 (Golfe) | — | A | `prefectures_10.csv` |
| Km de routes classées pour 10 000 habitants | km | moins de 2 ; 2 à 4 ; 4 à 6 ; 6 à 10 ; 10 ou plus | de 0 (Mô) à 15,17 (Agou) | — | B | `prefectures_10.csv` |
| Densité routière | km pour 1 000 km² | moins de 40 ; 40 à 60 ; 60 à 100 ; 100 à 150 ; 150 ou plus | de 0 (Mô) à 401,9 (Golfe) | — | B | `indicateurs_07.csv` (densité routière) |
| Accès rural à une route revêtue | % des ruraux à moins de 2 km | moins de 5 ; 5 à 10 ; 10 à 20 ; 20 à 30 ; 30 ou plus | de 0,0 (Mô) à 45,8 (Lacs) | Golfe et Agoè-Nyivé : sans population rurale | C | `prefectures_10.csv` |
| Auto-écoles agréées pour 100 000 habitants | auto-écoles | aucune ; moins de 1 ; 1 à 2 ; 2 à 3 ; 3 ou plus | de 0 (23 préfectures) à 5,67 (Golfe) | — | C | `classement_08.csv` |
| Distance à l’auto-école agréée la plus proche | km à vol d’oiseau | moins de 5 ; 5 à 10 ; 10 à 25 ; 25 à 50 ; 50 ou plus | de 0,2 (Golfe, Kloto) à 84,0 (Oti-Sud) | — | C | `prefectures_10.csv` ; points de départ : `D13_points_depart_o4_08.csv` |
| Priorité | haute, moyenne, aucune action | `PRIORITE` : `#0d366b`, `#3987e5`, `#b9b6ad` | 5 haute, 26 moyenne, 8 sans action | — | C | `prefectures_10.csv` |

- **Valeurs absentes :** en gris `#b9b6ad`, avec leur mention ; jamais colorées comme 0. Une valeur nulle mesurée (0 auto-école agréée, 0 % de travaux) reste dans la première classe.
- **Territoire choisi :** les préfectures hors du territoire passent en `#ebe8e0` ; la légende compte les préfectures du territoire.
- **Distance :** la classe « 5 à 10 km » s’arrête au seuil d’éloignement du classement (10 km). La couche dessine les points de départ : un rond jaune pour un chef-lieu (30 préfectures), un losange pour un point central (9 préfectures sans chef-lieu dans les données).
- **Densité :** rapportée à la surface, pas aux habitants. Le Grand Lomé a beaucoup de routes au km², mais peu par habitant ; la note de la couche le dit.

### Section 4 — Points, tracés et limites

- **Limites des 5 régions :** toujours tracées, en bande grise large (`rgba(20,20,19,.38)`, 3,4 px), sous les routes. En trait noir fin, on les confondait avec les routes nationales revêtues.
- **Territoire choisi :** cerclé de noir, 3 px.
- **Tracé « Routes classées par type »** (par défaut), lu dans `geo/routes_classees.geojson`. Il est en noir et gris, sans couleur : le vert, le jaune, le rouge et le bleu sont réservés aux états, et une route bleue se perd sur le fond. Chaque trait a un liseré blanc pour rester lisible sur toutes les classes.

| Type | Trait | Tronçons | Km |
| ---- | ----- | -------- | -- |
| Route nationale revêtue | plein, `#141413`, 1,7 px | 398 | 2 236,4 |
| Route nationale non revêtue | tirets, `#141413`, 1,3 px | 196 | 863,1 |
| Voirie urbaine | plein, `#55534e`, 0,9 px | 192 | 233,2 |
| Piste rurale | pointillés, `#55534e`, 1,2 px | 13 | 33,8 |

- **Tracé « État des tronçons relevés »**, lu dans `D4_etat_troncons.csv` (colonne « Noms du tracé ») et `geo/routes_classees.geojson` :
  - les 49 tronçons en mauvais état en rouge `#e34948`, épaisseur de 1,2 à 5 px selon les km en mauvais état, comme sur la carte de la page 3 ;
  - les 35 autres tronçons relevés en gris foncé `#55534e` ;
  - les routes nationales sans état relevé (99,0 km) en tirets gris clair `#b9b6ad`, « non évaluées », jamais « en bon état ».

  Chaque tronçon est rattaché au tracé par son nom (04 §5, `correspondance_etat_trace.csv`) : le tableau de bord choisit les lignes dont le nom figure dans « Noms du tracé », c’est une sélection, pas un calcul. Pour 7 tronçons rattachés par l’axe, l’état est réparti le long de l’axe. **Info-bulle d’un tronçon :** son nom réécrit (11 §4.2), ses km relevés et ses km dans les 4 états, les préfectures traversées, et « état réparti le long de l’axe » s’il y a lieu.
- **Auto-écoles** (affichées par défaut), lues dans `geo/auto_ecoles.geojson` : les 132 agréées (85 agréées, 47 antennes agréées) en blanc cerclé de noir ; les 138 non agréées et les 2 au statut non renseigné en gris `#8a8780`. Info-bulle : statut et préfecture.
- **Équipements de sécurité routière** (facultatifs, masqués par défaut), lus dans `geo/equipements.geojson` : un type à la fois, en points orange `#eb6834`, avec la mention « non utilisée dans les indicateurs » (03 §3.2 et §10). Les passages piétons, publiés en polygones, sont montrés par un point intérieur du polygone : une transformation d’affichage, comme le sens des contours (section 5), pas un calcul d’indicateur. Info-bulle : type et préfecture, ou « hors des 39 préfectures » pour les 29 points hors des limites.
- **Encart du Grand Lomé :** à droite de la carte du pays, dans sa moitié basse, avec les mêmes couches. Un cadre pointillé marque sa zone sur la carte du pays.

### Section 5 — Réglages de la figure

Ceux de la carte des constats de la page 3 (maquette §8.14) : projection Mercator, sans fond de carte, cadrage explicite sur le Togo (± 0,05°) ; contours blancs de 0,8 px ; hauteur 620 px ; survol et clic, sans zoom. Les anneaux extérieurs des contours sont dans le sens des aiguilles d’une montre, que la cartographie de Plotly attend.

Deux cartes dans la même figure : le pays (52 % de la largeur) et l’encart du Grand Lomé (44 %, moitié basse), avec le titre « Grand Lomé, agrandi · Golfe et Agoè-Nyivé ».

### Section 6 — Info-bulle d’une préfecture

**Toujours :** nom, zone et région, population ; valeur de la couche active, ou sa mention si elle est absente ; leviers et priorité ; « Cliquez pour afficher sa fiche ».

**Selon la couche :**

| Couche | Lignes ajoutées | Source |
| ------ | --------------- | ------ |
| État du réseau | km évalués, tronçons relevés, tronçons critiques ; km en bon état, moyen, mauvais, en travaux et non évalués | `prefectures_10.csv`, `prefectures_06.csv` (tronçons du relevé), `indicateurs_07.csv` (km par état) |
| Km pour 10 000 habitants | km de routes classées | `prefectures_06.csv` |
| Densité routière | km de routes classées et surface | `prefectures_06.csv` |
| Accès rural | population rurale | `prefectures_10.csv` |
| Auto-écoles pour 100 000 habitants | agréées sur recensées | `prefectures_10.csv` |
| Distance | point de départ (chef-lieu ou point central), préfecture de l’auto-école la plus proche ; agréées sur recensées | `prefectures_06.csv`, `prefectures_10.csv` |
| Priorité | km à remettre en état, auto-écoles à ouvrir | `prefectures_10.csv` |

Les km évalués et le nombre de tronçons relevés évitent de lire un pourcentage calculé sur peu de km : Agoè-Nyivé, 26,0 % sur 27,8 km ; Tandjoaré, un seul tronçon relevé ; Danyi, 100 % sur 49,8 km (06, points d’attention).

### Section 7 — Fiche de la préfecture choisie

Un clic sur une préfecture, sur la carte ou dans le tableau des 8 couches, l’affiche sous la carte (`st.plotly_chart` avec `on_select`) :

- nom, zone et région, population ;
- priorité, en pastille `PRIORITE`, et leviers ;
- actions recommandées (`prefectures_10.csv`, colonne `Actions`, réécrite selon 11 §4.2) ;
- un bouton « Voir la fiche de <préfecture> → ». Il écrit la préfecture dans `st.session_state["fiche_prefecture"]` et le rang de l’onglet dans `st.session_state["recommandations_rang"]` (7, « Actions par zone »), puis appelle `st.switch_page` vers la page 6, qui s’ouvre sur cet onglet, filtrée sur la préfecture (design-page6.md, section 5).

Sans clic : « Cliquez sur une préfecture : elle s’affiche ici, avec ses actions et un lien vers sa fiche. »

### Section 8 — Constat, légende et niveau

**Constat**, à côté de la carte : il change avec la couche affichée, et avec l’état pour la couche État du réseau. Son titre nomme la couche (« Constat · État du réseau · mauvais »).

| Couche | Constat | Sources |
| ------ | ------- | ------- |
| État : mauvais | « Le réseau le plus dégradé est au centre du pays : la Centrale a 40,3 % de ses routes en mauvais état, et Danyi, 100 % de ses 49,8 km évalués. » | `regions_08.csv` (Centrale), `prefectures_10.csv` |
| État : bon | « Vo a 78,9 % de ses routes évaluées en bon état, Haho 71,5 % ; à Danyi, aucun km n’est en bon état. » | `prefectures_06.csv` |
| État : moyen | « L’état moyen domine à Est-Mono (68,7 %) et à Binah (61,9 %) : plus de la moitié de leurs routes évaluées. » | `prefectures_06.csv` |
| État : travaux | « En 2020, des travaux couvraient 78,5 % des routes évaluées de Moyen-Mono et 70,4 % de celles d’Avé ; 10 préfectures n’en avaient aucun. » | `indicateurs_07.csv` |
| État : non évalué | « Le relevé couvre presque tout le réseau national : 3,2 % des km sont sans état, surtout à Agoè-Nyivé (20,0 %) et à Blitta (19,8 %) ; 25 préfectures sont entièrement évaluées. » | `regions_08.csv` (ligne du pays), `indicateurs_07.csv` |
| Population | « Le Grand Lomé, Golfe et Agoè-Nyivé, regroupe 27,0 % de la population du pays ; Danyi, la moins peuplée, a 40 240 habitants. » | `rapports_06.csv` (part de la population, Grand Lomé), `prefectures_10.csv` |
| Km pour 10 000 habitants | « Les préfectures les plus peuplées ont le moins de routes par habitant : 0,74 km pour 10 000 habitants dans le Golfe et à Agoè-Nyivé, contre 15,17 à Agou ; Mô n’a aucune route classée. » | `prefectures_10.csv` |
| Densité routière | « Le Grand Lomé a le réseau le plus dense : 401,9 km pour 1 000 km² dans le Golfe, 390,5 à Agoè-Nyivé ; Akébou n’en a que 6,1, et Mô aucune route classée. » | `indicateurs_07.csv` |
| Accès rural | « 17,2 % des ruraux vivent à moins de 2 km d’une route revêtue : de 45,8 % aux Lacs à 0,6 % à Akébou, et aucun à Mô. » | `zones_10.csv` (ligne du pays), `prefectures_10.csv` |
| Auto-écoles pour 100 000 habitants | « 23 préfectures sur 39 n’ont aucune auto-école agréée (2 932 492 habitants) ; le Golfe en a 5,67 pour 100 000 habitants. » | `indicateurs_07.csv`, `classement_08.csv` |
| Distance | « 26 préfectures ont leur chef-lieu à plus de 10 km de l’auto-école agréée la plus proche (3 482 856 habitants) ; jusqu’à 84,0 km pour Oti-Sud. » | `indicateurs_07.csv`, `prefectures_10.csv` |
| Priorité | « 5 préfectures sont en priorité haute : Danyi, Blitta, Agou, Tchamba et Bassar cumulent un réseau dégradé et un manque d’auto-écoles (641 955 habitants). » | `prefectures_10.csv`, `recommandations_10.csv` (population concernée de la recommandation sur ces 5 préfectures) |

**Légende**, sous le Constat :

- le titre et l’unité de la couche ; les 5 classes, avec leurs bornes et leur effectif ; les valeurs absentes, avec leur mention ; « hors du territoire choisi » quand un filtre est actif ;
- le niveau de preuve de la couche, avec sa légende (A = mesuré, B = calculé, C = estimé) ;
- « Sur la carte » : le symbole de chaque élément affiché (limites des régions, territoire choisi, tracé, points de départ, auto-écoles, équipements), avec son nombre ou ses km.

**Sous la carte :** le niveau et la note de la couche (par exemple : « Relevé de 2020, routes nationales seulement ; part des km évalués de la préfecture ») ; le bouton « Télécharger la couche (CSV) ».

### Section 9 — Les 8 couches, préfecture par préfecture

La carte en tableau, avant la synthèse chiffrée. Une ligne par préfecture (39), 15 colonnes :

- Préfecture ; Zone, avec une pastille de la couleur de la zone (palette `COULEUR_REGION`, 11 §4.1) ; Région ;
- Population ; état du réseau en 5 colonnes (mauvais, bon, moyen, travaux, non évalué) ; km pour 10 000 habitants ; km pour 1 000 km² ; accès rural ; auto-écoles agréées pour 100 000 habitants ; distance ; priorité.

**Règles :**

- chaque case a la couleur de sa classe sur la carte, avec un texte blanc sur les deux classes les plus foncées ; une valeur absente est sur fond `#ebe8e0`, avec « non défini » ou « sans ruraux », et sa mention complète au survol ; la priorité est en pastille `PRIORITE` ;
- la colonne de la couche affichée est soulignée ;
- le tableau suit le filtre du territoire ; il se trie par colonne ; par défaut, les préfectures sont groupées par zone (ordre de R-02), puis par nom ;
- un clic sur une ligne affiche la fiche de la préfecture (section 7).

**Sources :** celles des couches (section 3).

**Pas de ligne par zone ni par région :** les valeurs par zone et par région, avec leurs seuils, sont en page 2 (section 4), et deux couches n’existent qu’à la préfecture (distance, priorité). Le tableau recoupe celui de la page 2 (section 7, « Les 39 préfectures ») ; ici, il reprend les classes et les couleurs de la carte, la page 2 garde les seuils et la desserte faible.

**Export :** le tableau, en CSV (valeurs sans couleurs, colonnes Zone et Région comprises).

### Section 10 — Les 272 auto-écoles recensées

Une ligne par auto-école, lue dans `geo/auto_ecoles.geojson` ; la population vient de `prefectures_10.csv`, les habitants par auto-école agréée de `indicateurs_07.csv`.

| Colonne | Source et règle |
| ------- | --------------- |
| Auto-école | `Nom` |
| Statut | `Statut`, en pastille : agréée (`#0d366b`), antenne agréée (`#e3eefb`), non agréée (gris), non renseigné (contour) |
| Localité, commune, canton | `Localité`, `Commune`, `Canton` |
| Préfecture | `Préfecture` : le rattachement par la position, utilisé par tous les indicateurs. Il diffère de la préfecture déclarée pour 4 auto-écoles, entre le Golfe, Agoè-Nyivé et Zio |
| Zone, région | `Zone`, avec la pastille de sa couleur ; `Région` |
| Population de la préfecture | `prefectures_10.csv` |
| Habitants par auto-école agréée de la préfecture | `indicateurs_07.csv` (habitants par auto-école), en 5 classes `BLEUS` : moins de 25 000 ; 25 000 à 50 000 ; 50 000 à 100 000 ; 100 000 à 150 000 ; 150 000 ou plus. « Aucune agréée », en pastille ocre, dans les 23 préfectures sans auto-école agréée |

- **À vérifier, en couleur :** les 13 auto-écoles non agréées des 8 préfectures qui n’en ont aucune d’agréée (Oti 3 ; Bassar, Blitta, Tchamba 2 chacune ; Agou, Amou, Bas-Mono, Yoto 1 chacune). Fond ocre clair, liseré `#eda100`, mention « aucune agréée : à vérifier ». Leur fiche demande de vérifier leur activité et leur agrément (`prefectures_10.csv`).
- **Filtres :** territoire (il suit celui de la carte), statut (dont « à vérifier »), recherche par nom, localité ou commune.
- **Tri :** par colonne ; par défaut, par zone, préfecture, statut (agréées d’abord), puis nom.
- **Compte sous le tableau :** auto-écoles affichées, agréées (dont antennes), non agréées, au statut non renseigné, à vérifier.
- **Export :** la liste, en CSV, avec la longitude et la latitude.

**Écartés :**

- **la distance de chaque auto-école au chef-lieu :** aucune analyse du 04 au 10 ne la calcule, le tableau de bord ne calcule pas (11 §4.4), et 9 préfectures n’ont pas de chef-lieu dans les données. La distance qui compte pour l’accès est celle de la couche Distance : du chef-lieu à l’auto-école agréée la plus proche ;
- **la population autour de chaque auto-école :** la population n’existe que par préfecture. Une grille de population (WorldPop, recensée, non téléchargée) le permettrait : c’est une piste de l’annexe A1 ;
- **l’activité :** non publiée (écart 13) ; les jours d’ouverture déclarés (256 sur 272) ne la prouvent pas ;
- **l’adresse :** renseignée pour 101 auto-écoles sur 272, surtout par des numéros de téléphone.

### Section 11 — Ce que la carte ne montre pas

- **Les accidents, les tués et les blessés :** publiés pour tout le pays seulement. Ils sont en page 3, onglet Sécurité routière.
- **Les permis et les immatriculations :** publiés pour tout le pays seulement. Ils sont en page 3, onglet Mobilité.
- **Le risque par préfecture :** il n’est pas classé, faute d’accidents par territoire. La priorité ne porte que sur le réseau et la formation.
- **L’accès aux secours, le trafic et la vitesse :** aucune donnée.

### Section 12 — Synthèse chiffrée et limite

**Synthèse chiffrée :** 21,2 % des km évalués en mauvais état dans le pays (669,34 km sur 3 163 km) ; 13 préfectures au-delà du seuil de 22,13 % ; Mô sans route classée. Sources : `regions_08.csv` (ligne du pays), `controles_08.csv` (seuil).

**Limite :** « État relevé en 2020, sur les routes nationales seulement. Accès rural estimé avec une population répartie uniformément dans chaque préfecture. Distance à vol d’oiseau, depuis le chef-lieu ou un point central. Équipements recensés en 2021-2022, non vérifiés, hors indicateurs. »

**Sources de la page :** `geo/prefectures.geojson`, `geo/routes_classees.geojson`, `geo/auto_ecoles.geojson`, `geo/equipements.geojson`, `prefectures_10.csv`, `recommandations_10.csv`, `zones_10.csv`, `classement_08.csv`, `regions_08.csv`, `controles_08.csv`, `indicateurs_07.csv`, `prefectures_06.csv`, `rapports_06.csv`, `D4_etat_troncons.csv`, `D13_points_depart_o4_08.csv`.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages.

---
