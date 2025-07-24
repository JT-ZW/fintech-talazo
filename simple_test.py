#!/usr/bin/env python3
# simple_test.py
"""
Simple test to isolate import issues.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test imports step by step."""
    try:
        print("1. Testing core extensions...")
        from app.core.extensions import db
        print("✓ Core extensions imported")
        
        print("2. Testing config...")
        from app.core.config import get_config
        print("✓ Config imported")
        
        print("3. Testing individual models...")
        from app.models.farmer import Farmer
        print("✓ Farmer model imported")
        
        from app.models.soil_sample import SoilSample
        print("✓ SoilSample model imported")
        
        print("4. Testing app factory...")
        from app import create_app
        print("✓ App factory imported")
        
        print("5. Creating test app...")
        app = create_app('testing')
        print("✓ App created successfully")
        
        print("6. Testing database initialization...")
        with app.app_context():
            db.create_all()
            print("✓ Database tables created")
        
        print("\n🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
