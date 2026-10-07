"""Carries events from producers to subscribers."""

import logging
from collections.abc import Callable
from typing import Protocol

from notifications.events import Event

logger = logging.getLogger("notifications")


class EventPublisher(Protocol):
    def publish(self, event: Event) -> None: ...


class InProcessEventBus:
    """Calls every subscriber synchronously, in subscription order.

    The bus is the boundary between producers and the notification system
    (DEC-7): a subscriber that raises is logged with its traceback and the
    remaining subscribers still run, so a notification bug never breaks the
    producer's call.
    """

    def __init__(self) -> None:
        self._handlers: list[Callable[[Event], object]] = []

    def subscribe(self, handler: Callable[[Event], object]) -> None:
        self._handlers.append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Subscriber %s failed on %s",
                    getattr(handler, "__qualname__", repr(handler)),
                    type(event).__name__,
                )
