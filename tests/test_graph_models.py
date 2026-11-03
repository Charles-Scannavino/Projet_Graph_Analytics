import math
from pathlib import Path

import networkx as nx
import numpy as np
import pytest

from src.data_loader import load_frame
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph


# Configuration scientifique définitive
RADIUS = 100
BLIND_ANGLE = 25


def two_fish(x2, y2):
    """Deux poissons orientés vers la droite."""
    return {
        "px": np.array([0.0, x2]),
        "py": np.array([0.0, y2]),
        "vx": np.array([1.0, 1.0]),
        "vy": np.array([0.0, 0.0]),
        "onfish": np.array([1, 2]),
    }


def test_spatial_graph_and_isolates():
    frame = {
        "px": np.array([0.0, 3.0, 20.0]),
        "py": np.array([0.0, 4.0, 0.0]),
        "vx": np.ones(3),
        "vy": np.zeros(3),
        "onfish": np.array([11, 22, 33]),
    }

    G = build_graph(frame, radius=6)

    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 1
    assert G.has_edge(11, 22)
    assert G.degree(33) == 0
    assert G[11][22]["distance"] == pytest.approx(5.0)
    assert nx.number_of_selfloops(G) == 0


def test_strict_distance_threshold():
    G = build_graph(two_fish(3, 4), radius=5)
    assert G.number_of_edges() == 0


def test_forward_and_rear_visibility():
    G = build_visibility_graph(
        two_fish(1, 0),
        radius=2,
        rear_blind_angle_deg=BLIND_ANGLE,
    )

    assert G.has_edge(1, 2)
    assert not G.has_edge(2, 1)


def test_lateral_visibility():
    G = build_visibility_graph(
        two_fish(0, 1),
        radius=2,
        rear_blind_angle_deg=BLIND_ANGLE,
    )

    assert G.has_edge(1, 2)
    assert G.has_edge(2, 1)


@pytest.mark.parametrize(
    "direction_deg,expected_visible",
    [
        (160, True),
        (170, False),
    ],
)
def test_rear_blind_sector(direction_deg, expected_visible):
    angle = math.radians(direction_deg)

    frame = two_fish(
        math.cos(angle),
        math.sin(angle),
    )

    G = build_visibility_graph(
        frame,
        radius=2,
        rear_blind_angle_deg=BLIND_ANGLE,
    )

    assert G.has_edge(1, 2) == expected_visible


def test_zero_direction():
    frame = two_fish(1, 0)
    frame["vx"][0] = 0.0
    frame["vy"][0] = 0.0

    G = build_visibility_graph(
        frame,
        radius=2,
        rear_blind_angle_deg=BLIND_ANGLE,
    )

    assert G.out_degree(1) == 0


def test_invalid_blind_angle():
    with pytest.raises(ValueError):
        build_visibility_graph(
            two_fish(1, 0),
            radius=2,
            rear_blind_angle_deg=360,
        )


def test_invalid_radius():
    with pytest.raises(ValueError):
        build_graph(two_fish(1, 0), radius=0)


def test_real_frame_at_25_degrees():
    dataset = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "schooling_frames.json"
    )

    if not dataset.is_file():
        pytest.skip("Dataset expérimental non disponible.")

    print("\n[1/3] Chargement de la frame réelle...", flush=True)
    frame = load_frame(dataset, frame_id=1)

    print("[2/3] Construction du graphe spatial...", flush=True)
    spatial = build_graph(frame, radius=RADIUS)

    print("[3/3] Construction du graphe de visibilité...", flush=True)
    visible = build_visibility_graph(
        frame,
        radius=RADIUS,
        rear_blind_angle_deg=BLIND_ANGLE,
    )

    assert visible.number_of_nodes() == 253
    assert visible.number_of_edges() == 2386

    assert nx.number_weakly_connected_components(visible) == 4
    assert nx.number_strongly_connected_components(visible) == 4

    assert nx.number_of_selfloops(visible) == 0

    # Chaque arc doit respecter le voisinage spatial.
    for i, j in visible.edges():
        assert spatial.has_edge(i, j)

    print("[OK] Graphe à 25° validé.", flush=True)
