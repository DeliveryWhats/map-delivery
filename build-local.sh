#!/bin/bash

# Script para fazer build da imagem Docker localmente

# Configurações
IMAGE_NAME="sorrochey/store-coverage-api"
VERSION="latest"

echo "🐳 Building Docker image locally..."

# Build da imagem
docker build -t $IMAGE_NAME:$VERSION .

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "📦 Image: $IMAGE_NAME:$VERSION"
    echo ""
    echo "🚀 Ready to deploy with Docker Swarm!"
    echo "Use: docker stack deploy -c docker-compose.yml store-coverage-stack"
    echo ""
    echo "📋 Available images:"
    docker images | grep store-coverage-api
else
    echo "❌ Build failed"
fi
