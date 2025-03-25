class SoilHealthIndex:
    """
    Algorithm to calculate financial index based on soil health metrics
    for Zimbabwean small-scale farmers
    """
    
    # Ideal ranges for soil parameters in Zimbabwe
    IDEAL_RANGES = {
        'ph_level': (6.0, 7.0),
        'nitrogen_level': (20.0, 40.0),  # mg/kg
        'phosphorus_level': (15.0, 30.0),  # mg/kg
        'potassium_level': (150.0, 250.0),  # mg/kg
        'organic_matter': (3.0, 5.0),  # percentage
        'cation_exchange_capacity': (10.0, 20.0),  # cmol/kg
        'moisture_content': (20.0, 30.0)  # percentage
    }
    
    # Weight of each parameter in the overall score
    PARAMETER_WEIGHTS = {
        'ph_level': 0.20,
        'nitrogen_level': 0.15,
        'phosphorus_level': 0.15,
        'potassium_level': 0.15,
        'organic_matter': 0.15,
        'cation_exchange_capacity': 0.10,
        'moisture_content': 0.10
    }
    
    @staticmethod
    def calculate_parameter_score(param_name, value):
        """Calculate score for individual soil parameter"""
        if value is None:
            return 0
            
        ideal_min, ideal_max = SoilHealthIndex.IDEAL_RANGES[param_name]
        
        # Perfect score if within ideal range
        if ideal_min <= value <= ideal_max:
            return 100
        
        # Calculate how far from ideal range
        if value < ideal_min:
            deviation = (ideal_min - value) / ideal_min
        else:  # value > ideal_max
            deviation = (value - ideal_max) / ideal_max
        
        # Convert deviation to score (100 = perfect, 0 = extremely poor)
        score = max(0, 100 - (deviation * 100))
        return score
    
    @staticmethod
    def calculate_overall_score(soil_data):
        """Calculate overall soil health score"""
        total_score = 0
        total_weight = 0
        
        for param, weight in SoilHealthIndex.PARAMETER_WEIGHTS.items():
            if param in soil_data and soil_data[param] is not None:
                param_score = SoilHealthIndex.calculate_parameter_score(param, soil_data[param])
                total_score += param_score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0
            
        # Normalize based on actual weights used
        return total_score / total_weight
    
    @staticmethod
    def determine_risk_level(score):
        """Determine risk level based on soil health score"""
        if score >= 80:
            return "Low"
        elif score >= 60:
            return "Medium-Low"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Medium-High"
        else:
            return "High"
    
    @staticmethod
    def calculate_premium(score, base_premium=100):
        """Calculate insurance premium based on soil health score"""
        # Lower score = higher risk = higher premium
        risk_factor = (100 - score) / 100
        
        # Apply a non-linear relationship for more realistic premiums
        # Using a modified exponential function
        premium_multiplier = 1 + (risk_factor ** 1.5)
        
        return round(base_premium * premium_multiplier, 2)