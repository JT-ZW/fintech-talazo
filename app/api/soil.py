# app/api/soil.py
"""
Soil sample management API endpoints for Talazo AgriFinance Platform.
"""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.extensions import db, create_error_response, create_success_response
from app.models import SoilSample, SoilSampleSchema, Farmer

soil_bp = Blueprint('soil', __name__)

# Initialize schemas
soil_sample_schema = SoilSampleSchema()
soil_samples_schema = SoilSampleSchema(many=True)


@soil_bp.route('/samples', methods=['POST'])
def create_soil_sample():
    """
    Create a new soil sample record.
    
    Request Body:
        JSON object with soil sample data
    
    Returns:
        JSON response with created soil sample
    """
    try:
        # Validate request data
        sample_data = soil_sample_schema.load(request.json)
        
        # Validate farmer exists
        farmer = Farmer.query.get(sample_data.get('farmer_id'))
        if not farmer:
            return jsonify(create_error_response("Farmer not found", 404))
        
        # Create new soil sample
        soil_sample = SoilSample(**sample_data)
        
        # Calculate initial soil health score
        soil_sample.financial_index_score = soil_sample.calculate_soil_health_score()
        
        db.session.add(soil_sample)
        db.session.commit()
        
        current_app.logger.info(f"Created soil sample for farmer {soil_sample.farmer_id}")
        
        return jsonify(create_success_response(
            soil_sample_schema.dump(soil_sample),
            "Soil sample created successfully"
        )), 201
        
    except ValidationError as e:
        return jsonify(create_error_response(f"Validation error: {e.messages}", 400))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating soil sample: {str(e)}")
        return jsonify(create_error_response("Failed to create soil sample", 500))


@soil_bp.route('/samples/<int:sample_id>', methods=['GET'])
def get_soil_sample(sample_id):
    """
    Get a specific soil sample.
    
    Args:
        sample_id (int): Soil sample ID
    
    Returns:
        JSON response with soil sample data
    """
    try:
        sample = SoilSample.query.get_or_404(sample_id)
        return jsonify(create_success_response(soil_sample_schema.dump(sample)))
        
    except Exception as e:
        current_app.logger.error(f"Error fetching soil sample {sample_id}: {str(e)}")
        return jsonify(create_error_response("Failed to fetch soil sample", 500))


@soil_bp.route('/samples', methods=['GET'])
def get_soil_samples():
    """
    Get list of soil samples with optional filtering.
    
    Query Parameters:
        farmer_id (int): Filter by farmer ID
        status (str): Filter by sample status
        limit (int): Limit results (default: 20)
    
    Returns:
        JSON response with soil samples list
    """
    try:
        # Parse query parameters
        farmer_id = request.args.get('farmer_id', type=int)
        status = request.args.get('status')
        limit = min(request.args.get('limit', 20, type=int), 100)
        
        # Build query
        query = SoilSample.query
        
        if farmer_id:
            query = query.filter(SoilSample.farmer_id == farmer_id)
        
        if status:
            query = query.filter(SoilSample.status == status)
        
        # Execute query
        samples = query.order_by(SoilSample.collection_date.desc()).limit(limit).all()
        
        return jsonify(create_success_response({
            'soil_samples': soil_samples_schema.dump(samples),
            'total_count': len(samples),
            'filters_applied': {
                'farmer_id': farmer_id,
                'status': status
            }
        }))
        
    except Exception as e:
        current_app.logger.error(f"Error fetching soil samples: {str(e)}")
        return jsonify(create_error_response("Failed to fetch soil samples", 500))


@soil_bp.route('/samples/<int:sample_id>/analyze', methods=['POST'])
def analyze_soil_sample(sample_id):
    """
    Trigger analysis of a soil sample.
    
    Args:
        sample_id (int): Soil sample ID
    
    Returns:
        JSON response with analysis results
    """
    try:
        sample = SoilSample.query.get_or_404(sample_id)
        
        # Recalculate soil health score
        health_score = sample.calculate_soil_health_score()
        sample.financial_index_score = health_score
        
        # Update status to analyzed
        from app.models.soil_sample import SoilSampleStatus
        sample.status = SoilSampleStatus.ANALYZED
        
        db.session.commit()
        
        return jsonify(create_success_response({
            'sample_id': sample_id,
            'soil_health_score': health_score,
            'parameter_scores': sample.get_parameter_scores(),
            'status': sample.status.value
        }, "Soil sample analyzed successfully"))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error analyzing soil sample {sample_id}: {str(e)}")
        return jsonify(create_error_response("Failed to analyze soil sample", 500))
