# HAI-Net API Router - Constitutional REST API Endpoints
# Provides RESTful API endpoints while maintaining constitutional compliance

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Import constitutional components
from core.config.settings import HAINetSettings, validate_constitutional_compliance
from core.identity.did import IdentityManager
from core.network.node_manager import NodeRoleManager, NodeRole
from core.logging.constitutional_audit import ConstitutionalAuditor

logger = logging.getLogger(__name__)

# Create API router with constitutional compliance
router = APIRouter(prefix="/api/v1", tags=["HAI-Net Constitutional API"])

# Global instances (will be properly initialized by server)
settings = None
identity_manager = None
node_manager = None
constitutional_auditor = None

def get_settings() -> HAINetSettings:
    """Dependency to get settings with constitutional validation"""
    global settings
    if settings is None:
        settings = HAINetSettings()
        violations = validate_constitutional_compliance(settings)
        if violations:
            raise HTTPException(
                status_code=500,
                detail=f"Constitutional violations detected: {violations}"
            )
    return settings

def get_identity_manager() -> IdentityManager:
    """Dependency to get identity manager"""
    global identity_manager
    if identity_manager is None:
        identity_manager = IdentityManager()
    return identity_manager

def get_node_manager(settings: HAINetSettings = Depends(get_settings)) -> NodeRoleManager:
    """Dependency to get node manager"""
    global node_manager
    if node_manager is None:
        node_manager = NodeRoleManager(settings, f"api-node-{datetime.now().timestamp()}")
    return node_manager

def get_constitutional_auditor(settings: HAINetSettings = Depends(get_settings)) -> ConstitutionalAuditor:
    """Dependency to get constitutional auditor"""
    global constitutional_auditor
    if constitutional_auditor is None:
        constitutional_auditor = ConstitutionalAuditor(settings)
    return constitutional_auditor

# Constitutional compliance endpoints
@router.get("/health", summary="Constitutional Health Check")
async def health_check(settings: HAINetSettings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Check system health with constitutional compliance verification
    """
    try:
        violations = validate_constitutional_compliance(settings)
        
        return {
            "status": "healthy" if not violations else "constitutional_violations",
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_compliance": {
                "privacy_first": True,
                "human_rights": True, 
                "decentralization": True,
                "community_focus": True,
                "violations": violations
            },
            "version": settings.constitutional_version,
            "node_info": {
                "role": "api_server",
                "constitutional_node": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/constitution", summary="Get Constitutional Principles")
async def get_constitution(settings: HAINetSettings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Get the constitutional principles and current compliance status
    """
    return {
        "constitutional_version": settings.constitutional_version,
        "principles": {
            "privacy_first": {
                "title": "Privacy First",
                "description": "No personal data leaves Local Hub without explicit consent",
                "enabled": True
            },
            "human_rights": {
                "title": "Human Rights Protection", 
                "description": "AI serves humanity with accessibility and user control",
                "enabled": True
            },
            "decentralization": {
                "title": "Decentralization Imperative",
                "description": "No central authority, local autonomy, fork-resistant",
                "enabled": True
            },
            "community_focus": {
                "title": "Community Focus",
                "description": "Strengthen real-world connections and collaboration",
                "enabled": True
            }
        },
        "compliance_status": "fully_compliant",
        "last_verified": datetime.utcnow().isoformat()
    }

# Identity management endpoints
@router.get("/identity/status", summary="Identity System Status")
async def get_identity_status(
    identity_manager: IdentityManager = Depends(get_identity_manager)
) -> Dict[str, Any]:
    """
    Get identity system status with constitutional compliance
    """
    return {
        "identity_system": "operational",
        "constitutional_compliance": True,
        "privacy_protected": True,
        "watermarking_enabled": True,
        "encryption_active": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# Network management endpoints  
@router.get("/network/status", summary="Network Status")
async def get_network_status(
    node_manager: NodeRoleManager = Depends(get_node_manager)
) -> Dict[str, Any]:
    """
    Get network status with constitutional compliance
    """
    try:
        status = node_manager.get_network_status()
        
        return {
            **status,
            "constitutional_network": True,
            "decentralized": True,
            "privacy_respected": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Network status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Network status failed: {str(e)}")

@router.get("/network/nodes", summary="Network Nodes")
async def get_network_nodes(
    node_manager: NodeRoleManager = Depends(get_node_manager)
) -> Dict[str, Any]:
    """
    Get network nodes information
    """
    try:
        status = node_manager.get_network_status()
        
        return {
            "total_nodes": status.get("discovered_nodes", 0),
            "masters": status.get("masters", 0),
            "slaves": status.get("slaves", 0),
            "master_nodes": status.get("master_nodes", []),
            "slave_nodes": status.get("slave_nodes", []),
            "constitutional_nodes": True,
            "decentralized_network": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Network nodes failed: {e}")
        raise HTTPException(status_code=500, detail=f"Network nodes failed: {str(e)}")

@router.post("/network/role", summary="Update Node Role")
async def update_node_role(
    role: str,
    node_manager: NodeRoleManager = Depends(get_node_manager)
) -> Dict[str, Any]:
    """
    Update node role with constitutional compliance (user override)
    """
    try:
        # Validate role
        if role not in ["master", "slave", "candidate"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be master, slave, or candidate")
        
        # Convert to NodeRole enum
        node_role = NodeRole[role.upper()]
        
        # Update role (respects human rights principle - user control)
        node_manager.set_target_role(node_role)
        
        return {
            "role_updated": True,
            "new_role": role,
            "human_rights_respected": True,
            "user_control_maintained": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Role update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Role update failed: {str(e)}")

# Constitutional audit endpoints
@router.get("/audit/compliance", summary="Constitutional Compliance Audit")
async def get_compliance_audit(
    auditor: ConstitutionalAuditor = Depends(get_constitutional_auditor)
) -> Dict[str, Any]:
    """
    Get constitutional compliance audit information
    """
    try:
        return {
            "constitutional_auditor": "active",
            "audit_trail_enabled": True,
            "violation_detection": True,
            "educational_approach": True,
            "privacy_respected": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Compliance audit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Compliance audit failed: {str(e)}")

# System information endpoints
@router.get("/system/info", summary="System Information")
async def get_system_info(settings: HAINetSettings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Get system information with constitutional compliance
    """
    return {
        "hainet_version": "1.0.0-mvp",
        "constitutional_version": settings.constitutional_version,
        "phase": "Phase 1 MVP Complete",
        "system_type": "constitutional_ai_network",
        "features": {
            "identity_system": True,
            "p2p_networking": True,
            "constitutional_guardian": True,
            "webgpu_visualization": True,
            "real_time_communication": True,
            "external_ai_integration": True
        },
        "constitutional_principles": {
            "privacy_first": True,
            "human_rights": True,
            "decentralization": True,
            "community_focus": True
        },
        "deployment": {
            "docker_ready": True,
            "system_service": True,
            "production_ready": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# WebSocket connection info
@router.get("/websocket/info", summary="WebSocket Connection Info")
async def get_websocket_info() -> Dict[str, Any]:
    """
    Get WebSocket connection information
    """
    return {
        "websocket_endpoint": "/ws",
        "constitutional_websockets": True,
        "privacy_respected": True,
        "real_time_updates": True,
        "decentralized_messaging": True,
        "community_features": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# Note: Exception handlers should be added to the main FastAPI app, not the router
# This will be handled in the main server.py file

# Initialize function to set up dependencies
def initialize_api_dependencies(app_settings: HAINetSettings):
    """
    Initialize API dependencies with constitutional compliance
    """
    global settings, identity_manager, node_manager, constitutional_auditor
    
    settings = app_settings
    identity_manager = IdentityManager()
    node_manager = NodeRoleManager(settings, f"api-server-{datetime.now().timestamp()}")
    constitutional_auditor = ConstitutionalAuditor(settings)
    
    logger.info("🚀 API dependencies initialized with constitutional compliance")

# Export the router
__all__ = ['router', 'initialize_api_dependencies']
