# TUI Spectator Screen

## What is a TUI?

A TUI (terminal user interface) sits between a plain CLI and a full GUI. Where a CLI is
stateless — print a line, exit — a TUI owns the terminal, draws a layout, and reacts to
input in real time. The terminal becomes a canvas.

TUIs run anywhere a shell does: over SSH, inside CI, on a minimal server. No browser, no
display server, no Electron bundle. The constraint is the aesthetic.

## How Textual structures an app

Textual is a Python framework for building TUIs. An app subclasses `App`, defines its
layout in `compose` by yielding widgets, and responds to lifecycle events and input via
methods. Widgets are positioned with a CSS subset — `dock: bottom` pins a widget to an
edge of the screen.

Textual is async throughout. `on_mount` is a coroutine; timers fire callbacks on the
event loop. `set_interval(2, fn)` schedules `fn` every two seconds and returns a `Timer`
object you can pause or stop.

Testing is handled by `app.run_test()`, which runs the app in headless mode and returns
a `Pilot` for driving interactions. `await pilot.pause()` waits for the event loop to go
idle — enough to let `on_mount` and any queued widget updates settle before asserting.

## The spectator screen

The `CawmenApp` gained its first real game screen: a live spectator view that creates a
case on startup, renders the location list with the fugitive's current position
highlighted, advances the case every two seconds, and replaces the list with "Trail gone
cold" when the fugitive escapes.

## Injecting a Protocol instead of a concrete class

`CawmenApp.__init__` previously took a `BackendClient` directly. Testing the spectator
screen meant supplying controlled sequences of states — impossible with a concrete class
that hits a live backend.

The fix was `AbstractClient`, a `Protocol` in `client.py` with the four methods the app
actually calls. `BackendClient` satisfies it structurally. Test code supplies a
`FakeClient` dataclass with a prepopulated `advance_states` list. No mocking framework,
no `AsyncMock` leaking implementation details.

One related decision: `TemplatedTextProvider` (which formats the In-Game Clock) lives in
a dev-only backend dependency. Inlining `f"Day {state.day}"` avoids coupling production
TUI code to an internal backend module for what amounts to a string format.

## Timer behaviour in tests

`set_interval` returns a `Timer` stored on the app. Rather than sleeping 2 seconds per
tick in tests, the suite calls `app._tick()` directly after `await pilot.pause()`. This
tests what happens when `advance_case` returns something, without coupling to the timer
mechanism itself.

The `TrailGoneCold` path calls `timer.stop()` — final, unlike `timer.pause()` which can
be resumed. Once the fugitive has escaped, there is nothing left to tick.

## Keeping the terminal clean

When both the backend and the TUI run in the same terminal (e.g. `just serve &`),
uvicorn's per-request access log lines bleed through Textual's rendering. A line like
`INFO: "POST /cases/.../advance HTTP/1.1" 409 Conflict` appears as raw text, then
vanishes when Textual next redraws that region.

The fix is `access_log=False` in the `uvicorn.run()` call. Uvicorn still logs startup
info and errors; it just stops announcing every HTTP exchange to the terminal.
