# START OF FILE core/ai/prompt_assembler.py
"""
HAI-Net Prompt Assembler
Assembles state-specific system prompts for agents based on the TrippleEffect framework.
"""

import time
import json
from pathlib import Path
from typing import List, Optional
from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.llm import LLMMessage
from core.ai.agents import Agent, AgentRole, AgentState


class PromptAssembler:
    """
    Assembles context-aware prompts for agents based on their role and state.
    Loads prompts from centralized config/prompts.json file.
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.prompt_assembler", settings)
        
        # System prompts for each agent role and state
        self._load_prompts_from_file()
    
    def _load_prompts_from_file(self):
        """Load all system prompts from config/prompts.json"""
        
        try:
            # Find the prompts file
            prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.json"
            
            if not prompts_path.exists():
                self.logger.warning(f"Prompts file not found at {prompts_path}, using defaults", category="init", function="_load_prompts_from_file")
                self._initialize_default_prompts()
                return
            
            # Load prompts from JSON
            with open(prompts_path, 'r') as f:
                prompts_data = json.load(f)
            
            # Map JSON prompts to agent states
            self.admin_prompts = {
                AgentState.CONVERSATION: prompts_data["admin_prompts"]["conversation"],
                AgentState.PLANNING: prompts_data["admin_prompts"]["planning"]
            }
            
            self.pm_prompts = {
                AgentState.STARTUP: prompts_data["pm_prompts"]["startup"],
                AgentState.BUILD_TEAM_TASKS: prompts_data["pm_prompts"]["build_team_tasks"],
                AgentState.ACTIVATE_WORKERS: prompts_data["pm_prompts"]["activate_workers"],
                AgentState.MANAGE: prompts_data["pm_prompts"]["manage"],
                AgentState.STANDBY: prompts_data["pm_prompts"]["standby"]
            }
            
            self.worker_prompts = {
                AgentState.WORK: prompts_data["worker_prompts"]["work"],
                AgentState.WAIT: prompts_data["worker_prompts"]["wait"]
            }
            
            self.guardian_prompts = {
                AgentState.IDLE: prompts_data["guardian_prompts"]["idle"]
            }
            
            self.state_guidance = prompts_data["state_guidance"]
            self.tools_description = prompts_data["tools_description"]
            
            self.logger.info_init("Successfully loaded prompts from config/prompts.json", function="_load_prompts_from_file")
            
        except Exception as e:
            self.logger.error(f"Error loading prompts from file: {e}", category="init", function="_load_prompts_from_file")
            self._initialize_default_prompts()
    
    def _initialize_default_prompts(self):
        """Fallback default prompts if file loading fails"""
        self.logger.debug_init("Initializing fallback default prompts", function="_initialize_default_prompts")
        
        # Minimal default prompts
        self.admin_prompts = {
            AgentState.CONVERSATION: """You are the Admin AI, the primary AI assistant linked to the human user.

Your role is to:
- Engage in natural conversation with the user
- Monitor ongoing projects and their progress
- Identify when the user has a new high-level task or project request
- When you receive a significant project request, transition to PLANNING state to create a detailed plan

Available tools:
- send_message: Send messages to other agents (PMs, Workers)

When the user requests a project, respond acknowledging it and transition to planning state.
You can communicate in a friendly, helpful manner while maintaining constitutional compliance.""",

            AgentState.PLANNING: """You are the Admin AI in PLANNING mode.

Your ONLY task right now is to create a detailed, structured plan for the user's request.

The plan should:
1. Break down the user's request into clear objectives
2. Identify major milestones
3. List specific deliverables
4. Be detailed enough for a Project Manager to execute

Output your plan in this format:
<plan>
<project_name>Clear project name</project_name>
<description>Brief description</description>
<objectives>
- Objective 1
- Objective 2
</objectives>
<deliverables>
- Deliverable 1
- Deliverable 2
</deliverables>
</plan>

Once you output the plan, you will automatically transition back to CONVERSATION mode."""
        }
        
        # PM Agent Prompts
        self.pm_prompts = {
            AgentState.STARTUP: """You are a Project Manager AI in STARTUP mode.

You have been assigned a new project. Your current task is to:
1. Review the project plan you received
2. Break it down into specific, actionable tasks
3. Determine what worker agents are needed

Output your task breakdown in this format:
<task_list>
<task>
<name>Task name</name>
<description>Detailed description</description>
<required_skills>Skills needed</required_skills>
</task>
<!-- More tasks -->
</task_list>

After outputting the task list, you will transition to BUILD_TEAM_TASKS state.""",

            AgentState.BUILD_TEAM_TASKS: """You are a Project Manager AI in BUILD_TEAM_TASKS mode.

You have defined the tasks. Now create the worker agents needed for this project.

Use the send_message tool to request worker agent creation from the system.
Create one worker at a time, specifying their role and initial task.

Example:
<tool_requests>
<calls>
<tool_call>
<name>send_message</name>
<args>
<target_agent_id>admin_001</target_agent_id>
<message>Request worker agent for: [task description]</message>
</args>
</tool_call>
</calls>
</tool_requests>

After creating all needed workers, transition to ACTIVATE_WORKERS state.""",

            AgentState.ACTIVATE_WORKERS: """You are a Project Manager AI in ACTIVATE_WORKERS mode.

Your worker agents are ready. Now assign specific tasks to each worker.

Use send_message to delegate tasks:
<tool_requests>
<calls>
<tool_call>
<name>send_message</name>
<args>
<target_agent_id>worker_agent_id</target_agent_id>
<message>Your task: [detailed task description]</message>
</args>
</tool_call>
</calls>
</tool_requests>

After all tasks are assigned, transition to MANAGE state.""",

            AgentState.MANAGE: """You are a Project Manager AI in MANAGE mode.

Monitor your workers' progress and coordinate the project:
1. Check on worker status
2. Review completed work
3. Provide guidance when needed
4. Report progress to the Admin AI

Use send_message to communicate with workers and the Admin.

When the project is complete, transition to STANDBY state.""",

            AgentState.STANDBY: """You are a Project Manager AI in STANDBY mode.

Your project is complete. Wait for new instructions or project assignments."""
        }
        
        # Worker Agent Prompts
        self.worker_prompts = {
            AgentState.WORK: """You are a Worker AI executing a specific task.

Your assignment has been provided in your message history.

Execute the task to the best of your ability:
1. Understand the requirements
2. Perform the necessary work
3. Report your results

You can use available tools if needed.

When your task is complete, transition to WAIT state and report your completion.""",

            AgentState.WAIT: """You are a Worker AI in WAIT mode.

You have completed your current task. Wait for:
- Review and feedback from your PM
- A new task assignment
- Further instructions

Remain ready to receive new work."""
        }
        
        # Guardian Agent Prompts
        self.guardian_prompts = {
            AgentState.IDLE: """You are the Constitutional Guardian AI.

Monitor all agent activities for constitutional compliance:
- Privacy First: No personal data leaves without consent
- Human Rights: Protect and promote fundamental rights
- Decentralization: No central control points
- Community Focus: Strengthen real-world connections

Review agent outputs and flag any violations."""
        }
    
    def prepare_llm_call_data(self, agent: Agent) -> List[LLMMessage]:
        """
        Prepare the complete message list for an LLM call, including system prompts.
        
        Args:
            agent: The agent to prepare data for
            
        Returns:
            Complete list of messages ready for LLM
        """
        messages: List[LLMMessage] = []
        
        # 1. Add system prompt based on agent role and state
        system_prompt = self._get_system_prompt(agent)
        if system_prompt:
            messages.append(LLMMessage(
                role="system",
                content=system_prompt,
                timestamp=time.time()
            ))
        
        # 2. Add agent's message history
        messages.extend(agent.message_history)
        
        # 3. Add any dynamic context
        dynamic_context = self._get_dynamic_context(agent)
        if dynamic_context:
            messages.append(LLMMessage(
                role="system",
                content=dynamic_context,
                timestamp=time.time()
            ))
        
        return messages
    
    def _get_system_prompt(self, agent: Agent) -> str:
        """Get the system prompt for an agent based on role and state"""
        
        prompt = ""
        
        if agent.role == AgentRole.ADMIN:
            # If Admin is in IDLE state, use CONVERSATION prompt
            if agent.current_state == AgentState.IDLE:
                prompt = self.admin_prompts.get(AgentState.CONVERSATION, "")
            else:
                prompt = self.admin_prompts.get(agent.current_state, "")
        elif agent.role == AgentRole.PM:
            prompt = self.pm_prompts.get(agent.current_state, "")
        elif agent.role == AgentRole.WORKER:
            # If Worker is in IDLE state, use WORK prompt
            if agent.current_state == AgentState.IDLE:
                prompt = self.worker_prompts.get(AgentState.WORK, "")
            else:
                prompt = self.worker_prompts.get(agent.current_state, "")
        elif agent.role == AgentRole.GUARDIAN:
            prompt = self.guardian_prompts.get(agent.current_state, "")
        
        # Debug logging
        self.logger.debug_agent(f"[{agent.agent_id}] Getting system prompt: role={agent.role.value}, state={agent.current_state.value}, prompt_length={len(prompt)}", function="_get_system_prompt")
        
        return prompt
    
    def _get_dynamic_context(self, agent: Agent) -> str:
        """Get dynamic context to inject into the prompt"""
        
        context_parts: List[str] = []
        
        # Add current time for Admin agents
        if agent.role == AgentRole.ADMIN:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            context_parts.append(f"Current time: {current_time}")
        
        # Add available tools context
        if agent.manager and agent.manager.cycle_handler:
            tools_list = self._get_available_tools_description()
            if tools_list:
                context_parts.append(f"Available tools:\n{tools_list}")
        
        if context_parts:
            return "\n\n".join(context_parts)
        
        return ""
    
    def _get_available_tools_description(self) -> str:
        """Get a description of available tools"""
        # This would ideally query the ToolExecutor
        # For now, return a basic description
        return """- send_message: Send a message to another agent
  Usage: <tool_requests><calls><tool_call><name>send_message</name><args><target_agent_id>AGENT_ID</target_agent_id><message>Your message</message></args></tool_call></calls></tool_requests>"""
    
    def create_state_transition_message(self, agent: Agent, new_state: AgentState, context: Optional[str] = None) -> LLMMessage:
        """
        Create a system message to inform an agent about a state transition.
        
        Args:
            agent: The agent transitioning
            new_state: The new state
            context: Optional additional context
            
        Returns:
            System message for the agent's history
        """
        
        state_guidance = {
            AgentState.PLANNING: "You are now in PLANNING mode. Create a detailed plan for the user's request.",
            AgentState.CONVERSATION: "You are now in CONVERSATION mode. Continue engaging with the user.",
            AgentState.STARTUP: "You are now starting up a new project. Break down the plan into tasks.",
            AgentState.BUILD_TEAM_TASKS: "Build your team by creating worker agents for the tasks.",
            AgentState.ACTIVATE_WORKERS: "Assign tasks to your worker agents.",
            AgentState.MANAGE: "Monitor and coordinate your team's progress.",
            AgentState.WORK: "Execute your assigned task.",
            AgentState.WAIT: "Task complete. Wait for further instructions.",
            AgentState.STANDBY: "Project complete. Standing by for new assignments.",
        }
        
        message_content = f"[SYSTEM] State transition to: {new_state.value}"
        
        if new_state in state_guidance:
            message_content += f"\n{state_guidance[new_state]}"
        
        if context:
            message_content += f"\nContext: {context}"
        
        return LLMMessage(
            role="system",
            content=message_content,
            timestamp=time.time()
        )
