# START OF FILE core/ai/events.py
"""
HAI-Net Agent Event System
Constitutional compliance: All events logged with privacy protection
Event-driven architecture for real-time agent communication
"""

import time
from typing import Dict, List, Any, Callable, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger


class EventType(Enum):
    """Agent event types for real-time communication"""
    # Agent lifecycle events
    AGENT_THINKING = "agent_thinking"
    AGENT_STATE_CHANGE = "agent_state_change"
    
    # Response events
    RESPONSE_CHUNK = "response_chunk"
    RESPONSE_COMPLETE = "response_complete"
    
    # Tool events
    TOOL_EXECUTION_START = "tool_execution_start"
    TOOL_EXECUTION_COMPLETE = "tool_execution_complete"
    
    # Workflow events
    PLAN_CREATED = "plan_created"
    TASK_LIST_CREATED = "task_list_created"
    WORKER_CREATED = "worker_created"
    
    # Error events
    ERROR_OCCURRED = "error_occurred"
    
    # Constitutional events
    CONSTITUTIONAL_CHECK = "constitutional_check"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"


@dataclass
class AgentEvent:
    """Agent event with constitutional compliance tracking"""
    event_type: EventType
    agent_id: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    user_did: Optional[str] = None
    constitutional_compliant: bool = True
    privacy_protected: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "type": self.event_type.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "data": self.data,
            "user_did": self.user_did,
            "constitutional_compliant": self.constitutional_compliant,
            "privacy_protected": self.privacy_protected
        }
    
    def to_websocket_message(self) -> Dict[str, Any]:
        """Convert event to WebSocket message format"""
        return {
            "type": "agent_event",
            "event": self.event_type.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            **self.data
        }


class EventEmitter:
    """
    Event emitter for agent events with constitutional compliance
    Supports multiple subscribers and async event handling
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.events", settings)
        
        # Event subscribers by event type
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._global_subscribers: List[Callable] = []
        
        # Event history (for debugging and audit)
        self._event_history: List[AgentEvent] = []
        self._max_history = 1000
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        
        # Thread safety
        self._lock = asyncio.Lock()
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to specific event type
        
        Args:
            event_type: Event type to subscribe to
            callback: Async callback function(event: AgentEvent)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        self.logger.debug(f"Subscriber added for {event_type.value}", category="events", function="subscribe")
    
    def subscribe_all(self, callback: Callable):
        """
        Subscribe to all event types
        
        Args:
            callback: Async callback function(event: AgentEvent)
        """
        self._global_subscribers.append(callback)
        self.logger.debug("Global subscriber added", category="events", function="subscribe_all")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from event type"""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    async def emit(self, event: AgentEvent):
        """
        Emit an event to all subscribers
        
        Args:
            event: Agent event to emit
        """
        try:
            async with self._lock:
                # Add to history
                self._event_history.append(event)
                if len(self._event_history) > self._max_history:
                    self._event_history = self._event_history[-self._max_history:]
                
                # Log event for constitutional compliance
                self.logger.log_privacy_event(
                    f"event_{event.event_type.value}",
                    f"agent_{event.agent_id}",
                    user_consent=True
                )
            
            # Notify specific subscribers (don't hold lock during callbacks)
            if event.event_type in self._subscribers:
                for callback in self._subscribers[event.event_type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        self.logger.error(f"Subscriber callback error: {e}", category="events", function="emit")
            
            # Notify global subscribers
            for callback in self._global_subscribers:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self.logger.error(f"Global subscriber callback error: {e}", category="events", function="emit")
                    
        except Exception as e:
            self.logger.error(f"Event emission failed: {e}", category="events", function="emit")
    
    def get_event_history(self, agent_id: Optional[str] = None, 
                          event_type: Optional[EventType] = None,
                          limit: int = 100) -> List[AgentEvent]:
        """
        Get event history with optional filtering
        
        Args:
            agent_id: Filter by agent ID
            event_type: Filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self._event_history
        
        if agent_id:
            events = [e for e in events if e.agent_id == agent_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()


class ResponseCollector:
    """
    Collects response chunks and provides mechanisms to wait for complete responses
    Used for synchronous HTTP endpoints that need to wait for agent responses
    """
    
    def __init__(self):
        # Map of agent_id -> response data
        self._pending_responses: Dict[str, Dict[str, Any]] = {}
        self._response_futures: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
    
    async def start_response(self, agent_id: str, user_did: Optional[str] = None):
        """Start collecting response for an agent"""
        async with self._lock:
            self._pending_responses[agent_id] = {
                "chunks": [],
                "complete": False,
                "user_did": user_did,
                "started_at": time.time()
            }
            self._response_futures[agent_id] = asyncio.Future()
    
    async def add_chunk(self, agent_id: str, chunk: str):
        """Add a response chunk"""
        async with self._lock:
            if agent_id in self._pending_responses:
                self._pending_responses[agent_id]["chunks"].append(chunk)
    
    async def complete_response(self, agent_id: str, final_response: str):
        """Mark response as complete"""
        async with self._lock:
            if agent_id in self._pending_responses:
                self._pending_responses[agent_id]["complete"] = True
                self._pending_responses[agent_id]["final_response"] = final_response
                self._pending_responses[agent_id]["completed_at"] = time.time()
                
                # Set the future result
                if agent_id in self._response_futures and not self._response_futures[agent_id].done():
                    self._response_futures[agent_id].set_result(final_response)
    
    async def wait_for_response(self, agent_id: str, timeout: float = 30.0) -> Optional[str]:
        """
        Wait for agent response to complete
        
        Args:
            agent_id: Agent ID to wait for
            timeout: Timeout in seconds
            
        Returns:
            Final response or None if timeout
        """
        try:
            if agent_id not in self._response_futures:
                return None
            
            future = self._response_futures[agent_id]
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            return None
        finally:
            # Cleanup
            async with self._lock:
                if agent_id in self._pending_responses:
                    del self._pending_responses[agent_id]
                if agent_id in self._response_futures:
                    del self._response_futures[agent_id]
    
    async def cancel_response(self, agent_id: str):
        """Cancel waiting for a response"""
        async with self._lock:
            if agent_id in self._response_futures and not self._response_futures[agent_id].done():
                self._response_futures[agent_id].cancel()
            
            if agent_id in self._pending_responses:
                del self._pending_responses[agent_id]
            if agent_id in self._response_futures:
                del self._response_futures[agent_id]


def create_event_emitter(settings: HAINetSettings) -> EventEmitter:
    """
    Create constitutional event emitter
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured EventEmitter instance
    """
    return EventEmitter(settings)


if __name__ == "__main__":
    # Test the event system
    import asyncio
    from core.config.settings import HAINetSettings
    
    async def test_events():
        print("HAI-Net Event System Test")
        print("=" * 35)
        
        settings = HAINetSettings()
        emitter = create_event_emitter(settings)
        
        # Track received events
        received_events = []
        
        # Subscribe to events
        async def on_response_chunk(event: AgentEvent):
            received_events.append(event)
            print(f"📨 Response chunk: {event.data.get('chunk', '')}")
        
        async def on_any_event(event: AgentEvent):
            print(f"🔔 Event: {event.event_type.value}")
        
        emitter.subscribe(EventType.RESPONSE_CHUNK, on_response_chunk)
        emitter.subscribe_all(on_any_event)
        
        # Emit test events
        await emitter.emit(AgentEvent(
            event_type=EventType.AGENT_THINKING,
            agent_id="test_agent",
            timestamp=time.time(),
            data={"message": "Processing..."}
        ))
        
        await emitter.emit(AgentEvent(
            event_type=EventType.RESPONSE_CHUNK,
            agent_id="test_agent",
            timestamp=time.time(),
            data={"chunk": "Hello "}
        ))
        
        await emitter.emit(AgentEvent(
            event_type=EventType.RESPONSE_CHUNK,
            agent_id="test_agent",
            timestamp=time.time(),
            data={"chunk": "World!"}
        ))
        
        await emitter.emit(AgentEvent(
            event_type=EventType.RESPONSE_COMPLETE,
            agent_id="test_agent",
            timestamp=time.time(),
            data={"response": "Hello World!"}
        ))
        
        # Check history
        history = emitter.get_event_history(agent_id="test_agent")
        print(f"\n📚 Event history: {len(history)} events")
        print(f"✅ Received {len(received_events)} response chunks")
        
        # Test response collector
        print("\n--- Testing Response Collector ---")
        collector = ResponseCollector()
        
        # Start response
        await collector.start_response("test_agent")
        
        # Simulate async response completion
        async def complete_after_delay():
            await asyncio.sleep(0.5)
            await collector.add_chunk("test_agent", "Hello ")
            await asyncio.sleep(0.5)
            await collector.add_chunk("test_agent", "World!")
            await collector.complete_response("test_agent", "Hello World!")
        
        # Start completion task
        asyncio.create_task(complete_after_delay())
        
        # Wait for response
        response = await collector.wait_for_response("test_agent", timeout=5.0)
        print(f"✅ Collected response: {response}")
        
        print("\n🎉 Event System Working!")
    
    asyncio.run(test_events())
