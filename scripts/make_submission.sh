#!/usr/bin/env bash
# Construit l'archive à soumettre au jury (même principe qu'au défi « Économie numérique » :
# EconomyNumeric-Challenge2/scripts/make_submission.sh).
#
# ⚠️ **Liste blanche, pas liste noire.** Chaque élément à inclure est nommé explicitement :
# ce qui n'y figure pas ne peut pas se retrouver dans l'archive par oubli. Les contrôles de la
# fin vérifient ensuite l'absence de ce qui ne doit jamais s'y trouver.
#
# Volontairement absents :
#   • le rapport .pptx et scripts/build_presentation.py — le rapport se dépose dans son propre
#     champ du formulaire ; il est envoyé séparément, et son script le suit ;
#   • workspace/ et methodology/ — documents de travail : plans de pages, maquette, garde-fous,
#     énoncé, journaux de développement. Le jury lit les documents 01 à 11, pas nos brouillons ;
#   • tmp/ — notes internes, plan du rapport, figures du rapport ;
#   • _CONSTRAINTS_DEV.txt, _GUARD_RAILS_REPO.txt — consignes internes de développement ;
#   • .env, .git/, .venv/ — identifiants, historique, environnement ;
#   • dashboard/.streamlit/secrets.toml — jeton du bot Telegram (le modèle, lui, est inclus) ;
#   • data/raw/ (81 Mo) — les jeux de données d'origine, publiés sur leurs portails. Le registre
#     des sources (data/raw/_SOURCES.csv) est inclus : la page Méthodologie le lit, et il porte
#     l'URL et l'empreinte de chaque fichier ;
#   • data/interim/ (9,1 Mo) — étapes intermédiaires de la préparation, qui ne se rejouent pas
#     sans data/raw/ ;
#   • data/analysis/04_understanding/rapports/ (76 Mo) — les 52 rapports de profilage HTML.
#     Ils pèsent à eux seuls plus que tout le reste ; `python3 scripts/profil_04.py` les
#     régénère à partir des données d'origine.
#
# Ce que l'archive contient, et pourquoi : les 13 documents d'analyse (01 à 11 et l'annexe
# Horizon 2031), le cadre de décision du 02 (tables CSV et classeur), le tableau de bord complet
# avec ses données, les scripts qui produisent ces données, et les notebooks d'exploration.
# **Le tableau de bord se lance depuis l'archive seule** : toutes les tables qu'il lit en font
# partie (data/analysis/**/*.csv, data/processed/, data/reference/, data/raw/_SOURCES.csv).
#
# Taille : la page de soumission n'annonce pas de limite, mais au défi « Économie numérique »
# le support a jugé trop lourde une archive de 12,1 Mo. Le script refuse donc toute archive de
# plus de 15 Mo et le signale au-delà de 8 Mo, pour garder de la marge.
#
# Usage : bash scripts/make_submission.sh   (depuis n'importe où)

set -euo pipefail

ARCHIVE="Togo-Defi1-MobiliteSecuriteRoutiere.zip"
TAILLE_MAX_OCTETS=$((15 * 1024 * 1024))
TAILLE_CONFORT_OCTETS=$((8 * 1024 * 1024))
cd "$(dirname "$0")/.."

rm -f "$ARCHIVE"

# 1. Documents d'analyse, cadre de décision, code et données lues par le tableau de bord.
zip -r -q "$ARCHIVE" \
  01_problem_definition.md 02_decision_matrix.md 02_decision_matrix.xlsx 02_decision_matrix \
  03_data_inventory.md 04_data_understanding.md 05_data_preparation.md 06_exploration.md \
  07_indicateurs.md 08_priorisation.md 09_diagnostic.md 10_recommendation.md \
  11_tableau_de_bord.md A1_horizon.md \
  requirements.txt \
  dashboard scripts notebooks \
  data/analysis data/processed data/reference data/raw/_SOURCES.csv \
  -x '*/__pycache__/*' '*.pyc' '*/.pytest_cache/*' '*/.ruff_cache/*' '*/.ipynb_checkpoints/*' \
     '*/.DS_Store' \
     'scripts/build_presentation.py' \
     'dashboard/.streamlit/secrets.toml' \
     'data/analysis/04_understanding/rapports/*'

# Le contenu de l'archive, listé une seule fois. Les contrôles lisent cette variable et non un
# tuyau : avec `pipefail`, un `grep -q` qui sort au premier résultat ferme le tuyau sous `unzip`,
# qui meurt d'un SIGPIPE — le contrôle échouait alors sur un fichier pourtant présent.
contenu=$(unzip -Z1 "$ARCHIVE")

# 2. Contrôles : l'archive ne doit contenir aucun des éléments écartés.
for motif in '^workspace/' '^methodology/' '^tmp/' '^\.git/' '^\.venv/' '(^|/)\.env$' \
             '_CONSTRAINTS_DEV' '_GUARD_RAILS_REPO' '\.pptx$' 'build_presentation\.py$' \
             'secrets\.toml$' '^data/raw/(?!_SOURCES)' '^data/interim/' \
             '04_understanding/rapports/' '__pycache__'; do
  if grep -qP "$motif" <<< "$contenu"; then
    echo "ERREUR : l'archive contient « $motif » :" >&2
    grep -P "$motif" <<< "$contenu" | head -3 >&2
    exit 1
  fi
done

# 3. Contrôle : chaque table lue par le tableau de bord est bien dans l'archive, sinon il ne se
#    lancerait pas depuis l'archive seule. La liste vient des lectures de dashboard/.
for fichier in data/raw/_SOURCES.csv \
               data/processed/table_maitresse_prefecture.csv \
               data/processed/D4_etat_troncons.csv data/processed/D4_etat_national_pct.csv \
               data/processed/geo/prefectures.geojson data/processed/geo/auto_ecoles.geojson \
               data/processed/geo/routes_classees.geojson data/processed/geo/equipements.geojson \
               data/analysis/07_indicateurs/indicateurs_07.csv \
               data/analysis/08_priorisation/classement_08.csv \
               data/analysis/10_recommandations/cartes_10.csv \
               data/analysis/A1_horizon/horizon_A1.csv \
               dashboard/app.py dashboard/notify.py dashboard/requirements.txt \
               dashboard/.streamlit/config.toml dashboard/static/armoiries-togo-ecu.svg; do
  if ! grep -qxF "$fichier" <<< "$contenu"; then
    echo "ERREUR : « $fichier » manque dans l'archive." >&2
    exit 1
  fi
done

# 4. Contrôle : toutes les tables de résultats sont là (aucune n'est oubliée par un motif -x).
csv_depot=$(find data/analysis -name '*.csv' | wc -l)
csv_archive=$(grep -c '^data/analysis/.*\.csv$' <<< "$contenu" || true)
if [ "$csv_depot" -ne "$csv_archive" ]; then
  echo "ERREUR : $csv_archive tables dans l'archive, $csv_depot dans le dépôt." >&2
  exit 1
fi

taille=$(stat -c %s "$ARCHIVE")
if [ "$taille" -gt "$TAILLE_MAX_OCTETS" ]; then
  echo "ERREUR : l'archive pèse $(du -h "$ARCHIVE" | cut -f1), au-delà des 15 Mo retenus." >&2
  exit 1
fi
if [ "$taille" -gt "$TAILLE_CONFORT_OCTETS" ]; then
  echo "⚠ L'archive dépasse 8 Mo : au défi précédent, le support a refusé 12,1 Mo." >&2
fi

echo "$ARCHIVE — $(grep -c . <<< "$contenu") entrées, $(du -h "$ARCHIVE" | cut -f1)"
