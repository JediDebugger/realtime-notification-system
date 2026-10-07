"""Per-user notification preferences, switched on or off per category (FR-12)."""

from typing import Protocol

from notifications.notification import Category, Notification
from notifications.validation import check_id


class PreferenceStore(Protocol):
    def allows(self, notification: Notification) -> bool: ...


class InMemoryPreferenceStore:
    """Every category is enabled until a user turns it off (A-13)."""

    def __init__(self) -> None:
        self._enabled: dict[tuple[int, Category], bool] = {}

    def set_enabled(self, user_id: int, category: Category, enabled: bool) -> None:
        check_id("user_id", user_id)
        if not isinstance(category, Category):
            # A label such as "Game Events" would be stored under a key nothing reads.
            raise TypeError(f"category must be a Category, got {category!r}")
        self._enabled[(user_id, category)] = enabled

    def allows(self, notification: Notification) -> bool:
        return self._enabled.get((notification.recipient_id, notification.category), True)
