from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day"]
)

def init_extensions(app):
    """
    Initialize all Flask extensions
    
    Args:
        app (Flask): Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize database migrations
    migrate.init_app(app, db)
    
    # Initialize Marshmallow for serialization
    ma.init_app(app)
    
    # Configure CORS
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configure rate limiting
    limiter.init_app(app)
    
    # Additional extension configurations can be added here
    # For example, setting up custom configurations for each extension
    
    # Example of additional configuration
    limiter.limit("100 per day")(app)
    
    return app

# Optional: Create custom marshmallow fields or validators
class CustomValidationError(Exception):
    """Custom validation error for Marshmallow"""
    pass

def validate_not_empty(data):
    """
    Custom validator to ensure data is not empty
    
    Args:
        data: Data to validate
    
    Raises:
        CustomValidationError: If data is empty
    """
    if not data:
        raise CustomValidationError("Field cannot be empty")
    return data

# Example of a custom field type
class StrictStringField(ma.fields.String):
    """
    A more strict string field with additional validations
    """
    def __init__(self, *args, **kwargs):
        # Add min and max length validation
        kwargs.setdefault('validate', [])
        if 'min_length' not in kwargs:
            kwargs['min_length'] = 3
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 255
        
        super().__init__(*args, **kwargs)
    
    def _validate(self, value):
        """
        Additional custom validation
        
        Args:
            value: Value to validate
        
        Returns:
            Validated value
        
        Raises:
            ValidationError: If validation fails
        """
        # Remove leading/trailing whitespace
        value = value.strip() if isinstance(value, str) else value
        
        # Perform parent class validation
        value = super()._validate(value)
        
        # Additional custom checks can be added here
        return value

# Utility function for creating error responses
def create_error_response(message, status_code=400):
    """
    Create a standardized error response
    
    Args:
        message (str): Error message
        status_code (int, optional): HTTP status code. Defaults to 400.
    
    Returns:
        tuple: Response dictionary and status code
    """
    return {
        'error': True,
        'message': message
    }, status_code

# Example of a custom request parser/validator
class RequestValidator:
    """
    Centralized request validation utility
    """
    @staticmethod
    def validate_soil_data(data):
        """
        Validate soil data input
        
        Args:
            data (dict): Soil data to validate
        
        Returns:
            dict: Validated and cleaned data
        
        Raises:
            CustomValidationError: If validation fails
        """
        required_fields = [
            'ph_level', 
            'nitrogen_level', 
            'phosphorus_level', 
            'potassium_level'
        ]
        
        # Check for missing required fields
        missing_fields = [
            field for field in required_fields 
            if field not in data or data[field] is None
        ]
        
        if missing_fields:
            raise CustomValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Type and range validation
        try:
            validated_data = {
                'ph_level': float(data['ph_level']),
                'nitrogen_level': float(data['nitrogen_level']),
                'phosphorus_level': float(data['phosphorus_level']),
                'potassium_level': float(data['potassium_level'])
            }
        except (TypeError, ValueError):
            raise CustomValidationError("Invalid data types for soil parameters")
        
        # Additional range checks
        validations = {
            'ph_level': (0, 14),
            'nitrogen_level': (0, 100),
            'phosphorus_level': (0, 100),
            'potassium_level': (0, 500)
        }
        
        for param, (min_val, max_val) in validations.items():
            if not (min_val <= validated_data[param] <= max_val):
                raise CustomValidationError(
                    f"{param} must be between {min_val} and {max_val}"
                )
        
        return validated_data