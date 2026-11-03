from pathlib import Path

import networkx as nx
import pytest

from src.data_loader import load_frame
from src.graph_builder import build_graph
from src.visibility_graph import build_visibility_graph
from src.graph_metrics import analyze_graph


def test_undirected_graph_with_isolate():
    G = nx.path_graph(3)
    G.add_node(99)

    m = analyze_graph(G)

    assert m["nodes"] == 4
    assert m["edges"] == 2
    assert m["connected_components"] == 2
    assert m["largest_component_size"] == 3
    assert m["largest_component_share"] == 0.75
    assert m["diameter_largest_component_hops"] == 2
    assert m["radius_largest_component_hops"] == 1


def test_directed_cycle():
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1)])

    m = analyze_graph(G)

    assert m["arcs"] == 3
    assert m["weak_components"] == 1
    assert m["strong_components"] == 1
    assert m["diameter_largest_component_hops"] == 2
    assert m["radius_largest_component_hops"] == 2
    assert m["average_in_degree"] == 1
    assert m["average_out_degree"] == 1


def test_directed_chain():
    G = nx.DiGraph([(1, 2), (2, 3)])
    m = analyze_graph(G)

    assert m["weak_components"] == 1
    assert m["strong_components"] == 3
    assert m["largest_component_size"] == 1
    assert m["diameter_largest_component_hops"] == 0
    assert m["radius_largest_component_hops"] == 0


def test_empty_graph():
    with pytest.raises(ValueError):
        analyze_graph(nx.Graph())


def test_real_frame_metrics():
    dataset = (
        Path(__file__).resolve().parents[1]
        / "data" / "schooling_frames.json"
    )

    if not dataset.is_file():
        pytest.skip("Dataset expérimental absent.")

    print("\n[1/3] Chargement des observations...", flush=True)
    frame = load_frame(dataset, 1)

    print("[2/3] Calcul des métriques spatiales...", flush=True)
    spatial = analyze_graph(build_graph(frame, radius=100))

    assert spatial["nodes"] == 253
    assert spatial["edges"] == 1281
    assert spatial["connected_components"] == 4
    assert spatial["largest_component_size"] == 248
    assert spatial["diameter_largest_component_hops"] == 23
    assert spatial["radius_largest_component_hops"] == 12
    assert spatial["average_clustering"] == pytest.approx(0.578)

    print("[3/3] Calcul des métriques de visibilité...", flush=True)
    G = build_visibility_graph(
        frame, radius=100, rear_blind_angle_deg=25
    )
    visible = analyze_graph(G)

    assert G.graph["rear_blind_angle_deg"] == 25
    assert visible["arcs"] == 2386
    assert visible["weak_components"] == 4
    assert visible["strong_components"] == 4
    assert visible["largest_component_size"] == 248
    assert visible["diameter_largest_component_hops"] == 24
    assert visible["radius_largest_component_hops"] == 12
    assert visible["average_clustering"] == pytest.approx(0.54551)

    print("[OK] Métriques de la frame 1 validées.", flush=True)
