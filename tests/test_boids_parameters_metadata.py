import json
from dataclasses import replace

from src.boids_pilot import BoidsParameters
from src.compare_boids_graphs import compare_graphs


def test_boids_parameters_saved_in_metadata(tmp_path):
    ids = [101, 102, 103]

    frames = {}
    for frame_id in range(1, 4):
        frames[frame_id] = {
            "onfish": ids,
            "px": [10.0 + frame_id, 40.0 + frame_id, 70.0 + frame_id],
            "py": [10.0, 20.0, 30.0],
            "vx": [1.0, 1.0, 1.0],
            "vy": [0.0, 0.0, 0.0],
        }

    params = replace(
        BoidsParameters(),
        weight_separation=0.005,
        weight_alignment=0.05,
        weight_cohesion=0.005,
    )

    output = tmp_path / "comparison.json"

    compare_graphs(
        frames=frames,
        horizon=1,
        radius=100,
        parameters=params,
        output=output,
    )

    metadata = json.loads(output.read_text(encoding="utf-8"))["method"]
    saved = metadata["boids_parameters"]

    assert saved["weight_separation"] == 0.005
    assert saved["weight_alignment"] == 0.05
    assert saved["weight_cohesion"] == 0.005
    assert saved["radius_separation"] == params.radius_separation
    assert saved["radius_alignment"] == params.radius_alignment
    assert saved["radius_cohesion"] == params.radius_cohesion
    assert saved["rear_blind_angle_deg"] == params.rear_blind_angle_deg
