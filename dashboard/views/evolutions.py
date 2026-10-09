"""Page 3 — Évolutions et constats. Quatre onglets : Synthèse (les 17 vérifications), Mobilité, Sécurité routière,
Réseau (design-page3.md). Aucun recalcul : indicateurs_07, taux_09, hypotheses_09, consequences_11, D4_etat_troncons,
D4_etat_national_pct. Les onglets ouvrent sur le rang passé par la page 1 (st.session_state['evolutions_rang'])."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from composants import (ariane, carte_kpi, constat, entete, export_csv, fenetre_geo, habiller, limite, note,  # noqa: E402
                        onglets, pied, rangee_kpi, synthese, titre_bloc, tracer)
from donnees import contours, couche, fr, lire, lire_processed  # noqa: E402
from theme import BLEUS, ENCRE, THEME  # noqa: E402

ind = lire("07_indicateurs", "indicateurs_07")
NAT = ind[ind.Maille == "National"]
hyp = lire("09_diagnostic", "hypotheses_09")
taux = lire("09_diagnostic", "taux_09")
cons = lire("11_tableau_de_bord", "consequences_11").set_index("Code")
tron = lire_processed("D4_etat_troncons")
ann = lire_processed("D4_etat_national_pct")

# Thème de chaque vérification ou hypothèse (d'après le code, design-page3.md section 1).
THEME_CODE = {"S1": "Mobilité", "S2": "Mobilité", "H1": "Mobilité",
              "S3": "Sécurité routière", "S4": "Sécurité routière", "H2": "Sécurité routière", "H6": "Sécurité routière",
              "H7": "Sécurité routière", "H10": "Sécurité routière", "H11": "Sécurité routière", "H12": "Sécurité routière",
              "S5": "Réseau", "H3": "Réseau", "H5": "Réseau", "H4": "Formation", "H8": "Formation",
              "H9": "Réseau et formation"}
VERDICT_COUL = {"confirmée": "#1baf7a", "infirmée": "#e34948", "nuancée": "#eda100", "non testable": "#b9b6ad"}
# Badge clair : fond pastel, texte dans la teinte sombre de la même famille, pour rester lisible dans un tableau.
VERDICT_BADGE = {"confirmée": ("#e2f4ec", "#11613f"), "infirmée": ("#fde8e8", "#a02622"),
                 "nuancée": ("#fef3c7", "#8a5a00"), "non testable": ("#efece4", "#55534e")}


# Une couleur par type de mesure de sécurité routière : le rouge est réservé aux tués.
MESURE_COUL = {"Tués": "#e34948", "Blessés": "#eda100", "Accidents constatés": "#2a78d6"}
# Une couleur par type d'usager tué (2021), dans la palette catégorielle validée.
USAGER_COUL = {"Deux et trois-roues motorisés": "#e34948", "Piétons": "#2a78d6", "Véhicules à 4 roues": "#eb6834",
               "Cyclistes": "#1baf7a", "Autres et inconnus": "#8a8780"}

# Une couleur par catégorie de permis, la même que sur la figure de la page d'accueil (design-page1 §5).
PERMIS_COUL = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "E": "#1baf7a", "D": "#eda100", "F": "#8a8780"}
PERMIS_TRAIT = {"A": "solid", "B": "solid", "C": "solid", "E": "dash", "D": "solid", "F": "dot"}


def _badge_verdict(v):
    coul = VERDICT_BADGE.get(v)
    return f"background-color:{coul[0]};color:{coul[1]};font-weight:600" if coul else ""


@st.cache_data(show_spinner=False)
def _intitules() -> dict:
    """Code d'indicateur → intitulé en clair, lu dans le catalogue (11 §4.2)."""
    cat = lire("07_indicateurs", "catalogue_07")
    return dict(zip(cat["ID"], cat["Indicateur"]))


def nettoyer(txt: str) -> str:
    """Rend un texte de CSV affichable (11 §4.2) : chaque code d'indicateur est remplacé par son intitulé, et les
    renvois aux documents, aux seuils et aux signaux sont retirés. Aucun code ne doit rester à l'écran."""
    if txt != txt:
        return ""
    txt = str(txt)
    txt = re.sub(r"\[[^\]]*\]", "", txt)                                   # [SIG-01 à SIG-04]
    txt = re.sub(r"\((?:écart|PA-|SE-|SIG-|R-|0\d\s*§|O\d-|H\d)[^)]*\)", "", txt)   # (écart 21), (PA-03), (08 §3.1)
    txt = re.sub(r"\bO\d-(?:\d{2}|E\d)\b", lambda m: _intitules().get(m.group(0), ""), txt)
    txt = re.sub(r"\b(?:SE-\d+|SIG-\d+|PA-\d+|R-\d+)\b", "", txt)          # codes isolés restants
    txt = re.sub(r",\s*0\d\s*\)", ")", txt)                                # « …, année de rupture, 04) »
    txt = re.sub(r"\s*\(\s*0\d\s*\)", "", txt)                             # « (04) » seul
    txt = re.sub(r"\s{2,}", " ", txt).replace(" ,", ",").replace(" ;", " ;")
    txt = re.sub(r"^[\s:;,]+", "", txt)
    return txt.strip(" ;,")


def nom_troncon(nom: str) -> str:
    """Retire le code du relevé (« TGR… »), en gardant le numéro de route s'il y est collé (11 §4.2)."""
    m = re.match(r"^TGR\w*?(RN\d.*)$", nom)
    if m:
        return m.group(1)
    m = re.match(r"^TGR\w+\s+(.*)$", nom)
    return m.group(1) if m else nom


# --- Carte des constats : 5 classes fixes de la part de km en mauvais état de la zone (design-page3 §1) ---
CLASSES_MAUVAIS = [(0, 10, "moins de 10 %"), (10, 15, "10 à 15 %"), (15, 20, "15 à 20 %"),
                   (20, 30, "20 à 30 %"), (30, float("inf"), "30 % ou plus")]


def _echelle_discrete(couleurs):
    """Colorscale en bandes égales : z = indice de classe + 0,5, zmin 0, zmax n."""
    n = len(couleurs)
    sc = []
    for i, c in enumerate(couleurs):
        sc += [[i / n, c], [(i + 1) / n, c]]
    return sc


@st.cache_data(show_spinner=False)
def _table_carte():
    """Une ligne par préfecture : la part de km en mauvais état est celle de sa zone (seule maille où elle existe)."""
    pref = lire("10_recommandations", "prefectures_10")[["Préfecture", "Zone"]].rename(columns={"Préfecture": "code"})
    parts = lire("10_recommandations", "zones_10").set_index("Zone")["Part en mauvais état (%)"]
    pref["part_zone"] = pref["Zone"].map(parts)
    pref["classe"] = [next(i for i, (b, h, _) in enumerate(CLASSES_MAUVAIS) if b <= v < h) for v in pref["part_zone"]]
    return pref


@st.cache_data(show_spinner=False)
def _traces_mauvais():
    """Tracé des 49 tronçons qui ont des km en mauvais état, groupés par épaisseur (selon les km en mauvais état).

    Chaque tronçon relevé est rattaché au tracé par son nom : c'est une sélection, pas un calcul."""
    routes = couche("routes_classees")
    critiques = tron[tron["km_mauvais"] > 0]
    km_par_nom = {}
    for noms, km in zip(critiques["Noms du tracé"].fillna(""), critiques["km_mauvais"]):
        for nom in str(noms).split(" | "):
            if nom:
                km_par_nom[nom] = max(km_par_nom.get(nom, 0), km)
    maxi = max(km_par_nom.values()) if km_par_nom else 1
    groupes = {}
    for nom, km in km_par_nom.items():
        largeur = round(1.2 + 3.8 * (km / maxi), 1)        # de 1,2 à 5 px, comme le prévoit le plan
        groupes.setdefault(largeur, []).append(nom)
    sortie = {}
    for largeur, noms in groupes.items():
        sub = routes[routes["Nom"].isin(noms)]
        lon, lat = [], []
        for geom in sub.geometry:
            for line in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
                xs, ys = line.xy
                lon += list(xs) + [None]
                lat += list(ys) + [None]
        if lon:
            sortie[largeur] = (lon, lat)
    return sortie


def _encart(titre: str, chiffre: str, legende: str, verdict: str, couleur: str, serie, cle: str):
    """Un thème national : son verdict, son chiffre, et une courbe de rappel avec ses valeurs extrêmes."""
    st.markdown(f'<div style="font-size:.72rem;font-weight:700;color:{couleur};text-transform:uppercase;'
                f'letter-spacing:.03em;margin-top:6px">{titre} · {verdict}</div>'
                f'<div style="font-size:1.5rem;font-weight:700;color:#0d366b;line-height:1.1">{chiffre}</div>'
                f'<div style="font-size:.76rem;color:#55534e">{legende}</div>', unsafe_allow_html=True)
    f = go.Figure(go.Scatter(x=serie["x"], y=serie["y"], mode="lines", line=dict(color=couleur, width=2),
                             fill="tozeroy", fillcolor="rgba(42,120,214,0.10)"))
    for x, y, pos in [(serie["x"].iloc[0], serie["y"].iloc[0], "middle right"),
                      (serie["x"].iloc[-1], serie["y"].iloc[-1], "middle left")]:
        f.add_annotation(x=x, y=y, text=f"<b>{fr(y, 0 if y > 100 else 2)}</b>", showarrow=False,
                         font=dict(color=couleur, size=9), xanchor="left" if "right" in pos else "right")
    f.update_layout(height=92, margin=dict(l=2, r=2, t=2, b=2), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                    showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(f, key=cle, config={"displayModeBar": False, "staticPlot": True})


def valn(idc, annee=None, cat=None, mesure=None):
    s = NAT[NAT.ID == idc]
    if annee is not None:
        s = s[s["Année"].astype(str) == str(annee)]
    if cat is not None:
        s = s[s["Catégorie"] == cat]
    if mesure is not None:
        s = s[s["Mesure"] == mesure]
    return float(s.iloc[0]["Valeur"])


def _serie(idc, cat=None, debut=None):
    """Une série annuelle nationale, prête pour une courbe de rappel."""
    s = NAT[NAT.ID == idc].copy()
    if cat is not None:
        s = s[s["Catégorie"] == cat]
    s = s[s["Année"].astype(str).str.fullmatch(r"\d{4}")]
    s["Année"] = s["Année"].astype(int)
    if debut:
        s = s[s["Année"] >= debut]
    s = s.sort_values("Année")
    return {"x": s["Année"].reset_index(drop=True), "y": s["Valeur"].reset_index(drop=True)}


CARTE = _table_carte()
GEO_PREF = contours("prefectures")
AE = couche("auto_ecoles")
AE_AGREEES = AE[AE["Comptée (R-12)"]]
SERIE_IMMAT = _serie("O1-01", "Ensemble")
SERIE_TUES = _serie("O2-02", debut=2010)

ariane("Évolutions et constats")
entete("Évolutions et constats", "Qu'est-ce qui change, et que confirment les données ?",
       "Les immatriculations ont été multipliées par <strong>4,56</strong> en 20 ans, portées par les motos ; les "
       "accidents déclarés augmentent, mais les <strong>6 taux</strong> baissent ; <strong>49 tronçons</strong> sur 84 "
       "concentrent le mauvais état du réseau.")

ong = onglets("evolutions", ["Synthèse", "Mobilité", "Sécurité routière", "Réseau"])

# ============================================================ Onglet 0 — Synthèse
with ong[0]:
    n_conf = (hyp.Verdict == "confirmée").sum()
    n_inf = (hyp.Verdict == "infirmée").sum()
    n_nua = (hyp.Verdict == "nuancée").sum()
    n_nt = (hyp.Verdict == "non testable").sum()
    rangee_kpi("Les 17 vérifications et hypothèses du cadrage", [
        carte_kpi("Confirmées", str(n_conf), "sur 17 vérifications et hypothèses",
                  "L'énoncé du défi est largement vérifié.", etiquette="A", ton="ok"),
        carte_kpi("Infirmées ou nuancées", f"{n_inf + n_nua}", f"{n_inf} infirmées, {n_nua} nuancée",
                  "« Les accidents augmentent » est nuancé : volume en hausse, taux en baisse.", etiquette="A"),
        carte_kpi("Non testables", str(n_nt), "faute de données par territoire, par mois ou par âge",
                  "7 questions restent ouvertes : voir la page Méthodologie.", etiquette="C", ton="alerte"),
    ])
    constat("L'énoncé est vérifié, sauf « les accidents augmentent », qui est <strong>nuancé</strong> : les accidents "
            "déclarés montent, mais les six taux de risque baissent sur la période.")

    # ---------------------------------------------------------- Carte des constats + encart national
    st.markdown("")
    g_carte, d_carte = st.columns([1.5, 1], vertical_alignment="top")
    with g_carte:
        titre_bloc("La carte des constats", "Ce que les données confirment, vu sur le Togo. Chaque couche illustre "
                   "un verdict ; seul ce qui est mesuré par territoire est cartographié.")
        fig = go.Figure()
        fig.add_choropleth(
            geojson=GEO_PREF, featureidkey="properties.code", locations=list(CARTE["code"]),
            z=[c + 0.5 for c in CARTE["classe"]], zmin=0, zmax=len(BLEUS), colorscale=_echelle_discrete(BLEUS),
            showscale=False, marker_line_color="#ffffff", marker_line_width=0.8,
            customdata=[[z, fr(p, 1)] for z, p in zip(CARTE["Zone"], CARTE["part_zone"])],
            hovertemplate="<b>%{location}</b><br>Zone : %{customdata[0]}"
                          "<br>Km en mauvais état de la zone : %{customdata[1]} %<extra></extra>")
        for largeur, (lon, lat) in _traces_mauvais().items():
            fig.add_scattergeo(lon=lon, lat=lat, mode="lines", name="Tronçons en mauvais état",
                               line=dict(width=largeur, color="#e34948"), hoverinfo="skip", showlegend=False)
        fig.add_scattergeo(lon=AE_AGREEES.geometry.x, lat=AE_AGREEES.geometry.y, mode="markers",
                           name="Auto-écoles agréées", marker=dict(size=5, color="#ffffff",
                                                                   line=dict(width=0.8, color="#141413")),
                           text=AE_AGREEES["Préfecture"], hovertemplate="Auto-école agréée — %{text}<extra></extra>",
                           showlegend=False)
        fenetre_geo(fig, GEO_PREF)
        fig.update_layout(height=620, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#ffffff",
                          font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=ENCRE),
                          hoverlabel=dict(bgcolor="#ffffff"), separators=", ")
        st.plotly_chart(fig, key="ev_carte_constats",
                        config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False,
                                "modeBarButtonsToRemove": ["select2d", "lasso2d"]})
        eff = CARTE["classe"].value_counts()
        chips = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
            f'<span style="width:13px;height:13px;border-radius:3px;background:{BLEUS[i]};'
            f'border:1px solid #d8d6cc"></span>{lib} <b>({int(eff.get(i, 0))})</b></span>'
            for i, (_, _, lib) in enumerate(CLASSES_MAUVAIS))
        st.markdown(
            f'<div class="filtres-actifs"><b>Km en mauvais état de la zone</b> (préfectures) :<br>{chips}<br>'
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;font-size:.74rem">'
            f'<span style="width:16px;height:0;border-top:3px solid #e34948"></span>49 tronçons en mauvais état '
            f'(épaisseur selon les km)</span>'
            f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:.74rem">'
            f'<span style="width:11px;height:11px;border-radius:50%;background:#fff;border:1.5px solid #141413">'
            f'</span>132 auto-écoles agréées</span></div>', unsafe_allow_html=True)
        if st.button("Voir la carte détaillée →", key="ev_lien_carte"):
            st.switch_page("views/carte.py")
    with d_carte:
        st.markdown('<div class="filtres-actifs"><b>Le réseau est inégalement entretenu : confirmée</b><br>'
                    '32,6 points d\'écart entre la Centrale (40,3 %) et le Grand Lomé (7,7 %).</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="filtres-actifs"><b>Les auto-écoles sont concentrées dans les grandes villes : '
                    'confirmée</b><br>84,8 % des auto-écoles agréées dans les 4 préfectures urbaines.</div>',
                    unsafe_allow_html=True)
        titre_bloc("Ce qui n'a pas de territoire", "Publié pour tout le pays seulement.")
        _encart("Mobilité", "×4,56", "immatriculations de 2002 à 2022", "confirmée", THEME["Mobilité"],
                SERIE_IMMAT, "ev_spark_immat")
        _encart("Sécurité routière", "−29,4 %", "tués pour 100 000 habitants, 2010–2012 face à 2022–2024",
                "nuancée", THEME["Sécurité routière"], SERIE_TUES, "ev_spark_tues")
        st.markdown('<div class="filtres-actifs"><b>Accidents par territoire</b> — <i>non testable</i><br>'
                    'Non publiés : 7 questions restent sans réponse.</div>', unsafe_allow_html=True)
        st.caption("Les immatriculations, les permis et les accidents ne sont publiés que pour tout le pays : ils ne "
                   "se cartographient pas. Aucun curseur des années sur la carte : les données par territoire n'ont "
                   "qu'une date (réseau 2020, auto-écoles 2021-2022, population 2022).")

    f_verdict = st.multiselect("Filtrer par verdict", list(VERDICT_COUL), key="ev_verdict")
    titre_bloc("Les 17 vérifications et hypothèses", "Énoncé, verdict, et ce que montrent les données.")
    vue = hyp.copy()
    vue["Thème"] = vue["Code"].map(THEME_CODE)
    if f_verdict:
        vue = vue[vue.Verdict.isin(f_verdict)]
    lignes = []
    for _, r in vue.iterrows():
        montre = r["Raison"] if r["Verdict"] == "non testable" else r["Mesure"]
        lignes.append({"Thème": r["Thème"], "Énoncé": r["Énoncé"], "Verdict": r["Verdict"],
                       "Ce que montrent les données": nettoyer(montre), "Niveau": r["Niveau"]})
    tbl = pd.DataFrame(lignes)
    st.dataframe(tbl.style.map(_badge_verdict, subset=["Verdict"]), hide_index=True, use_container_width=True,
                 height=560)
    st.markdown('<div class="filtres-actifs"><b>Verdict :</b> '
                + "".join(f'<span style="display:inline-block;background:{c};color:{t};border-radius:999px;'
                          f'padding:1px 9px;font-size:.72rem;font-weight:600;margin-right:6px">{v}</span>'
                          for v, (c, t) in VERDICT_BADGE.items()) + '</div>', unsafe_allow_html=True)
    note(f"Bilan : {n_conf} confirmées, {n_inf} infirmées, {n_nua} nuancée, {n_nt} non testables.")
    export_csv(tbl, "verifications_17.csv", "ev_exp_verif")

    titre_bloc("Ce que chaque verdict change pour l'action", "La conséquence retenue par le diagnostic.",
               marge=True)
    chg = []
    for code in ["S1", "S2", "S3", "S4", "S5", "H1", "H2", "H5", "H6", "H8"]:
        if code in cons.index:
            chg.append({"Énoncé": cons.loc[code, "Énoncé"], "Verdict": cons.loc[code, "Verdict"],
                        "Ce qui change pour l'action": nettoyer(cons.loc[code, "Conséquence affichée"])})
    chg.append({"Énoncé": "Les 7 questions non testables", "Verdict": "non testable",
                "Ce qui change pour l'action": "Aucune recommandation ne s'y appuie. La donnée qui les rendrait "
                "testables est en page Méthodologie."})
    st.dataframe(pd.DataFrame(chg), hide_index=True, use_container_width=True)
    limite("7 questions restent non testables faute d'accidents par préfecture, par mois et par âge des conducteurs. "
           "Les tués sont ceux que déclarent la police et la gendarmerie.")

# ============================================================ Onglet 1 — Mobilité
with ong[1]:
    immat24 = valn("O1-01", 2024, "Ensemble")
    motos24 = valn("O1-01", 2024, "Moto")
    rangee_kpi("Mobilité — ce qui change", [
        carte_kpi("Immatriculations sur 20 ans", "×4,56", "de 2002 à 2022",
                  "×1,83 en 2024, depuis 2004 (année de rupture de série).", etiquette="B"),
        carte_kpi("Croissance annuelle moyenne", "7,8 %", "par an, 1990–2024",
                  "Motos : 11,7 % par an ; voitures : 4,2 %.", etiquette="B"),
        carte_kpi("Part des motos", "74,4 %", "des immatriculations de 2024",
                  "22,2 % en 1990.", etiquette="B", ton="ok"),
    ])
    g, d = st.columns([1.7, 1], vertical_alignment="top")
    with g:
        titre_bloc("Immatriculations par groupe, 1990–2024")
        mode = st.radio("Affichage", ["Volume", "Part (%)", "Pour 1 000 habitants"], horizontal=True,
                        label_visibility="collapsed", key="ev_immat_mode")
        COUL = {"Moto": "#2a78d6", "Voiture": "#eb6834", "Poids lourd": "#1baf7a", "Bus et car": "#eda100",
                "Autres": "#e87ba4"}
        if mode == "Volume":
            src, cats = NAT[NAT.ID == "O1-01"], list(COUL)
        elif mode == "Part (%)":
            src, cats = NAT[NAT.ID == "O1-02"], list(COUL)
        else:
            src, cats = NAT[NAT.ID == "O1-04"], ["Ensemble"]
        src = src[src["Année"].astype(str).str.fullmatch(r"\d{4}")].copy()
        src["Année"] = src["Année"].astype(int)
        fig = go.Figure()
        if mode == "Part (%)":
            for cat in cats:
                s = src[src["Catégorie"] == cat].sort_values("Année")
                fig.add_trace(go.Scatter(x=s["Année"], y=s["Valeur"], name=cat, mode="lines", stackgroup="un",
                                         line=dict(color=COUL[cat], width=0.5)))
        else:
            for cat in cats:
                s = src[src["Catégorie"] == cat].sort_values("Année")
                coul = COUL.get(cat, "#1c5cab")
                fig.add_trace(go.Scatter(x=s["Année"], y=s["Valeur"], name=cat, mode="lines",
                                         line=dict(color=coul, width=2)))
        habiller(fig, 400, legend=dict(orientation="h", y=1.14, x=0), margin=dict(l=10, r=10, t=48, b=10))
        # Les ruptures de série portent leur année en haut de la ligne, à l'intérieur du tracé (sous la légende).
        for an in [1995, 2004]:
            fig.add_vline(x=an, line_color="#8a8780", line_width=1.2, line_dash="dot",
                          annotation_text=f"<b>{an}</b> · rupture de série", annotation_position="top left",
                          annotation_yshift=-8, annotation_font=dict(color="#55534e", size=10))
        tracer(fig, "ev_immat")
        note("Ruptures de série en 1995 et 2004 (pointillés). Volume : niveau A ; part : B ; pour 1 000 habitants : "
             "B en 2010 et 2022 (recensements), C les autres années.")
        export_csv(NAT[NAT.ID == "O1-01"][["Année", "Catégorie", "Valeur"]], "immatriculations_groupe.csv", "ev_exp_im")
    with d:
        constat("Les immatriculations ont été multipliées par <strong>4,56</strong> de 2002 à 2022, et les motos font "
                "<strong>80,6 %</strong> de la hausse. Les permis moto suivent de loin : 40 motos immatriculées pour "
                "un permis moto sur 2007–2024.")

    g, d = st.columns(2, vertical_alignment="top")
    with g:
        titre_bloc("Permis par catégorie, 2007–2024")
        pm = NAT[NAT.ID == "O1-06"].copy()
        pm = pm[pm["Année"].astype(str).str.fullmatch(r"\d{4}")]
        pm["Année"] = pm["Année"].astype(int)
        pm.loc[pm["Année"] == 2013, "Valeur"] = None
        fig = go.Figure()
        for cat in ["A", "B", "C", "D", "E", "F"]:
            s = pm[pm["Catégorie"] == cat].sort_values("Année")
            fig.add_trace(go.Scatter(x=s["Année"], y=s["Valeur"], name=f"Permis {cat}", mode="lines",
                                     line=dict(color=PERMIS_COUL[cat], width=2, dash=PERMIS_TRAIT[cat]),
                                     connectgaps=False))
        habiller(fig, 340, legend=dict(orientation="h", y=1.16, x=0, font=dict(size=10)),
                 margin=dict(l=10, r=10, t=52, b=10))
        # L'année non renseignée est marquée par une ligne qui porte sa date, à l'intérieur du tracé.
        fig.add_vline(x=2013, line_color="#8a8780", line_width=1.2, line_dash="dot",
                      annotation_text="<b>2013</b> · non renseignée", annotation_position="top left",
                      annotation_yshift=-8, annotation_font=dict(color="#55534e", size=10))
        tracer(fig, "ev_permis")
        note("2013 non renseignée : la courbe s'interrompt, elle ne passe pas par zéro. Niveau A.")
    with d:
        titre_bloc("Immatriculations pour un permis, cumul 2007–2024")
        ratio = NAT[(NAT.ID == "O1-09") & (NAT["Année"].astype(str) == "2007–2024")].copy()
        ratio = ratio.sort_values("Valeur")
        # Chaque barre reprend la couleur de sa catégorie sur la courbe des permis.
        coul_barres = [PERMIS_COUL.get(c, "#1c5cab") for c in ratio["Catégorie"]]
        fig = go.Figure(go.Bar(x=ratio["Valeur"], y="Permis " + ratio["Catégorie"], orientation="h",
                               marker_color=coul_barres, text=[fr(v, 2) for v in ratio["Valeur"]],
                               textposition="outside"))
        habiller(fig, 320, xaxis=dict(gridcolor="#efece4", range=[0, ratio["Valeur"].max() * 1.15]),
                 yaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False)
        tracer(fig, "ev_ratio")
        note("Sur 2007–2024, 40 motos immatriculées pour un permis moto délivré ; moins de 2,5 véhicules pour un "
             "permis dans les autres catégories. Niveau B. Le permis F n'a aucun véhicule correspondant.")

    titre_bloc("Parc estimé des véhicules, 2009–2024",
               "Valeur centrale et fourchette ; sert de dénominateur aux taux par véhicule.")
    parc = NAT[(NAT.ID == "O1-05") & (NAT["Catégorie"] == "Ensemble")].copy()
    parc = parc[parc["Année"].astype(str).str.fullmatch(r"\d{4}")]
    parc["Année"] = parc["Année"].astype(int)
    parc = parc.sort_values("Année")
    motos = NAT[(NAT.ID == "O1-05") & (NAT["Catégorie"] == "Moto")].copy()
    motos = motos[motos["Année"].astype(str).str.fullmatch(r"\d{4}")]
    motos["Année"] = motos["Année"].astype(int)
    motos = motos.sort_values("Année")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(parc["Année"]) + list(parc["Année"])[::-1],
                             y=list(parc["Borne haute"]) + list(parc["Borne basse"])[::-1], fill="toself",
                             fillcolor="rgba(42,120,214,0.15)", line=dict(width=0), name="Fourchette", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=parc["Année"], y=parc["Valeur"], mode="lines", line=dict(color="#2a78d6", width=2.4),
                             name="Parc estimé, tous véhicules",
                             hovertemplate="%{x} : %{y:,.0f} véhicules<extra></extra>"))
    if len(motos):
        fig.add_trace(go.Scatter(x=motos["Année"], y=motos["Valeur"], mode="lines",
                                 line=dict(color="#1c5cab", width=2, dash="dash"), name="dont motos",
                                 hovertemplate="%{x} : %{y:,.0f} motos<extra></extra>"))
    # Les chiffres sont écrits de cinq ans en cinq ans, et sur la dernière année : lisible sans survoler.
    paliers = [a for a in parc["Année"] if a % 5 == 0] + [int(parc["Année"].max())]
    for an in sorted(set(paliers)):
        v = parc.loc[parc["Année"] == an, "Valeur"]
        if len(v):
            fig.add_annotation(x=an, y=float(v.iloc[0]), text=f"<b>{fr(v.iloc[0])}</b>", showarrow=False, yshift=14,
                               font=dict(color="#2a78d6", size=10))
        m = motos.loc[motos["Année"] == an, "Valeur"] if len(motos) else []
        if len(m):
            fig.add_annotation(x=an, y=float(m.iloc[0]), text=fr(m.iloc[0]), showarrow=False, yshift=-14,
                               font=dict(color="#1c5cab", size=9))
    habiller(fig, 340, legend=dict(orientation="h", y=1.12, x=0), margin=dict(l=10, r=26, t=36, b=10))
    tracer(fig, "ev_parc")
    note("En 2024 : 751 398 véhicules (de 579 845 à 965 702), dont 449 226 motos. Le parc n'est pas publié : il est "
         "estimé à partir des immatriculations et d'une durée de vie par groupe (7 ans pour une moto). Niveau C.")
    limite("Immatriculations de l'année, pas parc en circulation. Ruptures de série en 1995 et 2004. Permis de 2013 "
           "non renseignés. Le parc est estimé (C), et les taux par habitant hors 2010 et 2022 reposent sur une "
           "population projetée.")

# ============================================================ Onglet 2 — Sécurité routière
with ong[2]:
    rangee_kpi("Sécurité routière — ce qui change", [
        carte_kpi("Tués pour 100 000 habitants", "−29,4 %", "10,45 en 2010–2012, 7,38 en 2022–2024",
                  "Le risque par habitant baisse.", etiquette="C", ton="ok"),
        carte_kpi("Accidents constatés par an", "+9,4 %", "6 381,7 puis 6 980,7",
                  "Le volume monte : plus de véhicules.", etiquette="A"),
        carte_kpi("Tués estimés par l'OMS", "×2,63", "le taux déclaré de 2021 : 22,7 contre 8,62 /100 000",
                  "L'estimation de l'OMS ne corrige pas les tués déclarés.", etiquette="C", ton="alerte"),
    ])
    g, d = st.columns([1.7, 1], vertical_alignment="top")
    with g:
        titre_bloc("Les 6 taux : 2010–2012 face à 2022–2024", "Les 3 taux du cadre, puis les 3 compléments à l'énoncé.")
        cadre = taux[taux.ID.isin(["O2-03", "O2-02", "O2-04"])].copy()        # accidents/100k, tués/100k, tués/10k véh
        compl = taux[taux.ID.isin(["O2-E2", "O2-E1", "O2-E3"])].copy()
        aff = pd.concat([cadre, compl])
        aff["lib"] = aff["Mesure"] + " — " + aff["Lecture"]
        # Une couleur par type de mesure : les tués en rouge, les blessés en ambre, les accidents en bleu.
        # La période se lit à l'opacité : la plus ancienne est pâle, la récente est pleine.
        fig = go.Figure()
        for periode, alpha in [("Moyenne 2010–2012", 0.42), ("Moyenne 2022–2024", 1.0)]:
            fig.add_trace(go.Bar(
                y=aff["lib"], x=aff[periode], name=periode.replace("Moyenne ", ""), orientation="h",
                marker=dict(color=[MESURE_COUL.get(m, "#1c5cab") for m in aff["Mesure"]], opacity=alpha),
                text=[fr(v, 2) for v in aff[periode]], textposition="outside", textfont=dict(size=9),
                hovertemplate="%{y}<br>" + periode.replace("Moyenne ", "") + " : %{x:,.2f}<extra></extra>"))
        # Pas de légende Plotly : la couleur porte deux informations (mesure et période), expliquées juste en dessous.
        habiller(fig, 440, barmode="group", showlegend=False,
                 xaxis=dict(gridcolor="#efece4", range=[0, aff[["Moyenne 2010–2012", "Moyenne 2022–2024"]].max().max() * 1.14]),
                 yaxis=dict(gridcolor="rgba(0,0,0,0)"), margin=dict(l=10, r=20, t=14, b=10))
        tracer(fig, "ev_6taux")
        st.markdown('<div class="filtres-actifs"><b>Couleur par mesure :</b> '
                    + "".join(f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;'
                              f'font-size:.74rem"><span style="width:12px;height:12px;border-radius:3px;'
                              f'background:{c}"></span>{m}</span>' for m, c in MESURE_COUL.items())
                    + ' &nbsp;·&nbsp; teinte pâle : 2010–2012 · teinte pleine : 2022–2024</div>',
                    unsafe_allow_html=True)
        note("Les 3 premiers sont les taux du cadre d'analyse. Les 3 derniers (accidents et blessés pour 10 000 "
             "véhicules, blessés pour 100 000 habitants) sont des compléments : hors cadre, aucun verdict. Volumes : "
             "niveau A ; les 6 taux : C.")
        export_csv(aff[["Mesure", "Lecture", "Moyenne 2010–2012", "Moyenne 2022–2024", "Variation (%)"]],
                   "six_taux.csv", "ev_exp_taux")
    with d:
        constat("<strong>Plus de véhicules, pas une route plus dangereuse</strong> : les accidents déclarés augmentent "
                "(+9,4 %), mais les six taux de risque baissent.")

    titre_bloc("Accidents, blessés et tués, année par année, 2010–2024")
    c1, c2, c3 = st.columns(3)
    for col, (cat, coul, lib) in zip([c1, c2, c3], [("Accidents constatés", "#eb6834", "Accidents constatés"),
                                                    ("Blessés", "#eda100", "Blessés"), ("Tués", "#e34948", "Tués")]):
        with col:
            s = NAT[(NAT.ID == "O2-01") & (NAT["Catégorie"] == cat)].copy()
            s = s[s["Année"].astype(str).str.fullmatch(r"\d{4}")]
            s["Année"] = s["Année"].astype(int)
            s = s.sort_values("Année")
            fig = go.Figure(go.Scatter(x=s["Année"], y=s["Valeur"], mode="lines+markers",
                                       line=dict(color=coul, width=2), marker=dict(size=4)))
            habiller(fig, 240, showlegend=False)
            fig.update_layout(title=dict(text=lib, font=dict(size=12), x=0.02, y=0.96))
            tracer(fig, f"ev_annuel_{cat}")
    note("D'une année à l'autre, les séries varient fortement avant 2017 : l'évolution se lit sur des moyennes de "
         "trois ans (bloc ci-dessus). Niveau A, déclaré par la police et la gendarmerie.")

    g, d = st.columns(2, vertical_alignment="top")
    with g:
        titre_bloc("Les tués par type d'usager, 2021")
        us = NAT[(NAT.ID == "O2-09") & (NAT["Année"].astype(str) == "2021")].copy().sort_values("Valeur")
        # Une couleur par catégorie d'usager ; les libellés de l'axe sont en gras.
        us["lib"] = ["<b>" + c + "</b>" for c in us["Catégorie"]]
        fig = go.Figure(go.Bar(x=us["Valeur"], y=us["lib"], orientation="h",
                               marker_color=[USAGER_COUL.get(c, "#1c5cab") for c in us["Catégorie"]],
                               text=[fr(v, 0) + " %" for v in us["Valeur"]], textposition="outside",
                               hovertemplate="%{y} : %{x:.0f} % des tués déclarés<extra></extra>"))
        habiller(fig, 300, xaxis=dict(gridcolor="#efece4", ticksuffix=" %", range=[0, 70]),
                 yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11)), showlegend=False,
                 margin=dict(l=10, r=30, t=10, b=10))
        tracer(fig, "ev_usagers")
        note("60 % des tués sont des usagers de deux et trois-roues motorisés, pour 54,7 % à 59,7 % de motos dans le "
             "parc estimé : un peu plus que leur part du parc. Niveau C : une seule année, ni sexe ni âge.")
    with d:
        titre_bloc("Tués déclarés et estimation de l'OMS, 2021")
        oms = pd.DataFrame({"Repère": ["Tués déclarés (police, gendarmerie)", "Estimation de l'OMS pour le Togo",
                                       "Moyenne estimée Bénin, Ghana, Burkina"], "Taux": [8.62, 22.7, 26.17]})
        fig = go.Figure(go.Bar(x=oms["Taux"], y=oms["Repère"], orientation="h",
                               marker_color=["#0d366b", "#eda100", "#b9b6ad"],
                               text=[fr(v, 2) for v in oms["Taux"]], textposition="outside"))
        habiller(fig, 300, xaxis=dict(gridcolor="#efece4"), yaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False)
        tracer(fig, "ev_oms")
        note("Pour 100 000 habitants, 2021. L'OMS estime le taux de tués à 2,63 fois le taux déclaré ; cette "
             "estimation ne corrige pas les chiffres déclarés. Niveau C.")
    limite("Accidents et victimes déclarés par la police et la gendarmerie, au niveau national seulement : ni "
           "préfecture, ni mois, ni âge. Aucune définition publiée du tué ; l'OMS en estime 2,63 fois plus. Les taux "
           "par véhicule reposent sur un parc estimé (C).")

# ============================================================ Onglet 3 — Réseau
with ong[3]:
    rangee_kpi("Réseau — ce qui change", [
        carte_kpi("Réseau évalué", "3 163", "km de routes nationales, relevé de 2020",
                  "84 tronçons relevés.", etiquette="C", unite=" km"),
        carte_kpi("En mauvais état", "21,2 %", "669,34 km",
                  "Part des km évalués.", etiquette="C", ton="alerte"),
        carte_kpi("Tronçons en mauvais état", "49 sur 84", "34 revêtus, 15 non revêtus",
                  "Le mauvais état se concentre sur ces tronçons.", etiquette="C", ton="alerte"),
    ])
    g, d = st.columns([1.8, 1], vertical_alignment="top")
    with g:
        titre_bloc("Les 84 tronçons relevés et leur état", "Vue par défaut : les 49 tronçons en mauvais état.")
        tous = st.toggle("Afficher les 84 tronçons", key="ev_tous_tron")
        t = tron.copy()
        t["Tronçon"] = t["Tronçon"].map(nom_troncon)
        if not tous:
            t = t[t["km_mauvais"] > 0]
        t = t.sort_values(["km_mauvais", "km_total"], ascending=False)
        aff = t[["Tronçon", "Type", "km_bon", "km_moyen", "km_mauvais", "km_travaux", "km_total", "Zones traversées"]]
        aff = aff.rename(columns={"km_bon": "Bon", "km_moyen": "Moyen", "km_mauvais": "Mauvais", "km_travaux": "Travaux",
                                  "km_total": "Km relevés"})
        st.dataframe(aff, hide_index=True, use_container_width=True, height=440)
        note("En km, relevé de 2020. Les 49 tronçons de la vue par défaut sont les tronçons critiques du 07 "
             "(669,34 km). FRE : frontière. Pour 7 tronçons, l'état est réparti le long de l'axe (niveau C).")
        export_csv(aff, "troncons_etat.csv", "ev_exp_tron")
    with d:
        constat("Le mauvais état se concentre sur <strong>49 des 84 tronçons</strong> : ceux qui traversent les "
                "Plateaux en portent le plus (292,15 km, 23 tronçons), puis ceux de la Centrale (236,25 km, "
                "6 tronçons).")

    g, d = st.columns(2, vertical_alignment="top")
    with g:
        titre_bloc("Tronçons en mauvais état par zone traversée")
        parz = pd.DataFrame({"Zone": ["Plateaux", "Centrale", "Kara", "Maritime hors Grand Lomé", "Savanes", "Grand Lomé"],
                             "Tronçons": [23, 6, 8, 11, 8, 4], "Km mauvais": [292.15, 236.25, 108.68, 88.24, 66.79, 21.55]})
        fig = go.Figure(go.Bar(x=parz["Km mauvais"], y=parz["Zone"], orientation="h", marker_color="#e34948",
                               text=[fr(v, 1) for v in parz["Km mauvais"]], textposition="outside",
                               customdata=parz["Tronçons"],
                               hovertemplate="%{y} : %{x:.1f} km, %{customdata} tronçons<extra></extra>"))
        habiller(fig, 320, xaxis=dict(gridcolor="#efece4"), yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed"),
                 showlegend=False)
        tracer(fig, "ev_tron_zone")
        note("Un tronçon qui traverse plusieurs zones compte dans chacune, pour tous ses km : les lignes ne "
             "s'additionnent pas. Pays : 49 tronçons, 669,34 km.")
    with d:
        titre_bloc("Un constat frappant sur l'état du réseau en 2020 : l'annuaire national",
                   "Deux publications de la même année ne concordent pas.")
        a = ann[ann["Catégorie de route"] == "Routes nationales revêtues et non revêtues"]
        a = a[a["État"] == "Mauvais"].sort_values("Année")
        fig = go.Figure(go.Bar(x=a["Année"].astype(str), y=a["Part (%)"], marker_color="#eda100",
                               text=[fr(v, 2) + " %" for v in a["Part (%)"]], textposition="outside"))
        habiller(fig, 320, yaxis=dict(gridcolor="#efece4", ticksuffix=" %"), showlegend=False)
        tracer(fig, "ev_annuaire")
        note("Pour 2020, l'annuaire national donne 29,75 % de routes nationales en mauvais état, le relevé des "
             "tronçons 21,2 % : les deux publications ne concordent pas. Le tableau de bord s'appuie sur le relevé, le "
             "seul à donner l'état par tronçon et par préfecture. Niveau C.")
    limite("État relevé en 2020, sur les routes nationales seulement, méthode de notation non publiée. L'annuaire "
           "national de la même année donne d'autres parts (29,75 % en mauvais état, contre 21,2 %). Les tronçons "
           "sont rattachés au tracé par leur nom ; pour 7 d'entre eux, l'état est réparti le long de l'axe.")

# ============================================================ Synthèse de la page
st.markdown("")
synthese("×4,56", "les immatriculations de 2022 face à celles de 2002",
         ["7 vérifications confirmées sur 17, 2 infirmées, 1 nuancée, 7 non testables (onglet Synthèse).",
          "74,4 % des immatriculations de 2024 sont des motos ; 40 motos pour un permis moto sur 2007–2024 (Mobilité).",
          "Tués pour 100 000 habitants : 10,45 puis 7,38, alors que les accidents déclarés montent de 9,4 % (Sécurité).",
          "49 tronçons sur 84 en mauvais état, 669,34 km, dont 292,15 km sur les Plateaux (Réseau)."])
pied()
