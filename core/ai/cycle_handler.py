# START OF FILE core/ai/cycle_handler.py
"""
HAI-Net Agent Cycle Handler
Drives the agent execution loop by processing events from agents.
"""

from typing import Dict, Any, List, Optional
import asyncio

from core.logging.logger import get_logger
from core.config.settings import HAINetSettings
from core.ai.agents import Agent, AgentState
from core.ai.interaction_handler import InteractionHandler
from core.ai.workflow_manager import WorkflowManager
from core.ai.guardian import ConstitutionalGuardian

class AgentCycleHandler:
    """
    Manages a single execution cycle of an agent.
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
        Runs a full processing cycle for a given agent.
        """
        if agent.current_state == AgentState.PROCESSING:
            self.logger.warning(f"Agent {agent.agent_id} is already processing. Cycle aborted.")
            return

        await self.workflow_manager.change_agent_state(agent, AgentState.PROCESSING)

        try:
            self.logger.info(f"Starting cycle for agent {agent.agent_id} in state {agent.previous_state.value}")

            # The core of the cycle: iterate through the agent's yielded events
            async for event in agent.process_message():
                event_type = event.get("type")
                self.logger.debug(f"Agent {agent.agent_id} yielded event: {event_type}")

                if event_type == "tool_requests":
                    # In a real implementation, we would process tool calls here
                    # using self.interaction_handler
                    self.logger.info(f"Agent {agent.agent_id} requested tools: {event.get('calls')}")
                    pass # Placeholder

                elif event_type == "agent_state_change_requested":
                    new_state = AgentState(event.get("new_state"))
                    await self.workflow_manager.change_agent_state(agent, new_state)

                elif event_type == "final_response":
                    content = event.get("content", "")
                    self.logger.debug(f"Agent {agent.agent_id} produced final response. Sending to Guardian for review.")

                    review_result = await self.guardian.review_output(agent, content)

                    if review_result["compliant"]:
                        self.logger.info(f"Guardian approved output from agent {agent.agent_id}.")
                        # TODO: Add compliant response to message history and broadcast to user/other agents
                        self.logger.info(f"Final response from {agent.agent_id}: {content}")
                    else:
                        self.logger.warning(f"Guardian blocked output from agent {agent.agent_id}. Reason: {review_result.get('reason')}")
                        # TODO: Handle violation, e.g., send system message back to agent
                        self.logger.warning(f"Blocked content: {content}")

                    break # End the cycle on final response

                elif event_type == "agent_thought":
                    self.logger.info(f"Agent {agent.agent_id} thought: {event.get('content')}")

                else:
                    self.logger.warning(f"Unknown event type from agent {agent.agent_id}: {event_type}")

        except Exception as e:
            self.logger.error(f"Error during agent cycle for {agent.agent_id}: {e}", exc_info=True)
            await self.workflow_manager.change_agent_state(agent, AgentState.ERROR)

        finally:
            # After the loop, transition the agent back to IDLE unless it's in an error state
            if agent.current_state == AgentState.PROCESSING:
                await self.workflow_manager.change_agent_state(agent, AgentState.IDLE)
            self.logger.info(f"Cycle finished for agent {agent.agent_id}. Final state: {agent.current_state.value}")


if __name__ == "__main__":
    from core.ai.tools.executor import ToolExecutor
    from core.ai.agents import AgentManager

    async def test_cycle_handler():
        print("Testing AgentCycleHandler...")
        settings = HAINetSettings()

        # Setup all components
        tool_executor = ToolExecutor(settings)
        interaction_handler = InteractionHandler(settings, tool_executor)
        # The guardian needs to be mocked or created properly
        guardian = ConstitutionalGuardian(settings)
        workflow_manager = WorkflowManager(settings)

        cycle_handler = AgentCycleHandler(settings, interaction_handler, workflow_manager, guardian)

        # Mock an agent manager and an agent
        agent_manager = AgentManager(settings)
        agent_manager.set_handlers(cycle_handler, workflow_manager)

        agent_id = await agent_manager.create_agent(role=AgentState.CONVERSATION)
        agent = agent_manager.get_agent(agent_id)

        print(f"Created agent {agent.agent_id} with initial state {agent.current_state.value}")

        # Run a cycle
        await cycle_handler.run_cycle(agent)

        print(f"Agent state after cycle: {agent.current_state.value}")

    asyncio.run(test_cycle_handler())