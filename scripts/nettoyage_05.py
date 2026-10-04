"""Étape 05 : nettoyage des fichiers (05_data_preparation.md, §3 et §4).

Applique les décisions du §3 aux anomalies transmises par le 04, puis nettoie chaque besoin.

Sorties :
- data/processed/ : les tables qui n'ont pas de territoire à rattacher (D1, D2, D3, D4 national, D7
  national, D9, D10, D12, contexte de O3) ;
- data/interim/05_nettoyage/ : les tables nettoyées avant leur jointure (tronçons de l'état, tracé,
  auto-écoles, population par préfecture, équipements), reprises par jointures_05.py ;
- data/analysis/05_preparation/registre_anomalies.csv : une ligne par point transmis par le 04, avec
  sa décision et le nombre de valeurs touchées ;
- data/analysis/05_preparation/lignes_05.csv : par fichier, les lignes brutes, gardées et retirées,
  avec le motif de chaque retrait.

Aucune valeur n'est imputée : une valeur absente reste vide, jamais 0 (R-10). Un zéro n'est écrit que
s'il est prouvé, et la preuve est dans le motif. Aucun ratio. EHCVM : seuls des effectifs pondérés par
zone sortent du script (conditions d'usage de la Banque mondiale).

Usage : .venv/bin/python scripts/nettoyage_05.py
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
NETTOYE = INTERIM / "05_nettoyage"
SORTIE = RACINE / "data" / "processed"
ANALYSE = RACINE / "data" / "analysis" / "05_preparation"

DERNIERE_ANNEE_PORTAIL = 2022  # après, l'annuaire 2024 prolonge les séries (écart 17)
ARRONDI = 0.01 + 1e-9  # longueurs de l'état publiées au centième de km (4.1-05), plus la marge du calcul en flottants
ARRONDI_PCT = 0.05  # quatre parts arrondies au centième peuvent s'écarter de 100 de 0,02 (même tolérance qu'en 4.1-06)
DATE_DECISION = "2026-10-04"

# D1 : types du portail et de l'annuaire (tableau 40.1) ; groupes de O1-01 (02, Désagrégations)
TYPES_PORTAIL = {"Voitues": "Voitures", "Camionnettes": "Camionnettes", "Autocars/Autobus": "Autocars et autobus",
                 "Camions": "Camions", "Semi-remorques": "Semi-remorques", "Tracteurs": "Tracteurs",
                 "2 roues et assimilées": "Deux-roues et assimilées"}
TYPES_ANNUAIRE = {"Voiture": "Voitures", "Camionnette": "Camionnettes", "Autocar/Autobus": "Autocars et autobus",
                  "Camions": "Camions", "Semi-remorque": "Semi-remorques", "Tracteur": "Tracteurs",
                  "2 Roues": "Deux-roues et assimilées", "3 Roues": "Deux-roues et assimilées"}  # « 4 Roues moto » : absent du portail
GROUPES = {"Deux-roues et assimilées": "Moto", "Voitures": "Voiture", "Camions": "Poids lourd", "Semi-remorques": "Poids lourd",
           "Tracteurs": "Poids lourd", "Autocars et autobus": "Bus et car", "Camionnettes": "Autres"}
# D2 : catégories de permis
PERMIS_PORTAIL = {"Moto (A)": "A", "Voiture légèr (B)": "B", "Poids lourd (C)": "C", "Transport en commun (D)": "D",
                  "Semi-remorque (E)": "E", "Voiture spéciale (F)": "F"}
PERMIS_ANNUAIRE = {"Moto": "A", "Voiture légère": "B", "Poids lourd": "C", "Transport en commun": "D",
                   "Semi-remorque": "E", "Voiture spéciale (F)": "F"}
LIBELLES_PERMIS = {"A": "Moto", "B": "Voiture légère", "C": "Poids lourd", "D": "Transport en commun",
                   "E": "Semi-remorque", "F": "Voiture spéciale"}
# Ruptures de série annotées, sans lecture causale [4.2-02]
RUPTURES = {"D1": {1995, 2004}, "D2": {2016, 2019, 2022}}
# D3 : série de référence [4.4-05]
ACCIDENTS_CLES = {"Nombre de cas d'accidents de la circulation": "Accidents constatés", "Nombre de morts": "Tués",
                  "Nombre de blessés": "Blessés"}
ACCIDENTS_ANNUAIRE = {"Nombre d’accidents": "Accidents constatés", "Nombre de morts": "Tués", "Nombre de blesses": "Blessés"}
# D4
TYPES_ETAT = {"ROUTES REVETUES": "revêtue", "ROUTES EN TERRES": "non revêtue"}
ETATS = {"BON": "km_bon", "MOYEN": "km_moyen", "MAUVAIS": "km_mauvais", "TRAVAUX": "km_travaux"}
# D6 : valeurs qui disent « inconnu » (R-10)
INCONNU = {"Nsp", "Néant"}
# Hors 02 : équipements de sécurité, couche facultative (04 §7)
EQUIPEMENTS = {"equipements_feux_tricolores.csv": "Feu tricolore", "equipements_panneaux_signalisation.csv": "Panneau de signalisation",
               "equipements_passages_pietons.csv": "Passage piéton", "equipements_ralentisseurs.csv": "Ralentisseur"}
# D10
TRAFIC = {"Trafic de véhicules de transports de marchandises sur le réseau routier": "Véhicules de transport de marchandises",
          "Trafic de véhicules de transports de passagers sur le réseau routier": "Véhicules de transport de passagers"}
# D12 : codes de l'EHCVM (dictionnaire de l'enquête) et zones
EHCVM_ZONES = {1: "Maritime hors Grand Lomé", 2: "Plateaux", 3: "Centrale", 4: "Kara", 5: "Savanes", 6: "Grand Lomé"}
EHCVM_BIENS = {29: "Possède une moto", 28: "Possède une voiture", 30: "Possède un vélo"}  # s12q01
EHCVM_ACHATS = {212: "A payé un moto-taxi (7 derniers jours)", 209: "A acheté du carburant pour moto (7 derniers jours)"}  # s09bq01
DHS = {"Households possessing a motorcycle": "Ménages possédant une moto", "Households possessing a bicycle": "Ménages possédant un vélo"}
# Âges : groupes quinquennaux communs aux projections, au Livret 02 et à WPP
GROUPES_AGES = [f"{a}-{a + 4}" for a in range(0, 80, 5)] + ["80 et +"]

registre, lignes = [], []


def exiger(condition, message):
    """Contrôle préalable à un retrait ou à une décision : s'il échoue, rien n'est écrit."""
    if not condition:
        raise ValueError(message)


def memes(a, b):
    """Deux séries égales, sur le même index."""
    return a.index.equals(b.index) and bool((a == b).all())


def compter(fichier, brutes, gardees, retraits=None, note=""):
    retraits = retraits or {}
    exiger(brutes == gardees + sum(retraits.values()), f"{fichier} : {brutes} lignes ≠ {gardees} gardées + {sum(retraits.values())} retirées")
    lignes.append({"Fichier": fichier, "Lignes brutes": brutes, "Lignes gardées": gardees,
                   "Lignes retirées": sum(retraits.values()),
                   "Motifs": " ; ".join(f"{m} : {k}" for m, k in retraits.items() if k) or "aucun", "Note": note})


def anomalie(numero, ident, fichier, constat, decision, traitement, touchees, indicateurs):
    registre.append({"N°": numero, "ID (04)": ident, "Fichier": fichier, "Anomalie": constat, "Décision": decision,
                     "Traitement": traitement, "Valeurs touchées": touchees, "Indicateurs": indicateurs,
                     "Décidé le": DATE_DECISION})


def portail(fichier):
    df = pd.read_csv(BRUT / fichier, dtype=str)
    df["Value"], df["Date"] = pd.to_numeric(df["Value"]), pd.to_numeric(df["Date"])
    return df


def annuaire(numero):
    a = pd.read_csv(INTERIM / "annuaire2024_tableaux.csv")
    return a[a["Tableau"].astype(str) == numero]


def ecrire(df, nom, dossier=SORTIE):
    dossier.mkdir(parents=True, exist_ok=True)
    df.to_csv(dossier / nom, index=False)


# --- D1 : immatriculations -----------------------------------------------------------------------

def d1():
    p = portail("parc_immatricule_par_type_1.csv")
    total = p[p["types-de-vehicule"] == "Total"].set_index("Date")["Value"]
    types = p[p["types-de-vehicule"] != "Total"].copy()
    exiger(memes(types.groupby("Date")["Value"].sum(), total), "D1 : total ≠ somme des types (portail)")
    exiger(set(types["types-de-vehicule"]) == set(TYPES_PORTAIL), "D1 : types du portail inattendus")
    types["Type"] = types["types-de-vehicule"].map(TYPES_PORTAIL)
    compter("parc_immatricule_par_type_1.csv", len(p), len(types), {"ligne « Total », après contrôle total = somme des types": len(total)})

    a = annuaire("40.1").pivot(index="Ligne", columns="Année", values="Valeur")
    exiger((a.drop(index="Total").sum() == a.loc["Total"]).all(), "D1 : total ≠ somme des lignes (annuaire 40.1)")
    regroupe = a.drop(index=["Total", "4 Roues moto"]).groupby(TYPES_ANNUAIRE).sum()
    portail_large = types.pivot(index="Type", columns="Date", values="Value")
    communes = [an for an in regroupe.columns if an <= DERNIERE_ANNEE_PORTAIL]
    exiger(bool((regroupe[communes].values == portail_large.loc[regroupe.index, communes].values).all()),
           "D1 : annuaire ≠ portail sur les années communes, deux-roues = 2 roues + 3 roues")
    suite = regroupe[[an for an in regroupe.columns if an > DERNIERE_ANNEE_PORTAIL]].stack().rename("Value").reset_index()
    suite.columns = ["Type", "Date", "Value"]
    nb_lignes_annuaire = int(a.shape[0] * len([an for an in a.columns if an > DERNIERE_ANNEE_PORTAIL]))
    compter("annuaire 2024, tableau 40.1 (2023-2024)", nb_lignes_annuaire, nb_lignes_annuaire - 2 * 2,
            {"ligne « Total »": 2, "« 4 Roues moto », absent du portail": 2},
            "2 roues + 3 roues regroupés en « deux-roues et assimilées », comme le portail (contrôlé sur 2020–2022)")

    d = pd.concat([types.assign(Source="portail : parc_immatricule_par_type_1.csv")[["Date", "Type", "Value", "Source"]],
                   suite.assign(Source="annuaire statistique 2024, tableau 40.1")])
    d = d.rename(columns={"Date": "Année", "Value": "Immatriculations"})
    d["Année"], d["Immatriculations"] = d["Année"].astype(int), d["Immatriculations"].astype(int)
    d["Groupe"] = d["Type"].map(GROUPES)
    d["Mesure"] = "immatriculations de l'année (flux)"
    d["Niveau"] = "A"
    d["Rupture"] = d["Année"].isin(RUPTURES["D1"])
    d = d[["Année", "Type", "Groupe", "Immatriculations", "Mesure", "Source", "Niveau", "Rupture"]].sort_values(["Année", "Type"])
    ecrire(d, "D1_immatriculations.csv")

    deux_trois = annuaire("40.1")
    touche = deux_trois[(deux_trois["Année"] == 2024) & deux_trois["Ligne"].isin(["2 Roues", "3 Roues"])]
    anomalie(9, "4.4-01", "annuaire 2024, tableau 40.1", "Deux-roues 6 487 et trois-roues 59 106 en 2024, contre 62 736 et 4 903 en 2022",
             "Documenter", "Les deux lignes sont sommées en « deux-roues et assimilées », comme le portail ; le détail n'est pas repris",
             len(touche), "O1-01 à O1-03 : aucun impact")
    return d


# --- D2 : permis ------------------------------------------------------------------------------------

def d2():
    p = portail("permis_par_categorie.csv")
    total = p[p["categories-de-permis"] == "Total"].set_index("Date")["Value"]
    cat = p[p["categories-de-permis"] != "Total"].copy()
    somme = cat.groupby("Date")["Value"].sum()
    exiger(memes(somme, total.drop(index=[an for an in total.index if an not in somme.index])), "D2 : total ≠ somme des catégories")
    sans = [an for an in total.index if an not in somme.index]
    exiger(sans == [2013] and total[2013] == 0, "D2 : seule 2013 doit être sans catégorie, avec un total à 0")
    compter("permis_par_categorie.csv", len(p), len(cat), {"ligne « Total », après contrôle total = somme des catégories": len(total)},
            "2013 : aucune catégorie, total à 0 → catégories « non renseignées » (R-10, écart 14)")
    cat["Catégorie"] = cat["categories-de-permis"].map(PERMIS_PORTAIL)
    cat = cat.assign(Source="portail : permis_par_categorie.csv", Value=cat["Value"].astype(float))[["Date", "Catégorie", "Value", "Source"]]
    vide = pd.DataFrame({"Date": 2013, "Catégorie": list(LIBELLES_PERMIS), "Value": float("nan"),
                         "Source": "portail : permis_par_categorie.csv (2013 non publiée)"})

    a = annuaire("40.4").pivot(index="Ligne", columns="Année", values="Valeur")
    exiger((a.drop(index="Total").sum() == a.loc["Total"]).all(), "D2 : total ≠ somme des catégories (annuaire 40.4)")
    suite = a.drop(index="Total")[[an for an in a.columns if an > DERNIERE_ANNEE_PORTAIL]].stack().rename("Value").reset_index()
    suite.columns = ["Ligne", "Date", "Value"]
    suite["Catégorie"] = suite["Ligne"].map(PERMIS_ANNUAIRE)
    exiger(suite["Catégorie"].notna().all(), "D2 : catégorie de l'annuaire inconnue")
    compter("annuaire 2024, tableau 40.4 (2023-2024)", a.shape[0] * 2, len(suite), {"ligne « Total »": 2})

    d = pd.concat([cat, vide, suite.assign(Source="annuaire statistique 2024, tableau 40.4")[["Date", "Catégorie", "Value", "Source"]]])
    d = d.rename(columns={"Date": "Année", "Value": "Permis délivrés"})
    d["Année"] = d["Année"].astype(int)
    d["Permis délivrés"] = pd.to_numeric(d["Permis délivrés"]).astype("Int64")
    d["Libellé"] = d["Catégorie"].map(LIBELLES_PERMIS)
    d["Statut"] = d["Permis délivrés"].notna().map({True: "publié", False: "non renseigné"})
    d["Niveau"] = "A"
    d["Rupture"] = d["Année"].isin(RUPTURES["D2"])
    d = d[["Année", "Catégorie", "Libellé", "Permis délivrés", "Statut", "Source", "Niveau", "Rupture"]].sort_values(["Année", "Catégorie"])
    ecrire(d, "D2_permis.csv")
    return d


# --- D3 : accidents ----------------------------------------------------------------------------------

def d3():
    cles = portail("transports_statistiques_cles.csv")
    acc = cles[cles["indicateur"].isin(ACCIDENTS_CLES)].copy()
    acc["Mesure"] = acc["indicateur"].map(ACCIDENTS_CLES)
    serie = acc.set_index(["Mesure", "Date"])["Value"]
    for fichier in ("accidents_police_gendarmerie.csv", "accidents_bilan_police_gendarmerie.csv"):
        f = portail(fichier)
        f["Mesure"] = f["type"].map({"Nombre d’accidents": "Accidents constatés", "Nombre de morts": "Tués", "Nombre de blesses": "Blessés"})
        exiger((f.set_index(["Mesure", "Date"])["Value"] == serie.reindex(f.set_index(["Mesure", "Date"]).index)).all(),
               f"D3 : {fichier} ≠ statistiques clés")
        compter(fichier, len(f), 0, {"contrôle seulement : identique à la série de référence (4.4-05)": len(f)})
    mortels = cles[cles["indicateur"] == "Accidents mortels /100.000 hab"]
    autres = cles[~cles["indicateur"].isin(ACCIDENTS_CLES) & (cles["indicateur"] != "Accidents mortels /100.000 hab")
                  & ~cles["indicateur"].isin(TRAFIC)]
    compter("transports_statistiques_cles.csv", len(cles), len(acc) + int(cles["indicateur"].isin(TRAFIC).sum()),
            {"« Accidents mortels /100 000 hab », exclu (anomalie 4)": len(mortels),
             "autres séries : contrôles du 04 ou hors besoin (parc, permis, fret, rail)": len(autres)},
            "Gardées : accidents, tués et blessés (D3) ; trafic (D10)")
    anomalie(4, "4.4-06", "transports_statistiques_cles.csv",
             "« Accidents mortels /100 000 hab » : accidents constatés rapportés à la population ; 2010 calculé sur la projection de 2011",
             "Exclure", "Indicateur non repris ; O2-03 sera recalculé avec les accidents et la population (B)", len(mortels), "O2-03 : aucun impact")

    a = annuaire("7.2")
    exiger(all(serie[(ACCIDENTS_ANNUAIRE[r.Ligne], r.Année)] == r.Valeur for r in a.itertuples() if r.Année <= DERNIERE_ANNEE_PORTAIL),
           "D3 : annuaire 7.2 ≠ statistiques clés sur les années communes")
    suite = a[a["Année"] > DERNIERE_ANNEE_PORTAIL].assign(Mesure=lambda x: x["Ligne"].map(ACCIDENTS_ANNUAIRE))
    compter("annuaire 2024, tableau 7.2", len(a), len(suite), {"années 2020–2022 : contrôle seulement, identiques": int((a["Année"] <= DERNIERE_ANNEE_PORTAIL).sum())})

    d = pd.concat([acc.assign(Source="portail : transports_statistiques_cles.csv")[["Date", "Mesure", "Value", "Source"]],
                   suite.rename(columns={"Année": "Date", "Valeur": "Value"}).assign(Source="annuaire statistique 2024, tableau 7.2")[["Date", "Mesure", "Value", "Source"]]])
    d = d.rename(columns={"Date": "Année", "Value": "Valeur"})
    d["Année"], d["Valeur"] = d["Année"].astype(int), d["Valeur"].astype(int)
    d["Niveau"] = "A"
    d["Note"] = d["Mesure"].map({"Accidents constatés": "constatés par la police et la gendarmerie ; aucune source ne les dit corporels (écart 15)",
                                 "Tués": "aucune définition publiée du tué", "Blessés": ""})
    ecrire(d.sort_values(["Année", "Mesure"]), "D3_accidents.csv")

    oms = pd.read_csv(INTERIM / "oms_profil_2023.csv")
    usager = oms[oms["Indicateur"] == "Répartition des tués déclarés par type d’usager"]
    exiger(usager["Valeur"].sum() == 100, "D3 : la répartition des tués par usager ne fait pas 100 %")
    v = usager.rename(columns={"Modalité": "Type d'usager", "Valeur": "Part des tués déclarés (%)"})[["Année", "Type d'usager", "Part des tués déclarés (%)"]]
    v = v.assign(Année=v["Année"].astype(int), Source="OMS, profil de sécurité routière 2023", Niveau="C")
    ecrire(v, "D3_victimes_usager_2021.csv")
    return d, oms


# --- D4 : état du réseau -----------------------------------------------------------------------------

def d4():
    e = portail("etat_reseau_routier.csv")
    agregats = e["tronçon"].str.match(r"^(TOTAL|VOIRIES)")
    troncons = e[~agregats]
    p = troncons.pivot_table(index=["indicateur", "tronçon"], columns="etat", values="Value", aggfunc="first").reset_index()
    exiger(len(p) == troncons.groupby(["indicateur", "tronçon"]).ngroups and not troncons.duplicated(["indicateur", "tronçon", "etat"]).any(),
           "D4 : un tronçon a deux lignes pour le même état")
    etats = p[list(ETATS)].fillna(0).sum(axis=1)
    exiger(((etats - p["TOTAL"]).abs() <= ARRONDI).all(), "D4 : bon + moyen + mauvais + travaux ≠ total pour un tronçon")
    absents = {ETATS[k]: int(p[k].isna().sum()) for k in ETATS}
    p = p.rename(columns=ETATS | {"TOTAL": "km_total", "tronçon": "Tronçon"})
    p[list(ETATS.values())] = p[list(ETATS.values())].fillna(0)  # zéro prouvé : les états publiés font le total (4.1-05)
    p["Type"] = p["indicateur"].map(TYPES_ETAT)
    exiger(p["Type"].notna().all(), "D4 : type de route inattendu")
    p = p.assign(Année=2020, Source="portail : etat_reseau_routier.csv (relevé de 2020)", Niveau="C")
    ecrire(p[["Type", "Tronçon", *ETATS.values(), "km_total", "Année", "Source", "Niveau"]], "D4_etat_troncons.csv", NETTOYE)
    compter("etat_reseau_routier.csv", len(e), len(troncons),
            {"lignes de total (tronçon « TOTAL… »)": int(e["tronçon"].str.match(r"^TOTAL").sum()),
             "lignes des voiries, sans tronçon": int(e["tronçon"].str.match(r"^VOIRIES").sum())},
            f"{len(p)} tronçons ; état sans ligne = 0 km, prouvé par la somme des états publiés (4.1-05) : "
            + ", ".join(f"{k} {v}" for k, v in absents.items() if v))

    a = annuaire("39.2").rename(columns={"Ligne": "Catégorie de route", "Modalité": "État", "Valeur": "Part (%)"})
    somme = a.groupby(["Catégorie de route", "Année"])["Part (%)"].sum().round(2).rename("Somme de la ligne (%)")
    a = a.merge(somme, on=["Catégorie de route", "Année"])
    a = a.assign(Source="annuaire statistique 2024, tableau 39.2", Niveau="C")
    a["Note"] = a.apply(lambda r: f"« - » dans l'annuaire : non renseigné (R-10) ; la ligne fait {r['Somme de la ligne (%)']:g} % sans cette valeur"
                        if pd.isna(r["Part (%)"]) else "", axis=1)
    ecrire(a[["Année", "Catégorie de route", "État", "Part (%)", "Somme de la ligne (%)", "Source", "Niveau", "Note"]], "D4_etat_national_pct.csv")
    hors = somme[(somme - 100).abs() > ARRONDI_PCT]
    anomalie(1, "4.1-06", "annuaire 2024, tableau 39.2", "Deux lignes de 2022 ne font pas 100 % (99,90 % et 99,54 %)", "Documenter",
             "Pourcentages publiés, sans remise à 100 % ; somme de chaque ligne gardée dans la table", len(hors), "O3-07 : réserve déjà au 04")


# --- D5 : tracé --------------------------------------------------------------------------------------

def d5(ref):
    r = pd.read_csv(BRUT / "routes_classees.csv", dtype=str)
    r["Voies"] = pd.to_numeric(r["voies_nbr"]).astype("Int64")
    zero = int((r["Voies"] == 0).sum())
    r.loc[r["Voies"] == 0, "Voies"] = pd.NA  # une route tracée a au moins une voie (anomalie 7)
    declare = dict(zip(ref["Nom routes classées (D5)"], ref["Préfecture"]))
    r["Préfecture déclarée"] = r["prefecture_nom_bdd"].map(declare)
    exiger(r["Préfecture déclarée"].notna().all(), "D5 : préfecture déclarée hors référentiel")
    sans_nom = int(r["route_nom"].isna().sum())
    d = r.rename(columns={"route_nom": "Nom", "route_type": "Type"})[["FID", "Nom", "Type", "Voies", "Préfecture déclarée", "geometry"]]
    ecrire(d, "D5_routes_classees.csv", NETTOYE)
    compter("routes_classees.csv", len(r), len(d), note=f"0 voie → non renseigné : {zero} ; sans nom, gardés : {sans_nom}")
    anomalie(7, "profil (04 §3)", "routes_classees.csv", f"{zero} tronçons à 0 voie", "Corriger",
             "0 devient « non renseigné » (R-10) : une route tracée a au moins une voie", zero, "Aucun : aucun indicateur n'utilise le nombre de voies")


# --- D6 : auto-écoles --------------------------------------------------------------------------------

def d6(ref):
    a = pd.read_csv(BRUT / "auto_ecoles.csv", dtype=str)
    statut = a["agregation"].where(~a["agregation"].isin(INCONNU), "Non renseigné")
    inconnus = {c: int(a[c].isin(INCONNU).sum()) for c in ("adresse_etablissement", "journee_ouverture", "agregation")}
    d = pd.DataFrame({
        "FID": a["FID"], "Nom": a["nom_etablissement"], "Statut": statut,
        "Comptée (R-12)": statut.isin(["Agréée", "Antenne agréée"]),
        "Adresse": a["adresse_etablissement"].where(~a["adresse_etablissement"].isin(INCONNU)),
        "Jours d'ouverture": a["journee_ouverture"].where(~a["journee_ouverture"].isin(INCONNU)),
        "Localité": a["nom_localite"], "Canton": a["canton_nom_bdd"], "Commune": a["commune_nom_bdd"],
        "Préfecture déclarée": a["prefecture_nom_bdd"].map(dict(zip(ref["Nom auto-écoles (D6)"], ref["Préfecture"]))),
        "geometry": a["geometry"]})
    exiger(d["Préfecture déclarée"].notna().all(), "D6 : préfecture déclarée hors référentiel")
    exiger(a["activite_categorie"].nunique() == 1, "D6 : activite_categorie a plus d'une valeur")
    ecrire(d, "D6_auto_ecoles.csv", NETTOYE)
    compter("auto_ecoles.csv", len(a), len(d), note="« Nsp » ou « Néant » → non renseigné : " + ", ".join(f"{k} {v}" for k, v in inconnus.items())
            + " ; colonne activite_categorie retirée : une seule valeur, « {Auto-école} » (04 §6)")
    anomalie(8, "4.1-08", "auto_ecoles.csv", f"{inconnus['agregation']} auto-écoles au statut « Néant »", "Documenter",
             "Statut « non renseigné » ; gardées dans la table, jamais comptées (R-12)", inconnus["agregation"],
             "O4-04 à O4-08 : aucun impact, déjà hors des auto-écoles comptées")


# --- D7 : population -----------------------------------------------------------------------------------

def groupe_quinquennal(age):
    return "80 et +" if age >= 80 else f"{age // 5 * 5}-{age // 5 * 5 + 4}"


def d7():
    livret = pd.read_csv(INTERIM / "livret02_population_2022.csv")
    pref = livret[livret["Niveau"] == "préfecture"].rename(columns={"Unité": "Nom Livret 02", "Valeur": "Population"})
    ecrire(pref[["Nom Livret 02", "Groupe d’âges", "Milieu", "Sexe", "Population", "Lecture"]], "D7_population_prefecture_2022.csv", NETTOYE)
    milieux = livret[livret["Milieu"].isin(["Urbain", "Rural"])]  # les totaux reprennent l'écart : comptés comme au 04
    large = milieux.pivot_table(index=["Niveau", "Unité", "Groupe d’âges", "Milieu"], columns="Sexe", values="Valeur", aggfunc="first")
    ecart = large.dropna()
    ecart = ecart[ecart["Hommes"] + ecart["Femmes"] != ecart["Ensemble"]]
    compter("Livret 02 (extraction du 04)", len(livret), len(pref),
            {"niveaux pays, région et district : contrôles et série nationale": int((livret["Niveau"] != "préfecture").sum())},
            f"cellules « - » non renseignées : {int(pref['Population'].isna().sum())}")
    anomalie(2, "4.1-09", "Livret 02", "Écart d'une personne (hommes ruraux de Doufelgou, 25-29 ans et 85 ans et plus), repris dans la Kara et au Togo",
             "Documenter", "Valeurs publiées ; la colonne « Ensemble » fait référence ; aucune correction", len(ecart), "O1-07, O4-03, PA-03 : une personne, aucun impact")

    proj = portail("projections_demographiques_2011_2031.csv")
    p2010 = portail("population_region_sexe_2010.csv")
    pop2010 = p2010[(p2010["région"] == "Togo") & (p2010["sexe"] == "Total")]["Value"].item()
    togo = livret[(livret["Unité"] == "Togo") & (livret["Milieu"] == "Total") & (livret["Sexe"] == "Ensemble")].set_index("Groupe d’âges")["Valeur"]
    pop2022 = togo["Total"]
    wpp = pd.read_csv(BRUT / "wpp2024_population_age_simple_togo.csv", sep="|", skiprows=1)
    wpp = wpp[(wpp["Variant"] == "Median") & (wpp["Sex"] == "Both sexes")]
    wpp_total = wpp.groupby("TimeLabel")["Value"].sum()

    nat = proj[(proj["tranche-d-âges"] == "Togo") & (proj["sexe"] == "Total")].set_index("Date")["Value"]
    serie = [{"Année": an, "Population": round(pop2010 * wpp_total[an] / wpp_total[2010]),
              "Source": "reconstituée : recensement 2010 × croissance WPP 2024 (variante médiane) (écart 7)", "Niveau": "C"} for an in range(1990, 2010)]
    serie += [{"Année": 2010, "Population": pop2010, "Source": "recensement 2010 (population_region_sexe_2010.csv)", "Niveau": "A"}]
    serie += [{"Année": an, "Population": int(nat[an]), "Source": "projections de l'INSEED 2011-2031", "Niveau": "C"}
              for an in range(2011, 2025) if an != 2022]
    serie += [{"Année": 2022, "Population": int(pop2022), "Source": "recensement 2022 (RGPH-5, Livret 02)", "Niveau": "A"}]
    ecrire(pd.DataFrame(serie).sort_values("Année"), "D7_population_nationale.csv")

    # Population nationale par âge : projections (2011–2024 hors 2022), Livret 02 (2022), parts de WPP avant 2011
    pa = proj[(proj["sexe"] == "Total") & (proj["tranche-d-âges"] != "Togo")].copy()
    pa["Groupe"] = pa["tranche-d-âges"].str.replace(" ", "").str.replace("80ouplus", "80 et +")
    exiger(set(pa["Groupe"]) == set(GROUPES_AGES), "D7 : groupes d'âges des projections inattendus")
    ages = [{"Année": r.Date, "Groupe d'âges": r.Groupe, "Population": int(r.Value), "Source": "projections de l'INSEED 2011-2031", "Niveau": "C"}
            for r in pa.itertuples() if 2011 <= r.Date <= 2024 and r.Date != 2022]
    l22 = togo.drop(index="Total").rename(index={"0": "0-4", "1-4": "0-4", "80-84": "80 et +", "85 et +": "80 et +", "ND": "Non déclaré"})
    ages += [{"Année": 2022, "Groupe d'âges": g, "Population": int(v), "Source": "recensement 2022 (RGPH-5, Livret 02)", "Niveau": "A"}
             for g, v in l22.groupby(level=0).sum().items()]
    wpp["Groupe"] = wpp["AgeStart"].map(groupe_quinquennal)
    parts = wpp.groupby(["TimeLabel", "Groupe"])["Value"].sum() / wpp_total
    population = {s["Année"]: s["Population"] for s in serie}
    ages += [{"Année": an, "Groupe d'âges": g, "Population": round(population[an] * parts[(an, g)]),
              "Source": "population nationale × parts par âge de WPP 2024 (variante médiane)", "Niveau": "C"}
             for an in range(2007, 2011) for g in GROUPES_AGES]
    ordre = {g: i for i, g in enumerate(GROUPES_AGES + ["Non déclaré"])}
    ages = pd.DataFrame(ages).sort_values(["Année", "Groupe d'âges"], key=lambda s: s.map(ordre) if s.name == "Groupe d'âges" else s)
    ecrire(ages, "D7_population_age_nationale.csv")


# --- D9 à D13 et contexte ----------------------------------------------------------------------------

def contexte(oms):
    j = json.loads((BRUT / "oms_tues_pour_100000.json").read_text())["value"]
    rep = [{"Indicateur": "Tués estimés pour 100 000 habitants", "Pays": v["SpatialDim"], "Année": v["TimeDim"], "Valeur": v["NumericValue"],
            "Borne basse": v["Low"], "Borne haute": v["High"], "Unité": "pour 100 000 habitants", "Source": "OMS, Global Health Observatory (RS_198)"} for v in j]
    est = oms[oms["Indicateur"] == "Tués estimés par l’OMS"].set_index("Modalité")["Valeur"]
    rep.append({"Indicateur": "Tués estimés par l'OMS (repère SE-03, jamais une correction des tués déclarés)", "Pays": "TGO", "Année": 2021,
                "Valeur": est["valeur centrale"], "Borne basse": est["borne basse"], "Borne haute": est["borne haute"], "Unité": "tués",
                "Source": "OMS, profil de sécurité routière 2023"})
    ecrire(pd.DataFrame(rep).assign(Niveau="C"), "D9_repere_oms.csv")
    km_oms = oms[oms["Indicateur"] == "Kilomètres revêtus"]
    usager = oms["Indicateur"] == "Répartition des tués déclarés par type d’usager"
    compter("profil OMS (extraction du 04)", len(oms), int(usager.sum()) + len(est),
            {"« Kilomètres revêtus », exclu (anomalie 5)": len(km_oms),
             "doublons de D1, D3 ou du repère RS_198 (4.4-04)": len(oms) - int(usager.sum()) - len(est) - len(km_oms)})
    anomalie(5, "4.4-12", "profil OMS 2023", "11 777 km revêtus en 2021, 5,3 fois le réseau revêtu", "Exclure",
             "Chiffre sans définition ni périmètre, jamais repris", len(km_oms), "Aucun")

    cles = portail("transports_statistiques_cles.csv")
    t = cles[cles["indicateur"].isin(TRAFIC)]
    ecrire(pd.DataFrame({"Année": t["Date"].astype(int), "Indicateur": t["indicateur"].map(TRAFIC), "Valeur": t["Value"],
                         "Unité": t["Unit"], "Source": "portail : transports_statistiques_cles.csv", "Niveau": "C"}), "D10_trafic.csv")

    l = portail("longueur_route_entretenue.csv")
    km = l[l["indicateur"] == "Longueur de route entretenue"]
    ecrire(pd.DataFrame({"Année": km["Date"].astype(int), "Longueur entretenue (km)": km["Value"],
                         "Source": "portail : longueur_route_entretenue.csv", "Niveau": "C"}), "contexte_entretien.csv")
    compter("longueur_route_entretenue.csv", len(l), len(km), {"taux de couverture de l'entretien, exclu (anomalie 6)": len(l) - len(km)})
    anomalie(6, "4.3-11", "longueur_route_entretenue.csv", "Taux de couverture de l'entretien routier : 0 ou 1 %", "Exclure le taux",
             "La longueur entretenue (km, 2016–2019) est gardée, en contexte de O3", len(l) - len(km), "Contexte de O3 : aucun impact")


def equipements():
    couches, reparees = [], 0
    for fichier, type_ in EQUIPEMENTS.items():
        e = pd.read_csv(BRUT / fichier, dtype=str)
        g = gpd.GeoSeries.from_wkt(e["geometry"])
        invalides = ~g.is_valid
        reparees += int(invalides.sum())
        # Polygones qui se recoupent : géométrie réparée (shapely.make_valid), puis calée sur une grille de 1e-9 degré (0,1 mm),
        # qui retire les débris de surface nulle laissés par la réparation ; la surface enclose est contrôlée par validation_05.py (7-21)
        g[invalides] = g[invalides].make_valid().set_precision(1e-9)
        exiger(g.is_valid.all() and not g.is_empty.any(), f"Équipements : géométrie irréparable dans {fichier}")
        couches.append(pd.DataFrame({"FID": e["FID"], "Type": type_, "geometry": g.to_wkt(rounding_precision=-1)}))  # pleine précision
        compter(fichier, len(e), len(e), note=f"géométries invalides réparées : {int(invalides.sum())}" if invalides.any() else "")
    ecrire(pd.concat(couches), "equipements.csv", NETTOYE)
    anomalie(10, "nouvelle (05)", "equipements_passages_pietons.csv", f"{reparees} polygones de passages piétons invalides : leur contour se recoupe",
             "Corriger", "Géométrie réparée (shapely.make_valid), calée sur une grille de 1e-9 degré (0,1 mm) qui retire les débris de surface nulle ; nombre d'équipements gardé ; surface contrôlée en 7-21", reparees,
             "Aucun : couche facultative, hors 02")


def d12():
    with zipfile.ZipFile(BRUT / "ehcvm_2021_2022_csv.zip") as z:
        cle = ["grappe", "menage"]
        pond = pd.read_csv(z.open("ehcvm_ponderations_tgo2021.csv"), usecols=cle + ["poids", "s00q01"])
        sections = {"biens (section 12)": (pd.read_csv(z.open("s12_me_tgo2021.csv"), usecols=cle + ["s12q01", "s12q02"]), "s12q01", "s12q02", EHCVM_BIENS),
                    "achats des 7 derniers jours (section 9B)": (pd.read_csv(z.open("s09b_me_tgo2021.csv"), usecols=cle + ["s09bq01", "s09bq02"]), "s09bq01", "s09bq02", EHCVM_ACHATS)}
    lignes_zone = []
    for section, (df, code, oui, articles) in sections.items():
        exiger((df[oui] == 1).all(), f"D12 : la section {section} publie des réponses autres que « oui »")
        remplie = pond.merge(df[cle].drop_duplicates(), on=cle, how="left", indicator=True)
        remplie["remplie"] = remplie["_merge"] == "both"
        for art, libelle in articles.items():
            avec = df[df[code] == art][cle].drop_duplicates().assign(avec=True)
            m = remplie.merge(avec, on=cle, how="left")
            m["avec"] = m["avec"].eq(True)
            for z_, g in m.groupby("s00q01"):
                lignes_zone.append({"Zone": EHCVM_ZONES[z_], "Mesure": libelle, "Section": section,
                                    "Ménages concernés (pondérés)": round(g.loc[g["avec"], "poids"].sum()),
                                    "Ménages ayant rempli la section (pondérés)": round(g.loc[g["remplie"], "poids"].sum()),
                                    "Ménages non renseignés (pondérés)": round(g.loc[~g["remplie"], "poids"].sum()),
                                    "Ménages enquêtés": len(g)})
    ecrire(pd.DataFrame(lignes_zone).assign(Source="EHCVM 2021-2022 (INSEED, Banque mondiale)", Niveau="C",
                                            Note="ligne absente = « non » si la section est remplie, « non renseigné » sinon (04 §6)"), "D12_menages_zone.csv")

    dhs = pd.DataFrame(json.loads((BRUT / "dhs_possession_moto_velo_region.json").read_text())["Data"])
    dhs = pd.DataFrame({"Année": dhs["SurveyYear"], "Indicateur": dhs["Indicator"].map(DHS), "Région (libellé DHS)": dhs["CharacteristicLabel"],
                        "Part des ménages (%)": dhs["Value"], "Source": "DHS (enquêtes démographiques et de santé)", "Niveau": "C",
                        "Note": dhs["CharacteristicLabel"].map({"Ensemble Maritime": "inclut Lomé", "..Maritime": "sans Lomé", "..Lomé": "Lomé seul"}).fillna("")})
    ecrire(dhs.sort_values(["Indicateur", "Année", "Région (libellé DHS)"]), "D12_dhs_region.csv")


def main():
    for d in (SORTIE, NETTOYE, ANALYSE):
        d.mkdir(parents=True, exist_ok=True)
    ref = pd.read_csv(REFERENCE / "referentiel_prefectures.csv", dtype=str, keep_default_na=False)
    imm, permis = d1(), d2()
    anomalie(3, "4.2-02", "parc_immatricule_par_type_1.csv ; permis_par_categorie.csv",
             "Ruptures de série : parc en 1995 et 2004 ; permis en 2016, 2019 et 2022", "Documenter",
             "Valeurs gardées ; colonne « Rupture » dans D1 et D2, pour les annoter ; ni lissage ni exclusion",
             int(imm["Rupture"].sum() + permis["Rupture"].sum()), "O1-01 à O1-03, O1-06 : annotées, sans lecture causale (H1)")
    _, oms = d3()
    d4()
    d5(ref)
    d6(ref)
    d7()
    contexte(oms)
    equipements()
    d12()
    pd.DataFrame(registre).sort_values("N°").to_csv(ANALYSE / "registre_anomalies.csv", index=False)
    pd.DataFrame(lignes).to_csv(ANALYSE / "lignes_05.csv", index=False)
    print(f"{len(registre)} anomalies au registre ; {len(lignes)} fichiers comptés")


if __name__ == "__main__":
    main()
