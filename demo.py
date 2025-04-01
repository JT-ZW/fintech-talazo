# demo.py - A minimal Flask app for the demo
from flask import Flask, render_template, jsonify, send_from_directory
import random
import datetime
import math
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/demo-data')
def get_demo_data():
    """Generate random demo data"""
    # Generate random soil health between 30-90
    health_score = random.randint(30, 90)
    
    # Determine risk level based on health score
    if health_score >= 80:
        risk_level = "Low Risk"
    elif health_score >= 60:
        risk_level = "Medium-Low Risk"
    elif health_score >= 40:
        risk_level = "Medium Risk"
    elif health_score >= 20:
        risk_level = "Medium-High Risk"
    else:
        risk_level = "High Risk"
    
    # Generate random soil parameters with realistic values
    soil_data = {
        'ph_level': round(random.uniform(5.5, 7.5), 1),
        'nitrogen_level': round(random.uniform(15, 45), 1),
        'phosphorus_level': round(random.uniform(15, 35), 1),
        'potassium_level': round(random.uniform(150, 250), 1),
        'organic_matter': round(random.uniform(2, 6), 1),
        'cation_exchange_capacity': round(random.uniform(10, 20), 1),
        'moisture_content': round(random.uniform(15, 35), 1)
    }
    
    # Generate parameter scores
    parameter_scores = {}
    for param, value in soil_data.items():
        parameter_scores[param] = round(random.uniform(50, 100), 1)
    
    # Generate random yield prediction
    yield_prediction = {
        'predicted_yield': round(random.uniform(2.5, 5.5), 1),
        'yield_range': {
            'lower': round(random.uniform(2.0, 3.0), 1),
            'upper': round(random.uniform(5.0, 7.0), 1)
        },
        'confidence': random.randint(70, 95),
        'unit': 'tons per hectare'
    }
    
    # Generate crop recommendations
    crops = ["Maize", "Groundnuts", "Sorghum", "Cotton", "Soybeans", "Sweet Potatoes"]
    random.shuffle(crops)
    recommended_crops = crops[:3]  # Take first 3 crops
    
    # Generate recommendations
    recommendations = [
        {
            'title': 'Increase Nitrogen Levels',
            'action': f'Apply nitrogen fertilizer at {random.randint(100, 150)} kg/ha',
            'reason': 'Soil nitrogen is below optimal range',
            'cost_estimate': 'Medium',
            'timeframe': '2-4 weeks',
            'local_context': 'Split application recommended during the growing season'
        },
        {
            'title': 'Improve Soil pH',
            'action': 'Apply agricultural lime at 2-3 tons per hectare',
            'reason': 'Soil is moderately acidic',
            'cost_estimate': 'Medium',
            'timeframe': '3-6 months',
            'local_context': 'Lime is available from agricultural suppliers in most regions'
        },
        {
            'title': 'Increase Organic Matter',
            'action': 'Apply compost or manure at 5-10 tons per hectare',
            'reason': 'Low organic matter reduces nutrient retention',
            'cost_estimate': 'Low',
            'timeframe': '6-12 months',
            'local_context': 'Use locally available resources like cattle manure'
        }
    ]
    
    # Generate time series data for charts
    timestamps = []
    trend_points = []
    trend_scores = []
    
    now = datetime.datetime.now()
    for i in range(48):  # 24 hours of data at 30 minute intervals
        time_point = now - datetime.timedelta(minutes=30 * i)
        timestamps.append(time_point.isoformat())
        
        # Generate data point with some randomness but keeping the trend coherent
        point = {}
        for param, base_value in soil_data.items():
            # Add some random variation
            variation = (math.sin(i * 0.1) * 0.1 + random.uniform(-0.05, 0.05)) * base_value
            point[param] = round(base_value + variation, 1)
        
        point['timestamp'] = timestamps[-1]
        trend_points.append(point)
        
        # Generate health score with some correlation to the parameters
        trend_score = health_score + random.randint(-5, 5)
        trend_scores.append(trend_score)
    
    # Return complete demo data
    return jsonify({
        'soil_health': {
            'health_score': health_score,
            'risk_level': risk_level,
            'soil_data': soil_data,
            'parameter_scores': parameter_scores
        },
        'financial': {
            'index_score': health_score,
            'risk_level': risk_level,
            'premium_estimate': round(100 + (100 - health_score) * 1.5, 2),
            'loan_eligibility': health_score >= 40
        },
        'trend_data': {
            'points': trend_points,
            'scores': trend_scores
        },
        'yield_prediction': yield_prediction,
        'recommended_crops': recommended_crops,
        'recommendations': recommendations,
        'metadata': {
            'farmer_id': 1,
            'farmer_name': 'Demo Farmer',
            'primary_crop': 'Maize',
            'generated_at': datetime.datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    app.run(debug=True)