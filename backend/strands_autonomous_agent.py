"""
Fully Autonomous Multi-Step Agent using Strands Framework
Self-evolving agents that can plan, execute, and adapt autonomously
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import sys

# Add strands-tools to path
sys.path.append('/Users/franksimpson/Downloads/strands-tools/src')

try:
    from strands import Agent
    from strands_tools import (
        file_read, file_write, editor, shell, python_repl,
        calculator, http_request, generate_image, memory,
        use_browser, use_llm, environment, current_time,
        think, swarm, workflow, batch, journal, sleep,
        mem0_memory, retrieve, speak, stop, agent_graph
    )
    STRANDS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Strands framework not available: {e}")
    STRANDS_AVAILABLE = False


@dataclass
class AutonomousTask:
    """Represents a complex task for autonomous execution."""
    id: str
    title: str
    description: str
    objective: str
    constraints: List[str]
    success_criteria: List[str]
    max_steps: int = 50
    timeout_minutes: int = 30


class StrandsAutonomousAgent:
    """Fully autonomous agent using Strands framework."""
    
    def __init__(self, agent_id: str, agent_type: str = "autonomous"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.execution_history = []
        self.memory_store = {}
        
        # Initialize Strands Agent with full toolset
        if STRANDS_AVAILABLE:
            self.agent = Agent(
                name=f"AutonomousAgent_{agent_id}",
                tools=[
                    # Core tools
                    file_read, file_write, editor, shell, python_repl,
                    calculator, http_request, current_time, environment,
                    
                    # AI and reasoning tools
                    use_llm, generate_image, think, memory, mem0_memory,
                    
                    # Advanced coordination tools
                    swarm, workflow, batch, agent_graph,
                    
                    # Utility tools
                    journal, sleep, speak, stop,
                    
                    # Web and data tools
                    use_browser, retrieve
                ],
                system_prompt=self._get_system_prompt()
            )
        else:
            self.agent = None
            
    def _get_system_prompt(self) -> str:
        """Get the system prompt for autonomous operation."""
        return f"""You are an autonomous AI agent (ID: {self.agent_id}) with the ability to:

1. **THINK AUTONOMOUSLY**: Use the 'think' tool to reason through complex problems
2. **PLAN MULTI-STEP WORKFLOWS**: Break down complex tasks into executable steps
3. **EXECUTE TOOLS**: Use any available tool to accomplish objectives
4. **ADAPT AND LEARN**: Modify your approach based on results
5. **COORDINATE WITH OTHER AGENTS**: Use swarm intelligence when needed
6. **MAINTAIN MEMORY**: Store and retrieve information across sessions

**OPERATING PRINCIPLES**:
- Always start with the 'think' tool to analyze the task
- Create detailed execution plans using 'workflow' tool
- Use 'batch' tool for parallel operations when possible
- Store important findings in 'memory' or 'journal'
- Use 'swarm' tool for complex problems requiring multiple perspectives
- Continuously evaluate progress and adapt strategy
- Be proactive and creative in problem-solving

**AVAILABLE TOOLS**: You have access to 20+ powerful tools including:
- File operations (read, write, edit)
- Shell commands and Python execution
- Web browsing and HTTP requests
- Image generation and processing
- Mathematical calculations
- Memory and journaling
- Multi-agent coordination
- Workflow automation

**AUTONOMY LEVEL**: MAXIMUM - You should work independently to achieve objectives without constant human intervention. Make decisions, execute actions, and adapt as needed.

Remember: You are designed to be self-sufficient and proactive. Take initiative!"""

    async def execute_autonomous_task(self, task: AutonomousTask) -> Dict[str, Any]:
        """Execute a complex autonomous task."""
        
        if not STRANDS_AVAILABLE:
            return {"error": "Strands framework not available", "status": "failed"}
        
        print(f"🚀 Starting autonomous task: {task.title}")
        
        # Start with thinking and planning
        planning_result = await self._autonomous_planning(task)
        
        if not planning_result.get("success"):
            return {"error": "Planning failed", "status": "failed"}
        
        # Execute the planned workflow
        execution_result = await self._autonomous_execution(task, planning_result["plan"])
        
        # Evaluate and report results
        final_result = await self._autonomous_evaluation(task, execution_result)
        
        return final_result
    
    async def _autonomous_planning(self, task: AutonomousTask) -> Dict[str, Any]:
        """Autonomous planning phase using think and workflow tools."""
        
        try:
            # Use think tool for deep analysis
            thinking_result = self.agent.tool.think(
                thought=f"""
                TASK ANALYSIS:
                Title: {task.title}
                Description: {task.description}
                Objective: {task.objective}
                Constraints: {task.constraints}
                Success Criteria: {task.success_criteria}
                
                I need to create a comprehensive execution plan that:
                1. Breaks down the objective into actionable steps
                2. Identifies required tools and resources
                3. Considers constraints and limitations
                4. Defines success metrics
                5. Includes contingency plans
                
                Let me think through this systematically...
                """,
                cycle_count=3
            )
            
            # Create workflow based on thinking results
            workflow_steps = self._generate_workflow_steps(task, thinking_result)
            
            workflow_result = self.agent.tool.workflow(
                action="create",
                name=f"autonomous_task_{task.id}",
                steps=workflow_steps
            )
            
            # Journal the planning process
            self.agent.tool.journal(
                action="write",
                content=f"""
                AUTONOMOUS PLANNING COMPLETE
                Task: {task.title}
                Timestamp: {datetime.now().isoformat()}
                
                Thinking Process:
                {thinking_result}
                
                Generated Workflow:
                {json.dumps(workflow_steps, indent=2)}
                
                Status: Ready for execution
                """
            )
            
            return {
                "success": True,
                "plan": workflow_steps,
                "thinking": thinking_result,
                "workflow_id": workflow_result.get("workflow_id")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_workflow_steps(self, task: AutonomousTask, thinking_result: Any) -> List[Dict[str, Any]]:
        """Generate workflow steps based on task analysis."""
        
        # Base workflow template that adapts to different task types
        steps = [
            {
                "name": "initialize",
                "tool": "current_time",
                "arguments": {"timezone": "UTC"},
                "description": "Initialize task execution"
            },
            {
                "name": "gather_information",
                "tool": "batch",
                "arguments": {
                    "invocations": [
                        {"name": "environment", "arguments": {"action": "list"}},
                        {"name": "memory", "arguments": {"action": "retrieve", "query": task.objective}}
                    ]
                },
                "description": "Gather relevant information and context"
            }
        ]
        
        # Add task-specific steps based on objective
        if "research" in task.objective.lower() or "analyze" in task.objective.lower():
            steps.extend([
                {
                    "name": "web_research",
                    "tool": "http_request",
                    "arguments": {"method": "GET", "url": "https://api.example.com/search"},
                    "description": "Conduct web research"
                },
                {
                    "name": "data_analysis",
                    "tool": "python_repl",
                    "arguments": {"code": "# Data analysis code will be generated dynamically"},
                    "description": "Analyze gathered data"
                }
            ])
        
        if "write" in task.objective.lower() or "report" in task.objective.lower():
            steps.extend([
                {
                    "name": "content_creation",
                    "tool": "use_llm",
                    "arguments": {
                        "prompt": f"Create content for: {task.objective}",
                        "system_prompt": "You are an expert content creator"
                    },
                    "description": "Generate content"
                },
                {
                    "name": "save_content",
                    "tool": "file_write",
                    "arguments": {"path": f"output_{task.id}.md", "content": "{{generated_content}}"},
                    "description": "Save generated content"
                }
            ])
        
        if "image" in task.objective.lower() or "visual" in task.objective.lower():
            steps.append({
                "name": "generate_visual",
                "tool": "generate_image",
                "arguments": {"prompt": task.description},
                "description": "Generate visual content"
            })
        
        # Add coordination step for complex tasks
        if task.max_steps > 20 or "complex" in task.description.lower():
            steps.append({
                "name": "swarm_coordination",
                "tool": "swarm",
                "arguments": {
                    "task": task.objective,
                    "swarm_size": 3,
                    "coordination_pattern": "collaborative"
                },
                "description": "Use swarm intelligence for complex problem solving"
            })
        
        # Always end with evaluation and reporting
        steps.extend([
            {
                "name": "evaluate_results",
                "tool": "think",
                "arguments": {
                    "thought": f"Evaluate if we achieved: {task.success_criteria}",
                    "cycle_count": 2
                },
                "description": "Evaluate task completion"
            },
            {
                "name": "final_report",
                "tool": "journal",
                "arguments": {
                    "action": "write",
                    "content": f"Task {task.id} completion report"
                },
                "description": "Generate final report"
            }
        ])
        
        return steps
    
    async def _autonomous_execution(self, task: AutonomousTask, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the planned workflow autonomously."""
        
        execution_results = []
        context = {}  # Shared context between steps
        
        try:
            for i, step in enumerate(workflow_steps):
                print(f"🔄 Executing step {i+1}/{len(workflow_steps)}: {step['name']}")
                
                # Execute workflow step
                step_result = self.agent.tool.workflow(
                    action="execute_step",
                    workflow_id=f"autonomous_task_{task.id}",
                    step_name=step["name"]
                )
                
                # Store result and update context
                execution_results.append({
                    "step": step["name"],
                    "result": step_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update shared context for next steps
                context[step["name"]] = step_result
                
                # Adaptive decision making - modify next steps based on results
                if step_result.get("status") == "failed":
                    # Use think tool to adapt strategy
                    adaptation = self.agent.tool.think(
                        thought=f"Step {step['name']} failed. How should I adapt the remaining workflow?",
                        cycle_count=1
                    )
                    
                    # Could modify remaining steps based on adaptation
                    print(f"⚠️ Adapting strategy: {adaptation}")
                
                # Brief pause between steps
                await asyncio.sleep(1)
            
            return {
                "success": True,
                "results": execution_results,
                "context": context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "partial_results": execution_results
            }
    
    async def _autonomous_evaluation(self, task: AutonomousTask, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate task completion and generate final report."""
        
        try:
            # Use think tool for comprehensive evaluation
            evaluation = self.agent.tool.think(
                thought=f"""
                TASK EVALUATION:
                
                Original Objective: {task.objective}
                Success Criteria: {task.success_criteria}
                
                Execution Results: {json.dumps(execution_result, indent=2)}
                
                Questions to evaluate:
                1. Did we achieve the stated objective?
                2. Were all success criteria met?
                3. What worked well in the execution?
                4. What could be improved?
                5. What insights were gained?
                6. Should any follow-up actions be taken?
                
                Provide a comprehensive evaluation...
                """,
                cycle_count=2
            )
            
            # Generate final report
            final_report = self.agent.tool.journal(
                action="write",
                content=f"""
                AUTONOMOUS TASK COMPLETION REPORT
                ================================
                
                Task ID: {task.id}
                Title: {task.title}
                Completed: {datetime.now().isoformat()}
                Agent: {self.agent_id}
                
                OBJECTIVE:
                {task.objective}
                
                SUCCESS CRITERIA:
                {chr(10).join(f"- {criterion}" for criterion in task.success_criteria)}
                
                EXECUTION SUMMARY:
                - Total Steps: {len(execution_result.get('results', []))}
                - Success Rate: {self._calculate_success_rate(execution_result)}%
                - Duration: {self._calculate_duration(execution_result)}
                
                EVALUATION:
                {evaluation}
                
                DETAILED RESULTS:
                {json.dumps(execution_result, indent=2)}
                
                RECOMMENDATIONS:
                - Store successful patterns in memory
                - Update agent capabilities based on learnings
                - Consider automation of similar future tasks
                """
            )
            
            # Store learnings in memory
            self.agent.tool.memory(
                action="store",
                content=f"Task completion pattern for {task.title}: {evaluation}",
                metadata={"task_type": task.title, "success": execution_result.get("success")}
            )
            
            return {
                "task_id": task.id,
                "status": "completed" if execution_result.get("success") else "failed",
                "evaluation": evaluation,
                "report": final_report,
                "execution_summary": execution_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "task_id": task.id,
                "status": "evaluation_failed",
                "error": str(e),
                "execution_summary": execution_result
            }
    
    def _calculate_success_rate(self, execution_result: Dict[str, Any]) -> float:
        """Calculate success rate of execution steps."""
        results = execution_result.get("results", [])
        if not results:
            return 0.0
        
        successful_steps = sum(1 for result in results if result.get("result", {}).get("status") != "failed")
        return (successful_steps / len(results)) * 100
    
    def _calculate_duration(self, execution_result: Dict[str, Any]) -> str:
        """Calculate execution duration."""
        results = execution_result.get("results", [])
        if len(results) < 2:
            return "< 1 minute"
        
        start_time = datetime.fromisoformat(results[0]["timestamp"])
        end_time = datetime.fromisoformat(results[-1]["timestamp"])
        duration = end_time - start_time
        
        return str(duration)
    
    async def handle_autonomous_request(self, user_request: str) -> Dict[str, Any]:
        """Handle a user request autonomously by creating and executing a task."""
        
        # Use think tool to analyze the request and create a task
        analysis = self.agent.tool.think(
            thought=f"""
            USER REQUEST: {user_request}
            
            I need to analyze this request and create an autonomous task:
            1. What is the user really asking for?
            2. What would be the objective?
            3. What are the success criteria?
            4. What constraints should I consider?
            5. How complex is this task?
            
            Based on this analysis, I'll create a structured task...
            """,
            cycle_count=2
        )
        
        # Create autonomous task based on analysis
        task = AutonomousTask(
            id=f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=self._extract_title_from_request(user_request),
            description=user_request,
            objective=self._extract_objective_from_analysis(analysis),
            constraints=["Complete within reasonable time", "Use available tools only"],
            success_criteria=self._extract_success_criteria_from_analysis(analysis),
            max_steps=30,
            timeout_minutes=15
        )
        
        # Execute the task autonomously
        result = await self.execute_autonomous_task(task)
        
        return result
    
    def _extract_title_from_request(self, request: str) -> str:
        """Extract a concise title from user request."""
        words = request.split()[:6]  # First 6 words
        return " ".join(words) + ("..." if len(request.split()) > 6 else "")
    
    def _extract_objective_from_analysis(self, analysis: Any) -> str:
        """Extract objective from think tool analysis."""
        # In a real implementation, this would parse the analysis
        # For now, return a generic objective
        return "Complete the user's request autonomously using available tools"
    
    def _extract_success_criteria_from_analysis(self, analysis: Any) -> List[str]:
        """Extract success criteria from analysis."""
        return [
            "User request is fully addressed",
            "All required information is gathered",
            "Results are properly formatted and saved",
            "Process is documented for future reference"
        ]


# Factory function to create autonomous agents
def create_autonomous_agent(agent_id: str, agent_type: str = "autonomous") -> StrandsAutonomousAgent:
    """Create a new autonomous agent using Strands framework."""
    return StrandsAutonomousAgent(agent_id, agent_type)


# Example usage
async def demo_autonomous_agent():
    """Demonstrate autonomous agent capabilities."""
    
    if not STRANDS_AVAILABLE:
        print("❌ Strands framework not available for demo")
        return
    
    # Create autonomous agent
    agent = create_autonomous_agent("demo_001", "research_agent")
    
    # Example autonomous task
    task = AutonomousTask(
        id="demo_task_001",
        title="Bitcoin and Peanut Butter Price Analysis",
        description="Research and analyze the correlation between Bitcoin prices and peanut butter prices, then write a comprehensive report",
        objective="Create a detailed analysis report comparing Bitcoin and peanut butter price trends with data visualization and insights",
        constraints=[
            "Use publicly available data only",
            "Complete analysis within 30 minutes",
            "Generate visual charts if possible"
        ],
        success_criteria=[
            "Data is collected for both Bitcoin and peanut butter prices",
            "Statistical analysis is performed",
            "Correlation analysis is completed",
            "Report is written and saved to file",
            "Visualizations are created if possible"
        ],
        max_steps=25,
        timeout_minutes=30
    )
    
    # Execute autonomously
    print("🚀 Starting autonomous task execution...")
    result = await agent.execute_autonomous_task(task)
    
    print("✅ Autonomous execution completed!")
    print(f"Status: {result.get('status')}")
    print(f"Report: {result.get('report', 'No report generated')}")
    
    return result


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_autonomous_agent())
