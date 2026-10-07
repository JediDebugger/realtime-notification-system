"""Composition root: builds every component and wires them together."""

from dataclasses import dataclass

from notifications.bus import InProcessEventBus
from notifications.channels import InAppChannel
from notifications.composers import default_composers
from notifications.dispatcher import NotificationDispatcher
from notifications.lookups import ItemCatalog, ItemInfo, PlayerDirectory, Rarity
from notifications.preferences import InMemoryPreferenceStore
from notifications.producers import GameEngine

# Demo seed data, shared by the demo and the acceptance tests (DEC-14).
DEMO_PLAYERS = {1: "Aria", 2: "Borin", 3: "Cyra", 4: "Dax"}
DEMO_ITEMS = {
    "SwordOfAzeroth": ItemInfo("Sword of Azeroth", Rarity.LEGENDARY),
    "DragonScaleShield": ItemInfo("Dragon Scale Shield", Rarity.EPIC),
    "HealthPotion": ItemInfo("Health Potion", Rarity.COMMON),
}


@dataclass
class App:
    game_engine: GameEngine
    preferences: InMemoryPreferenceStore
    in_app: InAppChannel


def build_app() -> App:
    bus = InProcessEventBus()
    preferences = InMemoryPreferenceStore()
    in_app = InAppChannel()
    composers = default_composers(PlayerDirectory(DEMO_PLAYERS), ItemCatalog(DEMO_ITEMS))
    dispatcher = NotificationDispatcher(composers, preferences, [in_app])
    bus.subscribe(dispatcher.handle)
    return App(game_engine=GameEngine(bus), preferences=preferences, in_app=in_app)
