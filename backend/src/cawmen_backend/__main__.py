"""The cawmen-backend console script: serve the REST API."""

from pathlib import Path

import uvicorn
from cyclopts import App

from cawmen_backend.api.app import create_app
from cawmen_backend.api.schema import openapi_is_current, render_openapi

app = App(name="cawmen-backend", help="Cawmen Sandaigo backend.")


@app.command
def serve(*, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the backend REST API server (ADR-0007: frontends connect over HTTP)."""
    uvicorn.run(create_app(), host=host, port=port, access_log=False)


@app.command
def openapi(*, path: Path = Path("openapi.json"), check: bool = False) -> None:
    """Write the OpenAPI schema to `path`; `--check` verifies it is current."""
    if check:
        if not openapi_is_current(path):
            msg = f"{path} is stale; regenerate with `cawmen-backend openapi`."
            raise SystemExit(msg)
        return
    path.write_text(render_openapi(), encoding="utf-8")


if __name__ == "__main__":
    app()
