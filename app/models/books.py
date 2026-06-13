import enum
from datetime import date as date_
from datetime import datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BookStatus(str, enum.Enum):
    reading = "reading"
    want = "want"
    finished = "finished"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255), default="")
    pages: Mapped[int] = mapped_column(Integer, default=0)
    pages_read: Mapped[int] = mapped_column(Integer, default=0)
    cover: Mapped[str | None] = mapped_column(String, default=None)
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus, name="book_status"), default=BookStatus.want)
    notes: Mapped[str] = mapped_column(Text, default="")
    genre: Mapped[str] = mapped_column(String(64), default="")
    rating: Mapped[int] = mapped_column(Integer, default=0)
    date_added: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_finished: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


class ReadingProgress(Base):
    __tablename__ = "reading_progress"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_reading_progress_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date_] = mapped_column(Date, index=True)
    pages_read: Mapped[int] = mapped_column(Integer, default=0)


class ReadingGoal(Base):
    __tablename__ = "reading_goals"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    daily_goal: Mapped[int] = mapped_column(Integer, default=20)
