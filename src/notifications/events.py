"""Events emitted by the game platform. Each one validates its own shape (A-18)."""

from dataclasses import dataclass


def _is_positive_int(value: object) -> bool:
    # bool is a subclass of int, so True would otherwise pass as 1.
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _check_id(field: str, value: object) -> None:
    if not _is_positive_int(value):
        raise ValueError(f"{field} must be a positive integer, got {value!r}")


def _check_text(field: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-blank string, got {value!r}")


def _check_level(field: str, value: object) -> None:
    if not _is_positive_int(value):
        raise ValueError(f"{field} must be an integer of 1 or more, got {value!r}")


@dataclass(frozen=True)
class Event:
    """Marker base class for everything a producer publishes."""


@dataclass(frozen=True)
class PlayerLeveledUp(Event):
    player_id: int
    new_level: int

    def __post_init__(self) -> None:
        _check_id("player_id", self.player_id)
        _check_level("new_level", self.new_level)


@dataclass(frozen=True)
class ItemAcquired(Event):
    player_id: int
    item_id: str

    def __post_init__(self) -> None:
        _check_id("player_id", self.player_id)
        _check_text("item_id", self.item_id)
