"""Example usage (FR-15): simulated game events and how the system responds.

Run with: python -m notifications

Each step prints the trigger call with a comment saying who acts and who
should be notified, then what the system did: the in-app delivery and the
dispatcher's decision. Players: Aria (1), Borin (2), Cyra (3), Dax (4).
"""

import logging
import sys

from notifications.app import build_app
from notifications.notification import Category


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="  %(message)s", stream=sys.stdout)
    app = build_app()
    game, social, preferences = app.game_engine, app.social_system, app.preferences

    sections = [
        ("The spec's four example triggers", [
            ("game_engine.player_leveled_up(1, 15)",
             "Aria (1) reaches level 15 → notify 1",
             lambda: game.player_leveled_up(1, 15)),
            ('game_engine.item_acquired(2, "SwordOfAzeroth")',
             "Borin (2) gets a legendary item → notify 2",
             lambda: game.item_acquired(2, "SwordOfAzeroth")),
            ("social_system.friend_request_sent(3, 1)",
             "Cyra (3) sends Aria (1) a friend request → notify 1",
             lambda: social.friend_request_sent(3, 1)),
            ("social_system.friend_request_accepted(1, 3)",
             "Aria (1) accepts Cyra's (3) request → notify 3",
             lambda: social.friend_request_accepted(1, 3)),
        ]),
        ("Other event types", [
            ("game_engine.challenge_completed(1, \"Dragon's Lair\")",
             "Aria (1) completes a challenge → notify 1",
             lambda: game.challenge_completed(1, "Dragon's Lair")),
            ("social_system.player_followed(4, 1)",
             "Dax (4) follows Aria (1) → notify 1",
             lambda: social.player_followed(4, 1)),
            ("game_engine.player_attacked(2, 1)",
             "Borin (2) attacks Aria (1) → notify 1",
             lambda: game.player_attacked(2, 1)),
            ("game_engine.player_defeated(2, 1)",
             "Borin (2) defeats Aria (1) → notify 1",
             lambda: game.player_defeated(2, 1)),
        ]),
        ("Filtering: common items and preferences", [
            ('game_engine.item_acquired(2, "HealthPotion")',
             "Borin (2) gets a common item → notify nobody",
             lambda: game.item_acquired(2, "HealthPotion")),
            ("preferences.set_enabled(1, Category.GAME, False)",
             "Aria (1) turns Game Events off",
             lambda: preferences.set_enabled(1, Category.GAME, False)),
            ("game_engine.player_leveled_up(1, 16)",
             "Aria (1) reaches level 16 → suppressed",
             lambda: game.player_leveled_up(1, 16)),
        ]),
    ]

    width = max(len(call) for _, steps in sections for call, _, _ in steps)
    print("Notification system demo")
    for heading, steps in sections:
        print(f"\n=== {heading} ===")
        for call, comment, run in steps:
            print(f"\n> {call:<{width}}  # {comment}")
            run()


if __name__ == "__main__":
    main()
