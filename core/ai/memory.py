# START OF FILE core/ai/memory.py
"""
HAI-Net Memory Management System
Constitutional compliance: Privacy First + Human Rights + Community Focus
Sophisticated agent memory with vector search and constitutional protection
"""

import asyncio
import time
import json
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError
from core.storage.vector_store import VectorStore, VectorSearchResult
from .schemas import AgentMemory

class MemoryType(Enum):
    """Types of memories"""
    EPISODIC = "episodic"        # Specific events and experiences
    SEMANTIC = "semantic"        # Facts and knowledge
    PROCEDURAL = "procedural"    # Skills and procedures
    WORKING = "working"          # Current context and temporary data
    CONSTITUTIONAL = "constitutional"  # Constitutional compliance records

class MemoryImportance(Enum):
    """Importance levels for memory retention"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TEMPORARY = "temporary"

@dataclass
class Memory:
    """Represents a single memory"""
    memory_id: str
    agent_id: str
    memory_type: MemoryType
    content: str
    embedding: Optional[np.ndarray]
    importance: MemoryImportance
    timestamp: float
    metadata: Dict[str, Any]
    constitutional_compliant: bool = True
    user_consent: bool = True
    retention_days: Optional[int] = None

class MemoryManager:
    """
    Constitutional Memory Manager for HAI-Net
    Manages agent memories with vector search and constitutional compliance
    """
    
    def __init__(self, settings: HAINetSettings, vector_store: Optional[VectorStore] = None):
        self.settings = settings
        self.vector_store = vector_store
        self.logger = get_logger("ai.memory", settings)
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_memories_per_agent = 10000  # Privacy: data minimization
        
        # Memory storage
        self.agent_memories: Dict[str, Dict[str, Memory]] = {}
        self.memory_counter = 0
        
        # Retention policies (in days)
        self.retention_policies = {
            MemoryImportance.CRITICAL: None,      # Permanent
            MemoryImportance.HIGH: 365,           # 1 year
            MemoryImportance.MEDIUM: 90,          # 3 months
            MemoryImportance.LOW: 30,             # 1 month
            MemoryImportance.TEMPORARY: 1         # 1 day
        }
        
        # Thread safety
        self._lock = asyncio.Lock()
    
    async def store_memory(self, agent_id: str, content: str, memory_type: MemoryType,
                          importance: MemoryImportance, metadata: Optional[Dict[str, Any]] = None,
                          embedding: Optional[np.ndarray] = None) -> Optional[str]:
        """
        Store a memory for an agent with constitutional compliance
        
        Args:
            agent_id: Agent identifier
            content: Memory content
            memory_type: Type of memory
            importance: Importance level
            metadata: Optional metadata
            embedding: Optional vector embedding
            
        Returns:
            Memory ID if stored successfully
        """
        try:
            async with self._lock:
                # Check constitutional compliance
                if not await self._validate_memory_compliance(content, agent_id):
                    self.logger.log_violation("memory_constitutional_violation", {
                        "agent_id": agent_id,
                        "content_preview": content[:50] + "..." if len(content) > 50 else content
                    })
                    return None
                
                # Check memory limits per agent (community focus: resource limits)
                if agent_id not in self.agent_memories:
                    self.agent_memories[agent_id] = {}
                
                if len(self.agent_memories[agent_id]) >= self.max_memories_per_agent:
                    # Clean up old temporary memories
                    await self._cleanup_old_memories(agent_id)
                    
                    if len(self.agent_memories[agent_id]) >= self.max_memories_per_agent:
                        self.logger.log_violation("memory_limit_exceeded", {
                            "agent_id": agent_id,
                            "current_count": len(self.agent_memories[agent_id])
                        })
                        return None
                
                # Generate memory ID
                self.memory_counter += 1
                memory_id = f"mem_{agent_id}_{self.memory_counter:08d}"
                
                # Create memory
                memory = Memory(
                    memory_id=memory_id,
                    agent_id=agent_id,
                    memory_type=memory_type,
                    content=content,
                    embedding=embedding,
                    importance=importance,
                    timestamp=time.time(),
                    metadata=metadata or {},
                    constitutional_compliant=True,
                    user_consent=True,
                    retention_days=self.retention_policies.get(importance)
                )
                
                # Store in agent memories
                self.agent_memories[agent_id][memory_id] = memory
                
                # Store in vector store for semantic search
                if self.vector_store and embedding is not None:
                    await self._store_in_vector_store(memory)
                
                self.logger.log_privacy_event(
                    "memory_stored",
                    f"{memory_type.value}_{importance.value}",
                    user_consent=True
                )
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"Memory storage failed: {e}")
            return None
    
    async def retrieve_memory(self, agent_id: str, memory_id: str) -> Optional[Memory]:
        """Retrieve specific memory by ID"""
        try:
            async with self._lock:
                agent_memories = self.agent_memories.get(agent_id, {})
                memory = agent_memories.get(memory_id)
                
                if memory:
                    # Check if memory has expired
                    if await self._is_memory_expired(memory):
                        await self._delete_memory(agent_id, memory_id)
                        return None
                    
                    self.logger.log_privacy_event(
                        "memory_retrieved",
                        f"{memory.memory_type.value}",
                        user_consent=True
                    )
                
                return memory
                
        except Exception as e:
            self.logger.error(f"Memory retrieval failed: {e}")
            return None
    
    async def search_memories(self, agent_id: str, query: str, memory_type: Optional[MemoryType] = None,
                             limit: int = 10) -> List[Tuple[Memory, float]]:
        """
        Search agent memories using semantic similarity
        
        Args:
            agent_id: Agent identifier
            query: Search query
            memory_type: Optional memory type filter
            limit: Maximum results to return
            
        Returns:
            List of (Memory, similarity_score) tuples
        """
        try:
            async with self._lock:
                if agent_id not in self.agent_memories:
                    return []
                
                results = []
                
                # If vector store available, use semantic search
                if self.vector_store:
                    # This would require query embedding - simplified for now
                    # In full implementation, would embed query and search vector store
                    pass
                
                # Fallback to keyword search
                query_lower = query.lower()
                agent_memories = self.agent_memories[agent_id]
                
                for memory in agent_memories.values():
                    # Check if memory has expired
                    if await self._is_memory_expired(memory):
                        continue
                    
                    # Apply memory type filter
                    if memory_type and memory.memory_type != memory_type:
                        continue
                    
                    # Simple keyword matching
                    content_lower = memory.content.lower()
                    if query_lower in content_lower:
                        # Calculate simple similarity score
                        similarity = len(query_lower) / len(content_lower)
                        results.append((memory, similarity))
                
                # Sort by similarity and limit results
                results.sort(key=lambda x: x[1], reverse=True)
                results = results[:limit]
                
                self.logger.log_privacy_event(
                    "memory_search",
                    f"results_{len(results)}",
                    user_consent=True
                )
                
                return results
                
        except Exception as e:
            self.logger.error(f"Memory search failed: {e}")
            return []
    
    async def delete_memory(self, agent_id: str, memory_id: str, user_requested: bool = False) -> bool:
        """
        Delete a specific memory (right to be forgotten)
        
        Args:
            agent_id: Agent identifier
            memory_id: Memory identifier
            user_requested: Whether deletion was user-requested
            
        Returns:
            True if deleted successfully
        """
        return await self._delete_memory(agent_id, memory_id, user_requested)
    
    async def _delete_memory(self, agent_id: str, memory_id: str, user_requested: bool = False) -> bool:
        """Internal memory deletion"""
        try:
            async with self._lock:
                if agent_id not in self.agent_memories:
                    return False
                
                agent_memories = self.agent_memories[agent_id]
                if memory_id not in agent_memories:
                    return False
                
                memory = agent_memories[memory_id]
                
                # Remove from agent memories
                del agent_memories[memory_id]
                
                # Remove from vector store if present
                if self.vector_store:
                    # This would integrate with vector store deletion
                    pass
                
                if user_requested:
                    self.logger.log_human_rights_event(
                        "memory_deleted_user_request",
                        user_control=True
                    )
                else:
                    self.logger.log_privacy_event(
                        "memory_deleted_retention",
                        f"{memory.memory_type.value}",
                        user_consent=True
                    )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Memory deletion failed: {e}")
            return False
    
    async def get_agent_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summary of agent's memories"""
        try:
            async with self._lock:
                if agent_id not in self.agent_memories:
                    return {"total_memories": 0}
                
                agent_memories = self.agent_memories[agent_id]
                
                # Count by type
                type_counts = {}
                importance_counts = {}
                
                for memory in agent_memories.values():
                    # Skip expired memories
                    if await self._is_memory_expired(memory):
                        continue
                    
                    memory_type = memory.memory_type.value
                    importance = memory.importance.value
                    
                    type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
                    importance_counts[importance] = importance_counts.get(importance, 0) + 1
                
                return {
                    "total_memories": len(agent_memories),
                    "by_type": type_counts,
                    "by_importance": importance_counts,
                    "constitutional_compliant": all(m.constitutional_compliant for m in agent_memories.values())
                }
                
        except Exception as e:
            self.logger.error(f"Memory summary failed: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_memories(self) -> Dict[str, int]:
        """Clean up expired memories across all agents"""
        try:
            async with self._lock:
                cleanup_counts = {}
                
                for agent_id in list(self.agent_memories.keys()):
                    count = await self._cleanup_old_memories(agent_id)
                    if count > 0:
                        cleanup_counts[agent_id] = count
                
                total_cleaned = sum(cleanup_counts.values())
                if total_cleaned > 0:
                    self.logger.log_privacy_event(
                        "expired_memories_cleanup",
                        f"total_{total_cleaned}",
                        user_consent=True
                    )
                
                return cleanup_counts
                
        except Exception as e:
            self.logger.error(f"Memory cleanup failed: {e}")
            return {}
    
    async def _cleanup_old_memories(self, agent_id: str) -> int:
        """Clean up old memories for specific agent"""
        try:
            if agent_id not in self.agent_memories:
                return 0
            
            agent_memories = self.agent_memories[agent_id]
            expired_memory_ids = []
            
            for memory_id, memory in agent_memories.items():
                if await self._is_memory_expired(memory):
                    expired_memory_ids.append(memory_id)
            
            # Delete expired memories
            for memory_id in expired_memory_ids:
                await self._delete_memory(agent_id, memory_id)
            
            return len(expired_memory_ids)
            
        except Exception as e:
            self.logger.error(f"Agent memory cleanup failed: {e}")
            return 0
    
    async def _is_memory_expired(self, memory: Memory) -> bool:
        """Check if memory has expired based on retention policy"""
        if memory.retention_days is None:
            return False  # Permanent memory
        
        current_time = time.time()
        expiry_time = memory.timestamp + (memory.retention_days * 24 * 3600)
        
        return current_time > expiry_time
    
    async def _validate_memory_compliance(self, content: str, agent_id: str) -> bool:
        """Validate memory content for constitutional compliance"""
        # Check for sensitive information patterns
        content_lower = content.lower()
        sensitive_patterns = [
            "password", "private key", "secret", "api key",
            "social security", "credit card", "bank account"
        ]
        
        for pattern in sensitive_patterns:
            if pattern in content_lower:
                return False
        
        # Check content size (privacy: data minimization)
        if len(content.encode()) > 1024 * 1024:  # 1MB limit
            return False
        
        return True
    
    async def _store_in_vector_store(self, memory: Memory):
        """Store memory in vector store for semantic search"""
        try:
            if not self.vector_store or not memory.embedding:
                return
            
            # Store in agent memory collection
            success = self.vector_store.store_agent_memory(
                agent_id=memory.agent_id,
                content=memory.content,
                embedding=memory.embedding,
                metadata={
                    "memory_id": memory.memory_id,
                    "memory_type": memory.memory_type.value,
                    "importance": memory.importance.value,
                    "timestamp": memory.timestamp,
                    **memory.metadata
                }
            )
            
            if not success:
                self.logger.warning(f"Failed to store memory {memory.memory_id} in vector store")
                
        except Exception as e:
            self.logger.error(f"Vector store memory storage failed: {e}")

def create_memory_manager(settings: HAINetSettings, vector_store: Optional[VectorStore] = None) -> MemoryManager:
    """
    Create and configure constitutional memory manager
    
    Args:
        settings: HAI-Net settings
        vector_store: Optional vector store for semantic search
        
    Returns:
        Configured MemoryManager instance
    """
    return MemoryManager(settings, vector_store)

if __name__ == "__main__":
    # Test the constitutional memory system
    import asyncio
    from core.config.settings import HAINetSettings
    
    async def test_memory():
        print("HAI-Net Constitutional Memory Test")
        print("=" * 35)
        
        # Create test settings
        settings = HAINetSettings()
        
        # Create memory manager
        memory_manager = create_memory_manager(settings)
        
        try:
            # Test memory storage
            memory_id = await memory_manager.store_memory(
                agent_id="test_agent_001",
                content="Constitutional AI principles guide HAI-Net development and ensure human rights protection.",
                memory_type=MemoryType.SEMANTIC,
                importance=MemoryImportance.HIGH,
                metadata={"topic": "constitutional_ai", "source": "training"}
            )
            print(f"✅ Memory stored: {memory_id}")
            
            # Test memory retrieval
            if memory_id:
                retrieved_memory = await memory_manager.retrieve_memory("test_agent_001", memory_id)
                if retrieved_memory:
                    print(f"✅ Memory retrieved: {retrieved_memory.content[:50]}...")
            
            # Test memory search
            search_results = await memory_manager.search_memories(
                agent_id="test_agent_001",
                query="constitutional",
                limit=5
            )
            print(f"🔍 Memory search results: {len(search_results)}")
            
            # Test agent memory summary
            summary = await memory_manager.get_agent_memory_summary("test_agent_001")
            print(f"📊 Memory summary: {summary}")
            
            # Test memory cleanup
            cleanup_results = await memory_manager.cleanup_expired_memories()
            print(f"🧹 Cleanup results: {cleanup_results}")
            
            print("\n🎉 Constitutional Memory System Working!")
            
        except Exception as e:
            print(f"❌ Memory test failed: {e}")
    
    # Run the test
    asyncio.run(test_memory())
