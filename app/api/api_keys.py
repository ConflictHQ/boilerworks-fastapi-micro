import hashlib
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_api_key
from app.database import get_db
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiResponse)
async def create_api_key(
    body: ApiKeyCreate,
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = ApiKey(
        name=body.name,
        key_hash=key_hash,
        scopes=body.scopes,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiResponse(
        ok=True,
        data=ApiKeyCreated(
            key=raw_key,
            api_key=ApiKeyOut.model_validate(api_key),
        ).model_dump(mode="json"),
    )


@router.get("", response_model=ApiResponse)
async def list_api_keys(
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(ApiKey).where(ApiKey.is_active.is_(True)).order_by(ApiKey.created_at.desc()))
    keys = result.scalars().all()
    return ApiResponse(
        ok=True,
        data=[ApiKeyOut.model_validate(k).model_dump(mode="json") for k in keys],
    )


@router.delete("/{key_id}", response_model=ApiResponse)
async def revoke_api_key(
    key_id: uuid.UUID,
    _caller: ApiKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    await db.commit()
    return ApiResponse(ok=True, data={"revoked": True})
