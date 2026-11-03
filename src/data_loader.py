from pathlib import Path

import ijson
import numpy as np


REQUIRED_FIELDS = ("px", "py", "vx", "vy", "onfish")


def load_frame(json_path, frame_id=1):
    """Charge et valide une frame expérimentale du banc de poissons."""

    if not isinstance(frame_id, int) or frame_id < 1:
        raise ValueError("Le numéro de frame doit être un entier positif.")

    json_path = Path(json_path)

    with json_path.open("rb") as f:
        frame = next(ijson.items(f, str(frame_id)), None)

    if frame is None:
        raise KeyError(f"Frame {frame_id} introuvable.")

    if any(field not in frame for field in REQUIRED_FIELDS):
        raise ValueError("La frame contient des champs manquants.")

    lengths = [len(frame[field]) for field in REQUIRED_FIELDS]

    if len(set(lengths)) != 1:
        raise ValueError("Les tableaux n'ont pas la même longueur.")

    result = {
        field: np.asarray(frame[field], dtype=float)
        for field in ("px", "py", "vx", "vy")
    }

    result["onfish"] = np.asarray(frame["onfish"], dtype=int)

    if len(np.unique(result["onfish"])) != lengths[0]:
        raise ValueError("Identifiants de poissons dupliqués.")

    for field in ("px", "py", "vx", "vy"):
        if not np.all(np.isfinite(result[field])):
            raise ValueError(f"Valeurs non finies dans {field}.")

    return result


if __name__ == "__main__":
    dataset = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "schooling_frames.json"
    )

    for frame_id in (1, 1000, 2500, 5000):
        frame = load_frame(dataset, frame_id)
        print(f"Frame {frame_id} : {len(frame['onfish'])} poissons")
