# START OF FILE core/ai/workflow_manager.py
"""
HAI-Net Workflow Manager
Manages agent state transitions and high-level, multi-step workflows.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import time

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentState, AgentStateTransitions, AgentRole
from core.ai.llm import LLMMessage

if TYPE_CHECKING:
    from core.ai.agents import AgentManager

class WorkflowManager:
    """
    Orchestrates complex workflows and manages agent state transitions.
    """
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.workflow_manager", settings)
        self.workflows: Dict[str, Any] = {}
        self.agent_manager: Optional['AgentManager'] = None  # Will be set via dependency injection

    def set_agent_manager(self, agent_manager: 'AgentManager') -> None:
        """Inject the agent manager for workflow operations"""
        self.agent_manager = agent_manager

    async def change_agent_state(self, agent: Agent, new_state: AgentState, context: Optional[str] = None) -> bool:
        """
        Changes an agent's state, ensuring the transition is valid.
        Injects guidance message into agent's history.
        """
        if AgentStateTransitions.is_valid_transition(agent.current_state, new_state):
            self.logger.info(f"Transitioning agent {agent.agent_id} from {agent.current_state.value} to {new_state.value}")
            
            # Add state transition guidance message
            from core.ai.prompt_assembler import PromptAssembler
            assembler = PromptAssembler(self.settings)
            transition_msg = assembler.create_state_transition_message(agent, new_state, context)
            agent.message_history.append(transition_msg)
            
            # Manually update agent state (instead of calling protected method)
            if AgentStateTransitions.is_valid_transition(agent.current_state, new_state):
                old_state = agent.current_state
                agent.previous_state = agent.current_state
                agent.current_state = new_state
                
                # Record state change
                state_change: Dict[str, Any] = {
                    "from_state": old_state.value,
                    "to_state": new_state.value,
                    "timestamp": time.time(),
                    "agent_id": agent.agent_id,
                    "constitutional_compliant": True
                }
                
                agent.state_history.append(state_change)
                agent.last_activity = time.time()
                
                # Log state transition
                agent.logger.log_decentralization_event(
                    f"state_transition_{old_state.value}_to_{new_state.value}",
                    local_processing=True
                )
                
                # Notify callbacks
                for callback in agent.state_change_callbacks:
                    try:
                        callback(old_state, new_state)
                    except Exception as e:
                        agent.logger.error(f"State change callback error: {e}")
            
            return True
        else:
            self.logger.error(f"Invalid state transition for agent {agent.agent_id}: "
                              f"from {agent.current_state.value} to {new_state.value}")
            return False

    async def process_plan_creation(self, admin_agent: Agent, plan: Dict[str, Any]):
        """
        Handle the Project Creation workflow when Admin creates a plan.
        
        Steps:
        1. Create a new PM agent
        2. Assign the plan to the PM
        3. Transition PM to STARTUP state
        """
        if not self.agent_manager:
            self.logger.error("Cannot process plan creation: AgentManager not set")
            return
        
        self.logger.info(f"Starting ProjectCreationWorkflow for plan: {plan.get('project_name', 'Unnamed')}")
        
        try:
            # 1. Create PM agent
            pm_agent_id = await self.agent_manager.create_agent(AgentRole.PM)
            if not pm_agent_id:
                self.logger.error("Failed to create PM agent for project")
                return
            
            pm_agent = self.agent_manager.get_agent(pm_agent_id)
            if not pm_agent:
                return
            
            # 2. Provide the plan to the PM agent
            plan_message = LLMMessage(
                role="user",
                content=f"You have been assigned a new project:\n\nProject: {plan.get('project_name', 'Unnamed Project')}\n\nDescription: {plan.get('description', 'No description')}\n\nObjectives:\n" + "\n".join(f"- {obj}" for obj in plan.get('objectives', [])) + f"\n\nDeliverables:\n" + "\n".join(f"- {del_}" for del_ in plan.get('deliverables', [])),
                timestamp=time.time()
            )
            pm_agent.message_history.append(plan_message)
            
            # 3. Transition PM to STARTUP state and schedule
            await self.change_agent_state(pm_agent, AgentState.STARTUP, 
                                         context="Break down this project into actionable tasks")
            await self.agent_manager.schedule_cycle(pm_agent_id)
            
            # 4. Notify Admin that PM was created
            admin_agent.message_history.append(LLMMessage(
                role="system",
                content=f"[SYSTEM] Project Manager agent {pm_agent_id} has been created and assigned your plan. They will break it down into tasks.",
                timestamp=time.time()
            ))
            
            self.logger.info(f"✅ ProjectCreationWorkflow complete: PM {pm_agent_id} created and started")
            
        except Exception as e:
            self.logger.error(f"ProjectCreationWorkflow failed: {e}")

    async def process_task_list_creation(self, pm_agent: Agent, tasks: List[Dict[str, Any]]):
        """
        Handle when PM creates a task list.
        
        Steps:
        1. Store tasks in PM's memory
        2. Transition PM to BUILD_TEAM_TASKS state
        """
        self.logger.info(f"PM {pm_agent.agent_id} created {len(tasks)} tasks")
        
        # Store tasks in PM's memory for later use
        pm_agent.memory.short_term["tasks"] = tasks
        pm_agent.memory.short_term["tasks_timestamp"] = time.time()
        
        # Transition to next state
        await self.change_agent_state(pm_agent, AgentState.BUILD_TEAM_TASKS,
                                     context=f"You have defined {len(tasks)} tasks. Now create worker agents for these tasks.")
        
        # Schedule PM to continue workflow
        await pm_agent.manager.schedule_cycle(pm_agent.agent_id)
