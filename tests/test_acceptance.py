"""The spec's example triggers, end to end through build_app() and the producers."""

import pytest


def test_T1_level_up_reaches_player_1(app):
    app.game_engine.player_leveled_up(1, 15)
    assert [(n.recipient_id, n.message) for n in app.in_app.delivered] == [
        (1, "Congratulations! You've reached level 15!"),
    ]


def test_invalid_level_up_raises_and_sends_nothing(app):
    with pytest.raises(ValueError):
        app.game_engine.player_leveled_up(1, 0)
    assert app.in_app.delivered == []
