"""Composants partagés par toutes les pages : barre du haut, en-tête, chiffres clés, bandeaux, synthèse, cartes, export.

Gabarit commun (maquette §7) : barre du haut, en-tête sous forme de question, chiffres clés, visuel avec son constat,
synthèse chiffrée, limite de la page, pied de page. Français seul (bilingue abandonné, _CONSTRAINTS_DEV.txt). Structure
et CSS repris du tableau de bord du défi « Économie numérique », adaptés à notre palette et sans sélecteur de langue.
"""
import html
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from donnees import fr
from theme import BLEUS, COULEUR_ZONE, ENCRE, HORS_SELECTION

STATIQUE = Path(__file__).resolve().parent / "static"
EMBLEME = STATIQUE / "armoiries-togo-ecu.svg"
LOGO_AI_LAB = STATIQUE / "logo_togo_ai_lab.png"

MINISTERE = "Ministère de l'Efficacité du Service Public et de la Transformation Numérique"
MARQUE = "Mobilité et sécurité routière au Togo"
SOUS_TITRE = "Comprendre les risques, identifier les priorités d’action"
PIED_SOURCES = "Données : portail national de données ouvertes du Togo et sources institutionnelles complémentaires."
PIED_TITRE = "Togo AI Lab — Data Challenge | Administration territoriale et mobilité — Défi 1"
PIED_SOUS_TITRE = ("Diagnostic territorial et aide à la décision pour la mobilité, la sécurité routière et l'entretien "
                   "du réseau au Togo")


def topbar():
    """Barre du haut, en trois zones (maquette §4) : armoiries et ministère à gauche, nom du projet et drapeau au
    centre, carte du logo Togo AI Lab à droite. Sans sélecteur de langue (bilingue abandonné)."""
    with st.container(key="topbar"):
        gauche, centre, droite = st.columns([1.1, 1.3, 1], vertical_alignment="center")
        with gauche:
            embleme = (f'<img class="armoiries" src="app/static/{EMBLEME.name}" alt="">' if EMBLEME.exists()
                       else '<span class="armoiries-repli">🛡️</span>')
            st.markdown(f'<div class="topbar-ligne">{embleme}<div class="topbar-ministere">{html.escape(MINISTERE)}</div></div>',
                        unsafe_allow_html=True)
        with centre:
            st.markdown('<div class="topbar-centre">'
                        f'<div class="topbar-titre">🇹🇬 {html.escape(MARQUE)}</div>'
                        f'<div class="topbar-sous-titre">{html.escape(SOUS_TITRE)}</div></div>', unsafe_allow_html=True)
        with droite:
            with st.container(key="topbar_droite"):
                if LOGO_AI_LAB.exists():
                    logo = f'<img src="app/static/{LOGO_AI_LAB.name}" alt="Togo AI Lab">'
                else:
                    logo = '<div class="ai-lab-logo-repli">TOGO<br>AI LAB</div>'
                st.markdown(f'<div class="ai-lab-logo-carte">{logo}</div>', unsafe_allow_html=True)


SLOGAN = "Des routes plus sûres pour une mobilité durable au Togo"


def pied_barre_laterale():
    """Bas de la barre latérale : le slogan, puis l'illustration des montagnes et de la route (static/routes_slogan.svg).
    Le CSS (theme.py, .slogan-barre) le pousse en bas de la barre quand la place le permet."""
    st.markdown(f'<div class="slogan-barre"><p class="slogan-texte">“{html.escape(SLOGAN)}”</p>'
                '<div class="slogan-filet"></div>'
                '<img class="slogan-illustration" src="app/static/routes_slogan.svg" alt=""></div>',
                unsafe_allow_html=True)


def ariane(page: str):
    st.markdown(f'<div class="ariane">Tableau de bord › <b>{html.escape(page)}</b></div>', unsafe_allow_html=True)


def entete(surtitre: str, question: str, reponse_html: str, carte: bool = False):
    """En-tête de page ; `carte` présente la réponse dans une carte à fond blanc. Le surtitre n'est plus affiché : il
    doublait le fil d'Ariane (« Tableau de bord › page ») ; le paramètre reste pour ne pas changer les appels."""
    classe = "reponse en-carte" if carte else "reponse"
    st.markdown(f'<div class="question">{html.escape(question)}</div>'
                f'<div class="{classe}">{reponse_html}</div>', unsafe_allow_html=True)


def filtres_actifs(texte_html: str):
    st.markdown(f'<div class="filtres-actifs">{texte_html}</div>', unsafe_allow_html=True)


def _insecable(txt: str) -> str:
    return re.sub(r"(\d) (?=\d{3}\b)", "\\1\u00a0", txt.replace(" %", "\u00a0%"))


# Icônes des chiffres clés (tracés au trait, 24 × 24), avec la couleur de thème de l'objectif (11 §4.1)
ICONES = {
    "population": ('<circle cx="9" cy="7" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/>'
                   '<path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/>', "#1769aa"),
    "vehicule": ('<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3'
                 'c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/>'
                 '<circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>', "#16834a"),
    "tues": ('<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
             '<path d="M12 9v4"/><path d="M12 17h.01"/>', "#ce1126"),
    "blesses": ('<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2'
                'A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
                "#e6b422"),
    "route": ('<path d="M4 21 9 3"/><path d="M20 21 15 3"/><path d="M12 4v2"/><path d="M12 10v3"/><path d="M12 17v3"/>',
              "#64748b"),
    "ecole": ('<path d="M21.42 10.92a1 1 0 0 0-.02-1.84L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.83'
              'l8.57 3.91a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>', "#2474c6"),
}


def icone_kpi(nom: str) -> str:
    """Pastille arrondie portant l'icône du thème du chiffre clé, teintée de la couleur de ce thème."""
    trace, couleur = ICONES[nom]
    return (f'<span class="kpi-icone" style="background:{couleur}1f;color:{couleur};">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{trace}</svg></span>')


def carte_kpi(libelle: str, valeur: str, phrase: str, contexte: str = "", reserve: str = "", etiquette: str | None = None,
              ton: str = "neutre", unite: str = "", icone: str | None = None, periode: str = "",
              tendance: tuple[str, str, str] | None = None) -> str:
    """Chiffre clé (maquette §8.4) : la valeur se lit avec sa phrase ; la réserve, en bas, dit ce que le chiffre ne
    mesure pas (aucune si vide). `icone` (clé de ICONES) ajoute la pastille du thème à gauche du libellé ; `periode`
    s'écrit entre parenthèses sous le libellé ; `tendance` = (variation, référence, sens) s'affiche en badge sous la
    valeur, sens ∈ {"pire", "mieux", "neutre"}."""
    tag = f'<span class="etiquette {ton}">{html.escape(etiquette)}</span>' if etiquette else ""
    u = f'<span class="kpi-unite">{html.escape(unite)}</span>' if unite else ""
    ctx = f'<div class="kpi-contexte">{_insecable(contexte)}</div>' if contexte else ""
    res = f'<div class="kpi-reserve">{_insecable(html.escape(reserve))}</div>' if reserve else ""
    ico = icone_kpi(icone) if icone else ""
    per = f'<div class="kpi-periode">({html.escape(periode)})</div>' if periode else ""
    tend = ""
    if tendance:
        variation, reference, sens = tendance
        fleche = "↗" if variation.startswith("+") else "↘" if variation.startswith(("−", "-")) else "→"
        tend = (f'<span class="kpi-tendance {sens}">{fleche} {_insecable(html.escape(variation))} '
                f'<small>{html.escape(reference)}</small></span>')
    bas = f' style="border-bottom-color:{ICONES[icone][1]}"' if icone else ""   # liseré du bas, couleur du thème
    return (f'<div class="kpi"{bas}><div class="kpi-tete">{ico}<div class="kpi-libelle" lang="fr">{html.escape(libelle)}{per}</div>'
            f'{tag}</div><div class="kpi-centre">'
            f'<div class="kpi-valeur">{_insecable(html.escape(valeur))}{u}</div>{tend}'
            f'<div class="kpi-phrase">{_insecable(html.escape(phrase))}</div></div>{ctx}{res}</div>')


def rangee_kpi(groupe: str, cartes: list[str], une_ligne: bool = False):
    """Rangée de chiffres clés ; `une_ligne` les tient tous sur une seule ligne sur grand écran."""
    classe = "kpi-grille une-ligne" if une_ligne else "kpi-grille"
    st.markdown(f'<div class="groupe">{html.escape(groupe)}</div><div class="{classe}">{"".join(cartes)}</div>',
                unsafe_allow_html=True)


def constat(texte_html: str):
    st.markdown(f'<div class="constat"><div class="constat-titre">Constat</div>'
                f'<div class="constat-texte">{texte_html}</div></div>', unsafe_allow_html=True)


def synthese(chiffre: str, legende: str, puces_html: list[str]):
    puces = "".join(f"<li>{p}</li>" for p in puces_html)
    st.markdown(f'<div class="synthese"><div><div class="synthese-titre">Synthèse chiffrée</div>'
                f'<div class="synthese-chiffre">{chiffre}</div><div class="synthese-legende">{legende}</div></div>'
                f'<ul>{puces}</ul></div>', unsafe_allow_html=True)


def limite(texte: str, titre: str = "Limite de cette page", discret: bool = False):
    classe = "limite discret" if discret else "limite"
    st.markdown(f'<div class="{classe}"><div class="limite-titre">{html.escape(titre)}</div>'
                f'<div class="limite-texte">{html.escape(texte)}</div></div>', unsafe_allow_html=True)


def titre_bloc(titre: str, sous_titre: str | None = None, marge: bool = False):
    style = ' style="margin-top:1rem;"' if marge else ""
    sous = f'<div class="bloc-sous-titre">{html.escape(sous_titre)}</div>' if sous_titre else ""
    st.markdown(f'<div class="bloc-titre"{style}>{html.escape(titre)}</div>{sous}', unsafe_allow_html=True)


def note(texte: str, forte: bool = False):
    st.markdown(f'<div class="note-graphique{" forte" if forte else ""}">{html.escape(texte)}</div>', unsafe_allow_html=True)


def pied():
    st.markdown(f'<div class="pied">{html.escape(PIED_SOURCES)}</div>'
                f'<div class="pied-identite"><div class="pied-identite-titre">{html.escape(PIED_TITRE)}</div>'
                f'<div class="pied-identite-sous-titre">{html.escape(PIED_SOUS_TITRE)}</div></div>', unsafe_allow_html=True)


def badge(texte: str, couleur: str) -> str:
    """Pastille colorée. Le texte passe en blanc sur un fond sombre, en encre sur un fond clair."""
    clair = couleur in ("#eda100", "#b9b6ad", "#cde2fb", "#86b6ef", "#ebe8e0", "#efece4")
    return (f'<span style="display:inline-block;background:{couleur};'
            f'color:{"#141413" if clair else "#ffffff"};border-radius:999px;padding:1px 7px;'
            f'font-size:.69rem;font-weight:600;margin:1px 3px 1px 0;white-space:nowrap">'
            f'{html.escape(str(texte))}</span>')


def table_html(lignes: list[dict]) -> str:
    """Tableau HTML : les cellules portent déjà leur mise en forme (badges, chiffres colorés)."""
    cols = list(lignes[0])
    tete = "".join(f'<th style="text-align:left;padding:6px 6px;border-bottom:2px solid #e2dfd6;'
                   f'font-size:.70rem;text-transform:uppercase;letter-spacing:.02em;color:#55534e;'
                   f'line-height:1.2">{html.escape(c)}</th>' for c in cols)
    corps = ""
    for ligne in lignes:
        cellules = "".join(f'<td style="padding:6px 6px;border-bottom:1px solid #efece4;font-size:.82rem;'
                           f'vertical-align:middle">{ligne[c]}</td>' for c in cols)
        corps += f"<tr>{cellules}</tr>"
    return (f'<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;background:#fff;'
            f'border:1px solid #e2dfd6;border-radius:10px">'
            f"<thead><tr>{tete}</tr></thead><tbody>{corps}</tbody></table></div>")


def export_csv(df: pd.DataFrame, nom_fichier: str, cle: str, libelle: str = "Exporter (CSV)"):
    st.download_button(libelle, df.to_csv(index=False).encode("utf-8"), file_name=nom_fichier, mime="text/csv",
                       key=cle, icon=":material/download:")


def onglets(cle: str, libelles: list[str]) -> list:
    """Sous-onglets d'une page, en pastilles (maquette §8.10). L'onglet actif est gardé par son rang, pour survivre au
    passage par une autre page. Le repère « vue 2 sur 4 » est écrit en tête de l'onglet ouvert."""
    cle_rang = f"{cle}_rang"
    rang = min(st.session_state.get(cle_rang, 0), len(libelles) - 1)

    def _retenir():
        st.session_state[cle_rang] = libelles.index(st.session_state[cle])

    st.markdown(f'<div class="onglets-aide">{len(libelles)} vues — cliquez sur un onglet</div>', unsafe_allow_html=True)
    liste = st.tabs(libelles, default=libelles[rang], key=cle, on_change=_retenir)
    with liste[rang]:
        st.markdown(f'<div class="onglets-repere">{html.escape(libelles[rang])} · vue {rang + 1} sur {len(libelles)}</div>',
                    unsafe_allow_html=True)
    return liste


def habiller(fig: go.Figure, hauteur: int, suffixe_y: str = "", legende_y: float = 1.12, **kw) -> go.Figure:
    """Mise en forme commune des graphiques (maquette §8.13) : fond blanc, grille discrète, légende horizontale,
    séparateurs de milliers à la française."""
    reglages = dict(height=hauteur, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                    font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE, size=11),
                    legend=dict(orientation="h", y=legende_y, x=0), yaxis=dict(ticksuffix=suffixe_y, gridcolor="#efece4"),
                    xaxis=dict(gridcolor="#efece4"), hoverlabel=dict(bgcolor="#ffffff", font_size=12), separators=", ")
    reglages.update(kw)
    fig.update_layout(**reglages)
    return fig


def tracer(fig: go.Figure, cle: str):
    st.plotly_chart(fig, key=cle, config={"displayModeBar": False})


def fenetre_geo(fig, geo):
    """Fenêtre explicite lon/lat : le zoom automatique de Plotly laisse le Togo minuscule."""
    xs, ys = [], []
    for ft in geo["features"]:
        x0, y0, x1, y1 = ft["bbox"]
        xs += [x0, x1]
        ys += [y0, y1]
    fig.update_geos(visible=False, bgcolor="#ffffff", projection_type="mercator",
                    lonaxis_range=[min(xs) - 0.05, max(xs) + 0.05], lataxis_range=[min(ys) - 0.05, max(ys) + 0.05])


_fenetre = fenetre_geo


def choroplethe(geo: dict, df: pd.DataFrame, cle: str, colonne: str, titre_legende: str, hauteur: int = 600,
                categorique: bool = False, couleurs: dict | None = None, palette: str = "Blues",
                hover: dict | None = None, ordre: list | None = None):
    """Carte choroplèthe d'un indicateur, continu ou catégoriel. `df` porte `code` (= nom du territoire) et `colonne`."""
    hover_data = {"code": False, colonne: not categorique}
    if hover:
        hover_data.update(hover)
    kwargs = (dict(color_discrete_map=couleurs, category_orders={colonne: ordre} if ordre else None)
              if categorique else dict(color_continuous_scale=palette))
    fig = px.choropleth(df, geojson=geo, locations="code", featureidkey="properties.code", color=colonne,
                        hover_name="nom", hover_data=hover_data, labels={colonne: titre_legende}, **kwargs)
    fig.update_traces(marker_line_color="#ffffff", marker_line_width=0.8)
    _fenetre(fig, geo)
    fig.update_layout(height=hauteur, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#ffffff",
                      font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE),
                      hoverlabel=dict(bgcolor="#ffffff", font_size=12), coloraxis_colorbar=dict(title=""),
                      legend=dict(title="", x=1.0, xanchor="left", y=0.98))
    st.plotly_chart(fig, key=cle, config={"displayModeBar": False, "scrollZoom": False})


def couleur_zone(nom: str) -> str:
    return COULEUR_ZONE.get(nom, ENCRE)
