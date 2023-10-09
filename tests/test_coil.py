import pytest

from fastapi import Response

from conftest import client, async_session_maker

from src.coil.models import Coil


def test_coil_creation():
    data = {
        "length": 10,
        "weight": 10
    }
    response: Response = client.post("/api/coil", json=data)
    response_body = response.json()

    assert response.status_code == 201
    assert response_body["id"] == 1
