from datetime import date

from sqlalchemy import Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProfileMetrics(Base):
    __tablename__ = "profile_metrics"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    height: Mapped[float | None] = mapped_column(Float, default=None)
    weight: Mapped[float | None] = mapped_column(Float, default=None)
    chest: Mapped[float | None] = mapped_column(Float, default=None)
    waist: Mapped[float | None] = mapped_column(Float, default=None)
    hips: Mapped[float | None] = mapped_column(Float, default=None)
    shoulders: Mapped[float | None] = mapped_column(Float, default=None)
    bicep: Mapped[float | None] = mapped_column(Float, default=None)
    thigh: Mapped[float | None] = mapped_column(Float, default=None)
    birthdate: Mapped[date | None] = mapped_column(Date, default=None)
