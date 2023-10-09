from datetime import date

import pytest
from contextlib import nullcontext as does_not_raise

from fastapi import Response
from httpx import AsyncClient

from sqlalchemy import insert, text

from conftest import client, async_session_maker

from src.coil.models import Coil


@pytest.fixture
async def clear_coils_table():
    async with async_session_maker() as session:
        query = text(f"TRUNCATE TABLE {Coil.__tablename__} RESTART IDENTITY;")
        await session.execute(query)
        await session.commit()
        
        
@pytest.fixture
async def create_coils():
    async with async_session_maker() as session:
        coils = [{"length": 10, "weight": 100}, {"length": 5, "weight": 50}, {"length": 100, "weight": 1000}]
        query = insert(Coil).values(coils)
        await session.execute(query)
        await session.commit()


@pytest.mark.parametrize(
    "data, result_id",
    [
        ({"length": 10, "weight": 10}, 1),
        ({"length": 100, "weight": 100}, 1),
        ({"length": 50, "weight": 30}, 1),
    ]
)
async def test_coil_creation(data, result_id, async_client: AsyncClient, clear_coils_table):
    response: Response = await async_client.post("/api/coil", json=data)
    response_body = response.json()

    assert response.status_code == 201
    assert response_body["id"] == result_id


@pytest.mark.parametrize(
    "data",
    [
        ({"length": 0, "weight": 0}),
        ({"length": -1, "weight": 100}),
        ({"length": 50, "weight": 0}),
    ]
)
async def test_coil_creation_with_wrong_params(data, async_client: AsyncClient):
    response: Response = await async_client.post("/api/coil", json=data)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "id, status_code",
    [
        (1, 204),
        (2, 204),
        (-1, 404),
    ]
)
async def test_coil_deletion(id, status_code, async_client: AsyncClient, clear_coils_table, create_coils):
    response: Response = await async_client.delete(f"/api/coil/{id}")
    
    assert response.status_code == status_code


async def test_repetitive_coil_deletion(async_client: AsyncClient, clear_coils_table, create_coils):
    id = 1
    
    response: Response = await async_client.delete(f"/api/coil/{id}")
    assert response.status_code == 204
    
    response: Response = await async_client.delete(f"/api/coil/{id}")
    assert response.status_code == 404
    
    
@pytest.mark.parametrize(
    "id, status_code",
    [
        (1, 204),
        (2, 204),
        (-1, 404),
    ]
)
async def test_coil_deletion(id, status_code, async_client: AsyncClient, clear_coils_table, create_coils):
    response: Response = await async_client.delete(f"/api/coil/{id}")
    
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "query_params, expected_status_code, expected_amount",
    [
        ({"from_id": 1, "to_id": 3}, 200, 3),
        ({"from_id": 100, "to_id": 500}, 200, 0),
        ({"from_weight": 50, "to_weight": 100}, 200, 2),
        ({"from_id": 1}, 422, None),
        ({"to_id": 2}, 422, None),
        ({}, 422, None),
    ]
)
async def test_get_coil(query_params, expected_status_code, expected_amount, async_client: AsyncClient, clear_coils_table, create_coils):
    query_params = '&'.join(f"{key}={value}" for key, value in query_params.items())
    response: Response = await async_client.get(f"/api/coil?{query_params}")
    
    assert response.status_code == expected_status_code
    
    if isinstance(expected_amount, int):
        response_data = response.json()
        assert len(response_data) == expected_amount


@pytest.mark.parametrize(
    "from_date, to_date, expected_status_code, expected_values",
    [
        ("2023-01-01", "2023-12-31", 200, {
            "amount": 3,
            "deleted_amount": 0,
            "average_length": 38.33,
            "average_weight": 383.33,
            "max_length": 100,
            "min_length": 5,
            "max_weight": 1000,
            "min_weight": 50,
            "total_weight": 1150,
        }),
        ("2000-01-01", "2000-12-31", 404, None),
    ]
)        
async def test_get_coil_stats(from_date, to_date, expected_status_code, expected_values, async_client: AsyncClient, clear_coils_table, create_coils):
    response: Response = await async_client.get(f"/api/coil/stats?from_date={from_date}&to_date={to_date}")
    assert response.status_code == expected_status_code
    
    if expected_values:
        response_data = response.json()
        
        for key, value in expected_values.items():
            assert response_data[key] == value
