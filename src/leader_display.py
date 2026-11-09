"""Sélection et coloration des leaders potentiels."""

import csv
from pathlib import Path

BLUE = "#1f77b4"
RED = "#dc2626"

ROOT = Path(__file__).resolve().parents[1]
LEADER_DIR = ROOT / "results/leadership"


def load_leaders(folder=LEADER_DIR):
    phase_file = Path(folder) / "leaders_phases.csv"
    summary_file = Path(folder) / "leaders_summary.csv"

    if not phase_file.is_file() or not summary_file.is_file():
        return {}, set()

    phases = {}

    with phase_file.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["leader_phase"]):
                phase = int(row["phase"])
                phases.setdefault(phase, set()).add(
                    int(row["fish_id"])
                )

    persistent = set()

    with summary_file.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["persistent_leader"]):
                persistent.add(int(row["fish_id"]))

    return phases, persistent


def selected_leaders(
    mode, frame, start, horizon, phases, persistent
):
    # Les fichiers actuels couvrent uniquement 2000–2149.
    if start != 2000 or horizon != 150:
        return set()

    if not 2000 <= frame <= 2149:
        return set()

    if mode == "Phase":
        phase = (frame - 2000) // 30 + 1
        return phases.get(phase, set())

    if mode == "Persistants":
        return persistent

    return set()


def fish_colors(ids, leaders):
    return [
        RED if int(fish_id) in leaders else BLUE
        for fish_id in ids
    ]
