# Plan détaillé — page 8

## Page 8 — Horizon 2031

**Nom dans le menu :** « Horizon 2031 ». Groupe **Pilotage**, après « Recommandations » : la page 6 dit quoi faire, la page 8 dit combien il en faudra d’ici 1, 3 et 5 ans.

**Objectif :** montrer que le besoin grandit avec la population. Les quantités du document 10 valent pour 2022 ; la page 8 les recalcule à chaque horizon, et dit ce que la cible de sécurité demande d’éviter.

**Référence :** l’annexe Horizon 2031 (`A1_horizon.md`), ses sorties et son notebook. La page ne calcule rien : elle lit `horizon_A1.csv`, `population_A1.csv`, `national_A1.csv`, `acces_A1.csv`, `emplacements_A1.csv` et `sites_A1.csv`.

**Ce que la page n’affiche pas :** aucune carte des accidents ni des permis. Ils ne sont publiés qu’au niveau national ; les répartir entre les territoires inventerait une géographie. Aucun effet des routes ou des auto-écoles sur les accidents : les données ne le mesurent pas.

```text
┌──────────────────────────────────────────────────────────────────┐
│  COMBIEN EN FAUDRA-T-IL D’ICI 2031 ?                              │
│  [réponse en une phrase]                                          │
├──────────────────────────────────────────────────────────────────┤
│  [CURSEUR D’HORIZON : 2022 · 2026 · 2027 · 2029 · 2031]           │
├──────────────────────────────────────────────────────────────────┤
│  [4 CHIFFRES CLÉS de l’horizon choisi]                            │
├──────────────────────────────────────────────────────────────────┤
│  [CE QU’IL FAUT AJOUTER — carte + tableau par zone]      │CONSTAT│
├──────────────────────────────────────────────────────────────────┤
│  [SANS ACTION, LE TAUX BAISSE — 2 graphiques]                     │
├──────────────────────────────────────────────────────────────────┤
│  [SÉCURITÉ ROUTIÈRE — écart à la cible + plafond du casque]       │
├──────────────────────────────────────────────────────────────────┤
│  [OÙ OUVRIR LES AUTO-ÉCOLES — carte des sites]                    │
├──────────────────────────────────────────────────────────────────┤
│  [SYNTHÈSE CHIFFRÉE]  [LIMITE]                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Réponse sous le titre** (11 §4.3) : « Sans ouverture, le manque d’auto-écoles passe de 41 en 2022 à 50 en 2031 dans les préfectures qui en manquent, et 4,6 millions de ruraux resteront à plus de 2 km d’une route revêtue. » Chiffres lus dans `horizon_A1.csv` (maille Pays, périmètre « Levier du 08 » et accès rural).

**Le curseur d’horizon** est le seul filtre de la page. Il porte 5 positions, étiquetées « 2022 · aujourd’hui mesuré », « 2026 · population d’aujourd’hui », « 2027 · dans 1 an », « 2029 · dans 3 ans », « 2031 · dans 5 ans ». Il change tous les chiffres, cartes et tableaux de la page, sauf les graphiques de séries, qui montrent toutes les années et marquent l’horizon choisi. Valeur par défaut : **2029**, l’horizon de la plupart des recommandations.

**Mention sous le curseur :** « Les leviers restent à leur dernière observation : auto-écoles de 2021-2022, état du réseau relevé en 2020. Seule la population avance. »

---

### Section 1 — Les 4 chiffres clés de l’horizon

Rangée de 4 cartes de chiffre clé (maquette §8.4), relues à chaque position du curseur, dans `horizon_A1.csv`, maille Pays.

| # | Chiffre | Lecture | Source |
| - | ------- | ------- | ------ |
| 1 | **Habitants** | Population du Togo à l’horizon | `population_A1.csv`, somme des préfectures |
| 2 | **Auto-écoles à ouvrir** | Dans les préfectures sans auto-école agréée, avec la fourchette | `horizon_A1.csv`, levier « Auto-écoles », périmètre « Levier du 08 » |
| 3 | **Km à remettre en état** | Dans les préfectures au réseau dégradé ; la valeur ne change pas d’un horizon à l’autre | `horizon_A1.csv`, levier « Remise en état », périmètre « Levier du 08 » |
| 4 | **Ruraux loin d’une route revêtue** | À plus de 2 km d’une route nationale revêtue | `horizon_A1.csv`, levier « Accès rural » |

Chaque carte porte sa fourchette en dessous, quand les deux variantes de population diffèrent : « 48 à 50 selon la répartition de la population ». Le niveau de preuve C est rappelé sur la rangée.

---

### Section 2 — Ce qu’il faut ajouter

Visuel principal, à côté du Constat.

**Carte des préfectures**, avec un sélecteur de levier à deux positions :

- **Auto-écoles à ouvrir** : 5 classes fixes, 0, 1, 2, 3, 4 ou plus, palette `BLEUS` ; les classes ne changent pas d’un horizon à l’autre, pour que les couleurs se comparent.
- **Km à remettre en état** : 5 classes fixes ; un seul panneau, la valeur étant la même à tous les horizons. Un bandeau le dit : « Aucune donnée ne mesure l’usure du réseau : la quantité à remettre en état ne dépend pas de l’horizon. »

Mô en gris, « aucune route classée ». Encart du Grand Lomé comme sur les autres cartes.

**Tableau par zone**, sous la carte, exportable :

| Zone | Habitants | Auto-écoles à ouvrir | Fourchette | Km à remettre en état | Ruraux à plus de 2 km |
| ---- | --------- | -------------------- | ---------- | --------------------- | --------------------- |

Lu dans `horizon_A1.csv`, maille Zone, périmètre « Levier du 08 » pour les deux leviers et « Toutes les préfectures » pour l’accès rural. Une ligne de total pour le pays. Les 5 régions sont disponibles par le même sélecteur de maille que la page 2.

**Tableau par recommandation**, dépliable : une ligne par recommandation chiffrée du document 10, avec sa quantité de 2022, sa quantité à l’horizon choisi, et l’horizon que la recommandation elle-même porte. Lu dans `horizon_A1.csv`, maille Recommandation. Les titres viennent de `cartes_10.csv` ; les identifiants ne s’affichent pas (11 §4.2). Chaque ligne mène à sa carte en page 6.

**Règle des totaux :** une note sous le tableau rappelle que les quantités des recommandations de zone sont déjà comptées dans les leviers, et ne s’additionnent pas.

**Constat** (à droite de la carte) : « Les 41 auto-écoles qui manquaient en 2022 seront 50 en 2031 : la population grandit plus vite que l’offre. Les km à remettre en état, eux, ne bougent pas : c’est un retard déjà constitué. »

---

### Section 3 — Sans action, le taux baisse

Deux graphiques côte à côte, qui montrent toutes les années et marquent l’horizon choisi.

1. **Auto-écoles agréées pour 100 000 habitants, par zone**, de 2022 à 2031, si rien n’ouvre : 6 courbes, couleurs `COULEUR_REGION`, étiquettes directes. La ligne de cible, 1,065, en tireté. Lu dans `horizon_A1.csv`, colonne « sans action ».
2. **Population par zone**, de 2022 à 2031, avec la fourchette des deux variantes en bande. Lu dans `population_A1.csv`.

**Constat :** « Aucune zone n’atteint la cible aujourd’hui en dehors du Grand Lomé, et l’écart se creuse partout : le taux national passe de 1,63 à 1,35 auto-école pour 100 000 habitants. »

**Note de méthode, dépliable :** « La population de chaque préfecture suit la croissance de sa région entre les recensements de 2010 et de 2022, ramenée au total des projections nationales. L’autre variante garde les parts de 2022 : les deux donnent la fourchette. »

---

### Section 4 — Sécurité routière : ce que la cible demande

Au niveau national seulement. Un bandeau le dit en tête de section : « Les accidents ne sont publiés que pour tout le pays : cette section n’a pas de carte. »

**Graphique 1 — Les trois séries**, en trois panneaux sur la même échelle de temps, de 2010 à 2031 : accidents constatés, blessés, tués déclarés.

- trait plein jusqu’en 2024 : observé ;
- bande de 2025 à 2031 : les deux références sans action nouvelle, taux inchangé et tendance ;
- ligne de cible pour les blessés et les tués : moitié de la valeur de 2021 en 2030 ;
- période projetée grisée ; horizon choisi marqué.

**Graphique 2 — Tués : l’écart à la cible et le plafond du casque**, en barres, aux 4 horizons à venir. Deux barres d’écart (taux inchangé, tendance) et deux barres de plafond, avec leur intervalle.

**Constat :** « Même si la baisse observée depuis 2010 se poursuit, il faudrait éviter 204 tués de plus en 2029 pour suivre la cible. Généraliser le casque n’y suffirait pas : au mieux 147 à 174 tués évités. »

**Note sous le graphique :** « Le plafond suppose qu’aucun usager de deux-roues tué ne portait de casque. Le taux de port n’est pas publié : c’est une limite haute, pas une estimation. »

**Rappel de la limite des tués déclarés :** 8,62 tués déclarés pour 100 000 habitants en 2021, contre 22,7 estimés par l’OMS. Une baisse des déclarations ressemblerait à un progrès.

---

### Section 5 — Où ouvrir les auto-écoles

**Carte des sites**, pour les 23 préfectures du levier formation : les préfectures concernées en bleu clair, les auto-écoles agréées existantes en gris, les sites retenus en bleu. Lu dans `sites_A1.csv` et `geo/auto_ecoles.geojson`.

**Tableau par préfecture**, exportable, trié par population couverte : préfecture, auto-écoles à ouvrir, part de la population à moins de 10 km d’une auto-école avant, en les ouvrant toutes au chef-lieu, et en les répartissant. Lu dans `emplacements_A1.csv`.

**Constat :** « Réparties, 48 auto-écoles mettent 56,7 % de la population de ces préfectures à moins de 10 km d’une auto-école, contre 32,2 % si elles ouvrent toutes au chef-lieu : 719 730 habitants de plus. »

**Note sous la carte :** « Ces sites orientent une vérification sur place. Ce ne sont pas des adresses : ils sont choisis parmi les chefs-lieux et les points de canton, sur une grille de population modélisée. »

---

### Section 6 — Synthèse chiffrée et limite

**Synthèse chiffrée**, à l’horizon choisi : habitants ; auto-écoles à ouvrir ; km à remettre en état ; ruraux à plus de 2 km ; permis moto à délivrer dans l’année ; tués à éviter pour suivre la cible.

**Limite :**

> « Ces chiffres sont des estimations, pas des prévisions. Ils supposent la population projetée par l’INSEED et les leviers à leur dernière observation : auto-écoles de 2021-2022, état du réseau relevé en 2020. Ils ne chiffrent aucun coût, et ne prêtent aux actions aucun effet sur les accidents : les données ne permettent pas de le mesurer. »

**Sources de la page :** `horizon_A1.csv`, `population_A1.csv`, `national_A1.csv`, `acces_A1.csv`, `emplacements_A1.csv`, `sites_A1.csv`, `cartes_10.csv`, `geo/*.geojson`.

**Textes lus dans les CSV :** réécrits à l’affichage selon la règle commune (11 §4.2), comme sur toutes les pages. Les identifiants de recommandation, les codes d’indicateur et les renvois aux documents ne s’affichent jamais.

---
