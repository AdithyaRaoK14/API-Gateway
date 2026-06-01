from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
from gateway.main import app
from gateway.models.log import RequestLog
from tests.conftest import get_test_session
import uuid

client = TestClient(app)
SECRET_KEY = "supersecretkey"

def make_test_token():
    exp = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"sub": str(uuid.uuid4()), "role": "user", "exp": exp}, SECRET_KEY, algorithm="HS256")

def seed_logs():
    db = get_test_session()
    logs = [
        RequestLog(path="/users/1", method="GET", status_code=200, latency_ms=45, user_id="u1", service="user-svc"),
        RequestLog(path="/users/2", method="GET", status_code=200, latency_ms=30, user_id="u2", service="user-svc"),
        RequestLog(path="/products/1", method="GET", status_code=404, latency_ms=10, user_id="u1", service="prod-svc"),
        RequestLog(path="/users/1", method="POST", status_code=500, latency_ms=200, user_id="u3", service="user-svc"),
    ]
    db.add_all(logs)
    db.commit()
    db.close()

def test_summary_empty():
    token = make_test_token()
    r = client.get("/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["total_requests"] == 0

def test_summary_with_data():
    seed_logs()
    token = make_test_token()
    r = client.get("/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["total_requests"] == 4
    assert data["error_count"] == 2

def test_top_routes():
    seed_logs()
    token = make_test_token()
    r = client.get("/analytics/top-routes", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    routes = r.json()
    assert routes[0]["path"] == "/users/1"
    assert routes[0]["count"] == 2

def test_recent_logs():
    seed_logs()
    token = make_test_token()
    r = client.get("/analytics/recent", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 4

def test_status_breakdown():
    seed_logs()
    token = make_test_token()
    r = client.get("/analytics/status-breakdown", headers={"Authorization": f"Bearer {token}"})
    codes = {item["status_code"]: item["count"] for item in r.json()}
    assert codes[200] == 2
    assert codes[404] == 1
    assert codes[500] == 1

def test_analytics_requires_auth():
    r = client.get("/analytics/summary")
    assert r.status_code == 401
