# PostgreSQL Migration Strategy

## 🎯 **Migration Overview**

**Objective**: Migrate from SQLite to PostgreSQL for enhanced performance, scalability, and production readiness.

**Timeline**: Week 3 of Phase 2 development  
**Downtime**: <5 minutes with proper planning  
**Rollback Plan**: Automated rollback to SQLite if issues occur

## 📊 **Current State Analysis**

### SQLite Limitations (Phase 1)
- **Concurrency**: Limited concurrent write operations
- **Scalability**: Single file database, no horizontal scaling
- **Features**: Missing advanced features (JSON operations, full-text search)
- **Production**: Not recommended for high-traffic applications
- **Backup**: File-based backup only

### PostgreSQL Benefits (Phase 2)
- **Concurrency**: Excellent multi-user support
- **Scalability**: Horizontal scaling with read replicas
- **Features**: Advanced JSON, full-text search, extensions
- **Production**: Battle-tested for enterprise applications
- **Backup**: Point-in-time recovery, streaming replication

## 🗄️ **Schema Evolution**

### Phase 1 Tables (Existing)
```sql
-- Current SQLite schema
agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    status TEXT DEFAULT 'idle',
    capabilities TEXT,  -- JSON string
    system_prompt TEXT,
    model_provider TEXT DEFAULT 'openrouter',
    model_name TEXT DEFAULT 'auto',
    created_at TEXT,
    updated_at TEXT
);

tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    assigned_agent_id TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (assigned_agent_id) REFERENCES agents (id)
);
```

### Phase 2 Enhanced Schema (PostgreSQL)
```sql
-- Enhanced PostgreSQL schema with new features

-- Agents table with enhanced capabilities
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('chief_of_staff', 'master_operator')),
    status VARCHAR(50) DEFAULT 'idle' CHECK (status IN ('idle', 'active', 'busy', 'error', 'offline')),
    capabilities JSONB DEFAULT '[]',
    system_prompt TEXT,
    model_provider VARCHAR(100) DEFAULT 'openrouter',
    model_name VARCHAR(100) DEFAULT 'auto',
    performance_metrics JSONB DEFAULT '{}',
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table with workflow support
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    step_order INTEGER DEFAULT 0,
    context_data JSONB DEFAULT '{}',
    result_data JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- New: Agent messages for communication
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    correlation_id UUID,
    conversation_id UUID,
    sender_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    sender_type VARCHAR(50) NOT NULL,
    recipient_type VARCHAR(50) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'acknowledged', 'failed', 'expired')),
    subject VARCHAR(500),
    payload JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    expires_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- New: Workflows for multi-step task orchestration
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,  -- Workflow steps and conditions
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'failed')),
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES agents(id),
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- New: Workflow executions for tracking
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    current_step INTEGER DEFAULT 0,
    context_data JSONB DEFAULT '{}',
    result_data JSONB DEFAULT '{}',
    started_by UUID REFERENCES agents(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- New: Agent capabilities for better matching
CREATE TABLE agent_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    capability_name VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    last_used TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, capability_name)
);

-- New: Performance metrics tracking
CREATE TABLE agent_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX idx_agents_type_status ON agents(agent_type, status);
CREATE INDEX idx_agents_last_heartbeat ON agents(last_heartbeat);
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority);
CREATE INDEX idx_tasks_assigned_agent ON tasks(assigned_agent_id);
CREATE INDEX idx_tasks_workflow ON tasks(workflow_id);
CREATE INDEX idx_messages_recipient_status ON agent_messages(recipient_id, status);
CREATE INDEX idx_messages_sender_type ON agent_messages(sender_id, message_type);
CREATE INDEX idx_messages_correlation ON agent_messages(correlation_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_agent_capabilities_agent ON agent_capabilities(agent_id);
CREATE INDEX idx_agent_performance_agent_metric ON agent_performance(agent_id, metric_name);

-- Full-text search indexes
CREATE INDEX idx_tasks_search ON tasks USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));
CREATE INDEX idx_workflows_search ON workflows USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

## 🔄 **Migration Process**

### Step 1: Environment Setup
```bash
# Install PostgreSQL dependencies
pip install psycopg2-binary asyncpg

# Set up PostgreSQL connection
export DATABASE_URL="postgresql://user:password@localhost:5432/agent_platform"
```

### Step 2: Data Export from SQLite
```python
# Export existing data
import sqlite3
import json
from datetime import datetime

def export_sqlite_data():
    conn = sqlite3.connect('agents.db')
    
    # Export agents
    agents = conn.execute('SELECT * FROM agents').fetchall()
    with open('agents_export.json', 'w') as f:
        json.dump(agents, f)
    
    # Export tasks
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    with open('tasks_export.json', 'w') as f:
        json.dump(tasks, f)
    
    conn.close()
```

### Step 3: PostgreSQL Schema Creation
```python
# Create new schema
import asyncpg

async def create_postgresql_schema():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Execute schema creation script
    with open('phase2_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    await conn.execute(schema_sql)
    await conn.close()
```

### Step 4: Data Migration
```python
# Migrate data with transformation
async def migrate_data():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Migrate agents with UUID conversion
    with open('agents_export.json', 'r') as f:
        agents = json.load(f)
    
    for agent in agents:
        await conn.execute("""
            INSERT INTO agents (id, name, agent_type, status, capabilities, 
                               system_prompt, model_provider, model_name, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, 
        uuid.uuid4(),  # Generate new UUID
        agent['name'],
        agent['agent_type'],
        agent['status'],
        json.loads(agent['capabilities']) if agent['capabilities'] else [],
        agent['system_prompt'],
        agent['model_provider'],
        agent['model_name'],
        datetime.fromisoformat(agent['created_at'])
        )
    
    # Similar migration for tasks...
    await conn.close()
```

### Step 5: Validation and Testing
```python
# Validate migration
async def validate_migration():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Check record counts
    agent_count = await conn.fetchval('SELECT COUNT(*) FROM agents')
    task_count = await conn.fetchval('SELECT COUNT(*) FROM tasks')
    
    print(f"Migrated {agent_count} agents and {task_count} tasks")
    
    # Test queries
    active_agents = await conn.fetch(
        'SELECT * FROM agents WHERE status = $1', 'active'
    )
    
    await conn.close()
```

## 🔧 **Configuration Updates**

### Database Connection Configuration
```python
# phase2/backend/database/config.py
from pydantic import BaseSettings
from typing import Optional

class DatabaseSettings(BaseSettings):
    # PostgreSQL configuration
    database_url: str = "postgresql://user:password@localhost:5432/agent_platform"
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Migration settings
    migration_batch_size: int = 1000
    migration_timeout: int = 300
    
    # Backup settings
    backup_enabled: bool = True
    backup_retention_days: int = 30
    
    class Config:
        env_file = ".env"
```

### Connection Pool Setup
```python
# phase2/backend/database/connection.py
import asyncpg
from asyncpg import Pool
from typing import Optional

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[Pool] = None
    
    async def initialize(self, database_url: str, **kwargs):
        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            **kwargs
        )
    
    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

# Global database manager
db = DatabaseManager()
```

## 🚨 **Risk Mitigation**

### Rollback Strategy
1. **Automated Backup**: SQLite file backup before migration
2. **Validation Checks**: Comprehensive data integrity validation
3. **Quick Rollback**: Switch back to SQLite if issues occur
4. **Monitoring**: Real-time monitoring during migration

### Testing Strategy
1. **Staging Environment**: Full migration test on staging
2. **Performance Testing**: Load testing with PostgreSQL
3. **Data Integrity**: Checksum validation of migrated data
4. **Rollback Testing**: Verify rollback procedures work

### Monitoring and Alerts
1. **Migration Progress**: Real-time progress tracking
2. **Error Alerts**: Immediate notification of issues
3. **Performance Metrics**: Response time monitoring
4. **Health Checks**: Continuous health monitoring

## 📅 **Migration Timeline**

### Week 3 Schedule
- **Day 1**: PostgreSQL setup and schema creation
- **Day 2**: Migration script development and testing
- **Day 3**: Staging environment migration and validation
- **Day 4**: Production migration execution
- **Day 5**: Performance optimization and monitoring setup

### Success Criteria
- ✅ Zero data loss during migration
- ✅ <5 minutes downtime
- ✅ All existing functionality preserved
- ✅ Performance improvement measurable
- ✅ Rollback capability verified

---

**Migration Status**: 📋 **PLANNED**  
**Execution Date**: Week 3, Phase 2  
**Risk Level**: 🟡 **MEDIUM** (with mitigation strategies)
