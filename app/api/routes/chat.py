from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.chat import ChatMessage, ChatSender
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatMessageOut

router = APIRouter(prefix="/api/chat", tags=["chat"])

MOCK_RESPONSES = [
    "Звучи добре! Продължавай в този дух.",
    "Запомних това. Има ли друго, с което да помогна?",
    "Добра работа! Не забравяй да следиш прогреса си редовно.",
    "Разбрах. Ще се радвам да чуя как се справяш по-късно.",
]


@router.get("/messages", response_model=list[ChatMessageOut])
async def list_messages(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatMessage]:
    return (
        await db.scalars(
            select(ChatMessage).where(ChatMessage.user_id == user.id).order_by(ChatMessage.created_at)
        )
    ).all()


@router.post("/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessage:
    user_message = ChatMessage(user_id=user.id, sender=ChatSender.user, text=payload.text)
    db.add(user_message)

    ai_total = len(
        (
            await db.scalars(
                select(ChatMessage.id).where(
                    ChatMessage.user_id == user.id, ChatMessage.sender == ChatSender.ai
                )
            )
        ).all()
    )
    reply_text = MOCK_RESPONSES[ai_total % len(MOCK_RESPONSES)]

    ai_message = ChatMessage(user_id=user.id, sender=ChatSender.ai, text=reply_text)
    db.add(ai_message)

    await db.commit()
    await db.refresh(ai_message)
    return ai_message
