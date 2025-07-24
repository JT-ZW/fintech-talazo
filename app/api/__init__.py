# app/api/__init__.py
"""
API blueprints for Talazo AgriFinance Platform.
"""

from .main import main_bp
from .auth import auth_bp
from .farmers import farmers_bp
from .scoring import scoring_bp
from .loans import loans_bp
from .soil import soil_bp
from .iot import iot_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'farmers_bp', 
    'scoring_bp',
    'loans_bp',
    'soil_bp',
    'iot_bp'
]
