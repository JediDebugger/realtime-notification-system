import pytest

from notifications.app import App, build_app
from notifications.notification import Notification


class RecordingChannel:
    """Test double for NotificationChannel: keeps everything it's sent."""

    def __init__(self) -> None:
        self.received: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.received.append(notification)


class FailingChannel:
    """Test double for a channel whose delivery always fails."""

    def __init__(self) -> None:
        self.attempted: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.attempted.append(notification)
        raise RuntimeError("boom")


@pytest.fixture
def recording_channel() -> RecordingChannel:
    return RecordingChannel()


@pytest.fixture
def failing_channel() -> FailingChannel:
    return FailingChannel()


@pytest.fixture
def app() -> App:
    return build_app()
