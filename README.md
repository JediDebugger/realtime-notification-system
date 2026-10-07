# Real-time notification system for a gaming platform

A Python solution to Globalli's coding challenge: players get in-app notifications when something happens to them in the game (level up, rare item, challenge, PvP) or in their social network (friend request, friend accepted, new follower).
Simulated game and social systems emit events; the notification system builds each notification, checks the recipient's preferences, and delivers it in-app.

## Quick start

**Prerequisites:** Python 3.11 or newer, macOS or Linux, and internet access on the first build (pip installs pytest).

```sh
./build.sh   # finds Python 3.11+, creates .venv, installs the package, byte-compiles
./run.sh     # runs the demo
./test.sh    # runs the test suite
```

`build.sh` uses `python3` if it's 3.11 or newer, and otherwise the newest `python3.N` on your `PATH` that is. To choose an interpreter yourself, delete `.venv` if you've already built, then run:

```sh
PYTHON=/path/to/python3.12 ./build.sh
```

Extra arguments to `./test.sh` go to pytest, e.g. `./test.sh -k friend`.

<details>
<summary>Windows (untested)</summary>

The scripts are bash. On Windows, these should be the equivalent steps, but they haven't been run on Windows:

```bat
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m notifications
.venv\Scripts\python -m pytest
```
</details>

## The demo

`./run.sh` replays the spec's four example triggers, the other event types, and two kinds of filtering. Here is an excerpt; the full run has 11 steps.

```
=== The spec's four example triggers ===

> game_engine.player_leveled_up(1, 15)                 # Aria (1) reaches level 15 -> notify 1
[in-app] to player 1: Congratulations! You've reached level 15!
  SENT LEVEL_UP to player 1 (Game Events)
...
> social_system.friend_request_accepted(1, 3)          # Aria (1) accepts Cyra's (3) request -> notify 3
[in-app] to player 3: Player 'Aria' accepted your friend request.
  SENT FRIEND_ACCEPTED to player 3 (Social Events)
...
=== Filtering: common items and preferences ===

> game_engine.item_acquired(2, "HealthPotion")         # Borin (2) gets a common item -> notify nobody
  IGNORED ItemAcquired: not notification-worthy

> preferences.set_enabled(1, Category.GAME, False)     # Aria (1) turns Game Events off

> game_engine.player_leveled_up(1, 16)                 # Aria (1) reaches level 16 -> suppressed
  SUPPRESSED LEVEL_UP to player 1: Game Events disabled
```

### Reading the demo output

- **`> call   # comment`** is the trigger, called the way a part of the platform would call it. The comment says who acts and who should be notified. The players are Aria (1), Borin (2), Cyra (3), and Dax (4).
- **`[in-app] ...`** lines, flush left, are what the player receives in the game client.
- **Indented lines** are the dispatcher's log of what it decided and why:
  - `SENT` gives the type, the recipient, and the category.
  - `SUPPRESSED` means the recipient turned that category off.
  - `IGNORED` means the event doesn't warrant a notification.

### The spec's calls in Python

The methods are the snake_case forms of the spec's calls, with the same argument order: the actor comes first.

| Spec | Python | Notifies |
|---|---|---|
| `gameEngine.playerLeveledUp(1, 15)` | `game_engine.player_leveled_up(1, 15)` | 1 |
| `gameEngine.itemAcquired(2, "SwordOfAzeroth")` | `game_engine.item_acquired(2, "SwordOfAzeroth")` | 2 |
| `socialSystem.friendRequestSent(3, 1)` | `social_system.friend_request_sent(3, 1)` | 1 |
| `socialSystem.friendRequestAccepted(1, 3)` | `social_system.friend_request_accepted(1, 3)` | 3 |
| *(not in spec)* | `game_engine.challenge_completed(player_id, challenge_name)` | the player |
| *(not in spec)* | `social_system.player_followed(follower_id, followed_id)` | the followed player |
| *(not in spec, optional)* | `game_engine.player_attacked(attacker_id, victim_id)` | the victim |
| *(not in spec, optional)* | `game_engine.player_defeated(winner_id, loser_id)` | the loser |

## Features

- **In-game events:** level up, rare item acquired, challenge completed, and PvP attacked or defeated (optional in the spec, implemented here).
- **Social events:** friend request, friend accepted, and new follower.
- **Preferences:** each player can turn Game Events and Social Events on or off.
- **Delivery:** an in-app channel that stands in for the game client. A failing channel is logged and doesn't stop other notifications.

## Design

```
GameEngine / SocialSystem --publish(event)--> InProcessEventBus --> NotificationDispatcher
                                                                     1. composer for the event type -> Notification (or none)
                                                                     2. recipient's preference for its category -> send or suppress
                                                                     3. send to every channel (in-app)
```

The decisions a reviewer is most likely to ask about (full log in [ARCHITECTURE.md §7](docs/ARCHITECTURE.md#7-decisions)):

- **Event bus** ([DEC-1, DEC-2](docs/ARCHITECTURE.md#7-decisions)): producers only build events and call `publish()`. They don't know the notification system exists, so new consumers or a real broker can be added without touching them.
- **Composers** ([DEC-3](docs/ARCHITECTURE.md#7-decisions)): one small function per event type decides the recipient, category, and wording. Adding an event type means adding a composer and one registry line; the dispatcher doesn't change.
- **Two error boundaries** ([DEC-7](docs/ARCHITECTURE.md#7-decisions)):
  - A bug in the notification pipeline can't break the game's call: the bus catches and logs any subscriber failure.
  - A malformed event (a bad id or a blank name) is the caller's bug. It's rejected with `ValueError` when the producer builds it, before anything is published.
  - The dispatcher catches only delivery errors from channels.
- **The recipient's preferences** ([DEC-5](docs/ARCHITECTURE.md#7-decisions)): they're checked against the notification's recipient, never the actor. The store receives the whole notification, so per-event-type preferences would be a store-only change.
- **In-process only** ([DEC-1](docs/ARCHITECTURE.md#7-decisions), [A-15](docs/REQUIREMENTS.md#4-ambiguities-and-gaps)):
  - "Real-time" here means a notification is delivered before the triggering call returns.
  - The spec puts delivery to the client out of scope, so there is no server or broker.

[ARCHITECTURE.md §3](docs/ARCHITECTURE.md#3-extension-walkthrough) walks through extending the system: a new event type, a push or email channel, per-type preferences, and a message broker.

## Assumptions that change behaviour

- **Only rare-or-better items notify** (rare, epic, legendary). Unknown item ids are ignored with a warning.
- **A friend acceptance notifies the original requester only.** `friend_request_accepted(1, 3)` notifies player 3, not player 1.
- **Every category is on** until a player turns it off.
- **Self-targeted social and PvP events notify nobody**, e.g. a friend request to yourself. The composer ignores them, the dispatcher logs `IGNORED`, and the game's call returns normally. Malformed events (bad ids, blank names) are rejected with `ValueError`.

The rest are in [REQUIREMENTS.md §4](docs/REQUIREMENTS.md#4-ambiguities-and-gaps).

## Project layout

```
src/notifications/
  producers.py     GameEngine, SocialSystem (simulated event sources)
  events.py        immutable events, each validating its own shape
  bus.py           InProcessEventBus (isolates producers from subscriber failures)
  dispatcher.py    compose -> check preferences -> send
  composers.py     one composer per event type, with the message templates
  notification.py  Notification, NotificationType, Category
  preferences.py   per-user, per-category on/off switches
  channels.py      InAppChannel (stands in for the game client)
  lookups.py       player names and the item catalog
  validation.py    shape checks shared by events and preferences
  app.py           build_app(): wiring plus demo seed data
  __main__.py      the demo
tests/             unit, acceptance (the spec's triggers end to end), build-script, demo
docs/              requirements, architecture, plan, AI process
```

## Docs

- [REQUIREMENTS.md](docs/REQUIREMENTS.md): the spec, broken into requirements, with the confirmed assumptions.
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): the approaches considered, the design, the extension walkthrough, and the decision log.
- [PLAN.md](docs/PLAN.md): the test-first implementation plan, task by task.
- [AI_PROCESS.md](docs/AI_PROCESS.md): how AI was used.

## How AI was used

The work went from requirements to architecture to a test-first plan with an AI assistant, reviewed and approved at each step. Implementation then ran task by task, with checkpoints for review. The prompts, the workflow, and where AI output was corrected are in [docs/AI_PROCESS.md](docs/AI_PROCESS.md).
