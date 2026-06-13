from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Onboarding(Base):
    __tablename__ = "onboarding"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    goal: Mapped[str] = mapped_column(String(32), default="")
    activity: Mapped[str] = mapped_column(String(32), default="")
    diet: Mapped[str] = mapped_column(String(32), default="")
    target_weight: Mapped[str] = mapped_column(String(16), default="")
    reading_frequency: Mapped[str] = mapped_column(String(32), default="")
    plan: Mapped[str] = mapped_column(String(8), default="free")
    sports: Mapped[list[str]] = mapped_column(JSONB, default=list)
    allergies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    reading_genres: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
