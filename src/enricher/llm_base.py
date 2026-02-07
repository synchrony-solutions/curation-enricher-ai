"""Abstract base class for LLM service backends."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMServiceBase(ABC):
    """
    Abstract base class for LLM service implementations.

    Subclasses must implement the three core enrichment methods.
    This enables swapping between Claude Code (local) and Anthropic API backends.
    """

    @abstractmethod
    async def generate_column_descriptions(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Generate descriptions for dataset columns.

        Args:
            dataset_name: Name of the dataset
            columns: List of column metadata (fieldPath, nativeDataType, etc.)

        Returns:
            Dictionary mapping column names to suggested descriptions
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def check_connection(self) -> bool:
        """
        Verify that the LLM backend is available and configured.

        Returns:
            True if the backend is reachable, False otherwise
        """
        ...

    @abstractmethod
    def backend_name(self) -> str:
        """Return a human-readable name for this backend."""
        ...
