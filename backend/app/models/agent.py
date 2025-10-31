from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import uuid


class AgentType(str, Enum):
    """Types of agents in the dual-agent architecture."""
    CHIEF_OF_STAFF = "chief_of_staff"  # CoS - Orchestrates and manages
    MASTER_OPERATOR = "master_operator"  # MO - Executes tasks


class AgentStatus(str, Enum):
    """Agent operational status."""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapability(BaseModel):
    """Represents a capability that an agent possesses."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class Agent(BaseModel):
    """Core agent model representing both CoS and MO agents."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    
    # Agent configuration
    capabilities: List[AgentCapability] = Field(default_factory=list)
    system_prompt: str = ""
    model_provider: str = "openrouter"  # openrouter, groq, openai, anthropic, etc.
    model_name: str = "auto"
    
    # Operational data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    task_count: int = 0
    success_rate: float = 0.0
    
    # Relationships
    parent_agent_id: Optional[str] = None  # For agent hierarchy
    managed_agents: List[str] = Field(default_factory=list)  # IDs of managed agents
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent."""
    name: str
    agent_type: AgentType
    system_prompt: Optional[str] = ""
    model_provider: Optional[str] = "openrouter"
    model_name: Optional[str] = "auto"
    capabilities: Optional[List[AgentCapability]] = Field(default_factory=list)
    parent_agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentUpdateRequest(BaseModel):
    """Request model for updating an agent."""
    name: Optional[str] = None
    status: Optional[AgentStatus] = None
    system_prompt: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    capabilities: Optional[List[AgentCapability]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response model for agent operations."""
    agent: Agent
    message: str
    success: bool = True
