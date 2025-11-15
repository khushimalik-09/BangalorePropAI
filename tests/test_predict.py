from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_metadata():
    r = client.get("/api/metadata")
    assert r.status_code == 200
    assert "locations" in r.json()

def test_predict_invalid():
    r = client.post("/api/predict", json={"total_sqft":-1,"bhk":2,"bath":2,"location":"hsr layout"})
    assert r.status_code == 422 or r.status_code == 400
