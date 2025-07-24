# app/utils/validators.py
"""
Validation utilities for Talazo AgriFinance Platform.
"""

import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """
    Validate Zimbabwe phone number format.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove spaces, dashes, and plus signs
    cleaned = re.sub(r'[\s\-\+]', '', phone)
    
    # Zimbabwe mobile patterns
    patterns = [
        r'^263[0-9]{9}$',      # International format
        r'^0[0-9]{9}$',        # National format
        r'^[0-9]{9}$'          # Local format
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)


def validate_national_id(national_id: str) -> bool:
    """
    Validate Zimbabwe national ID format.
    
    Args:
        national_id (str): National ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not national_id:
        return False
    
    # Zimbabwe national ID format: XX-XXXXXXX-X-XX
    pattern = r'^[0-9]{2}-[0-9]{6,7}-[A-Z]-[0-9]{2}$'
    return bool(re.match(pattern, national_id.upper()))


def validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> bool:
    """
    Validate geographic coordinates for Zimbabwe.
    
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        bool: True if valid coordinates for Zimbabwe, False otherwise
    """
    if latitude is None or longitude is None:
        return False
    
    # Zimbabwe approximate boundaries
    # Latitude: -22.5 to -15.5
    # Longitude: 25.0 to 33.0
    return (-22.5 <= latitude <= -15.5) and (25.0 <= longitude <= 33.0)


def validate_soil_ph(ph: float) -> bool:
    """
    Validate soil pH value.
    
    Args:
        ph (float): pH value to validate
        
    Returns:
        bool: True if valid pH range, False otherwise
    """
    return 0 <= ph <= 14


def validate_nutrient_level(level: float, nutrient_type: str) -> bool:
    """
    Validate nutrient level based on type.
    
    Args:
        level (float): Nutrient level value
        nutrient_type (str): Type of nutrient (nitrogen, phosphorus, potassium)
        
    Returns:
        bool: True if within reasonable range, False otherwise
    """
    if level < 0:
        return False
    
    # Maximum reasonable values (mg/kg)
    max_values = {
        'nitrogen': 200,
        'phosphorus': 150,
        'potassium': 1000,
        'organic_matter': 15  # percentage
    }
    
    max_val = max_values.get(nutrient_type.lower(), 1000)
    return level <= max_val


def validate_farm_size(size: float) -> bool:
    """
    Validate farm size in hectares.
    
    Args:
        size (float): Farm size in hectares
        
    Returns:
        bool: True if reasonable farm size, False otherwise
    """
    # Reasonable range: 0.1 to 10000 hectares
    return 0.1 <= size <= 10000
