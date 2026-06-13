from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.workouts import Workout, WorkoutPlanDay
from app.schemas.workouts import PlanDaySchema, PlanOut, PlanUpdate, WorkoutCreate, WorkoutOut

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


@router.get("", response_model=list[WorkoutOut])
async def list_workouts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Workout]:
    return (
        await db.scalars(select(Workout).where(Workout.user_id == user.id).order_by(Workout.date.desc()))
    ).all()


@router.post("", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
async def create_workout(
    payload: WorkoutCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Workout:
    data = payload.model_dump()
    workout = Workout(
        user_id=user.id,
        name=data["name"],
        date=data["date"] or datetime.now(timezone.utc),
        duration=data["duration"],
        exercises=data["exercises"],
        calories_burned=data["calories_burned"],
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    workout = await db.get(Workout, workout_id)
    if workout is None or workout.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировката не е намерена")
    await db.delete(workout)
    await db.commit()


@router.get("/plan", response_model=PlanOut)
async def get_plan(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanOut:
    days = (await db.scalars(select(WorkoutPlanDay).where(WorkoutPlanDay.user_id == user.id))).all()
    return PlanOut(plan={d.day: PlanDaySchema(name=d.name, exercises=d.exercises) for d in days})


@router.put("/plan", response_model=PlanOut)
async def save_plan(
    payload: PlanUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanOut:
    existing = {
        d.day: d for d in (await db.scalars(select(WorkoutPlanDay).where(WorkoutPlanDay.user_id == user.id))).all()
    }
    for day, plan_day in payload.plan.items():
        if day in existing:
            existing[day].name = plan_day.name
            existing[day].exercises = plan_day.exercises
        else:
            db.add(WorkoutPlanDay(user_id=user.id, day=day, name=plan_day.name, exercises=plan_day.exercises))
    await db.commit()
    return await get_plan(user, db)
