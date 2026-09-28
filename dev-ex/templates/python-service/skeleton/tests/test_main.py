from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello():
    resp = client.get("/hello")
    assert resp.status_code == 200
    assert resp.json() == "Hello from ${{ values.name }}"


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
