# app/utils/helpers.py
"""
Helper utility functions for Talazo AgriFinance Platform.
"""

import uuid
import math
from typing import Tuple, Optional
from datetime import datetime


def generate_unique_id(prefix: str = '') -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix (str): Optional prefix for the ID
        
    Returns:
        str: Unique identifier string
    """
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"{prefix}{unique_id}" if prefix else unique_id


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two geographic points using Haversine formula.
    
    Args:
        lat1, lon1 (float): Latitude and longitude of first point
        lat2, lon2 (float): Latitude and longitude of second point
        
    Returns:
        float: Distance in kilometers
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def parse_location(location_string: str) -> Optional[Tuple[float, float]]:
    """
    Parse location string to extract coordinates.
    
    Args:
        location_string (str): Location string in various formats
        
    Returns:
        Tuple[float, float] or None: (latitude, longitude) or None if parsing fails
    """
    if not location_string:
        return None
    
    try:
        # Try comma-separated format
        if ',' in location_string:
            parts = location_string.split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return (lat, lon)
        
        # Try space-separated format
        parts = location_string.split()
        if len(parts) == 2:
            lat = float(parts[0])
            lon = float(parts[1])
            return (lat, lon)
            
    except (ValueError, IndexError):
        pass
    
    return None


def get_zimbabwe_districts():
    """
    Get list of Zimbabwe districts.
    
    Returns:
        list: List of district names
    """
    return [
        'Harare', 'Bulawayo', 'Chitungwiza', 'Mutare', 'Gweru',
        'Kwekwe', 'Kadoma', 'Masvingo', 'Chinhoyi', 'Norton',
        'Marondera', 'Ruwa', 'Chegutu', 'Zvishavane', 'Bindura',
        'Beitbridge', 'Redcliff', 'Victoria Falls', 'Hwange',
        'Chiredzi', 'Kariba', 'Karoi', 'Chinhoyi', 'Gokwe',
        'Lupane', 'Mberengwa', 'Shurugwi', 'Plumtree', 'Rusape'
    ]


def get_zimbabwe_provinces():
    """
    Get list of Zimbabwe provinces.
    
    Returns:
        list: List of province names
    """
    return [
        'Harare',
        'Bulawayo', 
        'Manicaland',
        'Mashonaland Central',
        'Mashonaland East',
        'Mashonaland West',
        'Masvingo',
        'Matabeleland North',
        'Matabeleland South',
        'Midlands'
    ]


def get_common_crops():
    """
    Get list of common crops grown in Zimbabwe.
    
    Returns:
        list: List of crop names
    """
    return [
        'Maize',
        'Tobacco',
        'Cotton',
        'Soybean',
        'Wheat',
        'Barley',
        'Sorghum',
        'Millet',
        'Groundnuts',
        'Sunflower',
        'Sugar Beans',
        'Cowpeas',
        'Sweet Potatoes',
        'Irish Potatoes',
        'Tomatoes',
        'Vegetables'
    ]


def calculate_age_from_date(birth_date: datetime) -> int:
    """
    Calculate age from birth date.
    
    Args:
        birth_date (datetime): Birth date
        
    Returns:
        int: Age in years
    """
    today = datetime.today()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
        
    return age


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    import re
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Ensure it's not too long
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst (list): List to split
        chunk_size (int): Size of each chunk
        
    Returns:
        list: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
