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

## 9. Ouvrir l'interface graphique

Sur un ordinateur disposant d'un affichage local :

```bash
python -m src.boids_interface
```

L'interface Matplotlib permet de comparer les poissons réels, l'inertie et Boids, d'explorer les fenêtres disponibles (**1–32**, **2000–2031**, **4000–4031**), d'afficher les liens spatiaux et de visualiser les leaders potentiels.

L'application charge les observations depuis `data/schooling_frames.json`. **Ne pas définir `MPLBACKEND=Agg`** pour cette commande : un backend interactif est nécessaire. En cas de problème d'affichage, lancer depuis le Terminal de l'ordinateur plutôt que depuis un notebook ou une session distante sans serveur graphique.

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
5. Les résultats de validation Boids ne concernent que deux fenêtres hors entraînement ; aucun test de significativité ou de généralisation large n'est établi.
6. Les leaders identifiés sont **potentiels** et ne démontrent pas une influence causale.

Pour le contenu scientifique détaillé, consulter le [rapport PDF](Rapport/Graphe/SCANNAVINO_CHEVOLOT-Rapport_Projet_Graphe.pdf), le [README](README.md), [CONTEXT.md](CONTEXT.md) et [AVANCEMENT.md](AVANCEMENT.md).
