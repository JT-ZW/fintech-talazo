# talazo/utils/errors.py
from flask import jsonify
import traceback
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception class for API errors"""
    
    def __init__(self, message, status_code=400, error_code=None, details=None):
        """
        Initialize API error
        
        Args:
            message (str): Error message
            status_code (int): HTTP status code
            error_code (str, optional): Application-specific error code
            details (dict, optional): Additional error details
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.error_code = error_code or f"ERR_{status_code}"
        self.details = details or {}
    
    def to_dict(self):
        """
        Convert error to dictionary for JSON response
        
        Returns:
            dict: Error information
        """
        error_dict = {
            'error': True,
            'code': self.error_code,
            'message': self.message
        }
        
        if self.details:
            error_dict['details'] = self.details
            
        return error_dict

class ValidationError(APIError):
    """Exception for validation errors"""
    
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )

class NotFoundError(APIError):
    """Exception for resource not found errors"""
    
    def __init__(self, message, resource_type=None, resource_id=None):
        details = {}
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
            
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details
        )

class AuthorizationError(APIError):
    """Exception for authorization errors"""
    
    def __init__(self, message="You do not have permission to access this resource"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )

class AuthenticationError(APIError):
    """Exception for authentication errors"""
    
    def __init__(self, message="Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )

def register_error_handlers(app):
    """
    Register error handlers for the Flask application
    
    Args:
        app (Flask): Flask application instance
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle APIError exceptions"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors"""
        return jsonify({
            'error': True,
            'code': 'BAD_REQUEST',
            'message': str(error) or 'Bad request'
        }), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle unauthorized errors"""
        return jsonify({
            'error': True,
            'code': 'UNAUTHORIZED',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle forbidden errors"""
        return jsonify({
            'error': True,
            'code': 'FORBIDDEN',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle resource not found errors"""
        return jsonify({
            'error': True,
            'code': 'NOT_FOUND',
            'message': 'The requested resource could not be found'
        }), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle internal server errors"""
        # Log the full error with traceback
        logger.error(f"Internal Server Error: {str(error)}\n{traceback.format_exc()}")
        
        return jsonify({
            'error': True,
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'An unexpected error occurred on the server'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        # Log the full error with traceback
        logger.error(f"Unexpected Error: {str(error)}\n{traceback.format_exc()}")
        
        return jsonify({
            'error': True,
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'An unexpected error occurred on the server'
        }), 500