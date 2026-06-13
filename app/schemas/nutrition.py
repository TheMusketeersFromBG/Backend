from datetime import date

from pydantic import BaseModel, ConfigDict


class WaterOut(BaseModel):
    date: date
    glasses: int


class SupplementCreate(BaseModel):
    name: str
    dose: str = ""
    time: str = ""


class SupplementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    dose: str
    time: str
    taken_today: bool


class NutritionGoalsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    protein: int
    carbs: int
    fat: int
    water: int


class RecipeCreate(BaseModel):
    name: str
    calories: int = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    prep_time: str = ""
    description: str = ""


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    prep_time: str
    description: str


class MealSlot(BaseModel):
    breakfast: str = ""
    lunch: str = ""
    dinner: str = ""


class MealSlotUpdate(BaseModel):
    slot: str
    value: str


class MealPlanOut(BaseModel):
    meal_plan: dict[str, MealSlot]
