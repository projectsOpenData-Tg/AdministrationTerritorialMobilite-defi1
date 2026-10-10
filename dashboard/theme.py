"""Thème du tableau de bord : polices, couleurs et styles des composants partagés.

Palette reprise strictement du plan du tableau de bord (11 §4.1), elle-même validée pour les daltonismes : rampe bleue
pour les classes, couleurs de priorité, couleurs de thème des objectifs, couleurs d'état du réseau, couleur par zone.
Les couleurs de base (fond, cartes, barre latérale) sont dans .streamlit/config.toml. Structure et CSS repris du
tableau de bord du défi « Économie numérique » (EconomyNumeric-Challenge2/dashboard/theme.py), adaptés à notre palette
et au français seul.
"""
import streamlit as st

# --- Neutres et structure (maquette §2.2) -----------------------------------------------------------------
ENCRE, ENCRE2, DISCRET, FILET, FOND, CARTE = "#141413", "#3a3935", "#55534e", "#e2dfd6", "#f4f2ec", "#ffffff"
BLEU_FONCE = "#0d366b"

# --- Palettes de données (11 §4.1 ; ne pas changer) -------------------------------------------------------
BLEUS = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]            # rampe séquentielle, 5 classes
PRIORITE = {"Haute": "#0d366b", "Moyenne": "#3987e5", "Faible": "#cde2fb", "Non classée": "#b9b6ad"}
HORS_SELECTION = "#ebe8e0"
# Couleurs de thème des 4 objectifs (palette CATEGORIELLE de la maquette)
THEME = {"Mobilité": "#2a78d6", "Sécurité routière": "#eda100", "Réseau": "#eb6834", "Couverture": "#1baf7a"}
CATEGORIELLE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]  # séries d'un graphique
# États du réseau (11 §4.1 ; vérifiés pour les daltonismes)
ETAT = {"Bon": "#1baf7a", "Moyen": "#eda100", "Mauvais": "#e34948", "Travaux": "#2a78d6", "Non évalué": "#b9b6ad"}
# Une couleur par zone, pour écrire son nom (la couleur suit la zone, jamais son rang)
COULEUR_ZONE = {"Grand Lomé": "#256abf", "Maritime hors Grand Lomé": "#008300", "Plateaux": "#ab6300",
                "Centrale": "#4a3aa7", "Kara": "#cb4b0c", "Savanes": "#bb537d"}

# Les 5 régions, dans la même palette validée (11 §4.1) : la Maritime englobe le Grand Lomé et reprend sa couleur.
COULEUR_REGION = {"Maritime": "#256abf", "Plateaux": "#ab6300", "Centrale": "#4a3aa7",
                  "Kara": "#cb4b0c", "Savanes": "#bb537d"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, label { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
h1, h2, h3 { font-family: 'Fraunces', Georgia, serif !important; font-weight: 600 !important; letter-spacing: 0 !important; }

/* Contenu : largeur fluide, espacement latéral fixe (maquette §2.4) */
[data-testid="stMainBlockContainer"] { padding-top: 0.6rem; padding-bottom: 2rem; padding-left: 1.5rem !important;
  padding-right: 1.5rem !important; max-width: 100% !important; }
/* Streamlit place un en-tête opaque dès qu'il affiche un bouton (Fork/GitHub sur Streamlit Cloud, réouverture de la
   barre latérale) : on ne réserve sa hauteur que dans ce cas (maquette §4, règle à appliquer). */
body:has([data-testid="stHeader"] [data-testid="stToolbar"]) [data-testid="stMainBlockContainer"] { padding-top: 4.4rem; }

/* Barre latérale */
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span { font-size: 0.93rem; }
/* Logo (st.logo) : Togo en miniature et nom du tableau de bord, en face du bouton qui replie la barre */
[data-testid="stSidebarHeader"] { height: auto !important; min-height: 6.6rem; align-items: center; padding-top: 1rem !important; padding-bottom: 0.4rem !important; }
[data-testid="stSidebarHeader"] img { height: auto !important; width: 100% !important; max-width: 100% !important; max-height: 7rem; object-fit: contain; object-position: left center; }
[data-testid="stSidebarHeader"] > div:first-child { flex: 1 1 auto !important; min-width: 0; max-width: none !important; width: auto !important; margin-right: 0.6rem; }
/* Slogan et illustration de route, poussés en bas de la barre latérale quand la place le permet */
[data-testid="stSidebarContent"] { display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] { flex: 1 0 auto; display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] > div, [data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] { flex: 1 0 auto; display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.slogan-barre) { margin-top: auto; }
.slogan-barre { padding: 1.6rem 0 0; }
.slogan-texte { font-style: italic; font-size: 1.02rem; line-height: 1.5; color: #e7eef8; margin: 0 0 0.9rem; }
.slogan-filet { width: 1.6rem; height: 2px; background: #2ec4b6; border-radius: 2px; margin-bottom: 1.4rem; }
.slogan-illustration { display: block; width: 100%; height: auto; opacity: 0.95; }
[data-testid="stSidebar"] [data-testid="stNavSectionHeader"] { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.72rem; color: #9fb2c6; }
[data-testid="stSidebarNavLink"] { border: 1.5px solid transparent; border-radius: 8px; }
[data-testid="stSidebarNavLink"][aria-current="page"] { border-color: #fce588 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { text-transform: uppercase; letter-spacing: 0.07em; font-size: 0.74rem !important;
  font-weight: 700; color: #fce588 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { margin-top: 0.5rem; }
[data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"] { display: flex !important; visibility: visible !important; opacity: 1 !important; }
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"] { background: transparent !important; border: 1.5px solid #fce588 !important; border-radius: 8px !important; }
[data-testid="stSidebarCollapseButton"] button:hover, [data-testid="stExpandSidebarButton"]:hover { background: rgba(252,229,136,0.15) !important; }

/* En-tête de page */
.ariane { font-size: 0.85rem; color: #55534e; margin-bottom: 0.4rem; }
.ariane b { color: #141413; }
.surtitre { font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; color: #0d366b; font-weight: 600; }
.question { font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; font-weight: 600; line-height: 1.1; margin: 0.2rem 0 0.5rem; color: #141413; }
.reponse { font-size: 1.05rem; line-height: 1.5; color: #3a3935; max-width: 880px; margin-bottom: 0.6rem; }
.filtres-actifs { font-size: 0.85rem; color: #3a3935; background: #ffffff; border: 1px solid #e2dfd6; border-radius: 10px; padding: 8px 12px; margin-bottom: 0.6rem; }

/* Chiffres clés */
.groupe { font-size: 0.82rem; font-weight: 600; color: #55534e; margin: 0.6rem 0 0.4rem; }
.kpi-grille { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; margin-bottom: 6px; }
.kpi { background: #ffffff; border: 1px solid #e2dfd6; border-radius: 14px; padding: 16px 18px; display: flex; flex-direction: column; gap: 6px; box-sizing: border-box;
       position: relative; overflow: hidden; transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease; }
.kpi::after { content: ""; position: absolute; top: 0; left: -80%; width: 50%; height: 100%; pointer-events: none;
              background: linear-gradient(115deg, transparent, rgba(252,229,136,0.45), transparent); transform: skewX(-20deg); }
.kpi:hover { transform: translateY(-3px); border-color: #fce588; box-shadow: 0 0 0 3px rgba(252,229,136,0.35), 0 10px 24px rgba(13,54,107,0.12); }
.kpi:hover::after { left: 130%; transition: left 0.8s ease; }
@media (prefers-reduced-motion: reduce) { .kpi, .kpi:hover { transform: none; transition: none; } .kpi::after { display: none; } }
.kpi-tete { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; min-height: 2.5rem; }
.kpi-libelle { font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; line-height: 1.35; color: #0d366b; }
.kpi-valeur { font-family: 'Fraunces', Georgia, serif; font-size: 2.2rem; font-weight: 600; line-height: 1.1; color: #141413; }
.kpi-unite { font-family: 'IBM Plex Sans', system-ui, sans-serif; font-size: 1.05rem; font-weight: 600; margin-left: 6px; }
.kpi-phrase { font-size: 0.95rem; font-weight: 600; line-height: 1.4; color: #141413; }
.kpi-contexte { font-size: 0.84rem; line-height: 1.45; color: #3a3935; }
.kpi-reserve { font-size: 0.78rem; line-height: 1.4; color: #55534e; border-top: 1px solid #efece4; padding-top: 7px; margin-top: auto; }
.etiquette { font-size: 0.74rem; font-weight: 600; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }
.etiquette.alerte { background: #fdf0d2; color: #6b4700; }
.etiquette.ok { background: #e3eefb; color: #0d366b; }
.etiquette.critique { background: #fbe3e2; color: #8a1c1b; }
.etiquette.neutre { background: #efece4; color: #3a3935; }
.etiquette.national { background: #efece4; color: #55534e; font-weight: 500; }

/* Cartes de recommandation */
div[class*="st-key-carte_reco_"] { background: #ffffff; border: 1px solid #e2dfd6 !important; border-radius: 18px !important; padding: 18px 20px !important;
  box-shadow: 0 1px 6px rgba(13,54,107,0.06); transition: transform 0.25s ease, box-shadow 0.25s ease; }
div[class*="st-key-carte_reco_"]:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(13,54,107,0.14); }
@media (prefers-reduced-motion: reduce) { div[class*="st-key-carte_reco_"], div[class*="st-key-carte_reco_"]:hover { transform: none; transition: none; } }
.reco-theme { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.reco-pastille { width: 34px; height: 34px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.reco-theme-lib { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.reco-titre { font-family: 'Fraunces', Georgia, serif; font-size: 1.12rem; font-weight: 600; color: #141413; line-height: 1.3; margin: 2px 0 6px; }
.reco-cible { font-size: 0.92rem; color: #141413; line-height: 1.45; margin-bottom: 4px; }
.reco-contexte { font-size: 0.84rem; color: #55534e; margin-bottom: 8px; }
.reco-horizon2031 { font-size: 0.84rem; color: #0d366b; background: #e8f0fb; border-radius: 8px; padding: 6px 10px; margin: 6px 0; line-height: 1.4; }
.etiquette.reco-priorite { background: #fdf0d2; color: #6b4700; }
.etiquette.reco-nature { background: #ece9fb; color: #4a3aa7; }
.etiquette.reco-horizon { background: #e2f4ec; color: #11613f; }

/* Blocs, constat, synthèse, limite */
.bloc-titre { font-family: 'Fraunces', Georgia, serif; font-size: 1.3rem; font-weight: 600; color: #141413; margin-bottom: 0.2rem; }
.bloc-sous-titre { font-size: 0.86rem; color: #55534e; line-height: 1.45; margin-bottom: 0.4rem; }
.constat { background: #e8f0fb; border: 1px solid #c7d8f0; border-radius: 14px; padding: 16px 18px; margin-bottom: 14px; }
.constat-titre, .limite-titre, .synthese-titre { font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.constat-titre { color: #0d366b; }
.constat-texte { font-size: 0.95rem; line-height: 1.5; color: #141413; margin-top: 4px; }
.synthese { background: #ffffff; border: 1px solid #e2dfd6; border-radius: 14px; padding: 20px 24px; display: grid; grid-template-columns: 280px 1fr; gap: 26px; align-items: center; margin-top: 8px; }
.synthese-titre { color: #55534e; }
.synthese-chiffre { font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; font-weight: 600; color: #0d366b; line-height: 1.05; margin: 4px 0; }
.synthese-legende { font-size: 0.88rem; line-height: 1.45; }
.synthese ul { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 8px; font-size: 0.92rem; line-height: 1.5; }
.limite { background: #fdf3d7; border: 1px solid #ecd28f; border-radius: 14px; padding: 14px 18px; margin-top: 14px; }
.limite-titre { color: #6b4700; }
.limite-texte { font-size: 0.9rem; line-height: 1.5; color: #3a2a00; margin-top: 4px; }
.limite.discret { background: transparent; border: 0; border-top: 1px solid #e2dfd6; border-radius: 0; padding: 12px 0 0; margin-top: 18px; }
.limite.discret .limite-titre { color: #55534e; }
.limite.discret .limite-texte { font-size: 0.86rem; color: #55534e; }

/* Listes (étapes, écarts, actions) */
.etapes { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; }
.etape { display: grid; grid-template-columns: 54px 1fr; gap: 16px; padding: 14px 0; border-bottom: 1px solid #efece4; }
.etape:last-child { border-bottom: 0; }
.etape-num { width: 54px; height: 54px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
  font-family: 'Fraunces', Georgia, serif; font-size: 1.4rem; font-weight: 600; }
.etape-titre { font-size: 1rem; font-weight: 700; color: #141413; }
.etape-desc { font-size: 0.88rem; color: #55534e; line-height: 1.5; margin-top: 2px; }
.etape-sortie { font-size: 0.82rem; color: #0d366b; background: #f4f7fc; border-left: 3px solid #86b6ef; border-radius: 6px; padding: 7px 10px; margin-top: 6px; }

/* Pied de page */
.pied { font-size: 0.8rem; color: #55534e; margin-top: 18px; }
.pied-identite { background: #ffffff; border: 1px solid #e2dfd6; border-radius: 12px; padding: 16px 24px;
  margin-top: 20px; text-align: center; box-shadow: 0 1px 4px rgba(13,54,107,0.06); }
.pied-identite-titre { font-size: 0.92rem; font-weight: 800; color: #0d366b; line-height: 1.4; }
.pied-identite-sous-titre { font-size: 0.78rem; color: #55534e; margin-top: 4px; line-height: 1.5; }

/* Barre du haut (maquette §4) : armoiries + ministère · nom du projet + drapeau · carte logo Togo AI Lab */
.topbar-ligne { display: flex; align-items: center; gap: 10px; }
.armoiries { height: 38px; width: auto; flex-shrink: 0; }
.armoiries-repli { font-size: 1.4rem; flex-shrink: 0; }
.topbar-ministere { font-size: 0.76rem; color: #3a3935; line-height: 1.3; }
.topbar-centre { text-align: center; }
.topbar-titre { font-family: 'Fraunces', Georgia, serif; font-size: 1.2rem; font-weight: 600; color: #0d366b; }
.topbar-sous-titre { font-size: 0.76rem; color: #55534e; font-style: italic; margin-top: 1px; }
.ai-lab-logo-carte { display: inline-flex; align-items: center; justify-content: center; background: #ffffff;
  border: 2px solid #ffce00; border-radius: 12px; padding: 7px 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); height: 56px; }
.ai-lab-logo-carte img { height: 40px; width: auto; max-width: 140px; object-fit: contain; }
.ai-lab-logo-repli { font-size: 0.55rem; font-weight: 700; color: #dc2626; line-height: 1.2; text-align: center; }
[data-testid="stVerticalBlockBorderWrapper"]:has(div.st-key-topbar) { margin-bottom: 0.8rem; }
div.st-key-topbar { background: #ffffff; min-height: 92px; padding: 16px 22px; box-shadow: 0 1px 8px rgba(13,54,107,0.08);
  margin-bottom: 0.6rem; box-sizing: border-box; border: 1px solid #e2dfd6; border-radius: 18px; }
div.st-key-topbar [data-testid="stHorizontalBlock"] { align-items: center; }
div.st-key-topbar_droite { display: flex; align-items: center; justify-content: flex-end; }

/* Graphiques et cartes sur fond blanc */
[data-testid="stPlotlyChart"] { background: #ffffff; border-radius: 10px; }

/* Sous-onglets en pastilles */
.stTabs [role="tablist"] { gap: 4px; background: #ffffff; padding: 6px; border-radius: 12px; border: 1px solid #e2dfd6;
  box-shadow: 0 1px 4px rgba(13,54,107,0.06); flex-wrap: wrap; }
.stTabs [data-testid="stTab"] { border-radius: 8px; padding: 7px 15px; height: auto; margin: 0; flex: 1 1 auto; justify-content: center; text-align: center; }
.stTabs [data-testid="stTab"] p { font-size: 0.9rem; font-weight: 600; color: #55534e; }
.stTabs [data-testid="stTab"]:hover { background: #e8f0fb; }
.stTabs [data-testid="stTab"]:hover p { color: #0d366b; }
.stTabs [data-testid="stTab"][aria-selected="true"] { background: #0d366b !important; }
.stTabs [data-testid="stTab"][aria-selected="true"] p { color: #ffffff !important; }
.stTabs .react-aria-SelectionIndicator { display: none; }
.onglets-aide { font-size: 0.84rem; font-weight: 600; color: #3a3935; margin: 0.8rem 0 0.3rem; }
.onglets-repere { font-size: 0.82rem; font-style: italic; color: #55534e; margin: 0.1rem 0 0.4rem; }
.note-graphique { font-size: 0.875rem; line-height: 1.5; color: #0d366b; margin: 0.2rem 0 0.6rem; }
.note-graphique.forte { font-weight: 700; }
</style>
"""


def appliquer_theme():
    st.markdown(CSS, unsafe_allow_html=True)
