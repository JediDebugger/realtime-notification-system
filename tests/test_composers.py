import pytest

from notifications.app import DEMO_ITEMS, DEMO_PLAYERS
from notifications.composers import compose_level_up, default_composers
from notifications.events import PlayerLeveledUp
from notifications.lookups import ItemCatalog, PlayerDirectory
from notifications.notification import Category, NotificationType


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
