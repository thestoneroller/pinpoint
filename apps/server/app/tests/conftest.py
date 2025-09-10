from typing import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as client:
            yield client
