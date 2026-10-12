"""Étape 10 : recommandations (10_recommendation.md).

Lit les sorties du 07 (indicateurs_07.csv), du 08 (classement_08.csv, regions_08.csv), du 09 (hypotheses_09.csv),
l'état des tronçons (D4_etat_troncons.csv), la population en âge de conduire (D7_population_age_conduire.csv),
la table maîtresse (population rurale) et les couches geo/ (routes classées, préfectures).
N'écrit rien dans data/processed/ ni dans les sorties du 06 au 09.
Calcule chaque chiffre cité dans le 10 (R-19) :
- les 15 recommandations, avec les champs de R-18, leur priorité (§5.1) et leur nature (§5.2) ;
- l'accès rural à une route revêtue (O4-E1, écart 32) et les zones les moins bien desservies (§4.6) ;
- les 39 fiches préfectures de l'onglet « Actions par zone » (§4.7, §6.2).

Les textes des cartes (§6.1) sont écrits dans le document : le script les reprend et vérifie chacun de leurs nombres.

Sorties, dans data/analysis/10_recommandations/ : recommandations_10.csv, prefectures_10.csv, zones_10.csv, cartes_10.csv,
controles_10.csv.

Usage : .venv/bin/python scripts/recommandations_10.py
"""
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
TRAITE = RACINE / "data" / "processed"
GEO = TRAITE / "geo"
INDICATEURS = RACINE / "data" / "analysis" / "07_indicateurs" / "indicateurs_07.csv"
PRIORISATION = RACINE / "data" / "analysis" / "08_priorisation"
DIAGNOSTIC = RACINE / "data" / "analysis" / "09_diagnostic"
SORTIE = RACINE / "data" / "analysis" / "10_recommandations"
DOCUMENT = RACINE / "10_recommendation.md"  # tableaux du §5.1 et du §6, textes du §6.1, relus par les contrôles

UTM = "EPSG:32631"  # R-16
BANDE_KM = 2  # indice d'accès rural : moins de 2 km d'une route praticable toute l'année (ODD 9.1.1)
TOUTE_SAISON = "Route nationale revêtue"  # approche de « praticable toute l'année » (écart 32)
EN_TETE = 10  # REC-R3 : les 10 premiers tronçons critiques
ANNEES_PERMIS = [2022, 2023, 2024]  # cible de REC-F3 : moyenne des 3 dernières années (écart 29)
RN1 = r"^(?:TG[A-Z]{3,4} ?)?RN1 (?!BRETELLE)"  # la RN1 comme route propre, sans les bretelles (09 §5 c)
INTERDITS = r"\bH(?:3|4|5|6|7|9|10|11|12)\b|O2-E\d"  # hypothèses non testables ou infirmées, compléments (écart 22)
CODES = r"\b[OS]\d-\d{2}\b|\bO\d-E\d\b|\bH\d{1,2}\b|\bSE-\d+|\bSIG-\d+|\bREC-|\b[ÉéEe]cart \d+|\bP\d\b|\bR-\d+|\bPA-\d+"
PRIORITES = ["Haute", "Moyenne", "Faible"]
CONFORME, ECHEC = "conforme", "échec"
POP = "Population"

controles = []


def n(x, decimales=0):
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def pct(x):
    return "100 %" if round(x, 1) == 100 else f"{n(x, 1)} %"


def un(k, mot, pluriel=None, feminin=True):
    if k == 1:
        return f"une {mot}" if feminin else f"un {mot}"
    return f"{k} {pluriel or mot + 's'}"


def controle(ident, intitule, attendu, mesure, ok):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC})


# --- Entrées --------------------------------------------------------------------------------------------

def lire():
    v = pd.read_csv(INDICATEURS)
    c = pd.read_csv(PRIORISATION / "classement_08.csv")
    r = pd.read_csv(PRIORISATION / "regions_08.csv")
    h = pd.read_csv(DIAGNOSTIC / "hypotheses_09.csv").set_index("Code")
    tr = pd.read_csv(TRAITE / "D4_etat_troncons.csv")
    tm = pd.read_csv(TRAITE / "table_maitresse_prefecture.csv")
    age = pd.read_csv(TRAITE / "D7_population_age_conduire.csv")
    rec = v[(v["ID"] == "O4-04") & (v["Maille"] == "Préfecture") & (v["Catégorie"] == "recensées")]
    c["Auto-écoles recensées"] = c["Préfecture"].map(rec.set_index("Territoire")["Valeur"]).astype(int)
    c["Leviers"] = c["Leviers"].fillna("")
    c["Réseau"] = c["Leviers"].str.contains("réseau")
    c["Formation"] = c["Leviers"].str.contains("formation")
    return v, c, r, h, tr, tm, age


def troncons(tr, c):
    """Tronçons critiques (O3-05, repli du 02) : ceux qui ont des km en mauvais état, triés par ces km."""
    crit = tr[tr["km_mauvais"] > 0].sort_values(["km_mauvais", "Tronçon"], ascending=[False, True]).reset_index(drop=True)
    crit["Préfectures"] = crit["Préfectures traversées"].fillna("").str.split(" ; ")
    tete = crit.head(EN_TETE)
    par_pref = crit.explode("Préfectures")
    c["Tronçons critiques"] = c["Préfecture"].map(par_pref["Préfectures"].value_counts()).fillna(0).astype(int)
    c["Dont parmi les 10 plus dégradés"] = c["Préfecture"].map(tete.explode("Préfectures")["Préfectures"].value_counts()).fillna(0).astype(int)
    return crit, tete


def acces_rural(tm, c):
    """O4-E1 : part des ruraux à moins de 2 km d'une route nationale revêtue, la population rurale étant supposée
    répartie uniformément dans la préfecture (approche de l'indice d'accès rural, écart 32, niveau C)."""
    pref = gpd.read_file(GEO / "prefectures.geojson").to_crs(UTM)
    routes = gpd.read_file(GEO / "routes_classees.geojson").to_crs(UTM)
    bande = routes[routes["Type"] == TOUTE_SAISON].buffer(BANDE_KM * 1000).union_all()
    part = pref.geometry.intersection(bande).area / pref.geometry.area
    acces = pd.Series(part.to_numpy(), index=pref["Préfecture"])
    rur = tm.set_index("Préfecture")["population_2022_rurale"].fillna(0)
    c["Population rurale"] = c["Préfecture"].map(rur).astype(int)
    c["Part de surface à moins de 2 km"] = c["Préfecture"].map(acces)
    c["Ruraux à moins de 2 km"] = c["Population rurale"] * c["Part de surface à moins de 2 km"]
    c["Accès rural à une route revêtue (%)"] = np.where(c["Population rurale"] > 0,
                                                        (c["Part de surface à moins de 2 km"] * 100).round(1), np.nan)
    return acces


# --- §4.6 Zones les moins bien desservies -----------------------------------------------------------------

def zones(c, r):
    z = r[r["Maille"] == "Zone"].set_index("Territoire")
    g = c.groupby("Zone").agg(rur=("Population rurale", "sum"), proches=("Ruraux à moins de 2 km", "sum"))
    z["Population rurale"] = g["rur"]
    z["Ruraux plus loin"] = (g["rur"] - g["proches"]).round()
    z["O4-E1"] = g["proches"] / g["rur"].replace(0, np.nan) * 100  # aligné sur les zones ; vide pour le Grand Lomé
    rurales = z[z["Population rurale"] > 0]
    med = {"O4-03": z["O4-03"].median(), "O4-05": z["O4-05"].median(), "O4-E1": rurales["O4-E1"].median()}
    national = g["proches"].sum() / g["rur"].sum() * 100
    a1 = set(z[(z["O4-03"] < med["O4-03"]) & (z["O4-05"] < med["O4-05"])].index)
    route = set(rurales[rurales["O4-E1"] < med["O4-E1"]].index)
    formation = set(z[z["O4-05"] < med["O4-05"]].index)
    return z, med, national, a1, route, formation


def table_zones(z, c, med, national, a1, route, formation, v):
    """zones_10.csv : les deux analyses du §4.6 et la conclusion par dimension, par zone, avec les médianes et le pays,
    pour que le tableau de bord les affiche sans rien agréger."""
    tm = pd.read_csv(TRAITE / "table_maitresse_prefecture.csv")
    etats = {"km_etat_bon": "Km en bon état", "km_etat_moyen": "Km en état moyen", "km_etat_mauvais": "Km en mauvais état",
             "km_etat_travaux": "Km en travaux", "km_rn_non_evaluee": "Km non évalués"}
    ke = tm.groupby("Zone")[list(etats)].sum().rename(columns=etats)
    o402 = v[(v["ID"] == "O4-02") & (v["Maille"] == "Préfecture")].set_index("Territoire")[["Numérateur", "Dénominateur"]]
    d = o402.join(c.set_index("Préfecture")["Zone"]).groupby("Zone").sum()
    rec = {"cumul": "REC-Z3", "route": "REC-Z1", "formation": "REC-Z2"}
    lignes = []
    for k, x in z.iterrows():
        r_, f_ = k in route, k in formation
        cas = "cumul" if r_ and f_ else "route" if r_ else "formation" if f_ else ""
        lignes.append({"Maille": "Zone", "Zone": k, POP: int(x[POP]), "Population rurale": int(x["Population rurale"]),
                       "Ruraux à plus de 2 km d’une route revêtue": int(x["Ruraux plus loin"]),
                       "Accès rural à une route revêtue (%)": round(x["O4-E1"], 2) if pd.notna(x["O4-E1"]) else np.nan,
                       "Desserte (km pour 10 000 hab.)": x["O4-03"], "Km de routes pour 1 000 km²": round(d.at[k, "Numérateur"] / d.at[k, "Dénominateur"] * 1000, 1),
                       "Auto-écoles pour 100 000 hab.": x["O4-05"], "Part en mauvais état (%)": x["O3-02"],
                       **{col: round(ke.at[k, col], 1) for col in etats.values()},
                       "Analyse 1 : moins bien desservie": k in a1, "Route : sous la médiane": r_, "Formation : sous la médiane": f_,
                       "Moins bien desservie pour": {"cumul": "la route et la formation", "route": "la route", "formation": "la formation"}.get(cas, ""),
                       "Recommandation": rec.get(cas, "")})
    lignes.append({"Maille": "Médiane des zones", "Zone": "", "Accès rural à une route revêtue (%)": round(med["O4-E1"], 2),
                   "Desserte (km pour 10 000 hab.)": round(med["O4-03"], 3), "Auto-écoles pour 100 000 hab.": round(med["O4-05"], 3)})
    lignes.append({"Maille": "Pays", "Zone": "Togo", POP: int(c[POP].sum()), "Population rurale": int(c["Population rurale"].sum()),
                   "Ruraux à plus de 2 km d’une route revêtue": int(round(c["Population rurale"].sum() - c["Ruraux à moins de 2 km"].sum())),
                   "Accès rural à une route revêtue (%)": round(national, 2)})
    t = pd.DataFrame(lignes)
    for col in (POP, "Population rurale", "Ruraux à plus de 2 km d’une route revêtue"):
        t[col] = t[col].astype("Int64")
    return t


# --- §4 Les recommandations ---------------------------------------------------------------------------------

def recommandations(v, c, r, h, crit, tete, age, z, med, national, route, formation):
    cl = c[c["Classée"]] if "Classée" in c else c[c["O3-02"].notna()]
    m0302 = round(float(cl["O3-02"].median()), 2)  # cible PA-04 du réseau
    m0405 = round(float(c[c["Auto-écoles comptées"] > 0]["O4-05"].median()), 3)  # cible de l'écart 21
    m0403 = round(float(c["O4-03"].median()), 2)  # écart 28
    pays = int(c[POP].sum())
    res, form = c[c["Réseau"]], c[c["Formation"]]
    r1, r2 = res[res["Formation"]], res[~res["Formation"]]
    f1, f2 = form[form["Auto-écoles recensées"] == 0], form[form["Auto-écoles recensées"] > 0]
    km, ae = "O5-04 km à remettre en état", "O5-04 auto-écoles manquantes (écart 21)"

    def uniques(prefs):
        return int(crit["Préfectures"].apply(lambda l: bool(set(l) & set(prefs))).sum())

    def zones_de(p):
        return " ; ".join(sorted(set(p["Zone"]), key=list(z.index).index))

    o109 = v[(v["ID"] == "O1-09") & (v["Maille"] == "National")]
    cumul = o109[o109["Année"] == "2007–2024"].set_index("Catégorie")["Valeur"]
    annuel = o109[(o109["Catégorie"] == "A") & o109["Année"].astype(str).str.fullmatch(r"\d{4}")]
    annuel = annuel.set_index(annuel["Année"].astype(str))
    permis_a = annuel.loc[[str(a) for a in ANNEES_PERMIS], "Dénominateur"].astype(int)
    rapport_a = annuel["Valeur"].astype(float)
    autres = cumul.drop("A")
    age18 = int(age[(age["Année"] == 2022) & (age["Catégorie"] == "A")]["Population en âge de conduire"].iloc[0])
    tues2r = float(v[(v["ID"] == "O2-09") & (v["Catégorie"] == "Deux et trois-roues motorisés")]["Valeur"].iloc[0])
    parc = v[(v["ID"] == "O1-05") & (v["Année"].astype(str) == "2021")].set_index("Catégorie")
    part_moto = {k: parc.at["Moto", col] / parc.at["Ensemble", col] * 100 for k, col in
                 (("bas", "Borne basse"), ("centre", "Valeur"), ("haut", "Borne haute"))}
    indice = sorted(round(tues2r / x, 2) for x in part_moto.values())
    o201 = v[(v["ID"] == "O2-01") & (v["Année"].astype(str) == "2022")].set_index("Catégorie")["Valeur"]
    non_testables = int((h["Verdict"] == "non testable").sum())
    rn1 = int(tete["Tronçon"].str.contains(RN1).sum())
    tete_prefs = sorted(set(tete["Préfectures"].sum()))
    mo = c[c["Préfecture"] == "Mô"].iloc[0]
    zc = z.loc[sorted(route & formation)]
    zr = z.loc[sorted(route - formation)]
    zf = z.loc[sorted(formation - route, key=lambda k: -z.at[k, POP])]
    pz3 = c[c["Zone"].isin(zc.index) & (c["Réseau"] | c["Formation"])]
    pz1 = c[c["Zone"].isin(zr.index) & c["Réseau"]]
    pz2 = c[c["Zone"].isin(zf.index) & c["Formation"]]
    n_ = lambda s: " et ".join([", ".join(s[:-1]), s[-1]] if len(s) > 1 else s)
    verif = "Vérifier sur place l’état relevé en 2020, puis "
    rows = []

    def ajouter(**k):
        rows.append(k)

    ajouter(ID="REC-R1", Levier="Réseau", **{"Sous-levier": "Entretien"}, _attr="cumul" if (r1["O5-01 déficits"] == 2).all() else "deficit",
            Constat=f"{len(r1)} préfectures cumulent un réseau dégradé et aucune auto-école comptée",
            Ampleur=f"{n(r1['Km en mauvais état'].sum(), 1)} km en mauvais état sur {n(r1['Km évalués'].sum(), 1)} km évalués ; {uniques(r1['Préfecture'])} tronçons critiques",
            Territoire=" ; ".join(f"{p} ({zz})" for p, zz in zip(r1["Préfecture"], r1["Zone"])),
            Déficit=f"{n(r1[km].sum(), 1)} km à remettre en état (" + " + ".join(n(x, 1) for x in r1[km]) + ")",
            Action=verif + "remettre en état les tronçons critiques",
            Acteur="Ministère des travaux publics, fonds d’entretien routier",
            Cible=f"Ramener chaque préfecture à la médiane nationale : {n(m0302, 2)} % de km en mauvais état",
            _phrase=f"Porter la part de routes en mauvais état de {n(r1['O3-02'].min(), 0)} à {n(r1['O3-02'].max(), 0)} % à {n(m0302, 2)} %",
            _pop=int(r1[POP].sum()), _prefs=list(r1["Préfecture"]), Horizon="1 an (vérification), 3 ans (entretien)", _h="3 ans",
            Suivi="O3-02", Niveau="C", Réserve="Relevé de 2020 ; méthode de notation non documentée", Source="SIG-29 ; 09 §6 ; 08 §5",
            _n=[len(r1), r1["O3-02"].min(), r1["O3-02"].max(), uniques(r1["Préfecture"]), m0302, r1[km].sum(), r1[POP].sum()])
    ajouter(ID="REC-R2", Levier="Réseau", **{"Sous-levier": "Entretien"}, _attr="deficit",
            Constat=f"{len(r2)} autres préfectures ont un réseau dégradé, sans déficit de formation",
            Ampleur=f"{n(r2['Km en mauvais état'].sum(), 1)} km en mauvais état sur {n(r2['Km évalués'].sum(), 1)} km évalués ; {uniques(r2['Préfecture'])} tronçons critiques",
            Territoire=" ; ".join(f"{p} ({zz})" for p, zz in zip(r2["Préfecture"], r2["Zone"])),
            Déficit=f"{n(r2[km].sum(), 1)} km à remettre en état",
            Action=verif + "remettre en état les tronçons critiques", Acteur="Ministère des travaux publics, fonds d’entretien routier",
            Cible=f"Ramener chaque préfecture à la médiane nationale : {n(m0302, 2)} % de km en mauvais état",
            _phrase=f"Porter la part de routes en mauvais état de {n(r2['O3-02'].min(), 1)} à {n(r2['O3-02'].max(), 1)} % à {n(m0302, 2)} %",
            _pop=int(r2[POP].sum()), _prefs=list(r2["Préfecture"]), Horizon="1 an (vérification), 5 ans (entretien)", _h="5 ans",
            Suivi="O3-02", Niveau="C",
            Réserve=f"Population portée par Agoè-Nyivé : {n(c.set_index('Préfecture').at['Agoè-Nyivé', POP])} habitants pour {n(c.set_index('Préfecture').at['Agoè-Nyivé', km], 1)} km ; relevé de 2020",
            Source="08 §5", _n=[len(r2), r2["O3-02"].min(), r2["O3-02"].max(), r2[km].sum(), r2[POP].sum(),
                               c.set_index("Préfecture").at["Agoè-Nyivé", POP], c.set_index("Préfecture").at["Agoè-Nyivé", km]])
    pt = c[c["Préfecture"].isin(tete_prefs)]
    ajouter(ID="REC-R3", Levier="Réseau", **{"Sous-levier": "Entretien"}, _attr="deficit",
            Constat=f"{len(crit)} tronçons ont des km en mauvais état, {n(crit['km_mauvais'].sum(), 2)} km en tout",
            Ampleur=f"Les {EN_TETE} premiers : {n(tete['km_mauvais'].sum(), 1)} km en mauvais état sur {n(tete['km_total'].sum(), 1)} km ; {rn1} sur la RN1",
            Territoire=f"{len(tete_prefs)} préfectures traversées : " + ", ".join(tete_prefs),
            Déficit=f"{n(tete['km_mauvais'].sum(), 1)} km en mauvais état",
            Action=verif + f"remettre en état les {EN_TETE} premiers tronçons critiques", Acteur="Ministère des travaux publics, fonds d’entretien routier",
            Cible=f"Ramener la part de km en mauvais état de ces tronçons de {n(tete['km_mauvais'].sum() / tete['km_total'].sum() * 100, 1)} % à {n(m0302, 2)} %",
            _phrase=f"Porter les {EN_TETE} tronçons les plus dégradés de {n(tete['km_mauvais'].sum() / tete['km_total'].sum() * 100, 1)} % à {n(m0302, 2)} % de km en mauvais état",
            _pop=int(pt[POP].sum()), _prefs=tete_prefs, Horizon="1 an (vérification), 3 ans (entretien)", _h="3 ans",
            Suivi="O3-05", Niveau="C", Réserve="Les tronçons croisent REC-R1 et REC-R2 ; 2 tronçons de la RN1, chacun pour ses propres km : pas le corridor (H5 infirmée) ; relevé de 2020",
            Source="O3-05 ; 07 §3", _n=[len(crit), crit["km_mauvais"].sum(), EN_TETE, tete["km_mauvais"].sum(), rn1, len(tete_prefs), 2020])
    ajouter(ID="REC-R4", Levier="Réseau", **{"Sous-levier": "Desserte"}, _attr="aucun",
            Constat="Mô est la seule préfecture sans route classée",
            Ampleur=f"Desserte nulle ; auto-école comptée la plus proche à {n(mo['O4-08'], 1)} km",
            Territoire="Mô (Centrale)", Déficit=f"Environ {n(m0403 * mo[POP] / 10000, 1)} km de routes classées pour la médiane nationale de desserte ({n(m0403, 2)} km pour 10 000 habitants)",
            Action="Vérifier la desserte sur place (routes non classées, pistes), puis étudier une liaison classée",
            Acteur="Ministère des travaux publics", Cible=f"Porter la desserte de 0 à {n(m0403, 2)} km pour 10 000 habitants (ordre de grandeur)",
            _phrase=f"Porter la desserte de 0 à {n(m0403, 2)} km pour 10 000 habitants",
            _pop=int(mo[POP]), _prefs=["Mô"], Horizon="1 an (vérification), 5 ans", _h="5 ans", Suivi="O4-03", Niveau="C",
            Réserve="Ordre de grandeur, pas un tracé ; la desserte ne déclenche aucun profil du 02 (SE-06)", Source="08 §3.2 b ; écart 28",
            _n=[mo["O4-08"], m0403, m0403 * mo[POP] / 10000, mo[POP], 0])
    ajouter(ID="REC-F1", Levier="Formation", **{"Sous-levier": "Ouverture"}, _attr="deficit",
            Constat=f"{len(f1)} préfectures n’ont aucune auto-école, ni comptée ni recensée",
            Ampleur=f"Auto-école comptée la plus proche à {n(f1['O4-08'].min(), 1)} à {n(f1['O4-08'].max(), 1)} km",
            Territoire=" ; ".join(f"{p} ({zz})" for p, zz in zip(f1["Préfecture"], f1["Zone"])),
            Déficit=f"{int(f1[ae].sum())} auto-écoles", Action="Vérifier sur place qu’il n’existe aucune auto-école, puis en ouvrir",
            Acteur="Ministère chargé des transports, auto-écoles",
            Cible=f"{n(m0405, 3)} auto-école pour 100 000 habitants dans chaque préfecture (écart 21)",
            _phrase=f"Porter l’offre de 0 à {n(m0405, 3)} auto-école pour 100 000 habitants : {int(f1[ae].sum())} auto-écoles",
            _pop=int(f1[POP].sum()), _prefs=list(f1["Préfecture"]), Horizon="1 an (vérification), 3 ans (ouverture)", _h="3 ans",
            Suivi="O4-05", Niveau="C", Réserve="Nature du zéro à vérifier sur place ; activité des auto-écoles non connue (écart 13)",
            Source="08 §5 ; H8 confirmée", _n=[len(f1), f1["O4-08"].min(), f1["O4-08"].max(), m0405, f1[ae].sum(), f1[POP].sum()])
    nonagr = int((f2["Auto-écoles recensées"] - f2["Auto-écoles comptées"]).sum())
    ajouter(ID="REC-F2", Levier="Formation", **{"Sous-levier": "Vérification"}, _attr="deficit",
            Constat=f"{len(f2)} préfectures n’ont aucune auto-école agréée, mais {nonagr} y sont recensées",
            Ampleur=f"{nonagr} auto-écoles recensées non agréées", Territoire=" ; ".join(f"{p} ({zz})" for p, zz in zip(f2["Préfecture"], f2["Zone"])),
            Déficit=f"{int(f2[ae].sum())} auto-écoles, si aucune n’est agréée",
            Action=f"Vérifier l’activité et l’agrément des {nonagr} auto-écoles recensées, puis combler le manque restant",
            Acteur="Ministère chargé des transports, auto-écoles",
            Cible=f"{n(m0405, 3)} auto-école pour 100 000 habitants dans chaque préfecture (écart 21)",
            _phrase=f"Vérifier {nonagr} auto-écoles, puis porter l’offre à {n(m0405, 3)} pour 100 000 habitants",
            _pop=int(f2[POP].sum()), _prefs=list(f2["Préfecture"]), Horizon="1 an (vérification), 3 ans (ouverture)", _h="3 ans",
            Suivi="O4-05", Niveau="C", Réserve="Le manque est peut-être administratif ; activité non connue (écart 13)",
            Source="08 §5 ; H8 confirmée", _n=[len(f2), nonagr, f2[ae].sum(), f2[POP].sum()])
    cible_a = int(round(permis_a.mean()))
    ajouter(ID="REC-F3", Levier="Formation", **{"Sous-levier": "Permis moto"}, _attr="hypothese" if h.at["H1", "Verdict"] == "confirmée" else "aucun",
            Constat=f"{n(cumul['A'], 1)} immatriculations de deux-roues par permis A en cumul 2007–2024 (H1 confirmée)",
            Ampleur=f"{n(autres.min(), 2)} à {n(autres.max(), 2)} pour les autres catégories ; rapport annuel des motos : "
                    + ", ".join(f"{n(rapport_a[str(a)], 2)} en {a}" for a in ANNEES_PERMIS),
            Territoire="National", Déficit=f"Permis A : " + ", ".join(f"{n(permis_a[str(a)])} en {a}" for a in ANNEES_PERMIS),
            Action="Faire du permis moto la priorité de la formation des auto-écoles, existantes et à ouvrir",
            Acteur="Ministère chargé des transports, auto-écoles", Cible=f"Au moins {n(cible_a)} permis A par an (moyenne 2022–2024, écart 29)",
            _phrase=f"Porter les permis A délivrés à au moins {n(cible_a)} par an",
            _pop=age18, _prefs=[], Horizon="3 ans", _h="3 ans", Suivi="O1-06 ; O1-09", Niveau=h.at["H1", "Niveau"],
            Réserve="2022 et 2024 atypiques [SIG-05] : la moyenne en dépend", Source="09 §5, H1",
            _n=[2007, 2024, cumul["A"], autres.min(), autres.max(), 2022, rapport_a["2022"], rapport_a["2024"], age18, cible_a])
    ajouter(ID="REC-S1", Levier="Sécurité routière", **{"Sous-levier": "Deux-roues"}, _attr="hypothese" if h.at["H2", "Verdict"] == "confirmée" else "aucun",
            Constat=f"{n(tues2r)} % des tués de 2021 sont des usagers de deux et trois-roues motorisés (H2 confirmée sur les tués)",
            Ampleur=f"{n(part_moto['bas'], 1)} % à {n(part_moto['haut'], 1)} % de motos dans le parc estimé ; indice de {n(indice[0], 2)} à {n(indice[-1], 2)}",
            Territoire="National", Déficit=f"Indice de surreprésentation de {n(indice[0], 2)} à {n(indice[-1], 2)}",
            Action="Vérifier la part des deux-roues parmi les tués sur une seconde année, puis cibler leurs usagers : contrôle du casque et du permis A, sensibilisation",
            Acteur="Organisme chargé de la sécurité routière (ONSR), police, gendarmerie",
            Cible="Indice sous 1 : part des deux-roues parmi les tués sous leur part dans le parc (écart 30)",
            _phrase=f"Porter l’indice des deux-roues parmi les tués de {n(indice[0], 2)}–{n(indice[-1], 2)} à moins de 1",
            _pop=pays, _prefs=[], Horizon="1 an (vérification), 3 ans", _h="3 ans", Suivi="O2-09", Niveau=h.at["H2", "Niveau"],
            Réserve="Surreprésentation faible, mesurée sur une seule année (2021, OMS)", Source="09 §5, H2 (écart 26)",
            _n=[2021, tues2r, part_moto["bas"], part_moto["haut"], indice[0], indice[-1]])
    zc_km, zc_ae = pz3[pz3["Réseau"]][km].sum(), pz3[pz3["Formation"]][ae].sum()
    ajouter(ID="REC-Z3", Levier="Zones les moins desservies", **{"Sous-levier": "Ciblage par zone : cumul"},
            _attr="cumul" if set(zc.index) <= (route & formation) and len(zc) else "aucun",
            Constat=f"{n_(list(zc.index))} : seule zone sous la médiane pour l’accès à la route et pour la formation",
            Ampleur=" ; ".join(f"{k} : {n(zc.at[k, 'O4-E1'], 1)} % des ruraux à moins de 2 km d’une route revêtue ({n(national, 1)} % dans le pays), "
                               f"{n(zc.at[k, 'Ruraux plus loin'])} ruraux plus loin, {n(zc.at[k, 'O3-02'], 1)} % de km en mauvais état, "
                               f"{n(zc.at[k, 'O4-05'], 2)} auto-école pour 100 000 habitants" for k in zc.index),
            Territoire=" ; ".join(f"{k} ({int(zc.at[k, 'Préfectures'])} préfectures)" for k in zc.index),
            Déficit=f"Réseau : {n(zc_km, 1)} km dans {int(pz3['Réseau'].sum())} préfectures ; formation : {int(zc_ae)} auto-écoles dans {int(pz3['Formation'].sum())} préfectures ; déjà dans les leviers",
            Action=f"Vérifier, puis remettre en état les {n(zc_km, 1)} km et ouvrir les {int(zc_ae)} auto-écoles en premier",
            Acteur="Ministère des travaux publics, fonds d’entretien routier ; ministère chargé des transports, auto-écoles",
            Cible=f"{n(m0302, 2)} % de km en mauvais état ; {n(m0405, 3)} auto-école pour 100 000 habitants, dans chaque préfecture au levier",
            _phrase=f"Remettre en état {n(zc_km, 1)} km et ouvrir {int(zc_ae)} auto-écoles en premier",
            _pop=int(zc[POP].sum()), _prefs=list(pz3["Préfecture"]), Horizon="1 an (vérification), 3 ans (action)", _h="3 ans",
            Suivi="O3-02, O4-05 ; O4-E1 en contexte", Niveau="C",
            Réserve="Quantités déjà dans les leviers ; accès rural estimé avec une population répartie uniformément (écart 32)",
            Source="§4.6 ; 08 §6 ; écarts 31 et 32",
            _n=[v_ for k in zc.index for v_ in (zc.at[k, "O4-E1"], zc.at[k, "O3-02"], zc.at[k, "O4-05"], zc.at[k, "Ruraux plus loin"])]
               + [BANDE_KM, national, zc_km, zc_ae, zc[POP].sum()])
    ajouter(ID="REC-Z1", Levier="Zones les moins desservies", **{"Sous-levier": "Ciblage par zone : route"}, _attr="deficit",
            Constat=f"{n_(list(zr.index))} : sous la médiane pour l’accès à la route, sans déficit de formation de zone",
            Ampleur=" ; ".join(f"{k} : {n(zr.at[k, 'O4-E1'], 1)} % des ruraux à moins de 2 km d’une route revêtue, {n(zr.at[k, 'Ruraux plus loin'])} ruraux plus loin, "
                               f"{n(zr.at[k, 'O3-02'], 1)} % de km en mauvais état" for k in zr.index),
            Territoire=" ; ".join(f"{k} ({int(zr.at[k, 'Préfectures'])} préfectures)" for k in zr.index),
            Déficit=f"{n(pz1[km].sum(), 1)} km dans {len(pz1)} préfectures au levier réseau ; déjà dans REC-R1 et REC-R2",
            Action=f"Vérifier, puis remettre en état les {n(pz1[km].sum(), 1)} km en premier", Acteur="Ministère des travaux publics, fonds d’entretien routier",
            Cible=f"{n(m0302, 2)} % de km en mauvais état dans chaque préfecture au levier ; accès rural suivi, sans cible",
            _phrase=f"Remettre en état {n(pz1[km].sum(), 1)} km en premier",
            _pop=int(zr[POP].sum()), _prefs=list(pz1["Préfecture"]), Horizon="1 an (vérification), 3 ans (entretien)", _h="3 ans",
            Suivi="O3-02 ; O4-E1 en contexte", Niveau="C", Réserve="Quantités déjà dans les leviers ; accès rural estimé (écart 32)",
            Source="§4.6 ; écarts 31 et 32",
            _n=[v_ for k in zr.index for v_ in (zr.at[k, "O4-E1"], zr.at[k, "O3-02"], zr.at[k, "Ruraux plus loin"])]
               + [BANDE_KM, national, len(pz1), pz1[km].sum(), zr[POP].sum()])
    ajouter(ID="REC-Z2", Levier="Zones les moins desservies", **{"Sous-levier": "Ciblage par zone : formation"}, _attr="deficit",
            Constat=f"{n_(list(zf.index))} : le moins d’auto-écoles par habitant des 6 zones",
            Ampleur=", ".join(f"{k} {n(zf.at[k, 'O4-05'], 2)}" for k in zf.index) + f" auto-école pour 100 000 habitants (médiane : {n(med['O4-05'], 2)})",
            Territoire=" ; ".join(f"{k} ({int(zf.at[k, 'Préfectures'])} préfectures)" for k in zf.index),
            Déficit=f"{int(pz2[ae].sum())} auto-écoles dans {len(pz2)} préfectures sans auto-école agréée ; déjà dans REC-F1 et REC-F2",
            Action=f"Vérifier, puis ouvrir les {int(pz2[ae].sum())} auto-écoles en premier", Acteur="Ministère chargé des transports, auto-écoles",
            Cible=f"{n(m0405, 3)} auto-école pour 100 000 habitants dans chaque préfecture au levier (écart 21)",
            _phrase=f"Ouvrir {int(pz2[ae].sum())} auto-écoles en premier",
            _pop=int(zf[POP].sum()), _prefs=list(pz2["Préfecture"]), Horizon="1 an (vérification), 3 ans (ouverture)", _h="3 ans",
            Suivi="O4-05", Niveau="C", Réserve="Quantités déjà dans REC-F1 et REC-F2 ; activité non connue (écart 13) ; Savanes en cas limite pour la route",
            Source="§4.6, analyse 1 ; écart 31", _n=[*zf["O4-05"], len(pz2), pz2[ae].sum(), zf[POP].sum()])
    donnees = [
        ("REC-D1", "Collecte", "condition", "Les accidents ne sont publiés qu’au niveau national",
         f"{n(o201['Accidents constatés'])} accidents et {n(o201['Tués'])} tués en 2022 ; {non_testables} hypothèses non testables",
         "Créer une base d’accidents par préfecture, tenue par l’ONSR, au format commun police–gendarmerie : préfecture, mois, âge, catégorie de véhicule, cause, accident corporel ou matériel, définition du tué",
         "39 préfectures renseignées sur 39", "Porter les préfectures renseignées sur les accidents de 0 à 39", [o201["Accidents constatés"], o201["Tués"], 2022, non_testables]),
        ("REC-D2", "Ouverture des données", "verifie", "L’état du réseau vient d’un seul relevé, de 2020, sans géométrie",
         "Couches « Dégradations » et « Ponts » de la collecte 2021–2022 non ouvertes ; méthode de notation non publiée",
         "Ouvrir les couches « Dégradations » et « Ponts » du géoportail ; publier la méthode de notation, un identifiant de tronçon commun et un relevé postérieur à 2020",
         "2 couches ouvertes et un relevé postérieur à 2020", "Ouvrir 2 couches et publier un relevé récent", [2020, 2021, 2022, int(res.shape[0])]),
        ("REC-D3", "Ouverture des données", "verifie", "L’activité des auto-écoles n’est pas publiée",
         f"{int(c['Auto-écoles recensées'].sum())} auto-écoles recensées, dont {int(c['Auto-écoles comptées'].sum())} comptées",
         "Publier l’activité des auto-écoles collectée par PRISE (personnel, activité, horaires, véhicules)",
         f"Activité publiée pour les {int(c['Auto-écoles recensées'].sum())} auto-écoles", f"Publier l’activité des {int(c['Auto-écoles recensées'].sum())} auto-écoles recensées",
         [c["Auto-écoles recensées"].sum(), len(form)]),
        ("REC-D4", "Ouverture des données", "aucun", "Aucun parc en circulation n’est publié ; plusieurs libellés du portail sont inexacts",
         "« Parc automobile immatriculé », « accidents mortels », « premières mises en circulation », « RN4 »",
         "Publier un parc en circulation, et corriger les libellés du portail", "Un parc en circulation publié ; 4 libellés corrigés",
         "Publier un parc en circulation et corriger 4 libellés", []),
    ]
    for ident, sous, attr, constat, ampleur, action, cible, phrase, nombres in donnees:
        ajouter(ID=ident, Levier="Données", **{"Sous-levier": sous}, _attr=attr, Constat=constat, Ampleur=ampleur, Territoire="National",
                Déficit="Donnée manquante (P5)", Action=action, Acteur="Producteurs des données", Cible=cible, _phrase=phrase,
                _pop=pays, _prefs=[], Horizon="1 an", _h="1 an", Suivi="Part des territoires renseignés", Niveau="—",
                Réserve="Dépend des producteurs ; aucune recommandation d’investissement tant que la donnée manque (R-10)",
                Source="03 §8 ; 04 §10", _n=nombres)

    k = pd.DataFrame(rows)
    k["Priorité"] = k["_attr"].map({"cumul": "Haute", "condition": "Haute", "deficit": "Moyenne", "hypothese": "Moyenne",
                                     "verifie": "Moyenne", "aucun": "Faible"})
    k["Nature"] = np.where(k["Niveau"] == "C", "Conditionnelle", "Immédiate")
    k["Population concernée"] = k["_pop"]
    return k, dict(m0302=m0302, m0405=m0405, m0403=m0403, r1=r1, r2=r2, f1=f1, f2=f2, pz1=pz1, pz2=pz2, pz3=pz3)


# --- §4.7 et §6.2 Fiches préfectures ------------------------------------------------------------------------

def fiches(c, k, cibles):
    cible = cibles["m0405"]
    maxi = c["O4-05"].max()
    par_pref = {}
    for _, x in k.iterrows():
        for p in x["_prefs"]:
            par_pref.setdefault(p, []).append(x["ID"])
    lignes = []
    for _, x in c.sort_values(["O5-02 rang", POP], ascending=[True, False], na_position="last").iterrows():
        p = x["Préfecture"]
        if p == "Mô":
            reseau = "Aucune route classée : ni état ni km évalué."
        else:
            t = x["Tronçons critiques"]
            tron = "aucun tronçon critique" if t == 0 else un(t, "tronçon critique", "tronçons critiques", feminin=False)
            etat = "Aucune route en mauvais état" if x["O3-02"] == 0 else f"{pct(x['O3-02'])} des routes en mauvais état"
            reseau = f"{etat} ({n(x['Km évalués'], 1)} km évalués, {tron})."
        ce, re_ = int(x["Auto-écoles comptées"]), int(x["Auto-écoles recensées"])
        if ce == 0 and re_ == 0:
            formation = f"Aucune auto-école, ni agréée ni recensée. La plus proche est à {n(x['O4-08'], 1)} km."
        elif ce == 0:
            formation = (f"Aucune auto-école agréée ; {un(re_, 'auto-école')} recensée{'s' if re_ > 1 else ''} sans agrément. "
                         f"La plus proche agréée est à {n(x['O4-08'], 1)} km.")
        else:
            formation = f"{un(ce, 'auto-école').capitalize()} agréée{'s' if ce > 1 else ''}, soit {n(x['O4-05'], 2)} pour 100 000 habitants"
            formation += " : la plus forte offre du pays." if x["O4-05"] == maxi else (", au-dessus de la cible." if x["O4-05"] >= cible else ".")
        actions = []
        if p == "Mô":
            actions.append("Vérifier la desserte sur place : aucune route classée.")
        if x["Réseau"]:
            actions.append(f"Vérifier l’état sur place, puis remettre en état {n(x['O5-04 km à remettre en état'], 1)} km.")
        if x["Formation"]:
            a = int(x["O5-04 auto-écoles manquantes (écart 21)"])
            ouvrir = "en ouvrir une" if a == 1 else f"en ouvrir {a}"
            if re_ == 0:
                actions.append(f"Vérifier qu’aucune auto-école n’existe, puis {ouvrir}.")
            else:
                objet = "de l’auto-école recensée" if re_ == 1 else f"des {re_} auto-écoles recensées"
                actions.append(f"Vérifier l’activité et l’agrément {objet}, puis {ouvrir} si le manque est réel.")
        if not (x["Réseau"] or x["Formation"]):
            actions.append("Suivi courant. Aucune action prioritaire.")
            if x["Dont parmi les 10 plus dégradés"] > 0:
                actions.append("Un des 10 tronçons les plus dégradés la traverse.")
        deficits = int(x["O5-01 déficits"])
        lignes.append({
            "Préfecture": p, "Zone": x["Zone"], "Région": x["Région"], POP: int(x[POP]),
            "Réseau — part en mauvais état (%)": x["O3-02"], "Réseau — km évalués": round(x["Km évalués"], 1),
            "Réseau — tronçons critiques": int(x["Tronçons critiques"]), "Réseau — dont parmi les 10 plus dégradés": int(x["Dont parmi les 10 plus dégradés"]),
            "Réseau — km à remettre en état": x["O5-04 km à remettre en état"] if x["Réseau"] else np.nan,
            "Formation — auto-écoles comptées": ce, "Formation — auto-écoles recensées": re_,
            "Formation — distance à la plus proche (km)": x["O4-08"],
            "Formation — auto-écoles à ouvrir": int(x["O5-04 auto-écoles manquantes (écart 21)"]) if x["Formation"] else np.nan,
            "Desserte (km pour 10 000 hab.)": x["O4-03"], "Population rurale": int(x["Population rurale"]),
            "Accès rural à une route revêtue (%)": x["Accès rural à une route revêtue (%)"],
            "Déficits": deficits, "Rang national": x["O5-02 rang"],
            "Leviers": x["Leviers"] or "aucun", "Recommandations": " ; ".join(sorted(par_pref.get(p, []))),
            "Priorité": "Haute" if deficits == 2 else "Moyenne" if deficits == 1 else "Aucune action",
            "Texte réseau": reseau, "Texte formation": formation, "Actions": " ".join(actions), "Note": x["Note"] if pd.notna(x["Note"]) else "",
        })
    f = pd.DataFrame(lignes)
    for col in ("Rang national", "Réseau — km à remettre en état", "Formation — auto-écoles à ouvrir"):
        f[col] = f[col].astype("Float64") if "km" in col else f[col].astype("Int64")
    return f


# --- §6 Cartes ----------------------------------------------------------------------------------------------

TITRES = {
    "REC-Z3": "Agir d’abord dans la Centrale, seule zone en retard sur la route et la formation",
    "REC-R1": "Remettre en état le réseau des 5 préfectures qui cumulent",
    "REC-S1": "Cibler les usagers de deux-roues motorisés",
    "REC-F3": "Faire du permis moto la priorité de la formation",
    "REC-R3": "Remettre en état les 10 tronçons les plus dégradés",
    "REC-Z2": "Ouvrir d’abord des auto-écoles dans les Savanes et la Maritime hors Grand Lomé",
    "REC-R2": "Remettre en état le réseau de 8 autres préfectures",
    "REC-F1": "Ouvrir des auto-écoles dans les 15 préfectures qui n’en ont aucune",
    "REC-Z1": "Remettre en état d’abord le réseau des Plateaux",
    "REC-F2": "Vérifier les auto-écoles non agréées de 8 préfectures",
    "REC-R4": "Vérifier la desserte de Mô",
    "REC-D1": "Créer une base d’accidents par préfecture",
    "REC-D2": "Ouvrir les couches « Dégradations » et « Ponts »",
    "REC-D3": "Publier l’activité des auto-écoles",
    "REC-D4": "Publier un parc en circulation et des libellés exacts",
}
SUIVI_AFFICHAGE = {  # indicateur de suivi en clair (R-18, règle des codes)
    "O3-02": "part des km de routes en mauvais état", "O3-05": "km en mauvais état des tronçons critiques",
    "O4-03": "km de routes classées pour 10 000 habitants", "O4-05": "auto-écoles agréées pour 100 000 habitants",
    "O1-06": "permis délivrés par catégorie", "O1-09": "immatriculations de motos par permis moto",
    "O2-09": "part des deux et trois-roues motorisés parmi les tués", "O4-E1": "accès rural à une route revêtue",
}
RESERVES_AFFICHAGE = {  # réserve en clair (R-18) ; la colonne technique garde ses références
    "REC-R1": "L’état date d’un relevé de 2020, dont la méthode de notation n’est pas publiée.",
    "REC-R2": "La population tient surtout à Agoè-Nyivé, pour peu de km. L’état date d’un relevé de 2020.",
    "REC-R3": "Ces tronçons traversent les préfectures des deux recommandations précédentes. L’état date d’un relevé de 2020.",
    "REC-R4": "Un ordre de grandeur, pas un tracé : la desserte seule ne fonde aucune action d’entretien.",
    "REC-F1": "Vérifier sur place qu’aucune auto-école n’existe ; l’activité des auto-écoles n’est pas publiée.",
    "REC-F2": "Le manque est peut-être administratif ; l’activité des auto-écoles n’est pas publiée.",
    "REC-F3": "Les permis moto ont varié fortement en 2022 et en 2024 : la moyenne en dépend.",
    "REC-S1": "Surreprésentation faible, mesurée sur une seule année (2021, estimation de l’OMS).",
    "REC-Z3": "Km et auto-écoles déjà comptés dans les autres recommandations. L’accès rural est estimé en supposant la population répartie uniformément.",
    "REC-Z1": "Km déjà comptés dans les autres recommandations. L’accès rural est estimé en supposant la population répartie uniformément.",
    "REC-Z2": "Auto-écoles déjà comptées dans les autres recommandations ; leur activité n’est pas publiée. Les Savanes sont un cas limite pour la route.",
}
RESERVE_DONNEES = "Dépend des producteurs de données ; aucun investissement tant que la donnée manque."
NIVEAUX = {"A": "A — mesuré", "B": "B — calculé", "C": "C — estimé", "—": "sans objet (demande de données)"}


def suivi_en_clair(code):
    if code == "Part des territoires renseignés":
        return "Part des préfectures renseignées"
    texte = " ; ".join(SUIVI_AFFICHAGE[m] for m in re.findall(r"O\d-(?:\d{2}|E\d)", code))
    return texte[:1].upper() + texte[1:]


ONGLETS = {"Réseau": "Réseau", "Formation": "Formation", "Sécurité routière": "Sécurité routière",
           "Zones les moins desservies": "Zones les moins desservies", "Données": "Données"}


def textes_doc():
    texte = DOCUMENT.read_text(encoding="utf-8")
    sec = texte.split("### 6.1 Textes des cartes")[1].split("### 6.2")[0]
    cartes = re.findall(r"\*\*Carte (\d+) — (.+?)\*\*\s*\n\s*\n> (.+)", sec)
    return texte, [(int(i), t.strip(), corps.strip()) for i, t, corps in cartes]


def cartes(k, c):
    rang = {p: i for i, p in enumerate(PRIORITES)}
    k = k.assign(_rub=(k["Levier"] == "Données").astype(int), _r=k["Priorité"].map(rang), _o=range(len(k)))
    k = k.sort_values(["_rub", "_r", "Population concernée", "_o"], ascending=[True, True, False, True])
    zones_rec = {i: (" ; ".join(sorted(set(c[c["Préfecture"].isin(p)]["Zone"]))) if p else "National") for i, p in zip(k["ID"], k["_prefs"])}
    _, doc = textes_doc()
    par_titre = {t: corps for _, t, corps in doc}
    lignes = []
    for ordre, (_, x) in enumerate(k.iterrows(), 1):
        nb = len(x["_prefs"])
        lignes.append({"ID": x["ID"], "Ordre": ordre, "Onglet": ONGLETS[x["Levier"]],
                       "Rubrique": "Pour aller plus loin" if x["Levier"] == "Données" else "Recommandations",
                       "Titre": TITRES[x["ID"]], "Cible": x["_phrase"],
                       "Contexte": (f"{nb} préfecture{'s' if nb > 1 else ''} · " if nb else "National · ") + f"{n(x['Population concernée'])} habitants concernés",
                       "Habitants": int(x["Population concernée"]), "Priorité": x["Priorité"], "Nature": x["Nature"], "Horizon": x["_h"],
                       "Zones": zones_rec[x["ID"]], "Acteur": x["Acteur"], "Indicateur de suivi": suivi_en_clair(x["Suivi"]),
                       "Niveau de preuve": NIVEAUX[x["Niveau"]], "Réserve": RESERVES_AFFICHAGE.get(x["ID"], RESERVE_DONNEES),
                       "Texte": par_titre.get(TITRES[x["ID"]], "")})
    return pd.DataFrame(lignes)


# --- §9 Contrôles -------------------------------------------------------------------------------------------

NOMBRE = r"\d{1,3}(?: \d{3})+(?:,\d+)?|\d+(?:,\d+)?"


def verifie_nombres(texte, candidats):
    t = re.sub(r"RN\d+|pour 10{1,2} 000|Carte \d+ — ", " ", texte)
    vals = np.array([float(v) for v in candidats if pd.notna(v)], dtype=float)
    faux, compte = [], 0
    for brut in re.findall(NOMBRE, t):
        compte += 1
        val = float(brut.replace(" ", "").replace(",", "."))
        dec = len(brut.split(",")[1]) if "," in brut else 0
        if not np.any(np.abs(np.round(vals, dec) - val) < 1e-9):
            faux.append(brut)
    return compte, faux


def controles_10(k, f, ca, zt, c, r, z, med, national, a1, route, formation, crit, tete, v, tm, cibles):
    champs = ["Constat", "Ampleur", "Territoire", "Déficit", "Action", "Acteur", "Cible", "Population concernée", "Horizon",
              "Suivi", "Niveau", "Réserve"]
    vides = [f"{x['ID']} {ch}" for _, x in k.iterrows() for ch in champs if pd.isna(x[ch]) or str(x[ch]).strip() == ""]
    leviers = set(k["Levier"])
    controle("10-01", "Recommandations", "15 lignes ; 4 leviers d’action et le ciblage par zone ; les champs de R-18 renseignés",
             f"{len(k)} lignes ; leviers : {', '.join(sorted(leviers))} ; champs vides : {', '.join(vides) or 'aucun'}",
             len(k) == 15 and len(leviers) == 5 and not vides)

    res, form = c[c["Réseau"]], c[c["Formation"]]
    km, ae = "O5-04 km à remettre en état", "O5-04 auto-écoles manquantes (écart 21)"
    r1, r2, f1, f2 = cibles["r1"], cibles["r2"], cibles["f1"], cibles["f2"]
    part_r = set(r1["Préfecture"]).isdisjoint(r2["Préfecture"]) and set(r1["Préfecture"]) | set(r2["Préfecture"]) == set(res["Préfecture"])
    controle("10-02", "Concordance réseau", "REC-R1 + REC-R2 = les 13 préfectures du 08, 304,6 km, 2 868 523 habitants ; chaque préfecture dans une seule des deux",
             f"{len(r1)} + {len(r2)} préfectures ; {n(r1[km].sum(), 1)} + {n(r2[km].sum(), 1)} = {n(r1[km].sum() + r2[km].sum(), 1)} km ; "
             f"{n(r1[POP].sum() + r2[POP].sum())} habitants ; partition : {'oui' if part_r else 'non'}",
             part_r and len(res) == 13 and round(r1[km].sum() + r2[km].sum(), 1) == 304.6 and r1[POP].sum() + r2[POP].sum() == 2868523)
    part_f = set(f1["Préfecture"]).isdisjoint(f2["Préfecture"]) and set(f1["Préfecture"]) | set(f2["Préfecture"]) == set(form["Préfecture"])
    controle("10-03", "Concordance formation", "REC-F1 + REC-F2 = les 23 préfectures du 08, 41 auto-écoles, 2 932 492 habitants ; chaque préfecture dans une seule des deux",
             f"{len(f1)} + {len(f2)} préfectures ; {int(f1[ae].sum())} + {int(f2[ae].sum())} = {int(f1[ae].sum() + f2[ae].sum())} auto-écoles ; "
             f"{n(f1[POP].sum() + f2[POP].sum())} habitants ; partition : {'oui' if part_f else 'non'}",
             part_f and len(form) == 23 and f1[ae].sum() + f2[ae].sum() == 41 and f1[POP].sum() + f2[POP].sum() == 2932492)

    zr = r[r["Maille"] == "Zone"].set_index("Territoire")
    g = f.groupby("Zone").agg(pop=(POP, "sum"), km=("Réseau — km à remettre en état", "sum"), ae=("Formation — auto-écoles à ouvrir", "sum"),
                              nr=("Réseau — km à remettre en état", "count"), nf=("Formation — auto-écoles à ouvrir", "count"))
    cmp = pd.DataFrame({"pop": zr[POP], "km": zr["O5-04 km à remettre en état, préfectures au levier réseau"].fillna(0),
                        "ae": zr["O5-04 auto-écoles manquantes (écart 21), préfectures au levier formation"].fillna(0),
                        "nr": zr["Préfectures au levier réseau"], "nf": zr["Préfectures au levier formation"]})
    ecarts = [f"{zz} {col}" for zz in cmp.index for col in cmp.columns if abs(float(g.at[zz, col]) - float(cmp.at[zz, col])) > 0.05]
    controle("10-04", "Zones", "Les sommes par zone de prefectures_10.csv égalent celles de regions_08.csv (§4.5)",
             f"6 zones × 5 grandeurs comparées ; écarts : {', '.join(ecarts) or 'aucun'}", not ecarts)

    rur_tot = int(tm["population_2022_rurale"].fillna(0).sum())
    parts = c["Part de surface à moins de 2 km"]
    z3, z1, z2 = (k.set_index("ID").at[i, "_prefs"] for i in ("REC-Z3", "REC-Z1", "REC-Z2"))
    pz = {i: set(c[c["Préfecture"].isin(p)]["Zone"]) for i, p in (("Z3", z3), ("Z1", z1), ("Z2", z2))}
    disjoint = pz["Z3"].isdisjoint(pz["Z1"]) and pz["Z3"].isdisjoint(pz["Z2"]) and pz["Z1"].isdisjoint(pz["Z2"])
    attendu = (a1 == {"Savanes", "Maritime hors Grand Lomé"} and route == {"Centrale", "Plateaux"}
               and formation == {"Centrale", "Savanes", "Maritime hors Grand Lomé"})
    controle("10-05", "Zones les moins desservies",
             "Analyse 1 : Savanes et Maritime hors Grand Lomé ; O4-E1 : ruraux = 4 621 706, parts entre 0 et 1, Centrale et Plateaux sous la médiane ; "
             "Z3 = Centrale, Z1 = Plateaux, Z2 = Savanes et Maritime hors Grand Lomé, chaque zone dans une seule",
             f"analyse 1 : {', '.join(sorted(a1))} ; route : {', '.join(sorted(route))} ; formation : {', '.join(sorted(formation))} ; "
             f"ruraux {n(c['Population rurale'].sum())} (table : {n(rur_tot)}) ; parts entre {n(parts.min(), 3)} et {n(parts.max(), 3)} ; "
             f"médiane {n(med['O4-E1'], 2)} %, national {n(national, 2)} % ; zones Z3 {', '.join(sorted(pz['Z3']))}, Z1 {', '.join(sorted(pz['Z1']))}, "
             f"Z2 {', '.join(sorted(pz['Z2']))} ; disjointes : {'oui' if disjoint else 'non'}",
             attendu and c["Population rurale"].sum() == rur_tot and parts.between(0, 1).all() and disjoint
             and pz["Z3"] == {"Centrale"} and pz["Z1"] == {"Plateaux"} and pz["Z2"] == {"Savanes", "Maritime hors Grand Lomé"})

    src = c.set_index("Préfecture")
    ff = f.set_index("Préfecture")
    paires = {POP: POP, "Réseau — part en mauvais état (%)": "O3-02", "Formation — auto-écoles comptées": "Auto-écoles comptées",
              "Formation — distance à la plus proche (km)": "O4-08", "Desserte (km pour 10 000 hab.)": "O4-03", "Déficits": "O5-01 déficits",
              "Rang national": "O5-02 rang"}
    diff = [f"{p} {a}" for a, b in paires.items() for p in ff.index
            if not (pd.isna(ff.at[p, a]) and pd.isna(src.at[p, b])) and (pd.isna(ff.at[p, a]) or pd.isna(src.at[p, b]) or abs(float(ff.at[p, a]) - float(src.at[p, b])) > 1e-9)]
    prio = f["Priorité"].value_counts().to_dict()
    controle("10-06", "Préfectures", "39 lignes ; 6 zones et 5 régions ; valeurs identiques à leur source ou recalculées ; 5 Haute, 26 Moyenne, 8 sans action",
             f"{len(f)} lignes ; {f['Zone'].nunique()} zones, {f['Région'].nunique()} régions ; {len(paires) * len(f)} valeurs comparées à classement_08.csv, "
             f"différences : {len(diff)} ; priorités : {', '.join(f'{a} {b}' for a, b in prio.items())}",
             len(f) == 39 and f["Zone"].nunique() == 6 and f["Région"].nunique() == 5 and not diff
             and prio == {"Moyenne": 26, "Haute": 5, "Aucune action": 8})

    nat = v[(v["ID"] == "O3-05") & (v["Maille"] == "National")].set_index("Mesure")["Valeur"]
    controle("10-07", "Tronçons", "49 tronçons critiques et 669,34 km, recomptés depuis le relevé, égaux au 07 ; les 10 premiers et leurs préfectures",
             f"{len(crit)} tronçons (07 : {int(nat['nombre de tronçons'])}) ; {n(crit['km_mauvais'].sum(), 2)} km (07 : {n(nat['km en mauvais état'], 2)}) ; "
             f"10 premiers : {n(tete['km_mauvais'].sum(), 1)} km en mauvais état, {len(set(tete['Préfectures'].sum()))} préfectures",
             len(crit) == nat["nombre de tronçons"] and abs(crit["km_mauvais"].sum() - nat["km en mauvais état"]) < 0.01)

    texte, doc = textes_doc()
    app = texte.split("**Application :**")[1].split("###")[0]
    plan = {p: set(re.findall(r"REC-[A-Z]\d", l)) for l in app.splitlines() for p in PRIORITES if l.startswith(f"| {p} |")}
    calc = {p: set(k[k["Priorité"] == p]["ID"]) for p in PRIORITES}
    controle("10-08", "Priorités", "Chaque priorité suit la règle du §5.1, recalculée ; égale au tableau du plan ; « Haute » seulement pour le cumul ou la base d’accidents",
             " ; ".join(f"{p} : {', '.join(sorted(calc[p]))}" for p in PRIORITES) + f" ; plan identique : {'oui' if plan == calc else 'non'}",
             plan == calc and set(k[k["Priorité"] == "Haute"]["_attr"]) <= {"cumul", "condition"})

    cond = k[k["Niveau"] == "C"]
    mal = [i for i, x in cond.set_index("ID").iterrows() if x["Nature"] != "Conditionnelle" or not x["Action"].startswith("Vérifier")]
    controle("10-09", "R-17", "Chaque recommandation en C est « conditionnelle », et son action commence par une vérification",
             f"{len(cond)} recommandations en C ; écarts : {', '.join(mal) or 'aucun'}", not mal)

    appuis = [f"{x['ID']}" for _, x in k.iterrows() if re.search(INTERDITS, " ".join(str(x[ch]) for ch in ("Constat", "Action", "Cible", "Source")))]
    appuis = [a for a in appuis if a != "REC-R3" or re.search(INTERDITS, " ".join(str(k.set_index("ID").at[a, ch]) for ch in ("Constat", "Action", "Cible", "Source")))]
    controle("10-10", "Hypothèses et compléments", "Aucune recommandation ne s’appuie sur une hypothèse non testable, sur H5 ou H6, ni sur O2-E1 à O2-E3",
             f"recommandations concernées : {', '.join(appuis) or 'aucune'}", not appuis)

    ordre_doc = [t for _, t, _ in sorted(doc)]
    ordre_calc = list(ca.sort_values("Ordre")["Titre"])
    nb, faux = 0, []
    cand = k.set_index("ID")["_n"]
    for i, t, corps in doc:
        ident = next((a for a, b in TITRES.items() if b == t), None)
        if ident is None:
            faux.append(f"carte {i} : titre inconnu")
            continue
        compte, err = verifie_nombres(t + " " + corps, list(cand[ident]) + [BANDE_KM, EN_TETE])
        nb += compte
        faux += [f"carte {i} : {e}" for e in err]
    tab = texte.split("**Les 15 cartes**")[1].split("### 6.1")[0]
    lignes_tab = [[x.strip() for x in l.strip("|").split("|")] for l in tab.splitlines() if re.match(r"^\| \d+ \|", l)]
    ca_t = ca.set_index("Titre")
    tab_err = [f"ligne {l[0]}" for l in lignes_tab if l[1] not in ca_t.index or
               (l[3].replace(" ", ""), l[4], l[5], l[6]) != (str(ca_t.at[l[1], "Habitants"]), ca_t.at[l[1], "Priorité"], ca_t.at[l[1], "Nature"], ca_t.at[l[1], "Horizon"])
               or int(l[0]) != ca_t.at[l[1], "Ordre"]]
    codes = [f"carte {i}" for i, t, corps in doc if re.search(CODES, t + " " + corps)]
    controle("10-11", "Cartes et fiches", "15 cartes et 39 fiches ; chaque nombre des cartes vaut, à son arrondi, une valeur calculée ; "
             "ordre, habitants, priorité, nature et horizon du tableau du §6 égaux au calcul ; aucun code interne",
             f"{len(doc)} cartes, {len(f)} fiches ; {nb} nombres vérifiés, écarts : {', '.join(faux) or 'aucun'} ; ordre identique : "
             f"{'oui' if ordre_doc == ordre_calc else 'non'} ; tableau du §6 : {len(lignes_tab)} lignes, écarts : {', '.join(tab_err) or 'aucun'} ; "
             f"codes : {', '.join(codes) or 'aucun'}",
             len(doc) == 15 and len(f) == 39 and not faux and ordre_doc == ordre_calc and len(lignes_tab) == 15 and not tab_err and not codes
             and (ca["Texte"] != "").all())

    multi_r = (c["Préfecture"].map(lambda p: int(p in set(r1["Préfecture"])) + int(p in set(r2["Préfecture"]))) > 1).sum()
    multi_f = (c["Préfecture"].map(lambda p: int(p in set(f1["Préfecture"])) + int(p in set(f2["Préfecture"]))) > 1).sum()
    zkm = sum(c[c["Préfecture"].isin(k.set_index("ID").at[i, "_prefs"]) & c["Réseau"]][km].sum() for i in ("REC-Z3", "REC-Z1"))
    zae = sum(c[c["Préfecture"].isin(k.set_index("ID").at[i, "_prefs"]) & c["Formation"]][ae].sum() for i in ("REC-Z3", "REC-Z2"))
    controle("10-12", "Pas de double compte", "Dans chaque levier, une préfecture n’apparaît qu’une fois ; les quantités des recommandations de zone sont incluses dans celles des leviers",
             f"préfectures en double : réseau {multi_r}, formation {multi_f} ; zones : {n(zkm, 1)} km sur {n(res[km].sum(), 1)}, {int(zae)} auto-écoles sur {int(form[ae].sum())}",
             multi_r == 0 and multi_f == 0 and zkm <= res[km].sum() + 1e-9 and zae <= form[ae].sum())

    textes = pd.concat([f["Texte réseau"], f["Texte formation"], f["Actions"], ca["Texte"], ca["Cible"], ca["Contexte"], ca["Acteur"],
                        ca["Indicateur de suivi"], ca["Réserve"]])
    mauvais = [t for t in textes if re.search(r"\b\d+ tronçon critique|\b[2-9]\d* \w+ critique\b|^[a-zé]", t) or re.search(r"\bNone\b|\bnan\b|\bNaN\b|<NA>|(?<![\d,])0 km évalués|(?<![\d,])0,0 %", t) or re.search(CODES, t)
               or not t.rstrip().endswith((".", "»")) and t in set(f["Texte réseau"]) | set(f["Texte formation"]) | set(f["Actions"])]
    controle("10-13", "Style des fiches et des cartes", "Phrases complètes ; aucun code interne ; aucun « None », « nan » ni « 0 » à la place d’une valeur manquante",
             f"{len(textes)} textes relus ; défauts : {len(mauvais)}" + (f" ({mauvais[0]})" if mauvais else ""), not mauvais)


def controle_zones(zt, r, c):
    """Contrôle 10-14 : zones_10.csv redonne les valeurs du 08 et les totaux du pays."""
    zr = r[r["Maille"] == "Zone"].set_index("Territoire")
    zz = zt[zt["Maille"] == "Zone"].set_index("Zone")
    pays = zt[zt["Maille"] == "Pays"].iloc[0]
    etats = ["Km en bon état", "Km en état moyen", "Km en mauvais état", "Km en travaux"]
    ecarts = []
    for k in zr.index:
        evalues = zz.loc[k, etats].sum()
        for nom, a, b, tol in ((POP, zz.at[k, POP], zr.at[k, POP], 0), ("O3-02", zz.at[k, "Part en mauvais état (%)"], zr.at[k, "O3-02"], 0),
                               ("O4-05", zz.at[k, "Auto-écoles pour 100 000 hab."], zr.at[k, "O4-05"], 0),
                               ("O4-03", zz.at[k, "Desserte (km pour 10 000 hab.)"], zr.at[k, "O4-03"], 0),
                               ("km en mauvais état", zz.at[k, "Km en mauvais état"], zr.at[k, "Km en mauvais état"], 0.06),
                               ("km évalués", evalues, zr.at[k, "Km évalués"], 0.25)):
            if abs(float(a) - float(b)) > tol + 1e-9:
                ecarts.append(f"{k} {nom}")
    rur = int(zz["Population rurale"].sum())
    loin = int(zz["Ruraux à plus de 2 km d’une route revêtue"].sum())
    ok_pays = (int(pays[POP]) == int(c[POP].sum()) and int(pays["Population rurale"]) == rur
               and abs(int(pays["Ruraux à plus de 2 km d’une route revêtue"]) - loin) <= 3)
    controle("10-14", "Table des zones", "zones_10.csv : 6 zones ; population, part en mauvais état, auto-écoles et desserte égales à regions_08.csv ; "
             "km par état cohérents avec les km évalués ; ligne du pays égale à la somme des zones",
             f"{len(zz)} zones ; écarts avec le 08 : {', '.join(ecarts) or 'aucun'} ; pays : {n(int(pays[POP]))} habitants, "
             f"{n(int(pays['Population rurale']))} ruraux (somme des zones {n(rur)}), {n(int(pays['Ruraux à plus de 2 km d’une route revêtue']))} ruraux à plus de 2 km "
             f"(somme des zones {n(loin)})", len(zz) == 6 and not ecarts and ok_pays)


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    v, c, r, h, tr, tm, age = lire()
    crit, tete = troncons(tr, c)
    acces_rural(tm, c)
    z, med, national, a1, route, formation = zones(c, r)
    k, cibles = recommandations(v, c, r, h, crit, tete, age, z, med, national, route, formation)
    f = fiches(c, k, cibles)
    ca = cartes(k, c)
    zt = table_zones(z, c, med, national, a1, route, formation, v)
    controles_10(k, f, ca, zt, c, r, z, med, national, a1, route, formation, crit, tete, v, tm, cibles)
    controle_zones(zt, r, c)

    colonnes = ["ID", "Levier", "Sous-levier", "Priorité", "Nature", "Constat", "Ampleur", "Territoire", "Déficit", "Action", "Acteur",
                "Cible", "Population concernée", "Horizon", "Suivi", "Niveau", "Réserve", "Source"]
    sortie = k[colonnes].rename(columns={"Suivi": "Indicateur de suivi", "Niveau": "Niveau de preuve"})
    sortie["Carte"] = sortie["ID"].map(ca.set_index("ID")["Ordre"]).map(lambda i: f"§6.1, carte {i}")
    sortie.to_csv(SORTIE / "recommandations_10.csv", index=False)
    f.to_csv(SORTIE / "prefectures_10.csv", index=False)
    zt.to_csv(SORTIE / "zones_10.csv", index=False)
    ca.to_csv(SORTIE / "cartes_10.csv", index=False)
    kk = pd.DataFrame(controles)
    kk.to_csv(SORTIE / "controles_10.csv", index=False)

    pd.set_option("display.max_colwidth", 220)
    pd.set_option("display.width", 300)
    zz = z.assign(**{"O4-E1": z["O4-E1"].round(2)})[[POP, "Population rurale", "Ruraux plus loin", "O4-E1", "O4-03", "O4-05", "O3-02"]]
    print(zz.to_string())
    print(f"médianes : O4-03 {med['O4-03']:.3f}, O4-05 {med['O4-05']:.3f}, O4-E1 {med['O4-E1']:.2f} ; national O4-E1 {national:.2f}")
    print(ca[["Ordre", "ID", "Priorité", "Nature", "Habitants", "Horizon", "Titre"]].to_string(index=False))
    print(f"contrôles : {int((kk['Résultat'] == CONFORME).sum())} conformes sur {len(kk)}")
    print(kk[["ID", "Contrôle", "Mesure", "Résultat"]].to_string(index=False))


if __name__ == "__main__":
    main()
