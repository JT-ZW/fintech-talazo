# talazo/routes/farmers.py
from flask import Blueprint, render_template, jsonify, request, current_app
from talazo.models import db, Farmer, User, FarmPlot, SoilSample
from sqlalchemy import func, and_
from datetime import datetime, timedelta

farmers_bp = Blueprint('farmers', __name__)

@farmers_bp.route('/')
def farmers_index():
    """Render the farmers management page"""
    return render_template('farmers/index.html')

@farmers_bp.route('/api/farmers')
def get_farmers():
    """
    API endpoint to retrieve farmers with filtering and pagination
    
    Query Parameters:
    - page: Current page number (default 1)
    - per_page: Number of items per page (default 10)
    - location: Filter by region/location
    - crop: Filter by primary crop
    - min_land_area: Minimum land area
    - max_land_area: Maximum land area
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    location = request.args.get('location')
    crop = request.args.get('crop')
    min_land_area = request.args.get('min_land_area', type=float)
    max_land_area = request.args.get('max_land_area', type=float)
    
    # Base query
    query = Farmer.query.join(User)
    
    # Apply filters
    if location:
        query = query.filter(Farmer.address.ilike(f'%{location}%'))
    
    if crop:
        query = query.filter(Farmer.primary_crop.ilike(f'%{crop}%'))
    
    if min_land_area is not None:
        query = query.filter(Farmer.total_land_area >= min_land_area)
    
    if max_land_area is not None:
        query = query.filter(Farmer.total_land_area <= max_land_area)
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare farmer data
    farmers_data = []
    for farmer in pagination.items:
        # Get latest soil sample
        latest_sample = SoilSample.query.filter_by(farmer_id=farmer.id)\
            .order_by(SoilSample.collection_date.desc()).first()
        
        # Get farm plots
        plots = FarmPlot.query.filter_by(farmer_id=farmer.id).all()
        
        farmers_data.append({
            'id': farmer.id,
            'full_name': farmer.full_name,
            'username': farmer.user.username,
            'email': farmer.user.email,
            'phone_number': farmer.phone_number,
            'address': farmer.address,
            'primary_crop': farmer.primary_crop,
            'total_land_area': farmer.total_land_area,
            'farming_experience': farmer.farming_experience_years,
            'soil_health_score': latest_sample.financial_index_score if latest_sample else None,
            'num_plots': len(plots),
            'location_lat': farmer.location_lat,
            'location_lng': farmer.location_lng
        })
    
    return jsonify({
        'farmers': farmers_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@farmers_bp.route('/api/farmers/<int:farmer_id>')
def get_farmer_details(farmer_id):
    """
    API endpoint to get detailed information for a specific farmer
    """
    farmer = Farmer.query.get_or_404(farmer_id)
    
    # Get farm plots
    plots = FarmPlot.query.filter_by(farmer_id=farmer_id).all()
    
    # Get soil samples
    soil_samples = SoilSample.query.filter_by(farmer_id=farmer_id)\
        .order_by(SoilSample.collection_date.desc()).all()
    
    # Get recent loans and insurance policies
    from talazo.models import Loan, InsurancePolicy
    recent_loans = Loan.query.filter_by(farmer_id=farmer_id)\
        .order_by(Loan.created_at.desc()).limit(3).all()
    
    recent_insurance = InsurancePolicy.query.filter_by(farmer_id=farmer_id)\
        .order_by(InsurancePolicy.created_at.desc()).limit(3).all()
    
    # Prepare detailed data
    farmer_data = {
        'personal_info': {
            'id': farmer.id,
            'full_name': farmer.full_name,
            'phone_number': farmer.phone_number,
            'national_id': farmer.national_id,
            'address': farmer.address,
            'location': {
                'lat': farmer.location_lat,
                'lng': farmer.location_lng
            }
        },
        'farming_details': {
            'primary_crop': farmer.primary_crop,
            'total_land_area': farmer.total_land_area,
            'farming_experience': farmer.farming_experience_years
        },
        'farm_plots': [{
            'id': plot.id,
            'name': plot.name,
            'area': plot.area,
            'current_crop': plot.current_crop,
            'planting_date': plot.planting_date.isoformat() if plot.planting_date else None,
            'expected_harvest_date': plot.expected_harvest_date.isoformat() if plot.expected_harvest_date else None
        } for plot in plots],
        'soil_samples': [{
            'id': sample.id,
            'collection_date': sample.collection_date.isoformat(),
            'ph_level': sample.ph_level,
            'nitrogen_level': sample.nitrogen_level,
            'phosphorus_level': sample.phosphorus_level,
            'potassium_level': sample.potassium_level,
            'organic_matter': sample.organic_matter,
            'financial_index_score': sample.financial_index_score,
            'risk_level': sample.risk_level.value if sample.risk_level else None
        } for sample in soil_samples],
        'recent_loans': [{
            'id': loan.id,
            'amount': loan.amount,
            'interest_rate': loan.interest_rate,
            'status': loan.status,
            'approval_date': loan.approval_date.isoformat() if loan.approval_date else None
        } for loan in recent_loans],
        'recent_insurance': [{
            'id': policy.id,
            'policy_number': policy.policy_number,
            'coverage_type': policy.coverage_type,
            'premium_amount': policy.premium_amount,
            'start_date': policy.start_date.isoformat(),
            'end_date': policy.end_date.isoformat(),
            'status': policy.status
        } for policy in recent_insurance]
    }
    
    return jsonify(farmer_data)

# Aggregate statistics for farmers dashboard
@farmers_bp.route('/api/farmers/stats')
def get_farmers_stats():
    """
    API endpoint to get aggregate statistics about farmers
    """
    # Total farmers count
    total_farmers = Farmer.query.count()
    
    # Total land area
    total_land_area = db.session.query(func.sum(Farmer.total_land_area)).scalar() or 0
    
    # Average farming experience
    avg_experience = db.session.query(func.avg(Farmer.farming_experience_years)).scalar() or 0
    
    # Crop distribution
    crop_distribution = db.session.query(
        Farmer.primary_crop, 
        func.count(Farmer.id)
    ).group_by(Farmer.primary_crop).all()
    
    # Recent farmers (joined in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_farmers = Farmer.query.filter(Farmer.created_at >= thirty_days_ago).count()
    
    # Farmers by region (based on address)
    region_distribution = db.session.query(
        func.substr(Farmer.address, -20),  # Extract last 20 characters as region
        func.count(Farmer.id)
    ).group_by(func.substr(Farmer.address, -20)).all()
    
    # Average land area by crop
    avg_land_by_crop = db.session.query(
        Farmer.primary_crop, 
        func.avg(Farmer.total_land_area)
    ).group_by(Farmer.primary_crop).all()
    
    return jsonify({
        'total_farmers': total_farmers,
        'total_land_area': round(total_land_area, 2),
        'average_farming_experience': round(avg_experience, 1),
        'recent_farmers': recent_farmers,
        'crop_distribution': dict(crop_distribution),
        'region_distribution': dict(region_distribution),
        'avg_land_by_crop': dict(avg_land_by_crop)
    })
    
    @farmers_bp.route('/new', methods=['GET'])
def new_farmer_form():
    """Render the new farmer registration form"""
    return render_template('farmers/add_farmer.html')

@farmers_bp.route('/api/farmers/new', methods=['POST'])
def create_farmer():
    """
    API endpoint to create a new farmer profile
    
    Expects JSON payload with farmer details
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'full_name', 'national_id', 'phone_number', 
            'primary_crop', 'total_land_area', 
            'farming_experience', 'username', 'password'
        ]
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({
                'success': False, 
                'message': 'Username already exists'
            }), 409
        
        # Create user account
        user = User(
            username=data['username'],
            email=data.get('email', ''),
            role=UserRole.FARMER
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create farmer profile
        farmer = Farmer(
            user_id=user.id,
            full_name=data['full_name'],
            national_id=data['national_id'],
            phone_number=data['phone_number'],
            address=data.get('address', ''),
            primary_crop=data['primary_crop'],
            total_land_area=float(data['total_land_area']),
            farming_experience_years=int(data['farming_experience']),
            location_lat=data.get('location_lat'),
            location_lng=data.get('location_lng')
        )
        db.session.add(farmer)
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Farmer profile created successfully',
            'farmer_id': farmer.id,
            'user_id': user.id
        }), 201
    
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        
        # Log the error
        current_app.logger.error(f"Error creating farmer: {str(e)}")
        
        return jsonify({
            'success': False, 
            'message': 'Failed to create farmer profile',
            'error': str(e)
        }), 500

@farmers_bp.route('/api/farmers/validate-username', methods=['GET'])
def validate_username():
    """
    API endpoint to check if a username is available
    """
    username = request.args.get('username')
    
    if not username:
        return jsonify({
            'available': False, 
            'message': 'Username is required'
        }), 400
    
    # Check if username exists
    existing_user = User.query.filter_by(username=username).first()
    
    return jsonify({
        'available': existing_user is None,
        'message': 'Username is available' if existing_user is None else 'Username is already taken'
    })

@farmers_bp.route('/api/farmers/export')
def export_farmers_data():
    """
    API endpoint to export farmers data in various formats
    """
    # Get export parameters
    export_format = request.args.get('format', 'csv').lower()
    include_fields = request.args.get('fields', 'basic').lower()
    
    # Fetch farmers based on export requirements
    farmers_query = Farmer.query.join(User)
    
    # Select fields based on requirements
    if include_fields == 'detailed':
        farmers = farmers_query.all()
        exported_data = []
        for farmer in farmers:
            exported_data.append({
                'id': farmer.id,
                'full_name': farmer.full_name,
                'phone_number': farmer.phone_number,
                'email': farmer.user.email,
                'primary_crop': farmer.primary_crop,
                'total_land_area': farmer.total_land_area,
                'farming_experience': farmer.farming_experience_years,
                'location': f"{farmer.location_lat}, {farmer.location_lng}",
                'address': farmer.address
            })
    else:
        # Basic export
        farmers = farmers_query.with_entities(
            Farmer.id, 
            Farmer.full_name, 
            Farmer.primary_crop, 
            Farmer.total_land_area
        ).all()
        exported_data = [
            {
                'id': f.id, 
                'full_name': f.full_name, 
                'primary_crop': f.primary_crop, 
                'total_land_area': f.total_land_area
            } for f in farmers
        ]
    
    # Export based on format
    if export_format == 'json':
        return jsonify(exported_data)
    elif export_format == 'csv':
        import csv
        from io import StringIO
        
        # Create CSV in memory
        si = StringIO()
        cw = csv.DictWriter(si, fieldnames=exported_data[0].keys())
        
        # Write headers and rows
        cw.writeheader()
        cw.writerows(exported_data)
        
        # Return CSV as downloadable file
        from flask import make_response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=farmers_export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    
    # Default to JSON if unsupported format
    return jsonify(exported_data)