from datetime import date as date_type
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.calories import CalorieGoal, FoodEntry
from app.models.user import User
from app.schemas.calories import CaloriesDayOut, FoodEntryCreate, FoodEntryOut, GoalUpdate

router = APIRouter(prefix="/api/calories", tags=["calories"])

DEFAULT_GOAL = 2000


async def _get_or_create_goal(db: AsyncSession, user_id: int, day: date_type) -> CalorieGoal:
    goal = await db.scalar(
        select(CalorieGoal).where(CalorieGoal.user_id == user_id, CalorieGoal.date == day)
    )
    if goal is None:
        goal = CalorieGoal(user_id=user_id, date=day, goal=DEFAULT_GOAL)
        db.add(goal)
        await db.flush()
    return goal


async def _day_out(db: AsyncSession, user_id: int, day: date_type) -> CaloriesDayOut:
    goal = await _get_or_create_goal(db, user_id, day)
    entries = (
        await db.scalars(select(FoodEntry).where(FoodEntry.user_id == user_id, FoodEntry.date == day))
    ).all()
    return CaloriesDayOut(
        date=day,
        goal=goal.goal,
        entries=[FoodEntryOut.model_validate(e) for e in entries],
        total_calories=sum(e.calories for e in entries),
        total_protein=sum(e.protein for e in entries),
        total_carbs=sum(e.carbs for e in entries),
        total_fat=sum(e.fat for e in entries),
    )


@router.get("/{day}", response_model=CaloriesDayOut)
async def get_day(
    day: date_type,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CaloriesDayOut:
    result = await _day_out(db, user.id, day)
    await db.commit()
    return result


@router.post("/{day}/entries", response_model=FoodEntryOut, status_code=status.HTTP_201_CREATED)
async def add_entry(
    day: date_type,
    payload: FoodEntryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FoodEntry:
    entry = FoodEntry(
        user_id=user.id,
        date=day,
        time=datetime.now().strftime("%H:%M"),
        **payload.model_dump(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    entry = await db.get(FoodEntry, entry_id)
    if entry is None or entry.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Записът не е намерен")
    await db.delete(entry)
    await db.commit()


@router.put("/{day}/goal", response_model=CaloriesDayOut)
async def set_goal(
    day: date_type,
    payload: GoalUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CaloriesDayOut:
    goal = await _get_or_create_goal(db, user.id, day)
    goal.goal = payload.goal
    result = await _day_out(db, user.id, day)
    await db.commit()
    return result
