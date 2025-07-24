# app/api/farmers.py
"""
Farmer management API endpoints for Talazo AgriFinance Platform.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from app.core.extensions import db, create_error_response, create_success_response
from app.models import Farmer, FarmerSchema, SoilSample

farmers_bp = Blueprint('farmers', __name__)

# Initialize schemas
farmer_schema = FarmerSchema()
farmers_schema = FarmerSchema(many=True)


@farmers_bp.route('/', methods=['GET'])
def get_farmers():
    """
    Get list of farmers with optional filtering and pagination.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        district (str): Filter by district
        province (str): Filter by province
        crop (str): Filter by primary crop
        active_only (bool): Show only active farmers (default: True)
        search (str): Search in farmer names
    
    Returns:
        JSON response with farmers list and pagination info
    """
    try:
        # Parse query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        district = request.args.get('district')
        province = request.args.get('province')
        crop = request.args.get('crop')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        search = request.args.get('search')
        
        # Build query
        query = Farmer.query
        
        if active_only:
            query = query.filter(Farmer.is_active == True)
        
        if district:
            query = query.filter(Farmer.district.ilike(f'%{district}%'))
        
        if province:
            query = query.filter(Farmer.province.ilike(f'%{province}%'))
        
        if crop:
            query = query.filter(Farmer.primary_crop.ilike(f'%{crop}%'))
        
        if search:
            query = query.filter(Farmer.full_name.ilike(f'%{search}%'))
        
        # Execute paginated query
        farmers_page = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify(create_success_response({
            'farmers': farmers_schema.dump(farmers_page.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': farmers_page.total,
                'pages': farmers_page.pages,
                'has_next': farmers_page.has_next,
                'has_prev': farmers_page.has_prev
            },
            'filters_applied': {
                'district': district,
                'province': province,
                'crop': crop,
                'active_only': active_only,
                'search': search
            }
        }))
        
    except Exception as e:
        current_app.logger.error(f"Error fetching farmers: {str(e)}")
        return jsonify(create_error_response("Failed to fetch farmers", 500))


@farmers_bp.route('/<int:farmer_id>', methods=['GET'])
def get_farmer(farmer_id):
    """
    Get detailed information for a specific farmer.
    
    Args:
        farmer_id (int): Farmer ID
    
    Returns:
        JSON response with farmer details
    """
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        
        # Get additional farmer statistics
        total_samples = SoilSample.query.filter_by(farmer_id=farmer_id).count()
        latest_sample = farmer.get_latest_soil_sample()
        
        farmer_data = farmer_schema.dump(farmer)
        farmer_data['statistics'] = {
            'total_soil_samples': total_samples,
            'latest_sample_date': latest_sample.collection_date.isoformat() if latest_sample else None,
            'current_credit_score': farmer.get_current_credit_score(),
            'risk_level': farmer.get_risk_level(),
            'loan_eligibility': farmer.get_loan_eligibility()
        }
        
        return jsonify(create_success_response(farmer_data))
        
    except Exception as e:
        current_app.logger.error(f"Error fetching farmer {farmer_id}: {str(e)}")
        return jsonify(create_error_response("Failed to fetch farmer details", 500))


@farmers_bp.route('/', methods=['POST'])
def create_farmer():
    """
    Create a new farmer record.
    
    Request Body:
        JSON object with farmer information
    
    Returns:
        JSON response with created farmer data
    """
    try:
        # Validate request data
        farmer_data = farmer_schema.load(request.json)
        
        # Create new farmer
        farmer = Farmer(**farmer_data)
        
        # Generate unique national_id if not provided
        if not farmer.national_id:
            import uuid
            farmer.national_id = f"TMP_{uuid.uuid4().hex[:8].upper()}"
        
        db.session.add(farmer)
        db.session.commit()
        
        current_app.logger.info(f"Created new farmer: {farmer.full_name} (ID: {farmer.id})")
        
        return jsonify(create_success_response(
            farmer_schema.dump(farmer),
            "Farmer created successfully"
        )), 201
        
    except ValidationError as e:
        return jsonify(create_error_response(f"Validation error: {e.messages}", 400))
    
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Database integrity error creating farmer: {str(e)}")
        return jsonify(create_error_response("Farmer with this national ID already exists", 409))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating farmer: {str(e)}")
        return jsonify(create_error_response("Failed to create farmer", 500))


@farmers_bp.route('/<int:farmer_id>', methods=['PUT'])
def update_farmer(farmer_id):
    """
    Update an existing farmer record.
    
    Args:
        farmer_id (int): Farmer ID
    
    Request Body:
        JSON object with farmer information to update
    
    Returns:
        JSON response with updated farmer data
    """
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        
        # Validate and load update data (partial=True allows partial updates)
        update_data = farmer_schema.load(request.json, partial=True)
        
        # Update farmer attributes
        for key, value in update_data.items():
            if hasattr(farmer, key):
                setattr(farmer, key, value)
        
        db.session.commit()
        
        current_app.logger.info(f"Updated farmer: {farmer.full_name} (ID: {farmer.id})")
        
        return jsonify(create_success_response(
            farmer_schema.dump(farmer),
            "Farmer updated successfully"
        ))
        
    except ValidationError as e:
        return jsonify(create_error_response(f"Validation error: {e.messages}", 400))
    
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Database integrity error updating farmer: {str(e)}")
        return jsonify(create_error_response("National ID conflict or constraint violation", 409))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating farmer {farmer_id}: {str(e)}")
        return jsonify(create_error_response("Failed to update farmer", 500))


@farmers_bp.route('/<int:farmer_id>', methods=['DELETE'])
def delete_farmer(farmer_id):
    """
    Delete a farmer record (soft delete by setting is_active=False).
    
    Args:
        farmer_id (int): Farmer ID
    
    Returns:
        JSON response confirming deletion
    """
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        
        # Soft delete - set is_active to False instead of deleting
        farmer.is_active = False
        db.session.commit()
        
        current_app.logger.info(f"Soft deleted farmer: {farmer.full_name} (ID: {farmer.id})")
        
        return jsonify(create_success_response(
            message="Farmer deactivated successfully"
        ))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting farmer {farmer_id}: {str(e)}")
        return jsonify(create_error_response("Failed to delete farmer", 500))


@farmers_bp.route('/<int:farmer_id>/soil-samples', methods=['GET'])
def get_farmer_soil_samples(farmer_id):
    """
    Get all soil samples for a specific farmer.
    
    Args:
        farmer_id (int): Farmer ID
    
    Query Parameters:
        limit (int): Limit number of results (default: 10)
        
    Returns:
        JSON response with farmer's soil samples
    """
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        limit = request.args.get('limit', 10, type=int)
        
        samples = SoilSample.query.filter_by(farmer_id=farmer_id)\
                                 .order_by(SoilSample.collection_date.desc())\
                                 .limit(limit).all()
        
        from app.models import SoilSampleSchema
        sample_schema = SoilSampleSchema(many=True)
        
        return jsonify(create_success_response({
            'farmer_id': farmer_id,
            'farmer_name': farmer.full_name,
            'soil_samples': sample_schema.dump(samples),
            'total_samples': len(samples)
        }))
        
    except Exception as e:
        current_app.logger.error(f"Error fetching soil samples for farmer {farmer_id}: {str(e)}")
        return jsonify(create_error_response("Failed to fetch soil samples", 500))


@farmers_bp.route('/<int:farmer_id>/credit-history', methods=['GET'])
def get_farmer_credit_history(farmer_id):
    """
    Get credit history for a specific farmer.
    
    Args:
        farmer_id (int): Farmer ID
        
    Returns:
        JSON response with farmer's credit history
    """
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        
        from app.models import CreditHistory, CreditHistorySchema
        credit_history = CreditHistory.query.filter_by(farmer_id=farmer_id)\
                                           .order_by(CreditHistory.loan_date.desc())\
                                           .all()
        
        history_schema = CreditHistorySchema(many=True)
        
        # Calculate summary statistics
        if credit_history:
            total_loans = len(credit_history)
            total_borrowed = sum(ch.loan_amount for ch in credit_history)
            total_paid = sum(ch.amount_paid or 0 for ch in credit_history)
            avg_risk_score = sum(ch.calculate_risk_score() for ch in credit_history) / total_loans
            good_standing_count = sum(1 for ch in credit_history if ch.is_good_standing())
        else:
            total_loans = total_borrowed = total_paid = avg_risk_score = good_standing_count = 0
        
        return jsonify(create_success_response({
            'farmer_id': farmer_id,
            'farmer_name': farmer.full_name,
            'credit_history': history_schema.dump(credit_history),
            'summary': {
                'total_loans': total_loans,
                'total_amount_borrowed': total_borrowed,
                'total_amount_paid': total_paid,
                'average_risk_score': round(avg_risk_score, 2),
                'loans_in_good_standing': good_standing_count,
                'good_standing_percentage': round((good_standing_count / total_loans * 100) if total_loans > 0 else 0, 2)
            }
        }))
        
    except Exception as e:
        current_app.logger.error(f"Error fetching credit history for farmer {farmer_id}: {str(e)}")
        return jsonify(create_error_response("Failed to fetch credit history", 500))


@farmers_bp.route('/statistics', methods=['GET'])
def get_farmers_statistics():
    """
    Get aggregate statistics about farmers in the system.
    
    Returns:
        JSON response with farmer statistics
    """
    try:
        # Basic counts
        total_farmers = Farmer.query.filter_by(is_active=True).count()
        total_verified = Farmer.query.filter_by(is_active=True, verification_status='verified').count()
        
        # Geographic distribution
        province_distribution = db.session.query(
            Farmer.province, 
            db.func.count(Farmer.id)
        ).filter(
            Farmer.is_active == True,
            Farmer.province.isnot(None)
        ).group_by(Farmer.province).all()
        
        # Crop distribution
        crop_distribution = db.session.query(
            Farmer.primary_crop,
            db.func.count(Farmer.id)
        ).filter(
            Farmer.is_active == True,
            Farmer.primary_crop.isnot(None)
        ).group_by(Farmer.primary_crop).all()
        
        # Experience distribution
        experience_stats = db.session.query(
            db.func.avg(Farmer.farming_experience_years),
            db.func.min(Farmer.farming_experience_years),
            db.func.max(Farmer.farming_experience_years)
        ).filter(
            Farmer.is_active == True,
            Farmer.farming_experience_years.isnot(None)
        ).first()
        
        # Land size statistics
        land_stats = db.session.query(
            db.func.avg(Farmer.total_land_area),
            db.func.sum(Farmer.total_land_area),
            db.func.min(Farmer.total_land_area),
            db.func.max(Farmer.total_land_area)
        ).filter(
            Farmer.is_active == True,
            Farmer.total_land_area.isnot(None)
        ).first()
        
        return jsonify(create_success_response({
            'totals': {
                'total_farmers': total_farmers,
                'verified_farmers': total_verified,
                'verification_rate': round((total_verified / total_farmers * 100) if total_farmers > 0 else 0, 2)
            },
            'geographic_distribution': {
                province: count for province, count in province_distribution
            },
            'crop_distribution': {
                crop: count for crop, count in crop_distribution
            },
            'experience_statistics': {
                'average_years': round(experience_stats[0] or 0, 2),
                'min_years': experience_stats[1] or 0,
                'max_years': experience_stats[2] or 0
            },
            'land_statistics': {
                'average_hectares': round(land_stats[0] or 0, 2),
                'total_hectares': round(land_stats[1] or 0, 2),
                'min_hectares': land_stats[2] or 0,
                'max_hectares': land_stats[3] or 0
            }
        }))
        
    except Exception as e:
        current_app.logger.error(f"Error generating farmer statistics: {str(e)}")
        return jsonify(create_error_response("Failed to generate statistics", 500))
