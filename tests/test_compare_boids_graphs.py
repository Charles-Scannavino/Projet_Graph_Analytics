import networkx as nx
import numpy as np
import pytest

from src.compare_boids_graphs import (
    compare_graphs,
    edge_jaccard,
)


def toy_frame(ids, xs):
    ids = np.asarray(ids, dtype=int)
    xs = np.asarray(xs, dtype=float)
    return {
        "onfish": ids,
        "px": xs,
        "py": np.zeros(len(ids)),
        "vx": np.full(len(ids), np.nan),
        "vy": np.full(len(ids), np.nan),
    }


def test_edge_jaccard_respects_orientation():
    a = nx.DiGraph([(1, 2), (2, 1)])
    b = nx.DiGraph([(1, 2)])

    assert edge_jaccard(a, b) == 0.5

    c = nx.Graph([(1, 2)])
    d = nx.Graph([(2, 1)])

    assert edge_jaccard(c, d) == 1.0


def test_fixed_cohort_and_inertial_prediction(tmp_path):
    frames = {
        1: toy_frame(
            [1, 2, 3, 4],
            [0, 400, 800, 1200],
        ),
        2: toy_frame(
            [1, 2, 3, 4],
            [1, 401, 801, 1201],
        ),
        3: toy_frame(
            [1, 2, 3],
            [2, 402, 802],
        ),
    }

    result = compare_graphs(
        frames=frames,
        horizon=1,
        output=tmp_path / "result.json",
    )

    assert result["method"]["cohort_size"] == 3
    assert len(result["results"]) == 6

    for row in result["results"]:
        assert row["nodes"] == 3
        assert row["edge_jaccard_vs_real"] == 1.0
        assert row["mean_position_error"] == 0.0


def test_invalid_radius():
    with pytest.raises(ValueError):
        compare_graphs(
            frames={},
            radius=0,
        )
