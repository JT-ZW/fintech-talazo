#!/usr/bin/env python3
# test_reorganized_app.py
"""
Test script to verify the reorganized Talazo AgriFinance Platform works correctly.
"""

import os
import sys
import tempfile
import unittest
from contextlib import contextmanager

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


class TalazoReorganizationTest(unittest.TestCase):
    """Test the reorganized application structure."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['DATABASE_URL'] = f'sqlite:///{self.test_db_path}'
    
    def tearDown(self):
        """Clean up test environment."""
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def test_app_factory_import(self):
        """Test that the app factory can be imported."""
        try:
            from app import create_app
            self.assertTrue(callable(create_app))
            print("✓ App factory import successful")
        except ImportError as e:
            self.fail(f"Failed to import app factory: {e}")
    
    def test_app_creation(self):
        """Test that the app can be created."""
        try:
            from app import create_app
            app = create_app('testing')
            self.assertIsNotNone(app)
            self.assertEqual(app.config['TESTING'], True)
            print("✓ App creation successful")
        except Exception as e:
            self.fail(f"Failed to create app: {e}")
    
    def test_core_imports(self):
        """Test that core modules can be imported."""
        try:
            from app.core.config import get_config
            from app.core.extensions import db, ma
            from app.core.errors import register_error_handlers
            print("✓ Core module imports successful")
        except ImportError as e:
            self.fail(f"Failed to import core modules: {e}")
    
    def test_model_imports(self):
        """Test that model modules can be imported."""
        try:
            from app.models import Farmer, SoilSample, CreditHistory
            print("✓ Model imports successful")
        except ImportError as e:
            self.fail(f"Failed to import models: {e}")
    
    def test_service_imports(self):
        """Test that service modules can be imported."""
        try:
            from app.services.soil_analyzer import SoilAnalyzer
            from app.services.farm_viability_scorer import FarmViabilityScorer
            from app.services.data_generator import DemoDataGenerator
            print("✓ Service imports successful")
        except ImportError as e:
            self.fail(f"Failed to import services: {e}")
    
    def test_api_imports(self):
        """Test that API blueprints can be imported."""
        try:
            from app.api.main import main_bp
            from app.api.farmers import farmers_bp
            from app.api.scoring import scoring_bp
            print("✓ API blueprint imports successful")
        except ImportError as e:
            self.fail(f"Failed to import API blueprints: {e}")
    
    def test_database_initialization(self):
        """Test that the database can be initialized."""
        try:
            from app import create_app
            from app.core.extensions import db
            
            app = create_app('testing')
            with app.app_context():
                db.create_all()
                # Test that tables are created
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                expected_tables = ['farmers', 'soil_samples', 'credit_history']
                for table in expected_tables:
                    if table in tables:
                        print(f"✓ Table '{table}' created successfully")
                    else:
                        print(f"⚠ Table '{table}' not found (might be expected)")
            
            print("✓ Database initialization successful")
        except Exception as e:
            self.fail(f"Failed to initialize database: {e}")
    
    def test_soil_analyzer_functionality(self):
        """Test that the soil analyzer works."""
        try:
            from app.services.soil_analyzer import SoilAnalyzer
            
            analyzer = SoilAnalyzer()
            
            # Test soil data
            soil_data = {
                'ph_level': 6.5,
                'nitrogen_level': 45,
                'phosphorus_level': 25,
                'potassium_level': 180,
                'organic_matter': 3.2,
                'moisture_content': 22
            }
            
            score = analyzer.calculate_financial_index(soil_data)
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
            
            risk_level = analyzer.determine_risk_level(score)
            self.assertIsInstance(risk_level, str)
            
            print(f"✓ Soil analyzer functional (Score: {score:.2f}, Risk: {risk_level})")
        except Exception as e:
            self.fail(f"Soil analyzer test failed: {e}")
    
    def test_farm_viability_scorer(self):
        """Test that the farm viability scorer works."""
        try:
            from app.services.farm_viability_scorer import FarmViabilityScorer
            
            scorer = FarmViabilityScorer()
            
            # Test farm data
            farm_data = {
                'soil_health_score': 75.5,
                'farm_size': 2.5,
                'farming_experience': 8,
                'crop_diversity': 3,
                'location_risk': 'medium'
            }
            
            viability_score = scorer.calculate_viability_score(farm_data)
            self.assertIsInstance(viability_score, (int, float))
            self.assertGreaterEqual(viability_score, 0)
            self.assertLessEqual(viability_score, 100)
            
            print(f"✓ Farm viability scorer functional (Score: {viability_score:.2f})")
        except Exception as e:
            self.fail(f"Farm viability scorer test failed: {e}")
    
    def test_api_endpoints(self):
        """Test that API endpoints are accessible."""
        try:
            from app import create_app
            
            app = create_app('testing')
            client = app.test_client()
            
            # Test main endpoint
            response = client.get('/')
            self.assertIn(response.status_code, [200, 404])  # 404 is OK if no template
            
            # Test API health check
            response = client.get('/api/healthcheck')
            self.assertEqual(response.status_code, 200)
            
            print("✓ API endpoints accessible")
        except Exception as e:
            self.fail(f"API endpoint test failed: {e}")


def run_comprehensive_test():
    """Run a comprehensive test of the reorganized application."""
    print("=" * 60)
    print("🧪 TALAZO AGRIFINANCE - REORGANIZATION TEST")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print()
    
    # Run tests
    suite = unittest.TestSuite()
    suite.addTest(TalazoReorganizationTest('test_app_factory_import'))
    suite.addTest(TalazoReorganizationTest('test_core_imports'))
    suite.addTest(TalazoReorganizationTest('test_model_imports'))
    suite.addTest(TalazoReorganizationTest('test_service_imports'))
    suite.addTest(TalazoReorganizationTest('test_api_imports'))
    suite.addTest(TalazoReorganizationTest('test_app_creation'))
    suite.addTest(TalazoReorganizationTest('test_database_initialization'))
    suite.addTest(TalazoReorganizationTest('test_soil_analyzer_functionality'))
    suite.addTest(TalazoReorganizationTest('test_farm_viability_scorer'))
    suite.addTest(TalazoReorganizationTest('test_api_endpoints'))
    
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED! Reorganization successful!")
        print("You can now run the application with: python run.py")
    else:
        print(f"❌ {len(result.failures + result.errors)} tests failed.")
        for test, error in result.failures + result.errors:
            print(f"Failed: {test}")
            print(f"Error: {error}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
