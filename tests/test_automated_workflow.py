# START OF FILE tests/test_automated_workflow.py
"""
Integration Test for the Automated HAI-Net Agent Workflow
Validates the end-to-end functionality of the automated TrippleEffect-based
agent hierarchy, from plan creation to worker execution.
"""

import asyncio
import pytest
import pytest_asyncio
import time
from typing import Dict, Any, List

from core.config.settings import HAINetSettings
from core.ai.agents import AgentManager, AgentRole, AgentState, Agent
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
        # We now need to provide responses based on the agent's state
        self.responses: Dict[str, Dict[str, str]] = {
            "admin": {},
            "pm": {},
            "worker": {}
        }
        self.requests: List[Dict[str, Any]] = []

    def set_response(self, agent_role: str, agent_state: str, response: str):
        if agent_role not in self.responses:
            self.responses[agent_role] = {}
        self.responses[agent_role][agent_state] = response

    async def stream_response(self, messages: list, model: str, user_did: str):
        self.requests.append({"messages": messages, "model": model})

        # Determine agent role and state from the system prompt in the message history
        # This is a more robust way to mock the behavior for our test.
        role = "worker" # default
        state = "work" # default

        # The system prompt injected by PromptAssembler tells us the state
        for m in reversed(messages):
            if m.role == "system":
                if "You are the Admin AI" in m.content:
                    role = "admin"
                    state = "planning" # Assume planning for this test
                elif "You are a Project Manager AI" in m.content:
                    role = "pm"
                    if "Your current state is: startup" in m.content:
                        state = "startup"
                    elif "Your current state is: build_team_tasks" in m.content:
                        state = "build_team_tasks"
                    elif "Your current state is: activate_workers" in m.content:
                        state = "activate_workers"
                elif "You are a Worker AI" in m.content:
                    role = "worker"
                    state = "work"
                break

        response_str = self.responses.get(role, {}).get(state, f"No mock response set for {role} in state {state}.")

        # Stream the response character by character
        for char in response_str:
            yield char
            await asyncio.sleep(0.001) # small delay to simulate streaming

@pytest_asyncio.fixture
async def full_agent_system():
    """Sets up the full agent system with mocks for testing."""
    settings = HAINetSettings()
    guardian = ConstitutionalGuardian(settings)
    llm_manager = MockLLMManager(settings)
    agent_manager = AgentManager(settings, llm_manager=llm_manager)
    tool_executor = ToolExecutor(settings, agent_manager=agent_manager)
    interaction_handler = InteractionHandler(settings, tool_executor)
    workflow_manager = WorkflowManager(settings)
    cycle_handler = AgentCycleHandler(settings, interaction_handler, workflow_manager, guardian)
    agent_manager.set_handlers(cycle_handler, workflow_manager)
    return agent_manager, llm_manager

@pytest.mark.asyncio
async def test_automated_end_to_end_workflow(full_agent_system):
    """
    Tests the full, automated Admin -> PM -> Worker workflow.
    - Admin creates a plan.
    - Framework creates a PM.
    - PM breaks down the plan into tasks.
    - PM requests worker creation.
    - Framework creates a Worker.
    - PM assigns the task to the Worker.
    - Worker executes the task.
    """
    agent_manager, mock_llm_manager = full_agent_system

    # 1. Define the mock LLM responses for each stage of the workflow
    mock_llm_manager.set_response("admin", "planning", """
        <plan>
            <project_name>Deploy a new web server</project_name>
            <description>Deploy the main web application on a new server.</description>
            <objectives>
                - Set up the server environment.
                - Deploy the application code.
            </objectives>
            <deliverables>
                - A running web server accessible at a public IP.
            </deliverables>
        </plan>
    """)

    mock_llm_manager.set_response("pm", "startup", """
        <task_list>
            <task>
                <id>1</id>
                <name>Setup Server Environment</name>
                <description>Install all necessary packages (nginx, python) on the new server.</description>
            </task>
        </task_list>
    """)

    mock_llm_manager.set_response("pm", "build_team_tasks", """
        <create_worker_request>
            <task_id>1</task_id>
            <specialty>devops</specialty>
        </create_worker_request>
    """)

    # This response will be given after the worker is created. The PM now needs to assign the task.
    # We will dynamically set this response later once we know the worker's ID.

    mock_llm_manager.set_response("worker", "work", "Work complete. Server environment is set up.")

    # 2. Kick off the workflow by creating an Admin agent and sending it a message
    admin_id = await agent_manager.create_agent(AgentRole.ADMIN, user_did="test_user")
    assert admin_id is not None
    await agent_manager.handle_user_message("Please create a plan to deploy our webapp.", user_did="test_user")

    # 3. Wait for the initial part of the workflow to complete (Admin -> PM -> Worker creation)
    await asyncio.sleep(2)

    # 4. Assert that the PM and a Worker agent were created
    pm_agents = agent_manager.get_agents_by_role(AgentRole.PM)
    assert len(pm_agents) == 1, "A PM agent should have been created."
    pm_agent = pm_agents[0]

    worker_agents = agent_manager.get_agents_by_role(AgentRole.WORKER)
    assert len(worker_agents) == 1, "A Worker agent should have been created."
    worker_agent = worker_agents[0]

    # Assert PM state
    assert pm_agent.current_state == AgentState.BUILD_TEAM_TASKS, f"PM agent should be in BUILD_TEAM_TASKS state, but is in {pm_agent.current_state}"

    # 5. Now that we have the worker ID, set the next response for the PM
    mock_llm_manager.set_response("pm", "activate_workers", f"""
        <tool_requests>
            <calls>
                <tool_call>
                    <name>send_message</name>
                    <args>
                        <target_agent_id>{worker_agent.agent_id}</target_agent_id>
                        <message>Your task is to set up the server environment. Install nginx and python.</message>
                    </args>
                </tool_call>
            </calls>
        </tool_requests>
    """)
    # Manually transition PM to the next state to trigger task assignment
    await agent_manager.workflow_manager.change_agent_state(pm_agent, AgentState.ACTIVATE_WORKERS)
    await agent_manager.schedule_cycle(pm_agent.agent_id)

    # 6. Wait for the final part of the workflow to complete (PM assigns task -> Worker executes)
    await asyncio.sleep(2)

    # 7. Final Assertions
    # Verify the PM is now in MANAGE state
    assert pm_agent.current_state == AgentState.MANAGE, f"PM should be in MANAGE state, but is in {pm_agent.current_state}"

    # Verify the worker received the task assignment
    assert any("Your task is to set up the server environment" in m.content for m in worker_agent.message_history), \
        "Worker message history does not contain the task assignment."

    # Verify the worker executed the task
    assert any("Work complete" in m.content for m in worker_agent.message_history), \
        "Worker message history does not contain the work completion message."

    print("\n✅ Automated end-to-end agent workflow test passed!")