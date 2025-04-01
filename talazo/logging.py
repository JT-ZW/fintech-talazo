import os
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import request, g
import time
import uuid

class ApplicationLogger:
    """
    Centralized logging management for the application
    Supports file logging, console logging, and error tracking
    """
    
    @staticmethod
    def initialize_logging(app):
        """
        Initialize logging configuration for the application
        
        Args:
            app (Flask): Flask application instance
        """
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Configure file logging
        file_handler = RotatingFileHandler(
            filename='logs/talazo_application.log', 
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d] - %(message)s'
        ))
        
        # Set log level from configuration
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
        file_handler.setLevel(log_level)
        
        # Add file handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        # Configure console logging for development
        if app.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            console_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(console_handler)
        
        # Initialize Sentry for error tracking if DSN is provided
        sentry_dsn = app.config.get('SENTRY_DSN')
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0  # Adjust in production
            )
    
    @staticmethod
    def log_request():
        """