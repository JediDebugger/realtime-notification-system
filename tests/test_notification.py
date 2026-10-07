import dataclasses
from datetime import UTC

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
