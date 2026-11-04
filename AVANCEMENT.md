# AVANCEMENT.md — Graph Analytics 2026 | Fish Schooling Networks

> **Dernière mise à jour :** 4 novembre 2026  
> **Version :** 2.3  
> **Statut :** pipeline des graphes spatiaux/visibilité (angle mort fixe 25°), métriques, communautés Louvain, analyse temporelle (21 frames) et **5 figures temporelles PNG/SVG** publiés. **38/38 tests réussis en une seule exécution (63,52 s)** ; dernier commit fonctionnel `202b62a`. Étude de sensibilité à R, interprétation et rapport à poursuivre.
> **Date limite du rapport :** mardi **10 novembre 2026 à 08:00** (Inside).  
> **Soutenance :** mardi **10 novembre 2026 de 14:00 à 17:00**, 8 minutes d'exposé et 2 minutes de questions.

## 0. Règles de suivi

- `[x]` : terminé et confirmé, avec un document ou une preuve disponible.
- `[ ]` : à faire, à tester ou non confirmé.
- `[!]` : point bloquant ou risque critique.
- **P0** : exigence officielle/priorité absolue ; **P1** : approfondissement pertinent ; **P2** : extension facultative.

Ne cocher `[x]` pour une fonctionnalité informatique que si les fichiers, l'exécution et les résultats ont été vérifiés.

## 1. Synthèse et décisions

### 1.1. Cadrage établi

- [x] Énoncé **`Instructions_Projet.pdf`** (2 pages) étudié et exigences extraites.
- [x] Sujet candidat : **réseaux de proximité de poissons** à partir de positions expérimentales.
- [x] Question proposée : relations entre **connectivité, distances, centralités, communautés** et organisation collective.
- [x] Choix méthodologique envisagé : **graphe simple non orienté** à seuil de distance, sur une ou plusieurs frames.
- [x] Priorisation : **Python + NetworkX** pour les analyses obligatoires ; Neo4j seulement si utile et faisable.
- [x] Ajout explicite au plan de calcul du **diamètre et du rayon**, avec traitement des graphes déconnectés.
- [x] Contraintes de groupe, rapport, GitHub, citations, IA, soutenance et remise consignées.
- [x] `CONTEXT.md` et `AVANCEMENT.md` préparés pour décrire exclusivement le projet Graph Analytics 2026.

### 1.2. Éléments encore non vérifiés

- [!] Nom du **second étudiant** non renseigné dans ces documents.
- [x] Dataset 2D `Data/schooling_frames.json` accessible sur Drive et audité (5 000 frames, 86,8 Mo).
- [!] Template du rapport sur **Inside** : non fourni ici.
- [x] Dépôt GitHub dédié : https://github.com/Charles-Scannavino/Projet_Graph_Analytics.
- [ ] Unités, continuité de suivi, sélection de frames et seuil `R` : à définir.
- [x] Premières métriques de graphe calculées sur des snapshots, **uniquement pour l'audit exploratoire**.
- [ ] Pipeline définitif reproductible et tests dans GitHub : modules `data_loader` et `graph_builder` validés localement le 03/11, mais pas encore publiés ; autres analyses à développer.
- [ ] Rapport PDF final, README reproductible et slides : à produire.

## 2. Tableau de conformité à l'énoncé officiel

| Exigence | État actuel | Preuve attendue | Priorité |
|---|---|---|---|
| Groupe de exactement 2 étudiants | [!] | Deux noms et répartition orale | P0 |
| Dataset : origine et intérêt | [x] Audit du 31/10 | DOI et licence identifiés ; JSON lu | P0 |
| Attribution du code effectivement utilisé | [ ] | Provenance du code incorporé, auteurs et URLs le cas échéant | P0 |
| Problématique explicite | [x] Formulation candidate | Question finalisée dans le rapport | P0 |
| Définition des nœuds et des arêtes | [ ] | Modèle et construction reproductibles | P0 |
| Graphe orienté/non orienté et simple/multigraphe | [ ] | Choix justifié | P0 |
| Attributs et poids | [ ] | Champs et unités documentés | P0 |
| Nombre de nœuds `N` et d'arêtes `M` | [x] Contrôle sur snapshots ; script final [ ] | Tableaux reproductibles à publier | P0 |
| Connectivité et composantes | [x] Contrôle sur snapshots ; interprétation finale [ ] | Tailles et comparaison entre frames | P0 |
| **Diamètre** | [x] Calcul sur LCC exploratoire ; script final [ ] | Convention annoncée : sauts sur LCC | P0 |
| **Rayon** | [x] Calcul sur LCC exploratoire ; script final [ ] | Convention annoncée : sauts sur LCC | P0 |
| Centralités et interprétation | [ ] | Scores, définitions et lecture scientifique | P0 |
| Communautés et interprétation | [x] Louvain test sur snapshots ; discussion finale [ ] | Seed, modularité, taille des groupes | P0 |
| Logiciels, paramètres et reproductibilité | [ ] | Versions, scripts, commande, jeu de données | P0 |
| Rapport PDF ≤15 pages avec template Inside | [!] | Document final conforme | P0 |
| Noms du binôme, URL GitHub, déclaration IA | [ ] | Sections du rapport | P0 |
| GitHub : code, données ou lien externe, README | [ ] | Dépôt utilisable par un correcteur | P0 |
| Soutenance 8+2 minutes, deux orateurs | [ ] | Présentation et répétition | P0 |
| Comparaison inter-frames/sensibilité à `R` | [ ] | Figures et mesures d'incertitude adaptées | P1 |
| Neo4j, 3D, simulations, LLM | [ ] | Seulement si P0 achevé | P2 |

## 3. Plan d'exécution

### Phase A — Données et organisation (P0)

- [ ] Confirmer les deux membres et répartir les tâches.
- [ ] Récupérer le **template de rapport** sur Inside.
- [x] Accéder au jeu *Fish Schooling Data Subset* (Google Drive) ; le fichier brut a été audité sans modification.
- [x] Vérifier DOI, auteurs, institution et licence depuis `Data/README.txt` (31/10/2026).
- [x] Auditer les 5 000 frames et les variables `px`, `py`, `vx`, `vy`, `onfish`.
- [x] Vérifier longueurs des tableaux, identifiants dupliqués par frame et effectifs observés.
- [ ] Vérifier précisément les unités, les valeurs non finies et la nature des vitesses : les normes `(vx, vy)` valent ≈1 sur les frames contrôlées.
- [x] Constater 10 751 identifiants de suivi distincts sur 5 000 frames et des effectifs variables ; documenter l'impossibilité de supposer un ID biologique permanent.
- [ ] Choisir la ou les frames sur critères observables et documentés.

**Livrable :** audit des données, dictionnaire des variables, provenance et sélection de frames.

### Phase B — Construction du graphe (P0)

- [ ] Définir et documenter la distance euclidienne entre deux individus.
- [ ] Déterminer un rayon `R` cohérent avec les unités des données ; formaliser `d_ij ≤ R` ou `d_ij < R`.
- [ ] Construire un **graphe simple, non orienté et sans boucle** par frame.
- [ ] Associer à chaque nœud ses attributs disponibles et à chaque arête sa distance géométrique.
- [ ] Justifier le modèle : absence de direction, règle d'adjacence, attributs et éventuels poids.
- [ ] Vérifier les propriétés du graphe avec quelques tests simples (symétrie, doublons, arêtes attendues).
- [ ] Exporter la figure du graphe et `N`, `M`.

**Livrable :** scripts de construction et figure reproductible du graphe.

### Phase C — Analyses obligatoires (P0)

- [ ] Décrire `N = |V|`, `M = |E|` et le type de graphe.
- [ ] Évaluer la connectivité et lister les tailles des composantes.
- [ ] Calculer la proportion de nœuds dans la plus grande composante (`LCC`).
- [ ] Calculer le **diamètre** sur une composante annoncée (par exemple LCC) si le graphe est déconnecté.
- [ ] Calculer le **rayon** selon la même convention ; expliciter longueurs de chemin **en sauts** si non pondérées.
- [ ] Définir le traitement d'une frame vide, des isolés et des composantes réduites à un sommet.
- [ ] Calculer et interpréter les centralités pertinentes (degré et intermédiarité ; proximité selon intérêt).
- [ ] Exécuter une méthode de communautés adaptée, documenter paramètres et interpréter le résultat.
- [ ] Vérifier les métriques sur des graphes simples de contrôle avant d'en tirer des conclusions.

**Livrable :** tableau d'indicateurs, figures et commentaires contextualisés.

**Convention candidate :** si `G` est déconnecté, utiliser `G_LCC`, annoncer `|V_LCC|/|V|`, donner `diameter(G_LCC)` et `radius(G_LCC)` et décrire les autres composantes. Aucun résultat numérique n'est encore produit.

### Phase D — Interprétation et robustesse (P0/P1)

- [ ] Relier les résultats à des configurations observées du banc, sans inférences causales non étayées.
- [ ] Distinguer connectivité, communautés et clustering géométrique.
- [ ] Tester un second seuil `R` ou plusieurs frames si le temps le permet.
- [ ] Contrôler l'effet du nombre de poissons observés et de la dépendance temporelle.
- [ ] Préparer **3 à 5 figures** informatives et lisibles pour le rapport.
- [ ] Rédiger les limites : seuil arbitraire, imperfections du suivi, un graphe de proximité n'observe pas directement une communication entre poissons.

**Livrable :** interprétation scientifique et analyses de sensibilité ciblées.

### Phase E — GitHub et reproductibilité (P0)

- [x] Identifier le dépôt GitHub **dédié au projet Graph Analytics** : https://github.com/Charles-Scannavino/Projet_Graph_Analytics.
- [x] Publier `CONTEXT.md` et `AVANCEMENT.md` à la racine.
- [x] Publier la première version des modules et tests : commit `748e463` sur `main`, 10 tests réussis en local.
- [ ] Ajouter les scripts de métriques, communauté, visualisation, comparaison/simulation et éventuellement figer les versions exactes.
- [ ] Inclure le dataset si raisonnable, sinon utiliser un hébergement externe et donner le lien dans `README.md`.
- [x] Créer un README de travail : problématique, source/licence, paramètres et commandes préliminaires.
- [ ] Finaliser et vérifier les commandes de reproduction et références pour le rendu.
- [ ] Attribuer précisément les éventuelles contributions de code préexistant utilisées et les codes provenant d'Internet.
- [ ] Tester sur un environnement propre et s'assurer qu'aucune clé ou donnée sensible n'est publiée.

**Livrable :** dépôt GitHub reproductible, documenté et vérifié.

### Phase F — Rapport et soutenance (P0)

- [ ] Utiliser **le modèle de rapport fourni sur Inside**.
- [ ] Écrire et vérifier un **PDF de 15 pages maximum**.
- [ ] Mentionner les **deux membres**, l'URL du dépôt et la provenance des données/code.
- [ ] Présenter question, construction du graphe, métriques, conventions, résultats et limites.
- [ ] Déclarer les **outils d'IA effectivement employés**, leur fonction et les contrôles réalisés.
- [ ] Préparer un support PowerPoint ou équivalent : **8 minutes** d'exposé et **2 minutes** de réponses.
- [ ] Répartir l'oral entre les deux étudiants ; répéter avec chronomètre.
- [ ] Remettre le rapport sur Inside **avant le 10/11/2026 à 08:00** ; vérifier sa réception.
- [ ] Participer à la soutenance **le 10/11 de 14:00 à 17:00** jusqu'à la fin de la session.

**Livrables :** rapport, slides et dépôt GitHub vérifiables.

## 4. Calendrier opérationnel proposé

> Ce calendrier organise le travail ; les dates ci-dessous, hors remise et soutenance, ne sont pas imposées par l'enseignant.

| Date | Activité principale | Validation attendue |
|---|---|---|
| **31 octobre** | Binôme, accès aux données, template Inside | Entrées disponibles et sources vérifiées |
| **1–2 novembre** | Audit et construction du premier graphe | Graphe calculé, `N`, `M`, schéma clair |
| **3–4 novembre** | Connectivité, composantes, diamètre, rayon, centralités | Analyses obligatoires calculées |
| **5 novembre** | Communautés ; comparaison optionnelle | Partition expliquée et figures sauvegardées |
| **6 novembre** | Robustesse et interprétation | Résultats consolidés et limites explicitées |
| **7–8 novembre** | GitHub/README, rapport ≤15 pages sur template Inside | Livrables reproductibles, rapport relu |
| **9 novembre** | Contrôle complet, répétition de 8 min et dépôt anticipé | Version prête avant l'échéance |
| **10 novembre à 08:00** | **Date limite officielle : PDF sur Inside** | Soumission confirmée |
| **10 novembre, 14:00–17:00** | **Soutenance officielle** | Deux participants, présence continue |

## 5. Répartition des rôles (à convenir à deux)

| Domaine | Responsable | Statut |
|---|---|---|
| Acquisition et audit du dataset | À convenir | Non attribué |
| Construction des graphes | À convenir | Non attribué |
| Analyses obligatoires et tests | À convenir | Non attribué |
| Figures, interprétation et rédaction | Travail partagé | En préparation |
| Rapport et contrôle des références | Travail partagé | À faire |
| Présentation | Les deux étudiants | À faire |

Ne pas afficher un travail individuel ou collectif comme terminé sans preuve, ni attribuer fictivement des tâches à un membre.

## 6. Questions ouvertes

- [ ] Qui est le second membre du binôme ?
- [x] Oui : `Data/schooling_frames.json` vérifié, 86 762 262 octets, 5 000 frames.
- [x] 87 à 289 observations par frame, moyenne 223,62 ; 10 751 IDs distincts sur la séquence, ID de suivi non permanent.
- [ ] Quelles sont les unités et quel seuil `R` est justifié ?
- [ ] Quelles frames seront retenues ?
- [ ] Quel algorithme de communautés et quelles centralités sont finalement choisis ?
- [ ] Le modèle de rapport Inside est-il disponible ?
- [x] URL du dépôt GitHub : https://github.com/Charles-Scannavino/Projet_Graph_Analytics
- [ ] Quels codes préexistants et outils d'IA ont effectivement contribué au rendu ?

## 7. Risques et stratégies de réponse

| Risque | Importance | Action |
|---|---|---|
| Dataset indisponible | Résolu | JSON 2D récupéré et audité, source conservée sur Drive |
| Unités ou seuil de voisinage non maîtrisés | Élevée | Audit des unités, justification de `R`, robustesse |
| Oubli du diamètre ou du rayon | Critique | Checklist P0, calcul explicite et convention des composantes |
| Mauvaise gestion de la déconnexion | Élevée | Métriques sur LCC ou par composante, description du choix |
| Analyse insuffisamment interprétée | Élevée | Formuler une question, discuter le sens des métriques et leurs limites |
| Absence de deuxième membre | Critique | Définir le binôme et partager la soutenance |
| Mauvais modèle/rapport trop long | Critique | Télécharger template Inside, vérifier ≤15 pages |
| Sources ou code non attribués | Critique | Conserver un registre de provenance et citer précisément |
| Dépôt non reproductible | Élevée | README, versions, test d'installation propre |
| Extensions chronophages | Élevée | Reporter 3D, Neo4j, simulateur et LLM tant que P0 n'est pas terminé |
| Clé API inscrite en clair dans un script de travail | Critique | Révoquer/renouveler la clé ; ne publier aucun script non assaini |

## 8. Journal de projet

### 4 novembre 2026 — Figures temporelles publiées et 38/38 tests réussis

- [x] `python -u -m src.plot_temporal` : 5 figures (10 exports PNG/SVG) régénérées avec suppression automatique des espaces finaux dans les SVG (**16,18 s** pour cette exécution) ; (graph-analytics) fonctionne.
- [x] `python -u -m pytest -v --durations=10` : **38 passed in 63,52 s**, première validation exhaustive de l'ensemble avec nouveau module de figures. Le test `test_real_frame_communities` a nécessité **31,59 s**, sans échec.
- [x] `git diff --cached --check` : aucune erreur ; **12 nouveaux fichiers** publiés dans le commit **`202b62a`** (module `src/plot_temporal.py`, `tests/test_plot_temporal.py`, 5 PNG + 5 SVG). `git push origin main` réussi et `git status` propre.
- [ ] Examiner visuellement les figures avant conclusion : les tests prouvent l'existence et la validité des fichiers, **pas** la lisibilité des légendes ni la pertinence des axes.
- [ ] **Étude de sensibilité à R** : comparer R = 60, 80, 100, 120 et 140 sur **les mêmes 21 frames**, angle mort arrière fixé à **25°**, en utilisant les proportions / mesures normalisées, et garder R = 100 comme référence exploratoire.
- [ ] Générer tableau et graphiques de robustesse ; interpréter l'influence du rayon, les limites des identifiants `onfish`, puis produire rapport et présentation.

---



### 4 novembre 2026 — Six tests supplémentaires de figures temporelles réussis

- [x] `python -u -m pytest tests/test_plot_temporal.py -v -s --durations=5` : **6 passed in 4,32 s** (test PNG/SVG en 0,64 s) : CSV valide et tri, champs manquants, CSV vide, NaN, génération de 10 exports PNG/SVG, CSV réel de 21 frames.
- [x] Dix figures locales confirmées par `ls -lh results/figures/temporal_*` : cinq PNG et cinq SVG, taille non nulle. `src/plot_temporal.py` et `tests/test_plot_temporal.py` sont également présents en local.
- [x] Cumul **38 tests individuels validés**, mais nouvelle **exécution globale de 38 tests encore à faire**.
- [ ] Les **12 nouveaux fichiers sont non suivis par Git**, et ne sont pas encore publiés : `src/plot_temporal.py`, `tests/test_plot_temporal.py` et les 10 figures `results/figures/temporal_*.png/.svg`.
- [ ] Vérifier les éventuels espaces de fin de ligne SVG avant staging, lancer la suite complète, `git diff --cached --check` puis publier les 12 fichiers. Examiner les figures avec captures avant conclusions visuelles définitives.
- [!] Ne pas confondre « 21 frames échantillonnées parmi 5000 » et une série exhaustive ; conserver R = 100 et l'angle mort arrière à 25° pour cette première exploration.

---



### 4 novembre 2026 — Cinq graphiques temporels générés localement

- [x] `src/plot_temporal.py` exécuté **localement** depuis l'environnement `~/.venvs/graph-analytics` : `python -u -m src.plot_temporal`.
- [x] Lecture du CSV de **21 frames**, production de **5 figures** en PNG et SVG (**10 fichiers**) dans `results/figures/`, en **1,81 s** : `temporal_fish_count`, `temporal_density`, `temporal_clustering`, `temporal_modularity`, `temporal_connectivity`.
- [x] `open results/figures/temporal_*.png` lancé sans erreur Terminal apparente ; **qualité visuelle non encore contrôlée** via captures ou inspection des fichiers.
- [!] Les courbes relient des frames échantillonnées espacées de 250 frames ; **pas une mesure exhaustive des fluctuations entre les points**. La connectivité spatiale (plus grande CC) et celle orientée (plus grande SCC) ne sont pas des notions identiques. Angle mort 25° constant.
- [ ] Ajouter des tests automatisés au nouveau module (import, colonnes requises, CSV vide/non fini, exports PNG/SVG), puis contrôler les figures et publier les fichiers locaux sur GitHub.
- [ ] Normaliser au besoin les espaces finaux dans les fichiers SVG générés avant `git diff --cached --check` ; les SVG Matplotlib précédents en comportaient.

---



### 4 novembre 2026 — Correction CRLF publiée et vérifiée

- [x] Commit **`2ff8ce4`** publié sur `main` : correction de `src/temporal_analysis.py`, test de non-régression dans `tests/test_temporal_analysis.py`, normalisation du CSV `results/temporal/metrics_step250_R100.csv`.
- [x] `csv.DictWriter` utilise maintenant `lineterminator="\\n"`, le test vérifie `b"\\r\\n" not in output.read_bytes()` et le CSV GitHub a bien des fins de ligne LF, pas de CRLF (21 lignes de données).
- [x] **7 tests temporels réussis** après correctif (**11,34 s**) ; `git diff --cached --check` sans message ; `git push origin main` réussi ; dernier `git status` propre et synchronisé.
- [ ] Prochaine étape : générer des séries temporelles en PNG/SVG à partir du CSV **publié** : nombre de poissons, densité, clustering, modularité Louvain et proportion dans les composantes principales. Ajouter des tests de visualisation et publier les figures.
- [!] Pour les figures, les graphes spatiaux sont non orientés, les graphes de visibilité orientés ; **LCC spatiale et SCC de visibilité ne sont pas des notions identiques**, même si leurs proportions peuvent être comparées descriptivement. L'angle mort reste 25°.

---



### 4 novembre 2026 — Publication temporelle et 32/32 tests validés

- [x] `python -u -m pytest -v -s --durations=10` : **32 passed in 56,94 s**. Exécution complète ; test Louvain sur frame réelle le plus long (**32,17 s**).
- [x] Commit **`268a320`** publié sur `main` : `src/temporal_analysis.py`, `tests/test_temporal_analysis.py`, `results/temporal/metrics_step250_R100.csv`. `git status` : **working tree clean**, synchronisé avec `origin/main`.
- [!] `git diff --cached --check` signalait des `trailing whitespace` pour les **22 lignes du CSV**. Fichier vérifié sur GitHub : ce sont les fins de ligne **CRLF (`\\r\\n`)** émises par `csv.DictWriter` sans `lineterminator`. Correction recommandée dans l'exporteur (`lineterminator="\\n"`), dans le fichier CSV et dans le test de non-régression, sans modifier les métriques.
- [x] Exploration du CSV 21 frames : poissons observés **91 à 280** ; densité spatiale **0,02906 à 0,12527** ; clustering spatial **0,53164 à 0,62994** ; modularité spatiale **0,56917 à 0,73456** ; part d'arcs visibles parmi les deux directions de chaque arête spatiale **0,92428 à 0,94171**.
- [ ] Générer des figures temporelles séparées avec axes explicites, les données du CSV et une comparaison prudente des modèles, en conservant l'angle mort fixe de 25° et en indiquant les effets du nombre variable de poissons.
- [ ] Faire la correction CRLF localement, exécuter les tests de non-régression puis publier un commit ciblé.

---



### 4 novembre 2026 — Validation des 7 tests temporels et export local

- [x] `python -u -m pytest tests/test_temporal_analysis.py -v -s --durations=5` : **7 passed in 7,10 s**. Contrôles : conversion des observations, longueur/identifiants incohérents, graphe spatial et visibilité sur données contrôlées (arc visible, angle mort 25°), streaming de trois frames synthétiques, contenu CSV, frame manquante, paramètres `step`/`radius` invalides.
- [x] `git status` local : branche `main` synchronisée avec `origin/main`, mais **3 éléments non suivis** : `src/temporal_analysis.py`, `tests/test_temporal_analysis.py`, `results/temporal/metrics_step250_R100.csv` (**3,0 Ko**).
- [x] Cumul **32 tests distincts validés localement** (25 anciens en 14,94 s, 7 nouveaux en 7,10 s). **Reste à exécuter la suite complète de 32 tests d'un seul tenant** après publication.
- [ ] Publier les trois fichiers temporels ensemble depuis le Mac par `git add` / `git commit` / `git push` ; vérifier ensuite le statut Git.
- [ ] Générer des courbes à partir du CSV, puis poursuivre la robustesse par variation du rayon `R`, avec angle mort fixe **25°**.
- [!] Prudence : nombre de poissons variable d'une frame à l'autre et communauté Louvain non équivalente à un sous-banc individuel biologiquement stable.

---



### 4 novembre 2026 — Analyse temporelle exploratoire réussie (21 frames)

- [x] Module **local** `src/temporal_analysis.py` exécuté : `python -u -m src.temporal_analysis --step 250 --radius 100`. Lecture streaming en une passe de **5 000 frames** et analyse de **21 frames** (1, 251, …, 4751, 5000), angle mort **25° constant**.
- [x] **Durée 7,52 s**, avec messages de progression ; export local `results/temporal/metrics_step250_R100.csv`, 21 lignes de données et en-tête.
- [x] Valeurs issues du terminal : frame 1 = 253 poissons, 11 communautés spatiales, 10 de visibilité ; frame 501 = 91 poissons, 5 et 6 communautés ; frame 4501 = 280 poissons, 8 et 10 ; frame 4751 = 272 poissons, 13 et 12 ; frame 5000 = 262 poissons, 12 et 11.
- [!] Nombre de poissons observés très variable (dans les 21 mesures affichées : **91 à 280**) ; **ne pas** interpréter directement les nombres absolus de communautés comme des transitions comportementales. Prioriser métriques normalisées, part de la plus grande composante et modularité ; temporalité et validité des ID `onfish` à expliciter.
- [ ] `src/temporal_analysis.py` et le CSV **non encore publiés** sur GitHub. Prochaine étape : tests unitaires du streaming, paramètres, frames absentes, export, puis contrôle du contenu CSV et commit.
- [ ] Produire des courbes temporelles et vérifier la robustesse pour plusieurs valeurs **de R uniquement** (angle mort invariant 25°). Structurer ensuite le rapport et prioriser résultats expérimentaux avant simulation Boids.

---



### 4 novembre 2026 — Nouvel environnement local validé : 25/25 tests

- [x] Création de `~/.venvs/graph-analytics` hors du dossier `~/Documents` (Python 3.12.6), installation **sans cache** des versions précédentes : NumPy 2.5.4, SciPy 1.18.1, NetworkX 3.7, Matplotlib 3.11.2, ijson 3.6, pytest 9.2.0.
- [x] Le fichier `~/.venvs/graph-analytics/lib/python3.12/site-packages/numpy/__init__.py` **n'a pas l'attribut `dataless`**.
- [x] Mesures d'imports séquentiels : numpy 0,355 s ; scipy.spatial.distance 5,986 s ; networkx 0,093 s ; matplotlib.pyplot 2,250 s ; ijson 0,179 s ; pytest 0,068 s ; **total 8,931 s**.
- [x] `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -u -m pytest tests/test_visualize.py -v -s --durations=5` : **5 passed in 10,40 s** ; toutes les figures produites dans les tests.
- [x] `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -u -m pytest -v -s --durations=10` : **25 passed in 14,94 s** ; sous-ensembles graphes 10, métriques 5, Louvain 5, visualisation 5.
- [!] Le problème de performance des imports a été fortement réduit par l'environnement hors `Documents`; **l'hypothèse des placeholders `dataless` est renforcée**, sans diagnostic exhaustif du service iCloud/macOS. Les fichiers sources du dépôt et les données restent dans `Documents`, à surveiller.
- [ ] Conserver provisoirement l'ancien `.venv` (ne pas le supprimer tant qu'une stratégie de déplacement n'est pas décidée).
- [ ] Prochaine étape : analyse temporelle des graphes réels en **streaming une seule lecture**, sur des frames réparties dans le temps, progression affichée, même rayon spatial et même angle mort arrière **25° constant**, export CSV/figures.
- [ ] Rapport, méthodologie de sélection de R et comparaison prudente avec simulation Boids.

---



### 4 novembre 2026 — Cause probable des imports très lents : fichiers dataless

- [x] Inspection locale : `ls -lO@` signale **`hidden,compressed,dataless`** sur les fichiers `.venv/lib/python3.12/site-packages/numpy/__init__.py` et `scipy/spatial/_kdtree.py`. Cela signifie que le contenu de ces fichiers n'est pas physiquement matérialisé localement.
- [x] Le dossier `~/Documents` porte les attributs `com.apple.file-provider-domain-id`, `com.apple.fileprovider.detached` et `com.apple.icloud.desktop`, compatibles avec une gestion iCloud/File Provider. **Hypothèse forte :** récupérations à la demande pendant les imports responsables du retard, à vérifier lors d'un test dans un environnement non synchronisé.
- [x] Volume `/System/Volumes/Data` : **228 Gio, 195 Gio utilisés, 8,7 Gio disponibles (96 %)**.
- [!] `git status` a précédemment rencontré `fatal: mmap failed: Operation canceled`, puis a réussi ; lien avec les placeholders plausible mais **non confirmé**.
- [ ] **Action recommandée sans suppression :** créer un nouveau venv dans `~/.venvs/graph-analytics` (hors `Documents`), installer les dépendances selon `requirements.txt`, vérifier l'absence de `dataless` et mesurer le temps d'import NumPy/SciPy/Matplotlib/NetworkX.
- [ ] Ensuite envisager une copie entièrement locale du dépôt vers `~/Developer/Projet_Graph_Analytics`, avec dataset réellement matérialisé ; **ne pas supprimer le dépôt original ni son venv tant que la copie n'est pas validée**.
- [ ] Libérer de l'espace disque avec précaution avant toute grosse copie ; éviter tout nettoyage destructif automatique.
- [ ] Une fois le fonctionnement stabilisé, lancer l'analyse temporelle progressive (angle mort 25° constant).

---



### 4 novembre 2026 — Visualisations publiées sur GitHub

- [x] **Commit `af1376a`** publié et vérifié sur `main` : `src/visualize.py`, `tests/test_visualize.py`, `results/figures/frame1_spatial_louvain.png/.svg`, `results/figures/frame1_visibility25_louvain.png/.svg` (6 fichiers).
- [x] Avant commit, `GIT_PAGER=cat git diff --cached --check` : aucune erreur après suppression des espaces de fin de ligne des deux SVG.
- [x] `git push origin main` réussi ; `git status` indique `nothing to commit, working tree clean`.
- [x] **25 tests individuels validés** en exécutions ciblées / précédentes (10 modèles, 5 métriques, 5 Louvain, 5 visualisation). *Pas de nouvelle exécution de la suite complète après le dernier commit.*
- [!] Lenteurs d'import de NumPy/SciPy/NetworkX/Matplotlib récurrentes, ainsi qu'un `fatal: mmap failed: Operation canceled` ponctuel dans `git status`, disparu lors de la vérification finale. Cause à diagnostiquer avant de lancer la grande analyse temporelle ; vérifier le statut stockage/cloud et les fichiers locaux sans modifier les environnements tant que la cause est inconnue.
- [ ] Prochaine livraison : pipeline temporel reproductible avec lecture streaming du JSON, échantillonnage initial sur quelques dizaines de frames, mesures de structure et Louvain (angle mort 25° constant), progression affichée, export CSV/figures.
- [ ] Puis étude de sensibilité du rayon **R**, interprétation du dataset, rapport ≤15 pages et présentation.

---



### 3 novembre 2026 — Cinq tests de visualisation réussis

- [x] `tests/test_visualize.py` créé localement pour tester graphe vide, partition incohérente, figures PNG/SVG spatiale/orientée et cas sans arêtes (`modularity=None`).
- [x] `src/visualize.py` corrigé localement pour afficher `N/A` quand la modularité ou le rayon sont absents.
- [x] Exécution avec Anaconda `base` désactivé et `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` : **5 passed in 924.15s (15 min 24 s)** ; durée totale du lanceur **935.38 s**.
- [x] Les trois tests générant des figures ont duré respectivement **15,17 s**, **0,14 s** et **0,12 s** ; l'essentiel des 924 s est donc lié à la **collecte/importation**, non aux calculs des tests. Trace lors de la collecte : `networkx.utils` via `importlib.get_data`, cohérente avec les imports précédemment très lents NumPy/SciPy.
- [!] Cause racine de la lenteur encore indéterminée ; le seul fait que les modules soient dans `~/Documents` et que le SSD soit occupé à 95 % ne prouve pas un problème spécifique de disque ou de synchronisation cloud.
- [ ] Publier `src/visualize.py`, `tests/test_visualize.py` et les quatre figures PNG/SVG validées (pas encore confirmées sur GitHub).
- [ ] Examiner séparément l'environnement Python et les accès au système de fichiers avant l'analyse multi-frames.
- [ ] Analyse temporelle, figures du rapport et comparaison exploratoire avec une simulation Boids.

---



### 3 novembre 2026 — Visualisations Louvain produites, imports Python excessivement longs

- [x] `src/visualize.py` exécuté **localement** via `runpy.run_module("src.visualize", run_name="__main__")` avec diagnostics `faulthandler` toutes les 20 s.
- [x] Les 7 étapes ont abouti ; **quatre fichiers créés localement** dans `results/figures/` : `frame1_spatial_louvain.png`, `frame1_spatial_louvain.svg`, `frame1_visibility25_louvain.png`, `frame1_visibility25_louvain.svg`.
- [x] Durée interne à `main()` : **19,43 secondes** ; durée globale du processus **1 018,90 secondes** (environ 16 min 59 s). Les appels d'importation et la préparation avant `main()` constituent donc presque toute l'attente.
- [!] Diagnostic : `faulthandler` a montré des imports Python très lents via `importlib._bootstrap_external.get_data`, successivement dans NumPy, SciPy (`sparse`, `linalg`, `spatial`) et autres sous-modules. **Le programme progresse et termine** ; aucune cause racine confirmée. Il serait prématuré de conclure à un bug de Matplotlib, NumPy ou au disque saturé.
- [ ] Vérifier visuellement les PNG et les dimensions/fichiers produits ; créer des tests ciblés des fonctions de visualisation et publier le script et figures retenues.
- [ ] Diagnostiquer séparément le système de fichiers, l'occupation mémoire/SSD et l'éventuelle synchronisation cloud du dossier `Documents`, avant de réinstaller les dépendances.
- [ ] Les quatre figures et `src/visualize.py` sont **locaux uniquement** ; pas de publication GitHub confirmée.

---



### 3 novembre 2026 — Louvain publié et dépôt synchronisé

- [x] Commit **`a92ce23`** publié sur `main` : `src/community_detection.py`, `tests/test_community_detection.py` et `results/communities_frame1_R100.json`.
- [x] `python -m pytest tests/test_community_detection.py -v -s --durations=5` : **5 passed in 0.44 s** ; test réel en **0,04 s**.
- [x] `git status` après `git push origin main` : branche à jour, **working tree clean**.
- [ ] Préparer une visualisation scientifique des deux partitions Louvain avec coordonnées `pos` des poissons, échelles communes et légendes indépendantes : `src/visualize.py`.
- [ ] Tester puis publier les figures PNG/SVG ; ne pas inférer l'équivalence biologique de communautés de même couleur entre graphes.

---



### 3 novembre 2026 — Louvain exécuté sur les deux graphes

- [x] `src/community_detection.py` créé et exécuté localement : `python -m src.community_detection` a terminé en **0,13 seconde**, en affichant les étapes de progression.
- [x] Frame 1, `R=100`, `seed=42`, `resolution=1.0`, `weight=None` : **11 communautés, modularité 0,70344** sur graphe spatial ; tailles **64, 47, 38, 30, 27, 26, 11, 5, 3, 1, 1**.
- [x] Même frame, angle mort constant **25°**, graphe dirigé : **10 communautés, modularité 0,70500** ; tailles **65, 43, 38, 37, 30, 30, 5, 3, 1, 1**.
- [x] Fichier local produit : `results/communities_frame1_R100.json`, incluant la partition par ID de suivi.
- [ ] Tests `pytest` du module, y compris la couverture des identifiants et les cas de graphe vide/sans lien ; **non encore exécutés**.
- [ ] Commit de `src/community_detection.py`, `tests/test_community_detection.py` et du fichier JSON de résultats ; le dépôt distant **ne contient pas encore** ces nouveaux fichiers.
- [ ] Visualiser les communautés sur les positions réelles et interpréter leur signification avec prudence (graphe dirigé/non dirigé et modularités non directement interchangeables).

**Prochaine étape :** ajouter les tests ciblés et publier les fichiers, avant la visualisation des communautés.

---



### 3 novembre 2026 — 15 tests réussis, mais lenteur d'exécution à diagnostiquer

- [x] `python -m pytest -v -s` exécuté depuis le venv du Mac M1, Python 3.12.6 / pytest 9.2.0 : **15 passed in 319.06s (0:05:19)**.
- [x] 10 tests déjà réussis sur les modèles spatial et directionnel à angle mort fixé à 25°.
- [x] 5 nouveaux tests du module local `src/graph_metrics.py` : isolé, cycle orienté, chaîne orientée, erreur sur graphe vide et régression frame 1 réelle, tous **PASSED**.
- [x] Première frame : 253 sommets, 1 281 arêtes spatiales, 2 386 arcs orientés ; diamètres LCC/SCC 23/24 et rayons 12/12 ; résultats cohérents avec l'exécution du module.
- [!] **Durée excessivement longue (319 s)** : `import numpy` a précédemment abouti en 15,40 s avec une trace au niveau de `importlib.get_data`, mais le ralentissement de toute la suite n'a pas encore été expliqué. Ne pas attribuer avec certitude le problème au SSD, à NumPy ou à pytest.
- [ ] Diagnostiquer à l'aide de `python -m pytest -v --durations=10` (séparer temps de collecte et durées des tests) puis, si nécessaire, `python -X importtime -c 'import numpy'`.
- [ ] **Commit du code restant :** `src/graph_metrics.py` et `tests/test_graph_metrics.py` validés localement, pas encore publiés.
- [ ] Poursuivre avec Louvain, figures et analyse temporelle avant extension de la simulation Boids.

---



### 3 novembre 2026 — Premier module de métriques structurelles exécuté

- [x] `src/graph_metrics.py` créé localement et exécuté avec `python -m src.graph_metrics` : **1,12 s**, affichage des six étapes, sortie JSON locale `results/metrics_frame1_R100.json`.
- [x] **Frame 1, `R=100` :** graphe spatial = 253 nœuds, 1 281 arêtes, 4 composantes, LCC 248 (98,02 %), diamètre LCC 23, rayon LCC 12, densité 0,04018, clustering 0,578, degré moyen 10,1265.
- [x] **Frame 1, visibilité angle mort 25° :** 253 nœuds, 2 386 arcs, 4 composantes faibles, 4 composantes fortes, plus grande SCC 248 (98,02 %), diamètre SCC 24, rayon SCC 12, densité 0,03742, clustering dirigé 0,54551, moyenne degrés entrant/sortant 9,4308.
- [x] Top intermédiarité spatiale : ID de suivi 99458 (0,16501). Top intermédiarité directionnelle : ID de suivi 99981 (0,14945). Ces ID **ne prouvent pas un leadership**.
- [x] Conventions : diamètre/rayon sur la plus grande composante pertinente, chemins **non pondérés en sauts** ; centralités sur graphes entiers, avec avertissement sur différences entre clustering dirigé/non dirigé.
- [ ] Ajouter `tests/test_graph_metrics.py` et valider les cas simples, les composantes isolées et les résultats de la frame 1 ; **ne pas affirmer que ce module est encore testé/committé**.
- [ ] Git : pousser `src/graph_metrics.py` avec les tests ; produire mesures sur plusieurs frames, Louvain, export CSV, figures et interprétation.
- [!] Le fichier `results/metrics_frame1_R100.json` est une sortie calculée locale, non encore un livrable public ; ne pas confondre cette première frame avec des résultats sur les 5 000 frames.

---



### 3 novembre 2026 — Extension décidée : simulation Boids puis comparaison réel/simulé

- [x] Premier commit du code validé publié depuis le Mac sur GitHub : `748e463` (`src/data_loader.py`, `graph_builder.py`, `visibility_graph.py`, `tests/test_graph_models.py`, `requirements.txt`, `.gitignore`). `git status` local annoncé **clean** après `git push origin main`.
- [x] **10 tests `pytest` réussis** localement le 3 novembre (`10 passed in 0.56s`), avec angle mort arrière 25°.
- [x] Extension **proposée et cadrée** : reconstruire un simulateur Boids à partir des anciennes fonctions assainies, puis comparer des fenêtres réelles et simulées avec des graphes et métriques identiques.
- [ ] Implémenter `src/boids_simulation.py` avec angle mort constant 25°, pas temporel/échelle calibrés, coefficients explicitement déclarés, progression terminal et gestion des frontières.
- [ ] Auditer les segments de suivi individuels sur fenêtres courtes pour vérifier appariement et vitesse observée ; ne pas traiter `vx,vy` normalisés comme des vitesses physiques.
- [ ] Implémenter `src/boids_comparison.py` : mêmes positions initiales, simulation libre, métriques de réseau (degré, composantes, clustering, communautés) et de banc (polarisation, voisin le plus proche, déplacements si ID stables).
- [ ] Calibrer les coefficients sur un sous-ensemble de fenêtres et évaluer sur des fenêtres disjointes, avec baseline de persistance et ablations des trois forces.
- [ ] Documenter les limites et l'absence de preuve directe que les poissons obéissent aux règles de Boids.
- [!] **Priorité pédagogique :** finaliser les métriques de Graph Analytics, les communautés, figures et le rapport **avant** de consacrer du temps à cette extension P1. Date limite officielle : 10/11/2026 08:00.
- [!] Ne jamais publier l'ancien script Boids contenant une clé Gemini en clair : révoquer/renouveler la clé et extraire seulement les calculs utiles.

**Résultat attendu du volet optionnel :** quantifier la proximité du modèle Boids avec les comportements observés, identifier quelles règles améliorent la prédiction, et signaler les limites d'inférence causale.

---



### 3 novembre 2026 — Graphe de visibilité définitif à 25° exécuté localement

- [x] Paramètre par défaut de `src/visibility_graph.py` modifié localement en `rear_blind_angle_deg=25` et boucle de démonstration limitée à `(25,)`.
- [x] Exécution locale `python -m src.visibility_graph` : **253 nœuds**, **2 386 arcs**, **4 composantes faiblement connexes** et **4 composantes fortement connexes**, pour `frame_id=1`, `R=100`, angle mort arrière constant de **25°** (champ visible 335°).
- [x] Valeur de référence fondée sur la littérature pour le Golden shiner, appliquée uniformément ; aucune sensibilité à l'angle prévue.
- [ ] Adapter les tests locaux `tests/test_graph_models.py` pour vérifier la configuration à 25° et ses cas limites ; `pytest` n'a pas encore été relancé depuis le changement.
- [ ] Ajouter des affichages de progression `print(..., flush=True)` dans les scripts lancés depuis le Terminal.
- [ ] Publier le code et les tests locaux (le dépôt GitHub contient à cette étape la documentation mais pas encore les nouveaux scripts).
- [ ] Compléter les tailles des composantes, centralités, diamètre/rayon et détection des communautés.

**Suite immédiate :** réviser les tests, lancer `python -m pytest -v`, vérifier le `.gitignore`, puis créer un commit local et le pousser.

---



### 3 novembre 2026 — Décision ferme : angle mort 25° pendant toute l'étude

- [x] **Paramètre figé par décision du responsable :** `rear_blind_angle_deg=25` (largeur totale de l'angle mort horizontal arrière) pour **chaque poisson et chaque frame** du modèle directionnel.
- [x] Champ visible horizontal nominal correspondant : **335°** ; l'axe visuel est approximé par `(vx,vy)`, sans occlusion.
- [x] **Plus de comparaison entre angles 25°, 60° et 240° dans le projet.** Les calculs à 60°/240° figurent exclusivement dans le journal des essais déjà réalisés.
- [x] Le **graphe spatial non orienté** reste une référence indépendante ; l'étude de la sensibilité au **rayon de proximité `R`** reste envisageable, sans variation d'angle.
- [x] Régler le code **local** `src/visibility_graph.py` sur 25° (argument par défaut et exécution principale).
- [ ] Adapter les tests à la configuration retenue.
- [x] Exécuter la frame 1 avec 25° et enregistrer les métriques réellement obtenues : 253 nœuds, 2 386 arcs, 4 composantes faibles et 4 fortes.
- [ ] Après validation, committer le code assaini et les tests locaux (ils ne sont pas encore publiés).

**Priorité :** un seul modèle de visibilité défini avec angle mort constant 25°, pas une expérimentation comparative sur le champ de vision.

---



### 3 novembre 2026 — Documentation scientifique du champ visuel et règle de progression

- [x] Documenté dans `CONTEXT.md` : toute exécution de code depuis le Terminal doit afficher des messages de progression `print(..., flush=True)`, à fréquence maîtrisée et avec un bilan final.
- [x] Espèce confirmée : *Notemigonus crysoleucas* (Golden shiner).
- [x] Pita et al., PeerJ 2015, DOI 10.7717/peerj.1113 : **secteur aveugle arrière horizontal 25° ± 1,20°**, champ visuel horizontal **335° ± 3,5°** (9 adultes, yeux au repos, valeurs ± erreur standard rapportée).
- [x] Davidson et al., JRSI 2021, DOI 10.1098/rsif.2021.0142 : réutilisation du **25°** pour le Golden shiner.
- [ ] Exécuter le modèle directionnel avec `rear_blind_angle_deg=25`, sauvegarder les résultats et écrire au moins un test de régression spécifique.
- [ ] Distinguer dans le rapport l'angle anatomique, la direction de déplacement et les occlusions non modélisées.

**Décision ultérieure du 03/11/2026 :** `25°` est **l'unique angle retenu** pour l'étude ; les résultats à `60°` et `240°` sont des essais techniques historiques, **non retenus comme scénarios comparatifs finaux**.

---



### 3 novembre 2026 — Tests automatisés des graphes : 6/6 validés localement

- [x] Création locale du fichier `tests/test_graph_models.py` (6 cas, dont deux essais sur la frame 1 réelle).
- [x] Exécution locale `python -m pytest -v` sous Python 3.12.6 : **6 passed in 0.28s**.
- [x] Tests réussis : graphe spatial simple et distance, seuil strict `d<R`, arc vers l'avant et exclusion vers l'arrière, visibilité latérale avec deux secteurs aveugles, comptages de nœuds/arcs et composantes faibles/fortes sur la frame 1.
- [x] Test de cohérence : chaque arc du graphe directionnel correspond à une arête du graphe spatial de référence.
- [ ] Les fichiers `src/`, `tests/`, `.gitignore` et `requirements.txt` sont encore **locaux, non committés**, au moment de ce relevé ; publication sécurisée à effectuer.
- [ ] Tester davantage les cas limites (rayon invalide, angle invalide, direction nulle, positions superposées, frames avec une détection) et produire le module `graph_metrics.py`.
- [!] Validation algorithmique ≠ validation biologique du champ de vision ; les métriques de visibilité restent des hypothèses directionnelles.

**Prochaine étape :** synchroniser le journal, améliorer `.gitignore` pour exclure `.pytest_cache/`, vérifier les fichiers staged et committer uniquement le code contrôlé, puis calculer les métriques obligatoires.

---



### 3 novembre 2026 — Graphe de visibilité : premières sorties locales

- [x] Exécution sur Mac M1 de `python -m src.visibility_graph` ; 253 nœuds dans les deux variantes.
- [x] `R=100`, secteur aveugle arrière **60°**, champ de visibilité **300°** : **2 139 arcs**, **4 composantes faiblement connexes**, **5 fortement connexes**.
- [x] `R=100`, secteur aveugle arrière **240°**, champ de visibilité **120°** (convention angulaire de l'ancien simulateur) : **887 arcs**, **10 composantes faiblement connexes**, **226 fortement connexes**.
- [x] Comparaison numérique avec le graphe spatial : 1 281 arêtes non orientées → maximum 2 562 arcs orientés de proximité ; rétention approximative 83,5 % et 34,6 %.
- [ ] **Tests automatisés du modèle de visibilité non encore exécutés.** À écrire : sens avant/arrière, asymétrie, zone latérale, angle nul/240°, dépendance à `R`, sous-ensemble d'arcs du graphe spatial, conservation des nœuds/ID et absence de boucles.
- [ ] `visibility_graph.py` est **présent localement mais non confirmé sur GitHub** ; commit contrôlé requis.
- [!] Ne pas confondre la direction de déplacement et le regard réel : champ visuel/angle mort hypothétiques, occlusion non modélisée, pas de démonstration de leadership ou d'influence.
- [ ] Analyser le sens scientifique des composantes fortement/faiblement connexes avec l'angle fixé à **25°** ; justification scientifique ajoutée au CONTEXT.

**Suite prioritaire :** tester `graph_builder.py` et `visibility_graph.py` avec `pytest`, puis committer le pipeline assaini et réaliser les métriques obligatoires du cours.

---


### 3 novembre 2026 — Validation locale du graphe et clarification de l'angle mort

- [x] Mac M1 : Python 3.12.6 dans `.venv` ; dépendances installées ; `schooling_frames.json` disponible via lien symbolique dans `data/`.
- [x] Module local `src/data_loader.py` exécuté avec succès : frames 1 = 253, 1000 = 251, 2500 = 138, 5000 = 262 poissons détectés.
- [x] Module local `src/graph_builder.py` exécuté : frame 1, `R=60/100/120` → arêtes 454/1281/1824 ; composantes 35/4/3 ; LCC 162/248/251 ; résultats identiques à l'audit exploratoire.
- [ ] Code, `.gitignore` et `requirements.txt` encore **non committés depuis le Mac** au moment de ce journal ; `pytest` non exécuté.
- [x] **Convention validée du modèle actuel : graphe spatial simple NON ORIENTÉ, `d<R`, sans angle mort.** Le filtre angulaire n'était pas activé dans les métriques affichées.
- [x] Audit du simulateur ancien : `abs(delta)<=60°` représente un **cône visible frontal de 120°**, soit une zone non visible de **240°** ; le nom `angle_mort_degre` y est donc trompeur.
- [ ] **Modèle de visibilité distinct à construire** : proposer `rear_blind_angle_deg=60` comme largeur totale aveugle derrière le poisson (visible 300°), `nx.DiGraph()`, `i→j` si `d<R` et `abs(delta_ij)<=150°` ; convention et plausibilité biologique à confirmer avant interprétation.
- [ ] Écrire des tests séparés pour le modèle spatial et le modèle directionnel ; analyser degrés entrants/sortants, composantes faibles/fortes et effet de l'angle.
- [!] Ne pas confondre seuils `R=60,100,120` de l'analyse avec les forces/coefficients Boids du simulateur ; les coordonnées restent en unités natives non calibrées.

**Décision :** conserver les résultats de proximité comme **référence** et traiter l'orientation et l'angle mort comme **modèle de visibilité supplémentaire**, documenté et testé séparément. Les comptes de nœuds/arêtes précédents ne sont pas des résultats du modèle directionnel.

---


### 31 octobre 2026 — Audit effectif des ressources (Drive et environnement d'analyse)

- [x] Source localisée : `Data/schooling_frames.json` (86 762 262 octets), `Data/README.txt` ; DOI https://doi.org/10.7267/zk51vq07c (CC BY 4.0 d'après le README).
- [x] JSON complet lu : 5 000 frames, 1 118 118 détections, 87–289 poissons détectés/frame, moyenne 223,62, 10 751 identifiants de suivi distincts.
- [x] Contrôle de cohérence des champs `px,py,vx,vy,onfish` par frame et absence d'IDs dupliqués au sein d'une frame.
- [x] Prototypes exploratoires NetworkX sur plusieurs frames et rayons 60, 100, 120 ; diamètre/rayon mesurés sur la composante connexe principale.
- [x] Frame 1 : pour `R=100`, **253 nœuds, 1 281 arêtes, 4 composantes, diamètre LCC 23, rayon LCC 12, clustering 0,578**.
- [x] Louvain testé à `R=100` sur frame 1 : 11 communautés, modularité ≈0,703 (`seed=42`), à vérifier/interpréter dans le pipeline final.
- [x] Audit statique des scripts disponibles : le simulateur `simulate_boids()` repart uniquement de la frame 1 ; il **ne parcourt pas** les 5 000 observations enregistrées.
- [x] Dossier 3D inspecté : les fichiers `train/ZebraFish-XX/gt/gt.txt` existent et contiennent des coordonnées 3D ; `schooling_frames_3d.json` est vide (`{}`) ; le chemin du script 3D est incorrect.
- [!] **Sécurité : une clé Gemini en clair est présente dans un script de travail sur Drive. Révocation/renouvellement par le titulaire indispensable avant publication.**
- [ ] Clarifier les unités des positions et la normalisation des vecteurs de vitesse avant d'écrire « mm » / « mm/s ».
- [ ] Créer des scripts indépendants et testables pour les données **observées**, plutôt que de lancer la simulation, l'animation GIF et les appels API.
- [ ] Valider le binôme, le template Inside et les tâches de chacun.

**Périmètre prioritaire :** snapshots réels → graphes NetworkX → composantes, diamètre/rayon LCC, centralités, Louvain → sensibilité à `R` → rapport. 3D, interface et LLM reportés.


### 31 octobre 2026 — Documentation scientifique et planification

- [x] Exigences de l'énoncé transcrites et classées par priorité.
- [x] Définition de la problématique candidate et du modèle de graphe envisagé.
- [x] Décomposition des étapes de travail jusqu'à la remise officielle.
- [x] Préparation des documents `CONTEXT.md` et `AVANCEMENT.md`.
- [x] Validation du dataset et calcul ponctuel des métriques par un programme d'audit (hors dépôt).
- [ ] Livrer et tester le script final reproductible d'analyse des graphes sur GitHub.
- [x] Mise en ligne des documents dans le dépôt GitHub dédié.

**Prochaine action :** créer le pipeline autonome sur les frames observées, sécuriser la clé Gemini, choisir/justifier le rayon de voisinage, produire figures et tableau de résultats ; récupérer le template Inside.

---

*Mettre à jour ce journal après toute étape effectivement vérifiée, en consignant les fichiers, commandes, résultats, obstacles et décisions.*