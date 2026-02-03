#!/bin/bash

# 更新 Docker images

set -e

echo "Updating Docker images..."

docker pull ghcr.io/glanceapp/glance:latest
docker pull ghcr.io/gethomepage/homepage:latest

echo "✓ Images pulled successfully"

# 列出 images
echo ""
echo "Available images:"
docker images | grep -E 'glance|homepage'
SCRIPT

chmod +x scripts/build-all.sh