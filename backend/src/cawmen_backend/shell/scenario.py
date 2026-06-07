"""Load a Scenario's Location Graph from its authored `graph.toml`.

This is shell I/O: it reads a file and validates it into domain data the pure core can
consume. Only the Location Graph is authored; the Suspect roster arrives later.
"""

import tomllib
from typing import TYPE_CHECKING

from cawmen_backend.core.location import Location, LocationGraph

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["Location", "LocationGraph", "load_location_graph"]


def load_location_graph(path: Path) -> LocationGraph:
    """Read and validate a Scenario's Location Graph from `graph.toml`."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return LocationGraph.model_validate(data)
