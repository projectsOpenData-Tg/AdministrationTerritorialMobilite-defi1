"""Style et chargements communs aux notebooks de l'étape 04.

Les notebooks visualisent ; ils ne produisent aucun chiffre cité dans le 04 (R-19) : ces chiffres
viennent des CSV écrits par les scripts (data/analysis/04_understanding/, data/interim/).
Palette : instance de référence du guide de visualisation, validée (adjacent, clair) pour 4 séries
et (toutes paires) pour 3 ; le vert d'eau et le jaune sont sous 3:1 sur le fond, d'où des étiquettes
directes et un tableau à côté de chaque graphique.
"""
from pathlib import Path

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
INTERIM = RACINE / "data" / "interim"
ANALYSE = RACINE / "data" / "analysis" / "04_understanding"

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # ordre fixe, jamais recyclé
SURFACE, ENCRE, ENCRE_2, MUET = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRILLE, AXE, NEUTRE = "#e1e0d9", "#c3c2b7", "#c3c2b7"
UTM31N = 32631
HALO = [pe.withStroke(linewidth=3, foreground=SURFACE)]  # lisibilité des noms posés sur une carte


def appliquer_style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXE, "axes.linewidth": 0.8, "axes.grid": True, "grid.color": GRILLE, "grid.linewidth": 0.6,
        "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": ENCRE_2, "xtick.color": MUET, "ytick.color": MUET, "text.color": ENCRE,
        "axes.titlecolor": ENCRE, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "font.family": "sans-serif", "font.size": 10, "lines.linewidth": 2, "legend.frameon": False,
        "figure.dpi": 110,
    })


def axe_annees(ax):
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))


def etiquettes_fin(ax, x, valeurs, ecart=0.05):
    """Étiquettes directes au bout des lignes, en encre secondaire, écartées d'au moins `ecart` de la hauteur
    de l'axe pour ne pas se chevaucher. À appeler après avoir fixé les limites de l'axe."""
    y0, y1 = ax.get_ylim()
    pas, places = ecart * (y1 - y0), []
    for texte, y in sorted(valeurs.items(), key=lambda kv: kv[1]):
        y = max(y, places[-1] + pas) if places else y
        places.append(y)
        ax.annotate(texte, (x, y), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=ENCRE_2)


def faisabilite(objectif):
    d = pd.read_csv(ANALYSE / "faisabilite_indicateurs.csv", keep_default_na=False)
    colonnes = ["ID", "Indicateur", "Prévu (03)", "Résultat (04)", "Maille obtenue", "Période", "Preuve (04)", "Réserve"]
    return d[d["Objectif"] == objectif][colonnes].set_index("ID")


def portail(fichier):
    df = pd.read_csv(BRUT / fichier, dtype=str)
    df["Value"], df["Date"] = pd.to_numeric(df["Value"]), pd.to_numeric(df["Date"])
    return df


def annuaire(numero):
    a = pd.read_csv(INTERIM / "annuaire2024_tableaux.csv")
    return a[a["Tableau"].astype(str) == numero]
