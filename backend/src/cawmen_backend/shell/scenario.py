"""Load a Scenario's Location Graph from its authored ``graph.toml``.

This is shell I/O: it reads a file and validates it into immutable domain data the pure
core can consume. Only the Location Graph is authored; the Suspect roster arrives later.
"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from pathlib import Path


class Location(BaseModel):
    """A single Location in the graph, tagged with the Location Stage that gates it."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    stage: int


class Connection(BaseModel):
    """A travel connection between two Locations."""

    model_config = ConfigDict(frozen=True)

    from_: str = Field(alias="from")
    to: str


class LocationGraph(BaseModel):
    """The full set of Locations and their connections defined in a Scenario."""

    model_config = ConfigDict(frozen=True)

    name: str
    locations: tuple[Location, ...]
    connections: tuple[Connection, ...]


def load_location_graph(path: Path) -> LocationGraph:
    """Read and validate a Scenario's Location Graph from ``graph.toml``."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return LocationGraph.model_validate(data)
