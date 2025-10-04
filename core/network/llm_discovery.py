# START OF FILE core/network/llm_discovery.py
"""
HAI-Net LLM Provider Discovery
Constitutional compliance: Decentralization Imperative (Article III)
Discovers local network LLM providers for constitutional AI collaboration
"""

import asyncio
import json
import time
import socket
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf, AsyncServiceInfo
import aiohttp
from pathlib import Path
import netifaces

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.network.discovery import NetworkNode
from core.ai.llm import LLMProvider, LLMModelInfo


@dataclass
class LLMNode:
    """Represents a discovered LLM provider node"""
    node_id: str
    address: str
    port: int
    provider_type: LLMProvider
    available_models: List[str]
    constitutional_version: str
    api_endpoint: str
    health_status: str  # 'healthy', 'degraded', 'offline'
    response_time_ms: float
    load_level: float  # 0.0 to 1.0
    trust_level: float  # 0.0 to 1.0
    discovered_at: float
    last_seen: float
    capabilities: Dict[str, Any]


class ConstitutionalLLMListener:
    """
    Async service listener for LLM providers with constitutional compliance.
    This class must implement both async and sync methods for compatibility.
    """

    def __init__(self, discovery_manager: 'LLMDiscovery'):
        self.discovery = discovery_manager
        self.logger = get_logger("network.llm_discovery")

    async def async_add_service(self, zeroconf: AsyncZeroconf, service_type: str, name: str) -> None:
        """Handle new LLM service discovery asynchronously."""
        info = await zeroconf.async_get_service_info(service_type, name)
        if info:
            try:
                llm_node = self.discovery._parse_llm_service_info(name, info)
                if self.discovery._validate_llm_constitutional_compliance(llm_node):
                    await self.discovery._add_discovered_llm_node(llm_node)
                    self.logger.log_decentralization_event(
                        f"llm_provider_discovered: {llm_node.node_id}",
                        local_processing=True
                    )
                else:
                    self.logger.log_violation("llm_constitutional_non_compliance", {
                        "node_id": llm_node.node_id,
                        "reason": "Failed constitutional validation"
                    })
            except Exception as e:
                self.logger.error(f"Failed to process discovered LLM service: {e}", exc_info=True)

    async def async_remove_service(self, zeroconf: AsyncZeroconf, service_type: str, name: str) -> None:
        """Handle LLM service removal asynchronously."""
        node_id = name.split('.')[0] if '.' in name else name
        await self.discovery._remove_discovered_llm_node(node_id)
        self.logger.log_decentralization_event(
            f"llm_provider_removed: {node_id}",
            local_processing=True
        )

    async def async_update_service(self, zeroconf: AsyncZeroconf, service_type: str, name: str) -> None:
        """Handle LLM service updates asynchronously."""
        info = await zeroconf.async_get_service_info(service_type, name)
        if info:
            try:
                llm_node = self.discovery._parse_llm_service_info(name, info)
                llm_node.last_seen = time.time()
                await self.discovery._update_discovered_llm_node(llm_node)
            except Exception as e:
                self.logger.error(f"Failed to update LLM service: {e}", exc_info=True)

    # Synchronous shims for compatibility
    def add_service(self, zeroconf: AsyncZeroconf, service_type: str, name: str) -> None:
        """Shim for older zeroconf versions."""
        asyncio.create_task(self.async_add_service(zeroconf, service_type, name))

    def remove_service(self, zeroconf: AsyncZeroconf, service_type: str, name: str) -> None:
        """Shim for older zeroconf versions."""
        asyncio.create_task(self.async_remove_service(zeroconf, service_type, name))

    def update_service(self, zeroconf: AsyncZeroconf, service_type: str, name: str) -> None:
        """Shim for older zeroconf versions."""
        asyncio.create_task(self.async_update_service(zeroconf, service_type, name))


class LLMDiscovery:
    """
    Comprehensive AI Service Discovery for HAI-Net
    Constitutional compliance: Decentralization Imperative (Article III)
    
    Automatically discovers and manages connections to AI services across the local network.
    """
    
    def __init__(self, settings: HAINetSettings, node_id: str):
        self.settings = settings
        self.node_id = node_id
        self.logger = get_logger("network.llm_discovery", settings)
        
        self.ai_service_types = {
            "_hai-llm._tcp.local.": "HAI-Net LLM",
            "_ollama._tcp.local.": "Ollama",
        }
        
        self.aiozc: Optional[AsyncZeroconf] = None
        self.service_info: Optional[AsyncServiceInfo] = None
        self.browser: Optional[AsyncServiceBrowser] = None
        
        self.discovered_llm_nodes: Dict[str, LLMNode] = {}
        self.discovery_callbacks: List[Callable[[LLMNode], None]] = []
        self.removal_callbacks: List[Callable[[str], None]] = []
        
        self.constitutional_version = "1.0"
        self.trust_threshold = 0.6
        
        self.running = False
        self._lock = asyncio.Lock()
        self.maintenance_task: Optional[asyncio.Task] = None
        
        self.health_check_interval = 60
        self.health_timeout = 5
    
    async def start_discovery(self) -> bool:
        """Start comprehensive AI service discovery using modern asyncio."""
        try:
            if self.running:
                self.logger.warning("AI discovery already running")
                return True

            self.aiozc = AsyncZeroconf()
            await self._register_local_llm_service()
            
            self.browser = AsyncServiceBrowser(
                self.aiozc.zeroconf,
                list(self.ai_service_types.keys()),
                listener=ConstitutionalLLMListener(self)
            )
            
            self.running = True
            self.maintenance_task = asyncio.create_task(self._discovery_maintenance_loop())
            asyncio.create_task(self._start_network_scanning())
            
            self.logger.log_decentralization_event("ai_discovery_started", local_processing=True)
            self.logger.info("🧠 HAI-Net comprehensive AI discovery started.")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start AI discovery: {e}", exc_info=True)
            return False
    
    async def stop_discovery(self):
        """Stop LLM discovery service."""
        try:
            self.running = False
            if self.maintenance_task:
                self.maintenance_task.cancel()
                try:
                    await self.maintenance_task
                except asyncio.CancelledError:
                    pass

            if self.browser:
                await self.browser.async_cancel()
                self.browser = None
            
            if self.service_info and self.aiozc:
                await self.aiozc.async_unregister_service(self.service_info)
                self.service_info = None

            if self.aiozc:
                await self.aiozc.async_close()
                self.aiozc = None
            
            self.logger.log_decentralization_event("llm_discovery_stopped", local_processing=True)
            self.logger.info("HAI-Net LLM discovery stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping LLM discovery: {e}", exc_info=True)

    async def _start_network_scanning(self):
        """Asynchronously scans the local network for potential AI services."""
        self.logger.info("Starting network scan for non-mDNS AI services...")
        network_ranges = self._get_comprehensive_network_ranges()
        tasks = []
        for network_range in network_ranges:
            # This is a simplified implementation assuming a /24 subnet
            base_ip = ".".join(network_range.split('.')[:-1])
            for i in range(1, 255):
                ip = f"{base_ip}.{i}"
                # Scan for Ollama on its default port
                tasks.append(self._scan_ai_service(ip, 11434, "Ollama"))

        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info("Network scan for AI services complete.")

    def _get_comprehensive_network_ranges(self) -> List[str]:
        """Gets a list of local network ranges to scan using netifaces."""
        ranges = set()
        try:
            for interface in netifaces.interfaces():
                ifaddresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in ifaddresses:
                    for link in ifaddresses[netifaces.AF_INET]:
                        ip = link.get('addr')
                        if ip and not ip.startswith("127."):
                            base_ip = ".".join(ip.split('.')[:-1])
                            ranges.add(f"{base_ip}.0/24")
        except Exception as e:
            self.logger.error(f"Could not determine network ranges via netifaces: {e}")

        if not ranges:
            ranges.add("192.168.1.0/24") # Default fallback for common home networks

        self.logger.debug(f"Network ranges to scan: {list(ranges)}")
        return list(ranges)

    async def _scan_ai_service(self, ip: str, port: int, service_name: str):
        """Probes a single IP:port to see if it's a connectable service."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=1.5
            )
            writer.close()
            await writer.wait_closed()

            self.logger.info(f"Potential '{service_name}' service found at {ip}:{port}. Probing API.")
            if service_name == "Ollama":
                await self._probe_ollama_endpoint(ip, port)
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            pass # This is expected for most IPs
        except Exception as e:
            self.logger.debug(f"Error scanning {ip}:{port}: {e}")

    async def _probe_ollama_endpoint(self, ip: str, port: int):
        """Probes a potential Ollama endpoint and registers it if valid."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                async with session.get(f"http://{ip}:{port}/api/tags") as response:
                    if response.status == 200:
                        self.logger.info(f"Confirmed Ollama service at {ip}:{port}. Registering as a node.")
                        # Manually construct an LLMNode for the discovered service
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]

                        node_id = f"ollama-scan-{ip.replace('.', '-')}"

                        # Avoid duplicating if already found by mDNS
                        async with self._lock:
                            if node_id in self.discovered_llm_nodes:
                                return

                        llm_node = LLMNode(
                            node_id=node_id,
                            address=ip,
                            port=port,
                            provider_type=LLMProvider.OLLAMA,
                            available_models=models,
                            constitutional_version=self.constitutional_version,
                            api_endpoint=f"http://{ip}:{port}",
                            health_status='healthy',
                            response_time_ms=100.0, # Placeholder
                            load_level=0.0, # Placeholder
                            trust_level=0.7, # Scanned nodes are reasonably trusted
                            discovered_at=time.time(),
                            last_seen=time.time(),
                            capabilities={}
                        )
                        await self._add_discovered_llm_node(llm_node)

        except Exception as e:
            self.logger.debug(f"Failed to probe confirmed Ollama endpoint at {ip}:{port}: {e}")
    
    async def _register_local_llm_service(self) -> bool:
        """Register local LLM service if available."""
        try:
            ollama_info = await self._check_local_ollama()
            if not ollama_info:
                self.logger.debug("No local Ollama service detected")
                return False
            
            models_list = ollama_info["models"][:]
            models_json_bytes = json.dumps(models_list).encode('utf-8')
            while len(models_json_bytes) > 220 and models_list:
                models_list.pop()
                models_json_bytes = json.dumps(models_list).encode('utf-8')

            properties = {
                "provider": "ollama",
                "constitutional_version": self.constitutional_version,
                "node_id": self.node_id,
                "models": models_json_bytes.decode('utf-8'),
                "api_version": ollama_info.get("version", "unknown"),
            }
            
            self.service_info = AsyncServiceInfo(
                "_hai-llm._tcp.local.",
                f"{self.node_id}-ollama._hai-llm._tcp.local.",
                addresses=[socket.inet_aton("127.0.0.1")],
                port=ollama_info["port"],
                properties=properties,
                server=f"{self.node_id}.local."
            )
            
            await self.aiozc.async_register_service(self.service_info)
            self.logger.log_privacy_event("local_llm_service_registered", "ollama_advertisement", user_consent=True)
            return True
            
        except Exception as e:
            import traceback
            self.logger.error(f"Failed to register local LLM service. Error: {repr(e)}, Type: {type(e).__name__}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    async def _check_local_ollama(self) -> Optional[Dict[str, Any]]:
        """Check if local Ollama service is running."""
        try:
            ollama_url = self.settings.ollama_base_url if hasattr(self.settings, 'ollama_base_url') else "http://localhost:11434"
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(f"{ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        parsed_url = aiohttp.helpers.parse_url(ollama_url)
                        return {"models": models, "port": parsed_url.port or 11434}
        except Exception as e:
            self.logger.debug(f"Local Ollama check failed: {e}")
        return None
    
    def _parse_llm_service_info(self, name: str, info: AsyncServiceInfo) -> LLMNode:
        """Parse mDNS service info into LLMNode"""
        node_id = name.split('.')[0]
        props = {key.decode('utf-8'): value.decode('utf-8') for key, value in info.properties.items()}
        models = json.loads(props.get('models', '[]'))
        address = socket.inet_ntoa(info.addresses[0]) if info.addresses else "unknown"
        
        return LLMNode(
            node_id=node_id,
            address=address,
            port=info.port,
            provider_type=LLMProvider(props.get('provider', 'ollama')),
            available_models=models,
            constitutional_version=props.get('constitutional_version', '1.0'),
            api_endpoint=f"http://{address}:{info.port}",
            health_status='unknown',
            response_time_ms=0.0,
            load_level=0.0,
            trust_level=0.5,
            discovered_at=time.time(),
            last_seen=time.time(),
            capabilities={}
        )
    
    def _validate_llm_constitutional_compliance(self, llm_node: LLMNode) -> bool:
        """Validate discovered LLM node."""
        return True

    async def _add_discovered_llm_node(self, llm_node: LLMNode):
        """Add newly discovered LLM node."""
        async with self._lock:
            self.discovered_llm_nodes[llm_node.node_id] = llm_node
            await self._perform_health_check(llm_node)
            self.logger.info(f"Discovered LLM provider: {llm_node.node_id}")
            for callback in self.discovery_callbacks:
                callback(llm_node)
    
    async def _update_discovered_llm_node(self, llm_node: LLMNode):
        """Update existing discovered LLM node."""
        async with self._lock:
            if llm_node.node_id in self.discovered_llm_nodes:
                self.discovered_llm_nodes[llm_node.node_id] = llm_node
    
    async def _remove_discovered_llm_node(self, node_id: str):
        """Remove discovered LLM node."""
        async with self._lock:
            if node_id in self.discovered_llm_nodes:
                self.discovered_llm_nodes.pop(node_id, None)
                self.logger.info(f"Removed LLM provider: {node_id}")
                for callback in self.removal_callbacks:
                    callback(node_id)
    
    async def _perform_health_check(self, llm_node: LLMNode):
        """Perform health check on LLM node"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.health_timeout)) as session:
                async with session.get(f"{llm_node.api_endpoint}/api/tags") as response:
                    if response.status == 200:
                        llm_node.health_status = 'healthy'
                    else:
                        llm_node.health_status = 'degraded'
        except Exception:
            llm_node.health_status = 'offline'

    async def _discovery_maintenance_loop(self):
        """Asynchronous background maintenance for LLM discovery service."""
        while self.running:
            await asyncio.sleep(self.health_check_interval)
            async with self._lock:
                nodes_to_check = list(self.discovered_llm_nodes.values())

            await asyncio.gather(*[self._perform_health_check(node) for node in nodes_to_check])

            stale_node_ids = [
                node.node_id for node in nodes_to_check
                if time.time() - node.last_seen > 300
            ]
            for node_id in stale_node_ids:
                await self._remove_discovered_llm_node(node_id)
    
    def get_discovered_llm_nodes(self, **kwargs) -> List[LLMNode]:
        return list(self.discovered_llm_nodes.values())

def create_llm_discovery_service(settings: HAINetSettings, node_id: str) -> LLMDiscovery:
    return LLMDiscovery(settings, node_id)