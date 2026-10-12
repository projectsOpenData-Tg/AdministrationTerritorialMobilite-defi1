"""Style et chargements communs aux notebooks de l'étape 06.

Les notebooks montrent ; ils ne produisent aucun chiffre cité dans le 06 (R-19) : ces chiffres viennent
des CSV écrits par scripts/exploration_06.py (data/analysis/06_exploration/) et des tables du 05.
Palette : celle du 04 (style_04.py), prolongée aux six premiers emplacements de l'instance de référence,
dans le même ordre ; validée (adjacent, clair) : contraste sous 3:1 pour l'aqua, le jaune et le magenta,
d'où des étiquettes directes et un tableau à côté de chaque graphique. Un nuage ou une carte ne porte
pas plus de trois couleurs : au-delà, un panneau par catégorie.
Cartes : classes = quartiles des 39 préfectures (06 §4), jamais les terciles du 02 (seuils, appliqués au 08).
"""
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from style_04 import (AXE, ENCRE, ENCRE_2, GRILLE, HALO, MUET, SURFACE, UTM31N, appliquer_style,  # noqa: F401,E402
                      axe_annees, etiquettes_fin)

RACINE = Path(__file__).resolve().parent.parent
TRAITE = RACINE / "data" / "processed"
REFERENCE = RACINE / "data" / "reference"
ANALYSE = RACINE / "data" / "analysis" / "06_exploration"

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]  # ordre fixe, jamais recyclé
SEQUENTIEL = ["#b7d3f6", "#6da7ec", "#2a78d6", "#184f95"]  # bleu, pas 150, 300, 450, 600 : du quart bas au quart haut
NON_DEFINI = "#e1e0d9"
# États du réseau : bon, moyen, mauvais sur la rampe bleue (plus d'encre = plus dégradé) ; travaux à part ; non évalué en gris
ETAT_COULEURS = {"Bon": "#6da7ec", "Moyen": "#2a78d6", "Mauvais": "#184f95", "Travaux": "#eb6834", "Non évalué": NON_DEFINI}
CLASSES = ["≤ Q1 (quart bas)", "Q1 – médiane", "médiane – Q3", "≥ Q3 (quart haut)"]
ZONES = ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]


def lire(nom):
    return pd.read_csv(TRAITE / f"{nom}.csv")


def exploration(nom):
    return pd.read_csv(ANALYSE / f"{nom}_06.csv", low_memory=False)


def rapport(nom, maille="National"):
    r = exploration("rapports").fillna({"Catégorie": ""})
    return r[(r["Rapport"] == nom) & (r["Maille"] == maille)]


def serie(nom):
    """Rapport national annuel, en tableau Année × Catégorie."""
    r = rapport(nom)
    r = r[r["Année"].astype(str).str.fullmatch(r"\d{4}")].assign(Année=lambda d: d["Année"].astype(int))
    return r.pivot(index="Année", columns="Catégorie", values="Valeur")


def signaux(*regles, objectif=None):
    s = exploration("signaux")
    if objectif:
        s = s[s["Objectif"] == objectif]
    if regles:
        s = s[s["Règle"].str.startswith(regles)]
    return s[["ID", "Résumé", "Niveau", "Question transmise"]].set_index("ID")


def distribution(variable):
    d = exploration("distributions")
    return d[d["Variable"] == variable].iloc[0]


def annees_atypiques(variable):
    """Années hors des bornes de Tukey d'une série (06 §4), lues dans distributions_06.csv."""
    v = distribution(variable)["Valeurs atypiques"]
    return [] if pd.isna(v) else [int(x.split(" ")[0]) for x in v.split(" ; ")]


def prefectures_geo():
    g = gpd.read_file(TRAITE / "geo" / "prefectures.geojson").to_crs(UTM31N)[["Préfecture", "geometry"]]
    return g.merge(exploration("prefectures"), on="Préfecture")


def classe(valeur, d):
    """Classe de quartile, comme les positions du 06 §4 (ex aequo compris)."""
    if pd.isna(valeur):
        return "non défini"
    if valeur <= d["Q1"] and valeur < d["Q3"]:
        return CLASSES[0]
    if valeur >= d["Q3"] and valeur > d["Q1"]:
        return CLASSES[3]
    return CLASSES[1] if valeur <= d["Médiane"] else CLASSES[2]


def nettoyer(ax):
    """Carte : ni graduations, ni libellés d'axes, ni cadre."""
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel(""); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)


def choroplethe(g, variable, titre, source, zero=None, ax=None, encart=True):
    """Carte en quartiles ; non défini en gris ; `zero` : libellé des zéros mesurés, hachurés."""
    d = distribution(variable)
    g = g.assign(_classe=[classe(v, d) for v in g[variable]])
    couleurs = dict(zip(CLASSES, SEQUENTIEL)) | {"non défini": NON_DEFINI}
    if ax is None:
        fig, ax = plt.subplots(figsize=(8.8, 8.4))
    else:
        fig = ax.figure
    axes = [ax]
    if encart:
        gl = g[g["Zone"] == "Grand Lomé"].total_bounds
        ins = ax.inset_axes([1.02, 0.0, 0.6, 0.34])
        ins.set_xlim(gl[0] - 2000, gl[2] + 2000); ins.set_ylim(gl[1] - 2000, gl[3] + 2000)
        ins.set_title("Grand Lomé", fontsize=8, loc="left", fontweight="normal")
        axes.append(ins)
    for a in axes:
        g.plot(ax=a, color=g["_classe"].map(couleurs), edgecolor=SURFACE, linewidth=0.8)
        if zero is not None:
            g[g[variable] == 0].plot(ax=a, facecolor="none", edgecolor=ENCRE_2, hatch="////", linewidth=0)
        nettoyer(a)
        if a is not ax:
            for s in a.spines.values():
                s.set_visible(True); s.set_color(AXE)
    ax.set_aspect("equal")
    poignees = [Patch(facecolor=couleurs[c], label=f"{c}") for c in CLASSES]
    if g["_classe"].eq("non défini").any():
        poignees.append(Patch(facecolor=NON_DEFINI, label="non défini"))
    if zero is not None:
        poignees.append(Patch(facecolor="none", edgecolor=ENCRE_2, hatch="////", label=zero))
    ax.legend(handles=poignees, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8,
              title=f"Q1 {round(d['Q1'], 2):g} · médiane {round(d['Médiane'], 2):g} · Q3 {round(d['Q3'], 2):g}".replace(".", ","),
              title_fontsize=8)
    ax.set_title(titre)
    fig.text(0.02, 0.01, source, fontsize=8, color=MUET)
    return fig, ax, g


def pied(fig, texte):
    fig.text(0.01, -0.02, texte, fontsize=8, color=MUET)
