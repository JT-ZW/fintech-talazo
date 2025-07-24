# wsgi.py
"""
WSGI entry point for Talazo AgriFinance Platform.

This module provides the WSGI application object for production deployment.
"""

from app import create_app

# Create application instance for WSGI
application = create_app('production')

if __name__ == "__main__":
    application.run()