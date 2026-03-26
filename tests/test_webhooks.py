import uuid

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_event import WebhookEvent


async def test_receive_webhook(client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession) -> None:
    response = await client.post(
        "/webhooks",
        json={"event": "order.created", "source": "shopify", "data": {"id": "123", "total": 99.99}},
        headers=api_key_header,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["event"] == "order.created"
    assert body["data"]["source"] == "shopify"
    assert body["data"]["status"] == "received"

    result = await db.execute(select(WebhookEvent).where(WebhookEvent.event == "order.created"))
    event = result.scalar_one()
    assert event.payload == {"id": "123", "total": 99.99}
    assert event.status == "received"


async def test_receive_webhook_no_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/webhooks",
        json={"event": "order.created", "data": {"id": "123"}},
    )
    assert response.status_code == 401


async def test_receive_webhook_invalid_key(client: AsyncClient) -> None:
    response = await client.post(
        "/webhooks",
        json={"event": "order.created", "data": {"id": "123"}},
        headers={"X-API-Key": "bad-key"},
    )
    assert response.status_code == 401


async def test_list_webhook_events(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    await client.post(
        "/webhooks",
        json={"event": "user.signup", "data": {"email": "test@example.com"}},
        headers=api_key_header,
    )
    response = await client.get("/webhooks", headers=api_key_header)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert len(body["data"]) >= 1
    assert body["data"][0]["event"] == "user.signup"


async def test_list_webhook_events_no_auth(client: AsyncClient) -> None:
    response = await client.get("/webhooks")
    assert response.status_code == 401


async def test_get_webhook_event(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    create_resp = await client.post(
        "/webhooks",
        json={"event": "payment.completed", "data": {"amount": 50}},
        headers=api_key_header,
    )
    event_id = create_resp.json()["data"]["id"]

    response = await client.get(f"/webhooks/{event_id}", headers=api_key_header)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["event"] == "payment.completed"


async def test_get_webhook_event_not_found(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    response = await client.get(f"/webhooks/{uuid.uuid4()}", headers=api_key_header)
    assert response.status_code == 404


async def test_get_webhook_event_no_auth(client: AsyncClient) -> None:
    response = await client.get(f"/webhooks/{uuid.uuid4()}")
    assert response.status_code == 401


async def test_delete_webhook_event(client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession) -> None:
    create_resp = await client.post(
        "/webhooks",
        json={"event": "to.delete", "data": {}},
        headers=api_key_header,
    )
    event_id = create_resp.json()["data"]["id"]

    response = await client.delete(f"/webhooks/{event_id}", headers=api_key_header)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    result = await db.execute(select(WebhookEvent).where(WebhookEvent.id == event_id))
    event = result.scalar_one()
    assert event.deleted_at is not None


async def test_delete_webhook_event_not_found(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    response = await client.delete(f"/webhooks/{uuid.uuid4()}", headers=api_key_header)
    assert response.status_code == 404


async def test_delete_webhook_event_no_auth(client: AsyncClient) -> None:
    response = await client.delete(f"/webhooks/{uuid.uuid4()}")
    assert response.status_code == 401


async def test_delete_webhook_event_missing_scope(client: AsyncClient, limited_api_key_header: dict[str, str]) -> None:
    response = await client.delete(f"/webhooks/{uuid.uuid4()}", headers=limited_api_key_header)
    assert response.status_code == 403
    assert "Missing scope" in response.json()["detail"]
