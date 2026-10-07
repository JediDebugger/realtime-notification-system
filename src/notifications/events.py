"""Events emitted by the game platform. Each one validates its own shape (A-18)."""

from dataclasses import dataclass

from notifications.validation import check_id, check_level, check_text


@dataclass(frozen=True)
class Event:
    """Marker base class for everything a producer publishes."""


@dataclass(frozen=True)
class PlayerLeveledUp(Event):
    player_id: int
    new_level: int

    def __post_init__(self) -> None:
        check_id("player_id", self.player_id)
        check_level("new_level", self.new_level)


@dataclass(frozen=True)
class ItemAcquired(Event):
    player_id: int
    item_id: str

    def __post_init__(self) -> None:
        check_id("player_id", self.player_id)
        check_text("item_id", self.item_id)


@dataclass(frozen=True)
class ChallengeCompleted(Event):
    player_id: int
    challenge_name: str

    def __post_init__(self) -> None:
        check_id("player_id", self.player_id)
        check_text("challenge_name", self.challenge_name)


@dataclass(frozen=True)
class FriendRequestSent(Event):
    sender_id: int
    recipient_id: int

    def __post_init__(self) -> None:
        check_id("sender_id", self.sender_id)
        check_id("recipient_id", self.recipient_id)


@dataclass(frozen=True)
class FriendRequestAccepted(Event):
    accepter_id: int  # the actor comes first: the player who accepted
    requester_id: int

    def __post_init__(self) -> None:
        check_id("accepter_id", self.accepter_id)
        check_id("requester_id", self.requester_id)


@dataclass(frozen=True)
class PlayerFollowed(Event):
    follower_id: int
    followed_id: int

    def __post_init__(self) -> None:
        check_id("follower_id", self.follower_id)
        check_id("followed_id", self.followed_id)


@dataclass(frozen=True)
class PlayerAttacked(Event):
    attacker_id: int
    victim_id: int

    def __post_init__(self) -> None:
        check_id("attacker_id", self.attacker_id)
        check_id("victim_id", self.victim_id)


@dataclass(frozen=True)
class PlayerDefeated(Event):
    winner_id: int
    loser_id: int

    def __post_init__(self) -> None:
        check_id("winner_id", self.winner_id)
        check_id("loser_id", self.loser_id)
