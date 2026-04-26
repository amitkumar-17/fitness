from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    APP_NAME: str = "Fitness AI"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fitness_ai"

    # JWT Auth
    SECRET_KEY: str = "change-this-to-a-secure-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI / LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str | None = None

    # Vector DB
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"

    # PDF storage
    PDF_UPLOAD_DIR: str = "./data/pdfs"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        return value

    @field_validator("EMBEDDING_MODEL", mode="before")
    @classmethod
    def parse_embedding_model(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value


settings = Settings()
