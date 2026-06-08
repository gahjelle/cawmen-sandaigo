"""Loading a Scenario's Location Graph from its authored graph.toml."""

from pathlib import Path

from cawmen_backend.shell.scenario import load_location_graph

SCENARIOS = Path(__file__).resolve().parents[3] / "scenarios"


def test_loads_the_authored_locations_in_order() -> None:
    """The loader preserves the Locations in their authored order."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    assert [location.id for location in graph.locations if not location.escape] == [
        "paris",
        "berlin",
        "rome",
        "madrid",
    ]


def test_escape_location_is_distinguished() -> None:
    """The Escape Location is loaded but marked so the API can exclude it."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    escape = next(loc for loc in graph.locations if loc.escape)
    assert escape.id == "escape"


def test_loads_connections_between_locations() -> None:
    """The loader reads the travel connections between Locations."""
    graph = load_location_graph(SCENARIOS / "minimal" / "graph.toml")

    assert ("paris", "berlin") in [(c.from_, c.to) for c in graph.connections]
