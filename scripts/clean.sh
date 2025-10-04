#!/bin/bash
# Clean up Docker resources

echo "Cleaning up Docker resources..."
docker-compose down -v --remove-orphans
docker system prune -f

echo "Cleanup completed"