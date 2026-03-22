import pytest
from httpx import AsyncClient


# редирект
class TestRedirect:

    @pytest.mark.asyncio
    async def test_redirect_success(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://pupupupu.com"}
        )
        assert create.status_code == 200
        short_code = create.json()["short_url"].split("/")[-1]

        print(short_code)

        response = await client.get(f"/api/links/{short_code}", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert response.headers["location"] == "https://pupupupu.com"

    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client: AsyncClient):
        response = await client.get("/api/links/nonexist")
        assert response.status_code == 404
        assert "Ссылка не найдена" in response.text

    @pytest.mark.asyncio
    async def test_redirect_increments_clicks(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://theklik.com"}
        )
        short_code = create.json()["short_url"].split("/")[-1]

        stats = await client.get(f"/api/links/{short_code}/stats")
        assert stats.json()["clicks"] == 0

        await client.get(f"/api/links/{short_code}", follow_redirects=False)

        stats_after = await client.get(f"/api/links/{short_code}/stats")
        assert stats_after.json()["clicks"] == 1

    @pytest.mark.asyncio
    async def test_redirect_updates_last_used(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://hehehe.com"}
        )
        short_code = create.json()["short_url"].split("/")[-1]

        stats = await client.get(f"/api/links/{short_code}/stats")
        assert stats.json()["last_used"] is None

        await client.get(f"/api/links/{short_code}", follow_redirects=False)

        stats_after = await client.get(f"/api/links/{short_code}/stats")
        assert stats_after.json()["last_used"] is not None

    @pytest.mark.asyncio
    async def test_redirect_multiple_times(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://hihihi.com"}
        )
        short_code = create.json()["short_url"].split("/")[-1]

        for _ in range(3):
            await client.get(f"/api/links/{short_code}", follow_redirects=False)

        stats = await client.get(f"/api/links/{short_code}/stats")
        assert stats.json()["clicks"] == 3
