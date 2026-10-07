import logging

import pytest

from notifications.app import DEMO_ITEMS, DEMO_PLAYERS
from notifications.composers import compose_level_up, default_composers
from notifications.events import ChallengeCompleted, ItemAcquired, PlayerLeveledUp
from notifications.lookups import ItemCatalog, ItemInfo, PlayerDirectory, Rarity
from notifications.notification import Category, NotificationType


def compose(event, players=DEMO_PLAYERS, items=DEMO_ITEMS):
    """Compose through the registry, as the dispatcher does."""
    composers = default_composers(PlayerDirectory(players), ItemCatalog(items))
    return composers[type(event)](event)


@pytest.mark.parametrize(
    ("new_level", "message"),
    [
        (15, "Congratulations! You've reached level 15!"),
        (2, "Congratulations! You've reached level 2!"),
    ],
)
def test_level_up_message_matches_spec(new_level, message):
    assert compose_level_up(PlayerLeveledUp(1, new_level)).message == message


@pytest.mark.parametrize("player_id", [1, 7])
def test_level_up_goes_to_the_player_who_leveled(player_id):
    assert compose_level_up(PlayerLeveledUp(player_id, 15)).recipient_id == player_id


def test_level_up_type_category_and_data():
    n = compose_level_up(PlayerLeveledUp(1, 15))
    assert n.type is NotificationType.LEVEL_UP
    assert n.category is Category.GAME
    assert n.data == {"level": 15}


def test_default_composers_handles_level_up():
    compose = default_composers(PlayerDirectory(DEMO_PLAYERS), ItemCatalog(DEMO_ITEMS))[PlayerLeveledUp]
    n = compose(PlayerLeveledUp(1, 15))
    assert n.recipient_id == 1
    assert n.message == "Congratulations! You've reached level 15!"


def test_T2_item_message_matches_spec():
    n = compose(ItemAcquired(2, "SwordOfAzeroth"))
    assert n.message == "You've acquired the legendary Sword of Azeroth!"


def test_item_goes_to_the_acquiring_player():
    n = compose(ItemAcquired(2, "SwordOfAzeroth"))
    assert n.recipient_id == 2
    assert n.type is NotificationType.ITEM_ACQUIRED
    assert n.category is Category.GAME
    assert n.data == {"item_id": "SwordOfAzeroth", "rarity": "legendary"}


@pytest.mark.parametrize(
    ("rarity", "label"),
    [(Rarity.RARE, "rare"), (Rarity.EPIC, "epic"), (Rarity.LEGENDARY, "legendary")],
)
def test_rare_and_better_items_notify(rarity, label):
    items = {"Ring": ItemInfo("Ring of Testing", rarity)}
    n = compose(ItemAcquired(2, "Ring"), items=items)
    assert n.message == f"You've acquired the {label} Ring of Testing!"


@pytest.mark.parametrize("rarity", [Rarity.COMMON, Rarity.UNCOMMON])
def test_common_and_uncommon_items_do_not_notify(rarity):
    items = {"Ring": ItemInfo("Ring of Testing", rarity)}
    assert compose(ItemAcquired(2, "Ring"), items=items) is None


# "swordofazeroth" differs from a catalog id only in case (Review focus 5).
@pytest.mark.parametrize("item_id", ["UnknownThing", "swordofazeroth"])
def test_unknown_item_does_not_notify_and_warns(item_id, caplog):
    assert compose(ItemAcquired(2, item_id)) is None
    assert (
        "notifications",
        logging.WARNING,
        f"Unknown item id '{item_id}'; not notifying",
    ) in caplog.record_tuples


def test_challenge_message():
    n = compose(ChallengeCompleted(1, "Dragon's Lair"))
    assert n.message == "Well done! You've completed 'Dragon's Lair'!"


def test_challenge_goes_to_the_player():
    n = compose(ChallengeCompleted(4, "Dragon's Lair"))
    assert n.recipient_id == 4
    assert n.type is NotificationType.CHALLENGE_COMPLETED
    assert n.category is Category.GAME
    assert n.data == {"challenge": "Dragon's Lair"}
