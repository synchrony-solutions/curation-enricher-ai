"""Example usage of the DataHub AI Enricher."""

import asyncio
import shutil

from enricher import EnricherConfig, EnrichmentEngine


async def main() -> None:
    """Run example enrichment workflow."""
    # Load configuration from environment.
    # By default, uses the "claude-code" backend (local Claude Code CLI).
    # No API key needed -- just have `claude` installed and authenticated.
    config = EnricherConfig()

    # Or, to explicitly use the Anthropic API backend:
    # config = EnricherConfig(llm_backend="anthropic-api", anthropic_api_key="sk-ant-...")

    # Initialize the enrichment engine
    engine = EnrichmentEngine(config)
    print(f"Using LLM backend: {engine.llm_service.backend_name()}")

    # Example 1: Enrich a single dataset
    print("\nExample 1: Enriching a single dataset")
    dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.users,PROD)"
    suggestions = await engine.enrich_dataset(dataset_urn)

    print(f"Generated {len(suggestions)} suggestions:")
    for suggestion in suggestions:
        print(f"  - {suggestion.suggestion_type}: {suggestion.suggested_value}")

    # Example 2: Batch enrich multiple datasets
    print("\nExample 2: Batch enriching datasets")
    dataset_urns = [
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.users,PROD)",
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.orders,PROD)",
    ]
    results = await engine.enrich_datasets_batch(dataset_urns)

    for urn, suggestions in results.items():
        print(f"\n{urn}: {len(suggestions)} suggestions")

    # Example 3: Apply a suggestion
    print("\nExample 3: Applying a suggestion")
    if suggestions:
        first_suggestion = suggestions[0]
        success = await engine.apply_suggestion(first_suggestion)
        print(f"Applied suggestion: {success}")


if __name__ == "__main__":
    # Check that Claude Code CLI is available (for the default backend)
    if not shutil.which("claude"):
        print("Warning: 'claude' CLI not found in PATH.")
        print("Install Claude Code: https://docs.anthropic.com/en/docs/claude-code")
        print("Or switch to the API backend: ENRICHER_LLM_BACKEND=anthropic-api")

    asyncio.run(main())
