# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading
- Every issue ends with a `## Last step` section reminding the agent to write an article stub (see `articles.md`)

## Working an issue end-to-end

When implementing an issue, follow this sequence:

1. **Read the issue** — understand the acceptance criteria and the `## Last step` section
2. **Explore the codebase** — read relevant source files and tests before making changes
3. **Write failing tests** — one test per acceptance criterion; run them to confirm they fail
4. **Implement** — write the minimum code to make the tests pass; prefer editing existing files
5. **Run the full gate** — `just check` must pass before committing
6. **Write the article stub** — as the last implementation step, per `articles.md`
7. **Commit** — all changed files in one commit
8. **Close the issue** — two edits to the issue file:
   - Change `Status: ready-for-agent` → `Status: done`
   - Append a `## Comments` section with the date, commit hash, and a one-line summary

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.
