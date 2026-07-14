from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEVELOPMENT_JWT_SECRET = "super-secret-key-for-dev-only-change-in-prod"


class Settings(BaseSettings):
    app_name: str = "MathPath THPT Backend"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"

    environment: Literal["development", "test", "production"] = "development"

    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "mathpath_thpt"
    redis_url: str = "redis://localhost:6379/0"
    chroma_url: str = "http://localhost:8000"

    jwt_secret: SecretStr = Field(default=SecretStr(DEVELOPMENT_JWT_SECRET))
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    ai_service_url: str = "http://localhost:8001"
    primary_ai_provider: Literal["deepseek", "ollama", "fpt-ai-factory"] = "deepseek"
    deepseek_api_key: SecretStr | None = None
    fpt_ai_factory_api_key: SecretStr | None = None

    bootstrap_admin_username: str | None = None
    bootstrap_admin_password: SecretStr | None = None
    bootstrap_admin_tenant_id: str = "single"

    demo_mode: bool = True
    cors_origins: str = "*"
    upload_dir: str = "uploads"
    upload_limit_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        return self.validate_runtime()

    def validate_runtime(self) -> "Settings":
        if self.environment == "production":
            if self.cors_origins.strip() == "*":
                raise ValueError("Wildcard CORS is not allowed in production")
            if self.demo_mode:
                raise ValueError("Demo mode is not allowed in production")
            jwt_secret = self.jwt_secret.get_secret_value()
            if len(jwt_secret) < 32:
                raise ValueError("JWT secret must be at least 32 characters in production")
            if jwt_secret == DEVELOPMENT_JWT_SECRET:
                raise ValueError("The development JWT secret is not allowed in production")
            if self.primary_ai_provider == "deepseek" and (
                self.deepseek_api_key is None
                or not self.deepseek_api_key.get_secret_value().strip()
            ):
                raise ValueError("DeepSeek API key is required when DeepSeek is the primary provider")
            if self.primary_ai_provider == "fpt-ai-factory" and (
                self.fpt_ai_factory_api_key is None
                or not self.fpt_ai_factory_api_key.get_secret_value().strip()
            ):
                raise ValueError("FPT AI Factory API key is required when FPT AI Factory is the primary provider")
        if (self.bootstrap_admin_username is None) != (self.bootstrap_admin_password is None):
            raise ValueError("Bootstrap admin username and password must be configured together")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_root_path(self) -> Path:
        upload_path = Path(self.upload_dir)
        if upload_path.is_absolute():
            return upload_path
        backend_dir = Path(__file__).resolve().parents[2]
        return backend_dir / upload_path

    @property
    def knowledge_storage_root_path(self) -> Path:
        """Private object storage; never mount this directory as static files."""
        return self.upload_root_path.parent / "knowledge"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
