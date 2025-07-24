# app/core/errors.py
"""
Global error handlers for the Talazo AgriFinance Platform.
"""

from flask import jsonify, request
from werkzeug.http import HTTP_STATUS_CODES
from app.core.extensions import create_error_response


def register_error_handlers(app):
    """Register application error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify(create_error_response(
            "Bad request - please check your input data",
            400
        ))
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return jsonify(create_error_response(
            "Authentication required",
            401
        ))
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors.""" 
        return jsonify(create_error_response(
            "Access forbidden - insufficient permissions",
            403
        ))
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        if request.path.startswith('/api/'):
            return jsonify(create_error_response(
                "API endpoint not found",
                404
            ))
        # For non-API routes, you might want to render an HTML template
        return jsonify(create_error_response(
            "Resource not found",
            404
        ))
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify(create_error_response(
            f"Method {request.method} not allowed for this endpoint",
            405
        ))
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors."""
        return jsonify(create_error_response(
            "File too large - maximum upload size is 16MB",
            413
        ))
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        """Handle 429 Too Many Requests errors."""
        return jsonify(create_error_response(
            "Rate limit exceeded - please try again later",
            429
        ))
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        app.logger.error(f'Unhandled Exception: {str(error)}')
        return jsonify(create_error_response(
            "An internal server error occurred",
            500
        ))
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unhandled exceptions."""
        app.logger.error(f'Unexpected error: {str(error)}', exc_info=True)
        return jsonify(create_error_response(
            "An unexpected error occurred",
            500
        ))
