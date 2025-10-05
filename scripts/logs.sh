#!/bin/bash
# View logs for specific agent or all
# Usage: ./scripts/logs.sh [agent-name]

if [ -z "$1" ]; then
    echo "Showing logs for all agents..."
    docker-compose logs -f
else
    echo "Showing logs for $1..."
    docker-compose logs -f $1
fi