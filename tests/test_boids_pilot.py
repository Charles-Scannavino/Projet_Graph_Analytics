import numpy as np
import pytest

from src.boids_pilot import (
    BoidsParameters,
    initial_state,
    step_boids,
    step_persistence,
)


def frame(ids, xy, direction=None):
    xy = np.asarray(xy, dtype=float)

    d = (
        np.full_like(xy, np.nan)
        if direction is None
        else np.asarray(direction, dtype=float)
    )

    return {
        "onfish": np.asarray(ids),
        "px": xy[:, 0],
        "py": xy[:, 1],
        "vx": d[:, 0],
        "vy": d[:, 1],
    }


def test_initial_state_uses_only_positions():
    old = frame(
        [2, 8],
        [[0, 0], [10, 1]],
    )

    current = frame(
        [8, 9],
        [[12, 4], [1, 1]],
    )

    ids, xy, v = initial_state(old, current)

    assert ids.tolist() == [8]

    np.testing.assert_allclose(xy, [[12, 4]])
    np.testing.assert_allclose(v, [[2, 3]])


def test_no_neighbours_matches_persistence():
    xy = np.array([
        [0., 0.],
        [500., 0.],
    ])

    v = np.array([
        [3., 0.],
        [0., -2.],
    ])

    b_pos, b_v = step_boids(xy, v)
    i_pos, i_v = step_persistence(xy, v)

    np.testing.assert_allclose(b_pos, i_pos)
    np.testing.assert_allclose(b_v, i_v)


def test_rear_blind_sector():
    xy = np.array([
        [0., 0.],
        [-3., 0.],
    ])

    v = np.array([
        [2., 0.],
        [2., 0.],
    ])

    p = BoidsParameters(
        radius_separation=10,
        radius_alignment=10,
        radius_cohesion=10,
        weight_separation=2,
        weight_alignment=0,
        weight_cohesion=0,
    )

    new_pos, new_v = step_boids(xy, v, p)

    np.testing.assert_allclose(
        new_pos[0],
        [2., 0.],
    )

    np.testing.assert_allclose(
        new_v[0],
        [2., 0.],
    )


def test_separation_can_reverse_headings():
    xy = np.array([
        [0., 0.],
        [3., 0.],
    ])

    v = np.array([
        [1., 0.],
        [-1., 0.],
    ])

    p = BoidsParameters(
        radius_separation=10,
        radius_alignment=10,
        radius_cohesion=10,
        weight_separation=2,
        weight_alignment=0,
        weight_cohesion=0,
    )

    _, new_v = step_boids(xy, v, p)

    assert new_v[0, 0] < 0
    assert new_v[1, 0] > 0

    np.testing.assert_allclose(
        np.linalg.norm(new_v, axis=1),
        [1, 1],
    )


def test_speed_conservation_and_finite_output():
    xy = np.array([
        [0., 0.],
        [10., 3.],
        [-4., 11.],
        [5., 5.],
    ])

    v = np.array([
        [3., 0.],
        [2., 1.],
        [0., -2.],
        [0., 0.],
    ])

    new_xy, new_v = step_boids(xy, v)

    assert np.isfinite(new_xy).all()

    np.testing.assert_allclose(
        np.linalg.norm(new_v, axis=1),
        np.linalg.norm(v, axis=1),
    )


def test_invalid_parameters_or_inputs():
    with pytest.raises(ValueError):
        step_boids(
            np.ones((2, 2)),
            np.ones((2, 2)),
            BoidsParameters(
                rear_blind_angle_deg=360
            ),
        )

    with pytest.raises(ValueError):
        step_boids(
            np.ones((2, 3)),
            np.ones((2, 3)),
        )

    with pytest.raises(ValueError):
        step_boids(
            np.ones((2, 2)),
            np.array([
                [1., 0.],
                [np.nan, 1.],
            ]),
        )
