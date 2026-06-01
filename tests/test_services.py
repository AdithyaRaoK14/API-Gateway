from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def get_admin_token():
    r = client.post("/auth/register", json={"username": "admin", "password": "adminpass", "role": "admin"})
    return r.json()["token"]

def get_user_token():
    r = client.post("/auth/register", json={"username": "user1", "password": "userpass", "role": "user"})
    return r.json()["token"]

def test_list_services_empty():
    token = get_user_token()
    r = client.get("/services/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == []

def test_register_service_as_admin():
    token = get_admin_token()
    r = client.post("/services/", json={"name": "user-svc", "url": "http://user:8001", "prefix": "/users"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["service"] == "user-svc"

def test_register_service_as_user_forbidden():
    token = get_user_token()
    r = client.post("/services/", json={"name": "svc", "url": "http://svc:8001", "prefix": "/svc"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

def test_register_duplicate_service():
    token = get_admin_token()
    payload = {"name": "svc2", "url": "http://svc:8002", "prefix": "/svc2"}
    client.post("/services/", json=payload, headers={"Authorization": f"Bearer {token}"})
    r = client.post("/services/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400

def test_delete_service_as_admin():
    token = get_admin_token()
    client.post("/services/", json={"name": "del-svc", "url": "http://del:8003", "prefix": "/del"},
                headers={"Authorization": f"Bearer {token}"})
    r = client.delete("/services/del-svc", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

def test_delete_nonexistent_service():
    token = get_admin_token()
    r = client.delete("/services/ghost", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404

def test_list_services_after_register():
    token = get_admin_token()
    client.post("/services/", json={"name": "prod-svc", "url": "http://prod:8004", "prefix": "/products"},
                headers={"Authorization": f"Bearer {token}"})
    r = client.get("/services/", headers={"Authorization": f"Bearer {token}"})
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "prod-svc"

def test_delete_service_as_user_forbidden():
    admin_token = get_admin_token()
    client.post("/services/", json={"name": "target", "url": "http://t:9000", "prefix": "/target"},
                headers={"Authorization": f"Bearer {admin_token}"})
    user_token = get_user_token()
    r = client.delete("/services/target", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 403
