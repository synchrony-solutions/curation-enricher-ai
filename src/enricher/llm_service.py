"""LLM service for generating metadata enrichment suggestions using Claude."""

import logging
from typing import Any, Dict, List

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from enricher.config import EnricherConfig

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with Claude API to generate metadata suggestions.

    This service handles prompt construction, API calls, and response parsing
    for various enrichment tasks.
    """

    def __init__(self, config: EnricherConfig) -> None:
        """
        Initialize the LLM service.

        Args:
            config: Enricher configuration containing API keys and settings
        """
        self.config = config
        self.client = Anthropic(api_key=config.anthropic_api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_column_descriptions(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Generate descriptions for dataset columns using Claude.

        Args:
            dataset_name: Name of the dataset
            columns: List of column metadata (fieldPath, nativeDataType, etc.)

        Returns:
            Dictionary mapping column names to suggested descriptions
        """
        from enricher.prompts.column_description import build_column_description_prompt

        prompt = build_column_description_prompt(dataset_name, columns)

        response = self.client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse response and extract column descriptions
        # TODO: Implement proper response parsing
        logger.info(f"Generated descriptions for {len(columns)} columns in {dataset_name}")
        return {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def detect_pii_columns(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Detect columns that may contain PII or sensitive data.

        Args:
            dataset_name: Name of the dataset
            columns: List of column metadata

        Returns:
            List of column names that may contain PII
        """
        from enricher.prompts.pii_detection import build_pii_detection_prompt

        prompt = build_pii_detection_prompt(dataset_name, columns)

        response = self.client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse response and extract PII column names
        # TODO: Implement proper response parsing
        logger.info(f"Detected PII columns in {dataset_name}")
        return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def suggest_tags(
        self, dataset_name: str, dataset_description: str, columns: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Suggest relevant tags for a dataset.

        Args:
            dataset_name: Name of the dataset
            dataset_description: Description of the dataset
            columns: List of column metadata

        Returns:
            List of suggested tag names
        """
        from enricher.prompts.tag_suggestion import build_tag_suggestion_prompt

        prompt = build_tag_suggestion_prompt(dataset_name, dataset_description, columns)

        response = self.client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse response and extract suggested tags
        # TODO: Implement proper response parsing
        logger.info(f"Suggested tags for {dataset_name}")
        return []
