"""The cawmen-backend console script wiring."""

from typing import TYPE_CHECKING, Any

import pytest

from cawmen_backend import __main__

if TYPE_CHECKING:
    from pathlib import Path


def test_serve_runs_uvicorn_on_the_requested_host_and_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The serve command starts uvicorn on the host and port it is given."""
    captured: dict[str, Any] = {}

    def fake_run(app: object, *, host: str, port: int, access_log: bool) -> None:
        captured["app"] = app
        captured["host"] = host
        captured["port"] = port
        captured["access_log"] = access_log

    monkeypatch.setattr(__main__.uvicorn, "run", fake_run)

    with pytest.raises(SystemExit) as exit_info:
        __main__.app(["serve", "--host", "0.0.0.0", "--port", "9001"])  # noqa: S104

    assert exit_info.value.code == 0
    assert captured["host"] == "0.0.0.0"  # noqa: S104
    assert captured["port"] == 9001


def test_openapi_writes_then_checks_the_schema(tmp_path: Path) -> None:
    """`openapi` writes the schema and `--check` then reports it current."""
    target = tmp_path / "openapi.json"

    with pytest.raises(SystemExit) as write_exit:
        __main__.app(["openapi", "--path", str(target)])
    assert write_exit.value.code == 0
    assert target.exists()

    with pytest.raises(SystemExit) as check_exit:
        __main__.app(["openapi", "--path", str(target), "--check"])
    assert check_exit.value.code == 0


def test_openapi_check_fails_on_a_stale_schema(tmp_path: Path) -> None:
    """`openapi --check` exits non-zero when the committed schema has drifted."""
    target = tmp_path / "openapi.json"
    target.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit) as check_exit:
        __main__.app(["openapi", "--path", str(target), "--check"])

    assert check_exit.value.code != 0
