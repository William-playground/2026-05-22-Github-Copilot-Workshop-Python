"""Gamification logic for the Pomodoro timer.

This module is intentionally framework-agnostic so it can be exercised by
unit tests without spinning up the Flask app or a database.  All functions
operate on plain Python data (lists of ``datetime`` objects or dictionaries)
that the persistence layer in :mod:`app` provides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional


# ---------------------------------------------------------------------------
# XP / Level system
# ---------------------------------------------------------------------------

# A completed pomodoro grants this many XP points.
XP_PER_POMODORO = 25

# XP required to *reach* a given level.  Index 0 is unused so that the
# numbers line up with the human-readable level number (level 1 starts at
# 0 XP, level 2 at 100 XP, ...).  The curve is super-linear so leveling up
# becomes progressively harder.
LEVEL_THRESHOLDS = [n * n * 100 for n in range(0, 100)]


def level_for_xp(xp: int) -> int:
    """Return the current level for the supplied total XP."""
    if xp < 0:
        raise ValueError("xp must be non-negative")
    level = 1
    for idx, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = max(level, idx + 1)
        else:
            break
    return level


def xp_progress(xp: int) -> dict:
    """Return progress information towards the next level.

    The returned dictionary contains the current ``level``, ``current_xp``
    (total XP), ``level_xp`` (XP earned within the current level),
    ``next_level_xp`` (XP needed to reach the next level from the start of
    the current one) and ``percent`` (0-100).
    """
    level = level_for_xp(xp)
    current_floor = LEVEL_THRESHOLDS[level - 1]
    if level < len(LEVEL_THRESHOLDS):
        next_floor = LEVEL_THRESHOLDS[level]
    else:  # pragma: no cover - level cap
        next_floor = current_floor
    span = max(next_floor - current_floor, 1)
    level_xp = xp - current_floor
    percent = min(100, int(round(level_xp * 100 / span)))
    return {
        "level": level,
        "current_xp": xp,
        "level_xp": level_xp,
        "next_level_xp": span,
        "percent": percent,
    }


# ---------------------------------------------------------------------------
# Streak calculation
# ---------------------------------------------------------------------------


def _to_dates(completions: Iterable[datetime]) -> List[date]:
    seen = set()
    for ts in completions:
        seen.add(ts.date())
    return sorted(seen)


def current_streak(completions: Iterable[datetime], today: Optional[date] = None) -> int:
    """Return the number of consecutive days (ending today or yesterday).

    If the user completed a pomodoro today, the streak includes today.  If
    not, but they completed one yesterday, the streak still counts (so the
    UI can display "don't break the chain" without immediately resetting at
    midnight).  Otherwise the streak is 0.
    """
    today = today or date.today()
    days = set(_to_dates(completions))
    if today in days:
        cursor = today
    elif (today - timedelta(days=1)) in days:
        cursor = today - timedelta(days=1)
    else:
        return 0
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def longest_streak(completions: Iterable[datetime]) -> int:
    """Return the longest run of consecutive days ever achieved."""
    days = _to_dates(completions)
    if not days:
        return 0
    best = current = 1
    for prev, curr in zip(days, days[1:]):
        if (curr - prev).days == 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


# ---------------------------------------------------------------------------
# Statistics (weekly / monthly)
# ---------------------------------------------------------------------------


@dataclass
class SessionRecord:
    """A pomodoro session as persisted by the app."""

    started_at: datetime
    duration_minutes: int
    completed: bool
    completed_at: Optional[datetime] = None


def daily_counts(
    sessions: Iterable[SessionRecord],
    days: int,
    today: Optional[date] = None,
) -> List[dict]:
    """Return a list of ``{"date", "completed", "started"}`` dictionaries
    covering the most recent ``days`` days (oldest first, today last)."""
    today = today or date.today()
    buckets = {today - timedelta(days=i): {"completed": 0, "started": 0} for i in range(days)}
    for s in sessions:
        d = s.started_at.date()
        if d in buckets:
            buckets[d]["started"] += 1
            if s.completed:
                buckets[d]["completed"] += 1
    return [
        {"date": d.isoformat(), "completed": buckets[d]["completed"], "started": buckets[d]["started"]}
        for d in sorted(buckets)
    ]


def summarize(sessions: Iterable[SessionRecord], days: int, today: Optional[date] = None) -> dict:
    """Return summary statistics over the last ``days`` days."""
    today = today or date.today()
    cutoff = today - timedelta(days=days - 1)
    completed_durations: List[int] = []
    started = 0
    completed = 0
    for s in sessions:
        if s.started_at.date() < cutoff:
            continue
        started += 1
        if s.completed:
            completed += 1
            completed_durations.append(s.duration_minutes)
    completion_rate = (completed / started * 100) if started else 0.0
    avg_focus = (sum(completed_durations) / len(completed_durations)) if completed_durations else 0.0
    return {
        "days": days,
        "started": started,
        "completed": completed,
        "completion_rate": round(completion_rate, 1),
        "average_focus_minutes": round(avg_focus, 1),
        "total_focus_minutes": sum(completed_durations),
    }


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Badge:
    code: str
    name: str
    description: str


BADGES: List[Badge] = [
    Badge("first_pomodoro", "はじめの一歩", "最初のポモドーロを完了した"),
    Badge("ten_pomodoros", "集中の芽", "通算10ポモドーロ完了"),
    Badge("fifty_pomodoros", "集中マスター", "通算50ポモドーロ完了"),
    Badge("hundred_pomodoros", "集中の達人", "通算100ポモドーロ完了"),
    Badge("streak_3", "3日連続", "3日連続でポモドーロを完了した"),
    Badge("streak_7", "1週間継続", "7日連続でポモドーロを完了した"),
    Badge("streak_30", "1ヶ月継続", "30日連続でポモドーロを完了した"),
    Badge("week_10", "今週10回", "直近7日間で10回完了"),
    Badge("week_25", "今週25回", "直近7日間で25回完了"),
    Badge("level_5", "レベル5到達", "レベル5に到達した"),
    Badge("level_10", "レベル10到達", "レベル10に到達した"),
]

_BADGES_BY_CODE = {b.code: b for b in BADGES}


def get_badge(code: str) -> Badge:
    return _BADGES_BY_CODE[code]


def evaluate_badges(
    sessions: Iterable[SessionRecord],
    today: Optional[date] = None,
) -> List[str]:
    """Return the list of badge codes the user has unlocked."""
    today = today or date.today()
    sessions = list(sessions)
    completions = [s.completed_at or s.started_at for s in sessions if s.completed]
    total_completed = len(completions)

    earned: List[str] = []

    if total_completed >= 1:
        earned.append("first_pomodoro")
    if total_completed >= 10:
        earned.append("ten_pomodoros")
    if total_completed >= 50:
        earned.append("fifty_pomodoros")
    if total_completed >= 100:
        earned.append("hundred_pomodoros")

    streak = current_streak(completions, today)
    best = max(streak, longest_streak(completions))
    if best >= 3:
        earned.append("streak_3")
    if best >= 7:
        earned.append("streak_7")
    if best >= 30:
        earned.append("streak_30")

    week_summary = summarize(sessions, 7, today)
    if week_summary["completed"] >= 10:
        earned.append("week_10")
    if week_summary["completed"] >= 25:
        earned.append("week_25")

    xp = total_completed * XP_PER_POMODORO
    level = level_for_xp(xp)
    if level >= 5:
        earned.append("level_5")
    if level >= 10:
        earned.append("level_10")

    return earned


# ---------------------------------------------------------------------------
# Convenience: compute the full player profile
# ---------------------------------------------------------------------------


@dataclass
class Profile:
    xp: int
    level: int
    level_progress: dict
    streak: int
    best_streak: int
    total_completed: int
    badges: List[Badge] = field(default_factory=list)


def build_profile(sessions: Iterable[SessionRecord], today: Optional[date] = None) -> Profile:
    sessions = list(sessions)
    completions = [s.completed_at or s.started_at for s in sessions if s.completed]
    total = len(completions)
    xp = total * XP_PER_POMODORO
    badge_codes = evaluate_badges(sessions, today)
    return Profile(
        xp=xp,
        level=level_for_xp(xp),
        level_progress=xp_progress(xp),
        streak=current_streak(completions, today),
        best_streak=longest_streak(completions),
        total_completed=total,
        badges=[get_badge(c) for c in badge_codes],
    )
