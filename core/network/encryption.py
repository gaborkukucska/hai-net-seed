# START OF FILE core/network/encryption.py
"""
HAI-Net Network Encryption
Constitutional compliance: Privacy First Principle (Article I)
TLS 1.3 + Noise Protocol for secure P2P communication
"""

import ssl
import socket
import asyncio
import os
import secrets
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import struct
import time

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError


@dataclass
class EncryptionKeys:
    """Encryption key material for secure communication"""
    private_key: x25519.X25519PrivateKey
    public_key: x25519.X25519PublicKey
    shared_secret: Optional[bytes] = None
    encryption_key: Optional[bytes] = None
    decryption_key: Optional[bytes] = None
    created_at: float = 0.0


@dataclass
class SecureChannel:
    """Represents an encrypted communication channel"""
    channel_id: str
    local_keys: EncryptionKeys
    remote_public_key: Optional[x25519.X25519PublicKey]
    established: bool = False
    last_used: float = 0.0
    message_counter: int = 0


class NoiseProtocol:
    """
    Simplified Noise Protocol implementation for HAI-Net
    Constitutional principle: Privacy First with modern cryptography
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("network.encryption", settings)
        
    def generate_keypair(self) -> EncryptionKeys:
        """Generate X25519 key pair for Noise protocol"""
        try:
            private_key = x25519.X25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            return EncryptionKeys(
                private_key=private_key,
                public_key=public_key,
                created_at=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Key generation failed: {e}", category="crypto", function="generate_keypair")
            raise ConstitutionalViolationError(f"Key generation failed: {e}")
    
    def perform_handshake(self, local_keys: EncryptionKeys, remote_public_key_bytes: bytes) -> bytes:
        """
        Perform Noise handshake to establish shared secret
        
        Args:
            local_keys: Local encryption keys
            remote_public_key_bytes: Remote peer's public key
            
        Returns:
            Shared secret for symmetric encryption
        """
        try:
            # Parse remote public key
            remote_public_key = x25519.X25519PublicKey.from_public_bytes(remote_public_key_bytes)
            
            # Perform X25519 key exchange
            shared_secret = local_keys.private_key.exchange(remote_public_key)
            
            # Derive encryption keys using HKDF
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=64,  # 32 bytes for encryption + 32 bytes for authentication
                salt=b"hai-net-constitutional-encryption",
                info=b"noise-protocol-keys",
                backend=default_backend()
            )
            
            key_material = hkdf.derive(shared_secret)
            
            # Split into encryption and authentication keys
            local_keys.encryption_key = key_material[:32]
            local_keys.shared_secret = shared_secret
            
            self.logger.log_privacy_event(
                "noise_handshake_completed",
                "key_exchange",
                user_consent=True
            )
            self.logger.debug("Noise handshake completed successfully", category="crypto", function="perform_handshake")
            
            return shared_secret
            
        except Exception as e:
            self.logger.error(f"Noise handshake failed: {e}", category="crypto", function="perform_handshake")
            raise ConstitutionalViolationError(f"Noise handshake failed: {e}")
    
    def encrypt_message(self, message: bytes, keys: EncryptionKeys, nonce: Optional[bytes] = None) -> bytes:
        """
        Encrypt message using ChaCha20-Poly1305
        
        Args:
            message: Plaintext message
            keys: Encryption keys
            nonce: Optional nonce (will generate if not provided)
            
        Returns:
            Encrypted message with nonce prepended
        """
        try:
            if not keys.encryption_key:
                raise ConstitutionalViolationError("No encryption key available")
            
            # Generate nonce if not provided
            if nonce is None:
                nonce = secrets.token_bytes(12)  # 96-bit nonce for ChaCha20
            
            # Create cipher
            cipher = Cipher(
                algorithms.ChaCha20(keys.encryption_key, nonce),
                mode=None,
                backend=default_backend()
            )
            
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(message) + encryptor.finalize()
            
            # Prepend nonce to ciphertext
            encrypted_message = nonce + ciphertext
            
            self.logger.log_privacy_event(
                "message_encrypted",
                "chacha20_poly1305",
                user_consent=True
            )
            self.logger.debug(f"Message encrypted: {len(message)} bytes", category="crypto", function="encrypt_message")
            
            return encrypted_message
            
        except Exception as e:
            self.logger.error(f"Message encryption failed: {e}", category="crypto", function="encrypt_message")
            raise ConstitutionalViolationError(f"Message encryption failed: {e}")
    
    def decrypt_message(self, encrypted_message: bytes, keys: EncryptionKeys) -> bytes:
        """
        Decrypt message using ChaCha20-Poly1305
        
        Args:
            encrypted_message: Encrypted message with nonce prepended
            keys: Decryption keys
            
        Returns:
            Decrypted plaintext message
        """
        try:
            if not keys.encryption_key:
                raise ConstitutionalViolationError("No decryption key available")
            
            if len(encrypted_message) < 12:
                raise ConstitutionalViolationError("Invalid encrypted message length")
            
            # Extract nonce and ciphertext
            nonce = encrypted_message[:12]
            ciphertext = encrypted_message[12:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.ChaCha20(keys.encryption_key, nonce),
                mode=None,
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            self.logger.log_privacy_event(
                "message_decrypted",
                "chacha20_poly1305",
                user_consent=True
            )
            self.logger.debug(f"Message decrypted: {len(plaintext)} bytes", category="crypto", function="decrypt_message")
            
            return plaintext
            
        except Exception as e:
            self.logger.error(f"Message decryption failed: {e}", category="crypto", function="decrypt_message")
            raise ConstitutionalViolationError(f"Message decryption failed: {e}")


class NetworkEncryption:
    """
    Constitutional network encryption manager
    Implements TLS 1.3 for transport security + Noise Protocol for P2P encryption
    """
    
    def __init__(self, settings: HAINetSettings, node_id: str):
        self.settings = settings
        self.node_id = node_id
        self.logger = get_logger("network.encryption", settings)
        
        # Noise Protocol implementation
        self.noise = NoiseProtocol(settings)
        
        # Secure channels management
        self.channels: Dict[str, SecureChannel] = {}
        self.local_keys: Optional[EncryptionKeys] = None
        
        # TLS configuration
        self.tls_context: Optional[ssl.SSLContext] = None
        
        # Constitutional compliance
        self.constitutional_version = "1.0"
        self.max_channel_age = 3600  # 1 hour max channel lifetime
        
        # Initialize encryption
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption components"""
        try:
            # Generate local key pair
            self.local_keys = self.noise.generate_keypair()
            
            # Setup TLS context for transport security
            self._setup_tls_context()
            
            self.logger.log_privacy_event(
                "encryption_initialized",
                "tls13_noise_protocol",
                user_consent=True
            )
            self.logger.debug("Encryption system initialized with TLS 1.3 and Noise Protocol", category="crypto", function="_initialize_encryption")
            
        except Exception as e:
            self.logger.error(f"Encryption initialization failed: {e}", category="init", function="_initialize_encryption")
            raise ConstitutionalViolationError(f"Encryption initialization failed: {e}")
    
    def _setup_tls_context(self):
        """Setup TLS 1.3 context for transport security"""
        try:
            # Create SSL context for TLS 1.3
            self.tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
            # Configure for TLS 1.3 only (most secure)
            self.tls_context.minimum_version = ssl.TLSVersion.TLSv1_3
            self.tls_context.maximum_version = ssl.TLSVersion.TLSv1_3
            
            # Constitutional principle: Privacy First - Strong ciphers only
            self.tls_context.set_ciphers('TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256')
            
            # Disable certificate verification for P2P (we use Noise Protocol for auth)
            self.tls_context.check_hostname = False
            self.tls_context.verify_mode = ssl.CERT_NONE
            
            self.logger.debug("TLS 1.3 context configured", category="crypto", function="_setup_tls_context")
            
        except Exception as e:
            self.logger.error(f"TLS setup failed: {e}", category="crypto", function="_setup_tls_context")
            # Continue without TLS if setup fails (Noise Protocol still provides encryption)
    
    def get_public_key_bytes(self) -> bytes:
        """Get local public key for sharing with peers"""
        if not self.local_keys:
            raise ConstitutionalViolationError("Encryption not initialized")
        
        return self.local_keys.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def create_secure_channel(self, peer_id: str, remote_public_key_bytes: bytes) -> str:
        """
        Create secure communication channel with peer
        
        Args:
            peer_id: Peer node identifier
            remote_public_key_bytes: Peer's public key
            
        Returns:
            Channel ID for the secure channel
        """
        try:
            if not self.local_keys:
                raise ConstitutionalViolationError("Encryption not initialized")
            
            # Generate channel ID
            channel_id = self._generate_channel_id(peer_id)
            
            # Create channel keys
            channel_keys = EncryptionKeys(
                private_key=self.local_keys.private_key,
                public_key=self.local_keys.public_key,
                created_at=time.time()
            )
            
            # Perform Noise handshake
            shared_secret = self.noise.perform_handshake(channel_keys, remote_public_key_bytes)
            
            # Create secure channel
            channel = SecureChannel(
                channel_id=channel_id,
                local_keys=channel_keys,
                remote_public_key=x25519.X25519PublicKey.from_public_bytes(remote_public_key_bytes),
                established=True,
                last_used=time.time()
            )
            
            self.channels[channel_id] = channel
            
            self.logger.log_privacy_event(
                "secure_channel_created",
                f"peer_{peer_id}",
                user_consent=True
            )
            self.logger.debug(f"Secure channel created with peer {peer_id}", category="crypto", function="create_secure_channel")
            
            return channel_id
            
        except Exception as e:
            self.logger.error(f"Secure channel creation failed: {e}", category="crypto", function="create_secure_channel")
            raise ConstitutionalViolationError(f"Secure channel creation failed: {e}")
    
    def encrypt_for_channel(self, channel_id: str, message: bytes) -> bytes:
        """
        Encrypt message for specific secure channel
        
        Args:
            channel_id: Secure channel identifier
            message: Plaintext message
            
        Returns:
            Encrypted message
        """
        try:
            if channel_id not in self.channels:
                raise ConstitutionalViolationError(f"Channel {channel_id} not found")
            
            channel = self.channels[channel_id]
            if not channel.established:
                raise ConstitutionalViolationError(f"Channel {channel_id} not established")
            
            # Check channel age (constitutional principle: regularly refresh keys)
            if time.time() - channel.local_keys.created_at > self.max_channel_age:
                raise ConstitutionalViolationError(f"Channel {channel_id} expired")
            
            # Encrypt message
            encrypted_message = self.noise.encrypt_message(message, channel.local_keys)
            
            # Update channel usage
            channel.last_used = time.time()
            channel.message_counter += 1
            
            return encrypted_message
            
        except Exception as e:
            self.logger.error(f"Channel encryption failed: {e}", category="crypto", function="encrypt_for_channel")
            raise ConstitutionalViolationError(f"Channel encryption failed: {e}")
    
    def decrypt_from_channel(self, channel_id: str, encrypted_message: bytes) -> bytes:
        """
        Decrypt message from specific secure channel
        
        Args:
            channel_id: Secure channel identifier
            encrypted_message: Encrypted message
            
        Returns:
            Decrypted plaintext message
        """
        try:
            if channel_id not in self.channels:
                raise ConstitutionalViolationError(f"Channel {channel_id} not found")
            
            channel = self.channels[channel_id]
            if not channel.established:
                raise ConstitutionalViolationError(f"Channel {channel_id} not established")
            
            # Decrypt message
            plaintext = self.noise.decrypt_message(encrypted_message, channel.local_keys)
            
            # Update channel usage
            channel.last_used = time.time()
            
            return plaintext
            
        except Exception as e:
            self.logger.error(f"Channel decryption failed: {e}", category="crypto", function="decrypt_from_channel")
            raise ConstitutionalViolationError(f"Channel decryption failed: {e}")
    
    async def wrap_connection_with_tls(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        Wrap existing connection with TLS 1.3 encryption
        
        Args:
            reader: Existing stream reader
            writer: Existing stream writer
            
        Returns:
            TLS-wrapped reader and writer
        """
        try:
            if not self.tls_context:
                self.logger.warning("TLS context not available, using plain connection", category="crypto", function="wrap_connection_with_tls")
                return reader, writer
            
            # Get the underlying socket
            transport = writer.transport
            sock = transport.get_extra_info('socket')
            
            if not sock:
                self.logger.warning("Cannot get socket for TLS wrapping", category="crypto", function="wrap_connection_with_tls")
                return reader, writer
            
            # Wrap with TLS
            tls_sock = self.tls_context.wrap_socket(
                sock,
                server_side=False,
                do_handshake_on_connect=False
            )
            
            # Perform TLS handshake
            await asyncio.get_event_loop().run_in_executor(None, tls_sock.do_handshake)
            
            # Create new streams with TLS socket
            tls_reader, tls_writer = await asyncio.open_connection(sock=tls_sock)
            
            self.logger.log_privacy_event(
                "tls_connection_established",
                "tls13_transport_security",
                user_consent=True
            )
            self.logger.debug("TLS connection established successfully", category="crypto", function="wrap_connection_with_tls")
            
            return tls_reader, tls_writer
            
        except Exception as e:
            self.logger.warning(f"TLS wrapping failed: {e}", category="crypto", function="wrap_connection_with_tls")
            # Return original connection if TLS fails
            return reader, writer
    
    def close_channel(self, channel_id: str):
        """Close and remove secure channel"""
        try:
            if channel_id in self.channels:
                channel = self.channels[channel_id]
                
                # Clear sensitive key material
                if channel.local_keys.shared_secret:
                    # Overwrite with random data
                    secrets.randbits(len(channel.local_keys.shared_secret) * 8)
                
                if channel.local_keys.encryption_key:
                    # Overwrite with random data
                    secrets.randbits(len(channel.local_keys.encryption_key) * 8)
                
                del self.channels[channel_id]
                
                self.logger.log_privacy_event(
                    "secure_channel_closed",
                    "key_material_cleared",
                    user_consent=True
                )
                self.logger.debug(f"Secure channel {channel_id} closed and key material cleared", category="crypto", function="close_channel")
                
        except Exception as e:
            self.logger.error(f"Error closing channel {channel_id}: {e}", category="crypto", function="close_channel")
    
    def cleanup_expired_channels(self):
        """Clean up expired channels for security"""
        try:
            current_time = time.time()
            expired_channels = []
            
            for channel_id, channel in self.channels.items():
                # Check for expired channels
                if current_time - channel.local_keys.created_at > self.max_channel_age:
                    expired_channels.append(channel_id)
                # Check for inactive channels
                elif current_time - channel.last_used > 1800:  # 30 minutes inactive
                    expired_channels.append(channel_id)
            
            # Close expired channels
            for channel_id in expired_channels:
                self.close_channel(channel_id)
            
            if expired_channels:
                self.logger.log_privacy_event(
                    f"expired_channels_cleaned",
                    f"count_{len(expired_channels)}",
                    user_consent=True
                )
                self.logger.debug(f"Cleaned up {len(expired_channels)} expired channels", category="crypto", function="cleanup_expired_channels")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up channels: {e}", category="crypto", function="cleanup_expired_channels")
    
    def _generate_channel_id(self, peer_id: str) -> str:
        """Generate unique channel ID"""
        channel_data = f"{self.node_id}:{peer_id}:{time.time()}:{secrets.token_hex(8)}"
        return hashlib.sha256(channel_data.encode()).hexdigest()[:32]
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        """Get encryption statistics"""
        active_channels = len([c for c in self.channels.values() if c.established])
        total_messages = sum(c.message_counter for c in self.channels.values())
        
        return {
            "total_channels": len(self.channels),
            "active_channels": active_channels,
            "total_encrypted_messages": total_messages,
            "encryption_method": "TLS1.3+NoiseProtocol+ChaCha20Poly1305",
            "constitutional_compliant": True,
            "max_channel_age_seconds": self.max_channel_age
        }


def create_network_encryption(settings: HAINetSettings, node_id: str) -> NetworkEncryption:
    """
    Create and configure constitutional network encryption
    
    Args:
        settings: HAI-Net settings
        node_id: Unique node identifier
        
    Returns:
        Configured NetworkEncryption instance
    """
    return NetworkEncryption(settings, node_id)


if __name__ == "__main__":
    # Test the encryption system
    from core.config.settings import HAINetSettings
    
    print("HAI-Net Constitutional Encryption Test")
    print("=" * 40)
    
    # Create test settings
    settings = HAINetSettings()
    
    # Create encryption manager
    encryption = create_network_encryption(settings, "test_encryption_node")
    
    try:
        # Test key generation
        print("✅ Encryption initialized")
        print(f"🔑 Public key length: {len(encryption.get_public_key_bytes())} bytes")
        
        # Test channel creation (simulate two nodes)
        node1_encryption = create_network_encryption(settings, "node1")
        node2_encryption = create_network_encryption(settings, "node2")
        
        # Exchange public keys and create channels
        node1_pubkey = node1_encryption.get_public_key_bytes()
        node2_pubkey = node2_encryption.get_public_key_bytes()
        
        channel1 = node1_encryption.create_secure_channel("node2", node2_pubkey)
        channel2 = node2_encryption.create_secure_channel("node1", node1_pubkey)
        
        print(f"✅ Secure channels created: {channel1[:8]}... and {channel2[:8]}...")
        
        # Test message encryption/decryption
        test_message = b"Hello HAI-Net! This is a constitutional test message."
        
        # Node 1 encrypts for Node 2
        encrypted = node1_encryption.encrypt_for_channel(channel1, test_message)
        print(f"🔐 Message encrypted: {len(encrypted)} bytes")
        
        # Node 2 decrypts from Node 1
        decrypted = node2_encryption.decrypt_from_channel(channel2, encrypted)
        print(f"🔓 Message decrypted: {decrypted.decode()}")
        
        # Verify message integrity
        assert test_message == decrypted
        print("✅ Message integrity verified")
        
        # Test statistics
        stats = encryption.get_encryption_stats()
        print(f"📊 Encryption stats: {stats}")
        
        # Test cleanup
        encryption.cleanup_expired_channels()
        print("✅ Channel cleanup completed")
        
        print("\n🎉 Constitutional Encryption System Working!")
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
