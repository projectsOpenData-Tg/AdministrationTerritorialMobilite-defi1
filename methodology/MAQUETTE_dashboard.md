# Maquette du tableau de bord — spécification de reproduction

*Pour un développeur qui doit réécrire le tableau de bord « Togo Digital & Financial Inclusion » et obtenir le même rendu : mise en page, barres, cartes, onglets, dimensions, et règles d'affichage du contenu.*

Toutes les valeurs (couleurs, tailles, marges, rayons, hauteurs) sont celles du code en production au 29/09/2026 : [dashboard/theme.py](../dashboard/theme.py) pour le CSS, [dashboard/composants.py](../dashboard/composants.py) pour les composants, [.streamlit/config.toml](../.streamlit/config.toml) pour le thème de base, `dashboard/views/*.py` pour les pages. En cas de doute, le code fait foi.

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
9. Les 11 pages
10. État, filtres et interactions
11. Deux langues et format des nombres
12. Pièges connus de Streamlit
13. Recette : liste de contrôle

---

## 1. Pile technique et organisation

| Élément | Choix |
| --- | --- |
| Langage | Python 3.11+ |
| Cadre d'application | Streamlit 1.61 (`layout="wide"`, `initial_sidebar_state="expanded"`) |
| Graphiques et cartes | Plotly (`plotly.express`, `plotly.graph_objects`), choroplèthes sur GeoJSON |
| Données | pandas ; geopandas pour les contours ; tables CSV lues dans `data/analysis/`, avec `@st.cache_data` |
| Navigation | `st.navigation()` + `st.Page()`, menu en 4 groupes |
| Style | un seul bloc `<style>` injecté par `st.markdown(CSS, unsafe_allow_html=True)` au démarrage |
| Polices | Google Fonts : **Fraunces** (titres et grands chiffres, graisses 500 et 600) et **IBM Plex Sans** (texte, graisses 400, 500 et 600) |

### Arborescence

```
dashboard/
├── app.py            point d'entrée : configuration, thème, barre du haut, menu, filtres de la barre latérale, navigation.run()
├── theme.py          jetons de couleur + bloc CSS complet + appliquer_theme()
├── composants.py     barre du haut, en-tête, carte de chiffre clé, bandeaux, synthèse, pied, export, cartes géographiques, onglets
├── donnees.py        lecture des tables (cache), filtres, format des nombres — aucun recalcul d'indicateur
├── i18n.py           dictionnaire FR/EN (t), choix ponctuel (bi), traduction des valeurs de table (valeur)
├── notify.py         alerte de visite (facultatif)
├── static/           armoiries-togo-ecu.svg, logo_fr.svg, logo_en.svg, icone.svg, (logo_togo_ai_lab.png à fournir)
└── views/            une page par fichier — JAMAIS un dossier nommé pages/ (voir section 12)
    synthese.py internet.py marche.py offre.py population.py carte.py
    priorites.py diagnostic.py recommandations.py projections.py methodologie.py
.streamlit/config.toml   thème de base (section 2.1) ; enableStaticServing = true pour servir static/
```

### Règle d'architecture

**Le tableau de bord affiche, il ne calcule pas.** Chaque chiffre vient d'une table déjà calculée. Seules deux exceptions sont admises :
- les poids du score de priorité (page Priorités), recalculés avec la même formule que la table ;
- l'application d'un seuil choisi par le lecteur à une valeur déjà calculée (page Population et offre).

Aucun chiffre n'est écrit en dur dans une page.

---

## 2. Jetons de design

### 2.1 Thème de base (`.streamlit/config.toml`)

```toml
[theme]
base = "light"
primaryColor = "#0d366b"             # bleu foncé : boutons actifs, onglet actif, liens
backgroundColor = "#f4f2ec"          # fond crème de la page
secondaryBackgroundColor = "#ffffff"
textColor = "#141413"
borderColor = "#e2dfd6"

[theme.sidebar]
backgroundColor = "#0f2438"          # bleu nuit
secondaryBackgroundColor = "#1b3552"
textColor = "#ffffff"
primaryColor = "#cde2fb"
borderColor = "#2c4866"

[client]
toolbarMode = "minimal"
[server]
enableStaticServing = true           # les images de static/ sont servies sous app/static/<fichier>
```

### 2.2 Couleurs

**Neutres et structure**

| Jeton | Hex | Usage |
| --- | --- | --- |
| `ENCRE` | `#141413` | texte principal, valeurs des chiffres clés |
| `ENCRE2` | `#3a3935` | texte secondaire (réponse sous le titre, contexte) |
| `DISCRET` | `#55534e` | texte tertiaire (sous-titres, réserves, fil d'Ariane) |
| `FILET` | `#e2dfd6` | bordures des cartes et des blocs |
| filet clair | `#efece4` | séparateur interne, grille des graphiques, étiquette neutre |
| `FOND` | `#f4f2ec` | fond de page |
| `CARTE` | `#ffffff` | fond des cartes, des blocs et des graphiques |
| bleu foncé | `#0d366b` | couleur de marque : titres de marque, libellés des chiffres clés, chiffre de synthèse, onglet actif |
| jaune clair | `#fce588` | accents de la barre latérale, halo de survol des cartes |
| or | `#ffce00` | bordure de la carte du logo Togo AI Lab |

**Bandeaux**

| Bandeau | Fond | Bordure | Titre | Texte |
| --- | --- | --- | --- | --- |
| Constat | `#e8f0fb` | `#c7d8f0` | `#0d366b` | `#141413` |
| Limite | `#fdf3d7` | `#ecd28f` | `#6b4700` | `#3a2a00` |
| Synthèse chiffrée | `#ffffff` | `#e2dfd6` | `#55534e` | chiffre `#0d366b` |

**Palettes de données** (déjà validées pour l'accessibilité des couleurs ; ne pas les changer)

| Nom | Valeurs | Usage |
| --- | --- | --- |
| `BLEUS` (rampe séquentielle) | `#cde2fb` `#86b6ef` `#3987e5` `#1c5cab` `#0d366b` | cartes régionales en 5 classes, valeurs continues |
| `CATEGORIELLE` | `#2a78d6` `#eb6834` `#1baf7a` `#eda100` `#e87ba4` | séries d'un graphique |
| `CATEGORIELLE_8` | les 5 ci-dessus + `#008300` `#4a3aa7` `#e34948` | 8 pays de l'UEMOA |
| `PRIORITE` | haute `#0d366b`, moyenne `#3987e5`, faible `#cde2fb`, non classée `#b9b6ad` | cartes et légendes de priorité |
| hors sélection | `#ebe8e0` | territoires exclus par les filtres, sur une carte |
| `OCRE` | `#eda100` | communes où le mobile money est seul (priorité absolue) |
| `STATUT` | diversifiée `#2a78d6`, faible `#eda100`, mobile money dominant `#4a3aa7`, mobile money seul `#e34948` | statut d'accès financier |
| `DIMENSION` | accès `#eb6834`, maillage `#1baf7a`, couverture `#4a3aa7` | les 3 dimensions du score |
| `COULEUR_REGION` | Grand Lomé `#256abf`, Maritime hors GL `#008300`, Plateaux `#ab6300`, Centrale `#4a3aa7`, Kara `#cb4b0c`, Savanes `#bb537d` | nom de région écrit en couleur (tableaux, constats) — la couleur suit la région, jamais son rang |
| `TEXTE_CATEGORIELLE` | `#2a78d6`→`#256abf`, `#e87ba4`→`#bb537d`, `#eb6834`→`#cb4b0c`, `#eda100`→`#ab6300`, `#e34948`→`#d53b3c` | même teinte, assez foncée pour du texte sur blanc (contraste ≥ 4,5:1) |

### 2.3 Typographie

| Élément | Police | Taille | Graisse | Couleur | Autres |
| --- | --- | --- | --- | --- | --- |
| Corps, boutons, champs | IBM Plex Sans | défaut | 400 | `#141413` | — |
| `h1`, `h2`, `h3` | Fraunces | — | 600 | — | `letter-spacing: 0` |
| Question de page (titre) | Fraunces | 2.6rem | 600 | `#141413` | `line-height 1.1` |
| Surtitre | IBM Plex Sans | 0.78rem | 600 | `#0d366b` | majuscules, `letter-spacing .08em` |
| Réponse sous le titre | IBM Plex Sans | 1.05rem | 400 | `#3a3935` | `line-height 1.5`, `max-width 880px` |
| Titre de bloc | Fraunces | 1.3rem | 600 | `#141413` | — |
| Sous-titre de bloc | IBM Plex Sans | 0.86rem | 400 | `#55534e` | `line-height 1.45` |
| Valeur d'un chiffre clé | Fraunces | 2.2rem | 600 | `#141413` | `line-height 1.1` |
| Chiffre de synthèse | Fraunces | 2.6rem | 600 | `#0d366b` | `line-height 1.05` |
| Titres de bandeau (« CONSTAT »…) | IBM Plex Sans | 0.78rem | 600 | selon bandeau | majuscules, `letter-spacing .06em` |
| Étiquette (badge) | IBM Plex Sans | 0.74rem | 600 | selon ton | pilule |
| Note sous graphique | IBM Plex Sans | 0.875rem | 400 (700 si forte) | `#0d366b` | — |

Import des polices, en tête du CSS :

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, label { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
h1, h2, h3 { font-family: 'Fraunces', Georgia, serif !important; font-weight: 600 !important; letter-spacing: 0 !important; }
```

### 2.4 Rayons, ombres, espacements

| Rayon | Où |
| --- | --- |
| 8px | onglets (pastilles), liens du menu, bouton d'ouverture de la barre latérale |
| 10px | graphiques, bandeau « filtres actifs » |
| 12px | barre des onglets, pied de page, carte du logo |
| 14px | carte de chiffre clé, Constat, Synthèse chiffrée, Limite |
| 18px | barre du haut, carte de recommandation |
| 999px | étiquettes (badges) |

| Ombre | Où |
| --- | --- |
| `0 1px 8px rgba(13,54,107,.08)` | barre du haut |
| `0 1px 4px rgba(13,54,107,.06)` | barre des onglets, pied de page |
| `0 1px 6px rgba(13,54,107,.06)` | carte de recommandation (repos) |
| `0 2px 6px rgba(0,0,0,.08)` | carte du logo |
| `0 0 0 3px rgba(252,229,136,.35), 0 10px 24px rgba(13,54,107,.12)` | carte de chiffre clé au survol |
| `0 12px 28px rgba(13,54,107,.14)` | carte de recommandation au survol |

Contenu principal : `padding-top 0.6rem`, `padding-bottom 2rem`, `padding-left/right 1.5rem`, **largeur fluide** (`max-width: 100%`). Ne pas fixer de largeur maximale : sur un écran large, le contenu centré laisserait un vide des deux côtés.

```css
[data-testid="stMainBlockContainer"] { padding-top: 0.6rem; padding-bottom: 2rem; padding-left: 1.5rem !important;
  padding-right: 1.5rem !important; max-width: 100% !important; }
```

⚠️ `padding-top: 0.6rem` ne tient que si l'en-tête de Streamlit est transparent. Selon l'hébergement, il ne l'est pas toujours : voir section 4, « Contrainte : l'en-tête de Streamlit selon l'hébergement ».

---

## 3. Disposition générale de l'écran

```
┌────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│  BARRE LATÉRALE    │  ┌─────────────────────── BARRE DU HAUT (carte blanche) ────────────────┐ │
│  fond #0f2438      │  │ [écu] Ministère…      🇹🇬 Togo Digital & Financial     [FR][EN][LOGO] │ │
│                    │  │                        Accès numérique et inclusion…                 │ │
│  [logo]            │  └──────────────────────────────────────────────────────────────────────┘ │
│                    │  Tableau de bord › Page                       ← fil d'Ariane               │
│  PRINCIPAL         │  SURTITRE                                                                   │
│   ◦ Synthèse       │  Question de la page ?                        ← Fraunces 2.6rem            │
│  ANALYSES          │  Phrase de réponse, la conclusion d'abord.                                  │
│   ◦ …5 pages       │  [ Filtres actifs : … ]                       ← si des filtres sont posés  │
│  PILOTAGE          │                                                                             │
│   ◦ …4 pages       │  4 vues — cliquez sur un onglet                                             │
│  MÉTHODOLOGIE      │  ┌──────────────────── barre d'onglets ─────────────────────────────────┐  │
│   ◦ Sources        │  │ [■ Vue synthèse ■] [ Onglet 2 ] [ Onglet 3 ] [ Onglet 4 ]            │  │
│  ────────────      │  └──────────────────────────────────────────────────────────────────────┘  │
│  Filtres           │  Vue synthèse · vue 1 sur 4                                                 │
│  RÉGION   (pastilles)│                                                                           │
│  MAILLE   (segments)│  … contenu de l'onglet (section 7) …                                      │
│  PRIORITÉ (pastilles)│                                                                           │
│  MILIEU   (pastilles)│  Données : … Mise à jour : septembre 2026.   ← mention des sources       │
│  [Réinitialiser]   │  ┌──────────────────────── PIED DE PAGE (carte) ─────────────────────────┐ │
│  39 préfectures ·… │  │        Togo AI Lab — Data Challenge | Économie numérique — Défi 2      │ │
│                    │  │        Diagnostic territorial et aide à la décision…                  │ │
└────────────────────┴──┴────────────────────────────────────────────────────────────────────────┴─┘
```

- La barre du haut et le pied de page **ne sont pas collants** : la barre du haut est le premier élément du contenu, le pied le dernier, et les deux défilent avec la page. Ils sont identiques sur les 11 pages.
- La barre du haut est rendue une fois dans `app.py`, avant `navigation.run()`. Le pied est appelé (`pied()`) à la fin de chaque page.
- La barre latérale garde la largeur par défaut de Streamlit, redimensionnable à la souris.
- Au-dessus de la barre du haut se trouve l'en-tête de Streamlit (`stHeader`), qui n'apparaît pas sur le schéma. Il reste invisible en local et sur Heroku tant que la barre latérale est ouverte. Il devient une bande opaque d'environ 60 px sur Streamlit Community Cloud, ou quand la barre latérale est fermée (section 4).

---

## 4. Barre du haut

### Structure

Un conteneur à clé `topbar` (`st.container(key="topbar")`, que Streamlit rend avec la classe `.st-key-topbar`), puis 3 colonnes `st.columns([1, 1.3, 1], vertical_alignment="center")` :

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│ ┌──┐ Ministère de l'Efficacité du       │  🇹🇬 Togo Digital & Financial Inclusion  │ [FR][EN] ┌──────────┐ │
│ │écu│ Service Public et de la           │  Accès numérique et inclusion          │          │ TOGO      │ │
│ └──┘ Transformation Numérique           │  financière au Togo (italique)         │          │ AI LAB    │ │
│     colonne 1 (poids 1)                 │      colonne 2 (poids 1.3), centrée    │ col. 3 (1) └──────────┘ │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

### CSS

```css
div.st-key-topbar { background: #ffffff; min-height: 92px; padding: 16px 22px; box-shadow: 0 1px 8px rgba(13,54,107,.08);
  margin-bottom: 0.6rem; box-sizing: border-box; border: 1px solid #e2dfd6; border-radius: 18px; }
div.st-key-topbar [data-testid="stHorizontalBlock"] { align-items: center; }
.topbar-ligne { display: flex; align-items: center; gap: 10px; }
.armoiries { height: 38px; width: auto; flex-shrink: 0; }
.topbar-ministere { font-size: 0.76rem; color: #3a3935; line-height: 1.3; }
.topbar-centre { text-align: center; }
.topbar-titre { font-family: 'Fraunces', Georgia, serif; font-size: 1.2rem; font-weight: 600; color: #0d366b; }
.topbar-sous-titre { font-size: 0.76rem; color: #55534e; font-style: italic; margin-top: 1px; }
div.st-key-topbar_droite { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }
div.st-key-topbar_droite button { padding: 0.15rem 0.55rem !important; min-height: 1.6rem !important; }
.ai-lab-logo-carte { display: inline-flex; align-items: center; justify-content: center; background: #ffffff;
  border: 2px solid #ffce00; border-radius: 12px; padding: 7px 12px; box-shadow: 0 2px 6px rgba(0,0,0,.08); height: 56px; }
.ai-lab-logo-carte img { height: 40px; width: auto; max-width: 140px; object-fit: contain; }
.ai-lab-logo-repli { font-size: 0.55rem; font-weight: 700; color: #dc2626; line-height: 1.2; text-align: center; }
```

### Contenu

| Zone | Contenu | Détail |
| --- | --- | --- |
| Gauche | armoiries (écu seul, SVG, 38 px de haut) + nom du ministère | FR : « Ministère de l'Efficacité du Service Public et de la Transformation Numérique » ; EN : « Ministry of Public Service Efficiency and Digital Transformation ». Repli si l'image manque : 🛡️ |
| Centre | « 🇹🇬 Togo Digital & Financial Inclusion » + sous-titre | Le nom ne se traduit pas. Sous-titre FR : « Accès numérique et inclusion financière au Togo » ; EN : « Digital access and financial inclusion in Togo » |
| Droite | colonnes internes `[1, 1, 2]` : bouton FR, bouton EN, carte du logo | bouton de la langue active en `type="primary"` (plein, bleu foncé), l'autre en `secondary`. Clic : `st.session_state["lang"] = "fr"/"en"` puis `st.rerun()` |

**Fichier à fournir** : `static/logo_togo_ai_lab.png`. Tant qu'il manque, la carte affiche le texte de repli « TOGO / AI LAB » en rouge.

### Contrainte : l'en-tête de Streamlit selon l'hébergement

**Constat du 03/10/2026.** Sur Streamlit Community Cloud, le haut de la barre du haut est caché : on ne voit plus que le bas du titre et des boutons FR/EN. Le même code s'affiche entièrement sur Heroku.

**Mécanisme** (lu dans le code de Streamlit 1.61.1) :
- Streamlit place son propre en-tête au-dessus du contenu : `<header class="stAppHeader" data-testid="stHeader">`, en position absolue en haut de la page, haut d'environ 3,75rem (60 px), et placé au-dessus du contenu.
- **S'il n'a rien à afficher**, il est vide, transparent, et laisse passer les clics (`pointer-events: none`).
- **Dès qu'il affiche quelque chose**, il prend la couleur du fond de la page (`#f4f2ec`), devient opaque, et contient alors un bloc `[data-testid="stToolbar"]`.
- Il a quelque chose à afficher dans quatre cas :
  - la barre latérale est fermée : il porte le bouton de réouverture `stExpandSidebarButton` ;
  - un logo est affiché alors que la barre latérale est fermée ;
  - le menu est placé en haut de page (`position="top"`) ;
  - la barre d'outils contient des boutons, notamment ceux que l'hébergeur ajoute (`stToolbarActions`).

**Conséquence selon le lieu de déploiement**, avec `padding-top: 0.6rem` :

| Hébergement | Barre latérale | En-tête de Streamlit | Barre du haut |
| --- | --- | --- | --- |
| Local, Docker, Heroku | ouverte | transparent, vide | entièrement visible |
| Local, Docker, Heroku | fermée | opaque (bouton de réouverture) | **haut caché** |
| Streamlit Community Cloud | ouverte ou fermée | opaque : la plateforme y ajoute ses boutons « Fork » et GitHub | **haut caché** |

**Ce qui ne marche pas :**
- `toolbarMode = "minimal"` (`.streamlit/config.toml`) masque le menu de Streamlit, mais pas les boutons ajoutés par l'hébergeur. D'après les réponses du forum Streamlit, aucun réglage ne retire « Fork » et GitHub quand l'application vient d'un dépôt public. Seul un dépôt privé les retire, et Streamlit Cloud n'accepte alors qu'une seule application privée gratuite.
- **Masquer tout l'en-tête** (`[data-testid="stHeader"] { display: none; }`) : à proscrire. Il contient le bouton qui rouvre la barre latérale : une fois la barre fermée, le lecteur ne pourrait plus la rouvrir, ni accéder au menu et aux filtres.
- **Mettre `padding-top: 4.4rem` partout** : cela laisse une bande vide de 60 px en haut de page en local et sur Heroku.
- **Masquer seulement « Fork » et GitHub** (`[data-testid="stToolbarActions"] { display: none; }`) : l'en-tête reste opaque, simplement vide, et couvre toujours la barre du haut.

**Règle à appliquer.** Elle est **absente de `dashboard/theme.py` au 03/10/2026** et doit être ajoutée à la réécriture. Le principe : réserver la hauteur de l'en-tête **seulement quand il est visible**. L'en-tête ne contient un bloc `stToolbar` que dans ce cas, et `:has()` permet de le détecter :

```css
/* L'en-tête de Streamlit devient opaque dès qu'il affiche un bouton (Fork et GitHub sur Streamlit Cloud,
   bouton de réouverture de la barre latérale) : le contenu descend alors de sa hauteur. */
body:has([data-testid="stHeader"] [data-testid="stToolbar"]) [data-testid="stMainBlockContainer"] { padding-top: 4.4rem; }
```

4.4rem correspond à la hauteur de l'en-tête (3,75rem), plus l'espace habituel (0,6rem). `:has()` est déjà utilisé par le thème, et il est pris en charge par les navigateurs actuels (Chrome 105+, Safari 15.4+, Firefox 121+).

**Facultatif** : `[data-testid="stToolbarActions"] { display: none; }` masque en plus « Fork » et GitHub sur Streamlit Cloud. Streamlit ne prend pas cette astuce en charge, et une mise à jour peut la casser. Il faut la revérifier après chaque montée de version.

---

## 5. Barre latérale

### De haut en bas

1. **Logo** : `st.logo("static/logo_<langue>.svg", size="large", icon_image="static/icone.svg")`, soit le logo complet barre ouverte et l'icône (drapeau seul) barre fermée. Le logo est un SVG de 232 × 44 : drapeau du Togo (32 × 20) à gauche ; « Togo Digital & Financial » en Georgia 14 px gras blanc ; sous-titre en 11 px `#c9d4e0`. CSS : `[data-testid="stSidebarHeader"] img { height: 2.6rem; }`.
2. **Menu** en 4 groupes (section 9 pour la liste) :
   - titres de groupe en majuscules, 0.72rem, `letter-spacing .08em`, couleur `#9fb2c6` ;
   - liens en 0.93rem, chacun avec une icône Material ;
   - lien actif entouré d'une bordure 1,5 px `#fce588`, rayon 8 px. Les autres liens ont la même bordure, transparente, pour ne pas bouger au changement de page.
3. **Séparateur** (`st.divider()`), puis le titre « **Filtres** » en gras.
4. **Quatre filtres**, dans cet ordre :

| Libellé (FR / EN) | Widget | Valeurs | Défaut | Clé d'état |
| --- | --- | --- | --- | --- |
| Région / Region | `st.pills`, choix multiple | Grand Lomé, Maritime hors Grand Lomé, Plateaux, Centrale, Kara, Savanes | aucune | `f_regions` |
| Maille de la carte / Map scale | `st.segmented_control`, choix unique | Commune, Préfecture | Préfecture | `f_maille` |
| Priorité / Priority | `st.pills`, choix multiple | absolue, haute, moyenne, faible, non classée | aucune | `f_priorites` |
| Milieu / Area type | `st.pills`, choix multiple | Grand Lomé, Autres villes, Rural | aucun | `f_milieux` |

5. **Bouton** « Réinitialiser les filtres » (« Reset filters »), pleine largeur, icône `:material/restart_alt:`. Son rappel remet les 4 clés à leur défaut.
6. **Légende** (`st.caption`) : « 39 préfectures · 117 communes · points de service 2021/2022 · population 2022 ».

### CSS de la barre latérale

```css
[data-testid="stSidebar"] [data-testid="stNavSectionHeader"] { text-transform: uppercase; letter-spacing: .08em; font-size: .72rem; color: #9fb2c6; }
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span { font-size: .93rem; }
[data-testid="stSidebarNavLink"] { border: 1.5px solid transparent; border-radius: 8px; }
[data-testid="stSidebarNavLink"][aria-current="page"] { border-color: #fce588 !important; }
/* titres des filtres : majuscules jaune clair, distincts des choix */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { text-transform: uppercase; letter-spacing: .07em; font-size: .74rem !important;
  font-weight: 700; color: #fce588 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { margin-top: .5rem; }
/* bouton d'ouverture/fermeture : toujours visible, bordure jaune clair */
[data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"] { display: flex !important; visibility: visible !important; opacity: 1 !important; }
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"] { background: transparent !important;
  border: 1.5px solid #fce588 !important; border-radius: 8px !important; }
[data-testid="stSidebarCollapseButton"] button:hover, [data-testid="stExpandSidebarButton"]:hover { background: rgba(252,229,136,.15) !important; }
```

---

## 6. Pied de page

Deux éléments, à la fin de chaque page :

1. **Mention des sources** (`.pied`) en 0.8rem `#55534e`, `margin-top 18px` : « Données : portail national de données géographiques du Togo et sources institutionnelles complémentaires. Mise à jour : septembre 2026. » Aucun nom de fichier ni de source précise : le détail est sur la page Sources et méthode.
2. **Carte d'identité** (`.pied-identite`), centrée :

```css
.pied-identite { background: #ffffff; border: 1px solid #e2dfd6; border-radius: 12px; padding: 16px 24px;
  margin-top: 20px; text-align: center; box-shadow: 0 1px 4px rgba(13,54,107,.06); }
.pied-identite-titre { font-size: .92rem; font-weight: 800; color: #0d366b; line-height: 1.4; }
.pied-identite-sous-titre { font-size: .78rem; color: #55534e; margin-top: 4px; line-height: 1.5; }
```

| | Français | Anglais |
| --- | --- | --- |
| Titre | Togo AI Lab — Data Challenge \| Économie numérique — Défi 2 | Togo AI Lab — Data Challenge \| Digital Economy — Challenge 2 |
| Sous-titre | Diagnostic territorial et aide à la décision pour l'accès numérique et l'inclusion financière au Togo | Territorial diagnostic and decision support for digital access and financial inclusion in Togo |

---

## 7. Gabarit d'une page

Chaque page suit le même ordre, de haut en bas : le lecteur sait où regarder d'une page à l'autre.

| # | Zone | Composant | Règle de contenu |
| --- | --- | --- | --- |
| 1 | Fil d'Ariane | `ariane(page)` | « Tableau de bord › **Nom de la page** » |
| 2 | En-tête | `entete(surtitre, question, reponse_html)` | surtitre = nom de la page ; titre = **une question** ; réponse = **la conclusion d'abord**, chiffres clés en `<strong>` |
| 3 | Filtres actifs | bandeau `.filtres-actifs` | seulement si un filtre est posé, ou pour dire que les chiffres sont nationaux et ne bougent pas avec les filtres |
| 4 | Onglets | `onglets(cle, libelles)` | 3 à 5 vues ; la première est toujours une vue synthèse |
| 5 | Chiffres clés | `rangee_kpi(groupe, [carte_kpi(...)…])` | 3 ou 4 cartes par rangée ; règle des dix secondes |
| 6 | Visuel principal + Constat | `st.columns([1.5, 1])` : bloc graphique ou carte à gauche, `constat()` à droite | jamais un graphique sans phrase de lecture |
| 7 | Visuels secondaires | blocs à bordure, en 1 ou 2 colonnes | un bouton « Exporter (CSV) » sous chaque bloc |
| 8 | Synthèse chiffrée | `synthese(chiffre, legende, puces)` | **un seul** chiffre-titre et 3 ou 4 puces, chacune renvoyant à l'onglet de détail |
| 9 | Limite | `limite(texte)` | la réserve propre à ce qui est affiché, en jaune, à la fin de chaque onglet |
| 10 | Pied | `pied()` | identique partout |

### Exemple : l'onglet « Vue synthèse » d'une page d'analyse

```
SURTITRE
Question de la page ?
Réponse : la conclusion, avec ses 1 ou 2 chiffres clés en gras.

4 vues — cliquez sur un onglet
[■ Vue synthèse ■][ Vue 2 ][ Vue 3 ][ Vue 4 ]
Vue synthèse · vue 1 sur 4

TITRE DE GROUPE DE LA RANGÉE
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ KPI 1   │ │ KPI 2   │ │ KPI 3   │ │ KPI 4   │   ← grille auto-fit, minmax(230px, 1fr), gap 12px
└─────────┘ └─────────┘ └─────────┘ └─────────┘

┌───────────────── bloc à bordure (1.5) ─────────┐  ┌──── CONSTAT (1) ────────────┐
│ Titre du bloc (Fraunces 1.3rem)                 │  │ Une phrase de décision,      │
│ Sous-titre : ce que montre le graphique         │  │ chiffres en gras / couleur.  │
│ ┌─────────────── graphique, 420 px ────────────┐│  └─────────────────────────────┘
│ │                                               ││  ┌──── bloc secondaire ────────┐
│ └───────────────────────────────────────────────┘│  │ Titre + liste ou tableau     │
│ [⤓ Exporter (CSV)]                              │  └─────────────────────────────┘
└─────────────────────────────────────────────────┘

┌──────────────────────── SYNTHÈSE CHIFFRÉE ─────────────────────────────────┐
│ SYNTHÈSE CHIFFRÉE   │ • Puce 1 en gras, suite. (détail : onglet « … »)      │
│ × 3,2               │ • Puce 2 …                                            │
│ légende du chiffre  │ • Puce 3 …                                            │
│ (colonne de 280 px) │                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
┌──────────────────────── LIMITE DE CETTE PAGE (jaune) ──────────────────────┐
│ La réserve propre à ce qui est affiché.                                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Règles de contenu, sur toutes les pages

- **Quatre questions**, dans l'ordre du menu : quelle est la situation ? où sont les problèmes ? pourquoi ces territoires ? quelle action engager ?
- **Règle des dix secondes** : un message, trois chiffres, une action par page.
- **Langage de décideur.** Les pages d'analyse ne montrent jamais de noms de fichiers ou de scripts, de numéros d'étapes ou de documents, de codes internes (O4-01, P9, A13…) ni de noms de sources. Tout cela n'apparaît que sur la page Sources et méthode, et un code y est toujours accompagné de son intitulé.
- **Couleur :**
  - les phrases de lecture (notes sous graphique) sont en bleu foncé `#0d366b` ;
  - dans un constat, un chiffre est écrit dans la couleur de sa série (`<strong style="color:…">`) ;
  - un nom de région est écrit dans la couleur de la région ;
  - aucune information n'est portée par la couleur seule : il y a toujours un libellé.
- **Graphiques** : une légende dès deux séries ; jamais deux axes verticaux.
- **Libellés imposés** : « points de service », jamais « agents » ; « couverture théorique » ; « sans fibre recensée », jamais « sans Internet ».

---

## 8. Composants

### 8.1 Fil d'Ariane

`<div class="ariane">Tableau de bord › <b>Page</b></div>` en 0.85rem `#55534e`, le nom de page en `#141413`, `margin-bottom .4rem`.

### 8.2 En-tête

```html
<div class="surtitre">Usage d'Internet</div>
<div class="question">L'usage progresse-t-il, et à quel prix ?</div>
<div class="reponse">L'usage ralentit depuis 2021 : <strong>39,5 %</strong> en 2024 … 1 Go coûte <strong>…</strong> du revenu mensuel.</div>
```

`.question { margin: .2rem 0 .5rem; }` ; `.reponse { max-width: 880px; margin-bottom: .6rem; }`.

### 8.3 Bandeau « filtres actifs »

```css
.filtres-actifs { font-size: .85rem; color: #3a3935; background: #ffffff; border: 1px solid #e2dfd6; border-radius: 10px; padding: 8px 12px; margin-bottom: .6rem; }
```

Il a trois usages :
- rappeler les filtres posés : « Filtres actifs : Kara · Priorité haute · Rural. » ;
- prévenir que les chiffres nationaux ne changent pas avec les filtres ;
- résumer une sélection (page Recommandations : « 12 recommandations · 22 communes en priorité absolue (… habitants) · … »).

### 8.4 Carte de chiffre clé (KPI) — le composant central

**Anatomie.** Cinq emplacements, toujours dans cet ordre :

```
┌──────────────────────────────────────────────┐  ← .kpi : fond blanc, bordure 1px #e2dfd6, rayon 14px, padding 16px 18px
│ INTERNET (2024)                  ( Sous le seuil ) │  ← .kpi-tete : libellé + étiquette sur la même ligne, min-height 2.5rem
│ 39,5 %                                        │  ← .kpi-valeur : Fraunces 2.2rem 600 (+ .kpi-unite optionnelle)
│ de la population utilise Internet            │  ← .kpi-phrase : 0.95rem 600 — se lit avec la valeur, comme une phrase
│ seuil de 40 % ; Afrique subsaharienne : …    │  ← .kpi-contexte : 0.84rem #3a3935 — seuil ou comparaison
│ ──────────────────────────────────────────── │
│ Estimation internationale. Les enquêtes…     │  ← .kpi-reserve : 0.78rem #55534e, filet en haut, collée en bas
└──────────────────────────────────────────────┘
```

**Méthode d'affichage** (paramètres de `carte_kpi(libelle, valeur, phrase, contexte, reserve, etiquette, ton, unite)`) :

| Emplacement | Contenu | Exemple |
| --- | --- | --- |
| `libelle` | ce qui est mesuré, avec l'année ou la période entre parenthèses | « Internet (2024) » |
| `valeur` | le chiffre seul, formaté selon la langue | « 39,5 % », « 22 », « Duopole » |
| `unite` (optionnel) | unité accolée, en 1.05rem 600 | « communes » |
| `phrase` | la suite de la valeur : chiffre + phrase forment une phrase complète | « de la population utilise Internet » |
| `contexte` | le seuil, la comparaison ou la population concernée | « seuil de 40 % ; Afrique subsaharienne : … » |
| `reserve` | ce que le chiffre ne mesure pas ; vide = pas de pied | « Un abonnement n'est pas une personne… » |
| `etiquette` + `ton` | verdict court, coloré selon le ton | « Sous le seuil » / `alerte` |

**Rangée de cartes.** Chaque rangée a un titre de groupe (`.groupe` : 0.82rem 600 `#55534e`, `margin .6rem 0 .4rem`), puis une grille :

```css
.kpi-grille { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; margin-bottom: 6px; }
.kpi { background: #fff; border: 1px solid #e2dfd6; border-radius: 14px; padding: 16px 18px; display: flex; flex-direction: column; gap: 6px;
       box-sizing: border-box; position: relative; overflow: hidden; transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.kpi-tete { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; min-height: 2.5rem; }
.kpi-libelle { font-size: .76rem; font-weight: 700; text-transform: uppercase; letter-spacing: .02em; line-height: 1.35; color: #0d366b; }
.kpi-valeur { font-family: 'Fraunces', Georgia, serif; font-size: 2.2rem; font-weight: 600; line-height: 1.1; color: #141413; }
.kpi-unite { font-family: 'IBM Plex Sans', system-ui, sans-serif; font-size: 1.05rem; font-weight: 600; margin-left: 6px; }
.kpi-phrase { font-size: .95rem; font-weight: 600; line-height: 1.4; color: #141413; }
.kpi-contexte { font-size: .84rem; line-height: 1.45; color: #3a3935; }
.kpi-reserve { font-size: .78rem; line-height: 1.4; color: #55534e; border-top: 1px solid #efece4; padding-top: 7px; margin-top: auto; }
```

**Dimensions et comportement :**
- largeur minimale 230 px, puis partage égal de la largeur. Une rangée de 4 tient sur un écran large et passe à la ligne sur un écran étroit ;
- dans une rangée, toutes les cartes ont **la même hauteur** : la grille étire les cartes, et `margin-top: auto` colle la réserve en bas ;
- `min-height: 2.5rem` sur l'en-tête aligne les valeurs d'une carte à l'autre, même quand un libellé tient sur deux lignes ;
- une rangée = **une seule** chaîne HTML (toutes les cartes dans un même `st.markdown`). Sinon, Streamlit crée un bloc par carte et la grille ne fonctionne plus.

**Survol** : la carte se soulève, s'entoure d'un halo jaune clair, et un reflet la traverse.

```css
.kpi::after { content: ""; position: absolute; top: 0; left: -80%; width: 50%; height: 100%; pointer-events: none;
              background: linear-gradient(115deg, transparent, rgba(252,229,136,.45), transparent); transform: skewX(-20deg); }
.kpi:hover { transform: translateY(-3px); border-color: #fce588; box-shadow: 0 0 0 3px rgba(252,229,136,.35), 0 10px 24px rgba(13,54,107,.12); }
.kpi:hover::after { left: 130%; transition: left .8s ease; }
@media (prefers-reduced-motion: reduce) { .kpi, .kpi:hover { transform: none; transition: none; } .kpi::after { display: none; } }
```

**Typographie** : « 2 % » et « 10 000 » ne doivent jamais se couper en fin de ligne. Remplacer l'espace avant « % » et le séparateur de milliers par une espace insécable (`&nbsp;`).

### 8.5 Étiquettes (badges)

`.etiquette { font-size: .74rem; font-weight: 600; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }`

| Ton | Fond | Texte | Sens |
| --- | --- | --- | --- |
| `alerte` | `#fdf0d2` | `#6b4700` | sous un seuil, à surveiller |
| `ok` | `#e3eefb` | `#0d366b` | seuil franchi, préalable, priorité haute |
| `critique` | `#fbe3e2` | `#8a1c1b` | priorité absolue |
| `neutre` | `#efece4` | `#3a3935` | horizon, « à confirmer » |
| `national` | `#efece4` | `#55534e` (graisse 500) | chiffre national |
| `reco-priorite` | `#fdf0d2` | `#6b4700` | priorité d'une recommandation |
| `reco-nature` | `#ece9fb` | `#4a3aa7` | immédiate / conditionnelle / veille |
| `reco-horizon` | `#e2f4ec` | `#11613f` | 1 an / 3 ans / 5 ans |

### 8.6 Bloc à bordure

`st.container(border=True)` : bordure Streamlit par défaut, 1 px `#e2dfd6`, coins arrondis. Contenu type :

1. `titre_bloc(titre, sous_titre)` : titre en Fraunces 1.3rem, sous-titre en 0.86rem `#55534e` qui dit ce que montre le visuel et sa convention ;
2. le graphique, la carte ou le tableau ;
3. `export_csv(df, "nom.csv", cle)`.

### 8.7 Bandeau « Constat »

```css
.constat { background: #e8f0fb; border: 1px solid #c7d8f0; border-radius: 14px; padding: 16px 18px; margin-bottom: 14px; }
.constat-titre { font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #0d366b; }
.constat-texte { font-size: .95rem; line-height: 1.5; color: #141413; margin-top: 4px; }
```

- **Titre** : « CONSTAT » (« FINDING »).
- **Texte** : une ou deux phrases en termes de décision, chiffres en `<strong>`, éventuellement en couleur.
- **Position** : à droite du visuel principal, ou en tête d'onglet.

### 8.8 Bandeau « Synthèse chiffrée »

```css
.synthese { background: #fff; border: 1px solid #e2dfd6; border-radius: 14px; padding: 20px 24px; display: grid;
            grid-template-columns: 280px 1fr; gap: 26px; align-items: center; margin-top: 8px; }
.synthese-titre { font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #55534e; }
.synthese-chiffre { font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; font-weight: 600; color: #0d366b; line-height: 1.05; margin: 4px 0; }
.synthese-legende { font-size: .88rem; line-height: 1.45; }
.synthese ul { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 8px; font-size: .92rem; line-height: 1.5; }
```

- **Colonne de gauche (280 px)** : « SYNTHÈSE CHIFFRÉE », **un seul** chiffre-titre (le plus frappant), puis sa légende.
- **Colonne de droite** : 3 ou 4 puces. Chacune commence par une phrase en gras et se termine par un renvoi en italique : *(détail : onglet « … »)*.

### 8.9 Bandeau « Limite »

```css
.limite { background: #fdf3d7; border: 1px solid #ecd28f; border-radius: 14px; padding: 14px 18px; margin-top: 14px; }
.limite-titre { font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #6b4700; }
.limite-texte { font-size: .9rem; line-height: 1.5; color: #3a2a00; margin-top: 4px; }
/* variante discrète (page Synthèse) : sans fond ni cadre, filet en haut */
.limite.discret { background: transparent; border: 0; border-top: 1px solid #e2dfd6; border-radius: 0; padding: 12px 0 0; margin-top: 18px; }
.limite.discret .limite-titre, .limite.discret .limite-texte { color: #55534e; }  .limite.discret .limite-texte { font-size: .86rem; }
```

- Titre « LIMITE DE CETTE PAGE » : la limite voyage avec l'analyse, elle n'est pas renvoyée à la page Méthodologie.
- Sur la Synthèse, les réserves sont déjà sous chaque chiffre. Le bandeau y devient discret et s'intitule « Ce que cette page ne montre pas ».

### 8.10 Sous-onglets

**Rendu** : une barre blanche de pastilles qui se partagent toute la largeur, l'onglet actif plein en bleu foncé.

```
4 vues — cliquez sur un onglet                                         ← .onglets-aide : 0.84rem 600 #3a3935
┌──────────────────────────────────────────────────────────────────────┐
│ [■■ Vue synthèse ■■] [ Évolution de l'usage ] [ Accès et freins… ] [ Le Togo… ] │
└──────────────────────────────────────────────────────────────────────┘
Vue synthèse · vue 1 sur 4                                              ← .onglets-repere : 0.82rem italique #55534e
```

```css
.stTabs [role="tablist"] { gap: 4px; background: #fff; padding: 6px; border-radius: 12px; border: 1px solid #e2dfd6;
  box-shadow: 0 1px 4px rgba(13,54,107,.06); flex-wrap: wrap; }
.stTabs [data-testid="stTab"] { border-radius: 8px; padding: 7px 15px; height: auto; margin: 0; flex: 1 1 auto; justify-content: center; text-align: center; }
.stTabs [data-testid="stTab"] p { font-size: .9rem; font-weight: 600; color: #55534e; }
.stTabs [data-testid="stTab"]:hover { background: #e8f0fb; }
.stTabs [data-testid="stTab"]:hover p { color: #0d366b; }
.stTabs [data-testid="stTab"][aria-selected="true"] { background: #0d366b !important; }
.stTabs [data-testid="stTab"][aria-selected="true"] p { color: #fff !important; }
.stTabs .react-aria-SelectionIndicator { display: none; }   /* masque le soulignement natif */
.onglets-aide { font-size: .84rem; font-weight: 600; color: #3a3935; margin: .8rem 0 .3rem; }
.onglets-repere { font-size: .82rem; font-style: italic; color: #55534e; margin: .1rem 0 .4rem; }
```

**Comportement** (fonction `onglets(cle, libelles)`) :
- **seul l'onglet ouvert s'exécute** : chaque onglet est entouré de `if onglet.open is not False:`, ce qui accélère les pages lourdes ;
- l'onglet actif est retenu **par son rang**, pas par son libellé, dans `st.session_state[f"{cle}_rang"]`. Il survit au changement de langue (le libellé change, le rang non) et au passage par une autre page ;
- la clé du widget inclut la langue (`f"{cle}_{langue}"`), et `st.tabs(..., default=libelles[rang], on_change=retenir)` relit le rang ;
- les pastilles passent à la ligne sur un écran étroit, au lieu de défiler.

### 8.11 Carte de recommandation (page Recommandations)

**Grille** : `cols = st.columns(3)` ; la carte n° i va dans `cols[i % 3]`, dans un `st.container(border=True, key=f"carte_reco_{id}")`.

```
┌───────────────────────────────────────────┐   rayon 18px, padding 18px 20px, ombre 0 1px 6px rgba(13,54,107,.06)
│ ┌────┐                                    │
│ │ 🏦 │ AGENCES FINANCIÈRES                 │   ← .reco-pastille 34×34 rayon 10 + libellé du thème 0.72rem 700 majuscules
│ └────┘                                    │
│ Une première agence financière dans       │   ← .action-titre 0.92rem 600, min-height 3.4rem (titres alignés)
│ chacune des 22 communes…                  │
│ Porter … de 0 à 1 agence                  │   ← .kpi-phrase : la cible chiffrée
│ 22 communes · 123 456 habitants concernés │   ← .kpi-contexte : territoires · habitants
│ (Priorité absolue) (Immédiate) (1 an)     │   ← étiquettes priorité / nature / horizon
└───────────────────────────────────────────┘
```

```css
div[class*="st-key-carte_reco_"] { background: #fff; border: 1px solid #e2dfd6 !important; border-radius: 18px !important; padding: 18px 20px !important;
  box-shadow: 0 1px 6px rgba(13,54,107,.06); transition: transform .25s ease, box-shadow .25s ease; }
div[class*="st-key-carte_reco_"]:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(13,54,107,.14); }
.reco-theme { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.reco-pastille { width: 34px; height: 34px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }
.reco-theme-lib { font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.reco-meta { margin-top: 10px; padding-bottom: 8px; }
```

| Thème | Emoji | Fond de pastille | Couleur du libellé |
| --- | --- | --- | --- |
| Agences financières | 🏦 | `#e3eefb` | `#1c5cab` |
| Mobile money | 📱 | `#fde8dd` | `#b4451a` |
| Couverture réseau | 📡 | `#e2f4ec` | `#11613f` |
| Fibre | 🌐 | `#ece9fb` | `#4a3aa7` |
| Prix et frais | 💰 | `#fbe4f0` | `#a3246b` |
| Compétences et équipement | 🎓 | `#fdf0d2` | `#6b4700` |
| Investissement (veille) | 📈 | `#dff3f6` | `#0e6475` |

**Règle** : on n'additionne jamais les habitants d'une recommandation à l'autre, parce que les territoires se recoupent. Une légende sous la barre de résumé le dit.

### 8.12 Liste numérotée et liste d'actions (page Synthèse)

- `.ecarts` : liste `<ol>` sans puces, `gap 12px`, 0.92rem. Le numéro est en Fraunces 1.1rem 600 `#0d366b`, dans une colonne de 16 px. Chaque point commence par une phrase en gras.
- `.action` : une action par ligne, séparée par un filet `#efece4` (aucun filet sous la dernière). Le titre est en 0.92rem 600 ; la ligne de méta-données contient les étiquettes et les habitants, en 0.82rem `#55534e`.

### 8.13 Graphiques (Plotly)

Mise en forme commune, à appliquer à chaque figure (`habiller(fig, hauteur, suffixe_y)`) :

```python
fig.update_layout(height=hauteur, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                  font=dict(family="IBM Plex Sans, system-ui, sans-serif", color="#141413", size=11),
                  legend=dict(orientation="h", y=1.12, x=0),               # légende horizontale, au-dessus, à gauche
                  yaxis=dict(ticksuffix=" %", gridcolor="#efece4"), xaxis=dict(gridcolor="#efece4"),
                  hoverlabel=dict(bgcolor="#ffffff", font_size=12),
                  separators=", " if langue == "fr" else ".,")             # virgule décimale en français
st.plotly_chart(fig, key=cle, config={"displayModeBar": False})           # pas de barre d'outils Plotly
```

CSS : `[data-testid="stPlotlyChart"] { background: #fff; border-radius: 10px; }`.

| Hauteur | Usage |
| --- | --- |
| 240–300 px | petit graphique d'appoint (rang, distributeurs, barres de trajectoire) |
| 330–380 px | graphique standard dans une demi-largeur |
| 400–440 px | graphique principal d'un onglet |

**Conventions** :
- série principale en bleu foncé `#0d366b`, 3 px ; repère externe en gris `#8a8780`, pointillé ;
- seuil en ligne tiretée `#8a1c1b`, avec une annotation (« Seuil de 40 % ») ;
- dernière valeur annotée en gras au bout de la courbe ;
- une note de lecture sous le graphique (`note(texte)`, bleu foncé, gras si importante) :
  `.note-graphique { font-size: .875rem; line-height: 1.5; color: #0d366b; margin: .2rem 0 .6rem; } .note-graphique.forte { font-weight: 700; }`

### 8.14 Cartes géographiques (choroplèthes Plotly)

| Réglage | Valeur |
| --- | --- |
| Projection | `mercator`, fond `#ffffff`, `visible=False` (pas de fond de carte) |
| Cadrage | **explicite** : étendue (bbox) des contours ± 0,05°, pour `lonaxis_range` et `lataxis_range`. Ne pas utiliser `fitbounds`, qui laisse le Togo minuscule |
| Contours | blancs, 0.8 px |
| Hauteur | 560 px dans une colonne ; 620–640 px en pleine largeur ou sur la Synthèse ; 500–520 px pour la carte des 6 régions |
| Marges | `l=r=t=b=0` |
| Interaction | survol seulement : `displayModeBar: False`, `scrollZoom: False` |
| Légende | verticale, à droite (`x=1.0`) ; horizontale sous la carte pour la carte des régions |

Trois cartes types :

1. **Carte des priorités** (`carte_priorites`) :
   - classes haute, moyenne, faible et non classée dans la palette `PRIORITE`, chaque classe avec son effectif dans la légende (« Priorité haute (7) ») ;
   - territoires hors filtre en `#ebe8e0` ;
   - par-dessus, les communes où le mobile money est seul, en ocre `#eda100`, avec un contour noir de 0.7 px.
2. **Carte d'un indicateur** (`carte_valeur`) : échelle continue (`Blues`, ou `Oranges` pour le mobile money), ou classes avec des couleurs fixées.
3. **Carte des 6 régions** (`carte_regions`) :
   - 5 classes fixées à l'avance, dans la rampe `BLEUS` ; la légende montre toujours les 5 classes, même vides, pour comparer deux cartes côte à côte ;
   - la valeur est écrite sur chaque région, en blanc sur les deux classes les plus foncées ;
   - l'étiquette du Grand Lomé est placée sous la côte, reliée par un trait ;
   - les régions du filtre sont cerclées de noir (2.5 px).

### 8.15 Tableaux

| Type | Quand | Réglages |
| --- | --- | --- |
| `st.dataframe` | données triables | `hide_index=True`, `use_container_width=True` ; hauteur `35 × (lignes + 1) + 3` pour tout montrer, ou 280 à 520 px avec défilement |
| `st.table` | **des phrases** qui doivent revenir à la ligne | statique, index = première colonne |

**Mise en forme** :
- la colonne des régions est écrite en couleur, une couleur par région, en graisse 600 (`Styler.map`) ;
- nombres au format de la langue : séparateur de milliers, virgule décimale en français ;
- une colonne d'années ne prend jamais de séparateur (« 2030 », pas « 2 030 ») ;
- au plus 2 décimales, et seulement le nombre de décimales nécessaire ;
- Streamlit n'affiche pas de HTML dans une cellule de `st.dataframe`. Le comparateur de la page Priorités utilise donc un petit `<table>` HTML (0.92rem, valeurs alignées à droite).

### 8.16 Bouton d'export

`st.download_button("Exporter (CSV)", csv_utf8, file_name=…, mime="text/csv", icon=":material/download:")`, sous chaque bloc. L'export suit les filtres actifs et la langue choisie. **Chaque page a au moins un bloc exportable.**

### 8.17 Contrôles dans le contenu

| Widget | Usage |
| --- | --- |
| `st.segmented_control` | choix exclusif court : type d'établissement, maille, thème |
| `st.selectbox` | choisir un territoire, un pays ou un indicateur |
| `st.multiselect` (texte indicatif « Tous ») | filtres de la page Recommandations, scénarios affichés |
| `st.slider` | seuils déplaçables, poids du score (0 à 1, pas de 0.05, défaut 1/3) |
| `st.toggle` | basculer vers une variante (« Sans la couverture théorique », règle de statut) |

La référence reste toujours visible :
- quand un curseur (seuils, poids) quitte sa valeur de référence, une note s'affiche sous lui : « Vous regardez une variante : la référence est … », suivie du nombre de territoires qui changent de classe ;
- un interrupteur porte la variante dans son libellé (« Variante : … »), et son aide (`help=`, l'icône ⓘ) décrit la règle de référence.

---

## 9. Les 11 pages

### 9.1 Menu

| Groupe | Page (menu) | Icône Material | URL | Question (titre de la page) | Onglets |
| --- | --- | --- | --- | --- | --- |
| Principal | Synthèse nationale | `home` | `/` (défaut) | Le numérique et l'inclusion financière au Togo : où en est-on ? | — |
| Analyses | Usage d'Internet | `wifi` | `internet` | L'usage progresse-t-il, et à quel prix ? | 4 |
| | Marché des télécoms | `cell_tower` | `marche` | Qui tient le marché, et investit-il encore ? | 5 |
| | Offre financière | `account_balance` | `offre` | Où sont les établissements financiers ? | 4 |
| | Population et offre | `groups` | `population` | Combien d'habitants par point, et où le mobile money est-il seul ? | 4 |
| | Carte | `map` | `carte` | Que voit-on, commune par commune ? | — |
| Pilotage | Priorités | `flag` | `priorites` | Par quels territoires commencer ? | 4 |
| | Diagnostic | `troubleshoot` | `diagnostic` | Pourquoi ces territoires ? | 3 |
| | Recommandations | `task_alt` | `recommandations` | Quelle action engager ? | 4 |
| | Estimations et projections | `trending_up` | `projections` | Où va le Togo si l'on agit, et si rien ne change ? | — |
| Méthodologie | Sources et méthode | `menu_book` | `methodologie` | Sources, conventions et limites | — |

Les noms anglais des groupes sont Main, Analysis, Action et Methodology.

### 9.2 Disposition page par page

Notation : `[a, b]` = rapport de largeur des colonnes (`st.columns([a, b], gap="large")`) ; les nombres en px sont des hauteurs de graphique ou de carte.

**1. Synthèse nationale** (sans onglets)
- En-tête, puis le bandeau des filtres actifs, seulement si un filtre est posé.
- KPI, rangée 1 « Internet et marché des télécommunications (national) » : Internet · Haut débit mobile · Marché des télécoms · Prix de la data.
- KPI, rangée 2 « Inclusion financière et territoires » : Mobile money · Agences financières · Mobile money et agences · Réseau et mobile money. Cette rangée suit les filtres.
- `[1.12, 1]` :
  - à gauche, bloc « Où sont les territoires prioritaires ? », avec la carte des priorités (640 px, maille selon le filtre) et l'export ;
  - à droite, Constat, puis le bloc « Pourquoi ces écarts ? » (liste numérotée de 3), puis le bloc « Quelle action engager d'abord ? » (3 actions et un lien `st.page_link` vers les Recommandations).
- Synthèse chiffrée, limite discrète « Ce que cette page ne montre pas », pied.

**2. Usage d'Internet** — onglets : Vue synthèse · Évolution de l'usage · Accès et freins par région · Le Togo dans l'UEMOA
- Sous l'en-tête : bandeau « Chiffres nationaux : ils ne changent pas avec les filtres… ».
- **Vue synthèse** :
  - KPI ×4 ;
  - `[1.5, 1]` : courbe de l'usage depuis 1996 (420 px ; accélérations et ralentissements en points, cercle vide si la classe dépend de la période) / Constat et bloc « Accélération ou stagnation ? » ;
  - Synthèse ; Limite.
- **Évolution** : Constat ; `2 colonnes` : croissance annuelle (360) / enquêtes auprès des ménages (330) ; `2 colonnes` : abonnements data mobile (330) / abonnements par utilisateur (330) ; Limite.
- **Régions** : Constat ; `[2, 1]` : 2 cartes des régions (500, côte à côte) / alphabétisation et compétences (carte des régions, 500) ; tableau des freins par région ; Limite.
- **UEMOA** : Constat ; `[1.6, 1]` : courbes des 8 pays (440), avec une liste « Pays à mettre en évidence » / rang du Togo (240) et tableau des rangs ; Limite.

**2 bis. Marché des télécoms** — onglets : Vue synthèse · Parts de marché · Chiffre d'affaires et investissement · Technologies et fibre · Prix et couverture
- **Vue synthèse** : KPI ×4 ; Constat ; Synthèse ; Limite.
- **Parts de marché** : Constat ; `[1.5, 1]` : part de l'opérateur dominant selon trois mesures (400) / tableau de l'indice de concentration ; Limite.
- **Chiffre d'affaires** : Constat ; `2 colonnes` (380 / 380) ; `[1.5, 1]` (280) ; rangée KPI « revenu par abonnement » ; Limite.
- **Technologies et fibre** : `[1.6, 1]` (380) ; Constat ; `[1.6, 1]` : graphique (400) / carte des communes sans fibre recensée (460) et tableau des préfectures ; Limite.
- **Prix et couverture** : Constat ; `2 colonnes` : prix de la data (380) / couverture théorique et réception déclarée par région (380) ; Limite.

**3. Offre financière** — onglets : Vue synthèse · Établissements financiers · Réseau mobile money · Usage et coût du mobile money
- **Vue synthèse** : KPI ×4 ; Constat ; Synthèse ; Limite.
- **Établissements** :
  - Constat ;
  - `[1.15, 1]` : sélecteur « Type d'établissement » (segments) et carte (560) ;
  - distributeurs par région (300) ; villes et campagnes (330) ; par région (360), avec son tableau ; tableau par préfecture et par type (320) ;
  - Limite.
- **Réseau mobile money** : Constat ; `2 colonnes` : points mobile money (carte 560) / opérateurs (carte 560) ; répartition par région (340) ; Limite.
- **Usage et coût** :
  - Constat ; KPI ×4 « (national) » ;
  - `2 colonnes` (340 / 340) ;
  - bloc `[1, 1.3]` : carte des régions (500) / tableau ;
  - bloc « Ce que coûte un retrait » `[1.2, 1]` (320) ;
  - Limite.

**4. Population et offre** — onglets : Vue synthèse · Habitants par point de service · Agents par agence et mobile money seul · Statut et couverture
- **Vue synthèse** : KPI ×4 « (national) » ; Constat ; Synthèse ; Limite.
- **Habitants par point** : Constat ; `2 colonnes` : carte « habitants par agence » (560), avec un **curseur de seuils** (référence 10 000 et 30 000) et une note « variante » / carte « habitants par point mobile money » (560) ; tableau de densité ; Limite.
- **Agents par agence** : Constat ; `[1.15, 1]` : carte (560) / points loin d'une agence, par région (380) ; tableau ; Limite.
- **Statut et couverture** :
  - Constat ;
  - `[0.85, 1.15]` : carte du statut (560), avec un **interrupteur « Variante »** / tableau ;
  - matrice statut × couverture ; communes qui ne sont pas dans la classe de leur préfecture (280) ;
  - Limite.

**5. Carte** (sans onglets) — un explorateur
- `[2, 1]` : liste déroulante « Indicateur » / segments « Maille » (Commune, Préfecture ; Préfecture seule pour la priorité).
- Bloc avec la carte (620) et l'export de l'indicateur affiché.
- **La limite change avec l'indicateur.**
- Indicateurs : habitants par agence, habitants par point mobile money, couverture théorique, fibre enterrée et fibre aérienne recensées, agents par agence, statut d'accès, catégorie dominante d'opérateur, quotient de localisation, distance à l'agence, classe de priorité.

**6. Priorités** — onglets : Vue synthèse · Classement · Poids et robustesse · Comparateur
- Sous l'en-tête, sur toutes les vues, un bandeau Limite : « Le classement porte sur l'accès aux agences, au mobile money et au réseau… pas sur l'usage d'Internet. »
- **Vue synthèse** : KPI ×4 ; Constat ; `[0.85, 1.15]` : carte (560), avec l'interrupteur « Sans la couverture théorique » / tableau ; Limite.
- **Classement** : Constat ; « Ce qui place les priorités hautes en tête » (380) : une ligne par préfecture, un point par mesure (position de 0 à 100), un losange pour le score, seuil de 70 en pointillé ; tableau des 39 préfectures (520) ; Limite.
- **Poids et robustesse** :
  - Constat ;
  - `[0.85, 1.15]` : bloc « Changer les poids » avec 3 curseurs côte à côte (poids normalisés à 1) et la carte recalculée (540) / répartition des classes ;
  - tests de robustesse ; Limite.
  - Formule : score = Σ poids × position percentile ; classes : < 40 faible, 40–70 moyenne, > 70 haute.
- **Comparateur** : 2 listes « Préfecture A / B » ; tableau face à face (classe, 3 mesures, score, confiance, habitants) ; un « — » quand la donnée est inconnue ; Limite.

**7. Diagnostic** — onglets : Vue d'ensemble · Fiche de préfecture · Communes signalées
- **Vue d'ensemble** :
  - KPI ×4 ; Constat ;
  - « Carte d'identité des 10 préfectures » (560) ;
  - blocs « Ce qui se répète » (tableau), « Nature du manque et leviers », « Usage d'Internet par région » (tableau coloré) ;
  - Limite.
- **Fiche** : liste « Préfecture » ; Constat (la phrase de diagnostic) ; tableau des communes ; Limite.
- **Communes signalées** : Constat ; `[0.9, 1.1]` : carte (560) / liste (520) ; Limite.

**8. Recommandations** — onglets : Les 12 actions · Par thème · Par territoire · Ordre d'action et acteurs
- **Les 12 actions** :
  - 3 filtres en ligne (Thème, Nature, Horizon) ;
  - barre de résumé (`.filtres-actifs`) et légende « jamais d'addition d'habitants » ;
  - **grille de cartes de recommandation sur 3 colonnes** (8.11) ;
  - export ; Limite.
- **Par thème** : segments « Thème » ; Constat ; tableaux ; Limite.
- **Par territoire** : liste « Préfecture » ; Constat ; tableau des actions qui la concernent ; Limite.
- **Ordre et acteurs** : bloc « Ordre d'action » ; `[0.8, 1.2]` : carte des priorités (560) / « Qui agit ? » ; « Ce qui n'est pas recommandé » ; Limite.

**9. Estimations et projections** (sans onglets)
- KPI ×3 « Aujourd'hui, au rythme actuel, cible ».
- Bloc « Où va-t-on si rien ne change ? » : tableau statique de phrases.
- `[1.2, 1]` :
  - à gauche, scénarios d'usage à 2030 (380), avec la liste « Scénarios affichés », des lignes de seuil à 40 et 60 %, et un tableau ;
  - à droite, Constat et trajectoires de référence (barres groupées, 260).
- Bloc « Suivi des cibles » ; Limite ; pied.
- Les prolongements sont présentés comme des ordres de grandeur, jamais comme des prévisions.

**10. Sources et méthode** (sans onglets) — la seule page où apparaissent codes et sources
- Six blocs, chacun dans un cadre à bordure :
  - Les données du défi (`st.table`) ;
  - Sources institutionnelles externes : leur rôle ;
  - Conventions ;
  - Les 27 indicateurs (`st.dataframe` 420 et export) ;
  - Glossaire des codes ;
  - Crédits (dont l'auteur des armoiries, CC BY-SA 4.0).
- Pied.

---

## 10. État, filtres et interactions

| Clé de `st.session_state` | Rôle |
| --- | --- |
| `lang` | `"fr"` (défaut) ou `"en"` |
| `f_regions`, `f_maille`, `f_priorites`, `f_milieux` | filtres globaux, initialisés par `setdefault`, **conservés d'une page à l'autre** |
| `<page>_onglets_rang` | rang de l'onglet ouvert, par page |
| `poids_d1/d2/d3`, `cmp_a/b`, `reco_theme/nature/horizon`, `carte_indicateur`… | contrôles propres à une page |
| `pages` | références `st.Page` pour les liens internes (`st.page_link`) |

**Portée des filtres** :
- les chiffres nationaux (Internet, marché, prix, comptes) ne bougent pas avec les filtres, et un bandeau le dit ;
- les chiffres territoriaux, les cartes et les tableaux suivent les filtres ;
- sur une carte, les territoires hors sélection passent en gris clair, sans disparaître ;
- sur la carte des régions, les régions filtrées sont cerclées de noir.

**Prévu par le plan mais absent du code actuel** (à décider avant la réécriture) :
- filtre par préfecture ;
- maille « région » dans le filtre global ;
- recherche globale ;
- lien « page suivante » sur chaque page (la clé de traduction `ariane.suivant` existe, mais n'est pas utilisée).

---

## 11. Deux langues et format des nombres

- **Trois fonctions** :
  - `t(cle)` : textes communs (barres, pied, menu, classes, statuts) ;
  - `bi(fr, en)` : texte propre à une page, écrit deux fois sur place ;
  - `valeur(v)` : traduit en clair une valeur venue d'une table (« priorité 1 » → « priorité haute » / « high priority »).
- **Noms de lieux** non traduits, sauf « Maritime hors Grand Lomé » → « Maritime excluding Greater Lomé ».
- **Nombres** :

| | Français | Anglais |
| --- | --- | --- |
| Pourcentage | `39,5 %` (espace insécable avant %) | `39.5%` |
| Milliers | `759 599` (espace insécable) | `759,599` |
| Années | `2030` | `2030` |
| Plotly | `separators=", "` | `separators=".,"` |

- **Changement de langue** : `st.rerun()` ; l'onglet ouvert et les filtres sont conservés.
- **Exports CSV** dans la langue choisie.

---

## 12. Pièges connus de Streamlit (1.61)

| Piège | Conséquence | Parade |
| --- | --- | --- |
| Un dossier nommé `pages/` | Streamlit bascule sur son ancienne navigation et ignore `st.navigation` | nommer le dossier `views/` |
| `showSidebarNavigation = false` | masque aussi le menu | ne pas l'utiliser |
| Onglets en 1.61 | construits avec React Aria, plus avec BaseWeb | viser `[role="tablist"]`, `[data-testid="stTab"]`, `.react-aria-SelectionIndicator` |
| `st.container(key="x")` | rendu avec la classe `.st-key-x` | c'est ce qui permet de styler la barre du haut et les cartes de recommandation |
| Une carte KPI par `st.markdown` | chaque carte dans son propre bloc, la grille casse | une rangée = une seule chaîne HTML |
| HTML dans `st.dataframe` | non rendu | `Styler` pour la couleur ; `<table>` HTML si besoin |
| Plotly `fitbounds` | le Togo apparaît minuscule | cadrage lon/lat explicite |
| `AppTest` | ne rejoue pas le point d'entrée au changement de page ; échoue sur un `selectbox` à `format_func` rejoué | tests par page ; libellés directs dans les listes |
| Images dans le HTML | chemin `app/static/<fichier>` | `enableStaticServing = true` |
| En-tête de Streamlit (`stHeader`) | transparent en local et sur Heroku avec la barre latérale ouverte ; opaque, sur environ 60 px, sur Streamlit Cloud (boutons Fork et GitHub) ou avec la barre latérale fermée : le haut de la barre du haut est caché | ne pas masquer l'en-tête ; réserver sa hauteur seulement quand il contient `stToolbar` (section 4, « Contrainte : l'en-tête de Streamlit selon l'hébergement ») |
| `toolbarMode = "minimal"` | ne retire pas les boutons ajoutés par l'hébergeur | dépôt privé, ou CSS sur `stToolbarActions` (non pris en charge par Streamlit) |

---

## 13. Recette : liste de contrôle

- [ ] Les 11 pages et tous leurs onglets s'ouvrent sans erreur, en français et en anglais (référence : [tests/test_pages.py](../tests/test_pages.py)).
- [ ] Aucun sigle, code interne ni nom de source hors de la page Sources et méthode.
- [ ] La barre du haut et le pied de page sont identiques sur chaque page ; le bouton de langue actif est plein.
- [ ] La barre du haut est entièrement visible et ses boutons FR/EN sont cliquables, sur **chaque hébergement visé** (local ou Docker, Heroku, Streamlit Community Cloud), **barre latérale ouverte puis fermée**.
- [ ] Une fois fermée, la barre latérale se rouvre par le bouton de l'en-tête.
- [ ] Le lien actif du menu est cerclé de jaune clair ; les titres des filtres sont en majuscules jaunes.
- [ ] Dans une rangée de chiffres clés, toutes les cartes ont la même hauteur et les valeurs sont alignées ; la rangée passe à la ligne sur un écran étroit.
- [ ] Chaque carte de chiffre clé suit l'ordre libellé → valeur → phrase → contexte → réserve.
- [ ] Chaque onglet se termine par un bandeau Limite ; chaque page par le pied.
- [ ] Chaque page a au moins un bouton « Exporter (CSV) ».
- [ ] L'onglet ouvert est conservé au changement de langue et au retour sur la page.
- [ ] Un curseur déplacé affiche « Vous regardez une variante : la référence est … » ; un interrupteur de variante dit la règle de référence dans son aide.
- [ ] Les nombres suivent la langue ; une année n'a jamais de séparateur de milliers.
- [ ] Animations désactivées quand le système demande moins de mouvement (`prefers-reduced-motion`).

**Limite connue** : aucune règle n'est prévue pour les téléphones. La Synthèse chiffrée garde sa colonne de 280 px, et la barre du haut garde ses 3 colonnes. Ajouter des règles `@media (max-width: …)` si un usage mobile est visé.
