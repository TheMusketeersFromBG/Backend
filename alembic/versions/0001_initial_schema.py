"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="BG"),
        sa.Column("photo", sa.String(), nullable=True),
        sa.Column("notifications", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    op.create_table(
        "profile_metrics",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("chest", sa.Float(), nullable=True),
        sa.Column("waist", sa.Float(), nullable=True),
        sa.Column("hips", sa.Float(), nullable=True),
        sa.Column("shoulders", sa.Float(), nullable=True),
        sa.Column("bicep", sa.Float(), nullable=True),
        sa.Column("thigh", sa.Float(), nullable=True),
        sa.Column("birthdate", sa.Date(), nullable=True),
    )

    op.create_table(
        "onboarding",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("goal", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("activity", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("diet", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("target_weight", sa.String(length=16), nullable=False, server_default=""),
        sa.Column("reading_frequency", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("plan", sa.String(length=8), nullable=False, server_default="free"),
        sa.Column("sports", JSONB(), nullable=False, server_default="[]"),
        sa.Column("allergies", JSONB(), nullable=False, server_default="[]"),
        sa.Column("reading_genres", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "food_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("protein", sa.Float(), nullable=False, server_default="0"),
        sa.Column("carbs", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fat", sa.Float(), nullable=False, server_default="0"),
        sa.Column("time", sa.String(length=16), nullable=False, server_default=""),
        sa.Column("photo", sa.String(), nullable=True),
    )
    op.create_index("ix_food_entries_user_id", "food_entries", ["user_id"])
    op.create_index("ix_food_entries_date", "food_entries", ["date"])

    op.create_table(
        "calorie_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("goal", sa.Integer(), nullable=False, server_default="2000"),
        sa.UniqueConstraint("user_id", "date", name="uq_calorie_goal_user_date"),
    )
    op.create_index("ix_calorie_goals_user_id", "calorie_goals", ["user_id"])
    op.create_index("ix_calorie_goals_date", "calorie_goals", ["date"])

    book_status = sa.Enum("reading", "want", "finished", name="book_status")
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("pages", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pages_read", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cover", sa.String(), nullable=True),
        sa.Column("status", book_status, nullable=False, server_default="want"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("genre", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("date_added", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("date_finished", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_books_user_id", "books", ["user_id"])

    op.create_table(
        "reading_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("pages_read", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "date", name="uq_reading_progress_user_date"),
    )
    op.create_index("ix_reading_progress_user_id", "reading_progress", ["user_id"])
    op.create_index("ix_reading_progress_date", "reading_progress", ["date"])

    op.create_table(
        "reading_goals",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("daily_goal", sa.Integer(), nullable=False, server_default="20"),
    )

    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exercises", JSONB(), nullable=False, server_default="[]"),
        sa.Column("calories_burned", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_workouts_user_id", "workouts", ["user_id"])

    op.create_table(
        "workout_plan_days",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("exercises", JSONB(), nullable=False, server_default="[]"),
        sa.UniqueConstraint("user_id", "day", name="uq_workout_plan_user_day"),
    )
    op.create_index("ix_workout_plan_days_user_id", "workout_plan_days", ["user_id"])

    op.create_table(
        "water_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("glasses", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "date", name="uq_water_log_user_date"),
    )
    op.create_index("ix_water_logs_user_id", "water_logs", ["user_id"])
    op.create_index("ix_water_logs_date", "water_logs", ["date"])

    op.create_table(
        "supplements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("dose", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("time", sa.String(length=16), nullable=False, server_default=""),
    )
    op.create_index("ix_supplements_user_id", "supplements", ["user_id"])

    op.create_table(
        "supplement_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("supplement_id", sa.Integer(), sa.ForeignKey("supplements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("taken", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("supplement_id", "date", name="uq_supplement_log_supplement_date"),
    )
    op.create_index("ix_supplement_logs_supplement_id", "supplement_logs", ["supplement_id"])
    op.create_index("ix_supplement_logs_date", "supplement_logs", ["date"])

    op.create_table(
        "nutrition_goals",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("protein", sa.Integer(), nullable=False, server_default="150"),
        sa.Column("carbs", sa.Integer(), nullable=False, server_default="250"),
        sa.Column("fat", sa.Integer(), nullable=False, server_default="70"),
        sa.Column("water", sa.Integer(), nullable=False, server_default="8"),
    )

    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("protein", sa.Float(), nullable=False, server_default="0"),
        sa.Column("carbs", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fat", sa.Float(), nullable=False, server_default="0"),
        sa.Column("prep_time", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_recipes_user_id", "recipes", ["user_id"])

    op.create_table(
        "meal_plan_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.String(length=16), nullable=False),
        sa.Column("breakfast", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("lunch", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("dinner", sa.String(length=255), nullable=False, server_default=""),
        sa.UniqueConstraint("user_id", "day", name="uq_meal_plan_user_day"),
    )
    op.create_index("ix_meal_plan_entries_user_id", "meal_plan_entries", ["user_id"])

    op.create_table(
        "steps_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("steps", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "date", name="uq_steps_log_user_date"),
    )
    op.create_index("ix_steps_logs_user_id", "steps_logs", ["user_id"])
    op.create_index("ix_steps_logs_date", "steps_logs", ["date"])

    op.create_table(
        "steps_goals",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("goal", sa.Integer(), nullable=False, server_default="10000"),
    )

    op.create_table(
        "weight_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.UniqueConstraint("user_id", "date", name="uq_weight_log_user_date"),
    )
    op.create_index("ix_weight_logs_user_id", "weight_logs", ["user_id"])
    op.create_index("ix_weight_logs_date", "weight_logs", ["date"])

    chat_sender = sa.Enum("user", "ai", name="chat_sender")
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender", chat_sender, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"])

    # Seed global sample recipes (user_id = NULL), mirroring the frontend's SAMPLE_RECIPES
    recipes_table = sa.table(
        "recipes",
        sa.column("user_id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("calories", sa.Integer()),
        sa.column("protein", sa.Float()),
        sa.column("carbs", sa.Float()),
        sa.column("fat", sa.Float()),
        sa.column("prep_time", sa.String()),
        sa.column("description", sa.Text()),
    )
    op.bulk_insert(
        recipes_table,
        [
            {
                "user_id": None,
                "name": "Овесена каша с плодове",
                "calories": 320,
                "protein": 12,
                "carbs": 58,
                "fat": 6,
                "prep_time": "10 мин",
                "description": "Здравословна закуска богата на фибри и витамини.",
            },
            {
                "user_id": None,
                "name": "Пилешки гърди на скара",
                "calories": 280,
                "protein": 52,
                "carbs": 0,
                "fat": 6,
                "prep_time": "20 мин",
                "description": "Постно месо богато на протеин.",
            },
            {
                "user_id": None,
                "name": "Гръцка салата",
                "calories": 180,
                "protein": 8,
                "carbs": 12,
                "fat": 12,
                "prep_time": "10 мин",
                "description": "Свежа салата с фета и маслини.",
            },
            {
                "user_id": None,
                "name": "Лосос със зеленчуци",
                "calories": 420,
                "protein": 38,
                "carbs": 15,
                "fat": 24,
                "prep_time": "25 мин",
                "description": "Богат на омега-3 мастни киселини.",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    sa.Enum(name="chat_sender").drop(op.get_bind(), checkfirst=True)
    op.drop_table("weight_logs")
    op.drop_table("steps_goals")
    op.drop_table("steps_logs")
    op.drop_table("meal_plan_entries")
    op.drop_table("recipes")
    op.drop_table("nutrition_goals")
    op.drop_table("supplement_logs")
    op.drop_table("supplements")
    op.drop_table("water_logs")
    op.drop_table("workout_plan_days")
    op.drop_table("workouts")
    op.drop_table("reading_goals")
    op.drop_table("reading_progress")
    op.drop_table("books")
    sa.Enum(name="book_status").drop(op.get_bind(), checkfirst=True)
    op.drop_table("calorie_goals")
    op.drop_table("food_entries")
    op.drop_table("onboarding")
    op.drop_table("profile_metrics")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
