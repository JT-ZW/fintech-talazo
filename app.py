# app.py
"""
Alternative WSGI entry point for Talazo AgriFinance Platform.

This provides the 'app' instance that Gunicorn expects.
"""

from app import create_app

# Create Flask application instance
app = create_app('production')

if __name__ == "__main__":
    app.run()
