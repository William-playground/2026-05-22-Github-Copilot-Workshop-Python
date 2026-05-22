"""Flask Pomodoro Timer with gamification.

Run with::

    pip install -r requirements.txt
    python app.py

then open http://127.0.0.1:5000/ in a browser.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from flask import Flask, g, jsonify, render_template, request

import gamification
from gamification import SessionRecord


DEFAULT_DB_PATH = str(Path(__file__).resolve().parent / "pomodoro.db")


def _utcnow() -> datetime:
    """Return a naive UTC ``datetime`` (suitable for SQLite TEXT storage)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = db_path or os.environ.get("POMODORO_DB", DEFAULT_DB_PATH)

    # -- DB helpers -----------------------------------------------------
    def get_db() -> sqlite3.Connection:
        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = sqlite3.connect(app.config["DATABASE"])
            db.row_factory = sqlite3.Row
        return db

    @app.teardown_appcontext
    def close_db(_exc):  # noqa: D401
        db = getattr(g, "_database", None)
        if db is not None:
            db.close()

    def init_db() -> None:
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TIMESTAMP NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    completed_at TIMESTAMP
                );
                """
            )

    init_db()

    # -- Loading sessions ----------------------------------------------
    def load_sessions() -> List[SessionRecord]:
        cur = get_db().execute(
            "SELECT started_at, duration_minutes, completed, completed_at FROM sessions"
        )
        records: List[SessionRecord] = []
        for row in cur.fetchall():
            started = row["started_at"]
            completed_at = row["completed_at"]
            if isinstance(started, str):
                started = datetime.fromisoformat(started)
            if isinstance(completed_at, str):
                completed_at = datetime.fromisoformat(completed_at)
            records.append(
                SessionRecord(
                    started_at=started,
                    duration_minutes=row["duration_minutes"],
                    completed=bool(row["completed"]),
                    completed_at=completed_at,
                )
            )
        return records

    # -- Routes ---------------------------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/sessions/start", methods=["POST"])
    def start_session():
        payload = request.get_json(silent=True) or {}
        duration = int(payload.get("duration_minutes", 25))
        if duration <= 0 or duration > 180:
            return jsonify({"error": "duration_minutes must be between 1 and 180"}), 400
        db = get_db()
        cur = db.execute(
            "INSERT INTO sessions (started_at, duration_minutes, completed) VALUES (?, ?, 0)",
            (_utcnow().isoformat(), duration),
        )
        db.commit()
        return jsonify({"session_id": cur.lastrowid}), 201

    @app.route("/api/sessions/<int:session_id>/complete", methods=["POST"])
    def complete_session(session_id: int):
        db = get_db()
        cur = db.execute("SELECT id, completed FROM sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        if row is None:
            return jsonify({"error": "session not found"}), 404
        if row["completed"]:
            return jsonify({"error": "session already completed"}), 409

        before = gamification.build_profile(load_sessions())
        db.execute(
            "UPDATE sessions SET completed = 1, completed_at = ? WHERE id = ?",
            (_utcnow().isoformat(), session_id),
        )
        db.commit()
        after = gamification.build_profile(load_sessions())

        leveled_up = after.level > before.level
        new_badges = [
            {"code": b.code, "name": b.name, "description": b.description}
            for b in after.badges
            if b.code not in {x.code for x in before.badges}
        ]
        return jsonify(
            {
                "profile": _profile_to_dict(after),
                "leveled_up": leveled_up,
                "new_badges": new_badges,
                "xp_gained": gamification.XP_PER_POMODORO,
            }
        )

    @app.route("/api/sessions/<int:session_id>/cancel", methods=["POST"])
    def cancel_session(session_id: int):
        db = get_db()
        cur = db.execute("DELETE FROM sessions WHERE id = ? AND completed = 0", (session_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "session not found or already completed"}), 404
        return jsonify({"ok": True})

    @app.route("/api/profile", methods=["GET"])
    def profile():
        return jsonify(_profile_to_dict(gamification.build_profile(load_sessions())))

    @app.route("/api/stats", methods=["GET"])
    def stats():
        sessions = load_sessions()
        return jsonify(
            {
                "weekly": {
                    "summary": gamification.summarize(sessions, 7),
                    "daily": gamification.daily_counts(sessions, 7),
                },
                "monthly": {
                    "summary": gamification.summarize(sessions, 30),
                    "daily": gamification.daily_counts(sessions, 30),
                },
            }
        )

    return app


def _profile_to_dict(profile: gamification.Profile) -> dict:
    return {
        "xp": profile.xp,
        "level": profile.level,
        "level_progress": profile.level_progress,
        "streak": profile.streak,
        "best_streak": profile.best_streak,
        "total_completed": profile.total_completed,
        "badges": [
            {"code": b.code, "name": b.name, "description": b.description}
            for b in profile.badges
        ],
    }


app = create_app()


if __name__ == "__main__":  # pragma: no cover - manual entry point
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(debug=debug)
