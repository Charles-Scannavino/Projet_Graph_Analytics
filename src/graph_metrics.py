from pathlib import Path
import json
import time

import networkx as nx

from src.data_loader import load_frame
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph


def top_scores(scores, n=5):
    """Classement des n poissons ayant les scores les plus élevés."""
    ordered = sorted(
        scores.items(),
        key=lambda pair: (-pair[1], str(pair[0]))
    )

    return [
        {
            "fish_id": str(node),
            "score": round(float(value), 5)
        }
        for node, value in ordered[:n]
    ]


def analyze_graph(G):
    """Calcule les métriques structurelles d'un graphe NetworkX."""

    count = G.number_of_nodes()

    if count == 0:
        raise ValueError("Impossible d'analyser un graphe vide.")

    directed = G.is_directed()
    links = G.number_of_edges()

    # Composantes faibles ou connexes selon le type de graphe
    if directed:
        weak = list(nx.weakly_connected_components(G))
        strong = list(nx.strongly_connected_components(G))
        selected = strong
    else:
        weak = list(nx.connected_components(G))
        strong = None
        selected = weak

    # Diamètre et rayon sur la plus grande composante adaptée
    largest = max(selected, key=len)
    core = G.subgraph(largest)

    # Centralités non pondérées
    betweenness = nx.betweenness_centrality(
        G, weight=None, normalized=True
    )

    degree_centrality = (
        nx.out_degree_centrality(G)
        if directed
        else nx.degree_centrality(G)
    )

    result = {
        "graph_type": "directed" if directed else "undirected",
        "nodes": count,
        "arcs" if directed else "edges": links,
        "weak_components" if directed else "connected_components": len(weak),
        "largest_component_size": len(largest),
        "largest_component_share": round(len(largest) / count, 4),
        "diameter_largest_component_hops": nx.diameter(core),
        "radius_largest_component_hops": nx.radius(core),
        "density": round(nx.density(G), 5),
        "average_clustering": round(nx.average_clustering(G), 5),
        "top_betweenness": top_scores(betweenness),
    }

    if directed:
        result.update({
            "strong_components": len(strong),
            "largest_weak_component_size": max(map(len, weak)),
            "average_in_degree": round(links / count, 4),
            "average_out_degree": round(links / count, 4),
            "top_out_degree_centrality": top_scores(degree_centrality),
            "top_in_degree_centrality": top_scores(
                nx.in_degree_centrality(G)
            ),
        })
    else:
        result.update({
            "average_degree": round(2 * links / count, 4),
            "top_degree_centrality": top_scores(degree_centrality),
        })

    return result


def print_report(label, metrics):
    """Affiche toutes les métriques obtenues dans le Terminal."""
    print(f"\n=== {label} ===", flush=True)

    for name, value in metrics.items():
        print(f"{name}: {value}", flush=True)


if __name__ == "__main__":
    start = time.perf_counter()

    root = Path(__file__).resolve().parents[1]
    dataset = root / "data" / "schooling_frames.json"
    output = root / "results" / "metrics_frame1_R100.json"

    print("[1/6] Chargement de la frame 1...", flush=True)
    frame = load_frame(dataset, frame_id=1)
    print(f"      {len(frame['onfish'])} poissons chargés.", flush=True)

    print("[2/6] Construction du graphe spatial R=100...", flush=True)
    spatial = build_graph(frame, radius=100)
    print(f"      {spatial.number_of_edges()} arêtes.", flush=True)

    print("[3/6] Construction du graphe de visibilité à 25°...", flush=True)
    visibility = build_visibility_graph(
        frame,
        radius=100,
        rear_blind_angle_deg=25
    )
    print(f"      {visibility.number_of_edges()} arcs.", flush=True)

    print("[4/6] Calcul des métriques spatiales...", flush=True)
    spatial_metrics = analyze_graph(spatial)
    print_report("GRAPHE SPATIAL", spatial_metrics)

    print("[5/6] Calcul des métriques de visibilité...", flush=True)
    visibility_metrics = analyze_graph(visibility)
    print_report("GRAPHE DE VISIBILITÉ", visibility_metrics)

    print("[6/6] Sauvegarde des résultats...", flush=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    results = {
        "frame_id": 1,
        "radius": 100,
        "rear_blind_angle_deg": 25,
        "spatial": spatial_metrics,
        "visibility": visibility_metrics,
    }

    output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"      Fichier : {output}", flush=True)
    print(
        f"\nAnalyse terminée en {time.perf_counter() - start:.2f} s.",
        flush=True
    )
