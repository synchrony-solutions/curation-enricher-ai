"""LLM service backend using Claude Code CLI for local execution."""

import asyncio
import json
import logging
import shutil
import subprocess
from typing import Any, Dict, List

from enricher.llm_base import LLMServiceBase

logger = logging.getLogger(__name__)


class ClaudeCodeLocalService(LLMServiceBase):
    """
    LLM service that uses the Claude Code CLI for local execution.

    Instead of calling the Anthropic API directly, this backend invokes the
    `claude` CLI in non-interactive mode (--print). This means:
    - No API key management needed (uses existing Claude Code auth)
    - Data stays local on the user's machine
    - Included in the user's Claude Pro/Team subscription
    - No per-token billing

    Requires: Claude Code CLI installed and authenticated (`claude` command available).
    """

    def __init__(self, claude_command: str = "claude", max_turns: int = 1) -> None:
        """
        Initialize the Claude Code local service.

        Args:
            claude_command: Path or name of the claude CLI binary
            max_turns: Maximum agentic turns per invocation (1 for single-shot)
        """
        self.claude_command = claude_command
        self.max_turns = max_turns

    async def _invoke_claude(self, prompt: str) -> str:
        """
        Invoke the Claude Code CLI with a prompt and return the response text.

        Args:
            prompt: The prompt to send to Claude Code

        Returns:
            The text content of Claude's response

        Raises:
            RuntimeError: If the CLI invocation fails
        """
        cmd = [
            self.claude_command,
            "--print",
            "--output-format", "json",
            "--max-turns", str(self.max_turns),
        ]

        logger.debug(f"Invoking Claude Code CLI: {' '.join(cmd)}")

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=120,
                ),
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code CLI timed out after 120 seconds")

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            raise RuntimeError(f"Claude Code CLI failed (exit {result.returncode}): {error_msg}")

        stdout = result.stdout.strip()
        if not stdout:
            raise RuntimeError("Claude Code CLI returned empty output")

        try:
            response_data = json.loads(stdout)
        except json.JSONDecodeError:
            # If the output is not valid JSON, treat the raw stdout as the response
            logger.debug("Claude Code output was not JSON, using raw text")
            return stdout

        # The --output-format json returns {"result": "...", ...}
        if isinstance(response_data, dict) and "result" in response_data:
            return response_data["result"]

        return stdout

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
        import re

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
            # Find the matching closing bracket
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

    async def generate_column_descriptions(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate descriptions for dataset columns using Claude Code CLI."""
        from enricher.prompts.column_description import build_column_description_prompt

        prompt = build_column_description_prompt(dataset_name, columns)
        response = await self._invoke_claude(prompt)

        try:
            parsed = self._extract_json_from_response(response)
            if isinstance(parsed, dict):
                logger.info(
                    f"Generated descriptions for {len(parsed)} columns in {dataset_name}"
                )
                return {str(k): str(v) for k, v in parsed.items()}
        except ValueError:
            logger.warning(f"Failed to parse column descriptions for {dataset_name}")

        return {}

    async def detect_pii_columns(
        self, dataset_name: str, columns: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect PII columns using Claude Code CLI."""
        from enricher.prompts.pii_detection import build_pii_detection_prompt

        prompt = build_pii_detection_prompt(dataset_name, columns)
        response = await self._invoke_claude(prompt)

        try:
            parsed = self._extract_json_from_response(response)
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

    async def suggest_tags(
        self, dataset_name: str, dataset_description: str, columns: List[Dict[str, Any]]
    ) -> List[str]:
        """Suggest tags using Claude Code CLI."""
        from enricher.prompts.tag_suggestion import build_tag_suggestion_prompt

        prompt = build_tag_suggestion_prompt(dataset_name, dataset_description, columns)
        response = await self._invoke_claude(prompt)

        try:
            parsed = self._extract_json_from_response(response)
            if isinstance(parsed, dict) and "suggested_tags" in parsed:
                tags = [item["tag"] for item in parsed["suggested_tags"]]
                logger.info(f"Suggested {len(tags)} tags for {dataset_name}")
                return tags
        except (ValueError, KeyError, TypeError):
            logger.warning(f"Failed to parse tag suggestions for {dataset_name}")

        return []

    async def check_connection(self) -> bool:
        """Verify that the Claude Code CLI is installed and authenticated."""
        if not shutil.which(self.claude_command):
            logger.error(f"Claude Code CLI not found: {self.claude_command}")
            return False

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    [self.claude_command, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                ),
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Claude Code CLI available: {version}")
                return True
            else:
                logger.error(f"Claude Code CLI check failed: {result.stderr}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("Claude Code CLI not available")
            return False

    def backend_name(self) -> str:
        """Return backend name."""
        return "Claude Code (local)"
