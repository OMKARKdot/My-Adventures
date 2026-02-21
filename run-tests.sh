#!/bin/bash

# Selenium Test Runner Script for My Adventures
# Usage: ./run-tests.sh [local|docker|compose]

set -e

MODE=${1:-compose}
BASE_URL=${2:-http://localhost:9090}

echo "🧪 My Adventures - Selenium Test Runner"
echo "======================================"
echo "Mode: $MODE"
echo "Base URL: $BASE_URL"
echo ""

case $MODE in
  local)
    echo "📦 Running tests locally..."
    echo "Installing dependencies..."
    pip install -r requirements.txt -q
    echo "Running tests..."
    BASE_URL=$BASE_URL HEADLESS=false python test.py
    ;;
    
  docker)
    echo "🐳 Building Docker image..."
    docker build -f Dockerfile.selenium -t my-adventures-selenium .
    echo "Running tests in Docker..."
    docker run --network=host \
      -e BASE_URL=$BASE_URL \
      -e HEADLESS=true \
      -v "$(pwd)/test-results:/test-results" \
      my-adventures-selenium
    ;;
    
  compose|*)
    echo "🐳 Running with Docker Compose..."
    echo "This will start both the web server and test runner..."
    echo ""
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
    echo ""
    echo "Cleaning up..."
    docker-compose -f docker-compose.test.yml down
    ;;
esac

echo ""
echo "✅ Test run complete!"
