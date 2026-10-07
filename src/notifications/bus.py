"""Carries events from producers to subscribers."""

from collections.abc import Callable
from typing import Protocol

from notifications.events import Event


class EventPublisher(Protocol):
    def publish(self, event: Event) -> None: ...


class InProcessEventBus:
    """Calls every subscriber synchronously, in subscription order.

    Exceptions are not caught here (DEC-7): delivery errors are handled by the
    dispatcher, and anything else is a bug that should surface.
    """

    def __init__(self) -> None:
        self._handlers: list[Callable[[Event], object]] = []

    def subscribe(self, handler: Callable[[Event], object]) -> None:
        self._handlers.append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers:
            handler(event)
