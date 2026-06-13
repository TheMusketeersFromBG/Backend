from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    books,
    calories,
    chat,
    nutrition,
    onboarding,
    progress,
    users,
    workouts,
)
from app.core.config import settings

app = FastAPI(title="AISI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(onboarding.router)
app.include_router(calories.router)
app.include_router(books.router)
app.include_router(workouts.router)
app.include_router(nutrition.router)
app.include_router(progress.router)
app.include_router(chat.router)


@app.get("/")
async def root() -> dict:
    return {"status": "ok"}
