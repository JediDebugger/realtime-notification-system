import subprocess
import sys

import pytest

SPEC = "The spec's four example triggers"
OTHER = "Other event types"
FILTERING = "Filtering: common items and preferences"

# (heading, trigger call, trailing comment) for every step, in order.
EXPECTED_STEPS = [
    (SPEC, "game_engine.player_leveled_up(1, 15)", "Aria (1) reaches level 15 → notify 1"),
    (SPEC, 'game_engine.item_acquired(2, "SwordOfAzeroth")', "Borin (2) gets a legendary item → notify 2"),
    (SPEC, "social_system.friend_request_sent(3, 1)", "Cyra (3) sends Aria (1) a friend request → notify 1"),
    (SPEC, "social_system.friend_request_accepted(1, 3)", "Aria (1) accepts Cyra's (3) request → notify 3"),
    (OTHER, "game_engine.challenge_completed(1, \"Dragon's Lair\")", "Aria (1) completes a challenge → notify 1"),
    (OTHER, "social_system.player_followed(4, 1)", "Dax (4) follows Aria (1) → notify 1"),
    (OTHER, "game_engine.player_attacked(2, 1)", "Borin (2) attacks Aria (1) → notify 1"),
    (OTHER, "game_engine.player_defeated(2, 1)", "Borin (2) defeats Aria (1) → notify 1"),
    (FILTERING, 'game_engine.item_acquired(2, "HealthPotion")', "Borin (2) gets a common item → notify nobody"),
    (FILTERING, "preferences.set_enabled(1, Category.GAME, False)", "Aria (1) turns Game Events off"),
    (FILTERING, "game_engine.player_leveled_up(1, 16)", "Aria (1) reaches level 16 → suppressed"),
]


def run_demo() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "notifications"],
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture(scope="module")
def demo_output() -> str:
    return run_demo().stdout


def parse_steps(out: str) -> list[dict]:
    """Split the demo output into steps: heading, call, comment, response lines."""
    steps, heading = [], None
    for line in out.splitlines():
        if line.startswith("=== "):
            heading = line.strip("= ")
        elif line.startswith("> "):
            call, _, comment = line[2:].partition(" # ")
            steps.append(
                {"heading": heading, "call": call.strip(), "comment": comment.strip(), "response": []}
            )
        elif line.strip() and steps:
            steps[-1]["response"].append(line.strip())
    return steps


def responses(out: str) -> dict[str, list[str]]:
    return {step["call"]: step["response"] for step in parse_steps(out)}


def test_demo_runs_and_exits_zero():
    result = run_demo()
    assert result.returncode == 0, result.stderr


def test_demo_shows_each_trigger(demo_output):
    steps = [(s["heading"], s["call"], s["comment"]) for s in parse_steps(demo_output)]
    assert steps == EXPECTED_STEPS


def test_demo_separates_steps_with_blank_lines(demo_output):
    lines = demo_output.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("> "):
            assert lines[i - 1] == "", f"no blank line before: {line}"


def test_demo_shows_spec_triggers(demo_output):
    r = responses(demo_output)
    assert r["game_engine.player_leveled_up(1, 15)"] == [
        "[in-app] to player 1: Congratulations! You've reached level 15!",
        "SENT LEVEL_UP to player 1 (Game Events)",
    ]
    assert r['game_engine.item_acquired(2, "SwordOfAzeroth")'] == [
        "[in-app] to player 2: You've acquired the legendary Sword of Azeroth!",
        "SENT ITEM_ACQUIRED to player 2 (Game Events)",
    ]
    assert r["social_system.friend_request_sent(3, 1)"] == [
        "[in-app] to player 1: Player 'Cyra' has sent you a friend request.",
        "SENT FRIEND_REQUEST to player 1 (Social Events)",
    ]
    assert r["social_system.friend_request_accepted(1, 3)"] == [
        "[in-app] to player 3: Player 'Aria' accepted your friend request.",
        "SENT FRIEND_ACCEPTED to player 3 (Social Events)",
    ]


def test_demo_shows_other_event_types(demo_output):
    r = responses(demo_output)
    assert r["game_engine.challenge_completed(1, \"Dragon's Lair\")"] == [
        "[in-app] to player 1: Well done! You've completed 'Dragon's Lair'!",
        "SENT CHALLENGE_COMPLETED to player 1 (Game Events)",
    ]
    assert r["social_system.player_followed(4, 1)"] == [
        "[in-app] to player 1: Player 'Dax' started following you.",
        "SENT NEW_FOLLOWER to player 1 (Social Events)",
    ]
    assert r["game_engine.player_attacked(2, 1)"] == [
        "[in-app] to player 1: Player 'Borin' is attacking you!",
        "SENT PLAYER_ATTACKED to player 1 (Game Events)",
    ]
    assert r["game_engine.player_defeated(2, 1)"] == [
        "[in-app] to player 1: You've been defeated by Player 'Borin'.",
        "SENT PLAYER_DEFEATED to player 1 (Game Events)",
    ]


def test_demo_shows_ignored_and_suppressed(demo_output):
    r = responses(demo_output)
    assert r['game_engine.item_acquired(2, "HealthPotion")'] == [
        "IGNORED ItemAcquired: not notification-worthy",
    ]
    assert r["preferences.set_enabled(1, Category.GAME, False)"] == []
    assert r["game_engine.player_leveled_up(1, 16)"] == [
        "SUPPRESSED LEVEL_UP to player 1: Game Events disabled",
    ]
