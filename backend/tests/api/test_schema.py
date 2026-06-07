"""The committed OpenAPI schema is the API contract (ADR-0009)."""

from typing import TYPE_CHECKING

from cawmen_backend.api.schema import openapi_is_current, render_openapi

if TYPE_CHECKING:
    from pathlib import Path


def test_render_openapi_describes_the_health_path() -> None:
    """The rendered schema documents the public health endpoint."""
    assert "/health" in render_openapi()


def test_render_openapi_is_deterministic() -> None:
    """Rendering is byte-stable so a stale committed schema shows a clean diff."""
    assert render_openapi() == render_openapi()


def test_schema_matching_the_rendering_is_current(tmp_path: Path) -> None:
    """A file holding the freshly rendered schema is reported as current."""
    committed = tmp_path / "openapi.json"
    committed.write_text(render_openapi(), encoding="utf-8")

    assert openapi_is_current(committed)


def test_drifted_or_missing_schema_is_not_current(tmp_path: Path) -> None:
    """A stale or absent committed schema is reported as not current."""
    committed = tmp_path / "openapi.json"

    assert not openapi_is_current(committed)

    committed.write_text("{}", encoding="utf-8")
    assert not openapi_is_current(committed)
