
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    outcome = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "msg" in outcome
    assert outcome.get("msg") == "App Library API Interface"

