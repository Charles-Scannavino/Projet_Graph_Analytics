"""Polarisation et erreur angulaire : réel, Boids calibré, inertie.

Calibration : frames 1-32 uniquement.
Validation indépendante : frames 2000-2031 et 4000-4031.
Les directions réelles sont calculées à partir des positions successives.
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
OUTPUT = SIM_DIR / "boids_behavior_metrics.csv"

HORIZON = 30
CHECKPOINTS = (1, 5, 10, 20, 30)
EPS = 1e-12


def unit_vectors(velocities):
    """Renvoie les directions et un masque des vitesses non nulles."""
    v = np.asarray(velocities, dtype=float)

    if v.ndim != 2 or v.shape[1] != 2:
        raise ValueError("Vitesses de forme (N, 2) attendues.")
    if not np.isfinite(v).all():
        raise ValueError("Vitesses non finies.")

    norms = np.linalg.norm(v, axis=1)
    valid = norms > EPS

    directions = np.zeros_like(v)
    directions[valid] = v[valid] / norms[valid, None]

    return directions, valid


def polarization(velocities):
    """Norme de la direction moyenne des poissons en mouvement."""
    directions, valid = unit_vectors(velocities)

    if not np.any(valid):
        return float("nan")

    return float(np.linalg.norm(directions[valid].mean(axis=0)))


def angular_error(real_velocity, predicted_velocity):
    """Erreur angulaire moyenne en degrés, sur les paires valides."""
    real_dir, real_valid = unit_vectors(real_velocity)
    pred_dir, pred_valid = unit_vectors(predicted_velocity)

    if real_dir.shape != pred_dir.shape:
        raise ValueError("Dimensions de vitesses différentes.")

    valid = real_valid & pred_valid

    if not np.any(valid):
        return float("nan"), 0

    cosines = np.sum(
        real_dir[valid] * pred_dir[valid], axis=1
    )
    cosines = np.clip(cosines, -1.0, 1.0)

    angles = np.degrees(np.arccos(cosines))

    return float(np.mean(angles)), int(valid.sum())


def frame_mapping(frame):
    ids, positions = positions_from_frame(frame)
    return dict(zip(map(int, ids), positions))


def calibrated_parameters():
    if not CALIBRATION.is_file():
        raise FileNotFoundError(
            f"Calibration introuvable : {CALIBRATION}"
        )

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
    """Cohorte fixe identique pour les trois modèles."""
    ids_all, pos_all, vel_all = initial_state(
        frames[1], frames[2]
    )

    survivors = set(map(int, ids_all))

    for frame_id in range(3, HORIZON + 3):
        survivors &= set(frame_mapping(frames[frame_id]))

    indices = np.array([
        i for i, fish_id in enumerate(ids_all)
        if int(fish_id) in survivors
    ], dtype=int)

    if not len(indices):
        raise ValueError("Aucun poisson suivi continuellement.")

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

    for h in range(1, HORIZON + 1):
        pos_b, vel_b = step_boids(pos_b, vel_b, params)
        pos_i, vel_i = step_persistence(pos_i, vel_i)

        if h not in CHECKPOINTS:
            continue

        current = frame_mapping(frames[h + 2])
        previous = frame_mapping(frames[h + 1])

        real_pos = np.array([
            current[int(fish_id)] for fish_id in ids
        ])
        prev_pos = np.array([
            previous[int(fish_id)] for fish_id in ids
        ])

        real_vel = real_pos - prev_pos

        real_polarization = polarization(real_vel)

        for model, velocity in (
            ("real", real_vel),
            ("boids", vel_b),
            ("inertia", vel_i),
        ):
            pol = polarization(velocity)

            if model == "real":
                error = 0.0
                valid_count = int(unit_vectors(real_vel)[1].sum())
            else:
                error, valid_count = angular_error(
                    real_vel, velocity
                )

            rows.append({
                "window_start": start,
                "horizon_frames": h,
                "model": model,
                "cohort_size": len(ids),
                "polarization": round(pol, 6),
                "polarization_error": round(
                    abs(pol - real_polarization), 6
                ),
                "mean_angular_error_deg": round(error, 6),
                "valid_direction_pairs": valid_count,
            })

        print(
            f"  H={h:2d} | "
            f"P réel={real_polarization:.3f} | "
            f"P Boids={polarization(vel_b):.3f} | "
            f"P inertie={polarization(vel_i):.3f}",
            flush=True,
        )

    return rows


def plot_window(rows, start, metric, title, ylabel, filename):
    subset = [
        row for row in rows
        if row["window_start"] == start
    ]

    fig, ax = plt.subplots(figsize=(9, 5))

    for model, label in (
        ("real", "Réel"),
        ("boids", "Boids calibré"),
        ("inertia", "Inertie"),
    ):
        if metric == "mean_angular_error_deg" and model == "real":
            continue

        selected = sorted(
            (r for r in subset if r["model"] == model),
            key=lambda r: r["horizon_frames"],
        )

        ax.plot(
            [r["horizon_frames"] for r in selected],
            [r[metric] for r in selected],
            marker="o",
            linewidth=2,
            label=label,
        )

    ax.set_title(f"{title}\nFenêtre {start}-{start + 31}")
    ax.set_xlabel("Horizon de prédiction (frames)")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    ax.legend()

    if metric == "polarization":
        ax.set_ylim(0, 1)

    fig.tight_layout()

    for extension in ("png", "svg"):
        fig.savefig(
            FIG_DIR / f"{filename}.{extension}",
            dpi=180,
        )

    plt.close(fig)


def main():
    params = calibrated_parameters()

    print("=== MÉTRIQUES COMPORTEMENTALES ===")
    print(
        "Paramètres calibrés :",
        params.weight_separation,
        params.weight_alignment,
        params.weight_cohesion,
    )

    # Entraînement et validation restent identifiés séparément.
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
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)

    for start in sorted(windows):
        plot_window(
            rows, start,
            "polarization",
            "Polarisation du banc",
            "Polarisation (0 à 1)",
            f"boids_polarization_start{start}",
        )

        plot_window(
            rows, start,
            "mean_angular_error_deg",
            "Erreur angulaire par rapport au réel",
            "Erreur moyenne (degrés)",
            f"boids_angular_error_start{start}",
        )

    print("\n=== SYNTHÈSE VALIDATION H=30 ===")

    for model in ("boids", "inertia"):
        selected = [
            r for r in rows
            if r["window_start"] in (2000, 4000)
            and r["horizon_frames"] == 30
            and r["model"] == model
        ]

        print(
            f"{model:8} | "
            f"Écart polarisation="
            f"{np.mean([r['polarization_error'] for r in selected]):.4f} "
            f"| Erreur angulaire="
            f"{np.mean([r['mean_angular_error_deg'] for r in selected]):.2f}°"
        )

    print(f"\n[OK] {len(rows)} lignes : {OUTPUT}")
    print("[OK] 6 graphiques PNG + 6 SVG")
    print(f"[OK] Dossier : {FIG_DIR}")


if __name__ == "__main__":
    main()
