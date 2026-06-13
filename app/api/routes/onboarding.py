from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.onboarding import Onboarding
from app.models.user import User
from app.schemas.onboarding import OnboardingOut, OnboardingUpdate
from app.services.onboarding import seed_goals_from_onboarding

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.get("", response_model=OnboardingOut)
async def get_onboarding(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Onboarding:
    return await db.get(Onboarding, user.id)


@router.put("", response_model=OnboardingOut)
async def save_onboarding(
    payload: OnboardingUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Onboarding:
    onboarding = await db.get(Onboarding, user.id)
    for field, value in payload.model_dump().items():
        setattr(onboarding, field, value)
    onboarding.created_at = datetime.now(timezone.utc)

    await db.flush()
    await seed_goals_from_onboarding(db, user.id, onboarding)
    await db.commit()
    await db.refresh(onboarding)
    return onboarding
