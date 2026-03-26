import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WebhookPayload(BaseModel):
    event: str = Field(..., min_length=1, max_length=255)
    source: str = Field(default="", max_length=255)
    data: dict[str, Any] = Field(default_factory=dict)


class WebhookEventOut(BaseModel):
    id: uuid.UUID
    event: str
    source: str
    payload: dict[str, Any]
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
