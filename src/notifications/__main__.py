"""Example usage (FR-15): simulated game events and how the system responds.

Run with: python -m notifications
"""

import logging
import sys

from notifications.app import build_app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="  %(message)s", stream=sys.stdout)
    app = build_app()

    print("Notification system demo")
    print("> game_engine.player_leveled_up(1, 15)")
    app.game_engine.player_leveled_up(1, 15)


if __name__ == "__main__":
    main()
