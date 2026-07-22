"""Fugitive Route generation from a Location Graph."""

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from cawmen_backend.core.seed import derive_seed

if TYPE_CHECKING:
    from cawmen_backend.core.location import LocationGraph

type LocationId = str


@dataclass(frozen=True, kw_only=True)
class FugitiveRoute:
    """The fugitive's secret timed path; route[0] is the detective's origin.

    route[day] gives the fugitive's position on that day (1-indexed).
    The final element is always the Escape Location.
    """

    locations: list[LocationId]


def build_route(graph: LocationGraph, seed: str) -> FugitiveRoute:
    """Build a Fugitive Route from a Case Seed, deriving the RNG stream internally."""
    rng = random.Random(derive_seed(seed, "route"))  # noqa: S311
    return generate_route(graph, rng)


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
