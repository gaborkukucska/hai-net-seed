# START OF FILE core/web/server.py
"""
HAI-Net Web Server
Constitutional compliance: Privacy First + Human Rights + Community Focus
FastAPI web server with constitutional protection and real-time features
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError
from core.ai import LLMManager, AgentManager, ConstitutionalGuardian, MemoryManager
from core.ai.events import EventEmitter, AgentEvent, EventType
from core.storage import DatabaseManager, VectorStore
from core.network import LocalDiscovery, P2PManager, NetworkEncryption
from core.network.llm_discovery import create_llm_discovery_service

class WebServer:
    """
    Constitutional FastAPI Web Server for HAI-Net
    Serves the constitutional AI interface with privacy protection
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("web.server", settings)
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        
        # FastAPI app
        self.app = FastAPI(
            title="HAI-Net Constitutional AI",
            description="Privacy-first decentralized AI collaboration platform",
            version=self.constitutional_version,
            docs_url="/api/docs" if settings.debug_mode else None,
            redoc_url="/api/redoc" if settings.debug_mode else None
        )
        
        # Core components (will be injected)
        self.llm_manager: Optional[LLMManager] = None
        self.agent_manager: Optional[AgentManager] = None
        self.guardian: Optional[ConstitutionalGuardian] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.database_manager: Optional[DatabaseManager] = None
        self.vector_store: Optional[VectorStore] = None
        self.llm_discovery = None
        
        # WebSocket connections
        self.websocket_connections: Dict[str, WebSocket] = {}
        
        # Security
        self.security = HTTPBearer(auto_error=False)
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        # Static files and templates
        self.static_dir = Path(__file__).parent.parent.parent / "web" / "static"
        self.templates_dir = Path(__file__).parent.parent.parent / "web" / "templates"
        
        # Initialize server
        self._setup_middleware()
        self._setup_routes()
        self._setup_static_files()
    
    def _setup_middleware(self):
        """Setup middleware with constitutional compliance"""
        
        # CORS with constitutional restrictions
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Local development only
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        # Trusted hosts (decentralization: local-first)
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.local"]
        )
        
        # Constitutional logging middleware
        @self.app.middleware("http")
        async def constitutional_logging(request: Request, call_next):
            start_time = time.time()
            
            # Log request with privacy protection
            self.logger.log_privacy_event(
                "web_request",
                f"{request.method}_{request.url.path}",
                user_consent=True  # UI access implies consent
            )
            
            response = await call_next(request)
            
            # Log response time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
    
    def _setup_routes(self):
        """Setup API routes with constitutional compliance"""
        
        # Health check (both /health and /api/health for compatibility)
        @self.app.get("/health")
        @self.app.get("/api/health")
        async def health_check():
            """System health check"""
            return {
                "status": "healthy",
                "version": self.constitutional_version,
                "constitutional_compliant": True,
                "timestamp": time.time()
            }
        
        # Constitutional status
        @self.app.get("/api/constitutional/status")
        async def constitutional_status():
            """Get constitutional compliance status"""
            if not self.guardian:
                return {"error": "Constitutional Guardian not available"}
            
            status = self.guardian.get_guardian_status()
            return {
                "constitutional_status": status,
                "timestamp": time.time()
            }
        
        # Agent management
        @self.app.get("/api/agents")
        async def get_agents():
            """Get all agents with constitutional protection"""
            if not self.agent_manager:
                return {"error": "Agent manager not available"}
            
            agents = self.agent_manager.get_all_agents()
            agent_data = []
            
            for agent in agents:
                status = agent.get_status()
                # Remove sensitive information for privacy
                safe_status = {
                    "agent_id": status["agent_id"],
                    "role": status["role"],
                    "current_state": status["current_state"],
                    "capabilities": status["capabilities"],
                    "health_score": status["metrics"]["health_score"],
                    "uptime": status["uptime"],
                    "constitutional_compliant": status["constitutional_compliant"]
                }
                agent_data.append(safe_status)
            
            return {"agents": agent_data}
        
        @self.app.post("/api/agents/create")
        async def create_agent(request: Dict[str, Any]):
            """Create new agent with constitutional validation"""
            if not self.agent_manager:
                raise HTTPException(status_code=503, detail="Agent manager not available")
            
            try:
                from core.ai.agents import AgentRole
                
                role_str = request.get("role", "worker")
                role = AgentRole(role_str.lower())
                user_did = request.get("user_did")
                
                agent_id = await self.agent_manager.create_agent(role, user_did)
                
                if agent_id:
                    return {"success": True, "agent_id": agent_id}
                else:
                    raise HTTPException(status_code=400, detail="Failed to create agent")
                    
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # AI Chat interface - Routes to Agent System
        @self.app.post("/api/chat")
        async def chat_with_ai(request: Dict[str, Any]):
            """Chat with constitutional AI via Admin Agent"""
            if not self.agent_manager:
                raise HTTPException(status_code=503, detail="Agent manager not available")
            
            try:
                messages_data = request.get("messages", [])
                user_did = request.get("user_did", "did:hai:web_user")
                
                # Extract the latest user message
                user_message = ""
                if messages_data:
                    # Get the last user message
                    for msg in reversed(messages_data):
                        if msg.get("role") == "user":
                            user_message = msg.get("content", "")
                            break
                
                if not user_message:
                    raise HTTPException(status_code=400, detail="No user message provided")
                
                self.logger.debug(f"Routing chat message to Admin AI: {user_message[:50]}...", category="web", function="chat_with_ai")
                
                # Route to Agent Manager (Admin AI)
                # Note: The agent will process this asynchronously and send response via WebSocket
                # For now, we'll also try to get a direct response for backwards compatibility
                response_text = await self.agent_manager.handle_user_message(
                    user_message, 
                    user_did
                )
                
                # If we got a response, return it
                if response_text:
                    return {
                        "response": response_text,
                        "model": "admin_agent",
                        "constitutional_compliant": True,
                        "privacy_protected": True,
                        "timestamp": time.time()
                    }
                else:
                    # Agent is processing, return acknowledgment
                    return {
                        "response": "I've received your message and I'm processing it. You'll see my response shortly.",
                        "model": "admin_agent",
                        "constitutional_compliant": True,
                        "privacy_protected": True,
                        "timestamp": time.time()
                    }
                
            except Exception as e:
                self.logger.error(f"Chat API error: {e}", category="web", function="chat_with_ai")
                raise HTTPException(status_code=400, detail=str(e))
        
        # Network status
        @self.app.get("/api/network/status")
        async def network_status():
            """Get P2P network status"""
            # This would integrate with P2P manager
            return {
                "status": "local_node_active",
                "connected_peers": 0,
                "discovery_active": True,
                "constitutional_compliant": True
            }
        
        # Memory management
        @self.app.get("/api/memory/{agent_id}")
        async def get_agent_memory(agent_id: str):
            """Get agent memory summary with privacy protection"""
            if not self.memory_manager:
                raise HTTPException(status_code=503, detail="Memory manager not available")
            
            summary = await self.memory_manager.get_agent_memory_summary(agent_id)
            return {"memory_summary": summary}
        
        @self.app.post("/api/memory/{agent_id}/search")
        async def search_agent_memory(agent_id: str, request: Dict[str, Any]):
            """Search agent memory with constitutional compliance"""
            if not self.memory_manager:
                raise HTTPException(status_code=503, detail="Memory manager not available")
            
            query = request.get("query", "")
            limit = request.get("limit", 10)
            
            results = await self.memory_manager.search_memories(
                agent_id=agent_id,
                query=query,
                limit=limit
            )
            
            # Convert results to JSON-serializable format
            search_results = []
            for memory, score in results:
                search_results.append({
                    "memory_id": memory.memory_id,
                    "content": memory.content[:200] + "..." if len(memory.content) > 200 else memory.content,
                    "memory_type": memory.memory_type.value,
                    "importance": memory.importance.value,
                    "similarity_score": score,
                    "timestamp": memory.timestamp
                })
            
            return {"results": search_results}
        
        # Settings management
        @self.app.get("/settings")
        @self.app.get("/api/settings")
        async def get_settings():
            """Get non-sensitive settings"""
            return {
                "constitutional_version": self.constitutional_version,
                "privacy_mode": True,
                "local_processing": True,
                "decentralized": True,
                "community_focused": True
            }
        
        # WebSocket endpoint
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            """WebSocket connection for real-time updates"""
            await self._handle_websocket_connection(websocket, client_id)
    
    def _setup_static_files(self):
        """Setup static file serving"""
        try:
            # Create directories if they don't exist
            self.static_dir.mkdir(parents=True, exist_ok=True)
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Mount static files
            self.app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
            
            # Setup templates
            if self.templates_dir.exists():
                templates = Jinja2Templates(directory=str(self.templates_dir))
                
                @self.app.get("/", response_class=HTMLResponse)
                async def index(request: Request):
                    """Serve main UI"""
                    return templates.TemplateResponse("index.html", {"request": request})
            
        except Exception as e:
            self.logger.warning(f"Static files setup failed: {e}", category="web", function="_setup_static_files")

    async def _handle_websocket_connection(self, websocket: WebSocket, client_id: str):
        """Handle WebSocket connection with constitutional compliance"""
        await websocket.accept()
        self.websocket_connections[client_id] = websocket
        
        self.logger.log_privacy_event(
            "websocket_connected",
            f"client_{client_id}",
            user_consent=True
        )
        self.logger.debug(f"WebSocket connected: client_{client_id}", category="websocket", function="_handle_websocket_connection")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await self._handle_websocket_message(client_id, message)
                
        except WebSocketDisconnect:
            self.logger.log_privacy_event(
                "websocket_disconnected",
                f"client_{client_id}",
                user_consent=True
            )
            self.logger.debug(f"WebSocket disconnected: client_{client_id}", category="websocket", function="_handle_websocket_connection")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}", category="websocket", function="_handle_websocket_connection")
        finally:
            if client_id in self.websocket_connections:
                del self.websocket_connections[client_id]
    
    async def _handle_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = message.get("type")
        
        if message_type == "ping":
            await self._send_websocket_message(client_id, {"type": "pong", "timestamp": time.time()})
        
        elif message_type == "chat_message":
            # User sent a chat message - route to agent system
            user_message = message.get("message", "")
            user_did = message.get("user_did")
            
            if self.agent_manager and user_message:
                self.logger.debug(f"Routing chat message from client {client_id} to agent system", category="websocket", function="_handle_websocket_message")
                
                # Send message to agent manager (Admin AI)
                await self.agent_manager.handle_user_message(user_message, user_did)
                
                # Notify client that message was received
                await self._send_websocket_message(client_id, {
                    "type": "message_received",
                    "timestamp": time.time()
                })
        
        elif message_type == "subscribe_agent_updates":
            # Subscribe to agent status updates
            await self._send_websocket_message(client_id, {
                "type": "subscription_confirmed",
                "subscription": "agent_updates"
            })
        
        elif message_type == "subscribe_constitutional_updates":
            # Subscribe to constitutional compliance updates
            await self._send_websocket_message(client_id, {
                "type": "subscription_confirmed", 
                "subscription": "constitutional_updates"
            })
    
    async def _on_agent_event(self, event: AgentEvent):
        """Handle agent events and broadcast via WebSocket"""
        try:
            # FILTER: Only broadcast events from Admin agent to users
            # Internal agents (PM, Workers) should not have their events shown to users
            agent_id = event.agent_id
            
            # Check if this is an Admin agent (agent_admin_*)
            is_admin_agent = agent_id and 'admin' in agent_id.lower()
            
            # Only broadcast Admin agent events to users
            if not is_admin_agent:
                self.logger.debug(f"Filtered out non-admin agent event: {event.event_type.value} from {agent_id}", category="websocket", function="_on_agent_event")
                return
            
            # Convert event to WebSocket message
            ws_message = event.to_websocket_message()
            
            # Broadcast to all connected clients
            await self.broadcast_websocket_message(ws_message)
            
            # Log event broadcasting
            self.logger.debug(f"Broadcasted admin agent event: {event.event_type.value}", category="websocket", function="_on_agent_event")
            
        except Exception as e:
            self.logger.error(f"Error broadcasting agent event: {e}", category="websocket", function="_on_agent_event")
    
    async def _send_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to WebSocket client"""
        if client_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[client_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"WebSocket send error: {e}", category="websocket", function="_send_websocket_message")
                # Remove broken connection
                if client_id in self.websocket_connections:
                    del self.websocket_connections[client_id]
    
    async def broadcast_websocket_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        disconnected_clients = []
        
        for client_id, websocket in self.websocket_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self.websocket_connections[client_id]
    
    def inject_dependencies(self, llm_manager: Optional[LLMManager] = None,
                           agent_manager: Optional[AgentManager] = None,
                           guardian: Optional[ConstitutionalGuardian] = None,
                           memory_manager: Optional[MemoryManager] = None,
                           database_manager: Optional[DatabaseManager] = None,
                           vector_store: Optional[VectorStore] = None):
        """Inject core HAI-Net components"""
        self.llm_manager = llm_manager
        self.agent_manager = agent_manager
        self.guardian = guardian
        self.memory_manager = memory_manager
        self.database_manager = database_manager
        self.vector_store = vector_store
        
        # Subscribe to agent events for WebSocket broadcasting
        self.logger.debug(f"Checking event subscription: agent_manager={agent_manager is not None}, has_event_emitter={hasattr(agent_manager, 'event_emitter') if agent_manager else False}", category="web", function="inject_dependencies")
        
        if agent_manager and hasattr(agent_manager, 'event_emitter'):
            self.logger.debug(f"Event emitter found: {agent_manager.event_emitter}", category="web", function="inject_dependencies")
            agent_manager.event_emitter.subscribe_all(self._on_agent_event)
            self.logger.info("Subscribed to agent events for WebSocket broadcasting", category="web", function="inject_dependencies")
        else:
            self.logger.warning(f"Cannot subscribe to agent events - agent_manager: {agent_manager is not None}, has_emitter: {hasattr(agent_manager, 'event_emitter') if agent_manager else False}", category="web", function="inject_dependencies")
        
        # Start Constitutional Guardian monitoring
        if guardian:
            asyncio.create_task(self._start_guardian_monitoring())
            self.logger.info("Scheduled Constitutional Guardian monitoring startup", category="web", function="inject_dependencies")
        
        self.logger.log_decentralization_event(
            "web_server_dependencies_injected",
            local_processing=True
        )
        self.logger.debug("Web server dependencies injected", category="web", function="inject_dependencies")
    
    async def start(self, host: str = "127.0.0.1", port: int = 8000):
        """Start the web server with integrated AI discovery"""
        try:
            # Start AI discovery service first
            await self._start_ai_discovery()
            
            self.logger.log_human_rights_event(
                "web_server_starting",
                user_control=True
            )
            self.logger.info("Web server starting", category="web", function="start")
            
            # Start server
            config = uvicorn.Config(
                self.app,
                host=host,
                port=port,
                log_level="info" if self.settings.debug_mode else "warning",
                access_log=self.settings.debug_mode
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"Web server startup failed: {e}", category="web", function="start")
            await self._graceful_shutdown()
            raise
    
    async def _start_ai_discovery(self):
        """Start the AI discovery service"""
        try:
            # Create AI discovery service
            node_id = f"hai-net-{int(time.time())}"
            self.llm_discovery = create_llm_discovery_service(self.settings, node_id)
            
            # Start discovery
            if await self.llm_discovery.start_discovery():
                self.logger.info("🧠 AI discovery service started successfully", category="init", function="_start_ai_discovery")
                # Log progress after brief delay
                asyncio.create_task(self._log_discovery_progress())
            else:
                self.logger.error("Failed to start AI discovery service", category="init", function="_start_ai_discovery")
                
        except Exception as e:
            self.logger.error(f"Error starting AI discovery: {e}", category="init", function="_start_ai_discovery")
    
    async def _log_discovery_progress(self):
        """Log AI discovery progress"""
        try:
            await asyncio.sleep(8)  # Wait for discovery
            
            if self.llm_discovery:
                nodes = self.llm_discovery.get_discovered_llm_nodes(trusted_only=False, healthy_only=False)
                if nodes:
                    self.logger.info(f"🎯 AI Discovery: Found {len(nodes)} services", category="discovery", function="_log_discovery_progress")
                    for node in nodes:
                        models_info = f"{len(node.available_models)} models" if node.available_models else "models unknown"
                        self.logger.debug(f"   🤖 {node.address}:{node.port} ({models_info})", category="discovery", function="_log_discovery_progress")
                else:
                    self.logger.info("🔍 AI Discovery: No services found", category="discovery", function="_log_discovery_progress")
                    
        except Exception as e:
            self.logger.debug(f"Error logging discovery: {e}", category="discovery", function="_log_discovery_progress")
    
    async def _start_guardian_monitoring(self):
        """Start the Constitutional Guardian monitoring service"""
        try:
            if self.guardian:
                self.logger.info("🛡️ Starting Constitutional Guardian monitoring...", category="guardian", function="_start_guardian_monitoring")
                
                if await self.guardian.start_monitoring():
                    self.logger.info("✅ Constitutional Guardian monitoring active", category="guardian", function="_start_guardian_monitoring")
                    
                    # Log initial compliance status
                    await asyncio.sleep(1)
                    status = self.guardian.get_guardian_status()
                    self.logger.info(f"🎯 Constitutional Compliance Score: {status['compliance_score']:.2f}", category="guardian", function="_start_guardian_monitoring")
                else:
                    self.logger.error("❌ Failed to start Constitutional Guardian monitoring", category="guardian", function="_start_guardian_monitoring")
        except Exception as e:
            self.logger.error(f"Error starting Guardian monitoring: {e}", category="guardian", function="_start_guardian_monitoring")
    
    async def _graceful_shutdown(self):
        """Gracefully shutdown all services"""
        try:
            self.logger.info("🔄 Starting graceful shutdown...", category="web", function="_graceful_shutdown")
            
            # Stop Constitutional Guardian
            if self.guardian:
                self.logger.info("🛡️ Stopping Constitutional Guardian...", category="web", function="_graceful_shutdown")
                await self.guardian.stop_monitoring()
                self.logger.info("✅ Guardian stopped", category="web", function="_graceful_shutdown")
            
            # Stop AI discovery
            if self.llm_discovery:
                self.logger.info("🧠 Stopping AI discovery...", category="web", function="_graceful_shutdown")
                await self.llm_discovery.stop_discovery()
                self.logger.info("✅ AI discovery stopped", category="web", function="_graceful_shutdown")
            
            self.logger.info("✅ Graceful shutdown completed", category="web", function="_graceful_shutdown")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", category="web", function="_graceful_shutdown")
    
    async def stop(self):
        """Stop the web server gracefully"""
        await self._graceful_shutdown()
        
        # Close all WebSocket connections
        for client_id in list(self.websocket_connections.keys()):
            try:
                websocket = self.websocket_connections[client_id]
                await websocket.close()
            except Exception:
                pass
        
        self.websocket_connections.clear()
        
        self.logger.log_human_rights_event(
            "web_server_stopped",
            user_control=True
        )
        self.logger.info("Web server stopped", category="web", function="stop")

def create_web_server(settings: HAINetSettings) -> WebServer:
    """
    Create and configure constitutional web server
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured WebServer instance
    """
    return WebServer(settings)

if __name__ == "__main__":
    # Actually start the web server
    import asyncio
    import sys
    from core.config.settings import HAINetSettings
    from core.ai.agents import AgentManager
    from core.ai.guardian import ConstitutionalGuardian
    from core.ai.llm import LLMManager
    from core.ai.tools.executor import ToolExecutor
    from core.ai.interaction_handler import InteractionHandler
    from core.ai.workflow_manager import WorkflowManager
    from core.ai.cycle_handler import AgentCycleHandler
    
    async def start_web_server():
        print("HAI-Net Constitutional Web Server")
        print("=" * 40)
        
        # 1. Create settings from environment
        settings = HAINetSettings()
        
        # 2. Initialize all core components in the correct order
        print("🔧 Initializing HAI-Net core components...")
        guardian = ConstitutionalGuardian(settings)

        # 2.5. Start LLM discovery first
        print("🔍 Starting LLM discovery on network...")
        from core.network.llm_discovery import create_llm_discovery_service
        llm_discovery = create_llm_discovery_service(settings, f"hai-net-{int(time.time())}")
        await llm_discovery.start_discovery()
        
        # Wait for discovery to find services (network scan can take a few seconds)
        print("⏳ Waiting for network LLM discovery to complete...")
        await asyncio.sleep(6)
        
        # LLM Manager is needed by Agent Manager
        print("Initializing LLM Manager with discovered services...")
        llm_manager = LLMManager(settings)
        await llm_manager.initialize(llm_discovery=llm_discovery)

        # Memory Manager for agent memory storage
        print("Initializing Memory Manager...")
        from core.ai.memory import create_memory_manager
        memory_manager = create_memory_manager(settings)

        # Agent Manager is needed by Tool Executor
        print("Initializing Agent Manager...")
        agent_manager = AgentManager(settings, llm_manager=llm_manager, memory_manager=memory_manager)

        # Tool Executor is needed by Interaction Handler
        print("Initializing Tool Executor...")
        tool_executor = ToolExecutor(settings, agent_manager=agent_manager)

        # Handlers needed by Cycle Handler
        print("Initializing Handlers...")
        interaction_handler = InteractionHandler(settings, tool_executor)
        workflow_manager = WorkflowManager(settings)

        # Cycle Handler orchestrates agent execution
        cycle_handler = AgentCycleHandler(settings, interaction_handler, workflow_manager, guardian, 
                                         memory_manager=memory_manager)

        # 3. Wire up the dependencies for the agent manager
        print("🔗 Wiring up component dependencies...")
        agent_manager.set_handlers(cycle_handler, workflow_manager)

        # 4. Create Admin AI for the user
        print("👤 Creating Admin AI for user...")
        from core.ai.agents import AgentRole
        admin_agent_id = await agent_manager.create_agent(
            AgentRole.ADMIN,
            user_did="did:hai:local_user"
        )
        if admin_agent_id:
            print(f"✅ Admin AI created: {admin_agent_id}")
        else:
            print("⚠️ Failed to create Admin AI")

        # 5. Create and configure the web server
        web_server = create_web_server(settings)
        web_server.llm_discovery = llm_discovery  # Store discovery for later use
        web_server.inject_dependencies(
            llm_manager=llm_manager,
            agent_manager=agent_manager,
            guardian=guardian,
            memory_manager=memory_manager
        )
        
        try:
            print("✅ Web server created and configured successfully")
            print("📋 Available endpoints:")
            print("   - GET  /health")
            print("   - GET  /api/constitutional/status")
            print("   - GET  /api/agents")
            print("   - POST /api/agents/create")
            print("   - POST /api/chat")
            print("   - GET  /api/network/status")
            print("   - WS   /ws/{client_id}")

            print("\n🌐 Starting HAI-Net Constitutional Web Server...")
            print("   Web Interface: http://127.0.0.1:8000")
            print("   API Documentation: http://127.0.0.1:8000/api/docs")
            print("   Press Ctrl+C to stop")
            print("")

            # 5. Start the server
            await web_server.start(host="127.0.0.1", port=8000)

        except KeyboardInterrupt:
            # This is the expected, clean way to shut down the server.
            pass
        except Exception as e:
            print(f"❌ Web server failed during startup or operation: {e}")
            # The finally block will handle shutdown
        finally:
            print("\n🛑 Shutting down HAI-Net web server...")
            await web_server.stop()
            print("✅ Web server stopped gracefully")
    
    # Run the server
    asyncio.run(start_web_server())
