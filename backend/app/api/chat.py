"""
Chat endpoint — Free-form AI conversation about fitness.
Users can ask anything: "I want to bulk up, give me a 4-day gym split with non-veg diet"
The AI uses RAG to pull relevant info from your PDFs and generates personalized advice.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import shutil

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.rag_chain import generate_response
from app.ai.ingestion import ingest_single_pdf, ingest_pdfs
from app.core.config import settings

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get user profile
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get or create chat session
    if data.session_id:
        session_result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == data.session_id,
                ChatSession.user_id == user_id,
            )
        )
        session = session_result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(user_id=user_id, title=data.message[:50])
        db.add(session)
        await db.flush()

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.message,
    )
    db.add(user_msg)

    # Build user profile dict
    user_profile = {
        "fitness_goal": user.fitness_goal.value if user.fitness_goal else "general fitness",
        "diet_preference": user.diet_preference.value if user.diet_preference else "not specified",
        "workout_location": user.workout_location.value if user.workout_location else "gym",
        "experience_level": user.experience_level or "beginner",
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "age": user.age,
    }

    # Generate AI response using RAG
    ai_result = await generate_response(data.message, user_profile)

    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=ai_result["answer"],
        metadata_={"sources": ai_result["sources"]},
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        session_id=session.id,
        message=ai_result["answer"],
        sources=ai_result["sources"],
    )


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    category: str = "general",
    user_id: str = Depends(get_current_user),
):
    """Upload a PDF file to be ingested into the knowledge base."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    os.makedirs(settings.PDF_UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.PDF_UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = ingest_single_pdf(file_path, category=category)
    return {"message": f"PDF '{file.filename}' ingested successfully", **result}


@router.post("/ingest-all")
async def ingest_all_pdfs(user_id: str = Depends(get_current_user)):
    """Ingest all PDFs from the configured directory."""
    result = ingest_pdfs()
    return {"message": "All PDFs ingested", **result}
