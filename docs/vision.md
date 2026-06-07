# Cawmen Sandaigo — Vision

## What is it?

Cawmen Sandaigo is a geography and detective game inspired by the classic *Where in the World is Carmen Sandiego?* (1985). It is not a clone. The original's core loop — a detective chasing a fugitive across locations by gathering clues — is kept intact. Everything else is open for reinvention, with AI-generated narrative and a timed chase mechanic at the centre of what makes it distinct.

The game is multilingual by design: AI generates all narrative text directly in the player's chosen language, not as a translation layer but as a first-class output.

---

## The Core Loop

A **Case** begins with a **Crime** — an AI-generated act thematically matched to the **Fugitive** who committed it. The Fugitive flees, and the **Detective** (the player) sets off in pursuit.

At each **Location**, the Detective is presented with a list of named **Persons** present there. Most are innocent bystanders or witnesses. The Fugitive is also among them when their **Fugitive Route** places them there. The Detective can **Interview** any Person to receive **Clues** — witnesses answer truthfully, the Fugitive deflects with plausible lies or vague non-answers.

Clues reveal two things: details about the Fugitive's identity and motive, and hints about where they went next. Armed with this, the Detective makes a **Move** — choosing which Location to travel to next.

If the Detective believes they are co-located with the Fugitive, they must **Arrest** a named Person explicitly. A correct Arrest solves the Case. A false Arrest does not harm the case immediately, but costs significant time — and time is the core tension.

---

## The Timed Chase

The Fugitive follows a secret timed route: Location A on Day 1, Location B on Day 2, and so on. The **In-Game Clock** advances with every action the Detective takes. Clues carry temporal context ("was seen here two days ago"), giving the Detective a sense of whether they are close or falling behind — without ever stating a deadline directly.

At the end of the Fugitive Route sits the **Escape Location** — unnamed, unreachable, never revealed. When the Fugitive arrives there, the trail goes cold and the Case is lost. The Detective is not told when this will happen. Urgency is felt through stale clues and the advancing clock, not a countdown timer.

This creates the central trade-off of every Case: move fast and risk arresting without sufficient evidence, or linger to gather more Clues and risk the Fugitive escaping.

If the Detective has moved ahead of the Fugitive, they can simply wait — spending days at a Location interviewing Persons and gathering Clues until the Fugitive arrives. Alternatively, they can move back toward the Fugitive's last known position, but if both move on the same day they may pass each other in transit, the Detective arriving a day too late at a Location the Fugitive has already left.

---

## The Dossier

Across a Campaign, the Detective builds an understanding of the Suspect roster through the **Dossier** — a database of known criminals associated with a Scenario. Suspects have AI-generated prose profiles. The Detective queries the Dossier using natural language **Dossier Filters** (e.g., "connections to East Asia", "art world background") which are matched semantically via vector search. Multiple active Filters are ANDed together, progressively narrowing the candidate set until the Detective can name their target with confidence before making an Arrest.

The Dossier is consistent across all Campaigns played within the same Scenario — the same cast of Suspects, the same profiles.

---

## The Campaign Arc

A **Campaign** is a player's persistent run through a **Scenario**. It unfolds across multiple Cases, each seeded uniquely but deterministically — given the same Case Seed and the same Scenario, the same Fugitive, Crime, and Fugitive Route are always generated. This makes Cases reproducible and shareable.

As the Campaign progresses, each Case may contain **Mastermind Evidence** — Clues that, taken together across Cases, point toward the criminal network's leader. When enough Mastermind Evidence has accumulated, new Location Stages unlock, expanding the **Location Graph** additively. The world grows as the Detective closes in.

The Campaign culminates in a final Case: the confrontation with **Cawmen Sandaigo**, the mastermind behind the network. Catching Cawmen ends the Campaign in victory. The Player can then start a fresh Campaign on the same Scenario or a different one.

---

## Scenarios

A **Scenario** is a curated world: a Location Graph with staged Locations, a roster of Suspects, and the parameters that govern Case generation. Scenarios are created and maintained via the **Scenario Editor** — a separate workflow independent of gameplay, available to administrators.

The Scenario Editor is seeded with a short prompt ("Barcelona", "South America", "the world"). AI proposes candidate Locations; the editor then adds, removes, and adjusts Locations, connections, and Suspects. The full Location Graph is generated upfront with all Locations and their stages — early Cases use a subgraph, later Cases expand it as Mastermind Evidence unlocks new stages.

Scenarios are the unit of replayability: different players can run the same Scenario and encounter the same world, but their Case outcomes will differ based on their unique Campaign seeds.

---

## AI's Role

AI is used in three places:

1. **Location discovery** — given a scope, AI proposes candidate Locations for the Scenario Editor to review
2. **Narrative text** — Clue descriptions, Location atmosphere, Crime narratives, and Suspect profiles are all AI-generated
3. **Multilingual output** — AI generates text directly in the player's **Language Preference** for the session; text is not stored per-language and is generated fresh each time

AI does not own structural decisions: travel graph construction, Case route planning, Crime assignment, and seed-based generation are all deterministic backend logic.

---

## Architecture

The system has three components with a strict separation of concerns:

**Backend (Python)** — the authoritative source of all game state. Exposes a REST API. Runs all game logic, AI calls, and vector search. Issues JWT tokens for authentication. Frontends are thin clients: they send actions and render responses, holding no state of their own.

**TUI Frontend (Python Textual)** — a terminal interface consuming the REST API. Suited for development, testing, and players who prefer a keyboard-native experience.

**Web Frontend (Phoenix LiveView / Elixir)** — a browser interface consuming the same REST API. LiveView's server-driven model aligns naturally with the thin-client architecture.

**Authentication** is username and password, with JWT tokens shared across frontends — a Campaign started in the TUI can be continued in the browser.

The v1 scope is single-player. The architecture does not foreclose cooperative multiplayer: the backend already owns all state and Players are authenticated identities that could be associated with shared Campaigns in a future version.

---

## What Makes it Different

| Original | Cawmen Sandaigo |
|---|---|
| Canned text per location | AI-generated narrative per session |
| Fixed criminal roster | Scenario-scoped roster, reproducibly generated |
| English only | Any language, generated natively |
| Explicit deadline timer | Hidden deadline via timed Fugitive Route |
| Abstract trait matching for arrest | Named Persons at Locations, explicit Arrest action |
| Fixed world map | Expanding Location Graph tied to investigation progress |
| Single platform | TUI + Web, shared backend state |
