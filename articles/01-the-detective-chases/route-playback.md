# Route Playback and the New Case Loop

## End-of-case experience

When a Case reaches a terminal outcome (`won` or `lost`), the TUI enters a
two-phase end-of-case experience.

**Phase 1 — route playback.** A `set_interval` timer calls `_advance_playback()`
once per second. Each call moves `_playback_current` to the next location in
`fugitive_route` and re-renders `#locations`, highlighting the fugitive's
position in bold red alongside the detective's fixed end-location in reverse
video. The player sees the full chase replay day-by-day. The neighbour list
stays empty throughout; moves are refused.

**Phase 2 — banner.** When the last route position is shown, the timer stops and
`_show_end_banner()` writes to a dedicated `#banner` widget: "Caught them!" on a
win; "The trail went cold." on a loss. Both messages append `[N] New case
[Q] Quit` instructions.

## N/Q key bindings

`BINDINGS` wires `n` → `action_new_case` and `q` → `action_quit_app`. `action_new_case`
is guarded by `_terminal_status is None` so it silently ignores presses during
active play. On invocation it cancels the playback timer if still running,
resets all playback state, clears the banner, calls `create_case` with a fresh
UUID seed, and re-renders the opening position — same Scenario (`minimal`), new
random Case. `action_quit_app` calls `self.exit()`.

## Testability

`_advance_playback()` is a plain synchronous method, callable directly from
tests without waiting for real timers. Tests advance the full route with
`for _ in route: app._advance_playback()` and assert on `_playback_current` and
`#banner` content. The `TrackingFakeClient` subclass records seeds passed to
`create_case`, letting the N-key test confirm both that a second call was made
and that its seed differs from the first.
