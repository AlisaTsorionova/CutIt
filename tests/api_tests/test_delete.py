import pytest
from httpx import AsyncClient


class TestDeleteLink:

    @pytest.mark.asyncio
    async def test_delete_success(self, client: AsyncClient):
        await client.post(
            "/auth/register", json={"email": "del@test.com", "password": "password"}
        )
        login = await client.post(
            "/auth/login", data={"username": "del@test.com", "password": "password"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://delete.ty"},
            headers=headers,
        )
        code = create.json()["short_url"].split("/")[-1]

        response = await client.delete(f"/api/links/{code}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Ссылка удалена"

        check = await client.get(f"/api/links/{code}")
        assert check.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_unauthorized(self, client: AsyncClient):
        create = await client.post(
            "/api/links/shorten", params={"original_url": "https://ssul.com"}
        )
        code = create.json()["short_url"].split("/")[-1]

        response = await client.delete(f"/api/links/{code}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient):
        await client.post(
            "/auth/register", json={"email": "net@test.com", "password": "password"}
        )
        login = await client.post(
            "/auth/login", data={"username": "net@test.com", "password": "password"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.delete("/api/links/nonexist", headers=headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_other_user_link(self, client: AsyncClient):
        await client.post(
            "/auth/register", json={"email": "vitaly@test.com", "password": "password"}
        )
        login_vitaly = await client.post(
            "/auth/login", data={"username": "vitaly@test.com", "password": "password"}
        )
        token_vitaly = login_vitaly.json()["access_token"]

        create = await client.post(
            "/api/links/shorten",
            params={"original_url": "https://vitaly.com"},
            headers={"Authorization": f"Bearer {token_vitaly}"},
        )
        code = create.json()["short_url"].split("/")[-1]

        await client.post(
            "/auth/register", json={"email": "zarina@test.com", "password": "password"}
        )
        login_zarina = await client.post(
            "/auth/login", data={"username": "zarina@test.com", "password": "password"}
        )
        token_zarina = login_zarina.json()["access_token"]

        response = await client.delete(
            f"/api/links/{code}", headers={"Authorization": f"Bearer {token_zarina}"}
        )
        assert response.status_code == 403
        assert "Операция недоступна" in response.text
