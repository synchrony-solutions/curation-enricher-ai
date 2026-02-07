"""Core enrichment engine that orchestrates metadata suggestions."""

import logging
from typing import Any, Dict, List, Optional

from enricher.config import EnricherConfig
from enricher.datahub_client import DataHubClient
from enricher.llm_base import LLMServiceBase

logger = logging.getLogger(__name__)


def create_llm_service(config: EnricherConfig) -> LLMServiceBase:
    """
    Factory function to create the appropriate LLM service backend.

    Args:
        config: Enricher configuration with llm_backend setting

    Returns:
        An LLM service instance (ClaudeCodeLocalService or AnthropicAPIService)

    Raises:
        ValueError: If the configured backend is unknown
    """
    if config.llm_backend == "claude-code":
        from enricher.llm_claude_code import ClaudeCodeLocalService

        return ClaudeCodeLocalService(claude_command=config.claude_command)
    elif config.llm_backend == "anthropic-api":
        from enricher.llm_service import AnthropicAPIService

        return AnthropicAPIService(config)
    else:
        raise ValueError(f"Unknown LLM backend: {config.llm_backend}")


class EnrichmentSuggestion:
    """Represents a single metadata enrichment suggestion."""

    def __init__(
        self,
        dataset_urn: str,
        field_path: Optional[str],
        suggestion_type: str,
        suggested_value: Any,
        confidence: float = 1.0,
    ) -> None:
        """
        Initialize an enrichment suggestion.

        Args:
            dataset_urn: URN of the dataset
            field_path: Path to the field (None for dataset-level suggestions)
            suggestion_type: Type of suggestion (description, tag, pii, etc.)
            suggested_value: The suggested value
            confidence: Confidence score (0.0-1.0)
        """
        self.dataset_urn = dataset_urn
        self.field_path = field_path
        self.suggestion_type = suggestion_type
        self.suggested_value = suggested_value
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert suggestion to dictionary format."""
        return {
            "dataset_urn": self.dataset_urn,
            "field_path": self.field_path,
            "suggestion_type": self.suggestion_type,
            "suggested_value": self.suggested_value,
            "confidence": self.confidence,
        }


class EnrichmentEngine:
    """
    Core engine for generating and managing metadata enrichment suggestions.

    This engine coordinates between the DataHub client and LLM service to
    fetch metadata, generate suggestions, and optionally apply them.
    """

    def __init__(self, config: EnricherConfig) -> None:
        """
        Initialize the enrichment engine.

        Args:
            config: Configuration for the enricher
        """
        self.config = config
        self.datahub_client = DataHubClient(
            gms_url=config.datahub_gms_url, gms_token=config.datahub_gms_token
        )
        self.llm_service = create_llm_service(config)
        logger.info(
            f"EnrichmentEngine initialized with backend: {self.llm_service.backend_name()}"
        )

    async def enrich_dataset(self, dataset_urn: str) -> List[EnrichmentSuggestion]:
        """
        Generate enrichment suggestions for a single dataset.

        Args:
            dataset_urn: URN of the dataset to enrich

        Returns:
            List of enrichment suggestions
        """
        logger.info(f"Enriching dataset: {dataset_urn}")

        # Fetch dataset metadata from DataHub
        dataset = await self.datahub_client.get_dataset_schema(dataset_urn)
        if not dataset:
            logger.warning(f"Dataset not found: {dataset_urn}")
            return []

        suggestions: List[EnrichmentSuggestion] = []

        # Extract schema information
        schema = dataset.get("schemaMetadata", {})
        fields = schema.get("fields", [])

        if not fields:
            logger.warning(f"No schema fields found for dataset: {dataset_urn}")
            return suggestions

        # Generate column descriptions
        if self.config.enable_column_descriptions:
            descriptions = await self.llm_service.generate_column_descriptions(
                dataset_name=dataset["name"], columns=fields
            )
            for field_path, description in descriptions.items():
                suggestions.append(
                    EnrichmentSuggestion(
                        dataset_urn=dataset_urn,
                        field_path=field_path,
                        suggestion_type="description",
                        suggested_value=description,
                    )
                )

        # Detect PII columns
        if self.config.enable_pii_detection:
            pii_columns = await self.llm_service.detect_pii_columns(
                dataset_name=dataset["name"], columns=fields
            )
            for field_path in pii_columns:
                suggestions.append(
                    EnrichmentSuggestion(
                        dataset_urn=dataset_urn,
                        field_path=field_path,
                        suggestion_type="tag",
                        suggested_value="PII",
                    )
                )

        # Suggest dataset-level tags
        if self.config.enable_tag_suggestions:
            tags = await self.llm_service.suggest_tags(
                dataset_name=dataset["name"],
                dataset_description=dataset.get("description", ""),
                columns=fields,
            )
            for tag in tags:
                suggestions.append(
                    EnrichmentSuggestion(
                        dataset_urn=dataset_urn,
                        field_path=None,
                        suggestion_type="tag",
                        suggested_value=tag,
                    )
                )

        logger.info(f"Generated {len(suggestions)} suggestions for {dataset_urn}")
        return suggestions

    async def enrich_datasets_batch(
        self, dataset_urns: List[str]
    ) -> Dict[str, List[EnrichmentSuggestion]]:
        """
        Generate enrichment suggestions for multiple datasets.

        Args:
            dataset_urns: List of dataset URNs to enrich

        Returns:
            Dictionary mapping dataset URNs to their suggestions
        """
        results: Dict[str, List[EnrichmentSuggestion]] = {}

        for dataset_urn in dataset_urns:
            try:
                suggestions = await self.enrich_dataset(dataset_urn)
                results[dataset_urn] = suggestions
            except Exception as e:
                logger.error(f"Failed to enrich dataset {dataset_urn}: {e}")
                results[dataset_urn] = []

        return results

    async def apply_suggestion(self, suggestion: EnrichmentSuggestion) -> bool:
        """
        Apply a suggestion to DataHub.

        Args:
            suggestion: The suggestion to apply

        Returns:
            True if successfully applied, False otherwise
        """
        try:
            if suggestion.suggestion_type == "description":
                return await self.datahub_client.update_column_description(
                    dataset_urn=suggestion.dataset_urn,
                    field_path=suggestion.field_path,
                    description=suggestion.suggested_value,
                )
            elif suggestion.suggestion_type == "tag":
                # TODO: Implement tag application
                logger.info(
                    f"Would apply tag {suggestion.suggested_value} to "
                    f"{suggestion.dataset_urn}/{suggestion.field_path}"
                )
                return True
            else:
                logger.warning(f"Unknown suggestion type: {suggestion.suggestion_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to apply suggestion: {e}")
            return False
