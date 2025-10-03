# START OF FILE core/ai/workflow_manager.py
"""
HAI-Net Workflow Manager
Manages agent state transitions and high-level, multi-step workflows.
"""

from typing import Dict, Any, List, Optional
import asyncio

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentState, AgentStateTransitions

class WorkflowManager:
    """
    Orchestrates complex workflows and manages agent state transitions.
    """
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.workflow_manager", settings)
        self.workflows: Dict[str, Any] = {}

    async def change_agent_state(self, agent: Agent, new_state: AgentState) -> bool:
        """
        Changes an agent's state, ensuring the transition is valid.
        """
        if AgentStateTransitions.is_valid_transition(agent.current_state, new_state):
            self.logger.info(f"Transitioning agent {agent.agent_id} from {agent.current_state.value} to {new_state.value}")
            await agent._transition_state(new_state)
            return True
        else:
            self.logger.error(f"Invalid state transition for agent {agent.agent_id}: "
                              f"from {agent.current_state.value} to {new_state.value}")
            return False

    async def process_agent_output_for_workflow(self, agent: Agent, output: Dict[str, Any]):
        """
        Analyzes agent output to see if it triggers a high-level workflow.
        """
        self.logger.debug(f"Checking output from agent {agent.agent_id} for workflow triggers.")
        # This will be expanded later to handle workflows like project creation.
        pass