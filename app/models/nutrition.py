from datetime import date as date_

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WaterLog(Base):
    __tablename__ = "water_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_water_log_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    glasses: Mapped[int] = mapped_column(Integer, default=0)


class Supplement(Base):
    __tablename__ = "supplements"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    dose: Mapped[str] = mapped_column(String(64), default="")
    time: Mapped[str] = mapped_column(String(16), default="")


class SupplementLog(Base):
    __tablename__ = "supplement_logs"
    __table_args__ = (UniqueConstraint("supplement_id", "date", name="uq_supplement_log_supplement_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    supplement_id: Mapped[int] = mapped_column(ForeignKey("supplements.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    taken: Mapped[bool] = mapped_column(Boolean, default=False)


class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    protein: Mapped[int] = mapped_column(Integer, default=150)
    carbs: Mapped[int] = mapped_column(Integer, default=250)
    fat: Mapped[int] = mapped_column(Integer, default=70)
    water: Mapped[int] = mapped_column(Integer, default=8)


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, default=None)
    name: Mapped[str] = mapped_column(String(255))
    calories: Mapped[int] = mapped_column(Integer, default=0)
    protein: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    fat: Mapped[float] = mapped_column(Float, default=0)
    prep_time: Mapped[str] = mapped_column(String(32), default="")
    description: Mapped[str] = mapped_column(Text, default="")


class MealPlanEntry(Base):
    __tablename__ = "meal_plan_entries"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_meal_plan_user_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[str] = mapped_column(String(16))
    breakfast: Mapped[str] = mapped_column(String(255), default="")
    lunch: Mapped[str] = mapped_column(String(255), default="")
    dinner: Mapped[str] = mapped_column(String(255), default="")
