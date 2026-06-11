"""Location Graph domain model: pure data, no I/O."""

from cawmen_backend.models import FrozenModel


class Location(FrozenModel):
    """A single Location in the graph, tagged with the Location Stage that gates it."""

    id: str
    name: str
    stage: int
    escape: bool = False


class LocationGraph(FrozenModel):
    """The full set of Locations and their connections defined in a Scenario."""

    name: str
    locations: list[Location]
    connections: list[list[str]]

    def neighbors(self, location_id: str) -> list[str]:
        """Return the IDs reachable from `location_id` via undirected connections."""
        result = []
        for first, second in self.connections:
            if first == location_id:
                result.append(second)
            elif second == location_id:
                result.append(first)
        return result
