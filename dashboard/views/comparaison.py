"""Page 2 — Comparaison territoriale. Compare les territoires sur ce qui est mesuré par territoire : état du réseau,
offre de formation, desserte (design-page2.md). Maille zones / régions / préfectures. Aucun recalcul : les valeurs
viennent de regions_08, classement_08, prefectures_10, zones_10, signaux_06, hypotheses_09."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import html  # noqa: E402

import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from composants import (ariane, carte_kpi, constat, entete, export_csv, habiller, limite, note, pied,  # noqa: E402
                        rangee_kpi, synthese, titre_bloc, tracer)
from donnees import fr, lire  # noqa: E402
from theme import COULEUR_REGION, COULEUR_ZONE, ENCRE, ETAT  # noqa: E402

# Couleur de priorité, calée sur les valeurs réelles de la colonne (Haute / Moyenne / Aucune action).
PRIO_COUL = {"Haute": "#0d366b", "Moyenne": "#3987e5", "Aucune action": "#b9b6ad"}
# Un seuil franchi, une couleur (palette validée, 11 §4.1).
SEUIL_COUL = {"réseau": "#bb537d", "formation": "#4a3aa7", "desserte": "#eda100"}
# Lisibilité du texte inscrit dans une barre, selon la clarté de la couleur d'état.
PALIERS_KM = [(0, 10, "moins de 10 km", "#11613f"), (10, 20, "10 à 20 km", "#ab6300"),
              (20, 30, "20 à 30 km", "#cb4b0c"), (30, 40, "30 à 40 km", "#e34948"),
              (40, 50, "40 à 50 km", "#c0392b"), (50, 60, "50 à 60 km", "#a02622"),
              (60, 70, "60 à 70 km", "#80191a"), (70, 80, "70 à 80 km", "#5e1114"),
              (80, float("inf"), "80 km ou plus", "#3d0a0d")]
TEXTE_ETAT = {"Bon": "#ffffff", "Moyen": "#141413", "Mauvais": "#ffffff", "Travaux": "#ffffff",
              "Non évalué": "#141413"}


def _palier_km(v) -> int:
    """Palier de dix kilomètres d'une distance. Le premier palier est sous le seuil d'éloignement (10 km)."""
    for i, (bas, haut, _, _) in enumerate(PALIERS_KM):
        if bas <= v < haut:
            return i
    return len(PALIERS_KM) - 1


def _badge(texte: str, couleur: str) -> str:
    """Pastille colorée. Le texte passe en blanc sur un fond sombre, en encre sur un fond clair."""
    clair = couleur in ("#eda100", "#b9b6ad", "#cde2fb")
    return (f'<span style="display:inline-block;background:{couleur};'
            f'color:{"#141413" if clair else "#ffffff"};border-radius:999px;padding:1px 7px;'
            f'font-size:.69rem;font-weight:600;margin:1px 3px 1px 0;white-space:nowrap">'
            f'{html.escape(texte)}</span>')


def _valeur_forte(texte: str, alerte: bool) -> str:
    """Un chiffre mis en avant quand le territoire franchit le seuil."""
    return f'<b style="color:#e34948">{html.escape(texte)}</b>' if alerte else html.escape(texte)


def _table_html(lignes: list[dict]) -> str:
    """Tableau HTML : les cellules portent déjà leur mise en forme (badges, chiffres colorés)."""
    cols = list(lignes[0])
    entete = "".join(f'<th style="text-align:left;padding:6px 6px;border-bottom:2px solid #e2dfd6;'
                     f'font-size:.70rem;text-transform:uppercase;letter-spacing:.02em;color:#55534e;'
                     f'line-height:1.2">{html.escape(c)}</th>' for c in cols)
    corps = ""
    for ligne in lignes:
        cellules = "".join(f'<td style="padding:6px 6px;border-bottom:1px solid #efece4;font-size:.82rem;'
                           f'vertical-align:middle">{ligne[c]}</td>' for c in cols)
        corps += f"<tr>{cellules}</tr>"
    return (f'<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;background:#fff;'
            f'border:1px solid #e2dfd6;border-radius:10px">'
            f"<thead><tr>{entete}</tr></thead><tbody>{corps}</tbody></table></div>")

reg = lire("08_priorisation", "regions_08")
cla = lire("08_priorisation", "classement_08")
pref10 = lire("10_recommandations", "prefectures_10")
zones10 = lire("10_recommandations", "zones_10")
sig = lire("06_exploration", "signaux_06").set_index("ID")
hyp = lire("09_diagnostic", "hypotheses_09").set_index("Code")

f_zones = st.session_state.get("f_zones", [])
f_prio = st.session_state.get("f_priorites", [])


def _resume(code: str) -> str:
    """Texte d'un signal, à partir du deuxième deux-points (le code et la règle ne s'affichent pas, 11 §4.2)."""
    txt = str(sig.loc[code, "Résumé"])
    parts = txt.split(" : ", 2)
    return parts[2] if len(parts) >= 3 else (parts[-1] if parts else txt)


ariane("Comparaison territoriale")
entete("Comparaison territoriale", "Quels territoires sont les moins bien équipés ?",
       "La <strong>Centrale</strong> est la seule zone — et la seule région — qui cumule un réseau dégradé "
       "(<strong>40,3 %</strong> de routes en mauvais état) et un déficit de formation. <strong>23 préfectures "
       "sur 39</strong> n'ont aucune auto-école agréée ; <strong>13</strong> ont un réseau dégradé.")

# ------------------------------------------------------------------ Section 1 — Maille
titre_bloc("Choisir la maille", "Les objectifs 3 et 4 demandent ces mesures par région et par préfecture.")
maille = st.radio("Maille", ["Zones (6)", "Régions (5)", "Préfectures (39)"], horizontal=True,
                  label_visibility="collapsed", key="cmp_maille")

# ------------------------------------------------------------------ Section 2 — 3 chiffres clés (nationaux)
rangee_kpi("Trois territoires à surveiller (chiffres nationaux)", [
    carte_kpi("Préfectures au réseau dégradé", "13", "plus de 22,13 % de routes en mauvais état",
              "2 868 523 habitants concernés.", etiquette="C", ton="alerte"),
    carte_kpi("Préfectures sans auto-école agréée", "23 sur 39", "aucune auto-école agréée",
              "2 932 492 habitants ; 15 n'en ont aucune, même non agréée (1 822 046 hab.).", etiquette="B", ton="alerte"),
    carte_kpi("Préfectures loin d'une auto-école", "26 sur 39", "chef-lieu à plus de 10 km de la plus proche agréée",
              "3 482 856 habitants. Distance depuis le chef-lieu (un point central pour 9 préfectures).",
              etiquette="C", ton="alerte"),
])

# ------------------------------------------------------------------ Section 3 — Réseau et formation (nuage)
st.markdown("")
gauche, droite = st.columns([1.7, 1], vertical_alignment="top")
with gauche:
    titre_bloc("Réseau et formation", "Part de routes en mauvais état (horizontal) × auto-écoles agréées "
               "pour 100 000 habitants (vertical). Taille : population.")
    if maille.startswith("Préfectures"):
        d = cla.copy()
        d = d[d["O3-02"].notna()]  # Mô (aucune route classée) : part non définie, non placée
        if f_zones:
            d = d[d["Zone"].isin(f_zones)]
        if f_prio:
            # la priorité vient du 10 ; jointure par préfecture
            prio = pref10.set_index("Préfecture")["Priorité"]
            d = d[d["Préfecture"].map(prio).isin(f_prio)]
        seuil = st.slider("Seuil — part de routes en mauvais état (%)", 0.0, 100.0, 22.13, 0.5, key="cmp_seuil")
        fig = go.Figure()
        prio = pref10.set_index("Préfecture")["Priorité"]
        for p, coul in PRIO_COUL.items():
            s = d[d["Préfecture"].map(prio) == p]
            fig.add_trace(go.Scatter(
                x=s["O3-02"], y=s["O4-05"], mode="markers", name=p,
                marker=dict(size=(s["Population"] / 9000).clip(6, 42), color=coul, line=dict(width=0.6, color="#ffffff"),
                            opacity=0.85),
                text=s["Préfecture"], customdata=s["Population"],
                hovertemplate="<b>%{text}</b><br>Mauvais état : %{x:.1f} %<br>Auto-écoles /100 000 : %{y:.2f}"
                              "<br>Population : %{customdata:,.0f}<extra></extra>"))
        habiller(fig, 440, xaxis=dict(title="Part en mauvais état (%)", gridcolor="#efece4"),
                 yaxis=dict(title="Auto-écoles agréées / 100 000 hab.", gridcolor="#efece4"),
                 legend=dict(orientation="h", y=1.12, x=0), margin=dict(l=10, r=10, t=46, b=10))
        fig.add_vline(x=seuil, line_color="#e34948", line_width=2.2, line_dash="dash",
                      annotation_text=f"seuil : {fr(seuil, 2)} % de km en mauvais état",
                      annotation_position="top right",
                      annotation_font=dict(color="#e34948", size=11))
        tracer(fig, "cmp_nuage")
        au_dela = (d["O3-02"] > seuil).sum()
        pop_dela = int(d.loc[d["O3-02"] > seuil, "Population"].sum())
        note(f"Au seuil de {fr(seuil, 2)} %, {au_dela} préfecture(s) au-delà, {fr(pop_dela)} habitants. "
             "Mô (aucune route classée, part non définie) n'est pas placée.")
    else:
        est_zone = maille.startswith("Zones")
        d = reg[reg.Maille == ("Zone" if est_zone else "Région")].copy()
        if f_zones and est_zone:
            d = d[d["Territoire"].isin(f_zones)]
        fig = go.Figure()
        for _, r in d.iterrows():
            coul = COULEUR_ZONE.get(r["Territoire"], ENCRE)
            fig.add_trace(go.Scatter(
                x=[r["O3-02"]], y=[r["O4-05"]], mode="markers+text", name=r["Territoire"],
                marker=dict(size=(r["Population"] / 60000 + 10), color=coul, line=dict(width=0.8, color="#ffffff")),
                text=[r["Territoire"]], textposition="top center", textfont=dict(size=10),
                hovertemplate=f"<b>{r['Territoire']}</b><br>Mauvais état : {fr(r['O3-02'], 1)} %"
                              f"<br>Auto-écoles /100 000 : {fr(r['O4-05'], 2)}<extra></extra>"))
        habiller(fig, 440, xaxis=dict(title="Part en mauvais état (%)", gridcolor="#efece4"),
                 yaxis=dict(title="Auto-écoles agréées / 100 000 hab.", gridcolor="#efece4"), showlegend=False,
                 margin=dict(l=10, r=10, t=46, b=10))
        # Les seuils de cette maille sont les médianes du classement : tracées, puisque le curseur y est masqué.
        libelle_maille = "6 zones" if est_zone else "5 régions"
        med_res, med_for = d["O3-02"].median(), d["O4-05"].median()
        fig.add_vline(x=med_res, line_color="#e34948", line_width=2, line_dash="dash",
                      annotation_text=f"seuil réseau : médiane des {libelle_maille} ({fr(med_res, 1)} %)",
                      annotation_position="top right", annotation_font=dict(color="#e34948", size=11))
        fig.add_hline(y=med_for, line_color="#1baf7a", line_width=2, line_dash="dash",
                      annotation_text=f"seuil formation : médiane ({fr(med_for, 2)})",
                      annotation_position="top left", annotation_font=dict(color="#11613f", size=11))
        tracer(fig, "cmp_nuage_z")
        note(f"Le curseur est masqué dans cette maille : les seuils y sont les médianes des {libelle_maille}, "
             "tracées en pointillé. À droite de la ligne rouge, le réseau est dégradé ; sous la ligne verte, "
             "l'offre de formation est faible.")
with droite:
    constat("La <strong style='color:#4a3aa7'>Centrale</strong> est seule à franchir les seuils du réseau "
            "<em>et</em> de la formation : <strong>40,3 %</strong> de routes en mauvais état et "
            "<strong>0,50</strong> auto-école agréée pour 100 000 habitants.")
    st.caption("Niveau C : état relevé en 2020, activité des auto-écoles non publiée.")

# ------------------------------------------------------------------ Section 4 — Les territoires
st.markdown("")
if maille.startswith("Préfectures"):
    titre_bloc("Les territoires", "Tableau complet des 39 préfectures : voir plus bas.")
else:
    est_zone = maille.startswith("Zones")
    titre_bloc("Les territoires", "Zones (6)" if est_zone else "Régions (5)")
    d = reg[reg.Maille == ("Zone" if est_zone else "Région")].copy().sort_values("Rang")
    if f_zones and est_zone:
        d = d[d["Territoire"].isin(f_zones)]
    zmap = zones10.set_index("Zone")

    def _seuils(r):
        out = []
        if r["Réseau dégradé (au-dessus de la médiane)"] is True:
            out.append("réseau")
        if r["Formation faible (sous la médiane)"] is True:
            out.append("formation")
        if r["Desserte faible (sous la médiane)"] is True:
            out.append("desserte")
        return out

    def _levier_res(r):
        n, km = int(r["Préfectures au levier réseau"]), r["O5-04 km à remettre en état, préfectures au levier réseau"]
        return (n, km) if n else None

    def _levier_form(r):
        n = int(r["Préfectures au levier formation"])
        a = int(r["O5-04 auto-écoles manquantes (écart 21), préfectures au levier formation"])
        return (n, a) if n else None

    lignes, lignes_export = [], []
    for _, r in d.iterrows():
        t = r["Territoire"]
        seuils, lres, lform = _seuils(r), _levier_res(r), _levier_form(r)
        degrade = r["Réseau dégradé (au-dessus de la médiane)"] is True
        ligne = {"Territoire": f'<b>{html.escape(t)}</b>', "Rang": int(r["Rang"]),
                 "Population": fr(r["Population"]),
                 "Part en mauvais état": _valeur_forte(fr(r["O3-02"], 1) + " %", degrade),
                 "Auto-écoles /100 000": fr(r["O4-05"], 2), "Km /10 000 hab.": fr(r["O4-03"], 2)}
        exp = {"Territoire": t, "Rang": int(r["Rang"]), "Population": r["Population"],
               "Part en mauvais état (%)": r["O3-02"], "Auto-écoles /100 000": r["O4-05"],
               "Km /10 000 hab.": r["O4-03"]}
        if est_zone:
            km_km2 = zmap.loc[t, "Km de routes pour 1 000 km²"] if t in zmap.index else None
            ar = zmap.loc[t, "Accès rural à une route revêtue (%)"] if t in zmap.index else None
            ligne["Km /1 000 km²"] = fr(km_km2, 1) if km_km2 == km_km2 else "—"
            ligne["Accès rural"] = fr(ar, 1) + " %" if ar == ar else "<i>sans population rurale</i>"
            exp["Km /1 000 km²"] = km_km2
            exp["Accès rural (%)"] = ar
        ligne["Seuils franchis"] = ("".join(_badge(s, SEUIL_COUL[s]) for s in seuils)) if seuils else "—"
        ligne["Levier réseau"] = (_badge(f"{lres[0]} préf.", "#0d366b")
                                  + _badge(f"{fr(lres[1], 1)} km", "#eb6834")) if lres else "—"
        ligne["Levier formation"] = (_badge(f"{lform[0]} préf.", "#0d366b")
                                     + _badge(f"{lform[1]} auto-écoles", "#1baf7a")) if lform else "—"
        exp["Seuils franchis"] = ", ".join(seuils) if seuils else ""
        exp["Levier réseau"] = f"{lres[0]} préfectures, {fr(lres[1], 1)} km" if lres else ""
        exp["Levier formation"] = f"{lform[0]} préfectures, {lform[1]} auto-écoles" if lform else ""
        lignes.append(ligne)
        lignes_export.append(exp)
    st.markdown(_table_html(lignes), unsafe_allow_html=True)
    st.markdown(
        f'<div class="filtres-actifs" style="margin-top:8px"><b>Seuils franchis :</b> '
        f'{_badge("réseau", SEUIL_COUL["réseau"])} au-dessus de la médiane pour le mauvais état · '
        f'{_badge("formation", SEUIL_COUL["formation"])} sous la médiane pour les auto-écoles par habitant · '
        f'{_badge("desserte", SEUIL_COUL["desserte"])} sous la médiane pour les km de route par habitant</div>',
        unsafe_allow_html=True)
    tbl = pd.DataFrame(lignes_export)
    if not est_zone:
        st.caption("Les km pour 1 000 km² et l'accès rural ne sont calculés que par zone : absents ici, jamais additionnés.")
        constat("Avec le Grand Lomé, la région Maritime affiche <strong>3,06</strong> auto-écoles agréées pour "
                "100 000 habitants : ce chiffre cache celui de la Maritime hors Grand Lomé, <strong>0,37</strong>. "
                "La vue par zone est la lecture par défaut.")
    else:
        note("Les km de route par habitant baissent quand la densité monte : l'accès rural dit mieux qui est loin "
             "de la route.")
    export_csv(tbl, f"territoires_{'zones' if est_zone else 'regions'}.csv", "cmp_exp_terr")

# ------------------------------------------------------------------ Section 5 — État du réseau par zone
st.markdown("")
titre_bloc("État du réseau par zone", "Km par état, 6 zones. La part en mauvais état se calcule sur les km évalués.")
zz = zones10[zones10.Maille == "Zone"].copy()
if f_zones:
    zz = zz[zz["Zone"].isin(f_zones)]
zz = zz.sort_values("Part en mauvais état (%)", ascending=False)
etats = [("Km en bon état", "Bon"), ("Km en état moyen", "Moyen"), ("Km en mauvais état", "Mauvais"),
         ("Km en travaux", "Travaux"), ("Km non évalués", "Non évalué")]
degrade_zone = reg[reg.Maille == "Zone"].set_index("Territoire")["Réseau dégradé (au-dessus de la médiane)"]
fig = go.Figure()
for col, lib in etats:
    fig.add_trace(go.Bar(y=zz["Zone"], x=zz[col], name=lib, orientation="h", marker_color=ETAT[lib],
                         text=[fr(v, 0) for v in zz[col]], textposition="inside", insidetextanchor="middle",
                         textfont=dict(color=TEXTE_ETAT[lib], size=11), constraintext="inside", cliponaxis=False,
                         hovertemplate="%{y} — " + lib + " : %{x:.1f} km<extra></extra>"))
habiller(fig, 360, barmode="stack", xaxis=dict(title="Km", gridcolor="#efece4"),
         yaxis=dict(gridcolor="rgba(0,0,0,0)"), legend=dict(orientation="h", y=1.1, x=0, traceorder="normal"),
         margin=dict(l=10, r=76, t=10, b=10), uniformtext=dict(mode="hide", minsize=9))
# La part en mauvais état, au bout de la barre : en rouge pour les zones au-dessus de la médiane du classement.
totaux = zz[[c for c, _ in etats]].sum(axis=1)
for zone, total, part in zip(zz["Zone"], totaux, zz["Part en mauvais état (%)"]):
    alerte = degrade_zone.get(zone) is True
    fig.add_annotation(x=total, y=zone, text=f"<b>{fr(part, 1)} %</b>", showarrow=False, xanchor="left", xshift=9,
                       font=dict(color="#e34948" if alerte else ENCRE, size=12))
tracer(fig, "cmp_etat")
note("Les km sont inscrits dans chaque segment ; la part en mauvais état se lit au bout de la barre, en rouge pour "
     "les zones au-dessus de la médiane. Centrale : 40,3 %, la part la plus forte. Détail par tronçon en page Carte.")
if not maille.startswith("Zones"):
    st.caption("Ce bloc reste en 6 zones : l'état par type de route n'est calculé que par zone, jamais additionné.")

# ------------------------------------------------------------------ Section 6 — Où sont les auto-écoles
st.markdown("")
g, d = st.columns([1, 1.4], vertical_alignment="top")
with g:
    titre_bloc("Où sont les auto-écoles", "Concentration urbaine")
    conc = hyp.loc["H8", "Valeur"]
    st.markdown(f'<div class="synthese-chiffre" style="font-size:2.6rem">×{fr(conc, 2)}</div>'
                '<div class="synthese-legende">les 4 préfectures urbaines (Agoè-Nyivé, Golfe, Kloto, Kozah) '
                'ont 84,8 % des auto-écoles agréées pour 32,3 % de la population</div>', unsafe_allow_html=True)
    st.caption("Niveau B — calculé sur les auto-écoles agréées et la population de 2022.")
with d:
    titre_bloc("Distance à l'auto-école agréée la plus proche", "Une barre par préfecture, triée par distance.")
    dd = pref10[["Préfecture", "Formation — distance à la plus proche (km)", "Formation — auto-écoles comptées", "Zone"]].copy()
    dd = dd.rename(columns={"Formation — distance à la plus proche (km)": "dist", "Formation — auto-écoles comptées": "ae"})
    if f_zones:
        dd = dd[dd["Zone"].isin(f_zones)]
    dd = dd.sort_values("dist", ascending=True)
    coul = ["#1c5cab" if a == 0 else "#cde2fb" for a in dd["ae"]]
    # Le chiffre est écrit au bout de la barre, et prend la couleur de son palier de dix kilomètres.
    dd["palier"] = [_palier_km(v) for v in dd["dist"]]
    coul_txt = [PALIERS_KM[i][3] for i in dd["palier"]]
    fig = go.Figure(go.Bar(x=dd["dist"], y=dd["Préfecture"], orientation="h", marker_color=coul,
                           text=[fr(v, 1) + " km" for v in dd["dist"]], textposition="outside",
                           textfont=dict(color=coul_txt, size=10), cliponaxis=False,
                           hovertemplate="%{y} : %{x:.1f} km<extra></extra>"))
    habiller(fig, max(380, 17 * len(dd)),
             xaxis=dict(title="Distance (km)", gridcolor="#efece4", range=[0, dd["dist"].max() * 1.18]),
             yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed", tickfont=dict(size=10)),
             showlegend=False, margin=dict(l=10, r=20, t=34, b=10))
    fig.add_vline(x=10, line_color="#e34948", line_width=1.6, line_dash="dash",
                  annotation_text="seuil d'éloignement : 10 km", annotation_position="top right",
                  annotation_font=dict(color="#e34948", size=11))
    tracer(fig, "cmp_dist")
    presents = dd["palier"].value_counts()
    chips = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;font-size:.74rem">'
        f'<span style="width:11px;height:11px;border-radius:3px;background:{PALIERS_KM[i][3]}"></span>'
        f'{PALIERS_KM[i][2]} <b>({int(presents[i])})</b></span>'
        for i in sorted(presents.index))
    st.markdown(f'<div class="filtres-actifs"><b>Distance, par palier de dix kilomètres :</b><br>{chips}</div>',
                unsafe_allow_html=True)
    note("Le nombre laisse les 23 préfectures sans auto-école agréée toutes à zéro ; la distance les distingue : "
         "de 11,0 km (Agou) à 84,0 km (Oti-Sud). Ligne rouge : seuil de 10 km. Barre bleu foncé : aucune auto-école "
         "agréée. Le chiffre, au bout de la barre, prend la couleur de son palier de dix kilomètres.")
    export_csv(dd.rename(columns={"dist": "distance_km", "ae": "auto_ecoles_comptees"}),
               "distance_auto_ecoles.csv", "cmp_exp_dist")

# ------------------------------------------------------------------ Section 7 — Les 39 préfectures
st.markdown("")
titre_bloc("Les 39 préfectures", "Tableau triable. Cliquez sur l'en-tête d'une colonne pour trier.")
cla_ae = cla.set_index("Préfecture")["O4-05"]
non_eval = cla.set_index("Préfecture")["O3-06"]   # part du réseau national non évaluée (%)
p = pref10.copy()
if f_zones:
    p = p[p["Zone"].isin(f_zones)]
if f_prio:
    p = p[p["Priorité"].isin(f_prio)]
tab = p[["Préfecture", "Zone", "Région", "Population", "Réseau — part en mauvais état (%)", "Réseau — km évalués",
         "Formation — auto-écoles comptées", "Formation — auto-écoles recensées",
         "Formation — distance à la plus proche (km)", "Desserte (km pour 10 000 hab.)",
         "Accès rural à une route revêtue (%)", "Priorité"]].copy()
tab["Auto-écoles /100 000"] = tab["Préfecture"].map(cla_ae).round(2)
tab["Réseau non évalué (%)"] = tab["Préfecture"].map(non_eval).round(1)
tab = tab.rename(columns={"Réseau — part en mauvais état (%)": "Mauvais état (%)", "Réseau — km évalués": "Km évalués",
                          "Formation — auto-écoles comptées": "Auto-écoles agréées",
                          "Formation — auto-écoles recensées": "Auto-écoles recensées",
                          "Formation — distance à la plus proche (km)": "Distance (km)",
                          "Desserte (km pour 10 000 hab.)": "Km /10 000 hab.",
                          "Accès rural à une route revêtue (%)": "Accès rural (%)"})


SEUIL_PREF = 22.13  # seuil du classement : part de km en mauvais état


def _c_prio(v):
    coul = PRIO_COUL.get(v)
    if not coul:
        return ""
    return f"background-color:{coul};color:{'#141413' if v == 'Aucune action' else '#ffffff'};font-weight:600"


def _c_region(v):
    return f"color:{COULEUR_REGION.get(v, ENCRE)};font-weight:600"


def _c_zone(v):
    return f"color:{COULEUR_ZONE.get(v, ENCRE)};font-weight:600"


def _c_mauvais(v):
    if v != v:
        return "color:#8a8780;font-style:italic"
    if v >= SEUIL_PREF:
        return "color:#e34948;font-weight:700"
    return "color:#55534e"


def _f(d=1, vide="—"):
    """Formateur français : espace pour les milliers, virgule décimale, mention explicite si la valeur manque."""
    return lambda v: vide if v != v else fr(v, d)


FORMATS = {"Population": _f(0), "Mauvais état (%)": _f(1, "non définie"), "Km évalués": _f(1),
           "Auto-écoles agréées": _f(0), "Auto-écoles recensées": _f(0), "Distance (km)": _f(1),
           "Km /10 000 hab.": _f(2), "Accès rural (%)": _f(1, "sans ruraux"), "Auto-écoles /100 000": _f(2),
           "Réseau non évalué (%)": _f(1)}
style = (tab.style
         .format(FORMATS)
         .map(_c_prio, subset=["Priorité"])
         .map(_c_region, subset=["Région"])
         .map(_c_zone, subset=["Zone"])
         .map(_c_mauvais, subset=["Mauvais état (%)"]))
st.dataframe(style, hide_index=True, use_container_width=True, height=440)
st.markdown(
    f'<div class="filtres-actifs"><b>Priorité :</b> {_badge("Haute", PRIO_COUL["Haute"])}'
    f'{_badge("Moyenne", PRIO_COUL["Moyenne"])}{_badge("Aucune action", PRIO_COUL["Aucune action"])}'
    f' &nbsp;·&nbsp; <b style="color:#e34948">En rouge</b> : les préfectures au-dessus du seuil de '
    f'{fr(SEUIL_PREF, 2)} % de km en mauvais état. Le nom de la zone et de la région prend sa couleur de carte.</div>',
    unsafe_allow_html=True)
st.caption("Mô : part en mauvais état non définie (aucune route classée). Golfe et Agoè-Nyivé : sans population rurale. "
           "Une valeur nulle mesurée s'écrit 0 (23 préfectures à 0 auto-école agréée).")
export_csv(tab, "prefectures_comparaison.csv", "cmp_exp_pref")

# ------------------------------------------------------------------ Section 8 — Points d'attention
st.markdown("")
titre_bloc("Points d'attention", "Repères de l'exploration. Ils ne sont pas des seuils de décision et ne changent "
           "pas le classement.")
points = [
    ("Une seule auto-école agréée : si elle ferme, la préfecture n'en a plus", "SIG-43"),
    ("La plus peuplée des préfectures sans auto-école agréée", "SIG-31"),
    ("Peu de routes et peu d'auto-écoles par habitant", "SIG-30"),
    ("Un seul tronçon relevé, ou aucune route classée", "SIG-44"),
    ("Plus de ménages avec une moto que la médiane, avec moins d'auto-écoles", "SIG-35"),
]
cols = st.columns(len(points))
for col, (titre, code) in zip(cols, points):
    with col:
        st.markdown(f'<div class="constat" style="height:100%"><div class="constat-titre">{titre}</div>'
                    f'<div class="constat-texte">{_resume(code)}</div></div>', unsafe_allow_html=True)
st.caption("Niveau C. Dernier point : d'après une seule enquête auprès des ménages (2021-2022) ; l'ordre des zones "
           "change d'une enquête à l'autre.")

# ------------------------------------------------------------------ Section 9 — Synthèse et limite
st.markdown("")
g, d = st.columns([1, 1], vertical_alignment="top")
with g:
    synthese("13 + 23", "préfectures au réseau dégradé · sans auto-école agréée",
             ["13 au réseau dégradé (2 868 523 habitants).",
              "23 sans auto-école agréée (2 932 492 habitants).",
              "26 à plus de 10 km d'une auto-école agréée (3 482 856 habitants).",
              "5 cumulent réseau dégradé et aucune auto-école agréée (641 955 habitants)."])
with d:
    limite("État du réseau relevé en 2020 (niveau C) ; activité des auto-écoles non publiée ; accès rural estimé avec "
           "une population répartie uniformément dans chaque préfecture. La vue par région fond la Maritime hors Grand "
           "Lomé dans le Grand Lomé : la vue par zone est la lecture par défaut.")
pied()
