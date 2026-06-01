from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_register_user():
    r = client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    assert r.status_code == 200
    assert "token" in r.json()

def test_register_duplicate_user():
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    r = client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    assert r.status_code == 400

def test_login_success():
    client.post("/auth/register", json={"username": "bob", "password": "secret"})
    r = client.post("/auth/login", json={"username": "bob", "password": "secret"})
    assert r.status_code == 200
    assert "token" in r.json()

def test_login_wrong_password():
    client.post("/auth/register", json={"username": "carol", "password": "correct"})
    r = client.post("/auth/login", json={"username": "carol", "password": "wrong"})
    assert r.status_code == 401

def test_login_nonexistent_user():
    r = client.post("/auth/login", json={"username": "ghost", "password": "pass"})
    assert r.status_code == 401

def test_register_admin_role():
    r = client.post("/auth/register", json={"username": "admin1", "password": "adminpass", "role": "admin"})
    assert r.status_code == 200

def test_protected_route_no_token():
    r = client.get("/services/")
    assert r.status_code == 401

def test_protected_route_invalid_token():
    r = client.get("/services/", headers={"Authorization": "Bearer faketoken"})
    assert r.status_code == 401

def test_protected_route_valid_token():
    reg = client.post("/auth/register", json={"username": "dave", "password": "pass"})
    token = reg.json()["token"]
    r = client.get("/services/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

def test_health_endpoint_public():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── API Key tests ──
def test_create_api_key():
    reg = client.post("/auth/register", json={"username": "keyuser", "password": "pass"})
    token = reg.json()["token"]
    r = client.post("/api-keys/", json={"name": "test-key"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert "key" in data
    assert data["key"].startswith("gw_")

def test_api_key_auth():
    reg = client.post("/auth/register", json={"username": "keyuser2", "password": "pass"})
    token = reg.json()["token"]
    r = client.post("/api-keys/", json={"name": "ci-key"},
                    headers={"Authorization": f"Bearer {token}"})
    api_key = r.json()["key"]
    # use X-API-Key instead of JWT
    r2 = client.get("/services/", headers={"X-API-Key": api_key})
    assert r2.status_code == 200

def test_revoke_api_key():
    reg = client.post("/auth/register", json={"username": "keyuser3", "password": "pass"})
    token = reg.json()["token"]
    r = client.post("/api-keys/", json={"name": "temp-key"},
                    headers={"Authorization": f"Bearer {token}"})
    key_id = r.json()["id"]
    api_key = r.json()["key"]
    # revoke
    client.delete(f"/api-keys/{key_id}", headers={"Authorization": f"Bearer {token}"})
    # should now be rejected
    r2 = client.get("/services/", headers={"X-API-Key": api_key})
    assert r2.status_code == 401

def test_invalid_api_key():
    r = client.get("/services/", headers={"X-API-Key": "gw_fakekeyvalue"})
    assert r.status_code == 401
