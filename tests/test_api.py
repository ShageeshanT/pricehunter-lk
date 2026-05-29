from fastapi.testclient import TestClient

from pricehunter.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_research_endpoint():
    response = client.post("/research", json={"items": [{"name": "Plaque", "quantity": 2}]})
    assert response.status_code == 200
    body = response.json()
    assert body["report"]["items"][0]["recommended"]["vendor"] == "AwardLab"
    assert body["report"]["grand_total"] == "5700"


def test_price_range_endpoint():
    response = client.post("/price-range", json={"item_name": "A4 file"})
    assert response.status_code == 200
    body = response.json()["result"]
    assert body["cheapest"]["site_name"]
    assert body["most_expensive"]["site_name"]
