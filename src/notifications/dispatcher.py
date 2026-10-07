"""The spec's pipeline in one place: compose, check preferences, send."""

import logging
from collections.abc import Mapping, Sequence
from enum import Enum, auto

from notifications.channels import NotificationChannel
from notifications.composers import Composer
from notifications.events import Event
from notifications.preferences import PreferenceStore

logger = logging.getLogger("notifications")


class DispatchOutcome(Enum):
    SENT = auto()
    FAILED = auto()
    SUPPRESSED = auto()
    IGNORED = auto()


class NotificationDispatcher:
    def __init__(
        self,
        composers: Mapping[type[Event], Composer],
        preferences: PreferenceStore,
        channels: Sequence[NotificationChannel],
    ) -> None:
        if not channels:
            raise ValueError("NotificationDispatcher needs at least one channel")
        self._composers = dict(composers)
        self._preferences = preferences
        self._channels = list(channels)

    def handle(self, event: Event) -> DispatchOutcome:
        event_name = type(event).__name__
        compose = self._composers.get(type(event))
        if compose is None:
            logger.warning("IGNORED %s: no composer registered", event_name)
            return DispatchOutcome.IGNORED

        notification = compose(event)
        if notification is None:
            logger.info("IGNORED %s: not notification-worthy", event_name)
            return DispatchOutcome.IGNORED

        if not self._preferences.allows(notification):
            logger.info(
                "SUPPRESSED %s to player %d: %s disabled",
                notification.type.name,
                notification.recipient_id,
                notification.category.value,
            )
            return DispatchOutcome.SUPPRESSED

        failures = 0
        for channel in self._channels:
            # Only delivery errors are caught here (A-17); composer errors
            # propagate to the bus, which logs them (DEC-7).
            try:
                channel.send(notification)
            except Exception:
                failures += 1
                logger.exception(
                    "Channel %s failed for notification %s",
                    type(channel).__name__,
                    notification.id,
                )
        if failures == len(self._channels):
            logger.error(
                "FAILED %s to player %d: every channel failed",
                notification.type.name,
                notification.recipient_id,
            )
            return DispatchOutcome.FAILED

        logger.info(
            "SENT %s to player %d (%s)",
            notification.type.name,
            notification.recipient_id,
            notification.category.value,
        )
        return DispatchOutcome.SENT
