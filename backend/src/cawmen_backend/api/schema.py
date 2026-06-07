"""Render the API's OpenAPI schema as a canonical, diffable artifact.

The committed ``openapi.json`` is the source of truth for the client/server contract
(ADR-0009); a staleness check regenerates this and fails on any uncommitted drift.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from cawmen_backend.api.app import create_app

if TYPE_CHECKING:
    from pathlib import Path


def render_openapi() -> str:
    """Return the OpenAPI schema as canonical JSON (sorted keys, trailing newline)."""
    schema = create_app().openapi()
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def openapi_is_current(path: Path) -> bool:
    """Report whether the committed schema at ``path`` matches the live rendering."""
    return path.exists() and path.read_text(encoding="utf-8") == render_openapi()
