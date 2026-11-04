from pathlib import Path
import argparse
import csv
import time

import ijson
import networkx as nx
import numpy as np

from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph
from src.community_detection import detect_communities


BLIND_ANGLE_DEG = 25
FPS = 30
TOTAL_FRAMES = 5000


def convert_frame(raw):
    """Convertit et valide une frame lue en streaming."""
    fields = ("px", "py", "vx", "vy", "onfish")

    if any(field not in raw for field in fields):
        raise ValueError("Champs manquants dans une frame.")

    frame = {
        field: np.asarray(raw[field], dtype=float)
        for field in ("px", "py", "vx", "vy")
    }
    frame["onfish"] = np.asarray(raw["onfish"], dtype=int)

    sizes = [len(frame[field]) for field in fields]

    if len(set(sizes)) != 1 or sizes[0] == 0:
        raise ValueError("Frame vide ou tableaux incohérents.")

    if len(np.unique(frame["onfish"])) != sizes[0]:
        raise ValueError("Identifiants dupliqués.")

    if not all(
        np.all(np.isfinite(frame[field]))
        for field in ("px", "py", "vx", "vy")
    ):
        raise ValueError("Coordonnées ou directions non finies.")

    return frame


def analyze_frame(frame_id, frame, radius=100):
    """Calcule les indicateurs des deux graphes pour une frame."""

    spatial = build_graph(frame, radius=radius)
    visibility = build_visibility_graph(
        frame,
        radius=radius,
        rear_blind_angle_deg=BLIND_ANGLE_DEG,
    )

    spatial_louvain = detect_communities(spatial)
    visibility_louvain = detect_communities(visibility)

    n = spatial.number_of_nodes()
    m = spatial.number_of_edges()
    arcs = visibility.number_of_edges()

    spatial_components = list(nx.connected_components(spatial))
    strong_components = list(
        nx.strongly_connected_components(visibility)
    )

    return {
        "frame_id": frame_id,
        "time_seconds": round((frame_id - 1) / FPS, 3),
        "number_of_fish": n,

        "spatial_edges": m,
        "spatial_components": len(spatial_components),
        "spatial_largest_component_share": round(
            max(map(len, spatial_components)) / n, 5
        ),
        "spatial_average_degree": round(2 * m / n, 5),
        "spatial_density": round(nx.density(spatial), 5),
        "spatial_clustering": round(
            nx.average_clustering(spatial), 5
        ),
        "spatial_communities": (
            spatial_louvain["number_of_communities"]
        ),
        "spatial_modularity": spatial_louvain["modularity"],

        "visibility_arcs": arcs,
        "visibility_weak_components": (
            nx.number_weakly_connected_components(visibility)
        ),
        "visibility_strong_components": len(strong_components),
        "visibility_largest_scc_share": round(
            max(map(len, strong_components)) / n, 5
        ),
        "visibility_average_out_degree": round(arcs / n, 5),
        "visibility_density": round(nx.density(visibility), 5),
        "visibility_clustering": round(
            nx.average_clustering(visibility), 5
        ),
        "visibility_communities": (
            visibility_louvain["number_of_communities"]
        ),
        "visibility_modularity": visibility_louvain["modularity"],

        "visible_arc_fraction": (
            round(arcs / (2 * m), 5) if m else None
        ),
    }


def run_analysis(dataset, output, step=250, radius=100):
    if step <= 0:
        raise ValueError("Le pas doit être positif.")
    if radius <= 0:
        raise ValueError("Le rayon doit être positif.")

    start = time.perf_counter()

    selected = set(range(1, TOTAL_FRAMES + 1, step))
    selected.add(TOTAL_FRAMES)

    print("=== ANALYSE TEMPORELLE GRAPH ANALYTICS ===", flush=True)
    print(f"Frames sélectionnées : {len(selected)}", flush=True)
    print(f"Rayon : {radius}", flush=True)
    print(f"Angle mort fixe : {BLIND_ANGLE_DEG}°", flush=True)
    print("[1/3] Lecture streaming du dataset...", flush=True)

    rows = []
    scanned = 0

    with Path(dataset).open("rb") as stream:
        for frame_key, raw in ijson.kvitems(stream, ""):
            frame_id = int(frame_key)
            scanned += 1

            if frame_id in selected:
                frame = convert_frame(raw)
                row = analyze_frame(frame_id, frame, radius)
                rows.append(row)

                print(
                    f"[FRAME {frame_id}/{TOTAL_FRAMES}] "
                    f"{row['number_of_fish']} poissons | "
                    f"{row['spatial_communities']} communautés "
                    f"spatiales | "
                    f"{row['visibility_communities']} communautés "
                    f"de visibilité",
                    flush=True,
                )

            if scanned % 500 == 0:
                print(
                    f"[PROGRESSION] {scanned}/{TOTAL_FRAMES} "
                    f"frames parcourues",
                    flush=True,
                )

    if {row["frame_id"] for row in rows} != selected:
        raise ValueError("Certaines frames sélectionnées sont absentes.")

    rows.sort(key=lambda row: row["frame_id"])

    print("[2/3] Export CSV...", flush=True)

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("[3/3] Résumé...", flush=True)
    print(f"Frames analysées : {len(rows)}", flush=True)
    print(f"Résultat : {output}", flush=True)
    print(
        f"Durée : {time.perf_counter() - start:.2f} secondes",
        flush=True,
    )
    print("[OK] Analyse temporelle terminée.", flush=True)

    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=int, default=250)
    parser.add_argument("--radius", type=float, default=100)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]

    run_analysis(
        dataset=root / "data" / "schooling_frames.json",
        output=(
            root / "results" / "temporal"
            / f"metrics_step{args.step}_R{args.radius:g}.csv"
        ),
        step=args.step,
        radius=args.radius,
    )
