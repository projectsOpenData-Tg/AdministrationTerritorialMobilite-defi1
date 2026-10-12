# README technique — Notes de développement

Document interne (non destiné au jury). Référence rapide pour le développement, le déploiement et la maintenance du tableau de bord.

## Environnement de développement

```bash
# Environnement virtuel (convention du projet)
python3.11 -m venv .venv
source .venv/bin/activate

# Dépendances complètes (analyse + dashboard)
pip install -r requirements.txt

# Dépendances dashboard seul
pip install -r dashboard/requirements.txt
```

**Deux instances Streamlit** possibles en développement :
- Port **8501** : `.venv` (instance de test principale)
- Port **8502** : instance secondaire si besoin

```bash
# Lancer sur un port spécifique
streamlit run dashboard/app.py --server.port 8502
```

## Déployer sur Streamlit Community Cloud

1. **Dépôt** : ce dépôt Git. Les CSV et GeoJSON de `data/` sont versionnés ; seuls les bruts lourds (PDF, raster WorldPop, archive EHCVM) sont exclus.
2. **Main file path** : `dashboard/app.py`
3. **Dépendances** : `dashboard/requirements.txt` (pas le `requirements.txt` racine qui contient l'environnement d'analyse complet — ydata-profiling, rasterio, JupyterLab…). Vérifier que Streamlit Cloud installe **ce** fichier (adjacent au main file).
4. **Configuration** : `.streamlit/config.toml` dans `dashboard/.streamlit/` — thème, `enableStaticServing = true` pour les fichiers de `static/`.
5. **Secrets** (facultatif) : *Settings → Secrets* au format TOML. Ils activent uniquement l'alerte de visite Telegram ; le dashboard fonctionne sans.

## Alerte de visite Telegram

Notification Telegram à chaque ouverture de session (jury ou partenaire).

- Code : `dashboard/notify.py`, appelé par `signaler_visite()` dans `app.py`
- Tourne dans le processus qui sert la page (pas un ping externe)
- **Inactif** sans `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans les secrets
- En local, le `.env` du dépôt n'est pas lu → pas de notification en dev

**Activation** dans *Settings → Secrets* :

```toml
TELEGRAM_BOT_TOKEN = "…"      # jeton @BotFather
TELEGRAM_CHAT_ID   = "…"      # identifiant de conversation
```

Pour trouver le chat ID : écrire un message au bot, puis lire `https://api.telegram.org/bot<JETON>/getUpdates` → `chat.id`.

En local : même contenu dans `.streamlit/secrets.toml` (ignoré par git ; modèle dans `secrets.toml.example`).

| Garde-fou | Raison |
| --- | --- |
| Une alerte par session | Streamlit réexécute le script à chaque interaction |
| Envoi dans un thread démon, délai 5 s | Ne retarde pas le premier rendu |
| 50 envois/jour max | Protection contre le spam |
| Aucune exception ne sort | L'alerte en panne ne bloque jamais la page |
| `urllib` standard | Aucune dépendance ajoutée |

**Vie privée** : la notification transporte l'IP déclarée et le user-agent vers Telegram. Retirer les secrets après l'évaluation.

## Tests avec Playwright

```bash
pip install playwright
playwright install chromium

# Exemple : screenshot de la page méthodologie
.venv/bin/python scripts/test_screenshot.py
```

Les scripts de test Playwright se trouvent dans le scratchpad de session ou dans `scripts/`. Ils vérifient l'absence d'exceptions (`[data-testid="stException"]`) et prennent des captures à différentes positions de scroll.

## Architecture du code

```
dashboard/
├── app.py              Navigation (st.navigation / st.Page), filtres globaux, barre latérale
├── theme.py            Palette (11 §4.1), CSS, correctif anti-barre Streamlit Cloud
├── composants.py       Composants : topbar, entete(), note_carte(), constat(), synthese(),
│                       limite(), titre_bloc(), note(), ariane(), pied()…
├── donnees.py          Lecture CSV/GeoJSON (aucun recalcul)
├── i18n.py             Internationalisation (français seul, bilingue abandonné)
├── notify.py           Alerte Telegram
├── views/              Une page par fichier
└── static/             Armoiries, logos, illustrations
```

**Principe** : le tableau de bord affiche, il ne calcule pas (11 §2). Chaque chiffre vient d'un CSV dans `data/analysis/` ou `data/processed/`.

## Fichiers de suivi (workspace/)

| Fichier | Rôle |
| --- | --- |
| `design-progress.md` | Progression du design de chaque page |
| `dev-progress.md` | Journal de développement (horodaté) |
| `design-page[1-8].md` | Spécifications de design par page |
| `validation.md` | Notes de validation |
| `_PROJECT.txt` | Contexte du projet |
| `_SCORING.txt` | Grille de notation |

## Conventions

- **Ne jamais versionner** : `.env`, `secrets.toml`, token ONU (`workspace/onu-creds.py` → env `ONU_DATAPORTAL_TOKEN`)
- **Couleurs strictes** : les couleurs de `11_tableau_de_bord.md` §4.1 (priorités, thèmes, états du réseau) ne changent pas ; le reste est libre
- **Après chaque dev/fix** : mettre à jour `workspace/dev-progress.md` avec un horodatage
- **Données EHCVM** : pas de copie/redistribution, uniquement des agrégats par zone
- **Chaque chiffre cité** provient d'un CSV produit par un script (R-19)
