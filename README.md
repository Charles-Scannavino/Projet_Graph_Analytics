# Graph Analytics — Collective Fish Schooling Behaviour

**Albert School — Graph Analytics (2026)** · Jacques Chevolot et Charles Scannavino

Étude de l'organisation d'un banc de poissons à partir de **graphes spatiaux de proximité** et de **graphes orientés de visibilité**, prolongée par des analyses temporelles, une étude de sensibilité, une simulation **Boids**, une calibration et une recherche exploratoire de leaders potentiels.

> **Pour reproduire le projet sur un autre ordinateur : [GUIDE_REPRODUCTION.md](GUIDE_REPRODUCTION.md)**. Le fichier de données brutes n'est pas distribué dans GitHub.

## Données et hypothèses

- **Source** : *Fish Schooling Data Subset*, Oregon State University — [DOI 10.7267/zk51vq07c](https://doi.org/10.7267/zk51vq07c), licence CC BY 4.0 signalée dans les documents d'origine.
- **Structure** : 5 000 frames à 30 fps, champs `px`, `py`, `vx`, `vy`, `onfish`; banc d'environ 300 poissons, avec un nombre d'individus suivis variable.
- **Identifiants** : `onfish` représente un identifiant de suivi, pas une garantie d'identité biologique permanente.
- **Unités** : les positions et les rayons sont exprimés en unités natives du jeu de données ; aucune conversion physique n'est affirmée.
- **Graphe spatial** : `nx.Graph`, une arête non orientée pour `distance(i,j) < R`; rayon de référence `R=100`.
- **Graphe de visibilité** : `nx.DiGraph`, même condition spatiale et secteur aveugle arrière de **25° au total** (champ géométrique nominal de 335°). La direction de déplacement sert de proxy de l'orientation, sans modélisation des occlusions.
- **Sensibilité** : rayons `60, 80, 100, 120, 140`.

## Méthodes implémentées

| Axe | Implémentation | Résultats |
| --- | --- | --- |
| Graphes et mesures | `src/graph_builder.py`, `src/visibility_graph.py`, `src/graph_metrics.py` | `results/metrics_frame1_R100.json` |
| Communautés Louvain | `src/community_detection.py` | `results/communities_frame1_R100.json` |
| Analyse temporelle | `src/temporal_analysis.py`, `src/plot_temporal.py` | `results/temporal/`, `results/figures/` |
| Sensibilité au rayon | `src/sensitivity_analysis.py` | `results/sensitivity/`, `results/figures/` |
| Simulation Boids / inertie | `src/boids_pilot.py`, `src/compare_boids_graphs.py` | `results/simulation/` |
| Calibration et validation | `src/calibrate_boids.py`, `src/optimize_boids_weights.py`, `src/validate_calibrated_boids.py`, `src/validate_optimized_weights.py` | `results/simulation/` |
| Leadership exploratoire | `src/detect_fish_leaders.py`, `src/compare_fish_leadership.py` | `results/leadership/` |
| Interface interactive | `src/boids_interface.py` | Fenêtre Matplotlib locale |

### Quelques résultats reproductibles

À la frame 1 et `R=100`, le graphe spatial compte **253 sommets et 1 281 arêtes** ; le graphe de visibilité à angle mort arrière de 25° compte **253 sommets et 2 386 arcs**.

La calibration Boids utilise les frames **1–32**. Les fenêtres **2000–2031** et **4000–4031** servent à une validation hors entraînement, avec des cohortes de suivi continu. À l'horizon 30, les résultats incluent :

| Fenêtre | Modèle | Jaccard spatial | Erreur de position (unités natives) |
| --- | --- | ---: | ---: |
| 2000 | Inertie | 0,5046 | 40,04 |
| 2000 | Boids optimisé pour l'erreur de position | 0,5321 | 38,09 |
| 4000 | Inertie | 0,5198 | 37,36 |
| 4000 | Boids optimisé pour le Jaccard | 0,5458 | 35,54 |

Ces gains sont **modestes et descriptifs** : deux fenêtres de validation ne suffisent pas à prouver une généralisation statistique. La sélection de poissons présents pendant toute une fenêtre introduit un biais de cohorte survivante. Les signaux de leadership sont des précédences temporelles, **pas des preuves d'influence causale**.

## Démarrage rapide

Après récupération légitime du dataset, placer `schooling_frames.json` dans `data/schooling_frames.json` puis, à la racine du dépôt :

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.graph_metrics
python -m src.boids_interface
```

L'interface exige une session graphique et un backend Matplotlib interactif (éviter les environnements sans affichage). Pour Windows, les commandes d'activation et les instructions détaillées figurent dans le [guide de reproduction](GUIDE_REPRODUCTION.md).

## Rapport et livrables

- [Rapport PDF courant](Rapport/Graphe/SCANNAVINO_CHEVOLOT-Rapport_Projet_Graphe.pdf) — **29 pages**, incluant les annexes ; vérifier la règle de pagination du rendu.
- [Figures du rapport](Rapport/sources/) et [figures générées](results/figures/).
- [Contexte](CONTEXT.md) et [journal d'avancement](AVANCEMENT.md) : documents historiques ; certaines mentions d'état datées peuvent être dépassées.
- [Guide complet pour cloner, tester, reproduire et lancer l'interface](GUIDE_REPRODUCTION.md).

**Contrôle de référence au 9 novembre 2026 :** 77 tests `pytest` réussis sur la branche principale (exécution locale rapportée). Les résultats JSON historiques antérieurs à l'ajout de `boids_parameters` ne sont pas réécrits automatiquement ; les nouvelles comparaisons exportent les paramètres réellement utilisés.

## Références essentielles

- Katz et al. (2011), *Inferring the structure and dynamics of interactions in schooling fish*, [PNAS](https://doi.org/10.1073/pnas.1107583108).
- Pita et al. (2015), *Vision in two cyprinid fish*, [PeerJ](https://doi.org/10.7717/peerj.1113).
- Reynolds (1987), *Flocks, Herds, and Schools*, [SIGGRAPH](https://doi.org/10.1145/37402.37406).
- Blondel et al. (2008), *Fast unfolding of communities in large networks*.

L'utilisation éventuelle d'outils d'IA dans la rédaction ou le développement doit être déclarée conformément aux consignes pédagogiques ; cette documentation ne constitue pas à elle seule cette déclaration.
