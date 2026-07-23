## Agent skills

### Issue tracker

Issues and the `/wayfinder` map live as GitHub issues in `gahjelle/cawmen-sandaigo` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Article stubs

Article stubs are written after each task, combined into full articles per stage. Stubs
live under `articles/<NN>-<stage-name>/`, combined articles at `articles/<NN>-<stage-name>.md`.
See `docs/agents/articles.md`.

### Domain docs

Multi-context layout — `CONTEXT-MAP.md` at the root points to per-context `CONTEXT.md` files (backend + frontends). See `docs/agents/domain.md`.

## Tooling & conventions

Everything runs through `uv`; the full local gate is `just check`. Strict ruff (`ALL`) +
`ty`-only typing, plus repo-specific rules enforced by `uv run garuff check`.
See `docs/agents/conventions.md`.
