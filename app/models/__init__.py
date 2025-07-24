# app/models/__init__.py
"""
Database models for Talazo AgriFinance Platform.
"""

from app.core.extensions import db

# Import all models here for easy access
from .farmer import Farmer, FarmerSchema
from .soil_sample import SoilSample, SoilSampleSchema
from .credit_history import CreditHistory, CreditHistorySchema
from .loan_application import LoanApplication, LoanApplicationSchema
from .insurance_policy import InsurancePolicy, InsurancePolicySchema

# Export all models and schemas
__all__ = [
    'db',
    'Farmer', 'FarmerSchema',
    'SoilSample', 'SoilSampleSchema', 
    'CreditHistory', 'CreditHistorySchema',
    'LoanApplication', 'LoanApplicationSchema',
    'InsurancePolicy', 'InsurancePolicySchema'
]
