"""Étape 04 : extrait les tableaux des PDF utiles au 04 (04_data_understanding.md, §2).

Lecture seule de data/raw/ ; sorties dans data/interim/, en format long (une valeur par ligne) :
- annuaire2024_tableaux.csv : annuaire statistique national 2024 de l'INSEED, années 2020 à 2024 :
  accidents (7.2), état du réseau en % (39.2), parc immatriculé (40.1), premières mises en circulation
  (40.2), deux-roues par centre d'immatriculation (40.3), permis par catégorie (40.4) ;
- livret02_population_2022.csv : les 47 tableaux du Livret 02 du RGPH-5 (pays, régions, Grand Lomé,
  39 préfectures), par groupe d'âges, milieu de résidence et sexe ;
- oms_profil_2023.csv : valeurs chiffrées du profil OMS du Togo (tués déclarés et estimés, répartition
  des tués par type d'usager, véhicules immatriculés, kilomètres revêtus).

Les tableaux sont lus en mode « layout » de pypdf : les colonnes y sont séparées par au moins deux
espaces, les milliers par un seul. Une cellule « - » ou « _ » reste vide, jamais 0 (R-10). Aucune
valeur n'est corrigée : les contrôles sont faits par coherence_04.py. Le script s'arrête si un
tableau n'a pas la forme attendue.

Livret 02 : quand la mise en page coupe un nombre (« 1 703     380 »), la ligne est reconstituée par
le seul découpage qui respecte les sommes du tableau (hommes + femmes = ensemble, urbain + rural =
total) ; la colonne « Lecture » la signale, et coherence_04.py l'exclut de ses propres contrôles.

Usage : .venv/bin/python scripts/extraction_pdf_04.py
"""
import re
import sys
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "raw"
SORTIE = RACINE / "data" / "interim"

# Tableau de l'annuaire : (unité, nombre de lignes attendu)
ANNUAIRE = {
    "7.2": ("nombre", 3),
    "39.2": ("%", 3),
    "40.1": ("nombre", 10),
    "40.2": ("nombre", 3),
    "40.3": ("nombre", 7),
    "40.4": ("nombre", 7),
}
# Tableau 39.2 : libellés répartis sur plusieurs lignes, lus dans l'ordre du tableau
ETAT_LIGNES = ["Routes nationales revêtues", "Routes nationales non revêtues",
               "Routes nationales revêtues et non revêtues"]
ETAT_COLONNES = [(an, etat) for an in (2020, 2021, 2022) for etat in ("Bon", "Moyen", "Mauvais", "En travaux")]
LIVRET_COLONNES = [(milieu, sexe) for milieu in ("Urbain", "Rural", "Total")
                   for sexe in ("Hommes", "Femmes", "Ensemble")]
VIDE = {"-", "_", "–", ""}
OMS_USAGERS = ["Véhicules à 4 roues", "Deux et trois-roues motorisés", "Piétons", "Cyclistes", "Autres et inconnus"]


def valeur(cellule):
    """« 7 130 » → 7130 ; « 30,45 » → 30.45 ; « - » → None. Lève ValueError si la cellule n'est pas un nombre."""
    cellule = cellule.strip()
    if cellule in VIDE:
        return None
    return float(re.sub(r"[\s  ]", "", cellule).replace(",", "."))


def est_nombre(cellule):
    try:
        valeur(cellule)
        return True
    except ValueError:
        return False


def colonnes(ligne):
    return [c for c in re.split(r"\s{2,}", ligne.strip()) if c]


def pages_layout(chemin):
    return [page.extract_text(extraction_mode="layout") or "" for page in PdfReader(chemin).pages]


def annuaire():
    chemin = BRUT / "annuaire_statistique_national_2024.pdf"
    lecteur = PdfReader(chemin)
    textes = [page.extract_text() or "" for page in lecteur.pages]
    lignes = []
    for numero, (unite, attendu) in ANNUAIRE.items():
        # Page du tableau : son titre, hors table des matières (« Signet », pointillés)
        titre = re.compile(rf"Tableau {re.escape(numero)}\s*:")
        pages = [i for i, t in enumerate(textes) if titre.search(t) and "Signet" not in t and "....." not in t]
        if len(pages) != 1:
            sys.exit(f"Annuaire, tableau {numero} : {len(pages)} pages trouvées")
        page = lecteur.pages[pages[0]].extract_text(extraction_mode="layout").splitlines()
        debut = next(i for i, l in enumerate(page) if titre.search(l))
        fin = next(i for i in range(debut, len(page)) if page[i].strip().startswith("Source"))
        bloc = [l for l in page[debut + 1:fin] if l.strip()]
        titre_long = re.sub(r"\s+", " ", page[debut].split(":", 1)[1]).strip()
        lus = []
        if numero == "39.2":
            lus = [colonnes(l)[-12:] for l in bloc if len(colonnes(l)) >= 12 and est_nombre(colonnes(l)[-1])]
            for libelle, cellules in zip(ETAT_LIGNES, lus):
                for (an, etat), c in zip(ETAT_COLONNES, cellules):
                    lignes.append([numero, titre_long, pages[0] + 1, libelle, an, etat, valeur(c), unite])
        else:
            entete = next(l for l in bloc if len(re.findall(r"\b20\d\d\b", l)) >= 3)
            annees = [int(a) for a in re.findall(r"\b20\d\d\b", entete)]
            for l in bloc[bloc.index(entete) + 1:]:
                cellules = colonnes(l)
                if len(cellules) == len(annees) + 1:
                    lus.append(cellules)
                    for an, c in zip(annees, cellules[1:]):
                        lignes.append([numero, titre_long, pages[0] + 1, cellules[0], an, "", valeur(c), unite])
        if len(lus) != attendu:
            sys.exit(f"Annuaire, tableau {numero} : {len(lus)} lignes lues au lieu de {attendu}")
    return pd.DataFrame(lignes, columns=["Tableau", "Titre", "Page", "Ligne", "Année", "Modalité", "Valeur", "Unité"])


def unite_livret(phrase):
    """« de la préfecture d’Avé » → (« préfecture », « Avé »), comme dans referentiel_prefectures.py."""
    prefecture = re.match(r"de la préfecture\s+(?:du |de la |des |de |d’|d')\s*(.+)$", phrase)
    if prefecture:
        return "préfecture", prefecture.group(1)
    if phrase == "du Togo":
        return "pays", "Togo"
    if "Grand Lomé" in phrase and "District" in phrase:
        return "district", "Grand Lomé"
    region = re.match(r"de la région\s+(?:des |de la |du |de )?\s*(.+)$", phrase)
    if region:
        return "région", region.group(1)
    sys.exit(f"Livret 02 : unité non reconnue « {phrase} »")


def coherent(v):
    """Hommes + femmes = ensemble dans chaque milieu, urbain + rural = total pour chaque sexe."""
    v = [x or 0 for x in v]
    return all(v[m] + v[m + 1] == v[m + 2] for m in (0, 3, 6)) and all(v[s] + v[s + 3] == v[s + 6] for s in (0, 1, 2))


def decoupages(jetons, n):
    """Découpages des jetons en n nombres : 1 à 3 chiffres, puis des groupes de 3 chiffres ; « - » seul."""
    if not jetons:
        return [[]] if n == 0 else []
    if n == 0:
        return []
    if jetons[0] in VIDE:
        return [[None] + reste for reste in decoupages(jetons[1:], n - 1)]
    resultats = []
    for k in range(1, len(jetons) + 1):
        tete = jetons[:k]
        if not (re.fullmatch(r"\d{1,3}", tete[0]) or (k == 1 and re.fullmatch(r"\d+", tete[0]))):
            break
        if k > 1 and not re.fullmatch(r"\d{3}", tete[-1]):
            break
        resultats += [[float("".join(tete))] + reste for reste in decoupages(jetons[k:], n - 1)]
    return resultats


def ligne_livret(l):
    """(groupe d'âges, 9 valeurs, mode de lecture), ou None si la ligne n'est pas une ligne du tableau."""
    cellules = colonnes(l)
    if not cellules or not re.match(r"^(\d|ND|Total)", cellules[0]):
        return None
    if len(cellules) == 10:
        return cellules[0], [valeur(c) for c in cellules[1:]], "colonnes"
    # Nombre coupé par la mise en page (« 1 703     380 ») : seul le découpage cohérent est retenu
    jetons = " ".join(cellules[1:]).split()
    possibles = [d for d in decoupages(jetons, 9) if coherent(d)]
    if len(possibles) != 1:
        sys.exit(f"Livret 02 : ligne illisible ({len(possibles)} découpages cohérents) : {l.strip()}")
    return cellules[0], possibles[0], "reconstituée par les sommes du tableau"


def livret02():
    lignes, tableaux = [], set()
    for numero_page, texte in enumerate(pages_layout(BRUT / "rgph5_livret02_age_milieu_prefecture.pdf"), 1):
        titre = re.search(r"Tableau\s+(\d+)\s*:\s*Effectif de la population\s+(.+?)\s+par\s+groupe", texte, re.S)
        if not titre or "....." in texte:
            continue
        numero = int(titre.group(1))
        niveau, nom = unite_livret(re.sub(r"\s+", " ", titre.group(2)))
        lus = 0
        for l in texte.splitlines():
            lue = ligne_livret(l)
            if lue:
                groupe, valeurs, lecture = lue
                groupe = "0" if groupe == "0 an" else groupe
                for (milieu, sexe), v in zip(LIVRET_COLONNES, valeurs):
                    lignes.append([numero, numero_page, niveau, nom, groupe, milieu, sexe, v, lecture])
                lus += 1
        # 0, 1-4, 5-9 … 85 et +, ND, Total : 21 lignes
        if lus != 21:
            sys.exit(f"Livret 02, tableau {numero} ({nom}) : {lus} lignes lues au lieu de 21")
        tableaux.add(numero)
    if len(tableaux) != 47:
        sys.exit(f"Livret 02 : {len(tableaux)} tableaux lus au lieu de 47")
    return pd.DataFrame(lignes, columns=["Tableau", "Page", "Niveau", "Unité", "Groupe d’âges", "Milieu", "Sexe",
                                         "Valeur", "Lecture"])


def oms():
    texte = re.sub(r"\s+", " ", PdfReader(BRUT / "oms_profil_securite_routiere_2023.pdf").pages[0].extract_text())
    nombre = r"(\d{1,3}(?: \d{3})*(?:\.\d+)?)"

    def chercher(motif):
        m = re.search(motif, texte)
        if not m:
            sys.exit(f"Profil OMS : motif introuvable « {motif} »")
        return m

    def n(x):
        return float(x.replace(" ", ""))

    lignes = []
    m = chercher(rf"Reported fatalities \(year\) {nombre} \((\d{{4}})\)")
    annee = int(m.group(2))
    lignes.append(["Tués déclarés", "", annee, n(m.group(1)), "nombre", m.group(0)])
    m = chercher(r"Reported fatalities user distribution1 ([\d%; ]+?%)\s")
    parts = [float(p.strip().rstrip("%")) for p in m.group(1).split(";")]
    if len(parts) != len(OMS_USAGERS):
        sys.exit(f"Profil OMS : {len(parts)} types d'usager au lieu de {len(OMS_USAGERS)}")
    for usager, p in zip(OMS_USAGERS, parts):
        lignes.append(["Répartition des tués déclarés par type d’usager", usager, annee, p, "%", m.group(0)])
    m = chercher(rf"WHO estimated road traffic fatalities \(95% CI\) \(year\) {nombre} \(95% CI {nombre} - {nombre}\) \((\d{{4}})\)")
    for modalite, groupe in (("valeur centrale", 1), ("borne basse", 2), ("borne haute", 3)):
        lignes.append(["Tués estimés par l’OMS", modalite, int(m.group(4)), n(m.group(groupe)), "nombre", m.group(0)])
    m = chercher(rf"WHO estimated rate per 100 000 population \(year\) {nombre} \((\d{{4}})\)")
    lignes.append(["Tués estimés pour 100 000 habitants", "", int(m.group(2)), n(m.group(1)), "pour 100 000", m.group(0)])
    m = chercher(rf"Total paved kilometers \(year\) {nombre} \((\d{{4}})\)")
    lignes.append(["Kilomètres revêtus", "", int(m.group(2)), n(m.group(1)), "km", m.group(0)])
    m = chercher(rf"Total registered vehicles \[rate per 100 000 pop\] \(year\) {nombre} \[{nombre}\] \((\d{{4}})\)")
    annee_vehicules = int(m.group(3))
    lignes.append(["Véhicules immatriculés", "Total", annee_vehicules, n(m.group(1)), "nombre", m.group(0)])
    for libelle, modalite in (("Four-wheel vehicles", "Véhicules à 4 roues"), ("Powered 2- and 3-wheelers", "Deux et trois-roues motorisés"),
                              ("Heavy trucks", "Poids lourds"), ("Buses", "Bus")):
        m = chercher(rf"{re.escape(libelle)} {nombre}")
        lignes.append(["Véhicules immatriculés", modalite, annee_vehicules, n(m.group(1)), "nombre", m.group(0)])
    m = chercher(rf"Population: {nombre}")
    lignes.append(["Population retenue par l’OMS", "", "", n(m.group(1)), "habitants", m.group(0)])
    return pd.DataFrame(lignes, columns=["Indicateur", "Modalité", "Année", "Valeur", "Unité", "Texte source"])


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    for nom, fonction in (("annuaire2024_tableaux.csv", annuaire), ("livret02_population_2022.csv", livret02),
                          ("oms_profil_2023.csv", oms)):
        df = fonction()
        df.to_csv(SORTIE / nom, index=False)
        print(f"{nom} : {len(df)} valeurs, dont {int(df['Valeur'].isna().sum())} vides")


if __name__ == "__main__":
    main()
