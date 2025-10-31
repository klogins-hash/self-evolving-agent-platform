import chainlit as cl
import httpx
import asyncio
from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"


class AgentPlatformClient:
    """Client for interacting with the agent platform backend."""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents."""
        try:
            response = await self.client.get(f"{API_BASE}/agents/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent."""
        try:
            response = await self.client.post(f"{API_BASE}/agents/", json=agent_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        try:
            response = await self.client.get(f"{API_BASE}/tasks/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        try:
            response = await self.client.post(f"{API_BASE}/tasks/", json=task_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global client instance
platform_client = AgentPlatformClient()


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    await cl.Message(
        content="🤖 **Welcome to the Self-Evolving Agent Platform MVP!**\n\n"
                "I can help you:\n"
                "- 👥 **Manage Agents**: Create, view, and control AI agents\n"
                "- 📋 **Handle Tasks**: Create and track tasks for agents\n"
                "- 🔄 **Monitor System**: View agent status and task progress\n\n"
                "**Available Commands:**\n"
                "- `list agents` - Show all agents\n"
                "- `create agent` - Create a new agent\n"
                "- `list tasks` - Show all tasks\n"
                "- `create task` - Create a new task\n"
                "- `help` - Show this help message\n\n"
                "What would you like to do?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    user_input = message.content.lower().strip()
    
    # Command routing
    if user_input in ["help", "/help"]:
        await show_help()
    elif user_input in ["list agents", "show agents", "agents"]:
        await list_agents()
    elif user_input in ["create agent", "new agent", "add agent"]:
        await create_agent_flow()
    elif user_input in ["list tasks", "show tasks", "tasks"]:
        await list_tasks()
    elif user_input in ["create task", "new task", "add task"]:
        await create_task_flow()
    elif user_input in ["status", "system status"]:
        await show_system_status()
    else:
        await cl.Message(
            content="🤔 I didn't understand that command. Type `help` to see available commands."
        ).send()


async def show_help():
    """Show help information."""
    help_text = """
🆘 **Self-Evolving Agent Platform - Help**

**Agent Management:**
- `list agents` - View all agents in the system
- `create agent` - Start the agent creation wizard

**Task Management:**
- `list tasks` - View all tasks in the system  
- `create task` - Start the task creation wizard

**System:**
- `status` - Show system status
- `help` - Show this help message

**About the Platform:**
This MVP demonstrates a dual-agent architecture with:
- **Chief of Staff (CoS)**: Orchestrates and manages agent swarm
- **Master Operator (MO)**: Executes tasks and operations

The platform is designed to evolve and expand with additional capabilities.
    """
    await cl.Message(content=help_text).send()


async def list_agents():
    """List all agents in the system."""
    agents = await platform_client.get_agents()
    
    if not agents:
        await cl.Message(content="📭 No agents found. Create your first agent with `create agent`").send()
        return
    
    agent_list = "👥 **Current Agents:**\n\n"
    for agent in agents:
        status_emoji = {
            "active": "🟢",
            "idle": "🟡", 
            "busy": "🔴",
            "offline": "⚫",
            "error": "❌"
        }.get(agent.get("status", "idle"), "❓")
        
        agent_type_emoji = "👑" if agent.get("agent_type") == "chief_of_staff" else "⚙️"
        
        agent_list += f"{status_emoji} {agent_type_emoji} **{agent['name']}**\n"
        agent_list += f"   • Type: {agent.get('agent_type', 'unknown').replace('_', ' ').title()}\n"
        agent_list += f"   • Status: {agent.get('status', 'unknown').title()}\n"
        agent_list += f"   • Model: {agent.get('model_name', 'unknown')}\n"
        agent_list += f"   • ID: `{agent['id'][:8]}...`\n\n"
    
    await cl.Message(content=agent_list).send()


async def create_agent_flow():
    """Interactive agent creation flow."""
    await cl.Message(content="🛠️ **Agent Creation Wizard**\n\nLet's create a new agent step by step.").send()
    
    # Get agent name
    name_response = await cl.AskUserMessage(
        content="What should we name this agent?",
        timeout=60
    ).send()
    
    if not name_response:
        await cl.Message(content="❌ Agent creation cancelled.").send()
        return
    
    agent_name = name_response['output']
    
    # Get agent type
    type_response = await cl.AskUserMessage(
        content="What type of agent should this be?\n\n"
                "1️⃣ **Chief of Staff** (CoS) - Orchestrates and manages\n"
                "2️⃣ **Master Operator** (MO) - Executes tasks\n\n"
                "Enter 1 or 2:",
        timeout=60
    ).send()
    
    if not type_response:
        await cl.Message(content="❌ Agent creation cancelled.").send()
        return
    
    agent_type = "chief_of_staff" if type_response['output'].strip() == "1" else "master_operator"
    
    # Create the agent
    agent_data = {
        "name": agent_name,
        "agent_type": agent_type,
        "system_prompt": f"You are {agent_name}, a {agent_type.replace('_', ' ')} agent in the self-evolving platform.",
        "model_provider": "openrouter",
        "model_name": "auto"
    }
    
    result = await platform_client.create_agent(agent_data)
    
    if result.get("success"):
        agent = result.get("agent", {})
        await cl.Message(
            content=f"✅ **Agent Created Successfully!**\n\n"
                   f"🤖 **Name:** {agent.get('name')}\n"
                   f"🏷️ **Type:** {agent.get('agent_type', '').replace('_', ' ').title()}\n"
                   f"🆔 **ID:** `{agent.get('id', '')[:8]}...`\n"
                   f"📊 **Status:** {agent.get('status', '').title()}\n\n"
                   f"Your agent is ready to use!"
        ).send()
    else:
        await cl.Message(
            content=f"❌ **Failed to create agent:** {result.get('error', 'Unknown error')}"
        ).send()


async def list_tasks():
    """List all tasks in the system."""
    tasks = await platform_client.get_tasks()
    
    if not tasks:
        await cl.Message(content="📭 No tasks found. Create your first task with `create task`").send()
        return
    
    task_list = "📋 **Current Tasks:**\n\n"
    for task in tasks:
        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫"
        }.get(task.get("status", "pending"), "❓")
        
        priority_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠", 
            "urgent": "🔴"
        }.get(task.get("priority", "medium"), "❓")
        
        task_list += f"{status_emoji} {priority_emoji} **{task['title']}**\n"
        task_list += f"   • Status: {task.get('status', 'unknown').replace('_', ' ').title()}\n"
        task_list += f"   • Priority: {task.get('priority', 'unknown').title()}\n"
        if task.get('assigned_agent_id'):
            task_list += f"   • Assigned: Agent `{task['assigned_agent_id'][:8]}...`\n"
        task_list += f"   • ID: `{task['id'][:8]}...`\n\n"
    
    await cl.Message(content=task_list).send()


async def create_task_flow():
    """Interactive task creation flow."""
    await cl.Message(content="📝 **Task Creation Wizard**\n\nLet's create a new task step by step.").send()
    
    # Get task title
    title_response = await cl.AskUserMessage(
        content="What's the title of this task?",
        timeout=60
    ).send()
    
    if not title_response:
        await cl.Message(content="❌ Task creation cancelled.").send()
        return
    
    task_title = title_response['output']
    
    # Get task description
    desc_response = await cl.AskUserMessage(
        content="Please provide a description for this task:",
        timeout=60
    ).send()
    
    if not desc_response:
        await cl.Message(content="❌ Task creation cancelled.").send()
        return
    
    task_description = desc_response['output']
    
    # Get priority
    priority_response = await cl.AskUserMessage(
        content="What's the priority of this task?\n\n"
                "1️⃣ Low\n2️⃣ Medium\n3️⃣ High\n4️⃣ Urgent\n\n"
                "Enter 1-4:",
        timeout=60
    ).send()
    
    priority_map = {"1": "low", "2": "medium", "3": "high", "4": "urgent"}
    priority = priority_map.get(priority_response['output'].strip() if priority_response else "2", "medium")
    
    # Create the task
    task_data = {
        "title": task_title,
        "description": task_description,
        "priority": priority
    }
    
    result = await platform_client.create_task(task_data)
    
    if result.get("success"):
        task = result.get("task", {})
        await cl.Message(
            content=f"✅ **Task Created Successfully!**\n\n"
                   f"📝 **Title:** {task.get('title')}\n"
                   f"📋 **Description:** {task.get('description')}\n"
                   f"🏷️ **Priority:** {task.get('priority', '').title()}\n"
                   f"📊 **Status:** {task.get('status', '').replace('_', ' ').title()}\n"
                   f"🆔 **ID:** `{task.get('id', '')[:8]}...`\n\n"
                   f"Your task is ready to be assigned to an agent!"
        ).send()
    else:
        await cl.Message(
            content=f"❌ **Failed to create task:** {result.get('error', 'Unknown error')}"
        ).send()


async def show_system_status():
    """Show system status overview."""
    agents = await platform_client.get_agents()
    tasks = await platform_client.get_tasks()
    
    # Count agents by status
    agent_status_counts = {}
    for agent in agents:
        status = agent.get("status", "unknown")
        agent_status_counts[status] = agent_status_counts.get(status, 0) + 1
    
    # Count tasks by status
    task_status_counts = {}
    for task in tasks:
        status = task.get("status", "unknown")
        task_status_counts[status] = task_status_counts.get(status, 0) + 1
    
    status_text = f"""
📊 **System Status Overview**

**Agents:** {len(agents)} total
{chr(10).join([f"   • {status.title()}: {count}" for status, count in agent_status_counts.items()])}

**Tasks:** {len(tasks)} total  
{chr(10).join([f"   • {status.replace('_', ' ').title()}: {count}" for status, count in task_status_counts.items()])}

**Backend:** Connected to {BACKEND_URL}
**Status:** 🟢 Operational
    """
    
    await cl.Message(content=status_text).send()


if __name__ == "__main__":
    cl.run()
