#!/bin/bash

# User Management API - Startup Script
# This script provides easy commands to run the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_message "Python $PYTHON_VERSION detected"
}

# Setup virtual environment
setup_venv() {
    print_message "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_message "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    source venv/bin/activate
    print_message "Virtual environment activated"
}

# Install dependencies
install_deps() {
    print_message "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_message "Dependencies installed successfully"
}

# Run tests
run_tests() {
    print_message "Running tests..."
    source venv/bin/activate
    pytest tests/ -v --cov=app --cov-report=term-missing
}

# Run the application
run_app() {
    print_message "Starting User Management API..."
    source venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
}

# Run with Docker
run_docker() {
    print_message "Starting application with Docker Compose..."
    docker-compose up --build
}

# Stop Docker containers
stop_docker() {
    print_message "Stopping Docker containers..."
    docker-compose down
}

# Clean up
cleanup() {
    print_message "Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    print_message "Cleanup completed"
}

# Display help
show_help() {
    echo "User Management API - Startup Script"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up virtual environment and install dependencies"
    echo "  run         - Run the application locally"
    echo "  test        - Run tests with coverage"
    echo "  docker      - Run with Docker Compose"
    echo "  docker-stop - Stop Docker containers"
    echo "  clean       - Clean up Python cache files"
    echo "  help        - Show this help message"
    echo ""
}

# Main script logic
case "$1" in
    setup)
        check_python
        setup_venv
        install_deps
        print_message "Setup completed successfully!"
        print_message "Run './run.sh run' to start the application"
        ;;
    run)
        check_python
        run_app
        ;;
    test)
        check_python
        run_tests
        ;;
    docker)
        run_docker
        ;;
    docker-stop)
        stop_docker
        ;;
    clean)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

