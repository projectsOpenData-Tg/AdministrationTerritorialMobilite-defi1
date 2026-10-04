"""Étape 04 : contrôles de cohérence (04_data_understanding.md, §4).

Lit data/raw/, data/reference/ et les tableaux extraits des PDF (data/interim/, écrits par
extraction_pdf_04.py). Écrit data/analysis/04_understanding/controles_coherence.csv : une ligne par
contrôle, avec ce qu'il mesure, son résultat (conforme ; écart expliqué ; anomalie transmise au 05) et ce
qu'il décide.

Le 04 ne corrige rien : une anomalie est décrite, puis transmise au 05. Une valeur absente n'est jamais
comptée comme 0 (R-10) : les comparaisons portent sur les années publiées par les deux sources. Les
contrôles spatiaux (points et tronçons dans leur préfecture) sont faits par jointures_04.py (§5).

EHCVM : seules des statistiques agrégées sortent du script (conditions d'usage de la Banque mondiale).
En plus des fichiers utiles (03 §7), le script lit la taille des ménages (fichier welfare) et l'agrégat
`moto` du fichier des ménages, pour les contrôles du §4.5.

Usage : .venv/bin/python scripts/coherence_04.py
"""
import json
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
REFERENCE = RACINE / "data" / "reference"
INTERIM = RACINE / "data" / "interim"
SORTIE = RACINE / "data" / "analysis" / "04_understanding"

UTM31N = 32631  # R-16
CONFORME, EXPLIQUE, ANOMALIE = "conforme", "écart expliqué", "anomalie transmise au 05"
ZONES_RECENSEMENT = ["SAVANES", "KARA", "CENTRALE", "PLATEAUX", "MARITIME", "DAGL"]
# Zones du référentiel → tableaux du Livret 02
ZONES_LIVRET = {"Grand Lomé": "Grand Lomé", "Maritime hors Grand Lomé": "Maritime sans Grand Lomé",
                "Plateaux": "Plateaux", "Centrale": "Centrale", "Kara": "Kara", "Savanes": "Savanes"}
EHCVM_ZONES = {1: "Maritime hors Grand Lomé", 2: "Plateaux", 3: "Centrale", 4: "Kara", 5: "Savanes", 6: "Grand Lomé"}
EHCVM_MOTO = 29  # s12q01 : « Cyclomoteur/Vélomoteur, motocyclette » (dictionnaire de l'enquête)
PA01_MOTOS = (7, 5, 10)  # durée de vie des motos : valeur centrale, bornes (02, 03_Seuils)
ARRONDI = 0.01  # tolérance d'arrondi des longueurs publiées au centième de km

controles = []


def controle(ident, section, intitule, sources, mesure, resultat, decision):
    controles.append({"ID": ident, "Section": section, "Contrôle": intitule, "Sources": sources,
                      "Mesure": mesure, "Résultat": resultat, "Décision": decision})


def n(x, decimales=0):
    """Nombre au format français : 7 507 ; 0,34."""
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def pct(a, b, decimales=1):
    """Écart relatif signé de a à b : +1,7 % ; −4,8 %."""
    e = 100 * (a / b - 1)
    return ("+" if e > 0 else "") + n(e, decimales).replace("-", "−") + " %"


def portail(fichier):
    df = pd.read_csv(BRUT / fichier, dtype=str)
    df["Value"] = pd.to_numeric(df["Value"])
    df["Date"] = pd.to_numeric(df["Date"])
    return df


def serie(df, colonne, modalite):
    return df[df[colonne] == modalite].set_index("Date")["Value"].sort_index()


def egalite(a, b):
    """Années communes aux deux séries, et années où elles diffèrent."""
    communes = a.index.intersection(b.index)
    return communes, [an for an in communes if a[an] != b[an]]


def annuaire(numero):
    a = pd.read_csv(INTERIM / "annuaire2024_tableaux.csv")
    a = a[a["Tableau"].astype(str) == numero]
    if numero == "39.2":
        return a
    return a.pivot(index="Ligne", columns="Année", values="Valeur")


def lire_ehcvm():
    with zipfile.ZipFile(BRUT / "ehcvm_2021_2022_csv.zip") as z:
        lire = lambda f, c: pd.read_csv(z.open(f), usecols=c)
        cle = ["grappe", "menage"]
        return {
            "pond": lire("ehcvm_ponderations_tgo2021.csv", cle + ["poids", "s00q01"]),
            "s12": lire("s12_me_tgo2021.csv", cle + ["s12q01", "s12q03"]),
            "s09b": lire("s09b_me_tgo2021.csv", cle + ["s09bq01"]),
            "welfare": lire("ehcvm_welfare_tgo2021.csv", cle + ["hhweight", "hhsize"]),
            "menage": lire("ehcvm_menage_tgo2021.csv", cle + ["moto", "car"]),
        }


# --- 4.1 Cohérence interne ---------------------------------------------------------------------

def interne(p1, p2, permis, etat, accidents, livret):
    w1 = p1.pivot(index="Date", columns="types-de-vehicule", values="Value")
    types = [c for c in w1.columns if c != "Total"]
    complet = w1[types].notna().all(axis=1)
    faux = [an for an in w1.index[complet] if w1.loc[an, types].sum() != w1.loc[an, "Total"]]
    controle("4.1-01", "4.1", "Parc (fichier 1) : le total égale la somme des 7 types", "parc_immatricule_par_type_1.csv",
             f"{int(complet.sum()) - len(faux)} années sur {int(complet.sum())} ({w1.index.min()}–{w1.index.max()})",
             CONFORME if not faux else ANOMALIE, "Fiabilité de O1-01 à O1-03")

    w2 = p2.pivot(index="Date", columns="automobile", values="Value")
    quatre = ["Voitures", "Camionnettes", "Auto-cars", "Camions", "Semi-Remorques", "Tract. Routiers"]
    deux = ["Engins à 2 R de 50 à 125cm3", "Engins à 2 R + de 125cm3"]
    ecart4 = w2["Total 4 Roues"] - w2[quatre].sum(axis=1)
    ecart2 = w2["Total 2 Roues"] - w2[deux].sum(axis=1)
    controle("4.1-02", "4.1", "Parc (fichier 2) : totaux 4 roues et 2 roues égaux à la somme de leurs types",
             "parc_immatricule_par_type_2.csv",
             f"4 roues : {int((ecart4 == 0).sum())} années sur {len(w2)} ; 2 roues : {int((ecart2 == 0).sum())} sur {len(w2)}"
             + (f" ; total 2 roues moins les deux cylindrées : de {n(ecart2.min())} à {n(ecart2.max())}" if (ecart2 != 0).any() else ""),
             CONFORME if (ecart4 == 0).all() and (ecart2 == 0).all() else ANOMALIE,
             "Le fichier 2 sert seulement au détail des cylindrées (2013–2019)")

    sommes = []
    for numero, total, lignes in (("40.1", "Total", None), ("40.2", "Total", ["Neufs", "Occasions"]),
                                  ("40.3", "Total", None), ("40.4", "Total", None)):
        t = annuaire(numero)
        parts = t.drop(index=total) if lignes is None else t.loc[lignes]
        ecarts = (t.loc[total] - parts.sum()).astype(int)
        sommes.append(f"{numero} : {int((ecarts == 0).sum())}/{len(ecarts)}"
                      + ("" if (ecarts == 0).all() else f" (écarts {', '.join(f'{a} : {n(e)}' for a, e in ecarts.items() if e)})"))
    controle("4.1-03", "4.1", "Annuaire 2024 : chaque total égale la somme de ses lignes (2020–2024)", "annuaire 2024, tableaux 40.1 à 40.4",
             " ; ".join(sommes), CONFORME if all("écarts" not in s for s in sommes) else ANOMALIE,
             "Les tableaux de l'annuaire sont lisibles tels quels")

    wp = permis.pivot(index="Date", columns="categories-de-permis", values="Value")
    cats = [c for c in wp.columns if c != "Total"]
    complet = wp[cats].notna().all(axis=1)
    faux = [an for an in wp.index[complet] if wp.loc[an, cats].sum() != wp.loc[an, "Total"]]
    vides = [an for an in wp.index if wp.loc[an, cats].isna().all()]
    controle("4.1-04", "4.1", "Permis : le total égale la somme des catégories A à F", "permis_par_categorie.csv",
             f"{int(complet.sum()) - len(faux)} années sur {int(complet.sum())} ; "
             + "".join(f"{an} : aucune catégorie, total = {n(wp.loc[an, 'Total'])}" for an in vides),
             EXPLIQUE if not faux else ANOMALIE,
             "O1-06 ; 2013 « non renseignée » (R-10, écart 14)")

    # Lignes de total : « TOTAL » (routes revêtues), « TOTAL RT » (routes en terre) ; les voiries n'ont qu'une ligne
    w = etat.pivot_table(index=["indicateur", "tronçon"], columns="etat", values="Value", aggfunc="first")
    etats = ["BON", "MOYEN", "MAUVAIS", "TRAVAUX"]
    total = w.index.get_level_values("tronçon").str.match(r"^TOTAL")
    routes = w.index.get_level_values("indicateur").str.startswith("ROUTES")
    troncons, totaux, voiries = w[routes & ~total], w[total], w[~routes]
    ecart = (troncons["TOTAL"] - troncons[etats].sum(axis=1)).abs().round(2)
    somme = troncons.groupby(level="indicateur")[etats + ["TOTAL"]].sum()
    ecart_total = (totaux.droplevel("tronçon")[etats + ["TOTAL"]] - somme).abs().round(2)
    sans_travaux = int(troncons["TRAVAUX"].isna().sum())
    par_type = troncons.groupby(level="indicateur").size()
    controle("4.1-05", "4.1", "État du réseau : bon + moyen + mauvais + travaux = total, et somme des tronçons = ligne de total",
             "etat_reseau_routier.csv",
             f"{len(troncons)} tronçons ({', '.join(f'{k.lower()} : {v}' for k, v in par_type.items())}), plus {len(voiries)} lignes de voiries "
             f"sans tronçon ; états = total pour {int((ecart <= ARRONDI).sum())} tronçons sur {len(troncons)} (écart max. {n(ecart.max(), 2)} km, arrondi) ; "
             f"« TRAVAUX » absent pour {sans_travaux} tronçons, dont les états publiés font le total ; "
             f"somme des tronçons = ligne de total ({', '.join(totaux.index.get_level_values('tronçon'))}) : écart max. {n(ecart_total.max().max(), 2)} km",
             CONFORME if (ecart <= ARRONDI).all() else ANOMALIE,
             "Lignes de total exclues des calculs (pas de double compte dans O3-01 à O3-03) ; un tronçon sans ligne « TRAVAUX » a 0 km en travaux, puisque ses états publiés font son total")

    e = annuaire("39.2")
    s = e.groupby(["Ligne", "Année"])["Valeur"].agg(["sum", "count"])
    hors = s[(s["sum"] - 100).abs() > 0.05]
    controle("4.1-06", "4.1", "Annuaire 39.2 : bon + moyen + mauvais + travaux = 100 %", "annuaire 2024, tableau 39.2",
             f"{len(s) - len(hors)} lignes sur {len(s)} ; "
             + " ; ".join(f"{l} {a} : {n(r['sum'], 2)} %" + (" (travaux non publiés)" if r["count"] < 4 else "")
                          for (l, a), r in hors.iterrows()),
             ANOMALIE if len(hors) else CONFORME, "Lecture de O3-07 en pourcentage, avec ces réserves")

    w = accidents.pivot(index="Date", columns="type", values="Value")
    morts_ok = (w["Nombre de morts"] < w["Nombre d’accidents"]).all()
    ratio = w["Nombre de blesses"] / w["Nombre d’accidents"]
    controle("4.1-07", "4.1", "Accidents : tués et blessés cohérents avec les accidents", "accidents_police_gendarmerie.csv",
             f"Aucune série d'accidents mortels publiée ; tués < accidents chaque année : {'oui' if morts_ok else 'non'} ; "
             f"blessés par accident : de {n(ratio.min(), 2)} ({ratio.idxmin()}) à {n(ratio.max(), 2)} ({ratio.idxmax()})",
             CONFORME if morts_ok else ANOMALIE, "O2-05 et O2-06 calculables ; « accidents mortels ≤ accidents » sans objet")

    a = pd.read_csv(BRUT / "auto_ecoles.csv", dtype=str)["agregation"].value_counts()
    controle("4.1-08", "4.1", "Auto-écoles : modalités du statut d'agrément", "auto_ecoles.csv",
             " ; ".join(f"{k} : {v}" for k, v in a.items()) + f" ; agréées et antennes agréées : {a.get('Agréée', 0) + a.get('Antenne agréée', 0)}",
             EXPLIQUE, "R-12 : décompte officiel = agréées + antennes agréées ; « Néant » transmis au 05")

    # Une cellule « - » est absente : elle compte pour rien dans une somme, sans devenir un 0 publié
    lues = livret[livret["Lecture"] == "colonnes"]
    w = lues.pivot_table(index=["Tableau", "Unité", "Groupe d’âges"], columns=["Milieu", "Sexe"], values="Valeur", aggfunc="first")
    v = lambda m, s: w[(m, s)].fillna(0)
    sexes = pd.concat([(v(m, "Hommes") + v(m, "Femmes") - v(m, "Ensemble")).rename(m) for m in ("Urbain", "Rural", "Total")], axis=1)
    milieux = pd.concat([(v("Urbain", s) + v("Rural", s) - v("Total", s)).rename(s) for s in ("Hommes", "Femmes", "Ensemble")], axis=1)
    hors_sexe = sexes[(sexes != 0).any(axis=1)]
    cle = ["Tableau", "Milieu", "Sexe"]
    est_total = livret["Groupe d’âges"] == "Total"
    ages = livret[~est_total].groupby(cle)["Valeur"].sum() - livret[est_total].groupby(cle)["Valeur"].sum()
    niveaux = livret.drop_duplicates("Unité").set_index("Unité")["Niveau"]
    lieux = sorted({u for _, u, _ in hors_sexe.index})
    prefectures = [u for u in lieux if niveaux[u] == "préfecture"]
    superieurs = [u for u in lieux if niveaux[u] != "préfecture"]
    controle("4.1-09", "4.1", "Livret 02 : hommes + femmes = ensemble, urbain + rural = total, somme des âges = total",
             "livret02_population_2022.csv",
             f"{len(w)} lignes lues en colonnes : {int((milieux != 0).sum().sum())} écart par milieu ; {len(hors_sexe)} lignes où hommes + femmes ≠ ensemble, "
             f"toutes de +1 en milieu rural ({', '.join(f'{u} {g}' for _, u, g in hors_sexe.index)}) : l'écart de {', '.join(prefectures)} est repris tel quel dans {', '.join(superieurs)} ; "
             f"somme des âges = total : {int((ages == 0).sum())} colonnes sur {len(ages)} ; "
             f"{livret[livret['Lecture'] != 'colonnes'].drop_duplicates(['Tableau', 'Groupe d’âges']).shape[0]} ligne reconstituée par les sommes, hors contrôle",
             CONFORME if hors_sexe.empty and (ages == 0).all() else ANOMALIE,
             "Livret 02 utilisable pour O1-07, O4-03 et PA-03 ; écarts d'une personne transmis au 05")

    o = pd.read_csv(INTERIM / "oms_profil_2023.csv")
    usagers = o[o["Indicateur"].str.startswith("Répartition")]["Valeur"].sum()
    v = o[o["Indicateur"] == "Véhicules immatriculés"].set_index("Modalité")["Valeur"]
    controle("4.1-10", "4.1", "Profil OMS : répartition des tués = 100 % ; catégories de véhicules = total", "oms_profil_2023.csv",
             f"Répartition : {n(usagers)} % ; catégories : {n(v.drop('Total').sum())} pour un total de {n(v['Total'])} (« Other » non publié)",
             EXPLIQUE, "O2-09 : part des tués par type d'usager, 2021, national (écart 3)")


# --- 4.2 Cohérence temporelle ------------------------------------------------------------------

def temporelle(p1, permis):
    registre = pd.read_csv(BRUT / "_SOURCES.csv", dtype=str).set_index("Fichier")
    declare = registre.loc["parc_immatricule_par_type_1.csv", "Couverture déclarée"]
    controle("4.2-01", "4.2", "Parc : années couvertes face à la couverture déclarée par le portail", "_SOURCES.csv ; parc_immatricule_par_type_1.csv",
             f"Déclarée : {declare} ; fichier : {p1['Date'].min()}–{p1['Date'].max()}", EXPLIQUE,
             "Période de O1 : 1990–2022 (fichier), prolongée par l'annuaire jusqu'en 2024")

    chrono = pd.read_csv(REFERENCE / "chronologie_reformes.csv", dtype=str)
    annees = set(chrono["Date"].str[:4].astype(int))
    w1 = p1.pivot(index="Date", columns="types-de-vehicule", values="Value")
    quatre = [c for c in w1.columns if c not in ("Total", "2 roues et assimilées")]
    wp = permis[permis["Value"] > 0].pivot(index="Date", columns="categories-de-permis", values="Value")
    series = {"parc, total": w1["Total"], "parc, 4 roues et plus": w1[quatre].sum(axis=1),
              "parc, 2 roues": w1["2 roues et assimilées"], "permis, total": wp["Total"], "permis, moto (A)": wp["Moto (A)"]}
    textes = []
    for nom, s in series.items():
        s = s.dropna()
        var = {an: 100 * (s[an] / s[an - 1] - 1) for an in s.index if an - 1 in s.index}
        haut = sorted(var.items(), key=lambda kv: -abs(kv[1]))[:3]
        textes.append(f"{nom} : " + ", ".join(f"{an}{'*' if an in annees else ''} ({'+' if v > 0 else '−'}{n(abs(v))} %)" for an, v in haut))
    controle("4.2-02", "4.2", "Ruptures de série : les trois plus fortes variations annuelles (* année de la chronologie)",
             "parc_immatricule_par_type_1.csv ; permis_par_categorie.csv ; chronologie_reformes.csv", " ; ".join(textes), ANOMALIE,
             "Ruptures annotées sur les graphiques de O1, sans lecture causale (H1) ; registre au 05")

    t = annuaire("40.4")
    controle("4.2-03", "4.2", "Permis : sous-catégories A1 à A3", "permis_par_categorie.csv ; annuaire 2024, tableau 40.4",
             f"Portail (2007–2022) : catégories {', '.join(sorted(permis['categories-de-permis'].unique()))} ; "
             f"annuaire ({t.columns.min()}–{t.columns.max()}) : {', '.join(t.index)}", CONFORME,
             "O1-06 et O1-09 sur les catégories A à F ; aucune sous-catégorie publiée")

    p10 = portail("population_region_sexe_2010.csv")
    total10 = p10[(p10["région"] == "Togo") & (p10["sexe"] == "Total")]["Value"].iloc[0]
    controle("4.2-04", "4.2", "Population 2010 : libellé « population résidente en 2022 »", "population_region_sexe_2010.csv",
             f"Libellé : « {p10['indicateur'].iloc[0]} » ; années du fichier : {', '.join(map(str, p10['Date'].unique()))} ; "
             f"total : {n(total10)}, contre {n(8095498)} au recensement de 2022", EXPLIQUE,
             "Le fichier est le recensement de 2010 : libellé erroné, année réelle 2010")

    catalogue = json.loads((BRUT / "geoportail_catalogue.json").read_text(encoding="utf-8"))
    couches = {c["nom"]: c.get("source_collecte", "") for c in catalogue["couches"]}
    controle("4.2-05", "4.2", "Millésimes des données territoriales face à l'année de référence 2022 (R-05)",
             "_SOURCES.csv ; geoportail_catalogue.json ; annuaire 2024",
             f"État du réseau : {registre.loc['etat_reseau_routier.csv', 'Couverture déclarée']} (portail), 2020–2022 en % (annuaire 39.2) ; "
             f"routes classées : {couches.get('Routes - Routes classées')} ; auto-écoles : {couches.get('Entreprises - Auto-écoles')} ; "
             f"population : 2022 (recensement)", EXPLIQUE,
             "Croisements de 2022 légitimes pour les routes et les auto-écoles (collecte 2021-2022) ; état par tronçon : relevé de 2020, daté comme tel")


# --- 4.3 Cohérence géographique (hors contrôles spatiaux, faits au §5) ---------------------------

def geographique(rgph, livret, ehcvm):
    valeur = rgph.groupby("découpage-administratif")["Value"].max()
    zones = valeur[ZONES_RECENSEMENT].sum()
    t = livret[(livret["Groupe d’âges"] == "Total") & (livret["Milieu"] == "Total") & (livret["Sexe"] == "Ensemble")].set_index("Tableau")["Valeur"]
    controle("4.3-01", "4.3", "« Maritime » avec ou sans le Grand Lomé ; somme des zones = total national",
             "rgph_2022_population.csv ; livret02_population_2022.csv",
             f"Recensement CSV : « MARITIME » = {n(valeur['MARITIME'])}, hors Grand Lomé (« DAGL » = {n(valeur['DAGL'])}) ; "
             f"6 zones = {n(zones)}, TOGO = {n(valeur['TOGO'])}. Livret 02 : tableaux 3 à 8 = {n(t[[3, 4, 5, 6, 7, 8]].sum())}, "
             f"pays = {n(t[1])} ; Maritime avec Grand Lomé (tableau 2) = {n(t[2])}, tableaux 3 + 4 = {n(t[3] + t[4])}",
             CONFORME if zones == valeur["TOGO"] and t[[3, 4, 5, 6, 7, 8]].sum() == t[1] and t[2] == t[3] + t[4] else ANOMALIE,
             "Lecture en 6 zones (R-02, R-03) : « MARITIME » du recensement = Maritime hors Grand Lomé")

    p10 = portail("population_region_sexe_2010.csv")
    p10 = p10[p10["sexe"] == "Total"].set_index("région")["Value"]
    controle("4.3-02", "4.3", "Population 2010 : somme des zones = total national", "population_region_sexe_2010.csv",
             f"Zones : {', '.join(z for z in p10.index if z != 'Togo')} ; somme = {n(p10.drop('Togo').sum())}, Togo = {n(p10['Togo'])}",
             CONFORME if p10.drop("Togo").sum() == p10["Togo"] else ANOMALIE, "« Lomé Commune » publiée à part de la Maritime")

    dhs = json.loads((BRUT / "dhs_possession_moto_velo_region.json").read_text(encoding="utf-8"))["Data"]
    codes = sorted(ehcvm["pond"]["s00q01"].unique())
    controle("4.3-03", "4.3", "Enquêtes : zones présentes et sens de « Maritime »", "ehcvm_2021_2022_csv.zip ; dhs_possession_moto_velo_region.json",
             f"EHCVM : codes de zone {', '.join(map(str, codes))} ({', '.join(EHCVM_ZONES[c] for c in codes)}) ; "
             f"DHS : {', '.join(sorted({d['CharacteristicLabel'] for d in dhs}))}",
             CONFORME if codes == list(EHCVM_ZONES) else ANOMALIE,
             "EHCVM lue en 6 zones ; DHS : « Ensemble Maritime » contient Lomé, « ..Maritime » l'exclut")

    textes = []
    for fichier in ("routes_classees.csv", "auto_ecoles.csv"):
        d = pd.read_csv(BRUT / fichier, dtype=str, usecols=["region_nom_bdd", "prefecture_nom_bdd"])
        textes.append(f"{fichier} : « Maritime » contient {', '.join(sorted(d[d['region_nom_bdd'] == 'Maritime']['prefecture_nom_bdd'].unique()))}")
    controle("4.3-04", "4.3", "Routes et auto-écoles : « Maritime » avec ou sans le Grand Lomé", "routes_classees.csv ; auto_ecoles.csv",
             " ; ".join(textes), EXPLIQUE, "« Maritime » y inclut le Grand Lomé (Golfe, Agoè-Nyivé) : zone lue par la préfecture, jamais par ce libellé")


# --- 4.4 Cohérence entre sources ---------------------------------------------------------------

def entre_sources(p1, p2, cles, permis, accidents, ehcvm):
    t1, t2, t3 = annuaire("40.1"), annuaire("40.2"), annuaire("40.3")
    quatre_ann = t1.loc[["Autocar/Autobus", "Camions", "Camionnette", "Semi-remorque", "Tracteur", "Voiture"]].sum()
    egales = [an for an in t2.columns if quatre_ann[an] == t2.loc["Total", an]]
    deux_trois = t1.loc["2 Roues"] + t1.loc["3 Roues"]
    egales23 = [an for an in t3.columns if deux_trois[an] == t3.loc["Total", an]]
    autres = [an for an in t3.columns if an not in egales23]
    controle("4.4-01", "4.4", "Stock ou flux : le « parc immatriculé » face aux premières mises en circulation", "annuaire 2024, tableaux 40.1 à 40.3",
             f"4 roues et plus du parc (40.1) = premières mises en circulation, neufs et occasions (40.2) : {len(egales)} années sur {len(t2.columns)} "
             f"({', '.join(f'{an} : {n(quatre_ann[an])}' for an in t2.columns)}) ; 2 roues + 3 roues (40.1) = deux-roues par centre (40.3) : "
             f"{len(egales23)} années sur {len(t3.columns)}"
             + "".join(f" ({an} : {n(deux_trois[an])} contre {n(t3.loc['Total', an])} ; 2 roues {n(t1.loc['2 Roues', an])}, 3 roues {n(t1.loc['3 Roues', an])})" for an in autres)
             + f" ; total du parc : {', '.join(f'{an} : {n(v)}' for an, v in t1.loc['Total'].items())}",
             CONFORME if len(egales) == len(t2.columns) else ANOMALIE,
             "Le « parc immatriculé » est un flux : les immatriculations de l'année. O1-01 lit la série ; O2-04 suit R-11 jusqu'au cumul (PA-01, C) ; écart 16")

    w1 = p1.pivot(index="Date", columns="types-de-vehicule", values="Value")
    quatre = w1[[c for c in w1.columns if c not in ("Total", "2 roues et assimilées")]].sum(axis=1)
    c4 = serie(cles, "indicateur", "Evolution du parc automobile 4 roues et plus immatriculé")
    c2 = serie(cles, "indicateur", "Evolution des deux roues et assimilées immatriculées")
    communes4, diff4 = egalite(quatre, c4)
    communes2, diff2 = egalite(w1["2 roues et assimilées"], c2)
    ecart_ann = {an: int(t1.loc["Total", an] - w1.loc[an, "Total"]) for an in t1.columns if an in w1.index}
    w2 = p2.pivot(index="Date", columns="automobile", values="Value")
    communes_f2, diff_f2 = egalite(quatre, w2["Total 4 Roues"])
    communes_f22, diff_f22 = egalite(w1["2 roues et assimilées"], w2["Total 2 Roues"])
    controle("4.4-02", "4.4", "Parc : fichier 1 face aux statistiques clés, au fichier 2 et à l'annuaire", "parc 1 et 2 ; transports_statistiques_cles.csv ; annuaire 40.1",
             f"4 roues : égal aux statistiques clés {len(communes4) - len(diff4)}/{len(communes4)} années, au fichier 2 {len(communes_f2) - len(diff_f2)}/{len(communes_f2)} ; "
             f"2 roues : égal aux statistiques clés {len(communes2) - len(diff2)}/{len(communes2)}, au fichier 2 {len(communes_f22) - len(diff_f22)}/{len(communes_f22)} ; "
             f"annuaire moins portail (total) : {', '.join(f'{an} : {e}' for an, e in ecart_ann.items())}, soit les « 4 roues moto » "
             f"({', '.join(n(t1.loc['4 Roues moto', an]) for an in ecart_ann)})",
             CONFORME if not diff4 and not diff2 else ANOMALIE,
             "Une seule série, sans assemblage de sources ; le portail exclut les « 4 roues moto »")

    pm = serie(cles, "indicateur", "Evolution des premières mise en circulation du parc automobile 4 roues et plus immatriculés")
    communes, diff = egalite(pm, t2.loc["Neufs"])
    controle("4.4-03", "4.4", "« Premières mises en circulation » des statistiques clés face à l'annuaire", "transports_statistiques_cles.csv ; annuaire 40.2",
             f"Égales aux seuls véhicules neufs (40.2) : {len(communes) - len(diff)} années sur {len(communes)} "
             f"({', '.join(f'{an} : {n(pm[an])}' for an in communes)})",
             EXPLIQUE if not diff else ANOMALIE, "Libellé trompeur : la série des statistiques clés ne compte que les véhicules neufs")

    o = pd.read_csv(INTERIM / "oms_profil_2023.csv")
    v = o[o["Indicateur"] == "Véhicules immatriculés"].set_index("Modalité")["Valeur"]
    an = int(o[o["Indicateur"] == "Véhicules immatriculés"]["Année"].iloc[0])
    dtrf = {"Total": w1.loc[an, "Total"], "Véhicules à 4 roues": w1.loc[an, "Voitues"],
            "Deux et trois-roues motorisés": w1.loc[an, "2 roues et assimilées"],
            "Poids lourds": w1.loc[an, "Camions"], "Bus": w1.loc[an, "Autocars/Autobus"]}
    egal = [k for k in dtrf if dtrf[k] == v[k]]
    controle("4.4-04", "4.4", f"Véhicules immatriculés selon l'OMS ({an}) face au parc publié", "oms_profil_2023.csv ; parc_immatricule_par_type_1.csv",
             f"{len(egal)} valeurs sur {len(dtrf)} identiques aux immatriculations de {an} : total {n(v['Total'])} ; « 4 roues » de l'OMS = voitures "
             f"({n(v['Véhicules à 4 roues'])}) ; deux et trois-roues {n(v['Deux et trois-roues motorisés'])} ; poids lourds = camions ; bus = autocars",
             EXPLIQUE if len(egal) == len(dtrf) else ANOMALIE,
             "Même comptage de la DTRF : l'OMS ne confirme rien de façon indépendante, et ses « véhicules immatriculés » sont aussi un flux")

    serie_acc = accidents.pivot(index="Date", columns="type", values="Value")
    bilan = portail("accidents_bilan_police_gendarmerie.csv").pivot(index="Date", columns="type", values="Value")
    noms = {"Nombre de cas d'accidents de la circulation": "Nombre d’accidents", "Nombre de morts": "Nombre de morts", "Nombre de blessés": "Nombre de blesses"}
    cles_acc = cles[cles["indicateur"].isin(noms)].assign(type=lambda d: d["indicateur"].map(noms)).pivot(index="Date", columns="type", values="Value")
    t72 = annuaire("7.2").T
    def identiques(a, b):
        communes = a.index.intersection(b.index)
        return int((a.loc[communes] == b.loc[communes, a.columns]).all(axis=1).sum()), len(communes)
    i1, c1 = identiques(bilan, serie_acc)
    i2, c2_ = identiques(cles_acc[serie_acc.columns], serie_acc)
    i3, c3 = identiques(serie_acc, t72[serie_acc.columns])
    tues = o[o["Indicateur"] == "Tués déclarés"].iloc[0]
    controle("4.4-05", "4.4", "Accidents : trois séries du portail et annuaire ; 2022 face à l'énoncé", "accidents (2 fichiers) ; statistiques clés ; annuaire 7.2 ; profil OMS",
             f"Bilan = série 2014–2022 : {i1}/{c1} années ; statistiques clés (2010–2022) = série : {i2}/{c2_} ; annuaire (2020–2024) = série : {i3}/{c3} ; "
             f"2022 : {n(serie_acc.loc[2022, 'Nombre d’accidents'])} accidents, {n(serie_acc.loc[2022, 'Nombre de morts'])} tués (énoncé : plus de 7 500 et 683) ; "
             f"OMS : {n(tues['Valeur'])} tués déclarés en {int(tues['Année'])}, série : {n(serie_acc.loc[int(tues['Année']), 'Nombre de morts'])}",
             CONFORME if i1 == c1 and i2 == c2_ and i3 == c3 else ANOMALIE,
             "Une seule série de référence pour O2-01 : 2010–2024 (statistiques clés, puis annuaire) ; aucune source ne dit les accidents « corporels » (écart 15)")

    proj = portail("projections_demographiques_2011_2031.csv")
    proj = proj[(proj["tranche-d-âges"] == "Togo") & (proj["sexe"] == "Total")].set_index("Date")["Value"]
    taux = serie(cles, "indicateur", "Accidents mortels /100.000 hab")
    acc = serie(cles, "indicateur", "Nombre de cas d'accidents de la circulation")
    tues_c = serie(cles, "indicateur", "Nombre de morts")
    implicite = (acc / taux * 1e5).round()
    ecarts = {an: abs(implicite[an] / proj[an] - 1) for an in implicite.index if an in proj.index and an != 2022}
    controle("4.4-06", "4.4", "« Accidents mortels /100 000 hab » : quel numérateur, quelle population ?", "transports_statistiques_cles.csv ; projections ; recensements",
             f"Accidents ÷ indicateur × 100 000 = projection de l'INSEED de 2011 à 2021 (écart max. {n(100 * max(ecarts.values()), 2)} %) ; "
             f"2022 : {n(implicite[2022])} (recensement : {n(8095498)}) ; 2010 : {n(implicite[2010])}, soit la projection de 2011 ({n(proj[2011])}), "
             f"et non le recensement de 2010 ({n(6191155)}). Avec les tués au numérateur, la population serait de {n((tues_c / taux * 1e5).min())} "
             f"à {n((tues_c / taux * 1e5).max())} habitants",
             ANOMALIE, "Indicateur mal nommé : accidents constatés pour 100 000 habitants ; non repris, O2-03 est recalculé (B) ; anomalie de 2010 au 05")

    rec = portail("rgph_2022_population.csv")
    togo22 = rec[rec["découpage-administratif"] == "TOGO"]["Value"].iloc[0]
    controle("4.4-07", "4.4", "Projections et recensement en 2022", "projections_demographiques_2011_2031.csv ; rgph_2022_population.csv",
             f"Projection 2022 : {n(proj[2022])} ; recensement : {n(togo22)} ; écart : {pct(togo22, proj[2022], 2)}", EXPLIQUE,
             "2022 : recensement (A) ; 2011–2021 : projections (C) ; la série a un saut de 0,3 % en 2022 (R-06)")

    wpp = pd.read_csv(BRUT / "wpp2024_population_age_simple_togo.csv", sep="|", skiprows=1)
    wpp = wpp[(wpp["Variant"] == "Median") & (wpp["Sex"] == "Both sexes")].groupby("TimeLabel")["Value"].sum()
    p10 = portail("population_region_sexe_2010.csv")
    togo10 = p10[(p10["région"] == "Togo") & (p10["sexe"] == "Total")]["Value"].iloc[0]
    controle("4.4-08", "4.4", "WPP (variante Median) face à l'INSEED", "wpp2024_population_age_simple_togo.csv ; recensements 2010 et 2022",
             f"2010 : WPP {n(wpp[2010])}, recensement {n(togo10)}, écart {pct(wpp[2010], togo10)} ; "
             f"2022 : WPP {n(wpp[2022])}, recensement {n(togo22)}, écart {pct(wpp[2022], togo22)} "
             f"(face à la projection de l'INSEED : {pct(wpp[2022], proj[2022])}) ; "
             f"population retenue par le profil OMS : {n(o[o['Indicateur'] == 'Population retenue par l’OMS']['Valeur'].iloc[0])}",
             EXPLIQUE, "WPP ne sert qu'aux parts par âge et aux taux de croissance avant 2010 (C) ; jamais à un niveau de population")

    wp = permis.pivot(index="Date", columns="categories-de-permis", values="Value")
    t4 = annuaire("40.4")
    correspond = {"Moto (A)": "Moto", "Voiture légèr (B)": "Voiture légère", "Poids lourd (C)": "Poids lourd",
                  "Transport en commun (D)": "Transport en commun", "Semi-remorque (E)": "Semi-remorque",
                  "Voiture spéciale (F)": "Voiture spéciale (F)", "Total": "Total"}
    communes = [an for an in t4.columns if an in wp.index]
    identiques_p = sum(all(wp.loc[an, k] == t4.loc[v, an] for k, v in correspond.items()) for an in communes)
    controle("4.4-09", "4.4", "Permis : portail face à l'annuaire", "permis_par_categorie.csv ; annuaire 40.4",
             f"{identiques_p} années sur {len(communes)} identiques ({communes[0]}–{communes[-1]}) ; l'annuaire ajoute "
             f"{', '.join(str(an) for an in t4.columns if an not in wp.index)}",
             CONFORME if identiques_p == len(communes) else ANOMALIE, "O1-06 : 2007–2024, 2013 non renseignée")

    menages = ehcvm["pond"]
    avec12 = ehcvm["s12"][["grappe", "menage"]].drop_duplicates()
    rempli = menages.merge(avec12, on=["grappe", "menage"])
    motos = ehcvm["s12"][ehcvm["s12"]["s12q01"] == EHCVM_MOTO].merge(menages, on=["grappe", "menage"])
    part = motos["poids"].sum() / rempli["poids"].sum()
    nb_motos = (motos["poids"] * motos["s12q03"]).sum()
    deux = w1["2 roues et assimilées"]
    cumul = {k: deux.loc[2021 - k + 1:2021].sum() for k in PA01_MOTOS}
    controle("4.4-10", "4.4", "Motos des ménages (EHCVM 2021-2022) face aux deux-roues immatriculés", "ehcvm_2021_2022_csv.zip ; parc_immatricule_par_type_1.csv",
             f"Ménages avec au moins une moto : {n(100 * part, 1)} % des ménages qui ont rempli la section ; motos possédées (pondéré) : {n(nb_motos)} ; "
             f"deux-roues immatriculés en cumul jusqu'en 2021, sur la durée de vie PA-01 : {n(cumul[PA01_MOTOS[0]])} sur {PA01_MOTOS[0]} ans "
             f"[{n(cumul[PA01_MOTOS[1]])} sur {PA01_MOTOS[1]} ans ; {n(cumul[PA01_MOTOS[2]])} sur {PA01_MOTOS[2]} ans] ; "
             f"rapport : {n(nb_motos / cumul[PA01_MOTOS[0]], 1)} [{n(nb_motos / cumul[PA01_MOTOS[2]], 1)} – {n(nb_motos / cumul[PA01_MOTOS[1]], 1)}]",
             EXPLIQUE, "Ordre de grandeur du piège « motos non immatriculées », étiqueté C ; jamais une correction du parc")

    routes = pd.read_csv(BRUT / "routes_classees.csv", dtype=str, usecols=["route_type", "geometry"])
    geo = gpd.GeoSeries.from_wkt(routes["geometry"], crs=4326).to_crs(UTM31N)
    km = (geo.length / 1000).groupby(routes["route_type"]).sum()
    with zipfile.ZipFile(BRUT / "limites_administratives_hdx.geojson.zip") as z:
        pays = gpd.read_file(z.open("tgo_admin0.geojson")).to_crs(UTM31N)
    surface = pays.area.sum() / 1e6
    densite = portail("densite_reseau_routier.csv").set_index("types-de-routes")["Value"]
    etat = portail("etat_reseau_routier.csv")
    etat_total = etat[etat["tronçon"].str.match(r"^(TOTAL|VOIRIES)") & (etat["etat"] == "TOTAL")].set_index("indicateur")["Value"]
    publie = {"Route nationale revêtue": (densite["Routes Revêtues"], etat_total["ROUTES REVETUES"]),
              "Route nationale non revêtue": (densite["Routes en  Terre"], etat_total["ROUTES EN TERRES"]),
              "Voirie urbaine": (densite["Voiries urbaines"], etat_total["VOIRIES REVETUES"] + etat_total["VOIRIES EN TERRES"])}
    controle("4.4-11", "4.4", "Longueur des routes classées, calculée (UTM 31N), face à la densité et à l'état du réseau publiés",
             "routes_classees.csv ; limites HDX ; densite_reseau_routier.csv ; etat_reseau_routier.csv",
             f"Surface du Togo (HDX, UTM 31N) : {n(surface)} km². "
             + " ; ".join(f"{t} : tracé {n(km[t])} km, densité × surface {n(d * surface / 100)} km ({pct(km[t], d * surface / 100)}), "
                          f"état du réseau {n(e)} km ({pct(km[t], e)})" for t, (d, e) in publie.items())
             + f" ; pistes rurales : tracé {n(km['Piste rurale'])} km, sans équivalent publié",
             EXPLIQUE, "Sources de dates (état : 2020 ; tracé : collecte 2021-2022) et de périmètres différents, les voiries surtout : "
                       "O4-01 et O4-02 sont calculés sur le tracé (B) ; densité et état publiés en contrôle seulement")

    paves_oms = o[o["Indicateur"] == "Kilomètres revêtus"]
    controle("4.4-12", "4.4", "Kilomètres revêtus selon l'OMS face au réseau revêtu", "oms_profil_2023.csv ; routes_classees.csv ; etat_reseau_routier.csv",
             f"OMS : {n(paves_oms['Valeur'].iloc[0])} km revêtus en {int(paves_oms['Année'].iloc[0])} ; routes nationales revêtues : tracé {n(km['Route nationale revêtue'])} km, "
             f"état du réseau {n(etat_total['ROUTES REVETUES'])} km ; rapport : {n(paves_oms['Valeur'].iloc[0] / km['Route nationale revêtue'], 1)}",
             ANOMALIE, "Chiffre de l'OMS sans définition ni périmètre : jamais utilisé")


# --- 4.5 Contrôle des totaux -------------------------------------------------------------------

def totaux(rgph, livret, ehcvm):
    ref = pd.read_csv(REFERENCE / "referentiel_prefectures.csv", dtype=str)
    t = livret[(livret["Groupe d’âges"] == "Total") & (livret["Milieu"] == "Total") & (livret["Sexe"] == "Ensemble")]
    pref = t[t["Niveau"] == "préfecture"].set_index("Unité")["Valeur"]
    zones_livret = t[t["Niveau"] != "préfecture"].set_index("Unité")["Valeur"]
    ref["Livret"] = ref["Nom Livret 02 (D7)"].map(pref)
    par_zone = ref.groupby("Zone")["Livret"].sum()
    ecarts = {z: par_zone[z] - zones_livret[ZONES_LIVRET[z]] for z in ZONES_LIVRET}
    controle("4.5-01", "4.5", "Livret 02 : préfectures → zones → pays", "livret02_population_2022.csv ; referentiel_prefectures.csv",
             f"{int(ref['Livret'].notna().sum())} préfectures sur 39 lues ; somme par zone = tableau de zone : "
             f"{sum(1 for e in ecarts.values() if e == 0)} zones sur 6 ; somme des préfectures : {n(ref['Livret'].sum())}, pays : {n(zones_livret['Togo'])}",
             CONFORME if all(e == 0 for e in ecarts.values()) and ref["Livret"].sum() == zones_livret["Togo"] else ANOMALIE,
             "Population 2022 par préfecture : Livret 02 (A), dénominateur de O4-03, O4-05, O5-03")

    # Libellé de préfecture dans le recensement CSV : en cas de doublon, la préfecture est la plus peuplée
    valeur = rgph.groupby("découpage-administratif")["Value"].max()
    doublons = rgph["découpage-administratif"].value_counts()
    ref["CSV"] = ref["Nom recensement CSV (D7)"].map(valeur)
    differences = ref[ref["CSV"] != ref["Livret"]]
    controle("4.5-02", "4.5", "Livret 02 face au recensement CSV, préfecture par préfecture", "livret02_population_2022.csv ; rgph_2022_population.csv",
             f"{39 - len(differences)} préfectures sur 39 identiques"
             + (f" ; écarts : {', '.join(f'{r.Préfecture} ({n(r.CSV - r.Livret)})' for r in differences.itertuples())}" if len(differences) else "")
             + f" ; libellés de préfecture en double dans le CSV : {int((doublons[ref['Nom recensement CSV (D7)']] > 1).sum())}, résolus par la valeur la plus élevée",
             CONFORME if differences.empty else ANOMALIE, "Les deux sources se valent pour 2022 ; le Livret 02 ajoute l'âge, le sexe et le milieu")

    zones = valeur[ZONES_RECENSEMENT]
    somme_pref = ref["CSV"].sum()
    controle("4.5-03", "4.5", "Recensement CSV : niveaux sans code ; totaux par niveau", "rgph_2022_population.csv ; referentiel_prefectures.csv",
             f"{rgph['découpage-administratif'].nunique()} libellés pour {len(rgph)} lignes ; 6 zones = {n(zones.sum())} ; "
             f"39 préfectures = {n(somme_pref)} ; TOGO = {n(valeur['TOGO'])}",
             CONFORME if zones.sum() == somme_pref == valeur["TOGO"] else ANOMALIE,
             "Préfectures lues par le référentiel (R-01), jamais par la position dans le fichier")

    pond, welfare = ehcvm["pond"], ehcvm["welfare"]
    m = pond.merge(welfare, on=["grappe", "menage"])
    population = (m["poids"] * m["hhsize"]).sum()
    parts = (m.assign(p=m["poids"] * m["hhsize"]).groupby("s00q01")["p"].sum() / population).rename(index=EHCVM_ZONES)
    livret_zones = pd.Series({z: zones_livret[ZONES_LIVRET[z]] for z in ZONES_LIVRET}) / zones_livret["Togo"]
    ecart_parts = (parts - livret_zones).abs()
    controle("4.5-04", "4.5", "EHCVM : pondérations, population pondérée et parts des 6 zones", "ehcvm_2021_2022_csv.zip ; livret02_population_2022.csv",
             f"{len(pond)} ménages ; poids = hhweight : {'oui' if (m['poids'] - m['hhweight']).abs().max() < 1e-6 else 'non'} ; "
             f"somme des poids : {n(pond['poids'].sum())} ménages ; population pondérée : {n(population)}, recensement 2022 : {n(zones_livret['Togo'])} "
             f"({pct(population, zones_livret['Togo'])}) ; parts des zones : écart max. {n(100 * ecart_parts.max(), 1)} point ({ecart_parts.idxmax()})",
             EXPLIQUE, "Parts par zone utilisables en contexte (C) ; jamais un effectif")

    s12, s09b, menage = ehcvm["s12"], ehcvm["s09b"], ehcvm["menage"]
    cle = ["grappe", "menage"]
    sans12 = pond.merge(s12[cle].drop_duplicates(), on=cle, how="left", indicator=True)
    sans12 = sans12[sans12["_merge"] == "left_only"]
    sans09 = pond.merge(s09b[cle].drop_duplicates(), on=cle, how="left", indicator=True)
    sans09 = sans09[sans09["_merge"] == "left_only"]
    lignes_moto = s12[s12["s12q01"] == EHCVM_MOTO][cle].drop_duplicates()
    agr = menage.merge(sans12[cle], on=cle, how="inner")
    controle("4.5-05", "4.5", "EHCVM : ligne absente = « non » ou « non renseigné » ?", "ehcvm_2021_2022_csv.zip",
             f"Ménages ayant une ligne « moto » : {len(lignes_moto)} ; agrégat `moto` > 0 du producteur : {int((menage['moto'] > 0).sum())} ; "
             f"ménages sans aucune ligne en section 12 (biens) : {len(sans12)} ({n(100 * sans12['poids'].sum() / pond['poids'].sum(), 1)} % pondéré), "
             f"dont `moto` vide : {int(agr['moto'].isna().sum())} et `car` vide : {int(agr['car'].isna().sum())} ; "
             f"sans aucune ligne en section 9B (achats des 7 derniers jours) : {len(sans09)}",
             EXPLIQUE, "Ligne absente = « non » si la section est remplie, « non renseigné » sinon (R-10) ; agrégats du producteur non utilisés")


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    p1, p2 = portail("parc_immatricule_par_type_1.csv"), portail("parc_immatricule_par_type_2.csv")
    cles, permis = portail("transports_statistiques_cles.csv"), portail("permis_par_categorie.csv")
    etat, accidents = portail("etat_reseau_routier.csv"), portail("accidents_police_gendarmerie.csv")
    rgph = portail("rgph_2022_population.csv")
    livret = pd.read_csv(INTERIM / "livret02_population_2022.csv")
    ehcvm = lire_ehcvm()

    interne(p1, p2, permis, etat, accidents, livret)
    temporelle(p1, permis)
    geographique(rgph, livret, ehcvm)
    entre_sources(p1, p2, cles, permis, accidents, ehcvm)
    totaux(rgph, livret, ehcvm)

    df = pd.DataFrame(controles)
    df.to_csv(SORTIE / "controles_coherence.csv", index=False)
    print(f"{len(df)} contrôles : " + ", ".join(f"{k} {v}" for k, v in df["Résultat"].value_counts().items()))


if __name__ == "__main__":
    main()
