#!/bin/bash

# SearXNG Docker Deployment Script
# This script deploys SearXNG with API wrapper using Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="searxng-docker"
COMPOSE_FILE="docker-compose.yaml"
ENV_FILE=".env"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to check environment file
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found. Creating default one..."
        cat > "$ENV_FILE" << EOF
# SearXNG Configuration
SEARXNG_HOSTNAME=search.nexalexica.com
SEARXNG_TLS=internal
SEARXNG_BASE_URL=https://search.nexalexica.com/

# SearXNG Performance Settings
SEARXNG_UWSGI_WORKERS=4
SEARXNG_UWSGI_THREADS=4

# API Configuration
API_PORT=5001
VERIFY_SSL=false
MAX_RESULTS_LIMIT=20
REQUEST_TIMEOUT=15
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Redis Configuration (if needed)
REDIS_URL=redis://redis:6379
EOF
        print_success "Created default $ENV_FILE file"
        print_warning "Please review and update the environment variables in $ENV_FILE"
    else
        print_success "Environment file $ENV_FILE found"
    fi
}

# Function to validate configuration
validate_config() {
    print_status "Validating configuration..."
    
    # Check if required files exist
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Docker Compose file $COMPOSE_FILE not found"
        exit 1
    fi
    
    if [ ! -f "caddyfile" ]; then
        print_error "Caddyfile not found"
        exit 1
    fi
    
    if [ ! -f "Dockerfile.api" ]; then
        print_error "Dockerfile.api not found"
        exit 1
    fi
    
    if [ ! -f "app_api.py" ]; then
        print_error "app_api.py not found"
        exit 1
    fi
    
    print_success "Configuration validation passed"
}

# Function to stop and remove existing containers
cleanup_existing() {
    print_status "Cleaning up existing containers..."
    
    if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
        print_status "Stopping existing containers..."
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans
        print_success "Existing containers stopped and removed"
    else
        print_status "No existing containers found"
    fi
}

# Function to build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build the API image
    print_status "Building API image..."
    docker-compose -f "$COMPOSE_FILE" build api
    
    # Start all services
    print_status "Starting all services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_success "Services started successfully"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait a bit for services to start
    sleep 10
    
    # Check if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "All services are running"
    else
        print_error "Some services failed to start"
        docker-compose -f "$COMPOSE_FILE" ps
        exit 1
    fi
    
    # Check API health endpoint
    print_status "Checking API health..."
    if curl -f -s http://localhost:5001/api/health > /dev/null 2>&1; then
        print_success "API health check passed"
    else
        print_warning "API health check failed (this might be normal during startup)"
    fi
    
    # Check SearXNG
    print_status "Checking SearXNG..."
    if curl -f -s http://localhost:4000 > /dev/null 2>&1; then
        print_success "SearXNG is accessible"
    else
        print_warning "SearXNG health check failed (this might be normal during startup)"
    fi
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_status "Service URLs:"
    echo "  - SearXNG: http://localhost:4000"
    echo "  - API: http://localhost:5001"
    echo "  - API Health: http://localhost:5001/api/health"
    echo ""
    print_status "Logs can be viewed with: docker-compose logs -f [service_name]"
    print_status "Available services: caddy, redis, searxng, api"
}

# Function to show logs
show_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        print_status "Showing logs for $service..."
        docker-compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        print_status "Showing logs for all services..."
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Services stopped"
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose -f "$COMPOSE_FILE" restart
    print_success "Services restarted"
}

# Function to update services
update_services() {
    print_status "Updating services..."
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Rebuild and restart
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_success "Services updated"
}

# Function to show help
show_help() {
    echo "SearXNG Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Deploy all services (default)"
    echo "  start      - Start services"
    echo "  stop       - Stop services"
    echo "  restart    - Restart services"
    echo "  update     - Update and restart services"
    echo "  status     - Show service status"
    echo "  logs       - Show logs (all services)"
    echo "  logs [svc] - Show logs for specific service"
    echo "  health     - Check service health"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 logs api"
    echo "  $0 status"
}

# Main script logic
main() {
    local command=${1:-"deploy"}
    
    case "$command" in
        "deploy")
            print_status "Starting deployment..."
            check_docker
            check_docker_compose
            check_env_file
            validate_config
            cleanup_existing
            deploy_services
            check_health
            show_status
            ;;
        "start")
            check_docker
            check_docker_compose
            deploy_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "update")
            check_docker
            check_docker_compose
            update_services
            check_health
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "health")
            check_health
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 