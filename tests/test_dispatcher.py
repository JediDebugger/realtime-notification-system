import logging

import pytest

from notifications.channels import InAppChannel
from notifications.composers import compose_level_up
from notifications.dispatcher import DispatchOutcome, NotificationDispatcher
from notifications.events import Event, PlayerLeveledUp
from notifications.preferences import InMemoryPreferenceStore


class Unregistered(Event):
    """An event type no composer is registered for."""


def make_dispatcher(channels, composers=None) -> NotificationDispatcher:
    return NotificationDispatcher(
        composers={PlayerLeveledUp: compose_level_up} if composers is None else composers,
        preferences=InMemoryPreferenceStore(),
        channels=channels,
    )


def test_registered_event_is_composed_and_sent(recording_channel):
    outcome = make_dispatcher([recording_channel]).handle(PlayerLeveledUp(1, 15))
    assert outcome is DispatchOutcome.SENT
    assert [n.message for n in recording_channel.received] == [
        "Congratulations! You've reached level 15!"
    ]


def test_every_channel_receives_the_notification(recording_channel):
    in_app = InAppChannel()
    make_dispatcher([recording_channel, in_app]).handle(PlayerLeveledUp(1, 15))
    assert len(recording_channel.received) == 1
    assert len(in_app.delivered) == 1


def test_unregistered_event_is_ignored_with_warning(recording_channel, caplog):
    outcome = make_dispatcher([recording_channel]).handle(Unregistered())
    assert outcome is DispatchOutcome.IGNORED
    assert recording_channel.received == []
    assert (
        "notifications",
        logging.WARNING,
        "IGNORED Unregistered: no composer registered",
    ) in caplog.record_tuples


def test_composer_returning_none_is_ignored(recording_channel, caplog):
    caplog.set_level(logging.INFO, logger="notifications")
    dispatcher = make_dispatcher([recording_channel], composers={PlayerLeveledUp: lambda e: None})
    assert dispatcher.handle(PlayerLeveledUp(1, 15)) is DispatchOutcome.IGNORED
    assert recording_channel.received == []
    assert (
        "notifications",
        logging.INFO,
        "IGNORED PlayerLeveledUp: not notification-worthy",
    ) in caplog.record_tuples


def test_sent_is_logged(recording_channel, caplog):
    caplog.set_level(logging.INFO, logger="notifications")
    make_dispatcher([recording_channel]).handle(PlayerLeveledUp(1, 15))
    assert (
        "notifications",
        logging.INFO,
        "SENT LEVEL_UP to player 1 (Game Events)",
    ) in caplog.record_tuples


def test_dispatcher_requires_a_channel():
    with pytest.raises(ValueError):
        make_dispatcher([])
