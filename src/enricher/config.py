"""Configuration management for the DataHub AI Enricher."""

from typing import Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnricherConfig(BaseSettings):
    """
    Configuration for the DataHub AI Enricher.

    All settings can be provided via environment variables (prefixed with ENRICHER_)
    or via a YAML configuration file.

    Two LLM backends are supported:
    - "claude-code" (default): Uses the local Claude Code CLI. No API key needed.
    - "anthropic-api": Uses the Anthropic API directly. Requires an API key.
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

    # LLM Backend Selection
    llm_backend: str = Field(
        default="claude-code",
        description="LLM backend: 'claude-code' (local CLI) or 'anthropic-api' (cloud)",
    )

    # Anthropic API Configuration (only needed for 'anthropic-api' backend)
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key (only required for 'anthropic-api' backend)"
    )

    # LLM Configuration (only used by 'anthropic-api' backend)
    llm_model: str = Field(
        default="claude-sonnet-4-5-20250929", description="Claude model to use (API backend only)"
    )
    llm_max_tokens: int = Field(
        default=4096, description="Maximum tokens for LLM responses (API backend only)"
    )
    llm_temperature: float = Field(
        default=0.7, description="Temperature for LLM responses (API backend only, 0.0-1.0)"
    )

    # Claude Code Configuration (only used by 'claude-code' backend)
    claude_command: str = Field(
        default="claude", description="Path to the Claude Code CLI binary"
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

    @field_validator("llm_backend")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate that the LLM backend is a supported value."""
        valid_backends = ["claude-code", "anthropic-api"]
        if v not in valid_backends:
            raise ValueError(f"llm_backend must be one of {valid_backends}")
        return v

    @model_validator(mode="after")
    def validate_api_key_for_backend(self) -> "EnricherConfig":
        """Validate that anthropic_api_key is provided when using the API backend."""
        if self.llm_backend == "anthropic-api" and not self.anthropic_api_key:
            raise ValueError(
                "anthropic_api_key is required when llm_backend is 'anthropic-api'. "
                "Set ENRICHER_ANTHROPIC_API_KEY or switch to llm_backend='claude-code'."
            )
        return self

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
