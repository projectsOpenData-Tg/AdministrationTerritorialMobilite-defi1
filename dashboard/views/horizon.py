"""Page 8 du plan, 7e du menu — Horizon 2031. Combien en faudra-t-il d'ici 1, 3 et 5 ans (design-page8.md).

La page ne calcule rien : elle lit les sorties de l'annexe A1 (horizon_A1, population_A1, national_A1, acces_A1,
emplacements_A1, sites_A1) et les titres de cartes_10. Curseur d'horizon unique, défaut +3 ans (2029)."""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402
from pyproj import Transformer  # noqa: E402
from shapely.geometry import shape  # noqa: E402

from composants import (ariane, badge, carte_kpi, constat, entete, export_csv, habiller, limite,  # noqa: E402
                        note, pied, rangee_kpi, synthese, table_html, titre_bloc, tracer)
from donnees import contours, couche, fr, lire  # noqa: E402
from theme import BLEUS, COULEUR_ZONE, ENCRE  # noqa: E402

INF = float("inf")

hz = lire("A1_horizon", "horizon_A1")
popz = lire("A1_horizon", "population_A1")
nat = lire("A1_horizon", "national_A1")
empl_tout = lire("A1_horizon", "emplacements_A1")
TOTAL_EMPL = "Ensemble des 23"                      # dernière ligne du fichier : le total, pas une préfecture
empl = empl_tout[empl_tout["Préfecture"] != TOTAL_EMPL]
empl_total = empl_tout[empl_tout["Préfecture"] == TOTAL_EMPL]
sites = lire("A1_horizon", "sites_A1")
pref10 = lire("10_recommandations", "prefectures_10")
cartes10 = lire("10_recommandations", "cartes_10").set_index("ID")

PALIERS = {"2022 · aujourd'hui mesuré": "Passé", "2026 · population d'aujourd'hui": "Actuel",
           "2027 · dans 1 an": "+1 an", "2029 · dans 3 ans": "+3 ans", "2031 · dans 5 ans": "+5 ans"}
ANNEE = {"Passé": 2022, "Actuel": 2026, "+1 an": 2027, "+3 ans": 2029, "+5 ans": 2031}
A_VENIR = ["Actuel", "+1 an", "+3 ans", "+5 ans"]
CIBLE_AE = 1.065                      # médiane des préfectures équipées, cible du levier formation
DEBUT_PROJECTION = 2024.5             # au-delà : plus aucune observation

GEO = contours("prefectures")
ZONE_PREF = pref10.set_index("Préfecture")["Zone"].to_dict()
SUD = sorted(pref10[pref10["Région"] == "Maritime"]["Préfecture"])
RANG_ONGLET = {"Réseau": 1, "Formation": 2, "Sécurité routière": 3, "Zones les moins desservies": 4, "Données": 5}

# Classes fixes : elles ne changent pas d'un horizon à l'autre, pour que les couleurs se comparent (plan §2).
CL_AE = [(0, 1, "aucune"), (1, 2, "1"), (2, 3, "2"), (3, 4, "3"), (4, INF, "4 ou plus")]
CL_KM = [(0, 1e-9, "aucun"), (1e-9, 10, "moins de 10 km"), (10, 25, "10 à 25 km"), (25, 40, "25 à 40 km"),
         (40, INF, "40 km ou plus")]
ABSENT = "#b9b6ad"


def _classe(v, classes):
    if v != v:
        return None
    for i, (bas, haut, _) in enumerate(classes):
        if bas <= v < haut:
            return i
    return len(classes) - 1


def _echelle(couleurs):
    n = len(couleurs)
    sc = []
    for i, c in enumerate(couleurs):
        sc += [[i / n, c], [(i + 1) / n, c]]
    return sc


def _fenetre(codes=None, marge=0.05):
    xs, ys = [], []
    for ft in GEO["features"]:
        if codes is not None and ft["properties"]["code"] not in codes:
            continue
        x0, y0, x1, y1 = ft["bbox"]
        xs += [x0, x1]
        ys += [y0, y1]
    return [min(xs) - marge, max(xs) + marge], [min(ys) - marge, max(ys) + marge]


def _layout_geo(fig, titre_encart: str, hauteur: int = 540):
    """Deux panneaux dans la même figure : le pays, et l'agrandissement de la région Maritime et du Grand Lomé."""
    base = dict(visible=False, bgcolor="#ffffff", projection=dict(type="mercator"))
    lon_t, lat_t = _fenetre()
    lon_s, lat_s = _fenetre(set(SUD), marge=0.03)
    fig.update_layout(
        geo=dict(**base, domain=dict(x=[0, 0.46], y=[0, 1]), lonaxis=dict(range=lon_t), lataxis=dict(range=lat_t)),
        geo2=dict(**base, domain=dict(x=[0.48, 1], y=[0.02, 0.80]), lonaxis=dict(range=lon_s),
                  lataxis=dict(range=lat_s)),
        height=hauteur, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="#ffffff",
        font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE),
        hoverlabel=dict(bgcolor="#ffffff"), separators=", ", showlegend=False,
        annotations=[dict(x=0.48, y=0.90, xref="paper", yref="paper", xanchor="left", showarrow=False,
                          text=f"<b>{titre_encart}</b>", font=dict(size=12, color=ENCRE), align="left")])


def _chips(couleurs, libelles, effectifs, suffixe_html=""):
    chips = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
        f'<span style="width:13px;height:13px;border-radius:3px;background:{couleurs[i]};'
        f'border:1px solid #d8d6cc"></span>{html.escape(lib)} <b>({effectifs[i]})</b></span>'
        for i, lib in enumerate(libelles))
    return f'<div class="filtres-actifs">{chips}{suffixe_html}</div>'


@st.cache_data(show_spinner=False)
def _centroides() -> dict:
    """Un point intérieur par préfecture, pour écrire son nom sur l'agrandissement."""
    return {ft["properties"]["code"]: shape(ft["geometry"]).representative_point().coords[0]
            for ft in GEO["features"]}


@st.cache_data(show_spinner=False)
def _sites_lonlat():
    """Les 48 sites indicatifs, convertis de l'UTM 31N au lon/lat pour l'affichage (transformation d'affichage)."""
    t = Transformer.from_crs(32631, 4326, always_xy=True)
    lon, lat = zip(*[t.transform(x, y) for x, y in zip(sites["x_utm"], sites["y_utm"])])
    return list(lon), list(lat)


ariane("Horizon 2031")
entete("Horizon 2031", "Combien en faudra-t-il d'ici 2031 ?",
       "Sans ouverture, le manque d'auto-écoles passe de <strong>41 en 2022 à 50 en 2031</strong> dans les préfectures "
       "qui en manquent, et <strong>4,6 millions de ruraux</strong> resteront à plus de 2 km d'une route revêtue.")

label = st.select_slider("Horizon", list(PALIERS), value="2029 · dans 3 ans", key="hz_palier")
palier = PALIERS[label]
an = ANNEE[palier]
st.caption("Les leviers restent à leur dernière observation : auto-écoles de 2021-2022, état du réseau relevé en 2020. "
           "Seule la population avance.")


def pays(levier, perimetre, pal=None):
    s = hz[(hz.Maille == "Pays") & (hz.Levier == levier) & (hz["Périmètre"] == perimetre)
           & (hz.Palier == (pal or palier))]
    return s.iloc[0] if len(s) else None


def national(mesure, serie, pal=None):
    s = nat[(nat.Mesure == mesure) & (nat["Série"] == serie) & (nat.Palier == (pal or palier))]
    return s.iloc[0] if len(s) else None


# ------------------------------------------------------------------ Section 1 — 4 chiffres clés
hab = pays("Accès rural", "Toutes les préfectures")
ae = pays("Auto-écoles", "Levier du 08")
km = pays("Remise en état", "Levier du 08")
rur = hab


def fourchette(row):
    if row is not None and row["Borne basse"] != row["Borne haute"]:
        return f"{fr(row['Borne basse'])} à {fr(row['Borne haute'])} selon la répartition de la population"
    return ""


rangee_kpi(f"L'horizon {an} — niveau C", [
    carte_kpi("Habitants", fr(hab["Population"]) if hab is not None else "—", f"population du Togo en {an}",
              "Population projetée par l'INSEED.", etiquette="C"),
    carte_kpi("Auto-écoles à ouvrir", fr(ae["Valeur"]) if ae is not None else "—",
              "dans les préfectures sans auto-école agréée", fourchette(ae), etiquette="C", ton="alerte"),
    carte_kpi("Km à remettre en état", fr(km["Valeur"], 1) if km is not None else "—",
              "dans les préfectures au réseau dégradé", "Ne change pas d'un horizon à l'autre.", etiquette="C",
              ton="alerte"),
    carte_kpi("Ruraux loin d'une route", fr(rur["Valeur"]) if rur is not None else "—",
              "à plus de 2 km d'une route nationale revêtue", fourchette(rur), etiquette="C", ton="alerte"),
])

# ------------------------------------------------------------------ Section 2 — Ce qu'il faut ajouter
st.markdown("")
g, d = st.columns([1.8, 1], vertical_alignment="top")
with g:
    titre_bloc("Ce qu'il faut ajouter", f"À l'horizon {an}, préfecture par préfecture.")
    levier_vue = st.radio("Levier", ["Auto-écoles à ouvrir", "Km à remettre en état"], horizontal=True,
                          label_visibility="collapsed", key="hz_levier")
    auto = levier_vue.startswith("Auto")
    lev = "Auto-écoles" if auto else "Remise en état"
    classes = CL_AE if auto else CL_KM
    dec = 0 if auto else 1
    unite = "auto-écoles à ouvrir" if auto else "km à remettre en état"

    pp = hz[(hz.Maille == "Préfecture") & (hz.Levier == lev) & (hz.Palier == palier)
            & (hz["Périmètre"] != "Levier du 10")]
    valeurs = dict(zip(pp["Territoire"], pp["Valeur"]))
    if not auto:
        valeurs["Mô"] = float("nan")          # aucune route classée : ni état, ni km évalué
    cl = {p: _classe(v, classes) for p, v in valeurs.items()}
    dedans = [p for p in valeurs if cl[p] is not None]
    absents = [p for p in valeurs if cl[p] is None]

    textes = {p: (f"<b>{p}</b><br>{ZONE_PREF.get(p, '')}<br>"
                  + (f"{fr(valeurs[p], dec)} {unite}" if cl[p] is not None else "aucune route classée"))
              for p in valeurs}

    fig = go.Figure()
    for cible in ("geo", "geo2"):
        comm = dict(geojson=GEO, featureidkey="properties.code", marker_line_color="#ffffff",
                    marker_line_width=0.8, showscale=False, geo=cible)
        if absents:
            fig.add_choropleth(locations=absents, z=[0] * len(absents), colorscale=[[0, ABSENT], [1, ABSENT]],
                               zmin=0, zmax=1, text=[textes[p] for p in absents],
                               hovertemplate="%{text}<extra></extra>", **comm)
        fig.add_choropleth(locations=dedans, z=[cl[p] + 0.5 for p in dedans], zmin=0, zmax=len(BLEUS),
                           colorscale=_echelle(BLEUS), text=[textes[p] for p in dedans],
                           hovertemplate="%{text}<extra></extra>", **comm)
    cen = _centroides()
    fig.add_scattergeo(geo="geo2", mode="text", text=SUD, hoverinfo="skip",
                       lon=[cen[p][0] for p in SUD], lat=[cen[p][1] for p in SUD],
                       textfont=dict(size=10, color="#141413"))
    _layout_geo(fig, "Région Maritime et Grand Lomé, agrandi")
    st.plotly_chart(fig, key="hz_carte", config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False,
                                                 "modeBarButtonsToRemove": ["select2d", "lasso2d"]})
    eff = [sum(1 for p in dedans if cl[p] == i) for i in range(len(classes))]
    suffixe = (f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:.74rem">'
               f'<span style="width:13px;height:13px;border-radius:3px;background:{ABSENT};'
               f'border:1px solid #d8d6cc"></span>Mô : aucune route classée</span>' if absents else "")
    st.markdown(_chips(BLEUS, [lib for _, _, lib in classes], eff, suffixe), unsafe_allow_html=True)
    if not auto:
        note("Aucune donnée ne mesure l'usure du réseau : la quantité à remettre en état ne dépend pas de l'horizon.")

    # --- Tableau par zone ou par région
    maille = st.radio("Maille", ["Zones (6)", "Régions (5)"], horizontal=True, label_visibility="collapsed",
                      key="hz_maille")
    m = "Zone" if maille.startswith("Zones") else "Région"
    base = hz[(hz.Maille == m) & (hz.Palier == palier)]
    aez = base[(base.Levier == "Auto-écoles") & (base["Périmètre"] == "Levier du 08")].set_index("Territoire")
    kmz = base[(base.Levier == "Remise en état") & (base["Périmètre"] == "Levier du 08")].set_index("Territoire")
    rrz = base[(base.Levier == "Accès rural") & (base["Périmètre"] == "Toutes les préfectures")].set_index("Territoire")
    lignes = []
    for t in rrz.index:
        a = aez.loc[t] if t in aez.index else None
        k = kmz.loc[t] if t in kmz.index else None
        lignes.append({
            m: f'<b style="color:{COULEUR_ZONE.get(t, ENCRE)}">{html.escape(t)}</b>',
            "Habitants": fr(rrz.loc[t, "Population"]),
            "Auto-écoles à ouvrir": (badge(fr(a["Valeur"]), "#1baf7a") if a is not None and a["Valeur"] else "—"),
            "Fourchette": (f'{fr(a["Borne basse"])} à {fr(a["Borne haute"])}'
                           if a is not None and a["Borne basse"] != a["Borne haute"] else "—"),
            "Km à remettre en état": (badge(f'{fr(k["Valeur"], 1)} km', "#eb6834")
                                      if k is not None and k["Valeur"] else "—"),
            "Ruraux à plus de 2 km": fr(rrz.loc[t, "Valeur"]),
        })
    tot_ae, tot_km = pays("Auto-écoles", "Levier du 08"), pays("Remise en état", "Levier du 08")
    lignes.append({
        m: "<b>Togo</b>", "Habitants": fr(hab["Population"]) if hab is not None else "—",
        "Auto-écoles à ouvrir": badge(fr(tot_ae["Valeur"]), "#0d366b") if tot_ae is not None else "—",
        "Fourchette": (f'{fr(tot_ae["Borne basse"])} à {fr(tot_ae["Borne haute"])}' if tot_ae is not None else "—"),
        "Km à remettre en état": badge(f'{fr(tot_km["Valeur"], 1)} km', "#0d366b") if tot_km is not None else "—",
        "Ruraux à plus de 2 km": fr(rur["Valeur"]) if rur is not None else "—"})
    st.markdown(table_html(lignes), unsafe_allow_html=True)
    exp = rrz.reset_index()[["Territoire", "Population", "Valeur"]].rename(
        columns={"Territoire": m, "Population": "Habitants", "Valeur": "Ruraux à plus de 2 km"})
    exp["Auto-écoles à ouvrir"] = exp[m].map(aez["Valeur"])
    exp["Km à remettre en état"] = exp[m].map(kmz["Valeur"])
    export_csv(exp, f"horizon_{an}_{m.lower()}s.csv", "hz_exp_zone")
    st.caption("Les quantités des recommandations de zone sont déjà comptées dans les leviers : elles ne "
               "s'additionnent pas.")

    # --- Tableau par recommandation
    with st.expander("Les recommandations chiffrées, à cet horizon"):
        rec = hz[(hz.Maille == "Recommandation") & (hz.Mesure != "aucune quantité")]
        lignes = []
        for ident, sub in rec.groupby("Recommandation"):
            base_id = str(ident).split(" (")[0]
            if base_id not in cartes10.index:
                continue
            passe = sub[sub.Palier == "Passé"]
            ici = sub[sub.Palier == palier]
            if passe.empty or ici.empty:
                continue
            p0, p1 = passe.iloc[0], ici.iloc[0]
            d0 = 1 if "km" in str(p1["Mesure"]) else 0
            lignes.append({
                "Recommandation": f'<span style="font-size:.8rem">{html.escape(str(cartes10.loc[base_id, "Titre"]))}</span>',
                "Quantité": html.escape(str(p1["Mesure"])),
                "En 2022": fr(p0["Valeur"], d0),
                f"En {an}": f'<b>{fr(p1["Valeur"], d0)}</b>',
                "Horizon porté": f'{int(p1["Horizon (ans)"])} ans',
            })
        st.markdown(table_html(sorted(lignes, key=lambda x: x["Recommandation"])), unsafe_allow_html=True)
        st.caption("Les quantités des recommandations de zone sont déjà comptées dans les leviers : elles ne "
                   "s'additionnent pas. Le détail de chaque action est en page Recommandations.")
        choix = st.selectbox("Ouvrir une recommandation", ["—"] + [str(cartes10.loc[i, "Titre"])
                                                                   for i in cartes10.index], key="hz_choix_rec")
        if choix != "—" and st.button("Voir cette recommandation →", key="hz_lien_rec"):
            onglet = cartes10[cartes10["Titre"] == choix].iloc[0]["Onglet"]
            st.session_state["recommandations_rang"] = RANG_ONGLET.get(onglet, 0)
            st.switch_page("views/recommandations.py")
with d:
    constat("Les <strong>41 auto-écoles</strong> qui manquaient en 2022 seront <strong>50 en 2031</strong> : la "
            "population grandit plus vite que l'offre. Les km à remettre en état, eux, ne bougent pas : c'est un retard "
            "déjà constitué.")
    st.caption("Classes fixes d'un horizon à l'autre, pour que les couleurs se comparent. Projection Mercator, cadrée "
               "sur le Togo ; l'agrandissement reprend la région Maritime et le Grand Lomé.")

# ------------------------------------------------------------------ Section 3 — Sans action, le taux baisse
st.markdown("")
titre_bloc("Sans action, le taux baisse", "Toutes les années ; l'horizon choisi est marqué.")
g, d = st.columns(2, vertical_alignment="top")
with g:
    st.caption("Auto-écoles agréées pour 100 000 habitants, par zone, si rien n'ouvre")
    fig = go.Figure()
    finals = []
    for z in ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]:
        s = hz[(hz.Maille == "Zone") & (hz.Levier == "Auto-écoles") & (hz["Périmètre"] == "Toutes les préfectures")
               & (hz.Territoire == z)].copy()
        s["an"] = s["Palier"].map(ANNEE)
        s = s.sort_values("an")
        fig.add_trace(go.Scatter(x=s["an"], y=s["Sans action"], name=z, mode="lines",
                                 line=dict(color=COULEUR_ZONE.get(z, "#1c5cab"), width=2),
                                 hovertemplate=f"{z} — %{{y:.2f}} pour 100 000 (%{{x}})<extra></extra>"))
        finals.append((z, s["Sans action"].iloc[0], s["Sans action"].iloc[-1]))
    fig.add_hline(y=CIBLE_AE, line=dict(color="#55534e", width=1.2, dash="dash"),
                  annotation_text="cible 1,065", annotation_position="bottom left",
                  annotation_font=dict(size=9, color="#55534e"))
    fig.add_vline(x=an, line=dict(color="#55534e", width=1, dash="dot"))
    habiller(fig, 330, legend=dict(orientation="h", y=1.16, x=0, font=dict(size=9)),
             xaxis=dict(gridcolor="#efece4", range=[2021.5, 2031.5]))
    tracer(fig, "hz_sansaction")
    # Le Grand Lomé écrase les cinq autres zones : les valeurs sont écrites ici plutôt que sur les courbes.
    st.markdown('<div class="filtres-actifs" style="font-size:.74rem">2022 → 2031, sans ouverture : '
                + " · ".join(f'<span style="color:{COULEUR_ZONE.get(z, ENCRE)};font-weight:600">{html.escape(z)}</span> '
                             f'{fr(a, 2)} → <b>{fr(b, 2)}</b>' for z, a, b in finals) + "</div>",
                unsafe_allow_html=True)
with d:
    st.caption("Population par zone, 2022 → 2031 (fourchette des deux variantes en bande)")
    fig = go.Figure()
    for z in ["Grand Lomé", "Maritime hors Grand Lomé", "Plateaux", "Centrale", "Kara", "Savanes"]:
        s = popz[popz.Zone == z].groupby("Palier", as_index=False).agg(
            Population=("Population", "sum"), bb=("Borne basse", "sum"), bh=("Borne haute", "sum"))
        s["an"] = s["Palier"].map(ANNEE)
        s = s.sort_values("an")
        coul = COULEUR_ZONE.get(z, "#1c5cab")
        fig.add_trace(go.Scatter(x=list(s["an"]) + list(s["an"])[::-1],
                                 y=list(s["bh"]) + list(s["bb"])[::-1], fill="toself", mode="lines",
                                 line=dict(width=0), fillcolor=coul, opacity=0.14, hoverinfo="skip",
                                 showlegend=False))
        fig.add_trace(go.Scatter(x=s["an"], y=s["Population"], name=z, mode="lines", line=dict(color=coul, width=2),
                                 hovertemplate=f"{z} — %{{y:, .0f}} habitants (%{{x}})<extra></extra>"))
    fig.add_vline(x=an, line=dict(color="#55534e", width=1, dash="dot"))
    habiller(fig, 330, legend=dict(orientation="h", y=1.16, x=0, font=dict(size=9)),
             xaxis=dict(gridcolor="#efece4"))
    tracer(fig, "hz_pop")
note("Aucune zone n'atteint la cible aujourd'hui en dehors du Grand Lomé, et l'écart se creuse partout : le taux "
     "national passe de 1,63 à 1,35 auto-école pour 100 000 habitants.")
with st.expander("Note de méthode : comment la population avance"):
    st.markdown("La population de chaque préfecture suit la croissance de sa région entre les recensements de 2010 "
                "et de 2022, ramenée au total des projections nationales. L'autre variante garde les parts de 2022 : "
                "les deux donnent la fourchette (niveau C).")

# ------------------------------------------------------------------ Section 4 — Sécurité routière
st.markdown("")
titre_bloc("Sécurité routière : ce que la cible demande",
           "Au niveau national seulement : les accidents ne sont publiés que pour tout le pays, cette section n'a "
           "pas de carte.")
g, d = st.columns([1.35, 1], vertical_alignment="top")
with g:
    MESURES = [("Accidents constatés", "#2a78d6"), ("Blessés", "#eda100"), ("Tués", "#e34948")]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                        subplot_titles=[m for m, _ in MESURES])
    deja: set[str] = set()
    for i, (mesure, coul) in enumerate(MESURES, start=1):
        s = nat[nat.Mesure == mesure]
        obs = s[s["Série"].str.startswith("observ")].sort_values("Année")
        fig.add_trace(go.Scatter(x=obs["Année"], y=obs["Valeur"], mode="lines", line=dict(color=coul, width=2.4),
                                 name="observé", showlegend=(i == 1),
                                 hovertemplate="%{x} — %{y:, .0f}<extra></extra>"), row=i, col=1)
        for serie, dash, c in [("Taux inchangé", "dot", "#8a8780"), ("Tendance", "dash", coul),
                               ("Cible de la Décennie", "dashdot", "#1baf7a")]:
            p = s[s["Série"] == serie].sort_values("Année")
            if p.empty:
                continue
            montrer = serie not in deja                 # la cible n'existe pas sur le 1er panneau : légende au 2e
            deja.add(serie)
            fig.add_trace(go.Scatter(x=p["Année"], y=p["Valeur"], mode="lines", line=dict(color=c, width=1.6,
                                     dash=dash), name=serie, showlegend=montrer,
                                     hovertemplate=f"{serie} — %{{x}} : %{{y:, .0f}}<extra></extra>"), row=i, col=1)
        # La période projetée, en grisé : tout ce qui est à droite de la dernière observation.
        fig.add_vrect(x0=DEBUT_PROJECTION, x1=2031.5, fillcolor="#e2dfd6", opacity=0.45, line_width=0,
                      layer="below", row=i, col=1)
        fig.add_vline(x=an, line=dict(color="#55534e", width=1, dash="dot"), row=i, col=1)
    fig.add_annotation(x=2028, y=1.045, xref="x", yref="paper", showarrow=False,
                       text="projeté · 2025-2031, sans action nouvelle",
                       font=dict(size=9, color="#55534e"))
    habiller(fig, 480, legend=dict(orientation="h", y=1.14, x=0, font=dict(size=9)),
             xaxis3=dict(gridcolor="#efece4"), yaxis=dict(gridcolor="#efece4"))
    fig.update_annotations(font_size=11)
    tracer(fig, "hz_series")
    note("Trait plein : observé jusqu'en 2024. Sur fond gris : les deux références sans action nouvelle (taux "
         "inchangé, tendance) et la cible de la Décennie, moitié de la valeur de 2021 en 2030. Les accidents "
         "constatés n'ont pas de cible : la résolution porte sur les tués et les blessés.")
with d:
    constat("Même si la baisse observée depuis 2010 se poursuit, il faudrait éviter <strong>204 tués</strong> de plus "
            "en 2029 pour suivre la cible. Généraliser le casque n'y suffirait pas : au mieux 147 à 174 tués évités.")
    st.caption("Tués : écart à la cible et plafond du casque, aux 4 horizons à venir")
    fig = go.Figure()
    annees = [ANNEE[p] for p in A_VENIR]
    SERIES = [("Écart à la cible (taux inchangé)", "#8a8780"), ("Écart à la cible (tendance)", "#e34948"),
              ("Plafond du casque (taux inchangé)", "#cde2fb"), ("Plafond du casque (tendance)", "#2a78d6")]
    for serie, coul in SERIES:
        s = nat[(nat.Mesure == "Tués") & (nat["Série"] == serie) & nat.Palier.isin(A_VENIR)].copy()
        s["an"] = s["Palier"].map(ANNEE)
        s = s.sort_values("an")
        err = None
        if s["Borne haute"].notna().any():
            err = dict(type="data", symmetric=False, array=list(s["Borne haute"] - s["Valeur"]),
                       arrayminus=list(s["Valeur"] - s["Borne basse"]), color="#55534e", thickness=1, width=2)
        fig.add_trace(go.Bar(x=s["an"], y=s["Valeur"], name=serie, marker_color=coul, error_y=err,
                             hovertemplate=f"{serie} — %{{x}} : %{{y:, .0f}} tués<extra></extra>"))
    fig.add_vline(x=an, line=dict(color="#55534e", width=1, dash="dot"))
    habiller(fig, 300, barmode="group", legend=dict(orientation="h", y=1.3, x=0, font=dict(size=8)),
             xaxis=dict(tickmode="array", tickvals=annees, gridcolor="rgba(0,0,0,0)"),
             yaxis=dict(title="tués", gridcolor="#efece4"))
    tracer(fig, "hz_ecart")
    st.caption("Le plafond suppose qu'aucun usager de deux-roues tué ne portait de casque : limite haute, pas une "
               "estimation. Rappel : 8,62 tués déclarés pour 100 000 habitants en 2021, contre 22,7 estimés par "
               "l'OMS — une baisse des déclarations ressemblerait à un progrès.")

# ------------------------------------------------------------------ Section 5 — Où ouvrir les auto-écoles
st.markdown("")
titre_bloc("Où ouvrir les auto-écoles",
           "Les 23 préfectures du levier formation ; sites choisis parmi les chefs-lieux et les points de canton.")
g, d = st.columns([1.6, 1], vertical_alignment="top")
with g:
    concernees = sorted(set(empl["Préfecture"]))
    autres = [p for p in ZONE_PREF if p not in concernees]
    aec = couche("auto_ecoles")
    agreees = aec[aec["Comptée (R-12)"]]
    lon_s, lat_s = _sites_lonlat()
    fig = go.Figure()
    for cible in ("geo", "geo2"):
        comm = dict(geojson=GEO, featureidkey="properties.code", marker_line_color="#ffffff",
                    marker_line_width=0.8, showscale=False, geo=cible)
        fig.add_choropleth(locations=autres, z=[0] * len(autres), colorscale=[[0, "#f4f2ec"], [1, "#f4f2ec"]],
                           zmin=0, zmax=1, hoverinfo="skip", **comm)
        fig.add_choropleth(locations=concernees, z=[0] * len(concernees),
                           colorscale=[[0, "#cde2fb"], [1, "#cde2fb"]], zmin=0, zmax=1,
                           text=[f"<b>{p}</b><br>préfecture du levier formation" for p in concernees],
                           hovertemplate="%{text}<extra></extra>", **comm)
        fig.add_scattergeo(geo=cible, lon=agreees.geometry.x, lat=agreees.geometry.y, mode="markers",
                           marker=dict(size=5, color="#8a8780", line=dict(width=0.5, color="#ffffff")),
                           text=agreees["Préfecture"], hovertemplate="Auto-école agréée — %{text}<extra></extra>")
        fig.add_scattergeo(geo=cible, lon=lon_s, lat=lat_s, mode="markers",
                           marker=dict(size=9, color="#0d366b", symbol="diamond",
                                       line=dict(width=1, color="#ffffff")),
                           customdata=[[s, t, p, h] for s, t, p, h in zip(sites["Site"], sites["Type"],
                                                                          sites["Préfecture"],
                                                                          sites["Habitants gagnés (2022)"])],
                           hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>%{customdata[2]}"
                                         "<br>%{customdata[3]:, .0f} habitants gagnés<extra></extra>")
    _layout_geo(fig, "Région Maritime et Grand Lomé, agrandi")
    st.plotly_chart(fig, key="hz_sites", config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False,
                                                 "modeBarButtonsToRemove": ["select2d", "lasso2d"]})
    st.markdown(
        f'<div class="filtres-actifs">'
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:.74rem">'
        f'<span style="width:13px;height:13px;border-radius:3px;background:#cde2fb;border:1px solid #d8d6cc"></span>'
        f'{len(concernees)} préfectures du levier formation</span>'
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:.74rem">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:#8a8780"></span>'
        f'{len(agreees)} auto-écoles agréées existantes</span>'
        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:.74rem">'
        f'<span style="width:11px;height:11px;background:#0d366b;transform:rotate(45deg)"></span>'
        f'{len(sites)} sites retenus</span></div>', unsafe_allow_html=True)
    note("Ces sites orientent une vérification sur place. Ce ne sont pas des adresses : ils sont choisis parmi les "
         "chefs-lieux et les points de canton, sur une grille de population modélisée (niveau C).")
with d:
    constat("Réparties, <strong>48 auto-écoles</strong> mettent 56,7 % de la population de ces préfectures à moins de "
            "10 km d'une auto-école, contre 32,2 % si elles ouvrent toutes au chef-lieu : 719 730 habitants de plus.")

e = empl.copy().sort_values("Population (2022)", ascending=False)
et = e[["Préfecture", "Zone", "Auto-écoles à ouvrir (2029)", "Couverte à 10 km, avant (%)",
        "Couverte, site indicatif du 10 (%)", "Couverte, sites optimisés (%)"]].rename(
    columns={"Auto-écoles à ouvrir (2029)": "À ouvrir (2029)", "Couverte à 10 km, avant (%)": "Avant (%)",
             "Couverte, site indicatif du 10 (%)": "Au chef-lieu (%)", "Couverte, sites optimisés (%)": "Répartis (%)"})
st.dataframe(et, hide_index=True, use_container_width=True, height=380)
if len(empl_total):
    t = empl_total.iloc[0]
    st.caption(f"Ensemble des 23 préfectures : {int(t['Auto-écoles à ouvrir (2029)'])} auto-écoles à ouvrir en 2029 ; "
               f"{fr(t['Couverte à 10 km, avant (%)'], 1)} % de leur population est aujourd'hui à moins de 10 km "
               f"d'une auto-école, {fr(t['Couverte, site indicatif du 10 (%)'], 1)} % si elles ouvrent toutes au "
               f"chef-lieu, {fr(t['Couverte, sites optimisés (%)'], 1)} % réparties.")
export_csv(et, "horizon_sites_prefecture.csv", "hz_exp_sites")

# ------------------------------------------------------------------ Section 6 — Synthèse et limite
st.markdown("")
permis = national("Permis A", "Permis A pour garder le taux")
ecart = national("Tués", "Écart à la cible (tendance)")
g, d = st.columns(2, vertical_alignment="top")
with g:
    synthese(fr(ae["Valeur"]) if ae is not None else "—", f"auto-écoles à ouvrir à l'horizon {an}",
             [f"Habitants : {fr(hab['Population']) if hab is not None else '—'}.",
              f"Km à remettre en état : {fr(km['Valeur'], 1) if km is not None else '—'} (ne change pas).",
              f"Ruraux à plus de 2 km : {fr(rur['Valeur']) if rur is not None else '—'}.",
              f"Permis moto à délivrer dans l'année : {fr(permis['Valeur']) if permis is not None else '—'}.",
              f"Tués à éviter pour suivre la cible : {fr(ecart['Valeur']) if ecart is not None else '—'} "
              f"(tendance observée)."])
with d:
    limite("Ces chiffres sont des estimations, pas des prévisions. Ils supposent la population projetée par l'INSEED "
           "et les leviers à leur dernière observation : auto-écoles de 2021-2022, état du réseau relevé en 2020. Ils "
           "ne chiffrent aucun coût, et ne prêtent aux actions aucun effet sur les accidents : les données ne "
           "permettent pas de le mesurer.")
pied()
