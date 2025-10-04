# START OF FILE core/ai/tools/schemas.py
"""
HAI-Net Tool Schemas
Data structures for agent tools.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ToolCall:
    """Represents a request from an agent to call a tool."""
    name: str
    args: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResult:
    """Represents the result of a tool execution."""
    tool_name: str
    status: str  # "success" or "error"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None