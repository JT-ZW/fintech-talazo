# auth.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from .models import db, User, UserRole
from datetime import datetime, timedelta
import os

auth = Blueprint('auth', __name__)

# Initialize JWT
jwt = JWTManager()

@auth.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    try:
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    """Authenticate user and issue JWT token"""
    data = request.json
    
    # Validate required fields
    if not all(field in data for field in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Find user by username
    user = User.query.filter_by(username=data['username']).first()
    
    # Verify user exists and password is correct
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'email': user.email,
            'role': user.role.value
        }
    )
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value
        }
    }), 200

@auth.route('/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    """Get current user's information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Build response based on user role
    response = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role.value,
        'last_login': user.last_login.isoformat() if user.last_login else None
    }
    
    # Add role-specific information
    if user.role == UserRole.FARMER and user.farmer_profile:
        response['farmer_profile'] = {
            'id': user.farmer_profile.id,
            'full_name': user.farmer_profile.full_name,
            'total_land_area': user.farmer_profile.total_land_area,
            'primary_crop': user.farmer_profile.primary_crop
        }
    elif user.role == UserRole.FINANCIAL_INSTITUTION and user.financial_institution:
        response['institution_profile'] = {
            'id': user.financial_institution.id,
            'name': user.financial_institution.name,
            'institution_type': user.financial_institution.institution_type
        }
    
    return jsonify(response), 200