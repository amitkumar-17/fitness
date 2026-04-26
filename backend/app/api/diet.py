from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import DietPlanRequest, PlanResponse
from app.ai.rag_chain import generate_diet_plan

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
async def create_diet_plan(
    data: DietPlanRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = {
        "fitness_goal": data.goal,
        "diet_preference": data.diet_type,
        "workout_location": user.workout_location.value if user.workout_location else "gym",
        "experience_level": user.experience_level,
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "age": user.age,
    }

    ai_result = await generate_diet_plan(
        goal=data.goal,
        diet_type=data.diet_type,
        meals_per_day=data.meals_per_day,
        calories_target=data.calories_target,
        allergies=data.allergies,
        specific_requirements=data.specific_requirements,
        user_profile=user_profile,
    )

    return PlanResponse(
        plan_type="diet",
        title=f"{data.goal.title()} Diet Plan - {data.diet_type.replace('_', ' ').title()}",
        content=ai_result["answer"],
        sources=ai_result["sources"],
    )
