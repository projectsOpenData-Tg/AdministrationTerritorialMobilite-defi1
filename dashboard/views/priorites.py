"""Page 5 — Priorités. Par où commencer : zones en difficulté, 5 préfectures qui cumulent, 10 premières, 2 leviers,
robustesse, classement complet (design-page5.md).

Aucun recalcul (sauf le curseur de poids du réseau, exception admise par la maquette, 11 §4.4) : classement_08,
sensibilite_08, regions_08, zones_10, prefectures_10, cartes_10, phrases_11."""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from composants import (ariane, badge, constat, entete, export_csv, habiller, limite, note, pied,  # noqa: E402
                        synthese, table_html, titre_bloc, tracer)
from donnees import fr, lire  # noqa: E402
from theme import COULEUR_ZONE, ENCRE  # noqa: E402

cla = lire("08_priorisation", "classement_08")
sens = lire("08_priorisation", "sensibilite_08")
reg = lire("08_priorisation", "regions_08")
zones10 = lire("10_recommandations", "zones_10")
pref10 = lire("10_recommandations", "prefectures_10")
cartes = lire("10_recommandations", "cartes_10").set_index("ID")
phrases = lire("11_tableau_de_bord", "phrases_11")

f_zones = st.session_state.get("f_zones", [])
f_leviers = st.session_state.get("f_leviers", [])
f_prio = st.session_state.get("f_priorites", [])

# Couleur d'un levier, et couleur du déficit d'une zone (palette PRIORITE : deux déficits, un seul, aucun).
LEVIER_COUL = {"réseau": "#eb6834", "formation": "#1baf7a"}
DEFICIT_COUL = {"la route et la formation": "#0d366b", "la route": "#3987e5", "la formation": "#3987e5"}
RANG_RECO = {"toutes": 0, "réseau": 1, "formation": 2, "zones": 4}


def phrase(maille: str, territoire: str) -> str:
    """Phrase de diagnostic d'un territoire, déjà réécrite pour l'affichage (11 §4.2)."""
    s = phrases[(phrases.Maille == maille) & (phrases.Territoire == territoire)]
    return "" if s.empty else str(s.iloc[0]["Phrase affichée"])


def lien_reco(libelle: str, onglet: str, cle: str):
    """Bouton vers la page Recommandations, ouverte sur l'onglet voulu."""
    if st.button(libelle, key=cle):
        st.session_state["recommandations_rang"] = RANG_RECO[onglet]
        st.switch_page("views/recommandations.py")


def filtrer(df: pd.DataFrame, zone: str = "Zone") -> pd.DataFrame:
    """Filtres de la barre latérale : ils s'appliquent aux sections 2 à 6 (la section 1 montre toujours les 6 zones)."""
    if f_zones and zone in df:
        df = df[df[zone].isin(f_zones)]
    if f_leviers and "Leviers" in df:
        cible = [lv.lower() for lv in f_leviers]
        df = df[df["Leviers"].astype(str).apply(lambda s: any(c in s for c in cible))]
    return df


ariane("Priorités")
entete("Priorités", "Par où commencer ?",
       "Commencer par la <strong>Centrale</strong>, seule zone en retard sur la route et la formation, et par "
       "<strong>5 préfectures</strong> qui cumulent les deux déficits (641 955 habitants) ; aucun test de robustesse "
       "ne change plus de 2 des 10 premières.")

if f_zones or f_leviers:
    st.markdown('<div class="filtres-actifs"><b>Filtres actifs :</b> '
                + (f'zones — {", ".join(f_zones)}. ' if f_zones else "")
                + (f'leviers — {", ".join(f_leviers)}. ' if f_leviers else "")
                + 'Ils s\'appliquent aux sections suivantes ; les 6 zones restent toutes affichées.</div>',
                unsafe_allow_html=True)

# ------------------------------------------------------------------ Section 1 — Les zones en difficulté
g, d = st.columns([1.9, 1], vertical_alignment="top")
with g:
    titre_bloc("Les zones en difficulté",
               "Deux analyses désignent les mêmes 4 zones : le classement des zones et la desserte.")
    zz = zones10[zones10.Maille == "Zone"].set_index("Zone")
    rg = reg[reg.Maille == "Zone"].set_index("Territoire")
    ordre = rg.sort_values("Rang").index.tolist()
    lignes = []
    for z in ordre:
        desservie = zz.loc[z, "Moins bien desservie pour"] if z in zz.index else None
        desservie = "" if pd.isna(desservie) else str(desservie)
        nres = int(rg.loc[z, "Préfectures au levier réseau"])
        kmr = rg.loc[z, "O5-04 km à remettre en état, préfectures au levier réseau"]
        nfor = int(rg.loc[z, "Préfectures au levier formation"])
        afor = int(rg.loc[z, "O5-04 auto-écoles manquantes (écart 21), préfectures au levier formation"])
        ar = zz.loc[z, "Accès rural à une route revêtue (%)"] if z in zz.index else None
        rec = zz.loc[z, "Recommandation"] if z in zz.index else None
        titre_rec = "—" if pd.isna(rec) else html.escape(str(cartes.loc[rec, "Titre"]))
        lignes.append({
            "Zone": f'<b style="color:{COULEUR_ZONE.get(z, ENCRE)}">{html.escape(z)}</b>',
            "Rang": str(int(rg.loc[z, "Rang"])),
            "Moins bien desservie pour": (badge(desservie, DEFICIT_COUL[desservie]) if desservie
                                          else badge("aucun retard", "#b9b6ad")),
            "Accès rural": ((fr(ar, 1) + " %") if ar == ar else '<i style="color:#8a8780">sans ruraux</i>')
                           + (' <span style="color:#8a5a00;font-size:.72rem">cas limite</span>' if z == "Savanes"
                              else ""),
            "Auto-écoles /100 000": fr(rg.loc[z, "O4-05"], 2),
            "Levier réseau": (badge(f"{nres} préf.", "#0d366b") + badge(f"{fr(kmr, 1)} km", LEVIER_COUL["réseau"])
                              if nres else "—"),
            "Levier formation": (badge(f"{nfor} préf.", "#0d366b")
                                 + badge(f"{afor} auto-écoles", LEVIER_COUL["formation"]) if nfor else "—"),
            "Recommandation": f'<span style="font-size:.78rem">{titre_rec}</span>',
        })
    st.markdown(table_html(lignes), unsafe_allow_html=True)
    note("Une zone est moins bien desservie si elle est sous la médiane des zones : 16,9 % des ruraux à moins de 2 km "
         "d'une route revêtue pour la route, 0,53 auto-école pour 100 000 habitants pour la formation.")
    note("Les Savanes sont un cas limite pour la route : 16,9 %, pour 17,2 % dans le pays.")
    note("Mesuré avec une grille de population, l'accès rural change de lecture : les Savanes passent sous la médiane "
         "et la Centrale au-dessus. La Centrale garde la première place : elle reste la zone au réseau le plus "
         "dégradé, et sa formation ne change pas. Les deux mesures sont en page Méthodologie.")

    with st.expander("Ce que dit chaque zone"):
        for z in ordre:
            txt = phrase("Zone", z)
            if txt:
                st.markdown(f'<div style="margin-bottom:7px;font-size:.88rem">'
                            f'<b style="color:{COULEUR_ZONE.get(z, ENCRE)}">{html.escape(z)}</b> — '
                            f'{html.escape(txt)}</div>', unsafe_allow_html=True)
    st.caption("Par région : Centrale, puis Plateaux, Savanes, Kara et Maritime. La Centrale est en tête dans les "
               "deux lectures.")
    maritime = phrase("Région", "Maritime")
    if maritime:
        st.caption(maritime)
with d:
    constat("La <strong style='color:#4a3aa7'>Centrale</strong> est la seule zone en retard sur la route <em>et</em> la "
            "formation. Les Plateaux sont en retard sur la route ; les Savanes et la Maritime hors Grand Lomé, sur la "
            "formation.")
    lien_reco("Pourquoi ces zones → Recommandations", "zones", "pr_lien_reco")
    st.caption("La comparaison complète des zones, avec tous les indicateurs et leurs seuils, est en page Comparaison "
               "territoriale ; les deux mesures de l'accès rural sont en page Méthodologie.")

# ------------------------------------------------------------------ Section 2 — Les 5 qui cumulent
st.markdown("")
titre_bloc("Les 5 préfectures qui cumulent", "Réseau dégradé et aucune auto-école agréée.")
ORDRE_5 = ["Danyi", "Blitta", "Agou", "Tchamba", "Bassar"]
cinq = pref10[pref10["Préfecture"].isin(ORDRE_5)].copy()
cinq["ord"] = cinq["Préfecture"].map({p: i for i, p in enumerate(ORDRE_5)})
cinq = cinq.sort_values("ord")
cinq["Leviers"] = cinq["Préfecture"].map(cla.set_index("Préfecture")["Leviers"])
cinq = filtrer(cinq)
if cinq.empty:
    st.info("Aucune des 5 préfectures qui cumulent ne correspond aux filtres.")
else:
    st.markdown(table_html([{
        "Préfecture": f'<b>{html.escape(r["Préfecture"])}</b>',
        "Zone": f'<span style="color:{COULEUR_ZONE.get(r["Zone"], ENCRE)};font-weight:600">'
                f'{html.escape(r["Zone"])}</span>',
        "Population": fr(r["Population"]),
        "Part en mauvais état": f'<b style="color:#e34948">{fr(r["Réseau — part en mauvais état (%)"], 1)} %</b>',
        "Km à remettre en état": fr(r["Réseau — km à remettre en état"], 1),
        "Auto-écoles à ouvrir": str(int(r["Formation — auto-écoles à ouvrir"])),
    } for _, r in cinq.iterrows()]), unsafe_allow_html=True)
note("Total : 641 955 habitants ; 175,6 km à remettre en état ; 9 auto-écoles à ouvrir. Déjà repérées à "
     "l'exploration : ces 5 préfectures étaient dans le pire quart des deux dimensions.")
lien_reco("Remettre en état le réseau de ces 5 préfectures → Recommandations", "réseau", "pr_lien_cumul")

# ------------------------------------------------------------------ Section 3 — Les 10 premières
st.markdown("")
titre_bloc("Les 10 premières", "Score décomposé : la part du réseau et la part de la formation, et la robustesse.")
dix = filtrer(cla.sort_values("O5-02 rang").head(10).copy())
if dix.empty:
    st.info("Aucune des 10 premières ne correspond aux filtres.")
else:
    ordre_bas = dix.sort_values("O5-02 rang", ascending=False)
    scores = ordre_bas["Score"]            # le score publié est la somme des deux rangs percentiles (08 §4)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=ordre_bas["Préfecture"], x=ordre_bas["Rang percentile réseau"], name="Part réseau",
                         orientation="h", marker_color=LEVIER_COUL["réseau"],
                         hovertemplate="%{y} — part réseau : %{x:.2f}<extra></extra>"))
    fig.add_trace(go.Bar(y=ordre_bas["Préfecture"], x=ordre_bas["Rang percentile formation"],
                         name="Part formation", orientation="h", marker_color=LEVIER_COUL["formation"],
                         text=[f"  {fr(s, 2)}" for s in scores], textposition="outside",
                         textfont=dict(size=11, color="#3a3935"),
                         hovertemplate="%{y} — part formation : %{x:.2f}<extra></extra>"))
    # À droite de chaque barre, la robustesse : le nombre de tests où la préfecture reste dans les 10 premières.
    for y, t in zip(ordre_bas["Préfecture"], ordre_bas["Tests parmi les 10 premières (sur 6)"]):
        sur = int(t)
        fig.add_annotation(x=1.0, xref="paper", y=y, text=f"<b>{sur}</b>/6", showarrow=False, xanchor="right",
                           font=dict(size=10, color="#11613f" if sur == 6 else ("#8a5a00" if sur >= 4 else "#a02622")))
    habiller(fig, 380, barmode="stack", legend=dict(orientation="h", y=1.12, x=0, traceorder="normal"),
             xaxis=dict(title="Score (part réseau + part formation)", gridcolor="#efece4", range=[0, 2.45]),
             yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    tracer(fig, "pr_dix")
    st.caption("À droite de chaque barre : le nombre de tests de robustesse, sur 6, où la préfecture reste dans les "
               "10 premières.")

    lignes = []
    for _, r in dix.iterrows():
        lev = str(r["Leviers"])
        lignes.append({
            "Rang": str(int(r["O5-02 rang"])),
            "Préfecture": f'<b>{html.escape(r["Préfecture"])}</b>',
            "Zone": f'<span style="color:{COULEUR_ZONE.get(r["Zone"], ENCRE)};font-size:.78rem;font-weight:600">'
                    f'{html.escape(r["Zone"])}</span>',
            "Population": fr(r["Population"]),
            "Part en mauvais état": f'{fr(r["O3-02"], 1)} % <span style="color:#8a8780;font-size:.74rem">'
                                    f'({fr(r["Km évalués"], 1)} km évalués)</span>',
            "Auto-écoles /100 000": fr(r["O4-05"], 2),
            "Leviers": "".join(badge(x.strip(), LEVIER_COUL[x.strip()]) for x in lev.split(";")
                               if x.strip() in LEVIER_COUL) or "—",
            "Tests sur 6": f'{int(r["Tests parmi les 10 premières (sur 6)"])}/6',
        })
    st.markdown(table_html(lignes), unsafe_allow_html=True)
    with st.expander("Ce que cumule chacune des 10 premières"):
        for _, r in dix.iterrows():
            txt = phrase("Préfecture", r["Préfecture"])
            if txt:
                st.markdown(f'<div style="margin-bottom:7px;font-size:.88rem"><b>{html.escape(r["Préfecture"])}</b> — '
                            f'{html.escape(txt)}</div>', unsafe_allow_html=True)
note("Les km évalués sont écrits à côté de la part : le taux ne dit pas le volume. Danyi est en tête avec 100 % de km "
     "en mauvais état, sur 49,8 km évalués, pour 40 240 habitants. Les 10 premières comptent 1 416 859 habitants ; ni "
     "le Golfe ni Agoè-Nyivé n'en font partie.")

# ------------------------------------------------------------------ Section 4 — Les deux leviers
st.markdown("")
titre_bloc("Les deux leviers", "Chaque préfecture reçoit le levier de chaque seuil qu'elle franchit.")
recensees = pref10.set_index("Préfecture")["Formation — auto-écoles recensées"]
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="constat"><div class="constat-titre">Levier réseau — 13 préfectures</div>'
                '<div class="constat-texte">2 868 523 habitants · 304,6 km à remettre en état · cible : 14,35 % de km '
                'en mauvais état (médiane nationale) · en tête : Danyi (100,0 %).</div></div>', unsafe_allow_html=True)
    res = filtrer(cla[cla["Rang dans le levier réseau"].notna()].sort_values("Rang dans le levier réseau"))
    if res.empty:
        st.info("Aucune préfecture du levier réseau ne correspond aux filtres.")
    else:
        st.markdown(f'<div style="max-height:330px;overflow-y:auto">' + table_html([{
            "Rang": str(int(r["Rang dans le levier réseau"])),
            "Préfecture": f'<b>{html.escape(r["Préfecture"])}</b>',
            "Mauvais état": f'{fr(r["O3-02"], 1)} % <span style="color:#8a8780;font-size:.74rem">'
                            f'({fr(r["Km évalués"], 1)} km)</span>',
            "Km à remettre": badge(f'{fr(r["O5-04 km à remettre en état"], 1)} km', LEVIER_COUL["réseau"]),
        } for _, r in res.iterrows()]) + "</div>", unsafe_allow_html=True)
    lien_reco("Remettre en état le réseau → Recommandations", "réseau", "pr_lien_res")
with c2:
    st.markdown('<div class="constat"><div class="constat-titre">Levier formation — 23 préfectures, dont Mô</div>'
                '<div class="constat-texte">2 932 492 habitants · 41 auto-écoles à ouvrir · cible : 1,065 auto-école '
                'pour 100 000 habitants (médiane des 16 préfectures équipées) · en tête : Haho, la plus peuplée '
                '(305 096 habitants).</div></div>', unsafe_allow_html=True)
    form = filtrer(cla[cla["Rang dans le levier formation"].notna()].sort_values("Rang dans le levier formation"))
    if form.empty:
        st.info("Aucune préfecture du levier formation ne correspond aux filtres.")
    else:
        lignes = []
        for _, r in form.iterrows():
            nb_rec = recensees.get(r["Préfecture"], 0)
            nature = ("aucune recensée" if not nb_rec else f"{int(nb_rec)} recensées, non agréées")
            loin = r["Population au-delà de SE-08"]
            lignes.append({
                "Rang": str(int(r["Rang dans le levier formation"])),
                "Préfecture": f'<b>{html.escape(r["Préfecture"])}</b>',
                "Population": fr(r["Population"]),
                "À ouvrir": badge(str(int(r["O5-04 auto-écoles manquantes (écart 21)"])), LEVIER_COUL["formation"]),
                "Distance": f'{fr(r["O4-08"], 1)} km',
                "Nature du zéro": f'<span style="font-size:.74rem;color:'
                                  f'{"#8a5a00" if nb_rec else "#55534e"}">{nature}</span>',
                "Habitants à plus de 10 km": fr(loin) if loin == loin and loin else "—",
            })
        st.markdown('<div style="max-height:330px;overflow-y:auto">' + table_html(lignes) + "</div>",
                    unsafe_allow_html=True)
    lien_reco("Ouvrir et vérifier des auto-écoles → Recommandations", "formation", "pr_lien_form")
note("5 préfectures cumulent les deux déficits, 26 en ont un, 8 n'en ont aucun. La nature du zéro : 15 préfectures "
     "sans aucune auto-école recensée (25 auto-écoles), 8 avec des auto-écoles recensées non agréées (16 auto-écoles).")

# ------------------------------------------------------------------ Section 5 — Le classement tient-il ?
st.markdown("")
titre_bloc("Le classement tient-il ?", "Poids du réseau déplaçable, puis 5 tests de robustesse.")
g, d = st.columns([1, 1.2], vertical_alignment="top")
with g:
    poids = st.slider("Poids du réseau (%)", 0, 100, 50, 5, key="pr_poids")
    pr, pf = poids / 100, 1 - poids / 100
    rec = cla.copy()
    rec["score2"] = pr * rec["Rang percentile réseau"] + pf * rec["Rang percentile formation"]
    rec = rec.sort_values(["score2", "Population"], ascending=[False, False]).reset_index(drop=True)
    base = cla.sort_values("O5-02 rang")["Préfecture"].head(10).tolist()
    nouv = rec["Préfecture"].head(10).tolist()
    entrent = [p for p in nouv if p not in base]
    sortent = [p for p in base if p not in nouv]
    st.markdown(f"**Nouvelles 10 premières** (réseau {poids} %, formation {100 - poids} %) :")
    st.markdown(" · ".join(f"{i + 1}. {p}" for i, p in enumerate(nouv)))
    st.markdown(f'<div class="filtres-actifs"><b>Entrent :</b> {", ".join(entrent) or "—"} &nbsp;·&nbsp; '
                f'<b>Sortent :</b> {", ".join(sortent) or "—"} <span style="color:#55534e">(par rapport au '
                f'classement à 50 %)</span></div>', unsafe_allow_html=True)
    st.caption("Score = poids du réseau × rang percentile du réseau + poids de la formation × rang percentile de la "
               "formation ; à score égal, la préfecture la plus peuplée passe devant. Valeurs de contrôle : à 50 %, "
               "le classement publié ; à 65 %, Kloto et Ogou entrent, Est-Mono et Oti-Sud sortent ; à 35 %, Haho "
               "entre et Tchaoudjo sort.")
with d:
    syn = sens[sens["Préfecture"].isna() & (sens.Test != "T0")].copy()
    LIB = {"T1": "Réseau compté pour 2/3", "T2": "Formation comptée pour 2/3",
           "T3": "Écart à la médiane, au lieu du rang", "T4": "Sans le Grand Lomé",
           "T5": "Distance à l'auto-école, au lieu du nombre d'auto-écoles"}
    syn["Test"] = syn["Test"].map(LIB)
    st.markdown(table_html([{
        "Test": html.escape(str(r["Test"])),
        "Changements": badge(str(int(r["Changements parmi les 10 premières"])),
                             "#11613f" if int(r["Changements parmi les 10 premières"]) <= 1 else "#8a5a00"),
        "Entrent": f'<span style="color:#11613f">{html.escape(str(r["Entrées"]))}</span>',
        "Sortent": f'<span style="color:#a02622">{html.escape(str(r["Sorties"]))}</span>',
    } for _, r in syn.iterrows()]), unsafe_allow_html=True)
    note("Le classement est stable si aucun test ne change plus de 2 des 10 premières. Toujours en tête : Danyi, "
         "Blitta, Agou, Tchamba, Bassar, Oti, Bas-Mono. Les moins sûres : Est-Mono et Oti-Sud (4 tests sur 6), "
         "Tchaoudjo (3 sur 6).")

# ------------------------------------------------------------------ Section 6 — Classement complet
st.markdown("")
titre_bloc("Classement complet des 38 préfectures",
           "La desserte et la distance sont affichées à côté du classement, sans y entrer. Mô, hors classement, est "
           "présentée à part.")
comp = cla[cla["O5-02 rang"].notna()].sort_values("O5-02 rang").copy()
comp = filtrer(comp)
compt = comp[["O5-02 rang", "Préfecture", "Zone", "Population", "O3-02", "Km évalués", "O4-05", "O5-01 déficits",
              "Leviers", "O4-03", "Desserte faible (SE-06)", "O4-08",
              "Tests parmi les 10 premières (sur 6)"]].rename(
    columns={"O5-02 rang": "Rang", "O3-02": "Mauvais état (%)", "O4-05": "Auto-écoles /100 000",
             "O5-01 déficits": "Déficits (sur 2)", "O4-03": "Km /10 000 hab.", "O4-08": "Distance (km)",
             "Desserte faible (SE-06)": "Desserte faible",
             "Tests parmi les 10 premières (sur 6)": "Tests sur 6"})
if compt.empty:
    st.info("Aucune préfecture ne correspond aux filtres.")
else:
    lignes = []
    for _, r in compt.iterrows():
        lev = str(r["Leviers"])
        deficits = int(r["Déficits (sur 2)"])
        lignes.append({
            "Rang": str(int(r["Rang"])),
            "Préfecture": f'<b>{html.escape(r["Préfecture"])}</b>',
            "Zone": f'<span style="color:{COULEUR_ZONE.get(r["Zone"], ENCRE)};font-size:.76rem;font-weight:600">'
                    f'{html.escape(r["Zone"])}</span>',
            "Population": fr(r["Population"]),
            "Mauvais état": f'{fr(r["Mauvais état (%)"], 1)} % <span style="color:#8a8780;font-size:.72rem">'
                            f'({fr(r["Km évalués"], 1)} km)</span>',
            "Auto-écoles /100 000": fr(r["Auto-écoles /100 000"], 2),
            "Déficits": badge(f"{deficits}/2", "#0d366b" if deficits == 2 else
                              ("#3987e5" if deficits == 1 else "#b9b6ad")),
            "Leviers": "".join(badge(x.strip(), LEVIER_COUL[x.strip()]) for x in lev.split(";")
                               if x.strip() in LEVIER_COUL) or "—",
            "Km /10 000 hab.": fr(r["Km /10 000 hab."], 2) + (badge("desserte faible", "#eda100")
                                                              if bool(r["Desserte faible"]) else ""),
            "Distance": f'{fr(r["Distance (km)"], 1)} km',
            "Tests sur 6": f'{int(r["Tests sur 6"])}/6',
        })
    st.markdown(f'<div style="max-height:470px;overflow-y:auto;border-radius:10px">{table_html(lignes)}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="filtres-actifs"><b>Leviers :</b> {badge("réseau", LEVIER_COUL["réseau"])}'
                f'{badge("formation", LEVIER_COUL["formation"])} &nbsp;·&nbsp; <b>Déficits :</b> '
                f'{badge("2/2", "#0d366b")}{badge("1/2", "#3987e5")}{badge("0/2", "#b9b6ad")} &nbsp;·&nbsp; '
                f'{badge("desserte faible", "#eda100")} : 13 des 38 préfectures, et Mô.</div>',
                unsafe_allow_html=True)

mo = phrase("Préfecture", "Mô")
st.markdown(f'<div style="border:1px solid #e2dfd6;border-left:3px solid #b9b6ad;border-radius:10px;padding:10px 12px;'
            f'background:#fff;margin-top:8px"><b>Mô, hors classement</b><br>'
            f'<span style="font-size:.88rem">{html.escape(mo)}</span></div>', unsafe_allow_html=True)
export_csv(compt, "classement_prefectures.csv", "pr_exp_cla")
if st.button("Voir le classement sur la carte →", key="pr_lien_carte"):
    st.session_state["ca_couche"] = "Priorité"           # la carte s'ouvre sur la couche Priorité
    st.switch_page("views/carte.py")

# ------------------------------------------------------------------ Section 7 — Synthèse et limite
st.markdown("")
g, d = st.columns(2, vertical_alignment="top")
with g:
    synthese("4 zones", "en difficulté ; 5 préfectures cumulent les deux déficits",
             ["Centrale : route et formation ; Plateaux : route ; Savanes et Maritime hors Grand Lomé : formation.",
              "5 préfectures qui cumulent, 641 955 habitants ; 10 premières, 1 416 859 habitants.",
              "13 préfectures au levier réseau (304,6 km) ; 23 au levier formation (41 auto-écoles).",
              "Classement stable : aucun test ne change plus de 2 des 10 premières."])
with d:
    limite("Classement en C : vérification avant investissement. Le risque n'est pas classé par territoire, faute "
           "d'accidents par préfecture. L'accès rural, qui désigne les zones en retard sur la route, est estimé avec "
           "une population répartie uniformément dans chaque préfecture.")
pied()
