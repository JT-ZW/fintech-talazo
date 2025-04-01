# sensors.py
import random
import math
from datetime import datetime, timedelta

class SensorSimulator:
    def __init__(self):
        # Initial base values for soil parameters
        self.base_values = {
            'ph_level': 6.5,
            'nitrogen_level': 30,
            'phosphorus_level': 25,
            'potassium_level': 200,
            'organic_matter': 4,
            'cation_exchange_capacity': 15,
            'moisture_content': 25
        }
        
        # Define normal ranges for each parameter
        self.parameter_ranges = {
            'ph_level': (5.5, 7.5),
            'nitrogen_level': (20, 40),
            'phosphorus_level': (15, 35),
            'potassium_level': (150, 250),
            'organic_matter': (2, 6),
            'cation_exchange_capacity': (10, 20),
            'moisture_content': (20, 30)
        }
        
        # Simulation variables with seasonal effects
        self.trend_direction = {param: random.choice([-1, 1]) for param in self.base_values}
        self.last_update = datetime.now()
        
        # Seasonal patterns (simplified for Zimbabwe's climate)
        self.seasons = {
            # Summer (rainy season): Nov-Mar
            'summer': {
                'months': [11, 12, 1, 2, 3],
                'effects': {
                    'moisture_content': 6.0,
                    'nitrogen_level': 2.0,
                    'organic_matter': 1.0,
                    'ph_level': -0.2  # Slight acidification due to rainfall
                }
            },
            # Winter (dry season): May-Aug
            'winter': {
                'months': [5, 6, 7, 8],
                'effects': {
                    'moisture_content': -4.0,
                    'nitrogen_level': -1.0,
                    'ph_level': 0.1  # Slight increase in pH in dry conditions
                }
            },
            # Transition periods: Apr, Sep-Oct
            'transition': {
                'months': [4, 9, 10],
                'effects': {
                    'moisture_content': -2.0
                }
            }
        }
        
        # Add some random events
        self.last_event_time = datetime.now() - timedelta(hours=24)
        self.current_event = None
        self.event_duration = timedelta(hours=0)
        
        # Configurable volatility
        self.volatility = 0.5  # 0-1 scale, higher means more random fluctuations

    def generate_reading(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        # Get current season
        current_month = timestamp.month
        season = next((s for s, data in self.seasons.items() 
                      if current_month in data['months']), 'transition')
        
        # Get seasonal effects
        seasonal_effects = self.seasons[season]['effects']
        
        # Check if we need to generate a random event (5% chance every hour)
        hours_since_last_event = (timestamp - self.last_event_time).total_seconds() / 3600
        if hours_since_last_event > 1 and random.random() < 0.05:
            self.generate_random_event(timestamp)
        
        # Apply current event if active
        event_effects = {}
        if self.current_event and timestamp < self.last_event_time + self.event_duration:
            event_effects = self.current_event['effects']
        else:
            self.current_event = None

        # Time-based variations: daily cycle and hourly randomness
        time_of_day = timestamp.hour
        day_factor = math.sin(time_of_day * math.pi / 12)  # Daily cycle for temperature effect
        day_of_year = timestamp.timetuple().tm_yday
        annual_factor = math.sin((day_of_year / 365) * 2 * math.pi)  # Annual seasonal cycle

        readings = {}
        for param, base_value in self.base_values.items():
            # Calculate various factors
            seasonal_change = seasonal_effects.get(param, 0)
            event_change = event_effects.get(param, 0)
            
            # Daily cycle effects (mostly affects moisture)
            daily_effect = 0
            if param == 'moisture_content':
                daily_effect = -day_factor * 2  # More evaporation during day
            
            # Random walk component (soil changes gradually)
            if random.random() < 0.1:  # 10% chance to change trend direction
                self.trend_direction[param] *= random.choice([-1, 1])
            
            # Random fluctuation based on volatility setting
            random_factor = random.uniform(-self.volatility, self.volatility)
            trend_factor = self.trend_direction[param] * 0.05
            
          # Continuing the SensorSimulator class in sensors.py
            # Calculate new value combining all factors
            new_value = (base_value 
                         + seasonal_change 
                         + event_change 
                         + daily_effect 
                         + random_factor 
                         + trend_factor)
            
            # Ensure value stays within defined ranges
            min_val, max_val = self.parameter_ranges[param]
            new_value = max(min_val, min(max_val, new_value))
            
            readings[param] = round(new_value, 2)
        
        readings['timestamp'] = timestamp.isoformat()
        return readings

    def generate_random_event(self, timestamp):
        """Generate a random weather event that affects soil parameters"""
        # Define possible events
        events = [
            {
                'name': 'Heavy Rainfall',
                'probability': 0.4,
                'duration': timedelta(hours=random.randint(2, 8)),
                'effects': {
                    'moisture_content': random.uniform(3.0, 6.0),
                    'nitrogen_level': random.uniform(-1.0, -3.0),  # Leaching
                    'ph_level': random.uniform(-0.2, -0.5)  # Acidification
                }
            },
            {
                'name': 'Drought',
                'probability': 0.3,
                'duration': timedelta(days=random.randint(3, 7)),
                'effects': {
                    'moisture_content': random.uniform(-4.0, -8.0),
                    'organic_matter': random.uniform(-0.2, -0.5)
                }
            },
            {
                'name': 'Heat Wave',
                'probability': 0.2,
                'duration': timedelta(days=random.randint(2, 5)),
                'effects': {
                    'moisture_content': random.uniform(-3.0, -5.0),
                    'nitrogen_level': random.uniform(-0.5, -1.5)  # Increased volatilization
                }
            },
            {
                'name': 'Cold Snap',
                'probability': 0.1,
                'duration': timedelta(days=random.randint(1, 3)),
                'effects': {
                    'moisture_content': random.uniform(0.5, 1.5),  # Reduced evaporation
                    'nitrogen_level': random.uniform(-0.2, -0.8)  # Slower microbial activity
                }
            }
        ]
        
        # Choose an event weighted by probability
        weights = [event['probability'] for event in events]
        selected_event = random.choices(events, weights=weights, k=1)[0]
        
        # Set the current event
        self.current_event = selected_event
        self.last_event_time = timestamp
        self.event_duration = selected_event['duration']
        
        return selected_event

    def generate_historical_data(self, days=7):
        data = []
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Generate data points at 30-minute intervals
        current_time = start_time
        while current_time <= end_time:
            data.append(self.generate_reading(current_time))
            current_time += timedelta(minutes=30)
        
        return data

    def get_current_readings(self):
        """Get current sensor readings"""
        return self.generate_reading()