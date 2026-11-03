# Projet Graph Analytics 2026 — Fish Schooling Networks

**Sujet :** analyse de l'organisation spatiale et temporelle d'un banc de poissons à partir de graphes de voisinage.  
**Dépôt :** [Projet_Graph_Analytics](https://github.com/Charles-Scannavino/Projet_Graph_Analytics)  
**État au 3 novembre 2026 :** les modules `src/data_loader.py` et `src/graph_builder.py` fonctionnent **sur la machine locale de développement**, mais ne sont pas encore intégrés à cette branche GitHub ; les **six tests `pytest` de base ont réussi localement**, mais ne sont pas encore intégrés à cette branche GitHub.  
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



| Paramètre | Ancien simulateur | Modèle B proposé |
|---|---|---|
| Nom | `angle_mort_degre` | `rear_blind_angle_deg` |
| Valeur | 60° (dans le code historique) | **25° fixé pour l'étude** |
| Signification réelle | Demi-ouverture visuelle **avant** | Largeur de l'angle mort **arrière** |
| Champ visible obtenu | 120° | **335°** |
| Zone aveugle obtenue | 240° | **25°** |
| Graphe | Voisins filtrés pour les forces Boids | Arcs `i → j` de visibilité, **nouvelle analyse** |

**Analyses à prévoir pour le modèle B :** degrés entrant/sortant, composantes faiblement/fortement connexes ; définir explicitement si une projection non orientée est nécessaire pour comparer Louvain et les autres mesures. L'**angle mort reste constant à 25°** ; seule une sensibilité au **rayon `R`** peut être explorée. Des essais à 60° et 240° ont été exécutés auparavant, mais **aucun résultat à 25° n'a encore été confirmé**.

### Référence biologique pour le modèle B : 25°

L'espèce du dataset est le **Golden shiner** (*Notemigonus crysoleucas*). Une étude expérimentale dédiée, Pita et al. (2015), *Vision in two cyprinid fish: implications for collective behavior*, [DOI 10.7717/peerj.1113](https://doi.org/10.7717/peerj.1113), rapporte **25° ± 1,20°** pour la largeur moyenne de la **zone aveugle arrière horizontale** et une couverture horizontale de **335° ± 3,5°** (mesures sur 9 adultes avec yeux au repos ; ± erreur standard rapportée). Davidson et al. (2021), [DOI 10.1098/rsif.2021.0142](https://doi.org/10.1098/rsif.2021.0142), utilisent également un angle aveugle arrière de **25°** pour l'espèce.

**Décision définitive du 3 novembre 2026 :** `rear_blind_angle_deg=25` pour **tous les individus et tous les instants**, sans comparaison d'autres angles dans les résultats scientifiques finaux (secteur aveugle arrière total, visible = 335°). Les calculs historiques **60°** et **240°** sont archivés comme essais de développement, **pas** comme analyses de sensibilité du projet. **Résultats à 25° : non encore calculés ni validés.** Attention : la direction `(vx,vy)` peut différer de l'orientation corporelle, et les occlusions ne sont pas simulées.

### Historique technique des premiers essais du modèle B — hors analyse finale (3 novembre 2026, frame 1, R=100)

Le programme local `python -m src.visibility_graph` a été exécuté sur le Mac M1 et a affiché les résultats suivants. Le code est **encore local** ; six tests automatisés ont réussi localement le 3 novembre 2026 ; des tests de cas limites supplémentaires restent à faire.

| Angle mort arrière total | Champ visible | Nœuds | Arcs | Composantes faibles | Composantes fortes |
|---:|---:|---:|---:|---:|---:|
| 60° | 300° | 253 | 2 139 | 4 | 5 |
| 240° | 120° | 253 | 887 | 10 | 226 |

Comparaison : le graphe spatial de référence comprend **1 281 arêtes non orientées**, soit **2 562 arcs directionnels potentiels**. Les proportions d'arcs effectivement présents valent donc environ **83,5 %** (angle mort 60°) et **34,6 %** (angle mort 240°). Ces résultats sont des **observations de sortie de programme**, pas encore des preuves apportées par des tests de cohérence `pytest`.

**Statut :** mesures de développement conservées pour la traçabilité seulement. La version finale emploiera exclusivement un angle aveugle arrière de 25° ; aucune conclusion comparative sur 60° et 240° ne sera formulée dans le rapport. **Interprétation prudente :** l'élargissement du secteur non visible retire des arcs, ce qui peut accroître le nombre de composantes fortes et faibles. Une composante fortement connexe représente l'accessibilité **réciproque par chemin orienté**, pas nécessairement une interaction ou influence biologique. Les poissons peuvent être physiquement voisins même lorsqu'aucun arc de visibilité n'est présent.

**Limites supplémentaires :** les autres poissons ne sont pas modélisés comme des obstacles visuels (pas d'occlusion), la largeur du champ de vision est une hypothèse, et `(vx,vy)` représente la direction du déplacement, qui peut différer de l'orientation corporelle/visuelle.

## 4. Paramètres de l'ancienne simulation — hors calcul des graphes observés

L'ancien simulateur avait `r_separation=60`, `r_alignement=80`, `r_cohesion=120`, `k_separation=20`, `k_alignement=0.4`, `k_cohesion=0.015`, `angle_mort_degre=60`, `v_max=60` et `dt=1`. **Ce sont des paramètres de simulation Boids, pas des données empiriques ni des paramètres activés automatiquement dans le graphe de proximité validé.** Le seuil `R=100` utilisé dans l'analyse actuelle est un test de sensibilité supplémentaire.

## Consigne d'exécution terminal

Lorsqu'un script est lancé depuis le Terminal, ajouter dans son point d'entrée des `print(..., flush=True)` aux étapes de chargement, construction, calcul et sauvegarde, ainsi qu'une progression périodique pour les longues boucles. Ne pas afficher une ligne par poisson. Voir la règle complète dans [CONTEXT.md](CONTEXT.md).

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

**Tests locaux confirmés :** `python -m pytest -v` → **6 passed in 0.28s** (3 novembre 2026), incluant le seuil strict de distance, la visibilité avant/arrière et latérale, les composantes du dataset observé et le fait qu'aucun arc directionnel ne soit ajouté hors du graphe spatial. Tests présents sur le Mac mais **non encore publiés** sur GitHub.

## 6. Intégrité et reproductibilité

- Indiquer dans le rapport les données d'origine, le code ancien éventuellement réutilisé, les nouveaux développements et **l'usage effectif des outils IA**.
- Ne pas publier le script ancien non assaini : il contient une **clé API Gemini en clair**. Cette clé doit être révoquée/renouvelée par son titulaire.
- Ne jamais changer les dates de fichiers copiés pour laisser croire que les données ou scripts originaux ont été produits en 2026.
- Les métriques du modèle A ne peuvent **pas** être présentées comme des métriques du modèle B : le champ de visibilité transforme les arêtes, l'orientation et parfois les algorithmes applicables.
