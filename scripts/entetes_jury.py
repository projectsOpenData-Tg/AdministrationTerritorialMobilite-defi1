"""Prépare les 13 documents d'analyse pour le jury : retire l'en-tête de version.

Un jury lit un document, pas notre journal de gel. Les lignes retirées sont celles qui ne lui
disent rien du sujet :

    **Version :** 1.3 — **Date :** 2026-10-03 — **Statut :** **figé** le 2026-10-03
    **Validé par :** [noms à compléter]

Le reste est laissé tel quel, ligne pour ligne : le titre, la ligne « Projet », la ligne
« Sources », et tout le corps du document.

**Les copies complètes restent dans `workspace/documents_complets/`**, avec leur en-tête : c'est
là que se lit l'historique des versions. Celles de la racine partent dans l'archive de soumission
(`scripts/make_submission.sh`).

Le script est **idempotent et sans perte** : un document de la racine n'est copié vers
`workspace/` que s'il porte encore son en-tête. Relancé sur des documents déjà traités, il ne
fait rien et n'écrase aucune copie complète.

Usage :
    python3 scripts/entetes_jury.py              # copie puis retire les en-têtes
    python3 scripts/entetes_jury.py --verifier   # ne modifie rien ; dit ce qui serait fait
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
COPIES = RACINE / "workspace" / "documents_complets"

DOCUMENTS = [
    "01_problem_definition.md", "02_decision_matrix.md", "03_data_inventory.md",
    "04_data_understanding.md", "05_data_preparation.md", "06_exploration.md",
    "07_indicateurs.md", "08_priorisation.md", "09_diagnostic.md", "10_recommendation.md",
    "11_tableau_de_bord.md", "A1_horizon.md",
]

#: Les deux lignes retirées. Ancrées en début de ligne : une mention de version citée dans le
#: corps d'un document ne commence jamais une ligne par « **Version :** ».
ENTETES = [re.compile(r"^\*\*Version :\*\*.*$", re.MULTILINE),
           re.compile(r"^\*\*Validé par :\*\*.*$", re.MULTILINE)]


def porte_un_entete(texte: str) -> bool:
    return any(motif.search(texte) for motif in ENTETES)


def sans_entete(texte: str) -> str:
    """Retire les lignes d'en-tête, et la ligne vide qu'elles laisseraient derrière elles."""
    for motif in ENTETES:
        texte = motif.sub("\x00", texte)
    return "\n".join(ligne for ligne in texte.split("\n") if ligne != "\x00")


def main() -> int:
    verifier = "--verifier" in sys.argv
    COPIES.mkdir(parents=True, exist_ok=True)
    traites, intacts, manquants = [], [], []

    for nom in DOCUMENTS:
        source = RACINE / nom
        if not source.exists():
            manquants.append(nom)
            continue
        texte = source.read_text(encoding="utf-8")
        if not porte_un_entete(texte):
            intacts.append(nom)
            continue
        if not verifier:
            # La copie complète n'est écrite que depuis un document qui porte encore son en-tête :
            # jamais écrasée par une version déjà allégée.
            shutil.copy2(source, COPIES / nom)
            source.write_text(sans_entete(texte), encoding="utf-8")
        traites.append(nom)

    verbe = "à traiter" if verifier else "traités"
    print(f"{len(traites)} document(s) {verbe}, {len(intacts)} déjà sans en-tête.")
    for nom in traites:
        print(f"  • {nom}")
    if manquants:
        print(f"⚠ absents de la racine : {', '.join(manquants)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
