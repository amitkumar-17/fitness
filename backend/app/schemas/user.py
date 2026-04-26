from pydantic import BaseModel, EmailStr
from app.models.user import FitnessGoal, DietPreference, WorkoutLocation


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    full_name: str | None = None
    age: int | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    fitness_goal: FitnessGoal | None = None
    diet_preference: DietPreference | None = None
    workout_location: WorkoutLocation | None = None
    experience_level: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    age: int | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    fitness_goal: FitnessGoal | None = None
    diet_preference: DietPreference | None = None
    workout_location: WorkoutLocation | None = None
    experience_level: str | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
