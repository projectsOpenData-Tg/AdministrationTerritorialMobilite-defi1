# Fichiers statiques

Placer ici `logo_togo_ai_lab.png` (téléchargé depuis https://datalab.gouv.tg/) pour qu'il
s'affiche dans la bande officielle, en haut de chaque page.

Tant que ce fichier est absent, un texte de repli « TOGO AI LAB » s'affiche à la place —
c'est le comportement attendu, pas une erreur.

Nécessite `server.enableStaticServing = true` dans `.streamlit/config.toml` (déjà en
place, à la racine du dépôt et dans ce dossier `dashboard/`) et référence l'image via
`app/static/<fichier>`, l'URL que Streamlit réserve à ce dossier.

## `armoiries-togo-ecu.svg` et `armoiries-togo.svg` — armoiries de la République togolaise

Repris à l'identique du projet sœur `Environment-challenge2/assets/`, à la demande de
l'utilisateur.

| | |
|---|---|
| Source | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Bloc_Blason_R%C3%A9publique_Togolaise.svg) |
| Auteur | Edem Fiadjoe |
| Licence | **CC BY-SA 4.0** — https://creativecommons.org/licenses/by-sa/4.0 |

**L'attribution est obligatoire** — elle figure dans le pied de page de l'application
(`components/methodology.pied_de_page`).

Ce fichier est une **restitution par un contributeur**, pas une ressource officielle de
l'administration togolaise. `armoiries-togo-ecu.svg` est un recadrage sur l'écu seul
(`viewBox="6 2 146 128"`, aucun trait modifié) : la mention « RÉPUBLIQUE TOGOLAISE »
incrustée dans l'original devient illisible sous 60 px, et l'application affiche déjà le
nom du ministère comme texte, à côté. C'est cette version recadrée qu'utilise la bande
officielle ; `armoiries-togo.svg` (original complet) reste disponible si besoin d'un
affichage plus grand.
