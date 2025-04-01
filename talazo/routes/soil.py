# talazo/routes/soil.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

from talazo.utils.errors import ValidationError, NotFoundError
from talazo.utils.validation import validate_json_request, validate_soil_data
from talazo.models.base import db
from talazo.models.soil import SoilSample, SoilSampleStatus
from talazo.models.user import Farmer
from talazo.ml.ai_recommendations import AIRecommendationSystem

soil_bp = Blueprint('soil', __name__)
logger = logging.getLogger(__name__)

# Initialize AI recommendations system
ai_recommendations = AIRecommendationSystem()

@soil_bp.route('/analyze', methods=['POST'])
@validate_json_request(required_fields=['soil_data'])
def analyze_soil():
    """
    Analyze soil data and return health score and recommendations
    
    Request:
        JSON with soil_data object containing soil parameters
    
    Returns:
        JSON with soil health analysis
    """
    try:
        # Extract and validate soil data
        request_data = request.json
        soil_data = validate_soil_data(request_data['soil_data'])
        
        # Optional parameters
        region = request_data.get('region')
        crop = request_data.get('crop')
        
        # Get soil analyzer
        soil_analyzer = current_app.soil_analyzer
        
        # Calculate soil health score
        score, parameter_scores = soil_analyzer.calculate_score(soil_data, region)
        
        # Determine risk level
        risk_level = soil_analyzer.determine_risk_level(score)
        
        # Calculate premium
        premium = soil_analyzer.calculate_premium(score)
        
        # Get recommendations
        recommendations = soil_analyzer.get_recommendations(soil_data, region, crop)
        
        # Get recommended crops
        suitable_crops = soil_analyzer.recommend_suitable_crops(soil_data, region)
        
        # Return analysis results
        return jsonify({
            'status': 'success',
            'soil_health': {
                'score': round(score, 2),
                'parameter_scores': {k: round(v * 100, 2) for k, v in parameter_scores.items()},
                'risk_level': risk_level
            },
            'financial': {
                'premium_estimate': round(premium, 2),
                'loan_eligibility': score >= 40
            },
            'recommendations': recommendations,
            'suitable_crops': suitable_crops,
            'metadata': {
                'analyzed_at': datetime.utcnow().isoformat(),
                'region': region,
                'current_crop': crop
            }
        })
        
    except ValidationError as e:
        # Re-raise validation error for standard error handling
        raise e
    except Exception as e:
        logger.exception(f"Error in soil analysis: {str(e)}")
        raise ValidationError(f"Error analyzing soil data: {str(e)}")

@soil_bp.route('/predict-yield', methods=['POST'])
@validate_json_request(required_fields=['soil_data'])
def predict_yield():
    """
    Predict crop yield based on soil data
    
    Request:
        JSON with soil_data object and optional crop
    
    Returns:
        JSON with yield predictions
    """
    try:
        # Extract and validate soil data
        request_data = request.json
        soil_data = validate_soil_data(request_data['soil_data'])
        
        # Get crop if specified
        crop = request_data.get('crop', 'maize')  # Default to maize
        
        # Get yield predictor
        yield_predictor = current_app.yield_predictor
        
        # Get yield prediction
        prediction = yield_predictor.predict_yield(soil_data)
        
        # Return prediction results
        return jsonify({
            'status': 'success',
            'yield_prediction': prediction,
            'crop': crop,
            'metadata': {
                'predicted_at': datetime.utcnow().isoformat()
            }
        })
        
    except ValidationError as e:
        # Re-raise validation error for standard error handling
        raise e
    except Exception as e:
        logger.exception(f"Error in yield prediction: {str(e)}")
        raise ValidationError(f"Error predicting crop yield: {str(e)}")

@soil_bp.route('/ai-recommendations', methods=['POST'])
@validate_json_request(required_fields=['soil_data'])
def get_ai_recommendations():
    """
    Get AI-driven recommendations based on soil data
    
    Request:
        JSON with soil_data object and optional farmer_info, region, crop
    
    Returns:
        JSON with AI-generated recommendations
    """
    try:
        # Extract and validate soil data
        request_data = request.json
        soil_data = validate_soil_data(request_data['soil_data'])
        
        # Optional parameters
        farmer_info = request_data.get('farmer_info')
        region = request_data.get('region')
        crop = request_data.get('crop')
        
        # Get AI recommendations
        recommendations = ai_recommendations.generate_recommendations(
            soil_data=soil_data,
            farmer_info=farmer_info,
            region=region,
            crop=crop
        )
        
        # Add timestamp and request context
        recommendations['metadata']['request_context'] = {
            'region': region,
            'crop': crop
        }
        
        return jsonify(recommendations)
        
    except ValidationError as e:
        # Re-raise validation error for standard error handling
        raise e
    except Exception as e:
        logger.exception(f"Error getting AI recommendations: {str(e)}")
        raise ValidationError(f"Error generating AI recommendations: {str(e)}")

@soil_bp.route('/samples', methods=['GET'])
@jwt_required()
def get_soil_samples():
    """
    Get soil samples for the authenticated user
    
    Returns:
        JSON list of soil samples
    """
    try:
        # Get current user
        user_id = get_jwt_identity()
        
        # Get farmer profile
        farmer = Farmer.query.filter_by(user_id=user_id).first()
        if not farmer:
            raise NotFoundError("Farmer profile not found", resource_type="Farmer")
        
        # Query soil samples
        samples = SoilSample.query.filter_by(farmer_id=farmer.id).order_by(
            SoilSample.collection_date.desc()
        ).all()
        
        # Convert to JSON
        samples_data = []
        for sample in samples:
            samples_data.append({
                'id': sample.id,
                'collection_date': sample.collection_date.isoformat(),
                'status': sample.status.value,
                'farm_plot_id': sample.farm_plot_id,
                'farm_plot_name': sample.farm_plot.name if sample.farm_plot else None,
                'soil_data': {
                    'ph_level': sample.ph_level,
                    'nitrogen_level': sample.nitrogen_level,
                    'phosphorus_level': sample.phosphorus_level,
                    'potassium_level': sample.potassium_level,
                    'organic_matter': sample.organic_matter,
                    'cation_exchange_capacity': sample.cation_exchange_capacity,
                    'moisture_content': sample.moisture_content
                },
                'financial_index_score': sample.financial_index_score,
                'risk_level': sample.risk_level.value if sample.risk_level else None
            })
        
        return jsonify({
            'status': 'success',
            'samples': samples_data,
            'total': len(samples_data)
        })
        
    except NotFoundError as e:
        # Re-raise not found error for standard error handling
        raise e
    except Exception as e:
        logger.exception(f"Error retrieving soil samples: {str(e)}")
        raise ValidationError(f"Error retrieving soil samples: {str(e)}")

@soil_bp.route('/samples', methods=['POST'])
@jwt_required()
@validate_json_request(required_fields=['soil_data'])
def create_soil_sample():
    """
    Create a new soil sample for the authenticated user
    
    Request:
        JSON with soil_data object and optional farm_plot_id
    
    Returns:
        JSON with created soil sample details
    """
    try:
        # Get current user
        user_id = get_jwt_identity()
        
        # Get farmer profile
        farmer = Farmer.query.filter_by(user_id=user_id).first()
        if not farmer:
            raise NotFoundError("Farmer profile not found", resource_type="Farmer")
        
        # Extract request data
        request_data = request.json
        soil_data = validate_soil_data(request_data['soil_data'])
        farm_plot_id = request_data.get('farm_plot_id')
        
        # Calculate soil health score
        soil_analyzer = current_app.soil_analyzer
        score, _ = soil_analyzer.calculate_score(soil_data)
        risk_level = soil_analyzer.determine_risk_level(score)
        
        # Create soil sample
        sample = SoilSample(
            farmer_id=farmer.id,
            farm_plot_id=farm_plot_id,
            collection_date=datetime.utcnow(),
            status=SoilSampleStatus.COLLECTED,
            ph_level=soil_data.get('ph_level'),
            nitrogen_level=soil_data.get('nitrogen_level'),
            phosphorus_level=soil_data.get('phosphorus_level'),
            potassium_level=soil_data.get('potassium_level'),
            organic_matter=soil_data.get('organic_matter'),
            cation_exchange_capacity=soil_data.get('cation_exchange_capacity'),
            moisture_content=soil_data.get('moisture_content'),
            financial_index_score=score,
            analyzed_by='system',
            analysis_date=datetime.utcnow()
        )
        
        # Set risk level if available
        if risk_level:
            from talazo.models.soil import RiskLevel
            sample.risk_level = RiskLevel(risk_level.replace(' Risk', ''))
        
        # Save to database
        db.session.add(sample)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Soil sample created successfully',
            'sample_id': sample.id,
            'financial_index_score': round(score, 2),
            'risk_level': risk_level
        }), 201
        
    except NotFoundError as e:
        # Re-raise not found error for standard error handling
        raise e
    except ValidationError as e:
        # Re-raise validation error for standard error handling
        raise e
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error creating soil sample: {str(e)}")
        raise ValidationError(f"Error creating soil sample: {str(e)}")

@soil_bp.route('/dashboard-data', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """
    Get comprehensive dashboard data for visualization
    
    Returns:
        JSON with dashboard data
    """
    try:
        # Get current user
        user_id = get_jwt_identity()
        
        # Get farmer profile
        farmer = Farmer.query.filter_by(user_id=user_id).first()
        if not farmer:
            raise NotFoundError("Farmer profile not found", resource_type="Farmer")
        
        # Get latest soil sample
        latest_sample = SoilSample.query.filter_by(farmer_id=farmer.id).order_by(
            SoilSample.collection_date.desc()
        ).first()
        
        if not latest_sample:
            # If no real sample, use simulated data
            from talazo.sensors import SensorSimulator
            sensor_simulator = SensorSimulator()
            current_reading = sensor_simulator.generate_reading()
            soil_data = {k: v for k, v in current_reading.items() if k != 'timestamp'}
            
            # Calculate soil health score
            soil_analyzer = current_app.soil_analyzer
            score, parameter_scores = soil_analyzer.calculate_score(soil_data)
            risk_level = soil_analyzer.determine_risk_level(score)
            
            soil_health_data = {
                'simulated': True,
                'timestamp': current_reading['timestamp'],
                'soil_data': soil_data,
                'health_score': round(score, 2),
                'risk_level': risk_level,
                'parameter_scores': {k: round(v * 100, 2) for k, v in parameter_scores.items()}
            }
        else:
            # Use real sample data
            soil_data = {
                'ph_level': latest_sample.ph_level,
                'nitrogen_level': latest_sample.nitrogen_level,
                'phosphorus_level': latest_sample.phosphorus_level,
                'potassium_level': latest_sample.potassium_level,
                'organic_matter': latest_sample.organic_matter,
                'cation_exchange_capacity': latest_sample.cation_exchange_capacity,
                'moisture_content': latest_sample.moisture_content
            }
            
            # Calculate scores using current algorithm
            soil_analyzer = current_app.soil_analyzer
            score, parameter_scores = soil_analyzer.calculate_score(soil_data)
            
            soil_health_data = {
                'simulated': False,
                'sample_id': latest_sample.id,
                'timestamp': latest_sample.collection_date.isoformat(),
                'soil_data': soil_data,
                'health_score': round(score, 2),
                'risk_level': soil_analyzer.determine_risk_level(score),
                'parameter_scores': {k: round(v * 100, 2) for k, v in parameter_scores.items()}
            }
        
        # Get yield prediction
        yield_data = current_app.yield_predictor.predict_yield(soil_data)
        
        # Get recommended crops
        recommended_crops = current_app.soil_analyzer.recommend_suitable_crops(soil_data)
        
        # Get recommendations
        recommendations = current_app.soil_analyzer.get_recommendations(soil_data)
        
        return jsonify({
            'status': 'success',
            'soil_health': soil_health_data,
            'financial': {
                'index_score': soil_health_data['health_score'],
                'risk_level': soil_health_data['risk_level'],
                'premium_estimate': round(current_app.soil_analyzer.calculate_premium(score), 2),
                'loan_eligibility': score >= 40
            },
            'yield_prediction': yield_data,
            'recommended_crops': recommended_crops,
            'recommendations': recommendations[:3],  # Top 3 recommendations
            'metadata': {
                'farmer_id': farmer.id,
                'farmer_name': farmer.full_name,
                'primary_crop': farmer.primary_crop,
                'generated_at': datetime.utcnow().isoformat()
            }
        })
        
    except NotFoundError as e:
        # Re-raise not found error for standard error handling
        raise e
    except Exception as e:
        logger.exception(f"Error retrieving dashboard data: {str(e)}")
        raise ValidationError(f"Error retrieving dashboard data: {str(e)}")