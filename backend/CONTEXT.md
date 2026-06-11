# Backend

The authoritative core of Cawmen Sandaigo: it owns all game state, runs the chase
mechanics and Case generation, holds the Dossier and Scenarios, and exposes everything
through a REST API. It owns the game-domain language for the whole system; frontends
render these concepts but do not redefine them.

## The Chase

**Detective**:
The player's role — the pursuer who follows the fugitive's trail across locations.
_Avoid_: Player character, agent, investigator

**Fugitive**:
The character being chased — commits a crime and flees across Locations leaving a trail of Clues. Always appears as a Person at Locations on their Fugitive Route.
_Avoid_: Criminal, thief, villain, suspect (until positively identified)

**Fugitive Route**:
The fugitive's secret timed path through Locations — each Location has an assigned day of arrival. Ends at the Escape Location. Generated deterministically from the Case Seed.
_Avoid_: Travel path, itinerary, schedule

**Escape Location**:
An unnamed, unreachable Location at the end of the Fugitive Route — when the fugitive arrives there the trail goes cold and the Case is lost. Never revealed to the player by name.
_Avoid_: Final location, safe house, off-grid

**Person**:
A named individual present at a Location — most are innocent bystanders or witnesses; the Fugitive also appears as a Person when co-located with the detective.
_Avoid_: NPC, character, contact

**In-Game Clock**:
A clock visible to the player, tracking both day and hour (e.g. "Monday 14:00"). The detective's actions consume hours within a day; once the day is spent the clock rolls over, the detective rests, and the fugitive relocates overnight. Gives temporal context to Clue staleness ("seen two days ago") without revealing the Case deadline explicitly.
_Avoid_: Timer, countdown, turn counter

**Action Cost**:
The hours an action removes from the detective's day — Move scales with the distance travelled, Interview costs roughly an hour. The central tension: information-gathering early in a Case is expensive enough that the fugitive pulls ahead, while a well-informed detective later spends fewer hours and can close the gap. Each day also reserves a fixed block of hours for the detective to rest.
_Avoid_: Time cost, action points, turn budget

**Day**:
One tick of the fugitive's movement and the unit of the Fugitive Route — the fugitive occupies exactly one Location per day, travelling between them overnight. The detective may take several actions within a day before the clock rolls to the next.
_Avoid_: Turn, round, step

## Actions

**Move**:
The detective's choice of which Location to travel to next after gathering Clues.
_Avoid_: Travel, jump, step

**Interview**:
The detective's action of questioning a Person at a Location to receive Clues. Witnesses answer truthfully; the Fugitive answers with plausible lies or deliberately vague responses.
_Avoid_: Question, talk, interrogate

**Wait**:
The detective's action of remaining at a Location for one day — advances the In-Game Clock without changing position. Used to let the Fugitive catch up, or to gather more Clues before moving.
_Avoid_: Rest, pause, stay

**Arrest**:
The detective's explicit action of naming a specific Person as the Fugitive — must be triggered deliberately, never triggered by proximity alone.
_Avoid_: Accuse, catch, apprehend

## Case and Crime

**Case**:
A single playthrough — begins when a crime is committed and a fugitive flees, ends when the detective either arrests the fugitive or exhausts their leads.
_Avoid_: Mission, game, run

**Case Outcome**:
The terminal status of a Case: `won` when the detective catches the fugitive (co-location at Stage 1; a correct Arrest from Stage 3 on), or `lost` when the fugitive reaches the Escape Location. An in-progress Case has no outcome yet. Losing is a normal end state, not an error. On any outcome the full Fugitive Route is revealed so the player can replay the chase.
_Avoid_: Win/lose flag, game over, result code

**Crime**:
The act that opens a Case — AI-generated, thematically matched to the Fugitive, and mechanically relevant as a soft filter: the Crime type hints at the Fugitive's motive and can be used to narrow the Suspect roster in the Dossier.
_Avoid_: Theft, heist, incident

**Clue**:
A narrative fragment gathered at a Location — reveals either where the Fugitive went next, a detail about the Fugitive's identity or traits, or hints at motive connecting back to the Crime.
_Avoid_: Hint, tip, evidence

**Case Seed**:
A UUID assigned to a Case at creation — used as the random seed so that any Case with the same Seed and the same preset parameters generates identically (same Suspect, crime, and travel path).
_Avoid_: Case ID, random seed, replay ID

## The Dossier

**Dossier**:
The Scenario's Suspect roster as seen by the detective — queryable via semantic search against AI-generated prose profiles. Multiple Dossier Filters are ANDed together, each narrowing the remaining candidate set. Shared across all Campaigns played within the same Scenario.
_Avoid_: Interpol database, criminal database, suspect list

**Dossier Filter**:
A natural language query the detective applies to the Dossier — semantically matched against Suspect profiles via vector search. Multiple active Filters are ANDed to progressively narrow the candidate set.
_Avoid_: Search, query, tag

**Suspect**:
A known criminal defined in a Scenario — any of whom may be the Fugitive in a given Case. Shared across all Campaigns in the same Scenario.
_Avoid_: Criminal, villain, character

## World and Content

**Location Graph**:
The full set of Locations and their connections defined in a Scenario — Cases use a subgraph derived by withholding Locations assigned to later Location Stages.
_Avoid_: Map, world map, travel graph

**Location Stage**:
A tier assigned to each Location in the full Location Graph that controls when it becomes available — early-stage Locations appear in the first Cases; later-stage Locations are added additively as the Campaign progresses.
_Avoid_: Location tier, location level, unlock

**Scenario**:
A curated world configuration — a Location Graph with staged Locations, created and edited via the Scenario Editor. Serves as the fixed foundation that a Campaign is played within.
_Avoid_: World, map, template, scope

**Scenario Editor**:
A separate workflow (independent of gameplay) for creating and editing Scenarios — seeded by a short prompt, then refined by adding, removing, or updating Locations and connections.
_Avoid_: World builder, map editor, admin tool

## The Campaign Arc

**Player**:
An authenticated identity that owns Campaigns and persists across frontends.
_Avoid_: User, account, profile

**Campaign**:
A specific player's run through a Scenario — the Scenario's Suspect roster is shared, but Case details (Fugitive, Crime, Route) are reproducibly generated from the Scenario using Case Seeds. Culminates in confronting Cawmen Sandaigo.
_Avoid_: Run, game, playthrough

**Cawmen Sandaigo**:
The mastermind Fugitive — the final target of every Campaign, only confronted once the detective has accumulated enough evidence across earlier Cases that traces back to the mastermind.
_Avoid_: Boss, final villain, end boss

**Mastermind Evidence**:
Clues gathered across Cases that collectively point toward Cawmen Sandaigo — accumulates over a Campaign and eventually unlocks the final confrontation.
_Avoid_: Boss clues, meta-clues, campaign progress

**Language Preference**:
A player's chosen language for a session — AI generates all game text directly in this language on demand; text is not stored per-language.
_Avoid_: Locale, translation, language setting
