# HAI-Net Networking Module
# Constitutional P2P networking and local discovery

__version__ = "0.1.0"

from .discovery import LocalDiscovery, NetworkNode
from .p2p import P2PManager
from .encryption import NetworkEncryption

__all__ = [
    "LocalDiscovery",
    "NetworkNode", 
    "P2PManager",
    "NetworkEncryption"
]
