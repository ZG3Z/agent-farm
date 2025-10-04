#!/bin/bash
# Run all tests

set -e

echo "=========================================="
echo "Running Agent Farm Tests"
echo "=========================================="

# Check if agents are running
echo ""
echo "Checking if agents are running..."
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "ERROR: Agents not running. Start them first with: ./scripts/run_local.sh"
    exit 1
fi

# Install test dependencies
echo ""
echo "Installing test dependencies..."
pip install -q pytest requests pyyaml

# Run unit tests
echo ""
echo "=========================================="
echo "Running Unit Tests"
echo "=========================================="

echo ""
echo "Testing Translator..."
pytest tests/unit/test_translator.py -v

echo ""
echo "Testing Weather..."
pytest tests/unit/test_weather.py -v

echo ""
echo "Testing Wikipedia..."
pytest tests/unit/test_wikipedia.py -v

echo ""
echo "Testing Extractor..."
pytest tests/unit/test_extractor.py -v

# Run integration tests
echo ""
echo "=========================================="
echo "Running Integration Tests"
echo "=========================================="

pytest tests/integration/test_a2a_communication.py -v

echo ""
echo "=========================================="
echo "All tests completed"
echo "=========================================="

