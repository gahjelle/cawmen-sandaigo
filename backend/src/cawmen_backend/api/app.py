"""The FastAPI application factory and its routes."""

from fastapi import FastAPI

from cawmen_backend.models import StrictModel


class HealthResponse(StrictModel):
    """Liveness payload polled by the TUI launcher before it connects (ADR-0007)."""

    status: str


def create_app() -> FastAPI:
    """Build the FastAPI app exposing the Cawmen Sandaigo REST API."""
    app = FastAPI(title="Cawmen Sandaigo", version="0.0.0")

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return app
