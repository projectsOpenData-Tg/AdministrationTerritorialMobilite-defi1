"""Traduit les textes du tableau de bord, une fois, avant le déploiement (méthode « traduire avant le déploiement »).

1. Collecte : les textes que le tableau de bord affiche, de deux sources —
   - les chaînes écrites dans le code (dashboard/*.py et dashboard/views/*.py), lues par l'AST ;
   - les textes réellement affichés, enregistrés en exécutant les 8 pages (I18N_COLLECTE, voir dashboard/i18n.py),
     ce qui couvre les textes construits à partir des données (libellés, info-bulles, tableaux).
   Chaque texte est découpé en segments par i18n.segments() : HTML, markdown et gabarits %{…} restent hors traduction.
2. Traduction des segments absents (ou modifiés) avec un seul modèle pour toutes les langues : NLLB-200
   (facebook/nllb-200-distilled-600M, licence CC-BY-NC 4.0 — usage non commercial, ce tableau de bord est une démo).
   Moteur : CTranslate2 (version int8 du modèle), sinon transformers.
3. Écriture de dashboard/locales/<langue>.json : {"segment français": {"texte": "...", "relu": false}}.
   Une entrée marquée "relu": true (corrigée à la main) n'est jamais écrasée.

Usage : python scripts/traduire_dashboard.py [--langues en ee kbp] [--collecte-seule] [--limite N]
Dépendances (hors requirements du tableau de bord) : ctranslate2 sentencepiece huggingface_hub, ou transformers torch.
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DASH = RACINE / "dashboard"
sys.path.insert(0, str(DASH))
import i18n  # noqa: E402

LOCALES = DASH / "locales"
PAGES = ["views/vue_nationale.py", "views/comparaison.py", "views/evolutions.py", "views/carte.py",
         "views/priorites.py", "views/recommandations.py", "views/horizon.py", "views/methodologie.py"]
# Textes affichés hors du flux Streamlit : logo de la barre latérale (image SVG produite par logo_barre_laterale.py)
EXTRAS = ["Mobilité & sécurité routière", "Tableau de bord territorial d'aide à la décision"]


IDENTIFIANT = re.compile(r"[a-z0-9_./:%-]+|[A-Z0-9_-]+")   # clés, codes, noms de colonnes techniques


# --- 1. Collecte -------------------------------------------------------------------------------------------------
def chaines_du_code() -> set[str]:
    out = set()
    fichiers = [p for p in DASH.glob("*.py") if p.name not in ("i18n.py", "theme.py")]   # theme.py : CSS + list((DASH / "views").glob("*.py"))
    for f in fichiers:
        arbre = ast.parse(f.read_text(encoding="utf-8"))
        docstrings = {id(n.body[0].value) for n in ast.walk(arbre)
                      if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                      and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        # Morceaux de f-strings exclus : le texte complet n'existe qu'à l'affichage (collecté par chaines_affichees)
        dans_fstring = {id(c) for n in ast.walk(arbre) if isinstance(n, ast.JoinedStr) for c in n.values}
        for n in ast.walk(arbre):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings | dans_fstring:
                v = n.value.strip()
                if (IDENTIFIANT.fullmatch(v) or v.endswith((".py", ".csv", ".svg", ".png", ".geojson", ".json"))
                        or v.startswith(("#", "rgba", "views/", ".", "[", "div.", "st-key", ":material"))
                        or "data-testid" in v):
                    continue
                out.update(i18n.segments(n.value))
    return out


EXECUTEUR = r'''
import sys
from streamlit.testing.v1 import AppTest
app = sys.argv[1]
for page in sys.argv[2:]:
    at = AppTest.from_file(app, default_timeout=300)
    at.run()
    if page != "views/vue_nationale.py":
        at.switch_page(page).run()
    print(page, "exceptions:", len(at.exception), flush=True)
'''


def chaines_affichees() -> set[str]:
    with tempfile.TemporaryDirectory() as d:
        journal, script = Path(d) / "vus.jsonl", Path(d) / "executer.py"
        script.write_text(EXECUTEUR)
        env = dict(os.environ, I18N_COLLECTE=str(journal))
        subprocess.run([sys.executable, str(script), str(DASH / "app.py"), *PAGES], env=env, check=True)
        if not journal.exists():
            return set()
        return {json.loads(l) for l in journal.read_text(encoding="utf-8").splitlines() if l.strip()}


# --- 2. Traduction -----------------------------------------------------------------------------------------------
class Traducteur:
    MODELE = "facebook/nllb-200-distilled-600M"
    MODELE_CT2 = "JustFrederik/nllb-200-distilled-600M-ct2-int8"

    def __init__(self):
        try:
            import ctranslate2
            import sentencepiece as spm
            from huggingface_hub import hf_hub_download, snapshot_download
            self.ct2 = ctranslate2.Translator(snapshot_download(self.MODELE_CT2), device="cpu",
                                              inter_threads=1, intra_threads=os.cpu_count() or 4)
            self.sp = spm.SentencePieceProcessor(model_file=hf_hub_download(self.MODELE, "sentencepiece.bpe.model"))
            self.moteur = "ctranslate2"
        except ImportError:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            self.tok = AutoTokenizer.from_pretrained(self.MODELE, src_lang="fra_Latn")
            self.mod = AutoModelForSeq2SeqLM.from_pretrained(self.MODELE)
            self.moteur = "transformers"

    # Reformulations françaises que le modèle comprend mieux (le texte affiché en français ne change pas)
    REFORMULER = [("auto-écoles", "écoles de conduite"), ("auto-école", "école de conduite"),
                  ("Auto-écoles", "Écoles de conduite"), ("Auto-école", "École de conduite"),
                  ("AUTO-ÉCOLE", "ÉCOLE DE CONDUITE")]

    def traduire(self, textes: list[str], cible: str, prudent: bool = False) -> list[str]:
        code = i18n.CODES_NLLB[cible]
        for avant, apres in self.REFORMULER:
            textes = [t.replace(avant, apres) for t in textes]
        if self.moteur == "ctranslate2":
            src = [["fra_Latn"] + self.sp.encode(t, out_type=str) + ["</s>"] for t in textes]
            options = dict(beam_size=4, repetition_penalty=1.3, no_repeat_ngram_size=3) if prudent else dict(beam_size=2)
            res = self.ct2.translate_batch(src, target_prefix=[[code]] * len(src), max_decoding_length=256,
                                           max_batch_size=16, **options)
            return [self.sp.decode([x for x in r.hypotheses[0] if x != code]) for r in res]
        x = self.tok(textes, return_tensors="pt", padding=True, truncation=True, max_length=256)
        out = self.mod.generate(**x, forced_bos_token_id=self.tok.convert_tokens_to_ids(code), num_beams=2,
                                max_new_tokens=256)
        return self.tok.batch_decode(out, skip_special_tokens=True)


MANUEL = {"en": {"Tableau de bord": "Dashboard", "Principal": "Main", "Analyses": "Analysis", "Pilotage": "Steering",
                  "Constat": "Finding", "Limite": "Limitation", "À retenir": "Key points", "Filtres": "Filters",
                  "Langue": "Language", "Voir le détail →": "See details →", "et": "and",
                  "Immatriculations": "Vehicle registrations", "Réseau routier évalué": "Road network assessed",
                  "Comparaison territoriale": "Territorial comparison", "Évolutions et constats": "Trends and findings",
                  "Carte du réseau et des auto-écoles": "Road network and driving schools map",
                  "Synthèse chiffrée": "Key figures", "Mobilité & sécurité routière": "Mobility & road safety",
                  "de routes en mauvais état) et un déficit de formation.":
                      "of roads in poor condition) and a training deficit.",
                  "ont un réseau dégradé.": "have a degraded road network.",
                  "Choisir la maille": "Choose the level of detail", "Réseau et formation": "Road network and training",
                  "À savoir :": "Good to know:",
                  "confirmée": "confirmed", "infirmée": "refuted", "nuancée": "qualified",
                  "non testable": "not testable", "Confirmées": "Confirmed",
                  "Infirmées ou nuancées": "Refuted or qualified", "Non testables": "Not testable",
                  "Synthèse": "Summary", "Sécurité routière": "Road safety",
                  "Accidents par territoire": "Accidents by territory",
                  "Qu'est-ce qui change, et que confirment les données ?": "What is changing, and what do the data confirm?",
                  "La carte des constats": "The map of findings",
                  "Ce qui n'a pas de territoire": "What has no territory",
                  "Les 17 vérifications et hypothèses": "The 17 checks and assumptions",
                  "Ce que chaque verdict change pour l'action": "What each verdict changes for action",
                  "Verdict": "Verdict", "Énoncé": "Statement", "Niveau": "Level",
                  "État du réseau routier": "Road network condition",
                  "7 tronçons": "7 sections", "49 tronçons": "49 sections",
                  "Limites analytiques": "Analytical limits",
                  "État des tronçons :": "Road-section state:", "États du réseau à afficher": "Road states to show",
                  "État du réseau routier sur cette carte.": "Road network condition on this map.",
                  "Levier réseau": "Road-network lever", "Levier formation": "Training lever",
                  "Préfectures qui cumulent": "Prefectures with both deficits",
                  "Les 10 premières": "The top 10 prefectures"}}


def suspecte(src: str, trad: str) -> bool:
    """Traduction probablement inventée : beaucoup plus longue que la source, ou mot répété en boucle."""
    mots = re.findall(r"\w+", trad.lower())
    boucle = any(mots.count(m) >= 4 and len(m) > 2 for m in set(mots))
    return not trad.strip() or len(trad) > 2.5 * len(src) + 25 or boucle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langues", nargs="+", default=["en", "ee", "kbp"])
    ap.add_argument("--collecte-seule", action="store_true")
    ap.add_argument("--limite", type=int, default=0, help="ne traduire que N segments (essai)")
    a = ap.parse_args()

    segs = chaines_du_code() | chaines_affichees() | set(EXTRAS)
    segs = sorted(s for s in segs if i18n._a_traduire(s))
    LOCALES.mkdir(exist_ok=True)
    (LOCALES / "segments_fr.json").write_text(json.dumps(segs, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(segs)} segments à traduire")
    if a.collecte_seule:
        return

    trad = Traducteur()
    print("moteur :", trad.moteur)
    for lg in a.langues:
        f = LOCALES / f"{lg}.json"
        actuel = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        manquants = [s for s in segs if s not in actuel]
        if a.limite:
            manquants = manquants[: a.limite]
        t0 = time.time()
        for i in range(0, len(manquants), 32):
            lot = manquants[i:i + 32]
            for src, cible in zip(lot, trad.traduire(lot, lg)):
                actuel[src] = {"texte": cible.strip(), "relu": False}
            f.write_text(json.dumps(dict(sorted(actuel.items())), ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{lg} : {min(i + 32, len(manquants))}/{len(manquants)} ({time.time() - t0:.0f} s)", flush=True)
        # Termes d'interface fixés à la main (anglais seulement : pas de locuteur pour vérifier les autres langues)
        for src, cible in MANUEL.get(lg, {}).items():
            actuel[src] = {"texte": cible, "relu": True}
        # Traductions suspectes : une seconde passe prudente ; si elles restent suspectes, texte vide (repli en
        # français à l'affichage) et marque "suspect" pour la relecture
        douteux = [k for k, v in actuel.items() if not v.get("relu") and k in segs and suspecte(k, v["texte"])]
        for i in range(0, len(douteux), 16):
            lot = douteux[i:i + 16]
            for src, cible in zip(lot, trad.traduire(lot, lg, prudent=True)):
                ok = not suspecte(src, cible)
                actuel[src] = {"texte": cible.strip() if ok else "", "relu": False, **({} if ok else {"suspect": True})}
        print(f"{lg} : {len(douteux)} suspectes retraduites, "
              f"{sum(1 for k in douteux if actuel[k].get('suspect'))} laissées en français", flush=True)
        # On ne garde que les segments encore utilisés, plus ceux relus à la main
        actuel = {k: v for k, v in actuel.items() if k in segs or (isinstance(v, dict) and v.get("relu"))}
        f.write_text(json.dumps(dict(sorted(actuel.items())), ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
