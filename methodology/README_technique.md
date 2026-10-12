# README technique — Défi 2, Économie numérique

Document de travail, **hors soumission** : `workspace/` est ignoré par git (`.gitignore`) et absent de l'archive
(`scripts/make_submission.sh` le vérifie). Le `README.md` de la racine est celui du jury ; celui-ci couvre ce que le jury
n'a pas à lire : déploiement, alerte Telegram, archive, secrets, commandes de maintenance.

État au 29/09/2026 : branche `dev`, rien de commité depuis 35c9a6c (chaîne CI/CD, Dockerfile, alerte Telegram,
tests, archive et présentation en attente de commit).

---

## 1. Qui contient quoi

| Élément | Git | Archive (zip) | Image Docker |
| --- | :-: | :-: | :-: |
| `dashboard/`, `.streamlit/` | oui | oui | oui |
| `data/analysis/` (tables) | oui | oui | oui, sans `figures/` ni `06_spatial/cartes/` |
| `data/processed/geo/` (contours) | oui | oui | oui |
| `data/processed/` (reste), `data/interim/` | oui | oui | non |
| `prep/`, `analyse/`, `tests/`, `scripts/` | oui | oui | non |
| Documents 01 à 10, `02_decision_matrix.*` | oui | oui | `07_indicators.md` seul (lu par Sources et méthode) |
| `Togo-Economie-Numerique-Defi2.pptx` | **non suivi** (à décider) | oui | non |
| `README.md`, `LICENSE`, `requirements*.txt`, `pyproject.toml`, `Dockerfile`, `.dockerignore` | oui | oui | `requirements-runtime.txt` seul |
| `.github/workflows/ci-cd.yml` | oui | non | non |
| `11_plan_visuel_dashboard.md` | oui | **non** | non |
| `workspace/`, `tmp/` | non (ignorés) | **non** | non |
| `_PROJECT.txt` (énoncé) | oui | non | non |
| `data/raw/` (491 Mo) | en partie (449 fichiers) : les micro-données Banque mondiale sont ignorées | **non** | non |
| `.env` | non (ignoré) | **non** | **non** |

Les trois listes (`.dockerignore`, `make_submission.sh`, et dans une moindre mesure `.gitignore`) sont des **listes
blanches** pour l'image et l'archive : un nouveau fichier à la racine n'y entre que si on l'ajoute explicitement.

---

## 2. Environnement local

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # tout le projet : prep, analyses, figures, présentation, tests, lint
sudo dnf install poppler-utils           # pdftotext, pour prep/p08_references.py seulement
```

- `requirements.txt` : toutes les dépendances, versions figées.
- `requirements-runtime.txt` : le tableau de bord seul (streamlit, pandas, numpy, plotly, geopandas, shapely, pyogrio,
  pyproj). C'est ce que l'image et le job `test` de la CI installent.
- **Règle** : une dépendance du tableau de bord s'ajoute dans les deux fichiers, à la même version.
  `python scripts/check_requirements_sync.py` échoue sinon (et la CI avec).

Lancer le tableau de bord :

```bash
streamlit run dashboard/app.py --server.port 8599 --server.headless true
```

Arrêter le serveur : `ss -ltnp | grep :8599` pour lire le PID, puis `kill <PID>`. Pas de `pkill -f`.

---

## 3. Chaîne de données

```
data/raw/  ──prep/executer_tout.py──▶  data/interim/, data/processed/
           ──analyse/p05 … p10──────▶  data/analysis/<étape>/*.csv
           ──analyse/figures_*, cartes_06──▶  data/analysis/<étape>/figures/, 06_spatial/cartes/
data/analysis/ + data/processed/geo/  ──dashboard/donnees.py (lire(dossier, nom))──▶  pages
```

Rejouer :

```bash
python3 prep/executer_tout.py            # 9 étapes, p01 à p09 ; un contrôle bloquant arrête la chaîne
for s in p05_eda p06_spatial cartes_06 p07_indicateurs p08_score p09_diagnostic p10_recommandations \
         figures_05 figures_07 figures_08 figures_09 figures_10; do
  python3 analyse/$s.py || break
done
```

- Il faut `data/raw/` complet, micro-données comprises (EHCVM et Findex 2025, sous conditions de la Banque mondiale).
  Leur liste, URL et empreintes : `data/raw/_extradatas/_MANIFEST.csv` et `03_data_understanding.md`, section 12.
- Le tableau de bord **ne recalcule rien** : il lit les tables telles quelles. Seule exception : le score de priorité
  quand l'utilisateur déplace les poids (même formule que `analyse/p08_score.py`).
- Une table renommée ou supprimée dans `data/analysis/` casse une page : `test_chaque_table_lue_existe` le détecte.

---

## 4. Contrôles

```bash
ruff check .                             # erreurs de syntaxe, noms indéfinis, imports morts (E9, F)
python scripts/check_requirements_sync.py
pytest                                   # 79 tests, ~33 s (67 pour les pages, 12 pour l'alerte Telegram)
pytest -m "not lent"                     # les tests rapides seuls (déclarations, tables, alerte), sans démarrer l'application
```

`tests/test_pages.py` :

- chaque page (11) et chaque sous-onglet s'affichent sans exception, en français et en anglais (AppTest ; le rang de
  l'onglet est posé dans `session_state["<clé>_rang"]`) ;
- aucun sigle (DAB, IMF, UIT…), nom de source ou code interne (O1-01, R4a…) hors de la page Sources et méthode ;
  ARCEP et BCEAO restent permis sur Recommandations (ce sont les acteurs) ;
- les 11 pages sont déclarées dans `app.py`, le dossier des vues ne s'appelle pas `pages/` (Streamlit en ferait une
  seconde navigation) ;
- chaque `lire(dossier, nom)` du code pointe sur une table existante, les contours et `07_indicators.md` existent.

`tests/test_notify.py` (12 tests, repris du défi 1, aucun appel réseau : l'envoi est remplacé) : inerte sans les deux
variables, une alerte par session, une par nouveau visiteur, plafond de 50 par jour remis à zéro le lendemain (UTC),
IP lue en fin de `X-Forwarded-For`, message produit hors contexte HTTP, en-têtes tronqués, aucune exception ne sort.

Onglets par page, à tenir à jour dans `ONGLETS` si une page change : internet 4, marche 5, offre 4, population 4,
priorites 4, diagnostic 3, recommandations 4.

---

## 5. Image Docker

Docker n'est pas installé sur ce poste : **Podman**, mêmes commandes.

```bash
podman build -t togo-econum-defi2 .
podman run -d --name togo-econum -e PORT=8080 -p 8080:8080 togo-econum-defi2
curl -fsS http://localhost:8080/_stcore/health
podman rm -f togo-econum
```

- Base `python:3.11-slim-bookworm`, utilisateur non root `appuser`, `HOME=/app`, port lu dans `$PORT` à l'exécution
  (Heroku l'impose). Image ≈ 836 Mo, dont 7,5 Mo de données.
- L'arborescence `/app/dashboard` + `/app/data` doit rester celle du dépôt : `dashboard/donnees.py` résout ses chemins
  par `Path(__file__).resolve().parents[1]`.
- ⚠️ **Ce poste est en aarch64**, les dynos Heroku en amd64. Une image construite ici sans `--platform linux/amd64` est
  refusée par Heroku. La CI construit sur des runners amd64 : pas de souci par ce chemin.

---

## 6. CI/CD (GitHub Actions)

Fichier : `.github/workflows/ci-cd.yml`, repris du défi 1 (`../EconomyNumeric-Challenge-1`).

| Déclencheur | Jobs |
| --- | --- |
| push sur `dev` | lint, test, docker-build |
| PR vers `main` | lint, test, docker-build |
| push sur `main` (fusion d'une PR) | les trois, puis **deploy** |
| manuel (`workflow_dispatch`) | lint, test, docker-build (jamais deploy : il exige un push) |

1. **lint** : `ruff check .` et `check_requirements_sync.py`.
2. **test** : `pytest -v` avec `requirements-runtime.txt` + pytest seulement (l'environnement de production).
3. **docker-build** : build, démarrage sur `PORT=8080`, santé, page servie, les 11 routes en 200, tables des 6 dossiers
   de `data/analysis/`, contours et `07_indicators.md` présents ; échec si `/app/data/raw`, `/app/.env` ou
   `/app/workspace` existe.
4. **deploy** : vérifie le secret et la variable, `docker login` au registre Heroku, build `linux/amd64` chargé en local
   puis `docker push` (le registre refuse les manifestes OCI de buildx), `heroku container:release web`, puis attend
   jusqu'à 5 min que la production réponde sur `/_stcore/health`, puis dit si l'alerte Telegram est active (les deux
   config vars posées sur l'application) ; un simple avertissement sinon, jamais un échec. Environnement GitHub
   `production`.

Un push qui en remplace un autre annule la validation en cours, jamais un déploiement sur `main`.

L'alerte Telegram elle-même tourne dans le dyno, pas dans la CI : section 7.

### Réglages à faire une fois

1. GitHub → Settings → Secrets and variables → Actions :
   - **Secret** `HEROKU_API_KEY` : la valeur du `.env` (ou `heroku authorizations:create` pour un jeton dédié) ;
   - **Variable** `HEROKU_APP_NAME` = `togo-econum-finance-defi2` (le remote `heroku` du dépôt).
2. Heroku, si l'application a été créée avec un buildpack : `heroku stack:set container -a togo-econum-finance-defi2`.
   Sans cela, `container:release` échoue.

### Déployer

```bash
git push origin dev                      # la CI valide
# PR dev → main sur GitHub, fusion        # la CI valide puis déploie
```

### Déploiement manuel (secours, depuis ce poste)

```bash
heroku container:login
podman build --platform linux/amd64 -t registry.heroku.com/togo-econum-finance-defi2/web .
podman push --format v2s2 registry.heroku.com/togo-econum-finance-defi2/web
heroku container:release web -a togo-econum-finance-defi2
heroku logs --tail -a togo-econum-finance-defi2
```

`--format v2s2` : Podman pousse en OCI par défaut, que le registre Heroku refuse.

---

## 7. Alerte de visite Telegram

Reprise du défi 1. Une notification par **nouvelle session** du tableau de bord : nom de l'application, horodatage UTC,
adresse IP vue par le routeur Heroku, navigateur, provenance.

- Code : `dashboard/notify.py`, appelé par `signaler_visite()` dans `dashboard/app.py`, juste après le thème.
- Il tourne **dans le dyno** : un runner GitHub ne voit pas les connexions au site. La CI se contente de dire, à la fin du
  déploiement, si l'alerte est active.
- Sans `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans l'environnement, il ne fait rien : poste local, CI, image lancée
  sans ces variables. Le `.env` n'est pas lu (pas de chargement automatique) : lancer le tableau de bord en local
  n'envoie donc rien.

Activation, une fois, avec les valeurs du `.env` (sans les recopier à la main) :

```bash
heroku config:set $(grep -E '^TELEGRAM_(BOT_TOKEN|CHAT_ID)=' .env | xargs) -a togo-econum-finance-defi2
heroku config -a togo-econum-finance-defi2      # contrôle ; le dyno redémarre tout seul après config:set
```

Pour un nouveau bot : créer le bot auprès de @BotFather (jeton), lui écrire un message, puis lire
`https://api.telegram.org/bot<JETON>/getUpdates` pour y trouver `chat.id`.

| Garde-fou | Pourquoi |
| --- | --- |
| Une alerte par **session**, pas par exécution | Streamlit réexécute le script à chaque interaction : sans le drapeau de session, chaque filtre enverrait une notification |
| Envoi dans un **thread démon**, délai de 5 s | Un `api.telegram.org` lent retarderait sinon le premier rendu : le visiteur paierait la notification |
| **50 envois par jour** au maximum | Un robot qui ouvre des sessions en rafale ne doit saturer ni la conversation, ni le quota du bot |
| Aucune exception ne sort de `signaler_visite()` | Une alerte en panne ne doit jamais empêcher la page de s'afficher ; l'erreur va dans `heroku logs` (`[notify] …`) |
| `urllib` de la bibliothèque standard | Aucune dépendance ajoutée au runtime |

Vérifié le 29/09/2026 dans l'image (Podman), avec un jeton factice : deux visites, deux tentatives d'envoi, deux erreurs
404 de Telegram journalisées, pages rendues normalement ; sans les variables, aucune ligne `[notify]`.

Diagnostic en production : `heroku logs --tail -a togo-econum-finance-defi2 | grep notify`. Un `HTTP Error 401` ou
`404` signale un jeton faux ou révoqué ; `400` un `chat_id` faux ou un bot à qui personne n'a encore écrit.

⚠️ **Vie privée.** La notification transporte l'IP et l'agent utilisateur du visiteur vers une conversation Telegram.
C'est proportionné à l'usage (savoir que le jury a ouvert le tableau de bord), mais ce sont des données personnelles :
conversation privée seulement, et désactiver après l'évaluation
(`heroku config:unset TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID -a togo-econum-finance-defi2`).

---

## 8. Présentation

```bash
python3 scripts/build_presentation.py    # écrit Togo-Economie-Numerique-Defi2.pptx à la racine
```

- Aucun chiffre retapé : tout est lu dans `data/analysis/` par `dashboard/donnees.py` ; couleurs de
  `dashboard/theme.py`. Plan dans `tmp/ppt-plan.md`.
- On corrige le script, jamais le `.pptx`.
- Le `.pptx` n'est pas suivi par git : le commiter, ou l'ajouter à `.gitignore` comme l'archive.
- **Après toute régénération, reconstruire l'archive** (section 9), sinon le zip garde l'ancienne version.

---

## 9. Archive de soumission

```bash
bash scripts/make_submission.sh          # → Togo-Defi2-EconomieNumerique.zip à la racine (ignoré par git)
```

- Liste blanche dans le script : pour ajouter un fichier, l'ajouter à la commande `zip`.
- Le script échoue si l'archive contient `workspace/`, le 11, `tmp/`, `.github/`, `_PROJECT*`, `.env`, `.git/` ou
  `data/raw/`, ou si elle dépasse **20 Mo**. Dernière construction : 13 Mo, 312 entrées.
- Tester l'archive comme le jury la recevra :

```bash
d=$(mktemp -d) && unzip -q Togo-Defi2-EconomieNumerique.zip -d "$d" && (cd "$d" && pytest -q)
```

Restes visibles par le jury dans l'archive, sans effet sur le fonctionnement : les commentaires du `Dockerfile` parlent
d'Heroku ; la docstring de `scripts/build_presentation.py` cite `tmp/ppt-plan.md` et `workspace/_GARDRAILS_DASHBOARD.txt`.

---

## 10. Secrets et données sensibles

- `.env` (racine) : clé d'API Heroku, jetons Telegram, identifiants personnels. Ignoré par git, exclu de l'image (liste
  blanche du `.dockerignore`, vérifié par la CI) et de l'archive (vérifié par le script). Ne jamais le commiter, le
  copier dans un autre dossier suivi ni en afficher le contenu dans un log.
- Micro-données Banque mondiale (`data/raw/_extradatas/obj1/W2_ehcvm/`, `.../W3_findex2025/microdonnees/`) : ignorées
  par git, redistribution interdite par leurs conditions d'utilisation. Les tables agrégées qui en sont tirées
  (`data/analysis/`) sont publiables.
- Commits et pushes : faits par toi. Le shell de Claude n'a pas d'identifiants GitHub.

---

## 11. Avant de soumettre ou de fusionner dans `main`

- [ ] `ruff check .` et `python scripts/check_requirements_sync.py` passent
- [ ] `pytest` : 79 tests verts
- [ ] présentation régénérée si une table a changé, puis archive reconstruite
- [ ] archive ≤ 20 Mo, testée depuis un dossier vide
- [ ] `git status` : pas de `.env`, pas de zip, pas de `workspace/` dans ce qui part
- [ ] secret et variable posés sur GitHub avant la première fusion dans `main`
- [ ] alerte Telegram activée sur Heroku avant l'envoi du lien au jury (section 7)
