#!/bin/bash

# 健康檢查腳本

echo "Checking service health..."

GLANCE_URL="http://localhost:8081"
HOMEPAGE_URL="http://localhost:8080"

check_service() {
    local service=$1
    local url=$2
    local max_retries=5
    local retry=0

    while [ $retry -lt $max_retries ]; do
        if curl -sf $url > /dev/null 2>&1; then
            echo "✓ $service is running"
            return 0
        fi
        retry=$((retry + 1))
        echo "  Attempt $retry/$max_retries - waiting for $service..."
        sleep 5
    done

    echo "✗ $service failed health check"
    return 1
}

check_service "Glance" "$GLANCE_URL"
check_service "Homepage" "$HOMEPAGE_URL"