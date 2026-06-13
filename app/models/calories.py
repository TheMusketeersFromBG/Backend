from datetime import date as date_

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    name: Mapped[str] = mapped_column(String(255))
    calories: Mapped[int] = mapped_column(Integer, default=0)
    protein: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    fat: Mapped[float] = mapped_column(Float, default=0)
    time: Mapped[str] = mapped_column(String(16), default="")
    photo: Mapped[str | None] = mapped_column(String, default=None)


class CalorieGoal(Base):
    __tablename__ = "calorie_goals"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_calorie_goal_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    goal: Mapped[int] = mapped_column(Integer, default=2000)
