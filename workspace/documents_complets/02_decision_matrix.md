# 02 — Decision Matrix (plan du classeur)

**Projet :** Mobilité et sécurité routière au Togo
**Version :** 1.0 — **Date :** 2026-10-03 — **Statut :** plan validé ; classeur `02_decision_matrix.xlsx` v1.1 **figé le 2026-10-03**. En cas d’écart entre ce plan et le classeur, le classeur fait foi
**Sources :** `01_problem_definition.md` (v1.3, figé)

> Le 02 traduit le 01 en contrat analytique, **avant tout calcul** : pour chaque indicateur, sa formule, son seuil et la décision qu’il permet ; pour chaque hypothèse, son test ; pour le classement, sa méthode. Toute analyse sans ligne dans le 02 ne sera pas produite.
>
> Il décrit le **besoin**, pas l’existant : aucun résultat, aucune donnée réelle, aucun statut de disponibilité (cela relève du 03). Une fois figé, il n’est plus modifié. Un écart est déclaré dans l’étape concernée, décidé avant de voir le résultat.

---

## 1. Fichiers

| Fichier                              | Rôle                                                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `02_decision_matrix.xlsx`          | Le classeur : source de vérité                                                                                         |
| `02_decision_matrix/<feuille>.csv` | Un CSV par feuille, exporté du classeur par script, lu par les scripts et le tableau de bord. Jamais édité à la main |
| `02_decision_matrix/_version.csv`  | Manifeste écrit à chaque export : version, date et statut du classeur (lus dans `00_Legende`), nombre de lignes et empreinte SHA-256 du classeur et de chaque CSV |
| `02_decision_matrix.md`            | Ce plan                                                                                                                  |

---

## 2. Structure : 8 feuilles, une table par feuille

```text
02_decision_matrix.xlsx
├── 00_Legende            rôle de chaque feuille et de chaque colonne
├── 01_Matrice            une ligne par indicateur : question → calcul → seuil → décision
├── 02_Hypotheses         une ligne par hypothèse du 01 (S1–S5, H1–H12) : comment la tester
├── 03_Seuils             une ligne par seuil ou paramètre chiffré : valeur, justification, source
├── 04_Profils            les 5 profils de territoire de l’objectif 5 et leur levier
├── 05_Priorisation       la méthode de classement, paramètre par paramètre
├── 06_Donnees_requises   D1–D13 : ce qu’il faut, pas ce qu’on a
└── 07_Regles             les règles communes à toutes les feuilles
```

Chaque information n’est écrite qu’à un seul endroit ; les autres feuilles y renvoient par son identifiant (`O1-03`, `H4`, `SE-02`, `D3`, `R-05`…).

---

## 3. Feuilles et colonnes

### 00_Legende

| Colonne         | Contenu                             |
| --------------- | ----------------------------------- |
| Feuille         | Nom de la feuille                   |
| Colonne         | Nom de la colonne                   |
| Signification   | Ce qu’elle contient, en une phrase |
| Valeurs admises | Liste fermée ou format attendu     |

### 01_Matrice

Une ligne par indicateur. Elle reprend tous les indicateurs des tableaux du 01 (§3.1 à §3.4), et ajoute les 4 indicateurs calculés par l’objectif 5 : nombre de déficits par territoire (test de H9), rang de priorité (méthode dans `05_Priorisation`), population concernée, écart à la cible (par exemple le nombre d’auto-écoles manquantes pour atteindre la médiane). Sans ces lignes, la cible chiffrée et la population concernée des recommandations n’auraient pas de formule fixée d’avance. Un indicateur décliné par catégorie, sexe ou zone reste une seule ligne, la déclinaison va dans « Désagrégations ».

| Colonne                     | Contenu                                                                     | Exemple                                                                 |
| --------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| ID                          | `O<objectif>-<n°>`                                                       | `O1-09`                                                               |
| Objectif                    | O1 à O5                                                                    | `O1`                                                                  |
| Question                    | La question précise à laquelle l’indicateur répond                      | « Dans quelle catégorie la formation suit-elle le moins le parc ? »  |
| Indicateur                  | Nom court                                                                   | « Rapport immatriculations / permis, par catégorie »                 |
| Définition                 | Une phrase                                                                  | « Nouvelles immatriculations pour un nouveau permis, par catégorie » |
| Formule                     | Calcul exact                                                                | `immatriculations(cat, an) / premières délivrances(cat, an)`        |
| Unité                      | Nombre, ratio, %, km, pour 100 000 habitants…                              | ratio                                                                   |
| Sens                        | Plus haut = pire / Plus haut = mieux / Neutre                               | Plus haut = pire                                                        |
| Données                    | Codes D                                                                     | `D1, D2`                                                              |
| Maille cible                | National / zone / préfecture / tronçon                                    | National                                                                |
| Maille de repli             | Si la maille cible manque                                                   | —                                                                      |
| Temporalité                | Annuelle / mensuelle / les deux                                             | Annuelle ; mensuelle si disponible                                      |
| Désagrégations            | Sexe, âge, usager, catégorie, immatriculé ou non                         | Catégorie de véhicule                                                 |
| Condition de disponibilité | Ce qui doit exister pour calculer                                           | Séries par catégorie dans D1 et D2, nomenclature des permis           |
| Règle de repli             | Que faire si la condition n’est pas remplie                                | Comparer seulement les catégories communes aux deux sources            |
| Seuil                       | ID de`03_Seuils`, ou « aucun » pour un indicateur descriptif            | `SE-01`                                                               |
| Hypothèses liées          | Codes S / H testés avec cet indicateur                                     | `H1`                                                                  |
| Visualisation               | Type de graphique ou de carte                                               | Barres par catégorie                                                   |
| Décision possible          | Ce que le décideur peut faire de l’indicateur                             | « Cibler la catégorie la plus en retard pour la formation »          |
| Preuve attendue             | A / B / C                                                                   | B                                                                       |
| Statut                      | Socle (exigé par l’énoncé) / Si données (dépend des désagrégations) | Socle                                                                   |
| Note                        | Réserve propre à l’indicateur                                            | « Fragile par région : lieu d’enregistrement »                      |

### 02_Hypotheses

Une ligne par hypothèse du 01 (§5). Elle remplace la feuille de croisements du premier plan : chaque hypothèse est un croisement.

| Colonne                        | Contenu                                                           |
| ------------------------------ | ----------------------------------------------------------------- |
| Code                           | S1–S5, H1–H12                                                   |
| Type                           | Sujet / Écart / Lien / Cumul                                     |
| Énoncé                       | Repris du 01                                                      |
| Ordre de test                  | 1 écarts, 2 liens, 3 cumul (01, §5)                             |
| Indicateurs utilisés          | IDs de`01_Matrice`                                              |
| Méthode de test               | Comparaison de séries, de taux entre territoires, de parts, etc. |
| Confirmée si                  | Critère écrit avant le calcul                                   |
| Infirmée si                   | Critère écrit avant le calcul                                   |
| Conséquence pour la décision | Ce qui change dans les recommandations selon le résultat         |
| Limite                         | Ce que le test ne prouve pas                                      |
| Preuve attendue                | A / B / C                                                         |

### 03_Seuils

| Colonne                     | Contenu                                                                                |
| --------------------------- | -------------------------------------------------------------------------------------- |
| ID                          | `SE-<n°>` pour un seuil, `PA-<n°>` pour un paramètre de calcul                  |
| Nature                      | Seuil (déclenche « élevé » / « faible ») ou paramètre (entre dans une formule) |
| Indicateur                  | ID de`01_Matrice`, ou « transversal »                                              |
| Méthode                    | Terciles / médiane nationale / repère externe / valeur absolue                       |
| Valeur ou règle            | Ex. « tercile supérieur des 39 préfectures »                                       |
| Sens                        | Ce qui déclenche « élevé » ou « faible »                                        |
| Maille d’application       | Préfecture / zone / national                                                          |
| Justification               | Pourquoi cette méthode et cette valeur                                                |
| Source                      | Procédure, référence externe (OMS…), choix d’équipe                              |
| Déplaçable par le lecteur | Oui / non. Au moins un seuil doit l’être dans le tableau de bord                     |
| Bornes de déplacement      | Plage autorisée si déplaçable                                                       |

**Règles de choix des seuils :**

- **Terciles** à la maille préfecture uniquement (39 unités, 13 par tercile).
- **Aux 6 zones** : médiane nationale ou repère externe. Des terciles sur 6 zones n’ont pas de sens.
- **Repère absolu** ajouté quand il existe (taux de tués de l’OMS, pays voisins) : des terciles classent toujours un tiers des territoires en « élevé », même si tout le pays va bien.

**Valeurs déjà fixées :**

| ID    | Nature     | Valeur                                                                                                                               | Justification                                                                                                                                                                                                         |
| ----- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SE-01 | Seuil      | Effectif minimal pour publier un taux :**20 événements** (le numérateur : tués, ou accidents) par territoire et par année | À 20 événements, l’erreur relative d’un comptage est d’environ 22 % (1/√20). C’est la convention des statistiques sanitaires, qui signalent comme peu fiables les taux calculés sur moins de 20 événements |
| PA-01 | Paramètre | Durée de vie des véhicules pour estimer le parc par cumul : par catégorie, une valeur centrale et une fourchette                  | Fixée dans le classeur avec sa source. Sans source, fourchette large, et le taux par véhicule est affiché en fourchette, jamais en valeur unique                                                                   |

### 04_Profils

Une ligne par profil de l’objectif 5 (01, §3.5).

| Colonne                            | Contenu                                                    |
| ---------------------------------- | ---------------------------------------------------------- |
| Profil                             | Les 5 profils du 01                                        |
| Condition de déclenchement        | Combinaison de seuils (IDs`SE-`)                         |
| Type de déficit                   | Réseau / Formation / Surveillance / Données              |
| Levier                             | Entretien, formation, contrôle, sensibilisation, collecte |
| Acteur probable                    | Ministère, organisme, collectivité                       |
| Cible type                         | Ex. « atteindre la médiane nationale »                  |
| Calcul de la population concernée | Formule                                                    |
| Horizon                            | 1 / 3 / 5 ans                                              |
| Indicateur de suivi                | ID de`01_Matrice`                                        |
| Réserve                           | Ce qui reste incertain                                     |

Chaque recommandation suit la chaîne du 01 : constat → ampleur → territoire → déficit associé → action, avec acteur, cible chiffrée, population concernée, horizon, indicateur de suivi, niveau de preuve et réserve.

### 05_Priorisation

Une ligne par paramètre de la méthode de classement.

| Colonne       | Contenu                        |
| ------------- | ------------------------------ |
| Paramètre    | Voir la liste ci-dessous       |
| Choix         | La valeur retenue              |
| Justification | Pourquoi                       |
| Référence   | Procédure (étape) ou 01 (§) |

**Paramètres à fixer :**

| Paramètre               | Choix par défaut                                                                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dimensions               | Risque, réseau, formation. Mobilité seulement si ses données reflètent le lieu d’usage ; sinon affichée à part, en C (01, §3.1)                                     |
| Indicateur par dimension | Un indicateur principal par dimension, ID de`01_Matrice`                                                                                                                  |
| Normalisation            | Rang percentile, pas Min-Max : un seul extrême écrase le Min-Max                                                                                                          |
| Agrégation              | Somme des rangs, poids égaux par défaut. Un poids égal est déjà une pondération : il est testé comme les autres                                                      |
| Score composite          | Seulement si l’exploration le justifie (procédure, étape 09)                                                                                                             |
| Intensité et volume     | Le classement porte sur les taux. La population concernée est affichée à côté. À tercile égal, le territoire qui compte le plus d’habitants concernés passe devant |
| Sensibilité             | Trois tests : au moins trois jeux de pondérations ; normalisation alternative ; retrait du point extrême (probablement le Grand Lomé)                                    |
| Stabilité               | Classement stable si les territoires en tête changent de moins de 20 % d’un test à l’autre                                                                              |
| Si instable              | Présentation par profil (`04_Profils`) plutôt que par rang                                                                                                              |
| Valeurs manquantes       | Territoire « non déterminable », jamais classé favorable, affiché à part                                                                                              |
| Combinaison des profils  | P1 et P2 cumulables, le déficit le plus marqué en premier ; P3, P4, P6 exigent réseau et formation renseignés ; sinon P5 pour la dimension manquante                    |
| Territoires en tête     | Nombre à fixer dans le classeur, avec la population qu’ils représentent                                                                                                  |
| Sortie                   | Classement décomposé par dimension, population concernée, carte                                                                                                          |

### 06_Donnees_requises

Le besoin uniquement. Disponibilité, producteur, licence et date de téléchargement vont dans l’inventaire du 03.

| Colonne                | Contenu                                                                                       |
| ---------------------- | --------------------------------------------------------------------------------------------- |
| Code                   | D1–D13                                                                                       |
| Données               | Nom attendu                                                                                   |
| Rôle                  | Calcul / Référentiel / Repère / Contexte. Seul un jeu « Calcul » a des indicateurs liés |
| Variables nécessaires | Colonnes précises                                                                            |
| Période attendue      | Années                                                                                       |
| Maille cible           | National / zone / préfecture / tronçon / point                                              |
| Maille de repli        | Si la maille cible manque                                                                     |
| Type                   | Série, géométrie, liste, attribut                                                          |
| Objectifs              | O1–O5                                                                                        |
| Indicateurs liés      | IDs de`01_Matrice`                                                                          |
| Bloquant               | Oui / non                                                                                     |
| Piège connu           | Repris du 01                                                                                  |

| Code | Données                                                                                                                   |
| ---- | -------------------------------------------------------------------------------------------------------------------------- |
| D1   | Immatriculations par catégorie                                                                                            |
| D2   | Permis délivrés par catégorie (premières délivrances)                                                                 |
| D3   | Accidents, blessés, tués                                                                                                 |
| D4   | État du réseau                                                                                                           |
| D5   | Tracé du réseau classé                                                                                                  |
| D6   | Auto-écoles                                                                                                               |
| D7   | Population (INSEED : RGPH-5 2022, projections),**avec la structure par âge** pour la population en âge de conduire |
| D8   | Référentiel administratif (limites et codes) —**bloquant**                                                        |
| D9   | Benchmark externe (OMS, pays voisins)                                                                                      |
| D10  | Comptages de trafic                                                                                                        |
| D11  | Chronologie des réformes                                                                                                  |
| D12  | Enquête sur les déplacements des ménages                                                                                |
| D13  | Lieux candidats et grille de population                                                                                    |

### 07_Regles

| Colonne     | Contenu                                                             |
| ----------- | ------------------------------------------------------------------- |
| Code        | `R-<n°>`                                                         |
| Domaine     | Territoire, temps, données, tronçons, preuve, affichage, document |
| Règle      | Énoncé court                                                      |
| Application | Feuilles ou indicateurs concernés                                  |
| Exception   | Cas particuliers                                                    |
| Référence | § du 01 ou étape de la procédure                                 |

Les règles de seuil et de classement sont dans `03_Seuils` et `05_Priorisation`, pas ici.

| Code | Domaine     | Règle                                                                                                                                                                                                                                                                                                   |
| ---- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R-01 | Territoire  | Brique commune : la préfecture. Toute donnée est rattachée à une préfecture avant d’être agrégée                                                                                                                                                                                                |
| R-02 | Territoire  | Lecture régionale par défaut en 6 zones, pour tous les objectifs dès que les données le permettent. La vue en 5 régions est toujours disponible par agrégation, car l’énoncé demande « par région ». Une source qui ne sépare pas le Grand Lomé est lue en 5 régions, en repli étiqueté |
| R-03 | Territoire  | Le Grand Lomé (Golfe + Agoè-Nyivé) est séparé de la Maritime hors Grand Lomé dans les 6 zones                                                                                                                                                                                                      |
| R-04 | Territoire  | Chaque source est étiquetée : sa « Maritime » inclut-elle le Grand Lomé ? La somme des zones doit égaler le total national                                                                                                                                                                         |
| R-05 | Temps       | Année de référence des croisements : 2022 par défaut ; la plus récente si les données la couvrent et que sa population est disponible ; sinon l’année la plus proche, écart affiché                                                                                                            |
| R-06 | Temps       | Le dénominateur population est de la même année que le numérateur : projection INSEED de cette année si elle existe ; sinon l’année la plus proche, affichée (« population 2022 »)                                                                                                             |
| R-07 | Temps       | Annuelle pour les séries longues ; mensuelle si la source le permet                                                                                                                                                                                                                                     |
| R-08 | Temps       | En mensuel : volumes et indice de saisonnalité seulement (accidents par jour du mois / moyenne journalière de l’année, pour neutraliser les mois de 28 à 31 jours). Aucun taux mensuel par habitant ou par véhicule, aucun classement territorial mensuel                                          |
| R-09 | Données    | Petits volumes : sous l’effectif minimal (`SE-01`), le taux est calculé sur 3 ans cumulés ; s’il reste sous le seuil, le volume est affiché et le taux est marqué « peu fiable » et n’est jamais utilisé seul pour classer                                                                   |
| R-10 | Données    | Valeur manquante ≠ zéro. Jamais imputée. Affichée « non renseigné »                                                                                                                                                                                                                               |
| R-11 | Données    | Dénominateur du taux par véhicule, dans l’ordre : parc roulant s’il est publié ; parc immatriculé (B) ; cumul des immatriculations sur la durée de vie`PA-01` (C, affiché en fourchette). National seulement, sauf parc territorial fiable                                                     |
| R-12 | Données    | Si l’activité des auto-écoles n’est pas connue : on compte les agréées, l’offre de formation est étiquetée C « activité non vérifiée », et cette réserve est reprise dans toute recommandation qui s’appuie dessus                                                                       |
| R-13 | Données    | Causes d’accidents montrées seulement si déclarées, étiquetées « cause déclarée », avec la part de non-renseignés                                                                                                                                                                             |
| R-14 | Tronçons   | Un tronçon non évalué n’est pas en bon état : il est compté dans la part non évaluée                                                                                                                                                                                                             |
| R-15 | Tronçons   | Tronçon à cheval sur deux territoires : découpage par intersection géographique, sinon rattachement au territoire du plus long segment                                                                                                                                                               |
| R-16 | Géométrie | Longueurs, surfaces et distances en projection métrique UTM zone 31N                                                                                                                                                                                                                                    |
| R-17 | Preuve      | Niveaux A mesuré, B calculé, C estimé. Une recommandation portée par du C déclenche une vérification, pas un investissement                                                                                                                                                                        |
| R-18 | Affichage   | Aucune recommandation sans territoire, cible chiffrée, population concernée, horizon, acteur, indicateur de suivi, niveau de preuve et réserve                                                                                                                                                        |
| R-19 | Affichage   | Aucun chiffre retapé : le tableau de bord et le rapport lisent les CSV exportés du classeur                                                                                                                                                                                                            |
| R-20 | Document    | Le 02 figé n’est plus modifié. Un écart est déclaré dans l’étape concernée, décidé avant de voir le résultat                                                                                                                                                                                 |

---

## 4. Correspondance avec le 01

| Section du 01            | Feuille du 02                                      |
| ------------------------ | -------------------------------------------------- |
| §2.1 Décision          | `05_Priorisation`, `04_Profils`                |
| §2.3 Cadre              | `07_Regles` (R-01 à R-08)                       |
| §3.1 à §3.4 Objectifs | `01_Matrice`                                     |
| §3.5 Objectif 5         | `04_Profils`, `05_Priorisation`                |
| §4 Définitions         | Colonne « Définition » de`01_Matrice`         |
| §5 Hypothèses          | `02_Hypotheses`                                  |
| §7 Données attendues   | `06_Donnees_requises`                            |
| §8 Limites              | `07_Regles`, colonnes « Note » et « Limite » |
| §9 Questions ouvertes   | Hors 02 : elles sont traitées par le 03           |

---

## 5. Avant de figer le classeur

- [ ] Chaque indicateur des tableaux du 01 (§3.1 à §3.4) et les 4 indicateurs de l’objectif 5 ont une ligne dans `01_Matrice`.
- [ ] Chaque hypothèse S1–S5, H1–H12 a une ligne dans `02_Hypotheses`, avec ses critères « confirmée si » et « infirmée si ».
- [ ] Chaque seuil cité existe dans `03_Seuils`, avec justification et source.
- [ ] Au moins un seuil est déplaçable par le lecteur.
- [ ] Chaque code D cité existe dans `06_Donnees_requises`.
- [ ] Aucune colonne de disponibilité, de licence ou de résultat.
- [ ] Les CSV sont exportés et identiques au classeur.

**Prochaine étape :** `03` — inventaire des données : pour chaque code D, ce qui existe réellement, à quelle maille, sur quelles années, avec quelle fiabilité.
