from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.nutrition import MealPlanEntry, NutritionGoal, Recipe, Supplement, SupplementLog, WaterLog
from app.models.user import User
from app.schemas.nutrition import (
    MealPlanOut,
    MealSlot,
    MealSlotUpdate,
    NutritionGoalsSchema,
    RecipeCreate,
    RecipeOut,
    SupplementCreate,
    SupplementOut,
    WaterOut,
)

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])


# ---- Water ----

async def _get_water_log(db: AsyncSession, user_id: int, day: date_type) -> WaterLog | None:
    return await db.scalar(select(WaterLog).where(WaterLog.user_id == user_id, WaterLog.date == day))


@router.get("/water/{day}", response_model=WaterOut)
async def get_water(
    day: date_type,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WaterOut:
    log = await _get_water_log(db, user.id, day)
    return WaterOut(date=day, glasses=log.glasses if log else 0)


@router.post("/water/{day}", response_model=WaterOut)
async def add_water(
    day: date_type,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WaterOut:
    log = await _get_water_log(db, user.id, day)
    if log is None:
        log = WaterLog(user_id=user.id, date=day, glasses=0)
        db.add(log)
    log.glasses += 1
    await db.commit()
    return WaterOut(date=day, glasses=log.glasses)


@router.delete("/water/{day}", response_model=WaterOut)
async def remove_water(
    day: date_type,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WaterOut:
    log = await _get_water_log(db, user.id, day)
    if log is None:
        log = WaterLog(user_id=user.id, date=day, glasses=0)
        db.add(log)
    log.glasses = max(0, log.glasses - 1)
    await db.commit()
    return WaterOut(date=day, glasses=log.glasses)


# ---- Supplements ----

async def _supplement_out(db: AsyncSession, supplement: Supplement, today: date_type) -> SupplementOut:
    log = await db.scalar(
        select(SupplementLog).where(SupplementLog.supplement_id == supplement.id, SupplementLog.date == today)
    )
    return SupplementOut(
        id=supplement.id,
        name=supplement.name,
        dose=supplement.dose,
        time=supplement.time,
        taken_today=bool(log and log.taken),
    )


@router.get("/supplements", response_model=list[SupplementOut])
async def list_supplements(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SupplementOut]:
    today = date_type.today()
    supplements = (await db.scalars(select(Supplement).where(Supplement.user_id == user.id))).all()
    return [await _supplement_out(db, s, today) for s in supplements]


@router.post("/supplements", response_model=SupplementOut, status_code=status.HTTP_201_CREATED)
async def add_supplement(
    payload: SupplementCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SupplementOut:
    supplement = Supplement(user_id=user.id, **payload.model_dump())
    db.add(supplement)
    await db.commit()
    await db.refresh(supplement)
    return await _supplement_out(db, supplement, date_type.today())


@router.delete("/supplements/{supplement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplement(
    supplement_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    supplement = await db.get(Supplement, supplement_id)
    if supplement is None or supplement.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Добавката не е намерена")
    await db.delete(supplement)
    await db.commit()


@router.post("/supplements/{supplement_id}/toggle", response_model=SupplementOut)
async def toggle_supplement(
    supplement_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SupplementOut:
    supplement = await db.get(Supplement, supplement_id)
    if supplement is None or supplement.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Добавката не е намерена")

    today = date_type.today()
    log = await db.scalar(
        select(SupplementLog).where(SupplementLog.supplement_id == supplement_id, SupplementLog.date == today)
    )
    if log is None:
        log = SupplementLog(supplement_id=supplement_id, date=today, taken=False)
        db.add(log)
    log.taken = not log.taken
    await db.commit()
    return await _supplement_out(db, supplement, today)


# ---- Nutrition goals ----

@router.get("/goals", response_model=NutritionGoalsSchema)
async def get_goals(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NutritionGoal:
    return await db.get(NutritionGoal, user.id)


@router.put("/goals", response_model=NutritionGoalsSchema)
async def set_goals(
    payload: NutritionGoalsSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NutritionGoal:
    goals = await db.get(NutritionGoal, user.id)
    goals.protein = payload.protein
    goals.carbs = payload.carbs
    goals.fat = payload.fat
    goals.water = payload.water
    await db.commit()
    return goals


# ---- Recipes ----

@router.get("/recipes", response_model=list[RecipeOut])
async def list_recipes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Recipe]:
    return (
        await db.scalars(select(Recipe).where((Recipe.user_id == user.id) | (Recipe.user_id.is_(None))))
    ).all()


@router.post("/recipes", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
async def add_recipe(
    payload: RecipeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Recipe:
    recipe = Recipe(user_id=user.id, **payload.model_dump())
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    recipe = await db.get(Recipe, recipe_id)
    if recipe is None or recipe.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Рецептата не е намерена")
    await db.delete(recipe)
    await db.commit()


# ---- Meal plan ----

@router.get("/meal-plan", response_model=MealPlanOut)
async def get_meal_plan(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MealPlanOut:
    entries = (await db.scalars(select(MealPlanEntry).where(MealPlanEntry.user_id == user.id))).all()
    return MealPlanOut(
        meal_plan={e.day: MealSlot(breakfast=e.breakfast, lunch=e.lunch, dinner=e.dinner) for e in entries}
    )


@router.put("/meal-plan/{day}", response_model=MealPlanOut)
async def update_meal_slot(
    day: str,
    payload: MealSlotUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MealPlanOut:
    if payload.slot not in {"breakfast", "lunch", "dinner"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Невалиден слот")

    entry = await db.scalar(
        select(MealPlanEntry).where(MealPlanEntry.user_id == user.id, MealPlanEntry.day == day)
    )
    if entry is None:
        entry = MealPlanEntry(user_id=user.id, day=day)
        db.add(entry)
    setattr(entry, payload.slot, payload.value)
    await db.commit()
    return await get_meal_plan(user, db)
