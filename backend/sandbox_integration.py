"""
Sandbox Integration for Self-Evolving Agent Platform
Connects agents to E2B sandboxes and Strands tools
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.models import Agent, Task
from database.database import get_db


@dataclass
class SandboxSession:
    """Represents an active sandbox session for an agent."""
    agent_id: str
    sandbox_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    tools_used: List[str]
    execution_count: int
    status: str  # active, paused, terminated


class SandboxManager:
    """Manages sandbox sessions and tool execution for agents."""
    
    def __init__(self):
        self.active_sessions: Dict[str, SandboxSession] = {}
        self.sandbox_api_url = "http://localhost:8003"  # Sandbox UI endpoint
        self.e2b_api_key = os.getenv("E2B_API_KEY")
        
    async def create_sandbox_session(self, agent_id: str) -> SandboxSession:
        """Create a new sandbox session for an agent."""
        
        session_id = f"sandbox_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize sandbox via API
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.sandbox_api_url}/api/sandbox/create",
                    json={
                        "agent_id": agent_id,
                        "session_id": session_id,
                        "tools_enabled": True,
                        "approval_required": True
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    sandbox_data = response.json()
                    sandbox_id = sandbox_data.get("sandbox_id")
                else:
                    # Fallback to local sandbox creation
                    sandbox_id = f"local_{session_id}"
                    
            except Exception as e:
                print(f"Failed to create remote sandbox: {e}")
                sandbox_id = f"local_{session_id}"
        
        session = SandboxSession(
            agent_id=agent_id,
            sandbox_id=sandbox_id,
            session_id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            tools_used=[],
            execution_count=0,
            status="active"
        )
        
        self.active_sessions[agent_id] = session
        return session
    
    async def execute_tool_for_agent(
        self, 
        agent_id: str, 
        tool_name: str, 
        parameters: Dict[str, Any],
        require_approval: bool = True
    ) -> Dict[str, Any]:
        """Execute a tool in the agent's sandbox."""
        
        # Get or create sandbox session
        if agent_id not in self.active_sessions:
            await self.create_sandbox_session(agent_id)
        
        session = self.active_sessions[agent_id]
        
        # Update session activity
        session.last_activity = datetime.now()
        session.execution_count += 1
        
        if tool_name not in session.tools_used:
            session.tools_used.append(tool_name)
        
        # Execute tool via sandbox API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sandbox_api_url}/api/tool/execute",
                    json={
                        "session_id": session.session_id,
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "require_approval": require_approval,
                        "agent_id": agent_id
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Log execution to database
                    await self._log_tool_execution(
                        agent_id, tool_name, parameters, result, "success"
                    )
                    
                    return result
                else:
                    error_msg = f"Tool execution failed: {response.status_code}"
                    await self._log_tool_execution(
                        agent_id, tool_name, parameters, {"error": error_msg}, "error"
                    )
                    return {"error": error_msg, "status": "failed"}
                    
        except Exception as e:
            error_msg = f"Tool execution exception: {str(e)}"
            await self._log_tool_execution(
                agent_id, tool_name, parameters, {"error": error_msg}, "error"
            )
            return {"error": error_msg, "status": "failed"}
    
    async def get_available_tools(self, agent_id: str) -> Dict[str, Any]:
        """Get list of available tools for an agent."""
        
        # Standard tools available to all agents
        tools = {
            "core": {
                "python_repl": {
                    "name": "Python REPL",
                    "description": "Execute Python code with state persistence",
                    "parameters": {"code": "string"},
                    "risk_level": "medium"
                },
                "shell": {
                    "name": "Shell Command",
                    "description": "Execute shell commands in sandbox",
                    "parameters": {"command": "string"},
                    "risk_level": "high"
                },
                "file_read": {
                    "name": "File Reader",
                    "description": "Read file contents",
                    "parameters": {"path": "string"},
                    "risk_level": "low"
                },
                "file_write": {
                    "name": "File Writer",
                    "description": "Write content to file",
                    "parameters": {"path": "string", "content": "string"},
                    "risk_level": "medium"
                },
                "calculator": {
                    "name": "Calculator",
                    "description": "Perform mathematical calculations",
                    "parameters": {"expression": "string"},
                    "risk_level": "low"
                }
            },
            "web": {
                "http_request": {
                    "name": "HTTP Client",
                    "description": "Make HTTP requests",
                    "parameters": {"method": "string", "url": "string", "headers": "object", "data": "object"},
                    "risk_level": "medium"
                },
                "use_browser": {
                    "name": "Web Browser",
                    "description": "Browse websites and extract information",
                    "parameters": {"url": "string", "action": "string"},
                    "risk_level": "medium"
                }
            },
            "ai": {
                "generate_image": {
                    "name": "Image Generator",
                    "description": "Generate images using AI models",
                    "parameters": {"prompt": "string", "style": "string"},
                    "risk_level": "low"
                },
                "use_llm": {
                    "name": "LLM Access",
                    "description": "Access other language models",
                    "parameters": {"prompt": "string", "model": "string"},
                    "risk_level": "low"
                }
            }
        }
        
        # Get agent-specific capabilities from database
        async with get_db() as db:
            result = await db.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if agent and agent.capabilities:
                # Filter tools based on agent capabilities
                agent_caps = [cap.get("name", "") for cap in agent.capabilities]
                
                # Add specialized tools based on capabilities
                if "code_generation" in agent_caps:
                    tools["ai"]["code_assistant"] = {
                        "name": "Code Assistant",
                        "description": "Advanced code generation and analysis",
                        "parameters": {"task": "string", "language": "string"},
                        "risk_level": "medium"
                    }
                
                if "data_analysis" in agent_caps:
                    tools["core"]["data_processor"] = {
                        "name": "Data Processor",
                        "description": "Process and analyze datasets",
                        "parameters": {"data": "object", "operation": "string"},
                        "risk_level": "low"
                    }
        
        return tools
    
    async def get_sandbox_status(self, agent_id: str) -> Dict[str, Any]:
        """Get current sandbox status for an agent."""
        
        if agent_id not in self.active_sessions:
            return {"status": "no_session", "message": "No active sandbox session"}
        
        session = self.active_sessions[agent_id]
        
        # Get detailed status from sandbox
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.sandbox_api_url}/api/sandbox/status/{session.session_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    sandbox_status = response.json()
                else:
                    sandbox_status = {"status": "unknown"}
                    
        except Exception:
            sandbox_status = {"status": "disconnected"}
        
        return {
            "session_id": session.session_id,
            "sandbox_id": session.sandbox_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "tools_used": session.tools_used,
            "execution_count": session.execution_count,
            "sandbox_details": sandbox_status
        }
    
    async def terminate_sandbox(self, agent_id: str) -> bool:
        """Terminate sandbox session for an agent."""
        
        if agent_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[agent_id]
        
        # Terminate remote sandbox
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(
                    f"{self.sandbox_api_url}/api/sandbox/{session.session_id}",
                    timeout=10.0
                )
        except Exception as e:
            print(f"Failed to terminate remote sandbox: {e}")
        
        # Update session status
        session.status = "terminated"
        
        # Remove from active sessions
        del self.active_sessions[agent_id]
        
        return True
    
    async def _log_tool_execution(
        self, 
        agent_id: str, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        result: Dict[str, Any], 
        status: str
    ):
        """Log tool execution to database."""
        
        # This would integrate with your existing logging system
        # For now, just print for debugging
        print(f"TOOL EXECUTION LOG:")
        print(f"  Agent: {agent_id}")
        print(f"  Tool: {tool_name}")
        print(f"  Status: {status}")
        print(f"  Parameters: {parameters}")
        print(f"  Result: {str(result)[:200]}...")
    
    async def request_human_approval(
        self, 
        agent_id: str, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> bool:
        """Request human approval for tool execution."""
        
        # This would integrate with your notification system
        # For now, return True for demo purposes
        print(f"HUMAN APPROVAL REQUEST:")
        print(f"  Agent {agent_id} wants to use {tool_name}")
        print(f"  Parameters: {parameters}")
        print(f"  Auto-approving for demo...")
        
        return True
    
    async def get_execution_history(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for an agent."""
        
        # This would query your database for execution logs
        # For now, return mock data
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "tool": "python_repl",
                "parameters": {"code": "print('Hello World!')"},
                "result": {"stdout": "Hello World!\n"},
                "status": "success"
            }
        ]


# Global sandbox manager instance
sandbox_manager = SandboxManager()


# API endpoints for sandbox integration
async def create_agent_sandbox(agent_id: str):
    """API endpoint to create sandbox for agent."""
    return await sandbox_manager.create_sandbox_session(agent_id)


async def execute_agent_tool(agent_id: str, tool_name: str, parameters: Dict[str, Any]):
    """API endpoint to execute tool for agent."""
    return await sandbox_manager.execute_tool_for_agent(agent_id, tool_name, parameters)


async def get_agent_tools(agent_id: str):
    """API endpoint to get available tools for agent."""
    return await sandbox_manager.get_available_tools(agent_id)


async def get_agent_sandbox_status(agent_id: str):
    """API endpoint to get sandbox status for agent."""
    return await sandbox_manager.get_sandbox_status(agent_id)
