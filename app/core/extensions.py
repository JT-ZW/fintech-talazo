# app/core/extensions.py
"""
Flask extensions initialization.

This module contains all Flask extension instances that need to be 
shared across the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)


def create_error_response(message, status_code=400):
    """
    Create a standardized error response.
    
    Args:
        message (str): Error message.
        status_code (int): HTTP status code.
    
    Returns:
        dict: Standardized error response.
    """
    return {
        'success': False,
        'error': {
            'message': message,
            'status_code': status_code
        }
    }, status_code


def create_success_response(data=None, message="Success"):
    """
    Create a standardized success response.
    
    Args:
        data: Response data.
        message (str): Success message.
    
    Returns:
        dict: Standardized success response.
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return response
