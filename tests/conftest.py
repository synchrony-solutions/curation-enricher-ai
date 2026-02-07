"""Pytest configuration and shared fixtures."""

import pytest

from enricher.config import EnricherConfig


@pytest.fixture
def test_config() -> EnricherConfig:
    """
    Provide a test configuration with dummy values.

    This fixture can be used across all tests that need a basic config.
    """
    return EnricherConfig(
        anthropic_api_key="test_api_key_12345",
        datahub_gms_url="http://localhost:8080",
        llm_model="claude-sonnet-4-5-20250929",
        llm_temperature=0.7,
        batch_size=5,
        max_retries=2,
        log_level="INFO",
    )


@pytest.fixture
def sample_dataset_schema() -> dict:
    """
    Provide a sample dataset schema for testing.

    Returns a typical DataHub dataset schema structure.
    """
    return {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.users,PROD)",
        "name": "users",
        "description": "User account information",
        "schemaMetadata": {
            "fields": [
                {
                    "fieldPath": "user_id",
                    "nativeDataType": "INTEGER",
                    "description": "Unique user identifier",
                    "nullable": False,
                    "tags": [],
                },
                {
                    "fieldPath": "email",
                    "nativeDataType": "VARCHAR(255)",
                    "description": "",
                    "nullable": False,
                    "tags": [],
                },
                {
                    "fieldPath": "first_name",
                    "nativeDataType": "VARCHAR(100)",
                    "description": "",
                    "nullable": True,
                    "tags": [],
                },
                {
                    "fieldPath": "last_name",
                    "nativeDataType": "VARCHAR(100)",
                    "description": "",
                    "nullable": True,
                    "tags": [],
                },
                {
                    "fieldPath": "created_at",
                    "nativeDataType": "TIMESTAMP",
                    "description": "",
                    "nullable": False,
                    "tags": [],
                },
            ]
        },
        "tags": {"tags": []},
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
