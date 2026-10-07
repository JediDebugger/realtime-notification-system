"""Per-user notification preferences, switched on or off per category (FR-12)."""

from typing import Protocol

from notifications.notification import Notification


class PreferenceStore(Protocol):
    def allows(self, notification: Notification) -> bool: ...


class InMemoryPreferenceStore:
    """Every category is enabled until a user turns it off (A-13)."""

    def allows(self, notification: Notification) -> bool:
        return True
