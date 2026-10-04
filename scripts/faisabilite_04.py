"""Étape 04 : faisabilité des 43 indicateurs du 02 (04_data_understanding.md, §8 et §10).

Pour chaque indicateur, le script vérifie sur les données que le calcul est possible : à quelle maille,
sur quelles années ou combien de préfectures (numérateur et dénominateur présents), avec quel niveau de
preuve (R-17). Il ne publie aucune valeur d'indicateur : les valeurs relèvent du 08.

Entrées : data/raw/, data/interim/ (extraction_pdf_04.py, jointures_04.py), le 02 (02_decision_matrix/
01_Matrice.csv) et la prévision du 03, lue dans la colonne « Prévu (03) » du §8 du 04.
Sorties : data/analysis/04_understanding/faisabilite_indicateurs.csv, une ligne par indicateur ;
synthese_faisabilite.csv, les comptes par objectif (§10).

Usage : .venv/bin/python scripts/faisabilite_04.py
"""
import re
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
INTERIM = RACINE / "data" / "interim"
SORTIE = RACINE / "data" / "analysis" / "04_understanding"

PA01_MAX = {"Motos (deux-roues et assimilés)": 10, "Voitures": 20, "Poids lourds": 20, "Autres": 20}  # bornes hautes de PA-01

resultats = {}


def indicateur(ident, resultat, maille, periode, couverture, preuve, justification, reserve=""):
    resultats[ident] = {"Résultat (04)": resultat, "Maille obtenue": maille, "Période": periode,
                        "Couverture": couverture, "Preuve (04)": preuve, "Réserve": reserve, "Justification": justification}


def portail(fichier):
    df = pd.read_csv(BRUT / fichier, dtype=str)
    df["Value"], df["Date"] = pd.to_numeric(df["Value"]), pd.to_numeric(df["Date"])
    return df


def annuaire(numero):
    a = pd.read_csv(INTERIM / "annuaire2024_tableaux.csv")
    return a[a["Tableau"].astype(str) == numero].pivot(index="Année", columns="Ligne", values="Valeur")


def periode(annees):
    annees = sorted(int(a) for a in annees)
    if not annees:
        return ""
    trous = sorted(set(range(annees[0], annees[-1] + 1)) - set(annees))
    return f"{annees[0]}–{annees[-1]}" + (f" (sans {', '.join(map(str, trous))})" if trous else "")


def immatriculations():
    """Catégories de O1 : portail jusqu'en 2022, annuaire ensuite ; une somme incomplète reste vide (R-10)."""
    p = portail("parc_immatricule_par_type_1.csv").pivot(index="Date", columns="types-de-vehicule", values="Value")
    a = annuaire("40.1")
    a = a[a.index > p.index.max()]
    somme = lambda df, cols: df[cols].sum(axis=1, min_count=len(cols))
    portail_cat = pd.DataFrame({"Voitures": p["Voitues"], "Motos (deux-roues et assimilés)": p["2 roues et assimilées"],
                                "Poids lourds": somme(p, ["Camions", "Semi-remorques", "Tracteurs"]),
                                "Autres": somme(p, ["Camionnettes", "Autocars/Autobus"])})
    annuaire_cat = pd.DataFrame({"Voitures": a["Voiture"], "Motos (deux-roues et assimilés)": somme(a, ["2 Roues", "3 Roues"]),
                                 "Poids lourds": somme(a, ["Camions", "Semi-remorque", "Tracteur"]),
                                 "Autres": somme(a, ["Camionnette", "Autocar/Autobus"])})
    return pd.concat([portail_cat, annuaire_cat]).dropna()


def permis():
    p = portail("permis_par_categorie.csv").pivot(index="Date", columns="categories-de-permis", values="Value")
    p = p[p.drop(columns="Total").notna().all(axis=1)]  # 2013 : total 0 sans catégorie, non renseignée
    a = annuaire("40.4")
    return list(p.index) + [an for an in a.index if an > p.index.max()]


def accidents():
    cles = portail("transports_statistiques_cles.csv")
    an_cles = set(cles[cles["indicateur"] == "Nombre de morts"]["Date"])
    return sorted(an_cles | set(annuaire("7.2").index))


def population_nationale():
    """Année → niveau de preuve : recensement (A), projection ou WPP (C)."""
    proj = portail("projections_demographiques_2011_2031.csv")
    annees = {an: "C" for an in proj["Date"].unique()}
    wpp = pd.read_csv(BRUT / "wpp2024_population_age_simple_togo.csv", sep="|", skiprows=1, usecols=["TimeLabel"])
    annees.update({an: "C" for an in wpp["TimeLabel"].unique() if an < 2010})
    annees.update({2010: "A", 2022: "A"})
    return annees


def objectif_1():
    imm = immatriculations()
    ans = list(imm.index)
    pop = population_nationale()
    indicateur("O1-01", "Cible", "National", periode(ans), f"{len(ans)} années, 4 catégories", "A",
               "Immatriculations de l'année (flux, 4.4-01) ; portail jusqu'en 2022, annuaire 2023-2024 (écart 17)")
    indicateur("O1-02", "Cible", "National", periode(ans), f"{len(ans)} années ; total = somme des types (4.1-01, 4.1-03)", "B",
               "Parts calculées sur les catégories publiées")
    indicateur("O1-03", "Cible", "National", periode(ans), f"{len(ans)} années consécutives", "B",
               "Série continue ; ruptures annotées sans lecture causale (4.2-02)", "Ruptures de 1995 et 2004 à annoter")
    commun = [an for an in ans if an in pop]
    a_niveau = [an for an in commun if pop[an] == "A"]
    indicateur("O1-04", "Cible", "National", periode(commun), f"{len(commun)} années ; population recensée : {', '.join(map(str, a_niveau))}",
               "B en 2010 et 2022, C les autres années",
               "Population de l'année (R-06) : recensements (A), projections 2011–2021 et 2023–2024 (C), WPP avant 2010 (C, écart 7)")
    debut = {cat: ans[0] + l - 1 for cat, l in PA01_MAX.items()}
    complet = [an for an in ans if an >= max(debut.values())]
    indicateur("O1-05", "Cible", "National", periode(complet), f"Fourchette complète de PA-01 pour toutes les catégories : {len(complet)} années",
               "C", "Cumul des immatriculations sur la durée de vie PA-01, en fourchette (R-11, écart 16)")
    p = permis()
    indicateur("O1-06", "Cible", "National", periode(p), f"{len(p)} années, catégories A à F", "A",
               "Permis délivrés aux examens ; 2013 non renseignée (écart 14)", "Premières délivrances non prouvées (piège D2)")
    commun_p = [an for an in p if an in pop]
    indicateur("O1-07", "Cible", "National", periode(commun_p), f"{len(commun_p)} années", "C",
               "Âges minimaux du décret n° 2022-085/PR depuis août 2022, non documentés avant (écart 6) ; population par âge simple découpée avec WPP (C)")
    indicateur("O1-08", "Non", "—", "", "Aucune variable de sexe ni d'âge (§3)", "—", "Écart 5 confirmé")
    commun_9 = [an for an in p if an in set(ans)]
    indicateur("O1-09", "Cible", "National", periode(commun_9), f"{len(commun_9)} années", "B",
               "Rapport des immatriculations et des permis de l'année, par catégorie correspondante",
               "Correspondance des catégories de véhicules et de permis à fixer au 06")


def objectif_2():
    acc = accidents()
    pop = population_nationale()
    imm = immatriculations()
    commun = [an for an in acc if an in pop]
    niveaux = "B en 2010 et 2022, C les autres années"
    indicateur("O2-01", "Repli", "National", periode(acc), f"{len(acc)} années", "A",
               "Accidents nationaux (écart 1) ; accidents « constatés », non dits corporels (écart 15)", "Libellé « accidents constatés »")
    indicateur("O2-02", "Repli", "National", periode(commun), f"{len(commun)} années", niveaux, "Population de l'année (R-06) ; national seulement (écart 1)")
    indicateur("O2-03", "Repli", "National", periode(commun), f"{len(commun)} années", niveaux,
               "Recalculé : l'indicateur publié n'est pas repris (4.4-06) ; accidents constatés (écart 15)", "Libellé « accidents constatés »")
    debut = imm.index[0] + max(PA01_MAX.values()) - 1
    commun_4 = [an for an in acc if an >= debut and an in imm.index]
    indicateur("O2-04", "Cible", "National", periode(commun_4), f"{len(commun_4)} années", "C",
               "Aucun stock publié : cumul des immatriculations sur PA-01, en fourchette (R-11, écart 16)")
    indicateur("O2-05", "Repli", "National", periode(acc), f"{len(acc)} années", "B", "Mêmes accidents au numérateur et au dénominateur", "Accidents constatés (écart 15)")
    indicateur("O2-06", "Repli", "National", periode(acc), f"{len(acc)} années", "B", "Mêmes accidents au numérateur et au dénominateur", "Accidents constatés (écart 15)")
    o = pd.read_csv(INTERIM / "oms_profil_2023.csv")
    usagers = o[o["Indicateur"].str.startswith("Répartition")]
    indicateur("O2-09", "Repli", "National, type d'usager", str(int(usagers["Année"].iloc[0])), f"{len(usagers)} types d'usager, sans sexe ni âge", "C",
               "Parts publiées par l'OMS, méthode de classement non documentée (écart 3)")
    for ident, motif in (("O2-07", "Aucune catégorie de véhicule impliqué"), ("O2-08", "Aucune catégorie de véhicule impliqué"),
                         ("O2-10", "Aucune variable d'immatriculation des véhicules impliqués"), ("O2-11", "Aucun mois"),
                         ("O2-12", "Accidents sans territoire ; repli prévu à la zone seulement"),
                         ("O2-13", "Aucun âge des conducteurs"), ("O2-14", "Aucune cause")):
        indicateur(ident, "Non", "—", "", motif + " (§3)", "—", "Écarts 1 et 2 confirmés")


def objectif_3():
    rat = pd.read_csv(INTERIM / "etat_troncons_rattaches.csv")
    rp = pd.read_csv(INTERIM / "routes_par_prefecture.csv")
    lies = rat[rat["Méthode"] != "non rattaché"]
    noms = {n for liste in lies["Noms du tracé"].dropna() for n in liste.split(" | ")}
    evalues = rp[rp["route_nom"].isin(noms)]
    nationales = rp[rp["route_type"].str.startswith("Route nationale")]
    pref_eval = evalues.groupby("Préfecture")["km"].sum()
    sans = rat[rat["Méthode"] == "non rattaché"]
    par_axe = rat[rat["Méthode"] == "axe"]
    part = lies["km (état)"].sum() / rat["km (état)"].sum()
    couverture = (f"{len(lies)} tronçons sur {len(rat)} rattachés ({f'{100 * part:.1f}'.replace('.', ',')} % des km évalués), dont "
                  f"{len(par_axe)} par l'axe ; {len(pref_eval)} préfectures ont des km évalués")
    reserves = []
    if len(par_axe):
        reserves.append(f"{', '.join(par_axe['Axe'].unique())} rattachées par l'axe (table de correspondance) : "
                        "leur état est réparti le long de l'axe, au prorata des km")
    if len(sans):
        reserves.append(f"{len(sans)} tronçons ({sans['km (état)'].sum():.0f} km) non localisés, lus au niveau national")
    reserve = " ; ".join(reserves)
    for ident, quoi in (("O3-01", "Km par état"), ("O3-02", "Part des km en mauvais état"), ("O3-03", "Part des km en travaux")):
        indicateur(ident, "Cible", "Préfecture", "2020", couverture, "C",
                   f"{quoi} : tronçons rattachés au tracé par leur nom ou par l'axe (5-10), états répartis au prorata de la longueur "
                   "dans chaque préfecture ; notation non documentée", reserve)
    types = lies["Type (état)"].nunique()
    indicateur("O3-04", "Cible", "Zone", "2020", f"{types} types de route ; {len(lies)} tronçons localisés", "C",
               "Types de l'état du réseau, zones par le tracé", reserve)
    nat_etat = rat[rat["Type (état)"].str.startswith("ROUTES")]
    indicateur("O3-05", "Cible", "Tronçon", "2020", f"{len(nat_etat)} tronçons nationaux, dont {nat_etat['Méthode'].ne('non rattaché').sum()} localisés", "C",
               "Liste des tronçons en mauvais état, triée par longueur ; état non documenté")
    sans_etat = nationales[~nationales["route_nom"].isin(noms)].groupby("Préfecture")["km"].sum()
    pct_sans_etat = f"{100 * sans_etat.sum() / nationales['km'].sum():.1f}".replace(".", ",")
    indicateur("O3-06", "Cible", "Préfecture", "2020 (état), 2021-2022 (tracé)",
               f"{nationales['Préfecture'].nunique()} préfectures avec des routes nationales ; {len(sans_etat)} ont des km sans état", "B",
               "Longueur du tracé national sans tronçon d'état rattaché (5-11) ; jamais comptée en bon état (R-14)",
               f"{sans_etat.sum():.0f} km de routes nationales sans état ({pct_sans_etat} %), affichés comme non évalués")
    e = pd.read_csv(INTERIM / "annuaire2024_tableaux.csv")
    e = e[e["Tableau"].astype(str) == "39.2"]
    indicateur("O3-07", "Repli", "National, par catégorie de route", periode(e["Année"].unique()), f"{e['Ligne'].nunique()} catégories, en %", "C",
               "Annuaire 2024, tableau 39.2 (écart 18) ; sommes à 99,5 % à 100 % (4.1-06)", "Pourcentages seulement, sans km")


def objectif_4():
    rp = pd.read_csv(INTERIM / "routes_par_prefecture.csv")
    ae = pd.read_csv(INTERIM / "auto_ecoles_prefecture.csv")
    pref = gpd.read_file(INTERIM / "prefectures_2022.geojson")
    livret = pd.read_csv(INTERIM / "livret02_population_2022.csv")
    pop = livret[(livret["Niveau"] == "préfecture") & (livret["Groupe d’âges"] == "Total") & (livret["Milieu"] == "Total") & (livret["Sexe"] == "Ensemble")]
    ref = pd.read_csv(RACINE / "data" / "reference" / "referentiel_prefectures.csv", dtype=str)
    pop = pop.merge(ref, left_on="Unité", right_on="Nom Livret 02 (D7)")
    avec_route = rp["Préfecture"].nunique()
    sans_route = sorted(set(pref["Préfecture"]) - set(rp["Préfecture"]))
    indicateur("O4-01", "Cible", "Préfecture", "Collecte 2021-2022", f"39 préfectures : {avec_route} traversées, {', '.join(sans_route)} sans tracé (vrai vide, 5-05)", "B",
               "Longueurs des morceaux de tracé par préfecture, en UTM 31N (R-15, R-16)")
    indicateur("O4-02", "Cible", "Préfecture", "Collecte 2021-2022", f"39 surfaces calculées en UTM 31N", "B", "Surfaces HDX, Golfe et Lomé Commune fusionnés (5-01)")
    indicateur("O4-03", "Cible", "Préfecture", "2022", f"{pop['Préfecture'].nunique()} préfectures avec population (Livret 02)", "B",
               "Population 2022 par préfecture (A) ; tracé 2021-2022 (R-05)")
    agreees = ae[ae["agregation"].isin(["Agréée", "Antenne agréée"])]
    avec = agreees["Préfecture"].nunique()
    indicateur("O4-04", "Cible", "Préfecture", "Collecte 2021-2022", f"{len(agreees)} auto-écoles agréées ou antennes agréées dans {avec} préfectures ; "
               f"{len(ae)} recensées dans {ae['Préfecture'].nunique()}", "A", "Comptage par le polygone (4.3-09) ; R-12", "Activité non vérifiée (écart 13)")
    indicateur("O4-05", "Cible", "Préfecture", "2022", f"39 préfectures, dont {39 - avec} sans auto-école agréée", "C",
               "R-12 : activité non vérifiée, offre étiquetée C", "Activité non vérifiée (écart 13)")
    indicateur("O4-06", "Cible", "Préfecture", "2022", f"Défini pour {avec} préfectures ; non défini pour {39 - avec}", "C",
               "R-12 ; non défini sans auto-école", "Activité non vérifiée (écart 13)")
    indicateur("O4-07", "Cible", "Préfecture", "2022", f"{39 - avec} préfectures sans auto-école agréée ni antenne agréée", "B",
               "Liste tirée du comptage, avec la population 2022", "Activité non vérifiée (écart 13)")
    with zipfile.ZipFile(BRUT / "limites_administratives_hdx.geojson.zip") as z:
        capitales = gpd.read_file(z.open("tgo_admincapitals.geojson"))
        points = gpd.read_file(z.open("tgo_adminpoints.geojson"))
    capitales = gpd.sjoin(capitales, pref[["Préfecture", "geometry"]], predicate="within")
    couvertes = capitales["Préfecture"].nunique()
    etiquettes = points[points["admin_level"] == 2]
    indicateur("O4-08", "Repli", "Préfecture", "Collecte 2021-2022", f"Chef-lieu pour {couvertes} préfectures ; point d'étiquette HDX pour les {39 - couvertes} autres "
               f"({len(etiquettes)} points disponibles)", "C",
               "Distance à vol d'oiseau en UTM 31N (R-16) depuis le chef-lieu, ou le point d'étiquette HDX à défaut (écart 19) ; sans grille de population",
               "Distance d'un point par préfecture, pas de la population ; les préfectures mesurées depuis le point d'étiquette sont signalées comme telles")
    indicateur("O4-09", "Non", "—", "", "Champs de capacité collectés mais non publiés (écart 13)", "—", "Demande de données (§10)")


def objectif_5():
    indicateur("O5-01", "Repli", "Préfecture", "2022", "Dimensions calculables par préfecture : état du réseau (O3-02), auto-écoles (O4-05)", "C",
               "Dimension risque « non déterminable » (accidents nationaux, R-10) ; dimensions en C", "Recommandation C : vérification, pas investissement (R-17)")
    indicateur("O5-02", "Repli", "Préfecture", "2022", "Rangs sur 2 dimensions", "C", "Mêmes dimensions que O5-01", "Recommandation C (R-17)")
    indicateur("O5-03", "Cible", "Préfecture", "2022", "39 préfectures (Livret 02)", "A", "Population recensée de 2022 ; part de la population à distance : non (sans grille)")
    indicateur("O5-04", "Repli", "Préfecture", "2022", "Écarts calculables pour les auto-écoles et l'état du réseau", "C", "Mêmes dimensions que O5-01", "Recommandation C (R-17)")


def prevu_03():
    """Colonne « Prévu (03) » des tableaux du §8 du 04."""
    texte = (RACINE / "04_data_understanding.md").read_text(encoding="utf-8")
    prevu = {}
    for ligne in texte.splitlines():
        m = re.match(r"^\|\s*(O[1-5]-\d\d)\s*\|", ligne)
        if m:
            prevu[m.group(1)] = [c.strip() for c in ligne.strip("|").split("|")][4]
    return prevu


def main():
    for f in (objectif_1, objectif_2, objectif_3, objectif_4, objectif_5):
        f()
    matrice = pd.read_csv(RACINE / "02_decision_matrix" / "01_Matrice.csv", dtype=str)
    prevu = prevu_03()
    df = matrice[["ID", "Objectif", "Indicateur", "Maille cible", "Preuve attendue"]].rename(columns={"Preuve attendue": "Preuve (02)"})
    df["Prévu (03)"] = df["ID"].map(prevu)
    df = df.join(pd.DataFrame.from_dict(resultats, orient="index"), on="ID")
    manquants = df[df["Résultat (04)"].isna()]["ID"].tolist()
    if manquants or len(df) != 43:
        raise SystemExit(f"Indicateurs sans résultat : {manquants}")
    df["Catégorie (03)"] = df["Prévu (03)"].str.extract(r"^(Cible|Repli|Non)")[0]
    df.to_csv(SORTIE / "faisabilite_indicateurs.csv", index=False)

    # Synthèse (§10) : le niveau d'un indicateur est le plus faible qu'il cite (« B en 2010 et 2022, C les autres années » → C)
    df["Niveau"] = df["Preuve (04)"].str.extract(r"([ABC])(?!.*[ABC])")[0]

    def synthese(g):
        calc = g[g["Résultat (04)"] != "Non"]
        compte = lambda col: "/".join(str((g[col] == c).sum()) for c in ("Cible", "Repli", "Non"))
        return pd.Series({"Indicateurs": len(g), "Prévu (03) cible/repli/non": compte("Catégorie (03)"),
                          "Établi (04) cible/repli/non": compte("Résultat (04)"),
                          "Calculables (04)": f"{len(calc)} ({100 * len(calc) / len(g):.0f} %)",
                          "À la maille cible (04)": f"{(g['Résultat (04)'] == 'Cible').sum()} ({100 * (g['Résultat (04)'] == 'Cible').mean():.0f} %)",
                          "Preuve A/B/C": "/".join(str((calc["Niveau"] == c).sum()) for c in "ABC"),
                          "Changements": ", ".join(f"{r.ID} ({r['Catégorie (03)']} → {r['Résultat (04)']})"
                                                   for _, r in g[g["Catégorie (03)"] != g["Résultat (04)"]].iterrows())})
    tableau = pd.concat([df.groupby("Objectif").apply(synthese, include_groups=False),
                         synthese(df).to_frame("Ensemble").T])
    tableau.to_csv(SORTIE / "synthese_faisabilite.csv", index_label="Objectif")
    print(tableau.drop(columns="Changements").to_string())

if __name__ == "__main__":
    main()
