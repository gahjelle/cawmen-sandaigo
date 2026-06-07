# Cawmen Sandaigo — Implementation Plan

This is a high-level, chronological staging of the work described in [the vision](./vision.md). It identifies *what* each stage delivers and *why it comes when it does* — not *how*. Each stage will be grilled independently to decide its technical detail.

## Principles

- **Tracer bullets over horizontal layers.** Every stage cuts a thin slice through backend → API → frontend and leaves something visible and testable, rather than completing one layer in isolation.
- **Playable early, skillful soon after.** Reach a winnable game quickly, then make it reward skill.
- **Deterministic text first, AI later.** Lock the mechanics with canned/templated text, then swap in AI as a pure text layer once the structure is stable.
- **TUI first.** The Python Textual frontend leads. The Phoenix LiveView web frontend is introduced only once the API needs to prove it is frontend-agnostic.
- **The API exists from day one.** Even the MVP talks through REST, so strict backend/frontend separation is validated from the first line of code.

---

## Where the content comes from

Two distinct sources of content, with different lifecycles:

- **Scenarios are hand-authored data files from Stage 0.** The Location Graph (with stages) and the Suspect roster (with profiles) live in version-controlled data files that the engine loads. The engine never knows whether a Scenario was hand-written or produced by a tool. This makes Scenarios diffable, reviewable, and QA-able — and it means the **Scenario Editor (Stage 10) is a slot-in**: a UI with AI assistance that simply writes the same file format. When the database arrives (Stage 8), authored Scenarios can stay as files while runtime Campaign/Case state goes in the DB.

- **Cases are procedurally generated, not hand-authored.** Choosing the Fugitive, the Crime, the timed Fugitive Route to the Escape Location, and the placement of Persons and Clues *is* the core game logic, built up across Stages 1–4. The generator is **seeded from the start** ([ADR-0001](./adr/0001-case-seed-for-reproducibility.md)): a Case Seed is an input parameter from the first generation function, so a given seed always yields the same Case. This is free, makes generation deterministically testable from Stage 1, and avoids a painful seed-threading retrofit later. What Stage 8 adds is *persistence* — storing the seed and reproducing a Case by its UUID — not seeding itself. (At Stages 0–1 the route is trivial enough to be fixed or a simple seeded walk; real procedural variety becomes necessary at Stage 2, where a memorizable fixed route would defeat clue-following.)

---

## Stage 0 — The fugitive moves (MVP)

**Delivers:** A hand-authored Scenario data file providing a fixed Location Graph, and a Fugitive Route through it (fixed or a trivial random walk). A thin REST API exposes case state and advances the In-Game Clock. The TUI renders the graph and shows the fugitive stepping between Locations as the clock advances.

**Visible/testable:** You watch the fugitive travel its route in the terminal.

**Proves:** The full stack end to end — backend owns state, API serves it, TUI renders it. No game logic yet.

**Deferred:** All player interaction, clues, persons, identity, AI, persistence.

---

## Stage 1 — The detective chases (a game, but blind)

**Delivers:** The detective as a movable entity. The player issues a **Move** along graph edges via the API; the clock advances. The Case is won when detective and fugitive are co-located, and lost when the fugitive reaches the **Escape Location**.

**Visible/testable:** You can play, win, and lose — by guesswork, since there are no clues yet.

**Proves:** The core action loop and win/lose conditions over the timed route.

**Deferred:** Anything that makes movement informed rather than random.

---

## Stage 2 — Clues make it skillful

**Delivers:** The **Interview** action returns a **Clue** pointing toward the fugitive's next hop (templated text, no AI). Following clues now lets the player actually track the fugitive.

**Visible/testable:** The first genuinely playable game — chase a fugitive by reading clues.

**Deferred:** Persons (clues come from the Location for now), explicit arrest, identity.

---

## Stage 3 — Persons and explicit Arrest

**Delivers:** Locations are populated with named **Persons** — innocent witnesses plus the Fugitive when co-located. Interview targets a specific Person; the Fugitive answers with lies or vague non-answers. The **Arrest** action names a Person; a false Arrest costs time that can cascade into a lost Case. The **Wait** action is added.

**Visible/testable:** The complete single-Case verb set — Interview, Move, Wait, Arrest — is playable.

**Deferred:** Distinguishing *which* Suspect the fugitive is; the deduction layer.

---

## Stage 4 — Identity and the Dossier

**Delivers:** A roster of **Suspects** exists, and Clues now describe identity, traits, and motive (with the **Crime** as a soft filter), not just direction. A browsable **Dossier** lets the player match clues to a Suspect and decide who to arrest.

**Visible/testable:** A full single-Case experience — track the fugitive *and* deduce their identity before arresting.

**Deferred:** Semantic search over the Dossier (browsing/simple filtering only for now).

---

## Stage 5 — AI narrative

**Delivers:** Templated text is replaced by AI-generated Clues, Location atmosphere, Crime narratives, and Suspect profiles, generated directly in the player's **Language Preference**.

**Visible/testable:** The game reads as written prose, in multiple languages, with the mechanics unchanged.

**Proves:** AI slots cleanly into a stable structure as a pure text layer.

**Deferred:** Vector-based Dossier search.

---

## Stage 6 — Prove the API: the web frontend

**Delivers:** The Phoenix LiveView web frontend as a second thin client, mirroring the (now AI-driven) gameplay built so far. Identity can stay stubbed at this point.

**Visible/testable:** The same Case is playable in the browser and the TUI against one backend.

**Proves:** The API is genuinely frontend-agnostic — including serving generated prose to two different clients — caught and fixed now, while the surface is still small, rather than after persistence and the campaign arc are layered on.

**Deferred:** Real accounts and cross-session persistence (both frontends share the backend's in-memory state for now).

---

## Stage 7 — Dossier semantic search

**Delivers:** A vector store and embeddings behind the Dossier. Natural-language **Dossier Filters**, ANDed together, progressively narrow the candidate Suspects.

**Visible/testable:** The player narrows the roster with queries like "art-world background" instead of manual browsing.

---

## Stage 8 — Persistence, accounts, reproducible Cases

**Delivers:** A database. **Player** accounts with username/password and JWT auth shared across frontends. Campaigns and Cases persist across sessions. **Case Seeds** are stored so a Case can be reproduced or shared by its UUID (the generator was already seeded from Stage 0).

**Visible/testable:** Log in on the TUI, continue in the browser; a stored seed reproduces the same Case.

**Deferred:** The multi-Case campaign arc.

---

## Stage 9 — The Campaign arc

**Delivers:** A **Campaign** spanning multiple Cases. **Mastermind Evidence** accumulates across Cases; reaching thresholds expands the **Location Graph** by unlocking later **Location Stages**. The arc culminates in the final confrontation with **Cawmen Sandaigo** and a victory that ends the Campaign.

**Visible/testable:** A full campaign played start to finish, with a growing world and a climactic final Case.

---

## Stage 10 — Scenario Editor (admin)

**Delivers:** The admin **Scenario Editor** workflow: seed a Scenario from a short prompt, use AI Location discovery, then add/remove/edit Locations, connections, and Suspects to curate a reviewable, QA-able world.

**Visible/testable:** New Scenarios authored and edited outside of gameplay, then played as Campaigns.

**Note:** Until this stage, the game runs on one or more hand-built Scenarios. The Editor turns Scenario authoring into a first-class, repeatable workflow.

---

## Open sequencing questions (to revisit)

- **Web frontend timing (Stage 6).** Placed after the single-Case loop and AI narrative, to validate the API as frontend-agnostic before persistence and the campaign arc are layered on. Could move earlier (less to mirror) or later (more mature gameplay first) — a deliberate trade-off worth confirming.
- **Case Seeds (Stage 8).** The generator is seeded from Stage 0 ([ADR-0001](./adr/0001-case-seed-for-reproducibility.md)); only *persistence* of seeds and reproduction-by-UUID waits for the database at Stage 8 (see *Where the content comes from*).
