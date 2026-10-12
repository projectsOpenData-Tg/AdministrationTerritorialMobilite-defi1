"""Génère le rapport PowerPoint du Défi 1 — Mobilité et sécurité routière, écrit pour le décideur.

Plan : `tmp/ppt-plan.md`. Processus repris du défi « Économie numérique »
(`EconomyNumeric-Challenge2/scripts/build_presentation.py`) : un plan, un script, des contrôles. La relecture
« décideur » qui y avait fait réécrire les dix diapositives est appliquée ici dès la première version : chaque
diapositive dit ce qu'il faut décider, pas ce qui a été analysé.

⚠️ **Aucun chiffre n'est retapé** (R-19, comme le tableau de bord, 11 §2). Toutes les valeurs sont lues dans
`data/analysis/` et `data/processed/` par `dashboard/donnees.py`. Les constats qui nomment des territoires
(« les 5 préfectures qui cumulent », « ni le Golfe ni Agoè-Nyivé ») sont dérivés des tables, pour rester justes
si le pipeline est rejoué. Les couleurs viennent de `dashboard/theme.py` : le rapport et le tableau de bord ont
la même identité.

⚠️ **Règle des codes** (11 §4.2, `_CONSTRAINTS_DEV.txt`) : aucun code interne, aucun nom de fichier, aucun numéro
de document, aucun nom de source entre parenthèses sur les diapositives. « Auto-école agréée », jamais
« comptée » ; « accidents constatés », jamais « corporels ». La diapositive 2 est la seule à parler de méthode,
en clair ; le détail reste en page Méthodologie du tableau de bord.

Contraintes techniques : graphiques en matplotlib (l'export d'images Plotly exige Chrome) ; armoiries rasterisées
une fois (`python-pptx` ne lit pas le SVG) ; `python-pptx` n'est pas dans `.venv` mais dans le site utilisateur,
ajouté en fin de `sys.path` pour que les versions de `.venv` gardent la priorité — `.venv` n'est pas modifié.

Usage  : `.venv/bin/python scripts/build_presentation.py`
Sortie : `Togo-Mobilite-Securite-Routiere-Defi1.pptx`, à la racine du projet.
"""

from __future__ import annotations

import datetime
import logging
import site
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from PIL import Image, ImageFont  # noqa: E402

# python-pptx vit dans le site utilisateur : ajouté en fin de chemin, jamais devant (les versions de .venv priment).
try:
    import pptx  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - dépend du poste
    for _chemin in site.getusersitepackages() if isinstance(site.getusersitepackages(), list) \
            else [site.getusersitepackages()]:
        if _chemin not in sys.path:
            sys.path.append(_chemin)

from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "dashboard"))

from composants import MARQUE, MINISTERE, SLOGAN, SOUS_TITRE  # noqa: E402
from donnees import ZONES, fr, lire, lire_processed  # noqa: E402
from theme import (BLEUS, COULEUR_REGION, COULEUR_ZONE, DISCRET, ENCRE, ENCRE2, ETAT, FILET,  # noqa: E402
                   PRIORITE, SERIE, THEME)

# Hors d'une session Streamlit, les lectures en cache du tableau de bord signalent l'absence de serveur à chaque appel.
logging.getLogger("streamlit").setLevel(logging.ERROR)

ASSETS = RACINE / "tmp" / "ppt_assets"
ASSETS.mkdir(parents=True, exist_ok=True)
SORTIE = RACINE / "Togo-Mobilite-Securite-Routiere-Defi1.pptx"

# --------------------------------------------------------------------------------------------------------------------
# Identité : textes et adresses
# --------------------------------------------------------------------------------------------------------------------

#: ⚠️ À confirmer avant l'envoi : le nom paraît sur la couverture (fichier `.env` : firstanme / lastname).
PRESENTE_PAR = "Addi Carters"

#: ⚠️ À renseigner avant l'envoi : déploiement prévu sur Streamlit Cloud, aucune adresse dans le dépôt.
#: Laissée vide, la ligne n'est pas rendue — jamais de texte factice.
URL_DASHBOARD = ""

#: Mention de source générique des pages de décision (11 §4.2).
LIGNE_SOURCE = ("Données : portail national de données ouvertes du Togo, recensement de 2022 et sources "
                "institutionnelles complémentaires.")
PIED_IDENTITE = "Togo AI Lab — Data Challenge | Mobilité et sécurité routière — Défi 1"
BANDEAU = "Rapport de synthèse · Mobilité et sécurité routière — Défi 1"
#: Attribution obligatoire des armoiries (CC BY-SA 4.0) : `_CONSTRAINTS_DEV.txt`, `static/README_armoiries.md`.
ATTRIBUTION = "Armoiries du Togo : Edem Fiadjoe, CC BY-SA 4.0"

# --------------------------------------------------------------------------------------------------------------------
# Palette : celle du tableau de bord
# --------------------------------------------------------------------------------------------------------------------

NAVY = PRIORITE["Haute"]                 # #0d366b : titres de carte, priorité haute, phrases de lecture
BLANC = "#FFFFFF"
JAUNE = "#fce588"                        # jaune clair, lisible sur fond sombre
OR = "#ffce00"                           # bordure de la carte du logo, dans la barre du haut
GRIS_POINT = "#b9b6ad"
BLEU_CLAIR_TEXTE = "#cde2fb"
ROUGE_SERIE, ORANGE_SERIE, VERT_SERIE, JAUNE_SERIE = ETAT["Mauvais"], THEME["Sécurité routière"], ETAT["Bon"], ETAT["Moyen"]
#: Ocre lisible sur fond blanc, pour les surtitres (le jaune de thème ne passe pas sur blanc).
OCRE_TEXTE = "#8a5a00"

#: Tons des étiquettes et des encadrés du tableau de bord (theme.py : .etiquette, .constat, .limite).
TONS = {
    "bleu":   dict(bg="#e8f0fb", bord="#c7d8f0", encre=NAVY),
    "navy":   dict(bg="#e3eefb", bord="#c7d8f0", encre=NAVY),
    "ambre":  dict(bg="#fdf0d2", bord="#ecd28f", encre="#6b4700"),
    "limite": dict(bg="#fdf3d7", bord="#ecd28f", encre="#6b4700"),
    "rouge":  dict(bg="#fbe3e2", bord="#f1c4c2", encre="#8a1c1b"),
    "vert":   dict(bg="#e2f4ec", bord="#bfe3d2", encre="#11613f"),
    "violet": dict(bg="#ece9fb", bord="#d5cff3", encre="#4a3aa7"),
    "orange": dict(bg="#fde8dd", bord="#f6cdb7", encre="#b4451a"),
    "gris":   dict(bg="#efece4", bord=FILET, encre=ENCRE2),
}
ETIQUETTE = {"alerte": "ambre", "ok": "navy", "critique": "rouge", "neutre": "gris"}

#: Couleurs des 4 thèmes de l'énoncé, en pas lisibles sur fond blanc (les titres de thème du tableau de bord).
THEME_TEXTE = {"Mobilité": "#1b5894", "Sécurité routière": "#a74d08", "Réseau": "#8a5a00", "Couverture": "#0f6b3c"}

POLICE, POLICE_TITRE = "Calibri", "Cambria"
LARGEUR, HAUTEUR = Emu(12192000), Emu(6858000)   # 16:9 exact
SW, SH = 13.333, 7.5
M = 0.55                                        # marges gauche et droite
CW = SW - 2 * M                                 # largeur utile : 12,233
DROITE = M + CW
CORPS_Y, CORPS_Y_SOUS = 1.60, 1.96             # haut du contenu, sans et avec sous-titre
PIED_Y = 7.05

AVERTISSEMENTS: list[str] = []                  # textes réduits pour tenir dans leur cadre, signalés en fin d'exécution

# --------------------------------------------------------------------------------------------------------------------
# Données — lues une fois, jamais retapées
# --------------------------------------------------------------------------------------------------------------------

IND = lire("07_indicateurs", "indicateurs_07")
NAT = IND[IND.Maille == "National"]
TAUX = lire("09_diagnostic", "taux_09")
HYP = lire("09_diagnostic", "hypotheses_09").set_index("Code")
CL = lire("08_priorisation", "classement_08")
REG = lire("08_priorisation", "regions_08")
PAYS = REG[REG.Maille == "Pays"].iloc[0]
SENS = lire("08_priorisation", "sensibilite_08")
P10 = lire("10_recommandations", "prefectures_10")
Z10 = lire("10_recommandations", "zones_10")
R10 = lire("10_recommandations", "recommandations_10").set_index("ID")
C10 = lire("10_recommandations", "cartes_10").set_index("ID")
P06 = lire("06_exploration", "prefectures_06")
HOR = lire("A1_horizon", "horizon_A1")
NA1 = lire("A1_horizon", "national_A1")
TRONCONS = lire_processed("D4_etat_troncons")
ANNUAIRE = lire_processed("D4_etat_national_pct")

ZONE_ROWS = Z10[Z10.Maille == "Zone"].set_index("Zone")
REG_ZONES = REG[REG.Maille == "Zone"].set_index("Territoire")


def val(idc, annee=None, cat=None, mesure=None) -> float:
    """Une valeur nationale de `indicateurs_07`, filtrée comme le fait le tableau de bord."""
    s = NAT[NAT.ID == idc]
    if annee is not None:
        s = s[s["Année"].astype(str) == str(annee)]
    if cat is not None:
        s = s[s["Catégorie"] == cat]
    if mesure is not None:
        s = s[s["Mesure"] == mesure]
    return float(s.iloc[0]["Valeur"])


def serie(idc, cat=None, mesure=None) -> pd.Series:
    """Une série annuelle nationale, indexée par année entière (les lignes de cumul sont écartées)."""
    s = NAT[NAT.ID == idc]
    if cat is not None:
        s = s[s["Catégorie"] == cat]
    if mesure is not None:
        s = s[s["Mesure"] == mesure]
    s = s[s["Année"].astype(str).str.fullmatch(r"\d{4}")]
    return pd.Series(s["Valeur"].values, index=s["Année"].astype(int).values).sort_index()


# Objectif 1 — mobilité
GROUPES = ["Moto", "Voiture", "Poids lourd", "Bus et car", "Autres"]
A_IMM = int(serie("O1-01", cat="Ensemble").index.max())
IMM_TOT = val("O1-01", A_IMM, "Ensemble")
IMM_MOTO = val("O1-01", A_IMM, "Moto")
PART_MOTO = val("O1-02", A_IMM, "Moto")
MULT = float(HYP.loc["S1", "Valeur"])
_mult = serie("O1-03", cat="Ensemble", mesure="multiplicateur sur 20 ans").round(2)
A_MULT = int(_mult[_mult == round(MULT, 2)].index[0])
CONTRIB_MOTO = float(HYP.loc["S2", "Valeur"])
CAT_PERMIS = ["A", "B", "C", "D", "E", "F"]
A_PER = int(serie("O1-06", cat="B").index.max())
PERMIS = pd.Series({c: val("O1-06", A_PER, c) for c in CAT_PERMIS})
PERMIS_TOT = PERMIS.sum()
PERMIS_A_AVANT = serie("O1-06", cat="A")
A_AVANT = int(PERMIS_A_AVANT.index[PERMIS_A_AVANT.index < A_PER].max())
# Rapport immatriculations / permis en cumul : la catégorie F ne conduit aucun type de véhicule, elle n'en a pas.
_cumul = NAT[(NAT.ID == "O1-09") & (~NAT["Année"].astype(str).str.fullmatch(r"\d{4}"))]
A_CUMUL = str(_cumul["Année"].iloc[0])
RATIO_CUM = _cumul.set_index("Catégorie")["Valeur"].astype(float)

# Objectif 2 — sécurité routière
A_ACC = 2022                                     # année de l'énoncé, vérifiée présente dans la série
ACCIDENTS = val("O2-01", A_ACC, "Accidents constatés")
BLESSES = val("O2-01", A_ACC, "Blessés")
TUES = val("O2-01", A_ACC, "Tués")
VOLUMES = TAUX[TAUX.Lecture == "volume"].set_index("Mesure")
RATIOS = TAUX[TAUX.Lecture != "volume"]
assert len(RATIOS) == 6 and (RATIOS.Sens == "baisse").all(), "les 6 taux de risque"
HAUSSE_ACC = float(VOLUMES.loc["Accidents constatés", "Variation (%)"])
USAGER = NAT[NAT.ID == "O2-09"].set_index("Catégorie")["Valeur"]
PART_2ROUES = float(USAGER["Deux et trois-roues motorisés"])
TUES_HAB_2021 = float(PAYS["SE-03 O2-02 de 2021 (tués déclarés)"])
OMS_2021 = float(PAYS["SE-03 repère OMS Togo 2021"])
A_OMS = int(NAT[(NAT.ID == "O2-09")]["Année"].iloc[0])

# Objectif 3 — réseau
PART_MAUVAIS = float(PAYS["O3-02"])
KM_MAUVAIS = float(PAYS["Km en mauvais état"])
KM_EVALUES = float(PAYS["Km évalués"])
N_TRONCONS = len(TRONCONS)
N_CRITIQUES = int((TRONCONS.km_mauvais > 0).sum())
A_RELEVE = int(TRONCONS["Année"].iloc[0])
ECART_ZONES = float(HYP.loc["S5", "Valeur"])
ZONE_PIRE = ZONE_ROWS["Part en mauvais état (%)"].idxmax()
ZONE_MEILLEURE = ZONE_ROWS["Part en mauvais état (%)"].idxmin()
_ann = ANNUAIRE[(ANNUAIRE["Année"] == A_RELEVE) & (ANNUAIRE["État"] == "Mauvais")
                & (ANNUAIRE["Catégorie de route"] == "Routes nationales revêtues et non revêtues")]
ANNUAIRE_MAUVAIS = float(_ann.iloc[0]["Part (%)"])

# Objectif 4 — couverture et formation
AE_AGREEES = int(PAYS["Auto-écoles comptées"])
AE_RECENSEES = int(P10["Formation — auto-écoles recensées"].sum())
SANS_AE = P10[P10["Formation — auto-écoles comptées"] == 0]
POP_SANS_AE = int(SANS_AE.Population.sum())
URBAINES = P06[P06["Classe PA-03"] == "urbaine"]
PART_AE_URBAIN = 100 * URBAINES["Auto-écoles comptées"].sum() / P06["Auto-écoles comptées"].sum()
PART_POP_URBAIN = 100 * URBAINES["Population 2022"].sum() / P06["Population 2022"].sum()
FOIS_URBAIN = PART_AE_URBAIN / PART_POP_URBAIN
SEUIL_DISTANCE = 10                              # seuil de distance à l'auto-école agréée (08)
LOIN = P10[P10["Formation — distance à la plus proche (km)"] > SEUIL_DISTANCE]
ACCES_RURAL = float(Z10[Z10.Maille == "Pays"].iloc[0]["Accès rural à une route revêtue (%)"])
POPULATION = int(PAYS["Population"])

# Objectif 5 — priorités
CLASSEES = CL[CL["Classée"]].copy()
TOP10 = CLASSEES.nsmallest(10, "O5-02 rang").copy()
POP_TOP10 = int(TOP10.Population.sum())
CUMUL = P10[P10["Déficits"] == 2].copy()
POP_CUMUL = int(CUMUL.Population.sum())
KM_CUMUL = float(CUMUL["Réseau — km à remettre en état"].sum())
AE_CUMUL = int(CUMUL["Formation — auto-écoles à ouvrir"].sum())
N_RESEAU = int(PAYS["Préfectures au levier réseau"])
N_FORMATION = int(PAYS["Préfectures au levier formation"])
POP_RESEAU = int(PAYS["Population des préfectures au levier réseau"])
POP_FORMATION = int(PAYS["Population des préfectures au levier formation"])
KM_A_REMETTRE = float(PAYS["O5-04 km à remettre en état, préfectures au levier réseau"])
AE_A_OUVRIR = int(PAYS["O5-04 auto-écoles manquantes (écart 21), préfectures au levier formation"])
HORS_CLASSEMENT = CL[~CL["Classée"]].iloc[0]
MO = P10[P10["Préfecture"] == HORS_CLASSEMENT["Préfecture"]].iloc[0]
TESTS = SENS[SENS["Préfecture"].isna()]
TESTS_REELS = TESTS[TESTS["Changements parmi les 10 premières"] > 0]
MAX_CHANGEMENTS = int(TESTS["Changements parmi les 10 premières"].max())
N_TESTS = int(CLASSEES["Tests parmi les 10 premières (sur 6)"].max())
TOUJOURS = CLASSEES[CLASSEES["Tests parmi les 10 premières (sur 6)"] == N_TESTS]
PLUS_PEUPLEES = CL.nlargest(2, "Population")
HORS_TOP10 = [n for n in PLUS_PEUPLEES["Préfecture"] if n not in set(TOP10["Préfecture"])]
AGOE = P10[P10["Préfecture"] == "Agoè-Nyivé"].iloc[0]

# Déficits : combien cumulent, combien en ont un, combien aucun
DEFICITS = P10["Déficits"].value_counts()
# Nature du zéro, comme en page 5 : aucune auto-école recensée, ou recensées mais non agréées
SANS_AUCUNE = SANS_AE[SANS_AE["Formation — auto-écoles recensées"] == 0]
NON_AGREEES = SANS_AE[SANS_AE["Formation — auto-écoles recensées"] > 0]

# Vérifications et hypothèses
N_HYP = len(HYP)
N_CONFIRMEES = int((HYP.Verdict == "confirmée").sum())
N_NON_TESTABLES = int((HYP.Verdict == "non testable").sum())

# Recommandations
N_RECO = len(R10)
RECO_HAUTE = R10[R10["Priorité"] == "Haute"]
# Horizon 2031
_lev = HOR[(HOR.Maille == "Pays") & (HOR["Périmètre"] == "Levier du 08")]
AE_HORIZON = _lev[_lev.Levier == "Auto-écoles"].set_index("Année")["Valeur"]
KM_HORIZON = _lev[_lev.Levier == "Remise en état"].set_index("Année")["Valeur"]
_acces = HOR[(HOR.Maille == "Pays") & (HOR.Levier == "Accès rural")].set_index("Année")
RURAUX_HORIZON = _acces["Valeur"]
A_FIN = int(AE_HORIZON.index.max())
A_DEBUT = int(AE_HORIZON.index.min())
ECART_CIBLE = NA1[(NA1.Mesure == "Tués") & (NA1["Série"] == "Écart à la cible (tendance)")].set_index("Année")["Valeur"]
A_ECART = 2029                                   # horizon par défaut de la page Horizon 2031 (3 ans)
assert KM_HORIZON.nunique() == 1, "la remise en état ne dépend pas de l'horizon"

# Zones en difficulté (page 5, section 1) : rang du classement des zones et conclusion du 10
ZONES_DIFF = ZONE_ROWS[ZONE_ROWS["Moins bien desservie pour"].notna()]
ZONE_TETE = REG_ZONES.loc[[z for z in ZONES if z in REG_ZONES.index]].sort_values("Rang").index[0]
RECO_ZONE_TETE = C10.loc[ZONE_ROWS.loc[ZONE_TETE, "Recommandation"]]
#: La cible du permis moto est celle du document des recommandations, pour ne pas donner deux chiffres au jury.
CIBLE_PERMIS = str(C10.loc["REC-F3", "Cible"]).rstrip(".")


# --------------------------------------------------------------------------------------------------------------------
# Mise en forme des nombres (espaces insécables : un nombre ne se coupe jamais en fin de ligne)
# --------------------------------------------------------------------------------------------------------------------

def nb(x, d=0) -> str:
    """Le format français du tableau de bord, avec une espace insécable : un nombre ne se coupe jamais."""
    return fr(x, d).replace(" ", "\u00a0")


def pct(x, d=1) -> str:
    return f"{nb(x, d)} %"


def millions(x, d=1) -> str:
    return f"{nb(x / 1e6, d)} million{'s' if x >= 2e6 else ''}"


def et(noms) -> str:
    noms = list(noms)
    return noms[0] if len(noms) == 1 else ", ".join(noms[:-1]) + " et " + noms[-1]


def rgb(couleur: str) -> RGBColor:
    c = couleur.lstrip("#")
    return RGBColor(int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


# --------------------------------------------------------------------------------------------------------------------
# Mesure du texte — pour ajuster la taille avant d'écrire, pas après
# --------------------------------------------------------------------------------------------------------------------

#: Métriques de Liberation Sans, volontairement pessimistes : Calibri est plus étroite d'environ 10 %, Cambria a une
#: largeur voisine. Un texte qui tient ici tient dans PowerPoint.
_POLICES_MESURE = {False: "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
                   True: "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf"}
_cache_polices: dict = {}


def largeur_texte(texte: str, taille: float, gras: bool = False) -> float:
    """Largeur d'un texte, en pouces."""
    if gras not in _cache_polices:
        try:
            _cache_polices[gras] = ImageFont.truetype(_POLICES_MESURE[gras], 100)
        except OSError:
            _cache_polices[gras] = None
    police = _cache_polices[gras]
    if police is None:
        return len(texte) * 0.55 * taille / 72
    return police.getlength(texte) / 100 * taille / 72


def nombre_lignes(texte: str, taille: float, gras: bool, largeur: float) -> int:
    lignes = 0
    for morceau in texte.split("\n"):
        courante, n = "", 1
        for mot in morceau.split(" "):
            essai = f"{courante} {mot}" if courante else mot
            if courante and largeur_texte(essai, taille, gras) > largeur:
                n, courante = n + 1, mot
            else:
                courante = essai
        lignes += n
    return lignes


def taille_ajustee(texte: str, largeur: float, tailles=(26, 24, 22, 20, 18), gras=True) -> float:
    """La plus grande taille à laquelle le texte tient sur une seule ligne."""
    for taille in tailles:
        if largeur_texte(texte, taille, gras) <= largeur:
            return taille
    return tailles[-1]


# --------------------------------------------------------------------------------------------------------------------
# Primitives de composition — toutes les coordonnées sont en pouces
# --------------------------------------------------------------------------------------------------------------------

def nouvelle_diapositive(presentation):
    return presentation.slides.add_slide(presentation.slide_layouts[6])


def rect(d, x, y, w, h, *, fond=None, rayon=0.0, bord=None, epaisseur=0.75):
    forme = d.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rayon else MSO_SHAPE.RECTANGLE,
                               Inches(x), Inches(y), Inches(w), Inches(h))
    if rayon:
        forme.adjustments[0] = min(0.5, rayon / min(w, h))
    if fond:
        forme.fill.solid()
        forme.fill.fore_color.rgb = rgb(fond)
    else:
        forme.fill.background()
    if bord:
        forme.line.color.rgb = rgb(bord)
        forme.line.width = Pt(epaisseur)
    else:
        forme.line.fill.background()
    forme.shadow.inherit = False
    return forme


def _sans_marges(cadre) -> None:
    cadre.margin_left = cadre.margin_right = cadre.margin_top = cadre.margin_bottom = 0


def _run(paragraphe, texte, *, taille=12, gras=False, couleur=ENCRE, italique=False, police=POLICE, lien=None):
    run = paragraphe.add_run()
    run.text = texte
    run.font.size = Pt(taille)
    run.font.bold = gras
    run.font.italic = italique
    run.font.name = police
    run.font.color.rgb = rgb(couleur)
    if lien:
        run.hyperlink.address = lien
        run.font.underline = True
        run.font.color.rgb = rgb(couleur)
    return run


_STYLE = ("taille", "gras", "couleur", "italique", "police", "lien")


def _runs(ligne: dict) -> list[dict]:
    base = {k: ligne[k] for k in _STYLE if k in ligne}
    if "runs" in ligne:
        return [dict(base, **r) for r in ligne["runs"]]
    return [dict(base, texte=ligne["texte"])]


def _hauteur(lignes: list[dict], largeur: float, facteur: float = 1.0) -> float:
    total = 0.0
    for ligne in lignes:
        runs = _runs(ligne)
        taille = max(r.get("taille", 12) for r in runs) * facteur
        gras = any(r.get("gras") for r in runs)
        n = nombre_lignes("".join(r["texte"] for r in runs), taille, gras, largeur)
        total += n * taille * 1.2 * ligne.get("interligne", 1.0) / 72
        total += (ligne.get("avant", 0) + ligne.get("apres", 0)) / 72
    return total


def bloc(d, x, y, w, h, lignes, *, align=PP_ALIGN.LEFT, ancre=MSO_ANCHOR.TOP, ajuster=True):
    """Une zone de texte. Chaque ligne est un paragraphe : `texte` ou `runs`, et son style.

    Interligne et espacements sont **explicites, en points** : laissés implicites, chaque moteur de rendu les
    recalcule. Si le texte ne tient pas, la taille est réduite par pas de 2,5 %, jusqu'à 80 % au plus, et la
    réduction est signalée en fin d'exécution : un texte qui déborde n'est jamais laissé tel quel.
    """
    lignes = [dict(l) if isinstance(l, dict) else dict(texte=l) for l in lignes]
    facteur = 1.0
    if ajuster:
        while _hauteur(lignes, w, facteur) > h + 0.01 and facteur > 0.80:
            facteur -= 0.025
        if facteur < 1.0:
            apercu = "".join(r["texte"] for r in _runs(lignes[0]))[:50]
            AVERTISSEMENTS.append(f"réduit à {facteur:.0%} : « {apercu}… »")
    boite = d.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    cadre = boite.text_frame
    cadre.word_wrap = True
    cadre.auto_size = MSO_AUTO_SIZE.NONE
    cadre.vertical_anchor = ancre
    _sans_marges(cadre)
    for i, ligne in enumerate(lignes):
        p = cadre.paragraphs[0] if i == 0 else cadre.add_paragraph()
        p.alignment = ligne.get("align", align)
        p.line_spacing = ligne.get("interligne", 1.0)
        p.space_before = Pt(ligne.get("avant", 0))
        p.space_after = Pt(ligne.get("apres", 0))
        for r in _runs(ligne):
            style = {k: r[k] for k in _STYLE if k in r}
            style["taille"] = round(style.get("taille", 12) * facteur * 2) / 2
            _run(p, r["texte"], **style)
    return boite


def T(texte, **style) -> dict:
    return dict(texte=texte, **style)


def Z(zone: str, **style) -> dict:
    """Un nom de zone écrit dans sa couleur, comme dans les tableaux et les constats du tableau de bord."""
    return dict(texte=zone, couleur=COULEUR_ZONE[zone], gras=True, **style)


def surtitre(d, x, y, w, texte, couleur=OCRE_TEXTE):
    bloc(d, x, y, w, 0.24, [T(texte.upper(), taille=10, gras=True, couleur=couleur)])


def pastille(d, x, y, texte, ton, *, taille=9, h=0.24, droite=False) -> float:
    """Étiquette arrondie, comme `.etiquette` du tableau de bord. Avec `droite`, x est le bord droit."""
    w = largeur_texte(texte, taille, True) + 0.26
    if droite:
        x -= w
    tonalite = TONS[ETIQUETTE.get(ton, ton)]
    forme = rect(d, x, y, w, h, fond=tonalite["bg"], rayon=h / 2)
    cadre = forme.text_frame
    cadre.word_wrap = False
    _sans_marges(cadre)
    cadre.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cadre.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _run(p, texte, taille=taille, gras=True, couleur=tonalite["encre"])
    return w


def carre_numero(d, x, y, cote, texte, couleur, *, taille=13):
    """Le motif du rapport : une pastille carrée arrondie, pleine, chiffre blanc."""
    forme = rect(d, x, y, cote, cote, fond=couleur, rayon=cote * 0.28)
    cadre = forme.text_frame
    _sans_marges(cadre)
    cadre.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cadre.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _run(p, texte, taille=taille, gras=True, couleur=BLANC, police=POLICE_TITRE)
    return forme


def carte(d, x, y, w, h, *, fond=BLANC, bord=FILET):
    """Carte blanche, bordure fine, coins arrondis : le conteneur du tableau de bord."""
    return rect(d, x, y, w, h, fond=fond, rayon=0.12, bord=bord)


def cartouche(d, x, y, w, h, *, surtitre_txt, valeur, unite="", phrase, note="", etiquette=None, ton="alerte",
              couleur_valeur=ENCRE):
    """Carte de chiffre clé, sur le modèle des chiffres clés du tableau de bord."""
    carte(d, x, y, w, h)
    pad = 0.18
    interieur = w - 2 * pad
    largeur_etiquette = pastille(d, x + w - pad, y + 0.13, etiquette, ton, taille=8.5, h=0.22, droite=True) + 0.08 \
        if etiquette else 0
    bloc(d, x + pad, y + 0.15, interieur - largeur_etiquette, 0.22,
         [T(surtitre_txt.upper(), taille=8.5, gras=True, couleur=NAVY)])
    taille_valeur = 25
    while taille_valeur > 15 and (largeur_texte(valeur, taille_valeur, True)
                                  + (largeur_texte(f" {unite}", taille_valeur * 0.48, True) if unite else 0)
                                  > interieur - 0.06):
        taille_valeur -= 1
    runs = [T(valeur, taille=taille_valeur, gras=True, couleur=couleur_valeur, police=POLICE_TITRE)]
    if unite:
        runs.append(T(f" {unite}", taille=round(taille_valeur * 0.48 * 2) / 2, gras=True, couleur=couleur_valeur))
    bloc(d, x + pad, y + 0.40, interieur, 0.46, [dict(runs=runs)], ajuster=False)
    # La phrase prend une ou deux lignes : la note se place dessous, jamais sur elle.
    hauteur_phrase = nombre_lignes(phrase, 10.5, True, interieur) * 10.5 * 1.2 / 72 + 0.02
    bloc(d, x + pad, y + 0.88, interieur, hauteur_phrase, [T(phrase, taille=10.5, gras=True, couleur=ENCRE)])
    if note:
        y_note = y + 0.88 + hauteur_phrase + 0.05
        bloc(d, x + pad, y_note, interieur, y + h - 0.08 - y_note, [T(note, taille=9, couleur=ENCRE2)])


def banniere(d, x, y, w, h, etiquette, texte, style="sombre", *, taille=11.5):
    """Bandeau de message : `sombre` (le message à retenir), `constat`, `limite` ou `vert`."""
    if style == "sombre":
        rect(d, x, y, w, h, fond=NAVY, rayon=0.10)
        encre, encre_etiquette, gras = BLANC, JAUNE, True
    else:
        ton = {"constat": "bleu", "limite": "limite", "vert": "vert"}[style]
        rect(d, x, y, w, h, fond=TONS[ton]["bg"], rayon=0.10, bord=TONS[ton]["bord"])
        encre, encre_etiquette, gras = ENCRE, TONS[ton]["encre"], False
    runs = []
    if etiquette:
        runs.append(T(f"{etiquette.upper()}  ·  ", taille=taille - 1, gras=True, couleur=encre_etiquette))
    runs += [dict(r, **{"couleur": r.get("couleur", encre)}) for r in (texte if isinstance(texte, list) else [T(texte)])]
    runs = [dict(r, taille=r.get("taille", taille), gras=r.get("gras", gras)) for r in runs]
    bloc(d, x + 0.26, y + 0.06, w - 0.52, h - 0.12, [dict(runs=runs, interligne=1.05)], ancre=MSO_ANCHOR.MIDDLE)


def encadre(d, x, y, w, h, ton, runs, *, taille=11.5, gras=True):
    """Encadré teinté (constat, enjeu) : texte en gras, chiffres et territoires en couleur."""
    rect(d, x, y, w, h, fond=TONS[ton]["bg"], rayon=0.12, bord=TONS[ton]["bord"])
    runs = [dict(r, taille=r.get("taille", taille), gras=r.get("gras", gras)) for r in runs]
    bloc(d, x + 0.22, y + 0.12, w - 0.44, h - 0.24, [dict(runs=runs, interligne=1.12)], ancre=MSO_ANCHOR.MIDDLE)


def panneau(d, x, y, w, h, titre, *, sous_titre=None) -> float:
    """Carte blanche titrée, pour un graphique ou une carte. Renvoie l'ordonnée sous le titre."""
    carte(d, x, y, w, h)
    bloc(d, x + 0.22, y + 0.14, w - 0.44, 0.28, [T(titre, taille=12.5, gras=True, couleur=ENCRE, police=POLICE_TITRE)])
    if sous_titre:
        hauteur = nombre_lignes(sous_titre, 9, False, w - 0.44) * 9 * 1.2 / 72 + 0.02
        bloc(d, x + 0.22, y + 0.42, w - 0.44, hauteur, [T(sous_titre, taille=9, couleur=DISCRET)])
        return y + 0.44 + hauteur + 0.04
    return y + 0.46


def lien(d, x, y, w, texte, url, *, taille=11, couleur=NAVY):
    boite = d.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(0.28))
    cadre = boite.text_frame
    cadre.word_wrap = False
    _sans_marges(cadre)
    _run(cadre.paragraphs[0], texte, taille=taille, gras=True, couleur=couleur, lien=url)


def image_ajustee(d, chemin: Path, x, y, largeur_max, hauteur_max, *, centre=True):
    with Image.open(chemin) as image:
        largeur, hauteur = image.size
    ratio = min(largeur_max / largeur, hauteur_max / hauteur)
    w, h = largeur * ratio, hauteur * ratio
    if centre:
        x, y = x + (largeur_max - w) / 2, y + (hauteur_max - h) / 2
    d.shapes.add_picture(str(chemin), Inches(x), Inches(y), width=Inches(w), height=Inches(h))


def tableau_texte(d, x, y, w, colonnes, lignes, *, taille=10.5, h_ligne=0.30, h_entete=0.28) -> float:
    """Tableau dessiné en zones de texte. `colonnes` : (titre, largeur, alignement). Une cellule est un texte, ou un
    tuple (texte, couleur, gras). Renvoie l'ordonnée sous la dernière ligne."""
    rect(d, x, y, w, h_entete, fond=TONS["gris"]["bg"], rayon=0.06)
    curseur = x + 0.14
    for titre, largeur, align in colonnes:
        bloc(d, curseur, y, largeur - 0.08, h_entete, [T(titre, taille=8.5, gras=True, couleur=ENCRE2)], align=align,
             ancre=MSO_ANCHOR.MIDDLE)
        curseur += largeur
    ordonnee = y + h_entete
    for i, ligne in enumerate(lignes):
        curseur = x + 0.14
        for (_, largeur, align), cellule in zip(colonnes, ligne):
            texte, couleur, gras = cellule if isinstance(cellule, tuple) else (cellule, ENCRE, False)
            bloc(d, curseur, ordonnee + 0.02, largeur - 0.08, h_ligne - 0.04,
                 [T(texte, taille=taille, couleur=couleur, gras=gras, interligne=0.95)], align=align,
                 ancre=MSO_ANCHOR.MIDDLE)
            curseur += largeur
        ordonnee += h_ligne
        if i < len(lignes) - 1:
            rect(d, x + 0.10, ordonnee - 0.004, w - 0.20, 0.008, fond=FILET)
    return ordonnee


def en_tete(d, numero: int, surtitre_txt: str, titre: str, *, sous_titre: str | None = None) -> float:
    """Armoiries et nom du projet (la barre du haut du tableau de bord), surtitre, titre, numéro."""
    image_ajustee(d, ARMOIRIES, M, 0.17, 0.44, 0.40, centre=False)
    bloc(d, M + 0.56, 0.20, 6.2, 0.32, [T(MARQUE.upper(), taille=10, gras=True, couleur=NAVY)], ancre=MSO_ANCHOR.MIDDLE)
    bloc(d, DROITE - 5.6, 0.20, 5.6, 0.32, [T(BANDEAU, taille=9.5, couleur=DISCRET)], align=PP_ALIGN.RIGHT,
         ancre=MSO_ANCHOR.MIDDLE)
    surtitre(d, M, 0.70, 9.0, surtitre_txt)
    bloc(d, DROITE - 0.8, 0.66, 0.8, 0.30, [T(str(numero), taille=14, gras=True, couleur=GRIS_POINT)],
         align=PP_ALIGN.RIGHT)
    bloc(d, M, 0.95, CW, 0.52, [T(titre, taille=taille_ajustee(titre, CW), gras=True, couleur=ENCRE,
                                  police=POLICE_TITRE)])
    if sous_titre:
        bloc(d, M, 1.50, CW, 0.28, [T(sous_titre, taille=12, couleur=DISCRET)])
        return CORPS_Y_SOUS
    return CORPS_Y


def pied(d, texte: str = LIGNE_SOURCE) -> None:
    bloc(d, M, PIED_Y, 8.4, 0.24, [T(texte, taille=8.5, couleur=DISCRET)])
    bloc(d, DROITE - 3.9, PIED_Y, 3.9, 0.24, [T(PIED_IDENTITE, taille=8.5, couleur=DISCRET)], align=PP_ALIGN.RIGHT)


# --------------------------------------------------------------------------------------------------------------------
# Graphiques — matplotlib, dans la palette du tableau de bord
# --------------------------------------------------------------------------------------------------------------------

_familles = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Liberation Sans" if "Liberation Sans" in _familles else "DejaVu Sans",
    "font.size": 8.5, "axes.edgecolor": FILET, "axes.labelcolor": ENCRE2, "xtick.color": ENCRE2,
    "ytick.color": ENCRE2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white",
    "axes.facecolor": "white", "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.titlecolor": ENCRE,
})

GEO = RACINE / "data" / "processed" / "geo"


def _enregistrer(figure, nom: str) -> Path:
    chemin = ASSETS / f"{nom}.png"
    figure.savefig(chemin, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    return chemin


def _grille(axes, axe="y"):
    axes.grid(axis=axe, color="#efece4", linewidth=0.7)
    axes.set_axisbelow(True)


def _nom_zone(nom: str) -> str:
    return nom.replace("Maritime hors Grand Lomé", "Maritime hors\nGrand Lomé")


def graphique_mobilite(w=8.0, h=1.82) -> Path:
    """Objectif 1 : les immatriculations par groupe depuis 1990 ; les permis de la dernière année par catégorie."""
    figure, (a1, a2) = plt.subplots(1, 2, figsize=(w, h), gridspec_kw={"width_ratios": [1.9, 1], "wspace": 0.30})
    for groupe in GROUPES:
        s = serie("O1-01", cat=groupe)
        a1.plot(s.index, s.values / 1000, color=SERIE[groupe], lw=1.6 if groupe == "Moto" else 1.1, zorder=3,
                label=groupe)
    # Ruptures de série : une date situe une variation, elle ne l'explique pas (non-causalité, 11 §4.5).
    for annee in (1995, 2004):
        a1.axvline(annee, color=GRIS_POINT, ls="--", lw=0.8, zorder=1)
        # L'année se lit en bas : en haut, elle passait sous la légende.
        a1.text(annee, a1.get_ylim()[1] * 0.02, f" {annee}", fontsize=6.5, color=DISCRET, va="bottom")
    s_moto = serie("O1-01", cat="Moto")
    a1.annotate(f"{fr(s_moto.loc[A_IMM])}", (A_IMM, s_moto.loc[A_IMM] / 1000), xytext=(-2, 11),
                textcoords="offset points", ha="right", fontsize=8, weight="bold", color=SERIE["Moto"])
    a1.set_ylabel("Milliers de véhicules", fontsize=7.5)
    a1.set_xticks([a for a in s_moto.index if a % 5 == 0])
    a1.tick_params(axis="x", labelsize=7.5)
    a1.set_title("Immatriculations de l’année, par groupe de véhicules", loc="left")
    a1.legend(loc="upper left", fontsize=7, frameon=False, ncol=2, handlelength=1.2)
    a1.text(1996.0, a1.get_ylim()[1] * 0.12, "traits : ruptures de série", fontsize=6.5, color=DISCRET)
    _grille(a1)

    ordre = PERMIS.sort_values()
    y = np.arange(len(ordre))
    couleurs = {"A": SERIE["Moto"], "B": SERIE["Voiture"], "C": SERIE["Poids lourd"], "E": SERIE["Poids lourd"],
                "D": SERIE["Bus et car"], "F": GRIS_POINT}
    a2.barh(y, ordre.values, color=[couleurs[c] for c in ordre.index], height=0.64)
    for i, (c, v) in enumerate(ordre.items()):
        a2.text(v + PERMIS.max() * 0.03, i, fr(v), va="center", fontsize=7.5, color=ENCRE, weight="bold")
    a2.set_yticks(y, [f"Permis {c}" for c in ordre.index], fontsize=7.5)
    a2.set_xlim(0, PERMIS.max() * 1.32)
    a2.set_xticks([])
    a2.spines["bottom"].set_visible(False)
    a2.set_title(f"Permis délivrés par catégorie, {A_PER}", loc="left")
    return _enregistrer(figure, "mobilite")


def graphique_securite(w=8.0, h=1.82) -> Path:
    """Objectif 2 : les 6 taux de risque, deux périodes face à face ; les tués par type d'usager."""
    figure, (a1, a2) = plt.subplots(1, 2, figsize=(w, h), gridspec_kw={"width_ratios": [1.7, 1], "wspace": 0.52})
    vue = RATIOS.iloc[::-1]
    couleur_mesure = {"Accidents constatés": THEME["Mobilité"], "Blessés": ORANGE_SERIE, "Tués": ROUGE_SERIE}
    y = np.arange(len(vue))
    a1.barh(y + 0.20, vue["Moyenne 2010–2012"], height=0.36, color="#cde2fb", label="2010–2012")
    a1.barh(y - 0.20, vue["Moyenne 2022–2024"], height=0.36,
            color=[couleur_mesure[m] for m in vue.Mesure], label="2022–2024")
    maximum = vue["Moyenne 2010–2012"].max()
    for yi, (avant, apres, variation) in enumerate(zip(vue["Moyenne 2010–2012"], vue["Moyenne 2022–2024"],
                                                       vue["Variation (%)"])):
        a1.text(avant + maximum * 0.015, yi + 0.20, fr(avant, 1), va="center", fontsize=6.5, color=ENCRE2)
        a1.text(apres + maximum * 0.015, yi - 0.20, fr(apres, 1), va="center", fontsize=6.5, color=ENCRE,
                weight="bold")
        a1.text(max(avant, apres) + maximum * 0.14, yi, f"{fr(variation, 1)} %", va="center", fontsize=7.5,
                color=VERT_SERIE, weight="bold")
    a1.set_yticks(y, [f"{m}\n{l.replace('pour 100 000 habitants', 'pour 100 000 hab.')}"
                      for m, l in zip(vue.Mesure, vue.Lecture)], fontsize=6.5)
    a1.set_xlim(0, maximum * 1.30)
    a1.set_xticks([])
    a1.spines["bottom"].set_visible(False)
    a1.set_title("Les 6 taux de risque : 2010–2012 face à 2022–2024", loc="left")
    a1.legend(loc="lower right", fontsize=7, frameon=False, ncol=2)

    vue2 = USAGER.sort_values()
    y = np.arange(len(vue2))
    teinte = {"Deux et trois-roues motorisés": ROUGE_SERIE, "Piétons": ORANGE_SERIE,
              "Véhicules à 4 roues": THEME["Mobilité"], "Cyclistes": VERT_SERIE, "Autres et inconnus": GRIS_POINT}
    a2.barh(y, vue2.values, color=[teinte[i] for i in vue2.index], height=0.64)
    for i, (nom, v) in enumerate(vue2.items()):
        a2.text(v + 1.6, i, f"{fr(v)} %", va="center", fontsize=7.5, color=ENCRE, weight="bold")
    a2.set_yticks(y, [i.replace("Deux et trois-roues motorisés", "Deux et trois-roues\nmotorisés")
                      .replace("Autres et inconnus", "Autres et\ninconnus")
                      .replace("Véhicules à 4 roues", "Véhicules à\n4 roues") for i in vue2.index], fontsize=7)
    a2.set_xlim(0, 78)
    a2.set_xticks([])
    a2.spines["bottom"].set_visible(False)
    a2.set_title(f"Tués déclarés par type d’usager, {A_OMS}", loc="left")
    return _enregistrer(figure, "securite")


def graphique_reseau(w=8.0, h=1.82) -> Path:
    """Objectif 3 : les km relevés par état et par zone, et la part en mauvais état au bout de chaque barre."""
    etats = ["Bon", "Moyen", "Mauvais", "Travaux", "Non évalués"]
    colonnes = {"Bon": "Km en bon état", "Moyen": "Km en état moyen", "Mauvais": "Km en mauvais état",
                "Travaux": "Km en travaux", "Non évalués": "Km non évalués"}
    vue = ZONE_ROWS.loc[[z for z in ZONES if z in ZONE_ROWS.index]]
    vue = vue.iloc[::-1]
    figure, a = plt.subplots(figsize=(w, h))
    y = np.arange(len(vue))
    gauche = np.zeros(len(vue))
    for etat in etats:
        valeurs = vue[colonnes[etat]].fillna(0).values
        couleur = ETAT[etat if etat != "Non évalués" else "Non évalué"]
        a.barh(y, valeurs, left=gauche, color=couleur, height=0.62,
               label=etat.lower() if etat != "Non évalués" else "non évalué")
        for yi, (v, g) in enumerate(zip(valeurs, gauche)):
            if v > 55:
                a.text(g + v / 2, yi, fr(v, 0), ha="center", va="center", fontsize=6.5, color="white", weight="bold")
        gauche = gauche + valeurs
    for yi, (nom, total) in enumerate(zip(vue.index, gauche)):
        part = vue.loc[nom, "Part en mauvais état (%)"]
        a.text(total + 18, yi, f"{fr(part, 1)} %", va="center", fontsize=8, weight="bold", color=ROUGE_SERIE)
    a.set_yticks(y, [_nom_zone(n) for n in vue.index], fontsize=7.5)
    for etiquette, nom in zip(a.get_yticklabels(), vue.index):
        etiquette.set_color(COULEUR_ZONE[nom])
        etiquette.set_fontweight("bold")
    a.set_xlim(0, gauche.max() * 1.18)
    a.set_xlabel("Kilomètres relevés", fontsize=8)
    a.xaxis.set_major_formatter(lambda v, _: fr(v))
    a.legend(loc="upper center", bbox_to_anchor=(0.5, 1.10), fontsize=7.5, frameon=False, ncol=5,
             handlelength=1.1, columnspacing=1.4)
    _grille(a, "x")
    return _enregistrer(figure, "reseau")


def _prefectures_geo() -> gpd.GeoDataFrame:
    return gpd.read_file(GEO / "prefectures.geojson")[["Préfecture", "Zone", "Région", "geometry"]]


def _classes(valeurs: pd.Series, bornes: list[float]) -> list[str]:
    """Couleurs de la rampe BLEUS, en 5 classes fixes ; gris pour une valeur absente (pas de zéro inventé)."""
    sortie = []
    for v in valeurs:
        if pd.isna(v):
            sortie.append(GRIS_POINT)
            continue
        indice = sum(v >= b for b in bornes)
        sortie.append(BLEUS[min(indice, len(BLEUS) - 1)])
    return sortie


def carte_formation(w=2.3, h=3.9) -> Path:
    """Objectif 4 : les auto-écoles agréées pour 100 000 habitants, et les 272 auto-écoles recensées."""
    geo = _prefectures_geo().merge(
        P10[["Préfecture", "Formation — auto-écoles comptées", "Population"]], on="Préfecture")
    geo["pour100k"] = 1e5 * geo["Formation — auto-écoles comptées"] / geo["Population"]
    bornes = [0.001, 0.5, 1.0, 2.0]
    figure, a = plt.subplots(figsize=(w, h))
    geo.plot(ax=a, color=_classes(geo.pour100k, bornes), edgecolor="white", linewidth=0.4)
    ae = gpd.read_file(GEO / "auto_ecoles.geojson")
    agreees = ae[ae["Comptée (R-12)"]]
    autres = ae[~ae["Comptée (R-12)"]]
    autres.plot(ax=a, color="#8a8780", markersize=5, alpha=0.75, zorder=4)
    agreees.plot(ax=a, color=THEME["Couverture"], markersize=9, edgecolor="white", linewidth=0.3, zorder=5)
    geo.dissolve().boundary.plot(ax=a, color="#9a978f", linewidth=0.5)
    a.set_axis_off()
    libelles = ["aucune", "moins de 0,5", "0,5 à 1", "1 à 2", "2 ou plus"]
    poignees = [Patch(facecolor=BLEUS[i], edgecolor="#9a978f" if i == 0 else "none", linewidth=0.4, label=l)
                for i, l in enumerate(libelles)]
    poignees += [Line2D([0], [0], marker="o", ls="", markersize=6, markerfacecolor=THEME["Couverture"],
                        markeredgecolor="white", label=f"agréée ({len(agreees)})"),
                 Line2D([0], [0], marker="o", ls="", markersize=5, markerfacecolor="#8a8780",
                        markeredgecolor="none", label=f"non agréée ({len(autres)})")]
    a.legend(handles=poignees, loc="center left", bbox_to_anchor=(0.98, 0.5), fontsize=7.5, frameon=False,
             title="Auto-écoles agréées\npour 100 000 hab.", title_fontsize=7.5, alignment="left", labelspacing=0.8)
    return _enregistrer(figure, "carte_formation")


def carte_priorites(w=2.3, h=3.9) -> Path:
    """Les 39 préfectures par priorité du classement ; les 10 premières numérotées, celles qui cumulent cerclées."""
    geo = _prefectures_geo().merge(P10[["Préfecture", "Priorité", "Déficits"]], on="Préfecture")
    teinte = {"Haute": PRIORITE["Haute"], "Moyenne": PRIORITE["Moyenne"], "Aucune action": PRIORITE["Non classée"]}
    figure, a = plt.subplots(figsize=(w, h))
    geo.plot(ax=a, color=geo["Priorité"].map(teinte), edgecolor="white", linewidth=0.5)
    geo.dissolve().boundary.plot(ax=a, color="#9a978f", linewidth=0.5)
    points = geo.set_index("Préfecture").geometry.representative_point()
    for i, nom in enumerate(TOP10["Préfecture"], start=1):
        pt = points[nom]
        cumule = nom in set(CUMUL["Préfecture"])
        a.scatter(pt.x, pt.y, s=80, color="white", edgecolor=ROUGE_SERIE if cumule else NAVY,
                  linewidth=1.3 if cumule else 0.9, zorder=4)
        a.text(pt.x, pt.y, str(i), ha="center", va="center", fontsize=6, weight="bold",
               color=ROUGE_SERIE if cumule else NAVY, zorder=5)
    a.set_axis_off()
    comptes = geo["Priorité"].value_counts()
    poignees = [Patch(facecolor=teinte[k], edgecolor="#9a978f" if k == "Aucune action" else "none", linewidth=0.5,
                      label=f"{k.lower()} ({comptes.get(k, 0)})") for k in ["Haute", "Moyenne", "Aucune action"]]
    poignees += [Line2D([0], [0], marker="o", ls="", markersize=7, markerfacecolor="white",
                        markeredgecolor=ROUGE_SERIE, markeredgewidth=1.3,
                        label=f"cumule les deux\ndéficits ({len(CUMUL)})"),
                 Line2D([0], [0], marker="o", ls="", markersize=7, markerfacecolor="white", markeredgecolor=NAVY,
                        label="parmi les 10\npremières")]
    a.legend(handles=poignees, loc="center left", bbox_to_anchor=(0.98, 0.5), fontsize=7.5, frameon=False,
             title="Priorité", title_fontsize=8, alignment="left", labelspacing=0.8)
    return _enregistrer(figure, "carte_priorites")


def graphique_arbitrage(w=6.1, h=1.76) -> Path:
    """Rang du classement et habitants : l'intensité du manque et son volume ne vont pas ensemble."""
    vue = CLASSEES.merge(P10[["Préfecture", "Priorité", "Déficits"]], on="Préfecture")
    figure, a = plt.subplots(figsize=(w, h))
    a.axvspan(0.5, 10.5, color="#e8f0fb", zorder=0)
    a.axvline(10.5, color=NAVY, ls="--", lw=0.9)
    teinte = {"Haute": PRIORITE["Haute"], "Moyenne": PRIORITE["Moyenne"], "Aucune action": "#9a978f"}
    for k in ["Haute", "Moyenne", "Aucune action"]:
        g = vue[vue["Priorité"] == k]
        a.scatter(g["O5-02 rang"], g.Population / 1000, s=36, color=teinte[k], edgecolor="white", lw=0.6, zorder=3,
                  label=f"priorité {k.lower()} ({len(g)})" if k != "Aucune action" else f"aucune action ({len(g)})")
    for _, ligne in PLUS_PEUPLEES.iterrows():
        rang = ligne["O5-02 rang"]
        a.annotate(f"{ligne['Préfecture']} ({fr(ligne.Population / 1e6, 2)} M)", (rang, ligne.Population / 1000),
                   xytext=(8, -3), textcoords="offset points", fontsize=7.5, weight="bold", color=ENCRE)
    a.text(11.2, vue.Population.max() / 1000 * 0.98, "les 10 premières\ndu classement", fontsize=7.5, color=NAVY,
           weight="bold", va="top")
    a.set_xlim(0.5, len(vue) + 0.5)
    a.set_ylim(0, vue.Population.max() / 1000 * 1.10)
    a.set_xlabel("Rang du classement (1 = la préfecture la plus mal servie)", fontsize=8)
    a.set_ylabel("Habitants (milliers)", fontsize=8)
    a.yaxis.set_major_formatter(lambda v, _: fr(v))
    _grille(a, "both")
    a.legend(loc="upper right", fontsize=7, frameon=False)
    return _enregistrer(figure, "arbitrage")


def rasteriser_armoiries() -> Path:
    """`python-pptx` ne lit pas le SVG : les armoiries du tableau de bord sont rasterisées une fois."""
    sortie = ASSETS / "armoiries.png"
    subprocess.run(["rsvg-convert", "-a", "-w", "420",
                    str(RACINE / "dashboard" / "static" / "armoiries-togo-ecu.svg"), "-o", str(sortie)], check=True)
    return sortie


ARMOIRIES: Path = ASSETS / "armoiries.png"


# --------------------------------------------------------------------------------------------------------------------
# Les dix diapositives
# --------------------------------------------------------------------------------------------------------------------

def diapo_couverture(prs) -> None:
    """Couverture = synthèse exécutive : le résultat avant la méthode."""
    d = nouvelle_diapositive(prs)
    rect(d, 0, 0, SW, SH, fond=NAVY)

    carte(d, M, 0.40, 0.94, 0.94, bord=OR)
    image_ajustee(d, ARMOIRIES, M + 0.09, 0.49, 0.76, 0.76)
    haut, _, bas = MINISTERE.partition(" et de la ")
    lignes = [T(haut.upper(), taille=10.5, gras=True, couleur=BLANC)]
    if bas:
        lignes.append(T(f"ET DE LA {bas.upper()}", taille=10.5, gras=True, couleur=BLANC, avant=2))
    bloc(d, M + 1.14, 0.46, 6.2, 0.82, lignes, ancre=MSO_ANCHOR.MIDDLE)
    bloc(d, 7.5, 0.50, DROITE - 7.5, 0.40, [T(MARQUE, taille=16, gras=True, couleur=JAUNE, police=POLICE_TITRE)],
         align=PP_ALIGN.RIGHT)
    bloc(d, 7.5, 0.94, DROITE - 7.5, 0.28, [T(BANDEAU, taille=10.5, couleur=BLEU_CLAIR_TEXTE)], align=PP_ALIGN.RIGHT)

    bloc(d, M, 1.62, CW, 0.60, [T("Mobilité et sécurité routière au Togo", taille=34, gras=True, couleur=BLANC,
                                  police=POLICE_TITRE)])
    bloc(d, M, 2.26, CW, 0.34, [T("Où agir en priorité pour une mobilité plus sûre ?", taille=15,
                                  couleur=BLEU_CLAIR_TEXTE)])

    y, h, gap = 2.80, 1.70, 0.22
    w = (CW - 3 * gap) / 4
    cartes = [
        dict(surtitre_txt=f"Mobilité ({A_IMM})", valeur=nb(IMM_TOT), unite="véhicules",
             phrase="immatriculés dans l’année",
             note=f"× {nb(MULT, 2)} entre {A_MULT - 20} et {A_MULT} ; {pct(PART_MOTO)} de motos",
             etiquette="En hausse", ton="alerte", couleur_valeur=THEME_TEXTE["Mobilité"]),
        dict(surtitre_txt="Sécurité routière", valeur=nb(TUES), unite="tués",
             phrase=f"déclarés en {A_ACC}, pour {nb(ACCIDENTS)} accidents constatés",
             note=f"volume en hausse, mais les {len(RATIOS)} taux de risque baissent",
             etiquette="Taux en baisse", ton="ok", couleur_valeur=TONS["rouge"]["encre"]),
        dict(surtitre_txt=f"Réseau (relevé de {A_RELEVE})", valeur=pct(PART_MAUVAIS),
             phrase="des kilomètres évalués en mauvais état",
             note=f"{nb(KM_MAUVAIS, 2)} km sur {nb(KM_EVALUES, 0)} ; {N_CRITIQUES} tronçons critiques",
             etiquette="Inégal", ton="alerte", couleur_valeur=THEME_TEXTE["Réseau"]),
        dict(surtitre_txt="Formation", valeur=f"{len(SANS_AE)} sur {len(P10)}", unite="préfectures",
             phrase="sans aucune auto-école agréée",
             note=f"{nb(POP_SANS_AE)} habitants ; {AE_AGREEES} agréées sur {AE_RECENSEES} recensées",
             etiquette="Priorité", ton="critique", couleur_valeur=THEME_TEXTE["Couverture"]),
    ]
    for i, c in enumerate(cartes):
        cartouche(d, M + i * (w + gap), y, w, h, **c)

    banniere(d, M, 4.62, CW, 0.62, "Constat",
             [T("Plus de véhicules, pas une route plus dangereuse : ", gras=True),
              T(f"le volume des accidents monte de {pct(HAUSSE_ACC)} entre 2010–2012 et 2022–2024, mais les "
                f"{len(RATIOS)} taux de risque baissent de {pct(abs(RATIOS['Variation (%)']).min())} à "
                f"{pct(abs(RATIOS['Variation (%)']).max())}. Le manque est rural : réseau dégradé et formation "
                f"absente.", gras=False)], "constat", taille=11.5)
    banniere(d, M, 5.36, CW, 0.62, "Dans l’année",
             f"créer la base d’accidents par préfecture — {N_NON_TESTABLES} questions restent sans réponse faute "
             f"de ces données — et vérifier sur place l’état du réseau relevé en {A_RELEVE} avant d’engager les "
             f"travaux.", "limite", taille=11.5)

    surtitre(d, M, 6.20, 4.5, "Présenté par", couleur=JAUNE)
    bloc(d, M, 6.44, 4.5, 0.36, [T(PRESENTE_PAR, taille=16, gras=True, couleur=BLANC)])
    if URL_DASHBOARD:
        surtitre(d, 5.2, 6.20, DROITE - 5.2, "Tableau de bord interactif", couleur=JAUNE)
        lien(d, 5.2, 6.46, DROITE - 5.2, URL_DASHBOARD, URL_DASHBOARD, taille=12, couleur=BLEU_CLAIR_TEXTE)
    else:
        surtitre(d, 5.2, 6.20, DROITE - 5.2, "Livrables", couleur=JAUNE)
        bloc(d, 5.2, 6.44, DROITE - 5.2, 0.30,
             [T("Tableau de bord interactif en 8 pages, et ce rapport", taille=12, couleur=BLEU_CLAIR_TEXTE)])
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
            "novembre", "décembre"]
    aujourd_hui = datetime.date.today()
    bloc(d, M, PIED_Y, 7.4, 0.24, [T(f"{PIED_IDENTITE}  ·  {ATTRIBUTION}", taille=8.5, couleur="#9fb2c6")])
    bloc(d, DROITE - 3.0, PIED_Y, 3.0, 0.24, [T(f"{mois[aujourd_hui.month - 1].capitalize()} {aujourd_hui.year}",
                                                taille=8.5, couleur="#9fb2c6")], align=PP_ALIGN.RIGHT)


def diapo_methode(prs) -> None:
    """La seule diapositive de méthode, volontairement courte."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 2, "01 · Cadrage et méthode", "Comment ces résultats ont-ils été produits ?")

    banniere(d, M, y, CW, 0.60, "Question publique",
             "Où agir en priorité pour une mobilité plus sûre : quel territoire, quel manque, pour combien "
             "d’habitants ?", "sombre", taille=12.5)

    surtitre(d, M, y + 0.80, CW, "La chaîne de traitement")
    etapes = [
        ("Données publiques", f"immatriculations et permis depuis 1990, accidents, réseau routier, auto-écoles, "
                              f"recensement de {A_ACC}"),
        ("Diagnostic", f"les 5 objectifs de l’énoncé, {N_HYP} vérifications et hypothèses, lus dans {len(P10)} "
                       f"préfectures, {len(ZONES)} zones et {len(COULEUR_REGION)} régions"),
        ("Priorisation", f"un classement des {len(CLASSEES)} préfectures évaluables, sur deux dimensions, puis la "
                         f"nature du manque"),
        ("Recommandations", f"{N_RECO} actions, chacune avec son territoire, sa cible chiffrée, ses habitants et "
                            f"son horizon"),
    ]
    gap = 0.36
    w = (CW - 3 * gap) / 4
    for i, (titre, detail) in enumerate(etapes):
        x = M + i * (w + gap)
        carte(d, x, y + 1.10, w, 1.14)
        carre_numero(d, x + 0.18, y + 1.26, 0.34, str(i + 1), NAVY, taille=12)
        bloc(d, x + 0.62, y + 1.23, w - 0.78, 0.40, [T(titre, taille=13, gras=True, couleur=NAVY, police=POLICE_TITRE)],
             ancre=MSO_ANCHOR.MIDDLE)
        bloc(d, x + 0.18, y + 1.66, w - 0.36, 0.50, [T(detail, taille=9.5, couleur=ENCRE2, interligne=1.05)])
        if i < 3:
            bloc(d, x + w + 0.02, y + 1.46, gap - 0.04, 0.34, [T("→", taille=16, gras=True, couleur=GRIS_POINT)],
                 align=PP_ALIGN.CENTER)

    surtitre(d, M, y + 2.46, CW, f"Deux dimensions pour classer les {len(CLASSEES)} préfectures")
    dimensions = [
        ("Réseau", "État du réseau routier", f"part des kilomètres évalués en mauvais état ; cible : "
                                             f"{pct(14.35, 2)}, la médiane nationale"),
        ("Couverture", "Offre de formation", f"auto-écoles agréées pour 100 000 habitants ; cible : "
                                             f"{nb(1.065, 3)}, la médiane des préfectures équipées"),
    ]
    gap = 0.26
    w = (CW - gap) / 2
    for i, (cle, titre, detail) in enumerate(dimensions):
        x = M + i * (w + gap)
        carte(d, x, y + 2.76, w, 0.86)
        rect(d, x, y + 2.76, 0.07, 0.86, fond=THEME[cle if cle != "Réseau" else "Réseau"], rayon=0.03)
        bloc(d, x + 0.26, y + 2.86, w - 0.46, 0.30,
             [T(titre, taille=13, gras=True, couleur=THEME_TEXTE[cle], police=POLICE_TITRE)])
        bloc(d, x + 0.26, y + 3.18, w - 0.46, 0.36, [T(detail, taille=10, couleur=ENCRE2, interligne=1.05)])

    encadre(d, M, y + 3.78, CW, 0.74, "limite",
            [T("À retenir : ", couleur=TONS["limite"]["encre"]),
             T("le classement mesure l’intensité du manque, pas le risque d’accident — les accidents ne sont "
               "publiés qu’au niveau national. L’état du réseau vient d’un relevé de "),
             T(str(A_RELEVE), couleur=NAVY),
             T(" dont la méthode de notation n’est pas publiée : c’est une estimation, à vérifier sur place avant "
               "tout investissement.")], taille=11)
    pied(d)


def diapo_mobilite(prs, graphiques) -> None:
    """Objectif 1 : retracer les immatriculations et les permis."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 3, "02 · Objectif 1 — Mobilité",
                "Le parc immatriculé a plus que quadruplé en vingt ans, porté par les motos")

    gap = 0.22
    w = (CW - 3 * gap) / 4
    chiffres = [
        (f"× {nb(MULT, 2)}", f"d’immatriculations annuelles entre {A_MULT - 20} et {A_MULT}", THEME_TEXTE["Mobilité"]),
        (pct(PART_MOTO), f"de motos en {A_IMM} : {nb(IMM_MOTO)} sur {nb(IMM_TOT)}", SERIE["Moto"]),
        (pct(CONTRIB_MOTO), f"de la hausse de {A_MULT - 20} à {A_MULT} vient des motos", SERIE["Moto"]),
        (nb(PERMIS_TOT), f"permis délivrés en {A_PER}, dont {nb(PERMIS['A'])} permis moto", NAVY),
    ]
    for i, (valeur, phrase, couleur) in enumerate(chiffres):
        x = M + i * (w + gap)
        carte(d, x, y, w, 0.96)
        bloc(d, x + 0.18, y + 0.12, w - 0.36, 0.42,
             [T(valeur, taille=taille_ajustee(valeur, w - 0.36, (24, 22, 20, 18)), gras=True, couleur=couleur,
                police=POLICE_TITRE)])
        bloc(d, x + 0.18, y + 0.56, w - 0.36, 0.34, [T(phrase, taille=9.5, couleur=ENCRE2, interligne=1.05)])

    y_fig = y + 1.12
    h_fig = 2.72
    w_fig = 8.30
    sous = panneau(d, M, y_fig, w_fig, h_fig, "Immatriculations et permis",
                   sous_titre=f"Immatriculations de l’année, 1990–{A_IMM} ; permis délivrés en {A_PER}. "
                              f"Niveau : mesuré.")
    image_ajustee(d, graphiques["mobilite"], M + 0.14, sous, w_fig - 0.28, y_fig + h_fig - sous - 0.14)

    x_droite = M + w_fig + 0.25
    w_droite = DROITE - x_droite
    encadre(d, x_droite, y_fig, w_droite, 1.30, "bleu",
            [T("Constat  ·  ", couleur=NAVY),
             T(f"en cumul sur {A_CUMUL}, "),
             T(f"{nb(RATIO_CUM['A'], 0)} motos", couleur=SERIE["Moto"]),
             T(" ont été immatriculées pour un permis moto délivré, contre "),
             T(f"{nb(RATIO_CUM['B'], 1)}", couleur=SERIE["Voiture"]),
             T(" pour les voitures. Le permis moto a bondi : "),
             T(f"{nb(PERMIS['A'])}", couleur=SERIE["Moto"]),
             T(f" en {A_PER}, contre {nb(PERMIS_A_AVANT.loc[A_AVANT])} en {A_AVANT}.")], taille=10.5)
    encadre(d, x_droite, y_fig + 1.42, w_droite, 1.30, "ambre",
            [T("Enjeu  ·  ", couleur=TONS["ambre"]["encre"]),
             T("la formation doit cibler d’abord le permis moto : c’est la catégorie où l’écart entre véhicules "
               "immatriculés et conducteurs formés est le plus large, et celle qui porte la hausse du parc.")],
            taille=10.5)

    banniere(d, M, y_fig + h_fig + 0.18, CW, 0.62, "Synthèse chiffrée",
             f"{nb(IMM_TOT)} véhicules immatriculés en {A_IMM}, dont {pct(PART_MOTO)} de motos · × {nb(MULT, 2)} "
             f"en vingt ans · {nb(PERMIS_TOT)} permis délivrés en {A_PER}, de {len(CAT_PERMIS)} catégories.",
             "constat", taille=11.5)
    encadre(d, M, y_fig + h_fig + 0.86, CW, 0.68, "limite",
            [T("Limite  ·  ", couleur=TONS["limite"]["encre"]),
             T(f"ce sont les immatriculations de l’année, pas le parc en circulation, qui n’est pas publié. "
               f"Les séries connaissent deux ruptures, en 1995 et en 2004 : le multiplicateur est daté. "
               f"Les permis ne sont publiés ni par territoire, ni par âge.")], taille=10.5, gras=False)
    pied(d)


def diapo_securite(prs, graphiques) -> None:
    """Objectif 2 : analyser la sécurité routière, rapportée à la population et aux véhicules."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 4, "03 · Objectif 2 — Sécurité routière", "Plus de véhicules, pas une route plus dangereuse")

    gap = 0.22
    w = (CW - 3 * gap) / 4
    tues_vehicule = RATIOS[(RATIOS.Mesure == "Tués") & (RATIOS.Lecture == "pour 10 000 véhicules")].iloc[0]
    tues_habitant = RATIOS[(RATIOS.Mesure == "Tués") & (RATIOS.Lecture == "pour 100 000 habitants")].iloc[0]
    chiffres = [
        (f"+ {pct(HAUSSE_ACC)}", f"d’accidents constatés en volume entre 2010–2012 et 2022–2024", ORANGE_SERIE),
        (pct(tues_vehicule["Variation (%)"]), "de tués pour 10 000 véhicules sur les mêmes périodes", VERT_SERIE),
        (pct(PART_2ROUES, 0), f"des tués de {A_OMS} sont des usagers de deux et trois-roues motorisés", ROUGE_SERIE),
        (nb(TUES_HAB_2021, 2), f"tués déclarés pour 100 000 habitants en {A_OMS}, contre {nb(OMS_2021, 1)} estimés "
                               f"par l’OMS", NAVY),
    ]
    for i, (valeur, phrase, couleur) in enumerate(chiffres):
        x = M + i * (w + gap)
        carte(d, x, y, w, 0.96)
        bloc(d, x + 0.18, y + 0.12, w - 0.36, 0.42,
             [T(valeur, taille=taille_ajustee(valeur, w - 0.36, (24, 22, 20, 18)), gras=True, couleur=couleur,
                police=POLICE_TITRE)])
        bloc(d, x + 0.18, y + 0.56, w - 0.36, 0.34, [T(phrase, taille=9.5, couleur=ENCRE2, interligne=1.05)])

    y_fig = y + 1.12
    h_fig = 2.72
    w_fig = 8.30
    sous = panneau(d, M, y_fig, w_fig, h_fig, "Le risque routier, rapporté à la population et aux véhicules",
                   sous_titre="Accidents constatés, blessés et tués déclarés : volume, pour 100 000 habitants et "
                              "pour 10 000 véhicules. Niveau : estimé pour les taux.")
    image_ajustee(d, graphiques["securite"], M + 0.14, sous, w_fig - 0.28, y_fig + h_fig - sous - 0.14)

    x_droite = M + w_fig + 0.25
    w_droite = DROITE - x_droite
    encadre(d, x_droite, y_fig, w_droite, 1.30, "bleu",
            [T("Constat  ·  ", couleur=NAVY),
             T(f"les {len(RATIOS)} taux de risque baissent, de "),
             T(pct(abs(RATIOS["Variation (%)"]).min()), couleur=VERT_SERIE),
             T(" à "), T(pct(abs(RATIOS["Variation (%)"]).max()), couleur=VERT_SERIE),
             T(f". Les tués pour 100 000 habitants passent de {nb(tues_habitant['Moyenne 2010–2012'], 2)} à "
               f"{nb(tues_habitant['Moyenne 2022–2024'], 2)}. La hausse du volume vient de l’exposition, "
               f"pas d’une route devenue plus dangereuse.")], taille=10.5)
    encadre(d, x_droite, y_fig + 1.42, w_droite, 1.30, "ambre",
            [T("Enjeu  ·  ", couleur=TONS["ambre"]["encre"]),
             T(f"les deux-roues motorisés font {pct(PART_2ROUES, 0)} des tués, un peu plus que leur part du parc "
               f"estimé : casque, permis moto et contrôle sont les leviers nationaux.")], taille=10.5)

    banniere(d, M, y_fig + h_fig + 0.18, CW, 0.62, "Synthèse chiffrée",
             f"{nb(ACCIDENTS)} accidents constatés, {nb(BLESSES)} blessés et {nb(TUES)} tués déclarés en {A_ACC} · "
             f"{len(RATIOS)} taux de risque sur {len(RATIOS)} en baisse · {pct(PART_2ROUES, 0)} des tués de "
             f"{A_OMS} sont des usagers de deux et trois-roues motorisés.", "constat", taille=11.5)
    encadre(d, M, y_fig + h_fig + 0.86, CW, 0.68, "limite",
            [T("Limite  ·  ", couleur=TONS["limite"]["encre"]),
             T(f"ce sont des accidents déclarés par la police et la gendarmerie, publiés pour tout le pays "
               f"seulement : ni préfecture, ni mois, ni âge. Les taux par véhicule dépendent d’un parc estimé. "
               f"Une baisse des déclarations ressemblerait à un progrès.")], taille=10.5, gras=False)
    pied(d)


def diapo_reseau(prs, graphiques) -> None:
    """Objectif 3 : évaluer l'état du réseau par tronçon et par territoire."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 5, "04 · Objectif 3 — Réseau routier",
                f"Un réseau inégalement entretenu : {pct(PART_MAUVAIS)} des kilomètres évalués en mauvais état")

    gap = 0.22
    w = (CW - 3 * gap) / 4
    chiffres = [
        (f"{nb(KM_EVALUES, 0)} km", f"évalués sur {N_TRONCONS} tronçons, relevé de {A_RELEVE}", NAVY),
        (pct(PART_MAUVAIS), f"en mauvais état, soit {nb(KM_MAUVAIS, 2)} km", ROUGE_SERIE),
        (str(N_CRITIQUES), f"tronçons critiques, qui portent au moins un kilomètre en mauvais état",
         THEME_TEXTE["Réseau"]),
        (f"{nb(ECART_ZONES, 1)} pts", f"d’écart entre la {ZONE_PIRE} et le {ZONE_MEILLEURE}",
         COULEUR_ZONE[ZONE_PIRE]),
    ]
    for i, (valeur, phrase, couleur) in enumerate(chiffres):
        x = M + i * (w + gap)
        carte(d, x, y, w, 0.96)
        bloc(d, x + 0.18, y + 0.12, w - 0.36, 0.42,
             [T(valeur, taille=taille_ajustee(valeur, w - 0.36, (24, 22, 20, 18)), gras=True, couleur=couleur,
                police=POLICE_TITRE)])
        bloc(d, x + 0.18, y + 0.56, w - 0.36, 0.34, [T(phrase, taille=9.5, couleur=ENCRE2, interligne=1.05)])

    y_fig = y + 1.12
    h_fig = 2.72
    w_fig = 8.30
    sous = panneau(d, M, y_fig, w_fig, h_fig, "L’état du réseau relevé, zone par zone",
                   sous_titre=f"Kilomètres relevés en {A_RELEVE}, par état ; en rouge, la part en mauvais état. "
                              f"Niveau : estimé — méthode de notation non publiée.")
    image_ajustee(d, graphiques["reseau"], M + 0.14, sous, w_fig - 0.28, y_fig + h_fig - sous - 0.14)

    x_droite = M + w_fig + 0.25
    w_droite = DROITE - x_droite
    encadre(d, x_droite, y_fig, w_droite, 1.30, "bleu",
            [T("Constat  ·  ", couleur=NAVY),
             T("la "), Z(ZONE_PIRE), T(f" a {pct(ZONE_ROWS.loc[ZONE_PIRE, 'Part en mauvais état (%)'])} de ses "
                                       f"kilomètres évalués en mauvais état, le "),
             Z(ZONE_MEILLEURE), T(f" {pct(ZONE_ROWS.loc[ZONE_MEILLEURE, 'Part en mauvais état (%)'])}. L’entretien "
                                  f"se cible par territoire ; la vérification, elle, se fait tronçon par tronçon.")],
            taille=10.5)
    encadre(d, x_droite, y_fig + 1.42, w_droite, 1.30, "limite",
            [T("Réserve  ·  ", couleur=TONS["limite"]["encre"]),
             T(f"une autre publication de {A_RELEVE} donne {pct(ANNUAIRE_MAUVAIS, 2)} des routes nationales en "
               f"mauvais état, contre {pct(PART_MAUVAIS)} au relevé. Aucune des deux ne concorde : les deux sont "
               f"citées, jamais mêlées.")], taille=10.5)

    banniere(d, M, y_fig + h_fig + 0.18, CW, 0.62, "Synthèse chiffrée",
             f"{nb(KM_EVALUES, 0)} km évalués sur {N_TRONCONS} tronçons · {nb(KM_MAUVAIS, 2)} km en mauvais état "
             f"({pct(PART_MAUVAIS)}) · {N_CRITIQUES} tronçons critiques · {N_RESEAU} préfectures au-delà du seuil, "
             f"{nb(POP_RESEAU)} habitants · {nb(KM_A_REMETTRE, 1)} km à remettre en état pour atteindre la médiane.",
             "constat", taille=11.5)
    encadre(d, M, y_fig + h_fig + 0.86, CW, 0.68, "limite",
            [T("Limite  ·  ", couleur=TONS["limite"]["encre"]),
             T(f"{MO['Préfecture']} n’a aucune route classée : sa part en mauvais état n’est pas définie, elle "
               f"n’est pas nulle. {pct(float(PAYS['O3-06']))} du réseau tracé n’a pas d’état relevé. Aucune donnée "
               f"ne mesure l’usure depuis {A_RELEVE}.")], taille=10.5, gras=False)
    pied(d)


def diapo_couverture_formation(prs, graphiques) -> None:
    """Objectif 4 : cartographier le réseau et les auto-écoles, rapportés à la population."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 6, "05 · Objectif 4 — Couverture", "La formation des conducteurs s’arrête aux villes")

    x_carte = M
    w_carte = 2.95
    h_carte = 4.36
    sous = panneau(d, x_carte, y, w_carte, h_carte, "Les auto-écoles agréées",
                   sous_titre=f"Auto-écoles agréées pour 100 000 habitants, {A_ACC}. Niveau : estimé.")
    image_ajustee(d, graphiques["carte_formation"], x_carte + 0.12, sous, w_carte - 0.24, y + h_carte - sous - 0.12)

    x = x_carte + w_carte + 0.25
    w = DROITE - x
    gap = 0.20
    wk = (w - 2 * gap) / 3
    chiffres = [
        (f"{AE_AGREEES} / {AE_RECENSEES}", "auto-écoles agréées sur les auto-écoles recensées",
         THEME_TEXTE["Couverture"]),
        (f"{len(SANS_AE)} sur {len(P10)}", f"préfectures sans auto-école agréée · {nb(POP_SANS_AE)} habitants",
         TONS["rouge"]["encre"]),
        (pct(PART_AE_URBAIN), f"des auto-écoles agréées dans {len(URBAINES)} préfectures urbaines, qui comptent "
                              f"{pct(PART_POP_URBAIN)} de la population", NAVY),
    ]
    for i, (valeur, phrase, couleur) in enumerate(chiffres):
        xi = x + i * (wk + gap)
        carte(d, xi, y, wk, 1.18)
        bloc(d, xi + 0.18, y + 0.12, wk - 0.36, 0.42,
             [T(valeur, taille=taille_ajustee(valeur, wk - 0.36, (24, 22, 20, 18)), gras=True, couleur=couleur,
                police=POLICE_TITRE)])
        bloc(d, xi + 0.18, y + 0.56, wk - 0.36, 0.56, [T(phrase, taille=9.5, couleur=ENCRE2, interligne=1.05)])

    surtitre(d, x, y + 1.30, w, "Trois manques, trois actions")
    manques = [
        ("rouge", f"{len(SANS_AUCUNE)} préfectures sans aucune auto-école, même non agréée",
         f"{nb(int(SANS_AUCUNE.Population.sum()))} habitants · {int(SANS_AUCUNE['Formation — auto-écoles à ouvrir'].sum())} "
         f"auto-écoles à ouvrir", "Ouvrir"),
        ("ambre", f"{len(NON_AGREEES)} préfectures où les auto-écoles recensées ne sont pas agréées",
         f"{nb(int(NON_AGREEES.Population.sum()))} habitants · "
         f"{int(NON_AGREEES['Formation — auto-écoles recensées'].sum())} auto-écoles à vérifier", "Vérifier"),
        ("navy", f"{N_RESEAU} préfectures au réseau dégradé, dont {len(CUMUL)} qui cumulent les deux manques",
         f"{nb(POP_RESEAU)} habitants · {nb(KM_A_REMETTRE, 1)} km à remettre en état", "Remettre en état"),
    ]
    h, g = 0.70, 0.07
    for i, (ton, titre, detail, action) in enumerate(manques):
        yi = y + 1.56 + i * (h + g)
        carte(d, x, yi, w, h)
        rect(d, x, yi, 0.07, h, fond=TONS[ton]["encre"], rayon=0.03)
        bloc(d, x + 0.24, yi + 0.08, w - 2.30, 0.32, [T(titre, taille=11, gras=True, couleur=ENCRE, interligne=1.02)])
        bloc(d, x + 0.24, yi + 0.42, w - 2.30, 0.24, [T(detail, taille=9.5, couleur=ENCRE2)])
        pastille(d, x + w - 0.20, yi + 0.21, action, ton, taille=10, h=0.28, droite=True)

    banniere(d, x, y + 1.56 + 3 * (h + g) + 0.02, w, 0.52, "Le trait commun",
             f"la distance : {len(LOIN)} préfectures ont leur chef-lieu à plus de {SEUIL_DISTANCE} km de la "
             f"première auto-école agréée, et {pct(ACCES_RURAL)} seulement des ruraux vivent à moins de 2 km "
             f"d’une route revêtue.", "sombre", taille=11)

    encadre(d, M, y + h_carte + 0.16, CW, 0.72, "limite",
            [T("Limite  ·  ", couleur=TONS["limite"]["encre"]),
             T(f"l’activité des auto-écoles n’est pas publiée : une auto-école agréée n’est pas forcément active, "
               f"et les points recensés sont des lieux, pas des agents. L’accès rural est estimé avec une "
               f"population répartie uniformément dans chaque préfecture.")], taille=10.5, gras=False)
    pied(d)


def diapo_territoires(prs, graphiques) -> None:
    """Objectif 5 : où agir en priorité, et sur quel manque."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 7, "06 · Objectif 5 — Territoires", "Où agir en priorité ?")

    x_carte = M
    w_carte = 2.95
    h_carte = 4.36
    sous = panneau(d, x_carte, y, w_carte, h_carte, "Les 39 préfectures par priorité",
                   sous_titre="Les 10 premières du classement sont numérotées ; cerclées en rouge, celles qui "
                              "cumulent les deux manques.")
    image_ajustee(d, graphiques["carte_priorites"], x_carte + 0.12, sous, w_carte - 0.24, y + h_carte - sous - 0.12)

    x = x_carte + w_carte + 0.25
    w = DROITE - x
    surtitre(d, x, y, w, f"Les 10 premières préfectures · {nb(POP_TOP10)} habitants")
    nature = {"réseau ; formation": ("réseau et formation", "rouge"), "formation": ("formation d’abord", "navy"),
              "réseau": ("réseau d’abord", "ambre")}
    parts = [0.058, 0.138, 0.228, 0.112, 0.160, 0.106, 0.198]
    titres = ["Rang", "Préfecture", "Zone", "Habitants", "Mauvais état\n(km évalués)", "Auto-écoles\nagréées",
              "Nature du manque"]
    aligns = [PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.CENTER,
              PP_ALIGN.LEFT]
    colonnes = list(zip(titres, [round(f * w, 3) for f in parts], aligns))
    lignes = []
    for _, r in TOP10.iterrows():
        libelle, ton = nature[r["Leviers"]]
        part = r["O3-02"]
        lignes.append([
            (str(int(r["O5-02 rang"])), ENCRE2, True),
            (r["Préfecture"], ENCRE, True),
            (r["Zone"], COULEUR_ZONE[r["Zone"]], True),
            nb(r["Population"]),
            (f"{pct(part)}  ({nb(r['Km évalués'], 0)} km)", ROUGE_SERIE if part >= 14.35 else ENCRE, part >= 14.35),
            (nb(r["Auto-écoles comptées"]), ENCRE, False),
            (libelle, TONS[ton]["encre"], True),
        ])
    fin = tableau_texte(d, x, y + 0.26, w, colonnes, lignes, taille=9.5, h_ligne=0.285)

    encadre(d, x, fin + 0.12, w, 0.84, "bleu",
            [T("Constat  ·  ", couleur=NAVY),
             T(f"{len(CUMUL)} préfectures cumulent un réseau dégradé et aucune auto-école agréée — "),
             T(et(CUMUL["Préfecture"]), couleur=TONS["rouge"]["encre"]),
             T(f" —, soit {nb(POP_CUMUL)} habitants, {nb(KM_CUMUL, 1)} km à remettre en état et {AE_CUMUL} "
               f"auto-écoles à ouvrir.")], taille=10.5)

    encadre(d, M, y + h_carte + 0.14, CW, 0.76, "limite",
            [T("Hors classement  ·  ", couleur=TONS["limite"]["encre"]),
             T(f"{MO['Préfecture']} n’a aucune route classée — ni état, ni kilomètre évalué — et aucune "
               f"auto-école, ni agréée ni recensée, pour {nb(MO['Population'])} habitants, à "
               f"{nb(MO['Formation — distance à la plus proche (km)'], 1)} km de la plus proche. Elle n’entre pas "
               f"dans le classement : elle est traitée à part.")], taille=10.5, gras=False)
    pied(d)


def diapo_arbitrage(prs, graphiques) -> None:
    """L'arbitrage : l'intensité du manque n'est pas le volume de population, et la règle qui tranche."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 8, "07 · Arbitrage", "Priorité n’est pas population")

    w_fig = 6.40
    h_fig = 2.62
    sous = panneau(d, M, y, w_fig, h_fig, "Rang du classement et habitants",
                   sous_titre="Une préfecture par point ; les 10 premières sur fond bleu.")
    image_ajustee(d, graphiques["arbitrage"], M + 0.14, sous, w_fig - 0.28, y + h_fig - sous - 0.14)

    x = M + w_fig + 0.25
    w = DROITE - x
    encadre(d, x, y, w, 1.42, "bleu",
            [T("Ce que montre le nuage  ·  ", couleur=NAVY),
             T(f"les {len(TOP10)} premières comptent {nb(POP_TOP10)} habitants, "),
             T(pct(100 * POP_TOP10 / POPULATION), couleur=NAVY),
             T(" du pays. "),
             T(et(HORS_TOP10), couleur=TONS["rouge"]["encre"]),
             T(f", les deux préfectures les plus peuplées, n’en font pas partie : "
               f"{AGOE['Préfecture']} a {nb(AGOE['Réseau — km à remettre en état'], 1)} km à remettre en état pour "
               f"{nb(AGOE['Population'])} habitants.")], taille=10.5)

    surtitre(d, x, y + 1.46, w, "Les deux règles qui tranchent")
    regles = [
        ("rouge", "La préfecture sans aucune auto-école agréée passe en premier, quelle que soit sa population."),
        ("navy", "À score égal, la préfecture la plus peuplée passe devant."),
    ]
    for i, (ton, texte) in enumerate(regles):
        yi = y + 1.72 + i * 0.62
        carte(d, x, yi, w, 0.56)
        carre_numero(d, x + 0.16, yi + 0.12, 0.34, str(i + 1), TONS[ton]["encre"], taille=12)
        bloc(d, x + 0.60, yi + 0.08, w - 0.78, 0.42, [T(texte, taille=10.5, couleur=ENCRE, interligne=1.05)],
             ancre=MSO_ANCHOR.MIDDLE)

    y_tests = y + h_fig + 0.20
    surtitre(d, M, y_tests, CW, f"Le classement tient-il ? {len(TESTS) - 1} tests de robustesse")
    colonnes = [("Ce que le test change", 4.60, PP_ALIGN.LEFT),
                ("Changements parmi les 10 premières", 2.10, PP_ALIGN.CENTER),
                ("Entrent", 2.70, PP_ALIGN.LEFT), ("Sortent", 2.83, PP_ALIGN.LEFT)]
    libelles = {"T1": "Le réseau compte pour deux tiers du score",
                "T2": "La formation compte pour deux tiers du score",
                "T3": "Écart à la médiane, au lieu du rang",
                "T4": f"Sans {et(list(PLUS_PEUPLEES['Préfecture']))}, les plus peuplées",
                "T5": "Distance à l’auto-école, au lieu du nombre d’auto-écoles"}
    lignes = []
    for _, r in TESTS_REELS.iterrows():
        lignes.append([libelles[r["Test"]], (nb(r["Changements parmi les 10 premières"]), NAVY, True),
                       (r["Entrées"], VERT_SERIE, True), (r["Sorties"], ROUGE_SERIE, True)])
    tableau_texte(d, M, y_tests + 0.26, CW, colonnes, lignes, taille=10, h_ligne=0.275)

    banniere(d, M, PIED_Y - 0.72, CW, 0.58, "Le classement est stable",
             f"aucun test ne change plus de {MAX_CHANGEMENTS} des {len(TOP10)} premières, et {len(TOUJOURS)} "
             f"préfectures y restent dans les {N_TESTS} tests : {et(TOUJOURS['Préfecture'])}.", "sombre", taille=11.5)
    pied(d)


def diapo_plan(prs) -> None:
    """LA diapositive centrale : le plan d'action ordonné. Chaque effectif est lu dans les tables."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 9, "08 · Plan d’action", "Par où commencer ?")
    r_d1, r_r1, r_f1, r_f2, r_s1, r_z3 = (R10.loc[c] for c in ["REC-D1", "REC-R1", "REC-F1", "REC-F2", "REC-S1",
                                                               "REC-Z3"])
    actions = [
        ("rouge", "Créer la base d’accidents par préfecture, et vérifier l’état relevé sur place",
         f"Les accidents ne sont publiés que pour tout le pays : {N_NON_TESTABLES} questions restent sans réponse. "
         f"La vérification de l’état conditionne tous les travaux.",
         [("1 an", "ambre"), ("Préalable", "rouge")], "tout le pays",
         "Organisme chargé de la sécurité routière, producteurs des données"),
        ("navy", f"Remettre en état le réseau des {len(CUMUL)} préfectures qui cumulent les deux manques",
         f"{nb(KM_CUMUL, 1)} km à remettre en état : {et(CUMUL['Préfecture'])}. Cible : {pct(14.35, 2)} de "
         f"kilomètres en mauvais état, la médiane nationale.",
         [("3 ans", "violet"), ("Priorité haute", "navy")], f"{nb(POP_CUMUL)} habitants",
         "Ministère des travaux publics, fonds d’entretien routier"),
        ("vert", f"Ouvrir des auto-écoles dans les {len(SANS_AUCUNE)} préfectures qui n’en ont aucune, vérifier les "
                 f"{int(NON_AGREEES['Formation — auto-écoles recensées'].sum())} non agréées de {len(NON_AGREEES)} "
                 f"autres",
         f"{AE_A_OUVRIR} auto-écoles à ouvrir sur les {N_FORMATION} préfectures du levier formation, pour atteindre "
         f"{nb(1.065, 3)} auto-école agréée pour 100 000 habitants.",
         [("3 ans", "violet"), ("Priorité", "vert")], f"{nb(POP_FORMATION)} habitants",
         "Ministère chargé des transports, auto-écoles"),
        ("orange", "Cibler les usagers de deux-roues motorisés : casque, permis moto, contrôle",
         f"{pct(PART_2ROUES, 0)} des tués de {A_OMS} ; {CIBLE_PERMIS[0].lower() + CIBLE_PERMIS[1:]}.",
         [("3 ans", "violet"), ("National", "orange")], "tout le pays",
         "Organisme chargé de la sécurité routière, police, gendarmerie"),
        ("violet", f"Agir d’abord dans la {ZONE_TETE}, seule zone en retard sur la route et sur la formation",
         f"{RECO_ZONE_TETE['Cible']}. Les {len(ZONES_DIFF)} zones en difficulté sont "
         f"{et(list(ZONES_DIFF.index))}.",
         [(str(RECO_ZONE_TETE["Horizon"]), "violet"), ("Priorité haute", "navy")],
         f"{nb(int(RECO_ZONE_TETE['Habitants']))} habitants",
         "Travaux publics et transports, conjointement"),
    ]
    h, gap = 0.78, 0.055
    for i, (ton, titre, detail, etiquettes, habitants, acteurs) in enumerate(actions):
        yi = y + i * (h + gap)
        carte(d, M, yi, CW, h)
        carre_numero(d, M + 0.18, yi + 0.18, 0.44, str(i + 1), TONS[ton]["encre"], taille=15)
        bloc(d, M + 0.80, yi + 0.08, 4.00, h - 0.16, [T(titre, taille=11.5, gras=True, couleur=TONS[ton]["encre"],
                                                        interligne=1.02)], ancre=MSO_ANCHOR.MIDDLE)
        bloc(d, M + 4.98, yi + 0.08, 4.10, h - 0.16, [T(detail, taille=10, couleur=ENCRE, interligne=1.05)],
             ancre=MSO_ANCHOR.MIDDLE)
        xd = M + 9.26
        for texte, ton_e in etiquettes:
            xd += pastille(d, xd, yi + 0.10, texte, ton_e, taille=8.5, h=0.22) + 0.08
        bloc(d, M + 9.26, yi + 0.36, CW - 9.26 - 0.16, 0.22, [T(habitants, taille=10.5, gras=True, couleur=ENCRE)])
        bloc(d, M + 9.26, yi + 0.52, CW - 9.26 - 0.16, 0.26,
             [T(acteurs, taille=7.5, couleur=DISCRET, interligne=1.0)])

    y_veille = y + 5 * (h + gap) + 0.02
    bloc(d, M, y_veille, CW, 0.62,
         [dict(runs=[T(f"Ce que la population ajoute d’ici {A_FIN} : ", taille=10, gras=True, couleur=NAVY),
                     T(f"sans ouverture, le manque passe de {nb(AE_HORIZON.loc[A_DEBUT])} à "
                       f"{nb(AE_HORIZON.loc[A_FIN])} auto-écoles ; les {nb(KM_HORIZON.iloc[0], 1)} km à remettre en "
                       f"état ne bougent pas, c’est un retard déjà constitué ; {millions(RURAUX_HORIZON.loc[A_FIN])} "
                       f"de ruraux resteront à plus de 2 km d’une route revêtue.", taille=10, couleur=ENCRE2)]),
          dict(runs=[T(f"{N_RECO} recommandations au total, dont {len(RECO_HAUTE)} en priorité haute ; les "
                       f"habitants ne s’additionnent pas d’une action à l’autre : les territoires se recoupent.",
                       taille=9, couleur=DISCRET)], avant=3)])
    banniere(d, M, y_veille + 0.68, CW, 0.52, "Règle d’ordonnancement",
             "ce qui est mesuré n’attend pas (auto-écoles, contrôle, données) ; les travaux attendent la "
             f"vérification sur place de l’état relevé en {A_RELEVE}.", "sombre", taille=11.5)
    pied(d)


def diapo_decisions(prs) -> None:
    """Conclusion : quatre décisions, quatre limites."""
    d = nouvelle_diapositive(prs)
    y = en_tete(d, 10, "09 · Conclusion", "Les quatre décisions à engager")
    decisions = [
        ("rouge", "Mesurer", f"les accidents par préfecture, et vérifier sur place l’état du réseau relevé en "
                             f"{A_RELEVE}.", "dans l’année"),
        ("navy", "Remettre en état", f"{nb(KM_A_REMETTRE, 1)} km dans les {N_RESEAU} préfectures au réseau dégradé, "
                                     f"en commençant par les {len(CUMUL)} qui cumulent.", "à 3 ans"),
        ("vert", "Former", f"{AE_A_OUVRIR} auto-écoles à ouvrir dans les {N_FORMATION} préfectures qui en manquent, "
                           f"le permis moto d’abord.", "à 3 ans"),
        ("orange", "Protéger", f"les usagers de deux-roues motorisés, {pct(PART_2ROUES, 0)} des tués : casque, "
                               f"permis, contrôle.", "à 3 ans"),
    ]
    gap, h = 0.22, 1.86
    w = (CW - 3 * gap) / 4
    for i, (ton, verbe, texte, quand) in enumerate(decisions):
        x = M + i * (w + gap)
        carte(d, x, y, w, h)
        carre_numero(d, x + 0.20, y + 0.20, 0.40, str(i + 1), TONS[ton]["encre"], taille=14)
        pastille(d, x + w - 0.20, y + 0.28, quand, "ambre", taille=8.5, h=0.24, droite=True)
        bloc(d, x + 0.20, y + 0.70, w - 0.40, 0.40, [T(verbe, taille=taille_ajustee(verbe, w - 0.40, (18, 16, 15, 14)),
                                                       gras=True, couleur=TONS[ton]["encre"], police=POLICE_TITRE)])
        bloc(d, x + 0.20, y + 1.12, w - 0.40, h - 1.22, [T(texte, taille=10.5, couleur=ENCRE, interligne=1.06)])

    yb = y + h + 0.26
    wl = 7.70
    rect(d, M, yb, wl, 2.02, fond=TONS["limite"]["bg"], rayon=0.12, bord=TONS["limite"]["bord"])
    bloc(d, M + 0.24, yb + 0.14, wl - 0.48, 0.24, [T("CE QUE L’ANALYSE NE DIT PAS", taille=10, gras=True,
                                                     couleur=TONS["limite"]["encre"])])
    limites = [
        "Les accidents ne sont publiés qu’au niveau national : ni préfecture, ni mois, ni âge.",
        f"L’état du réseau vient d’un relevé de {A_RELEVE}, méthode de notation non publiée.",
        "L’activité des auto-écoles n’est pas publiée : agréée ne veut pas dire active.",
        "Aucun coût : des volumes (kilomètres, auto-écoles, habitants), pas des budgets.",
    ]
    bloc(d, M + 0.24, yb + 0.44, wl - 0.48, 1.06,
         [T(f"•  {l}", taille=10.5, couleur=ENCRE, apres=3) for l in limites])
    bloc(d, M + 0.24, yb + 1.56, wl - 0.48, 0.36,
         [T("L’analyse dit où agir et sur quel manque ; elle ne chiffre ni le coût des travaux, ni l’effet attendu "
            "sur les accidents.", taille=10.5, gras=True, couleur=TONS["limite"]["encre"])])

    xr = M + wl + 0.25
    wr = DROITE - xr
    carte(d, xr, yb, wr, 2.02)
    bloc(d, xr + 0.22, yb + 0.14, wr - 0.44, 0.24, [T("EXPLORER LE DÉTAIL", taille=10, gras=True, couleur=OCRE_TEXTE)])
    bloc(d, xr + 0.22, yb + 0.42, wr - 0.44, 0.30, [T("Tableau de bord interactif", taille=13, gras=True, couleur=NAVY,
                                                      police=POLICE_TITRE)])
    if URL_DASHBOARD:
        lien(d, xr + 0.22, yb + 0.80, wr - 0.44, URL_DASHBOARD.removeprefix("https://"), URL_DASHBOARD, taille=9.5)
        y_detail = yb + 1.14
    else:
        y_detail = yb + 0.78
    bloc(d, xr + 0.22, y_detail, wr - 0.44, 2.02 - (y_detail - yb) - 0.12,
         [T("Huit pages : la vue nationale, la comparaison des territoires, les évolutions et les constats, la "
            f"carte du réseau et des auto-écoles, les priorités, les {N_RECO} recommandations, l’horizon {A_FIN} "
            "et la méthode.", taille=10, couleur=ENCRE2, interligne=1.05)])

    banniere(d, M, yb + 2.24, CW, 0.66, "",
             [T(f"« {SLOGAN} » — {SOUS_TITRE.lower()}.", taille=14, police=POLICE_TITRE)], "sombre")
    pied(d)


def construire() -> None:
    global ARMOIRIES
    ARMOIRIES = rasteriser_armoiries()
    graphiques = {
        "mobilite": graphique_mobilite(),
        "securite": graphique_securite(),
        "reseau": graphique_reseau(),
        "carte_formation": carte_formation(),
        "carte_priorites": carte_priorites(),
        "arbitrage": graphique_arbitrage(),
    }
    prs = Presentation()
    prs.slide_width, prs.slide_height = LARGEUR, HAUTEUR
    diapo_couverture(prs)
    diapo_methode(prs)
    diapo_mobilite(prs, graphiques)
    diapo_securite(prs, graphiques)
    diapo_reseau(prs, graphiques)
    diapo_couverture_formation(prs, graphiques)
    diapo_territoires(prs, graphiques)
    diapo_arbitrage(prs, graphiques)
    diapo_plan(prs)
    diapo_decisions(prs)
    prs.save(SORTIE)
    print(f"{SORTIE.name} — {len(prs.slides)} diapositives, {SORTIE.stat().st_size / 1024:.0f} ko")
    for avertissement in AVERTISSEMENTS:
        print(f"  ⚠ {avertissement}")


if __name__ == "__main__":
    construire()
