import csv

import pytest

from src.sensitivity_analysis import (
    ROOT,
    RADII,
    METRICS,
    load_csv,
    summarize,
    plot_sensitivity,
)


def make_csv(path, fish=(3, 3), duplicate=False, nan=False):
    """Crée un CSV de test avec deux frames contrôlées."""
    columns = ["frame_id", "time_seconds", *METRICS]
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=columns, lineterminator="\n"
        )
        writer.writeheader()

        for index, (frame_id, t) in enumerate(
            [(1, 0.0), (251, 8.333)]
        ):
            row = {metric: 0.5 for metric in METRICS}
            row.update({
                "frame_id": 1 if duplicate else frame_id,
                "time_seconds": t,
                "number_of_fish": fish[index],
                "spatial_communities": 2 + 2 * index,
                "visibility_communities": 3 + 2 * index,
            })

            if nan and index == 0:
                row["spatial_density"] = float("nan")

            writer.writerow(row)


@pytest.fixture
def sample_inputs(tmp_path):
    folder = tmp_path / "inputs"

    for radius in RADII:
        make_csv(folder / f"metrics_step250_R{radius}.csv")

    return folder


def test_summary_and_means(sample_inputs, tmp_path):
    print("[TEST] Synthèse des cinq rayons", flush=True)

    results = summarize(sample_inputs, tmp_path / "summary")

    assert len(results) == 5
    assert [row["radius"] for row in results] == list(RADII)
    assert all(row["frames"] == 2 for row in results)
    assert results[0]["mean_spatial_communities"] == 3
    assert results[0]["mean_visibility_communities"] == 4
    assert (tmp_path / "summary/summary_step250.csv").is_file()


def test_inconsistent_fish(sample_inputs, tmp_path):
    print("[TEST] Poissons incohérents entre rayons", flush=True)

    make_csv(
        sample_inputs / "metrics_step250_R120.csv",
        fish=(4, 3),
    )

    with pytest.raises(ValueError, match="incohérents"):
        summarize(sample_inputs, tmp_path / "output")


def test_missing_radius(sample_inputs, tmp_path):
    print("[TEST] Fichier d'un rayon absent", flush=True)

    (sample_inputs / "metrics_step250_R80.csv").unlink()

    with pytest.raises(FileNotFoundError):
        summarize(sample_inputs, tmp_path / "output")


def test_missing_columns(tmp_path):
    print("[TEST] Colonnes manquantes", flush=True)

    path = tmp_path / "missing.csv"
    path.write_text(
        "frame_id,time_seconds\n1,0.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="colonnes absentes"):
        load_csv(path)


def test_duplicate_frames(tmp_path):
    print("[TEST] Frames dupliquées", flush=True)

    path = tmp_path / "duplicate.csv"
    make_csv(path, duplicate=True)

    with pytest.raises(ValueError, match="Frames dupliquées"):
        load_csv(path)


def test_nonfinite_values(tmp_path):
    print("[TEST] Valeurs NaN", flush=True)

    path = tmp_path / "nan.csv"
    make_csv(path, nan=True)

    with pytest.raises(ValueError, match="Valeur non finie"):
        load_csv(path)


def test_empty_csv(tmp_path):
    print("[TEST] CSV sans observations", flush=True)

    path = tmp_path / "empty.csv"
    path.write_text(
        ",".join(["frame_id", "time_seconds", *METRICS])
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="CSV vide"):
        load_csv(path)


def test_figure_exports(sample_inputs, tmp_path):
    print("[TEST] Dix figures PNG/SVG", flush=True)

    results = summarize(sample_inputs, tmp_path / "summary")
    outputs = plot_sensitivity(
        results, tmp_path / "figures"
    )

    assert len(outputs) == 10

    for path in outputs:
        assert path.is_file()
        assert path.stat().st_size > 1000

        if path.suffix == ".png":
            assert path.read_bytes().startswith(
                b"\x89PNG\r\n\x1a\n"
            )
        elif path.suffix == ".svg":
            assert "<svg" in path.read_text(encoding="utf-8")


def test_real_sensitivity_results(tmp_path):
    print("[TEST] Cinq CSV expérimentaux", flush=True)

    results = summarize(
        ROOT / "results/temporal",
        tmp_path / "summary",
    )

    assert len(results) == 5
    assert all(row["frames"] == 21 for row in results)

    assert results[0]["mean_spatial_communities"] == pytest.approx(
        29.76, abs=0.01
    )
    assert results[2]["mean_spatial_density"] == pytest.approx(
        0.0609, abs=0.0001
    )

    print("[OK] Analyse réelle cohérente", flush=True)
