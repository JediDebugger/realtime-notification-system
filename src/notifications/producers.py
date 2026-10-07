"""Simulated parts of the game platform that emit events.

Method names are the snake_case forms of the spec's calls, with the same
argument order: the actor comes first (A-4).
"""

from notifications.bus import EventPublisher
from notifications.events import (
    ChallengeCompleted,
    FriendRequestAccepted,
    FriendRequestSent,
    ItemAcquired,
    PlayerLeveledUp,
)


class GameEngine:
    def __init__(self, publisher: EventPublisher) -> None:
        self._publisher = publisher

    def player_leveled_up(self, player_id: int, new_level: int) -> None:
        self._publisher.publish(PlayerLeveledUp(player_id, new_level))

    def item_acquired(self, player_id: int, item_id: str) -> None:
        self._publisher.publish(ItemAcquired(player_id, item_id))

    def challenge_completed(self, player_id: int, challenge_name: str) -> None:
        self._publisher.publish(ChallengeCompleted(player_id, challenge_name))


class SocialSystem:
    def __init__(self, publisher: EventPublisher) -> None:
        self._publisher = publisher

    def friend_request_sent(self, sender_id: int, recipient_id: int) -> None:
        self._publisher.publish(FriendRequestSent(sender_id, recipient_id))

    def friend_request_accepted(self, accepter_id: int, requester_id: int) -> None:
        self._publisher.publish(FriendRequestAccepted(accepter_id, requester_id))
