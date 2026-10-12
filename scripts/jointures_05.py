"""Étape 05 : jointures finales, variables dérivées et table maîtresse (05_data_preparation.md, §5 et §6).

Lit les tables nettoyées par nettoyage_05.py (data/interim/05_nettoyage/ et data/processed/), les
polygones HDX de data/raw/, data/reference/ et les points de départ de O4-08 écrits par le 04.

Sorties, dans data/processed/ :
- D4_etat_troncons.csv, D4_D5_etat_trace.csv, D5_trace_prefecture.csv, D6_auto_ecoles.csv,
  D7_population_prefecture_2022.csv, D13_points_depart_o4_08.csv ;
- variables dérivées (§6) : D1_parc_estime.csv, D7_population_age_conduire.csv ;
- table_maitresse_prefecture.csv et dictionnaire_table_maitresse.csv ;
- geo/ : préfectures, routes classées, auto-écoles et équipements, en WGS 84 ;
et data/analysis/05_preparation/jointures_05.csv : le taux de succès de chaque jointure.

Rattachement de l'état au tracé : nom exact, nom normalisé (même règle qu'au 04), puis table de
correspondance validée. Aucun rapprochement approché : un nom proche n'est utilisé qu'une fois validé
et inscrit dans la table. L'état d'un tronçon est réparti entre préfectures au prorata des km de son
tracé dans chacune (R-15) ; pour un axe, au prorata des km de l'axe entier. Longueurs et surfaces en
UTM 31N (R-16). Aucun ratio : les tables portent des numérateurs et des dénominateurs.

Usage : .venv/bin/python scripts/jointures_05.py
"""
import io
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

from jointures_04 import cle_troncon  # règle de normalisation des noms de tronçon, validée au 04

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
REFERENCE = RACINE / "data" / "reference"
INTERIM = RACINE / "data" / "interim"
NETTOYE = INTERIM / "05_nettoyage"
SORTIE = RACINE / "data" / "processed"
GEO = SORTIE / "geo"
ANALYSE = RACINE / "data" / "analysis" / "05_preparation"

UTM31N, WGS84 = 32631, 4326
COLLECTE = "collecte 2021-2022"
# Durée de vie PA-01 : valeur centrale, borne basse, borne haute (02, 03_Seuils) ; « Autres » (camionnettes) : 05 §6
PA01 = {"Moto": (7, 5, 10), "Voiture": (15, 10, 20), "Poids lourd": (15, 10, 20), "Bus et car": (15, 10, 20), "Autres": (15, 10, 20)}
TYPES_ROUTE = {"Route nationale revêtue": "km_rn_revetue", "Route nationale non revêtue": "km_rn_non_revetue",
               "Piste rurale": "km_piste_rurale", "Voirie urbaine": "km_voirie_urbaine"}
TYPE_NATIONAL = {"Route nationale revêtue": "revêtue", "Route nationale non revêtue": "non revêtue"}
ETATS = {"km_bon": "Bon", "km_moyen": "Moyen", "km_mauvais": "Mauvais", "km_travaux": "Travaux"}

jointures = []


def exiger(condition, message):
    if not condition:
        raise ValueError(message)


def taux(jointure, cle, attendu, rattaches, total, reste=""):
    jointures.append({"Jointure": jointure, "Clé": cle, "Attendu": attendu, "Rattachés": rattaches, "Total": total,
                      "Taux (%)": round(100 * rattaches / total, 1), "Non rattachés": reste or "aucun"})


def lire_wkt(fichier):
    d = pd.read_csv(fichier, dtype={"FID": str})
    return gpd.GeoDataFrame(d.drop(columns="geometry"), geometry=gpd.GeoSeries.from_wkt(d["geometry"]), crs=WGS84)


def vers_wgs84(gdf, nom):
    GEO.mkdir(parents=True, exist_ok=True)
    gdf.to_crs(WGS84).to_file(GEO / nom, driver="GeoJSON")


# --- D8 : préfectures -----------------------------------------------------------------------------

def prefectures(ref):
    with zipfile.ZipFile(BRUT / "limites_administratives_hdx.geojson.zip") as z:
        admin2 = gpd.read_file(io.BytesIO(z.read("tgo_admin2.geojson")))
    code = {c.strip(): r["Préfecture"] for _, r in ref.iterrows() for c in r["Codes HDX regroupés"].split(",")}
    admin2["Préfecture"] = admin2["adm2_pcode"].map(code)
    exiger(admin2["Préfecture"].notna().all(), "D8 : unité HDX hors référentiel")
    pref = admin2.to_crs(UTM31N).dissolve(by="Préfecture", as_index=False)[["Préfecture", "geometry"]]
    pref = pref.merge(ref[["Préfecture", "Code HDX", "Région", "Zone"]], on="Préfecture")
    pref["Surface (km²)"] = (pref.area / 1e6).round(2)
    exiger(len(pref) == 39, "D8 : le référentiel doit compter 39 préfectures")
    vers_wgs84(pref, "prefectures.geojson")
    return pref


# --- D5 × D8 : tracé ------------------------------------------------------------------------------------

def trace(pref):
    routes = lire_wkt(NETTOYE / "D5_routes_classees.csv").to_crs(UTM31N)
    routes["km"] = routes.length / 1000
    vers_wgs84(routes.assign(km=routes["km"].round(3)), "routes_classees.geojson")
    morceaux = gpd.overlay(routes[["FID", "Nom", "Type", "geometry"]], pref[["Préfecture", "Région", "Zone", "geometry"]],
                           how="intersection", keep_geom_type=True)
    morceaux["km"] = morceaux.length / 1000
    dedans = morceaux["km"].sum()
    taux("D5 × D8 : tracé → préfectures", "polygone", "tout le tracé du Togo rattaché", morceaux["FID"].nunique(), len(routes),
         f"{routes['km'].sum() - dedans:.1f} km hors des 39 polygones (hors du Togo, 4.3-05)")

    grille = pd.MultiIndex.from_product([pref["Préfecture"], list(TYPES_ROUTE)], names=["Préfecture", "Type de route"])
    km = morceaux.groupby(["Préfecture", "Type"])["km"].sum().rename_axis(["Préfecture", "Type de route"]).reindex(grille, fill_value=0)
    d = km.round(3).reset_index().merge(pref[["Préfecture", "Région", "Zone"]], on="Préfecture")
    d["Note"] = d["km"].eq(0).map({True: "0 km : aucun tronçon de ce type dans le polygone", False: ""})
    d = d.assign(Année=COLLECTE, Source="routes classées (D5), découpées par préfecture (R-15), longueurs en UTM 31N", Niveau="B")
    d[["Préfecture", "Région", "Zone", "Type de route", "km", "Année", "Source", "Niveau", "Note"]].to_csv(SORTIE / "D5_trace_prefecture.csv", index=False)
    return routes, pd.DataFrame(morceaux.drop(columns="geometry")), d


# --- D4 × D5 : état du réseau rattaché au tracé ---------------------------------------------------------

def etat(routes, morceaux, pref):
    e = pd.read_csv(NETTOYE / "D4_etat_troncons.csv")
    table = pd.read_csv(REFERENCE / "correspondance_etat_trace.csv", dtype=str, keep_default_na=False)
    correspondance = {t: c for _, c in table.iterrows() for t in c["Tronçons de l'état"].split(" | ")}
    noms = sorted(routes["Nom"].dropna().unique())
    par_cle = {}
    for nom in noms:
        par_cle.setdefault(cle_troncon(nom), []).append(nom)

    liens = []
    for t in e["Tronçon"]:
        if t in noms:
            methode, axe, lies = "nom exact", "", [t]
        elif cle_troncon(t) in par_cle:
            methode, axe, lies = "nom normalisé", "", par_cle[cle_troncon(t)]
        elif t in correspondance:
            c = correspondance[t]
            methode = "axe" if c["Rattachement"] == "axe" else "nom proche, validé"
            axe, lies = c["Axe"], c["Noms du tracé"].split(" | ")
        else:
            methode, axe, lies = "non rattaché", "", []
        liens.append({"Tronçon": t, "Méthode": methode, "Axe": axe, "Groupe": axe or t, "Noms du tracé": lies})
    liens = pd.DataFrame(liens)
    utilises = liens.drop_duplicates("Groupe")["Noms du tracé"].explode().dropna()
    exiger(not utilises.duplicated().any(), "D4 × D5 : un nom du tracé est rattaché à deux groupes")

    # Part de chaque préfecture dans le tracé de chaque groupe (tronçon, ou axe entier)
    groupe_nom = liens.drop_duplicates("Groupe").explode("Noms du tracé").dropna(subset=["Noms du tracé"])[["Groupe", "Noms du tracé"]]
    km_groupe = groupe_nom.merge(morceaux, left_on="Noms du tracé", right_on="Nom").groupby(["Groupe", "Préfecture"])["km"].sum()
    parts = (km_groupe / km_groupe.groupby(level="Groupe").transform("sum")).rename("part").reset_index()

    e = e.merge(liens, on="Tronçon")
    reparti = e.merge(parts, on="Groupe")
    lignes = []
    for col, libelle in ETATS.items():
        lignes.append(reparti.assign(État=libelle, km=reparti[col] * reparti["part"])[["Préfecture", "Type", "État", "km"]])
    etat_pref = pd.concat(lignes).groupby(["Préfecture", "Type", "État"])["km"].sum().reset_index()
    etat_pref = etat_pref[etat_pref["km"] > 0].assign(Source="état du réseau (D4, relevé de 2020), réparti sur le tracé (D5)", Niveau="C", Année="2020")

    lies = set(utilises)
    nat = morceaux[morceaux["Type"].isin(TYPE_NATIONAL) & ~morceaux["Nom"].isin(lies)]
    sans = nat.assign(Type=nat["Type"].map(TYPE_NATIONAL)).groupby(["Préfecture", "Type"])["km"].sum().reset_index()
    sans = sans.assign(État="Non évalué", Source="tracé national (D5) sans tronçon d'état rattaché (R-14)", Niveau="B", Année=COLLECTE)
    d = pd.concat([etat_pref, sans]).rename(columns={"Type": "Type de route"}).merge(pref[["Préfecture", "Région", "Zone"]], on="Préfecture")
    d["km"] = d["km"].round(3)
    d[["Préfecture", "Région", "Zone", "Type de route", "État", "km", "Année", "Source", "Niveau"]].sort_values(
        ["Préfecture", "Type de route", "État"]).to_csv(SORTIE / "D4_D5_etat_trace.csv", index=False)

    # D4_etat_troncons.csv : chaque tronçon avec son rattachement et les territoires qu'il traverse (O3-05)
    territoires = parts.merge(pref[["Préfecture", "Région", "Zone"]], on="Préfecture").sort_values(["Groupe", "part"], ascending=[True, False])
    joindre = lambda s: " ; ".join(dict.fromkeys(s))
    trav = territoires.groupby("Groupe").agg(**{"Préfectures traversées": ("Préfecture", joindre), "Zones traversées": ("Zone", joindre),
                                                "Régions traversées": ("Région", joindre)}).reset_index()
    km_trace = km_groupe.groupby(level="Groupe").sum().round(2).rename("km du tracé").reset_index()
    types_trace = groupe_nom.merge(routes[["Nom", "Type"]].drop_duplicates(), left_on="Noms du tracé", right_on="Nom").groupby("Groupe")["Type"].agg(
        lambda s: " | ".join(sorted(set(s)))).rename("Types du tracé").reset_index()
    t = e.merge(trav, on="Groupe", how="left").merge(km_trace, on="Groupe", how="left").merge(types_trace, on="Groupe", how="left")
    t["Noms du tracé"] = t["Noms du tracé"].map(" | ".join)
    t = t[["Type", "Tronçon", *ETATS, "km_total", "Méthode", "Axe", "Noms du tracé", "Types du tracé", "km du tracé",
           "Préfectures traversées", "Zones traversées", "Régions traversées", "Année", "Source", "Niveau"]]
    t.to_csv(SORTIE / "D4_etat_troncons.csv", index=False)

    rattaches = int((liens["Méthode"] != "non rattaché").sum())
    taux("D4 × D5 : état → tracé", "nom du tronçon ; table de correspondance", "84 tronçons sur 84", rattaches, len(liens),
         ", ".join(liens.loc[liens["Méthode"] == "non rattaché", "Tronçon"]))
    return d


# --- D6 × D8, D7 × D8, D13 × D8 ------------------------------------------------------------------------

def auto_ecoles(pref):
    a = lire_wkt(NETTOYE / "D6_auto_ecoles.csv").to_crs(UTM31N)
    j = gpd.sjoin(a, pref[["Préfecture", "Région", "Zone", "geometry"]], how="left", predicate="within").drop(columns="index_right")
    taux("D6 × D8 : auto-écoles → préfectures", "point dans le polygone", "272 sur 272", int(j["Préfecture"].notna().sum()), len(j),
         ", ".join(j.loc[j["Préfecture"].isna(), "Nom"]))
    vers_wgs84(j, "auto_ecoles.geojson")
    wgs = j.to_crs(WGS84)
    d = pd.DataFrame(j.drop(columns="geometry")).assign(x_utm=j.geometry.x.round(1), y_utm=j.geometry.y.round(1),
                                                        lon=wgs.geometry.x.round(6), lat=wgs.geometry.y.round(6))
    d = d.assign(Année=COLLECTE, Source="auto-écoles (D6), préfecture par le polygone (R-01)", Niveau="A (comptage) ; C (offre, activité non vérifiée)")
    d.to_csv(SORTIE / "D6_auto_ecoles.csv", index=False)
    return d


def population(ref):
    p = pd.read_csv(NETTOYE / "D7_population_prefecture_2022.csv")
    nom = dict(zip(ref["Nom Livret 02 (D7)"], ref["Préfecture"]))
    p["Préfecture"] = p["Nom Livret 02"].map(nom)
    taux("D7 × D8 : population → préfectures", "libellé du Livret 02", "39 sur 39", p.loc[p["Préfecture"].notna(), "Nom Livret 02"].nunique(),
         p["Nom Livret 02"].nunique(), ", ".join(sorted(p.loc[p["Préfecture"].isna(), "Nom Livret 02"].unique())))
    p = p.merge(ref[["Préfecture", "Région", "Zone"]], on="Préfecture")
    p["Population"] = p["Population"].astype("Int64")
    p["Note"] = p["Lecture"].map(lambda l: "" if l == "colonnes" else l)
    p = p.assign(Année=2022, Source="recensement 2022 (RGPH-5, Livret 02)", Niveau="A")
    p[["Préfecture", "Région", "Zone", "Groupe d’âges", "Milieu", "Sexe", "Population", "Année", "Source", "Niveau", "Note"]].to_csv(
        SORTIE / "D7_population_prefecture_2022.csv", index=False)
    return p


def points_depart(ref):
    p = pd.read_csv(INTERIM / "points_depart_o4_08.csv").merge(ref[["Préfecture", "Région", "Zone"]], on="Préfecture", how="left")
    taux("D13 × D8 : points de départ de O4-08 → préfectures", "préfecture", "39 sur 39", p.loc[p["Région"].notna(), "Préfecture"].nunique(), 39)
    p = p.assign(Source="HDX : chefs-lieux (tgo_admincapitals), sinon point d'étiquette de la préfecture (tgo_adminpoints) (écart 19)", Niveau="C")
    p.to_csv(SORTIE / "D13_points_depart_o4_08.csv", index=False)
    return p


def equipements(pref):
    origine = lire_wkt(NETTOYE / "equipements.csv")
    j = gpd.sjoin(origine.to_crs(UTM31N), pref[["Préfecture", "geometry"]], how="left", predicate="within").drop(columns="index_right")
    taux("Hors 02 : équipements → préfectures", "point dans le polygone", "plus de 99 % (4.3-10)", int(j["Préfecture"].notna().sum()), len(j))
    # Couche écrite avec ses géométries d'origine : l'aller-retour WGS 84 → UTM rendrait invalides des contours de quelques cm
    vers_wgs84(origine.join(j[["Préfecture"]]), "equipements.geojson")


# --- Variables dérivées (§6) ------------------------------------------------------------------------------

def parc_estime():
    d1 = pd.read_csv(SORTIE / "D1_immatriculations.csv")
    flux = d1.pivot_table(index="Année", columns="Groupe", values="Immatriculations", aggfunc="sum")
    exiger(list(flux.index) == list(range(flux.index.min(), flux.index.max() + 1)), "Parc estimé : série annuelle incomplète")
    lignes = []
    for groupe, (centre, bas, haut) in PA01.items():
        cumul = {nom: flux[groupe].rolling(l, min_periods=l).sum() for nom, l in (("Borne basse", bas), ("Valeur centrale", centre), ("Borne haute", haut))}
        lignes.append(pd.DataFrame(cumul).assign(Groupe=groupe, **{"Durée de vie PA-01 (ans)": f"{centre} [{bas}–{haut}]"}))
    p = pd.concat(lignes).rename_axis("Année").reset_index()
    bornes = ["Borne basse", "Valeur centrale", "Borne haute"]
    ensemble = p.groupby("Année")[bornes].sum(min_count=len(PA01)).reset_index().assign(Groupe="Ensemble", **{"Durée de vie PA-01 (ans)": "par groupe"})
    p = pd.concat([p, ensemble])
    p[bornes] = p[bornes].round().astype("Int64")  # vide : moins de L années de série, jamais 0 (R-10)
    p = p.assign(Source="cumul des immatriculations de l'année (D1) sur la durée de vie PA-01 (R-11, écart 16)", Niveau="C")
    p["Note"] = p["Groupe"].map({"Autres": "camionnettes : absentes de PA-01 (02, figé) ; 15 ans [10–20], la valeur des autres véhicules à 4 roues (05 §6)",
                                 "Ensemble": "somme des groupes ; vide si un groupe est vide"}).fillna("")
    p[["Année", "Groupe", *bornes, "Durée de vie PA-01 (ans)", "Source", "Niveau", "Note"]].sort_values(["Groupe", "Année"]).to_csv(SORTIE / "D1_parc_estime.csv", index=False)


def population_age_conduire():
    ages = pd.read_csv(SORTIE / "D7_population_age_nationale.csv")
    minimaux = pd.read_csv(REFERENCE / "ages_minimaux_permis.csv").set_index("Catégorie")["Âge minimal"]
    wpp = pd.read_csv(BRUT / "wpp2024_population_age_simple_togo.csv", sep="|", skiprows=1)
    wpp = wpp[(wpp["Variant"] == "Median") & (wpp["Sex"] == "Both sexes")].set_index(["TimeLabel", "AgeStart"])["Value"]
    lignes = []
    for an, g in ages.groupby("Année"):
        g = g[g["Groupe d'âges"] != "Non déclaré"]  # âge inconnu : hors du décompte, signalé
        non_declare = int(ages[(ages["Année"] == an) & (ages["Groupe d'âges"] == "Non déclaré")]["Population"].sum())
        for cat, age in minimaux.items():
            total = 0.0
            for r in g.itertuples():
                debut = int(r[2].split("-")[0].split(" ")[0])
                fin = 200 if r[2] == "80 et +" else int(r[2].split("-")[1])
                if debut >= age:
                    total += r.Population
                elif fin >= age:  # groupe coupé : part des âges ≥ âge minimal, prise dans WPP la même année (03 §5)
                    total += r.Population * wpp.loc[an].loc[age:fin].sum() / wpp.loc[an].loc[debut:fin].sum()
            lignes.append({"Année": an, "Catégorie": cat, "Âge minimal": age, "Population en âge de conduire": round(total),
                           "Note": f"âge non déclaré, hors décompte : {non_declare}" if non_declare else ""})
    d = pd.DataFrame(lignes).assign(Source="population nationale par âge (D7) ; groupe coupé à l'âge minimal par les âges simples de WPP ; âges de PA-05",
                                    Niveau="C")
    d.to_csv(SORTIE / "D7_population_age_conduire.csv", index=False)


# --- Table maîtresse -------------------------------------------------------------------------------------

def table_maitresse(pref, d5, d4d5, ae, pop, pts):
    t = pd.DataFrame(pref.drop(columns="geometry"))[["Préfecture", "Code HDX", "Région", "Zone", "Surface (km²)"]]
    tot = pop[pop["Groupe d’âges"] == "Total"]
    for col, (milieu, sexe) in {"population_2022": ("Total", "Ensemble"), "population_2022_hommes": ("Total", "Hommes"),
                                "population_2022_femmes": ("Total", "Femmes"), "population_2022_urbaine": ("Urbain", "Ensemble"),
                                "population_2022_rurale": ("Rural", "Ensemble")}.items():
        t = t.merge(tot[(tot["Milieu"] == milieu) & (tot["Sexe"] == sexe)].set_index("Préfecture")["Population"].rename(col), on="Préfecture", how="left")
    t = t.merge(d5.pivot(index="Préfecture", columns="Type de route", values="km").rename(columns=TYPES_ROUTE), on="Préfecture", how="left")
    etats = d4d5.pivot_table(index="Préfecture", columns="État", values="km", aggfunc="sum").rename(
        columns={"Bon": "km_etat_bon", "Moyen": "km_etat_moyen", "Mauvais": "km_etat_mauvais", "Travaux": "km_etat_travaux",
                 "Non évalué": "km_rn_non_evaluee"})
    t = t.merge(etats, on="Préfecture", how="left")
    colonnes_etat = ["km_etat_bon", "km_etat_moyen", "km_etat_mauvais", "km_etat_travaux", "km_rn_non_evaluee"]
    t[colonnes_etat] = t[colonnes_etat].fillna(0).round(3)  # 0 : aucun km de cet état dans le polygone (tracé exhaustif de la couche)
    compte = ae.groupby("Préfecture").agg(auto_ecoles_recensees=("FID", "size"), auto_ecoles_comptees=("Comptée (R-12)", "sum"))
    t = t.merge(compte, on="Préfecture", how="left")
    t[["auto_ecoles_recensees", "auto_ecoles_comptees"]] = t[["auto_ecoles_recensees", "auto_ecoles_comptees"]].fillna(0).astype(int)  # recensement exhaustif (D6)
    t = t.merge(pts.set_index("Préfecture")["Origine"].rename("origine_point_o4_08"), on="Préfecture", how="left")

    dico = [("Préfecture", "Préfecture du référentiel (39)", "—", "data/reference/referentiel_prefectures.csv", "2022", "sans objet"),
            ("Code HDX", "Code de la préfecture (Golfe : TG0303 + TG0305)", "—", "HDX, limites administratives v02", "2021", "sans objet"),
            ("Région", "Région administrative (5)", "—", "référentiel", "2022", "sans objet"),
            ("Zone", "Zone de lecture (6, Grand Lomé séparé ; R-02, R-03)", "—", "référentiel", "2022", "sans objet"),
            ("Surface (km²)", "Surface du polygone, en UTM 31N (R-16)", "km²", "HDX", "2021", "B"),
            ("population_2022", "Population résidente", "habitants", "RGPH-5, Livret 02", "2022", "A"),
            ("population_2022_hommes", "Population résidente masculine", "habitants", "RGPH-5, Livret 02", "2022", "A"),
            ("population_2022_femmes", "Population résidente féminine", "habitants", "RGPH-5, Livret 02", "2022", "A"),
            ("population_2022_urbaine", "Population résidente en milieu urbain ; vide : « - » dans le Livret 02 (R-10)", "habitants", "RGPH-5, Livret 02", "2022", "A"),
            ("population_2022_rurale", "Population résidente en milieu rural ; vide : « - » dans le Livret 02 (R-10)", "habitants", "RGPH-5, Livret 02", "2022", "A")]
    dico += [(col, f"Longueur de {typ.lower()} dans la préfecture ; 0 = aucun tronçon de ce type dans le polygone", "km",
              "routes classées (D5)", COLLECTE, "B") for typ, col in TYPES_ROUTE.items()]
    dico += [(f"km_etat_{e.lower()}", f"Km de l'état du réseau en état « {e.lower()} », répartis au prorata du tracé (R-15)", "km",
              "état du réseau (D4) × tracé (D5)", "2020", "C") for e in ETATS.values()]
    dico += [("km_rn_non_evaluee", "Km de routes nationales du tracé sans tronçon d'état rattaché (R-14)", "km", "routes classées (D5)", COLLECTE, "B"),
             ("auto_ecoles_recensees", "Auto-écoles recensées, tous statuts, préfecture par le polygone", "établissements", "auto-écoles (D6)", COLLECTE, "A"),
             ("auto_ecoles_comptees", "Auto-écoles agréées et antennes agréées (R-12) ; activité non vérifiée", "établissements", "auto-écoles (D6)", COLLECTE, "C"),
             ("origine_point_o4_08", "Point de départ de la distance de O4-08 : chef-lieu, sinon point d'étiquette (écart 19)", "—", "HDX", "2021", "C")]
    dico = pd.DataFrame(dico, columns=["Colonne", "Définition", "Unité", "Source", "Année", "Niveau"])
    exiger(set(dico["Colonne"]) == set(t.columns) and len(dico) == t.shape[1], "Table maîtresse : dictionnaire et colonnes ne correspondent pas")
    t[list(dico["Colonne"])].sort_values("Préfecture").to_csv(SORTIE / "table_maitresse_prefecture.csv", index=False)
    dico.to_csv(SORTIE / "dictionnaire_table_maitresse.csv", index=False)


def main():
    for d in (SORTIE, GEO, ANALYSE):
        d.mkdir(parents=True, exist_ok=True)
    ref = pd.read_csv(REFERENCE / "referentiel_prefectures.csv", dtype=str, keep_default_na=False)
    pref = prefectures(ref)
    routes, morceaux, d5 = trace(pref)
    d4d5 = etat(routes, morceaux, pref)
    ae = auto_ecoles(pref)
    pop = population(ref)
    pts = points_depart(ref)
    equipements(pref)
    parc_estime()
    population_age_conduire()
    table_maitresse(pref, d5, d4d5, ae, pop, pts)
    j = pd.DataFrame(jointures)
    j.to_csv(ANALYSE / "jointures_05.csv", index=False)
    print(j[["Jointure", "Rattachés", "Total", "Taux (%)"]].to_string(index=False))


if __name__ == "__main__":
    main()
