"""Seeds default goals from onboarding answers.

Mirrors the frontend's initFromOnboarding (hooks/useOnboardingInit.ts): goals are
only overwritten while they still hold their original defaults, so a user's own
edits are never clobbered by re-running onboarding.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.books import ReadingGoal
from app.models.calories import CalorieGoal
from app.models.nutrition import NutritionGoal
from app.models.onboarding import Onboarding

DEFAULT_CALORIE_GOAL = 2000
DEFAULT_NUTRITION_GOALS = {"protein": 150, "carbs": 250, "fat": 70, "water": 8}
DEFAULT_READING_GOAL = 20


def _calc_calorie_goal(goal: str, activity: str) -> int:
    base = 2000
    if goal == "lose":
        base -= 300
    if goal == "gain":
        base += 400
    if activity == "sedentary":
        base -= 200
    if activity == "moderate":
        base += 200
    if activity == "very":
        base += 500
    return round(base / 50) * 50


def _calc_water_goal(activity: str) -> int:
    return {"sedentary": 6, "light": 7, "moderate": 8, "very": 10}.get(activity, 8)


def _calc_macros(goal: str, calories: int) -> dict[str, int]:
    if goal == "gain":
        return {
            "protein": round(calories * 0.30 / 4),
            "carbs": round(calories * 0.45 / 4),
            "fat": round(calories * 0.25 / 9),
        }
    if goal == "lose":
        return {
            "protein": round(calories * 0.35 / 4),
            "carbs": round(calories * 0.40 / 4),
            "fat": round(calories * 0.25 / 9),
        }
    return {
        "protein": round(calories * 0.25 / 4),
        "carbs": round(calories * 0.50 / 4),
        "fat": round(calories * 0.25 / 9),
    }


def _calc_reading_goal(frequency: str) -> int:
    return {"never": 5, "monthly": 10, "biweekly": 20, "weekly": 40}.get(frequency, 10)


async def seed_goals_from_onboarding(db: AsyncSession, user_id: int, onboarding: Onboarding) -> None:
    today = date.today()
    calories = _calc_calorie_goal(onboarding.goal, onboarding.activity)
    water = _calc_water_goal(onboarding.activity)
    macros = _calc_macros(onboarding.goal, calories)
    pages = _calc_reading_goal(onboarding.reading_frequency)

    calorie_goal = await db.scalar(
        select(CalorieGoal).where(CalorieGoal.user_id == user_id, CalorieGoal.date == today)
    )
    if calorie_goal is None:
        db.add(CalorieGoal(user_id=user_id, date=today, goal=calories))
    elif calorie_goal.goal == DEFAULT_CALORIE_GOAL:
        calorie_goal.goal = calories

    nutrition_goal = await db.get(NutritionGoal, user_id)
    if nutrition_goal is not None and (
        nutrition_goal.protein == DEFAULT_NUTRITION_GOALS["protein"]
        and nutrition_goal.carbs == DEFAULT_NUTRITION_GOALS["carbs"]
        and nutrition_goal.fat == DEFAULT_NUTRITION_GOALS["fat"]
        and nutrition_goal.water == DEFAULT_NUTRITION_GOALS["water"]
    ):
        nutrition_goal.protein = macros["protein"]
        nutrition_goal.carbs = macros["carbs"]
        nutrition_goal.fat = macros["fat"]
        nutrition_goal.water = water

    reading_goal = await db.get(ReadingGoal, user_id)
    if reading_goal is not None and reading_goal.daily_goal == DEFAULT_READING_GOAL:
        reading_goal.daily_goal = pages
