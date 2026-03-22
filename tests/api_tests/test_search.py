import pytest
from httpx import AsyncClient


# Поиск ссылки
class TestSearchLinks:

    @pytest.mark.asyncio
    async def test_search_success(self, client: AsyncClient):
        create_response = await client.post(
            "/api/links/shorten", params={"original_url": "https://me.com"}
        )
        assert create_response.status_code == 200

        response = await client.get(
            "/api/links/search", params={"original_url": "https://me.com"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["short_code"] is not None
        assert data["original_url"] == "https://me.com"
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_search_not_found(self, client: AsyncClient):
        response = await client.get(
            "/api/links/search", params={"original_url": "https://ots.com"}
        )
        assert response.status_code == 404
        assert "URL не найден" in response.text

    @pytest.mark.asyncio
    async def test_search_empty_url(self, client: AsyncClient):
        response = await client.get("/api/links/search", params={"original_url": ""})
        assert response.status_code == 404
        assert "URL не найден" in response.text
