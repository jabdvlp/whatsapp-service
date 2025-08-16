from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text
from datetime import datetime
import uuid
from .db import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wa_message_id: Mapped[str | None] = mapped_column(String(64))
    wa_from: Mapped[str | None] = mapped_column(String(32))
    wa_to: Mapped[str | None] = mapped_column(String(32))
    wa_type: Mapped[str | None] = mapped_column(String(16))
    direction: Mapped[str] = mapped_column(String(8), default="inbound")
    text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
