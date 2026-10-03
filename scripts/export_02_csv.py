"""Vérifie 02_decision_matrix.xlsx puis exporte un CSV par feuille.

Le classeur fait foi ; les CSV de 02_decision_matrix/ ne sont jamais édités à la main (R-19).
Les contrôles reprennent la liste « Avant de figer le classeur » du plan 02_decision_matrix.md.
Le manifeste _version.csv donne la version du classeur et l’empreinte SHA-256 de chaque fichier.

Usage : python scripts/export_02_csv.py [--classeur CHEMIN] [--sortie DOSSIER]
"""
import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

from openpyxl import load_workbook

RACINE = Path(__file__).resolve().parent.parent

FEUILLES = [
    "00_Legende", "01_Matrice", "02_Hypotheses", "03_Seuils", "04_Profils",
    "05_Priorisation", "06_Donnees_requises", "07_Regles",
]
HYPOTHESES_DU_01 = [f"S{i}" for i in range(1, 6)] + [f"H{i}" for i in range(1, 13)]
ROLES = {"Calcul", "Référentiel", "Repère", "Contexte"}
COLONNES_INTERDITES = {
    "Données disponibles", "Disponibilité", "Statut de disponibilité", "Producteur",
    "Producteur / contact", "Licence", "Date de téléchargement", "Résultat",
}
RENVOIS = {
    "indicateur": (re.compile(r"\bO[1-5]-\d{2}\b"), "01_Matrice"),
    "seuil ou paramètre": (re.compile(r"\b(?:SE|PA)-\d{2}\b"), "03_Seuils"),
    "règle": (re.compile(r"\bR-\d{2}\b"), "07_Regles"),
    "profil": (re.compile(r"\bP[1-9]\b"), "04_Profils"),
    "données": (re.compile(r"\bD\d{1,2}\b"), "06_Donnees_requises"),
}


def lire(classeur):
    """Renvoie {feuille: (colonnes, lignes)}, chaque ligne étant un dict colonne → texte."""
    wb = load_workbook(classeur, read_only=True, data_only=True)
    tables = {}
    for nom in wb.sheetnames:
        rangees = list(wb[nom].iter_rows(values_only=True))
        colonnes = [str(c) for c in rangees[0]]
        lignes = [
            {c: ("" if v is None else str(v)) for c, v in zip(colonnes, r)}
            for r in rangees[1:]
            if any(v not in (None, "") for v in r)
        ]
        tables[nom] = (colonnes, lignes)
    return tables


def lire_version(tables):
    """Lit version, date et statut dans les lignes « Classeur » de 00_Legende."""
    proprietes = {
        l["Colonne"]: l["Signification"]
        for l in tables["00_Legende"][1]
        if l["Feuille"] == "Classeur"
    }
    numero, _, date = proprietes.get("Version", "").partition("—")
    return {
        "Version du classeur": numero.strip(),
        "Date de version": date.strip(),
        "Statut": proprietes.get("Statut", "").strip(),
    }


def verifier(tables):
    erreurs = []

    manquantes = [f for f in FEUILLES if f not in tables]
    if manquantes:
        return [f"Feuilles manquantes : {', '.join(manquantes)}"]

    version = lire_version(tables)
    if not re.fullmatch(r"\d+\.\d+", version["Version du classeur"]) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", version["Date de version"]
    ):
        erreurs.append("00_Legende : ligne « Classeur / Version » absente ou mal formée (attendu « 1.1 — AAAA-MM-JJ »)")
    if not version["Statut"]:
        erreurs.append("00_Legende : ligne « Classeur / Statut » absente")

    ids = {}
    for nom in FEUILLES[1:]:
        colonnes, lignes = tables[nom]
        valeurs = [l[colonnes[0]] for l in lignes]
        doublons = sorted({v for v in valeurs if valeurs.count(v) > 1})
        if doublons:
            erreurs.append(f"{nom} : identifiants en double : {', '.join(doublons)}")
        ids[nom] = set(valeurs)
        interdites = COLONNES_INTERDITES.intersection(colonnes)
        if interdites:
            erreurs.append(f"{nom} : colonnes réservées au 03 : {', '.join(sorted(interdites))}")

    # Renvois : tout identifiant cité hors de la légende doit exister dans sa feuille.
    for nom in FEUILLES[1:]:
        colonnes, lignes = tables[nom]
        for ligne in lignes:
            cle = ligne[colonnes[0]]
            for texte in ligne.values():
                for genre, (motif, cible) in RENVOIS.items():
                    for ref in motif.findall(texte):
                        if ref not in ids[cible]:
                            erreurs.append(f"{nom} / {cle} : {genre} inconnu « {ref} »")

    _, matrice = tables["01_Matrice"]
    for ligne in matrice:
        for code in re.findall(r"\b[SH]\d{1,2}\b", ligne["Hypothèses liées"]):
            if code not in ids["02_Hypotheses"]:
                erreurs.append(f"01_Matrice / {ligne['ID']} : hypothèse inconnue « {code} »")

    absentes = [h for h in HYPOTHESES_DU_01 if h not in ids["02_Hypotheses"]]
    if absentes:
        erreurs.append(f"02_Hypotheses : hypothèses du 01 absentes : {', '.join(absentes)}")
    for ligne in tables["02_Hypotheses"][1]:
        for champ in ("Indicateurs utilisés", "Confirmée si", "Infirmée si"):
            if not ligne[champ].strip():
                erreurs.append(f"02_Hypotheses / {ligne['Code']} : « {champ} » vide")

    seuils = tables["03_Seuils"][1]
    if not any(l["Déplaçable par le lecteur"] == "Oui" for l in seuils):
        erreurs.append("03_Seuils : aucun seuil déplaçable par le lecteur")
    for ligne in seuils:
        for champ in ("Justification", "Source"):
            if not ligne[champ].strip():
                erreurs.append(f"03_Seuils / {ligne['ID']} : « {champ} » vide")

    # « Indicateurs liés » de 06 doit refléter la colonne « Données » de 01_Matrice.
    attendus = {code: [] for code in ids["06_Donnees_requises"]}
    for ligne in matrice:
        for code in re.findall(r"\bD\d{1,2}\b", ligne["Données"]):
            attendus.setdefault(code, []).append(ligne["ID"])
    for ligne in tables["06_Donnees_requises"][1]:
        attendu = ", ".join(attendus.get(ligne["Code"], [])) or "—"
        if ligne["Indicateurs liés"] != attendu:
            erreurs.append(
                f"06_Donnees_requises / {ligne['Code']} : « Indicateurs liés » vaut "
                f"« {ligne['Indicateurs liés']} », attendu « {attendu} »"
            )
        # Seul un jeu « Calcul » doit alimenter des indicateurs ; les autres rôles le disent.
        role = ligne["Rôle"].split("—")[0].strip()
        if role not in ROLES:
            erreurs.append(f"06_Donnees_requises / {ligne['Code']} : rôle inconnu « {role} »")
        elif role == "Calcul" and attendu == "—":
            erreurs.append(f"06_Donnees_requises / {ligne['Code']} : rôle « Calcul » sans indicateur lié")

    return erreurs


def empreinte(chemin):
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def exporter(tables, sortie, classeur):
    sortie.mkdir(parents=True, exist_ok=True)
    version = lire_version(tables)
    manifeste = [{"Fichier": classeur.name, **version, "Lignes": "—", "SHA-256": empreinte(classeur)}]
    for nom in FEUILLES:
        colonnes, lignes = tables[nom]
        chemin = sortie / f"{nom}.csv"
        with open(chemin, "w", newline="", encoding="utf-8") as f:
            ecrivain = csv.DictWriter(f, fieldnames=colonnes)
            ecrivain.writeheader()
            ecrivain.writerows(lignes)
        manifeste.append({"Fichier": chemin.name, **version, "Lignes": len(lignes), "SHA-256": empreinte(chemin)})

    with open(sortie / "_version.csv", "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(manifeste[0]))
        ecrivain.writeheader()
        ecrivain.writerows(manifeste)
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--classeur", type=Path, default=RACINE / "02_decision_matrix.xlsx")
    parser.add_argument("--sortie", type=Path, default=RACINE / "02_decision_matrix")
    args = parser.parse_args()

    tables = lire(args.classeur)
    erreurs = verifier(tables)
    if erreurs:
        print(f"{len(erreurs)} erreur(s), aucun CSV exporté :")
        for e in erreurs:
            print(f"  - {e}")
        sys.exit(1)

    version = exporter(tables, args.sortie, args.classeur)
    for nom in FEUILLES:
        print(f"  {nom}.csv : {len(tables[nom][1])} lignes")
    print(
        f"Contrôles passés. Classeur v{version['Version du classeur']} du {version['Date de version']} "
        f"({version['Statut']}) : CSV et _version.csv écrits dans {args.sortie}"
    )


if __name__ == "__main__":
    main()
