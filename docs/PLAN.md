# Implementation Plan: Real-Time Notification System

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Track progress with the checkboxes in the task overview.

**Goal:** A Python notification system that turns simulated game and social events into in-app notifications, honours per-category user preferences, and runs from a clean clone with `./build.sh` and `./run.sh`.
**Architecture:** An in-process synchronous event bus carries immutable events from simulated producers to a `NotificationDispatcher`. The dispatcher runs the spec's pipeline: compose (one composer per event type), check the recipient's preferences, then send to the in-app channel. See [ARCHITECTURE.md](ARCHITECTURE.md).
**Tech stack:** Python ≥ 3.11 standard library; pytest; bash build scripts.
**Spec:** [REQUIREMENTS.md](REQUIREMENTS.md) (approved) and [ARCHITECTURE.md](ARCHITECTURE.md) (approved).

## Global constraints

Every task must respect these.

- Python ≥ 3.11. The runtime uses only the standard library, and pytest is the only dev dependency.
- The package is `notifications`, under `src/`. The entry point is `python -m notifications`.
- The commands are `./build.sh`, `./run.sh`, and `./test.sh`. They must work on macOS and Linux from a clean clone.
- Producer methods use the snake_case form of the spec's names and keep the spec's argument order: actor first.
- The spec's messages must match verbatim: `Congratulations! You've reached level 15!`, `You've acquired the legendary Sword of Azeroth!`, `Player 'X' has sent you a friend request.`
- The categories are `Game Events` and `Social Events`, and every category is enabled by default.
- `Coding Challenge.pdf` is never committed.
- Test-first: each task's listed tests are written and seen failing before any implementation.
- No dependencies or features beyond REQUIREMENTS.md without asking.

## Review focus

These are inputs the spec implies but doesn't spell out, and the most likely to bite a user. Each has a test in the task that owns it.

1. **Booleans and numeric strings as ids.** `True` and `"1"` must raise `ValueError`. Python treats `True` as the int `1`, so a naive `isinstance(x, int)` check lets it through. Tested in Task 2, and the same helper covers every later event.
2. **Self-targeted social and PvP events.** A friend request to yourself, accepting your own request, following yourself, or attacking yourself must raise `ValueError`, and nothing is sent. Tested in Tasks 13–16.
3. **Blank text fields.** An empty or whitespace-only item id or challenge name must raise `ValueError`. Tested in Tasks 11–12.
4. **Preferences on the wrong person or the wrong category.** The actor's settings must never matter, and disabling one category must not block the other. Tested in Tasks 8 and 13.
5. **Item ids that differ only in case.** `"swordofazeroth"` isn't in the catalog. It's ignored, with a warning that names the id so the mismatch is visible. Tested in Tasks 10–11.

## Fixed strings used across tasks

Tests in several tasks assert these exact strings. Define each one once, in the module named.

| What | Exact text | Defined in |
|---|---|---|
| In-app output line | `[in-app] to player {recipient_id}: {message}` | `channels.py` (Task 4) |
| Logger name | `notifications` | all modules |
| Sent (INFO) | `SENT {TYPE} to player {id} ({category label})`, e.g. `SENT LEVEL_UP to player 1 (Game Events)` | `dispatcher.py` (Task 5) |
| No composer (WARNING) | `IGNORED {EventClass}: no composer registered` | `dispatcher.py` (Task 5) |
| Composer returned `None` (INFO) | `IGNORED {EventClass}: not notification-worthy` | `dispatcher.py` (Task 5) |
| Suppressed (INFO) | `SUPPRESSED {TYPE} to player {id}: {category label} disabled` | `dispatcher.py` (Task 8) |
| Channel error (ERROR, with traceback) | `Channel {ChannelClass} failed for notification {notification id}` | `dispatcher.py` (Task 9) |
| All channels failed (ERROR) | `FAILED {TYPE} to player {id}: every channel failed` | `dispatcher.py` (Task 9) |
| Unknown item (WARNING) | `Unknown item id '{item_id}'; not notifying` | `composers.py` (Task 11) |

Message templates, all in `composers.py`:

| Type | Template |
|---|---|
| `LEVEL_UP` | `Congratulations! You've reached level {new_level}!` |
| `ITEM_ACQUIRED` | `You've acquired the {rarity label} {item name}!` |
| `CHALLENGE_COMPLETED` | `Well done! You've completed '{challenge_name}'!` |
| `FRIEND_REQUEST` | `Player '{sender name}' has sent you a friend request.` |
| `FRIEND_ACCEPTED` | `Player '{accepter name}' accepted your friend request.` |
| `NEW_FOLLOWER` | `Player '{follower name}' started following you.` |
| `PLAYER_ATTACKED` | `Player '{attacker name}' is attacking you!` |
| `PLAYER_DEFEATED` | `You've been defeated by Player '{winner name}'.` |

Demo seed data in `app.py` (Task 10):
- **Players:** `{1: "Aria", 2: "Borin", 3: "Cyra", 4: "Dax"}`
- **Items:** `SwordOfAzeroth` → ("Sword of Azeroth", LEGENDARY); `DragonScaleShield` → ("Dragon Scale Shield", EPIC); `HealthPotion` → ("Health Potion", COMMON)

## How to run each task

1. Write the tests listed under **Tests first**.
2. Run `./test.sh` and confirm the new tests fail, and fail for the expected reason (missing name or wrong value), not because of a typo.
3. Write the minimum code that makes them pass.
4. Run `./test.sh`. The whole suite must be green, not just the new tests.
5. Run `./run.sh`. It must still exit 0.
6. Commit, one commit per task, with one red/green evidence line in the body, e.g. `Red: 5 new tests failed (ModuleNotFoundError: notifications.notification) → Green: 23 passed`. Tick the task's checkbox in the task overview in the same commit.

---

## Task overview

| # | Task | Phase | Covers |
|---|---|---|---|
| [x] 1 | Project skeleton and build scripts | Slice | TR-6, TR-7, D-2, D-6 |
| [x] 2 | Notification and level-up event models | Slice | FR-10, A-1, A-18 |
| [x] 3 | Level-up composer and registry | Slice | FR-1, FR-9, FR-11 |
| [x] 4 | In-app channel | Slice | FR-14, TR-4 |
| [x] 5 | Dispatcher happy path, default-on preferences | Slice | FR-9, FR-13 (default), FR-14 |
| [x] 6 | In-process event bus | Slice | FR-8, TR-3 |
| [ ] 7 | Game engine, wiring, and demo: **slice complete** | Slice | FR-1, FR-8, FR-15 (T1) |
| [ ] 8 | Per-category preferences and suppression | Outward | FR-12, FR-13, A-13, A-14 |
| [ ] 9 | Delivery failures | Outward | A-17 |
| [ ] 10 | Player directory and item catalog | Outward | A-5, A-8 |
| [ ] 11 | Item Acquired | Outward | FR-2, T2 |
| [ ] 12 | Challenge Completed | Outward | FR-3 |
| [ ] 13 | Social system and Friend Request | Outward | FR-5, T3 |
| [ ] 14 | Friend Accepted | Outward | FR-6, T4 |
| [ ] 15 | New Follower | Outward | FR-7 |
| [ ] 16 | PvP attacked and defeated | Outward | FR-4 |
| [ ] 17 | Full example-usage scenario | Outward | FR-15 |
| [ ] 18 | README and clean-clone check | Wrap-up | D-1, D-3 |

**Slice (Tasks 1–7):** `./run.sh` prints the level-up notification for player 1, end to end through every real component. Everything after that adds behaviour around a pipeline that already works.

---

## Slice: level-up to in-app notification

### Task 1: Project skeleton and build scripts

**Files:**
- Create:
  - `pyproject.toml`
  - `build.sh`, `run.sh`, `test.sh` (all executable)
  - `.gitignore`
  - `src/notifications/__init__.py`
  - `src/notifications/__main__.py`
  - `tests/test_demo.py`
- Setup: `git init` if the folder isn't a repo yet.

**Contents:**
- **`pyproject.toml`:**
  - project `notifications`, `requires-python = ">=3.11"`, no runtime dependencies
  - optional `dev = ["pytest"]`
  - setuptools with `src` layout
  - `[tool.pytest.ini_options] testpaths = ["tests"]`
- **`build.sh`** (`set -euo pipefail`):
  - Uses `${PYTHON:-python3}`. If its version is below 3.11, it exits non-zero with a message naming 3.11.
  - Creates `.venv` if it's missing.
  - Runs `.venv/bin/pip install -e ".[dev]"`.
  - Runs `.venv/bin/python -m compileall -q src`.
- **`run.sh`:** if `.venv` is missing, prints "run ./build.sh first" and exits 1. Otherwise runs `.venv/bin/python -m notifications`.
- **`test.sh`:** runs `.venv/bin/python -m pytest "$@"`.
- **`.gitignore`:** `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/`, `*.pdf`.
- **`__main__.py`:** prints a single title line for now.

**Tests first:**
- `test_demo.py::test_demo_runs_and_exits_zero`: runs `[sys.executable, "-m", "notifications"]` in a subprocess and asserts `returncode == 0`. It fails until the package and `__main__` exist.

**Done when:**
- In a copy of the folder without `.venv`, `./build.sh`, `./test.sh`, and `./run.sh` each exit 0.
- Running `./build.sh` a second time also succeeds.
- `PYTHON=/usr/bin/python3 ./build.sh` (3.9 on macOS) exits non-zero with the version message. If no older interpreter is available, temporarily raise the minimum to check the failure path, then revert.
- A deliberate syntax error in `src/` makes `./build.sh` fail. Check once, then revert.
- `git status` doesn't list the PDF.

### Task 2: Notification and level-up event models

**Files:**
- Create:
  - `src/notifications/notification.py`
  - `src/notifications/events.py`
  - `tests/test_notification.py`
  - `tests/test_events.py`

**Interfaces produced:**
- `Category(Enum)`: `GAME = "Game Events"`, `SOCIAL = "Social Events"`.
- `NotificationType(Enum)`: `LEVEL_UP`. Later tasks add one member each.
- `Notification`, a frozen dataclass with fields:
  - `recipient_id: int`
  - `type: NotificationType`
  - `category: Category`
  - `message: str`
  - `data: Mapping[str, object]`, stored as a read-only `MappingProxyType` over a copy of the input (DEC-15)
  - `id: str`, defaulting to `str(uuid4())`
  - `created_at: datetime`, defaulting to `datetime.now(UTC)`
- `Event`, a frozen dataclass marker base.
- `PlayerLeveledUp(Event)`: `player_id: int`, `new_level: int`.
- Private helpers in `events.py`, reused by every later event:
  - `_check_id(field: str, value: object) -> None`: raises `ValueError` unless the value is an `int`, not a `bool`, and greater than 0.
  - `_check_text(field: str, value: object) -> None`: raises `ValueError` unless the value is a `str` that's non-blank after `.strip()`.

**Tests first:**

`test_notification.py`:
- `test_notification_stores_its_fields`
- `test_notification_is_immutable`: assigning `message` raises `dataclasses.FrozenInstanceError`.
- `test_notification_data_is_read_only`: `n.data["level"] = 16` raises `TypeError`.
- `test_notification_data_is_a_copy_of_the_input`: changing the caller's original dict after construction leaves `n.data` unchanged.
- `test_each_notification_gets_a_unique_id`
- `test_created_at_is_utc`: `created_at.tzinfo` is `UTC`.
- `test_category_labels_match_spec`: `"Game Events"` and `"Social Events"`.

`test_events.py`:
- `test_player_leveled_up_holds_fields`
- `test_player_leveled_up_is_immutable`
- `test_player_leveled_up_rejects_bad_player_id`, parametrized over `0`, `-1`, `True`, `"1"`, `1.0`. Each raises `ValueError` *(Review focus 1)*.
- `test_player_leveled_up_rejects_bad_level`, parametrized over `0`, `-5`, `True`, `"15"`. Each raises `ValueError`.
- `test_level_one_is_valid`

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 3: Level-up composer and registry

**Files:**
- Create:
  - `src/notifications/composers.py`
  - `tests/test_composers.py`

**Interfaces consumed:** `Notification`, `NotificationType.LEVEL_UP`, `Category.GAME`, `PlayerLeveledUp`.

**Interfaces produced:**
- `Composer = Callable[[Event], Notification | None]`
- `compose_level_up(event: PlayerLeveledUp) -> Notification`
- `default_composers() -> dict[type[Event], Composer]`. Task 10 adds the `players` and `items` parameters.

**Tests first:**
- `test_level_up_message_matches_spec`: `PlayerLeveledUp(1, 15)` gives exactly `Congratulations! You've reached level 15!`.
- `test_level_up_goes_to_the_player_who_leveled`: `recipient_id == 1`.
- `test_level_up_type_category_and_data`: `LEVEL_UP`, `GAME`, and `data == {"level": 15}`.
- `test_default_composers_handles_level_up`: the registry entry for `PlayerLeveledUp` produces the same notification.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 4: In-app channel

**Files:**
- Create:
  - `src/notifications/channels.py`
  - `tests/test_channels.py`

**Interfaces produced:**
- `NotificationChannel(Protocol)`: `send(notification: Notification) -> None`.
- `InAppChannel`, with attribute `delivered: list[Notification]` (empty at start). `send()` appends the notification, then prints `[in-app] to player {recipient_id}: {message}`.

**Tests first:**
- `test_send_records_the_notification`
- `test_send_prints_recipient_and_message`: using `capsys`, stdout is exactly `[in-app] to player 1: Congratulations! You've reached level 15!\n`.
- `test_delivered_preserves_order`

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 5: Dispatcher happy path, with default-on preferences

**Files:**
- Create:
  - `src/notifications/preferences.py`
  - `src/notifications/dispatcher.py`
  - `tests/conftest.py`
  - `tests/test_preferences.py`
  - `tests/test_dispatcher.py`

**Interfaces consumed:** `Composer`, `compose_level_up`, `Notification`, `NotificationChannel`, `PlayerLeveledUp`, `Event`.

**Interfaces produced:**
- `PreferenceStore(Protocol)`: `allows(notification: Notification) -> bool`.
- `InMemoryPreferenceStore()`, whose `allows()` returns `True`. The setter arrives in Task 8.
- `DispatchOutcome(Enum)`: `SENT`, `IGNORED`. Task 8 adds `SUPPRESSED` and Task 9 adds `FAILED`.
- `NotificationDispatcher(composers: Mapping[type[Event], Composer], preferences: PreferenceStore, channels: Sequence[NotificationChannel])`, with `handle(event: Event) -> DispatchOutcome`.
  - It raises `ValueError` if `channels` is empty.
  - It logs to the `notifications` logger, using the fixed strings above.
- In `conftest.py`: a `RecordingChannel` class with a `received: list[Notification]`, exposed through the fixture `recording_channel`.

**Tests first:**

`test_preferences.py`:
- `test_users_without_settings_receive_everything`: `allows()` is `True` for user 99 in both categories.

`test_dispatcher.py`:
- `test_registered_event_is_composed_and_sent`: returns `SENT`, and the channel received one notification with the T1 message.
- `test_every_channel_receives_the_notification`: two recording channels each receive it.
- `test_unregistered_event_is_ignored_with_warning`: uses an `Event` subclass defined in the test. Returns `IGNORED`, nothing is sent, and a WARNING `IGNORED <Class>: no composer registered` is logged (`caplog`).
- `test_composer_returning_none_is_ignored`: uses the composer `lambda e: None`. Returns `IGNORED`, nothing is sent, and INFO `... not notification-worthy` is logged.
- `test_sent_is_logged`: INFO `SENT LEVEL_UP to player 1 (Game Events)`.
- `test_dispatcher_requires_a_channel`: an empty channel list raises `ValueError`.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 6: In-process event bus

**Files:**
- Create:
  - `src/notifications/bus.py`
  - `tests/test_bus.py`

**Interfaces produced:**
- `EventPublisher(Protocol)`: `publish(event: Event) -> None`.
- `InProcessEventBus`, with:
  - `subscribe(handler: Callable[[Event], object]) -> None`
  - `publish(event: Event) -> None`, which calls every handler synchronously, in subscription order.

**Tests first:**
- `test_subscriber_receives_published_event`
- `test_subscribers_called_in_subscription_order`
- `test_every_event_reaches_every_subscriber`: 2 events × 2 handlers gives 4 calls in the expected order.
- `test_publish_without_subscribers_does_nothing`
- `test_handler_exception_propagates`: the bus doesn't swallow errors (DEC-7).

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 7: Game engine, wiring, and demo (slice complete)

**Files:**
- Create:
  - `src/notifications/producers.py`
  - `src/notifications/app.py`
  - `tests/test_acceptance.py`
- Modify:
  - `src/notifications/__main__.py`
  - `tests/test_demo.py`
  - `tests/conftest.py`: add the `app` fixture.

**Interfaces consumed:** everything from Tasks 2–6.

**Interfaces produced:**
- `GameEngine(publisher: EventPublisher)`, with `player_leveled_up(player_id: int, new_level: int) -> None`.
- `App`, a dataclass with `game_engine: GameEngine`, `preferences: InMemoryPreferenceStore`, and `in_app: InAppChannel`. Task 13 adds `social_system`.
- `build_app() -> App`. It creates the bus, the preference store, the `InAppChannel`, and a dispatcher built from `default_composers()` and `[in_app]`, then subscribes `dispatcher.handle` to the bus.
- `__main__.py`:
  - Configures `logging.basicConfig(level=INFO, format="  %(message)s", stream=sys.stdout)`.
  - Prints `> game_engine.player_leveled_up(1, 15)`.
  - Calls `player_leveled_up(1, 15)`.

**Tests first:**

`test_acceptance.py`:
- `test_T1_level_up_reaches_player_1`: `app.in_app.delivered` holds exactly one notification, for recipient 1, with the T1 message.
- `test_invalid_level_up_raises_and_sends_nothing`: `player_leveled_up(1, 0)` raises `ValueError`, and `delivered` stays empty.

`test_demo.py`:
- `test_demo_shows_T1`: stdout contains `[in-app] to player 1: Congratulations! You've reached level 15!` and `SENT LEVEL_UP to player 1 (Game Events)`.

**Done when:**
- From a copy without `.venv`, `./build.sh && ./run.sh` prints the T1 line, and `./test.sh` passes.
- **The thin slice is complete.**

---

## Outward

### Task 8: Per-category preferences and suppression

**Files:**
- Modify:
  - `src/notifications/preferences.py`
  - `src/notifications/dispatcher.py`
  - `tests/test_preferences.py`
  - `tests/test_dispatcher.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `InMemoryPreferenceStore.set_enabled(user_id: int, category: Category, enabled: bool) -> None`.
- `allows()` resolves in order: the stored value if there is one, otherwise `True`.
- `DispatchOutcome.SUPPRESSED`.

**Tests first:**

`test_preferences.py`:
- `test_disabled_category_is_not_allowed`
- `test_re_enabling_restores_delivery`
- `test_categories_are_independent`: disabling `GAME` leaves `SOCIAL` allowed *(Review focus 4)*.
- `test_users_are_independent`: disabling for user 1 leaves user 2 allowed.

`test_dispatcher.py`:
- `test_disabled_category_is_suppressed`: returns `SUPPRESSED`, nothing is sent, and INFO `SUPPRESSED LEVEL_UP to player 1: Game Events disabled` is logged.

`test_acceptance.py`:
- `test_level_up_suppressed_when_player_disables_game_events`: after `set_enabled(1, GAME, False)`, a level-up for 1 delivers nothing, while a level-up for 2 is still delivered.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 9: Delivery failures

**Files:**
- Modify:
  - `src/notifications/dispatcher.py`
  - `tests/conftest.py`: add a `FailingChannel` class that raises `RuntimeError("boom")` from `send()`, exposed through the fixture `failing_channel`.
  - `tests/test_dispatcher.py`

**Interfaces produced:** `DispatchOutcome.FAILED`. The dispatcher catches `Exception` from each `channel.send()` and only there.

**Tests first:**
- `test_failing_channel_is_logged_and_reported`: with only the failing channel, the outcome is `FAILED`. The ERROR logs name `FailingChannel` and the notification id, and `FAILED ... every channel failed` is logged.
- `test_other_channels_still_receive_when_one_fails`: with `[failing, recording]`, the outcome is `SENT` and the recording channel received the notification.
- `test_next_event_is_processed_after_a_failure`: a channel that fails only on its first call. The first `handle` returns `FAILED` and the second returns `SENT`.
- `test_composer_errors_are_not_swallowed`: an exception raised by a composer propagates out of `handle` (DEC-7).

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 10: Player directory and item catalog

**Files:**
- Create:
  - `src/notifications/lookups.py`
  - `tests/test_lookups.py`
- Modify:
  - `src/notifications/composers.py`: new signature for `default_composers`.
  - `src/notifications/app.py`: seed data, and pass the lookups in.
  - `tests/test_composers.py`: update the registry test's call.

**Interfaces produced:**
- `Rarity(IntEnum)`: `COMMON=1`, `UNCOMMON=2`, `RARE=3`, `EPIC=4`, `LEGENDARY=5`. The property `label -> str` returns `name.lower()`.
- `ItemInfo`, a frozen dataclass: `name: str`, `rarity: Rarity`.
- `PlayerDirectory(names: Mapping[int, str])`, with `display_name(player_id: int) -> str`. An unknown id returns `str(player_id)`.
- `ItemCatalog(items: Mapping[str, ItemInfo])`, with `lookup(item_id: str) -> ItemInfo | None`. Matching is exact.
- `default_composers(players: PlayerDirectory, items: ItemCatalog) -> dict[type[Event], Composer]`.
- In `app.py`: `DEMO_PLAYERS` and `DEMO_ITEMS`, as listed under the fixed strings above.

**Tests first:**
- `test_known_player_display_name`
- `test_unknown_player_falls_back_to_id`: `display_name(7) == "7"`.
- `test_known_item_lookup`
- `test_unknown_item_returns_none`
- `test_item_lookup_is_case_sensitive`: `"swordofazeroth"` gives `None` *(Review focus 5)*.
- `test_rarity_order_and_label`: `COMMON < RARE < LEGENDARY`, and `LEGENDARY.label == "legendary"`.

**Done when:** the new tests pass, the rest of the suite stays green, and `./run.sh` output is unchanged.

### Task 11: Item Acquired (FR-2, T2)

**Files:**
- Modify:
  - `src/notifications/events.py`
  - `src/notifications/notification.py`
  - `src/notifications/composers.py`
  - `src/notifications/producers.py`
  - `tests/test_events.py`
  - `tests/test_composers.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `ItemAcquired(Event)`: `player_id: int`, `item_id: str`, checked with `_check_id` and `_check_text`.
- `NotificationType.ITEM_ACQUIRED`.
- An item composer, registered in `default_composers` for `ItemAcquired`. It returns `None` for rarity below `RARE`, and for unknown ids it logs the warning and returns `None`. Its data is `{"item_id": ..., "rarity": <label>}`, with category `GAME`.
- `GameEngine.item_acquired(player_id: int, item_id: str) -> None`.

**Tests first:**

`test_events.py`:
- `test_item_acquired_holds_fields`
- `test_item_acquired_rejects_bad_player_id`
- `test_item_acquired_rejects_blank_item_id`, parametrized over `""`, `"   "`, and `None`. Each raises `ValueError` *(Review focus 3)*.

`test_composers.py`:
- `test_T2_item_message_matches_spec`: exactly `You've acquired the legendary Sword of Azeroth!`.
- `test_item_goes_to_the_acquiring_player`: recipient 2, `ITEM_ACQUIRED`, `GAME`.
- `test_rare_and_better_items_notify`, parametrized over RARE, EPIC, and LEGENDARY.
- `test_common_and_uncommon_items_do_not_notify`
- `test_unknown_item_does_not_notify_and_warns`: returns `None`, and the WARNING names the id.

`test_acceptance.py`:
- `test_T2_item_acquired_reaches_player_2`
- `test_common_item_sends_nothing`: `HealthPotion` delivers nothing.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 12: Challenge Completed (FR-3)

**Files:**
- Modify:
  - `src/notifications/events.py`
  - `src/notifications/notification.py`
  - `src/notifications/composers.py`
  - `src/notifications/producers.py`
  - `tests/test_events.py`
  - `tests/test_composers.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `ChallengeCompleted(Event)`: `player_id: int`, `challenge_name: str`.
- `NotificationType.CHALLENGE_COMPLETED`.
- A registered composer with data `{"challenge": name}` and category `GAME`.
- `GameEngine.challenge_completed(player_id: int, challenge_name: str) -> None`.

**Tests first:**

`test_events.py`:
- `test_challenge_completed_rejects_blank_name`, parametrized over `""` and `"  "` *(Review focus 3)*.
- `test_challenge_completed_rejects_bad_player_id`

`test_composers.py`:
- `test_challenge_message`: `"Dragon's Lair"` gives `Well done! You've completed 'Dragon's Lair'!`.
- `test_challenge_goes_to_the_player`: recipient, type `CHALLENGE_COMPLETED`, category `GAME`.

`test_acceptance.py`:
- `test_challenge_completed_reaches_player`

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 13: Social system and Friend Request (FR-5, T3)

**Files:**
- Modify:
  - `src/notifications/events.py`
  - `src/notifications/notification.py`
  - `src/notifications/composers.py`
  - `src/notifications/producers.py`
  - `src/notifications/app.py`
  - `tests/test_events.py`
  - `tests/test_composers.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `_check_distinct(actor_field: str, actor: int, target_field: str, target: int) -> None` in `events.py`. It raises `ValueError` when the two ids are equal.
- `FriendRequestSent(Event)`: `sender_id: int`, `recipient_id: int`.
- `NotificationType.FRIEND_REQUEST`.
- A registered composer: recipient is `recipient_id`, category `SOCIAL`, data `{"actor_id": sender_id}`.
- `SocialSystem(publisher: EventPublisher)`, with `friend_request_sent(sender_id: int, recipient_id: int) -> None`.
- `App.social_system: SocialSystem`, wired in `build_app()`.

**Tests first:**

`test_events.py`:
- `test_friend_request_to_self_is_rejected` *(Review focus 2)*
- `test_friend_request_rejects_bad_ids`

`test_composers.py`:
- `test_T3_friend_request_message`: with the demo players, `FriendRequestSent(3, 1)` gives `Player 'Cyra' has sent you a friend request.`
- `test_friend_request_goes_to_recipient`: recipient 1, `FRIEND_REQUEST`, `SOCIAL`.
- `test_unknown_sender_falls_back_to_id`: sender 7 gives `Player '7' has sent you a friend request.`

`test_acceptance.py`:
- `test_T3_friend_request_reaches_user_1_not_user_3`: exactly one delivered, to 1, and none to 3.
- `test_T3_uses_recipients_preferences_not_senders`:
  - With `set_enabled(3, SOCIAL, False)`, the notification is still delivered to 1.
  - With `set_enabled(1, SOCIAL, False)`, it's suppressed.

  *(Review focus 4)*
- `test_disabling_game_events_does_not_block_friend_requests`

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 14: Friend Accepted (FR-6, T4)

**Files:**
- Modify:
  - `src/notifications/events.py`
  - `src/notifications/notification.py`
  - `src/notifications/composers.py`
  - `src/notifications/producers.py`
  - `tests/test_events.py`
  - `tests/test_composers.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `FriendRequestAccepted(Event)`: `accepter_id: int`, `requester_id: int`. The accepter (the actor) comes first.
- `NotificationType.FRIEND_ACCEPTED`.
- A registered composer: recipient is `requester_id`, category `SOCIAL`, data `{"actor_id": accepter_id}`.
- `SocialSystem.friend_request_accepted(accepter_id: int, requester_id: int) -> None`.

**Tests first:**

`test_events.py`:
- `test_accepting_own_request_is_rejected` *(Review focus 2)*

`test_composers.py`:
- `test_T4_acceptance_message_and_recipient`: `FriendRequestAccepted(1, 3)` goes to recipient 3 with `Player 'Aria' accepted your friend request.`

`test_acceptance.py`:
- `test_T4_acceptance_reaches_requester_3_not_accepter_1`. A comment in the test explains the argument-order trap from REQUIREMENTS §2.1.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 15: New Follower (FR-7)

**Files:**
- Modify:
  - `src/notifications/events.py`
  - `src/notifications/notification.py`
  - `src/notifications/composers.py`
  - `src/notifications/producers.py`
  - `tests/test_events.py`
  - `tests/test_composers.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `PlayerFollowed(Event)`: `follower_id: int`, `followed_id: int`.
- `NotificationType.NEW_FOLLOWER`.
- A registered composer: recipient is `followed_id`, category `SOCIAL`, data `{"actor_id": follower_id}`.
- `SocialSystem.player_followed(follower_id: int, followed_id: int) -> None`.

**Tests first:**

`test_events.py`:
- `test_following_self_is_rejected` *(Review focus 2)*

`test_composers.py`:
- `test_follower_message_and_recipient`: `PlayerFollowed(4, 1)` goes to recipient 1 with `Player 'Dax' started following you.`

`test_acceptance.py`:
- `test_new_follower_reaches_followed_player_only`: 1 gets one notification, and 4 gets none.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 16: PvP attacked and defeated (FR-4)

**Files:**
- Modify:
  - `src/notifications/events.py`
  - `src/notifications/notification.py`
  - `src/notifications/composers.py`
  - `src/notifications/producers.py`
  - `tests/test_events.py`
  - `tests/test_composers.py`
  - `tests/test_acceptance.py`

**Interfaces produced:**
- `PlayerAttacked(Event)`: `attacker_id: int`, `victim_id: int`.
- `PlayerDefeated(Event)`: `winner_id: int`, `loser_id: int`.
- `NotificationType.PLAYER_ATTACKED` and `NotificationType.PLAYER_DEFEATED`.
- Two registered composers. The recipient is the victim or the loser, the category is `GAME`, and the data is `{"actor_id": attacker_id or winner_id}`.
- `GameEngine.player_attacked(attacker_id: int, victim_id: int) -> None`.
- `GameEngine.player_defeated(winner_id: int, loser_id: int) -> None`.

**Tests first:**

`test_events.py`:
- `test_attacking_self_is_rejected` *(Review focus 2)*
- `test_defeating_self_is_rejected`

`test_composers.py`:
- `test_attacked_message_and_recipient`: `PlayerAttacked(2, 1)` goes to recipient 1 with `Player 'Borin' is attacking you!`, category `GAME`.
- `test_defeated_message_and_recipient`: `PlayerDefeated(2, 1)` goes to recipient 1 with `You've been defeated by Player 'Borin'.`

`test_acceptance.py`:
- `test_pvp_notifies_only_the_attacked_or_defeated_player`: player 2 receives nothing.
- `test_pvp_respects_game_events_preference`: with `GAME` disabled for 1, both are suppressed.

**Done when:** the new tests pass and the rest of the suite stays green.

### Task 17: Full example-usage scenario (FR-15)

**Files:**
- Modify:
  - `src/notifications/__main__.py`
  - `tests/test_demo.py`

**Scenario, in this order:** before each step, print a `> {call}` line.

1. `game_engine.player_leveled_up(1, 15)`
2. `game_engine.item_acquired(2, "SwordOfAzeroth")`
3. `social_system.friend_request_sent(3, 1)`
4. `social_system.friend_request_accepted(1, 3)`
5. `game_engine.challenge_completed(1, "Dragon's Lair")`
6. `social_system.player_followed(4, 1)`
7. `game_engine.player_attacked(2, 1)`
8. `game_engine.player_defeated(2, 1)`
9. `game_engine.item_acquired(2, "HealthPotion")`: ignored, because it's a common item.
10. `preferences.set_enabled(1, Category.GAME, False)`
11. `game_engine.player_leveled_up(1, 16)`: suppressed.

**Tests first:** each test asserts that the demo's stdout contains the given lines.
- `test_demo_shows_spec_triggers`: these four lines, verbatim:
  - `[in-app] to player 1: Congratulations! You've reached level 15!`
  - `[in-app] to player 2: You've acquired the legendary Sword of Azeroth!`
  - `[in-app] to player 1: Player 'Cyra' has sent you a friend request.`
  - `[in-app] to player 3: Player 'Aria' accepted your friend request.`
- `test_demo_shows_other_event_types`: the challenge, follower, attacked, and defeated lines.
- `test_demo_shows_ignored_and_suppressed`: `IGNORED ItemAcquired: not notification-worthy` and `SUPPRESSED LEVEL_UP to player 1: Game Events disabled`.
- `test_demo_shows_each_trigger`: one `> ` line for each of the 11 steps.

**Done when:**
- The new tests pass and the rest of the suite stays green.
- `./run.sh` output covers every item in REQUIREMENTS §3.3, points 2–3, and reads cleanly top to bottom.

---

## Wrap-up

### Task 18: README and clean-clone check

`docs/AI_PROCESS.md` (D-4) is written and maintained by the user, not in this plan.

**Files:**
- Create: `README.md`

**Contents:**
- **`README.md`:**
  - What the project is.
  - Prerequisites: Python ≥ 3.11, macOS or Linux, and the `PYTHON=` override.
  - The build, run, and test commands, plus the raw equivalents for Windows.
  - Sample output.
  - A table mapping each spec name to its Python name (A-4).
  - The features.
  - Key assumptions, linking to REQUIREMENTS §4.
  - Links to ARCHITECTURE, PLAN, and AI_PROCESS.
  - The project layout.

**Checks:** there are no code tests in this task. Instead:
- Clone the repo into a temp directory, then run `./build.sh`, `./test.sh`, and `./run.sh` there. All three exit 0.
- Copy-paste every command in the README. Each one works as written.
- `git ls-files` lists no `.pdf`.

**Done when:**
- All three checks pass.
- The repo is pushed to a public GitHub repo you own (D-1). That push is your action, or mine if you ask for it.

---

## Spec coverage

| Requirement | Task(s) |
|---|---|
| FR-1 Level Up | 3, 7 |
| FR-2 Item Acquired | 10, 11 |
| FR-3 Challenge Completed | 12 |
| FR-4 PvP | 16 |
| FR-5 Friend Request | 13 |
| FR-6 Friend Accepted | 14 |
| FR-7 New Follower | 15 |
| FR-8 Receive events | 6, 7, 13 |
| FR-9 Type and recipient | 3, 5, 11–16 |
| FR-10 Notification object | 2 |
| FR-11 Content | 3, 11–16 |
| FR-12 / FR-13 Preferences | 5, 8 |
| FR-14 In-app send | 4, 5 |
| FR-15 Example usage | 7, 17 |
| TR-6 / TR-7 Build and run | 1, 18 |
| A-17 Delivery failures | 9 |
| A-18 Validation | 2, 11–16 |
| D-3 README | 18 |
| D-4 AI process | written by the user |
