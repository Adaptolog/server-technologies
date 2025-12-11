#!/usr/bin/env python3
"""Main entry point for the application"""

from app import app

if __name__ == '__main__':
    import os
    import sys
    
    port = int(os.environ.get('PORT', 5000))
    
    # Check for debug mode
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)