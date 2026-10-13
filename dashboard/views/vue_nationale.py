"""Page 1 — Vue nationale. Synthèse du projet : 6 chiffres clés, carte du Togo, 4 cartes de thème, permis 2024,
immatriculations et permis, 5 messages. Point d'entrée vers les pages de détail (design-page1.md). Aucun recalcul."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402
from shapely.geometry import shape as shp_shape  # noqa: E402

from composants import (ariane, carte_kpi, constat, entete, export_csv, fenetre_geo, habiller, limite,  # noqa: E402
                        note, pied, rangee_kpi, synthese, titre_bloc, tracer)
from donnees import contours, contours_regions, couche, fr, lire  # noqa: E402
from theme import (BLEUS, COULEUR_REGION, COULEUR_ZONE, ENCRE, HORS_SELECTION, ROUGE_DRAPEAU, SERIE,  # noqa: E402
                   THEME)

ind = lire("07_indicateurs", "indicateurs_07")
reg = lire("08_priorisation", "regions_08")
pref10 = lire("10_recommandations", "prefectures_10")
taux = lire("09_diagnostic", "taux_09")
pays = reg[reg.Maille == "Pays"].iloc[0]
NAT = ind[ind.Maille == "National"]


def val(idc, annee=None, cat=None):
    s = ind[(ind.ID == idc) & (ind.Maille == "National")]
    if annee is not None:
        s = s[s["Année"].astype(str) == str(annee)]
    if cat is not None:
        s = s[s["Catégorie"] == cat]
    return float(s.iloc[0]["Valeur"])


ariane("Vue nationale")
entete("Vue nationale", "La mobilité et la sécurité routière au Togo : où en est-on ?",
       "Le parc immatriculé a <strong>plus que quadruplé en vingt ans</strong>, porté par les motos. "
       "Les accidents augmentent en volume — <strong>683 tués</strong> et <strong>7 507 accidents</strong> en 2022 — "
       "mais les six taux de risque baissent. Le réseau reste inégalement entretenu, et "
       "<strong>23 préfectures sur 39</strong> n'ont aucune auto-école agréée.", carte=True)

# ---------------------------------------------------------------- Section 1 — 6 chiffres clés
immat24 = val("O1-01", 2024, "Ensemble")
motos24 = val("O1-01", 2024, "Moto")


def variation(idc, cat, annee, sens_hausse):
    """Badge de tendance : variation sur un an lue dans indicateurs_07 (aucun calcul autre que le rapport).
    `sens_hausse` dit ce que signifie une hausse : "pire" (victimes) ou "neutre" (immatriculations)."""
    v, avant = val(idc, annee, cat), val(idc, annee - 1, cat)
    pct = (v / avant - 1) * 100
    signe = "+" if pct > 0 else "−"
    sens = sens_hausse if pct > 0 else ("mieux" if sens_hausse == "pire" else "neutre")
    return f"{signe}{fr(abs(pct), 1)} %", f"vs {annee - 1}", sens


rangee_kpi("La situation en bref", [
    carte_kpi("Population", fr(pays.Population), "habitants", "La population de référence de tous les taux.",
              periode="2022", icone="population"),
    carte_kpi("Immatriculations", fr(immat24), f"dont {fr(motos24 / immat24 * 100, 1)} % de motos ({fr(motos24)})",
              "Immatriculations de l'année, pas le parc en circulation.", periode="2024", icone="vehicule",
              tendance=variation("O1-01", "Ensemble", 2024, "neutre")),
    carte_kpi("Morts sur la route", fr(val("O2-01", 2022, "Tués")), "tués déclarés par la police et la gendarmerie",
              f"{fr(val('O2-01', 2022, 'Accidents constatés'))} accidents constatés la même année.", periode="2022",
              icone="tues", tendance=variation("O2-01", "Tués", 2022, "pire")),
    carte_kpi("Blessés sur la route", fr(val("O2-01", 2022, "Blessés")), "blessés déclarés",
              "Accidents déclarés, données nationales seulement.", periode="2022", icone="blesses",
              tendance=variation("O2-01", "Blessés", 2022, "pire")),
    carte_kpi("Réseau routier évalué", f"{fr(pays['Km évalués'] / 1000, 1)} ", "dont 84 tronçons",
              f"{fr(pays['O3-02'], 1)} % en mauvais état ({fr(pays['Km en mauvais état'], 0)} km).",
              unite="k km", periode="2020", icone="route"),
    carte_kpi("Préfectures sans auto-école agréée", "23 sur 39", "n'ont aucune auto-école agréée",
              "2 932 492 habitants concernés.", icone="ecole"),
], une_ligne=True)

# ---------------------------------------------------------------- Section 2 — Carte du Togo
st.markdown("")

CLASSES_POP = [(0, 100_000, "moins de 100 000"), (100_000, 150_000, "100 000 à 150 000"),
               (150_000, 200_000, "150 000 à 200 000"), (200_000, 300_000, "200 000 à 300 000"),
               (300_000, float("inf"), "300 000 ou plus")]
COUL_ROUTE = {"Route nationale revêtue": "#0d366b", "Route nationale non revêtue": "#3987e5",
              "Voirie urbaine": "#eb6834", "Piste rurale": "#1baf7a"}
# Du plus fréquent au plus rare : le plus rare est dessiné en dernier, pour rester visible.
COUL_EQUIP = {"Panneau de signalisation": "#eb6834", "Ralentisseur": "#2a78d6", "Passage piéton": "#1baf7a",
              "Feu tricolore": "#eda100"}


def _classe_pop(v):
    for i, (bas, haut, _) in enumerate(CLASSES_POP):
        if bas <= v < haut:
            return i
    return len(CLASSES_POP) - 1


def _echelle_discrete(couleurs):
    """Colorscale en bandes égales : z = indice de classe + 0,5, zmin 0, zmax n."""
    n = len(couleurs)
    sc = []
    for i, c in enumerate(couleurs):
        sc += [[i / n, c], [(i + 1) / n, c]]
    return sc


def _lignes(gdf, types):
    """Coordonnées lon/lat d'un ensemble de tronçons, regroupées par type."""
    out = {}
    for typ in types:
        sub = gdf[gdf.Type == typ]
        lon, lat = [], []
        for geom in sub.geometry:
            for line in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
                xs, ys = line.xy
                lon += list(xs) + [None]
                lat += list(ys) + [None]
        out[typ] = (lon, lat)
    return out


@st.cache_data(show_spinner=False)
def _centroides_vn():
    """Un point intérieur par préfecture, pour écrire son nom sur l'agrandissement."""
    g = contours("prefectures")
    return {ft["properties"]["code"]: shp_shape(ft["geometry"]).representative_point().coords[0]
            for ft in g["features"]}


@st.cache_data(show_spinner=False)
def _equipements():
    """Par type : lon, lat et préfecture de chaque équipement. Les passages piétons, publiés en polygones, sont
    montrés par un point intérieur, comme sur la page Carte."""
    eq = couche("equipements")
    pts = eq.geometry.representative_point()
    return {t: (list(pts[eq.Type == t].x), list(pts[eq.Type == t].y),
                list(eq.loc[eq.Type == t, "Préfecture"].fillna("hors des 39 préfectures")))
            for t in COUL_EQUIP}


@st.cache_data(show_spinner=False)
def _table_carte():
    """Une ligne par préfecture, avec tout ce que l'info-bulle affiche (design-page1 §2)."""
    p = pref10[["Préfecture", "Zone", "Région", "Population", "Formation — auto-écoles comptées",
                "Réseau — km évalués", "Réseau — part en mauvais état (%)", "Priorité", "Leviers"]].copy()
    p = p.rename(columns={"Préfecture": "code", "Formation — auto-écoles comptées": "ae",
                          "Réseau — km évalués": "km", "Réseau — part en mauvais état (%)": "part"})
    p["nom"] = p["code"]
    p["part_txt"] = [fr(v, 1) + " %" if v == v else "non définie (aucune route classée)" for v in p["part"]]
    p["km_txt"] = [fr(v, 1) + " km" if v == v and v > 0 else "aucune route classée" for v in p["km"]]
    p["classe"] = [_classe_pop(v) for v in p["Population"]]
    return p


pcarte = _table_carte()
geo = contours("prefectures")
geo_reg = contours_regions()

# Filtres de la barre latérale, comme sur les pages Carte et Priorités : « ou » dans un filtre, « et » entre filtres ;
# les préfectures écartées passent en beige.
f_zones = st.session_state.get("f_zones", [])
f_prio = st.session_state.get("f_priorites", [])
f_leviers = st.session_state.get("f_leviers", [])
garde = pcarte["code"].notna()
if f_zones:
    garde &= pcarte["Zone"].isin(f_zones)
if f_prio:
    garde &= pcarte["Priorité"].isin(f_prio)
if f_leviers:
    garde &= pcarte["Leviers"].astype(str).apply(lambda s: any(lv.lower() in s for lv in f_leviers))
hors = set(pcarte.loc[~garde, "code"])
pvis = pcarte[garde]

titre_bloc("Le Togo, préfecture par préfecture",
           "Les 5 régions sont tracées en couleur ; l'agrandissement montre la région Maritime et le Grand Lomé. "
           "Molette ou barre d'outils pour zoomer.")
constat("Le Togo compte <strong>8 095 498</strong> habitants, très inégalement répartis : le Grand Lomé en "
        "concentre près du quart. La densité des auto-écoles agréées suit les grandes villes, tandis que "
        f"<strong style='color:{ROUGE_DRAPEAU}'>23 préfectures</strong> rurales n'en ont aucune.")

gauche, droite = st.columns([1.25, 1], vertical_alignment="top")   # carte resserrée ; légendes et notes à droite
with gauche:
    couche_choisie = st.radio(
        "Couche", ["Toutes les couches", "Population", "Régions", "Auto-écoles", "Routes classées",
                   "Routes nationales seules", "Équipements routiers"],
        horizontal=True, label_visibility="collapsed", key="vn_couche")

    montre_pop = couche_choisie in ("Toutes les couches", "Population")
    montre_ae = couche_choisie in ("Toutes les couches", "Auto-écoles")
    montre_routes = couche_choisie in ("Toutes les couches", "Routes classées")
    montre_rn = couche_choisie == "Routes nationales seules"
    montre_equip = couche_choisie == "Équipements routiers"
    regions_pleines = couche_choisie == "Régions"

    ae_data = couche("auto_ecoles")
    ae_agree = ae_data[ae_data["Comptée (R-12)"]]
    ae_non = ae_data[~ae_data["Comptée (R-12)"]]
    routes_gdf = couche("routes_classees") if (montre_routes or montre_rn) else None

    fig = go.Figure()
    for cible, inset in [("geo", False), ("geo2", True)]:
        sl = not inset
        if hors:
            fig.add_choropleth(
                geojson=geo, featureidkey="properties.code", locations=sorted(hors), z=[0] * len(hors),
                colorscale=[[0, HORS_SELECTION], [1, HORS_SELECTION]], showscale=False, geo=cible,
                marker_line_color="#ffffff", marker_line_width=0.7, hoverinfo="skip")
        if montre_pop:
            fig.add_choropleth(
                geojson=geo, featureidkey="properties.code", locations=list(pvis["code"]),
                z=[c + 0.5 for c in pvis["classe"]], zmin=0, zmax=len(BLEUS),
                colorscale=_echelle_discrete(BLEUS), showscale=False, geo=cible,
                marker_line_color="#ffffff", marker_line_width=0.7,
                customdata=[[z, r, fr(p), int(a), k, pt] for z, r, p, a, k, pt in zip(
                    pvis["Zone"], pvis["Région"], pvis["Population"], pvis["ae"], pvis["km_txt"],
                    pvis["part_txt"])],
                hovertemplate="<b>%{location}</b><br>Zone : %{customdata[0]} · Région : %{customdata[1]}"
                              "<br>Population : %{customdata[2]} habitants"
                              "<br>Auto-écoles agréées : %{customdata[3]}"
                              "<br>Réseau évalué : %{customdata[4]}"
                              "<br>En mauvais état : %{customdata[5]}<extra></extra>")
        elif regions_pleines:
            for nom_reg, coul_r in COULEUR_REGION.items():
                mask = pvis["Région"] == nom_reg
                prefs = list(pvis.loc[mask, "code"])
                if not prefs:
                    continue
                fig.add_choropleth(
                    geojson=geo, featureidkey="properties.code", locations=prefs,
                    z=[0] * len(prefs), colorscale=[[0, coul_r], [1, coul_r]],
                    showscale=False, geo=cible, marker_line_color="#ffffff", marker_line_width=0.7,
                    marker_opacity=0.55,
                    customdata=[[z, nom_reg, fr(p), int(a)] for z, p, a in zip(
                        pvis.loc[mask, "Zone"], pvis.loc[mask, "Population"], pvis.loc[mask, "ae"])],
                    hovertemplate="<b>%{location}</b><br>Zone : %{customdata[0]} · Région : %{customdata[1]}"
                                  "<br>Population : %{customdata[2]} habitants"
                                  "<br>Auto-écoles agréées : %{customdata[3]}<extra></extra>")
        else:
            fond = "#f6f5f0" if (montre_routes or montre_rn or montre_equip) else "#f2f1ec"
            if hors:   # sans couche de fond, le territoire choisi se confondrait avec le beige du reste
                zones = list(COULEUR_ZONE)
                z, echelle, zmax, opacite = ([zones.index(v) + 0.5 for v in pvis["Zone"]],
                                             _echelle_discrete(list(COULEUR_ZONE.values())), len(zones), 0.35)
            else:
                z, echelle, zmax, opacite = [0] * len(pvis), [[0, fond], [1, fond]], 1, 1
            fig.add_choropleth(
                geojson=geo, featureidkey="properties.code", locations=list(pvis["code"]),
                z=z, zmin=0, zmax=zmax, colorscale=echelle, marker_opacity=opacite, showscale=False, geo=cible,
                marker_line_color="#d8d6cc", marker_line_width=0.6,
                customdata=[[z, r, fr(p), int(a)] for z, r, p, a in zip(
                    pvis["Zone"], pvis["Région"], pvis["Population"], pvis["ae"])],
                hovertemplate="<b>%{location}</b><br>Zone : %{customdata[0]} · Région : %{customdata[1]}"
                              "<br>Population : %{customdata[2]} habitants"
                              "<br>Auto-écoles agréées : %{customdata[3]}<extra></extra>")
        for nom_reg, coul_r in COULEUR_REGION.items():
            fig.add_choropleth(
                geojson=geo_reg, featureidkey="properties.code", locations=[nom_reg], z=[0],
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False, geo=cible, marker_line_color=coul_r, marker_line_width=2.2,
                showlegend=False, hovertemplate=f"<b>Région {nom_reg}</b><extra></extra>")
        if montre_routes:
            for typ, (lon, lat) in _lignes(routes_gdf, list(COUL_ROUTE)).items():
                fig.add_scattergeo(lon=lon, lat=lat, mode="lines", name=typ, geo=cible,
                                   line=dict(width=1.0, color=COUL_ROUTE[typ]), hoverinfo="skip", showlegend=sl)
        if montre_rn:
            nationales = ["Route nationale revêtue", "Route nationale non revêtue"]
            for typ, (lon, lat) in _lignes(routes_gdf, nationales).items():
                fig.add_scattergeo(lon=lon, lat=lat, mode="lines", name=typ, geo=cible,
                                   line=dict(width=2.0 if "non" not in typ else 1.6, color=COUL_ROUTE[typ],
                                             dash="solid" if "non" not in typ else "dash"),
                                   hoverinfo="skip", showlegend=sl)
        if montre_ae:
            fig.add_scattergeo(lon=ae_non.geometry.x, lat=ae_non.geometry.y, mode="markers", geo=cible,
                               name=f"Non agréée ou non renseignée ({len(ae_non)})",
                               marker=dict(size=8 if inset else 7, color="#e6b422",
                                           line=dict(width=0.8, color="#7a5a00")),
                               text=ae_non["Préfecture"], showlegend=sl,
                               hovertemplate="Auto-école non agréée — %{text}<extra></extra>")
            fig.add_scattergeo(lon=ae_agree.geometry.x, lat=ae_agree.geometry.y, mode="markers", geo=cible,
                               name=f"Agréée ({len(ae_agree)})",
                               marker=dict(size=12 if inset else 10, color="#16834a",
                                           line=dict(width=1.3, color="#ffffff")),
                               text=ae_agree["Préfecture"], showlegend=sl,
                               hovertemplate="Auto-école agréée — %{text}<extra></extra>")
        if montre_equip:
            for typ, (lon, lat, prefs) in _equipements().items():
                fig.add_scattergeo(lon=lon, lat=lat, mode="markers", geo=cible, text=prefs,
                                   name=f"{typ} ({fr(len(lon))})", legendgroup=typ, showlegend=sl,
                                   marker=dict(size=4.5 if inset else 3.5, color=COUL_EQUIP[typ], opacity=0.75),
                                   hovertemplate=f"{typ} — %{{text}}<extra></extra>")

    SUD = [c for c, r in zip(pcarte["code"], pcarte["Région"]) if r == "Maritime"]
    cen = _centroides_vn()
    fig.add_scattergeo(lon=[cen[p][0] for p in SUD if p in cen], lat=[cen[p][1] for p in SUD if p in cen],
                       mode="text", geo="geo2", text=[p for p in SUD if p in cen],
                       textfont=dict(size=9, color="#141413"), hoverinfo="skip", showlegend=False)

    xs, ys = [], []
    for ft in geo["features"]:
        x0, y0, x1, y1 = ft["bbox"]
        xs += [x0, x1]; ys += [y0, y1]
    lon_t, lat_t = [min(xs) - 0.05, max(xs) + 0.05], [min(ys) - 0.05, max(ys) + 0.05]
    sud_set = set(SUD)
    xs_s, ys_s = [], []
    for ft in geo["features"]:
        if ft["properties"]["code"] in sud_set:
            x0, y0, x1, y1 = ft["bbox"]
            xs_s += [x0, x1]; ys_s += [y0, y1]
    lon_s, lat_s = [min(xs_s) - 0.03, max(xs_s) + 0.03], [min(ys_s) - 0.03, max(ys_s) + 0.03]
    if montre_equip:
        eq = _equipements()
        n_eq_sud = sum(p in sud_set for _, _, prefs in eq.values() for p in prefs)
        sous_titre_sud = f"{fr(n_eq_sud)} des {fr(sum(len(v[0]) for v in eq.values()))} équipements"
    else:
        n_agree_sud = sum(1 for p in ae_agree["Préfecture"] if p in sud_set)
        sous_titre_sud = f"{n_agree_sud} des {len(ae_agree)} auto-écoles agréées"

    base_geo = dict(visible=False, bgcolor="#ffffff", projection=dict(type="mercator"))
    fig.update_layout(
        geo=dict(**base_geo, domain=dict(x=[0, 0.48], y=[0, 1]),
                 lonaxis=dict(range=lon_t), lataxis=dict(range=lat_t)),
        geo2=dict(**base_geo, domain=dict(x=[0.52, 1.0], y=[0.05, 0.82]),
                  lonaxis=dict(range=lon_s), lataxis=dict(range=lat_s)),
        height=620, margin=dict(l=0, r=0, t=48, b=0), paper_bgcolor="#ffffff",
        legend=dict(orientation="h", y=-0.02, x=0, font=dict(size=10)),
        font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE),
        hoverlabel=dict(bgcolor="#ffffff", font_size=12), separators=", ",
        annotations=[
            dict(x=0.0, y=1.05, xref="paper", yref="paper", xanchor="left", showarrow=False,
                 font=dict(size=11, color=ENCRE),
                 text="<b>Le Togo, préfecture par préfecture</b>"),
            dict(x=0.52, y=1.05, xref="paper", yref="paper", xanchor="left", showarrow=False,
                 font=dict(size=11, color=ENCRE),
                 text="<b>Maritime et Grand Lomé, agrandi</b><br>"
                      f"<span style='font-size:10px;color:#55534e'>{sous_titre_sud}</span>")])
    st.plotly_chart(fig, key="vn_carte", config={"displayModeBar": True, "scrollZoom": True,
                                                 "displaylogo": False,
                                                 "modeBarButtonsToRemove": ["select2d", "lasso2d"]})

with droite:
    nb_pref = pcarte.groupby("Région")["code"].nunique()          # préfectures par région (prefectures_10)
    pastilles_reg = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
        f'<span style="width:16px;height:0;border-top:3px solid {c};display:inline-block"></span>{r} '
        f'({nb_pref[r]} préfectures)</span>'
        for r, c in COULEUR_REGION.items())
    st.markdown(f'<div class="filtres-actifs"><b>Les 5 régions :</b> {pastilles_reg}</div>', unsafe_allow_html=True)

    if hors:
        filtres = []
        if f_zones:
            filtres.append("zone " + ", ".join(f'<b style="color:{COULEUR_ZONE[z]}">{z}</b>' for z in f_zones))
        if f_prio:
            filtres.append("priorité " + ", ".join(f"<b>{p.lower()}</b>" for p in f_prio))
        if f_leviers:
            filtres.append("levier " + ", ".join(f"<b>{lv.lower()}</b>" for lv in f_leviers))
        resultat = (f"{len(pvis)} préfecture{'s' if len(pvis) > 1 else ''} sur {len(pcarte)}." if len(pvis)
                    else "aucune préfecture ne répond à ces filtres.")
        st.markdown(
            f'<div class="filtres-actifs"><b>Filtres :</b> {" · ".join(filtres)} — {resultat} '
            f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:.74rem">'
            f'<span style="width:13px;height:13px;border-radius:3px;background:{HORS_SELECTION};'
            f'border:1px solid #d8d6cc"></span>hors des filtres <b>({len(hors)})</b></span></div>',
            unsafe_allow_html=True)

    if montre_pop:
        effectifs = pvis["classe"].value_counts()
        chips = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
            f'<span style="width:13px;height:13px;border-radius:3px;background:{BLEUS[i]};'
            f'border:1px solid #d8d6cc"></span>{lib} <b>({int(effectifs.get(i, 0))})</b></span>'
            for i, (_, _, lib) in enumerate(CLASSES_POP))
        st.markdown(f'<div class="filtres-actifs"><b>Population 2022, 5 classes :</b><br>{chips}</div>',
                    unsafe_allow_html=True)

    if montre_equip:
        eq = _equipements()
        chips_eq = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
            f'<span style="width:10px;height:10px;border-radius:50%;background:{c}"></span>{t} '
            f'<b>({fr(len(eq[t][0]))})</b></span>'
            for t, c in COUL_EQUIP.items())
        st.markdown(f'<div class="filtres-actifs"><b>Équipements de sécurité routière :</b><br>{chips_eq}<br>'
                    'Collecte 2021-2022, non vérifiée ; ils n\'entrent dans aucun indicateur. Cliquez sur un type '
                    'dans la légende de la carte pour le masquer.</div>', unsafe_allow_html=True)

    st.markdown('<div class="filtres-actifs"><b>Permis : données nationales seulement.</b> '
                '38 531 permis délivrés en 2024, dont 10 165 permis moto. Les permis n\'ont ni territoire, ni âge, ni mois.</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="filtres-actifs">Les 5 régions sont tracées en couleur sur toutes les couches (Maritime, '
                'Plateaux, Centrale, Kara, Savanes). Survolez une préfecture pour sa zone, sa région, sa population, '
                'ses auto-écoles agréées et l\'état de son réseau. Les filtres de la barre latérale (zone, '
                'priorité, levier) gardent en couleur les préfectures choisies ; les autres passent en beige.</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="filtres-actifs">Réseau : relevé de 2020. Auto-écoles : collecte 2021-2022, activité non '
                'vérifiée.</div>', unsafe_allow_html=True)
    if st.button("Voir la carte détaillée →", key="vn_lien_carte"):
        st.switch_page("views/carte.py")


# ---------------------------------------------------------------- Section 3 — 4 cartes de thème
st.markdown("")
titre_bloc("Les quatre thèmes confirmés")


def _mini(fig, cle, hauteur=110):
    fig.update_layout(height=hauteur, margin=dict(l=4, r=4, t=4, b=4), paper_bgcolor="#ffffff",
                      plot_bgcolor="#ffffff", showlegend=False,
                      font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE, size=9),
                      xaxis=dict(visible=False), yaxis=dict(visible=False), separators=", ")
    st.plotly_chart(fig, key=cle, config={"displayModeBar": False, "staticPlot": True})


c1, c2, c3, c4 = st.columns(4)
mult = 4.56
with c1:
    st.markdown('<div class="reco-theme mob"><span class="reco-pastille" style="background:#dbeafe">🚗</span>'
                '<span class="reco-theme-lib" style="color:#1c5cab">Mobilité</span></div>', unsafe_allow_html=True)
    st.markdown(f"**{fr(immat24)}** immatriculations (2024)  \n"
                f"**×{fr(mult, 2)}** en 20 ans (2002 → 2022)  \n"
                f"**{fr(motos24 / immat24 * 100, 1)} %** de motos (2024)")
    ens = NAT[(NAT.ID == "O1-01") & (NAT["Catégorie"] == "Ensemble")].copy()
    ens = ens[ens["Année"].astype(str).str.fullmatch(r"\d{4}")]
    ens["Année"] = ens["Année"].astype(int)
    ens = ens.sort_values("Année")
    f = go.Figure(go.Scatter(x=ens["Année"], y=ens["Valeur"], mode="lines",
                             line=dict(color=THEME["Mobilité"], width=2), fill="tozeroy",
                             fillcolor="rgba(36,116,198,0.12)"))
    for an in (1995, 2004):
        f.add_vline(x=an, line=dict(color="#b9b6ad", width=1, dash="dot"))
    _mini(f, "vn_mini_mob")
    st.caption("Immatriculations 1990–2024 ; ruptures de série de 1995 et 2004 en pointillé.")
    if st.button("Voir le détail →", key="vn_t_mob"):
        st.session_state["evolutions_rang"] = 1
        st.switch_page("views/evolutions.py")
with c2:
    st.markdown('<div class="reco-theme sec"><span class="reco-pastille" style="background:#fef3c7">🚦</span>'
                '<span class="reco-theme-lib" style="color:#b45309">Sécurité routière</span></div>', unsafe_allow_html=True)
    st.markdown(f"**{fr(val('O2-01', 2022, 'Tués'))}** tués (2022)  \n"
                f"**{fr(val('O2-01', 2022, 'Accidents constatés'))}** accidents constatés (2022)  \n"
                f"**60 %** des tués à moto ou trois-roues (2021)")
    six = taux[taux.Lecture != "volume"].copy()
    six["lib"] = six["Mesure"].str[:3] + " " + six["Lecture"].str.replace("pour ", "/", regex=False)
    f = go.Figure(go.Bar(x=six["Variation (%)"], y=six["lib"], orientation="h",
                         marker_color=THEME["Sécurité routière"]))
    f.add_vline(x=0, line=dict(color="#8a8780", width=1))
    _mini(f, "vn_mini_sec")
    st.caption("Les 6 taux, 2010–2012 face à 2022–2024 : tous en baisse.")
    st.caption("Accidents déclarés, données nationales seulement.")
    if st.button("Voir le détail →", key="vn_t_sec"):
        st.session_state["evolutions_rang"] = 2
        st.switch_page("views/evolutions.py")
with c3:
    st.markdown('<div class="reco-theme res"><span class="reco-pastille" style="background:#fce7f3">🛣️</span>'
                '<span class="reco-theme-lib" style="color:#b4451a">Réseau</span></div>', unsafe_allow_html=True)
    st.markdown(f"**{fr(pays['Km évalués'], 0)} km** évalués (relevé de 2020)  \n"
                f"**{fr(pays['O3-02'], 1)} %** en mauvais état ({fr(pays['Km en mauvais état'], 0)} km)  \n"
                f"**49** tronçons critiques")
    mauvais = pcarte[["code", "part"]].copy()
    f = go.Figure(go.Choropleth(
        geojson=geo, featureidkey="properties.code", locations=list(mauvais["code"]),
        z=list(mauvais["part"]), colorscale="Reds", showscale=False,
        marker_line_color="#ffffff", marker_line_width=0.4, hoverinfo="skip"))
    fenetre_geo(f, geo)
    f.update_layout(height=110, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#ffffff", showlegend=False)
    st.plotly_chart(f, key="vn_mini_res", config={"displayModeBar": False, "staticPlot": True})
    st.caption("Part en mauvais état par préfecture.")
    if st.button("Voir le détail →", key="vn_t_res"):
        st.switch_page("views/carte.py")
with c4:
    st.markdown('<div class="reco-theme couv"><span class="reco-pastille" style="background:#e2f4ec">🏫</span>'
                '<span class="reco-theme-lib" style="color:#11613f">Couverture</span></div>', unsafe_allow_html=True)
    st.markdown("**132** auto-écoles agréées, sur 272 recensées  \n"
                "**23 sur 39** préfectures sans auto-école agréée  \n"
                "**17,2 %** des ruraux à moins de 2 km d'une route revêtue")
    equipees, total_pref = 16, 39
    part = equipees / total_pref * 100
    st.markdown(
        f'<div style="margin:6px 0 2px"><div style="height:16px;border-radius:8px;background:#ebe8e0;overflow:hidden">'
        f'<div style="width:{part:.1f}%;height:100%;background:{THEME["Couverture"]}"></div></div>'
        f'<div style="font-size:.74rem;color:#55534e;margin-top:4px"><b>{equipees} préfectures sur {total_pref}</b> '
        f'ont au moins une auto-école agréée ({fr(part, 1)} %)</div></div>', unsafe_allow_html=True)
    st.caption("Accès rural estimé, niveau C.")
    if st.button("Voir le détail →", key="vn_t_couv"):
        st.switch_page("views/comparaison.py")


# ---------------------------------------------------------------- Section 4 — Permis 2024
st.markdown("")
titre_bloc("Permis de conduire délivrés", "Total et décomposition par catégorie")
g_tot, d_graph = st.columns([1, 3.2], vertical_alignment="center")
with d_graph:
    permis = NAT[(NAT.ID == "O1-06") & (NAT["Année"].astype(str) == "2024")][["Catégorie", "Valeur"]].copy()
    lib = {"A": "A — Moto", "B": "B — Voiture légère", "C": "C — Poids lourd", "D": "D — Transport en commun",
           "E": "E — Semi-remorque", "F": "F — Voiture spéciale"}
    permis["lib"] = permis["Catégorie"].map(lib)
    permis = permis.sort_values("Valeur")
    # Une couleur par catégorie, celle de la page Évolutions (PERMIS_COUL) ; E, vert de C éclairci (pointillé là-bas)
    coul_permis = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "E": "#8fd7bd", "D": "#eda100", "F": "#8a8780"}
    fig = go.Figure(go.Bar(x=permis.Valeur, y=permis.lib, orientation="h",
                           marker_color=[coul_permis[c] for c in permis["Catégorie"]]))
    for lib_c, v in zip(permis.lib, permis.Valeur):          # chiffres alignés à droite, hors des barres
        fig.add_annotation(x=1, xref="paper", xanchor="left", xshift=10, y=lib_c, text=f"<b>{fr(v)}</b>",
                           showarrow=False, font=dict(size=12, color=ENCRE))
    habiller(fig, 300, xaxis=dict(gridcolor="#efece4"), yaxis=dict(gridcolor="rgba(0,0,0,0)"), legend=dict(x=0, y=1))
    fig.update_layout(margin=dict(r=70))
    tracer(fig, "vn_permis")
with g_tot:
    st.markdown(f'<div class="total-carte"><div class="total-chiffre">{fr(sum(permis.Valeur))}</div>'
                '<div class="total-legende">permis délivrés en 2024, toutes catégories</div>'
                '<div class="total-note">Niveau A. Données nationales : les permis n\'ont ni territoire, ni âge.</div>'
                '</div>', unsafe_allow_html=True)
st.markdown('<div class="note-carte">Les permis moto ont bondi : 4 837 en 2022 et 10 165 en 2024, contre '
            '211 en 2021.</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- Section 5 — Immatriculations et permis (2 étages)
st.markdown("")
titre_bloc("Immatriculations et permis, 1990–2024",
           "Deux étages sur la même échelle des années : une date se lit sur les deux séries à la fois.")
COUL = {k: SERIE[k] for k in ("Moto", "Voiture", "Poids lourd", "Bus et car", "Autres")}
PERMIS_COUL = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "E": "#1baf7a", "D": "#eda100", "F": "#8a8780"}
PERMIS_TRAIT = {"A": "solid", "B": "solid", "C": "solid", "E": "dash", "D": "solid", "F": "dot"}

immat = NAT[(NAT.ID == "O1-01") & (NAT["Catégorie"] != "Ensemble")].copy()
immat = immat[immat["Année"].astype(str).str.fullmatch(r"\d{4}")]
immat["Année"] = immat["Année"].astype(int)
permis_s = NAT[NAT.ID == "O1-06"].copy()
permis_s = permis_s[permis_s["Année"].astype(str).str.fullmatch(r"\d{4}")]
permis_s["Année"] = permis_s["Année"].astype(int)
permis_s.loc[permis_s["Année"] == 2013, "Valeur"] = None  # 2013 non renseignée : la courbe s'interrompt

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09,
                    subplot_titles=("Immatriculations de l'année", "Permis délivrés"))
for cat, coul in COUL.items():
    s = immat[immat["Catégorie"] == cat].sort_values("Année")
    fig.add_trace(go.Scatter(x=s["Année"], y=s["Valeur"], name=cat, mode="lines", line=dict(color=coul, width=2),
                             legend="legend"), row=1, col=1)
for cat in ["A", "B", "C", "D", "E", "F"]:
    s = permis_s[permis_s["Catégorie"] == cat].sort_values("Année")
    fig.add_trace(go.Scatter(x=s["Année"], y=s["Valeur"], name=f"Permis {cat}", mode="lines",
                             line=dict(color=PERMIS_COUL[cat], width=2, dash=PERMIS_TRAIT[cat]),
                             legend="legend2", connectgaps=False), row=2, col=1)

# Ruptures de série, sur l'étage des immatriculations
for an in (1995, 2004):
    fig.add_vline(x=an, line=dict(color="#b9b6ad", width=1, dash="dot"), row=1, col=1)
fig.add_annotation(x=1995, y=1.0, yref="y domain", text="rupture de série", showarrow=False, yshift=-4,
                   font=dict(color="#8a8780", size=9), row=1, col=1)
fig.add_annotation(x=2004, y=1.0, yref="y domain", text="rupture de série", showarrow=False, yshift=-4,
                   font=dict(color="#8a8780", size=9), row=1, col=1)

# Repères de contexte, numérotés, qui traversent les deux étages
for an, lab in [(2019, "①"), (2022, "②"), (2023, "③")]:
    fig.add_vline(x=an, line=dict(color="#b9b6ad", width=1, dash="dash"))
    fig.add_annotation(x=an, y=1.06, yref="y domain", text=lab, showarrow=False,
                       font=dict(color="#55534e", size=12), row=1, col=1)

# Dernières valeurs, au bout des courbes, dans la couleur de la série
fig.add_annotation(x=2024, y=motos24, text=f"<b>{fr(motos24)}</b>", showarrow=False, xshift=24,
                   font=dict(color=COUL["Moto"], size=11), row=1, col=1)
for cat in ("B", "A"):
    der = permis_s[(permis_s["Catégorie"] == cat) & (permis_s["Année"] == 2024)]
    if len(der):
        fig.add_annotation(x=2024, y=float(der.iloc[0]["Valeur"]), text=f"<b>{fr(der.iloc[0]['Valeur'])}</b>",
                           showarrow=False, xshift=24, font=dict(color=PERMIS_COUL[cat], size=11), row=2, col=1)

fig.update_layout(height=560, margin=dict(l=10, r=62, t=44, b=10), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                  font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE, size=11), separators=", ",
                  legend=dict(orientation="h", y=1.14, x=0, font=dict(size=10)),
                  legend2=dict(orientation="h", y=0.46, x=0, font=dict(size=10)),
                  hoverlabel=dict(bgcolor="#ffffff"))
fig.update_xaxes(gridcolor="#efece4", range=[1989, 2026])
fig.update_yaxes(gridcolor="#efece4")
fig.add_annotation(x=1998, y=0.46, xref="x domain", yref="paper", text="Permis non publiés avant 2007",
                   showarrow=False, font=dict(color="#8a8780", size=10))
fig.add_annotation(x=2013, y=0.06, yref="y domain", text="2013 non renseignée", showarrow=False,
                   font=dict(color="#8a8780", size=9), row=2, col=1)
tracer(fig, "vn_immat_permis")
n_rouge, n_reperes = st.columns([1, 1.6], vertical_alignment="top")
n_rouge.markdown('<div class="note-carte blanche risque">En 2021, on comptait <strong>310 immatriculations de motos '
                 'pour chaque permis moto délivré</strong>, contre seulement <strong>6</strong> en 2024.</div>',
                 unsafe_allow_html=True)
n_reperes.markdown('<div class="note-carte blanche">Une date situe une variation ; elle ne l\'explique pas.<br>'
            '<b>Repères :</b> ① 2019 permis moto obligatoire · ② 2022 décret d\'application du code de la route · '
            '③ 2023 tournée d\'immatriculation des motos.</div>', unsafe_allow_html=True)

etage_haut = immat.pivot(index="Année", columns="Catégorie", values="Valeur")
etage_bas = NAT[NAT.ID == "O1-06"].copy()
etage_bas = etage_bas[etage_bas["Année"].astype(str).str.fullmatch(r"\d{4}")]
etage_bas["Année"] = etage_bas["Année"].astype(int)
etage_bas = etage_bas.pivot(index="Année", columns="Catégorie", values="Valeur").add_prefix("Permis ")
export_csv(etage_haut.join(etage_bas, how="outer").reset_index(),
           "immatriculations_et_permis_1990_2024.csv", "vn_exp_immat")


# ---------------------------------------------------------------- Section 6 — Messages, synthèse, limite
st.markdown("")
g, d = st.columns([1.3, 1], vertical_alignment="top")
with g:
    messages = [
        "<strong>Les immatriculations ont plus que quadruplé en 20 ans</strong> : ×4,56 de 2002 à 2022.",
        "<strong>Les motos portent la hausse</strong> : 80,6 % des immatriculations supplémentaires entre 2002 et 2022.",
        "<strong>Plus de véhicules, pas une route plus dangereuse</strong> : les accidents déclarés augmentent "
        "(+9,4 % entre 2010–2012 et 2022–2024), mais les 6 taux baissent.",
        "<strong>60 % des tués de 2021 sont des usagers de deux et trois-roues motorisés</strong>, un peu plus que "
        "leur part du parc (1,01 à 1,10 fois).",
        "<strong>7 questions restent sans réponse</strong>, faute d'accidents par préfecture, par mois et par âge."]
    puces = "".join(f'<li><span class="retenir-num">{i}</span><span>{m}</span></li>' for i, m in enumerate(messages, 1))
    st.markdown(f'<div class="retenir"><div class="retenir-titre">À retenir</div><ol>{puces}</ol></div>',
                unsafe_allow_html=True)
with d, st.container(key="vn_synthese"):       # carte verte : synthèse et bouton, même hauteur que « À retenir »
    synthese("8 095 498", "habitants, recensement de 2022",
             ["5 préfectures cumulent un réseau dégradé et aucune auto-école agréée (641 955 habitants).",
              "15 recommandations, dont 3 en priorité haute.",
              "23 préfectures sur 39 sans auto-école agréée (2 932 492 habitants)."])
    if st.button("Voir les recommandations →", key="vn_t_reco"):
        st.switch_page("views/recommandations.py")
limite("Les accidents ne sont publiés qu'au niveau national. Les volumes et les taux portent sur les accidents "
       "déclarés par la police et la gendarmerie, pas sur l'ensemble des accidents. Les taux par véhicule dépendent "
       "d'un parc estimé. Le coût des actions n'est pas dans les données.", titre="Limite")
pied()
