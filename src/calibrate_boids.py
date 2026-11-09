"""Calibration exploratoire Boids sur la seule fenêtre 1–32.

Objectif : maximiser le Jaccard spatial moyen à
5, 10, 20 et 30 frames.

Les fenêtres 2000–2031 et 4000–4031 ne sont pas utilisées.
"""

from dataclasses import asdict, replace
from itertools import product
from pathlib import Path
import csv
import json
import time

import numpy as np

from src.boids_pilot import (
    BoidsParameters,
    DATASET,
    initial_state,
    load_observations,
    positions_from_frame,
    step_boids,
)
from src.compare_boids_graphs import edge_jaccard
from src.graph_builder import build_graph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "results" / "simulation"

HORIZON = 30
RADIUS = 100
CHECKPOINTS = (5, 10, 20, 30)

SEPARATION_WEIGHTS = (0.0, 0.25, 0.5)
ALIGNMENT_WEIGHTS = (0.0, 0.15, 0.3)
COHESION_WEIGHTS = (0.0, 0.1, 0.2)


def make_spatial_graph(ids, positions):
    return build_graph(
        {
            "onfish": ids,
            "px": positions[:, 0],
            "py": positions[:, 1],
            "vx": np.zeros(len(ids)),
            "vy": np.zeros(len(ids)),
        },
        radius=RADIUS,
    )


def prepare_training_data(dataset=DATASET):
    frames = load_observations(dataset, HORIZON)

    initial_ids, initial_pos, initial_v = initial_state(
        frames[1], frames[2]
    )

    survivors = set(map(int, initial_ids))
    mappings = {}

    for frame_id in range(3, HORIZON + 3):
        ids, pos = positions_from_frame(frames[frame_id])

        mapping = {
            int(i): p for i, p in zip(ids, pos)
        }

        mappings[frame_id] = mapping
        survivors.intersection_update(mapping)

    indices = np.array([
        k for k, fish_id in enumerate(initial_ids)
        if int(fish_id) in survivors
    ], dtype=int)

    if not len(indices):
        raise ValueError("Aucune trajectoire continue.")

    ids = initial_ids[indices]
    pos = initial_pos[indices]
    velocity = initial_v[indices]

    truth = {}
    real_graphs = {}

    for horizon in CHECKPOINTS:
        frame_id = horizon + 2

        actual = np.array([
            mappings[frame_id][int(i)]
            for i in ids
        ])

        truth[horizon] = actual
        real_graphs[horizon] = make_spatial_graph(
            ids, actual
        )

    return ids, pos, velocity, truth, real_graphs


def evaluate_candidate(
    ids,
    initial_pos,
    initial_velocity,
    truth,
    real_graphs,
    params,
):
    pos = initial_pos.copy()
    velocity = initial_velocity.copy()

    jaccards = {}
    errors = {}

    for horizon in range(1, HORIZON + 1):
        pos, velocity = step_boids(
            pos, velocity, params
        )

        if horizon not in CHECKPOINTS:
            continue

        simulated_graph = make_spatial_graph(ids, pos)

        jaccards[horizon] = edge_jaccard(
            real_graphs[horizon],
            simulated_graph,
        )

        errors[horizon] = float(np.mean(
            np.linalg.norm(
                pos - truth[horizon], axis=1
            )
        ))

    return {
        "weight_separation": params.weight_separation,
        "weight_alignment": params.weight_alignment,
        "weight_cohesion": params.weight_cohesion,
        "mean_spatial_jaccard": round(
            float(np.mean(list(jaccards.values()))), 6
        ),
        "position_error_h30": round(
            errors[30], 6
        ),
        **{
            f"jaccard_h{h}": round(jaccards[h], 6)
            for h in CHECKPOINTS
        },
    }


def main():
    start = time.perf_counter()

    print(
        "=== CALIBRATION BOIDS : ENTRAÎNEMENT UNIQUEMENT ===",
        flush=True,
    )

    print(
        "[1/3] Préparation de la cohorte...",
        flush=True,
    )

    ids, pos, velocity, truth, real_graphs = (
        prepare_training_data()
    )

    print(
        f"[OK] {len(ids)} poissons suivis | "
        f"Frames 1–32 | R={RADIUS}",
        flush=True,
    )

    default = BoidsParameters()
    combinations = list(product(
        SEPARATION_WEIGHTS,
        ALIGNMENT_WEIGHTS,
        COHESION_WEIGHTS,
    ))

    print(
        f"[2/3] Évaluation de "
        f"{len(combinations)} configurations...",
        flush=True,
    )

    results = []

    for index, (sep, align, coh) in enumerate(
        combinations, start=1
    ):
        params = replace(
            default,
            weight_separation=sep,
            weight_alignment=align,
            weight_cohesion=coh,
        )

        result = evaluate_candidate(
            ids,
            pos,
            velocity,
            truth,
            real_graphs,
            params,
        )

        results.append(result)

        print(
            f"[{index:02}/{len(combinations)}] "
            f"S={sep:.2f} A={align:.2f} C={coh:.2f} "
            f"| Jaccard={result['mean_spatial_jaccard']:.5f} "
            f"| Erreur H30={result['position_error_h30']:.3f}",
            flush=True,
        )

    results.sort(
        key=lambda r: (
            -r["mean_spatial_jaccard"],
            r["position_error_h30"],
            (
                r["weight_separation"]
                + r["weight_alignment"]
                + r["weight_cohesion"]
            ),
        )
    )

    best = results[0]

    baseline = next(
        r for r in results
        if (
            r["weight_separation"],
            r["weight_alignment"],
            r["weight_cohesion"],
        ) == (0.0, 0.0, 0.0)
    )

    original = next(
        r for r in results
        if (
            r["weight_separation"],
            r["weight_alignment"],
            r["weight_cohesion"],
        ) == (0.5, 0.3, 0.2)
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        OUTPUT_DIR / "boids_calibration_train_R100.csv"
    )
    json_path = (
        OUTPUT_DIR / "boids_calibration_train_R100.json"
    )

    with csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(results[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "training_window": [1, 32],
        "training_cohort_size": len(ids),
        "checkpoints": list(CHECKPOINTS),
        "radius": RADIUS,
        "rear_blind_angle_total_deg": 25,
        "selection_objective": (
            "maximize_mean_spatial_edge_jaccard"
        ),
        "validation_windows_not_used": [
            [2000, 2031],
            [4000, 4031],
        ],
        "best": best,
        "inertial_baseline": baseline,
        "original_boids": original,
        "all_candidates": results,
    }

    json_path.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("\n[3/3] SYNTHÈSE", flush=True)

    for name, row in (
        ("MEILLEURE CONFIGURATION", best),
        ("INERTIE", baseline),
        ("BOIDS INITIAL", original),
    ):
        print(f"\n{name}")
        print(
            "Coefficients :",
            row["weight_separation"],
            row["weight_alignment"],
            row["weight_cohesion"],
        )
        print(
            "Jaccard moyen :",
            row["mean_spatial_jaccard"],
        )
        print(
            "Erreur position H30 :",
            row["position_error_h30"],
        )

    print(
        f"\n[OK] CSV : {csv_path}",
        flush=True,
    )
    print(
        f"[OK] JSON : {json_path}",
        flush=True,
    )
    print(
        f"[TERMINÉ] {time.perf_counter() - start:.2f} s",
        flush=True,
    )


if __name__ == "__main__":
    main()
