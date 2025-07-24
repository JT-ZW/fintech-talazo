# app/core/config.py
"""
Configuration settings for Talazo AgriFinance Platform.
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # API settings
    JSONIFY_PRETTYPRINT_REGULAR = True
    JSON_SORT_KEYS = False
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # ML Model settings
    ML_MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../models')
    
    # External API settings
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    SATELLITE_API_KEY = os.environ.get('SATELLITE_API_KEY')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../uploads')
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() == 'true'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    DEBUG = True
    DEVELOPMENT = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DEV_DATABASE_URL') or 
        'sqlite:///' + os.path.join(os.path.dirname(__file__), '../../instance/talazo_dev.db')
    )
    
    # Disable rate limiting in development
    RATELIMIT_ENABLED = False


class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable rate limiting in testing
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or 
        'sqlite:///' + os.path.join(os.path.dirname(__file__), '../../instance/talazo.db')
    )
    
    # Enable rate limiting
    RATELIMIT_ENABLED = True
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration class based on environment.
    
    Args:
        config_name (str, optional): Configuration name. 
                                   Defaults to 'default'.
    
    Returns:
        Config class: Configuration class instance.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])


def validate_config(app_config):
    """
    Validate critical configuration settings.
    
    Args:
        app_config: Flask app configuration object.
    
    Returns:
        list: List of validation errors, empty if valid.
    """
    errors = []
    
    # Check required environment variables for production
    if not app_config.get('DEBUG', False):
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        for var in required_vars:
            if not app_config.get(var):
                errors.append(f"Missing required configuration: {var}")
    
    # Validate database URL format
    db_url = app_config.get('SQLALCHEMY_DATABASE_URI')
    if db_url and not (db_url.startswith('sqlite://') or 
                      db_url.startswith('postgresql://') or 
                      db_url.startswith('mysql://')):
        errors.append("Invalid database URL format")
    
    return errors
