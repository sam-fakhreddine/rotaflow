#!/bin/bash
set -e

echo "🐳 Running Docker health check..."

# Build image
docker build -t schedule-manager:test . > /dev/null 2>&1

# Start container
docker run -d -p 6247:6247 --name health-test-container schedule-manager:test > /dev/null 2>&1

# Wait for startup
sleep 10

# Health check
echo "🔍 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:6247/health)

# Validate JSON structure
echo "$HEALTH_RESPONSE" | jq -e '.status == "healthy"' > /dev/null
echo "$HEALTH_RESPONSE" | jq -e 'has("checks") and has("timestamp") and has("version")' > /dev/null

# Test core endpoints
echo "🧪 Testing core functionality..."
curl -f http://localhost:6247/login > /dev/null 2>&1
curl -f http://localhost:6247/calendar.ics > /dev/null 2>&1

# Cleanup
docker stop health-test-container > /dev/null 2>&1
docker rm health-test-container > /dev/null 2>&1

echo "✅ Docker health check passed!"