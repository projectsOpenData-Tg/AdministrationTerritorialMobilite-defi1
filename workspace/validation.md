# Validation des recherches complémentaires

## Verdict global

**Travail remarquable.** La recherche est exhaustive (portail, INSEED, sources internationales), la méthode est transparente, et les résultats sont honnêtes. Sur les 11 points à valider, **j'en valide 8 tels quels, j'en nuance 2, j'en rejette 1**.

Le seul point vraiment structurant est le **n° 1** (accidents par territoire) : c'est lui qui décide si l'objectif 5 peut croiser risque et territoire, ou s'il reste organisé par levier.

---

## 1. Validation point par point

### Point 1 — Accidents par territoire : **Option A validée**

**Ce qui est proposé :** ne pas utiliser les chiffres régionaux dans les calculs, les citer en méthodologie, en tirer une recommandation « données ».

**Pourquoi c'est le bon choix :**

- Les données sont **hétérogènes** : 3 régions sur 5, variables différentes selon la région, Grand Lomé absent. Comparer la Maritime (gendarmerie seule) à la Centrale (gendarmerie + police) produirait un classement faux.
- Les **qualités sont douteuses par endroits** : chiffres identiques en 2019 et 2020 dans la Centrale, ligne « Ensemble » qui ne somme pas dans la Kara. Ces erreurs sont documentées dans le fichier lui-même.
- L'**option B** (encadré illustratif) ferait courir un risque réel : un lecteur pressé lirait ces chiffres comme un classement. Le 02 est figé, le repli est déjà prévu (pas de classement territorial du risque, recommandations par levier). L'option A respecte cette logique.
- La **recommandation « données »** transforme l'absence en action : « publier les accidents par préfecture selon un format commun police/gendarmerie ». C'est exactement ce que le 01 §3.5 appelle une recommandation de type « collecte de données ».

**Ma seule réserve :** la recommandation « données » doit apparaître dans le tableau de bord, pas seulement dans le rapport. Un encadré « ce que les données ne permettent pas de dire » dans la page O2 ou O5, avec la recommandation associée.

---

### Point 2 — Population : **validé**

**Pourquoi :**

- Les **projections 2011–2031** (national, âge, sexe, chaque année) permettent à O1-04 et O1-07 de passer **du repli à la maille cible**. C'est un gain direct sur 2 indicateurs sur 43.
- Le **Livret 02 du RGPH-5** (2022, âge × sexe × milieu, jusqu'à la préfecture) rend **PA-03 calculable**, donc **H8 testable**. C'est un gain sur une hypothèse entière.
- L'écart de **0,3 %** entre projections et recensement en 2022 est négligeable mais doit être documenté en 04.

**Réserve :** les 47 tableaux du Livret 02 sont en PDF. L'extraction en 04 doit être scriptée et vérifiée (totaux préfectoraux = totaux nationaux).

---

### Point 3 — Âges minimaux des permis : **validé, étiqueté C**

**Pourquoi :**

- Mieux vaut un âge étiqueté C qu'un âge par défaut à 18 ans pour toutes les catégories.
- Les sources secondaires sont **concordantes** (GAPOLA, Basileia, service-public.gouv.tg).
- L'étiquette C est correcte : le texte officiel (décret 2022-085) n'a pas été trouvé en ligne.

**Réserve :** en 04, tenter une dernière recherche du décret officiel. S'il est trouvé, passer de C à A.

**Méthode de calcul du dénominateur :** la règle « 2/5 des 15–19 ans + 20 ans et plus » est raisonnable. À documenter explicitement dans `03_Seuils` PA-05 ou dans une note du 04.

---

### Point 4 — Année de référence : **validé, avec précision**

**Pourquoi :**

- **2022 pour tout ce qui est territorial** est le bon choix : recensement, parc, permis s'arrêtent en 2022. Le 01 §2.3 le prévoyait déjà.
- **2023–2024 pour la courbe nationale des accidents** est utile pour montrer la tendance récente. Mais attention : cette courbe ne doit pas être confondue avec l'analyse territoriale.

**Précision à ajouter :** dans le tableau de bord, la page « accidents » doit clairement séparer :

- la **courbe nationale** 2010–2024 (tendance longue) ;
- les **chiffres 2022** utilisés dans les taux et les croisements.

Sinon un lecteur pourrait croire que le taux de tués de 2024 est comparable à celui de 2022 sur la même base de population.

---

### Point 5 — Chronologie D11 : **validé**

**Pourquoi :**

- Les **six dates sourcées** (2013, 2019, 2022, 2023) expliquent les ruptures attendues : permis moto obligatoire en 2019, campagne d'immatriculation des motos en 2019, sous-catégories A1–A3 en 2022.
- Sans cette chronologie, on lirait une rupture en 2019 comme un artefact de données, alors qu'elle est réelle.
- C'est du **contexte**, pas un indicateur. Aucune modification du 02 n'est nécessaire.

**Réserve :** la chronologie doit apparaître comme **annotation sur les courbes** de O1, pas comme un tableau séparé. Une ligne verticale « 2019 : permis moto obligatoire » sur la courbe des permis A, par exemple.

---

### Point 6 — Équipements de sécurité routière : **nuancé**

**Ce qui est proposé :** ne pas les retenir par défaut, à cause de l'exhaustivité inconnue.

**Mon avis :** je nuancerais.

- Ils sont **datés 2021–2022** (collecte PRISE), comme D5 et D6. Ce n'est pas un défaut.
- Ils sont **géolocalisés et rattachés à la préfecture** (39 préfectures pour les panneaux et ralentisseurs).
- Ils sont **hors 02** (aucun indicateur ne les utilise), donc ils ne peuvent pas entrer dans le classement.
- Mais ils pourraient servir de **couche de contexte optionnelle** sur la carte des recommandations, en clair « non utilisée dans les indicateurs ».

**Proposition :** les retenir comme **couche togglable** sur la carte O5, désactivée par défaut, avec un libellé explicite. Si le tableau de bord a la place, c'est un plus pour le décideur. Sinon, les citer en méthodologie comme « données disponibles non utilisées ».

**Ce que je rejetterais :** les intégrer dans un indicateur ou un profil. Ils ne mesurent pas le risque.

---

### Point 7 — Contexte entretien et coût : **nuancé**

**Ce qui est proposé :** optionnel.

**Mon avis :**

- **Longueur de route entretenue (2016–2019)** : oui, comme contexte de O3. Cela permet de comparer l'**effort** (km entretenus) à l'**état** (relevé 2020). Un territoire qui entretient peu et dont le réseau se dégrade, c'est une information utile pour le levier entretien. Mais c'est national, non territorial. Donc à afficher en **annexe nationale**, pas dans le classement.
- **Charges de sinistres automobiles (2014–2022)** : je ne le retiendrais pas. C'est un chiffre d'assurance, pas le coût social. Il donne un ordre de grandeur, mais il est trompeur (les accidents non déclarés n'y sont pas, les dommages corporels pris en charge par l'État non plus). À citer éventuellement en méthodologie, pas en indicateur.

---

### Point 8 — Recommandations « données » : **fortement validé**

**Pourquoi :**

- C'est le **meilleur apport** de cette recherche. Elle transforme un manque en action.
- Trois demandes claires : base d'accidents par préfecture (ONSR), ouverture des couches Dégradations et Ponts, publication de l'activité des auto-écoles.
- C'est exactement le profil **P5 « Non déterminable »** du 02 : « Collecte et ouverture des données manquantes ».

**Proposition :** en faire une **rubrique dédiée** du tableau de bord, à côté des recommandations territoriales. Intitulé : « Pour aller plus loin : ce que les données ne permettent pas encore de dire ».

**Réserve :** ne pas laisser cette rubrique devenir le livrable principal. Le projet doit d'abord produire ce qui est possible avec les données existantes.

---

### Point 9 — Profil OMS 2023 : **fortement validé**

**Pourquoi :**

- **O2-09 devient calculable en repli** (type d'usager, 2021, national). C'est le seul indicateur « Si données » qui passe de non-calculable à calculable.
- **H2 devient testable côté victimes** pour 2021 : 60 % des tués sont en deux-roues.
- L'écart **680 déclarés / 1 961 estimés** (2,9×) documente la sous-déclaration de façon chiffrée. C'est bien plus fort qu'une note qualitative.
- Les **93 944 véhicules immatriculés en 2021** aident à trancher « stock ou flux » en 04.
- L'**état des lois** (casque, alcool, téléphone) alimente D11.

**Réserve :** l'OMS est une **estimation modélisée**, pas un comptage. Le chiffre de 1 961 tués ne doit pas remplacer les 680 déclarés dans les calculs. Il sert de repère (SE-03), pas de correction. Le 02 le prévoyait déjà.

---

### Point 10 — Géoportail : **fortement validé**

**Pourquoi :**

- **Dater D5 et D6 à la collecte PRISE 2021–2022** est une information de traçabilité importante. Sans elle, on ne sait pas si les auto-écoles sont de 2015 ou de 2022.
- La **règle officielle de comptage** des auto-écoles (« agréées + antennes agréées ») tranche la question ouverte du §7 du 03. C'est une réponse ferme.
- La confirmation que les couches **« Dégradations » et « Ponts » existent mais ne sont pas ouvertes** renforce la recommandation « données ».

**Réserve :** le catalogue du géoportail doit être téléchargé dans `data/reference/`, pas seulement cité.

---

### Point 11 — Options modélisées : **validé partiellement**

| Option                                                        | Verdict | Raison                                                                                                                                                           |
| ------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DHS** (possession moto par région)                   | ✅ Oui  | Contexte pour D12 et H2. Donne une idée de l'exposition réelle à la moto, région par région. Étiqueté C.                                                  |
| **WPP** (âges simples)                                 | ✅ Oui  | Améliore PA-05 : au lieu de supposer une répartition uniforme dans les groupes quinquennaux, on a les âges simples. Gain de précision, coût faible.         |
| **WorldPop** (population par préfecture et par année) | ❌ Non  | 2022 suffit pour le territorial. R-06 prévoit la population de l'année la plus proche. Ajouter WorldPop introduirait une source C là où une source A existe. |
| **HeiGIT** (revêtement 2020–2024)                     | ❌ Non  | Ne mesure pas l'état (bon, moyen, mauvais). Mesure le revêtement. Confusion possible avec O3-02. À citer en contexte si utile, pas à intégrer.              |

**Nuance sur WorldPop :** si le 04 confirme que la population par préfecture et par année est vraiment nécessaire pour un taux territorial, WorldPop devient une option de repli. Mais ce n'est pas le cas aujourd'hui.

---

## 2. Ce que la recherche apporte et qui n'était pas demandé

Deux points méritent d'être soulignés :

### 2.1 — La raison de l'absence de données territoriales est maintenant connue

Le Togo n'a **pas encore de base nationale d'accidents**, l'Observatoire de la sécurité routière doit être mis en service (Banque mondiale, 2026), et l'observatoire africain n'a reçu **aucune donnée du Togo en 2021**. Ce n'est pas un oubli de recherche, c'est un fait institutionnel. Cela doit figurer dans la page Méthodologie, pas seulement dans le rapport.

### 2.2 — La comparaison avec les voisins devient possible

Avec le profil OMS et les données Bénin / Ghana / Burkina Faso (D9), le taux de tués du Togo peut être situé. C'est utile pour SE-03 (repère externe).

---

## 3. Risques à surveiller

| Risque                                                              | Où                | Mitigation                                |
| ------------------------------------------------------------------- | ------------------ | ----------------------------------------- |
| Confusion entre courbe nationale et analyse territoriale            | Tableau de bord O2 | Séparer visuellement les deux            |
| Les recommandations « données » deviennent le livrable principal | O5                 | Les placer en annexe, pas en tête        |
| La chronologie D11 est lue comme une cause                          | O1                 | Annotation, pas d'analyse causale         |
| Les chiffres OMS remplacent les chiffres déclarés                 | O2-01, O2-02       | Rappel : OMS = repère, pas correction    |
| Les équipements de sécurité deviennent un indicateur             | O5                 | Couche de contexte, jamais dans un profil |

---

## 4. Tableau de synthèse

| N° | Point                                | Verdict                 | Intégration                            |
| --- | ------------------------------------ | ----------------------- | --------------------------------------- |
| 1   | Accidents par territoire             | ✅ Option A             | Méthodologie + recommandation données |
| 2   | Population (projections + Livret 02) | ✅ Oui                  | D7, O1-04, O1-07, PA-03                 |
| 3   | Âges des permis                     | ✅ Oui, C               | PA-05                                   |
| 4   | Année de référence                | ✅ Oui, avec précision | 2022 territorial, 2024 national         |
| 5   | Chronologie D11                      | ✅ Oui                  | Annotation des courbes O1               |
| 6   | Équipements sécurité              | ⚠️ Nuancé            | Couche optionnelle, pas d'indicateur    |
| 7   | Entretien et coût                   | ⚠️ Nuancé            | Entretien oui en annexe, coût non      |
| 8   | Recommandations données             | ✅ Fort                 | Rubrique dédiée du tableau de bord    |
| 9   | Profil OMS 2023                      | ✅ Fort                 | O2-09, H2, D11, contrôle stock/flux    |
| 10  | Géoportail                          | ✅ Fort                 | Datation D5/D6, règle auto-écoles     |
| 11  | Options modélisées                 | ⚠️ Partiel            | DHS et WPP oui ; WorldPop et HeiGIT non |

---

---

## Verdict final

**La recherche complémentaire est validée à 80 %.** Les 8 points validés enrichissent le projet sans le dénaturer. Les 2 points nuancés (équipements, contexte) doivent être traités avec prudence. Le point 11 (options modélisées) doit être partiellement retenu : DHS et WPP oui, WorldPop et HeiGIT non.

**Le point 1 (accidents par territoire) reste la limite majeure du projet.** Il ne sera pas résolu par cette recherche, et c'est un fait documenté, pas un échec. Le projet doit assumer cette limite et la transformer en recommandation.
