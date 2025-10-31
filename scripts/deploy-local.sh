#!/bin/bash

# Self-Evolving Agent Platform - Local Docker Deployment Script
echo "🚀 Starting Self-Evolving Agent Platform Local Deployment..."

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

# Check if Docker is installed and running
print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

print_success "Docker is installed and running"

# Check if Docker Compose is available
print_status "Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

print_success "Docker Compose is available"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_success ".env file created"
else
    print_success ".env file exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p backend/data
print_success "Directories created"

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start services
print_status "Building Docker images..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    print_error "Failed to build Docker images"
    exit 1
fi

print_success "Docker images built successfully"

print_status "Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check backend health
print_status "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend health check failed after 30 attempts"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Check frontend
print_status "Checking frontend availability..."
sleep 5
if curl -s http://localhost:8001 > /dev/null 2>&1; then
    print_success "Frontend is available"
else
    print_warning "Frontend may still be starting up"
fi

# Display status
print_success "🎉 Self-Evolving Agent Platform deployed successfully!"
echo ""
echo "📋 Service Information:"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📖 API Docs: http://localhost:8000/docs"
echo "   🎨 Frontend UI: http://localhost:8001"
echo ""
echo "🔍 Useful Commands:"
echo "   📊 View logs: docker-compose logs -f"
echo "   🔄 Restart: docker-compose restart"
echo "   🛑 Stop: docker-compose down"
echo "   📈 Status: docker-compose ps"
echo ""
echo "🚀 Platform is ready for use!"
