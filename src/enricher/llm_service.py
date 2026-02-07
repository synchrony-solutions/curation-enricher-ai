"""LLM service backend using the Anthropic API (cloud)."""

import json
import logging
import re
from typing import Any, Dict, List

from tenacity import retry, stop_after_attempt, wait_exponential

from enricher.config import EnricherConfig
from enricher.llm_base import LLMServiceBase

logger = logging.getLogger(__name__)


class AnthropicAPIService(LLMServiceBase):
    """
    LLM service that calls the Anthropic API directly.

    This is the cloud backend for managed/enterprise deployments where
    an Anthropic API key is available. Useful for:
    - Managed service tier (controlled billing)
    - CI/CD pipelines without Claude Code installed
    - Environments where the Claude Code CLI is unavailable
    """

    def __init__(self, config: EnricherConfig) -> None:
        """
        Initialize the Anthropic API service.

        Args:
            config: Enricher configuration containing API key and model settings

        Raises:
            ImportError: If the anthropic package is not installed
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required for the API backend. "
                "Install it with: pip install 'curation-enricher-ai[api]'"
            )

        if not config.anthropic_api_key:
            raise ValueError(
                "anthropic_api_key is required for the API backend. "
                "Set ENRICHER_ANTHROPIC_API_KEY or use llm_backend='claude-code' instead."
            )

        self.config = config
        self.client = Anthropic(api_key=config.anthropic_api_key)

    def _extract_json_from_response(self, text: str) -> Any:
        """
        Extract JSON from a Claude response that may contain markdown fences.

        Args:
            text: Raw response text from Claude

        Returns:
            Parsed JSON object
        """
        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Look for JSON inside markdown code fences
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try to find JSON object or array in the text
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            if start == -1:
                continue
            depth = 0
            for i, char in enumerate(text[start:], start):
                if char == start_char:
                    depth += 1
                elif char == end_char:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start : i + 1])
                        except json.JSONDecodeError:
                            break

        raise ValueError(f"Could not extract JSON from response: {text[:200]}...")

    def _get_response_text(self, response: Any) -> str:
        """Extract text content from an Anthropic API response."""
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_column_descriptions(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate descriptions for dataset columns using the Anthropic API."""
        from enricher.prompts.column_description import build_column_description_prompt

        prompt = build_column_description_prompt(dataset_name, columns)

        response = self.client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        text = self._get_response_text(response)
        try:
            parsed = self._extract_json_from_response(text)
            if isinstance(parsed, dict):
                logger.info(
                    f"Generated descriptions for {len(parsed)} columns in {dataset_name}"
                )
                return {str(k): str(v) for k, v in parsed.items()}
        except ValueError:
            logger.warning(f"Failed to parse column descriptions for {dataset_name}")

        return {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def detect_pii_columns(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect PII columns using the Anthropic API."""
        from enricher.prompts.pii_detection import build_pii_detection_prompt

        prompt = build_pii_detection_prompt(dataset_name, columns)

        response = self.client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        text = self._get_response_text(response)
        try:
            parsed = self._extract_json_from_response(text)
            if isinstance(parsed, dict) and "pii_columns" in parsed:
                pii_fields = [
                    item["field_path"]
                    for item in parsed["pii_columns"]
                    if item.get("confidence") in ("high", "medium")
                ]
                logger.info(f"Detected {len(pii_fields)} PII columns in {dataset_name}")
                return pii_fields
        except (ValueError, KeyError, TypeError):
            logger.warning(f"Failed to parse PII detection for {dataset_name}")

        return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def suggest_tags(
        self, dataset_name: str, dataset_description: str, columns: List[Dict[str, Any]]
    ) -> List[str]:
        """Suggest tags using the Anthropic API."""
        from enricher.prompts.tag_suggestion import build_tag_suggestion_prompt

        prompt = build_tag_suggestion_prompt(dataset_name, dataset_description, columns)

        response = self.client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        text = self._get_response_text(response)
        try:
            parsed = self._extract_json_from_response(text)
            if isinstance(parsed, dict) and "suggested_tags" in parsed:
                tags = [item["tag"] for item in parsed["suggested_tags"]]
                logger.info(f"Suggested {len(tags)} tags for {dataset_name}")
                return tags
        except (ValueError, KeyError, TypeError):
            logger.warning(f"Failed to parse tag suggestions for {dataset_name}")

        return []

    async def check_connection(self) -> bool:
        """Verify that the Anthropic API key is valid."""
        try:
            self.client.messages.create(
                model=self.config.llm_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'ok'"}],
            )
            logger.info(f"Anthropic API connection verified (model: {self.config.llm_model})")
            return True
        except Exception as e:
            logger.error(f"Anthropic API connection failed: {e}")
            return False

    def backend_name(self) -> str:
        """Return backend name."""
        return f"Anthropic API ({self.config.llm_model})"


# Backwards-compatible alias
LLMService = AnthropicAPIService
