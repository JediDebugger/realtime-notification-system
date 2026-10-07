import dataclasses
from datetime import UTC, datetime

import pytest

from notifications.notification import Category, Notification, NotificationType


def make_notification(**overrides) -> Notification:
    fields = {
        "recipient_id": 1,
        "type": NotificationType.LEVEL_UP,
        "category": Category.GAME,
        "message": "Congratulations! You've reached level 15!",
        "data": {"level": 15},
    }
    fields.update(overrides)
    return Notification(**fields)


def test_notification_stores_its_fields():
    n = make_notification()
    assert n.recipient_id == 1
    assert n.type is NotificationType.LEVEL_UP
    assert n.category is Category.GAME
    assert n.message == "Congratulations! You've reached level 15!"
    assert dict(n.data) == {"level": 15}


def test_notification_is_immutable():
    n = make_notification()
    with pytest.raises(dataclasses.FrozenInstanceError):
        n.message = "changed"


def test_notification_data_is_read_only():
    n = make_notification()
    with pytest.raises(TypeError):
        n.data["level"] = 16


def test_notification_data_is_a_copy_of_the_input():
    original = {"level": 15}
    n = make_notification(data=original)
    original["level"] = 99
    assert n.data["level"] == 15


def test_each_notification_gets_a_unique_id():
    assert make_notification().id != make_notification().id


def test_created_at_is_utc():
    assert make_notification().created_at.tzinfo is UTC


def test_category_labels_match_spec():
    assert Category.GAME.value == "Game Events"
    assert Category.SOCIAL.value == "Social Events"


def test_notification_can_go_in_a_set():
    n = make_notification()
    assert n in {n}


def test_equal_notifications_collapse_in_a_set():
    when = datetime(2026, 10, 7, tzinfo=UTC)
    a = make_notification(id="n-1", created_at=when)
    b = make_notification(id="n-1", created_at=when)
    assert a == b
    assert len({a, b}) == 1


def test_notifications_differing_only_in_data_are_not_equal():
    when = datetime(2026, 10, 7, tzinfo=UTC)
    a = make_notification(id="n-1", created_at=when, data={"level": 15})
    b = make_notification(id="n-1", created_at=when, data={"level": 16})
    assert a != b
