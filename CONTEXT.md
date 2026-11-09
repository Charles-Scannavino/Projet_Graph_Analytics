# CONTEXT.md — Graph Analytics 2026 | Fish Schooling Networks

> **Version :** 2.1 — 31 octobre 2026 (audit empirique)
> **Référence officielle :** `Instructions_Projet.pdf`, *Graph analytics 2026 - Project* (2 pages).
> **Statut :** données 2D réellement lues et vérifiées ; métriques calculées sur plusieurs snapshots en environnement d'audit ; scripts définitifs, unités physiques et rapport restent à valider.
> **Rôle du document :** préciser le sujet, les exigences d'évaluation, les choix méthodologiques proposés et les conditions de reproductibilité.

## Consigne permanente pour les scripts exécutés dans un terminal

**Règle demandée par l'utilisateur — à appliquer à tout nouveau script ou module exécuté depuis le Terminal :**

> Toujours intégrer des affichages `print(..., flush=True)` permettant de suivre la progression du programme pendant son exécution, et pas seulement son résultat final.

- Au démarrage : afficher le module, les paramètres principaux et les fichiers d'entrée.
- Avant/après chaque grande étape : chargement, préparation des données, construction des graphes, métriques, sauvegarde.
- Pour les opérations longues : progression périodique (par exemple toutes les 10 % des frames ou toutes les 100 frames) avec nombre d'éléments traités, sans imprimer une ligne pour chaque poisson.
- À la fin : afficher le bilan, le chemin des résultats produits et le succès ou l'échec.
- En cas d'erreur anticipée : émettre un message suffisamment explicite pour identifier l'étape défaillante.
- Dans les fonctions réutilisables : utiliser si besoin un paramètre `verbose=False` ou un mécanisme de progression externe, afin que les tests unitaires restent lisibles ; **activer le suivi dans les points d'entrée exécutés depuis le Terminal**.
- Pour les tests, lancer `python -m pytest -v` (et `-s` lorsqu'il faut voir les `print`).

Cette consigne concerne aussi les exemples de commandes et tout nouveau code fourni pour ce projet.

## 1. Présentation du projet

- **Formation :** MSc Data & IA for Sustainability — Albert School / Mines Paris PSL.
- **Cours :** Graph Analytics, année 2026.
- **Dépôt GitHub :** https://github.com/Charles-Scannavino/Projet_Graph_Analytics.
- **Titre provisoire :** *Analyse dynamique des réseaux de proximité dans un banc de poissons : cohésion, connectivité et communautés*.
- **Titre anglais :** *Dynamic Graph Analysis of Fish Schooling: Connectivity, Centrality and Communities*.
- **Équipe :** groupe de **2 étudiants** : Charles Scannavino et Jacques Chevolot.
- **Objet :** convertir les observations individuelles de poissons (positions et, si disponibles, vitesses) en graphes de proximité, puis analyser mathématiquement l'organisation collective.
- **Question de recherche envisagée :** *Dans quelle mesure les mesures de connectivité, de distance, de centralité et de communauté d'un réseau de proximité permettent-elles de caractériser l'organisation spatiale d'un banc de poissons et ses variations temporelles ?*
- **Contribution centrale :** conception justifiée d'un graphe à partir de données spatiales non structurées comme graphe ; analyse quantitative et interprétation scientifique reproductibles.

### 1.1. Périmètre

Le projet évalué porte d'abord sur les **graphes et leurs propriétés**. Il ne nécessite ni simulateur, ni reconstruction 3D, ni chatbot. Les animations, les graphes temporels détaillés, les expériences Boids/Reynolds, Neo4j et l'interprétation par LLM sont des pistes **facultatives**, à traiter seulement après les exigences obligatoires.

## 2. Énoncé de l'enseignant : exigences officielles

### 2.1. Objet et intégrité académique

1. Choisir un dataset représentable par un graphe et utiliser des méthodes de Graph Analytics pour répondre à une **question claire**.
2. Les données d'entrée n'ont pas besoin d'être un graphe : la définition et la justification du modèle sont particulièrement valorisées.
3. Décrire l'origine du dataset et préciser **tout code préexistant effectivement utilisé** dans le travail remis.
4. Citer les auteurs et les sources de **tout code provenant d'Internet** ; un code externe non attribué constitue du plagiat et expose à une note de zéro.
5. Former un groupe de **2 étudiants exactement**.

### 2.2. Analyses requises

| Exigence | Ce que le rapport devra démontrer |
|---|---|
| Nature du graphe | Signification des nœuds et arêtes ; graphes orientés/non orientés ; simples/multigraphes |
| Construction | Règle de création des arêtes ; attributs des nœuds ; poids et attributs des relations |
| Taille | Nombre de sommets `N = |V|` et d'arêtes `M = |E|` |
| Connectivité | Connexe ou déconnecté ; composantes et signification des isolés ; connectivité forte/faible si orienté |
| Distances | **Diamètre et rayon**, méthode et convention annoncées ; en cas de déconnexion, calcul par composante ou sur une composante explicitement choisie |
| Centralités | Mesures pertinentes, définitions et interprétation pour les poissons |
| Communautés | Recherche de communautés si appropriée ; algorithme et interprétation, y compris si le partitionnement est peu probant |
| Reproductibilité | Logiciels, versions, algorithmes, paramètres, étapes de calcul et explications suffisantes |

### 2.3. Logiciels

- L'énoncé autorise **NetworkX ou Neo4j** : l'utilisation conjointe n'est pas imposée.
- **Choix technique proposé :** Python + NetworkX pour construire et analyser les graphes, compte tenu des délais et de la reproductibilité.
- **Neo4j/Cypher/GDS :** complément possible si les mesures obligatoires, les résultats et les livrables sont déjà opérationnels.

### 2.4. Livrables et calendrier officiels

| Élément | Consigne |
|---|---|
| Groupe | Exactement **2 étudiants** |
| Rapport | Un **PDF par groupe**, **15 pages maximum** |
| Modèle de rapport | Utiliser le **template fourni sur Inside** |
| Rapport — mentions | Noms des deux membres, sources, méthodes, résultats, lien GitHub, déclaration de l'usage éventuel d'outils d'IA et de leur rôle |
| GitHub | Code d'analyse, données si le volume le permet, `README.md` de reproduction |
| Données volumineuses | Hébergement externe permis ; renseigner le lien dans le README |
| **Remise** | **10 novembre 2026 à 08:00**, sur **Inside** |
| **Soutenance** | **10 novembre 2026, 14:00–17:00** |
| Présentation | **8 minutes** + **2 minutes de questions**, deux membres prennent la parole |
| Présence | Obligatoire durant l'intégralité de la session de soutenance |
| Évaluation | **Rapport : 60 %** ; **oral : 40 %** |
| Critère essentiel | Qualité, profondeur, pertinence et interprétation de l'analyse ; non la taille du dataset |

## 3. Données expérimentales et audit

### 3.0. Audit vérifié le 31 octobre 2026

**Source effectivement accessible :** dossier Drive de travail (non destiné à être publié en totalité), contenant `Data/schooling_frames.json` (86 762 262 octets) et `Data/README.txt`. Référence scientifique : Katz et al., *Fish Schooling Data Subset*, Oregon State University, DOI [10.7267/zk51vq07c](https://doi.org/10.7267/zk51vq07c), licence **CC BY 4.0** selon le README du jeu. Le README documente 300 golden shiners, 5 000 frames à 30 fps, bassin 2,1 × 1,2 m de faible profondeur.

**Contrôles exécutés sur le JSON complet, indépendamment de la simulation :**
- 5 000 frames numérotées de `1` à `5000`, 1 118 118 enregistrements individuels cumulés.
- Entre 87 et 289 individus détectés par frame ; moyenne 223,62, médiane 253.
- 10 751 identifiants `onfish` distincts au total : ce sont des **identifiants de segments de suivi**, pas 10 751 poissons physiques.
- Toutes les frames comportent les tableaux `px`, `py`, `vx`, `vy`, `onfish` avec longueurs cohérentes ; aucun doublon d'identifiant **au sein d'une frame**.
- Amplitude globale observée : `x` environ 155,46 à 1848,89 et `y` environ 40,71 à 1034,70 en **unités du fichier à confirmer**. Les vecteurs `(vx, vy)` ont une norme numérique de 1 sur les frames vérifiées : ne pas les interpréter automatiquement comme une vitesse physique en mm/s.
- Une frame enregistrée est une observation **réelle** ; les trajectoires produites par une éventuelle simulation doivent être distinguées des données observées.

**Premiers graphes de proximité calculés avec NetworkX (seuil numérique `d < R`, graphe simple non orienté, distances euclidiennes non normalisées) :**

| Frame | R | Sommets | Arêtes | Composantes | Diamètre LCC | Rayon LCC | Clustering moyen |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 60 | 253 | 454 | 35 | 38 | 19 | 0,4067 |
| 1 | 100 | 253 | 1 281 | 4 | 23 | 12 | 0,5780 |
| 1 | 120 | 253 | 1 824 | 3 | 19 | 10 | 0,6161 |
| 1000 | 100 | 251 | 2 017 | 2 | 14 | 7 | 0,5895 |
| 5000 | 100 | 262 | 1 249 | 3 | 24 | 12 | 0,5593 |

LCC = plus grande composante connexe ; diamètre et rayon calculés en **nombre de sauts** sur cette composante, pas sur le graphe déconnecté entier. Les valeurs ci-dessus sont **des contrôles exploratoires vérifiés**, pas les résultats définitifs du rapport. Les seuils 60/100/120 doivent être justifiés et les analyses reproduites depuis un script propre.


### Référence scientifique : champ visuel du Golden shiner

- **Espèce des observations :** *Notemigonus crysoleucas*, dit *Golden shiner* (méné jaune). Source du dataset : Katz et al., *Fish Schooling Data Subset* (Oregon State University), DOI [10.7267/zk51vq07c](https://doi.org/10.7267/zk51vq07c).
- **Mesure publiée, espèce spécifique :** Pita D., Moore B. A., Tyrrell L. P. et Fernández-Juricic E. (2015), *Vision in two cyprinid fish: implications for collective behavior*, PeerJ 3:e1113, [DOI 10.7717/peerj.1113](https://doi.org/10.7717/peerj.1113). La largeur moyenne du **secteur aveugle arrière horizontal** est de **25° ± 1,20°**, et la couverture visuelle horizontale moyenne **335° ± 3,5°**, chez neuf poissons adultes examinés par méthode ophtalmoscopique avec les yeux en position de repos. Les ± sont les erreurs standard rapportées, et non une plage de variation individuelle.
- **Corroboration :** Davidson J. D. et al. (2021), *Collective detection based on visual information in animal groups*, *Journal of the Royal Society Interface*, [DOI 10.1098/rsif.2021.0142](https://doi.org/10.1098/rsif.2021.0142), applique explicitement un angle aveugle arrière de 25° à cette espèce.
- **Comparaison interespèces :** les modèles classiques adoptent parfois une couverture visuelle de 300° / zone aveugle arrière de 60°, historiquement tirée d'autres espèces. Il **n'existe pas d'angle mort moyen universel des poissons**.
- **Décision méthodologique fixée le 03/11/2026 :** pour le **graphe orienté de visibilité**, utiliser exclusivement `rear_blind_angle_deg=25` (**largeur TOTALE** du secteur arrière, donc champ visible horizontal nominal 335°) pour tous les poissons et toutes les frames. **Aucune variation de l'angle mort n'est prévue dans l'étude.** Les valeurs `60` et `240` ne sont pas retenues dans l’analyse finale et ne constituent pas des mesures physiologiques du Golden shiner.
- **Point de rigueur :** le graphe actuel fondé sur `(vx,vy)` estime un **axe de déplacement**, utilisé comme approximation de l'orientation du corps. Il n'intègre ni mouvement des yeux, ni occlusion par les voisins, ni géométrie visuelle 3D. Une valeur de champ anatomique ne valide donc pas directement les arcs de visibilité calculés.
- **Statut du code :** `src/visibility_graph.py` local accepte déjà `rear_blind_angle_deg` comme argument. Les valeurs 60° et 240° ont été exécutées et testées ; **25° n'a pas encore été exécuté/testé dans cette session**. Ne pas lui attribuer de résultat numérique avant exécution.

### Décision méthodologique définitive — 3 novembre 2026 : angle mort constant à 25°

**Décision explicite du responsable du projet :** l'angle mort horizontal arrière du *Golden shiner* sera **fixé à 25° pour tous les poissons, toutes les frames et l'intégralité de l'analyse directionnelle**. Le champ de vision nominal sera donc **335°**. La valeur est une moyenne anatomique issue de Pita et al. (2015), employée comme **hypothèse constante** du modèle, et non une mesure individualisée de chaque poisson. **Aucune analyse de sensibilité sur l'angle mort n'est prévue.**

- Paramètre de référence : `rear_blind_angle_deg = 25` (secteur arrière total, centré à 180° de la direction de déplacement).
- Arc `i -> j` si `d(i,j) < R` et `abs(wrap(phi_ij - theta_i)) <= 167,5°` ; la distance `R` reste un paramètre distinct, pouvant faire l'objet d'une analyse de sensibilité.
- Conserver le **graphe spatial non orienté** comme baseline indépendante de l'angle mort ; le graphe directionnel conserve l'angle à 25°.
- Les exécutions historiques **60°/240°** sont documentées uniquement comme essais exploratoires effectués avant cette décision. **Ne pas les reprendre dans les résultats finaux ni les présenter comme variantes scientifiques de l'étude.**
- Mettre à jour le **script local** `src/visibility_graph.py` pour utiliser 25° par défaut et dans son exécution principale ; vérifier les tests correspondants. L'actualisation de GitHub ci-dessous est documentaire : le code local n'est pas encore publié.
- Réserve : `(vx,vy)` indique la direction de déplacement, utilisée comme approximation de l'orientation visuelle ; occlusions et variabilité individuelle non modélisées.

### 3.1. Dataset principal candidat

**Fish Schooling Data Subset — Oregon State University**
Source à citer : https://ir.library.oregonstate.edu/concern/datasets/zk51vq07c?locale=en

Caractéristiques documentaires à **confirmer par inspection des fichiers** :

- Étude expérimentale d'un banc de **300 golden shiners** (*Notemigonus crysoleucas*).
- Sous-ensemble annoncé de **5 000 frames**, enregistrées à **30 images/seconde**.
- Positions bidimensionnelles et vitesses : `px`, `py`, `vx`, `vy`.
- Champ `onfish`, à vérifier pour identifier les segments de suivi.
- Le nombre d'individus détectés par frame peut différer de l'effectif total, et les identifiants ne sont pas garantis permanents.
- **Statut au 31/10/2026 :** URL source connue ; copie exploitable du fichier, licence, unités et schéma exacts **non vérifiés dans ce dépôt**.

**Contrôles indispensables avant le calcul :**

1. Accès effectif aux données et intégrité du téléchargement.
2. Structure du JSON ou du format disponible ; nombre de frames et observations.
3. Unicité des identifiants par frame ; continuité et interruptions des segments de suivi.
4. Unités de position et de vitesse, dimensions du bassin et coordonnées extrêmes.
5. Valeurs manquantes, doublons, coordonnées aberrantes et cohérence temporelle.
6. Licence, publication/auteurs, date d'accès, citation et éventuels traitements de données.

### 3.2. Alternatives ou extensions à évaluer si nécessaire

| Ressource | Dimension | Adresse | Usage éventuel |
|---|---|---|---|
| Puy et al. (2026) | 2D | https://zenodo.org/records/17141691 | Relations temporelles, stabilité et positions relatives |
| Watts et al. | 3D | https://doi.org/10.5061/dryad.j0226 | Comparaison des graphes obtenus par distances 2D et 3D |
| 3D-ZeF | 3D | https://motchallenge.net/data/3D-ZeF20 | Analyses 3D avec étape de préparation du suivi |

**Statut :** références candidates, sans audit ni intégration validés. Ces ressources n'élargissent pas le périmètre par défaut.

## 4. Hypothèses et analyses scientifiques

### 4.1. Problématique opérationnelle

*Comment les propriétés topologiques d'un graphe de voisinage permettent-elles d'évaluer la cohésion, la fragmentation et les différences d'organisation spatiale d'un banc de poissons ?*

### 4.2. Hypothèses à tester, non résultats acquis

- **H1 — Cohésion :** à rayon de voisinage fixé, une configuration spatiale plus concentrée pourrait présenter un degré moyen plus élevé et une composante principale plus importante.
- **H2 — Fragmentation :** des séparations spatiales pourraient se traduire par une augmentation du nombre de composantes, sans nécessairement coïncider avec les communautés détectées.
- **H3 — Centralités :** certains individus occupent potentiellement une position topologique particulière, sans que cela démontre une influence comportementale causale.
- **H4 — Variation temporelle (option) :** les métriques pourraient différer entre plusieurs états collectifs effectivement identifiés dans les observations.

### 4.3. Construction du graphe proposée

Pour un instant `t`, définir `G_t = (V_t, E_t)` :

- **Nœud :** poisson observé à cet instant, identifié de manière unique **dans la frame**.
- **Attributs de nœud :** `px`, `py` et, si disponibles, `vx`, `vy`, `frame_id`, `track_id`.
- **Arête :** proximité spatiale entre deux poissons distincts `i` et `j`.
- **Distance euclidienne :** `d_ij = sqrt((px_i-px_j)^2 + (py_i-py_j)^2)`.
- **Règle candidate :** `(i,j) ∈ E_t` si `d_ij ≤ R`, avec `R` déterminé après vérification des unités et une étude de sensibilité ; convention exacte à fixer.
- **Type :** graphe **simple, non orienté, sans boucle**, sauf justification scientifique contraire.
- **Attribut d'arête :** `distance = d_ij`, avec unité documentée. Pour le diamètre et le rayon topologiques, les chemins pourront être **non pondérés** (nombre de sauts) ; bien distinguer les deux notions de distance.

Si le graphe est déconnecté : ne pas attribuer de diamètre/rayon global fini. Calculer ces mesures sur la **plus grande composante connexe** ou par composante, en annonçant et justifiant la convention retenue.

### 4.4. Mesures et méthodes proposées

- `N`, `M`, degré moyen et distribution des degrés.
- Connectivité ; nombre et taille des composantes ; part de la plus grande composante (`LCC`).
- **Diamètre** : maximum des distances des plus courts chemins dans la composante choisie.
- **Rayon** : minimum des excentricités dans cette même composante.
- Centralité de degré ; centralité d'intermédiarité, et éventuellement de proximité avec traitement explicite des composantes.
- Communautés avec Louvain (si compatible) ou une alternative justifiée ; tailles, modularité et interprétation.
- Coefficient de clustering et densité comme compléments.
- Comparaison de quelques frames ou variations de `R` pour tester la robustesse, sans traiter des observations temporellement proches comme indépendantes.

**Limite fondamentale :** un lien géométrique ne prouve ni communication effective ni leadership. Les communautés d'un graphe spatial peuvent être produites en partie par la règle de construction.

### 4.5. Extension scientifique — simulation Boids et comparaison aux observations

**Décision de cadrage du 3 novembre 2026 :** ajouter au projet un axe complémentaire de **simulation du comportement collectif avec les règles de Boids**, suivi d'une **comparaison quantitative entre les trajectoires expérimentales et les trajectoires simulées**. Ce volet est **prévu et non encore implémenté** dans le dépôt Graph Analytics 2026 ; priorité **P1**, après satisfaction des exigences P0 (mesures topologiques, centralités, communautés, figures, rapport).

**Nouvelle question secondaire :** « Dans quelle mesure les règles locales de séparation, alignement et cohésion permettent-elles de reproduire les propriétés dynamiques et topologiques des bancs de *Golden shiners* effectivement observés ? »

#### B1 — Simulateur Boids

- Forces : **séparation** (évitement des proches), **alignement** (tendance à suivre les directions locales), **cohésion** (attraction vers les voisins). Référence fondatrice : Reynolds (1987), [DOI 10.1145/37402.37406](https://doi.org/10.1145/37402.37406).
- **Angle mort impérativement fixé à 25°** (champ de vision 335°) dans la recherche des voisins de chaque agent, comme dans le graphe directionnel de l'étude. Conserver une définition explicite et constante de la largeur totale du secteur aveugle arrière.
- Repartir d'une **frame expérimentale initiale**, puis laisser évoluer librement la simulation sur plusieurs pas : ne jamais injecter les observations futures dans la simulation « libre ». Utiliser des règles de bord et une vitesse compatibles avec les données observées.
- **Attention aux unités** : `(vx,vy)` dans le JSON ressemble à des **directions normalisées**, pas à une vitesse physique. Le JSON fournit 30 fps, et les paramètres de temps et de vitesse doivent être définis dans des unités cohérentes. Estimer les déplacements/vitesses sur segments d'identifiants de suivi stables.
- **Système de suivi :** `onfish` peut être réattribué/rompu entre frames ; le nombre d'individus détectés varie. Commencer par des fenêtres courtes avec individus correctement appariés (ou comparer des indicateurs de groupe robustes à la disparition des détections).
- Ajouter des `print(..., flush=True)` de progression et une graine RNG fixe si le simulateur utilise de l'aléatoire.

#### B2 — Confrontation quantitative réel vs simulé

1. **Même point de départ** : frame expérimentale observée `t0`, même groupe, même échelle spatiale et convention de temps ; simuler un horizon court (`t0+H`) et comparer aux observations sans réinitialisation à chaque frame.
2. **Comparer les graphes construits à l'identique** sur les deux séries (même `R`, même angle de visibilité 25°) : `N`, nombre de liens, degré moyen, composantes/LCC, clustering, éventuellement modularité/Louvain (seed fixé) et densité.
3. **Comparer les comportements** : distribution des distances au plus proche voisin, polarisation (norme de la moyenne des directions unitaires), distribution des changements de cap, éventuel étalement/compacité, erreurs de trajectoire si identifiants appariés fiables.
4. **Calibrer les paramètres** de forces sur une ou plusieurs fenêtres d'entraînement, puis **évaluer sur d'autres fenêtres temporelles non utilisées pour le réglage** ; mesurer erreurs et variabilité entre fenêtres et, le cas échéant, graines.
5. **Ablations** : comparer le modèle complet à des variantes sans séparation, sans cohésion ou sans alignement et à une baseline de persistance du mouvement. Retirer une règle permet d'évaluer son apport prédictif dans **ce simulateur**, pas de prouver qu'elle est suivie biologiquement.
6. **Conclusion** : discuter ce que Boids explique et n'explique pas et les biais du modèle (suivi, orientation, vitesse, confondants, bords, retard de réponse, interactions à trois). Des graphes ressemblants ne prouvent **pas** que les mêmes règles individuelles sont utilisées.

**Mise en garde scientifique spécifique à l'espèce :** Katz et al. (2011), *Inferring the structure and dynamics of interactions in schooling fish*, [DOI 10.1073/pnas.1107583108](https://doi.org/10.1073/pnas.1107583108), infèrent des règles à partir de trajectoires de *Golden shiners* et rapportent que l'alignement peut émerger de l'attraction/répulsion sans appariement explicite des orientations. Le projet doit donc parler de **compatibilité avec Boids**, de **qualité de reproduction** et de **contribution prédictive des règles**, non de démonstration que toutes les règles sont « respectées ».

**Organisation logicielle envisagée :** `src/boids_simulation.py` (simulation assainie), `src/boids_comparison.py` (fenêtres et métriques), `tests/test_boids.py` (invariants et régression), `results/` (courbes/comparatifs). Recommandation : livrer d'abord un **prototype d'une fenêtre** et deux ou trois métriques robustes, avant de viser les 5 000 frames.

## 5. Architecture logicielle proposée

La structure ci-dessous est **une cible de dépôt**, et non la description de fichiers déjà créés :

```text
Graph_Analytics_2026/
├── README.md                     # objectif, sources, installation, reproduction
├── CONTEXT.md                    # contexte scientifique et exigences
├── AVANCEMENT.md                 # suivi des tâches et validations
├── requirements.txt             # ou pyproject.toml
├── data/
│   ├── raw/                     # données originales ou lien externe dans le README
│   └── processed/               # sous-ensembles documentés
├── src/
│   ├── data_audit.py            # validation du dataset
│   ├── graph_builder.py         # construction du graphe
│   ├── graph_metrics.py         # indicateurs obligatoires
│   └── visualize.py             # visualisations
├── results/
│   ├── tables/
│   └── figures/
├── report/                       # rapport ≤15 pages avec template Inside
└── slides/                       # soutenance 8 + 2 minutes
```

Commencer par le minimum exécutable : lecture d'une frame, création d'un graphe, métriques obligatoires, figures et rapport. N'ajouter des modules que s'ils répondent à une question de recherche.

### 5.1. Reproductibilité et attribution

- **Données :** documenter institution, publication/auteurs, URL/DOI, licence si connue, date d'accès, fichiers et transformations.
- **Code :** documenter l'origine de chaque portion de code préexistante effectivement incorporée, personnelle ou tierce, et distinguer les développements du groupe. Citer précisément les contributions tierces provenant d'Internet.
- **IA :** déclarer honnêtement les outils d'IA effectivement employés pour le rendu, leur fonction (cadrage, rédaction, programmation ou interprétation) et les validations humaines.
- **Exécution :** donner versions, commande d'installation, commandes de lancement, sélection des frames, définition de `R` et outputs attendus.
- **Sécurité :** exclure `.env`, secrets et éventuelles clés API du dépôt.

## 6. Priorités et jalons

- **P0, impératif :** dataset réellement lisible ; modèle de graphe justifié ; `N`, `M`, connectivité, composantes, diamètre, rayon, centralités et communautés ; interprétation.
- **P0, livrables :** rapport PDF ≤15 pages conforme au template Inside, GitHub avec code et README, déclaration des sources/code/IA, oral de 8 minutes avec deux intervenants.
- **P1, approfondissement :** comparaison de plusieurs frames, sensibilité au rayon `R`, figures statistiques et robustesse.
- **P2, option :** Simulation comportementale et animations.

**Dates officielles :** dépôt du rapport le **10 novembre 2026 à 08:00** ; soutenance le même jour **14:00–17:00**.

### 6.1. Points à confirmer

- Identité et répartition des tâches du binôme.
- ✅ Disponibilité et structure du dataset 2D vérifiées le 31 octobre 2026.
- Unités physiques, identification temporelle, frame(s) et rayon `R`.
- Modèle de rapport Inside.
- Algorithmes de communautés, choix final des centralités et résultats effectivement mesurés.

## 7. Règles de travail

1. Distinguer dans toutes les présentations **exigences**, **propositions**, **vérifications** et **résultats réellement mesurés**.
2. Ne jamais fabriquer de chiffres, de tests, de captures ou de résultats de graphes.
3. Conserver les observations brutes et documenter chaque transformation.
4. Annoncer les conventions utilisées pour les graphes vides, déconnectés ou comportant des sommets isolés.
5. Prioriser la qualité scientifique des résultats et la reproductibilité sur le nombre de fonctionnalités.
6. Actualiser `AVANCEMENT.md` avec des preuves (fichiers, commandes, sorties), des blocages et des étapes suivantes.
7. Respecter la limite de 15 pages, la présentation de 8 minutes et la date de remise.

## 8. Références

- **Énoncé :** `Instructions_Projet.pdf`, *Graph analytics 2026 - Project* (2026).
- **Données utilisées pour l'audit :** Katz et al. (2021), *Fish Schooling Data Subset*, Oregon State University, DOI https://doi.org/10.7267/zk51vq07c, licence CC BY 4.0 d'après `Data/README.txt`.
- **Méthode de simulation éventuelle :** Reynolds, C. W. (1987), *Flocks, Herds, and Schools: A Distributed Behavioral Model*.
- **Outils :** Python/NetworkX ; Neo4j/Cypher facultatifs.

---

## Actualisation de l'architecture — 9 novembre 2026

La section 4.5 et l'architecture initiale décrivent le cadrage
historique du projet. Une partie de cette extension a depuis été
implémentée.

Les modules récupérés couvrent notamment :

1. La simulation Boids.
2. La calibration et l'optimisation des paramètres.
3. Les comparaisons réel/simulé.
4. Les métriques structurelles et comportementales.
5. L'analyse exploratoire du leadership.
6. La validation sur plusieurs fenêtres temporelles.

Les programmes sont présents dans `src/`, les tests dans `tests/`,
et les résultats sauvegardés dans `results/simulation/`
et `results/leadership/`.

Le modèle conserve comme convention méthodologique un angle mort
arrière de 25 degrés. La conformité de chaque module à cette
convention reste à vérifier individuellement.

Les analyses de leadership sont exploratoires et ne constituent
pas une preuve d'interaction causale.

Les anciennes propositions de noms de modules doivent être
considérées comme des intentions de conception historiques,
et non comme la liste actuelle des fichiers.
