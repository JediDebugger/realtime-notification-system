from notifications.channels import InAppChannel
from notifications.notification import Category, Notification, NotificationType


def level_up_for(recipient_id: int, level: int) -> Notification:
    return Notification(
        recipient_id=recipient_id,
        type=NotificationType.LEVEL_UP,
        category=Category.GAME,
        message=f"Congratulations! You've reached level {level}!",
        data={"level": level},
    )


def test_send_records_the_notification():
    channel = InAppChannel()
    n = level_up_for(1, 15)
    channel.send(n)
    assert channel.delivered == [n]


def test_send_prints_recipient_and_message(capsys):
    InAppChannel().send(level_up_for(1, 15))
    assert capsys.readouterr().out == "[in-app] to player 1: Congratulations! You've reached level 15!\n"


def test_delivered_preserves_order():
    channel = InAppChannel()
    first, second = level_up_for(1, 15), level_up_for(2, 3)
    channel.send(first)
    channel.send(second)
    assert channel.delivered == [first, second]
