from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class RiskLevel(Enum):
    LOW = "Low Risk"
    MEDIUM_LOW = "Medium-Low Risk"
    MEDIUM = "Medium Risk"
    MEDIUM_HIGH = "Medium-High Risk"
    HIGH = "High Risk"

class CropType(Enum):
    MAIZE = "Maize"
    TOBACCO = "Tobacco"
    COTTON = "Cotton"
    WHEAT = "Wheat"
    SOYBEAN = "Soybean"
    GROUNDNUT = "Groundnut"

class Farmer(db.Model):
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    farm_size_hectares = db.Column(db.Float)
    crop_type = db.Column(db.Enum(CropType))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    national_id = db.Column(db.String(50), unique=True)
    farming_experience_years = db.Column(db.Integer)
    soil_samples = db.relationship('SoilSample', backref='farmer', lazy=True)
    credit_history = db.relationship('CreditHistory', backref='farmer', lazy=True)

    def __repr__(self):
        return f'<Farmer {self.name}>'

    def get_latest_soil_sample(self):
        return SoilSample.query.filter_by(farmer_id=self.id).order_by(SoilSample.collection_date.desc()).first()

    def get_average_credit_score(self):
        samples = SoilSample.query.filter_by(farmer_id=self.id).all()
        if not samples:
            return None
        return sum(sample.credit_score for sample in samples) / len(samples)

class SoilSample(db.Model):
    __tablename__ = 'soil_samples'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    collection_date = db.Column(db.Date, default=datetime.utcnow().date())
    
    # Soil metrics with validation ranges
    ph_level = db.Column(db.Float)  # Ideal range: 6.0-7.0
    nitrogen_level = db.Column(db.Float)  # mg/kg, Ideal: 20-40
    phosphorus_level = db.Column(db.Float)  # mg/kg, Ideal: 20-30
    potassium_level = db.Column(db.Float)  # mg/kg, Ideal: 150-250
    organic_matter = db.Column(db.Float)  # percentage, Ideal: 3-5%
    cation_exchange_capacity = db.Column(db.Float)  # cmol/kg, Ideal: 10-20
    moisture_content = db.Column(db.Float)  # percentage, Ideal: 20-30%
    
    # Additional soil properties
    soil_texture = db.Column(db.String(50))
    soil_depth = db.Column(db.Float)  # cm
    drainage_class = db.Column(db.String(50))
    
    # Calculated indices
    credit_score = db.Column(db.Float)
    risk_level = db.Column(db.Enum(RiskLevel))
    recommended_premium = db.Column(db.Float)
    
    # Metadata
    lab_technician = db.Column(db.String(100))
    testing_facility = db.Column(db.String(100))
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<SoilSample {self.id} for Farmer {self.farmer_id}>'

    @property
    def is_valid(self):
        """Check if soil sample values are within acceptable ranges"""
        return (
            5.5 <= self.ph_level <= 8.0 and
            0 <= self.nitrogen_level <= 100 and
            0 <= self.phosphorus_level <= 100 and
            0 <= self.potassium_level <= 500 and
            0 <= self.organic_matter <= 10 and
            0 <= self.cation_exchange_capacity <= 50 and
            0 <= self.moisture_content <= 100
        )

class CreditHistory(db.Model):
    __tablename__ = 'credit_history'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    loan_amount = db.Column(db.Float)
    loan_date = db.Column(db.Date)
    repayment_status = db.Column(db.String(20))
    interest_rate = db.Column(db.Float)
    loan_purpose = db.Column(db.String(200))
    repayment_schedule = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CreditHistory {self.id} for Farmer {self.farmer_id}>'