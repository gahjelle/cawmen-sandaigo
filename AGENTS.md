## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context layout — `CONTEXT-MAP.md` at the root points to per-context `CONTEXT.md` files (backend + frontends). See `docs/agents/domain.md`.

## Tooling & conventions

Everything runs through `uv`; the full local gate is `just check`. Strict ruff (`ALL`) +
`ty`-only typing, plus repo-specific rules enforced by `uv run python -m tools.repolint`.
See `docs/agents/conventions.md`.
