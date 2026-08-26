from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "FrameScout API"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://framescout:framescout_dev_password@localhost:5432/framescout_db"
    )

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # External Provider Keys
    PEXELS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MEDIA_STORAGE_DIR: str = "/tmp/framescout_media"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
