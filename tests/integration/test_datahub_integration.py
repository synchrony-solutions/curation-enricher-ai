"""Integration tests for DataHub client."""

import pytest

from enricher.config import EnricherConfig
from enricher.datahub_client import DataHubClient

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def datahub_client() -> DataHubClient:
    """Create a DataHub client for testing."""
    config = EnricherConfig(anthropic_api_key="test_key")
    return DataHubClient(gms_url=config.datahub_gms_url, gms_token=config.datahub_gms_token)


@pytest.mark.asyncio
async def test_list_datasets(datahub_client: DataHubClient) -> None:
    """Test listing datasets from DataHub."""
    # This test requires a running DataHub instance
    datasets = await datahub_client.list_datasets(limit=5)

    assert isinstance(datasets, list)
    # Note: May be empty if DataHub has no data yet
    if datasets:
        assert "urn" in datasets[0]
        assert "name" in datasets[0]


@pytest.mark.asyncio
async def test_get_dataset_schema(datahub_client: DataHubClient) -> None:
    """Test fetching schema for a specific dataset."""
    # This test requires a running DataHub instance with sample data
    # Skip if no datasets are available
    datasets = await datahub_client.list_datasets(limit=1)

    if not datasets:
        pytest.skip("No datasets available in DataHub")

    dataset_urn = datasets[0]["urn"]
    schema = await datahub_client.get_dataset_schema(dataset_urn)

    assert schema is not None
    assert "urn" in schema
