from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    duration: Mapped[int] = mapped_column(Integer, default=0)
    exercises: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    calories_burned: Mapped[int] = mapped_column(Integer, default=0)


class WorkoutPlanDay(Base):
    __tablename__ = "workout_plan_days"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_workout_plan_user_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[str] = mapped_column(String(8))
    name: Mapped[str] = mapped_column(String(255), default="")
    exercises: Mapped[list[str]] = mapped_column(JSONB, default=list)
