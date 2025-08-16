from pydantic import BaseModel
from datetime import datetime

class MessageOut(BaseModel):
    id: str
    wa_message_id: str | None
    wa_from: str | None
    wa_to: str | None
    wa_type: str | None
    direction: str
    text: str | None
    created_at: datetime

    class Config:
        from_attributes = True
