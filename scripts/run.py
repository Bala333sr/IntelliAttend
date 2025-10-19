#!/usr/bin/env python3
"""
Runner script for IntelliAttend application
"""

import os
import sys

if __name__ == "__main__":
    # Add backend directory to Python path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_dir = os.path.join(parent_dir, 'backend')
    sys.path.insert(0, backend_dir)
    
    # Import and run the application
    from backend.app import app
    
    # Set default port if not specified
    port = int(os.environ.get('PORT', 5002))
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    )