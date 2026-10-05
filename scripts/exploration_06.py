"""Étape 06 : exploration (06_exploration.md).

Lit les tables du 05 (data/processed/) et data/reference/ ; n'écrit rien dans data/processed/.
Calcule chaque chiffre cité dans le 06 (R-19) :
- les rapports d'exploration, au national et par zone, avec la formule du 02 (§1) ;
- les variables par préfecture (§3, §4) ;
- les distributions et les valeurs atypiques, par la règle de Tukey (§4) ;
- les paires de préfectures voisines (§7, contradiction 3) ;
- les comparaisons de sources nouvelles (§5) ;
- les cinq contradictions et les signaux (§4, §7).

Aucun seuil du 02, aucun rang, aucun score : ils viennent au 08 (§9). Les règles du §4 s'appliquent aux
valeurs telles qu'écrites dans les CSV, donc arrondies. Distances et frontières en UTM 31N (R-16).
Un rapport sans dénominateur est « non défini » (case vide), jamais 0 (R-10).

Sorties, dans data/analysis/06_exploration/ : rapports_06.csv, prefectures_06.csv, distributions_06.csv,
voisines_06.csv, comparaisons_06.csv, signaux_06.csv.

Usage : .venv/bin/python scripts/exploration_06.py
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
TRAITE = RACINE / "data" / "processed"
REFERENCE = RACINE / "data" / "reference"
SORTIE = RACINE / "data" / "analysis" / "06_exploration"

UTM31N = 32631
ZONES = ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]
GROUPES = ["Moto", "Voiture", "Poids lourd", "Bus et car", "Autres"]
ETATS = {"km_etat_bon": "Bon", "km_etat_moyen": "Moyen", "km_etat_mauvais": "Mauvais", "km_etat_travaux": "Travaux"}
TYPES_ROUTE = {"km_rn_revetue": "Km de route nationale revêtue", "km_rn_non_revetue": "Km de route nationale non revêtue",
               "km_piste_rurale": "Km de piste rurale", "km_voirie_urbaine": "Km de voirie urbaine"}
ARRONDI_PCT = 0.05  # écart toléré entre deux pourcentages publiés, comme au 05 (anomalie 1)
TERCILES = {"Part en mauvais état (%)": "SE-04", "Km pour 10 000 habitants": "SE-06",
            "Auto-écoles comptées pour 100 000 habitants": "SE-07"}  # seuils du 02 en terciles, à la préfecture

# Variables par préfecture passées aux règles du §4 : indicateur du 02, unité, niveau de preuve (R-17), décimales
VARIABLES = {
    "Population 2022": ("O5-03 ; dénominateur de O4-03 et O4-05", "habitants", "A", 0),
    "Km de routes classées": ("O4-01", "km", "B", 1),
    **{nom: ("O4-01", "km", "B", 1) for nom in TYPES_ROUTE.values()},
    "Km pour 10 000 habitants": ("O4-03", "km pour 10 000 habitants", "B", 2),
    "Km pour 1 000 km²": ("O4-02", "km pour 1 000 km²", "B", 1),
    "Part en mauvais état (%)": ("O3-02", "%", "C", 1),
    "Part en travaux (%)": ("O3-03", "%", "C", 1),
    "Part non évaluée (%)": ("O3-06", "%", "B", 1),
    "Auto-écoles recensées": ("O4-04", "nombre", "A", 0),
    "Auto-écoles comptées": ("O4-04", "nombre", "A", 0),
    "Auto-écoles comptées pour 100 000 habitants": ("O4-05", "pour 100 000 habitants", "C", 2),
    "Distance à l’auto-école comptée la plus proche (km)": ("O4-08", "km", "C", 1),
}
# Séries nationales passées à la règle des variations atypiques (§4) : rapport de rapports_06.csv
SERIES = {"Variation annuelle : immatriculations": "O1",
          "Variation annuelle : permis délivrés": "O1",
          "Variation annuelle : population": "O1",
          "Variation annuelle : accidents, tués, blessés": "O2"}

rapports, signaux = [], []


def exiger(condition, message):
    if not condition:
        raise ValueError(message)


def n(x, decimales=0, signe=False):
    s = f"{x:+,.{decimales}f}" if signe else f"{x:,.{decimales}f}"
    return s.replace(",", " ").replace(".", ",")


def lire(nom):
    return pd.read_csv(TRAITE / f"{nom}.csv")


def quotient(num, den, facteur, decimales):
    """Rapport arrondi ; non défini (NaN) si un terme manque ou si le dénominateur est nul."""
    if pd.isna(num) or pd.isna(den) or den == 0:
        return np.nan
    return round(num / den * facteur, decimales)


def quotients(num, den, facteur, decimales):
    return (num / den.where(den > 0) * facteur).round(decimales)


def niveau(*niveaux):
    """Un rapport est calculé (B), ou estimé (C) si l'un de ses termes l'est (R-17)."""
    return "C" if "C" in niveaux else "B"


def rapport(maille, territoire, annee, categorie, nom, indicateur, num, den, valeur, unite, niv, note="",
            basse=np.nan, haute=np.nan):
    rapports.append({"Maille": maille, "Territoire": territoire, "Année": annee, "Catégorie": categorie,
                     "Rapport": nom, "Indicateur": indicateur, "Numérateur": num, "Dénominateur": den,
                     "Valeur": valeur, "Borne basse": basse, "Borne haute": haute, "Unité": unite,
                     "Niveau": niv, "Note": note})


def variations(tableau, mesure, indicateur, niveaux=None, note=""):
    """Variation annuelle en %, de l'année précédente à l'année ; non définie si l'une manque ou vaut 0."""
    for col in tableau.columns:
        s = tableau[col]
        for an in s.index:
            if an - 1 not in s.index:
                continue
            niv = niveau(niveaux[an], niveaux[an - 1]) if niveaux is not None else "B"
            num, den = s.at[an], s.at[an - 1]
            valeur = round((num / den - 1) * 100, 1) if pd.notna(num) and pd.notna(den) and den > 0 else np.nan
            rapport("National", "Togo", an, col, f"Variation annuelle : {mesure}", indicateur, num, den, valeur, "%", niv, note)


# --- O1 et O2 : séries nationales --------------------------------------------------------------------

def national():
    pop = lire("D7_population_nationale").set_index("Année")
    np_pop = pop["Niveau"].to_dict()

    d1 = lire("D1_immatriculations")
    imm = d1.pivot_table(index="Année", columns="Groupe", values="Immatriculations", aggfunc="sum")[GROUPES]
    imm["Ensemble"] = imm.sum(axis=1)
    for an in imm.index:
        for g in GROUPES:
            rapport("National", "Togo", an, g, "Part de chaque groupe", "O1-02", imm.at[an, g], imm.at[an, "Ensemble"],
                    quotient(imm.at[an, g], imm.at[an, "Ensemble"], 100, 1), "%", "B")
        for g in GROUPES + ["Ensemble"]:
            rapport("National", "Togo", an, g, "Immatriculations pour 1 000 habitants", "O1-04", imm.at[an, g],
                    pop.at[an, "Population"], quotient(imm.at[an, g], pop.at[an, "Population"], 1000, 2),
                    "pour 1 000 habitants", niveau(np_pop[an]))
    variations(imm[GROUPES], "immatriculations", "O1-03")
    variations(pop[["Population"]].rename(columns={"Population": "Togo"}), "population",
               "dénominateur des taux par habitant (R-06)", np_pop, "raccord entre sources si les deux années n’ont pas la même source")

    d2 = lire("D2_permis")
    permis = d2.pivot(index="Année", columns="Catégorie", values="Permis délivrés")  # 2013 reste vide (R-10)
    variations(permis, "permis délivrés", "O1-06", note="2013 non renseignée : variations de 2013 et 2014 non définies")

    age = lire("D7_population_age_conduire").pivot(index="Année", columns="Catégorie", values="Population en âge de conduire")
    for an in permis.index:
        for cat in permis.columns:
            rapport("National", "Togo", an, cat, "Permis pour 1 000 habitants en âge de conduire", "O1-07",
                    permis.at[an, cat], age.at[an, cat], quotient(permis.at[an, cat], age.at[an, cat], 1000, 2),
                    "pour 1 000 habitants en âge de conduire", "C")

    corr = pd.read_csv(REFERENCE / "correspondance_vehicules_permis.csv", keep_default_na=False)
    par_type = d1.pivot_table(index="Année", columns="Type", values="Immatriculations", aggfunc="sum")
    for _, c in corr.iterrows():
        types = [t.strip() for t in c["Types immatriculés (D1)"].split("|") if t.strip()]
        if not types:
            continue  # F : aucun type immatriculé à part (05 §6)
        cat = c["Catégorie"]
        immcat = par_type[types].sum(axis=1)
        communs = [an for an in permis.index if pd.notna(permis.at[an, cat]) and an in immcat.index]
        for an in communs:
            rapport("National", "Togo", an, cat, "Immatriculations pour un permis délivré", "O1-09", immcat[an],
                    permis.at[an, cat], quotient(immcat[an], permis.at[an, cat], 1, 2), "ratio", "B", " + ".join(types))
        rapport("National", "Togo", f"{min(communs)}–{max(communs)}", cat, "Immatriculations pour un permis délivré",
                "O1-09", immcat[communs].sum(), permis.loc[communs, cat].sum(),
                quotient(immcat[communs].sum(), permis.loc[communs, cat].sum(), 1, 2), "ratio", "B",
                f"cumul des années communes, sans 2013 ; {' + '.join(types)}")

    parc = lire("D1_parc_estime").dropna(subset=["Borne basse", "Valeur centrale", "Borne haute"])
    for _, p in parc.iterrows():
        rapport("National", "Togo", p["Année"], p["Groupe"], "Largeur de la fourchette du parc estimé", "O1-05",
                p["Borne haute"] - p["Borne basse"], p["Valeur centrale"],
                quotient(p["Borne haute"] - p["Borne basse"], p["Valeur centrale"], 100, 1), "% de la valeur centrale", "C",
                "(borne haute − borne basse) / valeur centrale")

    d3 = lire("D3_accidents").pivot(index="Année", columns="Mesure", values="Valeur")
    ens = parc[parc["Groupe"] == "Ensemble"].set_index("Année")
    for an in d3.index:
        acc, tues, bles, hab = d3.at[an, "Accidents constatés"], d3.at[an, "Tués"], d3.at[an, "Blessés"], pop.at[an, "Population"]
        rapport("National", "Togo", an, "", "Accidents constatés pour 100 000 habitants", "O2-03", acc, hab,
                quotient(acc, hab, 1e5, 1), "pour 100 000 habitants", niveau(np_pop[an]), "accidents constatés (écart 15)")
        rapport("National", "Togo", an, "", "Tués pour 100 000 habitants", "O2-02", tues, hab,
                quotient(tues, hab, 1e5, 2), "pour 100 000 habitants", niveau(np_pop[an]))
        rapport("National", "Togo", an, "", "Tués pour 100 accidents", "O2-05", tues, acc, quotient(tues, acc, 100, 1),
                "pour 100 accidents constatés", "B")
        rapport("National", "Togo", an, "", "Blessés pour 100 accidents", "O2-06", bles, acc, quotient(bles, acc, 100, 1),
                "pour 100 accidents constatés", "B")
        if an in ens.index:
            v = ens.loc[an]
            rapport("National", "Togo", an, "", "Tués pour 10 000 véhicules", "O2-04", tues, v["Valeur centrale"],
                    quotient(tues, v["Valeur centrale"], 1e4, 2), "pour 10 000 véhicules du parc estimé", "C",
                    "bornes : parc estimé haut, puis bas (PA-01)",
                    basse=quotient(tues, v["Borne haute"], 1e4, 2), haute=quotient(tues, v["Borne basse"], 1e4, 2))
    variations(d3[["Accidents constatés", "Tués", "Blessés"]], "accidents, tués, blessés", "O2-01")


# --- O3, O4, O5 : préfectures et zones --------------------------------------------------------------

def distances():
    """Distance à vol d'oiseau (UTM 31N, R-16) de chaque point de départ (D13) à l'auto-école comptée la plus proche."""
    pts = lire("D13_points_depart_o4_08").set_index("Préfecture")
    ae = lire("D6_auto_ecoles")
    ae = ae[ae["Comptée (R-12)"]].reset_index(drop=True)
    dx = pts["x_utm"].to_numpy()[:, None] - ae["x_utm"].to_numpy()[None, :]
    dy = pts["y_utm"].to_numpy()[:, None] - ae["y_utm"].to_numpy()[None, :]
    d = np.hypot(dx, dy)
    proche = d.argmin(axis=1)
    return pd.DataFrame({"Distance à l’auto-école comptée la plus proche (km)": (d.min(axis=1) / 1000).round(1),
                         "Préfecture de l’auto-école la plus proche": ae.loc[proche, "Préfecture"].to_numpy(),
                         "Origine du point de départ": pts["Origine"].to_numpy()}, index=pts.index)


def prefectures():
    t = lire("table_maitresse_prefecture")
    exiger(len(t) == 39, "table maîtresse : 39 préfectures attendues")
    p = t[["Préfecture", "Région", "Zone"]].copy()
    pop = t["population_2022"]
    part_urbaine = t["population_2022_urbaine"] / pop * 100
    p["Population 2022"] = pop
    p["Part urbaine (%)"] = part_urbaine.round(1)
    # PA-03 : Grand Lomé urbain par règle ; ailleurs, urbaine si plus de 50 % de la population est urbaine
    p["Classe PA-03"] = np.where(t["Zone"] == "Grand Lomé", "urbaine", np.where(part_urbaine > 50, "urbaine", "rurale"))
    km = t[list(TYPES_ROUTE)].sum(axis=1)
    rn = t["km_rn_revetue"] + t["km_rn_non_revetue"]
    evalues = t[list(ETATS)].sum(axis=1)
    p["Km de routes classées"] = km.round(1)
    for col, nom in TYPES_ROUTE.items():
        p[nom] = t[col].round(1)
    p["Km pour 10 000 habitants"] = quotients(km, pop, 1e4, 2)
    p["Surface (km²)"] = t["Surface (km²)"]
    p["Km pour 1 000 km²"] = quotients(km, t["Surface (km²)"], 1e3, 1)
    p["Km de routes nationales"] = rn.round(1)
    p["Km évalués"] = evalues.round(1)
    for col, etat in ETATS.items():
        p[f"Km {etat.lower()}"] = t[col].round(1)
    p["Km non évalués"] = t["km_rn_non_evaluee"].round(1)
    p["Part en bon état (%)"] = quotients(t["km_etat_bon"], evalues, 100, 1)
    p["Part en état moyen (%)"] = quotients(t["km_etat_moyen"], evalues, 100, 1)
    p["Part en mauvais état (%)"] = quotients(t["km_etat_mauvais"], evalues, 100, 1)
    p["Part en travaux (%)"] = quotients(t["km_etat_travaux"], evalues, 100, 1)
    p["Part non évaluée (%)"] = quotients(t["km_rn_non_evaluee"], rn, 100, 1)
    p["Auto-écoles recensées"] = t["auto_ecoles_recensees"]
    p["Auto-écoles comptées"] = t["auto_ecoles_comptees"]
    p["Auto-écoles comptées pour 100 000 habitants"] = quotients(t["auto_ecoles_comptees"].astype(float), pop, 1e5, 2)
    p["Habitants par auto-école comptée"] = quotients(pop.astype(float), t["auto_ecoles_comptees"], 1, 0).astype("Int64")
    p = p.join(distances(), on="Préfecture")
    tr = lire("D4_etat_troncons")
    traverse = tr["Préfectures traversées"].str.split(" ; ").explode().value_counts()
    p["Tronçons du relevé"] = p["Préfecture"].map(traverse).fillna(0).astype(int)  # 0 : aucun tronçon ne la traverse
    p = p.sort_values("Préfecture").reset_index(drop=True)
    p.to_csv(SORTIE / "prefectures_06.csv", index=False)
    return t, p


def zones(t):
    """Rapports par zone (R-02) : sommes des numérateurs et des dénominateurs des préfectures."""
    z = t.assign(km=t[list(TYPES_ROUTE)].sum(axis=1), rn=t["km_rn_revetue"] + t["km_rn_non_revetue"],
                 evalues=t[list(ETATS)].sum(axis=1)).groupby("Zone")[
        ["population_2022", "auto_ecoles_comptees", "km", "Surface (km²)", "rn", "evalues", "km_etat_mauvais",
         "km_etat_travaux", "km_rn_non_evaluee"]].sum()
    pays = z.sum()
    for zone in ZONES:
        r = z.loc[zone]
        lignes = [
            ("Part de la population", "H8", r["population_2022"], pays["population_2022"], 100, 1, "% du pays", "B"),
            ("Part des auto-écoles comptées", "H8", r["auto_ecoles_comptees"], pays["auto_ecoles_comptees"], 100, 1, "% du pays", "C"),
            ("Auto-écoles comptées pour 100 000 habitants", "O4-05", r["auto_ecoles_comptees"], r["population_2022"], 1e5, 2, "pour 100 000 habitants", "C"),
            ("Km pour 10 000 habitants", "O4-03", r["km"], r["population_2022"], 1e4, 2, "km pour 10 000 habitants", "B"),
            ("Km pour 1 000 km²", "O4-02", r["km"], r["Surface (km²)"], 1e3, 1, "km pour 1 000 km²", "B"),
            ("Part en mauvais état", "O3-02", r["km_etat_mauvais"], r["evalues"], 100, 1, "% des km évalués", "C"),
            ("Part en travaux", "O3-03", r["km_etat_travaux"], r["evalues"], 100, 1, "% des km évalués", "C"),
            ("Part non évaluée", "O3-06", r["km_rn_non_evaluee"], r["rn"], 100, 1, "% des km de routes nationales", "B"),
        ]
        for nom, ind, num, den, k, d, unite, niv in lignes:
            rapport("Zone", zone, 2022, "", nom, ind, round(num, 3), round(den, 3), quotient(num, den, k, d), unite, niv)
    menages = lire("D12_menages_zone")
    for _, m in menages.iterrows():
        rapport("Zone", m["Zone"], "2021-2022", m["Mesure"], "Part des ménages", "contexte (D12)",
                m["Ménages concernés (pondérés)"], m["Ménages ayant rempli la section (pondérés)"],
                quotient(m["Ménages concernés (pondérés)"], m["Ménages ayant rempli la section (pondérés)"], 100, 1),
                "% des ménages ayant rempli la section", "C", "EHCVM, pondérée ; ménages non renseignés hors du dénominateur (R-10)")


def troncons():
    """Part en mauvais état de chaque groupe de tronçons rattachés au même tracé (carte de O3-05)."""
    tr = lire("D4_etat_troncons")
    g = tr.groupby("Noms du tracé").agg(Tronçons=("Tronçon", " | ".join), mauvais=("km_mauvais", "sum"), total=("km_total", "sum"))
    for noms, r in g.sort_index().iterrows():
        rapport("Tronçon", noms, 2020, r["Tronçons"], "Part en mauvais état", "O3-05", round(r["mauvais"], 2),
                round(r["total"], 2), quotient(r["mauvais"], r["total"], 100, 1), "% des km du tronçon", "C",
                "Territoire : noms du tracé ; Catégorie : tronçons du relevé rattachés à ce tracé")


# --- §4 : distributions et positions ------------------------------------------------------------------

def quartiles(v):
    v = v.dropna()
    q1, med, q3 = (round(float(x), 4) for x in v.quantile([0.25, 0.5, 0.75]))
    ei = round(q3 - q1, 4)
    return q1, med, q3, ei, round(q1 - 1.5 * ei, 4), round(q3 + 1.5 * ei, 4)


def position(valeur, q1, q3):
    """Haut : ≥ Q3 ; bas : ≤ Q1 ; ex aequo compris. Si Q1 = Q3, haut et bas restent stricts de part et d'autre."""
    if pd.isna(valeur):
        return "non défini"
    if valeur >= q3 and valeur > q1:
        return "haut"
    if valeur <= q1 and valeur < q3:
        return "bas"
    return "milieu"


def distributions(p):
    lignes, positions = [], pd.DataFrame({"Préfecture": p["Préfecture"]})
    for var, (ind, unite, niv, dec) in VARIABLES.items():
        v = p.set_index("Préfecture")[var].astype(float)
        q1, med, q3, ei, tb, th = quartiles(v)
        atyp = v[(v < tb) | (v > th)].sort_values(ascending=False)
        positions[var] = [position(x, q1, q3) for x in v]
        lignes.append({"Maille": "Préfecture", "Variable": var, "Indicateur": ind, "Unité": unite, "Effectif": int(v.notna().sum()),
                       "Non définis": int(v.isna().sum()), "Minimum": v.min(), "Q1": q1, "Médiane": med, "Q3": q3,
                       "Maximum": v.max(), "Écart interquartile": ei, "Borne basse de Tukey": tb, "Borne haute de Tukey": th,
                       "Valeurs atypiques": " ; ".join(f"{k} ({n(x, dec)})" for k, x in atyp.items()),
                       "Nombre d’atypiques": len(atyp), "Hautes (≥ Q3)": int((positions[var] == "haut").sum()),
                       "Basses (≤ Q1)": int((positions[var] == "bas").sum()),
                       "Ex aequo au minimum": int((v == v.min()).sum()), "Niveau": niv})
    r = pd.DataFrame(rapports)
    for mesure in SERIES:
        s = r[r["Rapport"] == mesure]
        for cat, serie in s.groupby("Catégorie", sort=False):
            v = serie.set_index("Année")["Valeur"].astype(float)
            q1, med, q3, ei, tb, th = quartiles(v)
            atyp = v[(v < tb) | (v > th)]
            lignes.append({"Maille": "Série nationale", "Variable": f"{mesure} ({cat})", "Indicateur": serie["Indicateur"].iloc[0],
                           "Unité": "%", "Effectif": int(v.notna().sum()), "Non définis": int(v.isna().sum()),
                           "Minimum": v.min(), "Q1": q1, "Médiane": med, "Q3": q3, "Maximum": v.max(), "Écart interquartile": ei,
                           "Borne basse de Tukey": tb, "Borne haute de Tukey": th,
                           "Valeurs atypiques": " ; ".join(f"{int(a)} ({n(x, 1, True)} %)" for a, x in atyp.items()),
                           "Nombre d’atypiques": len(atyp), "Hautes (≥ Q3)": np.nan, "Basses (≤ Q1)": np.nan,
                           "Ex aequo au minimum": np.nan, "Niveau": niveau(*serie["Niveau"])})
    d = pd.DataFrame(lignes)
    d.to_csv(SORTIE / "distributions_06.csv", index=False)
    return d, positions.set_index("Préfecture")


def voisines(p, positions):
    """Paires de préfectures ayant une frontière commune (longueur > 0 ; un point de contact ne compte pas)."""
    g = gpd.read_file(TRAITE / "geo" / "prefectures.geojson").to_crs(UTM31N)[["Préfecture", "geometry"]]
    j = gpd.sjoin(g, g, predicate="intersects")
    j = j[j["Préfecture_left"] < j["Préfecture_right"]]
    geom = g.set_index("Préfecture").geometry
    lignes = []
    variables = ["Km pour 10 000 habitants", "Auto-écoles comptées pour 100 000 habitants", "Part en mauvais état (%)",
                 "Part non évaluée (%)"]
    v = p.set_index("Préfecture")
    for a, b in sorted(zip(j["Préfecture_left"], j["Préfecture_right"])):
        km = geom[a].boundary.intersection(geom[b].boundary).length / 1000
        if km <= 0:
            continue
        for var in variables:
            pa, pb = positions.at[a, var], positions.at[b, var]
            lignes.append({"Préfecture A": a, "Préfecture B": b, "Frontière commune (km)": round(km, 1), "Variable": var,
                           "Valeur A": v.at[a, var], "Valeur B": v.at[b, var], "Position A": pa, "Position B": pb,
                           "Très différentes": {pa, pb} == {"haut", "bas"}})
    d = pd.DataFrame(lignes)
    exiger(set(d["Préfecture A"]) | set(d["Préfecture B"]) == set(p["Préfecture"]), "voisines : une préfecture sans voisine")
    d.to_csv(SORTIE / "voisines_06.csv", index=False)
    return d


# --- §5 : comparaisons de sources ---------------------------------------------------------------------

def comparaisons():
    lignes = []
    tr = lire("D4_etat_troncons")
    an = lire("D4_etat_national_pct")
    an = an[an["Année"] == 2020].set_index(["Catégorie de route", "État"])["Part (%)"]
    categories = {"Routes nationales revêtues": tr["Type"] == "revêtue", "Routes nationales non revêtues": tr["Type"] == "non revêtue",
                  "Routes nationales revêtues et non revêtues": tr["Type"].notna()}
    for cat, masque in categories.items():
        total = tr.loc[masque, "km_total"].sum()
        for col, etat in {"km_bon": "Bon", "km_moyen": "Moyen", "km_mauvais": "Mauvais", "km_travaux": "En travaux"}.items():
            releve = quotient(tr.loc[masque, col].sum(), total, 100, 2)
            publie = an.get((cat, etat), np.nan)
            ecart = round(releve - publie, 2) if pd.notna(publie) else np.nan
            lignes.append({"Comparaison": "État national de 2020 : relevé des 84 tronçons face à l’annuaire 39.2",
                           "Élément": f"{cat} : {etat.lower()}", "Source 1": "relevé de 2020 (D4_etat_troncons)", "Valeur 1": releve,
                           "Source 2": "annuaire 2024, tableau 39.2 (D4_etat_national_pct)", "Valeur 2": publie,
                           "Écart (points)": ecart, "Unité": "% des km",
                           "Identiques": abs(ecart) <= ARRONDI_PCT if pd.notna(ecart) else np.nan,
                           "Note": "« - » dans l’annuaire : non renseigné (R-10)" if pd.isna(publie) else ""})
    dhs = lire("D12_dhs_region")
    dhs = dhs[(dhs["Année"] == 2017) & (dhs["Indicateur"] == "Ménages possédant une moto")]
    zone_dhs = {"..Lomé": "Grand Lomé", "..Maritime": "Maritime hors Grand Lomé", "Plateaux": "Plateaux",
                "Centrale": "Centrale", "Kara": "Kara", "Savanes": "Savanes"}
    dhs = dhs[dhs["Région (libellé DHS)"].isin(zone_dhs)].assign(Zone=lambda d: d["Région (libellé DHS)"].map(zone_dhs)).set_index("Zone")
    r = pd.DataFrame(rapports)
    ehcvm = r[(r["Rapport"] == "Part des ménages") & (r["Catégorie"] == "Possède une moto")].set_index("Territoire")["Valeur"]
    ordre_dhs = dhs["Part des ménages (%)"].rank(ascending=False, method="min").astype(int)
    ordre_ehcvm = ehcvm.rank(ascending=False, method="min").astype(int)
    for zone in ZONES:
        lignes.append({"Comparaison": "Ménages possédant une moto : DHS 2017, puis EHCVM 2021-2022",
                       "Élément": zone, "Source 1": f"DHS 2017 ({dhs.at[zone, 'Région (libellé DHS)']})",
                       "Valeur 1": dhs.at[zone, "Part des ménages (%)"], "Source 2": "EHCVM 2021-2022 (D12_menages_zone)",
                       "Valeur 2": ehcvm[zone], "Écart (points)": round(ehcvm[zone] - dhs.at[zone, "Part des ménages (%)"], 1),
                       "Unité": "% des ménages", "Identiques": np.nan,
                       "Note": f"ordre parmi les 6 zones (1 = la plus forte part) : DHS {ordre_dhs[zone]}, EHCVM {ordre_ehcvm[zone]}"
                               + (" ; périmètres à comparer : « Lomé » de la DHS, Grand Lomé de l’EHCVM (4.3-03)" if zone == "Grand Lomé" else "")})
    d = pd.DataFrame(lignes)
    d.to_csv(SORTIE / "comparaisons_06.csv", index=False)
    return d, (ordre_dhs.reindex(ZONES) == ordre_ehcvm.reindex(ZONES)).all()


# --- §7 et §4 : contradictions et signaux -------------------------------------------------------------

def signal(objectif, resume, table, territoire, ampleur, regle, niv, question, indicateurs):
    signaux.append({"ID": f"SIG-{len(signaux) + 1:02d}", "Résumé": resume, "Objectif": objectif, "Table et colonne": table,
                    "Territoire ou période": territoire, "Ampleur": ampleur, "Règle": regle, "Niveau": niv,
                    "Question transmise": question, "Indicateurs et hypothèses": indicateurs})


def liste(noms, p=None):
    if not len(noms):
        return "aucune"
    if p is None:
        return ", ".join(noms)
    pop = p.set_index("Préfecture")["Population 2022"]
    return ", ".join(noms) + f" ({n(pop[list(noms)].sum())} habitants)"


def contradictions(p, positions, vois, zone_rapports):
    v = p.set_index("Préfecture")
    pos = positions
    T = "prefectures_06.csv"

    def et(*conds):
        return sorted(pos.index[np.logical_and.reduce(conds)])

    haut = lambda var: (pos[var] == "haut").to_numpy()
    bas = lambda var: (pos[var] == "bas").to_numpy()
    AE, KM, MAUV, NE = "Auto-écoles comptées pour 100 000 habitants", "Km pour 10 000 habitants", "Part en mauvais état (%)", "Part non évaluée (%)"

    for var, ind in ((AE, "O4-05"), (KM, "O4-03")):
        x = et(haut("Population 2022"), bas(var))
        signal("O5", f"Contradiction 1 ({'formation' if var == AE else 'réseau'}) : {len(x)} préfecture(s) à population haute et {var.lower()} bas : {liste(x, p)}",
               f"{T} : Population 2022, {var}", "2022", f"{len(x)} préfecture(s)", "Contradiction 1 (§7)", "C" if var == AE else "B",
               "Ces préfectures, peuplées et peu dotées : leur population est la population concernée (O5-03), à afficher à côté du taux.",
               f"{ind}, O5-03 ; H9")

    x = et(~bas(KM) & (pos[KM] != "non défini").to_numpy(), haut(MAUV))
    signal("O3", f"Contradiction 2a : {len(x)} préfecture(s) au réseau hors du quart bas et à part en mauvais état haute : {liste(x, p)}",
           f"{T} : {KM}, {MAUV}", "relevé de 2020 ; tracé 2021-2022", f"{len(x)} préfecture(s)", "Contradiction 2a (§7)", "C",
           "Ici le réseau existe mais il est dégradé : le 07 lit-il ces préfectures sur l’état (O3-02) plutôt que sur la quantité (O4-03) ?",
           "O3-02, O4-03 ; S5")

    dist = "Distance à l’auto-école comptée la plus proche (km)"
    x = et((v["Auto-écoles comptées"] >= 1).to_numpy(), haut(dist))
    signal("O4", f"Contradiction 2b : {len(x)} préfecture(s) avec au moins une auto-école comptée mais un point de départ loin de la plus proche : {liste(x, p)}",
           f"{T} : Auto-écoles comptées, {dist}", "collecte 2021-2022", f"{len(x)} préfecture(s)", "Contradiction 2b (§7)", "C",
           "La distance montre-t-elle un manque que le nombre ne montre pas ? Le 07 affiche les deux (O4-05, O4-08).",
           "O4-05, O4-08")

    moto = zone_rapports[(zone_rapports["Rapport"] == "Part des ménages") & (zone_rapports["Catégorie"] == "Possède une moto")].set_index("Territoire")["Valeur"]
    ae_z = zone_rapports[zone_rapports["Rapport"] == "Auto-écoles comptées pour 100 000 habitants"].set_index("Territoire")["Valeur"]
    x = sorted(z for z in ZONES if moto[z] > moto.median() and ae_z[z] < ae_z.median())
    signal("O4", f"Contradiction 2c : {len(x)} zone(s) où plus de ménages possèdent une moto que la médiane des 6 zones, avec moins d’auto-écoles comptées pour 100 000 habitants : {liste(x)}",
           "rapports_06.csv : Part des ménages (Possède une moto), Auto-écoles comptées pour 100 000 habitants", "EHCVM 2021-2022 ; 2022",
           f"{len(x)} zone(s) sur 6", "Contradiction 2c (§7)", "C",
           "L’usage déclaré (EHCVM, C) va-t-il contre l’offre de formation ? Lecture par zone seulement.", "O4-05 ; D12")

    for var, ind in ((KM, "O4-03"), (AE, "O4-05"), (MAUV, "O3-02"), (NE, "O3-06")):
        s = vois[(vois["Variable"] == var) & vois["Très différentes"]]
        paires = [f"{a} – {b}" for a, b in zip(s["Préfecture A"], s["Préfecture B"])]
        npaires = int((vois["Variable"] == var).sum())
        signal("O5", f"Contradiction 3 ({var.lower()}) : {len(paires)} paire(s) de voisines, l’une dans le quart haut, l’autre dans le quart bas, sur {npaires} paires : {liste(paires)}",
               f"voisines_06.csv : {var}", "2022", f"{len(paires)} paire(s) sur {npaires}", "Contradiction 3 (§7)", VARIABLES[var][2],
               "Ces écarts entre voisines tiennent-ils à la donnée (limite, rattachement) ou au territoire ? À vérifier avant de les afficher.",
               ind)

    x = et(haut(AE), bas("Auto-écoles comptées"))
    y = et(bas(AE), haut("Population 2022"))
    q1_km, _, q3_km, *_ = quartiles(v["Km évalués"])
    w = sorted(k for k in pos.index if pos.at[k, MAUV] == "haut" and position(v.at[k, "Km évalués"], q1_km, q3_km) == "bas")
    for texte, x_, var_txt, niv, ind in (
            ("taux d’auto-écoles comptées haut sur un nombre d’auto-écoles comptées bas", x, f"{AE}, Auto-écoles comptées", "C", "O4-04, O4-05"),
            ("taux d’auto-écoles comptées bas sur une population haute", y, f"{AE}, Population 2022", "C", "O4-05, O5-03"),
            ("part en mauvais état haute sur peu de km évalués", w, f"{MAUV}, Km évalués", "C", "O3-02")):
        signal("O5", f"Contradiction 4 : {len(x_)} préfecture(s) à {texte} : {liste(x_, p)}", f"{T} : {var_txt}", "2022",
               f"{len(x_)} préfecture(s)", "Contradiction 4 (§7)", niv,
               "Taux porté par un petit volume, ou volume derrière un taux faible : le 07 affiche le volume à côté du taux (intensité n’est pas volume).",
               ind)

    x = sorted(v.index[v["Auto-écoles comptées"] == 1])
    signal("O4", f"Contradiction 5 (formation) : {len(x)} préfecture(s) avec une seule auto-école comptée : {liste(x, p)}",
           f"{T} : Auto-écoles comptées", "collecte 2021-2022", f"{len(x)} préfecture(s)", "Contradiction 5 (§7)", "C",
           "Si cette auto-école ferme, la préfecture rejoint les préfectures sans auto-école comptée (O4-07) : population à afficher (O5-03).",
           "O4-04, O4-07, O5-03")
    x = sorted(v.index[v["Tronçons du relevé"] == 1])
    sans = sorted(v.index[v["Km de routes classées"] == 0])
    signal("O3", f"Contradiction 5 (réseau) : {len(x)} préfecture(s) traversée(s) par un seul tronçon du relevé : {liste(x, p)} ; sans route classée : {liste(sans, p)}",
           f"{T} : Tronçons du relevé, Km de routes classées", "relevé de 2020 ; tracé 2021-2022", f"{len(x)} préfecture(s) ; {len(sans)} sans route classée",
           "Contradiction 5 (§7)", "C",
           "Tout le réseau national évalué tient en un tronçon : son état dit l’état de la préfecture. Le 07 l’affiche avec cette réserve.",
           "O3-02, O3-05, O4-01")


def croisements(p, positions):
    """§3, O5 : préfectures en bas du réseau et de la formation à la fois, selon les quartiles du §4 (aucun seuil du 02)."""
    pos = positions
    AE = "Auto-écoles comptées pour 100 000 habitants"
    for var, texte, ind in (("Part en mauvais état (%)", "réseau dégradé (part en mauvais état dans le quart haut)", "O3-02, O4-05, O5-03 ; H9"),
                            ("Km pour 10 000 habitants", "desserte basse (km pour 10 000 habitants dans le quart bas)", "O4-03, O4-05, O5-03")):
        cote = "haut" if var.startswith("Part") else "bas"
        x = sorted(pos.index[(pos[var] == cote) & (pos[AE] == "bas")])
        signal("O5", f"Croisement : {len(x)} préfecture(s) à {texte} et à formation basse (auto-écoles comptées pour 100 000 habitants dans le quart bas) : {liste(x, p)}",
               f"prefectures_06.csv : {var}, {AE}", "2022", f"{len(x)} préfecture(s)", "Croisement (§3, O5)", "C",
               "Le 08 retrouve-t-il ces préfectures avec les seuils du 02 (terciles) ? Les quartiles du 06 ne sont pas ces seuils.", ind)


def signaux_distributions(dist):
    chrono = pd.read_csv(REFERENCE / "chronologie_reformes.csv")
    chrono = chrono[chrono["Type"] != "État des lois"].assign(An=lambda c: c["Date"].astype(str).str[:4].astype(int))
    court = chrono["Mesure"].str.split(r" : | \(|;|,", regex=True).str[0].str.strip()
    evenements = court.groupby(chrono["An"]).agg(" ; ".join).to_dict()
    dist = dist.sort_values("Maille", ascending=False, kind="stable")  # séries nationales (O1, O2), puis préfectures
    for _, d in dist[dist["Nombre d’atypiques"] > 0].iterrows():
        if d["Maille"] == "Préfecture":
            dec = VARIABLES[d["Variable"]][3]
            signal("O5" if d["Indicateur"].startswith("O5") else d["Indicateur"][:2],
                   f"{d['Variable']} : {d['Nombre d’atypiques']} préfecture(s) hors des bornes de Tukey ({n(d['Borne basse de Tukey'], dec + 1)} ; {n(d['Borne haute de Tukey'], dec + 1)}) : {d['Valeurs atypiques']}",
                   f"prefectures_06.csv : {d['Variable']}", "2022", d["Valeurs atypiques"], "Valeur atypique (§4)", d["Niveau"],
                   "Le classement tient-il sans ces valeurs ? Le 08 le vérifie (sensibilité au point extrême, 05_Priorisation).",
                   d["Indicateur"])
        else:
            annees = [int(a.split(" ")[0]) for a in d["Valeurs atypiques"].split(" ; ")]
            coincide = [f"{a} : {evenements[a]}" for a in annees if a in evenements]
            signal(SERIES[d["Variable"].split(" (")[0]],
                   f"{d['Variable']} : variation atypique en {', '.join(map(str, annees))}. Chronologie la même année : {' | '.join(coincide) if coincide else 'aucune'}",
                   f"rapports_06.csv : {d['Variable']}", ", ".join(map(str, annees)), d["Valeurs atypiques"], "Variation atypique (§4)",
                   d["Niveau"], "Le 07 annote ces années ; une date de la chronologie est une coïncidence, pas une cause (H1).",
                   d["Indicateur"])
    for var, seuil in TERCILES.items():
        d = dist[(dist["Maille"] == "Préfecture") & (dist["Variable"] == var)].iloc[0]
        if d["Ex aequo au minimum"] > d["Effectif"] / 3:
            ex = int(d["Ex aequo au minimum"])
            signal(VARIABLES[var][0][:2], f"{var} : {ex} préfectures sur {d['Effectif']} sont ex aequo au minimum ({n(d['Minimum'], VARIABLES[var][3])}), plus d’un tiers",
                   f"prefectures_06.csv : {var}", "2022", f"{ex} ex aequo sur {d['Effectif']}", "Ex aequo et terciles (§3, O4)",
                   d["Niveau"], f"Le tercile inférieur de {seuil} ne peut pas séparer ces ex aequo : comment le 08 coupe-t-il ? À trancher avant de voir le classement (R-20).",
                   f"{VARIABLES[var][0]} ; {seuil}")


def signaux_comparaisons(comp, ordre_identique):
    e = comp[comp["Comparaison"].str.startswith("État")]
    diff = e[e["Identiques"] == False]  # noqa: E712 (NaN : annuaire non renseigné)
    pire = e.loc[e["Écart (points)"].abs().idxmax()]
    signal("O3", f"État national de 2020 : {len(diff)} part(s) sur {int(e['Identiques'].notna().sum())} diffèrent entre le relevé et l’annuaire 39.2 ; écart maximal {n(pire['Écart (points)'], 2, True)} points ({pire['Élément']})",
           "comparaisons_06.csv : État national de 2020", "2020", f"{n(e['Écart (points)'].abs().max(), 2)} points au plus", "Comparaison de sources (§5)", "C",
           "Les deux publications de 2020 diffèrent : le 07 dit laquelle porte O3-07 et laquelle porte O3-01 à O3-06." if len(diff)
           else "Les deux publications de 2020 concordent : O3-07 et O3-01 à O3-06 décrivent le même réseau.", "O3-01 à O3-07")
    m = comp[comp["Comparaison"].str.startswith("Ménages")]
    signal("O1", f"Ménages possédant une moto : l’ordre des 6 zones {'est le même' if ordre_identique else 'change'} entre la DHS 2017 et l’EHCVM 2021-2022 ; écarts de {n(m['Écart (points)'].min(), 1, True)} à {n(m['Écart (points)'].max(), 1, True)} points",
           "comparaisons_06.csv : Ménages possédant une moto", "2017 ; 2021-2022", f"écarts de {n(m['Écart (points)'].min(), 1, True)} à {n(m['Écart (points)'].max(), 1, True)} points",
           "Comparaison de sources (§5)", "C",
           "La possession de motos se lit en C, enquête par enquête ; deux enquêtes et deux dates ne font pas une tendance.", "D12 ; contexte de O1")


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    national()
    t, p = prefectures()
    zones(t)
    troncons()
    dist, positions = distributions(p)
    vois = voisines(p, positions)
    r = pd.DataFrame(rapports)
    comp, ordre_identique = comparaisons()
    signaux_distributions(dist)
    signaux_comparaisons(comp, ordre_identique)
    croisements(p, positions)
    contradictions(p, positions, vois, r[r["Maille"] == "Zone"])
    r.to_csv(SORTIE / "rapports_06.csv", index=False)
    s = pd.DataFrame(signaux)
    s.to_csv(SORTIE / "signaux_06.csv", index=False)
    print(f"rapports : {len(r)} ; préfectures : {len(p)} ; distributions : {len(dist)} ; paires de voisines : {vois['Préfecture A'].count() // 4} ; "
          f"comparaisons : {len(comp)} ; signaux : {len(s)}")
    print(s[["ID", "Résumé"]].to_string(index=False))


if __name__ == "__main__":
    main()
