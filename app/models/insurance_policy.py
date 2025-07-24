# app/models/insurance_policy.py
"""
Insurance policy model and schema for Talazo AgriFinance Platform.
"""

from datetime import datetime, date
from enum import Enum
from app.core.extensions import db, ma
from marshmallow import fields, validate


class PolicyStatus(Enum):
    """Enumeration for insurance policy status."""
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    SUSPENDED = 'suspended'
    PENDING = 'pending'


class InsuranceType(Enum):
    """Enumeration for insurance types."""
    CROP_YIELD = 'crop_yield'
    WEATHER_INDEX = 'weather_index'
    MULTI_PERIL = 'multi_peril'
    LIVESTOCK = 'livestock'
    EQUIPMENT = 'equipment'


class ClaimStatus(Enum):
    """Enumeration for claim status."""
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PAID = 'paid'


class InsurancePolicy(db.Model):
    """Insurance policy model for tracking farmer insurance coverage."""
    
    __tablename__ = 'insurance_policies'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Policy details
    policy_number = db.Column(db.String(20), unique=True, nullable=False)
    insurance_type = db.Column(db.Enum(InsuranceType), nullable=False)
    status = db.Column(db.Enum(PolicyStatus), default=PolicyStatus.PENDING)
    
    # Coverage details
    coverage_amount = db.Column(db.Float, nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    deductible = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    # Policy period
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Premium payment
    premium_frequency = db.Column(db.String(20), default='annual')  # annual, semi-annual, quarterly, monthly
    premium_paid = db.Column(db.Float, default=0.0)
    next_premium_due = db.Column(db.Date)
    payment_status = db.Column(db.String(20), default='pending')  # paid, pending, overdue
    
    # Risk assessment
    risk_score = db.Column(db.Float)  # Based on soil health and other factors
    base_premium_rate = db.Column(db.Float)  # Base rate percentage
    risk_adjustment = db.Column(db.Float, default=0.0)  # Risk-based adjustment
    final_premium_rate = db.Column(db.Float)  # Final calculated rate
    
    # Coverage specifics
    covered_crops = db.Column(db.String(200))  # comma-separated list
    covered_area = db.Column(db.Float)  # hectares
    covered_perils = db.Column(db.Text)  # JSON list of covered perils
    exclusions = db.Column(db.Text)  # Policy exclusions
    
    # Weather/Index parameters (for index-based insurance)
    weather_station_id = db.Column(db.String(50))
    trigger_conditions = db.Column(db.Text)  # JSON conditions for payouts
    payout_schedule = db.Column(db.Text)  # JSON payout schedule
    
    # Provider information
    insurance_provider = db.Column(db.String(100), nullable=False)
    agent_name = db.Column(db.String(100))
    agent_contact = db.Column(db.String(50))
    
    # Claims information
    claims_count = db.Column(db.Integer, default=0)
    total_claims_amount = db.Column(db.Float, default=0.0)
    last_claim_date = db.Column(db.Date)
    
    # Additional information
    terms_conditions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<InsurancePolicy {self.policy_number}>'
    
    def generate_policy_number(self):
        """Generate unique policy number."""
        import random
        import string
        
        timestamp = datetime.now().strftime('%Y%m')
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"IP{timestamp}{random_part}"
    
    def is_active(self):
        """Check if policy is currently active."""
        today = date.today()
        return (
            self.status == PolicyStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )
    
    def days_until_expiry(self):
        """Calculate days until policy expires."""
        if self.end_date:
            return (self.end_date - date.today()).days
        return None
    
    def premium_balance(self):
        """Calculate outstanding premium balance."""
        return self.premium_amount - (self.premium_paid or 0)
    
    def coverage_utilization(self):
        """Calculate how much of coverage has been claimed."""
        if self.coverage_amount > 0:
            return round((self.total_claims_amount or 0) / self.coverage_amount, 4)
        return 0.0
    
    def calculate_premium_based_on_risk(self, soil_score, credit_score, weather_risk=1.0):
        """Calculate premium based on risk factors."""
        # Base premium rate (percentage of coverage amount)
        base_rate = self.base_premium_rate or 0.05  # Default 5%
        
        # Risk adjustment based on soil score
        soil_adjustment = 0.0
        if soil_score:
            if soil_score >= 80:
                soil_adjustment = -0.01  # 1% discount for excellent soil
            elif soil_score >= 60:
                soil_adjustment = 0.0   # No adjustment for good soil
            elif soil_score >= 40:
                soil_adjustment = 0.005  # 0.5% increase for fair soil
            else:
                soil_adjustment = 0.015  # 1.5% increase for poor soil
        
        # Credit score adjustment
        credit_adjustment = 0.0
        if credit_score:
            if credit_score >= 700:
                credit_adjustment = -0.005  # 0.5% discount
            elif credit_score < 500:
                credit_adjustment = 0.01   # 1% increase
        
        # Weather risk adjustment
        weather_adjustment = (weather_risk - 1.0) * 0.02
        
        # Calculate final rate
        final_rate = base_rate + soil_adjustment + credit_adjustment + weather_adjustment
        final_rate = max(0.02, min(0.15, final_rate))  # Cap between 2% and 15%
        
        # Update model
        self.risk_adjustment = soil_adjustment + credit_adjustment + weather_adjustment
        self.final_premium_rate = final_rate
        
        return self.coverage_amount * final_rate
    
    def get_payout_eligibility(self, event_data):
        """Check if conditions are met for insurance payout."""
        # This would be implemented based on specific insurance type
        # For now, return basic structure
        return {
            'eligible': False,
            'payout_amount': 0.0,
            'conditions_met': [],
            'conditions_failed': [],
            'assessment_date': datetime.utcnow().isoformat()
        }
    
    def to_dict(self):
        """Convert insurance policy to dictionary."""
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'farmer_id': self.farmer_id,
            'insurance_type': self.insurance_type.value if self.insurance_type else None,
            'status': self.status.value if self.status else None,
            'coverage_amount': self.coverage_amount,
            'premium_amount': self.premium_amount,
            'deductible': self.deductible,
            'currency': self.currency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'premium_frequency': self.premium_frequency,
            'premium_paid': self.premium_paid,
            'payment_status': self.payment_status,
            'risk_score': self.risk_score,
            'final_premium_rate': self.final_premium_rate,
            'covered_crops': self.covered_crops,
            'covered_area': self.covered_area,
            'insurance_provider': self.insurance_provider,
            'claims_count': self.claims_count,
            'total_claims_amount': self.total_claims_amount,
            'is_active': self.is_active(),
            'days_until_expiry': self.days_until_expiry(),
            'premium_balance': self.premium_balance(),
            'coverage_utilization': self.coverage_utilization()
        }


from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class InsurancePolicySchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for InsurancePolicy model."""
    
    class Meta:
        model = InsurancePolicy
        load_instance = True
        include_fk = True
    
    # Required fields validation
    coverage_amount = fields.Float(required=True, validate=validate.Range(min=1))
    premium_amount = fields.Float(required=True, validate=validate.Range(min=0))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    insurance_provider = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    
    # Optional fields validation
    deductible = fields.Float(validate=validate.Range(min=0))
    covered_area = fields.Float(validate=validate.Range(min=0))
    
    # Read-only fields
    id = fields.Int(dump_only=True)
    policy_number = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    is_active = fields.Method("get_is_active", dump_only=True)
    days_until_expiry = fields.Method("get_days_until_expiry", dump_only=True)
    premium_balance = fields.Method("get_premium_balance", dump_only=True)
    coverage_utilization = fields.Method("get_coverage_utilization", dump_only=True)
    
    def get_is_active(self, obj):
        return obj.is_active()
    
    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry()
    
    def get_premium_balance(self, obj):
        return obj.premium_balance()
    
    def get_coverage_utilization(self, obj):
        return obj.coverage_utilization()
