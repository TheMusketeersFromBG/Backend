from datetime import date

from pydantic import BaseModel, ConfigDict


class DayDataOut(BaseModel):
    date: str
    label: str
    calories: int
    steps: int
    workouts: int
    pages: int


class StepsLogCreate(BaseModel):
    steps: int


class StepsGoalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    goal: int


class WeightEntryCreate(BaseModel):
    weight: float


class WeightEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    weight: float


class StreakOut(BaseModel):
    streak: int
