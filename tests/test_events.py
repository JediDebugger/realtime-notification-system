import dataclasses

import pytest

from notifications.events import PlayerLeveledUp


def test_player_leveled_up_holds_fields():
    event = PlayerLeveledUp(player_id=1, new_level=15)
    assert event.player_id == 1
    assert event.new_level == 15


def test_player_leveled_up_is_immutable():
    event = PlayerLeveledUp(1, 15)
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.new_level = 16


# True is an int in Python, so it would pass a plain isinstance(x, int) check.
@pytest.mark.parametrize("player_id", [0, -1, True, "1", 1.0])
def test_player_leveled_up_rejects_bad_player_id(player_id):
    with pytest.raises(ValueError):
        PlayerLeveledUp(player_id, 15)


@pytest.mark.parametrize("new_level", [0, -5, True, "15"])
def test_player_leveled_up_rejects_bad_level(new_level):
    with pytest.raises(ValueError):
        PlayerLeveledUp(1, new_level)


def test_level_one_is_valid():
    assert PlayerLeveledUp(1, 1).new_level == 1
