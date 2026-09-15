from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_order_requires_items():
    response = client.post("/orders", json={"customer_id": 1, "items": []})
    assert response.status_code == 400
