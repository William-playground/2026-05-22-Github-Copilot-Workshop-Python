from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parent
POMODORO_DIR = REPO_ROOT / "1.pomodoro"


class PomodoroPhase7Tests(unittest.TestCase):
    def test_index_has_accessible_controls(self):
        html = (POMODORO_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-label="タイマー操作"', html)
        self.assertIn('id="start-btn"', html)
        self.assertIn('id="pause-btn"', html)
        self.assertIn('id="reset-btn"', html)
        self.assertIn('aria-live="polite"', html)

    def test_css_has_interaction_and_mobile_rules(self):
        css = (POMODORO_DIR / "static/css/style.css").read_text(encoding="utf-8")
        self.assertIn(":hover", css)
        self.assertIn(":focus-visible", css)
        self.assertIn(":active", css)
        self.assertIn("@media (max-width: 480px)", css)

    def test_js_shows_timer_states_without_debug_log(self):
        js = (POMODORO_DIR / "static/js/timer.js").read_text(encoding="utf-8")
        self.assertIn("実行中", js)
        self.assertIn("停止中", js)
        self.assertNotIn("console.log(", js)


if __name__ == "__main__":
    unittest.main()
