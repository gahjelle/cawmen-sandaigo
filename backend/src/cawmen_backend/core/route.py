"""Fugitive Route generation from a Location Graph."""

from typing import TYPE_CHECKING

from cawmen_backend.core.chase import FugitiveRoute

if TYPE_CHECKING:
    import random

    from cawmen_backend.core.location import LocationGraph


def generate_route(graph: LocationGraph, rng: random.Random) -> FugitiveRoute:
    """Generate a seeded Fugitive Route by walking the graph from a random start."""
    non_escape = [loc for loc in graph.locations if not loc.escape]
    escape = next(loc for loc in graph.locations if loc.escape)

    start = rng.choice(non_escape)
    route: list[str] = [start.id]
    current = start.id

    while len(route) < len(non_escape):
        current = next(
            c.to
            for c in graph.connections
            if c.from_ == current and c.to not in route and c.to != escape.id
        )
        route.append(current)

    route.append(escape.id)
    return FugitiveRoute(locations=route)
