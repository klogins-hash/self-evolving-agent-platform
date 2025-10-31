# Phase 2 Scaleway Integration Plan

## 🎯 **Current Deployment Status**

**Live System**: http://51.15.214.182:8000 (API) | :8001 (UI)  
**Status**: ✅ Healthy and running  
**Containers**: Backend + Frontend operational  
**Database**: SQLite (Phase 1)  

## 🔄 **Phase 2 Integration Strategy**

### **Approach: Gradual Integration**
- **Keep Phase 1 stable** while adding Phase 2 features
- **Side-by-side deployment** for testing
- **Feature flags** for controlled rollout
- **Zero-downtime migration** when ready

## 🏗️ **Infrastructure Requirements**

### **New Services Needed**
```yaml
services:
  # Existing (Phase 1)
  backend:          # ✅ Running
  frontend:         # ✅ Running
  
  # New (Phase 2)
  redis:           # Message queue & caching
  postgresql:      # Enhanced database
  phase2-backend:  # Enhanced backend with new features
```

### **Redis Setup**
```bash
# Add Redis container for message queuing
docker run -d \
  --name redis \
  --network self-evolving-agent-platform_agent_network \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --appendonly yes
```

### **PostgreSQL Setup**
```bash
# Add PostgreSQL for enhanced database
docker run -d \
  --name postgresql \
  --network self-evolving-agent-platform_agent_network \
  -p 5432:5432 \
  -e POSTGRES_DB=agent_platform \
  -e POSTGRES_USER=agent_user \
  -e POSTGRES_PASSWORD=secure_password_123 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

## 🔧 **Integration Steps**

### **Step 1: Add Infrastructure Services**
```bash
# On Scaleway server
cd self-evolving-agent-platform

# Create Phase 2 docker-compose
cat > docker-compose.phase2.yml << 'EOF'
version: '3.8'

services:
  # Phase 1 services (existing)
  backend:
    image: agent-platform-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./agents.db
      - REDIS_URL=redis://redis:6379
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    depends_on:
      - redis
    networks:
      - agent_network

  frontend:
    image: agent-platform-frontend
    ports:
      - "8001:8001"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - agent_network

  # Phase 2 services (new)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - agent_network
    restart: unless-stopped

  postgresql:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=agent_platform
      - POSTGRES_USER=agent_user
      - POSTGRES_PASSWORD=secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - agent_network
    restart: unless-stopped

  # Phase 2 enhanced backend (parallel to Phase 1)
  backend-v2:
    image: agent-platform-backend-v2
    ports:
      - "8002:8000"  # Different port for testing
    environment:
      - DATABASE_URL=postgresql://agent_user:secure_password_123@postgresql:5432/agent_platform
      - REDIS_URL=redis://redis:6379
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - PHASE=2
    depends_on:
      - postgresql
      - redis
    networks:
      - agent_network

volumes:
  agent_data:
  redis_data:
  postgres_data:

networks:
  agent_network:
EOF
```

### **Step 2: Build Phase 2 Backend**
```bash
# Create Phase 2 Dockerfile
cat > phase2/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Phase 1 backend (base)
COPY backend/ ./backend/
COPY phase2/backend/ ./phase2/backend/

# Install Python dependencies
COPY backend/requirements.txt ./
COPY phase2/requirements.txt ./phase2-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r phase2-requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### **Step 3: Phase 2 Requirements**
```bash
# Create Phase 2 Python requirements
cat > phase2/requirements.txt << 'EOF'
# Phase 2 additional dependencies
asyncpg>=0.29.0
redis>=5.0.0
websockets>=12.0
celery>=5.3.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pydantic-settings>=2.0.0
pytest-asyncio>=0.21.0
pytest-redis>=3.0.0
EOF
```

## 🚀 **Deployment Commands**

### **Deploy Phase 2 Infrastructure**
```bash
# On Scaleway server
cd self-evolving-agent-platform

# Start Phase 2 services
docker-compose -f docker-compose.phase2.yml up -d redis postgresql

# Wait for services to be ready
sleep 10

# Initialize PostgreSQL schema
docker exec -i postgresql psql -U agent_user -d agent_platform < phase2/backend/database/schema.sql

# Build Phase 2 backend
docker build -f phase2/Dockerfile -t agent-platform-backend-v2 .

# Start Phase 2 backend
docker-compose -f docker-compose.phase2.yml up -d backend-v2
```

### **Test Phase 2 Integration**
```bash
# Test Redis connection
docker exec redis redis-cli ping

# Test PostgreSQL connection
docker exec postgresql psql -U agent_user -d agent_platform -c "SELECT version();"

# Test Phase 2 backend
curl http://localhost:8002/health
curl http://localhost:8002/api/v2/agents/
```

## 🔍 **Monitoring & Validation**

### **Health Checks**
```bash
# Check all services
docker ps
docker-compose -f docker-compose.phase2.yml ps

# Check logs
docker logs self-evolving-agent-platform-redis-1
docker logs self-evolving-agent-platform-postgresql-1
docker logs self-evolving-agent-platform-backend-v2-1

# Test endpoints
curl http://51.15.214.182:8000/health  # Phase 1
curl http://51.15.214.182:8002/health  # Phase 2
```

### **Performance Monitoring**
```bash
# Redis stats
docker exec redis redis-cli info stats

# PostgreSQL stats
docker exec postgresql psql -U agent_user -d agent_platform -c "SELECT * FROM pg_stat_activity;"

# Container resources
docker stats
```

## 🔄 **Migration Strategy**

### **Phase 1 → Phase 2 Data Migration**
```bash
# Export Phase 1 data
docker exec self-evolving-agent-platform-backend-1 python -c "
import sqlite3
import json
conn = sqlite3.connect('/app/agents.db')
agents = conn.execute('SELECT * FROM agents').fetchall()
tasks = conn.execute('SELECT * FROM tasks').fetchall()
with open('/tmp/phase1_export.json', 'w') as f:
    json.dump({'agents': agents, 'tasks': tasks}, f)
conn.close()
"

# Copy to Phase 2 and import
docker cp self-evolving-agent-platform-backend-1:/tmp/phase1_export.json ./
# ... migration script execution
```

## 🎯 **Feature Rollout Plan**

### **Week 1: Infrastructure**
- ✅ Redis + PostgreSQL deployment
- ✅ Phase 2 backend parallel deployment
- ✅ Health monitoring setup

### **Week 2: Core Features**
- 🔄 Agent communication via Redis
- 🔄 Multi-model AI integration
- 🔄 Basic workflow engine

### **Week 3: Advanced Features**
- 🔄 Real-time WebSocket updates
- 🔄 Enhanced Chainlit UI
- 🔄 Performance optimization

### **Week 4: Production Migration**
- 🔄 Full data migration
- 🔄 Switch traffic to Phase 2
- 🔄 Phase 1 deprecation

## 🚨 **Risk Mitigation**

### **Rollback Strategy**
- **Keep Phase 1 running** during Phase 2 testing
- **Database backups** before migration
- **Traffic switching** capability
- **Monitoring alerts** for issues

### **Testing Strategy**
- **Parallel testing** on port 8002
- **Load testing** with both systems
- **Data integrity validation**
- **Performance benchmarking**

---

**Integration Status**: 🚀 **READY TO DEPLOY**  
**Risk Level**: 🟢 **LOW** (parallel deployment)  
**Rollback Time**: <2 minutes
