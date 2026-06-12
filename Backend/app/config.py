import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# Set via the APP_ENV environment variable, e.g. in PowerShell:
#   $env:APP_ENV = "staging"
APP_ENV = os.getenv("APP_ENV", "local")

_BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = _BACKEND_DIR / f".env.{APP_ENV}"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_DRIVER: str = "psycopg2"


dbSettings = DatabaseSettings()


vendor_connection_url = URL.create(
    drivername=f"postgresql+{dbSettings.DB_DRIVER}",
    username=dbSettings.DB_USER,
    password=dbSettings.DB_PASSWORD,
    host=dbSettings.DB_HOST,
    port=dbSettings.DB_PORT,
    database=dbSettings.DB_NAME,
)
