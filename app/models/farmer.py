# app/models/farmer.py
"""
Farmer model and schema for Talazo AgriFinance Platform.
"""

from datetime import datetime
from app.core.extensions import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate


class Farmer(db.Model):
    """Farmer model representing farm operators in the system."""
    
    __tablename__ = 'farmers'
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal information
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    national_id = db.Column(db.String(30), unique=True)
    address = db.Column(db.String(200))
    
    # Location data
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    district = db.Column(db.String(50))
    province = db.Column(db.String(50))
    
    # Farming details
    farming_experience_years = db.Column(db.Integer)
    total_land_area = db.Column(db.Float)  # in hectares
    primary_crop = db.Column(db.String(50))
    secondary_crops = db.Column(db.String(200))  # comma-separated
    
    # Financial information
    monthly_income = db.Column(db.Float)
    other_income_sources = db.Column(db.String(200))
    banking_status = db.Column(db.String(20))  # banked, unbanked, underbanked
    
    # Timestamps
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Relationships removed temporarily to avoid circular import issues
    # soil_samples = db.relationship('SoilSample', backref='farmer', lazy=True, cascade='all, delete-orphan')
    # credit_history = db.relationship('CreditHistory', backref='farmer', lazy=True, cascade='all, delete-orphan')
    # loan_applications = db.relationship('LoanApplication', backref='farmer', lazy=True, cascade='all, delete-orphan')
    # insurance_policies = db.relationship('InsurancePolicy', backref='farmer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Farmer {self.full_name}>'
    
    def get_latest_soil_sample(self):
        """Get the most recent soil sample for this farmer."""
        # Temporarily disabled to avoid import issues
        # from app.models.soil_sample import SoilSample
        # return SoilSample.query.filter_by(farmer_id=self.id)\
        #                      .order_by(SoilSample.collection_date.desc())\
        #                      .first()
        return None
    
    def get_current_credit_score(self):
        """Get the current credit score based on latest soil sample."""
        latest_sample = self.get_latest_soil_sample()
        if latest_sample:
            return latest_sample.financial_index_score
        return None
    
    def get_risk_level(self):
        """Get the current risk level based on latest soil sample."""
        latest_sample = self.get_latest_soil_sample()
        if latest_sample:
            return latest_sample.risk_level
        return None
    
    def get_loan_eligibility(self):
        """Check loan eligibility based on credit score and risk level."""
        credit_score = self.get_current_credit_score()
        risk_level = self.get_risk_level()
        
        if not credit_score or not risk_level:
            return {'eligible': False, 'reason': 'No soil data available'}
        
        if credit_score >= 70 and risk_level in ['LOW', 'MEDIUM_LOW']:
            return {'eligible': True, 'max_amount': credit_score * 100}
        elif credit_score >= 50:
            return {'eligible': True, 'max_amount': credit_score * 50}
        else:
            return {'eligible': False, 'reason': 'Credit score too low'}
    
    def to_dict(self):
        """Convert farmer instance to dictionary."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'district': self.district,
            'province': self.province,
            'farming_experience_years': self.farming_experience_years,
            'total_land_area': self.total_land_area,
            'primary_crop': self.primary_crop,
            'banking_status': self.banking_status,
            'current_credit_score': self.get_current_credit_score(),
            'risk_level': self.get_risk_level(),
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'verification_status': self.verification_status,
            'is_active': self.is_active
        }


from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class FarmerSchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for Farmer model."""
    
    class Meta:
        model = Farmer
        load_instance = True
        include_fk = True
    
    # Validation
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone_number = fields.Str(validate=validate.Length(max=20))
    email = fields.Email()
    total_land_area = fields.Float(validate=validate.Range(min=0))
    farming_experience_years = fields.Int(validate=validate.Range(min=0, max=100))
    
    # Read-only fields
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    current_credit_score = fields.Method("get_current_credit_score", dump_only=True)
    risk_level = fields.Method("get_risk_level", dump_only=True)
    loan_eligibility = fields.Method("get_loan_eligibility", dump_only=True)
    
    def get_current_credit_score(self, obj):
        return obj.get_current_credit_score()
    
    def get_risk_level(self, obj):
        return obj.get_risk_level()
    
    def get_loan_eligibility(self, obj):
        return obj.get_loan_eligibility()
