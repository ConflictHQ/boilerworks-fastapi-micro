from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> ApiResponse:
    await db.execute(text("SELECT 1"))
    return ApiResponse(ok=True, data={"status": "healthy"})
