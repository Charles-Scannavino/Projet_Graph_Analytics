import csv

from src.compare_fish_leadership import (
    WINDOW_STARTS,
    N_FRAMES,
    MIN_PERSISTENT_PHASES,
)

RESULTS = "results/leadership/comparison"


def read_csv(name):
    with open(
        f"{RESULTS}/{name}",
        newline="",
        encoding="utf-8",
    ) as f:
        return list(csv.DictReader(f))


def test_window_configuration():
    assert WINDOW_STARTS == (1, 2000, 4000)
    assert N_FRAMES == 150
    assert MIN_PERSISTENT_PHASES == 3


def test_comparison_windows():
    rows = read_csv("leadership_comparison.csv")

    assert len(rows) == 3
    assert [int(r["window_start"]) for r in rows] == [
        1, 2000, 4000
    ]

    for row in rows:
        start = int(row["window_start"])
        end = int(row["window_end"])

        assert end == start + 149
        assert int(row["phase_count"]) == 5


def test_phase_boundaries():
    rows = read_csv("leaders_phases_all_windows.csv")

    for row in rows:
        start = int(row["window_start"])
        phase = int(row["phase"])

        assert int(row["start_frame"]) == (
            start + (phase - 1) * 30
        )
        assert int(row["end_frame"]) == (
            start + phase * 30 - 1
        )


def test_reference_persistent_leader():
    rows = read_csv("leaders_summary_all_windows.csv")

    persistent = {
        int(row["fish_id"])
        for row in rows
        if int(row["window_start"]) == 2000
        and int(row["persistent_leader"]) == 1
    }

    assert persistent == {105760}


def test_persistence_consistency():
    rows = read_csv("leaders_summary_all_windows.csv")

    for row in rows:
        phases = int(row["leader_phases"])
        persistent = int(row["persistent_leader"])

        assert 0 <= phases <= 5
        assert persistent == int(
            phases >= MIN_PERSISTENT_PHASES
        )


def test_comparison_counts():
    rows = read_csv("leadership_comparison.csv")

    expected = {
        1: (105, 17, 0),
        2000: (93, 21, 1),
        4000: (140, 27, 0),
    }

    for row in rows:
        start = int(row["window_start"])

        actual = (
            int(row["fish_count"]),
            int(row["potential_leaders"]),
            int(row["persistent_leaders"]),
        )

        assert actual == expected[start]
