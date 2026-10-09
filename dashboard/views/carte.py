"""Page 4 — Carte du réseau et des auto-écoles. Les 39 préfectures, une couche à la fois, avec les routes, l'état
des tronçons relevés, les auto-écoles et les équipements (design-page4.md).

Aucun recalcul (11 §2) : prefectures_10, prefectures_06, classement_08, D4_etat_troncons et les couches geo/*.geojson.
Les classes des couches sont celles du plan (section 3) ; les tronçons sont rattachés au tracé par leur nom, c'est une
sélection, pas un calcul (04 §5)."""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from shapely.geometry import shape  # noqa: E402

from composants import (ariane, badge, carte_kpi, constat, entete, export_csv, limite, note, pied,  # noqa: E402
                        rangee_kpi, synthese, table_html, titre_bloc)
from donnees import contours, contours_regions, couche, fr, lire, lire_processed  # noqa: E402
from theme import BLEUS, COULEUR_ZONE, ENCRE, HORS_SELECTION  # noqa: E402

INF = float("inf")

pref10 = lire("10_recommandations", "prefectures_10")
pref06 = lire("06_exploration", "prefectures_06")
cla = lire("08_priorisation", "classement_08")
tron = lire_processed("D4_etat_troncons")

ae = couche("auto_ecoles")
AE_AGREEES = ae[ae["Comptée (R-12)"]]
AE_NON = ae[~ae["Comptée (R-12)"]]

GEO = contours("prefectures")
CODES = [ft["properties"]["code"] for ft in GEO["features"]]

f_zones = st.session_state.get("f_zones", [])
f_prio = st.session_state.get("f_priorites", [])

# --- Couleurs propres à cette page (hors palettes imposées du 11 §4.1) ------------------------------------
PRIO_COUL = {"Haute": "#0d366b", "Moyenne": "#3987e5", "Aucune action": "#b9b6ad"}
ABSENT = "#b9b6ad"
# Un type de route, un trait ET une couleur : revêtue et non revêtue se confondaient quand les deux étaient noires.
ROUTE_STYLE = {"Route nationale revêtue": ("#141413", "solid", 1.7),
               "Route nationale non revêtue": ("#8a5a00", "dash", 1.4),
               "Voirie urbaine": ("#55534e", "solid", 0.9),
               "Piste rurale": ("#8a8780", "dot", 1.2)}
# Auto-écoles : deux statuts, deux couleurs (le gris ne porte aucun jugement, il dit « hors indicateurs »).
AE_COUL = {"agréée": "#0d366b", "non agréée": "#8a8780"}
EQUIPEMENT = "#eb6834"

# --- Les classes des couches (design-page4 section 3) ----------------------------------------------------
CL_ETAT = [(0, 10, "moins de 10 %"), (10, 25, "10 à 25 %"), (25, 40, "25 à 40 %"), (40, 60, "40 à 60 %"),
           (60, INF, "60 % ou plus")]
CL_NON_EVAL = [(0, 1e-9, "0 %"), (1e-9, 5, "moins de 5 %"), (5, 10, "5 à 10 %"), (10, 15, "10 à 15 %"),
               (15, INF, "15 % ou plus")]
CL_POP = [(0, 100_000, "moins de 100 000"), (100_000, 150_000, "100 000 à 150 000"),
          (150_000, 200_000, "150 000 à 200 000"), (200_000, 300_000, "200 000 à 300 000"),
          (300_000, INF, "300 000 ou plus")]
CL_KM10 = [(0, 2, "moins de 2 km"), (2, 4, "2 à 4 km"), (4, 6, "4 à 6 km"), (6, 10, "6 à 10 km"),
           (10, INF, "10 km ou plus")]
CL_DENS = [(0, 40, "moins de 40"), (40, 60, "40 à 60"), (60, 100, "60 à 100"), (100, 150, "100 à 150"),
           (150, INF, "150 ou plus")]
CL_RURAL = [(0, 5, "moins de 5 %"), (5, 10, "5 à 10 %"), (10, 20, "10 à 20 %"), (20, 30, "20 à 30 %"),
            (30, INF, "30 % ou plus")]
CL_AE = [(0, 1e-9, "aucune"), (1e-9, 1, "moins de 1"), (1, 2, "1 à 2"), (2, 3, "2 à 3"), (3, INF, "3 ou plus")]
CL_DIST = [(0, 5, "moins de 5 km"), (5, 10, "5 à 10 km"), (10, 25, "10 à 25 km"), (25, 50, "25 à 50 km"),
           (50, INF, "50 km ou plus")]

# --- Une table unique, à partir des tables du projet -----------------------------------------------------
D = pref10.set_index("Préfecture").copy()
_p6 = pref06.set_index("Préfecture")
for _c in ["Part en bon état (%)", "Part en état moyen (%)", "Part en travaux (%)", "Part non évaluée (%)",
           "Km pour 1 000 km²", "Km de routes classées", "Km évalués", "Km bon", "Km moyen", "Km mauvais",
           "Km travaux", "Km non évalués", "Surface (km²)", "Tronçons du relevé", "Origine du point de départ",
           "Préfecture de l’auto-école la plus proche"]:
    D[_c] = _p6[_c]
D["Auto-écoles agréées /100 000 hab."] = cla.set_index("Préfecture")["O4-05"]
D = D.loc[[c for c in CODES if c in D.index]]

COUCHES = {
    "État du réseau : mauvais": dict(
        col="Réseau — part en mauvais état (%)", classes=CL_ETAT, unite="% des km évalués", dec=1, niveau="C",
        absent="non définie : aucune route classée",
        note="Relevé de 2020, routes nationales seulement ; part des km évalués de la préfecture.",
        constat="Le réseau le plus dégradé est au centre du pays : la Centrale a 40,3 % de ses routes en mauvais "
                "état, et Danyi 100 % de ses 49,8 km évalués."),
    "État du réseau : bon": dict(
        col="Part en bon état (%)", classes=CL_ETAT, unite="% des km évalués", dec=1, niveau="C",
        absent="non définie : aucune route classée",
        note="Relevé de 2020, routes nationales seulement.",
        constat="Vo a 78,9 % de ses routes évaluées en bon état, Haho 71,5 % ; à Danyi, aucun km n'est en bon état."),
    "État du réseau : moyen": dict(
        col="Part en état moyen (%)", classes=CL_ETAT, unite="% des km évalués", dec=1, niveau="C",
        absent="non définie : aucune route classée",
        note="Relevé de 2020, routes nationales seulement.",
        constat="L'état moyen domine à Est-Mono (68,7 %) et à Binah (61,9 %) : plus de la moitié de leurs routes "
                "évaluées."),
    "État du réseau : travaux": dict(
        col="Part en travaux (%)", classes=CL_ETAT, unite="% des km évalués", dec=1, niveau="C",
        absent="non définie : aucune route classée",
        note="Travaux relevés en 2020 : un état du relevé, pas un suivi de chantier.",
        constat="En 2020, des travaux couvraient 78,5 % des routes évaluées de Moyen-Mono et 70,4 % de celles d'Avé ; "
                "10 préfectures n'en avaient aucun."),
    "État du réseau : non évalué": dict(
        col="Part non évaluée (%)", classes=CL_NON_EVAL, unite="% des km de routes nationales", dec=1, niveau="B",
        absent="non définie : aucune route classée",
        note="Part des km de routes nationales sans état relevé : « non évaluée », jamais « en bon état ».",
        constat="Le relevé couvre presque tout le réseau national : 3,2 % des km sont sans état, surtout à "
                "Agoè-Nyivé (20,0 %) et à Blitta (19,8 %) ; 25 préfectures sont entièrement évaluées."),
    "Population (2022)": dict(
        col="Population", classes=CL_POP, unite="habitants", dec=0, niveau="A", absent="",
        note="Recensement de 2022.",
        constat="Le Grand Lomé (Golfe et Agoè-Nyivé) regroupe 27,0 % de la population ; Danyi, la moins peuplée, a "
                "40 240 habitants."),
    "Km de routes classées pour 10 000 hab.": dict(
        col="Desserte (km pour 10 000 hab.)", classes=CL_KM10, unite="km pour 10 000 habitants", dec=2, niveau="B",
        absent="", note="Km de routes classées rapportés à la population de 2022.",
        constat="Les préfectures les plus peuplées ont le moins de routes par habitant : 0,74 km pour 10 000 "
                "habitants dans le Golfe, contre 15,17 à Agou ; Mô n'a aucune route classée."),
    "Densité routière": dict(
        col="Km pour 1 000 km²", classes=CL_DENS, unite="km pour 1 000 km²", dec=1, niveau="B", absent="",
        note="Rapportée à la surface, pas aux habitants : le Grand Lomé a beaucoup de routes au km², mais peu "
             "par habitant.",
        constat="Le Grand Lomé a le réseau le plus dense : 401,9 km pour 1 000 km² dans le Golfe, 390,5 à "
                "Agoè-Nyivé ; Akébou n'en a que 6,1, et Mô aucune route classée."),
    "Accès rural à une route revêtue": dict(
        col="Accès rural à une route revêtue (%)", classes=CL_RURAL, unite="% des ruraux à moins de 2 km", dec=1,
        niveau="C", absent="sans population rurale",
        note="Estimé avec une population répartie uniformément dans chaque préfecture.",
        constat="17,2 % des ruraux vivent à moins de 2 km d'une route revêtue : de 45,8 % aux Lacs à 0,6 % à "
                "Akébou, et aucun à Mô."),
    "Auto-écoles agréées pour 100 000 hab.": dict(
        col="Auto-écoles agréées /100 000 hab.", classes=CL_AE, unite="auto-écoles pour 100 000 habitants", dec=2,
        niveau="C", absent="",
        note="Agrément relevé dans le recensement des auto-écoles ; l'activité n'est pas publiée.",
        constat="23 préfectures sur 39 n'ont aucune auto-école agréée (2 932 492 habitants) ; le Golfe en a 5,67 "
                "pour 100 000 habitants."),
    "Distance à l'auto-école agréée la plus proche": dict(
        col="Formation — distance à la plus proche (km)", classes=CL_DIST, unite="km à vol d'oiseau", dec=1,
        niveau="C", absent="",
        note="À vol d'oiseau, depuis le chef-lieu (30 préfectures) ou un point central (9 préfectures). La classe "
             "« 5 à 10 km » s'arrête au seuil d'éloignement du classement.",
        constat="26 préfectures ont leur chef-lieu à plus de 10 km de l'auto-école agréée la plus proche "
                "(3 482 856 habitants) ; jusqu'à 84,0 km pour Oti-Sud."),
    "Priorité": dict(
        col="Priorité", classes=None, unite="niveau de priorité", dec=0, niveau="C", absent="",
        note="Priorité du classement : réseau dégradé et manque d'auto-écoles.",
        constat="5 préfectures sont en priorité haute : Danyi, Blitta, Agou, Tchamba et Bassar cumulent un réseau "
                "dégradé et un manque d'auto-écoles (641 955 habitants)."),
}


def _classe(v, classes) -> int | None:
    if v != v:
        return None
    for i, (bas, haut, _) in enumerate(classes):
        if bas <= v < haut:
            return i
    return len(classes) - 1


def _echelle(couleurs):
    """Colorscale en bandes égales : z = indice de classe + 0,5, zmin 0, zmax n (comme la carte des constats)."""
    n = len(couleurs)
    sc = []
    for i, c in enumerate(couleurs):
        sc += [[i / n, c], [(i + 1) / n, c]]
    return sc


def _uni(couleur):
    return [[0, couleur], [1, couleur]]


@st.cache_data(show_spinner=False)
def _centroides() -> dict:
    """Un point intérieur par préfecture, pour écrire son nom sur l'agrandissement."""
    return {ft["properties"]["code"]: shape(ft["geometry"]).representative_point().coords[0]
            for ft in GEO["features"]}


def _fenetre(codes=None, marge=0.05):
    xs, ys = [], []
    for ft in GEO["features"]:
        if codes is not None and ft["properties"]["code"] not in codes:
            continue
        x0, y0, x1, y1 = ft["bbox"]
        xs += [x0, x1]
        ys += [y0, y1]
    return [min(xs) - marge, max(xs) + marge], [min(ys) - marge, max(ys) + marge]


@st.cache_data(show_spinner=False)
def _lignes_regions():
    """Limites des 5 régions, en bande grise large sous les routes (un trait fin se confondait avec une nationale)."""
    lon, lat = [], []
    for ft in contours_regions()["features"]:
        g = shape(ft["geometry"])
        for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
            xs, ys = poly.exterior.xy
            lon += list(xs) + [None]
            lat += list(ys) + [None]
    return lon, lat


def _coords(sub):
    lon, lat = [], []
    for geom in sub.geometry:
        for line in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
            xs, ys = line.xy
            lon += list(xs) + [None]
            lat += list(ys) + [None]
    return lon, lat


@st.cache_data(show_spinner=False)
def _routes_par_type() -> dict:
    routes = couche("routes_classees")
    return {typ: _coords(routes[routes.Type == typ]) for typ in ROUTE_STYLE}


@st.cache_data(show_spinner=False)
def _routes_par_etat() -> dict:
    """Trois groupes : les 49 tronçons avec des km en mauvais état (épaisseur selon les km), les 35 autres tronçons
    relevés, et les routes nationales sans état relevé. Le rattachement au tracé se fait par le nom du tronçon."""
    routes = couche("routes_classees")
    nat = routes[routes.Type.str.startswith("Route nationale")]
    km_mauvais, releves = {}, set()
    for noms, km in zip(tron["Noms du tracé"].fillna(""), tron["km_mauvais"]):
        for nom in str(noms).split(" | "):
            if nom:
                releves.add(nom)
                km_mauvais[nom] = max(km_mauvais.get(nom, 0), km)
    mauvais = {n: k for n, k in km_mauvais.items() if k > 0}
    maxi = max(mauvais.values()) if mauvais else 1
    groupes = {}
    for nom, km in mauvais.items():
        groupes.setdefault(round(1.2 + 3.8 * (km / maxi), 1), []).append(nom)
    sortie = {"mauvais": {largeur: _coords(nat[nat["Nom"].isin(noms)]) for largeur, noms in groupes.items()},
              "autres": _coords(nat[nat["Nom"].isin(releves - set(mauvais))]),
              "sans": _coords(nat[~nat["Nom"].isin(releves)])}
    return sortie


@st.cache_data(show_spinner=False)
def _points_equipements(typ: str):
    """Un point par équipement. Les passages piétons, publiés en polygones, sont montrés par un point intérieur :
    une transformation d'affichage, pas un calcul d'indicateur."""
    eq = couche("equipements")
    eq = eq[eq.Type == typ]
    pts = eq.geometry.representative_point()
    return list(pts.x), list(pts.y), list(eq["Préfecture"].fillna("hors des 39 préfectures"))


ariane("Carte du réseau et des auto-écoles")
entete("Carte du réseau et des auto-écoles", "Que voit-on, préfecture par préfecture ?",
       "Le mauvais état du réseau se concentre au centre du pays (<strong>40,3 %</strong> des km évalués dans la "
       "Centrale) ; <strong>103 des 132</strong> auto-écoles agréées sont dans le Grand Lomé, et <strong>26 "
       "préfectures</strong> ont leur chef-lieu à plus de 10 km de la plus proche.")

# ------------------------------------------------------------------ Section 1 — 4 chiffres clés
n_agree = len(AE_AGREEES)
rangee_kpi("Ce que montre la carte", [
    carte_kpi("Préfectures au réseau dégradé", "13 sur 38", "plus de 22,13 % de routes en mauvais état",
              "2 868 523 habitants. Mô : aucune route classée (38 évaluées).", etiquette="C", ton="alerte"),
    carte_kpi("Auto-écoles recensées", f"{len(ae)}", f"dont {n_agree} agréées (85 agréées, 47 antennes)",
              "Activité non publiée : aucune n'est vérifiée en activité.", etiquette="A"),
    carte_kpi("Préfectures sans auto-école agréée", "23 sur 39", "2 932 492 habitants",
              "Dont 15 sans aucune auto-école recensée (1 822 046 hab.).", etiquette="B", ton="alerte"),
    carte_kpi("Équipements de sécurité routière", "16 797", "panneaux, ralentisseurs, passages, feux",
              "Collecte 2021-2022, non vérifiée ; hors indicateurs.", etiquette="C"),
])

# ------------------------------------------------------------------ Section 2 — Réglages et carte
st.markdown("")
g, d = st.columns([2.1, 1], vertical_alignment="top")
with g:
    titre_bloc("Le Togo, préfecture par préfecture",
               "Une couche à la fois, en 5 classes fixes ; l'agrandissement montre la région Maritime et le Grand "
               "Lomé, où se concentrent les auto-écoles. Molette ou barre d'outils pour zoomer.")
    r1, r2 = st.columns([1.3, 1])
    nom_couche = r1.selectbox("Couche", list(COUCHES), key="ca_couche")
    trace = r2.selectbox("Tracé", ["Routes classées par type", "État des tronçons relevés", "Aucun"], key="ca_trace")
    r3, r4 = st.columns([1, 1.3])
    montrer_ae = r3.checkbox("Auto-écoles", value=True, key="ca_ae")
    equip = r4.selectbox("Équipements de sécurité routière (hors indicateurs)",
                         ["Masqués", "Panneau de signalisation", "Ralentisseur", "Passage piéton", "Feu tricolore"],
                         key="ca_equip")

    cfg = COUCHES[nom_couche]
    classes = cfg["classes"]
    categorique = classes is None
    vals = D[cfg["col"]]

    # Trois groupes de préfectures : dans la couche, valeur absente, hors du territoire choisi.
    hors = set(D.index[~D["Zone"].isin(f_zones)]) if f_zones else set()
    if f_prio:
        hors |= set(D.index[~D["Priorité"].isin(f_prio)])
    if categorique:
        cl = {p: ["Haute", "Moyenne", "Aucune action"].index(v) if v in PRIO_COUL else None for p, v in vals.items()}
    else:
        cl = {p: _classe(v, classes) for p, v in vals.items()}

    dedans = [p for p in D.index if p not in hors and cl[p] is not None]
    absents = [p for p in D.index if p not in hors and cl[p] is None]

    def _texte(p):
        r = D.loc[p]
        v = vals[p]
        if categorique:
            valeur = str(v)
        elif v != v:
            valeur = cfg["absent"] or "non définie"
        else:
            valeur = f"{fr(v, cfg['dec'])} {cfg['unite']}"
        lignes = [f"<b>{p}</b>", f"{r['Zone']} · région {r['Région']}", f"{fr(r['Population'])} habitants",
                  f"<b>{nom_couche}</b> : {valeur}"]
        if nom_couche.startswith("État du réseau"):
            lignes.append(f"{fr(r['Km évalués'], 1)} km évalués · {int(r['Tronçons du relevé'])} tronçons relevés"
                          if r["Km évalués"] == r["Km évalués"] else "aucune route classée")
        if nom_couche == "Distance à l'auto-école agréée la plus proche":
            lignes.append(f"Départ : {r['Origine du point de départ']} → {r['Préfecture de l’auto-école la plus proche']}")
        lignes.append(f"Priorité : {r['Priorité']} · leviers : {r['Leviers']}")
        lignes.append("<i>Cliquez pour afficher sa fiche</i>")
        return "<br>".join(lignes)

    textes = {p: _texte(p) for p in D.index}
    couleurs = ([PRIO_COUL["Haute"], PRIO_COUL["Moyenne"], PRIO_COUL["Aucune action"]] if categorique else BLEUS)

    # La préfecture cliquée au passage précédent : l'état du graphique est déjà posé quand la page se rejoue,
    # ce qui permet de la cercler de noir sur la carte (design-page4 section 4).
    def _cliquee() -> str | None:
        etat = st.session_state.get("ca_carte") or {}
        for pt in ((etat.get("selection") or {}).get("points") or []):
            loc = pt.get("location")
            if loc in D.index:                       # clic sur une préfecture
                return loc
            txt = pt.get("text")
            if isinstance(txt, str):                 # clic sur une auto-école ou un équipement : sa préfecture
                if txt in D.index:
                    return txt
                debut = re.match(r"<b>(.+?)</b>", txt)
                if debut and debut.group(1) in D.index:
                    return debut.group(1)
        return None

    # La sélection de Plotly est effacée dès que la figure change (ici, le cerclage de la préfecture choisie) ou
    # qu'un autre bouton rejoue la page : on garde donc la préfecture retenue à part.
    retenue = _cliquee()
    if retenue:
        st.session_state["ca_prefecture"] = retenue
    choisie = st.session_state.get("ca_prefecture")

    fig = go.Figure()

    def dessiner(cible: str, inset: bool):
        # Opacité figée : sans cela, Plotly estompe tout le fond dès qu'un point est sélectionné.
        comm = dict(geojson=GEO, featureidkey="properties.code", marker_line_color="#ffffff",
                    marker_line_width=0.8, showscale=False, geo=cible,
                    selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1)))
        if hors:
            fig.add_choropleth(locations=sorted(hors), z=[0] * len(hors), colorscale=_uni(HORS_SELECTION),
                               zmin=0, zmax=1, hoverinfo="skip", **comm)
        if absents:
            fig.add_choropleth(locations=absents, z=[0] * len(absents), colorscale=_uni(ABSENT), zmin=0, zmax=1,
                               text=[textes[p] for p in absents], hovertemplate="%{text}<extra></extra>", **comm)
        if dedans:
            fig.add_choropleth(locations=dedans, z=[cl[p] + 0.5 for p in dedans], zmin=0, zmax=len(couleurs),
                               colorscale=_echelle(couleurs), text=[textes[p] for p in dedans],
                               hovertemplate="%{text}<extra></extra>", **comm)
        lon, lat = _lignes_regions()
        fig.add_scattergeo(lon=lon, lat=lat, mode="lines", line=dict(width=3.4, color="rgba(20,20,19,.38)"),
                           hoverinfo="skip", showlegend=False, geo=cible)
        if trace == "Routes classées par type":
            for typ, (coul, dash, largeur) in ROUTE_STYLE.items():
                lon, lat = _routes_par_type()[typ]
                fig.add_scattergeo(lon=lon, lat=lat, mode="lines", hoverinfo="skip", showlegend=False, geo=cible,
                                   line=dict(width=largeur * (1.2 if inset else 1), color=coul, dash=dash))
        elif trace == "État des tronçons relevés":
            etats = _routes_par_etat()
            lon, lat = etats["sans"]
            fig.add_scattergeo(lon=lon, lat=lat, mode="lines", hoverinfo="skip", showlegend=False, geo=cible,
                               line=dict(width=1.1, color="#b9b6ad", dash="dash"))
            lon, lat = etats["autres"]
            fig.add_scattergeo(lon=lon, lat=lat, mode="lines", hoverinfo="skip", showlegend=False, geo=cible,
                               line=dict(width=1.4, color="#55534e"))
            for largeur, (lon, lat) in etats["mauvais"].items():
                fig.add_scattergeo(lon=lon, lat=lat, mode="lines", hoverinfo="skip", showlegend=False, geo=cible,
                                   line=dict(width=largeur * (1.3 if inset else 1), color="#e34948"))
        plein = dict(selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1)))
        if montrer_ae:
            fig.add_scattergeo(lon=AE_NON.geometry.x, lat=AE_NON.geometry.y, mode="markers", geo=cible,
                               marker=dict(size=5 if inset else 4, color=AE_COUL["non agréée"],
                                           line=dict(width=0.6, color="#ffffff")),
                               text=AE_NON["Préfecture"], showlegend=False, **plein,
                               hovertemplate="Auto-école non agréée — %{text}<extra></extra>")
            fig.add_scattergeo(lon=AE_AGREEES.geometry.x, lat=AE_AGREEES.geometry.y, mode="markers", geo=cible,
                               marker=dict(size=8 if inset else 6, color=AE_COUL["agréée"],
                                           line=dict(width=1.1, color="#ffffff")),
                               text=AE_AGREEES["Préfecture"], showlegend=False, **plein,
                               hovertemplate="Auto-école agréée — %{text}<extra></extra>")
        if equip != "Masqués":
            lons, lats, prefs = _points_equipements(equip)
            fig.add_scattergeo(lon=lons, lat=lats, mode="markers", geo=cible, text=prefs, showlegend=False,
                               marker=dict(size=3.5, color=EQUIPEMENT, opacity=0.75), **plein,
                               hovertemplate=f"{equip} — %{{text}}<extra></extra>")
        if choisie:                                  # la préfecture cliquée, cerclée de noir
            fig.add_choropleth(geojson=GEO, featureidkey="properties.code", locations=[choisie], z=[0],
                               colorscale=_uni("rgba(0,0,0,0)"), zmin=0, zmax=1, showscale=False, geo=cible,
                               marker_line_color="#141413", marker_line_width=3, hoverinfo="skip",
                               selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1)))

    dessiner("geo", inset=False)
    dessiner("geo2", inset=True)

    # Noms des préfectures sur l'agrandissement, comme sur la figure du notebook « 04 — O3 ».
    SUD = [p for p in D.index if D.loc[p, "Région"] == "Maritime"]
    cen = _centroides()
    fig.add_scattergeo(lon=[cen[p][0] for p in SUD], lat=[cen[p][1] for p in SUD], mode="text", geo="geo2",
                       text=SUD, textfont=dict(size=10, color="#141413"), hoverinfo="skip", showlegend=False)

    base_geo = dict(visible=False, bgcolor="#ffffff", projection=dict(type="mercator"))
    lon_t, lat_t = _fenetre()
    lon_s, lat_s = _fenetre(set(SUD), marge=0.03)
    fig.update_layout(
        geo=dict(**base_geo, domain=dict(x=[0, 0.46], y=[0, 1]),
                 lonaxis=dict(range=lon_t), lataxis=dict(range=lat_t)),
        geo2=dict(**base_geo, domain=dict(x=[0.48, 1], y=[0.02, 0.80]),
                  lonaxis=dict(range=lon_s), lataxis=dict(range=lat_s)),
        height=620, margin=dict(l=0, r=0, t=22, b=0), paper_bgcolor="#ffffff",
        font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE),
        hoverlabel=dict(bgcolor="#ffffff"), separators=", ",
        annotations=[dict(x=0.48, y=0.90, xref="paper", yref="paper", xanchor="left", showarrow=False,
                          text="<b>Région Maritime et Grand Lomé, agrandi</b><br>"
                               "<span style='font-size:10px;color:#55534e'>la région la plus dense : "
                               "103 des 132 auto-écoles agréées</span>",
                          font=dict(size=12, color=ENCRE), align="left")])
    st.plotly_chart(fig, key="ca_carte", on_select="rerun", selection_mode="points",
                          config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False,
                                  "modeBarButtonsToRemove": ["select2d", "lasso2d"]})

    # --- Légende : les 5 classes avec leur effectif, les valeurs absentes, et ce qui est dessiné
    eff = {i: sum(1 for p in dedans if cl[p] == i) for i in range(len(couleurs))}
    libelles = (["haute", "moyenne", "aucune action"] if categorique else [lib for _, _, lib in classes])
    chips = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
        f'<span style="width:13px;height:13px;border-radius:3px;background:{couleurs[i]};'
        f'border:1px solid #d8d6cc"></span>{html.escape(lib)} <b>({eff[i]})</b></span>'
        for i, lib in enumerate(libelles))
    if absents:
        chips += (f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
                  f'<span style="width:13px;height:13px;border-radius:3px;background:{ABSENT};'
                  f'border:1px solid #d8d6cc"></span>{html.escape(cfg["absent"] or "valeur absente")} '
                  f'<b>({len(absents)})</b></span>')
    if hors:
        chips += (f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:.74rem">'
                  f'<span style="width:13px;height:13px;border-radius:3px;background:{HORS_SELECTION};'
                  f'border:1px solid #d8d6cc"></span>hors du territoire choisi <b>({len(hors)})</b></span>')

    sur_carte = ['<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                 '<span style="width:16px;height:0;border-top:3px solid rgba(20,20,19,.38)"></span>'
                 'limites des 5 régions</span>']
    if trace == "Routes classées par type":
        km = {"Route nationale revêtue": "2 236,4 km", "Route nationale non revêtue": "863,1 km",
              "Voirie urbaine": "233,2 km", "Piste rurale": "33,8 km"}
        for typ, (coul, dash, _) in ROUTE_STYLE.items():
            style = "dashed" if dash == "dash" else ("dotted" if dash == "dot" else "solid")
            sur_carte.append(f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                             f'<span style="width:18px;height:0;border-top:2.5px {style} {coul}"></span>'
                             f'{typ.lower()} ({km[typ]})</span>')
    elif trace == "État des tronçons relevés":
        sur_carte += ['<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                      '<span style="width:18px;height:0;border-top:3px solid #e34948"></span>49 tronçons en mauvais '
                      'état (épaisseur selon les km)</span>',
                      '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                      '<span style="width:18px;height:0;border-top:2.5px solid #55534e"></span>35 autres tronçons '
                      'relevés</span>',
                      '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                      '<span style="width:18px;height:0;border-top:2.5px dashed #b9b6ad"></span>99,0 km de routes '
                      'nationales sans état relevé</span>']
    if montrer_ae:
        sur_carte += [f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                      f'<span style="width:11px;height:11px;border-radius:50%;background:{AE_COUL["agréée"]};'
                      f'border:1.5px solid #fff"></span>{n_agree} auto-écoles agréées</span>',
                      f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                      f'<span style="width:9px;height:9px;border-radius:50%;background:{AE_COUL["non agréée"]};'
                      f'border:1px solid #fff"></span>{len(AE_NON)} non agréées ou au statut non renseigné</span>']
    if equip != "Masqués":
        sur_carte.append(f'<span style="display:inline-flex;align-items:center;gap:5px">'
                         f'<span style="width:9px;height:9px;border-radius:50%;background:{EQUIPEMENT}"></span>'
                         f'{equip.lower()}s — non utilisés dans les indicateurs</span>')
    st.markdown(f'<div class="filtres-actifs"><b>{html.escape(nom_couche)}</b> '
                f'<span style="color:#55534e">({html.escape(cfg["unite"])})</span><br>{chips}<br>'
                f'<span style="font-size:.74rem"><b>Sur la carte :</b> {"".join(sur_carte)}</span></div>',
                unsafe_allow_html=True)
    note(f"Niveau {cfg['niveau']} — {cfg['note']} A = mesuré, B = calculé, C = estimé.")
    exp = D.reset_index()[["Préfecture", "Zone", "Région", "Population", cfg["col"]]]
    export_csv(exp, "couche_affichee.csv", "ca_exp_couche", "Télécharger la couche (CSV)")

with d:
    constat(f'<strong>{html.escape(nom_couche)}</strong><br>{cfg["constat"]}')
    st.caption("Projection Mercator, cadrée sur le Togo, sans fond de carte. Les contours des 5 régions sont "
               "toujours tracés ; le territoire choisi dans la barre latérale garde ses couleurs, les autres "
               "préfectures passent en beige.")

    # ---------------------------------------------------------- Section 7 — Fiche de la préfecture choisie
    titre_bloc("La préfecture choisie")
    if choisie is None:
        st.caption("Cliquez sur une préfecture, une auto-école ou un équipement : la préfecture s'affiche ici, "
                   "avec ses actions et un lien vers sa fiche.")
    else:
        r = D.loc[choisie]
        st.markdown(
            f'<div style="border:1px solid #e2dfd6;border-left:3px solid {PRIO_COUL.get(r["Priorité"], ABSENT)};'
            f'border-radius:10px;padding:12px;background:#fff">'
            f'<div style="font-weight:700;font-size:1.05rem">{html.escape(choisie)}</div>'
            f'<div style="color:#55534e;font-size:.8rem">{html.escape(r["Zone"])} · région '
            f'{html.escape(r["Région"])}</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:#0d366b;margin:3px 0">{fr(r["Population"])}'
            f'<span style="font-size:.7rem;font-weight:400;color:#55534e"> habitants</span></div>'
            f'<div style="margin:4px 0">{badge(r["Priorité"], PRIO_COUL.get(r["Priorité"], ABSENT))}'
            f'<span style="font-size:.78rem;color:#55534e">leviers : {html.escape(str(r["Leviers"]))}</span></div>'
            f'<div style="background:#f4f2ec;border-left:3px solid #55534e;padding:7px 9px;font-size:.82rem">'
            f'<b>Actions recommandées :</b> {html.escape(str(r["Actions"]))}</div></div>', unsafe_allow_html=True)
        b1, b2 = st.columns([2, 1])
        if b1.button(f"Voir la fiche de {choisie} →", key="ca_fiche"):
            st.session_state["fiche_prefecture"] = choisie
            st.session_state["recommandations_rang"] = 6
            st.switch_page("views/recommandations.py")
        if b2.button("Effacer", key="ca_effacer"):
            st.session_state["ca_prefecture"] = None
            st.rerun()

# ------------------------------------------------------------------ Section 9 — Les couches, préfecture par préfecture
st.markdown("")
titre_bloc("Les couches, préfecture par préfecture",
           "Les mêmes classes que la carte. Recoupe le tableau de la page Comparaison territoriale, qui garde "
           "les seuils du classement.")

tab = D.reset_index()[["Préfecture", "Zone", "Région", "Population", "Réseau — part en mauvais état (%)",
                       "Part en bon état (%)", "Part en état moyen (%)", "Part en travaux (%)",
                       "Part non évaluée (%)", "Desserte (km pour 10 000 hab.)", "Km pour 1 000 km²",
                       "Accès rural à une route revêtue (%)", "Auto-écoles agréées /100 000 hab.",
                       "Formation — distance à la plus proche (km)", "Priorité"]].rename(columns={
    "Réseau — part en mauvais état (%)": "Mauvais état (%)", "Part en bon état (%)": "Bon état (%)",
    "Part en état moyen (%)": "État moyen (%)", "Part en travaux (%)": "Travaux (%)",
    "Part non évaluée (%)": "Non évalué (%)", "Desserte (km pour 10 000 hab.)": "Km /10 000 hab.",
    "Km pour 1 000 km²": "Km /1 000 km²", "Accès rural à une route revêtue (%)": "Accès rural (%)",
    "Auto-écoles agréées /100 000 hab.": "Auto-écoles /100 000",
    "Formation — distance à la plus proche (km)": "Distance (km)"})
if f_zones:
    tab = tab[tab["Zone"].isin(f_zones)]
if f_prio:
    tab = tab[tab["Priorité"].isin(f_prio)]

TRIS = {"Zone, puis préfecture": ["Zone", "Préfecture"], "Mauvais état, du plus élevé": ["Mauvais état (%)"],
        "Population, de la plus forte": ["Population"], "Distance à l'auto-école, de la plus longue": ["Distance (km)"],
        "Priorité": ["Priorité"], "Préfecture (A-Z)": ["Préfecture"]}
tri = st.selectbox("Trier le tableau", list(TRIS), key="ca_tri")
cols_tri = TRIS[tri]
tab = tab.sort_values(cols_tri, ascending=(tri in ("Zone, puis préfecture", "Préfecture (A-Z)", "Priorité")),
                      na_position="last")

lignes = []
for _, r in tab.iterrows():
    icl = _classe(r["Mauvais état (%)"], CL_ETAT)
    mauvais = (badge(f"{fr(r['Mauvais état (%)'], 1)} %", BLEUS[icl]) if icl is not None
               else badge("non définie", ABSENT))
    lignes.append({
        "Préfecture": f'<b>{html.escape(r["Préfecture"])}</b>',
        "Zone": (f'<span style="color:{COULEUR_ZONE.get(r["Zone"], ENCRE)};font-size:.76rem;font-weight:600">'
                 f'{html.escape(r["Zone"])}</span>'),
        "Région": html.escape(r["Région"]),
        "Population": fr(r["Population"]),
        "Mauvais état": mauvais,
        "Bon état": f'{fr(r["Bon état (%)"], 1)} %' if r["Bon état (%)"] == r["Bon état (%)"] else "—",
        "Non évalué": f'{fr(r["Non évalué (%)"], 1)} %' if r["Non évalué (%)"] == r["Non évalué (%)"] else "—",
        "Km /10 000 hab.": fr(r["Km /10 000 hab."], 2),
        "Accès rural": (f'{fr(r["Accès rural (%)"], 1)} %' if r["Accès rural (%)"] == r["Accès rural (%)"]
                        else '<i style="color:#8a8780">sans ruraux</i>'),
        "Auto-écoles /100 000": fr(r["Auto-écoles /100 000"], 2),
        "Distance": f'{fr(r["Distance (km)"], 1)} km',
        "Priorité": badge(r["Priorité"], PRIO_COUL.get(r["Priorité"], ABSENT)),
    })
st.markdown(f'<div style="max-height:470px;overflow-y:auto;border-radius:10px">{table_html(lignes)}</div>',
            unsafe_allow_html=True)
st.markdown(
    f'<div class="filtres-actifs"><b>Priorité :</b> {badge("Haute", PRIO_COUL["Haute"])}'
    f'{badge("Moyenne", PRIO_COUL["Moyenne"])}{badge("Aucune action", PRIO_COUL["Aucune action"])}'
    f' &nbsp;·&nbsp; <b>Mauvais état :</b> la pastille prend la couleur de sa classe sur la carte — '
    + "".join(f'{badge(lib, BLEUS[i])}' for i, (_, _, lib) in enumerate(CL_ETAT))
    + ' &nbsp;·&nbsp; Mô : part en mauvais état non définie (aucune route classée).</div>', unsafe_allow_html=True)
st.caption(f"{len(tab)} préfectures affichées. Les 5 états du réseau, la densité et l'état moyen sont dans l'export ; "
           "la carte les montre couche par couche.")
export_csv(tab, "couches_prefectures.csv", "ca_exp_couches")

# ------------------------------------------------------------------ Section 10 — Les 272 auto-écoles recensées
st.markdown("")
titre_bloc("Les 272 auto-écoles recensées", "Statut, localisation et préfecture de rattachement (par la position).")
AGREEES_PAR_PREF = AE_AGREEES["Préfecture"].value_counts()
SANS_AGREEE = {p for p in D.index if AGREEES_PAR_PREF.get(p, 0) == 0}

aet = ae[["Nom", "Statut", "Localité", "Commune", "Canton", "Préfecture", "Zone", "Région"]].copy()
aet["À vérifier"] = [("à vérifier" if (not c) and p in SANS_AGREEE else "")
                     for c, p in zip(ae["Comptée (R-12)"], ae["Préfecture"])]
aet["Habitants par auto-école agréée"] = aet["Préfecture"].map(
    lambda p: fr(D.loc[p, "Population"] / AGREEES_PAR_PREF[p], 0) if AGREEES_PAR_PREF.get(p, 0) else "aucune agréée")

c1, c2 = st.columns([2, 1])
rech = c1.text_input("Rechercher (nom, localité, commune)", key="ca_rech")
stat = c2.multiselect("Statut", ["Agréée", "Antenne agréée", "Non agréée", "Non renseigné"], key="ca_stat")
vue = aet.copy()
if f_zones:
    vue = vue[vue["Zone"].isin(f_zones)]
if rech:
    m = vue["Nom"].str.contains(rech, case=False, na=False) | vue["Localité"].str.contains(rech, case=False, na=False) \
        | vue["Commune"].str.contains(rech, case=False, na=False)
    vue = vue[m]
if stat:
    vue = vue[vue["Statut"].isin(stat)]
vue = vue.sort_values(["Zone", "Préfecture", "Statut", "Nom"])

STATUT_COUL = {"Agréée": "#0d366b", "Antenne agréée": "#cde2fb", "Non agréée": "#efece4", "Non renseigné": "#ffffff"}


def _c_statut(v):
    coul = STATUT_COUL.get(v)
    if not coul:
        return ""
    return f"background-color:{coul};color:{'#ffffff' if v == 'Agréée' else '#141413'};font-weight:600"


def _c_verif(v):
    return "background-color:#fef3c7;color:#8a5a00;font-weight:600" if v else ""


def _c_sans_agreee(v):
    return "color:#8a5a00;font-style:italic" if v == "aucune agréée" else ""


style = (vue.style
         .map(_c_sans_agreee, subset=["Habitants par auto-école agréée"])
         .map(_c_statut, subset=["Statut"])
         .map(_c_verif, subset=["À vérifier"]))
st.dataframe(style, hide_index=True, use_container_width=True, height=360)
n_verif = int((vue["À vérifier"] != "").sum())
st.caption(f"{len(vue)} auto-écoles affichées, dont {int(vue['Statut'].isin(['Agréée', 'Antenne agréée']).sum())} "
           f"agréées (antennes comprises) et {n_verif} à vérifier : non agréées dans une préfecture qui n'a aucune "
           "auto-école agréée. La préfecture est le rattachement par la position (utilisé par les indicateurs) ; "
           "il diffère de la préfecture déclarée pour 4 auto-écoles.")
exp = ae[["Nom", "Statut", "Localité", "Commune", "Canton", "Préfecture", "Zone", "Région"]].copy()
exp["longitude"] = ae.geometry.x
exp["latitude"] = ae.geometry.y
export_csv(exp, "auto_ecoles_272.csv", "ca_exp_ae")

# ------------------------------------------------------------------ Section 11 — Ce que la carte ne montre pas
st.markdown("")
titre_bloc("Ce que la carte ne montre pas")
for t in ["Les accidents, les tués et les blessés : publiés pour tout le pays seulement (page Évolutions, onglet "
          "Sécurité routière).",
          "Les permis et les immatriculations : publiés pour tout le pays seulement (page Évolutions, onglet Mobilité).",
          "Le risque par préfecture : non classé, faute d'accidents par territoire. La priorité ne porte que sur le "
          "réseau et la formation.",
          "L'accès aux secours, le trafic et la vitesse : aucune donnée."]:
    st.markdown(f"- {t}")

# ------------------------------------------------------------------ Section 12 — Synthèse et limite
st.markdown("")
g, d = st.columns(2, vertical_alignment="top")
with g:
    synthese("21,2 %", "des km évalués en mauvais état dans le pays (669,34 km sur 3 163 km)",
             ["13 préfectures au-delà du seuil de 22,13 %.",
              "Mô sans route classée : 38 préfectures évaluées sur 39.",
              "103 des 132 auto-écoles agréées dans le Grand Lomé."])
with d:
    limite("État relevé en 2020, sur les routes nationales seulement. Accès rural estimé avec une population répartie "
           "uniformément dans chaque préfecture. Distance à vol d'oiseau, depuis le chef-lieu ou un point central. "
           "Équipements recensés en 2021-2022, non vérifiés, hors indicateurs.")
pied()
