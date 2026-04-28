import json
from fastapi import status
#from fastapi.testclient import ClientTest
from tests.database import client, db_session, engine


def test_category_create(client):
    payload = json.dumps(dict(name="First Category", active=True))
    response = client.post("/categories/", json=payload)
    outcome = response.json()
    assert response.status_code == status.HTTP_200_OK
