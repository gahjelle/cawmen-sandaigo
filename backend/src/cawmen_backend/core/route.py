"""Fugitive Route generation from a Location Graph."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import random

    from cawmen_backend.core.location import LocationGraph

type LocationId = str


@dataclass(frozen=True)
class FugitiveRoute:
    """The fugitive's secret timed path; route[0] is the detective's origin.

    route[day] gives the fugitive's position on that day (1-indexed).
    The final element is always the Escape Location.
    """

    locations: list[LocationId]


def generate_route(graph: LocationGraph, rng: random.Random) -> FugitiveRoute:
    """Generate a seeded Fugitive Route by self-avoiding walk from a random start."""
    non_escape = [loc for loc in graph.locations if not loc.escape]
    escape = next(loc for loc in graph.locations if loc.escape)

    start = rng.choice(non_escape)
    route: list[str] = [start.id]
    current = start.id

    while True:
        candidates = [n for n in graph.neighbors(current) if n not in route]
        if not candidates:
            break
        current = rng.choice(candidates)
        route.append(current)

    return FugitiveRoute(locations=[*route, escape.id])
