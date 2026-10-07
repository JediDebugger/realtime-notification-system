"""Composition root: builds every component and wires them together."""

from dataclasses import dataclass

from notifications.bus import InProcessEventBus
from notifications.channels import InAppChannel
from notifications.composers import default_composers
from notifications.dispatcher import NotificationDispatcher
from notifications.preferences import InMemoryPreferenceStore
from notifications.producers import GameEngine


@dataclass
class App:
    game_engine: GameEngine
    preferences: InMemoryPreferenceStore
    in_app: InAppChannel


def build_app() -> App:
    bus = InProcessEventBus()
    preferences = InMemoryPreferenceStore()
    in_app = InAppChannel()
    dispatcher = NotificationDispatcher(default_composers(), preferences, [in_app])
    bus.subscribe(dispatcher.handle)
    return App(game_engine=GameEngine(bus), preferences=preferences, in_app=in_app)
