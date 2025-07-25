# app/api/loans.py
"""
Loan management API endpoints for Talazo AgriFinance Platform.
"""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from app.core.extensions import db, create_error_response, create_success_response
from app.models import LoanApplication, LoanApplicationSchema

loans_bp = Blueprint('loans', __name__)

# Initialize schemas
loan_application_schema = LoanApplicationSchema()
loan_applications_schema = LoanApplicationSchema(many=True)


@loans_bp.route('/applications', methods=['POST'])
def create_loan_application():
    """Create a new loan application."""
    try:
        # Get request data
        json_data = request.get_json()
        if not json_data:
            return jsonify(create_error_response("No input data provided", 400))

        # Validate and deserialize input
        try:
            loan_data = loan_application_schema.load(json_data)
        except ValidationError as err:
            return jsonify(create_error_response(f"Validation error: {err.messages}", 400))

        # Create new loan application
        new_application = LoanApplication(**loan_data)
        db.session.add(new_application)
        db.session.commit()

        # Return success response
        result = loan_application_schema.dump(new_application)
        return jsonify(create_success_response(
            result, 
            "Loan application created successfully"
        )), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating loan application: {str(e)}")
        return jsonify(create_error_response("Failed to create loan application", 500))


@loans_bp.route('/applications/<int:application_id>', methods=['GET'])
def get_loan_application(application_id):
    """Get loan application details."""
    try:
        application = LoanApplication.query.get(application_id)
        if not application:
            return jsonify(create_error_response("Loan application not found", 404))

        result = loan_application_schema.dump(application)
        return jsonify(create_success_response(
            result, 
            "Loan application retrieved successfully"
        ))

    except Exception as e:
        current_app.logger.error(f"Error retrieving loan application: {str(e)}")
        return jsonify(create_error_response("Failed to retrieve loan application", 500))


@loans_bp.route('/applications', methods=['GET'])
def get_loan_applications():
    """Get list of loan applications with optional filtering."""
    try:
        # Get query parameters for filtering
        farmer_id = request.args.get('farmer_id', type=int)
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Build query
        query = LoanApplication.query

        if farmer_id:
            query = query.filter_by(farmer_id=farmer_id)
        if status:
            query = query.filter_by(status=status)

        # Apply pagination
        applications = query.offset(offset).limit(limit).all()
        total_count = query.count()

        # Serialize data
        result = loan_applications_schema.dump(applications)

        return jsonify(create_success_response({
            'applications': result,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'count': len(applications)
            },
            'filters_applied': {
                'farmer_id': farmer_id,
                'status': status
            }
        }, "Loan applications retrieved successfully"))

    except Exception as e:
        current_app.logger.error(f"Error retrieving loan applications: {str(e)}")
        return jsonify(create_error_response("Failed to retrieve loan applications", 500))


@loans_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
def update_loan_status(application_id):
    """Update loan application status."""
    try:
        application = LoanApplication.query.get(application_id)
        if not application:
            return jsonify(create_error_response("Loan application not found", 404))

        json_data = request.get_json()
        if not json_data or 'status' not in json_data:
            return jsonify(create_error_response("Status is required", 400))

        # Update status
        application.status = json_data['status']
        if 'approval_notes' in json_data:
            application.approval_notes = json_data['approval_notes']
        
        db.session.commit()

        result = loan_application_schema.dump(application)
        return jsonify(create_success_response(
            result, 
            "Loan application status updated successfully"
        ))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating loan application: {str(e)}")
        return jsonify(create_error_response("Failed to update loan application", 500))
