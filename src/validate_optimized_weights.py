"""Validation indépendante des coefficients Boids optimisés."""

from dataclasses import replace
from pathlib import Path
import csv

import numpy as np

from src.boids_pilot import (
    BoidsParameters,
    initial_state,
    positions_from_frame,
    step_boids,
    step_persistence,
)
from src.calibrate_boids import (
    CHECKPOINTS,
    make_spatial_graph,
)
from src.compare_boids_graphs import edge_jaccard
from src.validate_boids_windows import load_windows


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/local/schooling_frames.json"
OUTPUT = ROOT / "results/simulation/boids_validation_optimized.csv"

CONFIGS = {
    "inertia": None,
    "ancienne": (0.0, 0.15, 0.0),
    "jaccard": (0.005, 0.05, 0.005),
    "position_h30": (0.025, 0.3, 0.01),
}


def prepare_window(frames):
    ids, positions, velocities = initial_state(
        frames[1], frames[2]
    )

    mappings = {}

    for t in range(1, 33):
        frame_ids, xy = positions_from_frame(frames[t])
        mappings[t] = {
            int(i): p for i, p in zip(frame_ids, xy)
        }

    survivors = set(map(int, ids))

    for mapping in mappings.values():
        survivors.intersection_update(mapping)

    indices = np.array([
        k for k, fish_id in enumerate(ids)
        if int(fish_id) in survivors
    ], dtype=int)

    ids = ids[indices]
    positions = positions[indices]
    velocities = velocities[indices]

    truth = {
        h: np.array([
            mappings[h + 2][int(i)] for i in ids
        ])
        for h in CHECKPOINTS
    }

    real_graphs = {
        h: make_spatial_graph(ids, truth[h])
        for h in CHECKPOINTS
    }

    return ids, positions, velocities, truth, real_graphs


def evaluate(start, frames):
    ids, initial_pos, initial_vel, truth, graphs = (
        prepare_window(frames)
    )

    rows = []

    for name, weights in CONFIGS.items():
        pos = initial_pos.copy()
        vel = initial_vel.copy()

        params = (
            None if weights is None else replace(
                BoidsParameters(),
                weight_separation=weights[0],
                weight_alignment=weights[1],
                weight_cohesion=weights[2],
            )
        )

        for h in range(1, 31):
            if params is None:
                pos, vel = step_persistence(pos, vel)
            else:
                pos, vel = step_boids(pos, vel, params)

            if h not in CHECKPOINTS:
                continue

            predicted_graph = make_spatial_graph(ids, pos)

            jaccard = edge_jaccard(
                graphs[h], predicted_graph
            )

            error = float(np.mean(
                np.linalg.norm(pos - truth[h], axis=1)
            ))

            rows.append({
                "window_start": start,
                "model": name,
                "horizon": h,
                "cohort_size": len(ids),
                "spatial_jaccard": round(jaccard, 6),
                "position_error": round(error, 6),
            })

    return rows


def main():
    if not DATASET.is_file():
        raise FileNotFoundError(DATASET)

    windows = load_windows(
        dataset=DATASET,
        starts=(2000, 4000),
        horizon=30,
    )

    rows = []

    for start, frames in sorted(windows.items()):
        rows.extend(evaluate(start, frames))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print("\n=== VALIDATION INDÉPENDANTE ===")

    for name in CONFIGS:
        selected = [r for r in rows if r["model"] == name]
        h30 = [r for r in selected if r["horizon"] == 30]

        print(
            f"{name:14} | "
            f"Jaccard moyen="
            f"{np.mean([r['spatial_jaccard'] for r in selected]):.6f} "
            f"| Erreur H30="
            f"{np.mean([r['position_error'] for r in h30]):.6f}"
        )

    print(f"\n[OK] Résultats : {OUTPUT}")


if __name__ == "__main__":
    main()
