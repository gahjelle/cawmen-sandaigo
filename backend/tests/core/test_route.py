"""Tests for the seeded Fugitive Route generator."""

import random

from cawmen_backend.core.chase import CaseState, has_escaped
from cawmen_backend.core.location import Connection, Location, LocationGraph
from cawmen_backend.core.route import generate_route

PARIS = Location(id="paris", name="Paris", stage=0)
BERLIN = Location(id="berlin", name="Berlin", stage=0)
ESCAPE = Location(id="escape", name="Escape", stage=0, escape=True)

GRAPH = LocationGraph(
    name="test",
    locations=[PARIS, BERLIN, ESCAPE],
    connections=[
        Connection(**{"from": "paris", "to": "berlin"}),
        Connection(**{"from": "berlin", "to": "paris"}),
        Connection(**{"from": "berlin", "to": "escape"}),
        Connection(**{"from": "paris", "to": "escape"}),
    ],
)


def test_route_is_deterministic_for_fixed_seed() -> None:
    """Same seed always produces the same route."""
    route_a = generate_route(GRAPH, random.Random(42))  # noqa: S311
    route_b = generate_route(GRAPH, random.Random(42))  # noqa: S311

    assert route_a == route_b


def test_final_location_is_the_escape_location() -> None:
    """The Escape Location is always last."""
    route = generate_route(GRAPH, random.Random(0))  # noqa: S311

    assert route.locations[-1] == "escape"


def test_all_non_escape_locations_appear_exactly_once() -> None:
    """Every non-escape Location appears in the route exactly once."""
    route = generate_route(GRAPH, random.Random(0))  # noqa: S311

    non_escape_ids = [loc.id for loc in GRAPH.locations if not loc.escape]
    assert sorted(route.locations[:-1]) == sorted(non_escape_ids)


def test_has_escaped_is_true_at_end_of_route() -> None:
    """has_escaped returns True when the clock reaches the Escape Location."""
    route = generate_route(GRAPH, random.Random(0))  # noqa: S311
    final_day = CaseState(day=len(route.locations))

    assert has_escaped(route, final_day)
