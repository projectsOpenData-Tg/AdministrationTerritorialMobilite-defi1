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
