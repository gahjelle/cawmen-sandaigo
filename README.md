# Cawmen Sandaigo

A geography and detective game where you play a detective chasing a fugitive across cities. The fugitive moves on a secret schedule, leaving clues at each location. Your job is to follow the trail and make the arrest before they slip away for good.

## What the game looks like right now

The current build lets you watch a case unfold in the terminal. A fugitive is assigned a route through a handful of European cities — Paris, Berlin, Rome, Madrid — and you can see their position update in real time as the in-game clock advances. The backend runs all the game logic and exposes a REST API; the terminal client connects to it and renders the live state.

It's a spectator view at this stage: you watch the chase happen rather than making decisions yourself. The plumbing — case creation, route generation, live tracking — is all wired up and working.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) — used for all dependency management and running tools

## Getting started

**1. Clone the repo and install dependencies**

```
git clone <repo-url>
cd cawmen-sandaigo
uv sync
```

**2. Start the backend**

```
just serve
```

The backend starts on `http://localhost:8000` by default.

**3. Launch the terminal client**

In a second terminal:

```
just tui
```

The TUI connects to the running backend and opens the spectator screen.

## Running the checks

The full local gate — lint, types, tests, and schema freshness — runs with:

```
just check
```

## Where this is going

The full vision is in [docs/vision.md](docs/vision.md). Development is being written up as it happens — articles covering each stage of the build live in the `articles/` directory.
