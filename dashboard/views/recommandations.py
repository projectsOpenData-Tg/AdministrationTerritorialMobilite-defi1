"""Page 6 — Recommandations. Les 15 cartes du 10 et les 39 fiches préfectures, en 7 onglets (design-page6.md).

Aucun recalcul : cartes_10, prefectures_10, zones_10, horizon_A1. Les textes lus dans les CSV sont réécrits à
l'affichage (11 §4.2) ; aucun identifiant de recommandation ni renvoi de document n'apparaît à l'écran."""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from composants import (ariane, constat, entete, export_csv, limite, onglets, pied, synthese,  # noqa: E402
                        titre_bloc)
from donnees import fr, lire  # noqa: E402

cartes = lire("10_recommandations", "cartes_10")
pref10 = lire("10_recommandations", "prefectures_10")
zones10 = lire("10_recommandations", "zones_10")

f_zones = st.session_state.get("f_zones", [])
f_prio = st.session_state.get("f_priorites", [])

PRIO_COUL = {"Haute": "#0d366b", "Moyenne": "#3987e5", "Faible": "#cde2fb", "Aucune action": "#b9b6ad"}
THEME_PASTILLE = {"Réseau": "#eb6834", "Formation": "#1baf7a", "Sécurité routière": "#eda100",
                  "Zones les moins desservies": "#0d366b", "Données": "#55534e"}


def _etiq(txt, coul, fonce=False):
    c = "#ffffff" if fonce else "#141413"
    return f'<span style="background:{coul};color:{c};border-radius:999px;padding:2px 10px;font-size:.72rem;' \
           f'font-weight:600;margin-right:6px;white-space:nowrap">{html.escape(str(txt))}</span>'


@st.cache_data(show_spinner=False)
def _horizons() -> dict:
    """Pour chaque recommandation, la ligne d'horizon de l'annexe A1 : la quantité au palier de l'horizon qu'elle
    porte, quand cette quantité change avec la population. Quand elle ne change pas (remise en état), la ligne dit
    pourquoi. Les recommandations sans quantité n'ont pas de ligne."""
    h = lire("A1_horizon", "horizon_A1")
    h = h[h.Maille == "Recommandation"]
    sortie: dict[str, list[str]] = {}
    for rec, sub in h.groupby("Recommandation"):
        ident = str(rec).split(" (")[0]
        pal = sub[sub["Palier de l’horizon"].astype(str) == "True"]
        passe = sub[sub["Palier"].astype(str) == "Passé"]
        if pal.empty:
            continue
        p = pal.iloc[0]
        mesure = str(p["Mesure"])
        if mesure == "aucune quantité" or p["Valeur"] != p["Valeur"]:
            continue
        depart = passe.iloc[0]["Valeur"] if not passe.empty else None
        if mesure == "km à remettre en état":
            # La remise en état ne suit pas la population : le relevé de 2020 est la seule mesure de l'état.
            ligne = "Cette quantité ne change pas avec l'horizon : aucune donnée ne mesure l'usure du réseau."
        else:
            dec = 1 if "km" in mesure else 0          # des km au dixième, des comptes entiers
            grandi = (depart is not None and p["Valeur"] > depart)
            ligne = (f"D'ici {int(p['Année'])}, horizon de cette action : {fr(p['Valeur'], dec)} {mesure}"
                     + (", la population ayant grandi." if grandi else "."))
        sortie.setdefault(ident, [])
        if ligne not in sortie[ident]:
            sortie[ident].append(ligne)
    return sortie


HORIZONS = _horizons()


def carte(row, cle: str):
    theme = row["Onglet"]
    coul_t = THEME_PASTILLE.get(theme, "#55534e")
    coul_p = PRIO_COUL.get(row["Priorité"], "#b9b6ad")
    fonce = row["Priorité"] in ("Haute",)
    national = str(row["Zones"]).strip() == "National"
    etiqs = (_etiq(row["Priorité"], coul_p, fonce) + _etiq(row["Nature"], "#efece4") + _etiq(row["Horizon"], "#efece4")
             + (_etiq("national", "#e3eefb") if national else ""))
    lignes_h = HORIZONS.get(str(row["ID"]), [])
    horizon = "".join(f'<div style="font-size:.78rem;color:#55534e;border-left:2px solid #e2dfd6;padding-left:7px;'
                      f'margin-top:6px">{html.escape(t)}</div>' for t in lignes_h)
    st.markdown(
        f'<div class="reco-carte" style="border:1px solid #e2dfd6;border-radius:12px;padding:14px;background:#fff;'
        f'height:100%;border-top:3px solid {coul_t}">'
        f'<div style="font-size:.7rem;font-weight:700;letter-spacing:.04em;color:{coul_t}">{html.escape(theme.upper())}</div>'
        f'<div style="font-weight:600;margin:4px 0;line-height:1.25">{html.escape(row["Titre"])}</div>'
        f'<div style="color:#3a3935;font-size:.9rem">{html.escape(str(row["Cible"]))}</div>'
        f'<div style="color:#55534e;font-size:.8rem;margin:6px 0">{html.escape(str(row["Contexte"]))}</div>'
        f'<div style="margin:8px 0">{etiqs}</div>'
        f'<div style="font-size:.85rem;color:#3a3935">{html.escape(str(row["Texte"]))}</div>'
        f'{horizon}</div>',
        unsafe_allow_html=True)
    with st.expander("Détail"):
        st.markdown(f"**Acteur :** {row['Acteur']}  \n**Suivi :** {row['Indicateur de suivi']}  \n"
                    f"**Niveau :** {row['Niveau de preuve']}  \n**Réserve :** {row['Réserve']}")
        if st.button("Voir l'horizon de cette action →", key=f"{cle}_hz_{row['ID']}"):
            st.switch_page("views/horizon.py")


def grille(df, cle):
    """Les cartes en grille de 3 colonnes, dans l'ordre du 10 (priorité, puis habitants), filtres appliqués."""
    df = df.sort_values("Ordre")
    if f_prio:
        df = df[df["Priorité"].isin(f_prio)]
    if f_zones:
        df = df[df["Zones"].astype(str).apply(lambda s: s.strip() == "National" or any(z in s for z in f_zones))]
    if recherche:
        m = recherche.lower()
        df = df[df.apply(lambda r: m in str(r["Titre"]).lower() or m in str(r["Texte"]).lower()
                         or m in str(r["Cible"]).lower(), axis=1)]
    if df.empty:
        st.info("Aucune recommandation ne correspond aux filtres.")
        return
    lignes = list(df.to_dict("records"))
    for i in range(0, len(lignes), 3):
        cols = st.columns(3)
        for col, row in zip(cols, lignes[i:i + 3]):
            with col:
                carte(row, cle)


def fiche(row):
    coul_p = PRIO_COUL.get(row["Priorité"], "#b9b6ad")
    lev = str(row["Leviers"])
    icone = "🛣️📚" if "réseau" in lev and "formation" in lev else ("🛣️" if "réseau" in lev else
            ("📚" if "formation" in lev else "✓"))
    titre_reseau = "Desserte" if row["Préfecture"] == "Mô" else "Réseau"
    st.markdown(
        f'<div class="reco-carte" style="border:1px solid #e2dfd6;border-radius:12px;padding:14px;background:#fff;'
        f'height:100%;border-left:3px solid {coul_p}">'
        f'<div style="display:flex;justify-content:space-between"><div style="font-weight:700">{icone} '
        f'{html.escape(row["Préfecture"])}</div><div style="color:#55534e;font-size:.8rem">{html.escape(row["Zone"])}</div></div>'
        f'<div style="font-size:1.4rem;font-weight:700;color:#0d366b;margin:2px 0">{fr(row["Population"])}</div>'
        f'<div style="font-size:.7rem;color:#55534e;margin-bottom:6px">habitants</div>'
        f'<div style="font-size:.85rem"><b>{titre_reseau} :</b> {html.escape(str(row["Texte réseau"]))}</div>'
        f'<div style="font-size:.85rem;margin-top:3px"><b>Formation :</b> {html.escape(str(row["Texte formation"]))}</div>'
        f'<div style="background:#f4f2ec;border-left:3px solid #55534e;padding:7px 9px;margin-top:8px;font-size:.82rem">'
        f'<b>Actions recommandées :</b> {html.escape(str(row["Actions"]))}</div>'
        f'<div style="margin-top:8px">{_etiq(row["Priorité"], coul_p, row["Priorité"] == "Haute")}'
        f'<span style="color:#55534e;font-size:.78rem">📍 {html.escape(row["Zone"])} — {html.escape(row["Préfecture"])}</span></div>'
        f'</div>', unsafe_allow_html=True)


ariane("Recommandations")
entete("Recommandations", "Quelle action engager ?",
       "<strong>15 recommandations</strong> : 3 en priorité haute, 10 en moyenne, 2 en faible ; 5 préfectures cumulent "
       "les deux déficits. <strong>Les habitants ne s'additionnent pas</strong> d'une carte à l'autre.")

# ------------------------------------------------------------------ Barre de résumé et recherche
b1, b2 = st.columns([1.6, 1], vertical_alignment="center")
with b1:
    st.markdown('<div class="filtres-actifs"><b>15 recommandations</b> · les habitants ne s\'additionnent pas d\'une '
                'carte à l\'autre · priorité et zone se choisissent dans la barre latérale.</div>',
                unsafe_allow_html=True)
with b2:
    recherche = st.text_input("Rechercher dans les recommandations", key="r_rech",
                              placeholder="titre, cible ou texte")

# Les zones en difficulté, lues dans zones_10 (une ligne, en tête de page).
zz = zones10[(zones10.Maille == "Zone") & zones10["Moins bien desservie pour"].notna()]
par_deficit: dict[str, list[str]] = {}
for _, r in zz.iterrows():
    par_deficit.setdefault(str(r["Moins bien desservie pour"]), []).append(str(r["Zone"]))
texte_zones = " · ".join(f"<b>{', '.join(z)}</b> ({d})" for d, z in par_deficit.items())

z1, z2 = st.columns([3, 1], vertical_alignment="center")
with z1:
    st.markdown(f'<div class="filtres-actifs"><b>Zones en difficulté :</b> {texte_zones}.</div>',
                unsafe_allow_html=True)
with z2:
    if st.button("Pourquoi ces zones →", key="r_lien_p5"):
        st.switch_page("views/priorites.py")

ong = onglets("recommandations", ["Toutes", "Réseau", "Formation", "Sécurité routière",
                                  "Zones les moins desservies", "Données", "Actions par zone"])

reco = cartes[cartes.Rubrique == "Recommandations"]
loin = cartes[cartes.Rubrique == "Pour aller plus loin"]

with ong[0]:
    grille(reco, "r_toutes")
    titre_bloc("Pour aller plus loin : ce que les données ne permettent pas encore de dire", marge=True)
    st.caption("Ces 4 actions relèvent des producteurs de données, pas des régions. La base d'accidents par "
               "préfecture permettrait de trancher 7 questions que le diagnostic laisse ouvertes, dont le lien entre "
               "réseau dégradé et accidents. Les trois autres rendraient vérifiables les chiffres estimés de cette "
               "page.")
    grille(loin, "r_loin")

with ong[1]:
    grille(cartes[cartes.Onglet == "Réseau"], "r_reseau")
with ong[2]:
    grille(cartes[cartes.Onglet == "Formation"], "r_formation")
with ong[3]:
    grille(cartes[cartes.Onglet == "Sécurité routière"], "r_securite")
with ong[4]:
    st.markdown('<div class="filtres-actifs"><b>Par où commencer :</b> ces trois cartes ne créent ni km ni auto-école '
                'en plus ; elles disent par quelle zone commencer.</div>', unsafe_allow_html=True)
    grille(cartes[cartes.Onglet == "Zones les moins desservies"], "r_zones")
    if st.button("Pourquoi ces zones → Priorités", key="r_lien_zones"):
        st.switch_page("views/priorites.py")
    st.caption("Mesuré avec une grille de population, l'accès rural change de lecture : les Savanes passent sous la "
               "médiane et la Centrale au-dessus. La Centrale garde la première place : elle reste la zone au réseau "
               "le plus dégradé, et sa formation ne change pas. Les deux mesures sont en page Méthodologie.")
with ong[5]:
    grille(cartes[cartes.Onglet == "Données"], "r_donnees")

with ong[6]:
    titre_bloc("Les 39 fiches préfectures", "Filtre par zone dans la barre latérale ; tri au choix.")
    p = pref10.copy()
    p["Déficits"] = p["Déficits"].fillna(0)
    fiche_pref = st.session_state.get("fiche_prefecture")
    if fiche_pref and fiche_pref in set(p["Préfecture"]):
        st.info(f"Fiche filtrée sur **{fiche_pref}** (arrivée depuis la carte).")
        if st.button("Voir les 39 fiches", key="r_toutes_fiches"):
            st.session_state["fiche_prefecture"] = None
            st.rerun()
        p = p[p["Préfecture"] == fiche_pref]
    else:
        if f_zones:
            p = p[p["Zone"].isin(f_zones)]
        if f_prio:
            p = p[p["Priorité"].isin(f_prio)]
        if recherche:
            m = recherche.lower()
            p = p[p.apply(lambda r: m in str(r["Préfecture"]).lower() or m in str(r["Actions"]).lower()
                          or m in str(r["Texte réseau"]).lower() or m in str(r["Texte formation"]).lower(), axis=1)]
    TRIS = {"Rang national (Mô à la fin)": (["Rang national", "Population"], [True, False]),
            "Population, de la plus forte": (["Population"], [False]),
            "Zone, puis préfecture": (["Zone", "Préfecture"], [True, True]),
            "Nombre de déficits": (["Déficits", "Population"], [False, False])}
    tri = st.selectbox("Trier les fiches", list(TRIS), key="r_tri")
    cols_tri, sens = TRIS[tri]
    p = p.sort_values(cols_tri, ascending=sens, na_position="last")
    if p.empty:
        st.info("Aucune fiche ne correspond aux filtres.")
    else:
        lignes = list(p.to_dict("records"))
        for i in range(0, len(lignes), 3):
            cols = st.columns(3)
            for col, row in zip(cols, lignes[i:i + 3]):
                with col:
                    fiche(row)
        st.caption(f"{len(p)} fiches affichées. Répartition d'ensemble : 5 en priorité haute, 26 en moyenne, "
                   "8 sans action. 🛣️ réseau · 📚 formation · 🛣️📚 les deux · ✓ suivi courant.")
    export_csv(p[["Préfecture", "Zone", "Région", "Population", "Priorité", "Leviers", "Texte réseau",
                  "Texte formation", "Actions"]], "fiches_prefectures.csv", "r_exp_fiches")

# ------------------------------------------------------------------ Synthèse, limite et exports
st.markdown("")
g, d = st.columns(2, vertical_alignment="top")
with g:
    constat("5 préfectures cumulent les deux déficits : <strong>Danyi, Blitta, Agou, Tchamba et Bassar</strong>, "
            "641 955 habitants.")
    synthese("15", "recommandations : 3 hautes, 10 moyennes, 2 faibles",
             ["10 conditionnelles, 5 immédiates.",
              "Réseau : 304,6 km à remettre en état dans 13 préfectures.",
              "Formation : 41 auto-écoles dans 23 préfectures.",
              "Les habitants ne s'additionnent pas d'une carte à l'autre."])
with d:
    limite("Recommandations en C : vérifier avant d'investir ; pas d'accidents par territoire ; le coût n'est pas dans "
           "les données. Le détail par horizon, zone et préfecture est en page Horizon 2031.")
export_csv(cartes[["Onglet", "Rubrique", "Titre", "Cible", "Contexte", "Priorité", "Nature", "Horizon", "Zones",
                   "Acteur", "Indicateur de suivi", "Niveau de preuve", "Réserve", "Texte"]],
           "recommandations_15.csv", "r_exp_cartes", "Exporter les 15 recommandations (CSV)")
pied()
