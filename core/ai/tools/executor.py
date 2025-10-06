# START OF FILE core/ai/tools/executor.py
"""
HAI-Net Tool Executor
Discovers, validates, and executes tools for agents.
"""

import asyncio
from typing import Dict, Any, List, Optional

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import AgentManager
from .communication import SendMessageTool

class ToolExecutor:
    """
    Manages and executes tools available to agents.
    """
    def __init__(self, settings: HAINetSettings, agent_manager: AgentManager):
        self.settings = settings
        self.logger = get_logger("ai.tools.executor", settings)
        self.agent_manager = agent_manager
        self.tools: Dict[str, Any] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """
        Auto-discovers and registers available tools.
        """
        self.logger.debug_init("Initializing and discovering tools...", function="_initialize_tools")
        # This will be expanded to scan for tool plugins.
        send_message_tool = SendMessageTool(self.settings, self.agent_manager)
        self.register_tool("send_message", send_message_tool.execute)
        self.logger.info(f"Tool discovery complete. Registered {len(self.tools)} tool(s)", category="init", function="_initialize_tools")

    def register_tool(self, name: str, tool: Any):
        """Registers a single tool."""
        if name in self.tools:
            self.logger.warning(f"Tool '{name}' is already registered. Overwriting", category="agent", function="register_tool")
        self.tools[name] = tool
        self.logger.debug(f"Tool '{name}' registered successfully", category="agent", function="register_tool")

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a registered tool by name with the given arguments.
        """
        # Get sender_agent for logging context if available
        sender_id = args.get('sender_agent', 'unknown')
        sender_id = getattr(sender_id, 'agent_id', str(sender_id))
        
        self.logger.debug_agent(f"[{sender_id}] Executing tool '{name}' with {len(args)-1} arg(s)", function="execute_tool")
        
        if name not in self.tools:
            self.logger.error(f"[{sender_id}] Tool '{name}' not found", category="agent", function="execute_tool")
            return {"error": f"Tool '{name}' not found."}

        try:
            tool_func = self.tools[name]
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)

            self.logger.debug_agent(f"[{sender_id}] Tool '{name}' executed successfully", function="execute_tool")
            return {"result": result}
        except Exception as e:
            self.logger.error(f"[{sender_id}] Error executing tool '{name}': {e}", category="agent", function="execute_tool")
            return {"error": f"Error executing tool '{name}': {e}"}

    def get_available_tools(self) -> List[str]:
        """Returns a list of available tool names."""
        return list(self.tools.keys())
