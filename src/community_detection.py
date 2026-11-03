from pathlib import Path
import json
import time

import networkx as nx

from src.data_loader import load_frame
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph


def detect_communities(G, seed=42, resolution=1.0):
    """Détecte les communautés Louvain d'un graphe NetworkX."""

    if G.number_of_nodes() == 0:
        raise ValueError("Impossible d'analyser un graphe vide.")

    if G.number_of_edges() == 0:
        groups = [{node} for node in G.nodes()]
        modularity = None
    else:
        groups = nx.community.louvain_communities(
            G,
            seed=seed,
            resolution=resolution,
            weight=None,
        )

        modularity = nx.community.modularity(
            G,
            groups,
            resolution=resolution,
            weight=None,
        )

    # Ordre déterministe des communautés
    groups = sorted(
        groups,
        key=lambda group: (-len(group), min(group))
    )

    membership = {
        str(node): community_id
        for community_id, group in enumerate(groups, start=1)
        for node in group
    }

    return {
        "graph_type": "directed" if G.is_directed() else "undirected",
        "seed": seed,
        "resolution": resolution,
        "weight": None,
        "number_of_communities": len(groups),
        "community_sizes": [len(group) for group in groups],
        "modularity": (
            round(float(modularity), 5)
            if modularity is not None else None
        ),
        "membership": membership,
    }


if __name__ == "__main__":
    start = time.perf_counter()

    root = Path(__file__).resolve().parents[1]
    dataset = root / "data" / "schooling_frames.json"
    output = root / "results" / "communities_frame1_R100.json"

    print("[1/6] Chargement des données expérimentales...", flush=True)
    frame = load_frame(dataset, frame_id=1)
    print(f"      {len(frame['onfish'])} poissons.", flush=True)

    print("[2/6] Construction du graphe spatial...", flush=True)
    spatial = build_graph(frame, radius=100)
    print(f"      {spatial.number_of_edges()} arêtes.", flush=True)

    print("[3/6] Construction du graphe de visibilité...", flush=True)
    visibility = build_visibility_graph(
        frame,
        radius=100,
        rear_blind_angle_deg=25,
    )
    print(f"      {visibility.number_of_edges()} arcs.", flush=True)

    print("[4/6] Louvain sur le graphe spatial...", flush=True)
    spatial_results = detect_communities(spatial)

    print("[5/6] Louvain sur le graphe de visibilité...", flush=True)
    visibility_results = detect_communities(visibility)

    for name, results in [
        ("SPATIAL", spatial_results),
        ("VISIBILITÉ 25°", visibility_results),
    ]:
        print(f"\n=== COMMUNAUTÉS {name} ===", flush=True)
        print(
            "Nombre de communautés :",
            results["number_of_communities"],
            flush=True,
        )
        print("Modularité :", results["modularity"], flush=True)
        print("Tailles :", results["community_sizes"], flush=True)

    print("\n[6/6] Sauvegarde des résultats...", flush=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(
            {
                "frame_id": 1,
                "radius": 100,
                "rear_blind_angle_deg": 25,
                "spatial": spatial_results,
                "visibility": visibility_results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"      Fichier : {output}", flush=True)
    print(
        f"[OK] Analyse terminée en "
        f"{time.perf_counter() - start:.2f} s.",
        flush=True,
    )
