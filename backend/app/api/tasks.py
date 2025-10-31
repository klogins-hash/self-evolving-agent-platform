from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
from app.models.task import (
    Task, TaskCreateRequest, TaskUpdateRequest, TaskResponse,
    TaskStatus, TaskPriority
)

router = APIRouter()

# In-memory storage for MVP (replace with database in production)
tasks_db: Dict[str, Task] = {}


@router.get("/", response_model=List[Task])
async def list_tasks():
    """Get all tasks in the system."""
    return list(tasks_db.values())


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a specific task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


@router.post("/", response_model=TaskResponse)
async def create_task(request: TaskCreateRequest):
    """Create a new task."""
    task = Task(
        title=request.title,
        description=request.description,
        priority=request.priority or TaskPriority.MEDIUM,
        assigned_agent_id=request.assigned_agent_id,
        input_data=request.input_data or {},
        estimated_duration=request.estimated_duration,
        depends_on=request.depends_on or [],
        tags=request.tags or [],
        metadata=request.metadata or {}
    )
    
    tasks_db[task.id] = task
    
    return TaskResponse(
        task=task,
        message=f"Task '{task.title}' created successfully",
        success=True
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, request: TaskUpdateRequest):
    """Update an existing task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    # Update fields if provided
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.status is not None:
        # Handle status transitions
        if request.status == TaskStatus.IN_PROGRESS and task.status == TaskStatus.PENDING:
            task.started_at = datetime.utcnow()
        elif request.status == TaskStatus.COMPLETED and task.status == TaskStatus.IN_PROGRESS:
            task.completed_at = datetime.utcnow()
        task.status = request.status
    if request.priority is not None:
        task.priority = request.priority
    if request.assigned_agent_id is not None:
        task.assigned_agent_id = request.assigned_agent_id
    if request.output_data is not None:
        task.output_data = request.output_data
    if request.error_message is not None:
        task.error_message = request.error_message
    if request.tags is not None:
        task.tags = request.tags
    if request.metadata is not None:
        task.metadata.update(request.metadata)
    
    tasks_db[task_id] = task
    
    return TaskResponse(
        task=task,
        message=f"Task '{task.title}' updated successfully",
        success=True
    )


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db.pop(task_id)
    
    return {
        "message": f"Task '{task.title}' deleted successfully",
        "success": True
    }


@router.get("/status/{status}", response_model=List[Task])
async def get_tasks_by_status(status: TaskStatus):
    """Get all tasks with a specific status."""
    return [task for task in tasks_db.values() if task.status == status]


@router.get("/priority/{priority}", response_model=List[Task])
async def get_tasks_by_priority(priority: TaskPriority):
    """Get all tasks with a specific priority."""
    return [task for task in tasks_db.values() if task.priority == priority]


@router.get("/agent/{agent_id}", response_model=List[Task])
async def get_tasks_by_agent(agent_id: str):
    """Get all tasks assigned to a specific agent."""
    return [task for task in tasks_db.values() if task.assigned_agent_id == agent_id]


@router.post("/{task_id}/start")
async def start_task(task_id: str):
    """Start a task (set status to in_progress)."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="Task is not in pending status")
    
    task.status = TaskStatus.IN_PROGRESS
    task.started_at = datetime.utcnow()
    
    return {
        "message": f"Task '{task.title}' started",
        "success": True
    }


@router.post("/{task_id}/complete")
async def complete_task(task_id: str, output_data: Dict[str, Any] = None):
    """Complete a task (set status to completed)."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    if task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Task is not in progress")
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    if output_data:
        task.output_data = output_data
    
    return {
        "message": f"Task '{task.title}' completed",
        "success": True
    }


@router.post("/{task_id}/fail")
async def fail_task(task_id: str, error_message: str):
    """Mark a task as failed."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task.status = TaskStatus.FAILED
    task.error_message = error_message
    task.completed_at = datetime.utcnow()
    
    return {
        "message": f"Task '{task.title}' marked as failed",
        "success": True
    }
