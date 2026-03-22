import pytest
from httpx import AsyncClient


class TestUpdateLink:

    @pytest.mark.asyncio
    async def test_update_success(self, client: AsyncClient):

        # только для зарегистрированных
        await client.post(
            "/auth/register", json={"email": "user@test.com", "password": "password"}
        )
        login = await client.post(
            "/auth/login", data={"username": "user@test.com", "password": "password"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://pipik.com"},
            headers=headers,
        )
        old_code = create.json()["short_url"].split("/")[-1]

        response = await client.put(
            f"/api/links/{old_code}",
            params={"new_short_code": "pipikpapik"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["new_code"] == "pipikpapik"

    @pytest.mark.asyncio
    async def test_update_unauthorized(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://papa.com"}
        )
        code = create.json()["short_url"].split("/")[-1]
        response = await client.put(
            f"/api/links/{code}", params={"new_short_code": "nucode"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_other_user_link(self, client: AsyncClient):
        await client.post(
            "/auth/register", json={"email": "lana@test.com", "password": "password"}
        )
        login_lana = await client.post(
            "/auth/login", data={"username": "lana@test.com", "password": "password"}
        )
        token_lana = login_lana.json()["access_token"]

        create = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://lana.com"},
            headers={"Authorization": f"Bearer {token_lana}"},
        )
        code = create.json()["short_url"].split("/")[-1]

        await client.post(
            "/auth/register", json={"email": "uruzmag@test.com", "password": "password"}
        )
        login_uruzmag = await client.post(
            "/auth/login", data={"username": "uruzmag@test.com", "password": "password"}
        )
        token_uruzmag = login_uruzmag.json()["access_token"]

        response = await client.put(
            f"/api/links/{code}",
            params={"new_short_code": "hacked"},
            headers={"Authorization": f"Bearer {token_uruzmag}"},
        )
        assert response.status_code == 403
