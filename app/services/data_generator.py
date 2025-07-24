# app/services/data_generator.py
"""
Demo data generation service for Talazo AgriFinance Platform.
"""

import random
from datetime import datetime, timedelta
from typing import List
from app.models import Farmer, SoilSample, CreditHistory
from app.core.extensions import db
from app.utils.helpers import get_zimbabwe_districts, get_zimbabwe_provinces, get_common_crops


class DemoDataGenerator:
    """Service for generating realistic demo data."""
    
    def __init__(self):
        self.districts = get_zimbabwe_districts()
        self.provinces = get_zimbabwe_provinces()
        self.crops = get_common_crops()
    
    def generate_demo_farmers(self, count: int = 10) -> List[Farmer]:
        """Generate demo farmer records."""
        farmers = []
        
        for i in range(count):
            farmer = Farmer(
                full_name=self._generate_farmer_name(),
                phone_number=self._generate_phone_number(),
                district=random.choice(self.districts),
                province=random.choice(self.provinces),
                primary_crop=random.choice(self.crops),
                farming_experience_years=random.randint(1, 30),
                total_land_area=round(random.uniform(0.5, 10.0), 2),
                national_id=self._generate_national_id()
            )
            
            db.session.add(farmer)
            farmers.append(farmer)
        
        db.session.commit()
        
        # Generate soil samples for each farmer
        for farmer in farmers:
            self._generate_soil_samples_for_farmer(farmer)
        
        return farmers
    
    def _generate_farmer_name(self) -> str:
        """Generate realistic Zimbabwean farmer names."""
        first_names = ['Tendai', 'Chipo', 'Blessing', 'Faith', 'Memory', 'Gift', 'Trust', 'Hope']
        last_names = ['Moyo', 'Ncube', 'Dube', 'Sibanda', 'Mpofu', 'Nyoni', 'Banda', 'Phiri']
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_phone_number(self) -> str:
        """Generate realistic Zimbabwe phone number."""
        return f"077{random.randint(1000000, 9999999)}"
    
    def _generate_national_id(self) -> str:
        """Generate demo national ID."""
        return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}-A-{random.randint(10, 99)}"
    
    def _generate_soil_samples_for_farmer(self, farmer: Farmer, count: int = 3):
        """Generate soil samples for a farmer."""
        for i in range(count):
            days_ago = random.randint(30, 365)
            collection_date = datetime.utcnow() - timedelta(days=days_ago)
            
            sample = SoilSample(
                farmer_id=farmer.id,
                collection_date=collection_date,
                ph_level=round(random.uniform(4.5, 8.0), 1),
                nitrogen_level=round(random.uniform(10, 60), 1),
                phosphorus_level=round(random.uniform(5, 50), 1),
                potassium_level=round(random.uniform(50, 300), 1),
                organic_matter=round(random.uniform(0.5, 6.0), 1),
                moisture_content=round(random.uniform(10, 40), 1)
            )
            
            # Calculate scores
            sample.financial_index_score = sample.calculate_soil_health_score()
            
            db.session.add(sample)
        
        db.session.commit()
