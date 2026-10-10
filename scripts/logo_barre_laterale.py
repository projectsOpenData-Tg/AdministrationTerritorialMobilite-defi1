"""Dessine le logo de la barre latérale du tableau de bord : le Togo en miniature aux couleurs du drapeau, traversé
par une route, avec le nom du tableau de bord à côté.

Le contour du pays est celui des 39 préfectures du projet (data/processed/geo/prefectures.geojson), fusionnées et
simplifiées : la silhouette affichée est donc la même que celle des cartes du tableau de bord.

Sorties, dans dashboard/static/ (affichées par st.logo) :
- logo_barre_laterale.svg : silhouette et texte, en face du bouton de la barre latérale dépliée ;
- logo_togo_icone.svg : silhouette seule, en haut à gauche quand la barre est repliée (fond clair, texte illisible).

Usage : python scripts/logo_barre_laterale.py
"""
import math
from pathlib import Path

import geopandas as gpd

RACINE = Path(__file__).resolve().parent.parent
CONTOURS = RACINE / "data" / "processed" / "geo" / "prefectures.geojson"
STATIQUE = RACINE / "dashboard" / "static"
SORTIE = STATIQUE / "logo_barre_laterale.svg"
SORTIE_ICONE = STATIQUE / "logo_togo_icone.svg"

# Couleurs officielles du drapeau togolais
VERT, JAUNE, ROUGE, BLANC = "#006a4e", "#ffce00", "#d21034", "#ffffff"

HAUTEUR_CARTE = 104          # hauteur de la silhouette dans le logo, en unités SVG
MARGE = 3


def silhouette() -> tuple[str, float]:
    """Chemin SVG du contour du Togo, mis à l'échelle sur HAUTEUR_CARTE, et largeur obtenue."""
    pays = gpd.read_file(CONTOURS).union_all().simplify(0.006, preserve_topology=True)
    x0, y0, x1, y1 = pays.bounds
    kx = math.cos(math.radians((y0 + y1) / 2))          # équirectangulaire, corrigée de la latitude moyenne
    echelle = HAUTEUR_CARTE / (y1 - y0)
    largeur = (x1 - x0) * kx * echelle

    def point(x, y):
        return f"{MARGE + (x - x0) * kx * echelle:.1f},{MARGE + (y1 - y) * echelle:.1f}"

    anneaux = [pays.exterior] if pays.geom_type == "Polygon" else [p.exterior for p in pays.geoms]
    chemin = " ".join("M" + " L".join(point(x, y) for x, y in a.coords) + "Z" for a in anneaux)
    return chemin, largeur


def etoile(cx: float, cy: float, r: float) -> str:
    sommets = []
    for i in range(10):
        rayon = r if i % 2 == 0 else r * 0.382
        angle = math.radians(-90 + i * 36)
        sommets.append(f"{cx + rayon * math.cos(angle):.1f},{cy + rayon * math.sin(angle):.1f}")
    return "M" + " L".join(sommets) + "Z"


def logo(avec_texte: bool = True) -> str:
    chemin, l = silhouette()
    h, x, y = HAUTEUR_CARTE, MARGE, MARGE
    bande = h / 5
    # Drapeau étiré sur la silhouette : 5 bandes vert / jaune, canton rouge en haut à gauche avec l'étoile blanche
    bandes = "".join(f'<rect x="{x - 2}" y="{y + i * bande:.1f}" width="{l + 4:.1f}" height="{bande + 0.4:.1f}" '
                     f'fill="{VERT if i % 2 == 0 else JAUNE}"/>' for i in range(5))
    canton = l * 0.62
    drapeau = (bandes + f'<rect x="{x - 2}" y="{y - 2}" width="{canton + 2:.1f}" height="{bande * 2.2:.1f}" fill="{ROUGE}"/>'
               f'<path d="{etoile(x + canton * 0.5, y + bande * 1.05, bande * 0.62)}" fill="{BLANC}"/>')
    # Route en perspective : large au premier plan (sud-ouest), elle s'affine en remontant vers le nord-est
    route = (f'<path d="M{x - 2},{y + h + 2} C{x + l * 0.35},{y + h * 0.8} {x + l * 0.15},{y + h * 0.62} {x + l * 0.62},{y + h * 0.5} '
             f'L{x + l * 0.7},{y + h * 0.53} C{x + l * 0.42},{y + h * 0.66} {x + l * 0.75},{y + h * 0.82} {x + l * 0.55},{y + h + 2} Z" '
             'fill="#3b4553" stroke="#c9d3df" stroke-width="0.8"/>'
             f'<path d="M{x + l * 0.27},{y + h + 2} C{x + l * 0.52},{y + h * 0.82} {x + l * 0.3},{y + h * 0.65} {x + l * 0.66},{y + h * 0.515}" '
             f'fill="none" stroke="{BLANC}" stroke-width="1.3" stroke-dasharray="3.2 2.6"/>')
    tx = x + l + 14
    largeur_totale = tx + 156 if avec_texte else l + 2 * MARGE          # « SÉCURITÉ ROUTIÈRE » tient dans 152 unités
    hauteur_totale = h + 2 * MARGE
    police = "font-family=\"'IBM Plex Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif\""
    texte = (f'<text x="{tx:.1f}" y="27" {police} font-size="24" font-weight="700" fill="{BLANC}" letter-spacing="1">TOGO</text>'
             f'<text x="{tx:.1f}" y="49" {police} font-size="15.5" font-weight="700" fill="{BLANC}">MOBILITÉ &amp;</text>'
             f'<text x="{tx:.1f}" y="68" {police} font-size="15.5" font-weight="700" fill="{BLANC}">SÉCURITÉ ROUTIÈRE</text>'
             f'<text x="{tx:.1f}" y="88" {police} font-size="11.5" fill="#cde2fb">Tableau de bord territorial</text>'
             f'<text x="{tx:.1f}" y="103" {police} font-size="11.5" fill="#cde2fb">d’aide à la décision</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur_totale:.0f} {hauteur_totale:.0f}" '
            f'width="{largeur_totale:.0f}" height="{hauteur_totale:.0f}" role="img" '
            'aria-label="Togo — Mobilité et sécurité routière, tableau de bord territorial d’aide à la décision">'
            f'<defs><clipPath id="pays"><path d="{chemin}"/></clipPath></defs>'
            f'<g clip-path="url(#pays)">{drapeau}{route}</g>'
            f'<path d="{chemin}" fill="none" stroke="{BLANC}" stroke-opacity="0.85" stroke-width="1.1" stroke-linejoin="round"/>'
            f'{texte if avec_texte else ""}</svg>\n')


if __name__ == "__main__":
    for chemin, avec_texte in ((SORTIE, True), (SORTIE_ICONE, False)):
        chemin.write_text(logo(avec_texte), encoding="utf-8")
        print(f"Écrit : {chemin.relative_to(RACINE)}")
