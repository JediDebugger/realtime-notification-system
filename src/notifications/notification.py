"""The notification delivered to a player, with its type and category (A-1)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from types import MappingProxyType
from uuid import uuid4


class Category(Enum):
    GAME = "Game Events"
    SOCIAL = "Social Events"


class NotificationType(Enum):
    LEVEL_UP = auto()
    ITEM_ACQUIRED = auto()
    CHALLENGE_COMPLETED = auto()
    FRIEND_REQUEST = auto()


@dataclass(frozen=True)
class Notification:
    recipient_id: int
    type: NotificationType
    category: Category
    message: str
    # Left out of the hash because a mapping isn't hashable. It still counts
    # for equality, so equal notifications still hash equally (DEC-15).
    data: Mapping[str, object] = field(hash=False)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        # frozen=True stops reassigning `data` but not mutating it, so keep a
        # read-only copy of the caller's mapping (DEC-15).
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))
