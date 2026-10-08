# How AI was used

I built this with Claude Code, using separate sessions for separate jobs: one planned and reviewed, one implemented, and one reviewed the finished repo from scratch. I made every scope and design call and approved every phase. Below are the tools, the workflow, where I corrected the AI and why, and every prompt I sent.

## Tools

- **Claude Code** in VS Code, running Claude Opus 5.5, for all three sessions.
- **The superpowers plugin** in the implementation session: its `executing-plans` skill tracked tasks against [PLAN.md](PLAN.md), and its `test-driven-development` skill enforced writing a failing test first.
- **[CLAUDE.md](../CLAUDE.md)** holds the project rules, which every session loads: build only what the spec asks, no code before the architecture is approved, test-first, log every design decision, ask when the spec is ambiguous.
- **git** is the audit trail. The docs were committed before any code. After that there's one commit per task, and each commit message records the failing test result and then the passing one.

## Three sessions, three roles

| Session | Does | Never does |
|---|---|---|
| **Review chat** | Reads the spec, drafts each phase's prompt, then reads the actual files, diffs and commit messages after each phase and recommends what to approve or change. | Write code. |
| **Implementation chat** | Writes the docs and code each prompt asks for, test-first, and stops at agreed checkpoints with a report. | Decide scope, or approve its own work. |
| **Independent review** | Starts fresh with only the PDF and the repo, the way a grader would. | Change files. |

**Why split them:** a session reviewing its own work starts from its own framing. Keeping the reviewer separate meant every checkpoint was read cold against the code, not just against the implementer's summary of it. It also made each prompt a deliberate step I could review before sending.

**The loop at each step:**
1. The implementation chat stops and reports.
2. I paste the report into the review chat.
3. The review chat reads the repo itself, flags problems, and drafts the next prompt.
4. I decide what goes in and send it.

## Workflow

Every phase ended with a gate where I approved the output before the next one started.

1. **Requirements, no code** → [REQUIREMENTS.md](REQUIREMENTS.md). The AI listed 21 ambiguities, each with a proposed assumption, and 10 open questions. I answered each one; the answers are in §6.
2. **Architecture, no code** → [ARCHITECTURE.md](ARCHITECTURE.md). It compared three approaches with their tradeoffs, recommended an in-process event bus, walked through four extension scenarios, and listed what it considered overengineering.
3. **Plan** → [PLAN.md](PLAN.md). 18 test-first tasks, ordered so a thin end-to-end slice (level-up → in-app) worked by Task 7. I amended it before approving.
4. **Implementation in four batches**, with a checkpoint review after each: Tasks 1–7, 8–12, 13–17, then 18. Each checkpoint report included test and demo output, the git log, any deviations from the plan, and open questions. At every checkpoint, the review chat read the diff before I approved.
5. **Independent review** in a fresh session, then fixes.
6. **Push.**

## Where I corrected or overrode the AI

| When | What the AI produced | What I changed | Why | Found by |
|---|---|---|---|---|
| Plan review | `Notification` was a frozen dataclass holding a plain `dict` in `data`. | Store a read-only copy ([DEC-15](ARCHITECTURE.md#7-decisions)). | `frozen` stops reassigning the field, not changing what's inside it. One channel could have changed what the next one sees. | Review chat |
| Plan review | Run every task in one go and review only at the end. The AI-process record would be written by the implementer at the end. | Checkpoints after Tasks 7, 12 and 17. Docs committed before code. I keep the AI-process record myself. | Design mistakes get caught at checkpoints, not at the end. The implementer only knows its own side of the process. | Me, with the review chat |
| Checkpoint 1 | The bus let subscriber exceptions propagate (original DEC-7). | The bus catches, logs, and isolates subscriber failures ([DEC-7](ARCHITECTURE.md#7-decisions), revised). | A bug in the notification code would have broken `game_engine.player_leveled_up()`. Keeping producers independent of notifications was the whole reason for choosing the bus. | Review chat |
| Checkpoint 1 | In Tasks 3–6, the first failing run happened only because the new module didn't exist yet. | New rule: add stubs and see the behaviour tests fail before implementing. | A test that fails on an import error doesn't show the test checks anything. | AI flagged it; I set the rule |
| Checkpoint 1 | DEC-15 made `hash(notification)` raise `TypeError`. | `data` uses `field(hash=False)`. | An immutable value object should be hashable. Equality is unchanged. | AI flagged it; I chose the fix |
| Checkpoint 3 | The demo printed `→`. | Plain ASCII, with a test that checks for it. | On Windows, redirecting the output to a file uses cp1252, which can't encode `→`, so the demo would crash. | AI flagged it as optional; I made it required |
| Checkpoint 3 | `build.sh` used `python3` only. | It now finds the first installed Python that's 3.11 or newer ([DEC-16](ARCHITECTURE.md#7-decisions)). | On a stock Mac, `python3` is 3.9, and graders run the build script exactly as provided. The AI's own checks passed only because its machine's default `python3` was 3.11 (installed through pyenv), not the stock 3.9. | Review chat |
| Checkpoint 3 | The demo's output was one flat list of steps. | Grouped under headings, with a comment on each trigger line in the spec's style saying who acts and who is notified. The README opens with what a grader needs first. | A grader runs the demo and reads the README first, so both should be easy to check against the spec. | Me, with the review chat |

**What the AI got right without correction.** Before the requirements phase, I wrote a checklist of traps in the spec and deliberately left it out of the prompt, to see whether the AI would find them on its own. It found all of them:
- `friendRequestAccepted(1, 3)` notifies user 3, not user 1.
- `itemAcquired` has no rarity, but the example message says "legendary".
- The "provided" `Notification` class isn't in the PDF.
- "Player 'X'" messages need names, but events carry only ids.
- Three events have no example call.
- The spec doesn't say what preferences a new player starts with.
- What "real-time" should mean when the game client is mocked.

**Points I questioned and kept as proposed:**
- Stub composers that return `None` and fail with `AttributeError`: kept. That's the behaviour failing, not a missing name.
- The bus log names `NotificationDispatcher.handle` rather than the composer that failed: kept. Each event class maps to exactly one composer, and the traceback names it.

## Independent review

Before pushing, a fresh session reviewed the repo using only the PDF and the code (prompt 8 below). It cloned the repo and followed the README the way a grader would, mapped each requirement to its implementation and tests, checked that the docs match the code, and listed the hardest interview questions.

**Verdict:** the code meets every requirement. Recipients and preference checks were correct for all eight event types, and a clean clone built, ran and passed. The two blocking items were deliverables: this file wasn't committed yet, and nothing was pushed. It also raised seven should-fix findings and ten nitpicks. I went through them in the review chat, and the implementation chat fixed them in 11 commits, each naming the finding it addresses (prompt 9).

| ID | Finding | Decision | Why |
|---|---|---|---|
| S1 | `build.sh` tries only 3.13, 3.12 and 3.11, so it misses 3.14 and newer. | **Fix.** Use `python3` if it's new enough, otherwise the newest `python3.N` on `PATH`. | A fixed list goes stale. The default `python3` is the interpreter most likely to have `venv` and `pip` working. |
| S2 | A half-created `.venv` makes every later build fail. | **Fix.** Detect a broken venv and recreate it. If `venv` itself fails, remove the partial `.venv` and print a hint. | A grader's second attempt has to work. |
| S3 | Self-targeted events (`player_attacked(2, 2)`) raise `ValueError` out of the game's own call. | **Fix in code.** Composers ignore them, and shape checks stay. | It contradicted both the bus boundary and A-18. "You can't target yourself" is a game rule, not a shape check. |
| S4 | ARCHITECTURE §5 claimed a dispatcher test proves suppression uses the recipient's preferences, but that test's actor *is* the recipient. | **Fix** by adding a test where they differ. | Make the claim true rather than weaken it. |
| S5 | No test of whose preferences T4 checks. | **Fix:** add one. | T4 is the easiest trigger to get wrong. The code was already correct, so both new tests passed at once. To prove they could catch the bug, the implementation chat temporarily made the store check the actor's preferences, saw both tests fail, and reverted. |
| S6 | The broker design partitioned by recipient id, which producers don't have. Ids are a fresh `uuid4`, so redelivered events can't be deduplicated. | **Fix the docs:** an events topic, then a delivery topic partitioned by recipient, with notification ids derived from the event's id. | The original §3d wouldn't have worked as written. |
| S7 | DEC-16 rejects Python 3.9 without saying why. | **Keep 3.11, and record the reason.** Add install hints to the error. | 3.9 is end of life, and supporting it means working around its old pip. |
| Nits | build-script noise, `set_enabled` accepting any category, stale doc rows, the README understating what a new event type needs, and a few others. | **Fix all but one.** A partial channel failure is still logged as `SENT`. Shared shape checks moved to `validation.py` ([DEC-19](ARCHITECTURE.md#7-decisions)), and the ASCII-only demo got its own entry ([DEC-18](ARCHITECTURE.md#7-decisions)). | The partial failure is already documented in ARCHITECTURE §2.5. |
| Interview | Fan-out ("notify all followers"), and why the notification system owns item rarity. | **Document:** a new [§3(e)](ARCHITECTURE.md#3-extension-walkthrough) walkthrough and [DEC-17](ARCHITECTURE.md#7-decisions). | Both are design questions, and now the answers are written down. |

The reviewer called the read-only `data` and its hash fix (DEC-15) borderline scope. I kept them: a notification goes to several channels, so it should be immutable.

## What worked, and what I'd keep

- **Ask for ambiguities before design.** Having the AI list every gap with a proposed assumption, then confirming each one, settled all the spec's traps before any code was written.
- **Keep a checklist the AI doesn't see.** It tests whether the AI finds the problems unaided, rather than just agreeing with whatever the prompt points it at.
- **A decision log with the alternatives considered.** CLAUDE.md requires it. Every review had something to check against, and the log doubles as interview preparation.
- **Read the diff, not the summary.** The checkpoint reports were accurate, but the two most important fixes (DEC-7 and the build script) weren't in them. Both came from reading the code.
- **Look from the grader's environment.** The AI verifies in its own environment, where everything passed. The Python-version and encoding problems only showed up when the review chat asked what a grader's machine would do.
- **Thin slice first, small commits, proof of the failing test in every commit.** Each step was small enough to review, and the history shows the tests came first.
- **A truly fresh reviewer at the end.** The review chat had read every checkpoint, yet it missed S3 (self-targeted events contradicting the error-boundary story) and S6 (a broker design that couldn't work). A session that started from only the PDF and the repo found both. Reviewing many small diffs one at a time doesn't replace one cold read of the whole thing.

## Prompt log

These are the prompts I sent, verbatim. Every prompt from 2 onward was drafted in the review chat after it had read the previous phase's output in the repo.

<details>
<summary><b>0. To the review chat: kickoff</b></summary>

I attached the PDF and asked, in short: build the real-time notification system it describes, but first give me prompts for a second chat that will do the work, since the interview assesses prompting. How should I proceed?

**Result:** the phased approach above, the CLAUDE.md rules, and a draft prompt for each phase.
</details>

<details>
<summary><b>1. Requirements</b></summary>

```
Read `Coding Challenge.pdf` in this folder. It's a take-home challenge: a real-time notification system for a gaming platform, to be built in Python.

Don't write code yet. Write docs/REQUIREMENTS.md with:
1. Functional requirements with IDs (FR-1, FR-2…), marked required or optional as the spec states.
2. Technical requirements and deliverables (build scripts, README, what "it runs" means).
3. Ambiguities and gaps: anything underspecified, contradictory, or referenced but missing. For each one, give a proposed assumption and your reasoning.
4. What's explicitly out of scope.

For each example trigger, be precise about who receives the notification. When you're done, list the open questions for me to confirm and stop.
```

**Result:** 21 assumptions and 10 questions. I answered each one; see [REQUIREMENTS.md §6](REQUIREMENTS.md#6-resolved-questions-2026-10-06).
</details>

<details>
<summary><b>2. Architecture</b></summary>

```
Requirements approved. My answers to the open questions: [Q1–Q10, as recorded in REQUIREMENTS.md §6].

Still no code. Write docs/ARCHITECTURE.md:
1. 2–3 overall approaches (e.g. direct service calls vs. an in-process event bus vs. …) with their tradeoffs at this scope. Recommend one.
2. For your recommendation: the components and interfaces, what each is responsible for, and how `gameEngine.playerLeveledUp(1, 15)` flows to a delivered notification. Add a Mermaid diagram.
3. Extension walkthrough: what code changes to (a) add a new event type, (b) add a push or email channel, (c) add per-event-type preferences, (d) move to a distributed setup with a message broker. Call out any of these that forces edits to existing classes.
4. Folder structure and test strategy.

Keep it proportionate: this is a take-home, not a production platform. Flag anything you consider overengineering.
```

**Result:** three approaches compared, and the in-process synchronous event bus chosen (DEC-1). Approved.
</details>

<details>
<summary><b>3. Plan</b></summary>

```
Architecture approved. Write docs/PLAN.md: small tasks that can each be tested on their own. Order them so a thin end-to-end slice works first (level-up -> in-app notification), then build outward. For each task, list the files touched, the tests to write first, and when it counts as done. Don't implement anything yet.
```

**Result:** 18 tasks. The AI asked whether to run them in one session or with a separate agent per task, and whether to commit after every task.
</details>

<details>
<summary><b>4. Plan approved; start Tasks 1–7</b></summary>

```
Plan approved. Answers to your questions:

1. Coverage: yes.
2. Execution: native, in this session, with checkpoints for my review. Stop after Task 7 (thin slice), after Task 12, and after Task 17. Start Task 18 only when I say go.
3. Commits: yes, one per task. Before Task 1:
   - Run git init and create .gitignore first (the contents from Task 1, including *.pdf). Confirm `git status` doesn't list the PDF.
   - Commit CLAUDE.md and docs/ as a single commit, so the history shows the design came before the code.

One plan amendment, in Task 2: Notification.data is a dict inside a frozen dataclass, so it can still be changed. Store a read-only copy (e.g. MappingProxyType over a copy of the input), add a test that mutating data fails and that changing the caller's original dict doesn't affect the notification, and log it as a DEC entry.

Rules while implementing:
- Follow PLAN.md's "How to run each task" exactly. Run each task's new tests and see them fail for the expected reason before writing the implementation.
- Put one line of red/green evidence in each commit message body, e.g. "Red: 5 new tests failed (ModuleNotFoundError: notifications.notification) → Green: 23 passed".
- Tick the task's checkbox in PLAN.md in the same commit.
- If you need to deviate from PLAN.md or ARCHITECTURE.md (a signature, a string, a file), add a DEC entry in ARCHITECTURE.md §7 and mention it at the next checkpoint. Don't diverge silently.
- If something is ambiguous, or a planned test turns out to be wrong, stop and ask.
- Don't create or edit docs/AI_PROCESS.md. I'm keeping that myself, so drop that part of Task 18.

At each checkpoint, stop and report:
- the output of ./test.sh and ./run.sh
- git log --oneline for the batch
- any deviations and the DEC entries you added
- anything you're unsure about or would change

Start with the setup, then Tasks 1–7.
```
</details>

<details>
<summary><b>5. Checkpoint 1 → Tasks 8–12</b></summary>

```
Checkpoint 1 approved. Answers to your points, plus one design change.

1. Git identity: keep JediDebugger. It's my GitHub account.
2. Add .claude/ to .gitignore. It only holds machine-specific permission settings.
3. Weak red phase: from now on, if new tests fail only because a name doesn't exist yet, add a minimal stub (the class or function with no real behaviour). Confirm the behaviour tests then fail on their assertions before you implement, as you did in Tasks 2 and 7. Record both failures in the red line.
4. hash(notification): fix it. Exclude data from the generated hash with field(hash=False). Equality still compares data, so equal notifications still hash equally. Add a test that a notification can go in a set, and update DEC-15.

Design change to DEC-7: the bus should isolate subscriber failures from producers. Right now an exception in a composer or the dispatcher propagates through publish() into game_engine.player_leveled_up(), so a notification bug breaks the game's own call. That undercuts why we chose the bus: producers shouldn't depend on the notification system. Change it so that:
- InProcessEventBus.publish() catches Exception per handler, logs it at ERROR with the traceback (naming the handler and the event class), and carries on with the remaining handlers.
- Validation errors still raise at the producer, because they happen when the event is built, before publish().
- The dispatcher still doesn't swallow composer errors, so Task 9's test stays. The bus is the boundary.

Make this its own test-first commit before Task 8:
- Replace test_handler_exception_propagates with tests showing that the failure is logged, doesn't reach the publisher, and later subscribers still run.
- Add a test that wires GameEngine → bus → dispatcher with a composer that raises, and shows that player_leveled_up() returns normally and the error is logged.
- Update DEC-7 and ARCHITECTURE.md §2.5 to match, with the reasoning above.

Then continue with Tasks 8–12. Stop at checkpoint 2 with the same report as before.
```
</details>

<details>
<summary><b>6. Checkpoint 2 → Tasks 13–17</b></summary>

```
Checkpoint 2 approved. Answers:

1. Composer stubs: keep returning None. An AttributeError on None means the behaviour is missing, not a name, so it counts as a real failing test. Don't add placeholder notifications.
2. Composer bugs naming the subscriber: leave it. The log names the event class, each event class maps to exactly one composer, and the traceback names the composer function.

Go ahead with Tasks 13–17, same rules as before.

One addition to Task 17. The demo is the first thing the graders see, so make it easy to check against the spec:
- Group the steps under three short headings: the spec's four example triggers, the other event types, and filtering (the common item and the preference suppression).
- Give each trigger line a short trailing comment in the spec's style, saying who acts and who should be notified. For example:
  > social_system.friend_request_accepted(1, 3)   # Aria (1) accepts Cyra's (3) request → notify 3
- Put a blank line between steps.
- Update test_demo.py to match.

Stop at checkpoint 3 after Task 17 with the same report, and include the full ./run.sh output verbatim so I can review the demo.
```
</details>

<details>
<summary><b>7. Checkpoint 3 → build fix and Task 18</b></summary>

```
Checkpoint 3 approved , and the answers:

1. Arrows: switch → to -> in the demo output and its tests. The README will list Windows commands, and on Windows, redirecting the output to a file uses cp1252, where → makes the demo crash with UnicodeEncodeError.
2. Indentation: keep it as is. It separates what the player sees ([in-app], flush left) from what the system logged (indented). Explain that in the README instead.

One fix before Task 18, as its own test-first commit: on a stock Mac, python3 is 3.9, so ./build.sh fails unless the grader knows to set PYTHON. When PYTHON isn't set, try python3.13, python3.12, python3.11, then python3, and use the first one that's 3.11 or newer. Keep the PYTHON override, and keep the clear error message for when none qualifies.

Then do Task 18. On top of the plan's README list:
- Write the first screen for a grader who has just cloned the repo: what this is in two sentences, the prerequisites (Python ≥ 3.11, macOS or Linux, internet access for pip on the first build), and the three commands.
- Add "Reading the demo output": [in-app] lines are what the player receives, and the indented lines are the dispatcher's log of what it decided and why.
- Add a short "Design" section: the pipeline in a few lines or a small diagram, plus the decisions a reviewer is most likely to ask about, each linked to its DEC entry: the event bus, composers, the two error boundaries, checking the recipient's preferences, and why it's in-process only. Link ARCHITECTURE.md §3 for how to extend it.
- Under "Assumptions", list only the ones that change behaviour: the item rarity filter, who a friend acceptance notifies, preferences on by default, and self-targeted events being rejected. Link REQUIREMENTS §4 for the rest.
- Add "How AI was used": two or three lines linking docs/AI_PROCESS.md. I'm adding that file myself before we push, so a dangling link is fine for now.
- Keep it short and skimmable. The detail lives in docs/.
- Only document commands you actually ran. If you can't run the Windows equivalents here, label them as untested.

Run the plan's clean-clone check, then stop. Don't create the GitHub repo or push. Report the full README text, the clean-clone output, and git log for this batch.
```
</details>

<details>
<summary><b>8. Independent review (fresh session)</b></summary>

The implementation chat offered to start a reviewer agent itself. I used a new session instead, so the review wouldn't start from the implementer's framing.

```
You're reviewing a take-home submission before it's handed in. Review it the way the grader will. Don't change any files or make commits. Report findings only.

1. Read `Coding Challenge.pdf` first. Before opening anything else, write down what you'd expect a complete solution to do.
2. Clone this repo into a temp directory and follow README.md exactly, as a grader would: build, run, test. Report anything that fails or is unclear.
3. Map every requirement in the PDF to where it's implemented and where it's tested. List anything missing, partial or wrong.
4. Look for bugs, especially in who receives each notification, whose preferences are checked, error handling, and build.sh.
5. Check that the docs match the code: README.md, docs/REQUIREMENTS.md, docs/ARCHITECTURE.md (especially the DEC entries in §7) and docs/PLAN.md. Flag anything stale, or claimed but not true. Skip docs/AI_PROCESS.md: it's uncommitted and still being written.
6. Point out scope creep: anything built that the spec didn't ask for, and whether it's justified.
7. List the 5 questions about this design you'd find hardest to answer in an interview.

Group findings by severity (must fix before submitting / should fix / nitpick). Give file:line for each, and say how confident you are.
```
</details>

<details>
<summary><b>9. Review fixes</b></summary>

```
A fresh session reviewed the whole repo against the PDF. Its verdict: the code meets every requirement, and the recipients and preference checks are correct everywhere. Below are the findings I'm accepting and what to do about each. Same rules as before: test-first for code changes, a DEC entry for any design change, small commits. Put the finding IDs in each commit subject, e.g. "fix(S2): ...".

Leave docs/AI_PROCESS.md alone and uncommitted. It gets committed in the final push step.

## build.sh
- S1: discovery uses a fixed list (3.13, 3.12, 3.11). A machine whose python3 is 3.10 and that has only python3.14 installed fails. Don't depend on a fixed list:
  - Use python3 if it's 3.11 or newer. It's the machine's default, so it's the most likely to have venv and pip working.
  - Otherwise, use the newest python3.N on PATH that's 3.11 or newer (e.g. via compgen -c python3.).
  - Update DEC-16, the README and the tests.
- S2: if .venv exists but is broken (e.g. a venv that failed halfway on Ubuntu without python3-venv), every later build fails with "No module named pip".
  - Detect a .venv whose python can't run pip, remove it and recreate it.
  - If `-m venv` itself fails, remove the partial .venv and print a hint (on Debian/Ubuntu: install the python3.X-venv package).
- S7: keep 3.11 as the minimum, but give the reason in DEC-16: Python 3.9 has been end of life since October 2025. You can also cite that the pip bundled with the stock macOS 3.9 can't do the editable install, but only if you've verified it. Add install hints to the "none found" error (macOS: Homebrew or the python.org installer; Debian/Ubuntu: apt).
- Nitpick: an interpreter that can't report its version prints "[: unknown: integer expression expected". Make is_supported handle a non-numeric version quietly.

## Self-targeted events (S3)
Rejecting a self-targeted event with ValueError contradicts our own docs. The bus is there so notification problems can't break the game's call, and A-18 says we trust the producer's business rules. "You can't target yourself" is a business rule, not a shape check. So:
- Remove _check_distinct from the events. Shape checks (positive int ids, non-blank strings) stay and still raise, because a malformed event is the caller's bug.
- The five social and PvP composers return None when the actor is the recipient. The dispatcher logs IGNORED, nothing is sent, and the producer's call returns normally.
- Move the self-targeting tests from test_events.py to the composer and acceptance tests.
- Update A-18, DEC-8 and the README's assumptions.
- Make the README's error-boundary line precise: a bug in the notification pipeline can't break the game's call, while a malformed event is rejected when the producer builds it.

## Tests
- S4: ARCHITECTURE §5 says test_dispatcher.py proves suppression uses the recipient's preferences, not the actor's. But it only uses a level-up, where actor and recipient are the same player. Add a dispatcher test with an event whose actor and recipient differ, so the claim is true.
- S5: add a T4 acceptance test for whose preferences count:
  - With the requester's (3) Social Events off, friend_request_accepted(1, 3) is suppressed.
  - With only the accepter's (1) off, it's still delivered to 3.
- Nitpick: set_enabled(1, "Game Events", False) silently does nothing. Raise TypeError unless category is a Category, and validate user_id the same way the events do.

## Docs (no code)
- S6: ARCHITECTURE §3d partitions the broker by recipient id, but producers don't know the recipient, because composers decide it (DEC-3). Redo it as two stages:
  - Events are partitioned by a key the producer has: the acting player.
  - The notification service composes and publishes notifications to a delivery topic partitioned by recipient_id. That's where per-player ordering comes from.
  - Also cover dedupe. Notification.id is a fresh uuid4 each time, so a redelivered event gets a new id. Once events carry an event_id, derive the notification id from it instead (e.g. uuid5).
- New §3(f), fan-out: "also notify the winner", or "tell all followers when someone reaches level 50". Say what changes: the composer contract (from one notification or none to a list), the dispatcher loop, the per-recipient preference checks, and where the follower list comes from. Design only, don't build it.
- New DEC: rarity lives in the notification system (the item catalog).
  - Alternatives: the game puts rarity in the event, or emits a separate RareItemAcquired event.
  - Why: the spec's trigger itemAcquired(2, "SwordOfAzeroth") carries no rarity, and we kept its signature.
  - Tradeoff: every pickup goes through the pipeline and a catalog lookup. That's cheap in memory; at scale, filter at the producer or put rarity in the event.
- New DEC: the demo output is ASCII-only, and why (Windows redirects).
- Nitpicks:
  - README "adding an event type" should list everything §3a lists: the event class, the enum member, the composer plus its registry line, and the producer method.
  - The README's internet note should say pip also downloads setuptools for the build.
  - Fix the ARCHITECTURE §4 .gitignore comment and the §5 test_bus.py row.
  - Fix the DEC-14 wording: the seed data are module constants, not build_app() defaults.
  - Remove the unused DragonScaleShield seed item and its mention in PLAN.md.
- Keep as is: a partial channel failure is logged as SENT. §2.5 already documents that.

When you're done, run the clean-clone check again (build, test, run, and every README command), then stop. Report:
- a table mapping each finding ID to its commit
- the clean-clone output
- anything you disagreed with or did differently
Don't push yet.
```
</details>

<details>
<summary><b>10. Final: Linux check, commit this file, push</b></summary>

```
Review fixes approved. On the points you raised: leave the build-script tests unmarked, and keep the generic IGNORED reason for self-targeted events.

Final step:
1. Linux check. If Docker is available, run a fresh clone inside a python:3.11-slim container (mount it in): ./build.sh, ./test.sh, ./run.sh.
   - If they pass, keep "macOS or Linux" in the README.
   - If Docker isn't available, change the README to say it's tested on macOS and expected to work on Linux.
   - Commit any change.
2. Commit docs/AI_PROCESS.md exactly as it is now, without editing it. Tick Task 18 in PLAN.md in the same commit.
3. Create a public GitHub repo under JediDebugger named realtime-notification-system, with a one-line description, and push main.
4. Verify from GitHub: clone the pushed repo into a temp directory, run ./build.sh, ./test.sh and ./run.sh, and confirm the clone contains no PDF and no .claude/.
5. Report the repo URL, the verification output, and git log --oneline | head -5.
```
</details>
