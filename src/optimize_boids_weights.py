"""Optimisation des trois coefficients Boids sur les frames 1-32."""

from dataclasses import replace
from itertools import product
from pathlib import Path
import csv
import json
import time

from src.boids_pilot import BoidsParameters
from src.calibrate_boids import (
    prepare_training_data,
    evaluate_candidate,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "simulation"

SEPARATION = (0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1)
ALIGNMENT = (0.0, 0.001, 0.005, 0.01, 0.05, 0.075, 0.15, 0.3)
COHESION = (0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1)


def main():
    start = time.perf_counter()

    print("=== OPTIMISATION BOIDS ===", flush=True)
    print("Entrainement : frames 1-32 uniquement", flush=True)

    ids, pos, velocity, truth, real_graphs = prepare_training_data(ROOT / "data/local/schooling_frames.json")

    combinations = list(product(
        SEPARATION, ALIGNMENT, COHESION
    ))

    print(f"Poissons suivis : {len(ids)}", flush=True)
    print(f"Configurations : {len(combinations)}", flush=True)

    results = []
    defaults = BoidsParameters()

    for index, (sep, align, coh) in enumerate(combinations, 1):
        params = replace(
            defaults,
            weight_separation=sep,
            weight_alignment=align,
            weight_cohesion=coh,
        )

        result = evaluate_candidate(
            ids, pos, velocity, truth, real_graphs, params
        )

        results.append(result)

        print(
            f"[{index:03d}/{len(combinations)}] "
            f"S={sep:.3f} A={align:.3f} C={coh:.3f} "
            f"| Jaccard={result['mean_spatial_jaccard']:.5f} "
            f"| Erreur H30={result['position_error_h30']:.3f}",
            flush=True,
        )

    by_jaccard = sorted(
        results,
        key=lambda r: (
            -r["mean_spatial_jaccard"],
            r["position_error_h30"],
        ),
    )

    by_position = sorted(
        results,
        key=lambda r: (
            r["position_error_h30"],
            -r["mean_spatial_jaccard"],
        ),
    )

    previous = next(
        r for r in results
        if (
            r["weight_separation"],
            r["weight_alignment"],
            r["weight_cohesion"],
        ) == (0.0, 0.15, 0.0)
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT / "boids_weights_optimization_train.csv"
    json_path = OUTPUT / "boids_weights_optimization_train.json"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(results[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(by_jaccard)

    summary = {
        "training_window": [1, 32],
        "training_cohort_size": len(ids),
        "checkpoints": [5, 10, 20, 30],
        "spatial_radius": 100,
        "number_of_candidates": len(results),
        "search_space": {
            "separation": SEPARATION,
            "alignment": ALIGNMENT,
            "cohesion": COHESION,
        },
        "previous_calibration": previous,
        "best_spatial_jaccard": by_jaccard[0],
        "best_position_error_h30": by_position[0],
        "top_10_jaccard": by_jaccard[:10],
        "top_10_position": by_position[:10],
        "validation_windows_not_used": [
            [2000, 2031],
            [4000, 4031],
        ],
    }

    json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    for label, result in (
        ("ANCIENNE CALIBRATION", previous),
        ("MEILLEUR JACCARD", by_jaccard[0]),
        ("MEILLEURE POSITION H30", by_position[0]),
    ):
        print(f"\n=== {label} ===")
        print(
            "Séparation =", result["weight_separation"],
            "| Alignement =", result["weight_alignment"],
            "| Cohésion =", result["weight_cohesion"],
        )
        print("Jaccard moyen :", result["mean_spatial_jaccard"])
        print("Erreur position H30 :", result["position_error_h30"])

    print("\nCSV :", csv_path)
    print("JSON :", json_path)
    print(f"Temps total : {time.perf_counter() - start:.1f} s")


if __name__ == "__main__":
    main()
