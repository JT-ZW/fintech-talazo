# app/api/scoring.py
"""
Farm viability scoring API endpoints for Talazo AgriFinance Platform.
"""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError

from app.core.extensions import db, create_error_response, create_success_response, limiter
from app.models import Farmer, SoilSample
from app.services import FarmViabilityScorer

scoring_bp = Blueprint('scoring', __name__)

# Initialize scorer
scorer = FarmViabilityScorer()


@scoring_bp.route('/calculate', methods=['POST'])
@limiter.limit("10 per minute")
def calculate_farm_score():
    """
    Calculate comprehensive farm viability score.
    
    Request Body:
        {
            "farmer_id": int,
            "additional_data": {
                "has_irrigation": bool,
                "water_sources": ["borehole", "well", "river"],
                "climate_adaptations": ["drought_resistant_crops", "conservation_agriculture"],
                "transport_access": ["good_roads", "public_transport"],
                "has_storage_facilities": bool,
                "has_processing_access": bool,
                "rainfall_reliability": float (0-1)
            }
        }
    
    Returns:
        JSON response with comprehensive scoring results
    """
    try:
        data = request.get_json()
        
        if not data or 'farmer_id' not in data:
            return jsonify(create_error_response("farmer_id is required", 400))
        
        farmer_id = data['farmer_id']
        additional_data = data.get('additional_data', {})
        
        # Validate farmer exists
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return jsonify(create_error_response(f"Farmer with ID {farmer_id} not found", 404))
        
        if not farmer.is_active:
            return jsonify(create_error_response("Farmer account is inactive", 400))
        
        # Check if farmer has soil data
        latest_sample = farmer.get_latest_soil_sample()
        if not latest_sample:
            return jsonify(create_error_response(
                "No soil data available for this farmer. Please submit soil sample first.", 400
            ))
        
        # Calculate comprehensive score
        scoring_result = scorer.calculate_comprehensive_score(farmer_id, additional_data)
        
        # Update farmer's latest soil sample with the new score
        latest_sample.financial_index_score = scoring_result['overall_score']
        latest_sample.risk_level = scoring_result['risk_level']
        db.session.commit()
        
        current_app.logger.info(f"Calculated score for farmer {farmer_id}: {scoring_result['overall_score']}")
        
        return jsonify(create_success_response(scoring_result, "Farm score calculated successfully"))
        
    except ValueError as e:
        return jsonify(create_error_response(str(e), 400))
    
    except Exception as e:
        current_app.logger.error(f"Error calculating farm score: {str(e)}")
        return jsonify(create_error_response("Failed to calculate farm score", 500))


@scoring_bp.route('/loan-eligibility', methods=['POST'])
@limiter.limit("5 per minute")
def calculate_loan_eligibility():
    """
    Calculate loan eligibility based on farm viability score.
    
    Request Body:
        {
            "farmer_id": int
        }
    
    Returns:
        JSON response with loan eligibility assessment
    """
    try:
        data = request.get_json()
        
        if not data or 'farmer_id' not in data:
            return jsonify(create_error_response("farmer_id is required", 400))
        
        farmer_id = data['farmer_id']
        
        # Validate farmer exists
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return jsonify(create_error_response(f"Farmer with ID {farmer_id} not found", 404))
        
        # Calculate loan eligibility
        eligibility_result = scorer.calculate_loan_eligibility(farmer_id)
        
        if 'error' in eligibility_result:
            return jsonify(create_error_response(eligibility_result['error'], 400))
        
        current_app.logger.info(f"Calculated loan eligibility for farmer {farmer_id}: {eligibility_result['eligible']}")
        
        return jsonify(create_success_response(eligibility_result, "Loan eligibility calculated successfully"))
        
    except Exception as e:
        current_app.logger.error(f"Error calculating loan eligibility: {str(e)}")
        return jsonify(create_error_response("Failed to calculate loan eligibility", 500))


@scoring_bp.route('/what-if-analysis', methods=['POST'])
@limiter.limit("5 per minute")
def what_if_analysis():
    """
    Perform what-if analysis showing score changes with improvements.
    
    Request Body:
        {
            "farmer_id": int,
            "improvements": {
                "soil_ph": float,
                "nitrogen_increase": float,
                "phosphorus_increase": float,
                "potassium_increase": float,
                "organic_matter_increase": float,
                "add_irrigation": bool,
                "add_storage": bool
            }
        }
    
    Returns:
        JSON response with current vs projected scores
    """
    try:
        data = request.get_json()
        
        if not data or 'farmer_id' not in data:
            return jsonify(create_error_response("farmer_id is required", 400))
        
        farmer_id = data['farmer_id']
        improvements = data.get('improvements', {})
        
        # Validate farmer exists
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return jsonify(create_error_response(f"Farmer with ID {farmer_id} not found", 404))
        
        # Get current score
        current_result = scorer.calculate_comprehensive_score(farmer_id)
        current_score = current_result['overall_score']
        
        # Calculate projected improvements
        improvement_impacts = []
        total_improvement = 0
        
        # Soil parameter improvements
        if improvements.get('soil_ph'):
            impact = _calculate_ph_improvement_impact(
                farmer.get_latest_soil_sample().ph_level,
                improvements['soil_ph']
            )
            improvement_impacts.append({
                'improvement': 'Soil pH adjustment',
                'current_value': farmer.get_latest_soil_sample().ph_level,
                'target_value': improvements['soil_ph'],
                'score_impact': impact,
                'cost_estimate': 150,  # USD per hectare
                'implementation_time': '3-6 months'
            })
            total_improvement += impact
        
        if improvements.get('nitrogen_increase'):
            impact = improvements['nitrogen_increase'] * 0.3  # Rough estimate
            improvement_impacts.append({
                'improvement': 'Nitrogen fertilizer application',
                'increase': improvements['nitrogen_increase'],
                'score_impact': impact,
                'cost_estimate': 200,
                'implementation_time': '1-2 months'
            })
            total_improvement += impact
        
        if improvements.get('organic_matter_increase'):
            impact = improvements['organic_matter_increase'] * 2.0  # Higher impact
            improvement_impacts.append({
                'improvement': 'Organic matter enhancement',
                'increase': improvements['organic_matter_increase'],
                'score_impact': impact,
                'cost_estimate': 100,
                'implementation_time': '6-12 months'
            })
            total_improvement += impact
        
        # Infrastructure improvements
        if improvements.get('add_irrigation'):
            impact = 8.0  # Fixed impact for irrigation
            improvement_impacts.append({
                'improvement': 'Irrigation system installation',
                'score_impact': impact,
                'cost_estimate': 2000,
                'implementation_time': '2-4 months'
            })
            total_improvement += impact
        
        if improvements.get('add_storage'):
            impact = 3.0  # Fixed impact for storage
            improvement_impacts.append({
                'improvement': 'Storage facility construction',
                'score_impact': impact,
                'cost_estimate': 1500,
                'implementation_time': '1-3 months'
            })
            total_improvement += impact
        
        # Calculate projected score (capped at 100)
        projected_score = min(100, current_score + total_improvement)
        
        # Calculate new loan eligibility
        projected_eligibility = _calculate_projected_loan_eligibility(projected_score)
        
        return jsonify(create_success_response({
            'farmer_id': farmer_id,
            'current_score': current_score,
            'projected_score': projected_score,
            'total_improvement': total_improvement,
            'current_loan_eligibility': scorer.calculate_loan_eligibility(farmer_id),
            'projected_loan_eligibility': projected_eligibility,
            'improvement_breakdown': improvement_impacts,
            'total_estimated_cost': sum(imp.get('cost_estimate', 0) for imp in improvement_impacts),
            'roi_analysis': {
                'loan_amount_increase': projected_eligibility.get('max_loan_amount', 0) - 
                                      scorer.calculate_loan_eligibility(farmer_id).get('max_loan_amount', 0),
                'payback_period_months': 12  # Simplified calculation
            }
        }))
        
    except Exception as e:
        current_app.logger.error(f"Error performing what-if analysis: {str(e)}")
        return jsonify(create_error_response("Failed to perform what-if analysis", 500))


@scoring_bp.route('/batch-calculate', methods=['POST'])
@limiter.limit("2 per minute")
def batch_calculate_scores():
    """
    Calculate scores for multiple farmers in batch.
    
    Request Body:
        {
            "farmer_ids": [int, int, ...],
            "additional_data": {...}  # Applied to all farmers
        }
    
    Returns:
        JSON response with batch scoring results
    """
    try:
        data = request.get_json()
        
        if not data or 'farmer_ids' not in data:
            return jsonify(create_error_response("farmer_ids list is required", 400))
        
        farmer_ids = data['farmer_ids']
        additional_data = data.get('additional_data', {})
        
        if len(farmer_ids) > 50:  # Limit batch size
            return jsonify(create_error_response("Maximum 50 farmers per batch", 400))
        
        results = []
        errors = []
        
        for farmer_id in farmer_ids:
            try:
                # Validate farmer exists
                farmer = Farmer.query.get(farmer_id)
                if not farmer:
                    errors.append(f"Farmer {farmer_id} not found")
                    continue
                
                # Calculate score
                scoring_result = scorer.calculate_comprehensive_score(farmer_id, additional_data)
                
                # Update database
                latest_sample = farmer.get_latest_soil_sample()
                if latest_sample:
                    latest_sample.financial_index_score = scoring_result['overall_score']
                    latest_sample.risk_level = scoring_result['risk_level']
                
                results.append({
                    'farmer_id': farmer_id,
                    'farmer_name': farmer.full_name,
                    'score': scoring_result['overall_score'],
                    'risk_level': scoring_result['risk_level'],
                    'success': True
                })
                
            except Exception as e:
                errors.append(f"Error processing farmer {farmer_id}: {str(e)}")
                results.append({
                    'farmer_id': farmer_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Commit all successful updates
        db.session.commit()
        
        current_app.logger.info(f"Batch calculated scores for {len(results)} farmers")
        
        return jsonify(create_success_response({
            'total_processed': len(farmer_ids),
            'successful': len([r for r in results if r.get('success')]),
            'failed': len(errors),
            'results': results,
            'errors': errors
        }))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in batch score calculation: {str(e)}")
        return jsonify(create_error_response("Failed to process batch scoring", 500))


@scoring_bp.route('/parameters/weights', methods=['GET'])
def get_scoring_weights():
    """
    Get current scoring weights and parameters.
    
    Returns:
        JSON response with scoring configuration
    """
    return jsonify(create_success_response({
        'weights': scorer.weights,
        'optimal_ranges': scorer.optimal_ranges,
        'crop_requirements': scorer.crop_requirements,
        'risk_thresholds': scorer.risk_thresholds
    }))


def _calculate_ph_improvement_impact(current_ph, target_ph):
    """Calculate score impact of pH improvement."""
    current_score = scorer._normalize_ph_score(current_ph) if hasattr(scorer, '_normalize_ph_score') else 50
    target_score = scorer._normalize_ph_score(target_ph) if hasattr(scorer, '_normalize_ph_score') else 50
    
    # Impact is weighted by soil health weight
    return (target_score - current_score) * scorer.weights['soil_health'] * 0.25  # pH is 25% of soil health


def _calculate_projected_loan_eligibility(projected_score):
    """Calculate loan eligibility for projected score."""
    risk_level = 'LOW' if projected_score >= 80 else 'MEDIUM_LOW' if projected_score >= 65 else 'MEDIUM'
    
    if projected_score >= 80:
        return {
            'eligible': True,
            'max_loan_amount': projected_score * 150,
            'recommended_interest_rate': 8.0,
            'max_term_months': 24
        }
    elif projected_score >= 65:
        return {
            'eligible': True,
            'max_loan_amount': projected_score * 100,
            'recommended_interest_rate': 12.0,
            'max_term_months': 18
        }
    elif projected_score >= 50:
        return {
            'eligible': True,
            'max_loan_amount': projected_score * 75,
            'recommended_interest_rate': 15.0,
            'max_term_months': 12
        }
    else:
        return {
            'eligible': False,
            'max_loan_amount': 0,
            'recommended_interest_rate': None,
            'max_term_months': None
        }
