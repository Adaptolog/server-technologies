#!/usr/bin/env python3
"""Main entry point for the application"""

from app import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)