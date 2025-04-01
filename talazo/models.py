# models.py - Enhanced database models
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class SoilSampleStatus(enum.Enum):
    COLLECTED = 'collected'
    ANALYZED = 'analyzed'
    VERIFIED = 'verified'

class RiskLevel(enum.Enum):
    LOW = 'Low'
    MEDIUM_LOW = 'Medium-Low'
    MEDIUM = 'Medium'
    MEDIUM_HIGH = 'Medium-High'
    HIGH = 'High'

class UserRole(enum.Enum):
    ADMIN = 'admin'
    FINANCIAL_INSTITUTION = 'financial_institution'
    FARMER = 'farmer'
    FIELD_OFFICER = 'field_officer'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.FARMER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    farmer_profile = db.relationship('Farmer', backref='user', uselist=False)
    financial_institution = db.relationship('FinancialInstitution', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

class Farmer(db.Model):
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    national_id = db.Column(db.String(30), unique=True)
    address = db.Column(db.String(200))
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    farming_experience_years = db.Column(db.Integer)
    total_land_area = db.Column(db.Float)  # in hectares
    primary_crop = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farm_plots = db.relationship('FarmPlot', backref='farmer', lazy=True)
    soil_samples = db.relationship('SoilSample', backref='farmer', lazy=True)
    loans = db.relationship('Loan', backref='farmer', lazy=True)
    insurance_policies = db.relationship('InsurancePolicy', backref='farmer', lazy=True)
    
    def __repr__(self):
        return f'<Farmer {self.full_name}>'
    
    def get_latest_soil_sample(self):
        return SoilSample.query.filter_by(farmer_id=self.id).order_by(SoilSample.collection_date.desc()).first()
    
    def get_credit_score(self):
        latest_sample = self.get_latest_soil_sample()
        if latest_sample:
            return latest_sample.financial_index_score
        return None

class FarmPlot(db.Model):
    __tablename__ = 'farm_plots'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    name = db.Column(db.String(100))
    area = db.Column(db.Float)  # in hectares
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    current_crop = db.Column(db.String(50))
    planting_date = db.Column(db.Date)
    expected_harvest_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    soil_samples = db.relationship('SoilSample', backref='farm_plot', lazy=True)
    
    def __repr__(self):
        return f'<FarmPlot {self.name} of {self.farmer_id}>'

class SoilSample(db.Model):
    __tablename__ = 'soil_samples'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    farm_plot_id = db.Column(db.Integer, db.ForeignKey('farm_plots.id'))
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(SoilSampleStatus), default=SoilSampleStatus.COLLECTED)
    
    # Soil parameters
    ph_level = db.Column(db.Float)
    nitrogen_level = db.Column(db.Float)
    phosphorus_level = db.Column(db.Float)
    potassium_level = db.Column(db.Float)
    organic_matter = db.Column(db.Float)
    cation_exchange_capacity = db.Column(db.Float)
    moisture_content = db.Column(db.Float)
    
    # Additional properties
    texture = db.Column(db.String(50))
    structure = db.Column(db.String(50))
    depth = db.Column(db.Float)  # in cm
    
    # Analysis results
    financial_index_score = db.Column(db.Float)
    risk_level = db.Column(db.Enum(RiskLevel))
    
    # Metadata
    analyzed_by = db.Column(db.String(100))
    analysis_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<SoilSample {self.id} from {self.farmer_id}>'

class FinancialInstitution(db.Model):
    __tablename__ = 'financial_institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    institution_type = db.Column(db.String(50))  # bank, microfinance, etc.
    contact_person = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    loans = db.relationship('Loan', backref='institution', lazy=True)
    insurance_policies = db.relationship('InsurancePolicy', backref='institution', lazy=True)
    
    def __repr__(self):
        return f'<FinancialInstitution {self.name}>'

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('financial_institutions.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)  # annual rate in percent
    term_months = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(200))
    approval_date = db.Column(db.DateTime)
    disbursement_date = db.Column(db.DateTime)
    repayment_schedule = db.Column(db.String(50))  # monthly, quarterly, etc.
    status = db.Column(db.String(50))  # pending, active, completed, defaulted
    financial_index_score = db.Column(db.Float)  # score at the time of application
    risk_level = db.Column(db.Enum(RiskLevel))  # risk assessment at application time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    repayments = db.relationship('LoanRepayment', backref='loan', lazy=True)
    
    def __repr__(self):
        return f'<Loan {self.id} for {self.farmer_id}>'

class LoanRepayment(db.Model):
    __tablename__ = 'loan_repayments'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<LoanRepayment {self.id} for Loan {self.loan_id}>'

class InsurancePolicy(db.Model):
    __tablename__ = 'insurance_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('financial_institutions.id'), nullable=False)
    policy_number = db.Column(db.String(50), unique=True)
    farm_plot_id = db.Column(db.Integer, db.ForeignKey('farm_plots.id'))
    coverage_type = db.Column(db.String(50))  # crop, weather, multi-peril, etc.
    premium_amount = db.Column(db.Float, nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50))  # active, expired, cancelled
    financial_index_score = db.Column(db.Float)  # score at the time of application
    risk_level = db.Column(db.Enum(RiskLevel))  # risk assessment at application time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    claims = db.relationship('InsuranceClaim', backref='policy', lazy=True)
    
    def __repr__(self):
        return f'<InsurancePolicy {self.policy_number}>'

class InsuranceClaim(db.Model):
    __tablename__ = 'insurance_claims'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'), nullable=False)
    claim_date = db.Column(db.DateTime, default=datetime.utcnow)
    incident_date = db.Column(db.Date, nullable=False)
    incident_type = db.Column(db.String(50))  # drought, flood, pest, disease, etc.
    description = db.Column(db.Text)
    claimed_amount = db.Column(db.Float, nullable=False)
    approved_amount = db.Column(db.Float)
    status = db.Column(db.String(50))  # pending, approved, rejected, paid
    resolution_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<InsuranceClaim {self.id} for Policy {self.policy_id}>'

class WeatherEvent(db.Model):
    __tablename__ = 'weather_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))  # rain, drought, frost, etc.
    severity = db.Column(db.String(50))  # mild, moderate, severe
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    radius_km = db.Column(db.Float)  # affected radius in kilometers
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WeatherEvent {self.event_type} on {self.start_date}>'

class SensorDevice(db.Model):
    __tablename__ = 'sensor_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    farm_plot_id = db.Column(db.Integer, db.ForeignKey('farm_plots.id'))
    device_type = db.Column(db.String(50))  # soil, weather, etc.
    manufacturer = db.Column(db.String(100))
    model_number = db.Column(db.String(50))
    installation_date = db.Column(db.DateTime)
    last_maintenance = db.Column(db.DateTime)
    battery_level = db.Column(db.Float)  # percentage
    status = db.Column(db.String(50))  # active, inactive, maintenance
    firmware_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    readings = db.relationship('SensorReading', backref='device', lazy=True)
    
    def __repr__(self):
        return f'<SensorDevice {self.device_id}>'

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('sensor_devices.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reading_type = db.Column(db.String(50))  # ph, nitrogen, moisture, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    quality = db.Column(db.Float)  # data quality indicator (0-1)
    
    def __repr__(self):
        return f'<SensorReading {self.reading_type}: {self.value}{self.unit}>'

class CropYieldPrediction(db.Model):
    __tablename__ = 'crop_yield_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_plot_id = db.Column(db.Integer, db.ForeignKey('farm_plots.id'), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_yield = db.Column(db.Float)  # in tons per hectare
    lower_bound = db.Column(db.Float)
    upper_bound = db.Column(db.Float)
    confidence = db.Column(db.Float)  # 0-100
    model_version = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<CropYieldPrediction {self.id} for Plot {self.farm_plot_id}>'

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    farm_plot_id = db.Column(db.Integer, db.ForeignKey('farm_plots.id'))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))  # soil, crop, finance, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(50))  # high, medium, low
    estimated_cost = db.Column(db.Float)
    estimated_benefit = db.Column(db.Text)
    implementation_timeframe = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')  # pending, implemented, ignored
    
    def __repr__(self):
        return f'<Recommendation {self.id} for Farmer {self.farmer_id}>'