# START OF FILE core/ai/cycle_handler.py
"""
HAI-Net Agent Cycle Handler
Drives the agent execution loop by processing events from agents, as described
in the TrippleEffect framework.
"""

import time
from typing import Optional

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentState
from core.ai.llm import LLMMessage
from core.ai.interaction_handler import InteractionHandler
from core.ai.workflow_manager import WorkflowManager
from core.ai.guardian import ConstitutionalGuardian
from core.ai.prompt_assembler import PromptAssembler
from core.ai.events import EventEmitter, AgentEvent, EventType, ResponseCollector
from core.ai.memory import MemoryManager, MemoryType, MemoryImportance

class AgentCycleHandler:
    """
    Manages a single execution cycle of an agent. It orchestrates the process
    of getting events from an agent, handling them, and determining the agent's
    next state.
    """
    def __init__(self, settings: HAINetSettings,
                 interaction_handler: InteractionHandler,
                 workflow_manager: WorkflowManager,
                 guardian: ConstitutionalGuardian,
                 event_emitter: Optional[EventEmitter] = None,
                 response_collector: Optional[ResponseCollector] = None,
                 memory_manager: Optional[MemoryManager] = None):
        self.settings = settings
        self.logger = get_logger("ai.cycle_handler", settings)
        self.interaction_handler = interaction_handler
        self.workflow_manager = workflow_manager
        self.guardian = guardian
        self.prompt_assembler = PromptAssembler(settings)
        self.event_emitter = event_emitter
        self.response_collector = response_collector
        self.memory_manager = memory_manager

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

            # 2. Emit agent thinking event
            if self.event_emitter:
                await self.event_emitter.emit(AgentEvent(
                    event_type=EventType.AGENT_THINKING,
                    agent_id=agent.agent_id,
                    timestamp=time.time(),
                    data={
                        "role": agent.role.value,
                        "state": agent.current_state.value,
                        "message": "Processing your request..."
                    },
                    user_did=agent.user_did
                ))

            # 3. Set agent state to PROCESSING
            await self.workflow_manager.change_agent_state(agent, AgentState.PROCESSING)

            # 4. Process events from the agent's generator
            start_time = time.time()
            reschedule = False
            accumulated_response = ""

            async for event in agent.process_message(messages_for_llm):
                event_type = event.get("type")

                if event_type == "agent_thought":
                    self.logger.debug_agent(f"[{agent.agent_id}] Thought: {event.get('content')}", function="run_cycle")
                    # Don't emit another AGENT_THINKING event here - we already emitted one at the start of the cycle
                
                elif event_type == "response_chunk":
                    chunk = event.get("content", "")
                    accumulated_response += chunk
                    
                    # Emit chunk event for real-time streaming
                    if self.event_emitter:
                        await self.event_emitter.emit(AgentEvent(
                            event_type=EventType.RESPONSE_CHUNK,
                            agent_id=agent.agent_id,
                            timestamp=time.time(),
                            data={"chunk": chunk},
                            user_did=agent.user_did
                        ))
                    
                    # Also add to response collector for streaming display
                    if self.response_collector:
                        await self.response_collector.add_chunk(agent.agent_id, chunk)

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
                        
                        # Store tool execution in procedural memory
                        if self.memory_manager:
                            tool_name = tool_call.get('name', 'unknown')
                            tool_args = tool_call.get('arguments', {})
                            await self.memory_manager.store_memory(
                                agent_id=agent.agent_id,
                                content=f"Executed tool '{tool_name}' with result: {str(result)[:200]}",
                                memory_type=MemoryType.PROCEDURAL,
                                importance=MemoryImportance.MEDIUM,
                                metadata={
                                    "event": "tool_execution",
                                    "tool_name": tool_name,
                                    "tool_args": str(tool_args)[:500],
                                    "result_preview": str(result)[:200],
                                    "role": agent.role.value,
                                    "state": agent.current_state.value
                                }
                            )

                    # The agent needs to process the tool results, so we schedule another cycle.
                    reschedule = True
                    break

                elif event_type == "agent_state_change_requested":
                    new_state_str = event.get("new_state")
                    if new_state_str:
                        old_state = agent.current_state
                        new_state = AgentState(new_state_str)
                        await self.workflow_manager.change_agent_state(agent, new_state)
                        self.logger.info(f"[{agent.agent_id}] State change requested: {old_state.value} -> {new_state.value}", category="agent", function="run_cycle")
                        
                        # Store state transition in episodic memory
                        if self.memory_manager:
                            await self.memory_manager.store_memory(
                                agent_id=agent.agent_id,
                                content=f"State changed from {old_state.value} to {new_state.value}",
                                memory_type=MemoryType.EPISODIC,
                                importance=MemoryImportance.MEDIUM,
                                metadata={
                                    "event": "state_transition",
                                    "old_state": old_state.value,
                                    "new_state": new_state.value,
                                    "role": agent.role.value
                                }
                            )
                        
                        # Automatically reschedule agent to continue processing in new state
                        await agent.manager.schedule_cycle(agent.agent_id)
                        self.logger.debug_agent(f"[{agent.agent_id}] Rescheduled to continue in {new_state.value} state", function="run_cycle")
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
                    
                    # Store plan creation in episodic memory with HIGH importance
                    if self.memory_manager:
                        await self.memory_manager.store_memory(
                            agent_id=agent.agent_id,
                            content=f"Created project plan: {plan.get('project_name', 'Unnamed')}",
                            memory_type=MemoryType.EPISODIC,
                            importance=MemoryImportance.HIGH,
                            metadata={
                                "event": "plan_created",
                                "project_name": plan.get('project_name', 'Unnamed'),
                                "plan_details": str(plan)[:1000],
                                "role": agent.role.value
                            }
                        )
                    
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
                    
                    # Store task list creation in episodic memory with HIGH importance
                    if self.memory_manager:
                        task_summaries = [f"{i+1}. {t.get('description', 'No description')[:100]}" for i, t in enumerate(tasks[:5])]
                        await self.memory_manager.store_memory(
                            agent_id=agent.agent_id,
                            content=f"Created task list with {len(tasks)} tasks: " + "; ".join(task_summaries),
                            memory_type=MemoryType.EPISODIC,
                            importance=MemoryImportance.HIGH,
                            metadata={
                                "event": "task_list_created",
                                "task_count": len(tasks),
                                "tasks": str(tasks)[:2000],
                                "role": agent.role.value
                            }
                        )
                    
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
                    accumulated_response = content

                    # Constitutional Guardian check for response compliance
                    await self._check_response_compliance(agent, content)
                    
                    self.logger.debug_agent(f"[{agent.agent_id}] Final response generated (length={len(content)} chars)", function="run_cycle")

                    agent.message_history.append(LLMMessage(role="assistant", content=content, timestamp=time.time()))
                    
                    # Store important conversations in episodic memory
                    if self.memory_manager and len(content) > 50:  # Only store substantial responses
                        # Determine importance based on content length and context
                        importance = MemoryImportance.MEDIUM
                        if len(content) > 500 or any(keyword in content.lower() for keyword in ['completed', 'finished', 'done', 'success']):
                            importance = MemoryImportance.HIGH
                        
                        await self.memory_manager.store_memory(
                            agent_id=agent.agent_id,
                            content=content[:500],  # Store first 500 chars
                            memory_type=MemoryType.EPISODIC,
                            importance=importance,
                            metadata={
                                "event": "agent_response",
                                "role": agent.role.value,
                                "state": agent.current_state.value,
                                "response_length": len(content)
                            }
                        )
                    
                    # Emit response complete event
                    if self.event_emitter:
                        await self.event_emitter.emit(AgentEvent(
                            event_type=EventType.RESPONSE_COMPLETE,
                            agent_id=agent.agent_id,
                            timestamp=time.time(),
                            data={
                                "response": content,
                                "role": agent.role.value
                            },
                            user_did=agent.user_did
                        ))
                    
                    # Notify response collector
                    if self.response_collector:
                        await self.response_collector.complete_response(agent.agent_id, content)
                    
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
    
    async def _check_response_compliance(self, agent: Agent, content: str):
        """
        Check agent response for constitutional compliance using the Guardian.
        """
        try:
            from .guardian import ViolationType, ViolationSeverity
            
            # Privacy check - look for potential personal data exposure
            privacy_patterns = [
                "social security", "ssn", "credit card", "password", "api key",
                "email", "phone number", "home address", "passport"
            ]
            
            content_lower = content.lower()
            for pattern in privacy_patterns:
                if pattern in content_lower:
                    await self.guardian.report_violation(
                        ViolationType.PRIVACY_VIOLATION,
                        ViolationSeverity.HIGH,
                        "Privacy First",
                        f"Agent response may contain sensitive information: {pattern}",
                        f"agent_{agent.role.value}",
                        source_agent=agent.agent_id,
                        details={"pattern_matched": pattern, "response_length": len(content)}
                    )
                    self.logger.warning(f"[{agent.agent_id}] Privacy concern detected in response: {pattern}")
            
            # Human rights check - look for bias or harmful content
            harmful_patterns = [
                "discriminat", "bias against", "inferior", "superior race",
                "manipulat", "deceive", "trick the user"
            ]
            
            for pattern in harmful_patterns:
                if pattern in content_lower:
                    await self.guardian.report_violation(
                        ViolationType.HUMAN_RIGHTS_VIOLATION,
                        ViolationSeverity.MEDIUM,
                        "Human Rights",
                        f"Agent response contains potentially harmful language: {pattern}",
                        f"agent_{agent.role.value}",
                        source_agent=agent.agent_id,
                        details={"pattern_matched": pattern}
                    )
                    self.logger.warning(f"[{agent.agent_id}] Human rights concern detected: {pattern}")
            
            # Centralization check - look for references to central control
            centralization_patterns = [
                "central server only", "must use cloud", "require central authority",
                "single point of control", "centralized database only"
            ]
            
            for pattern in centralization_patterns:
                if pattern in content_lower:
                    await self.guardian.report_violation(
                        ViolationType.CENTRALIZATION_VIOLATION,
                        ViolationSeverity.LOW,
                        "Decentralization",
                        f"Agent response suggests centralization: {pattern}",
                        f"agent_{agent.role.value}",
                        source_agent=agent.agent_id,
                        details={"pattern_matched": pattern}
                    )
            
            # Log clean responses
            if agent.agent_id and not any(p in content_lower for p in privacy_patterns + harmful_patterns + centralization_patterns):
                self.logger.debug_agent(f"[{agent.agent_id}] Response passed constitutional compliance checks", function="_check_response_compliance")
                
        except Exception as e:
            self.logger.error(f"Constitutional compliance check failed: {e}", category="guardian", function="_check_response_compliance")
    
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
