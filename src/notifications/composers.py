"""Turn events into notifications: one composer per event type.

Each composer decides who is told, under which type and category, and what
the message says. It returns None when the event shouldn't notify anyone.
"""

import logging
from collections.abc import Callable

from notifications.events import (
    ChallengeCompleted,
    Event,
    FriendRequestAccepted,
    FriendRequestSent,
    ItemAcquired,
    PlayerFollowed,
    PlayerLeveledUp,
)
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


def make_friend_request_composer(players: PlayerDirectory) -> Composer:
    def compose_friend_request(event: FriendRequestSent) -> Notification:
        sender = players.display_name(event.sender_id)
        return Notification(
            recipient_id=event.recipient_id,
            type=NotificationType.FRIEND_REQUEST,
            category=Category.SOCIAL,
            message=f"Player '{sender}' has sent you a friend request.",
            data={"actor_id": event.sender_id},
        )

    return compose_friend_request


def make_friend_accepted_composer(players: PlayerDirectory) -> Composer:
    def compose_friend_accepted(event: FriendRequestAccepted) -> Notification:
        accepter = players.display_name(event.accepter_id)
        return Notification(
            recipient_id=event.requester_id,
            type=NotificationType.FRIEND_ACCEPTED,
            category=Category.SOCIAL,
            message=f"Player '{accepter}' accepted your friend request.",
            data={"actor_id": event.accepter_id},
        )

    return compose_friend_accepted


def make_new_follower_composer(players: PlayerDirectory) -> Composer:
    def compose_new_follower(event: PlayerFollowed) -> Notification:
        follower = players.display_name(event.follower_id)
        return Notification(
            recipient_id=event.followed_id,
            type=NotificationType.NEW_FOLLOWER,
            category=Category.SOCIAL,
            message=f"Player '{follower}' started following you.",
            data={"actor_id": event.follower_id},
        )

    return compose_new_follower


def default_composers(players: PlayerDirectory, items: ItemCatalog) -> dict[type[Event], Composer]:
    return {
        PlayerLeveledUp: compose_level_up,
        ItemAcquired: make_item_acquired_composer(items),
        ChallengeCompleted: compose_challenge_completed,
        FriendRequestSent: make_friend_request_composer(players),
        FriendRequestAccepted: make_friend_accepted_composer(players),
        PlayerFollowed: make_new_follower_composer(players),
    }
