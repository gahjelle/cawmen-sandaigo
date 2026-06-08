"""Location Graph domain model: pure data, no I/O."""

from pydantic import Field

from cawmen_backend.models import FrozenModel


class Location(FrozenModel):
    """A single Location in the graph, tagged with the Location Stage that gates it."""

    id: str
    name: str
    stage: int
    escape: bool = False


class Connection(FrozenModel):
    """A travel connection between two Locations."""

    from_: str = Field(alias="from")
    to: str


class LocationGraph(FrozenModel):
    """The full set of Locations and their connections defined in a Scenario."""

    name: str
    locations: list[Location]
    connections: list[Connection]
