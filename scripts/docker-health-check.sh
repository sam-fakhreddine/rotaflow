#!/bin/bash
set -e

echo "🐳 Running Docker health check..."

# Cleanup any existing containers
docker stop health-test-container 2>/dev/null || true
docker rm health-test-container 2>/dev/null || true

# Build image
echo "Building Docker image..."
docker build -t schedule-manager:test . > /dev/null

# Start container on different port to avoid conflicts
echo "Starting container..."
docker run -d -p 6248:6247 --name health-test-container schedule-manager:test

# Wait for startup
echo "Waiting for startup..."
sleep 15

# Health check
echo "🔍 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:6248/health)
echo "Health response: $HEALTH_RESPONSE"

# Validate JSON structure
echo "$HEALTH_RESPONSE" | jq -e '.status == "healthy"'
echo "$HEALTH_RESPONSE" | jq -e 'has("checks") and has("timestamp") and has("version")'

# Test core endpoints
echo "🧪 Testing core functionality..."
curl -f http://localhost:6248/login > /dev/null
curl -f http://localhost:6248/calendar.ics > /dev/null

# Cleanup
echo "Cleaning up..."
docker stop health-test-container
docker rm health-test-container

echo "✅ Docker health check passed!"