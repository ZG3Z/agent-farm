#!/bin/bash

set -e

AGENTS_DIR="agents"
OUTPUT_FILE="agents-matrix.json"

# Find all directories with Dockerfile
agents=()
for dir in "$AGENTS_DIR"/*/ ; do
    agent_name=$(basename "$dir")  
    agents+=("$agent_name")
done

# Generate JSON array
printf -v agents_json '"%s",' "${agents[@]}"
agents_json="[${agents_json%,}]"

# Output for GitHub Actions
echo "{\"agent\": $agents_json}"

# Save to file if needed
echo "{\"agent\": $agents_json}" > "$OUTPUT_FILE"