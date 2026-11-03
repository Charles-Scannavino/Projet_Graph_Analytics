from pathlib import Path

import networkx as nx
import pytest

from src.data_loader import load_frame
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph
from src.community_detection import detect_communities


def verify_partition(G, result):
    """Vérifie que chaque sommet appartient à une seule communauté."""

    membership = result["membership"]
    sizes = result["community_sizes"]
    k = result["number_of_communities"]

    assert len(membership) == G.number_of_nodes()
    assert set(membership) == {str(n) for n in G.nodes()}
    assert sum(sizes) == G.number_of_nodes()
    assert len(sizes) == k
    assert set(membership.values()) == set(range(1, k + 1))
    assert sizes == sorted(sizes, reverse=True)


def test_empty_graph():
    with pytest.raises(ValueError):
        detect_communities(nx.Graph())


def test_graph_without_edges():
    G = nx.empty_graph(3)
    result = detect_communities(G)

    verify_partition(G, result)

    assert result["number_of_communities"] == 3
    assert result["community_sizes"] == [1, 1, 1]
    assert result["modularity"] is None


def test_undirected_graph():
    G = nx.Graph()
    G.add_edges_from([
        (1, 2), (2, 3), (3, 1),
        (4, 5), (5, 6), (6, 4),
    ])
    G.add_node(7)

    result = detect_communities(G)

    verify_partition(G, result)
    assert result["graph_type"] == "undirected"
    assert result["modularity"] is not None


def test_directed_graph_reproducibility():
    G = nx.DiGraph()
    G.add_edges_from([
        (1, 2), (2, 3), (3, 1),
        (4, 5), (5, 6), (6, 4),
        (3, 4),
    ])

    first = detect_communities(G, seed=42)
    second = detect_communities(G, seed=42)

    verify_partition(G, first)

    assert first["graph_type"] == "directed"
    assert first == second


def test_real_frame_communities():
    dataset = (
        Path(__file__).resolve().parents[1]
        / "data" / "schooling_frames.json"
    )

    if not dataset.is_file():
        pytest.skip("Dataset expérimental absent.")

    print("\n[1/3] Chargement de la frame 1...", flush=True)
    frame = load_frame(dataset, frame_id=1)

    print("[2/3] Louvain sur le graphe spatial...", flush=True)
    spatial = build_graph(frame, radius=100)
    result_spatial = detect_communities(spatial)

    verify_partition(spatial, result_spatial)

    assert result_spatial["number_of_communities"] == 11
    assert result_spatial["modularity"] == pytest.approx(0.70344)
    assert result_spatial["community_sizes"] == [
        64, 47, 38, 30, 27, 26, 11, 5, 3, 1, 1
    ]

    print("[3/3] Louvain sur le graphe de visibilité...", flush=True)
    visibility = build_visibility_graph(
        frame,
        radius=100,
        rear_blind_angle_deg=25,
    )
    result_visibility = detect_communities(visibility)

    verify_partition(visibility, result_visibility)

    assert result_visibility["number_of_communities"] == 10
    assert result_visibility["modularity"] == pytest.approx(0.705)
    assert result_visibility["community_sizes"] == [
        65, 43, 38, 37, 30, 30, 5, 3, 1, 1
    ]

    print("[OK] Communautés Louvain validées.", flush=True)
