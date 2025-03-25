class SoilHealthIndex:
    def __init__(self):
        self.weights = {
            'ph_level': 0.20,
            'nitrogen_level': 0.15,
            'phosphorus_level': 0.15,
            'potassium_level': 0.15,
            'organic_matter': 0.15,
            'cation_exchange_capacity': 0.10,
            'moisture_content': 0.10
        }
        
        self.ideal_ranges = {
            'ph_level': (6.0, 7.0),
            'nitrogen_level': (20, 40),
            'phosphorus_level': (20, 30),
            'potassium_level': (150, 250),
            'organic_matter': (3, 5),
            'cation_exchange_capacity': (10, 20),
            'moisture_content': (20, 30)
        }

    def calculate_score(self, soil_data):
        total_score = 0
        for param, value in soil_data.items():
            if param in self.weights:
                param_score = self._score_parameter(param, value)
                total_score += param_score * self.weights[param]
        return total_score * 100  # Convert to 0-100 scale

    def _score_parameter(self, param, value):
        min_ideal, max_ideal = self.ideal_ranges[param]
        if min_ideal <= value <= max_ideal:
            return 1.0
        elif value < min_ideal:
            return max(0, 1 - (min_ideal - value) / min_ideal)
        else:
            return max(0, 1 - (value - max_ideal) / max_ideal)

    def determine_risk_level(self, score):
        if score >= 80:
            return "Low Risk"
        elif score >= 60:
            return "Medium-Low Risk"
        elif score >= 40:
            return "Medium Risk"
        elif score >= 20:
            return "Medium-High Risk"
        else:
            return "High Risk"

    def calculate_premium(self, score):
        base_premium = 1000  # Base premium in USD
        risk_factor = (100 - score) / 100
        return base_premium * (1 + risk_factor)

    def get_recommendations(self, soil_data):
        recommendations = []
        for param, value in soil_data.items():
            if param in self.ideal_ranges:
                min_ideal, max_ideal = self.ideal_ranges[param]
                if value < min_ideal:
                    recommendations.append(f"Increase {param.replace('_', ' ')} to reach optimal range")
                elif value > max_ideal:
                    recommendations.append(f"Decrease {param.replace('_', ' ')} to reach optimal range")
        return recommendations