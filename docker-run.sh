#!/bin/bash

# Docker run script for DocuGen AI
# This script provides easy commands to build and run the Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        print_error "Docker is not running or not installed"
        exit 1
    fi
}

# Function to build the Docker image
build_image() {
    print_status "Building DocuGen AI Docker image..."
    docker build -t neuralnotes-io:local .
    print_success "Docker image built successfully"
}

# Function to run the container
run_container() {
    local openai_key=""
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        source .env
        if [ ! -z "$OPENAI_API_KEY" ]; then
            openai_key="-e OPENAI_API_KEY=$OPENAI_API_KEY"
            print_status "Using OpenAI API key from .env file"
        fi
    fi
    
    print_status "Starting DocuGen AI container..."
    
    # Stop existing container if running
    docker stop neuralnotes-io 2>/dev/null || true
    docker rm neuralnotes-io 2>/dev/null || true
    
    # Run new container
    docker run -d \
        --name neuralnotes-io \
        -p 8000:8000 \
        $openai_key \
        -v neuralnotes_data:/app/data \
        --restart unless-stopped \
        neuralnotes-io:local
    
    print_success "Container started successfully"
    print_status "Application available at: http://localhost:8000"
    print_status "Health check: http://localhost:8000/api/health"
}

# Function to stop the container
stop_container() {
    print_status "Stopping DocuGen AI container..."
    docker stop neuralnotes-io 2>/dev/null || true
    docker rm neuralnotes-io 2>/dev/null || true
    print_success "Container stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker logs -f neuralnotes-io
}

# Function to show container status
show_status() {
    print_status "Container status:"
    docker ps -a --filter name=neuralnotes-io
    
    echo ""
    print_status "Health check:"
    curl -f http://localhost:8000/api/health 2>/dev/null && \
        print_success "Application is healthy" || \
        print_warning "Application is not responding"
}

# Function to run with docker-compose
run_compose() {
    print_status "Starting with Docker Compose..."
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found"
        exit 1
    fi
    
    docker-compose up -d
    print_success "Docker Compose started successfully"
    print_status "Application available at: http://localhost:8000"
}

# Function to stop docker-compose
stop_compose() {
    print_status "Stopping Docker Compose..."
    docker-compose down
    print_success "Docker Compose stopped"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build      Build the Docker image"
    echo "  run        Run the container (build if needed)"
    echo "  stop       Stop and remove the container"
    echo "  logs       Show container logs"
    echo "  status     Show container status and health"
    echo "  compose    Start with Docker Compose"
    echo "  compose-stop Stop Docker Compose"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build      # Build the image"
    echo "  $0 run        # Build and run the container"
    echo "  $0 logs       # View container logs"
    echo "  $0 compose    # Use Docker Compose"
}

# Main script logic
main() {
    check_docker
    
    case "${1:-}" in
        build)
            build_image
            ;;
        run)
            if ! docker image inspect neuralnotes-io:local > /dev/null 2>&1; then
                print_warning "Image not found, building first..."
                build_image
            fi
            run_container
            ;;
        stop)
            stop_container
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        compose)
            run_compose
            ;;
        compose-stop)
            stop_compose
            ;;
        help|--help|-h)
            show_usage
            ;;
        "")
            print_warning "No command specified"
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"