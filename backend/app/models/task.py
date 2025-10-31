from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import uuid


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """Core task model for agent operations."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # Assignment
    assigned_agent_id: Optional[str] = None
    created_by_agent_id: Optional[str] = None
    
    # Execution data
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # seconds
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list)  # Task IDs
    blocks: List[str] = Field(default_factory=list)  # Task IDs
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskCreateRequest(BaseModel):
    """Request model for creating a new task."""
    title: str
    description: str
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assigned_agent_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    estimated_duration: Optional[int] = None
    depends_on: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_agent_id: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Response model for task operations."""
    task: Task
    message: str
    success: bool = True
