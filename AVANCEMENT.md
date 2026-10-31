# AVANCEMENT.md — Graph Analytics 2026 | Fish Schooling Networks

> **Dernière mise à jour :** 31 octobre 2026  
> **Version :** 2.0  
> **Statut :** cadrage documentaire établi ; **aucune analyse sur les fichiers bruts n'est encore vérifiée dans le dépôt du projet**.  
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
- [!] Fichier de données réellement disponible et inspecté : **non confirmé**.
- [!] Template du rapport sur **Inside** : non fourni ici.
- [x] Dépôt GitHub dédié : https://github.com/Charles-Scannavino/Projet_Graph_Analytics.
- [ ] Unités, continuité de suivi, sélection de frames et seuil `R` : à définir.
- [ ] Code d'analyse, résultats chiffrés et figures calculées : non validés.
- [ ] Rapport PDF final, README reproductible et slides : à produire.

## 2. Tableau de conformité à l'énoncé officiel

| Exigence | État actuel | Preuve attendue | Priorité |
|---|---|---|---|
| Groupe de exactement 2 étudiants | [!] | Deux noms et répartition orale | P0 |
| Dataset : origine et intérêt | [ ] | Référence, licence, fichier accessible et audité | P0 |
| Attribution du code effectivement utilisé | [ ] | Provenance du code incorporé, auteurs et URLs le cas échéant | P0 |
| Problématique explicite | [x] Formulation candidate | Question finalisée dans le rapport | P0 |
| Définition des nœuds et des arêtes | [ ] | Modèle et construction reproductibles | P0 |
| Graphe orienté/non orienté et simple/multigraphe | [ ] | Choix justifié | P0 |
| Attributs et poids | [ ] | Champs et unités documentés | P0 |
| Nombre de nœuds `N` et d'arêtes `M` | [ ] | Chiffres calculés | P0 |
| Connectivité et composantes | [ ] | Calcul et interprétation des composantes | P0 |
| **Diamètre** | [!] | Valeur + convention + méthode | P0 |
| **Rayon** | [!] | Valeur + convention + méthode | P0 |
| Centralités et interprétation | [ ] | Scores, définitions et lecture scientifique | P0 |
| Communautés et interprétation | [ ] | Algorithme, paramètres, partition et discussion | P0 |
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
- [ ] Accéder au jeu *Fish Schooling Data Subset* et conserver les fichiers sources non modifiés.
- [ ] Contrôler URL/DOI, auteur/institution, licence et date d'accès.
- [ ] Analyser la structure des frames, les variables `px`, `py`, `vx`, `vy`, `onfish`.
- [ ] Vérifier doublons, valeurs manquantes, individus visibles, unités et cohérence des vitesses.
- [ ] Identifier les limites du suivi individuel et du découpage temporel.
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
- [ ] Le dataset Oregon State est-il disponible sous forme exploitable ?
- [ ] Quel est le nombre d'observations par frame et comment se comportent les identifiants ?
- [ ] Quelles sont les unités et quel seuil `R` est justifié ?
- [ ] Quelles frames seront retenues ?
- [ ] Quel algorithme de communautés et quelles centralités sont finalement choisis ?
- [ ] Le modèle de rapport Inside est-il disponible ?
- [x] URL du dépôt GitHub : https://github.com/Charles-Scannavino/Projet_Graph_Analytics
- [ ] Quels codes préexistants et outils d'IA ont effectivement contribué au rendu ?

## 7. Risques et stratégies de réponse

| Risque | Importance | Action |
|---|---|---|
| Dataset indisponible | Critique | Vérifier les accès ; étudier le jeu alternatif 2D avant d'avancer |
| Unités ou seuil de voisinage non maîtrisés | Élevée | Audit des unités, justification de `R`, robustesse |
| Oubli du diamètre ou du rayon | Critique | Checklist P0, calcul explicite et convention des composantes |
| Mauvaise gestion de la déconnexion | Élevée | Métriques sur LCC ou par composante, description du choix |
| Analyse insuffisamment interprétée | Élevée | Formuler une question, discuter le sens des métriques et leurs limites |
| Absence de deuxième membre | Critique | Définir le binôme et partager la soutenance |
| Mauvais modèle/rapport trop long | Critique | Télécharger template Inside, vérifier ≤15 pages |
| Sources ou code non attribués | Critique | Conserver un registre de provenance et citer précisément |
| Dépôt non reproductible | Élevée | README, versions, test d'installation propre |
| Extensions chronophages | Élevée | Reporter 3D, Neo4j, simulateur et LLM tant que P0 n'est pas terminé |

## 8. Journal de projet

### 31 octobre 2026 — Documentation scientifique et planification

- [x] Exigences de l'énoncé transcrites et classées par priorité.
- [x] Définition de la problématique candidate et du modèle de graphe envisagé.
- [x] Décomposition des étapes de travail jusqu'à la remise officielle.
- [x] Préparation des documents `CONTEXT.md` et `AVANCEMENT.md`.
- [ ] Validation du dataset et des métriques sur une exécution réelle.
- [x] Mise en ligne des documents dans le dépôt GitHub dédié.

**Prochaine action :** vérifier et charger le dataset pour calculer les indicateurs obligatoires.

---

*Mettre à jour ce journal après toute étape effectivement vérifiée, en consignant les fichiers, commandes, résultats, obstacles et décisions.*