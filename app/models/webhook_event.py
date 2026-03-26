from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditBase, SoftDeleteMixin


class WebhookEvent(AuditBase, SoftDeleteMixin):
    __tablename__ = "webhook_events"

    event: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(255), default="")
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="received")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
