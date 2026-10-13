# Maquette du tableau de bord — spécification de reproduction (Défi 1)

*Pour un développeur qui doit réécrire, étendre ou reproduire le tableau de bord « Mobilité et sécurité routière au Togo » et obtenir le même rendu : mise en page, barres, cartes, chiffres clés, onglets, dimensions, couleurs et règles d'affichage.*

Toutes les valeurs (couleurs, tailles, marges, rayons, hauteurs) sont celles du code en production au 13/10/2026 : [dashboard/theme.py](../dashboard/theme.py) pour les jetons et le CSS, [dashboard/composants.py](../dashboard/composants.py) pour les composants, [dashboard/.streamlit/config.toml](../dashboard/.streamlit/config.toml) pour le thème de base, [dashboard/app.py](../dashboard/app.py) pour l'assemblage, [dashboard/donnees.py](../dashboard/donnees.py) pour la lecture des données, [dashboard/i18n.py](../dashboard/i18n.py) pour la traduction, et `dashboard/views/*.py` pour les 8 pages. **En cas de doute, le code fait foi.**

Ce document est le pendant, pour le Défi 1, de la maquette patron [MAQUETTE_dashboard.md](./MAQUETTE_dashboard.md) (tableau de bord du Défi 2 « Économie numérique », conservée comme gabarit d'inspiration). Les deux tableaux de bord partagent l'ossature ; ce fichier décrit ce qui est réellement construit ici et ce qui en diffère.

Journaux de construction, à lire en complément : [workspace/dev-progress.md](../workspace/dev-progress.md) (développement fonctionnel), [workspace/design-progress.md](../workspace/design-progress.md) (changements de design validés un à un).

---

## Sommaire

1. Pile technique et organisation
2. Jetons de design : couleurs, typographie, rayons, ombres
3. Disposition générale de l'écran
4. Barre du haut
5. Barre latérale
6. Pied de page
7. Gabarit d'une page
8. Composants
9. Les 8 pages
10. État, filtres et interactions
11. Quatre langues et format des nombres
12. Cartes et graphiques (Plotly)
13. Pièges connus de Streamlit
14. Recette : liste de contrôle

---

## 1. Pile technique et organisation

| Élément | Choix |
| --- | --- |
| Langage | Python 3.11+ |
| Cadre d'application | Streamlit 1.61 (`layout="wide"`, `initial_sidebar_state="expanded"`) |
| Graphiques et cartes | Plotly (`plotly.express`, `plotly.graph_objects`), choroplèthes sur GeoJSON, `make_subplots` pour les figures multi-panneaux |
| Données | pandas ; geopandas + shapely pour les contours ; tables CSV lues dans `data/analysis/`, `data/processed/`, `data/reference/`, avec `@st.cache_data` |
| Navigation | `st.navigation()` + `st.Page()`, menu en 4 groupes |
| Style | un seul bloc `<style>` injecté par `st.markdown(CSS, unsafe_allow_html=True)` au démarrage (`theme.appliquer_theme()`) |
| Polices | Google Fonts : **Fraunces** (titres et grands chiffres, graisses 500 et 600) et **IBM Plex Sans** (texte, graisses 400, 500, 600) |
| Traduction | 4 langues (fr, en, ee, kbp), pré-traduites hors ligne par NLLB-200 et lues dans `locales/*.json` ; aucun appel réseau à l'affichage |
| Déploiement visé | local, puis Streamlit Community Cloud ; alerte de visite Telegram optionnelle (`notify.py`) |

### Arborescence

```
dashboard/
├── app.py            point d'entrée : config, thème, alerte visite, i18n, logo, barre du haut, menu,
│                     filtres de la barre latérale, navigation.run()
├── theme.py          jetons de couleur (ENCRE, BLEUS, THEME, ETAT, COULEUR_ZONE…) + bloc CSS complet + appliquer_theme()
├── composants.py     barre du haut, en-tête, chiffre clé (+ icônes SVG), bandeaux (constat/synthèse/limite),
│                     note en carte, onglets, export CSV, choroplèthe générique, habillage Plotly, badges, table HTML
├── donnees.py        lecture des tables (cache), contours géo (préfectures/zones/régions), format des nombres FR —
│                     AUCUN recalcul d'indicateur
├── i18n.py           traduction par segments (installer, bi, selecteur) à partir de locales/*.json
├── notify.py         alerte de visite Telegram (facultatif, inactif sans secrets)
├── static/           armoiries-togo-ecu.svg, logo_barre_laterale[_<langue>].svg, logo_togo_icone.svg,
│                     routes_slogan.svg, (logo_togo_ai_lab.png à fournir)
├── locales/          fr/en/ee/kbp.json (traductions commitées) + segments_fr.json (collecte)
└── views/            une page par fichier — JAMAIS un dossier nommé pages/ (voir §13)
    vue_nationale.py comparaison.py evolutions.py carte.py
    priorites.py recommandations.py horizon.py methodologie.py
.streamlit/config.toml   thème de base (§2.1) ; enableStaticServing = true pour servir static/
```

### Règle d'architecture

**Le tableau de bord affiche, il ne calcule pas** (11 §2). Chaque chiffre vient d'une table déjà produite (`data/analysis/**`). `donnees.py` ne fait que lire, joindre et filtrer. Trois exceptions seulement, admises et marquées dans le code :

- le **poids du réseau** dans le score de priorité (page Priorités), recalculé avec la même formule que la table ;
- l'application d'un **seuil choisi par le lecteur** à une valeur déjà calculée (curseur du seuil de mauvais état, page Comparaison) ;
- la lecture d'un **palier d'horizon** choisi par le lecteur (page Horizon 2031), sélection dans la table, pas un calcul.

Aucun chiffre n'est écrit en dur dans une page ; les noms de territoires cités dans les constats sont dérivés des tables (R-19).

---

## 2. Jetons de design

### 2.1 Thème de base (`.streamlit/config.toml`)

```toml
[server]
headless = true
enableStaticServing = true          # static/ servi sous app/static/<fichier>
[client]
toolbarMode = "minimal"

[theme]
base = "light"
primaryColor = "#1769aa"            # bleu soutenu : boutons actifs, onglet actif, liens, sélection des filtres
backgroundColor = "#f4f2ec"         # fond café (conservé du gabarit, à la demande)
secondaryBackgroundColor = "#ffffff"
textColor = "#172b3a"
borderColor = "#e2e8f0"

[theme.sidebar]
backgroundColor = "#0b263d"         # bleu nuit
secondaryBackgroundColor = "#123552"
textColor = "#f8fafc"
primaryColor = "#1769aa"
borderColor = "#24415c"
```

> **Différence avec le gabarit Défi 2 :** la palette passe d'un bleu `#0d366b` / accent jaune clair à une palette « institutionnelle moderne » (bleu nuit `#0b263d`, bleu actif `#1769aa`, bordures `#e2e8f0`), le fond café `#f4f2ec` étant conservé. La navigation active est **bleue pleine**, plus jaune.

### 2.2 Couleurs (`theme.py`)

**Neutres et structure**

| Jeton (code) | Hex | Usage |
| --- | --- | --- |
| `ENCRE` | `#172b3a` | texte principal, valeurs de chiffres clés dans le corps |
| `ENCRE2` | `#334155` | texte secondaire (réponse sous le titre, contexte) |
| `DISCRET` | `#64748b` | texte tertiaire (sous-titres, réserves, fil d'Ariane, groupes) |
| `FILET` | `#e2e8f0` | bordures des cartes et des blocs |
| filet clair | `#eef2f6` / `#efece4` | séparateurs internes, grille des graphiques |
| `FOND` | `#f4f2ec` | fond de page |
| `CARTE` | `#ffffff` | fond des cartes, blocs et graphiques |
| `BLEU_FONCE` | `#0b263d` | marque : barre latérale, titres, chiffres clés, onglet actif |
| `BLEU_ACTIF` | `#1769aa` | navigation active, sélection des filtres, liseré des notes en carte |
| or | `#ffce00` | bordure de la carte du logo Togo AI Lab |

**Accents nationaux (drapeau)** — `VERT_DRAPEAU #006b3f`, `JAUNE_DRAPEAU #fcd116`, `ROUGE_DRAPEAU #ce1126`. Convention : vert = favorable, jaune = mise en évidence / avertissement, rouge = risque élevé. Le filet du bas du constat et le petit filet tricolore de la barre du haut les utilisent.

**Bandeaux**

| Bandeau | Fond | Bordure | Accent | Titre |
| --- | --- | --- | --- | --- |
| Constat (`.constat`) | `#ffffff` | `#e2e8f0` | liseré gauche jaune drapeau `#fcd116` (4 px) | `#0b263d` |
| Synthèse chiffrée (`.synthese`) | `#ffffff` | `#e2e8f0` | — | chiffre `#0b263d` |
| Limite (`.limite`) | `#fdf3d7` | `#ecd28f` | — | `#6b4700`, texte `#3a2a00` |
| Note en carte (`.note-carte`) | `#eef4fd` ou `#ffffff` | liseré gauche 4 px : bleu `#1769aa`, vert `#16834a`, rouge `#ce1126`, jaune `#e6b422` | pastille « i » de la couleur du liseré | — |

**Palettes de données** (validées pour les daltonismes ; ne pas les changer)

| Nom (code) | Valeurs | Usage |
| --- | --- | --- |
| `BLEUS` (rampe séquentielle) | `#cde2fb #86b6ef #3987e5 #1c5cab #0d366b` | choroplèthes en 5 classes, valeurs croissantes |
| `CATEGORIELLE` | `#2a78d6 #eb6834 #1baf7a #eda100 #e87ba4 #008300` | séries d'un graphique |
| `PRIORITE` | Haute `#0d366b`, Moyenne `#3987e5`, Faible `#cde2fb`, Non classée `#b9b6ad` | cartes et légendes de priorité |
| `HORS_SELECTION` | `#ebe8e0` | territoires exclus par un filtre, sur une carte |
| `THEME` (4 objectifs) | Mobilité `#2474c6`, Sécurité routière `#e87518`, Réseau `#e6b422`, Couverture `#16834a` | couleur de thème : pastille d'icône, liseré, titres de carte de thème |
| `ETAT` (routes) | Bon `#16834a`, Moyen `#e6b422`, Mauvais `#ce1126`, Travaux `#8293a7`, Non évalué `#b9b6ad` | tronçons et barres d'état du réseau |
| `SERIE` (une couleur par donnée) | Moto `#16834a`, Voiture `#2474c6`, Poids lourd `#e6b422`, Bus `#8293a7`, Autres `#b6c0cc`, Accidents `#ce1126`, Blessés `#e87518`, Décès `#8e1b2b`, Auto-écoles `#2474c6` | un indicateur garde **sa** couleur sur toutes les pages |
| `COULEUR_ZONE` (6 zones) | Grand Lomé `#256abf`, Maritime hors GL `#008300`, Plateaux `#ab6300`, Centrale `#4a3aa7`, Kara `#cb4b0c`, Savanes `#bb537d` | nom de zone écrit en couleur, fond de zone — la couleur suit la zone, jamais son rang |
| `COULEUR_REGION` (5 régions) | Maritime `#256abf`, Plateaux `#ab6300`, Centrale `#4a3aa7`, Kara `#cb4b0c`, Savanes `#bb537d` | limites régionales colorées, tableaux par région |

**Règle daltonisme :** vert et rouge côte à côte sont confondus par une partie des daltoniens — toujours écrire le libellé ou la valeur à côté de la couleur ; aucune information portée par la couleur seule.

### 2.3 Typographie

Identique au gabarit (§2.3 de [MAQUETTE_dashboard.md](./MAQUETTE_dashboard.md)), aux couleurs près (encre `#172b3a`, bleu nuit `#0b263d`). Import en tête du CSS :

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, label { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
h1, h2, h3 { font-family: 'Fraunces', Georgia, serif !important; font-weight: 600 !important; letter-spacing: 0 !important; }
```

| Élément | Police | Taille | Graisse | Couleur |
| --- | --- | --- | --- | --- |
| Question de page (`.question`) | Fraunces | 2.6rem | 600 | `#172b3a` |
| Surtitre (`.surtitre`) | IBM Plex Sans | 0.78rem MAJ | 600 | `#0b263d` *(présent mais non rendu, voir §8.2)* |
| Réponse (`.reponse`) | IBM Plex Sans | 1.05rem | 400 | `#334155`, `max-width 880px` |
| Titre de bloc (`.bloc-titre`) | Fraunces | 1.3rem | 600 | `#172b3a` |
| Valeur de chiffre clé (`.kpi-valeur`) | Fraunces | 2.2rem (1.75rem en `une-ligne`) | 600 | `#0b263d` |
| Chiffre de synthèse (`.synthese-chiffre`) | Fraunces | 2.6rem | 600 | `#0b263d` |

### 2.4 Rayons, ombres, espacements

| Rayon | Où |
| --- | --- |
| 8px | onglets (pastilles), liens du menu, bouton de repli de la barre, note en carte |
| 10px | graphiques, bandeau filtres actifs, table HTML |
| 12px | barre des onglets, pied de page, carte du logo, carte KPI, cartes de thème, cartes de zone, encarts |
| 14px | Constat, Synthèse, Limite, carte-chiffre, total-carte, retenir |
| 18px | barre du haut, carte de recommandation |
| 999px | étiquettes et badges, tendance, sélecteur de langue |

> **Note :** la carte KPI est à **12px** ici (le gabarit Défi 2 était à 14px) ; elle porte une ombre discrète permanente `0 1px 2px rgba(11,38,61,.04)`.

| Ombre | Où |
| --- | --- |
| `0 1px 8px rgba(13,54,107,.08)` | barre du haut |
| `0 1px 2px rgba(11,38,61,.04)` | carte KPI, cartes de thème au repos |
| `0 8px 20px rgba(11,38,61,.08)` | carte KPI / thème / zone au survol |
| `0 1px 6px rgba(13,54,107,.06)` → `0 12px 28px rgba(13,54,107,.14)` | carte de recommandation (repos → survol) |

Contenu principal : largeur fluide, espacement latéral fixe.

```css
[data-testid="stMainBlockContainer"] { padding-top: 0.6rem; padding-bottom: 2rem;
  padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }
```

---

## 3. Disposition générale de l'écran

```
┌────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│  BARRE LATÉRALE    │  ┌──────────────────── BARRE DU HAUT (carte blanche, rayon 18) ─────────────┐ │
│  fond #0b263d      │  │ [écu] Ministère…        🇹🇬 Mobilité et sécurité routière…   [carte LOGO]│ │
│  [logo Togo + nom] │  │                          Comprendre les risques…  (filet tricolore)      │ │
│  FR · EN · Eʋe · Kab│  └───────────────────────────────────────────────────────────────────────────┘ │
│  PRINCIPAL         │  Tableau de bord › Page                        ← fil d'Ariane                 │
│   ◦ Vue nationale  │  Question de la page ?                         ← Fraunces 2.6rem              │
│  ANALYSES          │  ┌ carte blanche, liseré bleu nuit : réponse, conclusion d'abord ┐           │
│   ◦ …3 pages       │  └────────────────────────────────────────────────────────────────┘           │
│  PILOTAGE          │  [ Filtres actifs : … ]                        ← si un filtre est posé        │
│   ◦ …3 pages       │  ┌──────────────── barre d'onglets (si la page en a) ─────────────────────┐   │
│  MÉTHODOLOGIE      │  │ [■ Synthèse ■] [ Onglet 2 ] [ Onglet 3 ] [ Onglet 4 ]                   │   │
│   ◦ Méthodologie   │  └──────────────────────────────────────────────────────────────────────────┘   │
│  ──────────        │  GROUPE DE RANGÉE                                                             │
│  Filtres           │  ┌ KPI ┐ ┌ KPI ┐ ┌ KPI ┐ … (grille auto-fit, ou 6 sur une ligne)            │
│  ZONE   (pastilles)│  … sections : titre de bloc → graphique/carte → note en carte → constat …    │
│  PRIORITÉ          │  ┌ SYNTHÈSE CHIFFRÉE ┐  ┌ LIMITE (jaune) ┐  ← souvent côte à côte, même haut.│
│  LEVIER            │  Données : …                                  ← mention des sources           │
│  [réglages page]   │  ┌──────────────────── PIED DE PAGE (carte centrée) ────────────────────────┐ │
│  [Réinitialiser]   │  │     Togo AI Lab — Data Challenge | Administration territoriale…           │ │
│  • 39 préfectures… │  └───────────────────────────────────────────────────────────────────────────┘ │
│  “slogan” + route  │                                                                               │
└────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

- La barre du haut et le pied **ne sont pas collants** : la barre du haut est rendue une fois dans `app.py` avant `navigation.run()` ; le pied (`pied()`) est le dernier appel de chaque page. Les deux sont identiques sur les 8 pages.
- L'en-tête de Streamlit (`stHeader`) est au-dessus de la barre du haut. Ici, il est **rendu transparent** et on laisse ses boutons (Share/GitHub de Streamlit Cloud) se poser dans le coin droit de la barre blanche — voir §4.

---

## 4. Barre du haut

### Structure (`composants.topbar`)

Un conteneur `st.container(key="topbar")` (classe `.st-key-topbar`), puis 3 colonnes `st.columns([1.1, 1.3, 1], vertical_alignment="center")` :

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ ┌──┐ Ministère de l'Efficacité du  │  🇹🇬 Mobilité et sécurité routière au Togo  │ ┌────────┐ │
│ │écu│ Service Public et de la       │  Comprendre les risques, identifier…       │ │ TOGO   │ │
│ └──┘ Transformation Numérique       │  ───── filet vert/jaune/rouge ─────        │ │ AI LAB │ │
│   colonne 1 (1.1)                   │     colonne 2 (1.3), centrée               │ col 3  └────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

| Zone | Contenu | Détail |
| --- | --- | --- |
| Gauche | armoiries (écu seul, SVG 38 px) + nom du ministère | `MINISTERE` ; repli `🛡️` si le SVG manque |
| Centre | « 🇹🇬 Mobilité et sécurité routière au Togo » + sous-titre italique + **filet tricolore** | `MARQUE` + `SOUS_TITRE` ; le filet est un `::after` dégradé vert 0-34 % / jaune 34-67 % / rouge 67-100 % |
| Droite | carte du logo Togo AI Lab (conteneur `topbar_droite`) | repli texte « TOGO / AI LAB » rouge tant que `static/logo_togo_ai_lab.png` manque |

> **Différence avec le gabarit :** pas de boutons FR/EN dans la barre du haut (le sélecteur de langue est passé dans la barre latérale, §5) ; ajout du filet tricolore sous le titre central.

### CSS principal

```css
div.st-key-topbar { background:#fff; min-height:92px; padding:16px 22px; box-shadow:0 1px 8px rgba(13,54,107,.08);
  border:1px solid #e2e8f0; border-radius:18px; box-sizing:border-box; }
.topbar-titre { font-family:'Fraunces',Georgia,serif; font-size:1.2rem; font-weight:600; color:#0b263d; }
.topbar-centre::after { content:""; display:block; width:56px; height:3px; margin:7px auto 0; border-radius:2px;
  background:linear-gradient(90deg,#006b3f 0 34%,#fcd116 34% 67%,#ce1126 67% 100%); }
.ai-lab-logo-carte { background:#fff; border:2px solid #ffce00; border-radius:12px; padding:7px 12px; height:56px;
  box-shadow:0 2px 6px rgba(0,0,0,.08); display:inline-flex; align-items:center; justify-content:center; }
```

### Contrainte : en-tête de Streamlit selon l'hébergement (option A retenue)

Streamlit place son `stHeader` au-dessus du contenu ; sur Streamlit Cloud il devient opaque et porte les boutons Share/GitHub, qui masqueraient le haut de notre barre. Choix fait ici (**option A**) : rendre l'en-tête **transparent** et **réserver 230 px à droite** de la barre du haut pour que les boutons de la plateforme s'y logent, au lieu de réserver de la hauteur.

```css
[data-testid="stHeader"] { background:transparent !important; pointer-events:none; }
[data-testid="stHeader"] * { pointer-events:auto; }
body:has([data-testid="stHeader"] [data-testid="stToolbar"]) div.st-key-topbar_droite { padding-right:230px; }
```

> À vérifier sur l'application déployée (le comportement exact de Streamlit Cloud n'est pas documenté). L'option B (masquer les boutons) a été écartée.

---

## 5. Barre latérale

De haut en bas (rendue dans `app.py`, styles dans `theme.py`) :

1. **Logo** (`st.logo`) : `static/logo_barre_laterale_<langue>.svg` barre ouverte, `static/logo_togo_icone.svg` (silhouette du Togo) barre repliée. Le logo = Togo en miniature aux couleurs du drapeau traversé par une route + « TOGO / MOBILITÉ & SÉCURITÉ ROUTIÈRE / Tableau de bord territorial d'aide à la décision ». Produit par `scripts/logo_barre_laterale.py`. Contour tiré des 39 préfectures (`prefectures.geojson`).
2. **Sélecteur de langue** (`i18n.selecteur`), juste sous le logo : groupe de boutons `FR · EN · Eʋegbe · Kabɩyɛ`. Rendu dans le contenu de la barre puis **remonté par CSS** en position absolue (`div.st-key-selecteur_langue { position:absolute; top:7.9rem; … }`) ; le menu reçoit `margin-top:4.4rem` pour lui laisser la place. La langue suit l'adresse (`?lang=…`) et persiste d'une page à l'autre.
3. **Menu** en 4 groupes (`st.navigation`, §9.1) : titres de groupe en MAJ `#cbd5e1` ; liens `#f8fafc` 0.93rem avec icône Material ; **lien actif en bleu plein** `#1769aa` (texte blanc), survol bleu translucide.
4. **Séparateur** (`st.divider()`), titre **« Filtres »** en gras.
5. **Trois filtres** (`st.pills`, choix multiple ; fond blanc, sélection bleue `#1769aa`), titres en MAJ `#cbd5e1` :

| Libellé | Valeurs | Défaut | Clé d'état |
| --- | --- | --- | --- |
| Zone | Grand Lomé, Maritime hors Grand Lomé, Plateaux, Centrale, Kara, Savanes | aucune | `f_zones` |
| Priorité | Haute, Moyenne, Aucune action | aucune | `f_priorites` |
| Levier | Réseau, Formation | aucun | `f_leviers` |

6. **Conteneur de réglages propres à la page** : `st.session_state["sidebar_reglages"] = st.container()`, placé **au-dessus** du bouton Réinitialiser. La page Carte y dépose ses sélecteurs (Couche, Tracé, Équipements, États du réseau) ; ils n'apparaissent donc que sur cette page.
7. **Bouton « Réinitialiser les filtres »** (pleine largeur, `:material/restart_alt:`) : `reinitialiser()` remet les 3 clés à vide.
8. **Repères chiffrés** (`ul.sidebar-stats`, liste à puces discrète) : 39 préfectures · 6 zones ; population 2022 (INSEED) 8,095 M ; 272 auto-écoles dont 132 agréées ; 23 préfectures sans auto-école agréée ; 13 préfectures au réseau dégradé ; 16 797 équipements.
9. **Slogan + illustration** (`composants.pied_barre_laterale`), poussés en **bas** de la barre par un `flex` : « Des routes plus sûres pour une mobilité durable au Togo », filet turquoise `#2ec4b6`, puis `static/routes_slogan.svg` (montagnes et route sinueuse).

> **Différences avec le gabarit :** 3 filtres au lieu de 4, tous en `st.pills` (pas de `segmented_control` de maille — la maille est choisie dans le contenu des pages) ; ajout du sélecteur de langue, du conteneur de réglages de page, et du bloc slogan+illustration en pied de barre.

---

## 6. Pied de page (`composants.pied`)

Deux éléments, à la fin de chaque page :

1. **Mention des sources** (`.pied`, 0.8rem `#64748b`) : « Données : portail national de données ouvertes du Togo et sources institutionnelles complémentaires. » Aucun nom de fichier : le détail est sur la page Méthodologie.
2. **Carte d'identité** (`.pied-identite`, centrée, blanc, rayon 12) :
   - Titre `.pied-identite-titre` (0.92rem, 800, `#0b263d`) : « Togo AI Lab — Data Challenge | Administration territoriale et mobilité — Défi 1 ».
   - Sous-titre `.pied-identite-sous-titre` (0.78rem `#64748b`) : « Diagnostic territorial et aide à la décision pour la mobilité, la sécurité routière et l'entretien du réseau au Togo ».

---

## 7. Gabarit d'une page

Chaque page suit le même ordre, de haut en bas. Le lecteur sait où regarder d'une page à l'autre.

| # | Zone | Composant | Règle de contenu |
| --- | --- | --- | --- |
| 1 | Fil d'Ariane | *(rendu par `st.navigation`/`entete`)* | « Tableau de bord › **Nom de la page** » |
| 2 | En-tête | `entete(surtitre, question, reponse_html, carte=True)` | titre = **une question** ; réponse = **la conclusion d'abord**, chiffres en `<strong>`, présentée dans une carte blanche à liseré bleu nuit |
| 3 | Filtres actifs | `filtres_actifs(html)` | seulement si un filtre est posé, ou pour prévenir que les chiffres nationaux ne bougent pas |
| 4 | Onglets | `onglets(cle, libelles)` | 3 à 4 vues ; la 1ʳᵉ est une vue synthèse (pages Évolutions et Recommandations) |
| 5 | Chiffres clés | `rangee_kpi(groupe, [carte_kpi(...)…], une_ligne=…, centre=…)` | 3 à 6 cartes ; règle des dix secondes |
| 6 | Visuel + lecture | `titre_bloc` → graphique/carte → `note_carte(...)` → `constat(...)` | **le constat passe sous ou avant la section**, en pleine largeur (choix de ce projet) ; jamais un graphique sans phrase de lecture |
| 7 | Visuels secondaires | blocs en 1 ou 2 colonnes (`st.columns`) | un `export_csv(...)` par bloc exportable |
| 8 | Synthèse + Limite | `synthese(...)` et `limite(...)`, souvent **côte à côte, même hauteur** (`egale=True`) | un seul chiffre-titre ; la limite voyage avec l'analyse |
| 9 | Pied | `pied()` | identique partout |

### Règles de contenu transverses

- **Quatre questions**, dans l'ordre du projet : où en est-on ? quels territoires ? qu'est-ce qui change / pourquoi ? quelle action, et à quel horizon ?
- **Langage de décideur.** Hors page Méthodologie, jamais de nom de fichier, de code interne (`O3-02`, `H8`…), de numéro de document ni de nom de source. Le helper `evolutions.nettoyer()` **remplace chaque code par son intitulé** lu dans `catalogue_07.csv`.
- **Le constat est en pleine largeur**, placé sous ou en tête de sa section (sur ce projet), et non dans une colonne de droite comme sur le gabarit.
- **Couleur :** phrases de lecture en bleu nuit ; nom de zone/région dans sa couleur ; nom de lieu dans un constat en violet `.lieu #4a3aa7` ; effectifs d'habitants en rouge `.habitants #ce1126` ; jamais d'information portée par la seule couleur.

---

## 8. Composants (`composants.py`)

### 8.1 Fil d'Ariane — `ariane(page)`
`<div class="ariane">Tableau de bord › <b>Page</b></div>`, 0.85rem `#64748b`, nom de page `#172b3a`.

### 8.2 En-tête — `entete(surtitre, question, reponse_html, carte=False)`
Rend `.question` (Fraunces 2.6rem) puis `.reponse`. Avec `carte=True` (utilisé partout), la réponse est une **carte blanche à liseré gauche bleu nuit** (`.reponse.en-carte` : `border-left:4px solid #0b263d`, rayon 14, ombre discrète). **Le surtitre n'est plus rendu** (il doublait le fil d'Ariane) ; le paramètre subsiste pour ne pas changer les appels.

### 8.3 Bandeau « filtres actifs » — `filtres_actifs(html)`
`.filtres-actifs` : 0.85rem, blanc, bordure `#e2e8f0`, rayon 10. Rappelle les filtres posés, ou prévient que des chiffres nationaux ne changent pas avec les filtres.

### 8.4 Carte de chiffre clé (KPI) — le composant central

`carte_kpi(libelle, valeur, phrase, contexte="", reserve="", etiquette=None, ton="neutre", unite="", icone=None, periode="", tendance=None, pastille=None, bordure=None) -> str` **renvoie une chaîne HTML** (elle n'écrit rien). Une rangée = **une seule** `st.markdown` qui concatène les cartes (sinon la grille CSS casse — §13).

**Anatomie** (ordre fixe) :

```
┌───────────────────────────────────────────────┐ ← .kpi : blanc, bordure #e2e8f0, rayon 12, liseré bas 3px coloré
│ [icône]  IMMATRICULATIONS            (étiquette)│ ← .kpi-tete : pastille d'icône + libellé + étiquette A/B/C
│          (2024)                                 │ ← .kpi-periode : l'année entre parenthèses, sous le libellé
│              751 398          [↘ −32,6 % vs 23] │ ← .kpi-centre : valeur (Fraunces 2.2rem) + badge de tendance
│          dont 32 % de motos                     │ ← .kpi-phrase : se lit avec la valeur
│   Immatriculations de l'année, pas le parc…     │ ← .kpi-contexte : seuil / comparaison
│   ─────────────────────────────────────────    │
│   Réserve : ce que le chiffre ne mesure pas     │ ← .kpi-reserve : filet en haut, collée en bas (margin-top:auto)
└───────────────────────────────────────────────┘
```

| Paramètre | Rôle |
| --- | --- |
| `libelle` / `periode` | ce qui est mesuré ; l'année/période s'écrit `(2024)` sous le libellé |
| `valeur` / `unite` | le chiffre seul (formaté FR par `_insecable`) + unité accolée en 1.05rem |
| `phrase` | la suite de la valeur : chiffre + phrase forment une phrase |
| `contexte` / `reserve` | seuil/comparaison ; puis ce que le chiffre ne mesure pas (vide = pas de pied) |
| `etiquette` + `ton` | verdict court coloré : `ton ∈ {alerte, ok, critique, neutre, national}` |
| `icone` | clé de `ICONES` → pastille d'icône au trait, teinte = couleur du thème ; **fixe aussi la couleur du liseré bas** |
| `pastille` | `(emoji, fond)` : remplace l'icône au trait par un émoji sur fond coloré |
| `tendance` | `(variation, référence, sens)` : badge arrondi sous la valeur, `sens ∈ {pire(rouge), mieux(vert), neutre(gris)}`, flèche ↗/↘/→ déduite du signe |
| `bordure` | force la couleur du liseré bas (sinon = couleur de l'icône) |

**Grille** `rangee_kpi(groupe, cartes, une_ligne=False, centre=False)` :
- défaut : `.kpi-grille` = `repeat(auto-fit, minmax(230px,1fr))`, gap 12 — 3 à 4 cartes, passe à la ligne sur écran étroit ;
- `une_ligne=True` : `.kpi-grille.une-ligne` = `repeat(6, 1fr)` (→ 3 colonnes sous 1350px, 2 sous 760px) ; valeur réduite à 1.75rem, bloc central centré. **Utilisé pour les 6 chiffres de la Vue nationale.**
- `centre=True` : `.kpi-grille.centre` centre chiffre, phrase et réserve.
- Toutes les cartes d'une rangée ont **la même hauteur** (la grille étire ; `min-height:2.5rem` sur l'en-tête aligne les valeurs ; `margin-top:auto` colle la réserve).

**Icônes** (`ICONES`, dict `nom → (tracé SVG 24×24, couleur de thème)`), rendues par `icone_kpi(nom)` dans une pastille 34×34 rayon 10, fond = couleur à 12 % d'opacité (`{couleur}1f`) : `population` (bleu), `vehicule` (vert), `permis` (bleu), `moto` (orange), `tues` (triangle rouge), `blesses` (cœur jaune-or), `route`/`route_vert`/`route_rouge` (gris/vert/rouge), `ecole`/`ecole_jaune` (toque), `troncons` (triangle jaune-or), `alerte` (cercle « ! » rouge), `etablissement` (bâtiment vert), `signalisation` (feu bleu).

**Survol** : `translateY(-2px)`, bordure bleue `#1769aa`, ombre, et un reflet jaune clair traverse la carte (`::after`). Désactivé sous `prefers-reduced-motion`.

### 8.5 Étiquettes et badges

`.etiquette` (pilule 0.74rem) : `alerte` (jaune), `ok` (bleu clair), `critique` (rouge), `neutre` (gris), `national` (gris, graisse 500). Variantes reco : `reco-priorite` (jaune), `reco-nature` (indigo), `reco-horizon` (vert).
`badge(texte, couleur)` : pilule inline dont le texte passe blanc sur fond sombre, encre sur fond clair (liste de clairs codée en dur). `table_html(lignes)` : petit `<table>` HTML quand les cellules portent déjà leurs badges/couleurs (Streamlit n'affiche pas de HTML dans `st.dataframe`).

### 8.6 Bloc à bordure et titre de bloc
`titre_bloc(titre, sous_titre=None, marge=False)` : `.bloc-titre` (Fraunces 1.3rem) + `.bloc-sous-titre` (0.86rem `#64748b`). Les tableaux statiques sont souvent enveloppés d'un `st.container(border=True)`.

### 8.7 Constat — `constat(texte_html, egale=False)`
Carte **blanche à liseré gauche jaune drapeau** (`.constat` : `border-left:4px solid #fcd116`, rayon 14). Titre « Constat », une à deux phrases de décision, chiffres en `<strong>`/couleur. `egale=True` ajoute `.carte-egale` pour égaliser la hauteur avec la carte voisine.

### 8.8 Note en carte — `note_carte(texte_html, couleur="vert", titre="")`
**Composant propre à ce projet** (remplace les légendes grises sous les graphiques). Carte blanche, pictogramme « i » cerclé, **liseré gauche 4 px** coloré : `vert #16834a`, `bleu #1769aa`, `rouge #ce1126`, `jaune #e6b422`. Variantes CSS `.note-carte.a-savoir` (pictogramme), `.lisere-*`, `.blanche`, `.risque`.

### 8.9 Synthèse chiffrée — `synthese(chiffre, legende, puces_html, egale=False)`
`.synthese` : grille `280px 1fr`. Colonne gauche : titre + **un seul** chiffre-titre (Fraunces 2.6rem) + légende. Colonne droite : 3-4 puces en gras. Variante **Vue nationale** : carte **vert clair** (`div.st-key-vn_synthese`, fond `#e6f4ec`) avec un bouton « Voir les recommandations » en bas à droite, même hauteur que la carte « À retenir ».

### 8.10 Limite — `limite(texte="", titre="Limite de cette page", discret=False, puces=None, egale=False, texte_html=None)`
`.limite` : fond jaune `#fdf3d7`, bordure `#ecd28f`. Trois formes du corps : texte simple, **liste à puces** (`puces=`), ou **HTML libre** (`texte_html=`, pour gras et chiffres colorés). `discret=True` → variante sans fond, filet en haut (page de synthèse).

### 8.11 Carte de recommandation (page Recommandations)
Grille `st.columns(3)` ; chaque carte dans `st.container(border=True, key=f"carte_reco_{id}")` → classe `.st-key-carte_reco_*` (rayon 18, ombre, survol `translateY(-4px)`). Contenu : pastille d'émoji du thème + libellé, titre (`.reco-titre` Fraunces 1.12rem), cible, contexte, **ligne d'horizon** (`.reco-horizon2031`, bandeau bleu clair), étiquettes priorité/nature/horizon.

Thèmes (`THEME_EMOJI`, `THEME_PASTILLE`) : Réseau 🛣️ `#eb6834`, Formation 🏫 `#1baf7a`, Sécurité routière 🚦 `#eda100`, Zones les moins desservies 📍 `#0d366b`, Données 📊 `#55534e`. **Règle : on n'additionne jamais les habitants d'une recommandation à l'autre** (les territoires se recoupent) — une note le dit.

### 8.12 Cartes de thème (Vue nationale)
Quatre `st.columns(4)` ; chaque colonne qui contient un `.reco-theme` devient une **carte blanche arrondie** (sélecteur CSS `[data-testid="stColumn"]:has(.reco-theme)`), **liseré bas 3 px** de la couleur du thème (`.mob` bleu, `.sec` ambre, `.res` brique, `.couv` vert), survol sans balayage. Le bouton « Voir le détail → » est **poussé en bas** (`margin-top:auto`) pour que les 4 cartes aient la même hauteur ; survol bleu clair `#e8f0fb`.

### 8.13 Autres cartes de mise en page
- **`.zone-grille` / `.zone-carte`** (Priorités, « Diagnostic par zone ») : grille 3×2 de cartes blanches, nom de zone en couleur, liseré bas de la couleur de la zone, survol.
- **`.carte-chiffre`** : carte horizontale à liseré bleu, grand chiffre à gauche + texte à droite.
- **`.total-carte`** : carte bleu clair centrée pour un grand total (permis).
- **`.retenir`** : carte blanche, messages numérotés en pastilles rondes.
- **`.encart` / `.st-key-enc_*`** (Évolutions) : carte blanche à liseré gauche coloré **par le verdict**.
- **`.tbl-verdict` / `.verdict-badge`** : tableau HTML avec en-tête collant et colonne « Verdict » en **pilule colorée**.
- **`.etapes` / `.etape`** (Méthodologie) : liste des 9 étapes, numéro en pastille 54×54 (rampe `BLEUS`).
- **`.carte-egale`** : mécanisme réutilisable qui égalise les hauteurs des cartes d'une même rangée `st.columns` (options `egale=True`).

### 8.14 Onglets — `onglets(cle, libelles) -> list`
Barre blanche de pastilles (`.stTabs [role="tablist"]`), onglet actif **bleu nuit plein** `#0b263d`, texte blanc. L'onglet actif est retenu **par son rang** dans `st.session_state[f"{cle}_rang"]` : il survit au changement de langue (le libellé change, le rang non) et au passage par une autre page. En tête de l'onglet ouvert : repère « vue 2 sur 4 ». Les pastilles passent à la ligne (`flex-wrap`) sur écran étroit.

### 8.15 Export, habillage Plotly, choroplèthe générique
- `export_csv(df, nom, cle)` : `st.download_button` « Exporter (CSV) », icône `:material/download:`, sous chaque bloc exportable.
- `habiller(fig, hauteur, suffixe_y, legende_y=1.12, **kw)` + `tracer(fig, cle)` : fond blanc, grille `#efece4`, légende horizontale au-dessus, séparateurs FR (`", "`), **pas de barre d'outils Plotly**.
- `fenetre_geo(fig, geo)` : fenêtre lon/lat **explicite** (bbox ± 0,05°) — ne jamais utiliser `fitbounds` (le Togo apparaît minuscule).
- `choroplethe(geo, df, cle, colonne, …, categorique=…, couleurs=…, palette="Blues", …)` : choroplèthe continue ou catégorielle, contours blancs 0.8 px, légende à droite, zoom désactivé.

---

## 9. Les 8 pages

### 9.1 Menu (`app.py`)

| Groupe | Page | Icône Material | url_path | Question (titre) | Onglets |
| --- | --- | --- | --- | --- | --- |
| Principal | Vue nationale | `home` | `/` (défaut) | La mobilité et la sécurité routière au Togo : où en est-on ? | — |
| Analyses | Comparaison territoriale | `bar_chart` | `comparaison` | Quels territoires sont les moins bien équipés ? | — |
|  | Évolutions et constats | `timeline` | `evolutions` | Qu'est-ce qui change, et que confirment les données ? | 4 |
|  | Carte du réseau et des auto-écoles | `map` | `carte` | Que voit-on, préfecture par préfecture ? | — |
| Pilotage | Priorités | `flag` | `priorites` | Par où commencer ? | — |
|  | Recommandations | `task_alt` | `recommandations` | Quelle action engager ? | ≥2 (Toutes + thèmes + Actions par zone) |
|  | Horizon 2031 | `trending_up` | `horizon` | Combien en faudra-t-il d'ici 2031 ? | — |
| Méthodologie | Méthodologie | `menu_book` | `methodologie` | Sources, méthode et limites | — |

`st.session_state["pages"]` garde les références `st.Page` des pages Recommandations et Horizon, pour les liens internes (`st.switch_page`).

### 9.2 Disposition page par page

Notation : `[a, b]` = ratio de `st.columns([a, b])` ; px = hauteur de graphique/carte.

**Vue nationale** (`vue_nationale.py`) — sans onglets
- En-tête en carte, puis **6 chiffres clés sur une ligne** (`une_ligne=True`) : Population (2022, icône `population`) · Immatriculations (2024, `vehicule`, tendance neutre) · Morts sur la route (2022, `tues`, tendance « pire ») · Blessés (2022, `blesses`, tendance « pire ») · Réseau évalué (2020, `route`) · Préfectures sans auto-école agréée (`ecole`).
- Section 2 « Le Togo, préfecture par préfecture » : Constat sous le titre (pleine largeur), puis `[1.25, 1]` carte double (principale + inset Maritime/Grand Lomé, panneaux `geo`/`geo2`) à gauche, légendes/notes à droite. Fond par région, auto-écoles vert/jaune-or.
- Section 3 « Les quatre thèmes confirmés » : `st.columns(4)` de **cartes de thème** (§8.12) avec mini-visualisations et « Voir le détail → ».
- Section 4 « Permis de conduire délivrés » : `[1, 3.2]` grand total (`.total-carte`) + barres horizontales par catégorie.
- Section 5 « Immatriculations et permis, 1990–2024 » : figure à deux étages (`make_subplots`, deux légendes), repères ① ② ③, trou de 2013 ; puis `[1, 1.6]` deux notes en carte.
- Section 6 : `[1.3, 1]` carte « À retenir » (`.retenir`) + **Synthèse chiffrée verte** (`vn_synthese`) ; Limite ; pied.

**Comparaison territoriale** (`comparaison.py`) — sans onglets
- En-tête en carte ; **3 chiffres clés** nationaux (`centre=True`, pastilles d'émoji) ; « Choisir la maille » (segments zones/régions/préfectures).
- « Réseau et formation » : Constat sous le titre, nuage pleine largeur, **curseur de seuil** en maille préfectures (`st.slider`, note en carte « À savoir »).
- « Les territoires » : tableau HTML à badges (seuils franchis, leviers, part en mauvais état en rouge).
- « État du réseau par zone » : barres empilées, km inscrits dans les segments, part au bout de la barre.
- « Où sont les auto-écoles » + « Distance à l'auto-école la plus proche » : barres pleine largeur, chiffre coloré par palier de 10 km (légende des paliers).
- « Les 39 préfectures » : `st.dataframe` triable mis en forme par `Styler` (zone/région en couleur, badges de priorité). Points d'attention (`st.columns`, 5 cartes `carte-egale`). Synthèse + Limite côte à côte (`egale=True`).

**Évolutions et constats** (`evolutions.py`) — 4 onglets : Synthèse · Mobilité · Sécurité routière · État du réseau routier
- **Synthèse** : 3 KPI (icônes ✅/⚠️/❓, `centre=True`) ; Constat ; `[1.5, 1]` **carte des constats** (fond = part de mauvais état de la zone en 5 classes ; 49 tronçons rouges ; 132 auto-écoles agréées) à gauche, **encarts nationaux** (`.st-key-enc_*`, liseré par verdict) + notes en carte à droite ; multiselect de verdict ; tableaux **à badges de verdict** (`_table_verdict`, HTML) ; Limite.
- **Mobilité** : 3 KPI (icônes `permis`/`vehicule`/`moto`, liserés propres) ; graphe pleine largeur ; constats en notes en carte (« i » vert) ; parc estimé.
- **Sécurité routière** : 3 KPI (`tues`/`vehicule`/`alerte`) ; « Les 6 taux » pleine largeur ; 3 panneaux année par année (`st.columns(3)`) ; tués par usager + estimation OMS ; Limite « Limites analytiques ».
- **État du réseau routier** : 3 KPI (`route_vert`/`route_rouge`/`troncons`) ; **tableau des 84 tronçons** pleine largeur (HTML `_table_troncons` : type en badge, zones traversées chacune dans sa couleur) ; toggle « Afficher les 84 tronçons ».

**Carte du réseau et des auto-écoles** (`carte.py`) — sans onglets
- En-tête en carte ; **4 chiffres clés** (`centre=True`, icônes `route_rouge`/`etablissement`/`ecole_jaune`/`signalisation`).
- **Réglages dans la barre latérale** (conteneur réservé, §5) : Couche (sélecteur de couches thématiques), Tracé (routes par type / état des tronçons / aucun), Équipements, États du réseau (multiselect).
- **Trois cartes réunies dans une seule figure** côte à côte, pleine largeur : carte 1 (Togo, couche thématique en 5 classes fixes — voir listes `CL_*`), carte 2 (zoom Maritime/Grand Lomé), carte 3 (état du réseau : zones en fond, tronçons par état dominant `ETAT_LIGNE`, régions colorées). `dessiner()` et `dessiner_etat()` ajoutent les traces. Fiche de préfecture au clic (préfecture cerclée de noir).
- Légende complète sous la figure ; « Les couches, préfecture par préfecture » (tableau triable à badges) ; « Les 272 auto-écoles » (recherche + filtre + badges de statut) ; « Ce que la carte ne montre pas » (note en carte jaune) ; Synthèse + Limite.

**Priorités** (`priorites.py`) — sans onglets
- En-tête en carte ; **5 chiffres clés** (`centre=True`, icônes `troncons`/`alerte`/`population`/`route_rouge`/`etablissement`).
- « Les zones en difficulté » : Constat avant la section ; tableau pleine largeur ; note en carte verte + carte warning ; **« Diagnostic par zone »** = grille 3×2 `.zone-carte`.
- « Les 5 préfectures qui cumulent » ; « Les 10 premières en priorité » (barres empilées réseau/formation portant le score, robustesse n/6) ; « Les deux leviers » (`st.columns(2)`).
- « Le classement tient-il ? » : Constat ; `[1, 1.2]` **curseur de poids du réseau** (`st.slider`, recalcul autorisé) + carte recalculée ; notes en carte (formule du score, règle de stabilité) ; tests de robustesse.
- « Classement complet des 38 préfectures » ; boutons « Exporter » / « Voir le classement sur la carte → » côte à côte ; Synthèse + Limite (`egale=True`, limite en puces).

**Recommandations** (`recommandations.py`) — onglets Toutes · Réseau · Formation · Sécurité routière · … + Actions par zone
- En-tête en carte ; barre de recherche `[3, 1]`.
- Onglet « Toutes » et par thème : **grille 3 colonnes de cartes de recommandation** (§8.11), `grille()` préfixe les clés par onglet (sinon `StreamlitDuplicateElementKey`). Note bleue « Pour aller plus loin ».
- Onglet « Actions par zone » : 39 fiches préfectures, sélecteur de tri. Constat + Limite côte à côte, puis séparation, puis Synthèse pleine largeur.

**Horizon 2031** (`horizon.py`) — sans onglets
- En-tête en carte ; curseur d'horizon (Passé/Actuel/+1/+3/+5, défaut 2029) ; **4 chiffres clés** (`centre=True`, icônes `population`/`ecole_jaune`/`route_rouge`/`route`), étiquette niveau C.
- « Ce qu'il faut ajouter » : carte des préfectures (5 classes fixes, inset Maritime) + tableau par zone/région, pleine largeur ; note en carte verte ; tableau par recommandation (expander).
- « Sans action, le taux baisse » : `st.columns(2)` auto-écoles pour 100 000 hab. sans action / population par zone (bande de fourchette).
- « Sécurité routière » : `[1.35, 1]` trois panneaux (accidents/blessés/tués) avec **période projetée grisée** + graphique des écarts/plafonds ; Constat.
- « Où ouvrir les auto-écoles » : carte pleine largeur (48 sites en losanges roses, auto-écoles agréées en vert) ; Synthèse + Limite (`egale=True`).

**Méthodologie** (`methodologie.py`) — sans onglets, **seule page où codes et sources apparaissent**
- En-tête en carte ; « Comment nous avons travaillé » (9 étapes en cards bordés) ; « Sources » (tableau dans `st.container(border=True)` + note en carte) ; « Limites majeures » (8 cards à badge numéroté rouge) ; `[1, 1.4]` Niveaux de preuve / Questions ouvertes ; « Les zones les moins desservies » ; « Les formules » ; « Corrections et contrôles » ; « Licences » (dont armoiries CC BY-SA 4.0) ; `st.columns(2)` Constat + Synthèse ; Limite ; pied.

---

## 10. État, filtres et interactions

| Clé de `st.session_state` | Rôle |
| --- | --- |
| `langue` | `"fr"` (défaut), `"en"`, `"ee"`, `"kbp"` ; suit `?lang=` |
| `f_zones`, `f_priorites`, `f_leviers` | filtres globaux, `setdefault([])`, **conservés d'une page à l'autre** |
| `<page>_rang` | rang de l'onglet ouvert, par page (voir `onglets`) |
| `sidebar_reglages` | conteneur réservé dans la barre latérale pour les réglages de la page Carte |
| `pages` | références `st.Page` pour les liens internes (`st.switch_page`) |
| `pr_poids`, `cmp_seuil`, `ca_couche`/`ca_trace`/`ca_etats`, `ca_prefecture`, `ev_verdict`, `r_tri`, … | contrôles propres à une page |

**Portée des filtres :** les chiffres nationaux (population, immatriculations, accidents, parc) **ne bougent pas** avec les filtres — un bandeau le dit ; les cartes, tableaux et chiffres territoriaux suivent `f_zones` (helper `donnees.filtrer_zone`) ; sur une carte, les territoires hors sélection passent en gris clair sans disparaître. La section 1 de certaines pages (ex. zones en difficulté) montre toujours toutes les zones.

**Parcours inter-pages :** la carte → fiche de préfecture, les cartes de thème / leviers → page de détail, « Voir le classement sur la carte » → page Carte sur la couche Priorité. La sélection Plotly étant effacée à chaque rerun, la préfecture choisie est gardée en session (`ca_prefecture`).

---

## 11. Quatre langues et format des nombres

- **Méthode « traduire avant le déploiement »** : les pages restent écrites en **français** ; `scripts/traduire_dashboard.py` recense les segments affichés, les traduit **une fois hors ligne** avec **NLLB-200** et écrit `dashboard/locales/{en,ee,kbp}.json` (commitées). À l'affichage, `i18n.installer()` fait passer par `bi()` tout ce que Streamlit rend (markdown, widgets, onglets, tableaux, Plotly) : aucun modèle, aucun appel réseau (compatible Streamlit Cloud).
- **Découpage en segments** (`i18n._SEP`) : le HTML, les balises, les entités, les gabarits Plotly `%{…}`, le gras markdown `**`, les puces, flèches, pictogrammes et numéros cerclés sont **protégés** ; un bloc `<style>…</style>` est protégé en entier. Un segment absent du fichier reste en français.
- **Noms de lieux et sigles** (`i18n._VALEURS`) non traduits (Togo, zones, A–F, WorldPop, NLLB-200…).
- **Qualité :** anglais correct (termes d'interface relus à la main, `"relu": true`) ; éwé et kabiyè approximatifs. Les traductions jugées inventées restent en français (`"suspect": true`). **Relecture par des locuteurs nécessaire avant une présentation officielle.**
- **Nombres (FR, `donnees.fr`/`pct`)** : milliers par espace insécable (`8 095 498`), virgule décimale (`21,2 %`, espace insécable avant `%` via `_insecable`), années sans séparateur (`2024`), Plotly `separators=", "`. L'export CSV suit la langue.

Après un changement de texte : `python scripts/traduire_dashboard.py` (ne traduit que le nouveau), puis `python scripts/logo_barre_laterale.py`.

---

## 12. Cartes et graphiques (Plotly)

**Graphiques** : `habiller(fig, hauteur, suffixe_y)` + `tracer(fig, cle)`. Hauteurs : 240–300 px (appoint), 330–380 (demi-largeur), 400–440 (principal), deux étages pour les figures `make_subplots`.

**Choroplèthes** : projection `mercator`, fond `#ffffff`, `visible=False`, **cadrage lon/lat explicite** (`fenetre_geo`, jamais `fitbounds`), contours blancs 0.8 px, survol seulement (`displayModeBar: False`, `scrollZoom: False`). Contours lus par `donnees.contours*()` : préfectures (39), zones (6, par `dissolve("Zone")`), régions (5, par `dissolve("Région")`), simplifiés à 0,002° et **réorientés** (`shapely.orient(sign=-1)`) pour Plotly ; chaque feature porte `code` = nom du territoire pour la jointure.

**5 classes fixes :** les pages Carte et Horizon rangent chaque indicateur dans des bornes fixes (`CL_ETAT`, `CL_POP`, `CL_KM10`, `CL_DIST`…) pour que **les couleurs se comparent d'un horizon / d'une couche à l'autre**. Valeurs absentes en gris avec leur mention explicite (Mô « aucune route classée » ; Golfe et Agoè-Nyivé « sans population rurale »), jamais confondues avec un 0 mesuré.

**Figures multi-panneaux :** la carte principale + son zoom Maritime (`geo`/`geo2`), et les 3 cartes de la page Carte (`geo`/`geo2`/`geo3`), sont des **panneaux d'une même figure** (layout manuel `lonaxis`/`lataxis`), avec légende sur la seule carte principale.

---

## 13. Pièges connus de Streamlit (1.61)

| Piège | Conséquence | Parade |
| --- | --- | --- |
| Un dossier nommé `pages/` | Streamlit bascule sur son ancienne navigation et ignore `st.navigation` | nommer le dossier `views/` |
| Une carte KPI par `st.markdown` | chaque carte dans son propre bloc, la grille CSS casse | une rangée = **une seule** chaîne HTML concaténée |
| `st.container(key="x")` | rendu avec la classe `.st-key-x` | c'est ce qui permet de styler la barre du haut, les cartes de reco, les encarts |
| HTML dans `st.dataframe` | non rendu | `Styler` pour la couleur, sinon `<table>` HTML (`table_html`, `_table_verdict`, `_table_troncons`) |
| Plotly `fitbounds` | le Togo apparaît minuscule | cadrage lon/lat explicite (`fenetre_geo`) |
| Clé de widget en double (même carte dans deux onglets) | `StreamlitDuplicateElementKey` | préfixer les clés par l'onglet (`grille(df, cle)`) |
| Sélection Plotly perdue au rerun | la fiche au clic disparaît (la figure change parce qu'on cercle la préfecture) | garder la sélection en session (`ca_prefecture`), fixer `selected`/`unselected` opacité 1 |
| En-tête de Streamlit (`stHeader`) | opaque sur Streamlit Cloud (boutons Share/GitHub) → masque le haut de la barre du haut | option A : en-tête transparent + 230 px réservés à droite de la barre (`st-key-topbar_droite`) |
| `i18n.installer()` qui parcourt tous les attributs de `st` | lisait l'attribut déprécié `st._bottom` (avertissement) | liste explicite de fonctions enveloppées |
| `enableStaticServing` | images référencées en `app/static/<fichier>` dans le HTML | `enableStaticServing = true` dans config.toml |

---

## 14. Recette : liste de contrôle

- [ ] Les 8 pages et tous leurs onglets s'ouvrent **sans exception** (`[data-testid="stException"]`), dans les 4 langues.
- [ ] Aucun code interne, nom de fichier ni nom de source hors de la page Méthodologie (`evolutions.nettoyer()` remplace le code par son intitulé).
- [ ] Barre du haut et pied identiques sur chaque page ; barre du haut entièrement visible et non masquée par l'en-tête de Streamlit, **barre latérale ouverte puis fermée**, sur chaque hébergement visé.
- [ ] Lien de menu actif en bleu plein ; sélecteur de langue sous le logo ; filtres en pastilles ; réglages de la page Carte au-dessus du bouton Réinitialiser ; slogan + illustration en bas de la barre.
- [ ] Dans une rangée de chiffres clés, toutes les cartes ont la même hauteur et les valeurs sont alignées ; la rangée de 6 passe à 3 puis 2 colonnes sur écran étroit.
- [ ] Chaque carte KPI suit l'ordre icône/libellé → valeur (+ tendance) → phrase → contexte → réserve, liseré bas de la couleur du thème.
- [ ] Chaque graphique a sa phrase de lecture (note en carte) ; chaque constat est en pleine largeur, sous ou en tête de section.
- [ ] Chaque page se termine par Synthèse + Limite (souvent `egale=True`) puis le pied ; chaque page a au moins un « Exporter (CSV) ».
- [ ] L'onglet ouvert et les filtres sont conservés au changement de langue et au retour sur la page.
- [ ] Les choroplèthes gardent des classes fixes comparables d'une couche / d'un horizon à l'autre ; valeurs absentes en gris, jamais confondues avec 0.
- [ ] Les nombres suivent le format français ; une année n'a jamais de séparateur ; vert/rouge toujours accompagnés d'un libellé.
- [ ] Animations désactivées sous `prefers-reduced-motion`.

**Limite connue** : comme le gabarit, aucune règle n'est prévue pour les téléphones au-delà des rangées de KPI (`@media` sur `.kpi-grille.une-ligne`, `.zone-grille`, `.carte-chiffre`). La barre du haut garde ses 3 colonnes et la synthèse sa colonne de 280 px. Ajouter des `@media (max-width: …)` si un usage mobile est visé.
