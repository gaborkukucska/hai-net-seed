# START OF FILE core/ai/interaction_handler.py
"""
HAI-Net Interaction Handler
Mediates tool execution for agents.
"""

from typing import Dict, Any

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.tools.executor import ToolExecutor
from core.ai.agents import Agent

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
        Injects the calling agent into the arguments for context.
        """
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})

        if not tool_name:
            error_msg = "Malformed tool call: missing 'name'."
            self.logger.error(f"[{agent.agent_id}] {error_msg}", category="agent", function="execute_tool_call")
            return {"error": error_msg}

        self.logger.debug_agent(f"[{agent.agent_id}] Executing tool '{tool_name}' with args: {tool_args}", function="execute_tool_call")

        # Inject the sender agent into the tool arguments for context
        tool_args_with_sender = tool_args.copy()
        tool_args_with_sender['sender_agent'] = agent

        # Execute the tool via the ToolExecutor
        execution_result = await self.tool_executor.execute_tool(tool_name, tool_args_with_sender)

        # Log the interaction for constitutional audit (without the injected sender)
        self.logger.log_community_event(
            action=f"tool_executed_{tool_name}",
            community_benefit=True
        )

        return execution_result
