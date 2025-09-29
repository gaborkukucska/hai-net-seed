# START OF FILE core/network/node_manager.py
"""
HAI-Net Node Role Manager
Constitutional compliance: Decentralization Imperative (Article III)
Implements dynamic master/slave role assignment without central authority
"""

import time
import threading
import hashlib
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
import random

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.network.discovery import LocalDiscovery, NetworkNode, create_discovery_service
from core.identity.did import ConstitutionalViolationError


class NodeRole(Enum):
    """Node roles in HAI-Net hierarchy"""
    MASTER = "master"
    SLAVE = "slave"
    CANDIDATE = "candidate"  # Transitional state


class RoleChangeReason(Enum):
    """Reasons for role changes"""
    NETWORK_DISCOVERY = "network_discovery"
    MASTER_FAILURE = "master_failure" 
    RESOURCE_OPTIMIZATION = "resource_optimization"
    CONSTITUTIONAL_REQUIREMENT = "constitutional_requirement"
    USER_OVERRIDE = "user_override"


@dataclass
class NodeMetrics:
    """Metrics for node role decision making"""
    uptime: float
    cpu_cores: int
    available_memory_gb: float
    network_stability: float  # 0.0 to 1.0
    constitutional_compliance_score: float  # 0.0 to 1.0
    trust_score: float  # 0.0 to 1.0
    connected_peers: int
    last_updated: float


@dataclass
class RoleChangeEvent:
    """Record of role change for audit trail"""
    timestamp: float
    previous_role: NodeRole
    new_role: NodeRole
    reason: RoleChangeReason
    node_metrics: NodeMetrics
    network_state: Dict[str, any]


class NodeRoleManager:
    """
    Constitutional node role manager for HAI-Net
    Implements decentralized master/slave role assignment
    """
    
    def __init__(self, settings: HAINetSettings, node_id: str, did: Optional[str] = None):
        self.settings = settings
        self.node_id = node_id
        self.did = did
        self.logger = get_logger("network.node_manager", settings)
        
        # Current state
        self.current_role = NodeRole.CANDIDATE
        self.target_role = self._get_initial_target_role()
        self.role_stable_since = time.time()
        
        # Discovery integration
        self.discovery: Optional[LocalDiscovery] = None
        self.discovered_masters: Set[str] = set()
        self.discovered_slaves: Set[str] = set()
        
        # Role management
        self.role_change_callbacks: List[Callable[[RoleChangeEvent], None]] = []
        self.role_history: List[RoleChangeEvent] = []
        self.election_in_progress = False
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_masters_per_network = 3  # Constitutional limit for decentralization
        self.min_slaves_per_master = 1   # Ensure distributed workload
        
        # Threading
        self.role_thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.Lock()
        
        # Metrics tracking
        self.node_metrics = self._initialize_node_metrics()
        self.peer_metrics: Dict[str, NodeMetrics] = {}
    
    def start_role_management(self) -> bool:
        """
        Start node role management with constitutional compliance
        
        Returns:
            True if started successfully
        """
        try:
            if self.running:
                self.logger.warning("Node role manager already running")
                return True
            
            # Initialize discovery service
            self.discovery = create_discovery_service(self.settings, self.node_id, self.did)
            
            # Add discovery callbacks
            self.discovery.add_discovery_callback(self._on_node_discovered)
            self.discovery.add_removal_callback(self._on_node_removed)
            
            # Start discovery
            if not self.discovery.start_discovery():
                self.logger.error("Failed to start network discovery")
                return False
            
            # Start role management thread
            self.running = True
            self.role_thread = threading.Thread(
                target=self._role_management_loop,
                daemon=True
            )
            self.role_thread.start()
            
            self.logger.log_decentralization_event(
                "role_management_started",
                local_processing=True
            )
            self.logger.info(f"Node role manager started for {self.node_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start role management: {e}")
            return False
    
    def stop_role_management(self):
        """Stop node role management"""
        try:
            self.running = False
            
            if self.role_thread:
                self.role_thread.join(timeout=5.0)
            
            if self.discovery:
                self.discovery.stop_discovery()
            
            self.logger.log_decentralization_event(
                "role_management_stopped", 
                local_processing=True
            )
            self.logger.info("Node role manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping role management: {e}")
    
    def get_current_role(self) -> NodeRole:
        """Get current node role"""
        with self._lock:
            return self.current_role
    
    def get_role_history(self) -> List[RoleChangeEvent]:
        """Get role change history for audit trail"""
        with self._lock:
            return self.role_history.copy()
    
    def force_role_change(self, new_role: NodeRole, reason: str = "user_override") -> bool:
        """
        Force a role change (constitutional user override)
        
        Args:
            new_role: Target role
            reason: Reason for change
            
        Returns:
            True if role change was applied
        """
        try:
            with self._lock:
                if self.current_role == new_role:
                    return True
                
                # Constitutional check: Ensure user has override rights
                if not self.settings.user_override_enabled:
                    raise ConstitutionalViolationError(
                        "User override disabled - protecting user rights to system control"
                    )
                
                # Record role change
                self._record_role_change(
                    new_role,
                    RoleChangeReason.USER_OVERRIDE,
                    f"User forced role change: {reason}"
                )
                
                # Apply role change
                self._apply_role_change(new_role)
                
                self.logger.log_human_rights_event(
                    f"user_role_override: {self.current_role.value} -> {new_role.value}",
                    user_control=True
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to force role change: {e}")
            return False
    
    def get_network_status(self) -> Dict[str, any]:
        """Get current network status and role distribution"""
        with self._lock:
            discovered_nodes = self.discovery.get_discovered_nodes() if self.discovery else []
            
            masters = [n for n in discovered_nodes if n.role == "master"]
            slaves = [n for n in discovered_nodes if n.role == "slave"]
            
            return {
                "node_id": self.node_id,
                "current_role": self.current_role.value,
                "target_role": self.target_role.value,
                "role_stable_since": self.role_stable_since,
                "discovered_nodes": len(discovered_nodes),
                "masters": len(masters),
                "slaves": len(slaves),
                "master_nodes": [{"id": n.node_id, "trust": n.trust_level} for n in masters],
                "slave_nodes": [{"id": n.node_id, "trust": n.trust_level} for n in slaves],
                "election_in_progress": self.election_in_progress,
                "constitutional_compliance": True,
                "network_decentralized": len(masters) <= self.max_masters_per_network
            }
    
    def add_role_change_callback(self, callback: Callable[[RoleChangeEvent], None]):
        """Add callback for role change events"""
        self.role_change_callbacks.append(callback)
    
    def _get_initial_target_role(self) -> NodeRole:
        """Determine initial target role from configuration"""
        config_role = self.settings.node_role.lower()
        if config_role == "master":
            return NodeRole.MASTER
        elif config_role == "slave":
            return NodeRole.SLAVE
        else:
            return NodeRole.CANDIDATE
    
    def _initialize_node_metrics(self) -> NodeMetrics:
        """Initialize metrics for this node"""
        import psutil
        
        return NodeMetrics(
            uptime=time.time(),
            cpu_cores=psutil.cpu_count(),
            available_memory_gb=psutil.virtual_memory().available / (1024**3),
            network_stability=1.0,  # Start optimistic
            constitutional_compliance_score=1.0,  # We're compliant by design
            trust_score=1.0,  # Trust ourselves
            connected_peers=0,
            last_updated=time.time()
        )
    
    def _update_node_metrics(self):
        """Update current node metrics"""
        try:
            import psutil
            
            with self._lock:
                self.node_metrics.available_memory_gb = psutil.virtual_memory().available / (1024**3)
                self.node_metrics.connected_peers = len(self.discovered_masters) + len(self.discovered_slaves)
                self.node_metrics.last_updated = time.time()
                
                # Update network stability based on discovery consistency
                if self.discovery:
                    stats = self.discovery.get_discovery_stats()
                    total_nodes = stats.get("total_nodes", 0)
                    trusted_nodes = stats.get("trusted_nodes", 0)
                    
                    if total_nodes > 0:
                        self.node_metrics.network_stability = trusted_nodes / total_nodes
                    else:
                        self.node_metrics.network_stability = 1.0
                        
        except Exception as e:
            self.logger.debug(f"Failed to update node metrics: {e}")
    
    def _role_management_loop(self):
        """Main role management loop"""
        while self.running:
            try:
                # Update metrics
                self._update_node_metrics()
                
                # Determine optimal role
                optimal_role = self._determine_optimal_role()
                
                # Check if role change is needed
                if optimal_role != self.current_role and not self.election_in_progress:
                    self._initiate_role_change(optimal_role)
                
                # Clean up stale peer metrics
                self._cleanup_stale_metrics()
                
                # Sleep before next cycle
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Role management loop error: {e}")
                time.sleep(5)  # Shorter sleep on error
    
    def _determine_optimal_role(self) -> NodeRole:
        """
        Determine optimal role based on network state and constitutional principles
        
        Returns:
            Optimal role for this node
        """
        try:
            if not self.discovery:
                return self.target_role
            
            discovered_nodes = self.discovery.get_discovered_nodes(trusted_only=True)
            masters = [n for n in discovered_nodes if n.role == "master"]
            slaves = [n for n in discovered_nodes if n.role == "slave"]
            
            # Constitutional compliance: Ensure decentralization
            if len(masters) >= self.max_masters_per_network:
                # Too many masters, prefer slave role
                if self.current_role == NodeRole.MASTER:
                    # Check if we're the least suitable master
                    if self._should_demote_to_slave(masters):
                        return NodeRole.SLAVE
                else:
                    return NodeRole.SLAVE
            
            # If no masters exist, someone needs to be master
            if len(masters) == 0:
                # Use deterministic election based on node characteristics
                if self._should_become_master(discovered_nodes):
                    return NodeRole.MASTER
                else:
                    return NodeRole.SLAVE
            
            # If we're configured as master and there's room, become master
            if (self.target_role == NodeRole.MASTER and 
                len(masters) < self.max_masters_per_network and
                self._meets_master_requirements()):
                return NodeRole.MASTER
            
            # Default to slave role for decentralization
            return NodeRole.SLAVE
            
        except Exception as e:
            self.logger.error(f"Error determining optimal role: {e}")
            return self.current_role
    
    def _should_become_master(self, discovered_nodes: List[NetworkNode]) -> bool:
        """
        Determine if this node should become master using constitutional election
        
        Args:
            discovered_nodes: All discovered nodes
            
        Returns:
            True if this node should become master
        """
        # Create deterministic election based on node characteristics
        # This ensures constitutional decentralization without central authority
        
        all_candidates = [self.node_id] + [n.node_id for n in discovered_nodes]
        
        # Sort candidates by deterministic criteria
        def election_score(node_id: str) -> tuple:
            if node_id == self.node_id:
                metrics = self.node_metrics
                stability = metrics.network_stability
                resources = metrics.cpu_cores + metrics.available_memory_gb
            else:
                # Estimate other node capabilities (conservative)
                stability = 0.8
                resources = 4.0  # Assume modest resources
            
            # Create deterministic hash for tie-breaking
            hash_val = int(hashlib.sha256(node_id.encode()).hexdigest()[:8], 16)
            
            return (stability, resources, hash_val)
        
        sorted_candidates = sorted(all_candidates, key=election_score, reverse=True)
        
        # We should be master if we're the top candidate
        return sorted_candidates[0] == self.node_id
    
    def _should_demote_to_slave(self, masters: List[NetworkNode]) -> bool:
        """
        Determine if this master node should demote to slave
        
        Args:
            masters: Current master nodes
            
        Returns:
            True if this node should demote
        """
        # Find master with lowest suitability score
        master_scores = []
        
        for master in masters:
            if master.node_id == self.node_id:
                # Our score
                score = (
                    self.node_metrics.network_stability +
                    self.node_metrics.trust_score +
                    (self.node_metrics.cpu_cores / 16.0) +  # Normalize CPU
                    (self.node_metrics.available_memory_gb / 32.0)  # Normalize memory
                )
            else:
                # Estimate other master scores (conservative)
                score = (
                    master.trust_level +
                    0.8 +  # Assume good stability
                    0.5 +  # Assume modest CPU
                    0.5    # Assume modest memory
                )
            
            master_scores.append((master.node_id, score))
        
        # Sort by score (lowest first)
        master_scores.sort(key=lambda x: x[1])
        
        # We should demote if we're the lowest scoring master
        return master_scores[0][0] == self.node_id
    
    def _meets_master_requirements(self) -> bool:
        """Check if this node meets requirements to be a master"""
        return (
            self.node_metrics.cpu_cores >= 2 and
            self.node_metrics.available_memory_gb >= 2.0 and
            self.node_metrics.network_stability >= 0.7 and
            self.node_metrics.constitutional_compliance_score >= 0.9
        )
    
    def _initiate_role_change(self, new_role: NodeRole):
        """Initiate a role change process"""
        try:
            with self._lock:
                if self.election_in_progress:
                    return
                
                self.election_in_progress = True
            
            # Constitutional compliance check
            if not self._validate_role_change_constitutional(new_role):
                self.logger.log_violation("unconstitutional_role_change", {
                    "current_role": self.current_role.value,
                    "requested_role": new_role.value,
                    "reason": "Violates constitutional principles"
                })
                return
            
            # Determine reason for role change
            reason = self._determine_role_change_reason(new_role)
            
            # Record role change
            self._record_role_change(new_role, reason)
            
            # Apply role change
            self._apply_role_change(new_role)
            
        except Exception as e:
            self.logger.error(f"Failed to initiate role change: {e}")
        finally:
            with self._lock:
                self.election_in_progress = False
    
    def _validate_role_change_constitutional(self, new_role: NodeRole) -> bool:
        """Validate that role change adheres to constitutional principles"""
        
        # Ensure decentralization
        if new_role == NodeRole.MASTER:
            if self.discovery:
                discovered_nodes = self.discovery.get_discovered_nodes(trusted_only=True)
                current_masters = len([n for n in discovered_nodes if n.role == "master"])
                
                if current_masters >= self.max_masters_per_network:
                    return False
        
        # Ensure user rights are respected
        if not self.settings.user_override_enabled and self.target_role != new_role:
            # Only allow role changes that respect user configuration
            return False
        
        return True
    
    def _determine_role_change_reason(self, new_role: NodeRole) -> RoleChangeReason:
        """Determine reason for role change"""
        if len(self.discovered_masters) == 0 and new_role == NodeRole.MASTER:
            return RoleChangeReason.MASTER_FAILURE
        elif new_role == self.target_role:
            return RoleChangeReason.NETWORK_DISCOVERY
        else:
            return RoleChangeReason.RESOURCE_OPTIMIZATION
    
    def _record_role_change(self, new_role: NodeRole, reason: RoleChangeReason, details: str = ""):
        """Record role change for constitutional audit trail"""
        event = RoleChangeEvent(
            timestamp=time.time(),
            previous_role=self.current_role,
            new_role=new_role,
            reason=reason,
            node_metrics=self.node_metrics,
            network_state=self.get_network_status()
        )
        
        with self._lock:
            self.role_history.append(event)
            
            # Keep only last 100 role changes
            if len(self.role_history) > 100:
                self.role_history = self.role_history[-100:]
        
        # Log constitutional compliance
        self.logger.log_decentralization_event(
            f"role_change: {self.current_role.value} -> {new_role.value}",
            local_processing=True
        )
        
        # Notify callbacks
        for callback in self.role_change_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Role change callback error: {e}")
    
    def _apply_role_change(self, new_role: NodeRole):
        """Apply the role change"""
        previous_role = self.current_role
        
        with self._lock:
            self.current_role = new_role
            self.role_stable_since = time.time()
        
        # Update configuration if needed
        if new_role == NodeRole.MASTER:
            self.settings.node_role = "master"
        elif new_role == NodeRole.SLAVE:
            self.settings.node_role = "slave"
        
        # Restart discovery with new role
        if self.discovery:
            self.discovery.stop_discovery()
            time.sleep(1)  # Brief pause
            self.discovery.start_discovery()
        
        self.logger.info(f"Role changed: {previous_role.value} -> {new_role.value}")
    
    def _on_node_discovered(self, node: NetworkNode):
        """Handle discovery of new node"""
        try:
            with self._lock:
                if node.role == "master":
                    self.discovered_masters.add(node.node_id)
                elif node.role == "slave":
                    self.discovered_slaves.add(node.node_id)
                
                # Store peer metrics (estimated)
                self.peer_metrics[node.node_id] = NodeMetrics(
                    uptime=time.time() - node.discovered_at,
                    cpu_cores=4,  # Conservative estimate
                    available_memory_gb=4.0,  # Conservative estimate
                    network_stability=node.trust_level,
                    constitutional_compliance_score=1.0 if node.constitutional_version == self.constitutional_version else 0.5,
                    trust_score=node.trust_level,
                    connected_peers=1,  # At least connected to us
                    last_updated=time.time()
                )
            
            self.logger.info(f"Discovered {node.role} node: {node.node_id} (trust: {node.trust_level:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error handling node discovery: {e}")
    
    def _on_node_removed(self, node_id: str):
        """Handle removal of node"""
        try:
            with self._lock:
                self.discovered_masters.discard(node_id)
                self.discovered_slaves.discard(node_id)
                self.peer_metrics.pop(node_id, None)
            
            self.logger.info(f"Node removed: {node_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling node removal: {e}")
    
    def _cleanup_stale_metrics(self):
        """Clean up stale peer metrics"""
        current_time = time.time()
        stale_threshold = 300  # 5 minutes
        
        with self._lock:
            stale_nodes = []
            for node_id, metrics in self.peer_metrics.items():
                if current_time - metrics.last_updated > stale_threshold:
                    stale_nodes.append(node_id)
            
            for node_id in stale_nodes:
                self.peer_metrics.pop(node_id, None)
                self.discovered_masters.discard(node_id)
                self.discovered_slaves.discard(node_id)


def create_node_role_manager(settings: HAINetSettings, node_id: str, did: Optional[str] = None) -> NodeRoleManager:
    """
    Create and configure a constitutional node role manager
    
    Args:
        settings: HAI-Net settings
        node_id: Unique node identifier
        did: Optional decentralized identity
        
    Returns:
        Configured NodeRoleManager instance
    """
    return NodeRoleManager(settings, node_id, did)


if __name__ == "__main__":
    # Test the node role manager
    from core.config.settings import HAINetSettings
    import uuid
    
    print("HAI-Net Constitutional Node Role Manager Test")
    print("=" * 50)
    
    # Create test settings
    settings = HAINetSettings()
    
    # Create node role manager
    node_id = f"test_node_{uuid.uuid4().hex[:8]}"
    role_manager = create_node_role_manager(
        settings,
        node_id=node_id,
        did=f"did:hai:{uuid.uuid4().hex[:16]}"
    )
    
    # Add role change callback
    def on_role_changed(event: RoleChangeEvent):
        print(f"🔄 Role changed: {event.previous_role.value} -> {event.new_role.value}")
        print(f"   Reason: {event.reason.value}")
        print(f"   Trust: {event.node_metrics.trust_score:.2f}")
    
    role_manager.add_role_change_callback(on_role_changed)
    
    try:
        # Start role management
        if role_manager.start_role_management():
            print(f"✅ Role management started for {node_id}")
            print(f"🎯 Current role: {role_manager.get_current_role().value}")
            print("Press Ctrl+C to stop...")
            
            # Monitor role changes
            while True:
                time.sleep(10)
                status = role_manager.get_network_status()
                print(f"📊 Network: {status['masters']} masters, {status['slaves']} slaves")
                print(f"🔍 Role: {status['current_role']} (stable for {time.time() - status['role_stable_since']:.1f}s)")
                
        else:
            print("❌ Failed to start role management")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping role management...")
        role_manager.stop_role_management()
        print("✅ Role management stopped")
    
    except Exception as e:
        print(f"❌ Role management error: {e}")
        role_manager.stop_role_management()
