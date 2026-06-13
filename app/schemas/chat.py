from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.chat import ChatSender


class ChatMessageCreate(BaseModel):
    text: str


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: ChatSender
    text: str
    created_at: datetime
