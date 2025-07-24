# app/models/soil_sample.py
"""
Soil sample model and schema for Talazo AgriFinance Platform.
"""

from datetime import datetime
from enum import Enum
from app.core.extensions import db, ma
from marshmallow import fields, validate


class SoilSampleStatus(Enum):
    """Enumeration for soil sample processing status."""
    COLLECTED = 'collected'
    ANALYZED = 'analyzed'
    VERIFIED = 'verified'
    REJECTED = 'rejected'


class RiskLevel(Enum):
    """Enumeration for financial risk levels."""
    LOW = 'Low'
    MEDIUM_LOW = 'Medium-Low' 
    MEDIUM = 'Medium'
    MEDIUM_HIGH = 'Medium-High'
    HIGH = 'High'


class SoilSample(db.Model):
    """Soil sample model representing soil analysis data."""
    
    __tablename__ = 'soil_samples'
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Collection information
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)
    collection_location = db.Column(db.String(100))
    collection_lat = db.Column(db.Float)
    collection_lng = db.Column(db.Float)
    status = db.Column(db.Enum(SoilSampleStatus), default=SoilSampleStatus.COLLECTED)
    
    # Primary soil parameters (required for financial scoring)
    ph_level = db.Column(db.Float, nullable=False)
    nitrogen_level = db.Column(db.Float, nullable=False)  # mg/kg
    phosphorus_level = db.Column(db.Float, nullable=False)  # mg/kg
    potassium_level = db.Column(db.Float, nullable=False)  # mg/kg
    
    # Secondary soil parameters (optional but recommended)
    organic_matter = db.Column(db.Float)  # percentage
    cation_exchange_capacity = db.Column(db.Float)  # cmol/kg
    moisture_content = db.Column(db.Float)  # percentage
    
    # Additional soil properties
    texture = db.Column(db.String(50))  # clay, loam, sand, etc.
    structure = db.Column(db.String(50))
    bulk_density = db.Column(db.Float)
    porosity = db.Column(db.Float)
    depth = db.Column(db.Float)  # sampling depth in cm
    
    # Micronutrients
    iron_level = db.Column(db.Float)  # mg/kg
    zinc_level = db.Column(db.Float)  # mg/kg
    manganese_level = db.Column(db.Float)  # mg/kg
    copper_level = db.Column(db.Float)  # mg/kg
    
    # Analysis results
    financial_index_score = db.Column(db.Float)  # 0-100 scale
    risk_level = db.Column(db.Enum(RiskLevel))
    yield_prediction = db.Column(db.Float)  # predicted yield in kg/ha
    recommendation_score = db.Column(db.Float)  # agriculture recommendation score
    
    # Analysis metadata
    analyzed_by = db.Column(db.String(100))
    analysis_date = db.Column(db.DateTime)
    analysis_method = db.Column(db.String(100))
    laboratory = db.Column(db.String(100))
    
    # Weather context
    rainfall_last_30_days = db.Column(db.Float)  # mm
    temperature_avg = db.Column(db.Float)  # celsius
    humidity_avg = db.Column(db.Float)  # percentage
    
    # Notes and comments
    notes = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SoilSample {self.id} - Farmer {self.farmer_id}>'
    
    def calculate_soil_health_score(self):
        """Calculate overall soil health score (0-100)."""
        if not all([self.ph_level, self.nitrogen_level, self.phosphorus_level, self.potassium_level]):
            return None
        
        # Normalized scoring for each parameter
        ph_score = self._normalize_ph_score(self.ph_level)
        n_score = self._normalize_nutrient_score(self.nitrogen_level, 'nitrogen')
        p_score = self._normalize_nutrient_score(self.phosphorus_level, 'phosphorus')
        k_score = self._normalize_nutrient_score(self.potassium_level, 'potassium')
        
        # Optional parameters
        om_score = self._normalize_organic_matter_score(self.organic_matter) if self.organic_matter else 70
        moisture_score = self._normalize_moisture_score(self.moisture_content) if self.moisture_content else 70
        
        # Weighted average
        weights = {
            'ph': 0.25,
            'nitrogen': 0.20,
            'phosphorus': 0.20,
            'potassium': 0.20,
            'organic_matter': 0.10,
            'moisture': 0.05
        }
        
        total_score = (
            ph_score * weights['ph'] +
            n_score * weights['nitrogen'] +
            p_score * weights['phosphorus'] +
            k_score * weights['potassium'] +
            om_score * weights['organic_matter'] +
            moisture_score * weights['moisture']
        )
        
        return round(total_score, 2)
    
    def _normalize_ph_score(self, ph):
        """Normalize pH to 0-100 score."""
        if 6.0 <= ph <= 7.5:
            return 100
        elif 5.5 <= ph < 6.0 or 7.5 < ph <= 8.0:
            return 85
        elif 5.0 <= ph < 5.5 or 8.0 < ph <= 8.5:
            return 70
        elif 4.5 <= ph < 5.0 or 8.5 < ph <= 9.0:
            return 50
        else:
            return 25
    
    def _normalize_nutrient_score(self, level, nutrient_type):
        """Normalize nutrient levels to 0-100 score."""
        ranges = {
            'nitrogen': {'low': 20, 'medium': 40, 'high': 60, 'excess': 100},
            'phosphorus': {'low': 10, 'medium': 25, 'high': 50, 'excess': 75},
            'potassium': {'low': 80, 'medium': 150, 'high': 250, 'excess': 400}
        }
        
        r = ranges[nutrient_type]
        
        if level < r['low']:
            return 30
        elif level < r['medium']:
            return 60
        elif level < r['high']:
            return 85
        elif level < r['excess']:
            return 100
        else:
            return 80  # Slight penalty for excessive levels
    
    def _normalize_organic_matter_score(self, om):
        """Normalize organic matter to 0-100 score."""
        if om >= 3.0:
            return 100
        elif om >= 2.0:
            return 85
        elif om >= 1.0:
            return 70
        elif om >= 0.5:
            return 50
        else:
            return 25
    
    def _normalize_moisture_score(self, moisture):
        """Normalize moisture content to 0-100 score."""
        if 20 <= moisture <= 35:
            return 100
        elif 15 <= moisture < 20 or 35 < moisture <= 45:
            return 85
        elif 10 <= moisture < 15 or 45 < moisture <= 55:
            return 70
        else:
            return 50
    
    def get_parameter_scores(self):
        """Get individual parameter scores."""
        return {
            'ph_score': self._normalize_ph_score(self.ph_level) if self.ph_level else None,
            'nitrogen_score': self._normalize_nutrient_score(self.nitrogen_level, 'nitrogen') if self.nitrogen_level else None,
            'phosphorus_score': self._normalize_nutrient_score(self.phosphorus_level, 'phosphorus') if self.phosphorus_level else None,
            'potassium_score': self._normalize_nutrient_score(self.potassium_level, 'potassium') if self.potassium_level else None,
            'organic_matter_score': self._normalize_organic_matter_score(self.organic_matter) if self.organic_matter else None,
            'moisture_score': self._normalize_moisture_score(self.moisture_content) if self.moisture_content else None
        }
    
    def to_dict(self):
        """Convert soil sample to dictionary."""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'status': self.status.value if self.status else None,
            'ph_level': self.ph_level,
            'nitrogen_level': self.nitrogen_level,
            'phosphorus_level': self.phosphorus_level,
            'potassium_level': self.potassium_level,
            'organic_matter': self.organic_matter,
            'moisture_content': self.moisture_content,
            'financial_index_score': self.financial_index_score,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'yield_prediction': self.yield_prediction,
            'soil_health_score': self.calculate_soil_health_score(),
            'parameter_scores': self.get_parameter_scores()
        }


from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class SoilSampleSchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for SoilSample model."""
    
    class Meta:
        model = SoilSample
        load_instance = True
        include_fk = True
    
    # Required fields validation
    ph_level = fields.Float(required=True, validate=validate.Range(min=0, max=14))
    nitrogen_level = fields.Float(required=True, validate=validate.Range(min=0))
    phosphorus_level = fields.Float(required=True, validate=validate.Range(min=0))
    potassium_level = fields.Float(required=True, validate=validate.Range(min=0))
    
    # Optional fields validation
    organic_matter = fields.Float(validate=validate.Range(min=0, max=100))
    moisture_content = fields.Float(validate=validate.Range(min=0, max=100))
    
    # Read-only fields
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    soil_health_score = fields.Method("get_soil_health_score", dump_only=True)
    parameter_scores = fields.Method("get_parameter_scores", dump_only=True)
    
    def get_soil_health_score(self, obj):
        return obj.calculate_soil_health_score()
    
    def get_parameter_scores(self, obj):
        return obj.get_parameter_scores()
