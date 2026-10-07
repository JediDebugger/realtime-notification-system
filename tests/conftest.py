import pytest

from notifications.app import App, build_app
from notifications.notification import Notification


class RecordingChannel:
    """Test double for NotificationChannel: keeps everything it's sent."""

    def __init__(self) -> None:
        self.received: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.received.append(notification)


@pytest.fixture
def recording_channel() -> RecordingChannel:
    return RecordingChannel()


@pytest.fixture
def app() -> App:
    return build_app()
