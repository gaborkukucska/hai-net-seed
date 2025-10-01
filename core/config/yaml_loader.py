"""
HAI-Net YAML Settings Loader
Loads configuration from root settings.yaml file
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from core.config.settings import HAINetSettings

def load_yaml_settings(yaml_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load settings from YAML file
    
    Args:
        yaml_path: Path to YAML file (defaults to root settings.yaml)
        
    Returns:
        Dictionary of settings loaded from YAML
    """
    if yaml_path is None:
        # Default to root settings.yaml
        yaml_path = Path(__file__).parent.parent.parent / "settings.yaml"
    
    if not yaml_path.exists():
        logging.warning(f"Settings file not found: {yaml_path}")
        return {}
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            settings_data = yaml.safe_load(f) or {}
        
        logging.info(f"Loaded settings from {yaml_path}")
        return settings_data
        
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML settings file: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error loading settings file: {e}")
        return {}

def convert_yaml_to_hainet_settings(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert YAML settings to HAINetSettings format
    
    Args:
        yaml_data: Raw YAML data
        
    Returns:
        Settings in HAINetSettings format
    """
    settings = {}
    
    # Logging settings
    if 'logging' in yaml_data:
        log_config = yaml_data['logging']
        settings['log_level'] = log_config.get('level', 'INFO')
        settings['debug_mode'] = log_config.get('level', 'INFO') == 'DEBUG'
    
    # Node settings
    if 'node' in yaml_data:
        node_config = yaml_data['node']
        settings['node_role'] = node_config.get('role', 'master')
        settings['local_hub_name'] = node_config.get('name', 'HAI-Net Local Hub')
    
    # Network settings
    if 'network' in yaml_data:
        network_config = yaml_data['network']
        settings['api_port'] = network_config.get('web_port', 8000)
        settings['web_ui_port'] = network_config.get('api_port', 8080)
        settings['p2p_port'] = network_config.get('p2p_port', 4001)
    
    # Development settings
    if 'development' in yaml_data:
        dev_config = yaml_data['development']
        settings['debug_mode'] = dev_config.get('debug_mode', False)
    
    # Constitutional settings
    if 'constitutional' in yaml_data:
        const_config = yaml_data['constitutional']
        settings['constitutional_version'] = const_config.get('version', '1.0')
        
        # Privacy settings
        if 'privacy' in const_config:
            privacy = const_config['privacy']
            settings['data_sharing_consent'] = privacy.get('data_sharing_consent', False)
            settings['encryption_enabled'] = privacy.get('encryption_enabled', True)
            settings['watermarking_enabled'] = privacy.get('watermarking_enabled', True)
        
        # Human rights settings
        if 'human_rights' in const_config:
            hr = const_config['human_rights']
            settings['accessibility_mode'] = hr.get('accessibility_mode', True)
            settings['user_override_enabled'] = hr.get('user_override_enabled', True)
            settings['bias_detection_enabled'] = hr.get('bias_detection', True)
        
        # Decentralization settings
        if 'decentralization' in const_config:
            decent = const_config['decentralization']
            settings['central_authority_disabled'] = decent.get('central_authority_disabled', True)
            settings['local_first'] = decent.get('local_first', True)
            settings['mesh_networking_enabled'] = decent.get('mesh_networking', True)
        
        # Community settings
        if 'community' in const_config:
            community = const_config['community']
            settings['community_participation'] = community.get('participation_enabled', True)
            settings['environmental_mode'] = community.get('environmental_mode', True)
            settings['irl_prioritization'] = community.get('irl_prioritization', True)
    
    # AI settings
    if 'ai' in yaml_data:
        ai_config = yaml_data['ai']
        settings['llm_backend'] = ai_config.get('backend', 'ollama')
        settings['default_model'] = ai_config.get('default_model', 'llama2:7b')
        settings['voice_stt_enabled'] = ai_config.get('voice_enabled', True)
        settings['voice_tts_enabled'] = ai_config.get('voice_enabled', True)
    
    # Resource settings
    if 'resources' in yaml_data:
        res_config = yaml_data['resources']
        settings['max_cpu_usage'] = res_config.get('max_cpu_percent', 80.0)
        settings['max_memory_usage'] = res_config.get('max_memory_percent', 85.0)
        settings['min_disk_space_gb'] = res_config.get('min_disk_space_gb', 10.0)
    
    # Security settings
    if 'security' in yaml_data:
        sec_config = yaml_data['security']
        settings['session_timeout_minutes'] = sec_config.get('session_timeout_minutes', 60)
        settings['max_login_attempts'] = sec_config.get('max_login_attempts', 3)
        settings['require_2fa'] = sec_config.get('require_2fa', False)
    
    # Guardian settings
    if 'guardian' in yaml_data:
        guard_config = yaml_data['guardian']
        settings['guardian_enabled'] = guard_config.get('enabled', True)
        settings['guardian_mode'] = guard_config.get('mode', 'educational')
        settings['auto_correction'] = guard_config.get('auto_correction', True)
    
    return settings

def load_settings_from_yaml() -> HAINetSettings:
    """
    Load HAINet settings from root settings.yaml file
    
    Returns:
        Configured HAINetSettings object
    """
    # Load YAML data
    yaml_data = load_yaml_settings()
    
    # Convert to HAINetSettings format
    settings_dict = convert_yaml_to_hainet_settings(yaml_data)
    
    # Create HAINetSettings object with YAML overrides
    try:
        settings = HAINetSettings(**settings_dict)
        
        # Store original YAML data for reference
        settings._yaml_config = yaml_data
        
        return settings
        
    except Exception as e:
        logging.error(f"Error creating settings from YAML: {e}")
        # Fall back to default settings
        return HAINetSettings()

def get_logging_config_from_yaml() -> Dict[str, Any]:
    """
    Get logging configuration specifically from YAML
    
    Returns:
        Logging configuration dictionary
    """
    yaml_data = load_yaml_settings()
    
    default_config = {
        'level': 'INFO',
        'save_to_file': True,
        'console_output': True
    }
    
    if 'logging' in yaml_data:
        log_config = yaml_data['logging']
        return {
            'level': log_config.get('level', 'INFO'),
            'save_to_file': log_config.get('save_to_file', True),
            'console_output': log_config.get('console_output', True)
        }
    
    return default_config

if __name__ == "__main__":
    # Test YAML settings loading
    print("Testing YAML Settings Loader")
    print("=" * 40)
    
    # Load settings
    settings = load_settings_from_yaml()
    
    print(f"✅ Settings loaded successfully")
    print(f"Log Level: {settings.log_level}")
    print(f"Node Role: {settings.node_role}")
    print(f"Debug Mode: {settings.debug_mode}")
    print(f"Constitutional Version: {settings.constitutional_version}")
    
    # Test logging config
    log_config = get_logging_config_from_yaml()
    print(f"Logging Config: {log_config}")
