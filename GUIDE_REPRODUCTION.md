# Guide de reproduction — Projet Graph Analytics

Ce guide permet de **cloner le dépôt**, **installer l'environnement**, **exécuter les 77 tests de référence**, **recalculer les principales analyses** et **ouvrir l'interface graphique**.

> Important : les résultats déjà publiés dans `results/` sont consultables immédiatement après le clone, mais **les scripts exploitant les observations nécessitent le fichier brut** `schooling_frames.json`, volontairement exclu de Git. Les 77 tests réussis correspondent à l'exécution locale du 9 novembre 2026 ; ils doivent être revérifiés sur la machine cible. Certains scripts de calibration peuvent prendre du temps.

## 1. Prérequis

- Git.
- Python **3.12** recommandé (environnement de référence : Python 3.12.6) et `pip`.
- Un ordinateur disposant d'une interface graphique pour Matplotlib ; la commande de lancement de l'interface n'est pas destinée à un serveur sans écran.
- Connexion Internet pour le clone, le dataset et l'installation des dépendances.
- Espace disque suffisant pour le dataset (environ 83 Mo dans l'environnement de travail d'origine), l'environnement Python et les résultats.

Le projet a été développé sur macOS ; les scripts Python sont majoritairement portables, mais l'interface graphique doit être vérifiée sur chaque système.

## 2. Cloner le dépôt

```bash
git clone https://github.com/Charles-Scannavino/Projet_Graph_Analytics.git
cd Projet_Graph_Analytics
git status -sb
```

Pour reproduire un état strictement identique, relever le commit utilisé :

```bash
git rev-parse HEAD
```

## 3. Créer l'environnement Python

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloque l'activation, utiliser `cmd.exe` avec `.venv\Scripts\activate.bat` ou appeler directement `.venv\Scripts\python.exe`. Ne pas modifier la politique de sécurité globale uniquement pour ce projet.

Dépendances listées dans `requirements.txt` : `numpy`, `scipy`, `networkx`, `matplotlib`, `ijson`, `pytest`. Les versions ne sont pas épinglées : pour une reproductibilité exacte, enregistrer les versions effectivement installées :

```bash
python --version
python -m pip freeze > environment_local.txt
```

Le fichier `environment_local.txt` est une trace locale, pas un lockfile officiel du dépôt.

## 4. Récupérer et placer les données

Source : **Fish Schooling Data Subset**, Oregon State University, [DOI 10.7267/zk51vq07c](https://doi.org/10.7267/zk51vq07c). Consulter la notice du dataset et télécharger la distribution appropriée conformément à ses conditions d'utilisation. Le dépôt **ne contient pas** le JSON brut et ne fournit pas de téléchargement automatisé garanti.

Après téléchargement et extraction, vérifier que le fichier s'appelle exactement `schooling_frames.json` et que les clés des frames comprennent `px`, `py`, `vx`, `vy`, `onfish`.

Créer le dossier et copier le fichier :

```bash
mkdir -p data
cp "/CHEMIN/VERS/schooling_frames.json" data/schooling_frames.json
```

Remplacer `/CHEMIN/VERS/` par le chemin réel du fichier (macOS / Linux). Sous Windows, créer `data` puis copier le fichier via l'Explorateur ou PowerShell.

Vérifier la lecture et le format :

```bash
python -m src.data_loader
```

Ce contrôle charge les frames 1, 1000, 2500 et 5000 et affiche les nombres de poissons. Si le fichier manque, vérifier le chemin `data/schooling_frames.json` et son nom exact. **Ne pas ajouter le JSON brut à Git.**

## 5. Exécuter les tests automatisés

Depuis la racine du dépôt, environnement virtuel activé :

```bash
python -m pytest -q
```

**Référence observée le 9 novembre 2026 : `77 passed`.** Les tests peuvent être lancés avant le téléchargement du dataset si leurs données synthétiques suffisent, mais les commandes scientifiques de la section suivante requièrent le JSON réel. Un résultat différent doit être diagnostiqué plutôt que considéré automatiquement comme valide.

## 6. Recalculer les analyses de graphes

Exécuter les modules **depuis la racine du dépôt**, avec `python -m src.nom_du_module` :

```bash
python -m src.graph_metrics
python -m src.community_detection
python -m src.temporal_analysis --step 250 --radius 100
python -m src.plot_temporal
```

Les principaux fichiers produits se trouvent dans :

- `results/metrics_frame1_R100.json`
- `results/communities_frame1_R100.json`
- `results/temporal/metrics_step250_R100.csv`
- `results/figures/`

Pour reproduire l'étude de sensibilité aux cinq rayons, produire les cinq CSV avant de générer les graphiques :

```bash
for R in 60 80 100 120 140; do
  python -m src.temporal_analysis --step 250 --radius "$R"
done
python -m src.sensitivity_analysis
```

La boucle ci-dessus est prévue pour macOS / Linux ; sous Windows PowerShell, exécuter les cinq commandes individuellement ou utiliser `foreach ($R in 60,80,100,120,140) { python -m src.temporal_analysis --step 250 --radius $R }`.

## 7. Reproduire les simulations et validations Boids

### Pilote et comparaison de graphes

```bash
python -m src.boids_pilot
python -m src.compare_boids_graphs
python -m src.plot_boids_comparison
```

Sorties principales : `results/simulation/boids_pilot_h30.json`, `results/simulation/graph_comparison_h30_R100.json` et figures dans `results/figures/`.

### Calibration et validation hors entraînement

Respecter l'ordre suivant : **calibrer sur 1–32**, puis évaluer sur **2000–2031** et **4000–4031**. Ne pas sélectionner de paramètres sur les fenêtres de validation en prétendant qu'elles sont indépendantes.

```bash
python -m src.calibrate_boids
python -m src.validate_calibrated_boids
python -m src.optimize_boids_weights
python -m src.validate_optimized_weights
```

Sorties :

- `results/simulation/boids_calibration_train_R100.json` et `.csv`
- `results/simulation/boids_holdout_validation.json` et `.csv`
- `results/simulation/boids_weights_optimization_train.json` et `.csv`
- `results/simulation/boids_validation_optimized.csv`

Les expériences peuvent être coûteuses. Le script `src/validate_calibrated_boids.py` régénère aussi les comparaisons de graphes calibrés sur les fenêtres de validation. Le script `src/validate_boids_windows.py` permet d'obtenir les comparaisons non calibrées correspondantes :

```bash
python -m src.validate_boids_windows
```

Les anciens fichiers JSON conservés dans Git peuvent avoir été produits avant l'ajout du champ de traçabilité `method.boids_parameters`. **Ne pas leur attribuer rétroactivement des paramètres sans relancer l'expérience.**

## 8. Analyse exploratoire des leaders

```bash
python -m src.detect_fish_leaders
python -m src.compare_fish_leadership
```

Les résultats sont enregistrés dans `results/leadership/` et `results/leadership/comparison/`. L'interface utilise notamment `results/leadership/leaders_phases.csv` et `leaders_summary.csv`, déjà présents dans le dépôt.

Ces scores indiquent une **précédence temporelle corrélée**, pas une causalité ou une hiérarchie biologique démontrée.

## 9. Installer, lancer et utiliser l'interface graphique Matplotlib

### 9.1. Installation initiale (macOS / Linux)

Depuis la racine du dépôt, créer un environnement virtuel **si `.venv` n'existe pas encore**, puis installer les dépendances :

```bash
cd ~/Developer/Projet_Graph_Analytics  # adapter ce chemin à son installation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Le dossier `.venv` n'est pas versionné sur GitHub : il est normal qu'il manque après un clone. Si un environnement Python fonctionnel existe déjà, le réutiliser au lieu d'en créer un autre. Sous Windows, suivre la procédure PowerShell de la section 3.

Vérifier la présence du JSON brut (non inclus dans Git) :

```bash
ls -lh data/schooling_frames.json
```

Les modules de l'interface utilisent `data/schooling_frames.json`. Ne pas déplacer ni ajouter le fichier brut à Git. Pour un premier démarrage, les fichiers CSV de leaders présents dans `results/leadership/` sont également nécessaires pour afficher les leaders en rouge.

### 9.2. Démarrage et arrêt

À chaque nouvelle session Terminal macOS / Linux :

```bash
cd ~/Developer/Projet_Graph_Analytics  # adapter si nécessaire
source .venv/bin/activate
python -m src.boids_interface
```

Si `(.venv)` apparaît déjà dans l'invite et que le Terminal est dans le dépôt, seule la dernière commande est nécessaire. Une fenêtre Matplotlib interactive s'ouvre ; la fermeture de cette fenêtre termine normalement l'interface. `Ctrl+C` permet d'interrompre le processus depuis le Terminal si besoin.

L'interface affiche trois vues comparatives : **observations réelles, inertie et simulation Boids**. Elle permet de changer les coefficients, la fenêtre temporelle, d'afficher ou masquer les arêtes spatiales, de mettre en pause et de mettre en évidence les leaders potentiels.

### 9.3. Champs et boutons

| Contrôle | Utilisation |
| --- | --- |
| `Séparation` | Poids de la règle d'évitement Boids ; valeur initiale affichée : `0.005`. |
| `Alignement` | Poids de l'alignement ; valeur initiale : `0.05`. |
| `Cohésion` | Poids du rapprochement vers le groupe ; valeur initiale : `0.005`. |
| `Début` | Numéro de la première frame de la fenêtre (initialement `1`). |
| `Horizon (frames)` | Nombre de pas simulés : **30, 60, 150 ou 300** uniquement. |
| `Redémarrer` | Recharge la fenêtre et recalcule les trajectoires avec les valeurs saisies. |
| `Pause` | Suspend/reprend l'animation. |
| `Arêtes spatiales : ON/OFF` | Affiche/masque les liens de proximité. |
| `Paramètres calibrés` | Rétablit les poids de simulation calibrés proposés par l'interface. |
| `Leaders : OFF/Phase/Persistants` | Fait défiler les trois modes de visualisation des leaders. |

Le graphe spatial affiché utilise un rayon de **100 unités natives** ; l'angle mort arrière modélisé est de **25°**. La simulation ne modélise pas de frontières physiques. Les poids Boids modifient la simulation, **pas** les identifiants de leaders préalablement calculés.

### 9.4. Démonstration : afficher les leaders en rouge

Les CSV de leadership livrés avec le dépôt concernent **exclusivement les frames 2000 à 2149**. La fonction `selected_leaders()` n'active leur coloration que si **`Début = 2000` et `Horizon = 150`**.

1. Saisir **`2000`** dans `Début` et **`150`** dans `Horizon (frames)`.
2. Conserver par exemple les poids initiaux `Séparation = 0.005`, `Alignement = 0.05`, `Cohésion = 0.005` ; ils ne conditionnent pas l'identification des leaders.
3. Cliquer sur **`Redémarrer`** et attendre le chargement/calcul de la fenêtre.
4. Cliquer **une fois** sur `Leaders : OFF` pour obtenir **`Leaders : Phase`** : les candidats leaders sont affichés en rouge selon la phase courante.
5. Cliquer **une deuxième fois** pour obtenir **`Leaders : Persistants`** : les candidats présents dans au moins **3 des 5 phases** sont mis en évidence. Un troisième clic revient à **`OFF`**.

| Phase | Frames | Comportement en mode `Phase` |
| --- | --- | --- |
| 1 | 2000–2029 | Leaders potentiels de la phase 1 |
| 2 | 2030–2059 | Leaders potentiels de la phase 2 |
| 3 | 2060–2089 | Leaders potentiels de la phase 3 |
| 4 | 2090–2119 | Leaders potentiels de la phase 4 |
| 5 | 2120–2149 | Leaders potentiels de la phase 5 |

Les poissons sélectionnés sont représentés par des **triangles rouges plus grands**, avec leur identifiant. Le poisson **105760** est un exemple de candidat persistant (**3 phases sur 5**, soit **60 %** de persistance) dans les résultats publiés. En mode `Phase`, les poissons rouges peuvent changer au fil de l'animation ; en mode `Persistants`, la liste de candidats est fixe sur la fenêtre.

**Cas sans coloration :** avec `Début = 1`, ou avec `Début = 2000` et `Horizon = 30`, aucun leader n'est sélectionné par le mécanisme actuel. L'absence de rouge hors de la fenêtre 2000–2149 ne signifie donc pas qu'aucun leader biologique n'existe.

La détection est **exploratoire** : elle repose sur des corrélations temporelles des changements de direction et ne prouve pas une influence causale.

### 9.5. Dépannage

- **`source: no such file or directory: .venv/bin/activate`** : vérifier `pwd` et `ls -la` à la racine du dépôt ; si `.venv` manque, exécuter `python3 -m venv .venv`, puis l'activer et installer `requirements.txt`.
- **`ModuleNotFoundError`** : vérifier que `(.venv)` est actif et réexécuter `python -m pip install -r requirements.txt`.
- **`FileNotFoundError` pour le JSON** : vérifier `data/schooling_frames.json` et la section 4.
- **L'interface paraît bloquée au lancement** : la lecture JSON et la préparation des trajectoires peuvent prendre du temps, particulièrement avec 150 ou 300 frames ; attendre avant d'interrompre.
- **Aucun leader rouge** : vérifier les deux champs exacts `2000` et `150`, le mode `Phase` ou `Persistants`, et la présence de `results/leadership/leaders_phases.csv` et `leaders_summary.csv`.
- **Pas de fenêtre** : utiliser un Terminal local avec affichage graphique ; **ne pas définir `MPLBACKEND=Agg`**, qui désactive l'affichage interactif.


## 10. Vérifier les sorties et ne pas écraser ses résultats par erreur

Les dossiers `results/` et `Rapport/sources/` contiennent déjà des résultats et figures versionnés. **Relancer les scripts peut écraser des fichiers portant les mêmes noms.** Pour une comparaison stricte avant/après, travailler dans un clone séparé ou créer une branche Git et vérifier les modifications :

```bash
git status -sb
git diff --stat
```

Pour conserver un journal d'exécution sans modifier les sources :

```bash
python -m pytest -q > tests_execution.txt 2>&1
```

Ne pas committer automatiquement les résultats régénérés, les données brutes ou des informations personnelles.

## 11. Dépannage rapide

| Problème | Vérification |
| --- | --- |
| `ModuleNotFoundError: src` | Se placer à la racine du dépôt ; utiliser `python -m src.module`. |
| `FileNotFoundError: ...schooling_frames.json` | Placer le dataset sous `data/schooling_frames.json`. |
| `No module named pytest` | Activer `.venv` puis réinstaller `requirements.txt`. |
| Interface absente / backend non interactif | Utiliser un Terminal local avec affichage ; vérifier le backend Matplotlib. |
| Résultats différents | Vérifier le commit, les versions des bibliothèques, le dataset et les paramètres. |
| Exécution lente | Certaines mesures de graphes et grilles de calibration sont coûteuses ; attendre les messages de progression. |

## 12. Limites scientifiques à conserver dans toute reproduction

1. Les distances sont en unités natives et `vx/vy` ne constituent pas une vitesse physique calibrée.
2. Les arêtes de proximité et arcs de visibilité ne prouvent pas une interaction réelle.
3. Le graphe de visibilité utilise une approximation de l'orientation et ignore les occlusions.
4. Les cohortes retenues sur la durée d'une fenêtre introduisent un biais de sélection.

Pour le contenu scientifique détaillé, consulter le [rapport PDF](Rapport/Graphe/SCANNAVINO_CHEVOLOT-Rapport_Projet_Graphe.pdf), le [README](README.md), [CONTEXT.md](CONTEXT.md) et [AVANCEMENT.md](AVANCEMENT.md).
