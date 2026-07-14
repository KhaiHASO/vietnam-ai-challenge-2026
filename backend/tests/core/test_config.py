from pydantic import ValidationError
import pytest
from app.core.config import Settings

def test_production_rejects_wildcard_cors_and_demo_mode() -> None:
    try:
        # Giả lập tham số trực tiếp, bỏ qua dotenv bằng _env_file=None hoặc truyền kwargs
        Settings(
            environment="production", 
            cors_origins="*", 
            demo_mode=True, 
            jwt_secret="short",
            _env_file=None,
        )
    except ValidationError as exc:
        assert "production" in str(exc).lower() or "cors" in str(exc).lower() or "secret" in str(exc).lower()
    else:
        raise AssertionError("insecure production settings were accepted")


def test_production_rejects_the_committed_development_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="development JWT secret"):
        Settings(
            environment="production",
            cors_origins="https://cropdoctor.example",
            demo_mode=False,
            deepseek_api_key="production-provider-key",
            _env_file=None,
        )


def test_production_requires_credentials_for_the_primary_deepseek_provider() -> None:
    with pytest.raises(ValidationError, match="DeepSeek API key"):
        Settings(
            environment="production",
            cors_origins="https://cropdoctor.example",
            demo_mode=False,
            jwt_secret="a-production-secret-that-is-not-the-development-default",
            primary_ai_provider="deepseek",
            deepseek_api_key=None,
            _env_file=None,
        )


def test_production_requires_fpt_key_when_fpt_is_primary() -> None:
    with pytest.raises(ValidationError, match="FPT AI Factory API key"):
        Settings(
            environment="production",
            cors_origins="https://cropdoctor.example",
            demo_mode=False,
            jwt_secret="a-production-secret-that-is-not-the-development-default",
            primary_ai_provider="fpt-ai-factory",
            fpt_ai_factory_api_key=None,
            _env_file=None,
        )
