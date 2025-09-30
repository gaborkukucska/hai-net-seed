# START OF FILE core/identity/watermark.py
"""
HAI-Net Watermark Management
Constitutional compliance: Transparency for AI-generated content
"""

from typing import Optional, Dict, Any, List
import json
import time
import base64
import hashlib

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger


class WatermarkManager:
    """
    Constitutional watermark manager for AI-generated content
    Implements transparency requirements for AI content identification
    """
    
    def __init__(self, settings: Optional[HAINetSettings] = None):
        self.settings = settings or HAINetSettings()
        self.logger = get_logger("identity.watermark", settings)
        self.constitutional_version = "1.0"
    
    def create_watermark(self, did: str, content_type: str = "text", 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create constitutional watermark for AI-generated content
        Constitutional requirement: AI transparency
        """
        watermark_data = {
            "did": did,
            "timestamp": time.time(),
            "content_type": content_type,
            "constitutional_version": self.constitutional_version,
            "watermark_id": self._generate_watermark_id(did),
            "metadata": metadata or {}
        }
        
        self.logger.log_constitutional_event(
            "watermark_created",
            {
                "did": did,
                "content_type": content_type,
                "constitutional_compliant": True
            }
        )
        
        return watermark_data
    
    def embed_watermark(self, content: bytes, watermark_data: Dict[str, Any]) -> bytes:
        """
        Embed watermark into content
        Constitutional compliance: Transparency principle
        """
        watermark_json = json.dumps(watermark_data)
        watermark_encoded = base64.b64encode(watermark_json.encode())
        
        # Simple embedding strategy: append with marker
        marker = b"HAINET_WATERMARK:"
        watermarked_content = content + marker + watermark_encoded
        
        self.logger.log_constitutional_event(
            "watermark_embedded",
            {
                "content_size": len(content),
                "watermark_size": len(watermark_encoded),
                "constitutional_compliant": True
            }
        )
        
        return watermarked_content
    
    def extract_watermark(self, content: bytes) -> Optional[Dict[str, Any]]:
        """
        Extract watermark from content
        Constitutional verification of AI content
        """
        try:
            marker = b"HAINET_WATERMARK:"
            marker_pos = content.rfind(marker)
            
            if marker_pos == -1:
                return None
            
            watermark_encoded = content[marker_pos + len(marker):]
            watermark_json = base64.b64decode(watermark_encoded).decode()
            watermark_data = json.loads(watermark_json)
            
            # Verify constitutional compliance
            if not self._verify_watermark(watermark_data):
                return None
            
            self.logger.log_constitutional_event(
                "watermark_extracted",
                {
                    "did": watermark_data.get("did", "unknown"),
                    "constitutional_compliant": True
                }
            )
            
            return watermark_data
            
        except Exception as e:
            self.logger.debug(f"Watermark extraction failed: {e}")
            return None
    
    def verify_watermark(self, watermark_data: Dict[str, Any]) -> bool:
        """
        Verify watermark authenticity and constitutional compliance
        """
        return self._verify_watermark(watermark_data)
    
    def _verify_watermark(self, watermark_data: Dict[str, Any]) -> bool:
        """
        Internal watermark verification
        """
        required_fields = ["did", "timestamp", "constitutional_version"]
        
        # Check required fields
        for field in required_fields:
            if field not in watermark_data:
                return False
        
        # Check constitutional version compatibility
        if watermark_data["constitutional_version"] != self.constitutional_version:
            return False
        
        # Check timestamp validity (not too old or in future)
        current_time = time.time()
        watermark_time = watermark_data["timestamp"]
        
        # Allow up to 1 year old, prevent future timestamps
        if (current_time - watermark_time) > (365 * 24 * 3600) or watermark_time > current_time:
            return False
        
        return True
    
    def _generate_watermark_id(self, did: str) -> str:
        """
        Generate unique watermark ID
        """
        timestamp = str(int(time.time() * 1000))
        combined = f"{did}:{timestamp}"
        watermark_hash = hashlib.sha256(combined.encode()).hexdigest()
        return watermark_hash[:16]  # First 16 characters
    
    def get_watermark_stats(self) -> Dict[str, Any]:
        """
        Get watermark system statistics
        """
        return {
            "watermark_system_active": True,
            "constitutional_version": self.constitutional_version,
            "supported_content_types": ["text", "image", "audio", "video"],
            "embedding_method": "append_with_marker",
            "constitutional_compliant": True
        }
    
    def batch_verify_content(self, content_list: List[bytes]) -> List[Dict[str, Any]]:
        """
        Batch verify multiple pieces of content
        """
        results = []
        
        for i, content in enumerate(content_list):
            watermark = self.extract_watermark(content)
            results.append({
                "index": i,
                "watermarked": watermark is not None,
                "watermark_data": watermark,
                "constitutional_compliant": watermark is not None and self.verify_watermark(watermark)
            })
        
        self.logger.log_constitutional_event(
            "batch_verification_completed",
            {
                "total_content": len(content_list),
                "watermarked_count": sum(1 for r in results if r["watermarked"]),
                "constitutional_compliant": True
            }
        )
        
        return results


def create_watermark_manager(settings: Optional[HAINetSettings] = None) -> WatermarkManager:
    """
    Create constitutional watermark manager
    
    Args:
        settings: HAI-Net settings
        
    Returns:
        Configured WatermarkManager instance
    """
    return WatermarkManager(settings)
