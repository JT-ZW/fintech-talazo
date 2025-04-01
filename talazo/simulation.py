# simulation.py
import random
from datetime import datetime, timedelta
import json
import csv
import os
from .models import SoilSampleStatus, Farmer, FarmPlot, SoilSample, User, UserRole, db
from .sensors import SensorSimulator
from werkzeug.security import generate_password_hash

class SimulationManager:
    def __init__(self):
        self.sensor_simulator = SensorSimulator()
        self.regions = [
            'Mashonaland Central', 'Mashonaland East', 'Mashonaland West',
            'Manicaland', 'Masvingo', 'Matabeleland North', 'Matabeleland South',
            'Midlands', 'Harare', 'Bulawayo'
        ]
        self.common_crops = [
            'Maize', 'Tobacco', 'Cotton', 'Soybean', 'Groundnut',
            'Sorghum', 'Millet', 'Wheat', 'Sugar cane', 'Vegetables'
        ]
        
    def generate_demo_data(self, num_farmers=50):
        """Generate demonstration data for the specified number of farmers"""
        # Create users and farmers
        farmers_data = self._create_farmers(num_farmers)
        
        # Create farm plots for each farmer
        plots_data = self._create_farm_plots(farmers_data)
        
        # Generate soil samples for each plot
        soil_samples = self._generate_soil_samples(plots_data)
        
        return {
            'farmers': farmers_data,
            'plots': plots_data,
            'soil_samples': soil_samples
        }
    
    def _create_farmers(self, num_farmers):
        """Create simulated farmer data"""
        farmers = []
        
        for i in range(num_farmers):
            # Create user account
            username = f"farmer{i+1}"
            email = f"farmer{i+1}@example.com"
            
            # Generate farmer data
            farmer_data = {
                'username': username,
                'email': email,
                'full_name': self._generate_random_name(),
                'phone_number': f"+263 7{random.randint(10000000, 99999999)}",
                'national_id': f"{random.randint(10, 99)}-{random.randint(100000, 999999)}-{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(10, 99)}",
                'address': f"Plot {random.randint(1, 1000)}, {random.choice(['Village', 'Farm', 'Homestead'])} {random.randint(1, 100)}, {random.choice(self.regions)}",
                'location_lat': -17.0 + random.uniform(-2, 2),  # Zimbabwe is roughly -17 to -22 latitude
                'location_lng': 30.0 + random.uniform(-5, 3),   # and 25 to 33 longitude
                'farming_experience_years': random.randint(1, 40),
                'total_land_area': round(random.uniform(0.5, 50), 1),  # hectares
                'primary_crop': random.choice(self.common_crops)
            }
            
            farmers.append(farmer_data)
        
        return farmers
    
    def _create_farm_plots(self, farmers):
        """Create farm plots for each farmer"""
        plots = []
        
        for i, farmer in enumerate(farmers):
            # Each farmer has 1-3 plots
            num_plots = random.randint(1, 3)
            
            for j in range(num_plots):
                # Divide total land area among plots
                total_area = farmer['total_land_area']
                if num_plots == 1:
                    plot_area = total_area
                else:
                    # Random division of land
                    if j < num_plots - 1:
                        plot_area = round(random.uniform(0.2, 0.7) * total_area, 1)
                        total_area -= plot_area
                    else:
                        plot_area = round(total_area, 1)
                
                plot_data = {
                    'farmer_id': i + 1,
                    'name': f"Plot {j+1}",
                    'area': plot_area,
                    'location_lat': farmer['location_lat'] + random.uniform(-0.01, 0.01),
                    'location_lng': farmer['location_lng'] + random.uniform(-0.01, 0.01),
                    'current_crop': farmer['primary_crop'] if j == 0 else random.choice(self.common_crops),
                    'planting_date': (datetime.now() - timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d'),
                    'expected_harvest_date': (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d')
                }
                
                plots.append(plot_data)
        
        return plots
    
    def _generate_soil_samples(self, plots):
        """Generate soil samples for each farm plot"""
        samples = []
        
        for i, plot in enumerate(plots):
            # Each plot has 1-2 soil samples
            num_samples = random.randint(1, 2)
            
            for j in range(num_samples):
                # For multiple samples, use different dates
                if j == 0:
                    collection_date = datetime.now() - timedelta(days=random.randint(1, 30))
                else:
                    collection_date = datetime.now() - timedelta(days=random.randint(60, 180))
                
                # Generate soil reading for this location and date
                soil_reading = self.sensor_simulator.generate_reading(collection_date)
                
                sample_data = {
                    'farmer_id': plot['farmer_id'],
                    'farm_plot_id': i + 1,
                    'collection_date': collection_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': random.choice(['collected', 'analyzed', 'verified']),
                    'ph_level': soil_reading['ph_level'],
                    'nitrogen_level': soil_reading['nitrogen_level'],
                    'phosphorus_level': soil_reading['phosphorus_level'],
                    'potassium_level': soil_reading['potassium_level'],
                    'organic_matter': soil_reading['organic_matter'],
                    'cation_exchange_capacity': soil_reading['cation_exchange_capacity'],
                    'moisture_content': soil_reading['moisture_content'],
                    'texture': random.choice(['Sandy', 'Clay', 'Loam', 'Sandy Loam', 'Clay Loam']),
                    'structure': random.choice(['Granular', 'Blocky', 'Platy', 'Prismatic']),
                    'depth': random.randint(10, 60)  # cm
                }
                
                samples.append(sample_data)
        
        return samples
    
    def _generate_random_name(self):
        """Generate a random Zimbabwean name"""
        first_names = [
            'Tatenda', 'Farai', 'Tendai', 'Tafadzwa', 'Tapiwa', 'Kudakwashe', 'Tinashe',
            'Simba', 'Nyasha', 'Tanaka', 'Chiedza', 'Rumbidzai', 'Vimbai', 'Chipo',
            'Munashe', 'Panashe', 'Kudzai', 'Tsitsi', 'Tonderai', 'Takudzwa'
        ]
        
        last_names = [
            'Moyo', 'Ncube', 'Dube', 'Mpofu', 'Ndlovu', 'Sibanda', 'Nkomo',
            'Mutasa', 'Chigwedere', 'Mugabe', 'Tsvangirai', 'Chiwenga', 'Shumba',
            'Muchinguri', 'Sekeramayi', 'Mnangagwa', 'Chinamasa', 'Muzenda', 'Mujuru'
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def save_to_database(self):
        """Save generated data to the database"""
        # Generate data
        data = self.generate_demo_data()
        
        try:
            # Create users and farmers
            for farmer_data in data['farmers']:
                # Create user
                user = User(
                    username=farmer_data['username'],
                    email=farmer_data['email'],
                    role=UserRole.FARMER
                )
                user.set_password('password123')  # Default password
                db.session.add(user)
                db.session.flush()  # Get the user ID
                
                # Create farmer profile
                farmer = Farmer(
                    user_id=user.id,
                    full_name=farmer_data['full_name'],
                    phone_number=farmer_data['phone_number'],
                    national_id=farmer_data['national_id'],
                    address=farmer_data['address'],
                    location_lat=farmer_data['location_lat'],
                    location_lng=farmer_data['location_lng'],
                    farming_experience_years=farmer_data['farming_experience_years'],
                    total_land_area=farmer_data['total_land_area'],
                    primary_crop=farmer_data['primary_crop']
                )
                db.session.add(farmer)
            
            db.session.commit()
            
            # Create farm plots
            for plot_data in data['plots']:
                plot = FarmPlot(
                    farmer_id=plot_data['farmer_id'],
                    name=plot_data['name'],
                    area=plot_data['area'],
                    location_lat=plot_data['location_lat'],
                    location_lng=plot_data['location_lng'],
                    current_crop=plot_data['current_crop'],
                    planting_date=datetime.strptime(plot_data['planting_date'], '%Y-%m-%d'),
                    expected_harvest_date=datetime.strptime(plot_data['expected_harvest_date'], '%Y-%m-%d')
                )
                db.session.add(plot)
            
            db.session.commit()
            
            # Create soil samples
            for sample_data in data['soil_samples']:
                sample = SoilSample(
                    farmer_id=sample_data['farmer_id'],
                    farm_plot_id=sample_data['farm_plot_id'],
                    collection_date=datetime.strptime(sample_data['collection_date'], '%Y-%m-%d %H:%M:%S'),
                    status=SoilSampleStatus(sample_data['status']),
                    ph_level=sample_data['ph_level'],
                    nitrogen_level=sample_data['nitrogen_level'],
                    phosphorus_level=sample_data['phosphorus_level'],
                    potassium_level=sample_data['potassium_level'],
                    organic_matter=sample_data['organic_matter'],
                    cation_exchange_capacity=sample_data['cation_exchange_capacity'],
                    moisture_content=sample_data['moisture_content'],
                    texture=sample_data['texture'],
                    structure=sample_data['structure'],
                    depth=sample_data['depth']
                )
                db.session.add(sample)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f"Created {len(data['farmers'])} farmers, {len(data['plots'])} plots, and {len(data['soil_samples'])} soil samples"
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_csv(self, output_dir='data'):
        """Export generated data to CSV files"""
        # Generate data
        data = self.generate_demo_data()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Write farmers data
        with open(os.path.join(output_dir, 'farmers.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data['farmers'][0].keys())
            writer.writeheader()
            writer.writerows(data['farmers'])
        
        # Write plots data
        with open(os.path.join(output_dir, 'plots.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data['plots'][0].keys())
            writer.writeheader()
            writer.writerows(data['plots'])
        
       # Write soil samples data
        with open(os.path.join(output_dir, 'soil_samples.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data['soil_samples'][0].keys())
            writer.writeheader()
            writer.writerows(data['soil_samples'])
        
        return {
            'success': True,
            'message': f"Exported {len(data['farmers'])} farmers, {len(data['plots'])} plots, and {len(data['soil_samples'])} soil samples to {output_dir}/"
        }