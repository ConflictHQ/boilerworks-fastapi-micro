import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: list[str] = Field(default_factory=lambda: ["*"])


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    name: str
    scopes: list[str]
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyCreated(BaseModel):
    key: str
    api_key: ApiKeyOut
