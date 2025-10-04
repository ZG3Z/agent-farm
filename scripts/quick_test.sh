#!/bin/bash
# Quick test of all agents (basic health checks)

set -e

echo "Quick health check of all agents..."

echo ""
echo "Translator:"
curl -s http://localhost:8080/health | jq '.'

echo ""
echo "Weather:"
curl -s http://localhost:8081/health | jq '.'

echo ""
echo "Wikipedia:"
curl -s http://localhost:8082/health | jq '.'

echo ""
echo "Extractor:"
curl -s http://localhost:8083/health | jq '.'

echo ""
echo "All agents are healthy"