"""The cawmen-tui console script: launch the terminal client.

Ships the "assume-running" path first (ADR-0007): `--api-url` connects to a
backend that is already serving. Auto-spawn can be added later with zero client rework.
"""

from cyclopts import App

from cawmen_tui.app import CawmenApp

app = App(name="cawmen-tui", help="Cawmen Sandaigo terminal client.")


@app.default
def play(*, api_url: str = "http://127.0.0.1:8000") -> None:
    """Launch the TUI against a backend already serving at `api_url`."""
    CawmenApp.from_api_url(api_url).run()


if __name__ == "__main__":
    app()
