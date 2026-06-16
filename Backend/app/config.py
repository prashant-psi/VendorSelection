import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# APP_ENV picks the env file name, e.g. .env.local, .env.staging
# Falls back to .env when the env-specific file does not exist.
APP_ENV = os.getenv("APP_ENV", "local")

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_SPECIFIC = _BACKEND_DIR / f".env.{APP_ENV}"
ENV_FILE = _ENV_SPECIFIC if _ENV_SPECIFIC.exists() else _BACKEND_DIR / ".env"


class AppSettings(BaseSettings):
    """Loads database and Azure OpenAI settings from the env file."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_DRIVER: str = "psycopg2"

    # Azure OpenAI — used by the chat assistant
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT: str
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"


settings = AppSettings()

vendor_connection_url = URL.create(
    drivername=f"postgresql+{settings.DB_DRIVER}",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

# Keep old name so existing imports still work.
dbSettings = settings
