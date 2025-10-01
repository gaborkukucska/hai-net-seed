# START OF FILE core/ai/workflow_manager.py
"""
HAI-Net Workflow Manager
Manages agent state transitions and high-level, multi-step workflows.
"""

from typing import Dict, Any, List, Optional
import asyncio

from core.logging.logger import get_logger
from core.config.settings import HAINetSettings
from core.ai.agents import Agent, AgentState, AgentStateTransitions

class WorkflowManager:
    """
    Orchestrates complex workflows and manages agent state transitions.
    """
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.workflow_manager", settings)
        # In a real implementation, this would hold workflow definitions.
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
        Placeholder for now.
        """
        self.logger.debug(f"Checking output from agent {agent.agent_id} for workflow triggers.")
        # Example: if agent output contains a <plan> tag, trigger a project creation workflow.
        # This will be implemented in a later step.
        pass

if __name__ == "__main__":

    # Mock Agent for testing
    class MockAgent:
        def __init__(self, agent_id, initial_state):
            self.agent_id = agent_id
            self.current_state = initial_state
            self.state_history = []
            self.logger = get_logger("mock_agent", HAINetSettings())

        async def _transition_state(self, new_state):
            print(f"MockAgent: Transitioning from {self.current_state.value} to {new_state.value}")
            self.current_state = new_state
            self.state_history.append(new_state)

    async def test_workflow_manager():
        print("Testing WorkflowManager...")
        settings = HAINetSettings()
        workflow_manager = WorkflowManager(settings)

        mock_agent = MockAgent("test_agent_001", AgentState.IDLE)

        print(f"Initial state: {mock_agent.current_state.value}")

        # Test valid transition
        success = await workflow_manager.change_agent_state(mock_agent, AgentState.PLANNING)
        print(f"Valid transition (IDLE -> PLANNING) successful: {success}")
        print(f"New state: {mock_agent.current_state.value}")

        # Test invalid transition
        success_invalid = await workflow_manager.change_agent_state(mock_agent, AgentState.SHUTDOWN)
        print(f"Invalid transition (PLANNING -> SHUTDOWN) successful: {success_invalid}")
        print(f"State after invalid attempt: {mock_agent.current_state.value}")

    asyncio.run(test_workflow_manager())