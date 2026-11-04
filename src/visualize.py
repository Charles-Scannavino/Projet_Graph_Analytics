from pathlib import Path
import time

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

from src.data_loader import load_frame
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph
from src.community_detection import detect_communities


# Palette de couleurs : communautés classées par taille.
COLOR_ORDER = [
    0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
    1, 3, 5, 7, 9, 11, 13, 15, 17, 19,
]


def plot_communities(G, results, output_png, title):
    """
    Visualise les communautés Louvain avec les positions réelles.

    - Les sommets représentent les poissons.
    - Les couleurs représentent les communautés.
    - Les liens sont affichés en arrière-plan.
    - Les arcs orientés sont tracés sans flèche pour éviter
      de surcharger la figure.
    """

    if G.number_of_nodes() == 0:
        raise ValueError("Impossible de visualiser un graphe vide.")

    membership = results["membership"]

    if set(membership) != {str(node) for node in G.nodes()}:
        raise ValueError(
            "La partition Louvain ne correspond pas aux sommets."
        )

    positions = {
        node: G.nodes[node]["pos"]
        for node in G.nodes()
    }

    coordinates = np.array(list(positions.values()), dtype=float)

    if coordinates.shape != (G.number_of_nodes(), 2):
        raise ValueError("Positions 2D invalides.")

    fig, ax = plt.subplots(figsize=(12.5, 7.5))

    # Dessiner les liens avec une faible opacité.
    segments = [
        [positions[source], positions[target]]
        for source, target in G.edges()
    ]

    if segments:
        edges = LineCollection(
            segments,
            colors="#526179",
            linewidths=0.5,
            alpha=0.10 if not G.is_directed() else 0.06,
            zorder=1,
        )
        ax.add_collection(edges)

    cmap = plt.get_cmap("tab20")
    colors = [cmap.colors[i] for i in COLOR_ORDER]

    # Colorier les poissons selon leur communauté.
    for community_id in range(
        1, results["number_of_communities"] + 1
    ):
        nodes = [
            node
            for node in G.nodes()
            if membership[str(node)] == community_id
        ]

        if not nodes:
            raise ValueError("Une communauté est vide.")

        xy = np.array([positions[node] for node in nodes])

        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=34,
            color=colors[(community_id - 1) % len(colors)],
            edgecolors="white",
            linewidths=0.3,
            label=f"C{community_id} — {len(nodes)} poissons",
            zorder=3,
        )

    # Appliquer des limites identiques pour les deux graphes,
    # puisque leurs positions expérimentales sont identiques.
    x_values = coordinates[:, 0]
    y_values = coordinates[:, 1]

    x_padding = max(float(np.ptp(x_values)) * 0.06, 1.0)
    y_padding = max(float(np.ptp(y_values)) * 0.06, 1.0)

    ax.set_xlim(
        float(x_values.min()) - x_padding,
        float(x_values.max()) + x_padding,
    )
    ax.set_ylim(
        float(y_values.min()) - y_padding,
        float(y_values.max()) + y_padding,
    )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Position X (unités natives)")
    ax.set_ylabel("Position Y (unités natives)")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=18)
    ax.grid(alpha=0.15, linewidth=0.5)

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        title="Communautés Louvain",
        fontsize=9,
        frameon=False,
    )

    modularity = results["modularity"]
    radius = G.graph.get("radius")

    modularity_label = (
        f"{modularity:.5f}"
        if modularity is not None else "N/A"
    )
    radius_label = f"{radius:g}" if radius is not None else "N/A"

    info = (
        f"{G.number_of_nodes()} poissons | "
        f"{G.number_of_edges()} liens | "
        f"R={radius_label} | "
        f"Q={modularity_label}"
    )

    fig.text(0.10, 0.055, info, fontsize=9, color="#444444")

    if G.is_directed():
        fig.text(
            0.10,
            0.025,
            "Graphe orienté : arcs affichés sans flèches "
            "pour faciliter la lecture.",
            fontsize=8,
            color="#666666",
        )

    fig.subplots_adjust(
        left=0.10,
        right=0.73,
        top=0.89,
        bottom=0.15,
    )

    output_png = Path(output_png)
    output_png.parent.mkdir(parents=True, exist_ok=True)

    output_svg = output_png.with_suffix(".svg")

    fig.savefig(output_png, dpi=220, bbox_inches="tight")
    fig.savefig(output_svg, bbox_inches="tight")

    plt.close(fig)

    return output_png, output_svg


def main():
    start = time.perf_counter()

    root = Path(__file__).resolve().parents[1]
    dataset = root / "data" / "schooling_frames.json"
    figures = root / "results" / "figures"

    print("[1/7] Chargement de la frame 1...", flush=True)
    frame = load_frame(dataset, frame_id=1)

    print("[2/7] Construction du graphe spatial...", flush=True)
    spatial = build_graph(frame, radius=100)

    print("[3/7] Construction du graphe de visibilité...", flush=True)
    visibility = build_visibility_graph(
        frame,
        radius=100,
        rear_blind_angle_deg=25,
    )

    print("[4/7] Calcul des communautés spatiales...", flush=True)
    spatial_results = detect_communities(spatial)

    print("[5/7] Calcul des communautés de visibilité...", flush=True)
    visibility_results = detect_communities(visibility)

    print("[6/7] Création de la figure spatiale...", flush=True)
    spatial_files = plot_communities(
        spatial,
        spatial_results,
        figures / "frame1_spatial_louvain.png",
        "Frame 1 — Communautés du graphe spatial",
    )

    print("[7/7] Création de la figure de visibilité...", flush=True)
    visibility_files = plot_communities(
        visibility,
        visibility_results,
        figures / "frame1_visibility25_louvain.png",
        "Frame 1 — Communautés du graphe de visibilité (25°)",
    )

    print("\n=== FIGURES GÉNÉRÉES ===", flush=True)

    for path in (*spatial_files, *visibility_files):
        print(f"  {path}", flush=True)

    print(
        f"\n[OK] Visualisations terminées en "
        f"{time.perf_counter() - start:.2f} s.",
        flush=True,
    )


if __name__ == "__main__":
    main()
