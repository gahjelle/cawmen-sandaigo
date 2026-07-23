# TUI Interview surface

Status: open
Labels: wayfinder:grilling
Assignee:
Parent: [Stage 2 map](../MAP.md)

## Question

How does the player trigger Interview in the Textual TUI, and how is the returned Clue
presented?

- **Trigger**: a keybinding / action (mirroring the existing Move affordance) — which key,
  and how it reads against the current bindings.
- **Display**: where the clue text appears (a log/panel, a transient banner, a persistent
  clue history?) and whether prior clues stay visible as the chase progresses.
- **State feedback**: if Interview advances the clock (per the interview-cost ticket), the
  screen must reflect the new day / fugitive-fled state consistently with Move.

Note: this rides on top of the `GameSession` / `PlaybackState` split (that refactor adds
the seam for live-game clue state). Resolve via `/grilling`; use `/prototype` if the
layout is the crux.

## Blocked by

- [Interview API surface](./05-interview-api-surface.md)
