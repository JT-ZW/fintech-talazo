from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from .models import db
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Get the project root directory
    project_dir = Path(__file__).parent.parent
    instance_dir = os.path.join(project_dir, 'instance')
    
    # Make sure the instance directory exists
    os.makedirs(instance_dir, exist_ok=True)
    
    # Database path with absolute path
    db_path = os.path.join(instance_dir, 'talazo.db')
    
    # Load the default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_change_in_production'),
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
        JSON_SORT_KEYS=False,
    )
    
    print(f"Database path: {db_path}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Load the test config if passed
    if test_config:
        app.config.from_mapping(test_config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    
    # Import and register blueprints
    from .routes import main, api
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')
    
    # Import and register CLI commands if they exist
    try:
        from .cli import simulation
        app.cli.add_command(simulation)
    except ImportError:
        pass  # CLI commands are optional
    
    # Create required directories
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, 'logs'), exist_ok=True)
    
    # Set up logging
    if not app.debug:
        file_handler = RotatingFileHandler(
            os.path.join(app.instance_path, 'logs', 'talazo.log'),
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Talazo AgriFinance startup')
    
    # Create the database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created successfully')
        except Exception as e:
            app.logger.error(f'Error creating database tables: {e}')
    
    return app