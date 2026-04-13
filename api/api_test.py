from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_pred_high_status():
    response = client.get("/pred_high")
    assert response.status_code == 200


def test_pred_high_fields():
    response = client.get("/pred_high")
    data = response.json()
    assert "based_on_date" in data
    assert "last_close" in data
    assert "high_perc" in data
    assert "predicted_high" in data


