from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    message: str
    sources: list[str] = []  # PDF sources used for the answer


class WorkoutPlanRequest(BaseModel):
    goal: str  # bulking, shredding, leaning, general_fitness
    location: str  # home or gym
    experience_level: str | None = None
    days_per_week: int = 5
    duration_minutes: int = 60
    specific_requirements: str | None = None


class DietPlanRequest(BaseModel):
    goal: str  # bulking, shredding, leaning, general_fitness
    diet_type: str  # vegetarian, non_vegetarian, vegan
    meals_per_day: int = 4
    calories_target: int | None = None
    allergies: list[str] = []
    specific_requirements: str | None = None


class PlanResponse(BaseModel):
    plan_type: str
    title: str
    content: str
    sources: list[str] = []
