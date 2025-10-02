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
import threading
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo, ServiceListener
import aiohttp
from pathlib import Path

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


class ConstitutionalLLMListener(ServiceListener):
    """
    Service listener for LLM providers with constitutional compliance
    """
    
    def __init__(self, discovery_manager):
        self.discovery = discovery_manager
        self.logger = get_logger("network.llm_discovery")
    
    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle new LLM service discovery"""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            try:
                llm_node = self.discovery._parse_llm_service_info(name, info)
                if self.discovery._validate_llm_constitutional_compliance(llm_node):
                    # Use thread-safe method to add discovered node
                    self.discovery._add_discovered_llm_node_sync(llm_node)
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
                self.logger.error(f"Failed to process discovered LLM service: {e}")
    
    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle LLM service removal"""
        node_id = name.split('.')[0] if '.' in name else name
        self.discovery._remove_discovered_llm_node(node_id)
        self.logger.log_decentralization_event(
            f"llm_provider_removed: {node_id}",
            local_processing=True
        )
    
    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        """Handle LLM service updates"""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            try:
                llm_node = self.discovery._parse_llm_service_info(name, info)
                llm_node.last_seen = time.time()
                asyncio.create_task(self.discovery._update_discovered_llm_node(llm_node))
            except Exception as e:
                self.logger.error(f"Failed to update LLM service: {e}")


class LLMDiscovery:
    """
    Comprehensive AI Service Discovery for HAI-Net
    Constitutional compliance: Decentralization Imperative (Article III)
    
    Automatically discovers and manages connections to AI services across the local network:
    - Ollama, ComfyUI, vLLM, Text Generation WebUI, Automatic1111
    - LM Studio, TabbyAPI, llama.cpp, FastChat
    - Any OpenAI-compatible API services
    
    Uses both mDNS service discovery and aggressive network scanning
    to find AI services that give HAI-Net its distributed intelligence.
    """
    
    def __init__(self, settings: HAINetSettings, node_id: str):
        self.settings = settings
        self.node_id = node_id
        self.logger = get_logger("network.llm_discovery", settings)
        
        # Service configuration - comprehensive AI service discovery
        self.ai_service_types = {
            "_hai-llm._tcp.local.": "HAI-Net LLM",
            "_ollama._tcp.local.": "Ollama", 
            "_llamacpp._tcp.local.": "llama.cpp",
            "_vllm._tcp.local.": "vLLM",
            "_textgen._tcp.local.": "Text Generation WebUI",
            "_comfyui._tcp.local.": "ComfyUI",
            "_automatic1111._tcp.local.": "Automatic1111",
            "_fastchat._tcp.local.": "FastChat",
            "_lmstudio._tcp.local.": "LM Studio",
            "_tabbyapi._tcp.local.": "TabbyAPI",
            "_openai._tcp.local.": "OpenAI Compatible"
        }
        
        # Zeroconf instances
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self.browsers: List[ServiceBrowser] = []
        self.listener: Optional[ConstitutionalLLMListener] = None
        
        # Discovered LLM nodes
        self.discovered_llm_nodes: Dict[str, LLMNode] = {}
        self.discovery_callbacks: List[Callable[[LLMNode], None]] = []
        self.removal_callbacks: List[Callable[[str], None]] = []
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.trust_threshold = 0.6  # Higher threshold for LLM providers
        
        # Threading and async
        self.discovery_thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.Lock()
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Health monitoring
        self.health_check_interval = 30  # seconds
        self.health_timeout = 5  # seconds
    
    async def start_discovery(self) -> bool:
        """
        Start comprehensive AI service discovery across the local network
        Constitutional requirement: Local-first AI discovery
        """
        try:
            if self.running:
                self.logger.warning("AI discovery already running")
                return True
            
            # Initialize Zeroconf
            self.zeroconf = Zeroconf()
            
            # Register local AI services if we have any
            await self._register_local_ai_services()
            
            # Start mDNS browsing for AI services
            self._start_llm_browsing()
            
            # Start aggressive network scanning for non-mDNS services
            asyncio.create_task(self._start_network_scanning())
            
            # Start maintenance thread
            self.running = True
            self.discovery_thread = threading.Thread(
                target=self._discovery_maintenance_loop,
                daemon=True
            )
            self.discovery_thread.start()
            
            self.logger.log_decentralization_event(
                "ai_discovery_started",
                local_processing=True
            )
            self.logger.info("🧠 HAI-Net comprehensive AI discovery started - scanning local network for intelligence...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start AI discovery: {e}")
            return False
    
    async def _start_network_scanning(self):
        """Comprehensively scan local network for AI services that don't advertise via mDNS"""
        try:
            self.logger.info("🕵️ Starting comprehensive network scan for AI services...")
            
            # Get all possible local network ranges
            network_ranges = self._get_comprehensive_network_ranges()
            self.logger.info(f"🔍 Scanning network ranges: {network_ranges}")
            
            # Common AI service ports to scan (prioritize Ollama)
            ai_service_ports = {
                11434: "Ollama",
                8000: "vLLM/FastAPI", 
                7860: "Gradio/Automatic1111",
                8188: "ComfyUI",
                1234: "LM Studio",
                5000: "Text Generation WebUI",
                8080: "TabbyAPI"
            }
            
            # Priority scan for Ollama first (since user knows there's one)
            await self._priority_scan_ollama(network_ranges)
            
            # Create comprehensive scan tasks
            scan_tasks = []
            total_ips_to_scan = 0
            
            for network_range in network_ranges:
                ip_count = 0
                for ip in self._generate_network_ips(network_range):
                    if ip_count >= 100:  # Increased from 50
                        break
                    
                    # Prioritize Ollama port first
                    for port, service_name in ai_service_ports.items():
                        task = asyncio.create_task(
                            self._scan_ai_service(ip, port, service_name)
                        )
                        scan_tasks.append(task)
                    ip_count += 1
                    total_ips_to_scan += 1
            
            self.logger.info(f"🔍 Scanning {total_ips_to_scan} IPs across {len(network_ranges)} network ranges")
            
            # Execute scans with higher concurrency
            semaphore = asyncio.Semaphore(20)  # Increased from 10
            
            async def limited_scan(task):
                async with semaphore:
                    return await task
            
            # Process in batches to avoid overwhelming
            batch_size = 200
            total_discovered = 0
            
            for i in range(0, len(scan_tasks), batch_size):
                batch = scan_tasks[i:i + batch_size]
                self.logger.info(f"🔍 Processing scan batch {i//batch_size + 1}/{(len(scan_tasks)-1)//batch_size + 1} ({len(batch)} tasks)")
                
                results = await asyncio.gather(
                    *[limited_scan(task) for task in batch],
                    return_exceptions=True
                )
                
                batch_discovered = sum(1 for r in results if r and not isinstance(r, Exception))
                total_discovered += batch_discovered
                
                if batch_discovered > 0:
                    self.logger.info(f"🎯 Found {batch_discovered} AI services in this batch")
            
            self.logger.info(f"🎯 Network scan completed: {total_discovered} AI services discovered across {total_ips_to_scan} IPs")
            
        except Exception as e:
            self.logger.error(f"Network scanning failed: {e}")
    
    async def _priority_scan_ollama(self, network_ranges: List[str]):
        """Priority scan specifically for Ollama services"""
        try:
            self.logger.info("🎯 Priority scan for Ollama services...")
            
            priority_tasks = []
            for network_range in network_ranges:
                ip_count = 0
                for ip in self._generate_network_ips(network_range):
                    if ip_count >= 150:  # More IPs for priority scan
                        break
                    task = asyncio.create_task(
                        self._scan_ai_service(ip, 11434, "Ollama-Priority")
                    )
                    priority_tasks.append(task)
                    ip_count += 1
            
            # Fast concurrent execution for Ollama
            semaphore = asyncio.Semaphore(30)
            
            async def fast_scan(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(
                *[fast_scan(task) for task in priority_tasks],
                return_exceptions=True
            )
            
            ollama_found = sum(1 for r in results if r and not isinstance(r, Exception))
            self.logger.info(f"🎯 Priority Ollama scan completed: {ollama_found} Ollama services found")
            
        except Exception as e:
            self.logger.error(f"Priority Ollama scan failed: {e}")
    
    def _get_comprehensive_network_ranges(self) -> List[str]:
        """Get comprehensive local network IP ranges to scan"""
        ranges = set()
        
        try:
            import subprocess
            import re
            
            # Method 1: Use ip route to find network ranges
            try:
                result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    # Look for local network routes
                    if 'dev' in line and ('192.168.' in line or '10.' in line or '172.' in line):
                        # Extract network from route
                        match = re.search(r'(192\.168\.\d+\.\d+/\d+|10\.\d+\.\d+\.\d+/\d+|172\.\d+\.\d+\.\d+/\d+)', line)
                        if match:
                            ranges.add(match.group(1))
            except Exception as e:
                self.logger.debug(f"ip route method failed: {e}")
            
            # Method 2: Use hostname and socket to detect current network
            try:
                import socket
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                
                # Generate network range based on local IP
                ip_parts = local_ip.split('.')
                if ip_parts[0] == '192' and ip_parts[1] == '168':
                    ranges.add(f"192.168.{ip_parts[2]}.0/24")
                elif ip_parts[0] == '10':
                    ranges.add(f"10.{ip_parts[1]}.{ip_parts[2]}.0/24")
                elif ip_parts[0] == '172':
                    ranges.add(f"172.{ip_parts[1]}.{ip_parts[2]}.0/24")
            except Exception as e:
                self.logger.debug(f"Socket method failed: {e}")
            
            # Method 3: Check common network interfaces
            try:
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and ('192.168.' in line or '10.' in line or '172.' in line):
                        # Extract IP/CIDR
                        match = re.search(r'inet (192\.168\.\d+\.\d+/\d+|10\.\d+\.\d+\.\d+/\d+|172\.\d+\.\d+\.\d+/\d+)', line)
                        if match:
                            ip_cidr = match.group(1)
                            # Convert to network range
                            ip, cidr = ip_cidr.split('/')
                            ip_parts = ip.split('.')
                            if cidr == '24':
                                network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                                ranges.add(network)
            except Exception as e:
                self.logger.debug(f"ip addr method failed: {e}")
            
        except Exception as e:
            self.logger.debug(f"Network detection failed: {e}")
        
        # Add common ranges as fallback
        common_ranges = [
            '192.168.1.0/24',
            '192.168.0.0/24', 
            '192.168.2.0/24',
            '192.168.10.0/24',
            '192.168.100.0/24',
            '10.0.0.0/24',
            '10.0.1.0/24',
            '172.16.0.0/24'
        ]
        
        for common_range in common_ranges:
            ranges.add(common_range)
        
        # Convert to list and limit to reasonable number
        range_list = list(ranges)[:8]  # Limit to 8 ranges max
        
        return range_list
    
    def _get_local_network_ranges(self) -> List[str]:
        """Get local network IP ranges to scan"""
        ranges = []
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Generate network range based on local IP
            ip_parts = local_ip.split('.')
            if ip_parts[0] == '192' and ip_parts[1] == '168':
                ranges.append(f"192.168.{ip_parts[2]}.0/24")
            elif ip_parts[0] == '10':
                ranges.append(f"10.{ip_parts[1]}.{ip_parts[2]}.0/24")
            else:
                # Fallback to common ranges
                ranges = ['192.168.1.0/24', '192.168.0.0/24']
        except Exception as e:
            self.logger.debug(f"Failed to get network ranges: {e}")
            ranges = ['192.168.1.0/24', '192.168.0.0/24']
        
        return ranges
    
    def _generate_network_ips(self, network_range: str):
        """Generate IP addresses to scan in the network range"""
        try:
            # Simple IP generation for common ranges
            base_ip = network_range.split('/')[0]
            ip_parts = base_ip.split('.')
            base = '.'.join(ip_parts[:3])
            
            for i in range(1, 255):
                yield f"{base}.{i}"
        except Exception as e:
            self.logger.debug(f"Failed to generate IPs for {network_range}: {e}")
    
    async def _scan_ai_service(self, ip: str, port: int, service_name: str) -> Optional[LLMNode]:
        """Scan a specific IP:port for AI service"""
        try:
            # Quick port check first
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=1.0  # Very quick timeout
            )
            writer.close()
            await writer.wait_closed()
            
            # Port is open, now check if it's an AI service
            ai_node = await self._probe_ai_service(ip, port, service_name)
            if ai_node:
                await self._add_discovered_llm_node(ai_node)
                self.logger.info(f"🎯 Found {service_name} at {ip}:{port}")
                return ai_node
                
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            # Port closed or filtered - normal for most IPs
            pass
        except Exception as e:
            self.logger.debug(f"Scan error for {ip}:{port}: {e}")
        
        return None
    
    async def _probe_ai_service(self, ip: str, port: int, service_name: str) -> Optional[LLMNode]:
        """Probe an open port to see if it's an AI service"""
        try:
            # Common AI service API endpoints to try
            test_endpoints = ["/api/tags", "/v1/models", "/docs", "/health"]
            base_url = f"http://{ip}:{port}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                for endpoint in test_endpoints:
                    try:
                        async with session.get(f"{base_url}{endpoint}") as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Try to parse as AI service
                                node = await self._parse_ai_service_response(
                                    ip, port, endpoint, content, service_name
                                )
                                if node:
                                    return node
                    except:
                        continue
                        
        except Exception as e:
            self.logger.debug(f"AI service probe failed for {ip}:{port}: {e}")
        
        return None
    
    async def _parse_ai_service_response(self, ip: str, port: int, endpoint: str, 
                                       content: str, service_name: str) -> Optional[LLMNode]:
        """Parse AI service response to create LLMNode"""
        try:
            # Try to parse JSON response
            data = json.loads(content)
            
            models = []
            provider_type = LLMProvider.OLLAMA  # Default
            
            # Ollama format
            if 'models' in data and isinstance(data['models'], list):
                models = [model.get('name', model) if isinstance(model, dict) else str(model) 
                         for model in data['models']]
                provider_type = LLMProvider.OLLAMA
            
            # OpenAI compatible format
            elif 'data' in data and isinstance(data['data'], list):
                models = [model.get('id', model) if isinstance(model, dict) else str(model)
                         for model in data['data']]
                provider_type = LLMProvider.OLLAMA  # Compatible
            
            # If we found models, create a node
            if models:
                node_id = f"discovered-{ip.replace('.', '-')}-{port}"
                
                return LLMNode(
                    node_id=node_id,
                    address=ip,
                    port=port,
                    provider_type=provider_type,
                    available_models=models,
                    constitutional_version="1.0",
                    api_endpoint=f"http://{ip}:{port}",
                    health_status='healthy',
                    response_time_ms=0.0,
                    load_level=0.0,
                    trust_level=self._calculate_network_trust(ip),
                    discovered_at=time.time(),
                    last_seen=time.time(),
                    capabilities={'discovered_via': 'network_scan', 'service_hint': service_name}
                )
            
        except json.JSONDecodeError:
            # Not JSON, might be HTML - check for AI service indicators
            content_lower = content.lower()
            ai_indicators = ['ollama', 'llama', 'ai model', 'language model', 'comfy', 'automatic1111']
            
            if any(indicator in content_lower for indicator in ai_indicators):
                # Looks like an AI service UI
                node_id = f"discovered-{ip.replace('.', '-')}-{port}"
                
                return LLMNode(
                    node_id=node_id,
                    address=ip,
                    port=port,
                    provider_type=LLMProvider.OLLAMA,
                    available_models=[],  # Will be populated later
                    constitutional_version="1.0",
                    api_endpoint=f"http://{ip}:{port}",
                    health_status='healthy',
                    response_time_ms=0.0,
                    load_level=0.0,
                    trust_level=self._calculate_network_trust(ip),
                    discovered_at=time.time(),
                    last_seen=time.time(),
                    capabilities={'discovered_via': 'network_scan', 'service_hint': service_name, 'ui_detected': True}
                )
        
        except Exception as e:
            self.logger.debug(f"Failed to parse AI service response: {e}")
        
        return None
    
    def _calculate_network_trust(self, ip: str) -> float:
        """Calculate trust level for network-discovered services"""
        trust = 0.5  # Base trust
        
        # Local network gets higher trust (per user feedback)
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            trust += 0.4  # Local network services get good trust
        elif ip in ['127.0.0.1', 'localhost']:
            trust += 0.3  # Localhost services
        
        return min(1.0, trust)
    
    async def _register_local_ai_services(self) -> bool:
        """Register local AI services if available"""
        registered = False
        
        # Check for local Ollama
        if await self._register_local_llm_service():
            registered = True
        
        # TODO: Add checks for other local AI services
        # - ComfyUI, Automatic1111, Custom services
        
        return registered
    
    async def stop_discovery(self):
        """Stop LLM discovery service"""
        try:
            self.running = False
            
            if self.discovery_thread:
                self.discovery_thread.join(timeout=5.0)
            
            for browser in self.browsers:
                browser.cancel()
            self.browsers.clear()
            
            if self.service_info and self.zeroconf:
                self.zeroconf.unregister_service(self.service_info)
                self.service_info = None
            
            if self.zeroconf:
                self.zeroconf.close()
                self.zeroconf = None
            
            self.logger.log_decentralization_event(
                "llm_discovery_stopped",
                local_processing=True
            )
            self.logger.info("HAI-Net LLM discovery stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping LLM discovery: {e}")
    
    async def _register_local_llm_service(self) -> bool:
        """Register local LLM service if available"""
        try:
            # Check if local Ollama is running
            ollama_info = await self._check_local_ollama()
            if not ollama_info:
                self.logger.debug("No local Ollama service detected")
                return False
            
            # Prepare service properties, ensuring the models list fits in mDNS TXT record
            models_list = ollama_info["models"][:]  # Make a copy to avoid modifying the original

            # Truncate model list if it's too long for a single TXT record by re-serializing it until it fits
            # Max length for a single string in a TXT record is 255 bytes. We'll aim for less to be safe.
            models_json_bytes = json.dumps(models_list).encode('utf-8')
            while len(models_json_bytes) > 220 and models_list:
                models_list.pop()
                models_json_bytes = json.dumps(models_list).encode('utf-8')

            properties = {
                b"provider": b"ollama",
                b"constitutional_version": self.constitutional_version.encode(),
                b"node_id": self.node_id.encode(),
                b"models": models_json_bytes,
                b"api_version": ollama_info.get("version", "unknown").encode(),
                b"health_endpoint": b"/api/tags",
                b"privacy_compliant": b"true",
                b"local_processing": b"true"
            }
            
            # Create service info
            hai_llm_service_type = "_hai-llm._tcp.local."
            service_name = f"{self.node_id}-ollama.{hai_llm_service_type}"
            
            self.service_info = ServiceInfo(
                hai_llm_service_type,
                service_name,
                addresses=[socket.inet_aton("127.0.0.1")],
                port=ollama_info["port"],
                properties=properties,
                server=f"{self.node_id}.local."
            )
            
            # Register the service
            self.zeroconf.register_service(self.service_info)
            
            self.logger.log_privacy_event(
                "local_llm_service_registered",
                "ollama_advertisement",
                user_consent=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register local LLM service. Error: {repr(e)}, Type: {type(e).__name__}")
            return False
    
    async def _check_local_ollama(self) -> Optional[Dict[str, Any]]:
        """Check if local Ollama service is running"""
        try:
            ollama_url = self.settings.ollama_base_url if hasattr(self.settings, 'ollama_base_url') else "http://localhost:11434"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                # Check if Ollama is responding
                async with session.get(f"{ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        
                        # Get Ollama version
                        version = "unknown"
                        try:
                            async with session.get(f"{ollama_url}/api/version") as version_response:
                                if version_response.status == 200:
                                    version_data = await version_response.json()
                                    version = version_data.get("version", "unknown")
                        except Exception:
                            pass
                        
                        # Extract port from URL
                        import urllib.parse
                        parsed_url = urllib.parse.urlparse(ollama_url)
                        port = parsed_url.port or 11434
                        
                        return {
                            "models": models,
                            "version": version,
                            "port": port,
                            "endpoint": ollama_url
                        }
                        
        except Exception as e:
            self.logger.debug(f"Local Ollama check failed: {e}")
            
        return None
    
    def _start_llm_browsing(self):
        """Start browsing for all AI services on the network"""
        try:
            self.listener = ConstitutionalLLMListener(self)
            
            # Browse for all AI service types
            for service_type, service_name in self.ai_service_types.items():
                try:
                    browser = ServiceBrowser(
                        self.zeroconf,
                        service_type,
                        listener=self.listener
                    )
                    self.browsers.append(browser)
                    self.logger.debug(f"Started browsing for {service_name} services: {service_type}")
                except Exception as e:
                    self.logger.warning(f"Failed to browse for {service_name} ({service_type}): {e}")
            
            service_types_list = list(self.ai_service_types.keys())
            self.logger.info(f"🔍 Network AI discovery started for {len(service_types_list)} service types")
            self.logger.info(f"Searching for: {', '.join(self.ai_service_types.values())}")
            
        except Exception as e:
            self.logger.error(f"Failed to start network AI browsing: {e}")
    
    def _parse_llm_service_info(self, name: str, info: ServiceInfo) -> LLMNode:
        """Parse mDNS service info into LLMNode"""
        node_id = name.split('.')[0] if '.' in name else name
        
        # Parse properties
        props = {}
        if info.properties:
            for key, value in info.properties.items():
                try:
                    props[key.decode()] = value.decode()
                except:
                    props[key.decode()] = value
        
        # Parse models
        models = []
        if 'models' in props:
            try:
                models = json.loads(props['models'])
            except:
                pass
        
        # Determine provider type
        provider_type = LLMProvider.OLLAMA  # Default
        if 'provider' in props:
            provider_str = props['provider'].lower()
            if provider_str == 'ollama':
                provider_type = LLMProvider.OLLAMA
            elif provider_str == 'llamacpp':
                provider_type = LLMProvider.LLAMACPP
        
        # Get address
        address = "unknown"
        if info.addresses:
            try:
                address = socket.inet_ntoa(info.addresses[0])
            except:
                pass
        
        # Build API endpoint
        api_endpoint = f"http://{address}:{info.port}"
        
        return LLMNode(
            node_id=node_id,
            address=address,
            port=info.port,
            provider_type=provider_type,
            available_models=models,
            constitutional_version=props.get('constitutional_version', '1.0'),
            api_endpoint=api_endpoint,
            health_status='unknown',
            response_time_ms=0.0,
            load_level=0.0,
            trust_level=0.0,
            discovered_at=time.time(),
            last_seen=time.time(),
            capabilities={}
        )
    
    def _validate_llm_constitutional_compliance(self, llm_node: LLMNode) -> bool:
        """Validate that discovered LLM node complies with constitutional principles"""
        
        # Check constitutional version compatibility
        if llm_node.constitutional_version != self.constitutional_version:
            self.logger.log_violation("llm_constitutional_version_mismatch", {
                "node_id": llm_node.node_id,
                "node_version": llm_node.constitutional_version,
                "required_version": self.constitutional_version
            })
            # Allow different versions but with reduced trust
            llm_node.trust_level = max(0.0, llm_node.trust_level - 0.3)
        
        # Local providers get higher trust
        if llm_node.address in ['127.0.0.1', 'localhost']:
            llm_node.trust_level += 0.4
        
        # Providers with models get higher trust
        if llm_node.available_models:
            llm_node.trust_level += 0.2
        
        # Ensure trust level is within bounds
        llm_node.trust_level = max(0.0, min(1.0, llm_node.trust_level))
        
        return True  # Always allow but with different trust levels
    
    async def _add_discovered_llm_node(self, llm_node: LLMNode):
        """Add newly discovered LLM node (async version)"""
        with self._lock:
            self.discovered_llm_nodes[llm_node.node_id] = llm_node
            
            # Start initial health check
            await self._perform_health_check(llm_node)
            
            self.logger.info(f"Discovered LLM provider: {llm_node.node_id} ({llm_node.provider_type.value}) at {llm_node.address}:{llm_node.port}")
            self.logger.debug(f"Available models: {llm_node.available_models}")
            
            # Notify callbacks
            for callback in self.discovery_callbacks:
                try:
                    callback(llm_node)
                except Exception as e:
                    self.logger.error(f"LLM discovery callback error: {e}")
    
    def _add_discovered_llm_node_sync(self, llm_node: LLMNode):
        """Add newly discovered LLM node (synchronous version for mDNS callbacks)"""
        with self._lock:
            self.discovered_llm_nodes[llm_node.node_id] = llm_node
            
            self.logger.info(f"Discovered LLM provider: {llm_node.node_id} ({llm_node.provider_type.value}) at {llm_node.address}:{llm_node.port}")
            self.logger.debug(f"Available models: {llm_node.available_models}")
            
            # Notify callbacks
            for callback in self.discovery_callbacks:
                try:
                    callback(llm_node)
                except Exception as e:
                    self.logger.error(f"LLM discovery callback error: {e}")
    
    async def _update_discovered_llm_node(self, llm_node: LLMNode):
        """Update existing discovered LLM node"""
        with self._lock:
            if llm_node.node_id in self.discovered_llm_nodes:
                existing = self.discovered_llm_nodes[llm_node.node_id]
                existing.last_seen = llm_node.last_seen
                existing.available_models = llm_node.available_models
                existing.capabilities = llm_node.capabilities
    
    def _remove_discovered_llm_node(self, node_id: str):
        """Remove discovered LLM node"""
        with self._lock:
            if node_id in self.discovered_llm_nodes:
                removed_node = self.discovered_llm_nodes.pop(node_id)
                self.logger.info(f"Removed LLM provider: {node_id}")
                
                # Notify callbacks
                for callback in self.removal_callbacks:
                    try:
                        callback(node_id)
                    except Exception as e:
                        self.logger.error(f"LLM removal callback error: {e}")
    
    async def _perform_health_check(self, llm_node: LLMNode):
        """Perform health check on LLM node"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.health_timeout)) as session:
                # Check health endpoint
                health_url = f"{llm_node.api_endpoint}/api/tags"
                
                async with session.get(health_url) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        llm_node.health_status = 'healthy'
                        llm_node.response_time_ms = response_time
                        llm_node.trust_level = min(1.0, llm_node.trust_level + 0.1)
                        
                        # Update models if available
                        try:
                            data = await response.json()
                            models = [model["name"] for model in data.get("models", [])]
                            if models:
                                llm_node.available_models = models
                        except:
                            pass
                            
                    else:
                        llm_node.health_status = 'degraded'
                        llm_node.response_time_ms = response_time
                        llm_node.trust_level = max(0.0, llm_node.trust_level - 0.2)
                        
        except Exception as e:
            llm_node.health_status = 'offline'
            llm_node.response_time_ms = float('inf')
            llm_node.trust_level = max(0.0, llm_node.trust_level - 0.3)
            self.logger.debug(f"Health check failed for {llm_node.node_id}: {e}")
    
    def _discovery_maintenance_loop(self):
        """Background maintenance for LLM discovery service"""
        while self.running:
            try:
                # Run maintenance in async context
                if self.loop is None:
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)
                
                self.loop.run_until_complete(self._maintenance_cycle())
                
                # Sleep before next maintenance cycle
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"LLM discovery maintenance error: {e}")
                time.sleep(10)  # Shorter sleep on error
    
    async def _maintenance_cycle(self):
        """Perform maintenance tasks"""
        current_time = time.time()
        
        with self._lock:
            stale_nodes = []
            
            for node_id, llm_node in self.discovered_llm_nodes.items():
                # Remove stale nodes (not seen for 5 minutes)
                if current_time - llm_node.last_seen > 300:
                    stale_nodes.append(node_id)
                    continue
                
                # Perform health check
                await self._perform_health_check(llm_node)
            
            # Remove stale nodes
            for node_id in stale_nodes:
                self._remove_discovered_llm_node(node_id)
    
    def get_discovered_llm_nodes(self, trusted_only: bool = True, healthy_only: bool = True) -> List[LLMNode]:
        """Get list of discovered LLM nodes"""
        with self._lock:
            nodes = list(self.discovered_llm_nodes.values())
            
            if trusted_only:
                nodes = [n for n in nodes if n.trust_level >= self.trust_threshold]
            
            if healthy_only:
                nodes = [n for n in nodes if n.health_status == 'healthy']
            
            # Sort by trust level and response time
            nodes.sort(key=lambda n: (n.trust_level, -n.response_time_ms), reverse=True)
            
            return nodes
    
    def get_llm_node_by_id(self, node_id: str) -> Optional[LLMNode]:
        """Get specific LLM node by ID"""
        with self._lock:
            return self.discovered_llm_nodes.get(node_id)
    
    def get_best_llm_node_for_model(self, model_name: str) -> Optional[LLMNode]:
        """Get the best LLM node that has the specified model"""
        available_nodes = self.get_discovered_llm_nodes(trusted_only=True, healthy_only=True)
        
        # Filter nodes that have the requested model
        matching_nodes = [
            node for node in available_nodes 
            if model_name in node.available_models
        ]
        
        if not matching_nodes:
            return None
        
        # Return the highest trust, lowest latency node
        return matching_nodes[0]
    
    def get_available_models(self) -> List[str]:
        """Get all available models across discovered nodes"""
        models = set()
        
        for llm_node in self.get_discovered_llm_nodes(trusted_only=True, healthy_only=True):
            models.update(llm_node.available_models)
        
        return sorted(list(models))
    
    def add_discovery_callback(self, callback: Callable[[LLMNode], None]):
        """Add callback for LLM node discovery events"""
        self.discovery_callbacks.append(callback)
    
    def add_removal_callback(self, callback: Callable[[str], None]):
        """Add callback for LLM node removal events"""
        self.removal_callbacks.append(callback)
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get LLM discovery statistics"""
        with self._lock:
            nodes = list(self.discovered_llm_nodes.values())
            trusted_nodes = [n for n in nodes if n.trust_level >= self.trust_threshold]
            healthy_nodes = [n for n in nodes if n.health_status == 'healthy']
            
            stats = {
                "total_llm_nodes": len(nodes),
                "trusted_llm_nodes": len(trusted_nodes),
                "healthy_llm_nodes": len(healthy_nodes),
                "total_models": len(self.get_available_models()),
                "average_trust": sum(n.trust_level for n in nodes) / max(len(nodes), 1),
                "average_response_time": sum(n.response_time_ms for n in healthy_nodes) / max(len(healthy_nodes), 1),
                "provider_types": list(set(n.provider_type.value for n in nodes))
            }
            
            return stats


def create_llm_discovery_service(settings: HAINetSettings, node_id: str) -> LLMDiscovery:
    """
    Create and configure a constitutional LLM discovery service
    
    Args:
        settings: HAI-Net settings
        node_id: Unique node identifier
        
    Returns:
        Configured LLMDiscovery instance
    """
    return LLMDiscovery(settings, node_id)


if __name__ == "__main__":
    # Test the LLM discovery system
    import asyncio
    from core.config.settings import HAINetSettings
    
    async def test_llm_discovery():
        print("HAI-Net Constitutional LLM Discovery Test")
        print("=" * 45)
        
        # Create test settings
        settings = HAINetSettings()
        
        # Create LLM discovery service
        discovery = create_llm_discovery_service(settings, "test_node_001")
        
        # Add callbacks
        def on_llm_discovered(llm_node: LLMNode):
            print(f"🔍 Discovered LLM: {llm_node.node_id} ({llm_node.provider_type.value})")
            print(f"   Address: {llm_node.address}:{llm_node.port}")
            print(f"   Models: {llm_node.available_models}")
            print(f"   Trust: {llm_node.trust_level:.2f}, Health: {llm_node.health_status}")
        
        def on_llm_removed(node_id: str):
            print(f"❌ Removed LLM: {node_id}")
        
        discovery.add_discovery_callback(on_llm_discovered)
        discovery.add_removal_callback(on_llm_removed)
        
        try:
            # Start discovery
            if await discovery.start_discovery():
                print("✅ LLM discovery started successfully")
                print("🔍 Searching for LLM providers...")
                print("Press Ctrl+C to stop...")
                
                # Keep running and show stats
                for i in range(60):  # Run for 1 minute
                    await asyncio.sleep(5)
                    stats = discovery.get_discovery_stats()
                    models = discovery.get_available_models()
                    print(f"📊 Stats: {stats['total_llm_nodes']} nodes, {stats['total_models']} models, {len(models)} unique")
                    
                    if models:
                        print(f"   Models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                
            else:
                print("❌ Failed to start LLM discovery")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping LLM discovery...")
        finally:
            await discovery.stop_discovery()
            print("✅ LLM discovery stopped")
    
    # Run the test
    asyncio.run(test_llm_discovery())
