# app/api/auth.py
"""
Authentication API endpoints for Talazo AgriFinance Platform.
"""

from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from marshmallow import ValidationError, Schema, fields, validate
from app.core.extensions import create_error_response, create_success_response

auth_bp = Blueprint('auth', __name__)


class LoginSchema(Schema):
    """Schema for login validation."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6))


class RegisterSchema(Schema):
    """Schema for registration validation."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    organization = fields.Str(missing=None)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        # Get request data
        json_data = request.get_json()
        if not json_data:
            return jsonify(create_error_response("No input data provided", 400))

        # Validate input
        schema = LoginSchema()
        try:
            login_data = schema.load(json_data)
        except ValidationError as err:
            return jsonify(create_error_response(f"Validation error: {err.messages}", 400))

        # For now, implement a simple demo authentication
        # In production, this would check against a user database
        demo_users = {
            'admin': {
                'password_hash': generate_password_hash('admin123'),
                'full_name': 'System Administrator',
                'role': 'admin',
                'organization': 'Talazo AgriFinance'
            },
            'demo': {
                'password_hash': generate_password_hash('demo123'),
                'full_name': 'Demo User',
                'role': 'user',
                'organization': 'Demo Organization'
            }
        }

        username = login_data['username']
        password = login_data['password']

        if username in demo_users and check_password_hash(demo_users[username]['password_hash'], password):
            # Create session
            session['user_id'] = username
            session['user_role'] = demo_users[username]['role']
            session['authenticated'] = True

            return jsonify(create_success_response({
                'user': {
                    'username': username,
                    'full_name': demo_users[username]['full_name'],
                    'role': demo_users[username]['role'],
                    'organization': demo_users[username]['organization']
                },
                'session': {
                    'authenticated': True,
                    'expires_in': '24 hours'
                }
            }, "Login successful"))
        else:
            return jsonify(create_error_response("Invalid username or password", 401))

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify(create_error_response("Authentication failed", 500))


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint."""
    try:
        # Clear session
        session.clear()
        
        return jsonify(create_success_response(
            message="Logout successful"
        ))

    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify(create_error_response("Logout failed", 500))


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        # Get request data
        json_data = request.get_json()
        if not json_data:
            return jsonify(create_error_response("No input data provided", 400))

        # Validate input
        schema = RegisterSchema()
        try:
            register_data = schema.load(json_data)
        except ValidationError as err:
            return jsonify(create_error_response(f"Validation error: {err.messages}", 400))

        # For demo purposes, simulate user registration
        # In production, this would save to a user database
        return jsonify(create_success_response({
            'message': 'Registration successful',
            'user': {
                'username': register_data['username'],
                'email': register_data['email'],
                'full_name': register_data['full_name'],
                'organization': register_data.get('organization'),
                'status': 'active',
                'role': 'user'
            },
            'note': 'Demo mode - user not persisted to database'
        }, "Registration completed"))

    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify(create_error_response("Registration failed", 500))


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile."""
    try:
        if not session.get('authenticated'):
            return jsonify(create_error_response("Not authenticated", 401))

        # Return current session user info
        return jsonify(create_success_response({
            'user': {
                'username': session.get('user_id'),
                'role': session.get('user_role'),
                'authenticated': True
            }
        }, "Profile retrieved successfully"))

    except Exception as e:
        current_app.logger.error(f"Profile error: {str(e)}")
        return jsonify(create_error_response("Failed to retrieve profile", 500))


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check authentication status."""
    return jsonify(create_success_response({
        'authenticated': session.get('authenticated', False),
        'user_id': session.get('user_id'),
        'role': session.get('user_role')
    }, "Authentication status retrieved"))
