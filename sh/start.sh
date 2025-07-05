#!/bin/bash ./start.sh

echo "=== SearXNG Docker Setup with API ==="
echo "Starting services..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file with default values..."
    cat > .env << EOF
# SearXNG Configuration
SEARXNG_HOSTNAME=localhost
SEARXNG_TLS=internal
SEARXNG_UWSGI_WORKERS=4
SEARXNG_UWSGI_THREADS=4

# API Configuration
API_PORT=5001
VERIFY_SSL=false
MAX_RESULTS_LIMIT=50
REQUEST_TIMEOUT=30
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
EOF
fi

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

echo ""
echo "=== Service Status ==="
docker-compose ps

echo ""
echo "=== Access Information ==="
echo "SearXNG Web Interface: http://localhost"
echo "API Endpoints: http://localhost/api"
echo "API Health Check: http://localhost/api/health"
echo "API Documentation: http://localhost/api"
echo ""
echo "=== API Examples ==="
echo "General Search: curl 'http://localhost/api/search?q=python&mode=general'"
echo "Academic Search: curl 'http://localhost/api/search?q=machine+learning&mode=academic'"
echo "News Search: curl 'http://localhost/api/search?q=latest+news&mode=news'"
echo "Available Modes: curl 'http://localhost/api/modes'"
echo ""
echo "=== Container Logs ==="
echo "To view logs: docker-compose logs -f [service_name]"
echo "Services: caddy, redis, searxng, api"
echo ""
echo "=== Stopping Services ==="
echo "To stop: docker-compose down"
echo "To stop and remove volumes: docker-compose down -v" 