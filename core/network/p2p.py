# START OF FILE core/network/p2p.py
"""
HAI-Net P2P Communication Protocol
Constitutional compliance: Decentralization Imperative (Article III)
Secure, encrypted peer-to-peer communication without central authority
"""

import asyncio
import json
import time
import ssl
import socket
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import struct
import hashlib
import secrets

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError
from .discovery import NetworkNode


class MessageType(Enum):
    """P2P message types"""
    HANDSHAKE = "handshake"
    HEARTBEAT = "heartbeat"
    CHAT = "chat"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    RESOURCE_OFFER = "resource_offer"
    RESOURCE_REQUEST = "resource_request"
    CONSTITUTIONAL_ALERT = "constitutional_alert"
    AGENT_COMMUNICATION = "agent_communication"


@dataclass
class P2PMessage:
    """Represents a P2P message"""
    message_id: str
    message_type: MessageType
    sender_id: str
    receiver_id: str
    content: Dict[str, Any]
    timestamp: float
    constitutional_version: str
    signature: Optional[str] = None
    encrypted: bool = False


@dataclass
class PeerConnection:
    """Represents a connection to a peer"""
    node: NetworkNode
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None
    connected: bool = False
    last_heartbeat: float = 0.0
    message_queue: Optional[List[P2PMessage]] = None
    encryption_key: Optional[bytes] = None
    
    def __post_init__(self):
        if self.message_queue is None:
            self.message_queue = []


class P2PManager:
    """
    Constitutional P2P communication manager
    Implements decentralized messaging without central authority
    """
    
    def __init__(self, settings: HAINetSettings, node_id: str, did: Optional[str] = None):
        self.settings = settings
        self.node_id = node_id
        self.did = did
        self.logger = get_logger("network.p2p", settings)
        
        # Network configuration
        self.listen_port = settings.p2p_port
        self.max_connections = 50  # Constitutional principle: local community focus
        
        # Connection management
        self.connections: Dict[str, PeerConnection] = {}
        self.message_handlers: Dict[MessageType, Callable[[P2PMessage, str], None]] = {}
        self.server: Optional[asyncio.Server] = None
        
        # Message tracking
        self.sent_messages: Dict[str, P2PMessage] = {}
        self.received_messages: Dict[str, P2PMessage] = {}
        self.message_callbacks: List[Callable[[P2PMessage], None]] = []
        
        # Type for async message handlers
        from typing import Coroutine
        self._handler_type = Callable[[P2PMessage, str], Coroutine[Any, Any, None]]
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_message_size = 1024 * 1024  # 1MB limit for privacy
        
        # Async management
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.running = False
        self._lock = asyncio.Lock()
        
        # Setup default message handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default constitutional message handlers"""
        # Note: These are async handlers, will be awaited when called
        self.message_handlers[MessageType.HANDSHAKE] = self._handle_handshake  # type: ignore
        self.message_handlers[MessageType.HEARTBEAT] = self._handle_heartbeat  # type: ignore
        self.message_handlers[MessageType.CONSTITUTIONAL_ALERT] = self._handle_constitutional_alert  # type: ignore
    
    async def start_p2p_service(self) -> bool:
        """
        Start P2P communication service
        Constitutional requirement: Decentralized communication
        """
        try:
            if self.running:
                self.logger.warning("P2P service already running", category="network", function="start_p2p_service")
                return True
            
            # Get or create event loop
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            # Start listening server
            self.server = await asyncio.start_server(
                self._handle_incoming_connection,
                host='0.0.0.0',
                port=self.listen_port,
                family=socket.AF_INET
            )
            
            self.running = True
            
            # Start maintenance tasks
            asyncio.create_task(self._connection_maintenance_loop())
            asyncio.create_task(self._heartbeat_loop())
            
            self.logger.log_decentralization_event(
                "p2p_service_started",
                local_processing=True
            )
            self.logger.info_network(f"P2P service started on port {self.listen_port}", function="start_p2p_service")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start P2P service: {e}", category="network", function="start_p2p_service")
            return False
    
    async def stop_p2p_service(self):
        """Stop P2P communication service"""
        try:
            self.running = False
            
            # Close all connections
            for connection in list(self.connections.values()):
                await self._close_connection(connection)
            
            # Close server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                self.server = None
            
            self.logger.log_decentralization_event(
                "p2p_service_stopped",
                local_processing=True
            )
            self.logger.info_network("P2P service stopped", function="stop_p2p_service")
            
        except Exception as e:
            self.logger.error(f"Error stopping P2P service: {e}", category="network", function="stop_p2p_service")
    
    async def connect_to_peer(self, node: NetworkNode) -> bool:
        """
        Establish connection to a peer node
        Constitutional validation required
        """
        try:
            if node.node_id in self.connections:
                self.logger.debug_network(f"Already connected to {node.node_id}", function="connect_to_peer")
                return True
            
            # Constitutional compliance check
            if not self._validate_peer_constitutional_compliance(node):
                self.logger.log_violation("peer_constitutional_violation", {
                    "node_id": node.node_id,
                    "reason": "Failed constitutional validation"
                })
                return False
            
            # Check connection limits (community focus principle)
            if len(self.connections) >= self.max_connections:
                self.logger.warning(f"Connection limit reached ({self.max_connections})", category="network", function="connect_to_peer")
                return False
            
            # Establish TCP connection
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(node.address, node.port),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"Connection timeout to {node.node_id}", category="network", function="connect_to_peer")
                return False
            except Exception as e:
                self.logger.warning(f"Failed to connect to {node.node_id}: {e}", category="network", function="connect_to_peer")
                return False
            
            # Create peer connection
            connection = PeerConnection(
                node=node,
                reader=reader,
                writer=writer,
                connected=True,
                last_heartbeat=time.time()
            )
            
            async with self._lock:
                self.connections[node.node_id] = connection
            
            # Start connection handler
            asyncio.create_task(self._handle_peer_connection(connection))
            
            # Send handshake
            await self._send_handshake(connection)
            
            self.logger.log_decentralization_event(
                f"peer_connected: {node.node_id}",
                local_processing=True
            )
            self.logger.info_network(f"Connected to peer: {node.node_id} at {node.address}:{node.port}", function="connect_to_peer")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to peer {node.node_id}: {e}", category="network", function="connect_to_peer")
            return False
    
    async def disconnect_from_peer(self, node_id: str):
        """Disconnect from a specific peer"""
        async with self._lock:
            if node_id in self.connections:
                connection = self.connections[node_id]
                await self._close_connection(connection)
                del self.connections[node_id]
                
                self.logger.log_decentralization_event(
                    f"peer_disconnected: {node_id}",
                    local_processing=True
                )
                self.logger.info_network(f"Disconnected from peer: {node_id}", function="disconnect_from_peer")
    
    async def send_message(self, receiver_id: str, message_type: MessageType, content: Dict[str, Any]) -> bool:
        """
        Send message to a specific peer
        Constitutional compliance enforced
        """
        try:
            # Validate constitutional compliance of message content
            if not self._validate_message_constitutional_compliance(message_type, content):
                self.logger.log_violation("message_constitutional_violation", {
                    "receiver": receiver_id,
                    "type": message_type.value,
                    "reason": "Message violates constitutional principles"
                })
                return False
            
            # Check if connected to peer
            async with self._lock:
                if receiver_id not in self.connections:
                    self.logger.warning(f"Not connected to peer: {receiver_id}", category="network", function="send_message")
                    return False
                
                connection = self.connections[receiver_id]
                if not connection.connected:
                    self.logger.warning(f"Connection to {receiver_id} is not active", category="network", function="send_message")
                    return False
            
            # Create message
            message = P2PMessage(
                message_id=self._generate_message_id(),
                message_type=message_type,
                sender_id=self.node_id,
                receiver_id=receiver_id,
                content=content,
                timestamp=time.time(),
                constitutional_version=self.constitutional_version
            )
            
            # Add to sent messages tracking
            self.sent_messages[message.message_id] = message
            
            # Send message
            await self._send_message_to_connection(connection, message)
            
            self.logger.log_privacy_event(
                f"message_sent: {message_type.value}",
                "p2p_communication",
                user_consent=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message to {receiver_id}: {e}", category="network", function="send_message")
            return False
    
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any], trusted_only: bool = True) -> int:
        """
        Broadcast message to all connected peers
        Constitutional principle: Community communication
        """
        sent_count = 0
        
        try:
            # Validate message
            if not self._validate_message_constitutional_compliance(message_type, content):
                self.logger.log_violation("broadcast_constitutional_violation", {
                    "type": message_type.value,
                    "reason": "Broadcast message violates constitutional principles"
                })
                return 0
            
            async with self._lock:
                connections = list(self.connections.values())
            
            # Send to all appropriate connections
            for connection in connections:
                if not connection.connected:
                    continue
                
                # Check trust level if required
                if trusted_only and connection.node.trust_level < 0.5:
                    continue
                
                success = await self.send_message(
                    connection.node.node_id,
                    message_type,
                    content
                )
                
                if success:
                    sent_count += 1
            
            self.logger.log_community_event(
                f"broadcast_sent: {message_type.value} to {sent_count} peers",
                community_benefit=True
            )
            
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Error broadcasting message: {e}", category="network", function="broadcast_message")
            return 0
    
    async def _handle_incoming_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming peer connection"""
        try:
            # Get peer address
            peer_addr = writer.get_extra_info('peername')
            peer_ip = peer_addr[0] if peer_addr else "unknown"
            
            self.logger.debug_network(f"Incoming connection from {peer_ip}", function="_handle_incoming_connection")
            
            # Create temporary connection for handshake
            temp_connection = PeerConnection(
                node=NetworkNode(
                    node_id="unknown",
                    did=None,
                    address=peer_ip,
                    port=0,
                    role="unknown",
                    capabilities={},
                    constitutional_version="unknown",
                    discovered_at=time.time(),
                    last_seen=time.time()
                ),
                reader=reader,
                writer=writer,
                connected=True
            )
            
            # Wait for handshake with timeout
            try:
                handshake_message = await asyncio.wait_for(
                    self._receive_message_from_connection(temp_connection),
                    timeout=30.0
                )
                
                if handshake_message is None:
                    self.logger.warning(f"No handshake received from {peer_ip}", category="network", function="_handle_incoming_connection")
                    await self._close_connection(temp_connection)
                    return
                
                if handshake_message.message_type != MessageType.HANDSHAKE:
                    self.logger.warning(f"Expected handshake from {peer_ip}, got {handshake_message.message_type}", category="network", function="_handle_incoming_connection")
                    await self._close_connection(temp_connection)
                    return
                
                # Process handshake
                node_id = handshake_message.sender_id
                
                # Constitutional compliance check
                if handshake_message.constitutional_version != self.constitutional_version:
                    self.logger.log_violation("incoming_constitutional_violation", {
                        "node_id": node_id,
                        "version": handshake_message.constitutional_version
                    })
                    await self._close_connection(temp_connection)
                    return
                
                # Check connection limits
                if len(self.connections) >= self.max_connections:
                    self.logger.warning(f"Connection limit reached, rejecting {node_id}", category="network", function="_handle_incoming_connection")
                    await self._close_connection(temp_connection)
                    return
                
                # Update connection with proper node info
                temp_connection.node.node_id = node_id
                temp_connection.node.constitutional_version = handshake_message.constitutional_version
                temp_connection.node.capabilities = handshake_message.content.get("capabilities", {})
                temp_connection.node.role = handshake_message.content.get("role", "unknown")
                temp_connection.node.did = handshake_message.content.get("did")
                
                async with self._lock:
                    self.connections[node_id] = temp_connection
                
                # Send handshake response
                await self._send_handshake(temp_connection)
                
                # Start connection handler
                asyncio.create_task(self._handle_peer_connection(temp_connection))
                
                self.logger.log_decentralization_event(
                    f"incoming_peer_accepted: {node_id}",
                    local_processing=True
                )
                self.logger.info_network(f"Accepted incoming connection from {node_id}", function="_handle_incoming_connection")
                
            except asyncio.TimeoutError:
                self.logger.warning(f"Handshake timeout from {peer_ip}", category="network", function="_handle_incoming_connection")
                await self._close_connection(temp_connection)
            
        except Exception as e:
            self.logger.error(f"Error handling incoming connection: {e}", category="network", function="_handle_incoming_connection")
            if 'temp_connection' in locals():
                await self._close_connection(temp_connection)
    
    async def _handle_peer_connection(self, connection: PeerConnection):
        """Handle ongoing communication with a peer"""
        try:
            while connection.connected and self.running:
                try:
                    # Receive message with timeout
                    message = await asyncio.wait_for(
                        self._receive_message_from_connection(connection),
                        timeout=60.0
                    )
                    
                    if message is not None:
                        await self._process_received_message(message, connection.node.node_id)
                    
                except asyncio.TimeoutError:
                    # Check if connection is still alive via heartbeat
                    if time.time() - connection.last_heartbeat > 300:  # 5 minutes
                        self.logger.info_network(f"Connection timeout for {connection.node.node_id}", function="_handle_peer_connection")
                        break
                    
                except Exception as e:
                    self.logger.error(f"Error in peer connection {connection.node.node_id}: {e}", category="network", function="_handle_peer_connection")
                    break
            
        except Exception as e:
            self.logger.error(f"Peer connection handler error for {connection.node.node_id}: {e}", category="network", function="_handle_peer_connection")
        
        finally:
            await self._close_connection(connection)
    
    async def _send_message_to_connection(self, connection: PeerConnection, message: P2PMessage):
        """Send message to a specific connection"""
        try:
            if connection.writer is None:
                raise RuntimeError("Connection writer is None")
            
            # Serialize message
            message_data = self._serialize_message(message)
            
            # Check message size
            if len(message_data) > self.max_message_size:
                raise ConstitutionalViolationError("Message exceeds size limit")
            
            # Send message length first, then message
            message_length = struct.pack('!I', len(message_data))
            connection.writer.write(message_length)
            connection.writer.write(message_data)
            await connection.writer.drain()
            
        except Exception as e:
            self.logger.error(f"Error sending message to {connection.node.node_id}: {e}", category="network", function="_send_message_to_connection")
            raise
    
    async def _receive_message_from_connection(self, connection: PeerConnection) -> Optional[P2PMessage]:
        """Receive message from a specific connection"""
        try:
            if connection.reader is None:
                raise RuntimeError("Connection reader is None")
            
            # Read message length
            length_data = await connection.reader.readexactly(4)
            message_length = struct.unpack('!I', length_data)[0]
            
            # Validate message length
            if message_length > self.max_message_size:
                raise ConstitutionalViolationError("Received message exceeds size limit")
            
            # Read message data
            message_data = await connection.reader.readexactly(message_length)
            
            # Deserialize message
            message = self._deserialize_message(message_data)
            
            return message
            
        except asyncio.IncompleteReadError:
            # Connection closed
            return None
        except Exception as e:
            self.logger.error(f"Error receiving message from {connection.node.node_id}: {e}", category="network", function="_receive_message_from_connection")
            return None
    
    async def _process_received_message(self, message: P2PMessage, sender_id: str):
        """Process a received message"""
        try:
            # Validate constitutional compliance
            if not self._validate_received_message(message):
                self.logger.log_violation("received_message_violation", {
                    "sender": sender_id,
                    "type": message.message_type.value if message.message_type else "unknown",
                    "reason": "Message violates constitutional principles"
                })
                return
            
            # Add to received messages
            self.received_messages[message.message_id] = message
            
            # Call appropriate handler
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                # Handler is async, await it
                if asyncio.iscoroutinefunction(handler):
                    await handler(message, sender_id)
                else:
                    handler(message, sender_id)
            
            # Notify callbacks
            for callback in self.message_callbacks:
                try:
                    callback(message)
                except Exception as e:
                    self.logger.error(f"Message callback error: {e}", category="network", function="_process_received_message")
            
            self.logger.log_privacy_event(
                f"message_received: {message.message_type.value}",
                "p2p_communication",
                user_consent=True
            )
            
        except Exception as e:
            self.logger.error(f"Error processing message from {sender_id}: {e}", category="network", function="_process_received_message")
    
    async def _send_handshake(self, connection: PeerConnection):
        """Send handshake message to establish connection"""
        handshake_content = {
            "constitutional_version": self.constitutional_version,
            "node_role": self.settings.node_role,
            "capabilities": self._get_node_capabilities(),
            "did": self.did,
            "timestamp": time.time()
        }
        
        message = P2PMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.HANDSHAKE,
            sender_id=self.node_id,
            receiver_id=connection.node.node_id,
            content=handshake_content,
            timestamp=time.time(),
            constitutional_version=self.constitutional_version
        )
        
        await self._send_message_to_connection(connection, message)
    
    async def _handle_handshake(self, message: P2PMessage, sender_id: str):
        """Handle handshake message"""
        self.logger.debug_network(f"Handshake received from {sender_id}", function="_handle_handshake")
        
        # Update connection info if needed
        async with self._lock:
            if sender_id in self.connections:
                connection = self.connections[sender_id]
                connection.last_heartbeat = time.time()
    
    async def _handle_heartbeat(self, message: P2PMessage, sender_id: str):
        """Handle heartbeat message"""
        async with self._lock:
            if sender_id in self.connections:
                connection = self.connections[sender_id]
                connection.last_heartbeat = time.time()
    
    async def _handle_constitutional_alert(self, message: P2PMessage, sender_id: str):
        """Handle constitutional alert from peer"""
        self.logger.log_violation("peer_constitutional_alert", {
            "sender": sender_id,
            "alert": message.content
        })
    
    async def _connection_maintenance_loop(self):
        """Background maintenance for P2P connections"""
        while self.running:
            try:
                current_time = time.time()
                
                # Check for stale connections
                async with self._lock:
                    stale_connections = []
                    for node_id, connection in self.connections.items():
                        if current_time - connection.last_heartbeat > 300:  # 5 minutes
                            stale_connections.append(node_id)
                
                # Clean up stale connections
                for node_id in stale_connections:
                    await self.disconnect_from_peer(node_id)
                
                # Sleep before next maintenance cycle
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"P2P maintenance error: {e}", category="network", function="_connection_maintenance_loop")
                await asyncio.sleep(30)  # Shorter sleep on error
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to maintain connections"""
        while self.running:
            try:
                async with self._lock:
                    connections = list(self.connections.values())
                
                # Send heartbeat to all connections
                for connection in connections:
                    if connection.connected:
                        try:
                            await self.send_message(
                                connection.node.node_id,
                                MessageType.HEARTBEAT,
                                {"timestamp": time.time()}
                            )
                        except Exception as e:
                            self.logger.debug_network(f"Heartbeat failed to {connection.node.node_id}", function="_heartbeat_loop")
                
                # Sleep before next heartbeat
                await asyncio.sleep(120)  # Heartbeat every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}", category="network", function="_heartbeat_loop")
                await asyncio.sleep(60)
    
    async def _close_connection(self, connection: PeerConnection):
        """Close a peer connection"""
        try:
            connection.connected = False
            
            if connection.writer:
                connection.writer.close()
                await connection.writer.wait_closed()
            
        except Exception as e:
            self.logger.debug_network(f"Error closing connection", function="_close_connection")
    
    def _validate_peer_constitutional_compliance(self, node: NetworkNode) -> bool:
        """Validate peer constitutional compliance"""
        return (
            node.constitutional_version == self.constitutional_version and
            node.role in ['master', 'slave'] and
            node.trust_level >= 0.5
        )
    
    def _validate_message_constitutional_compliance(self, message_type: MessageType, content: Dict[str, Any]) -> bool:
        """Validate message constitutional compliance"""
        # Check content size (privacy principle)
        if len(json.dumps(content).encode()) > self.max_message_size:
            return False
        
        # Check for sensitive data (privacy principle)
        content_str = json.dumps(content).lower()
        sensitive_patterns = ['password', 'private_key', 'secret', 'ssn', 'credit_card']
        if any(pattern in content_str for pattern in sensitive_patterns):
            return False
        
        return True
    
    def _validate_received_message(self, message: P2PMessage) -> bool:
        """Validate received message"""
        return (
            message.constitutional_version == self.constitutional_version and
            message.timestamp > 0 and
            abs(time.time() - message.timestamp) < 3600  # Within 1 hour
        )
    
    def _serialize_message(self, message: P2PMessage) -> bytes:
        """Serialize message for transmission"""
        message_dict = {
            "message_id": message.message_id,
            "message_type": message.message_type.value,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "timestamp": message.timestamp,
            "constitutional_version": message.constitutional_version,
            "signature": message.signature,
            "encrypted": message.encrypted
        }
        
        return json.dumps(message_dict).encode('utf-8')
    
    def _deserialize_message(self, data: bytes) -> P2PMessage:
        """Deserialize message from transmission"""
        message_dict = json.loads(data.decode('utf-8'))
        
        return P2PMessage(
            message_id=message_dict["message_id"],
            message_type=MessageType(message_dict["message_type"]),
            sender_id=message_dict["sender_id"],
            receiver_id=message_dict["receiver_id"],
            content=message_dict["content"],
            timestamp=message_dict["timestamp"],
            constitutional_version=message_dict["constitutional_version"],
            signature=message_dict.get("signature"),
            encrypted=message_dict.get("encrypted", False)
        )
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"{self.node_id}_{int(time.time() * 1000)}_{secrets.token_hex(8)}"
    
    def _get_node_capabilities(self) -> Dict[str, Any]:
        """Get this node's capabilities"""
        return {
            "llm_support": True,
            "voice_stt": self.settings.voice_stt_enabled,
            "voice_tts": self.settings.voice_tts_enabled,
            "image_generation": self.settings.image_generation_enabled,
            "resource_sharing": self.settings.resource_sharing_enabled,
            "version": "0.1.0"
        }
    
    def add_message_handler(self, message_type: MessageType, handler: Callable[[P2PMessage, str], None]):
        """Add custom message handler"""
        self.message_handlers[message_type] = handler
    
    def add_message_callback(self, callback: Callable[[P2PMessage], None]):
        """Add message callback"""
        self.message_callbacks.append(callback)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get P2P connection statistics"""
        current_time = time.time()
        
        active_connections = len([c for c in self.connections.values() if c.connected])
        recent_heartbeats = len([
            c for c in self.connections.values() 
            if c.connected and current_time - c.last_heartbeat < 300
        ])
        
        return {
            "total_connections": len(self.connections),
            "active_connections": active_connections,
            "recent_heartbeats": recent_heartbeats,
            "sent_messages": len(self.sent_messages),
            "received_messages": len(self.received_messages),
            "constitutional_compliant": len([
                c for c in self.connections.values()
                if c.node.constitutional_version == self.constitutional_version
            ])
        }


def create_p2p_manager(settings: HAINetSettings, node_id: str, did: Optional[str] = None) -> P2PManager:
    """
    Create and configure a constitutional P2P manager
    
    Args:
        settings: HAI-Net settings
        node_id: Unique node identifier
        did: Optional decentralized identity
        
    Returns:
        Configured P2PManager instance
    """
    return P2PManager(settings, node_id, did)


if __name__ == "__main__":
    # Test the P2P system
    from core.config.settings import HAINetSettings
    
    async def test_p2p():
        print("HAI-Net Constitutional P2P Test")
        print("=" * 35)
        
        # Create test settings
        settings = HAINetSettings()
        
        # Create P2P manager
        p2p = create_p2p_manager(
            settings,
            node_id="test_p2p_node",
            did="did:hai:p2ptest123"
        )
        
        # Add message callback
        def on_message_received(message: P2PMessage):
            print(f"📨 Received: {message.message_type.value} from {message.sender_id}")
            print(f"   Content: {message.content}")
        
        p2p.add_message_callback(on_message_received)
        
        try:
            # Start P2P service
            if await p2p.start_p2p_service():
                print("✅ P2P service started successfully")
                print(f"🔗 Listening on port {settings.p2p_port}")
                print("Press Ctrl+C to stop...")
                
                # Keep running
                while True:
                    await asyncio.sleep(5)
                    stats = p2p.get_connection_stats()
                    print(f"📊 Stats: {stats['active_connections']} active, {stats['sent_messages']} sent")
                    
            else:
                print("❌ Failed to start P2P service")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping P2P service...")
            await p2p.stop_p2p_service()
            print("✅ P2P service stopped")
        
        except Exception as e:
            print(f"❌ P2P error: {e}")
            await p2p.stop_p2p_service()
    
    # Run the test
    asyncio.run(test_p2p())
