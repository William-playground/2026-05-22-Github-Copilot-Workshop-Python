import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parent
POMODORO_DIR = REPO_ROOT / "1.pomodoro"


class PomodoroPhase6Tests(unittest.TestCase):
    def test_index_template_has_progress_elements(self):
        html = (POMODORO_DIR / "templates/index.html").read_text(encoding="utf-8")
        self.assertIn('id="completed-count"', html)
        self.assertIn('id="focus-time"', html)
        self.assertIn('id="complete-session"', html)

    def test_timer_script_contains_local_storage_logic(self):
        script_path = POMODORO_DIR / "static/js/timer.js"
        script = script_path.read_text(encoding="utf-8")
        self.assertIn("localStorage.getItem", script)
        self.assertIn("localStorage.setItem", script)
        self.assertIn("parsed.date !== today", script)
        self.assertIn("formatFocusTime", script)
        self.assertIn("時間", script)


if __name__ == "__main__":
    unittest.main()
