# API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication
Currently no authentication required for MVP. Future versions will implement JWT-based authentication.

## Endpoints

### System Endpoints

#### GET /
Get platform information and status.

**Response:**
```json
{
  "message": "Self-Evolving Agent Platform MVP",
  "version": "0.1.0",
  "status": "active",
  "docs": "/docs"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T15:23:00Z"
}
```

### Agent Management

#### GET /api/v1/agents/
List all agents in the system.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "name": "Agent Name",
    "agent_type": "chief_of_staff",
    "status": "active",
    "capabilities": [],
    "created_at": "2025-10-31T15:23:00Z",
    "metadata": {}
  }
]
```

#### POST /api/v1/agents/
Create a new agent.

**Request Body:**
```json
{
  "name": "My Agent",
  "agent_type": "chief_of_staff",
  "system_prompt": "You are a helpful agent",
  "model_provider": "openai",
  "model_name": "gpt-4"
}
```

**Response:**
```json
{
  "agent": {
    "id": "uuid-string",
    "name": "My Agent",
    "agent_type": "chief_of_staff",
    "status": "idle",
    "created_at": "2025-10-31T15:23:00Z"
  },
  "message": "Agent 'My Agent' created successfully",
  "success": true
}
```

#### GET /api/v1/agents/{agent_id}
Get a specific agent by ID.

#### PUT /api/v1/agents/{agent_id}
Update an existing agent.

#### DELETE /api/v1/agents/{agent_id}
Delete an agent.

### Task Management

#### GET /api/v1/tasks/
List all tasks in the system.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "title": "Task Title",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "assigned_agent_id": "agent-uuid",
    "created_at": "2025-10-31T15:23:00Z"
  }
]
```

#### POST /api/v1/tasks/
Create a new task.

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "priority": "high",
  "assigned_agent_id": "agent-uuid"
}
```

#### GET /api/v1/tasks/{task_id}
Get a specific task by ID.

#### PUT /api/v1/tasks/{task_id}
Update an existing task.

#### DELETE /api/v1/tasks/{task_id}
Delete a task.

### Filtering Endpoints

#### GET /api/v1/agents/type/{agent_type}
Get agents by type (`chief_of_staff` or `master_operator`).

#### GET /api/v1/agents/status/{status}
Get agents by status (`idle`, `active`, `busy`, `error`, `offline`).

#### GET /api/v1/tasks/status/{status}
Get tasks by status (`pending`, `in_progress`, `completed`, `failed`, `cancelled`).

#### GET /api/v1/tasks/priority/{priority}
Get tasks by priority (`low`, `medium`, `high`, `urgent`).

#### GET /api/v1/tasks/agent/{agent_id}
Get all tasks assigned to a specific agent.

### Agent Control

#### POST /api/v1/agents/{agent_id}/activate
Activate an agent (set status to active).

#### POST /api/v1/agents/{agent_id}/deactivate
Deactivate an agent (set status to offline).

### Task Control

#### POST /api/v1/tasks/{task_id}/start
Start a task (set status to in_progress).

#### POST /api/v1/tasks/{task_id}/complete
Complete a task (set status to completed).

**Request Body (optional):**
```json
{
  "output_data": {
    "result": "Task completed successfully"
  }
}
```

#### POST /api/v1/tasks/{task_id}/fail
Mark a task as failed.

**Request Body:**
```json
{
  "error_message": "Task failed due to error"
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

Error response format:
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation or `/redoc` for ReDoc documentation when the server is running.
