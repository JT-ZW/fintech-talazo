# cli.py - Command Line Interface for Talazo AgriFinance

import click
from flask.cli import with_appcontext
from talazo import create_app
from talazo.simulation import SimulationManager
from talazo.models import db

@click.group()
def cli():
    """Talazo AgriFinance Management CLI"""
    pass

# Create a simulation subgroup
@cli.group('simulation')
def simulation_group():
    """Commands for data simulation"""
    pass

@simulation_group.command('generate-demo-data')
@click.option('--num-farmers', default=50, help='Number of farmers to generate')
@click.option('--output-format', type=click.Choice(['database', 'csv']), default='database')
@with_appcontext
def generate_demo_data(num_farmers, output_format):
    """Generate demonstration data for the application"""
    app = create_app()
    
    with app.app_context():
        # Initialize simulation manager
        sim_manager = SimulationManager()
        
        if output_format == 'database':
            # Save to database
            result = sim_manager.save_to_database()
            if result['success']:
                click.echo(result['message'])
            else:
                click.echo(f"Error: {result['error']}")
        else:
            # Export to CSV
            result = sim_manager.export_to_csv()
            if result['success']:
                click.echo(result['message'])
            else:
                click.echo(f"Error: {result['error']}")

@simulation_group.command('reset-database')
@with_appcontext
def reset_database():
    """Reset the entire database and create fresh tables"""
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create new tables
        db.create_all()
        
        click.echo("Database has been reset and tables recreated.")

@simulation_group.command('add-default-admin')
@with_appcontext
def add_default_admin():
    """Add a default admin user to the database"""
    from talazo.models import User, UserRole
    from werkzeug.security import generate_password_hash
    
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        
        if existing_admin:
            click.echo("Admin user already exists.")
            return
        
        # Create default admin
        admin_user = User(
            username='admin',
            email='admin@talazoagritech.com',
            role=UserRole.ADMIN
        )
        admin_user.set_password('admin123')
        
        db.session.add(admin_user)
        db.session.commit()
        
        click.echo("Default admin user created successfully.")

# Optionally, you can add more groups and commands here
if __name__ == '__main__':
    cli()