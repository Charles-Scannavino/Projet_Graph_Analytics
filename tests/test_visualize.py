import networkx as nx
import pytest

from src.visualize import plot_communities


def make_graph(directed=False):
    G = nx.DiGraph() if directed else nx.Graph()
    G.graph["radius"] = 100.0

    for node, pos in {
        1: (0.0, 0.0),
        2: (1.0, 1.0),
        3: (8.0, 8.0),
        4: (9.0, 9.0),
    }.items():
        G.add_node(node, pos=pos)

    G.add_edges_from([(1, 2), (3, 4)])
    return G


def partition():
    return {
        "membership": {"1": 1, "2": 1, "3": 2, "4": 2},
        "number_of_communities": 2,
        "modularity": 0.5,
    }


def verify_files(paths):
    png, svg = paths

    assert png.is_file()
    assert svg.is_file()

    assert png.stat().st_size > 1000
    assert svg.stat().st_size > 1000

    assert png.read_bytes().startswith(b"\x89PNG")
    assert "<svg" in svg.read_text(encoding="utf-8")[:2000]


def test_empty_graph(tmp_path):
    print("[TEST] Graphe vide", flush=True)
    with pytest.raises(ValueError, match="vide"):
        plot_communities(
            nx.Graph(), {}, tmp_path / "empty.png", "Vide"
        )


def test_invalid_membership(tmp_path):
    print("[TEST] Partition incohérente", flush=True)
    G = make_graph()
    result = partition()
    result["membership"].pop("4")

    with pytest.raises(ValueError, match="partition"):
        plot_communities(
            G, result, tmp_path / "invalid.png", "Erreur"
        )


def test_spatial_figure(tmp_path):
    print("[TEST] Figure spatiale PNG/SVG", flush=True)
    paths = plot_communities(
        make_graph(),
        partition(),
        tmp_path / "spatial.png",
        "Graphe spatial",
    )
    verify_files(paths)


def test_directed_figure(tmp_path):
    print("[TEST] Figure orientée PNG/SVG", flush=True)
    paths = plot_communities(
        make_graph(directed=True),
        partition(),
        tmp_path / "visibility.png",
        "Graphe de visibilité",
    )
    verify_files(paths)


def test_graph_without_edges(tmp_path):
    print("[TEST] Graphe sans arêtes", flush=True)

    G = nx.Graph()
    G.graph["radius"] = 100
    G.add_node(1, pos=(0.0, 0.0))
    G.add_node(2, pos=(1.0, 1.0))

    result = {
        "membership": {"1": 1, "2": 2},
        "number_of_communities": 2,
        "modularity": None,
    }

    paths = plot_communities(
        G,
        result,
        tmp_path / "isolates.png",
        "Poissons isolés",
    )
    verify_files(paths)
