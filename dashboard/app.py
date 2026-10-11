"""Tableau de bord — mobilité et sécurité routière au Togo (Défi 1).

Restitue les résultats du projet (documents 06 à 10 et annexe Horizon 2031) selon le plan du tableau de bord
(11_tableau_de_bord.md) : 8 pages en 4 groupes de menu, filtres globaux dans la barre latérale, gabarit commun,
barre du haut et pied de page identiques. Français seul (bilingue abandonné). Le tableau de bord affiche, il ne
calcule pas (11 §2) : chaque chiffre vient d'une table déjà produite.

Lancement, depuis la racine du projet :  streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

import streamlit as st

ICI = Path(__file__).resolve().parent
if str(ICI) not in sys.path:
    sys.path.insert(0, str(ICI))

import i18n  # noqa: E402
from composants import pied_barre_laterale, topbar  # noqa: E402
from donnees import ZONES  # noqa: E402
from theme import appliquer_theme  # noqa: E402

st.set_page_config(page_title="Mobilité et sécurité routière au Togo", page_icon=":material/directions_car:",
                   layout="wide", initial_sidebar_state="expanded")
appliquer_theme()
# Traduction : tout ce que Streamlit affiche passe par i18n.bi() ; sélecteur de langue sous le logo de la barre latérale
i18n.installer()
i18n.selecteur()
bi = i18n.bi
# Logo de la barre latérale (Togo en miniature et nom du tableau de bord), en face du bouton qui la replie ;
# silhouette seule quand la barre est repliée. Fichiers produits par scripts/logo_barre_laterale.py.
_logo = ICI / "static" / f"logo_barre_laterale_{i18n.langue()}.svg"
st.logo(str(_logo if _logo.exists() else ICI / "static" / "logo_barre_laterale.svg"), size="large",
        icon_image=str(ICI / "static" / "logo_togo_icone.svg"))
topbar()

# ----------------------------------------------------------------- Filtres globaux, conservés d'une page à l'autre
DEFAUTS = {"f_zones": [], "f_priorites": [], "f_leviers": []}
for k, v in DEFAUTS.items():
    st.session_state.setdefault(k, v)


def reinitialiser():
    for k, v in DEFAUTS.items():
        st.session_state[k] = v


PAGES = {
    bi("Principal"): [st.Page("views/vue_nationale.py", title=bi("Vue nationale"), icon=":material/home:", default=True)],
    bi("Analyses"): [
        st.Page("views/comparaison.py", title=bi("Comparaison territoriale"), icon=":material/bar_chart:", url_path="comparaison"),
        st.Page("views/evolutions.py", title=bi("Évolutions et constats"), icon=":material/timeline:", url_path="evolutions"),
        st.Page("views/carte.py", title=bi("Carte du réseau et des auto-écoles"), icon=":material/map:", url_path="carte"),
    ],
    bi("Pilotage"): [
        st.Page("views/priorites.py", title=bi("Priorités"), icon=":material/flag:", url_path="priorites"),
        PAGE_RECOS := st.Page("views/recommandations.py", title=bi("Recommandations"), icon=":material/task_alt:", url_path="recommandations"),
        PAGE_HORIZON := st.Page("views/horizon.py", title=bi("Horizon 2031"), icon=":material/trending_up:", url_path="horizon"),
    ],
    bi("Méthodologie"): [
        st.Page("views/methodologie.py", title=bi("Méthodologie"), icon=":material/menu_book:", url_path="methodologie"),
    ],
}

st.session_state["pages"] = {"recommandations": PAGE_RECOS, "horizon": PAGE_HORIZON}
navigation = st.navigation(PAGES)

PRIORITES = ["Haute", "Moyenne", "Aucune action"]
LEVIERS = ["Réseau", "Formation"]

with st.sidebar:
    st.divider()
    st.markdown("**Filtres**")
    st.pills("Zone", ZONES, selection_mode="multi", key="f_zones")
    st.pills("Priorité", PRIORITES, selection_mode="multi", key="f_priorites")
    st.pills("Levier", LEVIERS, selection_mode="multi", key="f_leviers")
    st.button("Réinitialiser les filtres", on_click=reinitialiser, use_container_width=True, icon=":material/restart_alt:")
    st.caption("39 préfectures · 6 zones · population 2022 · réseau relevé en 2020 · auto-écoles 2021-2022")
    pied_barre_laterale()

navigation.run()
