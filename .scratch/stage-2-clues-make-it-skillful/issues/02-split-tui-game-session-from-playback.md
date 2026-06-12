# Split TUI GameSession from PlaybackState

Status: needs-triage

## Context

Architecture review (2026-06-12) identified that `CawmenApp.__init__` holds nine
instance fields mixed across two concerns: live-game state (`_case_id`,
`_detective_location`, `_locations_map`, `_location_names`, `_current_neighbors`)
and post-game animation state (`_playback_route`, `_playback_step`, `_playback_current`,
`_terminal_status`, `_playback_timer`). Additionally, `on_mount` and `action_new_case`
duplicate the "start a Case" setup logic (~10 shared lines).

Stage 2 adds Interview, which will introduce more live-game fields (current-person
target, clue history). Without a seam, those fields join the flat soup and the new-case
reset path grows again.

## What to build

When implementing Stage 2 TUI changes, refactor `CawmenApp` before adding new fields.

- Extract a `GameSession` dataclass (in `app.py` or a new `session.py`) holding the
  five live-game fields: `case_id`, `detective_location`, `locations_map`,
  `location_names`, `current_neighbors`.
- Extract a `PlaybackState` dataclass holding the five animation fields: `route`,
  `step`, `current`, `status`, `timer`.
- `CawmenApp` holds `_session: GameSession | None` and `_playback: PlaybackState | None`.
- Extract `_start_session(case: CaseCreated) -> None` (async) that replaces the
  duplicated startup logic in `on_mount` and `action_new_case`.
- `action_new_case` resets by assigning `self._playback = None` before calling
  `_start_session`; no field-by-field teardown needed.

## Acceptance criteria

- [ ] `GameSession` and `PlaybackState` dataclasses exist and hold the appropriate fields
- [ ] `CawmenApp.__init__` assigns `_session = None` and `_playback = None` (two lines,
      not ten)
- [ ] `on_mount` and `action_new_case` share a single `_start_session()` call with no
      duplicated field assignments
- [ ] Existing TUI tests pass without modification (behaviour unchanged)
- [ ] `just check` passes

## Blocked by

Nothing — can be done as a pure refactor before or alongside the Interview TUI work.

## Last step

Write an article stub under `articles/02-clues-make-it-skillful/` covering the
`GameSession` / `PlaybackState` split and how it tightens the new-case reset path.
