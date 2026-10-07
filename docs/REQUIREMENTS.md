# Requirements: Real-Time Notification System

**Source:** `Coding Challenge.pdf` (Globalli engineering hiring exercise, 3 pages). The PDF is not committed. This file is the working summary of it.
**Language:** Python. The PDF doesn't name a language.
**Status:** Approved 2026-10-06. All assumptions in §4 are confirmed, and §6 records the explicit answers.

Status labels used below follow the spec's own wording: **Required**, **Optional** ("optional, but good to consider"), **Recommended**, **Suggested** ("you can…").

---

## 1. Functional requirements

### 1.1 Notification types

| ID | Event | Spec wording | Status | Category |
|---|---|---|---|---|
| FR-1 | Level Up | "When a player reaches a new level." | Required | Game Events |
| FR-2 | Item Acquired | "When a player obtains a rare or valuable item." | Required | Game Events |
| FR-3 | Challenge Completed | "When a player completes a challenging quest or achievement." | Required | Game Events |
| FR-4 | PvP: attacked / defeated | "When a player is attacked or defeated by another player (optional, but good to consider)." | **Optional, in scope** (Q5) | Game Events (A-12) |
| FR-5 | Friend Request | "When another player sends them a friend request." | Required | Social Events |
| FR-6 | Friend Accepted | "When a friend request is accepted." | Required | Social Events |
| FR-7 | New Follower | "When another player starts following them." | Required | Social Events |

### 1.2 Processing

| ID | Requirement | Status |
|---|---|---|
| FR-8 | **Receive events** from separate parts of the platform: game events come from a game engine, social events from a social system. Capture both and pass them to the notification system. The producers are simulated. | Required |
| FR-9 | **Determine the notification type** for each event, and its recipient. The spec states the type; the recipient is implied (see §2). | Required |
| FR-10 | **Create a `Notification` object** for it. | Required |
| FR-11 | **Content** is "clear, concise, and informative" and matches the spec's example messages where they exist (§2.1). | Required |
| FR-12 | **User preferences:** each user can enable or disable notifications per category ("Game Events", "Social Events"). A simple dict/map is acceptable. | Required |
| FR-13 | **Check the recipient's preference** for the notification's category. Don't send if it's disabled. | Required |
| FR-14 | **Send** through the in-app channel, in real time. The game client's receiving mechanism is assumed to exist and may be mocked. | Required |
| FR-15 | **Example usage:** demonstrate how parts of the game trigger events. It must "clearly show how events are triggered and how the notification system responds." | Required |

The spec gives the pipeline order as: "determine the type of notification, create the Notification object, check user preferences, and send the notification" (FR-9 → FR-10 → FR-13 → FR-14).

---

## 2. Who receives what

### 2.1 The spec's example triggers

As written in the spec (Java/C#-style syntax):

```
gameEngine.playerLeveledUp(1, 15);             // User 1 leveled up to 15
gameEngine.itemAcquired(2, "SwordOfAzeroth");  // User 2 acquired an item
socialSystem.friendRequestSent(3, 1);          // User 3 sent a friend request to user 1
socialSystem.friendRequestAccepted(1, 3);      // User 1 accepted friend request from 3
```

| # | Call | Actor | **Recipient** | Not notified | Category | Preference checked | Message |
|---|---|---|---|---|---|---|---|
| T1 | `playerLeveledUp(1, 15)` | 1 | **User 1** | n/a | Game | User 1, Game Events | "Congratulations! You've reached level 15!" *(spec text)* |
| T2 | `itemAcquired(2, "SwordOfAzeroth")` | 2 | **User 2** | n/a | Game | User 2, Game Events | "You've acquired the legendary Sword of Azeroth!" *(spec text; needs a display name and rarity the event doesn't carry, see A-5)* |
| T3 | `friendRequestSent(3, 1)` | 3 | **User 1** | User 3 (sender) | Social | User 1, Social Events | "Player '‹name of 3›' has sent you a friend request." *(spec template)* |
| T4 | `friendRequestAccepted(1, 3)` | 1 | **User 3** | User 1 (accepter) | Social | User 3, Social Events | "Player '‹name of 1›' accepted your friend request." *(see A-9, A-11)* |

Points that are easy to get wrong:

- **The arguments are ordered actor first, not requester first.** In T3, user 3 is the requester and comes first. In T4, user 3 is still the requester but comes *second*, because user 1 is the one acting. If you read T4 the way you read T3 ("first argument is the requester"), you notify the wrong user.
- For game events (T1, T2) the actor is the recipient. For social events (T3, T4) the recipient is the second argument.
- The preference that gets checked is always the **recipient's**, never the actor's. If user 1 has disabled Social Events, T3 is suppressed. User 3's settings play no part in T3.
- One event produces at most one notification, for exactly one recipient. Nothing goes to friends or followers (A-10).

### 2.2 Events with no spec trigger

The spec gives no call signature or message for these. The signatures below use the same actor-first convention. Python names are snake_case (A-4).

| FR | Call | **Recipient** | Not notified | Message |
|---|---|---|---|---|
| FR-3 | `game_engine.challenge_completed(player_id, challenge_name)` | player_id | n/a | "Well done! You've completed '‹challenge›'!" |
| FR-7 | `social_system.player_followed(follower_id, followed_id)` | followed_id | follower_id | "Player '‹follower›' started following you." |
| FR-4 | `game_engine.player_attacked(attacker_id, victim_id)` | victim_id | attacker_id | "Player '‹attacker›' is attacking you!" |
| FR-4 | `game_engine.player_defeated(winner_id, loser_id)` | loser_id | winner_id | "You've been defeated by Player '‹winner›'." |

---

## 3. Technical requirements and deliverables

### 3.1 Technical requirements

| ID | Requirement | Source | Status |
|---|---|---|---|
| TR-1 | **Notification class:** "You are provided with a `Notification` class." The PDF doesn't include it (A-1). | Spec | Required |
| TR-2 | **Notification handling:** design the components for sending, checking preferences, and interacting with the game and social systems. The spec suggests "interfaces, services, and classes" and asks for a structure that stays flexible and maintainable "as the system grows". In Python, "interfaces" means `typing.Protocol`. | Spec | Required |
| TR-3 | **Event handling:** a mechanism that receives events from separate producers and hands them to the notification system. | Spec | Required |
| TR-4 | **External delivery:** final delivery and display belong to an external dependency, which we may "mock or simulate". | Spec | Required |
| TR-5 | **Tests:** "You can simulate these event triggers in your test code." | Spec | Suggested (required by CLAUDE.md, test-first) |
| TR-6 | **It must compile and run:** "We will clone the repo and run it using the build scripts you provide." | Spec | Required |
| TR-7 | One build command and one run command, from a clean clone. | CLAUDE.md | Required |

### 3.2 Deliverables

| ID | Deliverable | Status |
|---|---|---|
| D-1 | A public GitHub repo, owned by the candidate, containing the project. | Required |
| D-2 | Build scripts that the graders use to build and run the project. | Required |
| D-3 | `README.md` explaining how to run it and the main features included. | Recommended |
| D-4 | A record of AI use: "the prompts you used and the process you followed to go from requirements to a working solution. Workflows and patterns used, tools used. **Keep that as part of the deliverable.**" | Required |
| D-5 | Be ready to defend the result in the interview: the architecture patterns and why, the tradeoffs, what adding features would involve, and how the system works. This isn't a file deliverable. `docs/ARCHITECTURE.md` (with its Decisions log) serves as preparation. | Interview |
| D-6 | `Coding Challenge.pdf` must not be committed. | CLAUDE.md |

### 3.3 What "it runs" means (acceptance criteria)

Start from a clean clone on macOS or Linux, with only Python ≥ 3.11 on `PATH`. Then:

1. **Build** (`./build.sh`) creates a local virtualenv, installs the project and its test dependency, and byte-compiles the sources so that syntax errors fail the build. It exits 0.
2. **Run** (`./run.sh`) runs the example-usage scenario and exits 0. For each event, the output shows the trigger call, the resolved recipient, the category, the preference decision (sent or suppressed), and the delivered message text.
3. The run covers at least:
   - T1–T4, with messages matching §2.1.
   - One Challenge Completed, one New Follower, and one PvP attack and defeat.
   - One notification suppressed because its recipient disabled that category.
4. **Test** (`./test.sh`) passes. The tests assert the recipient and message for T1–T4, plus the suppression path.
5. Nothing else is needed: no server, database, Docker, or external service. The runtime uses only the standard library. pytest is the only dev dependency.

---

## 4. Ambiguities and gaps

Each entry gives what the spec says, the assumption, and the reasoning. All were confirmed on 2026-10-06. **→ Q*n*** points to the explicit answer in §6.

### Spec artifacts and platform

**A-1. The `Notification` class is referenced but not provided.** → Q1
- *Spec:* "Notification Class: You are provided with a `Notification` class." The PDF contains no class, file, or field list.
- *Assumption:* Define our own minimal immutable `Notification` with these fields:
  - `id`
  - `recipient_id`
  - `type`: LEVEL_UP, ITEM_ACQUIRED, …
  - `category`: GAME or SOCIAL
  - `message`
  - `created_at`
  - `data`: a structured payload, e.g. level, item id, actor id

  It lives in its own module, so a provided class can be swapped in later.
- *Reasoning:* The dispatcher must "create the Notification object", so this is a core contract and we can't wait for it. Keeping structured fields alongside `message` lets a client render richer UI without parsing text.

**A-2. "Compile and run" for a Python project.** → Q7
- *Spec:* "The resulting product must compile and run… using the build scripts you provide." The examples use Java/C#-style syntax, and the spec talks about "interfaces". No language is named.
- *Assumption:* Python is acceptable. "Compile" maps to a build step that can fail: set up the env, install, byte-compile. "Interfaces" maps to `typing.Protocol`.
- *Reasoning:* This is the closest match to what the graders expect: a build that fails loudly when the code is broken, and a run that proves it works.

**A-3. Build tooling, OS, Python version.** → Q7
- *Spec:* "build scripts". Nothing on OS or versions.
- *Assumption:* Bash scripts `build.sh`, `run.sh`, and `test.sh` at the repo root, for macOS and Linux. The README also lists the equivalent raw `python -m …` commands for Windows. Python ≥ 3.11, and `build.sh` fails with a clear message on older versions.
- *Reasoning:* Shell scripts need nothing but bash, and `make` isn't always installed. A stdlib-only runtime can't break on dependency resolution. The `python3` bundled with macOS is 3.9, and the version check makes that failure obvious. **Revised at checkpoint 3:** `build.sh` first looks for `python3.13`, `python3.12` and `python3.11` before falling back to `python3`, so a Mac with a newer Python installed builds without setting `PYTHON` (ARCHITECTURE DEC-16).

**A-4. Method names.** → Q8
- *Spec:* camelCase in C-style syntax (`gameEngine.playerLeveledUp(1, 15)`).
- *Assumption:* PEP 8 snake_case (`game_engine.player_leveled_up(1, 15)`), with the same argument order. The README maps each name to the spec's name.
- *Reasoning:* Idiomatic Python, with the mapping kept for traceability.

### Event data

**A-5. Item Acquired: what counts as "rare or valuable", and where the display data comes from.** → Q2
- *Spec:* Notify when a player obtains "a rare or valuable item". The trigger passes only `(2, "SwordOfAzeroth")`, yet the expected message is "You've acquired the **legendary** **Sword of Azeroth**!". The rarity and display name aren't in the event. Splitting the CamelCase id gives "Sword *Of* Azeroth", which doesn't match.
- *Assumption:*
  - A small in-memory item catalog maps each item id to a display name and a rarity tier (common, uncommon, rare, epic, legendary).
  - Notify only for rare and above.
  - An unknown item id produces no notification and logs a warning.
  - "Valuable" is treated as covered by rarity. Monetary value isn't modelled.
- *Reasoning:* The example message can't be produced without this data. `itemAcquired` is a generic event that fires for any item, so the "rare or valuable" filter has to live somewhere. The spec states it as a notification rule, so it goes in the notification layer.

**A-6. Challenge Completed: no signature, no message, no difficulty data.** → Q10
- *Spec:* "When a player completes a challenging quest or achievement." No trigger or example is given.
- *Assumption:* `challenge_completed(player_id, challenge_name)`. Every such event notifies, with no difficulty filter. Quests and achievements share one notification type.
- *Reasoning:* Unlike `itemAcquired`, the event name already says a challenge was completed, so the game engine has decided it's notable. Splitting quests from achievements would add a type with no behavioural difference.

**A-7. New Follower: no signature, no message.** → Q10
- *Spec:* "When another player starts following them."
- *Assumption:* `player_followed(follower_id, followed_id)`. The followed player is notified. The follower isn't.
- *Reasoning:* Actor first, matching `friendRequestSent`.

**A-8. Player display names.**
- *Spec:* "Player 'X' has sent you a friend request." The events carry only integer ids.
- *Assumption:* An in-memory player directory maps each id to a display name. An unknown id falls back to the id itself ("Player '3' …").
- *Reasoning:* A bare number isn't "informative" to a player. The directory is the minimal stand-in for a real profile service.

### Recipients

**A-9. Friend Accepted: who is notified.** → Q3
- *Spec:* "When a friend request is accepted." It doesn't say who is told. The trigger is `friendRequestAccepted(1, 3) // User 1 accepted friend request from 3`, with no example message.
- *Assumption:* Notify the original requester (user 3) only: "Player '‹name of 1›' accepted your friend request." The accepter (user 1) isn't notified.
- *Reasoning:* The accepter performed the action and already knows. The requester is the one waiting for an outcome.

**A-10. One recipient per event, no fan-out.**
- *Spec:* Every example message is in the second person, addressed to one player. Nothing mentions telling friends or followers about each other's achievements.
- *Assumption:* Each event produces at most one notification, for one recipient. No "your friend reached level 15".
- *Reasoning:* This follows the spec's examples. Fan-out is a feature addition.

### Content

**A-11. Messages for types the spec has no example for.** → Q10
- *Spec:* Examples exist only for Level Up, Item Acquired, and Friend Request.
- *Assumption:* Use the messages in §2.1 (T4) and §2.2. They follow the spec's style: second person, "Player 'X'" for other players, one short sentence.
- *Reasoning:* This keeps every message consistent with the three the spec defines.

### Preferences

**A-12. Categories and granularity.** → Q4
- *Spec:* "each user can enable or disable notifications for each category of events (e.g., 'Game Events,' 'Social Events')".
- *Assumption:* Exactly two categories, Game Events and Social Events. Preferences are per category, not per event type. PvP goes under Game Events, because the spec lists it under In-Game Events.
- *Reasoning:* The spec says the granularity is the category, and the two named categories cover every listed event.

**A-13. Default preference state.** → Q4
- *Spec:* Says nothing about the initial state, or about users with no entry.
- *Assumption:* Enabled by default (opt-out). A user with no entry, or with a missing category, receives notifications.
- *Reasoning:* The example triggers come with no preference setup and are clearly expected to produce notifications.

**A-14. What happens to a suppressed notification.**
- *Spec:* "create the Notification object, check user preferences, and send". It doesn't say what happens to one that fails the check.
- *Assumption:* Follow the spec's order. A suppressed notification is discarded: not delivered, queued, or stored. The decision is logged so the demo can show it. Re-enabling a category doesn't replay missed notifications.
- *Reasoning:* No persistence or inbox is asked for.

### Delivery

**A-15. What "real-time" means.** → Q6
- *Spec:* "Players should receive real-time notifications". "Assume the game client has a mechanism to receive these notifications in real-time." Display and final delivery are out of scope and may be mocked.
- *Assumption:*
  - A notification is dispatched as soon as its event is received, in the same process, with no batching, polling, or scheduling.
  - The client is a mock in-app delivery client that records and prints what it receives.
  - There's no network server (WebSocket or HTTP) and no message broker.
  - The program runs the scenario and exits.
- *Reasoning:* The spec puts transport to the client out of scope and tells us to mock it.

**A-16. "Multiple Notification Channels" vs. in-app only.**
- *Spec:* The heading says "Multiple Notification Channels". The body says "focus on in-app notifications", with push and email mentioned only as the real-world case.
- *Assumption:* Implement only the in-app channel. Keep sending behind a channel interface, so that adding push or email means adding a class rather than changing the dispatcher.
- *Reasoning:* The body text is the instruction. The heading signals that the design should make more channels easy to add.

**A-17. Delivery failures.**
- *Spec:* Silent.
- *Assumption:* If the delivery client raises an error, it's logged and processing continues with the next event. No retries and no dead-letter queue.
- *Reasoning:* One failed delivery shouldn't block notifications to other players. Retries and durability need persistence, which is out of scope.

### Validation

**A-18. Invalid or inconsistent events.**
- *Spec:* Silent on cases such as accepting a request that was never sent, sending a friend request to yourself, repeated follows, or a level that isn't higher than before.
- *Assumption:* The notification system doesn't own or check social-graph or player state. It trusts the producing system's business rules. It validates only the shape of an event: ids are positive integers, levels are ≥ 1, names are non-empty. It also rejects social and PvP events where the actor and the recipient are the same player.
- *Reasoning:* The social system is the source of truth for friendships, and mirroring its state here would couple the two. Shape checks are cheap and catch programming errors.

### Scope

**A-19. PvP (optional).** → Q5
- *Spec:* "When a player is attacked or defeated by another player (optional, but good to consider)." No trigger or message is given.
- *Decision:* Implement both events once the required features work:
  - `player_attacked(attacker_id, victim_id)`
  - `player_defeated(winner_id, loser_id)`

  The **player who was attacked or defeated** is notified. The attacker or winner isn't. Both are in the Game Events category. One known limitation: "attacked" can fire many times per fight, and there's no throttling.
- *Reasoning:* It's in the spec, it's cheap once the pipeline exists, and it shows the design extends.

### Deliverables

**A-20. Format of the AI-process record.** → Q9
- *Spec:* Prompts, process, workflows, patterns, and tools: "Keep that as part of the deliverable." No format is given.
- *Assumption:* `docs/AI_PROCESS.md` covers the tools used, the workflow (requirements → architecture → test-first implementation), the key prompts verbatim, and where AI output was corrected or rejected. `CLAUDE.md` and the `docs/` trail are committed as supporting evidence.
- *Reasoning:* The first part of the interview is about this, and keeping it in the repo satisfies "part of the deliverable".

**A-21. Spec content in a public repo.** → Q10
- *Spec:* Delivery is a public repo, and CLAUDE.md forbids committing the PDF.
- *Assumption:* Committing this file is fine, even though it quotes the spec's requirement wording, example messages, and the four triggers.
- *Reasoning:* The quotes are needed for traceability.

---

## 5. Out of scope

### 5.1 Explicitly out of scope (stated in the spec)

- **Displaying notifications in the game client:** "The actual display of the notification in the game client is not part of this exercise's scope."
- **Final delivery to the client:** "assume that there is an existing notification client or mechanism to handle the final delivery… You are free to mock or simulate this."
- **Push, email, and other non-in-app channels:** "In a real-world scenario, you'd have push notifications, email, etc., but we're simplifying."
- **A real game engine and social system:** "you can simulate these events".
- **Anything beyond the listed features until those are complete:** "Focus only on the required features… additional features are welcome if you decide to add them after you completed."

### 5.2 Not mentioned in the spec; treated as out of scope

- Persistence: a database, notification history or inbox, read/unread state, and holding notifications for offline players.
- Network transport or API: a WebSocket or HTTP server, or a message broker.
- Authentication and authorization.
- Retries, durability, rate limiting, batching or digests, and de-duplication.
- Per-event-type preferences, quiet hours, and a preference UI or preference persistence.
- Localization.
- Fan-out to friends or followers.
- Multi-process or distributed deployment.

`docs/ARCHITECTURE.md` covers where the main ones would plug in.

---

## 6. Resolved questions (2026-10-06)

| Q | Question | Answer | Refs |
|---|---|---|---|
| Q1 | Define our own `Notification` class, or wait for the "provided" one? | Define our own. | A-1 |
| Q2 | Items: use a catalog with rarity, notify only for rare and above, and skip unknown items? | Yes. | A-5 |
| Q3 | Friend Accepted: notify only the original requester? | Yes. | A-9 |
| Q4 | Exactly two categories, PvP under Game, and everything enabled by default? | Yes. | A-12, A-13 |
| Q5 | PvP: implement it, or document the design only? | Implement it. The attacked or defeated player is notified. | A-19 |
| Q6 | Real-time means in-process immediate dispatch to a mocked client, with a CLI demo and no server? | Yes. | A-15 |
| Q7 | Use `build.sh`, `run.sh`, and `test.sh`, and require Python ≥ 3.11? | Yes. | A-2, A-3 |
| Q8 | snake_case or the spec's camelCase for method names? | snake_case. | A-4 |
| Q9 | Use a curated `docs/AI_PROCESS.md`, and commit `CLAUDE.md` and `docs/`? | Yes. | A-20 |
| Q10 | Approve the signatures and messages in §2.2 and T4, and quoting the spec in a public repo? | Yes. | A-6, A-7, A-11, A-21 |
