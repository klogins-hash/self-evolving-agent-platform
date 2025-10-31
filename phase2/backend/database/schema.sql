-- Phase 2: PostgreSQL Schema
-- Enhanced database schema for agent communication and workflows

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Agents table with enhanced capabilities
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Agent messages for communication
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
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

-- Workflows for multi-step task orchestration
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'failed')),
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES agents(id),
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow executions for tracking
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Agent capabilities for better matching
CREATE TABLE agent_capabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    capability_name VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    last_used TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, capability_name)
);

-- Performance metrics tracking
CREATE TABLE agent_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
