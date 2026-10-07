"""The spec's example triggers, end to end through build_app() and the producers."""

import logging

import pytest

from notifications.notification import Category


def test_T1_level_up_reaches_player_1(app):
    app.game_engine.player_leveled_up(1, 15)
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (1, "Congratulations! You've reached level 15!"),
    ]


def test_invalid_level_up_raises_and_sends_nothing(app):
    with pytest.raises(ValueError):
        app.game_engine.player_leveled_up(1, 0)
    assert app.in_app.delivered == []


def test_level_up_suppressed_when_player_disables_game_events(app):
    app.preferences.set_enabled(1, Category.GAME, False)
    app.game_engine.player_leveled_up(1, 15)
    app.game_engine.player_leveled_up(2, 15)
    assert [n.recipient_id for n in app.in_app.delivered] == [2]


def test_T2_item_acquired_reaches_player_2(app):
    app.game_engine.item_acquired(2, "SwordOfAzeroth")
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (2, "You've acquired the legendary Sword of Azeroth!"),
    ]


def test_common_item_sends_nothing(app):
    app.game_engine.item_acquired(2, "HealthPotion")
    assert app.in_app.delivered == []


def test_challenge_completed_reaches_player(app):
    app.game_engine.challenge_completed(1, "Dragon's Lair")
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (1, "Well done! You've completed 'Dragon's Lair'!"),
    ]


def test_T3_friend_request_reaches_user_1_not_user_3(app):
    app.social_system.friend_request_sent(3, 1)
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (1, "Player 'Cyra' has sent you a friend request."),
    ]


def test_T3_uses_recipients_preferences_not_senders(app):
    app.preferences.set_enabled(3, Category.SOCIAL, False)
    app.social_system.friend_request_sent(3, 1)
    assert [n.recipient_id for n in app.in_app.delivered] == [1]

    app.preferences.set_enabled(1, Category.SOCIAL, False)
    app.social_system.friend_request_sent(3, 1)
    assert [n.recipient_id for n in app.in_app.delivered] == [1]  # second one suppressed


def test_disabling_game_events_does_not_block_friend_requests(app):
    app.preferences.set_enabled(1, Category.GAME, False)
    app.social_system.friend_request_sent(3, 1)
    assert [n.recipient_id for n in app.in_app.delivered] == [1]


def test_T4_acceptance_reaches_requester_3_not_accepter_1(app):
    # Arguments are actor first, not requester first. In T3 the requester (3)
    # comes first because they act; here user 1 acts by accepting, so the
    # requester (3) comes second, and 3 is the one notified.
    app.social_system.friend_request_accepted(1, 3)
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (3, "Player 'Aria' accepted your friend request."),
    ]


def test_new_follower_reaches_followed_player_only(app):
    app.social_system.player_followed(4, 1)
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (1, "Player 'Dax' started following you."),
    ]


def test_pvp_notifies_only_the_attacked_or_defeated_player(app):
    app.game_engine.player_attacked(2, 1)
    app.game_engine.player_defeated(2, 1)
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (1, "Player 'Borin' is attacking you!"),
        (1, "You've been defeated by Player 'Borin'."),
    ]


def test_pvp_respects_game_events_preference(app):
    app.preferences.set_enabled(1, Category.GAME, False)
    app.game_engine.player_attacked(2, 1)
    app.game_engine.player_defeated(2, 1)
    assert app.in_app.delivered == []


@pytest.mark.parametrize(
    ("call", "event_name"),
    [
        (lambda app: app.social_system.friend_request_sent(1, 1), "FriendRequestSent"),
        (lambda app: app.social_system.friend_request_accepted(1, 1), "FriendRequestAccepted"),
        (lambda app: app.social_system.player_followed(1, 1), "PlayerFollowed"),
        (lambda app: app.game_engine.player_attacked(1, 1), "PlayerAttacked"),
        (lambda app: app.game_engine.player_defeated(1, 1), "PlayerDefeated"),
    ],
    ids=["friend_request", "friend_accepted", "follow", "attack", "defeat"],
)
def test_self_targeted_events_return_normally_and_notify_nobody(app, caplog, call, event_name):
    caplog.set_level(logging.INFO, logger="notifications")
    call(app)  # returns normally: no ValueError reaches the game
    assert app.in_app.delivered == []
    assert (
        "notifications",
        logging.INFO,
        f"IGNORED {event_name}: not notification-worthy",
    ) in caplog.record_tuples


def test_T4_uses_the_requesters_preferences_not_the_accepters(app):
    app.preferences.set_enabled(1, Category.SOCIAL, False)  # only the accepter (1) is off
    app.social_system.friend_request_accepted(1, 3)
    assert [n.recipient_id for n in app.in_app.delivered] == [3]

    app.preferences.set_enabled(3, Category.SOCIAL, False)  # now the requester (3) is off too
    app.social_system.friend_request_accepted(1, 3)
    assert [n.recipient_id for n in app.in_app.delivered] == [3]  # second one suppressed
