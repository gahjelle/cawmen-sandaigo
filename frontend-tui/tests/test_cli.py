"""The cawmen-tui console script wiring."""

import pytest

from cawmen_tui import __main__
from cawmen_tui.app import CawmenApp


def test_play_targets_the_backend_at_the_given_api_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The --api-url option points the client at an already-running backend."""
    captured: dict[str, str] = {}

    def fake_run(self: CawmenApp) -> None:
        captured["base_url"] = str(self._client._http.base_url)

    monkeypatch.setattr(CawmenApp, "run", fake_run)

    with pytest.raises(SystemExit) as exit_info:
        __main__.app(["--api-url", "http://example:9999"])

    assert exit_info.value.code == 0
    assert captured["base_url"] == "http://example:9999"
