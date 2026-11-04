import csv
import json

import numpy as np
import pytest

from src.temporal_analysis import (
    BLIND_ANGLE_DEG,
    convert_frame,
    analyze_frame,
    run_analysis,
)


def sample_raw():
    return {
        "px": [0.0, 10.0, 300.0],
        "py": [0.0, 0.0, 0.0],
        "vx": [1.0, 1.0, 1.0],
        "vy": [0.0, 0.0, 0.0],
        "onfish": [10, 11, 12],
    }


def test_convert_frame():
    print("[TEST] Conversion des observations", flush=True)

    frame = convert_frame(sample_raw())

    assert len(frame["onfish"]) == 3
    assert frame["px"].dtype == np.float64
    assert list(frame["onfish"]) == [10, 11, 12]


def test_invalid_frame():
    print("[TEST] Validation des données", flush=True)

    raw = sample_raw()
    raw["px"] = [0.0]

    with pytest.raises(ValueError):
        convert_frame(raw)

    raw = sample_raw()
    raw["onfish"] = [10, 10, 12]

    with pytest.raises(ValueError):
        convert_frame(raw)


def test_temporal_graph_metrics():
    print("[TEST] Métriques sur graphe contrôlé", flush=True)

    assert BLIND_ANGLE_DEG == 25

    frame = convert_frame(sample_raw())
    result = analyze_frame(1, frame, radius=100)

    assert result["number_of_fish"] == 3
    assert result["spatial_edges"] == 1
    assert result["spatial_components"] == 2
    assert result["spatial_largest_component_share"] == pytest.approx(
        2 / 3, abs=1e-5
    )

    assert result["visibility_arcs"] == 1
    assert result["visibility_weak_components"] == 2
    assert result["visibility_strong_components"] == 3
    assert result["visible_arc_fraction"] == 0.5


def test_streaming_and_csv(tmp_path):
    print("[TEST] Lecture streaming et export CSV", flush=True)

    dataset = tmp_path / "sample.json"
    output = tmp_path / "results" / "temporal.csv"

    dataset.write_text(
        json.dumps({
            "1": sample_raw(),
            "2501": sample_raw(),
            "5000": sample_raw(),
        }),
        encoding="utf-8",
    )

    rows = run_analysis(
        dataset=dataset,
        output=output,
        step=2500,
        radius=100,
    )

    assert len(rows) == 3
    assert [row["frame_id"] for row in rows] == [
        1, 2501, 5000
    ]

    assert output.is_file()

    with output.open(newline="", encoding="utf-8") as file:
        saved = list(csv.DictReader(file))

    assert len(saved) == 3
    assert saved[0]["frame_id"] == "1"
    assert saved[0]["number_of_fish"] == "3"

    print("[OK] Streaming et CSV validés", flush=True)


def test_missing_selected_frame(tmp_path):
    print("[TEST] Détection des frames absentes", flush=True)

    dataset = tmp_path / "incomplete.json"
    output = tmp_path / "missing.csv"

    dataset.write_text(
        json.dumps({"1": sample_raw()}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="absentes"):
        run_analysis(dataset, output, step=5000)

    assert not output.exists()


@pytest.mark.parametrize(
    "step,radius",
    [(0, 100), (5000, 0)],
)
def test_invalid_parameters(tmp_path, step, radius):
    print("[TEST] Validation des paramètres", flush=True)

    with pytest.raises(ValueError):
        run_analysis(
            dataset=tmp_path / "unused.json",
            output=tmp_path / "unused.csv",
            step=step,
            radius=radius,
        )
