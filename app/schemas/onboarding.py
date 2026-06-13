from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OnboardingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    goal: str
    activity: str
    sports: list[str]
    diet: str
    allergies: list[str]
    target_weight: str
    reading_genres: list[str]
    reading_frequency: str
    plan: str
    created_at: datetime


class OnboardingUpdate(BaseModel):
    goal: str
    activity: str
    sports: list[str] = []
    diet: str
    allergies: list[str] = []
    target_weight: str = ""
    reading_genres: list[str] = []
    reading_frequency: str
    plan: str = "free"
