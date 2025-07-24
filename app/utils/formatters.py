# app/utils/formatters.py
"""
Formatting utilities for Talazo AgriFinance Platform.
"""

from datetime import datetime
from typing import Optional


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format currency amount with proper symbol and formatting.
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code (USD, ZWL, etc.)
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return 'N/A'
    
    symbols = {
        'USD': '$',
        'ZWL': 'ZW$',
        'EUR': '€',
        'GBP': '£'
    }
    
    symbol = symbols.get(currency.upper(), currency)
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage value.
    
    Args:
        value (float): Percentage value (e.g., 0.85 for 85%)
        decimal_places (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        return 'N/A'
    
    percentage = value * 100 if value <= 1 else value
    return f"{percentage:.{decimal_places}f}%"


def format_date(date_obj: Optional[datetime], format_string: str = '%Y-%m-%d') -> str:
    """
    Format datetime object to string.
    
    Args:
        date_obj (datetime): Date object to format
        format_string (str): Format string
        
    Returns:
        str: Formatted date string
    """
    if date_obj is None:
        return 'N/A'
    
    return date_obj.strftime(format_string)


def format_soil_parameter(value: float, parameter_type: str) -> str:
    """
    Format soil parameter with appropriate units.
    
    Args:
        value (float): Parameter value
        parameter_type (str): Type of parameter
        
    Returns:
        str: Formatted parameter string with units
    """
    if value is None:
        return 'N/A'
    
    units = {
        'ph': '',
        'nitrogen': ' mg/kg',
        'phosphorus': ' mg/kg', 
        'potassium': ' mg/kg',
        'organic_matter': '%',
        'moisture': '%',
        'cec': ' cmol/kg'
    }
    
    unit = units.get(parameter_type.lower(), '')
    
    if parameter_type.lower() == 'ph':
        return f"{value:.1f}"
    else:
        return f"{value:.2f}{unit}"


def format_farm_size(size: float) -> str:
    """
    Format farm size with appropriate units.
    
    Args:
        size (float): Farm size in hectares
        
    Returns:
        str: Formatted farm size string
    """
    if size is None:
        return 'N/A'
    
    if size < 1:
        # Convert to square meters for small plots
        return f"{size * 10000:.0f} m²"
    else:
        return f"{size:.2f} ha"


def format_score(score: float) -> str:
    """
    Format viability score.
    
    Args:
        score (float): Score value (0-100)
        
    Returns:
        str: Formatted score string
    """
    if score is None:
        return 'N/A'
    
    return f"{score:.1f}/100"


def format_risk_level(risk_level: str) -> str:
    """
    Format risk level for display.
    
    Args:
        risk_level (str): Risk level code
        
    Returns:
        str: Formatted risk level string
    """
    if not risk_level:
        return 'Unknown'
    
    risk_display = {
        'LOW': 'Low Risk',
        'MEDIUM_LOW': 'Medium-Low Risk',
        'MEDIUM': 'Medium Risk', 
        'MEDIUM_HIGH': 'Medium-High Risk',
        'HIGH': 'High Risk'
    }
    
    return risk_display.get(risk_level.upper(), risk_level.title())
