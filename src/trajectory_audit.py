"""Audit exploratoire de la continuité d'identifiants dans les données de poissons.

Les observations invalides sont comptabilisées ; elles ne provoquent pas
l'abandon de toute une frame. Aucune identité biologique n'est inférée.
"""
from pathlib import Path
import json
import time

import ijson
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "schooling_frames.json"
OUTPUT = ROOT / "results" / "trajectory" / "continuity_audit.json"
WINDOWS = ((1, 120), (2000, 2119), (4000, 4119))
FIELDS = ("px", "py", "vx", "vy")
FPS = 30


def summarize_numbers(values):
    return {
        "count": len(values),
        "median": float(np.median(values)) if values else None,
        "p90": float(np.percentile(values, 90)) if values else None,
    }


def prepare_observations(raw, frame_id):
    """Sépare les positions utilisables des directions utilisables.

    Les positions ayant px/py non finis sont exclues des associations d'ID.
    Une direction vx/vy non finie n'exclut PAS une position valide ; elle est
    seulement absente de l'analyse de cohérence angulaire.
    """
    expected = (*FIELDS, "onfish")
    absent = [field for field in expected if field not in raw]
    if absent:
        raise ValueError(f"Frame {frame_id} : champs absents {absent}")

    arrays = {field: np.asarray(raw[field], dtype=float) for field in FIELDS}
    try:
        ids = np.asarray(raw["onfish"], dtype=int)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"Frame {frame_id} : IDs non convertibles en entiers") from exc

    lengths = [len(ids), *(len(arrays[field]) for field in FIELDS)]
    if len(set(lengths)) != 1:
        raise ValueError(f"Frame {frame_id} : tableaux de tailles différentes {lengths}")
    if len(np.unique(ids)) != len(ids):
        raise ValueError(f"Frame {frame_id} : identifiants de suivi dupliqués")

    finite = {field: np.isfinite(arrays[field]) for field in FIELDS}
    pos_ok = finite["px"] & finite["py"]
    dir_ok = finite["vx"] & finite["vy"]

    positions = {
        int(ids[i]): np.array([arrays["px"][i], arrays["py"][i]])
        for i in np.flatnonzero(pos_ok)
    }
    directions = {
        int(ids[i]): np.array([arrays["vx"][i], arrays["vy"][i]])
        for i in np.flatnonzero(pos_ok & dir_ok)
    }
    invalid_fields = {
        field: int(np.count_nonzero(~finite[field])) for field in FIELDS
    }

    return {
        "positions": positions,
        "directions": directions,
        "observations": len(ids),
        "excluded_positions": int(np.count_nonzero(~pos_ok)),
        "invalid_directions_with_valid_position": int(np.count_nonzero(pos_ok & ~dir_ok)),
        "invalid_fields": invalid_fields,
    }


def audit_trajectories(dataset=DATASET, output=OUTPUT, windows=WINDOWS):
    started = time.perf_counter()
    print("=== AUDIT DES TRAJECTOIRES EXPÉRIMENTALES ===", flush=True)
    print(f"Fenêtres : {windows} | cadence : {FPS} fps", flush=True)

    stats = {}
    for start, end in windows:
        stats[f"{start}-{end}"] = {
            "start": start,
            "end": end,
            "frames_read": 0,
            "frames_with_nonfinite_values": 0,
            "frames_without_valid_position": 0,
            "invalid_field_counts": {field: 0 for field in FIELDS},
            "excluded_position_rows": 0,
            "invalid_direction_rows_with_valid_position": 0,
            "consecutive_pairs": 0,
            "retentions": [],
            "jaccards": [],
            "displacements": [],
            "direction_cosines": [],
            "example_invalid_frames": [],
        }

    previous = None
    previous_id = None
    previous_window = None
    scanned = 0

    with Path(dataset).open("rb") as stream:
        for frame_key, raw in ijson.kvitems(stream, ""):
            frame_id = int(frame_key)
            scanned += 1
            window = next(
                ((a, b) for a, b in windows if a <= frame_id <= b), None
            )

            if window is None:
                previous = None
                previous_id = None
                previous_window = None
                if scanned % 1000 == 0:
                    print(f"[PROGRESSION] {scanned} frames parcourues", flush=True)
                continue

            start, end = window
            key = f"{start}-{end}"
            current_stats = stats[key]
            current_stats["frames_read"] += 1
            current = prepare_observations(raw, frame_id)

            for field, number in current["invalid_fields"].items():
                current_stats["invalid_field_counts"][field] += number
            current_stats["excluded_position_rows"] += current["excluded_positions"]
            current_stats["invalid_direction_rows_with_valid_position"] += current[
                "invalid_directions_with_valid_position"
            ]

            if any(current["invalid_fields"].values()):
                current_stats["frames_with_nonfinite_values"] += 1
                if len(current_stats["example_invalid_frames"]) < 5:
                    current_stats["example_invalid_frames"].append({
                        "frame_id": frame_id,
                        "invalid_fields": current["invalid_fields"],
                        "excluded_positions": current["excluded_positions"],
                    })
                    print(
                        f"[QUALITÉ] Frame {frame_id} : "
                        f"{current['invalid_fields']} ; "
                        f"positions exclues={current['excluded_positions']}",
                        flush=True,
                    )

            if not current["positions"]:
                current_stats["frames_without_valid_position"] += 1
                previous = None
                previous_id = None
                previous_window = None
                continue

            if (previous is not None and previous_window == window
                    and previous_id == frame_id - 1):
                old_ids = set(previous["positions"])
                new_ids = set(current["positions"])
                common = old_ids & new_ids
                union = old_ids | new_ids
                current_stats["consecutive_pairs"] += 1
                current_stats["retentions"].append(len(common) / len(old_ids))
                current_stats["jaccards"].append(len(common) / len(union))

                for fish_id in common:
                    movement = (
                        current["positions"][fish_id]
                        - previous["positions"][fish_id]
                    )
                    distance = float(np.linalg.norm(movement))
                    current_stats["displacements"].append(distance)

                    direction = previous["directions"].get(fish_id)
                    if direction is None:
                        continue
                    norm = float(np.linalg.norm(direction))
                    if distance > 0 and norm > 0:
                        cosine = float(np.dot(movement, direction) / (distance * norm))
                        current_stats["direction_cosines"].append(
                            float(np.clip(cosine, -1, 1))
                        )

            previous = current
            previous_id = frame_id
            previous_window = window

            if frame_id == end:
                print(f"[OK] Fenêtre {key} : {current_stats['frames_read']} frames", flush=True)
            if scanned % 1000 == 0:
                print(f"[PROGRESSION] {scanned} frames parcourues", flush=True)

    print("[SYNTHÈSE]", flush=True)
    summary = {"fps": FPS, "coordinate_units": "native", "windows": {}}
    for key, item in stats.items():
        expected = item["end"] - item["start"] + 1
        if item["frames_read"] != expected:
            raise ValueError(
                f"Fenêtre {key} incomplète : {item['frames_read']}/{expected} frames"
            )
        result = {
            "frames": item["frames_read"],
            "consecutive_pairs": item["consecutive_pairs"],
            "frames_with_nonfinite_values": item["frames_with_nonfinite_values"],
            "frames_without_valid_position": item["frames_without_valid_position"],
            "invalid_field_counts": item["invalid_field_counts"],
            "excluded_position_rows": item["excluded_position_rows"],
            "invalid_direction_rows_with_valid_position": item[
                "invalid_direction_rows_with_valid_position"
            ],
            "mean_retention_valid_positions": (
                float(np.mean(item["retentions"])) if item["retentions"] else None
            ),
            "mean_jaccard_valid_positions": (
                float(np.mean(item["jaccards"])) if item["jaccards"] else None
            ),
            "displacement_per_frame": summarize_numbers(item["displacements"]),
            "direction_cosine": summarize_numbers(item["direction_cosines"]),
            "example_invalid_frames": item["example_invalid_frames"],
        }
        summary["windows"][key] = result
        print(f"\n=== FENÊTRE {key} ===", flush=True)
        for name, value in result.items():
            print(f"{name}: {value}", flush=True)

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n[OK] Résultat : {output}", flush=True)
    print(f"[TERMINÉ] Durée : {time.perf_counter() - started:.2f} s", flush=True)
    return summary


if __name__ == "__main__":
    audit_trajectories()
