"""Étape 11 : textes du 09 pour le tableau de bord (11_tableau_de_bord.md §2).

Extrait du 09 (09_diagnostic.md), sans rien calculer ni modifier le 09 ou ses sorties : le texte est repris mot pour mot (R-19).
- Les deux tableaux du 09 §10 : la conséquence retenue pour chaque verdict, et la donnée qui rendrait chaque hypothèse
  testable, reliées aux 17 vérifications et hypothèses de hypotheses_09.csv (pages 3 et 7).
- Les phrases de diagnostic du 09 §6 : 10 préfectures, Mô, 6 zones, la région Maritime, reliées aux 18 lignes de
  diagnostic_09.csv (pages 2 et 5).

Les colonnes « affichées » retirent ce que l'interface ne montre pas (codes, renvois, mentions techniques, 11 §4.2).
Les réécritures sont listées dans AFFICHAGE et PHRASES ; les contrôles vérifient qu'elles ne changent aucun nombre.

Sorties, dans data/analysis/11_tableau_de_bord/ : consequences_11.csv, phrases_11.csv, controles_11.csv.

Usage : .venv/bin/python scripts/consequences_11.py
"""
import re
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
DOCUMENT = RACINE / "09_diagnostic.md"
HYPOTHESES = RACINE / "data" / "analysis" / "09_diagnostic" / "hypotheses_09.csv"
DIAGNOSTIC = RACINE / "data" / "analysis" / "09_diagnostic" / "diagnostic_09.csv"
SORTIE = RACINE / "data" / "analysis" / "11_tableau_de_bord"

EN_TETE_CONSEQUENCES = "| Verdict | Conséquence du 02 pour le 10 |"
EN_TETE_DONNEES = "| Hypothèse | Donnée manquante |"
SOURCE = "09 §10"

# Texte du 09 → texte affiché, quand le texte du 09 contient un code ou un renvoi à un document
AFFICHAGE = {
    "La moto est la catégorie de référence de O1 et de H1": "La moto est la catégorie de référence",
    "Des mesures ciblées sur les motos (casque, permis moto) deviennent recommandables, en C. La surreprésentation est faible "
    "(indice de 1,01 à 1,10), mais elle tient sur toute la fourchette : le 10 l’écrit ainsi":
        "Des mesures ciblées sur les motos (casque, permis moto) deviennent recommandables, après vérification. "
        "La surreprésentation est faible (indice de 1,01 à 1,10), mais elle tient sur toute la fourchette",
    "Aucune recommandation ne s’y appuie ; le 13 dit quelle donnée les rendrait testables": "Aucune recommandation ne s’y appuie",
    "Accidents par préfecture (risque) ; immatriculations au lieu d’usage, si la mobilité est retenue (`05_Priorisation`)":
        "Accidents par préfecture ; immatriculations au lieu d’usage",
    "Catégorie des véhicules impliqués (O2-08)": "Catégorie des véhicules impliqués",
}
# Phrases du 09 §6 → texte affiché : mentions techniques réécrites en clair, sans changer de nombre
PHRASES = [
    (r"\s*\[SIG-\d+\]", ""),
    (r", valeur hors des bornes au 06", ", la plus grande distance du pays"),
    (r"ni comptée ni recensée", "ni agréée ni recensée"),
    (r"auto-école(s?) comptée(s?)", r"auto-école\1 agréée\2"),
    (r"(\d+) tests sur 6 : la moins sûre", r"En tête du classement dans \1 des 6 tests de robustesse : la moins sûre"),
    (r"\b6 tests sur 6\.", "En tête du classement dans les 6 tests de robustesse."),
    (r"\b(\d) tests sur 6\.", r"En tête du classement dans \1 des 6 tests de robustesse."),
]
CODES = r"\b[OS]\d(?:-\d{2})?\b|\bO\d-E\d\b|\bH\d{1,2}\b|\bSE-\d+|\bSIG-\d+|\bPA-\d+|\bR-\d+|[ÉéEe]cart \d+|§|`|✅|\ble 1[0-3]\b|, en C\b"
NOMBRE = r"\d+(?:,\d+)?"
CONFORME, ECHEC = "conforme", "échec"

controles = []


def controle(ident, intitule, attendu, mesure, ok):
    controles.append({"ID": ident, "Contrôle": intitule, "Attendu": attendu, "Mesure": mesure,
                      "Résultat": CONFORME if ok else ECHEC})


def section_suite():
    texte = DOCUMENT.read_text(encoding="utf-8")
    debut = texte.index("## 10. Suite")
    return texte[debut:texte.index("## 11.", debut)]


def tableau(section, en_tete):
    """Lignes du tableau markdown qui suit l'en-tête donné : liste de (première cellule, seconde cellule)."""
    lignes = section[section.index(en_tete):].splitlines()[2:]
    rangs = []
    for ligne in lignes:
        ligne = ligne.strip()
        if not ligne.startswith("|"):
            break
        cellules = [c.strip() for c in ligne.strip("|").split("|")]
        rangs.append((cellules[0], cellules[1].replace("✅ ", "")))
    return rangs


def codes(cellule):
    """« H3, H4, H7, H9 à H12 non testables » → [H3, H4, H7, H9, H10, H11, H12]."""
    trouves = []
    for lettre, debut, fin in re.findall(r"\b([SH])(\d+)(?:\s+à\s+[SH](\d+))?\b", cellule):
        trouves += [f"{lettre}{i}" for i in range(int(debut), int(fin or debut) + 1)]
    return trouves


def section_diagnostic():
    texte = DOCUMENT.read_text(encoding="utf-8")
    debut = texte.index("## 6. Diagnostic par territoire")
    return texte[debut:texte.index("## 7.", debut)]


def phrases_09(section):
    """Phrases du 09 §6 : (maille, territoire, rang écrit, phrase sans gras)."""
    sortie, maille = [], None
    for ligne in section.splitlines():
        ligne = ligne.strip()
        if ligne.startswith("**Résultat : préfectures en tête**"):
            maille = "Préfecture"
        elif ligne.startswith("**Résultat : zones**"):
            maille = "Zone"
        m = re.match(r"^(\d+)\. \*\*(.+?)\*\*(.*)$", ligne)
        if m and maille:
            sortie.append((maille, m.group(2), int(m.group(1)), m.group(2) + m.group(3)))
        elif ligne.startswith("**Mô**"):
            sortie.append(("Préfecture", "Mô", None, ligne.replace("**", "")))
        elif ligne.startswith("**Région Maritime**"):
            sortie.append(("Région", "Maritime", None, ligne.replace("**", "")))
    return sortie


def phrase_affichee(texte):
    for motif, remplacement in PHRASES:
        texte = re.sub(motif, remplacement, texte)
    return texte


def affiche(texte):
    return AFFICHAGE.get(texte, texte) if isinstance(texte, str) else texte


def nombres(texte):
    return set(re.findall(NOMBRE, texte)) if isinstance(texte, str) else set()


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    section = section_suite()
    h = pd.read_csv(HYPOTHESES, dtype=str)

    consequences, verdicts_09 = {}, {}
    for cellule, texte in tableau(section, EN_TETE_CONSEQUENCES):
        for code in codes(cellule):
            consequences.setdefault(code, []).append(texte)
            verdicts_09[code] = cellule
    donnees, precisions = {}, {}
    for cellule, texte in tableau(section, EN_TETE_DONNEES):
        for code in codes(cellule):
            donnees.setdefault(code, []).append(texte)
            precision = re.sub(r"^[SH\d,\sà]+", "", cellule).strip(" ,")
            if precision:
                precisions[code] = precision

    k = h[["Code", "Énoncé", "Verdict"]].copy()
    k["Conséquence retenue"] = k["Code"].map(lambda c: consequences.get(c, [None])[0])
    k["Conséquence affichée"] = k["Conséquence retenue"].map(affiche)
    k["Donnée manquante"] = k["Code"].map(lambda c: donnees.get(c, [None])[0])
    k["Précision"] = k["Code"].map(precisions)
    k["Donnée manquante affichée"] = k["Donnée manquante"].map(affiche)
    k["Source"] = SOURCE

    # --- Contrôles ---
    attendus = set(h["Code"])
    multiples = sorted(c for c, v in consequences.items() if len(v) > 1)
    controle("11-01", "Conséquences", "Les 17 codes de hypotheses_09.csv ont chacun une conséquence, et une seule ; aucun code en trop",
             f"{k['Conséquence retenue'].notna().sum()} sur {len(k)} ; en double : {multiples or 'aucun'} ; "
             f"en trop : {sorted(set(consequences) - attendus) or 'aucun'}",
             k["Conséquence retenue"].notna().all() and not multiples and set(consequences) <= attendus)
    discordants = [c for c in k["Code"] if c in verdicts_09
                   and k.loc[k["Code"] == c, "Verdict"].iloc[0].split(",")[0] not in verdicts_09[c]]
    controle("11-02", "Verdicts", "Le verdict écrit au 09 §10 est celui de hypotheses_09.csv",
             f"discordants : {discordants or 'aucun'}", not discordants)
    non_testables = k[k["Verdict"] == "non testable"]
    sans_donnee = sorted(non_testables.loc[non_testables["Donnée manquante"].isna(), "Code"])
    controle("11-03", "Données manquantes", "Chaque hypothèse non testable a sa donnée manquante ; aucun code en trop",
             f"{len(non_testables) - len(sans_donnee)} sur {len(non_testables)} ; sans donnée : {sans_donnee or 'aucune'} ; "
             f"en trop : {sorted(set(donnees) - attendus) or 'aucun'}",
             not sans_donnee and set(donnees) <= attendus)
    affichees = pd.concat([k["Conséquence affichée"], k["Donnée manquante affichée"]]).dropna()
    avec_code = sorted({t for t in affichees if re.search(CODES, t)})
    controle("11-04", "Règle des codes", "Aucun code, renvoi ou mention technique dans les colonnes affichées (11 §4.2)",
             f"textes en défaut : {avec_code or 'aucun'}", not avec_code)
    changes = [c for c, a, b in zip(k["Code"], k["Conséquence retenue"], k["Conséquence affichée"]) if not nombres(b) <= nombres(a)]
    changes += [c for c, a, b in zip(k["Code"], k["Donnée manquante"], k["Donnée manquante affichée"]) if not nombres(b) <= nombres(a)]
    inutiles = sorted(t for t in AFFICHAGE if t not in set(k["Conséquence retenue"]) | set(k["Donnée manquante"]))
    controle("11-05", "Réécritures", "Chaque réécriture vise un texte du 09 §10 et n’ajoute ni ne change aucun nombre",
             f"nombres changés : {changes or 'aucun'} ; réécritures sans texte : {len(inutiles)}", not changes and not inutiles)

    # --- Phrases de diagnostic du 09 §6 ---
    d = pd.read_csv(DIAGNOSTIC)
    f = pd.DataFrame(phrases_09(section_diagnostic()), columns=["Maille", "Territoire", "Rang écrit", "Phrase"])
    f["Phrase affichée"] = f["Phrase"].map(phrase_affichee)
    f["Source"] = "09 §6"
    attendus_d = set(zip(d["Maille"], d["Territoire"]))
    trouves_d = set(zip(f["Maille"], f["Territoire"]))
    controle("11-06", "Phrases", "Une phrase du 09 §6 pour chacune des 18 lignes de diagnostic_09.csv (10 préfectures, Mô, 6 zones, la région Maritime), et aucune autre",
             f"{len(f)} phrases ; manquantes : {sorted(attendus_d - trouves_d) or 'aucune'} ; en trop : {sorted(trouves_d - attendus_d) or 'aucune'}",
             len(f) == len(d) and attendus_d == trouves_d)
    rangs = d.assign(R=d["O5-02 rang"].fillna(d["Rang (zones ou régions)"]))
    rang_csv = {(m, t): r for m, t, r in zip(rangs["Maille"], rangs["Territoire"], rangs["R"])}
    faux = [t for m, t, r in zip(f["Maille"], f["Territoire"], f["Rang écrit"]) if pd.notna(r) and rang_csv[(m, t)] != r]
    controle("11-07", "Rangs des phrases", "Le rang écrit au 09 §6 est le rang de diagnostic_09.csv (préfectures, zones)",
             f"discordants : {faux or 'aucun'}", not faux)
    en_defaut = sorted(t for t, x in zip(f["Territoire"], f["Phrase affichée"]) if re.search(CODES, x) or "comptée" in x or "tests sur 6" in x)
    controle("11-08", "Règle des codes, phrases", "Aucun code, « comptée » ni « tests sur 6 » dans les phrases affichées (11 §4.2)",
             f"phrases en défaut : {en_defaut or 'aucune'}", not en_defaut)
    changes_f = [t for t, a, b in zip(f["Territoire"], f["Phrase"], f["Phrase affichée"]) if not nombres(b) <= nombres(a)]
    controle("11-09", "Réécritures des phrases", "Les réécritures n’ajoutent ni ne changent aucun nombre",
             f"nombres changés : {changes_f or 'aucun'}", not changes_f)

    k.to_csv(SORTIE / "consequences_11.csv", index=False)
    f.to_csv(SORTIE / "phrases_11.csv", index=False)
    kk = pd.DataFrame(controles)
    kk.to_csv(SORTIE / "controles_11.csv", index=False)

    pd.set_option("display.max_colwidth", 120)
    pd.set_option("display.width", 300)
    print(k[["Code", "Verdict", "Conséquence affichée", "Donnée manquante affichée"]].to_string(index=False))
    print(f[["Maille", "Territoire", "Phrase affichée"]].to_string(index=False))
    print(f"contrôles : {int((kk['Résultat'] == CONFORME).sum())} conformes sur {len(kk)}")
    print(kk[["ID", "Contrôle", "Mesure", "Résultat"]].to_string(index=False))


if __name__ == "__main__":
    main()
