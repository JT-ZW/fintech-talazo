# run.py
"""
Development server entry point for Talazo AgriFinance Platform.

This script runs the Flask development server.
Use this for local development only.
"""

import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🌱 Talazo AgriFinance Platform Starting...")
    print("=" * 60)
    print("📊 Dashboard URL: http://localhost:5000/dashboard")
    print("📡 API Base URL: http://localhost:5000/api")
    print("🏥 Health Check: http://localhost:5000/api/healthcheck")
    print("=" * 60)
    
    # Run development server
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000))
    )