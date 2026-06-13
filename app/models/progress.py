from datetime import date as date_

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StepsLog(Base):
    __tablename__ = "steps_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_steps_log_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    steps: Mapped[int] = mapped_column(Integer, default=0)


class StepsGoal(Base):
    __tablename__ = "steps_goals"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    goal: Mapped[int] = mapped_column(Integer, default=10000)


class WeightLog(Base):
    __tablename__ = "weight_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_weight_log_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    weight: Mapped[float] = mapped_column(Float)
