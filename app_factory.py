# talazo/app_factory.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Import error handlers and utilities
from talazo.utils.errors import register_error_handlers
from talazo.utils.logging import configure_logging
from talazo.routes.loans import loan_bp
from talazo.routes.farmers import farmers_bp

# Import database and models
from talazo.models.base import db

def create_app(config_name=None):
    """
    Application factory for creating the Flask application
    
    Args:
        config_name (str, optional): Configuration environment name
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Determine configuration environment
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask application
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    
    # Load configuration
    from talazo.config import get_config
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Validate configuration
    from talazo.config import validate_config
    config_errors = validate_config(app.config)
    if config_errors:
        for error in config_errors:
            app.logger.warning(f"Configuration Warning: {error}")
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Set up logging
    configure_logging(app)
    
    # Initialize machine learning components
    initialize_ml_components(app)
    
    # Health check endpoint
    @app.route('/healthcheck')
    def healthcheck():
        """
        Provide application health status
        
        Returns:
            JSON: Application health information
        """
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name,
            'database_status': check_database_connection(app)
        }), 200
    
    # Initialize database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created successfully')
        except Exception as e:
            app.logger.error(f'Error creating database tables: {e}')
    
    return app

def initialize_extensions(app):
    """
    Initialize Flask extensions
    
    Args:
        app (Flask): Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Migrate
    Migrate(app, db)
    
    # Initialize Marshmallow
    Marshmallow(app)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '100 per day')]
    )
    
    return app

def register_blueprints(app):
    """
    Register application blueprints
    
    Args:
        app (Flask): Flask application instance
    """
    # Import blueprints
    from talazo.routes.main import main_bp
    from talazo.routes.auth import auth_bp
    from talazo.routes.soil import soil_bp
    from talazo.routes.loans import loan_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(soil_bp, url_prefix='/api/soil')
    app.register_blueprint(loan_bp, url_prefix='/api/loans')

def initialize_ml_components(app):
    """
    Initialize machine learning components
    
    Args:
        app (Flask): Flask application instance
    """
    # Import machine learning components
    from talazo.ml.soil_analyzer import SoilHealthIndex
    from talazo.ml.yield_predictor import YieldPredictor
    
    # Initialize global ML components
    with app.app_context():
        app.soil_analyzer = SoilHealthIndex()
        app.yield_predictor = YieldPredictor()
        app.logger.info('ML components initialized successfully')

def check_database_connection(app):
    """
    Check database connectivity
    
    Args:
        app (Flask): Flask application instance
        
    Returns:
        str: Database connection status
    """
    try:
        with app.app_context():
            # Attempt a simple database query
            db.session.execute('SELECT 1')
            return 'connected'
    except Exception as e:
        return f'disconnected: {str(e)}'

def init_database(app):
    """
    Initialize the database with initial data
    
    Args:
        app (Flask): Flask application instance
    """
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if default admin exists
        from talazo.models.user import User, UserRole
        admin_exists = User.query.filter_by(username='admin').first()
        
        if not admin_exists:
            # Create a default admin user
            from werkzeug.security import generate_password_hash
            
            default_admin = User(
                username='admin',
                email='admin@talazoagritech.com',
                password_hash=generate_password_hash('admin123'),
                role=UserRole.ADMIN
            )
            
            db.session.add(default_admin)
            db.session.commit()
            app.logger.info("Created default admin user")