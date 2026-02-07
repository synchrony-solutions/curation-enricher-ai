"""Command-line interface for the DataHub AI Enricher."""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from enricher.config import EnricherConfig
from enricher.enrichment_engine import EnrichmentEngine

# Load environment variables
load_dotenv()


def setup_logging(log_level: str) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """
    DataHub AI Enricher - Automatically suggest metadata enrichments for your data catalog.

    Use this CLI to generate AI-powered suggestions for column descriptions,
    PII detection, and tag recommendations for your DataHub datasets.
    """
    pass


@main.command()
@click.argument("dataset_urn")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option("--apply", is_flag=True, help="Automatically apply suggestions (use with caution)")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for suggestions")
def enrich(
    dataset_urn: str, config: Optional[Path], apply: bool, output: Optional[Path]
) -> None:
    """
    Generate enrichment suggestions for a dataset.

    DATASET_URN: The URN of the dataset to enrich (e.g., urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.table,PROD))
    """
    try:
        # Load configuration
        enricher_config = EnricherConfig()
        setup_logging(enricher_config.log_level)
        logger = logging.getLogger(__name__)

        logger.info(f"Enriching dataset: {dataset_urn}")

        # Run enrichment
        engine = EnrichmentEngine(enricher_config)
        suggestions = asyncio.run(engine.enrich_dataset(dataset_urn))

        # Display suggestions
        click.echo(f"\n✨ Generated {len(suggestions)} suggestions:\n")
        for i, suggestion in enumerate(suggestions, 1):
            field_info = f" (field: {suggestion.field_path})" if suggestion.field_path else ""
            click.echo(
                f"{i}. [{suggestion.suggestion_type}]{field_info}: {suggestion.suggested_value}"
            )

        # Apply suggestions if requested
        if apply:
            click.echo("\n📝 Applying suggestions...")
            for suggestion in suggestions:
                success = asyncio.run(engine.apply_suggestion(suggestion))
                status = "✅" if success else "❌"
                click.echo(f"{status} Applied {suggestion.suggestion_type} suggestion")

        # Save to file if requested
        if output:
            output_data = [s.to_dict() for s in suggestions]
            output.write_text(json.dumps(output_data, indent=2))
            click.echo(f"\n💾 Saved suggestions to {output}")

    except Exception as e:
        logger.error(f"Enrichment failed: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--platform",
    "-p",
    help="Filter by platform (e.g., snowflake, postgres)",
)
@click.option(
    "--limit",
    "-l",
    default=10,
    help="Maximum number of datasets to enrich",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for results")
def batch(
    platform: Optional[str], limit: int, config: Optional[Path], output: Optional[Path]
) -> None:
    """
    Enrich multiple datasets in batch mode.

    Fetches datasets from DataHub and generates suggestions for each.
    """
    try:
        # Load configuration
        enricher_config = EnricherConfig()
        setup_logging(enricher_config.log_level)
        logger = logging.getLogger(__name__)

        logger.info(f"Starting batch enrichment (limit: {limit})")

        # Initialize engine
        engine = EnrichmentEngine(enricher_config)

        # Fetch datasets
        click.echo("📚 Fetching datasets from DataHub...")
        datasets = asyncio.run(engine.datahub_client.list_datasets(platform=platform, limit=limit))
        click.echo(f"Found {len(datasets)} datasets\n")

        # Enrich each dataset
        all_results = {}
        with click.progressbar(datasets, label="Enriching datasets") as bar:
            for dataset in bar:
                dataset_urn = dataset["urn"]
                suggestions = asyncio.run(engine.enrich_dataset(dataset_urn))
                all_results[dataset_urn] = [s.to_dict() for s in suggestions]

        # Display summary
        total_suggestions = sum(len(suggestions) for suggestions in all_results.values())
        click.echo(f"\n✨ Generated {total_suggestions} total suggestions")

        # Save to file if requested
        if output:
            output.write_text(json.dumps(all_results, indent=2))
            click.echo(f"💾 Saved results to {output}")

    except Exception as e:
        logger.error(f"Batch enrichment failed: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def test_connection() -> None:
    """Test connection to DataHub and Claude API."""
    try:
        enricher_config = EnricherConfig()
        setup_logging(enricher_config.log_level)
        logger = logging.getLogger(__name__)

        # Test DataHub connection
        click.echo("🔗 Testing DataHub connection...")
        from enricher.datahub_client import DataHubClient

        client = DataHubClient(
            gms_url=enricher_config.datahub_gms_url, gms_token=enricher_config.datahub_gms_token
        )
        datasets = asyncio.run(client.list_datasets(limit=1))
        click.echo(f"✅ DataHub connection successful (found {len(datasets)} datasets)")

        # Test Claude API connection
        click.echo("\n🤖 Testing Claude API connection...")
        from enricher.llm_service import LLMService

        llm_service = LLMService(enricher_config)
        click.echo(f"✅ Claude API initialized (model: {enricher_config.llm_model})")

        click.echo("\n✨ All connections successful!")

    except Exception as e:
        logger.error(f"Connection test failed: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
