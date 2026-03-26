import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_api_key, require_scope
from app.database import get_db
from app.models.api_key import ApiKey
from app.models.webhook_event import WebhookEvent
from app.schemas.common import ApiResponse
from app.schemas.webhook import WebhookEventOut, WebhookPayload

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("", response_model=ApiResponse)
async def receive_webhook(
    body: WebhookPayload,
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    event = WebhookEvent(
        event=body.event,
        source=body.source,
        payload=body.data,
        status="received",
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return ApiResponse(
        ok=True,
        data=WebhookEventOut.model_validate(event).model_dump(mode="json"),
    )


@router.get("", response_model=ApiResponse)
async def list_webhook_events(
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(
        select(WebhookEvent)
        .where(WebhookEvent.deleted_at.is_(None))
        .order_by(WebhookEvent.created_at.desc())
        .limit(100)
    )
    events = result.scalars().all()
    return ApiResponse(
        ok=True,
        data=[WebhookEventOut.model_validate(e).model_dump(mode="json") for e in events],
    )


@router.get("/{event_id}", response_model=ApiResponse)
async def get_webhook_event(
    event_id: uuid.UUID,
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.id == event_id, WebhookEvent.deleted_at.is_(None))
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Webhook event not found")

    return ApiResponse(
        ok=True,
        data=WebhookEventOut.model_validate(event).model_dump(mode="json"),
    )


@router.delete("/{event_id}", response_model=ApiResponse, dependencies=[require_scope("webhooks.delete")])
async def delete_webhook_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.id == event_id, WebhookEvent.deleted_at.is_(None))
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Webhook event not found")

    event.deleted_at = func.now()
    await db.commit()
    return ApiResponse(ok=True, data={"deleted": True})
