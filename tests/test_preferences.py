import pytest

from notifications.notification import Category, Notification, NotificationType
from notifications.preferences import InMemoryPreferenceStore


def notification_for(recipient_id: int, category: Category) -> Notification:
    return Notification(
        recipient_id=recipient_id,
        type=NotificationType.LEVEL_UP,
        category=category,
        message="any message",
        data={},
    )


def test_users_without_settings_receive_everything():
    store = InMemoryPreferenceStore()
    assert store.allows(notification_for(99, Category.GAME))
    assert store.allows(notification_for(99, Category.SOCIAL))


def test_disabled_category_is_not_allowed():
    store = InMemoryPreferenceStore()
    store.set_enabled(1, Category.GAME, False)
    assert not store.allows(notification_for(1, Category.GAME))


def test_re_enabling_restores_delivery():
    store = InMemoryPreferenceStore()
    store.set_enabled(1, Category.GAME, False)
    store.set_enabled(1, Category.GAME, True)
    assert store.allows(notification_for(1, Category.GAME))


def test_categories_are_independent():
    store = InMemoryPreferenceStore()
    store.set_enabled(1, Category.GAME, False)
    assert store.allows(notification_for(1, Category.SOCIAL))


def test_users_are_independent():
    store = InMemoryPreferenceStore()
    store.set_enabled(1, Category.GAME, False)
    assert store.allows(notification_for(2, Category.GAME))


# True is an int in Python, so it would pass a plain isinstance(x, int) check.
@pytest.mark.parametrize("user_id", [0, -1, True, "1"])
def test_set_enabled_rejects_bad_user_ids(user_id):
    with pytest.raises(ValueError):
        InMemoryPreferenceStore().set_enabled(user_id, Category.GAME, False)


def test_set_enabled_rejects_a_category_label_instead_of_a_category():
    # Before this check, the label was stored under a key nothing ever reads.
    with pytest.raises(TypeError):
        InMemoryPreferenceStore().set_enabled(1, "Game Events", False)
