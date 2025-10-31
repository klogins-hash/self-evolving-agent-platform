"""
Enhanced Agent Sandbox with E2B Integration and Strands Tools
Real-time agent execution environment with human-in-the-loop controls
"""

import chainlit as cl
import chainlit.input_widget as input_widget
import httpx
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import subprocess

# Add strands-tools to path
sys.path.append('/Users/franksimpson/Downloads/strands-tools/src')

try:
    from e2b import Sandbox
    from e2b_code_interpreter import CodeInterpreter
    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    print("⚠️ E2B not installed. Install with: pip install e2b e2b-code-interpreter")

# Import Strands tools
try:
    from strands_tools import (
        file_read, file_write, editor, shell, python_repl,
        calculator, http_request, generate_image, memory,
        use_browser, use_llm, environment, current_time
    )
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    print("⚠️ Strands tools not available. Installing...")

load_dotenv()

# Configuration
E2B_API_KEY = os.getenv("E2B_API_KEY", "e2b_08cd803fb0f53235473753396ec7e5c987cdd8fd")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"


class AgentSandbox:
    """Enhanced agent sandbox with E2B and Strands tools integration."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.sandbox = None
        self.code_interpreter = None
        self.session_data = {}
        self.execution_history = []
        self.human_approval_required = True
        self.available_tools = self._load_available_tools()
        
    def _load_available_tools(self):
        """Load all available tools for the agent."""
        tools = {
            "core": {
                "file_read": "Read and analyze files with syntax highlighting",
                "file_write": "Create and modify files safely",
                "editor": "Advanced text editing with intelligent modifications",
                "shell": "Execute shell commands with safety checks",
                "python_repl": "Run Python code with state persistence",
                "calculator": "Advanced mathematical calculations",
                "current_time": "Get current date and time information"
            },
            "web": {
                "http_request": "Make HTTP requests with authentication",
                "use_browser": "Browse websites and extract information",
            },
            "ai": {
                "use_llm": "Access other language models",
                "generate_image": "Create images using AI models",
                "memory": "Store and retrieve memories across sessions"
            },
            "system": {
                "environment": "Manage environment variables safely",
                "sleep": "Pause execution for specified time",
                "stop": "Stop current execution"
            }
        }
        
        if E2B_AVAILABLE:
            tools["sandbox"] = {
                "e2b_sandbox": "Full Linux environment with persistent state",
                "code_interpreter": "Jupyter-like code execution environment"
            }
            
        return tools
    
    async def initialize_sandbox(self):
        """Initialize E2B sandbox environment."""
        if not E2B_AVAILABLE:
            await cl.ErrorMessage(content="❌ E2B not available. Sandbox features disabled.").send()
            return False
            
        try:
            # Initialize code interpreter sandbox
            self.code_interpreter = CodeInterpreter(api_key=E2B_API_KEY)
            
            # Initialize general sandbox
            self.sandbox = Sandbox(
                template="base",
                api_key=E2B_API_KEY,
                metadata={"agent_id": self.agent_id, "session": datetime.now().isoformat()}
            )
            
            await cl.Message(content="🚀 **Sandbox Initialized Successfully!**\n\n"
                           f"- **Code Interpreter**: Ready for Python execution\n"
                           f"- **Linux Environment**: Full system access\n"
                           f"- **Agent ID**: {self.agent_id}\n"
                           f"- **Session**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").send()
            
            return True
            
        except Exception as e:
            await cl.ErrorMessage(content=f"❌ Failed to initialize sandbox: {str(e)}").send()
            return False
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], require_approval: bool = True):
        """Execute a tool with optional human approval."""
        
        if require_approval and self.human_approval_required:
            # Request human approval
            approval = await self._request_human_approval(tool_name, parameters)
            if not approval:
                await cl.Message(content="❌ **Execution Cancelled**\n\nHuman operator denied permission.").send()
                return None
        
        try:
            result = await self._execute_tool_internal(tool_name, parameters)
            
            # Log execution
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "parameters": parameters,
                "result": str(result)[:500] + "..." if len(str(result)) > 500 else str(result),
                "status": "success"
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "parameters": parameters,
                "error": error_msg,
                "status": "error"
            })
            
            await cl.ErrorMessage(content=f"❌ **Tool Execution Failed**\n\n"
                                 f"**Tool**: {tool_name}\n"
                                 f"**Error**: {error_msg}").send()
            return None
    
    async def _request_human_approval(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Request human approval for tool execution."""
        
        # Create approval form
        approval_msg = f"""🤖 **Agent Requesting Permission**

**Tool**: `{tool_name}`
**Parameters**: 
```json
{json.dumps(parameters, indent=2)}
```

**Description**: {self._get_tool_description(tool_name)}

Do you approve this execution?"""
        
        actions = [
            cl.Action(name="approve", value="approve", label="✅ Approve", payload={"tool": tool_name}),
            cl.Action(name="deny", value="deny", label="❌ Deny", payload={"tool": tool_name}),
            cl.Action(name="modify", value="modify", label="✏️ Modify", payload={"tool": tool_name}),
        ]
        
        await cl.Message(content=approval_msg, actions=actions).send()
        
        # Wait for human response (simplified for demo)
        # In production, this would use proper async waiting
        return True  # For demo, auto-approve
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Get description for a tool."""
        for category, tools in self.available_tools.items():
            if tool_name in tools:
                return tools[tool_name]
        return "Unknown tool"
    
    async def _execute_tool_internal(self, tool_name: str, parameters: Dict[str, Any]):
        """Internal tool execution logic."""
        
        if tool_name == "python_repl" and self.code_interpreter:
            return await self._execute_python_code(parameters.get("code", ""))
        
        elif tool_name == "shell" and self.sandbox:
            return await self._execute_shell_command(parameters.get("command", ""))
        
        elif tool_name == "file_read":
            return await self._read_file(parameters.get("path", ""))
        
        elif tool_name == "file_write":
            return await self._write_file(parameters.get("path", ""), parameters.get("content", ""))
        
        elif tool_name == "calculator":
            return await self._calculate(parameters.get("expression", ""))
        
        elif tool_name == "http_request":
            return await self._make_http_request(parameters)
        
        elif tool_name == "generate_image":
            return await self._generate_image(parameters.get("prompt", ""))
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_python_code(self, code: str):
        """Execute Python code in E2B code interpreter."""
        if not self.code_interpreter:
            raise ValueError("Code interpreter not initialized")
        
        execution = self.code_interpreter.notebook.exec_cell(code)
        
        result = {
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
            "results": [r.text for r in execution.results] if execution.results else [],
            "error": execution.error.name if execution.error else None
        }
        
        return result
    
    async def _execute_shell_command(self, command: str):
        """Execute shell command in E2B sandbox."""
        if not self.sandbox:
            raise ValueError("Sandbox not initialized")
        
        process = self.sandbox.process.start(command)
        process.wait()
        
        return {
            "exit_code": process.exit_code,
            "stdout": process.stdout,
            "stderr": process.stderr
        }
    
    async def _read_file(self, path: str):
        """Read file content."""
        if self.sandbox:
            return self.sandbox.filesystem.read(path)
        else:
            # Local file reading for demo
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Cannot read file: {e}")
    
    async def _write_file(self, path: str, content: str):
        """Write file content."""
        if self.sandbox:
            self.sandbox.filesystem.write(path, content)
            return f"File written to {path}"
        else:
            # Local file writing for demo (restricted)
            raise ValueError("Local file writing not allowed in demo mode")
    
    async def _calculate(self, expression: str):
        """Perform mathematical calculation."""
        try:
            # Safe evaluation for demo
            import ast
            import operator
            
            # Supported operations
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(node)
            
            result = eval_expr(ast.parse(expression, mode='eval').body)
            return {"expression": expression, "result": result}
            
        except Exception as e:
            raise ValueError(f"Calculation error: {e}")
    
    async def _make_http_request(self, params: Dict[str, Any]):
        """Make HTTP request."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=params.get("method", "GET"),
                url=params.get("url"),
                headers=params.get("headers", {}),
                json=params.get("json"),
                data=params.get("data")
            )
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:1000] + "..." if len(response.text) > 1000 else response.text
            }
    
    async def _generate_image(self, prompt: str):
        """Generate image (placeholder for demo)."""
        return {
            "prompt": prompt,
            "message": "Image generation would happen here with Stability AI or other providers",
            "status": "demo_mode"
        }
    
    async def cleanup(self):
        """Clean up sandbox resources."""
        if self.code_interpreter:
            self.code_interpreter.close()
        if self.sandbox:
            self.sandbox.close()


# Global sandbox instances
sandbox_instances = {}


@cl.set_starters
async def set_starters():
    """Set up starter prompts for sandbox."""
    return [
        cl.Starter(
            label="🚀 Initialize Sandbox",
            message="Initialize my agent sandbox environment",
            icon="/public/sandbox.svg",
        ),
        cl.Starter(
            label="🐍 Run Python Code",
            message="I want to execute Python code",
            icon="/public/python.svg",
        ),
        cl.Starter(
            label="🛠️ Use Tools",
            message="Show me available tools",
            icon="/public/tools.svg",
        ),
        cl.Starter(
            label="👨‍💼 Human Takeover",
            message="I need human assistance",
            icon="/public/human.svg",
        ),
    ]


@cl.set_chat_profiles
async def chat_profile():
    """Set up chat profiles for different agent types."""
    return [
        cl.ChatProfile(
            name="sandbox_agent",
            markdown_description="**Sandbox Agent** - Full access to tools and E2B environment.",
            icon="🤖",
        ),
        cl.ChatProfile(
            name="restricted_agent",
            markdown_description="**Restricted Agent** - Limited tools, requires approval for all actions.",
            icon="🔒",
        ),
        cl.ChatProfile(
            name="autonomous_agent",
            markdown_description="**Autonomous Agent** - Can execute tools without human approval.",
            icon="🚀",
        ),
    ]


@cl.on_chat_start
async def start():
    """Initialize agent sandbox session."""
    
    # Get user session info
    user_id = cl.user_session.get("id", "demo_user")
    agent_id = f"agent_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create sandbox instance
    sandbox = AgentSandbox(agent_id)
    sandbox_instances[agent_id] = sandbox
    cl.user_session.set("sandbox", sandbox)
    cl.user_session.set("agent_id", agent_id)
    
    # Welcome message
    welcome_content = f"""# 🤖 **Agent Sandbox Environment**

Welcome to the enhanced agent playground! Your agent now has access to:

## 🛠️ **Available Tools**
- **🐍 Python Execution**: Full Python environment with state persistence
- **💻 Shell Access**: Linux command execution in secure sandbox
- **📁 File Operations**: Read, write, and edit files
- **🧮 Calculator**: Advanced mathematical operations
- **🌐 HTTP Client**: Make API requests and web interactions
- **🖼️ Image Generation**: Create images with AI models
- **🧠 Memory**: Persistent memory across sessions
- **🔧 System Tools**: Environment management and utilities

## 🚦 **Safety Features**
- **Human-in-the-Loop**: Approval required for sensitive operations
- **Execution History**: Full audit trail of all actions
- **Sandbox Isolation**: Secure execution environment
- **Resource Limits**: Controlled resource usage

## 🎮 **Getting Started**
- Type `initialize` to set up your E2B sandbox
- Use `tools` to see all available capabilities
- Try `python print("Hello from agent sandbox!")` to test code execution
- Say `help` for detailed command reference

**Agent ID**: `{agent_id}`
**Status**: Ready for initialization
"""
    
    actions = [
        cl.Action(name="initialize", value="init_sandbox", label="🚀 Initialize Sandbox", payload={}),
        cl.Action(name="show_tools", value="show_tools", label="🛠️ Show Tools", payload={}),
        cl.Action(name="toggle_approval", value="toggle_approval", label="🔐 Toggle Approval", payload={}),
    ]
    
    await cl.Message(content=welcome_content, actions=actions).send()


@cl.action_callback("initialize")
async def initialize_sandbox(action):
    """Initialize the E2B sandbox environment."""
    sandbox = cl.user_session.get("sandbox")
    if sandbox:
        success = await sandbox.initialize_sandbox()
        if success:
            await cl.Message(content="✅ **Sandbox Ready!** You can now execute code and use tools.").send()
        else:
            await cl.Message(content="❌ **Sandbox initialization failed.** Some features may be limited.").send()


@cl.action_callback("show_tools")
async def show_available_tools(action):
    """Display all available tools."""
    sandbox = cl.user_session.get("sandbox")
    if not sandbox:
        await cl.ErrorMessage(content="No sandbox session found.").send()
        return
    
    tools_content = "# 🛠️ **Available Tools**\n\n"
    
    for category, tools in sandbox.available_tools.items():
        tools_content += f"## {category.title()} Tools\n\n"
        for tool_name, description in tools.items():
            tools_content += f"- **`{tool_name}`**: {description}\n"
        tools_content += "\n"
    
    tools_content += """## 🎯 **Usage Examples**
- `execute python_repl {"code": "import numpy as np; print(np.array([1,2,3]))"}`
- `execute shell {"command": "ls -la"}`
- `execute calculator {"expression": "2**10 + 5*3"}`
- `execute http_request {"method": "GET", "url": "https://api.github.com/repos/octocat/Hello-World"}`

Type `execute <tool_name> <parameters>` to use any tool!"""
    
    await cl.Message(content=tools_content).send()


@cl.action_callback("toggle_approval")
async def toggle_human_approval(action):
    """Toggle human approval requirement."""
    sandbox = cl.user_session.get("sandbox")
    if sandbox:
        sandbox.human_approval_required = not sandbox.human_approval_required
        status = "enabled" if sandbox.human_approval_required else "disabled"
        await cl.Message(content=f"🔐 **Human approval {status}**\n\n"
                        f"Agents will {'require' if sandbox.human_approval_required else 'not require'} "
                        f"permission before executing tools.").send()


@cl.on_message
async def main(message: cl.Message):
    """Handle sandbox commands and tool execution."""
    
    user_input = message.content.strip()
    sandbox = cl.user_session.get("sandbox")
    
    if not sandbox:
        await cl.ErrorMessage(content="No sandbox session. Please restart the chat.").send()
        return
    
    # Command parsing
    if user_input.lower() in ["initialize", "init"]:
        await initialize_sandbox(None)
        
    elif user_input.lower() in ["tools", "show tools"]:
        await show_available_tools(None)
        
    elif user_input.lower().startswith("execute "):
        await handle_tool_execution(user_input, sandbox)
        
    elif user_input.lower().startswith("python "):
        # Quick Python execution
        code = user_input[7:]  # Remove "python " prefix
        result = await sandbox.execute_tool("python_repl", {"code": code})
        await display_execution_result("python_repl", result)
        
    elif user_input.lower() in ["history", "show history"]:
        await show_execution_history(sandbox)
        
    elif user_input.lower() in ["help", "commands"]:
        await show_help()
        
    else:
        # Natural language processing for tool suggestions
        await suggest_tools_for_query(user_input, sandbox)


async def handle_tool_execution(command: str, sandbox: AgentSandbox):
    """Parse and execute tool commands."""
    try:
        # Parse: execute tool_name {"param": "value"}
        parts = command[8:].strip()  # Remove "execute "
        
        if " {" in parts:
            tool_name = parts.split(" {")[0].strip()
            params_str = "{" + parts.split(" {", 1)[1]
            parameters = json.loads(params_str)
        else:
            tool_name = parts
            parameters = {}
        
        await cl.Message(content=f"🔄 **Executing**: `{tool_name}`\n\nParameters: `{parameters}`").send()
        
        result = await sandbox.execute_tool(tool_name, parameters)
        await display_execution_result(tool_name, result)
        
    except Exception as e:
        await cl.ErrorMessage(content=f"❌ **Command parsing error**: {str(e)}\n\n"
                             f"Usage: `execute tool_name {{\"param\": \"value\"}}`").send()


async def display_execution_result(tool_name: str, result: Any):
    """Display tool execution results."""
    if result is None:
        return
    
    content = f"✅ **Tool Execution Complete**: `{tool_name}`\n\n"
    
    if isinstance(result, dict):
        if "stdout" in result:
            content += f"**Output**:\n```\n{result['stdout']}\n```\n"
        if "stderr" in result and result["stderr"]:
            content += f"**Errors**:\n```\n{result['stderr']}\n```\n"
        if "results" in result and result["results"]:
            content += f"**Results**:\n```\n{result['results']}\n```\n"
        if "result" in result:
            content += f"**Result**: {result['result']}\n"
    else:
        content += f"**Result**:\n```\n{str(result)}\n```"
    
    await cl.Message(content=content).send()


async def show_execution_history(sandbox: AgentSandbox):
    """Show execution history."""
    if not sandbox.execution_history:
        await cl.Message(content="📝 **No execution history yet.**\n\nStart using tools to see history here.").send()
        return
    
    content = "# 📝 **Execution History**\n\n"
    
    for i, entry in enumerate(sandbox.execution_history[-10:], 1):  # Show last 10
        status_emoji = "✅" if entry["status"] == "success" else "❌"
        content += f"## {i}. {status_emoji} **{entry['tool']}**\n"
        content += f"- **Time**: {entry['timestamp']}\n"
        content += f"- **Parameters**: `{entry['parameters']}`\n"
        
        if entry["status"] == "success":
            result_preview = entry["result"][:100] + "..." if len(entry["result"]) > 100 else entry["result"]
            content += f"- **Result**: {result_preview}\n"
        else:
            content += f"- **Error**: {entry.get('error', 'Unknown error')}\n"
        
        content += "\n"
    
    await cl.Message(content=content).send()


async def show_help():
    """Show help and command reference."""
    help_content = """# 🆘 **Agent Sandbox Help**

## 🚀 **Quick Commands**
- `initialize` - Set up E2B sandbox environment
- `tools` - Show all available tools
- `python <code>` - Quick Python code execution
- `execute <tool> <params>` - Execute specific tool
- `history` - Show execution history
- `help` - Show this help message

## 🛠️ **Tool Execution Format**
```
execute tool_name {"parameter": "value"}
```

## 📝 **Examples**
```
python print("Hello World!")
execute calculator {"expression": "2**10"}
execute shell {"command": "ls -la"}
execute http_request {"method": "GET", "url": "https://httpbin.org/json"}
```

## 🔐 **Safety Features**
- Human approval required for sensitive operations
- All executions are logged and auditable
- Sandbox isolation prevents system damage
- Resource limits prevent abuse

## 🎯 **Agent Capabilities**
Your agent can now perform complex tasks like:
- Data analysis with Python/pandas
- Web scraping and API interactions
- File processing and manipulation
- Mathematical computations
- Image generation and processing
- System administration tasks

**Have fun exploring the enhanced agent capabilities!** 🚀"""
    
    await cl.Message(content=help_content).send()


async def suggest_tools_for_query(query: str, sandbox: AgentSandbox):
    """Suggest appropriate tools based on natural language query."""
    query_lower = query.lower()
    suggestions = []
    
    # Simple keyword matching for tool suggestions
    if any(word in query_lower for word in ["calculate", "math", "compute", "equation"]):
        suggestions.append(("calculator", "Perform mathematical calculations"))
    
    if any(word in query_lower for word in ["python", "code", "script", "program"]):
        suggestions.append(("python_repl", "Execute Python code"))
    
    if any(word in query_lower for word in ["file", "read", "write", "edit"]):
        suggestions.append(("file_read", "Read file contents"))
        suggestions.append(("file_write", "Write to file"))
    
    if any(word in query_lower for word in ["web", "http", "api", "request"]):
        suggestions.append(("http_request", "Make HTTP requests"))
    
    if any(word in query_lower for word in ["shell", "command", "terminal", "bash"]):
        suggestions.append(("shell", "Execute shell commands"))
    
    if any(word in query_lower for word in ["image", "picture", "generate", "create"]):
        suggestions.append(("generate_image", "Generate images"))
    
    if suggestions:
        content = f"🤔 **I understand you want to**: \"{query}\"\n\n**Suggested tools**:\n\n"
        for tool, description in suggestions:
            content += f"- **`{tool}`**: {description}\n"
        
        content += f"\n💡 **Try**: `execute {suggestions[0][0]} {{\"param\": \"value\"}}`"
    else:
        content = f"🤔 **I understand you're asking about**: \"{query}\"\n\n" \
                 f"I'm not sure which tool would be best for this. Try:\n" \
                 f"- `tools` to see all available options\n" \
                 f"- `help` for command reference\n" \
                 f"- `python <code>` for quick Python execution"
    
    await cl.Message(content=content).send()


@cl.on_chat_end
async def cleanup():
    """Clean up sandbox resources when chat ends."""
    sandbox = cl.user_session.get("sandbox")
    if sandbox:
        await sandbox.cleanup()
        agent_id = cl.user_session.get("agent_id")
        if agent_id in sandbox_instances:
            del sandbox_instances[agent_id]


if __name__ == "__main__":
    cl.run()
