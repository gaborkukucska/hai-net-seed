# START OF FILE core/ai/cycle_handler.py
"""
HAI-Net Agent Cycle Handler
Drives the agent execution loop by processing events from agents, as described
in the TrippleEffect framework.
"""

import time

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentState
from core.ai.llm import LLMMessage
from core.ai.interaction_handler import InteractionHandler
from core.ai.workflow_manager import WorkflowManager
from core.ai.guardian import ConstitutionalGuardian
from core.ai.prompt_assembler import PromptAssembler

class AgentCycleHandler:
    """
    Manages a single execution cycle of an agent. It orchestrates the process
    of getting events from an agent, handling them, and determining the agent's
    next state.
    """
    def __init__(self, settings: HAINetSettings,
                 interaction_handler: InteractionHandler,
                 workflow_manager: WorkflowManager,
                 guardian: ConstitutionalGuardian):
        self.settings = settings
        self.logger = get_logger("ai.cycle_handler", settings)
        self.interaction_handler = interaction_handler
        self.workflow_manager = workflow_manager
        self.guardian = guardian
        self.prompt_assembler = PromptAssembler(settings)

    async def run_cycle(self, agent: Agent):
        """
        Runs a full processing cycle for a given agent, based on the TrippleEffect architecture.
        """
        if agent.current_state == AgentState.PROCESSING:
            self.logger.warning(f"Agent {agent.agent_id} is already processing. Aborting new cycle.", category="agent", function="run_cycle")
            return

        try:
            # 1. Prepare LLM call data BEFORE transitioning to PROCESSING
            # This ensures the system prompt matches the agent's actual state
            self.logger.debug_agent(f"Starting cycle for agent {agent.agent_id} (role={agent.role.value}, state={agent.current_state.value})", function="run_cycle")
            messages_for_llm = self.prompt_assembler.prepare_llm_call_data(agent)

            # 2. Set agent state to PROCESSING
            await self.workflow_manager.change_agent_state(agent, AgentState.PROCESSING)

            # 3. Process events from the agent's generator
            start_time = time.time()
            reschedule = False

            async for event in agent.process_message(messages_for_llm):
                event_type = event.get("type")

                if event_type == "agent_thought":
                    self.logger.debug_agent(f"[{agent.agent_id}] Thought: {event.get('content')}", function="run_cycle")
                    # In a real system, this would be logged to a DB for observability.

                elif event_type == "tool_requests":
                    tool_calls = event.get("calls", [])
                    self.logger.debug_agent(f"[{agent.agent_id}] Requesting {len(tool_calls)} tool(s): {[tc.get('name') for tc in tool_calls]}", function="run_cycle")

                    for tool_call in tool_calls:
                        result = await self.interaction_handler.execute_tool_call(agent, tool_call)
                        # Format result and append to history for the agent to process
                        tool_result_message = LLMMessage(
                            role="tool",
                            content=str(result),  # Ensure content is string
                            timestamp=time.time()
                        )
                        agent.message_history.append(tool_result_message)

                    # The agent needs to process the tool results, so we schedule another cycle.
                    reschedule = True
                    break

                elif event_type == "agent_state_change_requested":
                    new_state_str = event.get("new_state")
                    if new_state_str:
                        new_state = AgentState(new_state_str)
                        await self.workflow_manager.change_agent_state(agent, new_state)
                        self.logger.info(f"[{agent.agent_id}] State change requested: {agent.current_state.value} -> {new_state.value}", category="agent", function="run_cycle")
                    break

                elif event_type == "plan_created":
                    # Admin created a plan - trigger workflow
                    plan = event.get("plan", {})
                    self.logger.info(f"[{agent.agent_id}] Plan created: {plan.get('project_name', 'Unnamed')}", category="agent", function="run_cycle")
                    
                    # Store plan in agent's memory for workflow manager
                    agent.message_history.append(LLMMessage(
                        role="assistant",
                        content=f"Plan created: {plan}",
                        timestamp=time.time()
                    ))
                    
                    # Trigger workflow processing
                    await self.workflow_manager.process_plan_creation(agent, plan)
                    break
                
                elif event_type == "task_list_created":
                    # PM created task list
                    tasks = event.get("tasks", [])
                    self.logger.info(f"[{agent.agent_id}] Task list created: {len(tasks)} tasks defined", category="agent", function="run_cycle")
                    
                    agent.message_history.append(LLMMessage(
                        role="assistant",
                        content=f"Task list created: {len(tasks)} tasks defined",
                        timestamp=time.time()
                    ))
                    
                    # Store the state before workflow processing
                    state_before_workflow = agent.current_state
                    
                    # Trigger task list workflow
                    await self.workflow_manager.process_task_list_creation(agent, tasks)
                    
                    # If workflow changed the state, don't transition to IDLE at the end
                    if agent.current_state != state_before_workflow:
                        return  # Exit early, workflow has taken control
                    break

                elif event_type == "create_worker_requested":
                    # PM requested to create a worker
                    request = event.get("request", {})
                    self.logger.debug_agent(f"[{agent.agent_id}] Worker creation requested for task_id={request.get('task_id')}, specialty={request.get('specialty')}", function="run_cycle")
                    
                    await self.workflow_manager.process_worker_creation(agent, request)
                    
                    # Workflow manager handles state transitions and rescheduling
                    # Exit early to let workflow control the agent state
                    return

                elif event_type == "final_response":
                    content = event.get("content", "")

                    # In a real system, the guardian would be more deeply integrated.
                    # For now, we log and proceed.
                    # self.guardian.check(content)
                    self.logger.debug_agent(f"[{agent.agent_id}] Final response generated (length={len(content)} chars)", function="run_cycle")

                    agent.message_history.append(LLMMessage(role="assistant", content=content, timestamp=time.time()))
                    
                    # Check for automatic state transitions based on agent state
                    await self._check_auto_transitions(agent)
                    break

                elif event_type == "error":
                    self.logger.error(f"[{agent.agent_id}] Agent reported error: {event.get('content')}", category="agent", function="run_cycle")
                    await self.workflow_manager.change_agent_state(agent, AgentState.ERROR)
                    break

            execution_time = time.time() - start_time
            agent.metrics.average_response_time = execution_time if agent.metrics.average_response_time == 0 else (0.1 * execution_time + 0.9 * agent.metrics.average_response_time)

            # 5. Determine next step and set final state
            if reschedule:
                # If a tool was called, the agent needs to process the results immediately.
                await agent.manager.schedule_cycle(agent.agent_id)
            else:
                # Check if agent is in a workflow state that should be preserved
                workflow_states = {AgentState.BUILD_TEAM_TASKS, AgentState.ACTIVATE_WORKERS, AgentState.MANAGE, 
                                  AgentState.PLANNING, AgentState.CONVERSATION, AgentState.WORK, AgentState.WAIT}
                
                if agent.current_state not in workflow_states and agent.current_state != AgentState.ERROR:
                    # If the cycle finished normally and not in a workflow state, set agent to IDLE
                    await self.workflow_manager.change_agent_state(agent, AgentState.IDLE)
                # Otherwise, the agent is already in the correct state (set by workflow manager)

        except Exception as e:
            self.logger.error(f"[{agent.agent_id}] Critical error during agent cycle: {e}", category="agent", function="run_cycle", exc_info=True)
            try:
                await self.workflow_manager.change_agent_state(agent, AgentState.ERROR)
            except Exception as e2:
                self.logger.critical(f"[{agent.agent_id}] Could not transition to ERROR state after critical failure: {e2}", category="agent", function="run_cycle")
    
    async def _check_auto_transitions(self, agent: Agent):
        """
        Check if the agent should automatically transition to a new state based on its current context.
        """
        from core.ai.agents import AgentRole, AgentState
        
        # PM in ACTIVATE_WORKERS state: check if all tasks are assigned
        if agent.role == AgentRole.PM and agent.current_state == AgentState.ACTIVATE_WORKERS:
            # Check if all workers have been assigned tasks
            worker_map = agent.memory.short_term.get("worker_map", {})
            tasks = agent.memory.short_term.get("tasks", [])
            
            if len(worker_map) > 0 and len(worker_map) == len(tasks):
                # Check message history to see if we've sent messages to all workers
                workers_assigned: set[str] = set()
                for msg in reversed(agent.message_history):
                    if msg.role == "tool" and "send_message" in str(msg.content):
                        # Extract worker ID from tool result
                        for worker_id in worker_map.values():
                            if worker_id in str(msg.content):
                                workers_assigned.add(str(worker_id))
                
                # If all workers have been assigned, transition to MANAGE
                if len(workers_assigned) == len(worker_map):
                    self.logger.info(f"[{agent.agent_id}] All {len(worker_map)} tasks assigned. Auto-transitioning to MANAGE state", category="agent", function="_check_auto_transitions")
                    await self.workflow_manager.change_agent_state(agent, AgentState.MANAGE,
                                                                   context="All tasks have been assigned to workers. Now monitor their progress.")
