import os
import tempfile

import pytest

import app as app_module


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    application = app_module.create_app(db_path=path)
    application.config["TESTING"] = True
    with application.test_client() as c:
        yield c
    os.unlink(path)


def test_full_flow_grants_xp_and_first_badge(client):
    r = client.post("/api/sessions/start", json={"duration_minutes": 25})
    assert r.status_code == 201
    sid = r.get_json()["session_id"]

    r = client.post(f"/api/sessions/{sid}/complete")
    assert r.status_code == 200
    data = r.get_json()
    assert data["xp_gained"] == 25
    assert data["profile"]["xp"] == 25
    assert data["profile"]["total_completed"] == 1
    assert any(b["code"] == "first_pomodoro" for b in data["new_badges"])


def test_complete_twice_is_rejected(client):
    sid = client.post("/api/sessions/start", json={"duration_minutes": 25}).get_json()["session_id"]
    client.post(f"/api/sessions/{sid}/complete")
    r = client.post(f"/api/sessions/{sid}/complete")
    assert r.status_code == 409


def test_cancel_removes_session(client):
    sid = client.post("/api/sessions/start", json={"duration_minutes": 25}).get_json()["session_id"]
    r = client.post(f"/api/sessions/{sid}/cancel")
    assert r.status_code == 200
    # the cancelled session should not count as started
    stats = client.get("/api/stats").get_json()
    assert stats["weekly"]["summary"]["started"] == 0


def test_invalid_duration(client):
    r = client.post("/api/sessions/start", json={"duration_minutes": 0})
    assert r.status_code == 400


def test_stats_endpoint_shape(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.get_json()
    assert set(data) == {"weekly", "monthly"}
    assert len(data["weekly"]["daily"]) == 7
    assert len(data["monthly"]["daily"]) == 30


def test_profile_endpoint_initial(client):
    r = client.get("/api/profile")
    assert r.status_code == 200
    p = r.get_json()
    assert p["xp"] == 0
    assert p["level"] == 1
    assert p["streak"] == 0
    assert p["badges"] == []
