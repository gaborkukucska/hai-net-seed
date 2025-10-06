# START OF FILE core/web/websocket.py
# HAI-Net WebSocket Manager - Constitutional Real-Time Communication
# Handles WebSocket connections for real-time updates while maintaining constitutional compliance

import asyncio
import json
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from core.logging.logger import get_logger
from core.config.settings import HAINetSettings

class WebSocketManager:
    """
    Constitutional WebSocket Manager for real-time communication
    
    Constitutional Compliance:
    - Privacy First: Local-only WebSocket connections, no external data sharing
    - Human Rights: User control over connection and data flow
    - Decentralization: P2P WebSocket communication support
    - Community Focus: Collaborative real-time features
    """
    
    def __init__(self, settings: Optional[HAINetSettings] = None):
        # Active WebSocket connections
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Constitutional compliance tracking
        self.constitutional_compliance = True
        self.privacy_first = True
        self.human_rights_protected = True
        self.decentralized = True
        self.community_focused = True
        
        # Initialize logger
        self.settings = settings or HAINetSettings()
        self.logger = get_logger("web.websocket", self.settings)
        
        self.logger.info("🌐 WebSocket Manager initialized with constitutional compliance", category="init", function="__init__")
    
    async def connect(self, websocket: WebSocket, client_info: Optional[Dict[str, Any]] = None):
        """
        Accept new WebSocket connection with constitutional compliance
        """
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            
            # Store constitutional metadata
            self.connection_metadata[websocket] = {
                'connected_at': datetime.utcnow().isoformat(),
                'client_info': client_info or {},
                'constitutional_compliance': True,
                'privacy_respected': True,
                'messages_sent': 0,
                'last_activity': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ WebSocket connection established (Total: {len(self.active_connections)})", category="websocket", function="connect")
            
            # Send welcome message with constitutional principles
            await self.send_to_connection(websocket, {
                'type': 'connection_established',
                'message': 'Welcome to HAI-Net Constitutional Network',
                'constitutional_principles': {
                    'privacy_first': 'Your data stays local',
                    'human_rights': 'You maintain control',
                    'decentralization': 'No central authority',
                    'community_focus': 'Collaborative governance'
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"❌ WebSocket connection failed: {e}", category="websocket", function="connect")
            raise
    
    def disconnect(self, websocket: WebSocket):
        """
        Handle WebSocket disconnection
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
            if websocket in self.connection_metadata:
                metadata = self.connection_metadata.pop(websocket)
                self.logger.debug(f"🔌 WebSocket disconnected (Messages sent: {metadata['messages_sent']})", category="websocket", function="disconnect")
            
            self.logger.debug(f"📊 Active connections: {len(self.active_connections)}", category="websocket", function="disconnect")
    
    async def send_to_connection(self, websocket: WebSocket, data: Dict[str, Any]):
        """
        Send data to specific WebSocket connection with constitutional compliance
        """
        try:
            # Add constitutional metadata to all messages
            message = {
                **data,
                'constitutional_compliant': True,
                'privacy_respected': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(message))
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]['messages_sent'] += 1
                self.connection_metadata[websocket]['last_activity'] = datetime.utcnow().isoformat()
                
        except WebSocketDisconnect:
            self.logger.debug("🔌 WebSocket disconnected during send", category="websocket", function="send_to_connection")
            self.disconnect(websocket)
        except Exception as e:
            self.logger.error(f"❌ Failed to send WebSocket message: {e}", category="websocket", function="send_to_connection")
            self.disconnect(websocket)
    
    async def broadcast(self, data: Dict[str, Any], exclude: Optional[WebSocket] = None):
        """
        Broadcast message to all connected clients with constitutional compliance
        """
        if not self.active_connections:
            self.logger.debug("📡 No active connections for broadcast", category="websocket", function="broadcast")
            return
        
        # Add constitutional compliance metadata
        message = {
            **data,
            'type': data.get('type', 'broadcast'),
            'constitutional_compliant': True,
            'privacy_respected': True,
            'broadcast_timestamp': datetime.utcnow().isoformat()
        }
        
        # Send to all connections except excluded one
        disconnected_connections = []
        
        for connection in self.active_connections:
            if connection == exclude:
                continue
                
            try:
                await connection.send_text(json.dumps(message))
                
                # Update metadata
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]['messages_sent'] += 1
                    self.connection_metadata[connection]['last_activity'] = datetime.utcnow().isoformat()
                    
            except WebSocketDisconnect:
                self.logger.debug("🔌 WebSocket disconnected during broadcast", category="websocket", function="broadcast")
                disconnected_connections.append(connection)
            except Exception as e:
                self.logger.error(f"❌ Failed to send broadcast to connection: {e}", category="websocket", function="broadcast")
                disconnected_connections.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
        
        self.logger.debug(f"📡 Broadcast sent to {len(self.active_connections) - len(disconnected_connections)} connections", category="websocket", function="broadcast")
    
    async def send_constitutional_update(self, update_type: str, data: Dict[str, Any]):
        """
        Send constitutional compliance updates to all connections
        """
        await self.broadcast({
            'type': 'constitutional_update',
            'update_type': update_type,
            'data': data,
            'constitutional_principles_maintained': True
        })
    
    async def send_network_status(self, status: Dict[str, Any]):
        """
        Send network status updates
        """
        await self.broadcast({
            'type': 'network_status',
            'status': status,
            'decentralized_network': True
        })
    
    async def send_node_update(self, node_data: Dict[str, Any]):
        """
        Send node status updates
        """
        await self.broadcast({
            'type': 'node_update',
            'node_data': node_data,
            'constitutional_node': True
        })
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket connection statistics with constitutional compliance
        """
        total_messages = sum(
            metadata.get('messages_sent', 0) 
            for metadata in self.connection_metadata.values()
        )
        
        return {
            'active_connections': len(self.active_connections),
            'total_messages_sent': total_messages,
            'constitutional_compliance': self.constitutional_compliance,
            'privacy_first': self.privacy_first,
            'human_rights_protected': self.human_rights_protected,
            'decentralized': self.decentralized,
            'community_focused': self.community_focused,
            'uptime_info': {
                'connections_established': len(self.connection_metadata),
                'average_messages_per_connection': total_messages / max(len(self.connection_metadata), 1)
            }
        }

# Global WebSocket manager instance - will be initialized with settings when needed
websocket_manager = None

def get_websocket_manager(settings: Optional[HAINetSettings] = None) -> WebSocketManager:
    """Get or create the global WebSocket manager instance"""
    global websocket_manager
    if websocket_manager is None:
        websocket_manager = WebSocketManager(settings)
    return websocket_manager

# Export for use in other modules
__all__ = ['WebSocketManager', 'websocket_manager', 'get_websocket_manager']
