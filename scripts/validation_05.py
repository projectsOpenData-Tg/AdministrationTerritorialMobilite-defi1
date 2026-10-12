"""Étape 05 : validation du nettoyage et des jointures (05_data_preparation.md, §7).

Recontrôle les tables de data/processed/ à partir de data/raw/ (et des tableaux extraits des PDF par
le 04), sans reprendre le code de nettoyage_05.py ni de jointures_05.py : un script ne valide pas sa
propre sortie.

Sortie : data/analysis/05_preparation/controles_05.csv, une ligne par contrôle (mesure, résultat,
bloquant ou non). Un contrôle bloquant en échec arrête la chaîne : le script sort avec le code 1.

Usage : .venv/bin/python scripts/validation_05.py
"""
import io
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
REFERENCE = RACINE / "data" / "reference"
INTERIM = RACINE / "data" / "interim"
TRAITE = RACINE / "data" / "processed"
ANALYSE = RACINE / "data" / "analysis" / "05_preparation"

UTM31N = 32631
TOLERANCE_KM = 0.05  # arrondis des km répartis (3 décimales par ligne)
CONFORME, ECHEC = "conforme", "échec"
ANNEES_NUMERIQUES = ["D1_immatriculations", "D1_parc_estime", "D2_permis", "D3_accidents", "D3_victimes_usager_2021",
                     "D4_etat_national_pct", "D7_population_nationale", "D7_population_age_nationale",
                     "D7_population_age_conduire", "D9_repere_oms", "D10_trafic", "D12_dhs_region", "contexte_entretien",
                     "D7_population_prefecture_2022"]

controles = []


def controle(ident, intitule, attendu, mesure, ok, bloquant=False):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC, "Bloquant": "oui" if bloquant else "non"})


def n(x, decimales=0):
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def lire(nom):
    return pd.read_csv(TRAITE / f"{nom}.csv")


def portail(fichier):
    d = pd.read_csv(BRUT / fichier, dtype=str)
    d["Value"], d["Date"] = pd.to_numeric(d["Value"]), pd.to_numeric(d["Date"])
    return d


def annuaire(numero):
    a = pd.read_csv(INTERIM / "annuaire2024_tableaux.csv")
    return a[a["Tableau"].astype(str) == numero]


# --- Lignes avant et après -----------------------------------------------------------------------

def lignes():
    l = pd.read_csv(ANALYSE / "lignes_05.csv")
    equilibre = (l["Lignes brutes"] == l["Lignes gardées"] + l["Lignes retirées"]).all()
    bruts = {f: len(pd.read_csv(BRUT / f, dtype=str)) for f in l["Fichier"] if (BRUT / f).exists()}
    recompte = all(l.set_index("Fichier").loc[f, "Lignes brutes"] == k for f, k in bruts.items())
    controle("7-01", "Lignes avant et après, par fichier", "Brutes = gardées + retirées, chaque retrait avec son motif ; lignes brutes recomptées",
             f"{len(l)} fichiers ; équilibre : {'oui' if equilibre else 'non'} ; {len(bruts)} fichiers bruts recomptés, identiques : {'oui' if recompte else 'non'} ; "
             f"retirées : {int(l['Lignes retirées'].sum())}, toutes avec un motif : {'oui' if (l.loc[l['Lignes retirées'] > 0, 'Motifs'] != 'aucun').all() else 'non'}",
             equilibre and recompte and (l.loc[l["Lignes retirées"] > 0, "Motifs"] != "aucun").all())

    attendu = {"D1_immatriculations": 7 * 35, "D2_permis": 6 * 18, "D3_accidents": 3 * 15, "D4_etat_troncons": 84,
               "D5_trace_prefecture": 39 * 4, "D6_auto_ecoles": 272, "table_maitresse_prefecture": 39}
    obtenu = {k: len(lire(k)) for k in attendu}
    controle("7-02", "Lignes des tables produites", "Types × années, tronçons, établissements, préfectures attendus",
             " ; ".join(f"{k} : {obtenu[k]} (attendu {v})" for k, v in attendu.items()), obtenu == attendu)


# --- Totaux conservés ------------------------------------------------------------------------------------

def totaux():
    d1 = lire("D1_immatriculations")
    p = portail("parc_immatricule_par_type_1.csv")
    total = p[p["types-de-vehicule"] == "Total"].set_index("Date")["Value"]
    a = annuaire("40.1").pivot(index="Ligne", columns="Année", values="Valeur")
    attendu = pd.concat([total, (a.loc["Total"] - a.loc["4 Roues moto"])[[2023, 2024]]])
    somme = d1.groupby("Année")["Immatriculations"].sum()
    ok1 = somme.reindex(attendu.index).eq(attendu).all() and len(somme) == len(attendu)
    controle("7-03", "D1 : totaux conservés", "Somme des types = total publié, chaque année (annuaire : sans les « 4 roues moto »)",
             f"{int(somme.reindex(attendu.index).eq(attendu).sum())} années sur {len(attendu)}", ok1)

    d2 = lire("D2_permis")
    p = portail("permis_par_categorie.csv")
    total = p[p["categories-de-permis"] == "Total"].set_index("Date")["Value"]
    a = annuaire("40.4").pivot(index="Ligne", columns="Année", values="Valeur").loc["Total"][[2023, 2024]]
    attendu = pd.concat([total.drop(index=2013), a])
    somme = d2.groupby("Année")["Permis délivrés"].sum(min_count=1)
    vide = d2[d2["Année"] == 2013]["Permis délivrés"]
    ok2 = somme.reindex(attendu.index).eq(attendu).all() and vide.isna().all() and len(vide) == 6
    controle("7-04", "D2 : totaux conservés", "Somme des catégories = total publié, chaque année ; 2013 vide",
             f"{int(somme.reindex(attendu.index).eq(attendu).sum())} années sur {len(attendu)} ; 2013 : {int(vide.isna().sum())} catégories vides sur {len(vide)}, aucune à 0",
             ok2)

    d3 = lire("D3_accidents").set_index(["Mesure", "Année"])["Valeur"]
    cles = portail("transports_statistiques_cles.csv")
    noms = {"Nombre de cas d'accidents de la circulation": "Accidents constatés", "Nombre de morts": "Tués", "Nombre de blessés": "Blessés"}
    ref = cles[cles["indicateur"].isin(noms)].assign(Mesure=lambda x: x["indicateur"].map(noms)).set_index(["Mesure", "Date"])["Value"]
    t = annuaire("7.2")
    t = t[t["Année"] > 2022].assign(Mesure=t["Ligne"].map({"Nombre d’accidents": "Accidents constatés", "Nombre de morts": "Tués", "Nombre de blesses": "Blessés"}))
    ref = pd.concat([ref, t.set_index(["Mesure", "Année"])["Valeur"]])
    ok3 = len(ref) == len(d3) and d3.reindex(ref.index).eq(ref).all()
    controle("7-05", "D3 : séries publiées", "Statistiques clés 2010–2022, annuaire 2023–2024, sans écart",
             f"{int(d3.reindex(ref.index).eq(ref).sum())} valeurs sur {len(ref)} identiques", ok3)

    e = portail("etat_reseau_routier.csv")
    e = e[~e["tronçon"].str.match(r"^(TOTAL|VOIRIES)")]
    tot_brut = e[e["etat"] == "TOTAL"]["Value"].sum()
    d4 = lire("D4_etat_troncons")
    ecart = (d4[["km_bon", "km_moyen", "km_mauvais", "km_travaux"]].sum(axis=1) - d4["km_total"]).abs().max()
    ok4 = abs(d4["km_total"].sum() - tot_brut) < 1e-6 and ecart <= 0.01 + 1e-9
    controle("7-06", "D4 : km de l'état conservés", "Km total des tronçons = total brut ; états = total de chaque tronçon (au centième)",
             f"{n(d4['km_total'].sum(), 2)} km pour {n(tot_brut, 2)} km bruts ; écart max. par tronçon : {n(ecart, 2)} km", ok4)

    d4d5 = lire("D4_D5_etat_trace")
    reparti = d4d5[d4d5["État"] != "Non évalué"].groupby("État")["km"].sum()
    source = d4[["km_bon", "km_moyen", "km_mauvais", "km_travaux"]].sum().rename(index={"km_bon": "Bon", "km_moyen": "Moyen", "km_mauvais": "Mauvais", "km_travaux": "Travaux"})
    ecart = (reparti.reindex(source.index) - source).abs().max()
    controle("7-07", "D4 × D5 : km répartis conservés", f"Km par état répartis entre préfectures = km de l'état (± {n(TOLERANCE_KM, 2)} km)",
             " ; ".join(f"{k} : {n(reparti[k], 2)} / {n(source[k], 2)}" for k in source.index), ecart <= TOLERANCE_KM)

    r = pd.read_csv(BRUT / "routes_classees.csv", dtype=str)
    r = gpd.GeoDataFrame(r, geometry=gpd.GeoSeries.from_wkt(r["geometry"]), crs=4326).to_crs(UTM31N)
    with zipfile.ZipFile(BRUT / "limites_administratives_hdx.geojson.zip") as z:
        admin2 = gpd.read_file(io.BytesIO(z.read("tgo_admin2.geojson"))).to_crs(UTM31N)
    togo = admin2.geometry.union_all()
    dedans = r.geometry.intersection(togo).length.sum() / 1000
    d5 = lire("D5_trace_prefecture")
    controle("7-08", "D5 : km du tracé conservés", "Somme des km par préfecture = tracé dans les 40 polygones HDX ; le reste est hors du Togo",
             f"{n(d5['km'].sum(), 1)} km par préfecture ; {n(dedans, 1)} km recalculés dans les polygones ; hors du Togo : {n(r.length.sum() / 1000 - dedans, 1)} km",
             abs(d5["km"].sum() - dedans) <= TOLERANCE_KM)

    a = pd.read_csv(BRUT / "auto_ecoles.csv", dtype=str)
    d6 = lire("D6_auto_ecoles")
    comptees_brut = int(a["agregation"].isin(["Agréée", "Antenne agréée"]).sum())
    controle("7-09", "D6 : auto-écoles conservées", "272 établissements, identifiants uniques ; comptées = agréées + antennes agréées du fichier brut",
             f"{len(d6)} établissements, {d6['FID'].nunique()} identifiants ; comptées : {int(d6['Comptée (R-12)'].sum())} (brut : {comptees_brut})",
             len(d6) == len(a) == d6["FID"].nunique() and int(d6["Comptée (R-12)"].sum()) == comptees_brut)

    rgph = portail("rgph_2022_population.csv")
    pays = rgph[(rgph["découpage-administratif"] == "TOGO") & (rgph["sexe"] == "Total")]["Value"].item()
    pop = lire("D7_population_prefecture_2022")
    tot = pop[(pop["Groupe d’âges"] == "Total") & (pop["Milieu"] == "Total") & (pop["Sexe"] == "Ensemble")]
    livret = pd.read_csv(INTERIM / "livret02_population_2022.csv")
    zl = livret[(livret["Niveau"] != "préfecture") & (livret["Groupe d’âges"] == "Total") & (livret["Milieu"] == "Total") & (livret["Sexe"] == "Ensemble")].set_index("Unité")["Valeur"]
    zones = tot.groupby("Zone")["Population"].sum().rename(index={"Maritime hors Grand Lomé": "Maritime sans Grand Lomé"})
    ok_zones = all(zones[z] == zl[z] for z in zones.index)
    t = lire("table_maitresse_prefecture")
    controle("7-10", "D7 : préfectures = zones = pays", "Somme des 39 préfectures = chaque zone du Livret 02 = pays (recensement CSV)",
             f"39 préfectures : {n(tot['Population'].sum())} ; pays : {n(pays)} ; 6 zones égales : {'oui' if ok_zones else 'non'} ; table maîtresse : {n(t['population_2022'].sum())}",
             tot["Population"].sum() == pays == t["population_2022"].sum() and ok_zones and len(zones) == 6)

    nat = lire("D7_population_nationale").set_index("Année")
    proj = portail("projections_demographiques_2011_2031.csv")
    proj = proj[(proj["tranche-d-âges"] == "Togo") & (proj["sexe"] == "Total")].set_index("Date")["Value"]
    p10 = portail("population_region_sexe_2010.csv")
    p10 = p10[(p10["région"] == "Togo") & (p10["sexe"] == "Total")]["Value"].item()
    annees_proj = [an for an in range(2011, 2025) if an != 2022]
    ok = nat.loc[2010, "Population"] == p10 and nat.loc[2022, "Population"] == pays and (nat.loc[annees_proj, "Population"] == proj[annees_proj]).all()
    controle("7-11", "D7 : série nationale", "2010 et 2022 = recensements ; 2011–2021 et 2023–2024 = projections ; 1990–2024 sans trou",
             f"{len(nat)} années ({nat.index.min()}–{nat.index.max()}) ; recensements et projections identiques : {'oui' if ok else 'non'}",
             ok and list(nat.index) == list(range(1990, 2025)))


# --- Jointures --------------------------------------------------------------------------------------------

def jointures():
    j = pd.read_csv(ANALYSE / "jointures_05.csv")
    besoin = j[~j["Jointure"].str.startswith("Hors 02")]
    eq = j[j["Jointure"].str.startswith("Hors 02")]
    d4 = lire("D4_etat_troncons")
    d6 = lire("D6_auto_ecoles")
    ok = (besoin["Taux (%)"] == 100).all() and (eq["Taux (%)"] >= 99).all() and (d4["Méthode"] != "non rattaché").all() and d6["Préfecture"].notna().all()
    controle("7-12", "Taux de succès des jointures", "100 % pour chaque jointure du §5 ; équipements (hors 02) : 99 % au moins",
             " ; ".join(f"{r.Jointure} : {r.Rattachés}/{r.Total} ({n(r._6, 1)} %)" for r in j.itertuples()), ok)


# --- Valeurs manquantes, zéros, types, niveaux -------------------------------------------------------------

def manquants():
    routes = gpd.read_file(TRAITE / "geo" / "routes_classees.geojson")
    d6 = lire("D6_auto_ecoles")
    pop = lire("D7_population_prefecture_2022")
    livret = pd.read_csv(INTERIM / "livret02_population_2022.csv")
    vides_livret = int(livret[livret["Niveau"] == "préfecture"]["Valeur"].isna().sum())
    d2 = lire("D2_permis")
    brut = portail("permis_par_categorie.csv")
    zeros_brut = int(((brut["Value"] == 0) & (brut["categories-de-permis"] != "Total")).sum())
    zeros_d2 = int((d2["Permis délivrés"] == 0).sum())
    zero_voie = int((routes["Voies"] == 0).sum())
    inconnus = int(d6[["Adresse", "Jours d'ouverture", "Statut"]].isin(["Nsp", "Néant"]).sum().sum())
    ok = (zero_voie == 0 and inconnus == 0 and int(pop["Population"].isna().sum()) == vides_livret
          and d2.loc[d2["Année"] == 2013, "Permis délivrés"].isna().all() and zeros_d2 == zeros_brut)
    controle("7-13", "Aucun zéro là où la source n'a rien", "Permis de 2013 vides ; un 0 de D2 est un 0 publié ; cellules « - » vides ; aucune voie à 0 ; aucun « Nsp » ni « Néant »",
             f"permis de 2013 vides : {int(d2.loc[d2['Année'] == 2013, 'Permis délivrés'].isna().sum())}/6 ; permis à 0 : {zeros_d2}, tous publiés (brut : {zeros_brut}) ; "
             f"population vide : {int(pop['Population'].isna().sum())} "
             f"(« - » dans le Livret : {vides_livret}) ; tronçons à 0 voie : {zero_voie} ; « Nsp » ou « Néant » restants : {inconnus}", ok)

    e = portail("etat_reseau_routier.csv")
    e = e[~e["tronçon"].str.match(r"^(TOTAL|VOIRIES)")]
    sans_travaux = e.groupby("tronçon")["etat"].apply(lambda s: "TRAVAUX" not in set(s)).sum()
    d4 = lire("D4_etat_troncons")
    t = lire("table_maitresse_prefecture")
    mo = t[t["Préfecture"] == "Mô"]
    r = pd.read_csv(BRUT / "routes_classees.csv", dtype=str)
    r = gpd.GeoDataFrame(r, geometry=gpd.GeoSeries.from_wkt(r["geometry"]), crs=4326).to_crs(UTM31N)
    pref = gpd.read_file(TRAITE / "geo" / "prefectures.geojson").to_crs(UTM31N)
    dans_mo = r.geometry.intersection(pref[pref["Préfecture"] == "Mô"].geometry.item()).length.sum() / 1000
    km_cols = [c for c in t.columns if c.startswith("km_")]
    ok = int((d4["km_travaux"] == 0).sum()) == int(sans_travaux) and dans_mo == 0 and (mo[km_cols] == 0).all(axis=None)
    controle("7-14", "Chaque zéro gardé a sa preuve", "Travaux à 0 = tronçons sans ligne « TRAVAUX » dont les états font le total ; Mô à 0 km = aucun tracé dans son polygone",
             f"travaux à 0 : {int((d4['km_travaux'] == 0).sum())} tronçons (sans ligne « TRAVAUX » dans le brut : {int(sans_travaux)}) ; "
             f"tracé brut dans Mô : {n(dans_mo, 1)} km ; km de Mô dans la table maîtresse, tous à 0 : {'oui' if (mo[km_cols] == 0).all(axis=None) else 'non'}", ok)

    vides = {}
    for f in sorted(TRAITE.glob("*.csv")):
        d = pd.read_csv(f).drop(columns=["Note", "Axe"], errors="ignore")  # colonnes d'annotation : vides par construction
        par_col = d.isna().sum()
        if par_col.sum():
            vides[f.stem] = ", ".join(f"{c} {k}" for c, k in par_col[par_col > 0].items())
    controle("7-15", "Valeurs non renseignées, par table", "Comptées et laissées vides, jamais remplacées (colonnes d'annotation exclues)",
             " ; ".join(f"{k} : {v}" for k, v in vides.items()), True)


def types_et_niveaux():
    pb = []
    for nom in ANNEES_NUMERIQUES:
        d = lire(nom)
        if not pd.api.types.is_integer_dtype(d["Année"]):
            pb.append(f"{nom} : année non entière")
    numeriques = {"D1_immatriculations": ["Immatriculations"], "D3_accidents": ["Valeur"], "D4_etat_troncons": ["km_bon", "km_total"],
                  "D4_D5_etat_trace": ["km"], "D5_trace_prefecture": ["km"], "D7_population_nationale": ["Population"],
                  "D1_parc_estime": ["Valeur centrale"], "table_maitresse_prefecture": ["population_2022", "km_rn_revetue", "auto_ecoles_comptees"]}
    for nom, cols in numeriques.items():
        d = lire(nom)
        pb += [f"{nom} : {c} non numérique" for c in cols if not pd.api.types.is_numeric_dtype(d[c])]
    geo = {}
    for f in sorted((TRAITE / "geo").glob("*.geojson")):
        g = gpd.read_file(f)
        geo[f.stem] = (len(g), int(g.geometry.is_valid.sum()), g.crs.to_epsg())
        if geo[f.stem][1] != len(g) or geo[f.stem][2] != 4326:
            pb.append(f"{f.name} : géométries invalides ou projection ≠ WGS 84")
    controle("7-16", "Types", "Années en entiers ; valeurs numériques ; géométries valides, en WGS 84",
             (" ; ".join(pb) or "aucun problème") + " ; couches : " + ", ".join(f"{k} {v[1]}/{v[0]} valides" for k, v in geo.items()), not pb)

    sans = []
    for f in sorted(TRAITE.glob("*.csv")):
        if f.stem in ("table_maitresse_prefecture", "dictionnaire_table_maitresse"):
            continue
        d = pd.read_csv(f)
        if not {"Source", "Niveau"} <= set(d.columns) or d[["Source", "Niveau"]].isna().any(axis=None):
            sans.append(f.stem)
    t, dico = lire("table_maitresse_prefecture"), lire("dictionnaire_table_maitresse")
    couvert = set(t.columns) == set(dico["Colonne"]) and dico[["Source", "Niveau"]].notna().all(axis=None)
    controle("7-17", "Niveau de preuve", "Chaque table a une source et un niveau sur chaque ligne ; la table maîtresse, par son dictionnaire",
             f"tables sans source ou niveau : {', '.join(sans) or 'aucune'} ; dictionnaire complet : {'oui' if couvert else 'non'}", not sans and couvert)


# --- Variables dérivées -----------------------------------------------------------------------------------

def derivees():
    d1 = lire("D1_immatriculations").pivot_table(index="Année", columns="Groupe", values="Immatriculations", aggfunc="sum")
    p = lire("D1_parc_estime")
    durees = {"Moto": (7, 5, 10), "Voiture": (15, 10, 20), "Poids lourd": (15, 10, 20), "Bus et car": (15, 10, 20), "Autres": (15, 10, 20)}
    pb = 0
    for g, (c, b, h) in durees.items():
        s = p[p["Groupe"] == g].set_index("Année")
        for col, l in (("Borne basse", b), ("Valeur centrale", c), ("Borne haute", h)):
            for an in s.index:
                fenetre = [y for y in range(an - l + 1, an + 1)]
                attendu = d1.loc[fenetre, g].sum() if fenetre[0] >= d1.index.min() else None
                v = s.loc[an, col]
                pb += (pd.isna(v) != (attendu is None)) or (attendu is not None and v != attendu)
    complet = p.dropna(subset=["Borne basse", "Valeur centrale", "Borne haute"])
    ordre = ((complet["Borne basse"] <= complet["Valeur centrale"]) & (complet["Valeur centrale"] <= complet["Borne haute"])).all()
    controle("7-18", "Parc estimé", "Chaque valeur = somme de sa fenêtre ; basse ≤ centrale ≤ haute ; vide sans fenêtre complète",
             f"valeurs différentes du recalcul : {pb} ; bornes ordonnées : {'oui' if ordre else 'non'} ; années complètes, tous groupes : "
             f"{p[p['Groupe'] == 'Ensemble'].dropna()['Année'].min()}–{p['Année'].max()}", pb == 0 and ordre)

    a = lire("D7_population_age_conduire")
    nat = lire("D7_population_nationale").set_index("Année")["Population"]
    m = a.merge(nat.rename("Total"), left_on="Année", right_index=True)
    ages = pd.read_csv(REFERENCE / "ages_minimaux_permis.csv").set_index("Catégorie")["Âge minimal"]
    ok = (m["Population en âge de conduire"] <= m["Total"]).all() and (a["Âge minimal"] == a["Catégorie"].map(ages)).all()
    controle("7-19", "Population en âge de conduire", "≤ population totale de l'année ; âge minimal = table PA-05",
             f"{len(a)} valeurs ({a['Année'].min()}–{a['Année'].max()}) ; toutes ≤ population totale : {'oui' if (m['Population en âge de conduire'] <= m['Total']).all() else 'non'}",
             ok)


def correspondance():
    c = pd.read_csv(REFERENCE / "correspondance_vehicules_permis.csv", keep_default_na=False)
    types = [t for v in c["Types immatriculés (D1)"] if v for t in v.split(" | ")]
    d1 = set(lire("D1_immatriculations")["Type"])
    ok = set(types) == d1 and len(types) == len(set(types)) and list(c["Catégorie"]) == list("ABCDEF")
    controle("7-20", "Correspondance entre véhicules et permis (O1-09)", "Chaque type immatriculé de D1 dans une seule catégorie ; catégories A à F",
             f"{len(set(types))} types sur {len(d1)} placés, chacun une fois : {'oui' if len(types) == len(set(types)) else 'non'} ; "
             f"catégories sans type immatriculé : {', '.join(c.loc[c['Types immatriculés (D1)'] == '', 'Catégorie']) or 'aucune'}", ok)


def anomalie_10():
    """Surface des polygones réparés face à la surface enclose par leur contour brut. L'aire d'un polygone dont le
    contour se recoupe est mal définie (ses lobes s'annulent) : la référence est l'union des faces formées par son contour."""
    r = pd.read_csv(BRUT / "equipements_passages_pietons.csv", dtype=str)
    brut = gpd.GeoSeries.from_wkt(r["geometry"], crs=4326)
    invalides = ~brut.is_valid
    faces = gpd.GeoSeries([shapely.union_all(shapely.get_parts(shapely.polygonize(shapely.get_parts(shapely.node(g.boundary)))))
                           for g in brut[invalides]], index=r.loc[invalides, "FID"].values, crs=4326)
    traite = gpd.read_file(TRAITE / "geo" / "equipements.geojson").set_index("FID").geometry.loc[faces.index]
    a0, a1 = faces.to_crs(UTM31N).area.sum(), traite.to_crs(UTM31N).area.sum()
    b0, b1 = np.array(faces.to_crs(UTM31N).bounds), np.array(traite.to_crs(UTM31N).bounds)
    emprise = np.abs(b0 - b1).max(axis=1)
    ecart = 100 * abs(a1 / a0 - 1)
    controle("7-21", "Anomalie 10 : surface des polygones réparés", "Écart de surface < 0,1 % face à la surface enclose par le contour brut",
             f"{int(invalides.sum())} polygones ; surface enclose : {n(a0, 3)} m² ; après réparation : {n(a1, 3)} m² (écart {n(ecart, 4)} %) ; "
             f"emprise changée de plus d'1 cm : {int((emprise > 0.01).sum())} polygone(s), au plus de {n(emprise.max(), 1)} m (pointe de surface nulle retirée)",
             ecart < 0.1)


def populations_totales():
    pop = lire("D7_population_prefecture_2022")
    tot = pop[(pop["Groupe d’âges"] == "Total") & (pop["Milieu"] == "Total") & (pop["Sexe"] == "Ensemble")]
    vides = pop[pop["Population"].isna()]
    rural_gl = vides[vides["Préfecture"].isin(["Golfe", "Agoè-Nyivé"]) & (vides["Milieu"] == "Rural")]
    ok = tot["Population"].notna().all() and len(tot) == 39
    controle("7-22", "Population totale de chaque préfecture renseignée", "39 totaux renseignés ; les cellules vides ne touchent que les ventilations",
             f"totaux renseignés : {int(tot['Population'].notna().sum())} sur 39 ; cellules vides : {len(vides)}, toutes dans les ventilations par milieu, sexe "
             f"ou âge, dont {len(rural_gl)} en milieu rural à Golfe et Agoè-Nyivé (urbaines par la règle PA-03)", ok)


# --- Contrôles bloquants -------------------------------------------------------------------------------

def bloquants():
    t = lire("table_maitresse_prefecture")
    ref = pd.read_csv(REFERENCE / "referentiel_prefectures.csv", dtype=str)
    ok = (set(t["Préfecture"]) == set(ref["Préfecture"]) and len(t) == 39 and t["Zone"].nunique() == ref["Zone"].nunique() == 6
          and t["Région"].nunique() == ref["Région"].nunique() == 5)
    controle("B-01", "Entités par maille = découpage officiel", "39 préfectures, 6 zones, 5 régions",
             f"{len(t)} préfectures ({t['Préfecture'].nunique()} distinctes), {t['Zone'].nunique()} zones, {t['Région'].nunique()} régions", ok, True)

    rgph = portail("rgph_2022_population.csv")
    pays = rgph[(rgph["découpage-administratif"] == "TOGO") & (rgph["sexe"] == "Total")]["Value"].item()
    a = pd.read_csv(BRUT / "auto_ecoles.csv", dtype=str)
    d4 = lire("D4_etat_troncons")
    km_etat = t[["km_etat_bon", "km_etat_moyen", "km_etat_mauvais", "km_etat_travaux"]].sum().sum()
    ok = t["population_2022"].sum() <= pays and t["auto_ecoles_recensees"].sum() <= len(a) and km_etat <= d4["km_total"].sum() + TOLERANCE_KM
    controle("B-02", "Aucune somme au-dessus du total réel", "Préfectures ≤ pays : population, auto-écoles, km de l'état",
             f"population : {n(t['population_2022'].sum())} ≤ {n(pays)} ; auto-écoles : {t['auto_ecoles_recensees'].sum()} ≤ {len(a)} ; "
             f"km de l'état : {n(km_etat, 1)} ≤ {n(d4['km_total'].sum(), 1)}", ok, True)

    nat = t[["km_rn_revetue", "km_rn_non_revetue"]].sum().sum()
    evaluee = 100 * (1 - t["km_rn_non_evaluee"].sum() / nat)
    avec = 100 * (t["auto_ecoles_comptees"] > 0).mean()
    controle("B-03", "Aucune couverture nationale à 0 % ni à 100 %", "Part du réseau national évaluée et part des préfectures avec une auto-école comptée, strictement entre 0 et 100 %",
             f"réseau national évalué : {n(evaluee, 1)} % ; préfectures avec une auto-école comptée : {n(avec, 1)} %, soit {int((t['auto_ecoles_comptees'] > 0).sum())} sur 39 "
             f"({int((t['auto_ecoles_comptees'] == 0).sum())} sans auto-école comptée, dont {int((t['auto_ecoles_recensees'] == 0).sum())} sans aucune auto-école recensée)",
             0 < evaluee < 100 and 0 < avec < 100, True)


def main():
    ANALYSE.mkdir(parents=True, exist_ok=True)
    lignes()
    totaux()
    jointures()
    manquants()
    types_et_niveaux()
    derivees()
    correspondance()
    anomalie_10()
    populations_totales()
    bloquants()
    df = pd.DataFrame(controles)
    df.to_csv(ANALYSE / "controles_05.csv", index=False)
    print(f"{len(df)} contrôles : " + ", ".join(f"{k} {v}" for k, v in df["Résultat"].value_counts().items()))
    echecs = df[df["Résultat"] == ECHEC]
    if len(echecs):
        print(echecs[["ID", "Contrôle", "Mesure"]].to_string(index=False))
    if ((df["Bloquant"] == "oui") & (df["Résultat"] == ECHEC)).any():
        sys.exit(1)


if __name__ == "__main__":
    main()
