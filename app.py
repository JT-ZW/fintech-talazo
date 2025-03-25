from flask import Flask, render_template, request, jsonify
import os

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
        parameter_scores = {}
        
        for param, value in soil_data.items():
            if param in self.weights:
                param_score = self._score_parameter(param, float(value))
                parameter_scores[param] = param_score
                total_score += param_score * self.weights[param]
        
        return total_score * 100, parameter_scores

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
                value = float(value)
                if value < min_ideal:
                    recommendations.append(f"Increase {param.replace('_', ' ')} to reach optimal range")
                elif value > max_ideal:
                    recommendations.append(f"Decrease {param.replace('_', ' ')} to reach optimal range")
        return recommendations

# Create Flask application
# Make sure the app knows where to find static files
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

soil_analyzer = SoilHealthIndex()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate-index', methods=['POST'])
def calculate_index():
    """API endpoint to calculate financial index based on soil data"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['ph_level', 'nitrogen_level', 'phosphorus_level', 'potassium_level']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required soil parameters'}), 400

        # Extract soil data from request
        soil_data = {
            'ph_level': data.get('ph_level'),
            'nitrogen_level': data.get('nitrogen_level'),
            'phosphorus_level': data.get('phosphorus_level'),
            'potassium_level': data.get('potassium_level'),
            'organic_matter': data.get('organic_matter', 0),
            'cation_exchange_capacity': data.get('cation_exchange_capacity', 0),
            'moisture_content': data.get('moisture_content', 0)
        }
        
        # Calculate financial index
        score, parameter_scores = soil_analyzer.calculate_score(soil_data)
        risk_level = soil_analyzer.determine_risk_level(score)
        premium = soil_analyzer.calculate_premium(score)
        
        return jsonify({
            'credit_score': round(score, 2),
            'risk_level': risk_level,
            'recommended_premium': round(premium, 2),
            'parameter_scores': {
                param: round(score, 2)
                for param, score in parameter_scores.items()
            },
            'recommendations': soil_analyzer.get_recommendations(soil_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)