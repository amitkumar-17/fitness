from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import WorkoutPlanRequest, PlanResponse
from app.ai.rag_chain import generate_workout_plan

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def create_workout_plan(
    data: WorkoutPlanRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get user profile for personalization
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = {
        "fitness_goal": data.goal,
        "workout_location": data.location,
        "experience_level": data.experience_level or user.experience_level,
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "age": user.age,
        "diet_preference": user.diet_preference.value if user.diet_preference else None,
    }

    ai_result = await generate_workout_plan(
        goal=data.goal,
        location=data.location,
        experience_level=data.experience_level or "beginner",
        days_per_week=data.days_per_week,
        duration_minutes=data.duration_minutes,
        specific_requirements=data.specific_requirements,
        user_profile=user_profile,
    )

    return PlanResponse(
        plan_type="workout",
        title=f"{data.goal.title()} Workout Plan - {data.location.title()}",
        content=ai_result["answer"],
        sources=ai_result["sources"],
    )
