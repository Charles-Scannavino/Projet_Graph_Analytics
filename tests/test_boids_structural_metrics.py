import numpy as np
import pytest

from src.boids_structural_metrics import (
    nearest_neighbor_distances,
    spatial_degrees,
)


def test_nearest_neighbor_distances():
    xy = np.array([
        [0.0, 0.0],
        [3.0, 0.0],
        [0.0, 4.0],
    ])

    result = nearest_neighbor_distances(xy)

    np.testing.assert_allclose(result, [3.0, 3.0, 4.0])


def test_spatial_degrees():
    xy = np.array([
        [0.0, 0.0],
        [3.0, 0.0],
        [0.0, 4.0],
    ])

    result = spatial_degrees(xy, radius=4.5)

    np.testing.assert_array_equal(result, [2, 1, 1])


def test_isolated_nodes():
    xy = np.array([
        [0.0, 0.0],
        [100.0, 0.0],
        [200.0, 0.0],
    ])

    result = spatial_degrees(xy, radius=50)

    np.testing.assert_array_equal(result, [0, 0, 0])


def test_invalid_radius():
    xy = np.array([[0.0, 0.0], [1.0, 0.0]])

    with pytest.raises(ValueError):
        spatial_degrees(xy, radius=0)


def test_single_fish_nearest_neighbor():
    with pytest.raises(ValueError):
        nearest_neighbor_distances(np.array([[0.0, 0.0]]))


def test_invalid_positions():
    xy = np.array([
        [0.0, 0.0],
        [np.nan, 1.0],
    ])

    with pytest.raises(ValueError):
        spatial_degrees(xy)
