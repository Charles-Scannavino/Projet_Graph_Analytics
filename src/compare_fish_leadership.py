"""Comparaison temporelle des leaders sur trois fenêtres indépendantes."""

import csv
from pathlib import Path

import numpy as np

from src.boids_pilot import positions_from_frame
from src.validate_boids_windows import load_windows
from src.detect_fish_leaders import (
    DATASET,
    PHASE_LENGTH,
    phase_scores,
    turning_signals,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "results/leadership/comparison"

WINDOW_STARTS = (1, 2000, 4000)
N_FRAMES = 150
MIN_PERSISTENT_PHASES = 3


def load_all_trajectories():
    """Charger les trois fenêtres en une seule lecture du JSON."""

    windows = load_windows(
        dataset=DATASET,
        starts=WINDOW_STARTS,
        horizon=N_FRAMES - 2,
    )

    trajectories = {}

    for start, frames in windows.items():
        mappings = []

        for t in range(1, N_FRAMES + 1):
            ids, xy = positions_from_frame(frames[t])
            mappings.append(
                dict(zip(map(int, ids), xy))
            )

        common = set(mappings[0])

        for mapping in mappings[1:]:
            common.intersection_update(mapping)

        ids = np.array(sorted(common), dtype=int)

        if len(ids) < 2:
            raise ValueError(
                f"Pas assez de poissons continus "
                f"pour la fenêtre {start}."
            )

        positions = np.array(
            [
                [mapping[int(fish_id)] for fish_id in ids]
                for mapping in mappings
            ],
            dtype=float,
        )

        trajectories[start] = (ids, positions)

        print(
            f"[OK] Fenêtre {start} : "
            f"{len(ids)} poissons suivis"
        )

    return trajectories


def analyze_window(start, ids, positions):
    """Calculer les scores et la persistance des leaders."""

    turns = turning_signals(positions)
    n_phases = N_FRAMES // PHASE_LENGTH

    phase_rows = []

    for phase in range(n_phases):
        rows = phase_scores(
            ids, positions, turns, phase
        )

        for row in rows:
            # phase_scores utilise START=2000 en interne.
            # On corrige les bornes dans la copie des résultats,
            # sans modifier le détecteur de référence.
            row = dict(row)

            row["start_frame"] = (
                start + phase * PHASE_LENGTH
            )
            row["end_frame"] = (
                row["start_frame"] + PHASE_LENGTH - 1
            )
            row["window_start"] = start

            phase_rows.append(row)

        leaders = [
            row["fish_id"]
            for row in rows
            if row["leader_phase"]
        ]

        print(
            f"  Phase {phase + 1} : "
            f"{len(leaders)} leaders potentiels"
        )

    summary_rows = []

    for fish_id in ids:
        fish_rows = [
            row
            for row in phase_rows
            if row["fish_id"] == int(fish_id)
        ]

        count = sum(
            row["leader_phase"]
            for row in fish_rows
        )

        total_influence = sum(
            row["influence_score"]
            for row in fish_rows
        )

        total_followers = sum(
            row["followers"]
            for row in fish_rows
        )

        summary_rows.append({
            "window_start": start,
            "fish_id": int(fish_id),
            "leader_phases": count,
            "persistence": round(
                count / n_phases, 3
            ),
            "total_influence": round(
                total_influence, 6
            ),
            "total_followers": total_followers,
            "persistent_leader": int(
                count >= MIN_PERSISTENT_PHASES
            ),
        })

    potential_ids = {
        row["fish_id"]
        for row in phase_rows
        if row["leader_phase"]
    }

    persistent_ids = {
        row["fish_id"]
        for row in summary_rows
        if row["persistent_leader"]
    }

    comparison = {
        "window_start": start,
        "window_end": start + N_FRAMES - 1,
        "fish_count": len(ids),
        "phase_count": n_phases,
        "potential_leaders": len(potential_ids),
        "persistent_leaders": len(persistent_ids),
        "total_influence": round(
            sum(
                row["total_influence"]
                for row in summary_rows
            ),
            6,
        ),
        "persistent_ids": ";".join(
            map(str, sorted(persistent_ids))
        ),
    }

    return phase_rows, summary_rows, comparison


def save_csv(filename, rows):
    """Enregistrer un CSV avec des colonnes explicites."""

    if not rows:
        raise ValueError(
            f"Aucune donnée pour {filename}"
        )

    OUTPUT_DIR.mkdir(
        parents=True, exist_ok=True
    )

    path = OUTPUT_DIR / filename

    with path.open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] {path}")


def main():
    print(
        "\n=== COMPARAISON TEMPORELLE "
        "DU LEADERSHIP ===\n"
    )

    trajectories = load_all_trajectories()

    all_phases = []
    all_summary = []
    all_comparison = []

    for start in WINDOW_STARTS:
        print(
            f"\n=== FENÊTRE "
            f"{start}–{start + N_FRAMES - 1} ==="
        )

        ids, positions = trajectories[start]

        phases, summary, comparison = (
            analyze_window(
                start, ids, positions
            )
        )

        all_phases.extend(phases)
        all_summary.extend(summary)
        all_comparison.append(comparison)

        print(
            "Leaders persistants :",
            comparison["persistent_ids"] or "Aucun",
        )

    save_csv(
        "leaders_phases_all_windows.csv",
        all_phases,
    )

    save_csv(
        "leaders_summary_all_windows.csv",
        all_summary,
    )

    save_csv(
        "leadership_comparison.csv",
        all_comparison,
    )

    print("\n=== SYNTHÈSE ===")

    for row in all_comparison:
        print(
            f"Fenêtre {row['window_start']} : "
            f"{row['fish_count']} poissons | "
            f"{row['potential_leaders']} "
            f"leaders potentiels | "
            f"{row['persistent_leaders']} "
            f"leaders persistants"
        )

    print("\n[TERMINÉ] Analyse comparative.")


if __name__ == "__main__":
    main()
