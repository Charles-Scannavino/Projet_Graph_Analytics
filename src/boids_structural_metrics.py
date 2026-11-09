"""Comparaison structurelle : poissons réels, Boids calibré, inertie.

Métriques :
- distance moyenne au plus proche voisin ;
- écart absolu de cette distance au réel ;
- degré moyen du graphe spatial ;
- erreur absolue moyenne des degrés individuels.

Calibration : fenêtre 1-32.
Validation : fenêtres 2000-2031 et 4000-4031.
"""

from dataclasses import replace
from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.boids_pilot import (
    BoidsParameters,
    initial_state,
    load_observations,
    positions_from_frame,
    step_boids,
    step_persistence,
)
from src.validate_boids_windows import load_windows


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "results" / "simulation"
FIG_DIR = ROOT / "results" / "figures"

CALIBRATION = SIM_DIR / "boids_calibration_train_R100.json"
OUTPUT = SIM_DIR / "boids_structural_metrics.csv"

RADIUS = 100.0
HORIZON = 30
CHECKPOINTS = (1, 5, 10, 20, 30)


def distance_matrix(positions):
    """Matrice des distances euclidiennes."""
    xy = np.asarray(positions, dtype=float)

    if xy.ndim != 2 or xy.shape[1] != 2:
        raise ValueError("Positions (N, 2) attendues.")

    if not np.isfinite(xy).all():
        raise ValueError("Positions non finies.")

    delta = xy[:, None, :] - xy[None, :, :]
    return np.linalg.norm(delta, axis=2)


def nearest_neighbor_distances(positions):
    """Distance au plus proche autre poisson pour chaque individu."""
    distances = distance_matrix(positions)

    if len(distances) < 2:
        raise ValueError("Au moins deux poissons nécessaires.")

    np.fill_diagonal(distances, np.inf)
    return np.min(distances, axis=1)


def spatial_degrees(positions, radius=RADIUS):
    """Degré de chaque poisson dans le graphe spatial non orienté."""
    if radius <= 0 or not np.isfinite(radius):
        raise ValueError("Rayon invalide.")

    distances = distance_matrix(positions)

    adjacency = distances < radius
    np.fill_diagonal(adjacency, False)

    return adjacency.sum(axis=1).astype(int)


def frame_mapping(frame):
    ids, xy = positions_from_frame(frame)
    return dict(zip(map(int, ids), xy))


def calibrated_parameters():
    data = json.loads(CALIBRATION.read_text(encoding="utf-8"))

    if data.get("training_window") != [1, 32]:
        raise ValueError("Fenêtre de calibration inattendue.")

    best = data["best"]

    return replace(
        BoidsParameters(),
        weight_separation=float(best["weight_separation"]),
        weight_alignment=float(best["weight_alignment"]),
        weight_cohesion=float(best["weight_cohesion"]),
    )


def analyze_window(frames, start, params):
    ids_all, pos_all, vel_all = initial_state(
        frames[1], frames[2]
    )

    survivors = set(map(int, ids_all))

    for frame_id in range(3, HORIZON + 3):
        survivors &= set(frame_mapping(frames[frame_id]))

    indices = np.array(
        [
            i for i, fish_id in enumerate(ids_all)
            if int(fish_id) in survivors
        ],
        dtype=int,
    )

    if len(indices) < 2:
        raise ValueError("Cohorte insuffisante.")

    ids = ids_all[indices]

    pos_b = pos_all[indices].copy()
    vel_b = vel_all[indices].copy()

    pos_i = pos_b.copy()
    vel_i = vel_b.copy()

    rows = []

    print(
        f"\n[FENÊTRE {start}-{start + 31}] "
        f"{len(ids)} poissons",
        flush=True,
    )

    for horizon in range(1, HORIZON + 1):
        pos_b, vel_b = step_boids(pos_b, vel_b, params)
        pos_i, vel_i = step_persistence(pos_i, vel_i)

        if horizon not in CHECKPOINTS:
            continue

        actual = frame_mapping(frames[horizon + 2])

        real_pos = np.array([
            actual[int(fish_id)] for fish_id in ids
        ])

        real_nn = nearest_neighbor_distances(real_pos)
        real_degrees = spatial_degrees(real_pos)

        for model, positions in (
            ("real", real_pos),
            ("boids", pos_b),
            ("inertia", pos_i),
        ):
            nn = nearest_neighbor_distances(positions)
            degrees = spatial_degrees(positions)

            rows.append({
                "window_start": start,
                "horizon_frames": horizon,
                "model": model,
                "cohort_size": len(ids),
                "radius": RADIUS,
                "mean_nearest_neighbor": round(
                    float(nn.mean()), 6
                ),
                "nearest_neighbor_mae": round(
                    float(np.mean(np.abs(nn - real_nn))), 6
                ),
                "mean_degree": round(
                    float(degrees.mean()), 6
                ),
                "degree_mae": round(
                    float(np.mean(
                        np.abs(degrees - real_degrees)
                    )), 6
                ),
            })

        print(
            f"  H={horizon:2d} | "
            f"distance NN réel={real_nn.mean():.3f} | "
            f"Boids={nearest_neighbor_distances(pos_b).mean():.3f} | "
            f"inertie={nearest_neighbor_distances(pos_i).mean():.3f}",
            flush=True,
        )

    return rows


def plot_metric(rows, start, metric, title, ylabel, filename):
    fig, ax = plt.subplots(figsize=(9, 5))

    for model, label in (
        ("real", "Réel"),
        ("boids", "Boids calibré"),
        ("inertia", "Inertie"),
    ):
        if metric.endswith("_mae") and model == "real":
            continue

        selected = sorted(
            [
                r for r in rows
                if r["window_start"] == start
                and r["model"] == model
            ],
            key=lambda r: r["horizon_frames"],
        )

        ax.plot(
            [r["horizon_frames"] for r in selected],
            [r[metric] for r in selected],
            marker="o",
            linewidth=2,
            label=label,
        )

    ax.set_title(f"{title} — fenêtre {start}-{start + 31}")
    ax.set_xlabel("Horizon de prédiction (frames)")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    for ext in ("png", "svg"):
        fig.savefig(
            FIG_DIR / f"{filename}.{ext}",
            dpi=180,
        )

    plt.close(fig)


def main():
    params = calibrated_parameters()

    print("=== VALIDATION STRUCTURELLE BOIDS ===")
    print(
        "Paramètres :",
        params.weight_separation,
        params.weight_alignment,
        params.weight_cohesion,
    )
    print("Rayon spatial :", RADIUS)

    windows = {
        1: load_observations(horizon=HORIZON)
    }

    windows.update(
        load_windows(
            starts=(2000, 4000),
            horizon=HORIZON,
        )
    )

    rows = []

    for start, frames in sorted(windows.items()):
        rows.extend(analyze_window(frames, start, params))

    SIM_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)

    metrics = (
        (
            "mean_nearest_neighbor",
            "Distance moyenne au plus proche voisin",
            "Distance (unités natives)",
            "nearest_neighbor",
        ),
        (
            "mean_degree",
            "Degré moyen du graphe spatial",
            "Nombre de voisins",
            "mean_degree",
        ),
        (
            "nearest_neighbor_mae",
            "Erreur de distance au plus proche voisin",
            "Erreur absolue (unités natives)",
            "nearest_neighbor_mae",
        ),
        (
            "degree_mae",
            "Erreur de degré individuel",
            "Erreur absolue (nombre de voisins)",
            "degree_mae",
        ),
    )

    for start in sorted(windows):
        for metric, title, ylabel, filename in metrics:
            plot_metric(
                rows, start, metric, title, ylabel,
                f"boids_{filename}_start{start}",
            )

    print("\n=== VALIDATION H=30 (FENÊTRES 2000 ET 4000) ===")

    for model in ("boids", "inertia"):
        selected = [
            r for r in rows
            if r["window_start"] in (2000, 4000)
            and r["horizon_frames"] == 30
            and r["model"] == model
        ]

        print(
            f"{model:8} | "
            f"Erreur NN="
            f"{np.mean([r['nearest_neighbor_mae'] for r in selected]):.4f}"
            f" | Erreur degré="
            f"{np.mean([r['degree_mae'] for r in selected]):.4f}"
        )

    print(f"\n[OK] {len(rows)} lignes : {OUTPUT}")
    print("[OK] 12 graphiques PNG + 12 SVG")
    print(f"[OK] Dossier : {FIG_DIR}")


if __name__ == "__main__":
    main()
