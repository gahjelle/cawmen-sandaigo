"""Loading a Scenario's Location Graph from its authored graph.toml."""

from pathlib import Path

from cawmen_backend.shell.scenario import load_location_graph

SCENARIOS = Path(__file__).resolve().parents[3] / "scenarios"


def test_loads_the_authored_locations_in_order() -> None:
    """The loader preserves the Locations in their authored order."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    assert [location.id for location in graph.locations if not location.escape] == [
        "paris",
        "rome",
        "madrid",
        "berlin",
        "london",
        "oslo",
    ]


def test_escape_location_is_distinguished() -> None:
    """The Escape Location is loaded but marked so the API can exclude it."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    escape = next(loc for loc in graph.locations if loc.escape)
    assert escape.id == "escape"


def test_loads_undirected_connections_and_expands_symmetrically() -> None:
    """The loader reads undirected pairs and neighbors() expands them symmetrically."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    assert "rome" in graph.neighbors("paris")
    assert "paris" in graph.neighbors("rome")
    assert "oslo" in graph.neighbors("paris")
    assert "paris" in graph.neighbors("oslo")


def test_escape_location_has_no_neighbours() -> None:
    """The Escape Location is not an endpoint of any authored connection."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    assert graph.neighbors("escape") == []
