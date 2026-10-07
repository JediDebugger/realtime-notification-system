"""The spec's example triggers, end to end through build_app() and the producers."""

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
