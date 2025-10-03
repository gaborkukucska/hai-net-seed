# START OF FILE core/ai/cycle_handler.py
"""
HAI-Net Agent Cycle Handler
Drives the agent execution loop by processing events from agents, as described
in the TrippleEffect framework.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentState
from core.ai.llm import LLMMessage
from core.ai.interaction_handler import InteractionHandler
from core.ai.workflow_manager import WorkflowManager
from core.ai.guardian import ConstitutionalGuardian

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

    async def run_cycle(self, agent: Agent):
        """
        Runs a full processing cycle for a given agent, based on the TrippleEffect architecture.
        """
        if agent.current_state == AgentState.PROCESSING:
            self.logger.warning(f"Agent {agent.agent_id} is already processing. Aborting new cycle.")
            return

        try:
            # 1. Set agent state to PROCESSING
            await self.workflow_manager.change_agent_state(agent, AgentState.PROCESSING)

            self.logger.info(f"Starting cycle for agent {agent.agent_id} in state {agent.previous_state.value}")

            # 2. Prepare LLM call data (simplified for now)
            # In a real implementation, a PromptAssembler would inject system prompts here.
            messages_for_llm = agent.message_history

            # 3. Process events from the agent's generator
            cycle_completed = False
            start_time = time.time()
            reschedule = False

            async for event in agent.process_message(messages_for_llm):
                event_type = event.get("type")

                if event_type == "agent_thought":
                    self.logger.info(f"Agent {agent.agent_id} Thought: {event.get('content')}")
                    # In a real system, this would be logged to a DB for observability.

                elif event_type == "tool_requests":
                    tool_calls = event.get("calls", [])
                    self.logger.info(f"Agent {agent.agent_id} requests tools: {tool_calls}")

                    for tool_call in tool_calls:
                        result = await self.interaction_handler.execute_tool_call(agent, tool_call)
                        # Format result and append to history for the agent to process
                        tool_result_message = LLMMessage(
                            role="tool",
                            content=str(result), # Ensure content is string
                            timestamp=time.time(),
                            metadata={'tool_name': tool_call.get('name')}
                        )
                        agent.message_history.append(tool_result_message)

                    # The agent needs to process the tool results, so we schedule another cycle.
                    reschedule = True
                    cycle_completed = True
                    break

                elif event_type == "agent_state_change_requested":
                    new_state_str = event.get("new_state")
                    if new_state_str:
                        new_state = AgentState(new_state_str)
                        await self.workflow_manager.change_agent_state(agent, new_state)
                        self.logger.info(f"Agent {agent.agent_id} requested state change to {new_state.value}")
                    cycle_completed = True # State change often ends a turn
                    break

                elif event_type == "final_response":
                    content = event.get("content", "")

                    # In a real system, the guardian would be more deeply integrated.
                    # For now, we log and proceed.
                    # self.guardian.check(content)
                    self.logger.info(f"Agent {agent.agent_id} final response: {content}")

                    agent.message_history.append(LLMMessage(role="assistant", content=content, timestamp=time.time()))
                    cycle_completed = True
                    break

                elif event_type == "error":
                    self.logger.error(f"Agent {agent.agent_id} reported an error: {event.get('content')}")
                    await self.workflow_manager.change_agent_state(agent, AgentState.ERROR)
                    cycle_completed = True
                    break

            execution_time = time.time() - start_time
            agent._update_response_time_metric(execution_time)

            # 5. Determine next step and set final state
            if reschedule:
                # If a tool was called, the agent needs to process the results immediately.
                await agent.manager.schedule_cycle(agent.agent_id)
            elif agent.current_state != AgentState.ERROR:
                # If the cycle finished normally, set agent to IDLE.
                await self.workflow_manager.change_agent_state(agent, AgentState.IDLE)

        except Exception as e:
            self.logger.error(f"Critical error during agent cycle for {agent.agent_id}: {e}", exc_info=True)
            try:
                await self.workflow_manager.change_agent_state(agent, AgentState.ERROR)
            except Exception as e2:
                self.logger.critical(f"Could not transition agent {agent.agent_id} to ERROR state after critical failure: {e2}")