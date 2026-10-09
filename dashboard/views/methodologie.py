"""Page 7 — Méthodologie. Comment la décision a été produite, et ce que les données ne disent pas (design-page7.md).
Décomptes (sources, contrôles) comptés à l'affichage dans les CSV ; aucun n'est écrit en dur. Les formules et le
cadre sont de la documentation de méthode."""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from composants import ariane, constat, entete, limite, note, pied, synthese, titre_bloc  # noqa: E402
from donnees import fr, lire, lire_raw  # noqa: E402
from theme import BLEUS, THEME  # noqa: E402

ariane("Méthodologie")
entete("Méthodologie", "Sources, méthode et limites",
       "Le tableau de bord montre la décision et son fondement ; cette page dit <strong>comment elle a été "
       "produite</strong> et <strong>où elle s'arrête</strong>. Chaque étape a été gelée avant la suivante, et aucun "
       "chiffre affiché n'a été recopié à la main.")

# ------------------------------------------------------------------ Section 1 — Comment nous avons travaillé
titre_bloc("Comment nous avons travaillé", "Du problème à la solution, en 9 étapes.")
ETAPES = [
    ("Ce que l'énoncé demande", "Cinq objectifs : retracer les immatriculations et les permis, analyser la sécurité "
     "routière, évaluer l'état du réseau, cartographier le réseau et les auto-écoles, recommander.",
     "5 objectifs, et une question de décision : où agir en priorité ?"),
    ("Le cadre de décision", "Chaque objectif devient des indicateurs mesurables, des hypothèses à trancher et des "
     "seuils, fixés avant de regarder les données. La sécurité routière en compte 14 à elle seule.",
     "43 indicateurs · 17 vérifications et hypothèses · 10 seuils · 20 règles"),
    ("Les données", "Recensement des données ouvertes : immatriculations, permis, accidents, réseau, auto-écoles, "
     "population, enquêtes. Licences, mailles et années vérifiées une à une.",
     "34 fichiers · 30 jeux de données · 7 recherches complémentaires, dont 2 sans réponse"),
    ("Préparation et calcul", "Nettoyage, jointures, puis calcul de chaque indicateur avec la formule du cadre. Chacun "
     "reçoit son niveau de preuve.", "32 indicateurs calculés : 5 mesurés, 10 calculés, 17 estimés"),
    ("Ce que les données disent", "Le constat, sans jugement : le parc a quadruplé, porté par les motos ; les accidents "
     "augmentent en volume mais les taux baissent ; le réseau est inégalement entretenu.",
     "5 messages · 5 préfectures qui cumulent les deux déficits · 4 zones en difficulté"),
    ("Ce qu'elles ne disent pas", "Les accidents ne sont publiés que pour tout le pays. L'activité des auto-écoles "
     "n'est pas publiée. Le coût des actions est absent. Chaque manque est écrit, jamais comblé par une hypothèse.",
     "9 indicateurs non calculables · 7 questions ouvertes · 32 écarts déclarés"),
    ("Priorité et recommandations", "Les territoires sont classés sur ce qui est mesuré, puis chaque recommandation "
     "reçoit un territoire, une cible chiffrée, une population, un horizon, un responsable et une réserve.",
     "38 préfectures classées · 15 recommandations, dont 10 avec une quantité"),
    ("Et d'ici 2031 ?", "La population projetée est appliquée à chaque levier : combien faudra-t-il ajouter dans 1, 3 "
     "et 5 ans, et que demande la cible internationale de sécurité routière.",
     "5 horizons · 2 références sans action nouvelle · une fourchette sur chaque quantité"),
    ("Le livrable", "Ce tableau de bord, qui lit des fichiers de résultats sans rien recalculer, et une présentation.",
     "8 pages · une présentation · cette page de méthode"),
]
for i, (titre, phrase, produit) in enumerate(ETAPES):
    coul = BLEUS[min(i * len(BLEUS) // len(ETAPES), len(BLEUS) - 1)]
    txt_coul = "#ffffff" if coul in (BLEUS[3], BLEUS[4]) else "#141413"
    st.markdown(
        f'<div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:10px">'
        f'<div style="flex:0 0 36px;height:36px;border-radius:50%;background:{coul};color:{txt_coul};'
        f'display:flex;align-items:center;justify-content:center;font-weight:700">{i + 1}</div>'
        f'<div style="flex:1"><div style="font-weight:600">{html.escape(titre)}</div>'
        f'<div style="color:#3a3935;font-size:.9rem">{html.escape(phrase)}</div></div>'
        f'<div style="flex:0 0 32%;background:#f4f2ec;border-radius:8px;padding:8px 10px;font-size:.8rem;'
        f'color:#55534e">{html.escape(produit)}</div></div>', unsafe_allow_html=True)
st.caption("Chaque étape a été gelée avant de passer à la suivante : les seuils ont été fixés avant de voir les "
           "résultats, et aucun chiffre affiché ici n'a été recopié à la main.")

# ------------------------------------------------------------------ Section 2 — Sources
st.markdown("")
src = lire_raw("_SOURCES")
n_tel = (src.Statut == "Téléchargé").sum()
n_rec = len(src) - n_tel
titre_bloc("Sources", f"{len(src)} fichiers, issus de {src['Jeu de données'].nunique()} jeux de données · "
           f"{n_tel} téléchargés, {n_rec} recensés seulement.")
vue = src[["Jeu de données", "Producteur", "Licence déclarée", "Statut", "Date de téléchargement"]].copy()
vue["Statut"] = vue["Statut"].str.split(" :").str[0]
st.dataframe(vue, hide_index=True, use_container_width=True, height=360)
note("La grille de population WorldPop, recensée seulement à l'inventaire, a été téléchargée ensuite pour mesurer "
     "l'accès rural et placer les auto-écoles (page Horizon 2031). Son empreinte est dans sources_A1.csv. Le registre "
     "reste celui de l'inventaire : il n'est pas réécrit après coup.")

# ------------------------------------------------------------------ Section 3 — Limites majeures
st.markdown("")
titre_bloc("Limites majeures")
for i, t in enumerate([
    "Les accidents ne sont publiés qu'au niveau national : ni préfecture, ni mois, ni âge, ni véhicule.",
    "L'activité des auto-écoles n'est pas publiée : une auto-école agréée n'est pas forcément active.",
    "L'état du réseau vient du relevé des tronçons de 2020, avec une méthode de notation non publiée. L'annuaire "
    "national de la même année donne d'autres parts par état ; aucune ne concorde.",
    "Le parc de véhicules en circulation n'est pas publié : il est estimé dans une fourchette.",
    "Le coût des actions n'est pas dans les données : les quantités sont des ordres de grandeur, pas des devis.",
    "Les recommandations en C demandent une vérification avant tout investissement.",
    "La population en âge de conduire ne se raccorde pas d'une source à l'autre : les 18 ans et plus font 51,8 % de "
    "la population au recensement de 2022 et 55,6 % dans la projection de 2023 (réserve A1-R1).",
    "Les quantités d'ici 2031 sont des estimations, pas des prévisions : elles supposent la population projetée par "
    "l'INSEED et les leviers à leur dernière observation.",
], 1):
    st.markdown(f"{i}. {t}")

# ------------------------------------------------------------------ Section 4 — Niveaux de preuve
st.markdown("")
g, d = st.columns([1, 1.4], vertical_alignment="top")
with g:
    titre_bloc("Niveaux de preuve")
    st.markdown("**A** = mesuré (comptage direct)  \n**B** = calculé (formule maîtrisée)  \n"
                "**C** = estimé (approximation ou méthode non documentée)")
    st.dataframe(pd.DataFrame({"Niveau": ["A", "B", "C", "Total"],
                               "Indicateurs du cadre": ["5", "10", "17", "32"]}),
                 hide_index=True, use_container_width=True)
    st.caption("S'y ajoutent les 3 compléments à l'énoncé (C) et l'accès rural à une route revêtue (C). "
               "Décompte lu dans catalogue_07.csv.")
with d:
    titre_bloc("Questions ouvertes", "Les 7 hypothèses non testables, et la donnée qui manque.")
    hyp = lire("09_diagnostic", "hypotheses_09")
    cons = lire("11_tableau_de_bord", "consequences_11").set_index("Code")
    nt = hyp[hyp.Verdict == "non testable"].copy()
    lignes = []
    for _, r in nt.iterrows():
        manque = cons.loc[r["Code"], "Donnée manquante affichée"] if r["Code"] in cons.index else ""
        lignes.append({"Hypothèse": r["Énoncé"], "Pourquoi non testable": r["Raison"],
                       "Donnée qui la rendrait testable": manque})
    st.dataframe(pd.DataFrame(lignes), hide_index=True, use_container_width=True, height=300)
    st.caption("Une base d'accidents par préfecture, avec le mois, l'âge et la catégorie de véhicule, rendrait ces "
               "7 questions testables (recommandation « Créer une base d'accidents par préfecture », page "
               "Recommandations).")

# ------------------------------------------------------------------ Section 6 — Zones les moins desservies
st.markdown("")
titre_bloc("Les zones les moins desservies", "Deux mesures de l'accès rural, côte à côte.")
acc = pd.DataFrame({
    "Zone": ["Maritime hors Grand Lomé", "Centrale", "Kara", "Savanes", "Plateaux", "Médiane des 5 zones", "Pays"],
    "Uniforme (%)": ["23,14", "13,19", "17,49", "16,93", "13,55", "16,93", "17,17"],
    "Position (uniforme)": ["au-dessus", "sous la médiane", "au-dessus", "au-dessus (médiane)", "sous la médiane", "", ""],
    "Grille WorldPop (%)": ["39,55", "25,12", "23,65", "23,37", "21,26", "23,65", "27,12"],
    "Position (grille)": ["au-dessus", "au-dessus", "au-dessus (médiane)", "sous la médiane", "sous la médiane", "", ""]})
st.dataframe(acc, hide_index=True, use_container_width=True)
st.markdown("La grille place la population là où elle vit, au lieu de l'étaler sur toute la préfecture : l'accès monte "
            "partout. Les Plateaux restent sous la médiane dans les deux mesures. **La zone qui cumule les deux "
            "retards est la Centrale dans la première mesure et les Savanes dans la seconde.**")
constat("La recommandation de zone de la Centrale garde sa priorité haute : la Centrale reste la zone au réseau le "
        "plus dégradé, 40,3 % de km en mauvais état contre 12,8 % dans les Savanes, et la lecture « formation » ne "
        "change pas. Un écart de 0,28 point ne sépare pas deux zones à ce niveau de preuve.")
limite("L'accès rural est estimé : avec la population rurale supposée répartie uniformément dans chaque préfecture, ou "
       "placée par la grille de population WorldPop 2020 (carreaux de 100 m). Les deux mesures sont affichées ; la "
       "seconde est la plus fine, mais la grille est elle-même un modèle.", titre="Limite de l'accès rural")

# ------------------------------------------------------------------ Section 7 — Les formules
st.markdown("")
titre_bloc("Les formules", "Chaque indicateur affiché vient d'une de ces formules. L'exemple reprend une valeur "
           "affichée ailleurs dans le tableau de bord.")
BLOCS = {
    "Mobilité": (THEME["Mobilité"], [
        ("Immatriculations pour 1 000 habitants (A)", "immatriculations de l'année ÷ population × 1 000",
         "2022 : 93 770 ÷ 8 095 498 × 1 000 = 11,6 pour 1 000 habitants"),
        ("Rapport immatriculations / permis (B)", "immatriculations d'une catégorie ÷ permis de la catégorie",
         "Cumul 2007–2024 : 40,2 motos immatriculées par permis moto, contre 0,37 à 2,33 ailleurs"),
        ("Croissance annuelle moyenne (B)", "(valeur finale ÷ valeur initiale)^(1/n) − 1",
         "Immatriculations 1990–2024 : (88 198 ÷ 6 829)^(1/34) − 1 = 7,8 % par an")]),
    "Sécurité routière": (THEME["Sécurité routière"], [
        ("Tués pour 100 000 habitants (B)", "tués de l'année ÷ population × 100 000",
         "2022 : 683 ÷ 8 095 498 × 100 000 = 8,44 pour 100 000 habitants"),
        ("Tués pour 10 000 véhicules (C)", "tués de l'année ÷ parc estimé × 10 000",
         "2024 : 597 ÷ 751 398 × 10 000 = 7,95 (de 6,18 à 10,30)"),
        ("Gravité (B)", "tués ÷ accidents constatés × 100",
         "2022 : 683 ÷ 7 507 × 100 = 9,1 tués pour 100 accidents")]),
    "Réseau routier": (THEME["Réseau"], [
        ("Part en mauvais état (C)", "km en mauvais état ÷ km évalués × 100 (évalués = bon+moyen+mauvais+travaux)",
         "Blitta : 69,0 ÷ 101,1 × 100 = 68,2 % en mauvais état"),
        ("Km de routes pour 10 000 habitants (B)", "km de routes classées ÷ population × 10 000",
         "Savanes : 528,0 ÷ 1 143 520 × 10 000 = 4,62 km pour 10 000 habitants"),
        ("Densité routière (B)", "km de routes classées ÷ surface × 1 000 (surface en km²)",
         "Golfe : 96,8 ÷ 240,8 × 1 000 = 401,9 km pour 1 000 km²"),
        ("Accès rural à une route revêtue (C)", "ruraux à moins de 2 km d'une route revêtue ÷ population rurale × 100",
         "Pays : 17,2 % (population uniforme), 27,1 % (grille WorldPop)")]),
    "Formation": (THEME["Couverture"], [
        ("Auto-écoles pour 100 000 habitants (C)", "auto-écoles agréées ÷ population × 100 000",
         "Savanes : 4 ÷ 1 143 520 × 100 000 = 0,35 pour 100 000 habitants"),
        ("Habitants par auto-école agréée (B)", "population ÷ auto-écoles agréées (non défini si aucune)",
         "Haho : 305 096 ÷ 0 = non défini, aucune auto-école agréée"),
        ("Distance à l'auto-école agréée la plus proche (C)", "plus courte distance chef-lieu → auto-école agréée",
         "Oti-Sud : 84,0 km, la plus grande des 39 préfectures")]),
    "Horizon 2031": ("#0d366b", [
        ("Auto-écoles à ouvrir (C)", "⌈1,065 × population ÷ 100 000⌉ − auto-écoles agréées (≥ 0, par préfecture)",
         "Haho en 2029 : ⌈1,065 × 334 220 ÷ 100 000⌉ = 4, moins 0 = 4 auto-écoles"),
        ("Km à remettre en état (C)", "km en mauvais état − 14,35 % des km évalués (≥ 0 ; inchangé selon l'horizon)",
         "Blitta : 69,0 − (14,35 % × 101,1) = 54,5 km"),
        ("Permis moto à délivrer dans l'année (C)", "1,275 × population de 18 ans et plus ÷ 1 000",
         "2029 : 6 540 permis moto, pour 5 131 425 habitants de 18 ans et plus"),
        ("Cible de la Décennie (C)", "valeur de 2021 diminuée de moitié en 2030, trajectoire régulière",
         "Tués : la moitié de 680 = 340 tués en 2030"),
        ("Plafond du casque (C)", "tués attendus × 60 % × 42 % (part deux-roues × réduction du casque)",
         "2031 : de 144 à 182 tués, pour un écart à la cible de 231 à 380")]),
}
for nom, (coul, formules) in BLOCS.items():
    st.markdown(f'<div style="font-weight:700;margin-top:8px"><span style="display:inline-block;width:12px;height:12px;'
                f'border-radius:3px;background:{coul};margin-right:7px"></span>{html.escape(nom)}</div>',
                unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(formules, columns=["Formule", "Calcul", "Exemple chiffré"]),
                 hide_index=True, use_container_width=True)
with st.expander("Toutes les autres formules du cadre d'analyse"):
    cat = lire("07_indicateurs", "catalogue_07")
    st.dataframe(cat[["Indicateur", "Formule", "Unité", "Niveau (04)"]], hide_index=True, use_container_width=True)

# ------------------------------------------------------------------ Section 8 — Corrections et contrôles
st.markdown("")
titre_bloc("Corrections et contrôles")
with st.expander("Ce qu'une analyse plus fine a corrigé", expanded=True):
    err = lire("A1_horizon", "erratum_A1")
    st.dataframe(err[["Type", "Objet", "Conséquence"]], hide_index=True, use_container_width=True)
    st.caption("Les analyses ont été gelées étape par étape. Une analyse plus fine, faite ensuite, a corrigé une "
               "conclusion et mis un chiffre en réserve. Les deux sont ici, avec leur source.")
with st.expander("Les contrôles, étape par étape", expanded=True):
    TABLES = [("Compréhension des données", "04_understanding", "controles_coherence"),
              ("Préparation des données", "05_preparation", "controles_05"),
              ("Indicateurs", "07_indicateurs", "controles_07"),
              ("Classement", "08_priorisation", "controles_08"),
              ("Diagnostic", "09_diagnostic", "controles_09"),
              ("Recommandations", "10_recommandations", "controles_10"),
              ("Textes du tableau de bord", "11_tableau_de_bord", "controles_11"),
              ("Horizon 2031", "A1_horizon", "controles_A1")]
    lignes = []
    for etape, dossier, nom in TABLES:
        d = lire(dossier, nom)
        res = d["Résultat"].astype(str).str.strip().str.lower()
        conformes = res.str.startswith("conforme").sum()
        lignes.append({"Étape": etape, "Contrôles": len(d), "Conformes": int(conformes)})
    st.dataframe(pd.DataFrame(lignes), hide_index=True, use_container_width=True)
    st.caption("Chaque étape vérifie ses propres chiffres avant de passer à la suivante : les sommes, les totaux, les "
               "bornes, et chaque chiffre écrit dans le document correspondant. Comptés à l'affichage, aucun en dur.")

# ------------------------------------------------------------------ Section 9 — Licences
st.markdown("")
titre_bloc("Licences")
st.dataframe(pd.DataFrame([
    ("HDX (limites administratives, chefs-lieux)", "CC BY-IGO"),
    ("OMS (profil du Togo)", "CC BY-NC-SA 3.0 IGO, usage non commercial"),
    ("WPP (Nations unies)", "CC BY 3.0 IGO"),
    ("DHS", "Conditions du programme DHS"),
    ("EHCVM (Banque mondiale)", "Conditions de la Banque mondiale, sans redistribution ; citation obligatoire"),
    ("Jeux de l'INSEED et catalogue du géoportail", "Licence non déclarée ; usage couvert par l'énoncé"),
    ("WorldPop", "CC BY 4.0 ; grille de population 2020 (accès rural, emplacement des auto-écoles)"),
    ("Armoiries du Togo (écu, static/)", "CC BY-SA 4.0, Edem Fiadjoe — attribution obligatoire"),
], columns=["Source", "Licence"]), hide_index=True, use_container_width=True)

# ------------------------------------------------------------------ Section 10 — Constat, synthèse, limite
st.markdown("")
g, d = st.columns(2, vertical_alignment="top")
with g:
    constat("Le tableau de bord montre la décision et son fondement ; cette page dit comment elle a été produite et "
            "où elle s'arrête.")
    synthese("9 étapes", "de travail, gelées l'une après l'autre",
             ["30 jeux de données ; 32 indicateurs, dont 17 en C.",
              "18 formules ; 7 questions ouvertes.",
              "1 correction et 1 réserve (annexe Horizon 2031)."])
with d:
    limite("Un indicateur en C demande une vérification avant tout investissement.")
pied()
