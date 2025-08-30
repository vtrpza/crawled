#!/bin/bash

echo "🧹 Cleaning up Docker mess..."

# Stop all containers
echo "📍 Stopping all containers..."
docker-compose down --remove-orphans

# Remove all stopped containers
echo "🗑️ Removing stopped containers..."
docker container prune -f

# Remove corrupted containers specifically
echo "💀 Force removing corrupted containers..."
docker rm -f $(docker ps -aq) 2>/dev/null || true

# Clean up volumes
echo "📦 Cleaning volumes..."
docker volume prune -f

# Clean up networks
echo "🌐 Cleaning networks..."
docker network prune -f

# Remove images to force rebuild
echo "🏗️ Removing images for fresh rebuild..."
docker rmi $(docker images -q) -f 2>/dev/null || true

# Clean system
echo "🧽 Deep system cleanup..."
docker system prune -af --volumes

# Restart Docker daemon (if possible)
echo "🔄 Restarting Docker service..."
sudo systemctl restart docker 2>/dev/null || echo "⚠️ Cannot restart Docker service - continue manually"

sleep 5

# Rebuild everything from scratch
echo "🚀 Rebuilding everything from scratch..."
docker-compose build --no-cache

# Start services
echo "▶️ Starting services..."
docker-compose up -d

echo "✅ Cleanup complete! Services should be running fresh."
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"

# Show status
docker-compose ps