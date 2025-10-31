"""
Strands Autonomous Agent UI
Chainlit interface for fully autonomous multi-step agents
"""

import chainlit as cl
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add paths
sys.path.append('/Users/franksimpson/Downloads/self-evolving-agent-platform/backend')
sys.path.append('/Users/franksimpson/Downloads/strands-tools/src')

try:
    from strands_autonomous_agent import StrandsAutonomousAgent, AutonomousTask, create_autonomous_agent
    STRANDS_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Strands autonomous agent not available: {e}")
    STRANDS_AGENT_AVAILABLE = False

# Global agent instances
active_agents: Dict[str, StrandsAutonomousAgent] = {}


@cl.set_starters
async def set_starters():
    """Set up starter prompts for autonomous agents."""
    return [
        cl.Starter(
            label="🤖 Create Autonomous Agent",
            message="Create a new autonomous agent",
            icon="/public/autonomous.svg",
        ),
        cl.Starter(
            label="📊 Bitcoin & Peanut Butter Analysis",
            message="awesome! can you write me a report about how the current price of bitcoin is being affected by the current price of peanut butter",
            icon="/public/analysis.svg",
        ),
        cl.Starter(
            label="🔬 Research Task",
            message="Research the latest developments in AI and write a comprehensive summary",
            icon="/public/research.svg",
        ),
        cl.Starter(
            label="🎨 Creative Project",
            message="Create a marketing campaign for a sustainable fashion brand including visuals and copy",
            icon="/public/creative.svg",
        ),
    ]


@cl.set_chat_profiles
async def chat_profile():
    """Set up chat profiles for different autonomous agent types."""
    return [
        cl.ChatProfile(
            name="research_agent",
            markdown_description="**Research Agent** - Specializes in data gathering, analysis, and report generation.",
            icon="🔬",
        ),
        cl.ChatProfile(
            name="creative_agent",
            markdown_description="**Creative Agent** - Focuses on content creation, design, and marketing materials.",
            icon="🎨",
        ),
        cl.ChatProfile(
            name="technical_agent",
            markdown_description="**Technical Agent** - Handles coding, system administration, and technical tasks.",
            icon="💻",
        ),
        cl.ChatProfile(
            name="general_agent",
            markdown_description="**General Agent** - Versatile agent capable of handling diverse tasks autonomously.",
            icon="🤖",
        ),
    ]


@cl.on_chat_start
async def start():
    """Initialize autonomous agent session."""
    
    if not STRANDS_AGENT_AVAILABLE:
        await cl.ErrorMessage(
            content="❌ **Strands Framework Not Available**\n\n"
                   "The autonomous agent system requires the Strands framework. "
                   "Please install it first:\n\n"
                   "```bash\n"
                   "pip install strands-agents-tools\n"
                   "```"
        ).send()
        return
    
    # Get chat profile
    chat_profile = cl.user_session.get("chat_profile", "general_agent")
    user_id = cl.user_session.get("id", "demo_user")
    agent_id = f"{chat_profile}_{user_id}_{datetime.now().strftime('%H%M%S')}"
    
    # Create autonomous agent
    try:
        agent = create_autonomous_agent(agent_id, chat_profile)
        active_agents[agent_id] = agent
        cl.user_session.set("agent", agent)
        cl.user_session.set("agent_id", agent_id)
        
        # Welcome message
        welcome_content = f"""# 🤖 **Autonomous Agent Ready!**

Welcome to the **Strands-powered autonomous agent system**! Your agent is now ready to handle complex, multi-step tasks completely autonomously.

## 🧠 **Agent Capabilities**
Your **{chat_profile.replace('_', ' ').title()}** can:

### 🛠️ **Core Tools** (20+ available)
- **🐍 Python Execution**: Run complex data analysis and processing
- **💻 Shell Commands**: Execute system operations and scripts  
- **📁 File Operations**: Read, write, and edit files intelligently
- **🌐 Web Research**: Browse websites and make API calls
- **🧮 Mathematical Analysis**: Perform advanced calculations
- **🖼️ Image Generation**: Create AI-powered visuals
- **🧠 Memory Management**: Store and retrieve information across sessions

### 🚀 **Autonomous Features**
- **🎯 Multi-Step Planning**: Breaks down complex tasks automatically
- **🔄 Adaptive Execution**: Modifies approach based on results
- **🤝 Swarm Intelligence**: Coordinates multiple AI perspectives
- **📊 Self-Evaluation**: Assesses progress and success
- **📝 Comprehensive Reporting**: Documents entire process
- **🧠 Continuous Learning**: Improves from each task

### 🎮 **How It Works**
1. **Give me any complex task** - I'll analyze and plan autonomously
2. **I'll think through the problem** - Using advanced reasoning
3. **I'll execute step-by-step** - With real tools and actions
4. **I'll adapt as needed** - Based on intermediate results
5. **I'll deliver complete results** - With full documentation

## 💬 **Example Requests**
- *"Research and analyze market trends for electric vehicles"*
- *"Create a complete marketing campaign with visuals and copy"*
- *"Build a data analysis pipeline and generate insights"*
- *"Write a comprehensive report on renewable energy technologies"*

**Agent ID**: `{agent_id}`
**Status**: 🟢 Ready for autonomous operation
**Framework**: Strands AI Tools

Just describe what you want accomplished - I'll handle the rest autonomously! 🚀"""

        actions = [
            cl.Action(name="show_tools", value="show_tools", label="🛠️ Show All Tools", payload={}),
            cl.Action(name="example_task", value="example", label="📋 Run Example Task", payload={}),
            cl.Action(name="agent_status", value="status", label="📊 Agent Status", payload={}),
        ]
        
        await cl.Message(content=welcome_content, actions=actions).send()
        
    except Exception as e:
        await cl.ErrorMessage(
            content=f"❌ **Failed to initialize autonomous agent**\n\n"
                   f"Error: {str(e)}\n\n"
                   f"Please check that the Strands framework is properly installed."
        ).send()


@cl.action_callback("show_tools")
async def show_available_tools(action):
    """Display all available Strands tools."""
    
    tools_content = """# 🛠️ **Strands Framework Tools**

Your autonomous agent has access to these powerful tools:

## 📁 **File & Data Operations**
- **`file_read`** - Read and analyze files with syntax highlighting
- **`file_write`** - Create and modify files safely
- **`editor`** - Advanced text editing with intelligent modifications
- **`python_repl`** - Execute Python code with state persistence

## 💻 **System & Web**
- **`shell`** - Execute shell commands securely
- **`http_request`** - Make HTTP requests with authentication
- **`use_browser`** - Browse websites and extract information
- **`environment`** - Manage environment variables safely

## 🧠 **AI & Intelligence**
- **`think`** - Advanced reasoning and problem analysis
- **`use_llm`** - Access other language models for specialized tasks
- **`generate_image`** - Create AI-powered images
- **`swarm`** - Coordinate multiple AI agents for complex problems

## 📊 **Analysis & Math**
- **`calculator`** - Advanced mathematical operations
- **`memory`** - Store and retrieve information across sessions
- **`retrieve`** - Search knowledge bases
- **`journal`** - Create structured logs and documentation

## 🔄 **Workflow & Coordination**
- **`workflow`** - Define and execute multi-step processes
- **`batch`** - Run multiple tools in parallel
- **`agent_graph`** - Visualize agent relationships
- **`current_time`** - Get current time information

## 🎯 **Autonomous Operation**
The agent uses these tools automatically based on your requests. You don't need to specify which tools to use - the agent will:

1. **Analyze your request** using `think`
2. **Plan the workflow** using `workflow`
3. **Execute tools** as needed (`python_repl`, `http_request`, etc.)
4. **Coordinate if complex** using `swarm`
5. **Document results** using `journal`
6. **Store learnings** using `memory`

**Just describe what you want - the agent handles tool selection and execution!** 🚀"""
    
    await cl.Message(content=tools_content).send()


@cl.action_callback("example")
async def run_example_task(action):
    """Run an example autonomous task."""
    
    agent = cl.user_session.get("agent")
    if not agent:
        await cl.ErrorMessage(content="No agent available. Please restart the chat.").send()
        return
    
    await cl.Message(content="🚀 **Starting Example Autonomous Task**\n\n"
                           "I'll demonstrate autonomous operation by analyzing Bitcoin and peanut butter prices...\n\n"
                           "*This may take a few minutes as I work through the task autonomously.*").send()
    
    # Create example task
    example_request = "Research the current price of Bitcoin and peanut butter, analyze any potential correlations, and write a brief report with your findings"
    
    # Execute autonomously
    try:
        result = await agent.handle_autonomous_request(example_request)
        
        # Display results
        status_emoji = "✅" if result.get("status") == "completed" else "⚠️"
        
        result_content = f"""{status_emoji} **Autonomous Task Complete**

**Status**: {result.get('status', 'unknown')}
**Task ID**: {result.get('task_id', 'N/A')}
**Completed**: {result.get('timestamp', 'N/A')}

**Evaluation**:
{result.get('evaluation', 'No evaluation available')}

**Full Report**:
{result.get('report', 'No report generated')}

The agent worked completely autonomously to analyze your request, plan the execution, gather data, perform analysis, and generate this report! 🤖✨"""
        
        await cl.Message(content=result_content).send()
        
    except Exception as e:
        await cl.ErrorMessage(content=f"❌ **Autonomous execution failed**: {str(e)}").send()


@cl.action_callback("status")
async def show_agent_status(action):
    """Show current agent status and capabilities."""
    
    agent = cl.user_session.get("agent")
    agent_id = cl.user_session.get("agent_id", "unknown")
    
    if not agent:
        await cl.ErrorMessage(content="No agent available.").send()
        return
    
    status_content = f"""# 📊 **Agent Status Report**

**Agent ID**: `{agent_id}`
**Type**: {agent.agent_type.replace('_', ' ').title()}
**Framework**: Strands AI Tools
**Status**: 🟢 Active and Ready

## 🧠 **Autonomous Capabilities**
- ✅ **Multi-Step Planning**: Can break down complex tasks
- ✅ **Tool Selection**: Automatically chooses appropriate tools
- ✅ **Adaptive Execution**: Modifies approach based on results
- ✅ **Self-Evaluation**: Assesses own performance
- ✅ **Memory Persistence**: Learns from each interaction
- ✅ **Swarm Coordination**: Can work with other agents

## 📈 **Execution History**
- **Tasks Completed**: {len(agent.execution_history)}
- **Memory Entries**: {len(agent.memory_store)}
- **Last Activity**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 **Ready For**
- Research and analysis tasks
- Content creation and writing
- Data processing and visualization
- Web scraping and API integration
- Image generation and processing
- Complex multi-step workflows
- Collaborative problem solving

**The agent is fully autonomous and ready to handle any complex task you provide!** 🚀"""
    
    await cl.Message(content=status_content).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages with autonomous agent processing."""
    
    agent = cl.user_session.get("agent")
    if not agent:
        await cl.ErrorMessage(content="No agent available. Please restart the chat.").send()
        return
    
    user_request = message.content.strip()
    
    # Show that agent is thinking and planning
    thinking_msg = await cl.Message(
        content="🧠 **Autonomous Agent Thinking...**\n\n"
               "I'm analyzing your request and creating an execution plan. "
               "This involves:\n\n"
               "1. 🎯 **Understanding** your objective\n"
               "2. 📋 **Planning** the workflow steps\n"
               "3. 🛠️ **Selecting** appropriate tools\n"
               "4. 🚀 **Executing** autonomously\n"
               "5. 📊 **Evaluating** results\n\n"
               "*Please wait while I work through this autonomously...*"
    ).send()
    
    try:
        # Execute the request autonomously
        result = await agent.handle_autonomous_request(user_request)
        
        # Update the thinking message with results
        status_emoji = "✅" if result.get("status") == "completed" else "⚠️"
        
        final_content = f"""{status_emoji} **Autonomous Execution Complete!**

**Your Request**: "{user_request}"

**Status**: {result.get('status', 'unknown')}
**Task ID**: {result.get('task_id', 'N/A')}
**Completed**: {result.get('timestamp', datetime.now().isoformat())}

## 🎯 **What I Did Autonomously**
I analyzed your request, created a multi-step execution plan, selected and used appropriate tools, adapted my approach based on intermediate results, and generated a comprehensive report.

## 📋 **Execution Summary**
{result.get('execution_summary', {}).get('success', 'Execution details not available')}

## 🧠 **My Evaluation**
{result.get('evaluation', 'No evaluation available')}

## 📄 **Generated Report**
{result.get('report', 'No detailed report available')}

---
*This entire process was completed autonomously using the Strands framework with 20+ AI tools!* 🤖✨"""
        
        # Update the original message
        thinking_msg.content = final_content
        await thinking_msg.update()
        
        # If there were files created, mention them
        if "file_write" in str(result):
            await cl.Message(
                content="📁 **Files Created**: Check your workspace for generated files from this autonomous task!"
            ).send()
        
    except Exception as e:
        error_content = f"""❌ **Autonomous Execution Error**

I encountered an issue while processing your request autonomously:

**Error**: {str(e)}

**What happened**: The autonomous agent system experienced an unexpected error during execution.

**Next steps**: 
- Try rephrasing your request
- Check that all required dependencies are installed
- Restart the chat if the issue persists

I'm designed to handle complex tasks autonomously, so this error is unexpected. Please try again! 🔄"""
        
        thinking_msg.content = error_content
        await thinking_msg.update()


@cl.on_chat_end
async def cleanup():
    """Clean up agent resources when chat ends."""
    agent_id = cl.user_session.get("agent_id")
    if agent_id and agent_id in active_agents:
        del active_agents[agent_id]
        print(f"🧹 Cleaned up autonomous agent: {agent_id}")


if __name__ == "__main__":
    cl.run()
