from datetime import date as date_type
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.books import ReadingProgress
from app.models.calories import FoodEntry
from app.models.progress import StepsGoal, StepsLog, WeightLog
from app.models.user import User
from app.models.workouts import Workout
from app.schemas.progress import (
    DayDataOut,
    StepsGoalSchema,
    StepsLogCreate,
    StreakOut,
    WeightEntryCreate,
    WeightEntryOut,
)

router = APIRouter(prefix="/api/progress", tags=["progress"])

DAY_LABELS_BG = ["Пон", "Вт", "Ср", "Чет", "Пет", "Съб", "Нед"]
STEPS_STREAK_THRESHOLD = 1000
MAX_STREAK_DAYS = 365


async def _day_data(db: AsyncSession, user_id: int, day: date_type) -> DayDataOut:
    calories = await db.scalar(
        select(func.coalesce(func.sum(FoodEntry.calories), 0)).where(
            FoodEntry.user_id == user_id, FoodEntry.date == day
        )
    )
    steps_log = await db.scalar(select(StepsLog).where(StepsLog.user_id == user_id, StepsLog.date == day))
    workouts = await db.scalar(
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == user_id, func.date(Workout.date) == day)
    )
    pages_log = await db.scalar(
        select(ReadingProgress).where(ReadingProgress.user_id == user_id, ReadingProgress.date == day)
    )
    return DayDataOut(
        date=day.isoformat(),
        label=DAY_LABELS_BG[day.weekday()],
        calories=int(calories or 0),
        steps=steps_log.steps if steps_log else 0,
        workouts=int(workouts or 0),
        pages=pages_log.pages_read if pages_log else 0,
    )


@router.get("/days", response_model=list[DayDataOut])
async def get_days(
    start: date_type = Query(...),
    end: date_type = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DayDataOut]:
    days = []
    day = start
    while day <= end:
        days.append(await _day_data(db, user.id, day))
        day += timedelta(days=1)
    return days


@router.post("/steps")
async def log_steps(
    payload: StepsLogCreate,
    day: date_type | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    day = day or date_type.today()
    log = await db.scalar(select(StepsLog).where(StepsLog.user_id == user.id, StepsLog.date == day))
    if log is None:
        log = StepsLog(user_id=user.id, date=day, steps=payload.steps)
        db.add(log)
    else:
        log.steps = payload.steps
    await db.commit()
    return {"date": day, "steps": log.steps}


@router.get("/steps-goal", response_model=StepsGoalSchema)
async def get_steps_goal(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StepsGoal:
    return await db.get(StepsGoal, user.id)


@router.put("/steps-goal", response_model=StepsGoalSchema)
async def set_steps_goal(
    payload: StepsGoalSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StepsGoal:
    goal = await db.get(StepsGoal, user.id)
    goal.goal = payload.goal
    await db.commit()
    return goal


@router.get("/weight", response_model=list[WeightEntryOut])
async def list_weight(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WeightLog]:
    return (
        await db.scalars(select(WeightLog).where(WeightLog.user_id == user.id).order_by(WeightLog.date))
    ).all()


@router.post("/weight", response_model=WeightEntryOut)
async def add_weight(
    payload: WeightEntryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WeightLog:
    today = date_type.today()
    entry = await db.scalar(select(WeightLog).where(WeightLog.user_id == user.id, WeightLog.date == today))
    if entry is None:
        entry = WeightLog(user_id=user.id, date=today, weight=payload.weight)
        db.add(entry)
    else:
        entry.weight = payload.weight
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/streak", response_model=StreakOut)
async def get_streak(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreakOut:
    streak = 0
    day = date_type.today()
    for _ in range(MAX_STREAK_DAYS + 1):
        has_workout = await db.scalar(
            select(func.count())
            .select_from(Workout)
            .where(Workout.user_id == user.id, func.date(Workout.date) == day)
        )
        steps_log = await db.scalar(select(StepsLog).where(StepsLog.user_id == user.id, StepsLog.date == day))
        has_steps = bool(steps_log and steps_log.steps > STEPS_STREAK_THRESHOLD)
        if not (has_workout or has_steps):
            break
        streak += 1
        day -= timedelta(days=1)
    return StreakOut(streak=streak)
