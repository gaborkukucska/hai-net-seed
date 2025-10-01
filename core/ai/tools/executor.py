# START OF FILE core/ai/tools/executor.py
"""
HAI-Net Tool Executor
Discovers, validates, and executes tools for agents.
"""

import asyncio
from typing import Dict, Any, List, Optional

from core.logging.logger import get_logger
from core.config.settings import HAINetSettings

class ToolExecutor:
    """
    Manages and executes tools available to agents.
    """
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.tools.executor", settings)
        self.tools: Dict[str, Any] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """
        Auto-discovers and registers available tools.
        Placeholder for now.
        """
        self.logger.info("Initializing and discovering tools...")
        # In a real implementation, this would scan a directory for tool plugins.
        # For now, we can register a placeholder tool.
        self.register_tool("placeholder_tool", self.placeholder_tool)
        self.logger.info(f"Registered tools: {list(self.tools.keys())}")

    def register_tool(self, name: str, tool: Any):
        """Registers a single tool."""
        if name in self.tools:
            self.logger.warning(f"Tool '{name}' is already registered. Overwriting.")
        self.tools[name] = tool
        self.logger.debug(f"Tool '{name}' registered.")

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a registered tool by name with the given arguments.
        """
        self.logger.info(f"Attempting to execute tool '{name}' with args: {args}")
        if name not in self.tools:
            self.logger.error(f"Tool '{name}' not found.")
            return {"error": f"Tool '{name}' not found."}

        try:
            tool_func = self.tools[name]
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)

            self.logger.info(f"Tool '{name}' executed successfully.")
            return {"result": result}
        except Exception as e:
            self.logger.error(f"Error executing tool '{name}': {e}")
            return {"error": f"Error executing tool '{name}': {e}"}

    async def placeholder_tool(self, **kwargs) -> str:
        """A simple placeholder tool for testing."""
        self.logger.info(f"Placeholder tool executed with kwargs: {kwargs}")
        return "Placeholder tool executed successfully."

    def get_available_tools(self) -> List[str]:
        """Returns a list of available tool names."""
        return list(self.tools.keys())

if __name__ == "__main__":
    async def test_executor():
        print("Testing ToolExecutor...")
        settings = HAINetSettings()
        executor = ToolExecutor(settings)

        print(f"Available tools: {executor.get_available_tools()}")

        result = await executor.execute_tool("placeholder_tool", {"arg1": "test"})
        print(f"Execution result: {result}")

        result_not_found = await executor.execute_tool("non_existent_tool", {})
        print(f"Execution result (not found): {result_not_found}")

    asyncio.run(test_executor())