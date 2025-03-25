from flask import Flask, render_template, request, jsonify
import os
import random
from datetime import datetime, timedelta
import json
import math
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import pickle
from pathlib import Path
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields, validate
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SoilHealthIndex:
    def __init__(self):
        self.weights = {
        }
        
        self.ideal_ranges = {
            'ph_level': (6.0, 7.0),
            'nitrogen_level': (20, 40),
            'phosphorus_level': (20, 30),
            'potassium_level': (150, 250),
            'organic_matter': (3, 5),
            'cation_exchange_capacity': (10, 20),
            'moisture_content': (20, 30)
        }
        
        # Define typical crops for Zimbabwean small-scale farmers
        self.crops = {
            'maize': {
                'ideal_ph': (5.8, 6.8),
                'nitrogen_requirement': 'high',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'medium',
                'growing_season': 'summer'
            },
            'sorghum': {
                'ideal_ph': (5.5, 7.5),
                'nitrogen_requirement': 'medium',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'high',
                'growing_season': 'summer'
            },
            'groundnuts': {
                'ideal_ph': (5.5, 7.0),
                'nitrogen_requirement': 'low',
                'phosphorus_requirement': 'high',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'medium',
                'growing_season': 'summer'
            },
            'soybeans': {
                'ideal_ph': (6.0, 7.0),
                'nitrogen_requirement': 'low',  # Nitrogen-fixing
                'phosphorus_requirement': 'high',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'medium',
                'growing_season': 'summer'
            },
            'cotton': {
                'ideal_ph': (5.8, 7.0),
                'nitrogen_requirement': 'high',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'high',
                'drought_tolerance': 'high',
                'growing_season': 'summer'
            }
        }

    def calculate_score(self, soil_data):
        total_score = 0
        parameter_scores = {}
        
        for param, value in soil_data.items():
            if param in self.weights:
                param_score = self._score_parameter(param, float(value))
                parameter_scores[param] = param_score
                total_score += param_score * self.weights[param]
        
        return total_score * 100, parameter_scores

    def _score_parameter(self, param, value):
        min_ideal, max_ideal = self.ideal_ranges[param]
        if min_ideal <= value <= max_ideal:
            return 1.0
        elif value < min_ideal:
            return max(0, 1 - (min_ideal - value) / min_ideal)
        else:
            return max(0, 1 - (value - max_ideal) / max_ideal)

    def determine_risk_level(self, score):
        if score >= 80:
            return "Low Risk"
        elif score >= 60:
            return "Medium-Low Risk"
        elif score >= 40:
            return "Medium Risk"
        elif score >= 20:
            return "Medium-High Risk"
        else:
            return "High Risk"

    def calculate_premium(self, score):
        base_premium = 1000  # Base premium in USD
        risk_factor = (100 - score) / 100
        return base_premium * (1 + risk_factor)

    def get_recommendations(self, soil_data):
        """Enhanced recommendation system with contextual advice"""
        recommendations = []
        
        # Specific recommendations based on soil parameters
        for param, value in soil_data.items():
            if param in self.ideal_ranges:
                min_ideal, max_ideal = self.ideal_ranges[param]
                value = float(value)
                
                if param == 'ph_level':
                    if value < min_ideal:
                        recommendations.append({
                            'parameter': 'pH level',
                            'issue': 'Soil is too acidic',
                            'action': 'Apply agricultural lime at 2-4 tons per hectare to increase pH',
                            'benefit': 'Improves nutrient availability and microbial activity',
                            'cost_estimate': 'Medium',
                            'timeframe': 'Effects visible within 3-6 months'
                        })
                    elif value > max_ideal:
                        recommendations.append({
                            'parameter': 'pH level',
                            'issue': 'Soil is too alkaline',
                            'action': 'Apply agricultural sulfur or organic matter to decrease pH',
                            'benefit': 'Prevents micronutrient deficiencies',
                            'cost_estimate': 'Medium',
                            'timeframe': 'Effects visible within 3-6 months'
                        })
                
                elif param == 'nitrogen_level':
                    if value < min_ideal:
                        recommendations.append({
                            'parameter': 'Nitrogen level',
                            'issue': 'Nitrogen deficiency',
                            'action': 'Apply nitrogen fertilizer (ammonium nitrate or urea) at 100-150 kg/ha',
                            'benefit': 'Promotes vegetative growth and increases yield potential',
                            'cost_estimate': 'Medium-High',
                            'timeframe': 'Rapid effects within 2-4 weeks'
                        })
                    elif value > max_ideal:
                        recommendations.append({
                            'parameter': 'Nitrogen level',
                            'issue': 'Excess nitrogen',
                            'action': 'Reduce nitrogen fertilizer application and consider planting cover crops like legumes',
                            'benefit': 'Prevents excessive vegetative growth and reduces leaching',
                            'cost_estimate': 'Low',
                            'timeframe': 'Gradual improvement over growing season'
                        })
                
                elif param == 'phosphorus_level':
                    if value < min_ideal:
                        recommendations.append({
                            'parameter': 'Phosphorus level',
                            'issue': 'Phosphorus deficiency',
                            'action': 'Apply phosphate fertilizer (single or triple superphosphate) at 50-100 kg/ha',
                            'benefit': 'Improves root development and flowering',
                            'cost_estimate': 'Medium',
                            'timeframe': 'Effects visible within 4-8 weeks'
                        })
                    elif value > max_ideal:
                        recommendations.append({
                            'parameter': 'Phosphorus level',
                            'issue': 'Excess phosphorus',
                            'action': 'Avoid further phosphorus application for 1-2 seasons',
                            'benefit': 'Prevents nutrient imbalance and water pollution',
                            'cost_estimate': 'Low',
                            'timeframe': 'Long-term management'
                        })
                
                elif param == 'potassium_level':
                    if value < min_ideal:
                        recommendations.append({
                            'parameter': 'Potassium level',
                            'issue': 'Potassium deficiency',
                            'action': 'Apply potassium fertilizer (potassium chloride or sulfate) at 50-100 kg/ha',
                            'benefit': 'Enhances disease resistance and drought tolerance',
                            'cost_estimate': 'Medium',
                            'timeframe': 'Effects visible within 4-8 weeks'
                        })
                    elif value > max_ideal:
                        recommendations.append({
                            'parameter': 'Potassium level',
                            'issue': 'Excess potassium',
                            'action': 'Avoid further potassium application for 1-2 seasons',
                            'benefit': 'Prevents nutrient imbalance',
                            'cost_estimate': 'Low',
                            'timeframe': 'Long-term management'
                        })
                
                elif param == 'organic_matter':
                    if value < min_ideal:
                        recommendations.append({
                            'parameter': 'Organic matter',
                            'issue': 'Low organic matter content',
                            'action': 'Apply compost or manure at 10-20 tons per hectare and practice crop rotation',
                            'benefit': 'Improves soil structure, water retention, and nutrient availability',
                            'cost_estimate': 'Low-Medium',
                            'timeframe': 'Gradual improvement over 1-3 years'
                        })
                
                elif param == 'moisture_content':
                    if value < min_ideal:
                        recommendations.append({
                            'parameter': 'Moisture content',
                            'issue': 'Low soil moisture',
                            'action': 'Implement mulching, conservation tillage, or consider drip irrigation',
                            'benefit': 'Reduces water stress and improves nutrient uptake',
                            'cost_estimate': 'Medium-High for irrigation, Low for mulching',
                            'timeframe': 'Immediate effects with irrigation, gradual with conservation practices'
                        })
                    elif value > max_ideal:
                        recommendations.append({
                            'parameter': 'Moisture content',
                            'issue': 'Excess soil moisture',
                            'action': 'Improve drainage through ditches or raised beds',
                            'benefit': 'Prevents root diseases and nutrient leaching',
                            'cost_estimate': 'Medium',
                            'timeframe': 'Immediate effects after implementation'
                        })
        
        # Crop-specific recommendations based on soil conditions
        suitable_crops = self.recommend_suitable_crops(soil_data)
        if suitable_crops:
            crops_text = ", ".join(suitable_crops[:3])
            recommendations.append({
                'parameter': 'Crop selection',
                'issue': 'Optimal crop selection for current soil conditions',
                'action': f'Consider planting {crops_text} based on current soil properties',
                'benefit': 'Maximizes yield potential and reduces input requirements',
                'cost_estimate': 'Varies by crop',
                'timeframe': 'Next planting season'
            })
        
        return recommendations

    def recommend_suitable_crops(self, soil_data):
        """Recommend suitable crops based on soil parameters"""
        if 'ph_level' not in soil_data:
            return []
            
        ph = float(soil_data.get('ph_level', 0))
        nitrogen = float(soil_data.get('nitrogen_level', 0))
        phosphorus = float(soil_data.get('phosphorus_level', 0))
        potassium = float(soil_data.get('potassium_level', 0))
        
        # Score each crop based on how well the soil matches its requirements
        crop_scores = {}
        for crop_name, crop_data in self.crops.items():
            min_ph, max_ph = crop_data['ideal_ph']
            
            # Score based on pH match (0-1)
            if min_ph <= ph <= max_ph:
                ph_score = 1.0
            else:
                distance = min(abs(ph - min_ph), abs(ph - max_ph))
                ph_score = max(0, 1 - distance / 2)  # Penalize based on distance from ideal range
            
            # Score based on nitrogen level match (0-1)
            n_requirement = crop_data['nitrogen_requirement']
            if n_requirement == 'low':
                n_score = 1.0 if nitrogen < 30 else max(0, 1 - (nitrogen - 30) / 30)
            elif n_requirement == 'medium':
                n_score = 1.0 if 20 <= nitrogen <= 40 else max(0, 1 - min(abs(nitrogen - 20), abs(nitrogen - 40)) / 20)
            else:  # high
                n_score = 1.0 if nitrogen > 30 else max(0, 1 - (30 - nitrogen) / 30)
            
            # Calculate overall score (weighted average)
            overall_score = (ph_score * 0.4) + (n_score * 0.3) + 0.3  # Base score component
            crop_scores[crop_name] = overall_score
        
        # Sort crops by score and return top matches
        sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
        return [crop for crop, score in sorted_crops if score > 0.6]  # Return crops with score > 0.6

class SensorSimulator:
    def __init__(self):
        # Initial base values for soil parameters
        self.base_values = {
            'ph_level': 6.5,
            'nitrogen_level': 30,
            'phosphorus_level': 25,
            'potassium_level': 200,
            'organic_matter': 4,
            'cation_exchange_capacity': 15,
            'moisture_content': 25
        }
        
        # Define normal ranges for each parameter
        self.parameter_ranges = {
            'ph_level': (5.5, 7.5),
            'nitrogen_level': (20, 40),
            'phosphorus_level': (15, 35),
            'potassium_level': (150, 250),
            'organic_matter': (2, 6),
            'cation_exchange_capacity': (10, 20),
            'moisture_content': (20, 30)
        }
        
        # Simulation variables with seasonal effects
        self.trend_direction = {param: random.choice([-1, 1]) for param in self.base_values}
        self.last_update = datetime.now()
        
        # Seasonal patterns (simplified for Zimbabwe's climate)
        self.seasons = {
            # Summer (rainy season): Nov-Mar
            'summer': {
                'months': [11, 12, 1, 2, 3],
                'effects': {
                    'moisture_content': 6.0,
                    'nitrogen_level': 2.0,
                    'organic_matter': 1.0,
                    'ph_level': -0.2  # Slight acidification due to rainfall
                }
            },
            # Winter (dry season): May-Aug
            'winter': {
                'months': [5, 6, 7, 8],
                'effects': {
                    'moisture_content': -4.0,
                    'nitrogen_level': -1.0,
                    'ph_level': 0.1  # Slight increase in pH in dry conditions
                }
            },
            # Transition periods: Apr, Sep-Oct
            'transition': {
                'months': [4, 9, 10],
                'effects': {
                    'moisture_content': -2.0
                }
            }
        }
        
        # Add some random events
        self.last_event_time = datetime.now() - timedelta(hours=24)
        self.current_event = None
        self.event_duration = timedelta(hours=0)
        
        # Configurable volatility
        self.volatility = 0.5  # 0-1 scale, higher means more random fluctuations

    def generate_reading(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        # Get current season
        current_month = timestamp.month
        season = next((s for s, data in self.seasons.items() 
                      if current_month in data['months']), 'transition')
        
        # Get seasonal effects
        seasonal_effects = self.seasons[season]['effects']
        
        # Check if we need to generate a random event (5% chance every hour)
        hours_since_last_event = (timestamp - self.last_event_time).total_seconds() / 3600
        if hours_since_last_event > 1 and random.random() < 0.05:
            self.generate_random_event(timestamp)
        
        # Apply current event if active
        event_effects = {}
        if self.current_event and timestamp < self.last_event_time + self.event_duration:
            event_effects = self.current_event['effects']
        else:
            self.current_event = None

        # Time-based variations: daily cycle and hourly randomness
        time_of_day = timestamp.hour
        day_factor = math.sin(time_of_day * math.pi / 12)  # Daily cycle for temperature effect
        day_of_year = timestamp.timetuple().tm_yday
        annual_factor = math.sin((day_of_year / 365) * 2 * math.pi)  # Annual seasonal cycle

        readings = {}
        for param, base_value in self.base_values.items():
            # Calculate various factors
            seasonal_change = seasonal_effects.get(param, 0)
            event_change = event_effects.get(param, 0)
            
            # Daily cycle effects (mostly affects moisture)
            daily_effect = 0
            if param == 'moisture_content':
                daily_effect = -day_factor * 2  # More evaporation during day
            
            # Random walk component (soil changes gradually)
            if random.random() < 0.1:  # 10% chance to change trend direction
                self.trend_direction[param] *= random.choice([-1, 1])
            
            # Random fluctuation based on volatility setting
            random_factor = random.uniform(-self.volatility, self.volatility)
            trend_factor = self.trend_direction[param] * 0.05
            
            # Calculate new value combining all factors
            new_value = (base_value 
                         + seasonal_change 
                         + event_change 
                         + daily_effect 
                         + random_factor 
                         + trend_factor)
            
            # Ensure value stays within defined ranges
            min_val, max_val = self.parameter_ranges[param]
            new_value = max(min_val, min(max_val, new_value))
            
            readings[param] = round(new_value, 2)
        
        readings['timestamp'] = timestamp.isoformat()
        return readings

    def generate_random_event(self, timestamp):
        """Generate a random weather event that affects soil parameters"""
        # Define possible events
        events = [
            {
                'name': 'Heavy Rainfall',
                'probability': 0.4,
                'duration': timedelta(hours=random.randint(2, 8)),
                'effects': {
                    'moisture_content': random.uniform(3.0, 6.0),
                    'nitrogen_level': random.uniform(-1.0, -3.0),  # Leaching
                    'ph_level': random.uniform(-0.2, -0.5)  # Acidification
                }
            },
            {
                'name': 'Drought',
                'probability': 0.3,
                'duration': timedelta(days=random.randint(3, 7)),
                'effects': {
                    'moisture_content': random.uniform(-4.0, -8.0),
                    'organic_matter': random.uniform(-0.2, -0.5)
                }
            },
            {
                'name': 'Heat Wave',
                'probability': 0.2,
                'duration': timedelta(days=random.randint(2, 5)),
                'effects': {
                    'moisture_content': random.uniform(-3.0, -5.0),
                    'nitrogen_level': random.uniform(-0.5, -1.5)  # Increased volatilization
                }
            },
            {
                'name': 'Cold Snap',
                'probability': 0.1,
                'duration': timedelta(days=random.randint(1, 3)),
                'effects': {
                    'moisture_content': random.uniform(0.5, 1.5),  # Reduced evaporation
                    'nitrogen_level': random.uniform(-0.2, -0.8)  # Slower microbial activity
                }
            }
        ]
        
        # Choose an event weighted by probability
        weights = [event['probability'] for event in events]
        selected_event = random.choices(events, weights=weights, k=1)[0]
        
        # Set the current event
        self.current_event = selected_event
        self.last_event_time = timestamp
        self.event_duration = selected_event['duration']
        
        return selected_event

    def generate_historical_data(self, days=7):
        data = []
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Generate data points at 30-minute intervals
        current_time = start_time
        while current_time <= end_time:
            data.append(self.generate_reading(current_time))
            current_time += timedelta(minutes=30)
        
        return data

    def get_current_readings(self):
        """Get current sensor readings"""
        return self.generate_reading()

class YieldPredictor:
    def __init__(self):
        self.model = None
        self.model_file = Path('yield_model.pkl')
        
        # If model exists, load it; otherwise, train a new one
        if self.model_file.exists():
            self.model = joblib.load(self.model_file)
        else:
            self._train_model()
    
    def _train_model(self):
        """Train a simple RandomForest model for yield prediction"""
        print("Training new yield prediction model...")
        
        # Generate synthetic training data
        # In a real scenario, this would be replaced with actual historical data
        X_train, y_train = self._generate_synthetic_data()
        
        # Train RandomForest model
        self.model = RandomForestRegressor(
            n_estimators=100, 
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(self.model, self.model_file)
        print("Model trained and saved")
    
    def _generate_synthetic_data(self):
        """Generate synthetic data for initial model training"""
        # Number of samples
        n_samples = 500
        
        # Generate features with realistic correlations
        X = np.zeros((n_samples, 7))
        
        # pH level (5.5 to 8.0)
        X[:, 0] = np.random.uniform(5.5, 8.0, n_samples)
        
        # Nitrogen level (10 to 50)
        X[:, 1] = np.random.uniform(10, 50, n_samples)
        
        # Phosphorus level (10 to 40)
        X[:, 2] = np.random.uniform(10, 40, n_samples)
        
        # Potassium level (100 to 300)
        X[:, 3] = np.random.uniform(100, 300, n_samples)
        
        # Organic matter (1 to 8)
        X[:, 4] = np.random.uniform(1, 8, n_samples)
        
        # Cation exchange capacity (5 to 25)
        X[:, 5] = np.random.uniform(5, 25, n_samples)
        
        # Average moisture content (15 to 35)
        X[:, 6] = np.random.uniform(15, 35, n_samples)
        
        # Generate target yields (tons per hectare)
        # Base yield influenced by all parameters
        y = np.zeros(n_samples)
        
        # pH effect (optimal around 6.5)
        y += -0.5 * np.abs(X[:, 0] - 6.5) + 2
        
        # Nitrogen effect (more is better, with diminishing returns)
        y += 0.05 * X[:, 1] - 0.0005 * X[:, 1]**2
        
        # Phosphorus effect
        y += 0.02 * X[:, 2]
        
        # Potassium effect
        y += 0.005 * X[:, 3]
        
        # Organic matter effect (very important)
        y += 0.3 * X[:, 4]
        
        # CEC effect
        y += 0.05 * X[:, 5]
        
        # Moisture content effect (optimal around 25%)
        y += -0.05 * np.abs(X[:, 6] - 25) + 1
        
        # Add noise
        y += np.random.normal(0, 0.5, n_samples)
        
        # Ensure all yields are positive and realistic (1-15 tons/ha)
        y = np.clip(y, 1, 15)
        
        return X, y
    
    def predict_yield(self, soil_data):
        """Predict yield potential based on soil data"""
        if not self.model:
            self._train_model()
            
        # Extract and order features for the model
        features = np.array([
            float(soil_data.get('ph_level', 6.5)),
            float(soil_data.get('nitrogen_level', 30)),
            float(soil_data.get('phosphorus_level', 25)),
            float(soil_data.get('potassium_level', 200)),
            float(soil_data.get('organic_matter', 4)),
            float(soil_data.get('cation_exchange_capacity', 15)),
            float(soil_data.get('moisture_content', 25))
        ]).reshape(1, -1)
        
        # Make prediction
        predicted_yield = self.model.predict(features)[0]
        
        # Calculate yield range and confidence
        feature_importance = self.model.feature_importances_
        
        # Calculate uncertainty factors
        uncertainty = 0.5  # Base uncertainty
        
        # Higher uncertainty for extreme values
        for i, (param, value) in enumerate([
            ('ph_level', features[0, 0]),
            ('nitrogen_level', features[0, 1]),
            ('phosphorus_level', features[0, 2]),
            ('potassium_level', features[0, 3]),
            ('organic_matter', features[0, 4]),
            ('cation_exchange_capacity', features[0, 5]),
            ('moisture_content', features[0, 6])
        ]):
            # Check if value is in ideal range
            if param in soil_analyzer.ideal_ranges:
                min_val, max_val = soil_analyzer.ideal_ranges[param]
                if value < min_val or value > max_val:
                    # Add uncertainty for out-of-range values
                    uncertainty += 0.1 * feature_importance[i]
        
        lower_bound = max(0, predicted_yield - predicted_yield * uncertainty)
        upper_bound = predicted_yield + predicted_yield * uncertainty
        
        # Determine crop suitability score (0-10)
        top_crops = soil_analyzer.recommend_suitable_crops(soil_data)
        crop_suitability = len(top_crops) * 2 if len(top_crops) <= 5 else 10
        
        # Return prediction with additional context
        return {
            'predicted_yield': round(predicted_yield, 2),
            'yield_range': {
                'lower': round(lower_bound, 2),
                'upper': round(upper_bound, 2)
            },
            'confidence': round((1 - uncertainty) * 100),
            'unit': 'tons per hectare',
            'top_crops': top_crops[:3],
            'crop_suitability_score': crop_suitability,
            'limiting_factors': self._identify_limiting_factors(soil_data, feature_importance)
        }
    
    def _identify_limiting_factors(self, soil_data, feature_importance):
        """Identify factors that might be limiting yield potential"""
        limiting_factors = []
        
        # Map feature indices to parameter names
        feature_map = {
            0: 'ph_level',
            1: 'nitrogen_level',
            2: 'phosphorus_level',
            3: 'potassium_level',
            4: 'organic_matter',
            5: 'cation_exchange_capacity',
            6: 'moisture_content'
        }
        
        # Sort features by importance
        sorted_features = sorted(enumerate(feature_importance), key=lambda x: x[1], reverse=True)
        
        # Check the top 3 important features for non-optimal values
        for idx, importance in sorted_features[:3]:
            param = feature_map[idx]
            if param in soil_analyzer.ideal_ranges:
                value = float(soil_data.get(param, 0))
                min_ideal, max_ideal = soil_analyzer.ideal_ranges[param]
                
                if value < min_ideal:
                    limiting_factors.append({
                        'parameter': param.replace('_', ' ').title(),
                        'status': 'below optimal range',
                        'current_value': value,
                        'optimal_range': f"{min_ideal} - {max_ideal}",
                        'impact': 'high' if importance > 0.15 else 'medium'
                    })
                elif value > max_ideal:
                    limiting_factors.append({
                        'parameter': param.replace('_', ' ').title(),
                        'status': 'above optimal range',
                        'current_value': value,
                        'optimal_range': f"{min_ideal} - {max_ideal}",
                        'impact': 'high' if importance > 0.15 else 'medium'
                    })
        
        return limiting_factors

# Create Flask application
app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

# Enable CORS
CORS(app)

# Initialize components
soil_analyzer = SoilHealthIndex()
sensor_simulator = SensorSimulator()
yield_predictor = YieldPredictor()

# Enable CORS
CORS(app)

# Configure Swagger UI
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Soil Health API"
    }
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

class SoilDataSchema(Schema):
    """Schema for validating soil data input"""
    ph_level = fields.Float(required=True, validate=validate.Range(min=0, max=14))
    nitrogen_level = fields.Float(required=True, validate=validate.Range(min=0))
    phosphorus_level = fields.Float(required=True, validate=validate.Range(min=0))
    potassium_level = fields.Float(required=True, validate=validate.Range(min=0))
    organic_matter = fields.Float(validate=validate.Range(min=0))
    cation_exchange_capacity = fields.Float(validate=validate.Range(min=0))
    moisture_content = fields.Float(validate=validate.Range(min=0))

soil_data_schema = SoilDataSchema()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/calculate-index', methods=['POST'])
def calculate_index():
    """API endpoint to calculate financial index based on soil data"""
    try:
        # Validate input data
        errors = soil_data_schema.validate(request.json)
        if errors:
            return jsonify({
                'error': 'Invalid input data',
                'details': errors
            }), 400
            
        soil_data = request.json
        
        # Calculate soil health score
        score, parameter_scores = soil_analyzer.calculate_score(soil_data)
        
        # Get recommendations
        recommendations = soil_analyzer.get_recommendations(soil_data)
        
        # Calculate risk level and premium
        risk_level = soil_analyzer.determine_risk_level(score)
        premium = soil_analyzer.calculate_premium(score)
        
        return jsonify({
            'score': round(score, 2),
            'parameter_scores': parameter_scores,
            'risk_level': risk_level,
            'premium': round(premium, 2),
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime-data', methods=['GET'])
def get_realtime_data():
    """API endpoint to get simulated real-time sensor data"""
    try:
        # Generate a current reading
        reading = sensor_simulator.generate_reading()
        
        # Calculate score based on this reading
        score, parameter_scores = soil_analyzer.calculate_score(reading)
        risk_level = soil_analyzer.determine_risk_level(score)
        
        # Return the reading with the score
        return jsonify({
            'timestamp': reading['timestamp'],
            'soil_data': {k: v for k, v in reading.items() if k != 'timestamp'},
            'health_score': round(score, 2),
            'risk_level': risk_level
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical-data', methods=['GET'])
def get_historical_data():
    """API endpoint to get simulated historical data"""
    try:
        # Get days parameter, default to 7 days
        days = request.args.get('days', default=7, type=int)
        
        # Generate historical data
        data = sensor_simulator.generate_historical_data(days)
        
        # Calculate scores for each data point
        for point in data:
            soil_data = {k: v for k, v in point.items() if k != 'timestamp'}
            score, _ = soil_analyzer.calculate_score(soil_data)
            point['health_score'] = round(score, 2)
            point['risk_level'] = soil_analyzer.determine_risk_level(score)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-recommendations', methods=['POST'])
def get_ai_recommendations():
    """API endpoint to get AI-driven recommendations based on soil data"""
    try:
        data = request.json
        
        # Get soil data either from request or generate current reading if not provided
        if 'soil_data' in data:
            soil_data = data['soil_data']
        else:
            reading = sensor_simulator.generate_reading()
            soil_data = {k: v for k, v in reading.items() if k != 'timestamp'}
        
        # Get basic recommendations
        basic_recommendations = soil_analyzer.get_recommendations(soil_data)
        
        # Enhanced AI-driven analysis
        ai_analysis = generate_ai_analysis(soil_data, data.get('farm_size', 1), 
                                          data.get('budget_constraint', 'medium'),
                                          data.get('region', 'unknown'))
        
        # Get yield prediction
        yield_prediction = yield_predictor.predict_yield(soil_data)
        
        return jsonify({
            'soil_data': soil_data,
            'basic_recommendations': basic_recommendations,
            'ai_analysis': ai_analysis,
            'yield_prediction': yield_prediction
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_ai_analysis(soil_data, farm_size, budget_constraint, region):
    """
    Generate enhanced AI-driven analysis and recommendations
    
    This function simulates an AI recommendation system that would normally
    use machine learning models to provide context-aware advice.
    """
    # Calculate soil health score
    score, parameter_scores = soil_analyzer.calculate_score(soil_data)
    
    # Identify the weakest parameters (lowest scores)
    sorted_params = sorted(parameter_scores.items(), key=lambda x: x[1])
    weakest_params = sorted_params[:2]  # Get the two weakest parameters
    
    # Generate priority recommendations
    priority_recommendations = []
    
    for param, param_score in weakest_params:
        if param_score < 0.7:  # Only recommend for parameters below 70% optimal
            if param == 'ph_level':
                value = float(soil_data[param])
                ideal_min, ideal_max = soil_analyzer.ideal_ranges[param]
                
                if value < ideal_min:
                    # pH is too low (acidic)
                    if budget_constraint == 'low':
                        priority_recommendations.append({
                            'parameter': 'pH level',
                            'issue': 'Soil is too acidic',
                            'action': 'Apply agricultural lime at 1-2 tons per hectare',
                            'cost_estimate': f'${int(farm_size * 150)} - ${int(farm_size * 300)}',
                            'priority': 'High',
                            'roi_estimate': '3x-5x investment in increased yield',
                            'local_context': f'Many soils in {region} region tend to be acidic due to leaching from rainfall'
                        })
                    else:
                        priority_recommendations.append({
                            'parameter': 'pH level',
                            'issue': 'Soil is too acidic',
                            'action': 'Apply agricultural lime at 2-4 tons per hectare',
                            'cost_estimate': f'${int(farm_size * 300)} - ${int(farm_size * 600)}',
                            'priority': 'High',
                            'roi_estimate': '3x-5x investment in increased yield',
                            'local_context': f'Many soils in {region} region tend to be acidic due to leaching from rainfall'
                        })
                elif value > ideal_max:
                    # pH is too high (alkaline)
                    priority_recommendations.append({
                        'parameter': 'pH level',
                        'issue': 'Soil is too alkaline',
                        'action': 'Apply agricultural sulfur or incorporate organic matter',
                        'cost_estimate': f'${int(farm_size * 200)} - ${int(farm_size * 400)}',
                        'priority': 'High',
                        'roi_estimate': '2x-4x investment in increased yield',
                        'local_context': 'Alkaline soils may require multiple treatments over several seasons'
                    })
            
            elif param == 'nitrogen_level':
                value = float(soil_data[param])
                ideal_min, ideal_max = soil_analyzer.ideal_ranges[param]
                
                if value < ideal_min:
                    priority_recommendations.append({
                        'parameter': 'Nitrogen',
                        'issue': 'Nitrogen deficiency',
                        'action': 'Apply ammonium nitrate fertilizer at 150-200 kg/ha',
                        'cost_estimate': f'${int(farm_size * 180)} - ${int(farm_size * 250)}',
                        'priority': 'High',
                        'roi_estimate': '4x-6x investment in increased yield',
                        'local_context': 'Consider split application: 50% at planting, 50% at vegetative growth'
                    })
            
            elif param == 'phosphorus_level':
                value = float(soil_data[param])
                ideal_min, ideal_max = soil_analyzer.ideal_ranges[param]
                
                if value < ideal_min:
                    priority_recommendations.append({
                        'parameter': 'Phosphorus',
                        'issue': 'Phosphorus deficiency',
                        'action': 'Apply superphosphate fertilizer at 100-150 kg/ha',
                        'cost_estimate': f'${int(farm_size * 150)} - ${int(farm_size * 220)}',
                        'priority': 'Medium-High',
                        'roi_estimate': '2x-4x investment in increased yield',
                        'local_context': 'Apply before planting for best results'
                    })
            
            elif param == 'organic_matter':
                value = float(soil_data[param])
                ideal_min, ideal_max = soil_analyzer.ideal_ranges[param]
                
                if value < ideal_min:
                    if budget_constraint == 'low':
                        priority_recommendations.append({
                            'parameter': 'Organic Matter',
                            'issue': 'Low organic matter content',
                            'action': 'Implement crop rotation with legumes and leave crop residues in the field',
                            'cost_estimate': 'Low (mainly labor cost)',
                            'priority': 'Medium',
                            'roi_estimate': 'Long-term soil improvement, 2x-3x over 3-5 years',
                            'local_context': 'Mucuna (velvet bean) is an effective cover crop in Zimbabwean conditions'
                        })
                    else:
                        priority_recommendations.append({
                            'parameter': 'Organic Matter',
                            'issue': 'Low organic matter content',
                            'action': 'Apply 10-15 tons of composted manure per hectare',
                            'cost_estimate': f'${int(farm_size * 300)} - ${int(farm_size * 450)}',
                            'priority': 'Medium',
                            'roi_estimate': '2x-3x investment over 2-3 years',
                            'local_context': 'Local cattle manure is often available at lower costs in rural areas'
                        })
    
    # Generate seasonal context
    current_month = datetime.now().month
    seasonal_context = generate_seasonal_context(current_month, region)
    
    # Generate sustainable farming practices
    sustainable_practices = generate_sustainable_practices(soil_data, farm_size, region)
    
    # Yield optimization suggestions
    yield_suggestions = []
    predicted_yield = yield_predictor.predict_yield(soil_data)
    
    if predicted_yield['confidence'] < 70:
        yield_suggestions.append({
            'suggestion': 'Consider soil testing before planting',
            'reasoning': 'Current soil data has significant uncertainty, professional testing would improve predictions',
            'potential_benefit': 'More accurate crop selection and input planning'
        })
    
    if 'top_crops' in predicted_yield and predicted_yield['top_crops']:
        crop_info = []
        for crop in predicted_yield['top_crops']:
            crop_data = soil_analyzer.crops.get(crop, {})
            ideal_ph = crop_data.get('ideal_ph', (0, 0))
            crop_info.append({
                'crop': crop.capitalize(),
                'ideal_ph': f"{ideal_ph[0]}-{ideal_ph[1]}",
                'drought_tolerance': crop_data.get('drought_tolerance', 'unknown'),
                'expected_yield': f"{predicted_yield['predicted_yield'] * 0.9:.1f}-{predicted_yield['predicted_yield'] * 1.1:.1f} tons/ha"
            })
        
        yield_suggestions.append({
            'suggestion': 'Optimal crop selection',
            'reasoning': 'Based on current soil conditions, these crops are most suitable',
            'crops': crop_info
        })
    
    # Combined analysis
    return {
        'score': round(score, 2),
        'priority_recommendations': priority_recommendations,
        'seasonal_context': seasonal_context,
        'sustainable_practices': sustainable_practices,
        'yield_optimization': yield_suggestions,
        'confidence_level': 'Medium-High' if score > 60 else 'Medium'
    }

def generate_seasonal_context(month, region):
    """Generate seasonal farming context based on the current month"""
    # Define seasons in Zimbabwe
    rainy_season = [11, 12, 1, 2, 3]  # Nov-Mar
    dry_season = [5, 6, 7, 8]  # May-Aug
    transition_months = [4, 9, 10]  # Apr, Sep-Oct
    
    if month in rainy_season:
        if month in [11, 12]:  # Early rainy season
            return {
                'current_season': 'Early Rainy Season',
                'farming_activities': [
                    'Complete planting of main crops',
                    'Apply basal fertilizer',
                    'Implement soil moisture conservation practices',
                    'Monitor for pests after rain'
                ],
                'precipitation_outlook': 'Increasing rainfall expected',
                'risk_factors': 'Waterlogging in low-lying areas, nitrogen leaching',
                'opportunity_factors': 'Good time for nitrogen application as crops establish'
            }
        else:  # Mid to late rainy season
            return {
                'current_season': 'Mid to Late Rainy Season',
                'farming_activities': [
                    'Apply top dressing fertilizers',
                    'Weed control',
                    'Pest and disease monitoring',
                    'Prepare for possible dry spells'
                ],
                'precipitation_outlook': 'Regular rainfall with possible short dry spells',
                'risk_factors': 'Increased disease pressure, soil erosion',
                'opportunity_factors': 'Good growing conditions for most crops'
            }
    elif month in dry_season:
        return {
            'current_season': 'Dry Season',
            'farming_activities': [
                'Harvesting and post-harvest handling',
                'Soil testing for next season',
                'Crop residue management',
                'Land preparation for winter crops (if irrigation available)'
            ],
            'precipitation_outlook': 'Minimal rainfall expected',
            'risk_factors': 'Soil moisture depletion, wind erosion',
            'opportunity_factors': 'Good time for lime application if needed'
        }
    else:  # Transition season
        if month == 4:  # End of rainy season
            return {
                'current_season': 'End of Rainy Season',
                'farming_activities': [
                    'Harvesting early maturing crops',
                    'Cover cropping',
                    'Soil conservation practices',
                    'Prepare for dry season'
                ],
                'precipitation_outlook': 'Decreasing rainfall',
                'risk_factors': 'Unexpected late rains can affect harvesting',
                'opportunity_factors': 'Good time for soil sampling and analysis'
            }
        else:  # Transition to rainy season
            return {
                'current_season': 'Transition to Rainy Season',
                'farming_activities': [
                    'Land preparation',
                    'Soil amendment application (lime, manure)',
                    'Early planting planning',
                    'Input procurement'
                ],
                'precipitation_outlook': 'Possibility of early rains',
                'risk_factors': 'Unpredictable rainfall patterns',
                'opportunity_factors': 'Ideal time for pH correction and basal fertilizer application'
            }

def generate_sustainable_practices(soil_data, farm_size, region):
    """Generate sustainable farming practice recommendations"""
    practices = []
    
    # Conservation agriculture practices
    practices.append({
        'practice': 'Minimum tillage',
        'benefits': [
            'Reduces soil erosion',
            'Preserves soil structure',
            'Conserves soil moisture',
            'Reduces labor and fuel costs'
        ],
        'implementation_cost': 'Low to Medium',
        'timeframe': 'Can be implemented immediately',
        'local_relevance': 'Highly relevant for Zimbabwean small-scale farmers'
    })
    
    # Check organic matter levels
    organic_matter = float(soil_data.get('organic_matter', 0))
    if organic_matter < 3:
        practices.append({
            'practice': 'Green manuring with leguminous cover crops',
            'benefits': [
                'Increases soil organic matter',
                'Fixes atmospheric nitrogen',
                'Suppresses weeds',
                'Prevents soil erosion'
            ],
            'implementation_cost': 'Low',
            'timeframe': 'One growing season',
            'local_relevance': 'Sunhemp and velvet bean are well-adapted to local conditions'
        })
    
    # Check moisture levels
    moisture = float(soil_data.get('moisture_content', 0))
    if moisture < 20:
        practices.append({
            'practice': 'Mulching with crop residues',
            'benefits': [
                'Conserves soil moisture',
                'Moderates soil temperature',
                'Adds organic matter as it decomposes',
                'Suppresses weeds'
            ],
            'implementation_cost': 'Low',
            'timeframe': 'Immediate effects',
            'local_relevance': 'Particularly important during dry season and dry spells'
        })
    
    # Check pH levels
    ph = float(soil_data.get('ph_level', 0))
    if ph < 5.5:
        practices.append({
            'practice': 'Agroforestry with Faidherbia albida (Apple-ring Acacia)',
            'benefits': [
                'Naturally increases soil pH over time',
                'Fixes nitrogen',
                'Provides shade in dry season, sheds leaves in wet season',
                'Can provide additional income from wood'
            ],
            'implementation_cost': 'Low',
            'timeframe': 'Long-term (3-5 years for significant impact)',
            'local_relevance': 'Native to Zimbabwe and well adapted to local conditions'
        })
    
    return practices

@app.route('/api/events', methods=['GET'])
def get_weather_events():
    """Get current and recent weather events that affect soil conditions"""
    try:
        # Check if there's a current event
        current_event = sensor_simulator.current_event
        current_event_data = None
        
        if current_event:
            end_time = sensor_simulator.last_event_time + sensor_simulator.event_duration
            if datetime.now() < end_time:
                current_event_data = {
                    'name': current_event['name'],
                    'start_time': sensor_simulator.last_event_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'effects': {k: round(v, 2) for k, v in current_event['effects'].items()},
                    'status': 'active'
                }
        
        # Generate some past events for historical context
        past_events = generate_past_events()
        
        return jsonify({
            'current_event': current_event_data,
            'past_events': past_events
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_past_events():
    """Generate some past weather events for context"""
    # This would typically come from a database in a real app
    past_events = []
    now = datetime.now()
    
    # Event 1: Heavy rainfall 5 days ago
    event_time = now - timedelta(days=5)
    past_events.append({
        'name': 'Heavy Rainfall',
        'start_time': event_time.isoformat(),
        'end_time': (event_time + timedelta(hours=6)).isoformat(),
        'effects': {
            'moisture_content': 5.2,
            'nitrogen_level': -2.3,
            'ph_level': -0.3
        },
        'status': 'past'
    })
    
    # Event 2: Mild drought 12 days ago
    event_time = now - timedelta(days=12)
    past_events.append({
        'name': 'Mild Drought',
        'start_time': event_time.isoformat(),
        'end_time': (event_time + timedelta(days=4)).isoformat(),
        'effects': {
            'moisture_content': -6.5,
            'organic_matter': -0.3
        },
        'status': 'past'
    })
    
    return past_events

@app.route('/api/ml-model-info', methods=['GET'])
def get_ml_model_info():
    """Get information about the yield prediction ML model"""
    model = yield_predictor.model
    
    if not model:
        return jsonify({'error': 'Model not initialized'}), 500
    
    # Get feature importances
    feature_importance = model.feature_importances_
    
    # Map to parameter names
    parameters = [
        'pH Level',
        'Nitrogen Level',
        'Phosphorus Level',
        'Potassium Level',
        'Organic Matter',
        'Cation Exchange Capacity',
        'Moisture Content'
    ]
    
    importance_data = []
    for param, importance in zip(parameters, feature_importance):
        importance_data.append({
            'parameter': param,
            'importance': round(importance * 100, 2)  # Convert to percentage
        })
    
    # Sort by importance
    importance_data = sorted(importance_data, key=lambda x: x['importance'], reverse=True)
    
    return jsonify({
        'model_type': 'Random Forest Regression',
        'n_estimators': model.n_estimators,
        'max_depth': model.max_depth,
        'feature_importance': importance_data,
        'model_confidence': 'Medium-High',
        'last_updated': 'Model is based on synthetic data and would need to be retrained with actual farm data'
    })

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data for visualization"""
    try:
        # Generate current reading
        current_reading = sensor_simulator.generate_reading()
        soil_data = {k: v for k, v in current_reading.items() if k != 'timestamp'}
        
        # Calculate soil health score
        score, parameter_scores = soil_analyzer.calculate_score(soil_data)
        risk_level = soil_analyzer.determine_risk_level(score)
        
        # Get trend data (7 days)
        trend_data = sensor_simulator.generate_historical_data(7)
        
        # Calculate scores for trend data
        trend_scores = []
        for point in trend_data:
            point_data = {k: v for k, v in point.items() if k != 'timestamp'}
            point_score, _ = soil_analyzer.calculate_score(point_data)
            trend_scores.append({
                'timestamp': point['timestamp'],
                'score': round(point_score, 2)
            })
        
        # Get yield prediction
        yield_data = yield_predictor.predict_yield(soil_data)
        
        # Get AI recommendations
        ai_analysis = generate_ai_analysis(soil_data, 1, 'medium', 'Central Zimbabwe')
        
        # Get current event if any
        current_event = None
        if sensor_simulator.current_event:
            end_time = sensor_simulator.last_event_time + sensor_simulator.event_duration
            if datetime.now() < end_time:
                current_event = sensor_simulator.current_event['name']
        
        return jsonify({
            'current_reading': {
                'timestamp': current_reading['timestamp'],
                'soil_data': soil_data,
                'health_score': round(score, 2),
                'risk_level': risk_level,
                'parameter_scores': {k: round(v * 100, 2) for k, v in parameter_scores.items()}
            },
            'trend_data': {
                'timestamps': [point['timestamp'] for point in trend_data[-48:]],  # Last 24 hours (30 min intervals)
                'parameters': {
                    param: [point[param] for point in trend_data[-48:]] 
                    for param in soil_data.keys()
                },
                'scores': [point_score['score'] for point_score in trend_scores[-48:]]
            },
            'yield_prediction': yield_data,
            'recommendations': ai_analysis['priority_recommendations'][:3],
            'current_event': current_event,
            'seasonal_context': ai_analysis['seasonal_context']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/demo')
def demo_dashboard():
    """Interactive dashboard demo page"""
    return render_template('demo.html')

@app.route('/api/simulate-improvement', methods=['POST'])
def simulate_improvement():
    """Simulate the effect of implementing recommendations"""
    try:
        data = request.json
        
        # Get original soil data
        original_soil = data.get('soil_data', None)
        if not original_soil:
            # Generate if not provided
            reading = sensor_simulator.generate_reading()
            original_soil = {k: v for k, v in reading.items() if k != 'timestamp'}
        
        # Get the actions to simulate
        actions = data.get('actions', [])
        
        # Create a copy of original soil data to modify
        improved_soil = original_soil.copy()
        
        # Apply effects of each action
        action_effects = []
        for action in actions:
            action_type = action.get('type', '')
            
            if action_type == 'lime_application':
                # Simulate lime application
                amount = action.get('amount', 2)  # tons per hectare
                current_ph = float(improved_soil['ph_level'])
                # Lime effect increases with amount but has diminishing returns
                ph_increase = min(1.0, 0.3 * amount**0.7)
                new_ph = min(7.5, current_ph + ph_increase)
                
                action_effects.append({
                    'action': 'Lime Application',
                    'parameter': 'ph_level',
                    'before': current_ph,
                    'after': new_ph,
                    'change': round(new_ph - current_ph, 2)
                })
                
                improved_soil['ph_level'] = new_ph
            
            elif action_type == 'nitrogen_fertilizer':
                # Simulate nitrogen fertilizer application
                amount = action.get('amount', 100)  # kg per hectare
                current_n = float(improved_soil['nitrogen_level'])
                # Effect is proportional to amount with upper limit
                n_increase = min(20, amount / 10)
                new_n = min(50, current_n + n_increase)
                
                action_effects.append({
                    'action': 'Nitrogen Fertilizer Application',
                    'parameter': 'nitrogen_level',
                    'before': current_n,
                    'after': new_n,
                    'change': round(new_n - current_n, 2)
                })
                
                improved_soil['nitrogen_level'] = new_n
            
            elif action_type == 'organic_matter_addition':
                # Simulate adding organic matter
                amount = action.get('amount', 10)  # tons per hectare
                current_om = float(improved_soil['organic_matter'])
                # Organic matter increases gradually
                om_increase = min(3, amount / 10)
                new_om = min(8, current_om + om_increase)
                
                action_effects.append({
                    'action': 'Organic Matter Addition',
                    'parameter': 'organic_matter',
                    'before': current_om,
                    'after': new_om,
                    'change': round(new_om - current_om, 2)
                })
                
                improved_soil['organic_matter'] = new_om
                
                # Organic matter also affects other parameters
                if 'cation_exchange_capacity' in improved_soil:
                    current_cec = float(improved_soil['cation_exchange_capacity'])
                    new_cec = min(25, current_cec + om_increase * 0.5)
                    improved_soil['cation_exchange_capacity'] = new_cec
                    
                    action_effects.append({
                        'action': 'Organic Matter Addition',
                        'parameter': 'cation_exchange_capacity',
                        'before': current_cec,
                        'after': new_cec,
                        'change': round(new_cec - current_cec, 2)
                    })
                
                if 'moisture_content' in improved_soil:
                    current_mc = float(improved_soil['moisture_content'])
                    new_mc = min(35, current_mc + om_increase * 0.7)
                    improved_soil['moisture_content'] = new_mc
                    
                    action_effects.append({
                        'action': 'Organic Matter Addition',
                        'parameter': 'moisture_content',
                        'before': current_mc,
                        'after': new_mc,
                        'change': round(new_mc - current_mc, 2)
                    })
        
        # Calculate score before and after
        original_score, original_param_scores = soil_analyzer.calculate_score(original_soil)
        improved_score, improved_param_scores = soil_analyzer.calculate_score(improved_soil)
        
        # Calculate yield prediction before and after
        original_yield = yield_predictor.predict_yield(original_soil)
        improved_yield = yield_predictor.predict_yield(improved_soil)
        
        return jsonify({
            'original_soil': original_soil,
            'improved_soil': improved_soil,
            'original_score': round(original_score, 2),
            'improved_score': round(improved_score, 2),
            'score_change': round(improved_score - original_score, 2),
            'action_effects': action_effects,
            'original_yield': original_yield['predicted_yield'],
            'improved_yield': improved_yield['predicted_yield'],
            'yield_change': round(improved_yield['predicted_yield'] - original_yield['predicted_yield'], 2),
            'roi_estimate': calculate_roi_estimate(action_effects, improved_yield['predicted_yield'] - original_yield['predicted_yield'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_roi_estimate(action_effects, yield_increase):
    """Calculate estimated ROI for implemented actions"""
    # Simplified ROI calculation
    # Assume maize price of $250 per ton
    crop_price = 250  # USD per ton
    revenue_increase = yield_increase * crop_price
    
    # Estimate costs based on actions
    total_cost = 0
    for effect in action_effects:
        action = effect['action']
        if 'Lime Application' in action:
            total_cost += 150  # Average cost per hectare
        elif 'Nitrogen Fertilizer' in action:
            total_cost += 180  # Average cost per hectare
        elif 'Organic Matter' in action:
            total_cost += 300  # Average cost per hectare
    
    if total_cost == 0:
        return "Infinite (no costs calculated)"
    
    roi = (revenue_increase / total_cost)
    return f"{round(roi * 100, 1)}% ({round(revenue_increase, 2)} / {total_cost})"

@app.route('/api/soil-data')
def get_soil_data():
    try:
        # Generate current reading using sensor simulator
        sensor_data = sensor_simulator.generate_reading()
        
        # Remove timestamp from parameters for score calculation
        soil_parameters = {k: v for k, v in sensor_data.items() if k != 'timestamp'}
        
        # Calculate scores and recommendations
        score, parameter_scores = soil_analyzer.calculate_score(soil_parameters)
        risk_level = soil_analyzer.determine_risk_level(score)
        premium = soil_analyzer.calculate_premium(score)
        recommendations = soil_analyzer.get_recommendations(soil_parameters)
        
        # Get yield prediction
        yield_data = yield_predictor.predict_yield(soil_parameters)
        
        return jsonify({
            'timestamp': sensor_data['timestamp'],
            'parameters': soil_parameters,
            'financial_index': {
                'score': round(score, 2),
                'risk_level': risk_level,
                'premium': round(premium, 2)
            },
            'parameter_scores': {k: round(v * 100, 2) for k, v in parameter_scores.items()},
            'recommendations': recommendations,
            'yield_prediction': yield_data,
            'alerts': generate_alerts(soil_parameters)
        })
        
    except Exception as e:
        app.logger.error(f"Error in get_soil_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_alerts(sensor_data):
    alerts = []
    thresholds = {
        'ph_level': {'warning': (5.5, 7.5), 'critical': (5.0, 8.0)},
        'nitrogen_level': {'warning': (15, 45), 'critical': (10, 50)},
        # Add other parameters...
    }
    
    for param, value in sensor_data.items():
        if param in thresholds:
            warning = thresholds[param]['warning']
            critical = thresholds[param]['critical']
            
            if not critical[0] <= float(value) <= critical[1]:
                alerts.append({
                    'id': f'alert_{len(alerts)+1}',
                    'title': f'Critical {param.replace("_", " ").title()}',
                    'message': f'{param.replace("_", " ").title()} is at critical level: {value}',
                    'priority': 'critical',
                    'timestamp': datetime.now().isoformat()
                })
            elif not warning[0] <= float(value) <= warning[1]:
                alerts.append({
                    'id': f'alert_{len(alerts)+1}',
                    'title': f'Warning {param.replace("_", " ").title()}',
                    'message': f'{param.replace("_", " ").title()} is at warning level: {value}',
                    'priority': 'warning',
                    'timestamp': datetime.now().isoformat()
                })
    
    return alerts

# Main entry point
if __name__ == '__main__':
    # Initialize components
    soil_analyzer = SoilHealthIndex()
    sensor_simulator = SensorSimulator()
    yield_predictor = YieldPredictor()
    
    # Configure Flask app
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config.from_object('config.Config')
    
    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Soil Health API startup')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)


class SensorSimulator:
    """Class to simulate soil sensor readings"""
    
    def __init__(self):
        self.base_values = {
            'ph_level': 6.0,
            'nitrogen_level': 20.0,
            'phosphorus_level': 15.0,
            'potassium_level': 20.0,
            'organic_matter': 3.0,
            'cation_exchange_capacity': 12.0,
            'moisture_content': 25.0
        }
        
        # Define possible weather events that affect soil
        self.weather_events = [
            {
                'name': 'Heavy Rainfall',
                'probability': 0.05,
                'effects': {
                    'moisture_content': 7.0,
                    'nitrogen_level': -3.0,
                    'ph_level': -0.3
                }
            },
            {
                'name': 'Drought',
                'probability': 0.03,
                'effects': {
                    'moisture_content': -8.0,
                    'organic_matter': -0.2
                }
            },
            {
                'name': 'Windy Day',
                'probability': 0.08,
                'effects': {
                    'moisture_content': -2.0
                }
            },
            {
                'name': 'Light Rain',
                'probability': 0.15,
                'effects': {
                    'moisture_content': 3.0
                }
            }
        ]
        
        # Track current weather event
        self.current_event = None
        self.last_event_time = datetime.now()
        self.event_duration = timedelta(hours=6)  # Events last 6 hours
        
        # Initialize historical data
        self.historical_data = self.generate_historical_data(30)  # Generate 30 days of data
    
    def check_for_weather_event(self):
        """Check if a new weather event should occur"""
        # Check if current event has ended
        if self.current_event:
            if datetime.now() > self.last_event_time + self.event_duration:
                self.current_event = None
            else:
                return  # Event still ongoing
        
        # Random chance for new event
        for event in self.weather_events:
            if random.random() < event['probability']:
                self.current_event = event
                self.last_event_time = datetime.now()
                break
    
    def apply_weather_effects(self, reading):
        """Apply effects of current weather event"""
        if not self.current_event:
            return reading
        
        # Copy reading to avoid modifying the original
        modified_reading = reading.copy()
        
        # Apply each effect
        for param, effect in self.current_event['effects'].items():
            if param in modified_reading:
                modified_reading[param] += effect
                
                # Ensure values stay within realistic ranges
                if param == 'ph_level':
                    modified_reading[param] = max(4.0, min(8.0, modified_reading[param]))
                elif param == 'moisture_content':
                    modified_reading[param] = max(5.0, min(45.0, modified_reading[param]))
                elif param == 'organic_matter':
                    modified_reading[param] = max(0.5, min(8.0, modified_reading[param]))
                else:
                    modified_reading[param] = max(0.0, modified_reading[param])
        
        return modified_reading
    
    def generate_reading(self):
        """Generate a simulated sensor reading"""
        # Check for weather events
        self.check_for_weather_event()
        
        # Start with base values and add random variation
        reading = {}
        for param, base_value in self.base_values.items():
            # Different parameters have different variability
            if param == 'ph_level':
                variation = random.uniform(-0.2, 0.2)
            elif param in ['nitrogen_level', 'phosphorus_level', 'potassium_level']:
                variation = random.uniform(-2.0, 2.0)
            elif param == 'moisture_content':
                variation = random.uniform(-3.0, 3.0)
            else:
                variation = random.uniform(-0.5, 0.5)
            
            reading[param] = round(base_value + variation, 2)
        
        # Apply any weather effects
        reading = self.apply_weather_effects(reading)
        
        # Add timestamp
        reading['timestamp'] = datetime.now().isoformat()
        
        return reading
    
    def generate_historical_data(self, days):
        """Generate historical data for a specified number of days"""
        data = []
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Generate data at 30-minute intervals
        current_time = start_time
        while current_time <= end_time:
            # Generate reading
            reading = {}
            for param, base_value in self.base_values.items():
                # Add some daily and seasonal patterns
                hour_of_day = current_time.hour
                day_of_year = current_time.timetuple().tm_yday
                
                # Daily moisture cycle
                if param == 'moisture_content':
                    # Lower in afternoon, higher at night/morning
                    time_factor = math.cos((hour_of_day - 6) * math.pi / 12) * 3.0
                    seasonal_factor = math.sin(day_of_year * 2 * math.pi / 365) * 5.0  # Seasonal variation
                    variation = random.uniform(-2.0, 2.0) + time_factor + seasonal_factor
                
                # pH varies less but can have seasonal trends
                elif param == 'ph_level':
                    seasonal_factor = math.sin(day_of_year * 2 * math.pi / 365) * 0.3
                    variation = random.uniform(-0.1, 0.1) + seasonal_factor
                
                # Nutrients vary with seasonal cycles
                elif param in ['nitrogen_level', 'phosphorus_level', 'potassium_level']:
                    seasonal_factor = math.sin(day_of_year * 2 * math.pi / 365) * 2.0
                    variation = random.uniform(-1.5, 1.5) + seasonal_factor
                
                # Other parameters
                else:
                    variation = random.uniform(-0.5, 0.5)
                
                reading[param] = round(base_value + variation, 2)
            
            # Add timestamp
            reading['timestamp'] = current_time.isoformat()
            
            # Add to data
            data.append(reading)
            
            # Increment time
            current_time += timedelta(minutes=30)
        
        return data


class SoilAnalyzer:
    """Class to analyze soil data and calculate soil health scores"""
    
    def __init__(self):
        # Define ideal ranges for each soil parameter
        self.ideal_ranges = {
            'ph_level': (6.0, 7.0),
            'nitrogen_level': (25.0, 40.0),
            'phosphorus_level': (20.0, 30.0),
            'potassium_level': (20.0, 30.0),
            'organic_matter': (3.0, 5.0),
            'cation_exchange_capacity': (12.0, 20.0),
            'moisture_content': (20.0, 30.0)
        }
        
        # Define parameter weights for scoring
        self.parameter_weights = {
            'ph_level': 2.0,
            'nitrogen_level': 1.5,
            'phosphorus_level': 1.2,
            'potassium_level': 1.2,
            'organic_matter': 1.5,
            'cation_exchange_capacity': 0.8,
            'moisture_content': 0.8
        }
        
        # Define crop database with ideal conditions
        self.crops = {
            'maize': {
                'ideal_ph': (5.8, 7.0),
                'nitrogen_need': 'high',
                'drought_tolerance': 'medium',
                'yield_potential': 10.0  # tons per hectare
            },
            'soybean': {
                'ideal_ph': (6.0, 7.0),
                'nitrogen_need': 'low',
                'drought_tolerance': 'medium-high',
                'yield_potential': 4.0
            },
            'wheat': {
                'ideal_ph': (6.0, 7.5),
                'nitrogen_need': 'high',
                'drought_tolerance': 'medium',
                'yield_potential': 6.0
            },
            'sorghum': {
                'ideal_ph': (5.5, 7.5),
                'nitrogen_need': 'medium',
                'drought_tolerance': 'high',
                'yield_potential': 5.0
            },
            'groundnut': {
                'ideal_ph': (5.5, 7.0),
                'nitrogen_need': 'low',
                'drought_tolerance': 'medium-high',
                'yield_potential': 3.0
            },
            'cotton': {
                'ideal_ph': (5.8, 8.0),
                'nitrogen_need': 'medium',
                'drought_tolerance': 'high',
                'yield_potential': 2.5
            }
        }
    
    def calculate_parameter_score(self, param, value):
        """Calculate score for a single parameter based on ideal range"""
        if param not in self.ideal_ranges:
            return 0.0
        
        min_val, max_val = self.ideal_ranges[param]
        
        # Perfect score if within ideal range
        if min_val <= value <= max_val:
            return 1.0
        
        # Calculate how far from ideal range
        if value < min_val:
            distance = min_val - value
            # More penalty for pH being too low vs. too high
            if param == 'ph_level':
                scale_factor = min_val - 3.0  # Assume pH of 3.0 would be worst case
            else:
                scale_factor = min_val * 0.5  # 50% of minimum ideal is worst case
        else:  # value > max_val
            distance = value - max_val
            # Less penalty for pH being too high vs. too low
            if param == 'ph_level':
                scale_factor = 10.0 - max_val  # Assume pH of 10.0 would be worst case
            else:
                scale_factor = max_val * 0.5  # 50% above maximum ideal is worst case
        
        # Prevent division by zero
        if scale_factor == 0:
            scale_factor = 0.01
        
        # Calculate score (1.0 is perfect, 0.0 is worst)
        score = max(0.0, 1.0 - (distance / scale_factor))
        
        return score
    
    def calculate_score(self, soil_data):
        """Calculate overall soil health score and individual parameter scores"""
        if not soil_data:
            return 0.0, {}
        
        total_weight = 0.0
        weighted_score = 0.0
        parameter_scores = {}
        
        for param, value in soil_data.items():
            if param in self.parameter_weights:
                weight = self.parameter_weights[param]
                param_score = self.calculate_parameter_score(param, float(value))
                parameter_scores[param] = param_score
                weighted_score += param_score * weight
                total_weight += weight
        
        # Calculate final score as percentage (0-100)
        final_score = (weighted_score / total_weight) * 100 if total_weight > 0 else 0
        
        return final_score, parameter_scores
    
    def determine_risk_level(self, score):
        """Determine risk level based on soil health score"""
        if score >= 80:
            return "Low"
        elif score >= 60:
            return "Medium-Low"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Medium-High"
        else:
            return "High"
    
    def calculate_premium(self, score):
        """Calculate insurance premium based on soil health score"""
        # Base premium
        base_premium = 100  # dollars per hectare
        
        # Risk factor based on score (higher score = lower risk = lower premium)
        risk_factor = 2.0 - (score / 100.0)  # Range from 1.0 to 2.0
        
        # Calculate premium
        premium = base_premium * risk_factor
        
        return premium
    
    def get_recommendations(self, soil_data):
        """Generate basic recommendations based on soil analysis"""
        recommendations = []
        
        # Check each parameter against ideal ranges
        for param, value in soil_data.items():
            if param not in self.ideal_ranges:
                continue
            
            min_val, max_val = self.ideal_ranges[param]
            value = float(value)
            
            if value < min_val:
                if param == 'ph_level':
                    recommendations.append({
                        'parameter': 'pH Level',
                        'issue': 'Soil is too acidic',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Apply agricultural lime to raise pH'
                    })
                elif param == 'nitrogen_level':
                    recommendations.append({
                        'parameter': 'Nitrogen',
                        'issue': 'Nitrogen deficiency',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Apply nitrogen fertilizer'
                    })
                elif param == 'phosphorus_level':
                    recommendations.append({
                        'parameter': 'Phosphorus',
                        'issue': 'Phosphorus deficiency',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Apply phosphate fertilizer'
                    })
                elif param == 'potassium_level':
                    recommendations.append({
                        'parameter': 'Potassium',
                        'issue': 'Potassium deficiency',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Apply potassium fertilizer'
                    })
                elif param == 'organic_matter':
                    recommendations.append({
                        'parameter': 'Organic Matter',
                        'issue': 'Low organic matter content',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Add compost or implement cover crops'
                    })
                elif param == 'moisture_content':
                    recommendations.append({
                        'parameter': 'Moisture Content',
                        'issue': 'Soil is too dry',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Implement irrigation or water retention practices'
                    })
            elif value > max_val:
                if param == 'ph_level':
                    recommendations.append({
                        'parameter': 'pH Level',
                        'issue': 'Soil is too alkaline',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Apply sulfur or organic matter to lower pH'
                    })
                elif param == 'moisture_content':
                    recommendations.append({
                        'parameter': 'Moisture Content',
                        'issue': 'Soil is too wet',
                        'current_value': value,
                        'target_range': f"{min_val} - {max_val}",
                        'action': 'Improve drainage or reduce irrigation'
                    })
        
        return recommendations


class YieldPredictor:
    """Class to predict crop yields based on soil data using machine learning"""
    
    def __init__(self):
        # Initialize the ML model
        self.model = self._train_model()
    
    def _train_model(self):
        """
        Train a machine learning model to predict crop yields
        
        This would typically use real training data, but for this example,
        we'll create a synthetic model.
        """
        # Generate synthetic training data
        X_train = []
        y_train = []
        
        # Create a random forest regressor model
        from sklearn.ensemble import RandomForestRegressor
        
        # Generate synthetic data points
        for _ in range(1000):
            # Generate random soil parameters
            soil_sample = {
                'ph_level': random.uniform(4.0, 8.0),
                'nitrogen_level': random.uniform(10.0, 50.0),
                'phosphorus_level': random.uniform(5.0, 40.0),
                'potassium_level': random.uniform(10.0, 40.0),
                'organic_matter': random.uniform(1.0, 7.0),
                'cation_exchange_capacity': random.uniform(5.0, 25.0),
                'moisture_content': random.uniform(10.0, 40.0)
            }
            
            # Convert to feature vector
            features = [
                soil_sample['ph_level'],
                soil_sample['nitrogen_level'],
                soil_sample['phosphorus_level'],
                soil_sample['potassium_level'],
                soil_sample['organic_matter'],
                soil_sample['cation_exchange_capacity'],
                soil_sample['moisture_content']
            ]
            
            X_train.append(features)
            
            # Generate synthetic yield based on idealized relationships
            # Ideal pH around 6.5
            ph_factor = 1.0 - abs(soil_sample['ph_level'] - 6.5) * 0.15
            
            # Nitrogen has strong positive correlation with yield
            n_factor = min(1.0, soil_sample['nitrogen_level'] / 40.0)
            
            # Phosphorus important but with diminishing returns
            p_factor = min(1.0, soil_sample['phosphorus_level'] / 30.0)
            
            # Potassium similar to phosphorus
            k_factor = min(1.0, soil_sample['potassium_level'] / 30.0)
            
            # Organic matter improves overall soil health
            om_factor = min(1.0, soil_sample['organic_matter'] / 5.0)
            
            # Moisture needs to be in optimal range
            moisture = soil_sample['moisture_content']
            if moisture < 15:
                m_factor = moisture / 15.0  # Too dry
            elif moisture > 35:
                m_factor = 1.0 - (moisture - 35) / 15.0  # Too wet
            else:
                m_factor = 1.0  # Optimal
            
            # Combine factors with different weights
            yield_factor = (
                ph_factor * 0.2 +
                n_factor * 0.25 +
                p_factor * 0.15 +
                k_factor * 0.15 +
                om_factor * 0.15 +
                m_factor * 0.1
            )
            
            # Base yield in tons per hectare (maize)
            base_yield = 10.0
            simulated_yield = base_yield * yield_factor
            
            # Add some random noise
            simulated_yield += random.uniform(-0.5, 0.5)
            simulated_yield = max(0.5, simulated_yield)  # Ensure non-negative yield
            
            y_train.append(simulated_yield)
        
        # Train the model
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        return model
    
    def predict_yield(self, soil_data):
        """
        Predict crop yield based on soil data
        
        Args:
            soil_data: Dictionary with soil parameters
            
        Returns:
            Dictionary with yield prediction and related info
        """
        # Extract features from soil data
        try:
            features = [
                float(soil_data.get('ph_level', 6.0)),
                float(soil_data.get('nitrogen_level', 20.0)),
                float(soil_data.get('phosphorus_level', 15.0)),
                float(soil_data.get('potassium_level', 20.0)),
                float(soil_data.get('organic_matter', 3.0)),
                float(soil_data.get('cation_exchange_capacity', 12.0)),
                float(soil_data.get('moisture_content', 25.0))
            ]
            
            # Make prediction
            predicted_yield = self.model.predict([features])[0]
            
            # Determine confidence based on how close values are to training distribution
            confidence = self._calculate_prediction_confidence(features)
            
            # Identify suitable crops based on soil conditions
            suitable_crops = self._recommend_crops(soil_data)
            
            return {
                'predicted_yield': round(predicted_yield, 2),
                'confidence': confidence,
                'units': 'tons per hectare',
                'top_crops': suitable_crops,
                'estimated_revenue': round(predicted_yield * 250, 2),  # $250 per ton
                'potential_improvement': self._calculate_potential_improvement(soil_data)
            }
        except Exception as e:
            return {
                'error': str(e),
                'predicted_yield': 0.0,
                'confidence': 0
            }
    
    def _calculate_prediction_confidence(self, features):
        """
        Calculate a confidence score for the prediction
        
        Args:
            features: List of soil parameters
            
        Returns:
            Confidence score (0-100)
        """
        # This is a simplified confidence calculation
        # In reality, would use proper uncertainty estimation
        
        # Check if features are within expected ranges
        range_checks = [
            (4.0 <= features[0] <= 8.0),  # pH
            (5.0 <= features[1] <= 60.0),  # Nitrogen
            (5.0 <= features[2] <= 40.0),  # Phosphorus
            (5.0 <= features[3] <= 40.0),  # Potassium
            (0.5 <= features[4] <= 8.0),  # Organic matter
            (5.0 <= features[5] <= 30.0),  # CEC
            (5.0 <= features[6] <= 45.0)   # Moisture
        ]
        
        # Percentage of features in expected range
        range_score = sum(range_checks) / len(range_checks) * 100
        
        # Adjust confidence based on model uncertainty (simulated)
        model_uncertainty = random.uniform(70, 95)
        
        # Combine factors
        confidence = (range_score * 0.7) + (model_uncertainty * 0.3)
        
        return round(confidence)
    
    def _recommend_crops(self, soil_data):
        """
        Recommend suitable crops based on soil conditions
        
        Args:
            soil_data: Dictionary with soil parameters
            
        Returns:
            List of recommended crops
        """
        # Create a soil analyzer instance to get crop data
        analyzer = SoilAnalyzer()
        
        # Get soil parameters
        ph = float(soil_data.get('ph_level', 6.0))
        nitrogen = float(soil_data.get('nitrogen_level', 20.0))
        moisture = float(soil_data.get('moisture_content', 25.0))
        
        # Calculate suitability scores for each crop
        crop_scores = {}
        for crop, data in analyzer.crops.items():
            # Check pH suitability
            min_ph, max_ph = data['ideal_ph']
            if min_ph <= ph <= max_ph:
                ph_score = 1.0
            else:
                ph_distance = min(abs(ph - min_ph), abs(ph - max_ph))
                ph_score = max(0.0, 1.0 - (ph_distance / 1.0))
            
            # Check nitrogen requirement
            n_requirement = data['nitrogen_need']
            if n_requirement == 'low':
                n_score = 1.0 if nitrogen < 25.0 else 0.8
            elif n_requirement == 'medium':
                n_score = 1.0 if 20.0 <= nitrogen <= 35.0 else 0.7
            else:  # high
                n_score = 1.0 if nitrogen > 30.0 else 0.6
            
            # Check drought tolerance
            drought_tolerance = data['drought_tolerance']
            if moisture < 15.0:
                if drought_tolerance == 'high':
                    moisture_score = 0.9
                elif drought_tolerance == 'medium-high':
                    moisture_score = 0.7
                elif drought_tolerance == 'medium':
                    moisture_score = 0.5
                else:
                    moisture_score = 0.3
            elif 15.0 <= moisture <= 35.0:
                moisture_score = 1.0
            else:  # moisture > 35.0
                moisture_score = 0.6  # Excess moisture is problematic for most crops
            
            # Calculate overall score
            overall_score = (ph_score * 0.4) + (n_score * 0.3) + (moisture_score * 0.3)
            crop_scores[crop] = overall_score
        
        # Sort crops by score and return top 3
        sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
        top_crops = [crop for crop, score in sorted_crops[:3] if score > 0.6]
        
        return top_crops
    
    def _calculate_potential_improvement(self, soil_data):
        """
        Calculate potential yield improvement if soil conditions were optimized
        
        Args:
            soil_data: Dictionary with soil parameters
            
        Returns:
            Dictionary with improvement potential
        """
        # Clone soil data and optimize values
        optimized_data = soil_data.copy()
        
        # Optimize key parameters
        analyzer = SoilAnalyzer()
        for param, (min_val, max_val) in analyzer.ideal_ranges.items():
            if param in optimized_data:
                # Set to midpoint of ideal range
                optimized_data[param] = (min_val + max_val) / 2
        
        # Predict yield with optimized conditions
        features = [
            float(optimized_data.get('ph_level', 6.5)),
            float(optimized_data.get('nitrogen_level', 32.5)),
            float(optimized_data.get('phosphorus_level', 25.0)),
            float(optimized_data.get('potassium_level', 25.0)),
            float(optimized_data.get('organic_matter', 4.0)),
            float(optimized_data.get('cation_exchange_capacity', 16.0)),
            float(optimized_data.get('moisture_content', 25.0))
        ]
        
        # Make prediction
        optimized_yield = self.model.predict([features])[0]
        
        # Extract features from original soil data
        original_features = [
            float(soil_data.get('ph_level', 6.0)),
            float(soil_data.get('nitrogen_level', 20.0)),
            float(soil_data.get('phosphorus_level', 15.0)),
            float(soil_data.get('potassium_level', 20.0)),
            float(soil_data.get('organic_matter', 3.0)),
            float(soil_data.get('cation_exchange_capacity', 12.0)),
            float(soil_data.get('moisture_content', 25.0))
        ]
        
        # Make prediction for original data
        original_yield = self.model.predict([original_features])[0]
        
        # Calculate improvement
        improvement = optimized_yield - original_yield
        percent_improvement = (improvement / original_yield) * 100 if original_yield > 0 else 0
        
        return {
            'potential_yield': round(optimized_yield, 2),
            'improvement': round(improvement, 2),
            'percent_improvement': round(percent_improvement, 1),
            'increased_revenue': round(improvement * 250, 2)  # $250 per ton
        }

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler for unhandled exceptions"""
    logger.error(f"Unhandled error: {str(error)}")
    return jsonify({
        'error': str(error),
        'status': 'error'
    }), 500

@app.route('/test')
def test():
    """Test route to verify API is working"""
    return jsonify({
        'status': 'ok',
        'message': 'API is working'
    })

