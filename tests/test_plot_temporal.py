import csv

import pytest

from src.plot_temporal import (
    PLOTS,
    INPUT_CSV,
    load_metrics,
    generate_figures,
)


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "sample_metrics.csv"

    columns = ["frame_id", "time_seconds"] + sorted({
        name
        for _, _, _, series, _ in PLOTS
        for name, _ in series
    })

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            lineterminator="\n",
        )
        writer.writeheader()

        for frame, timestamp in [(251, 8.333), (1, 0.0)]:
            row = {column: 0.6 for column in columns}
            row["frame_id"] = frame
            row["time_seconds"] = timestamp
            row["number_of_fish"] = 200
            writer.writerow(row)

    return path


def test_load_valid_csv(sample_csv):
    print("[TEST] Chargement et tri du CSV", flush=True)

    rows = load_metrics(sample_csv)

    assert len(rows) == 2
    assert [row["frame_id"] for row in rows] == [1, 251]


def test_missing_columns(tmp_path):
    print("[TEST] Détection des colonnes manquantes", flush=True)

    path = tmp_path / "incomplete.csv"
    path.write_text(
        "frame_id,time_seconds\n1,0.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Colonnes absentes"):
        load_metrics(path)


def test_empty_csv(tmp_path, sample_csv):
    print("[TEST] Détection d'un CSV vide", flush=True)

    path = tmp_path / "empty.csv"
    header = sample_csv.read_text(
        encoding="utf-8"
    ).splitlines()[0]

    path.write_text(header + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="aucune observation"):
        load_metrics(path)


def test_nonfinite_values(sample_csv):
    print("[TEST] Détection des valeurs NaN", flush=True)

    text = sample_csv.read_text(encoding="utf-8")
    sample_csv.write_text(
        text.replace("0.6", "nan", 1),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non finies"):
        load_metrics(sample_csv)


def test_png_svg_exports(sample_csv, tmp_path):
    print("[TEST] Génération des dix figures", flush=True)

    outputs = generate_figures(
        csv_path=sample_csv,
        output_dir=tmp_path / "figures",
    )

    assert len(outputs) == 10

    for path in outputs:
        assert path.exists()
        assert path.stat().st_size > 1000

        if path.suffix == ".png":
            assert path.read_bytes().startswith(
                b"\x89PNG\r\n\x1a\n"
            )
        elif path.suffix == ".svg":
            assert "<svg" in path.read_text(encoding="utf-8")


def test_real_dataset_metrics():
    print("[TEST] CSV réel : 21 frames", flush=True)

    rows = load_metrics(INPUT_CSV)

    assert len(rows) == 21
    assert rows[0]["frame_id"] == 1
    assert rows[-1]["frame_id"] == 5000
