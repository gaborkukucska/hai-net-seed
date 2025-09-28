# HAI-Net Identity Management Module
# Decentralized Identity and Cryptographic Services

__version__ = "0.1.0"

from .did import IdentityManager, DIDGenerator
from .encryption import EncryptionManager
from .watermark import WatermarkManager

__all__ = [
    "IdentityManager",
    "DIDGenerator", 
    "EncryptionManager",
    "WatermarkManager"
]
