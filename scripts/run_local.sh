#!/bin/bash
# scripts/run_local.sh
# Build and start all agents locally

set -e

echo "=========================================="
echo "Starting Agent Farm - Local Environment"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# # Check required API keys
# if [ -z "$OPENAI_API_KEY" ] && [ -z "$OPENAI_API_KEY_TRANSLATOR" ]; then
#     echo "ERROR: OPENAI_API_KEY not set"
#     exit 1
# fi

# if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY_WEATHER" ]; then
#     echo "ERROR: ANTHROPIC_API_KEY not set"
#     exit 1
# fi

if [ -z "$GOOGLE_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY not set"
    exit 1
fi

if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo "ERROR: OPENWEATHER_API_KEY not"
    exit 1
fi

echo ""
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting agents..."
docker-compose up -d

echo ""
echo "Waiting for agents to be ready..."
sleep 15

echo ""
echo "Checking agent health..."
curl -s http://localhost:8080/health | jq '.' || echo "Translator not ready"
curl -s http://localhost:8081/health | jq '.' || echo "Weather not ready"
curl -s http://localhost:8082/health | jq '.' || echo "Wikipedia not ready"
curl -s http://localhost:8083/health | jq '.' || echo "Extractor not ready"

echo ""
echo "=========================================="
echo "All agents started successfully"
echo "=========================================="
echo ""
echo "Endpoints:"
echo "  Translator: http://localhost:8080"
echo "  Weather:    http://localhost:8081"
echo "  Wikipedia:  http://localhost:8082"
echo "  Extractor:  http://localhost:8083"
echo ""
echo "To view logs: docker-compose logs -f [service-name]"
echo "To stop: docker-compose down"
echo ""
