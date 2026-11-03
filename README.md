# Projet Graph Analytics 2026 — Fish Schooling Networks

**Sujet :** analyse de l'organisation spatiale et temporelle d'un banc de poissons à partir de graphes de voisinage.  
**Dépôt :** [Projet_Graph_Analytics](https://github.com/Charles-Scannavino/Projet_Graph_Analytics)  
**État au 3 novembre 2026 :** les modules `src/data_loader.py` et `src/graph_builder.py` fonctionnent **sur la machine locale de développement**, mais ne sont pas encore intégrés à cette branche GitHub ; les tests `pytest` restent à exécuter.  
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

## 3. Modèle B : graphe orienté de visibilité — À DÉVELOPPER ET VALIDER

Une relation de visibilité `i → j` est potentiellement **asymétrique** : le poisson `i` peut voir `j` sans que `j` voie `i`. Il faut donc utiliser `nx.DiGraph()` si ce modèle est retenu ; ne pas remplacer silencieusement `nx.Graph()` par un graphe de visibilité et continuer d'interpréter les mêmes métriques.

### Convention géométrique explicite

- Direction du poisson `i` : `theta_i = atan2(vy_i, vx_i)`.
- Direction de `i` vers `j` : `phi_ij = atan2(py_j - py_i, px_j - px_i)`.
- Différence angulaire ramenée à `[-180°,180°]` : `delta_ij = wrap(phi_ij - theta_i)`.
- **Proposition scientifique distincte de l'ancien code :** `rear_blind_angle_deg = 60` représente la **largeur totale d'un secteur aveugle de 60° centré derrière le poisson**. Sous cette convention, `j` est visible depuis `i` si `abs(delta_ij) <= 180° - rear_blind_angle_deg/2` (donc `<= 150°`), et si `d(i,j) < R`.
- **Ce 60° est un paramètre de modélisation à justifier, pas une mesure biologiquement validée du dataset.**
- Si le vecteur direction est de norme nulle, définir explicitement la convention (par exemple exclure les arcs sortants, ou signaler la frame).



| Paramètre | Ancien simulateur | Modèle B proposé |
|---|---|---|
| Nom | `angle_mort_degre` | `rear_blind_angle_deg` |
| Valeur de départ | 60° | 60° (hypothèse à tester) |
| Signification réelle | Demi-ouverture visuelle **avant** | Largeur de l'angle mort **arrière** |
| Champ visible obtenu | 120° | 300° |
| Zone aveugle obtenue | 240° | 60° |
| Graphe | Voisins filtrés pour les forces Boids | Arcs `i → j` de visibilité, **nouvelle analyse** |

**Analyses à prévoir pour le modèle B :** degrés entrant/sortant, composantes faiblement/fortement connexes ; définir explicitement si une projection non orientée est nécessaire pour comparer Louvain et les autres mesures. Tester la sensibilité à l'angle et au rayon. **Aucune métrique de visibilité n'a encore été exécutée.**

## 4. Paramètres de l'ancienne simulation — hors calcul des graphes observés

L'ancien simulateur avait `r_separation=60`, `r_alignement=80`, `r_cohesion=120`, `k_separation=20`, `k_alignement=0.4`, `k_cohesion=0.015`, `angle_mort_degre=60`, `v_max=60` et `dt=1`. **Ce sont des paramètres de simulation Boids, pas des données empiriques ni des paramètres activés automatiquement dans le graphe de proximité validé.** Le seuil `R=100` utilisé dans l'analyse actuelle est un test de sensibilité supplémentaire.

## 5. Environnement et exécution locale

Environnement validé : MacBook Pro M1, Python **3.12.6**, NumPy **2.5.4**, SciPy **1.18.1**, NetworkX **3.7**, Matplotlib **3.11.2**, ijson **3.6.0**, pytest **9.2.0**. Ces versions correspondent à l'installation locale rapportée ; `requirements.txt` reste à committer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --no-cache-dir -r requirements.txt
python -m src.data_loader
python -m src.graph_builder
# Après création des tests :
python -m pytest -v
```

**Ces commandes de modules nécessitent que leurs fichiers locaux soient ajoutés au dépôt ; à ce jour ils ne figurent pas encore dans la branche GitHub.** Le dataset est conservé localement hors Git.

## 6. Intégrité et reproductibilité

- Indiquer dans le rapport les données d'origine, le code ancien éventuellement réutilisé, les nouveaux développements et **l'usage effectif des outils IA**.
- Ne pas publier le script ancien non assaini : il contient une **clé API Gemini en clair**. Cette clé doit être révoquée/renouvelée par son titulaire.
- Ne jamais changer les dates de fichiers copiés pour laisser croire que les données ou scripts originaux ont été produits en 2026.
- Les métriques du modèle A ne peuvent **pas** être présentées comme des métriques du modèle B : le champ de visibilité transforme les arêtes, l'orientation et parfois les algorithmes applicables.
