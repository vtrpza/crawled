#!/bin/bash

# Crawl4AI Database Setup Script
# This script sets up the PostgreSQL database for development

set -e  # Exit on any error

echo "=== Crawl4AI Database Setup ==="
echo

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "Error: docker-compose is not installed."
    exit 1
fi

echo "Starting PostgreSQL and Redis containers..."
docker-compose -f docker-compose.dev.yml up -d

echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U crawl4ai_user -d crawl4ai >/dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Check if PostgreSQL is ready
if ! docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U crawl4ai_user -d crawl4ai >/dev/null 2>&1; then
    echo "Error: PostgreSQL is not ready after 60 seconds"
    exit 1
fi

echo "Database containers are running!"
echo

# Show connection info
echo "=== Database Connection Info ==="
echo "Host: localhost"
echo "Port: 5432"
echo "Database: crawl4ai"
echo "Username: crawl4ai_user"
echo "Password: crawl4ai_password"
echo
echo "Redis: localhost:6379"
echo

# Test the connection using Python
echo "Testing database connection..."
if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://crawl4ai_user:crawl4ai_password@localhost:5432/crawl4ai')
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    version = cursor.fetchone()[0]
    print(f'✓ Connection successful!')
    print(f'  PostgreSQL version: {version}')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
    exit(1)
"; then
    echo "✓ Database connection test passed!"
else
    echo "✗ Database connection test failed!"
    exit 1
fi

echo
echo "=== Setup Complete ==="
echo
echo "Your database is ready! You can now:"
echo "1. Start the API server: python api_server.py"
echo "2. Check database status: docker-compose -f docker-compose.dev.yml ps"
echo "3. View database logs: docker-compose -f docker-compose.dev.yml logs postgres"
echo "4. Stop containers: docker-compose -f docker-compose.dev.yml down"
echo
echo "Environment variables (add to .env if needed):"
echo "DATABASE_URL=postgresql://crawl4ai_user:crawl4ai_password@localhost:5432/crawl4ai"
echo "REDIS_URL=redis://localhost:6379/0"