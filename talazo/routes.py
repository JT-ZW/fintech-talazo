# routes.py
from flask import Blueprint, render_template, jsonify, request
import random
import datetime
import math

# Define blueprints
main = Blueprint('main', __name__)
api = Blueprint('api', __name__)

# Main routes
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/loans')
def loans():
    """Render the loans page"""
    return render_template('loans.html')

@main.route('/insurance')
def insurance():
    """Render the insurance page"""
    return render_template('insurance.html')

@main.route('/soil_analysis')
def soil_analysis():
    """Render the soil analysis page"""
    return render_template('soil_analysis.html')


# API routes
@api.route('/demo-data')
def get_demo_data():
    """
    Generate random demo data for the dashboard prototype.
    This endpoint always returns simulated data regardless of backend status.
    """
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
# Add this route to your existing routes.py file

@main.route('/farmers')
def farmers():
    """Render the farmers management page"""
    return render_template('farmers.html')

# API routes for farmers data
@api.route('/farmers')
def get_farmers():
    """
    Get list of farmers with pagination, filtering, and sorting
    """
    try:
        # Get request parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '')
        region = request.args.get('region', '')
        crop = request.args.get('crop', '')
        risk_level = request.args.get('risk_level', '')
        sort_by = request.args.get('sort_by', 'id')
        sort_dir = request.args.get('sort_dir', 'asc')
        
        # In a real application, this would query a database
        # For prototype, we'll generate dummy data
        farmers = generate_dummy_farmers(50)
        
        # Apply filtering
        filtered_farmers = farmers
        if search:
            search = search.lower()
            filtered_farmers = [f for f in filtered_farmers if 
                search in f['full_name'].lower() or
                search in f['region'].lower() or
                str(f['id']) == search]
        
        if region:
            filtered_farmers = [f for f in filtered_farmers if f['region'] == region]
        
        if crop:
            filtered_farmers = [f for f in filtered_farmers if f['primary_crop'] == crop]
        
        if risk_level:
            filtered_farmers = [f for f in filtered_farmers if f['risk_level'].lower().replace(' ', '-') == risk_level]
        
        # Apply sorting
        reverse = sort_dir.lower() == 'desc'
        if sort_by == 'name':
            filtered_farmers.sort(key=lambda x: x['full_name'], reverse=reverse)
        elif sort_by == 'location':
            filtered_farmers.sort(key=lambda x: x['region'], reverse=reverse)
        elif sort_by == 'financial_index':
            filtered_farmers.sort(key=lambda x: x['financial_index'], reverse=reverse)
        else:
            filtered_farmers.sort(key=lambda x: x[sort_by], reverse=reverse)
        
        # Apply pagination
        total = len(filtered_farmers)
        total_pages = math.ceil(total / limit)
        start = (page - 1) * limit
        end = start + limit
        paginated_farmers = filtered_farmers[start:end]
        
        return jsonify({
            'farmers': paginated_farmers,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>')
def get_farmer(farmer_id):
    """
    Get details of a specific farmer
    """
    try:
        # In a real application, this would query a database
        farmers = generate_dummy_farmers(50)
        
        # Find farmer by ID
        farmer = next((f for f in farmers if f['id'] == farmer_id), None)
        
        if not farmer:
            return jsonify({
                'error': 'Farmer not found'
            }), 404
        
        return jsonify({
            'farmer': farmer
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers', methods=['POST'])
def create_farmer():
    """
    Create a new farmer
    """
    try:
        data = request.json
        
        # In a real application, this would insert into a database
        # For prototype, we'll return success with dummy ID
        
        return jsonify({
            'message': 'Farmer created successfully',
            'farmer_id': random.randint(1000, 9999)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>', methods=['PUT'])
def update_farmer(farmer_id):
    """
    Update an existing farmer
    """
    try:
        data = request.json
        
        # In a real application, this would update a database
        # For prototype, we'll return success
        
        return jsonify({
            'message': 'Farmer updated successfully',
            'farmer_id': farmer_id
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>', methods=['DELETE'])
def delete_farmer(farmer_id):
    """
    Delete a farmer
    """
    try:
        # In a real application, this would delete from a database
        # For prototype, we'll return success
        
        return jsonify({
            'message': 'Farmer deleted successfully',
            'farmer_id': farmer_id
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>/documents')
def get_farmer_documents(farmer_id):
    """
    Get documents for a specific farmer
    """
    try:
        # In a real application, this would query a database
        # For prototype, we'll return dummy data
        
        documents = [
            {
                'id': 1,
                'title': 'National ID',
                'type': 'id',
                'upload_date': (datetime.datetime.now() - datetime.timedelta(days=150)).isoformat(),
                'file_path': '/static/demo/id_doc.pdf'
            },
            {
                'id': 2,
                'title': 'Loan Agreement',
                'type': 'loan',
                'upload_date': (datetime.datetime.now() - datetime.timedelta(days=60)).isoformat(),
                'file_path': '/static/demo/loan_doc.pdf'
            },
            {
                'id': 3,
                'title': 'Soil Test Report',
                'type': 'soil_test',
                'upload_date': (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),
                'file_path': '/static/demo/soil_report.pdf'
            }
        ]
        
        return jsonify({
            'documents': documents
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>/documents', methods=['POST'])
def upload_document(farmer_id):
    """
    Upload a document for a specific farmer
    """
    try:
        # In a real application, this would save the file and update a database
        # For prototype, we'll return success
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document_id': random.randint(1000, 9999)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>/communications')
def get_farmer_communications(farmer_id):
    """
    Get communication history for a specific farmer
    """
    try:
        # In a real application, this would query a database
        # For prototype, we'll return dummy data
        
        communications = [
            {
                'id': 1,
                'type': 'sms',
                'date': (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                'message': 'Reminder: Your soil test appointment is scheduled for tomorrow at 10:00 AM.',
                'status': 'delivered'
            },
            {
                'id': 2,
                'type': 'email',
                'date': (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat(),
                'subject': 'Loan Application Status',
                'message': 'Your loan application has been pre-approved. Please visit our office to complete the documentation.',
                'status': 'opened'
            },
            {
                'id': 3,
                'type': 'visit',
                'date': (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat(),
                'notes': 'Conducted farm inspection. Soil samples collected for analysis.',
                'status': 'completed'
            }
        ]
        
        return jsonify({
            'communications': communications
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api.route('/farmers/<int:farmer_id>/communications', methods=['POST'])
def send_communication(farmer_id):
    """
    Send a communication to a specific farmer
    """
    try:
        data = request.json
        
        # In a real application, this would send the message and update a database
        # For prototype, we'll return success
        
        return jsonify({
            'message': 'Communication sent successfully',
            'communication_id': random.randint(1000, 9999)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

def generate_dummy_farmers(count):
    """Generate dummy farmer data for demonstration"""
    regions = [
        'mashonaland_central', 'mashonaland_east', 'mashonaland_west',
        'matabeleland_north', 'matabeleland_south', 'midlands',
        'masvingo', 'manicaland', 'harare', 'bulawayo'
    ]
    
    crops = [
        'maize', 'tobacco', 'cotton', 'groundnuts', 'soybeans',
        'wheat', 'sorghum', 'millet', 'vegetables', 'fruits'
    ]
    
    farmers = []
    
    for i in range(1, count + 1):
        financial_index = random.randint(0, 100)
        
        if financial_index >= 80:
            risk_level = 'Low Risk'
        elif financial_index >= 60:
            risk_level = 'Medium-Low Risk'
        elif financial_index >= 40:
            risk_level = 'Medium Risk'
        elif financial_index >= 20:
            risk_level = 'Medium-High Risk'
        else:
            risk_level = 'High Risk'
        
        farmer = {
            'id': i,
            'first_name': f'First{i}',
            'last_name': f'Last{i}',
            'full_name': f'First{i} Last{i}',
            'gender': 'Male' if random.random() > 0.5 else 'Female',
            'phone': f'+263 7{random.randint(0, 9)}{random.randint(0, 9)} {random.randint(1000000, 9999999)}',
            'email': f'farmer{i}@example.com',
            'region': random.choice(regions),
            'district': f'District {random.randint(1, 10)}',
            'farm_size': round(random.uniform(1, 20), 1),
            'primary_crop': random.choice(crops),
            'financial_index': financial_index,
            'risk_level': risk_level,
            'registration_date': (datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 1000))).isoformat()
        }
        
        # Format the region name for display
        farmer['region_formatted'] = farmer['region'].replace('_', ' ').title()
        
        farmers.append(farmer)
    
    return farmers