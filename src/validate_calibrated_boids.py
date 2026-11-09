"""Validation hors entraînement du modèle Boids calibré.

Entraînement : frames 1-32 uniquement.
Validation : frames 2000-2031 et 4000-4031.
Les coefficients sont lus et figés avant la validation.
"""

from dataclasses import replace
from pathlib import Path
from statistics import mean
import csv
import json
import time

from src.boids_pilot import BoidsParameters
from src.compare_boids_graphs import compare_graphs
from src.validate_boids_windows import load_windows


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "results" / "simulation"

TRAINING = DIRECTORY / "boids_calibration_train_R100.json"
OUTPUT_CSV = DIRECTORY / "boids_holdout_validation.csv"
OUTPUT_JSON = DIRECTORY / "boids_holdout_validation.json"

WINDOWS = (2000, 4000)
HORIZONS = (5, 10, 20, 30)
GRAPH_TYPES = ("spatial", "visibility")


def find_row(data, horizon, graph_type, model):
    matches = [
        row for row in data["results"]
        if row["horizon_frames"] == horizon
        and row["graph_type"] == graph_type
        and row["model"] == model
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Résultat absent ou dupliqué : "
            f"{horizon}, {graph_type}, {model}"
        )

    return matches[0]


def evaluate_model(data, model, graph_type):
    samples = [
        find_row(data, h, graph_type, model)
        for h in HORIZONS
    ]

    final = samples[-1]

    real_final = find_row(
        data, 30, graph_type, "real"
    )

    def difference(key):
        a = final[key]
        b = real_final[key]

        if a is None or b is None:
            return None

        return round(abs(a - b), 6)

    return {
        "model": model,
        "graph_type": graph_type,
        "mean_jaccard": round(mean(
            r["edge_jaccard_vs_real"]
            for r in samples
        ), 6),
        "jaccard_h30": final[
            "edge_jaccard_vs_real"
        ],
        "position_error_h30": final[
            "mean_position_error"
        ],
        "modularity_error_h30": difference(
            "modularity"
        ),
        "clustering_error_h30": difference(
            "clustering"
        ),
        "community_count_error_h30": abs(
            final["communities"]
            - real_final["communities"]
        ),
    }


def validate_baseline_consistency(old, calibrated):
    if (
        old["method"]["cohort_size"]
        != calibrated["method"]["cohort_size"]
    ):
        raise ValueError(
            "Les cohortes de validation diffèrent."
        )

    for graph_type in GRAPH_TYPES:
        for horizon in (1, 5, 10, 20, 30):
            for model in ("real", "inertia"):
                a = find_row(
                    old, horizon, graph_type, model
                )

                b = find_row(
                    calibrated, horizon, graph_type, model
                )

                for key in (
                    "nodes",
                    "links",
                    "density",
                    "edge_jaccard_vs_real",
                    "mean_position_error",
                ):
                    if a[key] != b[key]:
                        raise ValueError(
                            f"Baseline différente : "
                            f"{graph_type}, {horizon}, "
                            f"{model}, {key}"
                        )


def main():
    tic = time.perf_counter()

    print(
        "=== VALIDATION BOIDS HORS ENTRAÎNEMENT ===",
        flush=True,
    )

    training = json.loads(
        TRAINING.read_text(encoding="utf-8")
    )

    best = training["best"]

    params = replace(
        BoidsParameters(),
        weight_separation=best[
            "weight_separation"
        ],
        weight_alignment=best[
            "weight_alignment"
        ],
        weight_cohesion=best[
            "weight_cohesion"
        ],
    )

    print("\nPARAMÈTRES FIGÉS")
    print("Séparation :", params.weight_separation)
    print("Alignement :", params.weight_alignment)
    print("Cohésion :", params.weight_cohesion)
    print("Angle mort :", params.rear_blind_angle_deg)
    print("Rayon graphe : 100")

    print(
        "\n[1/3] Chargement des fenêtres...",
        flush=True,
    )

    windows = load_windows(
        starts=WINDOWS,
        horizon=30,
    )

    records = []

    print(
        "\n[2/3] Validation sans recalibration...",
        flush=True,
    )

    for start in WINDOWS:
        original_path = DIRECTORY / (
            f"graph_comparison_start{start}"
            f"_h30_R100.json"
        )

        original = json.loads(
            original_path.read_text(encoding="utf-8")
        )

        calibrated_path = DIRECTORY / (
            f"graph_comparison_calibrated_start{start}"
            f"_h30_R100.json"
        )

        calibrated = compare_graphs(
            frames=windows[start],
            horizon=30,
            radius=100,
            parameters=params,
            output=calibrated_path,
        )

        validate_baseline_consistency(
            original, calibrated
        )

        for graph_type in GRAPH_TYPES:
            for name, data, key in (
                ("inertia", original, "inertia"),
                ("original_boids", original, "boids"),
                ("calibrated_boids", calibrated, "boids"),
            ):
                row = evaluate_model(
                    data, key, graph_type
                )

                row["window"] = (
                    f"{start}-{start + 31}"
                )

                row["cohort_size"] = (
                    calibrated["method"]["cohort_size"]
                )

                row["model"] = name
                records.append(row)

    print("\n[3/3] RÉSULTATS DE VALIDATION")

    for start in WINDOWS:
        print(f"\n=== FENÊTRE {start} ===")

        for graph_type in GRAPH_TYPES:
            print(f"\n{graph_type.upper()}")

            selected = [
                row for row in records
                if row["window"].startswith(
                    str(start) + "-"
                )
                and row["graph_type"] == graph_type
            ]

            for row in selected:
                print(
                    f"{row['model']:17} "
                    f"| Jaccard moyen="
                    f"{row['mean_jaccard']:.6f} "
                    f"| Jaccard H30="
                    f"{row['jaccard_h30']:.5f} "
                    f"| Position H30="
                    f"{row['position_error_h30']:.3f} "
                    f"| Écart modularité H30="
                    f"{row['modularity_error_h30']}"
                )

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(records[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)

    summary = {
        "training_window": [1, 32],
        "validation_windows": [
            [2000, 2031],
            [4000, 4031],
        ],
        "selected_parameters": {
            "weight_separation": params.weight_separation,
            "weight_alignment": params.weight_alignment,
            "weight_cohesion": params.weight_cohesion,
            "radius_separation": params.radius_separation,
            "radius_alignment": params.radius_alignment,
            "radius_cohesion": params.radius_cohesion,
            "rear_blind_angle_deg": params.rear_blind_angle_deg,
        },
        "selection_objective": training[
            "selection_objective"
        ],
        "results": records,
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"\n[OK] CSV : {OUTPUT_CSV}")
    print(f"[OK] JSON : {OUTPUT_JSON}")
    print(
        f"[TERMINÉ] "
        f"{time.perf_counter() - tic:.2f} s",
        flush=True,
    )


if __name__ == "__main__":
    main()
