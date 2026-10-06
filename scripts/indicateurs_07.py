"""Étape 07 : indicateurs (07_indicateurs.md).

Lit les tables du 05 (data/processed/), data/reference/, le 02 (01_Matrice.csv, 03_Seuils.csv), le 04
(faisabilite_indicateurs.csv) et le 06 (signaux_06.csv ; rapports_06.csv et prefectures_06.csv pour les contrôles).
N'écrit rien dans data/processed/.
Calcule chaque chiffre cité dans le 07 (R-19) :
- les 32 indicateurs du 02 calculables au 07, avec la formule du 02 et la maille du 04 (§3) ;
- les 3 compléments de l'énoncé, hors 02 (écart 22) ;
- les deux cibles de O5-04 pour la formation et la nature du zéro (écart 21) ;
- les contrôles du §7.

Aucun seuil de classement, aucun rang, aucun score : ils viennent au 08. SE-01 et SE-08 sont lus dans le 02.
Un rapport sans dénominateur est « non défini » (case vide), jamais 0 (R-10). Distances en UTM 31N (R-16).

Sorties, dans data/analysis/07_indicateurs/ : indicateurs_07.csv, catalogue_07.csv, controles_07.csv.

Usage : .venv/bin/python scripts/indicateurs_07.py
"""
import math
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
TRAITE = RACINE / "data" / "processed"
REFERENCE = RACINE / "data" / "reference"
MATRICE = RACINE / "02_decision_matrix"
FAISABILITE = RACINE / "data" / "analysis" / "04_understanding" / "faisabilite_indicateurs.csv"
EXPLORATION = RACINE / "data" / "analysis" / "06_exploration"
SORTIE = RACINE / "data" / "analysis" / "07_indicateurs"

UTM31N = 32631
ZONES = ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]
GROUPES = ["Moto", "Voiture", "Poids lourd", "Bus et car", "Autres"]
ETATS = ["Bon", "Moyen", "Mauvais", "Travaux", "Non évalué"]
TYPES_ROUTE = ["Route nationale revêtue", "Route nationale non revêtue", "Piste rurale", "Voirie urbaine"]
PASSES_AU_08 = ["O5-01", "O5-02"]  # écart 20
HORS_02 = "complément de l’énoncé, hors 02 (écart 22)"
CONFORME, ECHEC = "conforme", "échec"

# Écart 22 : les 3 taux de l'énoncé absents du 02 (01 §3.2). Indicateur, définition, formule, unité, sens, niveau
COMPLEMENTS = {
    "O2-E1": ("Blessés pour 100 000 habitants", "Blessés rapportés à la population",
              "blessés(an) / population(an) × 100 000 (R-06)", "Pour 100 000 habitants", "Plus haut = pire",
              "B en 2010 et 2022, C les autres années"),
    "O2-E2": ("Accidents constatés pour 10 000 véhicules", "Accidents constatés rapportés au parc",
              "accidents(an) / parc(an) × 10 000 ; parc estimé en fourchette (R-11)", "Pour 10 000 véhicules",
              "Plus haut = pire", "C"),
    "O2-E3": ("Blessés pour 10 000 véhicules", "Blessés rapportés au parc",
              "blessés(an) / parc(an) × 10 000 ; parc estimé en fourchette (R-11)", "Pour 10 000 véhicules",
              "Plus haut = pire", "C"),
}

# Calcul au 07 et justification issue du 06 (07 §3, §5)
CALCUL = {
    "O1-01": ("Lues dans D1, par groupe", "Années atypiques à annoter [SIG-01 à SIG-04]"),
    "O1-02": ("Groupe / total × 100", "Part des motos de 22,2 % à 74,4 % (06 §3, O1)"),
    "O1-03": ("Par groupe et pour l’ensemble ; TCAM sur 1990–2024 ; multiplicateur sur 20 ans, de 2010 à 2024",
              "Ruptures de 1995 et 2004, à annoter [SIG-01]"),
    "O1-04": ("Population de la même année (R-06)", "Raccord de population de 2011 [SIG-11]"),
    "O1-05": ("Lu dans D1_parc_estime.csv, calculé une seule fois au 05 (05 §6)",
              "Fourchette à 51,4 % de la valeur centrale en 2024 : jamais sans ses bornes (06 §3, O1)"),
    "O1-06": ("Lus dans D2 ; 2013 non renseignée", "Années atypiques à annoter [SIG-05 à SIG-10]"),
    "O1-07": ("Dénominateur : D7_population_age_conduire.csv", "Hausse de A en 2022 et 2024 [SIG-05]"),
    "O1-09": ("Par catégorie de permis (correspondance du 05), par année et en cumul",
              "Écarts entre catégories en cumul : de 0,37 (D) à 40,2 (A) (06 §3, O1)"),
    "O2-01": ("Lus dans D3", "Années atypiques à annoter [SIG-12 à SIG-14]"),
    "O2-02": ("Population de la même année (R-06)",
              "Raccord de population de 2011 [SIG-11] ; repère de l’OMS (SE-03) appliqué au 08"),
    "O2-03": ("Population de la même année (R-06)", "[SIG-11, SIG-12]"),
    "O2-04": ("Dénominateur : le parc estimé, avec ses bornes (R-11)", "Fourchette large (06 §3, O2)"),
    "O2-05": ("Tués / accidents × 100", "De 7,9 à 16,6 (06 §3, O2)"),
    "O2-06": ("Blessés / accidents × 100", "De 103,2 à 201,3 (06 §3, O2)"),
    "O2-09": ("Lues dans D3_victimes_usager_2021.csv", "60 % de deux et trois-roues motorisés (06 §3, O2)"),
    "O2-E1": ("Blessés / population × 100 000 ; règles de O2-02",
              "Taux non exploré au 06 (hors 02) ; blessés atypiques en 2016 [SIG-14] ; raccord de population [SIG-11]"),
    "O2-E2": ("Accidents / parc estimé × 10 000 ; règles de O2-04",
              "Taux non exploré au 06 (hors 02) ; accidents atypiques [SIG-12] ; fourchette du parc (06 §3, O2)"),
    "O2-E3": ("Blessés / parc estimé × 10 000 ; règles de O2-04",
              "Taux non exploré au 06 (hors 02) ; [SIG-14] ; fourchette du parc (06 §3, O2)"),
    "O3-01": ("Km par état, répartis sur le tracé (R-15)", "[SIG-20, SIG-27]"),
    "O3-02": ("Mauvais / km évalués × 100 ; non défini pour Mô", "Danyi, Blitta, Kloto hors des bornes [SIG-20]"),
    "O3-03": ("Travaux / km évalués × 100", "Médiane 21,85 % ; 10 préfectures à 0 (06 §3, O3)"),
    "O3-04": ("Somme par zone, type de route nationale et état, non évalué compris",
              "De 7,7 % à 40,3 % en mauvais état selon la zone (06 §3, O3)"),
    "O3-05": ("Tronçons qui ont des km en mauvais état, triés par ces km (repli du 02) ; nombre et somme des km, "
              "par zone traversée", "Carte des tronçons (06 §3, O3)"),
    "O3-06": ("Km sans état / km de routes nationales du tracé × 100", "7 préfectures hors des bornes [SIG-21]"),
    "O3-07": ("Part de chaque état, l’année moins l’année précédente, en points, par catégorie de route : "
              "2021 − 2020, 2022 − 2021", "Deux sources de 2020 en désaccord [SIG-27]"),
    "O4-01": ("Lus dans D5, par type", "[SIG-16 à SIG-18] ; Mô sans route classée [SIG-44]"),
    "O4-02": ("Km / surface × 1 000", "Golfe, Agoè-Nyivé, Lacs hors des bornes [SIG-19]"),
    "O4-03": ("Km / population 2022 × 10 000", "[SIG-30, SIG-32]"),
    "O4-04": ("Comptées (R-12) ; recensées en désagrégation", "[SIG-22, SIG-23, SIG-43]"),
    "O4-05": ("Comptées / population 2022 × 100 000", "23 préfectures ex aequo à 0 [SIG-24, SIG-26]"),
    "O4-06": ("Population / comptées ; non défini sans auto-école comptée", "Non défini pour 23 préfectures [SIG-26]"),
    "O4-07": ("Les préfectures sans auto-école comptée (R-12, 04 §8), avec leur population ; la note distingue "
              "celles sans aucune auto-école recensée, définition littérale du 02", "[SIG-26]"),
    "O4-08": ("Repli du 02 : distance du point de départ à l’auto-école comptée la plus proche, en UTM 31N ; avec SE-08, "
              "population des préfectures dont le point de départ est au-delà", "Oti-Sud hors des bornes [SIG-25] ; "
              "la distance distingue les 23 préfectures à zéro (06 §3, O4)"),
    "O5-03": ("Population 2022 de chaque préfecture ; pour la distance, celle de O4-08",
              "Le volume à côté du taux [SIG-29 à SIG-32]"),
    "O5-04": ("Km à remettre en état : cible PA-04 (médiane de O3-02). Auto-écoles manquantes : formule du 02 et "
              "variante de l’écart 21, côte à côte, avec la nature du zéro",
              "Médiane de O4-05 = 0 [SIG-26] ; médiane de O3-02 = 14,35 % (06 §3, O3)"),
}
RESERVES = {
    "O3-07": "Jamais mélangé avec O3-01 à O3-06 : les deux sources de 2020 diffèrent [SIG-27]",
    "O5-04": "Écart de tués non calculable : O2-02 est national (écart 1)",
}

valeurs, controles = [], []


def exiger(condition, message):
    if not condition:
        raise ValueError(message)


def n(x, decimales=0):
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def lire(nom):
    return pd.read_csv(TRAITE / f"{nom}.csv")


def quotient(num, den, facteur, decimales):
    """Rapport arrondi ; non défini (NaN) si un terme manque ou si le dénominateur est nul."""
    if pd.isna(num) or pd.isna(den) or den == 0:
        return np.nan
    return round(num / den * facteur, decimales)


def niveau(*niveaux):
    """Un rapport est calculé (B), ou estimé (C) si l'un de ses termes l'est (R-17)."""
    return "C" if "C" in niveaux else "B"


def valeur(ind, maille, territoire, annee, categorie, mesure, v, unite, niv, source, num=np.nan, den=np.nan,
           basse=np.nan, haute=np.nan, note=""):
    valeurs.append({"ID": ind, "Maille": maille, "Territoire": territoire, "Année": annee, "Catégorie": categorie,
                    "Mesure": mesure, "Numérateur": num, "Dénominateur": den, "Valeur": v, "Borne basse": basse,
                    "Borne haute": haute, "Unité": unite, "Niveau": niv, "Source": source, "Note": note})


def notes(*morceaux):
    return " ; ".join(m for m in morceaux if m)


def seuil(ident):
    """Valeur numérique d'un seuil du 02 (03_Seuils.csv), lue et non recopiée."""
    s = pd.read_csv(MATRICE / "03_Seuils.csv").set_index("ID").at[ident, "Valeur ou règle"]
    return float(re.match(r"\d+(?:[.,]\d+)?", s).group().replace(",", "."))


def atypiques():
    """Années atypiques des séries nationales (06 §4) : {(série, catégorie) : {année : signal}}."""
    s = pd.read_csv(EXPLORATION / "signaux_06.csv")
    s = s[s["Règle"] == "Variation atypique (§4)"]
    a = {}
    for _, r in s.iterrows():
        serie, cat = re.match(r"rapports_06\.csv : Variation annuelle : (.+) \((.+)\)$", r["Table et colonne"]).groups()
        a[(serie, cat)] = {int(x): r["ID"] for x in r["Territoire ou période"].split(", ")}
    return a


def annotation(atyp, serie, cat, an, texte="variation atypique depuis l’année précédente"):
    sig = atyp.get((serie, cat), {}).get(an)
    return f"{texte} [{sig}]" if sig else ""


# --- O1 et O2 : séries nationales (§3) ---------------------------------------------------------------

def national(atyp):
    pop = lire("D7_population_nationale").set_index("Année")
    np_pop = pop["Niveau"].to_dict()
    SP = "D7_population_nationale.csv"

    def note_pop(an):
        return annotation(atyp, "population", "Togo", an, "population : variation atypique depuis l’année précédente")

    d1 = lire("D1_immatriculations")
    rupture = set(d1.loc[d1["Rupture"], "Année"])
    imm = d1.pivot_table(index="Année", columns="Groupe", values="Immatriculations", aggfunc="sum")[GROUPES]
    imm["Ensemble"] = imm[GROUPES].sum(axis=1)
    S1 = "D1_immatriculations.csv"
    for an in imm.index:
        rup = "rupture de série (04)" if an in rupture else ""
        for g in GROUPES + ["Ensemble"]:
            valeur("O1-01", "National", "Togo", an, g, "", imm.at[an, g], "véhicules", "A", S1,
                   note=notes(annotation(atyp, "immatriculations", g, an), rup))
            if g != "Ensemble":
                valeur("O1-02", "National", "Togo", an, g, "", quotient(imm.at[an, g], imm.at[an, "Ensemble"], 100, 1),
                       "%", "B", S1, imm.at[an, g], imm.at[an, "Ensemble"])
            valeur("O1-04", "National", "Togo", an, g, "", quotient(imm.at[an, g], pop.at[an, "Population"], 1000, 2),
                   "pour 1 000 habitants", niveau(np_pop[an]), f"{S1} ; {SP}", imm.at[an, g], pop.at[an, "Population"],
                   note=note_pop(an))
            if an - 1 in imm.index:
                num, den = imm.at[an, g], imm.at[an - 1, g]
                v = round((num / den - 1) * 100, 1) if den > 0 else np.nan
                valeur("O1-03", "National", "Togo", an, g, "croissance annuelle", v, "%", "B", S1, num, den,
                       note=notes(annotation(atyp, "immatriculations", g, an), rup))
            if an - 20 in imm.index:
                valeur("O1-03", "National", "Togo", an, g, "multiplicateur sur 20 ans",
                       quotient(imm.at[an, g], imm.at[an - 20, g], 1, 2), "multiplicateur", "B", S1, imm.at[an, g],
                       imm.at[an - 20, g], note=notes(f"I({an}) / I({an - 20})", *(f"rupture de série en {a} (04)"
                                                                               for a in (an - 20, an) if a in rupture)))
    debut, fin = imm.index.min(), imm.index.max()
    for g in GROUPES + ["Ensemble"]:
        tcam = round(((imm.at[fin, g] / imm.at[debut, g]) ** (1 / (fin - debut)) - 1) * 100, 1)
        valeur("O1-03", "National", "Togo", f"{debut}–{fin}", g, "taux de croissance annuel moyen", tcam, "% par an", "B",
               S1, imm.at[fin, g], imm.at[debut, g], note=f"(I({fin}) / I({debut}))^(1/{fin - debut}) − 1")

    parc = lire("D1_parc_estime").dropna(subset=["Borne basse", "Valeur centrale", "Borne haute"])
    parc = parc[parc["Année"] >= parc[parc["Groupe"] == "Ensemble"]["Année"].min()]  # période commune (04)
    for _, p in parc.iterrows():
        valeur("O1-05", "National", "Togo", p["Année"], p["Groupe"], "", p["Valeur centrale"], "véhicules", "C",
               "D1_parc_estime.csv", basse=p["Borne basse"], haute=p["Borne haute"],
               note=notes(f"durée de vie PA-01 (ans) : {p['Durée de vie PA-01 (ans)']}" if pd.notna(p["Durée de vie PA-01 (ans)"]) else "",
                          p["Note"] if pd.notna(p["Note"]) else ""))

    d2 = lire("D2_permis")
    permis = d2.pivot(index="Année", columns="Catégorie", values="Permis délivrés")  # 2013 reste vide (R-10)
    age = lire("D7_population_age_conduire").pivot(index="Année", columns="Catégorie", values="Population en âge de conduire")
    S2 = "D2_permis.csv"
    for an in permis.index:
        nr = "non renseignée (R-10)" if pd.isna(permis.loc[an]).all() else ""
        for cat in permis.columns:
            valeur("O1-06", "National", "Togo", an, cat, "", permis.at[an, cat], "permis", "A", S2,
                   note=notes(nr, annotation(atyp, "permis délivrés", cat, an)))
            valeur("O1-07", "National", "Togo", an, cat, "", quotient(permis.at[an, cat], age.at[an, cat], 1000, 2),
                   "pour 1 000 habitants en âge de conduire", "C", f"{S2} ; D7_population_age_conduire.csv",
                   permis.at[an, cat], age.at[an, cat], note=nr)

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
            valeur("O1-09", "National", "Togo", an, cat, "", quotient(immcat[an], permis.at[an, cat], 1, 2), "ratio", "B",
                   f"{S1} ; {S2}", immcat[an], permis.at[an, cat], note=" + ".join(types))
        valeur("O1-09", "National", "Togo", f"{min(communs)}–{max(communs)}", cat, "",
               quotient(immcat[communs].sum(), permis.loc[communs, cat].sum(), 1, 2), "ratio", "B", f"{S1} ; {S2}",
               immcat[communs].sum(), permis.loc[communs, cat].sum(),
               note=f"cumul des années communes, sans 2013 ; {' + '.join(types)}")

    d3 = lire("D3_accidents")
    note_d3 = d3.dropna(subset=["Note"]).groupby("Mesure")["Note"].first().to_dict()
    d3 = d3.pivot(index="Année", columns="Mesure", values="Valeur")
    ens = parc[parc["Groupe"] == "Ensemble"].set_index("Année")
    S3, SP1 = "D3_accidents.csv", "D1_parc_estime.csv"
    bornes = "bornes : parc estimé haut, puis bas (PA-01)"
    for an in d3.index:
        acc, tues, bles, hab = d3.at[an, "Accidents constatés"], d3.at[an, "Tués"], d3.at[an, "Blessés"], pop.at[an, "Population"]
        serie = "accidents, tués, blessés"
        for mesure in ("Accidents constatés", "Blessés", "Tués"):
            valeur("O2-01", "National", "Togo", an, mesure, "", d3.at[an, mesure], "victimes" if mesure != "Accidents constatés"
                   else "accidents", "A", S3, note=notes(note_d3.get(mesure, ""), annotation(atyp, serie, mesure, an)))
        niv = niveau(np_pop[an])
        valeur("O2-02", "National", "Togo", an, "", "", quotient(tues, hab, 1e5, 2), "pour 100 000 habitants", niv,
               f"{S3} ; {SP}", tues, hab, note=notes(annotation(atyp, serie, "Tués", an), note_pop(an)))
        valeur("O2-03", "National", "Togo", an, "", "", quotient(acc, hab, 1e5, 1), "pour 100 000 habitants", niv,
               f"{S3} ; {SP}", acc, hab, note=notes("accidents constatés (écart 15)", annotation(atyp, serie, "Accidents constatés", an), note_pop(an)))
        valeur("O2-05", "National", "Togo", an, "", "", quotient(tues, acc, 100, 1), "pour 100 accidents constatés", "B", S3, tues, acc)
        valeur("O2-06", "National", "Togo", an, "", "", quotient(bles, acc, 100, 1), "pour 100 accidents constatés", "B", S3, bles, acc)
        valeur("O2-E1", "National", "Togo", an, "", "", quotient(bles, hab, 1e5, 1), "pour 100 000 habitants", niv,
               f"{S3} ; {SP}", bles, hab, note=notes(HORS_02, annotation(atyp, serie, "Blessés", an), note_pop(an)))
        if an in ens.index:
            v = ens.loc[an]
            for ind, num, mes in (("O2-04", tues, "Tués"), ("O2-E2", acc, "Accidents constatés"), ("O2-E3", bles, "Blessés")):
                valeur(ind, "National", "Togo", an, "", "", quotient(num, v["Valeur centrale"], 1e4, 2),
                       "pour 10 000 véhicules du parc estimé", "C", f"{S3} ; {SP1}", num, v["Valeur centrale"],
                       quotient(num, v["Borne haute"], 1e4, 2), quotient(num, v["Borne basse"], 1e4, 2),
                       notes(HORS_02 if ind != "O2-04" else "", bornes, annotation(atyp, serie, mes, an)))

    vic = lire("D3_victimes_usager_2021")
    for _, r in vic.iterrows():
        valeur("O2-09", "National", "Togo", r["Année"], r["Type d'usager"], "", r["Part des tués déclarés (%)"],
               "% des tués déclarés", "C", "D3_victimes_usager_2021.csv", note="OMS ; ni sexe ni âge (écart 3)")
    return d3


# --- O3, O4, O5 : préfectures, zones et tronçons (§3) ------------------------------------------------

def distances():
    """Distance à vol d'oiseau (UTM 31N, R-16) de chaque point de départ (D13) à l'auto-école comptée la plus proche."""
    pts = lire("D13_points_depart_o4_08").set_index("Préfecture")
    ae = lire("D6_auto_ecoles")
    ae = ae[ae["Comptée (R-12)"]].reset_index(drop=True)
    d = np.hypot(pts["x_utm"].to_numpy()[:, None] - ae["x_utm"].to_numpy()[None, :],
                 pts["y_utm"].to_numpy()[:, None] - ae["y_utm"].to_numpy()[None, :])
    return pd.DataFrame({"distance": (d.min(axis=1) / 1000).round(1),
                         "plus proche": ae.loc[d.argmin(axis=1), "Préfecture"].to_numpy(),
                         "origine": pts["Origine"].to_numpy()}, index=pts.index)


def prefectures():
    """Termes par préfecture, lus dans les tables détaillées du 05 (et non dans la table maîtresse lue par le 06)."""
    ref = pd.read_csv(REFERENCE / "referentiel_prefectures.csv").drop_duplicates("Préfecture").set_index("Préfecture")[["Région", "Zone"]]
    d7 = lire("D7_population_prefecture_2022")
    pop = d7[(d7["Milieu"] == "Total") & (d7["Sexe"] == "Ensemble") & (d7["Groupe d’âges"] == "Total")].groupby("Préfecture")["Population"].sum()
    # sommes ramenées à 3 décimales, celles des km répartis du 05 : un résidu flottant ne change pas un arrondi
    etat = lire("D4_D5_etat_trace").pivot_table(index="Préfecture", columns="État", values="km", aggfunc="sum").round(3)
    trace = lire("D5_trace_prefecture").pivot_table(index="Préfecture", columns="Type de route", values="km", aggfunc="sum").round(3)
    ae = lire("D6_auto_ecoles")
    surface = lire("table_maitresse_prefecture").set_index("Préfecture")["Surface (km²)"]
    p = ref.copy()
    p["population"] = pop.astype(int)
    for e in ETATS:
        p[e] = etat[e] if e in etat else 0.0
    for t in TYPES_ROUTE:
        p[t] = trace[t]
    p = p.fillna({e: 0.0 for e in ETATS})  # aucun tronçon d'état : 0 km dans chaque état
    p["routes"] = p[TYPES_ROUTE].sum(axis=1).round(3)
    p["rn"] = (p["Route nationale revêtue"] + p["Route nationale non revêtue"]).round(3)
    p["évalués"] = p[ETATS[:4]].sum(axis=1).round(3)
    p["surface"] = surface
    p["recensées"] = ae.groupby("Préfecture").size()
    p["comptées"] = ae[ae["Comptée (R-12)"]].groupby("Préfecture").size()
    p[["recensées", "comptées"]] = p[["recensées", "comptées"]].fillna(0).astype(int)
    p = p.join(distances())
    exiger(len(p) == 39 and p["population"].notna().all() and p["surface"].notna().all(), "39 préfectures complètes attendues")
    return p.sort_index()


def reseau(p):
    S = "D4_D5_etat_trace.csv"
    for pref, r in p.iterrows():
        for e in ETATS:
            valeur("O3-01", "Préfecture", pref, 2020, e, "", round(r[e], 1), "km", "C", S,
                   note="aucune route nationale" if r["rn"] == 0 else "")
        nd = "non défini : aucun km évalué (R-10)" if r["évalués"] == 0 else ""
        valeur("O3-02", "Préfecture", pref, 2020, "", "", quotient(r["Mauvais"], r["évalués"], 100, 1), "% des km évalués",
               "C", S, round(r["Mauvais"], 3), round(r["évalués"], 3), note=nd)
        valeur("O3-03", "Préfecture", pref, 2020, "", "", quotient(r["Travaux"], r["évalués"], 100, 1), "% des km évalués",
               "C", S, round(r["Travaux"], 3), round(r["évalués"], 3), note=nd)
        valeur("O3-06", "Préfecture", pref, "2020 (état) ; 2021-2022 (tracé)", "", "",
               quotient(r["Non évalué"], r["rn"], 100, 1), "% des km de routes nationales", "B",
               f"{S} ; D5_trace_prefecture.csv", round(r["Non évalué"], 3), round(r["rn"], 3),
               note="non défini : aucune route nationale (R-10)" if r["rn"] == 0 else "")

    z = lire("D4_D5_etat_trace").groupby(["Zone", "Type de route", "État"])["km"].sum()
    for zone in ZONES:
        for t in ("revêtue", "non revêtue"):
            for e in ETATS:
                valeur("O3-04", "Zone", zone, 2020, f"route nationale {t} ; {e}", "", round(z.get((zone, t, e), 0.0), 1),
                       "km", "C", S)

    tr = lire("D4_etat_troncons")
    crit = tr[tr["km_mauvais"] > 0].sort_values(["km_mauvais", "Tronçon"], ascending=[False, True]).reset_index(drop=True)
    for i, r in crit.iterrows():
        valeur("O3-05", "Tronçon", r["Tronçon"], 2020, f"route nationale {r['Type']}", "km en mauvais état", r["km_mauvais"],
               "km", "C", "D4_etat_troncons.csv",
               note=f"rang {i + 1} sur {len(crit)} ; {n(r['km_total'], 2)} km relevés ; zones traversées : {r['Zones traversées']}")
    zones_tr = crit.assign(Zone=crit["Zones traversées"].str.split(" ; ")).explode("Zone")
    for zone in ZONES:
        s = zones_tr[zones_tr["Zone"] == zone]
        for mesure, v, unite in (("nombre de tronçons", len(s), "tronçons"), ("km en mauvais état", round(s["km_mauvais"].sum(), 2), "km")):
            valeur("O3-05", "Zone", zone, 2020, "", mesure, v, unite, "C", "D4_etat_troncons.csv",
                   note="un tronçon qui traverse plusieurs zones compte dans chacune")
    for mesure, v, unite in (("nombre de tronçons", len(crit), "tronçons"), ("km en mauvais état", round(crit["km_mauvais"].sum(), 2), "km")):
        valeur("O3-05", "National", "Togo", 2020, "", mesure, v, unite, "C", "D4_etat_troncons.csv")

    an = lire("D4_etat_national_pct").set_index(["Catégorie de route", "État", "Année"])["Part (%)"]
    for (cat, etat), _ in an.groupby(level=[0, 1], sort=False):
        for a in (2021, 2022):
            v1, v0 = an.get((cat, etat, a)), an.get((cat, etat, a - 1))
            valeur("O3-07", "National", "Togo", f"{a - 1}–{a}", f"{cat} ; {etat}", "", round(v1 - v0, 2) if pd.notna(v1) and pd.notna(v0) else np.nan,
                   "points de %", "C", "D4_etat_national_pct.csv", v1, v0,
                   note="non défini : « - » dans l’annuaire (R-10)" if pd.isna(v1) or pd.isna(v0) else "")


def couverture(p, se08):
    S5, S6, S7 = "D5_trace_prefecture.csv", "D6_auto_ecoles.csv", "D7_population_prefecture_2022.csv"
    zero = p[p["comptées"] == 0]
    for pref, r in p.iterrows():
        for t in TYPES_ROUTE + ["Ensemble"]:
            valeur("O4-01", "Préfecture", pref, "2021-2022", t, "", round(r["routes"] if t == "Ensemble" else r[t], 1), "km", "B", S5,
                   note="aucune route classée (vrai vide, 05)" if r["routes"] == 0 else "")
        valeur("O4-02", "Préfecture", pref, "2021-2022", "", "", quotient(r["routes"], r["surface"], 1e3, 1), "km pour 1 000 km²",
               "B", f"{S5} ; table_maitresse_prefecture.csv", round(r["routes"], 3), r["surface"])
        valeur("O4-03", "Préfecture", pref, 2022, "", "", quotient(r["routes"], r["population"], 1e4, 2), "km pour 10 000 habitants",
               "B", f"{S5} ; {S7}", round(r["routes"], 3), r["population"])
        valeur("O4-04", "Préfecture", pref, "2021-2022", "comptées (R-12)", "", r["comptées"], "auto-écoles", "A", S6)
        valeur("O4-04", "Préfecture", pref, "2021-2022", "recensées", "", r["recensées"], "auto-écoles", "A", S6,
               note="agréées, antennes agréées, non agréées et non renseignées")
        valeur("O4-05", "Préfecture", pref, 2022, "", "", quotient(r["comptées"], r["population"], 1e5, 2), "pour 100 000 habitants",
               "C", f"{S6} ; {S7}", r["comptées"], r["population"], note="activité non vérifiée (écart 13)")
        h = quotient(r["population"], r["comptées"], 1, 0)
        valeur("O4-06", "Préfecture", pref, 2022, "", "", h if pd.isna(h) else int(h), "habitants", "C", f"{S6} ; {S7}",
               r["population"], r["comptées"], note="non défini : aucune auto-école comptée (R-10)" if r["comptées"] == 0 else "")
        loin = r["distance"] > se08
        valeur("O4-08", "Préfecture", pref, "2021-2022", "", "distance (km)", r["distance"], "km", "C",
               f"D13_points_depart_o4_08.csv ; {S6}",
               note=notes(f"point de départ : {r['origine']}", f"auto-école la plus proche : {r['plus proche']}",
                          f"au-delà de SE-08 ({n(se08)} km)" if loin else ""))
        valeur("O4-08", "Préfecture", pref, 2022, "", f"population si le point de départ est au-delà de SE-08 ({n(se08)} km)",
               r["population"] if loin else 0, "habitants", "C", f"{S7} ; D13_points_depart_o4_08.csv",
               note="population de la préfecture, pas population à plus de 10 km : pas de grille (04 §8)")
        valeur("O5-03", "Préfecture", pref, 2022, "", "", r["population"], "habitants", "A", S7)
    for pref, r in zero.iterrows():
        valeur("O4-07", "Préfecture", pref, 2022, "sans auto-école comptée (R-12)", "population", r["population"], "habitants", "B",
               f"{S6} ; {S7}", note=nature_zero(r))
    sans_aucune = zero[zero["recensées"] == 0]
    for cat, s in (("sans auto-école comptée (R-12)", zero), ("sans aucune auto-école recensée (définition littérale du 02)", sans_aucune)):
        valeur("O4-07", "National", "Togo", 2022, cat, "nombre de préfectures", len(s), "préfectures", "B", S6)
        valeur("O4-07", "National", "Togo", 2022, cat, "population", int(s["population"].sum()), "habitants", "B", f"{S6} ; {S7}")
    loin = p[p["distance"] > se08]
    valeur("O4-08", "National", "Togo", 2022, "", f"nombre de préfectures dont le point de départ est au-delà de SE-08 ({n(se08)} km)",
           len(loin), "préfectures", "C", "D13_points_depart_o4_08.csv", note=", ".join(loin.index))
    valeur("O4-08", "National", "Togo", 2022, "", f"population si le point de départ est au-delà de SE-08 ({n(se08)} km)",
           int(loin["population"].sum()), "habitants", "C", f"{S7} ; D13_points_depart_o4_08.csv",
           note="population des préfectures, pas population à plus de 10 km : pas de grille (04 §8)")


def nature_zero(r):
    """Écart 21 : pourquoi une préfecture n'a aucune auto-école comptée."""
    if r["recensées"] == 0:
        return "nature du zéro : aucune auto-école recensée ; vérifier sur place qu’il n’en existe pas"
    return f"nature du zéro : {r['recensées']} auto-école(s) recensée(s), aucune agréée ; vérifier leur activité et leur agrément"


def ecart_cible(p):
    """O5-04 : km à remettre en état (PA-04) ; auto-écoles manquantes avec la cible du 02 et celle de l'écart 21."""
    v = pd.DataFrame(valeurs)
    o302 = v[v["ID"] == "O3-02"].set_index("Territoire")["Valeur"].astype(float)
    o405 = v[v["ID"] == "O4-05"].set_index("Territoire")["Valeur"].astype(float)
    med_km = round(float(o302.median()), 4)
    med_02 = round(float(o405.median()), 4)
    med_21 = round(float(o405[p["comptées"] >= 1].median()), 4)
    avec = int((p["comptées"] >= 1).sum())
    cibles = ((f"cible du 02 : médiane de O4-05 sur les 39 préfectures ({n(med_02, 2)})", med_02),
              (f"cible de l’écart 21 : médiane de O4-05 sur les {avec} préfectures avec au moins une auto-école comptée ({n(med_21, 3)})", med_21))
    S = "D4_D5_etat_trace.csv ; D6_auto_ecoles.csv ; D7_population_prefecture_2022.csv"
    for pref, r in p.iterrows():
        km = round(r["Mauvais"] - med_km / 100 * r["évalués"], 1) if r["évalués"] > 0 else np.nan
        valeur("O5-04", "Préfecture", pref, 2022, f"cible PA-04 : médiane de O3-02 ({n(med_km, 2)} %)", "km à remettre en état",
               km, "km", "C", S, note=notes("non défini : aucun km évalué (R-10)" if pd.isna(km) else "",
                                         "négatif : déjà sous la cible" if km < 0 else ""))
        for cat, med in cibles:
            manque = math.ceil(round(r["population"] * med / 1e5, 9)) - r["comptées"]
            valeur("O5-04", "Préfecture", pref, 2022, cat, "auto-écoles manquantes", manque, "auto-écoles", "C", S,
                   note=notes(nature_zero(r) if r["comptées"] == 0 else "", "négatif ou nul : déjà à la cible" if manque <= 0 else ""))
    o5 = pd.DataFrame(valeurs)
    o5 = o5[(o5["ID"] == "O5-04") & (o5["Maille"] == "Préfecture")]
    for (cat, mesure), s in o5.groupby(["Catégorie", "Mesure"], sort=False):
        pos = s[s["Valeur"] > 0]
        unite = "km" if mesure.startswith("km") else "auto-écoles"
        valeur("O5-04", "National", "Togo", 2022, cat, "préfectures à écart positif", len(pos), "préfectures", "C", S,
               note=", ".join(pos["Territoire"]))
        valeur("O5-04", "National", "Togo", 2022, cat, f"somme des écarts positifs ({mesure})", round(pos["Valeur"].sum(), 1),
               unite, "C", S, note="les écarts négatifs ne se compensent pas entre préfectures")
    return med_km, med_02, med_21


# --- Catalogue (§8) ----------------------------------------------------------------------------------

def catalogue(attendus):
    m = pd.read_csv(MATRICE / "01_Matrice.csv").set_index("ID")
    f = pd.read_csv(FAISABILITE).set_index("ID")
    v = pd.DataFrame(valeurs)
    lignes = []
    for ind in attendus:
        if ind in COMPLEMENTS:
            nom, definition, formule, unite, sens, niv = COMPLEMENTS[ind]
            src = {"Objectif": "O2", "Indicateur": nom, "Définition": definition, "Formule": formule, "Unité": unite,
                   "Sens": sens, "Maille (04)": "National", "Période (04)": "2010–2024", "Niveau (04)": niv,
                   "Réserve": "Hors 02 : n’entre ni dans O5-01, ni dans O5-02, ni dans les profils P1 à P6",
                   "Périmètre": "complément de l’énoncé, hors 02, hors classement (écart 22)"}
        else:
            r, q = m.loc[ind], f.loc[ind]
            src = {"Objectif": r["Objectif"], "Indicateur": r["Indicateur"], "Définition": r["Définition"],
                   "Formule": r["Formule"], "Unité": r["Unité"], "Sens": r["Sens"], "Maille (04)": q["Maille obtenue"],
                   "Période (04)": q["Période"], "Niveau (04)": q["Preuve (04)"],
                   "Réserve": notes(q["Réserve"] if pd.notna(q["Réserve"]) else "", RESERVES.get(ind, "")), "Périmètre": "02"}
        s = v[v["ID"] == ind]
        lignes.append({"ID": ind, **{k: src[k] for k in ("Objectif", "Indicateur", "Définition", "Formule", "Unité", "Sens")},
                       "Calcul au 07": CALCUL[ind][0], "Maille (04)": src["Maille (04)"], "Période (04)": src["Période (04)"],
                       "Niveau (04)": src["Niveau (04)"], "Justification (06)": CALCUL[ind][1], "Réserve": src["Réserve"],
                       "Périmètre": src["Périmètre"], "Lignes": len(s), "Valeurs renseignées": int(s["Valeur"].notna().sum())})
    return pd.DataFrame(lignes)


# --- Contrôles (§7) ----------------------------------------------------------------------------------

def controle(ident, intitule, attendu, mesure, ok):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC})


def annees(x):
    return [int(a) for a in re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)", str(x))]


def niveau_attendu(regle, annee):
    if regle.startswith("B en 2010 et 2022"):
        return "B" if annee in (2010, 2022) else "C"
    return regle


def concordance(v):
    """Valeurs du 07 face aux mêmes rapports calculés par le 06, de son côté (rapports_06.csv, prefectures_06.csv)."""
    r6 = pd.read_csv(EXPLORATION / "rapports_06.csv")
    r6 = r6[r6["Maille"] == "National"]
    nat = {"Part de chaque groupe": ("O1-02", ""), "Immatriculations pour 1 000 habitants": ("O1-04", ""),
           "Variation annuelle : immatriculations": ("O1-03", "croissance annuelle"),
           "Permis pour 1 000 habitants en âge de conduire": ("O1-07", ""),
           "Immatriculations pour un permis délivré": ("O1-09", ""), "Tués pour 100 000 habitants": ("O2-02", ""),
           "Accidents constatés pour 100 000 habitants": ("O2-03", ""), "Tués pour 10 000 véhicules": ("O2-04", ""),
           "Tués pour 100 accidents": ("O2-05", ""), "Blessés pour 100 accidents": ("O2-06", "")}
    a = r6[r6["Rapport"].isin(nat)].assign(ID=lambda d: d["Rapport"].map(lambda x: nat[x][0]),
                                          Mesure=lambda d: d["Rapport"].map(lambda x: nat[x][1]))
    a = a[["ID", "Territoire", "Année", "Catégorie", "Mesure", "Valeur", "Borne basse", "Borne haute"]]
    p6 = pd.read_csv(EXPLORATION / "prefectures_06.csv").set_index("Préfecture")
    cols = {"Km de routes classées": ("O4-01", "Ensemble", ""), "Km de route nationale revêtue": ("O4-01", "Route nationale revêtue", ""),
            "Km de route nationale non revêtue": ("O4-01", "Route nationale non revêtue", ""),
            "Km de piste rurale": ("O4-01", "Piste rurale", ""), "Km de voirie urbaine": ("O4-01", "Voirie urbaine", ""),
            "Km pour 1 000 km²": ("O4-02", "", ""), "Km pour 10 000 habitants": ("O4-03", "", ""),
            "Km bon": ("O3-01", "Bon", ""), "Km moyen": ("O3-01", "Moyen", ""), "Km mauvais": ("O3-01", "Mauvais", ""),
            "Km travaux": ("O3-01", "Travaux", ""), "Km non évalués": ("O3-01", "Non évalué", ""),
            "Part en mauvais état (%)": ("O3-02", "", ""), "Part en travaux (%)": ("O3-03", "", ""),
            "Part non évaluée (%)": ("O3-06", "", ""), "Auto-écoles comptées": ("O4-04", "comptées (R-12)", ""),
            "Auto-écoles recensées": ("O4-04", "recensées", ""), "Auto-écoles comptées pour 100 000 habitants": ("O4-05", "", ""),
            "Habitants par auto-école comptée": ("O4-06", "", ""),
            "Distance à l’auto-école comptée la plus proche (km)": ("O4-08", "", "distance (km)"),
            "Population 2022": ("O5-03", "", "")}
    b = pd.DataFrame([{"ID": i, "Territoire": pref, "Catégorie": c, "Mesure": m, "Valeur": p6.at[pref, col]}
                      for col, (i, c, m) in cols.items() for pref in p6.index])
    b["Année"] = None
    six = pd.concat([a, b], ignore_index=True)
    cle = ["ID", "Territoire", "Catégorie", "Mesure"]
    sept = v.copy()
    for d in (six, sept):
        d["Catégorie"] = d["Catégorie"].fillna("").astype(str)
        d["Mesure"] = d["Mesure"].fillna("").astype(str)
    sept["Année"] = sept["Année"].astype(str)
    six["Année"] = six["Année"].astype(str)
    nat6, pref6 = six[six["Année"] != "None"], six[six["Année"] == "None"].drop(columns="Année")
    j = pd.concat([nat6.merge(sept, on=cle + ["Année"], how="left", suffixes=("_06", "_07")),
                   pref6.merge(sept[sept["Maille"] == "Préfecture"], on=cle, how="left", suffixes=("_06", "_07"))], ignore_index=True)
    trouve = j["ID"].notna() & j["Maille"].notna()

    def egal(x, y):
        x, y = pd.to_numeric(x, errors="coerce"), pd.to_numeric(y, errors="coerce")
        return ((x - y).abs() < 1e-9) | (x.isna() & y.isna())

    ok = egal(j["Valeur_06"], j["Valeur_07"]) & egal(j["Borne basse_06"], j["Borne basse_07"]) & egal(j["Borne haute_06"], j["Borne haute_07"])
    diff = j[~ok | ~trouve]
    return len(j), int(trouve.sum()), diff


def controles_07(v, cat, attendus, d3, se01, p, meds):
    f = pd.read_csv(FAISABILITE).set_index("ID")
    calculables = sorted(f.index[f["Résultat (04)"].isin(["Cible", "Repli"])])
    non_calc = sorted(f.index[f["Résultat (04)"] == "Non"])
    ids = sorted(v["ID"].unique())
    du_02 = [i for i in ids if i not in COMPLEMENTS]
    controle("7-01", "Indicateurs calculés", "32 indicateurs du 02 et les 3 compléments ; ni O5-01 ni O5-02 ; aucun des 9 non calculables",
             f"{len(du_02)} du 02 (calculables au 04 : {len(calculables)}, moins {', '.join(PASSES_AU_08)}) ; "
             f"{len([i for i in ids if i in COMPLEMENTS])} compléments ; non calculables présents : "
             f"{', '.join(set(ids) & set(non_calc)) or 'aucun'}",
             du_02 == sorted(set(calculables) - set(PASSES_AU_08)) and len(du_02) == 32 and set(COMPLEMENTS) <= set(ids)
             and not set(ids) & set(non_calc + PASSES_AU_08))

    sans = [i for i in attendus if v[(v["ID"] == i)]["Valeur"].notna().sum() == 0]
    incomplet = v[v[["Source", "Année", "Niveau"]].isna().any(axis=1) | (v["Source"] == "")]
    controle("7-02", "Valeurs", "Chaque indicateur a au moins une valeur ; chaque valeur a sa source, son année, son niveau",
             f"{len(v)} lignes, {int(v['Valeur'].notna().sum())} valeurs ; indicateurs sans valeur : {', '.join(sans) or 'aucun'} ; "
             f"lignes sans source, année ou niveau : {len(incomplet)}", not sans and incomplet.empty)

    regles = cat.set_index("ID")["Niveau (04)"]
    v_an = v["Année"].map(lambda a: annees(a)[0] if annees(a) else None)
    attendu = [niveau_attendu(regles[i], a) for i, a in zip(v["ID"], v_an)]
    ecarts = v[v["Niveau"] != pd.Series(attendu, index=v.index)]
    detail = ecarts.groupby(["ID", "Catégorie", "Niveau"]).size().reset_index()
    controle("7-03", "Niveaux", "Le niveau de chaque valeur est celui du 04 (B en 2010 et 2022, C sinon, pour les taux par habitant)",
             f"{len(v) - len(ecarts)} lignes sur {len(v)} au niveau du 04" + (" ; autres : " + " ; ".join(
                 f"{r['ID']} {r['Catégorie']} en {r['Niveau']} ({r[0]})" for _, r in detail.iterrows()) if len(ecarts) else ""),
             ecarts.empty)

    maille = {"National": "National", "Préfecture": "Préfecture", "Zone": "Zone", "Tronçon": "Tronçon",
              "National, type d'usager": "National", "National, par catégorie de route": "National"}
    pb = []
    for i in attendus:
        s, c = v[v["ID"] == i], cat.set_index("ID").loc[i]
        cible = maille.get(c["Maille (04)"], c["Maille (04)"])
        an7, an4 = [a for x in s["Année"] for a in annees(x)], annees(c["Période (04)"])
        if cible not in set(s["Maille"]) or (min(an7), max(an7)) != (min(an4), max(an4)):
            pb.append(f"{i} : {sorted(set(s['Maille']))} {min(an7)}–{max(an7)} ; 04 : {c['Maille (04)']} {c['Période (04)']}")
    controle("7-04", "Maille et période", "Celles du 04 (faisabilite_indicateurs.csv) ; agrégats de O3-05, O4-07, O4-08 en plus",
             f"{len(attendus) - len(pb)} indicateurs sur {len(attendus)} conformes" + (" ; " + " | ".join(pb) if pb else ""), not pb)

    total, trouves, diff = concordance(v)
    controle("7-05", "Concordance avec le 06", "Même valeur que le 06 pour chaque rapport calculé des deux côtés",
             f"{total} valeurs comparées ({trouves} retrouvées au 07) ; différences : {len(diff)}" +
             (" ; " + " | ".join(f"{r['ID']} {r['Territoire']} {r['Catégorie']} {r['Année'] if 'Année' in r else ''} : 06 {r['Valeur_06']}, 07 {r['Valeur_07']}"
                                 for _, r in diff.head(10).iterrows()) if len(diff) else ""), len(diff) == 0 and trouves == total)

    o1 = v[v["ID"] == "O2-01"].set_index(["Année", "Catégorie"])["Valeur"]
    o2 = v[v["ID"] == "O2-02"].set_index("Année")["Dénominateur"]
    o4 = v[v["ID"] == "O2-04"].set_index("Année")["Dénominateur"]
    pb = []
    for ind, mesure, den in (("O2-E1", "Blessés", o2), ("O2-E2", "Accidents constatés", o4), ("O2-E3", "Blessés", o4)):
        for _, r in v[v["ID"] == ind].iterrows():
            if r["Numérateur"] != o1[(r["Année"], mesure)] or r["Dénominateur"] != den[r["Année"]] or HORS_02 not in r["Note"]:
                pb.append(f"{ind} {r['Année']}")
    ncomp = int(v["ID"].isin(COMPLEMENTS).sum())
    controle("7-06", "Compléments (écart 22)", "Numérateur de O2-01, dénominateur de O2-02 ou de O2-04, la même année ; « hors 02 » sur chaque ligne",
             f"{ncomp - len(pb)} lignes sur {ncomp} conformes" + (" ; " + ", ".join(pb) if pb else ""), not pb)

    tr = lire("D4_etat_troncons")
    km_etat = {e: tr[f"km_{e.lower()}"].sum() for e in ETATS[:4]}
    routes = gpd.read_file(TRAITE / "geo" / "routes_classees.geojson").to_crs(UTM31N)
    limites = gpd.read_file(TRAITE / "geo" / "prefectures.geojson").to_crs(UTM31N).union_all()
    km_trace = routes.intersection(limites).length.sum() / 1000
    ae = lire("D6_auto_ecoles")
    pop_nat = lire("D7_population_nationale").set_index("Année").at[2022, "Population"]
    totaux = [(f"km {e.lower()}", p[e].sum(), km_etat[e], 0.01, "tronçons du relevé (D4_etat_troncons)") for e in ETATS[:4]] + [
        ("km de routes classées", p["routes"].sum(), km_trace, 0.05, "tracé découpé par les limites des préfectures (geo)"),
        ("auto-écoles comptées", p["comptées"].sum(), int(ae["Comptée (R-12)"].sum()), 0, "D6, toutes préfectures"),
        ("auto-écoles recensées", p["recensées"].sum(), len(ae), 0, "D6, toutes préfectures"),
        ("population 2022", p["population"].sum(), pop_nat, 0, "D7_population_nationale")]
    zones_ok = all(abs(p.groupby("Zone")[c].sum().sum() - p[c].sum()) < 1e-6 for c in ["Mauvais", "routes", "comptées", "population"])
    controle("7-07", "Totaux (R-04)", "Somme des préfectures = total national : km par état, km de routes classées, auto-écoles, population ; "
             "somme des zones = somme des préfectures",
             " ; ".join(f"{nom} : {n(a, 2 if isinstance(a, float) else 0)} (national : {n(b, 2 if isinstance(b, float) else 0)}, {src})"
                        for nom, a, b, _, src in totaux) + f" ; zones : {'oui' if zones_ok else 'non'}",
             all(abs(a - b) <= tol for _, a, b, tol, _ in totaux) and zones_ok)

    rapports = v[v["Dénominateur"].notna() | v["Numérateur"].notna()]
    zero_nd = rapports[((rapports["Dénominateur"] == 0) | rapports["Dénominateur"].isna() | rapports["Numérateur"].isna())
                       & rapports["Valeur"].notna() & ~rapports["ID"].isin(["O3-07"])]
    mo = v[(v["Territoire"] == "Mô") & v["ID"].isin(["O3-02", "O3-03", "O3-06"])]
    o406 = v[v["ID"] == "O4-06"]
    permis13 = v[v["ID"].isin(["O1-06", "O1-07"]) & (v["Année"] == 2013)]
    controle("7-08", "Valeurs manquantes (R-10)", "Aucun zéro là où le rapport est non défini (Mô ; O4-06 sans auto-école comptée) ; "
             "2013 non renseignée pour les permis",
             f"rapports à dénominateur nul ou manquant avec une valeur : {len(zero_nd)} ; Mô (O3-02, O3-03, O3-06) vides : "
             f"{int(mo['Valeur'].isna().sum())} sur {len(mo)} ; O4-06 non définis : {int(o406['Valeur'].isna().sum())} "
             f"(sans auto-école comptée : {int((p['comptées'] == 0).sum())}) ; permis 2013 vides et annotés : "
             f"{int((permis13['Valeur'].isna() & permis13['Note'].str.contains('non renseignée')).sum())} sur {len(permis13)}",
             zero_nd.empty and mo["Valeur"].isna().all() and o406["Valeur"].isna().sum() == (p["comptées"] == 0).sum()
             and (permis13["Valeur"].isna() & permis13["Note"].str.contains("non renseignée")).all())

    controle("7-09", "SE-01 (R-09) au national", f"Au moins {n(se01)} tués par an : taux national sans cumul",
             f"tués de {n(d3['Tués'].min())} ({int(d3['Tués'].idxmin())}) à {n(d3['Tués'].max())} par an", d3["Tués"].min() >= se01)

    med_km, med_02, med_21 = meds
    o5 = v[v["ID"] == "O5-04"]
    o5 = o5[o5["Maille"] == "Préfecture"]
    ae5 = o5[o5["Mesure"] == "auto-écoles manquantes"]
    par_cible = ae5.groupby("Catégorie")["Valeur"].agg(["count", lambda s: int((s > 0).sum())])
    natures = ae5[ae5["Note"].str.contains("nature du zéro")].drop_duplicates("Territoire")["Note"]
    n15 = int(natures.str.contains("aucune auto-école recensée").sum())
    n8 = int(natures.str.contains("aucune agréée").sum())
    zero = p[p["comptées"] == 0]
    km_pos = int((o5[o5["Mesure"] == "km à remettre en état"]["Valeur"] > 0).sum())
    pos_02 = int(par_cible.iloc[:, 1][par_cible.index.str.startswith("cible du 02")].iloc[0])
    pos_21 = int(par_cible.iloc[:, 1][par_cible.index.str.startswith("cible de l’écart 21")].iloc[0])
    controle("7-10", "Écart 21", "Deux valeurs d’auto-écoles manquantes par préfecture ; une nature du zéro pour chaque préfecture "
             "sans auto-école comptée ; règle d’usage appliquée à la formule du 02",
             f"valeurs par cible : {', '.join(str(int(c)) for c in par_cible['count'])} ; natures : {len(natures)} "
             f"({n15} sans aucune recensée, {n8} sans agréée ; {int(zero['recensées'].sum())} non agréées recensées) ; "
             f"écarts positifs : formule du 02 (médiane {n(med_02, 2)}) {pos_02}, variante (médiane {n(med_21, 3)}) {pos_21} ; "
             f"réseau (médiane de O3-02 {n(med_km, 2)} %) {km_pos} → "
             f"{'variante pour la formation' if pos_02 == 0 else 'formule du 02 pour la formation'}, formule du 02 pour le réseau",
             (par_cible["count"] == 39).all() and len(par_cible) == 2 and len(natures) == len(zero) and n15 + n8 == len(zero))

    s6 = set(pd.read_csv(EXPLORATION / "signaux_06.csv")["ID"])
    cites = set()
    for txt in cat["Justification (06)"]:
        for a, b in re.findall(r"SIG-(\d+) à SIG-(\d+)", txt):
            cites |= {f"SIG-{k:02d}" for k in range(int(a), int(b) + 1)}
        cites |= set(re.findall(r"SIG-\d+", txt))
    vides = cat[cat["Justification (06)"].str.strip() == ""]["ID"].tolist()
    controle("7-11", "Justification", "Chaque indicateur cite un signal ou un paragraphe du 06 ; chaque signal cité existe",
             f"{len(cat) - len(vides)} indicateurs sur {len(cat)} justifiés ; {len(cites)} signaux cités, inconnus : "
             f"{', '.join(sorted(cites - s6)) or 'aucun'}", not vides and cites <= s6)


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    se01, se08 = seuil("SE-01"), seuil("SE-08")
    d3 = national(atypiques())
    p = prefectures()
    reseau(p)
    couverture(p, se08)
    meds = ecart_cible(p)

    f = pd.read_csv(FAISABILITE)
    attendus = [i for i in f["ID"] if i in CALCUL] + list(COMPLEMENTS)
    attendus = sorted(attendus, key=lambda i: (i[:3], i.replace("E", "Z")))  # compléments après O2-09
    v = pd.DataFrame(valeurs)
    v["_ordre"] = v["ID"].map({i: k for k, i in enumerate(attendus)})
    v = v.sort_values("_ordre", kind="stable").drop(columns="_ordre").reset_index(drop=True)
    cat = catalogue(attendus)
    controles_07(v, cat, attendus, d3, se01, p, meds)

    v.to_csv(SORTIE / "indicateurs_07.csv", index=False)
    cat.to_csv(SORTIE / "catalogue_07.csv", index=False)
    c = pd.DataFrame(controles)
    c.to_csv(SORTIE / "controles_07.csv", index=False)
    print(f"valeurs : {len(v)} lignes ; indicateurs : {v['ID'].nunique()} ; contrôles : "
          f"{int((c['Résultat'] == CONFORME).sum())} conformes sur {len(c)}")
    pd.set_option("display.max_colwidth", 400)
    print(c[["ID", "Contrôle", "Mesure", "Résultat"]].to_string(index=False))


if __name__ == "__main__":
    main()
