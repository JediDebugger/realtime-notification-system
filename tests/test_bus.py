import logging

from notifications.bus import InProcessEventBus
from notifications.dispatcher import NotificationDispatcher
from notifications.events import PlayerLeveledUp
from notifications.preferences import InMemoryPreferenceStore
from notifications.producers import GameEngine


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


def failing_handler(event):
    raise RuntimeError("boom")


def test_handler_failure_does_not_reach_the_publisher():
    bus = InProcessEventBus()
    bus.subscribe(failing_handler)
    bus.publish(PlayerLeveledUp(1, 15))  # returns normally


def test_handler_failure_is_logged_with_traceback(caplog):
    bus = InProcessEventBus()
    bus.subscribe(failing_handler)
    bus.publish(PlayerLeveledUp(1, 15))
    [record] = [r for r in caplog.records if r.name == "notifications"]
    assert record.levelno == logging.ERROR
    assert record.getMessage() == "Subscriber failing_handler failed on PlayerLeveledUp"
    assert record.exc_info is not None and record.exc_info[0] is RuntimeError


def test_later_subscribers_still_run_after_a_failure():
    bus = InProcessEventBus()
    received = []
    bus.subscribe(failing_handler)
    bus.subscribe(received.append)
    event = PlayerLeveledUp(1, 15)
    bus.publish(event)
    assert received == [event]


def test_composer_bug_does_not_break_the_game_call(recording_channel, caplog):
    def broken_composer(event):
        raise RuntimeError("composer bug")

    bus = InProcessEventBus()
    dispatcher = NotificationDispatcher(
        {PlayerLeveledUp: broken_composer}, InMemoryPreferenceStore(), [recording_channel]
    )
    bus.subscribe(dispatcher.handle)

    GameEngine(bus).player_leveled_up(1, 15)  # returns normally

    assert recording_channel.received == []
    assert (
        "notifications",
        logging.ERROR,
        "Subscriber NotificationDispatcher.handle failed on PlayerLeveledUp",
    ) in caplog.record_tuples
