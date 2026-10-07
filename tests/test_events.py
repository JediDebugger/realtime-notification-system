import dataclasses

import pytest

from notifications.events import (
    ChallengeCompleted,
    FriendRequestAccepted,
    FriendRequestSent,
    ItemAcquired,
    PlayerLeveledUp,
)


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


def test_item_acquired_holds_fields():
    event = ItemAcquired(player_id=2, item_id="SwordOfAzeroth")
    assert (event.player_id, event.item_id) == (2, "SwordOfAzeroth")


@pytest.mark.parametrize("player_id", [0, True, "2"])
def test_item_acquired_rejects_bad_player_id(player_id):
    with pytest.raises(ValueError):
        ItemAcquired(player_id, "SwordOfAzeroth")


@pytest.mark.parametrize("item_id", ["", "   ", None])
def test_item_acquired_rejects_blank_item_id(item_id):
    with pytest.raises(ValueError):
        ItemAcquired(2, item_id)


@pytest.mark.parametrize("challenge_name", ["", "  "])
def test_challenge_completed_rejects_blank_name(challenge_name):
    with pytest.raises(ValueError):
        ChallengeCompleted(1, challenge_name)


@pytest.mark.parametrize("player_id", [0, True, "1"])
def test_challenge_completed_rejects_bad_player_id(player_id):
    with pytest.raises(ValueError):
        ChallengeCompleted(player_id, "Dragon's Lair")


def test_friend_request_to_self_is_rejected():
    with pytest.raises(ValueError):
        FriendRequestSent(3, 3)


@pytest.mark.parametrize(("sender_id", "recipient_id"), [(0, 1), (3, -1), (True, 1), (3, "1")])
def test_friend_request_rejects_bad_ids(sender_id, recipient_id):
    with pytest.raises(ValueError):
        FriendRequestSent(sender_id, recipient_id)


def test_accepting_own_request_is_rejected():
    with pytest.raises(ValueError):
        FriendRequestAccepted(1, 1)


@pytest.mark.parametrize(("accepter_id", "requester_id"), [(0, 3), (1, True)])
def test_friend_accepted_rejects_bad_ids(accepter_id, requester_id):
    with pytest.raises(ValueError):
        FriendRequestAccepted(accepter_id, requester_id)
