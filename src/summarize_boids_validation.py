"""Synthèse des validations Boids sur trois fenêtres."""

from pathlib import Path
from statistics import mean
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "results" / "simulation"
OUTPUT = DIRECTORY / "boids_validation_summary.csv"

FILES = {
    "1-32": "graph_comparison_h30_R100.json",
    "2000-2031": "graph_comparison_start2000_h30_R100.json",
    "4000-4031": "graph_comparison_start4000_h30_R100.json",
}

HORIZONS = (1, 10, 30)
GRAPH_TYPES = ("spatial", "visibility")
MODELS = ("boids", "inertia")


def select_row(rows, horizon, graph_type, model):
    selected = [
        r for r in rows
        if r["horizon_frames"] == horizon
        and r["graph_type"] == graph_type
        and r["model"] == model
    ]

    if len(selected) != 1:
        raise ValueError(
            f"Résultat manquant ou dupliqué : "
            f"{horizon}, {graph_type}, {model}"
        )

    return selected[0]


def absolute_difference(a, b):
    if a is None or b is None:
        return None
    return round(abs(a - b), 5)


def summarize():
    records = []

    for window, filename in FILES.items():
        path = DIRECTORY / filename

        if not path.is_file():
            raise FileNotFoundError(path)

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        rows = data["results"]
        cohort = data["method"]["cohort_size"]

        for horizon in HORIZONS:
            for graph_type in GRAPH_TYPES:
                real = select_row(
                    rows, horizon, graph_type, "real"
                )

                for model in MODELS:
                    simulated = select_row(
                        rows, horizon, graph_type, model
                    )

                    records.append({
                        "window": window,
                        "cohort_size": cohort,
                        "horizon": horizon,
                        "graph_type": graph_type,
                        "model": model,
                        "edge_jaccard": simulated[
                            "edge_jaccard_vs_real"
                        ],
                        "position_error": simulated[
                            "mean_position_error"
                        ],
                        "modularity_real": real["modularity"],
                        "modularity_simulated": simulated[
                            "modularity"
                        ],
                        "modularity_abs_error": absolute_difference(
                            real["modularity"],
                            simulated["modularity"],
                        ),
                        "clustering_abs_error": absolute_difference(
                            real["clustering"],
                            simulated["clustering"],
                        ),
                        "component_abs_error": absolute_difference(
                            real["largest_component_share"],
                            simulated["largest_component_share"],
                        ),
                        "community_count_abs_error": abs(
                            real["communities"]
                            - simulated["communities"]
                        ),
                    })

        print(
            f"[OK] Fenêtre {window} : "
            f"{cohort} poissons",
            flush=True,
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(records[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)

    print("\n=== SYNTHÈSE À 30 FRAMES ===")

    for graph_type in GRAPH_TYPES:
        print(f"\n{graph_type.upper()}")

        for model in MODELS:
            sample = [
                r for r in records
                if r["horizon"] == 30
                and r["graph_type"] == graph_type
                and r["model"] == model
            ]

            print(
                f"{model:8} | "
                f"Jaccard={mean(r['edge_jaccard'] for r in sample):.5f} "
                f"| Erreur position="
                f"{mean(r['position_error'] for r in sample):.5f} "
                f"| Écart modularité="
                f"{mean(r['modularity_abs_error'] for r in sample):.5f} "
                f"| Écart clustering="
                f"{mean(r['clustering_abs_error'] for r in sample):.5f}"
            )

    print(
        f"\n[OK] {len(records)} lignes : {OUTPUT}",
        flush=True,
    )

    return records


if __name__ == "__main__":
    summarize()
