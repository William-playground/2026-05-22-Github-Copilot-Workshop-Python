"""Tests for the customizable Pomodoro Flask app."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import (  # noqa: E402
    BREAK_MINUTES_CHOICES,
    DEFAULT_SETTINGS,
    SOUND_CHOICES,
    THEME_CHOICES,
    WORK_MINUTES_CHOICES,
    create_app,
)


def test_choice_constants():
    assert WORK_MINUTES_CHOICES == [15, 25, 35, 45]
    assert BREAK_MINUTES_CHOICES == [5, 10, 15]
    assert THEME_CHOICES == ["dark", "light", "focus-minimal"]
    assert SOUND_CHOICES == ["start", "end", "tick"]
    assert DEFAULT_SETTINGS["work_minutes"] in WORK_MINUTES_CHOICES
    assert DEFAULT_SETTINGS["break_minutes"] in BREAK_MINUTES_CHOICES
    assert DEFAULT_SETTINGS["theme"] in THEME_CHOICES
    assert set(DEFAULT_SETTINGS["sounds"]) == set(SOUND_CHOICES)


def test_index_renders_all_choices():
    client = create_app().test_client()
    res = client.get("/")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    for m in WORK_MINUTES_CHOICES:
        assert f'data-value="{m}"' in body
    for m in BREAK_MINUTES_CHOICES:
        assert f'data-value="{m}"' in body
    for t in THEME_CHOICES:
        assert f'data-value="{t}"' in body
    for s in SOUND_CHOICES:
        assert f'data-name="{s}"' in body


def test_settings_options_endpoint():
    client = create_app().test_client()
    res = client.get("/api/settings/options")
    assert res.status_code == 200
    data = res.get_json()
    assert data["work_minutes"] == WORK_MINUTES_CHOICES
    assert data["break_minutes"] == BREAK_MINUTES_CHOICES
    assert data["themes"] == THEME_CHOICES
    assert data["sounds"] == SOUND_CHOICES
    assert data["defaults"]["theme"] in THEME_CHOICES
