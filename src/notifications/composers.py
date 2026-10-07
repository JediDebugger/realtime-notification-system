"""Turn events into notifications: one composer per event type.

Each composer decides who is told, under which type and category, and what
the message says. It returns None when the event shouldn't notify anyone.
"""

from collections.abc import Callable

from notifications.events import Event, PlayerLeveledUp
from notifications.notification import Category, Notification, NotificationType

Composer = Callable[[Event], Notification | None]


def compose_level_up(event: PlayerLeveledUp) -> Notification:
    return Notification(
        recipient_id=event.player_id,
        type=NotificationType.LEVEL_UP,
        category=Category.GAME,
        message=f"Congratulations! You've reached level {event.new_level}!",
        data={"level": event.new_level},
    )


def default_composers() -> dict[type[Event], Composer]:
    return {
        PlayerLeveledUp: compose_level_up,
    }
