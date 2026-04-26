import logging

from asyncpg import PostgresError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.api import auth, users, workout, diet, chat
from app.core.database import init_db
from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fitness AI",
    description="AI-powered fitness and diet planning app",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(workout.router, prefix="/api/workout", tags=["Workout Plans"])
app.include_router(diet.router, prefix="/api/diet", tags=["Diet Plans"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])


@app.on_event("startup")
async def startup() -> None:
    try:
        await init_db()
    except (OSError, PostgresError, SQLAlchemyError) as exc:
        # Let the API start; auth endpoints return 503 until the database is available.
        logger.warning("Database initialization skipped: %s", exc)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
