"""Étape 04 : profil de chaque fichier et de chaque variable (04_data_understanding.md, §3).

Le profil lit ; il ne nettoie pas : data/raw/ et data/reference/ ne sont jamais modifiés.
Périmètre : les fichiers téléchargés des besoins D1 à D13 (registre data/raw/_SOURCES.csv, hors
sources « Hors 02 ») et les tables de data/reference/.

Sorties, dans data/analysis/04_understanding/ :
- profil_fichiers.csv : une ligne par table (un classeur Excel, une archive ou un JSON en contiennent
  plusieurs) : format, encodage, séparateur, disposition, volumétrie, années, unités, cellules vides,
  doublons, remarques ;
- profil_variables.csv : une ligne par variable (colonne d'une table large, ou série d'un fichier long
  du portail) : type, unité, valeurs, vides, modalités, extrêmes, zéros, valeurs atypiques, années,
  usage et niveau de preuve (R-17) ;
- rapports/*.html : rapports ydata-profiling, non versionnés. L'EHCVM n'en a pas : ses conditions
  d'usage interdisent toute redistribution, et seules des statistiques agrégées sortent du script.

Une cellule vide est comptée, jamais remplacée par zéro (R-10). Les PDF n'ont qu'une ligne de fichier :
leurs tableaux sont extraits par extraction_pdf_04.py.

Usage : .venv/bin/python scripts/profil_04.py [--sans-rapports]
"""
import argparse
import csv
import io
import json
import os
import re
import time
import warnings
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
from pypdf import PdfReader

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
REFERENCE = RACINE / "data" / "reference"
SORTIE = RACINE / "data" / "analysis" / "04_understanding"

BESOINS_REFERENCE = {
    "referentiel_prefectures.csv": "D8",
    "chronologie_reformes.csv": "D11",
    "ages_minimaux_permis.csv": "PA-05",
}
# Format long du portail : une valeur par ligne, décrite par l'indicateur et ses modalités.
COLONNES_LONGUES = {"Unit", "Date", "Value"}
# Colonne des unités d'un fichier long (territoire, tronçon, âge) : hors de la clé de série.
UNITES_LONGUES = {
    "etat_reseau_routier.csv": "tronçon",
    "rgph_2022_population.csv": "découpage-administratif",
    "projections_demographiques_2011_2031.csv": "tranche-d-âges",
    "population_region_sexe_2010.csv": "région",
}
# EHCVM : fichiers utiles (03 §7) et colonnes lues ; ni coordonnées GPS ni texte libre.
EHCVM_UTILES = {
    "s00_me_tgo2021.csv": ["grappe", "menage", "vague", "s00q01", "s00q02", "s00q04"],
    "s09b_me_tgo2021.csv": ["grappe", "menage", "vague", "s09bq01", "s09bq02", "s09bq03"],
    "s12_me_tgo2021.csv": ["grappe", "menage", "vague", "s12q01", "s12q02"],
    "ehcvm_ponderations_tgo2021.csv": ["grappe", "menage", "poids", "s00q01", "s00q02", "s00q04"],
}
# Année de la mesure, avant la date de publication (« Date » de l'OMS)
COLONNES_ANNEE = ("TimeDim", "TimeLabel", "SurveyYear", "Date")
# Colonne territoriale d'une table large : la première présente, de la plus fine à la plus large.
COLONNES_TERRITOIRE = (
    "prefecture_nom_bdd", "Préfecture", "adm4_pcode", "adm3_pcode", "adm2_pcode", "adm1_pcode",
    "adm0_pcode", "CharacteristicLabel", "SpatialDim", "s00q01",
)
COLONNES_IDENTIFIANT = {"FID", "Id", "DataId", "id", "No."}
# Valeurs qui tiennent lieu de réponse dans une colonne de texte : comptées, jamais interprétées.
REMPLACEMENTS = {"nsp", "néant", "neant", "n/a", "na", "nd", "-", "--", "?", "inconnu", "non renseigné", "0"}
WKT = re.compile(r"^\s*(MULTI)?(POINT|LINESTRING|POLYGON)\s*\(", re.I)
MODALITES_MAX = 30

# Usage et niveau de preuve des variables utilisées (R-17) : A mesuré, B calculé, C estimé.
# (fichier, table ou None, variable ou None, usage, niveau, justification) ; la première règle qui
# s'applique l'emporte. Les motifs sont des expressions régulières ; une variable sans règle n'est
# pas utilisée par un indicateur (dimension, identifiant, champ hors périmètre).
COMPTAGE = "Comptage administratif publié, lu tel quel"
NIVEAUX = [
    # D1, D2, D3, D10 : séries nationales du portail
    ("transports_statistiques_cles.csv", None, r"^Accidents mortels", "contrôle", "C",
     "Indicateur pré-calculé, mal nommé : accidents constatés (pas les mortels) / population de l'INSEED (§4.4)"),
    ("transports_statistiques_cles.csv", None, r"^Trafic", "contexte", "C",
     "Comptage de trafic national, méthode non documentée (D10)"),
    ("transports_statistiques_cles.csv", None, r"chemins de fer|rails|fret", "", "", ""),
    ("transports_statistiques_cles.csv", None, r"^Evolution des premières mise", "calcul", "A",
     COMPTAGE + " ; véhicules neufs seulement (annuaire 2024, tableau 40.2)"),
    ("transports_statistiques_cles.csv", None, None, "calcul", "A", COMPTAGE + ", national, annuel"),
    (r"parc_immatricule_par_type_[12]\.csv", None, None, "calcul", "A",
     COMPTAGE + " ; immatriculations de l'année, un flux (§4.4)"),
    ("permis_par_categorie.csv", None, None, "calcul", "A", "Comptage des permis délivrés aux examens"),
    (r"accidents_(bilan_)?police_gendarmerie\.csv", None, None, "calcul", "A",
     "Comptage déclaré par la police et la gendarmerie ; sous-déclaration (piège D3)"),
    # D4, D5
    ("etat_reseau_routier.csv", None, None, "calcul", "C",
     "Longueurs déclarées par état ; notation dont la méthode n'est pas documentée (piège D4)"),
    ("routes_classees.csv", None, r"^geometry$", "calcul", "B",
     "Longueurs et rattachements calculés en UTM 31N à partir du tracé (R-16)"),
    ("routes_classees.csv", None, r"^(route_type|route_classee|route_recouvrement|voies_nbr)$", "calcul", "A",
     "Attribut publié par le producteur, compté tel quel"),
    ("routes_classees.csv", None, r"^(region|prefecture)_nom_bdd$", "jointure", "A",
     "Rattachement déclaré, contrôlé par le polygone (§4.3)"),
    ("routes_classees.csv", None, r"^route_nom$", "jointure", "A", "Seule clé possible pour l'état du réseau (§5)"),
    ("densite_reseau_routier.csv", None, None, "contrôle", "C",
     "Indicateur pré-calculé : surface et longueurs non documentées"),
    # D6
    ("auto_ecoles.csv", None, r"^geometry$", "calcul", "A",
     "Position publiée ; géocodage contrôlé par le polygone (§4.3)"),
    ("auto_ecoles.csv", None, r"^agregation$", "calcul", "A", "Statut d'agrément publié (R-12)"),
    ("auto_ecoles.csv", None, r"^journee_ouverture$", "contrôle", "C",
     "Jours d'ouverture déclarés : ne prouvent pas l'activité (R-12, écart 13)"),
    ("auto_ecoles.csv", None, r"^activite_categorie$", "contrôle", "sans objet",
     "Une seule modalité : la catégorie de l'établissement, pas son activité (écart 13)"),
    ("auto_ecoles.csv", None, r"^(region|prefecture)_nom_bdd$", "jointure", "A",
     "Rattachement déclaré, contrôlé par le polygone (§4.3)"),
    ("auto_ecoles.csv", None, r"^nom_etablissement$", "contrôle", "A", "Repérage des doublons (piège D6)"),
    (r".*_metadonnees\.csv", None, None, "dictionnaire", "sans objet", "Description des champs du jeu"),
    # D7
    ("rgph_2022_population.csv", None, None, "calcul", "A", "Recensement exhaustif de 2022 (RGPH-5)"),
    ("population_region_sexe_2010.csv", None, None, "calcul", "A", "Recensement de 2010 (RGPH-4)"),
    ("projections_demographiques_2011_2031.csv", None, None, "calcul", "C",
     "Projection de l'INSEED, méthode non jointe : une estimation, pas un comptage"),
    ("wpp2024_population_age_simple_togo.csv", None, r"^Value$", "calcul", "C",
     "Estimation modélisée de l'ONU ; seules la structure par âge et l'évolution servent (03 §7)"),
    # D8, D13
    ("limites_administratives_hdx.geojson.zip", r"^tgo_admin[012]\.geojson$", r"^geometry$", "calcul", "B",
     "Surfaces et rattachements calculés en UTM 31N (R-16) ; Golfe et Lomé Commune fusionnés (§5)"),
    ("limites_administratives_hdx.geojson.zip", r"^tgo_admincapitals\.geojson$", r"^geometry$", "calcul", "C",
     "Chef-lieu pris comme approximation du lieu de résidence (O4-08, piège D13)"),
    ("limites_administratives_hdx.xlsx", r"^tgo_admin2$", r"^area_sqkm$", "contrôle", "C",
     "Surface pré-calculée, projection non documentée ; recalculée en UTM 31N"),
    ("limites_administratives_hdx.xlsx", r"^tgo_admin2$", r"^adm2_(pcode|name)$", "référentiel", "sans objet",
     "Clé du référentiel des préfectures (D8)"),
    # D9, D11, D12, PA-05
    ("oms_tues_pour_100000.json", None, r"^NumericValue$", "repère", "C", "Estimation modélisée de l'OMS (SE-03)"),
    ("chronologie_reformes.csv", None, r"^(Date|Mesure)$", "contexte", "sans objet",
     "Table compilée, une source par ligne : pas une mesure"),
    ("dhs_possession_moto_velo_region.json", None, r"^Value$", "contexte", "C",
     "Part de ménages déclarée, publiée par le programme DHS"),
    ("ehcvm_2021_2022_csv.zip", None, r"^(s09bq0[1-3]|s12q0[12])$", "contexte", "C",
     "Déclaration des ménages ; ligne absente = « non » si la section est remplie ; parts pondérées par zone (03 §5)"),
    ("ehcvm_2021_2022_csv.zip", None, r"^poids$", "calcul", "sans objet", "Pondération de l'enquête"),
    ("ehcvm_2021_2022_csv.zip", r"ponderations", r"^s00q01$", "jointure", "sans objet", "Zone d'enquête (6 zones)"),
    ("ages_minimaux_permis.csv", None, r"^Âge minimal$", "calcul", "C",
     "Décret n° 2022-085/PR depuis août 2022, non documenté avant : C sur la série 2007–2024 ; niveau par ligne dans la table"),
    ("referentiel_prefectures.csv", None, None, "référentiel", "sans objet", "Référentiel arrêté au 03 (R-01)"),
]

COLONNES_FICHIERS = [
    "Fichier", "Besoin", "Table", "Format", "Encodage", "Séparateur", "Disposition", "Lignes", "Colonnes",
    "Années", "Unités (colonne)", "Cellules vides (%)", "Doublons", "Remarques",
]
COLONNES_VARIABLES = [
    "Fichier", "Table", "Variable", "Type", "Unité", "Valeurs", "Vides", "Vides (%)", "Modalités (nombre)",
    "Modalités", "Min", "Max", "Zéros", "Atypiques", "Années", "Années absentes", "Unités",
    "Usage", "Niveau de preuve", "Justification",
]


def court(valeur, longueur=60):
    texte = str(valeur).replace("\n", " ")
    return texte if len(texte) <= longueur else texte[: longueur - 1] + "…"


def nombre(x):
    return "" if pd.isna(x) else (str(int(x)) if float(x).is_integer() else f"{x:.6g}")


def plages(annees):
    """[2003, 2004, 2005, 2010] → « 2003–2005, 2010 »."""
    morceaux, debut = [], None
    for i, a in enumerate(annees):
        debut = a if debut is None else debut
        if i + 1 == len(annees) or annees[i + 1] != a + 1:
            morceaux.append(str(a) if a == debut else f"{debut}–{a}")
            debut = None
    return ", ".join(morceaux)


def texte_brut(s):
    """Listes et dictionnaires (JSON) en texte ; le reste inchangé."""
    return s.map(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)


def est_vide(s):
    if isinstance(s, gpd.GeoSeries):
        return s.isna() | s.is_empty
    return s.isna() | s.astype(str).str.strip().eq("")


def est_geometrie(s):
    if isinstance(s, gpd.GeoSeries):
        return True
    valeurs = s[~est_vide(s)].astype(str).head(20)
    return len(valeurs) > 0 and valeurs.str.match(WKT).all()


def niveau(fichier, table, variable):
    for f, t, v, usage, niv, justification in NIVEAUX:
        if (re.fullmatch(f, fichier) and (t is None or re.search(t, table))
                and (v is None or re.search(v, variable))):
            return {"Usage": usage, "Niveau de preuve": niv, "Justification": justification}
    return {}


def profil_geometrie(s):
    vide = est_vide(s)
    if isinstance(s, gpd.GeoSeries):
        geo, illisibles = s[~vide], 0
    else:
        geo = gpd.GeoSeries(shapely.from_wkt(s[~vide].astype(str), on_invalid="ignore"))
        illisibles = int(geo.isna().sum())
        geo = geo.dropna()
    types = geo.geom_type.value_counts()
    invalides = int((~geo.is_valid).sum())
    xmin, ymin, xmax, ymax = geo.total_bounds if len(geo) else [float("nan")] * 4
    atypiques = [f"{n} {etiquette}" for n, etiquette in ((invalides, "invalides"), (illisibles, "illisibles")) if n]
    return {
        "Type": "géométrie", "Valeurs": int((~vide).sum()), "Vides": int(vide.sum()),
        "Modalités (nombre)": len(types), "Modalités": " ; ".join(f"{t} ({n})" for t, n in types.items()),
        "Min": f"{xmin:.4f} ; {ymin:.4f}", "Max": f"{xmax:.4f} ; {ymax:.4f}",
        "Atypiques": " ; ".join(atypiques),
    }


def profil_variable(s, mesure=False):
    """Type, vides, modalités, extrêmes, zéros et valeurs atypiques d'une colonne."""
    if est_geometrie(s):
        p = profil_geometrie(s)
    else:
        s = texte_brut(s)
        vide = est_vide(s)
        valeurs = s[~vide].astype(str).str.strip()
        nombres = pd.to_numeric(valeurs, errors="coerce")
        part = nombres.notna().mean() if len(valeurs) else 0
        type_ = "numérique" if len(valeurs) and part == 1 else "numérique et texte" if part >= 0.95 else "texte"
        comptes = valeurs.value_counts()
        p = {"Type": type_, "Valeurs": len(valeurs), "Vides": int(vide.sum()), "Modalités (nombre)": len(comptes)}
        if not mesure:
            haut = comptes.head(MODALITES_MAX if len(comptes) <= MODALITES_MAX else 5)
            p["Modalités"] = " ; ".join(f"{court(v)} ({n})" for v, n in haut.items()) + (
                " ; …" if len(comptes) > len(haut) else "")
        atypiques = []
        if type_ == "texte":
            atypiques = [f"« {v} » ({n})" for v, n in comptes.items() if v.lower() in REMPLACEMENTS]
        else:
            negatifs = int((nombres < 0).sum())
            textes = sorted(set(valeurs[nombres.isna()]))
            p.update({"Min": nombre(nombres.min()), "Max": nombre(nombres.max()), "Zéros": int((nombres == 0).sum())})
            atypiques += [f"{negatifs} négatives"] if negatifs else []
            atypiques += [f"texte : {', '.join(court(t, 20) for t in textes[:5])}"] if textes else []
        p["Atypiques"] = " ; ".join(atypiques)
    total = p["Valeurs"] + p["Vides"]
    p["Vides (%)"] = round(100 * p["Vides"] / total, 1) if total else ""
    return p


def profil_long(fichier, df):
    """Une variable par série : indicateur et modalités, hors colonne des unités."""
    unite = UNITES_LONGUES.get(fichier)
    cle = [c for c in df.columns if c not in COLONNES_LONGUES and c != unite]
    lignes = []
    for valeurs_cle, g in df.groupby(cle, sort=False):
        valeurs_cle = valeurs_cle if isinstance(valeurs_cle, tuple) else (valeurs_cle,)
        p = profil_variable(g["Value"], mesure=True)
        annees = sorted(pd.to_numeric(g["Date"], errors="coerce").dropna().astype(int).unique())
        absentes = sorted(set(range(annees[0], annees[-1] + 1)) - set(annees)) if annees else []
        p.update({
            "Variable": " | ".join(valeurs_cle), "Unité": " ; ".join(g["Unit"].unique()),
            "Années": f"{annees[0]}–{annees[-1]}" if annees else "", "Années absentes": plages(absentes),
            "Unités": g[unite].nunique() if unite else "",
        })
        lignes.append(p)
    return lignes


def profil_table(fichier, table, df, entete):
    """Une ligne de profil_fichiers.csv et les lignes de profil_variables.csv d'une table."""
    long_ = COLONNES_LONGUES <= set(df.columns)
    geo_cols = [c for c in df.columns if est_geometrie(df[c])]
    vides = sum(int(est_vide(df[c]).sum()) for c in df.columns)
    remarques = []
    if long_:
        variables = profil_long(fichier, df)
        dims = [c for c in df.columns if c not in {"Unit", "Value"}]
        doublons = int(df.duplicated(dims).sum())
        for c in dims:
            # Lignes de total mêlées aux modalités qu'elles additionnent
            totaux = df[c].str.match(r"(?i)^\s*total")
            if totaux.any() and df[c].nunique() > 1:
                remarques.append(f"lignes de total ({c}) : {int(totaux.sum())}")
        absentes = sum(1 for v in variables if v["Années absentes"])
        remarques += [f"séries avec années absentes : {absentes}"] if absentes else []
        unite = UNITES_LONGUES.get(fichier)
    else:
        variables = []
        for c in df.columns:
            p = profil_variable(df[c])
            p["Variable"] = c
            variables.append(p)
        comparable = pd.DataFrame({
            c: df[c].to_wkb() if isinstance(df[c], gpd.GeoSeries) else texte_brut(df[c])
            for c in df.columns if c not in COLONNES_IDENTIFIANT
        })
        doublons = int(comparable.duplicated().sum()) if len(comparable.columns) else 0
        vides_cols = [v["Variable"] for v in variables if v["Valeurs"] == 0]
        constantes = [v["Variable"] for v in variables if v["Modalités (nombre)"] == 1 and v["Vides"] == 0]
        remarques += [f"colonnes vides : {', '.join(vides_cols)}"] if vides_cols else []
        remarques += [f"colonnes constantes : {len(constantes)}"] if constantes else []
        renseignees = [c for c in COLONNES_TERRITOIRE if c in df.columns and (~est_vide(df[c])).any()]
        unite = max(renseignees, key=lambda c: df[c].nunique(), default=None)
    for v in variables:
        if v.get("Atypiques") and v["Type"] == "géométrie":
            remarques.append(f"{v['Variable']} : {v['Atypiques']}")
    colonne_annee = next((c for c in COLONNES_ANNEE if c in df.columns), None)
    annees = pd.Series([], dtype=float)
    if colonne_annee:  # « 2014 », 2021 ou « 2013-06-07 » : l'année est le premier nombre à 4 chiffres
        annees = pd.to_numeric(df[colonne_annee].astype(str).str.extract(r"(\d{4})")[0], errors="coerce").dropna()
    fiche = dict(entete)
    fiche.update({
        "Table": table, "Disposition": "longue" if long_ else "large, avec géométrie" if geo_cols else "large",
        "Lignes": len(df), "Colonnes": len(df.columns),
        "Années": f"{int(annees.min())}–{int(annees.max())}" if len(annees) else "",
        "Unités (colonne)": f"{df[unite].nunique()} ({unite})" if unite else "",
        "Cellules vides (%)": round(100 * vides / df.size, 1) if df.size else "",
        "Doublons": doublons, "Remarques": " ; ".join(remarques),
    })
    for v in variables:
        v.update({"Fichier": fichier, "Table": table})
        v.update(niveau(fichier, table, v["Variable"]))
    return fiche, variables


def lire_csv(contenu):
    """Texte brut : encodage, séparateur et table, sans conversion ni valeur par défaut."""
    if contenu.startswith(b"\xef\xbb\xbf"):
        encodage, texte = "utf-8 (BOM)", contenu[3:].decode("utf-8")
    else:
        try:
            encodage, texte = "utf-8", contenu.decode("utf-8")
        except UnicodeDecodeError:
            encodage, texte = "cp1252", contenu.decode("cp1252")
    entete = texte.split("\n", 1)[0].strip()
    ligne_sep = re.fullmatch(r"sep\s*=\s*(.)", entete)
    if ligne_sep:  # WPP : une ligne « sep =| » précède l'en-tête
        separateur, texte = ligne_sep.group(1), texte.split("\n", 1)[1]
    else:
        separateur = max(",;|\t", key=entete.count)
    df = pd.read_csv(io.StringIO(texte), sep=separateur, dtype=str, keep_default_na=False)
    return df, encodage, separateur


def tables(chemin):
    """(table, format, encodage, séparateur, DataFrame, rapport ydata autorisé) pour chaque table du fichier."""
    nom = chemin.name
    if nom == "ehcvm_2021_2022_csv.zip":
        with zipfile.ZipFile(chemin) as z:
            for membre, colonnes in EHCVM_UTILES.items():
                df, encodage, sep = lire_csv(z.read(membre))
                yield membre, "CSV (zip)", encodage, sep, df[colonnes], False
    elif nom.endswith(".geojson.zip"):
        with zipfile.ZipFile(chemin) as z:
            for membre in sorted(z.namelist()):
                yield membre, "GeoJSON (zip)", "utf-8", "", gpd.read_file(io.BytesIO(z.read(membre))), True
    elif nom.endswith(".csv"):
        df, encodage, sep = lire_csv(chemin.read_bytes())
        yield "—", "CSV", encodage, sep, df, True
    elif nom.endswith(".json"):
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
        for cle, valeur in donnees.items():
            if isinstance(valeur, list) and valeur and isinstance(valeur[0], dict):
                yield cle, "JSON", "utf-8", "", pd.DataFrame(valeur), True
    elif nom.endswith(".xlsx"):
        for feuille, df in pd.read_excel(chemin, sheet_name=None, dtype=str).items():
            yield feuille, "XLSX", "", "", df, True


def fiche_pdf(chemin, entete):
    lecteur = PdfReader(chemin)
    pages = len(lecteur.pages)
    avec_texte = sum(1 for page in lecteur.pages if len((page.extract_text() or "").strip()) > 100)
    fiche = dict(entete)
    fiche.update({
        "Table": "—", "Format": "PDF", "Disposition": "document", "Lignes": pages,
        "Remarques": f"{pages} pages, dont {avec_texte} avec une couche texte ; tableaux à extraire (extraction_pdf_04.py)",
    })
    return fiche


def typer(s):
    """Colonne numérique si toutes ses valeurs non vides le sont ; une cellule vide reste vide (R-10)."""
    s = texte_brut(s)
    s = s.mask(est_vide(s))
    n = pd.to_numeric(s, errors="coerce")
    return n if n.notna().sum() == s.notna().sum() else s


def rapport(df, chemin, titre):
    os.environ.setdefault("TQDM_DISABLE", "1")
    from ydata_profiling import ProfileReport  # import lourd : seulement si des rapports sont demandés

    df = df.drop(columns=[c for c in df.columns if est_geometrie(df[c])])
    df = pd.DataFrame({c: typer(df[c]) for c in df.columns})
    ProfileReport(df, title=titre, minimal=True, progress_bar=False).to_file(chemin, silent=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sans-rapports", action="store_true", help="ne pas produire les rapports ydata-profiling")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    (SORTIE / "rapports").mkdir(parents=True, exist_ok=True)
    debut = time.time()

    with open(BRUT / "_SOURCES.csv", encoding="utf-8", newline="") as f:
        registre = [r for r in csv.DictReader(f)
                    if r["Statut"].startswith("Téléchargé") and r["Codes D"] != "Hors 02"]
    perimetre = [(BRUT / r["Fichier"], r["Codes D"]) for r in registre]
    perimetre += [(REFERENCE / nom, besoin) for nom, besoin in BESOINS_REFERENCE.items()]

    fiches, variables, rapports = [], [], 0
    for chemin, besoin in perimetre:
        entete = {"Fichier": chemin.name, "Besoin": besoin}
        if chemin.suffix == ".pdf":
            fiches.append(fiche_pdf(chemin, entete))
            continue
        for table, format_, encodage, sep, df, avec_rapport in tables(chemin):
            entete.update({"Format": format_, "Encodage": encodage, "Séparateur": sep})
            fiche, vars_table = profil_table(chemin.name, table, df, entete)
            fiches.append(fiche)
            variables += vars_table
            if avec_rapport and not args.sans_rapports:
                suffixe = "" if table == "—" else "__" + Path(table).stem
                nom = chemin.name.replace(".", "_") + suffixe
                rapport(df, SORTIE / "rapports" / f"{nom}.html", f"{chemin.name} {table}".removesuffix(" —"))
                rapports += 1
        print(f"  {chemin.name}")

    for lignes, colonnes, nom, entiers in (
        (fiches, COLONNES_FICHIERS, "profil_fichiers.csv", ["Lignes", "Colonnes", "Doublons"]),
        (variables, COLONNES_VARIABLES, "profil_variables.csv",
         ["Valeurs", "Vides", "Modalités (nombre)", "Zéros", "Unités"]),
    ):
        df = pd.DataFrame(lignes, columns=colonnes)
        df[entiers] = df[entiers].apply(lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"))
        df.to_csv(SORTIE / nom, index=False)
    utilisees = [v for v in variables if v.get("Usage")]
    print(f"{len(perimetre)} fichiers, {len(fiches)} tables, {len(variables)} variables "
          f"dont {len(utilisees)} utilisées ; {rapports} rapports ; {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
