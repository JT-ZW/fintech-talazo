# app/services/ml_trainer.py
"""
Machine Learning Model Trainer for Talazo AgriFinance Platform.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MLModelTrainer:
    """Train and manage machine learning models for the platform."""
    
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(__file__), '../../models')
        os.makedirs(self.models_dir, exist_ok=True)
    
    def train_yield_prediction_model(self, data=None):
        """
        Train the crop yield prediction model.
        
        Args:
            data (pd.DataFrame, optional): Training data. If None, generates synthetic data.
        """
        logger.info("Training yield prediction model...")
        
        if data is None:
            data = self._generate_synthetic_training_data()
        
        # Prepare features and target
        feature_columns = [
            'ph_level', 'nitrogen_level', 'phosphorus_level', 
            'potassium_level', 'organic_matter', 'moisture_content'
        ]
        
        X = data[feature_columns]
        y = data['yield_tons_per_hectare']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model performance - MSE: {mse:.4f}, R²: {r2:.4f}")
        
        # Save model
        model_path = os.path.join(self.models_dir, 'yield_prediction_model.pkl')
        joblib.dump(model, model_path)
        
        # Save model metadata
        metadata = {
            'model_type': 'RandomForestRegressor',
            'features': feature_columns,
            'performance': {'mse': mse, 'r2': r2},
            'trained_at': datetime.utcnow().isoformat(),
            'model_path': model_path
        }
        
        metadata_path = os.path.join(self.models_dir, 'yield_model_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        return model
    
    def train_all_models(self):
        """Train all ML models."""
        models = {}
        
        # Train yield prediction model
        models['yield_prediction'] = self.train_yield_prediction_model()
        
        logger.info("All models trained successfully")
        return models
    
    def _generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic training data for model development."""
        np.random.seed(42)
        
        # Generate soil parameters
        ph_levels = np.random.normal(6.5, 0.8, n_samples)
        nitrogen_levels = np.random.normal(50, 15, n_samples)
        phosphorus_levels = np.random.normal(30, 10, n_samples)
        potassium_levels = np.random.normal(200, 50, n_samples)
        organic_matter = np.random.normal(3.5, 1.0, n_samples)
        moisture_content = np.random.normal(25, 8, n_samples)
        
        # Clip values to realistic ranges
        ph_levels = np.clip(ph_levels, 4.0, 9.0)
        nitrogen_levels = np.clip(nitrogen_levels, 10, 120)
        phosphorus_levels = np.clip(phosphorus_levels, 5, 80)
        potassium_levels = np.clip(potassium_levels, 50, 400)
        organic_matter = np.clip(organic_matter, 0.5, 8.0)
        moisture_content = np.clip(moisture_content, 5, 50)
        
        # Calculate yield based on soil parameters (simplified model)
        yield_base = 3.0  # base yield in tons per hectare
        
        # pH effect (optimal around 6.0-7.0)
        ph_factor = 1 - 0.1 * np.abs(ph_levels - 6.5)
        
        # Nutrient effects
        n_factor = np.minimum(nitrogen_levels / 80.0, 1.0)
        p_factor = np.minimum(phosphorus_levels / 40.0, 1.0)
        k_factor = np.minimum(potassium_levels / 250.0, 1.0)
        
        # Organic matter and moisture effects
        om_factor = np.minimum(organic_matter / 5.0, 1.0)
        moisture_factor = np.maximum(0.3, 1 - 0.02 * np.abs(moisture_content - 25))
        
        # Calculate final yield
        yield_tons = (yield_base * ph_factor * n_factor * p_factor * 
                     k_factor * om_factor * moisture_factor)
        
        # Add some noise
        yield_tons += np.random.normal(0, 0.3, n_samples)
        yield_tons = np.clip(yield_tons, 0.5, 8.0)
        
        # Create DataFrame
        data = pd.DataFrame({
            'ph_level': ph_levels,
            'nitrogen_level': nitrogen_levels,
            'phosphorus_level': phosphorus_levels,
            'potassium_level': potassium_levels,
            'organic_matter': organic_matter,
            'moisture_content': moisture_content,
            'yield_tons_per_hectare': yield_tons
        })
        
        return data
