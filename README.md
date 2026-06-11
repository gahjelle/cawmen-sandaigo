# Cawmen Sandaigo

A geography and detective game where you play a detective chasing a fugitive across cities. The fugitive moves on a secret schedule, leaving clues at each location. Your job is to follow the trail and make the arrest before they slip away for good.

## What the game looks like right now

The current build is a playable detective chase in the terminal. A fugitive is assigned a secret route through a handful of European cities and starts moving the moment the case opens. You play the detective: each turn you pick an adjacent city to travel to, trying to be in the same place as the fugitive before they reach the escape location and the trail goes cold.

The backend runs all the game logic and exposes a REST API; the terminal client connects to it, shows your current location and neighbors, and accepts your move. When the case ends — win or lose — the full fugitive route is revealed so you can see where they went.

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
