"""Étape 04 : tests du référentiel des préfectures et des jointures (04_data_understanding.md, §5),
et contrôles spatiaux du §4.3.

Sorties :
- data/analysis/04_understanding/jointures.csv : une ligne par test ou jointure, de même forme que
  controles_coherence.csv (mesure, résultat, décision) ;
- data/interim/prefectures_2022.geojson : les 39 préfectures du référentiel (polygones HDX, Golfe et
  Lomé Commune fusionnés), en WGS 84, avec leur surface calculée en UTM 31N ;
- data/interim/routes_par_prefecture.csv : chaque tronçon du tracé découpé par préfecture (R-15),
  longueur en UTM 31N (R-16) ;
- data/interim/auto_ecoles_prefecture.csv : chaque auto-école, sa préfecture déclarée et celle du
  polygone qui la contient ;
- data/interim/etat_troncons_rattaches.csv : les 84 tronçons de l'état du réseau, leur rattachement
  au tracé et la méthode employée ;
- data/interim/points_depart_o4_08.csv : un point de départ par préfecture pour O4-08, le chef-lieu
  HDX ou, à défaut, le point d'étiquette HDX de la préfecture (écart 19).

Rattachement de l'état du réseau au tracé, faute d'identifiant commun : nom exact ; sinon nom
normalisé (sans accent ni ponctuation, sans le code « TGR… » de la DGTP en tête, sans le suffixe de
segment « _1 ») ; sinon table de correspondance validée (data/reference/correspondance_etat_trace.csv :
noms proches validés, et axes dont l'état et le tracé découpent la route autrement) ; sinon nom le plus
proche, si sa similarité atteint SIMILARITE, signalé « à valider ». Pour un axe, la longueur du tracé et
le rapport tracé / état sont ceux de l'axe entier. Un tronçon non rattaché n'est jamais réparti entre
préfectures : il reste lu au niveau national.

Usage : .venv/bin/python scripts/jointures_04.py
"""
import difflib
import io
import re
import unicodedata
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
SIMILARITE = 0.9  # rapprochement approché des noms de tronçon (difflib), au-delà des coquilles : rien
CONFORME, EXPLIQUE, ANOMALIE = "conforme", "écart expliqué", "anomalie transmise au 05"
REGION_CODE = {"M": "Maritime", "P": "Plateaux", "C": "Centrale", "K": "Kara", "S": "Savanes"}
NIVEAU_CHEF_LIEU = {0: "capitale", 1: "chef-lieu de région", 2: "chef-lieu de préfecture"}

lignes = []


def test(ident, section, intitule, attendu, mesure, resultat, decision):
    lignes.append({"ID": ident, "Section": section, "Test": intitule, "Attendu": attendu,
                   "Mesure": mesure, "Résultat": resultat, "Décision": decision})


def n(x, decimales=0):
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def hdx(couche):
    with zipfile.ZipFile(BRUT / "limites_administratives_hdx.geojson.zip") as z:
        return gpd.read_file(io.BytesIO(z.read(couche)))


def cle_troncon(nom):
    """Nom de tronçon comparable : majuscules sans accent, sans code DGTP ni suffixe de segment, sans ponctuation."""
    s = unicodedata.normalize("NFKD", str(nom).upper()).encode("ascii", "ignore").decode().strip()
    s = re.sub(r"_\d+$", "", s)
    s = re.sub(r"^TGR[A-Z]{1,5}?(?=RN\d|\s)", "", s)
    return re.sub(r"[^A-Z0-9]", "", s)


def prefectures(ref):
    """Les 39 préfectures : polygones HDX de niveau 2 regroupés selon le référentiel."""
    admin2 = hdx("tgo_admin2.geojson")
    code = {c.strip(): r["Préfecture"] for _, r in ref.iterrows() for c in r["Codes HDX regroupés"].split(",")}
    admin2["Préfecture"] = admin2["adm2_pcode"].map(code)
    admin2_utm = admin2.to_crs(UTM31N)
    golfe = admin2_utm[admin2_utm["adm2_pcode"].isin(["TG0303", "TG0305"])]
    pref = admin2_utm.dissolve(by="Préfecture", as_index=False)[["Préfecture", "geometry"]]
    pref = pref.merge(ref[["Préfecture", "Région", "Zone", "Code HDX"]], on="Préfecture")
    pref["Surface (km²)"] = pref.area / 1e6
    union_golfe = pref[pref["Préfecture"] == "Golfe"].geometry.iloc[0]
    test("5-01", "5", "Fusion des polygones TG0303 (Golfe) et TG0305 (Lomé Commune)",
         "Un seul polygone pour le Golfe ; sa surface égale la somme des deux",
         f"{len(admin2)} unités HDX → {len(pref)} préfectures ; Golfe : {union_golfe.geom_type}, "
         f"{n(union_golfe.area / 1e6, 1)} km² pour {n(golfe.area.sum() / 1e6, 1)} km² (TG0303 + TG0305)",
         CONFORME if union_golfe.geom_type == "Polygon" and abs(union_golfe.area - golfe.area.sum()) < 1e4 else ANOMALIE,
         "Référentiel des 39 préfectures, surfaces en UTM 31N (O4-02)")
    unites = admin2["adm2_pcode"].nunique()
    test("5-02", "5", "Jointure D8 : polygones HDX → référentiel, par code HDX", "40 unités → 39 préfectures",
         f"{unites} codes HDX, tous rattachés : {'oui' if admin2['Préfecture'].notna().all() else 'non'} ; {pref['Préfecture'].nunique()} préfectures",
         CONFORME if admin2["Préfecture"].notna().all() and len(pref) == 39 else ANOMALIE, "Jointure D8 utilisable")
    return pref


def routes_par_prefecture(ref, pref, pays):
    routes = pd.read_csv(BRUT / "routes_classees.csv", dtype=str)
    geo = gpd.GeoDataFrame(routes.drop(columns="geometry"), geometry=gpd.GeoSeries.from_wkt(routes["geometry"]), crs=4326).to_crs(UTM31N)
    geo["km"] = geo.length / 1000
    declare = dict(zip(ref["Nom routes classées (D5)"], ref["Préfecture"]))
    geo["Préfecture déclarée"] = geo["prefecture_nom_bdd"].map(declare)
    morceaux = gpd.overlay(geo[["FID", "route_type", "route_nom", "Préfecture déclarée", "km", "geometry"]],
                           pref[["Préfecture", "Région", "geometry"]], how="intersection", keep_geom_type=True)
    morceaux["km_prefecture"] = morceaux.length / 1000
    hors = geo["km"].sum() - morceaux["km_prefecture"].sum()
    dehors = geo.geometry.difference(pays).length.sum() / 1000
    test("4.3-05", "4.3", "Tronçons dans les limites du Togo, après reprojection en UTM 31N", "Tout le tracé dans le Togo",
         f"Tracé : {n(geo['km'].sum())} km, {len(geo)} tronçons ; hors du Togo : {n(dehors, 1)} km ; hors des 39 préfectures : {n(hors, 1)} km",
         CONFORME if dehors < 1 else EXPLIQUE, "O4-01 : longueurs prises dans les préfectures")

    principale = (morceaux.sort_values("km_prefecture", ascending=False).drop_duplicates("FID")
                  .set_index("FID")[["Préfecture", "Région"]])
    geo = geo.join(principale, on="FID")
    connue = geo["Préfecture déclarée"].notna()
    egales = (geo["Préfecture déclarée"] == geo["Préfecture"])
    diff = geo[connue & ~egales]
    test("4.3-06", "4.3", "Routes : la préfecture déclarée est celle où passe la plus grande part du tronçon", "100 %",
         f"{int(egales.sum())} tronçons sur {len(geo)} ({n(100 * egales.mean(), 1)} %) ; noms déclarés hors référentiel : {int((~connue).sum())} ; "
         f"autres : {len(diff)} tronçons, {n(diff['km'].sum())} km"
         + (f" (par exemple : {', '.join(f'{a} → {b}' for a, b in diff[['Préfecture déclarée', 'Préfecture']].value_counts().head(4).index)})" if len(diff) else ""),
         CONFORME if egales.all() else EXPLIQUE, "Rattachement par le polygone, jamais par le nom déclaré (R-01)")

    nb = morceaux.groupby("FID")["Préfecture"].nunique()
    a_cheval = nb[nb > 1].index
    km_hors = morceaux[morceaux["FID"].isin(a_cheval)].merge(principale["Préfecture"].rename("principale"), left_on="FID", right_index=True)
    km_hors = km_hors[km_hors["Préfecture"] != km_hors["principale"]]["km_prefecture"].sum()
    test("4.3-07", "4.3", "Tronçons à cheval sur deux préfectures", "Découpage selon R-15",
         f"{len(a_cheval)} tronçons sur {len(geo)} touchent plus d'une préfecture ; {n(km_hors)} km hors de leur préfecture principale "
         f"({n(100 * km_hors / geo['km'].sum(), 1)} % du tracé)",
         EXPLIQUE, "R-15 : chaque tronçon est découpé par préfecture ; les longueurs sont celles des morceaux")

    codes = geo["route_nom"].str.extract(r"^TGR([MPCKS])")[0].map(REGION_CODE)
    avec_code = codes.notna()
    accord = (codes == geo["Région"])
    test("5-03", "5", "Codes de région dans le nom des tronçons (« TGRM… », « TGRP… »)", "Région du code = région du polygone",
         f"{int(avec_code.sum())} tronçons ont un code ; {int((accord & avec_code).sum())} concordent avec la région du polygone",
         CONFORME if (accord | ~avec_code).all() else EXPLIQUE, "Le code n'est pas utilisé pour rattacher : le polygone suffit")

    # Kpendjal-Ouest (« Naki-Ouest » dans HDX)
    kpo = geo[geo["Préfecture déclarée"] == "Kpendjal-Ouest"]
    kpo_dans = morceaux[(morceaux["FID"].isin(kpo["FID"])) & (morceaux["Préfecture"] == "Kpendjal-Ouest")]["km_prefecture"].sum()
    test("5-04", "5", "Kpendjal-Ouest et « Naki-Ouest » (TG0518) : routes", "Les routes déclarées à Kpendjal-Ouest tombent dans TG0518",
         f"{len(kpo)} tronçons déclarés, {n(kpo['km'].sum(), 1)} km, dont {n(kpo_dans, 1)} km dans TG0518",
         CONFORME if len(kpo) and kpo_dans / kpo["km"].sum() > 0.5 else (EXPLIQUE if not len(kpo) else ANOMALIE),
         "TG0518 est bien Kpendjal-Ouest")

    mo = morceaux[morceaux["Préfecture"] == "Mô"]
    test("5-05", "5", "Absence de Mô dans les routes classées", "Vrai vide ou défaut de rattachement",
         f"Tronçons déclarés à Mô : {int((geo['Préfecture déclarée'] == 'Mô').sum())} ; tracé dans le polygone de Mô : {mo['FID'].nunique()} tronçons, "
         f"{n(mo['km_prefecture'].sum(), 1)} km"
         + (f", déclarés à {', '.join(sorted(mo['Préfecture déclarée'].dropna().unique()))}" if len(mo) else ""),
         EXPLIQUE, "Vrai vide si aucun tracé ne passe dans Mô ; sinon, ses kilomètres sont comptés par le polygone")

    morceaux[["FID", "route_type", "route_nom", "Préfecture déclarée", "Préfecture", "Région", "km_prefecture"]].rename(
        columns={"km_prefecture": "km"}).to_csv(INTERIM / "routes_par_prefecture.csv", index=False)
    test("5-06", "5", "Jointure D5 : routes classées → référentiel", "38 préfectures ; absence de Mô expliquée",
         f"Noms déclarés : {geo['prefecture_nom_bdd'].nunique()}, tous dans le référentiel : {'oui' if connue.all() else 'non'} ; "
         f"préfectures traversées par le tracé : {morceaux['Préfecture'].nunique()} sur 39 ; sans tracé : "
         f"{', '.join(sorted(set(pref['Préfecture']) - set(morceaux['Préfecture']))) or 'aucune'}",
         CONFORME if connue.all() else ANOMALIE, "O4-01 à O4-03 par préfecture, sur les morceaux du tracé")
    return geo, morceaux


def auto_ecoles(ref, pref, pays):
    a = pd.read_csv(BRUT / "auto_ecoles.csv", dtype=str)
    geo = gpd.GeoDataFrame(a.drop(columns="geometry"), geometry=gpd.GeoSeries.from_wkt(a["geometry"]), crs=4326).to_crs(UTM31N)
    geo["Préfecture déclarée"] = geo["prefecture_nom_bdd"].map(dict(zip(ref["Nom auto-écoles (D6)"], ref["Préfecture"])))
    jointe = gpd.sjoin(geo, pref[["Préfecture", "Région", "Zone", "geometry"]], how="left", predicate="within").drop(columns="index_right")
    dehors = jointe[jointe["Préfecture"].isna()]
    distances = dehors.geometry.distance(pays) if len(dehors) else pd.Series(dtype=float)
    test("4.3-08", "4.3", "Auto-écoles dans les limites du Togo, après reprojection en UTM 31N", "Toutes dans le Togo",
         f"{len(jointe) - len(dehors)} sur {len(jointe)} dans une préfecture"
         + (f" ; hors des polygones : {len(dehors)}, à {n(distances.max())} m au plus de la limite" if len(dehors) else ""),
         CONFORME if dehors.empty else EXPLIQUE, "O4-04 : auto-écoles comptées par le polygone")
    egales = jointe["Préfecture déclarée"] == jointe["Préfecture"]
    diff = jointe[~egales & jointe["Préfecture"].notna()]
    test("4.3-09", "4.3", "Auto-écoles : la préfecture déclarée est celle du polygone qui contient le point", "100 %",
         f"{int(egales.sum())} sur {len(jointe)} ({n(100 * egales.mean(), 1)} %)"
         + (f" ; autres : {', '.join(f'{a} → {b} ({c})' for (a, b), c in diff[['Préfecture déclarée', 'Préfecture']].value_counts().items())}" if len(diff) else ""),
         CONFORME if egales.all() else EXPLIQUE, "Rattachement par le polygone (R-01) ; préfecture déclarée gardée pour mémoire")
    kpo = jointe[jointe["Préfecture déclarée"] == "Kpendjal-Ouest"]
    test("5-07", "5", "Kpendjal-Ouest et « Naki-Ouest » (TG0518) : auto-écoles", "Les auto-écoles déclarées à Kpendjal-Ouest tombent dans TG0518",
         f"{len(kpo)} auto-école déclarée à Kpendjal-Ouest" + (f", dont {int((kpo['Préfecture'] == 'Kpendjal-Ouest').sum())} dans TG0518" if len(kpo) else ""),
         CONFORME if len(kpo) == 0 or (kpo["Préfecture"] == "Kpendjal-Ouest").all() else ANOMALIE, "Test sans objet s'il n'y a pas d'auto-école")
    agreees = jointe["agregation"].isin(["Agréée", "Antenne agréée"])
    test("5-08", "5", "Jointure D6 : auto-écoles → référentiel", "24 préfectures",
         f"Noms déclarés : {geo['prefecture_nom_bdd'].nunique()}, tous dans le référentiel : {'oui' if geo['Préfecture déclarée'].notna().all() else 'non'} ; "
         f"préfectures avec au moins une auto-école (polygone) : {jointe['Préfecture'].nunique()} ; "
         f"avec au moins une agréée ou antenne agréée : {jointe[agreees]['Préfecture'].nunique()} ; sans aucune : {39 - jointe['Préfecture'].nunique()}",
         CONFORME if geo["Préfecture déclarée"].notna().all() else ANOMALIE, "O4-04 à O4-07 par préfecture (R-12)")
    jointe[["FID", "nom_etablissement", "agregation", "Préfecture déclarée", "Préfecture", "Région", "Zone"]].assign(
        x_utm=jointe.geometry.x.round(1), y_utm=jointe.geometry.y.round(1)).to_csv(INTERIM / "auto_ecoles_prefecture.csv", index=False)


def chefs_lieux(ref, pref):
    capitales = hdx("tgo_admincapitals.geojson").to_crs(UTM31N)
    jointe = gpd.sjoin(capitales, pref[["Préfecture", "geometry"]], how="left", predicate="within")
    couvertes = set(jointe["Préfecture"].dropna())
    sans = sorted(set(pref["Préfecture"]) - couvertes)
    niveaux = jointe["adm_p_lvl"].map(NIVEAU_CHEF_LIEU).value_counts()
    test("5-09", "5", "Chefs-lieux HDX (D13) pour O4-08", "Un point par préfecture",
         f"{len(capitales)} points ({', '.join(f'{k} : {v}' for k, v in niveaux.items())}) dans {len(couvertes)} préfectures ; "
         f"sans point : {len(sans)} ({', '.join(sans)})",
         EXPLIQUE if sans else CONFORME,
         "O4-08 par chef-lieu incomplet : repli par le point d'étiquette HDX de la préfecture (écart 19, test 5-15)")

    # Repli de l'écart 19 : point d'étiquette HDX de niveau 2, rattaché par son code puis contrôlé par le polygone
    code = {c.strip(): r["Préfecture"] for _, r in ref.iterrows() for c in r["Codes HDX regroupés"].split(",")}
    etiquettes = hdx("tgo_adminpoints.geojson").query("admin_level == 2").to_crs(UTM31N)
    etiquettes["Préfecture"] = etiquettes["adm2_pcode"].map(code)
    repli = gpd.sjoin(etiquettes[etiquettes["Préfecture"].isin(sans)],
                      pref[["Préfecture", "geometry"]].rename(columns={"Préfecture": "Polygone"}), how="left", predicate="within")
    dedans = repli["Préfecture"] == repli["Polygone"]
    test("5-15", "5", "Points d'étiquette HDX pour les préfectures sans chef-lieu (repli de O4-08, écart 19)",
         "Un point par préfecture sans chef-lieu, dans son polygone",
         f"{repli['Préfecture'].nunique()} préfectures sur {len(sans)} ont un point ; {int(dedans.sum())} dans leur polygone",
         CONFORME if set(repli["Préfecture"]) == set(sans) and dedans.all() else ANOMALIE,
         "O4-08 : distance depuis le chef-lieu, ou depuis le point d'étiquette pour ces préfectures, signalées comme telles (C)")

    # Un point de départ par préfecture : le chef-lieu du niveau le plus fin, sinon le point d'étiquette
    chefs = (jointe.dropna(subset=["Préfecture"]).sort_values("adm_p_lvl", ascending=False).drop_duplicates("Préfecture")
             .assign(Origine="chef-lieu HDX")[["Préfecture", "name", "Origine", "geometry"]])
    points = pd.concat([chefs, repli.assign(Origine="point d'étiquette HDX")[["Préfecture", "name", "Origine", "geometry"]]])
    points.rename(columns={"name": "Point"}).assign(x_utm=points.geometry.x.round(1), y_utm=points.geometry.y.round(1)).drop(
        columns="geometry").sort_values("Préfecture").to_csv(INTERIM / "points_depart_o4_08.csv", index=False)


def rattachement_etat(geo_routes):
    etat = pd.read_csv(BRUT / "etat_reseau_routier.csv", dtype=str)
    etat["Value"] = pd.to_numeric(etat["Value"])
    troncons = etat[~etat["tronçon"].str.match(r"^(TOTAL|VOIRIES)")].pivot_table(
        index=["indicateur", "tronçon"], columns="etat", values="Value", aggfunc="first").reset_index()
    noms = geo_routes.groupby("route_nom").agg(km=("km", "sum"), type=("route_type", "first")).reset_index()
    noms["cle"] = noms["route_nom"].map(cle_troncon)
    par_cle = noms.groupby("cle")
    table = pd.read_csv(REFERENCE / "correspondance_etat_trace.csv", dtype=str, keep_default_na=False)
    correspondance = {e: c for _, c in table.iterrows() for e in c["Tronçons de l'état"].split(" | ")}
    inconnus = ({e for e in correspondance if e not in set(troncons["tronçon"])}
                | {t for c in table["Noms du tracé"] for t in c.split(" | ") if t not in set(noms["route_nom"])})
    if inconnus:
        raise ValueError(f"Table de correspondance : noms absents des fichiers : {sorted(inconnus)}")
    resultats = []
    for _, t in troncons.iterrows():
        nom, cle, axe = t["tronçon"], cle_troncon(t["tronçon"]), ""
        if nom in set(noms["route_nom"]):
            methode, trouves = "nom exact", noms[noms["route_nom"] == nom]
        elif cle in par_cle.groups:
            methode, trouves = "nom normalisé", par_cle.get_group(cle)
        elif nom in correspondance:
            c = correspondance[nom]
            methode = "axe" if c["Rattachement"] == "axe" else "nom proche, validé"
            axe, trouves = c["Axe"], noms[noms["route_nom"].isin(c["Noms du tracé"].split(" | "))]
        else:
            proche = difflib.get_close_matches(cle, list(par_cle.groups), n=1, cutoff=SIMILARITE)
            methode, trouves = (("nom proche, à valider", par_cle.get_group(proche[0])) if proche else ("non rattaché", noms.iloc[0:0]))
        resultats.append({"Type (état)": t["indicateur"], "Tronçon (état)": nom, "km (état)": t["TOTAL"],
                          "Méthode": methode, "Axe": axe, "Noms du tracé": " | ".join(trouves["route_nom"]),
                          "Types du tracé": " | ".join(sorted(trouves["type"].unique())), "km (tracé)": round(trouves["km"].sum(), 2)})
    r = pd.DataFrame(resultats)
    km_etat = r.groupby(r["Axe"].where(r["Axe"] != "", r["Tronçon (état)"]))["km (état)"].transform("sum")
    r["Rapport tracé / état"] = (r["km (tracé)"] / km_etat).where(r["Méthode"] != "non rattaché").round(2)
    r.to_csv(INTERIM / "etat_troncons_rattaches.csv", index=False)
    methodes = r["Méthode"].value_counts()
    rattache = r[r["Méthode"] != "non rattaché"]
    km_rattache = rattache["km (état)"].sum() / r["km (état)"].sum()
    q = rattache.drop_duplicates(["Axe", "Noms du tracé"])["Rapport tracé / état"].quantile([0.25, 0.5, 0.75])
    axes = rattache[rattache["Méthode"] == "axe"].drop_duplicates("Axe")
    utilises = [t for s in rattache.drop_duplicates(["Axe", "Noms du tracé"])["Noms du tracé"] for t in s.split(" | ")]
    doubles = len(utilises) - len(set(utilises))
    test("5-10", "5", "Jointure D4 → D5 : état du réseau → routes classées, par le nom du tronçon",
         "Part des 84 tronçons rattachés ; à défaut, lecture par type de route et par région",
         f"{len(rattache)} tronçons sur {len(r)} rattachés ({', '.join(f'{k} : {v}' for k, v in methodes.items())}), "
         f"soit {n(100 * km_rattache, 1)} % des km évalués ; longueur du tracé rapportée à celle de l'état : médiane {n(q[0.5], 2)} "
         f"(quartiles {n(q[0.25], 2)} et {n(q[0.75], 2)}) ; par l'axe : {len(axes)} axes ({', '.join(axes['Axe'])}), rapports de "
         f"{n(axes['Rapport tracé / état'].min(), 2)} à {n(axes['Rapport tracé / état'].max(), 2)} ; noms du tracé rattachés deux fois : {doubles}"
         + (f" ; non rattachés : {', '.join(r[r['Méthode'] == 'non rattaché']['Tronçon (état)'])}" if len(rattache) < len(r) else ""),
         EXPLIQUE if doubles == 0 else ANOMALIE,
         "Aucun identifiant commun : table de correspondance validée pour les noms proches et les axes. O3 par préfecture, "
         "au prorata de la longueur dans chaque préfecture (C) ; pour un axe, l'état est réparti le long de l'axe")

    nationales = geo_routes[geo_routes["route_type"].str.startswith("Route nationale")]
    lies = set(n for noms_ in rattache["Noms du tracé"] for n in noms_.split(" | "))
    non_eval = nationales[~nationales["route_nom"].isin(lies)]["km"].sum()
    test("5-11", "5", "Part du réseau national non évaluée (R-14)", "Longueur du tracé sans état",
         f"Routes nationales du tracé : {n(nationales['km'].sum())} km ; sans tronçon d'état rattaché : {n(non_eval)} km "
         f"({n(100 * non_eval / nationales['km'].sum(), 1)} %)",
         EXPLIQUE, "O3-06 : part non évaluée affichée, jamais comptée en bon état (R-14)")


def autres_jointures(ref):
    livret = pd.read_csv(INTERIM / "livret02_population_2022.csv")
    rgph = pd.read_csv(BRUT / "rgph_2022_population.csv", dtype=str)
    l = ref["Nom Livret 02 (D7)"].isin(set(livret["Unité"]))
    c = ref["Nom recensement CSV (D7)"].isin(set(rgph["découpage-administratif"]))
    test("5-12", "5", "Jointure D7 : recensement CSV et Livret 02 → référentiel, par le libellé", "39 sur 39",
         f"Livret 02 : {int(l.sum())} sur 39 ; recensement CSV : {int(c.sum())} sur 39 (valeurs identiques : contrôle 4.5-02)",
         CONFORME if l.all() and c.all() else ANOMALIE, "Population 2022 par préfecture")
    with zipfile.ZipFile(BRUT / "ehcvm_2021_2022_csv.zip") as z:
        zones = pd.read_csv(z.open("ehcvm_ponderations_tgo2021.csv"), usecols=["s00q01"])["s00q01"].nunique()
    test("5-13", "5", "Jointure D12 : EHCVM → 6 zones, par le code de région", "6 zones",
         f"{zones} codes de région, du 1 au 6, le 6 étant le Grand Lomé (contrôle 4.3-03)", CONFORME if zones == 6 else ANOMALIE,
         "Parts de l'EHCVM par zone, jamais par préfecture")
    test("5-14", "5", "D3 : accidents", "Aucune jointure : accidents nationaux",
         "Aucune variable territoriale (§3)", CONFORME, "O2 au niveau national (écart 1)")


def sources_hors_02(ref, pref, pays):
    """Contrôle avant affichage des sources hors 02 (03 §3.2) : elles ne sont pas profilées."""
    avec_nom = ref[ref["Nom routes classées (D5)"] != ""]
    declare = dict(zip(avec_nom["Nom routes classées (D5)"], avec_nom["Préfecture"]))  # même orthographe que les routes
    textes, ok = [], True
    for fichier in ("equipements_panneaux_signalisation.csv", "equipements_ralentisseurs.csv",
                    "equipements_passages_pietons.csv", "equipements_feux_tricolores.csv"):
        e = pd.read_csv(BRUT / fichier, dtype=str, usecols=["prefecture_nom_bdd", "geometry"])
        geo = gpd.GeoDataFrame(e, geometry=gpd.GeoSeries.from_wkt(e["geometry"]), crs=4326).to_crs(UTM31N)
        geo["geometry"] = geo.geometry.representative_point()  # passages piétons : polygones
        jointe = gpd.sjoin(geo, pref[["Préfecture", "geometry"]], how="left", predicate="within")
        dans = int(jointe["Préfecture"].notna().sum())
        accord = (jointe["prefecture_nom_bdd"].map(declare).fillna(jointe["prefecture_nom_bdd"]) == jointe["Préfecture"]).mean()
        textes.append(f"{fichier.removeprefix('equipements_').removesuffix('.csv').replace('_', ' ')} : {len(geo)} points, "
                      f"{dans} dans une préfecture, {jointe['Préfecture'].nunique()} préfectures, préfecture déclarée = polygone à {100 * accord:.1f} %".replace(".", ","))
        ok &= dans / len(geo) > 0.99
    test("4.3-10", "4.3", "Sources hors 02 : équipements de sécurité routière (contrôle avant affichage, 03 §3.2)",
         "Points dans le Togo, rattachés aux 39 préfectures", " ; ".join(textes), CONFORME if ok else ANOMALIE,
         "Couche facultative de la carte de O5, désactivée par défaut, « non utilisée dans les indicateurs »")

    l = pd.read_csv(BRUT / "longueur_route_entretenue.csv", dtype=str)
    l["Value"] = pd.to_numeric(l["Value"])
    par = l.groupby(["indicateur", "Unit"]).agg(annees=("Date", lambda d: f"{d.min()}–{d.max()}"), valeurs=("Value", lambda v: ", ".join(f"{x:g}" for x in v)))
    test("4.3-11", "4.3", "Source hors 02 : longueur de route entretenue (contrôle avant affichage, 03 §3.2)", "Années et unité",
         " ; ".join(f"{i} ({u}, {r.annees}) : {r.valeurs}" for (i, u), r in par.iterrows()), ANOMALIE,
         "Longueur entretenue citable en annexe de O3 (km, 2016–2019) ; taux de couverture (0 ou 1 %) inutilisable, transmis au 05")


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    ref = pd.read_csv(REFERENCE / "referentiel_prefectures.csv", dtype=str, keep_default_na=False)
    pref = prefectures(ref)
    pays = hdx("tgo_admin0.geojson").to_crs(UTM31N).geometry.union_all()
    geo_routes, _ = routes_par_prefecture(ref, pref, pays)
    auto_ecoles(ref, pref, pays)
    chefs_lieux(ref, pref)
    rattachement_etat(geo_routes)
    autres_jointures(ref)
    sources_hors_02(ref, pref, pays)
    pref.assign(**{"Surface (km²)": pref["Surface (km²)"].round(2)}).to_crs(4326).to_file(INTERIM / "prefectures_2022.geojson", driver="GeoJSON")
    df = pd.DataFrame(lignes)
    df.to_csv(SORTIE / "jointures.csv", index=False)
    print(f"{len(df)} tests : " + ", ".join(f"{k} {v}" for k, v in df["Résultat"].value_counts().items()))


if __name__ == "__main__":
    main()
