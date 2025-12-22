#!/bin/bash
set -e

echo "🐳 Building Docker image with new chat interface..."

# Build the Docker image
docker build -t litellm-gateway:latest .

echo "✅ Docker image built successfully!"
echo ""
echo "To run the container:"
echo "  docker run -p 8080:8080 --env-file .env litellm-gateway:latest"
echo ""
echo "Or use docker-compose if you have it configured."
