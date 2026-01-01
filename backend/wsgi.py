"""
WSGI entry point for production deployment (Render, etc.)
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import the Flask app
from webapp.app import app

if __name__ == "__main__":
    app.run()
