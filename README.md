# Projet Graph Analytics 2026 — Fish Schooling Networks

**Sujet :** Analyse de l'organisation spatiale et temporelle d'un banc de poissons à partir de graphes de voisinage.
**Dépôt :** [Projet_Graph_Analytics](https://github.com/Charles-Scannavino/Projet_Graph_Analytics)
**État au 3 novembre 2026 :** les modules `src/data_loader.py`, `src/graph_builder.py` et `src/visibility_graph.py` ont été publiés sur la branche `main` ; **10 tests `pytest`** ont réussi localement, angle mort arrière fixé à **25°**.
**Documents de pilotage :** [CONTEXT.md](CONTEXT.md) · [AVANCEMENT.md](AVANCEMENT.md).

## 1. Données et provenance

- Dataset : *Fish Schooling Data Subset* (Katz et al., Oregon State University), DOI [10.7267/zk51vq07c](https://doi.org/10.7267/zk51vq07c). Licence CC BY 4.0 indiquée dans le README d'origine.
- `schooling_frames.json` : 5 000 frames à 30 images/seconde ; chaque frame contient `px`, `py`, `vx`, `vy` et `onfish`.
- `onfish` correspond à un **identifiant de suivi**, susceptible de changer lors des pertes/reprises de suivi ; les identifiants ne sont pas des preuves d'identités biologiques permanentes.
- Les vecteurs `(vx, vy)` fournissent la **direction du mouvement** dans les observations vérifiées (norme proche de 1) ; ne pas les qualifier de vitesse physique calibrée.
- Les coordonnées et seuils `R` sont exprimés en **unités natives du fichier**, dont la conversion physique reste à confirmer. Ne pas les étiqueter arbitrairement « mm ».
- Le fichier volumineux doit rester **hors Git** ; le placer localement sous `data/schooling_frames.json` (copie ou lien symbolique). Le dépôt doit fournir les instructions de récupération et citer la source.

## 2. Modèle A : graphe spatial de proximité — modèle de référence VALIDÉ localement

Pour chaque frame, un poisson est un sommet `onfish`. On crée **une arête non orientée** entre deux sommets distincts si :

```text
d(i,j) = sqrt((px_i - px_j)^2 + (py_i - py_j)^2)
A_ij = 1 si d(i,j) < R ; 0 sinon.
```

Le graphe est **simple, non orienté et sans boucle**. Les poissons isolés restent des sommets. Chaque nœud conserve `pos=(px,py)` et `direction=(vx,vy)` ; chaque arête conserve `distance=d(i,j)` comme **attribut géométrique**. Les métriques topologiques de base utilisent les liens sans pondération : la distance géométrique n'est pas le nombre de sauts d'un plus court chemin.

**Attention : ce modèle ne tient PAS compte de la visibilité ni de l'angle mort.** Il constitue la référence symétrique permettant la comparaison de la connectivité, du diamètre, du rayon, des centralités et de Louvain.

### Paramètres exploratoires du modèle A

| Paramètre | Valeur(s) | Statut / signification |
|---|---|---|
| `frame_id` | 1 ; vérifications sur 1000, 2500, 5000 | Frame observée, pas simulée |
| `R` / `radius` | **60, 100, 120** | Seuils exploratoires en unités natives, pas encore calibrés biologiquement |
| Comparaison des distances | `d < R` | Inégalité stricte, pas `<=` |
| Type de graphe | `nx.Graph()` | Non orienté, non pondéré pour la topologie |
| Identification des nœuds | `onfish` | Conserver les IDs de suivi et les sommets isolés |
| Angle mort / champ visuel | **non appliqué** | Aucun filtre d'orientation dans le modèle A |

**Résultats validés sur le Mac M1, frame 1 :**

| Rayon `R` | Sommets | Arêtes | Composantes | Plus grande composante | Degré moyen |
|---:|---:|---:|---:|---:|---:|
| 60 | 253 | 454 | 35 | 162 | 3,59 |
| 100 | 253 | 1 281 | 4 | 248 | 10,13 |
| 120 | 253 | 1 824 | 3 | 251 | 14,42 |

## 3. Modèle B : graphe orienté de visibilité — angle mort fixe 25°

Une relation de visibilité `i → j` est potentiellement **asymétrique** : le poisson `i` peut voir `j` sans que `j` voie `i`. Il faut donc utiliser `nx.DiGraph()` si ce modèle est retenu ; ne pas remplacer silencieusement `nx.Graph()` par un graphe de visibilité et continuer d'interpréter les mêmes métriques.

### Convention géométrique explicite

- Direction du poisson `i` : `theta_i = atan2(vy_i, vx_i)`.
- Direction de `i` vers `j` : `phi_ij = atan2(py_j - py_i, px_j - px_i)`.
- Différence angulaire ramenée à `[-180°,180°]` : `delta_ij = wrap(phi_ij - theta_i)`.
- **Hypothèse fixe retenue :** `rear_blind_angle_deg = 25` représente la **largeur totale du secteur aveugle arrière de 25°**, centré derrière le poisson. Une relation `i → j` existe si `abs(delta_ij) <= 180° - 25°/2 = 167,5°` ET `d(i,j) < R`. La valeur est fixe pour tous les poissons et toutes les frames.
- **Source biologique :** moyenne du secteur aveugle arrière mesuré chez le Golden shiner par Pita et al. (2015). Son application constante est une **hypothèse du modèle**, et non une mesure individuelle dans le dataset.
- Si le vecteur direction est de norme nulle, définir explicitement la convention (par exemple exclure les arcs sortants, ou signaler la frame).


### Référence biologique pour le modèle B : 25°

L'espèce du dataset est le **Golden shiner** (*Notemigonus crysoleucas*). Une étude expérimentale dédiée, Pita et al. (2015), *Vision in two cyprinid fish: implications for collective behavior*, [DOI 10.7717/peerj.1113](https://doi.org/10.7717/peerj.1113), rapporte **25° ± 1,20°** pour la largeur moyenne de la **zone aveugle arrière horizontale** et une couverture horizontale de **335° ± 3,5°** (mesures sur 9 adultes avec yeux au repos ; ± erreur standard rapportée). Davidson et al. (2021), [DOI 10.1098/rsif.2021.0142](https://doi.org/10.1098/rsif.2021.0142), utilisent également un angle aveugle arrière de **25°** pour l'espèce.

**Décision définitive du 3 novembre 2026 :** `rear_blind_angle_deg=25` pour **tous les individus et tous les instants**, sans comparaison d'autres angles dans les résultats scientifiques finaux (secteur aveugle arrière total, visible = 335°). Les valeurs **60°** et **240°** ne sont pas retenues pour l’analyse finale du projet. **Résultats à 25° : calculés et vérifiés par sortie Terminal ; tests automatisés spécifiques à 25° encore à exécuter.** Attention : la direction `(vx,vy)` peut différer de l'orientation corporelle, et les occlusions ne sont pas simulées.

### Résultat du modèle définitif à 25° — frame 1, R = 100

**Exécution locale confirmée le 3 novembre 2026 :** commande `python -m src.visibility_graph` après modification du paramètre par défaut et de l'exécution principale à `rear_blind_angle_deg=25`.

| Angle mort arrière constant | Champ visible | Sommets | Arcs dirigés | Composantes faiblement connexes | Composantes fortement connexes |
|---:|---:|---:|---:|---:|---:|
| **25°** | **335°** | **253** | **2 386** | **4** | **4** |

Le graphe de proximité de référence, sur la même frame et avec `R=100`, comporte **253 sommets et 1 281 arêtes non orientées**. Il existe donc **2 562 arcs directionnels spatialement possibles** dans le graphe de proximité, dont **2 386** sont retenus dans le modèle de visibilité (environ **93,1 %**). Ce pourcentage n'est pas une validation biologique et n'établit pas une communication entre individus. Les tailles des composantes, les centralités et les tests automatisés spécifiques au 25° restent à compléter.

Le résultat à 25° constitue la **référence du projet**. Les autres valeurs ci-dessous correspondent à des essais exploratoires non retenus.

### Essais exploratoires du modèle B — hors analyse finale (3 novembre 2026, frame 1, R=100)

Le programme local `python -m src.visibility_graph` a été exécuté sur le Mac M1 et a affiché les résultats suivants. Le code est **encore local** ; six tests automatisés ont réussi localement le 3 novembre 2026 ; des tests de cas limites supplémentaires restent à faire.

| Angle mort arrière total | Champ visible | Nœuds | Arcs | Composantes faibles | Composantes fortes |
|---:|---:|---:|---:|---:|---:|
| 60° | 300° | 253 | 2 139 | 4 | 5 |
| 240° | 120° | 253 | 887 | 10 | 226 |

Comparaison : le graphe spatial de référence comprend **1 281 arêtes non orientées**, soit **2 562 arcs directionnels potentiels**. Les proportions d'arcs effectivement présents valent donc environ **83,5 %** (angle mort 60°) et **34,6 %** (angle mort 240°). Ces résultats sont des **observations de sortie de programme**, pas encore des preuves apportées par des tests de cohérence `pytest`.

**Statut :** mesures exploratoires non retenues pour l’analyse finale. La version finale emploiera exclusivement un angle aveugle arrière de 25° ; aucune conclusion comparative sur 60° et 240° ne sera formulée dans le rapport. **Interprétation prudente :** l'élargissement du secteur non visible retire des arcs, ce qui peut accroître le nombre de composantes fortes et faibles. Une composante fortement connexe représente l'accessibilité **réciproque par chemin orienté**, pas nécessairement une interaction ou influence biologique. Les poissons peuvent être physiquement voisins même lorsqu'aucun arc de visibilité n'est présent.

**Limites supplémentaires :** les autres poissons ne sont pas modélisés comme des obstacles visuels (pas d'occlusion), la largeur du champ de vision est une hypothèse, et `(vx,vy)` représente la direction du déplacement, qui peut différer de l'orientation corporelle/visuelle.

## 4. Consigne d'exécution terminal

Lorsqu'un script est lancé depuis le Terminal, ajouter dans son point d'entrée des `print(..., flush=True)` aux étapes de chargement, construction, calcul et sauvegarde, ainsi qu'une progression périodique pour les longues boucles. Ne pas afficher une ligne par poisson. Voir la règle complète dans [CONTEXT.md](CONTEXT.md).

## 5. Environnement et exécution locale

Environnement validé : MacBook Pro M1, Python **3.12.6**, NumPy **2.5.4**, SciPy **1.18.1**, NetworkX **3.7**, Matplotlib **3.11.2**, ijson **3.6.0**, pytest **9.2.0**. Ces versions correspondent à l'installation locale rapportée.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --no-cache-dir -r requirements.txt
python -m src.data_loader
python -m src.graph_builder
# Après création des tests :
python -m pytest -v
```

**Les modules figurent sur la branche GitHub `main`.** Le dataset est conservé localement hors Git.

**Tests locaux confirmés :** `python -m pytest -v -s` → **10 passed in 0.56s** (3 novembre 2026), incluant la configuration 25° et le contrôle des 2 386 arcs sur la frame 1. Suite de tests documentée dans le projet.



## 6. Extension scientifique planifiée — simulation Boids / comparatif réel-simulé

**Projet complémentaire cadré, pas encore codé ni validé.** Deux nouveaux axes suivront la partie obligatoire de Graph Analytics : (1) simulation dynamique à partir d'une frame observée avec séparation / alignement / cohésion ; (2) confrontation quantitative des trajectoires et graphes expérimentaux aux trajectoires et graphes simulés sur des fenêtres temporelles comparables.

- **Angle mort inchangé : 25°** pour tous les agents, à toutes les étapes de simulation et de comparaison. Seuls les rayons et coefficients de comportement pourront faire l'objet d'une calibration documentée.
- Les vitesses `(vx,vy)` du dataset ressemblent à des directions unitaires ; l'échelle et `dt` du simulateur devront être calibrés à partir des trajectoires appariées et de la fréquence de **30 fps**.
- Comparaison prévue : mêmes états initiaux, simulation libre sur fenêtres courtes ; **graphe spatial et directionnel à 25°**, degré moyen, composantes, clustering, communautés, polarisation, distances aux plus proches voisins et écarts de trajectoire si suivis fiables.
- Contrôle de robustesse : évaluer sur fenêtres distinctes de celles servant au réglage, comparer au mouvement par persistance, retirer une règle à la fois (**ablations**). L'objectif est de mesurer la **capacité de Boids à reproduire des régularités**, pas de prouver que les poissons exécutent littéralement les trois règles.
- **Priorité : P1 après les livrables P0.** Référence scientifique : Reynolds (1987), [Flocks, Herds and Schools](https://doi.org/10.1145/37402.37406) ; Katz et al. (2011), [Inferring the structure and dynamics of interactions in schooling fish](https://doi.org/10.1073/pnas.1107583108).


## 7. Mesures structurelles — premiers résultats exécutés localement (3 novembre 2026)

**Module local :** `src/graph_metrics.py`, exécuté par `python -m src.graph_metrics` sur la frame observée 1, `R=100` (unités natives), angle mort arrière **constant de 25°** pour la visibilité. **Exécution réussie en 1,12 s**, avec messages de progression aux six étapes. Les deux jeux de métriques ont été enregistrés localement dans `results/metrics_frame1_R100.json`. À ce stade, **le module et ses nouveaux tests ne sont pas encore publiés sur GitHub**.

| Métrique | Graphe spatial non orienté | Graphe orienté de visibilité (25°) |
|---|---:|---:|
| Nœuds | 253 | 253 |
| Arêtes / arcs | 1 281 | 2 386 |
| Composantes connexes / fortement connexes | 4 | 4 |
| Taille de la plus grande composante pertinente | 248 | 248 |
| Part des nœuds dans cette composante | 98,02 % | 98,02 % |
| Diamètre de cette composante (sauts non pondérés) | 23 | 24 |
| Rayon de cette composante (sauts non pondérés) | 12 | 12 |
| Densité NetworkX | 0,04018 | 0,03742 |
| Clustering moyen NetworkX | 0,57800 | 0,54551 |
| Degré moyen / moyen entrant = sortant | 10,1265 | 9,4308 |
| Plus forte centralité d'intermédiarité (ID de suivi) | 99458 (0,16501) | 99981 (0,14945) |

**Conventions :** `nx.connected_components` pour le graphe spatial ; `nx.weakly_connected_components` et `nx.strongly_connected_components` pour le graphe orienté. Le diamètre et le rayon sont calculés **uniquement sur la plus grande composante connexe (spatial) ou fortement connexe (visibilité)**, en nombre de sauts, sans `weight`. Le clustering est calculé par NetworkX selon des définitions différentes en orienté/non orienté ; comparaison prudente. Centralités calculées sur **le graphe entier** avec chemin non pondéré, pas seulement la plus grande composante.

**Interprétation descriptive :** à `R=100`, 2 386 des 2 562 arcs possibles sur les paires proches sont conservés (~93,13 %). Cela ne confirme ni une communication réelle, ni un effet causal, ni un comportement de leadership : la direction `(vx,vy)` n'est qu'une approximation de l'orientation visuelle et les occlusions ne sont pas modélisées.

**À faire :** committer le module et ses 5 tests réussis localement, diagnostiquer le ralentissement de pytest, calculer les métriques sur plusieurs frames, visualiser et étudier les communautés Louvain. Les résultats de cette seule frame ne constituent pas une conclusion temporelle.


### Validation locale des métriques — 15 tests réussis (3 novembre 2026)

Commande exécutée sur le Mac M1 : `python -m pytest -v -s`. Résultat **15 passed in 319.06s (5 min 19 s)** : 10 tests des modèles de voisinage/visibilité à angle mort 25°, 5 tests du module `src/graph_metrics.py` (graphe spatial avec isolé, cycle et chaîne orientés, graphe vide, métriques de la frame réelle). Les valeurs de la frame 1 (`R=100`) ont été confirmées : 253 sommets, 1 281 arêtes spatiales, 2 386 arcs de visibilité, diamètres 23/24, rayons 12/12 et clustering 0,578/0,54551.

**Performance :** exécution complète **anormalement longue**. Un diagnostic isolé avait montré que `import numpy` demandait 15,40 s mais réussissait ; cette observation ne suffit pas à expliquer les 319,06 s. La cause reste **inconnue** ; cibler le ralentissement avec `python -m pytest --durations=10 -v` et, si la collecte reste longue, les temps d'importation de Python. Aucun problème fonctionnel n'a été révélé par ce run.

**Publication :** `src/graph_metrics.py` et `tests/test_graph_metrics.py` ont été créés et testés **localement**, mais leur commit GitHub n'est pas encore confirmé.


## 8. Détection des communautés Louvain — premiers résultats (3 novembre 2026)

**Exécution locale confirmée :** `python -m src.community_detection` sur la frame réelle 1 avec `R=100`, et angle mort arrière **constant de 25°** pour le modèle orienté. Module local **non encore committé**, tests unitaires spécifiques encore à réaliser.

| Indicateur | Graphe spatial | Graphe de visibilité 25° |
|---|---:|---:|
| Sommets | 253 | 253 |
| Liens | 1 281 arêtes | 2 386 arcs |
| Nombre de communautés Louvain | **11** | **10** |
| Modularité (NetworkX, poids ignorés) | **0,70344** | **0,70500** |
| Tailles des communautés, triées décroissantes | 64, 47, 38, 30, 27, 26, 11, 5, 3, 1, 1 | 65, 43, 38, 37, 30, 30, 5, 3, 1, 1 |

Paramètres : `nx.community.louvain_communities(G, seed=42, resolution=1.0, weight=None)`. L'algorithme de NetworkX prend en charge les graphes dirigés ; la fonction de modularité utilise des conventions distinctes pour les graphes dirigés/non dirigés. Les scores ne suffisent pas à établir un classement biologique de cohésion des deux modèles.

Les listes de tailles couvrent chacune **253 poissons observés**. Sortie locale : `results/communities_frame1_R100.json` ; le fichier contient la communauté de chaque ID de suivi pour une future figure utilisant leurs positions spatiales. **Temps affiché : 0,13 s** (ne pas généraliser à toute l'analyse des 5 000 frames). Les communautés ne sont pas une preuve de sous-bancs biologiques ou de leadership.

**À faire :** tests unitaires et régression frame 1, commit du module/des tests/du JSON, visualisation cartographique des groupes sur les positions réelles, stabilité entre frames.

