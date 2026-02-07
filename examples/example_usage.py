"""Example usage of the DataHub AI Enricher."""

import asyncio
import os

from enricher import EnricherConfig, EnrichmentEngine


async def main() -> None:
    """Run example enrichment workflow."""
    # Load configuration from environment
    config = EnricherConfig()

    # Initialize the enrichment engine
    engine = EnrichmentEngine(config)

    # Example 1: Enrich a single dataset
    print("Example 1: Enriching a single dataset")
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
    # Ensure required environment variables are set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY=your_key_here")
        exit(1)

    asyncio.run(main())
