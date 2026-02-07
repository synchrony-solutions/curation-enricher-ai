# DataHub AI Enricher - Project Context

## Project Overview

**Name:** DataHub AI Enricher (working title)

**Purpose:** An open-source DataHub plugin that uses LLMs to automatically suggest metadata enrichments for data catalogs, reducing manual data curation work.

**Core Value Proposition:** "Think of it like GitHub Copilot, but for documenting and governing your data warehouse instead of writing code."

**Target Users:** Data engineers, data stewards, analytics engineers, and data platform teams using DataHub for data cataloging.

**Business Context:** This is a 3-month MVP project to validate a SaaS business idea before expanding to paid managed services and platform marketplace apps (Snowflake, Databricks).

## Strategic Goals

### 3-Month Timeline Goals

1. **Week 1-4:** Foundation - Set up DataHub locally, customer discovery, technical spike
2. **Week 5-8:** Core Development - Build plugin scaffold and LLM integration
3. **Week 9-12:** Polish & Launch - Documentation, open source release, community engagement

### Success Metrics (3 Months)

- Plugin successfully installs on DataHub instances
- Processes 100+ datasets without errors
- Suggestion acceptance rate >40% from test users
- 10+ GitHub stars, 3+ active installations
- 5+ feedback conversations with users

### Post-MVP Monetization Path

1. **Months 4-9:** Managed service ($500-2k/month)
2. **Months 10-15:** Enterprise features (organizational learning, governance workflows)
3. **Months 16-24:** Snowflake Native App expansion

## Technical Architecture

### Core Technology Stack

```yaml
Language: Python 3.10+
Primary Dependencies:
  - acryl-datahub (DataHub SDK)
  - anthropic (Claude API)
  - pydantic (data validation)
  
Development Tools:
  - poetry (dependency management)
  - pytest (testing)
  - black/ruff (linting/formatting)
  - pre-commit (git hooks)
  
Infrastructure:
  - Docker (local development)
  - GitHub Actions (CI/CD)
  - PyPI (distribution)
```

### Architecture Pattern

The plugin will be implemented as a **DataHub ingestion source** that:

1. Connects to DataHub via GraphQL API
2. Fetches schema metadata for datasets
3. Calls Claude API to generate enrichment suggestions
4. Returns enriched metadata to DataHub for review/application

### Key Components

```text
curation-enricher-ai/
├── src/
│   ├── enricher/
│   │   ├── __init__.py
│   │   ├── datahub_client.py      # DataHub API interactions
│   │   ├── llm_service.py         # Claude API integration
│   │   ├── enrichment_engine.py   # Core suggestion logic
│   │   └── config.py              # Configuration management
│   ├── prompts/
│   │   ├── column_description.py  # Prompt templates
│   │   ├── pii_detection.py
│   │   └── tag_suggestion.py
│   └── cli.py                     # Command-line interface
├── tests/
├── examples/
│   └── sample_config.yml
├── pyproject.toml
├── README.md
└── claude.md                      # This file
```

## Feature Scope

### Must Have (v0.1 - 3 Month MVP)

- ✅ Generate column descriptions from schema metadata
- ✅ Suggest PII/sensitive data tags
- ✅ Configuration via YAML
- ✅ Works as DataHub ingestion source
- ✅ CLI interface for standalone use

### Nice to Have (v0.2 - Post Launch)

- 🔜 Learn from accepted/rejected suggestions
- 🔜 Custom prompt templates per organization
- 🔜 Integration with existing glossary terms
- 🔜 Batch processing of multiple datasets

### Explicitly Out of Scope

- ❌ Automatic application of suggestions (always require review)
- ❌ Data quality rule generation (too complex for MVP)
- ❌ Lineage inference
- ❌ Cross-platform support (just DataHub for now)

## Business Context

### Target Market

- **Primary:** Companies using DataHub (open source or Acryl managed)
- **Size:** Mid-market to enterprise (100-10,000 employees)
- **Use Case:** Teams struggling to keep data catalogs documented and maintained

### Competitive Landscape

- **Direct:** Atlan AI descriptions, Monte Carlo suggestions
- **Adjacent:** Alation, Collibra (enterprise catalogs)
- **Differentiation:** Open source, LLM-powered, learns from user patterns

### Monetization Strategy (Post-MVP)

1. **Free Tier:** Open source DataHub plugin (lead generation)
2. **Managed Service:** $500-2k/month (hosted plugin)
3. **Enterprise:** $5-15k/month (custom models, governance workflows)
4. **Platform Apps:** Snowflake/Databricks marketplace (different revenue model)

## Key Design Decisions

### Why DataHub First?

- No marketplace approval process (open source)
- Fast iteration and deployment
- Python-based with good documentation
- Active community for feedback
- Learnings transfer to paid platforms later

### Why Claude API?

- Best-in-class reasoning for metadata understanding
- Strong context window for complex schemas
- Anthropic credits available (developer advantage)
- Can swap providers later via abstraction

### Why Free and Open Source?

- Builds credibility and portfolio
- Generates inbound leads for paid services
- Community feedback improves product
- Lowers customer acquisition cost

## Development Conventions

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Docstrings for all public functions (Google style)
- Maximum line length: 100 characters
- Prefer composition over inheritance

### Testing Standards

- Minimum 80% code coverage
- Unit tests for all business logic
- Integration tests for DataHub/API interactions
- Mock external API calls in tests
- Use pytest fixtures for common test data

### Git Workflow

- Main branch is production-ready
- Feature branches: `feature/description`
- Commit messages: Conventional Commits format
- PRs require tests and documentation

### Configuration Management

- All secrets via environment variables
- Sample configs with placeholder values
- Validate config at startup with clear error messages
- Support both YAML files and env vars

## Important Context from Founders

### About Newt (Technical Lead)

- Senior Software Engineer at RTI International
- Expertise: AWS, Terraform, Kubernetes, DevOps, AI/ML
- Works on healthcare research platforms (FISMA-compliant)
- Experience with data pipelines, EHR systems, data lakes

### About Jacob (Business Lead)

- Co-founder of Synchrony Solutions LLC
- Focus: Customer discovery, documentation, go-to-market
- Will handle interviews, launch marketing, community engagement

### Team Capacity

- 15-20 hours/week for 3 months
- Split: Newt (technical) + Jacob (customer/docs)
- Weekday evenings (2-3 hours) + weekends (5-8 hours)

## Customer Discovery Insights

### Key Pain Points Identified

1. Manual documentation takes too long (hours per dataset)
2. Repetitive work across similar schemas
3. PII/sensitive data often not tagged properly
4. New datasets never get documented
5. No consistency in naming/tagging conventions

### What Users Will Pay For

- Removing operational burden (hosting)
- Learning from their specific patterns
- Governance workflows (approval, audit logs)
- Integration with their existing tools
- Compliance features (SOC2, HIPAA)

## Integration Requirements

### DataHub API Usage

- GraphQL endpoint for metadata queries
- Authentication via personal access tokens
- Entity model: datasets, schemas, columns
- Aspects: schemaMetadata, glossaryTerms, tags, ownership

### Claude API Usage

- Use Claude Sonnet 4.5 for cost/performance balance
- Implement retry logic with exponential backoff
- Track token usage for cost monitoring
- Consider caching for repeated schema patterns

### External Dependencies

- Keep dependencies minimal
- Pin versions for reproducibility
- Document any system requirements
- Provide Docker container for easy setup

## Documentation Standards

### README Must Include

- Clear description and value proposition
- Installation instructions (pip, Docker)
- Quick start guide with examples
- Configuration reference
- Troubleshooting section
- Contributing guidelines
- License (Apache 2.0)

### Code Documentation

- Module-level docstrings explaining purpose
- Function docstrings with Args/Returns/Raises
- Inline comments for complex logic only
- Examples in docstrings where helpful

## Future Considerations

### Scaling to Managed Service

- Multi-tenancy architecture from day 1
- Usage tracking and metrics built in
- Customer isolation at data layer
- Billing integration placeholder

### Platform Expansion

- Abstract DataHub-specific code
- Design for pluggable platform adapters
- Reusable LLM prompt library
- Common metadata model across platforms

### Enterprise Features

- Organizational learning (custom models)
- Approval workflows before applying suggestions
- Audit logs for compliance
- Integration with governance tools
- Custom prompt templates

## Resources and Links

### Documentation

- DataHub Docs: <https://datahubproject.io/docs>
- DataHub GitHub: <https://github.com/datahub-project/datahub>
- Anthropic Docs: <https://docs.anthropic.com>
- DataHub Slack: datahubproject.slack.com

### Inspiration

- DataHub Community Plugins: <https://github.com/datahub-project/datahub/tree/master/metadata-ingestion/src/datahub/ingestion/source>
- Example transformer: Great Expectations integration

### Competitors to Study

- Atlan: AI-assisted cataloging
- Monte Carlo: Data quality suggestions
- Alation: Enterprise catalog with AI features

## Current Status

**Phase:** Planning complete, ready to begin Week 1 of development

**Next Actions:**

1. Set up local DataHub instance with Docker
2. Create GitHub repository: `curation-enricher-ai`
3. Initialize Python project with poetry
4. Schedule 2 customer discovery calls
5. Test DataHub GraphQL API queries
6. Test Claude API with sample schema data

---

**Last Updated:** February 7, 2026
**Version:** 0.1-planning
**Contact:** Newt (Technical) + Jacob (Business)
