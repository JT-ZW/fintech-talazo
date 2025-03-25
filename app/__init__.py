from flask import Flask, render_template, request, jsonify, abort
from flask_migrate import Migrate
from models import db
from datetime import datetime
import os
from app.soil_analyzer import SoilHealthIndex
        
def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fintech.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/calculate-index', methods=['POST'])
    def calculate_index():
        try:
            data = request.json
            
            # Validate required fields
            required_fields = ['ph_level', 'nitrogen_level', 'phosphorus_level', 'potassium_level']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required soil parameters'}), 400

            # Extract soil data
            soil_data = {
                'ph_level': float(data.get('ph_level')),
                'nitrogen_level': float(data.get('nitrogen_level')),
                'phosphorus_level': float(data.get('phosphorus_level')),
                'potassium_level': float(data.get('potassium_level')),
                'organic_matter': float(data.get('organic_matter', 0)),
                'cation_exchange_capacity': float(data.get('cation_exchange_capacity', 0)),
                'moisture_content': float(data.get('moisture_content', 0))
            }
            
            # Calculate financial index
            analyzer = SoilHealthIndex()
            score = analyzer.calculate_score(soil_data)
            risk_level = analyzer.determine_risk_level(score)
            premium = analyzer.calculate_premium(score)
            
            return jsonify({
                'credit_score': round(score, 2),
                'risk_level': risk_level,
                'recommended_premium': round(premium, 2),
                'recommendations': analyzer.get_recommendations(soil_data)
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
