"""Unit tests for configuration management."""

import pytest
from pydantic import ValidationError

from enricher.config import EnricherConfig


def test_config_defaults_claude_code() -> None:
    """Test default config uses claude-code backend with no API key required."""
    config = EnricherConfig()

    assert config.llm_backend == "claude-code"
    assert config.anthropic_api_key is None
    assert config.claude_command == "claude"
    assert config.datahub_gms_url == "http://localhost:8080"
    assert config.llm_model == "claude-sonnet-4-5-20250929"
    assert config.llm_max_tokens == 4096
    assert config.llm_temperature == 0.7
    assert config.batch_size == 10
    assert config.max_retries == 3
    assert config.log_level == "INFO"


def test_config_api_backend_requires_key() -> None:
    """Test that anthropic-api backend requires an API key."""
    with pytest.raises(ValidationError) as exc_info:
        EnricherConfig(llm_backend="anthropic-api")

    assert "anthropic_api_key" in str(exc_info.value)


def test_config_api_backend_with_key() -> None:
    """Test that anthropic-api backend works when API key is provided."""
    config = EnricherConfig(llm_backend="anthropic-api", anthropic_api_key="test_key")

    assert config.llm_backend == "anthropic-api"
    assert config.anthropic_api_key == "test_key"


def test_config_invalid_backend() -> None:
    """Test that an invalid backend raises a validation error."""
    with pytest.raises(ValidationError):
        EnricherConfig(llm_backend="invalid-backend")


def test_config_custom_values() -> None:
    """Test that custom configuration values override defaults."""
    config = EnricherConfig(
        datahub_gms_url="http://custom:8080",
        llm_temperature=0.5,
        batch_size=20,
        claude_command="/usr/local/bin/claude",
    )

    assert config.datahub_gms_url == "http://custom:8080"
    assert config.llm_temperature == 0.5
    assert config.batch_size == 20
    assert config.claude_command == "/usr/local/bin/claude"


def test_config_temperature_validation() -> None:
    """Test that temperature validation works correctly."""
    # Valid temperatures
    EnricherConfig(llm_temperature=0.0)
    EnricherConfig(llm_temperature=0.5)
    EnricherConfig(llm_temperature=1.0)

    # Invalid temperatures
    with pytest.raises(ValidationError):
        EnricherConfig(llm_temperature=-0.1)

    with pytest.raises(ValidationError):
        EnricherConfig(llm_temperature=1.1)


def test_config_log_level_validation() -> None:
    """Test that log level validation works correctly."""
    # Valid log levels
    config = EnricherConfig(log_level="debug")
    assert config.log_level == "DEBUG"

    config = EnricherConfig(log_level="WARNING")
    assert config.log_level == "WARNING"

    # Invalid log level
    with pytest.raises(ValidationError):
        EnricherConfig(log_level="INVALID")


def test_config_positive_int_validation() -> None:
    """Test that positive integer validation works correctly."""
    # Valid values
    EnricherConfig(batch_size=1)
    EnricherConfig(max_retries=10)

    # Invalid values
    with pytest.raises(ValidationError):
        EnricherConfig(batch_size=0)

    with pytest.raises(ValidationError):
        EnricherConfig(max_retries=-1)


def test_config_claude_code_ignores_api_key() -> None:
    """Test that claude-code backend works even if API key is provided (ignored)."""
    config = EnricherConfig(llm_backend="claude-code", anthropic_api_key="some_key")

    assert config.llm_backend == "claude-code"
    assert config.anthropic_api_key == "some_key"
