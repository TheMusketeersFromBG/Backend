from datetime import date

from pydantic import BaseModel, ConfigDict


class ProfileMetricsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    height: float | None = None
    weight: float | None = None
    chest: float | None = None
    waist: float | None = None
    hips: float | None = None
    shoulders: float | None = None
    bicep: float | None = None
    thigh: float | None = None
    birthdate: date | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    language: str
    photo: str | None
    notifications: bool
    metrics: ProfileMetricsSchema


class UserUpdate(BaseModel):
    name: str | None = None
    photo: str | None = None
    language: str | None = None
    notifications: bool | None = None
    metrics: ProfileMetricsSchema | None = None
