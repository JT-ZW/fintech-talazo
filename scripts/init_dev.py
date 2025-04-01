# scripts/init_dev.py
import os
import sys
import subprocess
import secrets
from pathlib import Path
import shutil

# Add this near the top of init_dev.py, after imports
sys.path.insert(0, os.path.abspath('.'))

def setup_environment():
    """Set up the development environment"""
    print("Setting up Talazo development environment...")
    
    # Create .env file with development settings
    env_file = Path('.env')
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write(f"FLASK_APP=talazo\n")
            f.write(f"FLASK_ENV=development\n")
            f.write(f"SECRET_KEY={secrets.token_hex(16)}\n")
            f.write(f"DATABASE_URL=sqlite:///instance/talazo.db\n")
            # Add a placeholder for the Groq API key
            f.write(f"GROQ_API_KEY=your_groq_api_key_here\n")
    
    # Create instance directory if it doesn't exist
    instance_dir = Path('instance')
    if not instance_dir.exists():
        print("Creating instance directory...")
        instance_dir.mkdir()
    
    # Initialize the database
    print("Initializing database...")
    try:
        # Check if migrations directory exists
        migrations_dir = Path('migrations')
        
        # Handle existing migrations directory with options
        if migrations_dir.exists() and any(migrations_dir.iterdir()):
            print("Migrations directory already exists.")
            
            # Ask if user wants to recreate migrations
            choice = input("Do you want to [s]kip initialization, [r]ecreate migrations, or [c]ontinue with migrations? (s/r/c): ").lower()
            
            if choice == 'r':
                print("Recreating migrations directory...")
                shutil.rmtree(migrations_dir)
                subprocess.run(["flask", "db", "init"], check=True)
            elif choice == 's':
                print("Skipping database initialization...")
                # We'll continue without doing any database operations
            else:
                print("Continuing with existing migrations...")
                # We'll continue with migrate/upgrade but skip init
        else:
            # No migrations directory, so run init
            print("Creating new migrations directory...")
            subprocess.run(["flask", "db", "init"], check=True)
        
        # Only run migrate and upgrade if we didn't choose to skip
        if choice != 's' if 'choice' in locals() else True:
            print("Running database migrations...")
            subprocess.run(["flask", "db", "migrate", "-m", "Initial migration"], check=True)
            subprocess.run(["flask", "db", "upgrade"], check=True)
        
        # Create admin user
        from talazo.models import db, User, UserRole
        from talazo import create_app
        
        app = create_app()
        with app.app_context():
            # Check if admin user exists
            if not User.query.filter_by(username='admin').first():
                print("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role=UserRole.ADMIN
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created with username 'admin' and password 'admin123'")
        
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if setup_environment():
        print("Development environment setup complete!")
        print("Next steps:")
        print("1. Activate your virtual environment")
        print("2. Run 'flask run' to start the application")
        print("3. Visit http://localhost:5000 in your browser")
    else:
        print("Failed to set up development environment.")
        sys.exit(1)