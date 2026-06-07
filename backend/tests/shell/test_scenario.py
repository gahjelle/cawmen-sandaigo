"""Loading a Scenario's Location Graph from its authored graph.toml."""

from pathlib import Path

from cawmen_backend.shell.scenario import load_location_graph

SCENARIOS = Path(__file__).resolve().parents[3] / "scenarios"


def test_loads_the_authored_locations_in_order() -> None:
    """The loader preserves the Locations in their authored order."""
    graph = load_location_graph(SCENARIOS / "grand-tour" / "graph.toml")

    assert [location.id for location in graph.locations] == [
        "paris",
        "berlin",
        "rome",
        "madrid",
    ]


def test_loads_connections_between_locations() -> None:
    """The loader reads the travel connections between Locations."""
    graph = load_location_graph(SCENARIOS / "grand-tour" / "graph.toml")

    assert ("paris", "berlin") in [(c.from_, c.to) for c in graph.connections]
