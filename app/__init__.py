# app/__init__.py
"""
Talazo AgriFinance Platform - Application Factory

This module creates and configures the Flask application instance.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

# Import core extensions
from app.core.extensions import db, ma, limiter
from app.core.config import get_config

# Import error handlers
from app.core.errors import register_error_handlers

# Import CLI commands  
from app.core.cli import register_cli_commands


def create_app(config_name=None):
    """
    Application factory for creating Flask application instances.
    
    Args:
        config_name (str, optional): Configuration environment name.
                                   Defaults to 'development'.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    # Determine configuration environment
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask application instance
    app = Flask(__name__, 
                instance_relative_config=True,
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Configure logging
    configure_logging(app)
    
    return app


def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Enable CORS for API endpoints
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })


def register_blueprints(app):
    """Register application blueprints."""
    # Import blueprints here to avoid circular imports
    from app.api.main import main_bp
    from app.api.auth import auth_bp  
    from app.api.farmers import farmers_bp
    from app.api.scoring import scoring_bp
    from app.api.loans import loans_bp
    from app.api.soil import soil_bp
    from app.api.iot import iot_bp
    
    # Main routes (dashboard, index pages)
    app.register_blueprint(main_bp)
    
    # API routes with prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(farmers_bp, url_prefix='/api/farmers')
    app.register_blueprint(scoring_bp, url_prefix='/api/scoring')
    app.register_blueprint(loans_bp, url_prefix='/api/loans')
    app.register_blueprint(soil_bp, url_prefix='/api/soil')
    app.register_blueprint(iot_bp, url_prefix='/api/iot')


def configure_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # Configure file logging for production
        log_dir = os.path.join(os.path.dirname(app.instance_path), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'talazo.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Talazo AgriFinance Platform startup')
