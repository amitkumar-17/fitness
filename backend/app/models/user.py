import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum


class FitnessGoal(str, enum.Enum):
    BULKING = "bulking"
    SHREDDING = "shredding"
    LEANING = "leaning"
    GENERAL_FITNESS = "general_fitness"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"


class DietPreference(str, enum.Enum):
    VEGETARIAN = "vegetarian"
    NON_VEGETARIAN = "non_vegetarian"
    VEGAN = "vegan"
    EGGETARIAN = "eggetarian"


class WorkoutLocation(str, enum.Enum):
    HOME = "home"
    GYM = "gym"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)

    # Fitness profile
    age: Mapped[int | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    fitness_goal: Mapped[FitnessGoal | None] = mapped_column(
        SAEnum(FitnessGoal), nullable=True
    )
    diet_preference: Mapped[DietPreference | None] = mapped_column(
        SAEnum(DietPreference), nullable=True
    )
    workout_location: Mapped[WorkoutLocation | None] = mapped_column(
        SAEnum(WorkoutLocation), nullable=True
    )
    experience_level: Mapped[str | None] = mapped_column(String, nullable=True)  # beginner/intermediate/advanced

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
