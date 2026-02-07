# Getting Started with DataHub AI Enricher

This guide will walk you through setting up and using the DataHub AI Enricher for the first time.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** installed ([download here](https://www.python.org/downloads/))
- **Poetry** for dependency management ([install guide](https://python-poetry.org/docs/#installation))
- **Docker & Docker Compose** for running DataHub locally ([install guide](https://docs.docker.com/get-docker/))
- **Anthropic API key** ([get one here](https://console.anthropic.com/))

## Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/synchrony-solutions/curation-enricher-ai.git
cd curation-enricher-ai

# Install dependencies
make install-dev

# Or using poetry directly
poetry install --with dev
```

## Step 2: Set Up Environment

Create your environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Step 3: Start DataHub

Start all DataHub services using Docker Compose:

```bash
make docker-up

# Or using docker-compose directly
docker-compose up -d
```

Wait for all services to become healthy (this may take 2-3 minutes):

```bash
# Check service status
docker-compose ps

# Watch the logs
make docker-logs
```

DataHub will be available at:
- **UI**: http://localhost:9002
- **API**: http://localhost:8080

## Step 4: Verify Connections

Test that everything is connected properly:

```bash
make test-connection

# Or using the CLI directly
poetry run curation-enricher-ai test-connection
```

You should see:
```
🔗 Testing DataHub connection...
✅ DataHub connection successful (found X datasets)

🤖 Testing Claude API connection...
✅ Claude API initialized (model: claude-sonnet-4-5-20250929)

✨ All connections successful!
```

## Step 5: Add Sample Data (Optional)

If your DataHub instance is empty, you can ingest sample data:

```bash
# Install DataHub CLI
pip install acryl-datahub

# Ingest sample data
datahub docker ingest-sample-data
```

This will create some example datasets you can use to test the enricher.

## Step 6: Run Your First Enrichment

### Find a Dataset

First, list available datasets in DataHub:

```bash
# Using the DataHub UI
# Go to http://localhost:9002 and browse datasets

# Or using the API
curl http://localhost:8080/entities?action=search
```

### Enrich a Dataset

Copy the URN of a dataset and enrich it:

```bash
# Replace with an actual dataset URN from your DataHub instance
DATASET_URN="urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.users,PROD)"

poetry run curation-enricher-ai enrich "$DATASET_URN"
```

You'll see output like:

```
✨ Generated 12 suggestions:

1. [description] (field: email): Email address used for user account authentication and communication
2. [description] (field: first_name): User's given name as provided during registration
3. [tag] (field: email): PII
4. [tag]: customer_data
...
```

### Batch Enrich Multiple Datasets

To enrich multiple datasets at once:

```bash
poetry run curation-enricher-ai batch --limit 10

# Or filter by platform
poetry run curation-enricher-ai batch --platform snowflake --limit 5
```

## Step 7: Review and Apply Suggestions

By default, suggestions are only displayed, not applied. To apply suggestions automatically:

```bash
poetry run curation-enricher-ai enrich "$DATASET_URN" --apply
```

**⚠️ Warning**: The `--apply` flag will automatically update your DataHub metadata. Review suggestions first!

## Next Steps

### Customize Configuration

Edit your configuration in `.env` or create a YAML config:

```yaml
# config.yml
datahub:
  gms_url: "http://localhost:8080"

llm:
  temperature: 0.5  # Lower = more conservative suggestions
  max_tokens: 8192  # Higher = more detailed responses

features:
  enable_column_descriptions: true
  enable_pii_detection: true
  enable_tag_suggestions: false  # Disable if not needed
```

Use it with:

```bash
poetry run curation-enricher-ai enrich "$DATASET_URN" --config config.yml
```

### Integrate with Your Workflow

Add the enricher to your data pipeline:

```python
# In your Python code
import asyncio
from enricher import EnricherConfig, EnrichmentEngine

async def enrich_new_datasets():
    config = EnricherConfig()
    engine = EnrichmentEngine(config)

    # Get recently ingested datasets
    datasets = await engine.datahub_client.list_datasets(limit=50)

    # Enrich each one
    for dataset in datasets:
        suggestions = await engine.enrich_dataset(dataset['urn'])
        # Review and apply as needed
        for suggestion in suggestions:
            if suggestion.confidence > 0.8:
                await engine.apply_suggestion(suggestion)

asyncio.run(enrich_new_datasets())
```

### Run Tests

Verify everything works:

```bash
# Run unit tests
make test-unit

# Run integration tests (requires DataHub running)
make test-integration

# Check code quality
make lint
make type-check
```

## Troubleshooting

### DataHub Services Won't Start

Check Docker resources:
- Ensure Docker has at least 4GB RAM allocated
- Check disk space (DataHub needs ~2GB)
- View logs: `docker-compose logs datahub-gms`

### Connection Test Fails

**DataHub connection issues:**
- Verify services are running: `docker-compose ps`
- Check GMS health: `curl http://localhost:8080/health`
- Wait longer for services to become healthy

**Claude API issues:**
- Verify API key is correct in `.env`
- Check your Anthropic account has available credits
- Test the key at https://console.anthropic.com/

### No Datasets Found

If DataHub has no data:
```bash
datahub docker ingest-sample-data
```

Or ingest from your own sources using DataHub's ingestion framework.

### Import Errors

Make sure you're using the Poetry environment:
```bash
poetry shell  # Activate the virtual environment
# Or prefix commands with: poetry run
```

## Useful Commands

```bash
# Development
make help              # Show all available commands
make install-dev       # Install with dev dependencies
make format           # Format code
make test             # Run all tests

# Docker
make docker-up        # Start DataHub
make docker-down      # Stop DataHub
make docker-logs      # View logs
make docker-clean     # Remove all data and restart fresh

# Enrichment
make test-connection  # Verify setup
make enrich DATASET_URN="urn:..."  # Enrich a dataset
```

## Getting Help

- 📚 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/synchrony-solutions/curation-enricher-ai/issues)
- 💬 [Discussions](https://github.com/synchrony-solutions/curation-enricher-ai/discussions)
- 📖 [DataHub Docs](https://datahubproject.io/docs)

## What's Next?

Now that you're set up, check out:

1. [README.md](README.md) - Full feature documentation
2. [examples/](examples/) - More usage examples
3. [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

Happy enriching! 🚀
