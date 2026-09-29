import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(app):
    """Configure logging for atlas_core07"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    app.logger.handlers.clear()
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Error handler
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    app.logger.info('=' * 50)
    app.logger.info('atlas_core07 Backend Started')
    app.logger.info(f'Environment: {os.getenv("FLASK_ENV", "development")}')
    app.logger.info(f'AI Provider: {os.getenv("AI_PROVIDER", "mock")}')
    app.logger.info('=' * 50)

def get_logger(name):
    """Get logger instance"""
    return logging.getLogger(name)
