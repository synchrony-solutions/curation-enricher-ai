#!/bin/bash
# Quick setup script for DataHub AI Enricher

set -e

echo "🚀 Setting up DataHub AI Enricher..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies
echo "📦 Installing Python dependencies..."
poetry install --with dev

# Setup environment
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
poetry run pre-commit install

# Check Docker
echo "🐳 Checking Docker services..."
if docker compose ps | grep -q "datahub"; then
    echo "✅ DataHub services are already running"
else
    echo "📚 Starting DataHub services (this may take a few minutes)..."
    docker compose up -d
    echo "⏳ Waiting for services to become healthy..."
    sleep 30
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Wait for DataHub to fully start (check: docker compose ps)"
echo "3. Test the connection: make test-connection"
echo "4. Read GETTING_STARTED.md for more details"
echo ""
echo "Useful commands:"
echo "  make docker-up     # Start DataHub"
echo "  make docker-logs   # View DataHub logs"
echo "  make test          # Run tests"
echo "  make help          # Show all commands"
