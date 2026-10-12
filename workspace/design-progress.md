# Journal du design — tableau de bord

Suivi des changements de design du tableau de bord (`dashboard/`), validés un à un sur maquette avant d'être codés.
Branches : `design/sidebar-branding` (étapes 1 à 4), puis `design/palette-a` (étape 5 et suivantes, qui part de la
première). Le développement fonctionnel reste suivi dans `workspace/dev-progress.md`.

---

## 1. Barre latérale : logo et slogan (toutes les pages)

- **Logo en haut**, en face du bouton qui replie la barre (`st.logo`) : le Togo en miniature aux couleurs du drapeau,
  traversé par une route, avec « TOGO / MOBILITÉ & SÉCURITÉ ROUTIÈRE / Tableau de bord territorial d'aide à la
  décision ». Silhouette seule quand la barre est repliée.
  - Contour du pays tiré des 39 préfectures du projet (`data/processed/geo/prefectures.geojson`).
  - Produit par `scripts/logo_barre_laterale.py` → `static/logo_barre_laterale.svg` et `static/logo_togo_icone.svg`.
- **Slogan en bas** : « Des routes plus sûres pour une mobilité durable au Togo », un court filet turquoise, puis une
  illustration de montagnes et de route sinueuse (`static/routes_slogan.svg`). Poussé en bas de la barre par CSS
  quand la hauteur le permet (`composants.pied_barre_laterale`, `.slogan-barre`).

## 2. Barre du haut (toutes les pages)

- Sous-titre : « Comprendre les risques, identifier les priorités d'action » (au lieu de « Évolution de la
  mobilité, de la sécurité routière et du réseau »).
- **Superposition à l'en-tête de Streamlit Cloud (option A)** : l'en-tête de Streamlit devient transparent et notre
  barre blanche remonte tout en haut ; les boutons de Streamlit Cloud (Share, étoile, édition, GitHub) prennent place
  dans le coin droit de la barre, dont la colonne de droite leur réserve 230 px. Option B (masquer ces boutons)
  écartée. À vérifier sur l'application déployée.
- Logo Togo AI Lab aligné à droite de sa colonne.

## 3. Vue nationale : en-tête et chiffres clés

- Texte d'introduction sous le titre dans une **carte à fond blanc** (filet bleu nuit à gauche) :
  `entete(..., carte=True)`.
- **Six chiffres clés sur une seule ligne** (`rangee_kpi(..., une_ligne=True)`), 3 puis 2 colonnes sur écran étroit.
- **Pastille d'icône** du thème à gauche du titre de chaque carte (`carte_kpi(..., icone=...)`, `ICONES` dans
  `composants.py`) : personnes, voiture, triangle d'alerte, cœur-pouls, route, toque.
- Titres en MAJUSCULES, couleur d'encre ; **année entre parenthèses sous le titre** (`periode=`).
- Libellés :

  | Avant | Après |
  |---|---|
  | Population 2022 · « habitants, recensement de 2022 » | POPULATION (2022) · « habitants » |
  | Immatriculations 2024 | IMMATRICULATIONS (2024) |
  | Tués 2022 | MORTS SUR LA ROUTE (2022) |
  | Blessés 2022 | BLESSÉS SUR LA ROUTE (2022) |
  | Réseau évalué · « milliers de km, relevé de 2020 » · « 84 tronçons ; 21,2 % … » | RÉSEAU ROUTIER ÉVALUÉ (2020) · « dont 84 tronçons » · « 21,2 % en mauvais état (669 km). » |

- Étiquettes de qualité A / B / C retirées des six cartes de cette page (gardées sur les autres pages).
- Un peu d'espace avant le texte de fin de chaque carte ; chiffres alignés d'une carte à l'autre.

## 4. Palette A — institutionnelle moderne (validée)

Fond « café » `#F4F2EC` **conservé** à la demande. Le reste :

| Élément | Couleur |
|---|---|
| Cartes KPI et graphiques | blanc `#FFFFFF`, bordure `#E2E8F0`, ombre discrète |
| Barre latérale | bleu nuit `#0B263D` ; texte `#F8FAFC` ; intitulés `#CBD5E1` |
| Navigation active | fond bleu soutenu `#1769AA`, texte blanc (le jaune n'est plus sur les boutons) |
| Filtres | fond blanc, bordure `#E2E8F0`, sélection bleu `#1769AA` |
| Texte principal / secondaire | `#172B3A` / `#64748B` |
| Titres, chiffres clés | bleu nuit `#0B263D` |
| Accents nationaux | vert `#006B3F`, jaune `#FCD116`, rouge `#CE1126` |
| Barre du haut | fond blanc, titre bleu nuit, sous-titre gris ardoise, petit filet tricolore vert / jaune / rouge |

Couleurs fixes par donnée, dans `theme.py`, pour qu'un indicateur garde sa couleur sur toutes les pages :

- `SERIE` : motos `#16834A`, voitures `#2474C6`, poids lourds `#E6B422`, accidents `#CE1126`, blessés `#E87518`,
  décès `#8E1B2B`, auto-écoles `#2474C6`.
- `ETAT` (routes) : bon `#16834A`, moyen `#E6B422`, mauvais `#CE1126`, travaux `#8293A7`.
- `THEME` : Mobilité `#2474C6`, Sécurité routière `#E87518`, Réseau `#E6B422`, Couverture `#16834A`.
- Carte : rampe séquentielle bleue (`BLEUS`) pour les valeurs croissantes, inchangée.
- Vert et rouge côte à côte sont confondus par une part des daltoniens : toujours écrire le libellé ou la valeur
  à côté de la couleur.

## 5. Recommandations validées (R1, R2, R3)

- **R1 — Tendance en badge arrondi coloré** sous le chiffre (`carte_kpi(..., tendance=...)`), variation sur un an
  lue dans `indicateurs_07.csv` (`variation()` dans `vue_nationale.py`) :
  immatriculations −32,6 % vs 2023 (gris : ni bon ni mauvais), morts +0,4 % vs 2021 et blessés +5,8 % vs 2021
  (rouge : aggravation). Le vert est réservé à une amélioration démontrée.
- **R2 — Liseré fin en bas de chaque carte**, de la couleur de son thème (celle de la pastille d'icône).
- **R3 — Encadré « Constat »** sur fond blanc avec un filet jaune drapeau à gauche (toutes les pages).
- **Bloc central** : chiffre, badge de tendance et phrase qui suit (ex. « blessés déclarés ») centrés dans la carte,
  haut aligné pour que les chiffres restent sur une même ligne.
- R5 (passer les accidents en 2024) écarté : on garde 2022, année de la population de référence.

## 6. Ajustements des cartes et des sections (Vue nationale)

- Couleur (pastille d'icône et liseré bas) : **Immatriculations en vert** `#16834A`, **Morts sur la route en rouge**
  `#CE1126`, **Blessés en jaune-or** `#E6B422` (le jaune drapeau `#FCD116` est trop clair sur fond blanc pour une
  icône et un liseré lisibles).
- **Balayage lumineux au survol des chiffres clés rétabli** (il avait été retiré par la règle « pas de dégradés
  décoratifs » de la palette A).
- Section « Le Togo, préfecture par préfecture » : encadré **Constat placé sous le titre**, sur toute la largeur ;
  carte resserrée (colonnes 1,25 / 1 au lieu de 1,6 / 1) ; à droite, les légendes (régions, classes de population),
  la note sur les permis, les précisions et le lien « Voir la carte détaillée ».
- Section des thèmes renommée **« Les quatre thèmes confirmés »** ; chaque thème dans une **carte blanche arrondie**,
  liseré bas de la couleur de son titre (bleu, ambre, brique, vert), légère élévation au survol, sans balayage.
- **R4 refusé** : les émojis des cartes de thème restent tels quels.

## 7. Section carte, cartes de thème, contrôles (Vue nationale)

- Légende des régions : nombre de préfectures par région, lu dans `prefectures_10` — Maritime (8), Plateaux (12),
  Centrale (5), Kara (7), Savanes (7).
- Les deux précisions sous les légendes passent dans des **bandes-cartes** (même style que les légendes) ;
  « niveau C » retiré de la précision sur le réseau.
- **Boutons radio** de la couche : contour visible (2 px gris ardoise) même quand ils ne sont pas sélectionnés.
- **« Voir le détail »** : survol bleu `#1769AA`, texte blanc, comme la navigation de la barre latérale.
- Cartes de thème de même hauteur ; **« Voir le détail » toujours en bas** de chaque carte (Couverture comprise).
- Carte Réseau : précision « Relevé de 2020, niveau C. » retirée.

## 8. Bas de page (Vue nationale)

- « Voir le détail » : survol **bleu clair** `#E8F0FB` (texte bleu nuit), au lieu du bleu soutenu jugé trop foncé.
- **Permis de conduire délivrés** (titre sans 2024 ; sous-titre « Total et décomposition par catégorie ») : graphique
  et axes conservés ; chaque barre prend la couleur de sa catégorie, celle de la page Évolutions (A bleu, B orange,
  C vert, E vert clair, D ambre, F gris) ; chiffres alignés à droite des barres.
- **Immatriculations et permis, 1990–2024** : note de fin dans une carte (fond bleu clair, filet bleu), sur deux
  lignes — « Une date situe une variation… » puis « Repères : ① … ② … ③ … » (`.note-carte`).
- **À retenir** : carte blanche, cinq messages numérotés dans des pastilles rondes (`.retenir`).

## 9. Permis, notes, synthèse et limite (Vue nationale)

- **Permis de conduire délivrés** : le total (38 531, « permis délivrés en 2024, toutes catégories », niveau A)
  revient à gauche du graphique, dans une carte bleu clair `#E8F0FB` ; graphique inchangé.
- « Les permis moto ont bondi… » : bande arrondie bleu clair, liseré à gauche comme les autres notes.
- Sous le graphique immatriculations et permis, **deux cartes blanches côte à côte** :
  - liseré rouge à gauche : « En 2021, on comptait 310 immatriculations de motos pour chaque permis moto délivré,
    contre seulement 6 en 2024. » (nouvelle formulation) ;
  - liseré bleu à gauche, fond désormais blanc : « Une date situe une variation… » et « Repères : ① ② ③ ».
- **Synthèse chiffrée** : carte vert clair (`#E6F4EC`, textes vert foncé), même hauteur que la carte « À retenir » ;
  disposition d'origine (titre et chiffre à gauche, liste à droite) ; bouton « Voir les recommandations », au style
  de « Voir le détail », en bas à droite de la carte, en petit format.
- **Limite** : titre « Limite » (au lieu de « Limite de cette page ») ; « (niveau C) » retiré du texte.

## 10. En-têtes (toutes les pages), synthèse, pied

- **Surtitre en majuscules retiré de l'en-tête de toutes les pages** (« VUE NATIONALE », « PRIORITÉS »…) : il doublait
  le fil d'Ariane « Tableau de bord › page ». `entete()` garde son paramètre `surtitre` mais ne l'affiche plus.
- Synthèse chiffrée : contenu centré verticalement dans la carte verte, liste à puces alignée à gauche.
- Pied de page, sous la carte « Limite » : « Mise à jour : 2026. » retiré de la phrase sur les données.

## 11. Traduction (branche `design/traduction`, partie de `design/palette-a`)

- **Langues** : français (source), anglais, éwé, kabiyè. **Sélecteur** dans la barre latérale, sous le logo
  (FR · EN · Eʋegbe · Kabɩyɛ) ; la langue suit l'adresse (`?lang=en|ee|kbp`) et reste la même d'une page à l'autre.
- **Méthode « traduire avant le déploiement »** : `scripts/traduire_dashboard.py` recense les textes (chaînes du code
  et textes réellement affichés par les 8 pages), les traduit une fois avec **NLLB-200** (distillé 600M, via
  CTranslate2 ; licence CC-BY-NC, admise car le tableau de bord est une démo non commerciale) et écrit
  `dashboard/locales/<langue>.json`, qu'on commit. À l'affichage, `bi()` lit ces fichiers : aucun modèle, aucun
  appel réseau (compatible Heroku et Streamlit Cloud).
- **`dashboard/i18n.py`** : `installer()` fait passer par `bi()` tout ce que Streamlit affiche (markdown, widgets,
  onglets, tableaux, graphiques Plotly). Le HTML, le markdown, les gabarits `%{…}`, le CSS, les pictogrammes et les
  noms de lieux des données ne sont jamais traduits ; un segment absent reste en français.
- **Qualité** : anglais correct (quelques termes d'interface fixés à la main, marqués `"relu": true`) ; éwé et
  kabiyè approximatifs (contresens sur le vocabulaire technique, quelques mots répétés). Les traductions jugées
  inventées sont laissées en français et marquées `"suspect": true`. **Relecture par des locuteurs nécessaire**
  avant une présentation officielle : corriger le JSON et passer `"relu": true` pour que le script ne l'écrase pas.
- **Logo** de la barre latérale décliné par langue (`static/logo_barre_laterale_<langue>.svg`) ; texte français
  gardé quand la traduction est trop longue (cas du kabiyè).
- Mise à jour après un changement de texte : `python scripts/traduire_dashboard.py` (ne traduit que le nouveau),
  puis `python scripts/logo_barre_laterale.py`.

## 12. Page Comparaison territoriale

- Texte d'introduction dans une **carte blanche**, sur **deux lignes** (la Centrale… ; 23 préfectures…), mots et
  chiffres forts en couleur (Centrale dans sa couleur de zone, chiffres de risque en rouge drapeau).
- Les **3 chiffres clés** passent avant « Choisir la maille », avec une **pastille d'émoji** par thème, comme les
  cartes des quatre thèmes de la Vue nationale (🛣️ réseau, 🏫 auto-écoles, 📍 distance) : `carte_kpi(pastille=…)`.
- « Choisir la maille » : sous-titre « Les objectifs 3 et 4 demandent… » retiré.
- **Réseau et formation** : Constat sous le titre, graphique sur toute la largeur, note des seuils dans une carte
  blanche « ⓘ **À savoir :** … » (`.note-carte.a-savoir`).
- **Les territoires** : badge « desserte » en jaune drapeau `#FCD116` (texte foncé).
- **Distance à l'auto-école agréée la plus proche** : graphique sur toute la largeur ; le bloc « Où sont les
  auto-écoles » passe au-dessus.
- Nouveaux textes traduits (en, ee, kbp) ; un passage anglais inventé par le modèle corrigé à la main.

## 13. Comparaison territoriale (suite) et avertissement Streamlit

- **Avertissement « st._bottom »** corrigé : `i18n.installer()` ne parcourt plus tous les attributs de Streamlit
  (ce qui lisait l'attribut déprécié `st._bottom`), mais une liste explicite de fonctions.
- 3 chiffres clés : chiffre et phrase **centrés** (`rangee_kpi(centre=True)`).
- Retirés : « Niveau C : état relevé en 2020… », « Ce bloc reste en 6 zones… », « Niveau B — calculé… ».
- Notes en **cartes blanches à liseré vert et pictogramme « i »** (`composants.note_carte()`) : seuil des
  préfectures (maille Préfectures), état du réseau par type de route, distance à l'auto-école.
- **Où sont les auto-écoles** : carte horizontale à liseré bleu, « Concentration urbaine » et ×2,62 à gauche, le
  texte à droite (`.carte-chiffre`).
- **Les 39 préfectures** : note en carte à **liseré rouge**, noms de préfectures en gras (Mô, Golfe, Agoè-Nyivé).
- Traductions mises à jour (en, ee, kbp).

## 14. Comparaison : points d'attention, synthèse et limite

- **Points d'attention** : noms de lieux (préfectures, zones, régions) en **violet** `#4A3AA7` comme dans les
  constats, effectifs d'habitants en **rouge** `#CE1126` (`_colorer()` dans `comparaison.py`, classes `.lieu`
  et `.habitants`) ; les 5 cartes ont la **même hauteur**.
- **Synthèse chiffrée et Limite** côte à côte, **même hauteur** ; la Limite est présentée en **liste à points**,
  comme la synthèse (`limite(puces=…)`).
- Mécanisme réutilisable : classe `.carte-egale` (options `egale=True` de `synthese()` et `limite()`) pour égaliser
  les hauteurs des cartes d'une même rangée.

## 15. Évolutions — onglet Synthèse

- Texte d'introduction dans une **carte blanche** (`entete(carte=True)`).
- 3 chiffres clés : **icônes** (✅ confirmées, ⚠️ infirmées/nuancées, ❓ non testables) et contenu **centré**
  (`rangee_kpi(centre=True)`, `carte_kpi(pastille=…)`).
- **Couleurs de verdict uniformes** sur la page (palette A) : confirmée vert `#16834A`, infirmée rouge `#CE1126`,
  nuancée jaune-or `#E6B422`, non testable gris bleuté `#8293A7` — appliquées aux encarts, aux badges des tableaux,
  à la légende et aux marqueurs de la carte.
- **La carte des constats** : les 3 encarts nationaux (Mobilité·confirmée, Sécurité routière·nuancée, Accidents par
  territoire·non testable) deviennent des **cartes blanches à liseré gauche** coloré par leur verdict. Les deux
  constats cartographiés (réseau, auto-écoles) passent **sous la carte, à droite de la légende**, en cartes à
  liseré vert et pictogramme « i ». Les points d'auto-écoles de la carte prennent la couleur « nuancée ».
- **Tableaux « 17 vérifications » et « Ce que chaque verdict change »** : la colonne Verdict s'affiche en **badge
  coloré** (pilule), au lieu de colorer le fond de la cellule (tableaux rendus en HTML, `_table_verdict`).
- **i18n** : les blocs `<style>…</style>` sont désormais protégés comme un tout (au lieu d'exclure toute la chaîne),
  pour que le texte qui les entoure se traduise. Termes de verdict et d'interface fixés à la main en anglais.

## 16. Évolutions — tous les onglets (chiffres clés)

- **Liseré coloré en bas de chaque carte** de chiffre clé, sur les 4 onglets : Synthèse par verdict (vert/jaune/gris),
  Mobilité bleu, Sécurité routière orange, Réseau jaune-or (`carte_kpi(bordure=…)`).
- **Chiffre, phrase et constat (réserve) centrés** dans chaque carte (`rangee_kpi(centre=True)` ; la réserve est
  centrée et sans filet séparateur en mode centré).
- Carte « Confirmées » : texte « L'énoncé du défi est largement vérifié. » remplacé par
  « Les données confirment les principaux constats. »

## 17. Évolutions — onglet Réseau et carte des constats (sur design/palette-a, après la fusion de design/traduction)

- Onglet « Réseau » renommé **« État du réseau routier »**.
- **Carte des constats** réunie en une seule rangée : la carte, sa légende et le bouton à gauche ; à droite, les
  3 encarts nationaux puis les constats cartographiés — plus d'espace vide au-dessus des cartes à pictogramme « i ».
- Le texte « Les immatriculations, les permis et les accidents… » passe dans une **carte à fond blanc** (liseré
  bleu, pictogramme « i »), au lieu d'une simple légende grise.
- Cartes d'encart : `overflow: hidden` pour un bord net (correction du « haché » en bas de la carte « Accidents par
  territoire »).


## 18. Évolutions — onglet Mobilité (sur design/palette-a)

- **Icônes de thème sur les 3 chiffres clés**, chacun avec sa propre couleur de liseré bas (plus de liseré uniforme) :
  « Immatriculations sur 20 ans » → pictogramme *permis/plaque* (bleu `#2474C6`), « Croissance annuelle » →
  *véhicule* (vert `#16834A`), « Part des motos » → *moto* (orange `#EB6834`). Deux nouvelles icônes ajoutées au
  dictionnaire `ICONES` de `composants.py` : `permis` et `moto`.
- **Graphe « Immatriculations par groupe » en pleine largeur** (suppression de la colonne de droite), et la carte
  **Constat** passe **sous la section**, comme sur les autres pages.
- Titre de section : « Immatriculations par groupe, 1990–2024 » → **« Immatriculations par groupe de véhicules,
  1990–2024 »**.
- **Les constats sous chaque graphe passent en cartes blanches à pictogramme « i » et liseré vert** (`note_carte`),
  au lieu de simples légendes grises :
  - Permis : « 2013 non renseignée… Cela s'explique car l'année 2013 n'est pas renseignée dans les sources. »
    (mention « Niveau A » retirée).
  - Ratio : « Sur 2007–2024, **40 motos**… **moins de 2,5 véhicules**… **Le permis F**… » (chiffres et « permis F »
    en gras ; « Niveau B » retiré).
  - Parc : « En 2024 : **751 398 véhicules**… dont **449 226 motos**… » (chiffres en **violet** via la classe `.lieu` ;
    « Niveau C » retiré).
- **i18n** : 12 nouveaux segments traduits (en/ee/kbp) ; anciennes chaînes remplacées nettoyées des locales.

## 19. Évolutions — onglets Sécurité routière et État du réseau routier (sur design/palette-a)

**Sécurité routière**
- **Icônes de thème** sur les 3 chiffres clés : *tués* (triangle rouge), *véhicule* (accidents), *alerte* (cercle « ! »
  rouge, estimation OMS). Liseré bas conservé sur le thème orange.
- Section « Les 6 taux » : graphe **en pleine largeur**, carte **Constat** sous la section, note de fin passée en
  **carte « i » verte** (comme sur l'onglet Mobilité).
- Notes de fin de graphe en **cartes « i » vertes** : séries annuelles (« Niveau A » → « Sources »), tués par usager
  (chiffres **60 %** et **54,7 % à 59,7 %** en gras ; « Niveau C » → « L'analyse faite »), estimation OMS
  (**2,63 fois** en gras ; « Niveau C » retiré).
- Encadré **Limite** retitré « Limites analytiques » ; texte avec **à l'échelle nationale** et **× 2,63** en gras
  (nouveau paramètre `limite(texte_html=…)`).

**État du réseau routier**
- **Icônes de thème** sur les 3 chiffres clés, avec liseré assorti : *route verte* (réseau évalué, liseré vert),
  *route rouge* (mauvais état, liseré rouge), *triangle jaune-or* (tronçons en mauvais état). Nouvelles icônes
  `route_vert`, `route_rouge`, `troncons`, `alerte` dans `ICONES`.
- Tableau des 84 tronçons **en pleine largeur** (HTML `_table_troncons`) : colonne **Type** en **badge** (revêtue vert,
  non revêtue jaune-or), colonne **Zones traversées** avec **chaque zone dans sa couleur** (palette des 39 préfectures,
  `COULEUR_ZONE`), colonnes de km alignées à droite. Carte **Constat** ramenée sous la section.
- Les notes de fin de graphe restantes passent en **cartes « i » vertes**, chiffres et km en gras ; mentions
  « Niveau C » retirées.
- **i18n** : 20 nouveaux segments traduits (en/ee/kbp) ; « 7 tronçons » / « 49 tronçons » fixés en anglais
  (« sections »).

## 20. Carte du réseau et des auto-écoles (sur design/palette-a)

- Texte d'introduction dans une **carte blanche** (`entete(carte=True)`).
- 4 chiffres clés avec **icône de thème** et **liseré assorti** (couleur de l'icône) : réseau dégradé → *route rouge*,
  auto-écoles recensées → *établissement vert*, préfectures sans auto-école → *école jaune*, équipements →
  *signalisation bleue*. Contenu **centré** (`centre=True`). Nouvelles icônes `etablissement`, `ecole_jaune`,
  `signalisation` dans `composants.ICONES`.
- **Carte principale en pleine largeur** (suppression de la colonne de droite) ; les 3 réglages **sur une même
  rangée** (Couche, Tracé, Équipements) + case Auto-écoles. La carte **Constat** passe **sous la section**.
- **Filtre « État du réseau » séparé** : les 5 vues « État du réseau : … » sont retirées de « Couche » (qui ne
  garde que les couches thématiques) et pilotent une **seconde carte**.
- **Seconde carte « L'état du réseau routier »** : préfectures colorées **par zone** (COULEUR_ZONE, fond atténué),
  **tronçons colorés selon leur état dominant** (bon vert, moyen jaune-or, mauvais rouge, en travaux bleu, non
  évalué gris pointillé), **limites des 5 régions en couleurs distinctes** (COULEUR_REGION). Filtre multiselect des
  états avec pastilles de couleur ; suit les filtres de la barre latérale. Label « État du réseau routier sur cette
  carte ».
- **Limites des 5 régions colorées** aussi sur la carte principale (au lieu du trait gris unique).
- **Points des auto-écoles** : agréées en **vert** et agrandies ; non agréées / statut non renseigné en **jaune-or**
  (visibles) avec contour foncé.
- **Tableau des 272 auto-écoles** : passé en tableau HTML avec **badge de statut coloré** (agréée vert, antenne vert
  pâle, non agréée jaune-or, non renseigné gris), colonne **« À vérifier » en badge** (au lieu de colorer la ligne),
  **zones colorées**. Légende de bas de tableau en **carte « i » verte** (chiffres en gras/couleur).
- Section **« Ce que la carte ne montre pas »** : passée en **carte « i » à liseré jaune** (`note_carte(couleur="jaune")`,
  nouvelle classe CSS `.lisere-jaune`).
- **i18n** : nouveaux segments traduits (en/ee/kbp) ; correctif `html.escape(quote=False)` sur les noms propres du
  tableau des auto-écoles (l'apostrophe échappée fragmentait les noms à la traduction).

## 21. Carte — les 3 cartes sur une même grille horizontale (sur design/palette-a)

- Les **3 cartes réunies dans une seule figure** (panneaux `geo` / `geo2` / `geo3`) côte à côte, pleine largeur :
  carte 1 (Togo, couche thématique), carte 2 (zoom Maritime), carte 3 (état du réseau : zones en fond, tronçons
  par état, régions colorées). Titres numérotés au-dessus de chaque panneau.
- **Réglages déplacés dans la barre latérale** (bloc « Réglages de la carte », visible seulement sur la page Carte,
  sous les filtres de territoire) : Couche, Tracé, Auto-écoles, Équipements et États du réseau.
- **Filtre « Équipements » appliqué aussi à la carte 3** (`dessiner_etat` ajoute les points d'équipement).
- Suppression de la seconde `st.plotly_chart` séparée ; légendes des cartes 1 et 3 réunies sous la figure unique.
- Maquette de validation générée hors-ligne (rendu cartésien, le fond Plotly interactif n'étant pas chargeable
  dans le bac à sable ; la vraie appli garde survol/zoom/clic).

## 22. Barre latérale et page Carte — réorganisation (sur design/palette-a)

- **Réglages de la carte placés au-dessus du bouton « Réinitialiser les filtres »** : app.py réserve un conteneur
  dans la barre latérale (`st.session_state["sidebar_reglages"]`) entre les pastilles de filtre et le bouton ; la
  page Carte y dépose ses sélecteurs (ils n'apparaissent donc que sur cette page).
- **Repères chiffrés sous le bouton** passés en **liste à puces** (classe `.sidebar-stats`) : 39 préfectures · 6 zones ;
  population 2022 (INSEED) 8,095 M hab. ; 272 auto-écoles dont 132 agréées ; 23 préfectures sans auto-école agréée ;
  13 préfectures au réseau dégradé ; 16 797 équipements de sécurité routière.
- **Slogan + illustration de route bien en bas de la barre latérale** (inchangé, mais plus rien ne passe en dessous
  maintenant que les réglages de la page vont dans le conteneur réservé).
- Page Carte : le texte sous le titre « Le Togo, préfecture par préfecture » et la note « Projection Mercator… »
  réunis dans une **carte blanche à liseré bleu et pictogramme « i »** ; **titre « La préfecture choisie » retiré**.
- Légende « N préfectures affichées… » passée en **carte « i » verte** ; encadré **« Limite de cette page » en liste
  à puces** (une limite par ligne).

## 23. Priorités — carte d'introduction et chiffres clés (2026-10-12, branche design/pages-pilotage)

- Texte d'introduction dans une **carte blanche** (`entete(carte=True)`), comme sur les autres pages.
- **5 chiffres clés** ajoutés sous l'intro (`rangee_kpi(centre=True)`), icône de thème + liseré assorti, étiquette
  de niveau C :
  - Zones en difficulté — **4 sur 6** (icône alerte jaune-or « troncons »)
  - Préfectures qui cumulent — **5** (641 955 hab., icône « alerte » rouge)
  - Les 10 premières — **1,42 M** hab. (icône « population » bleu)
  - Levier réseau — **13** préfectures (304,6 km, icône « route_rouge »)
  - Levier formation — **23** préfectures (41 auto-écoles, icône « etablissement » vert)
- La 6e carte envisagée (« Le classement tient / robustesse ») **n'est pas** faite en chiffre clé : le message passe
  dans une **carte Constat** ajoutée en tête de la section « Le classement tient-il ? » (« classement stable ; aucun
  test ne change plus de 2 des 10 premières ; 7 préfectures restent dans les 6 tests »).
- Branche `design/pages-pilotage` partant de `dev` (après la fusion de `design/palette-a` sur `dev`), pour les pages
  Priorités, Recommandations, Horizon 2031 et Méthodologie.

## 24. Priorités — section 1, cartes de zones et mise en forme (2026-10-12, branche design/pages-pilotage)

- **Constat déplacé avant la section** « Les zones en difficulté », comme sur les autres pages.
- **Tableau pleine largeur** (suppression de la disposition en deux colonnes).
- **Carte verte** (`note_carte(couleur="vert")`) : médiane des zones et cas limite des Savanes (remplace 2 `note()`).
- **Carte warning** (fond jaune, `.limite`) : accès rural grille WorldPop, reformulé (« **Accès rural (grille
  WorldPop)** : mesuré avec la grille… »).
- Section « Ce que dit chaque zone » remplacée par **« Diagnostic par zone »** : 6 cartes blanches en grille 3×2
  (`.zone-grille`, `.zone-carte`), chaque carte porte le nom de la zone en couleur et sa phrase de diagnostic ;
  liseré en bas de la couleur de la zone, effet hover (élévation + ombre). CSS ajouté dans `theme.py` + styles
  inline pour contourner le cache CSS de Streamlit.
- **Carte blanche avec liseré vert** à gauche pour le texte « Par région : … Région Maritime … » (remplace 2
  `st.caption()`).
- **Carte fond blanc** pour le total des 5 préfectures qui cumulent (remplace `note()`).
- Titre **« Les 10 premières préfectures en priorité »** (au lieu de « Les 10 premières »).
- **Carte warning** pour le texte sur les déficits et la nature du zéro (remplace `note()`).
- Import de `note_carte` ajouté dans `priorites.py`.

## 25. Priorités : section « Le classement tient-il ? » et finitions (2026-10-12)

- **Entrent / Sortent** : icônes de tendance ▲ (vert) et ▼ (rouge) devant les clés ; noms des zones
  colorés en vert (entrent) et rouge (sortent) ; les clés « Entrent » et « Sortent » sont elles-mêmes
  colorées.
- **Formule du score** : l'ancien `st.caption` remplacé par une `note_carte` bleue avec pictogramme ;
  noms des zones de contrôle (**Kloto**, **Ogou**, **Est-Mono**, **Oti-Sud**, **Haho**, **Tchaoudjo**)
  en gras.
- **Règle de stabilité** : l'ancien `note()` remplacé par une `note_carte` verte ; clés **Règle**,
  **Toujours en tête** et **Les moins sûres** en gras.
- **Mô, hors class.** : titre abrégé (au lieu de « hors classement ») ; liseré passé du gris au jaune
  constat (`#eda100`).
- **Limites de cette page** : titre changé en « Limites de cette page » ; « Classement en C » remplacé
  par « Classement par estimation » ; contenu affiché par ligne (puces `•` + `<br>`) via `limite()`
  avec `texte_html`.

## 26. Priorités : cartes egale=True, boutons côte à côte (2026-10-12)

- **Synthèse et Limite de même hauteur** (`egale=True`) sur la page Priorités.
- **Boutons alignés** : « Exporter (CSV) » et « Voir le classement sur la carte → » sur la même ligne
  horizontale via `st.columns(2)`.
- **Espacement dans Limites** : `<br><br>` entre les puces pour occuper l'espace restant.

## 27. Recommandations : refonte des cartes et de la mise en page (2026-10-12)

- **Entête en carte** : `entete(…, carte=True)` — le texte sous le titre est maintenant dans une carte
  blanche avec liseré bleu-foncé à gauche, comme sur les autres pages.
- **Doublon supprimé** : la barre « 15 recommandations · les habitants ne s'additionnent pas… » a été
  retirée (doublonnait le texte de l'entête) ; la mention « Priorité et zone se choisissent dans la
  barre latérale » est intégrée au texte de l'entête.
- **Icônes de thème** dans chaque carte de recommandation : pastille emoji colorée (🛣️ Réseau,
  🏫 Formation, 🚦 Sécurité routière, 📍 Zones les moins desservies, 📊 Données) à gauche du titre,
  avec le nom du thème en dessous. Dict `THEME_EMOJI` ajouté.
- **Badge Moyenne en jaune-or** : `PRIO_COUL["Moyenne"]` passe de `#3987e5` (bleu) à `#eda100` (or).
- **Habitants en grand format** : le nombre d'habitants (colonne `Habitants`) s'affiche en Fraunces
  1.8 rem avec « habitants / concernés » en petit à droite, comme dans l'image de référence.
- **Badges horizon en violet** : fond `#ece9fb`, texte `#4a3aa7` (au lieu du gris `#efece4`).
- **Note bleue « Pour aller plus loin »** : le `st.caption` remplacé par `note_carte(…, couleur="bleu")`
  pour le texte sur les 4 actions des producteurs de données.
- **Synthèse pleine largeur** : la carte « Synthèse chiffrée » sort du `st.columns(2)` et prend toute
  la largeur de la page.
- **Constat et Limite côte à côte** : `constat(…, egale=True)` et `limite(…, egale=True)` dans un
  `st.columns(2)`, même hauteur. Paramètre `egale` ajouté à `constat()` dans `composants.py`.

## 28. Recommandations : espacement, hover et réordonnancement (2026-10-12)

**Fichiers :** `recommandations.py`, `theme.py`, `_CONSTRAINTS_DEV.txt`.

- **Espacement des fiches** : `st.markdown("")` ajouté après chaque rangée de 3 colonnes dans la
  fonction `grille()` (cartes de recommandation) et dans la boucle des fiches préfectures (onglet
  « Actions par zone »). Les cartes n'étaient plus collées verticalement.
- **Hover sur `.reco-carte`** : CSS ajouté dans `theme.py` — `translateY(-2px)` + ombre au survol,
  sans balayage de couleur (le `::after` du `.kpi` n'est pas repris). Respect de `prefers-reduced-motion`.
- **Constat/Limite avant Synthèse** : l'ordre en bas de page passe de Synthèse → Constat+Limite
  à Constat+Limite → séparation → Synthèse, conformément à la maquette. Une ligne vide
  (`st.markdown("")`) sépare les deux blocs.

## 29. Horizon 2031 : design unifié (2026-10-12)

**Fichiers :** `horizon.py`, `_CONSTRAINTS_DEV.txt`.

- **Entête en carte** : `entete(…, carte=True)` — le texte de réponse est maintenant dans une
  carte blanche avec liseré bleu-foncé, comme les autres pages.
- **KPI avec icônes et chiffres centrés** : `rangee_kpi(…, centre=True)`, chaque `carte_kpi` reçoit
  un `icone` (`population`, `ecole_jaune`, `route_rouge`, `route`) qui ajoute la pastille du thème
  et le liseré bas coloré automatiquement.
- **Couleurs par région dans le tableau** : quand la maille est « Région »,
  `COULEUR_REGION` est utilisé au lieu de `COULEUR_ZONE` (import ajouté).
- **Constat déplacé sous la section** : la carte Constat sort de la colonne droite et s'affiche
  en pleine largeur sous le tableau et le bouton d'export, dans la section « Ce qu'il faut ajouter ».
- **Expander pleine largeur** : « Les recommandations chiffrées, à cet horizon » sort de la
  colonne gauche pour occuper toute la largeur de la page.
- **5 note_carte vertes** : les `st.caption` et `note()` remplacés par `note_carte(…, couleur="vert")`
  avec pictogramme « i » vert et liseré vert à gauche, pour les textes :
  « Auto-écoles agréées… », « Population par zone… », « Trait plein : observé… » (avec
  « Sur fond gris » en gras), « Le plafond suppose… », « Ces sites orientent… ».
- **Import `note` conservé** pour la note « Aucune zone n'atteint… » (non listée par l'utilisateur).


## 30. Vue nationale : carte double, auto-écoles et fond par région (2026-10-12)

**Fichiers :** `vue_nationale.py`, `_CONSTRAINTS_DEV.txt`.

- **Auto-écoles — mêmes couleurs et tailles que la page Carte** : agréées en vert
  `#16834a` (taille 10/12), non agréées en jaune-or `#e6b422` (taille 7/8), avec
  les mêmes bordures (blanc pour agréées, or pour non agréées). Remplace les anciens
  cercles blancs/gris de taille 6.
- **Zoom Maritime et Grand Lomé (geo2)** : une seconde carte (inset) est ajoutée à
  droite de la carte principale, cadrée sur les préfectures de la région Maritime.
  Les noms des préfectures sont écrits sur le zoom (`_centroides_vn`, shapely). Le
  titre de l'annotation affiche le nombre d'auto-écoles agréées dans la zone
  (calculé dynamiquement : 108 des 132).
- **Fond coloré par région (couche « Régions »)** : chaque préfecture est colorée
  avec la `COULEUR_REGION` de sa région (opacity 0.55), au lieu de remplir le
  polygone régional entier. Les limites des préfectures restent visibles en blanc.
  Les contours des régions sont toujours tracés en couleur (2.2 px) sur toutes les
  couches.
- **Boucle dessiner (geo, geo2)** : les traces sont ajoutées aux deux cartes via
  `for cible, inset in [("geo", False), ("geo2", True)]`. Légende affichée
  uniquement sur la carte principale (`showlegend=sl`).
- **Import shapely** ajouté (`shp_shape`) pour les centroïdes. `fenetre_geo` n'est
  plus utilisé pour cette carte (layout manuel avec `lonaxis`/`lataxis`), mais
  reste importé pour le mini-carte réseau dans les thèmes.
- **Sous-titre** de `titre_bloc` mis à jour pour mentionner l'agrandissement Maritime.
- **Grammaire** corrigée dans `_CONSTRAINTS_DEV.txt` (lignes 265-269).

## 31. Rapport PowerPoint — `Togo-Mobilite-Securite-Routiere-Defi1.pptx` (2026-10-12)

**Livrable attendu par l'énoncé** : un rapport PowerPoint de 10 diapositives au plus, noté au
critère C4 (structure, clarté, méthodologie, qualité rédactionnelle), la qualité des conclusions
(C2) s'y jugeant aussi.

**Processus repris du défi 2** (`EconomyNumeric-Challenge2`) : un plan écrit d'abord, un script qui
génère le fichier, des contrôles automatiques, un aperçu relu à l'œil.

**Fichiers :** `tmp/ppt-plan.md` (le plan, hors dépôt : `tmp/` est ignoré par git),
`scripts/build_presentation.py` (le script), `tmp/ppt_assets/` (6 figures et les armoiries),
`Togo-Mobilite-Securite-Routiere-Defi1.pptx` (la sortie, à la racine).

- **Aucun chiffre retapé (R-19)** : le script lit les tables de `data/analysis/` par
  `dashboard/donnees.py` et prend ses couleurs dans `dashboard/theme.py`. Le rapport et le tableau
  de bord portent donc les mêmes chiffres et la même identité, par construction. Les constats qui
  nomment des territoires (les 5 préfectures qui cumulent, « ni le Golfe ni Agoè-Nyivé ») sont
  dérivés des tables.
- **Règle des codes appliquée au rapport** : aucun code interne, nom de fichier, numéro de
  document ni nom de source entre parenthèses ; « auto-école agréée » et « accidents constatés »
  partout. Seule la diapositive 2 parle de méthode, en clair.
- **Les 10 diapositives** : couverture (synthèse exécutive), méthode, puis un objectif par
  diapositive (mobilité, sécurité routière, réseau, couverture), les territoires, l'arbitrage
  « priorité n'est pas population », le plan d'action en 5 blocs, les 4 décisions.
- **`python-pptx` n'est pas dans `.venv`** : le script ajoute le site utilisateur **en fin** de
  `sys.path` (les versions de `.venv` gardent la priorité). `.venv` n'est pas modifié.
- **Graphiques redessinés en matplotlib** : Plotly n'exporte pas d'image sans Chrome. Armoiries
  rasterisées une fois par `rsvg-convert` (`python-pptx` ne lit pas le SVG) ; attribution
  CC BY-SA 4.0 au pied de la couverture, comme l'exigent les contraintes.
- **Contrôles** : 126 contrôles, 0 échec (10 diapositives, 16:9 exact, 28 motifs proscrits absents,
  55 chiffres relus directement dans les CSV sans passer par le code du tableau de bord, mention de
  source sur chaque diapositive intérieure, aucune forme hors cadre, test négatif) ; validation
  OOXML passée ; aucune réduction de taille de texte dans la version finale.
- **Ce que l'aperçu dessiné a fait corriger** : l'unité d'un chiffre clé qui passait à la ligne et
  écrasait sa phrase (la taille de la valeur s'ajuste désormais avant écriture) ; le bandeau
  « trait commun » qui passait sous le bandeau de limite (diapositive 6) ; le tableau des tests de
  robustesse qui passait sous son bandeau (diapositive 8) ; les étiquettes des 6 taux qui se
  chevauchaient (barres passées à l'horizontale) ; deux légendes posées sur les données
  (diapositives 3 et 5) ; les figures qui flottaient dans du blanc (proportions alignées sur leur
  panneau) ; l'emoji drapeau retiré du fichier PowerPoint (police non garantie à la lecture).
- **Deux chiffres harmonisés avec le tableau de bord** : la cible du permis moto est celle des
  recommandations (5 513 par an), et non celle de l'annexe ; le multiplicateur × 4,56 est daté
  (2002 → 2022), 2004 étant une année de rupture de série.

**Reste à trancher avant l'envoi** : le nom affiché en couverture (« Addi Carters », lu dans
`.env`) et l'URL du tableau de bord (déploiement Streamlit Cloud prévu, aucune adresse dans le
dépôt — la constante est laissée vide, la ligne n'est alors pas rendue). Deux constantes en tête
du script. **Non vérifié** : le rendu dans PowerPoint lui-même (ni PowerPoint ni LibreOffice sur
ce poste).

## 32. Horizon 2031 : mise en page élargie et design unifié (2026-10-12)

**Page** : `dashboard/views/horizon.py` · **Fichier contraintes** : `_CONSTRAINTS_DEV.txt`
lignes 261-275 (grammaire corrigée).

- **Section « Ce qu'il faut ajouter »** : suppression de la colonne droite (`st.columns`),
  carte et tableau désormais en pleine largeur. Le `st.caption` de la colonne droite et
  le `note()` conditionnel sont fusionnés en un seul `note_carte(..., couleur="vert")`
  placé sous la carte, avec le texte complet (usure du réseau, classes fixes, projection).
- **Section « Où ouvrir les auto-écoles »** : suppression des colonnes, carte en pleine
  largeur. Points des auto-écoles agréées agrandis (taille 10/12) et colorés en vert
  `#16834a` avec bordure blanche (comme page Carte). Points des 48 sites retenus passés
  du bleu foncé `#0d366b` au rose clair `#e88a98` avec bordure `#d04060`. Légende mise à
  jour (pastille verte, losange rose). Constat déplacé sous la carte (au lieu de la colonne
  droite).
- **Carte « Limite »** : titre passé à « Limites de cette page », format en puces (•) avec
  `texte_html` et `egale=True`, aligné sur le format de la page Priorités.
- **Grammaire** corrigée dans `_CONSTRAINTS_DEV.txt` (lignes 261-275).

## §33 — Page Méthodologie : cards, bordures, note_carte (2026-10-12)

Fichiers : `dashboard/views/methodologie.py`, `_CONSTRAINTS_DEV.txt` (lignes 284-302).

- **En-tête carte** : ajout de `carte=True` à l'appel `entete()` pour afficher la
  réponse dans une carte à fond blanc, comme sur les autres pages.
- **Section « Comment nous avons travaillé »** : chaque étape (1-9) est maintenant dans
  un card avec bordure arrondie (`border:1px solid #e2dfd6;border-radius:10px`) et fond
  blanc.
- **Section « Sources »** : tableau enveloppé dans `st.container(border=True)` pour une
  bordure visible. Le `note()` remplacé par `note_carte()` avec pictogramme « i » vert,
  texte reformulé pour le décideur (localisation WorldPop, dépendance accès rural).
- **Section « Limites majeures »** : refonte complète. Chaque limite (1-8) est dans un
  card bordé avec : badge numéroté rouge/corail (`#f4dfe1`/`#ce1126`), titre en gras,
  description en gris. Design aligné sur l'image de référence.
- **Section « Niveaux de preuve »** : tableau dans `st.container(border=True)`.
  `st.caption()` remplacé par `note_carte()` (texte reformulé : 3 compléments + accès
  rural estimés).
- **Section « Questions ouvertes »** : tableau dans `st.container(border=True)`.
  `st.caption()` remplacé par `note_carte()` (texte reformulé : « une seule donnée
  manquante bloque 7 hypothèses »).
- **Section « Les zones les moins desservies »** : tableau dans `st.container(border=True)`.
  `st.markdown()` remplacé par `note_carte()` (texte reformulé : localisation réelle vs
  uniforme, Centrale vs Savanes).
- **Grammaire** corrigée dans `_CONSTRAINTS_DEV.txt` (lignes 284-302) : « come »→« comme »,
  « autes »→« autres », « cahque »→« chaque », « etre »→« être », « balcn »→« blanc »,
  « bordrures »→« bordures », « uatres »→« autres », « decideur »→« décideur »,
  « travial »→« travail ».

## 32. Alerte de visite Telegram, adaptée à Streamlit Cloud (2026-10-12)

**Demande :** reprendre l'intégration Telegram du défi « Économie numérique »
(`EconomyNumeric-Challenge2/dashboard/notify.py`) pour ce projet, qui sera déployé sur
Streamlit Community Cloud.

**Fichiers :** `dashboard/notify.py` (nouveau), `dashboard/app.py` (appel),
`dashboard/.streamlit/secrets.toml.example` (nouveau), `dashboard/README.md`, `.gitignore`.

- **Une notification par visite**, envoyée à un bot Telegram privé : savoir qu'un jury ou un
  partenaire a ouvert le tableau de bord. Appel `signaler_visite()` dans `app.py`, juste après
  `appliquer_theme()`, pour qu'un incident réseau ne retarde jamais le premier rendu.
- **Ce qui change par rapport au défi 2, qui tournait sur Heroku :**
  - les identifiants sont cherchés dans l'environnement **puis dans `st.secrets`** (Streamlit
    Cloud : *Settings → Secrets*, au format TOML). L'accès à `st.secrets` lève quand aucun
    fichier de secrets n'existe : l'exception est attrapée, l'absence vaut « alerte inactive » ;
  - **l'adresse IP** : le routeur Heroku ajoutait l'adresse observée à la *fin* de
    `X-Forwarded-For`, la dernière valeur y était donc la seule sûre. Streamlit Cloud ne
    documente pas ce qu'il écrit : on prend `X-Real-Ip` s'il existe, sinon la **première** valeur
    de `X-Forwarded-For` (convention courante). Les deux sont falsifiables ; le message dit
    « IP déclarée » et rien n'en dépend ;
  - le titre de l'application est lu dans `composants.MARQUE` (et non dans `i18n`, le défi 2
    étant bilingue).
- **Garde-fous conservés** : une alerte par session (Streamlit réexécute le script à chaque
  interaction), envoi dans un thread démon avec délai de 5 s, plafond de 50 envois par jour
  compté en UTC, aucune exception ne sort de `signaler_visite()`, `urllib` de la bibliothèque
  standard (aucune dépendance ajoutée à `requirements.txt`).
- **Inactif par défaut** : sans les deux valeurs, le module ne fait rien — poste local, exécution
  hors ligne. Le `.env` du dépôt n'est pas lu.
- **`.gitignore`** : le motif `.streamlit/secrets.toml` contenait une barre oblique, donc était
  ancré à la racine et ne couvrait pas `dashboard/.streamlit/secrets.toml`. Remplacé par
  `**/.streamlit/secrets.toml` (vérifié avec `git check-ignore`).
- **Contrôles** : 15 contrôles, 0 échec, sans aucun appel réseau (`_envoyer` remplacé) — inertie
  sans configuration, une seule variable ne suffit pas, une alerte par session, un nouveau
  visiteur signalé, plafond quotidien et sa remise à zéro le lendemain (en UTC), extraction de
  l'IP dans ses quatre cas, titre de l'application présent, message produit hors contexte HTTP,
  en-têtes tronqués à 180 caractères, et `signaler_visite()` qui ne lève jamais même quand la
  construction du message échoue. Application relancée : HTTP 200, aucune erreur au journal,
  aucun envoi en local.

**À faire avant l'évaluation :** poser `TELEGRAM_BOT_TOKEN` (jeton du `.env`) et
`TELEGRAM_CHAT_ID` dans les secrets de l'application. L'identifiant de conversation manque encore :
écrire un message au bot, puis lire `getUpdates`. **Après l'évaluation :** retirer les deux
secrets — la notification transporte l'IP déclarée et l'agent utilisateur du visiteur.

## 33. Archive de soumission — `Togo-Defi1-MobiliteSecuriteRoutiere.zip` (2026-10-12)

**Demande :** une archive du projet **sans le rapport `.pptx` ni son script** (envoyés séparément),
**sans `workspace/` ni `methodology/`**, sur le modèle de ce qui a été fait au défi
« Économie numérique » (`EconomyNumeric-Challenge2/scripts/make_submission.sh`).

**Fichier :** `scripts/make_submission.sh` (nouveau). `bash scripts/make_submission.sh` depuis
n'importe où. Résultat : **6,7 Mo, 185 entrées.**

- **Liste blanche, pas liste noire** (principe repris du défi 2) : chaque élément à inclure est
  nommé explicitement ; ce qui n'y figure pas ne peut pas entrer dans l'archive par oubli. Les
  contrôles de la fin vérifient ensuite l'absence de ce qui ne doit jamais s'y trouver.
- **Ce que l'archive contient** : les 13 documents (01 à 11 et l'annexe Horizon 2031), le cadre de
  décision du 02 (ses 9 tables et le classeur), `dashboard/`, `scripts/`, `notebooks/`,
  `requirements.txt`, et les données que le tableau de bord lit (`data/analysis/**/*.csv`,
  `data/processed/`, `data/reference/`, `data/raw/_SOURCES.csv`).
- **Ce qui en est écarté, et pourquoi** : le `.pptx` et `scripts/build_presentation.py` (envoi
  séparé) ; `workspace/` et `methodology/` (documents de travail) ; `tmp/` ;
  `_CONSTRAINTS_DEV.txt` et `_GUARD_RAILS_REPO.txt` (consignes internes) ; `.env`, `.git/`,
  `.venv/`, `dashboard/.streamlit/secrets.toml` (le jeton du bot — le **modèle**, lui, est
  inclus) ; `data/raw/` (81 Mo, publiés sur leurs portails ; seul le registre des sources est
  gardé, car la page Méthodologie le lit) ; `data/interim/` (9,1 Mo, ne se rejoue pas sans les
  bruts) ; **`data/analysis/04_understanding/rapports/` (76 Mo)**, les 52 rapports de profilage
  HTML, qui pesaient à eux seuls plus de dix fois le reste et que `scripts/profil_04.py`
  régénère.
- **Quatre contrôles dans le script** : aucun des 15 motifs écartés n'est présent ; les 16
  fichiers indispensables au lancement sont là ; les 45 tables de `data/analysis/` sont toutes
  dans l'archive (aucune perdue par un motif d'exclusion) ; la taille est refusée au-delà de
  15 Mo et signalée au-delà de 8 Mo — au défi précédent, le support a jugé trop lourde une
  archive de 12,1 Mo.
- **Vérifié sur l'archive extraite, pas seulement sur sa liste** : le tableau de bord s'y lance
  (HTTP 200, aucune erreur au journal) et **41 lectures sur 41 réussissent** — les 31 tables de
  `data/analysis/`, les tables préparées, les tables de référence, le registre des sources, la
  table maîtresse, les 3 couches géographiques et les 3 jeux de contours. L'archive se suffit à
  elle-même.
- **Piège corrigé** : avec `set -o pipefail`, un `unzip -Z1 … | grep -q` échoue sur un SIGPIPE
  quand `grep` sort au premier résultat avant la fin d'`unzip`. Le contrôle signalait alors comme
  manquant un fichier pourtant présent. Le contenu est désormais listé **une seule fois** dans une
  variable, que les contrôles lisent par « here-string ».

**L'archive n'est pas suivie par git** : la commiter, ou l'ajouter à `.gitignore`, comme pour le
`.pptx`.

## 34. Documents du jury : en-têtes retirés, § 8 du 11 corrigé (2026-10-12)

**Demande :** corriger le document 11 pour qu'il décrive la structure réelle du code ; copier les
documents 01 à 11 dans `workspace/` et retirer, dans les exemplaires qui partent au jury, les
dates de gel et de création et le statut.

**Fichiers :** `scripts/entetes_jury.py` (nouveau), `workspace/documents_complets/` (nouveau,
13 copies + un README), les 12 documents de la racine, `11_tableau_de_bord.md` (§ 3, § 8 et
journal), `dashboard/app.py` et `tmp/ppt-plan.md` (mention de langue).

- **Document 11, § 8 réécrit sur le code écrit.** Le plan décrivait un `dashboard.zip` autonome,
  `app.py` à la racine du zip et une copie des données dedans, faite par « un script du livrable
  qui vérifie l'empreinte de chaque fichier ». Ce script n'existe pas et la structure est autre :
  l'archive porte **le projet entier**, `dashboard/` et `data/` côte à côte, et
  `scripts/make_submission.sh` la construit. `donnees.py` lit `dashboard/data/` si ce dossier
  existe, sinon `../data` : les deux dispositions marchent, celle du dépôt évite de dupliquer
  12 Mo. Ajoutés à l'arborescence : `i18n.py` et `locales/`, `notify.py`, le modèle de secrets ;
  versions des dépendances alignées sur `dashboard/requirements.txt` (plotly 7.1, et non 5.15).
  Lancement et déploiement corrigés. Les cinq autres mentions de `dashboard.zip` du document
  suivent, et une ligne est ajoutée au journal des décisions.
- **§ 3 complété** : le sélecteur de langue (français, anglais, éwé, kabiyè) n'était écrit nulle
  part dans le 11.
- **Deux mentions « français seul » corrigées** (`dashboard/app.py`, `tmp/ppt-plan.md`) : elles
  dataient de l'abandon du bilingue, la traduction a été intégrée depuis. Le **rapport**, lui,
  reste en français seul.
- **En-têtes de version retirés** des 12 documents de la racine par `scripts/entetes_jury.py` :
  la ligne `**Version :** … — **Date :** … — **Statut :** …` et, pour le 01, `**Validé par :**
  [noms à compléter]`. Le reste est intact, ligne pour ligne (vérifié par `diff` avec la copie).
  Les lignes `**Projet :**` et `**Sources :**` restent.
- **Les documents complets sont dans `workspace/documents_complets/`**, avec leur en-tête : c'est
  là que se lit l'historique des versions. Le script est **idempotent et sans perte** — un
  document n'est copié vers `workspace/` que s'il porte encore son en-tête, donc une relance
  n'écrase jamais une copie complète par une version allégée (vérifié : 12 traités, puis 0).
  `--verifier` dit ce qui serait fait sans rien modifier.
- **Archive reconstruite** : 186 entrées, 6,7 Mo ; aucun en-tête de version dedans ;
  `workspace/` toujours exclu.

**Reste ouvert** (signalé, non fait) : les lignes `**Sources :**` des documents du jury citent
`workspace/_PROJECT.txt` et `methodology/…`, et le § 5 du 11 renvoie 21 fois à
`workspace/design-pageN.md` — dossiers absents de l'archive. Les mentions « (figé) » y subsistent
aussi.
