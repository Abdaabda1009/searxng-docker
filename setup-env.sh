#!/bin/bash

# Environment Setup Script for SearXNG Docker
# This script helps manage environment variables and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ENV_FILE=".env"

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

# Function to create default environment file
create_default_env() {
    print_status "Creating default environment file..."
    
    cat > "$ENV_FILE" << 'EOF'
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
    
    print_success "Default environment file created at $ENV_FILE"
    print_warning "Please review and update the configuration values"
}

# Function to update specific environment variable
update_env_var() {
    local key="$1"
    local value="$2"
    
    if [ -z "$key" ] || [ -z "$value" ]; then
        print_error "Usage: $0 set <KEY> <VALUE>"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        create_default_env
    fi
    
    # Check if key exists
    if grep -q "^${key}=" "$ENV_FILE"; then
        # Update existing key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
        else
            # Linux
            sed -i "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
        fi
        print_success "Updated $key=$value"
    else
        # Add new key
        echo "${key}=${value}" >> "$ENV_FILE"
        print_success "Added $key=$value"
    fi
}

# Function to show current environment variables
show_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    print_status "Current environment variables:"
    echo ""
    cat "$ENV_FILE" | grep -v '^#' | grep -v '^$' | sort
}

# Function to validate environment file
validate_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    print_status "Validating environment file..."
    
    # Check for required variables
    local required_vars=("SEARXNG_HOSTNAME" "SEARXNG_BASE_URL" "API_PORT")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_success "All required environment variables are present"
    else
        print_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
}

# Function to backup environment file
backup_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    local backup_file="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$ENV_FILE" "$backup_file"
    print_success "Environment file backed up to $backup_file"
}

# Function to restore environment file
restore_env() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file $backup_file not found"
        exit 1
    fi
    
    cp "$backup_file" "$ENV_FILE"
    print_success "Environment file restored from $backup_file"
}

# Function to show help
show_help() {
    echo "Environment Setup Script for SearXNG Docker"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  create              - Create default environment file"
    echo "  show                - Show current environment variables"
    echo "  set <KEY> <VALUE>   - Set or update environment variable"
    echo "  validate            - Validate environment file"
    echo "  backup              - Backup current environment file"
    echo "  restore <FILE>      - Restore environment file from backup"
    echo "  help                - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 create"
    echo "  $0 set RATE_LIMIT_REQUESTS 500"
    echo "  $0 show"
    echo "  $0 backup"
    echo "  $0 restore .env.backup.20231201_143022"
}

# Main script logic
main() {
    local command=${1:-"help"}
    
    case "$command" in
        "create")
            create_default_env
            ;;
        "show")
            show_env
            ;;
        "set")
            update_env_var "$2" "$3"
            ;;
        "validate")
            validate_env
            ;;
        "backup")
            backup_env
            ;;
        "restore")
            restore_env "$2"
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