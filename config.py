import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    # Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secret-development-key')
    APPLICATION_NAME = 'TalazoAgritech'
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL statement logging
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Security Settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = '100 per day'
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/application.log'
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@talazoagritech.com')
    
    # External Services
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    # Machine Learning Model Settings
    MODEL_STORAGE_PATH = 'models/'
    
    # Feature Flags
    FEATURES = {
        'SOIL_HEALTH_PREDICTION': True,
        'LOAN_RISK_ASSESSMENT': True,
        'USER_REGISTRATION': True,
        'ADVANCED_ANALYTICS': False
    }

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL', 
        'sqlite:///development.db'
    )
    SQLALCHEMY_ECHO = True  # Log SQL statements
    RATELIMIT_ENABLED = False  # Disable rate limiting in dev
    
    # Relaxed security for development
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable rate limiting during tests
    RATELIMIT_ENABLED = False
    
    # Minimize logging during tests
    LOG_LEVEL = 'ERROR'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    
    # Production database (use environment variable)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'PRODUCTION_DATABASE_URL', 
        'postgresql://user:password@localhost/talazo_production'
    )
    
    # Enhanced security for production
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # More aggressive rate limiting
    RATELIMIT_DEFAULT = '1000 per day'
    
    # Logging to file in production
    LOG_LEVEL = 'WARNING'

class StagingConfig(Config):
    """Staging environment configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'STAGING_DATABASE_URL', 
        'postgresql://user:password@localhost/talazo_staging'
    )
    
    # Enable most features but with some production-like constraints
    FEATURES = {
        **Config.FEATURES,
        'ADVANCED_ANALYTICS': True
    }

def get_config():
    """
    Get the appropriate configuration based on the current environment.
    
    Uses the FLASK_ENV environment variable to determine the config.
    Defaults to development if not specified.
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'staging': StagingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)

# Helper function to validate configuration
def validate_config(config):
    """
    Validate the configuration to ensure critical settings are present.
    
    Args:
        config (Config): Configuration object to validate
    
    Returns:
        list: List of validation errors (empty list if no errors)
    """
    errors = []
    
    # Check for secret key
    if not config.SECRET_KEY or config.SECRET_KEY == 'your-very-secret-development-key':
        errors.append('SECRET_KEY is not set or using default value')
    
    # Check database URI
    if not config.SQLALCHEMY_DATABASE_URI:
        errors.append('Database URI is not configured')
    
    # Check mail configuration in production/staging
    if config.__class__.__name__ in ['ProductionConfig', 'StagingConfig']:
        if not config.MAIL_USERNAME or not config.MAIL_PASSWORD:
            errors.append('Email configuration is incomplete')
    
    return errors

# Example usage in application factory
def create_app():
    from flask import Flask
    from .models import db
    
    app = Flask(__name__)
    
    # Get appropriate configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Validate configuration
    config_errors = validate_config(app.config)
    if config_errors:
        # Log or handle configuration errors
        for error in config_errors:
            print(f"Configuration Error: {error}")
    
    # Initialize extensions
    db.init_app(app)
    
    return app