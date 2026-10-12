# Résumé de la démarche — du 01 au tableau de bord

*Comment le tableau de bord a été construit, étape par étape, et pourquoi chaque fichier a été créé.*

Un principe tient l'ensemble, tiré de [_PROCEDURE_METHODOLOGIE.txt](_PROCEDURE_METHODOLOGIE.txt) : on part de la décision à prendre, pas du graphique qu'on pourrait faire. Chaque fichier répond à une seule question et alimente le suivant. À la fin, le tableau de bord lit des tables déjà calculées et ne recalcule rien.

---

## Étape 0 — Le point de départ

- [_PROJECT.txt](../_PROJECT.txt) : l'énoncé du jury, avec le sujet, les 5 objectifs et les 6 jeux de données.
  - **Pourquoi :** c'est la référence finale. Tout ce qui suit doit répondre à ces 5 objectifs.
- [_PROCEDURE_METHODOLOGIE.txt](_PROCEDURE_METHODOLOGIE.txt) : la procédure en 14 étapes. C'est une version 2, révisée après le défi 1 (12/20) et l'étude des deux projets primés.
  - **Pourquoi :** ne pas refaire les erreurs du défi 1.

## Étape 1 — Cadrer le problème : [01_problem_definition.md](../01_problem_definition.md)

- **Pourquoi :** comprendre le problème avant de toucher aux données.
- **Ce qu'il fixe :**
  - les affirmations du sujet deviennent des hypothèses à vérifier (par exemple « moins de 4 personnes sur 10 utilisent Internet ») ;
  - chaque objectif est expliqué ;
  - l'ordre de traitement est posé : 1 et 2 (la demande et l'offre numérique), puis 3 et 4 (l'offre financière face à la population), puis 5 (les recommandations) ;
  - une première matrice de disponibilité des données, « à vérifier ».

## Étape 2 — Décider quoi mesurer : `02_decision_matrix.*`

- **Pourquoi :** fixer les indicateurs, leurs formules, leurs dénominateurs et leurs seuils **avant tout calcul**. Ainsi, impossible d'ajuster une règle après avoir vu le résultat.
- **Contenu :** pour chaque indicateur (O1-01 à O5-04), une question, une méthode, un seuil et la décision possible.
- **Les quatre fichiers :**
  - [02_decision_matrix.xlsx](../02_decision_matrix.xlsx) : le classeur ;
  - [02_decision_matrix.csv](../02_decision_matrix.csv) : la version lisible par les scripts ;
  - [02_decision_matrix_legende.csv](../02_decision_matrix_legende.csv) : l'objet du classeur ;
  - [02_decision_matrix_seuils.csv](../02_decision_matrix_seuils.csv) : la justification et la source de chaque seuil.
- **Statut :** le 02 est figé. On ne s'en écarte que par un écart déclaré, décidé avant de voir le résultat.

## Étape 3 — Vérifier que les données suffisent : [03_data_understanding.md](../03_data_understanding.md)

- **Pourquoi :** savoir si les données permettent vraiment de calculer ce que demande le 02.
- **Contenu :** une fiche par jeu de données (D1 à D6) : ce qu'il contient, ce qu'il permet de calculer, avec quelle fiabilité, et ce qu'il ne permet pas. Il attribue aussi un niveau de preuve à chaque donnée : A = mesuré, B = calculé, C = estimé.
- **Deux fichiers sont nés de ses constats :**
  - [_INVENTORY_datasets.txt](_INVENTORY_datasets.txt) : l'inventaire de tout ce qui a été téléchargé, avec sa traçabilité (URL, date, empreinte).
  - [_RECHERCHE_donnees_manquantes.md](_RECHERCHE_donnees_manquantes.md) : le journal de recherche. Le 03 a révélé des manques : la série d'usage d'Internet est presque entièrement estimée par l'UIT, et rien ne donne l'usage par territoire. D'où des recherches organisation par organisation (ARCEP, INSEED, BCEAO, enquêtes auprès des ménages), puis des décisions validées (D-1 à D-18, P, Q, R, S). Résultat : 133 fichiers complémentaires.
- **Exemple d'écart déclaré :** aucune année n'est une « stagnation » au sens du 02 (croissance de moins de 2 %). Le projet parle donc de « ralentissement ».

## Étape 4 — Préparer les données : [04_data_Preparation.md](../04_data_Preparation.md) + `prep/`

- **Pourquoi :** passer des fichiers bruts à des tables propres sans perdre, doubler ni inventer une valeur. Le 04 applique les décisions du 03 et contrôle chaque transformation (138 contrôles).
- **Les scripts, un par étape :**
  - `p01` : référentiel territorial ;
  - `p02` : population ;
  - `p03` : points de service (nettoyage, dédoublonnage) ;
  - `p04` : tables par territoire ;
  - `p05` : extraction des observatoires de l'ARCEP ;
  - `p06` : séries nationales ;
  - `p07` : enquêtes ;
  - `p08` : repères et chronologie ;
  - `p09` : contrôles.
  - [executer_tout.py](../prep/executer_tout.py) lance le tout ; [commun.py](../prep/commun.py) réunit les outils partagés.
- **Règle :** aucun ratio, aucun score à ce stade. Les tables portent les numérateurs et les dénominateurs.
- **Sortie :** `data/interim/` et `data/processed/`.

## Étapes 5 à 10 — L'analyse : à chaque document, deux scripts

À chaque document correspond un script `analyse/pXX_*.py`, qui calcule les tables dans `data/analysis/XX_*/`, et un script `analyse/figures_XX.py` (ou `cartes_06.py`), qui dessine les figures.

| Document                                                     | Question                          | Pourquoi ce fichier                                                                                                                                                                                                                                    |
| ------------------------------------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [05_data_analysis.md](../05_data_analysis.md)                 | Que montrent les données ?       | Explorer avant tout indicateur : chercher les écarts, pas les moyennes. Il teste 5 contradictions et formule les hypothèses H1 à H6.                                                                                                                |
| [06_data_spatial_analysis.md](../06_data_spatial_analysis.md) | Où ?                             | Le 05 dit*quoi*, le 06 dit *où*. Cartes à 3 mailles (objectif 3), offre rapportée à la population (objectif 4), analyse de voisinage. La distance au point formel le plus proche remplace les « zones blanches », impossibles à identifier. |
| [07_indicators.md](../07_indicators.md)                       | Combien, et dans quelle classe ?  | Applique enfin les seuils du 02, ce que le 05 et le 06 s'interdisaient. C'est le catalogue des 27 indicateurs des objectifs 1 à 4, avec leurs limites.                                                                                                |
| [08_prioritization.md](../08_prioritization.md)               | Par quels territoires commencer ? | Score de priorité des 39 préfectures, décomposé et testé en sensibilité, avec la population affichée à côté.                                                                                                                                 |
| [09_diagnostic.md](../09_diagnostic.md)                       | Pourquoi ces territoires ?        | Un décideur agit sur un déficit, pas sur un rang. Une fiche par préfecture prioritaire, plus les 25 communes signalées. Il nomme la nature du déficit et des facteurs associés, jamais des causes.                                               |
| [10_recommendations.md](../10_recommendations.md)             | Quoi faire ?                      | 12 recommandations chiffrées en habitants, avec une cible tirée du 02, des horizons à 1, 3 et 5 ans et les acteurs. Priorité absolue : les 22 communes servies uniquement par le mobile money.                                                     |

## Étape 11 — Planifier l'interface : [11_plan_visuel_dashboard.md](../11_plan_visuel_dashboard.md)

- **Pourquoi :** décider les pages, les visuels et les filtres **avant d'écrire du code**.
- **Point de départ :** la grille de notation. Au défi 1, l'ergonomie (C1) et les interactions (C3) avaient coûté le plus de points (3,5 sur 8).
- **Ce que le plan en tire :**
  - des filtres globaux ;
  - des seuils et des poids que le lecteur peut déplacer ;
  - un comparateur et des exports ;
  - une page = une question ;
  - chaque visuel porte son constat et sa limite.
- [_GARDRAILS_DASHBOARD.txt](_GARDRAILS_DASHBOARD.txt) fixe la règle d'affichage : le tableau de bord s'adresse à un décideur non technique. Pas de noms de fichiers, de scripts, de codes ou de sources sur les pages d'analyse : tout cela va sur la page Méthodologie.

## Étape 12 — Coder le tableau de bord : `dashboard/`

| Fichier                                    | Pourquoi                                                                                                                                                                                                             |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [app.py](../dashboard/app.py)               | Point d'entrée et menu en 4 groupes.                                                                                                                                                                                |
| `views/*.py`                             | Une page par fichier (11 pages), chacune répond à une question. Le dossier s'appelle`views/` et non `pages/`, parce que `pages/` fait basculer Streamlit sur son ancienne navigation (piège vu au défi 1). |
| [donnees.py](../dashboard/donnees.py)       | Lit les tables de`data/analysis/` avec cache, sans rien recalculer. Seule exception : les poids du score sur la page Priorités, avec la même formule que le 08.                                                  |
| [composants.py](../dashboard/composants.py) | Les briques partagées : chiffre clé, bandeaux Constat et Limite, sous-onglets, cartes, export CSV. Elles donnent le même gabarit à toutes les pages (critère C1).                                               |
| [theme.py](../dashboard/theme.py)           | Polices, couleurs et styles, repris en partie du défi 1.                                                                                                                                                            |
| [i18n.py](../dashboard/i18n.py)             | Le dictionnaire français/anglais, la traduction des valeurs des tables et le format des nombres.                                                                                                                    |
| [notify.py](../dashboard/notify.py)         | L'alerte Telegram à l'ouverture, reprise du défi 1.                                                                                                                                                                |
| [conding-progress.md](conding-progress.md)  | La file des corrections après le premier lancement, chacune cochée avec sa date.                                                                                                                                   |

## Étape 13 — Vérifier et livrer

- [tests/test_pages.py](../tests/test_pages.py) : ouvre les 11 pages, tous leurs onglets, dans les 2 langues. Le test échoue sur une erreur, sur un sigle ou une source visible hors de la page Méthodologie, ou sur une table manquante. Les règles d'affichage sont ainsi vérifiées automatiquement.
- `requirements.txt` et `requirements-runtime.txt` : le premier sert à tout le projet, le second au tableau de bord seul, pour une image Docker légère. [check_requirements_sync.py](../scripts/check_requirements_sync.py) vérifie qu'ils ne divergent pas.
- [Dockerfile](../Dockerfile) et [ci-cd.yml](../.github/workflows/ci-cd.yml) : lancer le tableau de bord n'importe où, avec les tests à chaque push.
- [build_presentation.py](../scripts/build_presentation.py) génère le `.pptx` pour le décideur (critère C4, le rapport), à partir des mêmes tables que le tableau de bord.
- [make_submission.sh](../scripts/make_submission.sh) construit le `.zip` à partir d'une liste blanche, qui exclut `workspace/`, `tmp/`, `.env` et les données brutes.
- [README.md](../README.md) est écrit pour le jury ; [README_technique.md](README_technique.md), pour la maintenance. Ce dernier n'est pas soumis.

---

## Le résumé en une ligne

```
_PROJECT → 01 problème → 02 contrat des indicateurs → 03 les données suffisent-elles ?
→ 04 + prep/ tables propres → 05/06 quoi, où → 07 indicateurs → 08 où commencer
→ 09 pourquoi → 10 quoi faire → 11 plan des pages → dashboard/ → tests, Docker, pptx, zip
```

## Numéros des documents et étapes de la procédure

Les numéros des documents ne suivent pas ceux de la procédure :

| Document | Étape de la procédure                           |
| -------- | ------------------------------------------------- |
| 01, 02   | 1, 2                                              |
| 03       | 3 et 4 (inventaire, compréhension des données)  |
| 04       | 5 et 6 (qualité, tables de décision)            |
| 05, 06   | 7 (exploration ; le 06 en est la partie spatiale) |
| 07       | 8 (indicateurs)                                   |
| 08       | 9 (score, priorisation)                           |
| 09       | 10 (diagnostic)                                   |
| 10       | 11 (recommandations)                              |
| 11       | 12 (tableau de bord)                              |
