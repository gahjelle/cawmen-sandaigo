# End-of-case experience: route playback + New case / Quit

Status: done

## Parent

PRD: `.scratch/stage-1-player-moves/PRD.md`.

## What to build

Give a finished Case a payoff in the TUI: replay the chase so the player sees where they
missed, then let them keep playing.

- On a terminal outcome (`won`/`lost`), stop accepting Moves and **play the revealed
  Fugitive Route back day-by-day** on a timer (reusing `set_interval`), highlighting each
  hop so the player sees how near or far they were.
- After the playback, show a banner — "Caught them!" / "The trail went cold." — and offer
  **[N]ew case / [Q]uit**.
- **New case** reuses the same Scenario (`minimal`) with a fresh random seed, returning to
  the opening position of a new Case without restarting the app.

## Acceptance criteria

- [x] On a terminal outcome the TUI stops accepting Moves and plays the revealed route
      back step-by-step on a timer
- [x] A win shows a win banner; a loss shows a loss banner
- [x] `[N]ew case` starts a fresh Case on `minimal` with a new random seed and renders the
      opening position
- [x] `[Q]uit` exits cleanly
- [x] `just check` passes

## Blocked by

- `04-detective-moves-playable-blind-loop.md`

## Last step

Write an article stub under `articles/01-the-detective-chases/route-playback.md`
summarising the end-of-case playback and the New case / Quit loop.
