# ml_models.py
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
import random
import math

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
            if param in self.ideal_ranges:
                min_val, max_val = self.ideal_ranges[param]
                if value < min_val or value > max_val:
                    # Add uncertainty for out-of-range values
                    uncertainty += 0.1 * feature_importance[i]
        
        lower_bound = max(0, predicted_yield - predicted_yield * uncertainty)
        upper_bound = predicted_yield + predicted_yield * uncertainty
        
        # Return prediction with additional context
        return {
            'predicted_yield': round(predicted_yield, 2),
            'yield_range': {
                'lower': round(lower_bound, 2),
                'upper': round(upper_bound, 2)
            },
            'confidence': round((1 - uncertainty) * 100),
            'unit': 'tons per hectare'
        }

    # Ideal ranges for soil parameters
    ideal_ranges = {
        'ph_level': (6.0, 7.0),
        'nitrogen_level': (20, 40),
        'phosphorus_level': (15, 35),
        'potassium_level': (150, 250),
        'organic_matter': (3, 5),
        'cation_exchange_capacity': (10, 20),
        'moisture_content': (20, 30)
    }