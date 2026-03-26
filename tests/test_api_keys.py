from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey


async def test_create_api_key(client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession) -> None:
    response = await client.post(
        "/api-keys",
        json={"name": "new-key", "scopes": ["webhooks.read"]},
        headers=api_key_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert "key" in body["data"]
    assert body["data"]["api_key"]["name"] == "new-key"
    assert body["data"]["api_key"]["scopes"] == ["webhooks.read"]

    result = await db.execute(select(ApiKey).where(ApiKey.name == "new-key"))
    created = result.scalar_one()
    assert created.is_active is True
    assert created.scopes == ["webhooks.read"]


async def test_create_api_key_no_auth(client: AsyncClient) -> None:
    response = await client.post("/api-keys", json={"name": "no-auth-key"})
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "API key required"


async def test_create_api_key_invalid_key(client: AsyncClient) -> None:
    response = await client.post(
        "/api-keys",
        json={"name": "bad-key"},
        headers={"X-API-Key": "nonexistent-key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


async def test_list_api_keys(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    response = await client.get("/api-keys", headers=api_key_header)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1


async def test_list_api_keys_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api-keys")
    assert response.status_code == 401


async def test_revoke_api_key(client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession) -> None:
    create_resp = await client.post(
        "/api-keys",
        json={"name": "to-revoke"},
        headers=api_key_header,
    )
    key_id = create_resp.json()["data"]["api_key"]["id"]

    response = await client.delete(f"/api-keys/{key_id}", headers=api_key_header)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    revoked = result.scalar_one()
    assert revoked.is_active is False


async def test_revoke_api_key_not_found(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    import uuid

    response = await client.delete(f"/api-keys/{uuid.uuid4()}", headers=api_key_header)
    assert response.status_code == 404


async def test_revoke_api_key_no_auth(client: AsyncClient) -> None:
    import uuid

    response = await client.delete(f"/api-keys/{uuid.uuid4()}")
    assert response.status_code == 401
