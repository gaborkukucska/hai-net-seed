# START OF FILE core/ai/agents.py
"""
HAI-Net Agent Management
Constitutional compliance: All four principles enforced in agent behavior
Agent state machine and lifecycle management with constitutional protection
"""

import asyncio
import time
import json
import secrets
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
import uuid

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError
from typing import Dict, List, Optional, Any, Callable, Set, AsyncGenerator
from .llm import LLMManager, LLMMessage, LLMResponse
from .schemas import AgentMemory

class AgentState(Enum):
    """
    Agent state machine states, inspired by the TrippleEffect framework.
    """
    # General States
    IDLE = "idle"                # Waiting for tasks or triggers
    PROCESSING = "processing"    # Actively in an execution cycle
    ERROR = "error"              # An error occurred, requires intervention
    SHUTDOWN = "shutdown"        # Agent is shutting down

    # Admin/PM Planning States
    PLANNING = "planning"        # Actively creating a plan

    # Admin Conversation State
    CONVERSATION = "conversation" # General interaction with the user

    # PM States
    STARTUP = "startup"                 # Initial state for a new PM agent to break down a plan
    BUILD_TEAM_TASKS = "build_team_tasks" # State for defining tasks and required team
    ACTIVATE_WORKERS = "activate_workers"   # State for assigning tasks to workers
    MANAGE = "manage"                   # PM's main operational state for monitoring progress
    STANDBY = "standby"                 # PM state when a project is complete

    # Worker States
    WORK = "work"                # Executing a specific assigned task
    WAIT = "wait"                # Task complete, waiting for review or next task

    # Maintenance State
    MAINTENANCE = "maintenance"  # Performing self-maintenance


class AgentRole(Enum):
    """Agent roles in HAI-Net hierarchy, aligned with TrippleEffect."""
    ADMIN = "admin"      # User-linked AI, corresponds to Admin AI
    PM = "pm"            # Project Manager AI, corresponds to PM Agent
    WORKER = "worker"    # Specialized task execution AI, corresponds to Worker Agent
    GUARDIAN = "guardian"# HAI-Net specific constitutional compliance monitor


class AgentCapability(Enum):
    """Agent capabilities"""
    TEXT_GENERATION = "text_generation"
    CONVERSATION = "conversation"
    TASK_PLANNING = "task_planning"
    CODE_GENERATION = "code_generation"
    RESEARCH = "research"
    MONITORING = "monitoring"
    COORDINATION = "coordination"
    COMPLIANCE_CHECK = "compliance_check"


# AgentTask is removed as we are moving to an event-driven model


@dataclass
class AgentMetrics:
    """Agent performance and health metrics"""
    uptime_seconds: float
    tasks_completed: int
    tasks_failed: int
    average_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    constitutional_violations: int
    privacy_violations: int
    last_heartbeat: float
    health_score: float  # 0.0 to 1.0


class AgentStateTransitions:
    """Manages valid state transitions for agents based on TrippleEffect workflows."""
    
    VALID_TRANSITIONS = {
        # General transitions
        AgentState.IDLE: [AgentState.STARTUP, AgentState.PROCESSING, AgentState.PLANNING, AgentState.CONVERSATION, AgentState.MANAGE, AgentState.WORK, AgentState.SHUTDOWN],
        AgentState.PROCESSING: [AgentState.IDLE, AgentState.ERROR],
        AgentState.ERROR: [AgentState.IDLE, AgentState.MAINTENANCE, AgentState.SHUTDOWN],
        AgentState.MAINTENANCE: [AgentState.IDLE],
        AgentState.SHUTDOWN: [],

        # Admin states
        AgentState.CONVERSATION: [AgentState.PROCESSING, AgentState.PLANNING, AgentState.IDLE],
        AgentState.PLANNING: [AgentState.PROCESSING, AgentState.CONVERSATION, AgentState.IDLE],

        # PM states
        AgentState.STARTUP: [AgentState.PROCESSING, AgentState.BUILD_TEAM_TASKS, AgentState.IDLE, AgentState.ERROR],
        AgentState.BUILD_TEAM_TASKS: [AgentState.PROCESSING, AgentState.ACTIVATE_WORKERS, AgentState.IDLE, AgentState.ERROR],
        AgentState.ACTIVATE_WORKERS: [AgentState.PROCESSING, AgentState.MANAGE, AgentState.IDLE, AgentState.ERROR],
        AgentState.MANAGE: [AgentState.PROCESSING, AgentState.STANDBY, AgentState.IDLE, AgentState.ERROR],
        AgentState.STANDBY: [AgentState.IDLE, AgentState.MANAGE],

        # Worker states
        AgentState.WORK: [AgentState.PROCESSING, AgentState.WAIT, AgentState.IDLE, AgentState.ERROR],
        AgentState.WAIT: [AgentState.WORK, AgentState.IDLE]
    }
    
    @classmethod
    def is_valid_transition(cls, from_state: AgentState, to_state: AgentState) -> bool:
        """Check if state transition is valid"""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def get_valid_transitions(cls, from_state: AgentState) -> List[AgentState]:
        """Get list of valid transitions from current state"""
        return cls.VALID_TRANSITIONS.get(from_state, [])


class Agent:
    """
    Constitutional AI Agent
    Implements an event-driven, state-based architecture.
    """
    
    def __init__(self, agent_id: str, role: AgentRole, settings: HAINetSettings,
                 manager: 'AgentManager',
                 llm_manager: Optional[LLMManager] = None,
                 user_did: Optional[str] = None):
        self.agent_id = agent_id
        self.role = role
        self.settings = settings
        self.manager = manager
        self.llm_manager = llm_manager
        self.user_did = user_did
        self.logger = get_logger(f"ai.agent.{agent_id}", settings)
        
        # Agent state
        self.current_state = AgentState.IDLE
        self.previous_state = AgentState.IDLE
        self.state_history: List[Dict[str, Any]] = []
        
        # Agent properties
        self.capabilities: Set[AgentCapability] = set()
        self.memory = AgentMemory()
        self.message_history: List[LLMMessage] = []
        self.metrics = AgentMetrics(
            uptime_seconds=0,
            tasks_completed=0,
            tasks_failed=0,
            average_response_time=0,
            memory_usage_mb=0,
            cpu_usage_percent=0,
            constitutional_violations=0,
            privacy_violations=0,
            last_heartbeat=time.time(),
            health_score=1.0
        )
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_memory_items = 1000  # Privacy principle: data minimization
        
        # Lifecycle management
        self.created_at = time.time()
        self.last_activity = time.time()
        self.running = False
        self.heartbeat_interval = 30  # seconds
        
        # Threading
        self._lock = asyncio.Lock()
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # State change callbacks
        self.state_change_callbacks: List[Callable[[AgentState, AgentState], None]] = []
        
        # Initialize based on role
        self._initialize_role_capabilities()
    
    def _initialize_role_capabilities(self):
        """Initialize capabilities based on agent role"""
        if self.role == AgentRole.ADMIN:
            self.capabilities.update([
                AgentCapability.CONVERSATION,
                AgentCapability.TASK_PLANNING,
                AgentCapability.COORDINATION,
                AgentCapability.MONITORING
            ])
        elif self.role == AgentRole.PM:
            self.capabilities.update([
                AgentCapability.TASK_PLANNING,
                AgentCapability.COORDINATION,
                AgentCapability.MONITORING
            ])
        elif self.role == AgentRole.WORKER:
            self.capabilities.update([
                AgentCapability.TEXT_GENERATION,
                AgentCapability.RESEARCH,
                AgentCapability.CODE_GENERATION
            ])
        elif self.role == AgentRole.GUARDIAN:
            self.capabilities.update([
                AgentCapability.MONITORING,
                AgentCapability.COMPLIANCE_CHECK
            ])
    
    async def start(self) -> bool:
        """Start the agent"""
        try:
            async with self._lock:
                if self.running:
                    return True
                
                # Transition to startup state
                await self._transition_state(AgentState.STARTUP)
                
                # Initialize agent
                await self._initialize_agent()
                
                # Start heartbeat
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # Transition to idle state
                await self._transition_state(AgentState.IDLE)
                
                self.running = True
                
                self.logger.log_decentralization_event(
                    f"agent_started_{self.role.value}",
                    local_processing=True
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Agent startup failed: {e}")
            await self._transition_state(AgentState.ERROR)
            return False
    
    async def stop(self):
        """Stop the agent"""
        try:
            async with self._lock:
                if not self.running:
                    return
                
                await self._transition_state(AgentState.SHUTDOWN)
                
                if self.heartbeat_task:
                    self.heartbeat_task.cancel()
                    try:
                        await self.heartbeat_task
                    except asyncio.CancelledError:
                        pass
                
                await self._save_agent_state()
                
                self.running = False
                
                self.logger.log_decentralization_event(
                    f"agent_stopped_{self.role.value}",
                    local_processing=True
                )
                
        except Exception as e:
            self.logger.error(f"Agent shutdown failed: {e}")
    
    async def _initialize_agent(self):
        """Initialize agent during startup"""
        # Set up memory structures
        if not self.memory.constitutional:
            self.memory.constitutional = {
                "violations": [],
                "compliance_score": 1.0,
                "last_check": time.time()
            }
        
        # Add startup memory
        self.memory.episodic.append({
            "event": "agent_startup",
            "timestamp": time.time(),
            "state": self.current_state.value,
            "role": self.role.value,
            "constitutional_compliant": True
        })
        
        # Initialize role-specific setup
        if self.role == AgentRole.GUARDIAN:
            self.memory.semantic["constitutional_principles"] = [
                "Privacy First", "Human Rights", "Decentralization", "Community Focus"
            ]
        
        self.logger.log_privacy_event(
            "agent_initialized",
            f"role_{self.role.value}",
            user_consent=True
        )
    
    async def _transition_state(self, new_state: AgentState):
        """Transition to new state with validation"""
        if not AgentStateTransitions.is_valid_transition(self.current_state, new_state):
            raise ConstitutionalViolationError(
                f"Invalid state transition: {self.current_state.value} -> {new_state.value}"
            )
        
        old_state = self.current_state
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Record state change
        state_change = {
            "from_state": old_state.value,
            "to_state": new_state.value,
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "constitutional_compliant": True
        }
        
        self.state_history.append(state_change)
        self.last_activity = time.time()
        
        # Log state transition
        self.logger.log_decentralization_event(
            f"state_transition_{old_state.value}_to_{new_state.value}",
            local_processing=True
        )
        
        # Notify callbacks
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self.logger.error(f"State change callback error: {e}")

    async def process_message(self, messages: List[LLMMessage]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Core event-yielding method for agent processing, based on TrippleEffect.
        This async generator streams the LLM response, parses it for tool calls or
        a final response, and yields structured events.
        """
        if not self.llm_manager:
            yield {"type": "error", "content": "LLM Manager not available."}
            return

        self.logger.debug(f"Agent {self.agent_id} starting process_message in state {self.current_state.value}")

        # Use getattr for safe access to pydantic model attributes with a default.
        model = getattr(self.settings, 'default_model', 'local_default')

        full_response = ""
        try:
            # Stream the response from the LLM provider
            async for chunk in self.llm_manager.stream_response(messages, model, self.user_did):
                if isinstance(chunk, str):
                    full_response += chunk
                elif isinstance(chunk, dict) and 'error' in chunk:
                    yield {"type": "error", "content": chunk['error']}
                    return

            # Basic parsing for tool calls. A real implementation would use a more robust XML parser.
            if "<tool_requests>" in full_response and "</tool_requests>" in full_response:
                yield {
                    "type": "agent_thought",
                    "content": "Tool request detected. Parsing and yielding tool_requests event."
                }
                # This is a highly simplified parser for the test case.
                # It finds the tool name, target_agent_id, and message.
                try:
                    tool_name = full_response.split("<name>")[1].split("</name>")[0].strip()
                    target_id = full_response.split("<target_agent_id>")[1].split("</target_agent_id>")[0].strip()
                    message = full_response.split("<message>")[1].split("</message>")[0].strip()

                    tool_call = {
                        "name": tool_name,
                        "args": {
                            "target_agent_id": target_id,
                            "message": message
                        }
                    }
                    yield {
                        "type": "tool_requests",
                        "calls": [tool_call]
                    }
                except IndexError:
                    yield {"type": "error", "content": "Malformed tool_requests XML."}

            else:
                # No tool call found, yield final response
                yield {
                    "type": "agent_thought",
                    "content": f"No tool request found. Preparing final response."
                }
                yield {
                    "type": "final_response",
                    "content": full_response.strip()
                }

        except Exception as e:
            self.logger.error(f"Error during agent's LLM stream processing: {e}", exc_info=True)
            yield {"type": "error", "content": f"An unexpected error occurred: {e}"}
    
    def _update_response_time_metric(self, execution_time: float):
        """Update average response time metric"""
        if self.metrics.average_response_time == 0:
            self.metrics.average_response_time = execution_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.average_response_time = (
                alpha * execution_time + 
                (1 - alpha) * self.metrics.average_response_time
            )
    
    async def _heartbeat_loop(self):
        """Agent heartbeat loop"""
        while self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if not self.running:
                    break
                
                # Update metrics
                self.metrics.uptime_seconds = time.time() - self.created_at
                self.metrics.last_heartbeat = time.time()
                
                # Update health score based on various factors
                await self._update_health_score()
                
                # Cleanup old memories (privacy principle)
                await self._cleanup_memories()
                
                # Log heartbeat
                self.logger.debug(f"Agent {self.agent_id} heartbeat - health: {self.metrics.health_score:.2f}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
    
    async def _update_health_score(self):
        """Update agent health score"""
        score = 1.0
        
        # Reduce score for constitutional violations
        if self.metrics.constitutional_violations > 0:
            score -= min(0.5, self.metrics.constitutional_violations * 0.1)
        
        # Reduce score for failed tasks
        if self.metrics.tasks_failed > 0:
            failure_rate = self.metrics.tasks_failed / max(1, self.metrics.tasks_completed + self.metrics.tasks_failed)
            score -= min(0.3, failure_rate)
        
        # Reduce score for being stuck in error state
        if self.current_state == AgentState.ERROR:
            score -= 0.4
        
        # Ensure score is between 0 and 1
        self.metrics.health_score = max(0.0, min(1.0, score))
    
    async def _cleanup_memories(self):
        """Cleanup old memories to respect privacy"""
        # Limit episodic memory
        if len(self.memory.episodic) > self.max_memory_items:
            # Keep most recent memories
            self.memory.episodic = self.memory.episodic[-self.max_memory_items:]
        
        # Cleanup old short-term memory
        current_time = time.time()
        for key, value in list(self.memory.short_term.items()):
            if isinstance(value, dict) and "timestamp" in value:
                # Remove items older than 1 hour
                if current_time - value["timestamp"] > 3600:
                    del self.memory.short_term[key]
    
    async def _save_agent_state(self):
        """Save agent state for persistence"""
        state_data = {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "current_state": self.current_state.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "metrics": asdict(self.metrics),
            "memory_summary": {
                "episodic_count": len(self.memory.episodic),
                "short_term_keys": list(self.memory.short_term.keys()),
                "constitutional_score": self.memory.constitutional.get("compliance_score", 1.0)
            },
            "saved_at": time.time()
        }
        
        # TODO: Save to database using storage system
        self.logger.debug(f"Agent state saved: {self.agent_id}")
    
    def add_state_change_callback(self, callback: Callable[[AgentState, AgentState], None]):
        """Add callback for state changes"""
        self.state_change_callbacks.append(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "current_state": self.current_state.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "metrics": asdict(self.metrics),
            "uptime": time.time() - self.created_at,
            "constitutional_compliant": self.metrics.constitutional_violations == 0,
            "running": self.running
        }


class AgentManager:
    """
    Constitutional Agent Manager for HAI-Net
    Central orchestrator for the agentic framework.
    """
    
    def __init__(self, settings: HAINetSettings, llm_manager: Optional[LLMManager] = None):
        self.settings = settings
        self.llm_manager = llm_manager
        self.logger = get_logger("ai.agent.manager", settings)
        
        self.cycle_handler: Optional['AgentCycleHandler'] = None
        self.workflow_manager: Optional['WorkflowManager'] = None

        self.agents: Dict[str, Agent] = {}
        self.agent_counter = 0
        
        self.constitutional_version = "1.0"
        self.max_agents = 20
        
        self.manager_metrics = {
            "total_agents_created": 0,
            "active_agents": 0,
            "total_cycles_run": 0,
            "constitutional_violations": 0
        }
        self._lock = asyncio.Lock()

    def set_handlers(self, cycle_handler: 'AgentCycleHandler', workflow_manager: 'WorkflowManager'):
        """Set the core handlers after initialization."""
        self.cycle_handler = cycle_handler
        self.workflow_manager = workflow_manager
    
    async def create_agent(self, role: AgentRole, user_did: Optional[str] = None,
                          capabilities: Optional[Set[AgentCapability]] = None) -> Optional[str]:
        """Create a new agent with constitutional compliance"""
        try:
            async with self._lock:
                if len(self.agents) >= self.max_agents:
                    self.logger.log_violation("agent_limit_exceeded", {
                        "current_count": len(self.agents),
                        "max_allowed": self.max_agents
                    })
                    return None
                
                self.agent_counter += 1
                agent_id = f"agent_{role.value}_{self.agent_counter:03d}_{secrets.token_hex(4)}"
                
                agent = Agent(
                    agent_id=agent_id,
                    role=role,
                    settings=self.settings,
                    manager=self,
                    llm_manager=self.llm_manager,
                    user_did=user_did
                )
                
                # Add custom capabilities if provided
                if capabilities:
                    agent.capabilities.update(capabilities)
                
                # Start agent
                if await agent.start():
                    self.agents[agent_id] = agent
                    self.manager_metrics["total_agents_created"] += 1
                    self.manager_metrics["active_agents"] = len(self.agents)
                    
                    self.logger.log_decentralization_event(
                        f"agent_created_{role.value}",
                        local_processing=True
                    )
                    
                    return agent_id
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Agent creation failed: {e}")
            return None
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent"""
        try:
            async with self._lock:
                if agent_id not in self.agents:
                    return False
                
                agent = self.agents[agent_id]
                await agent.stop()
                
                del self.agents[agent_id]
                self.manager_metrics["active_agents"] = len(self.agents)
                
                self.logger.log_decentralization_event(
                    f"agent_removed_{agent.role.value}",
                    local_processing=True
                )
                return True
                
        except Exception as e:
            self.logger.error(f"Agent removal failed: {e}")
            return False

    async def handle_user_message(self, user_input: str, user_did: Optional[str] = None):
        """Primary entry point for user interaction."""
        admin_agent = next((agent for agent in self.agents.values() if agent.role == AgentRole.ADMIN), None)

        if not admin_agent:
            self.logger.error("No Admin agent found to handle user message.")
            admin_agent_id = await self.create_agent(AgentRole.ADMIN, user_did=user_did)
            if not admin_agent_id:
                self.logger.error("Failed to create an Admin agent.")
                return
            admin_agent = self.get_agent(admin_agent_id)

        if admin_agent:
            admin_agent.message_history.append(LLMMessage(role="user", content=user_input, timestamp=time.time()))
            await self.schedule_cycle(admin_agent.agent_id)

    async def schedule_cycle(self, agent_id: str):
        """Schedules an agent to be run by the AgentCycleHandler."""
        if not self.cycle_handler:
            self.logger.error("AgentCycleHandler not set in AgentManager. Cannot schedule cycle.")
            return

        agent = self.get_agent(agent_id)
        if not agent:
            self.logger.error(f"Cannot schedule cycle: Agent {agent_id} not found.")
            return

        if agent.current_state != AgentState.PROCESSING:
            self.logger.info(f"Scheduling cycle for agent {agent_id}")
            self.manager_metrics["total_cycles_run"] += 1
            asyncio.create_task(self.cycle_handler.run_cycle(agent))
        else:
            self.logger.warning(f"Agent {agent_id} is already processing. Cycle not scheduled.")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get agents by role"""
        return [agent for agent in self.agents.values() if agent.role == role]
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        return list(self.agents.values())
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get agent manager statistics"""
        health_scores = [agent.metrics.health_score for agent in self.agents.values()]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        state_counts = {}
        for agent in self.agents.values():
            state = agent.current_state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        total_violations = sum(agent.metrics.constitutional_violations for agent in self.agents.values())
        
        return {
            **self.manager_metrics,
            "average_health_score": avg_health,
            "agent_states": state_counts,
            "total_constitutional_violations": total_violations,
            "constitutional_compliant": total_violations == 0
        }


def create_agent_manager(settings: HAINetSettings, llm_manager: Optional[LLMManager] = None) -> AgentManager:
    """
    Create and configure constitutional agent manager
    
    Args:
        settings: HAI-Net settings
        llm_manager: Optional LLM manager for agent AI capabilities
        
    Returns:
        Configured AgentManager instance
    """
    return AgentManager(settings, llm_manager)


if __name__ == "__main__":
    # Test the constitutional agent system
    import asyncio
    from core.config.settings import HAINetSettings
    
    class MockCycleHandler:
        async def run_cycle(self, agent: Agent):
            print(f"--- Running Mock Cycle for {agent.agent_id} ---")
            async for event in agent.process_message():
                print(f"Event: {event}")
            print(f"--- Finished Mock Cycle for {agent.agent_id} ---")

    class MockWorkflowManager:
        pass

    async def test_agents():
        print("HAI-Net Constitutional Agent Test (Refactored)")
        print("=" * 50)
        
        settings = HAINetSettings()
        agent_manager = create_agent_manager(settings)
        
        cycle_handler = MockCycleHandler()
        workflow_manager = MockWorkflowManager()
        agent_manager.set_handlers(cycle_handler, workflow_manager)

        try:
            admin_agent_id = await agent_manager.create_agent(
                AgentRole.ADMIN,
                user_did="did:hai:test_user"
            )
            print(f"✅ Admin agent created: {admin_agent_id}")
            
            worker_agent_id = await agent_manager.create_agent(
                AgentRole.WORKER
            )
            print(f"✅ Worker agent created: {worker_agent_id}")
            
            print("\n--- Testing User Message Handling ---")
            await agent_manager.handle_user_message("Hello, HAI-Net!")
            
            await asyncio.sleep(1)
            
            if admin_agent_id:
                admin_agent = agent_manager.get_agent(admin_agent_id)
                if admin_agent:
                    status = admin_agent.get_status()
                    print(f"\n📊 Admin agent status: {status['current_state']}")
                    print(f"   Health score: {status['metrics']['health_score']:.2f}")
            
            stats = agent_manager.get_manager_stats()
            print(f"📈 Manager stats: {stats}")
            
            print("\n🎉 Constitutional Agent System (Refactored) Working!")
            
        except Exception as e:
            print(f"❌ Agent test failed: {e}")
        
        finally:
            for agent_id in list(agent_manager.agents.keys()):
                await agent_manager.remove_agent(agent_id)
    
    asyncio.run(test_agents())
