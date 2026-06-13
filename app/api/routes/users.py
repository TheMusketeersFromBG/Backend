from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import ProfileMetrics
from app.models.user import User
from app.schemas.user import ProfileMetricsSchema, UserOut, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


def _to_user_out(user: User, metrics: ProfileMetrics) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        language=user.language,
        photo=user.photo,
        notifications=user.notifications,
        metrics=ProfileMetricsSchema.model_validate(metrics),
    )


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserOut:
    metrics = await db.get(ProfileMetrics, user.id)
    return _to_user_out(user, metrics)


@router.put("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    if payload.name is not None:
        user.name = payload.name
    if payload.photo is not None:
        user.photo = payload.photo
    if payload.language is not None:
        user.language = payload.language
    if payload.notifications is not None:
        user.notifications = payload.notifications

    metrics = await db.get(ProfileMetrics, user.id)
    if payload.metrics is not None:
        for field, value in payload.metrics.model_dump(exclude_unset=True).items():
            setattr(metrics, field, value)

    await db.commit()
    return _to_user_out(user, metrics)
