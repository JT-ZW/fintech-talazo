import os
from datetime import timedelta

class Config:
    """Flask configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    JSONIFY_PRETTYPRINT_REGULAR = True
    JSON_SORT_KEYS = False
    CORS_HEADERS = 'Content-Type'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fintech.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}