# app/models/credit_history.py
"""
Credit history model and schema for Talazo AgriFinance Platform.
"""

from datetime import datetime
from enum import Enum
from app.core.extensions import db, ma
from marshmallow import fields, validate


class PaymentStatus(Enum):
    """Enumeration for payment status."""
    ON_TIME = 'on_time'
    LATE = 'late'
    DEFAULTED = 'defaulted'
    RESTRUCTURED = 'restructured'


class LoanType(Enum):
    """Enumeration for loan types."""
    AGRICULTURAL = 'agricultural'
    EQUIPMENT = 'equipment'
    SEED_CAPITAL = 'seed_capital'
    EMERGENCY = 'emergency'
    BUSINESS = 'business'
    PERSONAL = 'personal'


class CreditHistory(db.Model):
    """Credit history model tracking farmer's financial track record."""
    
    __tablename__ = 'credit_history'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Loan information
    loan_type = db.Column(db.Enum(LoanType), nullable=False)
    lender_name = db.Column(db.String(100), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Loan terms
    interest_rate = db.Column(db.Float)  # Annual percentage rate
    loan_term_months = db.Column(db.Integer)  # Duration in months
    collateral_type = db.Column(db.String(100))
    collateral_value = db.Column(db.Float)
    
    # Dates
    loan_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)
    
    # Payment details
    amount_paid = db.Column(db.Float, default=0.0)
    remaining_balance = db.Column(db.Float)
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False)
    
    # Performance metrics
    days_late = db.Column(db.Integer, default=0)
    late_fees = db.Column(db.Float, default=0.0)
    penalty_rate = db.Column(db.Float, default=0.0)
    
    # Additional information
    purpose = db.Column(db.String(200))  # Purpose of the loan
    guarantor_name = db.Column(db.String(100))
    guarantor_contact = db.Column(db.String(50))
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True)
    is_settled = db.Column(db.Boolean, default=False)
    settlement_date = db.Column(db.Date)
    
    # Notes and comments
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CreditHistory {self.id} - Farmer {self.farmer_id}>'
    
    def calculate_payment_ratio(self):
        """Calculate the payment ratio (amount paid / loan amount)."""
        if self.loan_amount and self.loan_amount > 0:
            return round((self.amount_paid or 0) / self.loan_amount, 4)
        return 0.0
    
    def calculate_risk_score(self):
        """Calculate individual risk score for this credit entry (0-100, higher is better)."""
        score = 100
        
        # Payment status impact
        if self.payment_status == PaymentStatus.ON_TIME:
            score += 0  # No penalty
        elif self.payment_status == PaymentStatus.LATE:
            score -= 20
        elif self.payment_status == PaymentStatus.DEFAULTED:
            score -= 50
        elif self.payment_status == PaymentStatus.RESTRUCTURED:
            score -= 30
        
        # Days late impact
        if self.days_late:
            if self.days_late <= 30:
                score -= 10
            elif self.days_late <= 90:
                score -= 25
            else:
                score -= 40
        
        # Payment ratio impact
        payment_ratio = self.calculate_payment_ratio()
        if payment_ratio >= 1.0:
            score += 10  # Bonus for full payment
        elif payment_ratio >= 0.8:
            score -= 5
        elif payment_ratio >= 0.5:
            score -= 15
        else:
            score -= 30
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def is_good_standing(self):
        """Check if this credit entry represents good standing."""
        return (
            self.payment_status in [PaymentStatus.ON_TIME, PaymentStatus.RESTRUCTURED] and
            self.days_late <= 30 and
            self.calculate_payment_ratio() >= 0.8
        )
    
    def get_loan_performance_category(self):
        """Categorize loan performance."""
        risk_score = self.calculate_risk_score()
        
        if risk_score >= 85:
            return 'Excellent'
        elif risk_score >= 70:
            return 'Good'
        elif risk_score >= 50:
            return 'Fair'
        elif risk_score >= 30:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def to_dict(self):
        """Convert credit history to dictionary."""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'loan_type': self.loan_type.value if self.loan_type else None,
            'lender_name': self.lender_name,
            'loan_amount': self.loan_amount,
            'currency': self.currency,
            'interest_rate': self.interest_rate,
            'loan_term_months': self.loan_term_months,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'amount_paid': self.amount_paid,
            'remaining_balance': self.remaining_balance,
            'payment_status': self.payment_status.value if self.payment_status else None,
            'days_late': self.days_late,
            'payment_ratio': self.calculate_payment_ratio(),
            'risk_score': self.calculate_risk_score(),
            'performance_category': self.get_loan_performance_category(),
            'is_good_standing': self.is_good_standing(),
            'is_settled': self.is_settled,
            'purpose': self.purpose
        }


from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class CreditHistorySchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for CreditHistory model."""
    
    class Meta:
        model = CreditHistory
        load_instance = True
        include_fk = True
    
    # Required fields validation
    loan_amount = fields.Float(required=True, validate=validate.Range(min=0))
    lender_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    loan_date = fields.Date(required=True)
    
    # Optional fields validation
    interest_rate = fields.Float(validate=validate.Range(min=0, max=100))
    loan_term_months = fields.Int(validate=validate.Range(min=1, max=360))
    amount_paid = fields.Float(validate=validate.Range(min=0))
    days_late = fields.Int(validate=validate.Range(min=0))
    
    # Read-only fields
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    payment_ratio = fields.Method("get_payment_ratio", dump_only=True)
    risk_score = fields.Method("get_risk_score", dump_only=True)
    performance_category = fields.Method("get_performance_category", dump_only=True)
    is_good_standing = fields.Method("get_good_standing", dump_only=True)
    
    def get_payment_ratio(self, obj):
        return obj.calculate_payment_ratio()
    
    def get_risk_score(self, obj):
        return obj.calculate_risk_score()
    
    def get_performance_category(self, obj):
        return obj.get_loan_performance_category()
    
    def get_good_standing(self, obj):
        return obj.is_good_standing()
