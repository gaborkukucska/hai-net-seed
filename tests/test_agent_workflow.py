# START OF FILE tests/test_agent_workflow.py
"""
Integration Test for HAI-Net Agent Workflow
Validates the end-to-end functionality of the TrippleEffect-based agent hierarchy.
"""

import asyncio
import pytest
import pytest_asyncio
import time
from typing import Dict, Any

from core.config.settings import HAINetSettings
from core.ai.agents import AgentManager, AgentRole, Agent
from core.ai.llm import LLMManager, LLMMessage
from core.ai.guardian import ConstitutionalGuardian
from core.ai.tools.executor import ToolExecutor
from core.ai.interaction_handler import InteractionHandler
from core.ai.workflow_manager import WorkflowManager
from core.ai.cycle_handler import AgentCycleHandler

# Mock LLMManager to control agent responses for predictable testing
class MockLLMManager(LLMManager):
    def __init__(self, settings):
        super().__init__(settings)
        self.responses: Dict[str, str] = {}
        self.requests = []

    def set_response(self, agent_role: str, response: str):
        self.responses[agent_role] = response

    async def stream_response(self, messages: list, model: str, user_did: str):
        self.requests.append({"messages": messages, "model": model})

        # Determine which agent is calling based on its last message
        # This is a simplification for testing purposes.
        role = "worker" # default
        if any("I am the Admin" in m.content for m in messages):
             role = "admin"
        elif any("I am the PM" in m.content for m in messages):
             role = "pm"

        response_str = self.responses.get(role, "No mock response set for this role.")
        yield response_str

@pytest_asyncio.fixture
async def full_agent_system():
    """Sets up the full agent system with mocks for testing."""
    settings = HAINetSettings()
    guardian = ConstitutionalGuardian(settings)

    # Use the mock LLM Manager
    llm_manager = MockLLMManager(settings)

    agent_manager = AgentManager(settings, llm_manager=llm_manager)
    tool_executor = ToolExecutor(settings, agent_manager=agent_manager)
    interaction_handler = InteractionHandler(settings, tool_executor)
    workflow_manager = WorkflowManager(settings)
    cycle_handler = AgentCycleHandler(settings, interaction_handler, workflow_manager, guardian)

    agent_manager.set_handlers(cycle_handler, workflow_manager)

    return agent_manager, llm_manager

@pytest.mark.asyncio
async def test_full_agent_workflow(full_agent_system):
    """
    Tests a full Admin -> PM -> Worker delegation workflow.
    """
    agent_manager, mock_llm_manager = full_agent_system

    # 1. Create the agents
    admin_id = await agent_manager.create_agent(AgentRole.ADMIN, user_did="test_user")
    pm_id = await agent_manager.create_agent(AgentRole.PM)
    worker_id = await agent_manager.create_agent(AgentRole.WORKER)

    assert admin_id is not None
    assert pm_id is not None
    assert worker_id is not None

    admin_agent = agent_manager.get_agent(admin_id)
    pm_agent = agent_manager.get_agent(pm_id)
    worker_agent = agent_manager.get_agent(worker_id)

    # 2. Define mock responses for each agent role
    # Admin will delegate to PM
    mock_llm_manager.set_response("admin", f"""
        <tool_requests>
            <calls>
                <tool_call>
                    <name>send_message</name>
                    <args>
                        <target_agent_id>{pm_id}</target_agent_id>
                        <message>Please manage the project: 'Deploy the webapp'.</message>
                    </args>
                </tool_call>
            </calls>
        </tool_requests>
    """)

    # PM will delegate to Worker
    mock_llm_manager.set_response("pm", f"""
        <tool_requests>
            <calls>
                <tool_call>
                    <name>send_message</name>
                    <args>
                        <target_agent_id>{worker_id}</target_agent_id>
                        <message>Your task is to write the deployment script.</message>
                    </args>
                </tool_call>
            </calls>
        </tool_requests>
    """)

    # Worker will "complete" the task
    mock_llm_manager.set_response("worker", "Deployment script is complete. Pasting it here: `Done`")

    # 3. Kick off the workflow with a user message to the Admin
    # We add a marker to the message to identify the agent in the mock LLM
    admin_agent.message_history.append(LLMMessage(role="system", content="I am the Admin.", timestamp=time.time()))
    pm_agent.message_history.append(LLMMessage(role="system", content="I am the PM.", timestamp=time.time()))
    worker_agent.message_history.append(LLMMessage(role="system", content="I am the Worker.", timestamp=time.time()))
    await agent_manager.handle_user_message("Deploy the new webapp.", user_did="test_user")

    # 4. Wait for the workflow to propagate
    # This needs to be long enough for all three agents to run their cycles.
    await asyncio.sleep(3)

    # 5. Assert the final state
    # Check that the PM received the message from the Admin
    assert any("Please manage the project" in m.content for m in pm_agent.message_history)

    # Check that the Worker received the message from the PM
    assert any("Your task is to write the deployment script" in m.content for m in worker_agent.message_history)

    # Check that the worker produced the final output
    assert any("Deployment script is complete" in m.content for m in worker_agent.message_history)

    print("\n✅ Full agent workflow test passed!")
    print(f"Admin History: {[m.content for m in admin_agent.message_history]}")
    print(f"PM History: {[m.content for m in pm_agent.message_history]}")
    print(f"Worker History: {[m.content for m in worker_agent.message_history]}")