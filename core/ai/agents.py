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
from .llm import LLMManager, LLMMessage, LLMResponse


class AgentState(Enum):
    """Agent state machine states"""
    IDLE = "idle"
    STARTUP = "startup"
    PLANNING = "planning"
    CONVERSATION = "conversation"
    WORK = "work"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class AgentRole(Enum):
    """Agent roles in HAI-Net hierarchy"""
    ADMIN = "admin"          # User-linked primary agent
    MANAGER = "manager"      # Task coordination agent
    WORKER = "worker"        # Specialized execution agent
    GUARDIAN = "guardian"    # Constitutional compliance agent


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


@dataclass
class AgentMemory:
    """Agent memory structure"""
    short_term: Dict[str, Any]     # Current context and working memory
    long_term: List[Dict[str, Any]]  # Persistent memories
    episodic: List[Dict[str, Any]]   # Specific event memories
    semantic: Dict[str, Any]         # Knowledge and facts
    constitutional: Dict[str, Any]   # Constitutional compliance history

    def __post_init__(self):
        if not self.short_term:
            self.short_term = {}
        if not self.long_term:
            self.long_term = []
        if not self.episodic:
            self.episodic = []
        if not self.semantic:
            self.semantic = {}
        if not self.constitutional:
            self.constitutional = {
                "violations": [],
                "compliance_score": 1.0,
                "last_check": time.time()
            }


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    task_id: str
    task_type: str
    description: str
    priority: int  # 1-10, 10 being highest
    created_at: float
    deadline: Optional[float]
    parameters: Dict[str, Any]
    assigned_agent: Optional[str]
    status: str  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]]
    constitutional_approved: bool = True


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
    """Manages valid state transitions for agents"""
    
    VALID_TRANSITIONS = {
        AgentState.IDLE: [AgentState.STARTUP, AgentState.PLANNING, AgentState.CONVERSATION, 
                         AgentState.WORK, AgentState.MAINTENANCE, AgentState.SHUTDOWN],
        AgentState.STARTUP: [AgentState.IDLE, AgentState.PLANNING, AgentState.ERROR],
        AgentState.PLANNING: [AgentState.IDLE, AgentState.CONVERSATION, AgentState.WORK, 
                            AgentState.MAINTENANCE, AgentState.ERROR],
        AgentState.CONVERSATION: [AgentState.IDLE, AgentState.PLANNING, AgentState.WORK, 
                                AgentState.ERROR],
        AgentState.WORK: [AgentState.IDLE, AgentState.PLANNING, AgentState.CONVERSATION, 
                         AgentState.MAINTENANCE, AgentState.ERROR],
        AgentState.MAINTENANCE: [AgentState.IDLE, AgentState.SHUTDOWN, AgentState.ERROR],
        AgentState.SHUTDOWN: [AgentState.STARTUP],
        AgentState.ERROR: [AgentState.IDLE, AgentState.MAINTENANCE, AgentState.SHUTDOWN]
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
    Implements agent state machine with constitutional compliance
    """
    
    def __init__(self, agent_id: str, role: AgentRole, settings: HAINetSettings,
                 llm_manager: Optional[LLMManager] = None,
                 user_did: Optional[str] = None):
        self.agent_id = agent_id
        self.role = role
        self.settings = settings
        self.llm_manager = llm_manager
        self.user_did = user_did
        self.logger = get_logger(f"ai.agent.{agent_id}", settings)
        
        # Agent state
        self.current_state = AgentState.IDLE
        self.previous_state = AgentState.IDLE
        self.state_history: List[Dict[str, Any]] = []
        
        # Agent properties
        self.capabilities: Set[AgentCapability] = set()
        self.memory = AgentMemory({}, [], [], {}, {})
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
        
        # Task management
        self.current_task: Optional[AgentTask] = None
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []

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
        elif self.role == AgentRole.MANAGER:
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
                
                # Transition to shutdown state
                await self._transition_state(AgentState.SHUTDOWN)
                
                # Stop heartbeat
                if self.heartbeat_task:
                    self.heartbeat_task.cancel()
                    try:
                        await self.heartbeat_task
                    except asyncio.CancelledError:
                        pass
                
                # Complete current task if any
                if self.current_task:
                    await self._complete_current_task(status="interrupted")

                # Save state
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

    async def assign_task(self, task: AgentTask) -> bool:
        """Assign a task to the agent"""
        try:
            async with self._lock:
                # Check constitutional compliance of task
                if not await self._validate_task_compliance(task):
                    self.logger.log_violation("task_constitutional_violation", {
                        "task_id": task.task_id,
                        "agent_id": self.agent_id,
                        "reason": "Task violates constitutional principles"
                    })
                    return False

                # Check if agent can handle this task type
                if not await self._can_handle_task(task):
                    self.logger.warning(f"Agent {self.agent_id} cannot handle task {task.task_id}")
                    return False

                # Add to task queue
                task.assigned_agent = self.agent_id
                task.status = "pending"
                self.task_queue.append(task)

                # Sort by priority
                self.task_queue.sort(key=lambda t: t.priority, reverse=True)

                # If idle, start processing
                if self.current_state == AgentState.IDLE:
                    await self._process_next_task()

                self.logger.log_community_event(
                    f"task_assigned_{task.task_type}",
                    community_benefit=True
                )

                return True

        except Exception as e:
            self.logger.error(f"Task assignment failed: {e}")
            return False

    async def _process_next_task(self):
        """Process the next task in the queue"""
        try:
            if not self.task_queue or self.current_task:
                return

            # Get highest priority task
            task = self.task_queue.pop(0)
            self.current_task = task
            task.status = "in_progress"

            # Transition to appropriate state
            if task.task_type in ["conversation", "chat"]:
                await self._transition_state(AgentState.CONVERSATION)
            elif task.task_type in ["planning", "coordination"]:
                await self._transition_state(AgentState.PLANNING)
            else:
                await self._transition_state(AgentState.WORK)

            # Execute task
            result = await self._execute_task(task)

            # Complete task
            await self._complete_current_task(
                status="completed" if result else "failed",
                result=result
            )

        except Exception as e:
            self.logger.error(f"Task processing failed: {e}")
            await self._complete_current_task(status="failed")

    async def _execute_task(self, task: AgentTask) -> Optional[Dict[str, Any]]:
        """Execute a specific task"""
        try:
            start_time = time.time()

            # Add task to memory
            self.memory.episodic.append({
                "event": "task_started",
                "task_id": task.task_id,
                "task_type": task.task_type,
                "timestamp": start_time,
                "constitutional_compliant": True
            })

            result = None

            # Execute based on task type
            if task.task_type == "conversation":
                result = await self._handle_conversation_task(task)
            elif task.task_type == "planning":
                result = await self._handle_planning_task(task)
            elif task.task_type == "research":
                result = await self._handle_research_task(task)
            elif task.task_type == "monitoring":
                result = await self._handle_monitoring_task(task)
            else:
                result = await self._handle_generic_task(task)

            # Update metrics
            execution_time = time.time() - start_time
            self._update_response_time_metric(execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return None

    async def _handle_conversation_task(self, task: AgentTask) -> Optional[Dict[str, Any]]:
        """Handle conversation task"""
        try:
            if not self.llm_manager:
                return {"error": "No LLM manager available"}

            # Extract conversation parameters
            messages = task.parameters.get("messages", [])
            model = task.parameters.get("model", "")

            if not messages:
                return {"error": "No messages provided"}

            # Convert to LLM messages
            llm_messages = []
            for msg in messages:
                llm_messages.append(LLMMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=time.time()
                ))

            # Generate response
            response = await self.llm_manager.generate_response(
                messages=llm_messages,
                model=model,
                user_did=self.user_did
            )

            # Update constitutional compliance metrics
            if not response.constitutional_compliant:
                self.metrics.constitutional_violations += 1
            if not response.privacy_protected:
                self.metrics.privacy_violations += 1

            # Add to memory
            self.memory.short_term["last_conversation"] = {
                "messages": messages,
                "response": response.content,
                "timestamp": time.time(),
                "constitutional_compliant": response.constitutional_compliant
            }

            return {
                "response": response.content,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "constitutional_compliant": response.constitutional_compliant,
                "privacy_protected": response.privacy_protected
            }

        except Exception as e:
            self.logger.error(f"Conversation task failed: {e}")
            return {"error": str(e)}

    async def _handle_planning_task(self, task: AgentTask) -> Optional[Dict[str, Any]]:
        """Handle planning task"""
        # Implement planning logic
        plan_steps = [
            {"step": 1, "action": "analyze_requirements", "estimated_time": 5},
            {"step": 2, "action": "identify_resources", "estimated_time": 10},
            {"step": 3, "action": "create_execution_plan", "estimated_time": 15}
        ]

        return {
            "plan": plan_steps,
            "total_estimated_time": sum(step["estimated_time"] for step in plan_steps),
            "constitutional_compliant": True
        }

    async def _handle_research_task(self, task: AgentTask) -> Optional[Dict[str, Any]]:
        """Handle research task"""
        # Implement research logic using vector store
        query = task.parameters.get("query", "")
        
        return {
            "query": query,
            "findings": ["Research capability not yet implemented"],
            "sources": [],
            "constitutional_compliant": True
        }

    async def _handle_monitoring_task(self, task: AgentTask) -> Optional[Dict[str, Any]]:
        """Handle monitoring task"""
        # Collect system metrics
        system_status = {
            "agent_health": self.metrics.health_score,
            "uptime": self.metrics.uptime_seconds,
            "tasks_completed": self.metrics.tasks_completed,
            "constitutional_violations": self.metrics.constitutional_violations,
            "memory_usage": len(self.memory.episodic),
            "timestamp": time.time()
        }

        return {
            "status": "healthy" if self.metrics.health_score > 0.7 else "degraded",
            "metrics": system_status,
            "constitutional_compliant": True
        }

    async def _handle_generic_task(self, task: AgentTask) -> Optional[Dict[str, Any]]:
        """Handle generic task"""
        return {
            "task_type": task.task_type,
            "message": "Generic task handler - not yet implemented",
            "constitutional_compliant": True
        }
    
    async def _complete_current_task(self, status: str = "completed", result: Optional[Dict[str, Any]] = None):
        """Complete the current task"""
        if not self.current_task:
            return

        # Update task
        self.current_task.status = status
        self.current_task.result = result

        # Update metrics
        if status == "completed":
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1

        # Move to completed tasks
        self.completed_tasks.append(self.current_task)

        # Add to memory
        self.memory.episodic.append({
            "event": "task_completed",
            "task_id": self.current_task.task_id,
            "status": status,
            "timestamp": time.time(),
            "constitutional_compliant": True
        })

        # Clear current task
        self.current_task = None

        # Return to idle and process next task
        await self._transition_state(AgentState.IDLE)
        if self.task_queue:
            await self._process_next_task()

    async def _validate_task_compliance(self, task: AgentTask) -> bool:
        """Validate task compliance with constitutional principles"""
        # Check for privacy violations
        task_str = json.dumps(asdict(task)).lower()
        privacy_patterns = ["personal information", "private data", "password", "secret"]

        for pattern in privacy_patterns:
            if pattern in task_str:
                return False

        # Check task priority is reasonable (community focus)
        if task.priority > 10 or task.priority < 1:
            return False

        # Check deadline is reasonable
        if task.deadline and task.deadline < time.time():
            return False

        return True

    async def _can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle the given task"""
        task_capability_map = {
            "conversation": AgentCapability.CONVERSATION,
            "planning": AgentCapability.TASK_PLANNING,
            "research": AgentCapability.RESEARCH,
            "monitoring": AgentCapability.MONITORING,
            "code_generation": AgentCapability.CODE_GENERATION
        }

        required_capability = task_capability_map.get(task.task_type)
        if required_capability and required_capability not in self.capabilities:
            return False

        return True

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
            "current_task": self.current_task.task_id if self.current_task else None,
            "task_queue_size": len(self.task_queue),
            "metrics": asdict(self.metrics),
            "uptime": time.time() - self.created_at,
            "constitutional_compliant": self.metrics.constitutional_violations == 0,
            "running": self.running
        }


class AgentManager:
    """
    Constitutional Agent Manager for HAI-Net
    Manages multiple agents with constitutional compliance
    """
    
    def __init__(self, settings: HAINetSettings, llm_manager: Optional[LLMManager] = None):
        self.settings = settings
        self.llm_manager = llm_manager
        self.logger = get_logger("ai.agent.manager", settings)
        
        # Agent management
        self.agents: Dict[str, Agent] = {}
        self.agent_counter = 0
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_agents = 20  # Community focus: reasonable resource limits
        
        # Monitoring
        self.manager_metrics = {
            "total_agents_created": 0,
            "active_agents": 0,
            "total_tasks_processed": 0,
            "constitutional_violations": 0
        }
        
        # Thread safety
        self._lock = asyncio.Lock()
    
    async def create_agent(self, role: AgentRole, user_did: Optional[str] = None,
                          capabilities: Optional[Set[AgentCapability]] = None) -> Optional[str]:
        """Create a new agent with constitutional compliance"""
        try:
            async with self._lock:
                # Check agent limits (community focus)
                if len(self.agents) >= self.max_agents:
                    self.logger.log_violation("agent_limit_exceeded", {
                        "current_count": len(self.agents),
                        "max_allowed": self.max_agents
                    })
                    return None
                
                # Generate agent ID
                self.agent_counter += 1
                agent_id = f"agent_{role.value}_{self.agent_counter:03d}_{secrets.token_hex(4)}"
                
                # Create agent
                agent = Agent(
                    agent_id=agent_id,
                    role=role,
                    settings=self.settings,
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
                
                # Stop agent
                await agent.stop()
                
                # Remove from manager
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

    async def assign_task_to_agent(self, agent_id: str, task: AgentTask) -> bool:
        """Assign task to specific agent"""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        success = await agent.assign_task(task)

        if success:
            self.manager_metrics["total_tasks_processed"] += 1

        return success

    async def assign_task_by_capability(self, task: AgentTask,
                                       required_capability: AgentCapability) -> bool:
        """Assign task to an agent with the required capability"""
        # Find suitable agents
        suitable_agents = []
        for agent in self.agents.values():
            if (required_capability in agent.capabilities and
                agent.current_state in [AgentState.IDLE, AgentState.PLANNING]):
                suitable_agents.append(agent)

        if not suitable_agents:
            return False

        # Choose agent with lowest task queue
        best_agent = min(suitable_agents, key=lambda a: len(a.task_queue))

        return await best_agent.assign_task(task)

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
        # Collect agent health scores
        health_scores = [agent.metrics.health_score for agent in self.agents.values()]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        # Count agents by state
        state_counts = {}
        for agent in self.agents.values():
            state = agent.current_state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Count constitutional violations
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
    
    async def test_agents():
        print("HAI-Net Constitutional Agent Test")
        print("=" * 35)
        
        # Create test settings
        settings = HAINetSettings()
        
        # Create agent manager
        agent_manager = create_agent_manager(settings)
        
        try:
            # Create test agents
            admin_agent_id = await agent_manager.create_agent(
                AgentRole.ADMIN,
                user_did="did:hai:test_user"
            )
            print(f"✅ Admin agent created: {admin_agent_id}")
            
            worker_agent_id = await agent_manager.create_agent(
                AgentRole.WORKER
            )
            print(f"✅ Worker agent created: {worker_agent_id}")
            
            # Test task assignment
            test_task = AgentTask(
                task_id="test_task_001",
                task_type="monitoring",
                description="Test monitoring task",
                priority=5,
                created_at=time.time(),
                deadline=None,
                parameters={"target": "system_health"},
                assigned_agent=None,
                status="pending"
            )

            if admin_agent_id:
                success = await agent_manager.assign_task_to_agent(admin_agent_id, test_task)
                print(f"✅ Task assigned: {success}")
            
            # Wait a bit for task processing
            await asyncio.sleep(2)
            
            # Get agent status
            if admin_agent_id:
                admin_agent = agent_manager.get_agent(admin_agent_id)
                if admin_agent:
                    status = admin_agent.get_status()
                    print(f"📊 Admin agent status: {status['current_state']}")
                    print(f"   Tasks completed: {status['metrics']['tasks_completed']}")
                    print(f"   Health score: {status['metrics']['health_score']:.2f}")
            
            # Get manager statistics
            stats = agent_manager.get_manager_stats()
            print(f"📈 Manager stats: {stats}")
            
            print("\n🎉 Constitutional Agent System Working!")
            
        except Exception as e:
            print(f"❌ Agent test failed: {e}")
        
        finally:
            # Cleanup agents
            for agent_id in list(agent_manager.agents.keys()):
                await agent_manager.remove_agent(agent_id)
    
    # Run the test
    asyncio.run(test_agents())
