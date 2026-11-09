"""Détection exploratoire de leaders temporels dans un banc de poissons."""

from pathlib import Path
import csv
import numpy as np

from src.boids_pilot import positions_from_frame
from src.validate_boids_windows import load_windows

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/local/schooling_frames.json"
OUTPUT_DIR = ROOT / "results/leadership"

START = 2000
N_FRAMES = 150
PHASE_LENGTH = 30
RADIUS = 100.0
LAGS = range(1, 11)
MIN_PAIRS = 12
MIN_CORRELATION = 0.6
MIN_GAIN = 0.1
MIN_FOLLOWERS = 2


def load_trajectories():
    windows = load_windows(
        dataset=DATASET,
        starts=(START,),
        horizon=N_FRAMES - 2,
    )
    frames = windows[START]

    mappings = []
    for t in range(1, N_FRAMES + 1):
        ids, xy = positions_from_frame(frames[t])
        mappings.append(dict(zip(map(int, ids), xy)))

    common = set(mappings[0])
    for mapping in mappings[1:]:
        common.intersection_update(mapping)

    ids = np.array(sorted(common), dtype=int)
    if len(ids) < 2:
        raise ValueError("Pas assez de trajectoires continues.")

    positions = np.array([
        [mapping[int(i)] for i in ids]
        for mapping in mappings
    ], dtype=float)

    return ids, positions


def turning_signals(positions):
    velocities = np.diff(positions, axis=0)
    headings = np.arctan2(velocities[..., 1], velocities[..., 0])
    turns = np.angle(np.exp(1j * np.diff(headings, axis=0)))
    speeds = np.linalg.norm(velocities, axis=2)

    valid = (speeds[:-1] > 1e-8) & (speeds[1:] > 1e-8)
    turns[~valid] = np.nan
    return turns


def correlation(a, b):
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < MIN_PAIRS:
        return np.nan

    x = a[mask]
    y = b[mask]

    if np.std(x) < 1e-5 or np.std(y) < 1e-5:
        return np.nan

    return float(np.corrcoef(x, y)[0, 1])


def phase_scores(ids, positions, turns, phase_index):
    start = phase_index * PHASE_LENGTH
    end = start + PHASE_LENGTH

    phase_positions = positions[start:end]
    phase_turns = turns[start:min(end, len(turns))]

    n = len(ids)
    influence = np.zeros(n, dtype=float)
    followers = np.zeros(n, dtype=int)

    # Voisinage moyen pendant la phase.
    differences = (
        phase_positions[:, :, None, :]
        - phase_positions[:, None, :, :]
    )
    distances = np.linalg.norm(differences, axis=-1)
    proximity = np.mean(distances <= RADIUS, axis=0)

    for i in range(n):
        for j in range(n):
            if i == j or proximity[i, j] < 0.5:
                continue

            source = phase_turns[:, i]
            target = phase_turns[:, j]
            baseline = correlation(source, target)

            best = -np.inf
            for lag in LAGS:
                if len(source) - lag < MIN_PAIRS:
                    continue

                value = correlation(
                    source[:-lag], target[lag:]
                )
                if np.isfinite(value):
                    best = max(best, value)

            if not np.isfinite(best):
                continue

            baseline_value = baseline if np.isfinite(baseline) else 0.0

            if (
                best >= MIN_CORRELATION
                and best - baseline_value >= MIN_GAIN
            ):
                influence[i] += best
                followers[i] += 1

    rows = []
    for k, fish_id in enumerate(ids):
        rows.append({
            "phase": phase_index + 1,
            "start_frame": START + start,
            "end_frame": START + end - 1,
            "fish_id": int(fish_id),
            "followers": int(followers[k]),
            "influence_score": round(float(influence[k]), 6),
            "leader_phase": int(followers[k] >= MIN_FOLLOWERS),
        })

    return rows


def main():
    ids, positions = load_trajectories()
    turns = turning_signals(positions)

    rows = []
    n_phases = N_FRAMES // PHASE_LENGTH

    for phase in range(n_phases):
        phase_rows = phase_scores(ids, positions, turns, phase)
        rows.extend(phase_rows)

        leaders = [
            r["fish_id"] for r in phase_rows
            if r["leader_phase"]
        ]
        print(
            f"Phase {phase + 1}: "
            f"{len(leaders)} leaders potentiels : {leaders}"
        )

    summary = []
    for fish_id in ids:
        fish_rows = [
            r for r in rows if r["fish_id"] == int(fish_id)
        ]
        count = sum(r["leader_phase"] for r in fish_rows)

        summary.append({
            "fish_id": int(fish_id),
            "leader_phases": count,
            "persistence": round(count / n_phases, 3),
            "total_influence": round(
                sum(r["influence_score"] for r in fish_rows), 6
            ),
            "persistent_leader": int(count >= 3),
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, data in (
        ("leaders_phases.csv", rows),
        ("leaders_summary.csv", summary),
    ):
        path = OUTPUT_DIR / name
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=list(data[0])
            )
            writer.writeheader()
            writer.writerows(data)

        print(f"[OK] {path}")

    persistent = [
        r for r in summary if r["persistent_leader"]
    ]

    print(f"\nPoissons suivis : {len(ids)}")
    print(f"Leaders persistants potentiels : {len(persistent)}")
    print("Identifiants :", [r["fish_id"] for r in persistent])


if __name__ == "__main__":
    main()
