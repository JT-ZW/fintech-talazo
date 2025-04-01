import os
from flask import Flask, jsonify
from datetime import datetime

# Import configuration and extensions
from app.config import get_config
from app.extensions import init_extensions, db, create_error_response

# Import machine learning components
from app.soil_analyzer import SoilHealthIndex
from app.yield_predictor import YieldPredictor

# Import routes (Blueprints)
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.soil import soil_bp
from app.routes.loans import loan_bp

def create_app(config_name=None):
    """
    Application factory for creating Flask application
    
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
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(soil_bp, url_prefix='/api/soil')
    app.register_blueprint(loan_bp, url_prefix='/api/loans')
    
    # Initialize machine learning components
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Initialize ML components
        app.soil_analyzer = SoilHealthIndex()
        app.yield_predictor = YieldPredictor()
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return create_error_response(str(error), 400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        return create_error_response('Unauthorized access', 401)
    
    @app.errorhandler(403)
    def forbidden(error):
        return create_error_response('Forbidden', 403)
    
    @app.errorhandler(404)
    def not_found(error):
        return create_error_response('Resource not found', 404)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Unhandled Exception: {str(error)}')
        return create_error_response('Internal server error', 500)
    
    # Health check endpoint
    @app.route('/healthcheck')
    def healthcheck():
        """
        Provide basic application health status
        
        Returns:
            JSON: Application health information
        """
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name,
            'database_status': check_database_connection()
        }), 200
    
    return app

def check_database_connection():
    """
    Check database connectivity
    
    Returns:
        str: Database connection status
    """
    try:
        # Attempt a simple database query
        db.session.execute('SELECT 1')
        return 'connected'
    except Exception as e:
        return f'disconnected: {str(e)}'

def run():
    """
    Run the Flask development server
    """
    app = create_app()
    
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=app.config.get('DEBUG', False)
    )

# Allow direct script execution
if __name__ == '__main__':
    run()