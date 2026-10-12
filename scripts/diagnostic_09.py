"""Étape 09 : diagnostic (09_diagnostic.md).

Lit les sorties du 06 (signaux, distributions, préfectures), du 07 (indicateurs_07.csv), du 08 (classement_08.csv,
regions_08.csv), le 02 (02_Hypotheses.csv) et l'état des tronçons (D4_etat_troncons.csv).
N'écrit rien dans data/processed/ ni dans les sorties du 06, du 07 et du 08.
Calcule chaque chiffre cité dans le 09 (R-19) :
- les verdicts de S1 à S5 et de H1 à H12, avec les critères du 02 (§3, §5) ;
- les 6 taux de l'énoncé et leurs volumes, moyennes 2010–2012 et 2022–2024, sur toute la fourchette du parc (§4) ;
- les faits qui fondent les phrases de diagnostic (§6).

Aucune lecture causale, aucune recommandation (10). Les phrases du §6 sont écrites dans le document.

Sorties, dans data/analysis/09_diagnostic/ : hypotheses_09.csv, taux_09.csv, diagnostic_09.csv, controles_09.csv.

Usage : .venv/bin/python scripts/diagnostic_09.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
TRAITE = RACINE / "data" / "processed"
EXPLORATION = RACINE / "data" / "analysis" / "06_exploration"
INDICATEURS = RACINE / "data" / "analysis" / "07_indicateurs" / "indicateurs_07.csv"
PRIORISATION = RACINE / "data" / "analysis" / "08_priorisation"
HYPOTHESES = RACINE / "02_decision_matrix" / "02_Hypotheses.csv"
SORTIE = RACINE / "data" / "analysis" / "09_diagnostic"
DOCUMENT = RACINE / "09_diagnostic.md"  # phrases du §6, relues par le contrôle 8-07

REGIONS = 5  # régions du Togo (R-02)
ZONES = ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]
DEBUT, FIN = [2010, 2011, 2012], [2022, 2023, 2024]  # 3 premières et 3 dernières années (H6, S4)
ANNEE_ENONCE = 2022  # S1, S2 : année des chiffres de l'énoncé (§3 a) ; 2023 et 2024 à côté
ENONCE_2022 = {"Accidents constatés": 7500, "Tués": 683}  # S3
TOLERANCE_S3 = 5  # %, critère du 02
SEUIL_S1, SEUIL_S2, SEUIL_S5, SEUIL_H8 = 4, 50, 15, 1.5  # critères du 02 (02_Hypotheses)
EN_TETE = 10
# H5 : corridor PA-07, la RN1 du port de Lomé à la frontière du Burkina Faso, sans les bretelles (§5 c)
CORRIDOR = r"^(?:TG[A-Z]{3,4} ?)?RN1 (?!BRETELLE)"
AXE_CORRIDOR = "RN1 "
# Variables de prefectures_06.csv dont le 06 a fixé les quarts (06 §4)
QUARTS = {"O3-02": "Part en mauvais état (%)", "O4-05": "Auto-écoles comptées pour 100 000 habitants",
          "O4-03": "Km pour 10 000 habitants", "O4-08": "Distance à l’auto-école comptée la plus proche (km)",
          "Population": "Population 2022"}
VERDICTS = {"confirmée", "infirmée", "nuancée", "indéterminée", "non testable"}
CONFORME, ECHEC = "conforme", "échec"

hypotheses, controles = [], []


def n(x, decimales=0, signe=False):
    s = f"{x:+,.{decimales}f}" if signe else f"{x:,.{decimales}f}"
    return s.replace(",", " ").replace(".", ",")


def sens(debut, fin):
    return "hausse" if fin > debut else "baisse" if fin < debut else "stable"


def controle(ident, intitule, attendu, mesure, ok):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC})


def serie(v, ind, cat="", mes="", champ="Valeur"):
    s = v[(v["ID"] == ind) & (v["Maille"] == "National") & v["Catégorie"].fillna("").str.startswith(cat)
          & v["Mesure"].fillna("").str.startswith(mes)]
    s = s[s["Année"].astype(str).str.fullmatch(r"\d{4}")]
    return s.set_index(s["Année"].astype(int))[champ].astype(float)


def hypothese(code, mesure, valeur, verdict, raison="", niveau=None, note=""):
    hypotheses.append({"Code": code, "Mesure": mesure, "Valeur": valeur, "Verdict": verdict, "Raison": raison,
                       "Niveau": niveau, "Note": note})


# --- §4 Les 6 taux et leurs volumes ------------------------------------------------------------------

def taux(v):
    lignes = []
    mesures = {"Accidents constatés": ("O2-03", "O2-E2"), "Blessés": ("O2-E1", "O2-E3"), "Tués": ("O2-02", "O2-04")}
    for mesure, (hab, veh) in mesures.items():
        vol = serie(v, "O2-01", cat=mesure)
        lignes.append({"Mesure": mesure, "Lecture": "volume", "ID": "O2-01", "Moyenne 2010–2012": round(vol[DEBUT].mean(), 1),
                       "Moyenne 2022–2024": round(vol[FIN].mean(), 1), "Niveau": "A"})
        for lecture, ind in (("pour 100 000 habitants", hab), ("pour 10 000 véhicules", veh)):
            x = serie(v, ind)
            ligne = {"Mesure": mesure, "Lecture": lecture, "ID": ind, "Moyenne 2010–2012": round(x[DEBUT].mean(), 2),
                     "Moyenne 2022–2024": round(x[FIN].mean(), 2), "Niveau": "C",
                     "Note": "complément de l’énoncé, hors 02 (écart 22) : descriptif, sans verdict" if ind.startswith("O2-E") else ""}
            if lecture.endswith("véhicules"):
                # borne basse du taux = parc haut ; borne haute = parc bas (07, PA-01)
                for borne in ("Borne basse", "Borne haute"):
                    b = serie(v, ind, champ=borne)
                    ligne[f"Moyenne 2010–2012 ({borne.lower()})"] = round(b[DEBUT].mean(), 2)
                    ligne[f"Moyenne 2022–2024 ({borne.lower()})"] = round(b[FIN].mean(), 2)
                    ligne[f"Sens ({borne.lower()})"] = sens(b[DEBUT].mean(), b[FIN].mean())
            lignes.append(ligne)
    t = pd.DataFrame(lignes)
    t["Variation (%)"] = ((t["Moyenne 2022–2024"] / t["Moyenne 2010–2012"] - 1) * 100).round(1)
    t["Sens"] = [sens(a, b) for a, b in zip(t["Moyenne 2010–2012"], t["Moyenne 2022–2024"])]
    veh = t["Lecture"] == "pour 10 000 véhicules"
    t["Sens sur la fourchette"] = t["Sens"]
    t.loc[veh, "Sens sur la fourchette"] = [
        r["Sens"] if r["Sens"] == r["Sens (borne basse)"] == r["Sens (borne haute)"] else "indéterminé" for _, r in t[veh].iterrows()]
    colonnes = ["Mesure", "Lecture", "ID", "Moyenne 2010–2012", "Moyenne 2022–2024", "Variation (%)", "Sens",
                "Moyenne 2010–2012 (borne basse)", "Moyenne 2022–2024 (borne basse)", "Sens (borne basse)",
                "Moyenne 2010–2012 (borne haute)", "Moyenne 2022–2024 (borne haute)", "Sens (borne haute)",
                "Sens sur la fourchette", "Niveau", "Note"]
    return t[colonnes]


# --- §3 et §5 Hypothèses -----------------------------------------------------------------------------

def enonce(v, t, r):
    mult = serie(v, "O1-03", cat="Ensemble", mes="multiplicateur")
    m = mult[ANNEE_ENONCE]
    autres = " ; ".join(f"{a} : {n(mult[a], 2)}" + (" (depuis 2004, année de rupture de la série, 04)" if a - 20 == 2004 else "")
                        for a in (2023, 2024))
    hypothese("S1", f"Multiplicateur {ANNEE_ENONCE} : {n(m, 2)} (I({ANNEE_ENONCE}) / I({ANNEE_ENONCE - 20})) ; {autres}", m,
              "confirmée" if m >= SEUIL_S1 else "infirmée", niveau="B")

    imm = {g: serie(v, "O1-01", cat=g) for g in ("Moto", "Ensemble")}
    a, b = ANNEE_ENONCE, ANNEE_ENONCE - 20
    contrib = (imm["Moto"][a] - imm["Moto"][b]) / (imm["Ensemble"][a] - imm["Ensemble"][b]) * 100
    hypothese("S2", f"Contribution des motos à la hausse de {b} à {a} : {n(contrib, 1)} % "
                    f"({n(imm['Moto'][a] - imm['Moto'][b])} motos sur {n(imm['Ensemble'][a] - imm['Ensemble'][b])} immatriculations de plus)",
              round(contrib, 1), "confirmée" if contrib > SEUIL_S2 else "infirmée", niveau="B")

    ecarts = {k: (serie(v, "O2-01", cat=k)[2022], (serie(v, "O2-01", cat=k)[2022] / ref - 1) * 100) for k, ref in ENONCE_2022.items()}
    o202 = r.loc[r["Maille"] == "Pays"].iloc[0]
    rapport = o202["SE-03 repère OMS Togo 2021"] / o202["SE-03 O2-02 de 2021 (tués déclarés)"]
    hypothese("S3", " ; ".join(f"{k} 2022 : {n(x)} face à {n(ENONCE_2022[k])} ({n(e, 1, True)} %)" for k, (x, e) in ecarts.items()),
              round(max(abs(e) for _, e in ecarts.values()), 1),
              "confirmée" if all(abs(e) <= TOLERANCE_S3 for _, e in ecarts.values()) else "infirmée", niveau="A",
              note=f"Sous-déclaration : en 2021, l’estimation de l’OMS ({n(o202['SE-03 repère OMS Togo 2021'], 1)} tués pour 100 000 habitants) "
                   f"vaut {n(rapport, 2)} fois le taux déclaré ({n(o202['SE-03 O2-02 de 2021 (tués déclarés)'], 2)}) ; "
                   "une estimation, jamais une correction des tués déclarés (D9)")

    ti = t.set_index(["Mesure", "Lecture"])
    vol, hab, veh = ti.loc[("Accidents constatés", "volume")], ti.loc[("Tués", "pour 100 000 habitants")], ti.loc[("Tués", "pour 10 000 véhicules")]
    if vol["Sens"] == "baisse":
        verdict = "infirmée"
    elif hab["Sens"] == "baisse" or veh["Sens sur la fourchette"] == "baisse":
        verdict = "nuancée"
    else:
        verdict = "confirmée" if hab["Sens"] == "hausse" else "nuancée"
    hypothese("S4", f"Accidents constatés : {n(vol['Moyenne 2010–2012'], 1)} puis {n(vol['Moyenne 2022–2024'], 1)} par an ({vol['Sens']}) ; "
                    f"tués pour 100 000 habitants : {n(hab['Moyenne 2010–2012'], 2)} puis {n(hab['Moyenne 2022–2024'], 2)} ({hab['Sens']}) ; "
                    f"tués pour 10 000 véhicules : {n(veh['Moyenne 2010–2012'], 2)} puis {n(veh['Moyenne 2022–2024'], 2)} "
                    f"({veh['Sens sur la fourchette']} sur la fourchette du parc)",
              vol["Variation (%)"], verdict, niveau="B (C pour le taux par véhicule)")

    z = r[r["Maille"] == "Zone"].set_index("Territoire")["O3-02"]
    ecart = z.max() - z.min()
    hypothese("S5", f"O3-02 : {z.idxmax()} {n(z.max(), 1)} %, {z.idxmin()} {n(z.min(), 1)} % ; écart {n(ecart, 1)} points",
              round(ecart, 1), "confirmée" if ecart >= SEUIL_S5 else "infirmée", niveau="C")


def liens(v, t, r, c, p6):
    cumul = v[(v["ID"] == "O1-09") & v["Année"].astype(str).str.contains("–")].set_index("Catégorie")["Valeur"]
    hypothese("H1", "O1-09 en cumul 2007–2024 : " + ", ".join(f"{k} {n(x, 2)}" for k, x in cumul.sort_values(ascending=False).items()),
              cumul["A"], "confirmée" if cumul.idxmax() == "A" else "infirmée", niveau="B",
              note="catégorie A : motos ; une tension, pas un nombre de conducteurs sans permis (02)")

    part_tues = v[(v["ID"] == "O2-09") & (v["Catégorie"] == "Deux et trois-roues motorisés")]["Valeur"].iloc[0]
    parc = v[(v["ID"] == "O1-05") & (v["Année"].astype(str) == "2021")].set_index("Catégorie")
    indices = {}
    for nom, champ in (("valeur centrale", "Valeur"), ("parc bas", "Borne basse"), ("parc haut", "Borne haute")):
        indices[nom] = part_tues / (parc.at["Moto", champ] / parc.at["Ensemble", champ] * 100)
    verdict = "confirmée" if min(indices.values()) > 1 else "infirmée" if max(indices.values()) < 1 else "indéterminée"
    hypothese("H2", f"Tués de 2021 : {n(part_tues)} % de deux et trois-roues motorisés (OMS) ; part des motos dans le parc estimé : "
                    + ", ".join(f"{k} {n(parc.at['Moto', ch] / parc.at['Ensemble', ch] * 100, 1)} %" for k, ch in
                                (("centrale", "Valeur"), ("parc bas", "Borne basse"), ("parc haut", "Borne haute")))
                    + " ; indice : " + ", ".join(f"{k} {n(x, 2)}" for k, x in indices.items()),
              round(indices["valeur centrale"], 2), verdict, raison="testée sur les tués seulement (écart 26)", niveau="C",
              note="véhicules impliqués non testés (O2-08, écart 2) ; la catégorie de l’OMS inclut les trois-roues")

    pas_accidents = "pas d’accidents par territoire (écart 1)"
    for code in ("H3", "H4", "H7"):
        hypothese(code, "", np.nan, "non testable", raison=pas_accidents)

    tr = pd.read_csv(TRAITE / "D4_etat_troncons.csv")
    cor = tr[tr["Tronçon"].str.contains(CORRIDOR, regex=True) | tr["Axe"].fillna("").str.startswith(AXE_CORRIDOR)]
    part_cor = cor["km_mauvais"].sum() / cor["km_total"].sum() * 100
    pays = r[r["Maille"] == "Pays"].iloc[0]["O3-02"]
    # Le 02 : confirmée si les deux conditions sont remplies ; infirmée si l'une ne l'est pas. La condition sur les
    # accidents n'est pas mesurée (écart 2) : seule une condition réseau non remplie suffit à trancher.
    reseau_rempli = part_cor > pays
    hypothese("H5", f"Corridor de la RN1 : {len(cor)} tronçons, {n(cor['km_total'].sum(), 1)} km, {n(part_cor, 1)} % en mauvais état, "
                    f"{'au-dessus' if reseau_rempli else 'en dessous'} du pays ({n(pays, 1)} %) ; part des poids lourds dans les accidents : non mesurée",
              round(part_cor, 1), "non testable" if reseau_rempli else "infirmée",
              raison=("condition réseau remplie, mais la condition sur les accidents n’est pas mesurée (écart 2)" if reseau_rempli else
                      "condition réseau non remplie : cela suffit au critère du 02 ; la condition sur les accidents n’est pas mesurée (écart 2)"),
              niveau="C", note="tronçons : " + " | ".join(cor["Tronçon"]))

    ti = t.set_index(["Mesure", "Lecture"])
    hab, veh = ti.loc[("Tués", "pour 100 000 habitants")], ti.loc[("Tués", "pour 10 000 véhicules")]
    sens_veh = [veh["Sens"], veh["Sens (borne basse)"], veh["Sens (borne haute)"]]
    oppose = [s != hab["Sens"] and "stable" not in (s, hab["Sens"]) for s in sens_veh]
    verdict = "confirmée" if all(oppose) else "infirmée" if not any(oppose) else "indéterminée"
    hypothese("H6", f"Tués pour 100 000 habitants : {hab['Sens']} ({n(hab['Variation (%)'], 1, True)} %) ; tués pour 10 000 véhicules : "
                    f"{veh['Sens']} ({n(veh['Variation (%)'], 1, True)} %), parc haut : {veh['Sens (borne basse)']}, parc bas : {veh['Sens (borne haute)']}",
              veh["Variation (%)"], verdict, niveau="C")

    p = p6.set_index("Préfecture")
    urb = p["Classe PA-03"] == "urbaine"
    part_ae = p.loc[urb, "Auto-écoles comptées"].sum() / p["Auto-écoles comptées"].sum() * 100
    part_rec = p.loc[urb, "Auto-écoles recensées"].sum() / p["Auto-écoles recensées"].sum() * 100
    part_pop = p.loc[urb, "Population 2022"].sum() / p["Population 2022"].sum() * 100
    hypothese("H8", f"Préfectures urbaines (PA-03) : {', '.join(p.index[urb])} ; {n(part_ae, 1)} % des auto-écoles comptées pour "
                    f"{n(part_pop, 1)} % de la population, soit {n(part_ae / part_pop, 2)} fois ; recensées : {n(part_rec, 1)} %, "
                    f"{n(part_rec / part_pop, 2)} fois",
              round(part_ae / part_pop, 2), "confirmée" if part_ae / part_pop >= SEUIL_H8 else "infirmée", niveau="B")

    deux = c[c["O5-01 déficits"] == 2]
    hypothese("H9", f"Cumul partiel, sans valeur de verdict : {len(deux)} préfectures cumulent réseau dégradé et formation faible "
                    f"({', '.join(deux['Préfecture'])} ; {n(deux['Population'].sum())} habitants)",
              len(deux), "non testable", raison="le cumul complet (SE-10) exige le risque, non mesuré par territoire (08 §3.1)")
    hypothese("H10", "", np.nan, "non testable", raison="pas de mois (écart 2)")
    hypothese("H11", "", np.nan, "non testable", raison="ni la part du Grand Lomé dans les accidents ni son taux ne sont connus (écart 1)")
    hypothese("H12", "", np.nan, "non testable", raison="pas d’âge des conducteurs (écart 2)")
    return cor


def tableau_hypotheses():
    h = pd.read_csv(HYPOTHESES).set_index("Code")
    d = pd.DataFrame(hypotheses).set_index("Code")
    d = h[["Type", "Énoncé", "Indicateurs utilisés", "Confirmée si", "Infirmée si"]].join(d, how="inner")
    d = d.join(h[["Conséquence pour la décision", "Preuve attendue"]])
    d["Niveau"] = d["Niveau"].fillna("—")
    ordre = [f"S{i}" for i in range(1, 6)] + [f"H{i}" for i in range(1, 13)]
    return d.reindex(ordre).reset_index()


# --- §6 Diagnostic par territoire ---------------------------------------------------------------------

def position(valeur, q1, q3):
    """Règle du 06 (§4) : haut ≥ Q3 et > Q1 ; bas ≤ Q1 et < Q3 ; ex aequo compris."""
    if pd.isna(valeur):
        return "non défini"
    if valeur >= q3 and valeur > q1:
        return "haut"
    if valeur <= q1 and valeur < q3:
        return "bas"
    return "milieu"


def nomme(territoire, texte):
    return re.search(r"(?<![\w-])" + re.escape(territoire) + r"(?![\w-])", texte) is not None


def diagnostic(v, c, r, signaux, dist):
    tr = pd.read_csv(TRAITE / "D4_etat_troncons.csv")
    crit = tr[tr["km_mauvais"] > 0]
    par_pref = crit.assign(P=crit["Préfectures traversées"].str.split(" ; ")).explode("P")
    par_zone = crit.assign(Z=crit["Zones traversées"].str.split(" ; ")).explode("Z")
    rec = v[(v["ID"] == "O4-04") & (v["Catégorie"] == "recensées")].set_index("Territoire")["Valeur"]
    q = dist[dist["Maille"] == "Préfecture"].set_index("Variable")[["Q1", "Q3"]]

    def sig(territoire):
        return ", ".join(signaux.loc[[nomme(territoire, t) for t in signaux["Résumé"]], "ID"])

    lignes = []
    cible = c[(c["Parmi les 10 premières"] == True) | (c["Préfecture"] == "Mô")]  # noqa: E712
    for _, x in cible.iterrows():
        pref = x["Préfecture"]
        tp = par_pref[par_pref["P"] == pref]
        ligne = {"Maille": "Préfecture", "Territoire": pref, "Zone": x["Zone"], "Population": x["Population"],
                 "O5-02 rang": x["O5-02 rang"], "Leviers": x["Leviers"], "O5-01 déficits": x["O5-01 déficits"],
                 "O3-02": x["O3-02"], "Km évalués": x["Km évalués"], "Km en mauvais état": x["Km en mauvais état"],
                 "Tronçons critiques qui la traversent": len(tp), "Noms des tronçons critiques": " | ".join(tp["Tronçon"]),
                 "O4-05": x["O4-05"], "Auto-écoles comptées": x["Auto-écoles comptées"], "Auto-écoles recensées": int(rec[pref]),
                 "O4-03": x["O4-03"], "Desserte faible (SE-06)": x["Desserte faible (SE-06)"], "O4-08": x["O4-08"],
                 "Au-delà de SE-08": x["Population au-delà de SE-08"] > 0,
                 "O5-04 km à remettre en état": x["O5-04 km à remettre en état"],
                 "O5-04 auto-écoles manquantes (écart 21)": x["O5-04 auto-écoles manquantes (écart 21)"],
                 "Tests parmi les 10 premières (sur 6)": x["Tests parmi les 10 premières (sur 6)"],
                 "Signaux du 06": sig(pref), "Niveau": "C", "Note": x["Note"] if pd.notna(x["Note"]) else ""}
        for ind, var in QUARTS.items():
            ligne[f"Position {ind} (quarts du 06)"] = position(x[ind], q.at[var, "Q1"], q.at[var, "Q3"])
        lignes.append(ligne)
    for _, z in r[(r["Maille"] == "Zone") | ((r["Maille"] == "Région") & (r["Territoire"] == "Maritime"))].iterrows():
        nom = z["Territoire"]
        tz = par_zone[par_zone["Z"] == nom] if z["Maille"] == "Zone" else par_zone[par_zone["Z"].isin(["Grand Lomé", "Maritime hors Grand Lomé"])].drop_duplicates("Tronçon")
        seuils = [s for s, col in (("réseau", "Réseau dégradé (au-dessus de la médiane)"), ("formation", "Formation faible (sous la médiane)"),
                                   ("desserte", "Desserte faible (sous la médiane)")) if z[col] == True]  # noqa: E712
        lignes.append({"Maille": z["Maille"], "Territoire": nom, "Population": z["Population"], "Rang (zones ou régions)": z["Rang"],
                       "Seuils franchis (médiane)": ", ".join(seuils), "O3-02": z["O3-02"], "Km évalués": z["Km évalués"],
                       "Km en mauvais état": z["Km en mauvais état"], "Tronçons critiques qui la traversent": len(tz),
                       "O4-05": z["O4-05"], "Auto-écoles comptées": z["Auto-écoles comptées"], "O4-03": z["O4-03"],
                       "Préfectures": z["Préfectures"], "Préfectures au levier réseau": z["Préfectures au levier réseau"],
                       "Préfectures au levier formation": z["Préfectures au levier formation"],
                       "O5-04 km à remettre en état": z["O5-04 km à remettre en état, préfectures au levier réseau"],
                       "O5-04 auto-écoles manquantes (écart 21)": z["O5-04 auto-écoles manquantes (écart 21), préfectures au levier formation"],
                       "Signaux du 06": sig(nom), "Niveau": "C"})
    d = pd.DataFrame(lignes)
    for col in ("O5-02 rang", "Rang (zones ou régions)", "O5-01 déficits", "Tronçons critiques qui la traversent", "Auto-écoles comptées",
                "Auto-écoles recensées", "O5-04 auto-écoles manquantes (écart 21)", "Tests parmi les 10 premières (sur 6)",
                "Préfectures", "Préfectures au levier réseau", "Préfectures au levier formation"):
        d[col] = d[col].astype("Int64")
    premieres = ["Maille", "Territoire", "Zone", "Population", "O5-02 rang", "Rang (zones ou régions)", "Seuils franchis (médiane)"]
    return d[premieres + [k for k in d.columns if k not in premieres]], crit


# --- §8 Contrôles ------------------------------------------------------------------------------------

def controles_09(h, t, d, c, v, cor, crit):
    ref = pd.read_csv(HYPOTHESES).set_index("Code")
    hh = h.set_index("Code")
    memes = (hh[["Confirmée si", "Infirmée si"]] == ref.loc[hh.index, ["Confirmée si", "Infirmée si"]]).all(axis=1).all()
    permis = {"S4": {"confirmée", "infirmée", "nuancée"}, "H2": {"confirmée", "infirmée", "indéterminée"},
              "H6": {"confirmée", "infirmée", "indéterminée"}}
    hors = [k for k, x in hh["Verdict"].items() if x not in permis.get(k, {"confirmée", "infirmée", "non testable"})]
    sans_raison = [k for k, x in hh.iterrows() if x["Verdict"] == "non testable" and not x["Raison"]]
    controle("8-01", "Hypothèses", "17 lignes ; critères identiques au 02 ; un verdict permis par le 02 ; une raison pour chaque « non testable »",
             f"{len(hh)} lignes ; critères identiques : {'oui' if memes else 'non'} ; verdicts : "
             + ", ".join(f"{k} {x}" for k, x in hh["Verdict"].value_counts().items())
             + f" ; hors des verdicts permis : {', '.join(hors) or 'aucun'} ; non testables sans raison : {', '.join(sans_raison) or 'aucune'}",
             len(hh) == 17 and memes and not hors and not sans_raison)

    pref = d[d["Maille"] == "Préfecture"].set_index("Territoire")
    cl = c.set_index("Préfecture").loc[pref.index]
    cols = ["Population", "O3-02", "O4-05", "O4-03", "O4-08", "Km évalués", "Auto-écoles comptées"]
    diff = [f"{k} {col}" for col in cols for k in pref.index
            if not (pd.isna(pref.at[k, col]) and pd.isna(cl.at[k, col])) and abs(float(pref.at[k, col]) - float(cl.at[k, col])) > 1e-9]
    o202 = serie(v, "O2-02")
    t_ok = abs(t[(t["ID"] == "O2-02")]["Moyenne 2010–2012"].iloc[0] - round(o202[DEBUT].mean(), 2)) < 1e-9
    controle("8-02", "Concordance", "Valeurs reprises égales à celles du 07 et du 08",
             f"{len(cols) * len(pref)} valeurs de préfecture comparées à classement_08.csv, différences : {len(diff)} ; "
             f"moyennes de taux recalculées depuis indicateurs_07.csv : {'identiques' if t_ok else 'différentes'}",
             not diff and t_ok)

    complet = all(serie(v, i).reindex(DEBUT + FIN).notna().all() for i in t["ID"].unique() if i != "O2-01")
    veh = t[t["Lecture"] == "pour 10 000 véhicules"]
    controle("8-03", "6 taux", "6 taux et leurs 3 volumes ; moyennes sur 3 années complètes ; taux par véhicule aux trois valeurs du parc",
             f"{int((t['Lecture'] != 'volume').sum())} taux, {int((t['Lecture'] == 'volume').sum())} volumes ; années complètes : "
             f"{'oui' if complet else 'non'} ; taux par véhicule avec leurs bornes : {int(veh[['Sens (borne basse)', 'Sens (borne haute)']].notna().all(axis=1).sum())} sur {len(veh)}",
             len(t) == 9 and complet and veh[["Sens (borne basse)", "Sens (borne haute)"]].notna().all().all())

    h2 = hh.loc["H2"]
    controle("8-04", "H2 (écart 26)", "Part des motos aux deux bornes et à la valeur centrale du parc ; verdict selon la règle de SE-09",
             f"{h2['Mesure']} → {h2['Verdict']}", all(f"{k} " in h2["Mesure"].split("indice : ")[1] for k in ("valeur centrale", "parc bas", "parc haut")))

    somme = cor[["km_bon", "km_moyen", "km_mauvais", "km_travaux"]].sum().sum()
    bouts = (cor["Tronçon"].str.contains("LOME").any(), cor["Tronçon"].str.contains("FRE BURKINA").any())
    controle("8-05", "H5, partie réseau", "6 tronçons, de Lomé à la frontière du Burkina Faso ; sommes de km égales au relevé",
             f"{len(cor)} tronçons ; Lomé : {'oui' if bouts[0] else 'non'} ; frontière du Burkina Faso : {'oui' if bouts[1] else 'non'} ; "
             f"km par état {n(somme, 2)}, km relevés {n(cor['km_total'].sum(), 2)}",
             len(cor) == 6 and all(bouts) and abs(somme - cor["km_total"].sum()) < 0.05)

    nat = v[(v["ID"] == "O3-05") & (v["Maille"] == "National") & (v["Mesure"] == "nombre de tronçons")]["Valeur"].iloc[0]
    attendu = {"Préfecture": 11, "Zone": 6, "Région": 1}
    compte = d["Maille"].value_counts().to_dict()
    controle("8-06", "Diagnostic", "Une ligne par territoire (10 préfectures, Mô, 6 zones, la région Maritime) ; tronçons critiques recomptés depuis le relevé",
             f"lignes : {', '.join(f'{k} {x}' for k, x in compte.items())} ; Mô : {'oui' if 'Mô' in set(d['Territoire']) else 'non'} ; "
             f"tronçons critiques recomptés : {len(crit)} (07 : {int(nat)})",
             compte == attendu and "Mô" in set(d["Territoire"]) and len(crit) == nat)

    nb, nombres, erreurs = phrases(d)
    controle("8-07", "Phrases du §6", "Chaque nombre des phrases se retrouve dans diagnostic_09.csv, pour le territoire de la phrase "
             "ou un territoire qu’elle nomme ; rangs et tests vérifiés", f"{nb} phrases, {nombres} nombres vérifiés ; écarts : "
             + (", ".join(erreurs) if erreurs else "aucun"), nb == 18 and not erreurs)


NOMBRE = r"\d{1,3}(?: \d{3})+(?:,\d+)?|\d+(?:,\d+)?"


def phrases(d):
    """Contrôle 8-07 : chaque nombre d'une phrase du §6 vaut, à son arrondi, une valeur du territoire de la phrase
    ou d'un territoire qu'elle nomme. Sont retirés avant : les identifiants de signaux, les unités « pour 10 000 » et
    « pour 100 000 », et les tournures de rang et de tests, vérifiées à part."""
    texte = DOCUMENT.read_text(encoding="utf-8") if DOCUMENT.exists() else ""
    if "**Résultat : préfectures en tête**" not in texte:
        return 0, 0, ["section des phrases introuvable"]
    section = texte.split("**Résultat : préfectures en tête**")[1].split("\n## 7.")[0]
    lignes = [l for l in section.splitlines() if re.match(r"^(?:\d+\. )?\*\*[^*]+\*\*", l) and not l.startswith("**Résultat")]
    d = d.assign(_cle=d["Maille"].map({"Région": "Région "}).fillna("") + d["Territoire"])
    erreurs, compte = [], 0
    for ligne in lignes:
        nom = re.match(r"^(?:\d+\. )?\*\*([^*]+)\*\*", ligne).group(1)
        propre = d[d["_cle"] == nom]
        if propre.empty:
            erreurs.append(f"{nom} : territoire inconnu")
            continue
        x = propre.iloc[0]
        rangs = [x.get("O5-02 rang"), x.get("Rang (zones ou régions)")]
        t = re.sub(r"SIG-\d+|(?<![\d,])0\d(?![\d,])", "", ligne)  # signaux et numéros de documents (« au 06 »)
        t = re.sub(r"pour 10{1,2} 000", "pour", t)
        m = re.match(r"^(\d+)\. ", t)
        if m and int(m.group(1)) not in [int(r) for r in rangs if pd.notna(r)]:
            erreurs.append(f"{nom} : rang {m.group(1)}")
        t = re.sub(r"^\d+\. ", "", t)
        for tests in re.findall(r"(\d+) tests? sur 6", t):
            if int(tests) != x["Tests parmi les 10 premières (sur 6)"]:
                erreurs.append(f"{nom} : {tests} tests")
        t = re.sub(r"\d+ tests? sur 6", "", t).replace("la moins sûre des 10", "")
        for r, total in re.findall(r"\((\d+)e des (\d+) régions\)", t):
            if int(r) != x["Rang (zones ou régions)"] or int(total) != REGIONS:
                erreurs.append(f"{nom} : rang {r} sur {total}")
        t = re.sub(r"\(\d+e des \d+ régions\)", "", t).replace("Les 4 autres régions", "")
        nommes = d[[nomme(k, ligne) for k in d["Territoire"]]]
        candidats = pd.concat([propre, nommes]).select_dtypes("number").to_numpy().ravel()
        candidats = candidats[~pd.isna(candidats)].astype(float)
        for brut in re.findall(NOMBRE, t):
            compte += 1
            val = float(brut.replace(" ", "").replace(",", "."))
            dec = len(brut.split(",")[1]) if "," in brut else 0
            if not np.any(np.abs(np.round(candidats, dec) - val) < 1e-9):
                erreurs.append(f"{nom} : {brut}")
    return len(lignes), compte, erreurs


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    v = pd.read_csv(INDICATEURS)
    c = pd.read_csv(PRIORISATION / "classement_08.csv")
    r = pd.read_csv(PRIORISATION / "regions_08.csv")
    p6 = pd.read_csv(EXPLORATION / "prefectures_06.csv")
    t = taux(v)
    enonce(v, t, r)
    cor = liens(v, t, r, c, p6)
    h = tableau_hypotheses()
    d, crit = diagnostic(v, c, r, pd.read_csv(EXPLORATION / "signaux_06.csv"), pd.read_csv(EXPLORATION / "distributions_06.csv"))
    controles_09(h, t, d, c, v, cor, crit)

    h.to_csv(SORTIE / "hypotheses_09.csv", index=False)
    t.to_csv(SORTIE / "taux_09.csv", index=False)
    d.to_csv(SORTIE / "diagnostic_09.csv", index=False)
    k = pd.DataFrame(controles)
    k.to_csv(SORTIE / "controles_09.csv", index=False)
    pd.set_option("display.max_colwidth", 260)
    pd.set_option("display.width", 300)
    print(h[["Code", "Verdict", "Mesure"]].to_string(index=False))
    print(t[["Mesure", "Lecture", "Moyenne 2010–2012", "Moyenne 2022–2024", "Variation (%)", "Sens sur la fourchette"]].to_string(index=False))
    print(f"contrôles : {int((k['Résultat'] == CONFORME).sum())} conformes sur {len(k)}")
    print(k[["ID", "Contrôle", "Mesure", "Résultat"]].to_string(index=False))


if __name__ == "__main__":
    main()
