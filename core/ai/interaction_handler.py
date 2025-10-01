# START OF FILE core/ai/interaction_handler.py
"""
HAI-Net Interaction Handler
Mediates tool execution for agents.
"""

from typing import Dict, Any, List, Optional
import asyncio

from core.logging.logger import get_logger
from core.config.settings import HAINetSettings
from core.ai.tools.executor import ToolExecutor
from core.ai.agents import Agent # Forward declaration if needed, but should be fine

class InteractionHandler:
    """
    Handles the interaction between an agent's request and the tool executor.
    """
    def __init__(self, settings: HAINetSettings, tool_executor: ToolExecutor):
        self.settings = settings
        self.logger = get_logger("ai.interaction_handler", settings)
        self.tool_executor = tool_executor

    async def execute_tool_call(self, agent: Agent, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single tool call requested by an agent and returns the result.
        """
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})

        if not tool_name:
            error_msg = "Malformed tool call: missing 'name'."
            self.logger.error(error_msg)
            return {"error": error_msg}

        self.logger.info(f"Agent {agent.agent_id} is calling tool '{tool_name}' with args: {tool_args}")

        # Execute the tool via the ToolExecutor
        execution_result = await self.tool_executor.execute_tool(tool_name, tool_args)

        # Here, we would typically format the result into a message for the agent's history
        # For now, we just return the raw result.

        # Log the interaction for constitutional audit
        self.logger.log_community_event(
            event_type=f"tool_executed_{tool_name}",
            community_benefit=True,  # Assume tools are for community benefit
            details={"agent_id": agent.agent_id, "args": tool_args, "result": execution_result}
        )

        return execution_result

if __name__ == "__main__":
    async def test_interaction_handler():
        print("Testing InteractionHandler...")
        settings = HAINetSettings()
        tool_executor = ToolExecutor(settings)
        interaction_handler = InteractionHandler(settings, tool_executor)

        # Mock an agent
        class MockAgent:
            agent_id = "test_agent_001"

        mock_agent = MockAgent()

        # Mock a tool call
        tool_call = {
            "name": "placeholder_tool",
            "args": {"param1": "value1"}
        }

        result = await interaction_handler.execute_tool_call(mock_agent, tool_call)
        print(f"Result from placeholder_tool: {result}")

        # Test non-existent tool
        tool_call_bad = {
            "name": "non_existent_tool",
            "args": {}
        }
        result_bad = await interaction_handler.execute_tool_call(mock_agent, tool_call_bad)
        print(f"Result from non_existent_tool: {result_bad}")

    asyncio.run(test_interaction_handler())