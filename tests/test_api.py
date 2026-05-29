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
