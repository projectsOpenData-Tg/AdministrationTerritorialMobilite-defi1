# Journal de développement — tableau de bord

Suivi horodaté du codage de `dashboard/` (Streamlit), pour que tout développeur du projet voie ce qui est fait, les
bugs rencontrés et comment ils ont été résolus. Référence : `11_tableau_de_bord.md`, `workspace/design-pageX.md`,
`methodology/MAQUETTE_dashboard.md`, `_CONSTRAINTS_DEV.txt`.

---

## 2026-10-08

### Ossature posée
- **Arborescence** `dashboard/` créée : `app.py`, `theme.py`, `composants.py`, `donnees.py`, `views/` (8 pages),
  `static/`, `.streamlit/config.toml`, `data/` (vide, pour la copie du livrable).
- **`config.toml`** : thème de la maquette (fond crème, barre latérale bleu nuit) ; `enableStaticServing = true`
  (sert `static/` sous `app/static/<fichier>`) ; `toolbarMode = "minimal"`.
- **`theme.py`** : CSS complet repris de la maquette (§2 à §8), adapté à notre palette (11 §4.1, respectée strictement :
  priorités, thèmes des objectifs, états du réseau, couleur par zone) et au français seul. Inclut la règle anti-topbar
  Streamlit Cloud (maquette §4 : `body:has([data-testid="stHeader"] [data-testid="stToolbar"]) … { padding-top: 4.4rem }`).
- **`composants.py`** : topbar (armoiries + ministère · nom + drapeau 🇹🇬 · carte logo Togo AI Lab), **sans sélecteur
  FR/EN** (bilingue abandonné) ; en-tête, chiffres clés, constat, synthèse, limite, onglets, export CSV, choroplèthe,
  pied. Repli 🛡️ si l'armoirie manque, repli « TOGO AI LAB » si le PNG du logo manque.
- **`donnees.py`** : lecture des tables `data/analysis/` et des couches `data/processed/geo/` ; aucun recalcul.
  Lit le dépôt en développement, `dashboard/data/` en priorité si présent (livrable).
- **`app.py`** : 8 pages en 4 groupes (Principal, Analyses, Pilotage, Méthodologie) via `st.navigation()` ; filtres
  globaux dans la barre latérale (Zone, Priorité, Levier) ; topbar rendue une fois avant la navigation.
- **Armoiries** : `armoiries-togo-ecu.svg` + `README_armoiries.md` copiés de `EconomyNumeric-Challenge2`
  (CC BY-SA 4.0, Edem Fiadjoe — attribution à mettre en page Méthodologie).

### Environnement
- `streamlit==1.61.0` et `plotly==7.1.0` installés dans `.venv`. À ajouter au `requirements.txt` du livrable.
  NB : la maquette visait plotly 5.15+ ; 7.1 fonctionne, à surveiller pour d'éventuelles ruptures d'API.

### Vérifié
- L'application démarre sans erreur (HTTP 200) : topbar, barre latérale, menu 8 pages, filtres.
- Les 8 vues sont des **stubs** (ariane + en-tête + pied) ; contenu à construire page par page.

### Page 1 — Vue nationale : construite et vérifiée ✅
- 6 chiffres clés (2 rangées de 3) avec badges A/B/C ; valeurs lues dans `indicateurs_07.csv` et `regions_08.csv`,
  toutes conformes à `design-page1.md`.
- Carte du Togo avec sélecteur de couche (Population / Auto-écoles / Routes classées) : choroplèthe population +
  overlay de points auto-écoles (agréées vs non) + tracé des routes par type. Encart « permis nationaux ».
- 4 cartes de thème (Mobilité, Sécurité, Réseau, Couverture) avec boutons « Voir le détail → » : `st.switch_page`
  vers les pages de détail, et `evolutions_rang` écrit pour ouvrir le bon onglet de la page Évolutions.
- Permis 2024 : barres horizontales par catégorie + grand chiffre 38 531.
- Immatriculations et permis 1990–2024 : figure à deux étages (`make_subplots`, deux légendes `legend`/`legend2`),
  couleur par famille de véhicules, trou de 2013 (`connectgaps=False`), repères de contexte (`add_vline`).
- Messages « À retenir », synthèse chiffrée (×4,56), limite.
- **Vérifié par capture d'écran (Playwright)** : rendu complet sans exception ; topbar (armoiries + 🇹🇬 + carte logo),
  barre latérale (8 pages, filtres), KPIs, carte, graphiques, pied.

### Bugs rencontrés et corrigés
- `KeyError: ['Zone'] not in index` : `indicateurs_07.csv` n'a pas de colonne Zone. Corrigé en lisant la zone et la
  population dans `table_maitresse_prefecture.csv` (nouvelle fonction `donnees.lire_tm()`).
- Helper de fenêtre de carte renommé `fenetre_geo` (public) dans `composants.py` pour être réutilisable par les vues.

### Outils de dev
- `playwright` + chromium installés dans `.venv` pour les captures d'écran de vérification (non requis par le livrable).

## 2026-10-08 (suite) — pages 2 à 8 construites

Les 7 pages restantes sont construites et vérifiées. Toutes lisent des CSV/GeoJSON déjà produits (aucun recalcul,
sauf les deux curseurs de seuil admis par la maquette : poids du réseau page Priorités, seuil mauvais état page
Comparaison).

- **Page 2 — Comparaison territoriale** : maille zones/régions/préfectures ; nuage réseau×formation (curseur de seuil
  en préfectures) ; tableaux par territoire ; état du réseau par zone (barres empilées) ; distance aux auto-écoles ;
  tableau des 39 ; 5 points d'attention (signaux_06) ; synthèse/limite.
- **Page 3 — Évolutions et constats** : 4 onglets via `onglets("evolutions", …)`. Synthèse (17 vérifications de
  hypotheses_09 + conséquences_11) ; Mobilité (immat volume/part/pour 1000, permis, ratio cumul, parc estimé) ;
  Sécurité routière (6 taux de taux_09, séries annuelles, OMS, usagers 2021) ; Réseau (84 tronçons de
  D4_etat_troncons, par zone, annuaire national). Helpers `nettoyer()` (retrait des codes/renvois, 11 §4.2) et
  `nom_troncon()` (retrait du code « TGR… »).
- **Page 4 — Carte** : 4 chiffres clés ; sélecteur de 7 couches (choroplèthe) + superpositions routes et auto-écoles
  agréées ; constat par couche ; tableau des couches par préfecture ; les 272 auto-écoles (recherche + filtre statut) ;
  « ce que la carte ne montre pas » ; synthèse/limite.
- **Page 5 — Priorités** : zones en difficulté (zones_10 + regions_08) ; 5 qui cumulent ; 10 premières (score
  décomposé réseau/formation) ; 2 leviers (13 réseau / 23 formation) ; robustesse (curseur poids réseau + 5 tests de
  sensibilite_08) ; classement complet ; synthèse/limite.
- **Page 6 — Recommandations** : 7 onglets ; 15 cartes de cartes_10 (grille 3 colonnes, étiquettes priorité/nature/
  horizon, expander Détail) ; onglet « Actions par zone » = 39 fiches de prefectures_10 ; honore
  `recommandations_rang` et `fiche_prefecture` (arrivée depuis pages 1/4/5).
- **Page 7 — Méthodologie** : 9 étapes (rampe BLEUS) ; sources (_SOURCES.csv, décompte à l'affichage) ; limites ;
  niveaux de preuve ; 7 questions ouvertes (hypotheses_09 + consequences_11) ; zones les moins desservies (2 mesures
  d'accès rural) ; 18 formules par thème + bloc catalogue_07 replié ; corrections (erratum_A1) et contrôles (8 tables,
  comptés à l'affichage) ; licences (dont armoiries CC BY-SA 4.0) ; synthèse/limite.
- **Page 8 — Horizon 2031** : curseur d'horizon (Passé/Actuel/+1/+3/+5, défaut 2029) ; 4 chiffres clés (horizon_A1
  Pays) ; besoins par zone (sélecteur levier) ; population et besoin par zone dans le temps ; sécurité (national_A1 :
  tués observés + projections + cible + écarts/plafond casque) ; sites (emplacements_A1) ; synthèse/limite.

### Correctifs
- `app.py` : filtre Priorité aligné sur les valeurs réelles des données (`Haute`, `Moyenne`, `Aucune action`) au lieu
  de `Faible`.

### Déploiement Streamlit Cloud
- **`dashboard/requirements.txt`** créé (léger) : streamlit 1.61, plotly 7.1, pandas, geopandas, **pyogrio** (moteur de
  lecture des GeoJSON — indispensable sur un environnement propre), shapely, pyproj.
- **`dashboard/README.md`** créé : lancement local et pas-à-pas de déploiement (main file `dashboard/app.py` ;
  s'assurer que Cloud installe `dashboard/requirements.txt`, pas celui de la racine, lourd).
- Données versionnées (117 fichiers data/ suivis, GeoJSON et `_SOURCES.csv` compris) : le dépôt est déployable tel
  quel, le dashboard lit `../data`. Config, thème et `enableStaticServing` dans `dashboard/.streamlit/`, pris en compte
  quand le main file est `dashboard/app.py` (vérifié : armoiries servies en HTTP 200).

### Vérifié
- Les 8 pages s'affichent **sans aucune exception Streamlit** (Playwright, détection de `[data-testid="stException"]`).
- Branches à chemin distinct testées au clic : maille régions/préfectures (page 2), couches de la carte dont Priorité
  (catégorielle) et Distance. Branches non-défaut des sélecteurs (modes immat, positions extrêmes du curseur) vérifiées
  par lecture du code (filtrages vides-safe ou gardés par `if len(...)`).
- Captures d'écran relues : barre du haut (armoiries + 🇹🇬 + carte Togo AI Lab), KPIs A/B/C, constats, couleurs de
  zone, curseur d'horizon, cartes de recommandation, 9 étapes de méthode.

---

## 2026-10-09 — audit et reprise de la page 1 (Vue nationale)

Demande de l'utilisateur (`_CONSTRAINTS_DEV.txt`, texte corrigé) : changer le ministère, vérifier que la page 1 est
complète au regard de `design-page1.md`, et enrichir la carte.

### Audit de la page 1 contre design-page1.md — écarts trouvés et corrigés
| Élément du plan | Avant | Après |
| --- | --- | --- |
| Limites des 5 régions sur la carte | absentes | tracées en couleur sur **toutes** les couches |
| 4ᵉ couche « Routes nationales seules » | absente | ajoutée (revêtues pleines, non revêtues tiretées) |
| Info-bulle (nom, zone, région, population, auto-écoles, km évalués, part en mauvais état) | population + zone | complète ; Mô affiche « non définie (aucune route classée) » |
| Population en 5 classes `BLEUS` | rampe continue | 5 classes fixes + légende HTML avec effectifs (11/10/7/6/5) |
| Mini-visualisations des 4 cartes de thème | **absentes** | 4 ajoutées : courbe immat (ruptures 1995/2004), 6 taux de `taux_09`, mini-carte du mauvais état, jauge 16/39 |
| Ruptures de série 1995 et 2004 (étage haut) | absentes | tracées en pointillé + mention « rupture de série » |
| Mention « 2013 non renseignée » | absente | ajoutée sur l'étage des permis |
| Dernières valeurs annotées (motos, permis B, permis A) | motos seules | les 3, dans la couleur de leur série |
| Repères de contexte numérotés ① ② ③ | vlines sans numéro | numéros affichés en tête de l'étage haut |
| Export CSV des **deux** étages | immatriculations seules | immatriculations + permis |
| 5 messages « À retenir » | 5 messages divergents | les 5 du plan (dont 80,6 % des motos et les 7 questions ouvertes) |
| Synthèse chiffrée | « ×4,56 » + 3 puces hors plan | 8 095 498 habitants + 5 qui cumulent + 15 recommandations, **avec lien vers la page 6** |
| Limite | texte divergent | texte du plan (accidents nationaux, déclarés, parc estimé C, coût absent) |

### Ajouts demandés
- **Ministère de la topbar** : « Ministère de l'Efficacité du Service Public et de la Transformation Numérique »
  (`composants.MINISTERE`).
- **Couche par défaut « Toutes les couches »** : population + routes classées + auto-écoles réunies sur la même carte.
- **Découpage en 5 régions** : nouvelle couche « Régions » (régions remplies) ; sur toutes les autres couches, les
  5 régions sont tracées en contour épais de couleur, avec une légende HTML.
- **Zoom** : `scrollZoom: True` et barre d'outils Plotly (zoom, panoramique, réinitialisation, plein écran).

### Fichiers touchés
- `theme.py` : ajout de `COULEUR_REGION` (5 régions, dans la palette validée du 11 §4.1 ; la Maritime englobe le
  Grand Lomé et reprend sa couleur).
- `donnees.py` : ajout de `contours_regions()` (fusion des préfectures par région, orientation des anneaux pour Plotly).
- `composants.py` : `MINISTERE`.
- `views/vue_nationale.py` : réécrite (carte, mini-visualisations, section 5, messages, synthèse, limite).

### Vérifié
- Les **6 couches** de la carte s'affichent sans exception (Playwright) ; les 8 pages restent OK après modification des
  fichiers partagés.
- Captures relues : topbar avec le nouveau ministère, carte avec les 5 régions colorées et la barre de zoom, légendes
  HTML (régions, 5 classes de population), 4 mini-visualisations.
- Correctif de rendu : la légende des régions, illisible en légende Plotly (une trace choroplèthe n'a pas de pastille)
  et coûteuse en hauteur, est passée en HTML sous la carte ; le pays occupe maintenant toute la hauteur des 600 px.

---

## 2026-10-09 (suite) — audit et reprise de la page 2 (Comparaison territoriale)

### 🐛 Bug de données corrigé — un chiffre affiché sous un mauvais intitulé
`O3-06` est **« Part du réseau non évaluée »**, et non les km pour 10 000 habitants : c'est `O4-03`
(vérifié dans `catalogue_07.csv`). La colonne « Km /10 000 hab. » affichait donc la mauvaise grandeur.
- **Page 2, tableau des territoires** : Grand Lomé montrait 14,6 au lieu de **0,74** → corrigé en `O4-03`.
- **Page 5, classement complet** : même colonne, même correction.
- **Page 2, tableau des 39** : la colonne « Part du réseau non évaluée » demandée par le plan utilisait aussi
  `O4-03` ; elle lit maintenant `O3-06` et a été ajoutée au tableau.
Les valeurs concordent désormais avec `zones_10.csv` et avec le tableau de `design-page2.md`.

### Audit de la page 2 contre design-page2.md
Le gros œuvre était là (maille, 3 chiffres clés, nuage, tableaux, barres, concentration, distances, points
d'attention, synthèse). Écarts trouvés et corrigés, en plus du bug ci-dessus :
- la **ligne de seuil** n'était tracée qu'en maille préfectures, et sans étiquette ;
- en maille zones et régions, **aucun seuil n'était visible** alors que le plan les définit (médianes) ;
- la mention « par zone seulement » manquait sur le bloc de l'état du réseau en maille régions ;
- la colonne « Part du réseau non évaluée » du plan était absente du tableau des 39.

### Ajouts demandés
- **Section « Réseau et formation »** : la ligne de seuil est tracée et **étiquetée** (« seuil : 22,13 % de km en
  mauvais état »). En maille zones et régions, les deux médianes du classement sont tracées — réseau en rouge
  (vertical), formation en vert (horizontal) — puisque le curseur y est masqué.
- **Section « Les territoires »** : le tableau Streamlit est remplacé par un tableau HTML, qui permet les badges :
  - seuils franchis en pastilles colorées : **réseau rose `#bb537d`, formation indigo `#4a3aa7`,
    desserte jaune `#eda100`** (couleurs de la palette validée), avec une légende sous le tableau ;
  - leviers : « N préf. » en bleu nuit, puis la quantité dans une **autre couleur** — km en orange (réseau),
    auto-écoles en vert (formation) ;
  - « Part en mauvais état » **en rouge et en gras** pour les territoires au-dessus de la médiane.
  L'export CSV garde les valeurs brutes, sans mise en forme.
- **Section « État du réseau par zone »** : les km sont **inscrits dans chaque segment** (texte blanc sur fond
  sombre, encre sur fond clair) et la **part en mauvais état est écrite au bout de la barre**, en rouge pour les
  zones au-dessus de la médiane — comme sur l'image de référence. Ordre de légende remis dans le sens des barres.
- **Section « Où sont les auto-écoles »** : la ligne des 10 km est étiquetée. Les km, d'abord écrits devant le nom
  de la préfecture, ont été **déplacés au bout de la barre** (demande du 2026-10-09, voir ci-dessous).
- **Section « Les 39 préfectures »** : tableau mis en forme par un `Styler` (le tri par colonne reste actif) —
  priorité en **badge coloré**, **nom de la zone et de la région dans leur couleur de carte**, pourcentage de
  mauvais état **en rouge et en gras** au-dessus du seuil de 22,13 %. Formatage français rétabli après le passage
  au Styler (le Styler supprimait le format par défaut : « 100.000000 » → « 100,0 »).

### Codes et références retirés de l'affichage
Aucun code ni nom de fichier ne doit être visible hors Méthodologie et annexes. Corrigés :
- page 2 : « Niveau B. Source : hypotheses_09 (H8). » → « Niveau B — calculé sur les auto-écoles agréées et la
  population de 2022. » ; « (06 §5) » retiré ;
- page 3 : « (09 §10) » retiré ;
- pages 5 et 6 : « Erratum A1-E1 : … » → « Mesuré avec une grille de population, … ».
Contrôle automatique repassé : **aucune référence visible restante** dans les vues hors Méthodologie.

### Vérifié
- Les 3 mailles de la page 2 et les 8 pages s'affichent sans exception (Playwright).
- Captures relues : seuils tracés et étiquetés, badges des territoires, km dans les barres et pourcentage au bout,
  distances préfixées des km, tableau des 39 avec badges et couleurs, nombres au format français.
- Ajustement de rendu : le tableau des territoires (11 colonnes) débordait ; cellules et badges compactés, il tient
  maintenant en entier, avec défilement horizontal en secours.

### Reprise de la section « Distance à l'auto-école agréée la plus proche »
Les km étaient écrits devant le nom de la préfecture, sur l'axe vertical. Ils sont maintenant **au bout de chaque
barre**, à droite, et **chaque chiffre prend la couleur de son palier de dix kilomètres** :

| Palier | Couleur | Préfectures |
| --- | --- | --- |
| moins de 10 km | `#11613f` vert foncé (sous le seuil d'éloignement) | 13 |
| 10 à 20 km | `#ab6300` ocre | 4 |
| 20 à 30 km | `#cb4b0c` orange | 10 |
| 30 à 40 km | `#e34948` rouge | 3 |
| 40 à 50 km | `#c0392b` | 2 |
| 50 à 60 km | `#a02622` | 2 |
| 60 à 70 km | `#80191a` | 3 |
| 70 à 80 km | `#5e1114` | 1 |
| 80 km ou plus | `#3d0a0d` | 1 |

- Le premier palier s'arrête au **seuil d'éloignement du classement (10 km)** : la rupture de couleur tombe donc sur
  la décision, pas sur une graduation arbitraire. Au-delà, la teinte se réchauffe puis fonce avec la distance.
- Toutes les teintes sont assez sombres pour rester **lisibles en texte sur fond blanc** (les clairs de la rampe
  `BLEUS` ne l'auraient pas été).
- Une **légende des paliers**, avec l'effectif de chacun, est affichée sous le graphique (13+4+10+3+2+2+3+1+1 = 39).
- L'axe des x est étendu de 18 % pour que l'étiquette « 84,0 km » tienne hors de la barre.
- La couleur de remplissage de la barre garde son sens : bleu foncé = aucune auto-école agréée.

### Vérifié
- Les 8 pages s'affichent sans exception après la reprise ; capture relue (chiffres au bout des barres, dégradé des
  paliers, légende, total de 39).

---

## 2026-10-09 (suite) — audit et reprise de la page 3 (Évolutions et constats)

### ❗ Manque majeur comblé — la carte des constats
`design-page3.md` §1 fait de la **carte des constats** le visuel principal de l'onglet Synthèse. Elle n'avait pas été
construite. Elle l'est maintenant, avec ses trois couches et son encart :
- fond : les 39 préfectures, à la couleur de la part de km en mauvais état **de leur zone**, en 5 classes fixes
  (moins de 10 %, 10 à 15, 15 à 20, 20 à 30, 30 % ou plus), rampe `BLEUS` — effectifs 8 / 7 / 7 / 12 / 5 = 39 ;
- les **49 tronçons en mauvais état** tracés en rouge sur la route, épaisseur de 1,2 à 5 px selon les km en mauvais
  état. Chaque tronçon est rattaché au tracé par son nom (colonne « Noms du tracé », séparateur ` | `, 609 lignes du
  tracé appariées) : c'est une **sélection, pas un calcul** ;
- les **132 auto-écoles agréées** en points ;
- légende sous la carte (5 classes avec effectifs, trait rouge, point des auto-écoles) et zoom activé ;
- à droite, les deux verdicts illustrés, puis l'**encart national** « Ce qui n'a pas de territoire » : ×4,56
  (immatriculations) et −29,4 % (tués pour 100 000 habitants), chacun avec une courbe de 92 px portant sa première et
  sa dernière valeur, plus « Accidents par territoire — non testable ».

### 🐛 Codes encore visibles dans les textes — `nettoyer()` renforcé
La colonne « Ce que montrent les données » laissait passer des codes d'indicateur : « **O3-02** : Centrale 40,3 %… »,
« **O1-09** en cumul 2007–2024… ». La règle 11 §4.2 demande de **remplacer chaque code par son intitulé**, pas
seulement de retirer les renvois. `nettoyer()` le fait désormais :
- `O\d-\d\d` et `O\d-E\d` → intitulé lu dans `catalogue_07.csv` (« O3-02 » → « Part des km en mauvais état ») ;
- suppression des crochets, des parenthèses de renvoi, des codes isolés et des renvois de document en fin de
  parenthèse (« …, année de rupture de la série, 04) »).
Contrôle repassé sur `hypotheses_09` et `consequences_11` : **0 texte avec un code restant**.

### Ajouts demandés
- **Onglet Synthèse** : le verdict est en **badge coloré clair** (confirmée vert pâle, infirmée rouge pâle, nuancée
  ambre pâle, non testable gris), avec une légende sous le tableau. Le tri par colonne reste actif.
- **Immatriculations par groupe** : les ruptures de 1995 et 2004 portent **leur année** sur la ligne.
- **Permis par catégorie** : une ligne verticale porte « **2013** · non renseignée ».
- **Immatriculations pour un permis** : chaque barre prend **la couleur de sa catégorie de permis**, la même que sur
  la courbe des permis (la courbe elle-même est passée de la palette générique à ces couleurs, pour concorder).
- **Parc estimé** : titre devenu « **Parc estimé des véhicules, 2009–2024** » ; ajout de la courbe « dont motos » et
  des **nombres écrits de cinq ans en cinq ans** sur les deux courbes (426 417 → 751 398 ; 251 309 → 449 226).
- **Les 6 taux** : **une couleur par mesure** — tués en rouge, blessés en ambre, accidents en bleu — la période se
  lisant à l'opacité (pâle 2010–2012, pleine 2022–2024), avec une légende qui explique les deux dimensions.
- **Les tués par type d'usager** : **une couleur par catégorie** et les libellés **en gras**.
- **Annuaire national** : titre devenu « Un constat frappant sur l'état du réseau en 2020 : l'annuaire national ».

### Vérifié
- Les 8 pages et les 4 onglets s'affichent sans exception ; captures relues (carte des constats, encart national,
  badges de verdict, ruptures étiquetées, parc estimé chiffré, 6 taux colorés, usagers en couleur).
- Deux ajustements de rendu en cours de route : les étiquettes de rupture chevauchaient la légende (rentrées dans la
  zone de tracé) ; la légende Plotly des 6 taux était trompeuse, la couleur portant deux informations (supprimée au
  profit de la légende HTML), et la valeur 189,13 était tronquée (axe élargi).

### À faire
- Fournir `static/logo_togo_ai_lab.png` (sinon repli texte, comportement normal).
- Étape de livrable (optionnelle) : si l'on veut un `dashboard/` autonome, copier les CSV et GeoJSON lus dans
  `dashboard/data/` (le code bascule alors automatiquement sur `dashboard/data/`).
- Rédaction du ppt.

---

## 2026-10-09 — Page 4 « Carte du réseau et des auto-écoles » : refonte complète

### Audit contre `design-page4.md` : ce qui manquait
La page ne tenait que 7 couches sur 12, une échelle continue « Blues » au lieu des **5 classes fixes**, aucune légende
d'effectifs, pas de limites de régions, pas de choix de tracé, pas d'équipements, pas de fiche au clic, pas
d'agrandissement du Grand Lomé, et un tableau sans couleurs de classe. La page a donc été réécrite.

### Ce qui est maintenant en place (sections du plan)
- **12 couches** (section 3), chacune en **5 classes fixes** de la rampe `BLEUS` (la priorité en palette `PRIORITE`),
  avec son unité, son niveau de preuve, sa note et son constat : les 5 états du réseau (mauvais, bon, moyen, travaux,
  non évalué), population, km pour 10 000 habitants, densité routière, accès rural, auto-écoles pour 100 000
  habitants, distance à l'auto-école agréée, priorité. Valeurs absentes en gris avec leur mention (Mô « aucune route
  classée » ; Golfe et Agoè-Nyivé « sans population rurale »), jamais confondues avec un 0 mesuré.
- **Réglages** (section 2) : couche, tracé (routes classées par type · état des tronçons relevés · aucun),
  auto-écoles, équipements de sécurité routière (un type à la fois, avec la mention « hors indicateurs »).
- **Tracé « état des tronçons relevés »** : les 49 tronçons avec des km en mauvais état en rouge, épaisseur de 1,2 à
  5 px selon les km ; les 35 autres tronçons relevés en gris foncé ; les routes nationales sans état en tirets gris
  clair. Rattachement **par le nom du tronçon** : une sélection, pas un calcul.
- **Limites des 5 régions** toujours tracées, en bande grise large sous les routes.
- **Filtres de la barre latérale** respectés : hors territoire en beige, avec son compte dans la légende.
- **Légende complète** sous la carte : les 5 classes avec leur effectif, les valeurs absentes, le hors-sélection, puis
  « Sur la carte » (limites, types de routes avec leurs km, auto-écoles, équipements).
- **Fiche de la préfecture au clic** (section 7) : population, priorité en pastille, leviers, actions recommandées et
  bouton « Voir la fiche de <préfecture> → » qui ouvre la page Recommandations sur l'onglet « Actions par zone ».
  La préfecture choisie est **cerclée de noir** sur les deux cartes.
- **Les 272 auto-écoles** (section 10) : statut en pastille, colonne « à vérifier » (13 auto-écoles non agréées dans
  une préfecture sans aucune agréée), habitants par auto-école agréée, filtre par zone, recherche et export.

### Corrections demandées
- **Carte agrandie** comme la carte des constats : 620 px, zoom à la molette et barre d'outils, survol riche.
- **Agrandissement de la région Maritime et du Grand Lomé** dans la **même figure** (second panneau `geo2`, à droite),
  avec le nom des 8 préfectures, comme la figure « Carte : routes nationales avec et sans état » du notebook 04 — O3.
  Toutes les couches y sont reprises ; les points y sont un peu plus gros, la zone étant la plus dense.
- **Auto-écoles : deux couleurs** — agréées en bleu foncé cerclé de blanc (132), non agréées ou au statut non
  renseigné en gris plus petit (140).
- **Routes : deux couleurs** — nationale revêtue en noir plein, nationale **non revêtue en ocre tireté** (elles se
  confondaient, les deux étant noires) ; voirie urbaine en gris plein, piste rurale en gris pointillé.
- **Tableau des couches** : « Mauvais état » et « Priorité » en **badges colorés**, comme les seuils franchis de la
  page Comparaison territoriale ; le badge de mauvais état prend la couleur de sa classe sur la carte, le nom de la
  zone prend sa couleur. Tableau déroulant (39 lignes) avec un sélecteur de tri, légende des badges, export complet.
- Les aides `badge()` et `table_html()` sont remontées dans `composants.py` pour être partagées entre les pages.

### 🐛 Deux défauts trouvés en vérifiant
1. **Mauvaise préfecture dans la fiche.** Le clic sur une auto-école renvoyait un point sans `location` ; la
   résolution de secours par `point_index` prenait alors la n-ième préfecture de la liste : un clic sur une
   auto-école de **Sotouboua** affichait la fiche d'**Akébou**. La résolution lit maintenant `location` (préfecture)
   ou le texte du point (préfecture de l'auto-école ou de l'équipement), et plus jamais un index de position.
2. **Carte estompée après un clic.** Plotly applique une opacité réduite à tout ce qui n'est pas sélectionné : la
   carte entière pâlissait. `selected`/`unselected` sont fixés à une opacité de 1 sur toutes les traces ; le repère
   visuel est le cerclage noir de la préfecture choisie.
   Au passage : la colonne « Habitants par auto-école agréée » affichait `None` pour les 13 préfectures sans auto-école
   agréée (le formateur d'un `Styler` ne s'applique pas aux valeurs manquantes) — la colonne est désormais écrite en
   clair (« aucune agréée »).

### Vérifié
- Les 8 pages se chargent sans exception (contrôle Playwright) ; page 4 testée couche par couche (priorité, non
  évaluée, distance, accès rural), tracé « état des tronçons », équipements (ralentisseurs), clic sur une préfecture,
  tableau à badges et tableau des 272 auto-écoles. Captures relues.

---

## 2026-10-09 — Page 5 « Priorités » : audit et mise au plan

### Audit contre `design-page5.md` : ce qui manquait
La page tenait toutes les sections, mais plusieurs éléments du plan n'étaient pas là :
- section 1 : pas de pastille sur « moins bien desservie pour », pas de colonne **Recommandation** (titre lu dans
  `cartes_10.csv` via la colonne `Recommandation` de `zones_10.csv`), pas de **phrase de diagnostic par zone**
  (`phrases_11.csv`), pas la phrase de la région Maritime ;
- section 2 : pas de lien vers la recommandation ;
- section 3 : barres non colorées par levier lisible, pas de **score écrit au bout de la barre**, pas de robustesse
  à droite, les **km évalués** n'étaient pas écrits à côté de la part, pas de phrase « ce qu'elle cumule » ;
- section 4 : pas de rang, pas de **nature du zéro** (aucune recensée / recensées non agréées), pas de population
  dont le chef-lieu est à plus de 10 km, pas de liens vers les recommandations ;
- section 5 : pas de valeurs de contrôle du curseur ;
- section 6 : pas de mention **« desserte faible »**, Mô en simple légende au lieu de sa phrase de diagnostic, et le
  lien vers la carte n'ouvrait pas la couche Priorité ;
- les filtres de la barre latérale ne touchaient que deux sections, alors que le plan les applique aux sections 2 à 6.

### Ce qui a été ajouté
- **Section 1** en tableau HTML : zone à sa couleur, déficit en **pastille** (deux déficits `#0d366b`, un seul
  `#3987e5`, aucun gris), accès rural avec la mention « cas limite » pour les Savanes, leviers en badges, et le
  **titre de la recommandation** de la zone. Dépliant « Ce que dit chaque zone » avec les 6 phrases de diagnostic,
  puis la ligne par région et la phrase de la région Maritime.
- **Section 2** : tableau à badges, part en mauvais état en rouge, et lien « Remettre en état le réseau de ces
  5 préfectures → Recommandations ».
- **Section 3** : barres empilées réseau/formation portant le **score publié** au bout (la somme des deux rangs
  percentiles, celle de `classement_08.csv`, pas une moyenne refaite) et, à droite de chaque barre, la
  **robustesse `n/6`** en vert, ambre ou rouge. Tableau à badges avec les **km évalués à côté de la part**, et
  dépliant « Ce que cumule chacune des 10 premières » (phrases de diagnostic).
- **Section 4** : rang dans chaque levier, km à remettre en badge, et pour la formation la **nature du zéro**
  (« aucune recensée » ou « n recensées, non agréées ») et les **habitants à plus de 10 km** ; un lien vers les
  recommandations sous chaque liste.
- **Section 5** : tableau des 5 tests en badges (entrées en vert, sorties en rouge) et **valeurs de contrôle** du
  curseur écrites sous lui.
- **Section 6** : tableau à badges (déficits, leviers, **« desserte faible »** accolé aux km pour 10 000 habitants),
  déroulant, avec sa légende ; **Mô présentée à part** avec sa phrase de diagnostic ; le bouton « Voir le classement
  sur la carte → » ouvre maintenant la page 4 **sur la couche Priorité**.
- **Filtres** zone et levier appliqués aux sections 2 à 6, avec un bandeau qui les rappelle et un message quand une
  section devient vide ; la section 1 montre toujours les 6 zones, comme le demande le plan.

### Point de vigilance relevé
Le score du classement publié est la **somme** des deux rangs percentiles (Danyi 1,72), pas leur moyenne : les barres
affichaient des demi-parts et auraient porté une valeur qui ne correspondait à aucune colonne du CSV. Elles empilent
désormais les deux rangs percentiles tels quels, dont la somme est bien le score de `classement_08.csv` (R-19).

### Vérifié
- Les 8 pages se chargent sans exception ; page 5 relue section par section (captures), filtres zone et levier
  testés, et le lien vers la carte vérifié : il ouvre bien la page 4 sur la couche Priorité.

---

## 2026-10-09 — Page 6 « Recommandations » : audit et mise au plan

### Audit contre `design-page6.md` : ce qui manquait
Les 7 onglets, les 15 cartes et les 39 fiches étaient là, au bon format (thème, titre, cible, contexte, étiquettes,
bouton Détail avec acteur, suivi, niveau et réserve, soit la règle R-18). Manquaient :
- la **barre de résumé** et le filtre de **recherche** (titre, cible, texte) ;
- la mention **« national »** sur les cartes qui ne se répartissent pas par zone ;
- la **ligne d'horizon** de chaque carte, pourtant prévue au plan (lue dans `horizon_A1.csv`) ;
- le renvoi de chaque carte vers la page **Horizon 2031** ;
- la ligne **« Zones en difficulté »** lue dans `zones_10.csv` (elle était écrite en dur) et son lien vers la page 5 ;
- le lien **« Pourquoi ces zones → Priorités »** dans l'onglet des zones ;
- le **tri des 39 fiches** (rang national, population, zone, nombre de déficits) ;
- l'**export des 15 recommandations** en CSV (seules les fiches s'exportaient).

### Ce qui a été ajouté
- **Barre de résumé** « 15 recommandations · les habitants ne s'additionnent pas d'une carte à l'autre », et champ
  de **recherche** qui filtre les cartes (titre, cible, texte) comme les fiches.
- **Ligne « Zones en difficulté »** construite depuis `zones_10.csv` (colonne « Moins bien desservie pour »), avec le
  bouton « Pourquoi ces zones → » vers la page Priorités ; même lien sous l'onglet « Zones les moins desservies ».
- **Ligne d'horizon** sous le texte de chaque carte, lue dans `horizon_A1.csv` (lignes de maille « Recommandation »,
  colonne « Palier de l'horizon ») : « D'ici 2029, horizon de cette action : 30 auto-écoles, la population ayant
  grandi. » Pour la remise en état, la ligne dit à la place que **la quantité ne change pas avec l'horizon, aucune
  donnée ne mesurant l'usure du réseau**. Les recommandations sans quantité (données, deux-roues) n'ont pas de ligne.
  La carte de la Centrale en porte deux, réseau et formation, comme l'annexe les sépare.
- **Mention « national »** en étiquette sur les cartes nationales, qui restent affichées quel que soit le filtre de
  zone (le plan l'exige : pas de double compte, mais pas de disparition non plus).
- **Bouton « Voir l'horizon de cette action → »** dans le Détail de chaque carte, vers la page Horizon 2031.
- **Onglet « Actions par zone »** : sélecteur de tri (rang national avec Mô à la fin, population, zone, nombre de
  déficits), rappel de la répartition et de la légende des icônes, message explicite quand un filtre vide la liste.
- **Export** des 15 recommandations en CSV, à côté de celui des fiches.

### 🐛 Deux défauts trouvés en vérifiant
1. **Clé de bouton en double.** La même carte apparaît dans l'onglet « Toutes » et dans son onglet de thème : les
   deux boutons d'horizon portaient la même clé et Streamlit levait `StreamlitDuplicateElementKey`. Chaque grille
   préfixe désormais ses clés.
2. **La sélection de la carte (page 4) était perdue au rerun.** Plotly efface la sélection dès que la figure change —
   et elle change justement parce qu'on cercle la préfecture choisie. Conséquence : le bouton « Voir la fiche de
   <préfecture> → » n'arrivait jamais à s'exécuter, la fiche disparaissant au rerun du clic. La préfecture retenue
   est maintenant gardée dans `st.session_state["ca_prefecture"]`, avec un bouton « Effacer » ; le parcours
   carte → fiche fonctionne, et la page 6 s'ouvre bien sur l'onglet « Actions par zone », filtrée.

### Vérifié
- Les 8 pages se chargent sans exception ; page 6 relue onglet par onglet (captures), recherche testée, et les trois
  parcours vérifiés : carte → fiche de la préfecture, « Voir les 39 fiches » qui retire le filtre, et
  « Pourquoi ces zones → » qui ouvre la page Priorités.

---

## 2026-10-09 — Page « Horizon 2031 » : audit et mise au plan

Attention au numéro : cette page est la **7e du menu**, mais son plan est `design-page8.md` (`design-page7.md` est
celui de la page Méthodologie). Le bloc de consignes a été corrigé en ce sens.

### Audit contre `design-page8.md` : ce qui manquait — oui, des cartes
- **La carte des préfectures** de la section 2 n'existait pas : seules des barres par zone s'affichaient.
- **La carte des sites** de la section 5 n'existait pas non plus : seul le tableau était là.
- Section 2 : pas de sélecteur de maille zones/régions, pas de colonne « ruraux à plus de 2 km », pas de ligne de
  total pays, pas de **tableau par recommandation**.
- Section 3 : le premier graphique montrait les auto-écoles **à ouvrir** au lieu des **auto-écoles agréées pour
  100 000 habitants sans action**, sans la ligne de cible 1,065 ; la population n'avait pas sa bande de fourchette.
- Section 4 : un seul graphique (les tués) au lieu des **trois séries en trois panneaux**, pas de **période projetée
  grisée**, et pas de **graphique des écarts et plafonds** aux 4 horizons (une simple liste à puces).
- Section 6 : ni les permis moto, ni les tués à éviter lus dans les données (chiffre écrit en dur).

### Ce qui a été ajouté
- **Carte des préfectures** (section 2), avec le sélecteur de levier, **5 classes fixes** qui ne changent pas d'un
  horizon à l'autre pour que les couleurs se comparent, Mô en gris « aucune route classée » pour la remise en état,
  l'**agrandissement de la région Maritime et du Grand Lomé** dans la même figure, le zoom et la légende à effectifs.
- **Tableau par zone ou par région** (sélecteur), avec habitants, auto-écoles à ouvrir et leur fourchette, km à
  remettre en état, ruraux à plus de 2 km, et une **ligne Togo** ; export CSV.
- **Tableau par recommandation**, dépliable : quantité de 2022, quantité à l'horizon choisi, horizon porté par la
  recommandation, titres lus dans `cartes_10.csv` (aucun identifiant affiché), et un lien vers sa carte en page 6.
- **Section 3** refaite : auto-écoles agréées pour 100 000 habitants **sans action**, 6 zones, ligne de cible 1,065 ;
  population avec la **bande de fourchette** des deux variantes ; note de méthode dépliable.
- **Section 4** refaite : **trois panneaux** (accidents constatés, blessés, tués) de 2010 à 2031, observé en trait
  plein, références sans action et cible de la Décennie en pointillés, **bande grise sur la partie projetée avec son
  texte en petits caractères « projeté · 2025-2031, sans action nouvelle »** (demande explicite), horizon marqué ;
  et le **graphique en barres** des écarts à la cible et des plafonds du casque aux 4 horizons, avec leur intervalle.
- **Carte des sites** (section 5) : les 23 préfectures du levier formation en bleu clair, les 132 auto-écoles agréées
  existantes en gris, les **48 sites retenus** en losanges bleus, avec le nom du site, son type et les habitants
  gagnés au survol. Les coordonnées UTM 31N des sites sont converties en lon/lat pour l'affichage.
- **Synthèse** complétée : permis moto à délivrer dans l'année et tués à éviter, lus dans `national_A1.csv` au palier
  choisi, au lieu d'un chiffre écrit en dur.

### 🐛 Un défaut de données trouvé en vérifiant
`emplacements_A1.csv` porte une **ligne de total « Ensemble des 23 »** en plus des 23 préfectures. Elle était
affichée comme une préfecture dans le tableau des sites (zone vide) et comptait dans la carte : la légende annonçait
« 24 préfectures du levier formation ». La ligne est maintenant écartée du tableau et de la carte, et sert à écrire
le total sous le tableau.

### Deux ajustements de rendu
- Le Grand Lomé (4,71 → 3,80) écrase les cinq autres zones (0,3 à 0,7) : les étiquettes de fin de courbe se
  chevauchaient. Elles sont remplacées par une ligne de valeurs « 2022 → 2031 » sous le graphique.
- La « cible de la Décennie » n'apparaissait pas dans la légende des trois panneaux : elle n'existe pas sur le
  premier (les accidents constatés n'ont pas de cible). La légende prend désormais chaque série au premier panneau
  où elle existe.

### Vérifié
- Les 8 pages se chargent sans exception ; page Horizon relue section par section (captures), les deux cartes et les
  quatre graphiques contrôlés, le tableau par recommandation ouvert, et le curseur testé aux deux extrémités
  (2022 : 41 auto-écoles, 304,6 km, 8 095 498 habitants ; 2031).
