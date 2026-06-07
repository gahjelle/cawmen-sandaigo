"""Load a Scenario's Location Graph from its authored `graph.toml`.

This is shell I/O: it reads a file and validates it into domain data the pure core can
consume. Only the Location Graph is authored; the Suspect roster arrives later.
"""

import tomllib
from typing import TYPE_CHECKING

from pydantic import Field

from cawmen_backend.models import StrictModel

if TYPE_CHECKING:
    from pathlib import Path


class Location(StrictModel):
    """A single Location in the graph, tagged with the Location Stage that gates it."""

    id: str
    name: str
    stage: int


class Connection(StrictModel):
    """A travel connection between two Locations."""

    from_: str = Field(alias="from")
    to: str


class LocationGraph(StrictModel):
    """The full set of Locations and their connections defined in a Scenario."""

    name: str
    locations: list[Location]
    connections: list[Connection]


def load_location_graph(path: Path) -> LocationGraph:
    """Read and validate a Scenario's Location Graph from `graph.toml`."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return LocationGraph.model_validate(data)
