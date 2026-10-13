# Technical README — Developer Notes

Internal document (not intended for the jury). Quick reference for development, deployment and maintenance of
the dashboard: the project structure, how the analysis was done, how each objective from the brief is solved
and by which files, which data files feed the dashboard, and the constraints used to build it.

## Project structure

The repo splits into two kinds of folders (`workspace/_GUARD_RAILS_REPO.txt`):

**Data-engineering workspace** (working process, not submitted):

- `workspace/` — design specs, progress logs, validation notes, internal guardrails
- `methodology/` — methodology procedure, dashboard mockup, dashboard-content guardrails
- `02_decision_matrix/` — the decision-matrix workbook, as CSV sheets
- `tmp/` — scratch validation notes (checked against data and procedure before being applied anywhere)

**Submission** (jury-facing deliverables):

- `01_problem_definition.md` … `11_tableau_de_bord.md`, `A1_horizon.md` — the analytical documents (see pipeline
  below)
- `notebooks/` — exploratory notebooks backing documents 04 and 06, one per objective (`04_O1.ipynb`…`06_O5.ipynb`)
- `scripts/` — Python scripts that compute every figure cited in the documents and written to `data/analysis/`
- `dashboard/` — the Streamlit app (see [Code architecture](#code-architecture))
- `data/` — raw, interim, processed, analysis and reference datasets (see [Data](#data-from-raw-files-to-dashboard))
- `Togo-Mobilite-Securite-Routiere-Defi1.pptx` — the 10-slide report
- `Togo-Defi1-MobiliteSecuriteRoutiere.zip` — packaged submission archive

## How the analysis was done — the document pipeline

Each numbered document answers one question, is frozen once validated, and feeds the next one:

| #  | Document             | Question it answers                                                                         |
| -- | -------------------- | ------------------------------------------------------------------------------------------- |
| 01 | Problem definition   | What does the brief actually ask, and what decision must the dashboard support?             |
| 02 | Decision matrix      | For each indicator: formula, threshold, decision it enables. Frozen before any computation. |
| 03 | Data inventory       | For each need (D1–D13), what exists, where, under what license, at what granularity.       |
| 04 | Data understanding   | Are the available data reliable and usable enough to compute the 02's indicators?           |
| 05 | Data preparation     | Can these data be joined honestly, and which tables carry the decision?                     |
| 06 | Exploration          | What do the prepared data say, before fixing any indicator? Where are the gaps?             |
| 07 | Indicators           | What is each of the 02's 32 indicators worth, and what is each one based on?                |
| 08 | Prioritization       | Which prefectures/regions are priorities, on which lever, and does the ranking hold?        |
| 09 | Diagnostic           | Why are these territories at the top? Which of the 02's hypotheses hold?                    |
| 10 | Recommendations      | What to do, where, for how many people, and in what order?                                  |
| 11 | Dashboard            | What should the dashboard show, page by page, and with which data?                          |
| A1 | Horizon 2031 (annex) | If nothing changes, where will each territory be in 1/3/5 years, and what effort is needed? |

Documents 12 (validation) and 13 (final report) were **not written, for lack of time**: the dashboard's
Methodology page (11 §5) and the PowerPoint cover what they would have carried.

## Objectives → how each is solved

The brief (`workspace/_PROJECT.txt`) sets five objectives. Each one is carried through the same pipeline:
understood in 04, explored in 06, measured in 07/08, explained in 09, acted on in 10, then displayed on the
dashboard.

| Objective                                                              | Understood / explored in                   | Measured / explained in                        | Displayed on                                                      |
| ---------------------------------------------------------------------- | ------------------------------------------ | ---------------------------------------------- | ----------------------------------------------------------------- |
| O1 — Evolution of registered vehicles and driving licenses            | `notebooks/04_O1.ipynb`, `06_O1.ipynb` | `07_indicateurs.md` (`indicateurs_07.py`)  | Évolutions et constats (Mobilité tab)                           |
| O2 — Road safety: accidents, injuries, deaths                         | `04_O2.ipynb`, `06_O2.ipynb`           | `07_indicateurs.md`, `09_diagnostic.md`    | Évolutions et constats (Sécurité routière tab), Vue nationale |
| O3 — Road network condition, by segment and by region                 | `04_O3.ipynb`, `06_O3.ipynb`           | `08_priorisation.md` (`D4_etat_troncons`)  | Carte du réseau et des auto-écoles, Comparaison territoriale    |
| O4 — Map of the classified network and driving schools vs. population | `04_O4.ipynb`, `06_O4.ipynb`           | `08_priorisation.md`, `A1_horizon.md`      | Carte du réseau et des auto-écoles, Horizon 2031                |
| O5 — Targeted recommendations                                         | `04_O5.ipynb`, `06_O5.ipynb`           | `09_diagnostic.md`, `10_recommendation.md` | Priorités, Recommandations                                       |

## Data: from raw files to dashboard

`data/raw/` holds the original downloads (`_SOURCES.csv` is the source register) → scripts in `scripts/` clean
and join them into `data/interim/` and `data/processed/` → each document's own figures are written to
`data/analysis/<document>/` → the dashboard reads only those CSVs and recomputes nothing (R-19).

`03_data_inventory.md` tracks 13 data needs (D1–D13), each tied to the objective(s) it serves:

| Need | Content                                              | Objective(s)    | Key source files                                                            |
| ---- | ---------------------------------------------------- | --------------- | --------------------------------------------------------------------------- |
| D1   | Registrations by category                            | O1, O2          | `parc_immatricule_par_type_1/2.csv`, `transports_statistiques_cles.csv` |
| D2   | Licenses issued by category                          | O1              | `permis_par_categorie.csv`                                                |
| D3   | Accidents, injuries, deaths                          | O2, O5          | `accidents_police_gendarmerie.csv`, OMS and annuaire PDFs                 |
| D4   | Road network condition                               | O3, O5          | `etat_reseau_routier.csv`                                                 |
| D5   | Classified network layout                            | O2, O3, O4, O5  | `routes_classees.csv` (+ metadata), geolocated segments                   |
| D6   | Driving schools                                      | O4, O5          | `auto_ecoles.csv` (+ metadata)                                            |
| D7   | Population                                           | O1, O2, O4, O5  | RGPH 2022, demographic projections, WPP 2024                                |
| D8   | Administrative boundaries                            | O4 (+ all maps) | HDX boundaries,`data/reference/referentiel_prefectures.csv`               |
| D9   | External benchmark (WHO)                             | O2              | `oms_tues_pour_100000.json`                                               |
| D10  | Traffic counts (context)                             | O2, O3          | `transports_statistiques_cles.csv`                                        |
| D11  | Reform timeline (context)                            | O1, O2          | `data/reference/chronologie_reformes.csv`                                 |
| D12  | Household travel survey (context, not used in O1/O2) | O1, O2          | `ehcvm_2021_2022_csv.zip`, `dhs_possession_moto_velo_region.json`       |
| D13  | Candidate sites and population grid                  | O4, O5          | HDX locality list, WorldPop grid                                            |

Full detail — license, granularity, covered years, gaps and fallback rule for each need — is in
`03_data_inventory.md` §1.

## Constraints used to build the dashboard

From the decision matrix's frozen rules (`02_decision_matrix.md` §3, R-01…R-20) and the dashboard-content
guardrails (`methodology/_GARDRAILS_DASHBOARD.txt`):

- **No recalculation (R-19)**: the dashboard only reads CSVs already produced by the scripts; it never retypes
  or recomputes a figure.
- **Decisions before results (R-20)**: thresholds, weights and methods are fixed in the 02 *before* seeing any
  output; a deviation is logged in the step where it is found.
- **Evidence levels (R-17)**: A = measured, B = calculated, C = estimated. A recommendation resting on a C
  figure triggers a verification, not an investment — and must say so (R-18: every recommendation needs a
  territory, a numeric target, the population concerned, a horizon, an owner, a tracking indicator, an
  evidence level and a caveat).
- **Prefecture as the base territorial unit (R-01)**; regional reading defaults to 6 zones with Grand Lomé
  split out of Maritime (R-02, R-03); the 5-region view is always available by aggregation.
- **Fixed color palette**: the priority / theme / network-state colors defined in `11_tableau_de_bord.md` §4.1
  do not change; everything else (page background, general styling) is free.
- **Decision-maker language on the main pages**: no CSV or script file names, no pipeline step numbers
  (05/06/07/08…), no internal variable or code names on the content-facing pages — only KPIs, territorial gaps,
  exposed population, priority/confidence level and recommended action. That technical detail lives only on
  the Methodology page.
- **French-only UI**: bilingual FR/EN was abandoned (`dashboard/i18n.py`); the interface and its content stay
  French, and are translated separately for display — see `README_traduction.md`.
- **No redistribution of EHCVM microdata**: aggregates by zone only, never the raw household records.
- **Never versioned**: `.env`, `secrets.toml`, the UN data-portal token
  (`workspace/onu-creds.py` → env `ONU_DATAPORTAL_TOKEN`).

## Development environment

```bash
# Virtual environment (project convention)
python3.11 -m venv .venv
source .venv/bin/activate

# Full dependencies (analysis + dashboard)
pip install -r requirements.txt

# Dashboard-only dependencies
pip install -r dashboard/requirements.txt
```

**Two Streamlit instances** possible during development:

- Port **8501**: `.venv` (main test instance)
- Port **8502**: secondary instance if needed

```bash
# Run on a specific port
streamlit run dashboard/app.py --server.port 8502
```

## Deploying to Streamlit Community Cloud

1. **Repository**: this Git repo. The CSV and GeoJSON files in `data/` are versioned; only the heavy raw files
   (PDFs, the WorldPop raster, the EHCVM archive) are excluded.
2. **Main file path**: `dashboard/app.py`
3. **Dependencies**: `dashboard/requirements.txt` (not the root `requirements.txt`, which holds the full
   analysis environment — ydata-profiling, rasterio, JupyterLab…). Check that Streamlit Cloud installs
   **this** file (the one adjacent to the main file).
4. **Configuration**: `.streamlit/config.toml` in `dashboard/.streamlit/` — theme, `enableStaticServing = true`
   for the files under `static/`.
5. **Secrets** (optional): *Settings → Secrets*, TOML format. They only enable the Telegram visit alert; the
   dashboard works without them.

## Telegram visit alert

A Telegram notification on every session opened (jury or partner).

- Code: `dashboard/notify.py`, called from `signaler_visite()` in `app.py`
- Runs inside the process serving the page (not an external ping)
- **Inactive** without `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the secrets
- Locally, the repo's `.env` is not read → no notification in dev

**Enabling it** in *Settings → Secrets*:

```toml
TELEGRAM_BOT_TOKEN = "…"      # token from @BotFather
TELEGRAM_CHAT_ID   = "…"      # chat identifier
```

To find the chat ID: send a message to the bot, then read
`https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id`.

Locally: same content in `.streamlit/secrets.toml` (git-ignored; template in `secrets.toml.example`).

| Safeguard                            | Reason                                            |
| ------------------------------------ | ------------------------------------------------- |
| One alert per session                | Streamlit re-runs the script on every interaction |
| Sent from a daemon thread, 5 s delay | Does not delay the first render                   |
| 50 sends/day max                     | Protection against spam                           |
| No exception ever bubbles up         | A broken alert never blocks the page              |
| Standard`urllib`                   | No added dependency                               |

**Privacy**: the notification carries the declared IP and user-agent to Telegram. Remove the secrets after
the evaluation.

## Testing with Playwright

```bash
pip install playwright
playwright install chromium

# Example: screenshot of the methodology page
.venv/bin/python scripts/test_screenshot.py
```

Playwright test scripts live in the session scratchpad or in `scripts/`. They check for the absence of
exceptions (`[data-testid="stException"]`) and take screenshots at different scroll positions.

## Code architecture

```
dashboard/
├── app.py              Navigation (st.navigation / st.Page), global filters, sidebar
├── theme.py            Palette (11 §4.1), CSS, Streamlit Cloud top-bar override fix
├── composants.py       Components: topbar, entete(), note_carte(), constat(), synthese(),
│                       limite(), titre_bloc(), note(), ariane(), pied()…
├── donnees.py          CSV/GeoJSON reading (no recomputation)
├── i18n.py             Internationalization (French only; bilingual mode abandoned)
├── notify.py           Telegram alert
├── views/              One page per file (see table in "Objectives" above)
└── static/             Coat of arms, logos, illustrations
```

**Principle**: the dashboard displays, it does not compute (11 §2). Every figure comes from a CSV in
`data/analysis/` or `data/processed/`.

## Tracking files (workspace/)

| File                    | Role                          |
| ----------------------- | ----------------------------- |
| `design-progress.md`  | Design progress for each page |
| `dev-progress.md`     | Development log (timestamped) |
| `design-page[1-8].md` | Per-page design specification |
| `validation.md`       | Validation notes              |
| `_PROJECT.txt`        | Project brief                 |
| `_SCORING.txt`        | Scoring grid                  |

## Conventions

- **After every dev session or fix**: update `workspace/dev-progress.md` with a timestamp, so collaborators
  can see what already works and what was already fixed.
- **Every figure cited** comes from a CSV produced by a script (R-19) — never a number typed by hand.
