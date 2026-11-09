"""Comparaison expérimentale Boids et mouvement inertiel.

Initialisation : positions des frames 1 et 2.
Prévisions : frames 3 à 32.
Aucune direction future du dataset n'est utilisée.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import math
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "schooling_frames.json"
OUTPUT = ROOT / "results/simulation/boids_pilot_h30.json"


@dataclass(frozen=True)
class BoidsParameters:
    radius_separation: float = 60.0
    radius_alignment: float = 80.0
    radius_cohesion: float = 120.0
    rear_blind_angle_deg: float = 25.0
    weight_separation: float = 0.5
    weight_alignment: float = 0.3
    weight_cohesion: float = 0.2

    def validate(self):
        values = asdict(self)

        if not all(math.isfinite(x) for x in values.values()):
            raise ValueError("Paramètres non finis.")

        for key in (
            "radius_separation",
            "radius_alignment",
            "radius_cohesion",
        ):
            if getattr(self, key) <= 0:
                raise ValueError("Rayon non positif.")

        if not 0 <= self.rear_blind_angle_deg < 360:
            raise ValueError("Angle mort invalide.")

        for key in (
            "weight_separation",
            "weight_alignment",
            "weight_cohesion",
        ):
            if getattr(self, key) < 0:
                raise ValueError("Poids négatif interdit.")


def positions_from_frame(frame):
    ids = np.asarray(frame["onfish"], dtype=int)

    xy = np.column_stack((
        frame["px"],
        frame["py"],
    )).astype(float)

    if xy.shape != (len(ids), 2):
        raise ValueError("Dimensions incohérentes.")

    if len(set(map(int, ids))) != len(ids):
        raise ValueError("Identifiants dupliqués.")

    if not np.isfinite(xy).all():
        raise ValueError("Positions non finies.")

    return ids, xy


def initial_state(previous, current):
    old_ids, old_xy = positions_from_frame(previous)
    new_ids, new_xy = positions_from_frame(current)

    old_by_id = dict(zip(map(int, old_ids), old_xy))

    indices = [
        k for k, fish_id in enumerate(new_ids)
        if int(fish_id) in old_by_id
    ]

    if not indices:
        raise ValueError("Aucun identifiant commun.")

    ids = new_ids[indices].copy()
    xy = new_xy[indices].copy()

    previous_xy = np.array([
        old_by_id[int(i)] for i in ids
    ])

    velocity = xy - previous_xy
    return ids, xy, velocity


def unit(vector):
    norm = float(np.linalg.norm(vector))

    if norm <= 1e-12:
        return np.zeros(2)

    return vector / norm


def step_persistence(positions, velocity):
    return positions + velocity, velocity.copy()


def step_boids(
    positions,
    velocity,
    params=BoidsParameters(),
):
    params.validate()

    positions = np.asarray(positions, dtype=float)
    velocity = np.asarray(velocity, dtype=float)

    if (
        positions.ndim != 2
        or positions.shape[1] != 2
        or positions.shape != velocity.shape
    ):
        raise ValueError("Tableaux (N, 2) attendus.")

    if (
        not np.isfinite(positions).all()
        or not np.isfinite(velocity).all()
    ):
        raise ValueError("États non finis.")

    new_velocity = velocity.copy()

    cosine_limit = math.cos(math.radians(
        180 - params.rear_blind_angle_deg / 2
    ))

    for i in range(len(positions)):
        speed = float(np.linalg.norm(velocity[i]))

        if speed <= 1e-12:
            continue

        direction = velocity[i] / speed
        delta = positions - positions[i]
        distances = np.linalg.norm(delta, axis=1)

        nonzero = distances > 1e-12

        bearings = np.zeros_like(delta)
        bearings[nonzero] = (
            delta[nonzero] / distances[nonzero, None]
        )

        visible = (
            nonzero
            & ((bearings @ direction) >= cosine_limit)
        )

        sep = visible & (
            distances < params.radius_separation
        )

        align = visible & (
            distances < params.radius_alignment
        )

        coh = visible & (
            distances < params.radius_cohesion
        )

        steering = direction.copy()

        if np.any(sep):
            repulsion = -np.sum(
                bearings[sep] / distances[sep, None],
                axis=0,
            )

            steering += (
                params.weight_separation
                * unit(repulsion)
            )

        if np.any(align):
            headings = np.array([
                unit(v) for v in velocity[align]
            ])

            steering += (
                params.weight_alignment
                * unit(np.mean(headings, axis=0))
            )

        if np.any(coh):
            steering += (
                params.weight_cohesion
                * unit(np.mean(delta[coh], axis=0))
            )

        candidate = unit(steering)

        new_velocity[i] = speed * (
            candidate if np.any(candidate)
            else direction
        )

    return positions + new_velocity, new_velocity


def load_observations(dataset=DATASET, horizon=30):
    import ijson

    if horizon < 1:
        raise ValueError("Horizon invalide.")

    frames = {}

    with Path(dataset).open("rb") as stream:
        for key, frame in ijson.kvitems(stream, ""):
            frame_id = int(key)

            if frame_id > horizon + 2:
                break

            ids, xy = positions_from_frame(frame)

            frames[frame_id] = {
                "onfish": ids,
                "px": xy[:, 0],
                "py": xy[:, 1],
            }

    expected = set(range(1, horizon + 3))

    if set(frames) != expected:
        raise ValueError(
            f"Frames manquantes : "
            f"{sorted(expected - set(frames))}"
        )

    return frames


def evaluate_pilot(
    dataset=DATASET,
    output=OUTPUT,
    horizon=30,
    params=BoidsParameters(),
):
    start = time.perf_counter()
    params.validate()

    print(
        "=== BOIDS VS INERTIE ===",
        flush=True,
    )

    print("[1/3] Chargement des frames...", flush=True)

    frames = load_observations(dataset, horizon)

    ids, xy, v = initial_state(
        frames[1],
        frames[2],
    )

    print(
        f"[OK] {len(ids)} poissons initialisés",
        flush=True,
    )

    pos_b, vel_b = xy.copy(), v.copy()
    pos_i, vel_i = xy.copy(), v.copy()

    survivors = set(map(int, ids))
    rows = []

    print("[2/3] Simulation...", flush=True)

    for h in range(1, horizon + 1):
        frame_id = h + 2

        pos_b, vel_b = step_boids(
            pos_b, vel_b, params
        )

        pos_i, vel_i = step_persistence(
            pos_i, vel_i
        )

        actual_ids, actual_xy = positions_from_frame(
            frames[frame_id]
        )

        actual = dict(zip(
            map(int, actual_ids),
            actual_xy,
        ))

        survivors &= set(actual)

        indices = [
            k for k, fish_id in enumerate(ids)
            if int(fish_id) in survivors
        ]

        if not indices:
            raise ValueError(
                "Aucun identifiant suivi continuellement."
            )

        truth = np.array([
            actual[int(ids[k])]
            for k in indices
        ])

        error_b = np.linalg.norm(
            pos_b[indices] - truth,
            axis=1,
        )

        error_i = np.linalg.norm(
            pos_i[indices] - truth,
            axis=1,
        )

        row = {
            "horizon_frames": h,
            "frame_id": frame_id,
            "continuous_ids": len(indices),
            "mean_error_boids": round(
                float(np.mean(error_b)), 5
            ),
            "mean_error_persistence": round(
                float(np.mean(error_i)), 5
            ),
            "median_error_boids": round(
                float(np.median(error_b)), 5
            ),
            "median_error_persistence": round(
                float(np.median(error_i)), 5
            ),
        }

        rows.append(row)

        if h in (1, 5, 10, 20, 30) or h == horizon:
            print(
                f"[FRAME {frame_id}] "
                f"IDs={row['continuous_ids']} | "
                f"Boids={row['mean_error_boids']:.3f} | "
                f"Inertie={row['mean_error_persistence']:.3f}",
                flush=True,
            )

    result = {
        "setup": {
            "initial_frames": [1, 2],
            "predicted_frames": [3, horizon + 2],
            "fps": 30,
            "units": "native_coordinates",
            "initial_velocity": "positions_1_to_2",
            "use_future_vx_vy": False,
            "parameters": asdict(params),
            "status": "exploratory_not_calibrated",
            "boundaries": "not_modeled",
        },
        "per_horizon": rows,
    }

    output = Path(output)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        f"[3/3] Résultat : {output}",
        flush=True,
    )

    print(
        f"[TERMINÉ] "
        f"{time.perf_counter() - start:.2f} s",
        flush=True,
    )

    return result


if __name__ == "__main__":
    evaluate_pilot()
