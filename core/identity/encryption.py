"""
HAI-Net Identity Encryption Management
Constitutional compliance: Privacy First encryption for identity operations
"""

from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger


class EncryptionManager:
    """
    Constitutional encryption manager for identity operations
    Implements Privacy First principle for sensitive identity data
    """
    
    def __init__(self, settings: Optional[HAINetSettings] = None):
        self.settings = settings or HAINetSettings()
        self.logger = get_logger("identity.encryption", settings)
        self._encryption_key: Optional[bytes] = None
    
    def generate_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Generate encryption key from password
        Constitutional principle: Privacy First - secure key derivation
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        self.logger.log_privacy_event(
            "encryption_key_generated",
            "identity_protection",
            user_consent=True
        )
        
        return key
    
    def encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """
        Encrypt sensitive identity data
        Constitutional compliance: Privacy First principle
        """
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        
        self.logger.log_privacy_event(
            "data_encrypted",
            "identity_protection",
            user_consent=True
        )
        
        return encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt identity data with constitutional protection
        """
        try:
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            self.logger.log_privacy_event(
                "data_decrypted",
                "identity_access",
                user_consent=True
            )
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption system status"""
        return {
            "encryption_available": True,
            "algorithm": "Fernet (AES 128)",
            "key_derivation": "PBKDF2HMAC-SHA256",
            "constitutional_compliant": True
        }


def create_encryption_manager(settings: Optional[HAINetSettings] = None) -> EncryptionManager:
    """
    Create constitutional encryption manager
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured EncryptionManager instance
    """
    return EncryptionManager(settings)
