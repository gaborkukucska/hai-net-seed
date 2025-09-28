# HAI-Net Configuration Management Module
# Constitutional compliance and secure configuration handling

__version__ = "0.1.0"

from .config_manager import ConfigManager
from .settings import HAINetSettings

__all__ = [
    "ConfigManager",
    "HAINetSettings"
]
