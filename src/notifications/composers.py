"""Turn events into notifications: one composer per event type.

Each composer decides who is told, under which type and category, and what
the message says. It returns None when the event shouldn't notify anyone.
"""

import logging
from collections.abc import Callable

from notifications.events import ChallengeCompleted, Event, ItemAcquired, PlayerLeveledUp
from notifications.lookups import ItemCatalog, PlayerDirectory, Rarity
from notifications.notification import Category, Notification, NotificationType

logger = logging.getLogger("notifications")

Composer = Callable[[Event], Notification | None]


def compose_level_up(event: PlayerLeveledUp) -> Notification:
    return Notification(
        recipient_id=event.player_id,
        type=NotificationType.LEVEL_UP,
        category=Category.GAME,
        message=f"Congratulations! You've reached level {event.new_level}!",
        data={"level": event.new_level},
    )


def compose_challenge_completed(event: ChallengeCompleted) -> Notification:
    return Notification(
        recipient_id=event.player_id,
        type=NotificationType.CHALLENGE_COMPLETED,
        category=Category.GAME,
        message=f"Well done! You've completed '{event.challenge_name}'!",
        data={"challenge": event.challenge_name},
    )


def make_item_acquired_composer(items: ItemCatalog) -> Composer:
    def compose_item_acquired(event: ItemAcquired) -> Notification | None:
        info = items.lookup(event.item_id)
        if info is None:
            logger.warning("Unknown item id %r; not notifying", event.item_id)
            return None
        if info.rarity < Rarity.RARE:  # only rare or valuable items notify (A-5)
            return None
        return Notification(
            recipient_id=event.player_id,
            type=NotificationType.ITEM_ACQUIRED,
            category=Category.GAME,
            message=f"You've acquired the {info.rarity.label} {info.name}!",
            data={"item_id": event.item_id, "rarity": info.rarity.label},
        )

    return compose_item_acquired


def default_composers(players: PlayerDirectory, items: ItemCatalog) -> dict[type[Event], Composer]:
    return {
        PlayerLeveledUp: compose_level_up,
        ItemAcquired: make_item_acquired_composer(items),
        ChallengeCompleted: compose_challenge_completed,
    }
