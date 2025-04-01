#!/usr/bin/env python
"""
Talazo AgriFinance Platform - Development Setup Script
This script sets up the development environment for the Talazo AgriFinance Platform.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import random
import string
import json
from datetime import datetime

# Add the parent directory to the path so we can import the application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DOTENV_TEMPLATE = """# Talazo AgriFinance Platform - Development Environment Variables
FLASK_APP=talazo
FLASK_ENV=development
SECRET_KEY={secret_key}
GROQ_API_KEY=

# Database Configuration
DEV_DATABASE_URL=sqlite:///{db_path}
TESTING_DATABASE_URL=sqlite:///:memory:

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@talazoagritech.com
"""

def generate_secret_key(length=32):
    """Generate a random secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(alphabet) for _ in range(length))

def create_dotenv_file():
    """Create a .env file with development environment variables."""
    print("Creating .env file...")
    
    # Generate a random secret key
    secret_key = generate_secret_key()
    
    # Get the project root directory
    project_dir = Path(__file__).parent.parent
    instance_dir = os.path.join(project_dir, 'instance')
    
    # Make sure the instance directory exists
    os.makedirs(instance_dir, exist_ok=True)
    
    # Database path with absolute path
    db_path = os.path.join(instance_dir, 'talazo_dev.db')
    
    # Create the .env file
    dotenv_path = os.path.join(project_dir, '.env')
    with open(dotenv_path, 'w') as f:
        f.write(DOTENV_TEMPLATE.format(
            secret_key=secret_key,
            db_path=db_path
        ))
    
    print(f"Created .env file at {dotenv_path}")

def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    
    try:
        # Install the package in development mode
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
        
        # Install development dependencies
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'pytest', 'pytest-flask', 'flake8', 'black'
        ], check=True)
        
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def setup_database():
    """Set up the database with initial schema."""
    print("Setting up database...")
    
    try:
        # Import the application and create tables
        from talazo import create_app
        from talazo.models.base import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

def create_admin_user():
    """Create an admin user if it doesn't exist."""
    print("Creating admin user...")
    
    try:
        from talazo import create_app
        from talazo.models.base import db
        from talazo.models.user import User, UserRole
        
        app = create_app()
        with app.app_context():
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("Admin user already exists")
                return
            
            # Create admin user
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@talazoagritech.com',
                role=UserRole.ADMIN,
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        sys.exit(1)

def create_directory_structure():
    """Create the required directory structure for the project."""
    print("Creating directory structure...")
    
    # Get the project root directory
    project_dir = Path(__file__).parent.parent
    
    # Create required directories
    directories = [
        os.path.join(project_dir, 'instance'),
        os.path.join(project_dir, 'instance', 'logs'),
        os.path.join(project_dir, 'talazo', 'static', 'css'),
        os.path.join(project_dir, 'talazo', 'static', 'js'),
        os.path.join(project_dir, 'talazo', 'static', 'img'),
        os.path.join(project_dir, 'talazo', 'templates'),
        os.path.join(project_dir, 'tests')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_simulation_data():
    """Generate simulation data for development."""
    print("Setting up simulation data...")
    
    try:
        from talazo import create_app
        from talazo.simulation import SimulationManager
        
        app = create_app()
        with app.app_context():
            # Create simulation manager
            manager = SimulationManager()
            
            # Save demo data to database
            result = manager.save_to_database()
            if result['success']:
                print(result['message'])
            else:
                print(f"Error generating simulation data: {result['error']}")
    except Exception as e:
        print(f"Error setting up simulation data: {e}")

def main():
    """Main function to set up the development environment."""
    print("=== Talazo AgriFinance Platform - Development Setup ===")
    
    # Create directory structure
    create_directory_structure()
    
    # Create .env file
    create_dotenv_file()
    
    # Install dependencies
    install_dependencies()
    
    # Set up database
    setup_database()
    
    # Create admin user
    create_admin_user()
    
    # Set up simulation data
    setup_simulation_data()
    
    print("\n=== Setup Complete ===")
    print("You can now run the application with 'flask run'")
    print("Admin credentials: username=admin, password=admin123")

if __name__ == "__main__":
    main()