# AVANCEMENT.md — Graph Analytics 2026 | Fish Schooling Networks

> **Dernière mise à jour :** 3 novembre 2026  
> **Version :** 2.2  
> **Statut :** lecture JSON et construction du graphe spatial vérifiées localement (3 novembre) ; code local et tests restant à publier/valider dans GitHub. Le modèle de visibilité à angle constant 25° fonctionne localement (frame 1 : 2 386 arcs, 4 composantes faibles et 4 fortes), mais les tests spécifiques à 25° et la publication des scripts restent à faire.  
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
- [ ] Ajouter les scripts de calcul et les dépendances exactes.
- [ ] Inclure le dataset si raisonnable, sinon utiliser un hébergement externe et donner le lien dans `README.md`.
- [ ] Créer un README : problématique, source/licence, installation, commandes, paramètres, fichiers d'entrée/sortie, références et usage de l'IA.
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