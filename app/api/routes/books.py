from datetime import date as date_type
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.books import Book, BookStatus, ReadingGoal, ReadingProgress
from app.models.user import User
from app.schemas.books import (
    BookCreate,
    BookOut,
    BookUpdate,
    ReadingGoalSchema,
    ReadingProgressCreate,
    ReadingProgressOut,
)

router = APIRouter(prefix="/api/books", tags=["books"])


async def _get_owned_book(db: AsyncSession, user_id: int, book_id: int) -> Book:
    book = await db.get(Book, book_id)
    if book is None or book.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книгата не е намерена")
    return book


@router.get("", response_model=list[BookOut])
async def list_books(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Book]:
    return (await db.scalars(select(Book).where(Book.user_id == user.id))).all()


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Book:
    book = Book(user_id=user.id, **payload.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookOut)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Book:
    book = await _get_owned_book(db, user.id, book_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    book = await _get_owned_book(db, user.id, book_id)
    await db.delete(book)
    await db.commit()


@router.post("/{book_id}/finish", response_model=BookOut)
async def finish_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Book:
    book = await _get_owned_book(db, user.id, book_id)
    book.status = BookStatus.finished
    book.pages_read = book.pages
    book.date_finished = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(book)
    return book


@router.get("/reading-goal", response_model=ReadingGoalSchema)
async def get_reading_goal(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReadingGoal:
    return await db.get(ReadingGoal, user.id)


@router.put("/reading-goal", response_model=ReadingGoalSchema)
async def set_reading_goal(
    payload: ReadingGoalSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReadingGoal:
    goal = await db.get(ReadingGoal, user.id)
    goal.daily_goal = payload.daily_goal
    await db.commit()
    return goal


@router.post("/reading-progress", response_model=ReadingProgressOut)
async def add_reading_progress(
    payload: ReadingProgressCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReadingProgressOut:
    today = date_type.today()
    progress = await db.scalar(
        select(ReadingProgress).where(ReadingProgress.user_id == user.id, ReadingProgress.date == today)
    )
    if progress is None:
        progress = ReadingProgress(user_id=user.id, date=today, pages_read=0)
        db.add(progress)
    progress.pages_read += payload.pages
    await db.commit()
    return ReadingProgressOut(today_pages=progress.pages_read)
