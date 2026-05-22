from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class TimerViewState:
    remaining_time_text: str
    ring_progress_percent: int
    status_label: str
    completed_count: int
    today_focus_minutes: int


class PomodoroTimer:
    """Simple pomodoro timer state machine."""

    def __init__(self, work_minutes: int = 25, on_update: Optional[Callable[[TimerViewState], None]] = None) -> None:
        if work_minutes <= 0:
            raise ValueError("work_minutes must be positive")

        self.work_minutes = work_minutes
        self.work_duration_seconds = work_minutes * 60
        self.on_update = on_update

        self.is_running = False
        self.remaining_seconds = self.work_duration_seconds
        self.completed_count = 0
        self.today_focus_minutes = 0
        self.status_label = "停止中"

        self.remaining_time_text = self._format_time(self.remaining_seconds)
        self.ring_progress_percent = 0

    @property
    def remaining_time(self) -> int:
        return self.remaining_seconds

    def start(self) -> None:
        if self.remaining_seconds <= 0:
            self.reset()
        self.is_running = True
        self.status_label = "作業中"
        self._publish_update()

    def stop(self) -> None:
        self.is_running = False
        if self.remaining_seconds == 0:
            self.status_label = "完了"
        else:
            self.status_label = "停止中"
        self._publish_update()

    def pause(self) -> None:
        self.stop()

    def reset(self) -> None:
        self.is_running = False
        self.remaining_seconds = self.work_duration_seconds
        self.status_label = "停止中"
        self._sync_display_fields()
        self._publish_update()

    def tick(self, seconds: int = 1) -> None:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        if not self.is_running or seconds == 0:
            return

        self.remaining_seconds = max(0, self.remaining_seconds - seconds)

        if self.remaining_seconds == 0:
            self._complete_session()
            return

        self._sync_display_fields()
        self._publish_update()

    def _complete_session(self) -> None:
        self.is_running = False
        self.remaining_seconds = 0
        self.completed_count += 1
        self.today_focus_minutes += self.work_minutes
        self.status_label = "完了"
        self._sync_display_fields()
        self._publish_update()

    def _sync_display_fields(self) -> None:
        self.remaining_time_text = self._format_time(self.remaining_seconds)
        elapsed = self.work_duration_seconds - self.remaining_seconds
        progress = int(round((elapsed / self.work_duration_seconds) * 100))
        self.ring_progress_percent = max(0, min(100, progress))

    @staticmethod
    def _format_time(total_seconds: int) -> str:
        minutes, seconds = divmod(max(0, total_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def get_view_state(self) -> TimerViewState:
        return TimerViewState(
            remaining_time_text=self.remaining_time_text,
            ring_progress_percent=self.ring_progress_percent,
            status_label=self.status_label,
            completed_count=self.completed_count,
            today_focus_minutes=self.today_focus_minutes,
        )

    def _publish_update(self) -> None:
        if self.on_update is None:
            return
        self.on_update(self.get_view_state())
