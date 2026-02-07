"""DataHub API client for fetching and updating metadata."""

import logging
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class DataHubClient:
    """
    Client for interacting with the DataHub GraphQL API.

    This client handles fetching schema metadata, updating entities,
    and managing authentication with the DataHub backend.
    """

    def __init__(self, gms_url: str, gms_token: Optional[str] = None) -> None:
        """
        Initialize the DataHub client.

        Args:
            gms_url: URL of the DataHub GMS service
            gms_token: Optional personal access token for authentication
        """
        self.gms_url = gms_url.rstrip("/")
        self.gms_token = gms_token
        self.headers = self._build_headers()

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "X-RestLi-Protocol-Version": "2.0.0",
        }
        if self.gms_token:
            headers["Authorization"] = f"Bearer {self.gms_token}"
        return headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def query_graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query against DataHub.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Response data from the GraphQL API

        Raises:
            httpx.HTTPError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.gms_url}/api/graphql",
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_dataset_schema(self, dataset_urn: str) -> Dict[str, Any]:
        """
        Fetch schema metadata for a dataset.

        Args:
            dataset_urn: URN of the dataset

        Returns:
            Schema metadata including columns and their properties
        """
        query = """
        query getDataset($urn: String!) {
            dataset(urn: $urn) {
                urn
                name
                description
                schemaMetadata {
                    fields {
                        fieldPath
                        nativeDataType
                        description
                        nullable
                        tags {
                            tag {
                                name
                            }
                        }
                    }
                }
                tags {
                    tags {
                        tag {
                            name
                        }
                    }
                }
            }
        }
        """
        result = await self.query_graphql(query, {"urn": dataset_urn})
        return result.get("data", {}).get("dataset", {})

    async def list_datasets(
        self, platform: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List datasets in the catalog.

        Args:
            platform: Optional platform filter (e.g., 'snowflake', 'postgres')
            limit: Maximum number of datasets to return

        Returns:
            List of dataset metadata
        """
        query = """
        query searchDatasets($input: SearchInput!) {
            search(input: $input) {
                total
                searchResults {
                    entity {
                        ... on Dataset {
                            urn
                            name
                            platform {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {
            "input": {
                "type": "DATASET",
                "query": "*",
                "start": 0,
                "count": limit,
            }
        }
        if platform:
            variables["input"]["filters"] = [{"field": "platform", "value": platform}]

        result = await self.query_graphql(query, variables)
        search_results = result.get("data", {}).get("search", {}).get("searchResults", [])
        return [item["entity"] for item in search_results]

    async def update_column_description(
        self, dataset_urn: str, field_path: str, description: str
    ) -> bool:
        """
        Update the description for a specific column.

        Args:
            dataset_urn: URN of the dataset
            field_path: Path to the field/column
            description: New description text

        Returns:
            True if update was successful
        """
        # TODO: Implement using DataHub's metadata ingestion API
        logger.info(
            f"Would update column description: {dataset_urn} / {field_path} -> {description}"
        )
        return True

    async def add_tag_to_column(
        self, dataset_urn: str, field_path: str, tag_urn: str
    ) -> bool:
        """
        Add a tag to a specific column.

        Args:
            dataset_urn: URN of the dataset
            field_path: Path to the field/column
            tag_urn: URN of the tag to add

        Returns:
            True if tag was added successfully
        """
        # TODO: Implement using DataHub's metadata ingestion API
        logger.info(f"Would add tag to column: {dataset_urn} / {field_path} -> {tag_urn}")
        return True
