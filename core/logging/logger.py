# START OF FILE core/logging/logger.py
"""
HAI-Net Constitutional Logging System
Provides audit trail and compliance monitoring
"""

import logging
import logging.handlers
import json
import time
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
import threading

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from core.config.settings import HAINetSettings


class ConstitutionalLogFilter(logging.Filter):
    """
    Filter to add constitutional compliance context to log records
    """
    
    def __init__(self, constitutional_version: str = "1.0"):
        super().__init__()
        self.constitutional_version = constitutional_version
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add constitutional context to every log record"""
        record.constitutional_version = self.constitutional_version
        record.compliance_timestamp = time.time()
        record.thread_id = threading.get_ident()
        return True


class ConstitutionalFormatter(logging.Formatter):
    """
    Custom formatter that ensures constitutional compliance information
    """
    
    def __init__(self):
        super().__init__()
        self.base_format = "[{asctime}] [{constitutional_version}] [{levelname}] [{name}] [{thread_id}] {message}"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with constitutional compliance info"""
        # Ensure constitutional fields exist
        if not hasattr(record, 'constitutional_version'):
            record.constitutional_version = "1.0"
        if not hasattr(record, 'thread_id'):
            record.thread_id = threading.get_ident()
        
        # Format timestamp
        record.asctime = datetime.fromtimestamp(record.created).isoformat()
        
        # Ensure message field exists
        if not hasattr(record, 'message'):
            record.message = record.getMessage()
        
        # Apply base formatting
        formatted = self.base_format.format(**record.__dict__)
        
        # Add constitutional compliance marker
        if hasattr(record, 'constitutional_event'):
            formatted = f"[CONSTITUTIONAL] {formatted}"
        
        return formatted


class HAINetLogger:
    """
    Constitutional compliance-aware logger for HAI-Net
    Provides audit trail and privacy protection with categorized debug logging
    """
    
    def __init__(self, name: str, settings: Optional['HAINetSettings'] = None):
        self.name = name
        self.settings = settings
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
        # Constitutional compliance tracking
        self.compliance_events: List[Dict[str, Any]] = []
        self.violation_count = 0
        
        # Debug categorization
        self.debug_categories = {
            'init': 'INIT',
            'network': 'NETWORK', 
            'crypto': 'CRYPTO',
            'ai': 'AI',
            'storage': 'STORAGE',
            'web': 'WEB',
            'agent': 'AGENT',
            'guardian': 'GUARDIAN',
            'identity': 'IDENTITY',
            'config': 'CONFIG',
            'memory': 'MEMORY',
            'p2p': 'P2P',
            'discovery': 'DISCOVERY',
            'role': 'ROLE',
            'websocket': 'WEBSOCKET',
            'api': 'API',
            'constitutional': 'CONSTITUTIONAL',
            'violation': 'VIOLATION',
            'performance': 'PERFORMANCE',
            'error': 'ERROR'
        }
        
    def _setup_logger(self):
        """Set up logger with constitutional compliance"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        level = getattr(logging, (self.settings.log_level if self.settings else "INFO"))
        self.logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.addFilter(ConstitutionalLogFilter())
        console_handler.setFormatter(ConstitutionalFormatter())
        
        self.logger.addHandler(console_handler)
        
        # Create file handler if settings available
        if self.settings:
            self._setup_file_logging()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _setup_file_logging(self):
        """Set up file-based logging with rotation"""
        try:
            # Determine logs directory
            if self.settings and hasattr(self.settings, 'logs_dir'):
                logs_dir = self.settings.logs_dir
            else:
                # Default logs directory for when settings object not available
                logs_dir = Path("logs")
            
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if file logging is enabled in settings.yaml
            try:
                import yaml  # type: ignore
            except ImportError:
                yaml = None  # type: ignore
            
            settings_file = Path("settings.yaml")
            file_logging_enabled = True  # Default to enabled
            
            if yaml and settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        config = yaml.safe_load(f)
                        file_logging_enabled = config.get('logging', {}).get('save_to_file', True)
                except Exception:
                    pass  # If we can't read the config, default to enabled
            
            if not file_logging_enabled:
                return  # Skip file logging if disabled
            
            # Main log file
            main_log = logs_dir / f"{self.name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                main_log,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # Capture everything in files
            file_handler.addFilter(ConstitutionalLogFilter())
            file_handler.setFormatter(ConstitutionalFormatter())
            
            self.logger.addHandler(file_handler)
            
            # Log that file logging was successfully set up
            print(f"✅ File logging enabled: {main_log}")
            
            # Constitutional compliance log
            compliance_log = logs_dir / "constitutional_compliance.log"
            compliance_handler = logging.handlers.RotatingFileHandler(
                compliance_log,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=10,
                encoding='utf-8'
            )
            compliance_handler.setLevel(logging.INFO)
            compliance_handler.addFilter(ConstitutionalLogFilter())
            compliance_handler.setFormatter(ConstitutionalFormatter())
            
            # Only log constitutional events to compliance log
            class ConstitutionalOnlyFilter(logging.Filter):
                def filter(self, record: logging.LogRecord) -> bool:
                    return hasattr(record, 'constitutional_event')
            
            compliance_handler.addFilter(ConstitutionalOnlyFilter())
            self.logger.addHandler(compliance_handler)
            
        except Exception as e:
            print(f"⚠️ File logging setup failed: {e}")
            # Continue without file logging rather than crash
    
    def log_constitutional_event(self, event_type: str, details: Dict[str, Any], level: str = "INFO") -> None:
        """
        Log a constitutional compliance event
        
        Args:
            event_type: Type of constitutional event
            details: Event details and context
            level: Log level
        """
        event_data: Dict[str, Any] = {
            "event_type": event_type,
            "timestamp": time.time(),
            "details": details,
            "constitutional_version": "1.0"
        }
        
        # Add to compliance tracking
        self.compliance_events.append(event_data)
        
        # Create log record with constitutional marker
        log_level = getattr(logging, level.upper())
        record = self.logger.makeRecord(
            self.logger.name,
            log_level,
            __file__,
            0,
            f"Constitutional Event: {event_type} - {json.dumps(details)}",
            (),
            None
        )
        
        # Mark as constitutional event
        record.constitutional_event = True
        record.event_type = event_type
        record.event_data = event_data
        
        self.logger.handle(record)
    
    def log_privacy_event(self, action: str, data_type: str, user_consent: bool = False):
        """Log privacy-related events (Article I compliance)"""
        self.log_constitutional_event("PRIVACY", {
            "action": action,
            "data_type": data_type,
            "user_consent": user_consent,
            "principle": "Privacy First"
        })
    
    def log_human_rights_event(self, action: str, user_control: bool = True):
        """Log human rights protection events (Article II compliance)"""
        self.log_constitutional_event("HUMAN_RIGHTS", {
            "action": action,
            "user_control": user_control,
            "principle": "Human Rights Protection"
        })
    
    def log_decentralization_event(self, action: str, local_processing: bool = True):
        """Log decentralization events (Article III compliance)"""
        self.log_constitutional_event("DECENTRALIZATION", {
            "action": action,
            "local_processing": local_processing,
            "principle": "Decentralization Imperative"
        })
    
    def log_community_event(self, action: str, community_benefit: bool = True):
        """Log community focus events (Article IV compliance)"""
        self.log_constitutional_event("COMMUNITY", {
            "action": action,
            "community_benefit": community_benefit,
            "principle": "Community Focus"
        })
    
    def log_violation(self, violation_type: str, details: Dict[str, Any], severity: str = "WARNING") -> None:
        """
        Log constitutional violations with educational context
        
        Args:
            violation_type: Type of violation
            details: Violation details
            severity: Severity level
        """
        self.violation_count += 1
        
        violation_data: Dict[str, Any] = {
            "violation_type": violation_type,
            "severity": severity,
            "details": details,
            "violation_count": self.violation_count,
            "educational_note": "This violation was detected to protect constitutional principles"
        }
        
        self.log_constitutional_event("VIOLATION", violation_data, severity)
    
    def log_correction(self, correction_type: str, original_action: str, corrected_action: str):
        """Log constitutional corrections"""
        self.log_constitutional_event("CORRECTION", {
            "correction_type": correction_type,
            "original_action": original_action,
            "corrected_action": corrected_action,
            "educational_note": "Automatic correction applied for constitutional compliance"
        })
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of constitutional compliance events"""
        event_types: Dict[str, int] = {}
        for event in self.compliance_events:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "total_events": len(self.compliance_events),
            "violation_count": self.violation_count,
            "event_types": event_types,
            "compliance_rate": 1.0 - (self.violation_count / max(len(self.compliance_events), 1)),
            "last_event": self.compliance_events[-1] if self.compliance_events else None
        }
    
    def info(self, message: str, category: str = "general", function: str = "", **kwargs: Any) -> None:
        """Info level logging with categorization"""
        formatted_message = self._format_categorized_message(message, category, function)
        self.logger.info(formatted_message, **kwargs)
    
    def debug(self, message: str, category: str = "general", function: str = "", **kwargs: Any) -> None:
        """Debug level logging with categorization"""
        formatted_message = self._format_categorized_message(message, category, function)
        self.logger.debug(formatted_message, **kwargs)
    
    def warning(self, message: str, category: str = "general", function: str = "", **kwargs: Any) -> None:
        """Warning level logging with categorization"""
        formatted_message = self._format_categorized_message(message, category, function)
        self.logger.warning(formatted_message, **kwargs)
    
    def error(self, message: str, category: str = "error", function: str = "", **kwargs: Any) -> None:
        """Error level logging with categorization"""
        formatted_message = self._format_categorized_message(message, category, function)
        self.logger.error(formatted_message, **kwargs)
    
    def critical(self, message: str, category: str = "error", function: str = "", **kwargs: Any) -> None:
        """Critical level logging with categorization"""
        formatted_message = self._format_categorized_message(message, category, function)
        self.logger.critical(formatted_message, **kwargs)
    
    def _format_categorized_message(self, message: str, category: str, function: str) -> str:
        """Format message with category and function information for easy searching"""
        category_tag = self.debug_categories.get(category, category.upper())
        
        if function:
            return f"[{category_tag}::{function}] {message}"
        else:
            return f"[{category_tag}] {message}"
    
    # Convenience methods for specific categories
    def debug_init(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug initialization processes"""
        self.debug(message, category="init", function=function, **kwargs)
    
    def debug_network(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug network operations"""
        self.debug(message, category="network", function=function, **kwargs)
    
    def debug_crypto(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug cryptographic operations"""
        self.debug(message, category="crypto", function=function, **kwargs)
    
    def debug_ai(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug AI operations"""
        self.debug(message, category="ai", function=function, **kwargs)
    
    def debug_storage(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug storage operations"""
        self.debug(message, category="storage", function=function, **kwargs)
    
    def debug_web(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug web server operations"""
        self.debug(message, category="web", function=function, **kwargs)
    
    def debug_agent(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug agent operations"""
        self.debug(message, category="agent", function=function, **kwargs)
    
    def debug_constitutional(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug constitutional compliance"""
        self.debug(message, category="constitutional", function=function, **kwargs)
    
    def debug_performance(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Debug performance metrics"""
        self.debug(message, category="performance", function=function, **kwargs)
    
    def info_init(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Info initialization processes"""
        self.info(message, category="init", function=function, **kwargs)
    
    def info_network(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Info network operations"""
        self.info(message, category="network", function=function, **kwargs)
    
    def info_web(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Info web server operations"""
        self.info(message, category="web", function=function, **kwargs)
    
    def warning_constitutional(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Warning for constitutional issues"""
        self.warning(message, category="constitutional", function=function, **kwargs)
    
    def warning_network(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Warning for network issues"""
        self.warning(message, category="network", function=function, **kwargs)
    
    def error_constitutional(self, message: str, function: str = "", **kwargs: Any) -> None:
        """Error for constitutional violations"""
        self.error(message, category="constitutional", function=function, **kwargs)


# Global logger registry
_loggers: Dict[str, HAINetLogger] = {}
_default_settings: Optional['HAINetSettings'] = None


def set_default_settings(settings: 'HAINetSettings') -> None:
    """Set default settings for all loggers"""
    global _default_settings
    _default_settings = settings


def get_logger(name: str, settings: Optional['HAINetSettings'] = None) -> HAINetLogger:
    """
    Get or create a HAI-Net logger with constitutional compliance
    
    Args:
        name: Logger name
        settings: Optional settings (uses default if not provided)
        
    Returns:
        Constitutional logger instance
    """
    if name not in _loggers:
        logger_settings = settings or _default_settings
        _loggers[name] = HAINetLogger(name, logger_settings)
    
    return _loggers[name]


def log_system_start(component: str, version: str = "0.1.0"):
    """Log system component startup"""
    logger = get_logger("system")
    logger.log_constitutional_event("SYSTEM_START", {
        "component": component,
        "version": version,
        "constitutional_compliance": True
    })


def log_system_stop(component: str, clean_shutdown: bool = True):
    """Log system component shutdown"""
    logger = get_logger("system")
    logger.log_constitutional_event("SYSTEM_STOP", {
        "component": component,
        "clean_shutdown": clean_shutdown
    })


def get_all_compliance_summaries() -> Dict[str, Dict[str, Any]]:
    """Get compliance summaries for all loggers"""
    summaries: Dict[str, Dict[str, Any]] = {}
    for name, logger in _loggers.items():
        summaries[name] = logger.get_compliance_summary()
    
    return summaries


if __name__ == "__main__":
    # Test the logging system
    print("HAI-Net Constitutional Logging System Test")
    print("=" * 45)
    
    # Create test logger
    logger = get_logger("test")
    
    # Test basic logging
    logger.info("Testing HAI-Net constitutional logging")
    logger.debug("Debug message with constitutional compliance")
    
    # Test constitutional event logging
    logger.log_privacy_event("identity_creation", "DID", user_consent=True)
    logger.log_human_rights_event("user_authentication", user_control=True)
    logger.log_decentralization_event("local_processing", local_processing=True)
    logger.log_community_event("resource_sharing", community_benefit=True)
    
    # Test violation logging (educational)
    logger.log_violation("privacy_test", {
        "action": "test_violation",
        "detected_by": "test_system"
    }, "WARNING")
    
    # Test correction logging
    logger.log_correction("privacy_protection", "unsafe_action", "safe_action")
    
    # Get compliance summary
    summary = logger.get_compliance_summary()
    print(f"\nCompliance Summary:")
    print(f"Total Events: {summary['total_events']}")
    print(f"Violations: {summary['violation_count']}")
    print(f"Compliance Rate: {summary['compliance_rate']:.2%}")
    print(f"Event Types: {summary['event_types']}")
    
    print("\n✅ Constitutional Logging System Working!")
