# Self-Evolving Agent Platform - Docker Management

.PHONY: help build up down restart logs clean status test

# Default target
help: ## Show this help message
	@echo "Self-Evolving Agent Platform - Docker Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and deployment
setup: ## Initial setup - create .env and directories
	@echo "🔧 Setting up local environment..."
	@mkdir -p logs data backend/data
	@if [ ! -f .env ]; then cp .env.example .env; echo "📝 Created .env file"; fi
	@echo "✅ Setup complete"

build: ## Build Docker images
	@echo "🏗️  Building Docker images..."
	@docker-compose build --no-cache
	@echo "✅ Build complete"

up: setup ## Start all services
	@echo "🚀 Starting services..."
	@docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make status

down: ## Stop all services
	@echo "🛑 Stopping services..."
	@docker-compose down --remove-orphans
	@echo "✅ Services stopped"

restart: ## Restart all services
	@echo "🔄 Restarting services..."
	@docker-compose restart
	@echo "✅ Services restarted"

# Monitoring and logs
logs: ## Show logs from all services
	@docker-compose logs -f

logs-backend: ## Show backend logs only
	@docker-compose logs -f backend

logs-frontend: ## Show frontend logs only
	@docker-compose logs -f frontend

status: ## Show service status
	@echo "📊 Service Status:"
	@docker-compose ps
	@echo ""
	@echo "🔍 Health Checks:"
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend: Healthy" || echo "❌ Backend: Unhealthy"
	@curl -s http://localhost:8001 > /dev/null && echo "✅ Frontend: Available" || echo "❌ Frontend: Unavailable"

# Development
dev: ## Start in development mode with live reload
	@echo "🔧 Starting in development mode..."
	@docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
	@make status

shell-backend: ## Open shell in backend container
	@docker-compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	@docker-compose exec frontend /bin/bash

# Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	@docker-compose exec backend python -m pytest tests/ -v

test-build: ## Test build without starting services
	@echo "🧪 Testing Docker build..."
	@docker-compose build

# Maintenance
clean: ## Clean up containers, images, and volumes
	@echo "🧹 Cleaning up..."
	@docker-compose down --remove-orphans --volumes
	@docker system prune -f
	@echo "✅ Cleanup complete"

reset: clean build up ## Complete reset - clean, build, and start

# Quick deployment
deploy: ## Quick local deployment
	@chmod +x scripts/deploy-local.sh
	@./scripts/deploy-local.sh

# GPU deployment
gpu-setup: ## Setup GPU environment
	@echo "🔧 Setting up GPU environment..."
	@docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi || echo "❌ GPU not available"

gpu-build: ## Build GPU-enabled images
	@echo "🏗️  Building GPU-enabled images..."
	@docker build -f backend/Dockerfile.gpu -t agent-platform-backend-gpu:latest ./backend
	@docker build -f frontend/Dockerfile -t agent-platform-frontend:latest ./frontend

gpu-deploy: gpu-build ## Deploy with GPU support
	@echo "🚀 Starting GPU-enabled services..."
	@docker-compose -f docker-compose.gpu.yml up -d
	@make status

gpu-logs: ## Show GPU deployment logs
	@docker-compose -f docker-compose.gpu.yml logs -f

gpu-down: ## Stop GPU services
	@docker-compose -f docker-compose.gpu.yml down --remove-orphans

# Cloud deployment
cloud-build: ## Build and tag for cloud deployment
	@echo "☁️  Building for cloud deployment..."
	@docker build -f backend/Dockerfile.gpu -t ${DOCKER_REGISTRY}/agent-platform-backend-gpu:latest ./backend
	@docker build -f frontend/Dockerfile -t ${DOCKER_REGISTRY}/agent-platform-frontend:latest ./frontend

cloud-push: cloud-build ## Push images to registry
	@echo "📤 Pushing to registry..."
	@docker push ${DOCKER_REGISTRY}/agent-platform-backend-gpu:latest
	@docker push ${DOCKER_REGISTRY}/agent-platform-frontend:latest

# URLs
urls: ## Show service URLs
	@echo "🌐 Service URLs:"
	@echo "   Backend API: http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo "   Frontend UI: http://localhost:8001"
