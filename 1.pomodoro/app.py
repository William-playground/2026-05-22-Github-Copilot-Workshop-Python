"""Pomodoro Timer App (Pattern B: customizable UI / features).

A small Flask application that serves a Pomodoro timer with the
following user-configurable options:

* Work duration: 15 / 25 / 35 / 45 minutes
* Break duration: 5 / 10 / 15 minutes
* Theme: dark / light / focus-minimal
* Sound toggles: start sound / end sound / tick sound

The whole UI is shipped as a single page so that the app can be run
locally without any extra build tooling.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template

# Choices exposed both to the UI and to tests so they stay in sync.
WORK_MINUTES_CHOICES = [15, 25, 35, 45]
BREAK_MINUTES_CHOICES = [5, 10, 15]
THEME_CHOICES = ["dark", "light", "focus-minimal"]
SOUND_CHOICES = ["start", "end", "tick"]

DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "break_minutes": 5,
    "theme": "dark",
    "sounds": {"start": True, "end": True, "tick": False},
}


def create_app() -> Flask:
    """Application factory used by both the CLI entry point and tests."""

    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return render_template(
            "index.html",
            work_choices=WORK_MINUTES_CHOICES,
            break_choices=BREAK_MINUTES_CHOICES,
            theme_choices=THEME_CHOICES,
            sound_choices=SOUND_CHOICES,
            defaults=DEFAULT_SETTINGS,
        )

    @app.route("/api/settings/options")
    def settings_options():
        """Expose the available configuration options as JSON."""

        return jsonify(
            {
                "work_minutes": WORK_MINUTES_CHOICES,
                "break_minutes": BREAK_MINUTES_CHOICES,
                "themes": THEME_CHOICES,
                "sounds": SOUND_CHOICES,
                "defaults": DEFAULT_SETTINGS,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    app.run(host="127.0.0.1", port=5000)
