"""Comparaison de graphes sur une cohorte fixe observée pendant 32 frames.

Pilote exploratoire, R=100, angle mort arriere TOTAL=25 degres.
Les directions reelles sont calculees a rebours (position_t-position_t-1),
pour eviter la fuite d'information liee aux vx/vy prospectifs du dataset.
"""
from pathlib import Path
import json
import time

import networkx as nx
import numpy as np

from src.boids_pilot import (
    BoidsParameters,
    DATASET,
    initial_state,
    load_observations,
    positions_from_frame,
    step_boids,
    step_persistence,
)
from src.community_detection import detect_communities
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/simulation/graph_comparison_h30_R100.json"
CHECKPOINTS = (1, 5, 10, 20, 30)


def make_frame(ids, positions, velocity):
    return {
        "onfish": ids.copy(),
        "px": positions[:, 0].copy(),
        "py": positions[:, 1].copy(),
        "vx": velocity[:, 0].copy(),
        "vy": velocity[:, 1].copy(),
    }


def edge_signature(graph):
    if graph.is_directed():
        return set(graph.edges())
    return {frozenset(pair) for pair in graph.edges()}


def edge_jaccard(actual, candidate):
    left, right = edge_signature(actual), edge_signature(candidate)
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def network_summary(graph):
    n = graph.number_of_nodes()
    if n < 1:
        raise ValueError("Un graphe ne peut pas etre vide.")
    components = (
        nx.strongly_connected_components(graph)
        if graph.is_directed()
        else nx.connected_components(graph)
    )
    largest = max((len(c) for c in components), default=0)
    comm = detect_communities(graph, seed=42)
    return {
        "nodes": n,
        "links": graph.number_of_edges(),
        "density": round(float(nx.density(graph)), 5),
        "average_degree": round(
            (1 if graph.is_directed() else 2)
            * graph.number_of_edges() / n, 5
        ),
        "clustering": round(float(nx.average_clustering(graph)), 5),
        "largest_component_share": round(largest / n, 5),
        "communities": comm["number_of_communities"],
        "modularity": comm["modularity"],
    }


def position_mapping(frame):
    ids, xy = positions_from_frame(frame)
    return {int(i): p for i, p in zip(ids, xy)}


def compare_graphs(
    dataset=DATASET,
    output=OUTPUT,
    horizon=30,
    radius=100,
    parameters=BoidsParameters(),
    frames=None,
):
    if horizon < 1:
        raise ValueError("Horizon invalide.")
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("Rayon invalide.")
    parameters.validate()
    if frames is None:
        frames = load_observations(dataset, horizon)
    if set(frames) != set(range(1, horizon + 3)):
        raise ValueError("Frames incompletes.")

    all_ids, all_pos, all_vel = initial_state(frames[1], frames[2])
    common_ids = set(map(int, all_ids))
    for frame_id in range(3, horizon + 3):
        ids, _ = positions_from_frame(frames[frame_id])
        common_ids.intersection_update(map(int, ids))
    if not common_ids:
        raise ValueError("Aucune trajectoire continue.")

    indices = np.array([
        k for k, fish_id in enumerate(all_ids)
        if int(fish_id) in common_ids
    ], dtype=int)
    ids = all_ids[indices]
    pos_b = all_pos[indices].copy()
    vel_b = all_vel[indices].copy()
    pos_i, vel_i = pos_b.copy(), vel_b.copy()
    print(
        f"[COHORTE] {len(ids)} poissons suivis de la frame 1 "
        f"a la frame {horizon + 2}; R={radius}; angle mort=25 degres",
        flush=True,
    )

    checkpoints = sorted(set(CHECKPOINTS) & set(range(1, horizon + 1)))
    if horizon not in checkpoints:
        checkpoints.append(horizon)
    rows = []
    for h in range(1, horizon + 1):
        frame_id = h + 2
        pos_b, vel_b = step_boids(pos_b, vel_b, parameters)
        pos_i, vel_i = step_persistence(pos_i, vel_i)
        if h not in checkpoints:
            continue

        current = position_mapping(frames[frame_id])
        previous = position_mapping(frames[frame_id - 1])
        real_pos = np.array([current[int(fish_id)] for fish_id in ids])
        real_prev = np.array([previous[int(fish_id)] for fish_id in ids])
        real_vel = real_pos - real_prev
        snapshots = {
            "real": make_frame(ids, real_pos, real_vel),
            "boids": make_frame(ids, pos_b, vel_b),
            "inertia": make_frame(ids, pos_i, vel_i),
        }
        errors = {
            "real": 0.0,
            "boids": float(np.linalg.norm(pos_b - real_pos, axis=1).mean()),
            "inertia": float(np.linalg.norm(pos_i - real_pos, axis=1).mean()),
        }
        for graph_type in ("spatial", "visibility"):
            graphs = {}
            for model, snap in snapshots.items():
                if graph_type == "spatial":
                    graphs[model] = build_graph(snap, radius=radius)
                else:
                    graphs[model] = build_visibility_graph(
                        snap, radius=radius, rear_blind_angle_deg=25
                    )
            for model, graph in graphs.items():
                row = {
                    "horizon_frames": h,
                    "frame_id": frame_id,
                    "graph_type": graph_type,
                    "model": model,
                    **network_summary(graph),
                    "edge_jaccard_vs_real": round(
                        edge_jaccard(graphs["real"], graph), 5
                    ),
                    "mean_position_error": round(errors[model], 5),
                }
                rows.append(row)
                print(
                    f"[FRAME {frame_id:>2}] {graph_type:<10} "
                    f"{model:<7} densite={row['density']:.4f} "
                    f"clustering={row['clustering']:.4f} "
                    f"Jaccard={row['edge_jaccard_vs_real']:.4f}",
                    flush=True,
                )

    result = {
        "method": {
            "horizon": horizon,
            "radius": radius,
            "rear_blind_angle_total_deg": 25,
            "cohort_size": len(ids),
            "cohort_selection": "present_at_every_frame_1_to_horizon_plus_2",
            "init_velocity": "position_2_minus_position_1",
            "real_direction_for_visibility": "position_t_minus_position_t_minus_1",
            "boids_parameters": {
                "radius_separation": parameters.radius_separation,
                "radius_alignment": parameters.radius_alignment,
                "radius_cohesion": parameters.radius_cohesion,
                "rear_blind_angle_deg": parameters.rear_blind_angle_deg,
                "weight_separation": parameters.weight_separation,
                "weight_alignment": parameters.weight_alignment,
                "weight_cohesion": parameters.weight_cohesion,
            },
            "boundary_handling": "none",
            "limitation": "fixed survivor cohort conditional on future tracking",
        },
        "results": rows,
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] {len(rows)} lignes exportees : {output}", flush=True)
    return result


if __name__ == "__main__":
    tic = time.perf_counter()
    compare_graphs()
    print(f"[TERMINE] {time.perf_counter() - tic:.2f} s", flush=True)
