from pathlib import Path

import networkx as nx
import numpy as np
from scipy.spatial.distance import pdist, squareform

from src.data_loader import load_frame


def build_graph(frame, radius=100):
    """
    Construit un graphe de proximité non orienté
    à partir d'une frame expérimentale.
    """

    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("Le rayon doit être strictement positif.")

    ids = frame["onfish"]
    positions = np.column_stack((frame["px"], frame["py"]))

    if len(ids) != len(positions):
        raise ValueError("Nombre de positions et d'identifiants incohérent.")

    if len(set(map(int, ids))) != len(ids):
        raise ValueError("Identifiants dupliqués.")

    G = nx.Graph()
    G.graph["radius"] = float(radius)

    # Ajouter tous les poissons, y compris les poissons isolés
    for i, fish_id in enumerate(ids):
        G.add_node(
            int(fish_id),
            pos=(float(frame["px"][i]), float(frame["py"][i])),
            direction=(float(frame["vx"][i]), float(frame["vy"][i]))
        )

    # Calculer les distances entre poissons
    if len(ids) >= 2:
        distances = squareform(pdist(positions))

        # Paires distinctes dont la distance est < radius
        ii, jj = np.where(np.triu(distances < radius, k=1))

        for i, j in zip(ii, jj):
            G.add_edge(
                int(ids[i]),
                int(ids[j]),
                distance=float(distances[i, j])
            )

    return G


if __name__ == "__main__":
    dataset = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "schooling_frames.json"
    )

    frame = load_frame(dataset, frame_id=1)

    for radius in (60, 100, 120):
        G = build_graph(frame, radius=radius)

        composantes = list(nx.connected_components(G))
        plus_grande = max(composantes, key=len)

        print(f"\n=== FRAME 1 / R = {radius} ===")
        print("Nombre de noeuds :", G.number_of_nodes())
        print("Nombre d'aretes :", G.number_of_edges())
        print("Nombre de composantes :", len(composantes))
        print("Plus grande composante :", len(plus_grande))
        print("Degre moyen :", round(
            2 * G.number_of_edges() / G.number_of_nodes(), 2
        ))
