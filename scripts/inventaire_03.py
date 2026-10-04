"""Étape 03 : télécharge les sources accessibles dans data/raw/ et tient le registre _SOURCES.csv.

L'inventaire recense ; il n'analyse pas. Ce script ne lit le contenu d'aucun fichier :
il télécharge, mesure la taille, calcule l'empreinte SHA-256 et note les métadonnées publiées
par le portail (producteur, licence, dernière modification, couverture déclarée).
Les sources recensées mais non téléchargées figurent aussi au registre, avec la raison.
Si un téléchargement échoue alors que le fichier local est intact (même empreinte que dans le
registre précédent), la ligne précédente est conservée et l'échec est noté en remarque.

Population par âge simple (WPP, ONU) : l'API du Data Portal exige un jeton, lu dans la variable
d'environnement ONU_DATAPORTAL_TOKEN (ou dans la ligne du même nom du fichier .env, ignoré par git).
Sans jeton, le script se replie sur le fichier mondial publié (62 Mo, tous pays) : il n'en garde
que les lignes du Togo, et le registre note la taille et l'empreinte du fichier publié. Si le
fichier local vient déjà de l'API et reste intact, il est conservé au lieu d'être remplacé.

EHCVM 2021-2022 (catalogue de microdonnées de la Banque mondiale) : le téléchargement exige un compte,
lu dans les variables d'environnement BM_MICRODATA_EMAIL et BM_MICRODATA_PASSWORD (ou dans les lignes
email et password du fichier .env). Les conditions d'usage interdisent la redistribution : le fichier
n'est pas versionné.

Usage : python scripts/inventaire_03.py [--sortie data/raw]
"""
import argparse
import csv
import gzip
import hashlib
import http.cookiejar
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PORTAIL = "https://opendata.gouv.tg"
INSEED = "https://inseed.tg"
LICENCES = {
    "other-open": "Autre (ouverte)",
    "other-closed": "Autre (non ouverte)",
    "notspecified": "Non précisée",
}
WPP_API = (
    "https://population.un.org/dataportalapi/api/v1/data/indicators/47/locations/768/"
    "start/1990/end/2024?format=csv"
)
WPP_MONDIAL = (
    "https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/"
    "WPP2024_PopulationBySingleAgeSex_Medium_1950-2023.csv.gz"
)
MICRODONNEES_BM = "https://microdata.worldbank.org"
EHCVM_2021 = f"{MICRODONNEES_BM}/index.php/catalog/6279/download/100393"

# Une entrée par fichier publié. Fichier local, codes D du 02 servis par ce fichier (ou « Hors 02 »),
# slug du jeu sur opendata.gouv.tg (ou None), URL, raison si non téléchargé.
SOURCES = [
    ("transports_statistiques_cles.csv", "D1, D2, D3, D10",
     "donnees-ouvertes-sur-les-statistiques-cles-des-transports-terrestres-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-statistiques-cles-des-transports-terrestres-au-togo/20250106-180028/observationdata-hxdpzbg.csv",
     None),
    ("parc_immatricule_par_type_1.csv", "D1",
     "donnees-ouvertes-sur-levolution-du-parc-automobile-immatricule-par-type-de-vehicules",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-levolution-du-parc-automobile-immatricule-par-type-de-vehicules/20250106-164529/observationdata-akkouh.csv",
     None),
    ("parc_immatricule_par_type_2.csv", "D1",
     "donnees-ouvertes-sur-levolution-du-parc-automobile-immatricule-par-type-de-vehicules",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-levolution-du-parc-automobile-immatricule-par-type-de-vehicules/20250106-162931/observationdata-wklhvw.csv",
     None),
    ("permis_par_categorie.csv", "D2",
     "donnees-ouvertes-sur-le-nombre-de-permis-de-conduire-delivres-par-categorie-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-le-nombre-de-permis-de-conduire-delivres-par-categorie-au-togo/20250106-173650/observationdata-wvtolmb.csv",
     None),
    ("accidents_police_gendarmerie.csv", "D3",
     "donnees-ouvertes-sur-les-accidents-de-la-circulation-constates-par-les-services-de-police-et-de-gendarmerie-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-accidents-de-la-circulation-constates-par-les-services-de-police-et-de-gendarmerie-au-togo/20241227-095242/observationdata-avqvetg.csv",
     None),
    ("accidents_bilan_police_gendarmerie.csv", "D3",
     "donnee-ouvertes-sur-le-bilan-des-accidents-de-la-circulation-constates-par-les-services-de-police-et-de-gendarmerie-au-togo",
     f"{PORTAIL}/s/resources/donnee-ouvertes-sur-le-bilan-des-accidents-de-la-circulation-constates-par-les-services-de-police-et-de-gendarmerie-au-togo/20250107-162656/observationdata-xjumsed.csv",
     None),
    ("annuaire_statistique_national_2024.pdf", "D3", None,
     f"{INSEED}/download/7668/",
     None),
    ("oms_profil_securite_routiere_2023.pdf", "D1, D3, D9, D11", None,
     "https://cdn.who.int/media/docs/default-source/country-profiles/road-safety/road-safety-2023-tgo.pdf?sfvrsn=3138d67f_3&download=true",
     None),
    ("etat_reseau_routier.csv", "D4",
     "donnees-ouvertes-sur-letat-du-reseau-routier-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-letat-du-reseau-routier-au-togo/20241227-101241/observationdata-tmdtnad.csv",
     None),
    ("geoportail_catalogue.json", "D4, D5, D6", None,
     "https://api.geodata.gouv.tg/app/get_open_data_config",
     None),
    ("routes_classees.csv", "D5",
     "donnees-ouvertes-sur-les-routes-routes-classees-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-routes-classees-au-togo/20241218-203810/file-routes-routes-classees-18-12-2024-20-38-02.csv",
     None),
    ("routes_classees_metadonnees.csv", "D5",
     "donnees-ouvertes-sur-les-routes-routes-classees-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-routes-classees-au-togo/20241218-150814/routes-routes-classees.csv",
     None),
    ("densite_reseau_routier.csv", "D5",
     "donnees-ouvertes-sur-la-densite-du-reseau-routier-par-types-de-routes-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-la-densite-du-reseau-routier-par-types-de-routes-au-togo/20241227-102505/observationdata-vnpwrie.csv",
     None),
    ("reseau_routier_complet.csv", "D5",
     "donnees-ouvertes-sur-les-routes-reseau-routier-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-reseau-routier-togo/20250102-170306/file-routes-reseau-routier-02-01-2025-16-44-05.csv",
     "138 Mo ; réseau non classé hors périmètre de O4 (01 §6)"),
    ("routes_pistes_rurales.csv", "D5",
     "donnees-ouvertes-sur-les-routes-pistes-rurales-et-statut-de-route-classee",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-pistes-rurales-et-statut-de-route-classee/20250106-173348/file-routes-pistes-rurales-statut-de-route-classee-06-01-2025-17-29-13.csv",
     "110 Mo ; pistes non classées « à confirmer » au périmètre (01 §6)"),
    ("auto_ecoles.csv", "D6",
     "donnees-ouvertes-sur-les-entreprises-auto-ecoles-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-entreprises-auto-ecoles-au-togo/20250102-162842/file-entreprises-auto-ecoles-02-01-2025-16-28-05.csv",
     None),
    ("auto_ecoles_metadonnees.csv", "D6",
     "donnees-ouvertes-sur-les-entreprises-auto-ecoles-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-entreprises-auto-ecoles/20241218-100922/entreprises-auto-ecoles.csv",
     None),
    ("auto_ecoles_vehicules_metadonnees.csv", "D6",
     "donnees-ouvertes-sur-les-auto-ecoles-vehicules-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouverte-sur-auto-ecoles-vehicules-au-togo/20241218-093525/auto-ecoles-vehicules.csv",
     None),
    ("rgph_2022_population.csv", "D7",
     "donnee-ouverte-de-recensement-general-de-la-population-et-de-lhabitat-rgph",
     f"{PORTAIL}/s/resources/donnee-ouverte-de-recensement-general-de-la-population-et-de-lhabitat-rgph/20241227-082722/observationdata-kwwolwb.csv",
     None),
    ("rgph5_livret02_age_milieu_prefecture.pdf", "D7", None,
     f"{INSEED}/download/6619/",
     None),
    ("projections_demographiques_2011_2031.csv", "D7",
     "donnees-ouvertes-sur-les-projections-demographiques-du-togo-de-2011-a-2031",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-projections-demographiques-du-togo-de-2011-a-2031/20241226-181058/observationdata-umvldld.csv",
     None),
    ("population_region_sexe_2010.csv", "D7",
     "donnees-ouvertes-sur-leffectif-de-la-population-residente-par-region-et-par-sexe-en-2010-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-leffectif-de-la-population-residente-par-region-et-par-sexe-en-2010-au-togo/20241226-184321/observationdata-hyobzgb.csv",
     None),
    ("wpp2024_population_age_simple_togo.csv", "D7", None,
     WPP_API,
     None),
    ("limites_administratives_hdx.geojson.zip", "D8", None,
     "https://data.humdata.org/dataset/e6439952-e487-4682-8251-e9688aac60e1/resource/e08c2ae7-411b-4d83-a61e-2350ba93c924/download/tgo_admin_boundaries.geojson.zip",
     None),
    ("limites_administratives_hdx.xlsx", "D8, D13", None,
     "https://data.humdata.org/dataset/e6439952-e487-4682-8251-e9688aac60e1/resource/ed920639-dad1-43a5-bd84-5c0ae5634167/download/tgo_admin_boundaries.xlsx",
     None),
    ("oms_tues_pour_100000.json", "D9", None,
     "https://ghoapi.azureedge.net/api/RS_198?$filter=SpatialDim%20in%20('TGO','BEN','GHA','BFA')",
     None),
    ("dhs_possession_moto_velo_region.json", "D12", None,
     "https://api.dhsprogram.com/rest/dhs/data?countryIds=TG&indicatorIds=HC_TRNS_H_SCT,HC_TRNS_H_BIK&breakdown=subnational&perpage=1000&f=json",
     None),
    ("ehcvm_2021_2022_csv.zip", "D12", None,
     EHCVM_2021,
     None),
    ("worldpop_tgo_2020.tif", "D13", None,
     "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/TGO/tgo_ppp_2020.tif",
     "Raster utile seulement pour O4-08 ; téléchargé à l’étape 04 si la distance est calculée"),
    ("longueur_route_entretenue.csv", "Hors 02",
     "donnees-ouvertes-sur-la-longueur-de-route-entretenue-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-la-longueur-de-route-entretenue-au-togo/20250106-170616/observationdata-vibkrrd.csv",
     None),
    ("equipements_panneaux_signalisation.csv", "Hors 02",
     "donnees-ouvertes-sur-les-routes-et-panneaux-signalisation-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-et-panneaux-signalisation-au-togo/20250106-160235/file-routes-panneaux-signalisation-06-01-2025-16-02-25.csv",
     None),
    ("equipements_ralentisseurs.csv", "Hors 02",
     "donnees-ouvertes-sur-les-routes-et-ralentisseurs",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-et-ralentisseurs/20250106-173303/file-routes-ralentisseurs-06-01-2025-17-31-20.csv",
     None),
    ("equipements_passages_pietons.csv", "Hors 02",
     "donnees-ouvertes-sur-les-routes-et-passages-pietons-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-et-passages-pietons-au-togo/20250106-160426/file-routes-passages-pietons-06-01-2025-16-03-20.csv",
     None),
    ("equipements_feux_tricolores.csv", "Hors 02",
     "donnees-ouvertes-sur-les-routes-feux-tricolores-au-togo",
     f"{PORTAIL}/s/resources/donnees-ouvertes-sur-les-routes-feux-tricolores-au-togo/20250102-163241/file-routes-feux-tricolores-02-01-2025-16-31-56.csv",
     None),
]

# Jeu, producteur, licence et page des sources hors portail (le portail les fournit par son API).
HORS_PORTAIL = {
    "annuaire_statistique_national_2024.pdf": (
        "Annuaire statistique national 2024", "INSEED", "Non déclarée", f"{INSEED}/annuaires/"),
    "oms_profil_securite_routiere_2023.pdf": (
        "Rapport mondial sur la sécurité routière 2023 : profil du Togo",
        "Organisation mondiale de la santé", "CC BY-NC-SA 3.0 IGO",
        "https://www.who.int/teams/social-determinants-of-health/safety-and-mobility/global-status-report-on-road-safety-2023"),
    "geoportail_catalogue.json": (
        "Catalogue des couches et des indicateurs du géoportail national",
        "Ministère de l’Économie numérique (géoportail national)", "Non déclarée",
        "https://geodata.gouv.tg"),
    "rgph5_livret02_age_milieu_prefecture.pdf": (
        "RGPH-5, Livret 02 : population par groupe d’âges, milieu et sexe, du national aux préfectures",
        "INSEED", "Non déclarée", f"{INSEED}/depliant-et-communique-rgph/"),
    "wpp2024_population_age_simple_togo.csv": (
        "World Population Prospects 2024 : population par âge simple et sexe (indicateur 47), Togo",
        "Nations unies, Division de la population", "CC BY 3.0 IGO", "https://population.un.org/wpp/"),
    "limites_administratives_hdx.geojson.zip": (
        "Limites administratives du Togo (COD-AB)", "OCHA / HDX, d’après GAUL (FAO)", "CC BY-IGO",
        "https://data.humdata.org/dataset/cod-ab-tgo"),
    "limites_administratives_hdx.xlsx": (
        "Limites administratives du Togo (COD-AB)", "OCHA / HDX, d’après GAUL (FAO)", "CC BY-IGO",
        "https://data.humdata.org/dataset/cod-ab-tgo"),
    "oms_tues_pour_100000.json": (
        "Taux de tués sur la route estimé (indicateur RS_198)",
        "Organisation mondiale de la santé (GHO)", "CC BY-NC-SA 3.0 IGO",
        "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/estimated-road-traffic-death-rate-(per-100-000-population)"),
    "dhs_possession_moto_velo_region.json": (
        "Ménages possédant une moto ou un vélo, par région (DHS 1998, 2013 ; MIS 2017)",
        "The DHS Program", "Conditions d’utilisation du programme DHS", "https://api.dhsprogram.com/"),
    "ehcvm_2021_2022_csv.zip": (
        "Enquête harmonisée sur les conditions de vie des ménages 2021-2022 (EHCVM-2), fichiers CSV",
        "INSEED, avec la Banque mondiale et la Commission de l’UEMOA",
        "Fichiers publics de la Banque mondiale : compte requis, ni copie ni redistribution, citation obligatoire",
        f"{MICRODONNEES_BM}/index.php/catalog/6279"),
    "worldpop_tgo_2020.tif": (
        "Population 2020 par carreau de 100 m", "WorldPop (Université de Southampton)", "CC BY 4.0",
        "https://hub.worldpop.org/geodata/listing?id=29"),
}

COLONNES = [
    "Fichier", "Codes D", "Jeu de données", "Producteur", "Page source", "URL",
    "Licence déclarée", "Dernière modification (portail)", "Couverture déclarée",
    "Statut", "Date de téléchargement", "Taille (octets)", "SHA-256", "Remarque",
]


def lire_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def metadonnees_portail(slug, cache):
    if slug not in cache:
        cache[slug] = lire_json(f"{PORTAIL}/api/1/datasets/{slug}/")
    d = cache[slug]
    couverture = d.get("temporal_coverage") or {}
    return {
        "Jeu de données": d["title"],
        "Producteur": (d.get("organization") or {}).get("name", ""),
        "Page source": f"{PORTAIL}/fr/datasets/{slug}/",
        "Licence déclarée": LICENCES.get(d.get("license"), d.get("license") or ""),
        "Dernière modification (portail)": d.get("last_modified", "")[:10],
        "Couverture déclarée": "–".join(
            filter(None, [couverture.get("start", "")[:4], couverture.get("end", "")[:4]])
        ),
    }


def ouvrir(url, entetes=None):
    url = urllib.parse.quote(url, safe=":/?=&%$(),'")
    requete = urllib.request.Request(url, headers={"User-Agent": "inventaire-03", **(entetes or {})})
    return urllib.request.urlopen(requete, timeout=300)


def secret(variable, cle_env):
    """Secret lu dans une variable d'environnement, sinon dans une ligne du fichier .env."""
    if os.environ.get(variable):
        return os.environ[variable]
    env = RACINE / ".env"
    if env.exists():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            cle, _, valeur = ligne.partition("=")
            if cle.strip() == cle_env:
                return valeur.strip().strip('"\'')
    return None


def jeton_onu():
    """Jeton du Data Portal de l'ONU."""
    return secret("ONU_DATAPORTAL_TOKEN", "ONU_DATAPORTAL_TOKEN")


def connexion_banque_mondiale():
    """Ouvre une session sur le catalogue de microdonnées : e-mail, puis mot de passe."""
    email = secret("BM_MICRODATA_EMAIL", "email")
    mot_de_passe = secret("BM_MICRODATA_PASSWORD", "password")
    if not (email and mot_de_passe):
        raise RuntimeError("identifiants du catalogue de microdonnées absents")
    ouvreur = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    ouvreur.addheaders = [("User-Agent", "inventaire-03")]
    for page, champs in (("auth/login", {"email": email}), ("auth/password", {"password": mot_de_passe})):
        with ouvreur.open(f"{MICRODONNEES_BM}/{page}", timeout=60) as r:
            jeton = dict(re.findall(r'name="(csrf_name|csrf_value)" value="([^"]*)"', r.read().decode("utf-8")))
        donnees = urllib.parse.urlencode({**jeton, **champs, "submit": "Login"}).encode()
        ouvreur.open(f"{MICRODONNEES_BM}/{page}", donnees, timeout=60).close()
    with ouvreur.open(f"{MICRODONNEES_BM}/index.php/catalog/6279/get-microdata", timeout=60) as r:
        if "download/100393" not in r.read().decode("utf-8"):
            raise RuntimeError("connexion au catalogue de microdonnées refusée")
    return ouvreur


def telecharger(url, chemin, entetes=None, ouvreur=None):
    with (ouvreur.open(url, timeout=300) if ouvreur else ouvrir(url, entetes)) as r:
        chemin.write_bytes(r.read())
    contenu = chemin.read_bytes()
    return len(contenu), hashlib.sha256(contenu).hexdigest()


def extraire_togo_wpp(url, chemin):
    """Télécharge le fichier mondial WPP hors du projet et n'en garde que les lignes du Togo.

    Les lignes retenues sont recopiées telles quelles. Renvoie la remarque du registre,
    avec la taille et l'empreinte du fichier publié.
    """
    empreinte = hashlib.sha256()
    with tempfile.TemporaryDirectory() as dossier:
        mondial = Path(dossier) / "wpp_mondial.csv.gz"
        with ouvrir(url) as r, open(mondial, "wb") as f:
            for bloc in iter(lambda: r.read(1 << 20), b""):
                empreinte.update(bloc)
                f.write(bloc)
        taille = mondial.stat().st_size
        with gzip.open(mondial, "rt", encoding="utf-8", newline="") as source, \
                open(chemin, "w", encoding="utf-8", newline="") as sortie:
            entete = source.readline()
            colonne = next(csv.reader([entete])).index("ISO3_code")
            sortie.write(entete)
            for ligne in source:
                if next(csv.reader([ligne]))[colonne] == "TGO":
                    sortie.write(ligne)
    return (
        f"Extrait : lignes ISO3_code = TGO du fichier mondial publié "
        f"({taille} octets, SHA-256 {empreinte.hexdigest()})"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sortie", type=Path, default=RACINE / "data" / "raw")
    args = parser.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=True)

    precedent = {}
    if (args.sortie / "_SOURCES.csv").exists():
        with open(args.sortie / "_SOURCES.csv", encoding="utf-8", newline="") as f:
            precedent = {r["Fichier"]: r for r in csv.DictReader(f)}

    cache, registre, erreurs, conserves = {}, [], 0, 0
    for fichier, codes, slug, url, raison in SOURCES:
        ligne = dict.fromkeys(COLONNES, "")
        ligne.update({"Fichier": fichier, "Codes D": codes, "URL": url})
        if slug:
            ligne.update(metadonnees_portail(slug, cache))
        else:
            jeu, producteur, licence, page = HORS_PORTAIL[fichier]
            ligne.update({"Jeu de données": jeu, "Producteur": producteur,
                          "Licence déclarée": licence, "Page source": page})
        if raison:
            ligne["Statut"] = f"Recensé, non téléchargé : {raison}"
        else:
            try:
                chemin = args.sortie / fichier
                statut = "Téléchargé"
                if url == WPP_API and jeton_onu():
                    taille, sha = telecharger(url, chemin, {"Authorization": f"Bearer {jeton_onu()}"})
                    ligne["Remarque"] = "Réponse de l’API du Data Portal (jeton requis) : indicateur 47, Togo (768), 1990–2024"
                elif url == WPP_API:
                    if precedent.get(fichier, {}).get("Remarque", "").startswith("Réponse de l’API"):
                        # Le fichier de l'API couvre 1990–2024 ; l'extrait ne le remplace jamais.
                        raise RuntimeError("jeton de l’ONU absent")
                    ligne["URL"] = WPP_MONDIAL
                    ligne["Remarque"] = extraire_togo_wpp(WPP_MONDIAL, chemin)
                    contenu = chemin.read_bytes()
                    taille, sha = len(contenu), hashlib.sha256(contenu).hexdigest()
                    statut = "Téléchargé (extrait)"
                elif url == EHCVM_2021:
                    taille, sha = telecharger(url, chemin, ouvreur=connexion_banque_mondiale())
                    ligne["Remarque"] = (
                        "Conditions d’usage : fichier non versionné ni redistribué ; seuls des agrégats par zone "
                        "sont publiés. Citation : INSEED, Togo – Enquête harmonisée sur les conditions de vie des "
                        "ménages 2021-2022 (EHCVM-2), réf. TGO_2021_EHCVM-2_v01_M, téléchargée sur "
                        f"microdata.worldbank.org le {date.today().isoformat()}")
                else:
                    taille, sha = telecharger(url, chemin)
                ligne.update({
                    "Statut": statut,
                    "Date de téléchargement": date.today().isoformat(),
                    "Taille (octets)": taille, "SHA-256": sha,
                })
            except Exception as e:  # le registre garde la trace de l’échec
                avant = precedent.get(fichier, {})
                local = args.sortie / fichier
                if avant.get("SHA-256") and local.exists() and \
                        hashlib.sha256(local.read_bytes()).hexdigest() == avant["SHA-256"]:
                    conserves += 1
                    ligne.update({c: avant[c] for c in ("Statut", "Date de téléchargement", "Taille (octets)", "SHA-256")})
                    note = avant.get("Remarque", "").split(" ; Nouvelle tentative")[0]
                    ligne["Remarque"] = " ; ".join(filter(None, [
                        note, f"Nouvelle tentative du {date.today().isoformat()} en échec ({e}) : "
                              f"fichier du {avant['Date de téléchargement']} conservé"]))
                else:
                    erreurs += 1
                    ligne["Statut"] = f"Échec du téléchargement : {e}"
        registre.append(ligne)
        print(f"  {ligne['Statut'][:40]:40} {fichier}")

    with open(args.sortie / "_SOURCES.csv", "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=COLONNES)
        ecrivain.writeheader()
        ecrivain.writerows(registre)
    print(f"Registre écrit : {args.sortie / '_SOURCES.csv'} ({len(registre)} fichiers, {erreurs} échec(s), "
          f"{conserves} fichier(s) conservé(s) après un échec)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
