"""Validation de Boids sur plusieurs fenêtres expérimentales.

Aucun recalibrage des coefficients entre les fenêtres.
Chaque expérience conserve ses identifiants suivis sur 32 frames.
"""

from pathlib import Path
import time

import ijson

from src.boids_pilot import DATASET
from src.compare_boids_graphs import compare_graphs


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "results" / "simulation"

WINDOW_STARTS = (2000, 4000)
HORIZON = 30
RADIUS = 100


def load_windows(
    dataset=DATASET,
    starts=WINDOW_STARTS,
    horizon=HORIZON,
):
    starts = tuple(starts)

    windows = {start: {} for start in starts}
    last_frame = max(starts) + horizon + 1

    print(
        "[1/3] Lecture streaming du dataset...",
        flush=True,
    )

    with Path(dataset).open("rb") as stream:
        for key, frame in ijson.kvitems(stream, ""):
            frame_id = int(key)

            for start in starts:
                if start <= frame_id < start + horizon + 2:
                    relative_id = frame_id - start + 1
                    windows[start][relative_id] = frame

            if frame_id >= last_frame:
                break

    expected = set(range(1, horizon + 3))

    for start, frames in windows.items():
        if set(frames) != expected:
            missing = sorted(expected - set(frames))
            raise ValueError(
                f"Fenêtre {start} incomplète : {missing}"
            )

        print(
            f"[OK] Frames {start}–{start + horizon + 1} "
            f": {len(frames)} observations temporelles",
            flush=True,
        )

    return windows


def print_comparison(result, start):
    rows = result["results"]
    cohort = result["method"]["cohort_size"]

    print(
        f"\n=== FENÊTRE {start} | "
        f"COHORTE {cohort} POISSONS ===",
        flush=True,
    )

    for graph_type in ("spatial", "visibility"):
        print(
            f"\nGRAPHE {graph_type.upper()}",
            flush=True,
        )

        for horizon in (1, 10, 30):
            print(
                f"\nHorizon {horizon} frames",
                flush=True,
            )

            subset = {
                row["model"]: row
                for row in rows
                if row["graph_type"] == graph_type
                and row["horizon_frames"] == horizon
            }

            real = subset["real"]

            print(
                f"Réel : communautés={real['communities']} "
                f"| modularité={real['modularity']} "
                f"| composante={real['largest_component_share']}"
            )

            for model in ("boids", "inertia"):
                row = subset[model]

                modularity_difference = (
                    abs(
                        row["modularity"]
                        - real["modularity"]
                    )
                    if row["modularity"] is not None
                    and real["modularity"] is not None
                    else None
                )

                print(
                    f"{model:8} "
                    f"| Jaccard={row['edge_jaccard_vs_real']:.4f} "
                    f"| communautés={row['communities']} "
                    f"| écart modularité="
                    f"{modularity_difference} "
                    f"| composante="
                    f"{row['largest_component_share']:.4f}"
                )


def main():
    start_time = time.perf_counter()

    windows = load_windows()

    print(
        "\n[2/3] Comparaison des modèles...",
        flush=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = {}

    for start, frames in windows.items():
        output = OUTPUT_DIR / (
            f"graph_comparison_start{start}"
            f"_h30_R100.json"
        )

        print(
            f"\n=== DÉBUT FENÊTRE {start} ===",
            flush=True,
        )

        result = compare_graphs(
            frames=frames,
            horizon=HORIZON,
            radius=RADIUS,
            output=output,
        )

        results[start] = result

    print(
        "\n[3/3] Synthèse scientifique...",
        flush=True,
    )

    for start, result in results.items():
        print_comparison(result, start)

    print(
        f"\n[TERMINÉ] "
        f"{time.perf_counter() - start_time:.2f} s",
        flush=True,
    )


if __name__ == "__main__":
    main()
