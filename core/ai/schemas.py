# START OF FILE core/ai/schemas.py
"""
HAI-Net AI Schemas
Data structures shared across the AI module to prevent circular dependencies.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
import time

@dataclass
class AgentMemory:
    """Agent memory structure"""
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: List[Dict[str, Any]] = field(default_factory=list)
    episodic: List[Dict[str, Any]] = field(default_factory=list)
    semantic: Dict[str, Any] = field(default_factory=dict)
    constitutional: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.constitutional:
            self.constitutional = {
                "violations": [],
                "compliance_score": 1.0,
                "last_check": time.time()
            }