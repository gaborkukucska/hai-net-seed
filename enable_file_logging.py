#!/usr/bin/env python3
"""
Simple script to enable file logging for HAI-Net
Fixes the circular import issue by creating a minimal file logger
"""

import logging
import logging.handlers
import yaml
import sys
from pathlib import Path
from datetime import datetime

def setup_file_logging():
    """Setup basic file logging for HAI-Net"""
    
    # Load YAML config
    try:
        with open('settings.yaml', 'r') as f:
            config = yaml.safe_load(f)
        logging_config = config.get('logging', {})
    except:
        logging_config = {'level': 'INFO', 'save_to_file': True}
    
    # Only proceed if file logging is enabled
    if not logging_config.get('save_to_file', True):
        print("File logging disabled in settings.yaml")
        return
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create log file with today's date
    log_file = logs_dir / f"hai-net-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Get log level
    log_level = logging_config.get('level', 'INFO')
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create file handler
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # Simple formatter that matches the constitutional format
    formatter = logging.Formatter(
        '[%(asctime)s] [1.0] [%(levelname)s] [%(name)s] [%(thread)d] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S.%f'
    )
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    
    # Remove any existing file handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        if isinstance(handler, (logging.FileHandler, logging.handlers.TimedRotatingFileHandler)):
            root_logger.removeHandler(handler)
    
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level)
    
    print(f"✅ File logging enabled: {log_file}")
    print(f"📝 Log level: {log_level}")
    print(f"💾 Logs will be saved to: {logs_dir.absolute()}")
    
    # Test the file logging
    logging.info("File logging system initialized successfully")
    
    return str(log_file)

if __name__ == "__main__":
    setup_file_logging()
