"""Channels hand a notification to the player's client."""

from typing import Protocol

from notifications.notification import Notification


class NotificationChannel(Protocol):
    def send(self, notification: Notification) -> None: ...


class InAppChannel:
    """Stands in for the platform's existing real-time in-app mechanism.

    Delivery and display are out of scope (TR-4), so this records each
    notification and prints it.
    """

    def __init__(self) -> None:
        self.delivered: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.delivered.append(notification)
        print(f"[in-app] to player {notification.recipient_id}: {notification.message}")
