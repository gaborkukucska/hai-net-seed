# START OF FILE core/network/discovery.py
"""
HAI-Net Local Network Discovery
Constitutional compliance: Decentralization Imperative (Article III)
Uses mDNS/Zeroconf for local network discovery without central authority
"""

import socket
import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo, ServiceListener
import netifaces
import ipaddress

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError


@dataclass
class NetworkNode:
    """Represents a discovered HAI-Net node"""
    node_id: str
    did: Optional[str]
    address: str
    port: int
    role: str  # 'master' or 'slave'
    capabilities: Dict[str, Any]
    constitutional_version: str
    discovered_at: float
    last_seen: float
    trust_level: float = 0.0  # 0.0 to 1.0


class ConstitutionalNetworkListener(ServiceListener):
    """
    Service listener that enforces constitutional compliance
    """
    
    def __init__(self, discovery_manager):
        self.discovery = discovery_manager
        self.logger = get_logger("network.discovery")
    
    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle new service discovery"""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            try:
                node = self.discovery._parse_service_info(name, info)
                if self.discovery._validate_constitutional_compliance(node):
                    self.discovery._add_discovered_node(node)
                    self.logger.log_decentralization_event(
                        f"node_discovered: {node.node_id}",
                        local_processing=True
                    )
                else:
                    self.logger.log_violation("constitutional_non_compliance", {
                        "node_id": node.node_id,
                        "reason": "Failed constitutional validation"
                    })
            except Exception as e:
                self.logger.error(f"Failed to process discovered service: {e}", category="discovery", function="add_service")
    
    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle service removal"""
        node_id = name.split('.')[0] if '.' in name else name
        self.discovery._remove_discovered_node(node_id)
        self.logger.log_decentralization_event(
            f"node_removed: {node_id}",
            local_processing=True
        )
    
    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle service updates"""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            try:
                node = self.discovery._parse_service_info(name, info)
                node.last_seen = time.time()
                self.discovery._update_discovered_node(node)
            except Exception as e:
                self.logger.error(f"Failed to update service: {e}", category="discovery", function="update_service")


class LocalDiscovery:
    """
    mDNS-based local network discovery for HAI-Net nodes
    Constitutional Principle: Decentralization - no central authority required
    """
    
    def __init__(self, settings: HAINetSettings, node_id: str, did: Optional[str] = None):
        self.settings = settings
        self.node_id = node_id
        self.did = did
        self.logger = get_logger("network.discovery", settings)
        
        # Service configuration
        self.service_type = settings.mdns_service_name
        self.port = settings.p2p_port
        
        # Zeroconf instances
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self.browser: Optional[ServiceBrowser] = None
        self.listener: Optional[ConstitutionalNetworkListener] = None
        
        # Discovered nodes
        self.discovered_nodes: Dict[str, NetworkNode] = {}
        self.discovery_callbacks: List[Callable[[NetworkNode], None]] = []
        self.removal_callbacks: List[Callable[[str], None]] = []
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.trust_threshold = 0.5  # Minimum trust level for interaction
        
        # Threading
        self.discovery_thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.Lock()
    
    def start_discovery(self) -> bool:
        """
        Start mDNS discovery service
        Constitutional requirement: Local-first discovery
        """
        try:
            if self.running:
                self.logger.warning("Discovery already running", category="discovery", function="start_discovery")
                return True
            
            # Initialize Zeroconf
            self.zeroconf = Zeroconf()
            
            # Create and register our service
            if not self._register_service():
                return False
            
            # Start browsing for other services
            self._start_browsing()
            
            # Start maintenance thread
            self.running = True
            self.discovery_thread = threading.Thread(
                target=self._discovery_maintenance_loop,
                daemon=True
            )
            self.discovery_thread.start()
            
            self.logger.log_decentralization_event(
                "discovery_started",
                local_processing=True
            )
            self.logger.info(f"HAI-Net discovery started on {self.service_type}", category="discovery", function="start_discovery")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start discovery: {e}", category="discovery", function="start_discovery")
            return False
    
    def stop_discovery(self):
        """Stop discovery service"""
        try:
            self.running = False
            
            if self.discovery_thread:
                self.discovery_thread.join(timeout=5.0)
            
            if self.browser:
                self.browser.cancel()
                self.browser = None
            
            if self.service_info and self.zeroconf:
                self.zeroconf.unregister_service(self.service_info)
                self.service_info = None
            
            if self.zeroconf:
                self.zeroconf.close()
                self.zeroconf = None
            
            self.logger.log_decentralization_event(
                "discovery_stopped",
                local_processing=True
            )
            self.logger.info("HAI-Net discovery stopped", category="discovery", function="stop_discovery")
            
        except Exception as e:
            self.logger.error(f"Error stopping discovery: {e}", category="discovery", function="stop_discovery")
    
    def _register_service(self) -> bool:
        """Register this node as a HAI-Net service"""
        try:
            # Get local IP addresses
            local_ips = self._get_local_ip_addresses()
            if not local_ips:
                self.logger.error("No local IP addresses found", category="network", function="_register_service")
                return False
            
            # Prepare service properties (constitutional compliance info)
            properties = {
                "role": self.settings.node_role.encode(),
                "constitutional_version": self.constitutional_version.encode(),
                "did": (self.did or "").encode(),
                "capabilities": json.dumps(self._get_node_capabilities()).encode(),
                "privacy_compliant": b"true",
                "decentralized": b"true",
                "community_focused": b"true"
            }
            
            # Create service info
            service_name = f"{self.node_id}.{self.service_type}"
            
            # Convert IP addresses to bytes
            addresses = []
            for ip in local_ips:
                try:
                    addr = ipaddress.ip_address(ip)
                    if addr.version == 4:
                        addresses.append(socket.inet_aton(str(addr)))
                    # Note: IPv6 support can be added later
                except Exception as e:
                    self.logger.debug(f"Skipping invalid IP {ip}: {e}", category="network", function="_register_service")
            
            if not addresses:
                self.logger.error("No valid IP addresses for service registration", category="network", function="_register_service")
                return False
            
            self.service_info = ServiceInfo(
                self.service_type,
                service_name,
                addresses=addresses,
                port=self.port,
                properties=properties,
                server=f"{self.node_id}.local."
            )
            
            # Register the service
            self.zeroconf.register_service(self.service_info)
            
            self.logger.log_privacy_event(
                "service_registered",
                "node_advertisement",
                user_consent=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service: {e}", category="discovery", function="_register_service")
            return False
    
    def _start_browsing(self):
        """Start browsing for other HAI-Net services"""
        try:
            self.listener = ConstitutionalNetworkListener(self)
            self.browser = ServiceBrowser(
                self.zeroconf,
                self.service_type,
                listener=self.listener
            )
            
            self.logger.info(f"Started browsing for {self.service_type}", category="discovery", function="_start_browsing")
            
        except Exception as e:
            self.logger.error(f"Failed to start browsing: {e}", category="discovery", function="_start_browsing")
    
    def _get_local_ip_addresses(self) -> List[str]:
        """Get all local IP addresses for this machine"""
        ips = []
        
        try:
            # Get all network interfaces
            for interface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(interface)
                    
                    # Get IPv4 addresses
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info.get('addr')
                            if ip and ip != '127.0.0.1':  # Skip localhost
                                ips.append(ip)
                                
                except Exception:
                    continue  # Skip problematic interfaces
                    
        except Exception as e:
            self.logger.debug(f"Error getting network interfaces: {e}", category="network", function="_get_local_ip_addresses")
            
            # Fallback method
            try:
                # Connect to a remote address to get local IP
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    if local_ip and local_ip not in ips:
                        ips.append(local_ip)
            except Exception:
                pass
        
        return ips
    
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
    
    def _parse_service_info(self, name: str, info: ServiceInfo) -> NetworkNode:
        """Parse mDNS service info into NetworkNode"""
        node_id = name.split('.')[0] if '.' in name else name
        
        # Parse properties
        props = {}
        if info.properties:
            for key, value in info.properties.items():
                try:
                    props[key.decode()] = value.decode()
                except:
                    props[key.decode()] = value
        
        # Parse capabilities
        capabilities = {}
        if 'capabilities' in props:
            try:
                capabilities = json.loads(props['capabilities'])
            except:
                pass
        
        # Get first available address
        address = "unknown"
        if info.addresses:
            try:
                address = socket.inet_ntoa(info.addresses[0])
            except:
                pass
        
        return NetworkNode(
            node_id=node_id,
            did=props.get('did') or None,
            address=address,
            port=info.port,
            role=props.get('role', 'unknown'),
            capabilities=capabilities,
            constitutional_version=props.get('constitutional_version', '1.0'),
            discovered_at=time.time(),
            last_seen=time.time()
        )
    
    def _validate_constitutional_compliance(self, node: NetworkNode) -> bool:
        """Validate that discovered node complies with constitutional principles"""
        
        # Check constitutional version compatibility
        if node.constitutional_version != self.constitutional_version:
            self.logger.log_violation("constitutional_version_mismatch", {
                "node_id": node.node_id,
                "node_version": node.constitutional_version,
                "required_version": self.constitutional_version
            })
            return False
        
        # Check for required decentralization indicators
        if node.role not in ['master', 'slave']:
            self.logger.log_violation("invalid_node_role", {
                "node_id": node.node_id,
                "role": node.role
            })
            return False
        
        # Validate capabilities structure
        if not isinstance(node.capabilities, dict):
            return False
        
        return True
    
    def _add_discovered_node(self, node: NetworkNode):
        """Add newly discovered node"""
        with self._lock:
            self.discovered_nodes[node.node_id] = node
            
            # Calculate initial trust level
            node.trust_level = self._calculate_trust_level(node)
            
            self.logger.info(f"Discovered HAI-Net node: {node.node_id} ({node.role}) at {node.address}", category="discovery", function="_add_discovered_node")
            
            # Notify callbacks
            for callback in self.discovery_callbacks:
                try:
                    callback(node)
                except Exception as e:
                    self.logger.error(f"Discovery callback error: {e}", category="discovery", function="_add_discovered_node")
    
    def _update_discovered_node(self, node: NetworkNode):
        """Update existing discovered node"""
        with self._lock:
            if node.node_id in self.discovered_nodes:
                existing = self.discovered_nodes[node.node_id]
                existing.last_seen = node.last_seen
                existing.capabilities = node.capabilities
                existing.trust_level = self._calculate_trust_level(existing)
    
    def _remove_discovered_node(self, node_id: str):
        """Remove discovered node"""
        with self._lock:
            if node_id in self.discovered_nodes:
                removed_node = self.discovered_nodes.pop(node_id)
                self.logger.info(f"Removed HAI-Net node: {node_id}", category="discovery", function="_remove_discovered_node")
                
                # Notify callbacks
                for callback in self.removal_callbacks:
                    try:
                        callback(node_id)
                    except Exception as e:
                        self.logger.error(f"Removal callback error: {e}", category="discovery", function="_remove_discovered_node")
    
    def _calculate_trust_level(self, node: NetworkNode) -> float:
        """Calculate trust level for a node based on constitutional compliance"""
        trust = 0.0
        
        # Base trust for constitutional compliance
        if node.constitutional_version == self.constitutional_version:
            trust += 0.5
        
        # Trust based on role
        if node.role in ['master', 'slave']:
            trust += 0.2
        
        # Trust based on capabilities
        if isinstance(node.capabilities, dict):
            trust += 0.1
        
        # Trust based on time seen
        time_known = time.time() - node.discovered_at
        if time_known > 300:  # Known for 5+ minutes
            trust += 0.1
        
        # Trust based on recent activity
        time_since_seen = time.time() - node.last_seen
        if time_since_seen < 60:  # Seen within last minute
            trust += 0.1
        
        return min(1.0, trust)
    
    def _discovery_maintenance_loop(self):
        """Background maintenance for discovery service"""
        while self.running:
            try:
                current_time = time.time()
                
                # Clean up stale nodes
                with self._lock:
                    stale_nodes = []
                    for node_id, node in self.discovered_nodes.items():
                        if current_time - node.last_seen > 300:  # 5 minutes
                            stale_nodes.append(node_id)
                    
                    for node_id in stale_nodes:
                        self._remove_discovered_node(node_id)
                
                # Sleep before next maintenance cycle
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Discovery maintenance error: {e}", category="discovery", function="_discovery_maintenance_loop")
                time.sleep(10)  # Shorter sleep on error
    
    def get_discovered_nodes(self, trusted_only: bool = True) -> List[NetworkNode]:
        """Get list of discovered nodes"""
        with self._lock:
            nodes = list(self.discovered_nodes.values())
            
            if trusted_only:
                nodes = [n for n in nodes if n.trust_level >= self.trust_threshold]
            
            return sorted(nodes, key=lambda n: n.trust_level, reverse=True)
    
    def get_node_by_id(self, node_id: str) -> Optional[NetworkNode]:
        """Get specific node by ID"""
        with self._lock:
            return self.discovered_nodes.get(node_id)
    
    def add_discovery_callback(self, callback: Callable[[NetworkNode], None]):
        """Add callback for node discovery events"""
        self.discovery_callbacks.append(callback)
    
    def add_removal_callback(self, callback: Callable[[str], None]):
        """Add callback for node removal events"""
        self.removal_callbacks.append(callback)
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        with self._lock:
            nodes = list(self.discovered_nodes.values())
            
            stats = {
                "total_nodes": len(nodes),
                "trusted_nodes": len([n for n in nodes if n.trust_level >= self.trust_threshold]),
                "master_nodes": len([n for n in nodes if n.role == 'master']),
                "slave_nodes": len([n for n in nodes if n.role == 'slave']),
                "average_trust": sum(n.trust_level for n in nodes) / max(len(nodes), 1),
                "constitutional_compliant": len([n for n in nodes if n.constitutional_version == self.constitutional_version])
            }
            
            return stats


def create_discovery_service(settings: HAINetSettings, node_id: str, did: Optional[str] = None) -> LocalDiscovery:
    """
    Create and configure a constitutional discovery service
    
    Args:
        settings: HAI-Net settings
        node_id: Unique node identifier
        did: Optional decentralized identity
        
    Returns:
        Configured LocalDiscovery instance
    """
    return LocalDiscovery(settings, node_id, did)


if __name__ == "__main__":
    # Test the discovery system
    from core.config.settings import HAINetSettings
    
    print("HAI-Net Constitutional Discovery Test")
    print("=" * 40)
    
    # Create test settings
    settings = HAINetSettings()
    
    # Create discovery service
    discovery = create_discovery_service(
        settings,
        node_id="test_node_001",
        did="did:hai:test123"
    )
    
    # Add callbacks
    def on_node_discovered(node: NetworkNode):
        print(f"🔍 Discovered: {node.node_id} ({node.role}) at {node.address}:{node.port}")
        print(f"   Trust: {node.trust_level:.2f}, Constitutional: {node.constitutional_version}")
    
    def on_node_removed(node_id: str):
        print(f"❌ Removed: {node_id}")
    
    discovery.add_discovery_callback(on_node_discovered)
    discovery.add_removal_callback(on_node_removed)
    
    try:
        # Start discovery
        if discovery.start_discovery():
            print("✅ Discovery started successfully")
            print(f"🔍 Browsing for {settings.mdns_service_name}")
            print("Press Ctrl+C to stop...")
            
            # Keep running
            while True:
                time.sleep(5)
                stats = discovery.get_discovery_stats()
                print(f"📊 Stats: {stats['total_nodes']} total, {stats['trusted_nodes']} trusted")
                
        else:
            print("❌ Failed to start discovery")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping discovery...")
        discovery.stop_discovery()
        print("✅ Discovery stopped")
    
    except Exception as e:
        print(f"❌ Discovery error: {e}")
        discovery.stop_discovery()
