"""Lecture des résultats du projet pour le tableau de bord.

Le tableau de bord lit les tables de data/analysis/ et les couches de data/processed/geo/ ; il ne recalcule aucun
indicateur (11 §2). Les seules opérations faites ici sont des lectures, des jointures et des filtres, pour que chaque
chiffre affiché remonte à une table du projet (R-19).

En développement, les tables sont lues dans le dépôt (../data). Dans le livrable `dashboard.zip`, elles sont copiées
dans dashboard/data/ ; si ce dossier existe, il a la priorité.
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd
import streamlit as st
from shapely.geometry import MultiPolygon
from shapely.geometry.polygon import orient

ICI = Path(__file__).resolve().parent
LOCAL = ICI / "data"                       # copie du livrable, si présente
DEPOT = ICI.parent / "data"                # dépôt, en développement
BASE = LOCAL if (LOCAL / "analysis").exists() else DEPOT
ANALYSE = BASE / "analysis"
PROCESSED = BASE / "processed"
GEO = PROCESSED / "geo"
RAW = BASE / "raw"
REFERENCE = BASE / "reference"

ZONES = ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]
REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]


# --- Format des nombres (français) ------------------------------------------------------------------------
def fr(x, d=0) -> str:
    """Nombre au format français : espace pour les milliers, virgule décimale."""
    if pd.isna(x):
        return ""
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def pct(x, d=1) -> str:
    return f"{fr(x, d)} %"


# --- Lecture des tables -----------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def lire(dossier: str, nom: str) -> pd.DataFrame:
    return pd.read_csv(ANALYSE / dossier / f"{nom}.csv")


@st.cache_data(show_spinner=False)
def lire_processed(nom: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"{nom}.csv")


@st.cache_data(show_spinner=False)
def lire_reference(nom: str) -> pd.DataFrame:
    return pd.read_csv(REFERENCE / f"{nom}.csv")


@st.cache_data(show_spinner=False)
def lire_raw(nom: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{nom}.csv")


@st.cache_data(show_spinner=False)
def lire_tm() -> pd.DataFrame:
    """Table maîtresse par préfecture (population, surface, km, auto-écoles)."""
    return pd.read_csv(PROCESSED / "table_maitresse_prefecture.csv")


@st.cache_data(show_spinner=False)
def contours(niveau: str = "prefectures", cle: str = "Préfecture") -> dict:
    """Contours en longitude et latitude, simplifiés pour l'affichage. Chaque feature porte `code` = nom du territoire,
    pour que Plotly joigne sur ce nom."""
    g = gpd.read_file(GEO / f"{niveau}.geojson")
    g = g.rename(columns={cle: "code"})
    g["nom"] = g["code"]
    g = g[["code", "nom", "Zone", "geometry"]] if "Zone" in g else g[["code", "nom", "geometry"]]
    g["geometry"] = [orient(x, sign=-1.0) if x.geom_type == "Polygon"
                     else MultiPolygon([orient(q, sign=-1.0) for q in x.geoms])
                     for x in g.geometry.simplify(0.002, preserve_topology=True)]
    return g.__geo_interface__


@st.cache_data(show_spinner=False)
def contours_zones() -> dict:
    """Contours des 6 zones, par fusion des préfectures."""
    g = gpd.read_file(GEO / "prefectures.geojson").dissolve("Zone").reset_index()
    g = g.rename(columns={"Zone": "code"})
    g["nom"] = g["code"]
    g["geometry"] = [orient(x, sign=-1.0) if x.geom_type == "Polygon"
                     else MultiPolygon([orient(q, sign=-1.0) for q in x.geoms])
                     for x in g.geometry.simplify(0.002, preserve_topology=True)]
    return g[["code", "nom", "geometry"]].__geo_interface__


@st.cache_data(show_spinner=False)
def contours_regions() -> dict:
    """Contours des 5 régions, par fusion des préfectures. Sert à tracer le découpage régional sur les cartes."""
    g = gpd.read_file(GEO / "prefectures.geojson").dissolve("Région").reset_index()
    g = g.rename(columns={"Région": "code"})
    g["nom"] = g["code"]
    g["geometry"] = [orient(x, sign=-1.0) if x.geom_type == "Polygon"
                     else MultiPolygon([orient(q, sign=-1.0) for q in x.geoms])
                     for x in g.geometry.simplify(0.002, preserve_topology=True)]
    return g[["code", "nom", "geometry"]].__geo_interface__


@st.cache_data(show_spinner=False)
def couche(nom: str) -> gpd.GeoDataFrame:
    """Une couche géographique brute (auto_ecoles, routes_classees, equipements), en lon/lat."""
    return gpd.read_file(GEO / f"{nom}.geojson").to_crs("EPSG:4326")


# --- Filtre commun (zone seulement : le reste des filtres dépend de la page) ------------------------------
def filtrer_zone(df: pd.DataFrame, regions: list[str], colonne: str = "Zone") -> pd.DataFrame:
    return df[df[colonne].isin(regions)] if regions else df
