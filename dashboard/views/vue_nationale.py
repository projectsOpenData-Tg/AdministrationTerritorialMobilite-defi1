"""Page 1 — Vue nationale. Synthèse du projet : 6 chiffres clés, carte du Togo, 4 cartes de thème, permis 2024,
immatriculations et permis, 5 messages. Point d'entrée vers les pages de détail (design-page1.md). Aucun recalcul."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from composants import (ariane, carte_kpi, constat, entete, export_csv, fenetre_geo, habiller, limite,  # noqa: E402
                        note, pied, rangee_kpi, synthese, titre_bloc, tracer)
from donnees import contours, contours_regions, couche, fr, lire  # noqa: E402
from theme import BLEUS, COULEUR_REGION, ENCRE, ROUGE_DRAPEAU, SERIE, THEME  # noqa: E402

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
def _table_carte():
    """Une ligne par préfecture, avec tout ce que l'info-bulle affiche (design-page1 §2)."""
    p = pref10[["Préfecture", "Zone", "Région", "Population", "Formation — auto-écoles comptées",
                "Réseau — km évalués", "Réseau — part en mauvais état (%)"]].copy()
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

titre_bloc("Le Togo, préfecture par préfecture",
           "Les 5 régions sont tracées en couleur. Molette ou barre d'outils pour zoomer.")
constat("Le Togo compte <strong>8 095 498</strong> habitants, très inégalement répartis : le Grand Lomé en "
        "concentre près du quart. La densité des auto-écoles agréées suit les grandes villes, tandis que "
        f"<strong style='color:{ROUGE_DRAPEAU}'>23 préfectures</strong> rurales n'en ont aucune.")

gauche, droite = st.columns([1.25, 1], vertical_alignment="top")   # carte resserrée ; légendes et notes à droite
with gauche:
    couche_choisie = st.radio(
        "Couche", ["Toutes les couches", "Population", "Régions", "Auto-écoles", "Routes classées",
                   "Routes nationales seules"],
        horizontal=True, label_visibility="collapsed", key="vn_couche")

    montre_pop = couche_choisie in ("Toutes les couches", "Population")
    montre_ae = couche_choisie in ("Toutes les couches", "Auto-écoles")
    montre_routes = couche_choisie in ("Toutes les couches", "Routes classées")
    montre_rn = couche_choisie == "Routes nationales seules"
    regions_pleines = couche_choisie == "Régions"

    fig = go.Figure()

    # --- Fond : population en 5 classes, ou fond neutre
    if montre_pop:
        fig.add_choropleth(
            geojson=geo, featureidkey="properties.code", locations=list(pcarte["code"]),
            z=[c + 0.5 for c in pcarte["classe"]], zmin=0, zmax=len(BLEUS),
            colorscale=_echelle_discrete(BLEUS), showscale=False,
            marker_line_color="#ffffff", marker_line_width=0.7,
            customdata=[[z, r, fr(p), int(a), k, pt] for z, r, p, a, k, pt in zip(
                pcarte["Zone"], pcarte["Région"], pcarte["Population"], pcarte["ae"], pcarte["km_txt"],
                pcarte["part_txt"])],
            hovertemplate="<b>%{location}</b><br>Zone : %{customdata[0]} · Région : %{customdata[1]}"
                          "<br>Population : %{customdata[2]} habitants"
                          "<br>Auto-écoles agréées : %{customdata[3]}"
                          "<br>Réseau évalué : %{customdata[4]}"
                          "<br>En mauvais état : %{customdata[5]}<extra></extra>")
    elif not regions_pleines:
        fond = "#f6f5f0" if (montre_routes or montre_rn) else "#f2f1ec"
        fig.add_choropleth(
            geojson=geo, featureidkey="properties.code", locations=list(pcarte["code"]),
            z=[0] * len(pcarte), colorscale=[[0, fond], [1, fond]], showscale=False,
            marker_line_color="#d8d6cc", marker_line_width=0.6,
            customdata=[[z, r, fr(p), int(a)] for z, r, p, a in zip(
                pcarte["Zone"], pcarte["Région"], pcarte["Population"], pcarte["ae"])],
            hovertemplate="<b>%{location}</b><br>Zone : %{customdata[0]} · Région : %{customdata[1]}"
                          "<br>Population : %{customdata[2]} habitants"
                          "<br>Auto-écoles agréées : %{customdata[3]}<extra></extra>")

    # --- Les 5 régions : remplies (couche « Régions ») ou en contour de couleur sur toutes les autres couches
    for nom_reg, coul in COULEUR_REGION.items():
        fig.add_choropleth(
            geojson=geo_reg, featureidkey="properties.code", locations=[nom_reg], z=[0],
            colorscale=[[0, coul], [1, coul]] if regions_pleines else [[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            showscale=False, marker_line_color=coul,
            marker_line_width=1.0 if regions_pleines else 2.2,
            name=nom_reg, showlegend=False,  # légende des régions rendue en HTML sous la carte
            hovertemplate=f"<b>Région {nom_reg}</b><extra></extra>")

    # --- Routes
    if montre_routes:
        routes = couche("routes_classees")
        for typ, (lon, lat) in _lignes(routes, list(COUL_ROUTE)).items():
            fig.add_scattergeo(lon=lon, lat=lat, mode="lines", name=typ,
                               line=dict(width=1.0, color=COUL_ROUTE[typ]), hoverinfo="skip")
    if montre_rn:
        routes = couche("routes_classees")
        nationales = ["Route nationale revêtue", "Route nationale non revêtue"]
        for typ, (lon, lat) in _lignes(routes, nationales).items():
            fig.add_scattergeo(lon=lon, lat=lat, mode="lines", name=typ,
                               line=dict(width=2.0 if "non" not in typ else 1.6, color=COUL_ROUTE[typ],
                                         dash="solid" if "non" not in typ else "dash"), hoverinfo="skip")

    # --- Auto-écoles
    if montre_ae:
        ae = couche("auto_ecoles")
        ae["Statut affiché"] = ae["Comptée (R-12)"].map({True: "Agréée (132)",
                                                         False: "Non agréée ou non renseignée (140)"})
        for statut, coul in [("Agréée (132)", "#ffffff"), ("Non agréée ou non renseignée (140)", "#8a8780")]:
            s = ae[ae["Statut affiché"] == statut]
            fig.add_scattergeo(lon=s.geometry.x, lat=s.geometry.y, mode="markers", name=statut,
                               marker=dict(size=6, color=coul, line=dict(width=0.9, color="#141413")),
                               text=s["Préfecture"], hovertemplate="Auto-école — %{text}<extra></extra>")

    fenetre_geo(fig, geo)
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#ffffff",
                      legend=dict(orientation="h", y=-0.02, x=0, font=dict(size=10)),
                      font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE),
                      hoverlabel=dict(bgcolor="#ffffff", font_size=12), separators=", ")
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

    if montre_pop:
        effectifs = pcarte["classe"].value_counts()
        chips = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
            f'<span style="width:13px;height:13px;border-radius:3px;background:{BLEUS[i]};'
            f'border:1px solid #d8d6cc"></span>{lib} <b>({int(effectifs.get(i, 0))})</b></span>'
            for i, (_, _, lib) in enumerate(CLASSES_POP))
        st.markdown(f'<div class="filtres-actifs"><b>Population 2022, 5 classes :</b><br>{chips}</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="filtres-actifs"><b>Permis : données nationales seulement.</b> '
                '38 531 permis délivrés en 2024, dont 10 165 permis moto. Les permis n\'ont ni territoire, ni âge, ni mois.</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="filtres-actifs">Les 5 régions sont tracées en couleur sur toutes les couches (Maritime, '
                'Plateaux, Centrale, Kara, Savanes). Survolez une préfecture pour sa zone, sa région, sa population, '
                'ses auto-écoles agréées et l\'état de son réseau.</div>', unsafe_allow_html=True)
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
g, d = st.columns([1.5, 1], vertical_alignment="top")
with g:
    titre_bloc("Permis de conduire délivrés en 2024", "Par catégorie. L'objectif 1 demande les permis par catégorie.")
    permis = NAT[(NAT.ID == "O1-06") & (NAT["Année"].astype(str) == "2024")][["Catégorie", "Valeur"]].copy()
    lib = {"A": "A — Moto", "B": "B — Voiture légère", "C": "C — Poids lourd", "D": "D — Transport en commun",
           "E": "E — Semi-remorque", "F": "F — Voiture spéciale"}
    permis["lib"] = permis["Catégorie"].map(lib)
    permis = permis.sort_values("Valeur")
    fig = go.Figure(go.Bar(x=permis.Valeur, y=permis.lib, orientation="h", marker_color=BLEUS[2],
                           text=[fr(v) for v in permis.Valeur], textposition="outside"))
    habiller(fig, 300, xaxis=dict(gridcolor="#efece4"), yaxis=dict(gridcolor="rgba(0,0,0,0)"), legend=dict(x=0, y=1))
    tracer(fig, "vn_permis")
    note("Les permis moto ont bondi : 4 837 en 2022 et 10 165 en 2024, contre 211 en 2021.", forte=True)
with d:
    st.markdown("")
    st.markdown(f'<div class="synthese-chiffre" style="font-size:3rem">{fr(sum(permis.Valeur))}</div>'
                '<div class="synthese-legende">permis délivrés en 2024, toutes catégories</div>', unsafe_allow_html=True)
    st.caption("Niveau A. Données nationales : les permis n'ont ni territoire, ni âge.")


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
note("En 2021, 310 motos ont été immatriculées pour un permis moto délivré ; en 2024, 6.", forte=True)
note("Une date situe une variation ; elle ne l'explique pas. Repères : ① 2019 permis moto obligatoire · "
     "② 2022 décret d'application du code de la route · ③ 2023 tournée d'immatriculation des motos.")

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
    titre_bloc("À retenir")
    for m in ["**Les immatriculations ont plus que quadruplé en 20 ans** : ×4,56 de 2002 à 2022.",
              "**Les motos portent la hausse** : 80,6 % des immatriculations supplémentaires entre 2002 et 2022.",
              "**Plus de véhicules, pas une route plus dangereuse** : les accidents déclarés augmentent (+9,4 % entre "
              "2010–2012 et 2022–2024), mais les 6 taux baissent.",
              "**60 % des tués de 2021 sont des usagers de deux et trois-roues motorisés**, un peu plus que leur part "
              "du parc (1,01 à 1,10 fois).",
              "**7 questions restent sans réponse**, faute d'accidents par préfecture, par mois et par âge."]:
        st.markdown(f"- {m}")
with d:
    synthese("8 095 498", "habitants, recensement de 2022",
             ["5 préfectures cumulent un réseau dégradé et aucune auto-école agréée (641 955 habitants).",
              "15 recommandations, dont 3 en priorité haute.",
              "23 préfectures sur 39 sans auto-école agréée (2 932 492 habitants)."])
    if st.button("Voir les recommandations →", key="vn_lien_reco"):
        st.switch_page("views/recommandations.py")
limite("Les accidents ne sont publiés qu'au niveau national. Les volumes et les taux portent sur les accidents "
       "déclarés par la police et la gendarmerie, pas sur l'ensemble des accidents. Les taux par véhicule dépendent "
       "d'un parc estimé (niveau C). Le coût des actions n'est pas dans les données.")
pied()
