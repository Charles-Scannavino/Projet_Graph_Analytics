# CONTEXT.md — Graph Analytics 2026 | Fish Schooling Networks

> **Version :** 2.0 — 31 octobre 2026  
> **Référence officielle :** `Instructions_Projet.pdf`, *Graph analytics 2026 - Project* (2 pages).  
> **Statut :** cadrage scientifique et technique ; le dataset, les scripts et les résultats restent à valider.  
> **Rôle du document :** préciser le sujet, les exigences d'évaluation, les choix méthodologiques proposés et les conditions de reproductibilité.

## 1. Présentation du projet

- **Formation :** MSc Data & IA for Sustainability — Albert School / Mines Paris PSL.
- **Cours :** Graph Analytics, année 2026.
- **Dépôt GitHub :** https://github.com/Charles-Scannavino/Projet_Graph_Analytics.
- **Titre provisoire :** *Analyse dynamique des réseaux de proximité dans un banc de poissons : cohésion, connectivité et communautés*.
- **Titre anglais :** *Dynamic Graph Analysis of Fish Schooling: Connectivity, Centrality and Communities*.
- **Équipe :** groupe de **2 étudiants** : Charles Scannavino et **second membre à renseigner**.
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

## 3. Données expérimentales envisagées

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
- **P2, option :** Neo4j, simulation comportementale, 3D, animation, LLM.

**Dates officielles :** dépôt du rapport le **10 novembre 2026 à 08:00** ; soutenance le même jour **14:00–17:00**.

### 6.1. Points à confirmer

- Identité et répartition des tâches du binôme.
- Disponibilité effective du dataset et de son format.
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
- **Données candidates :** Oregon State University, *Fish Schooling Data Subset*, https://ir.library.oregonstate.edu/concern/datasets/zk51vq07c?locale=en.
- **Méthode de simulation éventuelle :** Reynolds, C. W. (1987), *Flocks, Herds, and Schools: A Distributed Behavioral Model*.
- **Outils :** Python/NetworkX ; Neo4j/Cypher facultatifs.