"""Tests for the seeded Fugitive Route generator."""

import random

from cawmen_backend.core.chase import CaseState, has_escaped
from cawmen_backend.core.location import Location, LocationGraph
from cawmen_backend.core.route import generate_route

PARIS = Location(id="paris", name="Paris", stage=0)
BERLIN = Location(id="berlin", name="Berlin", stage=0)
ESCAPE = Location(id="escape", name="Escape", stage=0, escape=True)

GRAPH = LocationGraph(
    name="test",
    locations=[PARIS, BERLIN, ESCAPE],
    connections=[["paris", "berlin"]],
)

# Triangular prism: Paris—Rome—Madrid (triangle A), Berlin—London—Oslo (triangle B),
# rungs Paris—Berlin, Rome—London, Madrid—Oslo. 3-regular, fully connected.
PRISM_LOCATIONS = [
    Location(id="paris", name="Paris", stage=0),
    Location(id="rome", name="Rome", stage=0),
    Location(id="madrid", name="Madrid", stage=0),
    Location(id="berlin", name="Berlin", stage=0),
    Location(id="london", name="London", stage=0),
    Location(id="oslo", name="Oslo", stage=0),
    Location(id="escape", name="Escape", stage=0, escape=True),
]
PRISM = LocationGraph(
    name="prism",
    locations=PRISM_LOCATIONS,
    connections=[
        ["paris", "rome"],
        ["rome", "madrid"],
        ["madrid", "paris"],
        ["berlin", "london"],
        ["london", "oslo"],
        ["oslo", "berlin"],
        ["paris", "berlin"],
        ["rome", "london"],
        ["madrid", "oslo"],
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
    final_day = CaseState(
        day=len(route.locations) - 1,
        seed="s",
        detective_location="paris",
        status="in_progress",
    )

    assert has_escaped(route, final_day)


def test_every_step_follows_adjacency() -> None:
    """Each consecutive pair of non-escape locations in the route is adjacent."""
    import itertools  # noqa: PLC0415

    route = generate_route(PRISM, random.Random(7))  # noqa: S311

    non_escape = route.locations[:-1]
    for a, b in itertools.pairwise(non_escape):
        assert b in PRISM.neighbors(a), f"{a} → {b} is not an edge in the prism"


def test_prism_route_never_errors_across_many_seeds() -> None:
    """Self-avoiding walk on the 3-regular prism never raises for any seed."""
    for seed in range(50):
        generate_route(PRISM, random.Random(seed))  # noqa: S311


def test_prism_route_ends_at_escape() -> None:
    """Routes on the prism always terminate at the Escape Location."""
    for seed in range(20):
        route = generate_route(PRISM, random.Random(seed))  # noqa: S311
        assert route.locations[-1] == "escape"
