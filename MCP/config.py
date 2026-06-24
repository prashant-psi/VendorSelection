from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BACKEND_URL: str = "http://localhost:8000/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()