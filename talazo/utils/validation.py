# talazo/utils/validation.py
from functools import wraps
from flask import request, jsonify
import logging
from talazo.utils.errors import ValidationError

logger = logging.getLogger(__name__)

def validate_json_request(schema=None, required_fields=None):
    """
    Decorator to validate JSON request data
    
    Args:
        schema (dict, optional): Schema for validation
        required_fields (list, optional): List of required fields
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                raise ValidationError("Request must be JSON")
            
            data = request.json
            
            # Check for required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise ValidationError(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        details={'missing_fields': missing_fields}
                    )
            
            # TODO: Add schema validation if needed
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_soil_data(data):
    """
    Validate soil data input
    
    Args:
        data (dict): Soil data to validate
        
    Returns:
        dict: Validated soil data
        
    Raises:
        ValidationError: If validation fails
    """
    # Required fields for soil data
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
        raise ValidationError(
            f"Missing required soil parameters: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )
    
    # Validate and convert values
    validated_data = {}
    
    # Parameter validation specs
    validations = {
        'ph_level': {'type': float, 'range': (0, 14)},
        'nitrogen_level': {'type': float, 'range': (0, 100)},
        'phosphorus_level': {'type': float, 'range': (0, 100)},
        'potassium_level': {'type': float, 'range': (0, 500)},
        'organic_matter': {'type': float, 'range': (0, 20)},
        'cation_exchange_capacity': {'type': float, 'range': (0, 50)},
        'moisture_content': {'type': float, 'range': (0, 100)}
    }
    
    # Process each parameter
    validation_errors = {}
    
    for param, spec in validations.items():
        if param in data and data[param] is not None:
            try:
                # Convert to correct type
                value = spec['type'](data[param])
                
                # Check range if specified
                if 'range' in spec:
                    min_val, max_val = spec['range']
                    if not (min_val <= value <= max_val):
                        validation_errors[param] = f"Value must be between {min_val} and {max_val}"
                        continue
                
                # Add validated parameter
                validated_data[param] = value
                
            except (ValueError, TypeError):
                validation_errors[param] = f"Invalid value type, expected {spec['type'].__name__}"
    
    # If there are validation errors, raise exception
    if validation_errors:
        raise ValidationError(
            "Invalid soil parameter values",
            details={'validation_errors': validation_errors}
        )
    
    return validated_data

def validate_farmer_data(data):
    """
    Validate farmer profile data
    
    Args:
        data (dict): Farmer data to validate
        
    Returns:
        dict: Validated farmer data
        
    Raises:
        ValidationError: If validation fails
    """
    required_fields = ['full_name', 'phone_number']
    
    # Check for missing required fields
    missing_fields = [
        field for field in required_fields 
        if field not in data or not data[field]
    ]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required farmer information: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )
    
    # Additional validation could be added here
    
    return data

def validate_loan_request(data):
    """
    Validate loan request data
    
    Args:
        data (dict): Loan request data to validate
        
    Returns:
        dict: Validated loan data
        
    Raises:
        ValidationError: If validation fails
    """
    required_fields = [
        'amount',
        'purpose',
        'term_months'
    ]
    
    # Check for missing required fields
    missing_fields = [
        field for field in required_fields 
        if field not in data or data[field] is None
    ]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required loan information: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )
    
    validation_errors = {}
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            validation_errors['amount'] = "Loan amount must be greater than zero"
    except (ValueError, TypeError):
        validation_errors['amount'] = "Invalid loan amount"
    
    # Validate term_months
    try:
        term_months = int(data['term_months'])
        if term_months <= 0:
            validation_errors['term_months'] = "Loan term must be greater than zero"
    except (ValueError, TypeError):
        validation_errors['term_months'] = "Invalid loan term"
    
    # If there are validation errors, raise exception
    if validation_errors:
        raise ValidationError(
            "Invalid loan request data",
            details={'validation_errors': validation_errors}
        )
    
    return data