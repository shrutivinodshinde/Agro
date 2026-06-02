from pathlib import Path
from typing import ClassVar
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Base Paths ─────────────────────────────────────────────────────────────
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    # ── Model Paths ────────────────────────────────────────────────────────────
    MODEL_PATH: str = str(BASE_DIR / "data/models/best_model.pth")
    MODEL_CLASSES_PATH: str = str(BASE_DIR / "data/models/classes.json")

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "AgriGuard API"
    APP_VERSION: str = "1.0.0"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── PostgreSQL ─────────────────────────────────────────────────────────────
    POSTGRES_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/agriguard"
    )

    # ── Ollama ─────────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # ── Authentication ─────────────────────────────────────────────────────────
    SECRET_KEY: str = "agriguard-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ── Demo User ──────────────────────────────────────────────────────────────
    DEMO_EMAIL: str = "admin@agriguard.com"
    DEMO_PASSWORD: str = "admin"
    DEMO_NAME: str = "AgriGuard Admin"

    # ── Anthropic / Claude ─────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-haiku-20240307"
    GROQ_API_KEY: str = ""

    # ── Image Inference ────────────────────────────────────────────────────────
    IMAGE_SIZE: int = 224
    TOP_K: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


@lru_cache
def get_settings():
    return Settings()