import dataclasses

import pytest

from notifications.events import (
    ChallengeCompleted,
    FriendRequestAccepted,
    FriendRequestSent,
    ItemAcquired,
    PlayerAttacked,
    PlayerDefeated,
    PlayerFollowed,
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


@pytest.mark.parametrize(("sender_id", "recipient_id"), [(0, 1), (3, -1), (True, 1), (3, "1")])
def test_friend_request_rejects_bad_ids(sender_id, recipient_id):
    with pytest.raises(ValueError):
        FriendRequestSent(sender_id, recipient_id)


@pytest.mark.parametrize(("accepter_id", "requester_id"), [(0, 3), (1, True)])
def test_friend_accepted_rejects_bad_ids(accepter_id, requester_id):
    with pytest.raises(ValueError):
        FriendRequestAccepted(accepter_id, requester_id)


@pytest.mark.parametrize(("follower_id", "followed_id"), [(-4, 1), (4, "1")])
def test_player_followed_rejects_bad_ids(follower_id, followed_id):
    with pytest.raises(ValueError):
        PlayerFollowed(follower_id, followed_id)


@pytest.mark.parametrize("event_type", [PlayerAttacked, PlayerDefeated])
@pytest.mark.parametrize(("actor_id", "target_id"), [(0, 1), (2, True)])
def test_pvp_events_reject_bad_ids(event_type, actor_id, target_id):
    with pytest.raises(ValueError):
        event_type(actor_id, target_id)


# Targeting yourself is a business rule, not a shape error, so the event is
# well-formed; the composers decide it notifies nobody (A-18, DEC-8).
@pytest.mark.parametrize(
    "event_type", [FriendRequestSent, FriendRequestAccepted, PlayerFollowed, PlayerAttacked, PlayerDefeated]
)
def test_self_targeted_events_are_well_formed(event_type):
    event_type(2, 2)
