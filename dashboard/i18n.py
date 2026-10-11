"""Traduction du tableau de bord : français (langue source), anglais, éwé, kabiyè.

Méthode « traduire avant le déploiement » : les textes sont traduits une fois, hors ligne, par
scripts/traduire_dashboard.py (modèle NLLB-200), et enregistrés dans dashboard/locales/<langue>.json, qu'on commit.
À l'affichage, bi() lit seulement ces fichiers : aucun modèle, aucun appel réseau.

Les pages restent écrites en français. installer() fait passer par bi() tout ce que Streamlit affiche (markdown,
légendes, boutons, onglets, options des widgets, tableaux, graphiques Plotly) : il n'y a pas à envelopper chaque
chaîne une à une. Un texte est découpé en segments (le HTML, le markdown et les gabarits Plotly %{…} restent
intacts) ; chaque segment est traduit s'il est dans le fichier de la langue, sinon il reste en français.

Collecte : avec la variable d'environnement I18N_COLLECTE=<fichier>, chaque segment affiché est ajouté à ce fichier ;
le script de traduction s'en sert, avec les chaînes lues dans le code, pour savoir quoi traduire.
"""
import copy
import functools
import json
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

ICI = Path(__file__).resolve().parent
LOCALES = ICI / "locales"

# Code de la langue (dashboard et fichiers) → libellé du sélecteur et code NLLB-200
LANGUES = {"fr": "FR", "en": "EN", "ee": "Eʋegbe", "kbp": "Kabɩyɛ"}
CODES_NLLB = {"fr": "fra_Latn", "en": "eng_Latn", "ee": "ewe_Latn", "kbp": "kbp_Latn"}

# Textes fixes écrits à la main ; une langue absente passe par la traduction automatique (bi)
_T = {"Langue": {"fr": "Langue", "en": "Language"}}

# Noms propres et sigles laissés tels quels dans toutes les langues (complétés par les noms des préfectures)
_VALEURS = {"Togo", "Togo AI Lab", "TOGO", "Grand Lomé", "Lomé", "Maritime", "Plateaux", "Centrale", "Kara",
            "Savanes", "Maritime hors Grand Lomé", "A", "B", "C", "D", "E", "F", "FR", "EN", "Eʋegbe", "Kabɩyɛ",
            "CSV", "RGPH-5", "HDX", "OSM", "WorldPop", "EHCVM", "NLLB-200"}

_COLLECTE = os.environ.get("I18N_COLLECTE")
_vus: set[str] = set()


def langue() -> str:
    try:
        return st.session_state.get("langue", "fr")
    except Exception:          # hors exécution Streamlit (scripts)
        return "fr"


@functools.lru_cache(maxsize=None)
def _dictionnaire(code: str) -> dict:
    f = LOCALES / f"{code}.json"
    if not f.exists():
        return {}
    brut = json.loads(f.read_text(encoding="utf-8"))
    return {k: (v["texte"] if isinstance(v, dict) else v) for k, v in brut.items() if v}


# --- Découpage en segments ------------------------------------------------------------------------------------
# Séparateurs gardés tels quels : balises HTML, entités, gabarits Plotly, gras markdown, sauts de ligne, puces,
# flèches et pictogrammes, numéros cerclés.
_SEP = re.compile(r"(<[^>]+>|&[a-z#0-9]+;|%\{[^}]*\}|\{[^}]*\}|\*\*|\n|^\s*[-•]\s+|[→←↗↘·①②③④⑤|]|:material/[a-z_]+:)",
                  re.M)
_LETTRES = re.compile(r"[A-Za-zÀ-ÿ]{2,}")


@functools.lru_cache(maxsize=1)
def _noms_propres() -> frozenset:
    """Noms de lieux et d'établissements des données (préfectures, régions, zones, auto-écoles, routes, localités) :
    jamais traduits."""
    noms = set(_VALEURS)
    geo = ICI.parent / "data" / "processed" / "geo"
    colonnes = {"prefectures": ("Préfecture", "Région", "Zone"),
                "auto_ecoles": ("Nom", "Adresse", "Localité", "Canton", "Commune", "Préfecture"),
                "routes_classees": ("Nom",)}
    for fichier, cols in colonnes.items():
        f = geo / f"{fichier}.geojson"
        if f.exists():
            for ft in json.loads(f.read_text(encoding="utf-8"))["features"]:
                noms.update(str(ft["properties"].get(c)).strip() for c in cols if ft["properties"].get(c))
    return frozenset(noms)


_PREFIXE = re.compile(r"^[^A-Za-zÀ-ÿ0-9]+")


def _a_traduire(seg: str) -> bool:
    s = _PREFIXE.sub("", seg.strip())
    if not s or not _LETTRES.search(s) or s.startswith(("http", "data:")):
        return False
    noms = _noms_propres()
    return not all(p.strip() in noms for p in re.split(r"\s*[;,/]\s*|\s+et\s+", s) if p.strip())


def _noter(seg: str):
    if _COLLECTE and seg not in _vus:
        _vus.add(seg)
        with open(_COLLECTE, "a", encoding="utf-8") as f:
            f.write(json.dumps(seg, ensure_ascii=False) + "\n")


def segments(texte: str) -> list[str]:
    """Segments traduisibles d'un texte (clés des fichiers de langue)."""
    if not isinstance(texte, str):
        return []
    return [m.strip() for m in _SEP.split(texte) if m and not _SEP.fullmatch(m) and _a_traduire(m)]


def bi(texte, code: str | None = None):
    """Traduit un texte affiché (str) dans la langue courante, segment par segment ; renvoie tel quel tout le reste."""
    if not isinstance(texte, str) or not texte:
        return texte
    code = code or langue()
    if code == "fr" and not _COLLECTE:
        return texte
    trad = _dictionnaire(code) if code != "fr" else {}
    morceaux = _SEP.split(texte)
    out = []
    for m in morceaux:
        if not m or _SEP.fullmatch(m) or not _a_traduire(m):
            out.append(m)
            continue
        cle = m.strip()
        _noter(cle)
        t = trad.get(cle)
        if t:
            gauche, droite = m[: len(m) - len(m.lstrip())], m[len(m.rstrip()):]
            out.append(gauche + t + droite)
        else:
            out.append(m)
    return "".join(out)


def t(cle: str) -> str:
    """Texte fixe de _T dans la langue courante, sinon sa traduction automatique."""
    return _T.get(cle, {}).get(langue()) or bi(cle)


# --- Traduction des objets affichés -----------------------------------------------------------------------------
def _bi_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].map(bi)
    return df.rename(columns=lambda c: bi(c) if isinstance(c, str) else c)


def _textes(v):
    """Liste de chaînes si v est une séquence de textes (liste, tuple, tableau, série), sinon None."""
    if v is None or isinstance(v, (str, bytes, dict)):
        return None
    try:
        v = list(v)
    except TypeError:
        return None
    return v if v and isinstance(v[0], str) else None


def _bi_figure(fig, garder_donnees: bool):
    """Copie traduite d'une figure Plotly : titres, axes, légendes, annotations, info-bulles, textes. Les catégories
    des barres sont traduites ; les données d'une figure à sélection (customdata, emplacements) ne le sont pas."""
    fig = copy.deepcopy(fig)
    lay = fig.layout
    if lay.title and lay.title.text:
        lay.title.text = bi(lay.title.text)
    for nom in [k for k in lay.to_plotly_json() if k.startswith(("xaxis", "yaxis"))]:
        ax = lay[nom]
        if ax.title and ax.title.text:
            ax.title.text = bi(ax.title.text)
        if ax.ticktext:
            ax.ticktext = [bi(x) for x in ax.ticktext]
        if ax.ticksuffix:
            ax.ticksuffix = bi(ax.ticksuffix)
    if lay.annotations:
        for a in lay.annotations:
            a.text = bi(a.text)
    if lay.legend and lay.legend.title and lay.legend.title.text:
        lay.legend.title.text = bi(lay.legend.title.text)
    for tr in fig.data:
        for att in ("name", "hovertemplate", "texttemplate", "legendgroup"):
            v = getattr(tr, att, None)
            if isinstance(v, str):
                setattr(tr, att, bi(v))
        for att in ("text", "hovertext"):
            v = getattr(tr, att, None)
            if isinstance(v, str):
                setattr(tr, att, bi(v))
            elif _textes(v):
                setattr(tr, att, [bi(x) for x in _textes(v)])
        if tr.type == "bar":
            for att in ("x", "y"):
                if _textes(getattr(tr, att, None)):
                    setattr(tr, att, [bi(x) for x in _textes(getattr(tr, att))])
        if not garder_donnees and getattr(tr, "customdata", None) is not None:
            try:
                tr.customdata = [[bi(x) for x in ligne] if hasattr(ligne, "__iter__") and not isinstance(ligne, str)
                                 else bi(ligne) for ligne in tr.customdata]
            except Exception:
                pass
    return fig


def _format(fn):
    """format_func traduit : la valeur reste en français (la logique des pages ne change pas), l'affichage est traduit."""
    def f(v):
        return bi(fn(v) if fn else str(v))
    return f


def _envelopper(nom, transformer):
    orig = getattr(DeltaGenerator, nom)

    @functools.wraps(orig)
    def enveloppe(self, *args, **kwargs):
        args, kwargs = transformer(list(args), kwargs)
        return orig(self, *args, **kwargs)
    setattr(DeltaGenerator, nom, enveloppe)


def _premier_libelle(args, kwargs, cle="body"):
    if args:
        args[0] = bi(args[0])
    elif cle in kwargs:
        kwargs[cle] = bi(kwargs[cle])
    for k in ("help", "placeholder"):
        if isinstance(kwargs.get(k), str):
            kwargs[k] = bi(kwargs[k])
    return args, kwargs


def _choix(args, kwargs):
    args, kwargs = _premier_libelle(args, kwargs, "label")
    kwargs["format_func"] = _format(kwargs.get("format_func"))
    return args, kwargs


def _onglets(args, kwargs):
    noms = list(args[0] if args else kwargs.pop("tabs"))
    if args:
        args[0] = [bi(x) for x in noms]
    else:
        kwargs["tabs"] = [bi(x) for x in noms]
    if kwargs.get("default") in noms:
        kwargs["default"] = bi(kwargs["default"])
    return args, kwargs


def _tableau(args, kwargs):
    if not args:
        return args, kwargs
    d = args[0]
    if isinstance(d, pd.DataFrame):
        args[0] = _bi_df(d)
    elif hasattr(d, "format") and hasattr(d, "data"):      # Styler : style calculé sur les valeurs françaises
        d.format(lambda v: bi(v) if isinstance(v, str) else v, subset=list(d.data.select_dtypes("object").columns))
        d.relabel_index([bi(c) for c in d.data.columns], axis=1)
    return args, kwargs


def _graphique(args, kwargs):
    if args:
        args[0] = _bi_figure(args[0], garder_donnees=bool(kwargs.get("on_select")))
    return args, kwargs


def installer():
    """Branche bi() sur l'affichage de Streamlit (une fois par processus)."""
    if getattr(DeltaGenerator, "_i18n_installe", False):
        return
    for nom in ("markdown", "caption", "info", "warning", "success", "error", "write", "text", "subheader", "title",
                "header"):
        _envelopper(nom, _premier_libelle)
    for nom in ("button", "download_button", "expander", "toggle", "slider", "text_input", "checkbox", "page_link",
                "popover"):
        _envelopper(nom, lambda a, k: _premier_libelle(a, k, "label"))
    for nom in ("radio", "selectbox", "pills", "multiselect", "select_slider", "segmented_control"):
        _envelopper(nom, _choix)
    _envelopper("tabs", _onglets)
    _envelopper("dataframe", _tableau)
    _envelopper("plotly_chart", _graphique)
    # st.markdown, st.caption… sont des méthodes liées au conteneur principal, figées à l'import : on les relie
    import streamlit
    for nom in dir(streamlit):
        f = getattr(streamlit, nom)
        if getattr(f, "__self__", None) is streamlit._main and hasattr(DeltaGenerator, nom):
            setattr(streamlit, nom, getattr(streamlit._main, nom))
    DeltaGenerator._i18n_installe = True


def selecteur():
    """Sélecteur de langue (barre latérale, sous le logo). La langue suit aussi l'adresse : ?lang=ee."""
    if "langue" not in st.session_state:
        demande = st.query_params.get("lang", "fr")
        st.session_state["langue"] = demande if demande in LANGUES else "fr"

    def _changer():
        if not st.session_state.get("langue"):
            st.session_state["langue"] = "fr"
        st.query_params["lang"] = st.session_state["langue"]

    with st.sidebar.container(key="selecteur_langue"):
        st.markdown(f'<div class="langue-lib">{t("Langue")}</div>', unsafe_allow_html=True)
        st.segmented_control(t("Langue"), list(LANGUES), format_func=lambda c: LANGUES[c], key="langue",
                             on_change=_changer, label_visibility="collapsed")
