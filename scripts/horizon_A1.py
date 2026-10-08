"""Annexe A1 : horizon 2031 (A1_horizon.md).

Lit la table maîtresse, les séries nationales (D2, D3, D7), les sorties du 07 au 10, quatre fichiers bruts
(projections de l'INSEED, recensement de 2010 par région, âges simples de WPP, lieux candidats de HDX)
et la grille WorldPop 2020 (partie 3).
N'écrit rien dans data/processed/ ni dans les sorties du 06 au 10.
Calcule chaque chiffre cité dans l'annexe (R-19) :
- la population par préfecture et par palier, variantes (a) et (b) (§3) ;
- le modèle des besoins, par préfecture, territoire et recommandation du 10 (§4) ;
- le modèle de sécurité : deux références sans action, cible de la Décennie, écart, plafond du casque (§5) ;
- la vérification avec la grille WorldPop : accès rural et emplacements des auto-écoles (§6).

Sorties, dans data/analysis/A1_horizon/ : population_A1.csv, horizon_A1.csv, national_A1.csv, acces_A1.csv,
emplacements_A1.csv, sites_A1.csv, erratum_A1.csv, formules_A1.csv, sources_A1.csv, controles_A1.csv.

Usage : .venv/bin/python scripts/horizon_A1.py
"""
import hashlib
import re
import urllib.request
from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from rasterio import features
from scipy.spatial import cKDTree

RACINE = Path(__file__).resolve().parent.parent
TRAITE = RACINE / "data" / "processed"
GEO = TRAITE / "geo"
BRUT = RACINE / "data" / "raw"
ANALYSE = RACINE / "data" / "analysis"
SORTIE = ANALYSE / "A1_horizon"
DOCUMENT = RACINE / "A1_horizon.md"  # blocs de résultats, relus par le contrôle 10-13
GRILLE = BRUT / "worldpop_tgo_2020.tif"  # non versionnée (.gitignore) : retéléchargée si elle manque
SHA_GRILLE = "f9c0ed84b8e3bacb184efadbe9343a8e9a1cc6043439e3fa4ef13574d0ed84e6"  # téléchargement du 2026-10-08

UTM = "EPSG:32631"  # R-16
PALIERS = {2022: "Passé", 2026: "Actuel", 2027: "+1 an", 2029: "+3 ans", 2031: "+5 ans"}
ANNEES = [2022, 2026, 2027, 2028, 2029, 2030, 2031]
ACTUEL = 2026
REF = [2022, 2023, 2024]  # 3 dernières années : méthode du 02 (H6, S4), cible de REC-F3 (écart 29)
DEBUT = [2010, 2011, 2012]  # fenêtre de début du 09 (H6)
DECENNIE = (2021, 2030, 0.5)  # résolution A/RES/74/299 : au moins 50 % de tués et de blessés en moins d'ici 2030
CASQUE = {"Valeur": 0.42, "Borne basse": 0.32, "Borne haute": 0.50}  # Liu et al., 2008 : OR 0,58 [0,50–0,68]
SOURCE_CASQUE = "revue Cochrane CD004333 (Liu et al., 2008) : risque de décès réduit de 42 % (OR 0,58 ; IC 95 % 0,50–0,68)"
SOURCE_DECENNIE = "résolution A/RES/74/299 de l'Assemblée générale des Nations unies (2020)"
BANDE_KM = 2  # indice d'accès rural (ODD 9.1.1), comme au 10
TOUTE_SAISON = "Route nationale revêtue"  # écart 32
SE08_KM = 10  # SE-08 : rayon de couverture d'une auto-école
HORIZON_SITES = 2029  # horizon de REC-F1 et REC-F2 (3 ans)
EN_TETE = 10  # REC-R3
REGIONS_2010 = {"Maritime": ["Maritime (sans Lomé Commune)", "Lomé Commune"], "Plateaux": ["Plateaux"],
                "Centrale": ["Centrale"], "Kara": ["Kara"], "Savanes": ["Savanes"]}
POP, NIV = "Population", "C"
CONFORME, ECHEC = "conforme", "échec"
SRC_POP = "recensement 2022 ; projections de l'INSEED 2011-2031 ; variante (b) : croissance régionale 2010-2022"

controles = []


def controle(ident, intitule, attendu, mesure, ok):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC})


def n(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def plafond(x):
    return np.ceil(np.round(x, 6))


# --- Entrées --------------------------------------------------------------------------------------------

def lire():
    tm = pd.read_csv(TRAITE / "table_maitresse_prefecture.csv").set_index("Préfecture")
    c = pd.read_csv(ANALYSE / "08_priorisation" / "classement_08.csv").set_index("Préfecture")
    c["Leviers"] = c["Leviers"].fillna("")
    pf = pd.DataFrame({"Zone": c["Zone"], "Région": c["Région"], "Pop22": tm["population_2022"].reindex(c.index)})
    pf["Rurale22"] = tm["population_2022_rurale"].reindex(c.index).fillna(0)
    pf["Surface"] = tm["Surface (km²)"].reindex(c.index)
    pf["Comptées"] = c["Auto-écoles comptées"]
    pf["Recensées"] = tm["auto_ecoles_recensees"].reindex(c.index)
    pf["Km mauvais"] = c["Km en mauvais état"]
    pf["Km évalués"] = c["Km évalués"]
    pf["Réseau"] = c["Leviers"].str.contains("réseau")
    pf["Formation"] = c["Leviers"].str.contains("formation")
    pf["Km O5-04 (08)"] = c["O5-04 km à remettre en état"]
    pf["AE O5-04 (08)"] = c["O5-04 auto-écoles manquantes (écart 21)"]
    pf["Rec réseau"] = np.where(pf["Réseau"] & pf["Formation"], "REC-R1", np.where(pf["Réseau"], "REC-R2", ""))
    pf["Rec formation"] = np.where(pf["Formation"] & (pf["Recensées"] == 0), "REC-F1", np.where(pf["Formation"], "REC-F2", ""))
    cibles = {  # les arrondis du 10 (recommandations_10.py), pour retrouver ses quantités
        "O3-02": round(float(c.loc[c["O3-02"].notna(), "O3-02"].median()), 2),
        "O4-05": round(float(c.loc[c["Auto-écoles comptées"] > 0, "O4-05"].median()), 3),
        "O4-03": round(float(c["O4-03"].median()), 2)}
    rec = pd.read_csv(ANALYSE / "10_recommandations" / "recommandations_10.csv").set_index("ID")
    zones10 = pd.read_csv(ANALYSE / "10_recommandations" / "zones_10.csv")
    return pf, cibles, rec, zones10


# --- §3 Population par préfecture -------------------------------------------------------------------------

def population(pf):
    proj = pd.read_csv(BRUT / "projections_demographiques_2011_2031.csv")
    nat = proj[(proj["tranche-d-âges"] == "Togo") & (proj["sexe"] == "Total")].set_index("Date")["Value"]
    N = {2022: float(pf["Pop22"].sum()), **{t: float(nat[t]) for t in ANNEES if t > 2022}}
    p10 = pd.read_csv(BRUT / "population_region_sexe_2010.csv")
    p10 = p10[p10["sexe"] == "Total"].set_index("région")["Value"]
    r10 = pd.Series({r: float(sum(p10[l] for l in libs)) for r, libs in REGIONS_2010.items()})
    r22 = pf.groupby("Région")["Pop22"].sum()
    g = (r22 / r10) ** (1 / 12)
    part = pf["Pop22"] / pf["Pop22"].sum()
    pa, pb = {}, {}
    for t in ANNEES:
        pa[t] = part * N[t]
        prov = r22 * g ** (t - 2022)
        rt = prov * N[t] / prov.sum()
        pb[t] = pf["Pop22"] * pf["Région"].map(rt / r22)
    lignes = []
    for t in ANNEES:
        for p in pf.index:
            a, b = pa[t][p], pb[t][p]
            rur = pf.at[p, "Rurale22"] / pf.at[p, "Pop22"]
            lignes.append({"Préfecture": p, "Zone": pf.at[p, "Zone"], "Région": pf.at[p, "Région"], "Année": t,
                           "Palier": PALIERS.get(t, ""), POP: round(b), "Borne basse": round(min(a, b)), "Borne haute": round(max(a, b)),
                           "Population (a)": round(a), "Population (b)": round(b), "Population rurale": round(b * rur),
                           "Densité (hab./km²)": round(b / pf.at[p, "Surface"], 1),
                           "Croissance annuelle de la région 2010-2022 (%)": round((g[pf.at[p, "Région"]] - 1) * 100, 2),
                           "Niveau": "A" if t == 2022 else NIV, "Source": "recensement 2022 (RGPH-5)" if t == 2022 else SRC_POP})
    croissance = pd.DataFrame({"Croissance annuelle 2010-2022 (%)": (g - 1) * 100, "Population 2010": r10, "Population 2022": r22})
    return pa, pb, N, pd.DataFrame(lignes), croissance


# --- §4 Modèle des besoins --------------------------------------------------------------------------------

def part_surface_proche():
    """Part de la surface de chaque préfecture à moins de 2 km d'une route nationale revêtue (méthode du 10, O4-E1)."""
    pref = gpd.read_file(GEO / "prefectures.geojson").to_crs(UTM)
    routes = gpd.read_file(GEO / "routes_classees.geojson").to_crs(UTM)
    bande = routes[routes["Type"] == TOUTE_SAISON].buffer(BANDE_KM * 1000).union_all()
    part = pref.geometry.intersection(bande).area / pref.geometry.area
    return pd.Series(part.to_numpy(), index=pref["Préfecture"]), bande


def besoins_prefectures(pf, cibles, pa, pb, part):
    """Une ligne par préfecture, levier et palier : quantité dans chaque variante."""
    lignes = []
    rur = pf["Rurale22"] / pf["Pop22"]
    km_besoin = (pf["Km mauvais"] - cibles["O3-02"] / 100 * pf["Km évalués"]).clip(lower=0).round(1)
    for t in PALIERS:
        for p in pf.index:
            x = pf.loc[p]
            pop = {"a": pa[t][p], "b": pb[t][p]}
            base = {"Préfecture": p, "Zone": x["Zone"], "Région": x["Région"], "Année": t, "Palier": PALIERS[t]}
            ae = {k: max(0.0, plafond(cibles["O4-05"] * v / 1e5) - x["Comptées"]) for k, v in pop.items()}
            lignes.append({**base, "Levier": "Auto-écoles", "Recommandation": x["Rec formation"],
                           "Périmètre": "Levier du 08" if x["Formation"] else "Hors levier",
                           "Existant": x["Comptées"], "Valeur a": ae["a"], "Valeur b": ae["b"],
                           "Sans action b": x["Comptées"] / pop["b"] * 1e5, "Avec action b": (x["Comptées"] + ae["b"]) / pop["b"] * 1e5,
                           "Pop a": pop["a"], "Pop b": pop["b"]})
            lignes.append({**base, "Levier": "Remise en état", "Recommandation": x["Rec réseau"],
                           "Périmètre": "Levier du 08" if x["Réseau"] else "Hors levier",
                           "Existant": x["Km mauvais"], "Valeur a": km_besoin[p], "Valeur b": km_besoin[p],
                           "Évalués": x["Km évalués"], "Pop a": pop["a"], "Pop b": pop["b"]})
            loin = {k: v * rur[p] * (1 - part.get(p, 0)) for k, v in pop.items()}
            lignes.append({**base, "Levier": "Accès rural", "Recommandation": "", "Périmètre": "Toutes",
                           "Existant": np.nan, "Valeur a": loin["a"], "Valeur b": loin["b"],
                           "Rurale a": pop["a"] * rur[p], "Rurale b": pop["b"] * rur[p], "Pop a": pop["a"], "Pop b": pop["b"]})
            if x["Km évalués"] == 0:  # Mô, seule préfecture sans route classée (REC-R4, écart 28)
                d = {k: cibles["O4-03"] * v / 1e4 for k, v in pop.items()}
                lignes.append({**base, "Levier": "Desserte de Mô", "Recommandation": "REC-R4", "Périmètre": "Levier du 10",
                               "Existant": 0.0, "Valeur a": d["a"], "Valeur b": d["b"], "Pop a": pop["a"], "Pop b": pop["b"]})
    return pd.DataFrame(lignes)


UNITES = {"Auto-écoles": ("auto-écoles à ouvrir", "auto-écoles agréées pour 100 000 habitants"),
          "Remise en état": ("km à remettre en état", "part des km évalués en mauvais état (%)"),
          "Accès rural": ("ruraux à plus de 2 km d’une route revêtue", "part des ruraux à moins de 2 km (%)"),
          "Desserte de Mô": ("km de routes classées", "km de routes classées pour 10 000 habitants")}


def cible_texte(levier, cibles):
    return {"Auto-écoles": f"{n(cibles['O4-05'], 3)} pour 100 000 habitants (écart 21)",
            "Remise en état": f"{n(cibles['O3-02'], 2)} % des km évalués en mauvais état (médiane de O3-02)",
            "Accès rural": "aucune (10 §4.6)",
            "Desserte de Mô": f"{n(cibles['O4-03'], 2)} km pour 10 000 habitants (écart 28)"}[levier]


def agreger(g, levier, cibles):
    """Somme d'un groupe de lignes préfecture : quantité par variante, indicateur sans et avec action."""
    va, vb = g["Valeur a"].sum(), g["Valeur b"].sum()
    pop = g["Pop b"].sum()
    r = {"Existant": g["Existant"].sum(min_count=1), "Valeur": vb, "Borne basse": min(va, vb), "Borne haute": max(va, vb), POP: pop}
    if levier == "Auto-écoles":
        r["Sans action"] = g["Existant"].sum() / pop * 1e5
        r["Avec action"] = (g["Existant"].sum() + vb) / pop * 1e5
    elif levier == "Remise en état":
        ev = g["Évalués"].sum()
        r["Sans action"] = g["Existant"].sum() / ev * 100 if ev else np.nan
        r["Avec action"] = (g["Existant"].sum() - vb) / ev * 100 if ev else np.nan
    elif levier == "Accès rural":
        rur = g["Rurale b"].sum()
        r["Existant"] = np.nan
        r["Sans action"] = (1 - vb / rur) * 100 if rur else np.nan
        r["Avec action"] = np.nan
    else:
        r["Sans action"], r["Avec action"] = 0.0, cibles["O4-03"]
    return r


def note_levier(levier):
    return {"Auto-écoles": "auto-écoles de la collecte 2021-2022, activité non vérifiée ; cible gardée à sa valeur de 2022 (A1-3)",
            "Remise en état": "relevé de 2020 ; même valeur à chaque palier : aucune donnée ne mesure l’usure",
            "Accès rural": "population rurale supposée uniforme dans la préfecture, comme au 10 ; aucune cible (10 §4.6)",
            "Desserte de Mô": "ordre de grandeur derrière une vérification (REC-R4)"}[levier]


def table_horizon(bp, pf, cibles, rec, N, permis):
    """horizon_A1.csv : préfectures, zones, régions, pays et recommandations du 10, à chaque palier."""
    lignes = []

    def ajouter(maille, territoire, levier, t, r, zone="", region="", recommandation="", perimetre="", note=""):
        mesure, indic = UNITES[levier]
        lignes.append({"Maille": maille, "Territoire": territoire, "Zone": zone, "Région": region, "Recommandation": recommandation,
                       "Périmètre": perimetre, "Levier": levier, "Mesure": mesure, "Année": t, "Palier": PALIERS[t],
                       "Existant": r["Existant"], "Cible": cible_texte(levier, cibles), "Valeur": r["Valeur"],
                       "Borne basse": r["Borne basse"], "Borne haute": r["Borne haute"], "Indicateur": indic,
                       "Sans action": r["Sans action"], "Avec action": r["Avec action"], POP: r[POP],
                       "Niveau": "B" if t == 2022 else NIV, "Source": "A1 §4 ; 08 (O5-04) ; 10" if t == 2022 else f"A1 §4 ; {SRC_POP}",
                       "Note": note or note_levier(levier)})

    for (p, levier, t), g in bp.groupby(["Préfecture", "Levier", "Année"], sort=False):
        x = g.iloc[0]
        ajouter("Préfecture", p, levier, t, agreger(g, levier, cibles), x["Zone"], x["Région"], x["Recommandation"], x["Périmètre"])
    for maille, cle in (("Zone", "Zone"), ("Région", "Région"), ("Pays", None)):
        for levier in ("Auto-écoles", "Remise en état", "Accès rural"):
            sous = bp[bp["Levier"] == levier]
            perims = ([("Toutes les préfectures", sous)] if levier == "Accès rural" else
                      [("Levier du 08", sous[sous["Périmètre"] == "Levier du 08"]), ("Toutes les préfectures", sous)])
            for nom, s in perims:
                for t in PALIERS:
                    st = s[s["Année"] == t]
                    groupes = st.groupby(cle) if cle else [("Togo", st)]
                    for terr, g in groupes:
                        ajouter(maille, terr, levier, t, agreger(g, levier, cibles), terr if maille == "Zone" else "",
                                terr if maille == "Région" else "", perimetre=nom)

    # Recommandations du 10 : quantité de chaque palier ; l'horizon d'action est lu dans recommandations_10.csv
    tr = pd.read_csv(TRAITE / "D4_etat_troncons.csv")
    tete = tr[tr["km_mauvais"] > 0].sort_values(["km_mauvais", "Tronçon"], ascending=[False, True]).head(EN_TETE)
    km_m, km_t = tete["km_mauvais"].sum(), tete["km_total"].sum()

    def groupe(filtre, levier):
        return bp[(bp["Levier"] == levier) & filtre(bp)]

    groupes = {
        "REC-R1": ("Remise en état", lambda d: d["Recommandation"] == "REC-R1"),
        "REC-R2": ("Remise en état", lambda d: d["Recommandation"] == "REC-R2"),
        "REC-R4": ("Desserte de Mô", lambda d: d["Recommandation"] == "REC-R4"),
        "REC-F1": ("Auto-écoles", lambda d: d["Recommandation"] == "REC-F1"),
        "REC-F2": ("Auto-écoles", lambda d: d["Recommandation"] == "REC-F2"),
        "REC-Z1": ("Remise en état", lambda d: (d["Périmètre"] == "Levier du 08") & (d["Zone"] == "Plateaux")),
        "REC-Z2": ("Auto-écoles", lambda d: (d["Périmètre"] == "Levier du 08") & d["Zone"].isin(["Maritime hors Grand Lomé", "Savanes"])),
        "REC-Z3 (réseau)": ("Remise en état", lambda d: (d["Périmètre"] == "Levier du 08") & (d["Zone"] == "Centrale")),
        "REC-Z3 (formation)": ("Auto-écoles", lambda d: (d["Périmètre"] == "Levier du 08") & (d["Zone"] == "Centrale")),
    }
    for ident in rec.index:
        h = max(int(a) for a in re.findall(r"(\d+) ans?", rec.at[ident, "Horizon"]))
        cles = [k for k in groupes if k.split(" ")[0] == ident]
        for t in PALIERS:
            base = {"Horizon (ans)": h, "Palier de l’horizon": t == ACTUEL + h}
            for k in cles:
                levier, f = groupes[k]
                g = groupe(f, levier)
                g = g[g["Année"] == t]
                ajouter("Recommandation", rec.at[ident, "Territoire"], levier, t, agreger(g, levier, cibles),
                        recommandation=k, perimetre="Levier du 10")
                lignes[-1].update(base)
            if ident == "REC-R3":
                v = max(0.0, km_m - cibles["O3-02"] / 100 * km_t)
                ajouter("Recommandation", rec.at[ident, "Territoire"], "Remise en état", t,
                        {"Existant": km_m, "Valeur": v, "Borne basse": v, "Borne haute": v, POP: np.nan,
                         "Sans action": km_m / km_t * 100, "Avec action": cibles["O3-02"]},
                        recommandation=ident, perimetre="Levier du 10",
                        note="les 10 tronçons les plus dégradés ; ils traversent les préfectures de REC-R1 et REC-R2 (pas d’addition)")
                lignes[-1].update(base)
            if ident == "REC-F3":
                p = permis[(permis["Série"] == "Permis A pour garder le taux") & (permis["Année"] == t)]
                v = float(p["Valeur"].iloc[0])
                lignes.append({"Maille": "Recommandation", "Territoire": "National", "Recommandation": ident, "Périmètre": "Levier du 10",
                               "Levier": "Permis moto", "Mesure": "permis A à délivrer dans l’année", "Année": t, "Palier": PALIERS[t],
                               "Existant": float(p["Existant"].iloc[0]), "Cible": "taux de 2022–2024 pour 1 000 habitants de 18 ans et plus (écart 29)",
                               "Valeur": v, "Borne basse": v, "Borne haute": v, "Indicateur": "permis A pour 1 000 habitants de 18 ans et plus",
                               "Sans action": np.nan, "Avec action": float(p["Taux"].iloc[0]), POP: float(p[POP].iloc[0]),
                               "Niveau": NIV, "Source": "A1 §4 ; D2 ; D7 ; projections de l'INSEED par âge", "Note": "population nationale, sans variante",
                               **base})
            if ident in ("REC-S1", "REC-D1", "REC-D2", "REC-D3", "REC-D4"):
                lignes.append({"Maille": "Recommandation", "Territoire": rec.at[ident, "Territoire"], "Recommandation": ident,
                               "Périmètre": "Levier du 10", "Levier": rec.at[ident, "Levier"], "Mesure": "aucune quantité",
                               "Année": t, "Palier": PALIERS[t], "Cible": rec.at[ident, "Cible"], POP: N[t] if t in N else np.nan,
                               "Niveau": NIV, "Source": "10", **base,
                               "Note": "la cible ne dépend pas de la population" if ident == "REC-S1" else "demande de données : horizon d’un an"})
    h = pd.DataFrame(lignes)
    for col in ("Valeur", "Borne basse", "Borne haute"):
        h[col] = np.where(h["Levier"].isin(["Auto-écoles", "Permis moto"]) | (h["Levier"] == "Accès rural"),
                          h[col].round(0), h[col].round(1))
    for col in ("Sans action", "Avec action"):
        h[col] = h[col].round(2)
    h["Existant"] = h["Existant"].round(1)
    h[POP] = h[POP].round(0)
    return h


# --- §5 Modèle de sécurité et permis (national) ------------------------------------------------------------

def population_18(N):
    """Population de 18 ans et plus : D7 jusqu'en 2024 ; de 2025 à 2031, groupes d'âges de l'INSEED, le groupe 15-19
    coupé à 18 ans avec les âges simples de WPP de 2024 (méthode du 05, A1-5)."""
    d7 = pd.read_csv(TRAITE / "D7_population_age_conduire.csv")
    d7 = d7[d7["Catégorie"] == "A"].set_index("Année")["Population en âge de conduire"]
    proj = pd.read_csv(BRUT / "projections_demographiques_2011_2031.csv")
    proj = proj[(proj["sexe"] == "Total") & (proj["tranche-d-âges"] != "Togo")]
    wpp = pd.read_csv(BRUT / "wpp2024_population_age_simple_togo.csv", sep="|", skiprows=1)
    wpp = wpp[(wpp["Variant"] == "Median") & (wpp["Sex"] == "Both sexes")].set_index(["TimeLabel", "AgeStart"])["Value"]

    def calcul(an, an_wpp):
        total = 0.0
        for r in proj[proj["Date"] == an].itertuples():
            debut = int(re.match(r"\s*(\d+)", r[2]).group(1))
            fin = 200 if "plus" in r[2] else int(re.findall(r"\d+", r[2])[1])
            if debut >= 18:
                total += r.Value
            elif fin >= 18:
                total += r.Value * wpp.loc[an_wpp].loc[18:fin].sum() / wpp.loc[an_wpp].loc[debut:fin].sum()
        return total

    # Les projections par âge ne raccordent pas au recensement (18 ans et plus : 51,8 % en 2022, 55,6 % projetés en 2023) :
    # niveau du recensement de 2022, croissance des projections de l'INSEED (la règle du 03 pour WPP), A1-5.
    proj18 = {an: calcul(an, min(an, 2024)) for an in range(2022, 2032)}
    serie = {an: float(d7[an]) for an in d7.index if an <= 2022}
    serie.update({an: float(d7[2022]) * proj18[an] / proj18[2022] for an in range(2023, 2032)})
    verif = {an: (calcul(an, an), float(d7[an])) for an in (2023, 2024)}
    raccord = {"recensement 2022": float(d7[2022]) / 8095498, "projection 2023 (D7)": float(d7[2023]) / 8251000}
    return pd.Series(serie), verif, raccord


def national(N, p18, raccord):
    pop = pd.read_csv(TRAITE / "D7_population_nationale.csv").set_index("Année")["Population"].astype(float)
    proj = pd.read_csv(BRUT / "projections_demographiques_2011_2031.csv")
    projn = proj[(proj["tranche-d-âges"] == "Togo") & (proj["sexe"] == "Total")].set_index("Date")["Value"]
    for t in range(2025, 2032):
        pop[t] = float(projn[t])
    lignes = []

    def ajouter(mesure, serie, an, valeur, unite, basse=np.nan, haute=np.nan, niveau=NIV, source="", note="", **k):
        lignes.append({"Mesure": mesure, "Série": serie, "Année": an, "Palier": PALIERS.get(an, ""), "Valeur": valeur,
                       "Borne basse": basse, "Borne haute": haute, "Unité": unite, "Niveau": niveau, "Source": source, "Note": note, **k})

    for an in pop.index:
        if an >= 2007:
            ajouter("Population", "observée" if an <= 2024 else "projetée", an, pop[an], "habitants",
                    niveau="A" if an in (2010, 2022) else NIV, source="D7 ; projections de l'INSEED")
    for an in p18.index:
        ajouter("Population de 18 ans et plus", "observée" if an <= 2022 else "projetée", an, p18[an], "habitants",
                niveau="A" if an == 2022 else NIV,
                source="D7_population_age_conduire.csv" if an <= 2022 else
                "recensement 2022 × croissance des projections de l'INSEED par âge (groupe 15-19 coupé avec WPP), A1-5",
                note="" if an <= 2022 else
                f"raccord : 18 ans et plus = {n(raccord['recensement 2022'] * 100, 1)} % de la population au recensement 2022, "
                f"{n(raccord['projection 2023 (D7)'] * 100, 1)} % dans les projections de 2023")

    # Permis A (REC-F3)
    d2 = pd.read_csv(TRAITE / "D2_permis.csv")
    pa = d2[d2["Catégorie"] == "A"].set_index("Année")["Permis délivrés"].astype(float)
    taux = pa.loc[REF].mean() / p18.loc[REF].mean() * 1000
    for an in pa.index:
        ajouter("Permis A", "observé", an, pa[an], "permis délivrés", niveau="A", source="D2_permis.csv")
    permis = []
    for an in sorted(set(range(2022, 2032)) | set(PALIERS)):
        v = taux * p18[an] / 1000
        ajouter("Permis A", "Permis A pour garder le taux", an, v, "permis délivrés",
                source="A1 §4 (A1-5) : taux moyen de 2022–2024 × population de 18 ans et plus", note=f"taux : {n(taux, 3)} pour 1 000")
        permis.append({"Série": "Permis A pour garder le taux", "Année": an, "Valeur": v, "Taux": taux, POP: p18[an],
                       "Existant": pa.get(an, pa.loc[REF].mean())})

    # Accidents, blessés, tués
    d3 = pd.read_csv(TRAITE / "D3_accidents.csv")
    usager = pd.read_csv(TRAITE / "D3_victimes_usager_2021.csv").set_index("Type d'usager")["Part des tués déclarés (%)"]
    part2r = float(usager["Deux et trois-roues motorisés"]) / 100
    resume = {}
    for mesure in ("Accidents constatés", "Blessés", "Tués"):
        s = d3[d3["Mesure"] == mesure].set_index("Année")["Valeur"].astype(float)
        taux_obs = s / pop.loc[s.index] * 1e5
        fixe = taux_obs.loc[REF].mean()
        r = (taux_obs.loc[REF].mean() / taux_obs.loc[DEBUT].mean()) ** (1 / 12) - 1
        for an in s.index:
            ajouter(mesure, "observé", an, s[an], "nombre", niveau="A", source="D3_accidents.csv")
            ajouter(f"{mesure} pour 100 000 habitants", "observé", an, taux_obs[an], "pour 100 000 habitants",
                    niveau="A" if an in (2010, 2022) else NIV, source="D3 ; D7")
        cible = None
        if mesure != "Accidents constatés":
            a0, a1, red = DECENNIE
            cible = {an: s[a0] * (1 - red * min(an - a0, a1 - a0) / (a1 - a0)) for an in range(a0, 2032)}
        for an in range(2025, 2032):
            ti = fixe * pop[an] / 1e5
            td = taux_obs.loc[REF].mean() * (1 + r) ** (an - 2023) * pop[an] / 1e5
            ajouter(mesure, "Taux inchangé", an, ti, "nombre", min(ti, td), max(ti, td),
                    source="A1 §5 (A1-6) : taux moyen de 2022–2024 × population", note=f"taux : {n(fixe, 2)} pour 100 000")
            ajouter(mesure, "Tendance", an, td, "nombre", min(ti, td), max(ti, td),
                    source="A1 §5 (A1-6) : variation annuelle entre 2010–2012 et 2022–2024", note=f"variation annuelle : {n(r * 100, 2)} %")
            if cible:
                ajouter(mesure, "Écart à la cible (taux inchangé)", an, ti - cible[an], "nombre", source=f"A1 §5 ; {SOURCE_DECENNIE}")
                ajouter(mesure, "Écart à la cible (tendance)", an, td - cible[an], "nombre", source=f"A1 §5 ; {SOURCE_DECENNIE}")
            if mesure == "Tués":
                for serie, tu in (("taux inchangé", ti), ("tendance", td)):
                    ajouter(mesure, f"Plafond du casque ({serie})", an, tu * part2r * CASQUE["Valeur"], "tués évitables au plus",
                            tu * part2r * CASQUE["Borne basse"], tu * part2r * CASQUE["Borne haute"],
                            source=f"D3_victimes_usager_2021.csv (OMS) ; {SOURCE_CASQUE}",
                            note="plafond : suppose qu’aucun usager de deux-roues tué ne portait de casque ; taux de port non publié (OMS 2023)")
        if cible:
            for an in range(DECENNIE[0], 2032):
                ajouter(mesure, "Cible de la Décennie", an, cible[an], "nombre", niveau=NIV, source=SOURCE_DECENNIE,
                        note="trajectoire linéaire depuis 2021 ; 2031 garde la cible de 2030")
        resume[mesure] = {"taux fixe": fixe, "variation": r, "s": s, "cible": cible}
    d = pd.DataFrame(lignes)
    for col in ("Valeur", "Borne basse", "Borne haute"):
        d[col] = np.where(d["Unité"].str.startswith("pour"), d[col].round(2), d[col].round(0))
    return d, pd.DataFrame(permis), resume, part2r, taux


# --- §6 Partie 3 : grille WorldPop --------------------------------------------------------------------------

def telecharger_grille():
    """Partie 3 : la grille WorldPop recensée au 03 (URL du registre), téléchargée si elle manque, empreinte vérifiée."""
    if not GRILLE.exists():
        url = pd.read_csv(BRUT / "_SOURCES.csv").set_index("Fichier").at[GRILLE.name, "URL"]
        urllib.request.urlretrieve(url, GRILLE)
    if sha256(GRILLE) != SHA_GRILLE:
        raise SystemExit(f"{GRILLE.name} : empreinte différente de celle du téléchargement du 2026-10-08")


def grille(pf, bande):
    """Carreaux peuplés de la grille, ramenés à la population 2022 de chaque préfecture ; parts urbaine et rurale ;
    carreaux à moins de 2 km d'une route nationale revêtue."""
    telecharger_grille()
    pref = gpd.read_file(GEO / "prefectures.geojson").set_index("Préfecture").loc[pf.index].reset_index()
    with rasterio.open(GRILLE) as src:
        v = src.read(1)
        tr, forme, crs = src.transform, src.shape, src.crs
        nodata = src.nodata
    code = features.rasterize(((g, i + 1) for i, g in enumerate(pref.to_crs(crs).geometry)), out_shape=forme, transform=tr,
                              fill=0, dtype="int16")
    dans = features.rasterize([(gpd.GeoSeries([bande], crs=UTM).to_crs(crs).iloc[0], 1)], out_shape=forme, transform=tr,
                              fill=0, dtype="uint8")
    ok = (v != nodata) & (v > 0) & (code > 0)
    lig, col = np.nonzero(ok)
    lon, lat = rasterio.transform.xy(tr, lig, col, offset="center")
    x, y = Transformer.from_crs(crs, UTM, always_xy=True).transform(np.asarray(lon), np.asarray(lat))
    cel = pd.DataFrame({"Préfecture": pref["Préfecture"].to_numpy()[code[ok] - 1], "brut": v[ok].astype(float),
                        "proche": dans[ok].astype(bool), "x": x, "y": y})
    cel["pop"] = cel["brut"] * cel["Préfecture"].map(pf["Pop22"] / cel.groupby("Préfecture")["brut"].sum())
    # partage urbain / rural : les carreaux les plus denses portent la population urbaine du recensement (A1-9)
    cel = cel.sort_values(["Préfecture", "brut"], ascending=[True, False])
    avant = cel.groupby("Préfecture")["pop"].cumsum() - cel["pop"]
    urb = cel["Préfecture"].map(pf["Pop22"] - pf["Rurale22"])
    cel["urbaine"] = np.clip(urb - avant, 0, cel["pop"])
    cel["rurale"] = cel["pop"] - cel["urbaine"]
    return cel, float(v[(v != nodata) & (v > 0)].sum())


def acces_grille(cel, pf, part, pb, zones10):
    g = cel.assign(rp=cel["rurale"] * cel["proche"]).groupby("Préfecture").agg(rur=("rurale", "sum"), proches=("rp", "sum"))
    p = pd.DataFrame({"Zone": pf["Zone"], "Région": pf["Région"], "Population rurale": pf["Rurale22"]})
    p["Accès (uniforme, %)"] = np.where(pf["Rurale22"] > 0, part.reindex(pf.index) * 100, np.nan)
    p["Accès (grille, %)"] = np.where(g["rur"].reindex(pf.index) > 0, g["proches"].reindex(pf.index) / g["rur"].reindex(pf.index) * 100, np.nan)
    p["Ruraux à moins de 2 km (uniforme)"] = pf["Rurale22"] * part.reindex(pf.index)
    p["Ruraux à moins de 2 km (grille)"] = g["proches"].reindex(pf.index).fillna(0)
    lignes = []
    for t in PALIERS:
        fac = pb[t] / pf["Pop22"]
        for maille, cle in (("Préfecture", None), ("Zone", "Zone"), ("Pays", "Pays")):
            d = p.assign(Pays="Togo", f=fac)
            d["rur_t"] = d["Population rurale"] * d["f"]
            d["uni_t"] = d["Ruraux à moins de 2 km (uniforme)"] * d["f"]
            d["gri_t"] = d["Ruraux à moins de 2 km (grille)"] * d["f"]
            grp = d.groupby(cle) if cle else d.groupby(level=0)
            for terr, x in grp:
                rur, uni, gri = x["rur_t"].sum(), x["uni_t"].sum(), x["gri_t"].sum()
                lignes.append({"Maille": maille, "Territoire": terr, "Zone": x["Zone"].iloc[0] if maille != "Pays" else "",
                               "Année": t, "Palier": PALIERS[t], "Population rurale": round(rur),
                               "Accès rural, uniforme (%)": round(uni / rur * 100, 2) if rur else np.nan,
                               "Accès rural, grille (%)": round(gri / rur * 100, 2) if rur else np.nan,
                               "Ruraux à plus de 2 km, uniforme": round(rur - uni), "Ruraux à plus de 2 km, grille": round(rur - gri),
                               "Niveau": NIV, "Source": "grille WorldPop 2020 (100 m) ramenée au recensement 2022 ; routes classées (D5)",
                               "Note": "variante (b) de la population ; parts d’accès de 2022 gardées à chaque palier"})
    a = pd.DataFrame(lignes)
    z = a[(a["Maille"] == "Zone") & (a["Année"] == 2022)].set_index("Territoire")
    rurales = z[z["Population rurale"] > 0]
    med = {k: rurales[f"Accès rural, {k} (%)"].median() for k in ("uniforme", "grille")}
    sous = {k: set(rurales[rurales[f"Accès rural, {k} (%)"] < med[k]].index) for k in med}
    pays = a[(a["Maille"] == "Pays") & (a["Année"] == 2022)].iloc[0]
    route10 = set(zones10.loc[(zones10["Maille"] == "Zone") & (zones10["Route : sous la médiane"] == True), "Zone"])  # noqa: E712
    verdict = "confirmée" if sous["grille"] == route10 else "corrigée"
    for k in ("uniforme", "grille"):
        a.loc[len(a)] = {"Maille": "Médiane des zones", "Territoire": k, "Année": 2022, "Palier": PALIERS[2022],
                         f"Accès rural, {k} (%)": round(med[k], 2), "Niveau": NIV,
                         "Note": f"zones sous la médiane : {', '.join(sorted(sous[k]))}"}
    a.loc[len(a)] = {"Maille": "Conclusion du 10 §4.6", "Territoire": verdict, "Année": 2022, "Palier": PALIERS[2022], "Niveau": NIV,
                     "Note": f"10 : {', '.join(sorted(route10))} ; grille : {', '.join(sorted(sous['grille']))} ; critère fixé avant le calcul (A1 §6)"}
    return a, p, med, sous, route10, verdict, pays


def emplacements(cel, pf, bh):
    """Couverture maximale à 10 km : sites choisis parmi les lieux candidats de D13, gloutonnement (A1-10)."""
    hdx = pd.ExcelFile(BRUT / "limites_administratives_hdx.xlsx")
    cap = hdx.parse("tgo_admincapitals")[["name", "x_coord", "y_coord"]].assign(Type="chef-lieu")
    pts = hdx.parse("tgo_adminpoints")
    pts = pts[pts["admin_level"].isin([2, 3])][["name", "x_coord", "y_coord", "admin_level"]]
    pts = pts.assign(Type=np.where(pts["admin_level"] == 2, "point de préfecture", "point de canton")).drop(columns="admin_level")
    cand = pd.concat([cap, pts], ignore_index=True)
    cand = gpd.GeoDataFrame(cand, geometry=gpd.points_from_xy(cand["x_coord"], cand["y_coord"]), crs="EPSG:4326").to_crs(UTM)
    pref = gpd.read_file(GEO / "prefectures.geojson").to_crs(UTM)[["Préfecture", "geometry"]]
    cand = gpd.sjoin(cand, pref, predicate="within").drop(columns="index_right")
    cand["x"], cand["y"] = cand.geometry.x.round(0), cand.geometry.y.round(0)
    cand = cand.drop_duplicates(["Préfecture", "x", "y"])
    depart = pd.read_csv(TRAITE / "D13_points_depart_o4_08.csv").set_index("Préfecture")
    ae = gpd.read_file(GEO / "auto_ecoles.geojson")
    ae = ae[ae["Comptée (R-12)"] == True].to_crs(UTM)  # noqa: E712
    arbre_ae = cKDTree(np.c_[ae.geometry.x, ae.geometry.y])
    besoin = bh[(bh["Maille"] == "Préfecture") & (bh["Levier"] == "Auto-écoles") & (bh["Année"] == HORIZON_SITES)
                & (bh["Périmètre"] == "Levier du 08")].set_index("Territoire")["Valeur"]
    lignes, sites = [], []
    r = SE08_KM * 1000
    for p, k in besoin.items():
        c = cel[cel["Préfecture"] == p]
        xy, pop = c[["x", "y"]].to_numpy(), c["pop"].to_numpy()
        couvert = arbre_ae.query(xy, distance_upper_bound=r)[0] <= r
        avant = pop[couvert].sum()
        arbre = cKDTree(xy)
        cp = cand[cand["Préfecture"] == p].reset_index(drop=True)
        voisins = arbre.query_ball_point(cp[["x", "y"]].to_numpy(), r)
        dep = depart.loc[p, ["x_utm", "y_utm"]].to_numpy(dtype=float)
        idx = arbre.query_ball_point(dep, r)
        indicatif = avant + pop[idx][~couvert[idx]].sum()
        choisis, cv = [], couvert.copy()
        for _ in range(int(k)):
            gains = [pop[i][~cv[i]].sum() if len(i) else 0.0 for i in voisins]
            j = int(np.argmax(gains)) if gains else -1
            if j < 0 or gains[j] <= 0:
                break
            cv[voisins[j]] = True
            choisis.append(j)
            sites.append({"Préfecture": p, "Zone": pf.at[p, "Zone"], "Ordre": len(choisis), "Site": cp.at[j, "name"], "Type": cp.at[j, "Type"],
                          "x_utm": cp.at[j, "x"], "y_utm": cp.at[j, "y"], "Habitants gagnés (2022)": round(gains[j]),
                          "Niveau": NIV, "Source": "lieux candidats HDX (D13) ; grille WorldPop 2020 ramenée au recensement 2022"})
        apres = pop[cv].sum()
        tot = pop.sum()
        lignes.append({"Préfecture": p, "Zone": pf.at[p, "Zone"], "Recommandation": "REC-F1" if pf.at[p, "Recensées"] == 0 else "REC-F2",
                       "Auto-écoles à ouvrir (2029)": int(k), "Sites distincts retenus": len(choisis), "Lieux candidats": len(cp),
                       "Population (2022)": round(tot), "Couverte à 10 km, avant (%)": round(avant / tot * 100, 1),
                       "Couverte, site indicatif du 10 (%)": round(indicatif / tot * 100, 1),
                       "Couverte, sites optimisés (%)": round(apres / tot * 100, 1),
                       "Habitants couverts en plus, optimisés contre indicatif (2022)": round(apres - indicatif),
                       "Couverte, avant (2022)": round(avant), "Couverte, site indicatif (2022)": round(indicatif), "Couverte, sites optimisés (2022)": round(apres),
                       "Niveau": NIV, "Source": "grille WorldPop 2020 ramenée au recensement 2022 ; auto-écoles comptées (D6) ; D13",
                       "Note": "site indicatif : point de départ de O4-08 (10, point a) ; une auto-école de plus au même site n’étend pas la couverture"})
    e = pd.DataFrame(lignes)
    tot = e[["Population (2022)", "Couverte, avant (2022)", "Couverte, site indicatif (2022)", "Couverte, sites optimisés (2022)"]].sum()
    e.loc[len(e)] = {"Préfecture": "Ensemble des 23", "Zone": "", "Recommandation": "REC-F1 ; REC-F2",
                     "Auto-écoles à ouvrir (2029)": int(e["Auto-écoles à ouvrir (2029)"].sum()), "Sites distincts retenus": int(e["Sites distincts retenus"].sum()),
                     "Lieux candidats": int(e["Lieux candidats"].sum()), "Population (2022)": tot["Population (2022)"],
                     "Couverte à 10 km, avant (%)": round(tot["Couverte, avant (2022)"] / tot["Population (2022)"] * 100, 1),
                     "Couverte, site indicatif du 10 (%)": round(tot["Couverte, site indicatif (2022)"] / tot["Population (2022)"] * 100, 1),
                     "Couverte, sites optimisés (%)": round(tot["Couverte, sites optimisés (2022)"] / tot["Population (2022)"] * 100, 1),
                     "Habitants couverts en plus, optimisés contre indicatif (2022)": tot["Couverte, sites optimisés (2022)"] - tot["Couverte, site indicatif (2022)"],
                     "Couverte, avant (2022)": tot["Couverte, avant (2022)"], "Couverte, site indicatif (2022)": tot["Couverte, site indicatif (2022)"],
                     "Couverte, sites optimisés (2022)": tot["Couverte, sites optimisés (2022)"], "Niveau": NIV, "Source": "somme des 23 préfectures", "Note": ""}
    return e, pd.DataFrame(sites)


# --- Erratum et formules (lus par la page 7 du tableau de bord) ----------------------------------------------

def erratum(a, med, sous, route10, pays, zones10, raccord, p18):
    """erratum_A1.csv : ce que l'annexe corrige ou met en réserve dans les documents figés, et pourquoi.
    Une correction change une conclusion ; une réserve dit de quoi un chiffre dépend, sans le dire faux."""
    z = zones10[zones10["Maille"] == "Zone"].set_index("Zone")
    uni, gri = "Accès rural, uniforme (%)", "Accès rural, grille (%)"
    pu, pg = float(pays[uni]), float(pays[gri])
    dix, gr = sorted(route10), sorted(sous["grille"])
    a22 = a[(a["Maille"] == "Zone") & (a["Année"] == 2022)].set_index("Territoire")
    marge = round(float(med["grille"]) - float(a22.at["Savanes", gri]), 2)
    lignes = [{
        "ID": "A1-E1", "Type": "Correction", "Document concerné": "10, section « Les régions les moins bien desservies »",
        "Objet": "La zone qui cumule les deux retards : accès à la route et formation",
        "Ce que dit le document": f"La Centrale, avec {n(float(a22.at['Centrale', uni]), 2)} % de ruraux à moins de 2 km d’une route revêtue, "
                                  f"sous la médiane des zones ({n(float(med['uniforme']), 2)} %) ; la population rurale est supposée répartie "
                                  f"uniformément dans chaque préfecture. Pays : {n(pu, 2)} %",
        "Ce que montre l’annexe": f"Les Savanes, avec {n(float(a22.at['Savanes', gri]), 2)} % pour une médiane de {n(float(med['grille']), 2)} %, "
                                  f"soit {n(marge, 2)} point d’écart ; la Centrale passe au-dessus avec {n(float(a22.at['Centrale', gri]), 2)} %. "
                                  f"Pays : {n(pg, 2)} %. Les Plateaux restent sous la médiane dans les deux lectures",
        "Source": "grille de population WorldPop 2020 (100 m, CC BY 4.0), ramenée au recensement de 2022",
        "Conséquence": f"La recommandation de zone de la Centrale garde sa priorité haute : la Centrale reste la zone au réseau le plus dégradé "
                       f"({n(float(z.at['Centrale', 'Part en mauvais état (%)']), 1)} % de km en mauvais état, contre "
                       f"{n(float(z.at['Savanes', 'Part en mauvais état (%)']), 1)} % dans les Savanes), et la lecture « formation » ne change pas. "
                       f"Un écart de {n(marge, 2)} point ne sépare pas deux zones à ce niveau de preuve",
        "Lecture du document figé": ", ".join(dix), "Lecture de l’annexe": ", ".join(gr),
        "Niveau": NIV, "Affiché en": "page Méthodologie ; note sur les pages Priorités, Recommandations et Horizon"}, {
        "ID": "A1-R1", "Type": "Réserve", "Document concerné": "07, permis pour 1 000 habitants en âge de conduire (années 2023 et 2024)",
        "Objet": "La population de 18 ans et plus après le recensement",
        "Ce que dit le document": "Les permis délivrés sont rapportés à la population en âge de conduire, tirée des projections de l’INSEED par âge",
        "Ce que montre l’annexe": f"Les projections par âge ne raccordent pas au recensement : les 18 ans et plus font "
                                  f"{n(raccord['recensement 2022'] * 100, 1)} % de la population au recensement de 2022 et "
                                  f"{n(raccord['projection 2023 (D7)'] * 100, 1)} % dans la projection de 2023",
        "Source": "recensement 2022 (RGPH-5, Livret 02) ; projections de l’INSEED 2011-2031",
        "Conséquence": f"Les taux de 2023 et 2024 dépendent de ce saut ; leur niveau de preuve reste C. L’annexe garde le niveau du recensement "
                       f"et la seule croissance des projections : {n(float(p18[2022]))} habitants de 18 ans et plus en 2022, {n(float(p18[2031]))} en 2031. "
                       f"Le document 07 n’est pas corrigé : aucun de ses calculs n’est faux",
        "Lecture du document figé": "", "Lecture de l’annexe": "",
        "Niveau": NIV, "Affiché en": "page Méthodologie, limites majeures"}]
    return pd.DataFrame(lignes)


def formules(cibles, taux_permis, resume, part2r):
    """formules_A1.csv : les formules des estimations, en clair, pour la page Méthodologie et le ppt."""
    a0, a1, red = DECENNIE
    f = [("Auto-écoles à ouvrir dans une préfecture",
          f"arrondi supérieur de ({n(cibles['O4-05'], 3)} × population ÷ 100 000) − auto-écoles agréées existantes, si le résultat est positif",
          f"la cible est {n(cibles['O4-05'], 3)} auto-école agréée pour 100 000 habitants, la médiane des préfectures qui en ont au moins une"),
         ("Km à remettre en état dans une préfecture",
          f"km en mauvais état − ({n(cibles['O3-02'], 2)} % × km évalués), si le résultat est positif",
          f"la cible est {n(cibles['O3-02'], 2)} % de km en mauvais état, la médiane des préfectures évaluées ; la valeur ne change pas d’un horizon "
          "à l’autre, aucune donnée ne mesurant l’usure"),
         ("Km de routes classées pour Mô",
          f"{n(cibles['O4-03'], 2)} × population ÷ 10 000",
          f"la cible est {n(cibles['O4-03'], 2)} km de routes classées pour 10 000 habitants, la médiane des préfectures ; un ordre de grandeur "
          "derrière une vérification"),
         ("Permis moto à délivrer dans l’année",
          f"{n(taux_permis, 3)} × population de 18 ans et plus ÷ 1 000",
          "le taux est celui des années 2022 à 2024, la cible du document 10"),
         ("Accidents, blessés ou tués attendus sans action nouvelle",
          "taux moyen de 2022 à 2024 × population ÷ 100 000 (référence « taux inchangé ») ; le même taux prolongé par sa variation annuelle "
          "entre 2010-2012 et 2022-2024 (référence « tendance »)",
          " ; ".join(f"{m} : {n(resume[m]['taux fixe'], 2)} pour 100 000, variation de {n(resume[m]['variation'] * 100, 2)} % par an"
                     for m in ("Accidents constatés", "Blessés", "Tués"))),
         ("Cible de la Décennie d’action",
          f"valeur de {a0} × (1 − {n(red * 100)} % × (année − {a0}) ÷ {a1 - a0}), pour les blessés et les tués ; l’année {a1 + 1} garde la cible de {a1}",
          f"au moins {n(red * 100)} % de tués et de blessés en moins d’ici {a1} ({SOURCE_DECENNIE})"),
         ("Accès rural à une route revêtue",
          f"part de la population rurale dont le carreau de population est à moins de {BANDE_KM} km d’une route nationale revêtue",
          "approche de l’indice d’accès rural de la Banque mondiale ; la grille WorldPop place la population, au lieu de la supposer uniforme"),
         ("Plafond de ce que le casque pourrait éviter",
          f"tués attendus × {n(part2r * 100)} % × {n(CASQUE['Valeur'] * 100)} %",
          f"{n(part2r * 100)} % des tués de 2021 étaient des usagers de deux ou trois-roues (OMS) ; {SOURCE_CASQUE}. "
          "C’est un plafond : le taux de port du casque n’est pas publié")]
    return pd.DataFrame([{"Grandeur": g, "Formule": fo, "D’où viennent les valeurs": pq, "Niveau": NIV} for g, fo, pq in f])


# --- Sources ----------------------------------------------------------------------------------------------

def sources():
    reg = pd.read_csv(BRUT / "_SOURCES.csv").set_index("Fichier")
    lignes = []
    for f in ("projections_demographiques_2011_2031.csv", "population_region_sexe_2010.csv", "wpp2024_population_age_simple_togo.csv",
              "limites_administratives_hdx.xlsx"):
        lignes.append({"Fichier": f, "Rôle": "lu par l'annexe (A1-7)", "Page source": reg.at[f, "Page source"], "URL": reg.at[f, "URL"],
                       "Licence": reg.at[f, "Licence déclarée"], "Date de téléchargement": reg.at[f, "Date de téléchargement"],
                       "Taille (octets)": (BRUT / f).stat().st_size, "SHA-256": sha256(BRUT / f), "SHA-256 du registre (03)": reg.at[f, "SHA-256"]})
    w = reg.loc[GRILLE.name]
    lignes.append({"Fichier": GRILLE.name, "Rôle": "partie 3 (A1-9), téléchargé pour l'annexe", "Page source": w["Page source"], "URL": w["URL"],
                   "Licence": w["Licence déclarée"], "Date de téléchargement": date.fromtimestamp(GRILLE.stat().st_mtime).isoformat(),
                   "Taille (octets)": GRILLE.stat().st_size, "SHA-256": sha256(GRILLE), "SHA-256 du registre (03)": "recensé, non téléchargé au 03"})
    return pd.DataFrame(lignes)


# --- §10 Contrôles ----------------------------------------------------------------------------------------

def nombres_du_document(fichiers):
    """10-13 : chaque nombre des blocs de résultats (entre <!-- résultats --> et <!-- fin -->) se retrouve dans les CSV."""
    texte = DOCUMENT.read_text()
    blocs = re.findall(r"<!-- résultats -->(.*?)<!-- fin -->", texte, flags=re.S)
    valeurs = set()
    for d in fichiers:
        for col in d.columns:
            for x in pd.to_numeric(d[col], errors="coerce").dropna():
                for k in (0, 1, 2, 3):
                    valeurs.add(round(abs(float(x)), k))
        for x in d.astype(str).to_numpy().ravel():  # nombres écrits dans les notes et les cibles
            for m in re.findall(r"\d[\d  ]*(?:,\d+)?", x):
                valeurs.add(round(float(m.replace(" ", "").replace(" ", "").replace(",", ".")), 3))
    erreurs, total = [], 0
    for b in blocs:
        b = re.sub(r"`[^`]*`|\[[^\]]*\]\([^)]*\)", " ", b)
        b = re.sub(r"\b(?:REC-[A-Z]\d|A1-\d+|10-\d{2}|O\d-[E\d]+|SE-\d+|H\d+|S\d|R-\d+)\b|§\d+(?:\.\d+)?|écart \d+|\b(?:19|20)\d{2}\b"
                   r"|pour 1[0 ]*000(?: habitants)?|\b\d+ (?:ans?|km|m)\b|\(a\)|\(b\)", " ", b)
        for m in re.findall(r"(?<![\w,])\d{1,3}(?:[  ]\d{3})*(?:,\d+)?(?![\w])", b):
            total += 1
            x = float(m.replace(" ", "").replace(" ", "").replace(",", "."))
            dec = len(m.split(",")[1]) if "," in m else 0
            if round(x, dec) not in valeurs and x not in valeurs:
                erreurs.append(m)
    return total, erreurs, len(blocs)


def controles_A1(pf, pa, pb, N, h, d, resume, cel, brut_grille, p18_verif, rec, zones10, e, src, cibles, err, fml):
    ok1 = all(abs(pa[t].sum() - N[t]) < 1e-6 and abs(pb[t].sum() - N[t]) < 1e-6 for t in ANNEES)
    controle("10-01", "Population", "Somme des préfectures = total national, chaque année et chaque variante (R-04)",
             f"{len(ANNEES)} années × 2 variantes ; 2031 : {n(N[2031])}", ok1)
    e22 = max(float((pa[2022] - pf["Pop22"]).abs().max()), float((pb[2022] - pf["Pop22"]).abs().max()))
    e18 = max(abs(a - b) for a, b in p18_verif.values())
    controle("10-02", "Population en 2022 ; méthode des 18 ans et plus",
             "(a) = (b) = recensement, préfecture par préfecture ; la coupe à 18 ans retrouve D7 en 2023 et 2024",
             f"écart maximal en 2022 : {e22:.6f} ; écart sur les 18 ans et plus : {e18:.1f}", e22 < 1e-6 and e18 <= 1)

    def tot(levier, perim, t=2022, maille="Pays"):
        x = h[(h["Maille"] == maille) & (h["Levier"] == levier) & (h["Périmètre"] == perim) & (h["Année"] == t)]
        return float(x["Valeur"].iloc[0])
    att = {"ae_levier": pf.loc[pf["Formation"], "AE O5-04 (08)"].sum(), "km_levier": round(pf.loc[pf["Réseau"], "Km O5-04 (08)"].sum(), 1),
           "ae_tous": pf["AE O5-04 (08)"].clip(lower=0).sum(), "km_tous": round(pf["Km O5-04 (08)"].clip(lower=0).sum(), 1)}
    mes = {"ae_levier": tot("Auto-écoles", "Levier du 08"), "km_levier": tot("Remise en état", "Levier du 08"),
           "ae_tous": tot("Auto-écoles", "Toutes les préfectures"), "km_tous": tot("Remise en état", "Toutes les préfectures")}
    controle("10-03", "Reproduction du 07 et du 08", "En 2022, les sommes des colonnes O5-04 de classement_08.csv",
             " ; ".join(f"{k} : {n(mes[k], 1)} pour {n(att[k], 1)}" for k in att), all(abs(mes[k] - att[k]) < 0.05 for k in att))

    def rec_val(ident, t=2022):
        x = h[(h["Maille"] == "Recommandation") & (h["Recommandation"] == ident) & (h["Année"] == t)]
        return float(x["Valeur"].iloc[0])

    def premier(texte):
        return float(re.search(r"\d[\d  ]*(?:,\d+)?", texte).group(0).replace(" ", "").replace(" ", "").replace(",", "."))
    att10 = {"REC-R1": premier(rec.at["REC-R1", "Déficit"]), "REC-R2": premier(rec.at["REC-R2", "Déficit"]),
             "REC-F1": premier(rec.at["REC-F1", "Déficit"]), "REC-F2": premier(rec.at["REC-F2", "Déficit"]),
             "REC-R4": premier(rec.at["REC-R4", "Déficit"])}
    mes10 = {k: rec_val(k) for k in att10}
    pa_ref = d[(d["Mesure"] == "Permis A") & (d["Série"] == "observé") & (d["Année"].isin(REF))]["Valeur"].mean()
    f3 = premier(rec.at["REC-F3", "Cible"])
    loin10 = float(zones10.loc[zones10["Maille"] == "Pays", "Ruraux à plus de 2 km d’une route revêtue"].iloc[0])
    loin = tot("Accès rural", "Toutes les préfectures")
    ok4 = all(abs(mes10[k] - att10[k]) < 0.05 for k in att10) and round(pa_ref) == f3 and abs(loin - loin10) <= 1
    controle("10-04", "Reproduction du 10", "En 2022, les quantités de recommandations_10.csv et les ruraux de zones_10.csv",
             " ; ".join(f"{k} : {n(mes10[k], 1)} pour {n(att10[k], 1)}" for k in att10)
             + f" ; REC-F3 : {n(pa_ref)} pour {n(f3)} ; ruraux à plus de 2 km : {n(loin)} pour {n(loin10)}", ok4)
    v = h[h["Valeur"].notna()]
    d_ = d[d["Borne basse"].notna()]
    ok5 = bool(((v["Borne basse"] <= v["Valeur"] + 1e-9) & (v["Valeur"] <= v["Borne haute"] + 1e-9)).all()
               and ((d_["Borne basse"] <= d_["Valeur"] + 1e-9) & (d_["Valeur"] <= d_["Borne haute"] + 1e-9)).all())
    controle("10-05", "Bornes", "Borne basse ≤ valeur ≤ borne haute, sur chaque ligne", f"{len(v) + len(d_)} lignes", ok5)
    q = h[h["Valeur"].notna() & (h["Levier"] != "Accès rural")]
    neg = int((q["Valeur"] < 0).sum())
    mono = 0
    for (m, terr, lev, rc, per), g in h[h["Levier"].isin(["Auto-écoles", "Desserte de Mô", "Permis moto"])].groupby(
            ["Maille", "Territoire", "Levier", "Recommandation", "Périmètre"], dropna=False):
        s = g[g["Année"] >= ACTUEL].sort_values("Année")
        mono += int((s["Valeur"].diff().dropna() < 0).sum() + (s["Borne basse"].diff().dropna() < 0).sum())
    controle("10-06", "Sens", "Quantités positives ou nulles ; non décroissantes de 2026 à 2031 (auto-écoles, Mô, permis)",
             f"{neg} quantité négative ; {mono} baisse", neg == 0 and mono == 0)
    pr = h[h["Maille"] == "Préfecture"]
    ecart = 0.0
    for maille, cle in (("Zone", "Zone"), ("Région", "Région")):
        agg = h[(h["Maille"] == maille) & (h["Périmètre"] == "Toutes les préfectures")]
        for r in agg.itertuples():
            s = pr[(pr[cle] == r.Territoire) & (pr["Levier"] == r.Levier) & (pr["Année"] == r.Année)]["Valeur"].sum()
            ecart = max(ecart, abs(s - r.Valeur))
    nz, nr = h.loc[h["Maille"] == "Zone", "Territoire"].nunique(), h.loc[h["Maille"] == "Région", "Territoire"].nunique()
    dbl = all(abs(rec_val("REC-R1", t) + rec_val("REC-R2", t) - tot("Remise en état", "Levier du 08", t)) < 0.15
              and abs(rec_val("REC-F1", t) + rec_val("REC-F2", t) - tot("Auto-écoles", "Levier du 08", t)) < 0.5 for t in PALIERS)
    controle("10-07", "Agrégats", "6 zones, 5 régions ; agrégat = somme des préfectures (R-02, R-03) ; REC-R1 + REC-R2 et REC-F1 + REC-F2 = pays, sans double compte",
             f"{nz} zones, {nr} régions ; écart maximal {ecart:.2f} (arrondis) ; double compte : {'aucun' if dbl else 'oui'}",
             nz == 6 and nr == 5 and ecart <= 2 and dbl)
    proj_h, proj_d = h[h["Année"] > 2022], d[(d["Année"] > 2024) & ~d["Série"].isin(["observé", "observée"])]
    ok8 = bool((proj_h["Niveau"] == NIV).all() and (proj_d["Niveau"] == NIV).all()
               and proj_h["Source"].fillna("").ne("").all() and proj_d["Source"].fillna("").ne("").all())
    controle("10-08", "Niveaux", "Toute valeur projetée en C, avec sa source", f"{len(proj_h) + len(proj_d)} lignes projetées", ok8)
    ok9 = all(abs(resume[m]["cible"][2030] - 0.5 * resume[m]["s"][2021]) < 1e-6 for m in ("Blessés", "Tués"))
    controle("10-09", "Cible de la Décennie", "En 2030 : moitié de la valeur de 2021, blessés et tués",
             " ; ".join(f"{m} : {n(resume[m]['cible'][2030])} pour {n(resume[m]['s'][2021])} en 2021" for m in ("Blessés", "Tués")), ok9)
    terr = h[(h["Maille"] != "Recommandation") & h["Levier"].isin(["Permis moto"])]
    controle("10-10", "Maille nationale", "Aucune ligne territoriale pour les permis et les accidents",
             f"{len(terr)} ligne territoriale ; national_A1.csv sans colonne de territoire",
             len(terr) == 0 and "Territoire" not in d.columns)
    pl = d[d["Série"].str.startswith("Plafond")]
    tu = d[(d["Mesure"] == "Tués") & d["Série"].isin(["Taux inchangé", "Tendance"])]
    ok11 = len(pl) == len(tu) and pl["Source"].str.contains("Cochrane").all() and pl["Source"].str.contains("OMS").all()
    p2r = float(pd.read_csv(TRAITE / "D3_victimes_usager_2021.csv").set_index("Type d'usager").at["Deux et trois-roues motorisés", "Part des tués déclarés (%)"]) / 100
    ex = tu[tu["Série"] == "Taux inchangé"].set_index("Année")["Valeur"] * p2r * CASQUE["Valeur"]
    ok11 = ok11 and float((pl[pl["Série"] == "Plafond du casque (taux inchangé)"].set_index("Année")["Valeur"] - ex).abs().max()) <= 1
    controle("10-11", "Plafond du casque", "Produit de la part des deux-roues parmi les tués (OMS) et de l’effet du casque (Cochrane)",
             f"{n(p2r * 100)} % × {n(CASQUE['Valeur'] * 100)} % = {n(p2r * CASQUE['Valeur'] * 100, 1)} % des tués", ok11)
    g = cel.groupby("Préfecture")[["pop", "rurale"]].sum()
    e12 = max(float((g["pop"] - pf["Pop22"]).abs().max()), float((g["rurale"] - pf["Rurale22"]).abs().max()))
    controle("10-12", "Grille WorldPop", "Grille ramenée = population et population rurale de chaque préfecture",
             f"{len(cel)} carreaux peuplés ; {n(brut_grille)} habitants dans la grille brute ; écart maximal {e12:.4f}", e12 < 0.01)
    total, introuvables, nb = nombres_du_document([h, d, e, err, fml, pd.DataFrame(controles), pd.read_csv(SORTIE / "population_A1.csv"), pd.read_csv(SORTIE / "acces_A1.csv"),
                                          pd.read_csv(SORTIE / "emplacements_A1.csv"), pd.read_csv(SORTIE / "sites_A1.csv"),
                                          pd.DataFrame({"cibles": list(cibles.values()) + [CASQUE["Valeur"] * 100, 58.0]})])
    controle("10-13", "Chiffres du document", "Chaque nombre des blocs de résultats se retrouve dans les CSV",
             f"{nb} blocs, {total} nombres, {len(introuvables)} introuvable(s)"
             f"{' : ' + ', '.join(introuvables[:10]) if introuvables else ''}", nb > 0 and not introuvables)
    s = src[src["Fichier"] != GRILLE.name]
    ok14 = bool((s["SHA-256"] == s["SHA-256 du registre (03)"]).all()) and src.loc[src["Fichier"] == GRILLE.name, "SHA-256"].str.len().eq(64).all()
    controle("10-14", "Sources", "Fichiers bruts identiques au registre du 03 ; empreinte de la grille consignée",
             f"{int((s['SHA-256'] == s['SHA-256 du registre (03)']).sum())} sur {len(s)} identiques ; grille {src.loc[src['Fichier'] == GRILLE.name, 'SHA-256'].iloc[0][:12]}…", ok14)
    champs = ["Document concerné", "Objet", "Ce que dit le document", "Ce que montre l’annexe", "Source", "Conséquence"]
    ok15 = bool(err[champs].apply(lambda c: c.str.strip().ne("")).all().all() and len(err) >= 1
                and set(err["Type"]) <= {"Correction", "Réserve"}
                and fml[["Grandeur", "Formule", "D’où viennent les valeurs"]].apply(lambda c: c.str.strip().ne("")).all().all())
    controle("10-15", "Erratum et formules",
             "Chaque ligne de l’erratum nomme le document, la source et la conséquence ; chaque formule dit d’où viennent ses valeurs",
             f"{int((err['Type'] == 'Correction').sum())} correction(s), {int((err['Type'] == 'Réserve').sum())} réserve(s), "
             f"{len(fml)} formules", ok15)


# --- Principal ----------------------------------------------------------------------------------------------

def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    pf, cibles, rec, zones10 = lire()
    pa, pb, N, popdf, croissance = population(pf)
    popdf.to_csv(SORTIE / "population_A1.csv", index=False)
    part, bande = part_surface_proche()
    p18, p18_verif, raccord = population_18(N)
    d, permis, resume, part2r, taux = national(N, p18, raccord)
    d.to_csv(SORTIE / "national_A1.csv", index=False)
    bp = besoins_prefectures(pf, cibles, pa, pb, part)
    h = table_horizon(bp, pf, cibles, rec, N, permis)
    h.to_csv(SORTIE / "horizon_A1.csv", index=False)
    cel, brut_grille = grille(pf, bande)
    a, pacc, med, sous, route10, verdict, pays = acces_grille(cel, pf, part, pb, zones10)
    a.to_csv(SORTIE / "acces_A1.csv", index=False)
    e, sites = emplacements(cel, pf, h)
    e.to_csv(SORTIE / "emplacements_A1.csv", index=False)
    sites.to_csv(SORTIE / "sites_A1.csv", index=False)
    err = erratum(a, med, sous, route10, pays, zones10, raccord, p18)
    err.to_csv(SORTIE / "erratum_A1.csv", index=False)
    fml = formules(cibles, taux, resume, part2r)
    fml.to_csv(SORTIE / "formules_A1.csv", index=False)
    src = sources()
    src.to_csv(SORTIE / "sources_A1.csv", index=False)
    controles_A1(pf, pa, pb, N, h, d, resume, cel, brut_grille, p18_verif, rec, zones10, e, src, cibles, err, fml)
    ct = pd.DataFrame(controles)
    ct.to_csv(SORTIE / "controles_A1.csv", index=False)

    # Résumé pour la rédaction (aucun chiffre n'est recopié : le document est relu par 10-13)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("cibles :", cibles, "; croissance régionale :\n", croissance.round(3))
    print("N :", {t: int(N[t]) for t in ANNEES}, "; part des 18 ans et plus :", raccord)
    for lev, per in (("Auto-écoles", "Levier du 08"), ("Auto-écoles", "Toutes les préfectures"), ("Remise en état", "Levier du 08"),
                     ("Accès rural", "Toutes les préfectures")):
        x = h[(h["Maille"].isin(["Pays", "Zone"])) & (h["Levier"] == lev) & (h["Périmètre"] == per)]
        print(f"\n{lev} — {per}\n", x.pivot_table(index="Territoire", columns="Année", values="Valeur", aggfunc="first"))
    r = h[h["Maille"] == "Recommandation"]
    print("\n", r.pivot_table(index="Recommandation", columns="Année", values="Valeur", aggfunc="first"))
    print(r[r["Palier de l’horizon"] == True][["Recommandation", "Année", "Valeur", "Borne basse", "Borne haute", "Population"]])  # noqa: E712
    nat = d[d["Année"].isin(PALIERS)]
    print("\n", nat.pivot_table(index=["Mesure", "Série"], columns="Année", values="Valeur", aggfunc="first"))
    print({m: (round(resume[m]["taux fixe"], 2), round(resume[m]["variation"] * 100, 2)) for m in resume}, "taux permis", round(taux, 3))
    print("\naccès :", med, sous, route10, verdict)
    print(a[(a["Maille"].isin(["Zone", "Pays"])) & (a["Année"].isin([2022, 2031]))].to_string())
    print(e.to_string())
    print(ct.to_string())


if __name__ == "__main__":
    main()
