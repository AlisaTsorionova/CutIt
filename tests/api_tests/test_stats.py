import pytest
from httpx import AsyncClient


# редирект
class TestLinkStats:

    @pytest.mark.asyncio
    async def test_stats_success(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://statsis.com"}
        )
        assert create.status_code == 200
        short_code = create.json()["short_url"].split("/")[-1]

        response = await client.get(f"/api/links/{short_code}/stats")
        assert response.status_code == 200
        data = response.json()

        assert data["original_url"] == "https://statsis.com"
        assert data["short_code"] == short_code
        assert data["clicks"] == 0
        assert data["created_at"] is not None
        assert data["last_used"] is None
        assert data["expires_at"] is None

    @pytest.mark.asyncio
    async def test_stats_not_found(self, client: AsyncClient):
        response = await client.get("/api/links/bebebesbababa/stats")

        assert response.status_code == 404
        assert "Ссылка не найдена" in response.text

    @pytest.mark.asyncio
    async def test_stats_with_expires(self, client: AsyncClient):
        future_date = "2026-12-31T23:59:59"
        create = await client.post(
            "/api/links/shorten",
            params={
                "original_url": "https://tete.com",
                "expires_at": future_date,
            },
        )
        short_code = create.json()["short_url"].split("/")[-1]

        response = await client.get(f"/api/links/{short_code}/stats")
        assert response.status_code == 200
        data = response.json()

        assert data["expires_at"] is not None
        assert data["expires_at"].startswith("2026-12-31")

    @pytest.mark.asyncio
    async def test_stats_multiple_redirects(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://clicks.com"}
        )
        short_code = create.json()["short_url"].split("/")[-1]

        for _ in range(5):
            await client.get(f"/api/links/{short_code}", follow_redirects=False)

        response = await client.get(f"/api/links/{short_code}/stats")
        assert response.json()["clicks"] == 5
