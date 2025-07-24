# app/core/cli.py
"""
CLI commands for the Talazo AgriFinance Platform.
"""

import click
import os
from flask import current_app
from flask.cli import with_appcontext
from app.core.extensions import db


def register_cli_commands(app):
    """Register CLI commands with the Flask application."""
    
    @app.cli.command()
    @with_appcontext
    def init_db():
        """Initialize the database."""
        click.echo('Initializing database...')
        db.create_all()
        click.echo('Database initialized.')
    
    @app.cli.command()
    @with_appcontext
    def reset_db():
        """Reset the database (drop all tables and recreate)."""
        if click.confirm('This will delete all data. Are you sure?'):
            click.echo('Resetting database...')
            db.drop_all()
            db.create_all()
            click.echo('Database reset complete.')
    
    @app.cli.command()
    @click.option('--num-farmers', default=10, help='Number of demo farmers to create')
    @with_appcontext
    def create_demo_data(num_farmers):
        """Create demo data for testing."""
        try:
            from app.services.data_generator import DemoDataGenerator
            
            click.echo(f'Creating demo data with {num_farmers} farmers...')
            generator = DemoDataGenerator()
            generator.generate_demo_farmers(num_farmers)
            click.echo('Demo data created successfully.')
        except ImportError:
            click.echo('Demo data generator not available yet.')
    
    @app.cli.command()
    @with_appcontext
    def check_health():
        """Check system health."""
        click.echo('Checking system health...')
        
        # Check database connection
        try:
            db.engine.execute('SELECT 1')
            click.echo('✓ Database connection: OK')
        except Exception as e:
            click.echo(f'✗ Database connection: FAILED - {str(e)}')
        
        # Check required directories
        required_dirs = [
            current_app.instance_path,
            os.path.join(current_app.root_path, 'static'),
            os.path.join(current_app.root_path, '..', 'templates')
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                click.echo(f'✓ Directory {directory}: OK')
            else:
                click.echo(f'✗ Directory {directory}: MISSING')
        
        click.echo('Health check complete.')
    
    @app.cli.command()
    @with_appcontext
    def export_data():
        """Export data to CSV files."""
        try:
            from app.services.data_exporter import DataExporter
            
            click.echo('Exporting data...')
            exporter = DataExporter()
            exporter.export_all_data()
            click.echo('Data export complete.')
        except ImportError:
            click.echo('Data exporter not available yet.')
    
    @app.cli.command()
    @with_appcontext
    def train_models():
        """Train/retrain machine learning models."""
        try:
            from app.services.ml_trainer import MLModelTrainer
            
            click.echo('Training ML models...')
            trainer = MLModelTrainer()
            trainer.train_all_models()
            click.echo('Model training complete.')
        except ImportError:
            click.echo('ML trainer not available yet.')
