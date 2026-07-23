# Splitting the TUI's GameSession from its PlaybackState

`CawmenApp.__init__` had grown a flat soup of nine instance fields covering two
unrelated concerns. Five described the live game — which case is running, where the
detective stands, the world's adjacency and names, the currently offered neighbours.
Four described the post-game animation — the revealed fugitive route, how far the
playback has advanced, the position lit up right now, the terminal status, and the
timer driving it. They sat side by side in one `__init__`, and every new-case reset
had to remember to clear the right subset by hand.

Stage 2 adds Interview, which brings *more* live-game state (a clue history). Without a
seam, those fields would have joined the same soup and the reset path would have grown
again. So before Interview lands, this refactor draws the seam.

## Two dataclasses, one of each concern

The nine fields become two `@dataclass(kw_only=True)` value objects, and the app holds
one nullable reference to each:

```python
self._session: GameSession | None = None
self._playback: PlaybackState | None = None
```

`None` now carries real meaning: no `_session` means no case is running, no `_playback`
means the game hasn't reached a terminal outcome. The old code leaned on a scatter of
sentinel fields (`_terminal_status is None`) to ask the same questions; now `if
self._playback is None: return` guards the new-case action directly, and the intent reads
off the line.

## Collapsing the duplicated startup

`on_mount` and `action_new_case` both created a case and then rebuilt the two location
maps from `case.locations` — about ten shared lines, copy-pasted. Both now call a single
builder:

```python
def _start_session(self, case: CaseCreated) -> None:
    self._session = GameSession(
        case_id=case.case_id,
        detective_location=case.detective_location,
        locations_map={loc.id: loc.neighbors for loc in case.locations},
        location_names={loc.id: loc.name for loc in case.locations},
    )
```

Constructing a fresh `GameSession` *is* the reset — there is no longer a per-field
clear-down to keep in sync. Same for ending a game: `_render_state` assigns a brand-new
`PlaybackState`, and `action_new_case` drops it back to `None`.

## Moving the tests onto the seam

The existing pilot tests reached past the public surface and asserted on the old flat
fields — `app._detective_location`, `app._playback_route`, `app._playback_current`. The
tempting shortcut was to keep those names alive as read-only properties delegating to the
dataclasses, so the tests wouldn't have to change. But that just preserves the coupling
the refactor set out to break: the tests would still be reaching for storage that no
longer exists, papered over by a shim.

So the assertions move onto the new seam instead:

```python
assert cawmen_app._session is not None
assert cawmen_app._session.detective_location == "berlin"
```

The explicit `is not None` narrows the `GameSession | None` for the type checker and, more
usefully, states the precondition the assertion depends on: there *is* a live session by
this point. The behaviour under test is unchanged — only the address of the state moved.

One incidental note for Python 3.14: the `PlaybackState.timer` field is typed
`Timer | None` with `Timer` imported only under `TYPE_CHECKING`. PEP 649 evaluates
annotations lazily, so the dataclass never tries to resolve `Timer` at runtime — no
`from __future__ import annotations` needed (and the repo's conventions forbid it).
