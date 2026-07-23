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

## Keeping the tests untouched

The existing pilot tests reach past the public surface and assert on private fields —
`app._detective_location`, `app._playback_route`, `app._playback_current`. The refactor's
contract was that behaviour stays identical and those tests pass *without modification*.
Rather than relocate storage and rewrite the assertions, three read-only properties keep
the old names readable while the dataclasses own the storage:

```python
@property
def _detective_location(self) -> str | None:
    return self._session.detective_location if self._session else None
```

They're deliberately read-only — every *write* goes through the dataclass, so the flat
soup doesn't creep back in through a setter. The shims are the one concession to test
coupling; a later pass could push those assertions through the `_session` / `_playback`
seam and delete them.

One incidental note for Python 3.14: the `PlaybackState.timer` field is typed
`Timer | None` with `Timer` imported only under `TYPE_CHECKING`. PEP 649 evaluates
annotations lazily, so the dataclass never tries to resolve `Timer` at runtime — no
`from __future__ import annotations` needed (and the repo's conventions forbid it).
