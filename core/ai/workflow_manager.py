# START OF FILE core/ai/workflow_manager.py
"""
HAI-Net Workflow Manager
Manages agent state transitions and high-level, multi-step workflows.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import time

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentState, AgentRole
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
        Changes an agent's state by calling the agent's own transition method.
        Injects a guidance message into the agent's history beforehand.
        """
        try:
            self.logger.debug_agent(f"[{agent.agent_id}] State transition requested: {agent.current_state.value} -> {new_state.value}", function="change_agent_state")

            # Add state transition guidance message to provide context to the agent for its next action
            from core.ai.prompt_assembler import PromptAssembler
            assembler = PromptAssembler(self.settings)
            transition_msg = assembler.create_state_transition_message(agent, new_state, context)
            agent.message_history.append(transition_msg)

            # Call the agent's public state transition method
            await agent.transition_state(new_state)
            
            self.logger.info(f"[{agent.agent_id}] State transition complete: {new_state.value}", category="agent", function="change_agent_state")
            return True
        except Exception as e:
            self.logger.error(f"[{agent.agent_id}] State transition failed ({agent.current_state.value} -> {new_state.value}): {e}", category="agent", function="change_agent_state")
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
            self.logger.error("Cannot process plan creation: AgentManager not set", category="agent", function="process_plan_creation")
            return
        
        self.logger.info(f"[{admin_agent.agent_id}] Starting ProjectCreationWorkflow for plan: {plan.get('project_name', 'Unnamed')}", category="agent", function="process_plan_creation")
        
        try:
            # 1. Create PM agent
            pm_agent_id = await self.agent_manager.create_agent(AgentRole.PM)
            if not pm_agent_id:
                self.logger.error(f"[{admin_agent.agent_id}] Failed to create PM agent for project", category="agent", function="process_plan_creation")
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
            
            self.logger.info(f"[{admin_agent.agent_id}] ✅ ProjectCreationWorkflow complete: PM {pm_agent_id} created and started", category="agent", function="process_plan_creation")
            
        except Exception as e:
            self.logger.error(f"[{admin_agent.agent_id}] ProjectCreationWorkflow failed: {e}", category="agent", function="process_plan_creation")

    async def process_task_list_creation(self, pm_agent: Agent, tasks: List[Dict[str, Any]]):
        """
        Handle when PM creates a task list.
        
        Steps:
        1. Store tasks in PM's memory
        2. Transition PM to BUILD_TEAM_TASKS state
        """
        self.logger.debug_agent(f"[{pm_agent.agent_id}] Processing task list creation: {len(tasks)} tasks", function="process_task_list_creation")
        
        # Store tasks in PM's memory for later use
        pm_agent.memory.short_term["tasks"] = tasks
        pm_agent.memory.short_term["tasks_timestamp"] = time.time()
        
        # Transition to next state
        await self.change_agent_state(pm_agent, AgentState.BUILD_TEAM_TASKS,
                                     context=f"You have defined {len(tasks)} tasks. Now create worker agents for these tasks.")
        
        # Schedule PM to continue workflow
        await pm_agent.manager.schedule_cycle(pm_agent.agent_id)

    async def process_worker_creation(self, pm_agent: Agent, request: Dict[str, Any]):
        """
        Handle when PM requests to create a worker agent.

        Steps:
        1. Create a new WORKER agent.
        2. Map the worker to the task_id in the PM's memory.
        3. Notify the PM agent.
        4. Check if all workers are created, if so transition to ACTIVATE_WORKERS.
        5. Otherwise, reschedule the PM to create the next worker.
        """
        if not self.agent_manager:
            self.logger.error("Cannot process worker creation: AgentManager not set", category="agent", function="process_worker_creation")
            return

        task_id = request.get("task_id")
        specialty = request.get("specialty", "general")
        
        if not task_id:
            self.logger.error(f"[{pm_agent.agent_id}] Worker creation requested without task_id", category="agent", function="process_worker_creation")
            return

        self.logger.debug_agent(f"[{pm_agent.agent_id}] Creating worker for task_id={task_id}, specialty={specialty}", function="process_worker_creation")

        try:
            # 1. Create Worker agent
            worker_agent_id = await self.agent_manager.create_agent(AgentRole.WORKER)
            if not worker_agent_id:
                self.logger.error(f"[{pm_agent.agent_id}] Failed to create worker agent for task {task_id}", category="agent", function="process_worker_creation")
                return

            # 2. Map worker to task in PM's memory
            if "worker_map" not in pm_agent.memory.short_term:
                pm_agent.memory.short_term["worker_map"] = {}
            pm_agent.memory.short_term["worker_map"][task_id] = worker_agent_id
            
            # Track how many workers have been created
            if "workers_created_count" not in pm_agent.memory.short_term:
                pm_agent.memory.short_term["workers_created_count"] = 0
            pm_agent.memory.short_term["workers_created_count"] += 1

            # 3. Notify PM
            workers_count = pm_agent.memory.short_term["workers_created_count"]
            total_tasks = len(pm_agent.memory.short_term.get("tasks", []))
            
            system_message = LLMMessage(
                role="system",
                content=f"[SYSTEM] ✅ Worker agent {worker_agent_id} has been created for task {task_id} (Specialty: {specialty}).\n\nWorkers created: {workers_count}/{total_tasks}",
                timestamp=time.time()
            )
            pm_agent.message_history.append(system_message)

            self.logger.info(f"[{pm_agent.agent_id}] ✅ Worker {worker_agent_id} created for task {task_id} ({workers_count}/{total_tasks})", category="agent", function="process_worker_creation")

            # 4. Check if all workers are created
            if workers_count >= total_tasks:
                # All workers created, transition to ACTIVATE_WORKERS
                self.logger.info(f"[{pm_agent.agent_id}] All {workers_count} workers created. Transitioning to ACTIVATE_WORKERS", category="agent", function="process_worker_creation")
                await self.change_agent_state(pm_agent, AgentState.ACTIVATE_WORKERS,
                                             context=f"All {workers_count} workers have been created. Now assign tasks to each worker.")
                await pm_agent.manager.schedule_cycle(pm_agent.agent_id)
            else:
                # More workers needed, reschedule PM to create next worker
                remaining = total_tasks - workers_count
                pm_agent.message_history.append(LLMMessage(
                    role="system",
                    content=f"[SYSTEM] You still need to create {remaining} more worker(s). Please create the next worker now.",
                    timestamp=time.time()
                ))
                await pm_agent.manager.schedule_cycle(pm_agent.agent_id)

        except Exception as e:
            self.logger.error(f"[{pm_agent.agent_id}] Worker creation workflow failed: {e}", category="agent", function="process_worker_creation")
