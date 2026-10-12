"""Alerte Telegram à l'ouverture du tableau de bord.

Repris du tableau de bord du défi « Économie numérique » (`EconomyNumeric-Challenge2/dashboard/notify.py`), adapté à
**Streamlit Community Cloud** : les identifiants s'y posent dans les *secrets* de l'application, pas dans des variables
d'environnement de dyno.

Une notification par visite, envoyée à un bot Telegram privé. L'usage visé est de savoir qu'un jury ou un partenaire a
ouvert le tableau de bord, pas de faire de la mesure d'audience : à la première dizaine de visiteurs simultanés, ce
mécanisme devient du bruit et il faudra lui substituer un récapitulatif quotidien.

Ce module s'exécute dans le processus Streamlit qui sert la page. Rien d'extérieur ne peut le remplacer : interroger
l'URL depuis ailleurs répond à « le site est-il debout ? », pas à « quelqu'un l'a-t-il ouvert ? ».

**Activation par la configuration, jamais par le code.** Deux valeurs sont attendues :

    TELEGRAM_BOT_TOKEN   jeton donné par @BotFather
    TELEGRAM_CHAT_ID     identifiant de la conversation destinataire

Elles sont lues d'abord dans l'environnement, puis dans `st.secrets` (Streamlit Cloud : *Settings → Secrets*, au
format TOML). Les deux absentes — poste de développement, exécution hors ligne —, le module ne fait **strictement
rien** : aucun réseau sollicité. Le fichier `.env` du dépôt n'est pas lu : lancer le tableau de bord en local n'envoie
donc aucune notification, sauf à poser les variables soi-même.

Quatre points ont dicté cette implémentation :

  * Streamlit réexécute le script en entier à chaque interaction. Sans le drapeau posé dans `st.session_state`, chaque
    changement de filtre de la barre latérale enverrait une notification. Le dédoublonnage est par session, pas par
    exécution.

  * L'envoi part dans un thread démon. Un `api.telegram.org` lent ou injoignable retarderait sinon le premier rendu de
    la page d'autant : le visiteur paierait la notification. Démon pour ne pas retenir le processus à l'arrêt.

  * Plafond quotidien. Un robot qui ouvre des sessions en rafale ne doit pouvoir saturer ni la conversation Telegram,
    ni le quota d'API du bot.

  * `urllib` de la bibliothèque standard, pas `requests` : aucune dépendance ajoutée à `requirements.txt`, que
    Streamlit Cloud installe à chaque déploiement.
"""
from __future__ import annotations

import os
import sys
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import streamlit as st

from composants import MARQUE

_ENDPOINT = "https://api.telegram.org/bot{token}/sendMessage"

# Au-delà, l'appel est abandonné. Le thread est démon, mais un socket sans délai d'expiration resterait ouvert
# indéfiniment.
_DELAI = 5

# Compté par journée UTC, remis à zéro au premier envoi du jour suivant.
_PLAFOND_QUOTIDIEN = 50

# Les en-têtes d'un navigateur dépassent facilement le raisonnable ; tronqués pour garder le message lisible sur un
# téléphone.
_LONGUEUR_MAX_ENTETE = 180

_CLE_SESSION = "_visite_signalee"

# Compteur partagé par toutes les sessions du processus. Les globales d'un module importé survivent aux réexécutions du
# script (`sys.modules` le garde en cache), là où celles d'`app.py` sont reconstruites à chaque fois. Verrou car les
# sessions Streamlit sont servies par des threads distincts.
_verrou = threading.Lock()
_compteur = {"jour": None, "envoyes": 0}


def _secret(nom: str) -> str:
    """La valeur de `nom`, cherchée dans l'environnement puis dans les secrets de l'application.

    Lue à l'appel et non à l'import : modifier les secrets sur Streamlit Cloud redémarre l'application, et les tests
    peuvent poser ou retirer les variables sans jouer sur l'ordre des imports.

    `st.secrets` lève quand aucun fichier de secrets n'existe (cas du poste de développement) : l'absence n'est pas une
    erreur, elle signifie seulement que l'alerte est inactive.
    """
    valeur = os.environ.get(nom, "")
    if valeur.strip():
        return valeur.strip()
    try:
        return str(st.secrets.get(nom, "")).strip()
    except Exception:
        return ""


def _configuration():
    """(jeton, destinataire) si les deux valeurs sont présentes, sinon None."""
    jeton, destinataire = _secret("TELEGRAM_BOT_TOKEN"), _secret("TELEGRAM_CHAT_ID")
    if not jeton or not destinataire:
        return None
    return jeton, destinataire


def _quota_disponible():
    """Consomme une unité du plafond du jour. False si le plafond est atteint."""
    aujourdhui = datetime.now(timezone.utc).date()
    with _verrou:
        if _compteur["jour"] != aujourdhui:
            _compteur["jour"] = aujourdhui
            _compteur["envoyes"] = 0
        if _compteur["envoyes"] >= _PLAFOND_QUOTIDIEN:
            return False
        _compteur["envoyes"] += 1
        return True


def _adresse_client(entetes):
    """Adresse IP du visiteur, telle que le mandataire la déclare.

    ⚠️ Elle n'est pas garantie. Le défi « Économie numérique » tournait sur Heroku, dont le routeur **ajoute** à la fin
    de `X-Forwarded-For` l'adresse qu'il observe : la dernière valeur y était la seule sûre. Streamlit Cloud ne
    documente pas ce qu'il écrit. On prend donc `X-Real-Ip` quand il existe — un mandataire le pose avec l'adresse de
    la connexion qu'il voit —, sinon la première valeur de `X-Forwarded-For`, qui est la convention courante. Les deux
    sont falsifiables par le client : la notification les présente comme déclarées, et rien n'en dépend.
    """
    reelle = (entetes.get("X-Real-Ip") or entetes.get("X-Real-IP") or "").strip()
    if reelle:
        return reelle
    transmis = entetes.get("X-Forwarded-For", "")
    if not transmis:
        return "inconnue"
    return transmis.split(",")[0].strip() or "inconnue"


def _contexte():
    """En-têtes de la requête du visiteur, ou None hors contexte HTTP.

    `st.context` n'est pas disponible dans toutes les situations d'exécution. Son absence n'est pas une erreur, elle
    produit simplement une notification sans détail.
    """
    try:
        entetes = st.context.headers or {}
    except Exception:
        return None
    return {
        "ip": _adresse_client(entetes),
        "navigateur": (entetes.get("User-Agent") or "inconnu")[:_LONGUEUR_MAX_ENTETE],
        "provenance": (entetes.get("Referer") or "accès direct")[:_LONGUEUR_MAX_ENTETE],
    }


def _titre_application():
    """Le nom de l'application, lu dans `composants.py` comme la barre du haut et le titre de l'onglet.

    Écrit en dur ici, il finirait par désigner autre chose que ce que porte l'interface.
    """
    return MARQUE


def _message():
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lignes = [f"🚦 Nouvelle visite — {_titre_application()}", horodatage]
    contexte = _contexte()
    if contexte:
        lignes += [
            "",
            f"IP déclarée : {contexte['ip']}",
            f"Navigateur  : {contexte['navigateur']}",
            f"Provenance  : {contexte['provenance']}",
        ]
    return "\n".join(lignes)


def _envoyer(jeton, destinataire, texte):
    """Appelle l'API Telegram. Toute erreur est journalisée, jamais propagée.

    Ce thread s'exécute hors de tout contexte Streamlit : une exception qui en sortirait ne remonterait nulle part
    d'utile. On écrit sur stderr, que le journal de l'application capture : de quoi diagnostiquer un jeton révoqué sans
    que le visiteur voie quoi que ce soit.

    Texte brut, sans `parse_mode` : un en-tête de navigateur contenant `_` ou `*` ferait échouer l'analyse Markdown
    côté Telegram et perdre la notification.
    """
    charge = urllib.parse.urlencode({
        "chat_id": destinataire,
        "text": texte,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    requete = urllib.request.Request(_ENDPOINT.format(token=jeton), data=charge)
    try:
        with urllib.request.urlopen(requete, timeout=_DELAI):
            pass
    except Exception as erreur:
        print(f"[notify] envoi Telegram impossible : {erreur}", file=sys.stderr)


def signaler_visite():
    """Signale l'ouverture d'une session, au plus une fois par visiteur.

    Sans effet si la configuration est absente ou si le plafond quotidien est atteint. Ne lève jamais : une alerte
    défaillante ne doit pas empêcher le tableau de bord de s'afficher.
    """
    try:
        if st.session_state.get(_CLE_SESSION):
            return
        # Posé avant toute autre chose : même désactivée ou plafonnée, la session ne retentera pas à la réexécution
        # suivante.
        st.session_state[_CLE_SESSION] = True

        configuration = _configuration()
        if configuration is None or not _quota_disponible():
            return

        jeton, destinataire = configuration
        threading.Thread(
            target=_envoyer,
            args=(jeton, destinataire, _message()),
            daemon=True,
        ).start()
    except Exception as erreur:
        print(f"[notify] alerte de visite ignorée : {erreur}", file=sys.stderr)
