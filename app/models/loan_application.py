# app/models/loan_application.py
"""
Loan application model and schema for Talazo AgriFinance Platform.
"""

from datetime import datetime
from enum import Enum
from app.core.extensions import db, ma
from marshmallow import fields, validate


class ApplicationStatus(Enum):
    """Enumeration for loan application status."""
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    DISBURSED = 'disbursed'
    CANCELLED = 'cancelled'


class LoanPurpose(Enum):
    """Enumeration for loan purposes."""
    SEEDS_FERTILIZER = 'seeds_fertilizer'
    EQUIPMENT_PURCHASE = 'equipment_purchase'
    LAND_PREPARATION = 'land_preparation'
    IRRIGATION = 'irrigation'
    STORAGE_FACILITIES = 'storage_facilities'
    WORKING_CAPITAL = 'working_capital'
    EMERGENCY = 'emergency'
    OTHER = 'other'


class LoanApplication(db.Model):
    """Loan application model for tracking farmer loan requests."""
    
    __tablename__ = 'loan_applications'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Application details
    application_number = db.Column(db.String(20), unique=True, nullable=False)
    requested_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    purpose = db.Column(db.Enum(LoanPurpose), nullable=False)
    purpose_description = db.Column(db.Text)
    
    # Loan terms requested
    requested_term_months = db.Column(db.Integer)  # Duration in months
    preferred_interest_rate = db.Column(db.Float)
    collateral_offered = db.Column(db.String(200))
    collateral_value = db.Column(db.Float)
    
    # Financial information
    monthly_income = db.Column(db.Float)
    other_income = db.Column(db.Float)
    monthly_expenses = db.Column(db.Float)
    existing_debt = db.Column(db.Float)
    
    # Farm-specific information
    farm_size = db.Column(db.Float)  # hectares
    crop_type = db.Column(db.String(50))
    expected_yield = db.Column(db.Float)  # kg/ha
    expected_income = db.Column(db.Float)
    farming_plan = db.Column(db.Text)
    
    # Application status
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    submission_date = db.Column(db.DateTime)
    review_date = db.Column(db.DateTime)
    decision_date = db.Column(db.DateTime)
    disbursement_date = db.Column(db.DateTime)
    
    # Assessment results
    soil_score = db.Column(db.Float)  # From latest soil sample
    credit_score = db.Column(db.Float)  # Calculated credit score
    risk_assessment = db.Column(db.String(20))  # LOW, MEDIUM, HIGH
    viability_score = db.Column(db.Float)  # Overall farm viability score
    
    # Decision details
    approved_amount = db.Column(db.Float)
    approved_term_months = db.Column(db.Integer)
    approved_interest_rate = db.Column(db.Float)
    rejection_reason = db.Column(db.Text)
    conditions = db.Column(db.Text)
    
    # Review information
    reviewed_by = db.Column(db.String(100))
    reviewer_notes = db.Column(db.Text)
    financial_institution = db.Column(db.String(100))
    loan_officer = db.Column(db.String(100))
    
    # Supporting documents
    documents_submitted = db.Column(db.Text)  # JSON string of document list
    documents_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LoanApplication {self.application_number}>'
    
    def generate_application_number(self):
        """Generate unique application number."""
        import random
        import string
        
        timestamp = datetime.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"LA{timestamp}{random_part}"
    
    def calculate_debt_to_income_ratio(self):
        """Calculate debt-to-income ratio."""
        total_income = (self.monthly_income or 0) + (self.other_income or 0)
        if total_income > 0:
            return round((self.existing_debt or 0) / total_income, 4)
        return 0.0
    
    def calculate_loan_to_value_ratio(self):
        """Calculate loan-to-value ratio based on collateral."""
        if self.collateral_value and self.collateral_value > 0:
            return round((self.requested_amount or 0) / self.collateral_value, 4)
        return 0.0
    
    def calculate_affordability_ratio(self):
        """Calculate loan affordability based on income."""
        total_income = (self.monthly_income or 0) + (self.other_income or 0)
        net_income = total_income - (self.monthly_expenses or 0)
        
        if net_income > 0 and self.requested_term_months:
            monthly_payment = self.requested_amount / self.requested_term_months
            return round(monthly_payment / net_income, 4)
        return 0.0
    
    def get_eligibility_assessment(self):
        """Assess loan eligibility based on various factors."""
        assessment = {
            'eligible': False,
            'score': 0,
            'factors': [],
            'recommendations': []
        }
        
        score = 0
        
        # Soil score assessment
        if self.soil_score:
            if self.soil_score >= 80:
                score += 30
                assessment['factors'].append('Excellent soil health')
            elif self.soil_score >= 60:
                score += 20
                assessment['factors'].append('Good soil health')
            elif self.soil_score >= 40:
                score += 10
                assessment['factors'].append('Fair soil health')
            else:
                assessment['factors'].append('Poor soil health - improvement needed')
                assessment['recommendations'].append('Improve soil health through organic matter addition')
        
        # Credit score assessment
        if self.credit_score:
            if self.credit_score >= 700:
                score += 25
                assessment['factors'].append('Excellent credit history')
            elif self.credit_score >= 600:
                score += 15
                assessment['factors'].append('Good credit history')
            elif self.credit_score >= 500:
                score += 10
                assessment['factors'].append('Fair credit history')
            else:
                assessment['factors'].append('Poor credit history')
                assessment['recommendations'].append('Build credit history through smaller loans')
        
        # Debt-to-income ratio
        dti = self.calculate_debt_to_income_ratio()
        if dti <= 0.3:
            score += 20
            assessment['factors'].append('Good debt-to-income ratio')
        elif dti <= 0.5:
            score += 10
            assessment['factors'].append('Acceptable debt-to-income ratio')
        else:
            assessment['factors'].append('High debt-to-income ratio')
            assessment['recommendations'].append('Reduce existing debt before applying')
        
        # Collateral assessment
        ltv = self.calculate_loan_to_value_ratio()
        if ltv <= 0.7:
            score += 15
            assessment['factors'].append('Adequate collateral coverage')
        elif ltv <= 0.9:
            score += 8
            assessment['factors'].append('Marginal collateral coverage')
        else:
            assessment['factors'].append('Insufficient collateral')
            assessment['recommendations'].append('Provide additional collateral or reduce loan amount')
        
        # Farming experience (from farmer relationship)
        if hasattr(self, 'farmer') and self.farmer.farming_experience_years:
            if self.farmer.farming_experience_years >= 5:
                score += 10
                assessment['factors'].append('Experienced farmer')
            elif self.farmer.farming_experience_years >= 2:
                score += 5
                assessment['factors'].append('Some farming experience')
        
        assessment['score'] = score
        assessment['eligible'] = score >= 50
        
        return assessment
    
    def to_dict(self):
        """Convert loan application to dictionary."""
        return {
            'id': self.id,
            'application_number': self.application_number,
            'farmer_id': self.farmer_id,
            'requested_amount': self.requested_amount,
            'currency': self.currency,
            'purpose': self.purpose.value if self.purpose else None,
            'purpose_description': self.purpose_description,
            'requested_term_months': self.requested_term_months,
            'status': self.status.value if self.status else None,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'decision_date': self.decision_date.isoformat() if self.decision_date else None,
            'soil_score': self.soil_score,
            'credit_score': self.credit_score,
            'risk_assessment': self.risk_assessment,
            'viability_score': self.viability_score,
            'approved_amount': self.approved_amount,
            'approved_interest_rate': self.approved_interest_rate,
            'debt_to_income_ratio': self.calculate_debt_to_income_ratio(),
            'loan_to_value_ratio': self.calculate_loan_to_value_ratio(),
            'affordability_ratio': self.calculate_affordability_ratio(),
            'eligibility_assessment': self.get_eligibility_assessment()
        }


from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class LoanApplicationSchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for LoanApplication model."""
    
    class Meta:
        model = LoanApplication
        load_instance = True
        include_fk = True
    
    # Required fields validation
    requested_amount = fields.Float(required=True, validate=validate.Range(min=1))
    purpose = fields.Enum(LoanPurpose, required=True)
    
    # Optional fields validation
    requested_term_months = fields.Int(validate=validate.Range(min=1, max=360))
    monthly_income = fields.Float(validate=validate.Range(min=0))
    farm_size = fields.Float(validate=validate.Range(min=0))
    
    # Read-only fields
    id = fields.Int(dump_only=True)
    application_number = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    debt_to_income_ratio = fields.Method("get_debt_to_income_ratio", dump_only=True)
    loan_to_value_ratio = fields.Method("get_loan_to_value_ratio", dump_only=True)
    affordability_ratio = fields.Method("get_affordability_ratio", dump_only=True)
    eligibility_assessment = fields.Method("get_eligibility_assessment", dump_only=True)
    
    def get_debt_to_income_ratio(self, obj):
        return obj.calculate_debt_to_income_ratio()
    
    def get_loan_to_value_ratio(self, obj):
        return obj.calculate_loan_to_value_ratio()
    
    def get_affordability_ratio(self, obj):
        return obj.calculate_affordability_ratio()
    
    def get_eligibility_assessment(self, obj):
        return obj.get_eligibility_assessment()
