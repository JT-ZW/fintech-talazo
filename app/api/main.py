# app/api/main.py
"""
Main routes for Talazo AgriFinance Platform.

This module handles dashboard, home page, and general application routes.
"""

from flask import Blueprint, render_template, jsonify, current_app
from app.core.extensions import db
from app.models import Farmer, SoilSample
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard route."""
    return render_template('dashboard.html')


@main_bp.route('/farmers')
def farmers_page():
    """Farmers management page."""
    return render_template('farmers.html')


@main_bp.route('/loans')
def loans_page():
    """Loan management page."""
    return render_template('loans.html')


@main_bp.route('/insurance')
def insurance_page():
    """Insurance management page."""
    return render_template('insurance.html')


@main_bp.route('/soil_analysis')
def soil_analysis_page():
    """Soil analysis page."""
    return render_template('soil_analysis.html')


@main_bp.route('/ai_recommendations')
def ai_recommendations_page():
    """AI recommendations page."""
    return render_template('ai_recommendations.html')


@main_bp.route('/reports')
def reports_page():
    """Reports and analytics page."""
    return render_template('reports.html')


@main_bp.route('/trends')
def trends_page():
    """Market trends page."""
    return render_template('trends.html')


@main_bp.route('/settings')
def settings_page():
    """Settings page."""
    return render_template('settings.html')


@main_bp.route('/help')
def help_page():
    """Help and support page."""
    return render_template('help.html')


@main_bp.route('/api/healthcheck')
def healthcheck():
    """
    Comprehensive system health check endpoint.
    
    Returns:
        JSON response with system health status
    """
    try:
        # Check database connection (SQLAlchemy 2.0 compatible)
        with db.engine.connect() as connection:
            connection.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'
    
    # Get basic statistics
    try:
        farmer_count = Farmer.query.count()
        soil_sample_count = SoilSample.query.count()
        recent_samples = SoilSample.query.filter(
            SoilSample.collection_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
    except Exception as e:
        current_app.logger.error(f"Statistics query failed: {str(e)}")
        farmer_count = 0
        soil_sample_count = 0
        recent_samples = 0
    
    health_status = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'components': {
            'database': db_status,
            'application': 'healthy'
        },
        'statistics': {
            'total_farmers': farmer_count,
            'total_soil_samples': soil_sample_count,
            'recent_samples_30_days': recent_samples
        },
        'system_info': {
            'environment': current_app.config.get('ENV', 'unknown'),
            'debug_mode': current_app.debug
        }
    }
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@main_bp.route('/api/dashboard/summary')
def dashboard_summary():
    """
    Get dashboard summary statistics.
    
    Returns:
        JSON response with dashboard data
    """
    try:
        # Get basic counts
        total_farmers = Farmer.query.filter_by(is_active=True).count()
        total_soil_samples = SoilSample.query.count()
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_farmers = Farmer.query.filter(
            Farmer.registration_date >= thirty_days_ago
        ).count()
        recent_samples = SoilSample.query.filter(
            SoilSample.collection_date >= thirty_days_ago
        ).count()
        
        # Get average soil health score
        avg_soil_health = db.session.query(
            db.func.avg(SoilSample.financial_index_score)
        ).filter(
            SoilSample.financial_index_score.isnot(None)
        ).scalar()
        
        # Get risk distribution
        risk_distribution = {}
        for risk_level in ['LOW', 'MEDIUM_LOW', 'MEDIUM', 'MEDIUM_HIGH', 'HIGH']:
            count = SoilSample.query.filter_by(risk_level=risk_level).count()
            risk_distribution[risk_level] = count
        
        # Get recent high-scoring farmers
        recent_high_scores = db.session.query(
            Farmer.full_name, 
            Farmer.district,
            SoilSample.financial_index_score,
            SoilSample.collection_date
        ).join(SoilSample).filter(
            SoilSample.financial_index_score >= 70,
            SoilSample.collection_date >= thirty_days_ago
        ).order_by(
            SoilSample.financial_index_score.desc()
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'totals': {
                    'farmers': total_farmers,
                    'soil_samples': total_soil_samples
                },
                'recent_activity': {
                    'new_farmers': new_farmers,
                    'recent_samples': recent_samples,
                    'period_days': 30
                },
                'performance_metrics': {
                    'average_soil_health': round(avg_soil_health or 0, 2),
                    'risk_distribution': risk_distribution
                },
                'highlights': {
                    'top_performers': [
                        {
                            'farmer_name': row[0],
                            'district': row[1] or 'Unknown',
                            'score': round(row[2], 2),
                            'date': row[3].isoformat() if row[3] else None
                        }
                        for row in recent_high_scores
                    ]
                },
                'generated_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard summary error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate dashboard summary'
        }), 500


@main_bp.route('/api/system/status')
def system_status():
    """
    Get detailed system status information.
    
    Returns:
        JSON response with system status
    """
    try:
        # Check various system components
        components = {}
        
        # Database check
        try:
            db.engine.execute('SELECT 1')
            components['database'] = {
                'status': 'operational',
                'response_time_ms': None  # Could add timing here
            }
        except Exception as e:
            components['database'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Check if core services are available
        try:
            from app.services import FarmViabilityScorer
            scorer = FarmViabilityScorer()
            components['scoring_service'] = {'status': 'operational'}
        except Exception as e:
            components['scoring_service'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Overall system status
        overall_status = 'operational' if all(
            comp.get('status') == 'operational' 
            for comp in components.values()
        ) else 'degraded'
        
        return jsonify({
            'system_status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'components': components,
            'uptime': 'N/A',  # Could implement uptime tracking
            'version': '1.0.0'
        })
        
    except Exception as e:
        current_app.logger.error(f"System status error: {str(e)}")
        return jsonify({
            'system_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@main_bp.route('/api/alerts')
def get_alerts():
    """
    Get system alerts and notifications.
    
    Returns:
        JSON response with current alerts
    """
    try:
        alerts = []
        
        # Check for farmers without recent soil samples
        farmers_without_recent_samples = db.session.query(Farmer).filter(
            ~Farmer.id.in_(
                db.session.query(SoilSample.farmer_id).filter(
                    SoilSample.collection_date >= datetime.utcnow() - timedelta(days=90)
                )
            ),
            Farmer.is_active == True
        ).count()
        
        if farmers_without_recent_samples > 0:
            alerts.append({
                'type': 'warning',
                'title': 'Outdated Soil Data',
                'message': f'{farmers_without_recent_samples} farmers have not submitted soil samples in the last 90 days',
                'action': 'Review farmer soil sample schedules',
                'priority': 'medium'
            })
        
        # Check for high-risk farmers
        high_risk_samples = SoilSample.query.filter_by(risk_level='HIGH').count()
        if high_risk_samples > 0:
            alerts.append({
                'type': 'error',
                'title': 'High Risk Farmers',
                'message': f'{high_risk_samples} soil samples indicate high financial risk',
                'action': 'Review high-risk farmers for additional support',
                'priority': 'high'
            })
        
        # Check for system performance
        low_performing_farmers = SoilSample.query.filter(
            SoilSample.financial_index_score < 40
        ).count()
        
        if low_performing_farmers > 10:
            alerts.append({
                'type': 'info',
                'title': 'Low Performance Trend',
                'message': f'{low_performing_farmers} farmers have scores below 40',
                'action': 'Consider targeted intervention programs',
                'priority': 'low'
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'alert_count': len(alerts),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Alerts generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate alerts'
        }), 500
