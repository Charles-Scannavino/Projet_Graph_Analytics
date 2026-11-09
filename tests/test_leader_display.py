import numpy as np

from src.leader_display import (
    BLUE,
    RED,
    fish_colors,
    load_leaders,
    selected_leaders,
)
from src.boids_interface import fish_triangles


def test_leader_csv_loaded():
    phases, persistent = load_leaders()

    assert len(phases) == 5
    assert persistent == {105760}
    assert 105760 in phases[1]
    assert 105760 in phases[2]
    assert 105760 in phases[4]


def test_off_mode():
    phases, persistent = load_leaders()

    result = selected_leaders(
        "OFF", 2070, 2000, 150, phases, persistent
    )

    assert result == set()


def test_phase_mode():
    phases, persistent = load_leaders()

    expected = {
        1: {105424, 105469, 105561, 105652, 105738, 105760},
        2: {104628, 104939, 105293, 105424, 105561,
            105760, 105761, 105808},
        3: {105469, 105538, 105727, 105845},
        4: {105192, 105760, 105805, 105811, 105814, 105845},
        5: {104628, 105466, 105722, 105846},
    }

    for phase, leaders in expected.items():
        frame = 2000 + (phase - 1) * 30

        result = selected_leaders(
            "Phase", frame, 2000, 150,
            phases, persistent
        )

        assert result == leaders


def test_persistent_mode():
    phases, persistent = load_leaders()

    for frame in (2000, 2030, 2070, 2090, 2149):
        result = selected_leaders(
            "Persistants", frame, 2000, 150,
            phases, persistent
        )

        assert result == {105760}


def test_outside_analyzed_window():
    phases, persistent = load_leaders()

    for start, horizon, frame in (
        (1, 150, 70),
        (4000, 150, 4070),
        (2000, 30, 2010),
        (2000, 150, 2150),
    ):
        result = selected_leaders(
            "Persistants", frame, start, horizon,
            phases, persistent
        )

        assert result == set()


def test_fish_colors():
    ids = [105760, 105424, 105469]
    leaders = {105760}

    assert fish_colors(ids, leaders) == [
        RED, BLUE, BLUE
    ]


def test_triangle_orientation():
    positions = np.array([
        [100.0, 100.0],
        [200.0, 200.0],
    ])

    velocities = np.array([
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    triangles = fish_triangles(
        positions, velocities,
        length=35.0,
        width=20.0,
    )

    assert triangles.shape == (2, 3, 2)

    # Le premier sommet est la pointe du triangle.
    assert triangles[0, 0, 0] > positions[0, 0]
    assert triangles[1, 0, 1] > positions[1, 1]

    # La pointe est en avant du centre.
    for i in range(2):
        direction = velocities[i] / np.linalg.norm(
            velocities[i]
        )
        forward = triangles[i, 0] - positions[i]

        assert np.dot(forward, direction) > 0


def test_leader_triangle_larger():
    position = np.array([[100.0, 100.0]])
    velocity = np.array([[1.0, 0.0]])

    normal = fish_triangles(
        position, velocity,
        length=24.0, width=13.5
    )

    leader = fish_triangles(
        position, velocity,
        length=35.0, width=20.0
    )

    normal_extent = np.ptp(normal[0], axis=0)
    leader_extent = np.ptp(leader[0], axis=0)

    assert np.all(leader_extent > normal_extent)
