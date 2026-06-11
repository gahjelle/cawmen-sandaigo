"""Tests for the LocationGraph domain model."""

from cawmen_backend.core.location import Location, LocationGraph

PARIS = Location(id="paris", name="Paris", stage=0)
ROME = Location(id="rome", name="Rome", stage=0)
ESCAPE = Location(id="escape", name="Escape", stage=0, escape=True)

GRAPH = LocationGraph(
    name="test",
    locations=[PARIS, ROME, ESCAPE],
    connections=[["paris", "rome"]],
)


def test_neighbors_returns_the_other_endpoint_of_each_pair() -> None:
    """neighbors() expands each undirected pair into both directions."""
    assert GRAPH.neighbors("paris") == ["rome"]
    assert GRAPH.neighbors("rome") == ["paris"]


def test_escape_location_has_no_neighbors() -> None:
    """The Escape Location has no authored connections and returns no neighbors."""
    assert GRAPH.neighbors("escape") == []
