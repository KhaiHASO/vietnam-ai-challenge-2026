from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CropDoctor AI Backend"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"

    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "cropdoctor_ai"
    ai_service_url: str = "http://localhost:8001"
    demo_mode: bool = True
    cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
