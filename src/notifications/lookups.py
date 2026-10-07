"""In-memory stand-ins for the platform's player profiles and item catalog (A-5, A-8)."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import IntEnum


class Rarity(IntEnum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5

    @property
    def label(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class ItemInfo:
    name: str
    rarity: Rarity


class PlayerDirectory:
    def __init__(self, names: Mapping[int, str]) -> None:
        self._names = dict(names)

    def display_name(self, player_id: int) -> str:
        return self._names.get(player_id, str(player_id))


class ItemCatalog:
    """Looks items up by exact id, so a different case is a different item."""

    def __init__(self, items: Mapping[str, ItemInfo]) -> None:
        self._items = dict(items)

    def lookup(self, item_id: str) -> ItemInfo | None:
        return self._items.get(item_id)
