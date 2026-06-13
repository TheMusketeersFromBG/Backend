from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkoutSet(BaseModel):
    reps: str = ""
    weight: str = ""
    done: bool = False


class WorkoutExercise(BaseModel):
    name: str
    muscleGroup: str
    sets: list[WorkoutSet] = []


class WorkoutCreate(BaseModel):
    name: str = "Тренировка"
    date: datetime | None = None
    duration: int = 0
    exercises: list[WorkoutExercise] = []
    calories_burned: int = 0


class WorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    date: datetime
    duration: int
    exercises: list[WorkoutExercise]
    calories_burned: int


class PlanDaySchema(BaseModel):
    name: str = ""
    exercises: list[str] = []


class PlanUpdate(BaseModel):
    plan: dict[str, PlanDaySchema]


class PlanOut(BaseModel):
    plan: dict[str, PlanDaySchema]
