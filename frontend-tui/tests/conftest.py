"""Shared fixtures: an httpx client wired in-process to the real backend ASGI app.

Per ADR-0007/0009, the primary test transport is `httpx.ASGITransport` over the real
FastAPI app — deterministic and exercising the same typed client the run path uses.
"""

from typing import TYPE_CHECKING

import httpx
import pytest

from cawmen_backend.api.app import create_app

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.fixture
async def backend_http() -> AsyncIterator[httpx.AsyncClient]:
    """Yield an httpx client backed by the real backend app over ASGITransport."""
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://backend",
    ) as http:
        yield http
