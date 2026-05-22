import importlib.util
import sys
import unittest
from pathlib import Path


APP_PATH = Path(__file__).parent / "1.pomodoro" / "app.py"
spec = importlib.util.spec_from_file_location("pomodoro_app", APP_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)
PomodoroTimer = module.PomodoroTimer


class PomodoroCompletionTests(unittest.TestCase):
    def test_stops_and_updates_stats_when_timer_reaches_zero(self):
        timer = PomodoroTimer(work_minutes=1)

        timer.start()
        timer.tick(60)

        self.assertFalse(timer.is_running)
        self.assertEqual(timer.remaining_seconds, 0)
        self.assertEqual(timer.completed_count, 1)
        self.assertEqual(timer.today_focus_minutes, 1)
        self.assertEqual(timer.status_label, "完了")
        self.assertEqual(timer.remaining_time_text, "00:00")
        self.assertEqual(timer.ring_progress_percent, 100)

    def test_stop_sets_status_to_stopped_when_not_completed(self):
        timer = PomodoroTimer(work_minutes=1)

        timer.start()
        timer.tick(1)
        timer.stop()

        self.assertEqual(timer.status_label, "停止中")

    def test_completion_publishes_updated_progress_immediately(self):
        updates = []

        timer = PomodoroTimer(work_minutes=1, on_update=updates.append)
        timer.start()
        timer.tick(60)

        latest = updates[-1]
        self.assertEqual(latest.completed_count, 1)
        self.assertEqual(latest.today_focus_minutes, 1)
        self.assertEqual(latest.status_label, "完了")


if __name__ == "__main__":
    unittest.main()
