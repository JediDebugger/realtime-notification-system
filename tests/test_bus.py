import pytest

from notifications.bus import InProcessEventBus
from notifications.events import PlayerLeveledUp


def test_subscriber_receives_published_event():
    bus = InProcessEventBus()
    received = []
    bus.subscribe(received.append)
    event = PlayerLeveledUp(1, 15)
    bus.publish(event)
    assert received == [event]


def test_subscribers_called_in_subscription_order():
    bus = InProcessEventBus()
    calls = []
    bus.subscribe(lambda e: calls.append("first"))
    bus.subscribe(lambda e: calls.append("second"))
    bus.publish(PlayerLeveledUp(1, 15))
    assert calls == ["first", "second"]


def test_every_event_reaches_every_subscriber():
    bus = InProcessEventBus()
    calls = []
    bus.subscribe(lambda e: calls.append(("a", e.new_level)))
    bus.subscribe(lambda e: calls.append(("b", e.new_level)))
    bus.publish(PlayerLeveledUp(1, 15))
    bus.publish(PlayerLeveledUp(1, 16))
    assert calls == [("a", 15), ("b", 15), ("a", 16), ("b", 16)]


def test_publish_without_subscribers_does_nothing():
    InProcessEventBus().publish(PlayerLeveledUp(1, 15))


def test_handler_exception_propagates():
    bus = InProcessEventBus()

    def failing_handler(event):
        raise RuntimeError("boom")

    bus.subscribe(failing_handler)
    with pytest.raises(RuntimeError, match="boom"):
        bus.publish(PlayerLeveledUp(1, 15))
