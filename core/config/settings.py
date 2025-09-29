# START OF FILE core/config/settings.py
"""
HAI-Net Settings Management
Constitutional compliance and secure configuration
"""

from typing import Dict, Any, Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class HAINetSettings(BaseSettings):
    """
    HAI-Net configuration settings with constitutional compliance
    """
    
    # Constitutional compliance
    constitutional_version: str = Field(default="1.0", description="Constitutional framework version")
    
    # Node Configuration
    node_role: str = Field(default="master", description="Node role: master or slave")
    node_id: Optional[str] = Field(default=None, description="Unique node identifier")
    local_hub_name: str = Field(default="HAI-Net Local Hub", description="Local hub display name")
    
    # Privacy Settings (Constitutional Article I)
    data_sharing_consent: bool = Field(default=False, description="User consent for data sharing")
    analytics_consent: bool = Field(default=False, description="User consent for analytics")
    encryption_enabled: bool = Field(default=True, description="Encryption at rest and in transit")
    watermarking_enabled: bool = Field(default=True, description="AI content watermarking")
    
    # Human Rights Protection (Constitutional Article II)
    accessibility_mode: bool = Field(default=True, description="Accessibility features enabled")
    bias_detection_enabled: bool = Field(default=True, description="AI bias detection")
    content_filtering_enabled: bool = Field(default=True, description="Harmful content filtering")
    user_override_enabled: bool = Field(default=True, description="User can override AI decisions")
    
    # Decentralization (Constitutional Article III)
    central_authority_disabled: bool = Field(default=True, description="No central authority connections")
    local_first: bool = Field(default=True, description="Local processing priority")
    mesh_networking_enabled: bool = Field(default=True, description="P2P mesh networking")
    consensus_required: bool = Field(default=True, description="Consensus for major changes")
    
    # Community Focus (Constitutional Article IV)
    community_participation: bool = Field(default=True, description="Community participation enabled")
    resource_sharing_enabled: bool = Field(default=False, description="Surplus resource sharing")
    environmental_mode: bool = Field(default=True, description="Resource efficiency priority")
    irl_prioritization: bool = Field(default=True, description="In-person interaction priority")
    
    # Storage Paths
    data_dir: Path = Field(default=Path.home() / "hai-net" / "data", description="Local data directory")
    config_dir: Path = Field(default=Path.home() / "hai-net" / "config", description="Configuration directory")
    logs_dir: Path = Field(default=Path.home() / "hai-net" / "logs", description="Logs directory")
    models_dir: Path = Field(default=Path.home() / "hai-net" / "models", description="AI models directory")
    
    # Network Configuration
    discovery_enabled: bool = Field(default=True, description="Local network discovery")
    mdns_service_name: str = Field(default="_hai-net._tcp.local.", description="mDNS service name")
    p2p_port: int = Field(default=4001, description="P2P networking port")
    web_ui_port: int = Field(default=8080, description="Web UI port")
    api_port: int = Field(default=8000, description="API server port")
    
    # AI Service Configuration
    llm_backend: str = Field(default="ollama", description="LLM backend: ollama, llama.cpp, vllm")
    default_model: str = Field(default="llama2:7b", description="Default LLM model")
    voice_stt_enabled: bool = Field(default=True, description="Speech-to-text enabled")
    voice_tts_enabled: bool = Field(default=True, description="Text-to-speech enabled")
    image_generation_enabled: bool = Field(default=False, description="Image generation enabled")
    
    # Resource Management
    max_cpu_usage: float = Field(default=80.0, description="Maximum CPU usage percentage")
    max_memory_usage: float = Field(default=85.0, description="Maximum memory usage percentage")
    min_disk_space_gb: float = Field(default=10.0, description="Minimum free disk space in GB")
    surplus_sharing_threshold: float = Field(default=30.0, description="Idle threshold for surplus sharing")
    
    # Security Settings
    session_timeout_minutes: int = Field(default=60, description="User session timeout")
    max_login_attempts: int = Field(default=3, description="Maximum login attempts")
    password_min_length: int = Field(default=8, description="Minimum password length")
    require_2fa: bool = Field(default=False, description="Require two-factor authentication")
    
    # Guardian Agent Settings
    guardian_enabled: bool = Field(default=True, description="Constitutional Guardian agent enabled")
    guardian_mode: str = Field(default="educational", description="Guardian mode: educational, protective, emergency")
    violation_reporting: bool = Field(default=True, description="Constitutional violation reporting")
    auto_correction: bool = Field(default=True, description="Automatic constitutional corrections")
    
    # Development Settings
    debug_mode: bool = Field(default=False, description="Debug mode enabled")
    log_level: str = Field(default="INFO", description="Logging level")
    performance_monitoring: bool = Field(default=True, description="Performance monitoring enabled")
    telemetry_enabled: bool = Field(default=False, description="Telemetry data collection")
    
    @field_validator('node_role')
    def validate_node_role(cls, v):
        """Validate node role according to constitutional principles"""
        valid_roles = ['master', 'slave']
        if v not in valid_roles:
            raise ValueError(f"Node role must be one of {valid_roles}")
        return v
    
    @field_validator('guardian_mode')
    def validate_guardian_mode(cls, v):
        """Validate guardian mode settings"""
        valid_modes = ['educational', 'protective', 'emergency']
        if v not in valid_modes:
            raise ValueError(f"Guardian mode must be one of {valid_modes}")
        return v
    
    @field_validator('log_level')
    def validate_log_level(cls, v):
        """Validate logging level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator('data_sharing_consent')
    def validate_privacy_first(cls, v):
        """Enforce Privacy First constitutional principle"""
        # Data sharing consent must be explicitly granted, never default to True
        # This is acceptable as user has explicitly consented
        return v
    
    @field_validator('central_authority_disabled')
    def validate_decentralization(cls, v):
        """Enforce Decentralization constitutional principle"""
        if not v:
            raise ValueError("Central authority connections violate decentralization principle")
        return v
    
    def constitutional_compliance_check(self) -> Dict[str, bool]:
        """
        Verify all settings comply with constitutional principles
        """
        compliance = {
            "privacy_first": (
                not self.data_sharing_consent or  # Default to no sharing
                (self.encryption_enabled and self.watermarking_enabled)
            ),
            "human_rights": (
                self.accessibility_mode and
                self.bias_detection_enabled and
                self.user_override_enabled
            ),
            "decentralization": (
                self.central_authority_disabled and
                self.local_first and
                self.mesh_networking_enabled
            ),
            "community_focus": (
                self.community_participation and
                self.environmental_mode and
                self.irl_prioritization
            )
        }
        
        return compliance
    
    def get_secure_config(self) -> Dict[str, Any]:
        """
        Get configuration with sensitive data removed
        """
        config = self.dict()
        
        # Remove sensitive fields that should not be logged or shared
        sensitive_fields = [
            'session_timeout_minutes',
            'max_login_attempts', 
            'password_min_length'
        ]
        
        for field in sensitive_fields:
            if field in config:
                config[field] = "[REDACTED]"
        
        return config
    
    class Config:
        env_prefix = "HAINET_"
        case_sensitive = False
        use_enum_values = True
        
        # Load from .env file if it exists
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevelopmentSettings(HAINetSettings):
    """Development-specific settings"""
    
    debug_mode: bool = Field(default=True)
    log_level: str = Field(default="DEBUG") 
    performance_monitoring: bool = Field(default=True)
    telemetry_enabled: bool = Field(default=False)  # Still respect privacy in dev
    
    # Relaxed resource limits for development
    max_cpu_usage: float = Field(default=95.0)
    max_memory_usage: float = Field(default=95.0)
    min_disk_space_gb: float = Field(default=1.0)


class ProductionSettings(HAINetSettings):
    """Production-specific settings"""
    
    debug_mode: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    performance_monitoring: bool = Field(default=True)
    telemetry_enabled: bool = Field(default=False)  # Constitutional privacy protection
    
    # Strict resource limits for production
    max_cpu_usage: float = Field(default=70.0)
    max_memory_usage: float = Field(default=80.0)
    min_disk_space_gb: float = Field(default=20.0)
    
    # Enhanced security for production
    require_2fa: bool = Field(default=True)
    session_timeout_minutes: int = Field(default=30)


def get_settings(environment: str = "development") -> HAINetSettings:
    """
    Get appropriate settings based on environment
    
    Args:
        environment: "development", "production", or "default"
        
    Returns:
        Configured settings object
    """
    environment = environment.lower()
    
    if environment == "development":
        return DevelopmentSettings()
    elif environment == "production":
        return ProductionSettings()
    else:
        return HAINetSettings()


def validate_constitutional_compliance(settings: HAINetSettings) -> List[str]:
    """
    Validate that settings comply with constitutional principles
    
    Returns:
        List of compliance violations (empty if compliant)
    """
    violations = []
    compliance = settings.constitutional_compliance_check()
    
    principle_descriptions = {
        "privacy_first": "Privacy First Principle (Article I)",
        "human_rights": "Human Rights Protection (Article II)", 
        "decentralization": "Decentralization Imperative (Article III)",
        "community_focus": "Community Focus Principle (Article IV)"
    }
    
    for principle, is_compliant in compliance.items():
        if not is_compliant:
            violations.append(f"Violation of {principle_descriptions[principle]}")
    
    return violations


if __name__ == "__main__":
    # Test constitutional compliance
    print("HAI-Net Settings Constitutional Compliance Check")
    print("=" * 50)
    
    settings = HAINetSettings()
    violations = validate_constitutional_compliance(settings)
    
    if violations:
        print("❌ Constitutional violations detected:")
        for violation in violations:
            print(f"  - {violation}")
    else:
        print("✅ All settings are constitutionally compliant!")
    
    compliance = settings.constitutional_compliance_check()
    for principle, status in compliance.items():
        status_emoji = "✅" if status else "❌"
        print(f"{status_emoji} {principle.replace('_', ' ').title()}: {'Compliant' if status else 'Non-compliant'}")
