"""Étape 08 : priorisation (08_priorisation.md).

Lit les indicateurs du 07 (indicateurs_07.csv), les seuils du 02 (03_Seuils.csv), le repère de l'OMS (D9) et le
référentiel des préfectures. N'écrit rien dans data/processed/ ni dans data/analysis/07_indicateurs/.
Calcule chaque chiffre cité dans le 08 (R-19) :
- les seuils de classement applicables (§3) ;
- le nombre de déficits (O5-01) et le rang de priorité (O5-02), sans la dimension risque (§4) ;
- les leviers de chaque préfecture et l'ordre dans chaque levier (§5) ;
- la lecture par zone, par région et pour le pays, avec SE-03 (§6) ;
- les tests de sensibilité et la stabilité (§7, écarts 23 à 25) ;
- les contrôles du §9.

Risque « non déterminable » partout (P5) : ni P1, ni P2, ni P3, ni P4, ni P6 (07 §9). Les 3 compléments de l'écart 22
ne sont pas lus. Aucune recommandation (10), aucune lecture causale (09).

Sorties, dans data/analysis/08_priorisation/ : classement_08.csv, regions_08.csv, sensibilite_08.csv, controles_08.csv.

Usage : .venv/bin/python scripts/priorisation_08.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
INDICATEURS = RACINE / "data" / "analysis" / "07_indicateurs" / "indicateurs_07.csv"
SEUILS = RACINE / "02_decision_matrix" / "03_Seuils.csv"
REFERENCE = RACINE / "data" / "reference"
TRAITE = RACINE / "data" / "processed"
EXPLORATION = RACINE / "data" / "analysis" / "06_exploration"
SORTIE = RACINE / "data" / "analysis" / "08_priorisation"

ZONES = ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]
REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]
GRAND_LOME = ["Golfe", "Agoè-Nyivé"]
TERCILE_SUP, TERCILE_INF = 2 / 3, 1 / 3  # 02 : tercile supérieur (66,7e percentile), tercile inférieur
EN_TETE = 10  # 05_Priorisation, « Territoires en tête »
CHANGEMENTS_TOLERES = 2  # 05_Priorisation, « Stabilité »
VOISINS = ["BEN", "GHA", "BFA"]  # SE-03 : moyenne du Bénin, du Ghana et du Burkina Faso
LUS = ["O2-02", "O3-02", "O3-06", "O4-03", "O4-05", "O4-07", "O4-08", "O5-03", "O5-04"]
COMPLEMENTS = ["O2-E1", "O2-E2", "O2-E3"]  # écart 22 : hors classement, jamais lus
PROFIL = "P5 (risque non déterminable)"
NIVEAU = "C"  # O3-02 et O4-05 sont en C (R-17) : vérification avant investissement
CONFORME, ECHEC = "conforme", "échec"

controles = []


def exiger(condition, message):
    if not condition:
        raise ValueError(message)


def n(x, decimales=0):
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def quotient(num, den, facteur, decimales):
    """Rapport arrondi ; non défini (NaN) si le dénominateur est nul (R-10)."""
    return np.nan if pd.isna(den) or den == 0 else round(num / den * facteur, decimales)


def seuil(ident):
    """Valeur numérique d'un seuil du 02 (03_Seuils.csv), lue et non recopiée."""
    s = pd.read_csv(SEUILS).set_index("ID").at[ident, "Valeur ou règle"]
    return float(re.search(r"\d+(?:[.,]\d+)?", s).group().replace(",", "."))


def percentile(s, q):
    """Percentile par interpolation linéaire, comme au 06 ; valeurs non définies ignorées."""
    return round(float(s.quantile(q)), 4)


def classer(d, termes, poids, rang_percentile=True):
    """Score = Σ poids × terme ; le terme est le rang percentile (ex aequo : rang moyen) ou la valeur normalisée.
    Chaque terme est orienté : plus haut = plus prioritaire. Rang 1 = score le plus élevé ; à score égal, la plus
    peuplée passe devant (« Intensité et volume »)."""
    r = pd.DataFrame(index=d.index)
    for nom, s in termes.items():
        r[nom] = s.rank(method="average", pct=True).round(6) if rang_percentile else s.round(6)
    r["Score"] = sum(w * r[nom] for nom, w in zip(termes, poids)).round(6)
    ordre = (r.assign(_pop=d["Population"], _nom=d.index)
             .sort_values(["Score", "_pop", "_nom"], ascending=[False, False, True]).index)
    r["Rang"] = pd.Series(range(1, len(r) + 1), index=ordre)
    return r


def controle(ident, intitule, attendu, mesure, ok):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC})


# --- Préfectures : valeurs du 07 ---------------------------------------------------------------------

def prefectures(v):
    ref = (pd.read_csv(REFERENCE / "referentiel_prefectures.csv").drop_duplicates("Préfecture")
           .set_index("Préfecture")[["Zone", "Région"]])
    pr = v[v["Maille"] == "Préfecture"]

    def col(ind, cat="", mes="", champ="Valeur"):
        s = pr[(pr["ID"] == ind) & pr["Catégorie"].fillna("").str.startswith(cat) & pr["Mesure"].fillna("").str.startswith(mes)]
        exiger(s["Territoire"].is_unique, f"{ind} {cat} {mes} : une ligne par préfecture attendue")
        return s.set_index("Territoire")[champ]

    p = ref.copy()
    p["Population"] = col("O5-03").astype(int)
    p["O3-02"] = col("O3-02")
    p["Km en mauvais état"], p["Km évalués"] = col("O3-02", champ="Numérateur"), col("O3-02", champ="Dénominateur")
    p["O3-06"] = col("O3-06")
    p["Km non évalués"], p["Km de routes nationales"] = col("O3-06", champ="Numérateur"), col("O3-06", champ="Dénominateur")
    p["O4-03"] = col("O4-03")
    p["Km de routes classées"] = col("O4-03", champ="Numérateur")
    p["O4-05"] = col("O4-05")
    p["Auto-écoles comptées"] = col("O4-05", champ="Numérateur").astype(int)
    p["O4-08"] = col("O4-08", mes="distance")
    p["Population au-delà de SE-08"] = col("O4-08", mes="population").astype(int)
    p["O5-04 km à remettre en état"] = col("O5-04", mes="km à remettre") + 0.0  # « -0,0 » du 07 écrit 0,0
    p["O5-04 auto-écoles manquantes (écart 21)"] = col("O5-04", cat="cible de l’écart 21", mes="auto-écoles manquantes")
    p["Nature du zéro"] = pr[pr["ID"] == "O4-07"].set_index("Territoire")["Note"]
    exiger(len(p) == 39 and p["Population"].notna().all(), "39 préfectures attendues")
    return p.sort_index()


# --- §3 Seuils ; §4 déficits et rang ; §5 leviers ----------------------------------------------------

def appliquer_seuils(p, se05):
    s = {"SE-04": percentile(p["O3-02"], TERCILE_SUP), "SE-06": percentile(p["O4-03"], TERCILE_INF),
         "SE-07": percentile(p["O4-05"], TERCILE_INF), "SE-05": se05}
    p["Réseau dégradé (SE-04)"] = p["O3-02"] >= s["SE-04"]
    p["Réseau non déterminable (SE-05)"] = p["O3-06"] > se05
    p["Desserte faible (SE-06)"] = p["O4-03"] <= s["SE-06"]
    p["Formation faible (SE-07)"] = p["O4-05"] <= s["SE-07"]
    reseau = p["O3-02"].notna() & ~p["Réseau non déterminable (SE-05)"]
    p["Classée"] = reseau & p["O4-05"].notna()
    p["Dimensions mesurées"] = reseau.astype(int) + p["O4-05"].notna().astype(int)
    p["O5-01 déficits"] = (p["Réseau dégradé (SE-04)"] & reseau).astype(int) + p["Formation faible (SE-07)"].astype(int)
    return s


def termes(c, formation="O4-05"):
    """Dimensions orientées : plus haut = plus prioritaire."""
    return {"réseau": c["O3-02"], "formation": -c["O4-05"] if formation == "O4-05" else c["O4-08"]}


def leviers(p, t0):
    p["Rang percentile réseau"] = t0["réseau"]
    p["Rang percentile formation"] = t0["formation"]
    p["Score"] = t0["Score"]
    p["O5-02 rang"] = t0["Rang"].astype("Int64")
    p[f"Parmi les {EN_TETE} premières"] = p["O5-02 rang"] <= EN_TETE
    p["Profil du 02"] = PROFIL
    liste = []
    for pref, r in p.iterrows():
        lv = []
        if r["Réseau dégradé (SE-04)"]:
            lv.append(("réseau", r["Rang percentile réseau"]))
        if r["Formation faible (SE-07)"]:
            lv.append(("formation", r["Rang percentile formation"]))
        lv.sort(key=lambda x: -x[1] if pd.notna(x[1]) else 0)  # déficit au rang percentile le plus élevé en premier
        liste.append(" ; ".join(nom for nom, _ in lv))
    p["Leviers"] = liste
    for nom, col, croissant in (("réseau", "Réseau dégradé (SE-04)", False), ("formation", "Formation faible (SE-07)", True)):
        dim = "O3-02" if nom == "réseau" else "O4-05"
        r = p[p[col]].assign(_nom=lambda d: d.index).sort_values([dim, "Population", "_nom"], ascending=[croissant, False, True])
        p[f"Rang dans le levier {nom}"] = pd.Series(range(1, len(r) + 1), index=r.index).astype("Int64")
    p["Niveau"] = NIVEAU
    notes = []
    for pref, r in p.iterrows():
        nt = []
        if not r["Classée"]:
            nt.append("non classée : aucune route classée, O3-02 non défini (vrai vide du 05) ; réseau non défini, sans P5"
                      if r["Km de routes nationales"] == 0 else "non classée : dimension réseau non déterminable (SE-05)")
        if pd.notna(r["Nature du zéro"]):
            nt.append(r["Nature du zéro"])
        notes.append(" ; ".join(nt))
    p["Note"] = notes


# --- §6 Lecture par région ---------------------------------------------------------------------------

def regions(p, v, d9):
    lignes = []
    groupes = [("Zone", z) for z in ZONES] + [("Région", r) for r in REGIONS] + [("Pays", "Togo")]
    for maille, nom in groupes:
        s = p if maille == "Pays" else p[p[maille] == nom]
        lignes.append({
            "Maille": maille, "Territoire": nom, "Préfectures": len(s), "Population": int(s["Population"].sum()),
            "O3-02": quotient(s["Km en mauvais état"].sum(), s["Km évalués"].sum(), 100, 1),
            "Km en mauvais état": round(s["Km en mauvais état"].sum(), 3), "Km évalués": round(s["Km évalués"].sum(), 3),
            "O3-06": quotient(s["Km non évalués"].sum(), s["Km de routes nationales"].sum(), 100, 1),
            "O4-03": quotient(s["Km de routes classées"].sum(), s["Population"].sum(), 1e4, 2),
            "Km de routes classées": round(s["Km de routes classées"].sum(), 3),
            "O4-05": quotient(s["Auto-écoles comptées"].sum(), s["Population"].sum(), 1e5, 2),
            "Auto-écoles comptées": int(s["Auto-écoles comptées"].sum()),
            "Préfectures au levier réseau": int(s["Réseau dégradé (SE-04)"].sum()),
            "Préfectures au levier formation": int(s["Formation faible (SE-07)"].sum()),
            "Population des préfectures au levier réseau": int(s.loc[s["Réseau dégradé (SE-04)"], "Population"].sum()),
            "Population des préfectures au levier formation": int(s.loc[s["Formation faible (SE-07)"], "Population"].sum()),
            # écarts à la cible (O5-04) des seules préfectures qui reçoivent le levier ; positifs, sans compensation
            "O5-04 km à remettre en état, préfectures au levier réseau":
                round(s.loc[s["Réseau dégradé (SE-04)"], "O5-04 km à remettre en état"].clip(lower=0).sum(), 1),
            "O5-04 auto-écoles manquantes (écart 21), préfectures au levier formation":
                int(s.loc[s["Formation faible (SE-07)"], "O5-04 auto-écoles manquantes (écart 21)"].clip(lower=0).sum()),
        })
    r = pd.DataFrame(lignes)
    for maille, effectif in (("Zone", 6), ("Région", 5)):
        m = r["Maille"] == maille
        d = r[m].set_index("Territoire")
        med = d[["O3-02", "O4-05", "O4-03"]].median()
        r.loc[m, "Réseau dégradé (au-dessus de la médiane)"] = (d["O3-02"] > med["O3-02"]).to_numpy()
        r.loc[m, "Formation faible (sous la médiane)"] = (d["O4-05"] < med["O4-05"]).to_numpy()
        r.loc[m, "Desserte faible (sous la médiane)"] = (d["O4-03"] < med["O4-03"]).to_numpy()
        t = classer(d, termes(d), (1, 1))
        r.loc[m, "Rang percentile réseau"] = t["réseau"].to_numpy()
        r.loc[m, "Rang percentile formation"] = t["formation"].to_numpy()
        r.loc[m, "Score"] = t["Score"].to_numpy()
        r.loc[m, "Rang"] = t["Rang"].to_numpy()
        r.loc[m, "Note"] = (f"seuils : médiane des {effectif} {maille.lower()}s (SE-04, SE-06, SE-07) ; rang sur les "
                            f"{effectif}, présentés sans coupure ; Mô comptée dans la Centrale")
    r["Rang"] = r["Rang"].astype("Int64")
    # SE-03 : taux national de tués de 2021 face au repère de l'OMS (D9), sur la ligne du pays
    o202 = v[(v["ID"] == "O2-02") & (v["Année"].astype(str) == "2021")]["Valeur"].iloc[0]
    oms = d9[d9["Indicateur"] == "Tués estimés pour 100 000 habitants"].set_index("Pays")["Valeur"]
    pays = r["Maille"] == "Pays"
    r.loc[pays, "SE-03 O2-02 de 2021 (tués déclarés)"] = o202
    r.loc[pays, "SE-03 repère OMS Togo 2021"] = oms["TGO"]
    r.loc[pays, "SE-03 repère OMS moyenne Bénin, Ghana, Burkina Faso 2021"] = round(oms[VOISINS].mean(), 2)
    def position(repere, nom):
        return f"sous {nom}" if o202 < repere else f"au niveau ou au-dessus de {nom}"
    r.loc[pays, "SE-03 position"] = (f"{position(oms['TGO'], 'l’estimation de l’OMS pour le Togo')} ; "
                                     f"{position(oms[VOISINS].mean(), 'la moyenne des voisins')}")
    r.loc[pays, "Note"] = "totaux du pays (R-04) ; SE-03 ne déclenche aucun profil ; l’estimation de l’OMS n’est jamais une correction des tués déclarés (D9)"
    r["Niveau"] = NIVEAU
    return r


# --- §7 Sensibilité ----------------------------------------------------------------------------------

def sensibilite(p, c):
    med_r = percentile(c["O3-02"], 0.5)
    med_21 = percentile(p.loc[p["Auto-écoles comptées"] >= 1, "O4-05"], 0.5)  # médiane de l'écart 21
    tests = {
        "T0": ("Principal : poids égaux, rang percentile", classer(c, termes(c), (1, 1))),
        "T1": ("Pondérations : réseau 2/3, formation 1/3 (écart 23)", classer(c, termes(c), (2 / 3, 1 / 3))),
        "T2": ("Pondérations : réseau 1/3, formation 2/3 (écart 23)", classer(c, termes(c), (1 / 3, 2 / 3))),
        "T3": (f"Normalisation : écart à la médiane, en part de la médiane ; médianes {n(med_r, 2)} % (O3-02) "
               f"et {n(med_21, 3)} (O4-05, écart 21) (écart 24)",
               classer(c, {"réseau": (c["O3-02"] - med_r) / med_r, "formation": (med_21 - c["O4-05"]) / med_21}, (1, 1),
                       rang_percentile=False)),
        "T4": ("Point extrême : sans Golfe ni Agoè-Nyivé", classer(c.drop(GRAND_LOME), termes(c.drop(GRAND_LOME)), (1, 1))),
        "T5": ("Mesure de la formation : distance O4-08 au lieu de O4-05 (écart 25)",
               classer(c, termes(c, formation="O4-08"), (1, 1))),
    }
    t0 = tests["T0"][1]
    tete0 = set(t0.index[t0["Rang"] <= EN_TETE])
    gl_en_tete = sorted(set(GRAND_LOME) & tete0)
    lignes, synthese = [], {}
    for t, (desc, r) in tests.items():
        tete = set(r.index[r["Rang"] <= EN_TETE])
        ref = set(t0.drop(GRAND_LOME).sort_values("Rang").index[:EN_TETE]) if t == "T4" else tete0
        entrees, sorties = sorted(tete - ref), sorted(ref - tete)
        synthese[t] = (len(entrees), entrees, sorties)
        for pref, x in r.sort_values("Rang").iterrows():
            lignes.append({"Test": t, "Description": desc, "Préfecture": pref, "Score": x["Score"], "Rang": int(x["Rang"]),
                           f"Parmi les {EN_TETE} premières": x["Rang"] <= EN_TETE})
        note = ""
        if t == "T4":
            note = (f"comparé au classement T0 sans le Grand Lomé ; Grand Lomé parmi les {EN_TETE} premières de T0 : "
                    f"{', '.join(gl_en_tete) or 'aucune'}")
        lignes.append({"Test": t, "Description": desc, "Préfecture": "", "Préfectures classées": len(r),
                       f"Changements parmi les {EN_TETE} premières": len(entrees), "Entrées": ", ".join(entrees),
                       "Sorties": ", ".join(sorties), "Stable": len(entrees) <= CHANGEMENTS_TOLERES, "Note": note})
    s = pd.DataFrame(lignes)
    detail = s[s["Préfecture"] != ""]
    presence = detail[detail[f"Parmi les {EN_TETE} premières"] == True].groupby("Préfecture").size()  # noqa: E712
    p[f"Tests parmi les {EN_TETE} premières (sur 6)"] = presence.reindex(p.index).fillna(0).astype(int).where(p["Classée"]).astype("Int64")
    return s, synthese, tests, (med_r, med_21)


# --- §9 Contrôles ------------------------------------------------------------------------------------

def controles_08(p, v, r, s, synthese, tests, seuils, ids_lus):
    c = p[p["Classée"]]
    a_part = p[~p["Classée"]]
    controle("9-01", "Préfectures", "39 lignes ; 38 classées ; Mô à part, avec sa cause",
             f"{len(p)} lignes ; {len(c)} classées ; à part : " + "; ".join(f"{k} ({a_part.at[k, 'Note'].split(' ; ')[0]})" for k in a_part.index),
             len(p) == 39 and len(c) == 38 and list(a_part.index) == ["Mô"])

    f07 = p["Formation faible (SE-07)"]
    pays = r[r["Maille"] == "Pays"].iloc[0]
    controle("9-02", "Seuils", "Valeur de chaque percentile ; nombre de préfectures par seuil ; SE-07 : les 23 à 0 ; SE-03 sur la "
             "ligne du pays ; SE-02, SE-09, SE-10 non applicables",
             f"SE-04 : O3-02 ≥ {n(seuils['SE-04'], 2)} % → {int(p['Réseau dégradé (SE-04)'].sum())} préfectures (sur "
             f"{int(p['O3-02'].notna().sum())}) ; SE-05 : O3-06 > {n(seuils['SE-05'])} % → {int(p['Réseau non déterminable (SE-05)'].sum())} ; "
             f"SE-06 : O4-03 ≤ {n(seuils['SE-06'], 2)} → {int(p['Desserte faible (SE-06)'].sum())} ; SE-07 : O4-05 ≤ {n(seuils['SE-07'], 2)} → "
             f"{int(f07.sum())} (à 0 : {int((p['O4-05'] == 0).sum())}) ; SE-03 : {n(pays['SE-03 O2-02 de 2021 (tués déclarés)'], 2)} "
             f"face à {n(pays['SE-03 repère OMS Togo 2021'], 1)} et {n(pays['SE-03 repère OMS moyenne Bénin, Ghana, Burkina Faso 2021'], 2)} ; "
             "SE-02 : O2-02 national (écart 1) ; SE-09 : O2-08 non calculable ; SE-10 : cumul complet sans le risque impossible",
             seuils["SE-07"] == 0 and (f07 == (p["O4-05"] == 0)).all() and pd.notna(pays["SE-03 position"]))

    pr = v[v["Maille"] == "Préfecture"]
    paires = {"O3-02": ("O3-02", ""), "O4-05": ("O4-05", ""), "O4-03": ("O4-03", ""), "O4-08": ("O4-08", "distance"),
              "Population": ("O5-03", "")}
    ecarts = []
    for col, (ind, mes) in paires.items():
        s07 = pr[(pr["ID"] == ind) & pr["Mesure"].fillna("").str.startswith(mes)].set_index("Territoire")["Valeur"]
        x, y = p[col].astype(float), s07.reindex(p.index).astype(float)
        ecarts += [f"{col} {k}" for k in p.index[~(((x - y).abs() < 1e-9) | (x.isna() & y.isna()))]]
    controle("9-03", "Concordance avec le 07", "O3-02, O4-05, O4-03, O4-08 et O5-03 égaux à indicateurs_07.csv",
             f"{len(paires) * len(p)} valeurs comparées ; différences : {len(ecarts)}" + (" ; " + ", ".join(ecarts[:10]) if ecarts else ""),
             not ecarts)

    somme = (c["Réseau dégradé (SE-04)"].astype(int) + c["Formation faible (SE-07)"].astype(int))
    controle("9-04", "O5-01", "Entre 0 et 2 ; égal à la somme des seuils franchis",
             f"répartition : " + ", ".join(f"{k} déficit(s) : {int(x)}" for k, x in p["O5-01 déficits"].value_counts().sort_index().items()),
             p["O5-01 déficits"].between(0, 2).all() and (c["O5-01 déficits"] == somme).all())

    o = c.sort_values("O5-02 rang")
    egaux = o["Score"].diff().fillna(-1) == 0
    pop_ok = ((o["Population"].diff() <= 0) | ~egaux).all()
    controle("9-05", "O5-02", "Rangs de 1 à 38, sans trou ; scores décroissants ; ex aequo départagés par la population",
             f"rangs : {int(o['O5-02 rang'].min())} à {int(o['O5-02 rang'].max())} ; scores décroissants : "
             f"{'oui' if (o['Score'].diff().fillna(0) <= 0).all() else 'non'} ; scores ex aequo : {int(egaux.sum())} ; "
             f"départagés par la population : {'oui' if pop_ok else 'non'}",
             list(o["O5-02 rang"]) == list(range(1, 39)) and (o["Score"].diff().fillna(0) <= 0).all() and pop_ok)

    attendu = p.apply(lambda x: {nom for nom, col in (("réseau", "Réseau dégradé (SE-04)"), ("formation", "Formation faible (SE-07)")) if x[col]}, axis=1)
    obtenu = p["Leviers"].map(lambda x: set(filter(None, x.split(" ; "))))
    autres = p["Profil du 02"].str.contains(r"P[1-46]").sum() + p["Leviers"].str.contains(r"P\d").sum()
    controle("9-06", "Leviers", "Un levier pour chaque seuil franchi, et aucun autre ; P5 pour le risque partout ; ni P1, P2, P3, P4, P6",
             f"levier réseau : {int(p['Réseau dégradé (SE-04)'].sum())} ; levier formation : {int(p['Formation faible (SE-07)'].sum())} ; "
             f"les deux : {int((p['Réseau dégradé (SE-04)'] & p['Formation faible (SE-07)']).sum())} ; aucun : {int((p['Leviers'] == '').sum())} ; "
             f"leviers conformes aux seuils : {int((attendu == obtenu).sum())} sur {len(p)} ; P5 partout : "
             f"{'oui' if (p['Profil du 02'] == PROFIL).all() else 'non'} ; autres profils : {int(autres)}",
             (attendu == obtenu).all() and (p["Profil du 02"] == PROFIL).all() and autres == 0)

    cols = ["Population", "Auto-écoles comptées", "Km en mauvais état", "Km évalués", "Km de routes classées"]
    tot = {m: r[r["Maille"] == m][cols].sum() for m in ("Zone", "Région", "Pays")}
    r04 = all((tot[m] - tot["Pays"]).abs().max() < 1e-6 for m in ("Zone", "Région"))
    r06 = pd.read_csv(EXPLORATION / "rapports_06.csv")
    r06 = r06[r06["Maille"] == "Zone"]
    noms = {"O3-02": "Part en mauvais état", "O4-05": "Auto-écoles comptées pour 100 000 habitants",
            "O4-03": "Km pour 10 000 habitants", "O3-06": "Part non évaluée"}
    zones = r[r["Maille"] == "Zone"].set_index("Territoire")
    diff = [f"{col} {z}" for col, rap in noms.items() for z in ZONES
            if abs(zones.at[z, col] - r06[(r06["Rapport"] == rap) & (r06["Territoire"] == z)]["Valeur"].iloc[0]) > 1e-9]
    mo = "Mô" in p.index[p["Zone"] == "Centrale"] and zones.at["Centrale", "Préfectures"] == int((p["Zone"] == "Centrale").sum())
    controle("9-07", "Régions", "Somme des zones = somme des régions = ligne du pays (R-04), Mô comprise ; valeurs des 6 zones égales à celles du 06",
             f"totaux égaux ({', '.join(c.lower() for c in cols)}) : {'oui' if r04 else 'non'} ; Mô dans la Centrale : "
             f"{'oui' if mo else 'non'} ; {len(noms) * 6} valeurs de zone comparées au 06, différences : {len(diff)}"
             + (" (" + ", ".join(diff) + ")" if diff else ""), r04 and mo and not diff)

    controle("9-08", "Compléments", "O2-E1 à O2-E3 absents du classement (écart 22)",
             f"indicateurs lus : {', '.join(ids_lus)} ; compléments lus : {', '.join(set(ids_lus) & set(COMPLEMENTS)) or 'aucun'}",
             not set(ids_lus) & set(COMPLEMENTS) and not any("O2-E" in col for col in p.columns))

    stable = all(x[0] <= CHANGEMENTS_TOLERES for x in synthese.values())
    controle("9-09", "Sensibilité", f"6 classements ; nombre de changements parmi les {EN_TETE} premières, par test",
             " ; ".join(f"{t} : {len(tests[t][1])} préfectures, {x[0]} changement(s)" + (f" (entrées : {', '.join(x[1])} ; sorties : {', '.join(x[2])})" if x[0] else "")
                        for t, x in synthese.items()) + f" ; classement {'stable' if stable else 'instable'} (au plus {CHANGEMENTS_TOLERES} changements)",
             len(synthese) == 6 and all(len(tests[t][1]) == (36 if t == "T4" else 38) for t in tests))
    return stable


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    v = pd.read_csv(INDICATEURS)
    ids_lus = sorted(set(v["ID"]) & set(LUS))
    v = v[v["ID"].isin(LUS)]
    p = prefectures(v)
    seuils = appliquer_seuils(p, seuil("SE-05"))
    c = p[p["Classée"]]
    s, synthese, tests, meds = sensibilite(p, c)
    leviers(p, tests["T0"][1])
    r = regions(p, v, pd.read_csv(TRAITE / "D9_repere_oms.csv"))
    stable = controles_08(p, v, r, s, synthese, tests, seuils, ids_lus)

    ordre = ["Zone", "Région", "Population", "Classée", "O3-02", "O4-05", "O4-03", "O3-06", "O4-08",
             "Réseau dégradé (SE-04)", "Formation faible (SE-07)", "Desserte faible (SE-06)", "Réseau non déterminable (SE-05)",
             "Dimensions mesurées", "O5-01 déficits", "Rang percentile réseau", "Rang percentile formation", "Score", "O5-02 rang",
             f"Parmi les {EN_TETE} premières", f"Tests parmi les {EN_TETE} premières (sur 6)", "Profil du 02", "Leviers",
             "Rang dans le levier réseau", "Rang dans le levier formation", "O5-04 km à remettre en état",
             "O5-04 auto-écoles manquantes (écart 21)", "Population au-delà de SE-08", "Auto-écoles comptées",
             "Km en mauvais état", "Km évalués", "Niveau", "Note"]
    cl = p[ordre].rename_axis("Préfecture").reset_index()
    cl = cl.assign(_r=cl["O5-02 rang"].fillna(99)).sort_values(["_r", "Préfecture"]).drop(columns="_r")
    cl.to_csv(SORTIE / "classement_08.csv", index=False)
    r.to_csv(SORTIE / "regions_08.csv", index=False)
    s.to_csv(SORTIE / "sensibilite_08.csv", index=False)
    k = pd.DataFrame(controles)
    k.to_csv(SORTIE / "controles_08.csv", index=False)

    print(f"seuils : {seuils} ; médianes du test T3 : {meds} ; classement {'stable' if stable else 'instable'}")
    print(cl[cl[f"Parmi les {EN_TETE} premières"] == True][["O5-02 rang", "Préfecture", "Zone", "Population", "O3-02", "O4-05",  # noqa: E712
                                                           "Score", "Leviers", f"Tests parmi les {EN_TETE} premières (sur 6)"]].to_string(index=False))
    print(f"contrôles : {int((k['Résultat'] == CONFORME).sum())} conformes sur {len(k)}")
    pd.set_option("display.max_colwidth", 300)
    print(k[["ID", "Contrôle", "Mesure", "Résultat"]].to_string(index=False))


if __name__ == "__main__":
    main()
