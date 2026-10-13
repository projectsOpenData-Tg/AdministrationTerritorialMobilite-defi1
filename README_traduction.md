# Traduction du tableau de bord — note technique

Le tableau de bord est écrit en **français** (langue source) et s'affiche aussi en **anglais**, **éwé** et
**kabiyè**. Les textes sont traduits **une seule fois, avant le déploiement**, par un modèle de traduction
automatique ; l'application déployée se contente de lire les traductions dans des fichiers JSON.

## En bref

```
  pages Streamlit (texte en français)
            │
            ▼
  scripts/traduire_dashboard.py  ── 1. collecte les textes   ──►  dashboard/locales/segments_fr.json
            │                     ── 2. traduit (NLLB-200)
            ▼
  dashboard/locales/en.json, ee.json, kbp.json   (commités)
            │
            ▼
  dashboard/i18n.py : bi() lit le JSON de la langue choisie au moment de l'affichage
```

- **Aucun modèle au déploiement** : ni calcul, ni attente, ni appel réseau pour le visiteur. C'est compatible avec
  Streamlit Cloud et Heroku (512 Mo de RAM).
- **Un seul modèle pour les trois langues** : NLLB-200 (`facebook/nllb-200-distilled-600M`), exécuté avec
  CTranslate2 (version int8). Licence **CC-BY-NC 4.0** : usage non commercial seulement, ce qui convient à ce
  tableau de bord de démonstration.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `dashboard/i18n.py` | `bi()`, branchement sur Streamlit (`installer()`), sélecteur de langue (`selecteur()`) |
| `dashboard/locales/segments_fr.json` | liste des segments français à traduire (produite par le script) |
| `dashboard/locales/en.json`, `ee.json`, `kbp.json` | traductions, une entrée par segment |
| `scripts/traduire_dashboard.py` | collecte et traduction, à lancer avant un déploiement |
| `scripts/logo_barre_laterale.py` | produit le logo de la barre latérale, dont une version par langue |
| `dashboard/static/logo_barre_laterale_<langue>.svg` | logos traduits (le texte d'un logo est une image) |

## Comment l'affichage est traduit (`dashboard/i18n.py`)

**1. Choix de la langue.** Le sélecteur FR · EN · Eʋegbe · Kabɩyɛ est dans la barre latérale, sous le logo. La
langue est gardée dans `st.session_state["langue"]` et dans l'adresse (`?lang=en`, `ee` ou `kbp`) : elle reste la
même d'une page à l'autre, et un lien partagé s'ouvre dans la même langue.

**2. Aucune page n'est modifiée.** Plutôt que d'envelopper chaque chaîne dans `bi()`, `installer()` (appelé une fois
dans `app.py`) fait passer par `bi()` **tout ce que Streamlit affiche** :

- textes : `st.markdown`, `st.caption`, `st.info`… (donc aussi la barre du haut, les cartes, les notes) ;
- widgets : libellés et options des boutons, radios, pastilles, listes, curseurs, onglets. Les **valeurs** restent en
  français (la logique des pages ne change pas), seul l'**affichage** est traduit ;
- tableaux (`st.dataframe`) : en-têtes et cellules de texte ;
- graphiques Plotly : titres, axes, légendes, annotations, info-bulles, catégories des barres.

Les titres du menu et des sections sont traduits dans `app.py` avec `bi("…")`.

**3. Découpage en segments.** Un texte est découpé avant traduction ; ces éléments restent **intacts** :

- balises HTML, gras markdown `**`, sauts de ligne, puces ;
- gabarits Plotly `%{…}` et `{…}` ;
- pictogrammes, drapeau, flèches, tirets « — », « › », numéros ①②③ ;
- **blocs CSS** (`<style>`) : jamais traduits, sinon la mise en page casserait ;
- **noms propres** des données : préfectures, régions, zones, auto-écoles, routes, localités (lus dans
  `data/processed/geo/`), et la liste `_VALEURS` (Togo, Togo AI Lab, sigles…).

Chaque segment restant est cherché dans `locales/<langue>.json`. **S'il n'y est pas, il reste en français** : un
texte nouveau ou modifié s'affiche donc en français tant que le script n'a pas été relancé, sans jamais d'erreur.

## Le script de traduction (`scripts/traduire_dashboard.py`)

**1. Collecte**, de deux sources :

- les chaînes écrites dans le code (`dashboard/*.py`, `dashboard/views/*.py`), lues avec l'AST de Python ;
- les textes **réellement affichés** : le script exécute les 8 pages (`streamlit.testing`) avec la variable
  `I18N_COLLECTE`, et `bi()` note chaque segment rencontré. Cela couvre les textes construits à partir des données
  (chiffres dans une phrase, libellés de tableaux, info-bulles).

**2. Traduction** des seuls segments absents des fichiers de langue (le reste est réutilisé tel quel) :

- quelques mots sont reformulés pour le modèle (« auto-école » → « école de conduite ») sans changer le texte
  affiché en français ;
- une traduction **suspecte** (beaucoup plus longue que la source, ou mot répété en boucle) est refaite avec une
  pénalité de répétition ; si elle reste suspecte, elle est laissée vide (donc affichée en français) et marquée
  `"suspect": true` ;
- les termes d'interface anglais du dictionnaire `MANUEL` sont fixés à la main.

**3. Écriture** de `dashboard/locales/<langue>.json`. Les segments qui ne sont plus utilisés sont retirés.

### Format d'une entrée

```json
"Morts sur la route": {"texte": "Dead on the road", "relu": false}
```

- `"relu": true` : traduction vérifiée ou corrigée à la main ; **le script ne l'écrase jamais**.
- `"suspect": true` : le modèle a produit un texte jugé inventé ; l'entrée est vide et s'affiche en français.

## Mettre à jour après un changement de texte

Oui, après avoir modifié un texte d'une page, il faut **relancer le script** (sinon le nouveau texte s'affiche en
français dans les autres langues) :

```bash
pip install ctranslate2 sentencepiece huggingface_hub   # une fois, en plus de dashboard/requirements.txt
python scripts/traduire_dashboard.py                    # ne traduit que les segments nouveaux ou modifiés
python scripts/logo_barre_laterale.py                   # seulement si le texte du logo a changé
git add dashboard/locales dashboard/static && git commit -m "Traductions mises à jour"
```

- Le premier lancement télécharge le modèle (environ 600 Mo) depuis Hugging Face ; les suivants le réutilisent.
- Durée : quelques secondes à quelques minutes selon le nombre de segments nouveaux (environ 20 minutes pour tout
  traduire depuis zéro dans les trois langues, sur un processeur à 4 cœurs).
- Options : `--langues en` (une seule langue), `--collecte-seule` (lister sans traduire), `--limite 50` (essai).
- Un texte supprimé du code disparaît des fichiers de langue au lancement suivant (sauf s'il est marqué `relu`).

## Où sont le modèle et les dépendances (poste de développement)

Installés le 13/10/2026 ; rien de tout cela n'est dans le dépôt.

| Élément | Emplacement | Taille |
|---|---|---|
| `ctranslate2`, `sentencepiece`, `huggingface_hub` | environnement virtuel du projet, `.venv/` | — |
| Modèle CTranslate2 int8 (`JustFrederik/nllb-200-distilled-600M-ct2-int8`) | cache Hugging Face, `~/.cache/huggingface/hub/` | ≈ 615 Mo |
| Découpeur de mots (`sentencepiece.bpe.model` de `facebook/nllb-200-distilled-600M`) | même cache | quelques Mo |

- Le cache est **partagé par tous les projets** de l'utilisateur : supprimer `.venv/` ne supprime pas le modèle.
- Pour libérer la place : `rm -rf ~/.cache/huggingface/hub/models--JustFrederik--nllb-200-distilled-600M-ct2-int8 ~/.cache/huggingface/hub/models--facebook--nllb-200-distilled-600M`
  (le prochain lancement le retéléchargera).
- Pour placer le cache ailleurs : définir `HF_HOME=/chemin/voulu` avant de lancer le script.
- Sur un autre poste : refaire le `pip install` ci-dessus ; le premier lancement retélécharge le modèle.

### Utiliser le modèle directement

Pour traduire une phrase sans passer par la collecte des 8 pages, on peut réutiliser la classe `Traducteur` du script.
`HF_HUB_OFFLINE=1` interdit tout accès réseau : le modèle est lu dans le cache, ce qui prend environ 8 secondes.

```bash
HF_HUB_OFFLINE=1 .venv/bin/python -c "
import sys; sys.path.insert(0, 'scripts')
from traduire_dashboard import Traducteur
t = Traducteur()
for lg in ['en', 'ee', 'kbp']:
    print(lg, t.traduire(['Les accidents augmentent en volume, mais les taux baissent.'], lg))
"
```

- Langues : `en` (anglais), `ee` (éwé), `kbp` (kabiyè) ; codes NLLB dans `dashboard/i18n.py` (`CODES_NLLB`).
- `t.traduire([...], lg, prudent=True)` : passe plus lente qui limite les répétitions (celle que le script utilise
  pour les traductions suspectes).
- Pour garder un résultat dans le tableau de bord, l'écrire dans `dashboard/locales/<langue>.json` avec
  `"relu": true` (voir ci-dessous).

## Corriger une traduction à la main

1. Ouvrir `dashboard/locales/ee.json` (par exemple) et chercher le segment français.
2. Remplacer `"texte"` par la bonne traduction et passer `"relu": true`.
3. Commiter. Pas besoin de relancer le script.

## Qualité et limites

- **Anglais** : correct dans l'ensemble ; quelques termes d'interface fixés à la main. Le modèle supprime parfois
  la 2e ou la 3e phrase d'un segment et peut inventer une phrase sur un nom propre : relire les entrées nouvelles
  après chaque lancement (73 corrigées à la main le 13/10/2026).
- **Textes visibles seulement après un clic** (légende des équipements, ligne « Filtres » de la carte) : le script
  exécute les pages dans leur état par défaut et ne les collecte pas ; ils restent en français.
- **Éwé et kabiyè** : approximatifs (contresens sur le vocabulaire technique, syllabes parfois répétées). Une
  **relecture par des locuteurs** est nécessaire avant toute présentation officielle.
- Une phrase coupée par du gras (`<strong>…</strong>`) est traduite morceau par morceau : la grammaire de la
  phrase traduite peut en souffrir.
- Les nombres gardent leur format français (`8 095 498`, `3,2`) dans les textes construits par les pages.
- Le texte du logo kabiyè reste en français : la traduction proposée était trop longue pour le logo.
