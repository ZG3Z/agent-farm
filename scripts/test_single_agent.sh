#!/bin/bash
# Test single agent
# Usage: ./scripts/test_single_agent.sh translator

if [ -z "$1" ]; then
    echo "Usage: $0 <agent-name>"
    echo "Available agents: translator, weather, wikipedia, extractor"
    exit 1
fi

AGENT=$1

case $AGENT in
    translator)
        pytest tests/unit/test_translator.py -v
        ;;
    weather)
        pytest tests/unit/test_weather.py -v
        ;;
    wikipedia)
        pytest tests/unit/test_wikipedia.py -v
        ;;
    extractor)
        pytest tests/unit/test_extractor.py -v
        ;;
    *)
        echo "Unknown agent: $AGENT"
        exit 1
        ;;
esac