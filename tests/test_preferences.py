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
