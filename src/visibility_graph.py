from pathlib import Path
import math

import networkx as nx

from src.data_loader import load_frame
from src.graph_builder import build_graph


def build_visibility_graph(frame, radius=100, rear_blind_angle_deg=25):
    """
    Construit un graphe orienté de visibilité.

    Une arête i -> j existe si :
    - les deux poissons sont à une distance < radius ;
    - j se trouve hors du secteur aveugle arrière de i.

    rear_blind_angle_deg représente la largeur TOTALE
    du secteur aveugle centré derrière le poisson.
    """

    if not 0 <= rear_blind_angle_deg < 360:
        raise ValueError(
            "L'angle mort doit être compris entre 0 et 360 degrés exclus."
        )

    # Graphe spatial de référence
    spatial_graph = build_graph(frame, radius=radius)

    # Graphe orienté de visibilité
    G = nx.DiGraph()
    G.add_nodes_from(spatial_graph.nodes(data=True))

    G.graph["radius"] = float(radius)
    G.graph["rear_blind_angle_deg"] = float(rear_blind_angle_deg)

    visible_half_angle = math.radians(
        180 - rear_blind_angle_deg / 2
    )

    def can_see(source, target):
        x1, y1 = G.nodes[source]["pos"]
        x2, y2 = G.nodes[target]["pos"]

        vx, vy = G.nodes[source]["direction"]

        if math.hypot(vx, vy) == 0:
            return False

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return False

        heading = math.atan2(vy, vx)
        bearing = math.atan2(dy, dx)

        # Différence angulaire entre -pi et pi
        delta = math.atan2(
            math.sin(bearing - heading),
            math.cos(bearing - heading)
        )

        return abs(delta) <= visible_half_angle

    for i, j, attributes in spatial_graph.edges(data=True):
        distance = attributes["distance"]

        if can_see(i, j):
            G.add_edge(i, j, distance=distance)

        if can_see(j, i):
            G.add_edge(j, i, distance=distance)

    return G


if __name__ == "__main__":
    dataset = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "schooling_frames.json"
    )

    frame = load_frame(dataset, frame_id=1)

    for blind_angle in (25,):
        G = build_visibility_graph(
            frame,
            radius=100,
            rear_blind_angle_deg=blind_angle
        )

        print(f"\n=== VISIBILITÉ / ANGLE MORT = {blind_angle}° ===")
        print("Nombre de noeuds :", G.number_of_nodes())
        print("Nombre d'arcs :", G.number_of_edges())
        print(
            "Composantes faiblement connexes :",
            nx.number_weakly_connected_components(G)
        )
        print(
            "Composantes fortement connexes :",
            nx.number_strongly_connected_components(G)
        )
