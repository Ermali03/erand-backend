from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Ortopedia Clinic API"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/ortopedia"
    )
    SECRET_KEY: str = Field(
        default="change-me-in-production-min-32-characters",
        min_length=32,
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    CREATE_INITIAL_ADMIN: bool = False
    INITIAL_ADMIN_EMAIL: str | None = None
    INITIAL_ADMIN_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return _split_csv(value)
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        env = value.lower()
        if env not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(sorted(allowed))}")
        return env

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        insecure_default = "change-me-in-production-min-32-characters"
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == insecure_default:
            raise ValueError("SECRET_KEY must be overridden in production.")
        return self


settings = Settings()
