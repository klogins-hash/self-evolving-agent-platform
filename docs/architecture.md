# Architecture Overview

## System Architecture

The Self-Evolving Agent Platform MVP follows a microservices architecture with clear separation between frontend and backend components.

### High-Level Architecture

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Chainlit UI   │ ◄─────────────────► │   FastAPI       │
│   (Frontend)    │                      │   (Backend)     │
│   Port: 8001    │                      │   Port: 8000    │
└─────────────────┘                      └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │   SQLite DB     │
                                         │   (Data Layer)  │
                                         └─────────────────┘
```

## Dual-Agent Architecture

The platform implements a dual-agent system as specified in the original documentation:

### Chief of Staff (CoS) Agent
- **Role**: Orchestrator and manager
- **Responsibilities**:
  - Agent swarm management
  - Task delegation and coordination
  - Strategic decision making
  - Resource allocation

### Master Operator (MO) Agent
- **Role**: Task executor
- **Responsibilities**:
  - Direct task execution
  - Tool and API interactions
  - Data processing and analysis
  - Operational tasks

## Component Details

### Backend (FastAPI)

**Core Modules:**
- `app/main.py` - Application entry point and configuration
- `app/core/config.py` - Settings and environment management
- `app/models/` - Data models (Agent, Task, etc.)
- `app/api/` - REST API endpoints
- `app/agents/` - Agent management logic (future expansion)

**Key Features:**
- RESTful API design
- Pydantic data validation
- Async/await support
- CORS middleware for frontend integration
- Environment-based configuration

### Frontend (Chainlit)

**Core Features:**
- Conversational UI for agent interaction
- Real-time communication with backend
- Interactive agent and task management
- Command-based interface
- Visual status indicators

**Key Components:**
- `app.py` - Main Chainlit application
- `AgentPlatformClient` - Backend API client
- Interactive wizards for agent/task creation
- Status monitoring and system overview

### Data Layer

**MVP Storage:**
- SQLite for development and MVP
- In-memory storage for rapid prototyping
- Designed for easy migration to PostgreSQL

**Data Models:**
- **Agent**: Core agent entity with type, status, capabilities
- **Task**: Work units with priority, status, dependencies
- **AgentCapability**: Modular agent abilities
- Extensible metadata fields for future features

## API Design

### REST Endpoints

**Agents:**
- `GET /api/v1/agents/` - List all agents
- `POST /api/v1/agents/` - Create new agent
- `GET /api/v1/agents/{id}` - Get specific agent
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent

**Tasks:**
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

**System:**
- `GET /` - Platform information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Security Considerations

### MVP Security Features
- Environment-based configuration
- CORS protection
- Input validation with Pydantic
- Error handling and sanitization

### Future Security Enhancements
- JWT authentication
- Role-based access control
- API rate limiting
- Encryption at rest
- Zero-knowledge privacy features

## Scalability Design

### Current MVP Limitations
- Single-instance deployment
- SQLite database
- In-memory agent storage
- Basic error handling

### Designed for Growth
- Microservices architecture
- Database abstraction layer
- Async/await throughout
- Docker containerization
- Environment-based configuration

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: SQLite (MVP) → PostgreSQL (Production)
- **Validation**: Pydantic 2.5+
- **ASGI Server**: Uvicorn

### Frontend
- **Framework**: Chainlit 1.0+
- **Language**: Python 3.11+
- **HTTP Client**: httpx
- **UI**: Native Chainlit components

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Development**: Hot reload, environment isolation
- **Deployment**: Ready for cloud deployment

## Future Architecture Evolution

### Phase 2: Intelligence
- Advanced agent capabilities
- Self-evolution mechanisms
- Enhanced inter-agent communication
- Machine learning integration

### Phase 3: Scale
- Distributed agent swarms
- Advanced security features
- Performance optimization
- Enterprise-grade deployment

This architecture provides a solid foundation for the self-evolving agent platform while maintaining flexibility for future enhancements and scaling.
