# DataHub AI Enricher

> An open-source DataHub plugin that uses LLMs to automatically suggest metadata enrichments for your data catalog.

Think of it like GitHub Copilot, but for documenting and governing your data warehouse instead of writing code.

## Features

- **Column Descriptions**: Automatically generate clear, concise descriptions for dataset columns
- **PII Detection**: Identify columns that may contain personally identifiable information
- **Tag Suggestions**: Recommend relevant tags based on dataset content and structure
- **DataHub Native**: Works seamlessly with your existing DataHub installation
- **LLM-Powered**: Uses Claude AI for intelligent metadata suggestions

## Quick Start

### Prerequisites

- Python 3.9 or higher
- DataHub instance (local or remote)
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/datahub-ai-enricher.git
cd datahub-ai-enricher
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Set up your environment:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

4. Start DataHub (if running locally):
```bash
docker-compose up -d
```

### Usage

#### Command Line Interface

Enrich a single dataset:
```bash
poetry run datahub-ai-enricher enrich "urn:li:dataset:(urn:li:dataPlatform:snowflake,mydb.schema.users,PROD)"
```

Enrich multiple datasets in batch:
```bash
poetry run datahub-ai-enricher batch --platform snowflake --limit 10
```

Test your connections:
```bash
poetry run datahub-ai-enricher test-connection
```

#### Python API

```python
import asyncio
from enricher import EnricherConfig, EnrichmentEngine

async def main():
    config = EnricherConfig()
    engine = EnrichmentEngine(config)

    # Enrich a dataset
    suggestions = await engine.enrich_dataset(dataset_urn)

    # Apply suggestions
    for suggestion in suggestions:
        await engine.apply_suggestion(suggestion)

asyncio.run(main())
```

## Configuration

Configuration can be provided via environment variables or a YAML file:

```yaml
# config.yml
datahub:
  gms_url: "http://localhost:8080"
  gms_token: "optional_access_token"

llm:
  api_key: "${ANTHROPIC_API_KEY}"
  model: "claude-sonnet-4-5-20250929"
  temperature: 0.7

features:
  enable_column_descriptions: true
  enable_pii_detection: true
  enable_tag_suggestions: true
```

See [examples/sample_config.yml](examples/sample_config.yml) for more options.

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
poetry install --with dev
```

2. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

3. Run tests:
```bash
poetry run pytest
```

4. Run linting:
```bash
poetry run ruff check src/
poetry run black src/
poetry run mypy src/
```

### Running DataHub Locally

The project includes a Docker Compose setup for running DataHub locally:

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f datahub-gms

# Stop services
docker-compose down
```

DataHub UI will be available at http://localhost:9002

### Project Structure

```
datahub-ai-enricher/
├── src/enricher/          # Main package
│   ├── config.py          # Configuration management
│   ├── datahub_client.py  # DataHub API client
│   ├── llm_service.py     # Claude API integration
│   ├── enrichment_engine.py  # Core enrichment logic
│   ├── cli.py             # Command-line interface
│   └── prompts/           # LLM prompt templates
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── examples/              # Example usage and configs
├── docker-compose.yml     # DataHub local setup
└── pyproject.toml        # Poetry configuration
```

## Architecture

The enricher follows a clean architecture pattern:

1. **DataHub Client**: Handles all interactions with the DataHub GraphQL API
2. **LLM Service**: Manages communication with the Claude API
3. **Enrichment Engine**: Orchestrates the enrichment workflow
4. **CLI**: Provides a user-friendly command-line interface

```
┌─────────────┐
│     CLI     │
└──────┬──────┘
       │
┌──────▼──────────────┐
│ Enrichment Engine   │
└──────┬──────┬───────┘
       │      │
┌──────▼──┐ ┌▼────────┐
│ DataHub │ │   LLM   │
│ Client  │ │ Service │
└─────────┘ └─────────┘
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Roadmap

### v0.1 (Current)
- ✅ Column description generation
- ✅ PII detection
- ✅ Tag suggestions
- ✅ CLI interface
- ✅ DataHub integration

### v0.2 (Planned)
- 🔜 Learning from user feedback
- 🔜 Custom prompt templates
- 🔜 Glossary term integration
- 🔜 Batch processing improvements

### Future
- 📋 Enterprise features (approval workflows, audit logs)
- 📋 Multi-platform support (Snowflake, Databricks)
- 📋 Custom model fine-tuning

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [DataHub](https://datahubproject.io/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- Inspired by the data community's need for better metadata management

## Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/datahub-ai-enricher/issues)
- 💬 [Discussions](https://github.com/yourusername/datahub-ai-enricher/discussions)

---

Made with ❤️ by the data community
