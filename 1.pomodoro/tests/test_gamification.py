from datetime import date, datetime, timedelta

import pytest

from gamification import (
    BADGES,
    SessionRecord,
    XP_PER_POMODORO,
    build_profile,
    current_streak,
    daily_counts,
    evaluate_badges,
    level_for_xp,
    longest_streak,
    summarize,
    xp_progress,
)


def _completed(d: datetime, minutes: int = 25) -> SessionRecord:
    return SessionRecord(started_at=d, duration_minutes=minutes, completed=True, completed_at=d)


def _started(d: datetime, minutes: int = 25) -> SessionRecord:
    return SessionRecord(started_at=d, duration_minutes=minutes, completed=False)


# ---- XP / Level ----------------------------------------------------------

def test_level_for_xp_levels_up_at_thresholds():
    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(399) == 2
    assert level_for_xp(400) == 3


def test_level_for_xp_rejects_negative():
    with pytest.raises(ValueError):
        level_for_xp(-1)


def test_xp_progress_within_level():
    p = xp_progress(150)  # level 2, 50 / 300 to level 3
    assert p["level"] == 2
    assert p["level_xp"] == 50
    assert p["next_level_xp"] == 300
    assert 0 < p["percent"] < 100


# ---- Streak --------------------------------------------------------------

def test_current_streak_counts_today_and_back():
    today = date(2026, 5, 22)
    sessions = [
        datetime(2026, 5, 20, 9, 0),
        datetime(2026, 5, 21, 9, 0),
        datetime(2026, 5, 22, 9, 0),
    ]
    assert current_streak(sessions, today) == 3


def test_current_streak_allows_yesterday_only():
    today = date(2026, 5, 22)
    sessions = [datetime(2026, 5, 20, 9, 0), datetime(2026, 5, 21, 9, 0)]
    assert current_streak(sessions, today) == 2


def test_current_streak_resets_after_gap():
    today = date(2026, 5, 22)
    sessions = [datetime(2026, 5, 19, 9, 0)]
    assert current_streak(sessions, today) == 0


def test_longest_streak():
    sessions = [
        datetime(2026, 5, 1), datetime(2026, 5, 2), datetime(2026, 5, 3),
        datetime(2026, 5, 10), datetime(2026, 5, 11),
    ]
    assert longest_streak(sessions) == 3


# ---- Stats ---------------------------------------------------------------

def test_summarize_completion_rate_and_average():
    today = date(2026, 5, 22)
    sessions = [
        _completed(datetime(2026, 5, 22, 8, 0), 25),
        _completed(datetime(2026, 5, 21, 8, 0), 30),
        _started(datetime(2026, 5, 21, 9, 0), 25),
        _completed(datetime(2026, 4, 1, 8, 0), 25),  # outside 7-day window
    ]
    summary = summarize(sessions, 7, today)
    assert summary["started"] == 3
    assert summary["completed"] == 2
    assert summary["completion_rate"] == round(2 / 3 * 100, 1)
    assert summary["average_focus_minutes"] == 27.5
    assert summary["total_focus_minutes"] == 55


def test_daily_counts_window():
    today = date(2026, 5, 22)
    sessions = [
        _completed(datetime(2026, 5, 22, 8, 0)),
        _completed(datetime(2026, 5, 22, 9, 0)),
        _started(datetime(2026, 5, 21, 8, 0)),
    ]
    daily = daily_counts(sessions, 7, today)
    assert len(daily) == 7
    assert daily[-1] == {"date": "2026-05-22", "completed": 2, "started": 2}
    assert daily[-2] == {"date": "2026-05-21", "completed": 0, "started": 1}


# ---- Badges --------------------------------------------------------------

def test_badges_unique_codes():
    codes = [b.code for b in BADGES]
    assert len(codes) == len(set(codes))


def test_evaluate_badges_first_and_streak():
    today = date(2026, 5, 22)
    sessions = [_completed(datetime(2026, 5, 20 + i, 8, 0)) for i in range(3)]
    earned = set(evaluate_badges(sessions, today))
    assert {"first_pomodoro", "streak_3"} <= earned


def test_evaluate_badges_week_count():
    today = date(2026, 5, 22)
    sessions = [_completed(datetime(2026, 5, 22, 8, 0) + timedelta(minutes=i)) for i in range(10)]
    earned = set(evaluate_badges(sessions, today))
    assert "week_10" in earned
    assert "week_25" not in earned


def test_evaluate_badges_level_milestones():
    today = date(2026, 5, 22)
    # need enough XP to reach level 5 -> threshold is 1600 XP -> 64 pomodoros
    sessions = [_completed(datetime(2026, 5, 22, 8, 0) - timedelta(days=i)) for i in range(70)]
    earned = set(evaluate_badges(sessions, today))
    assert "level_5" in earned


def test_build_profile_combines_everything():
    today = date(2026, 5, 22)
    sessions = [_completed(datetime(2026, 5, 22, 8, 0) - timedelta(days=i)) for i in range(3)]
    profile = build_profile(sessions, today)
    assert profile.total_completed == 3
    assert profile.xp == 3 * XP_PER_POMODORO
    assert profile.streak == 3
    badge_codes = {b.code for b in profile.badges}
    assert "first_pomodoro" in badge_codes
    assert "streak_3" in badge_codes
