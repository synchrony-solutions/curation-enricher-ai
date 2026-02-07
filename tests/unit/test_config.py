"""Unit tests for configuration management."""

import pytest
from pydantic import ValidationError

from enricher.config import EnricherConfig


def test_config_defaults() -> None:
    """Test that default configuration values are set correctly."""
    config = EnricherConfig(anthropic_api_key="test_key")

    assert config.datahub_gms_url == "http://localhost:8080"
    assert config.llm_model == "claude-sonnet-4-5-20250929"
    assert config.llm_max_tokens == 4096
    assert config.llm_temperature == 0.7
    assert config.batch_size == 10
    assert config.max_retries == 3
    assert config.log_level == "INFO"


def test_config_custom_values() -> None:
    """Test that custom configuration values override defaults."""
    config = EnricherConfig(
        anthropic_api_key="test_key",
        datahub_gms_url="http://custom:8080",
        llm_temperature=0.5,
        batch_size=20,
    )

    assert config.datahub_gms_url == "http://custom:8080"
    assert config.llm_temperature == 0.5
    assert config.batch_size == 20


def test_config_temperature_validation() -> None:
    """Test that temperature validation works correctly."""
    # Valid temperatures
    EnricherConfig(anthropic_api_key="test_key", llm_temperature=0.0)
    EnricherConfig(anthropic_api_key="test_key", llm_temperature=0.5)
    EnricherConfig(anthropic_api_key="test_key", llm_temperature=1.0)

    # Invalid temperatures
    with pytest.raises(ValidationError):
        EnricherConfig(anthropic_api_key="test_key", llm_temperature=-0.1)

    with pytest.raises(ValidationError):
        EnricherConfig(anthropic_api_key="test_key", llm_temperature=1.1)


def test_config_log_level_validation() -> None:
    """Test that log level validation works correctly."""
    # Valid log levels
    config = EnricherConfig(anthropic_api_key="test_key", log_level="debug")
    assert config.log_level == "DEBUG"

    config = EnricherConfig(anthropic_api_key="test_key", log_level="WARNING")
    assert config.log_level == "WARNING"

    # Invalid log level
    with pytest.raises(ValidationError):
        EnricherConfig(anthropic_api_key="test_key", log_level="INVALID")


def test_config_positive_int_validation() -> None:
    """Test that positive integer validation works correctly."""
    # Valid values
    EnricherConfig(anthropic_api_key="test_key", batch_size=1)
    EnricherConfig(anthropic_api_key="test_key", max_retries=10)

    # Invalid values
    with pytest.raises(ValidationError):
        EnricherConfig(anthropic_api_key="test_key", batch_size=0)

    with pytest.raises(ValidationError):
        EnricherConfig(anthropic_api_key="test_key", max_retries=-1)


def test_config_missing_api_key() -> None:
    """Test that missing API key raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        EnricherConfig()

    assert "anthropic_api_key" in str(exc_info.value)
