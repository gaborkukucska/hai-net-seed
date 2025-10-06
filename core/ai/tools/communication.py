# START OF FILE core/ai/tools/communication.py
"""
HAI-Net Communication Tools
Tools that enable agents to communicate with each other.
"""

import time
from typing import Dict, Any, Optional
import asyncio

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.ai.agents import Agent, AgentManager
from core.ai.llm import LLMMessage

class SendMessageTool:
    """
    A tool that allows an agent to send a message to another agent,
    as described in the TrippleEffect framework.
    """
    def __init__(self, settings: HAINetSettings, agent_manager: AgentManager):
        self.settings = settings
        self.agent_manager = agent_manager
        self.logger = get_logger("ai.tools.communication", settings)

    async def execute(self, sender_agent: Agent, target_agent_id: str, message: str) -> Dict[str, Any]:
        """
        Executes the send message tool. Finds the target agent, appends the
        message to its history, and schedules a cycle for it to process.

        Args:
            sender_agent: The agent sending the message (injected by InteractionHandler).
            target_agent_id: The ID of the agent to receive the message.
            message: The content of the message.

        Returns:
            A dictionary indicating the status of the operation.
        """
        self.logger.debug_agent(f"[{sender_agent.agent_id}] Sending message to {target_agent_id} (length={len(message)} chars)", function="execute")

        target_agent = self.agent_manager.get_agent(target_agent_id)
        if not target_agent:
            error_msg = f"Target agent with ID '{target_agent_id}' not found."
            self.logger.error(f"[{sender_agent.agent_id}] {error_msg}", category="agent", function="execute")
            return {"status": "error", "message": error_msg}

        # Format the message to include the sender's identity
        formatted_message = f"[From @{sender_agent.agent_id}]: {message}"

        # Create an LLMMessage and append it to the target agent's history
        llm_message = LLMMessage(
            role="user", # From the target's perspective, this is a user-like message
            content=formatted_message,
            timestamp=time.time()
        )
        target_agent.message_history.append(llm_message)

        # Schedule the target agent to wake up and process the new message
        await self.agent_manager.schedule_cycle(target_agent_id)

        success_msg = f"Message successfully sent to agent {target_agent_id}."
        self.logger.debug_agent(f"[{sender_agent.agent_id}] ✅ Message delivered to {target_agent_id}", function="execute")
        return {"status": "success", "message": success_msg}
