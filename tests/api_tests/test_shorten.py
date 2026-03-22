import pytest
from httpx import AsyncClient


# Создание короткой ссылки
class TestCreateLink:

    @pytest.mark.asyncio
    async def test_create_success(self, client: AsyncClient):
        response = await client.post(
            "/api/links/shorten", params={"original_url": "https://pupupup.com"}
        )
        assert response.status_code == 200
        data = response.json()

        assert "short_url" in data
        assert data["original_url"] == "https://pupupup.com"
        assert data["owner_id"] is None

    @pytest.mark.asyncio
    async def test_create_with_custom_alias(self, client: AsyncClient):
        response = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://popug.com", "custom_alias": "moypopug"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "moypopug" in data["short_url"]
        assert data["custom_alias"] == "moypopug"

    @pytest.mark.asyncio
    async def test_create_duplicate_alias(self, client: AsyncClient):
        # Делаем одинаковые
        await client.post(
            "/api/links/shorten",
            params={"original_url": "https://babuba.com", "custom_alias": "mrdenmark"},
        )

        response = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://bububu.com", "custom_alias": "mrdenmark"},
        )
        assert response.status_code == 400
        assert "Алиас 'mrdenmark' уже занят" in response.text

    @pytest.mark.asyncio
    async def test_create_alias_invalid_chars(self, client: AsyncClient):
        response = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://ivan.com", "custom_alias": "durak!"},
        )
        assert response.status_code == 400
        assert "Алиас должен содержать только буквы и цифры" in response.text

    @pytest.mark.asyncio
    async def test_create_empty_url(self, client: AsyncClient):
        response = await client.post("/api/links/shorten", params={"original_url": ""})
        assert response.status_code == 400
        assert "URL обязателен" in response.text

    @pytest.mark.asyncio
    async def test_create_with_expires(self, client: AsyncClient):
        response = await client.post(
            "/api/links/shorten",
            params={
                "original_url": "https://nerano.com",
                "expires_at": "2026-12-31T23:59:59",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "2026-12-31T23:59:59" in data["expires_at"]

    @pytest.mark.asyncio
    async def test_create_expired_date(self, client: AsyncClient):
        response = await client.post(
            "/api/links/shorten",
            params={
                "original_url": "https://rano.com",
                "expires_at": "2020-01-01T00:00:00",
            },
        )
        assert response.status_code == 400
        assert "expires_at не может быть в прошлом" in response.text
