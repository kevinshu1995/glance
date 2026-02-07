#!/bin/bash

# 健康檢查腳本

set -e

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

if ! check_service "Glance" "$GLANCE_URL"; then
    echo "ERROR: Glance health check failed"
    exit 1
fi

if ! check_service "Homepage" "$HOMEPAGE_URL"; then
    echo "ERROR: Homepage health check failed"
    exit 1
fi

# 所有檢查通過
echo "All health checks passed"
exit 0