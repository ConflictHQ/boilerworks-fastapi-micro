import hashlib

from fastapi import Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.api_key import ApiKey


async def require_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    key = request.headers.get("X-API-Key")
    if not key:
        raise HTTPException(status_code=401, detail="API key required")

    key_hash = hashlib.sha256(key.encode()).hexdigest()
    result = await db.execute(select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True)))
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    api_key.last_used_at = func.now()
    await db.commit()
    return api_key


def require_scope(scope: str):
    async def dependency(api_key: ApiKey = Depends(require_api_key)) -> ApiKey:
        if scope not in api_key.scopes and "*" not in api_key.scopes:
            raise HTTPException(status_code=403, detail=f"Missing scope: {scope}")
        return api_key

    return Depends(dependency)
