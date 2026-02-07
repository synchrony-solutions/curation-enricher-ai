# Contributing to DataHub AI Enricher

Thank you for your interest in contributing to DataHub AI Enricher! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and collaborative. We're all here to make data cataloging better.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/synchrony-solutions/curation-enricher-ai.git
   cd curation-enricher-ai
   ```
3. Install dependencies:
   ```bash
   poetry install --with dev
   ```
4. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards (see below)

3. Write or update tests for your changes

4. Run the test suite:
   ```bash
   poetry run pytest
   ```

5. Run linting and formatting:
   ```bash
   poetry run ruff check src/ tests/
   poetry run black src/ tests/
   poetry run mypy src/
   ```

6. Commit your changes with a clear message:
   ```bash
   git commit -m "Add feature: description of what you did"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Open a Pull Request on GitHub

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use Black for code formatting
- Use Ruff for linting

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    More detailed explanation if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Testing

- Aim for 80%+ code coverage
- Write unit tests for business logic
- Write integration tests for external dependencies
- Use descriptive test names that explain what is being tested
- Mock external API calls in unit tests

### Commit Messages

Follow the Conventional Commits format:

- `feat: add new feature`
- `fix: resolve bug in XYZ`
- `docs: update README`
- `test: add tests for ABC`
- `refactor: improve code structure`
- `chore: update dependencies`

## Pull Request Process

1. Update the README.md or documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the CHANGELOG.md (if applicable)
5. Request review from maintainers

### PR Guidelines

- Keep PRs focused on a single feature or fix
- Include a clear description of what changed and why
- Reference any related issues
- Be responsive to feedback

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/enricher

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests
poetry run pytest tests/integration/
```

### Writing Tests

Place tests in the appropriate directory:
- `tests/unit/` - Unit tests (fast, isolated)
- `tests/integration/` - Integration tests (require external services)

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Keep documentation clear and concise

## Questions?

If you have questions or need help:
- Open a GitHub Discussion
- Check existing issues and PRs
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
