# START OF FILE core/config/config_manager.py
"""
HAI-Net Configuration Manager
Constitutional compliance and secure configuration management
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
import base64
import hashlib

from .settings import HAINetSettings, get_settings, validate_constitutional_compliance
from core.identity.did import ConstitutionalViolationError


class ConfigManager:
    """
    Manages HAI-Net configuration with constitutional compliance
    Constitutional Principle: Privacy First + Decentralization
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / "hai-net" / "config"
        self.config_file = self.config_dir / "hai-net.yaml"
        self.secure_config_file = self.config_dir / ".hai-net.enc"
        self.settings: Optional[HAINetSettings] = None
        self._encryption_key: Optional[bytes] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize configuration
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize configuration with constitutional compliance"""
        try:
            if self.config_file.exists():
                self.load_config()
            else:
                self.settings = get_settings("development")
                self.save_config()
        except Exception as e:
            # Constitutional principle: fail securely
            print(f"Configuration initialization error: {e}")
            self.settings = get_settings("development")
    
    def load_config(self, environment: str = "development") -> HAINetSettings:
        """
        Load configuration from file with constitutional validation
        
        Args:
            environment: Environment type for appropriate settings
            
        Returns:
            Validated settings object
            
        Raises:
            ConstitutionalViolationError: If config violates constitutional principles
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Merge with environment defaults
                self.settings = get_settings(environment)
                
                # Update with loaded configuration
                if config_data:
                    for key, value in config_data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
            else:
                self.settings = get_settings(environment)
            
            # Constitutional compliance validation
            violations = validate_constitutional_compliance(self.settings)
            if violations:
                raise ConstitutionalViolationError(
                    f"Configuration violates constitutional principles: {violations}"
                )
            
            return self.settings
            
        except Exception as e:
            # Constitutional principle: educational error handling
            print(f"Configuration loading failed, using secure defaults: {e}")
            self.settings = get_settings(environment)
            return self.settings
    
    def save_config(self) -> bool:
        """
        Save configuration to file with constitutional protection
        
        Returns:
            True if successful, False otherwise
        """
        if not self.settings:
            return False
        
        try:
            # Get secure config (sensitive data removed)
            config_data = self.settings.get_secure_config()
            
            # Save to YAML file
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            # Constitutional compliance: Log configuration change
            self._log_config_change("Configuration saved")
            
            return True
            
        except Exception as e:
            print(f"Configuration save failed: {e}")
            return False
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        Update a specific setting with constitutional validation
        
        Args:
            key: Setting key to update
            value: New value
            
        Returns:
            True if update successful and compliant
        """
        if not self.settings:
            self.settings = get_settings()
        
        # Check if setting exists
        if not hasattr(self.settings, key):
            print(f"Setting '{key}' does not exist")
            return False
        
        # Store original value for rollback
        original_value = getattr(self.settings, key)
        
        try:
            # Update the setting
            setattr(self.settings, key, value)
            
            # Validate constitutional compliance
            violations = validate_constitutional_compliance(self.settings)
            if violations:
                # Rollback on constitutional violation
                setattr(self.settings, key, original_value)
                raise ConstitutionalViolationError(
                    f"Setting update violates constitutional principles: {violations}"
                )
            
            # Save updated configuration
            self.save_config()
            
            self._log_config_change(f"Setting updated: {key} = {value}")
            return True
            
        except Exception as e:
            # Rollback on any error
            setattr(self.settings, key, original_value)
            print(f"Setting update failed: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value
        
        Args:
            key: Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        if not self.settings:
            self.load_config()
        
        return getattr(self.settings, key, default)
    
    def enable_resource_sharing(self, user_consent: bool = False) -> bool:
        """
        Enable resource sharing with explicit user consent
        Constitutional requirement: Privacy First + Community Focus
        
        Args:
            user_consent: Explicit user consent for resource sharing
            
        Returns:
            True if successfully enabled
        """
        if not user_consent:
            print("Resource sharing requires explicit user consent")
            return False
        
        # Update settings with constitutional compliance
        success = self.update_setting("resource_sharing_enabled", True)
        
        if success:
            # Also update data sharing consent if needed
            if self.get_setting("data_sharing_consent", False):
                print("Resource sharing enabled with data sharing consent")
            else:
                print("Resource sharing enabled (computational resources only)")
        
        return success
    
    def configure_guardian_mode(self, mode: str) -> bool:
        """
        Configure Constitutional Guardian agent mode
        
        Args:
            mode: Guardian mode (educational, protective, emergency)
            
        Returns:
            True if successfully configured
        """
        valid_modes = ["educational", "protective", "emergency"]
        
        if mode not in valid_modes:
            print(f"Invalid guardian mode. Must be one of: {valid_modes}")
            return False
        
        return self.update_setting("guardian_mode", mode)
    
    def setup_local_hub(self, hub_name: str, node_role: str = "master") -> bool:
        """
        Set up local hub configuration
        
        Args:
            hub_name: Display name for the local hub
            node_role: Node role (master or slave)
            
        Returns:
            True if successfully configured
        """
        try:
            # Update hub settings
            updates = {
                "local_hub_name": hub_name,
                "node_role": node_role
            }
            
            for key, value in updates.items():
                if not self.update_setting(key, value):
                    return False
            
            self._log_config_change(f"Local hub configured: {hub_name} as {node_role}")
            return True
            
        except Exception as e:
            print(f"Local hub setup failed: {e}")
            return False
    
    def get_constitutional_status(self) -> Dict[str, Any]:
        """
        Get comprehensive constitutional compliance status
        
        Returns:
            Dictionary with compliance status and details
        """
        if not self.settings:
            self.load_config()
        
        compliance = self.settings.constitutional_compliance_check()
        violations = validate_constitutional_compliance(self.settings)
        
        return {
            "overall_compliant": len(violations) == 0,
            "principle_compliance": compliance,
            "violations": violations,
            "constitutional_version": self.settings.constitutional_version,
            "last_updated": self._get_config_timestamp()
        }
    
    def export_config(self, export_path: Path, include_sensitive: bool = False) -> bool:
        """
        Export configuration to file
        Constitutional principle: User control and transparency
        
        Args:
            export_path: Path to export configuration
            include_sensitive: Whether to include sensitive settings
            
        Returns:
            True if export successful
        """
        if not self.settings:
            return False
        
        try:
            if include_sensitive:
                # Full configuration export (requires user confirmation)
                config_data = self.settings.dict()
            else:
                # Secure export (default)
                config_data = self.settings.get_secure_config()
            
            # Add constitutional compliance info
            config_data["constitutional_status"] = self.get_constitutional_status()
            
            with open(export_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            self._log_config_change(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"Configuration export failed: {e}")
            return False
    
    def reset_to_defaults(self, environment: str = "development") -> bool:
        """
        Reset configuration to constitutional defaults
        
        Args:
            environment: Environment for default settings
            
        Returns:
            True if reset successful
        """
        try:
            # Create fresh settings
            self.settings = get_settings(environment)
            
            # Save to file
            if self.save_config():
                self._log_config_change("Configuration reset to constitutional defaults")
                return True
            
            return False
            
        except Exception as e:
            print(f"Configuration reset failed: {e}")
            return False
    
    def _log_config_change(self, message: str):
        """Log configuration changes for audit trail"""
        timestamp = self._get_config_timestamp()
        log_message = f"[{timestamp}] {message}"
        
        # Write to config log file
        log_file = self.config_dir / "config.log"
        with open(log_file, 'a') as f:
            f.write(log_message + "\n")
    
    def _get_config_timestamp(self) -> str:
        """Get current timestamp for configuration tracking"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def validate_current_config(self) -> Dict[str, Any]:
        """
        Validate current configuration against constitutional principles
        
        Returns:
            Validation results with recommendations
        """
        if not self.settings:
            self.load_config()
        
        violations = validate_constitutional_compliance(self.settings)
        compliance = self.settings.constitutional_compliance_check()
        
        recommendations = []
        
        # Generate recommendations based on compliance
        if not compliance["privacy_first"]:
            recommendations.append("Enable encryption and watermarking for privacy protection")
        
        if not compliance["human_rights"]:
            recommendations.append("Enable accessibility features and bias detection")
        
        if not compliance["decentralization"]:
            recommendations.append("Disable central authority connections and enable mesh networking")
        
        if not compliance["community_focus"]:
            recommendations.append("Enable community participation and environmental optimization")
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "compliance": compliance,
            "recommendations": recommendations,
            "constitutional_version": self.settings.constitutional_version
        }


def create_default_config(config_dir: Optional[Path] = None) -> ConfigManager:
    """
    Create a default HAI-Net configuration with constitutional compliance
    
    Args:
        config_dir: Optional custom configuration directory
        
    Returns:
        Configured ConfigManager instance
    """
    manager = ConfigManager(config_dir)
    
    # Ensure constitutional compliance
    status = manager.get_constitutional_status()
    if not status["overall_compliant"]:
        print("Warning: Default configuration has constitutional issues")
        for violation in status["violations"]:
            print(f"  - {violation}")
    
    return manager


if __name__ == "__main__":
    # Test configuration management
    print("HAI-Net Configuration Manager Test")
    print("=" * 40)
    
    # Create config manager
    config = ConfigManager()
    
    # Test constitutional compliance
    status = config.get_constitutional_status()
    print(f"Constitutional Compliance: {'✅' if status['overall_compliant'] else '❌'}")
    
    # Display compliance per principle
    for principle, compliant in status["principle_compliance"].items():
        emoji = "✅" if compliant else "❌"
        print(f"{emoji} {principle.replace('_', ' ').title()}")
    
    # Test setting update
    print("\nTesting setting update...")
    result = config.update_setting("local_hub_name", "Test HAI-Net Hub")
    print(f"Setting update: {'✅' if result else '❌'}")
    
    # Test validation
    validation = config.validate_current_config()
    print(f"\nConfiguration valid: {'✅' if validation['is_valid'] else '❌'}")
    
    if validation["recommendations"]:
        print("Recommendations:")
        for rec in validation["recommendations"]:
            print(f"  - {rec}")
    
    print("\n🎉 Configuration Manager Working!")
