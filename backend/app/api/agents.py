from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.agent import (
    Agent, AgentCreateRequest, AgentUpdateRequest, AgentResponse,
    AgentType, AgentStatus
)

router = APIRouter()

# In-memory storage for MVP (replace with database in production)
agents_db: Dict[str, Agent] = {}


@router.get("/", response_model=List[Agent])
async def list_agents():
    """Get all agents in the system."""
    return list(agents_db.values())


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get a specific agent by ID."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]


@router.post("/", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest):
    """Create a new agent."""
    agent = Agent(
        name=request.name,
        agent_type=request.agent_type,
        system_prompt=request.system_prompt or "",
        model_provider=request.model_provider or "openrouter",
        model_name=request.model_name or "auto",
        capabilities=request.capabilities or [],
        parent_agent_id=request.parent_agent_id,
        metadata=request.metadata or {}
    )
    
    agents_db[agent.id] = agent
    
    return AgentResponse(
        agent=agent,
        message=f"Agent '{agent.name}' created successfully",
        success=True
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Update an existing agent."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    
    # Update fields if provided
    if request.name is not None:
        agent.name = request.name
    if request.status is not None:
        agent.status = request.status
    if request.system_prompt is not None:
        agent.system_prompt = request.system_prompt
    if request.model_provider is not None:
        agent.model_provider = request.model_provider
    if request.model_name is not None:
        agent.model_name = request.model_name
    if request.capabilities is not None:
        agent.capabilities = request.capabilities
    if request.metadata is not None:
        agent.metadata.update(request.metadata)
    
    agents_db[agent_id] = agent
    
    return AgentResponse(
        agent=agent,
        message=f"Agent '{agent.name}' updated successfully",
        success=True
    )


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db.pop(agent_id)
    
    return {
        "message": f"Agent '{agent.name}' deleted successfully",
        "success": True
    }


@router.get("/type/{agent_type}", response_model=List[Agent])
async def get_agents_by_type(agent_type: AgentType):
    """Get all agents of a specific type."""
    return [agent for agent in agents_db.values() if agent.agent_type == agent_type]


@router.get("/status/{status}", response_model=List[Agent])
async def get_agents_by_status(status: AgentStatus):
    """Get all agents with a specific status."""
    return [agent for agent in agents_db.values() if agent.status == status]


@router.post("/{agent_id}/activate")
async def activate_agent(agent_id: str):
    """Activate an agent (set status to active)."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    agent.status = AgentStatus.ACTIVE
    
    return {
        "message": f"Agent '{agent.name}' activated",
        "success": True
    }


@router.post("/{agent_id}/deactivate")
async def deactivate_agent(agent_id: str):
    """Deactivate an agent (set status to offline)."""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    agent.status = AgentStatus.OFFLINE
    
    return {
        "message": f"Agent '{agent.name}' deactivated",
        "success": True
    }
