#!/usr/bin/env python3
"""
Database initialization script for Talazo AgriFinance Platform.
"""

from app import create_app
from app.core.extensions import db
from app.models import Farmer, SoilSample, CreditHistory, LoanApplication, InsurancePolicy
from datetime import datetime, timedelta
import random

def init_database():
    """Initialize database with tables and sample data."""
    
    app = create_app()
    
    with app.app_context():
        print("🗄️  Creating database tables...")
        
        # Drop all tables first (for clean setup)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Add sample farmers
        sample_farmers = [
            {
                'full_name': 'John Moyo',
                'phone_number': '+263712345678',
                'email': 'john.moyo@email.com',
                'national_id': 'ID12345678',
                'address': '123 Farm Road, Harare',
                'location_lat': -17.8292,
                'location_lng': 31.0522,
                'district': 'Harare',
                'province': 'Harare Province',
                'farming_experience_years': 15,
                'total_land_area': 5.5,
                'primary_crop': 'Maize',
                'secondary_crops': 'Soybeans, Groundnuts',
                'monthly_income': 800.0,
                'other_income_sources': 'Livestock',
                'banking_status': 'banked',
                'verification_status': 'verified'
            },
            {
                'full_name': 'Mary Ncube',
                'phone_number': '+263712345679',
                'email': 'mary.ncube@email.com',
                'national_id': 'ID12345679',
                'address': '456 Rural Lane, Bulawayo',
                'location_lat': -20.1619,
                'location_lng': 28.5906,
                'district': 'Bulawayo',
                'province': 'Bulawayo Province',
                'farming_experience_years': 12,
                'total_land_area': 3.2,
                'primary_crop': 'Tobacco',
                'secondary_crops': 'Maize, Cotton',
                'monthly_income': 650.0,
                'other_income_sources': 'Poultry',
                'banking_status': 'underbanked',
                'verification_status': 'verified'
            },
            {
                'full_name': 'Peter Chikwanha',
                'phone_number': '+263712345680',
                'email': 'peter.chikwanha@email.com',
                'national_id': 'ID12345680',
                'address': '789 Mountain View, Mutare',
                'location_lat': -18.9707,
                'location_lng': 32.6407,
                'district': 'Mutare',
                'province': 'Manicaland',
                'farming_experience_years': 20,
                'total_land_area': 8.7,
                'primary_crop': 'Coffee',
                'secondary_crops': 'Bananas, Avocados',
                'monthly_income': 1200.0,
                'other_income_sources': 'Tourism, Honey',
                'banking_status': 'banked',
                'verification_status': 'verified'
            }
        ]
        
        farmers = []
        for farmer_data in sample_farmers:
            farmer = Farmer(**farmer_data)
            db.session.add(farmer)
            farmers.append(farmer)
        
        # Commit farmers first to get IDs
        db.session.commit()
        
        print(f"✅ Added {len(farmers)} sample farmers")
        
        # Add sample soil samples for each farmer
        for farmer in farmers:
            for i in range(3):  # 3 samples per farmer
                from app.models.soil_sample import RiskLevel
                soil_sample = SoilSample(
                    farmer_id=farmer.id,
                    ph_level=round(random.uniform(6.0, 7.5), 1),
                    nitrogen_level=round(random.uniform(20, 60), 1),
                    phosphorus_level=round(random.uniform(10, 30), 1),
                    potassium_level=round(random.uniform(100, 200), 1),
                    organic_matter=round(random.uniform(2.0, 4.0), 1),
                    moisture_content=round(random.uniform(15, 35), 1),
                    collection_date=datetime.utcnow() - timedelta(days=i*30),
                    financial_index_score=round(random.uniform(65, 85), 1),
                    risk_level=random.choice([RiskLevel.LOW, RiskLevel.MEDIUM_LOW, RiskLevel.MEDIUM]),
                    yield_prediction=round(random.uniform(3000, 5000), 0)
                )
                db.session.add(soil_sample)
        
        db.session.commit()
        print("✅ Added sample soil data")
        
        print("\n🌱 Database initialization complete!")
        print("📊 You can now access the dashboard at: http://localhost:5000/dashboard")
        print("👥 Farmers page: http://localhost:5000/farmers")
        print("💰 Loans page: http://localhost:5000/loans")


if __name__ == '__main__':
    init_database()
