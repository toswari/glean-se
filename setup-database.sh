#!/bin/bash
#
# setup-database.sh - Database Setup Script for FAQ RAG System
# 
# This script sets up and manages the Weaviate vector database using Docker.
# Supports starting, stopping, restarting, and checking the status of the database.
#
# Usage:
#   ./setup-database.sh start     - Start the Weaviate database
#   ./setup-database.sh stop      - Stop the Weaviate database
#   ./setup-database.sh restart   - Restart the Weaviate database
#   ./setup-database.sh status    - Check the status of the database
#   ./setup-database.sh clean     - Remove database and all data (use with caution)
#   ./setup-database.sh logs      - View database logs
#   ./setup-database.sh help      - Show this help message
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
WEAVIATE_CONTAINER_NAME="weaviate"
WEAVIATE_IMAGE="semitechnologies/weaviate:1.25.0"
WEAVIATE_PORT="8080"
WEAVIATE_DATA_VOLUME="weaviate_data"
NETWORK_NAME="glean-se-network"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        log_info "For macOS: brew install --cask docker"
        log_info "For Ubuntu/WSL2: Follow Docker installation guide at https://docs.docker.com/engine/install/"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Docker is running
check_docker_running() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker Desktop or Docker service."
        exit 1
    fi
}

# Create Docker network
create_network() {
    if ! docker network ls | grep -q "$NETWORK_NAME"; then
        log_info "Creating Docker network: $NETWORK_NAME"
        docker network create "$NETWORK_NAME" >/dev/null
        log_success "Docker network created"
    else
        log_info "Docker network already exists: $NETWORK_NAME"
    fi
}

# Start Weaviate database
start_weaviate() {
    log_info "Starting Weaviate vector database..."
    
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${WEAVIATE_CONTAINER_NAME}$"; then
        # Check if it's running
        if docker ps --format '{{.Names}}' | grep -q "^${WEAVIATE_CONTAINER_NAME}$"; then
            log_info "Weaviate is already running on port $WEAVIATE_PORT"
            print_access_info
            return
        else
            # Container exists but is stopped, start it
            log_info "Starting existing Weaviate container..."
            docker start "$WEAVIATE_CONTAINER_NAME"
        fi
    else
        # Create new container
        log_info "Creating Weaviate container..."
        
        docker run -d \
            --name "$WEAVIATE_CONTAINER_NAME" \
            --network "$NETWORK_NAME" \
            -p "$WEAVIATE_PORT:8080" \
            -e QUERY_DEFAULTS_LIMIT=25 \
            -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
            -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
            -e DEFAULT_VECTORIZER_MODULE=none \
            -e CLUSTER_HOSTNAME=weaviate \
            -v "$WEAVIATE_DATA_VOLUME:/var/lib/weaviate" \
            --health-cmd "curl -f http://localhost:8080/v1/.well-known/ready" \
            --health-interval 5s \
            --health-timeout 5s \
            --health-retries 5 \
            "$WEAVIATE_IMAGE"
    fi
    
    # Wait for container to be healthy
    log_info "Waiting for Weaviate to be ready..."
    wait_for_weaviate
    
    print_access_info
}

# Wait for Weaviate to be ready
wait_for_weaviate() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec "$WEAVIATE_CONTAINER_NAME" curl -sf http://localhost:8080/v1/.well-known/ready >/dev/null 2>&1; then
            log_success "Weaviate is ready and healthy!"
            return 0
        fi
        
        echo -ne "[${CYAN}Waiting${NC}] Attempt $attempt/$max_attempts\r"
        sleep 2
        ((attempt++))
    done
    
    echo
    log_error "Weaviate failed to start within expected time. Check logs with: ./setup-database.sh logs"
    return 1
}

# Stop Weaviate database
stop_weaviate() {
    log_info "Stopping Weaviate vector database..."
    
    if docker ps --format '{{.Names}}' | grep -q "^${WEAVIATE_CONTAINER_NAME}$"; then
        docker stop "$WEAVIATE_CONTAINER_NAME"
        log_success "Weaviate stopped successfully"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${WEAVIATE_CONTAINER_NAME}$"; then
        log_info "Weaviate container exists but is already stopped"
    else
        log_warning "Weaviate container does not exist"
    fi
}

# Restart Weaviate database
restart_weaviate() {
    log_info "Restarting Weaviate vector database..."
    stop_weaviate
    sleep 2
    start_weaviate
}

# Check Weaviate status
check_status() {
    log_info "Checking Weaviate status..."
    echo
    
    # Check if container exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${WEAVIATE_CONTAINER_NAME}$"; then
        # Get container status
        local status=$(docker inspect --format='{{.State.Status}}' "$WEAVIATE_CONTAINER_NAME" 2>/dev/null)
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$WEAVIATE_CONTAINER_NAME" 2>/dev/null)
        
        echo -e "Container: ${CYAN}$WEAVIATE_CONTAINER_NAME${NC}"
        echo -e "Status:    ${CYAN}$status${NC}"
        echo -e "Health:    ${CYAN}$health${NC}"
        
        if [ "$status" = "running" ]; then
            echo
            print_access_info
            
            # Test connectivity
            echo -ne "Testing connectivity..."
            if curl -sf "http://localhost:$WEAVIATE_PORT/v1/.well-known/ready" >/dev/null 2>&1; then
                echo -e " ${GREEN}✓ Connected${NC}"
            else
                echo -e " ${RED}✗ Connection failed${NC}"
            fi
        fi
    else
        log_warning "Weaviate container does not exist. Run './setup-database.sh start' to create it."
    fi
}

# Clean up Weaviate (remove container and data)
clean_weaviate() {
    log_warning "This will remove the Weaviate container and ALL data!"
    echo -n "Are you sure you want to continue? Type 'yes' to confirm: "
    read -r confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Aborted"
        return
    fi
    
    log_info "Stopping and removing Weaviate container..."
    docker stop "$WEAVIATE_CONTAINER_NAME" 2>/dev/null || true
    docker rm "$WEAVIATE_CONTAINER_NAME" 2>/dev/null || true
    
    log_info "Removing data volume..."
    docker volume rm "$WEAVIATE_DATA_VOLUME" 2>/dev/null || true
    
    log_success "Weaviate cleaned up successfully"
}

# View Weaviate logs
view_logs() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${WEAVIATE_CONTAINER_NAME}$"; then
        log_info "Showing Weaviate logs (press Ctrl+C to exit)..."
        docker logs -f "$WEAVIATE_CONTAINER_NAME"
    else
        log_warning "Weaviate container does not exist"
    fi
}

# Print access information
print_access_info() {
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Weaviate Vector Database Ready!     ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo -e "Access URL:  ${CYAN}http://localhost:${WEAVIATE_PORT}${NC}"
    echo -e "Swagger UI:  ${CYAN}http://localhost:${WEAVIATE_PORT}/v1${NC}"
    echo
    echo -e "Container:   ${CYAN}$WEAVIATE_CONTAINER_NAME${NC}"
    echo -e "Image:       ${CYAN}$WEAVIATE_IMAGE${NC}"
    echo -e "Network:     ${CYAN}$NETWORK_NAME${NC}"
    echo -e "Data Volume: ${CYAN}$WEAVIATE_DATA_VOLUME${NC}"
    echo
    echo -e "To stop:     ${YELLOW}./setup-database.sh stop${NC}"
    echo -e "To view logs:${YELLOW} ./setup-database.sh logs${NC}"
    echo
}

# Show help
show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Weaviate Database Management Script  ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
    echo "Usage: ./setup-database.sh <command>"
    echo
    echo "Commands:"
    echo "  start     - Start the Weaviate vector database"
    echo "  stop      - Stop the Weaviate vector database"
    echo "  restart   - Restart the Weaviate vector database"
    echo "  status    - Check the status of the database"
    echo "  clean     - Remove database container and all data"
    echo "  logs      - View database logs (follow mode)"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  ./setup-database.sh start     # Start the database"
    echo "  ./setup-database.sh status    # Check if running"
    echo "  ./setup-database.sh logs      # View logs"
    echo
}

# Main execution
main() {
    local command="${1:-help}"
    
    # Always check Docker
    check_docker
    check_docker_running
    create_network
    
    case "$command" in
        start)
            start_weaviate
            ;;
        stop)
            stop_weaviate
            ;;
        restart)
            restart_weaviate
            ;;
        status)
            check_status
            ;;
        clean)
            clean_weaviate
            ;;
        logs)
            view_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"