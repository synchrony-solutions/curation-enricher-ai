"""Configuration management for the DataHub AI Enricher."""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnricherConfig(BaseSettings):
    """
    Configuration for the DataHub AI Enricher.

    All settings can be provided via environment variables (prefixed with ENRICHER_)
    or via a YAML configuration file.
    """

    model_config = SettingsConfigDict(
        env_prefix="ENRICHER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # DataHub Configuration
    datahub_gms_url: str = Field(
        default="http://localhost:8080",
        description="URL of the DataHub GMS (Graph Metadata Service)",
    )
    datahub_gms_token: Optional[str] = Field(
        default=None, description="Personal access token for DataHub API authentication"
    )

    # Claude API Configuration
    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude")

    # LLM Configuration
    llm_model: str = Field(
        default="claude-sonnet-4-5-20250929", description="Claude model to use"
    )
    llm_max_tokens: int = Field(default=4096, description="Maximum tokens for LLM responses")
    llm_temperature: float = Field(
        default=0.7, description="Temperature for LLM responses (0.0-1.0)"
    )

    # Processing Configuration
    batch_size: int = Field(default=10, description="Number of datasets to process in one batch")
    max_retries: int = Field(default=3, description="Maximum number of retries for API calls")
    log_level: str = Field(default="INFO", description="Logging level")

    # Feature Flags
    enable_pii_detection: bool = Field(
        default=True, description="Enable PII detection suggestions"
    )
    enable_tag_suggestions: bool = Field(
        default=True, description="Enable tag suggestions"
    )
    enable_column_descriptions: bool = Field(
        default=True, description="Enable column description generation"
    )

    @field_validator("llm_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate that temperature is between 0.0 and 1.0."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    @field_validator("batch_size", "max_retries")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Validate that integer fields are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v
