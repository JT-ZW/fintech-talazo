# setup_dev.py
"""
Development environment setup script for Talazo AgriFinance Platform.

This script helps set up the development environment with sample data.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_directories():
    """Create necessary directories."""
    directories = [
        'instance',
        'instance/logs',
        'logs',
        'uploads',
        'static/uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def create_env_file():
    """Create .env file with default development settings."""
    env_content = """# Talazo AgriFinance Platform - Development Environment

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///instance/talazo_dev.db

# External API Keys (Optional)
GROQ_API_KEY=your-groq-api-key-here
SATELLITE_API_KEY=your-satellite-api-key-here

# Development Settings
DEBUG=True
LOG_TO_STDOUT=false

# Port Configuration
PORT=5000
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file with development settings")
    else:
        print("ℹ .env file already exists")


def setup_database():
    """Initialize the database with tables."""
    try:
        from app import create_app
        from app.core.extensions import db
        
        app = create_app('development')
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables created")
            
            # Generate demo data
            from app.services.data_generator import DemoDataGenerator
            generator = DemoDataGenerator()
            farmers = generator.generate_demo_farmers(20)
            
            print(f"✓ Generated {len(farmers)} demo farmers with soil samples")
            
    except Exception as e:
        print(f"✗ Database setup error: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("=" * 60)
    print("🚀 Talazo AgriFinance Platform - Development Setup")
    print("=" * 60)
    
    try:
        # Step 1: Create directories
        print("\n📁 Creating directories...")
        create_directories()
        
        # Step 2: Create environment file
        print("\n⚙️ Setting up environment...")
        create_env_file()
        
        # Step 3: Setup database
        print("\n🗄️ Setting up database...")
        if setup_database():
            print("\n🎉 Development environment setup complete!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Run the application: python run.py")
            print("3. Open browser: http://localhost:5000")
            print("4. Check API health: http://localhost:5000/api/healthcheck")
        else:
            print("\n❌ Database setup failed. Please check errors above.")
            return False
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False
    
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
