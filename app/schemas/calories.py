from datetime import date

from pydantic import BaseModel, ConfigDict


class FoodEntryCreate(BaseModel):
    name: str
    calories: int
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    photo: str | None = None


class FoodEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    time: str
    photo: str | None


class GoalUpdate(BaseModel):
    goal: int


class CaloriesDayOut(BaseModel):
    date: date
    goal: int
    entries: list[FoodEntryOut]
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
