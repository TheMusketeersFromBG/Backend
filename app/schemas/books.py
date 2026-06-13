from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.books import BookStatus


class BookCreate(BaseModel):
    title: str
    author: str = ""
    pages: int = 0
    cover: str | None = None
    status: BookStatus = BookStatus.want
    genre: str = ""


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    pages: int | None = None
    pages_read: int | None = None
    cover: str | None = None
    status: BookStatus | None = None
    notes: str | None = None
    genre: str | None = None
    rating: int | None = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    pages: int
    pages_read: int
    cover: str | None
    status: BookStatus
    notes: str
    genre: str
    rating: int
    date_added: datetime
    date_finished: datetime | None


class ReadingGoalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    daily_goal: int


class ReadingProgressCreate(BaseModel):
    pages: int


class ReadingProgressOut(BaseModel):
    today_pages: int
